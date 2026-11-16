# Broker / Street Consensus Packet — Zero-Weight Outcome

**As of:** 2026-08-12  
**Coverage:** 10 named strategy products  
**Formal status:** `no_usable_street_anchor; watchlist_only`

## Control conclusion

The collection did **not** establish an investable sell-side consensus. One original broker PDF was archived for `508011`, but it is a historical tracking note and does not contain a product rating, target, current cash-flow forecast or valuation method. Four individual-product webpages are reposts/previews, and three recovered sector pages are not individual-product valuation reports. Accordingly, every valuation weight is `0.0`; no rating, target, forecast, implied upside or consensus statistic enters the product valuation model.

| Ticker | Product | Best recovered source | Quality | Formal target / forecast / method | Weight | Street-anchor result |
|---|---|---|---|---|---:|---|
| `511010` | 国泰上证5年期国债ETF | No eligible product note recovered | `not_found` | not disclosed | 0.0 | None |
| `510880` | 华泰柏瑞上证红利ETF | No eligible product note recovered | `not_found` | not disclosed | 0.0 | None |
| `512890` | 华泰柏瑞中证红利低波ETF | No eligible product note recovered | `not_found` | not disclosed | 0.0 | None |
| `508069` | 华夏南京交通高速公路REIT | No eligible product note recovered | `not_found` | not disclosed | 0.0 | None |
| `508011` | 嘉实物美消费REIT | 财信证券 2025-03-31 original PDF | `original_pdf_context_only` | not disclosed | 0.0 | Historical context only |
| `508068` | 华夏北京保障房REIT | No eligible product note recovered | `not_found` | not disclosed | 0.0 | None |
| `508077` | 华夏华润有巢REIT | CICC / 申万宏源 reposts | `media_repost` | not disclosed in formal packet | 0.0 | Weak context only |
| `508055` | 汇添富上海地产租赁住房REIT | 申万宏源 IPO preview | `third_party_preview` | not disclosed in formal packet | 0.0 | Stale context only |
| `508080` | 中金亦庄产业园REIT | 财信证券 media repost | `media_repost` | not disclosed in formal packet | 0.0 | IPO context only |
| `508096` | 中航京能国际能源REIT | No eligible product note recovered | `not_found` | not disclosed | 0.0 | None |

The machine-readable source of record is [broker_street_consensus_20260812.json](./broker_street_consensus_20260812.json). The recovered corpus and the failed-probe logic are in [the collection index](../sources/broker-reports/2026-08-12/index.md) and [the exhaustion log](../sources/probe-broker-20260812/broker_search_exhaustion_20260812.md).

## Why zero weight is mandatory

The visible CICC, 申万宏源 and 财信 content is useful only as a lead. It is not a substitute for a source-controlled broker report. In particular, the CICC/申万宏源 pages for `508077`, the 申万宏源 IPO preview for `508055`, and the 财信 morning-note repost for `508080` were not treated as validated ratings, current targets, forecasts or valuation methodology. The report does not convert a displayed phrase, preview number or issuer-era IPO assumption into consensus.

## Required evidence before an external anchor can be added

For every product, archive an original broker PDF or broker-official research page that includes all of: product identifier; broker and analyst; report date; rating/stance; current target/return assumption; forward distribution, cash-flow or relevant forecast; valuation method; and risk disclosure. A source that misses any of those fields remains zero-weight. Until then, the appropriate status is `watchlist_only / insufficient Street evidence`.
