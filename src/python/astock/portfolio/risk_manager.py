"""Risk management"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from enum import Enum
import math


class RiskLevel(str, Enum):
    """Risk level"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RiskMetrics:
    """Risk metrics"""

    max_drawdown: float = 0.0  # Max drawdown
    volatility: float = 0.0  # Volatility
    sharpe_ratio: float = 0.0  # Sharpe ratio
    var_95: float = 0.0  # 95% VaR
    concentration_risk: float = 0.0  # Concentration risk
    risk_level: RiskLevel = RiskLevel.MEDIUM
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict[str, object]:
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
    """Risk control limits"""

    max_position_size: float = 0.2  # Max single stock position size
    max_sector_exposure: float = 0.4  # Max single sector exposure
    max_theme_exposure: float = 0.4  # Max single theme exposure
    max_drawdown_limit: float = 0.2  # Max drawdown limit
    max_positions: int = 10  # Max number of positions
    stop_loss_percent: float = 0.08  # Stop-loss ratio
    take_profit_percent: float = 0.15  # Take-profit ratio
    min_cash_ratio: float = 0.10  # Minimum cash reserve under normal conditions
    max_portfolio_risk: float = 0.03  # Sum of planned stop losses / account value
    max_portfolio_stress_loss: float = 0.06  # Sum of worst stated gap/limit stress losses / account value
    max_daily_new_risk: float = 0.01  # Maximum incremental planned loss / account value
    max_factor_exposure: float = 0.60  # Maximum aggregate exposure to any supplied factor
    max_pairwise_correlation: float = 0.80  # Pairwise correlation review threshold
    max_liquidity_participation: float = 0.10  # Maximum planned exit / average daily turnover
    max_structural_stress_loss: float = 0.10  # Maximum supplied factor-scenario loss / account value
    max_horizon_exposure: dict[str, float] = field(
        default_factory=lambda: {
            "short_term": 0.20,
            "swing": 0.30,
            "long_term": 0.50,
        }
    )


@dataclass(frozen=True)
class RiskBudgetReport:
    """Auditable portfolio risk-budget report for paper-trading decisions.

    `planned_loss` is the sum of each position's market value times its explicit
    stop distance (or a conservative fallback).  It is not VaR and must not be
    presented as a probabilistic loss estimate.
    """

    total_value: float
    cash_ratio: float
    planned_loss: float
    planned_loss_ratio: float
    stressed_loss: float
    stressed_loss_ratio: float
    sector_exposure: dict[str, float]
    theme_exposure: dict[str, float]
    horizon_exposure: dict[str, float]
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_value": self.total_value,
            "cash_ratio": self.cash_ratio,
            "planned_loss": self.planned_loss,
            "planned_loss_ratio": self.planned_loss_ratio,
            "stressed_loss": self.stressed_loss,
            "stressed_loss_ratio": self.stressed_loss_ratio,
            "sector_exposure": self.sector_exposure,
            "theme_exposure": self.theme_exposure,
            "horizon_exposure": self.horizon_exposure,
            "blockers": self.blockers,
            "warnings": self.warnings,
        }


@dataclass(frozen=True)
class PortfolioStructureRiskReport:
    """Factor, correlation, liquidity, and scenario-risk controls.

    All inputs are caller-supplied, source-labelled desk inputs. Missing factor,
    correlation, liquidity, or scenario data is a blocker rather than a zero.
    """

    total_value: float
    factor_exposure: dict[str, float]
    correlated_pairs: list[dict[str, Any]]
    liquidity: list[dict[str, Any]]
    scenario_losses: dict[str, float]
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "total_value": self.total_value,
            "factor_exposure": self.factor_exposure,
            "correlated_pairs": self.correlated_pairs,
            "liquidity": self.liquidity,
            "scenario_losses": self.scenario_losses,
            "blockers": self.blockers,
            "warnings": self.warnings,
        }


