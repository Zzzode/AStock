# Valuation Audit

Model Reproducibility: PASS

- Price date: 2026-07-17; all twelve closes cross-checked between Tencent and Sina/AStock.
- FY2025 and 2026Q1 actuals: verified packet; publication-critical company examples reconciled to issuer PDFs.
- 2026E/2027E revenue and NP: positive-weight original broker-PDF rows only.
- Shares: total market capitalization divided by close. Modeled EPS is forecast NP divided by this current-share denominator; source-PDF EPS is retained only as a diagnostic where corporate-action bases differ.
- Primary method: conservative mature-business 2026E P/E after removing unbridged high-growth premiums. Independent secondary method: justified P/B from official FY2025 attributable equity and normalized ROE; fundamental base-target weights are 60%/40%, while PEG carries zero target weight and is diagnostic only.
- Target formula: fundamental_weight * base + market_weight * current price + broker_weight * explicit broker target.
- Upside formula: final_target / current_price - 1; script-generated and recalculated.
- Atlas-specific 2026E revenue, profit and EPS: CNY 0 for all rows.
- No DCF is used because Atlas unit/ASP/capex/working-capital inputs are unavailable; P/E is the least falsely precise method.

Residual model risk: original broker forecasts can be optimistic; company-specific Atlas allocation, utilization and margin remain unverified; target multiples are scenario assumptions rather than observed transactions.
