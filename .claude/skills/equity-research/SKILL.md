---
name: equity-research
description: Institutional equity research report production system. Orchestrates 7 specialist subagents (Data Collector, Data Verifier, Industry Analyst, Valuation Modeler, Risk Analyst, LaTeX Writer, Reviewer) to produce publication-ready LaTeX/PDF reports in Goldman Sachs / Morgan Stanley style. Use when user asks to "write a research report", "equity research", "industry chain analysis", "产业链调研", "写调研报告", "行业研究", or needs to produce institutional-grade investment analysis.
---

# Equity Research — Institutional Report Production System

## Overview

A multi-stage subagent orchestration system that produces institutional-grade equity research reports. Encodes the complete workflow of a top-tier sell-side research team:

```
Research → Verify → Analyze → Write → Review → Publish
```

**Core principles (lessons from production):**
1. Never hallucinate numbers — every data point must have a traceable source
2. Market data is stale within days — always verify against live sources before publication
3. Free-float market cap, trading volumes, and northbound holdings change dramatically around catalysts
4. Sell-side target prices have systematic upward bias of 50-100%
5. ESG/compliance risks are institutional deal-breakers regardless of upside

## When to Use

**Triggers:**
- "帮我写调研报告" / "写一份行业研究"
- "equity research report" / "industry chain analysis"  
- "产业链分析" / "投资调研"
- Any request for institutional-grade investment analysis with PDF output

**Don't use when:**
- Simple stock price lookup (just use web search)
- Quick opinion on a single company (just answer directly)
- Non-financial research reports

## The Process

### Phase 0: SCOPE (You, the orchestrator)

Before dispatching any agents, clarify with the user:
1. **Target sector/theme** — what industry chain or investment theme?
2. **Ticker universe** — which specific companies to cover?
3. **Data cutoff** — what quarter's financials? What date for market data?
4. **Depth** — full report (50+ pages) or brief (15-20 pages)?
5. **Language** — Chinese body + English abstract (default) or full English?

Create a `research_brief.md` in the working directory capturing these decisions.

### Phase 1: RESEARCH (Parallel Subagents)

Dispatch these agents **in parallel** (they have no dependencies):

```
Agent 1: Data Collector (per-company financials)
  → Role: .agents/team/data-collector.md
  → Input: ticker list + data cutoff date
  → Output: structured tables of Q1 revenue, profit, growth rates, key metrics

Agent 2: Data Collector (market data)
  → Role: .agents/team/data-collector.md (market variant)
  → Input: ticker list + today's date
  → Output: current price, market cap, free float, trading volume, northbound holdings

Agent 3: Industry Analyst
  → Role: .agents/team/industry-analyst.md
  → Input: sector theme + competitive landscape questions
  → Output: TAM sizing, competitor matrix, geopolitical risks, policy environment
```

### Phase 2: VERIFY (Parallel, after Phase 1)

Dispatch verification agents **in parallel**:

```
Agent 4: Data Verifier (financials)
  → Role: .agents/team/data-verifier.md
  → Input: Phase 1 financial data
  → Task: Web search EVERY number against official filings (巨潮/交易所PDF)
  → Output: verified data + confidence levels + corrections log

Agent 5: Data Verifier (market data)
  → Role: .agents/team/data-verifier.md (market variant)
  → Input: Phase 1 market data
  → Task: Web search current prices, volumes, northbound from live sources
  → Output: corrected market data table
```

