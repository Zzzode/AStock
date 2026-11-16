# Build Provenance — 2026-08-12 Final Repair

- Status: **BUILT_AUTHOR_QA_PENDING_INDEPENDENT_REVIEW**
- Case / scope: `stable-income-multi-asset-strategy-20260811` / `strategic-allocation-etf-first-v2-20260811`
- Timestamp: `2026-08-12T04:57:57+08:00`
- Revision: final source-scope, model, prose and pagination repair. The active reader uses a 15/15/0/0 locally archived source scope; legacy S14, M01 and D01--D08 remain unrecovered audit history and are prohibited from active conclusions.
- Build platform: Linux 5.15.152.bsk.4-amd64 x86_64 GNU/Linux
- Build engine: XeLaTeX (`/usr/bin/xelatex`)
- TeX distribution: TeX Live 2022/Debian — `XeTeX 3.141592653-2.6-0.999994`
- CJK font configuration: Noto Serif CJK SC and Noto Sans CJK SC; `ctexrep.cls` and `xeCJK.sty` resolved locally.
- Build command: `/usr/bin/xelatex -interaction=nonstopmode -halt-on-error main.tex` (two passes)
- Reader-source SHA-256: `04ba969991bb6cb70e21da378ff4b1c93ea8dd100fc0dedf884f05260a55f94d`
- Reader-source graph SHA-256: `8dc0c58118162f8e456caf8ec025ed9312c5c900b97c5f3ee94af0a2c00302e4`
- PDF: `main.pdf`, 14 A4 pages, SHA-256 `ece9c8436ca4117889587a17177251a1ba93cf3af945e05ecd75bb20098a50f9`
- Extracted text: `main_current_text.txt`, SHA-256 `374cc0f1dd2c6b6fbb00aeedff324c6b93a094f03b4702508f34c3e9b360435b`
- Full render: `rendered/full-20260812-0457/`, 14 PNG pages at 150 DPI.
- Diagnostics: 0 fatal errors, 0 undefined-control-sequence errors, 0 missing-character records and 0 `Overfull \\hbox` records. One `Underfull \\hbox` at the cover-page source line 23 remains; it has no reader-visible clipping. `pdffonts` reports embedded fonts.
- Author visual review: all 14 rendered pages were inspected, including the target/action, return/cash, stress/actual-drawdown, implementation, source-appendix and disclosure pages. No clipping, overlap, table truncation, glyph fallback or unintended near-empty continuation page was observed.

The standard CLI adapter was unavailable because the workspace `.venv` does not contain the `astock` and `typer` runtime dependencies. Direct XeLaTeX is therefore the recorded fallback. This build packet records author build and visual-QA evidence only; independent R1--R4 review is recorded separately. The execution-eligibility policy remains `not_run`; all ETF qualification states remain `q=0` until a dated current-session packet passes.
