"""Deterministic building blocks for the A-share end-of-day market desk."""

from .decision import (
    CandidateGateResult,
    DeskDecision,
    InvestmentCommitteeDecision,
    MarketRegime,
    MarketRegimeAssessment,
    REQUIRED_IC_CONTROL_ROLES,
    RoleGateStatus,
    assess_market_regime,
    decide_investment_committee,
    evaluate_candidate_gate,
)
from .compliance import ComplianceAssessment, ComplianceStatus, assess_candidate_compliance
from .strategy_book import (
    StrategyHorizon,
    StrategyPlan,
    StrategyState,
    record_strategy_plan_review,
    transition_strategy_plan,
)
from .attribution import PaperDecisionReview, ReviewOutcome, review_paper_decision
from .restricted_list import (
    RestrictedListAttestation,
    RestrictedListEntry,
    RestrictedListStore,
)
from .assurance import PaperDeskAssuranceReport, verify_paper_desk_release
from .observation_action import ObservationAction, ObservationActionResult, evaluate_observation_action
from .playbooks import (
    PLAYBOOKS,
    EvidenceLevel,
    PlaybookDecision,
    PlaybookDefinition,
    evaluate_playbook,
    get_playbook,
    list_playbooks,
)
from .observation_log import (
    PublicDeskObservationRun,
    PublicDeskObservationExceptionReview,
    build_public_desk_observation_run,
    create_public_desk_observation_exception_review,
    list_public_desk_observation_runs,
    verify_public_desk_observation_run,
)

__all__ = [
    "CandidateGateResult",
    "DeskDecision",
    "InvestmentCommitteeDecision",
    "MarketRegime",
    "MarketRegimeAssessment",
    "REQUIRED_IC_CONTROL_ROLES",
    "RoleGateStatus",
    "assess_market_regime",
    "decide_investment_committee",
    "evaluate_candidate_gate",
    "StrategyHorizon",
    "StrategyPlan",
    "StrategyState",
    "record_strategy_plan_review",
    "transition_strategy_plan",
    "ComplianceAssessment",
    "ComplianceStatus",
    "assess_candidate_compliance",
    "PaperDecisionReview",
    "ReviewOutcome",
    "review_paper_decision",
    "RestrictedListEntry",
    "RestrictedListAttestation",
    "RestrictedListStore",
    "PaperDeskAssuranceReport",
    "verify_paper_desk_release",
    "ObservationAction",
    "ObservationActionResult",
    "evaluate_observation_action",
    "PLAYBOOKS",
    "EvidenceLevel",
    "PlaybookDecision",
    "PlaybookDefinition",
    "evaluate_playbook",
    "get_playbook",
    "list_playbooks",
    "PublicDeskObservationRun",
    "PublicDeskObservationExceptionReview",
    "build_public_desk_observation_run",
    "create_public_desk_observation_exception_review",
    "list_public_desk_observation_runs",
    "verify_public_desk_observation_run",
]
