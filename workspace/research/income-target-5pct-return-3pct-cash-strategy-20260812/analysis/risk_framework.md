# Risk Framework — Conditional Total-Return Research

## Status, hierarchy and non-negotiable boundary

This is a risk-governance framework for a conditional research allocation. It
does not authorize an order, a product subscription, a sale, or an automatic
rebalancing action. At the data cut-off every market-traded sleeve has
`q=0`; a market allocation is therefore **not** eligible. This states no
approved model allocation and infers no account holding or cash disposition.

The control hierarchy is deliberately one-way:

1. investment-purpose, no-leverage and product-scope restrictions;
2. approved portfolio loss budget and observed-drawdown state;
3. current product, valuation, liquidity, concentration and tax evidence;
4. any proposed weights and separate receipt-versus-disposition accounting; and only then
5. the 5% rolling total-return objective.

The objective cannot override an earlier control. An unfavorable outcome never
permits yield chasing, sale proceeds to be called investment return, lower
credit quality, leverage, a forced REIT fill, or a breach of a concentration
cap.

## The retired fixed vector and the -18% action line are not compatible

The prior first-round vector was 10% protected liquidity, 15% five-year
Treasury ETF, 40% high-dividend equity ETF, 25% public REITs and 10% defensive
diversifier. It is retired as a prospective allocation because the following
planning inputs, which are not market observations, forecasts, VaR, or a loss
cap, already reject it under the existing action line.

| Sleeve | Weight | Planning common-stress input | Contribution |
|---|---:|---:|---:|
| Eligible protected liquidity | 10% | 0% | 0.00% |
| Five-year Treasury ETF | 15% | -5% | -0.75% |
| High-dividend equity ETF | 40% | -45% | -18.00% |
| Public REITs | 25% | -25% | -6.25% |
| **Known-sleeve subtotal** | **90%** |  | **-25.00%** |
| Undefined diversifier | 10% | no approved input | not permitted in a pass calculation |

Thus, the known sleeves already produce a -25.00% planning loss. The legacy
illustration that assigned the undefined diversifier a -10% input produces
-26.00%, but that input cannot be used to qualify the sleeve or to offset
portfolio risk. A 10% unknown sleeve cannot make the target vector fit the
existing -18% loss-action boundary.

Accordingly, the retired vector fails the normal risk envelope and the
portfolio-level market-allocation gate remains `q_portfolio=0`. It may not be
described as a low-risk or asset-value-preservation portfolio. A future
candidate-level portfolio review is possible only as a research-governance
decision, and requires all of the following in one dated evidence pack:

- a completed, frozen-T2, candidate-specific common-stress recalculation,
  including every proposed direct equity, ETF, REIT, sovereign/cash tool and
  implementation-cost uncertainty;
- an explicit loss-capacity approval at least as large as that recalculated
  planning loss, with investment-horizon, liquidity-need and loss-capacity
  evidence reconfirmed;
- a documented acknowledgement that the -18% line is an early risk-action
  boundary, not a maximum possible loss; and
- independent passes for product eligibility, REIT concentration/correlation,
  account tax/settlement and current market-quality controls.

There is no such exception in this case. An exception clears only the portfolio
risk-budget gate; it is not an execution authorization and cannot change any
instrument-level `q=0` status.

## Observed drawdown states and mandatory research actions

Observed drawdown is calculated only from dated, external-flow-adjusted
account values:

\[
DD_t=\frac{MV_t^{\mathrm{flow\ adjusted}}}{HWM_t^{\mathrm{flow\ adjusted}}}-1.
\]

A planning-stress table never substitutes for this record. The actions below
are risk permissions and documentation requirements, not instructions to sell
or buy securities.

| State | Trigger | Mandatory effect on new allocations and settled cash | Release condition |
|---|---|---|---|
| Normal research state | (DD_t>-12\%\) and every other gate passes | A sleeve may be considered only under its effective `q`; cash disposition remains investor-directed. | None; `q` is reassessed at each validation. |
| Caution lock | (DD_t\leq-12\%\) | Set the portfolio risk-addition gate to zero. Pause scheduled risk tranches while product, liquidity, investment-purpose and concentration evidence is refreshed; cash disposition remains investor-directed. | Dated re-underwriting and independent risk approval; a price rebound alone is insufficient. |
| Risk stop | (DD_t\leq-18\%\) | All new allocations to market-risk candidates are prohibited. Cancel any unexecuted model tranche. Produce an incident pack and a non-automatic de-risk/recovery proposal; cash disposition remains investor-directed. | New risk-budget approval after the incident review, plus fresh `q=1` evidence for every affected candidate. |
| Stress-capacity incident | Observed loss reaches 90% of the separately approved planning-loss capacity, if an exception exists | The risk stop remains in force and the approved portfolio must be re-underwritten from current holdings, liquidity and investment purpose. No “make-up” allocation is allowed. | A replacement portfolio and risk budget must be approved; there is no mechanical re-entry rule. |

