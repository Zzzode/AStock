"""Tests for source-labelled portfolio risk input construction."""

from datetime import datetime, timezone

import pandas as pd
import pytest

from astock.portfolio import PortfolioRiskInputBuilder


def _history(multiplier: float) -> pd.DataFrame:
    dates = pd.date_range("2026-04-01", periods=65, freq="B")
    closes = [100 + multiplier * index for index in range(65)]
    return pd.DataFrame({"date": dates, "close": closes, "amount": [1_000_000] * 65})


def _factor_context() -> dict[str, object]:
    return {
        "schema_version": "portfolio-factor-risk-context.v1",
        "taxonomy_version": "factor-taxonomy.v1",
        "approved_by": "quant-risk-modeler",
        "approved_at": "2026-07-28T15:00:00+08:00",
        "valid_until": "2026-08-28T15:00:00+08:00",
        "classifications": {
            "600460": {
                "taxonomy_version": "factor-taxonomy.v1",
                "as_of": "2026-07-28T15:00:00+08:00",
                "source_refs": ["risk-model:factor-taxonomy.v1"],
                "factor_exposures": {"growth": 0.8, "momentum": 0.3},
            },
            "688001": {
                "taxonomy_version": "factor-taxonomy.v1",
                "as_of": "2026-07-28T15:00:00+08:00",
                "source_refs": ["risk-model:factor-taxonomy.v1"],
                "factor_exposures": {"growth": 0.7, "momentum": 0.2},
            },
        },
        "stress_scenarios": {
            "growth_down": {
                "as_of": "2026-07-28T15:00:00+08:00",
                "source_refs": ["risk-scenario:growth-down.v1"],
                "shocks": {"growth": -0.2, "momentum": -0.1},
            }
        },
    }


@pytest.mark.asyncio
async def test_risk_input_builder_computes_turnover_and_pair_correlation() -> None:
    async def fetch(code: str) -> pd.DataFrame:
        return _history(1.0 if code == "600460" else 2.0)

    packet = await PortfolioRiskInputBuilder(
        daily_fetcher=fetch,
        now=lambda: datetime(2026, 7, 28, 7, 0, tzinfo=timezone.utc),
    ).build(["600460", "688001"], lookback=60)

    assert packet["schema_version"] == "portfolio_risk_inputs.v1"
    assert packet["positions"]["600460"]["average_daily_turnover"] == 1_000_000
    assert packet["correlations"]["600460|688001"] > 0.99
    assert packet["factor_exposures"] == {}
    assert packet["provenance"]["components"]["600460"]["sample_count"] == 61


@pytest.mark.asyncio
async def test_risk_input_builder_accepts_only_governed_factor_context() -> None:
    async def fetch(code: str) -> pd.DataFrame:
        return _history(1.0 if code == "600460" else 2.0)

    packet = await PortfolioRiskInputBuilder(
        daily_fetcher=fetch,
        now=lambda: datetime(2026, 7, 28, 7, 0, tzinfo=timezone.utc),
    ).build(["600460", "688001"], factor_risk_context=_factor_context())

    assert packet["factor_governance"]["status"] == "approved"
    assert packet["factor_exposures"]["600460"]["growth"] == 0.8
    assert packet["stress_scenarios"]["growth_down"]["growth"] == -0.2


@pytest.mark.asyncio
async def test_risk_input_builder_blocks_invalid_factor_context() -> None:
    async def fetch(code: str) -> pd.DataFrame:
        return _history(1.0 if code == "600460" else 2.0)

    context = _factor_context()
    context["valid_until"] = "2026-07-27T15:00:00+08:00"
    packet = await PortfolioRiskInputBuilder(
        daily_fetcher=fetch,
        now=lambda: datetime(2026, 7, 28, 7, 0, tzinfo=timezone.utc),
    ).build(["600460", "688001"], factor_risk_context=context)

    assert packet["factor_governance"]["status"] == "invalid"
    assert packet["factor_exposures"] == {}
    assert packet["warnings"][-1]["code"] == "factor_risk_context_invalid"


@pytest.mark.asyncio
async def test_risk_input_builder_exposes_source_failure() -> None:
    async def fetch(code: str) -> pd.DataFrame:
        if code == "600460":
            raise ConnectionError("daily source down")
        return _history(1.0)

    packet = await PortfolioRiskInputBuilder(daily_fetcher=fetch).build(["600460", "688001"])

    assert packet["data_quality"] == "snapshot"
    assert packet["provenance"]["components"]["600460"]["status"] == "unavailable"
    assert packet["errors"][0]["code"] == "daily_history_unavailable"
