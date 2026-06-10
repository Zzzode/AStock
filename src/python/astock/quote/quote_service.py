"""Quote service - supports multiple data sources, caching, and error handling

Data source priority:
1. Baostock: stable and reliable, suitable for historical and valuation data (T+1)
2. AkShare: real-time quote supplement (degrades gracefully when unstable)
"""

import asyncio
from datetime import date, datetime, time as datetime_time, timedelta
from typing import Any, Optional, Union, cast

import pandas as pd

from .akshare_client import AkShareClient
from .baostock_client import BaostockClient
from ..storage import Database, DailyQuote, Stock
from ..utils import DataSourceError, ValidationError, get_logger
from ..utils.cache import get_cache

logger = get_logger("quote_service")


# Trading session definitions (Beijing time)
MORNING_OPEN = datetime_time(9, 30)
MORNING_CLOSE = datetime_time(11, 30)
AFTERNOON_OPEN = datetime_time(13, 0)
AFTERNOON_CLOSE = datetime_time(15, 0)


def is_trading_hours() -> bool:
    """Check whether the current time is within trading hours"""
    now = datetime.now().time()
    # No trading on weekends
    if datetime.now().weekday() >= 5:
        return False
    # Trading session check
    return (
        (MORNING_OPEN <= now <= MORNING_CLOSE)
        or (AFTERNOON_OPEN <= now <= AFTERNOON_CLOSE)
    )


def get_dynamic_ttl(cache_type: str) -> int:
    """Dynamically adjust TTL based on trading session

    During trading hours: shorter cache for real-time quotes
    Outside trading hours: longer cache duration
    """
    base_ttls = {
        "realtime": 3,
        "daily": 300,
    }

    if cache_type not in base_ttls:
        return 60

    if not is_trading_hours():
        # Outside trading hours, extend cache duration by 10x
        return base_ttls[cache_type] * 10

    return base_ttls[cache_type]


