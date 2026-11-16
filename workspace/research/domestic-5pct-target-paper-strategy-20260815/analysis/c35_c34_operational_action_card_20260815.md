# C35 — C34 Dual-Horizon Operational Action Card

- Artifact ID: `D5PT-C35-v1`
- As of: `2026-08-15`
- Status: `research_only_forward_ledger_incomplete`; `paper_operable=false`; `external_orders=false`
- Scope: a separate paper-operation card for `D5PT-C34-PROTOCOL-v1`. It does not amend, replace, or combine C34 with R01 or C30.
- Data quality: the rule uses retained common SSE market-price observations. They are a retrospective price proxy, not total return, NAV, IOPV, an executable quote, a fill, or a personal operating right.

## 1. Current use and hard boundary

The current C35 action is `NO_ACTION` outside a future, controlled paper-observation cycle. C34 is frozen for research calculation only, and C31 confirms dated product facts while leaving action-date terms, quotes, depth, access, friction, and settlement unverified. No broker instruction, external order, account change, or promise of a 5% outcome is created by this card.

This card applies only to C34's dual-horizon monthly rule. It does not borrow R01's 252-observation absolute-momentum target map or C30's semiannual static weights. Mixing those signals, weights, dates, costs, or results would be a new rule version.

## 2. Exact closed product map and dynamic target math

| C34 sleeve | Exact product(s) | Conditional target expression | Dated C31 product-card boundary |
|---|---|---|---|
| Equity | `510300`, `510880` | Each equals `0.5 × w_equity` | Stock-ETF T+1 is category guidance only; both legs are required and neither can replace the other. |
| Bond | `511010` | `w_bond` | Bond-ETF T+0 support is category guidance only. |
| Gold | `518880` | `w_gold` | Gold-ETF T+0 support is category guidance only. |
| Fallback | `511990` | `1.0` only during warm-up or when no risk sleeve is active; otherwise `0` | Money-ETF T+0 support is category guidance only. |

At monthly decision close `D`, use only the retained common price observations:

1. For every sleeve `s`, calculate 126- and 252-common-observation price returns, `r(s,126)` and `r(s,252)`. Equity is the arithmetic mean of the two component returns at each horizon.
2. Set `score(s) = 0.5 × r(s,126) + 0.5 × r(s,252)`. A risk sleeve is active only if `score(s) > score(fallback)`; equality is inactive.
3. For each active risk sleeve, calculate `sigma(s)`, the sample standard deviation (`ddof=1`) of the prior 60 common one-session simple price returns. Equity daily return is the 50/50 arithmetic mean of its component daily returns.
4. Set `u(s) = 1 / sigma(s)` and `w(s) = u(s) / sum(u(active sleeves))`. Then assign `w_510300 = w_510880 = 0.5 × w_equity`, `w_511010 = w_bond`, `w_518880 = w_gold`, and `w_511990 = 0`.
5. During the fixed 252-observation warm-up, target `w_511990 = 1.0`. If no risk sleeve is active after warm-up, use that same fallback target. If any required price, score, or active-sleeve volatility input is missing, non-finite, or non-positive, record `NO_ACTION`; do not convert the failure into a fallback target or replace a product.

The target vector must be non-negative and sum to 1.0 within documented calculation precision. It is an output of C34's rule, not a fill, holding, or external transaction.

## 3. Observation, earliest effective time, and action vocabulary

1. **Decision D:** after the final common market-price close of every calendar month, capture the five source rows, source hashes, available-at time, computed horizon returns, scores, active set, volatilities, inverse-volatility weights, and target vector.
2. **Earliest effective time E:** the next common session at its reported open. Same-session close execution and same-bar look-ahead are prohibited.
3. **Proxy sequence only:** existing paper holdings first receive the D-close-to-E-open proxy move; the target change and the illustrative 20 bp one-way-turnover load are applied at E open; only then do new target weights receive the E-open-to-E-close proxy move. The load is not an observed fee, tax, spread, impact, settlement, or fill.
4. **Paper-action labels:** `paper_rebalance_candidate`, `paper_hold`, `no_action`, and `operational_pause`. They are record labels only. C35 does not create, route, modify, or cancel an external order.

## 4. Pre-action evidence checks

All planned legs must pass the following check list at E. A category label, a historical price, an NAV, a later quote, or a close does not fill a missing action-date field.

| Check | Evidence required at E | Failure treatment |
|---|---|---|
| Product identity and current terms | Current legal document and temporary-announcement review; code/name; product objective, fee, and material-change status | `NO_ACTION` for the scheduled rebalance; no substitute |
| Trading state | Venue, valid session, tradable/halt state, applicable price-limit state and rule version | `NO_ACTION`; no asserted exit price |
| Quote and depth | Timestamped bid, ask, visible two-sided depth, and quote source for every planned leg | `NO_ACTION`; no close-price or assumed fill |
| IOPV when applicable | Time-matched IOPV source/value and its applicability determination | `NO_ACTION` where a required IOPV is missing or unusable |
| Lot, tick, and settlement | Product-, venue-, account-, and date-specific lot/tick, sellable-at, settlement status, and availability fields | `NO_ACTION`; do not use C31 category guidance as a standing permission |
| Fee, tax, and account terms | Current documented fee/tax treatment and account/product-access evidence | `NO_ACTION`; do not reconstruct or assume the field |
| Rule inputs | Complete valid D inputs; strictly applied score comparison; positive finite active-sleeve volatilities; target sum check | `NO_ACTION`; no parameter or product change |

