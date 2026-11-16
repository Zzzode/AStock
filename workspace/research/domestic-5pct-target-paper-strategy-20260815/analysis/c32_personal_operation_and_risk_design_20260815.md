# C32 — Personal Operation and Risk-Control Design

- Artifact ID: `D5PT-C32-v1`
- As of: `2026-08-15`
- Status: `research_only_not_admitted`; `formal_decision_eligible=false`; `external_orders=false`
- Scope: a fail-closed, paper-only operating card for the frozen R01 five-ETF benchmark. It is not an investment-committee decision, an account instruction, or a suitability finding.
- Data quality: derived from frozen artifacts through 2026-08-15. No live quote, product-change, account-access, fee, or settlement input was used; every action-date field must be re-evidenced or the result is `NO_ACTION`.

## 1. Primary recommendation and evidence boundary

The only current C32 action is `NO_ACTION`: retain the five-ETF design as a controlled paper-observation candidate, do not activate an external transaction, and keep futures at zero weight. The long-run annualized 5% objective is a research hurdle only; it is neither a forecast nor a promised outcome.

This conservative status is evidence-led. As of 2026-08-15, R01 is a defined monthly paper benchmark, but its market-price proxy has four complete calendar years below 5%, only 37 of 81 eligible rolling five-calendar-year endpoints at or above 5%, and a -24.94% maximum drawdown proxy. The independent reconstruction validates the bounded arithmetic, not investor results or stable performance. The case disposition is `NO_ADMITTED_USABLE_STRATEGY`. [M01](m01_dynamic_market_price_proxy_20260815.md), [R02](r02_independent_m01_r01_audit_20260815.md), and [R07](r07_current_open_universe_disposition_20260815.md), all dated 2026-08-15.

This document specifies how a future observer would make a paper record without inventing a price, fill, product substitution, settlement result, or personal permission. It does not turn the R01 benchmark into an admitted strategy.

## 2. Frozen candidate universe, target map, and hard exclusions

The only named candidates in this operating card are the five R01 instruments below. Their role is a dated research fact from P01; it is not a statement that they are presently tradable or suitable for any person.

| Sleeve / status | Candidate code(s) | Conditional R01 role | C32 action status |
|---|---|---|---|
| Equity | `510300` and `510880` | One equity sleeve; split equally whenever selected | Both legs must pass together; no substitution or single-leg expansion |
| Bond | `511010` | One bond sleeve | May only be a paper action after all gates pass |
| Gold | `518880` | One gold sleeve | May only be a paper action after all gates pass |
| Defensive fallback | `511990` | Full target only when no risk sleeve is selected | May only be a paper action after all gates pass |
| Futures, options, financing, shorting, direct stocks, REITs, direct bonds, other funds | None | Not in R01 | `0%`; no action |

The R01 target map is frozen. It is a target calculation for a future paper run, not a current allocation or an authority to act.

| Positive R01 sleeves at the observation date | 510300 | 510880 | 511010 | 518880 | 511990 |
|---|---:|---:|---:|---:|---:|
| Equity, bond, gold | 16.67% | 16.67% | 33.33% | 33.33% | 0% |
| Equity, bond | 25% | 25% | 50% | 0% | 0% |
| Equity, gold | 25% | 25% | 0% | 50% | 0% |
| Bond, gold | 0% | 0% | 50% | 50% | 0% |
| Equity only | 50% | 50% | 0% | 0% | 0% |
| Bond only | 0% | 0% | 100% | 0% | 0% |
| Gold only | 0% | 0% | 0% | 100% | 0% |
| None | 0% | 0% | 0% | 0% | 100% |

Source: [R01](r01_monthly_dynamic_etf_paper_rulebook_20260815.md), dated 2026-08-15. C30's separate non-admitted semiannual fixed-weight research protocol is not an alternate C32 action map. It cannot replace R01, introduce a new cadence, or supply a substitute target without a new version and independent review.

C31's dated refresh keeps these same five exact codes as the C30 core and explicitly keeps `510500`, `511180`, and `511380` outside it. That product refresh does not validate an action-date quote, access, fee, settlement, or fill, so it does not relax any C32 gate. [C31](c31_etf_product_diligence_refresh_20260815.md), dated 2026-08-15.

### Version-separation control

`D5PT-R01-v1` is the only target map and monthly D/E action card specified by C32. `D5PT-C30-PROTOCOL-v1` is a separate, non-admitted semiannual fixed-weight research protocol. C33 may not combine R01 signals with C30 weights or cadence, nor use C30 results to alter R01. If it wants to consider C30 as an action card, it must create its own matching operating design and meet its independent-review and forward-paper gates.

## 3. Calendar, signal, and candidate paper-action sequence

