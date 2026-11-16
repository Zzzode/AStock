# Broker Report Catalog — 2026-08-11

- **Scope:** 000703, 002379, 300014, 002497, 002432, 000623, 600739, 000685, 600150, 301308, 002812, 002240 and 300390.
- **Preferred directory window:** 2026-04-01 to 2026-08-11.
- **Public-directory result:** 30 visible rows across the nine tickers that returned coverage; 12 PDFs archived, representing 11 non-duplicate reports.
- **Source hierarchy:** original broker PDF > broker page/visible abstract > public directory row > no result. This catalog does not promote an abstract or a directory row into a target-price anchor.

| ID | Ticker | Broker | Date | Report | Rating | Target | Form / quality | Local archive | Valuation weight |
|---:|---|---|---|---|---|---:|---|---|---:|
| 01 | 000703 | 国信证券 | 2026-07-05 | 文莱炼化项目盈利提升，公司上半年业绩大幅增长 | 优于大市（首次） | 16.50–17.60 | original PDF / primary | `01-000703-guosen-20260705.pdf` + `.txt` | 0.10 |
| 02 | 002379 | 招银国际 | 2026-05-13 | 高盈利弹性，高分红比例；首次覆盖给予买入评级 | 买入（首次） | 29.00 | original PDF / primary | `02b-002379-cmbi-20260513.pdf` + `.txt` | 0.10 |
| 03 | 300014 | 东吴证券 | 2026-06-16 | 2026年Q2盈利韧性强劲，业绩超市场预期 | 买入（维持） | 103.00 | original PDF / primary | `03-300014-dongwu-20260616.pdf` | 0.00 |
| 04 | 300014 | 群益证券 | 2026-06-26 | 公司26H1净利润翻倍增长，储能业务加快扩张，建议“买进” | 买进 | 77.00 | original PDF / primary | `04-300014-qunyi-20260626.pdf` + `.txt` | 0.05 |
| 05 | 002497 | 东吴证券 | 2026-07-08 | 26H1业绩预告点评：Q2锂盐量利齐升，略超我们预期 | 买入（维持） | 42.00 | original PDF / primary | `05-002497-dongwu-20260708.pdf` + `.txt` | 0.10 |
| 06 | 000685 | 国信证券 | 2026-05-11 | 投资收益带动业绩高增，“公用事业+资本+科技”三大板块引领未来发展 | 优于大市（维持） | not disclosed | original PDF / primary | `06-000685-guosen-20260511.pdf` + `.txt` | 0.00 |
| 07 | 600150 | 华源证券 | 2026-07-14 | 26H1预告点评：Q2业绩预计同比大增，关注后续船价与集团整合 | 买入（维持） | not disclosed | original PDF / primary | `07-600150-huayuan-20260714.pdf` + `.txt` | 0.00 |
| 08 | 301308 | 爱建证券 | 2026-05-07 | 2025年报&2026Q1点评：国产存储模组龙头进入业绩爆发期 | 买入（维持） | not disclosed | original PDF / primary | `08-301308-aijian-20260507.pdf` + `.txt` | 0.00 |
| 09 | 002812 | 东吴证券 | 2026-07-10 | 26H1业绩预告点评：Q2业绩超我们预期，隔膜供需紧张盈利持续提升 | 买入（维持） | 103.00 | original PDF / primary | `09-002812-dongwu-20260710.pdf` + `.txt` | 0.10 |
| 10 | 002240 | 东吴证券 | 2026-07-09 | 26H1业绩预告点评：Q2锂盐出货高增，自有矿贡献利润 | 买入（维持） | not disclosed | original PDF / primary | `10-002240-dongwu-20260709.pdf` + `.txt` | 0.00 |
| 11 | 300390 | 华源证券 | 2026-06-06 | 氢氧化锂龙头，深度绑定大客户，锂资源加速布局 | 买入（首次） | not disclosed | original PDF / primary | `11-300390-huayuan-20260606.pdf` + `.txt` | 0.00 |

The English CMBI version of report 02 is also archived as `02-002379-cmbi-20260512.pdf`; it is the same initiation view, so it is not counted as independent coverage.

## Source traceability

All direct report pages use `https://data.eastmoney.com/report/info/<infoCode>.html`; exact page and direct-PDF URLs, report forecasts, quality flags, local paths and gaps are retained per row in [broker_street_consensus_20260811.json](broker_street_consensus_20260811.json).

Raw public-directory responses are retained at `sources/probe-20260811/eastmoney_report_list_<ticker>_20260401_20260811.json` for every universe member. The 002432, 000623 and 600739 response files contain an empty `data` array; their normalized catalog rows are explicit `not_found` / zero-weight entries rather than omissions.

## Consensus snapshot

- **Current explicit targets with original PDFs:** 000703 CNY16.50–17.60; 002379 CNY29.00; 300014 CNY77.00 and CNY103.00; 002497 CNY42.00; 002812 CNY103.00.
- **Target-quality warning:** no average target price is calculated. In particular, the two 300014 targets use different profit assumptions and the Qunyi report does not disclose a target derivation.
- **Ratings in normalized original-PDF sample:** ten Buy/Outperform-type ratings and one `买进`; no current neutral or sell rating found in the downloaded sample. This is coverage selection, not a conclusion about the whole Street.
- **Forecast-only / zero target weight:** 000685, 600150, 301308, 002240 and 300390.
- **Public-corpus gap / zero target weight:** 002432, 000623 and 600739.
