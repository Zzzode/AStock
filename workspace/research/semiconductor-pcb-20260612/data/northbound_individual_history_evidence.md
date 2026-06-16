# Northbound Individual Holding History Evidence

**Source:** AkShare `stock_hsgt_individual_em`, Eastmoney Stock Connect single-stock holding history.

**Boundary:** Public total Stock Connect holding history. This is not beneficial-owner disclosure, not institution-level current positioning, and not a substitute for Wind/Choice northbound database.

| Ticker | Name | Status | Records | First date | Latest date | Holding shares | Holding MV | A-share pct | Latest add shares |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | ok | 1673 | 2017-03-16 | 2024-08-16 | 8586.63万股 | 28.97亿元 | 4.48 | 254.53万股 |
| 300476 | 胜宏科技 | ok | 1680 | 2017-03-16 | 2024-08-16 | 1604.62万股 | 5.55亿元 | 1.86 | -124.24万股 |
| 002916 | 深南电路 | ok | 1374 | 2018-07-04 | 2024-08-16 | 1165.65万股 | 12.55亿元 | 2.27 | -52.14万股 |
| 600183 | 生益科技 | ok | 1675 | 2017-03-16 | 2024-08-16 | 17671.08万股 | 32.60亿元 | 7.45 | 182.85万股 |
| 603186 | 华正新材 | error | 0 | N/A | N/A | N/A | N/A | N/A | N/A |
| 688519 | 南亚新材 | ok | 267 | 2023-06-19 | 2024-08-16 | 133.82万股 | 0.27亿元 | 0.57 | 15.20万股 |
| 002436 | 兴森科技 | ok | 1677 | 2017-03-16 | 2024-08-16 | 3539.89万股 | 3.39亿元 | 2.09 | 210.52万股 |
| 301200 | 大族数控 | ok | 281 | 2023-01-12 | 2024-08-16 | 25.11万股 | 0.08亿元 | 0.05 | 0.45万股 |
| 688630 | 芯碁微装 | ok | 290 | 2023-03-13 | 2024-08-16 | 50.13万股 | 0.27亿元 | 0.38 | 3.56万股 |
| 300400 | 劲拓股份 | error | 0 | N/A | N/A | N/A | N/A | N/A | N/A |
| 301377 | 鼎泰高科 | ok | 332 | 2023-03-13 | 2024-08-16 | 59.13万股 | 0.10亿元 | 0.14 | 11.91万股 |

## Interpretation

- Public total Stock Connect holding histories are available for most core/watchlist names through Eastmoney/AkShare.
- 603186 may be unavailable from this interface, consistent with prior northbound API gaps.
- This materially improves northbound/Stock Connect positioning evidence but still does not provide beneficial-owner, broker-custodian or institution-level current holdings after the HKEX disclosure-rule change.
