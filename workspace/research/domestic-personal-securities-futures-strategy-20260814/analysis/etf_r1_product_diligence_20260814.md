# R1 ETF Product Diligence — Initial Comparison Set

## Decision boundary

This is dated product diligence, not a portfolio recommendation. Every named
ETF remains `q=0` and has **no admission**. The comparison set does not exclude
other lawful domestic instruments; no product label, fee, historical
distribution or past public-data output creates a return expectation,
settlement assumption or automatic-reinvestment premise.

| Code | Documented structure | Research description | Current R1 decision |
|---|---|---|---|
| 511990 | Shanghai-listed money-market ETF | Money-market comparison; settlement function unverified | No admission |
| 511010 | SSE five-year Treasury-bond ETF using optimized sampling | Treasury-bond comparison; defensive behaviour unproven | No admission |
| 510880 | Full-replication SSE Dividend Index ETF | Dividend-equity comparison | No admission |
| 510300 | Full-replication CSI 300 ETF | Broad A-share equity comparison | No admission |
| 518880 | Gold ETF with domestic gold-spot exposure | Gold-exposure comparison; diversification behaviour unproven | No admission |

## 511990 — 华宝现金添益 ETF (E01)

### Supported dated facts

The captured product summary identifies a money-market fund and describes its
permitted money-market/instrument range. It states annual management, custody
and sales-service fees of 0.35%, 0.09% and 0.25%. These are fund expenses, not
broker commission, bid/ask, tax or investor net result. The source discloses
market-price/NAV, liquidity, credit, valuation and creation/redemption risks.

### Open evidence and R2 admission gate

No evidence establishes daily per-unit income/NAV history, the applicable
income-booking convention, current premium/discount, spread/depth, market-maker
coverage, broker route, same-day settlement status, tax, actual costs, holdings
or maturity/credit-counterparty exposure. R2 needs a point-in-time income/NAV
and market-price ledger, product/session tradability evidence and dated cost/
no-fill inputs. The product cannot be called cash-equivalent or operationally
available for settlement before those tests pass.

## 511010 — 国泰上证5年期国债 ETF (E02)

### Supported dated facts

The product summary says the ETF tracks the SSE five-year Treasury-bond index
using optimized sampling and normally keeps at least 90% of NAV in index
constituents and substitutes after construction. It states annual management/
custody fees of 0.15%/0.05% and an estimated annual comprehensive operating
expense of 0.21%. Its stated tracking objective is a fund objective, not a
realized holder outcome.

### Open evidence and R2 admission gate

No current holdings, duration, yield/accrual, index-method/constituent history,
distribution ledger, NAV/IOPV/market-price series, liquidity/capacity, current
settlement route, tax or no-fill evidence is archived. No stress, correlation or
drawdown test establishes defensive behaviour. R2 requires source-consistent
price/NAV/event data, dated duration/constituent evidence, execution inputs and
an independently measured cross-asset stress record.

## 510880 — 华泰柏瑞上证红利 ETF (E03)

### Supported dated facts

The summary identifies a stock ETF tracking the SSE Dividend Index through full
replication subject to its stated liquidity exception, normally with at least
95% of NAV in constituents and substitutes. It states annual management/custody
fees of 0.50%/0.10% and an annual comprehensive operating-cost figure of 0.60%.

### Open evidence and R2 admission gate

The archive has no point-in-time constituent, sector or factor exposure; index
method-change record; dividend-versus-fund-distribution ledger; total-return
ledger; price/NAV, spread/depth, T+1/session-status or no-fill data. The
“dividend” label does not establish income, distribution reliability or lower
risk. R2 requires those records plus a dated overlap and stress analysis versus
510300 before either product may be mapped into a common or separate risk group.

## 510300 — 华泰柏瑞沪深300 ETF (E04)

### Supported dated facts

The captured summary identifies a CSI 300 stock-index ETF using full
replication, normally with at least 95% in constituents and substitutes. It
describes that the fund may participate in securities lending, but the captured
summary does not establish a lending limit, utilization or resulting income. It
states management/custody fees of 0.15%/0.05% and a cited annual comprehensive
operating-cost figure of 0.23%.

### Open evidence and R2 admission gate

No point-in-time CSI 300 membership, historical exposure, securities-lending
use, event/distribution ledger, total-return ledger, price/NAV/liquidity/
capacity, route-specific T+1 mechanics, tax/cost/no-fill data or measured
overlap/correlation/stress record versus 510880 is archived. Broad-equity beta
is an exposure description, not a stable-return property. R2 requires all of
those fields and a dated look-through assessment before risk grouping.

## 518880 — 华安易富黄金 ETF (E05)

### Supported dated facts

The summary identifies a domestic gold ETF seeking to track Shanghai Gold
Exchange-listed gold spot contracts, with no less than 90% in that exposure. It
states annual management/custody fees of 0.50%/0.10% and a 0.68% annual
comprehensive operating-cost figure. The source describes gold-price, market,
premium/discount, liquidity and valuation risks.

### Open evidence and R2 admission gate

There is no archived historical underlying-contract/cash exposure, custody or
valuation record, NAV/IOPV/market-price total-return ledger, premium/discount
or spread/depth history, holiday/suspension data, tax/broker/no-fill data or
equity-correlation/stress evidence. Gold exposure does not establish
diversification or an offset property. R2 requires those records and a joint
stress test with the equity ETFs and 511010.

## Cross-product control

The SSE FAQ distinguishes stock-ETF T+1 mechanics from categories of bond,
gold and money-market ETFs that may support same-day trading; individual product
and broker status still need a current check. The frozen four-ETF public-series
diagnostic covers 510300/510880/518880/511010, but its replay input declares
`forward_adjusted_or_unknown` and its protocol was exploratory after source
capture. Its numerical output is therefore **not admissible** as total-return
or execution evidence. See `data/etf_public_price_falsification_20260814.{md,json}`.

Primary sources: `sources/official-etf-r0-20260814/manifest.json`. Every named
product remains outside T2/T3/T4 until its stated R2 gates pass.
