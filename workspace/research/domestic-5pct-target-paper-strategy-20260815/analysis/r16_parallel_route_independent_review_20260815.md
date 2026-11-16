# R16 — Parallel-Route Independent Review

- Case: `domestic-5pct-target-paper-strategy-20260815`
- Review date / cutoff: `2026-08-15`, Asia/Shanghai
- Reviewer mode: independent, read-only maker-checker
- Scope: C37--C42, the C34 separation boundary, the associated source/probe archives, and reader-facing research-boundary language. This review creates no model result, investment view, selection, weight, or external instruction.

## Executive Verdict

- Review-scope publishability: `BLOCKED`.
- Scope-limited review score: `55/100`.
- New R16 findings: `1` open S-level, `1` open A-level, and `1` open B-level.
- Inherited release condition: the current repository gate run is `57 PASS / 36 FAIL`, `RESULT FAIL`; the case remains non-publish-bound and R15's pre-existing publication/actionability blockers are not reissued here as duplicate findings.
- Admission decision: **no strategy, ETF/index route, or individual security is admitted.** C37 remains a source-route `NO_GO`; C39 remains `NO_ACTION` with risk-model `VETO`; and `600519`, `600900`, and `601088` remain `NON_ADMITTED_RESEARCH_SUBJECT / NO_ACTION`.

## Review Scope and Method

- Read C37--C42 Markdown/JSON twins and C34's frozen diagnostic boundary.
- Parsed all six new JSON artifacts and checked their IDs, cutoff dates, decision fields, and C38 G0--G9 matrix coverage.
- Recomputed file sizes and SHA-256 hashes for the 22 C40--C42 primary files and three anti-bot probes; checked dossier-to-manifest source bindings.
- Rechecked the three sibling manifests referenced by C37 and their retained objects: C7 `6/6`, R4 `6/6`, and R3 `5/5` entries passed byte/hash verification.
- Decompressed and classified each retained SSE probe payload; all three are HTML/JavaScript anti-bot challenges, not announcement PDFs.
- Scanned C37--C42 plus current TeX/PDF-text reader material for an exact non-URL `3%` objective, principal/capital-preservation objective, cash-reinvestment objective, and affirmative investment-action/guarantee language.

## S-Level Issues (BLOCK publication)

### R16-S-001 — C40's declared Chinese-language dossier contains untranslated substantive valuation/risk/catalyst logic

- Lifecycle: `open -> fixed -> verified -> closed`; current state: `open`.
- Location: `analysis/c40_600519_equity_diligence_20260815.md`, lines 16--30.
- Evidence: the artifact declares `document_language: zh-CN`, while the reader-visible `Fundamental-analyst record` is English and includes `Catalyst Calendar`, `Valuation Context`, `Thesis Breakers`, and evidence-risk logic. This is substantive valuation/risk/catalyst content rather than a proper noun, ticker, formula, or source title.
- Impact: C40 cannot be released as a Chinese reader-facing research dossier. The defect does not relax any C38 gate or admit `600519`.
- Fix: translate this block into Chinese without changing its evidence, figures, status, or non-admission conclusion; then independently re-read the Markdown and JSON-context fields for language consistency.
- Owner: `research-prose-polish` / `research-prose-polish`.

## A-Level Issues (must fix)

### R16-A-001 — C40's machine-readable point-in-time statement contradicts its retained raw query response

- Lifecycle: `open -> fixed -> verified -> closed`; current state: `open`.
- Location: `analysis/c40_600519_equity_diligence_20260815.json`, lines 166--169 and 509; corroborated by the Markdown at line 53 and `sources/official-600519-equity-diligence-20260815/manifest.json`.
- Evidence: C40-S05 correctly records `query_response_case_archived_h1_pdfs_not_retrieved_due_antibot`, a retained path, and SHA-256 `ac3d…effd`. The same JSON later says that the timestamp semantics **and raw response are not retained**. The raw exchange query response is retained and hash-verified; only the H1/policy-change PDFs, timestamp semantics, content validation, and a usable point-in-time chain remain unclosed.
- Impact: this is a material source-record/twin inconsistency. It is conservative rather than a silent admission, but it obscures exactly what the raw-source upgrade did and did not establish.
- Fix: amend the later machine-readable statement to distinguish “raw query response retained” from “timestamp semantics/content/availability chain not validated”; preserve G1/G8 as un-cleared and do not modify the anti-bot/PDF boundary. Re-run the same source-binding review before marking fixed.
- Owner: `equity-research` / `source-governance-analyst`.

## B-Level Issues (should fix)

### R16-B-001 — Empty named probe batch has no manifest or provenance statement

