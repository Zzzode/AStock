# Verified Market Data

## Verification Method

Market data was first checked against the archived `current_market_snapshot.md`. Initial live refresh failed during the rebuild, but Tencent quote feed later refreshed 12/12 current-universe tickers on 2026-06-16.

See `data/tencent_realtime_market_snapshot_20260616.md` and raw `data/raw_tencent_quote/quote_20260616.txt`.

## Refreshed Public Quote Snapshot

| Ticker | Company | Price | Total market cap | PE TTM | PB | Timestamp | Status |
|---|---|---:|---:|---:|---:|---|---|
| 002463 | 沪电股份 | 139.03 | CNY 267.328bn | 62.19 | 16.90 | 20260616125539 | Tencent 2026-06-16 intraday quote |
| 300476 | 胜宏科技 | 350.45 | CNY 303.208bn | 73.60 | 21.99 | 20260616125539 | Tencent 2026-06-16 intraday quote |
| 002916 | 深南电路 | 406.04 | CNY 269.939bn | 76.10 | 16.81 | 20260616125633 | Tencent 2026-06-16 intraday quote |
| 600183 | 生益科技 | 180.56 | CNY 432.351bn | 111.65 | 27.44 | 20260616125606 | Tencent 2026-06-16 intraday quote |
| 603186 | 华正新材 | 206.06 | CNY 32.308bn | 111.70 | 13.92 | 20260616125606 | Tencent 2026-06-16 intraday quote |
| 688519 | 南亚新材 | 358.00 | CNY 84.195bn | 227.96 | 29.90 | 20260616125616 | Tencent 2026-06-16 intraday quote |
| 002436 | 兴森科技 | 43.18 | CNY 65.544bn | 508.54 | 13.88 | 20260616125542 | Tencent 2026-06-16 intraday quote |
| 301200 | 大族数控 | 324.55 | CNY 138.011bn | 154.02 | 14.41 | 20260616125624 | Tencent 2026-06-16 intraday quote |
| 688630 | 芯碁微装 | 458.22 | CNY 60.366bn | 174.24 | 25.95 | 20260616125612 | Tencent 2026-06-16 intraday quote |
| 300400 | 劲拓股份 | 43.73 | CNY 10.575bn | 125.09 | 15.01 | 20260616125630 | Tencent 2026-06-16 intraday quote |
| 301377 | 鼎泰高科 | 544.38 | CNY 53.818bn | 360.29 | 82.63 | 20260616125627 | Tencent 2026-06-16 intraday quote |
| 002938 | 鹏鼎控股 | 107.77 | CNY 248.882bn | 67.28 | 7.73 | 20260616125612 | Tencent 2026-06-16 intraday quote |

## Derived Metrics

| Company | Derived metric | Calculation | Status |
|---|---|---|---|
| 深南电路 | 2026E / 2027E / 2028E PE | 269.939 / 5.546 = 48.7x; 269.939 / 7.545 = 35.8x; 269.939 / 9.725 = 27.8x | refreshed public quote, broker forecast dependent |
| 华正新材 | 2026E / 2027E PE, updated Zheshang model | 32.308 / 0.573 = 56.4x; 32.308 / 0.803 = 40.2x | refreshed public quote, supplemental broker forecast dependent; 2028E unavailable |
| 胜宏科技 | 2026E / 2027E / 2028E PE, Kaiyuan model | 303.208 / 9.119 = 33.3x; 303.208 / 15.441 = 19.6x; 303.208 / 22.288 = 13.6x | restricted: source-dependent; see forecast range table for wider Guosheng/Kaiyuan dispersion |

## Quality Gate Result

Arithmetic checks pass for refreshed valuation anchors. This is an intraday public quote proxy, not Wind/Choice standardized valuation history or audited closing valuation.
