"""持仓模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class PositionSide(str, Enum):
    """持仓方向"""

    LONG = "long"
    SHORT = "short"


@dataclass
class Position:
    """持仓信息"""

    code: str  # 股票代码
    name: Optional[str] = None  # 股票名称
    shares: float = 0  # 持仓数量
    available_shares: float = 0  # 可用数量
    cost_price: float = 0.0  # 成本价
    current_price: float = 0.0  # 当前价
    side: PositionSide = PositionSide.LONG
    opened_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def market_value(self) -> float:
        """市值"""
        return self.shares * self.current_price

    @property
    def profit_loss(self) -> float:
        """浮动盈亏"""
        return (self.current_price - self.cost_price) * self.shares

    @property
    def profit_loss_percent(self) -> float:
        """盈亏比例"""
        if self.cost_price == 0:
            return 0
        return (self.current_price - self.cost_price) / self.cost_price * 100

    @property
    def is_empty(self) -> bool:
        """是否空仓"""
        return self.shares == 0

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "shares": self.shares,
            "available_shares": self.available_shares,
            "cost_price": self.cost_price,
            "current_price": self.current_price,
            "side": self.side.value,
            "market_value": self.market_value,
            "profit_loss": self.profit_loss,
            "profit_loss_percent": self.profit_loss_percent,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class PositionManager:
    """持仓管理器"""

    def __init__(self):
        self._positions: dict[str, Position] = {}

    def get_position(self, code: str) -> Optional[Position]:
        """获取持仓"""
        return self._positions.get(code)

    def get_all_positions(self) -> list[Position]:
        """获取所有持仓"""
        return list(self._positions.values())

    def add_position(
        self,
        code: str,
        shares: float,
        price: float,
        name: Optional[str] = None,
    ) -> Position:
        """添加持仓（买入）"""
        now = datetime.now()

        if code in self._positions:
            pos = self._positions[code]
            # 计算新的成本价
            total_cost = pos.cost_price * pos.shares + price * shares
            total_shares = pos.shares + shares
            pos.cost_price = total_cost / total_shares if total_shares > 0 else 0
            pos.shares = total_shares
            pos.available_shares += shares
            pos.current_price = price
            pos.updated_at = now
        else:
            pos = Position(
                code=code,
                name=name,
                shares=shares,
                available_shares=shares,
                cost_price=price,
                current_price=price,
                opened_at=now,
                updated_at=now,
            )
            self._positions[code] = pos

        return pos

    def reduce_position(
        self,
        code: str,
        shares: float,
        price: float,
    ) -> Optional[Position]:
        """减少持仓（卖出）"""
        if code not in self._positions:
            return None

        pos = self._positions[code]
        actual_shares = min(shares, pos.shares, pos.available_shares)
        pos.shares -= actual_shares
        pos.available_shares -= actual_shares
        pos.current_price = price
        pos.updated_at = datetime.now()

        if pos.shares <= 0:
            del self._positions[code]
            return None

        return pos

    def update_price(self, code: str, price: float) -> None:
        """更新持仓价格"""
        if code in self._positions:
            self._positions[code].current_price = price
            self._positions[code].updated_at = datetime.now()

    def update_prices(self, prices: dict[str, float]) -> None:
        """批量更新价格"""
        for code, price in prices.items():
            self.update_price(code, price)

    def get_total_value(self) -> float:
        """获取总市值"""
        return sum(p.market_value for p in self._positions.values())

    def get_total_profit_loss(self) -> float:
        """获取总盈亏"""
        return sum(p.profit_loss for p in self._positions.values())

    def clear(self) -> None:
        """清空所有持仓"""
        self._positions.clear()
