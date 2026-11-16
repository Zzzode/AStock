# C39 Independent Strategy-Hypothesis Protocol — Audited Cash-Flow Realization

- Artifact ID: `D5PT-C39-AUDITED-CASH-FLOW-REALIZATION-v1`
- Registered on: `2026-08-15`
- Status: `NO_ACTION — preregistration only; no evidence package, test result, product admission, portfolio construction, or forward-paper record is complete.`
- Risk Model Status: `VETO` — no portfolio loss budget, liquidity/capacity evidence, admitted product, total-return ledger, execution record, or forward observation exists from which loss can be bounded.
- Scope: China domestic public markets, with the first *testable* hypothesis family limited to CNY-denominated domestic common shares listed on the Shanghai, Shenzhen, and Beijing exchanges. The project-level research universe remains open to other domestic public products, but their different cash-flow and return mechanics require separately registered hypotheses.
- External orders, live security selection, target weights, notional amounts, and performance claims are prohibited.

## 1. Purpose and separation from C34

C39 is a replacement research route after the C34 ETF rule's limited proxy-screen failure. It is not a repair, sensitivity, reparameterization, product substitution, or continuation of C34. C39 has no C34 product list, monthly rotation, relative-momentum comparison, dual-horizon score, inverse-volatility sizing, defensive sleeve, fixed price-proxy cost load, or C34 sample split. C34 remains failed on its own record and cannot be revived by a C39 result.

The research question is deliberately economic rather than trend-following:

> Among a complete point-in-time universe of domestic non-financial common shares, do issuers whose audited operating cash flow and simple free-cash-flow proxy remain positive for two reported fiscal years, and whose contemporaneous free-cash-flow yield is no worse than their industry peer median, subsequently show a net total-return outcome above a long-run 5% research hurdle and above a mechanically matched control cohort?

The question is not a forecast. A result, if later obtained, would be evidence about this defined historical cohort only. It would not establish alpha, capacity, suitability, a return floor, or a future result.

## 2. Economic rationale

The proposed mechanism is disclosure-based cash-flow realization. Audited cash generation can be slower for the market to separate from accrual earnings, headline growth, or narrative risk, especially when a company has a plainly disclosed cash-flow record but is priced at no premium to comparable domestic issuers. The possible return source is a later revision in the market's assessment of durable cash generation and valuation—not momentum, volatility targeting, asset-class rotation, carry, a guaranteed dividend, or a cash-payment objective.

This mechanism can fail because the cash flow may be cyclical, temporarily boosted by working capital, committed to unproductive capital expenditure, impaired by governance, or already fully reflected in price. Those failure channels are part of the hypothesis, not reasons to relax it after a result.

## 3. Open-universe construction and fixed C39 test family

### 3.1 Project-level openness

The wider research universe remains open to China domestic listed equities, ETFs, listed funds, public REITs, bonds, futures, options, and other public instruments for which evidence can be obtained. C39 does not declare any of those categories inferior or excluded from future research. It simply does not mix incomparable total-return, financing, distribution, or execution conventions into one test.

### 3.2 C39 base universe

For each formation record, the base universe is **every historical and then-current CNY-denominated domestic common-share line** listed on SSE, SZSE, or BSE at that timestamp, including delisted, renamed, suspended, special-treatment, and later-delistable lines in the historical membership file. An exchange that had not yet opened is represented as a dated zero-member exchange, not silently omitted. Index membership, current listings, popularity, broker coverage, and later survival may not define membership.

The first C39 hypothesis applies only to non-financial operating companies because the stated cash-flow proxy is not economically comparable for banks, insurers, brokers, trusts, or other financial institutions. Financial issuers, funds, REITs, bonds, derivatives, and foreign-currency share classes remain in the open research universe but require another preregistered hypothesis; none may be substituted into C39 after results are known.

### 3.3 Mechanical cohort eligibility

A base-universe line becomes an *evaluated C39 candidate observation* only when all of the following are demonstrably true using information public by the formation timestamp:

1. A legally identifiable issuer/security mapping, share-class history, listing/status history, and first-public timestamp for the latest annual report are retained.
2. The latest two fiscal-year annual reports are retained from primary exchange/regulatory sources, have an unmodified audit opinion and no unresolved material going-concern qualification, and contain the required cash-flow-statement fields.
3. Operating cash flow is strictly positive in each of those two fiscal years.
4. The simple free-cash-flow proxy is strictly positive in each of those two fiscal years:

   `FCF proxy = cash received from operating activities − cash paid to acquire or construct fixed assets, intangible assets, and other long-lived assets.`

   The exact reported line-item mapping, issuer-specific deviations, and source pages must be preserved. A missing, restated, or non-comparable line is a failed data gate, not an invitation to estimate it.
