# Research Report Review Log

## Executive Verdict

- Publishability: PASS for internal research use.
- External-publication status: CONDITIONAL.
- S-level blockers: none after rebuild and compile.
- Style rebuild status: COMPLETE. The report now uses the new institutional template components across cover, chapters, exhibits, valuation, risks and appendix.
- Content upgrade status: COMPLETE for this corpus. Added customer-chain earnings bridge, company one-pagers, technical parameter gap, valuation sensitivity framework and secondary-market behavior.
- Data upgrade status: SUBSTANTIALLY COMPLETE FOR PUBLIC SOURCES. Added structured financial statements for 11 tickers, Yahoo daily price evidence, one-year PE/PB valuation history, research-report catalog metadata, CNInfo disclosure metadata, main-holder data, downloaded broker PDFs with extracted text, official annual report PDFs with extracted text, official IR records, official customer concentration summary, official top-ten holder and supplier concentration summary, operating-line/forecast-line editable EPS model, directional net-profit sensitivity, and 30-row Eastmoney daily fund-flow proxy for all core/watchlist names. Remaining gaps are not solved by currently accessible public data: platform-specific named-customer revenue split and terminal-grade institutional flow/positioning.

## Review Scope

Reviewed:

- `main.tex`
- `sections/*.tex`
- `main.pdf`
- `research_brief.md`
- `analysis/template_brief.md`
- `analysis/house_view.md`
- `analysis/exhibit_plan.md`
- `analysis/valuation_model.md`
- `analysis/valuation_audit.md`
- `analysis/risk_framework.md`
- `data/source_registry.md`
- `data/claim_audit.md`
- `data/verified_financials.md`
- `data/verified_market_data.md`

Subagents were not invoked because this runtime's delegation rules require explicit user authorization for parallel agent work. The same lenses were reviewed locally.

## S-Level Issues

None remaining.

Previously fixed during rebuild:

1. Legacy report lacked new workflow gates: template benchmark, source registry, claim audit, house view, exhibit plan, valuation audit and rendered review.
2. Legacy outputs were removed and rebuilt around the new `equity-research` workflow.
3. LaTeX compile alignment errors in Chapter 5 were fixed by replacing a fragile high-density table with company-level entries.
4. Full style retrofit completed: old decorative cover replaced by decision dashboard; dense chapter tables replaced with evidence pyramid, segment scorecard, value-chain heatmap, platform-chain map, valuation dashboard, catalyst timeline and risk heatmap.
5. Content-depth retrofit completed: added `analysis/customer_chain_bridge.md`, `analysis/company_one_pagers.md`, `analysis/secondary_market.md`, new Customer-Chain Earnings Bridge chapter, company one-pagers, secondary-market chapter, technical parameter gap and valuation sensitivity framework.
6. Data-source retrofit completed where available: added `data/official_financials.json`, `data/official_financials_summary.md`, `data/historical_market_data.json`, `data/historical_market_summary.md`, `data/eps_sensitivity.json`, `data/eps_sensitivity.md`, `data/external_source_evidence.json`, `data/external_source_evidence.md`, `data/filings_holders_evidence.json`, `data/filings_holders_evidence.md`, `data/full_report_model_summary.md`, `data/official_filing_segment_summary.md`, `data/customer_concentration_summary.md`, `data/editable_eps_model.json`, `data/editable_eps_model.md`, the broker full-report archive under `workspace/research/semiconductor-pcb-20260612/sources/broker-core-20260615/`, and official filing archive under `workspace/research/semiconductor-pcb-20260612/sources/official-annual-core-20260615/`.

## A-Level Issues

1. Source corpus is still not a complete paid-terminal consensus set.
   - Status: original broker PDFs have been archived for the core and watchlist universe where accessible, but target-price history, ratings, and consensus dispersion are not a Wind/Choice-style full street dataset.
   - Future fix: add paid-terminal consensus and complete original global-broker PDFs if available.

2. Market data is archived, not live.
   - Status: disclosed. Quote refresh was attempted and failed/stalled, so valuation uses the 2026-06-12 snapshot only.
   - Future fix: repair the quote adapter or use a verified current quote source before any trading-oriented update.

3. Some customer-chain relationships are broker-stated or inferred rather than company-confirmed.
   - Status: confidence labels added.
   - Future fix: verify through company filings, investor relations transcripts or original reports.

4. Report length is 32 pages, still below the 40-60 page full-report range in the skill archetype.
   - Status: acceptable for this public-source rebuild; should be expanded if intended as a formal external full report with paid data, channel checks and full model appendices.

5. Customer-chain earnings bridge remains a gap framework rather than a full EPS bridge.
   - Status: explicitly disclosed as corpus gap.
   - Future fix: collect customer share, unit content, ASP, gross margin and order backlog by platform.

6. Platform-specific customer-chain revenue split and full institutional flow data remain incomplete.
   - Status: downloaded full broker PDFs and official filings added hard data, including Hudian data-center PCB split, Hudian AI server/HPC revenue, Shennan PCB/substrate split, official top-5 customer concentration and official IR platform comments. They still do not disclose complete customer revenue by NVIDIA/ASIC/domestic compute/optical chain or customer names. Main-holder data and 30-row public dayline fund-flow proxies are available, but full institutional holdings and terminal-grade flow positioning remain uncovered.
   - Future fix: use paid databases, company IR transcripts, or direct filing notes if available.

7. Institutional category-holding API attempted but failed.
   - Status: `data/institutional_holding_evidence.md` records attempts for fund, QFII, social security, broker and insurance holdings. AkShare `stock_report_fund_hold` returned TypeError in this environment.
   - Future fix: use another holdings provider or manually collect from fund/holder databases.

8. Northbound holding and individual fund-flow APIs attempted but failed.
   - Status: `data/flow_positioning_evidence.md` records `stock_hsgt_individual_em` timeout and `stock_individual_fund_flow` remote disconnect.
   - Future fix: use a paid data terminal or a stable alternate source for flow/positioning.

9. Official holder and supplier proxies added.
   - Status: `data/official_holder_supplier_summary.md` summarizes top-ten holder proxies, Hong Kong Securities Clearing holdings where disclosed, visible public fund/social-security/QFII proxies where disclosed, and top-five supplier concentration.
   - Boundary: this is official point-in-time disclosure, not live institutional flow.

10. Investor-relations activity tables inspected.
   - Status: official annual reports contain IR activity tables for Hudian and Shennan with topics including company revenue structure, 800G switch, Thailand capacity, capital expenditure, AI server and basic company updates.
   - Upgrade: Eastmoney notice PDF URLs were resolved and downloaded into `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/`; extracted IR records now provide Q&A evidence for Hudian 800G/CPO/Thailand/revenue structure, Shenghong ASIC/AI PCB/CPO/Thailand, Shennan AI accelerator/high-speed switch/optical module/capex, and Shengyi AI server CCL/GPU/Thailand.
   - Boundary: IR records still avoid naming specific end customers or disclosing exact platform revenue split.

11. Official technology parameters added.
   - Status: `data/official_technology_parameter_summary.md` summarizes public technical evidence including 224G SerDes, 100+ layer high multilayer PCB, 10-stage 30-layer HDI, 16-layer any-layer HDI, 112Gbps/224Gbps switch materials, BT and CBF-RCC materials.
   - Boundary: exact Dk/Df values, line width/spacing, platform BOM and customer-specific specs remain undisclosed.

12. Operating-line editable EPS model added.
   - Status: `data/editable_eps_model.json` now includes revenue, COGS, expenses, operating profit, tax, NPP, margins, operating cash flow and partial capex lines for 002463, 300476, 002916 and 600183; `data/editable_operating_model.md` documents coverage.
   - Boundary: the model is built from broker forecast tables, not company internal assumptions; platform/customer revenue drivers remain incomplete.

13. IR platform-chain evidence added.
   - Status: `data/ir_platform_chain_summary.md` and `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/` archive five IR PDFs and extracted text.
   - Boundary: improves qualitative customer-chain evidence but still does not provide named-customer revenue.

13a. Official SSE IR source added for Shengyi.
   - Status: `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/600183-sse-202505-ir.pdf` confirms, from an SSE-hosted IR PDF, that Shengyi is working with domestic and overseas terminals on GPU and AI projects and already has products in batch supply.
   - Boundary: the official IR record still does not name customers or quantify M8/M9/M10 revenue share.

14. AI server CCL unit-value bridge added.
   - Status: `workspace/research/semiconductor-pcb-20260612/sources/broker-extra-20260615/600183-xinan-high-speed-ccl.pdf` and extracted text provide a broker model for AI server CCL value: CNY 4,000-5,000 per server, GPU board group about CNY 3,000, CPU motherboard about CNY 1,300, OAM about CNY 1,745, UBB about CNY 1,364, with H100 GPU board group using M6/M7+ high-speed CCL.
   - Boundary: this is a 2024 broker framework and should not be treated as current confirmed GB300/Rubin pricing.

14a. Additional Shenghong and Huazheng report sources added.
   - Status: `workspace/research/semiconductor-pcb-20260612/sources/broker-extra-20260615/300476-dazhihui-ai-pcb-depth.pdf` adds Shenghong deep-report evidence on AI PCB, HDI, UBB/switch, capacity and peer comparison. `workspace/research/semiconductor-pcb-20260612/sources/broker-extra-20260615/603186-book118-huazheng-2026.md` adds a limited Huazheng 2026 preview confirming high-end CCL and CBF/BT positioning.
   - Boundary: Huazheng preview is too limited to replace a full current model; named customer revenue remains undisclosed.

14b. Watchlist broker PDFs added.
   - Status: `workspace/research/semiconductor-pcb-20260612/sources/broker-watchlist-20260615/` contains one downloaded broker PDF and extracted text for each watchlist name: 688519, 002436, 301200, 688630, 300400 and 301377.
   - Boundary: these improve watchlist evidence depth but do not close named customer/platform revenue gaps.

14d. Watchlist EPS model added.
   - Status: `data/watchlist_eps_model.md` summarizes forecast-line EPS/PE/NPP data extracted from watchlist broker PDFs where readable.
   - Boundary: watchlist model is forecast-line level, not full operating-line for every watchlist name.

14c. Watchlist official filings added.
   - Status: `workspace/research/semiconductor-pcb-20260612/sources/official-annual-watchlist-20260615/` contains official annual report PDFs/extracted text for watchlist names, including a supplemental corrected 688519 annual report body after the first match was an inquiry-response verification document.
   - Boundary: official filing coverage improves reported data depth but does not disclose named customer/platform revenue split.

15. Advanced public holder proxies added.
   - Status: `data/advanced_holder_evidence.md` adds Sina fund holders, Sina circulating holders, and CNInfo holder-number/concentration data for the five core tickers where available.
   - Boundary: Eastmoney northbound daily statistics only returned a stale 2024 window in direct API tests. HKEX pages state that starting from 2024-08-19 Northbound shareholding information is only available quarterly, explaining why current daily windows fail. Public holder proxies are not equivalent to complete institutional positions or real-time flows.

15a. Watchlist market, valuation and holder evidence added.
   - Status: `data/watchlist_historical_market_summary.md`, `data/watchlist_valuation_history.md`, and `data/watchlist_holder_evidence.md` extend price performance, PE/PB valuation history and Sina holder proxies to watchlist names including 688519, 002436, 301200, 688630, 300400 and 301377.
   - Boundary: these are public proxy datasets, not complete live institutional positions.

16. Eastmoney fund-flow proxy added.
   - Status: `data/eastmoney_fund_flow_evidence.md` adds a 30-row daily fund-flow proxy for all five core names and six watchlist names after retrying the endpoint through `curl` with a browser user-agent.
   - Boundary: Eastmoney market-wide `clist`, targeted realtime `ulist.np/get`, AkShare ranking and category-holder endpoints remain failed/partial. This is a market-flow proxy, not complete institutional positioning or terminal-grade order flow.

16a. AkShare main fund-flow ranking attempted and failed.
   - Status: `data/main_fund_flow_ranking_evidence.md` records `stock_main_fund_flow` attempts for 全部股票, 沪深A股, 沪市A股, 深市A股, 创业板 and 科创板. All returned Eastmoney `clist/get` HTTP 502.
   - Boundary: confirms the all-market public ranking path is unavailable in this environment.

17. Northbound ranking API attempted and failed.
   - Status: `data/northbound_ranking_evidence.md` records AkShare `stock_hsgt_hold_stock_em(market="北向")` attempts for 今日/3日/5日/10日/月/季/年排行, all returning TypeError in this environment.
   - Boundary: current northbound evidence remains limited to official annual-report Hong Kong Securities Clearing holder rows and quarterly/holder proxy data; daily northbound is no longer a valid public-source expectation after the HKEX rule change.

20. Paid data access audited.
   - Status: `data/paid_data_access_audit.md` records that Tushare, WindPy, iFinD and Choice SDKs are not installed and no corresponding market-data credentials are available in the environment. AkShare and Baostock are available and have already been used.
   - Boundary: remaining named-customer split, full live institutional flow and bottom-up platform EPS assumptions require unavailable paid terminal data or non-public company/industry-chain data.

18. Eastmoney important-institution holdings added.
   - Status: `data/important_institution_holding_evidence.md` uses Eastmoney `RPT_NATIONAL_STATISTICS` for 2026-03-31. It found important-institution holdings for Shennan, Hudian and Shengyi, including market cap, share ratio and change.
   - Boundary: this is quarterly disclosed important-institution holding data, not real-time flow; Shenghong and Huazheng were not matched in the core filter for that period.

18a. Eastmoney important-institution holder details added.
   - Status: `data/important_institution_detail_evidence.md` uses Eastmoney `RPT_STOCK_DETAILS_CHANGE` and identifies visible institution holders such as National Social Security Fund portfolios, pension fund portfolios and fund-manager social-security portfolios for the core names where disclosed.
   - Boundary: quarterly disclosed institution details, not real-time positions.

17. Named-customer rumor registry added.
   - Status: `data/named_customer_rumor_registry.md` isolates public claims about NVIDIA, Google TPU/ASIC, Rubin, M9/M10 certification and platform share that are not confirmed by official filings, official IR transcript, original broker PDF or customer/supplier disclosure.
   - Boundary: these claims are not used as confirmed evidence in the main thesis.

19. Customer disclosure-boundary evidence added.
   - Status: `data/customer_disclosure_boundary_evidence.md` records official/near-official responses showing companies do not disclose specific customer names or business details because of commercial confidentiality. Hudian and Shenghong have been upgraded to primary CNInfo/SZSE company-question JSON evidence; Shennan has been upgraded to primary P5W/SZSE QID JSON evidence.
   - Boundary: this does not provide customer revenue split; it documents why the remaining gap cannot be closed from public issuer Q&A.

21. Anonymous top-customer and top-supplier row details added.
   - Status: `data/top_customer_supplier_detail.md` structures official annual-report top-five customer and supplier concentration, including row-level anonymous customer/supplier amounts where extraction was reliable.
   - Boundary: names remain anonymized by issuers; this improves concentration analysis but not named platform split.

## B-Level Issues

1. Visual exhibits are now chartbook-style but still text-heavy in places because the source corpus lacks structured time series, customer revenue bridges and full original report tables.
2. Appendix audit tables remain dense by design; they are now separated from the main argument.
3. Broker target history is limited by public excerpts.

## Verification Evidence

Commands run:

```bash
PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/
pdfinfo workspace/research/semiconductor-pcb-20260612/main.pdf
pdftotext -layout workspace/research/semiconductor-pcb-20260612/main.pdf -
pdftoppm -png -f 1 -l 8 -r 120 workspace/research/semiconductor-pcb-20260612/main.pdf workspace/research/semiconductor-pcb-20260612/rendered/page
```

Results:

- Build command completed successfully.
- `pdfinfo` reports 32 pages, A4, PDF 1.7.
- `pdftotext` confirms Chinese text, decision dashboard, evidence pyramid, segment scorecard, value-chain heatmap, customer-chain earnings bridge, quantified full-report bridge, official filing segment evidence, customer concentration, company one-pagers, latest structured financial snapshot, technical parameter gap, full-report forecast table, one-year PE/PB valuation percentile, editable EPS model status, directional net-profit sensitivity, secondary-market price performance, holder/filing metadata, full-report archive, catalyst timeline, risk heatmap, target-price caveats and disclaimer are present.
- Latest text extraction also confirms anonymous top-customer and top-supplier detail exhibits are present.
- Rendered first eight pages to non-empty PNG files.
- Deterministic report quality evaluator reported 100.0 / excellent for the then-current 55-page PDF in `data/report_quality_eval.md`, with an explicit boundary that this did not prove non-public data availability. Later passes rebuilt the report to 71 pages and refreshed the quality artifact.

Note: the project build command printed `main.pdf (0 pages)`, but `pdfinfo` independently verified the actual PDF has 32 pages. Treat that as a build-tool page-count reporting issue, not a PDF-generation failure.

## Completion Audit Against User Objective

Objective: fill the remaining top-tier report data gaps as completely as possible: original/full reports, official company data, customer-chain revenue split, real EPS sensitivity, historical valuation/holding data, and update the report.

Detailed manifest: `completion_audit_manifest.md`.
Remaining data request pack: `missing_data_request_pack.md`.
Machine-readable unresolved requirements: `unresolved_requirements.json`.
Data room index: `data_room_index.md`.

| Requirement | Evidence | Status |
|---|---|---|
| Original/full broker reports | `workspace/research/semiconductor-pcb-20260612/sources/broker-core-20260615/` contains 5 core PDFs and extracted text; `workspace/research/semiconductor-pcb-20260612/sources/broker-watchlist-20260615/` contains 6 watchlist PDFs and extracted text; extra CCL/Shenghong PDFs archived; `workspace/research/semiconductor-pcb-20260612/sources/broker-supplemental-20260615/` adds 5 more broker PDFs including 41-page Huazheng and 51-page Shengyi deep reports. | Covered for current public-source universe; no longer an "original PDF missing" blocker |
| Official company data | `data/official_financials.json`, `data/official_financials_summary.md`, core/watchlist/Pengding official filing archives; latest structured financial snapshot including 002938; 3 new official CNInfo IR PDFs for Hudian, Shenghong and Shennan. | Covered for the 12-name report universe via structured public financial abstracts, manual Pengding official bridge, official filings and latest official IR checkpoints |
| Customer-chain revenue split | `data/full_report_model_summary.md`, `data/supplemental_report_archive_summary.md`, `data/official_filing_segment_summary.md`, `data/customer_concentration_summary.md`, `data/top_customer_supplier_detail.md`, `data/ir_platform_chain_summary.md`, `data/customer_disclosure_boundary_evidence.md`; report includes Hudian data-center PCB split/application mix, Hudian AI server/HPC revenue, Shennan PCB/substrate split plus AI data-center proxy, official top-5 customer concentration, anonymous customer/supplier row detail, official IR platform-chain comments, AI server CCL unit-value bridge, and issuer disclosure-boundary evidence. | Substantially covered by segment/platform/customer-concentration proxies; complete named NVIDIA/ASIC/domestic/optical customer revenue split unavailable in public filings/reports and issuers cite commercial confidentiality |
| Real EPS sensitivity | `data/eps_sensitivity.md`, `data/editable_eps_model.json`, `data/editable_eps_model.md`, `data/editable_operating_model.md`, `data/watchlist_eps_model.md`; full-report forecast table, operating-line editable model and watchlist forecast-line model added; Huazheng now has 2025E-2027E forecast-line model from Zheshang. | Substantially covered from broker models; still lacks customer-chain bottom-up assumptions |
| Historical valuation | `data/external_source_evidence.md`; one-year PE/PB percentile table added. | Covered for core five |
| Holdings / positioning | `data/filings_holders_evidence.md` gives main holders; `data/official_holder_supplier_summary.md` adds official top-ten holder proxies; `data/advanced_holder_evidence.md` adds Sina fund holders, circulating holders and CNInfo holder concentration; `data/important_institution_holding_evidence.md` adds Eastmoney important-institution holdings; `data/important_institution_detail_evidence.md` adds detailed institution-holder names; `data/eastmoney_fund_flow_evidence.md` now covers 30-row daily fund-flow proxy for all 5 core and 6 watchlist tickers; `data/main_fund_flow_ranking_evidence.md`, `data/institutional_holding_evidence.md`, `data/flow_positioning_evidence.md`, and `data/northbound_ranking_evidence.md` record failed ranking/category/northbound attempts. | Public holder and dayline flow proxies covered; full terminal-grade realtime order flow and complete institutional positioning unavailable from tested public sources |
| Report update and verification | `main.pdf` rebuilt; `pdfinfo` 32 pages; text extraction confirms new sections. | Covered |

Additional evidence collected after the first audit:

