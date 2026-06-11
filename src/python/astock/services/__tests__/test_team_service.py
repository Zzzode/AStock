"""Team analysis service tests"""

import json
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from typer.testing import CliRunner

from astock import cli
from astock.config import UserConfig
from astock.services.analysis_service import FullAnalysisResult
from astock.services.team_service import (
    TeamAnalysisResult,
    TeamAnalysisService,
)
from astock.stock_picker.screener import ScreenResult


@pytest.fixture
def mock_db() -> AsyncMock:
    """Mock database"""
    return AsyncMock()


@pytest.fixture
def mock_quote_service() -> AsyncMock:
    """Mock quote service"""
    service = AsyncMock()
    service.get_realtime.return_value = {
        "code": "000001",
        "name": "平安银行",
        "price": 10.5,
        "change_percent": 1.5,
        "data_quality": "full_realtime",
    }
    return service


@pytest.fixture
def mock_analysis_service() -> MagicMock:
    """Mock analysis service"""
    service = MagicMock()
    service.analyze = AsyncMock(
        return_value=FullAnalysisResult(
            code="000001",
            name="平安银行",
            indicators={
                "close": 10.5,
                "rsi6": 25.0,
                "kdj_j": 15.0,
            },
            prev_indicators={"close": 10.1},
            signals=[
                {"type": "ma_cross_up", "bias": "bullish"},
                {"type": "kdj_oversold", "bias": "bullish"},
            ],
            signal_stats={"bullish_count": 2, "bearish_count": 0, "total_count": 2},
            quote={
                "code": "000001",
                "name": "平安银行",
                "price": 10.5,
                "change_percent": 1.5,
                "data_quality": "full_realtime",
            },
            data_quality={"daily": "daily_only", "quote": "full_realtime"},
        )
    )
    service.to_dict = MagicMock(
        return_value={
            "code": "000001",
            "name": "平安银行",
            "indicators": {"close": 10.5, "rsi6": 25.0, "kdj_j": 15.0},
            "signals": [
                {"type": "ma_cross_up", "bias": "bullish"},
                {"type": "kdj_oversold", "bias": "bullish"},
            ],
            "data_quality": {"daily": "daily_only", "quote": "full_realtime"},
        }
    )
    return service


@pytest.fixture
def mock_screener() -> MagicMock:
    """Mock stock screener"""
    screener = MagicMock()
    screener.screen = AsyncMock(
        return_value=[
            ScreenResult(
                code="000001",
                name="平安银行",
                matched_factors=["pe_low", "pb_low", "kdj_oversold"],
                matched_factor_count=3,
                factor_checks={
                    "pe_low": {"matched": True},
                    "pb_low": {"matched": True},
                    "kdj_oversold": {"matched": True},
                },
                data={"close": 10.5},
                screened_at=datetime(2026, 3, 27, 10, 0, 0),
            )
        ]
    )
    return screener


@pytest.fixture
def mock_config_manager() -> MagicMock:
    """Mock config manager"""
    manager = MagicMock()
    manager.load.return_value = UserConfig()
    return manager


@pytest.fixture
def mock_feedback_learner() -> AsyncMock:
    """Mock feedback learner"""
    learner = AsyncMock()
    learner.get_team_feedback_profile.return_value = {
        "sample_count": 0,
        "aggressiveness": 0.0,
        "caution": 0.0,
    }
    learner.get_global_profile.return_value = {
        "sample_count": 0,
        "risk_appetite": 0.0,
        "strategy_weights": {},
    }
    return learner


@pytest.mark.asyncio
async def test_team_service_generates_packet_and_report(
    mock_db: AsyncMock,
    mock_quote_service: AsyncMock,
    mock_analysis_service: MagicMock,
    mock_screener: MagicMock,
    mock_config_manager: MagicMock,
    mock_feedback_learner: AsyncMock,
    tmp_path,
) -> None:
    """Team service should generate shared data packet and Markdown session"""
    service = TeamAnalysisService(
        mock_db,
        quote_service=mock_quote_service,
        analysis_service=mock_analysis_service,
        screener=mock_screener,
        config_manager=mock_config_manager,
        feedback_learner=mock_feedback_learner,
        sessions_dir=tmp_path,
    )

    result = await service.analyze("000001", question="短线适合介入吗？")

    assert result.error is None
    assert result.summary == "Data packet ready, awaiting Agent team reasoning"
    assert result.recommended_roles == ["core", "short_term"]
    assert result.packet["screen"]["mode"] == "single_stock"
    assert result.packet["orchestration"]["strategy"] == "packet_only_agent_reasoning"
    assert "scalper" in result.orchestration["active_agent_ids"]
    assert result.data_quality["quote"] == "full_realtime"
    assert result.session_path is not None
    assert Path(result.session_path).exists()


def test_team_cli_json_output() -> None:
    """CLI adapter should output structured JSON from capability kernel"""
    runner = CliRunner()
    team_result = TeamAnalysisResult(
        code="000001",
        question="当前是否适合介入？",
        name="平安银行",
        summary="Data packet ready, awaiting Agent team reasoning",
        recommended_roles=["core", "swing"],
        data_quality={"quote": "daily_only"},
        warnings=["实时行情已降级到最近交易日日线快照。"],
        orchestration={
            "strategy": "packet_only_agent_reasoning",
            "active_agent_ids": ["market-analyst", "risk-manager", "swing-trader"],
        },
        packet={"recommended_roles": ["core", "swing"]},
        session_path="data/sessions/team-000001-20260327.md",
    )

    payload_dict = TeamAnalysisService(AsyncMock()).to_dict(team_result)

    with patch(
        "astock.cli.capabilities.build_team_packet",
        new=AsyncMock(return_value=payload_dict),
    ):
        result = runner.invoke(cli.app, ["team", "000001", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["summary"] == "Data packet ready, awaiting Agent team reasoning"
    assert payload["recommended_roles"] == ["core", "swing"]
    assert payload["orchestration"]["strategy"] == "packet_only_agent_reasoning"
