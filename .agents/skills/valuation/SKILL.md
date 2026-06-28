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
- House view and industry-chain classification so valuation methods match business economics.

If an input is missing, either collect it through the project capability layer or mark it explicitly as `not disclosed` / `insufficient evidence`. Do not fill broker, order, customer, or consensus fields with AStock assumptions.

## Workflow

1. **Classify each ticker before valuing it.**
   - Identify lifecycle, profit quality, cyclicality, asset intensity, segment mix, order durability, and evidence quality.
   - Select a primary method and at least one secondary check. Use PE/PEG for durable earnings, cycle-adjusted PE or EV/EBITDA for cyclicals, PB/ROE or EV/EBITDA for asset-heavy names, PS/EV-Sales for revenue-no-profit names, and SOTP/blended methods for mixed businesses.
   - Never force a heterogeneous industry chain into one PE template.

2. **Normalize the financial denominator.**
   - Show 2026E revenue, 2026E net profit/EPS, expected growth, and the bridge from reported quarters to the forecast.
   - Apply seasonality calibration before calling anything cheap or expensive.
   - If the denominator is near-zero, temporary, project-cycle distorted, or unsupported, switch methods or mark the ticker `insufficient evidence / watchlist only`.

3. **Build scenario valuation.**
   - Bear case: narrative breaks, lower multiple, lower margin, weaker price or order conversion, or cycle floor.
   - Base case: AStock cold assessment using the ticker's business-model driver.
   - Bull case: sell-side or market upside logic; disclose target-price bias and required validation.
   - Always show bubble degree: `(current / base target - 1) * 100%`.

4. **Build the multi-anchor target.**
   - Final target = fundamental/intrinsic value * Wf + market-implied sentiment anchor * Wm + broker/Street anchor * Ws.
   - Show current-implied PE/PS/PB/EV multiple, trading-value or momentum context where available, market anchor, broker anchor, final weights, final target, premium/discount, and embedded expectation gap.
   - Do not publish a mechanical sell/reduce action only because intrinsic value is below price when observable market evidence supports a sentiment premium. Label the premium and define what would break it.

5. **Translate valuation into research action.**
   - Use action labels that describe behavior: `core review`, `pullback entry`, `market-supported watch`, `event-driven validation`, `watchlist only`, `sentiment premium breaking`, or `high valuation risk`.
   - Include catalysts, invalidation triggers, and next-quarter thresholds.
   - No investable action is allowed without a current-price-based target or fair-value range and implied upside/downside.

6. **Audit before release.**
   - Recalculate market cap, EPS, PE/PS/PB, target price, upside/downside, scenario bands, and weights.
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

`analysis/valuation_audit.md` must contain:

- Arithmetic checks.
- Forecast availability.
- Target-price comparability.
- Final valuation completeness.
- Scenario-band checks.
- Market-implied sentiment anchor checks.
- Fake-precision flags.
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

## Integration Rules

- `equity-research` must run this skill after data verification and house view, before risk analysis, exhibit planning, LaTeX writing, and review.
- `latex-writer` must copy the valuation skill outputs into reader-facing sections and must not summarize away required tables.
- `research-report-reviewer` must treat missing valuation skill outputs as S-Level.
- Chinese reports must write reader-facing valuation logic, action labels, catalysts, invalidation triggers, and audit summaries in Chinese.
