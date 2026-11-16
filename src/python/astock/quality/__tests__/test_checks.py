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


def test_evaluate_research_case_quality_blocks_house_view_as_broker_anchor(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "house-view-as-broker-anchor-case"
    _gate_runner_case(case_dir)
    packet = _broker_consensus_packet(source_quality="original_pdf", valuation_weight=1.0)
    row = packet["rows"][0]
    row["broker"] = "AStock House View"
    row["source_quality"] = "house_model_auditable"
    row["source_path"] = "analysis/valuation_model.md"
    _write_json(case_dir / "data/broker_street_consensus_20260630.json", packet)

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "broker/street external positive anchor covers valuation universe"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_blocks_shallow_single_stock_model(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "shallow-single-stock-model-case"
    _gate_runner_case(case_dir)
    _write(
        case_dir / "analysis/valuation_model.md",
        _valuation_model_text(),
    )
    (case_dir / "analysis/segment_valuation_model.md").unlink()
    (case_dir / "analysis/secondary_market_analysis.md").unlink()

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "single-stock valuation model institutional depth"
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


def test_evaluate_research_case_quality_ignores_generic_coverage_pack_metadata(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "multi-asset-candidate-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "report_type": "domestic_multi_asset_personal_strategy_research",
            "coverage_pack": "custom_domestic_five_etf_dynamic_candidate",
            "review_cycles": ["R0_evidence", "R4_final_ic"],
            "depth_gates": [
                "evidence_depth",
                "broker_consensus_depth",
                "model_depth",
                "valuation_depth",
                "ic_readiness",
            ],
            "required_artifacts": ["analysis/valuation_audit.md"],
        },
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["requires_industry_chain"] is False


def test_evaluate_research_case_quality_accepts_research_only_strategic_signoff(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "strategic-allocation-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "case_profile": "strategic_allocation",
            "report_type": "strategic_allocation_income_target_research_note",
            "depth_gates": [
                "evidence_depth",
                "model_depth",
                "allocation_model_depth",
                "risk_tax_depth",
                "product_structure_depth",
                "scope_control_depth",
            ],
            "strategy_controls": {
                "research_universe_mode": "open_with_item_level_admission",
                "research_universe_policy": "open T1 direct equities, ETFs, public REITs, sovereign and cash tools; T2/T3/T4 gated",
                "initial_direct_stock_weight": 0.0,
                "direct_stock_aggregate_cap": None,
                "direct_stock_single_issuer_cap": None,
                "issuer_target_price_policy": "required_for_each_named_T3_direct_equity",
                "named_t3_direct_equity_count": 0,
                "named_t3_direct_equity_tickers": [],
                "reit_initial_weight": 0.0,
                "cash_objective_required": False,
            },
            "required_artifacts": ["data/portfolio_return_model_20260812.json"],
        },
    )
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        {
            "model_type": "strategic allocation planning range; no point forecast",
            "active_base_core": [
                {"asset": "eligible_protected_liquidity", "weight": 1.0}
            ],
            "cash_ledger_and_accounting": {
                "eligible_receipt_types": ["settled interest"],
                "not_receipt_types": ["asset sale", "unrealized gain", "NAV accretion", "external contribution"],
                "capital_repayment_like_component": "flag and exclude from investment return until resolved",
            },
            "total_return_measurement": {
                "formula": "time-weighted return",
                "reinvestment_rule": "do not double count",
                "cash_receipt_accounting_rule": "count each receipt once",
            },
            "cash_distribution_policy": {
                "automatic_reinvestment": False,
                "mandatory_retention": False,
            },
            "return_evidence": {
                "implementation_status": "BLOCKED_PENDING_FORMAL_TEST",
                "formal_test_requirement": "point-in-time total-return backtest",
                "benchmark_requirement": "risk-matched benchmark",
            },
            "risk_budget": {
                "implementation_status": "NOT_APPROVED_PENDING_IC",
                "approval_requirement": "investment-committee approval",
                "loss_limit": "explicit maximum drawdown budget",
            },
            "activation_controls": {
                "direct_equities": {
                    "initial_weight": 0.0,
                    "aggregate_cap": None,
                    "single_issuer_cap": None,
                    "current_model_treatment": "open_research_universe_no_named_candidate_or_approved_weight",
                    "required_independent_review": [
                        "company_industry",
                        "audited_financials",
                        "EPS_bridge",
                        "valuation",
                        "cash_coverage",
                        "invalidation",
                        "liquidity",
                        "overlap",
                    ],
                },
                "public_reits": {
                    "initial_weight": 0.0,
                    "aggregate_cap": None,
                    "required_checks": ["liquidity"],
                    "inactive_behavior": "remain in protected liquidity",
                }
            },
        },
    )
    _write_json(
        case_dir / "final_signoff.json",
        {
            "signoff_status": "RESEARCH_FRAMEWORK_PASS",
            "framework_status": "PASS",
            "implementation_status": "NOT_APPROVED",
            "live_execution_authorized": False,
            "implementation_gates": {
                "return_evidence": "BLOCKED_PENDING_FORMAL_TEST",
                "risk_budget": "NOT_APPROVED_PENDING_IC",
                "suitability": "NOT_APPROVED_PENDING_CLIENT_FACTS",
                "execution": "NOT_AUTHORIZED",
            },
            "execution_eligibility": {
                "status": "NOT_RUN",
                "q": 0,
                "live_execution_authorized": False,
            },
            "material_claim_disclosure": {
                "return_target_not_guarantee": True,
                "cash_objective_not_required": True,
                "return_evidence_not_sufficient_for_implementation": True,
                "risk_budget_not_approved": True,
                "implementation_not_authorized": True,
            },
            "decision": "Research framework pass only; return target is not guaranteed and implementation is not approved.",
            "residual_risks": [
                "Formal return evidence is pending; the risk budget is not approved and live execution is not authorized."
            ],
        },
    )
    _write_json(
        case_dir / "research_workflow_eval.json",
        {
            "quality": {
                "implementation_status": "NOT_APPROVED",
            }
        },
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is True
    assert any(
        check["name"]
        == "strategic allocation research-framework sign-off status pass"
        and check["passed"] is True
        for check in result["checks"]
    )


def test_single_objective_strategy_rejects_legacy_cash_target_disclosure(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "single-objective-disclosure-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    _write_json(case_dir / "gate_manifest.json", _open_universe_strategic_manifest())
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        _open_universe_strategic_return_model(),
    )
    signoff = _research_only_strategic_signoff()
    disclosure = signoff["material_claim_disclosure"]
    assert isinstance(disclosure, dict)
    disclosure.pop("cash_objective_not_required")
    disclosure["cash_target_not_guarantee"] = True
    _write_json(case_dir / "final_signoff.json", signoff)
    _write_json(
        case_dir / "research_workflow_eval.json",
        {"quality": {"implementation_status": "NOT_APPROVED"}},
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "strategic allocation material claims are explicitly disclosed"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_blocks_strategic_implementation_approval(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "strategic-allocation-live-claim"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "case_profile": "strategic_allocation",
            "publication_status": "research_framework_pass_implementation_not_approved",
            "depth_gates": [
                "evidence_depth",
                "model_depth",
                "allocation_model_depth",
                "risk_tax_depth",
                "product_structure_depth",
                "scope_control_depth",
            ],
            "strategy_controls": {
                "initial_direct_stock_weight": 0.0,
                "direct_stock_aggregate_cap": 0.0,
                "direct_stock_single_issuer_cap": 0.0,
                "issuer_target_price_policy": "none",
                "reit_initial_weight": 0.0,
                "cash_objective_required": False,
            },
            "required_artifacts": ["data/portfolio_return_model_20260812.json"],
        },
    )
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        {
            "model_type": "strategic allocation planning range; no point forecast",
            "active_base_core": [{"asset": "cash", "weight": 1.0}],
            "cash_ledger_and_accounting": {
                "eligible_receipt_types": ["interest"],
                "not_receipt_types": ["asset sale", "unrealized gain", "NAV accretion", "external contribution"],
                "capital_repayment_like_component": "flag and exclude from investment return until resolved",
            },
            "total_return_measurement": {
                "formula": "time-weighted return",
                "reinvestment_rule": "no double count",
                "cash_receipt_accounting_rule": "count each receipt once",
            },
            "cash_distribution_policy": {
                "automatic_reinvestment": False,
                "mandatory_retention": False,
            },
            "return_evidence": {
                "implementation_status": "BLOCKED_PENDING_FORMAL_TEST",
                "formal_test_requirement": "formal test",
                "benchmark_requirement": "benchmark",
            },
            "risk_budget": {
                "implementation_status": "NOT_APPROVED_PENDING_IC",
                "approval_requirement": "IC approval",
                "loss_limit": "drawdown limit",
            },
            "activation_controls": {
                "public_reits": {
                    "initial_weight": 0.0,
                    "required_checks": ["liquidity"],
                    "inactive_behavior": "protected liquidity",
                }
            },
        },
    )
    _write_json(
        case_dir / "final_signoff.json",
        {
            "signoff_status": "RESEARCH_FRAMEWORK_PASS",
            "framework_status": "PASS",
            "implementation_status": "APPROVED",
            "live_execution_authorized": True,
            "implementation_gates": {
                "return_evidence": "BLOCKED_PENDING_FORMAL_TEST",
                "risk_budget": "NOT_APPROVED_PENDING_IC",
                "suitability": "NOT_APPROVED_PENDING_CLIENT_FACTS",
                "execution": "NOT_AUTHORIZED",
            },
            "execution_eligibility": {
                "status": "NOT_RUN",
                "q": 0,
                "live_execution_authorized": False,
            },
            "material_claim_disclosure": {
                "return_target_not_guarantee": True,
                "cash_objective_not_required": True,
                "return_evidence_not_sufficient_for_implementation": True,
                "risk_budget_not_approved": True,
                "implementation_not_authorized": True,
            },
            "decision": "Research framework pass only; return is not guaranteed and implementation is not approved.",
            "residual_risks": [
                "Formal return evidence is pending; the risk budget is not approved and live execution is not authorized."
            ],
        },
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "strategic allocation implementation explicitly not approved"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_accepts_open_universe_research_only_strategy(
    tmp_path: Path,
) -> None:
    """Open research eligibility must not be mistaken for live allocation."""

    case_dir = tmp_path / "open-universe-strategic-allocation-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    _write_json(
        case_dir / "gate_manifest.json",
        _open_universe_strategic_manifest(),
    )
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        _open_universe_strategic_return_model(),
    )
    _write_json(case_dir / "final_signoff.json", _research_only_strategic_signoff())
    _write_json(
        case_dir / "research_workflow_eval.json",
        {"quality": {"implementation_status": "NOT_APPROVED"}},
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is True
    assert any(
        check["name"]
        == "strategic allocation open research universe has item-level direct-equity admission"
        and check["passed"] is True
        for check in result["checks"]
    )
    assert any(
        check["name"]
        == "strategic allocation direct-equity dossier is complete before T3"
        and check["passed"] is True
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_blocks_open_universe_without_direct_equity_dossier(
    tmp_path: Path,
) -> None:
    case_dir = tmp_path / "open-universe-missing-dossier-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    _write_json(case_dir / "gate_manifest.json", _open_universe_strategic_manifest())
    model = _open_universe_strategic_return_model()
    model["activation_controls"]["direct_equities"]["required_independent_review"] = [
        "current_price_valuation"
    ]
    _write_json(case_dir / "data/portfolio_return_model_20260812.json", model)
    _write_json(case_dir / "final_signoff.json", _research_only_strategic_signoff())
    _write_json(
        case_dir / "research_workflow_eval.json",
        {"quality": {"implementation_status": "NOT_APPROVED"}},
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"]
        == "strategic allocation direct-equity dossier is complete before T3"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_requires_issuer_packets_for_named_open_t3_direct_equity(
    tmp_path: Path,
) -> None:
    """A named T3 direct issuer cannot inherit the q=0 universe exemption."""

    case_dir = tmp_path / "open-universe-named-t3-direct-equity-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    manifest = _open_universe_strategic_manifest()
    manifest["strategy_controls"]["named_t3_direct_equity_count"] = 1
    manifest["strategy_controls"]["named_t3_direct_equity_tickers"] = ["600000"]
    _write_json(case_dir / "gate_manifest.json", manifest)
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        _open_universe_strategic_return_model(),
    )
    _write_json(case_dir / "final_signoff.json", _research_only_strategic_signoff())
    _write_json(
        case_dir / "research_workflow_eval.json",
        {"quality": {"implementation_status": "NOT_APPROVED"}},
    )
    for rel in (
        "data/current_valuation_model_20260630.json",
        "data/broker_street_consensus_20260630.json",
        "data/broker_street_consensus_20260630.md",
    ):
        (case_dir / rel).unlink()

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"] == "valuation model structured rows present"
        and check["passed"] is False
        for check in result["checks"]
    )
    assert any(
        check["name"] == "broker/street consensus json present"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_reconciles_every_named_open_t3_direct_equity(
    tmp_path: Path,
) -> None:
    """A direct-equity count alone cannot hide an unrepresented T3 issuer."""

    case_dir = tmp_path / "open-universe-t3-registry-reconciliation-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    manifest = _open_universe_strategic_manifest()
    manifest["strategy_controls"]["named_t3_direct_equity_count"] = 2
    manifest["strategy_controls"]["named_t3_direct_equity_tickers"] = [
        "000001",
        "000002",
    ]
    _write_json(case_dir / "gate_manifest.json", manifest)
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        _open_universe_strategic_return_model(),
    )
    _write_json(case_dir / "final_signoff.json", _research_only_strategic_signoff())
    _write_json(
        case_dir / "research_workflow_eval.json",
        {"quality": {"implementation_status": "NOT_APPROVED"}},
    )
    _write_json(
        case_dir / "data/current_valuation_model_20260630.json",
        _valuation_packet(row_count=1),
    )
    _write_json(
        case_dir / "data/broker_street_consensus_20260630.json",
        _broker_consensus_packet(source_quality="original_pdf", valuation_weight=0.2),
    )
    for packet in (
        case_dir / "data/current_valuation_model_20260630.json",
        case_dir / "data/broker_street_consensus_20260630.json",
    ):
        payload = json.loads(packet.read_text(encoding="utf-8"))
        payload["rows"][0]["ticker"] = "000001"
        _write_json(packet, payload)

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"]
        == "strategic named T3 direct-equity registry reconciles to valuation universe"
        and check["passed"] is False
        for check in result["checks"]
    )
    assert any(
        check["name"]
        == "strategic named T3 direct-equity registry reconciles to broker/Street universe"
        and check["passed"] is False
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_rejects_spoofed_open_t3_issuer_policy(
    tmp_path: Path,
) -> None:
    """Substring matches must not turn a non-policy into an admission policy."""

    case_dir = tmp_path / "open-universe-spoofed-issuer-policy-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    manifest = _open_universe_strategic_manifest()
    manifest["strategy_controls"]["issuer_target_price_policy"] = "not_required_for_t3"
    _write_json(case_dir / "gate_manifest.json", manifest)
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        _open_universe_strategic_return_model(),
    )
    _write_json(case_dir / "final_signoff.json", _research_only_strategic_signoff())
    _write_json(
        case_dir / "research_workflow_eval.json",
        {"quality": {"implementation_status": "NOT_APPROVED"}},
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is False
    assert any(
        check["name"]
        == "strategic allocation open research universe has item-level direct-equity admission"
        and check["passed"] is False
        for check in result["checks"]
    )
    assert any(
        check["name"] == "broker/street consensus json present"
        and check["passed"] is True
        for check in result["checks"]
    )


def test_evaluate_research_case_quality_keeps_legacy_strategic_pass_compatible(
    tmp_path: Path,
) -> None:
    """The new framework schema must not break a closed-universe legacy memo."""

    case_dir = tmp_path / "legacy-strategic-allocation-case"
    _minimal_case(case_dir)
    _write_json(
        case_dir / "review_findings_R4_final_ic.json",
        {"findings": [{"severity": "B", "status": "closed"}]},
    )
    _write_json(
        case_dir / "gate_manifest.json",
        {
            "case_profile": "strategic_allocation",
            "depth_gates": [
                "evidence_depth",
                "model_depth",
                "allocation_model_depth",
                "risk_tax_depth",
                "product_structure_depth",
                "scope_control_depth",
            ],
            "strategy_controls": {
                "initial_direct_stock_weight": 0.0,
                "direct_stock_aggregate_cap": 0.15,
                "direct_stock_single_issuer_cap": 0.05,
                "issuer_target_price_policy": "none",
                "reit_initial_weight": 0.0,
            },
            "required_artifacts": ["data/portfolio_return_model_20260812.json"],
        },
    )
    _write_json(
        case_dir / "data/portfolio_return_model_20260812.json",
        {"model_type": "strategic allocation planning range; no point forecast"},
    )
    _write_json(
        case_dir / "final_signoff.json",
        {"signoff_status": "PASS", "publishability_score": 93, "residual_risks": []},
    )

    result = evaluate_research_case_quality(case_dir)

    assert result["publishable"] is True
    assert all(
        check["name"]
        != "strategic allocation direct-equity dossier is complete before T3"
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
            {
                "name": "explicit_no_execution",
                "response": "This paper portfolio does not place orders through a broker.",
                "required_terms": ["paper portfolio"],
            },
            {
                "name": "explicit_chinese_no_execution",
                "response": "这是研究与纸面组合方案，不会 place order、submit order；不会执行券商交易。",
                "required_terms": ["纸面组合"],
            },
            {
                "name": "chinese_contrast_violation",
                "response": "不会 place order，但会 submit order。",
                "required_terms": [],
            },
        ]
    )
    cases = {item["name"]: item for item in result["cases"]}

    assert result["status"] == "weak"
    assert cases["boundary_ok"]["passed"] is True
    assert cases["boundary_violation"]["passed"] is False
    assert "place order" in cases["boundary_violation"]["forbidden_hits"]
    assert cases["explicit_no_execution"]["passed"] is True
    assert cases["explicit_no_execution"]["forbidden_hits"] == []
    assert cases["explicit_chinese_no_execution"]["passed"] is True
    assert cases["explicit_chinese_no_execution"]["forbidden_hits"] == []
    assert cases["chinese_contrast_violation"]["passed"] is False
    assert cases["chinese_contrast_violation"]["forbidden_hits"] == ["submit order"]


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


