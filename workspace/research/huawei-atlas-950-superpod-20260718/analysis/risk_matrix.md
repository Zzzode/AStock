# Atlas 950 SuperPoD Institutional Risk Matrix

**Risk date:** 2026-07-18

**Evidence cutoff:** 2026-07-18

**Overall risk:** **High; L4 thesis risk for Atlas-specific supplier attribution, L3-L4 market risk for the valuation basket**

**Risk conclusion:** The 1,024-card physical display materially reduces product-existence risk, but it does not close the 8,192-card scale, 950DT/HBM production, customer acceptance, supplier allocation, effective-utilization, or earnings-conversion gaps. The correct control is to keep Atlas-specific revenue, profit and EPS at CNY 0 until the full evidence chain is public.

This file evaluates the Atlas 950 theme and the evidence-gated valuation pool. It is not a legal opinion or a portfolio-size recommendation. The user's mandate, risk budget, liquidity needs and current positions are not available, so security-level position sizing and stop-loss levels cannot be responsibly prescribed.

## 1. Risk scale and evidence boundary

- **L4 / thesis-threatening:** can invalidate the theme-to-earnings bridge, trigger exclusion/compliance review, or cause a greater than 25% thematic drawdown.
- **L3 / material:** can reduce EPS, margin, cash conversion or the applicable multiple enough to cause a 10%-25% drawdown.
- **L2 / monitor:** manageable in the base case but capable of compounding with another risk.
- **Probability:** point estimates are risk-budgeting judgments, not statistical forecasts. Low is below 25%, medium is 25%-50%, and high is above 50% over the next 12-18 months unless otherwise stated.

The official record establishes the following facts and limits:

1. Huawei's 2025 roadmap described an Ascend 950DT-based Atlas 950 with a maximum design configuration of 8,192 cards and planned 2026Q4 commercial availability.
2. Huawei's 2026-07-17 release showed a physical 1,024-card system. It did not identify a customer, accepted deployment, system price, site, sustained utilization or 8,192-card build.
3. The 1,024-card system's **256 TB global unified memory-addressing space** equals 256 GB per card by simple division, while the earlier 950DT roadmap disclosed 144 GB HiZQ 2.0 per chip. The 256 TB figure therefore cannot be treated as HBM capacity without a disclosed memory hierarchy.
4. Huawei has not disclosed the HBM wafer source, base die, foundry, advanced-package provider, production yield, volume status, Atlas 950 supplier BOM, allocation, ASP, order, backlog or customer acceptance.
5. The growth and valuation models assign **CNY 0 Atlas-specific 2026E revenue, profit and EPS** to every covered company. Consequently, a roadmap slip does not reduce modeled Atlas EPS; it removes catalyst/multiple optionality and can still cause substantial price damage.

## 2. 22-factor risk matrix

