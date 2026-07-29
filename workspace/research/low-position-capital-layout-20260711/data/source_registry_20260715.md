# Refresh Source Registry

- R01 | Eastmoney datacenter paginated official H1 preview table | L1 | `refresh-20260715/data/raw_a_share_h1_2026_preview_20260715.json` | boundary: company-level unaudited preview; no segment/customer/ASP proof
- R02 | Tencent quote and adjusted K-line refresh | L1-L2 | `refresh-20260715/sources/market-20260715/; refresh-20260715/data/market/` | boundary: price/history only; no investor-identity inference
- R03 | Q1 financial and broker evidence refresh | L1-L3 by ticker | `refresh-20260715/data/financials/; refresh-20260715/sources/broker-reports-20260715/` | boundary: Q1 coverage 142/142; broker PDF coverage 138/142
- R04 | Latest available industry-flow packet | L2 fallback | `data/sector_scan_20260710.json` | boundary: not a 2026-07-15 live industry-flow confirmation
