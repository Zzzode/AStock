# Eastmoney Margin Financing Evidence

**Source:** Eastmoney DataCenter `RPTA_WEB_RZRQ_GGMX`. Raw JSON is archived under `data/raw_eastmoney_margin/`.

**Fields:** `RZYE` financing balance, `RQYE` securities lending balance, `RZRQYE` margin balance, `RZJME` net financing purchase, `RZYEZB` financing balance / float market value.

## Latest and recent financing pressure

| Ticker | Name | Records | Latest date | Margin balance | Financing balance | Financing / float MV | Latest net financing buy | 30-row net financing buy |
|---|---|---:|---|---:|---:|---:|---:|---:|
| 300476 | 胜宏科技 | 300 | 2026-06-15 | 232.10亿元 | 231.73亿元 | 7.77% | 5.76亿元 | 27.18亿元 |
| 002463 | 沪电股份 | 300 | 2026-06-15 | 66.68亿元 | 66.45亿元 | 2.58% | 1.72亿元 | 29.62亿元 |
| 600183 | 生益科技 | 300 | 2026-06-15 | 42.72亿元 | 42.21亿元 | 1.06% | 1.75亿元 | 20.84亿元 |
| 002436 | 兴森科技 | 300 | 2026-06-15 | 32.90亿元 | 32.59亿元 | 5.35% | 0.63亿元 | 10.78亿元 |
| 002938 | 鹏鼎控股 | 300 | 2026-06-15 | 24.82亿元 | 24.69亿元 | 1.02% | -0.15亿元 | 10.88亿元 |
| 002916 | 深南电路 | 300 | 2026-06-15 | 17.73亿元 | 17.60亿元 | 0.66% | -0.73亿元 | -2.64亿元 |
| 688630 | 芯碁微装 | 300 | 2026-06-15 | 9.89亿元 | 9.72亿元 | 1.68% | -0.57亿元 | -0.07亿元 |
| 688519 | 南亚新材 | 300 | 2026-06-15 | 7.23亿元 | 7.11亿元 | 0.89% | -0.47亿元 | 1.98亿元 |
| 301377 | 鼎泰高科 | 300 | 2026-06-15 | 6.56亿元 | 6.40亿元 | 1.17% | 0.58亿元 | 3.60亿元 |
| 301200 | 大族数控 | 300 | 2026-06-15 | 5.14亿元 | 5.09亿元 | 0.39% | 0.60亿元 | 1.29亿元 |

## Failed / empty tickers

- 603186 华正新材: 返回数据为空
- 300400 劲拓股份: 返回数据为空

## Boundary

- This is public margin-financing data and a leverage/crowding proxy, not institutional ownership.
- It does not provide order-book depth, beneficial-owner northbound data, active/passive fund classification or terminal-grade order flow.
- Empty rows can mean the ticker was not covered by this Eastmoney report or had no available public margin-financing data in the queried period.
