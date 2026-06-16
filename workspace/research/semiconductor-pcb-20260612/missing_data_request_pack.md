# Missing Data Request Pack

## Purpose

This pack lists the exact non-public or paid-terminal data still needed after the public-source rebuild. Public filings, public broker PDFs, public IR PDFs, H-share filings, official interaction platforms, customer-side public web pages including Apple official supply-chain pages, public customs/BOL pages, AkShare, Baostock, Yahoo chart data, Baidu valuation data, Tencent quote data, Sina holder data, CNInfo holder data and Eastmoney public endpoints have already been used or tested. Local paid-terminal SDKs/credentials for Tushare, Wind, Choice, iFinD, JQData, RQData, Datayes, Bloomberg/Refinitiv and paid BOL providers were rechecked and are unavailable.

## Public Coverage Already Added

| Area | Current public-source coverage |
|---|---|
| Original/full reports | Core/watchlist broker PDFs, supplemental reports, global-broker fallback PDFs, CMBI sector report, additional Shengyi/Pengding PDF refresh. Missing UBS/JPM/Goldman originals remain. |
| Company official data | Annual, interim, Q3 and Q1 filings; official IR records; Shennan/Huazheng refinancing documents; Shengyi Electronics inquiry reply; Pengding/Zhen Ding official filing, IR and monthly revenue evidence. |
| Customer-chain proxies | Official segment/application data, H-share anonymized customer time series, named PCB-customer rows where disclosed, customer concentration, issuer disclosure-boundary Q&A, customer-side public source probe including Apple official supply-chain / Newsroom clean-energy page testing, customs/BOL public-page probe. Apple Newsroom confirms Avary Holding joined Apple Supplier Clean Energy Program in 2020, but not PCB product, order value, ASP, shipment, platform allocation or revenue split. |
| EPS sensitivity | Core operating-line models, Pengding operating-line proxy, watchlist NPP/EPS stress tests including Xingsen refresh, Shengyi Electronics official project-level EPS bridge, Shennan dilution/capex bridge, Huazheng project-boundary audit. |
| Valuation / market data | Tencent 2026-06-16 quote feed refreshed 12/12 price, total market cap, PE and PB; Yahoo price history; Baidu/AkShare PE/PB/PCF history; Eastmoney liquidity / margin / block trade / pledge / LHB / lock-up / shareholder-change proxies. |
| Holdings / flow | Official holders, Sina fund/circulating holders, CNInfo fund-heavy holdings, fund-style/type mapping, shareholder-count bridge, HKEX quarterly Stock Connect, Eastmoney participant/custodian bridge and 30-row Eastmoney daily fund-flow proxy. |

## 1. Named Customer / Platform Revenue Split

| Target | Required fields | Period | Preferred source | Use in report |
|---|---|---|---|---|
| 沪电股份 | Revenue by NVIDIA / Google TPU / other ASIC / switch / optical / domestic compute; AI server and HPC by customer; customer gross margin or ASP if available | 2024A, 2025A, 2026Q1, 2026E-2028E | Company IR, sell-side channel checks, Wind/Choice supply-chain database | Convert platform-chain thesis into EPS bridge |
| 胜宏科技 | Revenue by NVIDIA, Google TPU, Microsoft/Amazon ASIC, AI Data Center UBB, OAM, switch, HDI; customer concentration; project status by platform | 2024A, 2025A, 2026Q1, 2026E-2028E | Company IR, original JPM/招商/国金 deep reports, industry-chain checks | Validate high-beta thesis and customer risk |
| 深南电路 | PCB revenue by AI accelerator card, high-speed switch, optical module, server, substrate customer/type; FC-BGA/ABF/BT revenue and customer certification | 2024A, 2025A, 2026Q1, 2026E-2028E | Company IR, official presentations, Wind/Choice segment database | Build PCB + substrate dual-driver model |
| 生益科技 | M7/M8/M9/M10 revenue, ASP, gross margin, certification customers, AI server/GPU/ASIC material exposure | 2024A, 2025A, 2026Q1, 2026E-2028E | Company IR, sell-side material-chain checks, customer certification evidence | Turn CCL thesis into material-margin model |
| 华正新材 | High-speed CCL, BT, CBF-RCC revenue; domestic compute customer validation; customer/project ramp | 2024A, 2025A, 2026Q1, 2026E-2028E | Company IR, filings, sell-side updates | Validate watchlist/aggressive status |

