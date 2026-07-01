# Artifact Contract

| Artifact | Owner skill | Stage | Required for | Required fields | Blocking |
|---|---|---|---|---|---|
| research_brief.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/template_brief.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| data/source_registry.json | equity-research | workflow | publication gate | source_id, source_type, source_quality, evidence_tier, limitations | True |
| data/claim_audit.json | equity-research | workflow | publication gate | claim, source type, confidence, used in valuation, adopted wording | True |
| source_exhaustion_log.json | equity-research | workflow | publication gate | probe_id, reason_unresolved, next_verification_path, blocks_valuation | True |
| data/blocked_core_candidate_report_collection_20260701.json | equity-research | workflow | publication gate | ticker, company, reports_archived, best_evidence_score, field_summary, source_path | True |
| data/source_exhausted_official_filing_collection_20260701.json | equity-research | workflow | publication gate | ticker, company, filings_archived, best_evidence_score, field_summary, source_path | True |
| data/proxy_field_official_filing_collection_20260701.json | equity-research | workflow | publication gate | ticker, company, proxy_fields_requested, filings_archived, field_summary, proxy_field_direct_hits | True |
| data/residual_proxy_field_audit_20260701.json | equity-research | workflow | publication gate | ticker, company, field, source, remaining_gap, valuation_consequence, next_verification_path | True |
| data/residual_proxy_field_audit_20260701.md | equity-research | workflow | publication gate | ticker, company, field, remaining gap, valuation consequence, next verification | True |
| sources/broker-reports/2026-06-30/index.md | equity-research | workflow | publication gate | broker, title, date, rating, PDF, Text, notes | True |
| data/broker_street_consensus_20260630.json | equity-research | workflow | publication gate | ticker, broker, report_date, rating, target_price, revenue_E, net_profit_E, EPS_E, method, implied_upside, source_quality, source_path | True |
| data/broker_street_consensus_20260630.md | equity-research | workflow | publication gate | ticker, broker, target_price, source_quality, valuation_weight | True |
| data/full_chain_universe_20260630.json | equity-research | workflow | publication gate | node_type, chain_block, evidence_status, classification, valuation_status | True |
| analysis/chain_business_research.md | equity-research | workflow | publication gate | upstream business, downstream business, business relationship, core technology, core revenue business, 2026E expectation | True |
| data/chain_business_matrix_20260630.json | equity-research | workflow | publication gate | upstream_business, downstream_business, business_relationship, core_technology, core_revenue_business, 2026e_expectation | True |
| analysis/full_chain_taxonomy.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/core_vs_satellite_universe.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/coverage_gap_matrix.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/supply_chain_model.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/company_fundamental_cards.md | equity-research | workflow | publication gate | cash flow, inventory, capex, debt, order, certification | True |
| analysis/value_chain_economics.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/chain_earnings_bridge.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| data/supply_chain_relationships.json | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| data/customer_chain_audit.json | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/growth_earnings_model.md | equity-research | workflow | publication gate | base business, growth segment, unit, ASP, gross profit, net profit, EPS, bear/base/bull, current-price-implied | True |
| analysis/segment_forecast_bridge.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/implied_growth_sensitivity.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| data/growth_driver_model.json | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/valuation_model.md | equity-research | workflow | publication gate | Final Valuation Table, Three-Tier Targets, Relative / PEG / PSG Comparison, Seasonality Calibration, Next-Quarter Threshold, Broker/Street Comparison, Market-Implied Sentiment Anchor, Growth Earnings Dependency | True |
| analysis/valuation_audit.md | equity-research | workflow | publication gate | price/share reconciliation, model reproducibility, method fit, broker comparison | True |
| data/current_valuation_model_20260630.json | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| data/core_candidate_extended_market_financials_20260701.json | equity-research | workflow | publication gate | ticker, company, current_price, shares_100mn, market_cap_100mn_cny, revenue_2026e_100mn, np_2026e_100mn, eps_2026e | True |
| data/core_candidate_extended_broker_consensus_20260701.json | equity-research | workflow | publication gate | ticker, broker, report_date, target_price, revenue_E, net_profit_E, EPS_E, source_quality, valuation_weight | True |
| data/core_candidate_extended_valuation_model_20260701.json | equity-research | workflow | publication gate | ticker, company, publication_status, current_price, shares_100mn, market_cap_100mn_cny, revenue_2026e_100mn, np_2026e_100mn, eps_2026e, method, bear, base, bull, final_target, upside, company_specific_disposition | True |
| data/combined_target_valuation_model_20260701.json | equity-research | workflow | publication gate | ticker, company, chain_bucket, current_price, revenue_2026e_100mn, np_2026e_100mn, eps_2026e, method, bear, base, bull, final_target, upside, rating_or_action, evidence_quality, broker_weight, catalyst, invalidation | True |
| data/combined_target_valuation_model_20260701.md | equity-research | workflow | publication gate | Final Valuation Table, Market-Implied Sentiment Anchor, Broker/Street Comparison, Next-Quarter Threshold | True |
| data/combined_broker_street_coverage_20260701.json | equity-research | workflow | publication gate | ticker, company, coverage_bucket, broker, report_date, target_price, revenue_E, net_profit_E, EPS_E, source_quality, broker_weight, weight_policy | True |
| data/combined_broker_street_coverage_20260701.md | equity-research | workflow | publication gate | Coverage bucket, Weight policy, Source quality | True |
| data/valuation_quality_audit_20260701.json | equity-research | workflow | publication gate | status, row_count, broker_coverage_count, issue_count, issues | True |
| data/valuation_quality_audit_20260701.md | equity-research | workflow | publication gate | Status, Target rows, Broker coverage rows, Model Reproducibility | True |
| data/valuation_triage_20260630.json | equity-research | workflow | publication gate | company, primary_classification, target_price_status, valuation_disposition, evidence_gap, next_verification_path | True |
| data/valuation_triage_20260630.md | equity-research | workflow | publication gate | company, primary class, target status, disposition, evidence gap, next verification | True |
| data/core_candidate_valuation_disposition_20260630.json | equity-research | workflow | publication gate | company, chain_blocks, candidate_method, target_price_status, valuation_disposition, residual_proxy_boundary, upgrade_trigger | True |
| data/core_candidate_valuation_disposition_20260630.md | equity-research | workflow | publication gate | company, candidate method, target status, disposition, residual proxy boundary, upgrade trigger | True |
| analysis/core_candidate_company_cards.md | equity-research | workflow | publication gate | chain role, product/process exposure, candidate valuation method, target-price status, field evidence status, residual proxy boundary, evidence gap, upgrade trigger | True |
| analysis/core_candidate_extended_valuation_model.md | equity-research | workflow | publication gate | publication status, current price, 2026E revenue, 2026E EPS, method, target, blocking reason, next verification | True |
| analysis/residual_proxy_field_audit.md | equity-research | workflow | publication gate | ticker, company, field, remaining gap, valuation consequence, next verification | True |
| analysis/valuation_coverage_reconciliation.md | equity-research | workflow | publication gate | full-pool mapped companies, core valuation candidates, published target-price combo, gate consequence | True |
| sections/ch04_supply_chain.tex | equity-research | workflow | publication gate | 算力与存储, 服务器、整柜与网络设备, 光通信, PCB、CCL, 供配电与液冷, AIDC/IDC 运营, 附录证据索引 | True |
| analysis/competitive_landscape.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/variant_perception.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/risk_framework.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/exhibit_plan.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/user_scope_coverage_audit.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| main.tex | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| main.pdf | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| main_current_text.txt | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| review_log.md | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| final_signoff.json | equity-research | workflow | publication gate | owner_skill, stage, required_for, evidence_quality_or_gap | True |
| analysis/delta_audit.json | equity-research | workflow | publication gate | user_correction, original_miss, responsible_skills, prevention_rule_added | True |
| skill_evolution_log.json | equity-research | workflow | publication gate | failure_mode, root_cause, changes_applied, regression_cases, validation_commands | True |
