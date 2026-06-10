"""Portfolio management"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .position import Position, PositionManager


@dataclass
class PortfolioStats:
    """Portfolio statistics"""

    total_value: float = 0.0  # Total assets
    cash: float = 0.0  # Cash
    market_value: float = 0.0  # Market value
    profit_loss: float = 0.0  # Total profit/loss
    profit_loss_percent: float = 0.0  # Return rate
    position_count: int = 0  # Number of positions
    max_position_ratio: float = 0.0  # Largest position ratio
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, object]:
        return {
            "total_value": self.total_value,
            "cash": self.cash,
            "market_value": self.market_value,
            "profit_loss": self.profit_loss,
            "profit_loss_percent": self.profit_loss_percent,
            "position_count": self.position_count,
            "max_position_ratio": self.max_position_ratio,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class Portfolio:
    """Investment portfolio"""

    name: str = "default"
    initial_capital: float = 100000.0
    cash: float = 100000.0
    position_manager: PositionManager = field(default_factory=PositionManager)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def market_value(self) -> float:
        """Market value"""
        return self.position_manager.get_total_value()

    @property
    def total_value(self) -> float:
        """Total assets"""
        return self.cash + self.market_value

    @property
    def profit_loss(self) -> float:
        """Total profit/loss"""
        return self.total_value - self.initial_capital

    @property
    def profit_loss_percent(self) -> float:
        """Return rate"""
        if self.initial_capital == 0:
            return 0
        return (self.total_value - self.initial_capital) / self.initial_capital * 100

    @property
    def position_count(self) -> int:
        """Number of positions"""
        return len(
            [p for p in self.position_manager.get_all_positions() if not p.is_empty]
        )

    def get_stats(self) -> PortfolioStats:
        """Get portfolio statistics"""
        positions = self.position_manager.get_all_positions()
        max_position_value = 0.0
        total_value = self.total_value

        for pos in positions:
            if pos.market_value > max_position_value:
                max_position_value = pos.market_value

        max_position_ratio = max_position_value / total_value if total_value > 0 else 0

        return PortfolioStats(
            total_value=self.total_value,
            cash=self.cash,
            market_value=self.market_value,
            profit_loss=self.profit_loss,
            profit_loss_percent=self.profit_loss_percent,
            position_count=self.position_count,
            max_position_ratio=max_position_ratio,
            updated_at=datetime.now(),
        )


class PortfolioManager:
    """Portfolio manager"""

    def __init__(self) -> None:
        self._portfolios: dict[str, Portfolio] = {}

    def create_portfolio(
        self,
        name: str = "default",
        initial_capital: float = 100000.0,
    ) -> Portfolio:
        """Create portfolio"""
        portfolio = Portfolio(
            name=name,
            initial_capital=initial_capital,
            cash=initial_capital,
        )
        self._portfolios[name] = portfolio
        return portfolio

    def get_portfolio(self, name: str = "default") -> Optional[Portfolio]:
        """Get portfolio"""
        return self._portfolios.get(name)

    def get_or_create(
        self, name: str = "default", initial_capital: float = 100000.0
    ) -> Portfolio:
        """Get or create portfolio"""
        if name not in self._portfolios:
            return self.create_portfolio(name, initial_capital)
        return self._portfolios[name]

    def buy(
        self,
        portfolio_name: str,
        code: str,
        shares: float,
        price: float,
        name: Optional[str] = None,
    ) -> Optional[Position]:
        """Buy"""
        portfolio = self.get_portfolio(portfolio_name)
        if not portfolio:
            return None

        # Calculate required funds
        required = shares * price
        if required > portfolio.cash:
            # Insufficient funds, adjust by available funds
            shares = int(portfolio.cash / price / 100) * 100  # A-share lot size: 100 shares
            if shares <= 0:
                return None
            required = shares * price

        # Deduct funds
        portfolio.cash -= required

        # Add position
        return portfolio.position_manager.add_position(code, shares, price, name)

    def sell(
        self,
        portfolio_name: str,
        code: str,
        shares: float,
        price: float,
    ) -> Optional[Position]:
        """Sell"""
        portfolio = self.get_portfolio(portfolio_name)
        if not portfolio:
            return None

        # Reduce position
        pos = portfolio.position_manager.reduce_position(code, shares, price)
        if pos is None:
            # Fully sold, return funds
            portfolio.cash += shares * price
        else:
            # Partially sold, return funds
            portfolio.cash += shares * price

        return pos

    def update_prices(self, portfolio_name: str, prices: dict[str, float]) -> None:
        """Update prices"""
        portfolio = self.get_portfolio(portfolio_name)
        if portfolio:
            portfolio.position_manager.update_prices(prices)

    def get_all_portfolios(self) -> list[Portfolio]:
        """Get all portfolios"""
        return list(self._portfolios.values())
