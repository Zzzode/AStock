# Gate Manifest

| Field | Value |
|---|---|
| case_id | a-share-double-upside-screen-20260722 |
| report_type | full-market opportunity screen with multi-stock valuation capsules |
| data_cutoff | 2026-07-22 |
| coverage_pack | custom cross-sectional high-upside screen |
| required_skills | equity-research; reports; operating-driver research; growth-earnings-model; valuation; research-report-review; pdf |
| review_cycles | R0_evidence; R1_model; R2_draft; R3_render_compliance; R4_final_ic |
| verifiers | case-local verifier; workspace/research/tools/run_research_gates.py |
| pass_conditions | zero open S-Level; zero open unwaived A-Level; score at least 90; Model Reproducibility PASS; PDF and visual review PASS |
| downgrade_path | watchlist only, evidence memo, or no-qualified-double conclusion |

## Required Artifacts

`research_brief.md`, `artifact_contract.md/json`, `analysis/template_brief.md`, verified market and financial packets, source registry, claim audit, source exhaustion log, broker/Street packet, company cards, driver economics, growth model, house view, variant perception, valuation model and audit, risk framework, exhibit plan, narrative blueprint, LaTeX/PDF deliverable, R0-R4 reviews, workflow evaluation, and final sign-off.

## Depth Gates

- evidence_depth
- broker_consensus_depth
- model_depth
- valuation_depth
- ic_readiness

## Pre-Publish Self-Checklist

- [ ] Every deep-model ticker has a current 2026-07-22 price, share count, market cap, and source timestamp.
- [ ] Every material H1 preview and earnings bridge is tied to an official filing or archived original evidence.
- [ ] Every bull-case double has explicit operating assumptions and a year-end catalyst path.
- [ ] Every base target, bull target, and implied upside recalculates from disclosed inputs.
- [ ] Low-base, holding-company, cyclical, and one-off denominators use the valuation recovery loop.
- [ ] Weak broker evidence has zero Street weight.
- [ ] Rejected false positives are visible to the reader.
- [ ] No open S-Level or unwaived A-Level issues remain.
- [ ] Latest PDF has been rendered and inspected.
- [ ] Case verifier, research gate, workflow eval, and final sign-off all pass.
