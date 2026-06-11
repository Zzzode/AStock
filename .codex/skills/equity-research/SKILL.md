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
Scope → Research → Verify → Analyze → Write → Review → Publish
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

## Phase 1: RESEARCH (Parallel)

Dispatch **in parallel** — no dependencies between them:

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Data Collector (financials) | `.agents/team/data-collector.md` | ticker list + data cutoff date, mode=financials | `data/raw_financials.md` |
| Data Collector (market) | `.agents/team/data-collector.md` | ticker list + today's date, mode=market | `data/raw_market_data.md` |
| Industry Analyst | `.agents/team/industry-analyst.md` | sector theme + competitive questions | `analysis/industry_landscape.md` |
| Report Collector | `.agents/team/report-collector.md` | sector/ticker + date_range=last_90d + min_reports=10 | `data/report_catalog.md` |

**Quality gate:** All tickers have data. If any ticker is missing, re-run collector for that ticker.

## Phase 2: VERIFY (Parallel, after Phase 1)

Dispatch **in parallel**:

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Data Verifier (financials) | `.agents/team/data-verifier.md` | `data/raw_financials.md` | `data/verified_financials.md` |
| Data Verifier (market) | `.agents/team/data-verifier.md` | `data/raw_market_data.md` | `data/verified_market_data.md` |
| Report Analyzer | `.agents/team/report-analyzer.md` | `data/report_catalog.md` | `data/consensus_analysis.md` |

**Quality gate:** >95% of numbers confirmed. Unconfirmed items flagged as "⚠️ unverified".

## Phase 3: ANALYZE (Sequential, builds on verified data)

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Valuation Modeler | `.agents/team/valuation-modeler.md` | `data/verified_financials.md` + `data/verified_market_data.md` + `data/consensus_analysis.md` | `analysis/valuation_model.md` |
| Risk Analyst | `.agents/team/risk-analyst.md` | all verified data + `analysis/industry_landscape.md` + `data/consensus_analysis.md` (blind spots) | `analysis/risk_framework.md` |

**Quality gate:** Valuation math checks (PE = price/EPS). Fix arithmetic before proceeding.

## Phase 4: WRITE (Sequential)

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| LaTeX Writer | `.agents/team/latex-writer.md` | all Phase 1-3 outputs + `.agents/templates/` | `main.tex` + `sections/*.tex` |

Templates:
- `.agents/templates/preamble.tex` — IB-style formatting
- `.agents/templates/report-main.tex` — document skeleton

Report must include a dedicated "Street Consensus" section from `data/consensus_analysis.md`.

**Quality gate:** XeLaTeX compiles without errors.

## Phase 5: REVIEW (Parallel per chapter, iterative)

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| Reviewer (×N) | `.agents/team/reviewer.md` | LaTeX source + verified data as ground truth | `review_log.md` |

After review, feed issues back to LaTeX Writer for fixes. **Repeat until zero S-level issues.**

**Quality gate:** Zero S-level issues before publish.

## Phase 6: PUBLISH

```bash
.venv/bin/python -m astock.cli build-pdf workspace/research/<topic-slug>-<YYYYMMDD>/
```

Verify PDF opens and Chinese renders. Report file location and page count to user.

## File Outputs

```
workspace/research/<topic-slug>-<YYYYMMDD>/
├── research_brief.md
├── data/
│   ├── raw_financials.md
│   ├── raw_market_data.md
│   ├── report_catalog.md
│   ├── verified_financials.md
│   ├── verified_market_data.md
│   └── consensus_analysis.md
├── analysis/
│   ├── industry_landscape.md
│   ├── valuation_model.md
│   └── risk_framework.md
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