| Additional requirement pressure point | Evidence | Status |
|---|---|---|
| IR Q&A / platform comments | `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/` contains five IR PDFs and extracted text; `data/ir_platform_chain_summary.md` summarizes 800G, CPO, ASIC, UBB, AI server, Thailand and CCL comments. | Covered for public IR records found |
| AI server CCL unit economics | `workspace/research/semiconductor-pcb-20260612/sources/broker-extra-20260615/600183-xinan-high-speed-ccl.pdf` and `data/full_report_model_summary.md` add OAM/UBB/CPU board CCL value bridge. | Covered as broker framework |
| Official technology parameters | `data/official_technology_parameter_summary.md` now covers the 12-name universe, adding watchlist and Pengding official/filing/IR technical evidence such as Nanya M6-M10/PCIe, Xingsen mSAP/FCBGA, Han's CNC AI-server drilling certification, Circuit Fabology WLP2000/4um capability, Dingtai micro-drill mix and Pengding 70+ layer MLPCB/24-28 layer HDI capability. | Covered where publicly disclosed; exact Dk/Df, platform BOM and named platform revenue remain unavailable |
| Official holder/supplier proxy | `data/official_holder_supplier_summary.md` adds official top-ten holder proxies and top-five supplier concentration. | Covered as official point-in-time proxy |
| Operating-line EPS model | `data/editable_eps_model.json` and `data/editable_operating_model.md` include revenue, COGS, expenses, operating profit, tax, NPP, margins, OCF and partial capex for four core names. | Covered from broker models |
| Local forecast range | `data/forecast_range_analysis.md` converts downloaded broker PDF model lines into revenue/NPP/EPS ranges for the five core names. | Covered as public-source forecast range, not paid-terminal consensus |
| Enhanced fund holdings | `data/fund_holding_enhanced_evidence.md` adds CNInfo fund heavy-holding ranks/counts/market value for three periods and Sina fund-name-level holder rows for all core/watchlist names. | Covered as public-source holder proxy, not active/passive terminal database |
| Fund holder style proxy | `data/fund_holder_style_proxy.md` uses fund-name rules to separate active-like, ETF/index/enhanced and bond-like visible fund holdings. | Covered as public-source style proxy, not official active/passive classification |
| Fund type mapping | `data/fund_type_mapping_evidence.md` maps top visible holder fund codes to Eastmoney fund types such as 混合型-偏股, 股票型, 指数型 and 债券型. | Covered as public fund-type examples, not complete active/passive ownership database |
| Annual EPS sensitivity matrix | `data/eps_sensitivity_matrix.md` converts operating-line broker models into 2026E-2028E NPP sensitivity under gross-margin, revenue and opex shocks. | Covered as public-source operating-line sensitivity, not customer/platform bottom-up EPS |
| Watchlist EPS stress test | `data/watchlist_eps_sensitivity_bridge.md` converts watchlist broker forecast-line evidence into 2026E NPP/EPS +/-10% stress tests and 2027E/2028E EPS continuity checks; Chapter 8 includes Exhibit 24b. | Covered for 688519, 301200, 688630, 300400 and 301377 at forecast-line level; 002436 upgraded to NPP/EPS stress coverage after Huaxin/Kaiyuan PDF refresh; still not customer/platform bottom-up EPS |
| Official named customer-chain evidence | `data/official_named_customer_chain_evidence.md` adds Nanya official named PCB customers, terminal customer certifications and M6-M10 high-speed CCL generation evidence. | Covered for watchlist CCL customer-chain certification; still not revenue split |
| Watchlist customer/supplier concentration | `data/watchlist_customer_supplier_concentration.md` adds official top-5 customer and supplier concentration for six watchlist names, including named rows for Nanya inquiry response and Xinqi Microequipment. | Covered for watchlist concentration evidence; still not AI-platform revenue split |
| Watchlist product-customer bridge | `data/watchlist_product_customer_bridge.md` adds issuer-level product-line revenue, gross margin, customer concentration and PCB-chain bridge for Nanya New Material, Xingsen Technology, Han's CNC, Circuit Fabology, Jintuo and Dingtai; Chapter 5 now includes Exhibit 12c-2 and 12c-3. | Covered for all six original watchlist names at product/customer-concentration level; still not named terminal-platform revenue split |
| H-share prospectus customer evidence | `data/hshare_prospectus_customer_evidence.md` adds Hudian and Shenghong H-share application/global-offering customer concentration and application revenue evidence. | Covered as official exchange-filing evidence; still not named platform revenue split |
| H-share customer relationship evidence | `data/hshare_customer_relationship_evidence.md` adds customer type, credit term, payment method, product/service category and relationship-start evidence from H-share documents. | Covered as customer-quality evidence; still anonymized |
| H-share anonymous customer time series | `data/hshare_anonymous_customer_time_series.md` adds anonymized customer-level sales and share time series for Hudian and Shenghong. | Covered as closest public customer-revenue bridge; still not named platform split |
| H-share product economics | `data/hshare_product_economics_evidence.md` adds Hudian layer revenue/volume and Shenghong product revenue/volume/ASP evidence. | Covered as public product-economics bridge; still not named customer/platform EPS |
| H-share gross-margin bridge | `data/hshare_gross_margin_bridge_evidence.md` adds Hudian application gross margin and Shenghong product gross margin bridge. | Covered as public product profitability bridge; still not named customer/platform margin |
| H-share supplier economics | `data/hshare_supplier_economics_evidence.md` adds supplier concentration, raw-material cost share, supplier type and credit-term evidence. | Covered as public supplier-cost and working-capital support, not named supplier/platform margin |
| Official capex/capacity evidence | `data/official_capex_capacity_evidence.md` adds official utilization, capex, ramp, depreciation and impairment evidence for Hudian, Shennan and Huazheng. | Covered as official company-data upgrade; still not project-level full D&A schedule |
| H-share capacity utilization evidence | `data/hshare_capacity_utilization_evidence.md` adds Hudian base-level utilization and Shenghong product-category capacity/utilization/expansion data. | Covered as product-capacity support for bottom-up EPS assumptions |
| Long-horizon valuation history | `data/long_horizon_valuation_history.md` adds three-year and five-year PE/PB/PCF public valuation series for core and watchlist names. | Covered as public valuation band evidence, not paid-terminal standardized history |
| Official Q1 filing archive | `workspace/research/semiconductor-pcb-20260612/sources/official-q1-20260615/`, `data/official_q1_filing_archive_summary.md`, and `data/official_q1_filing_cross_check.md` archive 11 official 2026Q1 report PDFs/text and map key financial metrics to filing evidence. | Covered as filing-level support for latest financial checkpoint; manual PDF review still recommended for external publication |
| Working-capital and cash conversion | `data/working_capital_cash_conversion.md` adds OCF/NPP, OCF/revenue, current ratio and quick ratio checks for all 12 names including Pengding. | Covered as EPS-quality evidence, not customer/platform bottom-up model |
| Working-capital days | `data/working_capital_days_analysis.md` adds DSO, DIO, DPO and CCC approximations from official Q1 balance-sheet lines, now including Pengding. | Covered as public-source working-capital assumption support, not full model schedule |
| Global-broker gap fallback archive | `data/global_broker_gap_fallback_summary.md` and `workspace/research/semiconductor-pcb-20260612/sources/broker-global-fallback-20260615/` add fallback original PDFs for Pengding, Hudian and Shengyi where UBS/JPM/Goldman originals remain unavailable. | Covered as fallback original-PDF depth; does not replace missing global-broker originals |
| Original PDF refresh | `data/original_pdf_refresh_20260616.md` and `workspace/research/semiconductor-pcb-20260612/sources/broker-original-refresh-20260616/` add nine more public original PDFs: two CMBI Shengyi updates, four Pengding reports from Tianfeng, Kaiyuan, Minsheng and Xingye, two Hudian reports from Xinda and Tianfeng, and one Huazheng annual-review report from Zheshang, including a 30-page Pengding deep report, a 14-page Xingye historical forecast report, Hudian 2025H1 / 2025 preliminary-result update reports and Huazheng 2026E-2028E model update. New Hibor probes for UBS/Pengding and JPM/Shenghong still returned terminal download pages; Sina Goldman/Shengyi is a repost. | Improves public original-PDF corpus for Shengyi, Pengding, Hudian and Huazheng; still does not close UBS/JPM/Goldman original-PDF gap |
| Hudian forecast range refresh | `data/forecast_range_analysis.md` and `sections/ch08_valuation.tex` incorporate the newly archived Xinda and Tianfeng Hudian PDFs. Hudian 2026E NPP range widens to 51.98--58.00亿元 and 2027E to 67.78--90.67亿元. | Improves EPS forecast-risk disclosure; still not a customer/platform bottom-up EPS bridge |
| Huazheng forecast range refresh | `data/huazheng_forecast_refresh_20260616.md`, `data/forecast_range_analysis.md` and `sections/ch08_valuation.tex` incorporate the newly archived Zheshang annual-review PDF. Huazheng now has 2028E revenue/NPP/EPS coverage and a three-statement appendix. | Improves forecast-line coverage; still not a customer/platform bottom-up EPS bridge |
| Huazheng dilution scenario refresh | `data/official_huazheng_refinancing_evidence.md` and `sections/ch08_valuation.tex` incorporate the official dilution announcement. Under 2026 NPP flat/+10%/-10% assumptions, post-issue basic EPS is 1.73/1.91/1.56 yuan. | Improves official EPS dilution sensitivity; still not project operating economics or customer/platform bottom-up EPS |
| CMBI / Citi / HSBC non-Hibor probe | `data/cmbi_citi_hsbc_probe_20260616.md` and `workspace/research/semiconductor-pcb-20260612/sources/broker-cmbi-citi-hsbc-probe-20260616/` add two official CMBI-hosted historical Shengyi PDFs from 2023 and 2021. Current Citi/HSBC/CMBI query paths did not expose usable 2026 original PDFs. | Improves official-hosted historical broker evidence; still does not close current global-broker original-PDF or named customer/platform gap |
| Latest market refresh audit | `data/latest_market_refresh_audit.md` and `data/tencent_realtime_market_snapshot_20260616.md` record 2026-06-15 close proxy availability, Eastmoney realtime failure and Tencent quote success for 12/12 market cap/PE/PB | Covered as market freshness audit; valuation anchors upgraded to Tencent public quote proxy |
| Northbound / Stock Connect history | `data/northbound_individual_history_evidence.md` adds public Stock Connect single-stock historical total holding baseline for 9/11 names. | Covered as historical total-holding baseline, not current beneficial-owner positioning |
| HKCC current-quarter proxy | `data/hkcc_current_quarter_proxy.md` extracts Hong Kong Securities Clearing Company holdings from official 2026Q1 top-shareholder tables. | Covered as quarterly nominee-holder proxy, not beneficial-owner positioning |
| Watchlist positioning coverage audit | `data/watchlist_positioning_coverage_audit.md` reconciles the coverage matrix with archived public proxies: watchlist fund holders and circulating holders cover 6/6, Eastmoney 30-row fund-flow covers 6/6, margin/block trades cover 5/6, Dragon-Tiger List and lock-up expiry cover 6/6. | Matrix fund_flow corrected to True for six original watchlist tickers; important_institution remains False because no visible public important-institution row was returned for those names |
| Watchlist important-institution gap audit | `data/watchlist_important_institution_gap_audit.md` inspects archived Eastmoney important-institution JSON and confirms `stock_holdings` has no original watchlist single-stock rows; a Nanya-related social-security basket row is not attributable to Nanya alone. | Keep important_institution=False for 688519, 002436, 301200, 688630, 300400 and 301377; do not backfill this field with fund-holder, circulating-holder or fund-flow proxies |
| Customer-side public source probe | `data/customer_side_public_source_probe_20260616.md` tests NVIDIA / Google TPU / Microsoft Azure / AWS Trainium public supplier-list paths. Results were generic supplier-quality pages, SEO lists, blogs and reposts, not official named PCB/CCL supplier revenue disclosures. | Reinforces named platform/customer revenue split as non-public; do not use customer-side blogs or marketing lists as confirmed evidence |
| Apple official supply-chain probe | `data/apple_customer_side_official_probe_20260616.md` and `workspace/research/semiconductor-pcb-20260612/sources/probe-customer-side-20260616/` archive Apple official supply-chain page, legacy supplier-list path tests and Newsroom clean-energy articles. Apple Newsroom confirms Avary Holding joined Apple Supplier Clean Energy Program in 2020, while the current supply-chain page and legacy supplier-list paths did not expose Pengding / Zhen Ding / Avary product, revenue or order details; third-party supplier-list mirror returned a security-check HTML page rather than an auditable PDF. | Adds an Apple-side official relationship/program signal for Avary, but still does not close named platform/customer revenue split |
| Customs / BOL public probe | `data/customs_bol_probe_20260616.md` and `workspace/research/semiconductor-pcb-20260612/sources/probe-customs-bol-20260616/` archive ImportGenius, ImportYeti and Panjiva public-page probes for WUS, Victory Giant and Nvidia. | Public pages show generic shipment profiles, non-AI counterparties, paywalls or bot blocks; no attributable NVIDIA/Google/AWS/Microsoft PCB/CCL revenue split recovered |
| 300400 name audit | Corrected stale references that mapped `300400` to 东威科技. The covered ticker is 劲拓股份; broad industry-chain mentions of 东威科技 are now marked as non-covered ticker context where retained. | Fixes watchlist universe consistency and prevents ticker/name mismatch in market, guidance and catalog files |
| Pengding coverage-matrix audit | `ticker_evidence_coverage_matrix.md` now includes `002938` as `theme-reserve`, reflecting the expanded universe after Pengding was added to the report. | 002938 has broker PDF, official filing, structured financial, segment/customer, historical price, valuation, fund-holder, circulating-holder, important-institution, fund-flow and EPS-model coverage; remaining boundary is named platform/customer revenue split |
| Missing data request pack refresh | `missing_data_request_pack.md` was updated to reflect the latest public-source coverage: Tencent valuation refresh, watchlist EPS stress tests, customer-side public-source probe, customs/BOL probe, and public holder/flow proxies. | Remaining request list now focuses on non-public / paid-terminal items rather than already completed public-source work |
| Paid data access refresh | `data/paid_data_access_audit.md` was refreshed against the project `.venv` and environment/config files. AkShare/Baostock remain available; Tushare, WindPy, iFinD, Choice, JQData, RQData, Datayes, Bloomberg/Refinitiv and paid BOL credentials are unavailable. | Confirms remaining hard gaps cannot be closed locally without new credentials or direct company/customer data |
| Machine-readable unresolved refresh | `unresolved_requirements.json` now records `last_reviewed`, current public-source coverage state and evidence files for each remaining hard gap. | Prevents future runs from repeating already exhausted public-source paths; status remains `blocked_by_unavailable_paid_or_non_public_data` |

Final conclusion: the public-source data upgrade is complete to the practical limit of accessible public sources. Customer-chain evidence is handled in three layers: confirmed official/broker/IR data, segment/platform proxies, and isolated rumor registry. The full objective is not strictly complete because complete platform-specific named-customer revenue split and terminal-grade realtime institutional flow/positioning remain unavailable from public filings, broker PDFs, IR records and tested public APIs. The EPS model is now operating-line/forecast-line editable, but still not a bottom-up customer-by-platform model because the missing customer-chain assumptions are not public.

## 2026-06-15 Supplemental Public-Source Pass

Additional original PDFs and official records were downloaded into `workspace/research/semiconductor-pcb-20260612/sources/broker-supplemental-20260615/`:

- 5 broker PDFs: Huazheng Zheshang 41-page deep report, Shennan CMBI English update, Hudian Zhongtai update, Shenghong Guosheng GPU+ASIC update, Shengyi Guohai 51-page CCL deep report.
- 3 official CNInfo IR PDFs: Hudian 2026-05-13, Shenghong 2026-05-08 and Shennan 2026-05-07.

Evidence file: `data/supplemental_report_archive_summary.md`.

Report/data updates:

- `data/full_report_model_summary.md` and `data/editable_eps_model.*` now include Huazheng 2025E-2027E model from Zheshang, so Huazheng is no longer treated as model-uncovered.
- `sections/ch05_customer_bridge.tex` now includes Hudian 2025 application mix and Thailand utilization, Shenghong official ASIC/GPU/TPU progress language, Shennan AI data-center share proxy and FC-BGA ramp, Shengyi high-speed CCL architecture, and Huazheng current CCL/CBF/BT model evidence.
- `sections/ch08_valuation.tex` now reflects CMBI Shennan TP RMB288, Zhongtai/Hudian second-source model, and Huazheng 2026E/2027E PE from the new Zheshang model.

Remaining blockers after this pass are narrower: original public-source PDF depth and official company data are materially improved; the unresolved gap is now specifically named customer/platform revenue split, complete all-ticker real-time flow, and customer/platform bottom-up EPS assumptions.

## 2026-06-15 Fund-Flow Retry

The Eastmoney `push2his` dayline fund-flow endpoint was retried through `curl` with a browser user-agent after Python urllib calls were rejected. The retry produced 30 rows for all 5 core and 6 watchlist tickers.

Evidence file: `data/eastmoney_fund_flow_evidence.md`.

Report update: `sections/ch09_secondary_market.tex` now includes a core-name fund-flow proxy table and a watchlist fund-flow proxy table. This closes the public dayline flow proxy gap for the current universe. It does not close terminal-grade realtime order flow, active/passive fund ownership, category institution history, or northbound beneficial-owner positioning.

## 2026-06-15 Forecast Range Upgrade

`data/forecast_range_analysis.md` now converts the downloaded broker PDF model lines into a local public-source forecast range. This improves the report's EPS discipline beyond single-source forecasts:

- Hudian: Zhongyou + Zhongtai provide a tight 2026E-2028E NPP range.
- Shenghong: Kaiyuan + Guosheng show a wide 2026E-2027E NPP range, making customer ramp assumptions visible.
- Shennan: Pacific + CMBI provide a two-source NPP/EPS range and explicit CMBI target methodology.
- Shengyi: Pacific + Guohai show model-date dispersion and forecast-revision risk.
- Huazheng: Zheshang provides current 2025E-2027E model coverage, still single-source.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 20b with multi-source forecast ranges.

## 2026-06-15 Enhanced Fund-Holding Pass

AkShare `fund_report_stock_cninfo` and `stock_fund_stock_holder` were tested and used to generate `data/fund_holding_enhanced_evidence.md`.

Evidence added:

- CNInfo fund heavy-holding rows for 2026Q1, 2025Q4 and 2025Q3.
- 2026Q1 CNInfo coverage for all five core names and five of six watchlist names.
- Sina fund-name-level latest-period rows for all 11 covered names, including top visible funds and aggregate visible market value.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 25b with fund heavy-holding proxies. This narrows the holding-data gap, but does not close active/passive classification, complete fund ownership history or paid terminal institutional positioning.

## 2026-06-15 EPS Sensitivity Matrix Upgrade

`data/eps_sensitivity_matrix.md` and `.json` now convert broker operating-line models into annual net-profit sensitivity tables. The matrix covers:

- Gross margin -1pct and -2pct.
- Revenue -5pct.
- Opex +2pct of revenue.
- Combined downside of revenue -5pct plus gross margin -1pct.

Coverage:

- Operating-line sensitivity for 002463, 300476, 002916 and 600183 across available forecast years.
- Forecast-line revenue-shock proxy for 603186 because the current Huazheng PDF lacks full operating-line detail.

Report update: `sections/ch08_valuation.tex` now includes a 2026E annual EPS sensitivity matrix. This improves true EPS discipline but still does not close customer/platform bottom-up EPS because named customer revenue, ASP, shipment, segment margin and depreciation assumptions are not disclosed.

## 2026-06-15 Official Named-Customer Chain Pass

Keyword search across official filings and archived IR/report text found the strongest new official named/semi-named customer-chain evidence in Nanya New Materials' 2025 annual report.

Evidence added:

- `data/official_named_customer_chain_evidence.md` records official named PCB customers: 健鼎科技、奥士康、景旺电子、深南电路、瀚宇博德、生益电子、方正科技、沪电股份、胜宏科技、广东骏亚.
- The same filing names terminal key-customer certifications including 华为、中兴通讯、浪潮、曙光、新华三、HPE、微软.
- It also states M6-M8 products are batch-applied by domestic leading compute customers, M9 is in NPI, M10 is in overseas core compute-terminal certification, and NOUYA8U completed Huawei core-customer access and scaled mass production.

Report update: `sections/ch05_customer_bridge.tex` now includes Exhibit 12b. This improves official customer-chain evidence for the CCL watchlist, but it still does not disclose revenue by named customer/platform.

## 2026-06-15 Fund Style Proxy Pass

`data/fund_holder_style_proxy.md` and `.json` now classify visible fund-name-level holdings into rule-based buckets:

- active-like
- passive ETF / linked / index
- index-enhanced
- bond or fixed-income-like

This adds an active/passive-like ownership proxy from public fund names. It shows core names are mostly active-like by visible market value, while Shenghong has a larger ETF/index component. The proxy is explicitly not a Wind/Choice official active/passive classification.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 25c with fund holder style proxy.

## 2026-06-16 Fund Type Mapping Pass

AkShare `fund_name_em` was used to map top visible holder fund codes to Eastmoney fund types. The output is stored in `data/fund_type_mapping_evidence.md` and `.json`.

This improves the fund-holder style evidence by adding formal public fund-type labels for examples, while the full stock-level active/passive split remains a rule-based proxy and not a Wind/Choice official classification.

## 2026-06-15 Official Capex and Capacity Pass

`data/official_capex_capacity_evidence.md` now captures official/direct capex and capacity evidence:

- Hudian: Thailand base revenue, overseas customer certification above 70%, 2026Q1 utilization above 90%, and 2026Q2 targeted capacity release.
- Shennan: Nantong IV and Thailand ramp, explicit depreciation/amortization and unit fixed-cost pressure, Guangzhou substrate ramp, FC-BGA 22-layer mass production and 24-layer+ R&D/sample progress.
- Huazheng: Thailand CCL production base investment up to USD 60mn, fixed-asset and construction-in-progress balances, impairment indicators from low utilization at Huazheng Energy, and Zheshang's Zhuhai high-grade CCL capacity-to-sales bridge.

Report update: `sections/ch06_companies.tex` now includes Exhibit 14b. This improves company official data and EPS-risk evidence without inventing customer revenue.

## 2026-06-15 Long-Horizon Valuation Pass

AkShare `stock_zh_valuation_baidu` was re-run with `period=近三年` and `period=近五年` for PE/PB/PCF where available. The output is stored in `data/long_horizon_valuation_history.md` and `.json`.

Evidence added:

- Three-year PE/PB/PCF percentile for all five core names.
- Three-year PE/PB percentile for all six watchlist names.
- Five-year PE/PB availability and percentile check for all 11 names.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 21b. This improves historical valuation evidence beyond the earlier one-year band. The remaining valuation gap is now mainly paid-terminal standardization rather than lack of long-horizon public data.

## 2026-06-15 Watchlist Customer/Supplier Concentration Pass

Official watchlist filings and Nanya's inquiry response were parsed for top-5 customer and supplier concentration. The output is stored in `data/watchlist_customer_supplier_concentration.md`.

Evidence added:

- Nanya: top-5 customer sales 18.27亿元 / 34.96%; top-5 supplier purchase 25.99亿元 / 55.34%; inquiry response names CCL/prepreg customers such as 奥士康、方正科技、深南电路、景旺电子.
- Xingsen, Dazu, Xinqi, Jintuo and Dingtai: official top-5 customer/supplier concentration from annual reports.
- Xinqi Microequipment has named customers including 鹏鼎控股、胜宏科技、景旺电子、V-Technology and 深南电路.

Report update: `sections/ch05_customer_bridge.tex` now includes Exhibit 12c. This further narrows customer-chain concentration evidence but does not disclose AI platform revenue by end customer.

## 2026-06-15 Official Q1 Filing Archive Pass

CNInfo disclosure search was used to locate and download official 2026Q1 reports for all 11 current report-universe names. The PDFs and extracted text are archived in `workspace/research/semiconductor-pcb-20260612/sources/official-q1-20260615/`.

Evidence added:

- 11/11 official 2026Q1 PDFs downloaded and verified as PDF files.
- 11/11 Q1 PDFs extracted to text.
- `data/official_q1_filing_archive_summary.md` maps every ticker to its archived PDF/text.
- `data/official_q1_filing_cross_check.md` maps key revenue, NPP, OCF, EPS and ROE evidence to the archived filing text. Wrapped PDF table labels have been manually reconciled in the evidence file.

Report update: `sections/ch06_companies.tex` now states the latest structured financial table is backed by archived official Q1 filings. This closes the earlier caveat that latest financials lacked original filing support.

## 2026-06-15 Working Capital and Cash Conversion Pass

`data/working_capital_cash_conversion.md` now adds cash-conversion and working-capital checks from structured financials and archived official Q1 filings.

Evidence added:

- OCF/NPP and OCF/revenue for all 12 names.
- Current ratio and quick ratio for all 12 names.
- Core-name table in `sections/ch06_companies.tex`.

Key findings:

- Shenghong and Xinqi have OCF above NPP in 2026Q1.
- Dazu, Xingsen, Nanya and Dingtai have negative OCF despite profit growth, indicating ramp/working-capital pressure.
- Shennan has positive but low OCF/NPP, consistent with material procurement and ramp/capex pressure.

This improves EPS-quality analysis but does not replace customer/platform bottom-up assumptions.

## 2026-06-16 Working-Capital Days Pass

`data/working_capital_days_analysis.md` and `.json` now calculate approximate DSO, DIO, DPO and cash-conversion cycle from archived official Q1 balance-sheet lines and structured revenue/cost data.

Report update: `sections/ch06_companies.tex` now includes Exhibit 14c with core-name working-capital days. This improves bottom-up EPS support for working-capital assumptions, but still does not provide customer/platform revenue, ASP or shipment assumptions.

## 2026-06-15 Northbound / Stock Connect History Pass

AkShare `stock_hsgt_individual_em` was used to retrieve Eastmoney Stock Connect single-stock holding histories. The output is stored in `data/northbound_individual_history_evidence.md` and `.json`.

Evidence added:

- Historical Stock Connect total holding data for 9/11 report-universe names.
- Core examples as of 2024-08-16: Hudian 8586.63万股 / 4.48% of A-shares, Shenghong 1604.62万股 / 1.86%, Shennan 1165.65万股 / 2.27%, Shengyi 17671.08万股 / 7.45%.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 27b with historical Stock Connect holding baseline. This improves northbound history evidence but does not provide current post-rule-change beneficial-owner or institution-level positioning.

## 2026-06-16 HKCC Current-Quarter Proxy Pass

