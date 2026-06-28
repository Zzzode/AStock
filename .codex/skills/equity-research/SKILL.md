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
Scope → Template Benchmark → Source Governance → Research → House View → Valuation Skill Gate → Exhibit Plan → Write → Render Review → Publish
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

## Phase 2.75: VALUATION SKILL READINESS

The standalone `valuation` skill is the authoritative valuation system for all full research reports. The orchestrator must not hand-roll a simplified valuation table inside `equity-research`; it must run the valuation skill after verified data and house view are available.

Required readiness inputs:
- `data/verified_financials.md`
- `data/verified_market_data.md`
- `data/consensus_analysis.md` or a public broker/consensus snapshot with unavailable fields marked `not disclosed`
- `data/source_registry.md`
- `data/claim_audit.md`
- `analysis/house_view.md`

**Quality gate:** If these files do not exist or are not usable, block valuation and fix the upstream research artifacts first. Do not proceed to risk, exhibit planning, LaTeX writing, or review with a simplified substitute.

## Institutional Depth Requirements

Full research reports must contain these evidence-backed sections. If evidence is unavailable, include a clearly marked "unverified / not found" table rather than omitting the topic. The `valuation` skill owns the valuation package and audit requirements in sections 3-5; use that skill's artifact contract as the source of truth.

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
   - Build a reader-facing broker comparison table for covered tickers whenever public data are available: broker, report date, rating, target price, 2026E/2027E revenue, net profit, EPS, valuation method, implied upside, and source quality.
   - If only abstracts or aggregator pages are available, still publish a clearly labeled `public broker/consensus snapshot` and mark unavailable fields as `not disclosed`; do not replace missing broker assumptions with AStock assumptions.

4. **Financial expectations versus delivery**
   - Include annual/quarterly reported revenue, net profit, margins, capex, backlog/order indicators where available.
   - Include broker forecast ranges for future revenue/net profit/EPS and compare with consensus.
   - State what would count as in-line, beat, or miss for subsequent results.
   - Include a market-expectation bridge: current price, 2026E revenue, expected revenue growth, 2026E net profit/EPS, expected PE/PS/PB or SOTP multiple, expectation-implied target price/fair value, and upside/downside.
   - The expectation bridge must answer what investors are paying for, not only what the company has already delivered. Reports must show whether upside comes from revenue growth, margin expansion, multiple expansion, or a combination.
   - Include a market-implied expectations and sentiment bridge: current price versus intrinsic value, current-implied PE/PS/PB/EV multiple, liquidity/trading-value percentile, momentum or price-action context where available, broker/Street target dispersion, sentiment premium/discount, and the embedded expectation needed to justify the market price.
   - The final research target must triangulate fundamental value, market-implied consensus pricing and broker/Street reference with explicit weights. If market evidence is strong, do not publish a mechanically conservative target or action that ignores observed market consensus; instead disclose the sentiment-supported component and the trigger that would invalidate it.

5. **Complete valuation model, final target price, and upside/downside**
   - Produce a complete final valuation package for every investable or explicitly covered ticker. This is mandatory for all full research reports.
   - Each valuation package must show current price and date, share count, market cap, currency/share class, forecast revenue/net profit/EPS, selected valuation method, core assumptions, bull/base/bear valuation, final target price or fair-value range, implied upside/downside, rating/action, key catalysts, and invalidation conditions.
   - Valuation method selection must match each ticker's business model, lifecycle, profit denominator and balance-sheet structure. Do not force a heterogeneous industry chain into one PE template.
   - For every covered ticker, explicitly state why the primary method is appropriate and include a secondary sanity check. Examples: AI optical-module leaders may use forward PE/PEG; optical chips and scarce precision-device names often need PE plus PS/strategic scarcity checks; fiber/cable, carrier-project and asset-heavy names require PB/EV-EBITDA/PS or SOTP-style blends; network-equipment names require PE plus cash-flow/order-book checks; loss-making or near-zero EPS names must not use PE as the primary method.
   - A target price that comes only from single-quarter annualized EPS multiplied by a sector PE is invalid unless the company is a stable earnings compounder and the section proves seasonality, customer durability and margin sustainability. Method mismatch is an S-Level publication blocker.
   - The reader-facing PDF must include a final valuation summary table that ties together current price, base target price, fair-value range, upside/downside, valuation method, rating/action, and evidence quality for the covered universe.
   - Broker target prices are evidence, not a substitute for AStock's own final valuation. Cite broker targets separately, disclose sell-side bias, and reconcile them against the house valuation.
   - Every full report must compare AStock valuation against broker/Street valuation and market-expectation valuation. The comparison must explain whether AStock is above, below, or in line with Street targets and which assumption drives the gap: 2026E revenue, margin, EPS, growth duration, multiple, or business-model classification.
   - Every full report must separate `intrinsic/fundamental value`, `market-implied sentiment anchor`, `broker/Street anchor`, and `final market-consensus adjusted target`. Reports must show the weights and explain why sentiment deserves high, medium, or low weight for each ticker.
   - If intrinsic value is far below the current price but market-implied evidence is strong, classify the gap as a sentiment premium instead of automatically calling the stock a sell. Use an action such as `Neutral / market-supported watch`, `Event-driven`, or `Hold while validating` unless the report proves the sentiment premium is already breaking.
   - If the inputs are insufficient to compute a defensible target price, label the ticker `insufficient evidence / watchlist only` and exclude it from investable recommendations. Do not publish an investable stance without a current-price-based target price or fair-value range.

