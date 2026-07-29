# Raw Financial Data Capture

## Scope and provenance

- Universe: 22 A-share issuers requested for the Huawei Atlas 950 SuperPoD case.
- Actual-period cutoff: FY2025 (`2025-12-31`) and 2026Q1 (`2026-03-31`).
- Actual-data source: `.venv/bin/python -m astock.cli financials <code> --periods 5 --json`; the capability wraps AkShare `stock_financial_abstract` / Eastmoney structured financial abstracts.
- Actual-data retrieval window: `2026-07-18 16:39:11-16:39:49 CST`.
- 2026H1 preview census: Eastmoney regulatory-notice index (official issuer announcements), announcements through `2026-07-17`; capture time `2026-07-18 16:33-16:40 CST`.
- Units below are raw CNY unless otherwise stated. No values were estimated or interpolated.

## FY2025 and 2026Q1 actuals

| Ticker | Company | FY2025 revenue | FY2025 parent NP | FY2025 deducted NP | FY2025 EPS | 2026Q1 revenue | 2026Q1 parent NP | 2026Q1 deducted NP | 2026Q1 EPS | Source / timestamp | Quality |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| 000034 | 神州数码 | 143,751,044,503.13 | 522,943,843.22 | 703,306,268.81 | 0.7711 | 40,557,142,015.74 | 235,993,097.38 | 233,118,208.42 | 0.3358 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 002261 | 拓维信息 | 3,171,008,206.09 | 63,742,956.25 | -40,192,156.45 | 0.0507 | 593,581,435.45 | 61,455,042.50 | -7,754,770.98 | 0.0488 | AStock CLI, 2026-07-18 16:39:12 CST | Medium |
| 000988 | 华工科技 | 14,354,760,508.18 | 1,470,794,704.16 | 1,187,461,550.92 | 1.4700 | 4,265,855,702.83 | 638,461,927.07 | 372,744,442.79 | 0.6400 | AStock CLI, 2026-07-18 16:39:12 CST | Medium |
| 002281 | 光迅科技 | 11,928,697,127.38 | 946,320,781.21 | 915,411,336.26 | 1.2100 | 2,773,352,847.92 | 239,931,671.46 | 227,777,420.56 | 0.3000 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 688498 | 源杰科技 | 601,434,509.56 | 190,924,031.75 | 167,222,369.40 | 2.2400 | 355,278,486.49 | 179,441,968.61 | 177,939,676.39 | 2.0900 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 300620 | 光库科技 | 1,473,966,074.80 | 176,672,911.07 | 139,948,940.52 | 0.7090 | 426,465,402.22 | 44,736,399.48 | 35,806,560.83 | 0.1795 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 300548 | 长芯博创 | 2,532,639,369.67 | 334,851,021.96 | 322,248,124.60 | 1.1600 | 670,605,570.02 | 130,067,296.15 | 127,654,983.87 | 0.4500 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 600183 | 生益科技 | 28,431,138,459.44 | 3,333,954,377.92 | 3,174,916,620.66 | 1.3900 | 8,141,455,910.40 | 1,158,139,324.56 | 1,082,821,715.86 | 0.4800 | AStock CLI, 2026-07-18 16:39:12 CST | Medium |
| 002916 | 深南电路 | 23,646,977,088.98 | 3,275,738,151.27 | 3,113,627,500.81 | 4.9100 | 6,595,587,902.38 | 850,230,796.58 | 849,446,715.47 | 1.2800 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 002463 | 沪电股份 | 18,945,220,585.00 | 3,822,306,272.00 | 3,760,567,906.00 | 1.9875 | 6,214,156,406.00 | 1,242,081,367.00 | 1,162,681,935.00 | 0.6455 | AStock CLI, 2026-07-18 16:39:11 CST | Medium |
| 300476 | 胜宏科技 | 19,292,313,457.36 | 4,311,988,274.40 | 4,303,867,824.00 | 5.0100 | 5,519,485,066.85 | 1,288,427,592.46 | 1,257,223,943.14 | 1.4800 | AStock CLI, 2026-07-18 16:39:41 CST | Medium |
| 002837 | 英维克 | 6,067,759,091.55 | 521,914,773.00 | 503,698,695.52 | 0.5400 | 1,175,329,313.61 | 8,657,602.27 | 5,392,856.48 | 0.0100 | AStock CLI, 2026-07-18 16:39:41 CST | Medium |
| 301018 | 申菱环境 | 4,209,198,844.25 | 216,777,173.18 | 207,219,611.80 | 0.8100 | 617,158,503.38 | 28,305,819.43 | 25,641,958.56 | 0.1100 | AStock CLI, 2026-07-18 16:39:41 CST | Medium |
| 300990 | 同飞股份 | 2,867,483,348.02 | 252,903,184.27 | 247,849,301.26 | 1.4900 | 698,648,608.86 | 59,774,437.93 | 59,139,496.96 | 0.3500 | AStock CLI, 2026-07-18 16:39:41 CST | Medium |
| 002335 | 科华数据 | 8,160,262,477.61 | 417,988,029.54 | 385,003,993.37 | 0.8300 | 1,430,062,407.61 | 78,008,800.49 | 64,759,399.94 | 0.1500 | AStock CLI, 2026-07-18 16:39:41 CST | Medium |
| 002364 | 中恒电气 | 2,137,227,829.77 | 126,374,581.15 | 115,324,081.29 | 0.2200 | 418,396,025.60 | 24,935,658.45 | 21,968,894.70 | 0.0400 | AStock CLI, 2026-07-18 16:39:41 CST | Medium |
| 002922 | 伊戈尔 | 5,263,733,523.65 | 200,241,927.11 | 183,644,656.20 | 0.5000 | 1,275,593,596.60 | 68,673,903.86 | 52,261,546.86 | 0.1600 | AStock CLI, 2026-07-18 16:39:48 CST | Medium |
| 002130 | 沃尔核材 | 8,450,660,581.14 | 1,143,868,383.15 | 1,093,317,711.57 | 0.9200 | 2,032,119,346.79 | 231,285,868.64 | 221,475,754.12 | 0.1726 | AStock CLI, 2026-07-18 16:39:49 CST | Medium |
| 300913 | 兆龙互连 | 2,123,930,905.00 | 231,363,263.59 | 225,467,547.01 | 0.7400 | 508,488,452.66 | 48,548,763.99 | 47,625,203.51 | 0.1416 | AStock CLI, 2026-07-18 16:39:48 CST | Medium |
| 688668 | 鼎通科技 | 1,587,675,135.79 | 240,524,940.42 | 221,948,572.41 | 1.7300 | 457,401,910.07 | 80,327,438.38 | 76,636,211.42 | 0.5800 | AStock CLI, 2026-07-18 16:39:48 CST | Medium |
| 002230 | 科大讯飞 | 27,105,390,547.66 | 839,390,861.36 | 264,276,850.77 | 0.3600 | 5,274,188,660.25 | -169,724,621.52 | -429,594,090.14 | -0.0700 | AStock CLI, 2026-07-18 16:39:49 CST | Medium |
| 002025 | 航天电器 | 5,819,834,373.25 | 182,846,795.18 | 147,143,217.14 | 0.4000 | 1,613,999,955.60 | 52,232,066.52 | 44,941,359.19 | 0.1100 | AStock CLI, 2026-07-18 16:39:49 CST | Medium |

## 2026H1 official preview census

Nine of 22 issuers had an official 2026H1 earnings preview through 2026-07-17: `002281`, `300620`, `300548`, `600183`, `002916`, `002463`, `002335`, `688668`, and `002230`. Exact announcement identifiers, ranges, and source URLs are preserved in `sources/official-filings-20260718/2026h1_guidance_capture.md`.

No 2026H1 earnings preview or earnings flash was found in the complete announcement-index scan for: `000034`, `002261`, `000988`, `688498`, `300476`, `002837`, `301018`, `300990`, `002364`, `002922`, `002130`, `300913`, and `002025`. This means **N/A (not disclosed through 2026-07-17)**, not zero and not an estimate.

## Raw-source limitations

- The AStock financial capability returned `data_quality=full` and no warnings for all 22 tickers, but its actuals are a structured secondary-source mirror rather than locally archived filing tables. Confidence is therefore tagged Medium pending line-by-line filing-PDF reconciliation.
- H1 previews are issuer regulatory announcements and are tagged High, but they are unaudited preliminary calculations and may differ from the eventual 2026H1 reports.