## 2. Bottom-Up EPS Model Assumptions

| Field | Needed for | Current status |
|---|---|---|
| Customer/platform revenue by year | Revenue bridge | Not publicly disclosed |
| Product ASP / CCL value per server by generation | Revenue and margin sensitivity | Partial: CCL unit-value framework from Southwest Securities |
| Shipment / order backlog by platform | Forecast confidence | Not publicly disclosed |
| Segment gross margin by AI PCB / CCL / substrate / equipment | EPS bridge | Partial: company segment tables only at broad level |
| Depreciation schedule by capex project | Operating profit bridge | Not fully extracted/disclosed |
| Tax rate and minority interest by forecast year | Net-profit bridge | Partial in broker models |
| Share count / dilution assumptions | EPS bridge | Partial in broker models |
| Working-capital assumptions | Cash-flow bridge | Partial in broker models |

## 3. Institutional Holdings / Flow

| Dataset | Required fields | Period/frequency | Preferred source | Current public-source status |
|---|---|---|---|---|
| Northbound holding by ticker | Shares, market cap, % of A-shares, daily change and beneficial-owner identity | Daily or latest terminal-supported frequency, last 12 months | Wind/Choice/Eastmoney terminal | HKEX quarterly aggregate and Eastmoney participant/custodian bridge covered; daily post-rule-change beneficial-owner data unavailable publicly |
| Fund holdings by ticker | Fund name, shares, market value, % NAV, official active/passive tag | Quarterly, 2024Q4-2026Q1 and latest available | Wind/Choice/Fund filings database | Sina/CNInfo fund proxies and rule-based style covered; official active/passive classification still missing |
| QFII/social-security/insurance/broker holdings | Institution name, shares, value, period change, full category coverage | Quarterly | Wind/Choice | Public important-institution endpoint covers only core/Pengding partial rows; original watchlist single-stock rows unavailable |
| Main fund flow | Terminal-grade main/super-large/large/medium/small net flow, ideally tick-level or realtime with methodology | Daily/intraday, last 3-12 months | Eastmoney terminal/Wind/Choice | Public Eastmoney dayline proxy now covers all core/watchlist names for 30 rows, but it is not terminal-grade realtime order flow |
| Institutional ownership history | Holder category, shares, market cap, change, beneficial-owner mapping | Quarterly, multi-year | Wind/Choice | Public endpoints provide partial category rows, fund-heavy holdings and shareholder-count proxies only |

## 4. Source Documents Needed

| Document type | Target | Why needed |
|---|---|---|
| Original JPM Shenghong report | 胜宏科技 | Verify H-share target, NVIDIA/Google ASIC assumptions, 2026-2028 forecast basis |
| Latest Goldman/Hudian report | 沪电股份 | Verify target/EPS and platform-chain assumptions |
| Latest Goldman/Shengyi or Citi/Shengyi report | 生益科技 | Verify M9/M10 certification and material revenue share |
| Latest Shennan global broker report | 深南电路 | Verify AI PCB and substrate customer-chain bridge beyond existing CMBI/国海/official evidence |
| Current Huazheng 2026 deep report with full model | 华正新材 | Improve beyond existing Zheshang 2025E-2027E model and official high-grade CCL project-boundary file |
| Full customs/BOL dataset | Core platform chains | Public BOL pages are insufficient and local paid BOL credentials are unavailable; need complete shipper/consignee/product/quantity/value/date fields to test shipment-based customer mapping |

## 5. Completion Criteria Once Data Is Obtained

The active goal can be marked complete only when these are true:

1. Customer/platform revenue split is available from attributable source documents, or direct company/customer/supplier confirmation explicitly states it is unavailable at the required granularity.
2. EPS model includes segment/customer revenue, margin, capex/depreciation, tax, share count and working-capital assumptions for core names by platform/customer bucket.
3. Holding/flow data covers northbound beneficial owners, funds with official active/passive labels and category institutions for all core names at current or latest terminal-supported periods.
4. Report PDF is rebuilt and review log maps every requirement to evidence.
