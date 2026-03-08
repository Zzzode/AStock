"""行情服务 - 支持缓存和错误处理"""

from datetime import date, datetime
from typing import Optional
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

    async def get_realtime(self, code: str) -> dict:
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

        try:
            # 使用缓存
            result = await self._cache.get_or_set(
                "realtime",
                f"quote:{code}",
                lambda: self.client.get_realtime_quote(code),
            )
            return result
        except ValueError as e:
            logger.warning(f"股票代码不存在: {code}")
            raise DataSourceError(
                f"股票代码 {code} 不存在", source="akshare", code=code
            ) from e
        except Exception as e:
            logger.error(f"获取实时行情失败: {code}", exc_info=True)
            raise DataSourceError(
                f"获取实时行情失败: {e}", source="akshare", code=code
            ) from e

    async def get_daily(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save: bool = True,
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

        try:
            # 构建缓存键
            cache_key = f"daily:{code}:{start_date}:{end_date}"

            df = await self._cache.get_or_set(
                "daily",
                cache_key,
                lambda: self.client.get_daily_quotes(code, start_date, end_date),
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
            logger.error(f"获取日线数据失败: {code}", exc_info=True)
            raise DataSourceError(
                f"获取日线数据失败: {e}", source="akshare", code=code
            ) from e

    async def refresh_stocks(self) -> int:
        """刷新股票列表

        Returns:
            更新的股票数量

        Raises:
            DataSourceError: 数据获取失败
        """
        from ..storage import Stock

        try:
            df = await self._cache.get_or_set(
                "stock_list", "all_stocks", lambda: self.client.get_stock_list()
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
