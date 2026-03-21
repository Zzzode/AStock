"""行情服务 - 支持多数据源、缓存和错误处理

数据源优先级：
1. Baostock：稳定可靠，适合历史数据和估值数据（T+1）
2. AkShare：实时行情补充（不稳定时降级处理）
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


# 交易时段定义（北京时间）
MORNING_OPEN = datetime_time(9, 30)
MORNING_CLOSE = datetime_time(11, 30)
AFTERNOON_OPEN = datetime_time(13, 0)
AFTERNOON_CLOSE = datetime_time(15, 0)


def is_trading_hours() -> bool:
    """判断当前是否在交易时段"""
    now = datetime.now().time()
    # 周末不交易
    if datetime.now().weekday() >= 5:
        return False
    # 交易时段判断
    return (
        (MORNING_OPEN <= now <= MORNING_CLOSE)
        or (AFTERNOON_OPEN <= now <= AFTERNOON_CLOSE)
    )


def get_dynamic_ttl(cache_type: str) -> int:
    """根据交易时段动态调整 TTL

    交易时段：实时行情缓存更短
    非交易时段：可以缓存更长时间
    """
    base_ttls = {
        "realtime": 3,
        "daily": 300,
    }

    if cache_type not in base_ttls:
        return 60

    if not is_trading_hours():
        # 非交易时段，缓存时间延长 10 倍
        return base_ttls[cache_type] * 10

    return base_ttls[cache_type]


class QuoteService:
    """行情服务 - 支持多数据源、缓存、重试、动态 TTL

    数据源策略：
    - 日线数据：优先 Baostock（稳定，含估值数据）
    - 实时行情：优先 Baostock（最近交易日），失败则 AkShare
    """

    def __init__(
        self,
        db: Database,
        primary_client: Optional[Union[BaostockClient, AkShareClient]] = None,
        fallback_client: Optional[AkShareClient] = None,
    ):
        self.db = db
        self._cache = get_cache()

        # 主数据源（默认 Baostock）
        if primary_client is None:
            self.primary_client = BaostockClient()
        else:
            self.primary_client = primary_client

        # 备用数据源（AkShare）
        self.fallback_client = fallback_client or AkShareClient()

        # 兼容旧代码
        self.client = self.primary_client

        self._realtime_retry_attempts = 3
        self._realtime_retry_delays = (1.0, 2.0)
        self._daily_retry_attempts = 3
        self._daily_retry_delays = (1.0, 2.0)

    def _is_retryable_error(self, error: Exception) -> bool:
        """判断是否为可重试错误"""
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
        """验证并规范化股票代码

        Args:
            code: 股票代码

        Returns:
            规范化后的 6 位代码

        Raises:
            ValidationError: 代码格式错误
        """
        if not code or not isinstance(code, str):
            raise ValidationError(
                "股票代码不能为空", field="code", value=repr(code)
            )

        code = code.strip()

        # 提取数字部分
        digits = "".join(ch for ch in code if ch.isdigit())

        if len(digits) != 6:
            raise ValidationError(
                f"股票代码格式错误: {code}，应为 6 位数字",
                field="code",
                value=code,
                details={"extracted_digits": digits, "length": len(digits)},
            )

        # 验证市场前缀
        first_digit = digits[0]
        market_info = {
            "0": "深市主板",
            "3": "创业板",
            "6": "沪市",
            "8": "北交所",
            "4": "北交所",
        }

        market = market_info.get(first_digit, "未知市场")
        logger.debug(f"股票代码验证通过: {digits} ({market})")

        return digits

    def _build_cache_key(self, prefix: str, *parts: Any) -> str:
        """构建缓存键

        将 None 转换为 "all" 以保持语义一致性
        """
        normalized_parts = [
            "all" if p is None else str(p)
            for p in parts
        ]
        return f"{prefix}:{':'.join(normalized_parts)}"

    async def get_realtime(self, code: str) -> dict[str, Any]:
        """获取实时行情（带缓存和动态 TTL）

        数据源优先级：
        1. Baostock（最近交易日数据，含估值）
        2. AkShare（实时数据，不稳定时降级）

        Args:
            code: 股票代码

        Returns:
            实时行情数据

        Raises:
            ValidationError: 股票代码格式错误
            DataSourceError: 数据获取失败
        """
        code = self._validate_stock_code(code)
        cache_key = self._build_cache_key("quote", code)
        ttl = get_dynamic_ttl("realtime")

        async def _fetch_realtime() -> dict[str, Any]:
            # 优先使用主数据源
            if isinstance(self.primary_client, BaostockClient):
                try:
                    result = await self.primary_client.get_realtime_quote(code)
                    logger.debug(f"Baostock 获取行情成功: {code}")
                    return result
                except Exception as e:
                    logger.warning(f"Baostock 获取行情失败，切换到 AkShare: {e}")

            # 降级到 AkShare
            try:
                result = await self.fallback_client.get_realtime_quote(code)
                logger.debug(f"AkShare 获取行情成功: {code}")
                return result
            except Exception as e:
                logger.error(f"所有数据源获取行情失败: {e}")
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
                return result

            except DataSourceError:
                raise
            except ValueError as e:
                logger.warning(f"股票代码不存在: {code}")
                raise DataSourceError(
                    f"股票代码 {code} 不存在",
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
                        f"获取实时行情失败，准备重试: {code}, "
                        f"attempt={attempt + 1}, error={e}"
                    )
                    self._cache.invalidate("realtime", cache_key)
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"获取实时行情失败: {code}, error={e}")
                raise DataSourceError(
                    f"获取实时行情失败: {e}",
                    source="multi",
                    code=code,
                    details={"attempts": attempt + 1, "last_error": str(e)},
                ) from e

        raise DataSourceError(
            f"获取实时行情失败（已达最大重试次数）",
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
        """获取日线数据（带缓存和优化）

        数据源优先级：
        1. Baostock（稳定，含 PE/PB 估值数据）
        2. AkShare（备用）
        3. 本地数据库（最后降级）

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            save: 是否保存到数据库
            limit: 返回数据条数限制，如果指定则会计算 start_date

        Returns:
            日线 DataFrame（含 pe, pb 列）

        Raises:
            ValidationError: 参数验证失败
            DataSourceError: 数据获取失败
        """
        code = self._validate_stock_code(code)

        # 如果指定了 limit 但没有 start_date，计算 start_date
        if limit is not None and start_date is None:
            if end_date is None:
                end_date = date.today()
            # 考虑周末和节假日，按 limit * 1.5 天计算
            start_date = end_date - timedelta(days=int(limit * 1.5))

        cache_key = self._build_cache_key("daily", code, start_date, end_date)
        ttl = get_dynamic_ttl("daily")

        async def _fetch_daily() -> pd.DataFrame:
            # 优先使用 Baostock
            if isinstance(self.primary_client, BaostockClient):
                try:
                    df = await self.primary_client.get_daily_quotes(code, start_date, end_date)
                    if not df.empty:
                        logger.debug(f"Baostock 获取日线成功: {code}, {len(df)} 条")
                        return df
                except Exception as e:
                    logger.warning(f"Baostock 获取日线失败，切换到 AkShare: {e}")

            # 降级到 AkShare
            try:
                df = await self.fallback_client.get_daily_quotes(code, start_date, end_date)
                logger.debug(f"AkShare 获取日线成功: {code}, {len(df)} 条")
                return df
            except Exception as e:
                logger.error(f"所有数据源获取日线失败: {e}")
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
                        f"获取日线数据失败，准备重试: {code}, "
                        f"attempt={attempt + 1}, error={e}"
                    )
                    self._cache.invalidate("daily", cache_key)
                    await asyncio.sleep(delay)
                    continue

                logger.error(f"获取日线数据失败: {code}, error={e}")
                break

        # 网络失败，尝试从本地数据库读取
        fallback_limit = limit or 100
        try:
            quotes = await self.db.get_daily_quotes(code, limit=fallback_limit)
        except Exception as e:
            raise DataSourceError(
                f"获取日线数据失败（本地回退也失败）: {e}",
                source="multi",
                code=code,
                details={"fallback_error": str(e)},
            ) from e

        if not quotes:
            error_msg = str(last_error) if last_error else "未知错误"
            raise DataSourceError(
                f"获取日线数据失败，且本地无历史数据: {error_msg}",
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
        logger.warning(f"日线数据回退到本地缓存: {code}, count={len(df)}")
        return df

    async def _save_daily_quotes(self, code: str, df: pd.DataFrame) -> None:
        """保存日线数据到数据库（优化版）

        使用 itertuples 替代 iterrows 提升性能
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
                logger.warning(f"跳过无效数据行: {row}, error={e}")
                continue

        if quotes:
            await self.db.save_daily_quotes(quotes)
            logger.debug(f"保存日线数据: {code}, {len(quotes)} 条")

    async def refresh_stocks(self) -> int:
        """刷新股票列表

        Returns:
            更新的股票数量

        Raises:
            DataSourceError: 数据获取失败
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

            logger.info(f"刷新股票列表完成: {count} 只")
            return count

        except Exception as e:
            logger.error("刷新股票列表失败", exc_info=True)
            raise DataSourceError(
                f"刷新股票列表失败: {e}",
                source="akshare",
                details={"error": str(e)},
            ) from e

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