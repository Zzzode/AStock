# Fund Holder Style Proxy

**Source:** AkShare `stock_fund_stock_holder`.

**Method:** Rule-based classification from fund names. ETF/link/index/enhanced/bond keywords are separated; all other funds are treated as `active_like`. This is a public-source proxy, not an official active/passive label from Wind/Choice.

## Latest-period style summary

| Ticker | Name | Period | Active-like MV | Passive/index MV | Bond/fixed-income MV | Total visible MV | Read-through |
|---|---|---:|---:|---:|---:|---:|---|
| 002463 | 沪电股份 | 2026-03-31 | 260.18亿元 | 51.73亿元 | 2.69亿元 | 314.60亿元 | active-led |
| 300476 | 胜宏科技 | 2026-03-31 | 108.77亿元 | 61.14亿元 | 0.48亿元 | 170.39亿元 | active-led |
| 002916 | 深南电路 | 2026-03-31 | 119.46亿元 | 6.65亿元 | 2.86亿元 | 128.97亿元 | active-led |
| 600183 | 生益科技 | 2026-03-31 | 60.95亿元 | 0.73亿元 | 0.77亿元 | 62.46亿元 | active-led |
| 603186 | 华正新材 | 2026-03-31 | 0.83亿元 | 0.23亿元 | 0.61亿元 | 1.67亿元 | mixed/low visibility |
| 688519 | 南亚新材 | 2026-03-31 | 21.14亿元 | 0.04亿元 | 1.21亿元 | 22.39亿元 | active-led |
| 002436 | 兴森科技 | 2026-03-31 | 1.88亿元 | 1.28亿元 | 1.02亿元 | 4.18亿元 | index/passive material |
| 301200 | 大族数控 | 2026-03-31 | 16.73亿元 | 0.74亿元 | 1.00亿元 | 18.47亿元 | active-led |
| 688630 | 芯碁微装 | 2026-03-31 | 21.76亿元 | 1.05亿元 | 0.00亿元 | 22.81亿元 | active-led |
| 300400 | 劲拓股份 | 2025-12-31 | 0.71亿元 | 0.39亿元 | 0.01亿元 | 1.10亿元 | active-led |
| 301377 | 鼎泰高科 | 2026-03-31 | 45.10亿元 | 0.55亿元 | 7.16亿元 | 52.81亿元 | active-led |

## Notes

- `active_like` includes funds without ETF/index/enhanced/bond keywords. This can include closet-index or quant products, so it is not a formal active classification.
- `passive/index MV` combines ETF, ETF-linked, index and index-enhanced buckets.
- The proxy improves ownership-style discussion but does not replace a paid terminal active/passive holdings database.
