# Claim Audit

## High-Impact Claims

| Claim | Evidence | Classification | Use in report |
|---|---|---|---|
| AI server platform upgrades increase PCB value through higher layers, lower-loss material, denser interconnect and more backplane/substrate-like content. | S01, S03, S06, S07 | broker-stated, cross-source | Core thesis, with valuation-crowding caveat. |
| M7/M8/M9/M10 migration turns CCL into a performance bottleneck and raises CCL unit value. | S03, S08, S11 | broker-stated | Core segment thesis for CCL leaders. |
| Global AI/HPC PCB market may grow from about USD 6bn in 2024 to USD 15bn in 2029. | S07 article cites Sullivan data | broker-stated, not independently verified | Use as directional market-size evidence, not standalone forecast. |
| Global PCB output may reach USD 94.661bn by 2029; AI/HPC server PCB market may reach USD 3.17bn by 2028 excluding substrate. | S03 | broker-stated | Use in technology/value-pool discussion with source label. |
| Shenghong's 2025-2028 net-profit CAGR may reach 81%. | S07 | broker-stated | Use as sell-side expectation, not house forecast. |
| Shennan 2025 revenue CNY 23.647bn and net profit CNY 3.276bn; 2026Q1 revenue CNY 6.596bn and net profit CNY 850mn. | S05 | broker-stated with reported-data nature | Use in financial delivery table, flagged as sourced from broker abstract. |
| Shennan 2026-2028 net-profit forecasts are CNY 5.678bn, 7.814bn, 10.625bn. | S05 | broker-stated forecast | Use for indicative PE and beat/miss framework. |
| Huazheng updated Zheshang forecast is 2025E-2027E revenue CNY 4.219bn, 7.343bn, 9.553bn; net profit CNY 300mn, 573mn, 803mn. | SUP01 | broker-stated forecast from downloaded PDF | Use as main Huazheng model; 2028E remains unavailable. |
| Hudian 12-month target price is CNY 142 based on 23x 2027E EPS. | S06 | broker-stated target | Use in broker-target table. |
| Shenghong H-share target price is HKD 600. | S07 | broker-stated target, non-comparable to A-share | Include but mark not directly comparable to A-share. |
| Earlier Huazheng public-text model implied much higher snapshot PE than report-date PE. | S11, M01, SUP01 | derived / superseded by newer PDF model | Keep only as source-freshness warning; main PE uses SUP01. |
| Pengding AI PCB thesis exists in UBS source but local body is unavailable. | S12, GBP04, GBP05 | partially verified by alternative sources | UBS original remains unavailable, but HKEX business excerpt plus Huatai/Zheshang PDFs support Pengding as watchlist/theme reserve, not core conclusion. Do not map anonymous customer codes to named platform revenue. |
| Microsoft FY24 Top 100 supplier list names several board/component suppliers. | CUST-MS01 | customer-side official supplier-list evidence | Use as relationship/source-lineage evidence only; do not infer product category, AI/cloud platform allocation, ASP, shipment, order value or revenue split. |
| OSH and upstream Apple/Dell/Samsung/AWS public lists show contributor/facility links for Tripod, Unimicron, Dongshan, Meiko, Mektec, Victory Giant and Avary/Zhen Ding-related sites. | OSH01, OSH02, CUST-UP01 | public-list relationship evidence | Can improve supply-chain relationship confidence; cannot support customer/platform revenue or EPS contribution. |
| Alphabet, Amazon and Meta official materials show elevated AI infrastructure / data-center / server / accelerated-compute capex. | CUST-CAPEX01 | demand-side official evidence | Use to support AI infrastructure demand and risk triggers; do not map to individual PCB/CCL supplier revenue. |
| Hudian and Victory Giant current issuer interaction rows confirm product/ramp/pricing progress while withholding customer details. | CNINFO-CUR01 | issuer-confirmed progress and confidentiality boundary | Use for product progress, capacity/ramp and disclosure boundary; do not use as named customer revenue. |
| Tencent 2026-06-18 quote feed refresh provides latest public price, market cap, PE and PB anchors. | M04 | public market data proxy | Use for valuation anchors with public-source quality note; not a standardized terminal valuation database and not order-flow evidence. |
| Reverse valuation matrix quantifies the NPP needed to justify current market cap at target PE bands. | VAL-REV01 | derived valuation discipline | Use as delivery-hurdle analysis only; not a customer/platform bottom-up EPS model. |

## Relationship Confidence Rules

| Relationship type | Default label |
|---|---|
| Company has business segment disclosed in archived broker abstract | broker-stated |
| Company is named in industry-chain map but no customer/project confirmation | inferred |
| Customer platform exposure such as NVIDIA / North American CSP / Google ASIC from article reproduction | broker-stated, not confirmed |
| Unavailable source body | unverified |
| Customer-side supplier-list rows without product/revenue fields | relationship evidence, not revenue evidence |
| Public quote / fund-flow / margin / Stock Connect APIs | market proxy, not terminal-grade order flow |
| Derived valuation hurdle from market cap / PE | derived scenario, not operating model |

## Rejected or Restricted Claims

| Claim | Decision |
|---|---|
| Directly comparing JPM's HKD 600 H-share target for Shenghong to A-share price | Rejected. Different listing/currency/security basis. |
| Giving new target prices for companies without sourced broker targets | Rejected. Use scenario logic only. |
| Treating the public source corpus as complete broker consensus | Rejected. Use "Publicly Available Research Sentiment". |
| Treating 2026-06-12 or 2026-06-16 quote snapshots as current after the 2026-06-18 refetch | Rejected. Use 2026-06-18 Tencent refetch / 2026-06-17 embedded timestamp snapshot for refreshed public valuation anchors. |
| Treating Tencent quote, Eastmoney fund-flow or margin data as terminal-grade order flow | Rejected. They are public proxies only. |
| Treating Microsoft / Apple / Dell / Samsung / Amazon / OSH supplier-list rows as customer revenue split | Rejected. They do not disclose product, ASP, shipment, order value, margin or revenue. |
| Treating hyperscaler capex as supplier revenue allocation | Rejected. It supports demand-side logic only. |
| Treating reverse valuation hurdle as customer/platform EPS model | Rejected. It is a top-down delivery check, not a bottom-up customer model. |
