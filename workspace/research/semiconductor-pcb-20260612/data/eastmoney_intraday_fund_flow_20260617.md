# Eastmoney Intraday Fund Flow Evidence

**Run date:** 2026-06-17

**Source:** Eastmoney `push2.eastmoney.com/api/qt/stock/fflow/kline/get`, `klt=1`, `lmt=0`.

**Fields:** `f51=time`, `f52=main_net`, `f53=small_net`, `f54=medium_net`, `f55=large_net`, `f56=super_large_net`.

**Boundary:** Public minute-level cumulative fund-flow proxy. It is not exchange tick/order-book data, not beneficial-owner positioning and not terminal-grade order flow.

| Ticker | Name | Records | Window | Latest main | Latest super-large | Latest large | Latest medium | Latest small |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | 3.83亿元 | 3.44亿元 | 0.39亿元 | -3.81亿元 | -0.03亿元 |
| 300476 | 胜宏科技 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | 1.17亿元 | 1.44亿元 | -0.27亿元 | 0.75亿元 | -1.92亿元 |
| 002916 | 深南电路 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | 7.24亿元 | 8.90亿元 | -1.66亿元 | -7.23亿元 | -0.01亿元 |
| 600183 | 生益科技 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | -20.83亿元 | -18.94亿元 | -1.89亿元 | 9.52亿元 | 11.31亿元 |
| 603186 | 华正新材 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | -2.22亿元 | -3.21亿元 | 0.98亿元 | 1.59亿元 | 0.63亿元 |
| 002938 | 鹏鼎控股 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | 9.47亿元 | 10.84亿元 | -1.37亿元 | -6.06亿元 | -3.41亿元 |
| 688519 | 南亚新材 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | 0.04亿元 | -0.38亿元 | 0.43亿元 | 0.04亿元 | -0.08亿元 |
| 002436 | 兴森科技 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | -8.55亿元 | -1.69亿元 | -6.86亿元 | -0.52亿元 | 9.07亿元 |
| 301200 | 大族数控 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | -1.30亿元 | 0.11亿元 | -1.41亿元 | 0.01亿元 | 1.28亿元 |
| 688630 | 芯碁微装 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | -2.28亿元 | -2.59亿元 | 0.31亿元 | 2.31亿元 | -0.03亿元 |
| 300400 | 劲拓股份 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | -1.38亿元 | -0.44亿元 | -0.93亿元 | -0.13亿元 | 1.50亿元 |
| 301377 | 鼎泰高科 | 240 | 2026-06-17 09:31 to 2026-06-17 15:00 | 0.66亿元 | 0.25亿元 | 0.42亿元 | -0.66亿元 | -0.00亿元 |

## Interpretation

- This is a finer intraday public proxy than the previously archived 30-row and 121-row daily fund-flow views.
- Main net flow equals large plus super-large net flow in Eastmoney display logic; medium and small buckets are shown separately.
- Values are cumulative by minute for the trading day returned by the public endpoint.
- This still does not satisfy terminal-grade order-flow, exchange tick-data or beneficial-owner requirements.
