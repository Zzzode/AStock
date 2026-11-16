# Raw Market Data — 2026-08-11 Pre-Open

- Collection window: 2026-08-11T09:22:48+08:00 to 2026-08-11T09:22:52+08:00
- Completed-session close date: 2026-08-10 (the 2026-08-11 collection was pre-open).
- Data path: Tencent public batch quote + Tencent adjusted daily K-line + Sohu daily OHLCV/trading value.
- Degradation: the preferred local astock CLI was unavailable because `.venv/bin/python` was absent.

| Ticker | Company | 8/10 close | 8/11 pre-open indication | 1Y position (adj.) | 1Y high / low (adj.) | 8/10 trading value | 5d avg trading value | Pre-open zero trade | Validation |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| 000703 | 恒逸石化 | 18.18 | 18.56 | 99.96% | 18.18 / 5.86 | CNY 2.07bn | CNY 1.50bn | yes | pass |
| 002379 | 宏桥控股 | 19.76 | 19.80 | 30.94% | 32.28 / 14.15 | CNY 1.25bn | CNY 1.52bn | yes | pass |
| 300014 | 亿纬锂能 | 55.22 | 55.31 | 22.45% | 90.77 / 44.93 | CNY 2.19bn | CNY 2.37bn | yes | pass |
| 002497 | 雅化集团 | 19.09 | 19.17 | 32.67% | 31.02 / 13.30 | CNY 0.95bn | CNY 0.69bn | yes | pass |
| 002432 | 九安医疗 | 72.28 | 70.20 | 65.29% | 91.27 / 36.58 | CNY 2.89bn | CNY 3.05bn | yes | pass |
| 000623 | 吉林敖东 | 18.28 | 18.35 | 38.75% | 21.53 / 16.23 | CNY 0.28bn | CNY 0.23bn | yes | pass |
| 600739 | 辽宁成大 | 10.90 | 10.87 | 28.86% | 13.34 / 9.91 | CNY 0.17bn | CNY 0.15bn | yes | pass |
| 000685 | 中山公用 | 11.26 | 11.28 | 43.25% | 14.04 / 9.14 | CNY 0.24bn | CNY 0.18bn | yes | pass |
| 600150 | 中国船舶 | 34.83 | 34.84 | 41.61% | 41.41 / 30.14 | CNY 2.86bn | CNY 2.93bn | yes | pass |
| 301308 | 江波龙 | 412.50 | 420.00 | 51.26% | 723.10 / 85.89 | CNY 11.85bn | CNY 8.58bn | yes | pass |
| 002812 | 恩捷股份 | 55.95 | 55.96 | 44.01% | 87.55 / 31.11 | CNY 1.80bn | CNY 1.23bn | yes | pass |
| 002240 | 盛新锂能 | 32.84 | 32.40 | 35.69% | 62.14 / 16.58 | CNY 1.84bn | CNY 1.45bn | yes | pass |
| 300390 | 天华新能 | 62.46 | 62.00 | 45.06% | 114.70 / 19.61 | CNY 3.19bn | CNY 2.23bn | yes | pass |

## Use Boundary

- Use `last_completed_session_close.close_cny` for 2026-08-10 close-based comparisons.
- Do not use `pre_open_snapshot_20260811.current_price_or_auction_indication_cny` as a close or as a realized 2026-08-11 return.
- Trading values are direct Sohu daily observations (CNY); no price-times-volume estimate was substituted.
- Full source URLs, retrieval times, file hashes, raw responses, and any failures are in `raw_market_data_20260811.json`.
