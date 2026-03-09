"""AkShare 行情客户端"""

import akshare as ak
import pandas as pd
from datetime import date
from typing import Optional, Any, Callable, Awaitable, TypeVar, ParamSpec, cast
import asyncio
from functools import wraps
import os


P = ParamSpec("P")
T = TypeVar("T")


def async_wrap(func: Callable[P, T]) -> Callable[P, Awaitable[T]]:
    """将同步函数包装为异步"""
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_event_loop()
        return cast(T, await loop.run_in_executor(None, lambda: func(*args, **kwargs)))
    return wrapper


class AkShareClient:
    """AkShare 行情数据客户端"""

    def _load_realtime_dataframe(self) -> pd.DataFrame:
        try:
            return ak.stock_zh_a_spot_em()
        except Exception:
            return ak.stock_zh_a_spot()

    def _normalize_code(self, value: object) -> str:
        text = str(value)
        digits = "".join(ch for ch in text if ch.isdigit())
        if len(digits) >= 6:
            return digits[-6:]
        return digits

    def _daily_symbol(self, code: str) -> str:
        if code.startswith("6"):
            return f"sh{code}"
        if code.startswith(("8", "4")):
            return f"bj{code}"
        return f"sz{code}"

    def _normalize_daily_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        column_map = {}
        if "日期" in df.columns:
            column_map["日期"] = "date"
        if "开盘" in df.columns:
            column_map["开盘"] = "open"
        if "最高" in df.columns:
            column_map["最高"] = "high"
        if "最低" in df.columns:
            column_map["最低"] = "low"
        if "收盘" in df.columns:
            column_map["收盘"] = "close"
        if "成交量" in df.columns:
            column_map["成交量"] = "volume"
        if "成交额" in df.columns:
            column_map["成交额"] = "amount"

        if column_map:
            df = df.rename(columns=column_map)

        required = ["date", "open", "high", "low", "close", "volume", "amount"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"日线数据缺少列: {missing}")
        return df[required]

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict[str, Any]:
        """获取实时行情

        Args:
            code: 股票代码，如 "000001"

        Returns:
            行情数据字典
        """
        if os.getenv("ASTOCK_OFFLINE") == "1":
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
        df = self._load_realtime_dataframe()
        if "代码" not in df.columns:
            raise ValueError("实时行情数据缺少 代码 列")

        normalized_codes = df["代码"].apply(self._normalize_code)
        result = df[normalized_codes == code]

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
        try:
            df = ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                adjust="qfq"
            )
        except Exception:
            symbol = self._daily_symbol(code)
            kwargs = {"symbol": symbol, "adjust": "qfq"}
            if start_date:
                kwargs["start_date"] = start_date.strftime("%Y%m%d")
            if end_date:
                kwargs["end_date"] = end_date.strftime("%Y%m%d")
            df = ak.stock_zh_a_daily(**kwargs)

        if start_date and "date" in df.columns:
            df = df[df["date"] >= start_date.strftime("%Y-%m-%d")]
        if end_date and "date" in df.columns:
            df = df[df["date"] <= end_date.strftime("%Y-%m-%d")]
        if start_date and "日期" in df.columns:
            df = df[df["日期"] >= start_date.strftime("%Y-%m-%d")]
        if end_date and "日期" in df.columns:
            df = df[df["日期"] <= end_date.strftime("%Y-%m-%d")]

        return self._normalize_daily_dataframe(df)

    @async_wrap
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A股股票列表"""
        df = ak.stock_zh_a_spot_em()
        return df[["代码", "名称"]].rename(columns={
            "代码": "code",
            "名称": "name"
        })
