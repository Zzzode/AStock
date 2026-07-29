"""Baostock quote client - stable and reliable A-share data source

Baostock features:
- Officially maintained by Baostock, stable and reliable data
- Supports daily, weekly, and monthly candlestick data
- Supports PE, PB and other valuation data
- T+1 updates (today's data available next day)
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from functools import partial, wraps
from typing import Any, Callable, Optional, TypeVar, ParamSpec

import baostock as bs
import pandas as pd

from ..utils import get_logger
from ..utils.exceptions import DataSourceError

logger = get_logger("baostock_client")

P = ParamSpec("P")
T = TypeVar("T")

# Dedicated thread pool
_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    """Get dedicated thread pool"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="baostock_")
    return _executor


def async_wrap(func: Callable[P, T]) -> Callable[P, "asyncio.Future[T]"]:
    """Wrap a synchronous function as async"""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_running_loop()
        func_partial = partial(func, *args, **kwargs)
        return await loop.run_in_executor(_get_executor(), func_partial)

    return wrapper


class BaostockClient:
    """Baostock quote data client

    Advantages:
    - Stable and reliable data, officially maintained by Baostock
    - Supports PE, PB, market cap and other valuation data
    - Simple and stable API

    Limitations:
    - Data updated T+1 (today's data available next day)
    - No real-time quotes (needs to be combined with other data sources)
    """

    def __init__(self):
        self._logged_in = False
        self._login_lock = asyncio.Lock()

    def _ensure_login(self) -> None:
        """Ensure logged in (synchronous version)"""
        if self._logged_in:
            return

        try:
            lg = bs.login()
            if lg.error_code != "0":
                raise DataSourceError(
                    f"Baostock login failed: {lg.error_msg}",
                    source="baostock",
                )
            self._logged_in = True
            logger.info("Baostock login successful")
        except Exception as e:
            raise DataSourceError(
                f"Baostock login error: {e}",
                source="baostock",
            ) from e

    async def ensure_login(self) -> None:
        """Ensure logged in (async version)"""
        async with self._login_lock:
            if not self._logged_in:
                await async_wrap(self._ensure_login)()

    def _baostock_code(self, code: str) -> str:
        """Convert to Baostock format stock code

        Args:
            code: 6-digit stock code, e.g. "600036"

        Returns:
            Baostock format code, e.g. "sh.600036"
        """
        code = code.zfill(6)
        if code.startswith("6"):
            return f"sh.{code}"
        else:
            return f"sz.{code}"

    def _normalize_code(self, bs_code: str) -> str:
        """Extract plain code from Baostock code

        Args:
            bs_code: Baostock format code, e.g. "sh.600036"

        Returns:
            6-digit code, e.g. "600036"
        """
        return bs_code.split(".")[-1]

    @async_wrap
    def get_stock_list(self) -> pd.DataFrame:
        """Get A-share stock list

        Returns:
            DataFrame with columns: code, name
        """
        self._ensure_login()

        try:
            # Try data from the most recent trading days
            today = date.today()
            data_list = []

            for i in range(7):  # Try last 7 days
                query_date = today - timedelta(days=i)
                rs = bs.query_all_stock(day=query_date.strftime("%Y-%m-%d"))

                if rs.error_code != "0":
                    continue

                while rs.error_code == "0" and rs.next():
                    data_list.append(rs.get_row_data())

                if data_list:
                    logger.debug(f"Using stock list data from {query_date}")
                    break

            if not data_list:
                raise DataSourceError(
                    "Failed to fetch stock list: no data available in the last 7 days",
                    source="baostock",
                )

            # fields: code, tradeStatus, code_name
            df = pd.DataFrame(data_list, columns=["bs_code", "trade_status", "name"])

            # Filter main board, ChiNext, and STAR Market (exclude indices)
            # sh.6xxxxx Shanghai Main Board, sz.0xxxxx Shenzhen Main Board, sz.3xxxxx ChiNext
            df = df[df["bs_code"].str.match(r"^(sh\.6\d{5}|sz\.0\d{5}|sz\.3\d{5})$")]

            # Standardize codes
            df["code"] = df["bs_code"].str.replace(r"^(sh|sz)\.", "", regex=True)

            logger.info(f"Stock list fetched successfully: {len(df)} stocks")
            return df[["code", "name"]]

        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(
                f"Stock list fetch error: {e}",
                source="baostock",
            ) from e

    @async_wrap
    def get_daily_quotes(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: int = 120,  # Default: fetch 120 days of data to reduce network transfer
    ) -> pd.DataFrame:
        """Get daily candlestick data (including valuation data)

        Args:
            code: Stock code, e.g. "600036"
            start_date: Start date
            end_date: End date
            days: Default number of days to fetch if start_date is not specified

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount, pe, pb
        """
        self._ensure_login()

        # Default date range
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=days)

        bs_code = self._baostock_code(code)

        try:
            # Query daily data including valuation indicators
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,code,open,high,low,close,volume,amount,turn,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                frequency="d",
                adjustflag="2",  # Forward-adjusted
            )

            if rs.error_code != "0":
                raise DataSourceError(
                    f"Failed to fetch daily data: {rs.error_msg}",
                    source="baostock",
                    code=code,
                )

            data_list = []
            while rs.error_code == "0" and rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(f"No data available for stock {code}")
                return pd.DataFrame()

            df = pd.DataFrame(data_list, columns=rs.fields)

            # Type conversion
            df["date"] = pd.to_datetime(df["date"])
            for col in ["open", "high", "low", "close", "volume", "amount"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Valuation data
            df["pe"] = pd.to_numeric(df.get("peTTM"), errors="coerce")
            df["pb"] = pd.to_numeric(df.get("pbMRQ"), errors="coerce")
            df["ps"] = pd.to_numeric(df.get("psTTM"), errors="coerce")
            df["pcf"] = pd.to_numeric(df.get("pcfNcfTTM"), errors="coerce")

            # Amount (unit: thousands -> yuan)
            if "amount" in df.columns:
                df["amount"] = df["amount"] * 1000

            logger.debug(f"Fetched daily data for {code}: {len(df)} records")
            return df[["date", "open", "high", "low", "close", "volume", "amount", "pe", "pb", "ps", "pcf"]]

        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(
                f"Daily data fetch error: {e}",
                source="baostock",
                code=code,
            ) from e

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict[str, Any]:
        """Get "real-time" quote (actually the latest trading day's data)

        Baostock does not support real-time quotes; returns the latest trading day's daily data

        Args:
            code: Stock code

        Returns:
            Quote data dictionary
        """
        self._ensure_login()

        try:
            # Get data from the last 5 trading days
            end_date = date.today()
            start_date = end_date - timedelta(days=10)

            df = self.get_daily_quotes.__wrapped__(self, code, start_date, end_date)

            if df.empty:
                raise DataSourceError(
                    f"No data available for stock {code}",
                    source="baostock",
                    code=code,
                )

            # Take the latest record
            latest = df.iloc[-1]

            # Calculate price change
            prev_close = df.iloc[-2]["close"] if len(df) > 1 else latest["close"]
            change = latest["close"] - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0

            return {
                "code": code,
                "name": "",  # Baostock daily data does not include stock name
                "price": float(latest["close"]),
                "open": float(latest["open"]),
                "high": float(latest["high"]),
                "low": float(latest["low"]),
                "volume": float(latest["volume"]),
                "amount": float(latest["amount"]) if "amount" in latest else 0,
                "prev_close": float(prev_close),
                "change": float(change),
                "change_percent": float(change_percent),
                "pe": float(latest["pe"]) if pd.notna(latest.get("pe")) else None,
                "pb": float(latest["pb"]) if pd.notna(latest.get("pb")) else None,
                "date": latest["date"].strftime("%Y-%m-%d"),
                "is_realtime": False,  # Marked as non-real-time data
            }

        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(
                f"Quote data fetch error: {e}",
                source="baostock",
                code=code,
            ) from e

    @async_wrap
    def get_stocks_daily_quotes(
        self,
        codes: list[str],
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> pd.DataFrame:
        """Batch fetch daily data for multiple stocks

        Args:
            codes: List of stock codes
            start_date: Start date
            end_date: End date

        Returns:
            DataFrame with multi-index (code, date)
        """
        self._ensure_login()

        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=365)

        all_data = []

        for code in codes:
            try:
                df = self.get_daily_quotes.__wrapped__(self, code, start_date, end_date)
                if not df.empty:
                    df["code"] = code
                    all_data.append(df)
            except Exception as e:
                logger.warning(f"Failed to fetch data for {code}: {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"Batch daily data fetched: {len(codes)} stocks, {len(result)} records")
        return result

    def logout(self) -> None:
        """Logout"""
        if self._logged_in:
            bs.logout()
            self._logged_in = False
            logger.info("Baostock logged out")
