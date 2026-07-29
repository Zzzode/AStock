"""Position model"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class PositionSide(str, Enum):
    """Position side"""

    LONG = "long"
    SHORT = "short"


@dataclass
class Position:
    """Position information"""

    code: str  # Stock code
    name: Optional[str] = None  # Stock name
    shares: float = 0  # Position quantity
    available_shares: float = 0  # Available quantity
    cost_price: float = 0.0  # Cost price
    current_price: float = 0.0  # Current price
    side: PositionSide = PositionSide.LONG
    opened_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def market_value(self) -> float:
        """Market value"""
        return self.shares * self.current_price

    @property
    def profit_loss(self) -> float:
        """Unrealized profit/loss"""
        return (self.current_price - self.cost_price) * self.shares

    @property
    def profit_loss_percent(self) -> float:
        """Profit/loss percentage"""
        if self.cost_price == 0:
            return 0
        return (self.current_price - self.cost_price) / self.cost_price * 100

    @property
    def is_empty(self) -> bool:
        """Whether position is empty"""
        return self.shares == 0

    def to_dict(self) -> dict[str, object]:
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
    """Position manager"""

    def __init__(self) -> None:
        self._positions: dict[str, Position] = {}

    def get_position(self, code: str) -> Optional[Position]:
        """Get position"""
        return self._positions.get(code)

    def get_all_positions(self) -> list[Position]:
        """Get all positions"""
        return list(self._positions.values())

    def add_position(
        self,
        code: str,
        shares: float,
        price: float,
        name: Optional[str] = None,
    ) -> Position:
        """Add position (buy)"""
        now = datetime.now()

        if code in self._positions:
            pos = self._positions[code]
            # Calculate new cost price
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
        """Reduce position (sell)"""
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
        """Update position price"""
        if code in self._positions:
            self._positions[code].current_price = price
            self._positions[code].updated_at = datetime.now()

    def update_prices(self, prices: dict[str, float]) -> None:
        """Batch update prices"""
        for code, price in prices.items():
            self.update_price(code, price)

    def get_total_value(self) -> float:
        """Get total market value"""
        return sum(p.market_value for p in self._positions.values())

    def get_total_profit_loss(self) -> float:
        """Get total profit/loss"""
        return sum(p.profit_loss for p in self._positions.values())

    def clear(self) -> None:
        """Clear all positions"""
        self._positions.clear()
