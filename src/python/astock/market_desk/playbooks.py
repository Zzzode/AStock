"""Deterministic contracts for the discretionary A-share trading playbooks.

The definitions in this module describe what a desk must prove before it may
create a *paper* plan.  They do not predict prices, express broker orders, or
turn a chart pattern into a decision by itself.  In particular, no moving
average, oscillator, or other mechanical-indicator rule is used here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping, Sequence

from .decision import MarketRegime


class EvidenceLevel(StrEnum):
    """The reproducibility threshold required for a piece of evidence."""

    TIMESTAMPED_PUBLIC = "timestamped_public_data"
    REPRODUCIBLE_INTRADAY_EXECUTION = "reproducible_intraday_execution_data"


class PlaybookDecision(StrEnum):
    """A research-only outcome from the playbook eligibility evaluation."""

    ALLOWED = "allowed"
    CONDITIONAL = "conditional"
    WATCH = "watch"
    REJECT = "reject"


@dataclass(frozen=True)
class EvidenceRequirement:
    """One source-addressable observation required by a discretionary setup."""

    key: str
    level: EvidenceLevel
    description: str


@dataclass(frozen=True)
class PlaybookRiskDefaults:
    """Default risk boundaries; a separate portfolio gate may tighten them."""

    max_position_pct: float
    max_loss_pct: float
    time_stop_sessions: int
    overnight_risk_review: bool


@dataclass(frozen=True)
class PlaybookDefinition:
    """A named discretionary pattern, not an automatic trading instruction."""

    name: str
    horizon: str
    permitted_regimes: tuple[MarketRegime, ...]
    evidence_requirements: tuple[EvidenceRequirement, ...]
    confirmation: str
    invalidation: str
    time_stop: str
    risk_defaults: PlaybookRiskDefaults
    required_team_roles: tuple[str, ...]
    decision_eligibility_conditions: tuple[str, ...]


@dataclass(frozen=True)
class PlaybookEvaluation:
    """A transparent result which remains strictly inside paper research."""

    playbook_id: str
    decision: PlaybookDecision
    passed_requirements: tuple[str, ...]
    failed_requirements: tuple[str, ...]
    conditional_requirements: tuple[str, ...]
    reasons: tuple[str, ...]
    paper_research_only: bool = True
    no_order_execution: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-playbook-evaluation.v1",
            "playbook_id": self.playbook_id,
            "decision": self.decision.value,
            "passed_requirements": list(self.passed_requirements),
            "failed_requirements": list(self.failed_requirements),
            "conditional_requirements": list(self.conditional_requirements),
            "warnings": list(self.reasons),
            "research_only": self.paper_research_only,
            "no_order_execution": self.no_order_execution,
        }


_CORE_ROLES = (
    "data-collector",
    "data-verifier",
    "market-regime-analyst",
    "risk-analyst",
    "contrarian-analyst",
    "portfolio-manager",
    "compliance-officer",
)


def _public(key: str, description: str) -> EvidenceRequirement:
    return EvidenceRequirement(key, EvidenceLevel.TIMESTAMPED_PUBLIC, description)


def _intraday(key: str, description: str) -> EvidenceRequirement:
    return EvidenceRequirement(key, EvidenceLevel.REPRODUCIBLE_INTRADAY_EXECUTION, description)


_ULTRA_SHORT_RISK = PlaybookRiskDefaults(0.10, 0.035, 2, True)
_SHORT_TERM_RISK = PlaybookRiskDefaults(0.15, 0.060, 7, True)
_SWING_RISK = PlaybookRiskDefaults(0.20, 0.080, 30, False)


PLAYBOOKS: dict[str, PlaybookDefinition] = {
    "theme_ignition_first_board": PlaybookDefinition(
        name="theme_ignition_first_board",
        horizon="ultra_short",
        permitted_regimes=(MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("new_catalyst", "Timestamped public disclosure or policy catalyst."),
            _public("theme_breadth", "Timestamped participation breadth across the named theme."),
            _public("leader_identity", "Timestamped evidence that the candidate is a liquid thematic leader."),
            _intraday("auction_and_trade_quality", "Reproducible auction and intraday trade record for the confirmation."),
        ),
        confirmation="Catalyst, breadth, and reproducible opening-to-intraday acceptance remain aligned.",
        invalidation="The catalyst is disproved, breadth fails, or the confirmed leader loses acceptance.",
        time_stop="Exit the paper thesis after two sessions without continuation.",
        risk_defaults=_ULTRA_SHORT_RISK,
        required_team_roles=(*_CORE_ROLES, "ultra-short-tactical-trader", "sector-rotation-analyst", "event-driven-institutional-analyst", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "leader_continuation": PlaybookDefinition(
        name="leader_continuation",
        horizon="ultra_short",
        permitted_regimes=(MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("theme_breadth", "Timestamped theme breadth and continuation evidence."),
            _public("leader_identity", "Timestamped market-wide leadership and liquidity evidence."),
            _public("prior_session_acceptance", "Timestamped prior-session acceptance and turnover record."),
            _intraday("auction_and_trade_quality", "Reproducible auction and intraday acceptance record."),
        ),
        confirmation="The established leader retains theme leadership and intraday acceptance after a planned review.",
        invalidation="Theme breadth contracts materially or the leader fails its acceptance condition.",
        time_stop="Review daily; expire after two sessions without continuation.",
        risk_defaults=_ULTRA_SHORT_RISK,
        required_team_roles=(*_CORE_ROLES, "ultra-short-tactical-trader", "sector-rotation-analyst", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "leader_pullback_acceptance": PlaybookDefinition(
        name="leader_pullback_acceptance",
        horizon="short_term",
        permitted_regimes=(MarketRegime.DEFENSIVE_ROTATION, MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("theme_breadth", "Timestamped evidence that the original theme remains active."),
            _public("leader_identity", "Timestamped liquid-leader identification."),
            _public("pullback_context", "Timestamped pullback, turnover, and relative-strength context."),
            _public("catalyst_validity", "Timestamped public evidence that the original catalyst remains valid."),
        ),
        confirmation="The pullback stabilizes while the leader and its theme retain relative acceptance.",
        invalidation="The catalyst or theme leadership breaks, or the stated pullback boundary fails.",
        time_stop="Expire after five sessions if acceptance is not reconfirmed.",
        risk_defaults=_SHORT_TERM_RISK,
        required_team_roles=(*_CORE_ROLES, "sector-rotation-analyst", "short-term-trader", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "emotion_repair_rebound": PlaybookDefinition(
        name="emotion_repair_rebound",
        horizon="ultra_short",
        permitted_regimes=(MarketRegime.DEFENSIVE_ROTATION, MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("market_emotion_damage", "Timestamped breadth and price-limit ecology evidence of the prior damage."),
            _public("repair_breadth", "Timestamped evidence of broad rather than isolated repair."),
            _public("core_liquidity", "Timestamped liquidity and turnover evidence for the candidate."),
            _public("catalyst_validity", "Timestamped catalyst or narrative validity evidence."),
            _intraday("repair_trade_quality", "Reproducible intraday trade record confirming broad repair rather than an isolated print."),
        ),
        confirmation="Repair expands beyond a single name and the selected liquid core holds acceptance.",
        invalidation="Repair breadth fades, new downside damage appears, or the catalyst fails.",
        time_stop="Expire after three sessions without broad repair follow-through.",
        risk_defaults=_ULTRA_SHORT_RISK,
        required_team_roles=(*_CORE_ROLES, "ultra-short-tactical-trader", "market-analyst", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "theme_follow_through": PlaybookDefinition(
        name="theme_follow_through",
        horizon="short_term",
        permitted_regimes=(MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("new_catalyst", "Timestamped public catalyst with source provenance."),
            _public("theme_breadth", "Timestamped multi-name theme participation and persistence."),
            _public("beneficiary_mapping", "Timestamped business exposure mapping, not merely a shared concept label."),
            _public("liquidity_context", "Timestamped liquidity and turnover context."),
        ),
        confirmation="The catalyst persists, participation broadens, and the candidate has verified beneficiary status.",
        invalidation="Catalyst, beneficiary mapping, or theme persistence is invalidated.",
        time_stop="Expire after seven sessions without follow-through.",
        risk_defaults=_SHORT_TERM_RISK,
        required_team_roles=(*_CORE_ROLES, "sector-rotation-analyst", "industry-analyst", "short-term-trader", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "event_repricing": PlaybookDefinition(
        name="event_repricing",
        horizon="short_term",
        permitted_regimes=(MarketRegime.DEFENSIVE_ROTATION, MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("primary_event", "Timestamped primary filing, official release, or issuer announcement."),
            _public("expectation_gap", "Timestamped comparison to the prior observable market expectation."),
            _public("fundamental_bridge", "Reproducible revenue, margin, cash-flow, supply-demand, or capital-allocation bridge."),
            _public("liquidity_context", "Timestamped liquidity and turnover context."),
        ),
        confirmation="The event changes a verified expectation bridge and price acceptance persists after review.",
        invalidation="The event is superseded, the bridge fails, or the stated acceptance condition breaks.",
        time_stop="Expire after seven sessions unless a separate swing plan is approved.",
        risk_defaults=_SHORT_TERM_RISK,
        required_team_roles=(*_CORE_ROLES, "event-driven-institutional-analyst", "fundamental-analyst", "valuation-specialist", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "swing_trend_continuation": PlaybookDefinition(
        name="swing_trend_continuation",
        horizon="swing",
        permitted_regimes=(MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("relative_strength_context", "Timestamped relative-strength and turnover context."),
            _public("industry_support", "Timestamped industry supply-demand or earnings support."),
            _public("catalyst_validity", "Timestamped catalyst validity evidence."),
            _public("liquidity_context", "Timestamped liquidity and trading-capacity context."),
        ),
        confirmation="Relative strength persists with sector support and no deterioration in the stated catalyst.",
        invalidation="The relative-strength boundary, industry support, or catalyst validity fails.",
        time_stop="Expire after 30 sessions without a verified continuation review.",
        risk_defaults=_SWING_RISK,
        required_team_roles=(*_CORE_ROLES, "swing-trend-analyst", "fundamental-analyst", "industry-analyst", "execution-liquidity-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
    "earnings_expectation_revision": PlaybookDefinition(
        name="earnings_expectation_revision",
        horizon="swing",
        permitted_regimes=(MarketRegime.DEFENSIVE_ROTATION, MarketRegime.SELECTIVE_RISK_ON, MarketRegime.TREND_RISK_ON),
        evidence_requirements=(
            _public("primary_earnings_source", "Timestamped issuer filing, earnings release, or official guidance."),
            _public("earnings_bridge", "Reproducible earnings, cash-flow, and balance-sheet bridge."),
            _public("expectation_gap", "Timestamped comparison to prior observable expectations."),
            _public("valuation_context", "Timestamped valuation and scenario context."),
        ),
        confirmation="A verified earnings bridge changes expectations and remains intact after the scheduled review.",
        invalidation="The earnings bridge, guidance, cash conversion, or valuation premise fails.",
        time_stop="Expire after 30 sessions without a maintained earnings-revision thesis.",
        risk_defaults=_SWING_RISK,
        required_team_roles=(*_CORE_ROLES, "growth-earnings-modeler", "fundamental-analyst", "valuation-specialist", "industry-analyst"),
        decision_eligibility_conditions=("confirmation_observed", "invalidation_defined", "time_stop_defined", "risk_within_default"),
    ),
}


def get_playbook(name: str) -> PlaybookDefinition:
    """Return one of the desk's eight named discretionary playbooks."""

    try:
        return PLAYBOOKS[name]
    except KeyError as exc:
        raise ValueError(f"unknown market-desk playbook: {name}") from exc


