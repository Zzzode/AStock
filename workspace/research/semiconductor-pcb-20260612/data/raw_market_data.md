# Raw Market Data

## Quote Collection Status

The local quote adapter was attempted during the rebuild and was slow/unresponsive. Eastmoney realtime `ulist` returned HTTP 502 in the latest retry. Tencent `qt.gtimg.cn` quote feed succeeded and is archived as raw data.

## Refreshed Snapshot Used

Latest valuation anchors use `data/tencent_realtime_market_snapshot_20260616.md`, generated from `data/raw_tencent_quote/quote_20260616.txt`.

| Ticker | Company | Price | Total market cap | Quality |
|---|---|---:|---:|---|
| 002463 | 沪电股份 | 139.03 | CNY 267.328bn | Tencent 2026-06-16 intraday quote |
| 300476 | 胜宏科技 | 350.45 | CNY 303.208bn | Tencent 2026-06-16 intraday quote |
| 002916 | 深南电路 | 406.04 | CNY 269.939bn | Tencent 2026-06-16 intraday quote |
| 600183 | 生益科技 | 180.56 | CNY 432.351bn | Tencent 2026-06-16 intraday quote |
| 603186 | 华正新材 | 206.06 | CNY 32.308bn | Tencent 2026-06-16 intraday quote |
| 688519 | 南亚新材 | 358.00 | CNY 84.195bn | Tencent 2026-06-16 intraday quote |
| 002436 | 兴森科技 | 43.18 | CNY 65.544bn | Tencent 2026-06-16 intraday quote |
| 301200 | 大族数控 | 324.55 | CNY 138.011bn | Tencent 2026-06-16 intraday quote |
| 688630 | 芯碁微装 | 458.22 | CNY 60.366bn | Tencent 2026-06-16 intraday quote |
| 300400 | 劲拓股份 | 43.73 | CNY 10.575bn | Tencent 2026-06-16 intraday quote |
| 301377 | 鼎泰高科 | 544.38 | CNY 53.818bn | Tencent 2026-06-16 intraday quote |
| 002938 | 鹏鼎控股 | 107.77 | CNY 248.882bn | Tencent 2026-06-16 intraday quote |

## Archived Baseline

The older `data/current_market_snapshot.md` dated 2026-06-12 is retained only as a historical baseline and should not be used as the latest valuation anchor.

## Usage Restriction

The Tencent snapshot can support indicative valuation and crowding discussion. It should not be presented as a standardized terminal valuation database or audited closing price.
