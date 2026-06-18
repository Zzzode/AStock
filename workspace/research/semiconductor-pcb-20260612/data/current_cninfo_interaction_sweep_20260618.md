# Current CNInfo Interaction Sweep

**Run date:** 2026-06-18

**Source:** CNInfo / SZSE Interactive Easy company-question POST endpoint, keyboard lookup endpoint and existing current company-page archives.

**Raw archive:** `data/raw_cninfo_current_interaction_sweep_20260618/`

**Status:** Completed for the 8 Shenzhen-listed report names covered by CNInfo / SZSE Interactive Easy. The sweep archived 160 completed company-question files, covering 20 keywords for each Shenzhen-listed name, plus keyboard lookup evidence for `301377`. The raw files contain 35 matched rows, which deduplicate to 14 unique question IDs. Shanghai-listed names were handled through the bounded SSE / 上证e互动 probe below.

**Boundary:** Official issuer interaction evidence. It can confirm product progress, capacity/ramp comments and disclosure boundaries. It does not disclose named customer/platform revenue, order value, ASP, shipment, margin or EPS contribution.

## Summary

| Ticker | Company | Incremental evidence from current sweep | Treatment |
|---|---|---|---|
| 002463 | Hudian | Latest CNInfo page rows include questions on office-area conversion to PCB production, high-end PCB price increases, Rubin supply-chain rumors, CoWoP/mSAP/light-copper integration, M10 materials, P2Pack data-center migration, Thailand plant profitability/ramp, and AI PCB price pass-through. Company replies confirm commercial-policy restriction on named vendors, high-end PCB pricing tied to technical value and market supply/demand, CoWoP/mSAP/light-copper/M10 development risk, supply-chain material upgrade work and Thailand operational ramp. | Strengthens product/ramp/pricing evidence and named-customer confidentiality boundary. Not revenue split. |
| 300476 | Victory Giant | Current CNInfo rows include ASIC/GPU demand questions, NVIDIA Spark, midplane, mSAP / orthogonal backplane capacity and certification, CB300, domestic chip customers, Tesla AI5, GB200/GB300, CoWoP rumors and GTC supplier-summit question. Company replies repeat commercial-policy restrictions, state ASIC-related business progresses smoothly, mSAP Huizhou capacity supports 1.6T optical modules with full orders and good utilization, CoWoP R&D/production is being advanced, high-end PCB capability includes 100+ layer MLPCB, 10-order 30-layer HDI and 16-layer any-layer HDI, and Huizhou/Thailand projects are ramping by phase. | Strengthens official product/capacity/order-progress evidence, but keeps named customer/platform claims confidential. |
| 002436 | Xingsen | Completed sweep recovered a current investor question citing Rubin rack value-chain logic, but no issuer reply was recovered in the completed files. | Archived as question-only; do not use as confirmed evidence. |

## Notable Extracts

- Hudian on Rubin / NVIDIA customer questions: the company states that, due to commercial policy restrictions, it cannot discuss specific vendors; it says it cooperates with domestic and overseas customers across multiple technology platforms and is capturing AI / high-speed-networking structural PCB demand.
- Hudian on high-end PCB pricing: the company says PCB products are highly customized and pricing is guided by technology value, quality premium and market supply/demand; AI-server and high-speed-switch products often involve 22+ layer multilayer boards, fine lines and advanced materials.
- Hudian on CoWoP / mSAP / light-copper / M10: related projects involve long R&D cycles, high technical difficulty and commercialization risk.
- Victory Giant on ASIC: the company says ASIC-related customer business is progressing smoothly, but it cannot discuss specific customer names or business details without permission.
- Victory Giant on mSAP / orthogonal backplane: the company says mSAP capacity in Huizhou is used for 1.6T optical modules; current orders are full and utilization is good; CoWoP R&D and production work is being advanced.
- Victory Giant on capacity: Huizhou plant-four projects are in phased ramp / mass-production stage; plant-ten, plant-eleven and Thailand factory construction are progressing quickly and orderly.

## Completion Impact

This sweep improves official issuer-side evidence for product progress, pricing mechanism, capacity ramp and disclosure boundaries. It still does not close the strict named customer/platform revenue split or customer/platform bottom-up EPS model because issuers continue to withhold specific customer names and business details under commercial-policy restrictions.

## SSE / 上证e互动 Shanghai-Name Probe

A bounded SSE interaction refresh was also run for Shanghai-listed report names:

| Probe | Archived source | Result | Treatment |
|---|---|---|---|
| Shengyi + M9/AI/CCL search | `sources/probe-sse-interaction-refresh-20260618/sse-search-600183-shengyi-m9-ai.html` | Search page archived; no useful visible result row recovered in the HTML. | Boundary evidence only. |
| Huazheng + CBF/BT search | `sources/probe-sse-interaction-refresh-20260618/sse-search-603186-huazheng-cbf-bt.html` | Search page archived; no useful visible result row recovered in the HTML. | Boundary evidence only. |
| Nanya + M8/M9/customer search | `sources/probe-sse-interaction-refresh-20260618/sse-search-688519-nanya-m8-m9.html` | Search page archived; no useful visible result row recovered in the HTML. | Boundary evidence only. |
| Circuit Fabology Q&A detail | `sources/probe-sse-interaction-refresh-20260618/sse-qadetail-688630-1728379.html` | Current visible Q&A only disclosed shareholder count: as of 2026-05-20, total shareholders were 19,849. | Holder metadata only; no customer/order/model evidence. |

This confirms no additional customer/platform revenue or EPS-model variables were recovered from the bounded SSE refresh.
