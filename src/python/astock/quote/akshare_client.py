"""AkShare 行情客户端"""

import asyncio
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from functools import partial
from typing import Any, Callable, Optional, TypeVar, ParamSpec, cast

import akshare as ak
import pandas as pd

from ..utils import get_logger
from ..utils.exceptions import DataSourceError

logger = get_logger("akshare_client")

P = ParamSpec("P")
T = TypeVar("T")

# 专用线程池，避免阻塞默认线程池
_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    """获取专用线程池（懒加载）"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="akshare_")
    return _executor


def async_wrap(func: Callable[P, T]) -> Callable[P, "asyncio.Future[T]"]:
    """将同步函数包装为异步（使用专用线程池）

    改进：
    1. 使用 asyncio.get_running_loop() 替代已弃用的 get_event_loop()
    2. 使用专用线程池避免阻塞其他 I/O 操作
    3. 使用 functools.partial 避免lambda 开销
    """

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_running_loop()
        func_partial = partial(func, *args, **kwargs)
        return await loop.run_in_executor(_get_executor(), func_partial)

    return wrapper


# 可重试的网络错误类型
RETRYABLE_ERRORS = (
    ConnectionError,
    TimeoutError,
    OSError,
)


class AkShareClient:
    """AkShare 行情数据客户端

    改进：
    1. 更精确的错误分类和重试逻辑
    2. 数据源一致性校验
    3. 请求限流支持
    """

    def __init__(self, rate_limit_per_second: float = 2.0):
        """初始化客户端

        Args:
            rate_limit_per_second: 每秒最大请求数
        """
        self._rate_limit = rate_limit_per_second
        self._last_request_time: float = 0.0
        self._rate_limit_lock = asyncio.Lock()

    async def _apply_rate_limit(self) -> None:
        """应用请求限流"""
        async with self._rate_limit_lock:
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            now = loop.time()
            elapsed = now - self._last_request_time
            min_interval = 1.0 / self._rate_limit

            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)

            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                loop = asyncio.get_event_loop()
            self._last_request_time = loop.time()

    def _classify_error(self, error: Exception) -> str:
        """分类错误类型

        Returns:
            "retryable": 可重试的网络错误
            "data": 数据格式错误
            "auth": 认证/权限错误
            "unknown": 未知错误
        """
        error_name = type(error).__name__
        error_msg = str(error).lower()

        # 网络相关错误
        if isinstance(error, RETRYABLE_ERRORS):
            return "retryable"
        if any(
            token in error_name
            for token in (
                "Connection",
                "Timeout",
                "RemoteDisconnected",
                "ProtocolError",
                "ChunkedEncoding",
            )
        ):
            return "retryable"

        # 认证/权限错误
        if any(
            token in error_msg
            for token in ("403", "forbidden", "unauthorized", "auth", "login")
        ):
            return "auth"

        # 数据格式错误
        if isinstance(error, (KeyError, ValueError, TypeError)):
            return "data"

        return "unknown"

    # 类级别缓存，避免频繁请求导致 mini-racer 崩溃
    _realtime_cache: Optional[pd.DataFrame] = None
    _realtime_cache_time: float = 0.0
    _cache_ttl: float = 60.0  # 缓存有效期 60 秒

    def _load_realtime_dataframe(self) -> pd.DataFrame:
        """加载实时行情数据

        优先级：
        1. 使用缓存（60秒内有效）
        2. 新浪数据源 stock_zh_a_spot()（更稳定，不需要 mini-racer）
        3. 东方财富数据源 stock_zh_a_spot_em()（数据更全，但可能触发 mini-racer）

        Returns:
            实时行情 DataFrame
        """
        # 检查缓存
        current_time = time.time()
        if (
            self._realtime_cache is not None
            and current_time - self._realtime_cache_time < self._cache_ttl
        ):
            logger.debug("使用缓存的实时行情数据")
            return self._realtime_cache

        errors: list[str] = []

        # 优先使用新浪数据源（不需要 mini-racer，更稳定）
        try:
            logger.info("尝试新浪数据源 stock_zh_a_spot...")
            df = ak.stock_zh_a_spot()
            self._validate_realtime_columns(df, "stock_zh_a_spot")
            self._realtime_cache = df
            self._realtime_cache_time = current_time
            logger.info(f"新浪数据源成功，获取 {len(df)} 条数据")
            return df
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"新浪: {type(e).__name__}: {e} (type={error_type})")
            logger.warning(f"新浪数据源失败: {e} (type={error_type})")

        # 备用：东方财富数据源
        try:
            logger.info("尝试东方财富数据源 stock_zh_a_spot_em...")
            df = ak.stock_zh_a_spot_em()
            self._validate_realtime_columns(df, "stock_zh_a_spot_em")
            self._realtime_cache = df
            self._realtime_cache_time = current_time
            logger.info(f"东方财富数据源成功，获取 {len(df)} 条数据")
            return df
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"东方财富: {type(e).__name__}: {e} (type={error_type})")
            logger.error(f"东方财富数据源也失败: {e}")

        # 第三备用：使用股票列表 + 百度估值
        try:
            logger.info("尝试使用股票列表（估值数据将按需获取）...")
            df_list = ak.stock_info_a_code_name()
            # 构建最小可用的数据集
            df = df_list.rename(columns={"code": "代码", "name": "名称"})
            # 添加必要的列（估值数据将在 _extract_realtime_data 中补充）
            df["最新价"] = 0.0
            df["涨跌幅"] = 0.0
            df["涨跌额"] = 0.0
            df["成交量"] = 0.0
            df["成交额"] = 0.0
            df["最高"] = 0.0
            df["最低"] = 0.0
            df["今开"] = 0.0
            df["昨收"] = 0.0
            df["市盈率-动态"] = None
            df["市净率"] = None
            self._realtime_cache = df
            self._realtime_cache_time = current_time
            logger.info(f"使用最小数据集，获取 {len(df)} 条数据")
            return df
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"股票列表: {type(e).__name__}: {e}")
            logger.error(f"股票列表接口也失败: {e}")

        # 所有数据源都失败
        raise DataSourceError(
            f"所有数据源均失败: {'; '.join(errors)}",
            source="akshare",
            details={"errors": errors},
        )

    def _validate_realtime_columns(
        self, df: pd.DataFrame, source: str
    ) -> None:
        """验证实时行情数据列

        Args:
            df: 数据框
            source: 数据源名称

        Raises:
            ValueError: 缺少必需列
        """
        required_columns = ["代码", "名称", "最新价"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"数据源 {source} 缺少必需列: {missing}")

    def _normalize_code(self, value: object) -> str:
        """规范化股票代码"""
        text = str(value)
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) >= 6:
            return digits[-6:]
        return digits

    def _daily_symbol(self, code: str) -> str:
        """获取日线数据的市场前缀"""
        if code.startswith("6"):
            return f"sh{code}"
        if code.startswith(("8", "4")):
            return f"bj{code}"
        return f"sz{code}"

    def _normalize_daily_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """规范化日线数据列名"""
        column_map = {
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
        }

        df = df.rename(columns={k: v for k, v in column_map.items() if k in df.columns})

        required = ["date", "open", "high", "low", "close", "volume", "amount"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"日线数据缺少必需列: {missing}")

        return df[required]

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict[str, Any]:
        """获取实时行情

        Args:
            code: 股票代码，如 "000001"

        Returns:
            行情数据字典

        Raises:
            DataSourceError: 数据获取失败
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            return self._get_offline_quote(code)

        df = self._load_realtime_dataframe()

        normalized_codes = df["代码"].apply(self._normalize_code)
        result = df[normalized_codes == code]

        if result.empty:
            raise DataSourceError(
                f"股票代码不存在: {code}",
                source="akshare",
                code=code,
                details={"suggestion": "请检查股票代码是否正确"},
            )

        row = result.iloc[0]
        return self._extract_realtime_data(row)

    def _get_offline_quote(self, code: str) -> dict[str, Any]:
        """获取离线模拟数据"""
        return {
            "code": code,
            "name": "OFFLINE",
            "price": 10.5,
            "change_percent": 0.1,
            "change": 0.01,
            "volume": 1000000.0,
            "amount": 10000000.0,
            "high": 10.6,
            "low": 10.4,
            "open": 10.5,
            "prev_close": 10.49,
        }

    def _extract_realtime_data(self, row: pd.Series) -> dict[str, Any]:
        """从 DataFrame 行提取实时行情数据"""
        data = {
            "code": str(row["代码"]),
            "name": str(row["名称"]),
            "price": self._safe_float(row.get("最新价")),
            "change_percent": self._safe_float(row.get("涨跌幅")),
            "change": self._safe_float(row.get("涨跌额")),
            "volume": self._safe_float(row.get("成交量")),
            "amount": self._safe_float(row.get("成交额")),
            "high": self._safe_float(row.get("最高")),
            "low": self._safe_float(row.get("最低")),
            "open": self._safe_float(row.get("今开")),
            "prev_close": self._safe_float(row.get("昨收")),
            # 估值数据（尝试多种列名）
            "pe": self._safe_float(row.get("市盈率-动态") or row.get("市盈率")),
            "pb": self._safe_float(row.get("市净率")),
            "pe_ttm": self._safe_float(row.get("市盈率-TTM")),
            "total_market_value": self._safe_float(row.get("总市值")),
            "circulating_market_value": self._safe_float(row.get("流通市值")),
            "turnover_rate": self._safe_float(row.get("换手率")),
            "volume_ratio": self._safe_float(row.get("量比")),
            "bid_price": self._safe_float(row.get("买一")),
            "ask_price": self._safe_float(row.get("卖一")),
        }

        # 如果缺少估值数据，尝试从百度获取
        if data["pe"] == 0 or data["pb"] == 0:
            valuation = self._get_valuation_from_baidu(data["code"])
            if data["pe"] == 0 and valuation.get("pe"):
                data["pe"] = valuation["pe"]
            if data["pb"] == 0 and valuation.get("pb"):
                data["pb"] = valuation["pb"]
            if valuation.get("pe_ttm"):
                data["pe_ttm"] = valuation["pe_ttm"]

        return data

    # 估值数据缓存
    _valuation_cache: dict[str, tuple[float, dict[str, float]]] = {}

    def _get_valuation_from_baidu(self, code: str) -> dict[str, float]:
        """从百度股市通获取估值数据

        Args:
            code: 股票代码

        Returns:
            估值数据字典 {"pe": x, "pb": y, "pe_ttm": z}
        """
        import time

        # 检查缓存（5分钟有效期）
        current_time = time.time()
        if code in self._valuation_cache:
            cache_time, cache_data = self._valuation_cache[code]
            if current_time - cache_time < 300:
                return cache_data

        result: dict[str, float] = {}

        try:
            # 获取市盈率(TTM)
            try:
                df = ak.stock_zh_valuation_baidu(symbol=code, indicator="市盈率(TTM)")
                if not df.empty:
                    result["pe_ttm"] = self._safe_float(df.iloc[-1]["value"])
                    result["pe"] = result["pe_ttm"]
            except Exception:
                pass

            # 获取市净率
            try:
                df = ak.stock_zh_valuation_baidu(symbol=code, indicator="市净率")
                if not df.empty:
                    result["pb"] = self._safe_float(df.iloc[-1]["value"])
            except Exception:
                pass

            # 更新缓存
            if result:
                self._valuation_cache[code] = (current_time, result)

        except Exception as e:
            logger.debug(f"获取 {code} 估值数据失败: {e}")

        return result

    def _safe_float(self, value: Any) -> float:
        """安全转换为浮点数"""
        if value is None or (isinstance(value, float) and pd.isna(value)):
            return 0.0
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    @async_wrap
    def get_daily_quotes(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> pd.DataFrame:
        """获取日线行情

        优先级：
        1. 新浪数据源 stock_zh_a_daily（更稳定，不需要 mini-racer）
        2. 东方财富数据源 stock_zh_a_hist（数据更全，但可能触发 mini-racer）

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame，包含 OHLCV 数据

        Raises:
            DataSourceError: 数据获取失败
        """
        errors: list[str] = []

        # 优先使用新浪数据源（更稳定）
        try:
            symbol = self._daily_symbol(code)
            kwargs: dict[str, Any] = {"symbol": symbol, "adjust": "qfq"}

            if start_date:
                kwargs["start_date"] = start_date.strftime("%Y%m%d")
            if end_date:
                kwargs["end_date"] = end_date.strftime("%Y%m%d")

            df = ak.stock_zh_a_daily(**kwargs)
            df = self._filter_by_date(df, start_date, end_date)
            return self._normalize_daily_dataframe(df)
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"新浪: {type(e).__name__}: {e} (type={error_type})")
            logger.warning(f"新浪数据源 stock_zh_a_daily 失败: {e} (type={error_type})")

        # 备用：东方财富数据源
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                adjust="qfq",
            )
            df = self._filter_by_date(df, start_date, end_date)
            return self._normalize_daily_dataframe(df)
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"东方财富: {type(e).__name__}: {e} (type={error_type})")
            logger.error(f"东方财富数据源 stock_zh_a_hist 也失败: {e}")

        raise DataSourceError(
            f"获取日线数据失败: {'; '.join(errors)}",
            source="akshare",
            code=code,
            details={"errors": errors, "code": code},
        )

    def _filter_by_date(
        self,
        df: pd.DataFrame,
        start_date: Optional[date],
        end_date: Optional[date],
    ) -> pd.DataFrame:
        """按日期范围过滤数据"""
        if df.empty:
            return df

        # 确定日期列名
        date_col = None
        for col in ["date", "日期"]:
            if col in df.columns:
                date_col = col
                break

        if date_col is None:
            return df

        if start_date:
            start_str = start_date.strftime("%Y-%m-%d")
            df = df[df[date_col] >= start_str]
        if end_date:
            end_str = end_date.strftime("%Y-%m-%d")
            df = df[df[date_col] <= end_str]

        return df

    @async_wrap
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A股股票列表

        优先级：
        1. 新浪数据源 stock_info_a_code_name（更稳定）
        2. 东方财富数据源 stock_zh_a_spot_em（数据更全）
        """
        errors: list[str] = []

        # 优先使用新浪数据源
        try:
            df = ak.stock_info_a_code_name()
            return df.rename(columns={"code": "code", "name": "name"})
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"新浪: {type(e).__name__}: {e}")
            logger.warning(f"新浪数据源 stock_info_a_code_name 失败: {e}")

        # 备用：东方财富数据源
        try:
            df = ak.stock_zh_a_spot_em()
            return df[["代码", "名称"]].rename(columns={"代码": "code", "名称": "name"})
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"东方财富: {type(e).__name__}: {e}")
            logger.error(f"东方财富数据源也失败: {e}")

        raise DataSourceError(
            f"获取股票列表失败: {'; '.join(errors)}",
            source="akshare",
            details={"errors": errors},
        )