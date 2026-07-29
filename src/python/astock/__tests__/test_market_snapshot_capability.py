"""Capability and CLI coverage for the whole-market snapshot adapter."""

import json
from datetime import datetime, timedelta, timezone

from unittest.mock import AsyncMock, patch

import pandas as pd
import pytest
from typer.testing import CliRunner

from astock import capabilities, cli
from astock.data import StockIndustry
from astock.market_data import build_public_market_observation_packet
from astock.market_rotation import MarketRotationService


@pytest.mark.asyncio
async def test_build_market_snapshot_v1_delegates_to_service() -> None:
    expected = {"schema_version": "market_snapshot.v1"}
    with patch(
        "astock.capabilities.MarketSnapshotService.build_snapshot",
        new=AsyncMock(return_value=expected),
    ) as build_snapshot:
        result = await capabilities.build_market_snapshot_v1(
            etf_codes=["510300"], industry_codes=["512480"]
        )

    assert result == expected
    build_snapshot.assert_awaited_once_with(
        etf_codes=["510300"], industry_codes=["512480"]
    )


@pytest.mark.asyncio
async def test_build_market_rotation_v1_delegates_to_service() -> None:
    expected = {"schema_version": "market_rotation.v1"}
    with patch(
        "astock.capabilities.MarketRotationService.build_cross_section",
        new=AsyncMock(return_value=expected),
    ) as build_cross_section:
        result = await capabilities.build_market_rotation_v1(
            include_concepts=False,
            observation_limit=12,
            history_validation_limit=3,
            history_scope="full",
            history_concurrency=4,
        )

    assert result == expected
    build_cross_section.assert_awaited_once_with(
        include_concepts=False,
        observation_limit=12,
        history_validation_limit=3,
        history_scope="full",
        history_concurrency=4,
    )


@pytest.mark.asyncio
async def test_public_market_discovery_combines_whole_market_context_but_never_releases_a_decision() -> None:
    overview = {"schema_version": "market_desk_overview.v1", "regime": {"regime": "risk_off"}}
    rotation = {"schema_version": "market_rotation.v1"}
    universe = {"schema_version": "market-desk-public-universe-snapshot.v1"}
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "formal_decision_eligible": False,
        "no_order_execution": True,
    }
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value=overview)),
        patch("astock.capabilities.build_market_rotation_v1", new=AsyncMock(return_value=rotation)),
        patch("astock.capabilities.PublicMarketDiscoveryService.build_universe_snapshot", new=AsyncMock(return_value=universe)),
        patch("astock.capabilities.PublicMarketDiscoveryService.discover", return_value=discovery) as discover,
    ):
        result = await capabilities.discover_public_market_desk_opportunities(
            include_concepts=False,
            observation_limit=12,
            candidate_limit=8,
            min_amount=100_000_000,
            min_change_pct=2.0,
        )

    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True
    discover.assert_called_once_with(
        market_overview=overview,
        rotation=rotation,
        universe_snapshot=universe,
        candidate_limit=8,
        min_amount=100_000_000,
        min_change_pct=2.0,
    )


@pytest.mark.asyncio
async def test_public_discovery_attaches_only_source_referenced_market_context(tmp_path) -> None:
    market_map_path = tmp_path / "market-map.json"
    capabilities.upsert_market_subject_mapping(
        {
            "code": "600460",
            "name": "士兰微",
            "industry": "Semiconductor",
            "sectors": ["Electronics"],
            "themes": ["Power semiconductor"],
            "source_refs": ["official:issuer:2026-07-28"],
        },
        market_map_path=market_map_path,
    )
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "candidates": [{"code": "600460"}, {"code": "300001"}],
        "warnings": [],
    }
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value={})),
        patch("astock.capabilities.build_market_rotation_v1", new=AsyncMock(return_value={})),
        patch("astock.capabilities.PublicMarketDiscoveryService.build_universe_snapshot", new=AsyncMock(return_value={})),
        patch("astock.capabilities.PublicMarketDiscoveryService.discover", return_value=discovery),
    ):
        result = await capabilities.discover_public_market_desk_opportunities(
            include_concepts=False, market_map_path=market_map_path
        )

    assert result["candidates"][0]["market_subject_mapping_status"] == "source_mapped"
    assert result["candidates"][0]["market_subject_context"]["relationships"]["industry"]["name"] == "Semiconductor"
    assert result["candidates"][1]["market_subject_mapping_status"] == "mapping_required"
    assert result["market_subject_mapping_coverage"] == {
        "mapped_candidate_count": 1,
        "unmapped_candidate_count": 1,
        "mapping_status": "source_referenced_context_only",
        "decision_weight": 0,
    }


@pytest.mark.asyncio
async def test_record_public_discovery_freezes_exact_research_only_queue(tmp_path) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "candidates": [],
    }
    with patch(
        "astock.capabilities.discover_public_market_desk_opportunities",
        new=AsyncMock(return_value=discovery),
    ):
        result = await capabilities.record_public_market_desk_discovery(
            archive_directory=tmp_path
        )

    assert result["operation"] == "record_public_discovery_only"
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True
    assert capabilities.verify_frozen_market_data_archive(
        result["source_archive_path"],
        expected_archive_id=result["source_manifest"]["archive_id"],
        expected_source="akshare_public",
    )["status"] == "pass"


