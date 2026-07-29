# Disclosure-time and market-event audit — 雅化集团（002497.SZ）

## Decision

**The 2026H1 earnings-preview disclosure date is confirmed as 2026-07-07; its exact intraday publication time is not confirmed by the archived evidence.** The report may show the subsequent trading window, but must not state or imply that the 2026-07-07 limit-up was caused by this notice.

| Audit field | Evidence | Result | Permitted wording |
|---|---|---|---|
| Issuer document | `FIN-26H1P`, primary PDF, board date 2026-07-06 | Confirmed | “公司于 7 月 7 日披露 2026H1 业绩预告。” |
| CNINFO catalogue date | `DISC-CNINFO-H1`, official query response | Confirmed | The catalogue lists the notice with `announcementTime_epoch_ms=1783353600000`, mechanically converting to 2026-07-07 00:00:00 China Standard Time. |
| Exact publication time | Primary PDF and query-response metadata | **Not confirmed** | The 00:00:00 catalogue value is date-normalized metadata, not proof of a before-open, intraday, or after-close release time. |
| 2026-07-07 return | `MKT-EVT-0723`, L2 daily bar | Confirmed observation | 雅化 closed at CNY24.65, +10.00% on 7 July. Do not write “公告推动涨停”. |

## Same-window price context

All returns are simple close-to-close calculations from the archived L2 daily bars. The peer basket is equal-weighted and descriptive only.

| Window | 雅化 | 天齐 | 赣锋 | 盛新 | Equal-weight peer basket | 沪深300 | Read-through allowed |
|---|---:|---:|---:|---:|---:|---:|---|
| 2026-07-06 → 2026-07-07 | +10.00% | +0.48% | -2.21% | +2.29% | +0.19% | -1.03% | 雅化当日表现强于三个锂业观察对象和大盘；由于披露时点未证实，不能指定因果。 |
| 2026-07-06 → 2026-07-23 | -20.79% | -21.68% | -19.80% | -26.57% | -22.68% | -2.77% | 锂业相关股票整体显著跑输大盘；雅化相对该三股简单篮子 +1.89 个百分点。 |
| 2026-07-07 → 2026-07-23 | -27.99% | -22.05% | -17.99% | -28.22% | -22.75% | -1.76% | 雅化从 7 月 7 日收盘至 7 月 23 日跑输该篮子 5.24 个百分点。 |

### Required limitations

- This is not an abnormal-return study: no intraday timestamp, factor model, sector index, market-adjusted t-statistic, fund-flow, northbound or financing-balance data is archived.
- It cannot establish that the price change reflects earnings quality, H2 expectations, investor positioning, or an individual news item.
- It is sufficient to reject a simplistic narrative that the market “continued to price the preview positively” through the cutoff: the observable post-7 July path was negative.

Source paths: `sources/rebuild-company-20260723/cninfo_disclosure_probe_20260723.json`, `sources/official-financial-20260723/002497_2026_h1_earnings_preview.pdf`, and `sources/market-data-20260723/eastmoney_event_window_20260706_20260723_raw.json`.
