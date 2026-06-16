# Eastmoney Block Trade Evidence

**Source:** Eastmoney DataCenter `RPT_DATA_BLOCKTRADE`; raw JSON archived under `data/raw_eastmoney_blocktrade/`.

**Period:** 2025-04-21 to 2026-06-15.

| Ticker | Name | Deals | Total amount | Avg amount | Max deal | Avg premium/discount | Discount deals | Latest date |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 300476 | 胜宏科技 | 136 | 37.47亿元 | 0.28亿元 | 11.08亿元 | -0.07% | 120 | 2026-05-11 |
| 002938 | 鹏鼎控股 | 62 | 35.19亿元 | 0.57亿元 | 19.92亿元 | -0.12% | 62 | 2026-05-25 |
| 688519 | 南亚新材 | 14 | 3.19亿元 | 0.23亿元 | 0.37亿元 | -0.02% | 13 | 2026-06-11 |
| 301200 | 大族数控 | 49 | 2.96亿元 | 0.06亿元 | 0.40亿元 | -0.20% | 47 | 2026-05-11 |
| 688630 | 芯碁微装 | 41 | 2.02亿元 | 0.05亿元 | 0.16亿元 | -0.13% | 40 | 2026-01-21 |
| 002463 | 沪电股份 | 6 | 1.13亿元 | 0.19亿元 | 0.45亿元 | -0.07% | 4 | 2026-05-11 |
| 002436 | 兴森科技 | 16 | 0.83亿元 | 0.05亿元 | 0.20亿元 | -0.04% | 10 | 2026-06-15 |
| 600183 | 生益科技 | 3 | 0.47亿元 | 0.16亿元 | 0.25亿元 | -0.05% | 1 | 2026-06-12 |
| 301377 | 鼎泰高科 | 1 | 0.15亿元 | 0.15亿元 | 0.15亿元 | 0.00% | 0 | 2026-06-12 |
| 002916 | 深南电路 | 1 | 0.03亿元 | 0.03亿元 | 0.03亿元 | 0.00% | 0 | 2026-04-22 |

## Failed / empty tickers

- 603186 华正新材: 返回数据为空
- 300400 劲拓股份: 返回数据为空

## Boundary

- Block trades are public large-transaction traces, not a complete order-flow tape.
- They do not identify ultimate beneficial owners beyond reported buyer/seller broker seats.
- Absence of records in the queried period does not prove no private negotiated transfer or off-exchange risk; it means Eastmoney public block-trade table returned no rows.
