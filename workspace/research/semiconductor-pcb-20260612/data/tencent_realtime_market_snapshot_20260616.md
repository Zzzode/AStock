# Tencent Realtime Market Snapshot
**Source:** Tencent `qt.gtimg.cn` quote feed archived at `data/raw_tencent_quote/quote_20260616.txt`.
**Timestamp:** intraday quote fields around 2026-06-16 12:55-12:56 CST.
**Purpose:** Refresh total market capitalization, PE and PB anchors after previous market-cap refresh attempts failed.
## Snapshot
| Ticker | Name | Price | Chg % | Total mcap | PE TTM | PB | Turnover | Amount | Timestamp |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 002463 | 沪电股份 | 139.03 | 3.94% | 2673.28亿元 | 62.19 | 16.90 | 3.14% | 83.31亿元 | 20260616125539 |
| 300476 | 胜宏科技 | 350.45 | 1.73% | 3032.08亿元 | 73.60 | 21.99 | 2.74% | 82.85亿元 | 20260616125539 |
| 002916 | 深南电路 | 406.04 | 1.56% | 2699.39亿元 | 76.10 | 16.81 | 1.33% | 35.69亿元 | 20260616125633 |
| 600183 | 生益科技 | 180.56 | 8.50% | 4323.51亿元 | 111.65 | 27.44 | 2.57% | 110.69亿元 | 20260616125606 |
| 603186 | 华正新材 | 206.06 | 10.00% | 323.08亿元 | 111.70 | 13.92 | 3.29% | 10.49亿元 | 20260616125606 |
| 688519 | 南亚新材 | 358.00 | 5.82% | 841.95亿元 | 227.96 | 29.90 | 2.18% | 17.62亿元 | 20260616125616 |
| 002436 | 兴森科技 | 43.18 | 7.71% | 655.44亿元 | 508.54 | 13.88 | 8.13% | 52.63亿元 | 20260616125542 |
| 301200 | 大族数控 | 324.55 | 6.62% | 1380.11亿元 | 154.02 | 14.41 | 1.07% | 14.72亿元 | 20260616125624 |
| 688630 | 芯碁微装 | 458.22 | 4.57% | 603.66亿元 | 174.24 | 25.95 | 2.66% | 15.83亿元 | 20260616125612 |
| 300400 | 劲拓股份 | 43.73 | 1.20% | 105.75亿元 | 125.09 | 15.01 | 5.91% | 6.16亿元 | 20260616125630 |
| 301377 | 鼎泰高科 | 544.38 | -1.66% | 538.18亿元 | 360.29 | 82.63 | 3.77% | 20.45亿元 | 20260616125627 |
| 002938 | 鹏鼎控股 | 107.77 | 2.99% | 2488.82亿元 | 67.28 | 7.73 | 1.31% | 32.25亿元 | 20260616125612 |

## Field Treatment

- Total market capitalization uses Tencent field 44 and is cross-checked against price times share-count scale from the same feed.
- PE uses field 39 and PB uses field 46.
- Tencent field 45 is archived as `secondary_market_cap_raw_cny_100m`, but not used in the report because it is not stable enough across A-share share-class contexts.
- This is an intraday public quote snapshot, not an audited closing valuation database and not a replacement for Wind/Choice standardized valuation history.
