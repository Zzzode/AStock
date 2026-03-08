"""风险管理"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum
import math


class RiskLevel(str, Enum):
    """风险等级"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskMetrics:
    """风险指标"""

    max_drawdown: float = 0.0  # 最大回撤
    volatility: float = 0.0  # 波动率
    sharpe_ratio: float = 0.0  # 夏普比率
    var_95: float = 0.0  # 95% VaR
    concentration_risk: float = 0.0  # 集中度风险
    risk_level: RiskLevel = RiskLevel.MEDIUM
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "max_drawdown": self.max_drawdown,
            "volatility": self.volatility,
            "sharpe_ratio": self.sharpe_ratio,
            "var_95": self.var_95,
            "concentration_risk": self.concentration_risk,
            "risk_level": self.risk_level.value,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class RiskLimits:
    """风控限制"""

    max_position_size: float = 0.2  # 单只股票最大仓位
    max_sector_exposure: float = 0.4  # 单行业最大敞口
    max_drawdown_limit: float = 0.2  # 最大回撤限制
    max_positions: int = 10  # 最大持仓数量
    stop_loss_percent: float = 0.08  # 止损比例
    take_profit_percent: float = 0.15  # 止盈比例


class RiskManager:
    """风险管理器"""

    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self._equity_history: list[dict] = []

    def check_position_limit(
        self,
        current_value: float,
        position_value: float,
        new_position_value: float,
    ) -> tuple[bool, str]:
        """检查仓位限制

        Returns:
            (是否通过, 原因)
        """
        total_value = current_value + new_position_value
        if total_value == 0:
            return True, ""

        position_ratio = (position_value + new_position_value) / total_value

        if position_ratio > self.limits.max_position_size:
            return False, f"单只股票仓位超过限制 {self.limits.max_position_size:.0%}"

        return True, ""

    def check_drawdown(
        self, peak_value: float, current_value: float
    ) -> tuple[bool, float]:
        """检查回撤

        Returns:
            (是否超过限制, 当前回撤)
        """
        if peak_value == 0:
            return False, 0

        drawdown = (peak_value - current_value) / peak_value

        if drawdown > self.limits.max_drawdown_limit:
            return True, drawdown

        return False, drawdown

    def check_stop_loss(
        self,
        cost_price: float,
        current_price: float,
    ) -> tuple[bool, float]:
        """检查止损

        Returns:
            (是否触发止损, 亏损比例)
        """
        if cost_price == 0:
            return False, 0

        loss_percent = (cost_price - current_price) / cost_price

        if loss_percent >= self.limits.stop_loss_percent:
            return True, loss_percent

        return False, loss_percent

    def check_take_profit(
        self,
        cost_price: float,
        current_price: float,
    ) -> tuple[bool, float]:
        """检查止盈

        Returns:
            (是否触发止盈, 盈利比例)
        """
        if cost_price == 0:
            return False, 0

        profit_percent = (current_price - cost_price) / cost_price

        if profit_percent >= self.limits.take_profit_percent:
            return True, profit_percent

        return False, profit_percent

    def calculate_var(
        self,
        returns: list[float],
        confidence: float = 0.95,
    ) -> float:
        """计算 VaR (Value at Risk)

        Args:
            returns: 收益率序列
            confidence: 置信度

        Returns:
            VaR 值
        """
        if not returns:
            return 0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index])

    def calculate_max_drawdown(self, equity_curve: list[float]) -> float:
        """计算最大回撤"""
        if not equity_curve:
            return 0

        peak = equity_curve[0]
        max_dd = 0

        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def calculate_sharpe_ratio(
        self,
        returns: list[float],
        risk_free_rate: float = 0.03,
    ) -> float:
        """计算夏普比率"""
        if not returns or len(returns) < 2:
            return 0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std = math.sqrt(variance)

        if std == 0:
            return 0

        # 年化
        annual_return = mean_return * 252
        annual_std = std * math.sqrt(252)

        return (annual_return - risk_free_rate) / annual_std

    def assess_risk(
        self,
        positions: list[dict],
        equity_curve: list[float],
        returns: list[float],
    ) -> RiskMetrics:
        """评估风险

        Args:
            positions: 持仓列表
            equity_curve: 权益曲线
            returns: 收益率序列

        Returns:
            风险指标
        """
        # 计算最大回撤
        max_drawdown = self.calculate_max_drawdown(equity_curve)

        # 计算波动率
        volatility = 0
        if returns and len(returns) > 1:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = math.sqrt(variance) * math.sqrt(252)

        # 计算夏普比率
        sharpe_ratio = self.calculate_sharpe_ratio(returns)

        # 计算 VaR
        var_95 = self.calculate_var(returns, 0.95)

        # 计算集中度风险
        total_value = sum(p.get("market_value", 0) for p in positions)
        max_position = max((p.get("market_value", 0) for p in positions), default=0)
        concentration_risk = max_position / total_value if total_value > 0 else 0

        # 确定风险等级
        risk_level = RiskLevel.LOW
        if max_drawdown > 0.2 or volatility > 0.3:
            risk_level = RiskLevel.CRITICAL
        elif max_drawdown > 0.15 or volatility > 0.25:
            risk_level = RiskLevel.HIGH
        elif max_drawdown > 0.1 or volatility > 0.2:
            risk_level = RiskLevel.MEDIUM

        return RiskMetrics(
            max_drawdown=max_drawdown,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            var_95=var_95,
            concentration_risk=concentration_risk,
            risk_level=risk_level,
            updated_at=datetime.now(),
        )

    def suggest_position_size(
        self,
        total_capital: float,
        stock_volatility: float,
        target_risk: float = 0.02,
    ) -> float:
        """建议仓位大小

        Args:
            total_capital: 总资金
            stock_volatility: 股票波动率
            target_risk: 目标风险（每日）

        Returns:
            建议仓位金额
        """
        if stock_volatility == 0:
            return total_capital * self.limits.max_position_size

        # 简化的凯利公式
        position_ratio = min(
            target_risk / stock_volatility, self.limits.max_position_size
        )
        return total_capital * position_ratio
