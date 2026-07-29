"""Tests for content-addressed public multi-asset portfolio replay inputs."""

import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock
from unittest.mock import patch
from typer.testing import CliRunner

from astock import capabilities
from astock.backtest import (
    build_frozen_portfolio_replay_input,
    parse_frozen_portfolio_replay_input,
)
from astock.backtest import backtest_cli
from astock.market_desk import review_paper_decision


def _frames() -> dict[str, pd.DataFrame]:
    dates = pd.date_range("2026-07-01", periods=3, freq="B")
    return {
        "600460": pd.DataFrame(
            {
                "date": dates,
                "open": [10.0, 10.0, 11.0],
                "close": [10.0, 11.0, 11.0],
                "tradable": [True, True, True],
                "execution_status": ["tradable", "tradable", "tradable"],
            }
        )
    }


def test_frozen_public_portfolio_replay_verifies_exact_archive_but_blocks_formal_claims(tmp_path) -> None:
    frames = _frames()
    dates = frames["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    packet = build_frozen_portfolio_replay_input(
        frames,
        {dates[0]: {"600460": 0.5}},
        trading_calendar=dates,
        universe_references={dates[0]: "public-unverified-universe:2026-07-01"},
        observed_at="2026-07-28T15:00:00+08:00",
    )
    archive_path = packet.write_frozen_archive(tmp_path)
    replay_path = packet.write_replay_input(tmp_path)

    result = capabilities.run_frozen_portfolio_backtest(
        packet.to_dict(), source_archive_path=archive_path
    )

    assert replay_path.exists()
    assert result["data_assurance"]["status"] == "pass"
    assert result["data_assurance"]["scope"] == "exact_input_replay"
    assert result["methodology_assurance"]["status"] == "blocked"
    assert result["reproducibility_assurance"]["status"] == "blocked"
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True


def test_frozen_public_portfolio_replay_rejects_tampered_market_data(tmp_path) -> None:
    frames = _frames()
    dates = frames["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    packet = build_frozen_portfolio_replay_input(
        frames,
        {dates[0]: {"600460": 0.5}},
        trading_calendar=dates,
        universe_references={dates[0]: "public-unverified-universe:2026-07-01"},
        observed_at="2026-07-28T15:00:00+08:00",
    )
    archive_path = packet.write_frozen_archive(tmp_path)
    replay = packet.to_dict()
    replay["market_data"]["600460"][1]["close"] = 99.0

    with pytest.raises(ValueError, match="archive_id"):
        capabilities.run_frozen_portfolio_backtest(
            replay, source_archive_path=archive_path
        )


def test_legacy_replay_input_without_calendar_source_remains_parseable() -> None:
    frames = _frames()
    dates = frames["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    packet = build_frozen_portfolio_replay_input(
        frames,
        {dates[0]: {"600460": 0.5}},
        trading_calendar=dates,
        universe_references={dates[0]: "public-unverified-universe:2026-07-01"},
        observed_at="2026-07-28T15:00:00+08:00",
    )
    legacy_input = packet.to_dict()
    legacy_input.pop("trading_calendar_source")
    legacy_input["portfolio_source_manifest"].pop("calendar_source")

    parsed = parse_frozen_portfolio_replay_input(legacy_input)

    assert parsed.archive_id == packet.archive_id
    assert parsed.trading_calendar_source == "caller_supplied"


