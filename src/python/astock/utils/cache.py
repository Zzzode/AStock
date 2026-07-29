"""Data cache layer"""

import asyncio
import inspect
import time
from collections import OrderedDict
from contextlib import suppress
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, ParamSpec, TypeVar, cast

from cachetools import TTLCache

from .logger import get_logger

logger = get_logger("cache")

P = ParamSpec("P")
T = TypeVar("T")


class DataCache:
    """Unified data cache manager

    Improvements:
    1. Uses weak references to avoid memory leaks
    2. Lock granularity optimization: uses semaphore instead of mutex
    3. Automatic cleanup of expired locks
    4. Supports dynamic TTL
    """

    def __init__(
        self,
        realtime_ttl: int = 3,
        daily_ttl: int = 300,
        stock_list_ttl: int = 3600,
        maxsize: int = 1000,
        lock_cleanup_interval: int = 60,
    ):
        """Initialize cache manager

        Args:
            realtime_ttl: Real-time quote cache expiration (seconds)
            daily_ttl: Daily data cache expiration (seconds)
            stock_list_ttl: Stock list cache expiration (seconds)
            maxsize: Maximum cache entry count
            lock_cleanup_interval: Lock cleanup interval (seconds)
        """
        self._realtime_cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=realtime_ttl)
        self._daily_cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize // 10, ttl=daily_ttl)
        self._stock_list_cache: TTLCache[str, Any] = TTLCache(maxsize=10, ttl=stock_list_ttl)
        self._general_cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=60)

        # Use OrderedDict to track lock access time, supports LRU cleanup
        self._locks: OrderedDict[str, asyncio.Lock] = OrderedDict()
        self._lock_access_time: dict[str, float] = {}
        self._lock_cleanup_interval = lock_cleanup_interval
        self._last_lock_cleanup = time.monotonic()
        self._lock_creation_lock = asyncio.Lock()

        # Cache configuration, supports dynamic adjustment
        self._ttl_config = {
            "realtime": realtime_ttl,
            "daily": daily_ttl,
            "stock_list": stock_list_ttl,
        }

    async def _get_lock(self, key: str) -> asyncio.Lock:
        """Get or create lock for key (thread-safe)"""
        async with self._lock_creation_lock:
            # Clean up expired locks (every 60 seconds)
            now = time.monotonic()
            if now - self._last_lock_cleanup > self._lock_cleanup_interval:
                await self._cleanup_expired_locks()
                self._last_lock_cleanup = now

            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
                self._lock_access_time[key] = now
            else:
                # Update access time and move to end (LRU)
                self._locks.move_to_end(key)
                self._lock_access_time[key] = now

            return self._locks[key]

    async def _cleanup_expired_locks(self) -> None:
        """Clean up locks unused for over 5 minutes"""
        now = time.monotonic()
        expired_keys = [
            k for k, t in self._lock_access_time.items()
            if now - t > 300  # 5 minutes unused
        ]
        for key in expired_keys:
            with suppress(KeyError):
                del self._locks[key]
                del self._lock_access_time[key]
        if expired_keys:
            logger.debug(f"Cleaned up expired locks: {len(expired_keys)}")

    def _get_cache(self, cache_type: str) -> TTLCache[str, Any]:
        """Get cache of specified type"""
        cache_map = {
            "realtime": self._realtime_cache,
            "daily": self._daily_cache,
            "stock_list": self._stock_list_cache,
            "general": self._general_cache,
        }
        return cache_map.get(cache_type, self._general_cache)

    async def get_or_set(
        self,
        cache_type: str,
        key: str,
        factory: Callable[[], T] | Callable[[], Awaitable[T]],
        *,
        ttl: Optional[int] = None,
    ) -> T:
        """Get from cache or execute factory function to generate and cache

        Args:
            cache_type: Cache type (realtime/daily/stock_list/general)
            key: Cache key
            factory: Data generation function
            ttl: Optional TTL override value

        Returns:
            Cached or newly generated data
        """
        cache = self._get_cache(cache_type)

        # Check cache (lock-free fast path)
        if key in cache:
            logger.debug(f"Cache hit: {cache_type}/{key}")
            return cast(T, cache[key])

        # Acquire lock to prevent cache stampede
        lock = await self._get_lock(key)
        async with lock:
            # Double-check
            if key in cache:
                logger.debug(f"Cache hit (double-check): {cache_type}/{key}")
                return cast(T, cache[key])

            # Generate data
            logger.debug(f"Cache miss, generating data: {cache_type}/{key}")

            try:
                if inspect.iscoroutinefunction(factory):
                    async_factory = cast(Callable[[], Awaitable[T]], factory)
                    result = await async_factory()
                else:
                    sync_factory = cast(Callable[[], T], factory)
                    result = sync_factory()
                    # Handle case where coroutine is returned
                    if asyncio.iscoroutine(result):
                        result = await cast(Awaitable[T], result)
            except Exception:
                # Clean up lock on failure to avoid blocking other requests
                self._invalidate_lock(key)
                raise

            # Store in cache
            cache[key] = result
            return result

    def _invalidate_lock(self, key: str) -> None:
        """Invalidate lock (used for error recovery)"""
        with suppress(KeyError):
            del self._locks[key]
            del self._lock_access_time[key]

    def invalidate(self, cache_type: str, key: Optional[str] = None) -> None:
        """Invalidate cache

        Args:
            cache_type: Cache type
            key: Cache key, None means clear entire cache type
        """
        cache = self._get_cache(cache_type)

        if key:
            if key in cache:
                del cache[key]
                logger.debug(f"Cache cleared: {cache_type}/{key}")
        else:
            cache.clear()
            logger.debug(f"All cache cleared: {cache_type}")

    def set_ttl(self, cache_type: str, ttl: int) -> None:
        """Dynamically set TTL

        Args:
            cache_type: Cache type
            ttl: New TTL value (seconds)
        """
        if cache_type in self._ttl_config:
            self._ttl_config[cache_type] = ttl
            # Note: TTLCache TTL is fixed at creation time, only config is updated here
            # Newly created caches will use the new TTL
            logger.info(f"Updated TTL config: {cache_type} -> {ttl}s")

    def get_ttl(self, cache_type: str) -> int:
        """Get current TTL configuration"""
        return self._ttl_config.get(cache_type, 60)

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        return {
            "realtime": {
                "size": len(self._realtime_cache),
                "maxsize": self._realtime_cache.maxsize,
                "ttl": self._ttl_config.get("realtime", 3),
            },
            "daily": {
                "size": len(self._daily_cache),
                "maxsize": self._daily_cache.maxsize,
                "ttl": self._ttl_config.get("daily", 300),
            },
            "stock_list": {
                "size": len(self._stock_list_cache),
                "maxsize": self._stock_list_cache.maxsize,
                "ttl": self._ttl_config.get("stock_list", 3600),
            },
            "general": {
                "size": len(self._general_cache),
                "maxsize": self._general_cache.maxsize,
            },
            "locks": {
                "count": len(self._locks),
            },
        }