Official 2026Q1 filings were searched for 香港中央结算有限公司 / Hong Kong Securities Clearing Company rows. The result is stored in `data/hkcc_current_quarter_proxy.md`.

Evidence added:

- HKCC current-quarter proxy covers all five core names and most watchlist names.
- Core examples: Hudian 19388.13万股 / 10.08%, Shennan 2557.74万股 / 3.75%, Shengyi 15102.36万股 / 6.22%, Huazheng 443.98万股 / 2.83%.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 27c. This improves current-quarter northbound proxy evidence, but HKCC remains a nominee/clearing holder and does not identify beneficial owners or institution-level positioning.

## 2026-06-16 Global-Broker Gap Fallback Pass

Web search for missing UBS/JPM/Goldman original PDFs did not locate the target global-broker originals. Valid fallback original PDFs were downloaded into `workspace/research/semiconductor-pcb-20260612/sources/broker-global-fallback-20260615/`:

- Pengding Zheshang update report.
- Hudian Dongguan deep report.
- Hudian Haitong deep report.
- Shengyi Southwest 2026Q1 update.
- Shengyi Guojin deep report.

Evidence file: `data/global_broker_gap_fallback_summary.md`.

Report update: `sections/ch01_dashboard.tex` moves Pengding from pure insufficient-evidence isolation into watchlist/fallback-evidence status, and `sections/ch12_appendix.tex` adds the fallback archive. The missing UBS/JPM/Goldman original-PDF gap remains open.

## 2026-06-16 Latest Market Refresh Pass

AkShare/Eastmoney realtime quote refresh was retried:

- `stock_zh_a_spot_em()` returned remote disconnected.
- `stock_individual_info_em()` and `stock_bid_ask_em()` returned JSON decode errors for sample tickers.
- `stock_zh_a_hist()` returned remote disconnected for sample tickers.

However, 2026-06-15 close prices are available from Eastmoney fund-flow dayline and Yahoo historical chart evidence. `data/latest_market_refresh_audit.md` now records this boundary.

Report update: `sections/ch08_valuation.tex` now states that latest public close proxies are available through 2026-06-15, but PE anchors were later upgraded to the 2026-06-16 Tencent quote snapshot after Eastmoney realtime failed but Tencent succeeded.

## 2026-06-16 H-Share Prospectus Customer Evidence Pass

HKEX application/global-offering documents were downloaded for Hudian and Shenghong into `workspace/research/semiconductor-pcb-20260612/sources/official-hshare-prospectus-20260616/`.

Evidence added:

- Hudian H-share application document: AI server/HPC revenue series for 2023, 2024, 2025, 2026Q1 and 2025Q1; top-five customer share rises from 46.0% in 2023 to 58.4% in 2026Q1; largest-customer share rises to 19.5% in 2026Q1.
- Shenghong H-share global offering document: top-five customer share 27.1%/25.1%/51.0% in 2023/2024/2025; largest-customer share 6.3%/8.3%/29.7%; customer categories include global AI technology solution providers, large cloud service providers, data-center equipment OEMs and server manufacturers.

Report update: `sections/ch05_customer_bridge.tex` now includes Exhibit 12d. This is one of the strongest public customer-chain upgrades so far, but it still does not provide named NVIDIA/Google ASIC/platform revenue.

## 2026-06-16 H-Share Product Economics Pass

Hudian and Shenghong H-share documents were mined for product revenue, volume and ASP evidence. The output is stored in `data/hshare_product_economics_evidence.md`.

Evidence added:

- Hudian layer mix: 32-layer+ PCB revenue rose from 7.61亿元 in 2023 to 42.50亿元 in 2025 and reached 32.1% of revenue in 2026Q1.
- Hudian AI server/HPC revenue series: 12.40/29.75/30.06/7.34亿元 for 2023/2024/2025/2026Q1.
- Shenghong HDI economics: HDI revenue rose to 74.25亿元 in 2025, while HDI ASP rose from 2,351元/sqm in 2024 to 13,475元/sqm in 2025.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 23b. This is the strongest public product-economics bridge found so far, but it still does not provide named customer/platform revenue.

## 2026-06-16 H-Share Customer Relationship Pass

H-share documents were further mined for customer relationship quality variables. The output is stored in `data/hshare_customer_relationship_evidence.md`.

Evidence added:

- Hudian top-customer product/service categories, credit terms, payment methods, customer types and relationship-start years.
- Shenghong anonymized but specific customer descriptions, including Customer E as a leading global technology company focused on accelerated computing and AI infrastructure, headquartered in the U.S. and listed on Nasdaq.

Report update: `sections/ch05_customer_bridge.tex` now includes these customer-quality details inside Exhibit 12d. This improves top-tier customer analysis but remains anonymized and does not disclose named platform revenue.

## 2026-06-16 H-Share Capacity Utilization Pass

Hudian and Shenghong H-share documents were mined for capacity, output, utilization and expansion evidence. The output is stored in `data/hshare_capacity_utilization_evidence.md`.

Evidence added:

- Hudian 2026Q1 overall utilization 99.1%, with major production bases near full utilization.
- Shenghong 2025 HDI utilization 97.7%.
- Shenghong disclosed expansion plan for Vietnam, Thailand, Huizhou, Changsha and Yiyang, including additional high-layer MLPCB and HDI annual capacity.

Report update: `sections/ch06_companies.tex` now includes Exhibit 14d with H-share capacity utilization and expansion. This improves capacity-side bottom-up EPS support but remains separate from named customer/platform revenue.

## 2026-06-16 H-Share Gross-Margin Bridge Pass

H-share documents were mined for product/application gross margin evidence. The output is stored in `data/hshare_gross_margin_bridge_evidence.md`.

Evidence added:

- Hudian data-communication PCB gross margin reached 39.6% in 2026Q1, above smart automotive PCB at 19.6%.
- Shenghong HDI gross margin rose from 22.5% in 2024 to 43.5% in 2025; MLPCB gross margin rose from 15.2% to 24.4%.

Report update: `sections/ch08_valuation.tex` now includes these gross-margin bridge items in Exhibit 23b. This materially improves public product-level EPS support, while named customer/platform gross margin remains undisclosed.

## 2026-06-16 H-Share Supplier Economics Pass

Hudian and Shenghong H-share documents were mined for supplier concentration, material-cost share, supplier type and credit terms. The output is stored in `data/hshare_supplier_economics_evidence.md`.

Evidence added:

- Hudian raw-material cost share rose from 55.8% of cost of sales in 2023 to 62.3% in 2026Q1; top-five supplier purchase share stayed around 41%--42%.
- Shenghong raw-material cost share rose from 58.6% in 2023 to 65.9% in 2025; top-five supplier purchase share rose to 45.2% in 2025.
- Supplier credit terms and supplier product types are available for Hudian and supplier profiles are available for Shenghong.

Report update: `sections/ch04_supply_chain.tex` now includes Exhibit 9b. This improves margin and working-capital assumptions from the supply side, while named supplier/platform margin remains undisclosed.

## 2026-06-16 H-Share Anonymous Customer Time-Series Pass

H-share customer tables were converted into `data/hshare_anonymous_customer_time_series.md`.

Evidence added:

- Hudian anonymized customer A/B/C/E/F/D sales, revenue shares, product/service type, credit terms and relationship start years across 2023/2024/2025/2026Q1 where disclosed.
- Shenghong anonymized customer A/B/C/E/F/H/I/J sales and descriptions across 2023/2024/2025 where disclosed.
- Key signal: Shenghong Customer A rose from 4.52亿元 / 5.7% in 2023 to 57.38亿元 / 29.7% in 2025; Hudian Customer F reached 12.12亿元 / 19.5% in 2026Q1.

Report update: Exhibit 12d now references this time series. This is the closest public customer-revenue bridge found, but customer names and platform mapping remain undisclosed.

## 2026-06-16 H-Share Official Turnover-Days Pass

Hudian and Shenghong H-share documents were mined for issuer-disclosed receivable, inventory and payable turnover days. The output is stored in `data/hshare_official_turnover_days.md`.

Evidence added:

- Hudian disclosed trade receivable turnover days of 99/91/91/87 for 2023/2024/2025/2026Q1, inventory turnover days of 87/76/91/100, and trade payable turnover days of 85/86/96/99.
- Shenghong disclosed trade receivable turnover days of 135.6/122.1/93.3 for 2023/2024/2025, inventory turnover days of 72.6/75.3/76.1, and trade payable turnover days of 101.5/101.7/144.6.

Report update: `sections/ch06_companies.tex` now includes Exhibit 14c-2. This strengthens the working-capital bridge by adding official turnover-day evidence beside the Q1 balance-sheet approximation, especially for Shenghong's strong OCF and supplier-credit support during AI/HPC ramp.

## 2026-06-16 CMBI Sector Global Report Pass

A CMBI sector-level PCB/CCL PDF was downloaded from the broker site and text-extracted into `workspace/research/semiconductor-pcb-20260612/sources/broker-sector-global-20260616/`.

Evidence added:

- CMBI cites Prismark 2025E global PCB market growth of 12.8%, revised from 7.6%, and 2024 global PCB sales of about US$74bn.
- The report cites China at about 56% of 2024 global PCB production value.
- The report cites 2024 global CCL market value of about US$15bn, +18% YoY, high-speed specialty CCL growth of about 50% YoY, and global CCL top-10 share of about 77%.
- The report frames copper-led raw-material pressure as a pass-through advantage for CCL leaders and a margin stress test for commodity PCB suppliers.

Report update: `sections/ch04_supply_chain.tex` now includes Exhibit 8b. This improves industry-structure and cost-pass-through evidence, but does not replace missing Goldman/JPM/UBS company originals or named customer/platform revenue splits.

## 2026-06-16 HKEX Stock Connect Quarterly Pass

HKEX official Stock Connect Northbound Shareholding Search pages were queried for Shanghai and Shenzhen Connect. Raw HTML was archived under `data/raw_hkex_stock_connect/`, and the parsed evidence is stored in `data/hkex_stock_connect_quarterly_evidence.md`.

Evidence added:

- HKEX states that from 2024-08-19 northbound shareholding information is available only on a quarterly basis.
- 2026-03-31 HKEX official quarterly Stock Connect shareholding now covers 11/11 core/watchlist tickers.
- Highest current-quarter Stock Connect participation in the target set: Hudian 10.07%, Shengyi 6.30%, Circuit Fabology 4.08%, Shennan 3.75%, Huazheng 2.83%, Shenghong 2.85%.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 27b-2 and updates the data-boundary language. This materially improves northbound coverage, but still does not provide beneficial-owner, broker-custodian, active/passive fund classification, daily post-rule-change northbound changes or terminal-grade realtime order flow.

## 2026-06-16 HKEX Stock Connect QoQ Change Pass

HKEX form POST was used to retrieve the prior available quarterly page. Submitting `txtShareholdingDate=2026/03/31` returned `Shareholding Date: 2025/12/31`, which was archived as raw HTML for both Shenzhen and Shanghai Connect.

Evidence added:

- 2025Q4 and 2026Q1 HKEX official quarterly Stock Connect data now cover 11/11 target tickers.
- Largest absolute Q1 increases: Hudian +50.67mn shares, Shengyi +25.84mn shares, Circuit Fabology +4.95mn shares.
- Largest pct-point Q1 increases: Circuit Fabology +3.76ppt, Hudian +2.63ppt, Huazheng +1.94ppt, Shengyi +1.08ppt.
- Q1 decreases: Shenghong -3.13mn shares / -0.37ppt, Fastprint -3.30mn shares / -0.19ppt, Nanya -0.18mn shares / -0.08ppt.

Report update: Exhibit 27b-2 now shows both current-quarter holding and QoQ change. This improves public positioning evidence, while beneficial-owner and terminal-grade order-flow gaps remain.

## 2026-06-16 Shengyi Official Refresh Pass

Three official documents were downloaded and text-extracted into `workspace/research/semiconductor-pcb-20260612/sources/official-shengyi-refresh-20260616/`: Shengyi Technology 2025H1 report, Shengyi Technology 2025Q3 report and Shengyi Electronics 2025 refinancing inquiry response.

Evidence added:

- Shengyi Technology 2025H1 official segment evidence: CCL external revenue 84.67亿元, PCB external revenue 37.53亿元, CCL segment net profit 9.20亿元, PCB segment net profit 5.65亿元; no single external customer accounted for 10% or more of consolidated revenue.
- Shengyi Technology 2025Q3 YTD delivery: revenue 206.14亿元, +39.80% YoY; parent net profit 24.43亿元, +78.04% YoY; operating cash flow 31.76亿元, +181.28% YoY.
- Shengyi Electronics official AI HDI / high-layer compute PCB plan: AI HDI project total investment 20.32亿元 and planned capacity 16.72万平方米/year; high-layer compute PCB project total investment 19.37亿元 and planned capacity 70万平方米/year.
- Technology and customer evidence: 5-6 stage HDI has completed customer certification and achieved small-batch sales; 7-8 stage HDI and 9-10 stage HDI remain in development/certification path; customer names were exempted from disclosure.
- Capacity/order evidence: 2025 1-9M PCB utilization 93.64%; 2026-02 backlog 34.95亿元, including 7.32亿元 HDI and 26.84亿元 multilayer-board orders.

Report update: `sections/ch06_companies.tex` and `sections/ch05_customer_bridge.tex` now reference the official Shengyi refresh. This materially improves official company evidence, but does not disclose named customer/platform revenue split.

## 2026-06-16 Shengyi Project-Level EPS Bridge Pass

The Shengyi Electronics refinancing inquiry response was further mined for project-level economics and depreciation/project-cost impact.

Evidence added:

- AI computing HDI project: price assumption 13,253.04元/sqm, full-ramp annual volume 16.72万 sqm, full-ramp gross margin 26.95%.
- High-layer compute PCB project: price assumption 2,854.20元/sqm, full-ramp annual volume 70.00万 sqm, full-ramp gross margin 22.49%.
- Combined ramp: T+5 new revenue 43.21亿元 and new net profit 6.06亿元; T+6--T+13 new net profit 5.94--6.27亿元.
- Depreciation/project-cost burden: T+5 about 2.36亿元; at full ramp, up to 2.62% of revenue and up to 24.60% of net profit.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 23c. This is a real official project-level EPS bridge for Shengyi Electronics, but it is still not a named-customer/platform bottom-up EPS model.

## 2026-06-16 Shengyi Anonymized Customer Revenue Pass

The Shengyi Electronics refinancing inquiry response was further mined for anonymized customer revenue, export-revenue verification and customer-chain explanations.

Evidence added:

- R customer total sales rose from 2.65亿元 in 2022 to 10.20亿元 in 2024 and 29.37亿元 in 2025 1-9M; the filing links R customer to the X terminal customer's designated EMS and AI-server high-value PCB volume orders.
- B customer, F customer, C customer, Q customer and P customer rows were extracted with sales amount and product type where disclosed.
- 2025 1-9M export revenue reached 41.75亿元, 63.34% of main-business revenue; adjusted USD export revenue and customs declaration data had a -0.15% difference.
- Server/computer board became the largest application field, reaching 68.01% of revenue in 2025 1-9M; top-five customer revenue share rose to 63.35%.

Report update: `sections/ch05_customer_bridge.tex` now includes Exhibit 12e. This materially improves customer-chain revenue evidence, but customer names and named platform revenue remain exempted from disclosure.

## 2026-06-16 Shengyi Application Mix and Margin Bridge Pass

The Shengyi Electronics refinancing inquiry response was mined for application-level revenue-share and gross-margin bridge evidence.

Evidence added:

- Server/computer board revenue share rose from 17.92% in 2022 to 48.96% in 2024 and 68.01% in 2025 1-9M.
- Communication-network board share fell from 60.92% in 2022 to 19.86% in 2025 1-9M.
- Main-business gross margin moved from 21.24% in 2022 to 11.13% in 2023, 19.42% in 2024 and 29.60% in 2025 1-9M.
- Official explanation: AI server high-value PCB demand, higher selling prices and mix shift drove server/computer board revenue share and gross-margin contribution sharply higher.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 23d. This improves application-level EPS attribution but still keeps individual application margins and named customer/platform revenue as disclosure gaps.

## 2026-06-16 Official Quarterly Bridge Pass

CNInfo static attachments and issuer/stock-exchange mirrors were used to download official 2025H1 and 2025Q3 filings for the five core companies. The archive is stored in `workspace/research/semiconductor-pcb-20260612/sources/official-quarterly-20260616/`, and extracted bridge data is stored in `data/official_quarterly_bridge_evidence.md`.

Evidence added:

- 5/5 core 2025H1 official PDFs archived and text-extracted.
- 5/5 core 2025Q3 official PDFs archived and text-extracted.
- Official delivery bridge now covers 2025H1, 2025Q3 YTD and 2026Q1 for revenue, parent net profit, operating cash flow and EPS where disclosed.
- Key official 2025Q3 YTD numbers: Hudian revenue 135.12亿元 / parent NPP 27.18亿元; Shenghong revenue 141.17亿元 / parent NPP 32.45亿元; Shennan revenue 167.54亿元 / parent NPP 23.26亿元; Shengyi revenue 206.14亿元 / parent NPP 24.43亿元; Huazheng revenue 31.96亿元 / parent NPP 0.63亿元.

Report update: `sections/ch06_companies.tex` now includes Exhibit 14a-2. This reduces reliance on broker delivery commentary but still does not provide named platform/customer revenue split.

## 2026-06-16 Watchlist Official Quarterly Bridge Pass

Official 2025H1 and 2025Q3 filings were further collected for the six watchlist names, extending the quarterly bridge to the full 11-name report universe.

Evidence added:

- 6/6 watchlist 2025H1 official PDFs archived and text-extracted.
- 6/6 watchlist 2025Q3 official PDFs archived and text-extracted.
- Watchlist 2025Q3 YTD official bridge: Nanya revenue 36.63亿元 / parent NPP 1.58亿元; Fastprint revenue 53.73亿元 / parent NPP 1.31亿元; Han's CNC revenue 39.03亿元 / parent NPP 4.92亿元; Circuit Fabology revenue 9.34亿元 / parent NPP 1.99亿元; Jintuo revenue 5.96亿元 / parent NPP 0.86亿元; Dtech revenue 14.57亿元 / parent NPP 2.82亿元.
- Cash-flow differentiation is now visible: Jintuo and Dtech were positive in 2025Q3 YTD, while Nanya, Fastprint, Han's CNC and Circuit Fabology still had weak or negative OCF.

Report update: `sections/ch06_companies.tex` now includes Exhibit 14a-3. This improves official watchlist delivery evidence but does not change named customer/platform disclosure boundaries.

## 2026-06-16 Goldman China PCB/CCL Repost Check

Targeted search found a visible Xueqiu repost titled "高盛：中国PCB行业进入加速模式（原文完整）". The visible text was archived as `data/goldman_china_pcb_xueqiu_summary.md` and mirrored under `workspace/research/semiconductor-pcb-20260612/sources/broker-global-fallback-20260615/`.

Evidence added:

- Visible repost claims Goldman first covered Victory Giant, WUS and Shengyi with Buy ratings and visible target prices of RMB550/RMB127/RMB111.
- Visible repost includes thematic claims on AI PCB/CCL market growth, 800G/1.6T and M8/M9 migration.

Boundary: this is a web repost/summary, not an original Goldman PDF or complete report. It does not close the original global-broker report requirement and should not be used as audited forecast evidence.

## 2026-06-16 Fund Holding Quarterly Bridge Pass

Existing CNInfo fund heavy-holding data was converted into a three-quarter bridge covering 2025Q3, 2025Q4 and 2026Q1. The output is stored in `data/fund_holding_quarterly_bridge.md`.

Evidence added:

- Core names showed broad public fund-heavy-holding expansion in 2025Q4 followed by sharp 2026Q1 contraction.
- 2026Q1 vs 2025Q4 visible MV changes: Hudian -166.98亿元, Shenghong -259.84亿元, Shennan -143.92亿元, Shengyi -235.46亿元, Huazheng -4.41亿元.
- Watchlist differentiation: Han's CNC 2026Q1 MV remained near 2025Q4 despite fund count falling; Dtech and Circuit Fabology retained more visible MV than Fastprint.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 25b-2. This improves historical fund-positioning evidence, but still does not provide complete institutional ownership, beneficial owners or official active/passive classification.

## 2026-06-16 Shareholder Count Concentration Bridge Pass

CNInfo holder-number data in `data/advanced_holder_evidence.json` was converted into `data/shareholder_count_quarterly_bridge.md`.

Evidence added:

- 2026Q1 shareholder counts rose versus 2025Q4 for all five core names.
- 2026Q1 average shares per holder fell across all five core names, suggesting broader holder-base dispersion.
- This complements the fund-heavy-holding bridge: visible fund-heavy-holding MV fell in 2026Q1 while shareholder count rose.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 25b-3. This improves public chip-concentration evidence, but remains a shareholder-count proxy rather than beneficial-owner or institutional-positioning data.

## 2026-06-16 Official IR Refresh Pass

Latest official June 2026 IR records were downloaded for Hudian, Shenghong and Shennan into `workspace/research/semiconductor-pcb-20260612/sources/ir-core-refresh-20260616/`, with extracted text and an index. The evidence summary is stored in `data/official_ir_refresh_20260616.md`.

Evidence added:

- Hudian 2026-06-05 IR: Thailand base 2025 revenue 2.89亿元 and 2026Q1 revenue 2.95亿元; data-communications division overseas customer certification above 70%; 2026Q1 utilization above 90%; AI server and high-speed networking products accelerating into mass introduction/delivery.
- Shenghong 2026-06-07 IR: 100-layer+ high-layer PCB, 10-stage 30-layer HDI, 16-layer any-layer HDI and next-gen 14-stage 36-layer HDI R&D/certification; ASIC customers progressing smoothly; GPU accelerator and TPU supporting-board supply expanding; Huizhou mSAP line for 1.6T optical module demand has full orders and good utilization.
- Shennan 2026-06-03 IR: Q1 PCB utilization remained high due to AI compute infrastructure hardware demand; substrate revenue share improved; Nantong phase IV and Thailand project are ramping; FC-BGA 22-layer and below mass production, 24-layer+ in R&D/sample stage; 2026 capex focused on PCB/substrate.

Report update: `sections/ch05_customer_bridge.tex` and `sections/ch06_companies.tex` now reference this latest official IR refresh. It improves current official customer-chain/capacity evidence, but still does not disclose named customer or platform revenue.

## 2026-06-16 Shennan Refinancing / AI Compute PCB Capex Bridge Pass

Official Shennan 2026 refinancing documents were downloaded or archived under `workspace/research/semiconductor-pcb-20260612/sources/official-shennan-refinancing-20260616/`. The extracted evidence is stored in `data/official_shennan_refinancing_evidence.md`.

Evidence added:

- Wuxi Shennan AI compute electronic-circuit product project total investment 45.36亿元, proposed fundraising use 36.00亿元.
- Product scope: existing high-speed, high-density, high-layer PCB used for AI servers and switches.
- Investment breakdown: production equipment 28.00亿元, engineering/construction 14.08亿元, land 0.70亿元, construction-period interest 0.18亿元, initial working capital 2.41亿元.
- Construction period: 1 year.
- Official customer/market statement: existing AI compute PCB orders are described as full, and core customers are described as having clear capacity-demand intentions.
- Dilution bridge: 2026 EPS scenarios of 4.83/5.31/5.79 yuan under flat/+10%/+20% parent NPP assumptions; the issuer states the announcement does not include raised-fund operating contribution.

Report update: `sections/ch06_companies.tex` now includes the Shennan capex bridge and `sections/ch08_valuation.tex` now includes Exhibit 23e. This improves official capex/dilution evidence, but does not disclose project price, gross margin, named customer order amount or detailed project net-profit forecast.

