# Gate Manifest

| Field | Contract |
|---|---|
| Case ID | `huawei-atlas-950-superpod-20260718` |
| Report type | Full industry-chain deep dive |
| Data cutoff | 2026-07-17 market close; FY2025 and 2026Q1 reported financials; 2026H1 official updates available by 2026-07-18 |
| Coverage pack | AIDC |
| Required skills | equity-research; reports; supply-chain-research; growth-earnings-model; valuation; pdf; research-report-review |
| Review cycles | R0 evidence; R1 model; R2 draft; R3 render/compliance; R4 final IC |
| Verifiers | Generic case verifier; industry-chain verifier; repo research-gate runner |
| Depth gates | Evidence depth; broker-consensus depth; model depth; valuation depth; IC readiness |
| Pass conditions | Eight AIDC blocks covered or downgraded; zero open S; zero open unwaived A; reproducible valuation; verifier and workflow-eval PASS; score at least 90; final sign-off PASS |
| Downgrade path | Unsupported names become watchlist-only; material core evidence or valuation gaps downgrade the report to CONDITIONAL or evidence memo |

## Pre-Publish Self-Checklist

- [x] Evidence depth: 105 registered sources, 96 audited claims, 50 chain nodes across eight blocks, and company-level relationship evidence are complete for the declared scope.
- [x] Broker-consensus depth: all 12 modeled names were searched; three usable target-price anchors retain positive weight and the nine unavailable anchors are mechanically weighted at zero and disclosed as a scope downgrade.
- [x] Model depth: all 12 modeled names have explicit net-profit/EPS bridges, scenario factors, a second-method cross-check, and Atlas-specific 2026E earnings credit fixed at zero where hard economics are absent.
- [x] Valuation depth: every modeled ticker has current price, business-model-matched P/E, bounded PEG cross-check, scenario range, evidence grade, catalyst/invalidation fields, and independently reproduced arithmetic.
- [x] IC readiness: chapter 1 states ranking, portfolio behavior, triggers, invalidation, evidence quality, and the zero-credit rule without converting unresolved Atlas supplier claims into valuation uplift.

## Required Artifacts

The machine-readable list in `gate_manifest.json` is authoritative. Required groups are intake/governance, raw and verified data, broker consensus, full-chain and customer-chain evidence, house view, growth model, valuation, risk/exhibits, LaTeX/PDF, R0-R4 reviews, workflow evaluation, and final sign-off.
