"""Backtest engine"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional

import numpy as np
from typing import cast
import pandas as pd

from .strategies import Signal, Strategy, Trade, get_strategy


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
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": self.equity_curve,
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
        strategy_params: Optional[dict[str, object]] = None,
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

        # Generate signals
        df = strategy.generate_signals(df)

        # Ensure date column exists and is in correct format
        if "date" not in df.columns:
            df["date"] = df.index

        # Iterate through dates and execute trades
        for i, row in df.iterrows():
            current_date = row["date"]
            if isinstance(current_date, str):
                current_date = date.fromisoformat(current_date)
            signal = row.get("signal", Signal.HOLD)
            close_price = row["close"]

            # Execute trade
            if signal == Signal.BUY and self.position == 0:
                # Buy with full position
                shares = int(self.capital / close_price / 100) * 100  # A-share lot size: 100 shares
                if shares > 0:
                    trade_value = shares * close_price
                    commission = trade_value * commission_rate
                    self.capital -= (trade_value + commission)
                    self.position = shares

                    self.trades.append(Trade(
                        date=current_date,
                        signal=Signal.BUY,
                        price=close_price,
                        shares=shares,
                        value=trade_value,
                        commission=commission,
                    ))

            elif signal == Signal.SELL and self.position > 0:
                # Sell entire position
                trade_value = self.position * close_price
                commission = trade_value * commission_rate
                self.capital += (trade_value - commission)

                self.trades.append(Trade(
                    date=current_date,
                    signal=Signal.SELL,
                    price=close_price,
                    shares=self.position,
                    value=trade_value,
                    commission=commission,
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

        # Calculate final equity
        final_price = df.iloc[-1]["close"]
        final_capital = self.capital + self.position * final_price

        # If still holding at the end, add a virtual sell for calculation
        if self.position > 0:
            self.trades.append(Trade(
                date=current_date,
                signal=Signal.SELL,
                price=final_price,
                shares=self.position,
                value=self.position * final_price,
                commission=0,
            ))

        # Calculate backtest metrics
        result = BacktestResult(
            code="",  # Set by caller
            strategy=strategy_name,
            start_date=self._get_start_date(df),
            end_date=self._get_end_date(df),
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_return=self._calc_total_return(initial_capital, final_capital),
            annual_return=self._calc_annual_return(initial_capital, final_capital, df),
            max_drawdown=self._calc_max_drawdown(),
            sharpe_ratio=self._calc_sharpe_ratio(),
            win_rate=self._calc_win_rate(),
            trades=self.trades[:-1] if self.position > 0 else self.trades,  # Exclude virtual sell
            equity_curve=self.equity_curve,
        )

        return result

    def _get_start_date(self, df: pd.DataFrame) -> date:
        """Get start date"""
        d = df.iloc[0]["date"]
        if isinstance(d, date):
            return d
        return cast(date, pd.to_datetime(d).date())

    def _get_end_date(self, df: pd.DataFrame) -> date:
        """Get end date"""
        d = df.iloc[-1]["date"]
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
