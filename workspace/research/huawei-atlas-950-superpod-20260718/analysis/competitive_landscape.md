# Competitive Landscape: Atlas 950 and the AIDC Full Chain

**Evidence cutoff:** 2026-07-18  
**Conclusion:** Huawei's competitive differentiation is a sovereign, multi-cabinet scale-up system based on Ascend, UnifiedBus and unified addressing; its moat will be durable only if the 1,024-card physical proof extends to an accepted 8,192-card system with repeatable software utilization, HBM supply and an open partner ecosystem.

## 1. Evidence and leadership standard

This file distinguishes four types of evidence:

- **Official product evidence:** proves that a company offers a stated product or participates in a named ecosystem.
- **Official filing evidence:** proves a disclosed end-market, customer relationship or financial exposure within the filing's wording.
- **Vendor leadership claim:** a company's statement that its own product is “leading” or “largest”; useful for positioning, not a neutral market-share conclusion.
- **Independent market-share evidence:** required for market share, CR3 or CR5. No consistently defined current concentration dataset was found in the checked primary-source set for the eight coverage-pack blocks.

Accordingly, the tables use “reference participants” where product evidence exists but independent leader ranking does not. **CR3 and CR5 are recorded as `not disclosed`, not estimated.**

## 2. Compute-system comparison

| Attribute | Huawei Atlas 950 | NVIDIA GB300 NVL72 | AMD Helios / UALink |
|---|---|---|---|
| Vendor-defined product boundary | Multi-cabinet SuperPoD intended to operate as one logical computer | One liquid-cooled rack-scale NVLink domain | Open Rack Wide reference design for OEM/ODM implementations |
| Accelerator count | 1,024 cards physically shown; up to 8,192 in maximum design | 72 Blackwell Ultra GPUs | 72 MI455X GPUs |
| Status at cutoff | 1,024-card hardware publicly shown 2026-07-17; 8,192 design planned for Q4 2026 | Product page states “available now” | Reference design shared with partners; volume deployment expected in 2H 2026 |
| FP8 | 1 EFLOPS physical 1,024-card system; 8 EFLOPS maximum design | 720 PFLOPS FP8/FP6, with sparsity per NVIDIA footnote | 1.4 EFLOPS, based on AMD internal analysis |
| FP4 | 2 EFLOPS physical; 16 EFLOPS maximum design | 1,440 PFLOPS sparse / 1,080 PFLOPS without sparsity | 2.9 EFLOPS, based on AMD internal analysis |
| Memory | 256 TB global unified address space in physical system; 144 GB HiZQ 2.0 HBM per 950DT in roadmap; 1,152 TB stated for full design | 20 TB GPU memory and 37 TB fast memory in rack | 31 TB HBM4 in rack; up to 432 GB per MI455X |
| Scale-up bandwidth | TB-class per NPU in July release; approximately 16 PB/s aggregate maximum-design claim | 130 TB/s NVLink aggregate | 260 TB/s aggregate scale-up |
| Fabric | UnifiedBus 2.0 and all-optical UB-Mesh across cabinets | NVLink/NVSwitch within rack; InfiniBand or Spectrum-X Ethernet scale-out | UALink over Ethernet within rack; UEC/Pensando Ethernet scale-out |
| Software | CANN, Mind ecosystem and Huawei's open-source/open-interface strategy | CUDA, NCCL, TensorRT, Dynamo, Mission Control and broad OEM ecosystem | ROCm and open framework support |
| Source / quality | Huawei official Sep-2025, Mar-2026 and Jul-2026 [H1][H3][H4]; roadmap and vendor performance claims | NVIDIA official product page [C1]; official specs with sparsity footnote | AMD official page [C2]; explicitly a reference design and internal estimates |

### Comparability judgment

Raw accelerator count is not a normalized performance metric. The products have different scale-up boundaries, precision/sparsity conventions, software stacks, availability status and power envelopes. Huawei's September comparison with NVIDIA NVL144/NVL576 is a vendor comparison against a peer roadmap, not an independent benchmark [H1]. A publishable cross-platform conclusion requires the same model, precision, batch/context, network boundary, power budget, availability target and software version.

NVIDIA's current 2026 production-ramp disclosure describes Vera Rubin as a five-rack POD built around Vera Rubin NVL72 systems, with production shipments planned from fall 2026 [C21]. That is not the same naming or system boundary as the NVL144 roadmap used in Huawei's September 2025 comparison. The report should therefore compare currently disclosed architectures separately and should not carry forward Huawei's 56.8-times card-count or 6.7-times compute claim as a current, independent competitive result.

