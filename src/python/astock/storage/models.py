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


class WatchItem(BaseModel):
    """监控项"""

    code: str
    name: Optional[str] = None
    conditions: dict = {}  # 监控条件配置
    alert_channels: list[str] = ["terminal"]  # 提醒渠道
    enabled: bool = True
    created_at: Optional[datetime] = None


class AlertRecord(BaseModel):
    """告警记录"""

    id: Optional[int] = None
    code: str
    signal_type: str
    signal_name: str
    message: str
    level: int = 3  # 1=紧急, 2=重要, 3=一般
    triggered_at: datetime
    status: str = "pending"  # pending, sent, failed
    channels: list[str] = []
