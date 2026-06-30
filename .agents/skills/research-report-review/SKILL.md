---
name: research-report-review
description: Use when reviewing an equity research report, industry report, LaTeX/PDF report, or workspace/research deliverable for institutional-quality issues, chapter-by-chapter parallel review, valuation defects, source evidence gaps, compliance risks, and optimization suggestions.
---

# Research Report Review

Review research reports through staged, read-only, maker-checker separated review cycles using global top-tier equity research standards. This skill is the authoritative review workflow for `equity-research`; it must run before publication and whenever a user asks to audit, review, or repair a research case.

## When to Use

- User asks to review, audit, critique, or improve a research report.
- User points to `workspace/research/<topic>/`, `main.tex`, `main.pdf`, or report sections.
- User wants chapter-by-chapter issues, institutional-quality gaps, or optimization suggestions.

## Required Review Lenses

Run independent read-only reviews across these lenses. The active cycle determines which lenses are mandatory:

0. **Template benchmark fit**
   - Compare the report against `workspace/templates/global-broker-research/deep_template_analysis.md`.
   - Check whether the selected report archetype matches the output: single-stock note, chartbook, thematic deep dive, annual outlook, macro whitepaper, or capital markets outlook.
1. **Thesis / industry / supply chain**
   - Investment thesis, industry logic, supply-chain mapping, customer relationships, competitive moat, technology architecture.
   - Verify the standalone `supply-chain-research` skill was used for full industry-chain reports: `data/full_chain_universe_<YYYYMMDD>.md/json`, `analysis/full_chain_taxonomy.md`, `analysis/core_vs_satellite_universe.md`, `analysis/coverage_gap_matrix.md`, `analysis/supply_chain_model.md`, `analysis/company_fundamental_cards.md`, `analysis/value_chain_economics.md`, `analysis/chain_earnings_bridge.md`, `data/supply_chain_relationships.md/json`, and `data/customer_chain_audit.md/json` must exist.
   - Verify the selected industry coverage pack is cited in `analysis/template_brief.md` and every required block is either covered or listed in `analysis/coverage_gap_matrix.md`.
   - Verify the full-chain universe includes non-listed / overseas / private / demand-anchor / low-purity / unavailable nodes where relevant, not only listed tickers.
   - Verify every universe row has `node_type`, chain block, evidence status, source count, core/satellite/demand-anchor classification, valuation status, and next verification path.
   - Verify every covered ticker has a company card and relationship row with layer, upstream input, product/process, downstream customer/platform/application, confidence, revenue exposure, capacity/certification/order visibility, margin/earnings impact, source, evidence gap, and valuation eligibility.
   - Verify `analysis/competitive_landscape.md` covers global and China leaders, CR3/CR5 when available, localization boundary, substitution risk, and evidence quality.
   - Verify `analysis/value_chain_economics.md` covers value amount, ASP/price proxy, margin pool, supply/demand, capacity/utilization/yield, certification/customer qualification, order visibility, and valuation credit.
   - For hardware/semiconductor themes, explicitly check platform chains such as NVIDIA, Google TPU, Amazon Trainium, Intel, SK Hynix/HBM, domestic compute, and networking/optical. Missing chains must be labeled as corpus gaps, not silently omitted.
2. **Valuation / financial model / secondary market**
   - Verify the standalone `valuation` skill was used: `analysis/valuation_model.md` and `analysis/valuation_audit.md` must exist, and structured valuation JSON should exist when the case uses a data room.
   - Verify `analysis/valuation_audit.md` contains `Model Reproducibility: PASS`; otherwise valuation is not publishable.
   - When high-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP valuation credit is used, verify the standalone `growth-earnings-model` skill was used: `analysis/growth_earnings_model.md`, `analysis/segment_forecast_bridge.md`, `analysis/implied_growth_sensitivity.md`, and `data/growth_driver_model.json` must exist.
   - Current price, market cap, share count, target-price history, quarterly bridge, earnings forecasts, scenario valuation, final target price or fair-value range, implied upside/downside, crowding and catalysts.
   - Verify every investable or covered ticker has a complete AStock final valuation package: current price/date, market cap, forecast EPS/net profit, valuation method, bull/base/bear values, final target, upside/downside, rating/action, catalysts, invalidation, and evidence quality.
   - Verify every high-growth valuation claim has a base/growth split, unit/order/ASP/proxy bridge, recognized revenue ratio, gross margin, incremental opex, net profit/EPS contribution, scenario sensitivity, current-price-implied growth, evidence gaps, and valuation credit classification.
   - Verify that earnings forecasts and valuation are tied to customer-chain order durability; generic AI demand is insufficient.
