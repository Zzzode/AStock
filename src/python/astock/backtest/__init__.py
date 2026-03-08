"""回测模块

提供策略回测功能，包含策略基类、回测引擎等。
"""

from .strategies import (
    Signal,
    Trade,
    Strategy,
    MACrossStrategy,
    MACDStrategy,
    STRATEGIES,
    get_strategy,
)
from .engine import BacktestEngine, BacktestResult

__all__ = [
    # 策略相关
    "Signal",
    "Trade",
    "Strategy",
    "MACrossStrategy",
    "MACDStrategy",
    "STRATEGIES",
    "get_strategy",
    # 引擎相关
    "BacktestEngine",
    "BacktestResult",
]