@pytest.mark.asyncio
async def test_akshare_builder_freezes_daily_bars_with_explicit_execution_assumption(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frame = _frames()["600460"].drop(columns=["tradable", "execution_status"])
    client = MagicMock()
    client.get_daily_quotes = AsyncMock(return_value=frame)
    monkeypatch.setattr(capabilities, "AkShareClient", lambda: client)
    monkeypatch.setattr(
        capabilities,
        "_fetch_akshare_exchange_trading_calendar",
        lambda _start, _end: ["2026-07-01", "2026-07-02", "2026-07-03"],
    )

    result = await capabilities.build_akshare_daily_portfolio_replay_input(
        ["600460"],
        {"2026-07-01": {"600460": 0.5}},
        start_date="2026-07-01",
        end_date="2026-07-03",
        archive_directory=tmp_path,
        observed_at="2026-07-28T15:00:00+08:00",
    )

    assert result["source_manifest"]["source"] == "akshare_public"
    assert result["coverage_manifest"]["halts"] == "unverified"
    assert result["execution_assumption"] == "daily_bar_presence_assumed_tradable"
    assert result["trading_calendar_source"] == "akshare.tool_trade_date_hist_sina"
    assert (tmp_path / (result["source_manifest"]["archive_id"].removeprefix("sha256:") + ".json")).exists()
    client.get_daily_quotes.assert_awaited_once()


@pytest.mark.asyncio
async def test_akshare_builder_uses_exchange_calendar_not_security_date_union(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _frames()["600460"].iloc[[0, 2]].drop(
        columns=["tradable", "execution_status"]
    )
    client = MagicMock()
    client.get_daily_quotes = AsyncMock(return_value=frame)
    monkeypatch.setattr(capabilities, "AkShareClient", lambda: client)
    monkeypatch.setattr(
        capabilities,
        "_fetch_akshare_exchange_trading_calendar",
        lambda _start, _end: ["2026-07-01", "2026-07-02", "2026-07-03"],
    )

    result = await capabilities.build_akshare_daily_portfolio_replay_input(
        ["600460"],
        {"2026-07-01": {"600460": 0.5}},
        start_date="2026-07-01",
        end_date="2026-07-03",
    )

    assert result["trading_calendar"] == ["2026-07-01", "2026-07-02", "2026-07-03"]
    assert len(result["market_data"]["600460"]) == 2
    assert "2026-07-02" not in {
        row["date"][:10] for row in result["market_data"]["600460"]
    }


def test_frozen_portfolio_cli_runs_archived_input(tmp_path) -> None:
    frames = _frames()
    dates = frames["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    packet = build_frozen_portfolio_replay_input(
        frames,
        {dates[0]: {"600460": 0.5}},
        trading_calendar=dates,
        universe_references={dates[0]: "public-unverified-universe:2026-07-01"},
        observed_at="2026-07-28T15:00:00+08:00",
    )
    archive_path = packet.write_frozen_archive(tmp_path)
    replay_path = packet.write_replay_input(tmp_path)

    result = CliRunner().invoke(
        backtest_cli.app,
        ["run-frozen-portfolio", str(replay_path), "--source-archive-path", str(archive_path), "--json"],
    )

    assert result.exit_code == 0, result.output
    assert '"formal_decision_eligible": false' in result.output


@pytest.mark.asyncio
async def test_public_portfolio_review_evidence_binds_replayed_return_and_benchmark(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frames = _frames()
    dates = frames["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    packet = build_frozen_portfolio_replay_input(
        frames,
        {dates[0]: {"600460": 0.5}},
        trading_calendar=dates,
        universe_references={dates[0]: "public-unverified-universe:2026-07-01"},
        observed_at="2026-07-28T15:00:00+08:00",
    )
    source_archive_path = packet.write_frozen_archive(tmp_path)
    benchmark = pd.DataFrame(
        {"date": dates, "close": [4_000.0, 4_040.0, 4_080.0]}
    )
    monkeypatch.setattr(
        capabilities,
        "_fetch_akshare_benchmark_daily",
        lambda *_: benchmark,
    )

    result = await capabilities.build_akshare_public_portfolio_review_evidence(
        packet.to_dict(),
        source_archive_path=source_archive_path,
        benchmark_id="000300.SH",
        evaluation_start="2026-07-01T15:00:00+08:00",
        evaluation_end="2026-07-03T15:00:00+08:00",
        archive_directory=tmp_path,
    )

    assert result["evidence_status"] == "public_frozen"
    assert result["review_inputs"]["benchmark_return"] == pytest.approx(0.02)
    assert result["return_evidence"]["source"] == "akshare_public"
    assert result["return_evidence"]["archive_id"] in result["return_evidence"]["paper_return_ref"]
    assert result["formal_decision_eligible"] is False

    review = review_paper_decision(
        entry_id="entry-1",
        strategy_plan={
            "plan_id": "public-review-plan",
            "horizon": "short_term",
            "state": "active",
            "target": "600460",
            "thesis": "paper-only",
            "as_of": "2026-07-01T14:00:00+08:00",
            "entry_condition": "condition",
            "invalidation_condition": "invalidates",
            "review_at": "2026-07-03T15:00:00+08:00",
            "time_stop_at": "2026-07-10T15:00:00+08:00",
            "evidence_refs": ["public:fixture"],
        },
        ic_decision={
            "schema_version": "market-desk-ic-decision.v1",
            "candidate_id": "public-review-plan",
            "decision": "conditional",
            "decided_at": "2026-07-01T14:30:00+08:00",
            "model_versions": {"market_regime": "v1"},
        },
        evaluation_start="2026-07-01T15:00:00+08:00",
        evaluation_end="2026-07-03T15:00:00+08:00",
        benchmark_id="000300.SH",
        gross_paper_return=result["review_inputs"]["gross_paper_return"],
        implementation_cost_return=result["review_inputs"]["implementation_cost_return"],
        benchmark_return=result["review_inputs"]["benchmark_return"],
        return_evidence=result["return_evidence"],
    )
    assert review.evidence_status == "public_frozen"


def test_akshare_benchmark_fetcher_uses_sina_only_after_eastmoney_retries_fail() -> None:
    fallback = pd.DataFrame(
        {"date": ["2026-07-01", "2026-07-02"], "close": [4_000.0, 4_040.0]}
    )
    with (
        patch(
            "akshare.stock_zh_index_daily_em",
            side_effect=[ConnectionError("first"), ConnectionError("second")],
        ) as eastmoney,
        patch("akshare.stock_zh_index_daily", return_value=fallback) as sina,
    ):
        result = capabilities._fetch_akshare_benchmark_daily(
            "sh000300", "2026-07-01", "2026-07-02"
        )

    assert eastmoney.call_count == 2
    sina.assert_called_once_with(symbol="sh000300")
    assert result.attrs["market_data_source"] == "akshare.stock_zh_index_daily"
    assert result.attrs["market_data_fallback_path"] == [
        "akshare.stock_zh_index_daily_em",
        "akshare.stock_zh_index_daily",
    ]
