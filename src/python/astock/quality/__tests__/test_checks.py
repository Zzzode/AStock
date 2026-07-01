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
        Evidence depth covers customer order ASP utilization evidence gap.
        Model depth separates base business and growth segment gross profit net profit EPS.
        Investment committee portfolio position risk budget expected return is explicit.
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
            "depth_gates": [
                "evidence_depth",
                "broker_consensus_depth",
                "model_depth",
                "valuation_depth",
                "ic_readiness",
            ],
            "required_artifacts": [
                "analysis/valuation_audit.md",
                "data/broker_street_consensus_20260630.json",
                "data/full_chain_universe_20260630.json",
            ],
        },
    )
    _write(case_dir / "artifact_contract.md", "artifact contract")
    _write_json(
        case_dir / "artifact_contract.json",
        {
            "artifacts": [
                _contract_item("analysis/value_chain_economics.md"),
                _contract_item("final_signoff.json"),
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
        "chain_business_research.md",
        "core_vs_satellite_universe.md",
        "coverage_gap_matrix.md",
        "supply_chain_model.md",
        "chain_earnings_bridge.md",
        "competitive_landscape.md",
        "variant_perception.md",
    ):
        _write(analysis_dir / rel, rel)
    _write(
        analysis_dir / "chain_business_research.md",
        "upstream business downstream business business relationship core technology core revenue business 2026E expectation",
    )
    _write(
        analysis_dir / "company_fundamental_cards.md",
        "cash flow inventory capex debt order certification",
    )
    _write(
        analysis_dir / "value_chain_economics.md",
        "ASP margin capacity utilization order valuation credit",
    )
    _write(
        analysis_dir / "growth_earnings_model.md",
        "base business growth segment unit ASP gross net profit EPS bear bull current-price-implied",
    )
    _write(
        analysis_dir / "valuation_model.md",
        _valuation_model_text(),
    )
    _write(analysis_dir / "valuation_audit.md", "Model Reproducibility: PASS")
    _write_json(data_dir / "current_valuation_model_20260630.json", _valuation_packet())
    _write(
        data_dir / "broker_street_consensus_20260630.md",
        "complete broker street consensus",
    )
    _write_json(
        data_dir / "broker_street_consensus_20260630.json",
        _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.2),
    )
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


def test_evaluate_research_case_quality_flags_shallow_industry_pass(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "shallow-industry-case"
    _gate_runner_case(case_dir, industry=True)
    _write(case_dir / "analysis/growth_earnings_model.md", "AI demand is strong.")
    _write_json(
        case_dir / "final_signoff.json",
        {
            "case_id": "shallow-industry-case",
            "report_type": "industry-chain",
            "data_cutoff": "2026-06-30",
            "pdf_path": "main.pdf",
            "page_count": 12,
            "publishability_score": 95,
            "verifier_results": {"status": "PASS"},
            "open_s_count": 0,
            "open_a_count": 0,
            "residual_risks": [
                "Customer/order/ASP/utilization evidence remains uneven."
            ],
            "signoff_status": "PASS",
        },
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "growth earnings model depth" and check["passed"] is False
        for check in result["checks"]
    )
    assert any(
        check["name"] == "final sign-off residual risks do not conflict with PASS"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_blocks_pass_with_incomplete_broker_consensus(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "broker-gap-pass-case"
    _gate_runner_case(case_dir, industry=True)
    _write_json(
        case_dir / "data/broker_street_consensus_20260630.json",
        _broker_consensus_packet(source_quality="not_found", valuation_weight=0.0),
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "broker/street consensus complete before PASS sign-off"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_blocks_pass_with_unusable_broker_values(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "broker-unusable-pass-case"
    _gate_runner_case(case_dir, industry=True)
    packet = _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.0)
    row = packet["rows"][0]
    row["target_price"] = "not disclosed"
    row["method"] = "not disclosed"
    row["implied_upside"] = "not disclosed"
    _write_json(case_dir / "data/broker_street_consensus_20260630.json", packet)

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert result["status"] == "blocked"
    assert any(
        check["name"] == "broker/street consensus values usable for valuation anchor"
        and check["passed"] is False
        for check in result["checks"]
    )
    assert any(
        check["name"] == "broker/street consensus complete before PASS sign-off"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_blocks_third_party_consensus_anchor(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "broker-third-party-anchor-case"
    _gate_runner_case(case_dir, industry=True)
    packet = _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.0)
    row = packet["rows"][0]
    row["source_quality"] = "third_party_consensus_aggregate"
    row["valuation_weight"] = 0.0
    _write_json(case_dir / "data/broker_street_consensus_20260630.json", packet)

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert result["status"] == "blocked"
    assert any(
        check["name"]
        == "broker/street positive-weight auditable anchor covers valuation universe"
        and check["passed"] is False
        for check in result["checks"]
    )


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


def test_run_research_gates_blocks_original_pdf_without_target_price(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "gate-broker-unusable-case"
    _gate_runner_case(case_dir)
    packet = _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.0)
    row = packet["rows"][0]
    row["target_price"] = "not disclosed"
    row["method"] = "not disclosed"
    row["implied_upside"] = "not disclosed"
    _write_json(case_dir / "data/broker_street_consensus_20260630.json", packet)
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

    assert completed.returncode != 0
    assert "broker/street consensus values usable for valuation anchor" in completed.stdout


def test_run_research_gates_blocks_third_party_zero_weight_anchor(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "gate-broker-third-party-case"
    _gate_runner_case(case_dir)
    packet = _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.0)
    row = packet["rows"][0]
    row["source_quality"] = "third_party_consensus_aggregate"
    row["valuation_weight"] = 0.0
    _write_json(case_dir / "data/broker_street_consensus_20260630.json", packet)
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

    assert completed.returncode != 0
    assert (
        "broker/street positive-weight auditable anchor covers valuation universe"
        in completed.stdout
    )


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


def test_evaluate_skill_response_cases_cover_research_report_evolution() -> None:
    result = evaluate_skill_response_cases(
        [
            {
                "name": "research_report_feedback_routes_to_evolve",
                "prompt": "The report passed gates but lacks evidence depth and reviewer did not trigger.",
                "response": (
                    "Route this to evolve with single_skill:equity-research, "
                    "research-report-review, supply-chain-research, "
                    "growth-earnings-model, and valuation. Create delta_audit, "
                    "skill_evolution_log, and a mechanical PASS / institutional FAIL regression."
                ),
                "required_terms": [
                    "evolve",
                    "research-report-review",
                    "delta_audit",
                    "skill_evolution_log",
                    "mechanical PASS / institutional FAIL",
                ],
            }
        ]
    )

    assert result["status"] == "excellent"
    assert result["passed_count"] == 1


def _minimal_case(case_dir: Path) -> None:
    (case_dir / "analysis").mkdir(parents=True)
    (case_dir / "data").mkdir()
    _write(case_dir / "research_brief.md", "single-stock report")
    _write(case_dir / "gate_manifest.md", "gate")
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "report_type": "single-stock",
            "depth_gates": [
                "evidence_depth",
                "broker_consensus_depth",
                "model_depth",
                "valuation_depth",
                "ic_readiness",
            ],
        },
    )
    _write(case_dir / "artifact_contract.md", "contract")
    _write_json(
        case_dir / "artifact_contract.json",
        {"artifacts": [_contract_item("analysis/valuation_audit.md")]},
    )
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
    _write(case_dir / "analysis/valuation_model.md", _valuation_model_text())
    _write_json(case_dir / "data/current_valuation_model_20260630.json", _valuation_packet())
    _write(
        case_dir / "data/broker_street_consensus_20260630.md",
        "complete broker street consensus",
    )
    _write_json(
        case_dir / "data/broker_street_consensus_20260630.json",
        _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.2),
    )
    _write(case_dir / "repair_plan_R0_evidence.md", "repair")
    _write_json(case_dir / "repair_plan_R0_evidence.json", {"status": "open"})


def _gate_runner_case(case_dir: Path, *, industry: bool = False) -> None:
    (case_dir / "analysis").mkdir(parents=True)
    (case_dir / "data").mkdir()
    (case_dir / "sources").mkdir()
    (case_dir / "tools").mkdir()
    _write(
        case_dir / "research_brief.md",
        "industry-chain full-chain report" if industry else "single-stock report",
    )
    _write(case_dir / "gate_manifest.md", "gate")
    gate_manifest = {
        "report_type": "industry-chain" if industry else "single-stock",
        "review_cycles": [
            "R0_evidence",
            "R1_model",
            "R2_draft",
            "R3_render_compliance",
            "R4_final_ic",
        ],
        "depth_gates": [
            "evidence_depth",
            "broker_consensus_depth",
            "model_depth",
            "valuation_depth",
            "ic_readiness",
        ],
        "required_artifacts": ["analysis/valuation_audit.md"],
    }
    if industry:
        gate_manifest["coverage_pack"] = "aidc"
        gate_manifest["depth_gates"].append("valuation_coverage_reconciliation")
        gate_manifest["required_artifacts"].extend(
            [
                "analysis/core_candidate_company_cards.md",
                "analysis/valuation_coverage_reconciliation.md",
                "data/valuation_triage_20260630.json",
                "data/core_candidate_valuation_disposition_20260630.json",
            ]
        )
    _write_json(case_dir / "gate_manifest.json", gate_manifest)
    _write(case_dir / "artifact_contract.md", "contract")
    _write_json(
        case_dir / "artifact_contract.json",
        {"artifacts": [_contract_item("analysis/valuation_audit.md")]},
    )
    _write(case_dir / "review_log.md", "Publishability Score: 95")
    _write(case_dir / "final_signoff.md", "signoff")
    _write_json(
        case_dir / "final_signoff.json",
        {
            "case_id": "gate-case",
            "report_type": "industry-chain" if industry else "single-stock",
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
    _write(case_dir / "analysis/valuation_model.md", _valuation_model_text())
    valuation_row_count = 18 if industry else 1
    _write_json(
        case_dir / "data/current_valuation_model_20260630.json",
        _valuation_packet(row_count=valuation_row_count),
    )
    _write(
        case_dir / "data/broker_street_consensus_20260630.md",
        "complete broker street consensus",
    )
    _write_json(
        case_dir / "data/broker_street_consensus_20260630.json",
        _broker_consensus_packet(
            source_quality="original_pdf",
            valuation_weight=0.2,
            row_count=valuation_row_count,
        ),
    )
    if industry:
        _write(case_dir / "analysis/template_brief.md", "aidc coverage pack")
        _write(case_dir / "analysis/full_chain_taxonomy.md", "full chain aidc")
        _write(
            case_dir / "analysis/chain_business_research.md",
            "upstream business downstream business business relationship core technology core revenue business 2026E expectation",
        )
        _write(case_dir / "analysis/core_vs_satellite_universe.md", "core satellite")
        _write(
            case_dir / "analysis/coverage_gap_matrix.md",
            "coverage gap next verification path valuation blocker",
        )
        _write(case_dir / "analysis/supply_chain_model.md", "supply chain")
        _write(
            case_dir / "analysis/company_fundamental_cards.md",
            "cash flow inventory capex debt order certification",
        )
        triage_rows, core_rows = _valuation_coverage_rows()
        _write(
            case_dir / "analysis/core_candidate_company_cards.md",
            "\n".join(f"## {row['company']}\ncore candidate card" for row in core_rows),
        )
        _write(
            case_dir / "analysis/valuation_coverage_reconciliation.md",
            "173 mapped stock-pool triage rows, 58 core candidates, 18 published target-price models",
        )
        _write(
            case_dir / "analysis/value_chain_economics.md",
            "ASP margin capacity utilization order certification valuation credit",
        )
        _write(case_dir / "analysis/chain_earnings_bridge.md", "bridge")
        _write(
            case_dir / "analysis/competitive_landscape.md",
            "global china localization substitution CR3 CR5",
        )
        _write(
            case_dir / "analysis/variant_perception.md",
            "consensus opposing falsification trigger",
        )
        _write(
            case_dir / "analysis/growth_earnings_model.md",
            "base business growth segment unit ASP gross net profit EPS bear bull current-price-implied",
        )
        _write(case_dir / "data/consensus_analysis.md", "source_quality original_pdf")
        _write_json(case_dir / "data/supply_chain_relationships.json", {"rows": []})
        _write_json(case_dir / "data/customer_chain_audit.json", {"rows": []})
        _write_json(
            case_dir / "data/valuation_triage_20260630.json",
            {"rows": triage_rows},
        )
        _write(
            case_dir / "data/valuation_triage_20260630.md",
            "valuation triage",
        )
        _write_json(
            case_dir / "data/core_candidate_valuation_disposition_20260630.json",
            {"rows": core_rows},
        )
        _write(
            case_dir / "data/core_candidate_valuation_disposition_20260630.md",
            "core candidate valuation disposition",
        )
        _write_json(
            case_dir / "data/full_chain_universe_20260630.json",
            {"rows": _full_chain_universe_rows()},
        )
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


def _valuation_model_text() -> str:
    sections = [
        "Final Valuation Table",
        "Three-Tier Targets",
        "Relative / PEG / PSG Comparison",
        "Seasonality Calibration",
        "Next-Quarter Threshold",
        "Method and Assumption Bridge",
        "Market-Expectation Valuation Bridge",
        "Broker/Street Comparison",
        "Market-Implied Sentiment Anchor",
        "Growth Earnings Dependency",
        "Full-Chain Classification Dependency",
    ]
    return "\n\n".join(f"## {section}\ncurrent share market cap broker Street market-implied weight target upside" for section in sections)


def _valuation_packet(*, row_count: int = 1) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for index in range(1, row_count + 1):
        current_price = 10.0 + index
        final_target = current_price * 1.1
        rows.append(
            {
                "ticker": f"{index:06d}",
                "company": f"Fixture Company {index:03d}",
                "current_price": current_price,
                "price_date": "2026-06-30",
                "shares_100mn": 100.0,
                "market_cap_100mn_cny": current_price * 100.0,
                "revenue_2026e_100mn": 200.0 + index,
                "np_2026e_100mn": 20.0 + index,
                "eps_2026e": 0.2 + index / 100.0,
                "method": "PE",
                "bear": current_price * 0.8,
                "base": current_price,
                "bull": current_price * 1.2,
                "market_implied_anchor": current_price,
                "fundamental_weight": 0.7,
                "market_weight": 0.1,
                "broker_weight": 0.2,
                "final_target": final_target,
                "upside": final_target / current_price - 1,
                "action": "core review",
                "evidence_quality": "A",
            }
        )
    return {"rows": rows}


def _broker_consensus_packet(
    *, source_quality: str, valuation_weight: float, row_count: int = 1
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for index in range(1, row_count + 1):
        rows.append(
            {
                "ticker": f"{index:06d}",
                "broker": "Fixture Securities",
                "report_date": "2026-06-30",
                "rating": "Buy" if source_quality == "original_pdf" else "not disclosed",
                "target_price": 12.0 + index if source_quality == "original_pdf" else "not disclosed",
                "revenue_E": {"2026E": 200.0 + index},
                "net_profit_E": {"2026E": 20.0 + index},
                "EPS_E": {"2026E": 0.2 + index / 100.0},
                "method": "PE" if source_quality == "original_pdf" else "not disclosed",
                "implied_upside": 0.2 if source_quality == "original_pdf" else "not disclosed",
                "source_quality": source_quality,
                "source_path": "sources/broker-reports/2026-06-30/index.md",
                "valuation_weight": valuation_weight,
            }
        )
    return {"rows": rows}


def _valuation_coverage_rows() -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    triage_rows: list[dict[str, object]] = []
    for index in range(1, 174):
        if index <= 58:
            classification = "core_valuation"
        elif index <= 140:
            classification = "satellite_watch"
        else:
            classification = "demand_anchor"
        has_target = index <= 18
        triage_rows.append(
            {
                "company": f"Fixture Company {index:03d}",
                "node_ids": [f"FC{index:03d}"],
                "chain_blocks": [f"block_{index % 8}"],
                "subsegments": [f"segment_{index % 12}"],
                "primary_classification": classification,
                "target_price_status": "target_price_published"
                if has_target
                else "no_target_until_evidence_complete",
                "valuation_disposition": "published_target_price_model"
                if has_target
                else "watchlist_until_evidence_complete",
                "candidate_method": "PE/SOTP with order and margin validation",
                "evidence_gap": "customer/order/ASP evidence requires verification",
                "next_verification_path": "collect official filings and broker evidence",
                "upgrade_trigger": "official revenue split and customer/order evidence",
                "existing_target_price_model": has_target,
            }
        )
    core_rows = [
        row for row in triage_rows if row["primary_classification"] == "core_valuation"
    ]
    return triage_rows, core_rows


def _full_chain_universe_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for index in range(1, 9):
        rows.append(
            {
                "node_type": "demand_anchor" if index == 8 else "listed",
                "chain_block": f"block_{index}",
                "subsegment": f"segment_{index}",
                "evidence_status": "verified",
                "source_count": 1,
                "classification": "core_valuation"
                if index <= 4
                else "satellite_watch",
                "valuation_status": "conditional valuation",
                "next_verification_path": "collect official filings",
            }
        )
    return rows


def _write(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _contract_item(path: str) -> dict[str, object]:
    return {
        "path": path,
        "required_fields": ["path", "owner_skill", "minimum_depth"],
        "minimum_depth": "field-level gate fixture",
        "blocking_conditions": ["missing required fields", "shallow artifact"],
        "reviewer_cycle": "R0_evidence",
        "verifier_check": "evaluate_research_case_quality",
    }
