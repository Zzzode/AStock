# Conditional Implementation and Cash-Use Boundary Checklist

## Status and decision boundary

This checklist controls whether a named candidate may move from the open
research universe into a finite decision universe, approved investable pool
and portfolio review. It is not a broker instruction, an order workflow, a
recommendation to trade or a suitability finding. The current result is
`q=0` for every market candidate and `q_portfolio=0` because no finite
cross-asset decision universe, current-session packet or candidate-specific
risk-budget approval exists. No model market allocation is approved and no
account holding is inferred.

An effective sleeve permission is:

\[
q_{effective,i}=q_{portfolio}\times q_{risk\ state}\times q_{research,i}
\times q_{valuation,i}\times q_{market\ quality,i}\times q_{concentration,i}\times q_{account,i}.
\]

Any zero makes the result zero. A passed sub-check never implies that the
other checks pass.

## Nomination and portfolio-level gates

Before a candidate can be compared, freeze its code or legal identity,
economic role, research question, data cutoff, responsible owner, primary
source plan and the competing T2 candidates. A screen result, historical
distribution or an unnamed category cannot enter the decision universe.

1. **Risk budget:** a dated candidate-level and portfolio-level risk-budget pack
   must replace the old -25.00% fixed-vector illustration, resolve stress,
   concentration, liquidity and implementation-cost uncertainty, and fit the
   approved loss-capacity boundary. No approved package means `q_portfolio=0`.
2. **Investment purpose:** the investment horizon, known liquidity needs and
   loss-capacity record must be current. Funds needed for a known short-horizon
   obligation cannot pass this gate.
3. **Current account record:** account eligibility, available cash, settlement
   convention, taxes, fees and external-flow-adjusted high-water mark must be
   recorded. A cash-yield estimate without account tax/fee evidence does not
   pass.
4. **Authorization boundary:** direct stocks, ETFs, REITs, sovereign/cash tools
   are researchable under this framework. Margin financing, leveraged/inverse
   products, futures/options, private or materially illiquid instruments need
   a separate written authorization path; none is automatically eligible.
5. **No risk lock:** documented (DD_t\leq-12\%\) pauses risk additions;
   (DD_t\leq-18\%\) is a mandatory risk stop. Neither state can be bypassed
   by a distribution, a discount, or an unfavorable objective outcome.

## Structure-specific evidence packs

| Sleeve | Required current evidence | Additional risk gate | Failure action |
|---|---|---|---|
| Protected liquidity / very-short sovereign exposure | Institution/direct-sovereign identity, term, withdrawal/maturity terms, aggregate insured-deposit exposure where relevant | It is a reference reserve, not an assumed yield source or substitute for an ETF | No model allocation or account holding is inferred. |
| Direct A-share equity | Named T2/T3 registry code reconciled one-for-one to current valuation and broker/Street records, plus company/industry/governance evidence, audited financials, revenue-to-EPS bridge, current-price bull/base/bear valuation, dividend/free-cash-flow bridge, float, suspension/price-limit, liquidity and capacity | Issuer-group, industry, factor and common-risk contribution versus every proposed holding | Keep the candidate in T1/T2 at `q=0`; no automatic ETF substitute. |
| ETF/fund | Current legal/index document, holdings, NAV/IOPV/reference, tracking, TTM settled distribution ledger, material derivatives/securities lending, capacity and account fields | Issuer-group, industry, factor and cross-product overlap; index yield is not holder cash | Set the failed candidate to `q=0`; no correlated substitute. |
| Public REITs | Current price and latest disclosed NAV/date, TTM settled distribution evidence, operating KPI, debt/refinancing/capex reserve, spread, capacity, lot, tax and settlement | Project/manager/sector/cash-flow-driver/common-risk and cross-sleeve overlap caps | Failed candidate stays `q=0`; no forced REIT fill. |
| Sovereign/cash product | Issuer/protection/term/withdrawal mechanics, cash convention, tax, account and concentration | Fits the approved investment-purpose and liquidity role; it is not an assumed total-return solution | Do not infer an account holding. |

Use the dynamic, candidate-specific market-quality rules in
`data/execution_eligibility_policy_20260812.json`. A historical snapshot,
one-quarter distribution annualisation, stale NAV, missing book depth, or a
product name is not a pass.

## Approval sequence and audit record

For every proposed T3 or T4 candidate, retain a single dated record with
source locator, timestamp, raw-record hash, item-dossier version, valuation
or reference-value inputs, cash inputs, common-risk map, capacity calculation,
pass/fail result, reviewer identity/role and fallback destination. The
following gates must pass in order:

1. data-verification and item-research gate — source, freshness, company/product
   structure, financial/operating facts and calculation fields;
2. independent valuation and risk/concentration gate — current value, stress, overlap, liquidity capacity
   and portfolio limits;
3. portfolio-governance gate — risk-budget state, drawdown state and investment
   purpose; and
4. portfolio-owner confirmation that the conditional research state may be
   reviewed.

For direct equities, the declared count and ordered code list in T3 must match
the dated valuation and broker/Street records exactly; an unmatched or duplicate
code is a blocking failure, not a zero-weight exception.

The last gate permits only continued research qualification. It does not
authorize an order, select a broker, set a live price, or create an automatic
trade.

## Receipt ledger and cash-disposition boundary

1. Record each **settled net** receipt in the cash ledger with date, source
   sleeve, gross amount, tax, fee, net amount and settlement evidence.
2. Record any issuer-labelled or economically similar capital-repayment
   component with a separate flag and predeclared accounting/tax treatment; it
   is not labelled investment return or counted twice.
3. The cash recipient may retain, withdraw or take no action with ledger
   recording only. This framework gives no default action and does not require
   retention or reinvestment.
4. A later proposal to use cash in a T3 candidate requires every
   effective `q=1`, no portfolio-limit breach and a new portfolio review. It
   may not be redirected automatically to a high-yield, correlated,
   lower-credit, leveraged or catch-up candidate.
5. A distribution date does not create a transaction. Selling assets to create
   cash is a reallocation, not a distribution receipt, and needs its own
   portfolio review.

## Review cadence and mandatory failure actions

| Event | Required research action |
|---|---|
| Each quarter | Reconcile distributions, taxes and fees to total-return accounting; refresh effective `q`, financial/operating evidence, holdings/overlap, liquidity capacity and external-flow-adjusted (DD_t). |
| Each scheduled model tranche or rebalance review | Collect a new same-session market-quality packet. There is no catch-up treatment for a missed tranche. |
| Annual review | Reconcile total return, distributions, taxes and fees; refresh the return-evidence packet and the risk-budget exception, if any. |
| Rolling-five-year annualized total return below objective | Record the outcome; do not raise risk. Two consecutive review-period outcomes below the objective freeze any risk-increase proposal pending full re-underwriting. |
| Missing/stale field, product event, price-reference anomaly, capacity failure or cap breach | Set the affected sleeve `q=0` and stop its new research tranche; do not infer an account holding or cash disposition. |
| (DD_t\leq-12\%\) | Caution lock: pause new risk additions pending re-underwriting; cash disposition remains investor-directed. |
| (DD_t\leq-18\%\) | Risk stop: prohibit all new market-risk allocations, cancel unexecuted model tranches and require a documented incident/de-risk proposal before any later re-approval. |

No row above directs a market transaction. It specifies the evidence state and
the only permitted fallback for a conditional research portfolio.
