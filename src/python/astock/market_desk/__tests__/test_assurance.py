"""Independent paper-desk release assurance tests."""

import hashlib
import json
from datetime import datetime, timezone

from astock import capabilities
from astock.market_desk import MarketRegime, decide_investment_committee, verify_paper_desk_release


def _snapshot() -> dict[str, object]:
    return {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "market_session": {"state": "continuous_morning", "calendar_basis": "exchange_calendar"},
        "indices": [{"code": "sh000001", "change_pct": 1.0}],
        "breadth": {"advances": 3_000, "declines": 1_000, "coverage_ratio": 1.0},
        "provenance": {
            "quality_tier": "realtime",
            "components": {"trading_calendar": {"status": "available"}},
        },
    }


def _plan() -> dict[str, object]:
    return {
        "schema_version": "market-desk-strategy-plan.v1",
        "plan_id": "short-600460-20260728",
        "horizon": "short_term",
        "state": "active",
        "target": "600460",
        "thesis": "Paper-plan thesis.",
        "as_of": "2026-07-28T15:00:00+08:00",
        "entry_condition": "Verified trigger.",
        "invalidation_condition": "Risk breach.",
        "review_at": "2026-07-29T15:00:00+08:00",
        "time_stop_at": "2026-08-07T15:00:00+08:00",
        "evidence_refs": ["market_snapshot:2026-07-28T15:00:00+08:00"],
    }


def _candidate() -> dict[str, object]:
    return {
        "targets": ["600460"],
        "restricted_list_snapshot": {"status": "current", "signature_status": "verified", "active_targets": [], "version": "restricted-list-test-v1"},
        "universe": {"eligible": True, "liquid": True},
        "data": {"as_of": "2026-07-28T15:00:00+08:00", "source": "tushare_pro", "quality": "realtime", "archive_id": "sha256:assurance-packet", "license_attestation": {"authorized": True, "attested_by": "research-data-owner"}},
        "edge": {"thesis": "test", "catalyst": "test", "invalidation": "test"},
        "risk": {"max_loss_pct": 0.01, "position_limit_pct": 0.1},
        "execution": {"entry_condition": "test", "exit_condition": "test", "review_at": "close"},
        "compliance": {"research_only_disclosure": True, "no_execution_instruction": True, "conflicts_disclosed": True, "suitability_disclosure": True},
    }


def _bind_candidate_data_archive(tmp_path, candidate: dict[str, object]) -> dict[str, object]:
    raw_records = {"candidate_market_data": {"code": "600460", "trade_date": "20260728"}}
    source = "tushare_pro"
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
            }
        ),
        encoding="utf-8",
    )
    bound = dict(candidate)
    bound["data"] = {**dict(candidate["data"]), "archive_id": archive_id, "source_archive_path": str(archive_path)}
    return bound


def _decision() -> dict[str, object]:
    controls = {
            role: {"status": "pass"}
            for role in (
                "data-verifier",
                "risk-analyst",
                "quant-risk-modeler",
                "execution-liquidity-analyst",
                "compliance-officer",
            )
    }
    return decide_investment_committee(_candidate(), candidate_id="short-600460-20260728", regime=MarketRegime.TREND_RISK_ON, control_assessments={role: {"status": "pass", "reason": "verified"} for role in controls}, decision_owner="portfolio-manager", evidence_refs=["snapshot:test"], model_versions={"market_regime": "market-desk-regime.v1"}).to_dict()


def _rotation(full_ready: bool = True) -> dict[str, object]:
    return {
        "ranking_basis": {
            "history_validation": {"full_cross_section_ready": full_ready}
        }
    }


def _plan_risk_packet(kind: str, blockers: list[str] | None = None) -> dict[str, object]:
    return {
        "schema_version": f"market-desk-plan-{kind}.v1",
        "plan_id": "short-600460-20260728",
        "target": "600460",
        "candidate_risk": _candidate()["risk"],
        "blockers": blockers or [],
    }


def test_assurance_passes_only_when_all_release_packets_are_linked_and_clear(tmp_path) -> None:
    candidate = _bind_candidate_data_archive(tmp_path, _candidate())
    report = verify_paper_desk_release(
        snapshot=_snapshot(),
        rotation=_rotation(),
        candidate=candidate,
        ic_decision=_decision(),
        strategy_plan=_plan(),
        risk_budget=_plan_risk_packet("risk-budget"),
        structural_risk=_plan_risk_packet("structural-risk"),
        restricted_list_health={"status": "current", "signature_status": "verified", "active_targets": [], "version": "restricted-list-test-v1"},
        require_full_rotation=True,
    )

    assert report.verdict == "pass"
    assert report.checks["investment_committee"] == "pass"
    assert report.checks["candidate_data_archive"] == "pass"
    assert report.checks["decision_review"] == "not_applicable"


def test_assurance_rejects_stale_restrictions_or_incomplete_full_rotation() -> None:
    report = capabilities.verify_market_desk_paper_release(
        snapshot=_snapshot(),
        rotation=_rotation(full_ready=False),
        candidate=_candidate(),
        ic_decision=_decision(),
        strategy_plan=_plan(),
        risk_budget=_plan_risk_packet("risk-budget"),
        structural_risk=_plan_risk_packet("structural-risk", ["liquidity missing"]),
        restricted_list_health={"status": "stale", "signature_status": "invalid", "active_targets": [], "version": "restricted-list-test-v1"},
        require_full_rotation=True,
    )

    assert report["verdict"] == "fail"
    assert report["checks"]["rotation"] == "fail"
    assert report["checks"]["restricted_list"] == "fail"
    assert report["checks"]["structural_risk"] == "fail"


def test_assurance_rejects_risk_packets_bound_to_another_plan_or_risk() -> None:
    risk_budget = _plan_risk_packet("risk-budget")
    risk_budget["plan_id"] = "other-plan"
    report = verify_paper_desk_release(
        snapshot=_snapshot(),
        rotation=_rotation(),
        candidate=_candidate(),
        ic_decision=_decision(),
        strategy_plan=_plan(),
        risk_budget=risk_budget,
        structural_risk=_plan_risk_packet("structural-risk"),
        restricted_list_health={"status": "current", "signature_status": "verified", "active_targets": [], "version": "restricted-list-test-v1"},
        require_full_rotation=True,
    )

    assert report.verdict == "fail"
    assert report.checks["risk_budget"] == "fail"


def test_assurance_rejects_declared_candidate_archive_without_verifiable_bytes() -> None:
    report = verify_paper_desk_release(
        snapshot=_snapshot(),
        rotation=_rotation(),
        candidate=_candidate(),
        ic_decision=_decision(),
        strategy_plan=_plan(),
        risk_budget=_plan_risk_packet("risk-budget"),
        structural_risk=_plan_risk_packet("structural-risk"),
        restricted_list_health={"status": "current", "signature_status": "verified", "active_targets": [], "version": "restricted-list-test-v1"},
    )

    assert report.verdict == "fail"
    assert report.checks["candidate_data_archive"] == "fail"