class RiskManager:
    """Risk manager"""

    def __init__(self, limits: Optional[RiskLimits] = None):
        self.limits = limits or RiskLimits()
        self._equity_history: list[dict[str, float]] = []

    def check_position_limit(
        self,
        current_value: float,
        position_value: float,
        new_position_value: float,
    ) -> tuple[bool, str]:
        """Check position limit

        Returns:
            (passed, reason)
        """
        if current_value <= 0:
            return True, ""

        # A paper buy reallocates existing cash; it does not create new account
        # equity.  `current_value` is therefore the account value before the
        # trade, not a value to which the order should be added again.
        position_ratio = (position_value + new_position_value) / current_value

        if position_ratio > self.limits.max_position_size:
            return False, f"Single stock position exceeds limit {self.limits.max_position_size:.0%}"

        return True, ""

    def check_drawdown(
        self, peak_value: float, current_value: float
    ) -> tuple[bool, float]:
        """Check drawdown

        Returns:
            (exceeded_limit, current_drawdown)
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
        """Check stop-loss

        Returns:
            (triggered, loss_percent)
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
        """Check take-profit

        Returns:
            (triggered, profit_percent)
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
        """Calculate VaR (Value at Risk)

        Args:
            returns: Return series
            confidence: Confidence level

        Returns:
            VaR value
        """
        if not returns:
            return 0

        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        return abs(sorted_returns[index])

    def calculate_max_drawdown(self, equity_curve: list[float]) -> float:
        """Calculate max drawdown"""
        if not equity_curve:
            return 0

        peak = equity_curve[0]
        max_dd = 0.0

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
        """Calculate Sharpe ratio"""
        if not returns or len(returns) < 2:
            return 0

        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std = math.sqrt(variance)

        if std == 0:
            return 0

        # Annualize
        annual_return = mean_return * 252
        annual_std = std * math.sqrt(252)

        return (annual_return - risk_free_rate) / annual_std

    def assess_risk(
        self,
        positions: list[dict[str, float]],
        equity_curve: list[float],
        returns: list[float],
    ) -> RiskMetrics:
        """Assess risk

        Args:
            positions: Position list
            equity_curve: Equity curve
            returns: Return series

        Returns:
            Risk metrics
        """
        # Calculate max drawdown
        max_drawdown = self.calculate_max_drawdown(equity_curve)

        # Calculate volatility
        volatility = 0.0
        if returns and len(returns) > 1:
            mean_return = sum(returns) / len(returns)
            variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
            volatility = math.sqrt(variance) * math.sqrt(252)

        # Calculate Sharpe ratio
        sharpe_ratio = self.calculate_sharpe_ratio(returns)

        # Calculate VaR
        var_95 = self.calculate_var(returns, 0.95)

        # Calculate concentration risk
        total_value = sum(p.get("market_value", 0.0) for p in positions)
        max_position = max(
            (p.get("market_value", 0.0) for p in positions), default=0.0
        )
        concentration_risk = max_position / total_value if total_value > 0 else 0

        # Determine risk level
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

    def assess_risk_budget(
        self,
        *,
        positions: list[dict[str, Any]],
        cash: float,
        planned_new_risk: float = 0.0,
    ) -> RiskBudgetReport:
        """Assess concentration, planned-loss, sector, and theme budget gates.

        Position records may include `market_value`, `stop_distance_pct`,
        `sector`, and `theme`. Missing stop distances use the configured stop
        limit and are explicitly reported, never silently treated as zero risk.
        """

        market_value = sum(max(0.0, float(item.get("market_value", 0.0))) for item in positions)
        total_value = max(0.0, cash) + market_value
        sector_exposure: dict[str, float] = {}
        theme_exposure: dict[str, float] = {}
        horizon_exposure: dict[str, float] = {}
        warnings: list[str] = []
        blockers: list[str] = []
        planned_loss = 0.0
        stressed_loss = 0.0
        normalized_new_risk = _nonnegative_float(planned_new_risk)
        if normalized_new_risk is None:
            blockers.append("New-risk budget must be a non-negative number.")
            normalized_new_risk = 0.0

        if total_value <= 0:
            return RiskBudgetReport(
                total_value=0.0,
                cash_ratio=1.0,
                planned_loss=0.0,
                planned_loss_ratio=0.0,
                stressed_loss=0.0,
                stressed_loss_ratio=0.0,
                sector_exposure={},
                theme_exposure={},
                horizon_exposure={},
                blockers=["Portfolio value must be positive before risk budget can be assessed."],
                warnings=[],
            )

        active_positions = 0
        for item in positions:
            value = max(0.0, float(item.get("market_value", 0.0)))
            if value > 0:
                active_positions += 1
            stop_distance = item.get("stop_distance_pct")
            normalized_stop = _nonnegative_float(stop_distance)
            if normalized_stop is None or normalized_stop <= 0 or normalized_stop > 1:
                stop_distance = self.limits.stop_loss_percent
                warnings.append(
                    f"{item.get('code', 'unknown')}: missing or invalid stop distance; used configured fallback."
                )
                normalized_stop = self.limits.stop_loss_percent
            planned_loss += value * normalized_stop

            horizon = str(item.get("horizon") or "").strip().lower()
            if horizon in self.limits.max_horizon_exposure:
                horizon_exposure[horizon] = (
                    horizon_exposure.get(horizon, 0.0) + value / total_value
                )
            overnight_stress = _bounded_loss(item.get("overnight_stress_pct"))
            limit_down_stress = _bounded_loss(item.get("limit_down_stress_pct"))
            if horizon in {"short_term", "swing"} and (
                overnight_stress is None or limit_down_stress is None
            ):
                blockers.append(
                    f"{item.get('code', 'unknown')}: {horizon} plan requires overnight and limit-down stress assumptions."
                )
            stress_distance = max(
                normalized_stop,
                overnight_stress if overnight_stress is not None else normalized_stop,
                limit_down_stress if limit_down_stress is not None else normalized_stop,
            )
            if horizon in {"short_term", "swing"} and stress_distance == normalized_stop:
                warnings.append(
                    f"{item.get('code', 'unknown')}: stress loss falls back to stop distance; plan is blocked until scenarios are supplied."
                )
            stressed_loss += value * stress_distance

            for field, exposures in (("sector", sector_exposure), ("theme", theme_exposure)):
                label = str(item.get(field) or "unclassified").strip() or "unclassified"
                exposures[label] = exposures.get(label, 0.0) + value / total_value

            if value / total_value > self.limits.max_position_size:
                blockers.append(
                    f"Position {item.get('code', 'unknown')} exposure {value / total_value:.1%} exceeds limit {self.limits.max_position_size:.1%}."
                )

        cash_ratio = max(0.0, cash) / total_value
        planned_loss_ratio = planned_loss / total_value
        stressed_loss_ratio = stressed_loss / total_value
        if cash_ratio < self.limits.min_cash_ratio:
            blockers.append(
                f"Cash ratio {cash_ratio:.1%} is below minimum {self.limits.min_cash_ratio:.1%}."
            )
        if planned_loss_ratio > self.limits.max_portfolio_risk:
            blockers.append(
                f"Planned-loss budget {planned_loss_ratio:.1%} exceeds limit {self.limits.max_portfolio_risk:.1%}."
            )
        if stressed_loss_ratio > self.limits.max_portfolio_stress_loss:
            blockers.append(
                f"Stress-loss budget {stressed_loss_ratio:.1%} exceeds limit {self.limits.max_portfolio_stress_loss:.1%}."
            )
        if normalized_new_risk / total_value > self.limits.max_daily_new_risk:
            blockers.append(
                f"New-risk budget {normalized_new_risk / total_value:.1%} exceeds daily limit {self.limits.max_daily_new_risk:.1%}."
            )
        if active_positions > self.limits.max_positions:
            blockers.append(
                f"Active positions {active_positions} exceed limit {self.limits.max_positions}."
            )
        for sector, exposure in sector_exposure.items():
            if exposure > self.limits.max_sector_exposure:
                blockers.append(
                    f"Sector {sector} exposure {exposure:.1%} exceeds limit {self.limits.max_sector_exposure:.1%}."
                )
        for theme, exposure in theme_exposure.items():
            if exposure > self.limits.max_theme_exposure:
                blockers.append(
                    f"Theme {theme} exposure {exposure:.1%} exceeds limit {self.limits.max_theme_exposure:.1%}."
                )
        for horizon, exposure in horizon_exposure.items():
            limit = self.limits.max_horizon_exposure[horizon]
            if exposure > limit:
                blockers.append(
                    f"{horizon} sleeve exposure {exposure:.1%} exceeds limit {limit:.1%}."
                )

        return RiskBudgetReport(
            total_value=total_value,
            cash_ratio=cash_ratio,
            planned_loss=planned_loss,
            planned_loss_ratio=planned_loss_ratio,
            stressed_loss=stressed_loss,
            stressed_loss_ratio=stressed_loss_ratio,
            sector_exposure=sector_exposure,
            theme_exposure=theme_exposure,
            horizon_exposure=horizon_exposure,
            blockers=blockers,
            warnings=list(dict.fromkeys(warnings)),
        )

    def assess_portfolio_structure(
        self,
        *,
        positions: list[dict[str, Any]],
        cash: float,
        correlations: Optional[dict[str, float]] = None,
        stress_scenarios: Optional[dict[str, dict[str, float]]] = None,
    ) -> PortfolioStructureRiskReport:
        """Assess supplied factor, correlation, liquidity, and scenario inputs.

        ``correlations`` uses the deterministic key ``CODE_A|CODE_B`` (sorted).
        ``stress_scenarios`` maps a scenario name to factor shocks as decimal
        returns, e.g. ``{"growth_down": {"growth": -0.15}}``.
        """
        market_value = sum(max(0.0, float(item.get("market_value", 0.0))) for item in positions)
        total_value = max(0.0, cash) + market_value
        blockers: list[str] = []
        warnings: list[str] = []
        factor_exposure: dict[str, float] = {}
        liquidity: list[dict[str, Any]] = []
        if total_value <= 0:
            return PortfolioStructureRiskReport(0.0, {}, [], [], {}, ["Portfolio value must be positive."], [])

        active = [item for item in positions if float(item.get("market_value", 0.0)) > 0]
        for item in active:
            code = str(item.get("code") or "unknown")
            value = max(0.0, float(item.get("market_value", 0.0)))
            exposures = item.get("factor_exposures")
            if not isinstance(exposures, dict) or not exposures:
                blockers.append(f"{code}: factor exposures are required for structural risk assessment.")
            else:
                for factor, loading in exposures.items():
                    normalized = _bounded_signed_float(loading)
                    if normalized is None:
                        blockers.append(f"{code}: factor loading {factor} must be between -1 and 1.")
                        continue
                    factor_exposure[str(factor)] = factor_exposure.get(str(factor), 0.0) + value / total_value * normalized
            average_turnover = _positive_float(item.get("average_daily_turnover"))
            planned_exit = _positive_float(item.get("planned_exit_value")) or value
            if average_turnover is None:
                blockers.append(f"{code}: average daily turnover is required for liquidity assessment.")
                liquidity.append({"code": code, "participation_ratio": None, "estimated_exit_days": None})
            else:
                participation = planned_exit / average_turnover
                record = {"code": code, "participation_ratio": participation, "estimated_exit_days": participation / self.limits.max_liquidity_participation}
                liquidity.append(record)
                if participation > self.limits.max_liquidity_participation:
                    blockers.append(f"{code}: planned exit is {participation:.1%} of average daily turnover, above {self.limits.max_liquidity_participation:.1%}.")

        for factor, exposure in factor_exposure.items():
            if abs(exposure) > self.limits.max_factor_exposure:
                blockers.append(f"Factor {factor} exposure {exposure:.1%} exceeds limit {self.limits.max_factor_exposure:.1%}.")

        supplied_correlations = correlations or {}
        correlated_pairs: list[dict[str, Any]] = []
        for index, left in enumerate(active):
            for right in active[index + 1:]:
                left_code, right_code = sorted((str(left.get("code") or "unknown"), str(right.get("code") or "unknown")))
                key = f"{left_code}|{right_code}"
                correlation = _bounded_signed_float(supplied_correlations.get(key))
                if correlation is None:
                    blockers.append(f"Correlation input is required for pair {key}.")
                    continue
                pair = {"pair": key, "correlation": correlation, "combined_exposure": (float(left.get("market_value", 0.0)) + float(right.get("market_value", 0.0))) / total_value}
                correlated_pairs.append(pair)
                if correlation > self.limits.max_pairwise_correlation:
                    blockers.append(f"Pair {key} correlation {correlation:.2f} exceeds limit {self.limits.max_pairwise_correlation:.2f}.")

        scenario_losses: dict[str, float] = {}
        if not stress_scenarios:
            blockers.append("At least one source-labelled factor stress scenario is required.")
        else:
            for name, shocks in stress_scenarios.items():
                if not isinstance(shocks, dict) or not shocks:
                    blockers.append(f"Stress scenario {name} has no factor shocks.")
                    continue
                scenario_loss = 0.0
                for item in active:
                    exposures = item.get("factor_exposures") if isinstance(item.get("factor_exposures"), dict) else {}
                    shock = sum(
                        (_bounded_signed_float(exposures.get(factor)) or 0.0) * (_bounded_signed_float(value) or 0.0)
                        for factor, value in shocks.items()
                    )
                    scenario_loss += max(0.0, -shock) * max(0.0, float(item.get("market_value", 0.0)))
                scenario_losses[str(name)] = scenario_loss / total_value
                if scenario_losses[str(name)] > self.limits.max_structural_stress_loss:
                    blockers.append(f"Stress scenario {name} loss {scenario_losses[str(name)]:.1%} exceeds limit {self.limits.max_structural_stress_loss:.1%}.")
        rounded_exposure = {factor: round(exposure, 8) for factor, exposure in factor_exposure.items()}
        rounded_pairs = [
            {**pair, "correlation": round(float(pair["correlation"]), 8), "combined_exposure": round(float(pair["combined_exposure"]), 8)}
            for pair in correlated_pairs
        ]
        rounded_liquidity = [
            {
                **item,
                "participation_ratio": round(float(item["participation_ratio"]), 8)
                if item["participation_ratio"] is not None
                else None,
                "estimated_exit_days": round(float(item["estimated_exit_days"]), 8)
                if item["estimated_exit_days"] is not None
                else None,
            }
            for item in liquidity
        ]
        rounded_scenarios = {name: round(loss, 8) for name, loss in scenario_losses.items()}
        return PortfolioStructureRiskReport(
            total_value,
            rounded_exposure,
            rounded_pairs,
            rounded_liquidity,
            rounded_scenarios,
            list(dict.fromkeys(blockers)),
            warnings,
        )

    def suggest_position_size(
        self,
        total_capital: float,
        stock_volatility: float,
        target_risk: float = 0.02,
    ) -> float:
        """Suggest position size

        Args:
            total_capital: Total capital
            stock_volatility: Stock volatility
            target_risk: Target risk (daily)

        Returns:
            Suggested position amount
        """
        if stock_volatility == 0:
            return total_capital * self.limits.max_position_size

        # Simplified Kelly formula
        position_ratio = min(
            target_risk / stock_volatility, self.limits.max_position_size
        )
        return total_capital * position_ratio


def _nonnegative_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if result >= 0 else None


def _bounded_loss(value: Any) -> float | None:
    result = _nonnegative_float(value)
    return result if result is not None and 0 < result <= 1 else None


def _positive_float(value: Any) -> float | None:
    result = _nonnegative_float(value)
    return result if result is not None and result > 0 else None


def _bounded_signed_float(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if -1 <= result <= 1 else None
