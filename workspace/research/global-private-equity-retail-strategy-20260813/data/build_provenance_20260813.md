# Build provenance

- **Case:** `global-private-equity-retail-strategy-20260813`
- **Build:** 2026-08-14 00:39:46 CST
- **Engine:** `/usr/bin/xelatex`, XeTeX 3.141592653-2.6-0.999994 (TeX Live 2022/Debian)
- **CJK font:** Noto Serif CJK SC
- **Command:** `xelatex -interaction=nonstopmode -halt-on-error main.tex` twice, followed by `pdftotext -layout` and `pdftoppm` render inspection.
- **Source SHA-256:** `7ff1ce34b8274a6b76db510087305ed50cf74b18b10e2277129f6184e5043f8b`
- **PDF SHA-256:** `a5b8b28c8594113c35c477f7063e2f5c52a0ffb48d496f68b253e01fc9767340`
- **Pages:** 20

The usual project CLI PDF adapter could not run because the local Python environment is missing a declared dependency (`typer`). XeLaTeX itself was available and was used directly; no alternate document engine was used.