## 3. Interconnect competition and moat durability

| Architecture | Strategic model | Current evidence | Moat | Moat durability | Failure or substitution scenario |
|---|---|---|---|---|---|
| Huawei UnifiedBus 2.0 | Extend scale-up from server/rack to multi-cabinet logical machine; pool compute, memory and storage; all-optical cabinet links | UB 1.0 deployed in Atlas 900 A3; UB 2.0 specification opened; 1,024-card Atlas 950 hardware shown; 8,192 remains design maximum [H1][H2][H4] | Co-design across Ascend, CANN, networking, optics and system architecture; sovereignty value in China | Medium-high in China if 8,192-card reliability and partner adoption are validated; medium-low globally until independent ecosystem proof | CANN utilization or porting lags; HBM/yield constrains supply; optical reliability at scale misses targets; partners do not adopt UB; scale-out Ethernet provides better economics |
| NVIDIA NVLink/NVSwitch | Dense rack-scale GPU domain integrated with CUDA and NVIDIA networking, then POD/InfiniBand/Ethernet scale-out | GB300 NVL72 available; May-2026 Vera Rubin five-rack POD production ramp; broad OEM, storage and networking ecosystem [C1][C5][C21] | CUDA/software compatibility, installed base, full-stack networking, production OEM and cloud references | High globally; constrained in China by export controls and sovereignty requirements | UALink/UEC or proprietary cloud ASICs reduce lock-in; power and economics limit adoption; export controls fragment the market |
| AMD UALink/UEC Helios | Open scale-up and scale-out standards with partner-built racks | Helios 72-GPU reference design; volume deployment expected 2H26 [C2] | Openness, OEM choice, ROCm, HBM capacity and avoidance of a single proprietary scale-up fabric | Medium and rising, but dependent on partner execution, software maturity and interoperability | Delayed volume production; ecosystem fragmentation; insufficient collective/software performance versus NVLink |
| OCS and CPO evolution | Replace or complement electrical packet switching and pluggable optics to reduce power/latency | Coherent ships OCS-related products; NVIDIA CPO platforms and ecosystem announced [C3][C4] | Optical device/process IP and system co-design | Medium-high as bandwidth/power rise; architecture and supplier shares can change sharply | CPO reduces pluggable-module content; OCS changes switch count; proprietary all-optical fabrics compress merchant-component opportunities |

## 4. Global and China competitive landscape by mandatory block

