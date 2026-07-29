"""Tests for the non-executing daily observation-action lane."""

from astock.market_desk import (
    MarketRegime,
    ObservationAction,
    evaluate_observation_action,
)


def _candidate() -> dict[str, object]:
    return {
        "data": {
            "source": "akshare_public",
            "quality": "realtime",
            "as_of": "2026-07-28T10:00:00+08:00",
        },
        "technical": {
            "entry_condition": "Close holds above the defined trigger with volume confirmation.",
            "invalidation_condition": "Close falls below the stated invalidation level.",
        },
        "risk": {"max_loss_pct": 0.02, "position_limit_pct": 0.1},
        "review_at": "2026-07-28T14:50:00+08:00",
    }


def test_public_realtime_observation_can_issue_only_conditional_paper_action() -> None:
    result = evaluate_observation_action(_candidate(), regime=MarketRegime.SELECTIVE_RISK_ON)

    assert result.action == ObservationAction.CONDITIONAL_PAPER_ENTRY
    assert result.formal_decision_eligible is False
    assert result.to_dict()["no_order_execution"] is True


def test_risk_off_changes_complete_setup_to_paper_risk_reduction() -> None:
    result = evaluate_observation_action(_candidate(), regime=MarketRegime.RISK_OFF)

    assert result.action == ObservationAction.PAPER_RISK_REDUCE


def test_missing_conditions_leave_observation_only() -> None:
    candidate = _candidate()
    candidate["technical"] = {}

    result = evaluate_observation_action(candidate, regime=MarketRegime.TREND_RISK_ON)

    assert result.action == ObservationAction.OBSERVE
    assert "technical_conditions" in result.failed_checks
