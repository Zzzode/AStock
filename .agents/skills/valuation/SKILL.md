---
name: valuation
description: Complete AStock valuation workflow for equity research. Use when building or auditing current-price-based valuation models, target prices, fair-value ranges, upside/downside, business-model matched methods, market-implied expectations, sentiment anchors, broker/Street comparisons, or whenever equity-research, research-report-review, latex-writer, or a valuation agent needs valuation outputs.
---

# Valuation

## Purpose

Build and audit AStock valuation packages. This skill is the authoritative valuation gate for research reports; do not create ad hoc valuation tables in an equity-research workflow when this skill applies.

## Required Inputs

- Ticker universe with share class and currency.
- Verified market data: current price/date, volume or trading value when available, shares or data needed to derive shares, market cap.
- Verified financial data: revenue, net profit, EPS, margins, equity/BPS, quarterly and annual history.
- Source registry and claim audit for product exposure, customer/order evidence, capacity, pricing, and broker/Street evidence.
- Broker or public consensus material when available; if unavailable, publish `not disclosed` fields with source-quality labels.
- Full-chain and supply-chain research outputs for full industry-chain reports: `data/full_chain_universe_<YYYYMMDD>.md/json`, `analysis/full_chain_taxonomy.md`, `analysis/core_vs_satellite_universe.md`, `analysis/coverage_gap_matrix.md`, `analysis/supply_chain_model.md`, `analysis/company_fundamental_cards.md`, `analysis/value_chain_economics.md`, `analysis/chain_earnings_bridge.md`, `data/supply_chain_relationships.md/json`, and `data/customer_chain_audit.md/json`.
- Growth earnings outputs when high-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP valuation credit is used: `analysis/growth_earnings_model.md`, `analysis/segment_forecast_bridge.md`, `analysis/implied_growth_sensitivity.md`, and `data/growth_driver_model.json`.
- House view and industry-chain classification so valuation methods match business economics.

If an input is missing, either collect it through the project capability layer or mark it explicitly as `not disclosed` / `insufficient evidence`. Do not fill broker, order, customer, or consensus fields with AStock assumptions.

## Workflow

1. **Classify each ticker before valuing it.**
   - Identify lifecycle, profit quality, cyclicality, asset intensity, segment mix, order durability, and evidence quality.
   - Select a primary method and at least one secondary check. Use PE/PEG for durable earnings, cycle-adjusted PE or EV/EBITDA for cyclicals, PB/ROE or EV/EBITDA for asset-heavy names, PS/EV-Sales for revenue-no-profit names, and SOTP/blended methods for mixed businesses.
   - Never force a heterogeneous industry chain into one PE template.
   - For full industry-chain reports, use the full-chain universe and supply-chain package to decide whether a ticker is a core beneficiary, satellite watch name, demand anchor, low-purity name, unavailable node, or thematic diffusion name.
   - Value only core valuation names unless the satellite section states exactly what evidence is missing and why the ticker remains watchlist-only.
   - Never value demand anchors as upstream beneficiaries.
   - If the valuation case depends on AI, high-growth segment mix, shipments, units, ASP, order/backlog conversion, customer allocation, or "sales/orders will double", consume the growth earnings package before assigning any growth multiple or upside.

2. **Normalize the financial denominator.**
   - Show 2026E revenue, 2026E net profit/EPS, expected growth, and the bridge from reported quarters to the forecast.
   - For high-growth stories, separate base business and growth segment economics using `analysis/segment_forecast_bridge.md`; do not apply high-growth multiples to consolidated revenue unless segment purity is proven.
   - Apply seasonality calibration before calling anything cheap or expensive.
   - If the denominator is near-zero, temporary, project-cycle distorted, or unsupported, switch methods or mark the ticker `insufficient evidence / watchlist only`.

3. **Build scenario valuation.**
   - Bear case: narrative breaks, lower multiple, lower margin, weaker price or order conversion, or cycle floor.
   - Base case: AStock cold assessment using the ticker's business-model driver.
   - Bull case: sell-side or market upside logic; disclose target-price bias and required validation.
   - When growth earnings outputs exist, scenario values must use the driver sensitivities for units/shipments, ASP, recognized revenue ratio, gross margin, incremental opex, tax, EPS, and valuation multiple.
   - Industry-chain scenario values must reference `analysis/value_chain_economics.md`: value amount, ASP/price proxy, margin pool, supply/demand, capacity, utilization/yield, certification, order visibility, and price pass-through.
   - Always show bubble degree: `(current / base target - 1) * 100%`.

4. **Build the multi-anchor target.**
   - Final target = fundamental/intrinsic value * Wf + market-implied sentiment anchor * Wm + broker/Street anchor * Ws.
   - Show current-implied PE/PS/PB/EV multiple, trading-value or momentum context where available, market anchor, broker anchor, final weights, final target, premium/discount, and embedded expectation gap.
   - For high-growth stories, reconcile the market-implied sentiment anchor to `analysis/implied_growth_sensitivity.md`: what current price already implies for growth revenue, margin, EPS, duration, shipments, ASP, or order conversion.
   - Do not publish a mechanical sell/reduce action only because intrinsic value is below price when observable market evidence supports a sentiment premium. Label the premium and define what would break it.

5. **Translate valuation into research action.**
   - Use action labels that describe behavior: `core review`, `pullback entry`, `market-supported watch`, `event-driven validation`, `watchlist only`, `sentiment premium breaking`, or `high valuation risk`.
   - Include catalysts, invalidation triggers, and next-quarter thresholds.
   - Tie catalysts and invalidation to `analysis/chain_earnings_bridge.md` and `data/supply_chain_relationships.md` when those files exist.
   - Tie high-growth catalysts, invalidation triggers, and next-quarter thresholds to `analysis/growth_earnings_model.md` and `data/growth_driver_model.json` when those files exist.
   - No investable action is allowed without a current-price-based target or fair-value range and implied upside/downside.

