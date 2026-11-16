# Unresolved Requirements

The completion decision is do_not_mark_complete. The JSON twin specifies
field-level requirements for ETF events, actual futures contracts, costs,
pre-registration and independent paper validation. Any missing block keeps the
affected sleeve at q=0.

UR04 is expanded by the formal replay-protocol requirements, including the
rolling-window statistic, endpoint status, expected-versus-actual endpoint-count
equality, CROSSING/all-history partition treatment, unitized accounting,
execution state-machine, a nonempty primary-holdout endpoint rule, parameter log
and deterministic run bundle. It additionally requires an executable
primary-holdout predicate and invalidation rule, overlap-dependence disclosure
with predeclared non-overlapping/regime/stress summaries, an allowed
state-transition matrix, and a hash-bound risk-and-feasibility pack with
numerical limits and pass/fail logic. It must additionally be cross-bound in
one canonical freeze record with the lockbox/predicate, input/revision,
code/runtime/command and first-outcome-view fields. UR05 also
requires both calendar-duration and distinct-observation thresholds together
with field-level materiality rules, the U0 population/class-neutral universe
audit, risk/feasibility pass-fail review and a reviewed exception log. A
state/configuration coverage matrix must give every applicable class, route,
term set, transaction type and material transition an observed, accepted-
conservative, source-proven-not-applicable or blocking-unvalidated disposition.
A
research-only usable-strategy label is unavailable unless all return, holdout,
coverage, data, feasibility, route/cost, paper-reconciliation and independent
review gates pass together.

UR03 also retains order-side/timestamp/route/quote/settlement causality, an
immutable cash-collateral term-set identity and a monotonic order-state-
transition ledger as open requirements. It additionally requires typed dated
broker/tax terms with route/account/instrument-or-product scope, effective
range and jurisdiction; a separate execution-state versus settlement-state
ledger with a deterministic end-run carry/cancel treatment; immutable per-fill
quantity, price, currency and time linked to fee/tax and settlement events; an
event-type-to-application-role mapping with component/currency reconciliation;
and T+1, lot/reservation and transaction-time cash/margin feasibility evidence.
It now explicitly includes each fill's linked state transition, cumulative and
residual quantity, quote-depth/capacity consumption and impact/proxy evidence;
the dated fee/tax output currency and any frozen FX conversion; and a
decision/submission/fill reservation-pool audit. An unfilled sell reservation
may reduce available-to-sell capacity, but must never reduce the economic
position, marked value or NAV.

UR04 additionally requires that the canonical freeze bind every replay,
order, ledger and endpoint row; each endpoint retain its calendar anchor,
selected start/end ledger, elapsed days, candidate roster and count audit; and
the accounting data model reconcile unitization, positions/lots/marks,
cashflow/P&L and residuals. UR05 cannot close while any prospective
configuration/state-coverage row is unresolved or while independent fill,
fee/tax, settlement, unitization or endpoint-population reconciliation is
missing.
The endpoint record must distinguish calendar anchor `a`, selected start
valuation `s` and endpoint valuation `e`; annualized TWRR is based on unit NAV,
not a total-NAV ratio when external flows exist. Candidate-status counts and a
zero-population state must reconcile. A PRIMARY_HOLDOUT start state needs
post-lockbox, row-level component membership rather than aggregate hashes.
The canonical frozen-run hash and all other row hashes must state their own
non-self-referential canonical serialization. Independent review must test
these semantics, not merely the presence of fields.
Neither design artifact closes a requirement: source, entitlement, replay and
paper-reconciliation evidence remains open in the JSON register.
