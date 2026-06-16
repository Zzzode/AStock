# Liquidity and Turnover Proxy

**Source:** Yahoo daily close and volume records already archived in `historical_market_data.json`, `watchlist_historical_market_data.json`, and `pengding_market_positioning_evidence.json`.

**Method:** Daily turnover proxy = close price x daily volume. For A-share tickers this is an approximate CNY traded-value proxy. It is not exchange official amount, Wind/Choice turnover, free-float turnover, or intraday liquidity.

| Ticker | Name | Group | Records | Avg daily turnover | Median daily turnover | Max daily turnover | Avg volume |
|---|---|---|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | core | 279 | 51.06亿元 | 43.67亿元 | 176.37亿元 | 7107.99万股 |
| 002916 | 深南电路 | core | 279 | 23.72亿元 | 20.91亿元 | 92.00亿元 | 1130.86万股 |
| 300476 | 胜宏科技 | core | 279 | 107.93亿元 | 90.56亿元 | 314.15亿元 | 4319.76万股 |
| 600183 | 生益科技 | core | 279 | 30.78亿元 | 25.10亿元 | 156.68亿元 | 4614.68万股 |
| 603186 | 华正新材 | core | 279 | 6.82亿元 | 4.66亿元 | 36.18亿元 | 1110.70万股 |
| 002436 | 兴森科技 | watchlist | 279 | 24.86亿元 | 19.12亿元 | 106.72亿元 | 10964.02万股 |
| 002938 | 鹏鼎控股 | watchlist | 279 | 20.58亿元 | 18.51亿元 | 116.39亿元 | 3584.98万股 |
| 300400 | 劲拓股份 | watchlist | 279 | 3.00亿元 | 1.88亿元 | 14.52亿元 | 1219.07万股 |
| 301200 | 大族数控 | watchlist | 279 | 7.04亿元 | 6.10亿元 | 28.55亿元 | 554.02万股 |
| 301377 | 鼎泰高科 | watchlist | 279 | 8.48亿元 | 6.78亿元 | 32.27亿元 | 721.28万股 |
| 688519 | 南亚新材 | watchlist | 279 | 6.34亿元 | 4.56亿元 | 27.15亿元 | 638.08万股 |
| 688630 | 芯碁微装 | watchlist | 279 | 10.05亿元 | 8.27亿元 | 39.03亿元 | 596.80万股 |

## Boundary

- This is a public daily liquidity proxy using Yahoo close and volume.
- It does not replace exchange official成交额, turnover ratio, order-book depth, intraday slippage, block trade, margin financing, northbound daily change, or terminal-grade order flow.
- Use only to compare rough trading activity and liquidity scale across the report universe.
