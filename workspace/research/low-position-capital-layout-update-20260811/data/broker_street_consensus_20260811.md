# Broker / Street Evidence Refresh — 2026-08-11

**Coverage:** 13 tickers. The preferred public-directory window is 2026-04-01 to 2026-08-11. Values below are broker estimates in CNY million except EPS and target price (CNY/share). This is a source packet, not a vendor consensus or a house valuation.

Only archived original broker PDFs with an explicit target receive a non-zero `valuation_weight`. The field is an evidence cap, not a portfolio allocation. Forecast-only reports, public-directory gaps and any unverifiable lead have a weight of zero.

**Important timing label:** the flat JSON field `implied_upside` is the report-date upside stated or reconstructed on each broker report's own date; it is not a refreshed 2026-08-10-close calculation. Refreshed external-reference arithmetic is separately shown in `analysis/valuation_audit.md` and the report appendix: 000703 about -9% to -3%, 002379 about +47%, 300014 about +39%/+87% (not averaged), 002497 about +120%, and 002812 about +84%.

| Ticker | Broker / date | Rating | Target | 2026E revenue / NP / EPS | 2027E revenue / NP / EPS | Source quality | Weight |
|---|---|---|---:|---:|---:|---|---:|
| 000703 | 国信证券, 2026-07-05 | 优于大市（首次） | 16.50–17.60 | 141,736 / 7,910 / 2.20 | 143,521 / 7,800 / 2.16 | Original PDF | 0.10 |
| 002379 | 招银国际, 2026-05-13 | 买入（首次） | 29.00 | 173,916 / 28,208.3* / 2.16 | 171,911 / 26,240.1* / 2.01 | Original PDF | 0.10 |
| 300014 | 东吴证券, 2026-06-16 | 买入（维持） | 103.00 | not disclosed / 7,230 / 3.33 | not disclosed / 9,520 / 4.38 | Original PDF | 0.00 |
| 300014 | 群益证券, 2026-06-26 | 买进 | 77.00 | 95,641 / 6,454 / 3.112 | 122,173 / 8,625 / 4.158 | Original PDF | 0.05 |
| 002497 | 东吴证券, 2026-07-08 | 买入（维持） | 42.00 | 17,052 / 3,031.65 / 2.63 | 22,215 / 3,575.28 / 3.10 | Original PDF | 0.10 |
| 002432 | no current public row | not disclosed | — | — | — | Not found | 0.00 |
| 000623 | no current public row | not disclosed | — | — | — | Not found | 0.00 |
| 600739 | no current public row | not disclosed | — | — | — | Not found | 0.00 |
| 000685 | 国信证券, 2026-05-11 | 优于大市（维持） | not disclosed | 4,884 / 2,145 / 1.45 | 5,010 / 2,378 / 1.61 | Original PDF | 0.00 |
| 600150 | 华源证券, 2026-07-14 | 买入（维持） | not disclosed | 173,501 / 18,198 / 2.42 | 197,304 / 23,538 / 3.13 | Re-scoped local PDF, provenance unverified | 0.00 |
| 301308 | 爱建证券, 2026-05-07 | 买入（维持） | not disclosed | 40,039 / 19,969 / 47.64 | 49,507 / 21,908 / 52.27 | Original PDF | 0.00 |
| 002812 | 东吴证券, 2026-07-10 | 买入（维持） | 103.00 | 20,058 / 2,279.37 / 2.32 | 31,115 / 5,068.27 / 5.16 | Original PDF | 0.10 |
| 002240 | 东吴证券, 2026-07-09 | 买入（维持） | not disclosed | 15,049 / 2,242.53 / 2.45 | 16,200 / 3,003.75 / 3.28 | Original PDF | 0.00 |
| 300390 | 华源证券, 2026-06-06 | 买入（首次） | not disclosed | 21,621 / 4,733 / 5.70 | 24,898 / 5,315 / 6.40 | Re-scoped local PDF, provenance unverified | 0.00 |

\* 招银国际 reports *adjusted net profit*, rather than a directly reconciled company-reported attributable-profit field.

## Usable target evidence

- **000703 — 国信证券:** target range CNY16.50–17.60 from FCFE plus peer P/E. The report forecasts 2026E/2027E revenue of CNY141.736bn/CNY143.521bn and attributable NP of CNY7.910bn/CNY7.800bn. [PDF](../sources/broker-reports/2026-08-11/01-000703-guosen-20260705.pdf) · [text](../sources/broker-reports/2026-08-11/01-000703-guosen-20260705.txt)
- **002379 — 招银国际:** CNY29 target from 13.2x 2026E P/E. The original report says China Hongqiao owns 89% of Hongqiao Holdings after the December 2025 backdoor listing. [PDF](../sources/broker-reports/2026-08-11/02b-002379-cmbi-20260513.pdf) · [text](../sources/broker-reports/2026-08-11/02b-002379-cmbi-20260513.txt)
- **300014 — Dongwu versus Qunyi:** CNY103 (30x 2026E P/E) versus CNY77 (method not disclosed). They are not averaged, because both earnings assumptions and target construction differ. Dongwu is a zero-weight target reference here because its revenue forecasts were not recoverable; Qunyi is the only positive-weight, complete-field row. [Dongwu PDF](../sources/broker-reports/2026-08-11/03-300014-dongwu-20260616.pdf) · [Qunyi PDF](../sources/broker-reports/2026-08-11/04-300014-qunyi-20260626.pdf)
- **002497 — 东吴证券:** CNY42 from 16x 2026E P/E. [PDF](../sources/broker-reports/2026-08-11/05-002497-dongwu-20260708.pdf) · [text](../sources/broker-reports/2026-08-11/05-002497-dongwu-20260708.txt)
- **002812 — 东吴证券:** CNY103 from 20x 2027E P/E. It is retained as a small, original-PDF anchor even though it is outside the four primary candidates. [PDF](../sources/broker-reports/2026-08-11/09-002812-dongwu-20260710.pdf) · [text](../sources/broker-reports/2026-08-11/09-002812-dongwu-20260710.txt)

## Gaps and handling

- 002432, 000623 and 600739 returned **zero** rows in the public Eastmoney directory over the preferred window. This is a public-corpus gap, not proof that licensed/private research does not exist; all broker valuation fields are zero-weight.
- 000685, 301308 and 002240 have current original forecast PDFs but no explicit broker target price in the archived report. They remain forecast references only. 600150 and 300390 are re-scoped local PDFs with incomplete predecessor provenance and remain zero-weight, non-target references.
- 300390’s refreshed public-directory response was empty even though a local June PDF was re-scoped. The zero directory result must not be reinterpreted as proof of zero coverage, and the re-scoped PDF must not be upgraded to primary evidence without predecessor-path and checksum support.
- 301308’s same-date Guosen directory row reports materially lower EPS than the archived Aijian report. This packet preserves that divergence rather than treating either estimate as consensus.

The machine-readable source-of-record is [broker_street_consensus_20260811.json](broker_street_consensus_20260811.json). Its top-level `rows` array is the flat schema consumed by gate-aware valuation tools; a target-bearing archived report with a missing required valuation field is excluded from this array. The detailed `tickers` array preserves the complete report archive and evidence hierarchy, including Dongwu's CNY103 target for 300014. Where visible, `implied_upside` is the broker report-date static figure (or a report-date price/PE calculation), not an August 11 market-price comparison. Failed probes and extraction/indexing limitations are recorded in `sources/probe-20260811/broker_source_exhaustion_log_20260811.*`.
