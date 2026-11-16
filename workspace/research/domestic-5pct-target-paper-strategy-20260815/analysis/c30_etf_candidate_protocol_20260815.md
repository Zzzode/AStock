# C30 ETF Candidate — Pre-computation Protocol

- Protocol ID: `D5PT-C30-PROTOCOL-v1`
- Recorded before calculation: `2026-08-15`
- Status: `frozen_for_research_only_calculation`
- Scope: a simple, strategic, ETF-only **research candidate**. It does not authorize an investment, account action, order, or product recommendation.

## 1. Fixed candidate card

**Name:** C30 five-ETF balanced strategic basket.

**Economic motivation:** retain a deliberately limited domestic equity risk-premium sleeve, balance it with a five-year Treasury-rate sleeve, add a small domestic-gold sleeve for a different macro exposure, and retain a money-market ETF sleeve for operational liquidity. This is an exposure-budget design, not a forecast that the sleeves are independent, protective, liquid, or sufficient to meet a return objective.

| Code | Dated P01 role | Fixed target weight | Action role |
|---|---|---:|---|
| `510300` | Broad China equity | 20% | One half of the 40% equity sleeve |
| `510880` | Dividend-style China equity | 20% | Other half of the 40% equity sleeve |
| `511010` | Five-year government-bond exposure | 40% | Interest-rate / government-bond sleeve |
| `518880` | Domestic gold-spot-related exposure | 10% | Gold sleeve |
| `511990` | Money-market-tool exposure | 10% | Liquidity sleeve, not account cash |

The five codes are exactly the products already covered by P01. There is no automatic replacement, leverage, borrowing, short sale, derivative overlay, cash-flow withdrawal rule, forecast, ranking, signal optimization, or product selection based on historical outcome.

## 2. Fixed operating rule

1. At the final common market-price **close** in June and December (decision session `D`), calculate only the existing drifted weights; the target vector above is not altered by market data.
2. A scheduled rebalance is modelled no earlier than the **next common session `E` at its reported open**. Existing holdings first receive the `D`-close-to-`E`-open proxy move; target changes and the illustrative cost are then applied at `E` open; only then does the new vector receive the `E`-open-to-`E`-close proxy move. Same-session close execution and same-bar look-ahead are prohibited.
3. Historical initialization is also delayed: the first common close is an initial decision record and the basket begins at the following common open.
4. Every scheduled event restores the fixed vector. The historical arithmetic does not simulate lots, partial fills, halts, price limits, IOPV, bid/ask, taxes, settlement, account availability, or no-fill states.

## 3. Source, return, and cost boundaries

The calculation may use only the five preserved JSONP responses in `sources/c7-static-etf-price-observation-20260815/`, hash-checked against that batch's manifest. They are official SSE market-price observations captured retrospectively, but their adjustment basis and point-in-time availability are not established.

The result is therefore an **unadjusted-or-undisclosed market-price proxy**, not investor total return, fund NAV return, execution result, capacity estimate, or evidence that a person could obtain a fill.

For a transparent friction sensitivity only, the base arithmetic deducts `20 bp` times one-way turnover at each proxy trade, including an initial one-way purchase of the basket. This is illustrative; it is not an observed commission, tax, spread, impact, fee, settlement, or fill. The cost mutations below use `0 bp` and `50 bp` in exactly the same arithmetic.

## 4. Frozen research hurdle and outcome set

The long-run research hurdle is **5% annualized**. It is neither an annual minimum, a promise, a prediction, a suitability conclusion, nor an authorization to act. The calculation must report:

- full-period annualized market-price proxy change;
- every complete calendar-year proxy change;
- each rolling five-calendar-year annualized proxy endpoint using only month-end endpoints;
- maximum drawdown and proxy daily / 20-session loss observations;
- illustrative turnover and cost arithmetic; and
- a separate explicit loss-bound and execution-data limitation.

If any complete calendar-year or rolling-five-year market-price proxy is below 5%, the candidate is rejected by this *limited proxy screen*. Even if no proxy observation were below 5%, the screen could not admit the candidate because it lacks total-return, execution, liquidity, portfolio, and forward-paper evidence.

## 5. Predeclared mutations — robustness only

The base candidate remains the base regardless of results. The following small family is reported in full only to test whether conclusions depend on a narrow, arbitrary allocation, cadence, or cost setting. It must never be ranked or used to select a winner.

| Mutation ID | Change from base |
|---|---|
| `low_equity_30` | `510300` 15%, `510880` 15%, `511010` 50%, `518880` 10%, `511990` 10%; same semiannual calendar and 20 bp cost |
| `high_equity_50` | `510300` 25%, `510880` 25%, `511010` 30%, `518880` 10%, `511990` 10%; same semiannual calendar and 20 bp cost |
| `annual_cadence` | Base weights; December only; 20 bp cost |
| `quarterly_cadence` | Base weights; March, June, September, and December; 20 bp cost |
| `zero_cost` | Base weights and semiannual calendar; 0 bp illustrative cost |
| `cost_stress_50bp` | Base weights and semiannual calendar; 50 bp illustrative cost |

## 6. Forward-paper action and no-action conditions

This candidate can describe a future **paper** action only when all five products have current legal-document and temporary-announcement checks, product and market status, account/appropriateness confirmation, available funds and shares, lot/tick/settlement facts, expected fees and taxes, timestamped bid/ask/depth, and IOPV where applicable. A paper order would use a limit-price protection check: buy only if displayed ask is no more than `IOPV × 1.003`, sell only if displayed bid is no less than `IOPV × 0.997`.

Record `no_action` and preserve the prior paper holdings if any required field is missing; a product is halted, delisted, price-limited, materially changed, or fails account/settlement checks; an equity leg cannot both be checked; a minimum 100-share lot would be violated; a limit order is partly filled, rejected, or unfilled; or reconciliation fails. Do not substitute a similar ETF, assume a fill, reuse unsettled proceeds, or treat category-level T+0/T+1 guidance as an account-level fact.

## 7. Expected disposition

The protocol is exploratory after public observations existed and is not a clean preregistration. Given the absent point-in-time total-return, liquidity, cost, execution, account, portfolio-loss-budget, and forward-paper ledgers, the required quant-risk disposition is `VETO` for use as a personal strategy. The calculation can characterize only the limited historical price proxy; it cannot make 5% guaranteed or authorize an actual investment action.
