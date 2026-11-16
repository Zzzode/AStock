# H2 CFFEX Public-Route Probe — Manifest

- Capture: `probe-h2-cffex-public-route-20260815`
- Retrieved: 2026-08-15T01:15:37+08:00
- Scope: route discovery only; no historical series, contract selection, return, allocation or action.

The `www.cffex.com.cn` pages are official discovery routes, but direct network access from this environment timed out. The `e-cffex` alias returned a generic 2,132-byte error page for the live daily-statistics, historical-service and fee URLs; those response files are retained only as transport evidence and are not market data.

| File | Requested URL | SHA-256 | Meaning |
|---|---|---|---|
| `ecffex_daily_stats_alias_response.html` | `https://www.e-cffex.com.cn/cn/rtj.html` | `7f3f0a9c9177e8f4b6cc3b0453f50d20febff1bc9e1097e916c38e8e9ca6eb4b` | Alias error, not a daily-data response |
| `ecffex_historical_service_alias_response.html` | `https://www.e-cffex.com.cn/lssjfw/` | `7f3f0a9c9177e8f4b6cc3b0453f50d20febff1bc9e1097e916c38e8e9ca6eb4b` | Alias error, not a historical-data response |
| `ecffex_fee_alias_response.html` | `https://www.e-cffex.com.cn/zjssf/20240701/39212.html` | `7f3f0a9c9177e8f4b6cc3b0453f50d20febff1bc9e1097e916c38e8e9ca6eb4b` | Alias error, not a fee-schedule response |

The live official URLs discovered are itemized in `manifest.json` with their exact limitations. Their discovery does not amount to a full public, point-in-time, roll-aware data path.
