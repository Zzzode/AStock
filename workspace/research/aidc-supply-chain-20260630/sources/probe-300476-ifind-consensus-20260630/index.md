# Probe: 300476 iFinD Consensus Target Evidence

**Probe date:** 2026-06-30  
**Ticker:** 300476  
**Company:** 胜宏科技  
**Purpose:** Close the A-share broker/Street target-price gap with a public auditable consensus snapshot while preserving the boundary that the original Eastmoney PDF corpus itself did not disclose a target price.

## Archived Sources

| Source | Local file | Evidence captured | Usability |
|---|---|---|---|
| 同花顺 iNews / iFinD article on 国盛证券 rating update, 2026-04-29 | `10jqka-guosheng-20260429.html` | Public iFinD table lists recent broker forecasts for 300476, including 中信证券 2026-04-23 target 360.0000 and 国投证券 2025-10-30 target 403.4200; the same article states the recent-six-month target range/average at 360.00 / 403.42 / 381.71 and labels the data source as 同花顺 iFinD. | Usable as `auditable_consensus_snapshot`, not as original broker PDF. |
| 东方财富 WAP report page for 中信证券 AP202604231821497562, 2026-04-23 | `eastmoney-citic-20260423.html` | Public URL identifies the 中信证券 300476 follow-up report. Public search snippet for the same URL states 2026E 36x PE, target market cap 3141亿元, target price 360元, and maintained buy rating; the downloaded WAP shell does not expose the full text. | Auxiliary public URL only; do not treat as full PDF. |
| Investing.com analyst target page | `investing-consensus.html` | Third-party analyst target average/range and broker names for overseas/Street targets. | Sentiment cross-check only; not used as the core A-share broker target anchor. |

## Normalized Decision

Use the iFinD table as an auditable consensus snapshot:

| Field | Normalized value |
|---|---|
| broker | 同花顺 iFinD consensus snapshot: 中信证券 / 国投证券 |
| report_date | 2026-04-29 snapshot; underlying target rows 2026-04-23 and 2025-10-30 |
| rating | 买入 |
| target_price | 381.71 |
| target_price_range | 360.00 to 403.42 |
| method | iFinD public consensus target range; 中信证券 public Eastmoney snippet indicates 2026E 36x PE, target market cap 3141亿元 and target price 360元 |
| implied_upside | Calculate against the 2026-06-30 current price in `data/current_valuation_model_20260630.json` |
| source_quality | auditable_consensus_snapshot |
| source_path | `sources/probe-300476-ifind-consensus-20260630/index.md` |
| valuation_weight | 0.10 |

The original Eastmoney 39-report API/PDF full scan remains valid negative evidence: it proves the Eastmoney public broker PDF corpus did not expose an explicit target price. The iFinD snapshot is a separate structured consensus source with broker identities and target values.
