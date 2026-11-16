# Chinese Prose Style Audit — R2 Reopen #3

## Scope

- Case: `global-institutional-strategy-personal-20260815`
- Trigger: user identified a surviving paired-negative frame using `没有` and `也没有`
- Reader-facing source: `main.tex` and all `sections/*.tex`
- Release text: `main_current_text.txt` extracted from the rebuilt `main.pdf`
- Immutable-text exceptions: none

## Current Hard Gate

The scan covers `最难`, `而非`, governed contrast variants, every authored `不是` and `没有` occurrence, plus paired negative stacks such as `既不……也不……`. The literal scans are deliberately conservative: each occurrence requires a disposition before R2 may close.

## Repair History

| Reopen | Finding | Repair | Disposition |
| --- | --- | --- | --- |
| First rewrite | 29 literal template matches across 27 reader-facing lines, then 14 close-variant constructions | Rewrote the matched text and extended the pattern set | Closed after source/PDF-text zero-hit check |
| Second rewrite | A strict authored-`不是` review found 33 reader-facing lines with remaining contrastive negative framing | Rewrote titles, prose, captions, tables, source notes and callouts into direct statements | Closed after source/PDF-text zero-hit check |
| Current rewrite | A strict authored-`没有` review found 17 reader-facing lines; paired negative stacks were reviewed in the same pass | Rewrote scope statements, legal/tax boundary prose, headings, tables, source notes and callouts into direct statements | Closed after source/PDF-text zero-hit check |

All items were author-written. No quotation, legal/regulatory text, or source-title exception was invoked.

## Final R2 Scan

| Check | Result |
| --- | --- |
| TeX source scan | PASS — 0 eligible hits |
| PDF text scan | PASS — 0 eligible hits |
| Normalized-text scan | PASS — 0 eligible hits |
| Immutable-text exception review | PASS — 0 exceptions |
| Fact-preservation check | PASS — no numbers, dates, source IDs, citations, formulas, q=0 boundaries, risk conclusions, or implementation boundaries changed |
| R2 disposition | CLOSED — `reader_prose_template_ban` verified |

## Scan Expression

```text
不是 | 没有 | 最难 | 而非 | (?:并非|绝非)[^。！？；\n]{0,96}(?:而是|也(?:不是|非|不)) | 既非[^。！？；\n]{0,96}也非 | (?:既)?不[^。！？；\n]{0,96}也不 | (?:无|未)[^。！？；\n]{0,96}也(?:无|未)
```

This audit establishes reader-facing style compliance only. It does not change the report's research-only scope, return-evidence limitation, q=0 state, or implementation boundary.