@pytest.mark.asyncio
async def test_public_discovery_industry_enrichment_requires_frozen_discovery_and_freezes_mapping(
    tmp_path, monkeypatch
) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "candidates": [
            {
                "candidate_id": "public-discovery:600460:2026-07-28",
                "code": "600460",
                "name": "士兰微",
                "formal_decision_eligible": False,
                "research_only": True,
                "no_order_execution": True,
            }
        ],
    }
    source_packet = build_public_market_observation_packet(
        subject="market_desk_discovery", observation=discovery
    )
    source_archive = source_packet.write_frozen_archive(tmp_path / "discovery")

    industry_service = type("IndustryServiceStub", (), {})()
    industry_service.initialize = AsyncMock()
    industry_service.get_stock_industry = AsyncMock(
        return_value=StockIndustry(
            code="600460", name="士兰微", industry="半导体", industry_code="BK1036"
        )
    )
    monkeypatch.setattr(capabilities, "get_industry_service", lambda: industry_service)

    result = await capabilities.enrich_public_discovery_industry_context(
        source_archive,
        mapping_archive_directory=tmp_path / "mapping-archives",
        market_map_path=tmp_path / "market-map.json",
    )

    assert result["mapped_count"] == 1
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True
    assert capabilities.verify_frozen_market_data_archive(
        result["mapping_archive_path"],
        expected_archive_id=result["mapping_archive_id"],
        expected_source="akshare_public",
    )["status"] == "pass"
    mapping = capabilities.resolve_market_subject_context(
        "600460", market_map_path=tmp_path / "market-map.json"
    )
    assert mapping["relationships"]["industry"]["name"] == "半导体"
    assert mapping["source_refs"][0].startswith("public-industry-enrichment:sha256:")
    with pytest.raises(ValueError, match="mapping_archive_path"):
        capabilities.promote_public_market_desk_discovery_candidate(
            source_archive_path=source_archive,
            candidate_id="public-discovery:600460:2026-07-28",
            market_map_path=tmp_path / "market-map.json",
            ledger_path=tmp_path / "blocked-ledger.json",
        )
    promoted = capabilities.promote_public_market_desk_discovery_candidate(
        source_archive_path=source_archive,
        candidate_id="public-discovery:600460:2026-07-28",
        market_map_path=tmp_path / "market-map.json",
        mapping_archive_path=result["mapping_archive_path"],
        ledger_path=tmp_path / "ledger.json",
    )
    assert promoted["status"] == "promoted_to_monitoring"
    assert promoted["formal_decision_eligible"] is False


@pytest.mark.asyncio
async def test_frozen_public_rotation_history_assurance_recomputes_embedded_records(
    tmp_path,
) -> None:
    async def industries() -> pd.DataFrame:
        return pd.DataFrame([{"板块名称": "创新药", "涨跌幅": 2.0}])

    async def concepts() -> pd.DataFrame:
        return pd.DataFrame()

    async def history(
        _component: str, _name: str, _start: object, _end: object
    ) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "日期": pd.date_range(end="2026-07-28", periods=70),
                "收盘": list(range(100, 170)),
            }
        )

    rotation = await MarketRotationService(
        industry_fetcher=industries,
        concept_fetcher=concepts,
        history_fetcher=history,
    ).build_cross_section(include_concepts=False, history_validation_limit=1)
    packet = capabilities.build_public_market_observation_packet(
        subject="market_rotation", observation=rotation
    )
    archive_path = packet.write_frozen_archive(tmp_path)

    assurance = capabilities.verify_frozen_public_market_rotation_history_evidence(
        archive_path
    )

    assert assurance["status"] == "pass"
    assert assurance["history_evidence"]["status"] == "pass"
    assert assurance["formal_decision_eligible"] is False


@pytest.mark.asyncio
async def test_scheduled_eod_discovery_skips_before_close_and_is_idempotent(tmp_path) -> None:
    overview = {
        "schema_version": "market_desk_overview.v1",
        "snapshot": {
            "observed_at": "2026-07-28T15:10:00+08:00",
            "market_session": {"state": "after_close", "calendar_basis": "exchange_calendar"},
        },
    }
    history = {
        "records": [
            {
                "status": "pass",
                "observed_at": "2026-07-28T15:05:00+08:00",
                "archive_id": "sha256:prior",
                "eod_validation": {"status": "pass"},
                "coverage_validation": {"status": "pass"},
            }
        ]
    }
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value=overview)),
        patch("astock.capabilities.list_public_market_discovery_archives", return_value=history),
        patch("astock.capabilities.record_public_market_desk_discovery", new=AsyncMock()) as record,
    ):
        result = await capabilities.run_public_market_desk_eod_discovery(
            archive_directory=tmp_path
        )

    assert result["status"] == "skipped"
    assert result["reason"] == "valid_eod_discovery_exists_for_session_date"
    assert result["existing_archive_ids"] == ["sha256:prior"]
    record.assert_not_awaited()