6. **Fundamental, news, geopolitics, and policy impact**
   - Analyze demand drivers, policy, export controls, localization, customer capex, supply-chain security, and geopolitical risk.
   - Distinguish structural drivers from short-term news catalysts.

7. **Secondary-market behavior**
   - Discuss market positioning, valuation crowding, momentum/catalyst calendar, liquidity/lockup/technical risk, and sector rotation.
   - If live market data is unavailable, disclose that and use qualitative secondary-market analysis only.

## Phase 3: ANALYZE (Sequential, builds on verified data)

| Agent | Role File | Input | Output File |
|-------|-----------|-------|-------------|
| Valuation Specialist | `.agents/team/valuation-specialist.md` + `valuation` skill | verified financials + verified market data + consensus + source registry + claim audit + house view | `analysis/valuation_model.md` + `analysis/valuation_audit.md` + structured valuation JSON when applicable |
| Risk Analyst | `.agents/team/risk-analyst.md` | all verified data + `analysis/industry_landscape.md` + `data/consensus_analysis.md` (blind spots) | `analysis/risk_framework.md` |
| Exhibit Architect | `.agents/team/exhibit-architect.md` | house view + industry + valuation + risk + source registry | `analysis/exhibit_plan.md` |

**Quality gate:** The valuation skill must complete before risk, exhibit planning, writing, or review. `analysis/valuation_model.md` must contain a complete final valuation table for every investable or covered ticker: current price/date, share count, market cap, forecast revenue/net profit/EPS, method, bull/base/bear values, intrinsic/fundamental value, market-implied sentiment anchor, broker/Street anchor where available, final market-consensus adjusted target price or fair-value range, implied upside/downside, rating/action, catalysts, invalidation, and source/evidence quality. It must also include three-tier targets, seasonality calibration, next-quarter threshold, method bridge, market-expectation bridge, broker/Street comparison, and market-implied sentiment anchor. `analysis/valuation_audit.md` must verify the actual method used (PE, PEG, PS, PB, EV/EBITDA, DCF, SOTP or blend), market cap = price × shares, upside = target/current - 1, scenario bands, and the explicit weights used in the multi-anchor target. A one-size-fits-all PE table across companies with different business models is an S-Level issue. A mechanically conservative target that ignores strong observable market consensus is also an S-Level issue. Target-price tables must cite broker/date/source and separate broker targets from AStock targets. Supply-chain relationship tables must label confidence. `analysis/exhibit_plan.md` must map every strong conclusion to an exhibit. Fix arithmetic, fake precision, missing final valuation outputs, missing exhibits, evidence gaps, method mismatch, and missing market-sentiment bridge before proceeding.

## Phase 4: WRITE (Sequential)

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| LaTeX Writer | `.agents/team/latex-writer.md` | all Phase 1-3 outputs + `.agents/templates/` | `main.tex` + `sections/*.tex` |

Templates:
- `.agents/templates/preamble.tex` — IB-style formatting
- `.agents/templates/report-main.tex` — document skeleton

Report must include a dedicated "Street Consensus" section from `data/consensus_analysis.md`, a dedicated final valuation section/table from valuation skill outputs (`analysis/valuation_model.md` and `analysis/valuation_audit.md`), and all sections listed in "Institutional Depth Requirements".
If source quality is weak, title the section "Publicly Available Research Sentiment" instead of "Street Consensus".

**Narrative quality gate:** The main body must read as institutional equity research, not a PPT deck, chartbook, source digest, or table stack. Each main-body chapter must:

- Open with prose that states the investment question and causal logic before the first table.
- Embed tables and diagrams inside the argument rather than using tables as the argument.
- Include synthesis after every major exhibit cluster explaining the investment implication, valuation consequence, risk, or monitoring action.
- Avoid consecutive table-heavy pages without explanatory prose.
- Keep appendices for source registries and dense audits; do not expose workflow files or repository paths in the reader-facing PDF.

**First-chapter gate:** Chapter 1 must be an investment committee summary. It must include:

- Direct investment conclusion with no meta-writing language.
- Current price, final target price or fair-value range, implied upside/downside, Q2E or next-quarter earnings bridge, ranking, action, and up/down triggers for primary names.
- A clear ranking methodology or weights.
- Definitions of action labels and risk labels in investment-behavior terms.
- Compact tables only; long triggers belong in prose.

**Quality gate:** XeLaTeX compiles without errors, and a text extraction review confirms prose-led chapters with no table-only main-body sections.

