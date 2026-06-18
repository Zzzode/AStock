# Current Customer Supplier-List Recheck

**Run date:** 2026-06-18

**Purpose:** Recheck current customer-owned supplier-list and responsible-sourcing pages for Amazon, Dell, Microsoft and Apple after the upstream supplier-list pass, with emphasis on whether newer public pages add product, PCB/CCL revenue, platform allocation, ASP, shipment, order value, margin or EPS inputs.

**Raw archive:** `sources/probe-current-customer-supplier-lists-20260618/`

**Boundary:** The recheck adds current customer-side source files and confirms supplier-map currency, but it does not disclose named platform revenue split or bottom-up EPS model inputs.

## Archived Source Files

| Source | Archived file | Extracted text | Result |
|---|---|---|---|
| Amazon supply-chain page | `amazon-supply-chain-20260618.html` | HTML archived directly | States the supplier list and interactive map cover finished-product suppliers of Amazon-branded apparel, consumer electronics, food and beverage, and home goods; the list is shared to Open Supply Hub, list `3316`, and was last reviewed in March 2026. |
| Amazon 2024 Sustainability Report | `amazon-2024-sustainability-report.pdf` | `amazon-2024-sustainability-report.txt` | States the 2024 supplier list included nearly 2,300 finished-product suppliers and that Amazon shares supplier-list data to Open Supply Hub. |
| Amazon Open Supply Hub list route | `amazon-osh-list-3316-20260618.html` | HTML archived directly | Public OSH route for Amazon contributor `1078` and list `3316` was archived as the current map entry point; static HTML does not expose product/revenue fields. |
| Dell reports/resources page | `dell-reports-resources-20260618.html` | HTML archived directly | Current Dell reports hub still links to the public supplier list. |
| Dell public supplier list | `dell-public-supplier-list-20260618.pdf` | `dell-public-supplier-list-20260618.txt` | Current downloadable Dell public supplier list was archived; it exposes procurement categories such as `Parts / Components`, `PCBA` and `Networking` for relevant supplier rows, including Tripod, Gold Circuit, Hannstar, Delton, Broadcom, Marvell and Nvidia International. |
| Microsoft reports hub | `microsoft-reports-hub-20260618.html` | HTML archived directly | Current Microsoft reports hub exposes 2025 sustainability, human-rights, conflict-minerals and responsible-sourcing reports, but the static page did not expose a newer Top 100 Production Suppliers link beyond the FY24 route already archived. |
| Apple supply-chain page | `apple-supply-chain-20260618.html` | HTML archived directly | Current Apple supply-chain overview discusses suppliers and recycled tin solder / gold plating in Apple-designed printed circuit boards, but does not provide a supplier list or supplier revenue allocation. |
| Apple Supplier Code of Conduct and Supplier Responsibility Standards | `apple-supplier-code-standards-20260618.pdf` | `apple-supplier-code-standards-20260618.txt` | Current Apple standards document was archived; it governs supplier conduct and standards, not supplier identities, products or platform revenue. |

## Incremental Evidence

| Customer route | Incremental fields recovered | What it does not recover |
|---|---|---|
| Amazon current supplier map | Confirms current public list route, Open Supply Hub list id `3316`, contributor id `1078`, March 2026 review date, and consumer-electronics scope. | No supplier product, PCB/CCL revenue, AWS/AI platform allocation, ASP, shipment, order value, margin or EPS assumptions. |
| Dell current public supplier list | Confirms current downloadable supplier list route and category-level rows including `PCBA`, `Networking`, and `Parts / Components`; relevant board/component suppliers include Tripod, Gold Circuit, Hannstar and Delton. | No specific Dell product/platform, AI server allocation, PCB revenue, order value, ASP, shipment or margin. |
| Microsoft current reports hub | Confirms responsible-sourcing report hub was rechecked; no newer Top 100 supplier list was exposed in static HTML. | Does not improve beyond the existing FY24 Microsoft Top 100 supplier PDF for supplier names; no product/platform/revenue fields. |
| Apple current supply-chain/standards route | Confirms current Apple pages are standards/overview documents, with a general Apple-designed PCB materials reference. | No supplier list, supplier product, revenue, order, ASP, shipment, platform allocation or EPS input. |

## Interpretation

- This pass removes another feasible public-source route from the uncollected bucket: current customer-owned supplier-list/reporting pages were archived, link-extracted and searched.
- Amazon and Dell add the strongest incremental current-source evidence because they expose supplier-map currency and procurement-category fields, respectively.
- The hard named-customer and EPS-model requirements remain unresolved: none of the current customer pages disclose the fields needed to build a named platform/customer revenue split or customer/platform bottom-up EPS model.

Machine-readable remaining gap: No current customer-side supplier-list route discloses named platform/customer revenue split, terminal-grade positioning/order flow, or customer/platform EPS model inputs.
