from datetime import datetime, timezone

import pandas as pd
import pytest

from astock.market_data import build_public_market_observation_packet
from astock.market_desk.discovery import (
    PublicMarketDiscoveryService,
    list_public_market_discovery_archives,
    verify_public_market_discovery_archive,
)


def _overview(regime: str = "selective_risk_on") -> dict:
    return {
        "schema_version": "market_desk_overview.v1",
        "regime": {"regime": regime, "warnings": []},
    }


def _rotation() -> dict:
    return {
        "schema_version": "market_rotation.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "data_quality": "snapshot",
        "observation_pool": [{"name": "半导体"}],
        "warnings": [],
    }


@pytest.mark.asyncio
async def test_public_discovery_uses_one_market_snapshot_and_only_creates_research_queue() -> None:
    frame = pd.DataFrame(
        [
            {"代码": "600001", "名称": "甲公司", "涨跌幅": 4.0, "成交额": 300_000_000, "换手率": 2.1},
            {"代码": "300002", "名称": "乙公司", "涨跌幅": 5.0, "成交额": 250_000_000, "换手率": 3.2},
            {"代码": "920005", "名称": "北交所公司", "涨跌幅": 6.0, "成交额": 220_000_000, "换手率": 4.0},
            {"代码": "000003", "名称": "*ST 丙", "涨跌幅": 7.0, "成交额": 500_000_000},
            {"代码": "900005", "名称": "B股公司", "涨跌幅": 9.0, "成交额": 500_000_000},
            {"代码": "600004", "名称": "丁公司", "涨跌幅": 2.9, "成交额": 500_000_000},
        ]
    )
    service = PublicMarketDiscoveryService(
        spot_fetcher=lambda: frame,
        now=lambda: datetime(2026, 7, 28, 7, 0, tzinfo=timezone.utc),
    )

    universe = await service.build_universe_snapshot()
    result = service.discover(
        market_overview=_overview(),
        rotation=_rotation(),
        universe_snapshot=universe,
        candidate_limit=10,
        min_amount=200_000_000,
        min_change_pct=3.0,
    )

    assert universe["coverage"]["eligible_a_share_count"] == 4
    assert [candidate["code"] for candidate in result["candidates"]] == ["920005", "300002", "600001"]
    assert result["screening_counts"] == {
        "eligible_public_rows": 4,
        "liquid_rows": 4,
        "movement_rows": 3,
        "returned_candidates": 3,
    }
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True
    assert {candidate["discovery_status"] for candidate in result["candidates"]} == {"prepare_research"}
    assert result["rotation_context"]["mapping_status"] == "not_mapped_to_discovery_candidates"


@pytest.mark.asyncio
async def test_public_discovery_never_promotes_risk_off_observations() -> None:
    service = PublicMarketDiscoveryService(
        spot_fetcher=lambda: pd.DataFrame(
            [{"代码": "600001", "名称": "甲公司", "涨跌幅": 8.0, "成交额": 500_000_000}]
        )
    )
    universe = await service.build_universe_snapshot()

    result = service.discover(
        market_overview=_overview("risk_off"),
        rotation=_rotation(),
        universe_snapshot=universe,
    )

    assert result["candidates"][0]["discovery_status"] == "observe"
    assert result["formal_decision_eligible"] is False
    assert any("no new risk" in warning.lower() for warning in result["warnings"])


@pytest.mark.asyncio
async def test_public_discovery_blocks_when_universe_source_is_unavailable() -> None:
    def fail() -> pd.DataFrame:
        raise TimeoutError("public source timeout")

    service = PublicMarketDiscoveryService(spot_fetcher=fail)
    universe = await service.build_universe_snapshot()
    result = service.discover(
        market_overview=_overview(), rotation=_rotation(), universe_snapshot=universe
    )

    assert universe["data_quality"] == "unavailable"
    assert result["candidates"] == []
    assert result["formal_decision_eligible"] is False


