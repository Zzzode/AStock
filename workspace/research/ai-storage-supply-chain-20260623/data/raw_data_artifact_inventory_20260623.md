# Raw Data Artifact Inventory

**Run date:** 2026-06-23

**Purpose:** Account for every PRIMARY raw-level capture supporting summarized evidence packets (top-level `data/` raw files + broker catalog draft).

| Metric | Value |
|---|---:|
| Raw data files (declared) | 4 |
| Present | 4 |
| Missing | 0 |
| `md` files | 3 |
| `json` files | 1 |

## Inventory

| Path | Level | Note | Type | Size bytes | SHA-256 |
|---|---|---|---|---:|---|
| `data/raw_financials.md` | L3 | L3 卖方一致预期解析 + 原始财务抓取摘要 | `md` | 42882 | `2de74e59bac52a1d6dc50b490c301729d1e78f9019a722d5d8765040e1c371e0` |
| `data/report_catalog.md` | L3 | L3 卖方研报目录 + 摘要清单 | `md` | 12857 | `79dc74feda93a89c152805a077e436476af3c47bf84967ff764839eef926cbbb` |
| `data/consensus_analysis_raw.md` | L5 | L5 机构一致预期聚合原始数据 | `md` | 16981 | `fb5eed5705e27b9ae3d85d6eba28c83d36ecd19afb021798b96c064deb66231c` |
| `sources/broker-reports/2026-06-23/_catalog_draft.json` | L3 | L3 卖方研报捕获目录草稿 | `json` | 38799 | `3dbd263ee639913289448d1638bbbf8173c5841bb354ca439a40812568ed9de9` |