@pytest.mark.asyncio
async def test_scheduled_eod_discovery_binds_verified_close_metadata_to_the_archive(tmp_path) -> None:
    overview = {
        "schema_version": "market_desk_overview.v1",
        "snapshot": {
            "observed_at": "2026-07-28T15:10:00+08:00",
            "market_session": {"state": "after_close", "calendar_basis": "exchange_calendar"},
        },
    }
    recorded = {
        "schema_version": "market-desk-public-discovery.v1",
        "source_archive_path": str(tmp_path / "discovery.json"),
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value=overview)),
        patch("astock.capabilities.list_public_market_discovery_archives", return_value={"records": []}),
        patch(
            "astock.capabilities.record_public_market_desk_discovery",
            new=AsyncMock(return_value=recorded),
        ) as record,
    ):
        result = await capabilities.run_public_market_desk_eod_discovery(
            archive_directory=tmp_path
        )

    assert result["status"] == "recorded"
    assert record.await_args.kwargs["eod_session"] == {
        "state": "after_close",
        "calendar_basis": "exchange_calendar",
        "session_date": "2026-07-28",
        "market_overview_observed_at": "2026-07-28T15:10:00+08:00",
    }


@pytest.mark.asyncio
async def test_market_desk_team_packet_reuses_one_shared_whole_market_input(monkeypatch, tmp_path) -> None:
    overview = {
        "schema_version": "market_desk_overview.v1",
        "snapshot": {"observed_at": "2026-07-28T15:10:00+08:00"},
        "regime": {"regime": "selective_risk_on"},
    }
    rotation = {"schema_version": "market_rotation.v1", "warnings": []}
    universe = {
        "source": "eastmoney.push2.a_share_spot",
        "observed_at": "2026-07-28T15:10:00+08:00",
        "data_quality": "public_snapshot",
        "rows": [{"code": "600001", "amount": 500_000_000, "change_pct": 4.0}],
        "coverage": {"source_row_count": 1, "eligible_a_share_count": 1},
        "warnings": [],
        "errors": [],
    }
    class _DiscoveryService:
        async def build_universe_snapshot(self):
            return universe
        def discover(self, *, market_overview, rotation, universe_snapshot, **_):
            assert market_overview is overview
            assert rotation is rotation_packet
            assert universe_snapshot is universe
            return {"schema_version": "market-desk-public-discovery.v1", "candidates": [], "warnings": []}
    rotation_packet = rotation
    monkeypatch.setattr(capabilities, "PublicMarketDiscoveryService", _DiscoveryService)
    monkeypatch.setattr(capabilities, "build_market_desk_overview", AsyncMock(return_value=overview))
    monkeypatch.setattr(capabilities, "build_market_rotation_v1", AsyncMock(return_value=rotation))
    monkeypatch.setattr(capabilities, "_attach_discovery_market_subject_context", lambda value, **_: dict(value))
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: {"market_data_mode": "public_observation"})
    monkeypatch.setattr(capabilities, "get_market_desk_strategy_books", lambda **_: {"book_counts": {}})
    monkeypatch.setattr(capabilities, "get_market_desk_review_queue", lambda **_: {"due_count": 0})
    monkeypatch.setattr(capabilities, "get_market_desk_postmortem_queue", lambda **_: {"due_count": 0})

    result = await capabilities.build_market_desk_team_packet(ledger_path=tmp_path / "ledger.json")

    assert result["observed_at"] == "2026-07-28T15:10:00+08:00"
    assert result["market_overview"] is overview
    assert result["rotation"] is rotation
    assert result["whole_market_discovery"]["schema_version"] == "market-desk-public-discovery.v1"
    assert result["team_orchestration"]["binding_veto_roles"] == [
        "data-verifier", "risk-analyst", "quant-risk-modeler", "execution-liquidity-analyst", "compliance-officer"
    ]
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True


def test_promote_frozen_discovery_candidate_creates_monitoring_entry_once(tmp_path) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "selection_rule": {"required": {"minimum_amount": 200000000}},
        "source_manifest": {"source": "akshare_public"},
        "candidates": [
            {
                "candidate_id": "public-discovery:600460:2026-07-28",
                "code": "600460",
                "name": "士兰微",
                "market_subject_mapping_status": "source_mapped",
                "market_subject_context": {
                    "found": True,
                    "source_refs": ["official:issuer:2026-07-28"],
                },
                "discovery_status": "prepare_research",
                "formal_decision_eligible": False,
                "research_only": True,
                "no_order_execution": True,
                "observation": {"amount": 500000000, "change_pct": 4.0},
            }
        ],
    }
    packet = capabilities.build_public_market_observation_packet(
        subject="market_desk_discovery", observation=discovery
    )
    archive_path = packet.write_frozen_archive(tmp_path / "archives")
    ledger_path = tmp_path / "research-ledger.json"

    created = capabilities.promote_public_market_desk_discovery_candidate(
        source_archive_path=archive_path,
        candidate_id="public-discovery:600460:2026-07-28",
        ledger_path=ledger_path,
    )
    duplicate = capabilities.promote_public_market_desk_discovery_candidate(
        source_archive_path=archive_path,
        candidate_id="public-discovery:600460:2026-07-28",
        ledger_path=ledger_path,
    )

    assert created["status"] == "promoted_to_monitoring"
    assert created["entry"]["status"] == "monitoring"
    assert created["entry"]["target_type"] == "public_discovery_observation"
    assert created["formal_decision_eligible"] is False
    assert created["entry"]["source_refs"][0]["archive_id"] == packet.archive_id
    assert duplicate["status"] == "already_promoted"
    assert capabilities.get_research_ledger_index(ledger_path=ledger_path)["index"]["entry_count"] == 1


