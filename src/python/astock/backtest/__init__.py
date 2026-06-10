"""Backtest module

Provides strategy backtesting functionality, including strategy base class and backtest engine.
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
    # Strategy related
    "Signal",
    "Trade",
    "Strategy",
    "MACrossStrategy",
    "MACDStrategy",
    "STRATEGIES",
    "get_strategy",
    # Engine related
    "BacktestEngine",
    "BacktestResult",
]