6. **Audit before release.**
   - Recalculate market cap, EPS, PE/PS/PB, target price, upside/downside, scenario bands, and weights.
   - Recalculate the final valuation table from disclosed inputs and write `Model Reproducibility: PASS` only if every current price, share count, market cap, forecast denominator, scenario value, final target, weight, and upside/downside matches within stated rounding tolerance.
   - If a row cannot be recalculated, mark `Model Reproducibility: FAIL` and block publication until the model table is repaired.
   - Check source hierarchy, fake precision, method mismatch, missing broker comparisons, and unsupported recommendations.
   - Missing required valuation artifacts are publication blockers, not formatting issues.

## Required Artifacts

Write these files for full equity-research reports:

- `analysis/valuation_model.md`
- `analysis/valuation_audit.md`
- `data/current_valuation_model_<YYYYMMDD>.json` when a structured case data room exists.

`analysis/valuation_model.md` must contain:

1. `Final Valuation Table` with current price/date, shares, market cap, 2026E revenue, 2026E NP/EPS, method, bear/base/bull, final target or fair-value range, upside/downside, action, catalyst, invalidation, and evidence quality.
2. `Three-Tier Targets` with bear/base/bull scenario notes and bubble degree.
3. `Relative / PEG / PSG Comparison` where the denominator is valid.
4. `Seasonality Calibration` showing quarter-to-year bridge and calibrated PE or alternative multiple.
5. `Next-Quarter Threshold` showing what revenue, margin, EPS, price, order, or customer evidence is needed to support current valuation.
6. `Method and Assumption Bridge` with primary method, secondary check, assumptions, catalyst needed, and invalidation trigger.
7. `Market-Expectation Valuation Bridge` showing what investors are paying for: revenue growth, margin expansion, multiple expansion, duration extension, or business-model reclassification.
8. `Broker/Street Comparison` with source, date, rating, target, forecasts, method, implied upside, AStock gap, and evidence quality; use `not disclosed` when unavailable.
9. `Market-Implied Sentiment Anchor` with current-implied multiples, trading or momentum context, market anchor, broker anchor, weights, final target, premium/discount, and action logic.
10. `Growth Earnings Dependency` when applicable, referencing the growth driver, base/growth split, unit or proxy, ASP/price, revenue recognition, margin, opex, net profit/EPS contribution, valuation credit, and current-price-implied growth.
11. `Full-Chain Classification Dependency` for industry-chain reports, referencing full-chain universe row, core/satellite classification, value-chain economics, and why the ticker is eligible or not eligible for valuation.

`analysis/valuation_audit.md` must contain:

- Arithmetic checks.
- Forecast availability.
- Target-price comparability.
- Final valuation completeness.
- Scenario-band checks.
- Market-implied sentiment anchor checks.
- Full-chain/core-satellite dependency checks.
- Value-chain economics dependency checks.
- Model reproducibility checks with `Model Reproducibility: PASS` or `FAIL`.
- Fake-precision flags.
- Supply-chain dependency checks: every investable ticker's valuation method, catalyst, invalidation, and next-quarter threshold must be traceable to the supply-chain package or marked `insufficient chain evidence`.
- Growth earnings dependency checks: every high-growth valuation credit must trace to base/growth split, unit/order/ASP/proxy math, recognized revenue ratio, margin, opex, net profit, EPS, scenario sensitivity, and current-price-implied growth or be marked `watchlist only / insufficient growth evidence`.
- Required fixes or `PASS` with explicit coverage.

## Publication Blockers

Block publication if any covered or investable ticker is missing:

- Current price/date, shares or market cap.
- Forecast revenue and net profit/EPS or an explicit `insufficient evidence` label.
- Business-model matched method and secondary check.
- Bear/base/bull values.
- Final target or fair-value range and implied upside/downside.
- Market-expectation bridge.
- Market-implied sentiment anchor and final weights.
- Broker/Street comparison when public evidence exists.
- Catalysts and invalidation triggers.
- Valuation audit.
- `Model Reproducibility: PASS` in `analysis/valuation_audit.md`.
- Full-chain universe row, core/satellite classification, and value-chain economics for full industry-chain reports.
- Supply-chain relationship row and company fundamental card for full industry-chain reports, or an explicit `insufficient chain evidence` label that blocks investable recommendations.
- Growth earnings artifacts for any high-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP valuation credit, or an explicit `watchlist only / insufficient growth evidence` label that blocks investable recommendations.

## Integration Rules

- `equity-research` must run `supply-chain-research` before this skill in full industry-chain reports, must run `growth-earnings-model` before this skill whenever high-growth valuation credit is used, then run this skill after data verification and house view, before risk analysis, exhibit planning, LaTeX writing, and review.
- `latex-writer` must copy the valuation skill outputs into reader-facing sections and must not summarize away required tables.
- `research-report-reviewer` must treat missing valuation skill outputs as S-Level.
- `research-report-reviewer` must treat valuation packages unsupported by supply-chain evidence as S-Level or A-Level depending on whether investable recommendations depend on the unsupported claim.
- `research-report-reviewer` must treat high-growth valuation packages unsupported by growth earnings artifacts as S-Level or A-Level depending on whether investable recommendations depend on the unsupported claim.
- Chinese reports must write reader-facing valuation logic, action labels, catalysts, invalidation triggers, and audit summaries in Chinese.
