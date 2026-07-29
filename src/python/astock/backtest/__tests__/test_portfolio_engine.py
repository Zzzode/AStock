"""Tests for point-in-time multi-asset paper-portfolio simulation."""

import pandas as pd
import pytest

from astock.backtest import PortfolioBacktestEngine


def _frame(opens: list[float], closes: list[float], tradable: list[bool] | None = None) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-07-01", periods=len(opens), freq="B"),
            "open": opens,
            "close": closes,
            "tradable": tradable or [True] * len(opens),
        }
    )


def _source_manifest() -> dict[str, object]:
    return {
        "schema_version": "portfolio_backtest_sources.v1",
        "as_of": "2026-07-28T15:30:00+08:00",
        "archive_id": "sha256:source-archive",
        "domains": {
            "trading_calendar": "tushare_pro",
            "eod_bars": "tushare_pro",
            "halts": "tushare_pro",
            "price_limits": "tushare_pro",
            "corporate_actions": "tushare_pro",
            "delistings": "tushare_pro",
        },
        "license_attestation": {"authorized": True, "attested_by": "research-data-owner"},
    }


def _universe_snapshot(date: str, codes: list[str], source_ref: str = "universe:test") -> dict[str, object]:
    return {
        date: {
            "as_of_date": date,
            "source_ref": source_ref,
            "archive_id": f"sha256:universe-{date}",
            "members": codes,
        }
    }


def test_portfolio_engine_executes_target_at_next_open_and_sells_after_t_plus_one() -> None:
    data = {
        "600460": _frame([10, 10, 10, 10], [10, 10, 10, 10]),
        "688001": _frame([20, 20, 20, 20], [20, 20, 20, 20]),
    }
    dates = data["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    result = PortfolioBacktestEngine().run(
        data,
        {
            dates[0]: {"600460": 0.5},
            dates[1]: {"600460": 0.0, "688001": 0.5},
        },
        universe_references={dates[0]: "universe:2026-07-01", dates[1]: "universe:2026-07-02"},
        trading_calendar=dates,
    )

    assert result.to_dict()["schema_version"] == "portfolio_backtest.v1"
    assert result.trades[0]["date"] == dates[1]
    assert result.trades[0]["side"] == "buy"
    assert result.trades[1]["date"] == dates[2]
    assert result.trades[1]["side"] == "sell"


def test_portfolio_engine_requires_point_in_time_universe_and_skips_halts() -> None:
    data = {"600460": _frame([10, 10, 10], [10, 10, 10], [True, False, True])}
    dates = data["600460"]["date"].dt.strftime("%Y-%m-%d").tolist()
    with pytest.raises(ValueError, match="universe reference"):
        PortfolioBacktestEngine().run(data, {dates[0]: {"600460": 0.5}}, universe_references={}, trading_calendar=dates)

    result = PortfolioBacktestEngine().run(
        data,
        {dates[0]: {"600460": 0.5}},
        universe_references={dates[0]: "universe:2026-07-01"},
        trading_calendar=dates,
    )
    assert not result.trades
    assert any("could not trade" in warning for warning in result.warnings)


def test_portfolio_engine_skips_locked_limit_status_without_synthetic_fill() -> None:
    frame = _frame([10, 10, 10], [10, 10, 10])
    frame["execution_status"] = ["tradable", "limit_up_locked", "tradable"]
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()

    result = PortfolioBacktestEngine().run(
        {"600460": frame},
        {dates[0]: {"600460": 0.5}},
        universe_references={dates[0]: "universe:2026-07-01"},
        trading_calendar=dates,
    )

    assert result.trades == []
    assert any("could not trade" in warning for warning in result.warnings)


def test_portfolio_engine_discloses_unverified_company_action_coverage() -> None:
    frame = _frame([10, 10, 10], [10, 10, 10])
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    result = PortfolioBacktestEngine().run(
        {"600460": frame}, {dates[0]: {"600460": 0.5}},
        universe_references={dates[0]: "universe:test"}, trading_calendar=dates,
    )
    assert result.coverage["corporate_actions"] == "unverified"
    assert any("corporate_actions" in warning for warning in result.warnings)
    assert result.source_assurance["status"] == "blocked"


def test_portfolio_engine_records_institutional_source_contract(monkeypatch) -> None:
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    frame = _frame([10, 10, 10], [10, 10, 10])
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    result = PortfolioBacktestEngine().run(
        {"600460": frame},
        {dates[0]: {"600460": 0.5}},
        universe_references={dates[0]: "universe:test"},
        trading_calendar=dates,
        source_manifest=_source_manifest(),
        universe_snapshots=_universe_snapshot(dates[0], ["600460"]),
    )

    assert result.source_assurance["status"] == "pass"
    assert result.source_assurance["formal_evidence_eligible"] is False
    assert result.to_dict()["source_assurance"]["resolved_domains"]["halts"] == "tushare_pro"
    assert result.archive_assurance["status"] == "blocked"
    assert result.reproducibility_assurance["status"] == "blocked"
    assert any(
        "licensed runtime source is not configured" in failure
        for failure in result.reproducibility_assurance["failures"]
    )


