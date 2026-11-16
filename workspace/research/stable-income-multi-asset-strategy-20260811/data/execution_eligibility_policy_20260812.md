# Execution Eligibility Policy — Controlled Model, 2026-08-12

## Status and purpose

- Status: **NOT RUN**. This file is a controlled model-policy template, not an execution-day observation packet or authorization to trade.
- Scope: the designated model instruments in `model_portfolio_implementation_20260812.json`.
- Rule: a missing field, stale timestamp, unavailable source, failed threshold, or failed look-through produces `q=0`. No field is assumed to pass from the 2026-08-11 historical packet.

## Required dated validation record

For each ETF, retain the source name, URL or terminal identifier, capture timestamp, market session, raw-record hash and pass/fail reason for: current product document/version and fee; trading status; IOPV or the relevant reference value; market price; premium/discount; best bid and ask; spread; same-session traded value or displayed executable depth; account eligibility; minimum lot; and available cash. Product documents must be current as of the validation date; market fields must be captured during the same China market session as the proposed tranche.

The protected-liquidity sleeve additionally records the insured institution, aggregate qualifying deposit exposure, withdrawal/term terms and, where relevant, direct-government-bond maturity. The CNY500,000 per-depositor/per-institution deposit-insurance ceiling is a source-backed boundary (S05), not a substitute for account-level validation.

## Controlled pass/fail thresholds

The following are model controls, not observed market facts or product promises:

| Control | Pass condition |
|---|---|
| Trading status | Normal trading; no suspension or unresolved material product event. |
| Price-reference availability | Market price and IOPV/reference value are both present with same-session timestamps. |
| Premium/discount | Absolute premium/discount is at most 1.00%. |
| Quoted spread | Best-bid/ask spread divided by mid-price is at most 0.50%. |
| Tranche liquidity | Proposed tranche is at most 10% of the recorded same-session traded value or independently captured executable depth. |
| Dividend look-through | For the combined 510880/512890 position, sector exposure is at most 25% of total portfolio and top-ten issuer-group exposure is at most 35% of the equity sleeve. |
| Caps | Staging cash does not exceed CNY10,000; dividend ETF exposure does not exceed 35% of portfolio; gold does not exceed 12%; rate bonds do not exceed 60%. |

## Deterministic failure waterfall

1. A failed or unobserved ETF test sets its `q=0`; no related trade is inferred.
2. The affected amount is placed in the **eligible protected-liquidity reserve**. It never increases staging cash above its CNY10,000 hard cap and does not automatically increase 511010 or another risk sleeve.
3. A later allocation requires a fresh, complete pass of this policy and occurs only at the next scheduled tranche or rebalancing review. It is not a catch-up trade.
4. REITs and direct stocks remain at CNY0 until their separate gates are independently passed.

The policy makes the portfolio temporarily more defensive when data or eligibility is missing. It does not turn this draft into a broker instruction, suitability determination, return forecast or personal recommendation.