1. **Observation date D — monthly.** After the close of the final common trading session in each calendar month, retain the five source rows, source locations, response hashes, available-at timestamps, product/status checks, and the 252-common-observation signal calculation. A missing, duplicate, stale, semantically changed, or non-common input makes the cycle `NO_ACTION`.
2. **Freeze the target.** Select only sleeves with strictly positive R01 trailing changes. Equal-weight selected sleeves, retain the fixed 50/50 split within equity, and use the fallback only if none is positive. No discretionary override, ranking, lookback change, product replacement, leverage, short position, future, or option overlay is permitted.
3. **Earliest paper-action date E.** A target formed at D may be considered only on the next common trading session. Same-session action is prohibited. Before recording E, re-run the pre-action controls in Sections 4–6.
4. **Candidate action vocabulary.** The only permitted ledger labels are `paper_increase`, `paper_reduce`, `paper_exit`, `paper_hold`, `no_action`, and `suspended`. Each is a paper ledger label; none creates, routes, amends, or cancels an external order. At the current non-admitted status, only `no_action`, `paper_hold` for historical ledger continuity, and `suspended` are available.
5. **Post-cycle reconciliation.** On each E cycle, record the target, intended and rounded quantities, eligible quote evidence, event/fee/tax/settlement fields, actual paper result or `NO_ACTION`, residuals, and a reconciliation result. A target is never treated as a result.

## 4. Paper-order, lot, price-protection, and price-limit controls

The following controls apply only to a future, independently authorized paper observation. They are deliberately stricter than a price-series calculation.

| Control | Required paper record / fail-closed treatment |
|---|---|
| Evidence identity | Rule version, source hash, observation and decision timestamps, product legal-document version, temporary-announcement check, venue and market-state fields |
| Side and size | Candidate action, prior and target weights, side, pre-action quantity, target quantity, rounded quantity, and residual quantity. No order identifier is generated because no external order exists. |
| Lot and tick | P01 records the SSE ETF FAQ, captured 2026-08-15, as category-level reference for a normal 100-share lot and CNY0.001 tick. Each paper action must nevertheless retain the product-, venue-, account-, and date-specific lot/tick evidence. Round each target **down** to the verified lot; a change below one verified lot is `NO_ACTION` and the residual is separately logged. |
| Limit-price protection | No paper market order and no close-price fill. With a same-session IOPV and two-sided quote, `buy_cap = IOPV × 1.003` and `sell_floor = IOPV × 0.997`; round each to the verified tick. A paper buy can be recorded only at the displayed ask at or below `buy_cap`; a paper sell only at the displayed bid at or above `sell_floor`. These are paper price-protection rules, not claims of executable liquidity. |
| Daily price-limit / halt state | Retain the product-date `price_limit_state`, applicable-rule version, halt state, and visible two-sided depth. If an instrument is limit-locked, halted, outside the valid session, has only unusable depth, or lacks a verified state, record `NO_ACTION`; never infer a fill from a close or an indicative quote. C32 does not assert a universal limit percentage. |
| Atomic equity sleeve | `510300` and `510880` must both meet the controls for a planned equity action. A failure in either leg makes the entire scheduled rebalance `NO_ACTION`; the surviving leg is not enlarged. |
| Partial and no-fill treatment | Visible depth alone cannot establish a partial fill. Until a future ledger has a frozen, independently checked partial-fill method, an incomplete planned rebalance is `NO_ACTION`. If a later paper protocol validly models a partial result, it must retain filled quantity, unfilled residual, evidence source, and cancellation status; it may not book the target as filled or perform an intraday catch-up. |
| Missing data | Missing IOPV, bid/ask, status, fee, tax, settlement, account, or product-document evidence causes the entire scheduled rebalance to be `NO_ACTION`. No similar product, historic quote, NAV, close, or later observation may fill the gap. |

The 100-share/CNY0.001, T+1/T+0 category references and the IOPV gates are drawn from P01/R01 dated 2026-08-15. P01 explicitly limits the former to category guidance and does not establish an individual account, broker, product state, fee, settlement result, or fill. [P01](p01_core_etf_product_diligence_20260815.md); [R01](r01_monthly_dynamic_etf_paper_rulebook_20260815.md).

## 5. T+1, T+0, and settlement discipline

The category facts below are dated references, not standing permissions. The paper ledger defaults to the more restrictive treatment whenever the action-date record is incomplete.

