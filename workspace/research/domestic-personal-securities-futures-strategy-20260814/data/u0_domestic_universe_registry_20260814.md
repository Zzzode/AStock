# U0 Domestic-Universe Registry

- Registry: DPSFS-U0-v2, version 2.
- Status: **population governance only; no eligible universe, allocation or
  action.**
- Current decision: every class and every potential item remains q=0.

## Purpose

The initial ETF/AU/CU/TA comparison set is not allowed to become the strategy
universe merely because it is convenient to research. This register separates
class discovery from selection. A missing source, product dossier or data feed
means **unresearched/evidence-pending**, not economically rejected.

It covers domestic exchange-listed securities, public funds/REITs and domestic
listed derivatives subject to venue, product, route, data, suitability and risk
gates. It never assumes an individual's access, suitability, tax treatment or
permission to trade.

This draft supersedes DPSFS-U0-v1. A future frozen snapshot must bind the
registry ID/version/SHA-256, population source manifests, query definition,
source-revision cut-off, approvers and timestamp. Any scope, class or gate
change requires a new registry version before outcomes are viewed.

## Class register

| Class | Current state | What exists in this case | Next gate |
|---|---|---|---|
| Direct A-share equities | Unresearched | No class-wide PIT population, corporate-action or issuer packet | Build the official venue population before naming issuers |
| Public REITs | Unresearched | No class-wide master, market/event or underlying-asset archive | Capture the population and asset-type fact packs |
| Listed equity ETFs | Evidence pending | Five illustrative product summaries only | Class-wide PIT master plus ETF event ledger |
| Bond and money-market ETFs | Evidence pending | Illustrative product facts; no defensive/cash-equivalent conclusion | Price/NAV/holdings/event and market-access package |
| Gold and other commodity ETFs | Evidence pending | One illustrative gold product summary only | Underlying exposure and ETF ledger reconciliation |
| Exchange-listed bonds and convertibles | Unresearched | No class-wide master, lifecycle or route evidence | Establish venue/route and terms/event package |
| Commodity futures | Evidence pending | Limited AU/CU/TA source-path samples only | All-commodity census plus actual-contract ledger |
| Financial futures | Unresearched | No class-specific data, rules or route packet | Build product/contract, settlement and access package |
| Listed options | Unresearched | No option-chain, exercise/assignment or route packet | Build full-chain and payoff-risk package |
| Leveraged/inverse listed products | Unresearched | No product population, reset/payoff, route or risk-accounting packet | Build a dedicated class module before it can be considered |

No row is data-qualified. No row is out of scope. A future class can enter only
through the documented intake path in the JSON twin.

## Common admission controls

Every class must pass the same six boundaries before it can be evaluated, still
without implying an allocation:

1. Dated primary identity, venue, lifecycle and trading-status evidence.
2. Authorized point-in-time data with as-of, available-at, revision and raw-hash
   lineage.
3. Complete class-appropriate event, settlement and tradability history.
4. Dated tax, cost, route, limit, suspension and no-fill evidence.
5. Product/issuer/contract economics and risk mapping appropriate to the class.
6. Historical membership/termination preservation and independent R0/R1/risk
   review.

Before any future decision-universe snapshot, the research must freeze its
population source, capture date, query definition, expected count and
reconciliation exceptions. Delisted, expired, renamed, suspended, merged and
terminated items remain in the historical population with their dated state.

Before T2 can be frozen, retain a U0 snapshot hash, per-class population,
qualified and excluded counts, each T2 parent class, the pre-frozen rule and
inclusion/exclusion reason, plus any independently approved exception. A
convenient manual nomination is not a U0-to-T2 derivation.

## Class-specific evidence examples

| Class | Minimum extra evidence before it can become evidence-qualified, still q=0 |
|---|---|
| Direct equities | Historical listed/delisted/ST/suspension master; OHLCV/free-float/actions; issuer filings with publication time; broker, tax, T+1 and no-fill packet |
| Public REITs | Unit/NAV/price/event master; underlying lease/toll/occupancy/cash-flow, sponsor and financing data; liquidity and corporate-action record |
| Equity ETFs | Index history, constituent/rebalance/overlap, price/NAV/IOPV/event, T+1/halts/limits and total-return reconciliation |
| Bond/money ETFs | Holdings/duration/accrual/credit or counterparty record; income/NAV/IOPV/creation-redemption, settlement and stress packet |
| Gold ETFs | Underlying/custody/valuation, market-price/NAV/IOPV/premium-discount, liquidity, holiday mismatch and joint stress record |
| Bonds/convertibles | Terms/lifecycle, coupon/redemption/conversion and credit events; clean/dirty price, accrued interest, quote/depth and route packet |
| Commodity futures | Full product/contract census; effective rules, delivery/position/margin/limit/fee, cross-section, roll/no-fill and broker/suitability packet |
| Financial futures | The actual-contract framework plus settlement, basis/roll and financial-futures-specific position/access controls |
| Options | Full contemporaneous chain including expiries; exercise/assignment/corporate adjustment, margins, quotes, underlying synchronization and payoff accounting |

The JSON registry is authoritative for field-level controls. Nothing in this
document names a preferred product or relaxes the existing R0/R1 gates.
