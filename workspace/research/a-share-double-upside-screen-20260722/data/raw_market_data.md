# Raw Market Data Capture

## Scope and provenance

- Market cutoff: **2026-07-22 close**.
- Universe: the 15 names in `research_brief.md`, plus `002497` (added to the deep-model pool during the research cycle).
- Close-price source 1: project-native `.venv/bin/python -m astock.cli market-snapshot <codes> --json`, whose market stream is Sina-backed. Initial-universe capture time was `2026-07-22 16:19:06 CST`; `002497` was captured at `16:27:24 CST`. Per-security tick timestamps were `15:34:59` to `15:36:00`, after the continuous auction close.
- Close-price, capitalization, and share-count source 2: Tencent Finance batch quote `https://qt.gtimg.cn/`, retrieved at approximately `2026-07-22 16:20 CST` for the initial universe and `16:27 CST` for `002497`; quote timestamps were `16:14:03` to `16:14:57`. Tencent and AStock/Sina close prices matched for all **16/16** names.
- Ten-session price/volume source: Tencent forward-adjusted daily K-line endpoint `https://web.ifzq.gtimg.cn/appstock/app/fqkline/get`, retrieved `2026-07-22 16:33 CST`. The response supplied `qfqday` through `2026-07-21`; the `2026-07-22` row is the same response's closing `qt` field. Tencent volume is in 100-share lots for all six names and is normalized below to million shares.
- Market capitalizations below are recomputed as `close x shares`. Tencent's displayed CNY100m market-cap fields agree after quote rounding.
- “Circulating shares” is the provider's unrestricted/circulating-share field, **not** an MSCI-style free-float measure. It does not identify strategic holdings or lock-up expiry dates.

## 2026-07-22 closing snapshot

| Ticker | Company | Close | Prev. close | Change | High / low | Volume (m shares) | Amount (CNYbn) | Sina tick time |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 600150 | 中国船舶 | CNY33.02 | 32.96 | +0.18% | 33.80 / 32.67 | 108.370 | 3.604 | 15:34:59 |
| 301308 | 江波龙 | CNY388.45 | 421.86 | -7.92% | 429.53 / 386.97 | 25.815 | 10.575 | 15:35:30 |
| 002812 | 恩捷股份 | CNY47.84 | 50.01 | -4.34% | 49.92 / 47.44 | 23.816 | 1.152 | 15:35:45 |
| 002240 | 盛新锂能 | CNY27.65 | 27.39 | +0.95% | 28.38 / 26.86 | 48.743 | 1.351 | 15:35:30 |
| 300390 | 天华新能 | CNY55.88 | 55.82 | +0.11% | 57.16 / 54.50 | 35.131 | 1.968 | 15:35:45 |
| 002460 | 赣锋锂业 | CNY47.43 | 47.69 | -0.55% | 48.54 / 46.95 | 42.806 | 2.043 | 15:35:45 |
| 000623 | 吉林敖东 | CNY18.31 | 18.47 | -0.87% | 18.55 / 18.15 | 16.962 | 0.311 | 15:35:30 |
| 600739 | 辽宁成大 | CNY10.92 | 10.99 | -0.64% | 11.02 / 10.78 | 16.913 | 0.184 | 15:34:59 |
| 002432 | 九安医疗 | CNY81.64 | 79.75 | +2.37% | 85.06 / 79.20 | 82.314 | 6.771 | 15:35:45 |
| 000685 | 中山公用 | CNY10.73 | 10.92 | -1.74% | 10.84 / 10.65 | 22.554 | 0.242 | 15:35:15 |
| 002648 | 卫星化学 | CNY24.48 | 23.82 | +2.77% | 24.87 / 23.70 | 64.659 | 1.580 | 15:36:00 |
| 000703 | 恒逸石化 | CNY15.16 | 14.64 | +3.55% | 15.43 / 14.33 | 92.035 | 1.381 | 15:35:15 |
| 600673 | 东阳光 | CNY29.50 | 30.41 | -2.99% | 31.35 / 29.05 | 65.062 | 1.964 | 15:34:59 |
| 600183 | 生益科技 | CNY126.00 | 135.67 | -7.13% | 140.19 / 124.06 | 82.386 | 10.952 | 15:34:59 |
| 002916 | 深南电路 | CNY337.98 | 350.00 | -3.43% | 366.98 / 334.00 | 12.545 | 4.412 | 15:35:30 |
| 002497 | 雅化集团 | CNY16.79 | 16.91 | -0.71% | 17.12 / 16.56 | 40.857 | 0.688 | 15:35:15 |

