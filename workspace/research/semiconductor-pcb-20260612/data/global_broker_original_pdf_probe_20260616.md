# Global Broker Original PDF Probe Evidence

**Directory:** `workspace/reports/semiconductor-pcb-global-broker-probe-20260616/`

**Purpose:** Re-tested whether public web search can close the missing UBS / JPMorgan / Goldman original-report gap. Exact-title and filetype queries were run for the previously identified Goldman-Hudian, JPMorgan-Shenghong, Goldman-Shengyi and UBS-Pengding report references.

## Result

No original UBS, JPMorgan or Goldman PDF was found in this pass. Six valid public PDFs were archived and text-extracted as supplemental original-source evidence.

| Ticker / scope | Source | Title | Pages | Incremental evidence | Boundary |
|---|---|---|---:|---|---|
| 002463 | 东吴证券 | 沪电股份：赴港递表加速全球化，谷歌TPU放量迎量价齐升 | 3 | Adds Google TPU chain framing, H-share filing/capacity expansion discussion and 2025E-2027E revenue/net-profit/EPS forecast. | Not Goldman original PDF. |
| 300476 | 华金证券 | 胜宏科技：聚焦AI服务器高端产品需求，业绩增长动能强劲 | 7 | Adds AI data-center revenue-share language, HDI/high-layer capability, Vietnam/Thailand project revenue assumptions and 2025E-2027E forecasts. | Not JPMorgan original PDF. |
| Industry | 东吴证券 | AI驱动PCB全面升级：材料、工艺与架构革新引领产业新周期 | 60 | Adds full sector technology framework: M9/PTFE, HVLP copper foil, mSAP/SAP, CoWoP, midplane, orthogonal backplane and company mapping. | Domestic broker sector PDF, not global-broker original. |
| 002938 | 华泰证券 | 鹏鼎控股：卡位AI端侧浪潮，加快算力硬板投入 | 8 | Adds Pengding target price, 2025E-2027E EPS and server/optical-module certification/capacity evidence. | Not UBS original PDF. |
| 002938 | 国海证券 | 鹏鼎控股：AI端侧浪潮开启在即，PCB龙头显著受益 | 50 | Adds a full 50-page original PDF for Pengding with end-side AI, automotive/server expansion, Thailand server/automotive capacity, 2024E-2026E revenue/NPP/EPS forecast and buy rating. | Not UBS original PDF; older 2025-03 report and mainly end-side AI / broad server layout, not named Rubin/NVIDIA revenue split. |
| 002938 | HKEX filing excerpt | Business Overview | 43 | Adds filing-style Frost & Sullivan evidence on AI/HPC PCB market position, 24-layer/28-layer HDI and 100+ layer MLPCB capability. | Draft filing excerpt, not sell-side report. |

## Failed original global-broker probes added after rebuild

| Target missing source | Public URL probed | Local archive | Result |
|---|---|---|---|
| JPMorgan / Shenghong 2476.HK 2026-06-08 | `http://m.hibor.com.cn/wap_detail.aspx?id=5123096` | `workspace/reports/semiconductor-pcb-global-broker-probe-20260616/jpm-shenghong-probe/hibor-5123096.html` | Returned Hibor intelligent terminal download page (`慧博智能策略终端_下载`), with no report body or PDF link. |
| Goldman / Hudian 002463 2026-05-10 | `http://m.hibor.com.cn/wap_detail.aspx?id=db73893e91c90fd2ba6982293ef4feb2` | `workspace/reports/semiconductor-pcb-global-broker-probe-20260616/goldman-hudian-probe/hibor-db73893e91c90fd2ba6982293ef4feb2.html` | Returned Hibor intelligent terminal download page, with no report body or PDF link. |
| Goldman / Shengyi 600183 2026-05-22 | Sina visible repost URL | `workspace/reports/semiconductor-pcb-global-broker-probe-20260616/goldman-shengyi-probe/sina-goldman-shengyi-20260522.html` | Visible repost text only; not original Goldman PDF and no downloadable original report found. |

## Treatment

- Use as supplemental Q2 broker-stated or filing evidence where the text directly supports a claim.
- Do not use these files as replacements for the missing original UBS / JPMorgan / Goldman PDFs.
- Do not use named customer/platform claims as confirmed customer-revenue split unless a filing, official IR transcript, original broker PDF with full context, or customer/supplier disclosure gives the revenue amount.
