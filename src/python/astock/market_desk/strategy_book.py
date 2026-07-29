"""Deterministic lifecycle contracts for paper-desk strategy books."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .decision import REQUIRED_IC_CONTROL_ROLES


class StrategyHorizon(StrEnum):
    ULTRA_SHORT = "ultra_short"
    SHORT_TERM = "short_term"
    SWING = "swing"
    LONG_TERM = "long_term"


class StrategyState(StrEnum):
    OBSERVATION = "observation"
    WATCH = "watch"
    CONDITIONAL = "conditional"
    ACTIVE = "active"
    REJECTED = "rejected"
    INVALIDATED = "invalidated"
    EXPIRED = "expired"
    CLOSED = "closed"


_ALLOWED_TRANSITIONS: dict[StrategyState, set[StrategyState]] = {
    StrategyState.OBSERVATION: {StrategyState.WATCH, StrategyState.REJECTED},
    StrategyState.WATCH: {StrategyState.CONDITIONAL, StrategyState.REJECTED, StrategyState.EXPIRED},
    StrategyState.CONDITIONAL: {StrategyState.ACTIVE, StrategyState.REJECTED, StrategyState.EXPIRED},
    StrategyState.ACTIVE: {StrategyState.INVALIDATED, StrategyState.EXPIRED, StrategyState.CLOSED},
    StrategyState.REJECTED: set(),
    StrategyState.INVALIDATED: set(),
    StrategyState.EXPIRED: set(),
    StrategyState.CLOSED: set(),
}


@dataclass(frozen=True)
class StrategyPlan:
    """One conditional paper-plan in one of the desk's three books."""

    plan_id: str
    horizon: StrategyHorizon
    state: StrategyState
    target: str
    thesis: str
    as_of: str
    entry_condition: str
    invalidation_condition: str
    review_at: str
    time_stop_at: str | None
    evidence_refs: tuple[str, ...]
    playbook_id: str | None = None
    transition_history: tuple[dict[str, str], ...] = ()
    review_history: tuple[dict[str, Any], ...] = ()

    def __post_init__(self) -> None:
        if not self.plan_id.strip() or not self.target.strip() or not self.thesis.strip():
            raise ValueError("strategy plan requires plan_id, target, and thesis")
        for label, value in (("as_of", self.as_of), ("review_at", self.review_at)):
            if _parse_iso(value) is None:
                raise ValueError(f"strategy plan {label} must be an ISO-8601 timestamp")
        if self.horizon in {StrategyHorizon.ULTRA_SHORT, StrategyHorizon.SHORT_TERM, StrategyHorizon.SWING}:
            if _parse_iso(self.time_stop_at) is None:
                raise ValueError("ultra-short, short-term, and swing plans require an ISO-8601 time_stop_at")
        if not self.entry_condition.strip() or not self.invalidation_condition.strip():
            raise ValueError("strategy plan requires entry and invalidation conditions")
        if not self.evidence_refs:
            raise ValueError("strategy plan requires at least one evidence reference")
        if self.playbook_id is not None and not self.playbook_id.strip():
            raise ValueError("strategy plan playbook_id must be nonempty when provided")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-strategy-plan.v1",
            "plan_id": self.plan_id,
            "horizon": self.horizon.value,
            "state": self.state.value,
            "target": self.target,
            "thesis": self.thesis,
            "as_of": self.as_of,
            "entry_condition": self.entry_condition,
            "invalidation_condition": self.invalidation_condition,
            "review_at": self.review_at,
            "time_stop_at": self.time_stop_at,
            "evidence_refs": list(self.evidence_refs),
            "playbook_id": self.playbook_id,
            "transition_history": list(self.transition_history),
            "review_history": list(self.review_history),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "StrategyPlan":
        history = data.get("transition_history", ())
        return cls(
            plan_id=str(data.get("plan_id") or ""),
            horizon=StrategyHorizon(str(data.get("horizon") or "")),
            state=StrategyState(str(data.get("state") or "")),
            target=str(data.get("target") or ""),
            thesis=str(data.get("thesis") or ""),
            as_of=str(data.get("as_of") or ""),
            entry_condition=str(data.get("entry_condition") or ""),
            invalidation_condition=str(data.get("invalidation_condition") or ""),
            review_at=str(data.get("review_at") or ""),
            time_stop_at=str(data["time_stop_at"]) if data.get("time_stop_at") else None,
            evidence_refs=tuple(str(item) for item in data.get("evidence_refs", ()) if str(item).strip()),
            playbook_id=str(data["playbook_id"]).strip() if data.get("playbook_id") is not None else None,
            transition_history=tuple(dict(item) for item in history if isinstance(item, Mapping)),
            review_history=tuple(
                dict(item)
                for item in data.get("review_history", ())
                if isinstance(item, Mapping)
            ),
        )


