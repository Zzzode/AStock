# Verified ETF fundamentals — 2026-08-12

## Verification conclusion

The archived official disclosures support a cross-checked product-terms, fee-rate, dated-financials and dated-holdings record for 511010, 510880 and 512890. They do **not** complete market, valuation, liquidity, tax, suitability, current-holdings or portfolio-risk diligence. All products therefore remain `watch_only_q0`.

The machine-readable source of truth is `data/verified_etf_fundamentals_20260812.json`; raw extraction and document hashes are in `data/raw_etf_fundamentals_20260812.json`.

## What was cross-checked

| Field | Test | Result |
|---|---|---|
| Legal terms | 2025 annual report against subsequent PDS and/or 2026 Q2 report | Fund code, manager, custodian, mandate and benchmark reconcile for all three ETFs. |
| Fee rates | PDS against annual-report fee-accrual notes | 511010: 0.15% management / 0.05% custody; 510880 and 512890: 0.50% / 0.10%. |
| 2025 financials | Annual report audit disclosure | Retained as audited year-end disclosures. |
| 2026 Q2 financials and holdings | Q2 report disclaimer | Retained as **unaudited** dated disclosures only. |
| Holding concentration | Arithmetic sum of published NAV weights | Dated computation only; table rounding applies. |

## Verified product cards

### 511010 — 国泰上证5年期国债ETF

The fund is a Treasury bond ETF managed by 国泰基金管理有限公司 and custodied by 中国建设银行股份有限公司. It tracks the 上证5年期国债指数收益率 through optimised sampling. The PDS requires at least 90% of NAV in underlying-index constituent/alternate government bonds after the build period.

- 2025 audited: CNY3.021bn NAV, CNY140.027 NAV per unit, 0.59% one-year NAV return, and CNY21.042 per ten units / CNY38.003m cash distribution.
- 2026 Q2 **unaudited**: CNY5.117bn NAV, CNY140.753 per unit, 0.78% three-month NAV return and 98.89% of NAV in government bonds.
- Disclosed ongoing fee schedule: 0.15% management fee, 0.05% custody fee and 0.21% PDS annual operating-cost estimate.
- An official SSE snapshot at 2026-08-12 16:29:05 reports CNY141.084 last price and CNY1.345bn amount; it has no same-session NAV/IOPV, spread, depth or capacity fields.

The evidence does not contain current duration, modified duration, DV01, convexity, market price/NAV/IOPV, premium/discount or executable-liquidity data. A Treasury ETF cannot be treated as protected liquidity on this record.

### 510880 — 华泰柏瑞上证红利ETF

The fund is an equity ETF managed by 华泰柏瑞基金管理有限公司 and custodied by 招商银行股份有限公司. It uses full replication of the 上证红利指数 and the PDS states a 95% minimum allocation to index constituents/alternates, subject to temporary adjustment conditions.

- 2025 audited: CNY19.265bn NAV, CNY3.1813 NAV per unit and -0.45% calendar-year NAV return. It reported cash distributions in 2025, 2024 and 2023 of CNY1.4200, CNY1.3100 and CNY1.3800 per ten units respectively.
- 2026 Q2 **unaudited**: CNY22.276bn NAV, CNY2.9103 per unit, -10.36% three-month NAV return and 98.73% of total assets in equities.
- Disclosed ongoing fee schedule: 0.50% management fee, 0.10% custody fee and 0.60% PDS annual operating-cost estimate.
- An official SSE snapshot at 2026-08-12 16:29:05 reports CNY3.303 last price and CNY389.653m amount; it is not an execution-clearance record.

Historical distribution is not a prospective cash-yield estimate. Current price/NAV/IOPV, premium/discount, liquidity, holdings overlap, TTM settled cash, tax and execution cost remain unresolved.

### 512890 — 华泰柏瑞中证红利低波动ETF

The fund is an equity ETF managed by 华泰柏瑞基金管理有限公司 and custodied by 中国建设银行股份有限公司. It uses full replication of the 中证红利低波动指数; the PDS states at least 90% of NAV and 80% of non-cash assets in index constituents/alternates, subject to stated exceptions.

- 2025 audited: CNY26.754bn NAV, CNY1.1745 NAV per unit and 4.74% calendar-year NAV return. The annual report says no profit distributions were implemented in the past three years.
- 2026 Q2 **unaudited**: CNY31.290bn NAV, CNY1.0668 per unit, -10.83% three-month NAV return and 97.77% of total assets in equities.
- Disclosed ongoing fee schedule: 0.50% management fee, 0.10% custody fee and 0.60% PDS annual operating-cost estimate.
- An official SSE snapshot at 2026-08-12 16:29:05 reports CNY1.159 last price and CNY517.864m amount; it is not an execution-clearance record.

The “low-volatility” name does not remove equity, factor, tracking, index-change or liquidity risk. It does not establish future holder cash and cannot be used as an income-target substitute without a separate forward cash and execution analysis.

## Required next evidence

- Current market price, NAV/IOPV, premium/discount, bid-ask, turnover and executable depth for each ETF.
- Current full holding files and issuer-group / REIT-overlap mapping for the two equity ETFs.
- Rate sensitivity (duration, modified duration, DV01 and convexity) for 511010.
- TTM settled cash, forward distribution-risk, tax, account and execution-cost treatment before a cash contribution is modeled.
- Portfolio-level correlation, drawdown and risk-budget assessment.

No allocation or investment action is authorised by this artifact.
