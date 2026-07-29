# Verified official financials - 600150.SH

**Verification cutoff:** 2026-07-22  
**Currency:** CNY100 million unless stated  
**Primary evidence:** SSE-filed company reports and merger notices archived in `sources/official-company-20260722/`.  
**Automated cross-check status:** unavailable. The project `financials` and `consistency-check` CLI commands returned empty output for both 600150 and 601989. All published values below were independently reconciled to official PDFs and arithmetic checks.

## Publication-safe financial table

| Period | Reporting perimeter | Revenue | YoY | Parent NP | YoY | Adjusted parent NP | OCF | EPS | Confidence |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 2023A | Legacy 600150 as originally reported | 748.39 | +25.81% | 29.57 | +1,614.73% | -2.91 | 182.13 | 0.66 | High - audited annual report S01 |
| 2024A | Legacy 600150 as originally reported | 785.84 | +5.01% | 36.14 | +22.21% | 30.72 | 52.35 | 0.81 | High - audited annual report S02 |
| 2024A | Restated continuing-company comparator | 1,333.51 | N/A in this table | 42.20 | N/A in this table | 30.72 | 147.27 | 0.71 | High - audited comparative in S03 |
| 2025A | Restated continuing company | 1,519.78 | +13.97% | 78.48 | +86.00% | 61.26 | 77.67 | 1.24 | High - audited annual report S03 |
| 2026Q1A | Restated continuing company | 433.12 | +54.90% | 48.32 | +251.64% | 47.67 | 81.52 | 0.642 | High - official unaudited Q1 report S04 |
| 2026H1E | Restated continuing company | Not disclosed | Not disclosed | 92.00-110.00 | +143.56% to +191.21% vs restated 2025H1 | 90.00-108.00 | Not disclosed | Not disclosed | High for disclosure / Medium for outcome - unaudited preview S05 |

Verified arithmetic:

- 2024 legacy revenue growth: `785.8441 / 748.3850 - 1 = 5.0053%`, rounds to 5.01%.
- 2024 legacy parent-NP growth: `36.1414 / 29.5740 - 1 = 22.2066%`, rounds to 22.21%.
- 2025 revenue growth uses the restated 2024 base: `1,519.7799 / 1,333.5084 - 1 = 13.9685%`, rounds to 13.97%.
- 2025 parent-NP growth uses the restated 2024 base: `78.4838 / 42.1957 - 1 = 85.9996%`, rounds to 86.00%.
- 2026Q1 revenue growth uses restated 2025Q1 CNY27.9621bn: +54.8968%, rounds to 54.90%.
- 2026Q1 parent-NP growth uses restated 2025Q1 CNY1.3742bn: +251.6407%.
- 2026H1 preview growth uses restated 2025H1 parent NP CNY3.7773bn: +143.5602% to +191.2133%.

## Publication-safe balance sheet and cash-investment table

| Metric | 2023 legacy | 2024 legacy | 2025 restated continuing company | 2026Q1 restated continuing company | Verification note |
|---|---:|---:|---:|---:|---|
| Monetary funds | 679.65 | 636.81 | 1,468.35 | 1,445.94 | Statutory balance-sheet line; not pure cash equivalents. |
| Contract liabilities | 625.39 | 708.60 | 1,522.14 | 1,523.60 | Best official proxy for customer advances; not identical to all order advances. |
| Short-term borrowings | 55.83 | 20.76 | 75.76 | 11.87 | Direct balance-sheet line. |
| Long-term borrowings | 133.67 | 100.34 | 149.40 | 147.02 | Excludes current maturities. |
| Current non-current liabilities | 63.62 | 40.28 | 138.45 | 105.37 | Includes lease/employee items; do not label the whole line as debt. |
| Cash capex | 24.22 | 16.42 | 34.45 | 7.96 | Cash paid for fixed, intangible, and other long-term assets. |

## Verified order/backlog scope

The publication-safe current backlog statement is:

> At 2025 year-end, post-merger 600150 disclosed 652 civil and offshore vessels in backlog, totaling 79.973m dwt and CNY467.451bn; repair backlog was 189 vessels/CNY0.839bn, and equipment/electromechanical/other backlog was CNY12.963bn.

Required scope qualifiers:

- This is the post-merger **listed company**, described as controlling seven major shipyards and 15 equipment enterprises. It is not CSSC Group.
- The vessel figure covers **civil and offshore** orders. The filing does not disclose a complete monetary backlog for classified military programs.
- It is not comparable with 2024 legacy 600150 backlog of 322 civil vessels/CNY216.962bn because 601989's perimeter entered the continuing company.
- Backlog is a contract stock, not revenue. Delivery schedule, cancellation clauses, price-adjustment terms, foreign-exchange effects, and margin recognition are not disclosed at the aggregate backlog level.

