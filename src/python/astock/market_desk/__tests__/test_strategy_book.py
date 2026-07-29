"""Lifecycle tests for the market desk's conditional strategy books."""

import pytest

from astock.market_desk import (
    StrategyHorizon,
    StrategyPlan,
    StrategyState,
    record_strategy_plan_review,
    transition_strategy_plan,
)


def _short_plan() -> StrategyPlan:
    return StrategyPlan(
        plan_id="short-600460-20260728",
        horizon=StrategyHorizon.SHORT_TERM,
        state=StrategyState.OBSERVATION,
        target="600460",
        thesis="Verified sector observation may justify a conditional setup.",
        as_of="2026-07-28T15:00:00+08:00",
        entry_condition="Close above the verified trigger after T+1 is feasible.",
        invalidation_condition="Close below the defined risk level.",
        review_at="2026-07-29T15:00:00+08:00",
        time_stop_at="2026-08-07T15:00:00+08:00",
        evidence_refs=("market_snapshot:2026-07-28T15:00:00+08:00",),
    )


def test_short_plan_requires_a_time_stop_and_evidence() -> None:
    payload = _short_plan().to_dict()
    payload["time_stop_at"] = None
    with pytest.raises(ValueError, match="time_stop"):
        StrategyPlan.from_dict(payload)


def test_ultra_short_plan_tracks_its_playbook_and_requires_time_stop() -> None:
    plan = StrategyPlan(
        plan_id="ultra-600460-20260728",
        horizon=StrategyHorizon.ULTRA_SHORT,
        state=StrategyState.OBSERVATION,
        target="600460",
        thesis="Leader continuation requires reproducible intraday confirmation.",
        as_of="2026-07-28T15:00:00+08:00",
        entry_condition="The named confirmation occurs.",
        invalidation_condition="The leader loses acceptance.",
        review_at="2026-07-29T15:00:00+08:00",
        time_stop_at="2026-07-30T15:00:00+08:00",
        evidence_refs=("market_snapshot:2026-07-28T15:00:00+08:00",),
        playbook_id="leader_continuation",
    )

    assert StrategyPlan.from_dict(plan.to_dict()).playbook_id == "leader_continuation"
    invalid = plan.to_dict()
    invalid["time_stop_at"] = None
    with pytest.raises(ValueError, match="time_stop"):
        StrategyPlan.from_dict(invalid)


def test_strategy_plan_has_a_one_way_auditable_lifecycle() -> None:
    watched = transition_strategy_plan(
        _short_plan(), "watch", reason="Breadth and history confirmation pending.", observed_at="2026-07-28T15:10:00+08:00"
    )
    conditional = transition_strategy_plan(
        watched, "conditional", reason="All setup prerequisites are explicit.", observed_at="2026-07-29T10:00:00+08:00"
    )
    active = transition_strategy_plan(
        conditional,
        "active",
        reason="Separate IC record approved the paper plan.",
        observed_at="2026-07-29T15:00:00+08:00",
        ic_decision={
            "schema_version": "market-desk-ic-decision.v1",
                "candidate_id": conditional.plan_id,
                "candidate_targets": [conditional.target],
            "decision": "approve",
            "decision_owner": "portfolio-manager",
            "decided_at": "2026-07-29T15:00:00+08:00",
            "evidence_refs": ["market_snapshot:2026-07-29T15:00:00+08:00"],
            "model_versions": {"market_regime": "market-desk-regime.v1"},
            "control_assessments": {
                role: {"status": "pass"}
                for role in (
                    "data-verifier",
                    "risk-analyst",
                    "quant-risk-modeler",
                    "execution-liquidity-analyst",
                    "compliance-officer",
                )
            },
            },
            release_assurance={
                "schema_version": "market-desk-paper-assurance.v1",
                "verdict": "pass",
                "plan_id": conditional.plan_id,
                "target": conditional.target,
                "ic_candidate_id": conditional.plan_id,
            },
        )
    invalidated = transition_strategy_plan(
        active, "invalidated", reason="Risk level breached.", observed_at="2026-07-30T10:00:00+08:00"
    )

    assert invalidated.state == StrategyState.INVALIDATED
    assert len(invalidated.transition_history) == 4
    with pytest.raises(ValueError, match="illegal"):
        transition_strategy_plan(invalidated, "active", reason="retry")


def test_observation_cannot_jump_directly_to_active() -> None:
    with pytest.raises(ValueError, match="illegal"):
        transition_strategy_plan(_short_plan(), "active", reason="not permitted")


def test_conditional_plan_cannot_activate_without_matching_ic_decision() -> None:
    watched = transition_strategy_plan(_short_plan(), "watch", reason="review")
    conditional = transition_strategy_plan(watched, "conditional", reason="review")

    with pytest.raises(ValueError, match="IC decision"):
        transition_strategy_plan(conditional, "active", reason="missing IC")


def test_continuation_review_requires_evidence_and_cannot_extend_past_time_stop() -> None:
    reviewed = record_strategy_plan_review(
        _short_plan(),
        reviewer="portfolio-manager",
        reason="The invalidation condition has not occurred; retain observation status.",
        evidence_refs=("public-observation:sha256:fixture",),
        observed_at="2026-07-28T16:00:00+08:00",
        next_review_at="2026-07-30T15:00:00+08:00",
    )

    assert reviewed.state == StrategyState.OBSERVATION
    assert reviewed.review_at == "2026-07-30T15:00:00+08:00"
    assert reviewed.review_history[-1]["reviewer"] == "portfolio-manager"
    with pytest.raises(ValueError, match="time_stop"):
        record_strategy_plan_review(
            reviewed,
            reviewer="portfolio-manager",
            reason="Attempted extension after time stop.",
            evidence_refs=("public-observation:sha256:fixture",),
            observed_at="2026-08-07T15:00:00+08:00",
            next_review_at="2026-08-08T15:00:00+08:00",
        )