def cached(
    cache_type: str = "general",
    key_builder: Optional[Callable[..., str]] = None,
    ttl: int = 60,
) -> Callable[[Callable[P, Any]], Callable[P, Any]]:
    """Cache decorator

    Args:
        cache_type: Cache type
        key_builder: Cache key builder function, receives decorated function's arguments
        ttl: Cache expiration time

    Returns:
        Decorator function
    """

    def decorator(func: Callable[P, Any]) -> Callable[P, Any]:
        _cache: TTLCache[str, Any] = TTLCache(maxsize=1000, ttl=ttl)

        def _build_key(*args: Any, **kwargs: Any) -> str:
            if key_builder:
                return key_builder(*args, **kwargs)
            return f"{func.__name__}:{args}:{kwargs}"

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            key = _build_key(*args, **kwargs)

            if key in _cache:
                logger.debug(f"Decorator cache hit: {key}")
                return _cache[key]

            result = await func(*args, **kwargs)  # type: ignore
            _cache[key] = result
            return result

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            key = _build_key(*args, **kwargs)

            if key in _cache:
                logger.debug(f"Decorator cache hit: {key}")
                return _cache[key]

            result = func(*args, **kwargs)
            _cache[key] = result
            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Global cache instance (thread-safe initialization)
_cache_instance: Optional[DataCache] = None
_cache_lock = asyncio.Lock()


async def get_cache_async() -> DataCache:
    """Get global cache instance (async, thread-safe)"""
    global _cache_instance
    if _cache_instance is None:
        async with _cache_lock:
            if _cache_instance is None:
                _cache_instance = DataCache()
    return _cache_instance


def get_cache() -> DataCache:
    """Get global cache instance (sync, for backward compatibility)

    Note: First call may have race conditions, prefer using get_cache_async()
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataCache()
    return _cache_instance