**CRITICAL ANTI-PATTERNS (from this session's learnings):**
- 北向持股: MUST check 深股通/沪股通 actual holding data, not outdated reports
- 自由流通市值: MUST calculate from (total shares - locked shares) × current price
- 日均成交额: MUST use recent 5-7 day window, not 20-day MA from weeks ago
- Catalyst events (like GTC) can inflate volumes 5-10x overnight

### Phase 3: ANALYZE (Sequential, builds on verified data)

```
Agent 6: Valuation Modeler
  → Role: .agents/team/valuation-modeler.md
  → Input: verified financial data + sector PE benchmarks
  → Output: per-ticker valuation (PE/PEG/PS/DCF), three-tier targets, relative comparison table

Agent 7: Risk Analyst
  → Role: .agents/team/risk-analyst.md
  → Input: verified data + industry analysis
  → Output: 22-factor risk matrix, ESG/HRF screening, Devil's Advocate (7 counter-arguments), stress test matrix
```

### Phase 4: WRITE (Sequential, uses templates)

```
Agent 8: LaTeX Writer
  → Role: .agents/team/latex-writer.md
  → Input: all Phase 1-3 outputs + .agents/templates/
  → Task: Write each chapter as separate .tex file, compile PDF
  → Output: main.tex + sections/*.tex + compiled PDF
```

The writer uses:
- `.agents/templates/preamble.tex` — professional IB-style setup
- `.agents/templates/report-main.tex` — document skeleton with cover page
- `references/chart-patterns.md` — pgfplots/TikZ/forest code snippets

### Phase 5: REVIEW (Parallel per chapter, iterative)

```
Agent 9-N: Reviewer (one per 2-3 chapters)
  → Role: .agents/team/reviewer.md
  → Input: LaTeX source + original data + checklists/review-criteria.md
  → Task: Check data accuracy, professional standards, completeness
  → Output: issue list with severity (S/A/B) and specific fix instructions
```

After review, feed issues back to LaTeX Writer agent for fixes. Repeat until all chapters pass.

**Review checklist priorities (from this session):**
1. S-level: Data errors (wrong numbers, wrong units, stale market data)
2. S-level: Missing compliance disclosures (BIS, ESG red flags, 澄清公告)
3. A-level: Missing companies/tickers in tables that should be comprehensive
4. A-level: Charts/tables that contradict each other within the same report
5. B-level: Formatting, style, terminology consistency

### Phase 6: PUBLISH

1. Compile: `.venv/bin/python -m astock.cli build-pdf workspace/research/<topic-slug>-<YYYYMMDD>/`
2. Verify PDF opens correctly and Chinese renders
3. Report file location and page count to user

## File Outputs

```
{working_directory}/
├── research_brief.md              # Scope decisions
├── data/
│   ├── raw_financials.md          # Phase 1 output
│   ├── raw_market_data.md         # Phase 1 output
│   ├── verified_financials.md     # Phase 2 output
│   └── verified_market_data.md    # Phase 2 output
├── analysis/
│   ├── industry_landscape.md      # Phase 3 output
│   ├── valuation_model.md         # Phase 3 output
│   └── risk_framework.md          # Phase 3 output
├── main.tex                       # Phase 4 output
├── sections/
│   ├── ch01_summary.tex
│   ├── ch02_*.tex
│   └── ...
├── main.pdf                       # Final output
└── review_log.md                  # Phase 5 issues and resolutions
```

## Quality Gates

Each phase has a quality gate before proceeding:

| Phase | Gate | Fail action |
|-------|------|-------------|
| Research | All tickers have Q1 data | Re-run collector for missing tickers |
| Verify | >95% of numbers confirmed | Flag unconfirmed as "⚠️ unverified" |
| Analyze | Valuation math checks (PE = price/EPS) | Fix arithmetic |
| Write | XeLaTeX compiles without errors | Fix LaTeX syntax |
| Review | Zero S-level issues | Mandatory fix before publish |

## Customization

The skill adapts to different report types:

| Type | Depth | Agents used | Output |
|------|-------|-------------|--------|
| Full research report | 40-60 pages | All 7 roles | Complete PDF |
| Quick sector note | 10-15 pages | Collector + Analyst + Writer | Brief PDF |
| Data verification only | N/A | Collector + Verifier | Markdown tables |
| Valuation update | 5-10 pages | Collector + Modeler + Writer | Focused PDF |

## Anti-Patterns Registry

Hard-won lessons from production sessions. The Verifier and Reviewer agents MUST check for these:

```yaml
anti_patterns:
  stale_market_data:
    symptom: "Free-float market cap wildly wrong (e.g., 960亿 for a 7800亿 stock)"
    cause: "Using data from months ago without updating for price appreciation"
    fix: "Always calculate: current price × (total shares - locked shares)"
    
  northbound_fantasy:
    symptom: "北向持股4.7%顶格 when actual is 1.8%"
    cause: "Copying from outdated research reports instead of checking 深/沪股通"
    fix: "Web search '[ticker] 深股通持股' for real-time data"
    
  volume_regime_change:
    symptom: "Daily volume 35亿 when actual is 150亿"
    cause: "Using 20-day MA from before a major catalyst event"
    fix: "Use 5-7 day recent window; note if catalyst-inflated"
    
  sell_side_bias:
    symptom: "Treating 券商目标价 as reliable targets"
    cause: "Not understanding systematic upward bias"
    fix: "Always note: sell-side targets have 50-100% upward bias (incentive misalignment)"
    
  layer_classification:
    symptom: "Putting 智微智能(L2仿真) in L4(执行终端)"
    cause: "Confusing company's product category with its industry chain position"
    fix: "Classify by what the company DOES in the value chain, not what it sells to end users"
    
  missing_compliance:
    symptom: "Only writing 'BIS实体清单' without full details"
    cause: "Abbreviating critical compliance information for space"
    fix: "ESG/BIS/处罚 information MUST include: date, entity, amount, current status"
```