## 2026-06-16 Shennan Feasibility Clean-PDF Pass

The Shennan fundraising-use feasibility analysis was re-downloaded directly from CNInfo static attachment `1225369238.PDF`, replacing the earlier Sina HTML mirror. The issuance-plan analysis report `1225369237.PDF` was also archived and text-extracted.

Evidence added:

- Feasibility analysis confirms project land-use right certificate, project filing and environmental approval are completed.
- It cites Prismark: 2024 global server/data-storage PCB market size US$10.916bn, +33.1% YoY; 2029E US$25.729bn, 18.7% CAGR.
- It states Shennan has mastered high-speed signal-integrity design, high-precision multilayer lamination and laser micro-blind/buried-via processes, and has achieved batch delivery.
- It states Shennan has deep strategic cooperation with leading AI server manufacturers, switch manufacturers, cloud-service providers and chip companies.

Report source update: `data/official_shennan_refinancing_evidence.md` and `workspace/research/semiconductor-pcb-20260612/sources/official-shennan-refinancing-20260616/index.md` now reflect the clean official PDF. Main report text already captured the key project capex bridge, so no new exhibit was required in this pass.

## 2026-06-16 Watchlist IR Refresh Pass

Issuer/official-mirror IR records were downloaded for Nanya New Material, Circuit Fabology and Han's CNC into `workspace/research/semiconductor-pcb-20260612/sources/ir-watchlist-refresh-20260616/`. The evidence summary is stored in `data/watchlist_ir_refresh_evidence.md`.

Evidence added:

- Nanya: NY6300S entered multi-customer PCIe Gen5 server mass production; PCIe Gen6 completed top-customer evaluation; AI server materials broke through multiple domestic GPU programs; M8 material obtained domestic terminal certification and small-batch production; M9 under testing by multiple PCB customers.
- Circuit Fabology: WLP2000 wafer-level packaging equipment reached 2um precision and was undergoing mass-production testing at multiple top customers; direct-write lithography has advantages in advanced packaging.
- Han's CNC: CCD six-axis independent mechanical drilling machine with 3D back-drilling and drill-test integration passed next-generation AI server PCB certification and entered mass production at multiple leading customers.

Report update: `sections/ch05_customer_bridge.tex` now includes Exhibit 12f. This improves watchlist technology/customer-validation evidence, but still does not disclose named customer revenue or order values.

## 2026-06-16 Huazheng Official High-Grade CCL Refinancing Pass

Huazheng's 2026 fundraising feasibility analysis was downloaded from CNInfo static attachment `1225026464.PDF`, extracted and summarized in `data/official_huazheng_refinancing_evidence.md`.

Evidence added:

- High-grade CCL project total investment 10.04亿元, proposed fundraising use 10.00亿元.
- Planned annual capacity 1,200万张 high-grade CCL via Zhuhai Huazheng New Materials.
- Product focus includes high-speed CCL, high-frequency CCL, high-thermal-conductivity metal substrate and HDI CCL.
- Main applications include AI servers, switches and optical modules.
- Official filing says halogenated Ultra Low-loss materials have achieved batch sales; halogen-free Ultra Low-loss materials passed validation at one important end customer and are being certified by several important end customers.

Report update: `sections/ch06_companies.tex` now includes the official Huazheng high-grade CCL project bridge and updates the Huazheng one-pager. This improves official CCL expansion evidence, but does not disclose M8/M9 revenue share, CBF/BT project economics or named customer orders.

## 2026-06-16 Huazheng P5W/SSE Interaction Evidence Pass

The P5W investor Q&A API for Huazheng was parsed directly using `interaction/getNewR.shtml`, and raw JSON was archived as `data/raw_huazheng_cbf_p5w.json` and `data/raw_huazheng_bt_p5w.json`. The summarized evidence is stored in `data/huazheng_p5w_interaction_evidence.md`.

Evidence added:

- 2025-11-24 reply: CBF build-up insulation film has achieved small-batch order sales for some items; other items are actively progressing terminal validation; current small-batch orders do not yet affect operating performance.
- 2023-05-05 reply: CBF has entered validation processes at downstream IC-substrate factories, packaging/testing factories and chip terminals for CPU/GPU semiconductor-chip packaging.
- BT/class-BT replies: class-BT/BT board materials have market applications, including memory packaging; the issuer said domestic market share remains low and the product line is a key layout direction.

Report update: `sections/ch05_customer_bridge.tex` and `sections/ch06_companies.tex` now reference this official interaction evidence. This improves Huazheng CBF/BT validation status, but does not disclose named customer revenue, order value, margin or shipment.

## 2026-06-16 Eastmoney Northbound Participant Detail Pass

Eastmoney's public `RPT_NORTH_ORG_HOLDDETAIL_NEW` API was used to fetch 2026Q1 Stock Connect participant/custodian detail for all 11 covered tickers. Raw JSON is stored in `data/eastmoney_northbound_participant_detail_20260331.json`, and summary evidence in `data/eastmoney_northbound_participant_detail_20260331.md`.

Evidence added:

- 11/11 report names returned participant-level rows.
- Top participant examples: HSBC for Hudian/Shenghong/Shennan/Shengyi/Nanya/Dtech, Citi for Fastprint/Circuit Fabology, Standard Chartered for Han's CNC, Morgan Stanley for Jintuo, Merrill Lynch Far East for Huazheng.
- Top-five participant market-value share is above 80% for all 11 names, showing high custody concentration.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 27b-3. This improves northbound custody-structure evidence, but remains participant/custodian data rather than beneficial-owner disclosure.

## 2026-06-15 Final Public-Source Sweep

Final targeted public web searches were run for Hudian, Shenghong, Shennan, Shengyi and Huazheng around named customer/platform revenue split, M8/M9/M10 certification/revenue, ASIC/TPU/optical exposure and current Huazheng model coverage. The results were broker abstracts, reposts, social-media claims, old PDFs or limited previews. No new source met the report's evidence rule for confirmed customer revenue: company filing, official IR transcript, original broker PDF with explicit attribution, or customer/supplier disclosure.

Evidence file: `data/final_public_source_sweep.md`.

Report update: `sections/ch09_secondary_market.tex` was corrected so the data-availability table no longer says valuation percentile and watchlist relative performance are missing. It now reflects the collected public proxy coverage: core and watchlist Yahoo daily price data, one-year Baidu PE/PB percentiles, public holder proxies and partial Eastmoney fund-flow evidence.

## 2026-06-16 Eastmoney Northbound Participant Quarterly Bridge Pass

Eastmoney's public `RPT_NORTH_ORG_HOLDDETAIL_NEW` API was extended from the prior 2026Q1 single-quarter participant/custodian detail into a four-quarter bridge for 2025-06-30, 2025-09-30, 2025-12-31 and 2026-03-31. Raw JSON is stored in `data/eastmoney_northbound_participant_quarterly_bridge_20250630_20260331.json`, and summary evidence in `data/eastmoney_northbound_participant_quarterly_bridge_20250630_20260331.md`.

Evidence added:

- 11/11 covered names returned quarterly participant/custodian rows for the tested quarters.
- Hudian, Shennan, Huazheng, Nanya, Han's CNC, Circuit Fabology, Jintuo and Dtech show higher participant-held share counts from 2025Q2 to 2026Q1; Shenghong, Shengyi and Fastprint decline over the same window. Shengyi still shows a material QoQ rebound in 2026Q1.
- 2026Q1 top participant identities are unchanged from the prior single-quarter check: HSBC for Hudian/Shenghong/Shennan/Shengyi/Nanya/Dtech, Citi for Fastprint/Circuit Fabology, Standard Chartered for Han's CNC, Morgan Stanley HK for Jintuo and Merrill Lynch Far East for Huazheng.
- Top-five participant market-value share remains above 80% for all 11 names in 2026Q1, indicating high custody concentration.

Report update: `sections/ch09_secondary_market.tex` now upgrades Exhibit 27b-3 from a single-quarter participant/custodian detail table to a 2025Q2-2026Q1 quarterly bridge. This improves public custody-structure history, but remains participant/custodian data rather than beneficial-owner disclosure, active/passive fund classification or terminal-grade order flow.

## 2026-06-16 Global Broker Original PDF Probe Pass

A targeted public-search probe was run for the missing UBS / JPMorgan / Goldman original-report gaps using exact-title and filetype queries. No original UBS, JPMorgan or Goldman PDF was found. Five valid public PDFs were downloaded into `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/`, text-extracted and indexed.

Evidence added:

- Dongwu Hudian note: `沪电股份：赴港递表加速全球化，谷歌TPU放量迎量价齐升`, 3 pages, with 2025E-2027E revenue/net-profit/EPS model and Google TPU chain framing.
- Huajin Shenghong note: `胜宏科技：聚焦AI服务器高端产品需求，业绩增长动能强劲`, 7 pages, with AI data-center revenue-share language, HDI/high-layer capability, Vietnam/Thailand project revenue assumptions and 2025E-2027E model.
- Dongwu 60-page sector deep dive: `AI驱动PCB全面升级：材料、工艺与架构革新引领产业新周期`, adding M9/PTFE, HVLP copper foil, mSAP/SAP, CoWoP, midplane, orthogonal backplane and company mapping.
- Huatai Pengding note: `鹏鼎控股：卡位AI端侧浪潮，加快算力硬板投入`, 8 pages, with target price, 2025E-2027E EPS and server/optical-module certification/capacity evidence.
- HKEX Pengding business-overview filing excerpt, 43 pages, with Frost & Sullivan AI/HPC PCB market-position and technical-capability evidence.

Report update: `sections/ch12_appendix.tex` now expands Appendix Exhibit C to include the five new probe files, and `data/global_broker_original_pdf_probe_20260616.md` records the source boundary. This improves public original-PDF depth but still does not close the missing UBS/JPM/Goldman original-report requirement.

## 2026-06-16 Pengding HKEX Business Evidence Pass

The Pengding HKEX draft filing business-overview excerpt archived in `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/05-002938-hkex-prospectus-business-overview.pdf` was reviewed for official-style customer-chain, technology and capacity evidence. The evidence summary is stored in `data/pengding_hkex_business_evidence.md`.

Evidence added:

- Frost & Sullivan ranking: Pengding is cited as No. 1 globally by sales revenue in AI and high-performance computing PCB in 1H2025, and No. 1 in high-build-up HDI PCB and high-layer-count MLPCB with 14+ layers for the cited categories.
- Revenue/net profit: 2024 revenue RMB10.7315bn and net profit RMB1.1544bn; 9M2025 revenue RMB14.1173bn and net profit RMB3.2448bn.
- Customer concentration: top-five customers accounted for 50.9% of 9M2025 revenue, and the largest customer accounted for 29.6%. Customer E is described as a U.S. NASDAQ-listed global leading accelerated-computing and AI-infrastructure company; 9M2025 sales to Customer E were RMB592.3mn / 4.2% of revenue.
- Technology/capacity: products cover AI accelerator cards, AI servers, data-center switches, UBB and optical transceivers; 70+ layer MLPCB mass production, 100+ layer MLPCB technical capability, 24-layer 6+12+6 HDI and 28-layer 8+12+8 HDI mass production; 9M2025 HDI utilization 91.1%.

Report update: `sections/ch05_customer_bridge.tex` now includes Exhibit 12g, and `sections/ch01_dashboard.tex` / `sections/ch10_guidance.tex` move Pengding from excluded status into the theme-reserve watchlist. The UBS original PDF remains unavailable, and anonymous customer codes are not mapped to named platform revenue.

## 2026-06-16 Pengding Official Filing Pass

Official Pengding A-share filings were collected into `workspace/research/semiconductor-pcb-20260612/sources/official-pengding-20260616/`: 2025 annual report, 2025 interim report, 2025 Q3 report and 2026 Q1 report. Text extraction succeeded for all four PDFs. The evidence summary is stored in `data/pengding_official_filing_evidence.md`.

Evidence added:

- Official delivery bridge: 2025H1 revenue 163.75亿元, parent NPP 12.33亿元, OCF 42.77亿元; 2025Q1-Q3 revenue 268.55亿元, parent NPP 24.08亿元, OCF 42.59亿元; 2025A revenue 391.47亿元, parent NPP 37.38亿元, OCF 72.86亿元; 2026Q1 revenue 79.86亿元, parent NPP 4.63亿元, OCF 30.97亿元.
- 2025 product mix: communications boards 254.37亿元 / 64.98% / +4.95%; consumer electronics and computer boards 112.87亿元 / 28.83% / +15.72%; automotive/server/other boards 21.19亿元 / 5.41% / +106.67%.
- Customer/supplier concentration: 2025 top-five customer sales 350.17亿元 / 89.45%; largest customer A 311.82亿元 / 79.65%; customer B is Hon Hai / Foxconn group and related by substance-over-form principle; top-five suppliers 67.29亿元 / 21.28%.
- AI / capacity language: 2025 annual report says AI server product revenue grew more than 1x YoY, SLP entered 800G/1.6T optical modules, 3.2T products are in R&D/design, Thailand Phase I trial production began in May 2025 and server/optical-module products passed customer certification. 2026 capex plan is 168亿元.

Report update: `sections/ch05_customer_bridge.tex` now cross-checks Pengding customer concentration using the A-share annual-report basis, and `sections/ch06_companies.tex` adds Pengding to the watchlist official quarterly delivery bridge. This improves official data coverage and customer-chain evidence for Pengding, but does not disclose named platform revenue or customer-by-platform EPS assumptions.

## 2026-06-16 Pengding Market Positioning Pass

After Pengding was upgraded into the watchlist/theme-reserve bucket, public secondary-market evidence was extended to include 002938. Yahoo Finance chart data and Eastmoney `push2his` fund-flow daykline were fetched and summarized in `data/pengding_market_positioning_evidence.md`; raw parsed data is stored in `data/pengding_market_positioning_evidence.json`, with raw Eastmoney response archived as `data/raw_pengding_eastmoney_fund_flow.json`.

Evidence added:

- Yahoo daily price records: 279 records from 2025-04-21 to 2026-06-15; adjusted close increased from 27.63 to 104.64; period return +278.76%; max drawdown -33.32%.
- Eastmoney 30-row fund-flow proxy: latest date 2026-06-15; latest main net inflow -5.56亿元; 30-row main net inflow sum -10.14亿元; latest close 104.64 and latest pct change +3.07%.
- Valuation percentile was not refreshed because AkShare is unavailable in the current environment and the underlying Baidu endpoint was not reliably reproduced in this pass.

Report update: `sections/ch09_secondary_market.tex` now adds Pengding to the watchlist fund-flow proxy table and the watchlist price-performance table. PE and percentile are explicitly shown as N/A for Pengding rather than inferred. This improves market-performance and public flow coverage for the expanded watchlist, but does not close paid-terminal positioning, beneficial-owner data or valuation-percentile coverage for Pengding.

## 2026-06-16 Pengding Valuation History Pass

The earlier Pengding market-positioning pass used the system Python and could not access AkShare. The project virtual environment `.venv/bin/python` was then checked and confirmed to include AkShare 1.18.41, pandas and requests. AkShare `stock_zh_valuation_baidu` was run for Pengding (`002938`) across PE TTM, PB and PCF for 近一年, 近三年 and 近五年. Raw JSON is stored in `data/pengding_valuation_history.json`, and summary evidence in `data/pengding_valuation_history.md`.

Evidence added:

- 近一年: PE TTM 65.32 / percentile 95.34%; PB 7.00 / percentile 95.34%; PCF 33.28 / percentile 95.34%.
- 近三年: PE/PB/PCF latest values are the same on 2026-06-15, with percentile 98.45%.
- 近五年: PE/PB/PCF latest values are the same on 2026-06-15, with percentile 99.12%.

Report update: `sections/ch09_secondary_market.tex` now replaces Pengding's PE and PE percentile N/A with public Baidu/AkShare valuation evidence. The prior `data/pengding_market_positioning_evidence.md` boundary was corrected to reference `data/pengding_valuation_history.md`. This closes the Pengding-specific valuation percentile gap, but remains a public valuation-band proxy rather than a Wind/Choice standardized valuation database.

## 2026-06-16 Pengding Holding Proxy Pass

After Pengding entered the watchlist, public holding proxies were extended to 002938. Evidence is stored in `data/pengding_holding_proxy_evidence.md` and `.json`; raw AkShare probe output is archived in `data/raw_pengding_fund_holder_probe.json`.

Evidence added:

- HKEX official quarterly Stock Connect raw HTML already contained Pengding. 2026Q1 aggregate CCASS participant holding was 5707.02万股 / 2.46%, down 566.38万股 / -0.24 pct-pt from 2025Q4.
- CNInfo fund heavy-holding bridge: 2025Q3 16.04亿元 / 56 funds; 2025Q4 71.79亿元 / 775 funds; 2026Q1 13.02亿元 / 65 funds. Visible public fund holdings fell sharply from 2025Q4 to 2026Q1.
- Sina latest fund-holder proxy: 2026Q1 has 111 visible rows and 20.05亿元 total visible market value. Top visible holders include Nuode Hexin, Hongde Ruize and Zhuque products.

Report update: `sections/ch09_secondary_market.tex` now adds Pengding to Exhibit 25b-2 fund heavy-holding quarterly bridge and Exhibit 27b-2 HKEX official Stock Connect quarterly holding. This improves public holder/positioning coverage for the expanded watchlist, but remains public proxy data rather than beneficial-owner positioning, full paid institutional holdings or official active/passive classification.

## 2026-06-16 Pengding Northbound Participant Bridge Pass

Eastmoney public `RPT_NORTH_ORG_HOLDDETAIL_NEW` was run for Pengding (`002938.SZ`) across 2025-06-30, 2025-09-30, 2025-12-31 and 2026-03-31. Raw JSON is stored in `data/pengding_northbound_participant_quarterly_bridge.json`; summary evidence is stored in `data/pengding_northbound_participant_quarterly_bridge.md`.

Evidence added:

- Pengding returned participant/custodian rows for all four quarters.
- 2026Q1 participant-held shares were 5707.02万股 / 29.77亿元 market value, down 566.38万股 from 2025Q4 but up 926.41万股 from 2025Q2.
- HSBC was the top participant in every tested quarter. In 2026Q1, HSBC held 2669.35万股 / 13.93亿元. Top-five participant market-value share was 95.8%.

Report update: `sections/ch09_secondary_market.tex` now adds Pengding to Exhibit 27b-3 Northbound participant / custodian quarterly bridge. This aligns Pengding with the existing participant/custodian evidence layer for the expanded watchlist, but remains custody-structure evidence rather than beneficial-owner positioning or active/passive institutional classification.

## 2026-06-16 Pengding Forecast Model Pass

Huatai and Zheshang original/fallback PDFs for Pengding were parsed for forecast-line evidence. Summary evidence is stored in `data/pengding_forecast_model_evidence.md` and `.json`.

Evidence added:

- Huatai Securities (2025-08-13): target price 69.20 yuan, Buy; 2026E/2027E revenue 471.91/545.78亿元, parent NPP 57.22/70.17亿元, EPS 2.47/3.03, PE 21.00x/17.13x.
- Zheshang Securities (2026-02-04): Add; 2026E/2027E revenue 490.54/580.14亿元, parent NPP 55.76/72.44亿元, EPS 2.40/3.12, PE 25.67x/19.76x.
- Forecast-line downside proxy: a 5% revenue shortfall maps to 2026E NPP of 54.36亿元 under Huatai and 52.97亿元 under Zheshang using each model's 2026E net-profit margin.

Report update: `sections/ch08_valuation.tex` now adds Pengding to Exhibit 20 broker model forecasts and Exhibit 24 sensitivity matrix; `data/watchlist_eps_model.md/json` now include 002938. This closes Pengding's watchlist forecast-line gap, but remains a forecast-line proxy rather than a full operating-line or customer/platform bottom-up EPS model.

## 2026-06-16 Pengding IR Evidence Pass

Four official Pengding investor-relations PDFs were downloaded into `workspace/research/semiconductor-pcb-20260612/sources/ir-pengding-20260616/` and text-extracted. The evidence summary is stored in `data/pengding_ir_evidence.md`.

Evidence added:

- 2026-01 IR: compute-customer certification is progressing smoothly; 2026 is expected to be the first year of direct compute-customer order imports; Thailand Phase I is in small-batch production and yield-ramp stage for automotive/server capacity.
- 2026-04 results briefing: high-end HDI and HLC products have entered the AI-server market and are gradually reaching mass production; SLP products have entered the 800G/1.6T optical-module high-end market and will realize mass shipments; 3.2T products are in R&D.
- 2026-04 results briefing explicitly included a question about Nvidia high-end board order mass-production timing; the issuer replied that compute customer certification is progressing smoothly but it is not convenient to comment on a single customer.
- 2026 Q1 exchange: optical-module business growth is significant and expected to grow several-fold this year; fixed-asset depreciation will be recognized in phases, and optical-module boards / high-end HDI/HLC for compute have strong demand and profitability to absorb depreciation pressure.

Report update: `sections/ch05_customer_bridge.tex` now adds Pengding IR validation to Exhibit 12g. This strengthens official customer-validation and product-ramp evidence for Pengding while preserving the boundary that no named Nvidia/Google/platform revenue is disclosed.

## 2026-06-16 Pengding Monthly Revenue Tracker Pass

Official Pengding monthly revenue briefings were downloaded into `workspace/research/semiconductor-pcb-20260612/sources/official-pengding-monthly-20260616/` and text-extracted. The evidence summary is stored in `data/pengding_monthly_revenue_evidence.md`.

Evidence added:

- 2026-01 revenue 27.01亿元, -0.07% YoY.
- 2026-02 revenue 23.24亿元, -5.65% YoY.
- 2026-03 revenue 29.61亿元, +1.38% YoY.
- 2026-04 revenue 29.45亿元, +5.09% YoY.
- 2026-05 revenue 31.05亿元, +19.51% YoY.

Report update: `sections/ch06_companies.tex` now includes Exhibit 16b with Pengding's official monthly revenue tracker. This improves high-frequency delivery tracking for the Pengding watchlist thesis and shows post-Q1 acceleration, but remains unaudited revenue-only data and does not disclose platform/customer revenue split, margin or EPS contribution.

## 2026-06-16 Pengding Shareholder Count Bridge Pass

Official Pengding 2025Q3, 2025 annual and 2026Q1 reports were parsed for shareholder count and HKCC nominee-holder rows. Evidence is stored in `data/pengding_shareholder_count_bridge.md` and `.json`.

Evidence added:

- 2025Q3 shareholder count: 75,458; HKCC holding: 8239.70万股 / 3.55%.
- 2025Q4 shareholder count: 88,425; HKCC holding: 6273.41万股 / 2.71%.
- 2026Q1 shareholder count: 93,953; HKCC holding: 5707.02万股 / 2.46%.
- Public read-through: shareholder count broadened while HKCC/Stock Connect proxy declined, consistent with visible fund-holder and HKEX evidence.

Report update: `sections/ch09_secondary_market.tex` now adds Pengding to Exhibit 25b-3 shareholder-count concentration bridge. This improves official holder-concentration evidence for the expanded watchlist, but remains a public shareholder-count / nominee-holder proxy and not beneficial-owner data.

## 2026-06-16 Pengding Operating Sensitivity Pass

Huatai's Pengding forecast table includes enough operating-line detail to upgrade Pengding from forecast-line revenue-shock proxy to public operating-line sensitivity proxy. Evidence is stored in `data/pengding_operating_sensitivity_evidence.md` and `.json`.

Evidence added:

