# Superseded Build Provenance — 2026-08-12 00:10

- Status: **SUPERSEDED** by `data/build_provenance_20260812_actionability.{md,json}` after the reader-facing model-portfolio actionability revision.
- Case / scope: `stable-income-multi-asset-strategy-20260811` / `strategic-allocation-etf-first-v2-20260811`
- Timestamp: `2026-08-12T00:10:36+08:00`
- Build platform: Linux 5.15.152.bsk.4-amd64 x86_64 GNU/Linux
- Build engine: XeLaTeX (`/usr/bin/xelatex`)
- TeX distribution: TeX Live 2022/Debian — `XeTeX 3.141592653-2.6-0.999994`
- CJK font: Noto Serif CJK SC and Noto Sans CJK SC; `ctexrep.cls` and `xeCJK.sty` resolved locally.
- Build command: `/usr/bin/xelatex -interaction=nonstopmode -halt-on-error main.tex` (two passes)
- Reader-source SHA-256: `cf5d712284859b46340069d61d216f5a6c58b5cfe1ffbe419be0bf157a742ceb`
- Reader-source graph SHA-256: `c2c05f87c4a51ce7caacc5eb6ee48036640283077660d317a39be5fe6a9f37ed`
- Archived PDF: `rendered/superseded-20260812-0010/main.pdf`, 18 A4 pages, SHA-256 `f6c9318abd5672515e0be4a34da2ccefc60294687ab336f0ae39608356bf1cf3`
- Extracted text checksum: `258a45b24198db927e740fb25e6df9fc624651379c35e468acd337af25aa6d61` (the superseded text extraction was replaced by the current build).
- Archived full render: `rendered/superseded-20260812-0010/pages/`, 18 PNG pages at 150 DPI.
- Diagnostics: 0 fatal errors, 0 undefined-control-sequence errors, 0 missing-character records and 0 `Overfull \\hbox` records; PDF fonts are embedded.

The standard CLI adapter was unavailable because the workspace `.venv` does not contain the `astock` and `typer` runtime dependencies. The direct XeLaTeX invocation above is therefore recorded as a transparent fallback. This is an author build record only. It is retained for history, not as the active source/PDF identity; independent R3 review and the remaining R0--R4 release conditions are still open.
