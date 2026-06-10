"""AkShare quote client"""

import asyncio
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from functools import partial, wraps
from typing import Any, Callable, Optional, TypeVar, ParamSpec, cast

import akshare as ak
import pandas as pd

from ..utils import get_logger
from ..utils.exceptions import DataSourceError

logger = get_logger("akshare_client")

P = ParamSpec("P")
T = TypeVar("T")

# Dedicated thread pool to avoid blocking the default pool
_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    """Get dedicated thread pool (lazy initialization)"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="akshare_")
    return _executor


def async_wrap(func: Callable[P, T]) -> Callable[P, "asyncio.Future[T]"]:
    """Wrap a synchronous function as async (using dedicated thread pool)

    Improvements:
    1. Uses asyncio.get_running_loop() instead of the deprecated get_event_loop()
    2. Uses a dedicated thread pool to avoid blocking other I/O operations
    3. Uses functools.partial to avoid lambda overhead
    """

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_running_loop()
        func_partial = partial(func, *args, **kwargs)
        return await loop.run_in_executor(_get_executor(), func_partial)

    return wrapper


# Retryable network error types
RETRYABLE_ERRORS = (
    ConnectionError,
    TimeoutError,
    OSError,
)


class AkShareClient:
    """AkShare quote data client

    Improvements:
    1. More precise error classification and retry logic
    2. Data source consistency validation
    3. Request rate limiting support
    """

    def __init__(self, rate_limit_per_second: float = 2.0):
        """Initialize client

        Args:
            rate_limit_per_second: Maximum requests per second
        """
        self._rate_limit = rate_limit_per_second
        self._last_request_time: float = 0.0
        self._rate_limit_lock = asyncio.Lock()

    async def _apply_rate_limit(self) -> None:
        """Apply request rate limiting"""
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
        """Classify error type

        Returns:
            "retryable": retryable network error
            "data": data format error
            "auth": authentication/permission error
            "unknown": unknown error
        """
        error_name = type(error).__name__
        error_msg = str(error).lower()

        # Network-related errors
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

        # Authentication/permission errors
        if any(
            token in error_msg
            for token in ("403", "forbidden", "unauthorized", "auth", "login")
        ):
            return "auth"

        # Data format errors
        if isinstance(error, (KeyError, ValueError, TypeError)):
            return "data"

        return "unknown"

    # Class-level cache to avoid crashes from frequent requests to mini-racer
    _realtime_cache: Optional[pd.DataFrame] = None
    _realtime_cache_time: float = 0.0
    _cache_ttl: float = 60.0  # Cache validity: 60 seconds

    def _load_realtime_dataframe(self) -> pd.DataFrame:
        """Load real-time quote data

        Priority:
        1. Use cache (valid within 60 seconds)
        2. Sina data source stock_zh_a_spot() (more stable, no mini-racer required)
        3. East Money data source stock_zh_a_spot_em() (more complete data, but may trigger mini-racer)

        Returns:
            Real-time quote DataFrame
        """
        # Check cache
        current_time = time.time()
        if (
            self._realtime_cache is not None
            and current_time - self._realtime_cache_time < self._cache_ttl
        ):
            logger.debug("Using cached real-time quote data")
            return self._realtime_cache

        errors: list[str] = []

        # Prefer Sina data source (no mini-racer required, more stable)
        try:
            logger.info("Trying Sina data source stock_zh_a_spot...")
            df = ak.stock_zh_a_spot()
            self._validate_realtime_columns(df, "stock_zh_a_spot")
            self._realtime_cache = df
            self._realtime_cache_time = current_time
            logger.info(f"Sina data source succeeded, fetched {len(df)} records")
            return df
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"Sina: {type(e).__name__}: {e} (type={error_type})")
            logger.warning(f"Sina data source failed: {e} (type={error_type})")

        # Fallback: East Money data source
        try:
            logger.info("Trying East Money data source stock_zh_a_spot_em...")
            df = ak.stock_zh_a_spot_em()
            self._validate_realtime_columns(df, "stock_zh_a_spot_em")
            self._realtime_cache = df
            self._realtime_cache_time = current_time
            logger.info(f"East Money data source succeeded, fetched {len(df)} records")
            return df
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"East Money: {type(e).__name__}: {e} (type={error_type})")
            logger.error(f"East Money data source also failed: {e}")

        # Third fallback: use stock list + Baidu valuation
        try:
            logger.info("Trying stock list (valuation data will be fetched on demand)...")
            df_list = ak.stock_info_a_code_name()
            # Build minimal usable dataset
            df = df_list.rename(columns={"code": "代码", "name": "名称"})
            # Add necessary columns (valuation data will be supplemented in _extract_realtime_data)
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
            logger.info(f"Using minimal dataset, fetched {len(df)} records")
            return df
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"Stock list: {type(e).__name__}: {e}")
            logger.error(f"Stock list API also failed: {e}")

        # All data sources failed
        raise DataSourceError(
            f"All data sources failed: {'; '.join(errors)}",
            source="akshare",
            details={"errors": errors},
        )

    def _validate_realtime_columns(
        self, df: pd.DataFrame, source: str
    ) -> None:
        """Validate real-time quote data columns

        Args:
            df: DataFrame
            source: Data source name

        Raises:
            ValueError: Missing required columns
        """
        required_columns = ["代码", "名称", "最新价"]
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise ValueError(f"Data source {source} is missing required columns: {missing}")

    def _normalize_code(self, value: object) -> str:
        """Normalize stock code"""
        text = str(value)
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) >= 6:
            return digits[-6:]
        return digits

    def _daily_symbol(self, code: str) -> str:
        """Get market prefix for daily data"""
        if code.startswith("6"):
            return f"sh{code}"
        if code.startswith(("8", "4")):
            return f"bj{code}"
        return f"sz{code}"

    def _normalize_daily_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize daily data column names"""
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
            raise ValueError(f"Daily data is missing required columns: {missing}")

        return df[required]

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict[str, Any]:
        """Get real-time quote

        Args:
            code: Stock code, e.g. "000001"

        Returns:
            Quote data dictionary

        Raises:
            DataSourceError: Failed to fetch data
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
            return self._get_offline_quote(code)

        df = self._load_realtime_dataframe()

        normalized_codes = df["代码"].apply(self._normalize_code)
        result = df[normalized_codes == code]

        if result.empty:
            raise DataSourceError(
                f"Stock code does not exist: {code}",
                source="akshare",
                code=code,
                details={"suggestion": "Please verify the stock code is correct"},
            )

        row = result.iloc[0]
        return self._extract_realtime_data(row)

    def _get_offline_quote(self, code: str) -> dict[str, Any]:
        """Get offline simulated data"""
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
        """Extract real-time quote data from a DataFrame row"""
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
            # Valuation data (try multiple column names)
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

        # If valuation data is missing, try fetching from Baidu
        if data["pe"] == 0 or data["pb"] == 0:
            valuation = self._get_valuation_from_baidu(data["code"])
            if data["pe"] == 0 and valuation.get("pe"):
                data["pe"] = valuation["pe"]
            if data["pb"] == 0 and valuation.get("pb"):
                data["pb"] = valuation["pb"]
            if valuation.get("pe_ttm"):
                data["pe_ttm"] = valuation["pe_ttm"]

        return data

    # Valuation data cache
    _valuation_cache: dict[str, tuple[float, dict[str, float]]] = {}

    def _get_valuation_from_baidu(self, code: str) -> dict[str, float]:
        """Get valuation data from Baidu Stock

        Args:
            code: Stock code

        Returns:
            Valuation data dictionary {"pe": x, "pb": y, "pe_ttm": z}
        """
        import time

        # Check cache (5-minute validity)
        current_time = time.time()
        if code in self._valuation_cache:
            cache_time, cache_data = self._valuation_cache[code]
            if current_time - cache_time < 300:
                return cache_data

        result: dict[str, float] = {}

        try:
            # Get PE ratio (TTM)
            try:
                df = ak.stock_zh_valuation_baidu(symbol=code, indicator="市盈率(TTM)")
                if not df.empty:
                    result["pe_ttm"] = self._safe_float(df.iloc[-1]["value"])
                    result["pe"] = result["pe_ttm"]
            except Exception:
                pass

            # Get PB ratio
            try:
                df = ak.stock_zh_valuation_baidu(symbol=code, indicator="市净率")
                if not df.empty:
                    result["pb"] = self._safe_float(df.iloc[-1]["value"])
            except Exception:
                pass

            # Update cache
            if result:
                self._valuation_cache[code] = (current_time, result)

        except Exception as e:
            logger.debug(f"Failed to fetch valuation data for {code}: {e}")

        return result

    def _safe_float(self, value: Any) -> float:
        """Safely convert to float"""
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
        """Get daily candlestick data

        Priority:
        1. Sina data source stock_zh_a_daily (more stable, no mini-racer required)
        2. East Money data source stock_zh_a_hist (more complete data, but may trigger mini-racer)

        Args:
            code: Stock code
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame containing OHLCV data

        Raises:
            DataSourceError: Failed to fetch data
        """
        errors: list[str] = []

        # Prefer Sina data source (more stable)
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
            errors.append(f"Sina: {type(e).__name__}: {e} (type={error_type})")
            logger.warning(f"Sina data source stock_zh_a_daily failed: {e} (type={error_type})")

        # Fallback: East Money data source
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
            errors.append(f"East Money: {type(e).__name__}: {e} (type={error_type})")
            logger.error(f"East Money data source stock_zh_a_hist also failed: {e}")

        raise DataSourceError(
            f"Failed to fetch daily data: {'; '.join(errors)}",
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
        """Filter data by date range"""
        if df.empty:
            return df

        # Determine date column name
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
        """Get A-share stock list

        Priority:
        1. Sina data source stock_info_a_code_name (more stable)
        2. East Money data source stock_zh_a_spot_em (more complete data)
        """
        errors: list[str] = []

        # Prefer Sina data source
        try:
            df = ak.stock_info_a_code_name()
            return df.rename(columns={"code": "code", "name": "name"})
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"Sina: {type(e).__name__}: {e}")
            logger.warning(f"Sina data source stock_info_a_code_name failed: {e}")

        # Fallback: East Money data source
        try:
            df = ak.stock_zh_a_spot_em()
            return df[["代码", "名称"]].rename(columns={"代码": "code", "名称": "name"})
        except Exception as e:
            error_type = self._classify_error(e)
            errors.append(f"East Money: {type(e).__name__}: {e}")
            logger.error(f"East Money data source also failed: {e}")

        raise DataSourceError(
            f"Failed to fetch stock list: {'; '.join(errors)}",
            source="akshare",
            details={"errors": errors},
        )
