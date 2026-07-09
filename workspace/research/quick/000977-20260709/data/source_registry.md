# Source Registry

| id | source | type | date | quality | used for |
|---|---|---|---|---|---|
| S1 | data/raw_quote_20260709.json | live quote packet | 2026-07-09 | full_realtime | current price, turnover amount, limit-up state |
| S2 | data/raw_financials_20260709.json | structured financial packet | 2026-07-09 | full | 2025A, 2026Q1 revenue, profit, margin, cash flow |
| S3 | data/raw_news_20260709.json | structured news/events packet | 2026-07-09 | full | H1 earnings preannouncement, abnormal movement, news flow |
| S4 | 01-capital-20260708-q2-beat.pdf/txt | original broker PDF | 2026-07-08 | original_pdf | target price 90, 2026-2028 EPS 3.86/4.13/4.95 |
| S5 | 02-kysec-20260708-h1-beat.pdf/txt | original broker PDF | 2026-07-08 | original_pdf | 2026-2028 net profit 51.26/75.90/95.44bn, EPS 3.49/5.17/6.50 |
| S6 | local AIDC official filing pack | official filing text mirror | 2025A/2026Q1 | official_filing_local | inventory, contract liabilities, customer concentration, liquid-cooling patents |
| S7 | public web snippets from Eastmoney/Sina/Securities Times | public media / exchange data repost | 2026-07-08/09 | media_repost | 7/8 LHB, holder snapshot, H1 preannouncement cross-check |
| S8 | historical AIDC report workspace | local research pack | 2026-06-30 | internal_prior_model | old valuation baseline and supply-chain framework |

Data gaps:
- The local technical-analysis packet degraded because daily data sources failed. The report therefore uses live quote, LHB, amount, broker PDFs, and public price context; detailed MA/MACD values are not claimed.
- Customer names for top five customers remain anonymized in the annual report. Named internet customer exposure is adopted only as broker-stated / industry-stated, not official customer disclosure.
