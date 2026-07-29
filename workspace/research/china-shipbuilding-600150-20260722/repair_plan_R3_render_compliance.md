# R3 Render & Compliance Repair Plan — Final Maker-Checker

- Case: `china-shipbuilding-600150-20260722`
- R3 cycle status: `PASS`
- Institutional status: `INSTITUTIONAL_PASS`
- Report publishability: `BLOCKED` pending R4, workflow evaluation, final sign-off and `39 PASS / 0 FAIL`
- R3 score: `92/100`
- Open: `0 S / 0 A / 3 B`

## No open publication-blocking R3 repair actions

The independent R3 maker-checker inspected all 50 rendered pages and verified:

1. The A4 PDF contains 50 pages and all 50 current render PNGs are present at a consistent `910x1287` resolution.
2. Cover, English abstract, three-page contents, every chapter opening, all wide tables, four TikZ diagrams, the cycle chart, five longtables, appendices and final important-statement page are visible and readable.
3. The repaired ch09 seven-column scenario table and ch10 seven-column broker matrix remain entirely inside their exhibit boundaries.
4. No page is blank; no publication-blocking orphan, clipping, overflow, overlap, missing glyph, mojibake or footer/header collision remains.
5. Three non-blocking layout defects remain: low-density orphan pages 26/35/47, a sentence-level widow/orphan across pages 42-43 and an overly dense risk matrix on page 38.
6. All PDF fonts are embedded/subsetted and have Unicode maps. A fresh `pdftotext -layout` extraction is byte-identical to `main_current_text.txt`.
7. Current price/target/upside/range/action remain visibly consistent at `33.02 / 33.07 / +0.15% / 31.64-35.96 / 中性偏多（持有/等待验证）`; the final disclaimer is complete and visible.
8. The build audit records two MacTeX XeLaTeX passes and final project-CLI success at 50 pages. The only residual Overfull box is `0.24898pt` in Appendix A; it is below the `20pt` hard gate and visually undetectable.

## Non-blocking R3 repairs

1. `R3-B-001` — recover the terminal boxes/conclusions on pages 26, 35 and 47 onto the prior pages using local page enlargement or spacing changes; do not reduce body font size.
2. `R3-B-002` — keep the short Appendix A paragraph together with a three-line `Needspace` guard or equivalent pagination control.
3. `R3-B-003` — split or shorten the page-38 risk matrix so it can return from `scriptsize` to `small` while preserving every threshold, sensitivity and action.

These are B-Level presentation findings. They do not obscure valuation, recommendation, source hierarchy or risk conclusions, so R3 remains `PASS`; they should be fixed before R4 or explicitly accepted as final-signoff residuals. Any fix reopens the PDF and requires a new 50-page R3 review.

## Residual constraints carried into R4

- R3 approval covers this exact PDF hash: `e5812560ed01ac79f451a62bad789648c9abc399c2f870da122d40a60e573f66`.
- Any PDF/source/font/pagination/target/disclaimer change, including closure of the three B findings, reopens R3 and requires a new full visual review.
- R4 must independently confirm the investment conclusion, valuation support, source boundary, risk/invalidation logic and compliance wording against the exact reviewed PDF.
- Publication remains blocked until workflow evaluation, final sign-off, dependency refreshes and the mandatory case-local `39 PASS / 0 FAIL` result are complete.

## Reopen triggers

Reopen R3 if a downstream change:

1. changes the PDF hash, page count, page size or render set;
2. breaks byte identity between fresh PDF text extraction and `main_current_text.txt`;
3. introduces clipping, overlap, blank pages, detached single-line orphans or unreadable core exhibits;
4. creates an Overfull box above `20pt`, a non-embedded font or a missing Unicode map;
5. changes `33.02 / 33.07 / +0.15% / 31.64-35.96`, the action label or the disclaimer without synchronized model/report refresh.

## Market-Data Remediation Recheck — 2026-07-23

Status: `PARTIAL_RECHECK_NO_BLOCKER_PENDING_FULL_RENDER_REFRESH`.

The current PDF is 51 A4 pages with SHA-256 `847ce2676eb646fba6520ae1f0bf77aa96200918fb6db87f687ef0577dc04052`. Direct renders of physical pages 36--39, which contain the new Chapter 12 market tables and the following chapter opening, show no clipping, overlap, broken glyph or unreadable source note. The Appendix A text also contains the `PR-02/PR-03` source rows and key-claim mapping.

This is deliberately not a full R3 completion claim: the main agent must refresh the complete 51-page render set and then recheck all pages, text-snapshot identity, fonts/overfull diagnostics and dependent gate artifacts. The inherited R3-B presentation waivers are historical and need revalidation if further pagination changes.
