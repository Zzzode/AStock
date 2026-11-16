# Skill Evolution Log — Chinese Prose Template Rule

## Failure Mode

The report review identified generic formulaic contrasts but lacked explicit Chinese patterns, a deterministic scan, a named owner, and a publication-blocking threshold. The first fixed-pattern repair then missed a double-denial construction because it did not inspect every authored `不是` occurrence. The next pass exposed a paired-negative `没有` frame outside that scan scope.

## Root Cause

The missing control spanned the drafting role, prose-polish skill, and review skill. The generic editorial instruction could not be tested or consistently applied.

## Change Set

- Added a named prohibition, source-scope boundary, literal scan, exception protocol, audit artifact, and A-Level closure rule to `research-prose-polish`.
- Added an R2 hard gate to `equity-research`.
- Added independent R2 re-scan and closure criteria to `research-report-review` and its reviewer role.
- Added first-draft prevention to the LaTeX writer role.
- Registered AP-004 in both anti-pattern registries.
- Added deterministic regression coverage in `test_research_prose_rules.py` for prohibited and direct, evidence-led samples.
- Extended the pattern set to include the close `而不是` variant after the rewrite review found it remained outside the first literal scan.
- Expanded the R2 scan to every authored `不是` occurrence after a user review found that a paired-pattern-only scan still allowed negative contrast framing to survive.
- Expanded the R2 scan to every authored `没有` occurrence and paired-negative stack after user review found that a parallel negative frame still survived.

## Regression Contract

The regression verifies all required prompt mirrors remain byte-identical and checks that the scan pattern detects each prohibited sample while leaving direct evidence-led samples clear. The integration workflow requires zero eligible hits, including zero authored `不是` / `没有` occurrences and zero paired-negative stacks, in `analysis/prose_style_audit.md/json` before an R2 pass.

## Validation Results

- Focused rule regression: `2 passed`.
- Affected quality tests (`test_research_prose_rules.py` plus `test_checks.py`): `28 passed`.
- `check_system_prompt_drift`: `20` mirror pairs checked, `0` drift.
- Case-local workspace verifier: `74 PASS / 0 FAIL` after the rewritten release.
- Generic research gates: `140 PASS / 0 FAIL` after the rewritten release.

The current reissued case is certified under the stricter rule: all eligible source and PDF-text scans are clear, the rewritten PDF has a refreshed release identity, and R2/R3/R4 are reclosed.

## Historical Case Disposition

The user then requested a full rewrite and later identified a surviving double-denial construction followed by a paired-negative frame. The current PDF is the exhaustive third reissue. The initial review found 29 literal matches across 27 reader-facing lines and a later pass found 14 close-variant constructions; later strict scans found 33 reader-facing lines with authored `不是` framing and 17 lines with authored `没有` framing. All eligible items were repaired, the R2 audit returned zero source/PDF-text hits, and R2/R3/R4 plus the case gates were reopened.