def test_promote_public_discovery_blocks_unmapped_candidate(tmp_path) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "candidates": [
            {
                "candidate_id": "public-discovery:600460:2026-07-28",
                "code": "600460",
                "name": "士兰微",
                "market_subject_mapping_status": "mapping_required",
                "market_subject_context": {"found": False, "source_refs": []},
                "formal_decision_eligible": False,
                "research_only": True,
                "no_order_execution": True,
                "observation": {},
            }
        ],
    }
    archive_path = capabilities.build_public_market_observation_packet(
        subject="market_desk_discovery", observation=discovery
    ).write_frozen_archive(tmp_path / "archives")

    with pytest.raises(ValueError, match="source-referenced market-subject mapping"):
        capabilities.promote_public_market_desk_discovery_candidate(
            source_archive_path=archive_path,
            candidate_id="public-discovery:600460:2026-07-28",
            ledger_path=tmp_path / "research-ledger.json",
        )


def test_discovery_research_queue_requires_timely_review_and_verifies_source(tmp_path) -> None:
    discovery = {
        "schema_version": "market-desk-public-discovery.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "candidates": [
            {
                "candidate_id": "public-discovery:600460:2026-07-28",
                "code": "600460",
                "name": "士兰微",
                "market_subject_mapping_status": "source_mapped",
                "market_subject_context": {
                    "found": True,
                    "source_refs": ["official:issuer:2026-07-28"],
                },
                "formal_decision_eligible": False,
                "research_only": True,
                "no_order_execution": True,
                "observation": {},
            }
        ],
    }
    packet = capabilities.build_public_market_observation_packet(
        subject="market_desk_discovery", observation=discovery
    )
    archive_path = packet.write_frozen_archive(tmp_path / "archives")
    ledger_path = tmp_path / "research-ledger.json"
    promoted = capabilities.promote_public_market_desk_discovery_candidate(
        source_archive_path=archive_path,
        candidate_id="public-discovery:600460:2026-07-28",
        ledger_path=ledger_path,
    )
    created_at = datetime.fromisoformat(promoted["entry"]["created_at"])
    reference_time = (created_at.replace(tzinfo=timezone.utc) if created_at.tzinfo is None else created_at) + timedelta(hours=49)

    queue = capabilities.get_market_desk_discovery_research_queue(
        ledger_path=ledger_path, now=reference_time
    )
    triaged = capabilities.record_market_desk_discovery_triage(
        promoted["entry"]["entry_id"],
        action="continue_research",
        reviewer="market-regime-analyst",
        reason="Reviewed source-backed evidence and retained for further research.",
        evidence_refs=["official:example"],
        reviewed_at=reference_time.isoformat(),
        next_review_at=(reference_time + timedelta(hours=24)).isoformat(),
        ledger_path=ledger_path,
    )
    reviewed_queue = capabilities.get_market_desk_discovery_research_queue(
        ledger_path=ledger_path, now=reference_time
    )

    assert queue["due_count"] == 1
    assert queue["due"][0]["attention"] == "research_review_due"
    assert queue["due"][0]["source_archive_assurance"]["status"] == "pass"
    assert triaged["triage_action"] == "continue_research"
    assert triaged["formal_decision_eligible"] is False
    assert reviewed_queue["due_count"] == 0


@pytest.mark.asyncio
async def test_freeze_public_market_rotation_binds_the_packet_to_a_content_archive(
    tmp_path,
) -> None:
    rotation = {
        "schema_version": "market_rotation.v1",
        "observed_at": "2026-07-28T15:00:00+08:00",
        "rankings": {"industries": [{"name": "电力", "change_pct": 1.2}]},
    }
    with patch(
        "astock.capabilities.build_market_rotation_v1",
        new=AsyncMock(return_value=rotation),
    ):
        result = await capabilities.freeze_public_market_rotation_observation(
            include_concepts=False,
            observation_limit=12,
            archive_directory=tmp_path,
        )

    assert result["source_manifest"]["source"] == "akshare_public"
    assert result["source_archive_path"]
    assert capabilities.verify_frozen_market_data_archive(
        result["source_archive_path"],
        expected_archive_id=result["source_manifest"]["archive_id"],
        expected_source="akshare_public",
    )["status"] == "pass"


