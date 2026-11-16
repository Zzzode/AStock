# Official Futures R0 Capture Manifest

- Capture batch: `official-futures-r0-20260814`
- Captured: 2026-08-14 14:03:53 +08:00
- Boundary: rules, data-field availability and suitability boundary only.

| File | Purpose | Bytes | SHA-256 |
|---|---|---:|---|
| `csrc_futures_investor_suitability_2022.html` | Suitability-system boundary | 74,719 | `6c7fd3…a79d` |
| `czce_futures_data_interface_20250523.pdf` | Contract, quote and trading-state field definitions | 1,656,623 | `5af5f9…1d4bd` |
| `shfe_information_rules_20250807.html` | Information rights and daily-data categories | 173,035 | `79e159…75e4a` |
| `shfe_information_service_20200610.pdf` | Published market-data scope | 1,790,788 | `5461f6…3a27` |

The SHFE information-rules file is a byte-identical successor copy of a
previous validated capture. A fresh direct URL request returned a WAF challenge;
that page was rejected and is recorded in `source_exhaustion_log.*`.
Full URLs and hashes are in `manifest.json`.
