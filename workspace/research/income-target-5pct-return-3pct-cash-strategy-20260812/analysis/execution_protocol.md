# Execution and Admission Protocol — Open Research, No Automatic Allocation

## Purpose and current state

This protocol controls admission from an open research universe into a finite
decision universe, then into an approved investable universe and eventually a
portfolio review. It is not an order manual: it does not submit orders, set
quantities, choose a broker, infer a fill or authorize external action.

The current state is not run: T3 and T4 are empty, every market candidate is
\(q=0\), and no candidate-specific risk budget or same-session implementation
packet is approved.

## Effective-q architecture

For candidate \(i\), eligibility for portfolio review is possible only when:

\[
q_{effective,i}=q_{portfolio}\,q_{risk\ state}\,q_{research,i}\,
q_{valuation,i}\,q_{market,i}\,q_{concentration,i}\,q_{account,i}.
\]

- \(q_{research}\) requires the item-specific R0--R4 dossier.
- \(q_{valuation}\) requires a current, reproducible valuation or reference-value
  method appropriate to the instrument, including scenario and invalidation
  treatment where investment risk is taken.
- \(q_{market}\) requires current tradability and capacity evidence.
- \(q_{concentration}\) requires common-risk and marginal-stress mapping across
  the entire proposed T4 portfolio.
- \(q_{portfolio}\) requires a candidate-specific, approved loss budget and a
  reproducible total-return replay of the frozen T2 set.

No term can be inferred from a screen, dividend label, historical announcement
or product format.

## Admission sequence

1. **Nominate to T1:** record thesis question, economic role, instrument
   identity and the reason the candidate could improve the available set.
2. **Freeze T2:** name a finite, dated comparison set. Record data cutoff,
   research owner, primary-source plan and the products it must be compared
   against.
3. **Build the item dossier:** use the direct-equity, ETF/fund, REIT or
   sovereign/cash evidence modules specified in research_brief.md. Each named
   direct equity must reconcile its code one-for-one to a dated valuation row
   and broker/Street row; the T3 registry count cannot exceed the matched list.
4. **Run independent reviews:** source/data verification, valuation or
   reference-value audit, risk/concentration, liquidity/capacity and
   tax/settlement/operating review.
5. **Approve or reject T3:** a pass only makes the item eligible for portfolio
   comparison. It does not set a weight.
6. **Approve or reject T4:** evaluate marginal total-return drivers,
   valuation, distribution accounting, common drivers, stress, concentration,
   capacity, suitability and monitoring expiry for the entire set.

## Current-session and capacity evidence

Every T3/T4 record must retain source/time/hash, identity, current
price/reference or valuation date, bid/ask where applicable, traded
value/depth, history sufficient to assess liquidity, lot/account/tax fields,
proposed notional and risk-budget context. For direct equities, include free float,
suspension, price-limit and corporate-action status. For ETFs, include
holdings, NAV/IOPV/reference methodology and material derivatives/securities
lending. For public REITs, include NAV date, intervening asset events,
operating KPI, tenant/offtaker, debt/refinancing and capex evidence.

The capacity calculation must be bounded by current and trailing liquidity,
observable executable depth and intended amount. Missing or stale inputs,
abnormal valuation deviation, suspension or an unresolved corporate/product
event result in \(q=0\).

## Distribution accounting and return evidence

Settled interest, dividends and fund/REIT distributions must reconcile to the
frozen portfolio's total-return series with actual holder taxes, receipt fees
and settlement dates. An issuer-labelled or economically similar capital-
repayment component requires a separate ledger flag and predeclared treatment.
Distribution history can inform operating and risk work, but it is not a cash
target, a selection threshold or a forward cash promise. A direct-stock
dividend is treated under the same accounting discipline as an ETF/REIT payment.

The return replay must use the exact T2 membership and substitution history,
point-in-time data, total-return/distribution/corporate-action treatment,
costs, taxes, capacity, A-share constraints and B0/B1 benchmarks. A
historical product card or single-stock price series is not portfolio evidence.

## Failure waterfall and non-execution boundary

Any exception, missing input, concentration breach, drawdown lock, product
event or unavailable tax/settlement record produces \(q=0\) for the affected
candidate. A failed global risk budget produces \(q=0\) for every market
candidate. It does not infer an account holding or direct a cash disposition.
The candidate may be compared against a newly nominated candidate in a later
research cycle, but there is no automatic replacement, catch-up allocation,
objective-repair trade or forced sale.