3. **Risk / evidence / compliance**
   - Source hierarchy, data quality, rumor isolation, recommendation boundary, geopolitical/policy risk, publishability.
   - Verify `source_exhaustion_log.md/json` exists and records failed probes, paywalls, abstracts-only situations, inaccessible sources, and next verification paths.
   - Verify `data/consensus_analysis.md` labels source quality for broker evidence and does not present media reposts, previews, or search snippets as full broker reports.
   - Verify `analysis/variant_perception.md` states consensus view, AStock's differentiated view, strongest opposing argument, falsification evidence, and monitoring triggers.
4. **Visual exhibit quality**
   - Inspect rendered PDF pages when available. Core conclusions should be supported by readable figures, heatmaps, timelines, scorecards, or diagrams rather than dense longtables only.
5. **Narrative flow and prose-led structure**
   - Check whether each main-body chapter opens with analytical prose before tables appear.
   - Check whether each major table/exhibit cluster is embedded in text and followed by a synthesis paragraph.
   - Flag any chapter that reads like PPT/chartbook pages, a source digest, or a table stack rather than institutional equity research prose.
6. **First-chapter investment committee quality**
   - Check whether Chapter 1 gives current price, final target price or fair-value range, upside/downside, Q2E or next-quarter earnings bridge, ranking, action, and up/down triggers for primary names.
   - Check whether ranking methodology and action labels are explicit.
   - Flag meta-language written for the author rather than the investor, such as "this chapter rewrites", "this report defines", "table should be read as", or "closer to institutional process".

Use `.agents/team/research-report-reviewer.md` as the reviewer role. If this runtime supports subagents, dispatch one reviewer per lens in parallel. If it does not, simulate the same review sequentially and say subagents were not actually invoked.

## Review Cycles

| Cycle | Timing | Required Lenses | Output |
|---|---|---|---|
| `R0_evidence` | Before synthesis or drafting | template benchmark, source hierarchy, full-chain universe, coverage gaps, source exhaustion, claim audit | `review_findings_R0_evidence.json`, `repair_plan_R0_evidence.md/json` |
| `R1_model` | Before drafting | growth model, value-chain economics, valuation model, valuation audit, current-price dependencies | `review_findings_R1_model.json`, `repair_plan_R1_model.md/json` |
| `R2_draft` | After draft | thesis, narrative, IC summary, chapter logic, evidence integration, language | `review_findings_R2_draft.json`, `repair_plan_R2_draft.md/json` |
| `R3_render_compliance` | After PDF build | rendered visual quality, compliance, source appendix, generic verifier, industry-chain verifier when applicable | `review_findings_R3_render_compliance.json`, `repair_plan_R3_render_compliance.md/json` |
| `R4_final_ic` | Before publication | issue closure, waivers, publishability score, residual risks, final sign-off | `review_findings_R4_final_ic.json`, `final_signoff.md/json` |

The reviewer is read-only. It does not repair files. It writes findings, repair plans, and final sign-off only after verifying current artifacts.

## Review Procedure

1. Inspect `gate_manifest.md/json`, `artifact_contract.md/json`, `research_brief.md`, `main.tex`, section files, `data/report_catalog.md`, `review_log.md`, `sources/`, and generated `main.pdf` metadata if present.
   Also inspect `analysis/template_brief.md`, `analysis/house_view.md`, `analysis/variant_perception.md`, `analysis/full_chain_taxonomy.md`, `analysis/core_vs_satellite_universe.md`, `analysis/coverage_gap_matrix.md`, `analysis/supply_chain_model.md`, `analysis/company_fundamental_cards.md`, `analysis/value_chain_economics.md`, `analysis/chain_earnings_bridge.md`, `analysis/competitive_landscape.md`, `analysis/growth_earnings_model.md`, `analysis/segment_forecast_bridge.md`, `analysis/implied_growth_sensitivity.md`, `analysis/valuation_model.md`, `analysis/valuation_audit.md`, `analysis/exhibit_plan.md`, `analysis/narrative_blueprint.md`, `data/full_chain_universe_<YYYYMMDD>.json`, `data/supply_chain_relationships.md/json`, `data/customer_chain_audit.md/json`, `data/growth_driver_model.json`, `data/source_registry.md/json`, `data/claim_audit.md/json`, `source_exhaustion_log.md/json`, `data/current_valuation_model_<YYYYMMDD>.json` if present, `review_findings_*.json`, `repair_plan_*.md/json`, `final_signoff.md/json`, and `data_room_index.md` if present.
   Raw PDFs, filings, IR records, web captures and failed-source probes should live under the case-scoped `sources/` tree, not under the deprecated global `workspace/reports/` directory.
