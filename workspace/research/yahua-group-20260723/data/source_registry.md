# Source registry — 雅化集团（002497.SZ）

**Hierarchy:** L1 = issuer / exchange / government primary evidence; L2 = complete attributable broker document or auditable market-data/aggregation snapshot; L3 = independent price or media/industry information. An L3 fact may frame a scenario, but cannot create positive company-specific EPS, multiple or target-price credit.

| ID | Source | Date / as-of | Tier | Approved use | Critical limitation |
|---|---|---|---|---|---|
| FIN-23A | 雅化 2023 annual report | 2024-04-26 | L1 audited | Historical P&L, CFO, balance sheet | Historical only. |
| FIN-24A | 雅化 2024 annual report | 2025-04-29 | L1 audited | Historical P&L, CFO, balance sheet | Historical only. |
| FIN-25A | 雅化 2025 annual report | 2026-04-27 | L1 audited | Segment base, cash conversion, capacity, resources, customers and risks | No 2026 unit economics, self-supply ratio or named-customer revenue. |
| FIN-26Q1 | 雅化 2026Q1 report | 2026-04-27 | L1 unaudited | Latest reported revenue, profit, CFO and balance sheet | One quarter; cannot annualize. |
| FIN-26H1P | 雅化 2026H1 preview | 2026-07-07 | L1 preliminary | H1/Q2 attributable-profit constraint and management direction | No revenue, segment P&L, cash flow or unit inputs. |
| DISC-CNINFO-H1 | CNINFO announcement query response | captured 2026-07-23 | L1 official catalogue | Confirms 7 July preview listing and no formal H1 report in query range | `00:00:00` is date-normalized metadata, not an intraday release time. |
| SHARE-26 | 2025 distribution implementation notice | 2026-06-13 | L1 primary | Total-share count cross-check | Does not supply market price. |
| MKT-YH-Q-0723 | Eastmoney 雅化 quote snapshot | 2026-07-23 close | L2 market snapshot | Current close, turnover, market cap cross-check | No provider timestamp / exchange daily file. |
| MKT-EVT-0723 | Eastmoney 雅化/peer/CSI daily bars | 2026-07-06 to 2026-07-23 | L2 market snapshot | Relative-return and liquidity context | No event causation, factor model or flow data. |
| IR-25 | 雅化 investor-relations record | 2025-09-12 | L1 primary | Sulfide-lithium and resource evidence boundary | Management communication; no order/revenue proof. |
| POL-25 | MIIT civil-explosives policy | 2025-02-28 | L1 government | Regulatory direction | No company share/order/read-through. |
| PEER-TQ-Q1 | 天齐 2026Q1 report | 2026-04-28 | L1 primary | Sector beta / peer Q1 evidence | SQM investment income impairs clean comparability. |
| PEER-GF-P | 赣锋 2026Q1 preview | 2026-04-17 | L1 preliminary | Sector beta direction | Preview; PLS fair-value effects. |
| PEER-SX-Q1 | 盛新 2026Q1 report | 2026-04-30 | L1 primary | Sector beta direction | Indonesia and product mix differ. |
| PEER-EST-TQ/GF/SX | Eastmoney peer forecast snapshots | captured 2026-07-23 | L2 aggregation | Relative P/E calibration only | Secondary aggregation; 20% combined-house-calibration cap. |
| PRICE-SMM-25D / PRICE-CNMN-26J / PRICE-SMM-26H1 | Lithium spot/review material | 2025-12-31 to 2026-07-10 | L3 | Scenario direction/range | Not 雅化 realized ASP, not a target-price input. |
| DEMAND-CAAM-26H1 | CAAM data reported by People.cn | 2026-07-09 | L2 secondary government-data report | Terminal-demand context | Not lithium purchasing or company orders. |
| MINEPOL-MIIT-25 | MIIT mining-explosives safety notice | 2025-04-30 | L2 government page | Regulatory constraint | Not demand or earnings evidence. |
| BRK-DW-26 | 东吴 26H1 preview comment | 2026-07-07 | L2 complete broker PDF | External forecast / one target sanity-check | Single analyst; max 10% forecast and 15% TP anchor. |
| BRK-GX-26 | 国信 2025AR/26Q1 review | 2026-04-30 | L2 complete broker PDF | External forecast reconciliation | No target/method disclosed; max 5% forecast reconciliation. |
| BRK-KY-26 | 开源 2025AR/26Q1 update | 2026-04-29 | L2 complete broker PDF | External forecast/revision reconciliation | No target/method disclosed; max 5% forecast reconciliation. |
| METH-CS-26 | 中国船舶 full-note artefacts | 2026-07-22 | Internal methodology only | Report-process reference | No transfer of Yahua facts, forecasts or valuation. |

Every source’s local path, original URL and SHA-256 are recorded in its corresponding `sources/*/capture_manifest.md`, `sources/*/source_manifest.md`, or broker `index.md`. `data/source_registry.json` is the machine-readable counterpart.