| Chain block | Global reference participants and evidence type | China reference participants and evidence type | CR3 | CR5 | Localization boundary | Substitution risk | Source quality |
|---|---|---|---|---|---|---|---|
| 1. Compute platform and accelerators | NVIDIA GB300 NVL72 (official available product); AMD Helios/UALink (official 2026 reference design); Google TPU and hyperscaler ASICs are architectural substitutes | Huawei Ascend/Atlas (official product and roadmap); Cambricon and Hygon (listed-company products/filings); Biren, Iluvatar and Moore Threads (private domestic alternatives) | not disclosed | not disclosed | **Localized now:** Huawei accelerator, CANN and UB architecture. **Still opaque/import-constrained:** leading process equipment, HBM manufacturing chain, advanced packaging yield and some EDA/IP dependencies. Huawei does not disclose fabrication source or yield | Very high: CUDA/NVLink, UALink/ROCm, domestic accelerators and cloud ASICs compete across software, power and TCO | H1/H3/H4/C1/C2 are official primary; non-Huawei domestic alternatives require company-by-company filing checks before leader language |
| 2. Server, OEM, ODM and rack integration | Dell, HPE, Lenovo and Supermicro as branded system builders; Foxconn, QCT, Wiwynn, Inventec and Celestica as ODM/integration participants in official platform ecosystems | Huawei, Lenovo, IEIT/Inspur, H3C and xFusion as system participants; Huawei opens NPU modules, cards, blades and reference architecture | not disclosed | not disclosed | China has broad server/rack engineering and manufacturing capability. Atlas 950's actual OEM/ODM, compute-cabinet and interconnect-cabinet manufacturers, allocation and service model are not disclosed | Medium-high: reference designs can shift value to ODMs; proprietary Huawei integration may limit merchant opportunity; system architecture changes rapidly | H2/C2/C5/C12 official product sources; participant status does not establish market share or Atlas supplier status |
| 3. Power, UPS, transformer, busway and backup | Vertiv, Schneider Electric, Eaton and Delta have official AI/data-centre power portfolios and reference designs | Huawei Digital Power, Kehua, Kstar, Sungrow and other domestic data-centre power vendors have product capability | not disclosed | not disclosed | Most facility-level equipment is available domestically, but Atlas 950's topology, voltage, system MW, UPS/busway/transformer suppliers, certification and value per system are not disclosed | Medium: AC versus DC architectures, higher-voltage distribution, modular power shelves and grid-interactive storage can redistribute BOM and margin | C6/C7/C22/C23/C25 official vendor engineering sources; no Atlas attachment or share data |
| 4. Liquid cooling and thermal management | Vertiv, Schneider/Motivair, CoolIT, Boyd and OEM thermal stacks have liquid-cooling products and reference designs | Huawei Digital Power, Envicool, Shenling, IEIT and other domestic suppliers have cooling products/capabilities | not disclosed | not disclosed | Cold plates, manifolds, CDU and facility cooling can be localized. Huawei's floating blind-mate connector, materials/process specifications, coolant loop and qualified vendors remain undisclosed | High: cold plate versus immersion, liquid-to-liquid versus liquid-to-air, CDU topology, negative-pressure designs and OEM integration alter supplier content | H2/C7/C12/C22/C23/C24 official product evidence; F3 is official-filing relationship evidence but not Atlas evidence |
| 5. Optical, networking, switches, NICs, OCS, copper and fiber | NVIDIA/Mellanox, Broadcom, Arista, Cisco/Acacia, Coherent and Lumentum; Coherent OCS and NVIDIA photonics are official product/ecosystem evidence | Huawei; Innolight, Eoptolink and Accelink are optical participants; NVIDIA officially names Innolight and Eoptolink in its photonics ecosystem | not disclosed | not disclosed | China can supply many optical modules, fiber and switches. Atlas 950's optical-module speed/form factor, DSP/CPO/OCS choice, count, UB switch silicon and suppliers are not disclosed | Very high: UBoE versus RoCE changes switch/module count; CPO/LPO/OCS versus pluggables can shift content and margins; copper reach competes within and between racks | H1/H2/C3/C4 official; NVIDIA ecosystem evidence is not Huawei supply evidence |
| 6. HBM, DRAM/NAND, SSD and storage | SK hynix, Samsung and Micron have official HBM4 product/ramp evidence; Dell, NetApp, DDN, VAST and other storage vendors participate in AI systems | Huawei proprietary HiBL/HiZQ and OceanStor; domestic DRAM/NAND/storage companies provide adjacent capability | not disclosed | not disclosed | Huawei claims proprietary HBM designs, but wafer manufacturing, base die, packaging, yield and volume are opaque. Domestic AI storage exists; Atlas 950 storage controller, checkpoint architecture and supplier are not disclosed | High: HBM generation, custom HBM, pooled memory, CXL, SSD/HBF and disaggregated storage can change value pools | H1/H4/C8/C9/C10/C11 official; none proves Atlas HBM manufacturing source or storage attach |
| 7. PCB, CCL, substrates, connectors, cables and precision components | TTM, Unimicron, Compeq, Ibiden; Panasonic/EMC; Amphenol, TE and Molex are global participants by product portfolio | WUS, Shennan Circuits, Victory Giant, Shengyi Technology, Luxshare and other domestic participants have official AI/data-centre/high-speed product exposure | not disclosed | not disclosed | China has high-speed/high-layer PCB, CCL and connector capability. Atlas 950 layer count, material grade, connector interface, qualification, yield, ASP and allocation are not disclosed | High: orthogonal cableless architecture, cable-over-PCB, CPO, higher layer counts and blind-mate connectors redistribute content; capacity without yield/qualification is not revenue | H2/C13/C14/C15/C26/C27/C28 official company product/filing evidence; no Atlas order proof |
| 8. IDC, cloud, telecom operator, colocation, construction and utilities | AWS, Microsoft Azure, Google, Oracle and Meta as cloud/demand anchors; Equinix and Digital Realty as colocation operators | Huawei Cloud, Alibaba Cloud, Tencent Cloud, ByteDance, China Mobile/Telecom/Unicom, GDS, VNET and Range Technology as cloud/operator/IDC participants | not disclosed | not disclosed | China can build and operate AIDC facilities, but grid access, energy mix, water, permits, PUE, utilization and cloud monetization constrain economics. Named Atlas 950 sites/customers are not disclosed | Medium-high: public cloud, sovereign cloud, colocation and customer-owned facilities compete; utilization and power price dominate returns | H1/H4/C18/C19/C20 official demand/policy evidence; demand anchor only |

