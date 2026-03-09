"""选股器测试"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import numpy as np

from astock.stock_picker.screener import StockScreener, ScreenResult
from astock.stock_picker.factors import Factor, FactorType


@pytest.fixture
def mock_quote_service() -> AsyncMock:
    """Mock 行情服务"""
    service = AsyncMock()

    # Mock 日线数据
    dates = pd.date_range(start="2024-01-01", periods=100, freq="D")
    df = pd.DataFrame(
        {
            "date": dates,
            "open": np.random.uniform(10, 20, 100),
            "high": np.random.uniform(20, 25, 100),
            "low": np.random.uniform(8, 12, 100),
            "close": np.random.uniform(12, 22, 100),
            "volume": np.random.uniform(1000000, 5000000, 100),
            "amount": np.random.uniform(10000000, 50000000, 100),
        }
    )
    service.get_daily.return_value = df

    # Mock 实时行情
    service.get_realtime.return_value = {
        "code": "000001",
        "name": "平安银行",
        "price": 15.5,
        "pe": 8.5,
        "pb": 0.9,
    }

    return service


@pytest.fixture
def screener(mock_quote_service: AsyncMock) -> StockScreener:
    """选股器实例"""
    return StockScreener(mock_quote_service, max_concurrent=5)


class TestStockScreener:
    """选股器测试"""

    @pytest.mark.asyncio
    async def test_screen_basic(self, screener: StockScreener, mock_quote_service: AsyncMock) -> None:
        """基础选股测试"""
        results = await screener.screen(codes=["000001"], limit=10)

        assert isinstance(results, list)
        # 验证调用
        mock_quote_service.get_daily.assert_called()

    @pytest.mark.asyncio
    async def test_screen_with_factors(self, screener: StockScreener, mock_quote_service: AsyncMock) -> None:
        """带因子选股测试"""
        results = await screener.screen(
            factors=["pe_low", "pb_low"], codes=["000001"], limit=10
        )

        assert isinstance(results, list)

    def test_get_factor_list(self, screener: StockScreener) -> None:
        """获取因子列表测试"""
        from astock.stock_picker.factors import FACTORS

        # 无参数时返回所有因子
        factors = screener._get_factor_list(None)
        assert len(factors) == len(FACTORS)

        # 指定因子
        factors = screener._get_factor_list(["pe_low", "pb_low"])
        assert len(factors) == 2

    def test_check_condition(self, screener: StockScreener) -> None:
        """条件检查测试"""
        from astock.stock_picker.factors import FACTORS

        data = {
            "pe": 25,
            "pb": 2.5,
            "close": 15,
            "ma20": 14,
        }

        # 测试 PE < 30
        factor = FACTORS["pe_low"]
        assert screener._check_condition(data, factor) == True

        # 测试 PB < 3
        factor = FACTORS["pb_low"]
        assert screener._check_condition(data, factor) == True

    def test_compare_values(self, screener: StockScreener) -> None:
        """值比较测试"""
        assert screener._compare_values(10, "lt", 20) == True
        assert screener._compare_values(10, "gt", 20) == False
        assert screener._compare_values(10, "eq", 10) == True
        assert screener._compare_values(10, "le", 10) == True
        assert screener._compare_values(10, "ge", 10) == True


class TestScreenResult:
    """选股结果测试"""

    def test_result_creation(self) -> None:
        """结果创建测试"""
        from datetime import datetime

        result = ScreenResult(
            code="000001",
            name="平安银行",
            score=5.5,
            matched_factors=["pe_low", "pb_low"],
            factor_scores={"pe_low": 1.0, "pb_low": 1.0},
            data={},
            screened_at=datetime.now(),
        )

        assert result.code == "000001"
        assert result.score == 5.5
        assert len(result.matched_factors) == 2
