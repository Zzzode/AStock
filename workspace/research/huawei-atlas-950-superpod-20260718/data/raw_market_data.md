# Raw Market Data Capture

## Scope and provenance

- Market cutoff: **2026-07-17 close**.
- Price cross-check source: AStock `market-snapshot` (Sina stream), retrieved `2026-07-18 16:28-16:47 CST`; all 22 close prices matched Tencent.
- Capitalization/share-count source: Tencent batch quote `https://qt.gtimg.cn/`, retrieved `2026-07-18 16:35 CST`; quote timestamps are `2026-07-17 16:14 CST`.
- Five-day volume source: Tencent adjusted daily K-line, dates `2026-07-13` through `2026-07-17`, retrieved `2026-07-18 16:35 CST`.
- Northbound source: HKEX official quarterly Northbound shareholding search, observation date `2026-06-30`, captured `2026-07-18 CST`.
- No market value was estimated. “Locked/non-circulating” in the verified table is the arithmetic difference between Tencent total shares and circulating shares; it is not a regulatory lock-up schedule.

## Raw close, capitalization, and share-count fields

| Ticker | Company | Close | Change | Total MCap (CNY 100m) | Circulating MCap (CNY 100m) | Total shares | Circulating shares | Quote timestamp | Source | Quality |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|
| 000034 | 神州数码 | 24.61 | -8.61% | 250.22 | 208.98 | 1,016,739,663 | 849,147,842 | 2026-07-17 16:14:09 | Tencent quote; Sina close cross-check | Medium |
| 002261 | 拓维信息 | 27.38 | -8.58% | 344.98 | 313.80 | 1,259,968,174 | 1,146,105,481 | 2026-07-17 16:14:48 | Tencent quote; Sina close cross-check | Medium |
| 000988 | 华工科技 | 117.62 | -10.00% | 1,182.67 | 1,182.06 | 1,005,502,707 | 1,004,985,657 | 2026-07-17 16:14:39 | Tencent quote; Sina close cross-check | Medium |
| 002281 | 光迅科技 | 189.45 | -10.00% | 1,567.82 | 1,478.65 | 827,565,038 | 780,498,352 | 2026-07-17 16:14:36 | Tencent quote; Sina close cross-check | Medium |
| 688498 | 源杰科技 | 1,656.00 | -9.31% | 2,061.73 | 2,035.09 | 124,500,377 | 122,892,144 | 2026-07-17 16:14:55 | Tencent quote; Sina close cross-check | Medium |
| 300620 | 光库科技 | 238.90 | -12.49% | 595.29 | 590.33 | 249,180,545 | 247,103,188 | 2026-07-17 16:14:18 | Tencent quote; Sina close cross-check | Medium |
| 300548 | 长芯博创 | 166.21 | -13.99% | 490.00 | 452.44 | 294,804,803 | 272,208,555 | 2026-07-17 16:14:06 | Tencent quote; Sina close cross-check | Medium |
| 600183 | 生益科技 | 132.29 | -10.00% | 3,213.33 | 3,167.69 | 2,429,003,670 | 2,394,501,544 | 2026-07-17 16:14:53 | Tencent quote; Sina close cross-check | Medium |
| 002916 | 深南电路 | 334.00 | -8.24% | 2,275.10 | 2,220.46 | 681,166,595 | 664,809,450 | 2026-07-17 16:14:33 | Tencent quote; Sina close cross-check | Medium |
| 002463 | 沪电股份 | 127.80 | -6.52% | 2,459.34 | 2,457.35 | 1,924,363,537 | 1,922,810,486 | 2026-07-17 16:14:21 | Tencent quote; Sina close cross-check | Medium |
| 300476 | 胜宏科技 | 241.50 | -10.86% | 2,373.43 | 2,089.45 | 982,784,813 | 865,194,945 | 2026-07-17 16:14:24 | Tencent quote; Sina close cross-check | Medium |
| 002837 | 英维克 | 61.57 | -9.27% | 784.62 | 696.02 | 1,274,349,692 | 1,130,458,146 | 2026-07-17 16:14:48 | Tencent quote; Sina close cross-check | Medium |
| 301018 | 申菱环境 | 86.96 | -15.50% | 325.48 | 245.94 | 374,281,339 | 282,822,899 | 2026-07-17 16:14:00 | Tencent quote; Sina close cross-check | Medium |
| 300990 | 同飞股份 | 92.74 | -15.54% | 158.79 | 72.12 | 171,216,590 | 77,763,920 | 2026-07-17 16:14:24 | Tencent quote; Sina close cross-check | Medium |
| 002335 | 科华数据 | 29.75 | -6.65% | 224.44 | 196.27 | 754,410,409 | 659,734,682 | 2026-07-17 16:14:06 | Tencent quote; Sina close cross-check | Medium |
| 002364 | 中恒电气 | 41.97 | -9.99% | 236.53 | 234.24 | 563,564,960 | 558,103,760 | 2026-07-17 16:14:24 | Tencent quote; Sina close cross-check | Medium |
| 002922 | 伊戈尔 | 23.30 | -6.35% | 98.46 | 87.84 | 422,582,924 | 377,000,057 | 2026-07-17 16:14:27 | Tencent quote; Sina close cross-check | Medium |
| 002130 | 沃尔核材 | 15.24 | -4.63% | 213.34 | 174.80 | 1,399,887,362 | 1,146,952,254 | 2026-07-17 16:14:30 | Tencent quote; Sina close cross-check | Medium |
| 300913 | 兆龙互连 | 33.22 | -7.70% | 113.87 | 94.96 | 342,781,120 | 285,854,320 | 2026-07-17 16:14:18 | Tencent quote; Sina close cross-check | Medium |
| 688668 | 鼎通科技 | 243.46 | -20.00% | 339.07 | 339.07 | 139,270,606 | 139,270,606 | 2026-07-17 16:14:53 | Tencent quote; Sina close cross-check | Medium |
| 002230 | 科大讯飞 | 41.12 | -2.07% | 987.74 | 900.24 | 2,402,079,841 | 2,189,292,700 | 2026-07-17 16:14:42 | Tencent quote; Sina close cross-check | Medium |
| 002025 | 航天电器 | 64.76 | -9.99% | 294.02 | 293.93 | 454,019,772 | 453,871,299 | 2026-07-17 16:14:33 | Tencent quote; Sina close cross-check | Medium |

## K-line unit handling

Tencent daily K-line volume is quoted in 100-share lots for main-board/ChiNext names, but in shares for STAR Market names (`688498`, `688668`). The verified five-day averages normalize both conventions to shares and were checked against the Sina 2026-07-17 volume field. Treating STAR Market raw volume as lots would overstate volume by 100x; that discrepancy was detected and corrected before verification.

## Northbound observation boundary

The official Northbound percentage is a **2026-06-30 quarter-end** observation, not a 2026-07-17 daily holding. Exact official rows and HKEX denominator cautions are preserved in `sources/official-filings-20260718/northbound_holdings_20260630.md`.
