# Return-Source Feasibility Note — 2026-08-14

## Decision boundary

This note separates economic return sources from product labels. It is a
research hypothesis map, not a portfolio, target allocation, holding list,
return forecast or action. Every class and initial comparison item remains
`q=0`.

The 5% figure is a strict historical, cost-aware rolling-five-year TWRR hurdle
for a future formal replay. It is not a promise, annual floor or probability
statement.

## What the current market context rules out

ChinaBond's 2026-08-13 government curve was 1.1915% at three months, 1.4009%
at five years and 2.1598% at 30 years (M01). A yield curve is neither a
tradable investor return nor an ETF result. It nevertheless rules out treating
unlevered government-curve carry alone as evidence for a stable 5% annual
total-return outcome. A bond ETF can also experience duration, price/NAV,
liquidity and execution outcomes that differ from the curve.

Consequently, a potentially viable research architecture cannot simply relabel
a cash or Treasury sleeve as a 5% strategy. Any incremental return hypothesis
must identify the risk that produces it and survive the same total-return,
cost, tradability and stress tests.

## Open return-source map

| Economic source under research | Candidate domestic implementation families | What must be demonstrated before consideration | Current state |
|---|---|---|---|
| Short-rate / government-curve carry and duration | Money-market and Treasury-bond ETFs; exchange-listed bonds | Total-return event accounting, duration and holdings history, price/NAV/IOPV, route, cost, no-fill and rate-stress evidence | No family admitted; illustrative 511990/511010 cards only |
| Broad equity and quality/dividend risk | Direct A-share equities; broad and dividend equity ETFs | Point-in-time population/constituents or issuer data, corporate actions, T+1, liquidity, overlap, concentration and stress tests | No issuer or product admitted; illustrative 510300/510880 cards only |
| Real-asset / commodity price exposure | Gold and commodity ETFs; actual commodity futures contracts | Underlying exposure, price/NAV/IOPV or actual-contract lifecycle, margin/limit/roll, delivery, cost and no-fill evidence | No product or contract admitted; 518880 and AU/CU/TA are research probes only |
| Credit / contractual cash-flow exposure | Exchange-listed bonds, convertibles and public REITs | Terms, issuer/underlying cash-flow, credit/financing, lifecycle, distribution/event, liquidity, tax and stress evidence | Unresearched U0 classes; no named product |
| Derivative risk transfer / trend response | Actual commodity or financial futures; listed options where separately justified | Full actual-contract or option-chain history, rules, margin, settlement, route/suitability, capacity and payoff accounting | Unresearched or evidence-pending; no derivative action |

The entries are deliberately economic families rather than a finite product
universe. DPSFS-U0-v2 keeps direct equities, public REITs, listed bonds,
financial futures and options open as unresearched classes; absence of a local
dataset is not an economic rejection.

## Falsifiable strategy architecture

A future strategy test must establish all of the following, in this order:

1. A defensive/settlement sleeve has a measured, not assumed, total-return and
   execution record. Its role is risk control, not a pre-asserted 5% yield.
2. Each return-seeking sleeve has a separately frozen economic rationale,
   class-neutral U0-to-T2 selection rule, cost/no-fill model and stress record.
3. The combined portfolio passes the strict all-endpoint and primary-holdout
   rolling-five-year net-TWRR hurdles after every fee, tax, FX, settlement,
   margin and unfilled-order effect is recorded.
4. A paper-reconciliation period confirms that the declared data/execution
   model does not rely on fictional fills, duplicate capacity or unavailable
   cash/lot collateral.

Failure at any stage leaves the relevant sleeve and the combined strategy at
`q=0`. There is no numerical allocation until the formal replay and its risk
controls are completed.

## Evidence references

- M01 — ChinaBond government-curve observation, retained in
  `sources/official-market-context-r0-20260814/`.
- E01--E05 — dated ETF product-fact cards; see
  `analysis/etf_r1_product_diligence_20260814.md`.
- F05--F06 — retrospective actual-contract source-path samples; see
  `analysis/futures_r1_feasibility_20260814.md`.
- DPSFS-U0-v2 — class-neutral domestic universe governance.

