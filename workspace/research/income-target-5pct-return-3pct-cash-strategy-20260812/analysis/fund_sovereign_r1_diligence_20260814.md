# R1 Product Diligence: Existing Fund and Sovereign T1 Candidates — 2026-08-14

## Boundary and status

This note covers only 512500, 510880, 511010, 511880 and 260008. It is product diligence, not an allocation, product selection or order instruction. Every candidate remains `q=0`.

R1 disclosures establish selected structure, methodology and event facts. They do not establish an authorized PIT total-return archive, market-price/NAV premium-discount series, spread/depth history, actual route-specific costs, or a pass of the conditional/ex-post rolling five-year cost-aware TWRR objective.

| Code | Exposure / structure | Current official mechanics | R1 evidence boundary |
|---|---|---|---|
| 512500 | ChinaAMC CSI 500 equity ETF; normally >=90% in constituents/substitutes. | Q2 2026 manager report disclosed +1.34% tracking deviation for the quarter and identified operating expenses, index changes, creations/redemptions and dividends as causes. SSE approved a primary market maker effective 2026-03-25. | Approval is not spread/depth evidence; reported fund NAV tracking is not investor total return. |
| 510880 | Huatai-PineBridge SSE Dividend equity ETF; complete replication subject to stated liquidity exception. | Q1 2026 report disclosed 0.011% daily average absolute tracking deviation and 0.020% period tracking error. SSE approved a primary market maker effective 2026-05-29. | Current fee legal document and price/NAV/liquidity history remain absent. |
| 511010 | Guotai SSE 5-Year Treasury Bond ETF; optimized sampling and >=90% sovereign constituent/substitute exposure. | Current summary sets <=0.2% daily average absolute deviation and <=2% annualized tracking-error objective; disclosed fees are 0.15% management, 0.05% custody and 0.21% estimated total operating expense. June 2026 fund distribution is an accounting event. | No authorized bond/ETF price, accrual, quote or cost history. |
| 511880 | Yinhua exchange-traded money-market fund A class; permitted money-market instruments with amortized-cost and shadow-pricing controls. | Current prospectus documents cash-substitution/difference mechanics and valuation/liquidity restrictions. A-class legal distribution is cash; SSE named a primary market maker effective 2026-06-17. | No observed exchange-price/NAV, spread/depth or secondary-market cost evidence. |
| 260008 | MOF five-year fixed-rate sovereign bond. | 1.50% coupon; annual coupon date is 15 April; issued April 2026 and matures April 2031. | No fund NAV/benchmark/tracking framework, no authorized quote/price archive, and the specific security lacks five years of history. |

## Distribution and coupon accounting

The 511010 notice records CNY8.144 per 10 units (record 2026-06-24, ex 2026-06-25, payment 2026-06-30). The 511880 A-class notice records CNY1.1553 per unit, with on-market payment 2026-01-07. These are dated ledger events only. The 260008 coupon is paid annually on 15 April; maturity redemption is dated 2031-04-15. None is an expected-return estimate or a total-return substitute.

## Required gates

**T1 to R1.** Confirm current legal terms, manager/issuer/custodian, benchmark and methodology; preserve distribution/coupon mechanics as ledger events; and record structural, valuation, liquidity and access gaps. This is only partially complete for all fund candidates. The bond terms are complete but the history constraint remains hard.

**R1 to R2.** Before any formal replay, obtain an authorized PIT archive of raw prices, NAV where applicable, distributions/coupons, actions, market status, benchmark membership and availability timestamps. Add route-specific cost, tax, spread, liquidity, settlement and no-fill evidence; then reconcile event accounting without double counting under a frozen unitized scale-neutral rulebook. The required source-entitlement matrix is [data_source_feasibility_r1_20260814.json](../data/data_source_feasibility_r1_20260814.json).

260008 cannot enter a five-year realized-history test until the specific security has enough history, even if price and access evidence later become available.

Primary raw evidence and hashes: `sources/official-fund-sovereign-r1-20260814/manifest.json`. Full normalized field pack: `data/fund_sovereign_r1_diligence_20260814.json`.
