"""Persistence and IC-binding tests for market-desk strategy plans."""

import hashlib
import json

from datetime import datetime, timezone

import pytest

from astock import capabilities
from astock.market_desk import RestrictedListAttestation, RestrictedListStore


def _write_candidate_data_archive(tmp_path, candidate: dict[str, object]) -> None:
    """Bind a release candidate to reproducible, content-addressed data."""
    source = "tushare_pro"
    raw_records = {
        "strategy_candidate": {"code": "600460", "trade_date": "20260728"}
    }
    digest = hashlib.sha256(
        json.dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": source,
                "raw_source_records": raw_records,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    archive_id = f"sha256:{digest}"
    archive_path = tmp_path / f"{digest}.json"
    archive_path.write_text(
        json.dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": source,
                "archive_id": archive_id,
                "raw_source_records": raw_records,
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    candidate["data"] = {
        **dict(candidate["data"]),
        "archive_id": archive_id,
        "source_archive_path": str(archive_path),
    }


def _plan() -> dict[str, object]:
    return {
        "plan_id": "short-600460-20260728",
        "horizon": "short_term",
        "state": "observation",
        "target": "600460",
        "thesis": "Conditional paper-plan thesis.",
        "as_of": "2026-07-28T15:00:00+08:00",
        "entry_condition": "A verified condition occurs.",
        "invalidation_condition": "The defined risk level breaks.",
        "review_at": "2026-07-29T15:00:00+08:00",
        "time_stop_at": "2026-08-07T15:00:00+08:00",
        "evidence_refs": ["market_snapshot:2026-07-28T15:00:00+08:00"],
    }


def test_strategy_plan_playbook_must_match_horizon(tmp_path) -> None:
    plan = {**_plan(), "playbook_id": "leader_continuation"}

    with pytest.raises(ValueError, match="horizon must match"):
        capabilities.create_market_desk_strategy_plan(
            plan, title="mismatched playbook", ledger_path=tmp_path / "ledger.json"
        )

    ultra_plan = {
        **plan,
        "plan_id": "ultra-600460-20260728",
        "horizon": "ultra_short",
        "time_stop_at": "2026-07-30T15:00:00+08:00",
    }
    created = capabilities.create_market_desk_strategy_plan(
        ultra_plan, title="leader continuation", ledger_path=tmp_path / "ledger.json"
    )

    assert created["entry"]["metadata"]["strategy_plan"]["playbook_id"] == "leader_continuation"


def test_persisted_strategy_plan_requires_ic_record_before_active(tmp_path, monkeypatch) -> None:
    created = capabilities.create_market_desk_strategy_plan(
        _plan(), title="600460 short-term plan", ledger_path=tmp_path / "ledger.json"
    )
    entry_id = created["entry"]["entry_id"]
    watched = capabilities.transition_market_desk_strategy_plan(
        entry_id, next_state="watch", reason="Verification pending.", ledger_path=tmp_path / "ledger.json"
    )
    conditional = capabilities.transition_market_desk_strategy_plan(
        entry_id, next_state="conditional", reason="Prerequisites stated.", ledger_path=tmp_path / "ledger.json"
    )
    assert watched["entry"]["status"] == "monitoring"
    assert conditional["entry"]["status"] == "monitoring"

    with pytest.raises(ValueError, match="IC decision"):
        capabilities.transition_market_desk_strategy_plan(
            entry_id, next_state="active", reason="No decision record.", ledger_path=tmp_path / "ledger.json"
        )

    restricted_list_path = tmp_path / "restricted-list.json"
    store = RestrictedListStore(restricted_list_path)
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY", "test-compliance-key")
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY_ID", "test-compliance-authority")
    store.attest_signed(
        RestrictedListAttestation(
            source_type="compliance-source",
            source_ref="test-clearance",
            reviewed_by="compliance-officer",
            reviewed_at="2026-07-29T15:00:00+08:00",
            expires_at="2099-12-31T15:00:00+08:00",
        ),
        key_id="test-compliance-authority",
        signing_key="test-compliance-key",
    )
    candidate = {
        "targets": ["600460"],
        "universe": {"eligible": True, "liquid": True},
        "data": {"as_of": datetime.now(timezone.utc).isoformat(), "source": "tushare_pro", "quality": "realtime", "archive_id": "sha256:strategy-packet", "license_attestation": {"authorized": True, "attested_by": "research-data-owner"}},
        "edge": {"thesis": "test", "catalyst": "test", "invalidation": "test"},
        "risk": {"max_loss_pct": 0.01, "position_limit_pct": 0.1},
        "execution": {"entry_condition": "test", "exit_condition": "test", "review_at": "close"},
        "compliance": {"research_only_disclosure": True, "no_execution_instruction": True, "conflicts_disclosed": True, "suitability_disclosure": True},
    }
    _write_candidate_data_archive(tmp_path, candidate)
    controls = {role: {"status": "pass", "reason": "verified"} for role in ("data-verifier", "risk-analyst", "quant-risk-modeler", "execution-liquidity-analyst", "compliance-officer")}
    decision = capabilities.decide_market_desk_investment_committee(candidate, candidate_id="short-600460-20260728", regime="trend_risk_on", control_assessments=controls, decision_owner="portfolio-manager", evidence_refs=["market_snapshot:test"], model_versions={"market_regime": "market-desk-regime.v1"}, restricted_list_path=restricted_list_path)
    release_inputs = {
        "snapshot": {
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "market_session": {"state": "after_close", "calendar_basis": "exchange_calendar"},
            "indices": [{"code": "sh000001", "change_pct": 1.0}],
            "breadth": {"advances": 3000, "declines": 1000, "coverage_ratio": 1.0},
            "provenance": {
                "quality_tier": "realtime",
                "components": {"trading_calendar": {"status": "available"}},
            },
        },
        "rotation": {"ranking_basis": {"history_validation": {"full_cross_section_ready": True}}},
        "candidate": candidate,
        "risk_budget": {
            "schema_version": "market-desk-plan-risk-budget.v1",
            "plan_id": "short-600460-20260728",
            "target": "600460",
            "candidate_risk": candidate["risk"],
            "blockers": [],
        },
        "structural_risk": {
            "schema_version": "market-desk-plan-structural-risk.v1",
            "plan_id": "short-600460-20260728",
            "target": "600460",
            "candidate_risk": candidate["risk"],
            "blockers": [],
        },
        "require_full_rotation": True,
    }
    blocked_portfolio_path = tmp_path / "blocked-portfolio.json"
    blocked_portfolio_path.write_text(
        json.dumps(
            {"cash": 90_000, "positions": {"600460": {"code": "600460"}}, "trades": []}
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="paper-portfolio governance"):
        capabilities.transition_market_desk_strategy_plan(
            entry_id,
            next_state="active",
            reason="Attempted release with an ungoverned portfolio.",
            ic_decision=decision,
            release_inputs=release_inputs,
            restricted_list_path=restricted_list_path,
            ledger_path=tmp_path / "ledger.json",
            portfolio_path=blocked_portfolio_path,
        )
    active = capabilities.transition_market_desk_strategy_plan(
        entry_id,
        next_state="active",
        reason="IC record permits the paper plan.",
        ic_decision=decision,
        release_inputs=release_inputs,
        restricted_list_path=restricted_list_path,
        ledger_path=tmp_path / "ledger.json",
        portfolio_path=tmp_path / "clean-portfolio.json",
    )
    assert active["entry"]["status"] == "active"
    assert active["entry"]["observations"][-1]["evidence"]["strategy_plan"]["state"] == "active"
    release_package = active["entry"]["observations"][-1]["evidence"]["release_package"]
    assert release_package["schema_version"] == "market-desk-release-package.v1"
    assert len(release_package["package_hash"]) == 64
    assert set(release_package["content_hashes"]) >= {"snapshot", "rotation", "candidate", "risk_budget", "structural_risk", "portfolio_governance"}


def test_strategy_books_group_horizons_and_flag_due_review_without_mutation(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.json"
    short = capabilities.create_market_desk_strategy_plan(
        _plan(), title="600460 short-term plan", ledger_path=ledger_path
    )
    long_plan = {
        **_plan(),
        "plan_id": "long-600588-20260728",
        "horizon": "long_term",
        "target": "600588",
        "review_at": "2026-07-31T15:00:00+08:00",
        "time_stop_at": None,
    }
    long = capabilities.create_market_desk_strategy_plan(
        long_plan, title="600588 long-term plan", ledger_path=ledger_path
    )

    books = capabilities.get_market_desk_strategy_books(
        ledger_path=ledger_path,
        now=datetime(2026, 8, 1, tzinfo=timezone.utc),
    )

    assert books["schema_version"] == "market-desk-strategy-books.v1"
    assert books["book_counts"] == {"ultra_short": 0, "short_term": 1, "swing": 0, "long_term": 1}
    assert books["books"]["short_term"][0]["attention"] == "review_due"
    assert books["books"]["long_term"][0]["attention"] == "review_due"
    assert books["no_order_execution"] is True
    assert short["entry"]["status"] == "monitoring"
    assert long["entry"]["status"] == "monitoring"

    queue = capabilities.get_market_desk_review_queue(
        ledger_path=ledger_path,
        now=datetime(2026, 8, 1, tzinfo=timezone.utc),
    )
    assert queue["schema_version"] == "market-desk-review-queue.v1"
    assert queue["due_count"] == 2
    assert queue["review_due_count"] == 2
    assert queue["time_stop_due_count"] == 0
    assert queue["no_order_execution"] is True


def test_persisted_strategy_review_records_evidence_and_reschedules(tmp_path) -> None:
    ledger_path = tmp_path / "ledger.json"
    created = capabilities.create_market_desk_strategy_plan(
        _plan(), title="600460 short-term plan", ledger_path=ledger_path
    )
    result = capabilities.record_market_desk_strategy_review(
        created["entry"]["entry_id"],
        reviewer="portfolio-manager",
        reason="No invalidation; retain research observation until next review.",
        evidence_refs=["public-observation:sha256:fixture"],
        observed_at="2026-07-28T16:00:00+08:00",
        next_review_at="2026-07-30T15:00:00+08:00",
        ledger_path=ledger_path,
    )

    observation = result["entry"]["observations"][-1]
    assert observation["observation_type"] == "strategy_lifecycle_review"
    assert observation["evidence"]["strategy_plan"]["review_at"] == "2026-07-30T15:00:00+08:00"
    assert observation["evidence"]["no_order_execution"] is True


def test_operational_readiness_separates_public_observation_from_formal_release(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.delenv("JQDATA_USERNAME", raising=False)
    monkeypatch.delenv("JQDATA_PASSWORD", raising=False)
    monkeypatch.delenv("MARKET_DATA_ATTESTED_BY", raising=False)
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "licensed_eod"},
    )

    readiness = capabilities.assess_market_desk_operational_readiness(
        ledger_path=tmp_path / "ledger.json",
        restricted_list_path=tmp_path / "restricted-list.json",
        observation_archive_directory=tmp_path / "observations",
        portfolio_path=tmp_path / "portfolio.json",
    )

    assert readiness["schema_version"] == "market-desk-operational-readiness.v1"
    assert readiness["observation_desk_status"] == "ready"
    assert readiness["formal_paper_desk_status"] == "blocked"
    assert readiness["checks"]["formal_decision_data"]["status"] == "blocked"
    assert readiness["checks"]["observation_history"]["status"] == "not_ready"
    assert readiness["checks"]["compliance_authority"]["status"] == "blocked"
    assert readiness["checks"]["reproducible_reviews"]["status"] == "not_ready"
    assert readiness["checks"]["quality_feedback"]["status"] == "not_ready"
    assert readiness["checks"]["postmortem_control"]["status"] == "not_ready"
    assert readiness["checks"]["paper_portfolio_governance"]["status"] == "pass"
    assert readiness["no_order_execution"] is True


def test_public_observation_profile_keeps_observation_ready_but_blocks_governed_entry_without_compliance_authority(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "public_observation"},
    )

    readiness = capabilities.assess_market_desk_operational_readiness(
        ledger_path=tmp_path / "ledger.json",
        restricted_list_path=tmp_path / "restricted-list.json",
        observation_archive_directory=tmp_path / "observations",
    )

    assert readiness["market_data_mode"] == "public_observation"
    assert readiness["observation_desk_status"] == "ready"
    assert readiness["public_paper_desk_status"] == "blocked"
    assert readiness["public_paper_entry_status"] == "blocked"
    assert readiness["formal_paper_desk_status"] == "not_enabled"
    assert readiness["checks"]["formal_decision_data"]["status"] == "not_enabled"
    assert readiness["checks"]["compliance_authority"]["status"] == "blocked"


def test_public_observation_profile_allows_governed_paper_entry_only_with_signed_compliance_authority(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "public_observation"},
    )
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY", "test-public-paper-key")
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY_ID", "public-paper-compliance")
    restricted_list_path = tmp_path / "restricted-list.json"
    RestrictedListStore(restricted_list_path).attest_signed(
        RestrictedListAttestation(
            source_type="compliance-source",
            source_ref="test-clearance",
            reviewed_by="compliance-officer",
            reviewed_at="2026-07-29T15:00:00+08:00",
            expires_at="2099-12-31T15:00:00+08:00",
        ),
        key_id="public-paper-compliance",
        signing_key="test-public-paper-key",
    )

    readiness = capabilities.assess_market_desk_operational_readiness(
        ledger_path=tmp_path / "ledger.json",
        restricted_list_path=restricted_list_path,
        observation_archive_directory=tmp_path / "observations",
        portfolio_path=tmp_path / "portfolio.json",
    )

    assert readiness["observation_desk_status"] == "ready"
    assert readiness["public_paper_desk_status"] == "ready"
    assert readiness["public_paper_entry_status"] == "ready"
    assert readiness["formal_paper_desk_status"] == "not_enabled"
    assert readiness["checks"]["compliance_authority"]["status"] == "pass"


def test_operational_readiness_blocks_portfolio_governance_gaps(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.delenv("JQDATA_USERNAME", raising=False)
    monkeypatch.delenv("JQDATA_PASSWORD", raising=False)
    monkeypatch.delenv("MARKET_DATA_ATTESTED_BY", raising=False)
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "licensed_eod"},
    )
    portfolio_path = tmp_path / "portfolio.json"
    portfolio_path.write_text(
        json.dumps(
            {
                "cash": 90_000,
                "positions": {"600460": {"code": "600460", "strategy_entry_id": "missing-plan"}},
                "trades": [],
            }
        ),
        encoding="utf-8",
    )

    readiness = capabilities.assess_market_desk_operational_readiness(
        ledger_path=tmp_path / "ledger.json",
        restricted_list_path=tmp_path / "restricted-list.json",
        observation_archive_directory=tmp_path / "observations",
        portfolio_path=portfolio_path,
    )

    portfolio = readiness["checks"]["paper_portfolio_governance"]
    assert portfolio["status"] == "blocked"
    assert portfolio["invalid_link_count"] == 1
    assert readiness["formal_paper_desk_status"] == "blocked"


