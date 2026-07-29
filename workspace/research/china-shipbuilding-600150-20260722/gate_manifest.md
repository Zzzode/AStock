# Gate Manifest

- Case ID: `china-shipbuilding-600150-20260722`
- Report type: single-stock full research with integrated shipbuilding-cycle and order-driven earnings analysis
- Data cutoff: 2026-07-22 CST
- Coverage pack: `workspace/templates/industry-coverage-packs/cyclical.md`
- Required skills: equity-research, reports, supply-chain-research, growth-earnings-model, valuation, research-report-review, pdf
- Required review cycles: R0_evidence, R1_model, R2_draft, R3_render_compliance, R4_final_ic
- Verifiers: case-local verifier, `tools/verify_research_workspace.py` where applicable, and `workspace/research/tools/run_research_gates.py`
- Pass conditions: zero open S-Level, zero open unwaived A-Level, `Model Reproducibility: PASS`, clean MacTeX XeLaTeX build, generic/case verifier PASS, research gate PASS, and no visual blocker
- Downgrade path: `watchlist only / insufficient evidence`, `CONDITIONAL`, or `MECHANICAL_PASS_INSTITUTIONAL_FAIL` when restructuring, order conversion, normalized earnings or original Street coverage is incomplete

## Required Depth Gates

| Gate | Minimum pass evidence |
|---|---|
| evidence_depth | Official filings and restructuring documents, listed-company order/backlog disclosures, exchange data, industry databases and broker evidence are archived with source tiers and limitations. |
| full_chain_depth | Full-chain universe/taxonomy, core-vs-satellite classification, competitive landscape, relationship table, customer audit, company cards, value-chain economics, coverage gaps and chain-earnings bridge are all present and reviewed; machine classification has exactly one valuation parent, 600150.SH. |
| broker_consensus_depth | Broker/date/rating/target/forecast/method/source quality are preserved; weak evidence receives zero valuation weight. |
| model_depth | Actual/pro-forma perimeter and share-count bridge; backlog/price/mix/delivery/recognition/margin/EPS bridge; cash and working-capital consequences. |
| valuation_depth | Business-model matched cycle-adjusted and asset/enterprise-value checks, three scenarios, market-implied expectations, Street comparison and reproducibility audit. |
| secondary_market_depth | Adjustment-labelled continuous daily K-line, dated volume/amount/turnover/circulating-share snapshot, daily margin data, dated Shanghai Connect and fund holdings, and an archived Dragon-Tiger lookback or defined negative query. Strict free float and daily Connect flow may be marked unavailable only with a source-specific boundary. |
| ic_readiness | Current price, action, fair-value range, next-result thresholds, catalysts, invalidation, execution/geopolitical risk and monitoring plan. |

## Pre-publish Self-checklist

- [ ] Evidence depth passed.
- [ ] Full-chain depth and method-specific blockers passed.
- [ ] Broker consensus depth passed.
- [ ] Model depth passed.
- [ ] Valuation depth passed.
- [ ] Secondary-market depth passed.
- [ ] IC readiness passed.
- [ ] R0-R4 review artifacts complete.
- [ ] Generic/case verifier and research gate pass.
- [ ] PDF visual review has no blocking defect.
