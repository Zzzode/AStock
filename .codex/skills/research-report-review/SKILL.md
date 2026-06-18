---
name: research-report-review
description: Use when reviewing an equity research report, industry report, LaTeX/PDF report, or workspace/research deliverable for institutional-quality issues, chapter-by-chapter parallel review, valuation defects, source evidence gaps, compliance risks, and optimization suggestions.
---

# Research Report Review

Review completed research reports through parallel, chapter-scoped subagents using global top-tier equity research standards.

## When to Use

- User asks to review, audit, critique, or improve a research report.
- User points to `workspace/research/<topic>/`, `main.tex`, `main.pdf`, or report sections.
- User wants chapter-by-chapter issues, institutional-quality gaps, or optimization suggestions.

## Required Review Lenses

Run independent read-only reviews across these lenses:

0. **Template benchmark fit**
   - Compare the report against `workspace/templates/global-broker-research/deep_template_analysis.md`.
   - Check whether the selected report archetype matches the output: single-stock note, chartbook, thematic deep dive, annual outlook, macro whitepaper, or capital markets outlook.
1. **Thesis / industry / supply chain**
   - Investment thesis, industry logic, supply-chain mapping, customer relationships, competitive moat, technology architecture.
   - For hardware/semiconductor themes, explicitly check platform chains such as NVIDIA, Google TPU, Amazon Trainium, Intel, SK Hynix/HBM, domestic compute, and networking/optical. Missing chains must be labeled as corpus gaps, not silently omitted.
2. **Valuation / financial model / secondary market**
   - Current price, market cap, target-price history, quarterly bridge, earnings forecasts, scenario valuation, crowding and catalysts.
   - Verify that earnings forecasts and valuation are tied to customer-chain order durability; generic AI demand is insufficient.
3. **Risk / evidence / compliance**
   - Source hierarchy, data quality, rumor isolation, recommendation boundary, geopolitical/policy risk, publishability.
4. **Visual exhibit quality**
   - Inspect rendered PDF pages when available. Core conclusions should be supported by readable figures, heatmaps, timelines, scorecards, or diagrams rather than dense longtables only.
5. **Narrative flow and prose-led structure**
   - Check whether each main-body chapter opens with analytical prose before tables appear.
   - Check whether each major table/exhibit cluster is embedded in text and followed by a synthesis paragraph.
   - Flag any chapter that reads like PPT/chartbook pages, a source digest, or a table stack rather than institutional equity research prose.
6. **First-chapter investment committee quality**
   - Check whether Chapter 1 gives current price, value range, upside/downside, Q2E or next-quarter earnings bridge, ranking, action, and up/down triggers for primary names.
   - Check whether ranking methodology and action labels are explicit.
   - Flag meta-language written for the author rather than the investor, such as "this chapter rewrites", "this report defines", "table should be read as", or "closer to institutional process".

Use `.agents/team/research-report-reviewer.md` as the reviewer role. If this runtime supports subagents, dispatch one reviewer per lens in parallel. If it does not, simulate the same three-lens review sequentially and say subagents were not actually invoked.

## Review Procedure

1. Inspect `main.tex`, section files, `data/report_catalog.md`, `review_log.md`, `sources/`, and generated `main.pdf` metadata if present.
   Also inspect `analysis/template_brief.md`, `analysis/house_view.md`, `analysis/exhibit_plan.md`, `data/source_registry.md`, `data/claim_audit.md`, and `data_room_index.md` if present.
   Raw PDFs, filings, IR records, web captures and failed-source probes should live under the case-scoped `sources/` tree, not under the deprecated global `workspace/reports/` directory.
2. Split chapters by lens:
   - Lens 1: summary, industry logic, technology, supply chain.
   - Lens 2: valuation, broker targets, market data, secondary-market sections.
   - Lens 3: consensus, risk, appendix, evidence and compliance.
3. Each reviewer returns S/A/B findings with exact file/section references and concrete fixes.
4. Merge duplicate findings and order by severity.
5. State publishability: `BLOCKED`, `CONDITIONAL`, or `PASS`.
6. Provide a repair plan, not just criticism.

## Severity Rules

- **S-Level:** blocks publication. Examples: contradictory market-data disclosure, unsupported investment recommendation, bad arithmetic, current-price valuation missing, source hierarchy failure.
- **S-Level:** also includes missing customer-chain matrix, missing customer-chain earnings bridge, or missing claim-audit appendix in platform-driven hardware reports.
- **S-Level:** also includes clipped core diagrams, overlapping tables, unreadable evidence appendices, or missing visual exhibits for valuation/risk/customer-chain conclusions.
- **S-Level:** also includes missing template benchmark, missing house view, missing exhibit plan, or a report that mechanically repeats broker views without AStock's own thesis.
- **S-Level:** also includes table-only treatment of core investment recommendation, valuation, risk, or customer-chain conclusions.
- **A-Level:** must fix before serious use. Examples: generic supply chain, weak technical parameters, no quarterly bridge, no geopolitical path.
- **A-Level:** includes main-body chapters that are table-led rather than prose-led, have consecutive exhibits without analytical text, or lack post-exhibit "so what" synthesis.
- **A-Level:** includes a first chapter that lacks price anchors, ranking methodology, next-quarter bridge, or actionable investment behavior.
- **B-Level:** polish. Examples: wording, table readability, diagram clarity.

## Output Format

```markdown
## Executive Verdict
- Publishability:
- Top blockers:

## S-Level Issues
1. [file:line] Issue
   Fix:

## A-Level Issues
...

## B-Level Issues
...

## Chapter-by-Chapter Notes
...

## Repair Plan
1. ...
```

## Constraints

- Review only unless user explicitly asks to fix.
- Do not flatter the report. Assume issues exist.
- Do not treat media reposts, previews, or search snippets as full broker evidence.
- Do not call something undervalued/overvalued without current price, market cap, and forecast bridge.
- Do not pass a report whose main body is a source digest rather than a house view supported by exhibits.
- Do not pass a report whose main body reads like a PPT deck or chartbook. Appendices may be dense; main chapters must be prose-led.
- Preserve project policy: research deliverables are LaTeX/PDF compiled with MacTeX XeLaTeX on macOS.