@pytest.mark.asyncio
async def test_public_discovery_uses_degraded_whole_market_fallback_without_upgrading_permission() -> None:
    def fail() -> pd.DataFrame:
        raise ConnectionError("East Money unavailable")

    fallback = pd.DataFrame(
        [{"代码": "600001", "名称": "甲公司", "涨跌幅": 4.0, "成交额": 300_000_000}]
    )
    service = PublicMarketDiscoveryService(
        spot_fetcher=fail,
        fallback_spot_fetcher=lambda: fallback,
    )

    universe = await service.build_universe_snapshot()
    result = service.discover(
        market_overview=_overview(),
        rotation=_rotation(),
        universe_snapshot=universe,
    )

    assert universe["source"] == "sina.market_center.a_share_spot"
    assert universe["data_quality"] == "public_snapshot_degraded"
    assert universe["coverage"]["fallback_path"] == ["eastmoney.push2.a_share_spot"]
    assert len(universe["errors"]) == 1
    assert result["candidates"][0]["discovery_status"] == "observe"
    assert result["formal_decision_eligible"] is False
    assert any("Degradation note" in warning for warning in result["warnings"])


def test_discovery_archive_history_detects_boundary_tampering_and_duplicates(tmp_path) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "candidates": [],
    }
    packet = build_public_market_observation_packet(
        subject="market_desk_discovery", observation=discovery
    )
    archive_path = packet.write_frozen_archive(tmp_path)

    assert verify_public_market_discovery_archive(archive_path)["status"] == "pass"
    history = list_public_market_discovery_archives(tmp_path)
    assert history["valid_count"] == 1
    assert history["eod_valid_count"] == 0
    assert history["duplicate_run_dates"] == []

    altered = archive_path.with_name("altered.json")
    altered.write_text(archive_path.read_text(encoding="utf-8").replace("research_only", "not_research_only", 1), encoding="utf-8")
    tampered_history = list_public_market_discovery_archives(tmp_path)
    assert tampered_history["valid_count"] == 1
    assert tampered_history["invalid_count"] == 1


def test_discovery_archive_with_source_outage_is_not_usable_eod_evidence(tmp_path) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "eod_session": {
            "state": "after_close",
            "calendar_basis": "exchange_calendar",
            "session_date": "2026-07-28",
        },
        "source": {
            "universe_snapshot": {
                "data_quality": "unavailable",
                "coverage": {"source_row_count": 0, "eligible_a_share_count": 0},
            }
        },
        "candidates": [],
    }
    packet = build_public_market_observation_packet(
        subject="market_desk_discovery", observation=discovery
    )
    archive_path = packet.write_frozen_archive(tmp_path)

    verification = verify_public_market_discovery_archive(archive_path)
    history = list_public_market_discovery_archives(tmp_path)

    assert verification["status"] == "pass"
    assert verification["eod_validation"]["status"] == "pass"
    assert verification["coverage_validation"]["status"] == "blocked"
    assert history["eod_valid_count"] == 1
    assert history["usable_eod_valid_count"] == 0


def test_discovery_history_only_flags_duplicate_usable_eod_runs(tmp_path) -> None:
    def write_discovery(*, observed_at: str, data_quality: str, rows: int) -> None:
        discovery = {
            "schema_version": "market-desk-public-discovery.v1",
            "observed_at": observed_at,
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
            "eod_session": {
                "state": "after_close",
                "calendar_basis": "exchange_calendar",
                "session_date": "2026-07-28",
            },
            "source": {
                "universe_snapshot": {
                    "data_quality": data_quality,
                    "coverage": {"source_row_count": rows, "eligible_a_share_count": rows},
                }
            },
            "candidates": [],
        }
        build_public_market_observation_packet(
            subject="market_desk_discovery", observation=discovery
        ).write_frozen_archive(tmp_path)

    write_discovery(
        observed_at="2026-07-28T15:05:00+08:00", data_quality="unavailable", rows=0
    )
    write_discovery(
        observed_at="2026-07-28T15:10:00+08:00", data_quality="public_snapshot", rows=5000
    )
    history = list_public_market_discovery_archives(tmp_path)

    assert history["duplicate_run_dates"] == ["2026-07-28"]
    assert history["usable_eod_valid_count"] == 1
    assert history["usable_eod_duplicate_run_dates"] == []
