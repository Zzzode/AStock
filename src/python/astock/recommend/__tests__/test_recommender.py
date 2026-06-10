"""Recommendation candidate pool tests"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from astock.config import RiskLevel, TradingStyle, UserConfig
from astock.recommend.recommender import Recommender
from astock.stock_picker.screener import ScreenResult


@pytest.fixture
def mock_screener() -> AsyncMock:
    screener = AsyncMock()
    screener.screen.return_value = [
        ScreenResult(
            code="000001",
            name="平安银行",
            matched_factors=["pe_low", "pb_low"],
            matched_factor_count=2,
            factor_checks={
                "pe_low": {"matched": True, "type": "valuation"},
                "pb_low": {"matched": True, "type": "valuation"},
            },
            data={"close": 10.5},
            screened_at=datetime(2026, 3, 27, 10, 0, 0),
        ),
        ScreenResult(
            code="600519",
            name="贵州茅台",
            matched_factors=["ma20_above"],
            matched_factor_count=1,
            factor_checks={
                "ma20_above": {"matched": True, "type": "momentum"},
            },
            data={"close": 1550.0},
            screened_at=datetime(2026, 3, 27, 10, 0, 0),
        ),
    ]
    return screener


@pytest.fixture
def mock_industry_service() -> AsyncMock:
    service = AsyncMock()

    async def get_stock_industry(code: str):
        mapping = {
            "000001": type("StockIndustry", (), {"industry": "银行", "industry_change": 1.2})(),
            "600519": type("StockIndustry", (), {"industry": "白酒", "industry_change": -0.8})(),
        }
        return mapping.get(code)

    service.get_stock_industry.side_effect = get_stock_industry
    return service


@pytest.mark.asyncio
async def test_build_candidate_pool_returns_packet(
    mock_screener: AsyncMock,
    mock_industry_service: AsyncMock,
) -> None:
    recommender = Recommender(mock_screener, mock_industry_service)
    config = UserConfig(
        user_id="default",
        trading_style=TradingStyle.SWING,
        risk_level=RiskLevel.MODERATE,
    )

    candidates, context = await recommender.build_candidate_pool(config, limit=2)

    assert len(candidates) == 2
    assert candidates[0].code == "000001"
    assert candidates[0].matched_factor_count == 2
    assert candidates[0].industry == "银行"
    assert context["style"] == "swing"
    assert context["risk"] == "moderate"
    assert context["returned_candidate_count"] == 2
    assert "pe_low" in context["screen_factor_keys"]


@pytest.mark.asyncio
async def test_handle_recommend_applies_preference_filters(
    mock_screener: AsyncMock,
    mock_industry_service: AsyncMock,
) -> None:
    recommender = Recommender(mock_screener, mock_industry_service)
    config = UserConfig(
        user_id="default",
        trading_style=TradingStyle.SWING,
        risk_level=RiskLevel.MODERATE,
        max_price=100.0,
        preferred_sectors=["银行"],
    )

    result = await recommender.handle_recommend(config=config, limit=5)

    assert result.success is True
    assert result.total == 1
    assert result.candidates[0].code == "000001"
    assert result.config_used["preferred_sectors"] == ["银行"]
    assert result.selection_context["postfilter_candidate_count"] == 1
