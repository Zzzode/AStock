# Personal Admission Scorecard

No current sleeve is approved. The following is a six-step checklist for evaluating a future **paper** candidate; a failed check freezes the candidate rather than being overridden by a desirable narrative.

| Step | Required evidence | CTA / factors / events application | Freeze condition |
| --- | --- | --- | --- |
| 1. Account and legal boundary | dated broker/exchange/product facts; jurisdiction | contract eligibility or stock/product scope | entitlement unclear |
| 2. Time semantics | publication timestamp and data-available timestamp | next-session signal; delayed fundamentals; event timestamp | look-ahead risk |
| 3. Universe and liquidity | lifecycle, suspension, delivery, turnover and capacity | contract roll; stock liquidity; event availability | exit assumed but unavailable |
| 4. Exact rule | formula, threshold, holding/exit and corporate-action handling | CTA score; factor rank; surprise gate | vague discretionary override |
| 5. Replay and costs | point-in-time data, fees, taxes, slippage, margin and failed fills | paper TWRR and trade ledger | gross or survivorship-only result |
| 6. Risk and monitoring | NAV basis, loss limit, margin/cash waterfall, invalidation owner | daily status and stop/review flag | no approved loss rule |

## Minimum protocol details

- **CTA:** use closes available before the decision time; calculate the 21/63/126-day volatility-normalised score, assume the earliest permissible later-session action, and explicitly model roll, daily settlement, margin, limit and delivery risks.
- **Factors:** freeze the accounting data as-of the first public availability date; form a cross-sectional score only after liquidity, concentration, industry and corporate-action exclusions; do not use later-restated fundamentals in an earlier decision.
- **Events:** archive the primary source, publication timestamp and availability timestamp; use only events no more than five trading sessions old; define surprise, alternative explanation and invalidation before replay.

The scorecard does not approve a trade. Its output is either `paper research admissible` or `blocked pending evidence`.
