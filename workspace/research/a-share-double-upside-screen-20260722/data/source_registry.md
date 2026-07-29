# Source Registry

The source-of-truth PDFs are archived case-locally. Official filings are L1; original broker PDFs are L3 forecast evidence; market feeds establish price but not causality.

| Source ID | Type | Date | Use | Quality | Limitation |
|---|---|---|---|---|---|
| MKT-ASTOCK-20260722 / MKT-TENCENT-20260722 | Realtime quote + daily bars | 2026-07-22 | price, market cap, drawdown | cross-checked | no seller/fundamental causality |
| MKT-CLOSE-NEWS-20260722 | Market close report | 2026-07-22 | index, turnover, breadth | reputable media | not exchange bulletin |
| OFF-600150-FY25/Q1/H1/SHARES | Official filings | 2026-04-30 to 2026-07-14 | merger-restated financials, H1 preview and 7.52562bn-share reconciliation | L1 | H1 unaudited; merger normalization |
| OFF-301308-FY25/Q1/H1/SHARES | Official filings | 2026-04-28 to 2026-07-03 | financials, H1 revenue/profit and 0.423061bn-share reconciliation | L1 | ASP, bit shipment and cash split absent |
| OFF-002812-FY25/Q1/H1/SHARES | Official filings | 2026-04-23 to 2026-07-22 | recovery, cash and shares | L1 | company-level price/utilization absent |
| OFF-002240-FY25/Q1/H1 | Official filings | 2026-03-28 to 2026-07-09 | turnaround and cash | L1 | tonnage/ASP/unit cost absent |
| OFF-300390-FY25/Q1/H1 | Official filings | 2026-04-02 to 2026-07-10 | corrected financials and preview | L1 | tonnage/ASP/customer order absent |
| OFF-002497-FY25/Q1/H1 | Official filings | 2026-04-27 to 2026-07-07 | segments, customers, contracts, cash and preview | L1 | 2026 H2 unit economics absent |
| BRK-002497-DW-20260707 | Original broker PDF | 2026-07-07 | EPS 2.63, 16x PE, target 42 | L3 original | target horizon not disclosed |
| BRK-002812-DW-20260710 | Original broker PDF | 2026-07-10 | EPS 5.16, 20x PE, target 103 as zero-weight sensitivity | L3 original | target horizon and company-level parameters absent |
| BRK-ZERO-WEIGHT-CATALOG | 12 other original PDFs | through 2026-07-14 | earnings context | L3 originals | no point target; zero valuation weight |

Full paths, official URLs and per-source limitations are in the paired JSON registry. Text extractions are convenience copies; PDFs remain the citation source of truth.
