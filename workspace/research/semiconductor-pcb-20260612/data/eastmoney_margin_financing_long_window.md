# Eastmoney Margin Financing Long-Window Evidence

**Source:** Eastmoney DataCenter `RPTA_WEB_RZRQ_GGMX`; raw JSON under `data/raw_eastmoney_margin/`.

**Window:** 300 public rows per successful ticker, ending 2026-06-15. This is a public leverage / crowding proxy, not institutional ownership, beneficial-owner positioning or terminal-grade order flow.

## 300-row leverage window

| Ticker | Name | Records | Window | Latest financing | Change vs first row | Latest financing / float MV | Max ratio | 300-row net financing buy |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 300476 | 胜宏科技 | 300 | 2025-03-20 to 2026-06-15 | 231.73亿元 | 187.90亿元 (+428.7%) | 7.77% | 8.08% | 188.25亿元 |
| 002436 | 兴森科技 | 300 | 2025-03-20 to 2026-06-15 | 32.59亿元 | 15.66亿元 (+92.5%) | 5.35% | 10.19% | 15.69亿元 |
| 002463 | 沪电股份 | 300 | 2025-03-20 to 2026-06-15 | 66.45亿元 | 45.36亿元 (+215.1%) | 2.58% | 3.98% | 45.07亿元 |
| 688630 | 芯碁微装 | 300 | 2025-03-20 to 2026-06-15 | 9.72亿元 | 6.78亿元 (+230.4%) | 1.68% | 8.22% | 7.02亿元 |
| 301377 | 鼎泰高科 | 300 | 2025-03-20 to 2026-06-15 | 6.40亿元 | 4.46亿元 (+228.8%) | 1.17% | 10.79% | 4.48亿元 |
| 600183 | 生益科技 | 300 | 2025-03-20 to 2026-06-15 | 42.21亿元 | 35.89亿元 (+568.5%) | 1.06% | 1.90% | 35.39亿元 |
| 002938 | 鹏鼎控股 | 300 | 2025-03-20 to 2026-06-15 | 24.69亿元 | 21.56亿元 (+688.9%) | 1.02% | 1.41% | 21.60亿元 |
| 688519 | 南亚新材 | 300 | 2025-03-20 to 2026-06-15 | 7.11亿元 | 6.01亿元 (+550.4%) | 0.89% | 2.09% | 6.14亿元 |
| 002916 | 深南电路 | 300 | 2025-03-20 to 2026-06-15 | 17.60亿元 | 5.39亿元 (+44.1%) | 0.66% | 2.23% | 5.96亿元 |
| 301200 | 大族数控 | 300 | 2025-03-20 to 2026-06-15 | 5.09亿元 | 3.53亿元 (+226.1%) | 0.39% | 11.49% | 3.55亿元 |

## Empty / unavailable tickers

- 300400, 603186

## Interpretation

- The long-window view separates persistent leverage crowding from a single-day or 30-row move.
- Shenghong and Xingsen show the highest latest financing-to-float-market-value ratios among successful tickers, so their drawdown risk is more sensitive to financing-balance reversal.
- Hudian, Shengyi and Pengding show large positive 300-row net financing purchases, indicating persistent public leverage accumulation over the available window.
- This remains a public margin-financing proxy and cannot identify institutions, active/passive funds, beneficial owners or realtime order flow.
