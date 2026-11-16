# Broker Report Collection — Income Strategy Product Universe

**Collection date:** 2026-08-12  
**Coverage:** all 10 named products in `data/product_universe_20260812.json`  
**Search window:** 2025-01-01 to 2026-08-12, with a focused current-window search in 2026  
**Collection status:** `source_exhausted_for_public_access; no_usable_street_anchor`

## Collection outcome

| Metric | Count | Meaning |
|---|---:|---|
| Named products screened | 10 | 511010, 510880, 512890 and seven public REITs. |
| Product-specific research references recovered | 5 | One original PDF plus four reprint/preview pages. |
| Sector-context research references recovered | 3 | Not individual-product valuation research. |
| Original broker PDFs archived | 1 | 财信证券 2025-03-31; historical 508011 tracking context only. |
| Public original/official reports meeting the full valuation-anchor standard | 0 | No row has a usable current rating, target/return input, forecast and method. |
| Positive external valuation weights | 0 | Mandatory zero-weight treatment. |

This directory deliberately distinguishes *a page that mentions a broker* from an original, dated, auditable broker source. It contains no reconstructed rating, target price, earnings estimate or consensus calculation.

## Recovered sources

| ID | Broker / source | Title | Report date | Product relevance | Form and local record | Anchor status |
|---|---|---|---|---|---|---|
| 01 | 财信证券 | 重点公募REITs年报跟踪 | 2025-03-31 | `508011` historical operating/market observation | [PDF](./01-caixin-key-reits-annual-tracking-20250331.pdf), [text extraction](./01-caixin-key-reits-annual-tracking-20250331.txt) | Original PDF, but no product rating, target, forecast or valuation method; zero weight. |
| 02 | 财信证券 | 晨会报告：中金亦庄产业园REIT简要分析 | 2025-06-05 | `508080` IPO-period context | [archived media repost](./02-caixin-morning-508080-20250605.html) | Repost; no current target/forecast/method; zero weight. |
| 03 | 中金公司 | 华夏基金华润有巢REIT：2025年业绩符合市场预期，关注后续租金走势 | 2026-03-31 | `508077` | [archived media repost](./03-cicc-508077-2025-results-20260331.html) | Repost rather than original broker delivery; zero weight. |
| 04 | 申万宏源 | 华夏华润有巢REIT：扩募价值深度分析 | 2025-11-27 | `508077` | [archived media repost](./04-swhy-508077-expansion-20251127.html) | Repost rather than original broker delivery; zero weight. |
| 05 | 申万宏源 | 汇添富上海地产租赁住房REIT申购价值分析 | 2025-03-11 | `508055` IPO-period context | [archived third-party preview](./05-swhy-508055-ipo-analysis-20250311.html) | Third-party preview, not current and not an original broker archive; zero weight. |
| 06 | 招商证券 | REITs行业26M5市场回顾及最新观点 | 2026-06-17 | Sector context | [archived third-party abstract](./06-cmb-reits-may-market-review-20260617.html) | Sector-only third-party abstract; zero weight. |
| 07 | 申万宏源 | 2026年公募REITs市场4月报 | 2026-05-08 | Sector context | [archived third-party listing](./07-swhy-reits-april-market-report-20260508.html) | Encryption/login-restricted listing; zero weight. |
| 08 | 平安证券 | 地产行业收租资产系列报告之十二：首批商业不动产REITs资产评估总览 | 2026-03-12 | Sector context | Failed direct retrieval is in [probe archive](../../probe-broker-20260812/08-pingan-commercial-reit-overview-20260312-404.html) | No usable source retrieved; zero weight. |

## Product-level Street-anchor status

| Product | Recovered material | Formal Street target / forecast / method | External valuation weight | Conclusion |
|---|---|---|---:|---|
| `511010` 国泰上证5年期国债ETF | None meeting product-specific research standard | not disclosed | 0 | No Street anchor. |
| `510880` 华泰柏瑞上证红利ETF | None meeting product-specific research standard | not disclosed | 0 | No Street anchor. |
| `512890` 华泰柏瑞中证红利低波ETF | None meeting product-specific research standard | not disclosed | 0 | No Street anchor. |
| `508069` 华夏南京交通高速公路REIT | None meeting product-specific research standard | not disclosed | 0 | No Street anchor. |
| `508011` 嘉实物美消费REIT | 2025 财信 historical tracking PDF | not disclosed | 0 | Context only; no current valuation anchor. |
| `508068` 华夏北京保障房REIT | None meeting product-specific research standard | not disclosed | 0 | No Street anchor. |
| `508077` 华夏华润有巢REIT | CICC and 申万宏源 reprints/previews | not disclosed in formal packet | 0 | Weak context only; no current original/official anchor. |
| `508055` 汇添富上海地产租赁住房REIT | 2025 申万宏源 IPO preview | not disclosed in formal packet | 0 | Stale preview only; no current anchor. |
| `508080` 中金亦庄产业园REIT | 2025 财信 media repost | not disclosed in formal packet | 0 | IPO context only; no current anchor. |
| `508096` 中航京能国际能源REIT | None meeting product-specific research standard | not disclosed | 0 | No Street anchor. |

## Consensus quick view

There is no usable cross-broker consensus for this universe. “Bullish / neutral / bearish” counts, target-price averages, forecast ranges and implied-upside averages are intentionally **not calculated**. The public excerpts and previews are discovery leads only and are not a portfolio-selection input.

See [the formal catalog](../../../data/report_catalog.md), [the machine-readable zero-weight packet](../../../data/broker_street_consensus_20260812.json), and [the source-exhaustion log](../../probe-broker-20260812/broker_search_exhaustion_20260812.md).
