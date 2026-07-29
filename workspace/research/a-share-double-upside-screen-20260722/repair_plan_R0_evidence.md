# Repair Plan — R0_evidence

## Status

- Publishability: **PASS**
- R0 score: **93/100**
- Open findings: **0 S-Level / 0 A-Level / 1 accepted-residual B-Level**
- Numeric reconciliation: **PASS** for the six deep-model names' prices, total shares, market caps, FY2025/Q1 actuals, H1 previews and Q1 operating cash flow.

## Required repairs

### `equity-research` — target-horizon consistency (`R0-S-001`)

Artifacts:

- `main.tex`
- `sections/ch09_risks.tex`
- `analysis/valuation_model.md`
- `analysis/valuation_audit.md`
- `analysis/risk_framework.md`
- regenerated `main.pdf` and `main_current_text.txt`

Status: **CLOSED / VERIFIED**.

`main.pdf` was rebuilt at 17:32:25 CST and `main_current_text.txt` regenerated at 17:32:39 CST. A focused full-corpus search finds no asserted 6–12 month target horizon. The abstract, decision, methodology, valuation and risk sections consistently state that the CNY42 and CNY103 target horizons are not disclosed.

### `equity-research` / `source-governance-analyst` — source-to-claim trace (`R0-A-001`)

Artifacts:

- `data/source_registry.md`
- `data/source_registry.json`
- `data/claim_audit.md`
- `data/claim_audit.json`

Status: **CLOSED / VERIFIED**.

`OFF-600150-SHARES` and `OFF-301308-SHARES` now point to the archived official announcements with official URLs, paths, use and limitations. The registry now individually represents all 21 official PDFs. Claim audit adds the CNY248.496bn and CNY164.338bn price-times-official-shares bridges, and all referenced source IDs resolve.

### `equity-research` / `data-collector` — immutable market capture (`R0-B-001`)

Artifacts:

- `data/raw_market_data.md`
- `data/source_registry.md/json`
- `source_exhaustion_log.md/json`
- case-local market-source captures

Status: **OPEN / ACCEPTED RESIDUAL**.

Archive the exact AStock/Sina output, Tencent quote/K-line payloads and market-close page with capture metadata and hashes when practical. Until then, retain the current two-source reconciliation and its evidence-ceiling disclosure.

Acceptance: each market source has an immutable local artifact or an explicit, governed evidence-ceiling disclosure.

## Re-review gate

`R0-S-001` and `R0-A-001` are closed. `R0-B-001` is an accepted audit-trail residual and does not block R0. No blocking R0 repair remains. The full-case verifier was intentionally not rerun in this independent evidence-only pass.
