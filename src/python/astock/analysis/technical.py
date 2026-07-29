"""Technical indicator analysis"""

import pandas as pd
import numpy as np
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