@pytest.mark.asyncio
async def test_public_market_desk_observation_records_frozen_rotation_and_never_releases_a_plan(
    tmp_path,
) -> None:
    overview = {
        "schema_version": "market_desk_overview.v1",
        "snapshot": {"observed_at": "2026-07-28T15:00:00+08:00", "data_quality": "snapshot"},
        "regime": {"regime": "selective_risk_on"},
    }
    rotation = {
        "schema_version": "public_market_observation.v1",
        "source_manifest": {"source": "akshare_public", "archive_id": "sha256:abc"},
        "source_archive_path": str(tmp_path / "rotation.json"),
    }
    readiness = {"observation_desk_status": "ready", "formal_paper_desk_status": "blocked"}
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value=overview)),
        patch("astock.capabilities.freeze_public_market_rotation_observation", new=AsyncMock(return_value=rotation)),
        patch("astock.capabilities.assess_market_desk_operational_readiness", return_value=readiness),
        patch("astock.capabilities.verify_frozen_market_data_archive", return_value={"status": "pass"}),
    ):
        result = await capabilities.run_public_market_desk_observation(
            include_concepts=False,
            archive_directory=tmp_path,
            rotation_archive_directory=tmp_path / "rotation",
        )

    assert result["operation"] == "record_observation_only"
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True
    assert result["rotation_archive_assurance"]["status"] == "pass"
    archived = json.loads((tmp_path / f"{result['archive_id'].removeprefix('sha256:')}.json").read_text())
    assert archived["rotation_observation"]["source_archive_assurance"]["status"] == "pass"
    assert (tmp_path / f"{result['archive_id'].removeprefix('sha256:')}.json").exists()


@pytest.mark.asyncio
async def test_scheduled_eod_observation_skips_outside_verified_after_close() -> None:
    overview = {
        "schema_version": "market_desk_overview.v1",
        "snapshot": {
            "observed_at": "2026-07-28T10:00:00+08:00",
            "market_session": {"state": "closed", "calendar_basis": "exchange_calendar"},
        },
        "regime": {"regime": "insufficient_data"},
    }
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value=overview)),
        patch("astock.capabilities.freeze_public_market_rotation_observation", new=AsyncMock()) as freeze,
    ):
        result = await capabilities.run_public_market_desk_eod_observation()

    assert result["status"] == "skipped"
    assert result["reason"] == "verified_exchange_after_close_required"
    assert result["formal_decision_eligible"] is False
    assert result["no_order_execution"] is True
    freeze.assert_not_awaited()


@pytest.mark.asyncio
async def test_scheduled_eod_observation_is_idempotent_for_a_verified_session_date(
    tmp_path,
) -> None:
    overview = {
        "schema_version": "market_desk_overview.v1",
        "snapshot": {
            "observed_at": "2026-07-28T15:10:00+08:00",
            "market_session": {"state": "after_close", "calendar_basis": "exchange_calendar"},
        },
        "regime": {"regime": "defensive_rotation"},
    }
    history = {
        "records": [
            {
                "status": "pass",
                "observed_at": "2026-07-28T15:05:00+08:00",
                "archive_id": "sha256:prior",
                "eod_validation": {"status": "pass"},
            }
        ],
    }
    with (
        patch("astock.capabilities.build_market_desk_overview", new=AsyncMock(return_value=overview)),
        patch("astock.capabilities.list_public_desk_observation_runs", return_value=history),
        patch("astock.capabilities.freeze_public_market_rotation_observation", new=AsyncMock()) as freeze,
    ):
        result = await capabilities.run_public_market_desk_eod_observation(
            archive_directory=tmp_path
        )

    assert result["status"] == "skipped"
    assert result["reason"] == "valid_eod_observation_exists_for_session_date"
    assert result["existing_archive_ids"] == ["sha256:prior"]
    freeze.assert_not_awaited()


@pytest.mark.asyncio
async def test_build_portfolio_risk_inputs_v1_delegates_to_builder() -> None:
    expected = {"schema_version": "portfolio_risk_inputs.v1"}
    factor_context = {"schema_version": "portfolio-factor-risk-context.v1"}
    with patch(
        "astock.capabilities.PortfolioRiskInputBuilder.build",
        new=AsyncMock(return_value=expected),
    ) as build:
        result = await capabilities.build_portfolio_risk_inputs_v1(
            ["600460", "688001"], lookback=90, factor_risk_context=factor_context
        )

    assert result == expected
    build.assert_awaited_once_with(
        ["600460", "688001"], lookback=90, factor_risk_context=factor_context
    )


def test_run_portfolio_backtest_exposes_the_point_in_time_engine() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-07-01", periods=3, freq="B"),
            "open": [10.0, 10.0, 10.0],
            "close": [10.0, 10.0, 10.0],
            "tradable": [True, True, True],
        }
    )
    result = capabilities.run_portfolio_backtest(
        {"600460": frame},
        {"2026-07-01": {"600460": 0.5}},
        universe_references={"2026-07-01": "universe:2026-07-01"},
        trading_calendar=frame["date"].dt.strftime("%Y-%m-%d").tolist(),
    )

    assert result["schema_version"] == "portfolio_backtest.v1"
    assert result["source_assurance"]["status"] == "blocked"


def test_market_overview_cli_emits_json_packet() -> None:
    runner = CliRunner()
    packet = {
        "schema_version": "market_snapshot.v1",
        "observed_at": "2026-07-28T03:30:00+00:00",
        "data_quality": "realtime",
        "indices": [],
        "breadth": {},
        "turnover": {},
        "etfs": [],
        "industry_observations": [],
        "warnings": [],
        "errors": [],
        "provenance": {},
    }
    with patch(
        "astock.cli.capabilities.build_market_snapshot_v1",
        new=AsyncMock(return_value=packet),
    ) as build_snapshot:
        result = runner.invoke(
            cli.app,
            ["market-overview", "--etf", "510300", "--industry", "512480", "--json"],
        )

    assert result.exit_code == 0
    assert '"schema_version": "market_snapshot.v1"' in result.stdout
    build_snapshot.assert_awaited_once_with(
        etf_codes=["510300"], industry_codes=["512480"]
    )


