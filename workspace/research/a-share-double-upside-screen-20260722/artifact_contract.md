# Artifact Contract

| Artifact | Owner | Stage | Required fields / sections | Minimum depth | Blocking conditions | Review | Verifier |
|---|---|---|---|---|---|---|---|
| research_brief.md | equity-research | Intake | objective, cutoff, universe, ranking method, double definition, downgrade path | explicit investable boundary | missing price date or double definition | R0 | existence |
| analysis/template_brief.md | template-benchmark-analyst | Intake | dashboard, chapter sequence, exhibits, archetype, custom pack | first-page decision design | missing benchmark or reader behavior | R0 | contract |
| data/verified_market_data.md | data-verifier | Evidence | price, timestamp, source, quality, warnings | all deep names plus controls | stale or missing current price | R0/R1 | price reconciliation |
| data/verified_financials.md | data-verifier | Evidence | annual, Q1, H1 preview, cash flow, shares | all deep names | unsupported earnings denominator | R0/R1 | source trace |
| data/source_registry.md/json | source-governance | Evidence | id, type, date, path, URL, tier, use, limitation | every material claim | weak evidence presented as primary | R0 | JSON parse |
| data/claim_audit.md/json | source-governance | Evidence | claim, evidence, source, confidence, model impact, gap | every target-driving claim | rumor or unsupported target input | R0 | JSON parse |
| source_exhaustion_log.md/json | source-governance | Evidence | probe, result, gap, next path, valuation consequence | every failed Street/official probe | silent source gap | R0 | JSON parse |
| data/broker_street_consensus_20260722.md/json | reports | Evidence | ticker, broker, date, rating, target, forecasts, method, quality, weight | every explicit current point target; report_catalog covers zero-target rows | weak source given positive weight | R0/R1 | broker gate |
| analysis/company_fundamental_cards.md | fundamental-analyst | Synthesis | business driver, financials, cash, moat, risk, eligibility | one card per deep ticker | shallow or missing company bridge | R0/R1 | contract |
| analysis/value_chain_economics.md | supply-chain-analyst | Synthesis | price/ASP proxy, margin, capacity, utilization, orders, valuation credit | operating driver for each deep ticker | capacity or cycle claim without conversion logic | R1 | depth terms |
| analysis/growth_earnings_model.md | growth-earnings-modeler | Modeling | base/growth split, units/proxy, revenue, margin, EPS, scenarios, implied growth | each high-growth/cyclical ticker | generic theme converted to EPS | R1 | growth gate |
| data/growth_driver_model.json | growth-earnings-modeler | Modeling | driver rows and bear/base/bull assumptions | all applicable tickers | missing reproducible scenario math | R1 | JSON parse |
| analysis/house_view.md | house-view-analyst | Synthesis | ranked conclusion, why now, false positives, monitoring | independent AStock thesis | broker-summary voice | R2 | contract |
| analysis/variant_perception.md | house-view-analyst | Synthesis | consensus, house view, strongest opposition, falsification | all primary names | no serious counter-case | R2 | contract |
| analysis/valuation_model.md | valuation-specialist | Modeling | all valuation skill sections and final table | bear/base/bull for every deep ticker | method mismatch or missing current target | R1/R2 | valuation gate |
| analysis/valuation_audit.md | valuation-auditor | Modeling | arithmetic, shares, market cap, weights, fake precision, reproducibility | line-by-line recomputation | Model Reproducibility not PASS | R1 | exact marker |
| data/current_valuation_model_20260722.json | valuation-specialist | Modeling | all required structured row fields | one row per formal positive-weight ticker | missing field, eligibility conflict, or arithmetic mismatch | R1 | row gate |
| data/zero_weight_valuation_model_20260722.json | valuation-specialist | Modeling | ticker, current price, diagnostic scenarios, source quality, missing fields, hard gate, recovery status, action | one row for every remaining deep ticker | missing coverage or accidental positive weight | R1 | zero-weight row gate |
| analysis/risk_framework.md | risk-analyst | Analysis | risk matrix, probability, impact, trigger, action | downside and year-end timing risk | generic risk list | R2 | contract |
| analysis/exhibit_plan.md | exhibit-architect | Draft | claim, exhibit, source, location, decision use | every strong conclusion mapped | unsupported core conclusion | R2 | contract |
| analysis/narrative_blueprint.md | latex-writer | Draft | chapter question, evidence, synthesis, reader action | prose-led sequence | table-stack structure | R2 | contract |
| main.tex/main.pdf | latex-writer | Draft/Render | dashboard, screen, models, risks, sources | 25-35 readable pages | compile, glyph, clipping, or source errors | R2/R3 | PDF verifier |
| review_findings and repair plans | research-report-reviewer | Review | severity, owner, evidence, fix, status | R0-R4 lifecycle | open S/A issues | R0-R4 | lifecycle gate |
| final_signoff.md/json | research-report-reviewer | Sign-off | score, verifier results, open counts, residual risks, status | IC-consistent final conclusion | material residual risk conflicts with PASS | R4 | sign-off gate |
