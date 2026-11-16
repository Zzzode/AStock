# Formal Replay Feasibility and Gap Assessment

- Scope ID: `total-return-open-universe-v3-20260814`
- As of: `2026-08-14`
- Status: **VETO — formal replay is not currently testable; all candidates and the portfolio remain `q=0`.**

## What the current record does and does not show

The frozen four-ETF public-price diagnostic is a useful negative result, not a
strategy backtest. Its 207 failures among 633 complete rolling five-year
*price* windows reject that static vector as evidence for the conditional 5%
total-return objective. The public input has neither total-return events nor
cost, tax, historical market-status, point-in-time-universe or execution
coverage.

An independent official CSI index discovery cross-check produces the same
negative decision. None of its six predeclared broad-equity, dividend or
published equity--bond references clears every observed rolling-five-year
index-value window; the closest 30/70 reference still records 32 misses out of
999 and a 4.43% minimum. This is stronger sourcing but still weaker than an
investor-level net-TWRR replay.

Two additional blockers matter just as much:

1. No named licensed source, entitlement or accountable data-owner record is
   configured for the required historical cross-asset data.
2. The existing portfolio simulator is intentionally discrete-lot based. It
   cannot answer this scale-neutral research question. A unitized replay must
   be a separate deterministic layer with proportional costs and no fixed-lot
   assumption.

## Required evidence hierarchy

| Layer | Required use | Boundary |
|---|---|---|
| Authorised system of record | Point-in-time calendar, raw prices, master/history, halts, limits, actions, fund/REIT distributions and bond cash events | Require source owner, entitlement and immutable raw archives. |
| Primary reconciliation | Exchange, issuer/fund-manager/REIT-manager, ChinaClear, venue and broker records | Validates selected events and mechanics; is not itself a scalable historical replay feed. |
| Frozen public observation | Discovery and sensitivity only | Cannot produce a formal return result or an allocation. |

The public record confirms that total-return series are a distinct methodology:
CSI describes its total-return indices as incorporating cash-dividend
reinvestment, while ChinaBond exposes a separate wealth/total-return index
dimension. These references identify useful reconciliation sources; they do
not replace an investable, cost-aware, point-in-time cross-asset ledger.

## The build gate, in order

1. Freeze a deterministic `OU-TR5` rulebook before examining a performance
   result: eligibility, availability/published-at controls, selection and
   substitution, weights, rebalancing, no-fill, event accounting, cost/tax
   convention and B0/B1 comparators.
2. Select and test one authorised system-of-record source against every
   required field. Archive raw results with `as_of`, `available_at`, source
   owner and content hash.
3. Build a unitized, scale-neutral daily-value simulator. Keep later lots,
   minimum fees, tax residency, account access and capacity in a separate
   feasibility gate.
4. Add or block structure-specific events. An unhandled rights issue, merger,
   spin-off, conversion, non-cash delisting, fund/REIT distribution or bond
   redemption must block that period, not be guessed.
5. Reconcile adversarial examples before broad testing: a cash distribution,
   share distribution, non-standard action, halt, limit lock, delisting and
   fund/REIT event.
6. Run a predeclared training/holdout and walk-forward protocol. Report every
   complete rolling and non-overlapping five-year out-of-sample result,
   including all misses.

## Scope control

The local strategy catalog does not create a shortcut. Its A-share factor and
earnings-event entries are draft, research-only target constructors without a
frozen point-in-time total-return replay. Its domestic-futures CTA path is a
separate conditional scope and public continuous futures series are explicitly
not executable historical roll evidence. Adding futures, options, offshore or
institutional long-short strategies would be a separate mandate, not a silent
repair to this strategy.

No allocation, cash-receipt objective, automatic reinvestment rule or order is
created by this assessment. The sole research objective remains conditional
and ex post; it is not a guarantee.

## Reference entry points

- [CSI 300 methodology — total-return treatment](https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/en/000300_Index_Methodology_en.pdf)
- [ChinaBond index query — total-return dimension](https://yield.chinabond.com.cn/cbweb-mn/indices/single_index_query)
- [Tushare daily-data documentation](https://tushare.pro/document/1?doc_id=27)
- [SZSE data-services overview](https://www.szse.cn/English/services/dataServices/index.html)
- [SSE public-data catalogue](https://www.sse.com.cn/market/publicdata/)
