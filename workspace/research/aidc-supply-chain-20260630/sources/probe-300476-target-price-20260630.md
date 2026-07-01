# Probe: 300476 Target-Price Evidence

**Probe date:** 2026-06-30  
**Ticker:** 300476  
**Company:** 胜宏科技  
**Purpose:** Verify whether a public, auditable broker target price can support the broker/Street consensus row.

## Probe Results

| Source | Result | Usability |
|---|---|---|
| Eastmoney report API, 2022-01-01 to 2026-06-30 | 39 public report rows checked; 0 rows expose `indvAimPriceL` or `indvAimPriceT`. | Original public broker-report corpus does not disclose target price. |
| Archived Eastmoney PDF `sources/broker-reports/2026-06-30/07-01-300476-report-2026q1.pdf` | Rating, 2026E revenue, net profit, EPS and PE table are available; explicit target price is not disclosed. | Usable for forecasts; not usable for target price or implied upside. |
| Moomoo article on JPMorgan H-share target | Mentions JPMorgan H-share target HKD600. | Different share class/currency and no full original report in case corpus; do not use for A-share target row. |
| Investing.com analyst target page | Shows third-party aggregate target range/average. | Aggregated third-party consensus without broker report identities; not a substitute for original broker evidence. |
| Wallstreetcn media summary on Citi target | Mentions Citi target CNY447. | Media summary/paywall-style repost; not an original broker PDF or official page. |
| Securities Times / Sina / CLS reports on Goldman target rumor | State that alleged Goldman target-price report was not verified or reportedly not issued. | Negative evidence; prevents using rumor-based Goldman target prices. |
| 同花顺 iNews / iFinD 2026-04-29 article | Public iFinD table lists broker identities and target rows: 中信证券 2026-04-23 target 360.0000 and 国投证券 2025-10-30 target 403.4200; recent-six-month target range/average is 360.00 / 403.42 / 381.71. | Usable as an auditable A-share consensus snapshot; label `source_quality=auditable_consensus_snapshot`, not `original_pdf`. |

## Decision

Keep the Eastmoney original-PDF row as forecast evidence only because the 39-report public API/PDF full scan found no explicit target price. Populate `target_price=381.71`, `target_price_range=360.00-403.42`, and computed `implied_upside` from `sources/probe-300476-ifind-consensus-20260630/index.md`. Set `source_quality=auditable_consensus_snapshot` and `valuation_weight=0.10`. Do not populate this field from media reposts, search snippets, H-share targets, or unverified Goldman/Citi rumors.
## Eastmoney Full Public-Report Scan

- Scan path: `sources/probe-300476-eastmoney-fullscan-20260630/`
- Date range: 2022-01-01 to 2026-06-30
- Reports scanned: 39
- API target rows: 0
- PDF explicit target rows: 0
- Verdict: no explicit public A-share broker target price found in this Eastmoney full scan