The -18% line is therefore a hard governance action, not a passive review. It
does not guarantee that losses stop at -18%, particularly in a gap, suspension,
or illiquid REIT scenario. Any discretionary reduction of an existing holding
is outside this research document and requires the investor's own decision and
separate current execution assessment.

## Allocation, overlap and concentration controls

| Exposure | Target / hard limit | Required control | Failure result |
|---|---:|---|---|
| Eligible protected liquidity | Notional reference only; any future floor is set only in an approved T4 package | Eligible institution/direct sovereign identity, term/withdrawal terms and deposit-insurance aggregation where applicable | No model allocation or account holding is inferred. |
| Direct equity, ETF/fund and public REIT | No pre-approved weight or format quota | Current item dossier, valuation/reference value, common-risk map, liquidity/capacity and marginal-stress contribution | `q=0`; the candidate cannot enter T3/T4. |
| Sovereign/cash tool | No pre-approved risk allocation | Current issuer/term/account/cash convention and investment-purpose evidence | Reject the candidate or leave it at `q=0`. |
| Margin, leveraged/inverse products, futures/options, private or materially illiquid instruments | No automatic admission | Separate written authorization plus full item and portfolio review | Not eligible under this case absent that path. |

For the REIT sleeve, “five tickers” is not evidence of diversification. Before
activation it must demonstrate at least three manager/sponsor groups and three
distinct operating cash-flow sectors. The following aggregation limits apply
after each proposed model tranche:

- no project: 5% of total portfolio;
- no common manager or sponsor group: 10% of total portfolio;
- no common sector, revenue driver, geography/regulatory regime, key
  tenant/offtaker, or refinancing-risk cluster: 10% of total portfolio;
- a pair whose verified rolling 60-observation return correlation exceeds 0.70
  is treated as one risk cluster, with the same 10% cluster cap; missing,
  inadequate, or structurally unreliable price history does not prove
  independence and requires a qualitative common-driver review;
- an equity-ETF/REIT look-through map must identify common sponsor, issuer
  group, property/rental, regulated-revenue, customer and financing exposures.
  A mapped shared operating-risk cluster may not exceed 15% of total portfolio
  across all sleeves; an unresolvable map sets the affected REIT `q=0`.

These are ex-ante risk caps, not statements that the current candidate pool
passes. In particular, multiple rental-housing tickers or multiple products
from the same manager are presumed correlated until the required evidence says
otherwise.

## Diversifier definition rule

No candidate may be an empty placeholder with an assumed stress input. A
potential diversifier must be named, must not be selected only for cash yield,
and must show a different economic-risk role from the proposed T2 set. Its
research pack must include:

- legal/product identity and exposure mechanics;
- a current price/reference and liquidity record appropriate to its structure;
- a rolling return-correlation and common-risk-driver assessment against every
  eligible direct-equity, ETF, REIT and sovereign/cash cluster;
- a candidate-specific common-stress input supported by product mechanics,
  rather than the retired generic -10% assumption; and
- evidence that including it does not worsen the approved portfolio stress,
  liquidity reserve or overlap caps.

No candidate is permitted to enter merely to repair an objective outcome.
Leveraged, derivative, private or materially illiquid candidates need a
separate written authorization path in addition to item and portfolio diligence.

## Distribution accounting and total-return objective protocol

Only settled interest, dividends, ETF distributions and REIT cash
distributions enter the receipt ledger. Sale proceeds, unrealized gains, NAV
accretion, external contributions and unpaid receivables do not. An issuer-
labelled or economically similar capital-repayment component requires a
separate ledger flag and predeclared accounting/tax treatment; it is not
labelled investment return. Cash is part of total return and is never added
twice after a later cash-use choice. Distribution history may inform product,
valuation and risk research, but it is not a separate target or a reason to
alter exposure.

- If rolling-five-year annualized total return is below 5%, record the
  conditional objective outcome. Do not call the cash receipt an additional
  return and do not use a recovery trade.
- If this outcome occurs for two consecutive scheduled review periods, freeze
  any proposal that raises market-risk exposure and rerun the full risk-budget,
  total-return, tax, liquidity and concentration review.

The detailed policy parameters and the effective-`q` architecture are in
`data/risk_budget_20260812.json` and
`data/execution_eligibility_policy_20260812.json`.
