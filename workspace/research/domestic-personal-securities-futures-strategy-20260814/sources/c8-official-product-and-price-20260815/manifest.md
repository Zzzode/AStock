# C8 Official Product and Price Capture Manifest

- Batch: `c8-official-product-and-price-20260815`
- Capture time: `2026-08-14T18:04:46.566606+00:00`
- Method: anonymous, read-only HTTPS requests to named official documents and the SSE ETF daily-price endpoint.
- Boundary: documents support dated product/mechanics facts; prices are retrospective market-price observations only, not investor total return or execution proof.

| File | Publisher | Date / price coverage | SHA-256 |
|---|---|---|---|
| 511180_product_summary_20250324.pdf | Shanghai Stock Exchange / Haifutong Fund Management | 2025-03-24 | `daecbc61e2b456cd0c58e5e4915a448942e7875c48cf542a4615bcb05d2a0ce6` |
| 511380_product_summary_20260626.pdf | Shanghai Stock Exchange / Bosera Fund Management | 2026-06-26 | `6fa1ebc35cf8adc389df34d7b6c52f18b8de769f4ab32390542cc1eaa7c90670` |
| 511010_product_summary_20260319.pdf | Shanghai Stock Exchange / Guotai Fund Management | 2026-03-19 | `a239534cd25671a4dfd8eda196052ccfeee5bff1d4c8bbb049510199775c6935` |
| sse_950041_investment_grade_cb_methodology.pdf | Shanghai Stock Exchange / China Securities Index | 2026-04-30 | `313efbed504a03a38a77a18f2f47907b2ad6b1187cb1923ed042fc9a44804102` |
| csi_931078_convertible_exchangeable_factsheet_20260130.pdf | China Securities Index | 2026-01-30 | `4fcc2e7885edfba9c01e5a74db431bfb567b772b470c5fadcbeb464b08aef004` |
| sse_bond_etf_guide_20200722.html | Shanghai Stock Exchange | 2020-07-22 | `75965d36517cdeba80cdcff91d359170ff60d7061f3f8d5b48754ee1fdf44c77` |
| sse_etf_faq_20260815.html | Shanghai Stock Exchange | 2026-08-15 | `7cac2227949d4ad46c094059f3b8bcc2f8d9e0c13d466b4b25b9b3ad3ecb769e` |
| sse_convertible_redemption_index_rule_20190906.html | Shanghai Stock Exchange / China Securities Index | 2019-09-06 | `686a514417d953bb75abacdcfcbc10897184d931f505de4bcda7f0929cdd4ed2` |
| sse_etf_dayk_511180_begin0_end5000.jsonp | Shanghai Stock Exchange | 20200826 to 20260814 (1447 rows) | `03157b2db9ea7051d02c7ef9f9bc15dc7677225469ba2ebffe0b065d070607d3` |
| sse_etf_dayk_511380_begin0_end5000.jsonp | Shanghai Stock Exchange | 20200407 to 20260814 (1543 rows) | `d01eab2d4746319042b2907a50debd4c664e4e67147d44613997ce1c3b268b3c` |
| sse_etf_dayk_511010_begin0_end5000.jsonp | Shanghai Stock Exchange | 20130325 to 20260814 (3255 rows) | `93b38794d47f20388c12bcf11b5bd59fd35ba6301ec5673e43eda2d9bc951ef9` |

Every hash in this table is verified by `tools/verify_source_manifests.py`. The existence of an official public response does not establish point-in-time availability, price-adjustment basis, event completeness, licensed replay, or a tradable result.