def test_portfolio_engine_applies_sourced_dividend_share_distribution_and_delisting() -> None:
    frame = _frame([10, 10, 10, 10, 10], [10, 10, 10, 10, 10])
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    result = PortfolioBacktestEngine().run(
        {"600460": frame},
        {dates[0]: {"600460": 0.5}},
        universe_references={dates[0]: "universe:test"},
        trading_calendar=dates,
        coverage_manifest={
            "corporate_actions": "covered",
            "delistings": "covered",
            "price_limits": "covered",
            "halts": "covered",
        },
        source_manifest=_source_manifest(),
        price_basis="raw",
        universe_snapshots=_universe_snapshot(dates[0], ["600460"]),
        delisting_status={
            "600460": {
                "list_status": "D",
                "delist_date": dates[3],
                "source_ref": "tushare_pro.stock_basic:600460",
            }
        },
        corporate_actions={
            "600460": [
                {
                    "event_id": "dividend-1",
                    "type": "cash_dividend",
                    "effective_date": dates[2],
                    "cash_per_share": 0.2,
                    "source_ref": "tushare:dividend:1",
                },
                {
                    "event_id": "shares-1",
                    "type": "share_distribution",
                    "effective_date": dates[2],
                    "share_factor": 1.1,
                    "source_ref": "tushare:dividend:1",
                    "sequence": 1,
                },
                {
                    "event_id": "delisting-1",
                    "type": "cash_delisting",
                    "effective_date": dates[3],
                    "cash_settlement_per_share": 8.0,
                    "source_ref": "exchange:delisting:1",
                },
            ]
        },
    )

    assert [event["type"] for event in result.corporate_action_events] == [
        "cash_dividend",
        "share_distribution",
        "cash_delisting",
    ]
    assert result.corporate_action_events[0]["cash_amount"] == 1_000.0
    assert result.corporate_action_events[1]["shares_after"] == 5_500
    assert result.corporate_action_events[2]["cash_amount"] == 44_000.0
    assert result.equity_curve[-1]["positions"]["600460"] == 0


def test_covered_delisting_requires_status_and_explicit_cash_settlement() -> None:
    frame = _frame([10, 10, 10, 10], [10, 10, 10, 10])
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    arguments = {
        "market_data": {"600460": frame},
        "target_weights": {dates[0]: {"600460": 0.5}},
        "universe_references": {dates[0]: "universe:test"},
        "trading_calendar": dates,
        "coverage_manifest": {"delistings": "covered"},
        "source_manifest": _source_manifest(),
        "universe_snapshots": _universe_snapshot(dates[0], ["600460"]),
    }
    with pytest.raises(ValueError, match="status record for every code"):
        PortfolioBacktestEngine().run(**arguments)

    arguments["delisting_status"] = {
        "600460": {
            "list_status": "D",
            "delist_date": dates[2],
            "source_ref": "tushare_pro.stock_basic:600460",
        }
    }
    with pytest.raises(ValueError, match="cash_delisting settlement event"):
        PortfolioBacktestEngine().run(**arguments)


def test_reproducible_source_contract_requires_matching_frozen_universe_membership() -> None:
    frame = _frame([10, 10, 10], [10, 10, 10])
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    arguments = {
        "market_data": {"600460": frame},
        "target_weights": {dates[0]: {"600460": 0.5}},
        "universe_references": {dates[0]: "universe:test"},
        "trading_calendar": dates,
        "source_manifest": _source_manifest(),
    }
    with pytest.raises(ValueError, match="frozen point-in-time universe snapshots"):
        PortfolioBacktestEngine().run(**arguments)

    arguments["universe_snapshots"] = _universe_snapshot(dates[0], ["000001"])
    with pytest.raises(ValueError, match="outside the frozen universe"):
        PortfolioBacktestEngine().run(**arguments)

    arguments["universe_snapshots"] = _universe_snapshot(dates[0], ["600460"])
    result = PortfolioBacktestEngine().run(**arguments)
    assert result.universe_assurance["status"] == "pass"


def test_portfolio_engine_rejects_covered_actions_with_adjusted_prices_or_unknown_events() -> None:
    frame = _frame([10, 10, 10], [10, 10, 10])
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    with pytest.raises(ValueError, match="raw, unadjusted"):
        PortfolioBacktestEngine().run(
            {"600460": frame},
            {dates[0]: {"600460": 0.5}},
            universe_references={dates[0]: "universe:test"},
            trading_calendar=dates,
            coverage_manifest={"corporate_actions": "covered"},
            source_manifest=_source_manifest(),
            universe_snapshots=_universe_snapshot(dates[0], ["600460"]),
            price_basis="forward_adjusted",
        )
    with pytest.raises(ValueError, match="unsupported corporate-action"):
        PortfolioBacktestEngine().run(
            {"600460": frame},
            {dates[0]: {"600460": 0.5}},
            universe_references={dates[0]: "universe:test"},
            trading_calendar=dates,
            corporate_actions={
                "600460": [
                    {
                        "event_id": "rights-1",
                        "type": "rights_issue",
                        "effective_date": dates[1],
                        "source_ref": "exchange:rights:1",
                    }
                ]
            },
        )


def test_portfolio_engine_applies_slippage_and_volume_participation_cap() -> None:
    frame = _frame([10, 10, 10], [10, 10, 10])
    frame["volume"] = [10_000, 10_000, 10_000]
    dates = frame["date"].dt.strftime("%Y-%m-%d").tolist()
    result = PortfolioBacktestEngine().run(
        {"600460": frame},
        {dates[0]: {"600460": 0.5}},
        universe_references={dates[0]: "universe:test"},
        trading_calendar=dates,
        slippage_bps=10,
        max_participation_rate=0.1,
    )

    assert result.trades[0]["shares"] == 1_000
    assert result.trades[0]["price"] == pytest.approx(10.01)
    assert result.trades[0]["capacity_limited"] is True
    assert any("participation limit" in warning for warning in result.warnings)
