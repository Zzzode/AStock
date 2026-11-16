# R0 Continuation: Non-REIT Fund and Sovereign Candidates — 2026-08-14

## Mandate boundary

This is a primary-source evidence note for 512500, 510880, 511010, 511880, and 260008. Each candidate is recorded at `q=0`. The only decision criterion is the conditional/ex-post test of rolling five-year cost-aware TWRR >=5%. No cash-income target, automatic reinvestment assumption, allocation, recommendation, or order authorization is made.

## R0 facts collected

| Code | Primary disclosure | Product/instrument facts established | Explicitly not established |
|---|---|---|---|
| 512500 | ChinaAMC product summary, 2026-05-29; Q2 2026 report | Equity ETF tracking CSI 500; normal 90% constituent/substitute-stock minimum; 0.15% management and 0.05% custody fee. | Secondary-market investor total return and realised execution cost. The disclosed 43.79% five-year fund net-value growth through 2026-06-30 is not cost-aware investor TWRR. |
| 510880 | SSE-hosted 2024 Q4 report, published 2025-01-22 | Equity ETF using complete replication of the SSE Dividend Index, subject to its stated liquidity exception. | Investor return/cost series. Its 45.05% five-year fund net-value growth through 2024-12-31 excludes holder trading/subscription costs and is outside the 2026 cutoff. |
| 511010 | SSE-hosted product summary, 2025-03-21 | Government-bond ETF, optimized sampling of SSE 5-Year Treasury Bond Index; >=90% of NAV in index/substitute government bonds; 0.15% management, 0.05% custody, disclosed 0.22% annual comprehensive operating-expense ratio. | Actual brokerage costs and an investor-level return series. On-market transaction fees remain broker-specific. |
| 511880 | SSE-hosted product summary, 2024-06-28 | Exchange-traded money-market fund; low-risk relative classification; disclosed A-share 0.30% management, 0.09% custody, 0.25% sales service and 0.64% annual comprehensive operating expense. | Investor total return. The primary disclosure warns of exchange-price/NAV divergence and secondary-market fee/liquidity effects; performance charts end at 2023-12-31. |
| 260008 | ChinaMoney/CETS reopening listing notice, 2026-06-23 | MOF-issued five-year fixed-rate sovereign: CNY100 face value, 1.5000% coupon paid annually, actual/actual day count, interest from 2026-04-15, redemption 2031-04-15; reopening price CNY100.6600 per CNY100. | A five-year realised history for this security. It did not exist until April 2026. |

The evidence paths and hashes are recorded in `sources/official-fund-sovereign-continuation-20260814/manifest.json`; normalized facts are in `data/fund_sovereign_r0_fact_pack_20260814.json`.

## Evidence interpretation constraints

The reported fund `净值增长率` figures are fund-level NAV performance disclosures. They cannot be silently relabelled as investor total return: actual secondary-market execution price and costs are not present, and the 510880 report expressly excludes holder subscription/trading costs from its fund indicators. Similarly, 260008's coupon and reopening price describe the instrument but do not establish a multi-year holding return.

## Remaining T2 blockers

1. Obtain a dated, audit-preserved total-return data set for each ETF that can reconcile NAV, exchange trading price, distributions/corporate actions and the specified no-automatic-reinvestment convention.
2. Obtain cost inputs at the route actually being tested: dated broker commission schedule, bid/ask series, slippage/market-impact method, applicable taxes/fees, and creation/redemption/custody costs where relevant. Published management and custody fees alone are not enough.
3. Specify and reproduce the rolling-five-year TWRR test: observation dates, price timestamp, cash-flow and distribution convention, eligible routes, and any rebalancing convention. Without these, the >=5% condition cannot be evaluated.
4. Exclude 260008 from any five-year realised-history test until it has the required history; no proxy or interpolation may replace it.

Status: R0 product/instrument facts collected; T2 not ready. All candidates remain `q=0`.
