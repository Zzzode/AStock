# Return-Evidence Memorandum — 5% Total-Return Objective

## Decision status

**Return-evidence gate: FAIL — not investment-committee eligible.**

The stated 5% target is a conditional objective, not an evidenced expected return or a minimum return. The case has an open research universe, but it does not have a dated, total-return-consistent, point-in-time history for a frozen cross-asset T2/T4 portfolio. No direct equity, ETF, REIT, sovereign/cash tool or other candidate is approved for implementation. A formal portfolio backtest, a probability of achieving 5%, and a recommendation to activate an allocation are blocked.

This is an evidence memorandum, not a synthetic portfolio backtest. The numerical history below is limited to primary annual reports for two named ETF sleeves. One public-REIT annual-report observation is included only to demonstrate why a distribution rate cannot substitute for total return.

## Scope test

| Question | Result | Reason |
|---|---|---|
| Did the final portfolio earn 5% annualized historically? | Not testable | No finite cross-asset T2/T4 set, point-in-time weights, substitution history or total-return input exists. |
| Is 5% a guaranteed or minimum annual return? | No | No market sleeve has this property; fund disclosures state that past performance is not future performance. |
| Do named sleeves have historical return evidence? | Partly | Annual reports provide fund NAV-growth history, before holder trading and subscription costs. |
| Do distributions establish strategy performance? | No | Fund distributions and REIT cash-flow distribution rates are product facts, not a final-portfolio total-return forecast. |
| Does this case pass a formal backtest or probability gate? | No | Final basket, total-return series, corporate-action records, costs, and point-in-time rules are missing. |

## Primary-source sleeve evidence

All performance values below are reported historical **fund NAV growth**. They are not investor account returns. Both annual reports say that holder subscription or trading costs are excluded. Annualized values are derived only from reported cumulative figures using `(1 + cumulative return)^(1 / years) - 1`.

| Sleeve | Primary source / period end | 1Y NAV growth | 3Y cumulative / annualized | 5Y cumulative / annualized | Permitted use | Hard limit |
|---|---|---:|---:|---:|---|---|
| 511010 5-year Treasury ETF | 2025 annual report, 2025-12-31 | 0.59% | 10.07% / 3.25% | 16.70% / 3.14% | Dated historical defensive-sleeve reference | Excludes holder trading costs; 2025 itself was below 5%. |
| 510880 high-dividend equity ETF | 2025 annual report, 2025-12-31 | -0.45% | 27.93% / 8.56% | 45.43% / 7.78% | Dated historical equity-sleeve reference | A strong five-year observation does not prove future return; the latest calendar year was negative. |
| 508069 public REIT, one observation | 2025 annual report, 2025-12-31 | IRR: 1.44% | N/A | N/A | Demonstrates distribution-rate / total-return non-equivalence | Not a final cross-asset basket and not a proxy for all REITs. |

The named equity ETF's five-year NAV history exceeds 5%, while the Treasury ETF's five-year NAV history is below it. This is neither a portfolio result nor an expected-return forecast. The 2025 observations alone, -0.45% for 510880 and 0.59% for 511010, rule out a claim that the target was achieved every calendar year.

The 508069 annual report reports a 9.19% annualized cash-flow distribution rate and a 1.44% internal rate of return for 2025. Those measures cannot be interchanged. The observation explicitly blocks using a quoted REIT distribution rate as a total-return input.

## Benchmark policy and present comparison status

A formal implementation test must use the same dates, valuation times, total-return treatment and cost convention for all comparisons.

| Benchmark | Definition | Purpose | Current status |
|---|---|---|---|
| B0: protected-liquidity alternative | Actual eligible deposit or direct very-short sovereign return, net of account terms | Measures the opportunity cost of taking market risk | Not selected: account product and terms absent. |
| B1: strategic blended benchmark | Frozen T2/T4 cross-asset weights, passively held and rebalanced under a pre-registered rule | Separates allocation outcome from tactical or security-selection changes | Not computable: no finite candidate set, weights or substitution history. |

The individual fund benchmarks in the reports are not substitutes for B0/B1: 511010 tracks the SSE 5-year Treasury Index and 510880 tracks the SSE Dividend Index. Neither represents the proposed multi-asset portfolio.

## Required reproducible portfolio test