2. Split chapters by lens:
   - Lens 1: summary, industry logic, technology, supply chain.
   - Lens 2: valuation, broker targets, market data, secondary-market sections.
   - Lens 3: consensus, risk, appendix, evidence and compliance.
3. Each reviewer returns S/A/B findings with exact file/section references and concrete fixes.
4. Merge duplicate findings and order by severity.
5. Write `review_findings_<cycle>.json`.
6. Write `repair_plan_<cycle>.md/json` unless the cycle is `R4_final_ic` and all gates pass.
7. State publishability: `BLOCKED`, `CONDITIONAL`, or `PASS`, plus a numeric publishability score from 0 to 100 using the scoring rubric below.
8. If the review is triggered by user feedback about a missing chain block, missing ticker, weak evidence, or bad structure, require `analysis/delta_audit.md` and check that it maps the correction to a skill/role prevention rule.

## Finding and Repair Schema

`review_findings_<cycle>.json` must contain:

```json
{
  "cycle": "R0_evidence",
  "publishability_status": "BLOCKED",
  "publishability_score": 0,
  "findings": [
    {
      "issue_id": "R0-S-001",
      "severity": "S",
      "owner_skill": "supply-chain-research",
      "owner_agent": "supply-chain-analyst",
      "artifact": "data/full_chain_universe_<YYYYMMDD>.json",
      "evidence": "missing node_type in row 4",
      "fix_required": "add node_type and rerun full-chain gate",
      "blocking_gate": "full_chain_universe",
      "status": "open",
      "verifier_ref": "industry_chain_verify_research_workspace.py",
      "reopened_count": 0
    }
  ]
}
```

`repair_plan_<cycle>.json` must group open S-Level and A-Level issues by `owner_skill` and list exact artifacts to regenerate. Repairs are complete only after the same cycle re-runs and marks issues `verified` or `closed`.

Lifecycle: `open -> fixed -> verified -> closed` or `open -> waived`. S-Level issues are not waivable unless the user explicitly instructs a waiver and the final sign-off records residual risk. A-Level waiver requires waiver reason, residual risk, and approver. B-Level issues may remain open only if final sign-off lists them.

## Publishability Score Rubric

Start from 100 and subtract:

| Condition | Deduction |
|---|---:|
| Any open S-Level | Immediate BLOCKED and score capped at 60 |
| Any open unwaived A-Level | Immediate BLOCKED and score capped at 84 |
| Missing required artifact from `gate_manifest` | 15 each |
| Generic verifier failure | 20 |
| Industry-chain verifier failure when required | 20 |
| Missing `Model Reproducibility: PASS` | 20 |
| Weak source-quality labeling or source-exhaustion gap | 10 |
| Narrative/IC summary incomplete | 10 |
| Visual/render issue | 5-15 by severity |

PASS requires score >= 90, zero open S-Level, zero open unwaived A-Level, generic verifier PASS, industry-chain verifier PASS when required, and `final_signoff.md/json`.
CONDITIONAL is for internal drafts only; published reports cannot be CONDITIONAL.

## Severity Rules

