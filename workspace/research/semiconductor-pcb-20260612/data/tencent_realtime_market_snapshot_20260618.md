# Tencent Latest Market Snapshot

**Source:** Tencent `qt.gtimg.cn` quote feed archived at `data/raw_tencent_quote/quote_20260618.txt`.
**Fetch date:** 2026-06-18 CST.
**Embedded quote timestamp:** latest returned Tencent fields are around 2026-06-17 16:14 CST.
**Purpose:** Refresh total market capitalization, PE and PB anchors after the previous 2026-06-16 snapshot.

## Snapshot

| Ticker | Name | Price | Chg % | Total mcap | PE TTM | PB | Turnover | Amount | Timestamp |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 002463 | 沪电股份 | 146.55 | 4.20% | 2817.88亿元 | 65.56 | 17.82 | 5.16% | 144.61亿元 | 20260617161436 |
| 300476 | 胜宏科技 | 361.70 | 1.75% | 3129.41亿元 | 75.96 | 22.69 | 5.14% | 160.01亿元 | 20260617161418 |
| 002916 | 深南电路 | 444.27 | 10.00% | 2953.55亿元 | 83.26 | 18.39 | 1.81% | 51.95亿元 | 20260617161445 |
| 600183 | 生益科技 | 180.15 | 0.42% | 4313.69亿元 | 111.39 | 27.38 | 4.83% | 212.44亿元 | 20260617161404 |
| 603186 | 华正新材 | 226.67 | 10.00% | 355.40亿元 | 122.88 | 15.31 | 10.23% | 36.03亿元 | 20260617161411 |
| 688519 | 南亚新材 | 395.01 | 10.82% | 928.99亿元 | 251.53 | 32.99 | 3.48% | 31.83亿元 | 20260617161451 |
| 002436 | 兴森科技 | 47.80 | 8.39% | 725.57亿元 | 562.95 | 15.37 | 17.00% | 122.38亿元 | 20260617161418 |
| 301200 | 大族数控 | 328.08 | 0.64% | 1395.12亿元 | 155.70 | 14.57 | 1.27% | 17.67亿元 | 20260617161445 |
| 688630 | 芯碁微装 | 475.77 | 2.58% | 626.78亿元 | 180.91 | 26.94 | 4.57% | 28.62亿元 | 20260617161449 |
| 300400 | 劲拓股份 | 43.61 | -2.76% | 105.46亿元 | 124.75 | 14.97 | 8.56% | 9.06亿元 | 20260617161421 |
| 301377 | 鼎泰高科 | 590.00 | 6.58% | 583.28亿元 | 390.48 | 89.55 | 5.62% | 31.56亿元 | 20260617161457 |
| 002938 | 鹏鼎控股 | 119.01 | 10.00% | 2748.40亿元 | 74.29 | 8.53 | 2.79% | 74.49亿元 | 20260617161439 |

## Field Treatment

- Total market capitalization uses Tencent field 44 and is cross-checked against price times share-count scale from the same feed.
- PE uses field 39 and PB uses field 46.
- Tencent field 45 is archived as `secondary_market_cap_raw_cny_100m`, but not used as the main market-cap anchor because it is not stable enough across A-share share-class contexts.
- This is a latest public quote snapshot returned on 2026-06-18 with embedded 2026-06-17 post-close timestamps. It is not a Wind/Choice standardized valuation database and not terminal-grade realtime order-flow evidence.
