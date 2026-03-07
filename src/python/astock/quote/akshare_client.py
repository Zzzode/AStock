"""AkShare 行情客户端"""

import akshare as ak
import pandas as pd
from datetime import date
from typing import Optional
import asyncio
from functools import wraps


def async_wrap(func):
    """将同步函数包装为异步"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))
    return wrapper


class AkShareClient:
    """AkShare 行情数据客户端"""

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict:
        """获取实时行情

        Args:
            code: 股票代码，如 "000001"

        Returns:
            行情数据字典
        """
        # A股实时行情
        df = ak.stock_zh_a_spot_em()

        # 查找对应股票
        result = df[df["代码"] == code]
        if result.empty:
            raise ValueError(f"股票代码 {code} 不存在")

        row = result.iloc[0]
        return {
            "code": row["代码"],
            "name": row["名称"],
            "price": float(row["最新价"]) if row["最新价"] else 0.0,
            "change_percent": float(row["涨跌幅"]) if row["涨跌幅"] else 0.0,
            "change": float(row["涨跌额"]) if row["涨跌额"] else 0.0,
            "volume": float(row["成交量"]) if row["成交量"] else 0.0,
            "amount": float(row["成交额"]) if row["成交额"] else 0.0,
            "high": float(row["最高"]) if row["最高"] else 0.0,
            "low": float(row["最低"]) if row["最低"] else 0.0,
            "open": float(row["今开"]) if row["今开"] else 0.0,
            "prev_close": float(row["昨收"]) if row["昨收"] else 0.0,
        }

    @async_wrap
    def get_daily_quotes(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> pd.DataFrame:
        """获取日线行情

        Args:
            code: 股票代码
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            DataFrame，包含 OHLCV 数据
        """
        period = "daily"
        adjust = "qfq"  # 前复权

        df = ak.stock_zh_a_hist(
            symbol=code,
            period=period,
            adjust=adjust
        )

        # 日期过滤
        if start_date:
            df = df[df["日期"] >= start_date.strftime("%Y-%m-%d")]
        if end_date:
            df = df[df["日期"] <= end_date.strftime("%Y-%m-%d")]

        # 重命名列
        df = df.rename(columns={
            "日期": "date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
        })

        return df[["date", "open", "high", "low", "close", "volume", "amount"]]

    @async_wrap
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A股股票列表"""
        df = ak.stock_zh_a_spot_em()
        return df[["代码", "名称"]].rename(columns={
            "代码": "code",
            "名称": "name"
        })