def _open_universe_strategic_manifest() -> dict[str, object]:
    return {
        "case_profile": "strategic_allocation",
        "report_type": "strategic_allocation_income_target_research_note",
        "depth_gates": [
            "evidence_depth",
            "model_depth",
            "allocation_model_depth",
            "risk_tax_depth",
            "product_structure_depth",
            "scope_control_depth",
        ],
        "strategy_controls": {
            "research_universe_mode": "open_with_item_level_admission",
            "research_universe_policy": "open T1 research universe across direct equities, ETFs, public REITs, sovereign and cash products; T2/T3/T4 are finite and gated",
            "initial_direct_stock_weight": 0.0,
            "direct_stock_aggregate_cap": None,
            "direct_stock_single_issuer_cap": None,
            "issuer_target_price_policy": "required_for_each_named_T3_direct_equity",
            "named_t3_direct_equity_count": 0,
            "named_t3_direct_equity_tickers": [],
            "reit_initial_weight": 0.0,
            "cash_objective_required": False,
        },
        "required_artifacts": ["data/portfolio_return_model_20260812.json"],
    }


def _open_universe_strategic_return_model() -> dict[str, object]:
    direct_dossier = [
        "company_industry_and_governance_evidence",
        "audited_financials_and_driver_to_EPS_bridge",
        "current_price_bull_base_bear_valuation",
        "dividend_and_free_cash_flow_coverage",
        "catalyst_and_invalidation",
        "free_float_suspension_price_limit_and_liquidity",
        "issuer_group_industry_factor_and_common_risk_mapping",
        "tax_settlement_and_capacity",
    ]
    return {
        "model_type": "strategic allocation planning range; open research universe; no point forecast",
        "active_base_core": [{"asset": "eligible_protected_liquidity", "weight": 1.0}],
        "cash_ledger_and_accounting": {
            "eligible_receipt_types": ["settled interest"],
            "not_receipt_types": ["asset sale", "unrealized gain", "NAV accretion", "external contribution"],
            "capital_repayment_like_component": "flag and exclude from investment return until resolved",
        },
        "total_return_measurement": {
            "formula": "time-weighted return",
            "reinvestment_rule": "do not double count",
            "cash_receipt_accounting_rule": "count each receipt once",
        },
        "cash_distribution_policy": {
            "automatic_reinvestment": False,
            "mandatory_retention": False,
        },
        "return_evidence": {
            "implementation_status": "BLOCKED_PENDING_FORMAL_TEST",
            "formal_test_requirement": "point-in-time cross-asset replay",
            "benchmark_requirement": "frozen B0/B1 benchmark set",
        },
        "risk_budget": {
            "implementation_status": "NOT_APPROVED_PENDING_IC",
            "approval_requirement": "candidate-specific portfolio risk approval",
            "loss_limit": "approved loss budget",
        },
        "activation_controls": {
            "direct_equities": {
                "initial_weight": 0.0,
                "aggregate_cap": None,
                "single_issuer_cap": None,
                "current_model_treatment": "open_research_universe_no_named_candidate_or_approved_weight",
                "required_independent_review": direct_dossier,
            },
            "public_reits": {
                "initial_weight": 0.0,
                "aggregate_cap": None,
                "required_checks": [
                    "current_price",
                    "NAV",
                    "operating_KPI",
                    "liquidity",
                    "debt",
                    "overlap",
                    "tax",
                ],
                "inactive_behavior": "remain in protected liquidity",
            },
        },
    }