- Lifecycle: `open -> fixed -> verified -> closed`; current state: `open`.
- Location: `sources/probe-sse-600519-announcement-query-20260815/`.
- Evidence: the directory is empty, has no `manifest.json`, and has no references elsewhere in the case. It is not used by C40, whose relevant anti-bot evidence is correctly retained in `probe-sse-600519-disclosure-access-20260815/`.
- Impact: no evidence, hash, gate, or admission conclusion is affected, but the empty capture-batch name weakens source-tree hygiene.
- Fix: either add a minimal zero-capture manifest explaining the batch was abandoned, or remove the empty staging directory after confirming it has no intended capture. Do not relabel it as an announcement source.
- Owner: `equity-research` / `source-governance-analyst`.

## Verified Controls and Findings

1. **C37 remains correctly fail-closed.** Its Markdown and JSON both state `NO_GO_PUBLIC_PRIMARY_HISTORICAL_TEST`; G1--G6 are not closed, G7 is not established, and G8 is specification-only. It neither selects an ETF/index nor computes a historical return. The cross-case evidence is explicitly labelled as sibling provenance rather than a local data delivery, and the referenced C7/R4/R3 manifest hashes resolve and validate.
2. **C39 is distinct from C34 and remains vetoed.** C39 explicitly prohibits reuse of C34 products, rotation, relative momentum, dual-horizon score, inverse-volatility sizing, sleeve construction, price-proxy cost load, samples, diagnostics, results, and parameters. The actual C34 ETF codes have zero hits in C39's Markdown/JSON; the only mentions of C34 mechanics are prohibitions. C39's current status is `NO_ACTION` and its risk-model status is `VETO`.
3. **C40--C42 obey C38's G0--G9 non-admission design.** C40 records G0--G5 `PARTIAL_NOT_CLEARED` and G6--G9 `BLOCKED`; C41 records G0--G5 `PARTIAL_NOT_CLEARED`, G6--G8 `BLOCKED`, and G9 `NOT_PERFORMED`; C42 records zero passed gates, G0--G5 `PARTIAL_UNCLEARED`, and G6--G9 `BLOCKED`. None uses a current price, valuation, target, upside/downside, total-return, liquidity, weight, or execution conclusion.
4. **Archive upgrades are real but bounded.** Dossier-to-manifest SHA-256 bindings pass for C40 `9/9`, C41 `6/6`, and C42 `7/7`; all 25 local primary/probe files pass both byte and SHA-256 checks. C40 and C42 correctly distinguish an exchange query/locator from anti-bot direct-PDF retrieval. The one C40 wording inconsistency is recorded separately as R16-A-001.
5. **Anti-bot records are correctly classified.** All three gzip objects pass `gzip -t` and decompress to HTML/JavaScript challenge content. C40 and C42 do not treat those files as issuer announcements, PDFs, primary numerical evidence, or same-session availability proof.
6. **No prohibited legacy objective or affirmative investment language was found.** After excluding percent-encoded URLs, the review found no exact reader-facing `3%` objective, principal/capital-preservation objective, or cash-reinvestment objective in C37--C42 or current TeX/PDF-text. C39's 5% research hurdle is expressly not a promise/floor/forecast, and its cash-ledger language is an event-accounting constraint, not a reinvestment objective. References to `NO_ACTION`, “not a recommendation,” or “do not trade” are negative governance boundaries; no affirmative buy/sell/hold, allocation, guarantee, or permission-to-trade wording was found.
7. **Twin-format validation is largely sound.** All six JSON files parse; all six Markdown/JSON filename pairs exist; their artifact IDs, cutoffs, and top-level non-admission decisions are aligned. R16-A-001 prevents a fully clean semantic-twin PASS for C40 until its internal source-capture wording is reconciled.

## Lifecycle Summary

| State | Findings |
|---|---|
| Open | `R16-S-001`, `R16-A-001`, `R16-B-001` |
| Fixed, awaiting independent verification | None |
| Verified / closed in this R16 cycle | No repair finding; the seven control conclusions above were independently verified as current-state checks. |

## Verifier Summary

- Repository research-gate runner, read-only: `57 PASS / 36 FAIL`, `RESULT FAIL`.
- This is consistent with the case's `not_publish_bound` status and R15's existing publication-gate blocker; it cannot be treated as a publication pass or as an actionability upgrade.
- No case-local `39 PASS / 0 FAIL` verifier result exists. Publication remains blocked independently of the R16-local findings.

## Final Decision

- Strategy admitted: **No**.
- C37 ETF/index historical-test route admitted: **No** (`NO_GO_PUBLIC_PRIMARY_HISTORICAL_TEST`).
- C39 hypothesis admitted as a usable strategy: **No** (`NO_ACTION`; risk-model `VETO`).
- `600519`, `600900`, or `601088` admitted as an individual security: **No**; each remains a non-admitted research subject.
- External action, order, allocation, performance, or guarantee authorization: **None**.