## Share-count and capitalization inputs

| Ticker | Total shares | Circulating shares / proxy | Total MCap | Circulating MCap proxy | Share-count provenance |
|---|---:|---:|---:|---:|---|
| 600150 | 7,525,621,288 | 7,525,621,288 | CNY248.496015bn | CNY248.496015bn | Official 2025 distribution implementation, base at 2026-07-20; Tencent matched |
| 301308 | 423,061,007 | 281,851,892 | CNY164.338048bn | CNY109.485367bn | Official 2026-05-26 distribution announcement confirms total shares after 3,915,740-share vesting; circulating is Tencent proxy |
| 002812 | 981,318,518 | 822,610,868 | CNY46.946278bn | CNY39.353704bn | Official 2026-07-22 cancellation-completion announcement; both counts matched Tencent |
| 002240 | 915,293,872 | 912,908,722 | CNY25.307876bn | CNY25.241926bn | Official 2026Q1 report total shares; circulating is Tencent proxy |
| 300390 | 830,750,788 | 672,267,581 | CNY46.422354bn | CNY37.566312bn | Official 2026Q1 report total shares; circulating is Tencent proxy |
| 002460 | 2,096,694,404 | 1,211,218,038 | CNY99.446216bn | CNY57.448072bn | Tencent quote; total-share capitalization at A-share close is a proxy for an A+H issuer |
| 000623 | 1,195,895,387 | 1,190,966,462 | CNY21.896845bn | CNY21.806596bn | Tencent quote |
| 600739 | 1,522,315,928 | 1,522,315,928 | CNY16.623690bn | CNY16.623690bn | Tencent quote |
| 002432 | 465,893,881 | 465,272,320 | CNY38.035576bn | CNY37.984832bn | Tencent quote |
| 000685 | 1,467,731,130 | 1,246,581,940 | CNY15.748755bn | CNY13.375824bn | Tencent quote |
| 002648 | 3,368,645,690 | 3,366,482,485 | CNY82.464446bn | CNY82.411491bn | Tencent quote |
| 000703 | 3,821,562,147 | 3,802,389,897 | CNY57.934882bn | CNY57.644231bn | Tencent quote; official 2026-06-30 total shares are also archived in the separate `hengyi-petrochemical-000703-20260722` case |
| 600673 | 3,009,555,059 | 3,001,557,927 | CNY88.781874bn | CNY88.545959bn | Tencent quote |
| 600183 | 2,429,003,670 | 2,394,501,544 | CNY306.054462bn | CNY301.707195bn | Tencent quote |
| 002916 | 681,166,595 | 664,809,450 | CNY230.220686bn | CNY224.692298bn | Tencent quote |
| 002497 | 1,152,562,520 | 1,059,587,615 | CNY19.351525bn | CNY17.790476bn | Official 2026Q1 report total shares; circulating is Tencent proxy |

## Ten-session forward-adjusted closes and volume

