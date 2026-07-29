# Verified Market Data — 2026-07-22 Close

## Verification result

- Close prices: **16/16 matched** between the project-native AStock/Sina snapshot and Tencent's post-close quote.
- Deep-model total shares: **6/6 reconciled** to official filings or share-change announcements. Circulating shares remain a provider proxy except for `002812`, whose 2026-07-22 official announcement disclosed both restricted and unrestricted counts.
- Market-cap arithmetic: **16/16 reconciled** as `close x shares` within Tencent's CNY100m display-rounding tolerance.
- Ten-session audit: Tencent `qfqday` plus the same response's 2026-07-22 closing quote covered ten sessions from `2026-07-09` through `2026-07-22` for all six deep-model names.

## Verified screen table

| Ticker | Company | Close | Total MCap | Circulating MCap proxy | Total-share evidence | Confidence |
|---|---|---:|---:|---:|---|---|
| 600150 | 中国船舶 | CNY33.02 | CNY248.496bn | CNY248.496bn | Official at 2026-07-20 | Price medium-high; shares high |
| 301308 | 江波龙 | CNY388.45 | CNY164.338bn | CNY109.485bn | Official at 2026-05-26 | Price medium-high; total shares high |
| 002812 | 恩捷股份 | CNY47.84 | CNY46.946bn | CNY39.354bn | Official at 2026-07-22 | Price medium-high; shares high |
| 002240 | 盛新锂能 | CNY27.65 | CNY25.308bn | CNY25.242bn | Official 2026Q1; no later share-change hit through cutoff | Price medium-high; total shares medium-high |
| 300390 | 天华新能 | CNY55.88 | CNY46.422bn | CNY37.566bn | Official 2026Q1; no later share-change hit through cutoff | Price medium-high; total shares medium-high |
| 002497 | 雅化集团 | CNY16.79 | CNY19.352bn | CNY17.790bn | Official 2026Q1; no later share-change hit through cutoff | Price medium-high; total shares medium-high |
| 002460 | 赣锋锂业 | CNY47.43 | CNY99.446bn | CNY57.448bn | Tencent quote | Medium; A+H total-cap proxy caveat |
| 000623 | 吉林敖东 | CNY18.31 | CNY21.897bn | CNY21.807bn | Tencent quote | Medium |
| 600739 | 辽宁成大 | CNY10.92 | CNY16.624bn | CNY16.624bn | Tencent quote | Medium |
| 002432 | 九安医疗 | CNY81.64 | CNY38.036bn | CNY37.985bn | Tencent quote | Medium |
| 000685 | 中山公用 | CNY10.73 | CNY15.749bn | CNY13.376bn | Tencent quote | Medium |
| 002648 | 卫星化学 | CNY24.48 | CNY82.464bn | CNY82.411bn | Tencent quote | Medium |
| 000703 | 恒逸石化 | CNY15.16 | CNY57.935bn | CNY57.644bn | Tencent matched separate official case evidence | Medium-high total shares |
| 600673 | 东阳光 | CNY29.50 | CNY88.782bn | CNY88.546bn | Tencent quote | Medium |
| 600183 | 生益科技 | CNY126.00 | CNY306.054bn | CNY301.707bn | Tencent quote | Medium |
| 002916 | 深南电路 | CNY337.98 | CNY230.221bn | CNY224.692bn | Tencent quote | Medium |

## Ten-session drawdown and volume audit

| Ticker | 2026-07-09 close | 2026-07-22 close | Start-to-end | Peak-to-trough close drawdown | 10d avg volume | 7/22 volume / 10d avg |
|---|---:|---:|---:|---:|---:|---:|
| 600150 | CNY35.695 | CNY33.02 | -7.49% | -12.82% (`36.675` to `31.975`) | 129.396m shares/day | 0.84x |
| 301308 | CNY620.00 | CNY388.45 | -37.35% | -39.28% (`620.00` to `376.49`) | 20.833m shares/day | 1.24x |
| 002812 | CNY59.33 | CNY47.84 | -19.37% | -19.37% (`59.33` to `47.84`) | 29.641m shares/day | 0.80x |
| 002240 | CNY35.55 | CNY27.65 | -22.22% | -26.89% (`35.55` to `25.99`) | 54.597m shares/day | 0.89x |
| 300390 | CNY69.10 | CNY55.88 | -19.13% | -22.82% (`69.10` to `53.33`) | 53.676m shares/day | 0.65x |
| 002497 | CNY20.20 | CNY16.79 | -16.88% | -19.36% (`20.20` to `16.29`) | 72.589m shares/day | 0.56x |

## Interpretation boundary

The table verifies a rapid price and valuation compression over ten sessions, especially for `301308` and the lithium complex. It is consistent with fast position reduction or de-leveraging, but the market tape alone cannot identify the seller, financing channel, or fundamental cause. No sentence in the report should convert these returns mechanically into “earnings deterioration.” Fundamentals must be assessed separately from official earnings and operating disclosures.

Additional cautions:

- `600150` went ex-dividend for CNY0.365/share on 2026-07-20; the -7.49% price-only comparison is not total shareholder return.
- `002812` completed an 813,379-share restricted-stock cancellation on 2026-07-21. The current total-share count is 981,318,518, not the 982,131,897 shown in its 2026Q1 report.
- `301308` added 3,915,740 shares through restricted-stock vesting on 2026-05-18; the current total is 423,061,007 rather than the 419,145,267 quarter-end count.
- Circulating market capitalization remains an unrestricted-share proxy, not regulatory or index free float.
