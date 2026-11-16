# Build Provenance — 2026-08-12 Actionability Revision

- Status: **BUILT_UNREVIEWED**
- Case / scope: `stable-income-multi-asset-strategy-20260811` / `strategic-allocation-etf-first-v2-20260811`
- Timestamp: `2026-08-12T00:57:26+08:00`
- Revision: reader-facing model targets, staged actions and validation-failure fallbacks were added after the allocation-strategy actionability correction.
- Build platform: Linux 5.15.152.bsk.4-amd64 x86_64 GNU/Linux
- Build engine: XeLaTeX (`/usr/bin/xelatex`)
- TeX distribution: TeX Live 2022/Debian — `XeTeX 3.141592653-2.6-0.999994`
- CJK font: Noto Serif CJK SC and Noto Sans CJK SC; `ctexrep.cls` and `xeCJK.sty` resolved locally.
- Build command: `/usr/bin/xelatex -interaction=nonstopmode -halt-on-error main.tex` (two passes)
- Reader-source SHA-256: `ff771a67bcefc9f1c22987f3115c6caca56c4dbc3c40aa91e79969e01f031a13`
- Reader-source graph SHA-256: `d208de98baeacae25ec56fcca51b2685aa45721c7c715f7f7880a255cacf7e55`
- PDF: `main.pdf`, 18 A4 pages, SHA-256 `d485b96227d0caca0abcb79b263b7a26301ee2d4e0395cb6ad39f41227d93102`
- Extracted text: `main_current_text.txt`, SHA-256 `171c58b604fac021ffae3ecc2733319c581a9509864855bce1144e3290c2085a`
- Full render: `rendered/full-20260812-0057/`, 18 PNG pages at 150 DPI.
- Diagnostics: 0 fatal errors, 0 undefined-control-sequence errors, 0 missing-character records and 0 `Overfull \\hbox` records; PDF fonts are embedded.
- Author visual inspection: physical pages 5, 6, 9, 10 and 15 were checked for the reader-facing target/action cards, staged-allocation tables and implementation controls. No clipping, overlap or table truncation was observed.

The standard CLI adapter was unavailable because the workspace `.venv` does not contain the `astock` and `typer` runtime dependencies. The direct XeLaTeX invocation above is therefore recorded as a transparent fallback. This is author build evidence only: it does not replace independent R2/R3 review, execution-day validation or R0--R4 release closure. In particular, the CNY30,000 `512890` sleeve remains deferred until the dated combined-holdings, industry and issuer-group look-through test passes.