## 5. Layer-specific moats and profit-pool consequences

| Layer | Moat | Durability | Profit-pool consequence | Evidence needed for valuation credit |
|---|---|---|---|---|
| Accelerator + software | Hardware/software co-design, compiler/runtime, model libraries and installed developer base | Huawei: medium-high domestically if CANN performance and 950DT ramp validate; NVIDIA: high globally; AMD: medium/rising | Highest value density, but also highest technology and policy risk | Production configuration, independent workload benchmark, shipment/acceptance, ASP and segment margin |
| Scale-up fabric | Protocol, switch silicon, topology, collective algorithms, fault recovery and unified memory semantics | Medium-high; systems are difficult to qualify but standards can shift | Can move value from commodity Ethernet toward proprietary switches, optics and system integration | Architecture/BOM disclosure, port count, module count, qualification and failure-rate data |
| Server/ODM integration | Mechanical, power, cooling and field-service co-design; manufacturing yield and delivery | Medium; reference designs and customer bargaining can compress margins | Large revenue pool but often lower margin than silicon/optics; working capital matters | Named product, customer, backlog, delivery cycle, ASP and gross margin |
| Power | Reliability qualification, grid-to-chip engineering, installed service network | Medium-high at facility level | Large MW-linked value pool; project margins and cash conversion can be uneven | MW per system/site, order/backlog, delivery, project margin and receivables |
| Liquid cooling | Leak prevention, cold-plate/CDU design, materials, controls and service | Medium-high after platform qualification; architecture risk remains | Content rises with rack density, but OEM integration can internalize margin | kW/rack, CDU/cold-plate count and ASP, certification, customer design-in, service economics |
| Optical / OCS / CPO | Laser/optical-engine process, packaging, DSP/switch co-design and customer qualification | High technically; high substitution risk between architectures | Potentially high gross-margin pool, but module count is topology-sensitive | Speed/form factor, port/module count, customer qualification, yield, ASP and allocation |
| HBM and storage | DRAM process, stacking, base die, packaging yield and system-software integration | Very high for HBM; medium-high for AI storage | HBM is a core bottleneck and value pool; storage economics depend on attach and workload | Manufacturer, capacity, yield, contract/qualification, price and volume |
| PCB/CCL/connectors | Signal integrity, material formulation, layer/process capability, yield and qualification | Medium-high for qualified high-end products; lower for generic capacity | Mix and yield drive margin more than nominal capacity; architecture can displace cables/boards | Product specification, platform qualification, ASP, capacity/yield, customer allocation |
| IDC/operator | Power quota, site, network, utilization, customer contract and cost of capital | High for scarce powered land; economics cyclical and capital intensive | EBITDA can be attractive after utilization, but depreciation/debt and ramp dilute cash returns | Signed MW, utilization ramp, rental/compute price, power cost, capex, debt and contract term |

## 6. Localization boundary by technology

### Substitutable or available domestically now

- A domestic accelerator/software/interconnect stack exists in the form of Ascend, CANN and UnifiedBus, and Huawei has physically shown a 1,024-card Atlas 950 system [H4].
- China has capable server/rack, power, liquid-cooling, optical-module, high-speed PCB/CCL, connector and data-centre operators. Official company sources verify broad product participation [C6][C12][C13][C14][C15][C22][C23][C24][C26][C27][C28].
- Huawei has an AI-storage portfolio and predecessor 384-card systems have achieved reported commercial deployments [H1][H4][C11].

### Still imported, overseas-led, private or not disclosed

- Ascend 950DT foundry/process route, HBM wafer and base-die manufacturing, advanced packaging provider, yield and volume are not disclosed.
- Atlas 950 optical modules, OCS/CPO choice, switching silicon, module count, PCB/CCL grade, connectors, CDU, power system and OEM/ODM suppliers are not disclosed.
- Some high-end manufacturing equipment, EDA/IP and HBM supply are exposed to U.S. export controls [C16][C17].
- The 8,192-card system has not been publicly identified as physically deployed or customer-accepted by the cutoff.

The correct localization conclusion is therefore: **system architecture localization is officially evidenced; component-level localization and supplier allocation are only partially evidenced and often undisclosed.**

## 7. A-share relationship boundary and pool classification

