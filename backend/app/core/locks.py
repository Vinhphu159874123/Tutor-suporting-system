"""
Distributed Lock Service using Redis
=====================================
Dùng để ngăn race conditions ở các critical sections như:
  - join_session: nhiều student cùng enroll 1 slot cuối
  - update_participant_status: tutor accept nhiều student đồng thời

Cơ chế: Redis SET NX PX (atomic SET if Not eXists with expiry)
  - SET lock_key <token> NX PX <ttl_ms>
  - NX = chỉ set nếu key CHƯA tồn tại  → đảm bảo chỉ 1 caller acquire được
  - PX = TTL tính bằng milliseconds     → tự động expire nếu process crash

Sau khi cache.py migrate sang redis.asyncio, locks.py không cần
run_in_executor workaround nữa — mọi Redis call đều là native async.
"""

import uuid
import time
import logging
from contextlib import asynccontextmanager

from app.core.cache import get_redis

logger = logging.getLogger(__name__)

# Thời gian mặc định giữ lock (ms)
DEFAULT_LOCK_TTL_MS = 5_000
# Thời gian chờ tối đa để acquire lock
DEFAULT_ACQUIRE_TIMEOUT_S = 3.0
# Khoảng sleep giữa các lần retry
RETRY_INTERVAL_MS = 50


class LockAcquisitionError(Exception):
    """Raise khi không acquire được lock trong timeout."""
    pass


async def _acquire_lock(client, key: str, token: str, ttl_ms: int) -> bool:
    """
    Atomic SET NX PX — trả về True nếu acquire thành công.
    Dùng redis.asyncio nên await trực tiếp, không cần run_in_executor.
    """
    result = await client.set(key, token, nx=True, px=ttl_ms)
    return result is True


async def _release_lock(client, key: str, token: str) -> None:
    """
    Lua script để release an toàn: chỉ xóa key nếu value = token của mình.
    Tránh trường hợp release nhầm lock của process khác (nếu TTL hết trước release).
    """
    lua_script = """
    if redis.call('get', KEYS[1]) == ARGV[1] then
        return redis.call('del', KEYS[1])
    else
        return 0
    end
    """
    try:
        await client.eval(lua_script, 1, key, token)
    except Exception as e:
        logger.warning(f"[Lock] Failed to release lock '{key}': {e}")


@asynccontextmanager
async def distributed_lock(
    resource: str,
    ttl_ms: int = DEFAULT_LOCK_TTL_MS,
    timeout_s: float = DEFAULT_ACQUIRE_TIMEOUT_S,
):
    """
    Async context manager để acquire/release distributed lock.

    Dùng như sau:
        async with distributed_lock(f"session:{session_id}:enroll"):
            # critical section — chỉ 1 coroutine chạy được cùng lúc
            ...

    Args:
        resource: Tên resource cần lock, VD: "session:42:enroll"
        ttl_ms:   TTL của lock (milliseconds). Tự expire nếu không được release.
        timeout_s: Thời gian tối đa (giây) để chờ acquire lock.

    Raises:
        LockAcquisitionError: Nếu không acquire được trong timeout_s.
    """
    import asyncio

    client = await get_redis()

    # Graceful degradation: nếu Redis down, vẫn chạy nhưng không có lock
    if client is None:
        logger.warning(
            f"[Lock] Redis unavailable. Running '{resource}' without lock protection. "
            "Race conditions may occur."
        )
        yield
        return

    lock_key = f"lock:{resource}"
    token = str(uuid.uuid4())
    deadline = time.monotonic() + timeout_s
    acquired = False

    # Spin-wait: thử acquire đến khi timeout
    while time.monotonic() < deadline:
        acquired = await _acquire_lock(client, lock_key, token, ttl_ms)
        if acquired:
            break
        await asyncio.sleep(RETRY_INTERVAL_MS / 1000)

    if not acquired:
        raise LockAcquisitionError(
            f"Could not acquire lock for '{resource}' within {timeout_s}s. "
            "The resource is currently being processed by another request. Please try again."
        )

    logger.debug(f"[Lock] Acquired '{lock_key}' (token={token[:8]}...)")
    try:
        yield  # ← critical section chạy ở đây
    finally:
        await _release_lock(client, lock_key, token)
        logger.debug(f"[Lock] Released '{lock_key}' (token={token[:8]}...)")
