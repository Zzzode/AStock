# R1 Product Diligence: Personal ETF Candidate Set — 2026-08-14

## Scope, decision boundary and conclusion

This is a product-diligence packet for the five ETFs below. It is not a
portfolio selection, weight, subscription, sale or order instruction. The
candidate set is finite solely to make the research testable; it does not
exclude other lawful domestic instruments from later comparison. Every product
remains `q=0` and no product is admitted to T3 or T4.

The associated frozen public-price rule uses 510300, 510880, 518880 and
511010. Its 10-bps turnover sensitivity produces a 5.09% full-period
annualized **price** observation but fails the all-window condition: 281 of
611 overlapping rolling five-year windows are below 5%, with a 3.88% minimum.
That result is not total return and cannot justify activation. See
`data/personal_etf_strategy_public_observation_20260814.json`.

| Code | Product role under research | Structural exposure | R1 conclusion |
|---|---|---|---|
| 511990 | Optional transaction/settlement parking instrument; no mandated allocation or cash objective | Exchange-traded money-market fund holding short-dated money-market instruments | Low-risk product structure is documented; income convention, route-specific trading cost, secondary-market premium/discount and history remain unresolved. |
| 511010 | Defensive duration sleeve in the test rule | Optimized-sampling SSE five-year Treasury-bond ETF | Long listed history and fee/methodology terms are documented; total-return, spread/depth and actual-route evidence are absent. |
| 510880 | Dividend-equity risk sleeve in the test rule | Full-replication SSE Dividend Index ETF | Equity/index, fee and risk terms are documented; it is not a defensive cash substitute and has not passed a net portfolio test. |
| 510300 | Broad-A-share risk sleeve in the test rule | Full-replication CSI 300 ETF, normally at least 95% in constituents/substitutes | Market-beta exposure, lending/derivatives permissions and fee terms are documented; current market quality and total return are unresolved. |
| 518880 | Domestic-gold risk sleeve in the test rule | Gold ETF with at least 90% in Shanghai Gold Exchange-listed gold spot contracts | Commodity-price exposure and cost terms are documented; it is not a bond hedge or low-volatility substitute. |

## Candidate cards

### 511990 — 华宝现金添益 ETF

**Verified structure.** The 2025 product summary identifies a Shanghai-listed
money-market fund, with cash, deposits, repos, central-bank bills, NCDs,
short-dated debt instruments and ABS in the stated permitted range. Its stated
benchmark is the after-tax seven-day call-deposit rate. The summary reports
annual management, custody and sales-service fees of 0.35%, 0.09% and 0.25%.
Those are product expenses, not a broker commission, bid-ask spread or a net
return forecast.

**Operational role and risks.** The candidate can be researched as a place to
record unallocated settlement value, but it has no required allocation and no
separate cash objective. A money-market classification does not eliminate
premium/discount, liquidity, credit, valuation, trading-access or operational
risks. SSE's ETF guidance says some money-market ETFs support same-day trading;
the actual broker route and the product's current trading/creation-redemption
status must be checked on the relevant day.

**R2 gate.** Freeze the daily per-unit income/accounting convention; obtain
dated secondary-market price, NAV or per-unit income, distribution, premium/
discount, spread/depth, broker commission and settlement data; reconcile all
income events exactly once in a total-return ledger. No headline money-market
income may be used as a portfolio return substitute.

### 511010 — 国泰上证 5 年期国债 ETF

**Verified structure.** The 2026 product summary says the ETF follows the SSE
five-year Treasury-bond index using optimized sampling and, after construction,
normally keeps at least 90% of NAV in index constituents and substitutes. It
discloses 0.15% management, 0.05% custody and 0.21% estimated annual
comprehensive operating expense. It targets daily average absolute tracking
deviation of no more than 0.2% and annualized tracking error no more than 2%
under normal conditions; these are product objectives, not realized investor
performance.

**Operational role and risks.** This is the defensive **market** sleeve in the
public-price screen, not a cash equivalent. Rate moves, index changes,
optimized-sampling, constituent-bond liquidity/settlement and secondary-market
price/NAV divergence can all matter. SSE's bond-ETF guide describes same-day
trading and redemption mechanics for bond ETFs, but does not prove a
particular day's executable price or the investor's broker route.

**R2 gate.** Obtain a single source-consistent price/NAV/accrual/distribution
series, historical index membership, actual spreads and commissions, and
market-status/no-fill records. A fund distribution must be booked once and not
added again to a total-return series.

