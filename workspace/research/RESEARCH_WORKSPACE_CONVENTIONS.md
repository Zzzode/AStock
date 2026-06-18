# Research Workspace Conventions

Canonical directory structure, file-naming, file-format, and version-control rules for research cases under `workspace/research/`. All research-producing agents (equity-research skill, data-collector, source-governance-analyst, latex-writer, internal-control, etc.) MUST follow these rules. The workspace verifier (`tools/verify_research_workspace.py`) enforces the audit-layer invariants and is the only acceptance gate.

## 1. Case layout

A research case lives at `workspace/research/<case-id>/` where `<case-id> = <topic-slug>-<YYYYMMDD>` (e.g. `semiconductor-pcb-20260612`). One self-contained case per directory.

```
<case-id>/
├── research_brief.md              # case definition: scope, tickers, objective
├── main.tex / main.pdf            # deliverable source / compiled PDF
├── main_current_text.txt          # extracted PDF text (regenerated on each rebuild)
├── sections/*.tex                 # chapter sources
├── analysis/*.md                  # human analyst output (valuation, risk, market...)
├── sources/                       # PRIMARY external evidence (non-regenerable)
├── data/                          # DERIVED/processed evidence + audit artifacts
├── rendered/                      # PDF raster snapshots (derived, large)
├── tools/                         # case-local verifier scripts
├── review_log.md                  # append-only change log
├── completion_audit_manifest.{md,json}
├── source_exhaustion_log.{md,json}
├── data_room_index.md
├── missing_data_request_pack.{md,json,csv}
├── unresolved_requirements.json
└── ...other governance files
```

## 2. Directory semantics — what is source-of-truth vs derived vs temp

| Path | Class | Track in git? | Why |
|---|---|---|---|
| `sources/` | PRIMARY non-regenerable | **YES** | Raw external captures; lost forever if deleted |
| `data/raw_*.{json,html}` | PRIMARY raw | **YES** | Original API/scrape responses |
| `data/<topic>_*.{md,json}` (proxy/summary) | DERIVED | **YES** | Reproducible but expensive; encodes analytical work |
| `data/*_{inventory,audit,checksums,manifest}*` | DERIVED index | **YES** | Governance layer; must stay internally consistent |
| `analysis/*.md` | HUMAN analyst | **YES** | Conclusions |
| `sections/*.tex`, `main.tex` | DELIVERABLE source | **YES** | The report |
| `main.pdf` | DERIVED build | **YES** | The deliverable artifact |
| `rendered/full-<ts>/*.png` | DERIVED raster | **policy, see §5** | Large; accumulates ~21 MB per rebuild |
| `rendered/current-<date>/*.png` | DERIVED exhibit | **YES** | Lightweight current-exhibit subset |
| LaTeX intermediates `*.aux .log .out .toc .fls .fdb_latexmk .synctex.gz .xdv .bcf .run.xml` | TEMP | **NO** (gitignored) | Regenerable from `main.tex` |
| `.DS_Store`, `*.swp`, `__pycache__/`, `.venv/` | TEMP | **NO** | OS / editor / env junk |

If a file is regenerable by re-running a script or rebuild, it is TEMP or DERIVED — never let it leak into the "PRIMARY" tier, and never edit it by hand.

## 3. File-naming conventions

- **Date suffix on time-bound artifacts**: `_YYYYMMDD` (e.g. `current_public_source_recheck_20260617.md`). Enables chronological ordering and de-duplication.
- **Prefix = category** inside `data/`: `raw_*` (raw capture), `<topic>_*` (e.g. `eastmoney_*`, `pengding_*`, `material_*`), `*_inventory` / `*_audit` / `*_checksums` / `*_manifest` (governance). One prefix per concern; do not mix.
- **`sources/` subdirs**: `<type>-<topic>-<YYYYMMDD>/` (e.g. `broker-core-20260615/`, `probe-customer-side-20260617/`, `official-quarterly-20260616/`). One subdir per capture batch.
- **`rendered/`**: `full-<YYYYMMDD>-<HHMM>/` for full-page raster sets; `current-<YYYYMMDD>/` for the lightweight current-exhibit set.

## 4. File-format conventions

