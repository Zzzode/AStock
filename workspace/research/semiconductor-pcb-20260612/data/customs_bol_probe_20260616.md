# Customs / Bill-of-Lading Probe Evidence

**Source directory:** `workspace/reports/semiconductor-pcb-customs-bol-probe-20260616/`

**Purpose:** Check whether public customs or bill-of-lading pages can provide customer-level evidence for AI PCB / CCL relationships that issuer filings and public broker reports do not disclose.

## Findings

| Source | Probe | Public result | Usefulness |
|---|---|---|---|
| ImportGenius | Wus Printed Circuit Co., Ltd. | Public page shows WUS shipment profile and visible sample partners such as Navico / Continental-related counterparties. | Useful only as proof that public BOL pages exist; not relevant to NVIDIA / Google / AWS / Microsoft AI-platform revenue. |
| ImportGenius | Victory Giant Technology (Huizhou) | Public page shows 25 total shipments, top partner Amphenol Manufacturing Bonded Wareh and product description `printed circuit board`. | Confirms generic PCB shipment visibility, but not named AI platform customer revenue. |
| ImportYeti | WUS Printed Circuit | Cloudflare challenge page. | No usable evidence. |
| Panjiva | Nvidia Corporation buyer profile | Public page shows Nvidia buyer profile and origin-country counts, but detailed suppliers/transactions are gated. | Does not disclose attributable PCB / CCL supplier list or shipment value publicly. |

## Decision

Do not use customs / BOL snippets as confirmed customer-chain revenue evidence. The public pages do not provide:

- named NVIDIA / Google / Microsoft / AWS PCB or CCL supplier rows for the covered A-share issuers,
- shipment values that can be tied to platform revenue,
- ASP / quantity / margin assumptions, or
- enough product detail to map a shipment to AI-server PCB / CCL platforms.

## Boundary

This path supports the unresolved requirement boundary. To close the named-platform revenue split from shipment data, a paid customs/BOL database query with full consignee, shipper, product, quantity, value and date fields would be required, followed by issuer-entity mapping and manual false-positive filtering.
