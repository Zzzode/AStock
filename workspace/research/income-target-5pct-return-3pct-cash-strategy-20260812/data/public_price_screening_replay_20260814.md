# R1 Public Price Screening Replay

- Scope ID: `total-return-open-universe-v3-20260814`
- Status: `screening_complete_static_vector_rejected_as_5pct_evidence`
- Research-only / formal decision eligible / portfolio q: `true / false / 0`

## Result

The limited static four-ETF screen is **rejected as evidence for the 5% total-return objective**.  Its full-period annualized *price* return is 7.77%, but 207 of 633 complete, overlapping rolling five-year price windows are below 5%; the minimum is 2.75%.  The result is not total return, does not include costs or taxes, and is not an investable allocation.

## Screening set

| Code | Role in this diagnostic | Marked weight |
|---|---|---:|
| 510300 | CSI 300 equity ETF price sleeve | 25% |
| 510880 | SSE Dividend equity ETF price sleeve | 25% |
| 511010 | SSE 5-year Treasury ETF price sleeve | 25% |
| 518880 | gold ETF price sleeve | 25% |

This finite set is a public-data discovery screen, not a T2 decision universe. It does not exclude direct equities, public REITs, direct sovereign instruments or other lawful products from later research.

## Frozen public input

- Capture manifest: `sources/probe-public-market-20260814/capture_manifest.json` (`SHA-256 cacabe167460b77e3a3f84bb35a9546d8e8c0fd89cbbc331b21e4c06e224736f`)
- Raw public archive: `sources/probe-public-market-20260814/e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda.json` (`sha256:e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda`)
- Replay input: `sources/probe-public-market-20260814/e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda.portfolio.replay.json`
- Window: 2019-01-02 to 2026-08-13 (1847 common price observations).

The provider is a public aggregation path and the calendar is the intersection of observed prices, not an official exchange calendar. The series use the unadjusted market-price setting. No distribution, corporate action, halt, limit-lock, delisting, bid/ask, spread, fill, tax or capacity claim is made.

## Diagnostic mechanics

- Equal 25% marked weights; reset at the first common price observation of each calendar quarter.
- The marked weight applies only to the next price interval.
- Unitized price path only; no external flow, cash-receipt objective, or automatic reinvestment.
- No cost, tax, lot, settlement, slippage or market-impact model.

## Results

| Metric | Result |
|---|---:|
| Cumulative price return | 76.76% |
| Annualized price return | 7.77% |
| Annualized daily price volatility | 9.45% |
| Maximum marked drawdown | -10.85% |
| Five-year windows at or above 5% price return | 426 / 633 |
| Five-year windows below 5% price return | 207 / 633 |
| Minimum five-year annualized price return | 2.75% |

| Window start | Window end | Annualized price return | At or above 5%? |
|---|---|---:|---|
| 2019-01-02 | 2024-01-02 | 5.43% | 是 |
| 2019-12-31 | 2024-12-31 | 5.07% | 是 |
| 2020-12-31 | 2025-12-31 | 6.14% | 是 |
| 2021-08-13 | 2026-08-13 | 6.47% | 是 |

## Boundary and next gate

The failure of an unadjusted, cost-free price proxy is sufficient to reject this static vector as supporting evidence. It does **not** demonstrate the performance of a total-return strategy, nor does it test a future model. Before any later T2/T3/T4 review, the research must freeze a versioned selection and rebalancing rule; obtain a source-consistent total-return and corporate-action ledger; model dated product-specific costs, taxes, settlement and liquidity; and complete equity-research-grade item dossiers plus portfolio-level risk review.
