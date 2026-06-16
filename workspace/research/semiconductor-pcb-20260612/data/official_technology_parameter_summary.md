# Official Technology Parameter Summary

**Source:** Official 2025 annual reports from CNInfo and downloaded broker PDFs.

| Company | Official / full-report technology evidence | Remaining gap |
|---|---|---|
| 沪电股份 | Official annual report states AI data-communication infrastructure pushes HLC, high-frequency/high-speed, HDI and high-current PCB requirements; mentions support for 224G SerDes transmission needs. | Does not disclose exact layer count by product, Dk/Df, line width/spacing or customer platform BOM. |
| 胜宏科技 | Official annual report states full PCB category coverage; 100+ layer high multilayer PCB capability; 10-stage 30-layer HDI and 16-layer any-layer HDI capability; next-generation 14-stage 36-layer HDI R&D certification; AI compute card and AI Data Center UBB/switch market share globally leading. | Does not disclose exact customer/project revenue split. |
| 深南电路 | Official annual report maps data-center products to switch, optical module, server/storage PCB and corresponding backplane, high-speed multilayer, HDI, high-speed material, high-density and fine-line processes; FC-BGA high-end substrate risk and capacity ramp are disclosed. | Does not disclose exact layer/material specs by customer. |
| 生益科技 | Official annual report discusses AI demand and high-end copper foil / Low Dk cloth supply shift; broker model shows gross-margin expansion. | M8/M9/M10 revenue share and Dk/Df values remain unavailable. |
| 华正新材 | Official annual report states high-speed CCL focus on AI server, switch, optical module and antenna markets; full-grade halogen-free high-speed CCL for 112Gbps and 224Gbps switches; develops ultra-low-loss substrate for AI servers and compute chips; BT material in RF PA, Memory, FC-BGA; CBF film in FC-BGA/ECP/VCM and CBF-RCC for AI server / CPU/GPU low-loss materials. | Customer certification names and revenue split remain unavailable. |
| 南亚新材 | Official annual report / IR evidence states M6-M8 materials are batch-applied by domestic leading compute customers; M9 is in NPI introduction; M10 launched in 2025Q4 and is under overseas core compute-terminal certification; NOUYA8U completed Huawei core-customer access and scaled mass production; NY6300S entered multi-customer PCIe Gen5 server mass production and PCIe Gen6 completed top-customer evaluation. | Dk/Df table, ASP and revenue by M6-M10 generation remain unavailable. |
| 兴森科技 | Official annual report states PCB revenue 48.97亿元 and IC substrate revenue 16.70亿元; FCBGA substrate project has made mass-production preparation in technology, capacity scale and yield, with customer introduction and sample delivery progressing; Huaxin report adds mSAP fine-line mass-production import and 2026-2028E NPP/EPS forecast. | FCBGA customer names, yield curve, ASP, and platform revenue remain unavailable. |
| 大族数控 | Official annual report states CCD six-axis independent mechanical drilling equipment completed next-generation AI-server PCB processing certification and achieved mass production at multiple high-layer-board leading customers; drilling-equipment revenue 41.67亿元 and AI high-layer/HDI demand drives equipment upgrades. | Customer names, contract backlog and product-by-platform equipment revenue remain unavailable. |
| 芯碁微装 | Official annual report / IR evidence shows PCB-series revenue 10.80亿元, pan-semiconductor-series revenue 2.33亿元, WLP2000 wafer-level packaging equipment with 2um precision, high-end PCB / HDI / substrate-like board focus, IC-substrate exposure equipment and 4um line-width capability. | Customer-level order backlog and AI platform capex attribution remain unavailable. |
| 劲拓股份 | Official annual report shows electronic assembly equipment revenue 7.27亿元, gross margin 31.68%, and terminal applications including compute servers; AI server growth is cited as a PCBA-chain structural opportunity. | This is a looser PCBA equipment proxy; no AI-server customer, order value or semiconductor-packaging furnace revenue split. |
| 鼎泰高科 | Official annual report shows precision-tool revenue 17.40亿元, grinding/polishing material revenue 1.92亿元, 0.20mm-and-below micro-drill sales share 29.65%, coated drill sales share 39.40%, above-50x high-aspect-ratio drill technical reserve, and AI-server ABF / PTFE / high-frequency-high-speed PCB tool R&D. | Customer/platform revenue and order value for AI-server drilling consumables remain unavailable. |
| 鹏鼎控股 | HKEX filing excerpt states products cover AI accelerator cards, AI servers, data-center switches, UBB and optical transceivers; technical capability includes 70+ layer MLPCB mass production, 100+ layer MLPCB technical capability, 24-layer 6+12+6 HDI and 28-layer 8+12+8 HDI mass production; 9M2025 HDI utilization 91.1%. Official IR adds 800G/1.6T optical-module SLP mass-shipment path and 3.2T R&D. | Anonymous customer codes cannot be mapped to named NVIDIA/Google/optical customers; product-level margins and platform revenue remain unavailable. |

## Interpretation

The technical gap is now reduced from pure concept to disclosed capability parameters across the 12-name report universe. Exact product-level Dk/Df, line width/spacing, platform BOM, customer-specific specs and named platform revenue remain unavailable in public filings.

## Extra broker technical report: Shengyi high-speed CCL

**Source:** `workspace/reports/semiconductor-pcb-extra-20260615/600183-xinan-high-speed-ccl.pdf`.

Key extracted evidence:
- High-frequency boards focus on Dk stability; high-speed boards focus on lower Df.
- CCL loss grade examples: Standard Loss Df 0.010-0.020; lower-loss grades are used for server/switch applications.
- AI server PCB increment is mainly GPU board group: OAM, NvSwitch and high-speed backplane.
- H100 GPU board group uses M6/M7+ high-speed CCL; OAM uses 5-stage 20-layer process; UBB uses 20-layer through-hole board.
- Single AI server CCL value estimated at CNY 4,000-5,000, including about CNY 3,000 from GPU board group and about CNY 1,300 from CPU motherboard group.
- OAM CCL value estimated at CNY 1,745 per server; UBB CCL value estimated at CNY 1,364 per server in the report assumptions.

This source materially improves the technical parameter and unit-value bridge for high-speed CCL, but it is a 2024 broker report and should be used as a framework, not current confirmed GB300/Rubin pricing.
