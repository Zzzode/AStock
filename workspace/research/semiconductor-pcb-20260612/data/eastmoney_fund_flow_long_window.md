# Eastmoney Fund Flow Long-Window Evidence

**Source:** `push2his.eastmoney.com/api/qt/stock/fflow/daykline/get` with `lmt=300`.

**Boundary:** Public daily fund-flow proxy only. It does not identify fund managers, active/passive ownership, beneficial owners, northbound ownership or terminal-grade order flow.

## Long-window fund-flow proxy

| Ticker | Name | Records | Window | Latest main net inflow | Long-window main net inflow | Large + super-large net inflow | Latest close |
|---|---|---:|---|---:|---:|---:|---:|
| 002916 | 深南电路 | 121 | 2025-12-12 to 2026-06-16 | 6.63亿元 | 38.29亿元 | 38.29亿元 | 403.88 |
| 600183 | 生益科技 | 121 | 2025-12-12 to 2026-06-16 | -8.05亿元 | 20.40亿元 | 20.40亿元 | 179.4 |
| 603186 | 华正新材 | 121 | 2025-12-12 to 2026-06-16 | 1.11亿元 | 10.86亿元 | 10.86亿元 | 206.06 |
| 301377 | 鼎泰高科 | 121 | 2025-12-12 to 2026-06-16 | -2.95亿元 | 0.41亿元 | 0.41亿元 | 553.58 |
| 688519 | 南亚新材 | 121 | 2025-12-12 to 2026-06-16 | 0.24亿元 | -0.55亿元 | -0.55亿元 | 356.44 |
| 301200 | 大族数控 | 121 | 2025-12-12 to 2026-06-16 | 1.64亿元 | -1.01亿元 | -1.01亿元 | 326.0 |
| 300400 | 劲拓股份 | 121 | 2025-12-12 to 2026-06-16 | -0.21亿元 | -3.17亿元 | -3.17亿元 | 44.85 |
| 688630 | 芯碁微装 | 121 | 2025-12-12 to 2026-06-16 | 1.88亿元 | -14.73亿元 | -14.73亿元 | 463.8 |
| 002436 | 兴森科技 | 121 | 2025-12-12 to 2026-06-16 | 8.99亿元 | -39.44亿元 | -39.44亿元 | 44.1 |
| 002463 | 沪电股份 | 121 | 2025-12-12 to 2026-06-16 | 7.77亿元 | -114.00亿元 | -114.00亿元 | 140.64 |
| 300476 | 胜宏科技 | 121 | 2025-12-12 to 2026-06-16 | 9.32亿元 | -336.91亿元 | -336.91亿元 | 355.48 |

## Interface limit

- `lmt=120` returned 120 rows for the test ticker, while `lmt=300` and `lmt=1000` returned only about 121 rows in this environment, starting around 2025-12-12.
- This extends the previous 30-row view but remains constrained by the public endpoint.

## Interpretation

- The long-window proxy improves persistence checks for public fund-flow direction beyond a one-month window.
- It remains a market-behavior proxy, not institutional ownership or verified exchange order-flow data.
