"""组合管理"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from .position import Position, PositionManager


@dataclass
class PortfolioStats:
    """组合统计"""

    total_value: float = 0.0  # 总资产
    cash: float = 0.0  # 现金
    market_value: float = 0.0  # 市值
    profit_loss: float = 0.0  # 总盈亏
    profit_loss_percent: float = 0.0  # 收益率
    position_count: int = 0  # 持仓数量
    max_position_ratio: float = 0.0  # 最大仓位比例
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
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
    """投资组合"""

    name: str = "default"
    initial_capital: float = 100000.0
    cash: float = 100000.0
    position_manager: PositionManager = field(default_factory=PositionManager)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def market_value(self) -> float:
        """市值"""
        return self.position_manager.get_total_value()

    @property
    def total_value(self) -> float:
        """总资产"""
        return self.cash + self.market_value

    @property
    def profit_loss(self) -> float:
        """总盈亏"""
        return self.total_value - self.initial_capital

    @property
    def profit_loss_percent(self) -> float:
        """收益率"""
        if self.initial_capital == 0:
            return 0
        return (self.total_value - self.initial_capital) / self.initial_capital * 100

    @property
    def position_count(self) -> int:
        """持仓数量"""
        return len(
            [p for p in self.position_manager.get_all_positions() if not p.is_empty]
        )

    def get_stats(self) -> PortfolioStats:
        """获取组合统计"""
        positions = self.position_manager.get_all_positions()
        max_position_value = 0
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
    """组合管理器"""

    def __init__(self):
        self._portfolios: dict[str, Portfolio] = {}

    def create_portfolio(
        self,
        name: str = "default",
        initial_capital: float = 100000.0,
    ) -> Portfolio:
        """创建组合"""
        portfolio = Portfolio(
            name=name,
            initial_capital=initial_capital,
            cash=initial_capital,
        )
        self._portfolios[name] = portfolio
        return portfolio

    def get_portfolio(self, name: str = "default") -> Optional[Portfolio]:
        """获取组合"""
        return self._portfolios.get(name)

    def get_or_create(
        self, name: str = "default", initial_capital: float = 100000.0
    ) -> Portfolio:
        """获取或创建组合"""
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
        """买入"""
        portfolio = self.get_portfolio(portfolio_name)
        if not portfolio:
            return None

        # 计算所需资金
        required = shares * price
        if required > portfolio.cash:
            # 资金不足，按可用资金调整
            shares = int(portfolio.cash / price / 100) * 100  # A股一手100股
            if shares <= 0:
                return None
            required = shares * price

        # 扣除资金
        portfolio.cash -= required

        # 添加持仓
        return portfolio.position_manager.add_position(code, shares, price, name)

    def sell(
        self,
        portfolio_name: str,
        code: str,
        shares: float,
        price: float,
    ) -> Optional[Position]:
        """卖出"""
        portfolio = self.get_portfolio(portfolio_name)
        if not portfolio:
            return None

        # 减少持仓
        pos = portfolio.position_manager.reduce_position(code, shares, price)
        if pos is None:
            # 完全卖出，返还资金
            portfolio.cash += shares * price
        else:
            # 部分卖出，返还资金
            portfolio.cash += shares * price

        return pos

    def update_prices(self, portfolio_name: str, prices: dict[str, float]) -> None:
        """更新价格"""
        portfolio = self.get_portfolio(portfolio_name)
        if portfolio:
            portfolio.position_manager.update_prices(prices)

    def get_all_portfolios(self) -> list[Portfolio]:
        """获取所有组合"""
        return list(self._portfolios.values())
