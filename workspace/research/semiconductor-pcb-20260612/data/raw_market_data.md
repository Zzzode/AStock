# Raw Market Data

## Quote Collection Status

The local quote adapter was attempted during the rebuild and was slow/unresponsive. Eastmoney realtime `ulist` returned HTTP 502 in the latest retry. Tencent `qt.gtimg.cn` quote feed succeeded and is archived as raw data.

## Refreshed Snapshot Used

Latest valuation anchors use `data/tencent_realtime_market_snapshot_20260618.md`, generated from `data/raw_tencent_quote/quote_20260618.txt`. The fetch ran on 2026-06-18 and Tencent returned embedded quote timestamps around 2026-06-17 16:14 CST.

| Ticker | Company | Price | Total market cap | Quality |
|---|---|---:|---:|---|
| 002463 | 沪电股份 | 146.55 | CNY 281.788bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 300476 | 胜宏科技 | 361.70 | CNY 312.941bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 002916 | 深南电路 | 444.27 | CNY 295.355bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 600183 | 生益科技 | 180.15 | CNY 431.369bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 603186 | 华正新材 | 226.67 | CNY 35.540bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 688519 | 南亚新材 | 395.01 | CNY 92.899bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 002436 | 兴森科技 | 47.80 | CNY 72.557bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 301200 | 大族数控 | 328.08 | CNY 139.512bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 688630 | 芯碁微装 | 475.77 | CNY 62.678bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 300400 | 劲拓股份 | 43.61 | CNY 10.546bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 301377 | 鼎泰高科 | 590.00 | CNY 58.328bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 002938 | 鹏鼎控股 | 119.01 | CNY 274.840bn | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |

## Archived Baseline

The older `data/current_market_snapshot.md` dated 2026-06-12 and `data/tencent_realtime_market_snapshot_20260616.md` are retained as historical baselines and should not be used as the latest valuation anchor.

## Usage Restriction

The Tencent snapshot can support indicative valuation and crowding discussion. It should not be presented as a standardized terminal valuation database, audited closing price or terminal-grade order-flow evidence.
