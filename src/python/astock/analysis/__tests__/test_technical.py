"""技术分析测试"""

import pytest
import pandas as pd
import numpy as np
from datetime import date, timedelta

from astock.analysis import TechnicalAnalyzer


@pytest.fixture
def sample_df():
    """创建示例数据"""
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(100)]
    np.random.seed(42)

    # 生成模拟价格数据
    close = 10 + np.cumsum(np.random.randn(100) * 0.1)
    high = close + np.random.rand(100) * 0.5
    low = close - np.random.rand(100) * 0.5
    open_price = close + np.random.randn(100) * 0.2
    volume = np.random.rand(100) * 1000000

    return pd.DataFrame({
        "date": dates,
        "open": open_price,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume
    })


def test_add_ma(sample_df: pd.DataFrame):
    """测试均线计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_ma([5, 10, 20])

    assert "ma5" in result.columns
    assert "ma10" in result.columns
    assert "ma20" in result.columns


def test_add_macd(sample_df: pd.DataFrame):
    """测试 MACD 计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_macd()

    assert "macd" in result.columns
    assert "macd_signal" in result.columns
    assert "macd_hist" in result.columns


def test_add_kdj(sample_df: pd.DataFrame):
    """测试 KDJ 计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_kdj()

    assert "kdj_k" in result.columns
    assert "kdj_d" in result.columns
    assert "kdj_j" in result.columns


def test_add_rsi(sample_df: pd.DataFrame):
    """测试 RSI 计算"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_rsi([6, 12, 24])

    assert "rsi6" in result.columns
    assert "rsi12" in result.columns
    assert "rsi24" in result.columns


def test_get_signals(sample_df: pd.DataFrame):
    """测试信号获取"""
    analyzer = TechnicalAnalyzer(sample_df)
    analyzer.add_all()
    signals = analyzer.get_signals()

    assert "signals" in signals
    assert "latest" in signals
    assert isinstance(signals["signals"], list)


def test_add_all(sample_df: pd.DataFrame):
    """测试添加所有指标"""
    analyzer = TechnicalAnalyzer(sample_df)
    result = analyzer.add_all()

    assert "ma5" in result.columns
    assert "macd" in result.columns
    assert "kdj_k" in result.columns
    assert "rsi6" in result.columns