## Verified subsidiary scope

The 2025 annual report identifies the main current-platform yards as Jiangnan Shipyard, Dalian Shipbuilding, Waigaoqiao Shipbuilding, CSSC Chengxi, Guangzhou Shipyard International, and Qingdao Beihai Shipbuilding. CSSC Marine Power appears in the same material-company table as an **associate**, not a consolidated subsidiary. Do not sum these revenues/profits to the consolidated result.

## Verified merger bridge

| Item | Verified conclusion | Evidence/confidence |
|---|---|---|
| Merger parties | 600150 is the surviving absorber; 601989 is the absorbed company. CSSC Group remains the actual controller and SASAC the ultimate controller. | S12-S16; High |
| Agreement effectiveness | All stated conditions were fulfilled no later than CSRC registration on 2025-07-18. Under the agreement clause, effectiveness follows satisfaction of all conditions. This date is an inference from the contract plus final approval, not a separately worded "effective-date" announcement. | S11-S12; High inference |
| Final swap terms | CNY37.59 for 600150 and CNY5.032 for 601989 after dividend adjustment; 1 share of 601989 converted into 0.1339 share of 600150. | S12, S14-S16; High |
| Delisting/record/listing | Swap record date 2025-09-04; 601989 delisted 2025-09-05; new shares registered 2025-09-11 and listed 2025-09-16. | S13-S16; High |
| Shares | 4,472,428,758 pre-existing + 3,053,192,530 new = 7,525,621,288 post-merger shares. Arithmetic reconciles exactly. | S14-S15; High |
| Legal succession | From the contractual delivery date, 600150 succeeds to all assets, liabilities, businesses, personnel, contracts, rights, and obligations of 601989; non-completion of a formal title registration does not negate substantive succession under the agreement. | S12, S14-S16; High |
| Formal transfer completion | S14 on 2025-09-12 said relevant asset registrations were being processed. S16 in May 2026 restated the mechanics but did not provide an asset-by-asset completion inventory. Publication must not claim that all registrations were complete. | S14, S16; High |
| 601989 legal deregistration | The merger plan contemplated cancellation of 601989's legal-person status, but no archived company/SSE filing through 2026-07-22 explicitly confirms completed deregistration. State `not found in official filings through cutoff`. | S12-S16; Medium-high |
| Accounting combination | The 2025 annual report uses 2025-09-30 as the common-control accounting combination date. This is distinct from 9/11 share registration and 9/16 listing. | S03; High |
| 2025 EPS share basis | 2025 basic EPS used weighted-average 6,329,638,855 shares; using year-end 7,525,621,288 would be wrong. | S03; High |

## S-level publication blockers

| Risk | Incorrect treatment | Required treatment |
|---|---|---|
| Scope splicing | Compare 2025 post-merger revenue CNY151.978bn with 2024 legacy CNY78.584bn and call the ~93% change organic growth. | Use restated 2024 CNY133.351bn; verified YoY is 13.97%. |
| Backlog scope | Call CNY467.451bn the CSSC Group backlog or a complete military-plus-civil backlog. | Label it post-merger 600150 civil-and-offshore backlog. |
| Pro forma vs statutory | Use merger-report pro-forma 2024 parent NP CNY4.885bn as the audited statutory comparator. | Statutory comparator in S03 is CNY4.220bn. Keep the pro-forma number transaction-only. |
| Share denominator | Use 7.526bn shares for 2025 EPS or compare per-share figures without merger weighting. | Use disclosed weighted-average 6.330bn for 2025 EPS; use 7.526bn only as period-end shares. |
| Transfer completion | State that all title registrations and 601989 deregistration were completed. | State substantive legal succession; formal-registration completion and legal deregistration are not fully disclosed. |

## A-level interpretation notes

- 2023 legacy parent NP included CNY2.659bn gain from disposing of an offshore platform; adjusted parent NP was a CNY0.291bn loss. Do not portray 2023 reported profit as pure shipbuilding-cycle earnings.
- 2025 OCF fell to CNY7.767bn from restated CNY14.727bn despite profit growth because production ramp-up raised purchases and work-in-progress cash needs.
- Contract liabilities increased to CNY152.214bn by 2025 year-end and stayed near that level at 2026Q1. This supports advance-payment visibility but is not itself profit or free cash flow.
- 2026H1 is an earnings preview only. Revenue, OCF, capex, contract liabilities, and order backlog at 2026-06-30 remain `not disclosed` as of the cutoff.

## Final verification verdict

Official filings support a high-confidence statutory earnings and merger-share bridge. The two material residual gaps are (1) no official asset-by-asset completion inventory for formal title registrations and (2) no explicit filing confirming 601989 legal-person deregistration through 2026-07-22. These gaps do not negate the disclosed substantive succession or common-control financial consolidation, but they must remain caveated in the report.
