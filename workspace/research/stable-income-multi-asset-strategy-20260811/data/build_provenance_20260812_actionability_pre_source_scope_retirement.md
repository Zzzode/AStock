# Build Provenance — 2026-08-12 Comprehensive Repair

- Status: **BUILT_UNREVIEWED**
- Case / scope: `stable-income-multi-asset-strategy-20260811` / `strategic-allocation-etf-first-v2-20260811`
- Timestamp: `2026-08-12T04:20:20+08:00`
- Revision: comprehensive model, source-boundary, prose and exhibit-layout repair; the active reader now identifies target sleeves, a controlled `q` gate, deterministic protected-liquidity fallback, the `r`/`D_0` boundary and the scenario-versus-observed-drawdown distinction.
- Build platform: Linux 5.15.152.bsk.4-amd64 x86_64 GNU/Linux
- Build engine: XeLaTeX (`/usr/bin/xelatex`)
- TeX distribution: TeX Live 2022/Debian — `XeTeX 3.141592653-2.6-0.999994`
- CJK font configuration: Noto Serif CJK SC and Noto Sans CJK SC; `ctexrep.cls` and `xeCJK.sty` resolved locally.
- Build command: `/usr/bin/xelatex -interaction=nonstopmode -halt-on-error main.tex` (two passes)
- Reader-source SHA-256: `8d9221de4f648b86e82e41b0115dca46841dfdf0f186090026e067c2a5edbac2`
- Reader-source graph SHA-256: `f3c4db6668bd52862a5821e62988bfad54646a000f993e81c702705beb645889`
- PDF: `main.pdf`, 17 A4 pages, SHA-256 `86ac768d39f425aa116c4ef8fac2492b5c192329bfe00935826be5b68cea5440`
- Extracted text: `main_current_text.txt`, SHA-256 `adcab61e68a792b427fd04ad5be09c98d25637297624980816402eb51fc26a2d`
- Full render: `rendered/full-20260812-0420/`, 17 PNG pages at 150 DPI.
- Diagnostics: 0 fatal errors, 0 undefined-control-sequence errors, 0 missing-character records and 0 `Overfull \\hbox` records. One `Underfull \\hbox` at the cover-page source line 23 remains; it has no reader-visible clipping. `pdffonts` reports embedded fonts.
- Author visual review: all 17 rendered pages were inspected, with targeted reinspection of the target/action, actual-drawdown and appendix/disclosure pages after pagination repair. No clipping, overlap, table truncation, glyph fallback or unintended near-empty continuation page was observed.

The standard CLI adapter was unavailable because the workspace `.venv` does not contain the `astock` and `typer` runtime dependencies. Direct XeLaTeX is therefore the recorded fallback. This is author build and visual-QA evidence only: it does not replace independent R1--R4 review, execution-day validation, primary-source archive completion or publication sign-off. The execution-eligibility policy remains `not_run`; all ETF qualification states remain `q=0` until a dated current-session packet passes.
