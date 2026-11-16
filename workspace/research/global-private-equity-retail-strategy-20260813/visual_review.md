# Visual review

## Method

Rendered all 20 PDF pages at 110 dpi from `main.pdf` at 2026-08-14 00:47:45--00:47:49 CST, after the final 2026-08-14 00:39:46 CST XeLaTeX build. The reviewed PDF SHA-256 is `a5b8b28c8594113c35c477f7063e2f5c52a0ffb48d496f68b253e01fc9767340`; this is the same identity recorded in `data/build_provenance_20260813.json`. Visual review sampled the cover, decision dashboard, institutional-method matrix, public-evidence funding diagram, China-constraint chapter, red-team page and source appendix.

## Sampled pages

| Render | What was checked | Result |
|---|---|---|
| `rendered/release-page-01.png` | Cover, Chinese font fidelity, decision and evidence boxes, footer boundary | PASS — rendered at 00:47:45 from the final PDF; readable title hierarchy, no clipped box or CJK fallback. |
| `rendered/release-page-05.png` | Decision dashboard and three-column table | PASS — rendered at 00:47:46 from the final PDF; table stays within exhibit frame and conclusion/risk boundary is visible. |
| `rendered/release-page-06.png` | Seven-manager matrix | PASS — rendered at 00:47:46 from the final PDF; columns remain legible and source note follows the table without semantic overlap. |
| `rendered/release-page-11.png` | Public-evidence funding diagram and research-satellite boundary | PASS — rendered at 00:47:47 from the final PDF; diagram, headings and q=0 language remain legible. |
| `rendered/release-page-13.png` | China-constraint chapter and public-REIT discussion | PASS — rendered at 00:47:48 from the final PDF; current-rule caveats are visible and no table-cell clipping appears. |
| `rendered/release-page-16.png` | Red-team warning box and failure-mode table | PASS — rendered at 00:47:48 from the final PDF; red risk box is visually distinct and table cells show no clipping. |
| `rendered/release-page-18.png` | Source appendix and limitation wording | PASS — rendered at 00:47:49 from the final PDF; source table stays within frame with no clipped reader-facing content. |

## Minor diagnostics disposition

The XeLaTeX log retains only non-material underfull messages in the narrow cover metadata and in deliberately compressed table text. The former box-edge overfull diagnostics were eliminated before this release build. The sampled renders show no clipped reader-facing text, overlap or unsafe whitespace.
