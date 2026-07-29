# Gate Manifest

| Field | Control |
|---|---|
| Case ID | `a-share-rotation-semi-healthcare-power-20260726` |
| Report type | Evidence memo / thematic investment research; formally downgraded from a full thematic deep dive because the core valuation pool is empty. |
| Data cutoff | 2026-07-24 market close; FY2025, 2026Q1 and official 2026H1 updates available by 2026-07-26 |
| Coverage pack | Custom: semiconductor + healthcare + power-equipment extension |
| Required skills | equity-research, reports, supply-chain-research, growth-earnings-model where AI/high-growth valuation credit is used, valuation, pdf, research-report-review |
| Required review cycles | R0 evidence, R1 model, R2 draft, R3 render/compliance, R4 final IC |
| Verifiers | case-local generic verifier, case-local industry-chain verifier, repo gate runner, workflow-quality evaluator |
| Depth gates | evidence depth; broker-consensus depth; model depth; valuation depth; IC readiness |
| Downgrade path | unsupported ticker → watchlist only; incomplete core broker/earnings/valuation evidence → conditional or evidence memo, never an investable PASS |

## Pre-publish self-checklist

- [ ] Evidence depth: source registry, claim audit, source exhaustion, complete chain universe, and verified financial / market evidence.
- [ ] Broker-consensus depth: dated source-quality-labelled coverage for every final core ticker, or an explicit downgrade.
- [ ] Model depth: value-chain economics and ticker-level revenue, margin and EPS bridges.
- [ ] Valuation depth: reproducible current-price base/bull/bear valuation with market and Street anchors.
- [ ] IC readiness: ranked action, catalysts, invalidation, risk budget, no open S or unwaived A findings, score at least 90.

## Pass Conditions

1. All custom-pack chain blocks are covered or explicitly recorded in the coverage-gap matrix.
2. Every final core ticker has source-governed evidence, a company card, relationship rows, earnings bridge and a method-appropriate valuation.
3. No open S-Level or unwaived A-Level review finding remains.
4. `Model Reproducibility: PASS`; generic and industry-chain verifiers pass; workflow evaluation is publishable with zero blockers.
5. Final sign-off records a publishability score of at least 90 and no material residual-risk conflict.
