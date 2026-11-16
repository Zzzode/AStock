# Vendor Data-Path Documentation Manifest

This archive captures documentation for nine ETF and futures data interfaces.
It supports only the statement that a possible subscription path documents the
required field families. It does not show that a subscription, data-right,
historical response archive or user access exists.

| Field family | Captured documentation |
|---|---|
| ETF price, NAV, distribution, adjustment and master | `tushare_fund_daily.html`, `tushare_fund_nav.html`, `tushare_fund_div.html`, `tushare_fund_adj.html`, `tushare_etf_basic.html` |
| Futures master, daily, settlement and limits | `tushare_fut_basic.html`, `tushare_fut_daily.html`, `tushare_fut_settle.html`, `tushare_ft_limit.html` |

Each file row in `manifest.json` now records publisher, local path, URL,
retrieval date, explicit "effective date not stated" convention, use boundary,
byte size and SHA-256. The batch-level caveat applies to every row: these pages
are documentation, not evidence of a token, entitlement or retained response.