C31 records a 100-fund-unit / CNY0.001 category reference from an SSE FAQ captured on 2026-08-15. It also records stock-ETF T+1 and bond/gold/money ETF T+0-supported categories. C35 treats each as an action-date field to verify, not as a live code-specific permission. A newly acquired equity ETF unit must not be treated as eligible for same-session reversal; any purported same-day functionality for bond, gold, or money ETFs defaults to unavailable unless the specific product, venue, account, settlement, and availability evidence says otherwise.

## 5. Price protection and rounded paper quantities

No market-order or close-price fill is permitted in the paper ledger.

- **Buy protection:** `buy_cap = IOPV × 1.003`, rounded to the verified tick. A paper buy is eligible only if the contemporaneous displayed ask is at or below `buy_cap`.
- **Sell protection:** `sell_floor = IOPV × 0.997`, rounded to the verified tick. A paper sell is eligible only if the contemporaneous displayed bid is at or above `sell_floor`.
- **Quantity:** round a calculated quantity down to the verified lot. A less-than-one-lot change, invalid tick, unavailable settlement field, or residual that cannot be handled under the frozen rule is `NO_ACTION`; it is not reassigned to another sleeve.
- **Market constraints:** a halt, limit lock, missing two-sided quote, missing IOPV where required, or unusable depth is `NO_ACTION`. C35 does not assert any universal daily price-limit percentage.

The thresholds are C34's paper price-protection formulation. They do not establish available liquidity, a fill, or a result.

## 6. Partial, no-fill, and reconciliation branches

| Branch | Required record | Resulting state |
|---|---|---|
| All action checks pass and every required leg is fully supportable | Target, prior paper state, rounded quantities, quote/IOPV/limit calculation, fee/tax/settlement fields, and paper evidence | `paper_rebalance_candidate`; target remains distinct from a fill |
| Any planned leg is partial, rejected, unfilled, below lot, or fails a price-protection/state check | Failed leg, reason, timestamps, evidence, unfilled quantity, and unchanged target calculation | Entire scheduled rebalance is `NO_ACTION`; preserve the prior paper state and do not fabricate a partial target |
| Equity leg failure | Both equity-leg records, reason, and no-substitution attestation | Entire scheduled rebalance is `NO_ACTION`; the other equity ETF is not enlarged |
| Reconciliation failure | Prior state, intended state, recorded result/no-action, residuals, fees/taxes/events, settlement, and the unexplained difference | `operational_pause`; no subsequent candidate action until resolved and independently reviewed |

Visible depth alone does not prove a partial result. C35 records the C34 failure branch rather than inventing a partial execution from a displayed book. It also prohibits an intraday catch-up or a delayed entry at a later, unaudited price.

## 7. Operational pause and review controls

Every monthly cycle requires a maker-checker review of source hashes, D/E timestamps, dynamic-target arithmetic, product documents/state, quote/IOPV/depth, lot/tick/settlement, fee/tax/account fields, action/no-action outcome, and reconciliation.

Set `operational_pause` immediately for an unresolved source/hash discrepancy, invalid or incomplete rule input, product/legal-status change, access or settlement failure, halt or price-limit lock, missing/invalid quote or IOPV, partial/no-fill event, unreconciled paper ledger, or an attempt to modify C34's universe, horizons, volatility window, eligibility threshold, timing, or protection formula. A pause blocks later candidate actions; it does not create a sale, a substitute, a different target, or a retroactive fill.

C34 has no frozen numerical drawdown trigger. C35 deliberately adds none: an arbitrary drawdown threshold would alter the protocol. Resumption requires a dated evidence refresh, resolved/reconciled exception record, and independent release under the unchanged C34 version. Any rule change starts a separate version and new observation history.

## 8. Forward-paper gate and validator

The case's [forward-paper ledger template](../data/c33_forward_paper_ledger_template_20260815.json) is `template_only_no_observations` as of 2026-08-15. Six uninterrupted, independently reviewed monthly observations are absent. C35 therefore remains `research_only`; the validator is structural only and cannot change this status to `paper_operable`.

Run the read-only validator:

```bash
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python workspace/research/domestic-5pct-target-paper-strategy-20260815/tools/c35_validate_c34_operational_action_card.py
```

It verifies C34/C31/C35 source links and hashes, the five-code core, dual-horizon score and inverse-volatility target math (including strict equality and invalid-volatility tests), timing separation, protection formula, no-leverage/no-short/no-futures controls, and the still-incomplete forward-paper gate. A passing validator result means only that this action card matches the frozen research protocol; it does not admit a strategy, establish total return, or authorize an external action.

## 9. Source references

| Reference | Date / hash | Use in C35 | Boundary |
|---|---|---|---|
| [C34 protocol](c34_dual_horizon_inverse_vol_etf_protocol_20260815.json) | 2026-08-15; `9d853055ef102e148fd5d265bbaadca56642f7c8de0da985ae00a315a8c25ac5` | Closed universe, monthly D/E timing, dual-horizon/inverse-volatility rule, price protection, no-action controls | Market-price proxy only; no total return, execution, or operating-right conclusion |
| [C31 product cards](c31_etf_product_diligence_refresh_20260815.json) | 2026-08-15; `939b57fa0ec19ed55500a99c82c3eaba73f8b8572204bc4eef814fd272ad2fcd` | Dated five-code product evidence and category-level mechanics | Current terms, access, quote, fill, fee, tax, and settlement remain unverified |
| [C33 forward-paper template](../data/c33_forward_paper_ledger_template_20260815.json) | 2026-08-15; `229014d774cf5e94e5218023d2b0a40b34b5f773183f3626afe387ec9fd887d4` | Six-month forward-paper requirement | It is an empty template, not a completed record |
