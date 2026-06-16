# Official / Structured Financials Summary

**Source:** `astock.capabilities.get_financial_statements()` backed by AkShare financial abstract data.
**Fetched at:** see `official_financials.json` per ticker.
**Use:** official/structured financial checkpoint for report update. The original 2026Q1 filing PDFs are now archived in `workspace/reports/semiconductor-pcb-q1-official-20260615/` for audit.

| Ticker | Latest period | Revenue | Net profit parent | Gross margin | ROE | Revenue growth | Profit growth | Data quality |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 002463 | 20260331 | 62.14亿元 | 12.42亿元 | 35.63% | 7.81% | 53.91% | 62.90% | full |
| 300476 | 20260331 | 55.19亿元 | 12.88亿元 | 34.46% | 7.62% | 27.99% | 39.95% | full |
| 002916 | 20260331 | 65.96亿元 | 8.50亿元 | 29.17% | 4.83% | 37.90% | 73.01% | full |
| 600183 | 20260331 | 81.41亿元 | 11.58亿元 | 28.10% | 6.68% | 45.09% | 105.47% | full |
| 603186 | 20260331 | 12.34亿元 | 0.31亿元 | 12.02% | 1.59% | 19.84% | 68.04% | full |
| 688519 | 20260331 | 18.32亿元 | 1.50亿元 | 15.20% | 5.08% | 92.36% | 610.83% | full |
| 002436 | 20260331 | 18.18亿元 | 0.19亿元 | 19.17% | 0.35% | 15.10% | 100.00% | full |
| 301200 | 20260331 | 19.55亿元 | 3.23亿元 | 33.12% | 3.74% | 103.69% | 176.53% | full |
| 688630 | 20260331 | 5.15亿元 | 1.08亿元 | 40.94% | 4.59% | 112.48% | 108.98% | full |
| 300400 | 20260331 | 1.69亿元 | 0.26亿元 | 39.66% | 3.52% | 9.18% | 3.40% | full |
| 301377 | 20260331 | 8.14亿元 | 2.61亿元 | 53.25% | 9.38% | 92.33% | 259.00% | full |
| 002938 | 20260331 | 79.86亿元 | 4.63亿元 | 22.96% | N/A | -1.25% | -5.21% | official_filing_manual_bridge |

## Notes

- Values are extracted from structured financial abstracts and normalized by the local capability kernel.
- The table uses the latest available reporting period per ticker.
- Original Q1 filing PDFs have been archived for the 11 original names, and Pengding's 2026Q1 filing is archived separately in `workspace/reports/semiconductor-pcb-pengding-official-20260616/`. External publication still requires manual line-by-line table audit.
