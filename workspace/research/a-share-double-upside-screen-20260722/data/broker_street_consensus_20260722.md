# Broker / Street Consensus Packet — 2026-07-22

## Governance boundary

This packet contains the two auditable original broker point targets with complete rating, forecasts, EPS, and valuation method. Target evidence completeness is separate from house valuation eligibility: `002497` receives a capped 0.10 external-anchor weight, while `002812` receives zero weight because its company-driver valuation gate is blocked. The source archive has 14 original PDFs across six names; the target gaps for `600150`, `301308`, `002240`, and `300390` are kept in `data/report_catalog.md` and `data/consensus_analysis.md`.

Both target-price reports leave the target horizon undisclosed. The valuation year (`2026E` or `2027E`) is not evidence that the target is specifically for 2026-12-31. Neither row is an explicit year-end target.

## Auditable point-target anchors

| Ticker | Broker | Report / publish date | Rating | Target | Forecasts (CNY mn; EPS CNY) | Method | 2026-07-22 price | Implied upside | Horizon / year-end status | Weight |
|---|---|---|---|---:|---|---|---:|---:|---|---:|
| 002497 雅化集团 | 东吴证券 | 2026-07-07 / 2026-07-08 | 买入（维持） | CNY42 | 2026E: revenue 17,052; NP 3,031.65; EPS 2.63. 2027E: revenue 22,215; NP 3,575.28; EPS 3.10. | 2026E EPS CNY2.63 × 16x PE = CNY42.08, rounded to CNY42. | CNY16.79 | +150.15% | Horizon not disclosed; not an explicit year-end target. | 0.10 |
| 002812 恩捷股份 | 东吴证券 | 2026-07-10 / 2026-07-10 | 买入（维持） | CNY103 | 2026E: revenue 20,058; NP 2,279.37; EPS 2.32. 2027E: revenue 31,115; NP 5,068.27; EPS 5.16. | 2027E EPS CNY5.16 × 20x PE = CNY103.20, rounded to CNY103. | CNY47.84 | +115.30% | Horizon not disclosed; company-driver valuation gate blocked. | 0.00 |

## Original evidence

- `002497`: [Eastmoney detail](https://data.eastmoney.com/report/zw_stock.jshtml?infocode=AP202607071826780391), [direct original PDF](https://pdf.dfcfw.com/pdf/H3_AP202607071826780391_1.pdf), local PDF `sources/broker-reports/2026-07-22/002497-雅化集团/2026-07-08-东吴证券-26H1业绩预告点评-Q2锂盐量利齐升-略超我们预期.pdf`, extracted text beside it.
- `002812`: [Eastmoney detail](https://data.eastmoney.com/report/zw_stock.jshtml?infocode=AP202607101826872306), [direct original PDF](https://pdf.dfcfw.com/pdf/H3_AP202607101826872306_1.pdf), local PDF `sources/broker-reports/2026-07-22/002812-恩捷股份/2026-07-10-东吴证券-26H1业绩预告点评-Q2业绩超我们预期-隔膜供需紧张盈利持续提升.pdf`, extracted text beside it.

The public metadata snapshots are archived under `sources/broker-reports/2026-07-22/metadata/`. Quote references came from `astock.quote_service` at 2026-07-22 16:29:49 CST for `002497` and 16:21:37 CST for `002812`, both marked `full_realtime`.

## Decision boundary

- The two targets mechanically clear +100% versus the captured 2026-07-22 prices.
- This does not prove a high-confidence base-case double by 2026 year-end: the reports do not define a year-end horizon, and the valuation years differ.
- The arithmetic average of CNY72.50 has no cross-company valuation meaning and is not used.
