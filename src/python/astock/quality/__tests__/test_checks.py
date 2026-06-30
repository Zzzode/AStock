import json
import subprocess
import sys
from pathlib import Path

from astock.quality import (
    check_prompt_drift,
    evaluate_research_case_quality,
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
        Source exhaustion log is complete.
        Full-chain coverage gap and full_chain_universe are listed.
        Model reproducibility appears in the valuation audit.
        Review findings and repair plan close the review lifecycle.
        Final sign-off includes publishability score.
        """)

    assert result["status"] == "excellent"
    assert result["passed_count"] == result["check_count"]


def test_evaluate_research_case_quality_passes_complete_industry_case(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "industry-case"
    data_dir = case_dir / "data"
    analysis_dir = case_dir / "analysis"
    data_dir.mkdir(parents=True)
    analysis_dir.mkdir()

    _write(case_dir / "research_brief.md", "Industry-chain full-chain report.")
    _write(
        case_dir / "gate_manifest.md",
        "review_cycles: R0_evidence, R1_model, R2_draft, R3_render_compliance, R4_final_ic",
    )
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "report_type": "industry-chain",
            "review_cycles": ["R0_evidence", "R4_final_ic"],
            "required_artifacts": [
                "analysis/valuation_audit.md",
                "data/full_chain_universe_20260630.json",
            ],
        },
    )
    _write(case_dir / "artifact_contract.md", "artifact contract")
    _write_json(
        case_dir / "artifact_contract.json",
        {
            "artifacts": [
                {"path": "analysis/value_chain_economics.md"},
                {"path": "final_signoff.json"},
            ]
        },
    )
    _write(case_dir / "review_log.md", "Publishability Score: 94")
    _write(case_dir / "final_signoff.md", "signoff")
    _write_json(
        case_dir / "final_signoff.json",
        {
            "signoff_status": "PASS",
            "publishability_score": 94,
            "open_s_count": 0,
            "open_a_count": 0,
        },
    )
    _write(case_dir / "source_exhaustion_log.md", "done")
    _write_json(case_dir / "source_exhaustion_log.json", {"status": "complete"})
    _write(data_dir / "source_registry.md", "sources")
    _write_json(data_dir / "source_registry.json", {"sources": []})
    _write(data_dir / "claim_audit.md", "claims")
    _write_json(data_dir / "claim_audit.json", {"claims": []})
    _write(
        case_dir / "review_findings_R0_evidence.json",
        json.dumps({"findings": [{"severity": "A", "status": "closed"}]}),
    )
    _write(case_dir / "repair_plan_R0_evidence.md", "closed")
    _write_json(case_dir / "repair_plan_R0_evidence.json", {"status": "closed"})
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )

    for rel in (
        "template_brief.md",
        "full_chain_taxonomy.md",
        "core_vs_satellite_universe.md",
        "coverage_gap_matrix.md",
        "supply_chain_model.md",
        "company_fundamental_cards.md",
        "value_chain_economics.md",
        "chain_earnings_bridge.md",
        "competitive_landscape.md",
        "variant_perception.md",
    ):
        _write(analysis_dir / rel, rel)
    _write(analysis_dir / "valuation_audit.md", "Model Reproducibility: PASS")
    _write_json(
        data_dir / "full_chain_universe_20260630.json",
        {"rows": [{"node_type": "listed"}]},
    )
    _write_json(data_dir / "supply_chain_relationships.json", {"rows": []})
    _write_json(data_dir / "customer_chain_audit.json", {"rows": []})

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is True
    assert result["status"] == "excellent"
    assert result["requires_industry_chain"] is True
    assert result["review_summary"]["open_s_count"] == 0


def test_evaluate_research_case_quality_blocks_open_s_issue(tmp_path: Path) -> None:
    case_dir = tmp_path / "blocked-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R0_evidence.json",
        {"findings": [{"severity": "S", "status": "open"}]},
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert result["review_summary"]["open_s_count"] == 1
    assert any(
        check["name"] == "no open S-Level findings" and check["passed"] is False
        for check in result["checks"]
    )


def test_run_research_gates_passes_complete_minimal_case(tmp_path: Path) -> None:
    case_dir = tmp_path / "gate-case"
    _gate_runner_case(case_dir)
    script = (
        Path(__file__).resolve().parents[5]
        / "workspace"
        / "research"
        / "tools"
        / "run_research_gates.py"
    )

    completed = subprocess.run(
        [sys.executable, str(script), str(case_dir)],
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "RESULT PASS" in completed.stdout


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


def _minimal_case(case_dir: Path) -> None:
    (case_dir / "analysis").mkdir(parents=True)
    (case_dir / "data").mkdir()
    _write(case_dir / "research_brief.md", "single-stock report")
    _write(case_dir / "gate_manifest.md", "gate")
    _write_json(case_dir / "gate_manifest.json", {"report_type": "single-stock"})
    _write(case_dir / "artifact_contract.md", "contract")
    _write_json(case_dir / "artifact_contract.json", {"artifacts": []})
    _write(case_dir / "review_log.md", "Publishability Score: 93")
    _write(case_dir / "final_signoff.md", "signoff")
    _write_json(
        case_dir / "final_signoff.json",
        {"signoff_status": "PASS", "publishability_score": 93},
    )
    _write(case_dir / "source_exhaustion_log.md", "done")
    _write_json(case_dir / "source_exhaustion_log.json", {"status": "complete"})
    _write(case_dir / "data/source_registry.md", "sources")
    _write_json(case_dir / "data/source_registry.json", {"sources": []})
    _write(case_dir / "data/claim_audit.md", "claims")
    _write_json(case_dir / "data/claim_audit.json", {"claims": []})
    _write(case_dir / "analysis/valuation_audit.md", "Model Reproducibility: PASS")
    _write(case_dir / "repair_plan_R0_evidence.md", "repair")
    _write_json(case_dir / "repair_plan_R0_evidence.json", {"status": "open"})


def _gate_runner_case(case_dir: Path) -> None:
    (case_dir / "analysis").mkdir(parents=True)
    (case_dir / "data").mkdir()
    (case_dir / "sources").mkdir()
    (case_dir / "tools").mkdir()
    _write(case_dir / "research_brief.md", "single-stock report")
    _write(case_dir / "gate_manifest.md", "gate")
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "report_type": "single-stock",
            "review_cycles": [
                "R0_evidence",
                "R1_model",
                "R2_draft",
                "R3_render_compliance",
                "R4_final_ic",
            ],
            "required_artifacts": ["analysis/valuation_audit.md"],
        },
    )
    _write(case_dir / "artifact_contract.md", "contract")
    _write_json(case_dir / "artifact_contract.json", {"artifacts": []})
    _write(case_dir / "review_log.md", "Publishability Score: 95")
    _write(case_dir / "final_signoff.md", "signoff")
    _write_json(
        case_dir / "final_signoff.json",
        {
            "case_id": "gate-case",
            "report_type": "single-stock",
            "data_cutoff": "2026-06-30",
            "pdf_path": "main.pdf",
            "page_count": 12,
            "publishability_score": 95,
            "verifier_results": {"status": "PASS"},
            "open_s_count": 0,
            "open_a_count": 0,
            "residual_risks": [],
            "signoff_status": "PASS",
        },
    )
    _write(case_dir / "research_workflow_eval.md", "workflow eval")
    _write_json(
        case_dir / "research_workflow_eval.json",
        {
            "success": True,
            "quality": {
                "status": "excellent",
                "publishable": True,
                "score": 95,
                "blocking_failure_count": 0,
            },
        },
    )
    _write(case_dir / "source_exhaustion_log.md", "done")
    _write_json(case_dir / "source_exhaustion_log.json", {"status": "complete"})
    _write(case_dir / "data/source_registry.md", "sources")
    _write_json(case_dir / "data/source_registry.json", {"sources": []})
    _write(case_dir / "data/claim_audit.md", "claims")
    _write_json(case_dir / "data/claim_audit.json", {"claims": []})
    _write(case_dir / "analysis/valuation_audit.md", "Model Reproducibility: PASS")
    for cycle in (
        "R0_evidence",
        "R1_model",
        "R2_draft",
        "R3_render_compliance",
        "R4_final_ic",
    ):
        _write_json(
            case_dir / f"review_findings_{cycle}.json",
            {"findings": [{"severity": "A", "status": "closed"}]},
        )
        if cycle != "R4_final_ic":
            _write(case_dir / f"repair_plan_{cycle}.md", "closed")
            _write_json(case_dir / f"repair_plan_{cycle}.json", {"status": "closed"})
    _write(
        case_dir / "tools/verify_research_workspace.py",
        "print('SUMMARY 39 PASS / 0 FAIL')\n",
    )


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
