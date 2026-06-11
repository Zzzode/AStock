from pathlib import Path

from astock.quality import (
    check_prompt_drift,
    evaluate_report_quality,
    evaluate_skill_response_cases,
    evaluate_source_health,
)


def test_evaluate_source_health_groups_by_source() -> None:
    result = evaluate_source_health(
        [
            {
                "source": "akshare.quote",
                "quality_tier": "realtime",
                "latency_ms": 100,
                "warnings": [],
                "errors": [],
            },
            {
                "source": "akshare.quote",
                "quality_tier": "degraded",
                "latency_ms": 300,
                "warnings": ["fallback"],
                "errors": [],
            },
            {
                "source": "eastmoney.flow",
                "quality_tier": "unavailable",
                "errors": ["timeout"],
            },
        ]
    )

    sources = {item["source"]: item for item in result["sources"]}
    assert result["overall_status"] == "failing"
    assert sources["akshare.quote"]["record_count"] == 2
    assert sources["akshare.quote"]["status"] == "degraded"
    assert sources["eastmoney.flow"]["status"] == "failing"


def test_check_prompt_drift_detects_identical_and_drifted_files(tmp_path: Path) -> None:
    left = tmp_path / "left.md"
    right = tmp_path / "right.md"
    drifted = tmp_path / "drifted.md"
    left.write_text("same\n", encoding="utf-8")
    right.write_text("same\n", encoding="utf-8")
    drifted.write_text("different\n", encoding="utf-8")

    result = check_prompt_drift(
        [
            {"name": "same", "left": left, "right": right},
            {"name": "drifted", "left": left, "right": drifted},
        ]
    )
    pairs = {item["name"]: item for item in result["pairs"]}

    assert result["status"] == "drift"
    assert pairs["same"]["identical"] is True
    assert pairs["drifted"]["identical"] is False
    assert result["drift_count"] == 1


def test_evaluate_report_quality_scores_required_elements() -> None:
    result = evaluate_report_quality("""
        Evidence and source provenance are listed.
        Risk: downside scenario is reviewed.
        Contrarian view: bear case is weaker.
        Monitoring trigger: watch volume confirmation.
        Invalidation: thesis fails if support breaks.
        Data quality: snapshot.
        """)

    assert result["status"] == "excellent"
    assert result["passed_count"] == result["check_count"]


def test_evaluate_skill_response_cases_flags_forbidden_actions() -> None:
    result = evaluate_skill_response_cases(
        [
            {
                "name": "boundary_ok",
                "response": "Python returns data packets; the agent explains risks.",
                "required_terms": ["data packets", "risks"],
            },
            {
                "name": "boundary_violation",
                "response": "I will place order through the broker login.",
                "required_terms": ["data"],
            },
        ]
    )
    cases = {item["name"]: item for item in result["cases"]}

    assert result["status"] == "weak"
    assert cases["boundary_ok"]["passed"] is True
    assert cases["boundary_violation"]["passed"] is False
    assert "place order" in cases["boundary_violation"]["forbidden_hits"]
