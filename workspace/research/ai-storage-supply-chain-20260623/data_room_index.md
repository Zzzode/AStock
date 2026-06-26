# Data Room Index

**Case:** `ai-storage-supply-chain-20260623`
**Run date:** 2026-06-26
**Purpose:** Current artifact inventory after AI-storage full valuation update and source refresh.

## Current Decision State

- Report state: `full_valuation_update`
- Reader-facing action: `组合低配；覆盖标的中性/减持`
- Weighted base upside on 2026-06-26 close: `-17.0%`
- Current valuation source of truth: `data/current_valuation_model_20260626.json`
- Current source registry record count: `40`

## Key File Index

| Path | Exists | Purpose | Size (bytes) |
|---|---:|---|---:|
| `workspace/research/ai-storage-supply-chain-20260623/data_room_index.md` | True | This data-room index | 4101 |
| `workspace/research/ai-storage-supply-chain-20260623/main.tex` | True | Deliverable LaTeX source | 8573 |
| `workspace/research/ai-storage-supply-chain-20260623/main.pdf` | True | Full valuation PDF | 865857 |
| `workspace/research/ai-storage-supply-chain-20260623/main_current_text.txt` | True | Current pdftotext mirror from rebuilt PDF | 141089 |
| `workspace/research/ai-storage-supply-chain-20260623/visual_review.md` | True | Visual review for full-valuation PDF | 1623 |
| `workspace/research/ai-storage-supply-chain-20260623/data/source_registry.md` | True | Rebuilt source registry | 8843 |
| `workspace/research/ai-storage-supply-chain-20260623/data/source_registry.json` | True | Machine-readable source registry | 29895 |
| `workspace/research/ai-storage-supply-chain-20260623/data/claim_audit.md` | True | Rebuilt claim audit | 3909 |
| `workspace/research/ai-storage-supply-chain-20260623/analysis/valuation_audit.md` | True | Current valuation audit | 1630 |
| `workspace/research/ai-storage-supply-chain-20260623/data/raw_market_data_20260626.json` | True | Tencent/Sina/THS market data packet | 16602 |
| `workspace/research/ai-storage-supply-chain-20260623/data/current_valuation_model_20260626.json` | True | 11-name full valuation model | 16161 |
| `workspace/research/ai-storage-supply-chain-20260623/data/source_capture_manifest_20260626.json` | True | Industry-source capture/probe manifest | 10528 |
| `workspace/research/ai-storage-supply-chain-20260623/completion_audit_manifest.json` | True | Completion manifest | 1888 |
| `workspace/research/ai-storage-supply-chain-20260623/completion_audit_manifest.md` | True | Completion manifest summary | 1165 |

## Directory Roll-up

| Directory | File count | Notes |
|---|---:|---|
| `workspace/research/ai-storage-supply-chain-20260623/sections/` | 12 | ch01/ch02/ch07/ch08/ch09/ch10/ch11/app aligned to full valuation |
| `workspace/research/ai-storage-supply-chain-20260623/analysis/` | 7 | Includes current valuation audit and model notes |
| `workspace/research/ai-storage-supply-chain-20260623/data/` | 168 | Includes market, valuation, source manifest, registry, claim audit, and checksum packets |
| `workspace/research/ai-storage-supply-chain-20260623/sources/` | 41 | Broker archive plus 2026-06-26 source refresh and market captures |
| `workspace/research/ai-storage-supply-chain-20260623/sources/industry-refresh-20260626/` | 23 | NVIDIA, BIS/eCFR, TrendForce, WSTS/SIA, SEMI/Gartner/Yole probes, Samsung, SK Hynix, Micron |
| `workspace/research/ai-storage-supply-chain-20260623/sources/market-data-20260626/` | 3 | Tencent, Sina, THS captures |
| `workspace/research/ai-storage-supply-chain-20260623/rendered/` | 106 | Full-valuation render plus legacy page PNGs |
| `workspace/research/ai-storage-supply-chain-20260623/rendered/full-valuation-20260626/` | 43 | Current full-valuation visual render |
| `workspace/research/ai-storage-supply-chain-20260623/tools/` | 12 | Valuation refresh, governance rebuild, and verifier scripts |

## Verification Work

- `main.pdf` must be rebuilt with XeLaTeX after valuation text changes.
- `main_current_text.txt` must be refreshed from the rebuilt PDF.
- `rendered/full-valuation-20260626/` must be refreshed for visual review.
- `tools/verify_ai_storage.py` and `tools/verify_research_workspace.py` are the active verifier entry points.
