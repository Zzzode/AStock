# Exhibit Format Review R1 — 雅化集团完整覆盖

**Scope:** `main.pdf`, rendered from the final 2026-07-23 source set to `rendered/full-note-20260723-r3/` at 150 dpi. Review date: 2026-07-23.

## Result: PASS

- **Exhibit inventory:** 38 labelled `exhibitbox` tables in the included chapter and appendix sources; all contain a decision-useful title, table body and source or data-quality note in the surrounding section.
- **Numbering:** main chapters use chapter-local labels (1-1 through 13-2, with 11-3); appendices use the contiguous A-1 through A-11 sequence. The prior duplicated appendix labels were corrected before the final render.
- **Width and legibility:** final render was inspected on cover, contents, operating, market, risk, evidence, governance and reconciliation pages. No clipped column, overlapping rule, unreadable header, placeholder glyph or unembedded-font symptom was observed.
- **Evidence separation:** historical fact tables identify company disclosure; House scenario tables identify their assumption status; broker and peer materials are not presented as House inputs.
- **Exceptions:** none. No decorative or redundant exhibit was retained merely to meet a page target.

## Checks performed

| Check | Result | Evidence |
|---|---|---|
| PDF page count and render completeness | PASS | `pdfinfo` = 40 pages; 40 PNG pages in `rendered/full-note-20260723-r3/`. |
| Font embedding and Unicode | PASS | `pdffonts` shows embedded, subsetted Unicode-capable CJK and Latin fonts. |
| Overflow / clipping scan | PASS | PDF text has no replacement glyph; visual inspection found no clipped table body or source note after the source-note repair. |
| Appendix exhibit identifiers | PASS | Extracted PDF contains one contiguous A-1 to A-11 sequence. |
| Highest-risk wide tables | PASS | Manually inspected market table 7-1/7-2, risk table 9-2, evidence table A-8, governance table A-10 and reconciliation table A-11. |

## Control conclusion

The final exhibit set is suitable for an institutional single-stock report: it makes the model, its evidence boundary and the investment action readable without reducing the report to table-only narrative.
