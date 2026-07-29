"""Condition-based paper actions for a non-executing observation desk."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any, Mapping

from .decision import MarketRegime


class ObservationAction(StrEnum):
    """Research actions that never express an order or broker instruction."""

    NO_ACTION = "no_action"
    OBSERVE = "observe"
    PREPARE_CONDITIONAL_PLAN = "prepare_conditional_plan"
    CONDITIONAL_PAPER_ENTRY = "conditional_paper_entry"
    PAPER_RISK_REDUCE = "paper_risk_reduce"


@dataclass(frozen=True)
class ObservationActionResult:
    """A bounded technical action instruction for research or paper tracking."""

    action: ObservationAction
    formal_decision_eligible: bool
    passed_checks: tuple[str, ...]
    failed_checks: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-observation-action.v1",
            "action": self.action.value,
            "formal_decision_eligible": self.formal_decision_eligible,
            "passed_checks": list(self.passed_checks),
            "failed_checks": list(self.failed_checks),
            "warnings": list(self.warnings),
            "research_only": True,
            "no_order_execution": True,
        }


def evaluate_observation_action(
    candidate: Mapping[str, Any], *, regime: MarketRegime | str
) -> ObservationActionResult:
    """Produce a conditional paper action from timestamped observation data.

    This lane deliberately accepts source-labelled public observations so an
    unconnected research desk can stay useful. It never grants formal IC
    approval, releases an active paper plan, or emits a brokerage action.
    """
    market_regime = MarketRegime(regime)
    passed: list[str] = []
    failed: list[str] = []
    warnings = [
        "Observation actions are research-only and never submit, route, or amend orders.",
        "Public or unfrozen data cannot support a formal investment-committee decision or active paper-plan release.",
    ]
    if _valid_observation_data(candidate.get("data")):
        passed.append("timestamped_observation_data")
    else:
        failed.append("timestamped_observation_data")
    if _valid_technical_conditions(candidate.get("technical")):
        passed.append("technical_conditions")
    else:
        failed.append("technical_conditions")
    if _valid_risk_bounds(candidate.get("risk")):
        passed.append("risk_bounds")
    else:
        failed.append("risk_bounds")
    if _valid_review_time(candidate.get("review_at")):
        passed.append("review_time")
    else:
        failed.append("review_time")

    if failed:
        return ObservationActionResult(
            action=ObservationAction.OBSERVE,
            formal_decision_eligible=False,
            passed_checks=tuple(passed),
            failed_checks=tuple(failed),
            warnings=tuple(warnings + ["Missing observation controls prevent a conditional paper action."]),
        )
    if market_regime == MarketRegime.INSUFFICIENT_DATA:
        return ObservationActionResult(
            action=ObservationAction.NO_ACTION,
            formal_decision_eligible=False,
            passed_checks=tuple(passed),
            failed_checks=(),
            warnings=tuple(warnings + ["Market regime is insufficient_data; refresh the broad-market packet first."]),
        )
    if market_regime == MarketRegime.RISK_OFF:
        return ObservationActionResult(
            action=ObservationAction.PAPER_RISK_REDUCE,
            formal_decision_eligible=False,
            passed_checks=tuple(passed),
            failed_checks=(),
            warnings=tuple(warnings + ["Risk-off permits only paper risk reduction or observation."]),
        )
    if market_regime == MarketRegime.DEFENSIVE_ROTATION:
        return ObservationActionResult(
            action=ObservationAction.PREPARE_CONDITIONAL_PLAN,
            formal_decision_eligible=False,
            passed_checks=tuple(passed),
            failed_checks=(),
            warnings=tuple(warnings + ["Defensive rotation does not confirm broad new-risk permission."]),
        )
    return ObservationActionResult(
        action=ObservationAction.CONDITIONAL_PAPER_ENTRY,
        formal_decision_eligible=False,
        passed_checks=tuple(passed),
        failed_checks=(),
        warnings=tuple(warnings + ["Execute the stated condition only in a separately maintained paper record; reassess at review_at."]),
    )


def _valid_observation_data(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    source = str(value.get("source") or "").strip()
    quality = str(value.get("quality") or value.get("quality_tier") or "").strip().lower()
    as_of = value.get("as_of")
    if not source or quality not in {"realtime", "delayed", "snapshot", "partial"}:
        return False
    try:
        datetime.fromisoformat(str(as_of).replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _valid_technical_conditions(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    return all(str(value.get(field) or "").strip() for field in ("entry_condition", "invalidation_condition"))


def _valid_risk_bounds(value: Any) -> bool:
    if not isinstance(value, Mapping):
        return False
    try:
        loss = float(value.get("max_loss_pct"))
        position = float(value.get("position_limit_pct"))
    except (TypeError, ValueError):
        return False
    return math.isfinite(loss) and math.isfinite(position) and 0 < loss <= 1 and 0 < position <= 1


def _valid_review_time(value: Any) -> bool:
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return False
    return True
