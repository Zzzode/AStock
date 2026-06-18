# Open Supply Hub Expanded Supplier Evidence

**Run date:** 2026-06-18

**Source:** Open Supply Hub facility search and facility API replay with browser client header.

**Raw archive:** `sources/probe-cloud-customer-side-20260617/osh-expanded-20260618/`

**Boundary:** OSH identifies public-list contributors, list names and facility metadata. It does not disclose customer product, PCB/CCL revenue, AI/cloud platform allocation, ASP, shipments, order value, gross margin, depreciation or working-capital assumptions.

## Search Scope

The expanded pass tested additional Microsoft FY24 Top 100 board/component supplier names and report-universe names after the initial Victory Giant / Avary pass:

- Tripod / Tripod Technology
- Unimicron Technology
- Suzhou Dongshan Precision / Dongshan Precision
- Shennan Circuits
- Meiko Electronics
- MEKTEC
- HannStar Board
- Samsung Electro Mechanics
- WUS Printed Circuit

## Material Hits

| Supplier / facility group | OSH facilities archived | Public-list contributors recovered | Product / facility metadata recovered | Raw evidence |
|---|---:|---|---|---|
| Tripod | 3 relevant China facilities | Amazon.com, Apple, Dell, Samsung, Alliance for Water Stewardship | Amazon rows: `Finished goods`; Dell rows: `Parts/Components` and `Other direct material suppliers`; AWS rows: `Semiconductor Manufacturing`; worker-count rows for Wuxi facilities | `osh-CN2022289NQR96X.json`; `osh-CN20222890YGFFP.json`; `osh-CN2022306X3EA7Z.json` |
| Unimicron Technology | 6 China/Taiwan/Japan facilities | Apple; Alliance for Water Stewardship | One AWS public-list row includes `Semiconductor Manufacturing`; otherwise no product/revenue fields | `osh-CN202229792A9DM.json`; `osh-TW20222979523C2.json`; `osh-JP20222979VPQPS.json`; `osh-TW2022297D0ZRAH.json`; `osh-TW2022297FKNQZG.json`; `osh-TW2022297042CNA.json` |
| Suzhou Dongshan Precision | 3 China facilities | Apple; Sheffield Hallam University Forced Labour Lab | No customer product, revenue or platform fields; one non-customer risk-list contributor row appears for one facility | `osh-CN2022297J0FGGA.json`; `osh-CN2022297AMSYA8.json`; `osh-CN2022297PRSVT5.json` |
| Meiko Electronics | 5 China/Vietnam/Japan facilities | Amazon.com; Samsung; gBizINFO | Amazon rows: `Finished goods` for Wuhan and Vietnam facilities; no product/revenue/platform fields | `osh-CN2022297438AXZ.json`; `osh-VN2022297V1PH65.json`; `osh-VN2022289P4RNRW.json`; `osh-JP2025352VBT7WG.json`; `osh-JP2025352QNYKT4.json` |
| MEKTEC / Mektec | 1 Taiwan facility | Amazon.com; Apple | Amazon rows: `Finished goods`; worker-count rows | `osh-TW20222974ZKT9W.json` |
| Shennan Circuits | 1 U.S. location | U.S. Small Business Administration | No customer/product/revenue/platform fields | `osh-US20243012ABMGF.json` |

## Searches With No Material Hit

| Search term | Result |
|---|---|
| `Tripod Technology` | No exact-hit facilities; broader `Tripod` recovered the material facilities above. |
| `HannStar Board` | No facilities recovered in this OSH pass. |
| `Samsung Electro Mechanics` | No facilities recovered in this OSH pass. |
| `WUS Printed Circuit` | No facilities recovered in this OSH pass. |

## Interpretation

- The expanded OSH pass materially strengthens customer-side public network evidence beyond Victory Giant and Avary. Tripod has Amazon, Apple, Dell and Samsung public-list links; Unimicron and Dongshan have Apple public-list links; Meiko and Mektec have Amazon public-list links.
- Some OSH public-list rows add coarse product/facility metadata such as `Parts/Components`, `Other direct material suppliers`, `Semiconductor Manufacturing` and `Finished goods`.
- None of the recovered OSH records provide named customer/platform revenue split, platform-specific shipment/ASP/order value, PCB/CCL product revenue, gross margin, depreciation, tax or working-capital inputs.
- Therefore this evidence improves relationship confidence and source exhaustion, but it does not close the strict `named_platform_customer_revenue_split` or `bottom_up_customer_platform_eps_model` requirements.
