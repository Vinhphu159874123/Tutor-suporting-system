"""
Redis Cache Service
Provides caching utilities for API responses
"""
import json
import redis
from typing import Optional, Any
from functools import wraps
import hashlib
from app.core.config import settings

# Redis connection pool
redis_client: Optional[redis.Redis] = None

def get_redis() -> redis.Redis:
    """Get Redis client singleton"""
    global redis_client
    if redis_client is None:
        try:
            # Check if using Upstash Redis (requires TLS)
            is_upstash = "upstash.io" in settings.REDIS_URL
            
            # Build connection params
            connection_params = {
                "encoding": "utf-8",
                "decode_responses": True,
                "socket_connect_timeout": 2,
                "socket_timeout": 2
            }
            
            # Add SSL params only for Upstash
            if is_upstash:
                import ssl as ssl_module
                connection_params["ssl_cert_reqs"] = ssl_module.CERT_NONE  # Skip cert verification
            
            redis_client = redis.from_url(settings.REDIS_URL, **connection_params)
            
            # Test connection
            redis_client.ping()
            print(f"✅ Redis connected successfully ({'TLS' if is_upstash else 'standard'})")
        except Exception as e:
            print(f"⚠️  Redis connection failed: {e}")
            print("📝 Continuing without cache...")
            redis_client = None
    return redis_client


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = f"{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


async def get_cached(key: str) -> Optional[Any]:
    """Get cached value"""
    try:
        client = get_redis()
        if client is None:
            return None
        
        cached = client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"⚠️  Cache read error: {e}")
    return None


async def set_cached(key: str, value: Any, ttl: int = 60) -> bool:
    """Set cached value with TTL in seconds"""
    try:
        client = get_redis()
        if client is None:
            return False
        
        client.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        print(f"⚠️  Cache write error: {e}")
        return False


async def delete_cached(pattern: str) -> int:
    """Delete cached keys matching pattern"""
    try:
        client = get_redis()
        if client is None:
            return 0
        
        keys = client.keys(pattern)
        if keys:
            return client.delete(*keys)
    except Exception as e:
        print(f"⚠️  Cache delete error: {e}")
    return 0


def cache_response(ttl: int = 60, key_prefix: str = ""):
    """
    Decorator to cache endpoint responses
    
    Usage:
        @cache_response(ttl=120, key_prefix="courses")
        async def get_courses(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = await get_cached(cache_key_str)
            if cached_value is not None:
                return cached_value
            
            # Call original function
            result = await func(*args, **kwargs)
            
            # Cache the result
            await set_cached(cache_key_str, result, ttl)
            
            return result
        return wrapper
    return decorator