| Candidate category | Dated reference | C32 paper rule |
|---|---|---|
| `510300`, `510880` equity ETFs | P01 cites the SSE ETF FAQ captured 2026-08-15 as classifying equity ETFs as T+1 | Newly acquired paper units receive an earliest-sellable field no earlier than the next trading session. Same-session reversal of a new unit is prohibited. |
| `511010` bond ETF; `518880` gold ETF; `511990` money-market ETF | P01 cites the same FAQ as saying these ETF categories may support T+0 | Set `same_day_roundtrip_allowed=false` unless the specific product, venue, account, settlement, and availability records on E establish otherwise. No presumption of same-day reuse, sale, or availability. |
| All candidates | P01 and R01 require action-date confirmation | Retain `sellable_at`, `settlement_status`, `availability_status`, and the source/version for each planned leg. If any is unavailable or contradictory, the scheduled rebalance is `NO_ACTION`. |

This structure prevents a category label from being mistaken for a present operating right. It also means that a price-limit lock, a suspension, or a settlement exception can prevent a paper exit from being booked; C32 never manufactures an exit price to make the ledger look complete.

## 6. Instrument admission, removal, and resumption gates

### Current admission state

No instrument is currently admitted for a usable strategy. The five ETF names are a frozen paper-benchmark universe only. C32 therefore does not select, initiate, expand, reduce, or exit an external position.

### Necessary gates before a future paper action

All gates must pass together; passing one does not cure another.

1. **Rule and evidence identity:** an unchanged, independently reproducible rule version; D-source rows, hashes, timestamps, and a next-session E decision record.
2. **Product evidence:** current dated legal document, temporary-announcement, code/name, objective, fee, listing/trading status, and material-change review for every planned product; a generic ETF FAQ is insufficient.
3. **Personal-operability evidence:** action-date account eligibility, product access, verified lot/tick, settlement/availability, expected fee and tax fields, and usable market session must all be retained. C32 does not infer these facts.
4. **Quote and protection evidence:** bid, ask, IOPV when applicable, depth, market state, price-limit/halt state, and the Section 4 price protection must all pass.
5. **Target integrity:** all required legs satisfy the target map; the equity pair is atomic; no residual is silently redirected; no unapproved instrument is added.
6. **Control integrity:** a reconciled prior paper ledger, no unresolved exception, no operational stop, and a recorded maker-checker release.
7. **Forward validation:** at least six uninterrupted monthly paper observations, with source, quote/state, fee/tax/event/settlement, result/no-action, and reconciliation records, followed by independent review.

### Removal, suspension, and resumption

Any of the following creates `suspended` or the scheduled-cycle `NO_ACTION`, rather than a replacement, artificial exit, or revised parameter: material legal-document, fee, objective, underlying, listing, or trading-status change; delisting or extended halt; source or data-semantic change; missing price/IOPV/status evidence; account or settlement failure; unreconciled ledger; a price-limit lock; or a rule change.

Resumption requires a dated evidence refresh, a documented cause-and-remedy record, a reconciled ledger, and independent release. A rule, target map, product set, or protection-threshold change is a new version and resets the forward-paper observation clock; it cannot be backfilled into R01.

## 7. Diversification, concentration, and exposure caps

The design manages overlap before it labels products diversified:

- The equity pair is one economic sleeve. `510300` and `510880` each remain 50% of that sleeve and cannot be treated as independent diversification or be used to replace a failed counterpart.
- R01 is capped at five named ETF candidates, three risk sleeves, and one defensive fallback. No direct stock, REIT, direct bond, open-ended fund, option, future, financed exposure, short exposure, or unapproved substitute can coexist in this rule version; each has a `0%` C32 weight.
- The fixed R01 map can reach a 100% target in a single bond, gold, or fallback ETF state. That is a concentration exposure, not a diversification assertion. Before any future paper action at such a target, a `single_instrument_concentration_review` must be retained with the current product, quote, trading-state, and settlement evidence. A failed review is `NO_ACTION`, not an ad hoc cap override or a substitute.
- C32 imposes no invented lower numerical concentration cap on the frozen R01 target map. Adding one in response to an observed result would change the rule and requires a new version, independent reconstruction, and a new forward-paper record.
- No other strategy can be combined with R01 to offset or improve its results while no strategy is admitted. Risk sleeves must be aggregated by economic exposure so the equity pair is not double-counted.

## 8. Drawdown controls and operational stops

Drawdown is measured only on the reconciled paper unit ledger: `DD_t = U_t / max(U_0 … U_t) − 1`, after recorded fees, taxes, events, and valid paper results. It is not a statement about an external account result.