| Company / ticker | Officially supported relationship | Evidence status | Correct pool | Why not core valuation yet | Upgrade trigger |
|---|---|---|---|---|---|
| iFlytek / 002230 | 2025 annual report states co-development on Ascend 950 and an Oct-2026 flagship-model plan | Official CNINFO filing [F1] | Demand anchor / satellite watch | Software/workload cooperation does not establish Atlas 950 hardware purchase, upstream order, ASP or margin | Named deployment or contract, product launch on 950, disclosed compute procurement and economics |
| Talkweb / 002261 | Direct Huawei/Ascend partnership documented in 2025 annual report | Official full CNINFO filing [F2] | Ascend ecosystem / satellite watch | Partnership scope does not identify Atlas 950 order, system configuration, revenue exposure or margin; recurring NP remains negative | Atlas 950 product name, qualification/order, delivery value, segment revenue and recurring profit |
| Shenling Environment / 301018 | Huawei is a disclosed data-service customer; cooperation with “Company H” | Official full CNINFO filing [F3] | High relationship watch; broader-AIDC valuation eligible | No Atlas 950 naming, platform certification, order/backlog, kW/ASP or margin bridge | Official Atlas platform design-in, order/backlog, CDU/cooling scope, delivery and margin disclosure |
| Innolight / 300308 and Eoptolink / 300502 | Named by NVIDIA in its photonics ecosystem | NVIDIA official ecosystem announcement [C3] | Global AI optics satellite | NVIDIA ecosystem participation is not Huawei Atlas 950 supply evidence; Atlas module count/architecture unknown | Huawei/UB platform qualification, named order, form factor, allocation and ASP |
| WUS / 002463, Shennan / 002916, Victory Giant / 300476 | Official filings describe AI-server/data-centre/high-speed PCB exposure | Official filings/product evidence [C14][C15] | PCB/CCL satellite | No Atlas 950 product, layer/material specification, customer qualification, order, yield or allocation | Atlas 950/UB platform naming plus product specification, qualification, order and economics |
| Luxshare / 002475 | Official product evidence for AI-rack copper, optical, power and thermal solutions | Official company product announcement [C13] | Interconnect satellite | Product capability and exhibition do not prove Huawei customer or Atlas content | Named platform/customer qualification, content per rack, order and margin |
| Power/IDC names | General AIDC power, cooling or facility exposure | Company/product/policy evidence varies | Satellite or demand anchor | Huawei roadmap and operator capex do not prove Atlas-specific order or revenue | Named project, MW, product, contract, delivery schedule, utilization and economics |

### Pool effect

- **Confirmed Atlas supplier core:** none. A company may enter only after official Atlas 950 product/process exposure, customer/platform qualification or order visibility, and economics sufficient to bridge revenue and margin.
- **Broader-business modeled pool:** 12 de-duplicated listed companies can receive a target based on official FY2025 actuals and original-PDF broader-business forecasts while Atlas revenue/NP/EPS credit remains zero. The authoritative relation/valuation/action reconciliation is `data/company_level_reconciliation_20260718.md/json`.
- **Satellite watch pool:** general AI-rack, Ascend ecosystem, optical, cooling, power, PCB/CCL/connector and IDC participants with explicit evidence gaps and upgrade triggers.
- **Demand anchors:** Huawei roadmap and predecessor deployment, iFlytek model collaboration, cloud/operator capex, national compute policy and global NVIDIA/AMD deployments. These validate demand context, not upstream earnings.

## 8. Concentration and source-exhaustion result

| Block | CR3 | CR5 | Sources checked | Result |
|---|---|---|---|---|
| Compute accelerators | not disclosed | not disclosed | Huawei, NVIDIA and AMD official product/roadmap sources | Product specifications found; comparable market denominator and current global/China shares not found |
| Server/OEM/ODM | not disclosed | not disclosed | Huawei open-hardware release, NVIDIA/AMD partner ecosystems, Lenovo and IEIT product sources | Participant lists found; share by AI rack, revenue or shipments not found |
| Power | not disclosed | not disclosed | Huawei Digital Power, Schneider, Vertiv, Delta and Eaton reference/product sources | Product capacities found; defined market concentration not found |
| Liquid cooling | not disclosed | not disclosed | Huawei, Schneider, Vertiv, Delta, Envicool and IEIT product/reference sources | Architecture and product evidence found; market concentration not found |
| Optical/networking/OCS | not disclosed | not disclosed | Huawei UB disclosures, NVIDIA photonics ecosystem, Coherent OCS | Participant and product evidence found; comparable module/port/revenue share not found |
| HBM/storage | not disclosed | not disclosed | Huawei, Samsung, Micron and SK hynix official sources | Product/ramp evidence found; current comparable HBM revenue/bit share and AI-storage concentration not established in the primary set |
| PCB/CCL/connectors | not disclosed | not disclosed | Luxshare, TTM, TE, Panasonic and official listed-company filings | Product/end-market exposure found; Atlas-specific and segment concentration not found |
| IDC/operators | not disclosed | not disclosed | Huawei deployments, MIIT policy, official global demand references | Demand and policy evidence found; comparable powered-MW or AI-compute-revenue concentration not found |