1. **Freeze the actual universe before observing results.** Select a finite, dated cross-asset T2 set from T1; preserve each direct-equity, ETF, REIT, sovereign/cash candidate, product documents, membership, substitutions and q decision. Do not use survivor-only or hindsight constituents.
2. **Use total-return-consistent inputs.** Each sleeve needs a source that captures price or NAV and cash distributions on the correct ex-date and payment date. Do not mix market-price return for one sleeve with NAV return for another, and do not add distributions twice when a total-return series already embeds them.
3. **Pre-register execution rules.** A target weight observed on date D must execute at the next valid open. Model A-share lots, T+1, suspensions, price-limit no-fill states, spreads/slippage, a conservative participation cap, and a rule-based rebalance process rather than hindsight trades.
4. **Use investor-relevant costs.** Fund NAV normally embeds fund operating expenses but the cited reports exclude holder trading and subscription costs. The replay needs the account's commission and transfer fees, bid-ask and slippage assumptions, tax convention, and ETF/REIT settlement treatment.
5. **Measure both manager and investor outcomes.** Calculate TWRR for strategy assessment and MWRR/XIRR whenever the investor has external contributions or withdrawals. A distribution is an external withdrawal only when it actually leaves the portfolio; otherwise it remains portfolio cash. Evaluate at least five completed calendar years in which every frozen final sleeve exists and show rolling five-year outcomes.
6. **Report all outcomes.** Annual and rolling-five-year net total returns, observation status for the 5% objective, maximum drawdown, volatility, downside deviation, B0/B1 excess return, turnover, costs, unfilled trades, capacity flags, correlation and concentration exposure, and every target-weight history.
7. **Separate history from probability.** A finite historical sample cannot establish the future probability of a 5% result. If a probability model is later added, disclose its model family, sample period, regime treatment, distribution and correlation assumptions, fees, taxes, parameter uncertainty, and out-of-sample validation. A model output is not a guarantee.

## Why a formal replay is blocked now

The configured data mode is `public_observation`. Under the repository policy, a frozen public daily-bar review may be reproducible for research but does not establish point-in-time universe membership, corporate actions, halts, price limits, delistings, capacity, or fill quality; it cannot support a formal investment-committee or trading claim. No licensed EOD archive is available.

In particular, a weighted blend of unrelated fund or stock returns must not be called a backtest. It would mix different periods, NAV and market-price conventions, unspecified membership, missing distributions and untested substitution rules. It would be false precision.

## Cash, total-return, scenario and probability boundaries

Eligible cash records are settled interest, dividends, ETF distributions and REIT distributions. Sale proceeds, NAV accretion, unrealized gains, and external contributions must not be misclassified as distributions. A return-of-capital-like component requires a separate ledger flag and a predeclared accounting/tax treatment; it is not labelled investment return.

510880 distributed cash in each of 2023-2025. The 511010 annual report shows a cash distribution in 2025 but none in 2023 or 2024. These facts can inform product analysis, but do not create a stable distribution or total-return forecast.

The existing -26% common-stress figure is planning arithmetic only. It is not a historical drawdown, VaR, expected shortfall, calibrated scenario, or probability statement. No bear/base/bull expected-return case can be calibrated until the frozen full-portfolio return, distribution, correlation, and cost/tax inputs exist.

## Current investment conclusion and upgrade gate

**Current conclusion: research framework only; implementation is not approved.** The available primary evidence is sufficient to reject a guaranteed-return narrative and to show why 5% cannot be assumed. It is not sufficient to claim that this portfolio has historically achieved, is expected to achieve, or has a stated probability of achieving 5% total return.

The return-evidence gate can change from FAIL only after a new dated packet contains:

- a frozen named cross-asset T2 set and structure-specific item dossiers;
- point-in-time T2/T4 weights and constituent/substitution history;
- frozen total-return and distribution data with corporate-action records;
- B0 and B1 benchmark series;
- account-specific costs, tax, settlement, slippage, and capacity assumptions;
- a reproducible replay with explicit public-data or licensed-data assurance;
- annual and rolling-five-year total-return outcomes; and
- independent checking that price return and distributions were not double counted.

## Source register

| ID | Source | Evidence used | Local reference | Scope limit |
|---|---|---|---|---|
| R14 | SSE / 国泰基金, 511010 2025 annual report, published 2026-03-30 | 2023-2025 annual NAV growth, 3Y/5Y cumulative NAV growth, distribution record, fee exclusion | Archived primary PDF/text; SHA-256 in `sources/official-20260812/manifest.json` and `data/return_evidence_20260812.json` | Fund-level NAV history, not portfolio or investor return. |
| R11 | SSE / 华泰柏瑞基金, 510880 2025 annual report, published 2026-03-31 | 2023-2025 annual NAV growth, 3Y/5Y cumulative NAV growth, distributions, fee exclusion | Existing primary archive plus URL and SHA-256 in the JSON packet | Fund-level NAV history, not portfolio or investor return. |
| R02 | SSE / 华夏基金, 508069 2025 annual report | 2025 9.19% annualized cash-flow distribution rate and 1.44% IRR | Existing case archive | One REIT only, not basket history. |
| R13 | SSE / 国泰基金, 511010 product summary | Risk and cost boundary | Existing case archive | Product disclosure, no forecast. |
