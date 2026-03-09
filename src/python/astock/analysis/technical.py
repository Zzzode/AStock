"""技术指标分析"""

import pandas as pd
import numpy as np
from typing import Optional, Any
import talib


class TechnicalAnalyzer:
    """技术指标分析器"""

    def __init__(self, df: pd.DataFrame):
        """
        Args:
            df: 包含 open, high, low, close, volume 的 DataFrame
        """
        self.df = df.copy()
        self.close = np.asarray(df["close"].astype(float), dtype=float)
        self.high = np.asarray(df["high"].astype(float), dtype=float)
        self.low = np.asarray(df["low"].astype(float), dtype=float)
        self.volume = np.asarray(df["volume"].astype(float), dtype=float)

    def add_ma(self, periods: list[int] = [5, 10, 20, 60]) -> pd.DataFrame:
        """添加均线指标

        Args:
            periods: 均线周期列表

        Returns:
            添加均线后的 DataFrame
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
        """添加 MACD 指标

        Args:
            fast: 快线周期
            slow: 慢线周期
            signal: 信号线周期

        Returns:
            添加 MACD 后的 DataFrame
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
        """添加 KDJ 指标

        Args:
            n: RSV 周期
            m1: K 值平滑周期
            m2: D 值平滑周期

        Returns:
            添加 KDJ 后的 DataFrame
        """
        rsv = (
            (self.close - talib.MIN(self.low, n)) /
            (talib.MAX(self.high, n) - talib.MIN(self.low, n))
        ) * 100

        # 处理除零情况
        rsv = np.nan_to_num(rsv, nan=50.0)

        k = talib.EMA(rsv, timeperiod=m1)
        d = talib.EMA(k, timeperiod=m2)
        j = 3 * k - 2 * d

        self.df["kdj_k"] = k
        self.df["kdj_d"] = d
        self.df["kdj_j"] = j
        return self.df

    def add_rsi(self, periods: list[int] = [6, 12, 24]) -> pd.DataFrame:
        """添加 RSI 指标

        Args:
            periods: RSI 周期列表

        Returns:
            添加 RSI 后的 DataFrame
        """
        for period in periods:
            self.df[f"rsi{period}"] = talib.RSI(self.close, timeperiod=period)
        return self.df

    def add_all(self) -> pd.DataFrame:
        """添加所有常用指标

        Returns:
            添加所有指标后的 DataFrame
        """
        self.add_ma()
        self.add_macd()
        self.add_kdj()
        self.add_rsi()
        return self.df

    def get_signals(self) -> dict[str, Any]:
        """获取技术信号

        Returns:
            信号字典
        """
        signals: list[dict[str, Any]] = []

        # 获取最新数据
        latest = self.df.iloc[-1]
        prev = self.df.iloc[-2] if len(self.df) > 1 else latest

        # MA 信号
        if "ma5" in self.df.columns and "ma20" in self.df.columns:
            if prev["ma5"] <= prev["ma20"] and latest["ma5"] > latest["ma20"]:
                signals.append({
                    "type": "ma_cross_up",
                    "name": "金叉",
                    "description": "MA5 上穿 MA20",
                    "bias": "bullish"
                })
            elif prev["ma5"] >= prev["ma20"] and latest["ma5"] < latest["ma20"]:
                signals.append({
                    "type": "ma_cross_down",
                    "name": "死叉",
                    "description": "MA5 下穿 MA20",
                    "bias": "bearish"
                })

        # MACD 信号
        if "macd" in self.df.columns:
            if prev["macd_hist"] <= 0 and latest["macd_hist"] > 0:
                signals.append({
                    "type": "macd_cross_up",
                    "name": "MACD金叉",
                    "description": "MACD 柱状线由负转正",
                    "bias": "bullish"
                })
            elif prev["macd_hist"] >= 0 and latest["macd_hist"] < 0:
                signals.append({
                    "type": "macd_cross_down",
                    "name": "MACD死叉",
                    "description": "MACD 柱状线由正转负",
                    "bias": "bearish"
                })

        # KDJ 信号
        if "kdj_k" in self.df.columns:
            # 超买超卖
            if latest["kdj_j"] < 20:
                signals.append({
                    "type": "kdj_oversold",
                    "name": "KDJ超卖",
                    "description": f"J值={latest['kdj_j']:.1f}，超卖区域",
                    "bias": "bullish"
                })
            elif latest["kdj_j"] > 80:
                signals.append({
                    "type": "kdj_overbought",
                    "name": "KDJ超买",
                    "description": f"J值={latest['kdj_j']:.1f}，超买区域",
                    "bias": "bearish"
                })

        # RSI 信号
        if "rsi6" in self.df.columns:
            if latest["rsi6"] < 30:
                signals.append({
                    "type": "rsi_oversold",
                    "name": "RSI超卖",
                    "description": f"RSI6={latest['rsi6']:.1f}，超卖区域",
                    "bias": "bullish"
                })
            elif latest["rsi6"] > 70:
                signals.append({
                    "type": "rsi_overbought",
                    "name": "RSI超买",
                    "description": f"RSI6={latest['rsi6']:.1f}，超买区域",
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
