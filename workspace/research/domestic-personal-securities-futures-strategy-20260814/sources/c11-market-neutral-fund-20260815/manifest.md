# C11 Official Market-Neutral Fund Source Manifest

- Batch: `c11-market-neutral-fund-20260815`
- Capture time: `2026-08-14T18:45:38.282484+00:00`
- Method: anonymous, read-only HTTPS requests to named ChinaAMC documents and the fund's published all-history NAV endpoint.
- Boundary: the NAV file supports cumulative-NAV proxy arithmetic only; it is not a holder dealing result or execution record.

| File | Publisher | Date / coverage | SHA-256 |
|---|---|---|---|
| 008856_product_summary_20260529.pdf | ChinaAMC Fund Management Co., Ltd. | 2026-05-29 | `b924244db7c1e03d4a306376d3bf7b742c09e27855c984d11a596bb5158e8695` |
| 008856_open_notice_20260512.pdf | ChinaAMC Fund Management Co., Ltd. | 2026-05-12 | `a466e9dc327488d864a033b35aa70fea0041d2ca75225d80001880b45554c2e2` |
| 008856_official_nav_all_20260815.js | ChinaAMC Fund Management Co., Ltd. | 2020-06-05 to 2026-08-14 (1464 observations) | `5a63fe2ea9c3bec1cc5d9cea7729ba5dc90f5b8658af302a6c18a268ee4228ea` |
| 008856_official_nav_history_page_20260815.html | ChinaAMC Fund Management Co., Ltd. | 2026-08-15 | `997e4114518f1aade1fb95768e2fb58d2f532da4f08477859bf06c817ba77171` |

Every raw-file hash in this table is checked by `tools/verify_source_manifests.py`. The hash control cannot establish the historical publication timestamp, holder charges, eligibility, dealing confirmation, or an actionable result.
