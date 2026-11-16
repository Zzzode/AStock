# Evidence and Model Review — 2026-08-11 Re-review

## Review Scope

- Cycles: `R0_evidence` and `R1_model`.
- Files reviewed: current market and financial packets; broker consensus and raw archives; source registry; claim audit; current valuation disposition; valuation model/audit/independent check; secondary-market analysis; current LaTeX sources; and the case-local verifier.
- Boundary tests: 8/11 pre-open is not a close; a preview is not actual H1; external broker targets are not house targets; a historic scenario is not reused as a current target.

## S-Level Issues (block publication)

None open in R0/R1 after re-review.

- The former missing case-local-verifier issue is resolved: `python3 tools/verify_research_workspace.py` now runs and truthfully reports `36 PASS / 3 FAIL`.
- The former incomplete valuation-disposition issue is resolved: all 13 covered names now have full, explicit no-target rows with `final_target` and `upside` set to `not_published`, and all house blend weights set to zero.
- The re-review caught and verified correction of explanatory tenfold unit errors: broker NP is now CNY7.910bn (000703), CNY6.454bn/CNY7.230bn (300014), and CNY3.032bn (002497), not ten times those amounts.

## A-Level Issues (must fix)

None open in R0/R1.

- The case-local valuation-universe check was reconciled to the declared 13-name coverage. It now requires exactly 13 rows that exactly equal the raw-market universe, while retaining its required-field, no-target and zero-weight tests; this is a stronger coverage check rather than a bypass.
- 8/11 cutoff records now reconcile to the 09:21–09:22 pre-open capture window, and broker `implied_upside` is explicitly separated into report-date arithmetic versus refreshed 8/10 external-reference arithmetic.

## B-Level Issues (should fix)

None open in R0/R1 after re-review.

## Missing Institutional Tables / Exhibits

None in the assigned R0/R1 evidence/model scope.

## Confirmed Strengths

- Every valuation price, return, turnover and range-position conclusion uses the 2026-08-10 completed-session close; 8/11 zero-trade quotes remain labelled pre-open observations.
- Only 000703 and 301308 are treated as actual H1 reports. The remaining nine H1 records are issuer previews and 600739/600150 retain official-search gaps.
- The flat and detailed broker schemas both downgrade 600150 and 300390 to `re_scoped_original_unverified`, with zero weight. Positive external anchors remain archived original-PDF evidence and are not presented as AStock targets or a vendor consensus.
- All 13 current coverage names carry an explicit no-target disposition. External anchors are retained only for evidence comparison; CNY77/CNY103 for 300014 are not averaged and historic scenarios are not reused.
- The four primary market-implied anchors now combine the 8/10 price, external-EPS diagnostic or denominator gap, range position, trading value and relevant 20/60-day momentum while preserving the diagnostic-only, zero-weight no-target boundary.
- `Model Reproducibility: PASS` is present for disclosed arithmetic, appropriately bounded to reproducibility rather than target support.

## Publishability

- Status: `BLOCKED`
- Institutional status: `BLOCKED`
- Score: `67/100`
- Review Cycle: `R0_evidence`, `R1_model` re-review
- Open S-Level: `0` in R0/R1
- Open A-Level: `0` in R0/R1
- Open B-Level: `0` in R0/R1
- Case-local verifier: `36 PASS / 3 FAIL`. The only failures are unavailable required MacTeX XeLaTeX, missing `main.pdf`, and missing rendered-page PNGs; these remain R3/R4 publication/render blockers.
- Repository gate: `83 PASS / 28 FAIL`. Its remaining failures are global workflow/final-signoff/render prerequisites; they are not waived here.
- Required next fixes: R3/R4 must build and inspect the mandated PDF in a MacTeX environment, complete final governance/sign-off artifacts, and rerun both gates to `39 PASS / 0 FAIL` case-local plus a clean repository gate.
