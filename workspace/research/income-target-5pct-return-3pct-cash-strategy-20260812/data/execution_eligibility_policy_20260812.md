# Execution Eligibility Policy — Open-Universe Research Qualification

## Current status

Status is `not_run`. `q_portfolio=0`, T3 and T4 are empty, and every market
candidate is `q=0`. No model market allocation is approved and no account
holding is inferred. This policy is not an order authorization, suitability
conclusion, return forecast or cash guarantee.

The effective permission for candidate \(i\) is:

\[
q_{effective,i}=q_{portfolio}\times q_{risk\ state}\times q_{research,i}
\times q_{valuation,i}\times q_{market\ quality,i}\times q_{concentration,i}
\times q_{account,i}.
\]

Every factor must pass. A candidate may be nominated at T1, but it cannot reach
T3/T4 through a screen, a dividend label, a historical product notice or its
asset class.

## Evidence modules and current-session controls

Each record must retain source/time/hash, identity, a dated valuation or
reference value, bid/ask where applicable, traded value/depth, history needed
to assess liquidity, lot/account/tax fields, target shortfall and proposed
notional. Missing or stale data means `q=0`.

- A direct A-share equity requires company/industry/governance evidence,
  audited financials, a revenue-to-EPS bridge, current-price bull/base/bear
  valuation, dividend/free-cash-flow coverage, catalyst/invalidation, free
  float, suspension/price-limit/corporate-action status, liquidity/capacity
  and issuer-group/industry/factor/common-risk mapping. A named T3 issuer must
  also reconcile one-for-one to the dated valuation and broker/Street registry;
  the declared T3 direct-equity count must equal that matched list.
- An ETF/fund requires current legal/index documents, holdings look-through,
  NAV/IOPV/reference methodology, tracking, TTM settled-distribution ledger,
  material derivatives/securities lending, capacity and account evidence.
- A public REIT requires price and latest disclosed NAV/date, TTM settled cash
  evidence, operating KPI, debt/refinancing/capex reserve, spread/capacity,
  project/manager/sector/tenant/refinancing mapping and tax/settlement review.
- A sovereign or cash product requires issuer/protection identity, term and
  withdrawal/maturity mechanics, cash convention, taxes, account fit and
  concentration review; it is not assumed to meet the total-return objective.

## Cash-flow accounting, portfolio gate and fallback

Cash distributions must be reconciled to the total-return series using settled
receipt dates, holder taxes, receipt fees and settlement evidence. Eligible
receipt types are settled interest, dividends, ETF distributions and REIT
distributions; sale proceeds, unrealized gains, NAV accretion, external
contributions and unsettled receivables are not receipts. An issuer-labelled
or economically similar capital-repayment component needs a separate ledger
flag and predeclared accounting/tax treatment. This is an accounting control,
not a cash-yield target, qualification threshold or allocation requirement.

Unitize every external contribution or withdrawal at its immediately pre-flow
marked value. A later withdrawal cannot mechanically alter past performance;
it affects only the subsequent portfolio path, TWRR and future cash capacity.
Retaining, withdrawing or taking no action with a receipt is investor-directed
and recorded in the ledger. Any later market allocation remains subject to a
fresh T1-to-T4 review.

The portfolio gate also requires a frozen T2 decision universe, an approved
candidate-specific risk budget, a reproducible total-return replay with B0/B1
benchmarks, investment-horizon/liquidity-need evidence and a current
drawdown record. An unresolved item or portfolio condition produces `q=0`; it
does not infer a holding or direct the disposition of account cash. It is never
automatically redirected into a higher-yield, leveraged, lower-credit,
correlated or direct-equity candidate.

The complete machine-readable control schema is
`data/execution_eligibility_policy_20260812.json`.
