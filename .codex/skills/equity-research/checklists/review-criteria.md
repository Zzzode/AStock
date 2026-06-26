# Review Criteria (Per-Chapter)

## Universal Checks (apply to every chapter)

| Priority | Check | Fail Condition |
|----------|-------|----------------|
| S | Data matches verified source | Any number differs from Appendix A |
| S | No internal contradictions | Table X says one thing, Chart Y says another |
| S | Complete coverage | Table claims "18标的" but has only 14 rows |
| A | Actionable conclusions | Section ends with data but no "so what" |
| A | Risk disclosures complete | BIS/ESG abbreviated to <5 words |
| B | Formatting consistent | Mixed number formats within same table |

## Chapter-Specific Criteria

### Ch1 (Executive Summary)
- [ ] All numbers here appear identically in detail chapters (single source of truth)
- [ ] Every primary recommendation includes current price, final target price or fair-value range, implied upside/downside, valuation method, and invalidation trigger
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
- [ ] Every company with 4+ stars gets full table treatment
- [ ] ESG red-flag companies (HRF triggers) have prominent red warnings
- [ ] Business relationship descriptions match Ch2 tech stack table

### Ch9 (Valuation)
- [ ] Three-tier table includes ALL 10+ major tickers (not subset)
- [ ] Final valuation summary table includes current price/date, shares, market cap, method, bull/base/bear values, final target/fair-value range, upside/downside, rating/action, catalysts, invalidation, and evidence quality for every investable ticker
- [ ] PE × profit = market cap (verify arithmetic for each row)
- [ ] "泡沫度" correctly calculated: (current/base - 1) × 100
- [ ] Upside/downside correctly calculated: (target or midpoint/current - 1) × 100
- [ ] Q2 threshold table has clear "if below → consequence" logic
- [ ] Thor/catalyst timeline has specific dates and amounts

### Ch10 (Competition)
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