def list_playbooks() -> list[dict[str, Any]]:
    """Return the complete playbook catalog as JSON-safe research metadata."""

    return [
        {
            "playbook_id": definition.name,
            "horizon": definition.horizon,
            "permitted_regimes": [regime.value for regime in definition.permitted_regimes],
            "evidence_requirements": [
                {
                    "key": requirement.key,
                    "level": requirement.level.value,
                    "description": requirement.description,
                }
                for requirement in definition.evidence_requirements
            ],
            "confirmation": definition.confirmation,
            "invalidation": definition.invalidation,
            "time_stop": definition.time_stop,
            "risk_defaults": {
                "max_position_pct": definition.risk_defaults.max_position_pct,
                "max_loss_pct": definition.risk_defaults.max_loss_pct,
                "time_stop_sessions": definition.risk_defaults.time_stop_sessions,
                "overnight_risk_review": definition.risk_defaults.overnight_risk_review,
            },
            "required_team_roles": list(definition.required_team_roles),
            "decision_eligibility_conditions": list(definition.decision_eligibility_conditions),
            "research_only": True,
            "no_order_execution": True,
        }
        for definition in PLAYBOOKS.values()
    ]


def evaluate_playbook(
    playbook_id: str,
    evidence: Mapping[str, Any],
    regime: MarketRegime | str,
) -> dict[str, Any]:
    """Evaluate a candidate against a playbook without creating an order.

    Evidence entries must be source-addressable mappings.  Public observations
    require ``source`` and ``as_of``.  Intraday observations additionally need
    ``reproducible=True`` plus a capture/sequence reference, preventing a
    transient screen view from being presented as an execution-quality record.
    """

    definition = get_playbook(playbook_id)
    market_regime = MarketRegime(regime)
    roles = evidence.get("completed_roles", ())
    eligibility = evidence.get("eligibility", {})
    passed: list[str] = []
    failed: list[str] = []
    conditional: list[str] = []
    reasons: list[str] = ["Result is research-only; no broker order or execution instruction is produced."]

    if market_regime in {MarketRegime.INSUFFICIENT_DATA, MarketRegime.RISK_OFF}:
        return PlaybookEvaluation(
            playbook_id=definition.name,
            decision=PlaybookDecision.REJECT,
            passed_requirements=(),
            failed_requirements=("market_regime",),
            conditional_requirements=(),
            reasons=tuple(reasons + [f"{market_regime.value} does not permit new {definition.horizon} playbook risk."]),
        ).to_dict()
    if market_regime not in definition.permitted_regimes:
        return PlaybookEvaluation(
            playbook_id=definition.name,
            decision=PlaybookDecision.REJECT,
            passed_requirements=(),
            failed_requirements=("market_regime",),
            conditional_requirements=(),
            reasons=tuple(reasons + [f"{definition.name} is not permitted in {market_regime.value}." ]),
        ).to_dict()
    passed.append("market_regime")

    for requirement in definition.evidence_requirements:
        if _valid_evidence(evidence.get(requirement.key), requirement.level):
            passed.append(requirement.key)
        else:
            failed.append(requirement.key)
            reasons.append(f"Missing or non-reproducible {requirement.level.value}: {requirement.key}.")

    if failed:
        return PlaybookEvaluation(
            playbook_id=definition.name,
            decision=PlaybookDecision.WATCH,
            passed_requirements=tuple(passed),
            failed_requirements=tuple(failed),
            conditional_requirements=(),
            reasons=tuple(reasons + ["Collect the missing evidence before considering a conditional paper plan."]),
        ).to_dict()

    role_set = {str(role).strip() for role in roles if str(role).strip()} if isinstance(roles, Sequence) and not isinstance(roles, str) else set()
    missing_roles = tuple(role for role in definition.required_team_roles if role not in role_set)
    if missing_roles:
        conditional.extend(f"team_role:{role}" for role in missing_roles)
        reasons.append("Required desk roles have not completed this review: " + ", ".join(missing_roles) + ".")

    for condition in definition.decision_eligibility_conditions:
        if isinstance(eligibility, Mapping) and eligibility.get(condition) is True:
            passed.append(condition)
        else:
            conditional.append(condition)
            reasons.append(f"Decision eligibility condition is not confirmed: {condition}.")

    if conditional:
        return PlaybookEvaluation(
            playbook_id=definition.name,
            decision=PlaybookDecision.CONDITIONAL,
            passed_requirements=tuple(passed),
            failed_requirements=(),
            conditional_requirements=tuple(conditional),
            reasons=tuple(reasons),
        ).to_dict()
    return PlaybookEvaluation(
        playbook_id=definition.name,
        decision=PlaybookDecision.ALLOWED,
        passed_requirements=tuple(passed),
        failed_requirements=(),
        conditional_requirements=(),
        reasons=tuple(reasons + ["All playbook gates passed; a separate IC process remains required for any active paper plan."]),
    ).to_dict()


def _valid_evidence(value: Any, level: EvidenceLevel) -> bool:
    if not isinstance(value, Mapping):
        return False
    if not str(value.get("source") or "").strip() or not _valid_timestamp(value.get("as_of")):
        return False
    if level == EvidenceLevel.TIMESTAMPED_PUBLIC:
        return True
    capture_reference = value.get("capture_ref") or value.get("sequence_ref")
    return value.get("reproducible") is True and bool(str(capture_reference or "").strip())


def _valid_timestamp(value: Any) -> bool:
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).tzinfo is not None
    except ValueError:
        return False
