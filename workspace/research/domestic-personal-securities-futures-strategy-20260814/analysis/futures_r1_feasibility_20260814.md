# R1 Commodity-Futures Feasibility — Actual-Contract Research Path

## Current decision

Commodity futures are not a current sleeve. `AU`, `CU` and `TA` are research
families only; each has `q=0`, no selected contract, no risk budget and no
action. Twelve retrospectively retrieved raw official daily-file samples (six
dates per exchange) show a better source-inspection path than a public
continuous series. They do not establish point-in-time availability, a return,
an executable roll, user suitability or transaction feasibility.

| Family | Retained actual-contract evidence | Economic research question | Current decision |
|---|---|---|---|
| AU | Six SHFE daily-file samples (F05) | Could a precious-metal contract add a distinct realised driver after full tests? | No admission; `q=0` |
| CU | Six SHFE daily-file samples (F05) | Could an industrial-metal contract add a distinct realised driver after full tests? | No admission; `q=0` |
| TA | Six CZCE daily-file samples (F06) | Could a petrochemical contract add a distinct realised driver after full tests? | No admission; `q=0` |

## AU — SHFE gold futures family

### What the retained evidence supports

The six retrospective SHFE sample files include actual AU contract rows with
daily OHLC, prior settlement/settlement, volume, open interest and turnover
fields (F05; `data/futures_exchange_data_access_probe_20260814.{md,json}`).
This supports inspection of actual listed contracts rather than a continuous
proxy. It does not support an AU return, a preferred contract, a roll or a
margin/fill assumption.

### Unavailable rule/execution facts

The direct AU product-rule URL is recorded as WAF/challenge blocked in metadata
probe PX01; no response body was retained. Therefore the effective-date-specific
contract unit, tick, listing/last-trade schedule, delivery restriction, margin,
limit, position-limit and fee terms are **unverified** in this case. No such
term may be filled from memory, a later rule version or a generic SHFE rule.

### R2 admission gate

Archive a dated official AU rule and lifecycle master, then bind every rule and
exchange/broker fee/margin term to its effective session. Retain full daily
cross-sections, tradability/limit/delivery states and broker-route evidence;
freeze a delivery-buffer, contract-choice and no-fill rule before observing a
replay outcome. The family remains `q=0` until independent R0/R1/risk review.

## CU — SHFE copper futures family

### What the retained evidence supports

The same six retrospective SHFE sample files contain actual CU contract rows
with the observed daily price, settlement and liquidity fields (F05). This is
source-path evidence only and cannot replace a point-in-time contract master or
an actual-contract P&L ledger.

### Unavailable rule/execution facts

The direct CU rule URL is recorded as WAF/challenge blocked in PX02; the
response body was not retained. Contract unit, tick, listing/last-trade and
delivery dates, margin, limits, position constraints and applicable fees must
therefore be treated as unavailable, with a dated effective-rule source required
for every eventual contract/session.

### R2 admission gate

Obtain an authorized, hash-bound CU rule/lifecycle archive and full daily
cross-section with effective margin/limit/fee fields. Test a predeclared
contract selection, roll, delivery-buffer and no-fill convention using actual
settlement marking and dated broker terms. Neither current daily rows nor a
continuous series authorizes an allocation; `q=0` remains.

## TA — CZCE PTA futures family

### What the retained evidence supports

Six retrospectively retrieved CZCE sample files contain actual TA contract rows
with prior settlement, OHLC, settlement, volume, open interest and turnover
fields (F06). They establish neither original-date availability nor a complete
history of tradability, lifecycle or execution inputs.

### Unavailable rule/execution facts

The direct PTA rule PDF URL returned HTTP 404 in metadata probe PX03; no body
was retained. The effective contract unit, tick, listing/last-trade/delivery
schedule, margin, price-limit, position-limit and fee terms are unavailable in
the local R1 pack. No generic commodity or current rule may be backfilled into
this gap.

### R2 admission gate

Capture a dated authorized PTA rule and lifecycle record, then retain daily
actual-contract cross-sections with contemporaneous status, margin, limits and
fees. Apply a frozen selection/roll/no-fill protocol and broker-route review
before any cost-aware paper ledger. The family remains `q=0`.

## Common data and execution boundary

The CZCE interface material documents actual-contract, quote and market-status
field concepts (F02), while the SHFE materials state information-rights
boundaries (F03/F04). The vendor documentation lists relevant field families
(D01), but none of these sources gives this case a token, retention right,
point-in-time vintage, full rule history, historical bid/ask, broker fee/margin,
limit-lock, delivery eligibility or fill record.

Before a formal test, retain full daily cross-sections and a point-in-time
lifecycle/rule archive; freeze selection, delivery buffer, roll, cost, collateral
and no-fill logic; then run a unitized settlement-to-settlement paper replay
with every complete rolling five-year endpoint disclosed. Until those steps pass
independent review, no futures family can leave `q=0`.
