# Verified financials — 雅化集团（002497.SZ）

**Data cutoff:** 2026-07-23. Units are CNYbn unless stated otherwise. Annual values are L1 audited issuer disclosure; 2026Q1 is L1 unaudited issuer disclosure; 2026H1 is L1 preliminary issuer disclosure. Derived metrics below are deterministic calculations from `data/raw_financials.md`, rounded for display.

## Historical P&L, cash and operating-quality bridge

| Metric | 2023A | 2024A | 2025A | 2026Q1 | Interpretation boundary |
|---|---:|---:|---:|---:|---|
| Revenue | 118.953 | 77.157 | 85.432 | 28.302 | Q1 is a three-month figure; do not annualize. |
| Gross profit | 16.017 | 12.891 | 18.849 | 6.958 | Derived as revenue less operating cost. |
| Gross margin | 13.46% | 16.71% | 22.06% | 24.59% | Consolidated, product-mix dependent; not lithium unit margin. |
| Operating profit | 0.220 | 2.986 | 7.972 | 4.063 | Includes reported non-operating-in-character items above operating profit. |
| Operating margin | 0.18% | 3.87% | 9.33% | 14.35% | Not a segment margin. |
| Attributable NP | 0.402 | 2.571 | 6.324 | 3.388 | 2025 includes impairment and investment-result effects disclosed in the annual report. |
| Attributable NP margin | 0.34% | 3.33% | 7.40% | 11.97% | Consolidated post-tax margin. |
| CFO | 8.308 | 9.437 | -5.698 | -4.306 | Cash-conversion risk requires H1 verification. |
| Cash capex proxy | 6.211 | 5.587 | 3.127 | 0.562 | Cash-flow item, not accounting capex. |
| CFO less capex proxy | 2.097 | 3.850 | -8.825 | -4.868 | A simple FCF proxy; excludes acquisitions, investments, dividends and financing. |
| CFO / attributable NP | 20.66x | 3.67x | -0.90x | -1.27x | Negative ratios flag a cash-conversion issue, not a fraud conclusion. |

## Working capital and balance-sheet bridge

| Metric | 2023A | 2024A | 2025A | 2026Q1 | Calculation / boundary |
|---|---:|---:|---:|---:|---|
| Cash + trading financial assets | 39.780 | 36.353 | 28.237 | 26.030 | Before restricted-cash, derivative and liquidity adjustments. |
| Defined gross debt | 17.841 | 10.386 | 9.293 | 11.186 | Short-term borrowings + current portion + long-term borrowings only. |
| Simple net cash | 21.939 | 25.967 | 18.944 | 14.844 | Cash + trading financial assets – defined gross debt; not enterprise value. |
| Accounts receivable | 9.630 | 9.389 | 13.257 | 19.801 | 2026Q1 rose CNY6.545bn from 2025A end. |
| AR days | 29.5 | 44.4 | 56.6 | 63.0 | Year-end AR / period revenue × 365; Q1 uses 90 days. A rough snapshot, not a DSO replacement. |
| Inventory | 22.314 | 16.453 | 16.958 | 18.728 | Product and raw-material mix are undisclosed in this bridge. |
| Inventory days | 79.1 | 93.4 | 93.0 | 79.0 | Year-end inventory / period operating cost × days; Q1 uses 90 days. |
| Parent equity | 103.391 | 104.244 | 107.282 | 110.328 | Reported issuer consolidated balance sheet. |
| Total liabilities | 38.120 | 32.603 | 38.994 | 37.646 | Derivative and lease liabilities are included here but excluded from defined gross debt. |

## What the verified packet permits

1. A house model can start from audited 2023–2025 segment base data, 2026Q1 consolidation, a 2026H1 profit constraint, working-capital stress and a disclosed cash/debt bridge.
2. It **cannot** source a 2026H2 revenue, lithium volume, realized ASP, unit cost, self-supply percentage, civil-explosives profit, or H1 operating cash flow from issuer disclosure. Those remain assumptions and must receive sensitivity treatment.
3. The financial packet deliberately keeps H1 revenue and cash-flow fields `not disclosed`; importing a broker model into those fields would violate the facts/assumptions boundary.

Source IDs: FIN-23A, FIN-24A, FIN-25A, FIN-26Q1, FIN-26H1P. Full raw values, issuer page references and source hashes: `data/raw_financials.md` and `sources/official-financial-20260723/capture_manifest.md`.
