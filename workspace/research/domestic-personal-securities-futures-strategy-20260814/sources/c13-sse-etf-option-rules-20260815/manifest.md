# C13 SSE ETF Option Source Manifest

- Batch: `c13-sse-etf-option-rules-20260815`
- Capture time: `2026-08-14T18:55:02.198582+00:00`
- Method: anonymous, read-only HTTPS requests to named SSE option and fund documents.
- Boundary: this documents rules and data-field requirements, not historical actual-contract access or an execution result.

| File | Date | SHA-256 |
|---|---|---|
| sse_300etf_option_listing_terms_20191217.html | 2019-12-17 | `7729efdf8651dc6d5385ac67122fbe0b40abce2d34471f66d8b1b35b0a19b0a6` |
| sse_stock_option_investor_suitability_20170628.html | 2017-06-28 | `e79cda6747d18ae145fbb2de8e6dd0bbc909969c2af4717976d7a6644c53a5c0` |
| sse_stock_option_trial_trading_rules_20150109.html | 2015-01-09 | `ddafdc569fe845cfb5e612e07006288629680433d9dd72bdb4e5ff5a2956b540` |
| sse_300etf_option_adjustment_20260116.html | 2026-01-16 | `3aed808984d8a401132cbe85ecc9a692c9448a1304b7c3530282640bab0e162a` |
| sse_option_market_data_file_spec_202601.pdf | 2026-01-01 | `49e5b719d07b25c48601ce3e723fed38707417004ecfc216c9908be540d18b0c` |
| sse_option_price_page_20260815.html | 2026-08-15 | `5b7f88565d943aa1503811b774b98e9d82815e67dc0be0f79669e2fe1b04091e` |
| 510300_product_summary_20251124.pdf | 2025-11-24 | `c00ceaf200a405a0e15459deff9d2ef5e1f12e8e0c88ba492169ca5f08f7b676` |

`tools/verify_source_manifests.py` verifies every retained raw-file hash. The frozen material cannot validate an individual account, a full historical contract chain, bid/ask availability, a fill, or a return result.
