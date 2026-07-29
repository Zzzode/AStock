# Gate Manifest

- Case ID: `hengyi-petrochemical-000703-20260722`
- Report type: single-stock full research with integrated cyclical business analysis
- Data cutoff: 2026-07-22 CST
- Research framework: `workspace/templates/industry-coverage-packs/cyclical.md`
- Required skills: equity-research, reports, valuation, research-report-review, pdf
- Review cycles: R0 evidence, R1 model, R2 draft, R3 render/compliance, R4 final IC
- Verifiers: case-local verifier and `workspace/research/tools/run_research_gates.py`
- Pass conditions: zero open S-Level, zero open unwaived A-Level, model reproducibility PASS, clean XeLaTeX build, case verifier PASS, research gate PASS, and no visual blocker
- Downgrade path: watchlist only / insufficient evidence or CONDITIONAL when original Street coverage or normalized earnings evidence is incomplete

## Required Depth Gates

| Gate | Minimum pass evidence |
|---|---|
| evidence_depth | Official filings, Brunei project disclosures, market/industry data and broker PDFs are archived with source tiers and limitations. |
| broker_consensus_depth | Broker/date/rating/target/forecast/method/source quality are preserved; weak evidence receives zero valuation weight. |
| model_depth | Reported-to-normalized earnings bridge separates Brunei, domestic PTA/polyester, financing, tax and minority interests. |
| valuation_depth | SOTP and a business-model-matched secondary check, three scenarios, market-implied expectations and reproducibility audit. |
| ic_readiness | Current price, action, price discipline, next-result thresholds, catalysts, invalidation, leverage risk and monitoring plan. |

## Pre-publish Checklist

- [ ] Evidence depth passed.
- [ ] Broker consensus depth passed.
- [ ] Model depth passed.
- [ ] Valuation depth passed.
- [ ] IC readiness passed.
- [ ] R0-R4 review artifacts complete.
- [ ] Case verifier and research gate pass.
- [ ] PDF visual review has no blocking defect.
