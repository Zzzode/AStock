"""Tests for quality feedback store."""

import json

import pytest

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


def test_reassessment_rebuilds_role_scores_instead_of_double_counting(store):
    store.record_quality_report(
        ResearchQualityReport(
            entry_id="entry-reassessed",
            agent_scores=[AgentRoleScore(role="risk", correct_calls=1, total_calls=1)],
        )
    )
    store.record_quality_report(
        ResearchQualityReport(
            entry_id="entry-reassessed",
            agent_scores=[AgentRoleScore(role="risk", correct_calls=0, total_calls=1)],
        )
    )

    score = store.get_aggregate_stats()["agent_role_scores"]["risk"]

    assert score["correct_calls"] == 0
    assert score["total_calls"] == 1
    assert score["accuracy"] == 0.0


def test_reload_rebuilds_legacy_aggregate_scores_from_reports(tmp_path) -> None:
    store_path = tmp_path / "feedback.json"
    report = ResearchQualityReport(
        entry_id="entry-persisted",
        agent_scores=[AgentRoleScore(role="risk", correct_calls=1, total_calls=1)],
    )
    store_path.write_text(
        json.dumps(
            {
                "schema_version": "quality-feedback.v1",
                "reports": [report.to_dict()],
                "aggregate_role_scores": [
                    {"role": "risk", "correct_calls": 99, "total_calls": 100}
                ],
            }
        ),
        encoding="utf-8",
    )

    reloaded = QualityFeedbackStore(store_path)
    score = reloaded.get_aggregate_stats()["agent_role_scores"]["risk"]

    assert score["correct_calls"] == 1
    assert score["total_calls"] == 1
