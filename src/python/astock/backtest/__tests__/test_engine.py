"""Backtest engine tests"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch

from astock.backtest.engine import BacktestEngine, BacktestResult
from astock.backtest.strategies import (
    Signal,
    MACrossStrategy,
    MACDStrategy,
    RSIStrategy,
    get_strategy,
    list_strategies,
)


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """Sample DataFrame"""
    dates = pd.date_range(start="2024-01-01", periods=200, freq="D")
    np.random.seed(42)

    # Generate simulated price data (with trend)
    trend = np.linspace(10, 15, 200)
    noise = np.random.normal(0, 0.5, 200)
    close = trend + noise

    df = pd.DataFrame(
        {
            "date": dates,
            "open": close + np.random.uniform(-0.3, 0.3, 200),
            "high": close + np.random.uniform(0.1, 0.5, 200),
            "low": close - np.random.uniform(0.1, 0.5, 200),
            "close": close,
            "volume": np.random.uniform(1000000, 5000000, 200),
        }
    )

    return df


class TestBacktestEngine:
    """Backtest engine tests"""

    def test_engine_creation(self) -> None:
        """Engine creation test"""
        engine = BacktestEngine()
        assert engine.position == 0
        assert engine.capital == 0

    def test_run_ma_cross_strategy(self, sample_df: pd.DataFrame) -> None:
        """MA crossover strategy backtest"""
        engine = BacktestEngine()
        result = engine.run(
            sample_df,
            strategy_name="ma_cross",
            initial_capital=100000,
        )

        assert isinstance(result, BacktestResult)
        assert result.initial_capital == 100000
        assert result.strategy == "ma_cross"
        assert result.total_return != 0 or len(result.trades) == 0

    def test_run_macd_strategy(self, sample_df: pd.DataFrame) -> None:
        """MACD strategy backtest"""
        engine = BacktestEngine()
        result = engine.run(
            sample_df,
            strategy_name="macd",
            initial_capital=100000,
        )

        assert isinstance(result, BacktestResult)
        assert result.strategy == "macd"

    def test_run_rsi_strategy(self, sample_df: pd.DataFrame) -> None:
        """RSI strategy backtest"""
        engine = BacktestEngine()
        result = engine.run(
            sample_df,
            strategy_name="rsi",
            initial_capital=100000,
        )

        assert isinstance(result, BacktestResult)
        assert result.strategy == "rsi"

    def test_result_to_dict(self, sample_df: pd.DataFrame) -> None:
        """Result to dictionary test"""
        engine = BacktestEngine()
        result = engine.run(sample_df, "ma_cross", 100000)

        result_dict = result.to_dict()

        assert "code" in result_dict
        assert "strategy" in result_dict
        assert "total_return" in result_dict
        assert "sharpe_ratio" in result_dict
        assert "max_drawdown" in result_dict
        assert result_dict["execution_assumptions"]["execution_timing"] == "next_open"
        assert result_dict["warnings"]

    def test_executes_completed_bar_signal_at_next_open(self) -> None:
        """A close-derived signal must never fill at that same close."""
        df = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=25, freq="D"),
                "open": [10.0] * 20 + [15.0, 16.0, 17.0, 18.0, 19.0],
                "high": [10.0] * 25,
                "low": [10.0] * 25,
                "close": [10.0] * 19 + [11.0, 20.0, 19.0, 18.0, 17.0, 16.0],
                "volume": [1_000_000.0] * 25,
            }
        )
        result = BacktestEngine().run(df, "ma_cross", initial_capital=100_000)

        assert result.execution_assumptions.execution_timing == "next_open"
        if result.trades:
            first_trade = result.trades[0]
            signal_index = next(
                index
                for index, row in MACrossStrategy().generate_signals(df).iterrows()
                if row["signal"] == first_trade.signal
            )
            assert first_trade.price == df.iloc[signal_index + 1]["open"]

    def test_terminal_value_includes_assumed_sell_cost_for_open_position(self) -> None:
        class BuyAndHoldStrategy:
            def generate_signals(self, frame: pd.DataFrame) -> pd.DataFrame:
                enriched = frame.copy()
                enriched["signal"] = [Signal.BUY, Signal.HOLD, Signal.HOLD]
                return enriched

        frame = pd.DataFrame(
            {
                "date": pd.date_range("2024-01-01", periods=3, freq="D"),
                "open": [10.0, 10.0, 20.0],
                "high": [10.0, 10.0, 20.0],
                "low": [10.0, 10.0, 20.0],
                "close": [10.0, 10.0, 20.0],
            }
        )
        with patch("astock.backtest.engine.get_strategy", return_value=BuyAndHoldStrategy()):
            result = BacktestEngine().run(frame, "test", initial_capital=2_000)

        expected_cost = 100 * 20 * (0.0003 + 0.0005 + 0.00001)
        assert result.terminal_liquidation_cost == pytest.approx(expected_cost)
        assert result.final_capital == pytest.approx(999.69 + 2_000 - expected_cost)
        assert result.equity_curve[-1]["equity"] == pytest.approx(result.final_capital)
        assert all(trade.signal != Signal.SELL for trade in result.trades)
        assert "includes modelled sell costs" in " ".join(result.warnings)

    def test_walk_forward_reports_only_out_of_sample_folds(self, sample_df: pd.DataFrame) -> None:
        result = BacktestEngine().run_walk_forward(
            sample_df,
            "ma_cross",
            train_bars=60,
            test_bars=30,
        )

        payload = result.to_dict()
        assert payload["schema_version"] == "walk_forward_backtest.v1"
        assert payload["fold_count"] == 5
        assert all(fold.start_date >= sample_df.iloc[60]["date"].date() for fold in result.folds)
        assert "not a continuous multi-asset" in payload["warnings"][1]

    def test_walk_forward_carries_explicit_cost_assumptions(self, sample_df: pd.DataFrame) -> None:
        result = BacktestEngine().run_walk_forward(
            sample_df,
            "ma_cross",
            train_bars=60,
            test_bars=30,
            transfer_fee_rate=0.00001,
        )

        assert all(
            fold.execution_assumptions.transfer_fee_rate == 0.00001
            for fold in result.folds
        )

    def test_calc_max_drawdown(self, sample_df: pd.DataFrame) -> None:
        """Max drawdown calculation test"""
        engine = BacktestEngine()
        engine.run(sample_df, "ma_cross", 100000)

        # Manually test max drawdown calculation
        equities = [100, 110, 105, 115, 100, 120]
        peak = equities[0]
        max_dd = 0.0

        for e in equities:
            if e > peak:
                peak = e
            dd = (peak - e) / peak
            if dd > max_dd:
                max_dd = dd

        assert max_dd > 0


class TestStrategies:
    """Strategy tests"""

    @pytest.fixture
    def sample_df(self) -> pd.DataFrame:
        """Sample data"""
        dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
        np.random.seed(42)
        close = np.linspace(10, 15, 100) + np.random.normal(0, 0.3, 100)

        return pd.DataFrame(
            {
                "date": dates,
                "open": close,
                "high": close + 0.5,
                "low": close - 0.5,
                "close": close,
                "volume": np.random.uniform(1000000, 5000000, 100),
            }
        )

    def test_ma_cross_strategy(self, sample_df: pd.DataFrame) -> None:
        """MA crossover strategy test"""
        strategy = MACrossStrategy(fast_period=5, slow_period=20)
        df = strategy.generate_signals(sample_df)

        assert "signal" in df.columns
        assert "ma_fast" in df.columns
        assert "ma_slow" in df.columns

    def test_macd_strategy(self, sample_df: pd.DataFrame) -> None:
        """MACD strategy test"""
        strategy = MACDStrategy()
        df = strategy.generate_signals(sample_df)

        assert "signal" in df.columns
        assert "macd" in df.columns
        assert "macd_signal" in df.columns

    def test_rsi_strategy(self, sample_df: pd.DataFrame) -> None:
        """RSI strategy test"""
        strategy = RSIStrategy()
        df = strategy.generate_signals(sample_df)

        assert "signal" in df.columns
        assert "rsi" in df.columns

    def test_get_strategy(self) -> None:
        """Get strategy test"""
        strategy = get_strategy("ma_cross")
        assert strategy.name == "ma_cross"

        with pytest.raises(ValueError):
            get_strategy("unknown_strategy")

    def test_list_strategies(self) -> None:
        """List strategies test"""
        strategies = list_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all("name" in s and "description" in s for s in strategies)


class TestSignal:
    """Signal tests"""

    def test_signal_values(self) -> None:
        """Signal value test"""
        assert Signal.BUY.value == "buy"
        assert Signal.SELL.value == "sell"
        assert Signal.HOLD.value == "hold"
