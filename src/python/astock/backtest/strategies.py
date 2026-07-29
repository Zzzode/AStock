"""Backtest strategies module"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

import pandas as pd
import numpy as np


class Signal(Enum):
    """Trading signal"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Trade:
    """Trade record"""
    date: date
    signal: Signal
    price: float
    shares: int
    value: float
    commission: float
    stamp_duty: float = 0.0
    transfer_fee: float = 0.0

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "signal": self.signal.value,
            "price": self.price,
            "shares": self.shares,
            "value": self.value,
            "commission": self.commission,
            "stamp_duty": self.stamp_duty,
            "transfer_fee": self.transfer_fee,
        }


class Strategy(ABC):
    """Strategy abstract base class"""

    name: str = "base"
    description: str = "Base Strategy"

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals

        Args:
            df: DataFrame with OHLCV data

        Returns:
            DataFrame with added signal column
        """
        pass

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare data (add necessary technical indicators)

        Args:
            df: Raw data

        Returns:
            Processed data
        """
        return df.copy()


class MACrossStrategy(Strategy):
    """MA Crossover Strategy

    Buy when short-term MA crosses above long-term MA; sell when it crosses below.
    """

    name = "ma_cross"
    description = "MA Crossover Strategy"

    def __init__(
        self,
        short_period: int = 5,
        long_period: int = 20,
        fast_period: Optional[int] = None,
        slow_period: Optional[int] = None,
    ):
        """
        Args:
            short_period: Short-term MA period
            long_period: Long-term MA period
        """
        self.short_period = fast_period if fast_period is not None else short_period
        self.long_period = slow_period if slow_period is not None else long_period

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare_data(df)
        close = np.asarray(df["close"].astype(float), dtype=float)

        # Calculate moving averages
        df[f"ma{self.short_period}"] = self._sma(close, self.short_period)
        df[f"ma{self.long_period}"] = self._sma(close, self.long_period)
        df["ma_fast"] = df[f"ma{self.short_period}"]
        df["ma_slow"] = df[f"ma{self.long_period}"]

        return df

    def _sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """Simple moving average"""
        result = np.full(len(data), np.nan)
        for i in range(period - 1, len(data)):
            result[i] = np.mean(data[i - period + 1:i + 1])
        return result

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare_data(df)

        short_ma = df[f"ma{self.short_period}"].values
        long_ma = df[f"ma{self.long_period}"].values

        signals = np.full(len(df), Signal.HOLD, dtype=object)

        # Find crossover points
        for i in range(1, len(df)):
            if np.isnan(short_ma[i]) or np.isnan(long_ma[i]):
                continue
            if np.isnan(short_ma[i-1]) or np.isnan(long_ma[i-1]):
                continue

            # Short-term MA crosses above long-term MA -> Buy
            if short_ma[i-1] <= long_ma[i-1] and short_ma[i] > long_ma[i]:
                signals[i] = Signal.BUY
            # Short-term MA crosses below long-term MA -> Sell
            elif short_ma[i-1] >= long_ma[i-1] and short_ma[i] < long_ma[i]:
                signals[i] = Signal.SELL

        df["signal"] = signals
        return df


class MACDStrategy(Strategy):
    """MACD Cross Strategy

    Buy when MACD histogram turns from negative to positive; sell when it turns from positive to negative.
    """

    name = "macd"
    description = "MACD Cross Strategy"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        Args:
            fast: Fast line period
            slow: Slow line period
            signal: Signal line period
        """
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare_data(df)
        close = np.asarray(df["close"].astype(float), dtype=float)

        # Calculate MACD
        macd, signal_line, hist = self._macd(
            close, self.fast, self.slow, self.signal_period
        )
        df["macd"] = macd
        df["macd_signal"] = signal_line
        df["macd_hist"] = hist

        return df

    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """Exponential moving average"""
        result = np.full(len(data), np.nan)
        multiplier = 2 / (period + 1)

        # Find the first non-NaN value
        first_valid = 0
        for i in range(len(data)):
            if not np.isnan(data[i]):
                first_valid = i
                break

        if first_valid >= len(data):
            return result

        # Initial value is the first valid value
        result[first_valid] = data[first_valid]

        for i in range(first_valid + 1, len(data)):
            if np.isnan(data[i]):
                result[i] = result[i-1]
            else:
                result[i] = (data[i] - result[i-1]) * multiplier + result[i-1]

        return result

    def _macd(
        self,
        data: np.ndarray,
        fast: int,
        slow: int,
        signal: int
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Calculate MACD"""
        ema_fast = self._ema(data, fast)
        ema_slow = self._ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self._ema(macd_line, signal)
        histogram = (macd_line - signal_line) * 2  # Histogram
        return macd_line, signal_line, histogram

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare_data(df)

        hist = df["macd_hist"].values
        signals = np.full(len(df), Signal.HOLD, dtype=object)

        # Find histogram crossover points
        for i in range(1, len(df)):
            if np.isnan(hist[i]) or np.isnan(hist[i-1]):
                continue

            # Histogram turns from negative to positive -> Buy
            if hist[i-1] <= 0 and hist[i] > 0:
                signals[i] = Signal.BUY
            # Histogram turns from positive to negative -> Sell
            elif hist[i-1] >= 0 and hist[i] < 0:
                signals[i] = Signal.SELL

        df["signal"] = signals
        return df


class RSIStrategy(Strategy):
    """RSI Overbought/Oversold Strategy"""

    name = "rsi"
    description = "RSI Overbought/Oversold Strategy"

    def __init__(self, period: int = 14, overbought: float = 70, oversold: float = 30):
        self.period = period
        self.overbought = overbought
        self.oversold = oversold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare_data(df)
        close = df["close"].astype(float)
        delta = close.diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.rolling(self.period, min_periods=self.period).mean()
        avg_loss = loss.rolling(self.period, min_periods=self.period).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        df["rsi"] = rsi

        signals = np.full(len(df), Signal.HOLD, dtype=object)
        for i in range(1, len(df)):
            if np.isnan(rsi.iloc[i]) or np.isnan(rsi.iloc[i - 1]):
                continue
            if rsi.iloc[i - 1] >= self.overbought and rsi.iloc[i] < self.overbought:
                signals[i] = Signal.SELL
            elif rsi.iloc[i - 1] <= self.oversold and rsi.iloc[i] > self.oversold:
                signals[i] = Signal.BUY

        df["signal"] = signals
        return df


# Strategy registry
STRATEGIES: dict[str, type[Strategy]] = {
    "ma_cross": MACrossStrategy,
    "macd": MACDStrategy,
    "rsi": RSIStrategy,
}


def get_strategy(name: str, **kwargs: object) -> Strategy:
    """Get strategy instance

    Args:
        name: Strategy name
        **kwargs: Strategy parameters

    Returns:
        Strategy instance

    Raises:
        ValueError: Invalid strategy name
    """
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGIES.keys())}")

    return STRATEGIES[name](**kwargs)


def list_strategies() -> list[dict[str, str]]:
    return [
        {"name": name, "description": cls.description}
        for name, cls in STRATEGIES.items()
    ]
