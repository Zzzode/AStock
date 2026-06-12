"""Tests for quality feedback store."""

import pytest
from pathlib import Path

from astock.quality.feedback import (
    AgentRoleScore,
    CatalystOutcome,
    QualityFeedbackStore,
    ResearchQualityReport,
    RiskOutcome,
)


@pytest.fixture
def store(tmp_path):
    return QualityFeedbackStore(tmp_path / "feedback.json")


def test_record_and_retrieve(store):
    report = ResearchQualityReport(
        entry_id="entry-001",
        catalyst_outcomes=[
            CatalystOutcome(catalyst="earnings beat", realized=True),
            CatalystOutcome(catalyst="policy boost", realized=False),
        ],
        risk_outcomes=[
            RiskOutcome(risk="macro downturn", materialized=False),
        ],
        unpredicted_risks=[
            RiskOutcome(risk="mgmt change", materialized=True, was_predicted=False),
        ],
    )
    store.record_quality_report(report)

    retrieved = store.get_report("entry-001")
    assert retrieved is not None
    assert retrieved.overall_catalyst_rate == 0.5
    assert retrieved.overall_risk_foresight == 0.0  # 1 materialized, 0 predicted


def test_aggregate_stats(store):
    report = ResearchQualityReport(
        entry_id="entry-002",
        catalyst_outcomes=[
            CatalystOutcome(catalyst="a", realized=True),
            CatalystOutcome(catalyst="b", realized=True),
        ],
        agent_scores=[
            AgentRoleScore(role="market", correct_calls=4, total_calls=5),
        ],
    )
    store.record_quality_report(report)

    stats = store.get_aggregate_stats()
    assert stats["total_assessed"] == 1
    assert stats["avg_catalyst_realization_rate"] == 1.0
    assert "market" in stats["agent_role_scores"]
    assert stats["agent_role_scores"]["market"]["accuracy"] == 0.8