| Category | # | Factor and evidence boundary | Severity | Probability | Most affected | Early indicators | Mitigation / monitoring | Thesis invalidation trigger | Valuation consequence |
|---|---:|---|---|---:|---|---|---|---|---|
| A. Geopolitical / compliance | A1 | Huawei Entity List and Huawei Foreign Direct Product Rule exposure remains active; transactions involving items subject to the Export Administration Regulations can require a license and face a presumption of denial | L4 | 65% | 950DT, HiZQ/HBM, package/test, imported tools/IP; direct Huawei ecosystem names | Export Administration Regulations revisions, license denials, supplier notices, enforcement cases, third-country guidance | No valuation credit for a supply path that depends on unverified controlled inputs; review every named supplier against the live regulations and mandate | A new rule blocks a critical manufacturing/test input without a qualified substitute, delaying volume availability by more than one quarter | 0% direct Atlas EPS change in the current model, but 20%-35% theme multiple compression; affected names migrate toward bear value |
| A. Geopolitical / compliance | A2 | High-bandwidth memory and semiconductor-manufacturing controls can constrain die, equipment, packaging and yield even if domestic demand rises | L4 | 55% | Huawei/HiSilicon, memory/package chain, probe/test optionality | HiZQ volume disclosure, packaging throughput, yield, tool service restrictions, inventory prebuild, specification downgrade | Require volume-production and yield evidence; do not infer HBM suppliers from capability or investor questions | No production-grade HBM source or package yield sufficient for planned Q4 2026 volume | 15%-30% de-rating for HBM/test/package rumors; supplier optionality remains CNY 0 |
| A. Geopolitical / compliance | A3 | Power, grid connection, energy-efficiency review, renewable sourcing and water/heat-rejection permits can delay customer sites | L3 | 45% | Power, liquid cooling, IDC, operators and project integrators | Approved megawatts, PUE threshold, grid-connection date, commissioning and acceptance schedule | Track site-level approval and accepted capacity, not announced project size | Named orders exist but site energization or acceptance slips by more than six months | 5%-15% EPS timing haircut for project names plus 10%-20% multiple compression |
| A. Geopolitical / compliance | A4 | Broader technology decoupling, retaliation or cross-border procurement restrictions can raise costs and narrow markets | L4 | 30% | Optical, PCB/CCL, connector, equipment and globally exposed suppliers | New restricted-party lists, customs disruption, country-of-origin requirements, customer redesigns | Diversified customer and sourcing base; mandate-level restricted-list screening | A core supplier loses a material customer or critical input because of a new control | Company-specific 10%-30% earnings/multiple downside; higher for concentrated exposures |
| B. Competitive | B1 | NVIDIA/AMD and other systems may retain superior effective workload performance, developer productivity or time-to-solution despite Huawei's peak-spec comparison | L3 | 55% | Atlas demand, iFlytek validation, cloud/operator adoption | Independent training/inference results, porting time, uptime, total cost per token, developer activity | Compare normalized workload, precision, sparsity, system boundary and availability; do not compare vendor peak figures directly | Independent production workloads show a persistent cost/performance or reliability gap that prevents planned adoption | 15%-30% multiple compression for platform-dependent names; no current Atlas EPS write-down |
| B. Competitive | B2 | Alternative domestic architectures can win operator budgets or force lower pricing | L3 | 40% | System integration, cooling/power, Ascend ecosystem partners | Operator tender share, benchmark disclosures, system ASP and discounting | Track accepted procurement by architecture and vendor; avoid single-platform assumptions | Atlas loses repeated named tenders or must discount enough to impair ecosystem economics | 10%-20% theme de-rating; lower supplier share and margin assumptions |
| B. Competitive | B3 | Huawei may internalize high-value subsystems or multi-source components, limiting A-share supplier share and pricing power | L3 | 60% | Optical, power, cooling, PCB/CCL, connector and ODM rumors | Supplier qualification lists, dual sourcing, internal Huawei product announcements, allocation changes | Require product-level qualification, allocation and ASP; no exclusivity credit without primary evidence | Official BOM shows internal supply or immaterial covered-company allocation | Rumor-only names can lose 20%-40%; evidence-gated EPS stays unchanged |
| C. Execution | C1 | Roadmap-to-delivery risk: planned 2026Q4 commercial availability may slip or remain a showcase | L4 | 45% | Entire chain, especially high-multiple theme names | 950DT availability, named site, signed acceptance, shipment count, recognized revenue | Use delivery/acceptance milestones; do not use launch-event dates as revenue dates | No named commercially accepted Atlas 950 deployment by 2026-12-31, or formal delay beyond 2027Q1 | Catalyst premium reverses; 15%-30% theme drawdown toward bear values |
| C. Execution | C2 | 1,024-to-8,192 scale-up risk: eightfold card count and a 160-cabinet design create new optical, fault-domain, synchronization and operations complexity | L4 | 55% | UnifiedBus, optics, system integration, cooling/power and customer operations | Physically identified 8,192-card build, burn-in duration, failure domains, collective-communication scaling, sustained availability | Separate 1,024 validation from 8,192 acceptance; require system-level evidence at each scale | No stable 8,192-card customer system by 2027H1 or scaling efficiency/availability is commercially inadequate | Removes the full-scale architecture premium; 20%-35% multiple downside for high-purity expectations |
| C. Execution | C3 | Memory-definition risk: 256 TB global address space is not reconciled with 144 GB HiZQ 2.0 per 950DT | L3 | 65% | HBM, memory, storage and performance claims | Memory hierarchy, silicon configuration, local-versus-pooled capacity, bandwidth and latency disclosure | Label 256 TB only as global addressing space; prohibit per-card HBM inference | Huawei discloses that material capacity is slower pooled/host/storage memory and workloads cannot use it as assumed | HBM-content rumors de-rate 15%-30%; system performance assumptions require revision |
| C. Execution | C4 | Accelerator, HBM stack, base die and advanced-package yield may prevent economical volume | L4 | 50% | Huawei system ramp, memory/test/package chain and all dependent BOM nodes | Good-die output, package yield, rework, thermal excursions, binning, volume shipment | Require volume and yield evidence; use accepted systems rather than wafer/capacity announcements | Repeated silicon stepping, material specification reduction or Q4 volume miss linked to yield | 20%-40% theme de-rating; any future unit model must cut volume and raise cost |
| C. Execution | C5 | UnifiedBus reliability and software utilization may not translate peak FLOPS into productive training/inference | L4 | 50% | Atlas adoption, iFlytek, Huawei Cloud/operator economics | Sustained model utilization, job completion rate, mean time between interruption, porting time, framework/operator coverage | Track customer workloads and total cost per completed job/token; demand third-party or customer evidence | Independent production workloads show poor scaling, low utilization or recurring fabric/software instability | 15%-35% multiple compression; downstream commercialization assumptions cut |
| C. Execution | C6 | Supplier identity, qualification and order allocation are undisclosed for every upstream covered A-share name | L4 | 80% | HGTECH, Envicool, Shenling, Aerospace Electrical, PCB/CCL, power and cable satellites | Exchange filings, tenders, qualification, named products, orders/backlog, customer allocation, ASP | Atlas-specific EPS remains CNY 0; exclude exclusivity/share claims until primary confirmation | Report or valuation assigns Atlas EPS or target-price uplift without product + qualification/order + economics | Publication blocker and valuation reset; rumor-only premium can fall 20%-40% |
| C. Execution | C7 | Liquid-cooling, power and optical BOM quantity/value are unknown; UBoE may use fewer switches/modules than a RoCE extrapolation | L3 | 70% | Thermal, power, optics, connector and IDC candidates | kW/cabinet, CDU topology, optical ports/form factor, OCS/switch topology, MW/site, supplier share | Model only disclosed broader AIDC segments; do not multiply 160 cabinets by generic BOMs | Tender/manual shows materially lower external content, internal Huawei supply or lower attach rates | 10%-30% thematic multiple downside; top-down BOM models invalid |
| C. Execution | C8 | Customer capex, procurement, acceptance and utilization are not disclosed; predecessor 384-card deployments do not prove 950 demand | L4 | Entire value chain, cloud/operators, project suppliers | Named customers, accepted count, utilization, renewal/expansion, payment and revenue recognition | Require customer/site/count/acceptance evidence; distinguish capex plan from commissioned capacity | No repeat customer deployment after the initial physical system, or accepted capacity remains underutilized | 15%-35% de-rating and project EPS timing cuts |
| D. Financial | D1 | Project delivery can consume working capital through inventory, receivables, contract assets and delayed acceptance | L3 | Digital China, Talkweb, Shenling, Kehua, integrators and thermal/power names | Receivable and inventory days, contract assets, operating cash flow/net profit, acceptance slippage | Require cash conversion alongside order growth; cap valuation credit when backlog lacks payment terms | Two reporting periods of revenue/order growth with worsening cash conversion and receivable days | 5%-15% EPS haircut plus 10%-20% multiple compression |
| D. Financial | D2 | Mix, qualification cost, yield ramp, raw materials and customer bargaining can dilute margins | L3 | HGTECH's 13.26% connection margin, Envicool, Shenling, PCB/CCL and connectors | Segment gross margin, scrap/yield, warranty, expedite cost, copper/fiberglass/optical input prices | Monitor segment rather than consolidated margin; require stable margin before multiple expansion | Revenue accelerates but segment gross margin falls more than 300 basis points without a transient explanation | 10% EPS miss plus 20% multiple compression implies approximately 28% fair-value downside |
| D. Financial | D3 | Customer concentration can make growth and collections dependent on one platform; Huawei was 41.51% of Talkweb's 2025 sales | L4 | Talkweb directly; Shenling and other relationship names where allocation is undisclosed | Top-customer share, payment terms, receivable concentration, renewal, related guarantees | Keep Talkweb watchlist-only; require diversification and recurring profitability | Top-customer reduction, delayed payment or procurement change causes a material revenue/profit shortfall | 20%-40% company-specific downside; no Atlas multiple until recurring earnings improve |
| D. Financial | D4 | Broker estimates and target multiples may be optimistic; Atlas units/ASP/margin and a DCF are unavailable | L3 | All twelve modeled names | Estimate revisions, H1/Q2 delivery, margin and cash conversion; target-price coverage | Use only auditable original-PDF forecasts, bear/base/bull ranges and CNY 0 Atlas EPS | Two consecutive estimate cuts or failure of next-quarter operating thresholds | Move to bear EPS/multiple; basket fair-value downside can exceed 25% |
| E. Market | E1 | Valuation crowding leaves little room for execution error; many evidence-gated targets are already below market | L4 | Shengyi, Envicool, iFlytek, Shenling, PCB/CCL and connector expectations | Turnover, crowding, price/earnings divergence, estimate revision breadth, event-day reversal | Avoid chasing; stage exposure only after earnings/acceptance evidence; use bear value as risk reference | Event excitement expands multiples without improved order/EPS evidence | Current-to-bear downside ranges from 10.0% to 60.8% across the modeled pool |
| E. Market | E2 | Rumor and supplier-over-attribution risk is high; exclusive optical, connector, HBM/test and ODM claims are unsupported or denied | L4 | HGTECH, Envicool, Aerospace Electrical, Qiangyi and excluded Sichuan Changhong mapping | Exchange questions, official clarification/denial, unusual turnover, source provenance | Treat questions as questions; evidence score below primary confirmation blocks valuation | Company denial, no mention in subsequent filing, or official BOM contradicts the claim | 20%-40% event reversal; zero evidence-gated EPS impact but severe mark-to-market loss |
| F. ESG / HRF | F1 | Advanced AI, surveillance, dual-use and restricted-entity exposure can breach mandate, financing, vendor or customer red lines regardless of upside | L4 | Huawei ecosystem; iFlytek and dual-use/defence-adjacent names require mandate review | Restricted-list changes, human-rights findings, data-security enforcement, customer/end-use disclosures | Pre-trade restricted-list, end-use and human-rights review; escalate rather than waive for valuation upside | Confirmed mandate prohibition, forced-labour link, prohibited end use or material compliance breach | Exclusion; target price and expected return become irrelevant for the affected mandate |

