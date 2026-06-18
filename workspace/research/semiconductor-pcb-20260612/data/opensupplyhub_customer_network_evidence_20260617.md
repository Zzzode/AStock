# Open Supply Hub Customer Network Evidence

**Run date:** 2026-06-17

**Source:** Open Supply Hub web UI and facility API with browser client header.

**Boundary:** OS Hub facility API and web UI identify contributors/list names and some facility metadata. They do not disclose products, PCB/CCL revenue, AWS/AI platform allocation, ASP, shipment or order value.

| Facility | OS ID | Sector | Facility / processing type | Worker count evidence | Contributors / list names | Raw JSON |
|---|---|---|---|---|---|---|
| Victory Giant Technology (Huizhou) Co., Ltd. | CN2022297DRGCBN | Electronics | Finished goods, Finished goods | 5982-5982 from Amazon.com, Inc.; 1000-1000 from Amazon.com, Inc. | Amazon.com, Inc. (Amazon Facility List 2022); Amazon.com, Inc. (Amazon Facility List 2023); Amazon.com, Inc. (Amazon Facility List 2024) | `sources/probe-cloud-customer-side-20260617/osh-CN2022297DRGCBN.json` |
| Avary Holding (Shenzhen) Co. Ltd | CN2022306H1D256 | Electronics | N/A | 1000-1000 from Amazon.com, Inc. | Amazon.com, Inc. (Amazon Facility List 2023); Alliance for Water Stewardship [Public List] (Alliance for Water Stewardship 2022 Facility List) | `sources/probe-cloud-customer-side-20260617/osh-CN2022306H1D256.json` |

## Interpretation

- Victory Giant Technology (Huizhou) has Amazon.com, Inc. contributor rows from Amazon Facility List 2022, 2023 and 2024, sector `Electronics`, and Amazon-contributed facility/processing type `Finished goods`.
- Avary Holding (Shenzhen) has Amazon.com, Inc. contributor row from Amazon Facility List 2023 and sector `Electronics`.
- This materially improves customer-side supply-chain network evidence, but it still does not provide product, revenue, platform, ASP, shipment or order details.

## Follow-up Expansion

On 2026-06-18, a broader OSH pass tested Tripod, Unimicron, Dongshan, Shennan, Meiko, MEKTEC, HannStar Board, Samsung Electro Mechanics and WUS Printed Circuit. The expanded evidence is stored separately in `data/opensupplyhub_expanded_supplier_evidence_20260618.md` and raw JSONs under `sources/probe-cloud-customer-side-20260617/osh-expanded-20260618/`.

That expansion added public-list contributor evidence for Tripod, Unimicron, Dongshan, Meiko and Mektec, but still did not recover customer product, revenue, platform, ASP, shipment or order-value fields.
