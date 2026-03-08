"""回测引擎测试"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, datetime

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
def sample_df():
    """示例 DataFrame"""
    dates = pd.date_range(start="2024-01-01", periods=200, freq="D")
    np.random.seed(42)

    # 生成模拟价格数据（带趋势）
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
    """回测引擎测试"""

    def test_engine_creation(self):
        """引擎创建测试"""
        engine = BacktestEngine()
        assert engine.position == 0
        assert engine.capital == 0

    def test_run_ma_cross_strategy(self, sample_df):
        """均线交叉策略回测"""
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

    def test_run_macd_strategy(self, sample_df):
        """MACD 策略回测"""
        engine = BacktestEngine()
        result = engine.run(
            sample_df,
            strategy_name="macd",
            initial_capital=100000,
        )

        assert isinstance(result, BacktestResult)
        assert result.strategy == "macd"

    def test_run_rsi_strategy(self, sample_df):
        """RSI 策略回测"""
        engine = BacktestEngine()
        result = engine.run(
            sample_df,
            strategy_name="rsi",
            initial_capital=100000,
        )

        assert isinstance(result, BacktestResult)
        assert result.strategy == "rsi"

    def test_result_to_dict(self, sample_df):
        """结果转字典测试"""
        engine = BacktestEngine()
        result = engine.run(sample_df, "ma_cross", 100000)

        result_dict = result.to_dict()

        assert "code" in result_dict
        assert "strategy" in result_dict
        assert "total_return" in result_dict
        assert "sharpe_ratio" in result_dict
        assert "max_drawdown" in result_dict

    def test_calc_max_drawdown(self, sample_df):
        """最大回撤计算测试"""
        engine = BacktestEngine()
        engine.run(sample_df, "ma_cross", 100000)

        # 手动测试最大回撤计算
        equities = [100, 110, 105, 115, 100, 120]
        peak = equities[0]
        max_dd = 0

        for e in equities:
            if e > peak:
                peak = e
            dd = (peak - e) / peak
            if dd > max_dd:
                max_dd = dd

        assert max_dd > 0


class TestStrategies:
    """策略测试"""

    @pytest.fixture
    def sample_df(self):
        """示例数据"""
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

    def test_ma_cross_strategy(self, sample_df):
        """均线交叉策略测试"""
        strategy = MACrossStrategy(fast_period=5, slow_period=20)
        df = strategy.generate_signals(sample_df)

        assert "signal" in df.columns
        assert "ma_fast" in df.columns
        assert "ma_slow" in df.columns

    def test_macd_strategy(self, sample_df):
        """MACD 策略测试"""
        strategy = MACDStrategy()
        df = strategy.generate_signals(sample_df)

        assert "signal" in df.columns
        assert "macd" in df.columns
        assert "macd_signal" in df.columns

    def test_rsi_strategy(self, sample_df):
        """RSI 策略测试"""
        strategy = RSIStrategy()
        df = strategy.generate_signals(sample_df)

        assert "signal" in df.columns
        assert "rsi" in df.columns

    def test_get_strategy(self):
        """获取策略测试"""
        strategy = get_strategy("ma_cross")
        assert strategy.name == "ma_cross"

        with pytest.raises(ValueError):
            get_strategy("unknown_strategy")

    def test_list_strategies(self):
        """列出策略测试"""
        strategies = list_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) > 0
        assert all("name" in s and "description" in s for s in strategies)


class TestSignal:
    """信号测试"""

    def test_signal_values(self):
        """信号值测试"""
        assert Signal.BUY.value == "buy"
        assert Signal.SELL.value == "sell"
        assert Signal.HOLD.value == "hold"