def transition_strategy_plan(
    plan: StrategyPlan,
    next_state: StrategyState | str,
    *,
    reason: str,
    observed_at: str | None = None,
    ic_decision: Mapping[str, Any] | None = None,
    release_assurance: Mapping[str, Any] | None = None,
) -> StrategyPlan:
    """Apply a legal, timestamped lifecycle transition to a paper plan."""

    state = StrategyState(next_state)
    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    if _parse_iso(timestamp) is None:
        raise ValueError("observed_at must be an ISO-8601 timestamp")
    if not reason.strip():
        raise ValueError("strategy lifecycle transition requires a reason")
    if state not in _ALLOWED_TRANSITIONS[plan.state]:
        raise ValueError(f"illegal strategy transition: {plan.state.value} -> {state.value}")
    if state == StrategyState.ACTIVE:
        _validate_ic_decision(plan, ic_decision)
        _validate_release_assurance(plan, ic_decision, release_assurance)
    history = (*plan.transition_history, {"from": plan.state.value, "to": state.value, "reason": reason.strip(), "observed_at": timestamp})
    return StrategyPlan(
        plan_id=plan.plan_id,
        horizon=plan.horizon,
        state=state,
        target=plan.target,
        thesis=plan.thesis,
        as_of=plan.as_of,
        entry_condition=plan.entry_condition,
        invalidation_condition=plan.invalidation_condition,
        review_at=plan.review_at,
        time_stop_at=plan.time_stop_at,
        evidence_refs=plan.evidence_refs,
        playbook_id=plan.playbook_id,
        transition_history=history,
        review_history=plan.review_history,
    )


def record_strategy_plan_review(
    plan: StrategyPlan,
    *,
    reviewer: str,
    reason: str,
    evidence_refs: Sequence[str],
    next_review_at: str,
    observed_at: str | None = None,
) -> StrategyPlan:
    """Record an explicit continuation review without changing plan state.

    Continuation is not a trade action. It is permitted only before a
    short/swing time stop and must schedule the next review before that stop.
    Terminal outcomes remain explicit lifecycle transitions.
    """
    if plan.state not in {
        StrategyState.OBSERVATION,
        StrategyState.WATCH,
        StrategyState.CONDITIONAL,
        StrategyState.ACTIVE,
    }:
        raise ValueError("only nonterminal strategy plans can receive a continuation review")
    timestamp_text = observed_at or datetime.now(timezone.utc).isoformat()
    timestamp = _parse_iso(timestamp_text)
    next_review = _parse_iso(next_review_at)
    if timestamp is None or next_review is None:
        raise ValueError("strategy review timestamps must be ISO-8601")
    if not reviewer.strip() or not reason.strip():
        raise ValueError("strategy continuation review requires reviewer and reason")
    normalized_refs = tuple(str(reference).strip() for reference in evidence_refs if str(reference).strip())
    if not normalized_refs:
        raise ValueError("strategy continuation review requires evidence references")
    if next_review <= timestamp:
        raise ValueError("strategy continuation next_review_at must be later than observed_at")
    time_stop = _parse_iso(plan.time_stop_at)
    if time_stop is not None:
        if timestamp >= time_stop:
            raise ValueError("strategy continuation is forbidden once time_stop_at is due; expire, close, or invalidate the plan")
        if next_review >= time_stop:
            raise ValueError("strategy continuation next_review_at must precede time_stop_at")
    review = {
        "action": "continue",
        "reviewer": reviewer.strip(),
        "reason": reason.strip(),
        "evidence_refs": list(normalized_refs),
        "observed_at": timestamp_text,
        "previous_review_at": plan.review_at,
        "next_review_at": next_review_at,
    }
    return StrategyPlan(
        plan_id=plan.plan_id,
        horizon=plan.horizon,
        state=plan.state,
        target=plan.target,
        thesis=plan.thesis,
        as_of=plan.as_of,
        entry_condition=plan.entry_condition,
        invalidation_condition=plan.invalidation_condition,
        review_at=next_review_at,
        time_stop_at=plan.time_stop_at,
        evidence_refs=plan.evidence_refs,
        playbook_id=plan.playbook_id,
        transition_history=plan.transition_history,
        review_history=(*plan.review_history, review),
    )


