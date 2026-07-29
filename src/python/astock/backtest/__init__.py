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
from .engine import AShareExecutionAssumptions, BacktestEngine, BacktestResult, WalkForwardResult
from .frozen_signal import (
    FrozenSignalReplayInput,
    build_frozen_signal_replay_input,
    parse_frozen_signal_replay_input,
)
from .frozen_portfolio import (
    FrozenPortfolioReplayInput,
    build_frozen_portfolio_replay_input,
    parse_frozen_portfolio_replay_input,
)
from .portfolio_engine import PortfolioBacktestEngine, PortfolioBacktestResult
from .model_validation import (
    ModelSelectionFold,
    RollingModelSelectionResult,
    run_rolling_model_selection,
)

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
    "FrozenSignalReplayInput",
    "FrozenPortfolioReplayInput",
    "AShareExecutionAssumptions",
    "WalkForwardResult",
    "PortfolioBacktestEngine",
    "PortfolioBacktestResult",
    "ModelSelectionFold",
    "RollingModelSelectionResult",
    "build_frozen_signal_replay_input",
    "parse_frozen_signal_replay_input",
    "build_frozen_portfolio_replay_input",
    "parse_frozen_portfolio_replay_input",
    "run_rolling_model_selection",
]
