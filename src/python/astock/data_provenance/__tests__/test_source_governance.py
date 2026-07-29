"""Tests for institutional market-data eligibility boundaries."""

from astock.data_provenance import (
    assess_backtest_source_manifest,
    list_market_data_source_governance,
)


def _institutional_manifest() -> dict[str, object]:
    return {
        "schema_version": "portfolio_backtest_sources.v1",
        "as_of": "2026-07-28T15:30:00+08:00",
        "archive_id": "sha256:example-frozen-archive",
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


def test_public_aggregation_is_observation_only() -> None:
    sources = list_market_data_source_governance()["sources"]
    akshare = next(item for item in sources if item["source_id"] == "akshare_public")

    assert akshare["decision_eligible"] is False
    assert akshare["reproducible_backtest_eligible"] is False


def test_jqdata_is_configured_only_when_both_login_credentials_exist(monkeypatch) -> None:
    monkeypatch.delenv("JQDATA_USERNAME", raising=False)
    monkeypatch.delenv("JQDATA_PASSWORD", raising=False)
    sources = list_market_data_source_governance()["sources"]
    jqdata = next(item for item in sources if item["source_id"] == "jqdata")
    assert jqdata["configured"] is False

    monkeypatch.setenv("JQDATA_USERNAME", "licensed-user")
    assert next(item for item in list_market_data_source_governance()["sources"] if item["source_id"] == "jqdata")["configured"] is False

    monkeypatch.setenv("JQDATA_PASSWORD", "licensed-password")
    assert next(item for item in list_market_data_source_governance()["sources"] if item["source_id"] == "jqdata")["configured"] is True


def test_backtest_manifest_requires_frozen_institutional_source_coverage(
    monkeypatch,
) -> None:
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    blocked = assess_backtest_source_manifest(
        {
            "schema_version": "portfolio_backtest_sources.v1",
            "as_of": "2026-07-28T15:30:00+08:00",
            "archive_id": "sha256:public-snapshot",
            "domains": {
                domain: "akshare_public"
                for domain in (
                    "trading_calendar",
                    "eod_bars",
                    "halts",
                    "price_limits",
                    "corporate_actions",
                    "delistings",
                )
            },
            "license_attestation": {"authorized": True, "attested_by": "owner"},
        }
    )
    passed = assess_backtest_source_manifest(_institutional_manifest())

    assert blocked["status"] == "blocked"
    assert any("observation-only" in item for item in blocked["failures"])
    assert passed["status"] == "pass"
    assert passed["resolved_domains"]["corporate_actions"] == "tushare_pro"
    assert passed["formal_evidence_eligible"] is False
    assert passed["unconfigured_sources"] == ["tushare_pro"]

    monkeypatch.setenv("TUSHARE_TOKEN", "licensed-token")
    configured = assess_backtest_source_manifest(_institutional_manifest())

    assert configured["formal_evidence_eligible"] is True
    assert configured["unconfigured_sources"] == []
