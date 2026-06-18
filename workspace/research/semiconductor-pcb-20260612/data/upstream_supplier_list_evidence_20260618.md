# Upstream Supplier List Evidence

**Run date:** 2026-06-18

**Purpose:** Follow the public-list contributors exposed by Open Supply Hub back to upstream customer / certification source files where those files are publicly retrievable.

**Raw archive:** `sources/probe-upstream-supplier-lists-20260618/`

**Boundary:** These lists identify supplier or certified-site relationships and sometimes coarse procurement categories. They do not disclose product shipped to a specific customer platform, PCB/CCL revenue, AI/cloud allocation, ASP, shipment, order value, margin, depreciation, tax or EPS assumptions.

## Archived Source Files

| Source | Archived file | Extracted text | Source scope |
|---|---|---|---|
| Apple Supplier List 2018 | `apple-supplier-list-g.pdf` | `apple-supplier-list-g.txt` | Facility-level Apple supplier list with addresses. |
| Apple Supplier List FY2020 / 2021 PDF | `apple-supplier-list-k.pdf` | `apple-supplier-list-k.txt` | Apple supplier list representing 98% of direct spend for materials, manufacturing and assembly in fiscal year 2020. |
| Dell Public Supplier List | `dell-public-supplier-list-official-retry.pdf` | `dell-public-supplier-list-official-retry.txt` | Public list of supplier facilities covering at least 95% of Dell spend in fiscal year 2025; includes procurement category and supplier type. |
| Samsung Electronics Supplier List | `samsung-supplier-list.pdf` | `samsung-supplier-list.txt` | Alphabetized component and outsourcing suppliers representing 80% of Samsung Electronics procurement expenditures for materials and manufacturing at publication. |
| Alliance for Water Stewardship certified sites | `aws-certified-sites.html` | HTML archived directly | Certified-site table with owner, site, address, certification level, dates, standard version and sector. |

## Incremental Evidence

| Source | Supplier / facility hits | Incremental fields recovered | What it does not recover |
|---|---|---|---|
| Apple Supplier List 2018 | Suzhou Dongshan Precision Manufacturing, Tripod Technology, Unimicron Technology. | Facility addresses for Dongshan in Suzhou; Tripod Wuxi and Taoyuan facilities; Unimicron Taoyuan, Suzhou and Hokkaido facilities. | No product, revenue, order, ASP, shipment or Apple-platform allocation. |
| Apple Supplier List FY2020 | Suzhou Dongshan Precision Manufacturing, Tripod Technology Corporation, Unimicron Technology Corporation, Samsung Electro-Mechanics Company Limited, Zhen Ding Technology Holding Limited. | Primary locations where manufacturing for Apple occurs. Zhen Ding locations include Guangdong, Hebei, Jiangsu and Tamil Nadu; Tripod in Jiangsu; Unimicron in Hokkaido/Hsinchu/Taoyuan; Samsung Electro-Mechanics in Tianjin/Busan/Sejong/Laguna/Chachoengsao. | No product, revenue, order, ASP, shipment or Apple-platform allocation. |
| Dell Public Supplier List FY2025 | Tripod; Gold Circuit; Hannstar. | Tripod rows classify procurement category as `Parts / Components` and supplier type as `Other direct material suppliers`; Dell list states it covers at least 95% of Dell spend in FY2025. | No specific Dell product/platform, PCB revenue, order value, ASP, shipment or margin. |
| Samsung Electronics Supplier List | Meiko Electronics, Samsung Electro-Mechanics, Tripod Technology, Korea Circuit, Ibiden, Daeduck Electronics. | Samsung list classifies the corpus as component and outsourcing suppliers representing 80% of Samsung Electronics procurement expenditures for materials/manufacturing; it lists Tripod Xiantao, Meiko Vietnam and Samsung Electro-Mechanics locations. | No specific Samsung product/platform, PCB revenue, order value, ASP, shipment or margin. |
| AWS certified sites | Avary/Hongqisheng, Qing Ding / Zhen Ding group, Tripod Wuxi, Victory Giant Huizhou. | Certified-site sector `Electronics & Semiconductor Manufacturing`, certification level/date/expiry and site addresses. | Certification evidence, not customer procurement; no customer product, revenue, order, ASP, shipment or EPS assumptions. |

## Interpretation

- This upstream-source pass confirms that several OSH public-list contributor rows can be traced to archived public customer or certification sources, not only OSH-derived metadata.
- Apple and Dell add the strongest incremental customer-side source quality because they are customer-owned supplier lists. Samsung adds a customer-side component / outsourcing supplier list for relevant PCB/component suppliers. AWS adds certified-site metadata, not procurement.
- The evidence improves relationship confidence for public-list supplier mapping, especially Tripod, Dongshan, Unimicron, Zhen Ding / Avary group, Meiko, Samsung Electro-Mechanics and Victory Giant.
- The hard requirements remain unresolved because none of the upstream lists disclose named customer/platform revenue split or bottom-up EPS model inputs.
