"""Independent release review for a paper market-desk decision package."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ..market_data import verify_frozen_market_archive
from .decision import REQUIRED_IC_CONTROL_ROLES, DeskDecision, assess_market_regime, evaluate_candidate_gate
from .strategy_book import StrategyPlan, StrategyState


@dataclass(frozen=True)
class PaperDeskAssuranceReport:
    """Independent package-level release verdict for research-only paper plans."""

    verdict: str
    checks: dict[str, str]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    plan_id: str | None = None
    target: str | None = None
    ic_candidate_id: str | None = None
    restricted_list_version: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-paper-assurance.v1",
            "verdict": self.verdict,
            "checks": self.checks,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "plan_id": self.plan_id,
            "target": self.target,
            "ic_candidate_id": self.ic_candidate_id,
            "restricted_list_version": self.restricted_list_version,
        }


def verify_paper_desk_release(
    *,
    snapshot: Mapping[str, Any],
    rotation: Mapping[str, Any],
    candidate: Mapping[str, Any],
    ic_decision: Mapping[str, Any],
    strategy_plan: Mapping[str, Any],
    risk_budget: Mapping[str, Any],
    structural_risk: Mapping[str, Any],
    restricted_list_health: Mapping[str, Any],
    require_full_rotation: bool = False,
    decision_review: Mapping[str, Any] | None = None,
) -> PaperDeskAssuranceReport:
    """Verify cross-packet identity, currency, and blocking controls.

    This verifier consumes completed packets; it does not make, upgrade, or
    amend an investment decision. A PASS only means that the paper-desk package
    is internally complete under these contracts, not that its thesis is true.
    """
    checks: dict[str, str] = {}
    blockers: list[str] = []
    warnings: list[str] = []

    regime = assess_market_regime(snapshot)
    if regime.regime.value == "insufficient_data":
        checks["market_snapshot"] = "fail"
        blockers.append("Market snapshot is insufficient, stale, or outside a verified session.")
    else:
        checks["market_snapshot"] = "pass"

    history = rotation.get("ranking_basis", {}).get("history_validation") if isinstance(rotation.get("ranking_basis"), Mapping) else None
    if not isinstance(history, Mapping):
        checks["rotation"] = "fail"
        blockers.append("Rotation packet lacks history-validation coverage.")
    elif require_full_rotation and not bool(history.get("full_cross_section_ready")):
        checks["rotation"] = "fail"
        blockers.append("Release requires full-universe multi-horizon rotation coverage, which is not ready.")
    else:
        checks["rotation"] = "pass"
        if not bool(history.get("full_cross_section_ready")):
            warnings.append("Rotation history is selected or partial; it cannot support a full-universe claim.")

    if (
        str(restricted_list_health.get("status") or "") != "current"
        or str(restricted_list_health.get("signature_status") or "") != "verified"
    ):
        checks["restricted_list"] = "fail"
        blockers.append("Restricted-list authority is missing, invalid, stale, unattested, or lacks a verified compliance signature.")
    else:
        checks["restricted_list"] = "pass"

    try:
        plan = StrategyPlan.from_dict(strategy_plan)
    except (TypeError, ValueError) as error:
        checks["strategy_plan"] = "fail"
        blockers.append(f"Strategy-plan packet is invalid: {error}")
        plan = None
    else:
        if plan.state != StrategyState.ACTIVE:
            checks["strategy_plan"] = "fail"
            blockers.append("Release review requires an active strategy plan.")
        else:
            checks["strategy_plan"] = "pass"

    if plan is not None and plan.target in {
        str(item).strip() for item in restricted_list_health.get("active_targets", ()) if str(item).strip()
    }:
        checks["restricted_target"] = "fail"
        blockers.append("Strategy-plan target is currently restricted.")
    else:
        checks["restricted_target"] = "pass"

    controls = ic_decision.get("control_assessments")
    control_ok = isinstance(controls, Mapping) and all(
        isinstance(controls.get(role), Mapping)
        and str(controls[role].get("status") or "") == "pass"
        for role in REQUIRED_IC_CONTROL_ROLES
    )
    decision_ok = (
        str(ic_decision.get("schema_version") or "") == "market-desk-ic-decision.v1"
        and str(ic_decision.get("decision") or "") == "approve"
        and isinstance(ic_decision.get("model_versions"), Mapping)
        and bool(ic_decision.get("model_versions"))
        and plan is not None
        and str(ic_decision.get("candidate_id") or "") == plan.plan_id
        and plan.target in {
            str(item).strip() for item in ic_decision.get("candidate_targets", ()) if str(item).strip()
        }
        and isinstance(ic_decision.get("restricted_list_snapshot"), Mapping)
        and str(ic_decision["restricted_list_snapshot"].get("status") or "") == "current"
        and str(ic_decision["restricted_list_snapshot"].get("signature_status") or "") == "verified"
        and str(ic_decision["restricted_list_snapshot"].get("version") or "")
        == str(restricted_list_health.get("version") or "")
        and control_ok
    )
    if decision_ok:
        checks["investment_committee"] = "pass"
    else:
        checks["investment_committee"] = "fail"
        blockers.append("IC decision is missing, unlinked, vetoed, or lacks required controls/model versions.")

    recomputed_gate = evaluate_candidate_gate(
        candidate,
        regime=str(ic_decision.get("regime") or "insufficient_data"),
        control_assessments=controls if isinstance(controls, Mapping) else {},
        restricted_targets=tuple(str(item) for item in restricted_list_health.get("active_targets", ()) if str(item).strip()),
    )
    candidate_snapshot = candidate.get("restricted_list_snapshot")
    candidate_gate_ok = (
        recomputed_gate.decision == DeskDecision.APPROVE
        and isinstance(candidate_snapshot, Mapping)
        and str(candidate_snapshot.get("status") or "") == "current"
        and str(candidate_snapshot.get("signature_status") or "") == "verified"
        and str(candidate_snapshot.get("version") or "") == str(restricted_list_health.get("version") or "")
        and plan is not None
        and plan.target in {str(item).strip() for item in candidate.get("targets", ()) if str(item).strip()}
        and dict(ic_decision.get("candidate_gate") or {}) == recomputed_gate.to_dict()
    )
    checks["candidate_gate_recheck"] = "pass" if candidate_gate_ok else "fail"
    if not candidate_gate_ok:
        blockers.append("Candidate gate cannot be independently recomputed from the release package.")

    candidate_data = candidate.get("data")
    if not isinstance(candidate_data, Mapping):
        checks["candidate_data_archive"] = "fail"
        blockers.append("Candidate lacks a source-labelled data packet and frozen archive reference.")
    else:
        archive_assurance = verify_frozen_market_archive(
            candidate_data.get("source_archive_path"),
            expected_archive_id=str(candidate_data.get("archive_id") or "") or None,
            expected_source=str(candidate_data.get("source") or "") or None,
        )
        checks["candidate_data_archive"] = (
            "pass" if archive_assurance.get("status") == "pass" else "fail"
        )
        if archive_assurance.get("status") != "pass":
            blockers.append(
                "Candidate data archive is missing, unreadable, or does not match its declared source and hash."
            )

    for label, packet, expected_schema in (
        ("risk_budget", risk_budget, "market-desk-plan-risk-budget.v1"),
        ("structural_risk", structural_risk, "market-desk-plan-structural-risk.v1"),
    ):
        reported = packet.get("blockers")
        identity_matches = (
            plan is not None
            and str(packet.get("schema_version") or "") == expected_schema
            and str(packet.get("plan_id") or "") == plan.plan_id
            and str(packet.get("target") or "") == plan.target
            and dict(packet.get("candidate_risk") or {})
            == dict(candidate.get("risk") or {})
        )
        if not isinstance(reported, list) or not identity_matches:
            checks[label] = "fail"
            blockers.append(
                f"{label} packet lacks an auditable blockers list or is not bound to this plan, target, and candidate risk."
            )
        elif reported:
            checks[label] = "fail"
            blockers.append(f"{label} retains blocking findings: {reported[0]}")
        else:
            checks[label] = "pass"

    if decision_review is not None:
        review_ok = (
            str(decision_review.get("schema_version") or "")
            == "market-desk-paper-decision-review.v1"
            and str(decision_review.get("evidence_status") or "") == "pass"
            and plan is not None
            and str(decision_review.get("plan_id") or "") == plan.plan_id
            and dict(decision_review.get("model_versions") or {})
            == dict(ic_decision.get("model_versions") or {})
        )
        checks["decision_review"] = "pass" if review_ok else "fail"
        if not review_ok:
            blockers.append("Decision-review packet lacks frozen return evidence or does not match the plan and IC model versions.")
    else:
        checks["decision_review"] = "not_applicable"
        warnings.append("No post-outcome decision review is available for this active plan.")

    return PaperDeskAssuranceReport(
        verdict="pass" if not blockers else "fail",
        checks=checks,
        blockers=tuple(blockers),
        warnings=tuple(warnings),
        plan_id=plan.plan_id if plan is not None else None,
        target=plan.target if plan is not None else None,
        ic_candidate_id=str(ic_decision.get("candidate_id") or "") or None,
        restricted_list_version=str(restricted_list_health.get("version") or "") or None,
    )
