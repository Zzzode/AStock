# Eastmoney Liquidity / Turnover Evidence

**Source:** Eastmoney `push2his` daily K-line public endpoint. Raw JSON is archived under `data/raw_eastmoney_kline/`.

**Fields:** `f57` daily amount, `f61` turnover rate. Period requested: 2025-04-21 to 2026-06-15.

## Successful tickers

| Ticker | Name | Records | Avg daily amount | Median amount | Max amount | Avg turnover | Max turnover |
|---|---|---:|---:|---:|---:|---:|---:|
| 300476 | 胜宏科技 | 279 | 107.59亿元 | 90.63亿元 | 291.43亿元 | 5.04% | 11.65% |
| 002463 | 沪电股份 | 279 | 50.97亿元 | 43.37亿元 | 171.85亿元 | 3.70% | 9.07% |
| 600183 | 生益科技 | 279 | 30.71亿元 | 25.20亿元 | 160.27亿元 | 1.93% | 4.82% |
| 688630 | 芯碁微装 | 279 | 10.02亿元 | 8.31亿元 | 40.20亿元 | 4.53% | 11.86% |
| 301377 | 鼎泰高科 | 279 | 8.41亿元 | 6.81亿元 | 31.19亿元 | 9.99% | 29.29% |
| 603186 | 华正新材 | 279 | 6.79亿元 | 4.65亿元 | 37.91亿元 | 7.55% | 20.36% |
| 688519 | 南亚新材 | 279 | 6.30亿元 | 4.53亿元 | 27.65亿元 | 2.72% | 8.18% |
| 300400 | 劲拓股份 | 279 | 2.99亿元 | 1.87亿元 | 14.64亿元 | 5.06% | 20.66% |

## Failed / unstable tickers

002916, 002436, 301200, 002938

## Boundary

- This is closer to exchange-style public market data than Yahoo close x volume because Eastmoney provides daily amount and turnover fields directly.
- Endpoint access was unstable in this environment; only successful raw JSON files are used. Failed tickers remain covered by Yahoo liquidity proxy.
- This still does not provide order-book depth, intraday slippage, block trades, margin financing, northbound daily beneficial-owner changes or terminal-grade order flow.
