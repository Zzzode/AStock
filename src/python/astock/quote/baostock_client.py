"""Baostock 行情客户端 - 稳定可靠的 A 股数据源

Baostock 特点：
- 证券宝官方维护，数据稳定可靠
- 支持日线、周线、月线
- 支持 PE、PB 等估值数据
- T+1 更新（当日数据次日可见）
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from functools import partial
from typing import Any, Callable, Optional, TypeVar, ParamSpec

import baostock as bs
import pandas as pd

from ..utils import get_logger
from ..utils.exceptions import DataSourceError

logger = get_logger("baostock_client")

P = ParamSpec("P")
T = TypeVar("T")

# 专用线程池
_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    """获取专用线程池"""
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="baostock_")
    return _executor


def async_wrap(func: Callable[P, T]) -> Callable[P, "asyncio.Future[T]"]:
    """将同步函数包装为异步"""

    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        loop = asyncio.get_running_loop()
        func_partial = partial(func, *args, **kwargs)
        return await loop.run_in_executor(_get_executor(), func_partial)

    return wrapper


class BaostockClient:
    """Baostock 行情数据客户端

    优势：
    - 数据稳定可靠，证券宝官方维护
    - 支持 PE、PB、市值等估值数据
    - API 简单稳定

    限制：
    - 当日数据 T+1 更新
    - 无实时行情（需要结合其他数据源）
    """

    def __init__(self):
        self._logged_in = False
        self._login_lock = asyncio.Lock()

    def _ensure_login(self) -> None:
        """确保已登录（同步版本）"""
        if self._logged_in:
            return

        try:
            lg = bs.login()
            if lg.error_code != "0":
                raise DataSourceError(
                    f"Baostock 登录失败: {lg.error_msg}",
                    source="baostock",
                )
            self._logged_in = True
            logger.info("Baostock 登录成功")
        except Exception as e:
            raise DataSourceError(
                f"Baostock 登录异常: {e}",
                source="baostock",
            ) from e

    async def ensure_login(self) -> None:
        """确保已登录（异步版本）"""
        async with self._login_lock:
            if not self._logged_in:
                await async_wrap(self._ensure_login)()

    def _baostock_code(self, code: str) -> str:
        """转换为 baostock 格式的股票代码

        Args:
            code: 6位股票代码，如 "600036"

        Returns:
            baostock 格式代码，如 "sh.600036"
        """
        code = code.zfill(6)
        if code.startswith("6"):
            return f"sh.{code}"
        else:
            return f"sz.{code}"

    def _normalize_code(self, bs_code: str) -> str:
        """从 baostock 代码提取纯代码

        Args:
            bs_code: baostock 格式代码，如 "sh.600036"

        Returns:
            6位代码，如 "600036"
        """
        return bs_code.split(".")[-1]

    @async_wrap
    def get_stock_list(self) -> pd.DataFrame:
        """获取 A 股股票列表

        Returns:
            DataFrame with columns: code, name
        """
        self._ensure_login()

        try:
            # 尝试最近几个交易日的数据
            today = date.today()
            data_list = []

            for i in range(7):  # 尝试最近7天
                query_date = today - timedelta(days=i)
                rs = bs.query_all_stock(day=query_date.strftime("%Y-%m-%d"))

                if rs.error_code != "0":
                    continue

                while rs.error_code == "0" and rs.next():
                    data_list.append(rs.get_row_data())

                if data_list:
                    logger.debug(f"使用 {query_date} 的股票列表数据")
                    break

            if not data_list:
                raise DataSourceError(
                    "获取股票列表失败: 最近7天无数据",
                    source="baostock",
                )

            # fields: code, tradeStatus, code_name
            df = pd.DataFrame(data_list, columns=["bs_code", "trade_status", "name"])

            # 过滤主板、创业板、科创板（排除指数）
            # sh.6xxxxx 沪市主板, sz.0xxxxx 深市主板, sz.3xxxxx 创业板
            df = df[df["bs_code"].str.match(r"^(sh\.6\d{5}|sz\.0\d{5}|sz\.3\d{5})$")]

            # 标准化代码
            df["code"] = df["bs_code"].str.replace(r"^(sh|sz)\.", "", regex=True)

            logger.info(f"获取股票列表成功: {len(df)} 只")
            return df[["code", "name"]]

        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(
                f"获取股票列表异常: {e}",
                source="baostock",
            ) from e

    @async_wrap
    def get_daily_quotes(
        self,
        code: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: int = 120,  # 默认获取120天数据，减少网络传输
    ) -> pd.DataFrame:
        """获取日线行情（含估值数据）

        Args:
            code: 股票代码，如 "600036"
            start_date: 开始日期
            end_date: 结束日期
            days: 如果未指定 start_date，默认获取的天数

        Returns:
            DataFrame with columns: date, open, high, low, close, volume, amount, pe, pb
        """
        self._ensure_login()

        # 默认日期范围
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=days)

        bs_code = self._baostock_code(code)

        try:
            # 查询日线数据，包含估值指标
            rs = bs.query_history_k_data_plus(
                bs_code,
                "date,code,open,high,low,close,volume,amount,turn,peTTM,pbMRQ,psTTM,pcfNcfTTM",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                frequency="d",
                adjustflag="2",  # 前复权
            )

            if rs.error_code != "0":
                raise DataSourceError(
                    f"获取日线数据失败: {rs.error_msg}",
                    source="baostock",
                    code=code,
                )

            data_list = []
            while rs.error_code == "0" and rs.next():
                data_list.append(rs.get_row_data())

            if not data_list:
                logger.warning(f"股票 {code} 无数据")
                return pd.DataFrame()

            df = pd.DataFrame(data_list, columns=rs.fields)

            # 类型转换
            df["date"] = pd.to_datetime(df["date"])
            for col in ["open", "high", "low", "close", "volume", "amount"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # 估值数据
            df["pe"] = pd.to_numeric(df.get("peTTM"), errors="coerce")
            df["pb"] = pd.to_numeric(df.get("pbMRQ"), errors="coerce")
            df["ps"] = pd.to_numeric(df.get("psTTM"), errors="coerce")
            df["pcf"] = pd.to_numeric(df.get("pcfNcfTTM"), errors="coerce")

            # 成交额（单位：千元 -> 元）
            if "amount" in df.columns:
                df["amount"] = df["amount"] * 1000

            logger.debug(f"获取 {code} 日线数据: {len(df)} 条")
            return df[["date", "open", "high", "low", "close", "volume", "amount", "pe", "pb", "ps", "pcf"]]

        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(
                f"获取日线数据异常: {e}",
                source="baostock",
                code=code,
            ) from e

    @async_wrap
    def get_realtime_quote(self, code: str) -> dict[str, Any]:
        """获取"实时"行情（实际上是最近交易日的数据）

        Baostock 不支持实时行情，返回最近交易日的日线数据

        Args:
            code: 股票代码

        Returns:
            行情数据字典
        """
        self._ensure_login()

        try:
            # 获取最近 5 个交易日的数据
            end_date = date.today()
            start_date = end_date - timedelta(days=10)

            df = self.get_daily_quotes.__wrapped__(self, code, start_date, end_date)

            if df.empty:
                raise DataSourceError(
                    f"股票 {code} 无数据",
                    source="baostock",
                    code=code,
                )

            # 取最新一条
            latest = df.iloc[-1]

            # 计算涨跌幅
            prev_close = df.iloc[-2]["close"] if len(df) > 1 else latest["close"]
            change = latest["close"] - prev_close
            change_percent = (change / prev_close * 100) if prev_close > 0 else 0

            return {
                "code": code,
                "name": "",  # Baostock 日线数据不含名称
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
                "is_realtime": False,  # 标记非实时数据
            }

        except DataSourceError:
            raise
        except Exception as e:
            raise DataSourceError(
                f"获取行情数据异常: {e}",
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
        """批量获取多只股票的日线数据

        Args:
            codes: 股票代码列表
            start_date: 开始日期
            end_date: 结束日期

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
                logger.warning(f"获取 {code} 数据失败: {e}")
                continue

        if not all_data:
            return pd.DataFrame()

        result = pd.concat(all_data, ignore_index=True)
        logger.info(f"批量获取日线数据: {len(codes)} 只股票, {len(result)} 条记录")
        return result

    def logout(self) -> None:
        """登出"""
        if self._logged_in:
            bs.logout()
            self._logged_in = False
            logger.info("Baostock 已登出")