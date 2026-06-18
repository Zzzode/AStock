# Verified Market Data

## Verification Method

Market data was first checked against the archived `current_market_snapshot.md`. Initial live refresh failed during the rebuild, but Tencent quote feed later refreshed 12/12 current-universe tickers on 2026-06-16 and was refetched on 2026-06-18 with embedded 2026-06-17 post-close timestamps.

See `data/tencent_realtime_market_snapshot_20260618.md` and raw `data/raw_tencent_quote/quote_20260618.txt`.

## Refreshed Public Quote Snapshot

| Ticker | Company | Price | Total market cap | PE TTM | PB | Timestamp | Status |
|---|---|---:|---:|---:|---:|---|---|
| 002463 | 沪电股份 | 146.55 | CNY 281.788bn | 65.56 | 17.82 | 20260617161436 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 300476 | 胜宏科技 | 361.70 | CNY 312.941bn | 75.96 | 22.69 | 20260617161418 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 002916 | 深南电路 | 444.27 | CNY 295.355bn | 83.26 | 18.39 | 20260617161445 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 600183 | 生益科技 | 180.15 | CNY 431.369bn | 111.39 | 27.38 | 20260617161404 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 603186 | 华正新材 | 226.67 | CNY 35.540bn | 122.88 | 15.31 | 20260617161411 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 688519 | 南亚新材 | 395.01 | CNY 92.899bn | 251.53 | 32.99 | 20260617161451 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 002436 | 兴森科技 | 47.80 | CNY 72.557bn | 562.95 | 15.37 | 20260617161418 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 301200 | 大族数控 | 328.08 | CNY 139.512bn | 155.70 | 14.57 | 20260617161445 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 688630 | 芯碁微装 | 475.77 | CNY 62.678bn | 180.91 | 26.94 | 20260617161449 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 300400 | 劲拓股份 | 43.61 | CNY 10.546bn | 124.75 | 14.97 | 20260617161421 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 301377 | 鼎泰高科 | 590.00 | CNY 58.328bn | 390.48 | 89.55 | 20260617161457 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |
| 002938 | 鹏鼎控股 | 119.01 | CNY 274.840bn | 74.29 | 8.53 | 20260617161439 | Tencent 2026-06-18 fetch / 2026-06-17 embedded timestamp |

## Derived Metrics

Derived valuation metrics now use `data/reverse_valuation_requirement_matrix_20260618.md` and Chapter 8 Exhibit 20b, based on the 2026-06-18 Tencent refetch.

## Quality Gate Result

Arithmetic checks pass for refreshed valuation anchors. This is a public quote proxy, not Wind/Choice standardized valuation history or audited closing valuation.
