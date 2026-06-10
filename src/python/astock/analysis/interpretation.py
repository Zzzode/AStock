"""Signal context module

Provides historical comparison and feedback statistics as context for LLM reasoning.
Does not contain any predefined interpretation text.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SignalContext:
    """Signal context information"""

    signal_type: str           # Signal type identifier
    current_value: float       # Current value
    prev_value: Optional[float] = None   # Previous value
    prev_signal_date: Optional[str] = None  # Date of last occurrence of this signal
    signal_count_30d: int = 0  # Number of occurrences in last 30 days

    # User feedback statistics
    feedback_total: int = 0    # Total feedback count for this signal
    feedback_good: int = 0     # Positive feedback count
    feedback_bad: int = 0      # Negative feedback count
    success_rate: Optional[float] = None  # Success rate


def detect_signals(
    latest: dict,
    prev: dict,
) -> list[dict]:
    """Detect technical signals

    Args:
        latest: Latest data point
        prev: Previous day's data point

    Returns:
        List of signals, each containing type, current value, and bias
    """
    signals = []

    # MA signals
    if "ma5" in latest and "ma20" in latest:
        ma5, ma20 = latest["ma5"], latest["ma20"]
        prev_ma5, prev_ma20 = prev.get("ma5", 0), prev.get("ma20", 0)

        if prev_ma5 <= prev_ma20 and ma5 > ma20:
            signals.append({
                "type": "ma_cross_up",
                "name": "MA Golden Cross",
                "current": {"ma5": ma5, "ma20": ma20},
                "bias": "bullish",
            })
        elif prev_ma5 >= prev_ma20 and ma5 < ma20:
            signals.append({
                "type": "ma_cross_down",
                "name": "MA Death Cross",
                "current": {"ma5": ma5, "ma20": ma20},
                "bias": "bearish",
            })

        # MA arrangement
        ma10 = latest.get("ma10", 0)
        close = latest.get("close", 0)
        if ma5 > ma10 > ma20 and close > ma5:
            signals.append({
                "type": "ma_bullish_arrangement",
                "name": "Bullish Alignment",
                "current": {"ma5": ma5, "ma10": ma10, "ma20": ma20, "close": close},
                "bias": "bullish",
            })
        elif ma5 < ma10 < ma20 and close < ma5:
            signals.append({
                "type": "ma_bearish_arrangement",
                "name": "Bearish Alignment",
                "current": {"ma5": ma5, "ma10": ma10, "ma20": ma20, "close": close},
                "bias": "bearish",
            })

    # MACD signals
    if "macd_hist" in latest:
        hist = latest["macd_hist"]
        prev_hist = prev.get("macd_hist", 0)

        if prev_hist <= 0 and hist > 0:
            signals.append({
                "type": "macd_cross_up",
                "name": "MACD Golden Cross",
                "current": {"hist": hist, "macd": latest.get("macd"), "signal": latest.get("macd_signal")},
                "bias": "bullish",
            })
        elif prev_hist >= 0 and hist < 0:
            signals.append({
                "type": "macd_cross_down",
                "name": "MACD Death Cross",
                "current": {"hist": hist, "macd": latest.get("macd"), "signal": latest.get("macd_signal")},
                "bias": "bearish",
            })

    # KDJ signals
    if "kdj_j" in latest:
        j = latest["kdj_j"]
        k = latest.get("kdj_k", 0)
        d = latest.get("kdj_d", 0)

        if j < 20:
            signals.append({
                "type": "kdj_oversold",
                "name": "KDJ Oversold",
                "current": {"j": j, "k": k, "d": d},
                "bias": "bullish",
            })
        elif j > 80:
            signals.append({
                "type": "kdj_overbought",
                "name": "KDJ Overbought",
                "current": {"j": j, "k": k, "d": d},
                "bias": "bearish",
            })

    # RSI signals
    if "rsi6" in latest:
        rsi = latest["rsi6"]

        if rsi < 30:
            signals.append({
                "type": "rsi_oversold",
                "name": "RSI Oversold",
                "current": {"rsi6": rsi},
                "bias": "bullish",
            })
        elif rsi > 70:
            signals.append({
                "type": "rsi_overbought",
                "name": "RSI Overbought",
                "current": {"rsi6": rsi},
                "bias": "bearish",
            })

    return signals


def calculate_statistics(signals: list[dict]) -> dict:
    """Calculate signal statistics

    Args:
        signals: List of signals

    Returns:
        Statistics summary
    """
    bullish_count = sum(1 for s in signals if s.get("bias") == "bullish")
    bearish_count = sum(1 for s in signals if s.get("bias") == "bearish")

    return {
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "total_count": len(signals),
    }