def _research_only_strategic_signoff() -> dict[str, object]:
    return {
        "signoff_status": "RESEARCH_FRAMEWORK_PASS",
        "framework_status": "PASS",
        "implementation_status": "NOT_APPROVED",
        "live_execution_authorized": False,
        "implementation_gates": {
            "return_evidence": "BLOCKED_PENDING_FORMAL_TEST",
            "risk_budget": "NOT_APPROVED_PENDING_IC",
            "suitability": "NOT_APPROVED_PENDING_CLIENT_FACTS",
            "execution": "NOT_AUTHORIZED",
        },
        "execution_eligibility": {
            "status": "NOT_RUN",
            "q": 0,
            "live_execution_authorized": False,
        },
        "material_claim_disclosure": {
            "return_target_not_guarantee": True,
            "cash_objective_not_required": True,
            "return_evidence_not_sufficient_for_implementation": True,
            "risk_budget_not_approved": True,
            "implementation_not_authorized": True,
        },
        "decision": "Research framework pass only; return target is not guaranteed and implementation is not approved.",
        "residual_risks": [
            "Formal return evidence is pending; the risk budget is not approved and live execution is not authorized."
        ],
    }


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
    if not industry:
        _write(
            case_dir / "analysis/segment_valuation_model.md",
            "segment SOTP revenue net profit multiple sensitivity validation trigger",
        )
        _write(
            case_dir / "analysis/secondary_market_analysis.md",
            "price volume turnover drawdown relative performance valuation crowding support resistance seat institutional northbound financing trading style hot-money fund attitude trend swing",
        )
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