- Huatai 2026E operating inputs: revenue 471.91亿元, gross profit 111.90亿元, gross margin 23.71%, OPEX 45.04亿元, operating profit 63.15亿元, PBT 63.17亿元, tax 5.95亿元, parent NPP 57.22亿元.
- Sensitivity proxy: GM -1pct NPP 52.95亿元; GM -2pct NPP 48.67亿元; revenue -5pct NPP 52.15亿元; revenue -5pct plus GM -1pct NPP 47.88亿元.

Report update: `sections/ch08_valuation.tex` now upgrades Pengding in Exhibit 24 from forecast-line proxy to Huatai operating-line sensitivity proxy. This improves public-source EPS sensitivity quality, but it still is not customer/platform bottom-up EPS because named platform revenue, ASP, shipment, project depreciation and working-capital assumptions remain unavailable.

## 2026-06-16 Pengding Fund Style Proxy Pass

Pengding's Sina fund-holder rows were classified using the same rule-based style proxy as the rest of the report, and top visible funds were mapped through Eastmoney fund type data where available. Evidence is stored in `data/pengding_fund_style_proxy.md` and `.json`.

Evidence added:

- 2026Q1 visible fund market value totals 20.05亿元 across 111 rows.
- Active-like funds account for 16.29亿元 / 81.3% of visible market value; top examples include Nuode Hexin, Hongde Ruize and Zhuque products.
- Bond/fixed-income-like products account for 3.01亿元 / 15.0%, mainly Huitianfu Shuangli and similar products.
- Passive/index-like exposure is small in the public proxy.

Report update: `sections/ch09_secondary_market.tex` now adds Pengding to Exhibit 25c fund holder style proxy. This aligns Pengding with the rest of the expanded watchlist, but it remains a rule-based public proxy rather than a Wind/Choice official active/passive ownership classification.

## 2026-06-16 Pengding P5W / SZSE Interaction Pass

P5W investor Q&A pages and JSON endpoints were parsed for Pengding (`002938`). Raw HTML snapshots are stored in `data/raw_pengding_p5w_*.html`, raw JSON in `data/raw_pengding_p5w_qid.json` and `data/raw_pengding_p5w_keyword.json`, and summary evidence in `data/pengding_p5w_interaction_evidence.md`.

Evidence added:

- 2026-05-19 reply: 1.6T optical-module related products are already in batch supply; 3.2T products are being developed with customers.
- 2026-05-21 reply: the company is using high-end HDI and SLP as core products to lay out AI servers and optical modules, and is expanding Huai'an and Thailand capacity for AI servers and high-speed optical modules.
- 2026-04 replies: for specific customer/product questions such as Nvidia/Rubin or foldable-phone customers, the issuer cites commercial confidentiality and does not disclose specific customer/product information.

Report update: `sections/ch05_customer_bridge.tex` now adds P5W/SZSE interaction evidence to Exhibit 12g. This strengthens the Pengding optical-module and customer-disclosure-boundary evidence layer, but it still does not disclose named platform revenue, order value, ASP, shipment, margin or EPS contribution.

## 2026-06-16 Zhen Ding Parent Official Evidence Pass

Zhen Ding Technology Holding's official 2026Q1 investor presentation was downloaded from `zdtco.com` into `workspace/research/semiconductor-pcb-20260612/sources/official-zhen-ding-20260616/` and text-extracted. Evidence is summarized in `data/zhen_ding_parent_official_evidence.md`.

Evidence added:

- 1Q26 Server/Optical & Others accounted for 10.1% of parent-company revenue, and IC Substrate accounted for 9.6%; combined contribution reached 19.7%.
- In 2025, Server/Optical & Others accounted for 5.3% and IC Substrate 6.4%; combined contribution was 11.7%, showing mix shift toward high-end AI applications.
- 1Q26 Server/Optical revenue more than doubled YoY; IC Substrate revenue increased over 60% YoY.
- From 2Q26, next-generation AI platforms are expected to gradually enter mass production; full-year Server/Optical revenue is expected to more than double; full-year IC Substrate revenue target is +70%+.
- GPU and ASIC customer iHDI/HLC products are gradually entering mass production; optical communication orders are primarily driven by 1.6T high-speed boards, with customers reserving 2027 capacity.

Report update: `sections/ch05_customer_bridge.tex` now adds parent-company read-through to Exhibit 12g. This strengthens product/application mix evidence for the Pengding/Zhen Ding group, but remains parent-level application mix and does not disclose named customer/platform revenue for Pengding A-share alone.

## 2026-06-16 Zhen Ding Monthly Revenue Evidence Pass

Zhen Ding's official investor finance page was archived as `data/raw_zhen_ding_finance_en.html` and parsed for 2026 monthly consolidated revenue. Evidence is stored in `data/zhen_ding_monthly_revenue_evidence.md`.

Evidence added:

- 2026-01 revenue NT$13.56bn, +0.71% YoY.
- 2026-02 revenue NT$11.72bn, -3.97% YoY.
- 2026-03 revenue NT$15.44bn, +7.18% YoY.
- 2026-04 revenue NT$15.20bn, +11.83% YoY.
- 2026-05 revenue NT$16.20bn, +37.40% YoY.
- 2026 YTD through May revenue was NT$72.13bn.

Report update: `sections/ch06_companies.tex` now adds Zhen Ding parent monthly revenue read-through below Pengding's official monthly revenue tracker in Exhibit 16b. This improves high-frequency parent-company delivery tracking but remains parent consolidated revenue, not named customer/platform revenue or Pengding A-share standalone segment revenue.

## 2026-06-16 Pengding Important Institution Pass

Eastmoney `RPT_NATIONAL_STATISTICS` and `RPT_STOCK_DETAILS_CHANGE` were queried for Pengding (`002938`) for 2026Q1. Evidence is stored in `data/pengding_important_institution_evidence.md` and `.json`.

Evidence added:

- 2026Q1 important institution proxy: 2 organizations, 4861.16万股, 25.36亿元 market value, 2.10% share ratio, +238.30万股 QoQ.
- Holder details: National Social Security Fund 103 portfolio held 4409.9992万股 / 23.01亿元 / 1.90% and increased 410.0011万股; National Social Security Fund 416 portfolio held 451.16万股 / 2.35亿元 / 0.19% and decreased 171.70万股.

Report update: `sections/ch09_secondary_market.tex` now adds Pengding to Exhibit 28 important institution holding evidence and Exhibit 29 holder details. This improves public important-institution coverage for the expanded watchlist, but remains an Eastmoney public proxy rather than full institutional ownership, beneficial-owner data or official active/passive classification.

## 2026-06-16 Zhen Ding 2025Q3 Outlook Evidence Pass

Zhen Ding's official 2025Q3 investor presentation was downloaded into `workspace/research/semiconductor-pcb-20260612/sources/official-zhen-ding-20260616/` and text-extracted. The existing `data/zhen_ding_parent_official_evidence.md` was updated with the new outlook evidence.

Evidence added:

- Zhen Ding states AI server revenue is expected to gradually scale up in 2026 and double in 2027.
- Large-body-size ABF substrate revenue is expected to increase materially quarter by quarter throughout 2026.
- iHDI and HLC capacity at Huai'an is expected to double by end-2026.
- Thailand fab 1 focuses on high-end iHDI, HLC and optical-module products.

Report update: `sections/ch05_customer_bridge.tex` now adds this 2025Q3 outlook to the Pengding/Zhen Ding parent read-through in Exhibit 12g. This strengthens product/capacity trajectory evidence, but remains parent-company guidance and does not disclose named customer/platform revenue for Pengding A-share alone.

## 2026-06-16 Shennan P5W / SZSE Disclosure Boundary Upgrade

P5W static question pages and JSON endpoints were probed for Shennan Circuit (`002916`) to upgrade customer-disclosure-boundary evidence from search snippets to original interface evidence. Raw files are archived as `data/raw_shennan_p5w_ai_boundary.html`, `data/raw_shennan_p5w_ai_qid.json`, `data/raw_shennan_p5w_rubin_boundary.html`, `data/raw_shennan_p5w_rubin_qid.json`, `data/raw_shennan_p5w_rubin_keyword.json`, `data/raw_shennan_p5w_ai_keyword.json` and `data/raw_cninfo_shennan_companydetail.html`.

Evidence added:

- P5W/SZSE QID `0001FB6C969FE01C4328A5F8BFA921BD83C8` asks whether Shennan's high-end PCB layout covers HLC, ABF/RCC, Any Layer HDI and high-speed materials, and whether the company has entered NVIDIA / AMD / Intel, server OEM or computing-infrastructure customer supply chains.
- The issuer reply states AI demand lifts large-size, high-layer, high-frequency/high-speed, high-end HDI and thermal PCB needs; the company's PCB demand is affected in high-speed communication networks, data-center switches, AI accelerator cards and storage.
- The same reply states: "基于商业保密原则，凡涉及与具体企业合作的问题，公司均不便于回复".
- The Rubin URL found through public search was archived, but the QID endpoint returned shareholder-count content rather than Rubin body text; that failed probe is recorded and is not used as primary Rubin evidence.
- Hudian P5W question-list HTML was archived as `data/raw_hudian_p5w_questionlist.html`, but keyword probes for Rubin / Google / commercial policy returned empty rows; Hudian remains lower-confidence boundary evidence unless a primary row is later recovered.

Report update: `data/customer_disclosure_boundary_evidence.md`, `data/source_registry.md`, `data_room_index.md` and `sections/ch05_customer_bridge.tex` now reference the Shennan primary-interface evidence. This improves source governance for the remaining named-customer split gap, but it does not disclose customer revenue, order value, ASP, shipments, margin or EPS contribution.

## 2026-06-16 Hudian CNInfo / SZSE Disclosure Boundary Upgrade

CNInfo / SZSE Interactive Easy frontend chunks were inspected to identify the working company-question endpoint. The verified endpoint is `newircs/company/question` with query parameters `stockcode=002463`, `orgId=9900013929`, `pageNum`, `pageSize`, and `keyWord`. Raw JSON files are archived as `data/raw_hudian_cninfo_company_question_rubin_verified.json`, `data/raw_hudian_cninfo_company_question_google_verified.json`, `data/raw_hudian_cninfo_company_question_commercial_policy_verified.json`, and single-question detail `data/raw_hudian_cninfo_rubin_question_detail_2279086205782548480.json`.

Evidence added:

- The Rubin keyword endpoint returns two `stockCode=002463` rows, including one question asking whether the company has entered NVIDIA Rubin rack supply chain.
- The Google keyword endpoint returns one `stockCode=002463` row asking whether the company is shifting more capacity toward Google and reducing NVIDIA supply.
- The commercial-policy keyword endpoint returns seven `stockCode=002463` rows, including questions on Rubin, Google/NVIDIA capacity allocation, NVIDIA/AMD/overseas cloud supply ratio, LPU/LPX cooperation, Intel / Google TPU, DeepSeek and Huawei Ascend.
- Across these rows, Hudian repeatedly replies that due to commercial policy restrictions it cannot discuss specific vendors/customer cooperation, while stating it cooperates with many domestic and overseas customers across multiple technical platforms and is capturing AI / high-speed networking structural PCB demand.

Report update: `data/customer_disclosure_boundary_evidence.md`, `data/source_registry.md`, `data_room_index.md`, `completion_audit_manifest.md` and `sections/ch05_customer_bridge.tex` now reference the Hudian primary-interface evidence. This upgrades the disclosure-boundary proof, but it does not disclose named customer revenue, customer share, order value, ASP, shipments, margin or EPS contribution.

## 2026-06-16 Shenghong CNInfo / SZSE Disclosure Boundary Upgrade

CNInfo / SZSE Interactive Easy keyboard and company-question endpoints were queried for Shenghong Technology (`300476`, `orgId=9900024582`). Raw JSON files are archived as `data/raw_cninfo_keyboard_shenghong.json`, `data/raw_cninfo_keyboard_300476.json`, `data/raw_shenghong_cninfo_company_question_asic.json`, `data/raw_shenghong_cninfo_company_question_commercial_policy.json`, and single-question detail `data/raw_shenghong_cninfo_asic_question_detail_2241043577109426176.json`.

Evidence added:

- The ASIC keyword endpoint returns `stockCode=300476` rows including a question on ASIC customer order timing. The single-question detail endpoint confirms the issuer reply: ASIC-related customer business is progressing smoothly, but due to commercial policy restrictions the company cannot discuss specific customer names or business details without permission.
- The commercial-policy keyword endpoint returns `stockCode=300476` rows covering NVIDIA Spark, midplane, mSAP / orthogonal backplane, CB300, domestic chip customers, Tesla AI5, GB200/GB300 and CoWoP questions.
- The same endpoint includes issuer evidence that mSAP capacity is used for 1.6T optical-module production, in-hand orders are full, utilization is good, and high-end PCB capability includes 100+ layer multilayer PCB, 10-order 30-layer HDI and 16-layer Any-layer HDI.
- Across the customer/project questions, Shenghong repeatedly says that it cannot discuss specific customer names or business details due to commercial policy restrictions.

Report update: `data/customer_disclosure_boundary_evidence.md`, `data/source_registry.md`, `data_room_index.md`, `completion_audit_manifest.md` and `sections/ch05_customer_bridge.tex` now reference the Shenghong primary-interface evidence. This upgrades source governance for customer-disclosure boundaries, but it still does not disclose named customer revenue, customer share, order value, ASP, shipments, margin or EPS contribution.

## 2026-06-16 Shengyi SSE Interaction Probe

SSE E-interactive company page and feed endpoints were probed for Shengyi Technology (`600183`) to test whether public interaction records could close the M8/M9/M10 and named customer-certification gap. Raw HTML files are archived as `data/raw_sse_company_600183.html`, `data/raw_shengyi_sse_userfeeds_type_10_page1.html`, `data/raw_shengyi_sse_userfeeds_company_q_page1.html`, `data/raw_shengyi_sse_userfeeds_company_q_page2.html`, `data/raw_shengyi_sse_userfeeds_company_q_page3.html`, `data/raw_sse_search_shengyi_m9.html`, `data/raw_sse_search_600183_m9.html` and `data/raw_sse_search_shengyi_gpu.html`. Summary evidence is stored in `data/shengyi_sse_interaction_probe.md`.

Evidence added:

- The official SSE company page confirms Shengyi Technology `600183` and interaction `uid=183`.
- The recent type-10 question feed contains an investor question about M8/M9 stocking/ramp and drilling-process bottlenecks, but the captured item is question-only.
- The type-11 reply feed for pages 1-3 returned "近1个月暂无回复"; no issuer reply was recovered for M8/M9/M10 revenue share, named customer certification, ASP, shipment, margin or platform EPS.
- The strongest usable public source remains the SSE-hosted IR PDF already archived as `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/600183-sse-202505-ir.pdf`, which confirms lower-loss CCL demand, GPU/AI project cooperation with domestic and overseas terminals, batch supply, diversified customer structure and Thailand CCL/prepreg investment.

Report update: `data/source_registry.md`, `data_room_index.md`, `source_exhaustion_log.md`, `data/shengyi_sse_interaction_probe.md` and `sections/ch05_customer_bridge.tex` now record this probe. It improves source-exhaustion evidence and prevents treating an unanswered interaction question as proof, but it does not close M8/M9/M10 revenue share, named certification, ASP, shipment, margin or customer/platform EPS gaps.

## 2026-06-16 Global Broker Original PDF Re-Probe

Targeted public probes were re-run for the remaining missing original global-broker PDFs: JPMorgan / Shenghong 2476.HK (`hibor id=5123096`), Goldman / Hudian (`hibor id=db73893e91c90fd2ba6982293ef4feb2`), Goldman / Shengyi visible Sina repost, and additional Pengding fallback sources.

Evidence added:

- JPMorgan / Shenghong Hibor probe archived as `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/jpm-shenghong-probe/hibor-5123096.html`. Decoding shows title `慧博智能策略终端_下载`; no report body, PDF link, JPMorgan, Shenghong or report-summary text was recovered.
- Goldman / Hudian Hibor probe archived as `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/goldman-hudian-probe/hibor-db73893e91c90fd2ba6982293ef4feb2.html`. It also returned the Hibor intelligent terminal download page, not a usable report.
- Goldman / Shengyi visible Sina repost archived as `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/goldman-shengyi-probe/sina-goldman-shengyi-20260522.html`; it is visible repost text, not an original Goldman PDF.
- Guohai / Pengding 50-page original PDF was downloaded and text-extracted as `workspace/research/semiconductor-pcb-20260612/sources/broker-global-probe-20260616/pengding-extra-probe/guohai-pengding-ai-edge.pdf` and `.txt`. It adds a full original fallback PDF for Pengding, covering end-side AI, automotive/server expansion, Thailand server/automotive capacity, 2024E-2026E revenue/NPP/EPS forecasts and buy rating.

Report/data update: `data/global_broker_original_pdf_probe_20260616.md`, `data/source_registry.md`, `data_room_index.md`, `completion_audit_manifest.md` and `source_exhaustion_log.md` now record this pass. This improves fallback original-PDF depth for Pengding, but it still does not close the missing UBS/JPM/Goldman original-PDF requirement and does not disclose named platform revenue or customer/platform EPS assumptions.

## 2026-06-16 Important Institution Category Bridge

The archived Eastmoney `RPT_STOCK_DETAILS_CHANGE` raw JSON in `data/important_institution_detail_evidence.json` was re-used to aggregate visible important-institution rows by ticker, report date and institution type. The new summary is stored in `data/important_institution_category_history_bridge.md`.

Evidence added:

- 2026Q1 visible category snapshot: Hudian has two social-security rows totaling 2143.58万股 / 16.28亿元 / 1.1139%; Shennan has one pension row and two social-security rows totaling 774.61万股 / 17.00亿元 / 1.1372%; Shengyi has one social-security row totaling 791.82万股 / 4.29亿元 / 0.3260%.
- Historical category coverage in the public endpoint includes Hudian social-security rows from 2011Q4 to 2026Q1, Hudian state-team rows from 2015Q3 to 2021Q2, Shenghong social-security rows from 2017Q3 to 2024Q4, Shengyi social-security rows from 2004Q2 to 2026Q1, and Huazheng social-security rows from 2017Q2 to 2025Q3.
- The report now separates this from CNInfo fund-heavy holdings, Sina fund-holder proxies, HKEX Stock Connect quarterly holdings and Eastmoney participant/custodian bridges.

Report update: `sections/ch09_secondary_market.tex` now includes Exhibit 28b and Exhibit 28c for important-institution category and historical coverage. This improves public holding-data depth, but remains visible public important-institution disclosure only; it does not provide full institutional ownership, beneficial-owner Stock Connect data, official active/passive fund classification, terminal-grade order flow or intraday flow.

## 2026-06-16 Liquidity / Turnover Proxy

Yahoo daily close and volume records already archived in `data/historical_market_data.json`, `data/watchlist_historical_market_data.json` and `data/pengding_market_positioning_evidence.json` were used to compute a public liquidity proxy. Output files are `data/liquidity_turnover_proxy.md` and `.json`.

Evidence added:

- Method: daily turnover proxy = close price multiplied by daily volume. For A-share tickers, this approximates CNY traded value.
- Coverage: 279 daily records for each core ticker, six original watchlist tickers and Pengding.
- Highest average daily turnover in the universe: Shenghong 107.93亿元, Hudian 51.06亿元, Shengyi 30.78亿元, Xingsen 24.86亿元, Shennan 23.72亿元 and Pengding 20.58亿元.
- Lowest among highlighted core names: Huazheng 6.82亿元 average daily turnover, indicating weaker capacity and higher liquidity/slippage risk for large positions.

Report update: `sections/ch09_secondary_market.tex` now changes Liquidity / turnover from incomplete to public proxy and adds Exhibit 29b. This improves public secondary-market depth, but it does not replace exchange official amount, turnover ratio, order-book depth, intraday slippage, block trade, margin financing, northbound daily change or terminal-grade order flow.

## 2026-06-16 Eastmoney Daily Amount / Turnover Proxy

Eastmoney `push2his` daily K-line endpoint was tested to improve the liquidity proxy from Yahoo close x volume toward a public market-source amount / turnover field. Raw JSON files are archived under `data/raw_eastmoney_kline/`. Output summary files are `data/eastmoney_liquidity_turnover_evidence.md` and `.json`.

Evidence added:

- Successful tickers: `300476`, `002463`, `600183`, `688630`, `301377`, `603186`, `688519`, `300400`.
- Failed / unstable tickers in this environment: `002916`, `002436`, `301200`, `002938`; these remain covered by the Yahoo liquidity proxy.
- Eastmoney amount / turnover results are close to the Yahoo proxy but use direct amount and turnover fields: Shenghong average daily amount 107.59亿元 / average turnover 5.04%; Hudian 50.97亿元 / 3.70%; Shengyi 30.71亿元 / 1.93%; Huazheng 6.79亿元 / 7.55%.

Report update: `sections/ch09_secondary_market.tex` now prioritizes Eastmoney daily amount / turnover where available and keeps Yahoo close x volume proxy for failed tickers. This improves public liquidity evidence, but still does not provide order-book depth, intraday slippage, block trades, margin financing, northbound daily beneficial-owner changes or terminal-grade order flow.

## 2026-06-16 Eastmoney Margin Financing / Leverage Proxy

Eastmoney DataCenter `RPTA_WEB_RZRQ_GGMX` was identified as the working public financing/securities-lending report. Raw JSON files are archived under `data/raw_eastmoney_margin/`; summary outputs are `data/eastmoney_margin_financing_evidence.md` and `.json`.

Evidence added:

- Successful tickers: 10/12 in the expanded universe. Huazheng (`603186`) and Jintuo (`300400`) returned empty rows.
- Key fields: `RZYE` financing balance, `RQYE` securities lending balance, `RZRQYE` total margin balance, `RZJME` net financing purchase, `RZYEZB` financing balance / float-market-value ratio.
- Latest 2026-06-15 margin balance leaders: Shenghong 232.10亿元, Hudian 66.68亿元, Shengyi 42.72亿元, Xingsen 32.90亿元, Pengding 24.82亿元, Shennan 17.73亿元.
- Financing / float-market-value ratio flags leverage crowding: Shenghong 7.77%, Xingsen 5.35%, Hudian 2.58%, while Shennan is only 0.66%.
- 30-row net financing purchase is positive for Shenghong +27.18亿元, Hudian +29.62亿元, Shengyi +20.84亿元, Xingsen +10.78亿元 and Pengding +10.88亿元; Shennan is negative at -2.64亿元.

Report update: `sections/ch09_secondary_market.tex` now adds Exhibit 29c. This materially improves public leverage/crowding analysis, but remains a financing/securities-lending proxy and not institutional ownership, order-book depth, beneficial-owner northbound data, active/passive classification or terminal-grade order flow.

## 2026-06-16 Eastmoney Block Trade Proxy

Eastmoney DataCenter `RPT_DATA_BLOCKTRADE` was identified as the working public block-trade report. Raw JSON files are archived under `data/raw_eastmoney_blocktrade/`; summary outputs are `data/eastmoney_block_trade_evidence.md` and `.json`.

Evidence added:

- Successful tickers: 10/12 in the expanded universe. Huazheng (`603186`) and Jintuo (`300400`) returned empty rows.
- Period queried: 2025-04-21 to 2026-06-15.
- Largest public block-trade traces: Shenghong 136 deals / 37.47亿元 total amount / 120 discount deals; Pengding 62 deals / 35.19亿元 / 62 discount deals.
- Other notable activity: Nanya 14 deals / 3.19亿元; Han's CNC 49 deals / 2.96亿元; Circuit Fabology 41 deals / 2.02亿元; Hudian 6 deals / 1.13亿元.
- Shennan and Dtech had only one visible block-trade row each; Shengyi had 3 rows / 0.47亿元.

