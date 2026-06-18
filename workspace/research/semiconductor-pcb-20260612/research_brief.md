# Research Brief: Semiconductor PCB Industry Chain, New Equity-Research Workflow

**Topic:** 半导体 PCB / AI PCB / CCL / IC 载板产业链投资机会  
**Report Date:** 2026-06-15 rebuild, using source corpus collected on 2026-06-12  
**Language:** Chinese body with English abstract  
**Depth:** Full sector report, focused on investable A-share opportunities  
**Primary Source Folder:** `workspace/research/semiconductor-pcb-20260612/data/`
**Workflow:** new `equity-research` pipeline: template benchmark, source governance, house view, exhibit plan, valuation audit, rendered review, research review.

## Scope

This rebuild deletes the legacy LaTeX/PDF outputs and rebuilds the report around a house view rather than a broker-summary narrative. The report studies whether AI server architecture, high-speed materials, and advanced packaging are making PCB a semiconductor-like interconnect bottleneck.

The required institutional depth sections are:

- Supply-chain relationship matrix with confidence labels.
- Technology principle and architecture explanation.
- Broker rating and target-price history.
- Financial expectations versus delivery.
- Investment guidance and scenario framework.
- Fundamental, news, geopolitics, and policy impact.
- Secondary-market behavior and valuation crowding.

## Core Questions

1. Is the AI PCB cycle a cyclical demand rebound or a structural value-pool migration?
2. Which layers have the best combination of visibility, pricing power, and investability?
3. Where does valuation already discount the bullish case?
4. Which evidence is confirmed, broker-stated, inferred, or unverified?

## Core Ticker Universe

| Segment | Core Names |
|---|---|
| PCB manufacturing | 沪电股份, 胜宏科技, 深南电路, 鹏鼎控股, 景旺电子, 生益电子 |
| CCL / high-speed materials | 生益科技, 华正新材, 南亚新材, 金安国纪, 建滔积层板 |
| IC substrate / packaging substrate | 深南电路, 兴森科技, 华正新材 |
| Equipment and consumables | 大族数控, 芯碁微装, 东威科技（非本报告覆盖ticker）, 凯格精机, 鼎泰高科, 中钨高新 |

## Data Cutoff and Quality

Public source corpus started from the 2026-06-12 seed set and was progressively refreshed through 2026-06-18. The rebuild began on 2026-06-15 and the current evidence state reflects later public-source refresh passes.

The report now uses archived broker abstracts, downloaded broker PDFs, official annual reports, official IR records, public valuation history, holder proxies, public article reproductions, Tencent 2026-06-18 quote refetch evidence, supplier-list/source-lineage probes, issuer-interaction probes, hyperscaler capex evidence, and reverse valuation checks. It still does not cover a complete Wind/Choice-style consensus database, named platform/customer revenue split, customer/platform bottom-up EPS assumptions, or terminal-grade real-time fund-flow positioning. Valuation uses `data/tencent_realtime_market_snapshot_20260618.md` as the latest public quote anchor and keeps older quote snapshots as historical baselines only; all valuation outputs remain indicative and time-sensitive.

## Deliverables

- `analysis/template_brief.md`
- `data/source_registry.md`
- `data/claim_audit.md`
- `analysis/house_view.md`
- `analysis/exhibit_plan.md`
- `analysis/valuation_model.md`
- `analysis/valuation_audit.md`
- `analysis/risk_framework.md`
- `main.tex`, `sections/*.tex`, `main.pdf`
- `visual_review.md`, `review_log.md`
