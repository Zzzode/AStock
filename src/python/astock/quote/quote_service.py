"""行情服务 - 支持缓存和错误处理"""

import asyncio
from datetime import date, datetime
from typing import Optional, Any, cast
import pandas as pd

from .akshare_client import AkShareClient
from ..storage import Database, DailyQuote
from ..utils import get_logger, DataSourceError, ValidationError
from ..utils.cache import get_cache

logger = get_logger("quote_service")


class QuoteService:
    """行情服务 - 支持缓存和异步"""

    def __init__(self, db: Database):
        self.client = AkShareClient()
        self.db = db
        self._cache = get_cache()
        self._realtime_retry_attempts = 3
        self._realtime_retry_delays = (1.0, 2.0)
        self._daily_retry_attempts = 3
        self._daily_retry_delays = (1.0, 2.0)

    def _is_retryable_error(self, error: Exception) -> bool:
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

    async def get_realtime(self, code: str) -> dict[str, Any]:
        """获取实时行情（带缓存）

        Args:
            code: 股票代码

        Returns:
            实时行情数据

        Raises:
            ValidationError: 股票代码格式错误
            DataSourceError: 数据获取失败
        """
        # 验证股票代码
        if not code or not isinstance(code, str):
            raise ValidationError("股票代码不能为空", field="code", value=code)

        code = code.strip()
        if not code.isdigit() or len(code) != 6:
            raise ValidationError(
                f"股票代码格式错误: {code}，应为6位数字", field="code", value=code
            )

        cache_key = f"quote:{code}"
        async def _fetch_realtime() -> dict[str, Any]:
            return await self.client.get_realtime_quote(code)

        for attempt in range(self._realtime_retry_attempts):
            try:
                result: dict[str, Any] = await self._cache.get_or_set(
                    "realtime",
                    cache_key,
                    _fetch_realtime,
                )
                return result
            except ValueError as e:
                logger.warning(f"股票代码不存在: {code}")
                raise DataSourceError(
                    f"股票代码 {code} 不存在", source="akshare", code=code
                ) from e
            except Exception as e:
                should_retry = self._is_retryable_error(e)
                last_attempt = attempt >= self._realtime_retry_attempts - 1
                if should_retry and not last_attempt:
                    delay = self._realtime_retry_delays[min(attempt, len(self._realtime_retry_delays) - 1)]
                    logger.warning(f"获取实时行情失败，准备重试: {code}, attempt={attempt + 1}, error={e}")
                    self._cache.invalidate("realtime", cache_key)
                    await asyncio.sleep(delay)
                    continue
                logger.error(f"获取实时行情失败: {code}, error={e}")
                raise DataSourceError(
                    f"获取实时行情失败: {e}", source="akshare", code=code
                ) from e

        raise DataSourceError("获取实时行情失败", source="akshare", code=code)

    async def get_daily(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save: bool = True,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """获取日线数据（带缓存）

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            save: 是否保存到数据库

        Returns:
            日线 DataFrame

        Raises:
            ValidationError: 参数验证失败
            DataSourceError: 数据获取失败
        """
        if not code or len(code) != 6:
            raise ValidationError(f"股票代码格式错误: {code}", field="code", value=code)

        cache_key = f"daily:{code}:{start_date}:{end_date}"
        last_error: Optional[Exception] = None
        async def _fetch_daily() -> pd.DataFrame:
            return await self.client.get_daily_quotes(code, start_date, end_date)

        for attempt in range(self._daily_retry_attempts):
            try:
                df: pd.DataFrame = await self._cache.get_or_set(
                    "daily",
                    cache_key,
                    _fetch_daily,
                )

                if save and not df.empty:
                    quotes = [
                        DailyQuote(
                            code=code,
                            date=row["date"]
                            if isinstance(row["date"], date)
                            else datetime.strptime(row["date"], "%Y-%m-%d").date(),
                            open=float(row["open"]),
                            high=float(row["high"]),
                            low=float(row["low"]),
                            close=float(row["close"]),
                            volume=float(row["volume"]),
                            amount=float(row["amount"]),
                        )
                        for _, row in df.iterrows()
                    ]
                    await self.db.save_daily_quotes(quotes)
                    logger.debug(f"保存日线数据: {code}, {len(quotes)} 条")

                return df
            except Exception as e:
                should_retry = self._is_retryable_error(e)
                last_attempt = attempt >= self._daily_retry_attempts - 1
                if should_retry and not last_attempt:
                    delay = self._daily_retry_delays[min(attempt, len(self._daily_retry_delays) - 1)]
                    logger.warning(f"获取日线数据失败，准备重试: {code}, attempt={attempt + 1}, error={e}")
                    self._cache.invalidate("daily", cache_key)
                    await asyncio.sleep(delay)
                    continue
                last_error = e
                logger.error(f"获取日线数据失败: {code}, error={e}")
                break

        fallback_limit = limit or 100
        try:
            quotes = await self.db.get_daily_quotes(code, limit=fallback_limit)
        except Exception as e:
            raise DataSourceError(
                f"获取日线数据失败: {e}", source="akshare", code=code
            ) from e

        if not quotes:
            if last_error is not None:
                raise DataSourceError(
                    f"获取日线数据失败: {last_error}", source="akshare", code=code
                ) from last_error
            raise DataSourceError("获取日线数据失败", source="akshare", code=code)

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
        logger.warning(f"日线数据回退到本地缓存: {code}, count={len(df)}")
        return df

    async def refresh_stocks(self) -> int:
        """刷新股票列表

        Returns:
            更新的股票数量

        Raises:
            DataSourceError: 数据获取失败
        """
        from ..storage import Stock

        try:
            async def _fetch_stock_list() -> pd.DataFrame:
                return await self.client.get_stock_list()

            df: pd.DataFrame = await self._cache.get_or_set(
                "stock_list", "all_stocks", _fetch_stock_list
            )

            count = 0
            for _, row in df.iterrows():
                stock = Stock(code=row["code"], name=row["name"])
                await self.db.save_stock(stock)
                count += 1

            logger.info(f"刷新股票列表完成: {count} 只")
            return count

        except Exception as e:
            logger.error("刷新股票列表失败", exc_info=True)
            raise DataSourceError(f"刷新股票列表失败: {e}", source="akshare") from e

    def invalidate_cache(self, code: Optional[str] = None) -> None:
        """使缓存失效

        Args:
            code: 股票代码，None 表示清除所有
        """
        if code:
            self._cache.invalidate("realtime", f"quote:{code}")
            self._cache.invalidate("daily", code)
        else:
            self._cache.invalidate("realtime")
            self._cache.invalidate("daily")