def test_market_data_sources_cli_exposes_eligibility_without_credentials() -> None:
    result = CliRunner().invoke(cli.app, ["market-data-sources", "--json"])

    assert result.exit_code == 0
    assert '"schema_version": "market_data_source_governance.v1"' in result.stdout
    assert '"source_id": "akshare_public"' in result.stdout


def test_market_desk_observe_cli_delegates_to_observation_only_capability(tmp_path) -> None:
    archive = tmp_path / "desk.json"
    packet = {
        "schema_version": "market-desk-public-observation-run.v1",
        "source_archive_path": str(archive),
        "formal_decision_eligible": False,
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.run_public_market_desk_observation",
        new=AsyncMock(return_value=packet),
    ) as observe:
        result = CliRunner().invoke(
            cli.app,
            ["market-desk-observe", "--industries-only", "--json"],
        )

    assert result.exit_code == 0
    assert '"no_order_execution": true' in result.stdout
    assert observe.await_args.kwargs["include_concepts"] is False


def test_market_desk_discover_cli_exposes_research_only_market_queue() -> None:
    packet = {
        "schema_version": "market-desk-public-discovery.v1",
        "formal_decision_eligible": False,
        "no_order_execution": True,
        "screening_counts": {"returned_candidates": 0},
        "candidates": [],
    }
    with patch(
        "astock.cli.capabilities.discover_public_market_desk_opportunities",
        new=AsyncMock(return_value=packet),
    ) as discover:
        result = CliRunner().invoke(
            cli.app,
            [
                "market-desk-discover",
                "--industries-only",
                "--candidate-limit",
                "8",
                "--min-amount",
                "100000000",
                "--min-change-pct",
                "2",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert '"formal_decision_eligible": false' in result.stdout
    assert '"no_order_execution": true' in result.stdout
    assert discover.await_args.kwargs == {
        "include_concepts": False,
        "observation_limit": 20,
        "candidate_limit": 8,
        "min_amount": 100_000_000.0,
        "min_change_pct": 2.0,
    }


def test_market_desk_record_and_promote_discovery_cli_delegate_without_execution(tmp_path) -> None:
    record_packet = {
        "schema_version": "market-desk-public-discovery.v1",
        "source_archive_path": str(tmp_path / "discovery.json"),
        "formal_decision_eligible": False,
        "no_order_execution": True,
    }
    promote_packet = {
        "status": "promoted_to_monitoring",
        "formal_decision_eligible": False,
        "no_order_execution": True,
    }
    source = tmp_path / "source.json"
    source.write_text("{}", encoding="utf-8")
    with (
        patch(
            "astock.cli.capabilities.record_public_market_desk_discovery",
            new=AsyncMock(return_value=record_packet),
        ) as record,
        patch(
            "astock.cli.capabilities.promote_public_market_desk_discovery_candidate",
            return_value=promote_packet,
        ) as promote,
    ):
        recorded = CliRunner().invoke(
            cli.app,
            ["market-desk-record-discovery", "--industries-only", "--json"],
        )
        promoted = CliRunner().invoke(
            cli.app,
            [
                "market-desk-promote-discovery",
                str(source),
                "--candidate-id",
                "public-discovery:600460:2026-07-28",
                "--ledger-path",
                str(tmp_path / "ledger.json"),
                "--json",
            ],
        )

    assert recorded.exit_code == 0
    assert '"no_order_execution": true' in recorded.stdout
    assert record.await_args.kwargs["include_concepts"] is False
    assert promoted.exit_code == 0
    assert '"formal_decision_eligible": false' in promoted.stdout
    assert promote.call_args.kwargs["candidate_id"] == "public-discovery:600460:2026-07-28"


def test_market_desk_discovery_history_cli_delegates_to_integrity_audit(tmp_path) -> None:
    packet = {
        "schema_version": "market-desk-public-discovery-history.v1",
        "run_count": 1,
        "valid_count": 1,
        "duplicate_run_dates": [],
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.get_public_market_desk_discovery_history",
        return_value=packet,
    ) as history:
        result = CliRunner().invoke(
            cli.app,
            ["market-desk-discovery-history", "--archive-directory", str(tmp_path), "--json"],
        )

    assert result.exit_code == 0
    assert '"valid_count": 1' in result.stdout
    history.assert_called_once_with(archive_directory=tmp_path)


def test_market_desk_discovery_research_queue_cli_is_read_only(tmp_path) -> None:
    packet = {
        "schema_version": "market-desk-discovery-research-queue.v1",
        "due_count": 0,
        "due": [],
        "research_only": True,
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.get_market_desk_discovery_research_queue",
        return_value=packet,
    ) as queue:
        result = CliRunner().invoke(
            cli.app,
            ["market-desk-discovery-research-queue", "--ledger-path", str(tmp_path / "ledger.json"), "--json"],
        )

    assert result.exit_code == 0
    assert '"no_order_execution": true' in result.stdout
    queue.assert_called_once_with(ledger_path=tmp_path / "ledger.json", review_sla_hours=48)


def test_market_desk_triage_discovery_cli_cannot_be_an_execution_path(tmp_path) -> None:
    packet = {
        "triage_action": "continue_research",
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.record_market_desk_discovery_triage",
        return_value=packet,
    ) as triage:
        result = CliRunner().invoke(
            cli.app,
            [
                "market-desk-triage-discovery",
                "research-1",
                "--action", "continue_research",
                "--reviewer", "researcher",
                "--reason", "evidence reviewed",
                "--evidence-ref", "official:1",
                "--next-review-at", "2026-07-30T15:00:00+08:00",
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert '"no_order_execution": true' in result.stdout
    assert triage.call_args.kwargs["action"] == "continue_research"
    assert triage.call_args.kwargs["evidence_refs"] == ["official:1"]


def test_market_desk_review_queue_cli_never_changes_a_strategy_plan() -> None:
    packet = {
        "schema_version": "market-desk-review-queue.v1",
        "due_count": 0,
        "due": [],
        "research_only": True,
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.get_market_desk_review_queue",
        return_value=packet,
    ) as queue:
        result = CliRunner().invoke(cli.app, ["market-desk-review-queue", "--json"])

    assert result.exit_code == 0
    assert '"no_order_execution": true' in result.stdout
    queue.assert_called_once_with(ledger_path=None)


def test_market_desk_observation_history_cli_delegates_to_integrity_audit(tmp_path) -> None:
    packet = {
        "schema_version": "market-desk-public-observation-history.v1",
        "run_count": 1,
        "valid_count": 1,
        "invalid_count": 0,
        "duplicate_run_dates": [],
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.get_public_market_desk_observation_history",
        return_value=packet,
    ) as history:
        result = CliRunner().invoke(
            cli.app,
            ["market-desk-observation-history", "--archive-directory", str(tmp_path), "--json"],
        )

    assert result.exit_code == 0
    assert '"valid_count": 1' in result.stdout
    history.assert_called_once_with(archive_directory=tmp_path, exception_directory=None)


def test_market_desk_observation_exception_review_cli_requires_a_bounded_review_packet(tmp_path) -> None:
    packet = {
        "success": True,
        "review_path": str(tmp_path / "review.json"),
        "no_order_execution": True,
    }
    with patch(
        "astock.cli.capabilities.resolve_public_market_desk_observation_duplicate",
        return_value=packet,
    ) as review:
        result = CliRunner().invoke(
            cli.app,
            [
                "market-desk-observation-exception-review",
                "--session-date", "2026-07-28",
                "--archive-id", "sha256:first",
                "--archive-id", "sha256:second",
                "--canonical-archive-id", "sha256:first",
                "--reviewer", "operations-control",
                "--reason", "Controlled duplicate replay.",
                "--evidence-ref", "ops-ticket:fixture",
                "--archive-directory", str(tmp_path / "runs"),
                "--exception-directory", str(tmp_path / "exceptions"),
                "--json",
            ],
        )

    assert result.exit_code == 0
    assert '"no_order_execution": true' in result.stdout
    assert review.call_args.kwargs["archive_ids"] == ["sha256:first", "sha256:second"]


def test_tushare_freeze_cli_delegates_without_exposing_credentials(tmp_path) -> None:
    runner = CliRunner()
    daily_packet = {"source_archive_path": str(tmp_path / "daily.json"), "market_data": {}}
    universe_packet = {"source_archive_path": str(tmp_path / "universe.json"), "members": ["600460.SH"]}
    with patch(
        "astock.cli.capabilities.require_licensed_market_data_mode",
    ) as require_licensed, patch(
        "astock.cli.capabilities.build_tushare_daily_replay_input",
        return_value=daily_packet,
    ) as freeze_daily:
        daily = runner.invoke(
            cli.app,
            [
                "freeze-tushare-daily",
                "600460.SH",
                "--start-date", "2026-07-01",
                "--end-date", "2026-07-03",
                "--archive-directory", str(tmp_path),
                "--json",
            ],
        )
    with patch(
        "astock.cli.capabilities.require_licensed_market_data_mode",
    ) as require_licensed_universe, patch(
        "astock.cli.capabilities.build_tushare_listing_universe_snapshot",
        return_value=universe_packet,
    ) as freeze_universe:
        universe = runner.invoke(
            cli.app,
            [
                "freeze-tushare-universe",
                "--as-of-date", "2026-07-01",
                "--archive-directory", str(tmp_path),
                "--json",
            ],
        )

    assert daily.exit_code == 0
    assert universe.exit_code == 0
    assert str(tmp_path / "daily.json") in daily.stdout
    assert str(tmp_path / "universe.json") in universe.stdout
    freeze_daily.assert_called_once_with(
        ["600460.SH"],
        start_date="2026-07-01",
        end_date="2026-07-03",
        user_id="default",
        archive_directory=tmp_path,
    )
    freeze_universe.assert_called_once_with(
        as_of_date="2026-07-01",
        user_id="default",
        archive_directory=tmp_path,
    )
    require_licensed.assert_called_once_with(user_id="default")
    require_licensed_universe.assert_called_once_with(user_id="default")


def test_tushare_freeze_cli_blocks_public_observation_profiles(tmp_path) -> None:
    runner = CliRunner()
    with patch(
        "astock.cli.capabilities.require_licensed_market_data_mode",
        side_effect=ValueError("Licensed market-data capability is disabled for this profile"),
    ), patch("astock.cli.capabilities.build_tushare_daily_replay_input") as freeze_daily:
        result = runner.invoke(
            cli.app,
            [
                "freeze-tushare-daily",
                "600460.SH",
                "--start-date", "2026-07-01",
                "--end-date", "2026-07-03",
                "--archive-directory", str(tmp_path),
                "--json",
            ],
        )

    assert result.exit_code == 1
    assert "Licensed market-data capability is disabled" in result.stdout
    freeze_daily.assert_not_called()


def test_market_desk_observation_action_cli_never_emits_execution_instruction(tmp_path) -> None:
    candidate = {
        "data": {
            "source": "akshare_public",
            "quality": "realtime",
            "as_of": "2026-07-28T10:00:00+08:00",
        },
        "technical": {
            "entry_condition": "Close holds above the trigger with volume confirmation.",
            "invalidation_condition": "Close falls below the invalidation level.",
        },
        "risk": {"max_loss_pct": 0.02, "position_limit_pct": 0.1},
        "review_at": "2026-07-28T14:50:00+08:00",
    }
    candidate_path = tmp_path / "observation-candidate.json"
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")

    result = CliRunner().invoke(
        cli.app,
        [
            "market-desk-observation-action",
            str(candidate_path),
            "--regime",
            "selective_risk_on",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"action": "conditional_paper_entry"' in result.stdout
    assert '"no_order_execution": true' in result.stdout
    assert '"formal_decision_eligible": false' in result.stdout


def test_market_desk_ic_capability_and_cli_emit_structured_decision(tmp_path) -> None:
    candidate = {
        "targets": ["600460"],
        "universe": {"eligible": True, "liquid": True},
        "data": {"as_of": "2026-07-28T15:00:00+08:00", "source": "tushare_pro", "quality": "realtime", "archive_id": "sha256:ic-packet", "license_attestation": {"authorized": True, "attested_by": "research-data-owner"}},
        "edge": {"thesis": "test", "catalyst": "test", "invalidation": "test"},
        "risk": {"max_loss_pct": 0.01, "position_limit_pct": 0.1},
        "execution": {"entry_condition": "test", "exit_condition": "test", "review_at": "close"},
        "compliance": {
            "research_only_disclosure": True,
            "no_execution_instruction": True,
            "conflicts_disclosed": True,
            "suitability_disclosure": True,
            "restricted": False,
            "mnpi_or_inside_information": False,
            "prohibited_claims": [],
        },
    }
    controls = {
        role: {"status": "pass", "reason": "verified"}
        for role in (
            "data-verifier",
            "risk-analyst",
            "quant-risk-modeler",
            "execution-liquidity-analyst",
            "compliance-officer",
        )
    }
    candidate_path = tmp_path / "candidate.json"
    controls_path = tmp_path / "controls.json"
    candidate_path.write_text(json.dumps(candidate), encoding="utf-8")
    controls_path.write_text(json.dumps(controls), encoding="utf-8")
    restricted_list_path = tmp_path / "restricted-list.json"
    restricted_list_path.write_text(
        json.dumps(
            {
                "schema_version": "market-desk-restricted-list.v1",
                "attestation": {
                    "source_type": "compliance_attestation",
                    "source_ref": "compliance:2026-07-28",
                    "reviewed_by": "compliance-officer",
                    "reviewed_at": "2026-07-28T09:00:00+08:00",
                    "expires_at": "2026-08-28T09:00:00+08:00",
                },
                "entries": [
                    {
                        "target": "000001",
                        "status": "cleared",
                        "source_type": "compliance_attestation",
                        "source_ref": "compliance:2026-07-28",
                        "effective_at": "2026-07-28T09:00:00+08:00",
                        "reviewed_by": "compliance-officer",
                        "reviewed_at": "2026-07-28T09:00:00+08:00",
                        "expires_at": "2026-08-28T09:00:00+08:00",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = CliRunner().invoke(
        cli.app,
        [
            "market-desk-decision",
            str(candidate_path),
            str(controls_path),
            "--candidate-id",
            "600460-short-20260728",
            "--regime",
            "trend_risk_on",
            "--owner",
            "portfolio-manager",
            "--evidence-ref",
            "market_snapshot:2026-07-28T15:00:00+08:00",
            "--model-version",
            "market_regime=market-desk-regime.v1",
            "--restricted-list",
            str(restricted_list_path),
            "--decided-at",
            "2026-07-28T15:05:00+08:00",
            "--json",
        ],
    )

    assert result.exit_code == 0
    assert '"schema_version": "market-desk-ic-decision.v1"' in result.stdout
    assert '"decision": "approve"' in result.stdout
