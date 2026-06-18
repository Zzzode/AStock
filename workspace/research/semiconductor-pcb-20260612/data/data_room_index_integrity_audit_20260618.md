# Data Room Index Integrity Audit

**Run date:** 2026-06-18

**Purpose:** Validate data-room index rows, artifact inventories, current full-render coverage and checksum manifest after the report rebuild.

| Check | Value |
|---|---:|
| Exists Rows Checked | 277 |
| Mismatches | 0 |
| Top Level Report Artifacts Checked | 18 |
| Top Level Data Files Checked | 368 |
| Source Files Checked | 634 |
| Rendered Files Checked | 1144 |
| Raw Data Files Checked | 358 |
| Source Directory Count Mismatches | 0 |
| Top Level Data Files Missing From Inventory | 0 |
| Source Files Missing From Inventory | 0 |
| Source Inventory Extra Files | 0 |
| Source Inventory Size Mismatches | 0 |

## Additional Gates

- Current full render is checked by `tools/verify_research_workspace.py` against `data/rendered_artifact_inventory_20260618.json`.
- Inventory mismatch fields and `mismatch_details` are checked by `tools/verify_research_workspace.py` against `data/data_room_index_integrity_audit_20260618.json`.
- Core artifact checksums and checksum Markdown alignment are checked by `tools/verify_research_workspace.py` against `data/core_artifact_checksums_20260618.json` and `data/core_artifact_checksums_20260618.md`.
- Request-pack CSV/JSON mirroring and required source-registry/template handoff terms are checked by `tools/verify_research_workspace.py`.
- Ticker coverage matrix alignment, audit Markdown summaries, consistency Markdown summaries and customer recheck Markdown summaries are checked by `tools/verify_research_workspace.py`.

## Mismatch Details

No mismatches found.

## Boundary

File and directory inventory integrity only; not substantive completion of non-public data requirements.
