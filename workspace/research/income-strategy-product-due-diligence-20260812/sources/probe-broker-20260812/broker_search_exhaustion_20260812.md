# Broker/Street Search Exhaustion Log

**Case:** `income-strategy-product-due-diligence-20260812`  
**Search date:** 2026-08-12  
**Cut-off:** 2026-08-12  
**Purpose:** locate dated, auditable sell-side research for every named product. This log is an evidence-boundary record, not a statement that no sell-side research exists in paid terminals or broker client systems.

## Acceptance rule

A report can become a valuation/Street anchor only when the research team has an archived original broker PDF or a broker-official page that identifies the broker, date, product, rating (if any), target/return metric (if any), forecast (if any), method and source path. A search-result snippet, media repost, upload-site preview, aggregator abstract, encrypted download page or a report without an actionable valuation field is retained for discovery only and receives zero valuation weight.

## Search matrix

| Product | Reproducible search URL | Result and exhaustion finding | Status | Evidence path |
|---|---|---|---|---|
| `511010` 国泰上证5年期国债ETF | [search](https://www.google.com/search?q=511010+%E5%9B%BD%E6%B3%B0%E4%B8%8A%E8%AF%815%E5%B9%B4%E6%9C%9F%E5%9B%BD%E5%80%BAETF+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | Searches surfaced fund legal disclosures and market-data pages, not a dated original sell-side product note with an auditable target/forecast/method. | `not_found_for_valuation` | this log; `data/broker_street_consensus_20260812.json` row `NF-511010` |
| `510880` 华泰柏瑞上证红利ETF | [search](https://www.google.com/search?q=510880+%E5%8D%8E%E6%B3%B0%E6%9F%8F%E7%91%9E%E4%B8%8A%E8%AF%81%E7%BA%A2%E5%88%A9ETF+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | Searches surfaced fund disclosures, fund-data pages and ETF industry reports, not a dated original product-specific broker valuation packet. | `not_found_for_valuation` | this log; row `NF-510880` |
| `512890` 华泰柏瑞中证红利低波ETF | [search](https://www.google.com/search?q=512890+%E7%BA%A2%E5%88%A9%E4%BD%8E%E6%B3%A2ETF+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | Searches surfaced exchange ETF-industry material and fund disclosures, not an auditable product-specific broker target/forecast report. | `not_found_for_valuation` | this log; row `NF-512890` |
| `508069` 华夏南京交通高速公路REIT | [search](https://www.google.com/search?q=508069+%E5%8D%8E%E5%A4%8F%E5%8D%97%E4%BA%AC%E4%BA%A4%E9%80%9A%E9%AB%98%E9%80%9FREIT+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | Searches returned fund announcements and media summaries. No archived original broker note meeting the anchor rule was obtained. | `not_found_for_valuation` | this log; row `NF-508069` |
| `508011` 嘉实物美消费REIT | [search](https://www.google.com/search?q=508011+%E5%98%89%E5%AE%9E%E7%89%A9%E7%BE%8E%E6%B6%88%E8%B4%B9REIT+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | A 财信证券 original PDF was recovered, but it is a 2025-03-31 market tracking note. It contains historical observations only—no individual rating, target, forward forecast or valuation method for this product. | `context_only_no_anchor` | `../broker-reports/2026-08-12/01-caixin-key-reits-annual-tracking-20250331.pdf` |
| `508068` 华夏北京保障房REIT | [search](https://www.google.com/search?q=508068+%E5%8D%8E%E5%A4%8F%E5%8C%97%E4%BA%AC%E4%BF%9D%E9%9A%9C%E6%88%BFRIET+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | Searches returned fund announcements and media commentary, but no original broker research packet was obtained. | `not_found_for_valuation` | this log; row `NF-508068` |
| `508077` 华夏华润有巢REIT | [search](https://www.google.com/search?q=508077+%E5%8D%8E%E6%B6%A6%E6%9C%89%E5%B7%A2REIT+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | CICC 2025-results and 申万宏源 expansion-analysis pages were found as media/third-party reprints or previews. Neither original broker PDF nor a broker-official full record was obtained. | `weak_context_only` | `../broker-reports/2026-08-12/03-cicc-508077-2025-results-20260331.html`; `04-swhy-508077-expansion-20251127.html` |
| `508055` 汇添富上海地产租赁住房REIT | [search](https://www.google.com/search?q=508055+%E6%B1%87%E6%B7%BB%E5%AF%8C%E4%B8%8A%E6%B5%B7%E5%9C%B0%E4%BA%A7%E7%A7%9F%E8%B5%81%E4%BD%8F%E6%88%BFREIT+%E7%94%B3%E4%B8%87%E5%AE%8F%E6%BA%90+%E7%94%B3%E8%B4%AD%E4%BB%B7%E5%80%BC%E5%88%86%E6%9E%90) | A 2025 IPO-era 申万宏源 preview/repost was found. It is not a current broker official document and cannot be used as a current valuation anchor. | `weak_context_only` | `../broker-reports/2026-08-12/05-swhy-508055-ipo-analysis-20250311.html` |
| `508080` 中金亦庄产业园REIT | [search](https://www.google.com/search?q=508080+%E4%B8%AD%E9%87%91%E4%BA%A6%E5%BA%84%E4%BA%A7%E4%B8%9A%E5%9B%ADREIT+%E8%B4%A2%E4%BF%A1%E8%AF%81%E5%88%B8+%E7%AE%80%E8%A6%81%E5%88%86%E6%9E%90) | A 财信证券 morning-note media repost was archived. It is IPO-period context, contains no current target/forecast/method packet, and is zero-weight. | `context_only_no_anchor` | `../broker-reports/2026-08-12/02-caixin-morning-508080-20250605.html` |
| `508096` 中航京能国际能源REIT | [search](https://www.google.com/search?q=508096+%E4%B8%AD%E8%88%AA%E4%BA%AC%E8%83%BD%E5%9B%BD%E9%99%85%E8%83%BD%E6%BA%90REIT+%E5%88%B8%E5%95%86+%E7%A0%94%E6%8A%A5+2025+2026) | Searches surfaced fund disclosures and media coverage of the expansion/name change, not an auditable product-specific broker valuation report. | `not_found_for_valuation` | this log; row `NF-508096` |

## Broadened sector searches

| Query / source | Result | Treatment |
|---|---|---|
| [招商证券 REITs 26M5 market review](https://m.hibor.com.cn/wap_detail.aspx?id=a196eb337814c54b841d24e8796db354) | Public third-party summary of a 2026-06-17 sector report. It is sector context, not a valuation report for any of the ten products. | Archived HTML, `third_party_abstract`, zero weight. |
| [申万宏源 2026 April REITs market report](https://www.nxny.com/report/view_6287854.html) | Third-party listing reports a login/encryption restriction; visible summary is not a complete original broker report. | Archived landing page, `third_party_listing`, zero weight. |
| [平安证券 commercial REIT overview](https://www.nxny.com/report/view_6234198.html) | Search result identified the 2026-03-12 report but the direct retrieval returned a site “page not found” response. | Failed response archived as `08-pingan-commercial-reit-overview-20260312-404.html`; zero weight. |

## Direct-download recovery attempt

The direct `pdf.dfcfw.com` URL for the 财信证券 2025-03-31 report first returned an anti-bot JavaScript page; that response is preserved as `01-caixin-direct-pdf-fetch-20250331.html`. A retry with the provider’s `?download=1` parameter returned a valid 6-page PDF, which is archived in `../broker-reports/2026-08-12/`. That recovery changes only the source availability for the historical 508011 context note; it does not create an actionable broker valuation anchor.

## Required next source for a positive Street weight

For any product to receive a non-zero external valuation/Street weight, archive the original broker PDF or broker-official research page and verify, in the same artifact, the product identifier, report date, analyst/broker, rating or stance, a current target/return input, forward cash-flow/earnings assumption where applicable, valuation methodology, and the report’s risk disclosure. Until then every named product has `valuation_weight = 0`.
