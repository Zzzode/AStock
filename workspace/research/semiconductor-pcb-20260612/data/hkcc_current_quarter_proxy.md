# HKCC Current Quarter Proxy

**Source:** Official 2026Q1 reports archived in `workspace/reports/semiconductor-pcb-q1-official-20260615/`.

**Purpose:** Use Hong Kong Securities Clearing Company (香港中央结算有限公司, HKCC) in official top-shareholder tables as a current-quarter public proxy for Stock Connect/northbound ownership. This is not beneficial-owner or institution-level northbound data.

| Ticker | Name | HKCC holding | Reported ratio | Source pointer |
|---|---|---:|---:|---|
| 002463 | 沪电股份 | 19388.13万股 | 10.08% | Q1 filing lines 149/173 |
| 300476 | 胜宏科技 | 2494.67万股 | N/A extracted row wrap | Q1 filing lines 220/264 |
| 002916 | 深南电路 | 2557.74万股 | 3.75% | Q1 filing lines 229/266 |
| 600183 | 生益科技 | 15102.36万股 | 6.22% | Q1 filing lines 154/196 |
| 603186 | 华正新材 | 443.98万股 | 2.83% | Q1 filing lines 191/231 |
| 002436 | 兴森科技 | 2774.46万股 | 1.63% | Q1 filing lines 219/245 |
| 300400 | 劲拓股份 | 244.54万股 | 1.01% | Q1 filing lines 170/187 |
| 301377 | 鼎泰高科 | 585.79万股 | 1.43% | Q1 filing lines 179/206 |
| 688630 | 芯碁微装 | 538.19万股 | N/A extracted row wrap | Q1 filing lines 210/252 |
| 688519 | 南亚新材 | not found in quick grep | N/A | Q1 filing holder table did not show HKCC in quick grep |
| 301200 | 大族数控 | 437.56万股 | N/A extracted row wrap | Q1 filing lines 241/286 |

## Interpretation

- HKCC current-quarter holder rows are available for all five core names and most watchlist names.
- This improves current-quarter northbound proxy evidence beyond the historical Stock Connect series that stops on 2024-08-16.
- HKCC is a nominee/clearing holder and does not identify beneficial owners, broker custodians, active/passive funds or daily changes.