5. At formation, latest-audited `FCF proxy / total market capitalization` is at least the median of the line's contemporaneous CSRC two-digit-industry peer set. The peer set must contain at least 15 data-complete base-universe lines; otherwise the line is `not_evaluable`, not moved to another industry or ranking rule.
6. The line passes the product, data, total-return, and execution gates in Sections 6–9 before its outcome is counted.

There is no composite score, rank selection, top-N list, discretionary exception, or weighting rule. Passing lines are observations in a research cohort, not holdings. A failure in any condition is recorded with its reason; it must not be repaired with a different product, sector classification, accounting proxy, or threshold after outcomes are visible.

## 4. Timing, outcome definition, and predeclared splits

### 4.1 Formation and horizon

For each eligible annual report, the formation timestamp is the **fourth eligible trading session after the independently evidenced first-public timestamp**, using a timestamped, side-aware quote snapshot at 14:30 Asia/Shanghai. The fourth-session delay prevents use of a same-session disclosure. It is a research measurement convention, not an order instruction.

The outcome horizon is exactly 18 calendar months after formation. If the date is not a trading session, use the first subsequent eligible session. There is no intermediate rebalance, reinvestment rule, stop, take-profit, or discretionary intervention. A company may be observed in later annual cohorts only if it independently passes the unchanged eligibility rules at that later formation; observations remain separately identified by issuer and formation date.

### 4.2 Locked partitions

No historical return, matched-control result, or aggregate statistic may be viewed by the rule author before the universe/data acceptance report and executable-code hash are frozen. The partitions below are calendar-fixed, cannot be rolled forward or re-cut after inspection, and use annual-report first-public dates:

| Partition | Annual-report first-public dates | Permitted use | Outcome completion requirement |
|---|---|---|---|
| P0 — pipeline validation | 2008-01-01 to 2011-12-31 | Schema, point-in-time, event-ledger, and code-path validation only. Return outputs remain masked. | Not a hypothesis test. |
| P1 — frozen historical test | 2012-01-01 to 2015-12-31 | First released test after independent reconstruction. | Each 18-month outcome must be complete. |
| P2 — frozen historical confirmation | 2016-01-01 to 2019-12-31 | Confirmation with the unchanged rule. | Each 18-month outcome must be complete. |
| P3 — frozen historical confirmation | 2020-01-01 to 2022-12-31 | Confirmation across a distinct market period with the unchanged rule. | Each 18-month outcome must be complete. |
| P4 — final historical holdout | 2023-01-01 to 2024-12-31 | Final historical release; it is not to be accessed if P1–P3 trigger a failure stop. | Each 18-month outcome must be complete by the recorded cutoff. |
| F1 — prospective paper observation | First eligible annual reports after `2026-08-15` | Forward record only, after all historical gates. | Two complete annual-report cycles plus every associated 18-month outcome. |

P0 may expose only synthetic results or integrity checks. P1, P2, P3, and P4 are released sequentially. A failure in an earlier partition stops later result release and closes C39; it does not authorize another version of the rule.

## 5. Outcome metrics and decision thresholds

### 5.1 Per-security net total-return record

For a candidate observation `i`, the research total-return record is:

`net_total_return_i = (terminal_bid_value_i + net_cash_distribution_ledger_i − formation_ask_value_i − documented_entry_and_exit_levies_i) / formation_ask_value_i`

`annualized_net_return_i = (1 + net_total_return_i)^(365 / elapsed_calendar_days_i) − 1`

The share count is evolved only through a complete corporate-action ledger. Cash distributions are recorded net of the predeclared, documented research tax profile and remain in a non-interest-bearing cash ledger until the outcome date; they are not assumed to buy additional shares. A rights issue, placement, split, consolidation, delisting, suspension, merger, tender, conversion, withdrawal, correction, or other event is handled only by its retained event record. If the record cannot be reconstructed, the observation is unresolved and the relevant gate fails. No adjusted-price vendor series can substitute for the raw event ledger.

No quantity, notional, position weight, portfolio return, capital allocation, or capacity estimate is calculated. The per-security calculation supports a cohort inference only and must not be recast as a tradable portfolio.

### 5.2 Matched-control metric

Each candidate is paired one-for-one, without replacement, with the non-candidate line in the same exchange and CSRC two-digit industry whose free-float market capitalization is nearest on the formation date. Ties are resolved by the permanent security identifier in ascending lexical order. The same total-return, quote, corporate-action, and execution rules apply to the control. A candidate without a valid control is unresolved; it is never matched using a different exchange, later classification, or an outcome-based substitute.

