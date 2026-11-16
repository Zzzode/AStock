# C34 Dual-Horizon Inverse-Volatility ETF Candidate — Pre-computation Protocol

- Protocol ID: `D5PT-C34-PROTOCOL-v1`
- Recorded before calculation: `2026-08-15`
- Status: `frozen_for_research_only_calculation`
- External orders: prohibited

## Fixed universe and sleeve definitions

This protocol is a distinct dynamic, ETF-only research candidate. It does not amend C30's static diagnostic or R01's monthly rule. The universe is closed to five dated, product-diligenced ETFs:

| Sleeve | Exact code(s) | Fixed sleeve construction |
|---|---|---|
| Equity | `510300`, `510880` | 50/50 equal-weight sleeve; each equity target is one half of the selected equity sleeve allocation |
| Bond | `511010` | One risk sleeve |
| Gold | `518880` | One risk sleeve |
| Fallback | `511990` | Full target only when no risk sleeve qualifies, and during score warm-up |

No replacement product, leverage, short sale, futures, options, borrowing, discretionary override, ranking, or post-result product change is allowed.

## Signal and target rule

All prices are the retained common SSE daily market-price observations. On the final common session of each calendar month, after the close (`D`):

1. For each risk sleeve and the fallback, calculate its 126- and 252-common-observation price returns. The equity sleeve return at each horizon is the arithmetic mean of the two ETF price returns; bond, gold, and fallback each use their own ETF price return.
2. Define the score as the equal mean of those two horizon returns. A risk sleeve is eligible only when its score is **strictly greater** than the fallback score. Equality is ineligible.
3. For every eligible risk sleeve, calculate the sample standard deviation (`ddof=1`) of its trailing 60 common one-session simple price returns. The equity daily sleeve return is the 50/50 arithmetic mean of the two ETF daily returns. Give active sleeves weights proportional to inverse realized volatility; split the equity weight 50/50 across `510300` and `510880`.
4. If no risk sleeve is eligible, target 100% `511990`. If a required price, score, or volatility value is absent, non-finite, or not strictly positive, the scheduled paper action is `no_action`; do not replace a product or infer a trade.

The 252-observation score warm-up is fixed: beginning at the first common close, the protocol targets 100% fallback until all frozen score and volatility inputs exist. This is not a return forecast.

## Timing and proxy arithmetic

The signal uses information through `D` close only. The earliest proxy target change is the following common session `E` at its reported open. Existing proxy holdings first receive the `D`-close-to-`E`-open move, a target change is then applied at `E` open, and the new target receives the `E`-open-to-`E`-close move. Same-session close execution and same-bar look-ahead are prohibited.

Each proxy trade, including the initial fallback entry, carries a fixed `20 bp` times one-way turnover arithmetic load. It is illustrative only, not an observed fee, tax, spread, impact, settlement, or fill. The retained inputs are price-only observations, not total-return, NAV, IOPV, execution, capacity, or account evidence.

## Frozen development, holdout, and context windows

- Development: `2014-12-31` through `2019-12-31`.
- Holdout: `2020-01-01` through `2025-12-31`.
- Full-sample context: every retained common session through the source cutoff.

The report must show calendar years, rolling five-calendar-year annualized price-proxy endpoints, and complete below-5% counts separately for these windows. A 5% annualized line is a research hurdle only; it is not a promise, floor, prediction, or suitability result.

## Controlled mutations — diagnostics only

The base remains the base whatever the result. All variants below are reported; none may be selected as a winner:

| ID | Score horizons | Volatility return observations | Eligibility threshold |
|---|---|---:|---|
| `base` | 126 and 252, equal mean | 60 | score > fallback score |
| `score_126_only` | 126 only | 60 | score > fallback score |
| `score_252_only` | 252 only | 60 | score > fallback score |
| `vol_48` | 126 and 252, equal mean | 48 | score > fallback score |
| `vol_72` | 126 and 252, equal mean | 72 | score > fallback score |

This small, predeclared family is a sensitivity check, not parameter optimization, out-of-sample proof, alpha evidence, or permission to relax the base rule.

## Forward-paper no-action gates and disposition

Before any future paper record, all current product documents and temporary announcements, market status, account and appropriateness facts, available shares and funds, lot/tick and settlement facts, expected fees and taxes, timestamped bid/ask/depth, and IOPV where applicable must be retained. Buy only if displayed ask is no more than `IOPV × 1.003`; sell only if displayed bid is no less than `IOPV × 0.997`. A missing or failed condition is `no_action`, with no assumed fill or automatic ETF substitution.

The historical proxy has none of these execution fields, has no total-return or event ledger, and is retrospective rather than point-in-time available-at evidence. Therefore the expected disposition is `VETO`, `research_only`, and no external action regardless of proxy arithmetic. If a complete calendar year or rolling five-year proxy endpoint is below the 5% research line, state that limited proxy failure plainly; do not compensate by changing the rule.