class QuoteService:
    """Quote service - supports multiple data sources, caching, retry, and dynamic TTL

    Data source strategy:
    - Daily data: prefer Baostock (stable, includes valuation data)
    - Real-time quotes: prefer Baostock (latest trading day), fallback to AkShare on failure
    """

    def __init__(
        self,
        db: Database,
        primary_client: Optional[Union[BaostockClient, AkShareClient]] = None,
        fallback_client: Optional[AkShareClient] = None,
    ):
        self.db = db
        self._cache = get_cache()

        # Primary data source (default: Baostock)
        if primary_client is None:
            self.primary_client = BaostockClient()
        else:
            self.primary_client = primary_client

        # Fallback data source (AkShare)
        self.fallback_client = fallback_client or AkShareClient()

        # Backward compatibility
        self.client = self.primary_client

        self._realtime_retry_attempts = 3
        self._realtime_retry_delays = (1.0, 2.0)
        self._daily_retry_attempts = 3
        self._daily_retry_delays = (1.0, 2.0)

    def _is_retryable_error(self, error: Exception) -> bool:
        """Determine whether the error is retryable"""
        current: Optional[BaseException] = error
        retryable_name_tokens = (
            "Connection",
            "Timeout",
            "RemoteDisconnected",
            "ProtocolError",
            "MaxRetryError",
            "ChunkedEncoding",
        )

        while current is not None:
            if isinstance(current, (ConnectionError, TimeoutError, OSError)):
                return True
            error_name = type(current).__name__
            if any(token in error_name for token in retryable_name_tokens):
                return True
            current = current.__cause__ or current.__context__

        return False

    def _validate_stock_code(self, code: str) -> str:
        """Validate and normalize a stock code

        Args:
            code: Stock code

        Returns:
            Normalized 6-digit code

        Raises:
            ValidationError: Invalid code format
        """
        if not code or not isinstance(code, str):
            raise ValidationError(
                "Stock code cannot be empty", field="code", value=repr(code)
            )

        code = code.strip()

        # Extract digit portion
        digits = "".join(ch for ch in code if ch.isdigit())

        if len(digits) != 6:
            raise ValidationError(
                f"Invalid stock code format: {code}, expected 6 digits",
                field="code",
                value=code,
                details={"extracted_digits": digits, "length": len(digits)},
            )

        # Validate market prefix
        first_digit = digits[0]
        market_info = {
            "0": "Shenzhen Main Board",
            "3": "ChiNext",
            "6": "Shanghai",
            "8": "BSE (Beijing Stock Exchange)",
            "4": "BSE (Beijing Stock Exchange)",
        }

        market = market_info.get(first_digit, "Unknown market")
        logger.debug(f"Stock code validated: {digits} ({market})")

        return digits

    def _build_cache_key(self, prefix: str, *parts: Any) -> str:
        """Build a cache key

        Converts None to "all" for semantic consistency
        """
        normalized_parts = [
            "all" if p is None else str(p)
            for p in parts
        ]
        return f"{prefix}:{':'.join(normalized_parts)}"

    def _classify_quote_data_quality(self, quote: dict[str, Any]) -> str:
        """Classify the quality level of quote data"""
        if not quote:
            return "unavailable"

        if quote.get("is_realtime") is False:
            return "daily_only"

        core_fields = (
            quote.get("price", 0),
            quote.get("open", 0),
            quote.get("high", 0),
            quote.get("low", 0),
            quote.get("volume", 0),
            quote.get("amount", 0),
        )
        has_live_like_fields = any(bool(v) for v in core_fields)
        has_snapshot_only_fields = any(
            quote.get(key) not in (None, 0, 0.0, "")
            for key in ("name", "pe", "pb", "pe_ttm")
        )

        if has_live_like_fields:
            return "full_realtime"
        if has_snapshot_only_fields:
            return "snapshot_degraded"
        return "unavailable"

    async def get_realtime(self, code: str) -> dict[str, Any]:
        """Get real-time quote (with caching and dynamic TTL)

        Data source priority:
        1. Baostock (latest trading day data, includes valuation)
        2. AkShare (real-time data, degrades gracefully when unstable)

        Args:
            code: Stock code

        Returns:
            Real-time quote data

        Raises:
            ValidationError: Invalid stock code format
            DataSourceError: Failed to fetch data
        """
        code = self._validate_stock_code(code)
        cache_key = self._build_cache_key("quote", code)
        ttl = get_dynamic_ttl("realtime")

        async def _fetch_realtime() -> dict[str, Any]:
            # Prefer primary data source
            if isinstance(self.primary_client, BaostockClient):
                try:
                    result = await self.primary_client.get_realtime_quote(code)
                    logger.debug(f"Baostock quote fetched successfully: {code}")
                    return result
                except Exception as e:
                    logger.warning(f"Baostock quote fetch failed, switching to AkShare: {e}")

            # Fallback to AkShare
            try:
                result = await self.fallback_client.get_realtime_quote(code)
                logger.debug(f"AkShare quote fetched successfully: {code}")
                return result
            except Exception as e:
                logger.error(f"All data sources failed to fetch quote: {e}")
                raise

        last_error: Optional[Exception] = None

        for attempt in range(self._realtime_retry_attempts):
            try:
                result: dict[str, Any] = await self._cache.get_or_set(
                    "realtime",
                    cache_key,
                    _fetch_realtime,
                    ttl=ttl,
                )
                if not result.get("name"):
                    stock_info = await self.get_stock_info(code)
                    if stock_info and stock_info.get("name"):
                        result["name"] = stock_info["name"]
                result["data_quality"] = self._classify_quote_data_quality(result)
                return result

            except DataSourceError:
                raise
            except ValueError as e:
                logger.warning(f"Stock code does not exist: {code}")
                raise DataSourceError(
                    f"Stock code {code} does not exist",
                    source="multi",
                    code=code,
                    details={"original_error": str(e)},
                ) from e
            except Exception as e:
                last_error = e
                should_retry = self._is_retryable_error(e)
                last_attempt = attempt >= self._realtime_retry_attempts - 1

                if should_retry and not last_attempt:
                    delay = self._realtime_retry_delays[
                        min(attempt, len(self._realtime_retry_delays) - 1)
                    ]
                    logger.warning(
                        f"Failed to fetch real-time quote, retrying: {code}, "
                        f"attempt={attempt + 1}, error={e}"
                    )
                    self._cache.invalidate("realtime", cache_key)
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"Failed to fetch real-time quote: {code}, error={e}")
                raise DataSourceError(
                    f"Failed to fetch real-time quote: {e}",
                    source="multi",
                    code=code,
                    details={"attempts": attempt + 1, "last_error": str(e)},
                ) from e

        raise DataSourceError(
            f"Failed to fetch real-time quote (max retries reached)",
            source="multi",
            code=code,
            details={"last_error": str(last_error) if last_error else None},
        )

    async def get_daily(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save: bool = True,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """Get daily candlestick data (with caching and optimization)

        Data source priority:
        1. Baostock (stable, includes PE/PB valuation data)
        2. AkShare (fallback)
        3. Local database (last resort)

        Args:
            code: Stock code
            start_date: Start date
            end_date: End date
            save: Whether to save to database
            limit: Limit on number of records returned; if specified, start_date is calculated accordingly

        Returns:
            Daily DataFrame (includes pe, pb columns)

        Raises:
            ValidationError: Parameter validation failed
            DataSourceError: Failed to fetch data
        """
        code = self._validate_stock_code(code)

        # If limit is specified but start_date is not, calculate start_date
        if limit is not None and start_date is None:
            if end_date is None:
                end_date = date.today()
            # Account for weekends and holidays, use limit * 1.5 days
            start_date = end_date - timedelta(days=int(limit * 1.5))

        cache_key = self._build_cache_key("daily", code, start_date, end_date)
        ttl = get_dynamic_ttl("daily")

        async def _fetch_daily() -> pd.DataFrame:
            # Prefer Baostock
            if isinstance(self.primary_client, BaostockClient):
                try:
                    df = await self.primary_client.get_daily_quotes(code, start_date, end_date)
                    if not df.empty:
                        logger.debug(f"Baostock daily data fetched successfully: {code}, {len(df)} records")
                        return df
                except Exception as e:
                    logger.warning(f"Baostock daily data fetch failed, switching to AkShare: {e}")

            # Fallback to AkShare
            try:
                df = await self.fallback_client.get_daily_quotes(code, start_date, end_date)
                logger.debug(f"AkShare daily data fetched successfully: {code}, {len(df)} records")
                return df
            except Exception as e:
                logger.error(f"All data sources failed to fetch daily data: {e}")
                raise

        last_error: Optional[Exception] = None

        for attempt in range(self._daily_retry_attempts):
            try:
                df: pd.DataFrame = await self._cache.get_or_set(
                    "daily",
                    cache_key,
                    _fetch_daily,
                    ttl=ttl,
                )

                if save and not df.empty:
                    await self._save_daily_quotes(code, df)

                return df

            except DataSourceError:
                raise
            except Exception as e:
                last_error = e
                should_retry = self._is_retryable_error(e)
                last_attempt = attempt >= self._daily_retry_attempts - 1

                if should_retry and not last_attempt:
                    delay = self._daily_retry_delays[
                        min(attempt, len(self._daily_retry_delays) - 1)
                    ]
                    logger.warning(
                        f"Failed to fetch daily data, retrying: {code}, "
                        f"attempt={attempt + 1}, error={e}"
                    )
                    self._cache.invalidate("daily", cache_key)
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"Failed to fetch daily data: {code}, error={e}")
                break

        # Network failure, try reading from local database
        fallback_limit = limit or 100
        try:
            quotes = await self.db.get_daily_quotes(code, limit=fallback_limit)
        except Exception as e:
            raise DataSourceError(
                f"Failed to fetch daily data (local fallback also failed): {e}",
                source="multi",
                code=code,
                details={"fallback_error": str(e)},
            ) from e

        if not quotes:
            error_msg = str(last_error) if last_error else "Unknown error"
            raise DataSourceError(
                f"Failed to fetch daily data, and no local historical data available: {error_msg}",
                source="akshare",
                code=code,
                details={
                    "network_error": error_msg,
                    "local_records": 0,
                },
            )

        df = pd.DataFrame(
            [
                {
                    "date": q.date,
                    "open": q.open,
                    "high": q.high,
                    "low": q.low,
                    "close": q.close,
                    "volume": q.volume,
                    "amount": q.amount,
                }
                for q in quotes
            ]
        )
        df = df.sort_values("date").reset_index(drop=True)
        logger.warning(f"Daily data fell back to local cache: {code}, count={len(df)}")
        return df

    async def _save_daily_quotes(self, code: str, df: pd.DataFrame) -> None:
        """Save daily quotes to database (optimized version)

        Uses itertuples instead of iterrows for better performance
        """
        if df.empty:
            return

        quotes = []
        for row in df.itertuples(index=False):
            try:
                row_date = row.date
                if isinstance(row_date, str):
                    row_date = datetime.strptime(row_date, "%Y-%m-%d").date()

                quotes.append(
                    DailyQuote(
                        code=code,
                        date=row_date,
                        open=float(row.open),
                        high=float(row.high),
                        low=float(row.low),
                        close=float(row.close),
                        volume=float(row.volume),
                        amount=float(row.amount),
                    )
                )
            except (AttributeError, ValueError, TypeError) as e:
                logger.warning(f"Skipping invalid data row: {row}, error={e}")
                continue

        if quotes:
            await self.db.save_daily_quotes(quotes)
            logger.debug(f"Saved daily data: {code}, {len(quotes)} records")

    async def refresh_stocks(self) -> int:
        """Refresh the stock list

        Returns:
            Number of stocks updated

        Raises:
            DataSourceError: Failed to fetch data
        """
        try:

            async def _fetch_stock_list() -> pd.DataFrame:
                return await self.client.get_stock_list()

            df: pd.DataFrame = await self._cache.get_or_set(
                "stock_list", "all_stocks", _fetch_stock_list
            )

            count = 0
            for row in df.itertuples(index=False):
                stock = Stock(code=row.code, name=row.name)
                await self.db.save_stock(stock)
                count += 1

            logger.info(f"Stock list refresh completed: {count} stocks")
            return count

        except Exception as e:
            logger.error("Failed to refresh stock list", exc_info=True)
            raise DataSourceError(
                f"Failed to refresh stock list: {e}",
                source="akshare",
                details={"error": str(e)},
            ) from e

    async def get_stock_info(
        self,
        code: str,
        allow_remote: bool = True,
    ) -> Optional[dict[str, Any]]:
        """Get basic stock information

        Prefers local database; falls back to stock list API when missing.
        """
        code = self._validate_stock_code(code)

        try:
            stock = await self.db.get_stock(code)
            if stock is not None:
                return {
                    "code": stock.code,
                    "name": stock.name,
                    "industry": stock.industry,
                    "list_date": stock.list_date,
                }
        except Exception as e:
            logger.debug(f"Failed to read stock info locally: {code}, error={e}")

        if not allow_remote:
            return None

        try:
            stock_list = await self.client.get_stock_list()
            result = stock_list[stock_list["code"].astype(str) == code]
            if result.empty:
                return None

            row = result.iloc[0]
            stock = Stock(
                code=code,
                name=str(row.get("name", "")),
                industry=None,
                list_date=None,
            )
            try:
                await self.db.save_stock(stock)
            except Exception as e:
                logger.debug(f"Failed to cache stock info: {code}, error={e}")

            return {
                "code": stock.code,
                "name": stock.name,
                "industry": stock.industry,
                "list_date": stock.list_date,
            }
        except Exception as e:
            logger.debug(f"Failed to read stock info from remote: {code}, error={e}")
            return None

    def invalidate_cache(self, code: Optional[str] = None) -> None:
        """Invalidate cache

        Args:
            code: Stock code; None means clear all
        """
        if code:
            self._cache.invalidate("realtime", f"quote:{code}")
            self._cache.invalidate("daily", code)
        else:
            self._cache.invalidate("realtime")
            self._cache.invalidate("daily")