### 5.3 Primary and corroborative metrics

For each P1–P4 partition, calculate and disclose without smoothing:

| Metric | Definition | Predeclared threshold |
|---|---|---|
| M1 | Median `annualized_net_return_i` across all resolved candidates. | Strictly greater than 5% in every P1–P4 partition. The 5% line is a research hurdle only, never a promise or floor. |
| M2 | Median candidate-minus-matched-control annualized net-total-return difference. | Strictly greater than 0 in every P1–P4 partition. |
| M3 | Number of resolved candidate/control pairs. | At least 150 in every P1–P4 partition. |
| M4 | Candidate and control outcome reconciliation rate, including corporate actions, quotes, fees, taxes, status, and exit evidence. | 100%; an unresolved result is not imputed. |
| M5 | Ten worst individual annualized net outcomes, full outcome distribution, and unresolved/security-status log. | Disclosure metric only; it has no offsetting threshold and cannot be hidden by the median. |

The pooled P1–P4 result is descriptive and cannot rescue a failed partition. A clustered-by-issuer and formation-year, nonparametric bootstrap interval for M2 may be reported only as a robustness description; it cannot create a pass, establish alpha, or override a failed metric. No VaR, correlation, capacity, or risk budget is inferred from the cohort data.

### 5.4 Hypothesis disposition

`SUPPORTED_FOR_FURTHER_RESEARCH_ONLY` is possible only if every P1–P4 metric threshold, every admission gate, immutable-version review, and forward-paper gate is met. It still does **not** produce an admitted strategy, target weights, an investable universe, or external action. Any consideration of portfolio construction would require a separate protocol with a separately bounded loss budget, concentration limits, liquidity model, and independent risk sign-off.

The immediate status, regardless of no result or a future historical pass, is `NO_ACTION` until F1 is complete and an independent review records all required gates. External execution remains outside scope.

## 6. Product-level diligence admission gate

Each candidate and matched control must have a product record that independently establishes:

1. Permanent identifier, issuer, share class, exchange, currency, listing/renaming/delisting chain, and historical status.
2. Whether and when it was suspended, subject to special treatment, in price-limit conditions, ex-rights/ex-dividend, delisting, or otherwise unavailable for a cash-equity transaction.
3. Primary annual-report, audit-opinion, correction/restatement, ownership/share-capital, and material-event source files with URL, first-public timestamp, retrieval timestamp, SHA-256, and source quality.
4. Applicable exchange trading, lot, tick, settlement, transfer, tax, investor-eligibility, and account-restriction rules at the relevant date.

Failure to prove one field creates `PRODUCT_DILIGENCE_FAIL`. A current product fact may not be backfilled into history, and historical identity may not be silently mapped to a currently listed security.

## 7. Data and point-in-time admission gate

Before any P1 return output is released, an independent data-acceptance record must prove all of the following:

- Rights-cleared point-in-time universe membership for SSE, SZSE, and BSE, including inactive and delisted records; date-specific identifier mappings; and a coverage report. The membership file must cover at least 99% of contemporaneous line count and 99.5% of free-float market capitalization where an exchange was operating. Any gap is named, quantified, and blocks the relevant partition.
- Primary financial filings and first-public timestamps, version/correction chains, CSRC industry classification history, share counts, free-float capitalization inputs, and the exact cash-flow line mapping.
- Daily calendar, exchange status, price limits, unadjusted bid/ask/depth snapshots, and timestamped tradeability fields for formation and outcome handling.
- A retained data dictionary, vendor/license/right record, raw-file checksums, code version, deterministic run manifest, and independent reconstruction of a blinded sample.

No current constituent list, adjusted-price series, later restatement, missing field, or commercial terminal screen is assumed to be point-in-time correct. A failure is `DATA_OR_POINT_IN_TIME_FAIL`, not an opportunity to narrow the universe after outcomes are viewed.

## 8. Total-return and corporate-action admission gate

Every counted observation requires a line-by-line ledger for unadjusted prices, cash dividends, withholding/tax treatment under the frozen research profile, rights/placements, stock dividends, splits/consolidations, capital changes, mergers, tender offers, delisting payments, trading-status events, and corrections. The ledger must preserve event effective date, first-public availability, entitlement/record dates where relevant, source file/hash, and calculation version.

The research profile cannot assume that a displayed adjusted close is total return, that a declared dividend was paid, that a distribution can be reinvested at an unknown price, or that a delisted line realizes its last close. Missing event data, an untraceable adjustment, or unreconciled cash/share count is `TOTAL_RETURN_FAIL` and prevents a result for the affected partition.

