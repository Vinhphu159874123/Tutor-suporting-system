"""
Redis Cache Service — Async Version
=====================================
Dùng redis.asyncio (non-blocking) thay cho redis sync.
Tất cả operations đều là coroutine, không block event loop của uvicorn.

Tại sao quan trọng:
  FastAPI chạy trên asyncio event loop. Nếu dùng redis sync (blocking I/O),
  toàn bộ server bị block khi chờ Redis response — không request nào khác
  được xử lý trong thời gian đó.

  redis.asyncio dùng non-blocking socket → event loop tiếp tục xử lý
  requests khác trong khi chờ Redis response.
"""
import json
import asyncio
import redis.asyncio as aioredis
from typing import Optional, Any, Callable, Awaitable
from functools import wraps
import hashlib
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Async Redis client singleton
_redis_client: Optional[aioredis.Redis] = None

# Singleflight: track in-flight loaders to prevent cache stampede
# Khi cache miss, chỉ 1 coroutine gọi loader(), các coroutine khác chờ kết quả.
_inflight: dict[str, asyncio.Future] = {}


async def get_redis() -> Optional[aioredis.Redis]:
    """
    Lấy async Redis client (singleton, lazy init).

    Trả về None nếu không kết nối được — các caller phải handle
    trường hợp này (graceful degradation: cache miss, lock skip).
    """
    global _redis_client
    if _redis_client is not None:
        return _redis_client

    try:
        is_upstash = "upstash.io" in settings.REDIS_URL

        if is_upstash:
            # Upstash yêu cầu TLS — dùng rediss:// URL
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
                ssl_cert_reqs=None,          # tắt cert verification (Upstash self-signed)
            )
        else:
            # Local Redis — kết nối thường
            _redis_client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=1.0,
                socket_timeout=1.0,
            )

        # Ping để xác nhận kết nối (async)
        await _redis_client.ping()
        print(f"✅ Redis (async) connected successfully ({'TLS/Upstash' if is_upstash else 'standard'})")

    except Exception as e:
        logger.warning(f"⚠️  Redis connection failed: {e}. Continuing without cache.")
        _redis_client = None

    return _redis_client


async def close_redis() -> None:
    """Đóng kết nối Redis — gọi khi app shutdown."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis connection closed.")


def _make_cache_key(*args, **kwargs) -> str:
    """Tạo cache key từ arguments bằng MD5 hash."""
    key_data = f"{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


async def get_cached(key: str) -> Optional[Any]:
    """
    Lấy value từ cache.
    Trả về None nếu cache miss hoặc Redis không available.
    """
    try:
        client = await get_redis()
        if client is None:
            return None

        cached = await client.get(key)   # non-blocking await
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"⚠️  Cache read error for key '{key}': {e}")
    return None


async def set_cached(key: str, value: Any, ttl: int = 60) -> bool:
    """
    Lưu value vào cache với TTL (giây).
    Trả về False nếu Redis không available hoặc lỗi.
    """
    try:
        client = await get_redis()
        if client is None:
            return False

        await client.setex(key, ttl, json.dumps(value, default=str))  # non-blocking
        return True
    except Exception as e:
        logger.warning(f"⚠️  Cache write error for key '{key}': {e}")
        return False


async def delete_cached(pattern: str) -> int:
    """
    Xóa tất cả keys khớp với pattern.
    Trả về số lượng keys đã xóa.
    """
    try:
        client = await get_redis()
        if client is None:
            return 0

        keys = await client.keys(pattern)   # non-blocking
        if keys:
            return await client.delete(*keys)   # non-blocking
    except Exception as e:
        logger.warning(f"⚠️  Cache delete error for pattern '{pattern}': {e}")
    return 0


async def get_or_load(
    key: str,
    loader: Callable[[], Awaitable[Any]],
    ttl: int = 60,
) -> Any:
    """
    Cache-Aside with Singleflight protection — chống Cache Stampede.

    Khi cache miss, chỉ 1 coroutine được gọi loader() để query DB.
    Các coroutine khác cùng key sẽ chờ kết quả từ coroutine đầu tiên.

    Flow:
        1. Check cache → hit → return ngay
        2. Cache miss + key đang được load bởi coroutine khác → chờ Future
        3. Cache miss + chưa ai load → tạo Future, gọi loader(), set cache

    Kết quả: N concurrent requests cùng key = 1 DB query thay vì N.

    Args:
        key:    Cache key
        loader: Async function trả về data (thường là DB query)
        ttl:    Time-to-live (giây)

    Returns:
        Data từ cache hoặc từ loader()
    """
    # 1. Try cache first
    cached = await get_cached(key)
    if cached is not None:
        return cached

    # 2. Check if another coroutine is already loading this key
    if key in _inflight:
        try:
            return await asyncio.shield(_inflight[key])
        except Exception:
            # Nếu coroutine đầu tiên fail, ta sẽ thử tự load bên dưới
            pass

    # 3. We're the first — create a Future and load
    loop = asyncio.get_running_loop()
    future: asyncio.Future = loop.create_future()
    _inflight[key] = future

    try:
        result = await loader()
        await set_cached(key, result, ttl)
        future.set_result(result)
        return result
    except Exception as e:
        future.set_exception(e)
        raise
    finally:
        _inflight.pop(key, None)


def cache_response(ttl: int = 60, key_prefix: str = ""):
    """
    Decorator để cache kết quả của async endpoint.

    Usage:
        @cache_response(ttl=120, key_prefix="courses")
        async def get_courses(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key_str = f"{key_prefix}:{_make_cache_key(*args, **kwargs)}"

            cached_value = await get_cached(cache_key_str)
            if cached_value is not None:
                return cached_value

            result = await func(*args, **kwargs)
            await set_cached(cache_key_str, result, ttl)
            return result
        return wrapper
    return decorator
