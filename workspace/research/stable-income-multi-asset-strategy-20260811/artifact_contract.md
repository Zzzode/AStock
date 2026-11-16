# Artifact Contract — Stable-Income Multi-Asset Strategy

- Case profile: strategic_allocation
- Scope ID: strategic-allocation-etf-first-v2-20260811
- Scope control: direct stocks and REITs start at 0%; direct stocks may only replace red-dividend ETF exposure after independent research, at most 15% in aggregate and 5% per issuer. REITs require three independently reviewed projects, are capped at 5% in aggregate and 2% per project, and can only replace high-quality RMB rate bonds.
- Reader-source graph: main.tex plus the eight paths declared in gate_manifest.json.

| Artifact | Stage | Required for | Required fields | Blocking conditions | Review cycle | Verifier check |
|---|---|---|---|---|---|---|
| research_brief.md | Intake | Scope freeze | Fixed principal, asset layers, exclusions, activation boundaries, designated targets and current not-run status | Direct stock before research; point-return promise; live-order implication | R0 | Scope/control parity |
| data/source_registry and data/claim_audit | Evidence | Traceability | IDs, active/retired status, authority, local archive status, URL, date, claim and limitations | Authority conflated with local archival; retired historical observation used as a current input | R0 | Active-source/claim resolution |
| data/portfolio_return_model_20260811.json | Modeling | Return and cash boundary | Base weights, formula-only r sensitivity, compounding formula, actual D0 ledger contract, direct-stock and REIT controls | Old point-return branch, r used to infer D0, or fixed-cash prediction | R1 | Weight and r/D0 control reconciliation |
| data/execution_eligibility_policy_20260812 | Modeling | Execution boundary | not_run status, current-session fields, source/timestamp requirements, controlled thresholds, q, combined look-through and fallback | Missing field treated as pass, undefined threshold, or current-data claim without a packet | R1/R2 | Eligibility-packet schema and no-live-decision control |
| data/model_portfolio_implementation_20260812 | Modeling | Model-portfolio actionability | Designated implementation, target notional, staged action, policy reference, deterministic fallback, capacity tests and observed-DD triggers | Generic product examples, unnamed active sleeve, cash-cap breach, substitute trade, or stale-data order claim | R1/R2 | Packet-to-reader action-card parity |
| analysis/allocation_model and related risk/cash-flow/scenario models | Modeling | Allocation decision | Target vectors, fixed CNY200,000 mapping, caps, q gates, protected-liquidity waterfall, r/D0 separation and observed-DD definition | Ineligible sleeve receives funds, scenario triggers live control, or weights fail to sum | R1 | Reproducibility review |
| main.tex and declared sections | Draft | Reader source | Chinese decision logic, active/retired source boundary, designated targets, amounts, sequencing, thresholds, fallback and observed-DD distinction | Legacy snapshot treated as current input, generic examples, point return, vague fallback or stale source-to-PDF identity | R2 | Input graph, action-card parity and TeX checks |
| main.pdf, text extraction, render evidence and build provenance | Render | Publication | Current source/PDF hashes, page count, full render set, XeLaTeX host/distribution/version/command provenance and diagnostics | Stale/partial/non-XeLaTeX render, unlogged diagnostics or author-only visual check | R3 | Artifact-identity and independent-review check |
| review_log and review findings/repair plans | Review | Lifecycle | Scope transition, finding status, repair evidence and publication disposition | Current scope relies on historical closure | R0--R4 | Review lifecycle |
| final_signoff and workflow evaluation | Sign-off | Publication decision | Scope/PDF identity, findings, residual risks, verifier results and status | PASS with stale identity, an open independent-review/render defect, or a claim that `q=0` constitutes live authorization | R4 | Sign-off consistency |

The machine-readable contract is artifact_contract.json; it is authoritative for the exact active controls and file graph.