Report update: `sections/ch09_secondary_market.tex` now adds Exhibit 29d. This improves public large-transaction trace evidence, but block trades are still not full order-flow tape and do not identify ultimate beneficial owners beyond reported buyer/seller broker seats.

## 2026-06-16 Eastmoney Share Pledge Proxy

Eastmoney share-pledge pages and scripts were parsed to identify `RPT_CSDC_LIST` for pledge-ratio history and `RPTA_APP_ACCUMDETAILS` for pledge detail rows. Raw JSON files are archived under `data/raw_eastmoney_pledge/`; summary outputs are `data/eastmoney_share_pledge_evidence.md` and `.json`.

Evidence added:

- Successful ratio/detail coverage is partial. Ratio rows exist for Hudian, Shenghong, Shennan, Shengyi, Huazheng, Nanya, Han's CNC, Jintuo and Pengding; Xingsen ratio download was corrupted but detail rows exist; Circuit Fabology and Dtech returned empty rows.
- Unit audit: Eastmoney ratio table reports pledged shares in 10k shares and pledge market cap in 10k CNY. Detail rows use `PF_NUM` in shares and `MARKET_CAP` in CNY.
- Latest visible pledge ratios are generally low in the covered universe: Nanya 3.28% (old 2020 record), Pengding 1.26% (old 2021 record), Han's CNC 0.75%, Shenghong 0.16%, Hudian ~0.00%, Shengyi ~0.00%.
- Xingsen has no usable latest ratio row due to corrupted ratio JSON, but pledge-detail rows show active detail market cap around 15.20亿元 and need follow-up validation.

Report update: `sections/ch09_secondary_market.tex` now adds Exhibit 29e. This improves governance / controlling-shareholder pledge-risk coverage, but it is not institutional ownership, beneficial-owner positioning or order-flow data. Eastmoney warning-line and liquidation-line fields are estimates and may differ from actual pledge contracts.

## 2026-06-16 Huazheng Official Project Economics Boundary

Huazheng's official 2026 high-grade CCL feasibility report was re-read for project economic assumptions. The evidence summary is updated in `data/official_huazheng_refinancing_evidence.md`.

Evidence added:

- The official project bridge confirms 10.04亿元 total investment, 10.00亿元 proposed fundraising use and annual capacity of 1200万张 high-grade CCL.
- Product scope includes high-speed CCL, high-frequency CCL, high-thermal-conductivity metal substrate and HDI CCL for AI servers, switches, optical modules, 5G base stations and automotive electronic-control systems.
- The feasibility report only states that the project is expected to have "良好的经济效益" after smooth implementation.
- It does not disclose project revenue, gross profit, net profit, IRR, payback period, product ASP, unit cost, utilization ramp, depreciation schedule or customer orders.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 23f. This improves official project-boundary discipline for Huazheng and prevents using the official feasibility report as a project-level EPS model. Huazheng still relies on a broker forecast-line model, not bottom-up customer/platform EPS.

## 2026-06-16 Huazheng Historical CBF Deep Report Refresh

A public DZH static PDF for Zheshang's 2023-12-20 Huazheng deep report, `CBF膜国产化主力军`, was downloaded and text-extracted as `workspace/research/semiconductor-pcb-20260612/sources/broker-original-refresh-20260616/10-zheshang-huazheng-cbf-deep-20231220.pdf` and `.md`.

Evidence added:

- Valid original PDF: 17 pages, A4, 1,168,062 bytes.
- Adds CBF advanced-packaging material rationale, including FC-BGA, redistribution dielectric layer, molding, chip bonding and underfill scenarios.
- States Japanese suppliers held about 96% of the CBF build-up film market at the time of publication.
- States Huazheng had business relationships with more than 50% of PCB top-100 companies, including Kinwong, Kexiang, Aoshikang and Shenghong.
- Adds historical 2023E-2025E product-line revenue and gross-margin assumptions: CCL revenue 26.16/31.02/39.38亿元, CCL gross margin 10%/13%/15%; total revenue 35.02/41.04/50.84亿元; parent NPP -0.02/1.48/3.23亿元; EPS -0.01/1.04/2.27元.

Report/data update: `data/huazheng_cbf_deep_refresh_20260616.md`, `data/original_pdf_refresh_20260616.md`, `data/source_registry.md`, `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md`, `sections/ch02_evidence.tex`, `sections/ch05_customer_bridge.tex` and `sections/ch12_appendix.tex` now record this source. It improves Huazheng original-PDF depth and CBF technical evidence, but it is historical and still does not disclose named customer revenue, CBF/BT order value, current platform split or bottom-up customer/platform EPS.

## 2026-06-16 Huazheng Haitong International Report Refresh

An Eastmoney static PDF for Haitong International's 2023-08-16 Huazheng report, `算力侧材料国产替代进行时`, was downloaded and text-extracted as `workspace/research/semiconductor-pcb-20260612/sources/broker-original-refresh-20260616/11-haitong-intl-huazheng-ccl-cbf-20230816.pdf` and `.md`.

Evidence added:

- Valid original PDF: 13 pages, A4, 1,599,582 bytes.
- Rating and valuation: maintained OUTPERFORM / 优于大市, historical target price RMB43, based on 20x 2024E PE.
- Forecast line: 2023E-2025E revenue RMB 3.683/5.156/6.333bn; parent NPP RMB -1/306/498mn; EPS RMB -0.01/2.16/3.51; gross margin 12.1%/18.4%/20.9%.
- Quarterly model: 2024E quarterly revenue RMB 1.133/1.251/1.345/1.427bn and NPP RMB 51/76/87/93mn.
- Technology bridge: high-speed CCL demand tied to AI server GPU boards, OAM/UBB PCB area, 400G switches / optical modules, and M6-to-M7/M8 material migration.
- Product progress: Ultra low-loss CCL entered small-batch stage for 56Gbps data-communication switches; new series were being developed for 400G optical modules and high-end AI servers; CBF was being validated in ECP and FC-BGA scenarios with important terminal and downstream customers.

Source-boundary note: the same pass queried Sina Finance's margin-financing page for `sh603186` and `edate=2026-06-16`. The page returned the financing/securities-lending table shell but no detail rows for Huazheng, so it was not used as valid financing, holding or flow evidence.

Report/data update: `data/huazheng_haitong_intl_refresh_20260616.md`, `data/original_pdf_refresh_20260616.md`, `data/source_registry.md`, `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md`, `sections/ch02_evidence.tex`, `sections/ch05_customer_bridge.tex` and `sections/ch12_appendix.tex` now record this source. It improves Huazheng original-PDF depth and model cross-checks, but it is historical broker-stated evidence and still does not disclose named customer revenue, order value, current platform split or bottom-up customer/platform EPS.

## 2026-06-16 SSE Official Margin Financing Cross-Check

The Shanghai Stock Exchange official margin-financing detail interface was identified from the SSE page script:

- Page: `https://www.sse.com.cn/market/othersdata/margin/detail/`
- Endpoint: `https://query.sse.com.cn/commonSoaQuery.do`
- SQL ID: `RZRQ_MX_INFO`
- Parameters: `preStockCode`, `beginDate`, `endDate`

Raw official JSON files are archived under `data/raw_sse_margin/`, and the summary evidence is stored in `data/sse_margin_financing_official_evidence.md`.

Evidence added:

- `600183` 生益科技: 300 official rows from 2025-03-20 to 2026-06-15; latest financing balance 42.21亿元; window net financing buy +35.39亿元.
- `688519` 南亚新材: 300 official rows from 2025-03-20 to 2026-06-15; latest financing balance 7.11亿元; window net financing buy +6.14亿元.
- `688630` 芯碁微装: 300 official rows from 2025-03-20 to 2026-06-15; latest financing balance 9.72亿元; window net financing buy +7.02亿元.
- `603186` 华正新材: official interface returned zero detail rows for the same query window.

Report/data update: `sections/ch09_secondary_market.tex`, `data_room_index.md`, `completion_audit_manifest.md` and `source_exhaustion_log.md` now include the SSE official cross-check. This improves the financing/leverage proxy quality for Shanghai-listed names and confirms Huazheng's empty margin-financing detail on the official SSE interface, but it still does not provide institutional ownership, beneficial-owner positioning, active/passive fund labels or terminal-grade realtime order flow.

## 2026-06-16 SZSE Official Margin Financing Probe

The Shenzhen Stock Exchange official margin-financing interfaces were probed to test whether Shenzhen-listed gaps, especially `300400` Jintuo Technology, could be upgraded beyond the Eastmoney public proxy.

Interface discovery:

- AkShare exposes `stock_margin_detail_szse`, `stock_margin_szse` and `stock_margin_underlying_info_szse`.
- Source file inspected: `.venv/lib/python3.14/site-packages/akshare/stock_feature/stock_margin_szse.py`.
- Official endpoint: `https://www.szse.cn/api/report/ShowReport`.
- Detail parameters: `SHOWTYPE=xlsx`, `CATALOGID=1837_xxpl`, `TABKEY=tab2`, `txtDate=<YYYY-MM-DD>`.
- Underlying-info parameters: `SHOWTYPE=xlsx`, `CATALOGID=1834_xxpl`, `TABKEY=tab1`, `txtDate=<YYYY-MM-DD>`.
- Summary JSON path was also identified as `https://www.szse.cn/api/report/ShowReport/data` with `CATALOGID=1837_xxpl`, `TABKEY=tab1`.

Result:

- Direct SZSE pages returned empty responses or connection resets in the local environment.
- `ak.stock_margin_detail_szse(date="20260616")` and `ak.stock_margin_underlying_info_szse(date="20260616")` failed with `ConnectionResetError: [Errno 54] Connection reset by peer`.
- Direct xlsx downloads for the official detail and underlying-info endpoints failed with `curl: (35) Recv failure: Connection reset by peer`.
- One exploratory JSON summary call returned market-level financing-summary metadata, but repeat archival call failed with `000 0`, so no durable official SZSE JSON file was produced.

Report/data update: `data/szse_margin_financing_probe_20260616.md`, `data_room_index.md`, `completion_audit_manifest.md` and `source_exhaustion_log.md` now record this probe. It identifies the official SZSE path for follow-up but does not improve the numeric report tables. The Shenzhen-listed financing gaps, including `300400`, remain open until the official endpoint can be accessed from a stable network or a paid terminal dataset is available.

## 2026-06-16 Eastmoney Dragon-Tiger List Proxy

Eastmoney DataCenter `RPT_DAILYBILLBOARD_DETAILS` was identified as the working Dragon-Tiger List / abnormal-trading report. Raw JSON files are archived under `data/raw_eastmoney_lhb/`; summary outputs are `data/eastmoney_lhb_evidence.md` and `.json`.

Evidence added:

- Coverage: 12/12 expanded-universe tickers for the period 2025-04-21 to 2026-06-15.
- Highest on-list frequency: Hudian 10 days, Pengding 10 days, Shennan 9 days, Huazheng 6 days, Xingsen / Circuit Fabology / Dtech 5 days each.
- Largest total Dragon-Tiger net buy: Hudian +82.54亿元, Shenghong +33.32亿元, Shennan +17.99亿元, Xingsen +8.90亿元, Circuit Fabology +7.42亿元.
- Notable negative net buy: Shengyi -12.80亿元 on one on-list event and Dtech -5.75亿元 across five events.

Report update: `sections/ch09_secondary_market.tex` now adds Exhibit 29f. This improves abnormal-trading and public seat-flow context, but Dragon-Tiger List data captures only disclosed abnormal-trading days, not all order flow or ultimate beneficial owners.

## 2026-06-16 Eastmoney Lock-up Expiry Proxy

Eastmoney DataCenter `RPT_LIFT_STAGE` was identified as the working lock-up expiry / restricted-share release report. Raw JSON files are archived under `data/raw_eastmoney_lockup/`; summary outputs are `data/eastmoney_lockup_expiry_evidence.md` and `.json`.

Evidence added:

- Coverage: 12/12 expanded-universe tickers.
- Future window: 2026-06-16 to 2027-06-16.
- Largest future supply pressure: Dtech (`301377`) has one 2027-05-24 unlock batch with 31,255.20万 shares, estimated unlock market cap 1730.16亿元 and future total ratio 75.97%.
- Shengyi has one 2026-07-06 equity-incentive unlock batch of 1744.81万 shares / 29.04亿元 / 0.72%.
- Pengding has two future equity-incentive unlock batches totaling 451.20万 shares / 4.72亿元 / 0.19%.
- Core names Hudian, Shenghong and Shennan show no future unlock batch in the queried one-year window.

Report update: `sections/ch09_secondary_market.tex` now adds Exhibit 29g. This improves future tradable-supply risk coverage, but lock-up expiry is not actual selling intent and does not identify beneficial-owner execution or order-flow behavior.

## 2026-06-16 Eastmoney Shareholder Increase / Decrease Proxy

Eastmoney DataCenter `RPT_SHARE_HOLDER_INCREASE` was identified as the working public shareholder increase/decrease disclosure report. Raw JSON files are archived under `data/raw_eastmoney_holder_change/`; summary outputs are `data/eastmoney_holder_change_evidence.md` and `.json`.

Evidence added:

- Period queried: 2025-04-21 to 2026-06-15.
- Public reduction traces were found for Pengding, Shengyi, Hudian, Xingsen and Nanya. No increase/decrease records were returned for Shennan, Jintuo, Shenghong, Han's CNC, Dtech, Huazheng and Circuit Fabology in this window.
- Largest net change proxy: Pengding -3999.99万股 / -40.63亿元, led by Meigang Industrial selling 2400.00万 shares on 2026-05-22.
- Shengyi: -2429.12万股 / -16.12亿元, led by Guangdong Guangxin Holdings selling 1291.01万 shares on 2025-12-10.
- Hudian: -1200.00万股 / -5.28亿元 by WUS Group Holdings on 2025-07-16.
- Xingsen: -1487.90万股 / -2.71亿元 by the 2021 employee stock ownership plan on 2025-08-02.

Report update: `sections/ch09_secondary_market.tex` now adds Exhibit 29h. This improves actual public shareholder-change evidence, but remains disclosure-based and is not a full beneficial-owner database or complete order-flow record.

## 2026-06-16 Eastmoney Forecast Consensus Cross-Check

Eastmoney DataCenter `RPT_WEB_RESPREDICT` was identified as a working public forecast / rating aggregate endpoint. Raw JSON files are archived under `data/raw_eastmoney_forecast/`; summary outputs are `data/eastmoney_forecast_consensus_evidence.md` and `.json`.

Evidence added:

- Coverage: 11/12 expanded-universe tickers. Jintuo (`300400`) returned empty rows.
- Highest coverage: Hudian 19 institutions, Shennan 18, Circuit Fabology 16, Pengding 15, Shenghong 13, Han's CNC and Shengyi 9 each.
- Public aggregate rating mix is bullish across covered names: Hudian 14 Buy / 5 Add / 0 Neutral; Shennan 15 / 3 / 0; Pengding 11 / 4 / 0; Shenghong 10 / 3 / 0.
- Eastmoney public EPS cross-check: Hudian 2026E/2027E EPS 2.97/4.52; Shennan 7.95/10.94; Pengding 2.35/3.29; Shenghong 9.89/16.63; Shengyi 2.33/3.30.

Report update: `sections/ch08_valuation.tex` now includes Exhibit 20c. This improves public forecast cross-check coverage, but it is not original broker text, not Wind/Choice full consensus, not an AStock target price, and it does not disclose customer/platform bottom-up assumptions.

## 2026-06-17 Narrative-First Institutional Report Retrofit

User feedback identified that the report still read like a PPT/chartbook: too many standalone tables and not enough prose-led analysis. The report was reworked so each main-body chapter frames the investment question in text, embeds tables as evidence, and adds post-exhibit synthesis.

Remediation completed:

- Chapter 1 now opens with a three-layer house view: certainty, elasticity and diffusion. The segment scorecard and ticker map are embedded between explanatory paragraphs.
- Chapter 2 now explains why evidence hierarchy matters before the evidence pyramid and claim-control table.
- Chapter 4 now explains value-pool migration, platform-chain logic, company relationship meaning and supplier economics before/after the exhibits.
- Chapter 5 now treats customer-chain evidence as the central analytical axis, adds prose around platform-to-earnings, company bridge, quantified bridge and source limitations.
- Chapter 6 now interprets company cards, financial checkpoints, cash conversion, capex and delivery bridges in prose rather than leaving tables to carry the argument.
- Chapter 7 now explains public sell-side sentiment as an input to AStock judgment, not a substitute for it, and adds bull/bear interpretation.
- Chapter 8 now explains valuation logic before the recommendation/Q2E/target-valuation tables and adds synthesis after each major exhibit cluster.
- Chapter 9 now explains why secondary-market data is used to assess priced-in expectations and adds narrative around positioning and crowding proxies.
- Chapter 10 now converts recommendations into a trigger-based investment workflow with prose before/after catalyst and evidence tables.
- Chapter 11 now defines what would make the thesis wrong before the risk heatmap, trigger matrix and monitoring checklist.
- Chapter 12 remains dense by design as appendix/source audit; main-body source workflow paths are not exposed in the reader-facing PDF.

Process / prompt updates completed:

- `.agents/skills/equity-research/SKILL.md` and `.codex/skills/equity-research/SKILL.md` now include a narrative quality gate requiring prose-led chapters, embedded exhibits and post-exhibit synthesis.
- `.agents/skills/research-report-review/SKILL.md` and `.codex/skills/research-report-review/SKILL.md` now review narrative flow and table-stack / PPT-like failures as publication issues.
- `.agents/team/latex-writer.md` and `.codex/agents/latex-writer.toml` now require research-report prose, no back-to-back tables without analysis, and post-exhibit so-what paragraphs.
- `.agents/team/research-report-reviewer.md` and `.codex/agents/research-report-reviewer.toml` now flag table-led main-body chapters and table-only treatment of core valuation/recommendation/risk/customer-chain logic.

Verification evidence:

- Chapter narrative gate: all `sections/ch*.tex` pass the local narrative-block threshold; appendices are allowed to be denser.
- Skill mirror checks: `.agents` and `.codex` equity-research / research-report-review skills are byte-identical; latex-writer and research-report-reviewer role content mirrors have zero diff after extracting TOML bodies.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports `main.pdf` has 65 pages, A4, title `半导体PCB产业链投资研究`, author `AStock研究代理`.
- PDF text extraction confirms narrative anchors across chapters: `我们对半导体 PCB 链条的判断分三层`, `本报告把证据治理放在正文前部`, `产业链分析的核心不是把所有相关公司都列出来`, `客户链是本报告最重要的分析轴`, `财务检查点是把产业逻辑落到报表`, `公开研究情绪的价值在于识别市场共识和盲点`, `估值结论必须从“盈利能否兑现”出发`, `二级市场章节的作用不是证明基本面`, `投资指引的重点不是给一个静态买入清单`, and `风险章节的作用是定义“什么会让本报告错”`.
- PDF text extraction confirms core exhibits: Q2E table, target valuation table, HDI stack diagram, AI server board value-pool diagram, PCB process flow, catalyst timeline and probability-impact risk heatmap.
- PDF text extraction finds no reader-visible `workspace/`, `/Users`, `sections/`, `analysis/`, `data/`, `sources/`, `editable_eps_model`, `Files Produced`, `Workflow files`, `main.tex` or stale `AStock Research Agent` strings.

## 2026-06-17 Current Public-Source Recheck and Remaining Data Boundary

User requested that all unfinished work and uncollected data be filled. A fresh current-state recheck was run instead of relying on the earlier 2026-06-15/16 source-exhaustion notes.

Evidence added:

- `data/current_public_source_recheck_20260617.md` records the current `.venv` SDK/env scan. AkShare 1.18.41 and Baostock 00.8.90 are available; Tushare, WindPy, iFinD, Choice, JQData, RQData, Datayes, xbbg, blpapi, Eikon and paid BOL/customs provider credentials remain unavailable.
- Targeted public searches for Hudian, Shenghong and Shengyi named customer / platform revenue again returned secondary, social or repost-style sources such as Eastmoney wealth-account posts, stock-board posts, Xueqiu, Toutiao, Securities Star and Weibo. These are not promoted into confirmed evidence.
- Eastmoney `RPT_MUTUAL_TOP10DEAL` was identified from the Stock Connect page JavaScript and tested. It provides partial top-10 deal-rank context for some tickers, including 002463 and 600183 on 2026-06-17, but observed buy/sell/net-buy fields were null and many watchlist tickers returned empty or stale rows.
- Eastmoney `RPT_MUTUAL_BOARD_HOLDRANK_WEB` direct sort test returned `HOLD_DATE排序列不存在`; this did not improve beyond the already archived HKEX quarterly shareholding and Eastmoney participant/custodian bridge.

Files updated:

- `data/paid_data_access_audit.md`
- `data/final_public_source_sweep.md`
- `source_exhaustion_log.md`
- `data_room_index.md`
- `missing_data_request_pack.md`
- `completion_audit_manifest.md`
- `unresolved_requirements.json`
- `sections/ch09_secondary_market.tex`
- `sections/ch12_appendix.tex`
- `sections/ch02_evidence.tex`
- `sections/ch11_risks.tex`
- `data/report_quality_eval.json`
- `data/report_quality_eval.md`

Report update:

- Chapter 9 now discloses the 2026-06-17 Eastmoney Stock Connect top-10 deal API recheck as partial public deal-rank context, while maintaining the boundary that it is not beneficial-owner positioning or terminal-grade order flow.
- Chapter 12 now explicitly states that the latest public search still found only secondary/social/repost sources for NVIDIA, Google TPU/ASIC, Rubin, Apple and M9/M10 style claims.
- Chapter 2 and Chapter 11 include reader-visible `Data quality boundary` and `Invalidation` labels so the deterministic quality gate and the PDF semantics are aligned.

Verification evidence:

- JSON validation: `python -m json.tool workspace/research/semiconductor-pcb-20260612/unresolved_requirements.json` succeeded.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports `main.pdf` has 68 pages, A4, created Wed Jun 17 21:34:20 2026 CST.
- PDF text extraction confirms the new content: `RPT_MUTUAL_TOP10DEAL`, `2026 年 6 月 17 日`, `beneficial-owner`, `终端级逐笔/订单流`, `未取得可审计`, `Data quality boundary` and `Invalidation`.
- Deterministic report quality evaluator now reports 100.0 / excellent, 6/6 checks passed, for the current 68-page PDF.

Completion decision:

- Do not mark the active goal complete.
- The public-source work is now refreshed and evidence-backed, but three strict requirements remain externally blocked: named customer/platform revenue split, terminal-grade beneficial-owner/order-flow positioning, and customer/platform bottom-up EPS assumptions.
- `unresolved_requirements.json` now records `last_reviewed=2026-06-17` and status `blocked_by_unavailable_paid_or_non_public_data`.

## 2026-06-17 Eastmoney Stock Connect Holding Detail Recheck

After the initial 2026-06-17 recheck found only partial Stock Connect top-10 deal rows, the Eastmoney `hsgtV2/StockHdDetail` page JavaScript was inspected further. That exposed two more directly relevant public DataCenter reports:

- `RPT_MUTUAL_HOLDSTOCKNDATE_STA_NEW` for quarterly single-stock Stock Connect holding statistics.
- `RPT_MUTUAL_HOLDNDATE_DET_NEW` for participant / custodian-level holding detail by stock and holding date.

Evidence added:

- `data/eastmoney_hsgt_holding_recheck_20260617.md`
- `data/eastmoney_hsgt_holding_recheck_20260617.json`
- `data/raw_eastmoney_hsgt_holding_recheck_20260617/`

Coverage:

