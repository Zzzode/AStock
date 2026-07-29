"""Backtest engine"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional

import numpy as np
from typing import cast
import pandas as pd

from .strategies import Signal, Trade, get_strategy


@dataclass(frozen=True)
class AShareExecutionAssumptions:
    """Explicit daily-bar execution assumptions for A-share research backtests.

    Signals are observed after a bar closes and are executed at the next
    available bar's open.  This avoids using information from a close to trade
    at that same close.  The model remains a research approximation: it does
    not model limit-up/limit-down, halts, liquidity capacity, corporate actions,
    or survivorship bias.
    """

    commission_rate: float = 0.0003
    stamp_duty_rate: float = 0.0005
    transfer_fee_rate: float = 0.00001
    execution_timing: str = "next_open"


@dataclass
class BacktestResult:
    """Backtest result"""
    code: str
    strategy: str
    start_date: date
    end_date: date
    initial_capital: float
    final_capital: float
    total_return: float  # Total return
    annual_return: float  # Annualized return
    max_drawdown: float  # Max drawdown
    sharpe_ratio: float  # Sharpe ratio
    win_rate: float  # Win rate
    execution_assumptions: AShareExecutionAssumptions = field(
        default_factory=AShareExecutionAssumptions
    )
    terminal_liquidation_cost: float = 0.0
    warnings: list[str] = field(default_factory=list)
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[dict[str, float | str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "code": self.code,
            "strategy": self.strategy,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "initial_capital": self.initial_capital,
            "final_capital": self.final_capital,
            "total_return": self.total_return,
            "annual_return": self.annual_return,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "win_rate": self.win_rate,
            "execution_assumptions": {
                "commission_rate": self.execution_assumptions.commission_rate,
                "stamp_duty_rate": self.execution_assumptions.stamp_duty_rate,
                "transfer_fee_rate": self.execution_assumptions.transfer_fee_rate,
                "execution_timing": self.execution_assumptions.execution_timing,
            },
            "terminal_liquidation_cost": self.terminal_liquidation_cost,
            "warnings": self.warnings,
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": self.equity_curve,
        }


@dataclass(frozen=True)
class WalkForwardResult:
    """Fixed-parameter rolling out-of-sample evaluation summary."""

    strategy: str
    train_bars: int
    test_bars: int
    folds: list[BacktestResult]
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        returns = [fold.total_return for fold in self.folds]
        return {
            "schema_version": "walk_forward_backtest.v1",
            "strategy": self.strategy,
            "train_bars": self.train_bars,
            "test_bars": self.test_bars,
            "fold_count": len(self.folds),
            "mean_out_of_sample_return": float(np.mean(returns)) if returns else 0.0,
            "positive_fold_ratio": sum(value > 0 for value in returns) / len(returns) if returns else 0.0,
            "folds": [fold.to_dict() for fold in self.folds],
            "warnings": self.warnings,
        }


class BacktestEngine:
    """Backtest engine"""

    def __init__(self) -> None:
        self.position = 0  # Current position quantity
        self.capital = 0.0  # Current capital
        self.trades: list[Trade] = []
        self.equity_curve: list[dict[str, float | str]] = []

    def run(
        self,
        df: pd.DataFrame,
        strategy_name: str,
        initial_capital: float = 100000.0,
        commission_rate: float = 0.0003,
        stamp_duty_rate: float = 0.0005,
        transfer_fee_rate: float = 0.00001,
        strategy_params: Optional[dict[str, object]] = None,
        evaluation_start_index: int = 0,
    ) -> BacktestResult:
        """Run backtest

        Args:
            df: DataFrame with OHLCV data, requires date, open, high, low, close, volume columns
            strategy_name: Strategy name
            initial_capital: Initial capital
            commission_rate: Commission rate
            strategy_params: Strategy parameters

        Returns:
            Backtest result
        """
        # Reset state
        self.position = 0
        self.capital = initial_capital
        self.trades = []
        self.equity_curve = []

        # Get strategy
        params = strategy_params or {}
        strategy = get_strategy(strategy_name, **params)

        if df.empty:
            raise ValueError("Backtest requires at least one daily bar")
        required_columns = {"open", "close", "date"}
        missing_columns = sorted(required_columns - set(df.columns))
        if missing_columns:
            raise ValueError(
                "Backtest requires columns: " + ", ".join(missing_columns)
            )
        if evaluation_start_index < 0 or evaluation_start_index >= len(df):
            raise ValueError("evaluation_start_index must select an in-range bar")

        assumptions = AShareExecutionAssumptions(
            commission_rate=commission_rate,
            stamp_duty_rate=stamp_duty_rate,
            transfer_fee_rate=transfer_fee_rate,
        )
        warnings = [
            "Signals are executed at the next daily bar open; same-bar close execution is not used.",
            "This daily-bar model does not simulate limit-up/limit-down, suspensions, liquidity capacity, corporate actions, or survivorship bias.",
        ]

        # Generate signals. A signal observed at bar i may only trade at i + 1.
        df = strategy.generate_signals(df)

        # Ensure date column exists and is in correct format
        if "date" not in df.columns:
            df["date"] = df.index

        # Iterate through dates. The first bar has no prior completed bar that
        # could have produced an executable signal.
        for row_index in range(evaluation_start_index, len(df)):
            row = df.iloc[row_index]
            current_date = row["date"]
            if isinstance(current_date, str):
                current_date = date.fromisoformat(current_date)
            signal = Signal.HOLD if row_index == 0 else df.iloc[row_index - 1].get(
                "signal", Signal.HOLD
            )
            close_price = row["close"]
            execution_price = row["open"]

            if pd.isna(execution_price) or float(execution_price) <= 0:
                warnings.append(
                    f"Skipped execution on {current_date}: invalid next-bar open."
                )
                signal = Signal.HOLD
            else:
                execution_price = float(execution_price)

            # Execute trade
            if signal == Signal.BUY and self.position == 0:
                # Buy with full position
                unit_cost = execution_price * (
                    1 + commission_rate + transfer_fee_rate
                )
                shares = int(self.capital / unit_cost / 100) * 100
                if shares > 0:
                    trade_value = shares * execution_price
                    commission = trade_value * commission_rate
                    transfer_fee = trade_value * transfer_fee_rate
                    self.capital -= (trade_value + commission + transfer_fee)
                    self.position = shares

                    self.trades.append(Trade(
                        date=current_date,
                        signal=Signal.BUY,
                        price=execution_price,
                        shares=shares,
                        value=trade_value,
                        commission=commission,
                        transfer_fee=transfer_fee,
                    ))

            elif signal == Signal.SELL and self.position > 0:
                # Sell entire position
                trade_value = self.position * execution_price
                commission = trade_value * commission_rate
                stamp_duty = trade_value * stamp_duty_rate
                transfer_fee = trade_value * transfer_fee_rate
                self.capital += trade_value - commission - stamp_duty - transfer_fee

                self.trades.append(Trade(
                    date=current_date,
                    signal=Signal.SELL,
                    price=execution_price,
                    shares=self.position,
                    value=trade_value,
                    commission=commission,
                    stamp_duty=stamp_duty,
                    transfer_fee=transfer_fee,
                ))

                self.position = 0

            # Record equity curve
            equity = self.capital + self.position * close_price
            self.equity_curve.append({
                "date": current_date.isoformat() if isinstance(current_date, date) else current_date,
                "equity": equity,
                "cash": self.capital,
                "position": self.position,
                "price": close_price,
            })

        # Calculate final equity. An open position is valued as though it were
        # liquidated at the final close, including the stated A-share sell
        # costs. This prevents the reported terminal return from omitting the
        # fees required to realize the marked-to-market gain or loss.
        final_price = df.iloc[-1]["close"]
        terminal_liquidation_cost = 0.0
        if self.position > 0:
            terminal_value = self.position * float(final_price)
            terminal_liquidation_cost = terminal_value * (
                commission_rate + stamp_duty_rate + transfer_fee_rate
            )
        final_capital = self.capital + self.position * float(final_price) - terminal_liquidation_cost
        if self.equity_curve:
            self.equity_curve[-1]["equity"] = final_capital
        if terminal_liquidation_cost > 0:
            warnings.append(
                "Terminal value assumes liquidation at the final close and includes modelled sell costs; it is not an historical fill."
            )

        # Calculate backtest metrics
        result = BacktestResult(
            code="",  # Set by caller
            strategy=strategy_name,
            start_date=self._get_start_date(df.iloc[evaluation_start_index:]),
            end_date=self._get_end_date(df),
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=self._calc_total_return(initial_capital, final_capital),
            annual_return=self._calc_annual_return(initial_capital, final_capital, df),
            max_drawdown=self._calc_max_drawdown(),
            sharpe_ratio=self._calc_sharpe_ratio(),
            win_rate=self._calc_win_rate(),
            execution_assumptions=assumptions,
            terminal_liquidation_cost=terminal_liquidation_cost,
            warnings=list(dict.fromkeys(warnings)),
            trades=self.trades,
            equity_curve=self.equity_curve,
        )

        return result

    def run_walk_forward(
        self,
        df: pd.DataFrame,
        strategy_name: str,
        *,
        train_bars: int,
        test_bars: int,
        initial_capital: float = 100000.0,
        strategy_params: Optional[dict[str, object]] = None,
        commission_rate: float = 0.0003,
        stamp_duty_rate: float = 0.0005,
        transfer_fee_rate: float = 0.00001,
    ) -> WalkForwardResult:
        """Evaluate fixed strategy parameters in rolling out-of-sample folds."""
        if train_bars < 20 or test_bars < 1:
            raise ValueError("walk-forward requires at least 20 train bars and one test bar")
        if len(df) <= train_bars:
            raise ValueError("walk-forward data does not contain an out-of-sample bar")
        folds: list[BacktestResult] = []
        for evaluation_start in range(train_bars, len(df), test_bars):
            evaluation_end = min(evaluation_start + test_bars, len(df))
            window = df.iloc[:evaluation_end].copy()
            folds.append(
                BacktestEngine().run(
                    window,
                    strategy_name=strategy_name,
                    initial_capital=initial_capital,
                    strategy_params=strategy_params,
                    evaluation_start_index=evaluation_start,
                    commission_rate=commission_rate,
                    stamp_duty_rate=stamp_duty_rate,
                    transfer_fee_rate=transfer_fee_rate,
                )
            )
        return WalkForwardResult(
            strategy=strategy_name,
            train_bars=train_bars,
            test_bars=test_bars,
            folds=folds,
            warnings=[
                "Parameters are fixed across folds; this does not perform parameter optimization.",
                "Each fold is independently marked to market at its endpoint; it is not a continuous multi-asset portfolio simulation.",
                "Daily-bar limitations remain: no limit-up/down, suspensions, liquidity capacity, corporate actions, or survivorship controls.",
            ],
        )

    def _get_start_date(self, df: pd.DataFrame) -> date:
        """Get start date"""
        d = df.iloc[0]["date"]
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, date):
            return d
        return cast(date, pd.to_datetime(d).date())

    def _get_end_date(self, df: pd.DataFrame) -> date:
        """Get end date"""
        d = df.iloc[-1]["date"]
        if isinstance(d, datetime):
            return d.date()
        if isinstance(d, date):
            return d
        return cast(date, pd.to_datetime(d).date())

    def _calc_total_return(self, initial: float, final: float) -> float:
        """Calculate total return"""
        return (final - initial) / initial * 100

    def _calc_annual_return(
        self,
        initial: float,
        final: float,
        df: pd.DataFrame
    ) -> float:
        """Calculate annualized return"""
        start = self._get_start_date(df)
        end = self._get_end_date(df)
        days = (end - start).days

        if days <= 0:
            return 0.0

        years = days / 365.0
        if years <= 0:
            return 0.0

        # Annualized return = (final value / initial value)^(1/years) - 1
        annual_return = (final / initial) ** (1 / years) - 1
        return float(annual_return * 100)

    def _calc_max_drawdown(self) -> float:
        """Calculate max drawdown"""
        if not self.equity_curve:
            return 0.0

        equities = [float(e["equity"]) for e in self.equity_curve]
        peak = equities[0]
        max_dd = 0.0

        for equity in equities:
            if equity > peak:
                peak = equity
            dd = (peak - equity) / peak * 100
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calc_sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        if len(self.equity_curve) < 2:
            return 0.0

        equities = [float(e["equity"]) for e in self.equity_curve]
        returns = []

        for i in range(1, len(equities)):
            if equities[i-1] > 0:
                r = (equities[i] - equities[i-1]) / equities[i-1]
                returns.append(r)

        if not returns:
            return 0.0

        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array)

        if std_return == 0:
            return 0.0

        # Annualized Sharpe ratio (assuming 252 trading days per year)
        risk_free_rate = 0.03 / 252  # Annualized risk-free rate ~3%
        sharpe = (mean_return - risk_free_rate) / std_return * np.sqrt(252)

        return float(sharpe)

    def _calc_win_rate(self) -> float:
        """Calculate win rate"""
        # Pair buy-sell trades
        buy_sell_pairs = []
        buy_trade = None

        for trade in self.trades:
            if trade.signal == Signal.BUY:
                buy_trade = trade
            elif trade.signal == Signal.SELL and buy_trade is not None:
                buy_sell_pairs.append((buy_trade, trade))
                buy_trade = None

        if not buy_sell_pairs:
            return 0.0

        wins = sum(1 for buy, sell in buy_sell_pairs if sell.price > buy.price)
        return wins / len(buy_sell_pairs) * 100