def _parse_iso(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _validate_ic_decision(
    plan: StrategyPlan, decision: Mapping[str, Any] | None
) -> None:
    if not isinstance(decision, Mapping):
        raise ValueError("active strategy plans require an IC decision record")
    if decision.get("schema_version") != "market-desk-ic-decision.v1":
        raise ValueError("active strategy plans require market-desk-ic-decision.v1")
    if str(decision.get("candidate_id") or "") != plan.plan_id:
        raise ValueError("IC decision candidate_id must match strategy plan_id")
    if str(decision.get("decision") or "") != "approve":
        raise ValueError("active strategy plans require an approved IC decision")
    targets = decision.get("candidate_targets")
    if not isinstance(targets, Sequence) or isinstance(targets, str) or plan.target not in {
        str(item).strip() for item in targets if str(item).strip()
    }:
        raise ValueError("active strategy plans require an IC decision bound to the strategy target")
    if not str(decision.get("decision_owner") or "").strip():
        raise ValueError("active strategy plans require an IC decision owner")
    if _parse_iso(str(decision.get("decided_at") or "")) is None:
        raise ValueError("active strategy plans require an IC decision timestamp")
    evidence_refs = decision.get("evidence_refs")
    if not isinstance(evidence_refs, Sequence) or isinstance(evidence_refs, str) or not any(
        str(reference).strip() for reference in evidence_refs
    ):
        raise ValueError("active strategy plans require IC evidence references")
    controls = decision.get("control_assessments")
    if not isinstance(controls, Mapping):
        raise ValueError("active strategy plans require all IC control assessments")
    for role in REQUIRED_IC_CONTROL_ROLES:
        assessment = controls.get(role)
        if not isinstance(assessment, Mapping) or str(assessment.get("status") or "") != "pass":
            raise ValueError(f"active strategy plans require a passing IC assessment from {role}")
    model_versions = decision.get("model_versions")
    if not isinstance(model_versions, Mapping) or not any(
        str(name).strip() and str(version).strip()
        for name, version in model_versions.items()
    ):
        raise ValueError("active strategy plans require explicit IC model versions")


def _validate_release_assurance(
    plan: StrategyPlan,
    decision: Mapping[str, Any] | None,
    assurance: Mapping[str, Any] | None,
) -> None:
    if not isinstance(assurance, Mapping):
        raise ValueError("active strategy plans require a release assurance report")
    if assurance.get("schema_version") != "market-desk-paper-assurance.v1":
        raise ValueError("active strategy plans require market-desk-paper-assurance.v1")
    if assurance.get("verdict") != "pass":
        raise ValueError("active strategy plans require a passing release assurance report")
    if str(assurance.get("plan_id") or "") != plan.plan_id or str(assurance.get("target") or "") != plan.target:
        raise ValueError("release assurance must bind the active strategy plan and target")
    if str(assurance.get("ic_candidate_id") or "") != str((decision or {}).get("candidate_id") or ""):
        raise ValueError("release assurance must bind the active IC decision")
