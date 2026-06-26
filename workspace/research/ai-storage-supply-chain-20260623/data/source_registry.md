# Source Registry - AI Storage Full Valuation - 2026-06-26

- **Status**: `PUBLISH_FULL_CURRENT_PRICE_VALUATION`
- **Decision**: current AStock target prices, valuation ranges, upside/downside, and ratings are published from the rebuilt model.
- **Current source of truth**: `data/current_valuation_model_20260626.json`
- **Admission rule**: current model claims require original URL or archived file, capture timestamp, hash/stable identity, and claim-audit boundary. Probe-only sources cannot support quantitative valuation.

## Summary

| Use boundary | Count |
|---|---:|
| `consensus_context_only` | 14 |
| `current_model_industry_evidence` | 18 |
| `current_model_input` | 3 |
| `failed_probe_only` | 1 |
| `probe_only` | 4 |
| **Total records** | **40** |

## Current Registry

| SID | Group | Status | Archive | SHA-256[:12] | Valuation boundary |
|---|---|---|---|---|---|
| MKT-001 | Market data valuation | captured | `sources/market-data-20260626/tencent_quote_20260626.txt` | `552d0057744f` | `current_model_input` |
| MKT-002 | Market data valuation | captured | `sources/market-data-20260626/sina_quote_20260626.txt` | `72eb4782b108` | `current_model_input` |
| MKT-003 | Market data valuation | captured | `sources/market-data-20260626/ths_profit_forecast_20260626.json` | `4ae0f900cfe4` | `current_model_input` |
| IND-001 | BIS / Federal Register | captured | `sources/industry-refresh-20260626/bis_federal_register_2024_28270.html` | `9a84e4a98b7e` | `current_model_industry_evidence` |
| IND-002 | BIS / Federal Register | captured | `sources/industry-refresh-20260626/bis_federal_register_2024_28270.pdf` | `9c9ea7f0655e` | `current_model_industry_evidence` |
| IND-003 | BIS / Federal Register | captured | `sources/industry-refresh-20260626/bis_federal_register_2025_02655.html` | `29314f1744c4` | `current_model_industry_evidence` |
| IND-004 | eCFR | captured | `sources/industry-refresh-20260626/ecfr_ear_774_supplement_1.html` | `4e3bbf62829b` | `current_model_industry_evidence` |
| IND-005 | NVIDIA | captured | `sources/industry-refresh-20260626/nvidia_vera_rubin_nvl72.html` | `32e03c186820` | `current_model_industry_evidence` |
| IND-006 | NVIDIA | captured | `sources/industry-refresh-20260626/nvidia_hgx_vera_rubin.html` | `d958f0ac60c5` | `current_model_industry_evidence` |
| IND-007 | TrendForce / DRAMeXchange | captured | `sources/industry-refresh-20260626/trendforce_dram_price.html` | `c7b7a9fd2120` | `current_model_industry_evidence` |
| IND-008 | TrendForce / DRAMeXchange | captured | `sources/industry-refresh-20260626/trendforce_flash_price.html` | `1db4b651218b` | `current_model_industry_evidence` |
| IND-009 | TrendForce / DRAMeXchange | captured | `sources/industry-refresh-20260626/trendforce_vera_rubin_800v_20260625.html` | `837bc17180d4` | `current_model_industry_evidence` |
| IND-010 | TrendForce / DRAMeXchange | captured | `sources/industry-refresh-20260626/trendforce_20260601_13070.html` | `00455d92712e` | `current_model_industry_evidence` |
| IND-011 | Gartner | http_error_captured | `sources/industry-refresh-20260626/gartner_semiconductor_forecast_20260408.html` | `76461cd0eb6d` | `probe_only` |
| IND-012 | WSTS | captured | `sources/industry-refresh-20260626/wsts_recent_news_release.html` | `135950e53625` | `current_model_industry_evidence` |
| IND-013 | SIA | captured | `sources/industry-refresh-20260626/sia_april_2026_sales.html` | `d89c67e83dbe` | `current_model_industry_evidence` |
| IND-014 | SEMI | http_error_captured | `sources/industry-refresh-20260626/semi_300mm_fab_spending_20260401.html` | `cb33f5cf72c6` | `probe_only` |
| IND-015 | SEMI | http_error_captured | `sources/industry-refresh-20260626/semi_equipment_sales_record_2027.html` | `045718e36512` | `probe_only` |
| IND-016 | Yole | http_error_captured | `sources/industry-refresh-20260626/yole_next_gen_dram_2026.html` | `7f318ab8d9b9` | `probe_only` |
| IND-017 | SK Hynix IR | captured | `sources/industry-refresh-20260626/skhynix_hbm4_development.html` | `6a002f8f978d` | `current_model_industry_evidence` |
| IND-018 | SK Hynix IR | captured | `sources/industry-refresh-20260626/skhynix_q1_2026_results.html` | `b01eac310da7` | `current_model_industry_evidence` |
| IND-019 | Micron IR | captured | `sources/industry-refresh-20260626/micron_hbm4_vera_rubin.html` | `9b1a254d56ca` | `current_model_industry_evidence` |
| IND-020 | Micron IR | captured | `sources/industry-refresh-20260626/micron_hbm4_vera_rubin.pdf` | `e97cc8b12af9` | `current_model_industry_evidence` |
| IND-021 | Samsung IR | captured | `sources/industry-refresh-20260626/samsung_hbm4e_gtc_2026.html` | `afd34f1ff5e9` | `current_model_industry_evidence` |
| IND-022 | Samsung IR | captured | `sources/industry-refresh-20260626/samsung_q1_2026_results.html` | `e845ea40fe93` | `current_model_industry_evidence` |
| IND-023 | CXL Consortium probe | failed | `sources/industry-refresh-20260626/cxl_4_0_release_businesswire.html` | `fcb1faaf29b3` | `failed_probe_only` |
| BRK-001 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-20_东海证券_澜起科技_公司深度报告_全球互连芯片龙头厂商_聚焦“运力”构建AI战略.pdf` | `dc1cc77d423c` | `consensus_context_only` |
| BRK-002 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-11_开源证券_澜起科技_公司深度报告_内存互连全球龙头_发力AI运力打造第二增长中枢.pdf` | `5f1b303907f3` | `consensus_context_only` |
| BRK-003 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-04-15_国元证券_澜起科技_2025年年报点评_产品结构升级改善盈利能力_运力芯片增强业.pdf` | `afbffe3dc3c3` | `consensus_context_only` |
| BRK-004 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-27_中邮证券_兆易创新_全芯赋能_智创未来.pdf` | `f18a6b0f2683` | `consensus_context_only` |
| BRK-005 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-18_中航证券_兆易创新_存储量价齐升空间打开_定制化存储进程加速.pdf` | `f19a2532a3a3` | `consensus_context_only` |
| BRK-006 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-07_国信证券_江波龙_1Q26归母净利润同比增长2644_05%_端侧应用多维拓展.pdf` | `d0dba97bd85a` | `consensus_context_only` |
| BRK-007 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-07_爱建证券_江波龙_2025年报&2026Q1点评_国产存储模组龙头进入业绩爆发.pdf` | `38d0e62f2f4c` | `consensus_context_only` |
| BRK-008 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-12_华鑫证券_长电科技_公司事件点评报告_盈利能力复苏_先进封装龙头受益于AI算力强.pdf` | `756c1bd5bd03` | `consensus_context_only` |
| BRK-009 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-07_华源证券_长电科技_盈利水平持续提升_产品升级与研发扩产双轮驱动.pdf` | `442143b8bec1` | `consensus_context_only` |
| BRK-010 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-04-21_东吴证券_北方华创_2025年报点评_营收稳步增长_平台化布局加速推进.pdf` | `ef2bb7a84643` | `consensus_context_only` |
| BRK-011 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-05-02_东吴证券_北方华创_2026一季报点评_营收稳步增长_平台化布局加速推进.pdf` | `351b48fc5c34` | `consensus_context_only` |
| BRK-012 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-04-20_开源证券_北方华创_公司信息更新报告_营收实现稳健增长_前瞻投入研发布局行业上行.pdf` | `b659d1690bb4` | `consensus_context_only` |
| BRK-013 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-06-22_国元证券_行业_半导体与半导体生产设备行业周报_英伟达Rubin开始量产交付.pdf` | `b551e1e3818c` | `consensus_context_only` |
| BRK-014 | Legacy broker report | captured | `sources/broker-reports/2026-06-23/2026-06-22_爱建证券_行业_电子行业周报_SK_Hynix送样12层HBM4E_AI高端.pdf` | `126f3e06bd61` | `consensus_context_only` |

## Use Boundaries

- `current_model_input`: can enter current price, market-cap, share-count, EPS, target-price, upside, and rating calculations with public-proxy disclosure.
- `current_model_industry_evidence`: can support industry, policy, HBM4, CXL, cycle, and stress-test assumptions after claim-level mapping.
- `consensus_context_only`: broker reports can explain consensus divergence; broker ratings are not copied into AStock final ratings.
- `probe_only` / `failed_probe_only`: access evidence only; cannot enter quantitative valuation.