| Ticker | Date | Close | Volume (m shares) |
|---|---|---:|---:|
| 600150 | 2026-07-09 | 35.695 | 114.679 |
| 600150 | 2026-07-10 | 36.675 | 194.667 |
| 600150 | 2026-07-13 | 33.845 | 216.601 |
| 600150 | 2026-07-14 | 33.405 | 150.839 |
| 600150 | 2026-07-15 | 33.945 | 99.521 |
| 600150 | 2026-07-16 | 32.635 | 122.150 |
| 600150 | 2026-07-17 | 31.975 | 93.956 |
| 600150 | 2026-07-20 | 33.010 | 99.899 |
| 600150 | 2026-07-21 | 32.960 | 93.280 |
| 600150 | 2026-07-22 | 33.020 | 108.370 |
| 301308 | 2026-07-09 | 620.000 | 20.171 |
| 301308 | 2026-07-10 | 587.600 | 19.252 |
| 301308 | 2026-07-13 | 522.040 | 18.022 |
| 301308 | 2026-07-14 | 538.510 | 16.790 |
| 301308 | 2026-07-15 | 488.000 | 22.791 |
| 301308 | 2026-07-16 | 463.590 | 17.096 |
| 301308 | 2026-07-17 | 396.000 | 22.790 |
| 301308 | 2026-07-20 | 376.490 | 19.677 |
| 301308 | 2026-07-21 | 421.860 | 25.932 |
| 301308 | 2026-07-22 | 388.450 | 25.815 |
| 002812 | 2026-07-09 | 59.330 | 44.973 |
| 002812 | 2026-07-10 | 54.800 | 51.675 |
| 002812 | 2026-07-13 | 52.630 | 29.088 |
| 002812 | 2026-07-14 | 53.700 | 22.687 |
| 002812 | 2026-07-15 | 54.960 | 24.792 |
| 002812 | 2026-07-16 | 51.330 | 24.897 |
| 002812 | 2026-07-17 | 50.160 | 23.720 |
| 002812 | 2026-07-20 | 48.000 | 26.019 |
| 002812 | 2026-07-21 | 50.010 | 24.748 |
| 002812 | 2026-07-22 | 47.840 | 23.816 |
| 002240 | 2026-07-09 | 35.550 | 87.992 |
| 002240 | 2026-07-10 | 34.100 | 67.278 |
| 002240 | 2026-07-13 | 32.190 | 47.649 |
| 002240 | 2026-07-14 | 33.080 | 41.292 |
| 002240 | 2026-07-15 | 31.110 | 45.619 |
| 002240 | 2026-07-16 | 30.170 | 44.308 |
| 002240 | 2026-07-17 | 28.880 | 44.771 |
| 002240 | 2026-07-20 | 25.990 | 55.408 |
| 002240 | 2026-07-21 | 27.390 | 62.907 |
| 002240 | 2026-07-22 | 27.650 | 48.743 |
| 300390 | 2026-07-09 | 69.100 | 97.624 |
| 300390 | 2026-07-10 | 65.700 | 74.789 |
| 300390 | 2026-07-13 | 64.060 | 46.311 |
| 300390 | 2026-07-14 | 64.650 | 44.725 |
| 300390 | 2026-07-15 | 60.010 | 52.376 |
| 300390 | 2026-07-16 | 59.010 | 41.604 |
| 300390 | 2026-07-17 | 57.020 | 44.175 |
| 300390 | 2026-07-20 | 53.330 | 53.025 |
| 300390 | 2026-07-21 | 55.820 | 46.996 |
| 300390 | 2026-07-22 | 55.880 | 35.131 |
| 002497 | 2026-07-09 | 20.200 | 122.951 |
| 002497 | 2026-07-10 | 18.700 | 110.627 |
| 002497 | 2026-07-13 | 18.120 | 71.316 |
| 002497 | 2026-07-14 | 18.670 | 70.999 |
| 002497 | 2026-07-15 | 18.070 | 52.057 |
| 002497 | 2026-07-16 | 17.450 | 56.560 |
| 002497 | 2026-07-17 | 17.140 | 70.408 |
| 002497 | 2026-07-20 | 16.290 | 71.892 |
| 002497 | 2026-07-21 | 16.910 | 58.225 |
| 002497 | 2026-07-22 | 16.790 | 40.857 |

## Raw-source limitations

- Neither Sina nor Tencent is the exchange's official closing-price archive; the identical two-source close is therefore rated medium-high rather than exchange-official high confidence.
- Tencent's K-line labels the history `qfqday`; the final session is taken from the response's closing quote because the historical array stopped at `2026-07-21` even though the market-status field stated both exchanges were closed.
- `600150` paid CNY0.365/share on `2026-07-20`; its price-only interval return is not a shareholder total return. The official implementation announcement is archived in `sources/official-20260722/`.
- Price declines are observations of market repricing and position reduction. They do not, by themselves, prove deterioration in orders, demand, margins, or earnings.
- Northbound holdings were not collected here because no current official HKEX observation for `2026-07-22` was available; no broker or aggregator estimate is substituted.
