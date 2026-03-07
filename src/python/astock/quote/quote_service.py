"""行情服务"""

from datetime import date, datetime
from typing import Optional
import pandas as pd

from .akshare_client import AkShareClient
from ..storage import Database, DailyQuote


class QuoteService:
    """行情服务"""

    def __init__(self, db: Database):
        self.client = AkShareClient()
        self.db = db

    async def get_realtime(self, code: str) -> dict:
        """获取实时行情

        Args:
            code: 股票代码

        Returns:
            实时行情数据
        """
        return await self.client.get_realtime_quote(code)

    async def get_daily(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        save: bool = True
    ) -> pd.DataFrame:
        """获取日线数据

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            save: 是否保存到数据库

        Returns:
            日线 DataFrame
        """
        df = await self.client.get_daily_quotes(code, start_date, end_date)

        if save and not df.empty:
            quotes = [
                DailyQuote(
                    code=code,
                    date=row["date"] if isinstance(row["date"], date)
                        else datetime.strptime(row["date"], "%Y-%m-%d").date(),
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                    amount=float(row["amount"])
                )
                for _, row in df.iterrows()
            ]
            await self.db.save_daily_quotes(quotes)

        return df

    async def refresh_stocks(self) -> int:
        """刷新股票列表

        Returns:
            更新的股票数量
        """
        from ..storage import Stock

        df = await self.client.get_stock_list()
        count = 0

        for _, row in df.iterrows():
            stock = Stock(code=row["code"], name=row["name"])
            await self.db.save_stock(stock)
            count += 1

        return count
