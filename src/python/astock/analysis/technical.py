"""Technical indicator analysis"""

import pandas as pd
import numpy as np
from typing import Optional, Any
import talib


class TechnicalAnalyzer:
    """Technical indicator analyzer"""

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: DataFrame containing open, high, low, close, volume columns
        """
        self.df = df.copy()
        self.close = np.asarray(df["close"].astype(float), dtype=float)
        self.high = np.asarray(df["high"].astype(float), dtype=float)
        self.low = np.asarray(df["low"].astype(float), dtype=float)
        self.volume = np.asarray(df["volume"].astype(float), dtype=float)

    def add_ma(self, periods: list[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """Add moving average indicators

        Args:
            periods: List of MA periods

        Returns:
            DataFrame with MA columns added
        """
        for period in periods:
            self.df[f"ma{period}"] = talib.MA(self.close, timeperiod=period)
        return self.df

    def add_macd(
        self,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> pd.DataFrame:
        """Add MACD indicator

        Args:
            fast: Fast line period
            slow: Slow line period
            signal: Signal line period

        Returns:
            DataFrame with MACD columns added
        """
        macd, signal_line, hist = talib.MACD(
            self.close,
            fastperiod=fast,
            slowperiod=slow,
            signalperiod=signal
        )
        self.df["macd"] = macd
        self.df["macd_signal"] = signal_line
        self.df["macd_hist"] = hist
        return self.df

    def add_kdj(
        self,
        n: int = 9,
        m1: int = 3,
        m2: int = 3
    ) -> pd.DataFrame:
        """Add KDJ indicator

        Args:
            n: RSV period
            m1: K value smoothing period
            m2: D value smoothing period

        Returns:
            DataFrame with KDJ columns added
        """
        # Calculate highest high and lowest low range
        high_n = talib.MAX(self.high, n)
        low_n = talib.MIN(self.low, n)
        price_range = high_n - low_n

        # Calculate RSV, handle division by zero
        with np.errstate(divide='ignore', invalid='ignore'):
            rsv = np.where(
                price_range > 0,
                (self.close - low_n) / price_range * 100,
                50.0  # When price_range is 0, RSV defaults to neutral value 50
            )

        k = talib.EMA(rsv, timeperiod=m1)
        d = talib.EMA(k, timeperiod=m2)
        j = 3 * k - 2 * d

        self.df["kdj_k"] = k
        self.df["kdj_d"] = d
        self.df["kdj_j"] = j
        return self.df

    def add_rsi(self, periods: list[int] = [6, 12, 24]) -> pd.DataFrame:
        """Add RSI indicator

        Args:
            periods: List of RSI periods

        Returns:
            DataFrame with RSI columns added
        """
        for period in periods:
            self.df[f"rsi{period}"] = talib.RSI(self.close, timeperiod=period)
        return self.df

    def add_all(self) -> pd.DataFrame:
        """Add all common indicators

        Returns:
            DataFrame with all indicators added
        """
        self.add_ma()
        self.add_macd()
        self.add_kdj()
        self.add_rsi()
        return self.df

    def get_signals(self) -> dict[str, Any]:
        """Get technical signals

        Returns:
            Signal dictionary
        """
        signals: list[dict[str, Any]] = []

        # Get latest data
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2] if len(self.df) > 1 else latest

        # MA signals
        if "ma5" in self.df.columns and "ma20" in self.df.columns:
            if prev["ma5"] <= prev["ma20"] and latest["ma5"] > latest["ma20"]:
                signals.append({
                    "type": "ma_cross_up",
                    "name": "Golden Cross",
                    "description": "MA5 crossed above MA20",
                    "bias": "bullish"
                })
            elif prev["ma5"] >= prev["ma20"] and latest["ma5"] < latest["ma20"]:
                signals.append({
                    "type": "ma_cross_down",
                    "name": "Death Cross",
                    "description": "MA5 crossed below MA20",
                    "bias": "bearish"
                })

        # MACD signals
        if "macd" in self.df.columns:
            if prev["macd_hist"] <= 0 and latest["macd_hist"] > 0:
                signals.append({
                    "type": "macd_cross_up",
                    "name": "MACD Golden Cross",
                    "description": "MACD histogram turned from negative to positive",
                    "bias": "bullish"
                })
            elif prev["macd_hist"] >= 0 and latest["macd_hist"] < 0:
                signals.append({
                    "type": "macd_cross_down",
                    "name": "MACD Death Cross",
                    "description": "MACD histogram turned from positive to negative",
                    "bias": "bearish"
                })

        # KDJ signals
        if "kdj_k" in self.df.columns:
            # Overbought/Oversold
            if latest["kdj_j"] < 20:
                signals.append({
                    "type": "kdj_oversold",
                    "name": "KDJ Oversold",
                    "description": f"J value={latest['kdj_j']:.1f}, in oversold zone",
                    "bias": "bullish"
                })
            elif latest["kdj_j"] > 80:
                signals.append({
                    "type": "kdj_overbought",
                    "name": "KDJ Overbought",
                    "description": f"J value={latest['kdj_j']:.1f}, in overbought zone",
                    "bias": "bearish"
                })

        # RSI signals
        if "rsi6" in self.df.columns:
            if latest["rsi6"] < 30:
                signals.append({
                    "type": "rsi_oversold",
                    "name": "RSI Oversold",
                    "description": f"RSI6={latest['rsi6']:.1f}, in oversold zone",
                    "bias": "bullish"
                })
            elif latest["rsi6"] > 70:
                signals.append({
                    "type": "rsi_overbought",
                    "name": "RSI Overbought",
                    "description": f"RSI6={latest['rsi6']:.1f}, in overbought zone",
                    "bias": "bearish"
                })

        return {
            "signals": signals,
            "latest": {
                "close": float(latest["close"]),
                "ma5": float(latest.get("ma5", 0)),
                "ma10": float(latest.get("ma10", 0)),
                "ma20": float(latest.get("ma20", 0)),
                "macd": float(latest.get("macd", 0)),
                "macd_signal": float(latest.get("macd_signal", 0)),
                "macd_hist": float(latest.get("macd_hist", 0)),
                "kdj_k": float(latest.get("kdj_k", 0)),
                "kdj_d": float(latest.get("kdj_d", 0)),
                "kdj_j": float(latest.get("kdj_j", 0)),
                "rsi6": float(latest.get("rsi6", 0)),
            }
        }
