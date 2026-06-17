---
name: equity-research
description: Institutional equity research report production system. Orchestrates team agents to produce publication-ready LaTeX/PDF reports in Goldman Sachs / Morgan Stanley style. Use when user asks to "write a research report", "equity research", "industry chain analysis", "产业链调研", "写调研报告", "行业研究", or needs to produce institutional-grade investment analysis.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Equity Research — Institutional Report Production System

## Overview

A multi-stage orchestration that produces institutional-grade equity research reports. All agent capabilities live in `.agents/team/*.md` — this skill only defines the pipeline: which agents, what order, what inputs flow where.

```
Scope → Template Benchmark → Source Governance → Research → House View → Exhibit Plan → Analyze → Write → Render Review → Publish
```

## When to Use

**Triggers:**
- "帮我写调研报告" / "写一份行业研究"
- "equity research report" / "industry chain analysis"
- "产业链分析" / "投资调研"
- Any request for institutional-grade investment analysis with PDF output

**Don't use when:**
- Simple stock price lookup → `/quote`
- Quick opinion on a single company → `/team`
- Non-financial research reports

## Phase 0: SCOPE (You, the orchestrator)

Before dispatching any agents, clarify with the user:
1. **Target sector/theme** — what industry chain or investment theme?
2. **Ticker universe** — which specific companies to cover?
3. **Data cutoff** — what quarter's financials? What date for market data?
4. **Depth** — full report (50+ pages) or brief (15-20 pages)?
5. **Language** — Chinese body + English abstract (default) or full English?

Create `research_brief.md` in the working directory.

## Phase 0.5: TEMPLATE BENCHMARK

Before collecting data, choose the report archetype and benchmark it against the sample library in `workspace/templates/global-broker-research/`.

| Agent | Role File | Output File |
|-------|-----------|-------------|
| Template Benchmark Analyst | `.agents/team/template-benchmark-analyst.md` | `analysis/template_brief.md` |

Reference archetypes:
- Single-stock note → JPM equity research sample.
- Market guide / chartbook → JPM Guide to the Markets.
- Global outlook in charts → BlackRock BII.
- Annual outlook / house view → Capital Group.
- Macro scenario whitepaper → Vanguard.
- Quarterly capital markets strategy → AllianceBernstein.

**Quality gate:** `analysis/template_brief.md` must define first-page dashboard, required chapter sequence, required exhibits, and what to avoid.

## Phase 1: RESEARCH (Parallel)

Dispatch **in parallel** — no dependencies between them:

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Data Collector (financials) | `.agents/team/data-collector.md` | ticker list + data cutoff date, mode=financials | `data/raw_financials.md` |
| Data Collector (market) | `.agents/team/data-collector.md` | ticker list + today's date, mode=market | `data/raw_market_data.md` |
| Industry Analyst | `.agents/team/industry-analyst.md` | sector theme + competitive questions | `analysis/industry_landscape.md` |
| Report Collector | `.agents/team/report-collector.md` | sector/ticker + date_range=last_90d + min_reports=10 + output_dir=`sources/broker-reports/<YYYY-MM-DD>/` | `data/report_catalog.md` + `sources/broker-reports/<YYYY-MM-DD>/` |
| Source Governance Analyst | `.agents/team/source-governance-analyst.md` | all collected sources | `data/source_registry.md` + `data/claim_audit.md` |

**Quality gate:** All tickers have data. If any ticker is missing, re-run collector for that ticker.
High-impact claims must be classified before they can enter the main report.

## Phase 2: VERIFY (Parallel, after Phase 1)

Dispatch **in parallel**:

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Data Verifier (financials) | `.agents/team/data-verifier.md` | `data/raw_financials.md` | `data/verified_financials.md` |
| Data Verifier (market) | `.agents/team/data-verifier.md` | `data/raw_market_data.md` | `data/verified_market_data.md` |
| Report Analyzer | `.agents/team/report-analyzer.md` | `data/report_catalog.md` | `data/consensus_analysis.md` |

**Quality gate:** >95% of numbers confirmed. Unconfirmed items flagged as "⚠️ unverified".

## Phase 2.5: HOUSE VIEW

The report must have AStock's own thesis. Broker views are evidence, not the report's voice.

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| House View Analyst | `.agents/team/house-view-analyst.md` | verified data + source registry + report catalog | `analysis/house_view.md` |

