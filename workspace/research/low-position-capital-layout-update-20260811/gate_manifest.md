# Gate Manifest — Low-Position Capital Layout Update

| Field | Value |
|---|---|
| Case ID | `low-position-capital-layout-update-20260811` |
| Report type | Valuation update / market and financial refresh |
| Data cutoff | 2026-08-11 09:21–09:22 CST pre-open snapshot; 2026-08-10 close for completed-session market measures; FY2025, 2026Q1, and 2026H1 disclosures available by 2026-08-11 |
| Scope definition | Cross-sector low-position earnings-recovery update |
| Required skills | equity-research; reports; valuation; research-report-review; agent-resilience |
| Required artifacts | Raw market and financial packets; source registry and claim audit; verified packets; broker consensus; house view; variant perception; valuation model/audit; risk; LaTeX/PDF; R0–R4 reviews; final sign-off; workflow evaluation |
| Review cycles | R0_evidence; R1_model; R2_draft; R3_render_compliance; R4_final_ic |
| Verifiers | case verifier; repository research gate; MacTeX XeLaTeX |
| Depth gates | evidence depth; broker-consensus depth; model depth; valuation depth; IC readiness |
| Downgrade path | core review → event-driven validation → watchlist only; a historic high-upside model stays watchlist-only until refreshed gates pass |

## Pass Conditions

1. Every covered ticker has a timestamped market-data row or an explicit unavailable label.
2. Financial observations link to official evidence or are explicitly labelled unavailable.
3. Broker evidence preserves source quality; weak evidence has zero valuation weight.
4. Every primary candidate has a reproducible current-price valuation-eligibility decision or an explicit event-validation/watchlist-only boundary.
5. Historical model upside is never presented as a current target without refreshed evidence.
6. R0–R4 contain no open S-Level or unwaived A-Level issue.
7. The case verifier reports 39 PASS / 0 FAIL and the repository research gate passes.
