"""回测策略模块"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional

import pandas as pd
import numpy as np


class Signal(Enum):
    """交易信号"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"


@dataclass
class Trade:
    """交易记录"""
    date: date
    signal: Signal
    price: float
    shares: int
    value: float
    commission: float

    def to_dict(self) -> dict[str, object]:
        return {
            "date": self.date.isoformat() if isinstance(self.date, date) else self.date,
            "signal": self.signal.value,
            "price": self.price,
            "shares": self.shares,
            "value": self.value,
            "commission": self.commission,
        }


class Strategy(ABC):
    """策略抽象基类"""

    name: str = "base"
    description: str = "基础策略"

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """生成交易信号

        Args:
            df: 包含 OHLCV 数据的 DataFrame

        Returns:
            添加 signal 列的 DataFrame
        """
        pass

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """准备数据（添加必要的技术指标）

        Args:
            df: 原始数据

        Returns:
            处理后的数据
        """
        return df.copy()


class MACrossStrategy(Strategy):
    """MA均线交叉策略

    当短期均线上穿长期均线时买入，下穿时卖出。
    """

    name = "ma_cross"
    description = "MA均线交叉策略"

    def __init__(
        self,
        short_period: int = 5,
        long_period: int = 20,
        fast_period: Optional[int] = None,
        slow_period: Optional[int] = None,
    ):
        """
        Args:
            short_period: 短期均线周期
            long_period: 长期均线周期
        """
        self.short_period = fast_period if fast_period is not None else short_period
        self.long_period = slow_period if slow_period is not None else long_period

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare_data(df)
        close = np.asarray(df["close"].astype(float), dtype=float)

        # 计算均线
        df[f"ma{self.short_period}"] = self._sma(close, self.short_period)
        df[f"ma{self.long_period}"] = self._sma(close, self.long_period)
        df["ma_fast"] = df[f"ma{self.short_period}"]
        df["ma_slow"] = df[f"ma{self.long_period}"]

        return df

    def _sma(self, data: np.ndarray, period: int) -> np.ndarray:
        """简单移动平均"""
        result = np.full(len(data), np.nan)
        for i in range(period - 1, len(data)):
            result[i] = np.mean(data[i - period + 1:i + 1])
        return result

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare_data(df)

        short_ma = df[f"ma{self.short_period}"].values
        long_ma = df[f"ma{self.long_period}"].values

        signals = np.full(len(df), Signal.HOLD, dtype=object)

        # 寻找交叉点
        for i in range(1, len(df)):
            if np.isnan(short_ma[i]) or np.isnan(long_ma[i]):
                continue
            if np.isnan(short_ma[i-1]) or np.isnan(long_ma[i-1]):
                continue

            # 短期均线上穿长期均线 -> 买入
            if short_ma[i-1] <= long_ma[i-1] and short_ma[i] > long_ma[i]:
                signals[i] = Signal.BUY
            # 短期均线下穿长期均线 -> 卖出
            elif short_ma[i-1] >= long_ma[i-1] and short_ma[i] < long_ma[i]:
                signals[i] = Signal.SELL

        df["signal"] = signals
        return df


class MACDStrategy(Strategy):
    """MACD金叉死叉策略

    当MACD柱状线由负转正时买入，由正转负时卖出。
    """

    name = "macd"
    description = "MACD金叉死叉策略"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        """
        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期
        """
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = super().prepare_data(df)
        close = np.asarray(df["close"].astype(float), dtype=float)

        # 计算 MACD
        macd, signal_line, hist = self._macd(
            close, self.fast, self.slow, self.signal_period
        )
        df["macd"] = macd
        df["macd_signal"] = signal_line
        df["macd_hist"] = hist

        return df

    def _ema(self, data: np.ndarray, period: int) -> np.ndarray:
        """指数移动平均"""
        result = np.full(len(data), np.nan)
        multiplier = 2 / (period + 1)

        # 找到第一个非 NaN 值
        first_valid = 0
        for i in range(len(data)):
            if not np.isnan(data[i]):
                first_valid = i
                break

        if first_valid >= len(data):
            return result

        # 初始值为第一个有效值
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
        """计算 MACD"""
        ema_fast = self._ema(data, fast)
        ema_slow = self._ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = self._ema(macd_line, signal)
        histogram = (macd_line - signal_line) * 2  # 柱状线
        return macd_line, signal_line, histogram

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.prepare_data(df)

        hist = df["macd_hist"].values
        signals = np.full(len(df), Signal.HOLD, dtype=object)

        # 寻找柱状线交叉点
        for i in range(1, len(df)):
            if np.isnan(hist[i]) or np.isnan(hist[i-1]):
                continue

            # 柱状线由负转正 -> 买入
            if hist[i-1] <= 0 and hist[i] > 0:
                signals[i] = Signal.BUY
            # 柱状线由正转负 -> 卖出
            elif hist[i-1] >= 0 and hist[i] < 0:
                signals[i] = Signal.SELL

        df["signal"] = signals
        return df


class RSIStrategy(Strategy):
    """RSI 超买超卖策略"""

    name = "rsi"
    description = "RSI超买超卖策略"

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


# 策略注册表
STRATEGIES: dict[str, type[Strategy]] = {
    "ma_cross": MACrossStrategy,
    "macd": MACDStrategy,
    "rsi": RSIStrategy,
}


def get_strategy(name: str, **kwargs: object) -> Strategy:
    """获取策略实例

    Args:
        name: 策略名称
        **kwargs: 策略参数

    Returns:
        策略实例

    Raises:
        ValueError: 策略名称无效
    """
    if name not in STRATEGIES:
        raise ValueError(f"Unknown strategy: {name}. Available: {list(STRATEGIES.keys())}")

    return STRATEGIES[name](**kwargs)


def list_strategies() -> list[dict[str, str]]:
    return [
        {"name": name, "description": cls.description}
        for name, cls in STRATEGIES.items()
    ]
