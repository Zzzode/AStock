# Repair Plan R1_model

## Status

- R1 publishability: **PASS**
- Publishability score: **93**
- Open S-Level: **0**
- Open A-Level: **0**
- Open B-Level: **0**
- Full case gate was not rerun by instruction. Targeted broker-summary, row-weight, PDF timestamp and extracted-text checks passed.

## Verified closures

- `R1-S-001` closed: 雅化集团 uses distinct operating-driver/NP/EPS scenarios; 恩捷股份 is a zero-weight sensitivity.
- `R1-A-001` closed: target horizons are consistently `not disclosed`.
- `R1-A-002` closed: the contract and verifier use one formal row plus five structured zero-weight rows.
- `R1-A-003` closed: the audit covers source overlap, alternative weights, eligibility, horizon and zero-weight coverage.
- `R1-A-004` closed: broker summary counts now reconcile to row weights—雅化集团 0.10, 恩捷股份 0.00; only `002497` is listed as a usable positive anchor.
- `R1-B-001` closed: the 17:32 rebuilt PDF/text contains the CNY25--26 reader range and 恩捷零权 treatment; old CNY26.29/CNY64.41 formal targets are absent.
- `R1-B-002` closed: `data/consensus_analysis.md` now uses `Auditable point-target reading`, which correctly covers both the positive-weight and zero-weight point-target evidence.

## Acceptance

R1 has zero open S/A/B issues and passes at 93. Structured weights, valuation arithmetic, eligibility, target horizon, action labels and the rebuilt reader artifact are mutually consistent.