### 510880 — 华泰柏瑞上证红利 ETF

**Verified structure.** The 2025 product summary identifies a stock ETF that
tracks the SSE Dividend Index through complete replication, subject to its
disclosed liquidity exception. It normally invests at least 95% of NAV in
constituents and substitutes. Disclosed annual management and custody fees are
0.50% and 0.10%, and the summary's annual comprehensive operating-cost figure
is 0.60%.

**Operational role and risks.** The product can contribute a diversified
dividend-index exposure, but it remains an equity sleeve: constituent/index
methodology changes, valuation, sector concentration, stock-market drawdowns,
T+1 sale constraint, suspension/limit-lock risk, price/NAV premium-discount
and tracking differences remain relevant. A historical distribution may inform
event accounting only; it cannot be turned into a fixed income, cash-receipt
or reinvestment assumption.

**R2 gate.** Preserve each distribution and corporate action on ex-date and
payment date, use total-return-consistent market or NAV data, model T+1 and
unfilled states, and document index constituent history, free-float/liquidity,
costs and price/NAV deviations.

### 510300 — 华泰柏瑞沪深 300 ETF

**Verified structure.** The captured product summary identifies a stock index
ETF established in 2012 that targets CSI 300 performance through complete
replication. It normally keeps at least 95% in index constituents and
substitutes, and may use a limited set of supplementary instruments and
securities-lending activity as disclosed. The summary states an objective of
daily average tracking deviation within 0.2% and annualized tracking error
within 2% under normal conditions. Management and custody fees are 0.15% and
0.05%; the cited annual comprehensive operating-cost figure is 0.23%.

**Operational role and risks.** This is broad A-share beta, not a stable-return
instrument. Its role in the rule is conditional on the dated price signal. It
shares common A-share, valuation, macro and liquidity drivers with 510880, so
the two must not be treated as independent simply because their index labels
differ. A current price, bid-ask, depth, IOPV premium/discount, halt/limit
state and constituent-event record are still absent.

**R2 gate.** Supply point-in-time index membership, dividend/corporate-action
records, total-return-consistent ETF data, T+1 execution constraints, actual
cost/spread/no-fill observations and a verified overlap/correlation map versus
510880 before a portfolio test.

### 518880 — 华安易富黄金 ETF

**Verified structure.** The 2024 product summary identifies a Shanghai-listed
gold ETF that seeks to track domestic gold spot prices. It invests no less than
90% in Shanghai Gold Exchange-listed gold spot contracts and reports 0.50%
management, 0.10% custody and a 0.68% annual comprehensive operating-cost
figure.

**Operational role and risks.** This sleeve may change the economic driver of
an ETF set, but it remains exposed to domestic gold-price volatility, exchange
trading, premium/discount, valuation and liquidity risk. It is not evidence of
a cash alternative, capital protection or a guaranteed offset to equity losses.
SSE's ETF FAQ categorizes gold ETFs among products that may support same-day
trading; the actual broker/product status needs a current check.

**R2 gate.** Obtain total-return-consistent market/NAV data, SGE/exchange
holiday and suspension records, price/NAV premium/discount history, actual
cost/spread/no-fill inputs, and a stress/correlation mapping against both
equity sleeves and the Treasury ETF.

## Cross-product controls and upgrade path

1. **Do not turn the set into a fixed allocation from product labels.** The
   public-price rule is an observation protocol, and it already fails the
   stable-all-window price threshold.
2. **Use one total-return convention.** Either an independently verified
   total-return series or raw price/NAV plus a dated event ledger is required;
   distributions cannot be added to both.
3. **Separate structure from execution.** Product terms, exchange category and
   market-maker notices do not show historical/current bid-ask, depth, fill,
   broker commission, settlement availability or a user's access.
4. **Refresh dated facts before any paper phase.** The product summaries are
   snapshots, not perpetual facts. Fee, manager, benchmark, lending,
   creation/redemption, tax, trading and market-status terms need a dated
   recheck.
5. **Do not extend the result to futures.** Futures need a separate actual-
   contract, margin, roll, delivery, price-limit and suitability dossier.

Primary raw evidence and hashes:
`sources/official-personal-etf-r1-20260814/manifest.json`. The normalized
field pack is `data/personal_etf_candidate_r1_diligence_20260814.json`.
