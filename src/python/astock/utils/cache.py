"""数据缓存层"""

from datetime import timedelta
from typing import Optional, Any, Callable, TypeVar, ParamSpec
from functools import wraps
import asyncio

from cachetools import TTLCache

from .logger import get_logger

logger = get_logger("cache")

P = ParamSpec("P")
T = TypeVar("T")


class DataCache:
    """统一数据缓存管理器"""

    def __init__(
        self,
        realtime_ttl: int = 3,  # 实时行情缓存 3 秒
        daily_ttl: int = 300,  # 日线数据缓存 5 分钟
        stock_list_ttl: int = 3600,  # 股票列表缓存 1 小时
        maxsize: int = 1000,
    ):
        """初始化缓存管理器

        Args:
            realtime_ttl: 实时行情缓存过期时间（秒）
            daily_ttl: 日线数据缓存过期时间（秒）
            stock_list_ttl: 股票列表缓存过期时间（秒）
            maxsize: 最大缓存条目数
        """
        self._realtime_cache = TTLCache(maxsize=maxsize, ttl=realtime_ttl)
        self._daily_cache = TTLCache(maxsize=maxsize // 10, ttl=daily_ttl)
        self._stock_list_cache = TTLCache(maxsize=10, ttl=stock_list_ttl)
        self._general_cache = TTLCache(maxsize=maxsize, ttl=60)

        self._locks: dict[str, asyncio.Lock] = {}

    def _get_lock(self, key: str) -> asyncio.Lock:
        """获取或创建键对应的锁"""
        if key not in self._locks:
            self._locks[key] = asyncio.Lock()
        return self._locks[key]

    async def get_or_set(
        self,
        cache_type: str,
        key: str,
        factory: Callable[[], T],
    ) -> T:
        """获取缓存或执行工厂函数生成并缓存

        Args:
            cache_type: 缓存类型 (realtime/daily/stock_list/general)
            key: 缓存键
            factory: 数据生成函数

        Returns:
            缓存或新生成的数据
        """
        cache_map = {
            "realtime": self._realtime_cache,
            "daily": self._daily_cache,
            "stock_list": self._stock_list_cache,
            "general": self._general_cache,
        }

        cache = cache_map.get(cache_type, self._general_cache)

        # 检查缓存
        if key in cache:
            logger.debug(f"缓存命中: {cache_type}/{key}")
            return cache[key]

        # 获取锁，防止缓存击穿
        lock = self._get_lock(key)
        async with lock:
            # 双重检查
            if key in cache:
                return cache[key]

            # 生成数据
            logger.debug(f"缓存未命中，生成数据: {cache_type}/{key}")
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()

            # 存入缓存
            cache[key] = value
            return value

    def invalidate(self, cache_type: str, key: Optional[str] = None) -> None:
        """使缓存失效

        Args:
            cache_type: 缓存类型
            key: 缓存键，None 表示清除整个缓存类型
        """
        cache_map = {
            "realtime": self._realtime_cache,
            "daily": self._daily_cache,
            "stock_list": self._stock_list_cache,
            "general": self._general_cache,
        }

        cache = cache_map.get(cache_type, self._general_cache)

        if key:
            if key in cache:
                del cache[key]
                logger.debug(f"缓存已清除: {cache_type}/{key}")
        else:
            cache.clear()
            logger.debug(f"缓存已全部清除: {cache_type}")

    def get_stats(self) -> dict[str, Any]:
        """获取缓存统计信息"""
        return {
            "realtime": {
                "size": len(self._realtime_cache),
                "maxsize": self._realtime_cache.maxsize,
            },
            "daily": {
                "size": len(self._daily_cache),
                "maxsize": self._daily_cache.maxsize,
            },
            "stock_list": {
                "size": len(self._stock_list_cache),
                "maxsize": self._stock_list_cache.maxsize,
            },
            "general": {
                "size": len(self._general_cache),
                "maxsize": self._general_cache.maxsize,
            },
        }


def cached(
    cache_type: str = "general",
    key_builder: Optional[Callable[..., str]] = None,
):
    """缓存装饰器

    Args:
        cache_type: 缓存类型
        key_builder: 缓存键构建函数，接收被装饰函数的参数

    Returns:
        装饰器函数

    Example:
        @cached("realtime", lambda code: f"quote:{code}")
        async def get_quote(code: str):
            ...
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        _cache: TTLCache = TTLCache(maxsize=1000, ttl=60)

        @wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            # 构建缓存键
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"

            if key in _cache:
                logger.debug(f"装饰器缓存命中: {key}")
                return _cache[key]

            result = await func(*args, **kwargs)
            _cache[key] = result
            return result

        @wraps(func)
        def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            if key_builder:
                key = key_builder(*args, **kwargs)
            else:
                key = f"{func.__name__}:{args}:{kwargs}"

            if key in _cache:
                logger.debug(f"装饰器缓存命中: {key}")
                return _cache[key]

            result = func(*args, **kwargs)
            _cache[key] = result
            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# 全局缓存实例
_cache_instance: Optional[DataCache] = None


def get_cache() -> DataCache:
    """获取全局缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = DataCache()
    return _cache_instance
