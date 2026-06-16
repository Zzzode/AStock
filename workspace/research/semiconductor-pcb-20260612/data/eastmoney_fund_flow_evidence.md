# Eastmoney Fund Flow Evidence

**Source:** `push2his.eastmoney.com/api/qt/stock/fflow/daykline/get`.

**Boundary:** This is a public daily fund-flow proxy, not full institutional positioning or verified exchange order-flow data.

| Ticker | Name | Bucket | Records | Latest date | Latest main net inflow | 30-row sum main net inflow | Latest close | Latest pct chg |
|---|---|---|---:|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | core | 30 | 2026-06-15 | 8.80亿元 | -55.63亿元 | 133.76 | 6.84% |
| 300476 | 胜宏科技 | core | 30 | 2026-06-15 | 9.29亿元 | -177.87亿元 | 344.50 | 5.28% |
| 002916 | 深南电路 | core | 30 | 2026-06-15 | 6.71亿元 | 16.37亿元 | 399.80 | 5.35% |
| 600183 | 生益科技 | core | 30 | 2026-06-15 | 20.67亿元 | 57.94亿元 | 166.41 | 10.00% |
| 603186 | 华正新材 | core | 30 | 2026-06-15 | 1.41亿元 | 7.37亿元 | 187.33 | 10.00% |
| 688519 | 南亚新材 | watchlist | 30 | 2026-06-15 | -0.44亿元 | 3.25亿元 | 338.30 | 13.83% |
| 002436 | 兴森科技 | watchlist | 30 | 2026-06-15 | 1.99亿元 | -2.66亿元 | 40.09 | 6.06% |
| 301200 | 大族数控 | watchlist | 30 | 2026-06-15 | 1.52亿元 | 0.73亿元 | 304.40 | 9.89% |
| 688630 | 芯碁微装 | watchlist | 30 | 2026-06-15 | -0.22亿元 | -1.55亿元 | 438.19 | 11.22% |
| 300400 | 劲拓股份 | watchlist | 30 | 2026-06-15 | -0.27亿元 | -1.39亿元 | 43.21 | 10.03% |
| 301377 | 鼎泰高科 | watchlist | 30 | 2026-06-15 | 2.54亿元 | 9.99亿元 | 553.56 | 17.45% |

## Notes

- Direct daykline endpoint was fetched through `curl` with a browser user agent after Python urllib requests were rejected by remote disconnects.
- The endpoint returned rows for every core and watchlist ticker in the current universe.
- Earlier `clist`, targeted realtime `ulist.np`, AkShare ranking and northbound attempts remain recorded as failed/partial in their own evidence files.
- Treat these as market-behavior proxies only; they do not identify fund managers, active/passive ownership, northbound beneficial owners or complete institutional positions.