def test_operational_readiness_does_not_treat_disclosure_only_source_as_eod_decision_data(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.delenv("JQDATA_USERNAME", raising=False)
    monkeypatch.delenv("JQDATA_PASSWORD", raising=False)
    monkeypatch.setenv("MARKET_DATA_ATTESTED_BY", "research-data-owner")
    monkeypatch.setattr(
        capabilities,
        "load_user_config",
        lambda user_id="default": {"market_data_mode": "licensed_eod"},
    )

    readiness = capabilities.assess_market_desk_operational_readiness(
        ledger_path=tmp_path / "ledger.json",
        restricted_list_path=tmp_path / "restricted-list.json",
        observation_archive_directory=tmp_path / "observations",
    )

    data = readiness["checks"]["formal_decision_data"]
    assert data["status"] == "blocked"
    assert "exchange_disclosures" in data["configured_decision_sources"]
    assert data["configured_eod_sources"] == []


def test_operational_readiness_flags_unanchored_quality_feedback(tmp_path, monkeypatch) -> None:
    monkeypatch.delenv("TUSHARE_TOKEN", raising=False)
    monkeypatch.delenv("JQDATA_USERNAME", raising=False)
    monkeypatch.delenv("JQDATA_PASSWORD", raising=False)
    monkeypatch.delenv("MARKET_DATA_ATTESTED_BY", raising=False)
    ledger_path = tmp_path / "ledger.json"
    created = capabilities.create_research_entry(
        title="Unanchored feedback",
        thesis="Manual feedback must not count as an observed outcome.",
        targets=["600460"],
        ledger_path=ledger_path,
    )
    capabilities.record_research_observation(
        created["entry"]["entry_id"],
        observation_type="quality_feedback",
        note="Legacy manual feedback.",
        evidence={
            "quality_feedback": {
                "entry_id": created["entry"]["entry_id"],
                "evidence_refs": ["review-packet:unlinked"],
            }
        },
        ledger_path=ledger_path,
    )

    readiness = capabilities.assess_market_desk_operational_readiness(
        ledger_path=ledger_path,
        restricted_list_path=tmp_path / "restricted-list.json",
        observation_archive_directory=tmp_path / "observations",
    )

    quality = readiness["checks"]["quality_feedback"]
    assert quality["status"] == "warning"
    assert quality["assessed_entry_count"] == 0
    assert quality["invalid_entry_count"] == 1
