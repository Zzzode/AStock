"""Tests for deterministic, research-only A-share playbook contracts."""

import pytest

from astock.market_desk.decision import MarketRegime
from astock.market_desk.playbooks import (
    EvidenceLevel,
    PLAYBOOKS,
    PlaybookDecision,
    evaluate_playbook,
)


def _evidence_for(name: str) -> dict[str, dict[str, object]]:
    payload: dict[str, dict[str, object]] = {}
    for requirement in PLAYBOOKS[name].evidence_requirements:
        item: dict[str, object] = {
            "source": "fixture:verified-source",
            "as_of": "2026-07-29T14:50:00+08:00",
        }
        if requirement.key == "next_session_plan":
            item.update(
                {
                    "entry_condition": "Only participate if the stated opening condition holds.",
                    "rejection_condition": "Cancel when the opening condition fails.",
                    "review_at": "2026-07-30T15:05:00+08:00",
                }
            )
        payload[requirement.key] = item
    payload["completed_roles"] = list(PLAYBOOKS[name].required_team_roles)  # type: ignore[assignment]
    payload["eligibility"] = _eligibility()  # type: ignore[assignment]
    return payload


def _eligibility(*, confirmed: bool = True) -> dict[str, bool]:
    return {
        "confirmation_observed": confirmed,
        "invalidation_defined": True,
        "time_stop_defined": True,
        "risk_within_default": True,
    }


def test_exactly_eight_named_playbooks_have_complete_contracts() -> None:
    assert tuple(PLAYBOOKS) == (
        "theme_ignition_first_board",
        "leader_continuation",
        "leader_pullback_acceptance",
        "emotion_repair_rebound",
        "theme_follow_through",
        "event_repricing",
        "swing_trend_continuation",
        "earnings_expectation_revision",
    )
    for definition in PLAYBOOKS.values():
        assert definition.horizon in {"ultra_short", "short_term", "swing", "long_term"}
        assert definition.evidence_requirements
        assert definition.confirmation and definition.invalidation and definition.time_stop
        assert definition.required_team_roles and definition.decision_eligibility_conditions


@pytest.mark.parametrize("name", ["theme_ignition_first_board", "leader_continuation", "emotion_repair_rebound"])
def test_ultra_short_daily_preplan_does_not_require_intraday_execution_data(name: str) -> None:
    result = evaluate_playbook(
        name,
        _evidence_for(name),
        MarketRegime.TREND_RISK_ON,
    )

    assert result["decision"] == PlaybookDecision.ALLOWED.value


@pytest.mark.parametrize("name", ["theme_ignition_first_board", "leader_continuation", "emotion_repair_rebound"])
def test_ultra_short_daily_preplan_requires_dated_next_session_conditions(name: str) -> None:
    evidence = _evidence_for(name)
    del evidence["next_session_plan"]

    result = evaluate_playbook(name, evidence, MarketRegime.TREND_RISK_ON)

    assert result["decision"] == PlaybookDecision.WATCH.value
    assert result["failed_requirements"] == ["next_session_plan"]


def test_ultra_short_daily_preplan_requires_entry_rejection_and_review_conditions() -> None:
    evidence = _evidence_for("leader_continuation")
    del evidence["next_session_plan"]["rejection_condition"]

    result = evaluate_playbook("leader_continuation", evidence, MarketRegime.TREND_RISK_ON)

    assert result["decision"] == PlaybookDecision.WATCH.value
    assert result["failed_requirements"] == ["next_session_plan"]


def test_regime_restriction_rejects_new_risk() -> None:
    result = evaluate_playbook(
        "theme_follow_through",
        _evidence_for("theme_follow_through"),
        MarketRegime.RISK_OFF,
    )

    assert result["decision"] == PlaybookDecision.REJECT.value
    assert result["failed_requirements"] == ["market_regime"]


def test_missing_public_evidence_stays_watch() -> None:
    evidence = _evidence_for("event_repricing")
    del evidence["fundamental_bridge"]
    result = evaluate_playbook(
        "event_repricing",
        evidence,
        MarketRegime.SELECTIVE_RISK_ON,
    )

    assert result["decision"] == PlaybookDecision.WATCH.value
    assert result["failed_requirements"] == ["fundamental_bridge"]


def test_invalid_timestamped_evidence_stays_watch() -> None:
    evidence = _evidence_for("theme_follow_through")
    evidence["new_catalyst"]["as_of"] = "not-a-timestamp"
    result = evaluate_playbook(
        "theme_follow_through",
        evidence,
        MarketRegime.TREND_RISK_ON,
    )

    assert result["decision"] == PlaybookDecision.WATCH.value
    assert result["failed_requirements"] == ["new_catalyst"]


def test_complete_evidence_with_unconfirmed_setup_is_conditional() -> None:
    name = "swing_trend_continuation"
    evidence = _evidence_for(name)
    evidence["eligibility"] = _eligibility(confirmed=False)  # type: ignore[assignment]
    result = evaluate_playbook(
        name,
        evidence,
        MarketRegime.TREND_RISK_ON,
    )

    assert result["decision"] == PlaybookDecision.CONDITIONAL.value
    assert result["conditional_requirements"] == ["confirmation_observed"]
    assert result["no_order_execution"] is True


def test_complete_playbook_evaluation_is_allowed_only_for_paper_research() -> None:
    name = "earnings_expectation_revision"
    result = evaluate_playbook(
        name,
        _evidence_for(name),
        MarketRegime.TREND_RISK_ON,
    )

    assert result["decision"] == PlaybookDecision.ALLOWED.value
    assert result["research_only"] is True