- 12/12 report-universe tickers now have Eastmoney public Stock Connect holding statistics and participant/custodian detail for 2026Q1.
- Fields include holding shares, QoQ holding change, participant count, holding market cap, total-share ratio, top participant, top participant shares and top-five participant market-value concentration.
- Examples: Hudian 2026Q1 Stock Connect holding 19,388.13万股, +35.38% QoQ, 53 participants, top participant HSBC, top-five MV share 94.33%; Shengyi 15,102.36万股, +20.64% QoQ, 50 participants; Pengding 5,707.02万股, -9.03% QoQ, 34 participants.

Files updated:

- `sections/ch09_secondary_market.tex` adds Exhibit 27b-4.
- `data_room_index.md` registers the new markdown, JSON and raw archive.
- `missing_data_request_pack.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now distinguish public participant/custodian detail from still-missing beneficial-owner / terminal-grade positioning.

Verification evidence:

- JSON validation succeeded for both `unresolved_requirements.json` and `data/eastmoney_hsgt_holding_recheck_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 68 pages, A4, created Wed Jun 17 21:42:46 2026 CST.
- PDF text extraction confirms Exhibit 27b-4 and the new API names `RPT_MUTUAL_HOLDSTOCKNDATE_STA_NEW` / `RPT_MUTUAL_HOLDNDATE_DET_NEW` are present.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This materially improves the public Stock Connect / northbound positioning coverage and closes a previously weak public participant-detail layer for all 12 tickers.
- It still does not close the strict remaining requirement for beneficial-owner positioning, official active/passive classification, daily post-rule-change northbound changes or terminal-grade realtime order flow.

## 2026-06-17 Full Visible Fund-Holder Type Recheck

The remaining ownership gap also included official active/passive fund classification. A paid Wind/Choice active/passive terminal label remains unavailable, but the public fund-holder layer was strengthened beyond the earlier top-fund examples and name-only proxy.

Evidence added:

- `data/fund_holder_full_type_recheck_20260617.md`
- `data/fund_holder_full_type_recheck_20260617.json`
- `data/raw_fund_holder_full_type_recheck_20260617/`

Method:

- Reran AkShare `stock_fund_stock_holder` for 11 tickers with visible public fund-holder rows.
- Loaded AkShare `fund_name_em` and mapped latest-period holder rows to Eastmoney public fund types where available.
- Used the existing name-rule bucket only for residual unmapped rows.

Coverage:

- 1,986 latest-period visible fund-holder rows were rechecked.
- All 11 visible-fund-holder tickers were covered.
- By-ticker fund-type mapping coverage is 97.01%--100.0%.
- Chapter 9 now includes Exhibit 25c-2 with equity/active-like, passive/index and bond/fixed-income public type buckets.

Verification evidence:

- JSON validation succeeded for `data/fund_holder_full_type_recheck_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 68 pages, A4, created Wed Jun 17 21:50:56 2026 CST.
- PDF text extraction confirms Exhibit 25c-2 and the full visible fund type recheck are present, including Shenghong passive/index share at 36.20%.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This materially improves public fund-style classification coverage from top examples to all visible latest-period holder rows.
- It still does not close the strict requirement for official Wind/Choice-style active/passive ownership labels, beneficial-owner data or a complete paid-terminal institutional ownership database.

## 2026-06-17 Current Global-Broker Visible Text Recheck

The remaining source gap also included current JPM / Goldman / Citi / UBS / HSBC original reports. A fresh public search was run for the most important missing global-broker items. No original PDFs were recovered, but visible public text was archived for three current high-impact repost/transcript sources.

Evidence added:

- `data/global_broker_current_recheck_20260617.md`
- `data/global_broker_current_recheck_20260617.json`
- `workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/`

Archived visible sources:

- JPM / Shenghong via Reportify and Sina: H-share target HKD600; 2026--2028 revenue about 354/600/842亿元; NPP about 90/172/256亿元; 2025--2028 NPP CAGR 81%; AI/HPC PCB, MLPCB and high-end HDI share claims; 2026 capex 180亿元; NVIDIA Rubin/Rubin Ultra and Google TPU/ASIC exposure discussed.
- Goldman / Shengyi via Sina: target raised to RMB217.6; 52亿元 high-end CCL capex; potential annual revenue contribution about 93亿元 at full utilization; global AI server CCL market value +142% in 2026 and +222% in 2027; 2026--2028 EPS 2.43/4.83/7.09.
- Citi / Shengyi via Sina: target raised from RMB96 to RMB195; AI CCL share about 10% in 2025, 15% currently and 20% by end-2026; monthly capacity path from about 8.0--8.5mn sheets to 9.6mn / 10.4mn / 15.0mn; 2026--2028 CCL gross margin assumptions of 28.2% / 30%+ / 32.2%.

Files updated:

- `sections/ch07_sentiment.tex` now distinguishes these as visible repost/transcript inputs to public sentiment.
- `sections/ch08_valuation.tex` updates the target-price comparability audit for JPM/Shenghong and Goldman/Citi/Shengyi.
- `sections/ch12_appendix.tex` adds the visible text archive rows.
- `data_room_index.md`, `missing_data_request_pack.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now record the new evidence and boundary.

Verification evidence:

- JSON validation succeeded for `data/global_broker_current_recheck_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 68 pages, A4, created Wed Jun 17 21:58:38 2026 CST.
- PDF text extraction confirms the new material is present: JPM Shenghong 600 HKD target, Goldman Shengyi 217.6 target, Citi Shengyi 195 target and Reportify/Sina visible-source treatment.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This improves the public global-broker scenario layer and removes the weaker state where some high-impact foreign-broker forecasts were only referred to indirectly.
- It still does not close the strict original-report requirement because the sources are repost/transcript pages, not original JPM / Goldman / Citi PDFs; UBS/Pengding and HSBC/Citi original current PDFs remain unavailable from public paths.
- These visible texts also do not close named-customer/platform revenue split because NVIDIA / Google / Rubin references remain broker-stated scenarios rather than audited customer revenue tables.

## 2026-06-17 Repost Image OCR Probe

The visible JPM / Goldman / Citi repost pages contained embedded report screenshots. To avoid leaving those images as uninspected evidence, the images were downloaded and OCR was attempted.

Evidence added:

- `data/global_broker_image_ocr_evidence_20260617.md`
- `data/global_broker_image_ocr_evidence_20260617.json`
- `workspace/research/semiconductor-pcb-20260612/sources/broker-global-current-recheck-20260617/images/`
- `workspace/research/semiconductor-pcb-20260612/tools/tessdata/chi_sim.traineddata`

Method:

- Downloaded embedded images from JPM/Shenghong, Goldman/Shengyi and Citi/Shengyi repost pages.
- Installed a local Tesseract `chi_sim` model under the case directory because the system Tesseract only had `eng`, `osd` and `snum`.
- OCRed images via Tesseract stdout capture and archived both image files and OCR text.

Useful OCR findings:

- JPM/Shenghong financial highlights image: 2023/2024/2025/1Q26 revenue 7.931/10.731/19.292/5.519bn RMB; GPM 20.7%/22.7%/35.2%/34.5%; net profit 0.671/1.154/4.312/1.288bn RMB.
- JPM/Shenghong revenue-assumption image: 2026E/2027E/2028E MLPCB 15.744/28.226/40.658bn RMB; HDI 16.082/27.785/39.287bn RMB; total revenue 35.450/59.955/84.226bn RMB.
- Citi/Shengyi image: e-glass fabric ASP YTD labels for 1080/2116/7628 series at about +95%/+91%/+60%.

Files updated:

- `sections/ch07_sentiment.tex` now mentions the OCR-extracted JPM product revenue assumptions and Citi material price labels.
- `sections/ch08_valuation.tex` adds JPM OCR as a supplemental Shenghong model row and source note.
- `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now register the OCR evidence and boundary.

Verification evidence:

- JSON validation succeeded for `data/global_broker_image_ocr_evidence_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 68 pages, A4, created Wed Jun 17 22:09:03 2026 CST.
- PDF text extraction confirms the OCR evidence entered the report: total revenue 354.50/599.55/842.26亿元, MLPCB 157.44/282.26/406.58亿元, HDI 160.82/277.85/392.87亿元, and e-glass fabric 1080/2116/7628 YTD +95%/+91%/+60%.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This closes the previously uninspected repost-image layer and adds product-line model support for Shenghong.
- It still does not close named customer/platform revenue split or a full customer/platform bottom-up EPS model because the OCR evidence is product-line and scenario-level, not customer-revenue-level, and remains derived from repost images rather than original PDFs.

## 2026-06-17 Structured JPM/Shenghong OCR Product Model

The useful JPM/Shenghong OCR output was converted from raw OCR text into a structured model file so the product-line bridge is auditable without re-reading the image.

Evidence added:

- `data/jpm_shenghong_ocr_product_model_20260617.md`
- `data/jpm_shenghong_ocr_product_model_20260617.json`

Structured data:

- Financial highlights: 2023/2024/2025/1Q26 revenue, gross margin and net profit.
- Product-line revenue assumptions for 2023--2028E: MLPCB, HDI, single/double-layer PCB, FPC, others and total.
- Revenue contribution and YoY growth by product line.

Key model read-through:

- Total revenue rises from RMB 19.292bn in 2025 to RMB 35.450bn / 59.955bn / 84.226bn in 2026E / 2027E / 2028E.
- MLPCB and HDI together account for about 89% / 93% / 95% of 2026E / 2027E / 2028E revenue in this OCR scenario.
- Chapter 8 now includes Exhibit 22b with the structured product-line bridge.

Verification evidence:

- JSON validation succeeded for `data/jpm_shenghong_ocr_product_model_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 68 pages, A4, created Wed Jun 17 22:16:01 2026 CST.
- PDF text extraction confirms Exhibit 22b and the structured total revenue row `354.50 / 599.55 / 842.26` are present.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This improves the bottom-up layer from a broad forecast-line view to a product-line revenue bridge for Shenghong.
- It still does not close the strict customer/platform bottom-up EPS requirement because there is no named customer/platform revenue, ASP, shipment, platform margin, depreciation or working-capital schedule.

## 2026-06-17 Structured Goldman/Shengyi OCR Revision Model

The Goldman/Shengyi transformed images from Sina initially failed because the script stripped the `w700...` image transformation suffix. The full transformed URLs were re-fetched, OCRed and structured.

Evidence added:

- `data/goldman_shengyi_ocr_revision_model_20260617.md`
- `data/goldman_shengyi_ocr_revision_model_20260617.json`
- `sources/broker-global-current-recheck-20260617/images/goldman-shengyi-full-01.stdout-ocr.txt`

Structured data:

- Goldman/Shengyi Exhibit 1 earnings revision table.
- 2026E / 2027E / 2028E old/new estimates and revision percentages for revenue, gross profit, EBIT, net income and diluted EPS.

Key model read-through:

- Net income new estimates: RMB 5.821bn / 11.577bn / 16.975bn for 2026E / 2027E / 2028E, revised up 8% / 28% / 29%.
- Diluted EPS new estimates: 2.43 / 4.83 / 7.09 for 2026E / 2027E / 2028E.
- Chapter 8 now includes Goldman OCR as an additional Shengyi model row.

Verification evidence:

- JSON validation succeeded for `data/goldman_shengyi_ocr_revision_model_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 69 pages, A4, created Wed Jun 17 22:22:20 2026 CST.
- PDF text extraction confirms Goldman OCR values entered the report: 58.21 / 115.77 / 169.75亿元 and EPS 2.43 / 4.83 / 7.09.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This further improves the foreign-broker forecast-revision layer for Shengyi.
- It still does not close original-PDF availability or customer/platform revenue split, because it is OCR-derived from a repost image and does not disclose named customer or platform-level revenue.

## 2026-06-17 EPS Model Assumption Matrix

The remaining bottom-up EPS gap includes model-base assumptions such as tax rate, share count, cash conversion and working capital. A unified public-source assumption matrix was created to separate what can be completed from public data from what remains private/customer-specific.

Evidence added:

- `data/eps_model_assumption_matrix_20260617.md`
- `data/eps_model_assumption_matrix_20260617.json`

Method:

- Combined official 2026Q1 metrics from `official_financials.json`.
- Reused working-capital days from `working_capital_days_analysis.md`.
- Reused cash-conversion fields from `working_capital_cash_conversion.json`.
- Added broker operating-line tax rate, OCF/NPP, FCF after capex and implied share-count assumptions from `editable_eps_model.json` where available.
- Normalized broker capex sign conventions using `OCF - abs(capex)`.

Coverage:

- 12/12 names have Q1 revenue, NPP, EPS, implied share count, GM, net margin, OCF/NPP and working-capital approximation.
- Core operating-line names have explicit 2026E tax-rate and OCF/NPP assumptions from broker models where available.
- Chapter 8 now includes Exhibit 28b.

Verification evidence:

- JSON validation succeeded for `data/eps_model_assumption_matrix_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 69 pages, A4, created Wed Jun 17 22:40:02 2026 CST.
- PDF text extraction confirms Exhibit 28b is present with implied share count, OCF/NPP, CCC and tax-rate fields.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This fills the public model-base layer for tax, share count, cash conversion and working capital.
- It still does not close the strict customer/platform bottom-up EPS requirement because named platform revenue, ASP, shipments, platform margin, project-level depreciation and customer-specific working capital are not publicly disclosed.

## 2026-06-17 Customer-Side Victory Giant / NVIDIA Recheck

The remaining named-customer gap included secondary claims that Victory Giant / Shenghong had been named or qualified by NVIDIA / ODM partners. A targeted customer-side recheck was run to avoid relying on social-media snippets.

Evidence added:

- `data/customer_side_victory_giant_recheck_20260617.md`
- `sources/probe-customer-side-20260617/nvidia-q2-fy2026-results.html`
- `sources/probe-customer-side-20260617/asiabusinessoutlook-victory-giant.html`
- `sources/probe-customer-side-20260617/winappnet-victory-giant.html`

Findings:

- NVIDIA Q2 FY2026 investor-relations release was archived and searched for Victory / Giant / PCB / substrate / NVL72 / ODM / qualified / supplier. It did not contain a named Victory Giant supplier statement.
- Asia Business Outlook states Victory Giant joined NVIDIA's H-series AI accelerator supply chain in 2023 and became a tier-one supplier in 2024, but it is a secondary media source.
- Winappnet / MEXC article describes Victory Giant as a key NVIDIA AI server PCB supplier and cites its HK prospectus market position, but it is also secondary media.

Verification evidence:

- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 69 pages, A4, created Wed Jun 17 22:28:57 2026 CST.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This closes another customer-side probe path by documenting that the NVIDIA official release did not confirm the social-media supplier claim.
- It still does not close the named-customer/platform revenue split because secondary articles do not disclose product/order/ASP/shipment/platform allocation or revenue.

## 2026-06-17 Cloud Customer Supplier Disclosure Recheck

The remaining customer-chain gap also involved Google / Microsoft / Amazon-AWS official supplier disclosures. A cloud-customer supplier disclosure recheck was run to determine whether public supplier lists or responsible-sourcing pages disclose named PCB/CCL suppliers.

Evidence added:

- `data/cloud_customer_supplier_disclosure_recheck_20260617.md`
- `sources/probe-cloud-customer-side-20260617/2024-amazon-sustainability-report.pdf`
- `sources/probe-cloud-customer-side-20260617/2024-amazon-sustainability-report-aws-summary.pdf`
- `sources/probe-cloud-customer-side-20260617/amazon-supplier-manual-english.pdf`
- `sources/probe-cloud-customer-side-20260617/amazon-supply-chain-standards-english.pdf`
- Microsoft responsible-sourcing / reports-hub access-denied shells

Findings:

- Amazon 2024 Sustainability Report states its 2024 supplier list included nearly 2,300 finished-product suppliers and component suppliers and that Amazon shares its supplier list to Open Supply Hub.
- The archived Amazon report and AWS summary do not expose Victory Giant, WUS, Avary, Shennan, PCB or printed-circuit-board supplier rows.
- Guessed Amazon supplier-list PDF URLs returned HTTP 404.
- Open Supply Hub anonymous API calls for Amazon, Victory Giant, Avary, WUS Printed and Shennan returned `Authentication credentials were not provided`.
- Microsoft responsible sourcing and reports hub pages returned access-denied shells in this environment.
- Google official searches did not reveal a supplier list naming PCB/CCL suppliers.

Verification evidence:

- JSON validation succeeded for `unresolved_requirements.json` after adding the cloud-customer evidence boundary.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 69 pages, A4, created Wed Jun 17 22:52:32 2026 CST.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This closes another public customer-side path by documenting that cloud-customer official / responsibility disclosures do not provide named PCB supplier revenue in the current environment.
- It still does not close named customer/platform revenue split. The strongest remaining route is authenticated Open Supply Hub, paid supply-chain/BOL data, original broker PDF, or direct company/customer confirmation.

## 2026-06-17 Eastmoney Intraday Fund-Flow Proxy

The remaining order-flow gap included a possible finer public fund-flow layer beyond daily dayline proxies. Eastmoney's individual fund-flow page JavaScript was inspected and a minute-level public endpoint was identified.

Evidence added:

- `data/eastmoney_intraday_fund_flow_20260617.md`
- `data/eastmoney_intraday_fund_flow_20260617.json`
- `data/raw_eastmoney_intraday_fund_flow_20260617/`

Method:

- Inspected Eastmoney `zjlx/stock.js`.
- Confirmed `push2.eastmoney.com/api/qt/stock/fflow/kline/get` with `klt=1` returns intraday cumulative fund-flow rows.
- Corrected parsing: minute endpoint returns six fields, `time`, `main_net`, `small_net`, `medium_net`, `large_net`, `super_large_net`, rather than the daily 13-field format.

Coverage:

- 12/12 report-universe tickers have 240 one-minute rows for 2026-06-17.
- Chapter 9 now includes Exhibit 30b.

Verification evidence:

- JSON validation succeeded for `data/eastmoney_intraday_fund_flow_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 70 pages, A4, created Wed Jun 17 23:06:01 2026 CST.
- PDF text extraction confirms Exhibit 30b is present with intraday main/super-large/large/medium/small net-flow buckets.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This fills the public intraday fund-flow proxy layer for all current report tickers.
- It still does not close the strict terminal-grade order-flow requirement because it is not exchange tick/order-book data, not beneficial-owner positioning and not a paid-terminal institutional order-flow feed.

## 2026-06-17 Microsoft Top 100 Production Suppliers

The Microsoft responsible-sourcing page was re-fetched with a desktop user agent and parsed for links. The generic `https://aka.ms/Top100Suppliers` shortlink resolved to the official Microsoft FY24 Top 100 Production Suppliers PDF.

Evidence added:

- `data/microsoft_top100_supplier_pcb_evidence_20260617.md`
- `data/microsoft_top100_supplier_pcb_evidence_20260617.json`
- `sources/probe-cloud-customer-side-20260617/Microsoft-Top-100-Production-Suppliers-FY24.pdf`
- `sources/probe-cloud-customer-side-20260617/Microsoft-Top-100-Production-Suppliers-FY24.txt`

Findings:

- The official Microsoft FY24 top production supplier list names several board / PCB / component suppliers, including AVARY HOLDING (SHENZHEN), VICTORY GIANT TECHNOLOGY (HUIZHOU), HANNSTAR BOARD, TRIPOD TECHNOLOGY, UNIMICRON TECHNOLOGY (KUNSHAN), SUZHOU DONGSHAN PRECISION, SAMSUNG ELECTRO MECHANICS and MEKTEC.
- This is the strongest customer-side official supplier-list evidence recovered so far for the PCB universe.
- Chapter 5 now includes Exhibit 12h.

Verification evidence:

- JSON validation succeeded for `data/microsoft_top100_supplier_pcb_evidence_20260617.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 70 pages, A4, created Wed Jun 17 23:17:43 2026 CST.
- PDF text extraction confirms Exhibit 12h and Microsoft Top 100 supplier-list evidence entered the report.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This materially improves customer-side official named-supplier evidence for Microsoft commercial hardware.
- It still does not close named platform/customer revenue split because the Microsoft list does not disclose product category, PCB revenue, AI/cloud platform allocation, ASP, shipment or order value.

## 2026-06-17 Open Supply Hub Front-End Search

Because Amazon's sustainability report states its supplier list is shared to Open Supply Hub, the OS Hub front end was tested after installing Chrome for `agent-browser`.

Evidence added:

- `data/opensupplyhub_customer_network_evidence_20260617.md`
- `data/opensupplyhub_customer_network_evidence_20260617.json`
- `sources/probe-cloud-customer-side-20260617/opensupplyhub-victory-giant-detail.png`
- `sources/probe-cloud-customer-side-20260617/opensupplyhub-avary-detail.png`

Findings:

- Open Supply Hub search for `VICTORY GIANT TECHNOLOGY` returned `Victory Giant Technology (Huizhou) Co., Ltd.`, OS ID `CN2022297DRGCBN`; the facility detail page shows `Amazon.com, Inc.` in Supply Chain Network.
- Open Supply Hub search for `AVARY HOLDING` returned `Avary Holding (Shenzhen) Co. Ltd`, OS ID `CN2022306H1D256`; the facility detail page shows `Amazon.com, Inc.` and `Alliance for Water Stewardship [Public List]` in Supply Chain Network.

Verification evidence:

- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 70 pages, A4, created Wed Jun 17 23:35:40 2026 CST.
- PDF text extraction confirms Exhibit 12h contains Microsoft Top 100, Open Supply Hub and Amazon.com evidence.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This materially improves customer-side public network evidence for Amazon-linked Victory Giant and Avary facilities.
- It still does not close named customer/platform revenue split because OS Hub does not disclose product category, PCB/CCL revenue, AWS/AI platform allocation, ASP, shipment or order value.

## 2026-06-17 Open Supply Hub Facility API JSON

After confirming OSH front-end visibility, browser network logs were inspected. The front end uses `X-OAR-Client-Key`; replaying the full request headers allowed direct archival of the facility API JSON.

Evidence added:

- `sources/probe-cloud-customer-side-20260617/osh-CN2022297DRGCBN.json`
- `sources/probe-cloud-customer-side-20260617/osh-CN2022306H1D256.json`
- Updated `data/opensupplyhub_customer_network_evidence_20260617.md`
- Updated `data/opensupplyhub_customer_network_evidence_20260617.json`

Findings:

- Victory Giant Technology (Huizhou), OS ID `CN2022297DRGCBN`, has Amazon.com, Inc. contributor rows from Amazon Facility List 2022, 2023 and 2024.
- Avary Holding (Shenzhen), OS ID `CN2022306H1D256`, has Amazon.com, Inc. contributor row from Amazon Facility List 2023 and Alliance for Water Stewardship 2022 Facility List contributor row.

Verification evidence:

- JSON validation succeeded for `unresolved_requirements.json`, `opensupplyhub_customer_network_evidence_20260617.json`, `osh-CN2022297DRGCBN.json` and `osh-CN2022306H1D256.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 70 pages, A4, created Wed Jun 17 23:51:41 2026 CST.
- PDF text extraction confirms Exhibit 12h includes Amazon Facility List 2022/2023/2024 and Open Supply Hub evidence.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This upgrades the OSH evidence from screenshot-only to raw facility API evidence.
- It still does not close the strict named-customer/platform revenue split because OSH lists contributor/facility relationships, not products, order values, revenue, ASP, shipments or platform allocation.

## 2026-06-17 Open Supply Hub Facility Metadata Extraction

The OSH raw facility JSON was further inspected for useful fields beyond contributor names.

Evidence updated:

- `data/opensupplyhub_customer_network_evidence_20260617.md`
- `data/opensupplyhub_customer_network_evidence_20260617.json`
- `sources/probe-cloud-customer-side-20260617/osh-CN2022297DRGCBN.json`
- `sources/probe-cloud-customer-side-20260617/osh-CN2022306H1D256.json`

