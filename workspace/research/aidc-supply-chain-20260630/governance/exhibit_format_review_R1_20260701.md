# Exhibit Format Review R1

- Project: aidc-supply-chain-20260630
- Review date: 2026-07-01
- Scope: Chapter 7 valuation tables plus PDF render spot checks
- PDF: main.pdf, 43 pages
- Chapter 7 Overfull audit: max 2.67pt, >20pt count 0
- Case verifier: 97 PASS / 0 FAIL
- Industry-chain verifier: 81 PASS / 0 FAIL
- Global gates: 227 PASS / 0 FAIL
- Conclusion: Chapter 7 valuation table layout PASS after repair

## 0. Traffic-Light Matrix

| Exhibit | Source | Pre-repair issue | Repair | Status |
|---|---|---|---|---|
| Unified 56-stock valuation table | sections/ch07_valuation.tex | 18-column tiny longtable compressed numeric, method, evidence, catalyst and invalidation fields into one unreadable grid | Split into three narrow tables: valuation numeric details, method/evidence/Street anchor, catalyst/invalidation | PASS |
| Broker/Street coverage table | sections/ch07_valuation.tex | Raw enum labels, long broker strings and unrounded EPS fields caused cramped cells | Replaced raw buckets with short Chinese labels, shortened broker/date fields, rounded forecast fields | PASS |
| Valuation quality gate table | sections/ch07_valuation.tex | Raw issue type and long decimal detail overlapped columns | Replaced with Chinese issue labels and rounded action text | PASS |
| Valuation chapter visual gate | tools/verify_research_workspace.py | No gate caught the unreadable table layout | Added valuation_chapter_visual_layout gate and wired final signoff | PASS |

## 1. Bug Class Summary

### Class F: Text clipping / unreadable table compression

Root cause: a single longtable attempted to carry 56 rows and 18 columns, including long prose fields. The table compiled but produced unreadable pages.

Repair:
- Keep the 56-row valuation universe intact.
- Split the display surface by reader task: numeric valuation, method/evidence/Street anchor, catalyst/invalidation.
- Use code/company makecell pairs and short labels rather than shrinking the entire table.

### Class H: Overfull hbox risk

Chapter 7 now has only minor overfull entries below the 20pt hard threshold. The remaining >20pt Overfull entries are outside Chapter 7 and should be handled in a separate full-report visual QA pass.

## 2. Verification Evidence

| Check | Result |
|---|---|
| Chapter 7 raw enum leakage | PASS |
| Old 18-column valuation table pattern removed | PASS |
| Chapter 7 Overfull >20pt | PASS, count 0 |
| Rendered page count | PASS, 43 pages |
| Case verifier | PASS, 97 / 0 |
| Industry-chain verifier | PASS, 81 / 0 |
| Global gates | PASS, 227 / 0 |

## 3. Remaining Non-Chapter-7 Risk

The full report still has non-Chapter-7 Overfull >20pt entries in Chapter 4 and appendices. They do not invalidate this Chapter 7 repair, but the report should not be described as globally visual-perfect until a full exhibit-format pass clears those entries.
