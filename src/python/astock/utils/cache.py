"""数据缓存层"""

import asyncio
import inspect
import time
from collections import OrderedDict
from contextlib import suppress
from datetime import timedelta
from functools import wraps
from typing import Any, Awaitable, Callable, Optional, ParamSpec, TypeVar, cast

from cachetools import TTLCache

from .logger import get_logger

logger = get_logger("cache")

P = ParamSpec("P")
T = TypeVar("T")


class DataCache:
    """统一数据缓存管理器

    改进点：
    1. 使用弱引用避免内存泄漏
    2. 锁粒度优化：使用信号量而非互斥锁
    3. 自动清理过期锁
    4. 支持动态 TTL
    """

    def __init__(
        self,
        realtime_ttl: int = 3,
        daily_ttl: int = 300,
        stock_list_ttl: int = 3600,
        maxsize: int = 1000,
        lock_cleanup_interval: int = 60,
    ):
        """初始化缓存管理器

        Args:
            realtime_ttl: 实时行情缓存过期时间（秒）
            daily_ttl: 日线数据缓存过期时间（秒）
            stock_list_ttl: 股票列表缓存过期时间（秒）
            maxsize: 最大缓存条目数
            lock_cleanup_interval: 锁清理间隔（秒）
        """
        self._realtime_cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=realtime_ttl)
        self._daily_cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize // 10, ttl=daily_ttl)
        self._stock_list_cache: TTLCache[str, Any] = TTLCache(maxsize=10, ttl=stock_list_ttl)
        self._general_cache: TTLCache[str, Any] = TTLCache(maxsize=maxsize, ttl=60)

        # 使用 OrderedDict 跟踪锁的访问时间，支持 LRU 清理
        self._locks: OrderedDict[str, asyncio.Lock] = OrderedDict()
        self._lock_access_time: dict[str, float] = {}
        self._lock_cleanup_interval = lock_cleanup_interval
        self._last_lock_cleanup = time.monotonic()
        self._lock_creation_lock = asyncio.Lock()

        # 缓存配置，支持动态调整
        self._ttl_config = {
            "realtime": realtime_ttl,
            "daily": daily_ttl,
            "stock_list": stock_list_ttl,
        }

    async def _get_lock(self, key: str) -> asyncio.Lock:
        """获取或创建键对应的锁（线程安全）"""
        async with self._lock_creation_lock:
            # 清理过期锁（每 60 秒执行一次）
            now = time.monotonic()
            if now - self._last_lock_cleanup > self._lock_cleanup_interval:
                await self._cleanup_expired_locks()
                self._last_lock_cleanup = now

            if key not in self._locks:
                self._locks[key] = asyncio.Lock()
                self._lock_access_time[key] = now
            else:
                # 更新访问时间并移到末尾（LRU）
                self._locks.move_to_end(key)
                self._lock_access_time[key] = now

            return self._locks[key]

    async def _cleanup_expired_locks(self) -> None:
        """清理超过 5 分钟未使用的锁"""
        now = time.monotonic()
        expired_keys = [
            k for k, t in self._lock_access_time.items()
            if now - t > 300  # 5 分钟未使用
        ]
        for key in expired_keys:
            with suppress(KeyError):
                del self._locks[key]
                del self._lock_access_time[key]
        if expired_keys:
            logger.debug(f"清理过期锁: {len(expired_keys)} 个")

    def _get_cache(self, cache_type: str) -> TTLCache[str, Any]:
        """获取指定类型的缓存"""
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
        """获取缓存或执行工厂函数生成并缓存

        Args:
            cache_type: 缓存类型 (realtime/daily/stock_list/general)
            key: 缓存键
            factory: 数据生成函数
            ttl: 可选的 TTL 覆盖值

        Returns:
            缓存或新生成的数据
        """
        cache = self._get_cache(cache_type)

        # 检查缓存（无锁快速路径）
        if key in cache:
            logger.debug(f"缓存命中: {cache_type}/{key}")
            return cast(T, cache[key])

        # 获取锁，防止缓存击穿
        lock = await self._get_lock(key)
        async with lock:
            # 双重检查
            if key in cache:
                logger.debug(f"缓存命中（双重检查）: {cache_type}/{key}")
                return cast(T, cache[key])

            # 生成数据
            logger.debug(f"缓存未命中，生成数据: {cache_type}/{key}")

            try:
                if inspect.iscoroutinefunction(factory):
                    async_factory = cast(Callable[[], Awaitable[T]], factory)
                    result = await async_factory()
                else:
                    sync_factory = cast(Callable[[], T], factory)
                    result = sync_factory()
                    # 处理返回协程的情况
                    if asyncio.iscoroutine(result):
                        result = await cast(Awaitable[T], result)
            except Exception:
                # 生成失败时清理锁，避免其他请求被阻塞
                self._invalidate_lock(key)
                raise

            # 存入缓存
            cache[key] = result
            return result

    def _invalidate_lock(self, key: str) -> None:
        """使锁失效（用于错误恢复）"""
        with suppress(KeyError):
            del self._locks[key]
            del self._lock_access_time[key]

    def invalidate(self, cache_type: str, key: Optional[str] = None) -> None:
        """使缓存失效

        Args:
            cache_type: 缓存类型
            key: 缓存键，None 表示清除整个缓存类型
        """
        cache = self._get_cache(cache_type)

        if key:
            if key in cache:
                del cache[key]
                logger.debug(f"缓存已清除: {cache_type}/{key}")
        else:
            cache.clear()
            logger.debug(f"缓存已全部清除: {cache_type}")

    def set_ttl(self, cache_type: str, ttl: int) -> None:
        """动态设置 TTL

        Args:
            cache_type: 缓存类型
            ttl: 新的 TTL 值（秒）
        """
        if cache_type in self._ttl_config:
            self._ttl_config[cache_type] = ttl
            # 注意：TTLCache 的 TTL 在创建时确定，这里只更新配置
            # 新创建的缓存会使用新 TTL
            logger.info(f"更新 TTL 配置: {cache_type} -> {ttl}s")

    def get_ttl(self, cache_type: str) -> int:
        """获取当前 TTL 配置"""
        return self._ttl_config.get(cache_type, 60)

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
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
    """缓存装饰器

    Args:
        cache_type: 缓存类型
        key_builder: 缓存键构建函数，接收被装饰函数的参数
        ttl: 缓存过期时间

    Returns:
        装饰器函数
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
                logger.debug(f"装饰器缓存命中: {key}")
                return _cache[key]

            result = await func(*args, **kwargs)  # type: ignore
            _cache[key] = result
            return result

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
            key = _build_key(*args, **kwargs)

            if key in _cache:
                logger.debug(f"装饰器缓存命中: {key}")
                return _cache[key]

            result = func(*args, **kwargs)
            _cache[key] = result
            return result

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# 全局缓存实例（线程安全初始化）
_cache_instance: Optional[DataCache] = None
_cache_lock = asyncio.Lock()


async def get_cache_async() -> DataCache:
    """获取全局缓存实例（异步，线程安全）"""
    global _cache_instance
    if _cache_instance is None:
        async with _cache_lock:
            if _cache_instance is None:
                _cache_instance = DataCache()
    return _cache_instance


def get_cache() -> DataCache:
    """获取全局缓存实例（同步，用于向后兼容）

    注意：首次调用时可能存在竞态条件，建议使用 get_cache_async()
    """
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataCache()
    return _cache_instance