# Shengyi SSE Interaction Probe

**Purpose:** Upgrade and bound Shengyi Technology (`600183`) public interaction evidence for AI CCL / GPU / M8-M9 questions.

## Official source files archived

| Source | Local file | Result |
|---|---|---|
| SSE company page | `data/raw_sse_company_600183.html` | Confirms official SSE interaction company page for Shengyi Technology and company `uid=183`. |
| SSE company feed, type 10 | `data/raw_shengyi_sse_userfeeds_type_10_page1.html` | Recent investor question feed; includes an investor question about M8/M9 stocking and drilling-process concerns, but no issuer reply in the captured item. |
| SSE company feed, type 11 | `data/raw_shengyi_sse_userfeeds_company_q_page1.html`; `page2`; `page3` | Reply feed returned "近1个月暂无回复"; no recent issuer reply body recovered. |
| SSE full-text searches | `data/raw_sse_search_shengyi_m9.html`; `data/raw_sse_search_600183_m9.html`; `data/raw_sse_search_shengyi_gpu.html` | Full-text search pages were archived, but did not expose a stronger issuer Q&A body for M8/M9/GPU customer certification beyond the already archived official IR PDF. |
| SSE official IR PDF | `workspace/research/semiconductor-pcb-20260612/sources/ir-core-20260615/600183-sse-202505-ir.pdf`; `.md` | Strongest current official source. Confirms AI server demand requires lower-loss CCL, Shengyi is working with domestic and overseas terminals around GPU and AI project development, some products are in batch supply, and Thailand CCL/prepreg base investment is about CNY 1.4bn. |

## Evidence recovered

- The SSE company page is directly accessible and identifies Shengyi Technology (`600183`) with interaction `uid=183`.
- The recent type-10 question feed includes an investor question asking about M8/M9 stocking/ramp and drilling-process impact, but it is a question-only item in the captured feed.
- The type-11 reply feed returned "近1个月暂无回复" for pages 1-3, so it does not provide a new company reply for M8/M9/M10 revenue share, named customer certification, ASP, shipment or customer-platform margin.
- The official SSE IR PDF remains the valid evidence layer: AI server hardware upgrades require lower-loss CCL; Shengyi is working with domestic and overseas terminals around GPU and AI project development; some products are already in batch supply; the company states customer structure is diversified and dependence on a single market is low.

## Boundary

This pass improves source exhaustion and reproducibility, not the named-customer model. The public SSE interaction page and recent feed do not disclose:

- M8/M9/M10 revenue share.
- Named GPU / ASIC / domestic compute / optical-module customer certifications for Shengyi Technology.
- Customer-specific CCL ASP, shipment, gross margin or order value.
- Customer/platform EPS contribution.

The report should continue to use the official SSE IR PDF and official filings as Q1/Q2 evidence, and should keep M8/M9/M10 revenue share and named certification as unresolved unless a new issuer reply, filing, original broker PDF or customer/supplier disclosure is obtained.
