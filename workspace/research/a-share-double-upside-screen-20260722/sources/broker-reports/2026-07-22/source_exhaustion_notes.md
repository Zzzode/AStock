# Broker Source Exhaustion Notes — 2026-07-22

This case-local note is an input to the root source-governance workflow. It does not replace `source_exhaustion_log.md/json`, which is owned by the root workflow.

## Probes completed

- Refreshed Eastmoney's public ticker report-list API from 2025-01-01 through 2026-07-22 for `600150`, `301308`, `002812`, `002240`, `300390`, and `002497`; raw responses are preserved under `metadata/`.
- Revalidated all 14 selected direct Eastmoney-hosted PDF URLs; each returned HTTP 200 and `application/pdf`.
- Searched public web results for newer broker coverage through 2026-07-22. No newer original broker PDF than the dates in the index was found for the six tickers.
- Excluded search snippets, media reposts, third-party previews, and public average-target aggregations from valuation weight.

## Gap rows for source governance

| Ticker | Requested evidence | Probes / result | Source quality | Valuation weight | Exhaustion reason | Next verification path |
|---|---|---|---|---:|---|---|
| 600150 | Explicit broker target price | Five original PDFs plus live Eastmoney metadata; no target disclosed | `not_found` for target; underlying forecasts are `original_broker_pdf` | 0 | Current-price PE is disclosed, but no explicit target is present | Licensed Wind/Choice/iFinD target-price table or broker client export |
| 301308 | Fresh post-H1 report and explicit target | Latest public originals are both 2026-05-07; no target disclosed | `not_found` for fresh target; older forecasts are `original_broker_pdf` | 0 | No post-2026-05-07 original report; profit forecasts diverge materially; aggregator average targets are not original evidence | Post-2026H1 original PDF or licensed broker-terminal export |
| 002240 | Explicit broker target price | Four original PDFs through 2026-07-09; no target disclosed | `not_found` for target; underlying forecasts are `original_broker_pdf` | 0 | Reports disclose only current-price PE | Licensed Wind/Choice/iFinD target-price table or broker client export |
| 300390 | Fresh multi-broker coverage and explicit target | One original PDF dated 2026-06-06; no target disclosed | `not_found` for fresh target; single report is `original_broker_pdf` | 0 | Only one public report since 2025 and it is older than 30 days | Post-2026H1 original PDF or licensed broker-terminal export |
| 002497 | Target horizon | Original PDF discloses CNY42 from 2026E EPS × 16x PE, but no target horizon | `original_broker_pdf` for target; `not_found` for horizon | 1 for target, 0 for any year-end-horizon claim | Forecast year does not establish target date | Broker analyst note/client export explicitly stating target horizon |
| 002812 | Target horizon | Original PDF discloses CNY103 from 2027E EPS × 20x PE, but no target horizon | `original_broker_pdf` for target; `not_found` for horizon | 1 for target, 0 for any year-end-horizon claim | Forecast year does not establish target date | Broker analyst note/client export explicitly stating target horizon |

## Required publication wording

- Permitted: “The original Dongwu reports state target prices of CNY42 for `002497` and CNY103 for `002812`; versus captured 2026-07-22 prices, these imply +150.15% and +115.30%.”
- Not permitted: “Street expects either stock to double by 2026 year-end.” The reports do not state that horizon.
- Not permitted: reverse-engineering targets for `600150`, `301308`, `002240`, or `300390` from current-price PE or AStock models.

