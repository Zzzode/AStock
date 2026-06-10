"""Stock screener tests"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import pandas as pd
import numpy as np

from astock.stock_picker.screener import StockScreener, ScreenResult
from astock.stock_picker.factors import Factor, FactorType


@pytest.fixture
def mock_quote_service() -> AsyncMock:
    """Mock quote service"""
    service = AsyncMock()

    # Mock daily data
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

    # Mock realtime quote
    service.get_realtime.return_value = {
        "code": "000001",
        "name": "平安银行",
        "price": 15.5,
        "pe": 8.5,
        "pb": 0.9,
    }
    service.get_stock_info.return_value = {
        "code": "000001",
        "name": "平安银行",
    }

    return service


@pytest.fixture
def screener(mock_quote_service: AsyncMock) -> StockScreener:
    """Screener instance"""
    return StockScreener(mock_quote_service, max_concurrent=5)


class TestStockScreener:
    """Stock screener tests"""

    @pytest.mark.asyncio
    async def test_screen_basic(self, screener: StockScreener, mock_quote_service: AsyncMock) -> None:
        """Basic screening test"""
        results = await screener.screen(codes=["000001"], limit=10)

        assert isinstance(results, list)
        # Verify calls
        mock_quote_service.get_daily.assert_called()
        mock_quote_service.get_stock_info.assert_called_with("000001", allow_remote=False)

    @pytest.mark.asyncio
    async def test_screen_with_factors(self, screener: StockScreener, mock_quote_service: AsyncMock) -> None:
        """Screening with factors test"""
        results = await screener.screen(
            factors=["pe_low", "pb_low"], codes=["000001"], limit=10
        )

        assert isinstance(results, list)

    def test_get_factor_list(self, screener: StockScreener) -> None:
        """Get factor list test"""
        from astock.stock_picker.factors import FACTORS

        # Returns all factors when no argument provided
        factors = screener._get_factor_list(None)
        assert len(factors) == len(FACTORS)

        # Specified factors
        factors = screener._get_factor_list(["pe_low", "pb_low"])
        assert len(factors) == 2

    def test_check_condition(self, screener: StockScreener) -> None:
        """Condition check test"""
        from astock.stock_picker.factors import FACTORS

        data = {
            "pe": 25,
            "pb": 2.5,
            "close": 15,
            "ma20": 14,
        }

        # Test PE < 30
        factor = FACTORS["pe_low"]
        assert screener._check_condition(data, factor) == True

        # Test PB < 3
        factor = FACTORS["pb_low"]
        assert screener._check_condition(data, factor) == True

    def test_compare_values(self, screener: StockScreener) -> None:
        """Value comparison test"""
        assert screener._compare_values(10, "lt", 20) == True
        assert screener._compare_values(10, "gt", 20) == False
        assert screener._compare_values(10, "eq", 10) == True
        assert screener._compare_values(10, "le", 10) == True
        assert screener._compare_values(10, "ge", 10) == True


class TestScreenResult:
    """Screen result tests"""

    def test_result_creation(self) -> None:
        """Result creation test"""
        from datetime import datetime

        result = ScreenResult(
            code="000001",
            name="平安银行",
            matched_factors=["pe_low", "pb_low"],
            matched_factor_count=2,
            factor_checks={
                "pe_low": {"matched": True},
                "pb_low": {"matched": True},
            },
            data={},
            screened_at=datetime.now(),
        )

        assert result.code == "000001"
        assert result.matched_factor_count == 2
        assert len(result.matched_factors) == 2
