"""信号上下文模块

提供历史对比和反馈统计等上下文信息，供 LLM 进行推理分析。
不包含任何预定义的解读文字。
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class SignalContext:
    """信号上下文信息"""

    signal_type: str           # 信号类型标识
    current_value: float       # 当前值
    prev_value: Optional[float] = None   # 上一个值
    prev_signal_date: Optional[str] = None  # 上次出现该信号的日期
    signal_count_30d: int = 0  # 30天内出现次数

    # 用户反馈统计
    feedback_total: int = 0    # 该信号的总反馈数
    feedback_good: int = 0     # 好评数
    feedback_bad: int = 0      # 差评数
    success_rate: Optional[float] = None  # 成功率


def detect_signals(
    latest: dict,
    prev: dict,
) -> list[dict]:
    """检测技术信号

    Args:
        latest: 最新数据
        prev: 前一日数据

    Returns:
        信号列表，每个信号包含类型、当前值、倾向
    """
    signals = []

    # MA 信号
    if "ma5" in latest and "ma20" in latest:
        ma5, ma20 = latest["ma5"], latest["ma20"]
        prev_ma5, prev_ma20 = prev.get("ma5", 0), prev.get("ma20", 0)

        if prev_ma5 <= prev_ma20 and ma5 > ma20:
            signals.append({
                "type": "ma_cross_up",
                "name": "MA金叉",
                "current": {"ma5": ma5, "ma20": ma20},
                "bias": "bullish",
            })
        elif prev_ma5 >= prev_ma20 and ma5 < ma20:
            signals.append({
                "type": "ma_cross_down",
                "name": "MA死叉",
                "current": {"ma5": ma5, "ma20": ma20},
                "bias": "bearish",
            })

        # MA 排列
        ma10 = latest.get("ma10", 0)
        close = latest.get("close", 0)
        if ma5 > ma10 > ma20 and close > ma5:
            signals.append({
                "type": "ma_bullish_arrangement",
                "name": "多头排列",
                "current": {"ma5": ma5, "ma10": ma10, "ma20": ma20, "close": close},
                "bias": "bullish",
            })
        elif ma5 < ma10 < ma20 and close < ma5:
            signals.append({
                "type": "ma_bearish_arrangement",
                "name": "空头排列",
                "current": {"ma5": ma5, "ma10": ma10, "ma20": ma20, "close": close},
                "bias": "bearish",
            })

    # MACD 信号
    if "macd_hist" in latest:
        hist = latest["macd_hist"]
        prev_hist = prev.get("macd_hist", 0)

        if prev_hist <= 0 and hist > 0:
            signals.append({
                "type": "macd_cross_up",
                "name": "MACD金叉",
                "current": {"hist": hist, "macd": latest.get("macd"), "signal": latest.get("macd_signal")},
                "bias": "bullish",
            })
        elif prev_hist >= 0 and hist < 0:
            signals.append({
                "type": "macd_cross_down",
                "name": "MACD死叉",
                "current": {"hist": hist, "macd": latest.get("macd"), "signal": latest.get("macd_signal")},
                "bias": "bearish",
            })

    # KDJ 信号
    if "kdj_j" in latest:
        j = latest["kdj_j"]
        k = latest.get("kdj_k", 0)
        d = latest.get("kdj_d", 0)

        if j < 20:
            signals.append({
                "type": "kdj_oversold",
                "name": "KDJ超卖",
                "current": {"j": j, "k": k, "d": d},
                "bias": "bullish",
            })
        elif j > 80:
            signals.append({
                "type": "kdj_overbought",
                "name": "KDJ超买",
                "current": {"j": j, "k": k, "d": d},
                "bias": "bearish",
            })

    # RSI 信号
    if "rsi6" in latest:
        rsi = latest["rsi6"]

        if rsi < 30:
            signals.append({
                "type": "rsi_oversold",
                "name": "RSI超卖",
                "current": {"rsi6": rsi},
                "bias": "bullish",
            })
        elif rsi > 70:
            signals.append({
                "type": "rsi_overbought",
                "name": "RSI超买",
                "current": {"rsi6": rsi},
                "bias": "bearish",
            })

    return signals


def calculate_statistics(signals: list[dict]) -> dict:
    """计算信号统计

    Args:
        signals: 信号列表

    Returns:
        统计信息
    """
    bullish_count = sum(1 for s in signals if s.get("bias") == "bullish")
    bearish_count = sum(1 for s in signals if s.get("bias") == "bearish")

    return {
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "total_count": len(signals),
    }