# Raw ETF fundamentals extraction — 2026-08-12

## Purpose and boundary

This is a source-anchored transcription ledger for the three ETF objects in the frozen research universe: 511010, 510880 and 512890. It is derived only from archived official annual reports, 2026 Q2 reports, product data summaries (PDS) and updated prospectuses. It is not a recommendation, valuation, allocation, income forecast, current market-data snapshot or implementation approval.

The machine-readable source of truth is `data/raw_etf_fundamentals_20260812.json`.

## Evidence standard

| Source class | Scope | Financial-information status |
|---|---|---|
| 2025 annual report | Audited year-end fundamentals, performance, distribution and holdings disclosures | Audited; 510880 and 512890 explicitly report standard unqualified opinions. 511010 includes the auditor’s opinion in the report. |
| 2026 Q2 report | Latest archived 2026-06-30 units, NAV, performance and holdings snapshot | **Unaudited** — each report explicitly says so. |
| PDS / updated prospectus | Legal terms, mandate, benchmark, fee schedule, disclosed risk and index construction | Product/legal disclosure; not current market data. |

The PDF hashes, document paths and all anchors are in the JSON twin. Q2 data must not be presented as audited financial information.

## Raw extraction summary

| Ticker | Product | 2025 year-end NAV / units | 2026 Q2 NAV / units | Principal dated holdings disclosure |
|---|---|---:|---:|---|
| 511010 | 国泰上证5年期国债ETF | CNY3.021bn / 21.576m | CNY5.117bn / 36.356m | 2025 and Q2 top-five government bonds |
| 510880 | 华泰柏瑞上证红利ETF | CNY19.265bn / 6.056bn | CNY22.276bn / 7.654bn | 2025 all-index-holdings table; 2026 Q2 top ten |
| 512890 | 华泰柏瑞中证红利低波动ETF | CNY26.754bn / 22.780bn | CNY31.290bn / 29.331bn | 2025 all-index-holdings table; 2026 Q2 top ten |

### 511010 — annual report and Q2 facts

- The 2025 annual report identifies an exchange-traded open-ended government-bond index fund managed by 国泰基金管理有限公司 and custodied by 中国建设银行股份有限公司. It follows the 上证5年期国债指数收益率 using optimised sampling. Anchors: `511010_2025_annual.txt:L159-L218`.
- At 2025-12-31 it reported CNY3.021bn net assets, CNY140.027 NAV per unit and a 0.59% calendar-year NAV return. It reported CNY21.042 per ten units / CNY38.003m cash distribution for 2025. Anchors: `L285-L389`.
- The PDS dated 2026-03-19 states 0.15% management fee, 0.05% custody fee and 0.21% annual operating-cost estimate; creation/redemption agent commission is stated as no more than 0.4%, while secondary-market broker charges are actual charges. Anchors: `511010_2026_pds.txt:L84-L123`.
- The 2026 Q2 report is explicitly unaudited. At 2026-06-30 it reported CNY5.117bn net assets, CNY140.753 NAV per unit, 36.356m units, 0.78% three-month NAV return and 98.89% of NAV in government bonds. Anchors: `511010_2026q2.txt:L26-L49`, `L120-L168`, `L413-L510`.

### 510880 — annual report and Q2 facts

- The annual report identifies an exchange-traded open-ended equity index fund managed by 华泰柏瑞基金管理有限公司 and custodied by 招商银行股份有限公司. It uses full replication of the 上证红利指数. Anchors: `510880_2025_annual.txt:L162-L189`.
- At 2025-12-31 it reported CNY19.265bn net assets, CNY3.1813 NAV per unit and a -0.45% calendar-year NAV return. The annual table reports cash distributions of CNY1.4200 per ten units / CNY1.028bn for 2025, CNY1.3100 / CNY795.586m for 2024 and CNY1.3800 / CNY697.890m for 2023. Anchors: `L229-L325`.
- The PDS dated 2026-06-19 states a 95% minimum index-constituent/alternate allocation, 0.50% management fee, 0.10% custody fee and 0.60% annual operating-cost estimate. It quotes creation/redemption agent commission at 0.5%; secondary-market broker charges are actual charges. Anchors: `510880_2026_pds.txt:L31-L54`, `L68-L117`.
- The 2026 Q2 report is explicitly unaudited. At 2026-06-30 it reported CNY22.276bn net assets, CNY2.9103 NAV per unit, 7.654bn units, -10.36% three-month NAV return and 98.73% of total assets in equities. Anchors: `510880_2026q2.txt:L18-L37`, `L66-L119`, `L395-L510`.

### 512890 — annual report and Q2 facts

- The annual report identifies an exchange-traded open-ended equity index fund managed by 华泰柏瑞基金管理有限公司 and custodied by 中国建设银行股份有限公司. It uses full replication of the 中证红利低波动指数. Anchors: `512890_2025_annual.txt:L163-L194`.
- At 2025-12-31 it reported CNY26.754bn net assets, CNY1.1745 NAV per unit and a 4.74% calendar-year NAV return. The annual report says it made no profit distributions in the past three years, including 2025. Anchors: `L234-L326`, `L640-L646`.
- The PDS dated 2026-03-18 states a 90% minimum net-asset allocation to index constituents/alternates and 80% minimum of non-cash assets, 0.50% management fee, 0.10% custody fee and 0.60% annual operating-cost estimate. Creation/redemption agent commission is stated as no more than 0.5%; secondary-market broker charges are actual charges. Anchors: `512890_2026_pds.txt:L33-L64`, `L83-L129`.
- The 2026 Q2 report is explicitly unaudited. At 2026-06-30 it reported CNY31.290bn net assets, CNY1.0668 NAV per unit, 29.331bn units, -10.83% three-month NAV return and 97.77% of total assets in equities. Anchors: `512890_2026q2.txt:L19-L38`, `L73-L115`, `L318-L438`.

## Material gaps retained for later gates

These disclosures do not establish current price, NAV/IOPV, premium/discount, 20-session liquidity, executable depth, tax/account suitability, all-in execution cost, or a current holdings/overlap file. For 511010 they also do not establish current duration, modified duration, DV01 or convexity. No missing item is filled by inference.

No ETF passes an investability or allocation gate through this extraction.