## 9. Competitive risks and monitoring triggers

| Risk | Why it matters | Trigger to monitor | Valuation consequence |
|---|---|---|---|
| 8,192-card execution gap | Competitive claim depends on scaling beyond the 1,024 physical system | Public full-system identification, independent benchmark, burn-in/acceptance, sustained utilization and failure rate | Do not give volume or premium-multiple credit before acceptance evidence |
| HBM and packaging opacity | 950DT memory is central to training/decode performance and supply | HBM manufacturing source, packaging capacity, yield, 144-GB specification confirmation and volume shipment | Blocks accelerator-volume and related supplier earnings bridge |
| Software utilization gap | Peak FLOPS can diverge from usable model throughput | Same-model benchmark, CANN version, porting time, training completion, inference latency and operator availability | Discount roadmap performance until independent workload proof |
| UBoE/optical topology change | Huawei itself says UBoE uses fewer switches/modules than RoCE | Final topology, port/module count, speed/form factor and OCS/CPO choice | Prevents simple optics-unit extrapolation; can upgrade some components while downgrading others |
| Power/cooling/site constraint | Multi-cabinet systems require facility-scale MW and heat rejection | kW per cabinet, system MW, CDU topology, grid approval, PUE, water and commissioning | Blocks power/cooling/IDC TAM and schedule credit |
| Export-control change | Affects competing imported accelerators and domestic manufacturing inputs | BIS EAR/licensing/HBM rule changes and enforcement guidance | Can increase domestic demand while worsening cost/yield and supply risk |
| Thematic over-attribution | General Huawei/AI exposure can be misread as an Atlas order | Exchange clarification, product naming, customer qualification, contract/backlog and revenue recognition | Keep unsupported names out of core valuation; cap at satellite watch |

## 10. Source key

- **[H1]** Huawei, 2025-09-18, official executive keynote: https://www.huawei.com/en/news/2025/9/hc-xu-keynote-speech. Capture: `sources/official-huawei-20260718/huawei_2025-09-18_xu_keynote_evidence.md`.
- **[H2]** Huawei, 2025-09-18, official open SuperPoD architecture release: https://www.huawei.com/en/news/2025/9/hc-superpod-innovation.
- **[H3]** Huawei, 2026-03-02, official MWC product launch: https://www.huawei.com/en/news/2026/3/mwc-superpod-ai. Capture: `sources/official-huawei-20260718/huawei_2026-03-02_mwc_atlas950_evidence.md`.
- **[H4]** Huawei, 2026-07-17, official WAIC physical-system release: https://www.huawei.com/cn/news/2026/7/atlas-950-superpod. Capture: `sources/official-huawei-20260718/huawei_2026-07-17_waic_physical_system_evidence.md`.
- **[C1]–[C28]** Official dated competitor, chain and policy sources: `sources/official-huawei-20260718/official_competitor_policy_source_index.md`.
- **[F1]** iFlytek 2025 annual report, official CNINFO filing: https://static.cninfo.com.cn/finalpage/2026-04-29/1225233581.PDF; local `sources/official-filings-20260718/002230-iflytek-2025-annual.pdf` and `.txt`.
- **[F2]** Talkweb 2025 full annual report, official CNINFO filing: https://static.cninfo.com.cn/finalpage/2026-04-28/1225218107.PDF; local `sources/official-filings-20260718/002261-talkweb-2025-annual-cninfo.pdf` and `.txt`.
- **[F3]** Shenling Environment 2025 full annual report, official CNINFO filing: https://static.cninfo.com.cn/finalpage/2026-04-27/1225181199.PDF; local `sources/official-filings-20260718/301018-shenling-2025-annual-cninfo.pdf` and `.txt`.
