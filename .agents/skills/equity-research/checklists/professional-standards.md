# Professional Standards Checklist

## Report Formatting

- [ ] Cover page has: title (bilingual), date, data cutoff, version number
- [ ] Table of contents auto-generated and correct (2 XeLaTeX passes)
- [ ] Page headers: report title (left), date (right)
- [ ] Page footers: page number (center), disclaimer (right)
- [ ] Disclaimer page at end with both Chinese and English text

## Number Formatting

- [ ] All monetary values have units (亿元, 万元, $B, $M)
- [ ] PE/PS/PB multiples written as `XX×` (not "XXx" or "XX倍" inconsistently)
- [ ] Percentages always with % sign: +42.96% (not "增长42.96")
- [ ] Value ranges use consistent delimiter: `+107--142%` (en-dash throughout)
- [ ] Large numbers use Chinese units: 1.4万亿 (not 14000亿)
- [ ] Decimals consistent: financial data 2 decimals, growth rates 1-2 decimals

## Valuation Model Standards

- [ ] Every investable or explicitly covered ticker has current price/date, share count, market cap, currency/share class, forecast EPS/net profit, valuation method, bull/base/bear values, final target price or fair-value range, implied upside/downside, rating/action, catalysts, invalidation, and evidence quality
- [ ] `analysis/valuation_audit.md` contains `Model Reproducibility: PASS`
- [ ] Full industry-chain valuation consumes full-chain row, core/satellite classification, and value-chain economics before assigning a target price
- [ ] The reader-facing report includes a final valuation summary table covering the full investable universe
- [ ] Broker target prices are separated from AStock final targets and clearly cited by broker/date/source
- [ ] Upside/downside is calculated from current price: `(target or range midpoint / current price - 1) × 100%`
- [ ] Any ticker without enough data for a defensible target is labeled `insufficient evidence / watchlist only` and is not given an investable recommendation

## Supply-Chain Research Standards

- [ ] Full industry-chain reports include `data/full_chain_universe_<YYYYMMDD>.md/json`, `analysis/full_chain_taxonomy.md`, `analysis/core_vs_satellite_universe.md`, `analysis/coverage_gap_matrix.md`, `analysis/supply_chain_model.md`, `analysis/company_fundamental_cards.md`, `analysis/value_chain_economics.md`, `analysis/chain_earnings_bridge.md`, `data/supply_chain_relationships.md/json`, and `data/customer_chain_audit.md/json`
- [ ] `analysis/template_brief.md` cites the selected industry coverage pack
- [ ] Every full-chain universe row has `node_type`, evidence status, source count, core/satellite/demand-anchor classification, valuation status, and next verification path
- [ ] Every covered ticker has a company card and at least one relationship row
- [ ] Relationship rows include upstream input, product/process, downstream customer/platform/application, confidence, revenue exposure, capacity/certification/order visibility, margin/earnings impact, source, evidence gap, and valuation eligibility
- [ ] Demand anchors are labeled separately and are not presented as proof of upstream revenue
- [ ] Missing customer, order, capacity, certification, or revenue-share evidence is marked `not found` or `not disclosed`, not omitted
- [ ] `analysis/competitive_landscape.md` covers global/China leaders, CR3/CR5 when available, localization boundary, substitution risk, and source quality

## Growth Earnings Model Standards

- [ ] Reports using high-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP valuation credit include `analysis/growth_earnings_model.md`, `analysis/segment_forecast_bridge.md`, `analysis/implied_growth_sensitivity.md`, and `data/growth_driver_model.json`
- [ ] Every applicable ticker has base business versus growth segment split, unit/order/ASP/proxy bridge, recognized revenue ratio, gross margin, incremental opex, net profit/EPS contribution, bear/base/bull cases, evidence gap, and valuation credit classification
- [ ] Current-price-implied growth is shown before final target or fair-value range is interpreted
- [ ] Growth segment upside is not applied to consolidated revenue or profit unless segment purity is proven
- [ ] Generic AI demand, downstream TAM, capacity, or one strong quarter supports only `optionality` or `watchlist only` language unless conversion into revenue, margin, and EPS is evidenced

## Source Governance Standards

- [ ] `data/source_registry.md/json`, `data/claim_audit.md/json`, and `source_exhaustion_log.md/json` exist and are synchronized
- [ ] Broker evidence quality is labeled; abstracts, media reposts, previews, and search snippets are not presented as original broker reports
- [ ] `data/consensus_analysis.md` preserves source quality for ratings, target prices, forecasts, valuation method, and unavailable fields

## Variant Perception Standards

- [ ] `analysis/variant_perception.md` states market consensus, AStock differentiated view, assumption gap, strongest opposing argument, falsification evidence, and monitoring triggers
- [ ] The reader-facing report includes the strongest opposing argument and what would prove the thesis wrong

## Table Standards

- [ ] All tables use booktabs (no vertical lines, \toprule/\midrule/\bottomrule)
- [ ] Every table has numbered caption below
- [ ] Column headers are bold
- [ ] Risk colors used consistently (red=severe, amber=warning, green=positive)
- [ ] Comprehensive tables include ALL tickers in coverage universe (no omissions)
- [ ] Tables that score/rank include a methodology note

## Chart Standards

- [ ] Every chart has numbered caption below
- [ ] Axis labels are readable (not too small)
- [ ] Legend is present and unambiguous
- [ ] Source attribution below chart (tiny font, grey)
- [ ] Radar charts have accompanying "decision table" explaining implications
- [ ] Scatter plots have all points listed in a legend/reference table
- [ ] No overlapping labels (adjust anchor positions)

## Reference System

- [ ] Every factual claim has source citation [Ax] or footnote
- [ ] [Ax] references map to Appendix A entries
- [ ] ESG claims reference [ESG-Ex] codes
- [ ] Appendix A covers all referenced numbers (no orphan references)

## Compliance/Risk Disclosures

- [ ] BIS entity list: full details (date, entities affected, business impact %)
- [ ] CSRC penalties: amount, reason, date, current status
- [ ] Shareholder pledges: exact %, whether at margin call level
- [ ] Official clarifications (澄清公告): quoted with date
- [ ] ST/delisting history: dates and current status
- [ ] Criminal/regulatory: custody (留置), investigation dates

## Language & Tone

- [ ] Analytical, not promotional (no "exciting opportunity" language)
- [ ] Risks stated directly, not buried in footnotes
- [ ] "Bubble" and "overvalued" used without hedging when data supports it
- [ ] Conclusions are actionable (specific: "buy below X", "sell above Y")
- [ ] No unexplained jargon without glossary reference

## Publishability Standards

- [ ] `review_log.md` contains publishability status and 0-100 publishability score
- [ ] `gate_manifest.md/json` and `artifact_contract.md/json` exist and list every required skill, artifact, review cycle, verifier, pass condition, and downgrade path
- [ ] `review_findings_<cycle>.json` and `repair_plan_<cycle>.md/json` exist for every executed cycle
- [ ] PASS requires score >= 90, zero open S-Level issues, zero open unwaived A-Level issues, final sign-off, generic verifier 39 PASS / 0 FAIL, and industry-chain verifier PASS when applicable
- [ ] `final_signoff.md/json` lists verifier results, open issue counts, waivers, residual risks, data cutoff, PDF path, and page count
- [ ] If the user flagged a material miss, `analysis/delta_audit.md` maps user correction, original miss, responsible skill/role, missing gate, files changed, and prevention rule
