# Source Exhaustion Log — 600150 Broker / Market Packet

Date: 2026-07-22

| Evidence sought | Probes completed | Result | Treatment | Next verification path |
|---|---|---|---|---|
| Original broker target prices in the 13 archived PDFs | Full-text search and manual review of all forecast/valuation sections | None of the 13 PDFs disclosed an explicit target price | Record `not disclosed`; never infer a target from stated PE | Obtain broker-authorized current reports or terminal exports preserving report identity and valuation table |
| 华泰证券 2026-05-03 original PDF | Public report aggregators, public F10 forecast page, and iFinD-derived public snapshot | Original PDF unavailable; public snapshot shows 2026E EPS 2.68, 22x PE and target 58.96 | Preserve as `auditable_consensus_snapshot`, valuation weight 0 | Broker official research portal or authorized Wind/Choice/iFinD export |
| 国泰海通证券 2026-05-19 original PDF | Public report preview page | Only visible abstract; EPS 2.35/3.19/4.17 and 20x 2026E PE / target 47.00 visible | Preserve as `third_party_preview`, valuation weight 0 | Broker official research portal or authorized terminal export |
| Current market capitalization from project quote packet | Project-native quote capability | `total_market_value=0`; unusable as a factual zero | Recompute from price 33.02 × official shares 7,525,621,288 = CNY 248.496bn | Replace with same-timestamp exchange market-cap field if available |
| Same-timestamp current shares / free float | Company 2026Q1 report and broker report cross-checks | Exact total shares verified at 2026-03-31; no same-timestamp exchange free-float packet archived | Use total shares for market cap; do not publish current free-float market cap | 2026H1 official report or SSE current capital structure snapshot |

Archived probe files:

- `astock-quote-600150-20260722.json`
- `600150-2026q1-report.pdf` and `.txt`
- `sina-600150-2026q1-bulletin.html`
- `10jqka-ifind-consensus-600150-20260518.html`
- `gw-f10-profit-forecast-600150-20260722.html`
- `huatai-600150-260503-preview.html`
- `guotai-haitong-600150-260519-preview.html`