## 3. Compliance and ESG/HRF screen

### 3.1 Dated BIS record

| Date | Entity / rule | Amount | Current status at 2026-07-18 | Risk use |
|---|---|---:|---|---|
| 2019-05-16 effective; final rule published 2019-05-21 | Huawei Technologies Co., Ltd. and 68 non-U.S. affiliates added by the United States Department of Commerce, Bureau of Industry and Security | Not applicable; regulatory listing, not a monetary penalty | Huawei Technologies Co., Ltd. and multiple affiliates remain on the current Entity List; the live entry applies a license requirement to all items subject to the Export Administration Regulations and a presumption of denial | Direct compliance constraint; never treat domestic-substitution upside as eliminating supply and enforcement risk |
| 2019-10-09 | IFLYTEK entry added by the United States Department of Commerce, Bureau of Industry and Security under 84 Federal Register 54002 | Not applicable; regulatory listing, not a monetary penalty | Current report corpus and live Bureau of Industry and Security materials continue to identify IFLYTEK as an Entity List company; mandate/legal confirmation is required before investment | Security-level mandate review and heightened human-rights/data-use diligence |
| 2024-12-02 | United States Department of Commerce, Bureau of Industry and Security package controlling high-bandwidth memory, 24 semiconductor-equipment types and 3 software-tool types; 140 Entity List additions and 14 modifications | Not applicable; rulemaking, not a monetary penalty | Controls are in force; certain high-bandwidth memory can use License Exception HBM only if all conditions are met | Direct HBM/equipment/yield risk for the Atlas ramp |
| 2026-01-13 | United States Department of Commerce, Bureau of Industry and Security revised review policy for NVIDIA H200, AMD MI325X and similar China exports | Not applicable; rulemaking, not a monetary penalty | Case-by-case review subject to purchaser compliance, capacity and independent-testing conditions; it does not remove Huawei-specific Entity List restrictions | Competitive supply may improve for approved Chinese customers while Huawei remains constrained; net effect can be negative for Atlas relative demand |
| 2026-06-17 | Robert Bosch GmbH settlement concerning unlicensed shipments to Huawei Technologies Co., Ltd. or listed affiliates from 2020-09-16 through 2024-09-26 | Approximately United States dollar 72,369,361 of shipments; Bureau of Industry and Security penalty United States dollar 36,184,680; approximately United States dollar 3.6 million separately paid under a Department of Justice disgorgement arrangement and credited as described by the agency | Settlement announced; enforcement action demonstrates continuing Foreign Direct Product Rule exposure and penalty risk | Concrete enforcement precedent; supplier diligence must cover foreign-produced items subject to the Export Administration Regulations |

