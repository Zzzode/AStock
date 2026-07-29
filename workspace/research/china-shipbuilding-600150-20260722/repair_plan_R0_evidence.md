# R0 Evidence Repair Plan — Second Recheck

- Case: `china-shipbuilding-600150-20260722`
- R0 cycle status: `PASS`
- Report publishability: `BLOCKED` pending R1-R4, final PDF and final sign-off
- R0 score: `95/100`
- Open: `0 S / 0 A / 0 B`
- Closed in second recheck: `R0-A-001`, `R0-A-004`, `R0-A-007`

## No open R0 repair actions

The second maker-checker reread verified:

1. `artifact_contract.md/json` has individual field-level rows for claim audit, source exhaustion, customer audit, coverage gap, competitive landscape and chain earnings bridge.
2. Relationship and customer row-governance entries contain concrete source IDs, exact local paths, exact URLs, dates and source types; generic path/URL placeholders are removed.
3. All 15 broker rows contain `ticker=600150.SH`; forecast consensus weight is separated from target-price valuation weight, and all unavailable/weak target-price anchors remain zero-weight.

## Residual evidence constraints carried into R1

- Original broker target prices remain unavailable; Street target-price valuation weight is zero.
- Ship-type ASP, delivery schedule, unified yard utilization and contract payment terms remain method-specific blocks.
- Backlog remains a visibility proxy, not revenue; military, Hudong-Zhonghua and unsupported group options remain excluded from base valuation.

No maker artifact should relax these constraints without new official or original evidence and another R0 reopening.

## Market-Data Remediation Recheck — 2026-07-23

Status: `SOURCE_RECHECK_PASS_PENDING_FINAL_GATE_REFRESH`; no open S/A issue.

- `PR-02` now gives an archived, explicitly `fqt=1` front-adjusted 727-day daily series together with `fqt=0/2` controls, cutoff price/liquidity/turnover/circulating-share fields and source hashes.
- `PR-03` now gives dated SSE margin evidence, quarterly SSE Shanghai Connect stock, Q2 public-fund aggregate, and a defined Dragon-Tiger negative query with raw responses.
- Strict free float and daily Shanghai Connect net holdings are not omissions. They are unavailable at the required definition/frequency and each has an archived source-specific boundary. The report uses circulating A shares and quarterly holdings only with their correct labels.

The main agent must refresh the case-local verifier, shared research gate and workflow evaluator after all current review/sign-off files are present. Historical 50-page verification results are not current evidence.