- **S-Level:** blocks publication. Examples: contradictory market-data disclosure, unsupported investment recommendation, bad arithmetic, current-price valuation missing, final target price/fair-value range missing for an investable ticker, implied upside/downside missing, source hierarchy failure.
- **S-Level:** also includes missing customer-chain matrix, missing customer-chain earnings bridge, or missing claim-audit appendix in platform-driven hardware reports.
- **S-Level:** also includes missing standalone `supply-chain-research` artifacts in a full industry-chain report, or a concept-stock table that bypasses the supply-chain skill contract.
- **S-Level:** also includes missing full-chain universe, missing industry coverage pack citation, missing `node_type`, missing core/satellite/demand-anchor classification, or missing coverage gap matrix in a full industry-chain report.
- **S-Level:** also includes missing `analysis/value_chain_economics.md` or `analysis/competitive_landscape.md` in a full industry-chain report.
- **S-Level:** also includes missing `source_exhaustion_log.md/json`, missing broker source-quality labels, or treating search snippets/media reposts as original broker reports.
- **S-Level:** also includes missing `analysis/variant_perception.md` or a house view that lacks the strongest opposing argument.
- **S-Level:** also includes missing standalone `growth-earnings-model` artifacts when high-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP valuation credit is used.
- **S-Level:** also includes clipped core diagrams, overlapping tables, unreadable evidence appendices, or missing visual exhibits for valuation/risk/customer-chain conclusions.
- **S-Level:** also includes missing template benchmark, missing house view, missing exhibit plan, or a report that mechanically repeats broker views without AStock's own thesis.
- **S-Level:** also includes table-only treatment of core investment recommendation, valuation, risk, or customer-chain conclusions.
- **S-Level:** also includes any full report that lacks a reader-facing final valuation summary table tying current price, AStock target/fair-value range, upside/downside, method, rating/action, and evidence quality across the covered universe.
- **S-Level:** also includes missing standalone valuation skill artifacts, missing valuation audit, or a valuation table created inside the report that bypasses the valuation skill contract.
- **S-Level:** also includes missing `Model Reproducibility: PASS` in `analysis/valuation_audit.md`.
- **S-Level:** also includes generic AI demand, downstream TAM, capacity, market heat, or one strong quarter converted into EPS or target-price upside without unit/order/ASP/proxy-to-EPS math.
- **S-Level:** also includes applying high-growth multiples to consolidated revenue or profit when only one segment has evidence-backed growth and segment purity is not proven.
- **A-Level:** must fix before serious use. Examples: generic supply chain, weak technical parameters, no quarterly bridge, no geopolitical path.
- **A-Level:** includes growth-earnings outputs that omit current-price-implied growth, scenario sensitivity, valuation credit classification, evidence gaps, or next-quarter validation thresholds.
- **A-Level:** includes main-body chapters that are table-led rather than prose-led, have consecutive exhibits without analytical text, or lack post-exhibit "so what" synthesis.
- **A-Level:** includes a first chapter that lacks price anchors, ranking methodology, next-quarter bridge, or actionable investment behavior.
- **A-Level:** includes a publishability score below 90/100 even if no single S-Level issue remains.
- **B-Level:** polish. Examples: wording, table readability, diagram clarity.

## Output Format

```markdown
## Executive Verdict
- Publishability:
- Publishability Score:
- Review Cycle:
- Open S-Level:
- Open A-Level:
- Verifier Summary:
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

For `R4_final_ic`, write `final_signoff.md/json` only when every pass condition is met. It must include:

```text
case_id | report_type | data_cutoff | pdf_path | page_count | publishability_score | verifier_results | industry_chain_verifier_results | open_s_count | open_a_count | waived_issues | residual_risks | downgrade_status | signoff_status
```

## Constraints

- Review only unless user explicitly asks to fix.
- Do not flatter the report. Assume issues exist.
- Do not treat media reposts, previews, or search snippets as full broker evidence.
- Do not call something undervalued/overvalued without current price, market cap, and forecast bridge.
- Do not pass any investable recommendation unless it has a complete current-price-based valuation model, final target price or fair-value range, and implied upside/downside.
- Do not pass a full industry-chain report unless it has the required supply-chain skill artifacts or clearly labels the report as a non-investable quick screen.
- Do not pass a report that turns high-growth, AI, order, shipment, ASP, customer-allocation, segment-mix, PEG/PSG, or PS/SOTP claims into valuation upside without the required growth earnings artifacts.
- Do not pass a report whose main body is a source digest rather than a house view supported by exhibits.
- Do not pass a report whose main body reads like a PPT deck or chartbook. Appendices may be dense; main chapters must be prose-led.
- Do not pass any report with open S-Level issues, open unwaived A-Level issues, publishability score below 90, missing final sign-off, or failing verifier.
- Do not mark a repair complete from the author's assertion; re-read the artifact and rerun the relevant review cycle.
- Preserve project policy: research deliverables are LaTeX/PDF compiled with MacTeX XeLaTeX on macOS.