## 9. Execution and cost admission gate

C39 treats historical execution conservatively and does not model a fictional flat spread, commission, or fill. The formation side uses the timestamped displayed best offer; the terminal side uses the timestamped displayed best bid. Both quote sizes, price limits, trading status, board-lot/tick constraints, T+1/settlement status, and a dated rule/fee schedule must be retained. Documented statutory levies, exchange/transfer fees, and the predeclared research account-profile commission are applied on their legally relevant side. If the account-profile schedule cannot be established, C39 cannot report M1 as net.

There is no assumed fill where the security is suspended, locked at a price limit, lacks a valid side quote/depth, has an ineligible account/status condition, or cannot be reconciled through settlement. A partial, rejected, or no-fill historical record is an `EXECUTION_FAIL`, not a fill at the close or an automatic substitution. Since C39 assigns no quantity or weight, it makes no capacity claim; a later portfolio protocol would need independent quantity, participation, concentration, and liquidation analysis.

## 10. Forward-paper admission gate (F1)

F1 can begin only after P1–P4 are completed without a failure stop, all historical evidence is independently reconstructed, and the C39 code/data manifest is immutable. It is a non-actionable observation ledger, not a paper order blotter. It must cover **two complete annual-report disclosure cycles** and every related 18-month outcome.

For each F1 observation, before the formation timestamp, retain the universe snapshot, source files/hashes, corporate-action ledger, eligibility decision, product status, account-profile assumption, quotes/depth, applicable price-limit/settlement/tax/fee rules, and `no_action` or unresolved reason. During the outcome period, retain every distribution, status change, corporate action, missing-data incident, and reconciliation. Any omitted record, rule/data-version drift, silent product substitution, unapproved correction, or independent-review failure invalidates F1 and maintains `NO_ACTION`.

## 11. Anti-data-snooping and governance controls

1. The sole C39 eligibility logic, industry mapping, formation delay, 18-month horizon, partitions, metrics, and thresholds are frozen in this artifact before access to outcome data. No parameter sweep, alternative score, top-N, alternate cash-flow definition, sector carve-out, exchange carve-out, horizon change, cost relaxation, or event-treatment change is permitted.
2. The return fields for P1–P4 remain masked from the author until the data-acceptance report, code hash, synthetic test results, and independent reconstruction record are finalized. An independent reviewer releases partitions sequentially.
3. All base-universe members and all failures are retained in a denominator log. Delisted, halted, special-treatment, renamed, and unavailable lines cannot disappear from a result table.
4. Every descriptive sensitivity or subgroup analysis is labelled non-decisive. It may explain a result but cannot select a replacement criterion or convert a failure into a pass.
5. C34 data, products, signals, diagnostics, results, and parameters cannot be used to choose any C39 rule element. C39 also does not inherit candidate names from another route.
6. If C39 fails, it is closed as `HYPOTHESIS_NOT_SUPPORTED` or `UNMEASURABLE`, as applicable. A future route must receive a new identifier, an economically distinct rationale, a new preregistration before outcome access, and its own data/product/total-return/execution/forward-paper gates. It may not be described as C39 retuning.

## 12. Failure taxonomy and current disposition

| Condition | Required disposition |
|---|---|
| Any M1–M4 threshold fails in P1, P2, P3, or P4 | `HYPOTHESIS_NOT_SUPPORTED`; stop later releases and do not retune. |
| Product, source-right, point-in-time, corporate-action, total-return, quote/depth, fee/tax, or execution evidence is incomplete | `UNMEASURABLE / NO_ACTION`; do not calculate a substitute proxy result. |
| A code, data, calendar, accounting mapping, or event-handling defect is found after a release | Invalidate the release; record the defect; rerun only the identical frozen code/data correction under independent review. No criterion may change. |
| F1 is incomplete, contains drift, or fails review | `FORWARD_PAPER_NOT_ADMITTED / NO_ACTION`. |
| All historical and F1 gates pass | `SUPPORTED_FOR_FURTHER_RESEARCH_ONLY / NO_ACTION`; a separate portfolio-and-risk protocol remains mandatory. |

**Current conclusion: `NO_ACTION`.** C39 contains no selected live product, no actionable weight or size, no evaluated performance, and no permission to trade. Its only present function is to make a future economic hypothesis falsifiable without reopening C34 or narrowing the open research universe after seeing results. Confidence in present actionability is therefore 0%; this is a declared evidence boundary, not a return estimate.
