from datetime import datetime

from astock.research import PostmortemRootCause, ResearchPostmortem


def test_research_postmortem_roundtrip() -> None:
    reviewed_at = datetime(2026, 6, 12, 15, 30)
    postmortem = ResearchPostmortem(
        entry_id="research-1",
        outcome="Thesis invalidated after catalyst failed.",
        root_cause="risk_assumption",
        expected="Policy support would offset margin pressure.",
        actual="Margin pressure dominated.",
        error_analysis="Risk assumption was too optimistic.",
        lessons=["Track margin data earlier", "Reduce catalyst confidence"],
        evidence={"source": "review"},
        reviewed_at=reviewed_at,
    )
    restored = ResearchPostmortem.from_dict(postmortem.to_dict())

    assert postmortem.postmortem_id.startswith("postmortem-20260612-")
    assert restored.root_cause == PostmortemRootCause.RISK_ASSUMPTION
    assert restored.lessons == (
        "Track margin data earlier",
        "Reduce catalyst confidence",
    )
    assert restored.evidence["source"] == "review"


def test_unknown_root_cause_degrades_to_unknown() -> None:
    postmortem = ResearchPostmortem(
        entry_id="research-1",
        outcome="Outcome unclear.",
        root_cause="unsupported",
    )

    assert postmortem.root_cause == PostmortemRootCause.UNKNOWN
