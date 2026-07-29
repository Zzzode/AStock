# Gate Manifest

- case_id: dongyangguang-600673-20260710
- report_type: single_stock_deep_research_update
- data_cutoff: 2026-07-13 11:33 CST
- coverage_basis: single_stock_not_applicable
- required_skills: ['equity-research', 'valuation', 'growth-earnings-model', 'reports', 'research-report-review', 'exhibit-format-reviewer']
- required_artifacts: ['research_brief.md', 'data/source_registry.md', 'data/source_registry.json', 'data/claim_audit.md', 'data/claim_audit.json', 'data/broker_street_consensus_20260713.md', 'data/broker_street_consensus_20260713.json', 'data/current_valuation_model_20260713.json', 'data/transaction_dilution_model_20260713.json', 'data/compute_contract_bridge_20260713.json', 'data/growth_driver_model.json', 'analysis/house_view.md', 'analysis/template_brief.md', 'analysis/exhibit_plan.md', 'analysis/variant_perception.md', 'analysis/growth_earnings_model.md', 'analysis/segment_forecast_bridge.md', 'analysis/implied_growth_sensitivity.md', 'analysis/value_chain_economics.md', 'analysis/segment_valuation_model.md', 'analysis/secondary_market_analysis.md', 'analysis/delta_audit.md', 'analysis/valuation_model.md', 'analysis/valuation_audit.md', 'analysis/broker_target_trend.md', 'analysis/risk_framework.md', 'source_exhaustion_log.md', 'source_exhaustion_log.json', 'main.tex', 'main.pdf', 'main_current_text.txt', 'review_log.md', 'final_signoff.md', 'final_signoff.json', 'research_workflow_eval.md', 'research_workflow_eval.json']
- review_cycles: ['R0_evidence', 'R1_model', 'R2_draft', 'R3_render_compliance', 'R4_final_ic']
- verifiers: ['tools/verify_research_workspace.py', 'workspace/research/tools/run_research_gates.py', 'astock.capabilities.evaluate_research_case_quality']
- depth_gates: ['evidence_depth', 'broker_consensus_depth', 'model_depth', 'valuation_depth', 'ic_readiness']
- pass_conditions: ['A/B/C official contract PDFs archived', 'transaction dilution and placement sensitivity modeled', 'Qinhuai official operating and valuation data used', 'original-PDF broker targets separated from House values', 'target/upside arithmetic reproducible', '39 local checks and repo research gates pass']
- downgrade_path: Neutral/Hold/Event-driven Watch when upside is below 10% or registration/acceptance remains incomplete.
- pre_publish_self_checklist: {'evidence_depth': 'official transaction, contract, broker and market evidence archived', 'broker_consensus_depth': 'Guojin original target plus Guotou auditable repost', 'model_depth': 'legacy/Qinhuai/compute bridge with dilution', 'valuation_depth': 'scenario, SOTP, Street and market anchors', 'ic_readiness': 'current action, triggers and invalidation present'}
