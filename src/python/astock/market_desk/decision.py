"""Market-state and candidate-gate contracts for paper trading decisions.

This module deliberately converts verified market observations into a bounded
research decision packet.  It does not send orders or claim that a regime is a
forecast.  A candidate remains non-investable unless its data, edge, risk, and
execution gates are all explicit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any, Mapping, Sequence

from ..data_provenance import is_auditable_decision_data_reference
from .compliance import ComplianceStatus, assess_candidate_compliance


class MarketRegime(StrEnum):
    """Market states used to control which research sleeves may be opened."""

    INSUFFICIENT_DATA = "insufficient_data"
    RISK_OFF = "risk_off"
    DEFENSIVE_ROTATION = "defensive_rotation"
    SELECTIVE_RISK_ON = "selective_risk_on"
    TREND_RISK_ON = "trend_risk_on"


class DeskDecision(StrEnum):
    """Only decisions that may leave the investment-committee gate."""

    APPROVE = "approve"
    CONDITIONAL = "conditional"
    WATCH = "watch"
    REJECT = "reject"


class RoleGateStatus(StrEnum):
    """Authoritative approval state returned by an IC control function."""

    PASS = "pass"
    CONDITIONAL = "conditional"
    VETO = "veto"


REQUIRED_IC_CONTROL_ROLES = (
    "data-verifier",
    "risk-analyst",
    "quant-risk-modeler",
    "execution-liquidity-analyst",
    "compliance-officer",
)
MIN_BREADTH_COVERAGE = 0.98
MAX_CONTINUOUS_SNAPSHOT_AGE = timedelta(minutes=15)
MAX_END_OF_DAY_SNAPSHOT_AGE = timedelta(hours=4)


@dataclass(frozen=True)
class MarketRegimeAssessment:
    """A transparent, data-quality-aware market-state result."""

    regime: MarketRegime
    allowed_horizons: tuple[str, ...]
    evidence: tuple[str, ...]
    warnings: tuple[str, ...]
    data_quality: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-regime.v1",
            "regime": self.regime.value,
            "allowed_horizons": list(self.allowed_horizons),
            "evidence": list(self.evidence),
            "warnings": list(self.warnings),
            "data_quality": self.data_quality,
        }


@dataclass(frozen=True)
class CandidateGateResult:
    """Result of the five mandatory market-desk candidate gates."""

    decision: DeskDecision
    passed_gates: tuple[str, ...]
    failed_gates: tuple[str, ...]
    control_statuses: dict[str, str]
    control_blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-candidate-gate.v1",
            "decision": self.decision.value,
            "passed_gates": list(self.passed_gates),
            "failed_gates": list(self.failed_gates),
            "control_statuses": self.control_statuses,
            "control_blockers": list(self.control_blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class InvestmentCommitteeDecision:
    """Immutable, evidence-addressable result of the paper-desk IC gate.

    A decision record is deliberately separate from a free-form role response:
    every required control role must report a valid state, and a VETO cannot be
    overridden by a portfolio-manager narrative.
    """

    candidate_id: str
    candidate_targets: tuple[str, ...]
    restricted_list_snapshot: dict[str, Any]
    decision_owner: str
    decided_at: str
    regime: MarketRegime
    decision: DeskDecision
    candidate_gate: CandidateGateResult
    control_assessments: dict[str, dict[str, Any]]
    model_versions: dict[str, str]
    evidence_refs: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-ic-decision.v1",
            "candidate_id": self.candidate_id,
            "candidate_targets": list(self.candidate_targets),
            "restricted_list_snapshot": self.restricted_list_snapshot,
            "decision_owner": self.decision_owner,
            "decided_at": self.decided_at,
            "regime": self.regime.value,
            "decision": self.decision.value,
            "candidate_gate": self.candidate_gate.to_dict(),
            "control_assessments": self.control_assessments,
            "model_versions": self.model_versions,
            "evidence_refs": list(self.evidence_refs),
            "blockers": list(self.blockers),
        }


def assess_market_regime(
    snapshot: Mapping[str, Any], *, now: datetime | None = None
) -> MarketRegimeAssessment:
    """Classify a timestamped broad-market snapshot without forecasting it.

    Required inputs are one or more index changes and breadth counts.  The
    thresholds are intentionally conservative, make no use of unverified fund
    flow, and are a *risk-permission* state rather than a buy/sell signal.
    """

    warnings = _string_items(snapshot.get("warnings"))
    quality = _quality_label(snapshot)
    freshness_issue, degraded = _snapshot_quality_state(snapshot, now=now)
    if freshness_issue:
        return MarketRegimeAssessment(
            regime=MarketRegime.INSUFFICIENT_DATA,
            allowed_horizons=(),
            evidence=(),
            warnings=tuple(warnings + [freshness_issue]),
            data_quality=quality,
        )
    indices = _index_changes(snapshot.get("indices"))
    breadth = snapshot.get("breadth")
    if not indices or not isinstance(breadth, Mapping):
        return MarketRegimeAssessment(
            regime=MarketRegime.INSUFFICIENT_DATA,
            allowed_horizons=(),
            evidence=(),
            warnings=tuple(
                warnings
                + ["Missing timestamped index changes or market breadth; regime is blocked."]
            ),
            data_quality=quality,
        )

    advances = _as_nonnegative_int(breadth.get("advances", breadth.get("advancers")))
    declines = _as_nonnegative_int(breadth.get("declines", breadth.get("decliners")))
    if advances + declines == 0:
        return MarketRegimeAssessment(
            regime=MarketRegime.INSUFFICIENT_DATA,
            allowed_horizons=(),
            evidence=(),
            warnings=tuple(warnings + ["Breadth has no advance/decline observations."]),
            data_quality=quality,
        )

    advance_ratio = advances / (advances + declines)
    limit_up = _as_nonnegative_int(breadth.get("limit_up"))
    limit_down = _as_nonnegative_int(breadth.get("limit_down"))
    benchmark_change = _benchmark_change(indices)
    growth_change = _growth_change(indices)
    evidence = [
        f"advance_ratio={advance_ratio:.1%}",
        f"limit_up={limit_up}",
        f"limit_down={limit_down}",
        f"benchmark_change={benchmark_change:+.2f}%",
    ]
    if growth_change is not None:
        evidence.append(f"growth_index_change={growth_change:+.2f}%")

    severe_growth_selloff = growth_change is not None and growth_change <= -3.0
    broad_damage = advance_ratio < 0.40 or limit_down > max(limit_up, 20)
    if benchmark_change <= -1.5 and (broad_damage or severe_growth_selloff):
        return MarketRegimeAssessment(
            regime=MarketRegime.RISK_OFF,
            allowed_horizons=("risk_management",),
            evidence=tuple(evidence),
            warnings=tuple(warnings + ["New short-term risk is blocked until the next validated snapshot."]),
            data_quality=quality,
        )

    if degraded:
        return MarketRegimeAssessment(
            regime=MarketRegime.DEFENSIVE_ROTATION,
            allowed_horizons=("watch", "conditional"),
            evidence=tuple(evidence),
            warnings=tuple(
                warnings
                + [
                    "Snapshot quality, market session, or coverage is degraded; new risk-on approval is blocked."
                ]
            ),
            data_quality=quality,
        )

    defensive_strength = _positive_defensive_observation(snapshot.get("etfs"))
    if benchmark_change <= 0 and advance_ratio < 0.55 and defensive_strength:
        return MarketRegimeAssessment(
            regime=MarketRegime.DEFENSIVE_ROTATION,
            allowed_horizons=("watch", "conditional"),
            evidence=tuple(evidence + ["defensive_relative_strength=true"]),
            warnings=tuple(warnings + ["Defensive relative strength is not a trend confirmation."]),
            data_quality=quality,
        )

    index_changes = list(indices.values())
    if advance_ratio >= 0.60 and all(change > 0 for change in index_changes):
        return MarketRegimeAssessment(
            regime=MarketRegime.TREND_RISK_ON,
            allowed_horizons=("ultra_short", "short_term", "swing", "long_term"),
            evidence=tuple(evidence),
            warnings=tuple(warnings),
            data_quality=quality,
        )
    if advance_ratio >= 0.52 and benchmark_change >= 0:
        return MarketRegimeAssessment(
            regime=MarketRegime.SELECTIVE_RISK_ON,
            allowed_horizons=("ultra_short", "short_term", "swing", "watch"),
            evidence=tuple(evidence),
            warnings=tuple(warnings + ["Risk-on is selective; candidate gates still apply."]),
            data_quality=quality,
        )

    return MarketRegimeAssessment(
        regime=MarketRegime.DEFENSIVE_ROTATION,
        allowed_horizons=("watch", "conditional"),
        evidence=tuple(evidence),
        warnings=tuple(warnings + ["Breadth does not support broad risk expansion."]),
        data_quality=quality,
    )


def evaluate_candidate_gate(
    candidate: Mapping[str, Any],
    *,
    regime: MarketRegime | str,
    control_assessments: Mapping[str, Any] | None = None,
    restricted_targets: Sequence[str] = (),
) -> CandidateGateResult:
    """Apply mandatory universe, data, edge, risk, and execution gates.

    Any missing hard gate or required control assessment blocks approval. In a
    risk-off regime, a fully formed candidate is retained only as a watch item
    because market permission is absent.
    """

    market_regime = MarketRegime(regime)
    passed: list[str] = []
    failed: list[str] = []
    compliance_assessment = assess_candidate_compliance(
        candidate, restricted_targets=restricted_targets
    )
    gates = {
        "universe": _valid_universe(candidate.get("universe")) and bool(_candidate_targets(candidate)),
        "data": _valid_data(candidate.get("data")),
        "edge": _valid_edge(candidate.get("edge")),
        "risk": _valid_risk(candidate.get("risk")),
        "execution": _valid_execution(candidate.get("execution")),
        "compliance": compliance_assessment.status == ComplianceStatus.PASS,
    }
    for name, valid in gates.items():
        (passed if valid else failed).append(name)

    parsed_controls, control_blockers, has_veto, has_conditional = _parse_controls(
        control_assessments
    )

    if compliance_assessment.status == ComplianceStatus.VETO:
        return CandidateGateResult(
            decision=DeskDecision.REJECT,
            passed_gates=tuple(passed),
            failed_gates=tuple(failed),
            control_statuses=parsed_controls,
            control_blockers=tuple(compliance_assessment.findings),
            warnings=("Internal compliance control issued a binding VETO.",),
        )
    if failed:
        return CandidateGateResult(
            decision=DeskDecision.WATCH,
            passed_gates=tuple(passed),
            failed_gates=tuple(failed),
            control_statuses=parsed_controls,
            control_blockers=tuple(control_blockers),
            warnings=("Candidate cannot enter the investment committee until every mandatory gate is explicit.",),
        )
    if has_veto:
        return CandidateGateResult(
            decision=DeskDecision.REJECT,
            passed_gates=tuple(passed),
            failed_gates=(),
            control_statuses=parsed_controls,
            control_blockers=tuple(control_blockers),
            warnings=("A required investment-committee control role issued a binding VETO.",),
        )
    if control_blockers:
        return CandidateGateResult(
            decision=DeskDecision.WATCH,
            passed_gates=tuple(passed),
            failed_gates=(),
            control_statuses=parsed_controls,
            control_blockers=tuple(control_blockers),
            warnings=("Candidate is not eligible until every required control role supplies an auditable assessment.",),
        )
    if market_regime in {MarketRegime.INSUFFICIENT_DATA, MarketRegime.RISK_OFF}:
        return CandidateGateResult(
            decision=DeskDecision.WATCH,
            passed_gates=tuple(passed),
            failed_gates=(),
            control_statuses=parsed_controls,
            control_blockers=(),
            warnings=("Market regime does not permit new risk despite a complete candidate packet.",),
        )
    if market_regime == MarketRegime.DEFENSIVE_ROTATION or has_conditional:
        return CandidateGateResult(
            decision=DeskDecision.CONDITIONAL,
            passed_gates=tuple(passed),
            failed_gates=(),
            control_statuses=parsed_controls,
            control_blockers=(),
            warnings=("Only staged, manually reviewed paper-plan exposure is permitted until all conditions clear.",),
        )
    return CandidateGateResult(
        decision=DeskDecision.APPROVE,
        passed_gates=tuple(passed),
        failed_gates=(),
        control_statuses=parsed_controls,
        control_blockers=(),
        warnings=(),
    )


def decide_investment_committee(
    candidate: Mapping[str, Any],
    *,
    candidate_id: str,
    regime: MarketRegime | str,
    control_assessments: Mapping[str, Any],
    decision_owner: str,
    evidence_refs: Sequence[str] = (),
    model_versions: Mapping[str, Any] | None = None,
    decided_at: str | None = None,
    restricted_targets: Sequence[str] = (),
) -> InvestmentCommitteeDecision:
    """Create the sole structured IC decision record for a paper plan.

    The caller must persist this exact packet with its source records; a
    narrative portfolio recommendation is not an IC decision record.
    """

    normalized_candidate_id = str(candidate_id).strip()
    normalized_owner = str(decision_owner).strip()
    normalized_evidence_refs = tuple(
        reference for reference in (str(item).strip() for item in evidence_refs) if reference
    )
    if not normalized_candidate_id:
        raise ValueError("candidate_id is required for an investment-committee decision")
    if not normalized_owner:
        raise ValueError("decision_owner is required for an investment-committee decision")
    if not normalized_evidence_refs:
        raise ValueError("at least one evidence reference is required for an investment-committee decision")
    normalized_model_versions = _normalize_model_versions(model_versions)
    if not normalized_model_versions:
        raise ValueError("at least one named model version is required for an investment-committee decision")
    timestamp = decided_at or datetime.now(timezone.utc).isoformat()
    if _parse_timestamp(timestamp) is None:
        raise ValueError("decided_at must be an ISO-8601 timestamp")
    candidate_targets = _candidate_targets(candidate)

    gate = evaluate_candidate_gate(
        candidate,
        regime=regime,
        control_assessments=control_assessments,
        restricted_targets=restricted_targets,
    )
    normalized_assessments = _normalized_assessments(control_assessments)
    blockers = tuple([*gate.failed_gates, *gate.control_blockers])
    return InvestmentCommitteeDecision(
        candidate_id=normalized_candidate_id,
        candidate_targets=candidate_targets,
        restricted_list_snapshot=(
            dict(candidate["restricted_list_snapshot"])
            if isinstance(candidate.get("restricted_list_snapshot"), Mapping)
            else {}
        ),
        decision_owner=normalized_owner,
        decided_at=timestamp,
        regime=MarketRegime(regime),
        decision=gate.decision,
        candidate_gate=gate,
        control_assessments=normalized_assessments,
        model_versions=normalized_model_versions,
        evidence_refs=normalized_evidence_refs,
        blockers=blockers,
    )


def _index_changes(value: Any) -> dict[str, float]:
    rows: Sequence[Any] = value if isinstance(value, Sequence) and not isinstance(value, str) else ()
    changes: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        change = _as_float(row.get("change_pct", row.get("change_percent")))
        key = str(row.get("code") or row.get("name") or "").strip()
        if key and change is not None:
            changes[key] = change
    return changes


def _benchmark_change(indices: Mapping[str, float]) -> float:
    for key in ("sh000001", "000001", "上证指数", "000300", "hs300", "沪深300"):
        if key in indices:
            return indices[key]
    return sum(indices.values()) / len(indices)


def _growth_change(indices: Mapping[str, float]) -> float | None:
    values = [
        change
        for key, change in indices.items()
        if key in {"sz399006", "399006", "创业板指", "sh000688", "000688", "科创50"}
    ]
    return min(values) if values else None


def _positive_defensive_observation(value: Any) -> bool:
    rows: Sequence[Any] = value if isinstance(value, Sequence) and not isinstance(value, str) else ()
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        labels = " ".join(str(row.get(name) or "") for name in ("name", "theme", "sector")).lower()
        if any(word in labels for word in ("power", "electric", "utility", "bank", "dividend", "电力", "银行", "红利")):
            change = _as_float(row.get("change_pct", row.get("change_percent")))
            if change is not None and change >= 0:
                return True
    return False


def _valid_universe(value: Any) -> bool:
    return isinstance(value, Mapping) and bool(value.get("eligible")) and bool(value.get("liquid"))


def _candidate_targets(candidate: Mapping[str, Any]) -> tuple[str, ...]:
    raw_targets = candidate.get("targets", ())
    if isinstance(raw_targets, str):
        raw_targets = (raw_targets,)
    if not isinstance(raw_targets, Sequence):
        return ()
    return tuple(dict.fromkeys(str(item).strip() for item in raw_targets if str(item).strip()))


def _valid_data(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    return (
        bool(value.get("as_of"))
        and is_auditable_decision_data_reference(value)
        and value.get("quality") in {"full", "realtime", "snapshot"}
    )


def _valid_edge(value: Any) -> bool:
    return isinstance(value, Mapping) and all(
        isinstance(value.get(key), str) and value[key].strip()
        for key in ("thesis", "catalyst", "invalidation")
    )


def _valid_risk(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    max_loss = _as_float(value.get("max_loss_pct"))
    position_limit = _as_float(value.get("position_limit_pct"))
    basic_risk_valid = bool(
        max_loss is not None
        and position_limit is not None
        and 0 < max_loss <= 1
        and 0 < position_limit <= 1
    )
    if not basic_risk_valid:
        return False
    horizon = str(value.get("horizon") or "").strip().lower()
    if horizon not in {"ultra_short", "short_term", "swing"}:
        return True
    overnight_stress = _as_float(value.get("overnight_stress_pct"))
    limit_down_stress = _as_float(value.get("limit_down_stress_pct"))
    return bool(
        overnight_stress is not None
        and limit_down_stress is not None
        and 0 < overnight_stress <= 1
        and 0 < limit_down_stress <= 1
    )


def _valid_execution(value: Any) -> bool:
    return isinstance(value, Mapping) and all(
        isinstance(value.get(key), str) and value[key].strip()
        for key in ("entry_condition", "exit_condition", "review_at")
    )


def _quality_label(snapshot: Mapping[str, Any]) -> str:
    provenance = snapshot.get("provenance")
    if isinstance(provenance, Mapping):
        return str(provenance.get("quality_tier") or provenance.get("quality") or "unknown")
    return str(snapshot.get("data_quality") or "unknown")


def _snapshot_quality_state(
    snapshot: Mapping[str, Any], *, now: datetime | None
) -> tuple[str | None, bool]:
    observed_at = snapshot.get("observed_at")
    if not isinstance(observed_at, str) or not observed_at.strip():
        return "Market snapshot lacks an observed_at timestamp; regime is blocked.", False
    observed = _parse_timestamp(observed_at)
    if observed is None:
        return "Market snapshot observed_at is not ISO-8601; regime is blocked.", False
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    observed_utc = observed.astimezone(timezone.utc)
    if observed_utc > current + timedelta(minutes=1):
        return "Market snapshot timestamp is in the future; regime is blocked.", False
    market_session = snapshot.get("market_session")
    if not isinstance(market_session, Mapping):
        return "Market snapshot lacks market_session metadata; regime is blocked.", False
    session_state = str(market_session.get("state") or "").strip()
    if session_state in {"", "closed"}:
        return "Market snapshot is outside a verified trading-day session; regime is blocked.", False
    if str(market_session.get("calendar_basis") or "").strip() != "exchange_calendar":
        return "Market snapshot lacks an exchange-calendar trading-session classification; regime is blocked.", False
    provenance = snapshot.get("provenance")
    components = provenance.get("components") if isinstance(provenance, Mapping) else None
    calendar_component = components.get("trading_calendar") if isinstance(components, Mapping) else None
    if not isinstance(calendar_component, Mapping) or calendar_component.get("status") != "available":
        return "Market snapshot lacks a healthy trading-calendar source component; regime is blocked.", False
    max_age = (
        MAX_CONTINUOUS_SNAPSHOT_AGE
        if session_state in {"open_auction", "continuous_morning", "continuous_afternoon"}
        else MAX_END_OF_DAY_SNAPSHOT_AGE
    )
    if current - observed_utc > max_age:
        return "Market snapshot exceeds its permitted freshness window; regime is blocked.", False
    breadth = snapshot.get("breadth")
    if not isinstance(breadth, Mapping):
        return "Market snapshot lacks breadth metadata; regime is blocked.", False
    coverage = _as_float(breadth.get("coverage_ratio"))
    if coverage is None:
        return "Market breadth coverage is unavailable; regime is blocked.", False
    quality = _quality_label(snapshot)
    degraded = (
        quality != "realtime"
        or coverage < MIN_BREADTH_COVERAGE
        or session_state in {"pre_open", "midday_break"}
    )
    return None, degraded


def _string_items(value: Any) -> list[str]:
    return [str(item) for item in value] if isinstance(value, Sequence) and not isinstance(value, str) else []


def _as_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_nonnegative_int(value: Any) -> int:
    converted = _as_float(value)
    return max(0, int(converted)) if converted is not None else 0


def _parse_controls(
    value: Mapping[str, Any] | None,
) -> tuple[dict[str, str], list[str], bool, bool]:
    normalized = _normalized_assessments(value or {})
    statuses: dict[str, str] = {}
    blockers: list[str] = []
    has_veto = False
    has_conditional = False
    for role in REQUIRED_IC_CONTROL_ROLES:
        assessment = normalized.get(role)
        if assessment is None:
            statuses[role] = "missing"
            blockers.append(f"Missing required control assessment: {role}.")
            continue
        raw_status = assessment.get("status")
        try:
            status = RoleGateStatus(str(raw_status).strip().lower())
        except ValueError:
            statuses[role] = "invalid"
            blockers.append(f"Invalid control status for {role}.")
            continue
        statuses[role] = status.value
        if not str(assessment.get("reason") or "").strip():
            blockers.append(f"Missing auditable control reason for {role}.")
        if status == RoleGateStatus.VETO:
            has_veto = True
            blockers.append(f"Binding VETO from {role}: {assessment.get('reason')}")
        elif status == RoleGateStatus.CONDITIONAL:
            has_conditional = True
    return statuses, list(dict.fromkeys(blockers)), has_veto, has_conditional


def _normalized_assessments(value: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for raw_role, raw_assessment in value.items():
        role = str(raw_role).strip()
        if not role or raw_assessment is None:
            continue
        if isinstance(raw_assessment, Mapping):
            evidence_refs = raw_assessment.get("evidence_refs", ())
            normalized[role] = {
                "status": str(raw_assessment.get("status") or "").strip().lower(),
                "reason": str(raw_assessment.get("reason") or "").strip(),
                "evidence_refs": [
                    str(reference).strip()
                    for reference in evidence_refs
                    if str(reference).strip()
                ]
                if isinstance(evidence_refs, Sequence) and not isinstance(evidence_refs, str)
                else [],
            }
        else:
            normalized[role] = {"status": str(raw_assessment).strip().lower(), "reason": "", "evidence_refs": []}
    return normalized


def _normalize_model_versions(value: Mapping[str, Any] | None) -> dict[str, str]:
    """Normalize explicit, human-auditable versions of material decision models."""
    if not isinstance(value, Mapping):
        return {}
    normalized: dict[str, str] = {}
    for raw_name, raw_version in value.items():
        name = str(raw_name).strip()
        version = str(raw_version).strip()
        if name and version:
            normalized[name] = version
    return dict(sorted(normalized.items()))


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