| Trigger | Required control response | Explicit non-response |
|---|---|---|
| `DD ≤ -12%` | Mark `amber_review_required`; independently check inputs, product documents, fees/taxes, quotes, settlement, events, and reconciliation before the next scheduled cycle. | Does not revise signals, weights, or create a stop-sale. |
| `DD ≤ -18%` | Mark `red_operational_pause`; block new candidate paper actions until an independent control review releases the pause. Preserve the ledger and all evidence. | Does not invent a liquidation, use an unverified price, or change the frozen target map. |
| Any hard operational exception | Immediately mark `suspended` or `NO_ACTION`: missing/contradictory data, data-semantic change, failed document/status check, account or settlement failure, price-limit lock/halt, missing IOPV or two-sided quote, unreconciled ledger, or unapproved rule/product change. | Does not use historic data, a close, a NAV, or a similar product as a substitute. |

The -12% and -18% review thresholds are inherited from R01's frozen paper risk controls, dated 2026-08-15. They are governance triggers, not a claim that loss can be limited. The operational pause intentionally stops new paper entries rather than forcing an exit in conditions where T+1, a limit lock, or a halt could make an asserted exit unobservable. [R01](r01_monthly_dynamic_etf_paper_rulebook_20260815.md).

## 9. Futures decision: excluded at zero weight

Futures are excluded from C32. C16's three-family actual-contract settlement diagnostic produced a 1.97% annualized gross settlement-mark change, 0 of 24 eligible rolling endpoints at or above 5%, and several source-covered calendar years below the hurdle. C17's separately frozen five-family diagnostic produced 2.08%, 0 of 24, and several below-hurdle years. Both omit fills, costs, margin, account access, price-limit lock outcomes, delivery, and other execution facts. Their independent audits validate the bounded calculations, not an action-ready strategy. [C16](c16_actual_contract_settlement_diagnostic_20260815.md), [C17](c17_diversified_actual_contract_settlement_diagnostic_20260815.md), [R04](r04_independent_c16_audit_20260815.json), and [R05](r05_independent_c17_audit_20260815.json), all dated 2026-08-15.

The future switch is therefore `off`, with `futures_weight=0%` and `futures_action=no_action`. It cannot be used to seek the 5% hurdle, soften a drawdown, or fill a missing ETF action.

It may be reconsidered only as a distinct, pre-calculation hypothesis that first supplies, for every actual contract and action date: product/contract diligence; contract multiplier and tick; price-limit, margin, position-limit, fee, session, and settlement versions; lifecycle, delivery/last-trade, and roll buffers; account eligibility and access evidence; quote/depth and no-fill records; a fixed sizing and aggregation method; independently reproducible net-of-all-recorded-frictions research; and uninterrupted forward paper observation with independent review. A successor cannot retune C16 or C17 after their negative screens.

## 10. Minimum monthly paper record and evidence references

An observer must be able to archive the following without a broker connection:

1. D-date signal packet: raw rows, hashes, source/available-at time, eligibility, positive sleeves, and frozen target map.
2. E-date control packet: product evidence, account/settlement fields, bid/ask, IOPV, depth, price-limit/halt/market state, lot/tick, price-protection calculation, and expected cost fields.
3. Candidate-action packet: prior state, target state, rounded quantities, residual, action or `NO_ACTION`, exception reason, and no-substitution attestation.
4. Reconciliation packet: event, fee/tax, settlement, ledger-unit, drawdown, operational-stop status, reviewer, and release or escalation record.

| Evidence | Date / provenance | What it supports | What it does not support |
|---|---|---|---|
| P01 core ETF diligence | Official product documents with dates from 2025-06-21 to 2026-06-19; SSE ETF FAQ captured 2026-08-15 | Dated product roles, category-level lot/tick/T+1/T+0 context, and fail-closed checks | Current quote, fill, fee, account eligibility, settlement result, or personal suitability |
| R01 rulebook | 2026-08-15 | Monthly D/E timing, target map, IOPV gates, lot rounding, no-substitution, risk reviews | Stable result or practical execution proof |
| M01 and R02 | 2026-08-15 | Bounded price-proxy outcomes and independent arithmetic reconstruction | Total return, investor result, or stable annual outcome |
| R07 disposition | 2026-08-15 | Current bounded non-admission state | A claim that every future domestic strategy fails |
| C16/C17 and R04/R05 | 2026-08-15 | Futures exclusion under the observed gross diagnostics | Futures access, net performance, or future result |
| C30 candidate protocol | 2026-08-15 | A separate non-admitted static research protocol and its version boundary | A substitute R01 action map or an admitted strategy |
| C31 ETF refresh | 2026-08-15 | The exact five-code core and dated product/venue evidence boundary | Action-date terms, access, quote, fill, or settlement |

## 11. Decision-use restriction

This is a C32 design input for later C33/R15 integration. It cannot on its own produce an `APPROVE`, an eligibility conclusion, a return conclusion, or an external transaction. Any such conclusion requires the completed shared packet, product refresh, independent review, and forward-paper evidence described above.
