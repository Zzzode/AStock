# Apple Customer-Side Official Probe

**Run date:** 2026-06-16

**Purpose:** Test whether Apple-side official public sources can strengthen or close the named customer/platform revenue-split gap for Pengding / Zhen Ding and related PCB suppliers.

## Archived Files

| Source | Local file | Result | Treatment |
|---|---|---|---|
| Apple official supply-chain page | `workspace/reports/semiconductor-pcb-customer-side-official-probe-20260616/apple-supply-chain.html` | Official Apple page downloaded successfully from `https://www.apple.com/supply-chain/`. Page discusses Apple supply-chain standards, environment, worker programs and responsible sourcing. It does not expose a searchable supplier list, Pengding / Zhen Ding / Avary entries, PCB supplier names, revenue, order value, ASP or shipment quantities. | Use as customer-side source-exhaustion evidence only. |
| Legacy Apple supplier-list PDF paths | `https://www.apple.com/supplier-responsibility/pdf/Apple-Supplier-List.pdf`, `Apple-Supplier-List-2024.pdf`, `Apple-Supplier-List-2023.pdf` | Apple server returned HTTP 301 to `https://www.apple.com/supply-chain/`, not a supplier-list PDF. | Records that old official PDF paths no longer provide a supplier-list PDF in this environment. |
| Third-party Apple supplier-list mirror | `workspace/reports/semiconductor-pcb-customer-side-official-probe-20260616/apple-supplier-list-2021-usermanual-mirror.html` | Attempted PDF download returned a Manuals+ / Cloudflare security-check HTML page, not a PDF. Search snippets mention a 2021 Apple Supplier List mirror, but the file was not accessible as an auditable source. | Reject as evidence. Do not use to confirm supplier relationship or revenue. |
| Apple Newsroom supplier clean energy article | `workspace/reports/semiconductor-pcb-customer-side-official-probe-20260616/apple-newsroom-202304-supplier-renewable-energy.html` | Apple official newsroom article states that more than 250 suppliers are committed to 100% renewable energy for Apple production by 2030 and that "Avary Holding, which joined the program in 2020, is launching its own initiative..." | Confirms customer-side official supply-chain program participation for Avary Holding, but not product type, PCB line item, revenue, order value, ASP, shipment or platform allocation. |
| Apple 2022 / 2024 clean-energy articles | `apple-newsroom-202210-decarbonize-supply-chain.html`; `apple-hk-newsroom-202404-clean-energy-water.html` | Official Apple articles document supplier decarbonization requirements and aggregate supplier clean-energy progress, including 200+ / 320+ supplier counts and direct manufacturing spend coverage. They do not name Pengding / Zhen Ding / Avary in the tested text except the 2023 Avary mention above. | Use as Apple customer-side context, not as revenue or customer-allocation evidence. |

## Finding

Apple official Newsroom confirms Avary Holding joined Apple’s Supplier Clean Energy Program in 2020. No Apple official public page or accessible PDF recovered in this pass discloses Pengding / Zhen Ding / Avary product type, revenue contribution, order amount, ASP, shipments or platform-level allocation.

## Boundary

This confirms one customer-side official relationship signal for Avary Holding but does not convert it into a PCB product, customer-revenue, platform, margin or EPS bridge. Apple-side public official sources still do not provide any revenue split that can close the named-customer / platform EPS model gap.

## Report Treatment

- Keep issuer filings, official IR and original broker PDFs as the primary evidence for Pengding / Zhen Ding customer-chain exposure.
- Keep Apple-side public pages as source-exhaustion evidence only.
- Do not use third-party Apple supplier-list mirrors, blogs or snippets as confirmed evidence.
