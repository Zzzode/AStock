# Raw Financial Data — Desay SV (002920.SZ)

- Data cutoff: 2026-07-23 CST.
- Currency: CNY. Amounts below are converted to RMB bn unless a table says otherwise; conversion is display-only (`RMB / 1e9`), not an estimate.
- Period rule: FY figures are full-year; 2026Q1 is a standalone three-month reported period. No quarter has been annualized.
- Latest disclosed periodic report: 2026Q1, published 2026-04-28; its financial statements are **unaudited**.

## Source register and raw-evidence locations

| ID | Source | Primary evidence / URL | Quality | Use and limitation |
|---|---|---|---|---|
| F1 | 2025 annual report (2026-03-06) | [CNINFO PDF](https://static.cninfo.com.cn/finalpage/2026-03-06/1224998406.PDF); local extracted text: `sources/ir-20260723/desay_sv_2025_annual_report_cninfo.txt` | High | Audited annual filing. It contains 2025 values and comparative 2024 values. |
| F2 | 2026Q1 report, announcement 2026-027 (2026-04-28) | [filer-issued announcement mirror](https://money.finance.sina.com.cn/corp/view/vCB_AllBulletinDetail.php?id=12211732&stockid=002920) | High for disclosure origin; unaudited period | The retrieved primary-document mirror states the full report title, announcement number, date and financial tables. Direct CNINFO query returned no usable record in this session. |
| F3 | `astock.cli financials 002920 --json`, fetched 2026-07-23 13:30 CST | Capability packet captured in collection log | Medium-high | Structured cross-check for 2023–2026Q1 revenue, profit, cash flow, margins and ratios; vendor field provenance is not attached to every value. |
| F4 | Eastmoney structured financial statements: `RPT_F10_FINANCE_MAINFINADATA`, `...GBALANCE`, `...GINCOME`, `...GCASHFLOW` | [main indicators endpoint](https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_F10_FINANCE_MAINFINADATA&columns=ALL&filter=(SECUCODE%3D%22002920.SZ%22)&pageNumber=1&pageSize=20&sortColumns=REPORT_DATE&sortTypes=-1&source=WEB&client=WEB) | Medium | Structured cross-check and the only collected normalized source for some 2023 balance-sheet fields. It is not a substitute for an audit opinion. |

## Income statement and operating cash flow

| Period | Revenue | YoY | Attributable NP | YoY | Deducted NP | YoY | Gross margin | Operating cash flow | Basic EPS | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| FY2023 | 21.9080 | 46.71% | 1.5467 | 30.57% | 1.4665 | 41.37% | 19.97% | 1.1410 | 2.81 | F3/F4 |
| FY2024 | 27.6181 | 26.06% | 2.0049 | 29.62% | 1.9456 | 32.66% | 19.88% | 1.4935 | 3.63 | F1 comparative / F3 / F4 |
| FY2025 | 32.5572 | 17.88% | 2.4536 | 22.38% | 2.4136 | 24.05% | 19.07% | 2.8838 | 4.35 | F1 / F3 / F4 |
| 2026Q1 | 6.4952 | -4.37% | 0.4615 | -20.74% | 0.4759 | -4.21% | 18.60% | 1.1158 | 0.77 | F2 / F3 / F4 |

Notes:

- `Deducted NP` means net profit attributable to owners after non-recurring gains/losses.
- FY2023 and FY2024 gross margin is the disclosed/structured gross margin. 2026Q1 gross margin is the statement-derived `1 - operating cost / revenue`; it is **not** an annualized rate.
- F1 directly states FY2025 revenue of RMB 32,557,178,348.37 and attributable NP of RMB 2,453,584,767.75; F2 directly states 2026Q1 revenue of RMB 6,495,182,292.00 and attributable NP of RMB 461,487,967.35.

## Balance sheet, working capital, R&D and share capital

| Period end | Total assets | Total liabilities | Parent equity | Debt ratio | Accounts receivable | Inventory | Contract liabilities | R&D investment | R&D expense | Share capital | Source |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 2023-12-31 | 18.0141 | 9.9540 | 7.9523 | 55.26% | 7.1681 | 3.2599 | 0.3450 | 2.0286 | 1.9823 | 555.0234m shares | F3/F4 |
| 2024-12-31 | 21.4833 | 11.7178 | 9.6433 | 54.54% | 9.6037 | 3.6965 | 0.5015 | 2.1918 | 2.2558 | 554.9594m shares | F1 comparative / F3 / F4 |
| 2025-12-31 | 29.8453 | 14.2826 | 15.4181 | 47.86% | 9.7785 | 4.7893 | 1.0053 | 2.6366 | 2.6421 | 596.8426m shares | F1 / F3 / F4 |
| 2026-03-31 | 30.2311 | 14.9210 | 15.1591 | 49.36% | 6.6376 | 5.4924 | 2.5627 | not disclosed | 0.6067 | 596.8093m shares | F2 / F3 / F4 |

Notes:

- `R&D investment` and `R&D expense` are different disclosures. FY2025 R&D investment was RMB 2,636,593,118.17 (8.10% of revenue); F1 reports FY2024 comparative investment of RMB 2,191,848,579.05. Do not interchange either measure with the income-statement R&D expense.
- 2026Q1 does not disclose a quarterly `R&D investment` total in the collected periodic-report summary, so it is marked **not disclosed**. `R&D expense` is the income-statement line from F4 and should not be read as a separately disclosed investment total.
- 2026Q1 report explicitly attributes the fall in accounts receivable to higher customer collections and the rise in contract liabilities to higher advances; these are management explanations, not a forecast.
- FY2025 report states that the 2025 private placement increased total share capital from 554,949,301 to 596,842,634 shares; it also describes a subsequent 33,340-share cancellation to 596,809,294 shares. The Q1 balance sheet uses the latter figure.

## 2026H1 disclosure status — kept separate from 2026Q1

| Item | Status at 2026-07-23 | Evidence / limit |
|---|---|---|
| 2026 interim report | **Not disclosed** | The latest collected periodic report is 2026Q1. The issuer’s historical interim-report list contains FY2025 as the most recent published interim report (2025-08-12). |
| 2026H1 earnings forecast / preannouncement | **Not disclosed in collected official/mirror announcement set** | No 2026H1 forecast was found in the collected issuer announcement list or source probes. CNINFO announcement-query calls were incomplete in this session, so this is a retrieval-status statement, not proof that no filing exists. |
| 2026H1 financial estimate | **Not produced** | No interpolation, Q1 annualization, or analyst estimate is used in this data packet. |
