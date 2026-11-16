# REIT R0 Fact Pack — 2026-08-14

Evidence-only, q=0 research record for 508069, 508068 and 508096. This is not an allocation, recommendation, suitability assessment, order, or return forecast. The sole conditional/ex-post objective remains rolling five-year cost-aware TWRR >=5%; cash distribution is neither a target nor automatically reinvested.

| Ticker | FY2025 unit NAV | FY2025 distributable amount / unit | FY2025 actual distribution / unit | Annual cash-flow distribution rate reported by fund | Property/project appraisal | Operating evidence |
|---|---:|---:|---:|---:|---|---|
| 508069 | RMB 4.8970 | RMB 298.65m / 0.5973 | RMB 0.7718 | 9.19% | RMB 2.705bn income approach; market-method check | Project revenue 99.12% of forecast; net cash flow 103.81% of forecast. |
| 508068 | RMB 2.9927 | RMB 74.82m / 0.1033 | RMB 0.0940 | 2.53% | RMB 2.024bn income approach; cost-method check | Six projects’ combined revenue 103.68% and net cash flow 106.63% of forecast. |
| 508096 | RMB 9.1720; fair-value reference NAV RMB 8.1264 | RMB 323.36m / 0.5381 | RMB 0.2372 | 5.33% | Jingtai PV RMB 382m; Yulin PV RMB 1.508bn; Lianghe hydropower RMB 2.465bn | Legacy PV revenue 78.36% and cash flow 78.60% of forecast; Q2 notice flags Jingtai electricity settlement -33.96% YoY. |

All figures above are issuer/exchange financial-disclosure data, not current market prices. Reported cash-flow distribution rate is the manager’s report-period `distributable amount / period-end market capitalisation` statistic. It is not an investor’s market-price total return and must not be used as a TWRR proxy.

Primary locations and hashes are in [capture_manifest.md](../sources/official-reit-continuation-20260814/capture_manifest.md).

## T2 blockers

1. Capture same-timestamp price, bid/ask, depth, ADTV/turnover, free float, lock-up releases, lot/settlement and transaction costs for each ticker. Without these, no cost-aware market-access finding is possible.
2. Capture current NAV/appraisal and calculate premium/discount only from matching-date price and NAV. Existing 2025 valuation/NAV data cannot be substituted for an August 2026 price.
3. Build an adjusted market-price return series with every distribution ex-date/cash date and costs. Do not substitute fund distributable cash, NAV growth or “cash-flow distribution rate”.
4. A realised rolling five-year TWRR cannot be tested as of 2026-08-14: 508069 listed 2024-11-01; 508068 2022-08-31; 508096 2023-03-29.
5. Refresh 508069/508068 through the disclosed 2026 Q2 reports before T2; this bounded collection archived FY2025 only. For 508096, reconcile the unaudited July project notice to later financial settlement and the next valuation update.
