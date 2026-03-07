"""数据模型定义"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel


class Stock(BaseModel):
    """股票基础信息"""

    code: str
    name: str
    industry: Optional[str] = None
    list_date: Optional[date] = None


class DailyQuote(BaseModel):
    """日线行情"""

    code: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float


class IntradayQuote(BaseModel):
    """分时行情"""

    code: str
    datetime: datetime
    price: float
    volume: float
    amount: float


class Trade(BaseModel):
    """交易记录"""

    id: Optional[int] = None
    code: str
    direction: str  # buy/sell
    price: float
    quantity: float
    traded_at: datetime
    source: str  # broker/ths/eastmoney
