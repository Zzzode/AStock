# Review Criteria (Per-Chapter)

## Universal Checks (apply to every chapter)

| Priority | Check | Fail Condition |
|----------|-------|----------------|
| S | Data matches verified source | Any number differs from Appendix A |
| S | No internal contradictions | Table X says one thing, Chart Y says another |
| S | Complete coverage | Table claims "18标的" but has only 14 rows |
| S | Full-chain universe complete | Full industry-chain report lacks `data/full_chain_universe_<YYYYMMDD>.md/json`, required coverage-pack blocks, `node_type`, or core/satellite/demand-anchor classification |
| S | Supply-chain skill artifacts complete | Full industry-chain report lacks required supply-chain outputs, coverage gap matrix, or value-chain economics |
| S | Growth earnings skill artifacts complete | High-growth valuation credit lacks required growth-earnings outputs |
| S | Valuation reproducible | `analysis/valuation_audit.md` lacks `Model Reproducibility: PASS` |
| S | Source quality complete | Broker evidence lacks source-quality labels or source-exhaustion log |
| S | Variant perception complete | Missing strongest opposing argument or falsification evidence |
| S | Review lifecycle complete | Missing gate manifest, artifact contract, review findings, repair plan, final sign-off, or open S/A issue closure evidence |
| A | Actionable conclusions | Section ends with data but no "so what" |
| A | Risk disclosures complete | BIS/ESG abbreviated to <5 words |
| B | Formatting consistent | Mixed number formats within same table |

## Chapter-Specific Criteria

### Ch1 (Executive Summary)
- [ ] All numbers here appear identically in detail chapters (single source of truth)
- [ ] Every primary recommendation includes current price, final target price or fair-value range, implied upside/downside, valuation method, and invalidation trigger
- [ ] Ch1 states what to buy or track, why now, key risks, triggers, and which names are satellite/watch-only or demand anchors
- [ ] Catalyst timeline dates are specific (month, not "H2")
- [ ] Risk tickers list is COMPLETE (not missing any high-risk names)
- [ ] Recommendation language is unambiguous

### Ch5 (Quadrant Chart)
- [ ] Every point on scatter = one row in legend table (1:1 mapping)
- [ ] Strategy table company lists match scatter quadrant assignments
- [ ] Coordinates match original analysis (not randomly placed)

### Ch6 (Full Overview Table)
- [ ] All 18 tickers present
- [ ] Star ratings consistent with Ch7 subsection headers
- [ ] Risk annotations include [ESG-Ex] references
- [ ] No company listed without at least one risk/caveat note

### Ch7 (Deep Dive)
- [ ] Layer classification (L0-L5) matches Ch3 architecture diagram
- [ ] Full-chain universe starts broad and then narrows to core valuation pool and satellite watch pool
- [ ] Non-listed, overseas, private, demand-anchor, low-purity, and unavailable nodes are recorded where relevant
- [ ] `analysis/coverage_gap_matrix.md` covers missing chain blocks, sources checked, reason unresolved, next verification path, and valuation blocker status
- [ ] Every covered company has a company card and supply-chain relationship row
- [ ] Customer/platform/order/capacity/certification claims are evidence-labeled or marked `not found`
- [ ] Every company with 4+ stars gets full table treatment
- [ ] ESG red-flag companies (HRF triggers) have prominent red warnings
- [ ] Business relationship descriptions match Ch2 tech stack table

### Ch9 (Valuation)
- [ ] Three-tier table includes ALL 10+ major tickers (not subset)
- [ ] Final valuation summary table includes current price/date, shares, market cap, method, bull/base/bear values, final target/fair-value range, upside/downside, rating/action, catalysts, invalidation, and evidence quality for every investable ticker
- [ ] Any high-growth, AI, order, shipment, ASP, segment-mix, PEG/PSG, or PS/SOTP valuation credit traces to `analysis/growth_earnings_model.md` and `data/growth_driver_model.json`
- [ ] Any industry-chain valuation traces to `analysis/core_vs_satellite_universe.md` and `analysis/value_chain_economics.md`
- [ ] `analysis/valuation_audit.md` has `Model Reproducibility: PASS`
- [ ] Growth model shows base/growth split, unit/order/ASP/proxy, recognized revenue ratio, gross margin, incremental opex, net profit/EPS contribution, scenarios, current-price-implied growth, evidence gap, and valuation credit classification
- [ ] PE × profit = market cap (verify arithmetic for each row)
- [ ] "泡沫度" correctly calculated: (current/base - 1) × 100
- [ ] Upside/downside correctly calculated: (target or midpoint/current - 1) × 100
- [ ] Q2 threshold table has clear "if below → consequence" logic
- [ ] Thor/catalyst timeline has specific dates and amounts

### Ch10 (Competition)
- [ ] `analysis/competitive_landscape.md` covers global/China leaders, CR3/CR5 when available, localization boundary, substitution risk, and source quality
- [ ] All transmission coefficient rows present (8 milestones)
- [ ] κ values sum logic: higher layers ≠ necessarily higher κ
- [ ] Dual-edge section has BOTH positive (3) AND negative (5) factors
- [ ] Same-layer PK table covers all contested positions

### Ch11 (Institutional)
- [ ] Raw data table: 18 tickers × all columns filled
- [ ] Market data is CURRENT (within 7 days of report date)
- [ ] Score arithmetic: component scores sum to total for every row
- [ ] Rating thresholds consistently applied (85+=A, 70-84=B, etc.)
- [ ] Decision matrix assignments consistent with scores

### Ch12 (Risk)
- [ ] 22 factors in table = 22 items in tree diagram (count matches)
- [ ] L4/L3/L2 counts in summary table match actual factor assignments
- [ ] Emergency matrix has RECOVERY conditions (not just exit rules)
- [ ] Radar chart has accompanying action table

### Ch13 (Devil's Advocate)
- [ ] All 7 arguments have: attack + destruction path + falsification table
- [ ] `analysis/variant_perception.md` states market consensus, AStock view, strongest opposing argument, falsification evidence, and monitoring trigger
- [ ] Falsification criteria are SPECIFIC and DATE-BOUND
- [ ] Stress test matrix probabilities sum to 100%
- [ ] Modification suggestions are concrete (not vague "be careful")

### Ch14 (PEG/Seasonality)
- [ ] PEG table includes all major tickers (not just top 5)
- [ ] Seasonal calibration math: Q1 actual ÷ Q1% = full year (verify)
- [ ] Final space table reflects ALL four calibration factors
- [ ] H2 narrative classification covers all relevant tickers

### Appendices
- [ ] Appendix A: all [Ax] references in main text have matching entry
- [ ] Appendix B: ESG scores match source document calculations
- [ ] Appendix C: all technical terms used in report are defined
- [ ] Source appendix distinguishes original PDFs, official pages, abstracts, media reposts, third-party previews, search snippets, corpus gaps, and not-found probes
- [ ] `gate_manifest.md/json` and `artifact_contract.md/json` cover all required artifacts
- [ ] `review_findings_<cycle>.json` has no open S-Level or unwaived A-Level issues
- [ ] `review_log.md` records publishability score; PASS requires score >= 90, final sign-off, generic verifier 39 PASS / 0 FAIL, and industry-chain verifier PASS when applicable