**Quality gate:** If the house view mostly says “broker X believes,” it fails.

## Institutional Depth Requirements

Full research reports must contain these evidence-backed sections. If evidence is unavailable, include a clearly marked "unverified / not found" table rather than omitting the topic.

1. **Supply-chain relationship matrix**
   - Map upstream/downstream relationships: which company supplies which customer, platform, component, or process.
   - Classify each relationship as `confirmed`, `broker-stated`, `inferred`, or `market-rumor / unverified`.
   - Include revenue exposure, order visibility, margin/earnings impact, and competitive moat where available.

2. **Technology principle and architecture analysis**
   - Explain the technical principle in plain language.
   - Include old-vs-new technology comparison tables.
   - For hardware/material themes, include diagrams such as cross-sections, process flow, BOM layer maps, or architecture schematics.
   - Map each ticker to its technology generation, layer, material grade, process node, or platform generation.

3. **Broker target-price and rating history**
   - Build a time-series table by broker/date/rating/target price/valuation method.
   - Show target-price changes, implied upside/downside, EPS/net-profit assumptions, and whether the broker is bullish, neutral, or cautious.
   - Separate original broker evidence from media summaries and market rumors.

4. **Financial expectations versus delivery**
   - Include annual/quarterly reported revenue, net profit, margins, capex, backlog/order indicators where available.
   - Include broker forecast ranges for future revenue/net profit/EPS and compare with consensus.
   - State what would count as in-line, beat, or miss for subsequent results.

5. **Investment guidance and target framework**
   - Provide a valuation framework and scenario table.
   - Give investment stance by category (core, aggressive, watchlist, avoid/insufficient evidence) with triggers and invalidation conditions.
   - Do not invent target prices. Use broker targets when sourced; otherwise provide scenario logic without a fake target.

6. **Fundamental, news, geopolitics, and policy impact**
   - Analyze demand drivers, policy, export controls, localization, customer capex, supply-chain security, and geopolitical risk.
   - Distinguish structural drivers from short-term news catalysts.

7. **Secondary-market behavior**
   - Discuss market positioning, valuation crowding, momentum/catalyst calendar, liquidity/lockup/technical risk, and sector rotation.
   - If live market data is unavailable, disclose that and use qualitative secondary-market analysis only.

## Phase 3: ANALYZE (Sequential, builds on verified data)

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Valuation Modeler | `.agents/team/valuation-modeler.md` | `data/verified_financials.md` + `data/verified_market_data.md` + `data/consensus_analysis.md` | `analysis/valuation_model.md` |
| Risk Analyst | `.agents/team/risk-analyst.md` | all verified data + `analysis/industry_landscape.md` + `data/consensus_analysis.md` (blind spots) | `analysis/risk_framework.md` |
| Exhibit Architect | `.agents/team/exhibit-architect.md` | house view + industry + valuation + risk + source registry | `analysis/exhibit_plan.md` |
| Valuation Auditor | `.agents/team/valuation-auditor.md` | valuation model + market data + broker targets | `analysis/valuation_audit.md` |

**Quality gate:** Valuation math checks (PE = price/EPS). Target-price tables must cite broker/date/source. Supply-chain relationship tables must label confidence. `analysis/exhibit_plan.md` must map every strong conclusion to an exhibit. Fix arithmetic, fake precision, missing exhibits, and evidence gaps before proceeding.

## Phase 4: WRITE (Sequential)

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| LaTeX Writer | `.agents/team/latex-writer.md` | all Phase 1-3 outputs + `.agents/templates/` | `main.tex` + `sections/*.tex` |

Templates:
- `.agents/templates/preamble.tex` — IB-style formatting
- `.agents/templates/report-main.tex` — document skeleton

Report must include a dedicated "Street Consensus" section from `data/consensus_analysis.md` and all sections listed in "Institutional Depth Requirements".
If source quality is weak, title the section "Publicly Available Research Sentiment" instead of "Street Consensus".

**Quality gate:** XeLaTeX compiles without errors.

**macOS compiler rule:** Use MacTeX's XeLaTeX toolchain only. If `xelatex` is not on `PATH`, check `/Library/TeX/texbin/xelatex` and run compile commands with `PATH="/Library/TeX/texbin:$PATH"`. Do not try `tectonic`, `typst`, `pdflatex`, `lualatex`, or any other non-MacTeX substitute for project research reports.

