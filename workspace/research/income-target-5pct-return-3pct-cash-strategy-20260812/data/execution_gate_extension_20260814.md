# Cross-Asset Execution Gate Extension — 2026-08-14

- Status: **blocked; every candidate q=0; no execution authorization.**

A usable strategy cannot treat “China-listed” or “ETF” as a substitute for
current access and execution evidence. Every later named candidate needs a
current, source-labelled access, suitability, tax, settlement, price/NAV,
spread/depth, market-status and adverse-unwind packet.

## Shared hard gates

1. Confirm legal identity, venue, account/fund authority and investor-product
   risk matching.
2. Reconcile gross-to-net fees, taxes, settlement and distribution/interest
   treatment for the actual structure and holder type.
3. Capture the same-session trading state, bid/ask, visible depth, turnover,
   limit status and relevant reference value.
4. Model an adverse exit from observed liquidity; do not assume queue priority,
   full displayed depth, same-day exit or normal trading through a limit or
   suspension.
5. Complete lots, minimum-fee, participation and tax feasibility separately.
   A scale-neutral model does not prove those facts, and no default amount is
   used as a substitute.

## Instrument-specific cautions

- Direct A-shares: price-limit, suspension, resale, float, depth and
  corporate-action states are all required.
- ETFs: same-day turnover is product-specific; current holdings, IOPV/NAV,
  premium/discount, creation/redemption, tracking, lending/derivatives and
  underlying-market risks must be checked.
- Direct Treasury: a CFETS/ChinaMoney identifier does not prove a particular
  account can access the venue or custody route; clean/dirty price, accrual,
  bid/offer, settlement and realized-sale risk must be documented.
- Public REITs: project events, financing, valuation timing, capital raises and
  secondary-market depth can impair exits; a distribution disclosure is not an
  execution or liquidity conclusion.

## SGOV boundary

SGOV is a USD NYSE-listed U.S. Treasury-bill ETF, not a mainland-listed
product. It should not be assumed to be available through a normal onshore
securities account. A lawful offshore route, if one exists, needs a separate
custody, funding/FX, tax, settlement, market-hours and liquidity packet before
it can even be considered for a later research tier.

## Primary policy links

- [SSE Trading Rules](https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml)
- [SSE ETF implementation rules](https://www.sse.com.cn/lawandrules/sselawsrules2025/fund/trading/c/c_20250606_10781071.shtml)
- [SSE public REIT trading rules](https://www.sse.com.cn/lawandrules/sselawsrules2025/reits/c/c_20251231_10803729.shtml)
- [CSRC investor suitability rule](https://www.csrc.gov.cn/csrc/c106256/c1653849/content.shtml)
- [SAFE individual foreign-exchange FAQ](https://www.safe.gov.cn/hainan/2019/0610/964.html)
- [BlackRock SGOV product page](https://www.ishares.com/us/products/314116/ishares-0-3-month-Treasury-bond-etf)

These links define research questions and must be archived/validated at the
later decision date. They do not create a trade, allocation, cash objective or
investment recommendation.
