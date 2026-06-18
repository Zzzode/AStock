# External Data Request Templates

## Purpose

These templates convert the remaining hard blockers into sendable requests for company IR, sell-side analysts, paid terminal vendors, customs/BOL providers or direct industry-chain contacts. They are not evidence by themselves.

## 1. Company IR / Supplier Confirmation Request

**Subject:** Request for public-disclosure boundary confirmation: AI PCB / CCL platform revenue split

Dear IR team,

We are updating an A-share semiconductor PCB/CCL research file and have exhausted public filings, IR records, public interaction platforms, customer-side supplier lists, current Amazon/Dell/Microsoft/Apple supplier-list routes, Open Supply Hub, upstream Apple/Dell/Samsung/AWS supplier/certification lists, customer annual-report / SEC-style risk disclosures, customer Form SD / conflict-minerals filings including NVIDIA, public customs/BOL pages and broker PDFs available to us.

Could the company confirm whether any of the following can be disclosed at company-approved granularity for 2024A, 2025A, 2026Q1 and 2026E-2028E?

- Revenue by named customer or platform, including NVIDIA, Google TPU / ASIC, Microsoft/Amazon ASIC, domestic compute, optical-module, switch/backplane and AI server/HPC chains.
- Product category tied to those chains, such as high-layer PCB, HDI, mSAP, OAM/UBB/backplane, high-speed CCL, BT or CBF materials.
- Order backlog, shipment, ASP, unit content, gross margin or certification status by platform/customer bucket.

If company policy does not allow disclosure at this level, please confirm the disclosure boundary and the highest public granularity the company can provide.

## 2. Paid Terminal / Ownership Data Request

**Subject:** Request for terminal-grade ownership, northbound and fund-flow dataset

Please provide the latest terminal-supported dataset for the 12-name semiconductor PCB report universe covering:

- Northbound holding by ticker: shares, market value, % A-shares, daily changes, participant and beneficial-owner identity where available.
- Fund holdings: fund name, shares, market value, % NAV, period, official active/passive tag.
- Institution categories: QFII, social-security, insurance, broker, pension, state-team and fund-asset-plan holdings with period-over-period change.
- Main/super-large/large/medium/small net flow with methodology, daily/intraday history for the latest 3-12 months, and terminal-grade realtime fields where available.

Please identify source database, field definitions, update frequency, disclosure-delay rules and any post-2024 Stock Connect methodology changes.

Public proxies already archived include HKEX quarterly aggregate Stock Connect, Eastmoney participant/custodian bridge, Sina/CNInfo fund proxies, rule-based fund-style mapping, shareholder-count proxies, public daily/minute Eastmoney fund-flow proxies and Tencent public Level-1 five-level quote-depth snapshot. These proxies do not provide beneficial-owner identity, official active/passive tags or terminal-grade realtime flow.

## 3. Bottom-Up Model / Broker Data Request

**Subject:** Request for operating-model assumptions by customer/platform bucket

Please provide available model assumptions for core semiconductor PCB/CCL names by 2024A, 2025A, 2026Q1 and 2026E-2028E:

- Customer/platform revenue by year.
- Product ASP, server/rack unit content, shipment, backlog and order ramp by platform.
- Segment or project gross margin, yield, depreciation schedule, capex project timing and utilization.
- Tax rate, minority interest, share count / dilution and working-capital assumptions.
- Original full PDFs or model tables for JPM/Shenghong, Goldman/Hudian, Goldman or Citi/Shengyi, global-broker Shennan and current Huazheng deep-model reports.

Please separate audited historical fields from forecast assumptions and mark any channel-check / non-public assumptions that cannot be redistributed.

Public evidence already includes operating-line broker models, EPS sensitivity, official project EPS bridges, broker forecast lines, EPS assumption matrix, reverse valuation matrix, customer annual-risk disclosures, Form SD due-diligence evidence and a customer purchase-commitment matrix. These public materials still do not provide customer/platform revenue, ASP, shipment, platform margin, depreciation or customer-specific working-capital assumptions.

## 4. Customs / BOL Dataset Request

**Subject:** Request for complete customs / bill-of-lading dataset for AI PCB customer-chain mapping

Please provide a Full customs/BOL dataset for the core platform chains and relevant PCB/CCL suppliers covering 2024A, 2025A, 2026Q1 and latest available 2026 records.

Required fields:

- Shipper, consignee and notify party.
- Product description, HS code, quantity, unit, declared value and currency.
- Shipment date, port of loading, port of discharge and country/region.
- Original bill or shipment identifier where redistribution is permitted.
- Supplier/customer normalization fields and confidence score if the dataset uses entity matching.

Public BOL pages are insufficient and local paid BOL credentials are unavailable; complete shipper/consignee/product/quantity/value/date fields are needed to test shipment-based customer mapping. Please separate raw records from vendor-normalized relationship flags and state any redistribution restrictions.

## 5. Material-Generation ASP / Margin / Certification Data Request

**Subject:** Request for M8/M9/M10 CCL material-generation ASP, margin and certification data

Please provide material-generation data for Shengyi Technology, Nanya New Material and Huazheng Materials covering 2024A, 2025A, 2026Q1 and 2026E-2028E where available.

Required fields:

- Product code and equivalent material generation, such as Synamic8GN, Synamic9GN, NY6300S, NOUYA8U, HSD7, HSD8, HSD8(K), M8, M9 and M10.
- Quarterly ASP by product or material generation.
- Revenue and shipment volume by product or material generation.
- Product gross margin or gross-margin premium versus commodity FR-4 / ordinary CCL.
- Customer certification list, certification stage and certification date by product or generation.
- Batch-supply start date, order backlog, allocation status and delivery lead time by product or generation.
- Whether the disclosed product is used in GPU server, ASIC server, switch, optical module, domestic compute, CPO or other platform buckets.

Public evidence already collected includes Shengyi Synamic8GN / Synamic9GN TDS and Line-up Dk/Df tables, Nanya NYHP specification sheets and official M6-M10 certification/ramp commentary, Huazheng HSD8 / HSD8(K) official Line-up tables, material revenue/margin proxies, implied unit-economics proxies, certification timelines and supply-tightness proxies. These public materials still do not provide product-level ASP, generation-level revenue share, generation-level gross margin, complete customer certification list or product-level delivery lead time.

## Boundary

Sending these requests or receiving public proxy data does not close the active blockers. The blockers close only when attributable source documents, paid datasets, or direct company/customer/supplier confirmations satisfy the completion tests in `missing_data_request_pack.json`.