**Language gate:** When the requested report language is Chinese, all reader-facing narrative, table descriptions, valuation explanations, risk statements, catalysts, invalidation triggers, and source summaries must be written in Chinese. English is allowed only for proper nouns, ticker names, technical abbreviations, formulas, source titles, URLs, and short bilingual captions. Untranslated English sentences in the main body or appendix are A-Level; untranslated English valuation or recommendation logic is S-Level.

**macOS compiler rule:** Use MacTeX's XeLaTeX toolchain only. If `xelatex` is not on `PATH`, check `/Library/TeX/texbin/xelatex` and run compile commands with `PATH="/Library/TeX/texbin:$PATH"`. Do not try `tectonic`, `typst`, `pdflatex`, `lualatex`, or any other non-MacTeX substitute for project research reports.

## Phase 4.5: RENDERED PDF VISUAL REVIEW

After first compile, render or inspect actual PDF pages. Do not rely only on TeX source.

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| Visual Layout Reviewer | `.agents/team/visual-layout-reviewer.md` | `main.pdf` + rendered page images + source | `visual_review.md` |

**Quality gate:** Clipped diagrams, overlapping tables, unreadable appendices, table-only main-body chapters, or missing exhibits for core conclusions block publication.

**macOS compiler rule:** Use MacTeX's XeLaTeX toolchain only. If `xelatex` is not on `PATH`, check `/Library/TeX/texbin/xelatex` and run compile commands with `PATH="/Library/TeX/texbin:$PATH"`. Do not try `tectonic`, `typst`, `pdflatex`, `lualatex`, or any other non-MacTeX substitute for project research reports.

## Phase 4.5: RENDERED PDF VISUAL REVIEW

After first compile, render or inspect actual PDF pages. Do not rely only on TeX source.

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| Visual Layout Reviewer | `.agents/team/visual-layout-reviewer.md` | `main.pdf` + rendered page images + source | `visual_review.md` |

**Quality gate:** Clipped diagrams, overlapping tables, unreadable appendices, table-only main-body chapters, or missing exhibits for core conclusions block publication.

## Phase 5: REVIEW (Parallel per chapter, iterative)

| Agent | Role File | Input | Output |
|-------|-----------|-------|--------|
| Reviewer (×N) | `.agents/team/reviewer.md` | LaTeX source + verified data as ground truth | `review_log.md` |
| Research Report Reviewer | `.agents/team/research-report-reviewer.md` | rendered PDF + source + data | `review_log.md` |

After review, feed issues back to LaTeX Writer for fixes. **Repeat until zero S-level issues.**

**Quality gate:** Zero S-level issues before publish. Any missing valuation skill artifact (`analysis/valuation_model.md`, `analysis/valuation_audit.md`, or structured valuation JSON when the case uses a data room), missing complete final valuation model, missing current-price-based target price/fair-value range, missing implied upside/downside, missing market-expectation valuation bridge, missing broker/Street comparison when public evidence exists, investable recommendation without valuation support, valuation method that does not fit the ticker's business model, or untranslated English recommendation/valuation logic in a Chinese report is S-Level and blocks publication. Any chapter that reads like a PPT/chartbook page instead of prose-led research must be revised before publish.
Missing market-implied sentiment anchor, missing multi-anchor valuation weights, or an action label that mechanically ignores strong observed market consensus is S-Level for full research reports.

## Phase 6: PUBLISH

```bash
.venv/bin/python -m astock.cli build-pdf workspace/research/<topic-slug>-<YYYYMMDD>/
# If macOS PATH has not loaded MacTeX:
PATH="/Library/TeX/texbin:$PATH" .venv/bin/python -m astock.cli build-pdf workspace/research/<topic-slug>-<YYYYMMDD>/
```

Verify PDF opens and Chinese renders. Report file location and page count to user.

## Workspace Conventions (authoritative)

The canonical directory structure, file-class semantics (PRIMARY / DERIVED / TEMP), file-naming and file-format rules (incl. Markdown+JSON twins, date/currency conventions, evidence-boundary discipline), `.gitignore` and rendered-PNG version-control policy, audit-artifact refresh dependencies, and the verifier gate are defined in [`workspace/research/RESEARCH_WORKSPACE_CONVENTIONS.md`](../../workspace/research/RESEARCH_WORKSPACE_CONVENTIONS.md). All research-producing agents (data-collector, source-governance-analyst, latex-writer, etc.) MUST follow it. It prevails on any conflict with the quick-reference layout below.

Key rules the orchestrator must enforce:
- `sources/` and `data/raw_*` are PRIMARY non-regenerable evidence — always tracked, never hand-edited.
- LaTeX intermediates (`*.aux .log .out .toc .fls .fdb_latexmk .synctex.gz .xdv .bcf .run.xml`) are TEMP — gitignored, delete after each rebuild.
- Markdown governance files have `.json` twins that MUST stay in sync; after editing either, update the other.
- After any PDF rebuild or governance edit, run `python3 tools/verify_research_workspace.py` — 39 PASS / 0 FAIL is the only acceptable state. See the conventions doc for the full refresh-dependency checklist.

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
