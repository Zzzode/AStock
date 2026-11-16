# R0 Evidence Repair Plan

Status: **repairs implemented; independent rerun pending**. The full
machine-readable plan is `repair_plan_R0_evidence.json`.

| Finding | Repair | Status |
|---|---|---|
| R0-S-001 | Reclassified the ETF input as unresolved-basis public daily bars and regenerated its diagnostic | Implemented |
| R0-S-002 | Retained and hash-bound all twelve SHFE/CZCE six-date samples; labeled them retrospective | Implemented |
| R0-S-003 | Created the R0 finding, repair-plan and log artifacts | Implemented |
| R0-A-001 | Relabeled the dynamic ETF exercise exploratory/post-source | Implemented |
| R0-A-002 | Added per-file vendor provenance fields and a mechanical check | Implemented |
| R0-A-003 | Added separate AU, CU and TA R1 cards | Implemented |
| R0-A-004 | Added metadata-only WAF/404 failed-probe records | Implemented |
| R0-B-001 | Expanded claim-audit source IDs | Implemented |
| Post-repair | Fresh independent R0 review | Conditional; added R0-A-005/R0-B-002 |
| R0-A-005 | Persisted manifest-derived retrospective provenance in every futures result row and generator output | Implemented |
| R0-B-002 | Made verification paths cwd-independent and tested repo/case roots | Implemented |
| Post-conditional repair | Final independent R0 repair check | Passed for evidence-governance repairs only |

None of these repairs closes the data, entitlement, cost, point-in-time,
formal-rule or paper-reconciliation requirements in `unresolved_requirements.json`.
The case remains `q=0` and non-investable.