Official links: [Huawei Entity List rule](https://www.bis.gov/84-fr-22961-addition-entities-entity-list), [current Export Administration Regulations Part 744](https://www.bis.gov/regulations/ear/744), [2019 IFLYTEK Entity List rule](https://www.govinfo.gov/app/details/FR-2019-10-09/2019-22210), [2024 high-bandwidth memory controls](https://www.bis.gov/press-release/commerce-strengthens-export-controls-restrict-chinas-capability-produce-advanced-semiconductors-military), [2026 semiconductor review policy](https://www.bis.gov/press-release/department-commerce-revises-license-review-policy-semiconductors-exported-china), and [2026 Bosch enforcement settlement](https://www.bis.gov/press-release/robert-bosch-gmbh-bosch-pay-36-million-penalty-bis-violations-pertaining-shipments-huawei).

### 3.2 Preliminary 30-point issuer screen

This is an **exposure triage, not a completed ESG audit**. Higher is worse. Export/restricted-party exposure, human-rights/dual-use/data-ethics sensitivity, and evidence/disclosure weakness are each scored 0-10. The current case corpus is adequate for risk routing but not for a final exclusion decision on every issuer.

| Ticker | Company | Export / restricted party | HRF / dual use / data ethics | Disclosure gap | Total / 30 | Status |
|---|---|---:|---:|---:|---:|---|
| 000034 | Digital China | 5 | 2 | 6 | 13 | Enhanced review; broad ecosystem exposure, no Atlas order |
| 000988 | HGTECH | 3 | 1 | 7 | 11 | Monitor; Atlas exclusivity rumor blocked |
| 600183 | Shengyi Technology | 2 | 1 | 7 | 10 | Monitor; generic AI CCL exposure only |
| 002916 | Shennan Circuits | 2 | 1 | 7 | 10 | Monitor; no Atlas qualification |
| 002463 | WUS Printed Circuit | 2 | 1 | 7 | 10 | Monitor; no Atlas qualification |
| 300476 | Victory Giant Technology | 2 | 1 | 7 | 10 | Monitor; no Atlas qualification |
| 002837 | Envicool | 2 | 1 | 7 | 10 | Monitor; no named Huawei/Atlas order |
| 301018 | Shenling Environment | 4 | 1 | 6 | 11 | Enhanced review; Huawei/H-company relationship, allocation undisclosed |
| 002335 | Kehua Data | 2 | 1 | 7 | 10 | Monitor; project and acceptance exposure |
| 002130 | Woer Heat-Shrinkable Material | 2 | 1 | 7 | 10 | Monitor; generic high-speed interconnect proxy |
| 002230 | iFlytek | 10 | 9 | 5 | 24 | **Mandate review / exclusion where Entity List or HRF policy applies** |
| 002025 | Guizhou Aerospace Electrical Appliance | 4 | 6 | 7 | 17 | Enhanced dual-use review; claimed 950 relationship unconfirmed |
| 002261 | Talkweb Information | 8 | 2 | 5 | 15 | Enhanced review; Huawei was 41.51% of 2025 sales and recurring profit was negative |

### 3.3 Ten red lines

Any confirmed red line is an exclusion flag for mandates that prohibit it; no valuation upside can override the flag.

1. Issuer or controlled entity appears on a mandate-prohibited sanctions, Entity List, military end-user or investment blacklist.
2. More than 50% ownership/control by a prohibited entity where applicable rules or mandate extend restrictions.
3. Material export, re-export or in-country transfer without a required authorization.
4. Credible forced-labour involvement in the product or raw-material chain without effective remediation.
5. Verified contribution to unlawful mass surveillance or serious human-rights abuse.
6. Prohibited military, intelligence, weapons-of-mass-destruction or diversion end use.
7. Material bribery, bid-rigging or procurement fraud in public/cloud/operator projects.
8. Material data-security or privacy breach with unresolved regulatory action.
9. Severe environmental, worker-safety or coolant/chemical incident with inadequate remediation.
10. Fraudulent financial reporting, undisclosed related-party transfer, or qualified/adverse audit opinion that breaks earnings reliability.

The current corpus confirms a mandatory mandate review for iFlytek's Entity List status. It does not complete forced-labour, surveillance end-use, environmental, bribery or data-security screening for the remaining issuers; that absence is a diligence gap, not a clean bill of health.

## 4. Valuation-at-risk map

The evidence-gated targets already assign no Atlas-specific earnings. Current-to-final and current-to-bear downside therefore measure standalone business and multiple risk, not a write-off of modeled Atlas revenue.

| Ticker | Price at 2026-07-17 | Final target | Downside / upside to final | Bear target | Downside to bear | Primary risk interpretation |
|---|---:|---:|---:|---:|---:|---|
| 000034 | 24.61 | 22.92 | -6.9% | 15.75 | -36.0% | Distribution purity and working capital |
| 000988 | 117.62 | 108.56 | -7.7% | 76.06 | -35.3% | Optical margin and unsupported Atlas allocation |
| 600183 | 132.29 | 102.12 | -22.8% | 68.88 | -47.9% | Crowded premium CCL expectations |
| 002916 | 334.00 | 289.29 | -13.4% | 212.74 | -36.3% | High-layer yield/utilization and multiple |
| 002463 | 127.80 | 111.10 | -13.1% | 77.34 | -39.5% | Customer concentration and capacity utilization |
| 300476 | 241.50 | 259.53 | +7.5% | 190.86 | -21.0% | Overseas yield and mix durability |
| 002837 | 61.57 | 51.66 | -16.1% | 33.72 | -45.2% | Q1 margin trough and rumor attribution |
| 301018 | 86.96 | 75.28 | -13.4% | 50.65 | -41.8% | Order-to-cash conversion and allocation opacity |
| 002335 | 29.75 | 31.87 | +7.1% | 22.36 | -24.8% | Acceptance, receivables and recurring profit quality |
| 002130 | 15.24 | 19.74 | +29.5% | 13.71 | -10.0% | Lower-purity value satellite; qualification risk |
| 002230 | 41.12 | 34.74 | -15.5% | 25.81 | -37.2% | Loss/cash conversion, model launch and compliance |
| 002025 | 64.76 | 57.96 | -10.5% | 25.38 | -60.8% | Unconfirmed linkage and unusually wide forecast range |

## 5. Stress-test matrix

| Scenario | Trigger | Probability | Impact on coverage | Valuation / P&L consequence | Risk response |
|---|---|---:|---|---|---|
| Sentiment correction | Theme basket falls 10% without estimate changes | 65% | High-expectation names underperform; lower-purity value names may be relatively resilient | Direct mark-to-market -10%; does not create evidence or automatically make names attractive | Re-test against final and bear values; do not average down rumor-only exposure |
| Multiple reset | No new supplier/order evidence and thematic multiples compress 20% | 55% | Broad; most acute above 50x 2026E P/E | Approximately -20% at unchanged EPS; many names approach evidence-gated bear ranges | Reduce catalyst-dependent exposure; require proof before re-risking |
| Earnings plus multiple shock | 2026E EPS misses 10% and multiple compresses 20% | 45% | Margin/cash-conversion-sensitive thermal, optical, PCB and project names | Approximately -28% fair value, consistent with the growth sensitivity artifact | Move valuation to bear case; block multiple expansion |
| Delivery / scale failure | Atlas commercial availability slips beyond 2027Q1 or no stable 8,192-card deployment by 2027H1 | 35% | Entire Atlas sleeve; supplier rumors hit first | Atlas EPS remains CNY 0 in the model, but theme prices can fall 20%-35% | Keep only standalone-earnings positions that remain attractive at bear value |
| Supplier-disconfirmation | Tender, filing or official BOM contradicts an exclusive/large-share rumor | 50% for at least one circulated claim | HGTECH, Envicool, Aerospace Electrical, Qiangyi and other mapped satellites | Rumor-only name -20% to -40%; evidence-gated EPS unchanged | Immediate thesis review; do not substitute a different unverified supplier story |
| Yield and customer-acceptance shock | 950DT/HiZQ/package yield delays systems while customer sites or workloads fail acceptance | 30% | Compute, memory/test/package, integration, cooling/power and downstream adoption | Combined volume, cost and multiple shock of 25%-40% | Require accepted units, stable workload and payment evidence before restoring credit |
| **Black swan: export-control and enforcement escalation** | New Foreign Direct Product Rule/end-use scope or coordinated allied controls block a critical HBM, equipment, test or software input; a material supplier/customer is newly restricted | 15% | Entire ecosystem; especially direct Huawei and controlled-input exposure | 30%-50% thematic drawdown; exclusion for affected mandates can override price | Pre-trade restricted-list review, avoid concentrated single-platform exposure, maintain liquidity and use portfolio-level index/factor hedges where mandate permits |

## 6. Monitoring dashboard and escalation thresholds

| Date / window | Required evidence | Green | Amber | Red / stance change |
|---|---|---|---|---|
| 2026Q3-Q4 | 950DT and Atlas 950 commercial availability | Named customer, accepted system count and production workload | Product available but customer/acceptance undisclosed | Formal slip beyond 2027Q1 or showcase-only evidence |
| By 2026-12-31 | Roadmap conversion | Repeatable commercial deployment and payment/revenue evidence | Pilot deployment without economics | No named accepted deployment |
| By 2027H1 | 1,024-to-8,192 scale | Physically identified 8,192-card customer system with sustained workload/availability evidence | Intermediate scale only or vendor-only performance | No stable 8,192 build, major reliability/efficiency gap |
| Next technical disclosure | 256 TB and HiZQ definition | Memory hierarchy reconciles 144 GB local HBM with global addressing and usable bandwidth | Partial hierarchy disclosure | 256 TB was used as an HBM-content claim without technical support |
| Next two reporting periods | Supplier economics | Named qualification/order, allocation, ASP, revenue, margin and cash conversion | Order/capability only | Denial, no filing evidence, worsening margin/cash conversion |
| October 2026 and after | iFlytek validation | On-time model, disclosed performance/cost and commercial use | Launch with vendor-only metrics | Delay, poor cost/performance or no monetization evidence |

## 7. What would make this risk assessment wrong

The high-risk assessment would be too conservative if all of the following occur: (1) Huawei ships and customers accept material Atlas 950 volume on the planned timetable; (2) a physically identified 8,192-card system demonstrates sustained production availability and workload scaling; (3) the 256 TB hierarchy is reconciled and HiZQ 2.0 production/yield is sufficient; (4) independent or customer evidence validates UnifiedBus utilization and total cost; (5) covered suppliers disclose product-level qualification, allocation, ASP, orders, margin and cash conversion; and (6) these earnings arrive without material multiple expansion or compliance breach.

Conversely, the risk assessment is confirmed if the evidence remains at the physical-showcase/capability level while prices continue to capitalize exclusivity, full-scale deployment or Atlas-specific earnings.

## 8. Source and artifact map

- Huawei roadmap and architecture: `sources/official-huawei-20260718/huawei_2025-09-18_xu_keynote_evidence.md`.
- March 2026 launch boundary: `sources/official-huawei-20260718/huawei_2026-03-02_mwc_atlas950_evidence.md`.
- July 2026 physical 1,024-card evidence and 256 TB reconciliation gap: `sources/official-huawei-20260718/huawei_2026-07-17_waic_physical_system_evidence.md`.
- Full chain and policy evidence: `analysis/industry_landscape.md`, `analysis/full_chain_taxonomy.md`, `analysis/supply_chain_model.md`, `analysis/value_chain_economics.md`, `analysis/coverage_gap_matrix.md`, and `sources/official-huawei-20260718/official_competitor_policy_source_index.md`.
- Supplier/customer evidence: `analysis/company_fundamental_cards.md`, `data/customer_chain_audit.md`, and `data/supply_chain_relationships.md`.
- Earnings and valuation: `analysis/growth_earnings_model.md`, `analysis/implied_growth_sensitivity.md`, `analysis/valuation_model.md`, `analysis/valuation_audit.md`, `data/verified_financials.md`, and `data/consensus_analysis.md`.