## Phase 4.5: RENDERED PDF VISUAL REVIEW

After first compile, render or inspect actual PDF pages. Do not rely only on TeX source.

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| Visual Layout Reviewer | `.agents/team/visual-layout-reviewer.md` | `main.pdf` + rendered page images + source | `visual_review.md` |

**Quality gate:** Clipped diagrams, overlapping tables, unreadable appendices, or missing exhibits for core conclusions block publication.

## Phase 5: REVIEW (Parallel per chapter, iterative)

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| Reviewer (×N) | `.agents/team/reviewer.md` | LaTeX source + verified data as ground truth | `review_log.md` |
| Research Report Reviewer | `.agents/team/research-report-reviewer.md` | rendered PDF + source + data | `review_log.md` |

After review, feed issues back to LaTeX Writer for fixes. **Repeat until zero S-level issues.**

**Quality gate:** Zero S-level issues before publish.

## Phase 6: PUBLISH

```bash
.venv/bin/python -m astock.cli build-pdf workspace/research/<topic-slug>-<YYYYMMDD>/
# If macOS PATH has not loaded MacTeX:
PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/<topic-slug>-<YYYYMMDD>/
```

Verify PDF opens and Chinese renders. Report file location and page count to user.

## Case-Scoped Directory Standard

Every deep research case owns its report, analysis outputs, evidence packets, and raw source archive. Do not use the deprecated global `workspace/reports/` directory for new research-source downloads. Put broker PDFs, official filings, IR records, web pages, probes, and failed-source evidence under the current case's `sources/` tree.

Recommended `sources/` subdirectories:

| Directory | Purpose |
|---|---|
| `sources/broker-reports/<YYYY-MM-DD>/` | Initial or ad hoc broker report collection from `/reports`. |
| `sources/broker-core-*`, `sources/broker-watchlist-*`, `sources/broker-original-refresh-*` | Curated sell-side PDFs and extracted text used by the report. |
| `sources/official-*` | Company filings, exchange documents, refinancing documents, monthly revenue, HKEX filing excerpts. |
| `sources/ir-*` | Investor-relations records and official Q&A documents. |
| `sources/probe-*` | Failed source probes, customer-side pages, customs/BOL pages, global-broker access attempts. |

`data/` is for normalized evidence packets, extracted tables, quality gates, and audit manifests. Raw downloaded documents belong in `sources/`, not `data/`.

## File Outputs

```
workspace/research/<topic-slug>-<YYYYMMDD>/
├── research_brief.md
├── data/
│   ├── raw_financials.md
│   ├── raw_market_data.md
│   ├── report_catalog.md
│   ├── source_registry.md
│   ├── claim_audit.md
│   ├── verified_financials.md
│   ├── verified_market_data.md
│   └── consensus_analysis.md
├── analysis/
│   ├── industry_landscape.md
│   ├── valuation_model.md
│   └── risk_framework.md
├── sources/
│   ├── broker-reports/<YYYY-MM-DD>/
│   ├── official-*/
│   ├── ir-*/
│   └── probe-*/
├── main.tex
├── sections/
│   ├── ch01_summary.tex
│   ├── ch02_*.tex
│   └── ...
├── main.pdf
└── review_log.md
```

## Customization

| Type | Depth | Agents Used | Output |
|------|-------|-------------|--------|
| Full research report | 40-60 pages | All roles | Complete PDF |
| Quick sector note | 10-15 pages | data-collector, report-collector, report-analyzer, industry-analyst, latex-writer | Brief PDF |
| Data verification only | N/A | data-collector, data-verifier | Markdown tables |
| Valuation update | 5-10 pages | data-collector, valuation-modeler, latex-writer | Focused PDF |
| Consensus survey | 5-10 pages | report-collector, report-analyzer, latex-writer | Street view PDF |

## Error Handling

| Scenario | Action |
|----------|--------|
| Data Collector returns partial data | Re-run for missing tickers; proceed with available if re-run also fails |
| Report Collector finds <3 reports | Note "limited sell-side coverage" in report; proceed without consensus section |
| Verifier flags >20% errors | Re-run Phase 1 collectors with corrected queries |
| LaTeX compilation fails | LaTeX Writer fixes syntax; retry up to 3 times |
| Reviewer finds S-level issues | Mandatory fix cycle before publish; max 3 iterations |