- **Markdown + JSON pairs**: every governance/summary file has a `.md` (human-readable) and a `.json` (machine-readable) twin. They MUST stay in sync. The verifier treats `.json` as source of truth for counts/sizes; the `.md` mirrors it. After editing either, regenerate the twin in the same change.
- **Dates**: ISO `YYYY-MM-DD` in prose; filename dates are compact `YYYYMMDD`. When recording a PDF build, quote `pdfinfo CreationDate` verbatim (e.g. `Thu Jun 18 19:22:23 2026 CST`).
- **Money**: state currency + unit explicitly (`CNY4.055bn`, `USD35.674bn`, `+80.60%`). Never bare numbers.
- **Paths in JSON**: use repo-relative absolute (`workspace/research/<case>/data/foo.json`) so references resolve from repo root. In `.md` body, case-relative (`data/foo.json`) is acceptable.
- **Evidence-boundary discipline**: every proxy/derived file states plainly what it does NOT prove. Proxy evidence (public TDS, segment aggregate, OCR repost, model-derived) does NOT close hard-data blockers (product-level ASP, generation revenue/margin, complete dated certification, lead-time/shipment sequence). Keep `completion_audit_manifest.decision = do_not_mark_complete` while any blocker is unmet.

## 5. Version-control rules — keeping the repo lean

Root `.gitignore` excludes all LaTeX intermediates, OS/editor junk, Python/Node caches, venv, and the runtime workspaces (`workspace/{backtest,recommend,team}/`). Research cases under `workspace/research/` ARE tracked (long-lived value).

**`rendered/` policy (the 304 MB problem):**
- `main.pdf` is tracked — it is the deliverable.
- `rendered/full-<ts>/` PNG rasters are DERIVED from `main.pdf` and balloon ~21 MB per rebuild. Rules:
  1. Track only the **current** full render — the one `rendered_artifact_inventory.full_render_sequence_check.directory` points to.
  2. Historical `full-*` dirs: keep on disk for audit, but `git rm --cached` them so they stop inflating the repo. Prune the oldest when the on-disk count grows too large.
  3. **Byte-identical rebuilds must not spawn a new `full-<ts>/` dir.** If a rebuild produces the same page count and file size (only CreationDate changed), keep the existing current render — it remains visually accurate.
- `rendered/current-<date>/` (lightweight exhibit subset) stays tracked.

**Git hygiene:**
- Never commit `.DS_Store`, editor swap files, `__pycache__/`, or LaTeX intermediates. The pre-commit hook syncs `.agents/ → .claude/ + .codex/`; let it.
- CRLF/LF: HTML/CSV captures may arrive CRLF; git normalizes to LF on commit (warning only). Do not hand-rewrite line endings.

## 6. Audit-artifact refresh dependencies

When you change something, refresh everything that depends on it before running the verifier.

**After a PDF rebuild:**
1. Clean LaTeX intermediates (`latexmk -c`, plus remove any `*.xdv`) so root file count is restored.
2. `report_quality_eval.json/.md` → `pdf_creation_date`, `pages`, `pdf_file_size`.
3. `completion_audit_manifest.json` → `verifier_summary.pdf_creation_date`.
4. `data/core_artifact_checksums_<date>.json/.md` → recompute size+sha256 for the 14 core files (use raw `read_bytes()`).
5. `data/top_level_data_artifact_inventory_<date>.json/.md` → file sizes are **self-referential** (the inventory lists itself); iterate the recompute-write-check loop to the fixed point.
6. `data/root_artifact_inventory_<date>.json/.md` → only if a root file's size changed.
7. Run `python3 tools/verify_research_workspace.py` → must be 39 PASS / 0 FAIL.

**After editing a governance `.md` (`source_exhaustion_log`, `completion_audit_manifest`, `data_room_index`, etc.):**
1. Sync its `.json` mirror (same rows/fields).
2. Recompute `core_artifact_checksums` for the changed `.md` (and any `.json` you touched).
3. Update `top_level_data_artifact_inventory` sizes for the changed files (iterate to fixed point).
4. Update `data_room_index.md` if it references new/deleted files.
5. Run the verifier → 39/39.

## 7. The verifier is the only gate

`tools/verify_research_workspace.py` is read-only and authoritative. It checks: root/data/source/raw/rendered file counts and sizes, core checksum manifest, current render validity, completion decision, source-exhaustion consistency, md/json summary currency, PDF hygiene (no path leakage, no unfinished markers), evidence-reference integrity, blocker/request-pack alignment, ticker coverage, and PDF page/creation-date. **39 PASS / 0 FAIL is the only acceptable state after any change.** Never hand-edit the verifier to force a pass — fix the underlying artifact.
