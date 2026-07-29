# Verified Market Data (2026-07-17 Close)

## Verification status

- Coverage: **22/22** close prices, total market capitalizations, circulating market capitalizations, five-day average volumes, share-count lock-up proxies, and latest official Northbound holdings.
- Close price: Tencent and AStock/Sina matched for all 22 tickers.
- Capitalization arithmetic: `market cap / close` was reconciled to the provider's share-count fields within quote-rounding tolerance for all 22 rows.
- Volume arithmetic: five trading days (`2026-07-13` to `2026-07-17`) were averaged after normalizing main-board/ChiNext lots and STAR Market shares.
- Northbound: latest official individual-stock observation is `2026-06-30`, because HKEX publishes Northbound holdings quarterly rather than daily.

## Market table

| Ticker | Company | Price | Change | Total MCap (CNY 100m) | Circulating MCap proxy (CNY 100m) | 5d Avg Vol (m shares) | Non-circulating proxy (m shares; %) | NB holding (2026-06-30) | Source / timestamp | Quality |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|
| 000034 | 神州数码 | 24.61 | -8.61% | 250.22 | 208.98 | 69.07 | 167.59; 16.48% | 1.43% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002261 | 拓维信息 | 27.38 | -8.58% | 344.98 | 313.80 | 123.29 | 113.86; 9.04% | 0.53% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 000988 | 华工科技 | 117.62 | -10.00% | 1,182.67 | 1,182.06 | 63.47 | 0.52; 0.05% | 2.54% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002281 | 光迅科技 | 189.45 | -10.00% | 1,567.82 | 1,478.65 | 44.27 | 47.07; 5.69% | 2.22% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 688498 | 源杰科技 | 1,656.00 | -9.31% | 2,061.73 | 2,035.09 | 5.20 | 1.61; 1.29% | 2.39% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 300620 | 光库科技 | 238.90 | -12.49% | 595.29 | 590.33 | 11.37 | 2.08; 0.83% | 1.22% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 300548 | 长芯博创 | 166.21 | -13.99% | 490.00 | 452.44 | 15.38 | 22.60; 7.66% | 1.88% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 600183 | 生益科技 | 132.29 | -10.00% | 3,213.33 | 3,167.69 | 80.52 | 34.50; 1.42% | 5.03% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002916 | 深南电路 | 334.00 | -8.24% | 2,275.10 | 2,220.46 | 16.73 | 16.36; 2.40% | 2.70% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002463 | 沪电股份 | 127.80 | -6.52% | 2,459.34 | 2,457.35 | 81.36 | 1.55; 0.08% | 8.95% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 300476 | 胜宏科技 | 241.50 | -10.86% | 2,373.43 | 2,089.45 | 35.08 | 117.59; 11.96% | 3.44% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002837 | 英维克 | 61.57 | -9.27% | 784.62 | 696.02 | 49.38 | 143.89; 11.29% | 3.14% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 301018 | 申菱环境 | 86.96 | -15.50% | 325.48 | 245.94 | 16.33 | 91.46; 24.44% | 0.72% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 300990 | 同飞股份 | 92.74 | -15.54% | 158.79 | 72.12 | 10.96 | 93.45; 54.58% | 1.80% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002335 | 科华数据 | 29.75 | -6.65% | 224.44 | 196.27 | 23.08 | 94.68; 12.55% | 1.34% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002364 | 中恒电气 | 41.97 | -9.99% | 236.53 | 234.24 | 46.46 | 5.46; 0.97% | 1.71% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002922 | 伊戈尔 | 23.30 | -6.35% | 98.46 | 87.84 | 17.47 | 45.58; 10.79% | 3.19% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002130 | 沃尔核材 | 15.24 | -4.63% | 213.34 | 174.80 | 30.95 | 252.94; 18.07% | 0.82% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 300913 | 兆龙互连 | 33.22 | -7.70% | 113.87 | 94.96 | 7.05 | 56.93; 16.61% | 0.38% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 688668 | 鼎通科技 | 243.46 | -20.00% | 339.07 | 339.07 | 4.86 | 0.00; 0.00% | 0.55% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002230 | 科大讯飞 | 41.12 | -2.07% | 987.74 | 900.24 | 46.08 | 212.79; 8.86% | 2.35% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |
| 002025 | 航天电器 | 64.76 | -9.99% | 294.02 | 293.93 | 24.76 | 0.15; 0.03% | 0.29% | Tencent/Sina 2026-07-17; HKEX 2026-06-30 | Medium quote; High NB |

## Discrepancy and use notes

- **M-01, corrected:** Tencent K-line volume uses shares for STAR Market names and 100-share lots for the other names in this universe. The verified table normalizes both to shares; an uncorrected calculation would overstate `688498` and `688668` volume by 100x.
- **M-02, terminology:** Tencent “circulating market cap” is an unrestricted/circulating-share proxy, not a factor-vendor strategic free-float calculation. It is labeled as a proxy and must not be treated as MSCI-style free float.
- **M-03, terminology:** “Non-circulating proxy” is `total shares - circulating shares`; it does not identify contractual lock-up expiry dates or distinguish strategic holdings.
- **M-04, timestamp:** Tencent quote timestamps are approximately 16:14 CST and Sina timestamps approximately 16:29 CST, but all 22 close prices matched. This is a timestamp-format/source-processing difference, not a price discrepancy.
- **M-05, Northbound:** the holding percentage is official and High confidence, but observed at 2026-06-30. HKEX also warns that its percentage denominator may lag corporate actions, so the displayed percentage is retained rather than recomputed.