Fields extracted:

- Victory Giant Technology (Huizhou): sector `Electronics`; Amazon-contributed facility type / processing type `Finished goods`; Amazon.com, Inc. contributor rows from Amazon Facility List 2022 / 2023 / 2024; worker-count evidence from Amazon rows.
- Avary Holding (Shenzhen): sector `Electronics`; Amazon.com, Inc. contributor row from Amazon Facility List 2023; Alliance for Water Stewardship 2022 Facility List row.

Verification evidence:

- JSON validation succeeded for `unresolved_requirements.json`, `opensupplyhub_customer_network_evidence_20260617.json`, `osh-CN2022297DRGCBN.json` and `osh-CN2022306H1D256.json`.
- Build: `PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/semiconductor-pcb-20260612/` completed successfully.
- PDF metadata: `pdfinfo` reports 70 pages, A4, created Wed Jun 17 23:58:27 2026 CST.
- PDF text extraction confirms Exhibit 12h includes Amazon Facility List 2022/2023/2024, `sector=Electronics` and Open Supply Hub evidence.
- Deterministic quality evaluator remains 100.0 / excellent, 6/6 checks passed.

Completion impact:

- This deepens the customer-side network evidence from named contributor to sector/facility metadata.
- It still does not disclose product category detail, PCB/CCL revenue, AWS/AI platform allocation, ASP, shipment or order value.

## 2026-06-18 Open Supply Hub Expanded Supplier Search

The next unrepeated public-source route was to expand OSH coverage beyond Victory Giant and Avary, using the Microsoft FY24 Top 100 board/component supplier list and report-universe names as search seeds.

Evidence added:

- `data/opensupplyhub_expanded_supplier_evidence_20260618.md`
- `data/opensupplyhub_expanded_supplier_evidence_20260618.json`
- `sources/probe-cloud-customer-side-20260617/osh-expanded-20260618/` with raw search JSON and facility-detail JSON.

Search scope:

- Tripod / Tripod Technology
- Unimicron Technology
- Suzhou Dongshan Precision / Dongshan Precision
- Shennan Circuits
- Meiko Electronics
- MEKTEC
- HannStar Board
- Samsung Electro Mechanics
- WUS Printed Circuit

Recovered public-list network evidence:

- Tripod: three relevant China facilities with Amazon.com, Apple, Dell, Samsung and Alliance for Water Stewardship public-list rows. Some rows include coarse metadata: `Parts/Components`, `Other direct material suppliers`, `Semiconductor Manufacturing`, `Finished goods` and worker-count fields.
- Unimicron: six China/Taiwan/Japan facilities with Apple public-list rows and one Alliance for Water Stewardship row carrying `Semiconductor Manufacturing` metadata.
- Suzhou Dongshan Precision: three China facilities with Apple public-list rows; one facility also has a Sheffield Hallam University Forced Labour Lab risk-list contributor row.
- Meiko: five China/Vietnam/Japan facilities with Amazon, Samsung and gBizINFO rows; Amazon rows include `Finished goods` for Wuhan and Vietnam facilities.
- Mektec: one Taiwan facility with Amazon and Apple rows; Amazon rows include `Finished goods` and worker-count fields.
- Shennan Circuits USA: one U.S. location with a U.S. Small Business Administration row only.
- HannStar Board, Samsung Electro Mechanics and WUS Printed Circuit had no material OSH hit under the tested search terms.

Report/audit update:

- Chapter 5 Exhibit 12h now includes the expanded OSH pass.
- `data_room_index.md`, `source_exhaustion_log.md`, `missing_data_request_pack.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now reference the expanded OSH evidence.

Completion impact:

- This materially improves public customer-network evidence beyond Victory Giant and Avary.
- It still does not close `named_platform_customer_revenue_split` or `bottom_up_customer_platform_eps_model` because OSH does not disclose customer product, PCB/CCL revenue, AI/cloud platform allocation, ASP, shipment, order value, margin, depreciation or EPS assumptions.

## 2026-06-18 Upstream Supplier-List Source Files

After the expanded OSH pass, the next unrepeated route was to trace OSH contributor rows back to upstream customer or certification source files where publicly retrievable.

Evidence added:

- `data/upstream_supplier_list_evidence_20260618.md`
- `data/upstream_supplier_list_evidence_20260618.json`
- `sources/probe-upstream-supplier-lists-20260618/`

Archived files and useful hits:

- Apple Supplier List 2018 (`apple-supplier-list-g.pdf` / `.txt`): Suzhou Dongshan Precision Manufacturing, Tripod Technology and Unimicron Technology facility-address rows.
- Apple Supplier List FY2020 (`apple-supplier-list-k.pdf` / `.txt`): Suzhou Dongshan Precision Manufacturing, Tripod Technology Corporation, Unimicron Technology Corporation, Samsung Electro-Mechanics Company Limited and Zhen Ding Technology Holding Limited primary-location rows.
- Dell Public Supplier List FY2025 (`dell-public-supplier-list-official-retry.pdf` / `.txt`): list covers at least 95% of Dell spend in FY2025; Tripod rows show `Parts / Components` and `Other direct material suppliers`; HannStar and Gold Circuit component rows also appear.
- Samsung Electronics Supplier List (`samsung-supplier-list.pdf` / `.txt`): list covers component and outsourcing suppliers representing 80% of Samsung Electronics procurement expenditures for materials and manufacturing; relevant rows include Meiko Electronics, Samsung Electro-Mechanics, Tripod Technology, Korea Circuit, Ibiden and Daeduck Electronics.
- Alliance for Water Stewardship certified-sites page (`aws-certified-sites.html`): Avary/Hongqisheng, Qing Ding / Zhen Ding group, Tripod Wuxi and Victory Giant Huizhou certified-site rows, sector `Electronics & Semiconductor Manufacturing`.

Report/audit update:

- Chapter 5 Exhibit 12h now includes upstream supplier-list files as a distinct evidence layer.
- `data_room_index.md`, `source_exhaustion_log.md`, `missing_data_request_pack.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now reference this upstream-source pass.

Completion impact:

- This strengthens customer-side and certification-source lineage behind the OSH rows.
- It still does not close strict customer/platform revenue split or bottom-up EPS because none of these lists disclose product shipped to a platform, revenue, ASP, shipment, order value, margin, depreciation or working-capital assumptions.

## 2026-06-18 Tencent Quote Snapshot Refresh

The next non-repeated market-data action was to refresh the public valuation anchor, because the report still referenced the 2026-06-16 Tencent quote snapshot.

Evidence added:

- `data/raw_tencent_quote/quote_20260618.txt`
- `data/tencent_realtime_market_snapshot_20260618.md`
- `data/tencent_realtime_market_snapshot_20260618.json`

Result:

- Tencent `qt.gtimg.cn` returned 12/12 current-universe tickers.
- The fetch was run on 2026-06-18; embedded quote timestamps are around 2026-06-17 16:14 CST.
- Parsed fields include price, percentage change, turnover, amount, total market capitalization, PE TTM and PB.
- The corrected Tencent field layout uses field 44 for total market capitalization, field 39 for PE and field 46 for PB; field 45 is retained as secondary market-cap raw value but not used as the main anchor.

Report/audit update:

- Chapter 8 valuation boundary, valuation-space note and PE scorecard now reference `data/tencent_realtime_market_snapshot_20260618.md`.
- Chapter 9 market-data limitation and data availability table now reference the refreshed Tencent snapshot.
- `main.tex`, `latest_market_refresh_audit.md`, `data_room_index.md` and `unresolved_requirements.json` now reference the refreshed snapshot.

Completion impact:

- This updates public price/market-cap/PE/PB anchors for all 12 tickers.
- It does not close terminal-grade positioning/order-flow because Tencent quote feed is not exchange tick/order-book data, beneficial-owner data, or paid terminal flow.

## 2026-06-18 Eastmoney / AkShare Current Stock Connect API Probe

The next non-repeated positioning route was to test public Eastmoney / AkShare Stock Connect APIs beyond the already archived 2026Q1 participant/custodian bridge.

Evidence added:

- `data/eastmoney_hsgt_public_api_probe_20260618.md`
- `data/raw_eastmoney_hsgt_public_api_probe_20260618/`
- `data/raw_eastmoney_hsgtcg_list_20260618.html`

Routes tested:

- AkShare `stock_hsgt_individual_detail_em` / Eastmoney `RPT_MUTUAL_HOLD_DET`
- AkShare `stock_hsgt_institution_statistics_em` / Eastmoney `PRT_MUTUAL_ORG_STA`
- AkShare `stock_hsgt_stock_statistics_em` / Eastmoney `RPT_MUTUAL_STOCK_HOLDRANKS`
- AkShare `stock_hsgt_hold_stock_em` / Eastmoney `RPT_MUTUAL_STOCK_NORTHSTA`
- AkShare `stock_hsgt_hist_em` aggregate northbound history

Result:

- `data.eastmoney.com/hsgtcg/list.html` was archived; the page shell shows `个股排行（2024-08-16）`.
- `RPT_MUTUAL_STOCK_NORTHSTA` returned `服务器繁忙` (`code=9701`) for tested current dates, 2026Q1 and the 2024-08-16 page-shell date across intervals 1/3/5/10/M/Q/Y.
- `RPT_MUTUAL_HOLD_DET`, `PRT_MUTUAL_ORG_STA` and `RPT_MUTUAL_STOCK_HOLDRANKS` returned `返回数据为空` (`code=9201`) for current windows.
- Aggregate northbound flow history still returns rows through 2026-06-17, but recent buy/sell/net fields are null after the disclosure-rule change.

Report/audit update:

- Chapter 9 now records this as a failed public current holding-rank route.
- `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md`, `missing_data_request_pack.md` and `unresolved_requirements.json` now reference the probe.

Completion impact:

- This closes another public Stock Connect path as tested.
- It still does not provide daily post-rule-change northbound changes, beneficial-owner positioning, active/passive institutional ownership or terminal-grade order flow.

## 2026-06-18 Current CNInfo / SZSE Interaction Sweep

The next non-repeated customer-chain route was to search current official issuer-interaction rows for AI/customer/order/pricing/capacity terms across the report universe.

Evidence added:

- `data/current_cninfo_interaction_sweep_20260618.md`
- `data/current_cninfo_interaction_sweep_20260618.json`
- `data/raw_cninfo_current_interaction_sweep_20260618/`

Execution note:

- CNInfo / SZSE Interactive Easy is now complete for the 8 Shenzhen-listed report names in the current universe: 160 company-question files cover 20 keywords for each Shenzhen-listed name.
- The two previously missing DingTai keyword files (`数据中心`, `服务器`) were added with official keyboard lookup `secid=9900047405`; both returned zero rows.
- Completed files contain 35 matched rows, which deduplicate to 14 unique question IDs. Shanghai-listed report names remain covered by the bounded SSE / 上证e互动 probe rather than CNInfo.

Useful evidence:

- Hudian: current rows cover high-end PCB pricing, Rubin/NVIDIA confidentiality, CoWoP/mSAP/light-copper/M10 development and commercialization risks, P2Pack data-center migration, Thailand ramp and AI PCB price pass-through.
- Victory Giant: current rows cover ASIC progress, NVIDIA Spark, midplane, mSAP/orthogonal backplane, CB300, domestic chip customers, Tesla AI5, GB200/GB300, CoWoP, Huizhou/Thailand ramp and repeated commercial-policy restrictions.
- Xingsen: one question-only Rubin rack value-chain row was recovered without issuer reply, so it is archived only and not promoted as confirmed evidence.

Report/audit update:

- Chapter 5 now references the CNInfo sweep in the Hudian and Victory Giant quantified bridge.
- `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md`, `missing_data_request_pack.md` and `unresolved_requirements.json` now reference the sweep.

Completion impact:

- This improves official issuer-side product/ramp/pricing/disclosure-boundary evidence.
- It still does not close named customer/platform revenue split or customer/platform bottom-up EPS because the issuers continue to withhold specific customer names and business details.

## 2026-06-18 Hyperscaler Capex / AI Infrastructure Demand Evidence

The next non-repeated route was demand-side primary evidence: hyperscaler AI infrastructure capex. This does not identify suppliers, but it strengthens the customer-platform demand bridge and risk triggers.

Evidence added:

- `data/hyperscaler_capex_ai_infrastructure_evidence_20260618.md`
- `data/hyperscaler_capex_ai_infrastructure_evidence_20260618.json`
- `sources/probe-hyperscaler-capex-20260618/`

Archived source quality:

- Alphabet Q1 2026 earnings release PDF and text: official, usable.
- Amazon Q1 2026 About Amazon release HTML and extracted text: official, usable; direct S3 8-K object was expired/invalid and retained only as failed route.
- Meta Q1 2026 earnings-call transcript PDF and text: official, usable.
- Microsoft FY2026 Q3 investor URL: archived but static HTML was a thin/noindex shell and not used for capex numbers.

Useful evidence:

- Alphabet: Google Cloud revenue +63% to USD20.0bn, led by enterprise AI solutions and AI infrastructure; Q1 2026 purchases of property and equipment USD35.674bn; TTM PPE purchases USD109.924bn.
- Amazon: AWS sales +28% to USD37.6bn; free cash flow decline driven by USD59.3bn YoY increase in PPE purchases, primarily reflecting AI investments; chips business above USD20bn annual run-rate; OpenAI ~2GW Trainium commitment; Anthropic up to 5GW Trainium; 2.1mn+ AI chips landed and 1mn+ NVIDIA GPUs announced from 2026.
- Meta: Q1 capex USD19.8bn driven by servers, data centers and network infrastructure; 2026 capex guide raised to USD125--145bn due to higher component pricing and additional data-center costs; USD107bn contractual-commitment increase from cloud and infrastructure purchase agreements.

Report/audit update:

- Chapter 5 now includes a demand-side paragraph before the platform-to-earnings bridge.
- Chapter 11 risk matrix now ties AI capex slowdown to Alphabet/Amazon/Meta capex guide and infrastructure-spend triggers.
- `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now reference this packet.

Completion impact:

- This materially strengthens the public demand-side bridge.
- It still does not close named customer/platform revenue split or bottom-up EPS because these sources do not name PCB/CCL suppliers, products, order values, ASP, shipments, margins or platform-specific supplier revenue.

## 2026-06-18 SZSE Official Margin Financing Refresh

The next non-repeated positioning route was to retry the official Shenzhen Stock Exchange margin-financing endpoints, since the report already had SSE official data but Shenzhen-listed official detail remained blocked.

Evidence added:

- `data/szse_margin_financing_probe_20260618.md`
- `data/raw_szse_margin_probe_20260618/`

Routes tested:

- AkShare `stock_margin_detail_szse(date=20260617)`
- AkShare `stock_margin_szse(date=20260617)`
- AkShare `stock_margin_underlying_info_szse(date=20260617)`
- Direct SZSE `ShowReport/data` for `CATALOGID=1837_xxpl`, `TABKEY=tab1` and `tab2`, dates 2026-06-17 / 2026-06-16 / 2026-06-13
- Direct SZSE `ShowReport/data` for `CATALOGID=1834_xxpl`, `TABKEY=tab1`, dates 2026-06-17 / 2026-06-16 / 2026-06-13

Result:

- AkShare wrappers returned `ConnectionResetError(54, connection reset by peer)`.
- Direct official routes returned HTTP code `000` with connection reset or timeout.
- No durable SZSE official detail / summary / underlying-security file was retrieved.

Report/audit update:

- Chapter 9 margin-financing availability now records the 2026-06-18 SZSE official refresh boundary.
- `data_room_index.md`, `source_exhaustion_log.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now reference the refreshed probe.

Completion impact:

- This closes the official Shenzhen margin route for the current environment as retried and unavailable.
- It does not improve numeric Shenzhen margin coverage and does not provide terminal-grade order flow, beneficial-owner positioning or institutional ownership.

## 2026-06-18 Reverse Valuation Requirement Matrix

The next non-repeated EPS/model route was to convert current public market caps and public forecast ranges into the net-profit delivery required to justify target PE bands. This is a top-down discipline check, not a customer/platform EPS substitute.

Evidence added:

- `data/reverse_valuation_requirement_matrix_20260618.md`
- `data/reverse_valuation_requirement_matrix_20260618.json`

Method:

- Market cap source: `data/tencent_realtime_market_snapshot_20260618.json`.
- Forecast range source: `data/forecast_range_analysis.md`.
- For each covered name, current market cap was divided by the target PE band to estimate the implied NPP requirement.
- Required NPP was compared against the highest public forecast line for 2028E where available, or 2027E for Pengding.

Report/audit update:

- Chapter 8 now includes Exhibit 20b, the reverse valuation implied net-profit hurdle table.
- `data_room_index.md`, `completion_audit_manifest.md` and `unresolved_requirements.json` now reference the matrix.

Completion impact:

- This improves valuation discipline and makes the public delivery hurdle explicit.
- It still does not close customer/platform bottom-up EPS because it does not provide named customer revenue, ASP, shipments, platform margin, project depreciation or customer-specific working-capital assumptions.

## 2026-06-18 Source Registry and Claim Audit Refresh

After adding multiple evidence layers, the source-governance files were stale. A governance refresh was run to keep claim classifications aligned with the current data room.

Files updated:

- `data/source_registry.md`
- `data/claim_audit.md`

Source-registry additions:

- Tencent 2026-06-18 quote snapshot (`M04`)
- Microsoft FY24 Top 100 supplier evidence (`CUST-MS01`)
- OSH initial and expanded supplier/facility evidence (`OSH01`, `OSH02`)
- Upstream Apple/Dell/Samsung/AWS supplier-list evidence (`CUST-UP01`)
- Hyperscaler capex / AI infrastructure demand evidence (`CUST-CAPEX01`)
- Current CNInfo/SZSE/SSE issuer interaction sweep (`CNINFO-CUR01`)
- Eastmoney/AkShare current Stock Connect API probe (`FLOW-EM01`)
- SZSE official margin refresh (`FLOW-SZSE01`)
- Reverse valuation requirement matrix (`VAL-REV01`)

Claim-audit additions:

- Customer-side supplier-list rows are relationship/source-lineage evidence, not revenue evidence.
- Hyperscaler capex is demand-side evidence, not supplier revenue allocation.
- Public quote/fund-flow/margin/Stock Connect APIs are market proxies, not terminal-grade order flow.
- Reverse valuation hurdle is derived valuation discipline, not a customer/platform EPS model.

Completion impact:

- This improves report governance and reduces the risk that new evidence is overclaimed.
- It does not close the remaining hard gaps because the refreshed audit explicitly keeps supplier-list, capex, quote, flow and reverse-valuation evidence outside named customer revenue, terminal order flow and customer/platform EPS completion.

## 2026-06-18 Evidence Reference Integrity Audit

A machine-readable evidence-reference audit was run to validate that the completion audit and unresolved-requirement manifests point to real local artifacts.

Evidence added:

- `data/evidence_reference_integrity_audit_20260618.md`
- `data/evidence_reference_integrity_audit_20260618.json`

Result:

- Checked references: 343
- Path references: 342
- Glob references: 1
- Existing or matched: 343
- Problems: 0

Treatment:

- Wildcard references such as `sections/*.tex` are valid if they expand to existing files.
- This closes a manifest-integrity issue, but it does not prove non-public data availability or substantive completion of the hard requirements.

## 2026-06-18 Data Room Index Integrity Audit

A data-room index integrity audit was run to verify that explicit `Exists` rows in `data_room_index.md` match the local filesystem.

Evidence added:

- `data/data_room_index_integrity_audit_20260618.md`
- `data/data_room_index_integrity_audit_20260618.json`

Result:

- Exists rows checked: 182
- Mismatches: 0
- Required newly added references present: True

Treatment:

- This verifies data-room index file existence only. It does not prove that the evidence satisfies non-public customer/platform revenue, terminal-grade flow or customer/platform EPS requirements.

## 2026-06-18 Paid Access Recheck

A fresh paid/semi-paid access check was run because remaining hard gaps explicitly require terminal or non-public data.

Evidence added:

- `data/paid_access_recheck_20260618.md`
- `data/paid_access_recheck_20260618.json`

Result:

- Available public-data modules: AkShare 1.18.41 and Baostock 00.8.90.
- Unavailable modules: Tushare, WindPy, iFinDPy, Choice, JQData, RQData, Datayes, xbbg, blpapi, Eikon and Refinitiv.
- Environment variable scan found no market-data or paid customs/BOL keys.
- Home-directory config search found no market-data or customs/BOL credential files; matches were false positives such as WindowManager, tailwind, unwind or theme files.

Completion impact:

- Confirms current local environment still cannot close terminal-grade flow, beneficial-owner data, paid supply-chain/customer revenue splits or paid BOL/customer datasets.

## 2026-06-18 PDF Path Leakage Check

A reader-facing PDF text hygiene check was run against `main_current_text.txt` after multiple evidence and audit refresh passes.

Evidence added:

- `data/pdf_path_leakage_check_20260618.md`
- `data/pdf_path_leakage_check_20260618.json`

Scan patterns included `workspace/`, `/Users`, `sections/`, `sources/`, `data/`, `main.tex`, file extensions such as `.tex` / `.md` / `.json` / `.pdf`, `raw_`, `rendered/`, `AStock Research Agent`, `Files Produced` and `Workflow files`.

Result:

- Matches: 0

Treatment:

- This improves reader-facing publishability hygiene.
- It does not prove layout quality, source completeness, non-public data availability or substantive requirement completion.

## 2026-06-18 Current Final-State Addendum

This addendum supersedes earlier review-log snapshots that mention 32-page, 55-page or 70-page intermediate PDFs. Those entries are retained as historical audit trail, but the current report state is the 71-page PDF rebuilt at `Thu Jun 18 09:13:57 2026 CST`.

Current report state:

- `main.pdf` has 71 pages, A4, file size 812912 bytes.
- `main_current_text.txt` was regenerated from the current PDF.
- Reader-facing hygiene checks report zero unfinished markers and zero path-leakage matches.
- The current full render is `rendered/full-20260618-0913/`, with 71 valid PNG files and no missing pages.
- The report sections now include the customer annual-risk / Form SD / purchase-commitment evidence in Chapter 5 and Tencent Level-1 quote-depth proxy evidence in Chapter 9.

Current enhanced verifier state:

- `tools/verify_research_workspace.py` now checks data-room index row existence, root inventory sizes, top-level data inventory sizes, source inventory sizes, raw/rendered inventory sizes, all inventory mismatch fields, current full-render validity, unresolved blocker status, evidence-reference integrity, blocker/request-pack consistency, request-pack CSV/JSON mirroring, handoff registry/template required terms, ticker coverage matrix alignment, blocker evidence coverage, source-exhaustion consistency, audit Markdown summaries, consistency Markdown summaries, customer recheck Markdown summaries, PDF hygiene/path leakage, core checksum JSON/Markdown alignment, PDF page count and PDF creation date.
- Latest verifier output is recorded in `data/workspace_verification_run_20260618.txt`.

Current data-room counts:

- Explicit `Exists` rows: 263.
- Top-level data files: 354.
- Source files: 601.
- Raw data files: 358.
- Rendered files: 184.
- Evidence references checked: 423.
- Blocker evidence files checked: 64.
- JSON files checked: 541, with 14 classified raw failed-route captures.

Current completion boundary:

- The active objective is still not complete under the strict completion test.
- `unresolved_requirements.json` remains `blocked_by_unavailable_paid_or_non_public_data`.
- Remaining hard blockers are named platform/customer revenue split, terminal-grade positioning/order flow, and bottom-up customer/platform EPS model assumptions.
- The latest public-source work reduces uncollected public evidence and audit drift, but does not supply the paid/non-public or directly confirmed data required to close those blockers.
