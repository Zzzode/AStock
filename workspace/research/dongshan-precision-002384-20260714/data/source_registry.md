# Source Registry

| ID | Date | Quality | Path | Model use | Limitation |
|---|---|---|---|---|---|
| S1 | 2026-07-14 13:27 CST | realtime | sources/market-20260714/quote_packet_20260714.json | price, market cap, turnover context | The quote service did not return valuation ratios; ratios are recomputed from disclosed shares and earnings. |
| S2 | 2026-07-14 | full | sources/market-20260714/financial_packet_20260714.json | 2025A and 2026Q1A consolidated financials | The packet does not provide a full forward segment forecast. |
| S3 | 2026-04-22 | official_pdf | sources/official-20260714/2026-04-22-2025年年度报告.pdf | segment revenue, gross margin, cash flow, debt, goodwill, acquisition accounting | 2025 optical revenue includes only the post-consolidation period. |
| S4 | 2026-04-28 | official_pdf | sources/official-20260714/2026-04-28-2026年第一季度报告.pdf | Q1 revenue, profit, cash flow, debt and capex indicators | No product-level ASP or customer revenue disclosure. |
| S5 | 2026-04-08 | official_pdf | sources/official-20260714/2026-04-08-2026年第一季度业绩预告.pdf | Q1 preview range and stated drivers | Preview was unaudited and is superseded by the Q1 report. |
| S6 | 2025-06-14 | official_pdf | sources/official-20260714/2025-06-14-收购索尔思光电对外投资公告.pdf | purchase price, business scope, historical financials and valuation basis | The acquisition announcement is not a customer order book. |
| S7 | 2026-06-17 | official_pdf | sources/official-20260714/2026-06-17-光芯片及光模块扩建对外投资公告.pdf | USD1.2bn expansion, capacity rationale and project risks | The announcement does not disclose capacity units, utilization or named customer commitments. |
| S8 | 2026-06-17 | official_ir | sources/official-20260714/2026-06-17-投资者关系活动记录表.pdf | EML/silicon photonics route, imported MOCVD equipment, material safeguards | The company did not disclose product-level volume, ASP or customer share. |
| S9 | 2026-06-05 | official_pdf | sources/official-20260714/2026-06-05-股票交易异常波动公告.pdf | official optical segment contribution and risk boundary | It confirms contribution ratios, not future growth. |
| S10 | 2026-03-30 | original_pdf | sources/broker-reports/2026-07-14/2026-03-30-东吴证券-光模块与高端PCB双轮驱动AI基建新龙头.pdf | external industry and segment forecast cross-check | No target price was disclosed in the archived pages. |
| S11 | 2026-04-30 | original_pdf | sources/broker-reports/2026-07-14/2026-04-30-开源证券-2026Q1业绩高增.pdf | external forecast cross-check | No target price was disclosed in the archived pages. |
| S12 | 2026-04-17 | auditable_broker_repost | sources/broker-reports/2026-07-14/2026-04-17-华创证券-研报摘要页.html | external target price, revenue, net profit and EPS anchor | The original licensed PDF is not archived; the public summary preserves the numeric forecast fields. |
| S13 | 2026-07-14 | auditable_consensus_snapshot | sources/market-20260714/10jqka_consensus_20260714.html | 12-institution forecast mean and target-price dispersion context | An aggregate is not a substitute for original broker methodology. |
| S14 | 2026-07-14 | public_snapshot | sources/market-20260714/dragon_tiger_20260701_20260714.json | institutional/seat behavior and crowding | Seat statistics are event snapshots, not a complete investor identity map. |
| S15 | 2026-07-14 | public_snapshot | sources/market-20260714/eastmoney_margin_20260714.html | financing balance and leverage crowding | Eastmoney labels the article as data dissemination; exchange data remains the underlying reference. |
| S16 | 2026-07-14 16:36 CST / notice date 2026-07-15 | official_pdf | sources/official-20260715/2026-07-15-2026年半年度业绩预告.pdf | H1 parent profit, deducted profit, EPS range and Q2 bridge | Unaudited company-level range; no optical segment revenue, ASP, margin or order split. |
| S17 | 2026-07-14 | official_report | sources/official-20260714/2026-04-28-2026年第一季度报告.pdf | named insurance, public-fund, ETF, HKSCC and controller positions | Quarter-end holder snapshot; not current July ownership. |
| S18 | 2026-07-14 | public_snapshot | sources/market-20260714/capital_structure_20260714.json | latest institution/Stock Connect/LHB direction and turnover | Institution seats and HKSCC are aggregates; they do not identify a named fund. |
