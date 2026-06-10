"""Data model definitions"""

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class Stock(BaseModel):
    """Stock basic information"""

    code: str
    name: str
    industry: Optional[str] = None
    list_date: Optional[date] = None


class DailyQuote(BaseModel):
    """Daily quote"""

    code: str
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: float
    amount: float


class IntradayQuote(BaseModel):
    """Intraday quote"""

    code: str
    datetime: datetime
    price: float
    volume: float
    amount: float


class Trade(BaseModel):
    """Trade record"""

    id: Optional[int] = None
    code: str
    direction: str  # buy/sell
    price: float
    quantity: float
    traded_at: datetime
    source: str  # broker/ths/eastmoney


class WatchItem(BaseModel):
    """Watch item"""

    code: str
    name: Optional[str] = None
    conditions: dict[str, object] = Field(default_factory=dict)
    alert_channels: list[str] = Field(default_factory=lambda: ["terminal"])
    enabled: bool = True
    created_at: Optional[datetime] = None


class AlertRecord(BaseModel):
    """Alert record"""

    id: Optional[int] = None
    code: str
    signal_type: str
    signal_name: str
    message: str
    level: int = 3  # 1=urgent, 2=important, 3=normal
    triggered_at: datetime
    status: str = "pending"  # pending, sent, failed
    channels: list[str] = Field(default_factory=list)
