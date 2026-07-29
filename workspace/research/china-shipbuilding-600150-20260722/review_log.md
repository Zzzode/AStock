# Review Log

## Current Market-Data Remediation Status

- R0 source recheck: `PASS_PENDING_FINAL_GATE_REFRESH` (`96/100`; open S/A/B `0 / 0 / 0`)
- R2 draft recheck: `PASS_PENDING_FINAL_GATE_REFRESH` (`94/100`; open S/A/B `0 / 0 / 0`)
- R3: changed market-data pages show no visual blocker, but the current 51-page PDF still needs a full rendered-set refresh.
- R4 institutional recheck: no open S/A; `PENDING_FINAL_GATE_REFRESH`.
- Publication is not yet PASS because the current PDF/review state has not run the project-native verifier, shared gate or workflow refresh. Historical 50-page gate evidence is retained below only as history.

## R0_evidence — 2026-07-22

- Reviewer: independent maker-checker using `research-report-review`
- Scope: brief, gates/contracts, official company/industry evidence, original broker corpus, verified financial/market packets, full-chain artifacts, source registry, claim audit and source exhaustion
- Status: `BLOCKED`
- Institutional status: `BLOCKED`
- Historical initial-cycle score: `50/100`
- Open S-Level: `2`
- Open A-Level: `6`
- Open B-Level: `2`
- Generic verifier: `NOT RUN` — the gate-declared case-local `tools/verify_research_workspace.py` is absent
- Research gate: `FAIL` — `run_research_gates.py` crashed in `check_proxy_field_official_collection_depth` with `TypeError: 'NoneType' object is not iterable`
- Top blockers:
  1. Audited COSCO CNY50bn project attribution to 600150 subsidiaries is reversed in current chain/claim artifacts.
  2. The CNY47.00 Guotai Haitong lead is a local 404/not-found source but remains populated as a visible abstract in the broker packet.
  3. Full-chain and source-governance artifacts are not completely enforced by gate/contract rows.
- Confirmed controls: actual/restated/pro-forma separation; 75.2562bn-share current denominator; 601989 delisting versus legal deregistration caveat; unaudited H1 and no annualization; backlog not revenue; military/Hudong/group options excluded from valuation; original broker PDFs separated from weak target-price leads.
- Structured findings: `review_findings_R0_evidence.json`
- Repair plan: `repair_plan_R0_evidence.md/json`

## R0_evidence First Recheck — 2026-07-22

- Reviewer: independent maker-checker using `research-report-review`; maker files read only
- Status: `BLOCKED`
- Institutional status: `BLOCKED`
- Historical first-recheck score: `82/100`
- Open S-Level: `0`
- Open A-Level: `3`
- Open B-Level: `0`
- Closed after artifact reread: `R0-S-001`, `R0-S-002`, `R0-A-002`, `R0-A-003`, `R0-A-005`, `R0-A-006`, `R0-B-001`, `R0-B-002`
- Remaining A-Level:
  1. `R0-A-001`: mandatory R0 files are enumerated in the gate, but six artifacts still lack individual field-level rows in `artifact_contract.md/json`.
  2. `R0-A-004`: relationship/customer row governance has source IDs but still uses generic `local_path`/`original_url` placeholders instead of exact values.
  3. `R0-A-007`: all broker rows omit row-level ticker and positive `valuation_weight` conflates forecast weight with unavailable target-price anchor weight.
- Case verifier after this review update: `22 PASS / 17 FAIL`; remaining failures are downstream R1-R4 artifacts plus R0 closure state.
- Shared research gate after this review update: `73 PASS / 45 FAIL`; it runs without the prior single-stock proxy crash and additionally confirms the open broker-row contract defects above.
- Confirmed critical controls: COSCO attribution and de-duplication; AG-04 not-found handling; actual/restated/pro-forma separation; 75.2562bn-share denominator; 601989 legal-status caveat; unaudited H1/no annualization; backlog not revenue; military/Hudong unsupported options at zero valuation credit.
- Updated findings: `review_findings_R0_evidence.json`
- Updated repair plan: `repair_plan_R0_evidence.md/json`

## R0_evidence Second Recheck — 2026-07-22

- Reviewer: independent maker-checker using `research-report-review`; maker files read only
- R0 cycle status: `PASS`
- R0 score: `95/100`
- Open S-Level: `0`
- Open A-Level: `0`
- Open B-Level: `0`
- Closed after field-level reread: `R0-A-001`, `R0-A-004`, `R0-A-007`
- `R0-A-001`: six missing artifact-contract rows now exist in both twins with required fields, depth, blockers, reviewer cycle and verifier check.
- `R0-A-004`: all relationship/customer row-governance sources now use concrete IDs, exact local paths, exact URLs, dates and types; placeholder scan is clean.
- `R0-A-007`: all 15 broker rows have `ticker=600150.SH`; positive forecast weights are separated from zero target-price valuation weights.
- Residual constraints: original Street target prices remain unavailable and zero-weight; ship-type ASP/schedule/utilization/payment fields remain model-method blocks; backlog is not revenue; military/Hudong/group options remain excluded.
- R0 PASS is a cycle gate only. The report remains non-publishable until R1-R4, 39 PASS / 0 FAIL, final PDF and final sign-off are complete.
- Case verifier: `22 PASS / 17 FAIL`; R0 evidence checks 01--18 and related market/house checks pass, while downstream valuation, report, lifecycle and final-signoff checks remain open.
- Shared research gate: `76 PASS / 42 FAIL`; broker coverage, row schema and zero-weight controls now pass, while downstream R1-R4 and final publication gates remain open.
- Updated findings: `review_findings_R0_evidence.json`
- Updated closure plan: `repair_plan_R0_evidence.md/json`

## R1_model — 2026-07-22

- Reviewer: independent maker-checker using `research-report-review`; growth and valuation maker files were read only
- R1 cycle status: `PASS`
- Institutional status: `R1_INSTITUTIONAL_PASS_DOWNSTREAM_INCOMPLETE`
- R1 score: `95/100`
- Open R1 S/A/B: `0 / 0 / 0`
- Closed before final freeze: `R1-S-001`, `R1-A-001`, `R1-A-002`
- Growth Base parent NP 2026E-2028E: `172.762156 / 216.489959 / 246.810914` 亿元; EPS denominator `75.25621288` 亿股
- Valuation: current `33.02`, market cap `2,484.9601492976` 亿元, Bear/Base/Bull `11.207610 / 33.0821075 / 48.342034`, weights `85% / 15% / 0%`, published target `33.07`, upside `+0.1514%`
- Action: `中性偏多（持有/等待验证） / event-driven validation`; not Buy
- Confirmed controls: no H1 annualization; COSCO approximately CNY50bn project de-duplicated; one valuation parent only; no subsidiary fake SOTP; military/Hudong-Zhonghua/group/weak-target optionality all zero; `broker_weight=0`
- Unsupported Bull-bias percentages and historical target-achievement claims were removed before final freeze
- Case-local verifier after R1 review artifacts: `32 PASS / 7 FAIL`; all R1 growth/valuation/segment/target/weight checks pass, while failures are downstream R2-R4, LaTeX/PDF, workflow evaluation and final sign-off
- Shared research gate after R1 review artifacts: `88 PASS / 37 FAIL`; R1 findings/repair lifecycle and valuation-depth checks pass. Remaining failures include downstream publication artifacts/cycles, unavailable positive Street target anchors, the literal source-exhaustion token check, final sign-off/workflow evaluation and the non-final case-verifier status
- Residual constraints: growth model remains `CONDITIONAL` for granular ASP/schedule/utilization/payment/cost evidence; original Street target prices remain unavailable and zero-weight; publication remains blocked pending all downstream gates
- Structured findings: `review_findings_R1_model.json`
- Repair/closure plan: `repair_plan_R1_model.md/json`

## R2_draft — 2026-07-22

- Reviewer: independent maker-checker using `research-report-review`; `main.tex` and all 17 section files were read only
- R2 cycle status: `PASS`
- Institutional status: `INSTITUTIONAL_PASS`
- R2 score: `94/100`
- Open R2 S/A/B: `0 / 0 / 0`
- Closed before final freeze: `R2-S-001`, `R2-A-001` through `R2-A-006`
- Final thesis/action: current `33.02`, target `33.07`, upside `+0.15%`, fair-value range `31.64-35.96`, action `中性偏多（持有/等待验证）`
- Final valuation exhibit: sole parent `600150.SH`; market cap `2,484.96` 亿元; 2026E-2028E NP/EPS, method, Bear/Base/Bull, target/range, action, catalysts, invalidation, evidence quality and zero-credit boundaries are consolidated in one exhibit
- Forecast bridge: analytical Base reconciles `206.99 = 186.17 + 20.82`; Base PBT-to-tax-to-minority-to-parent-NP/EPS is reader-reproducible; Bear/Bull tax and attribution assumptions are disclosed
- Market expectation/risk: House fair values and downside are shown at observation multiples; risk probability/impact bands, hard thresholds and quantified sensitivities are explicit
- Confirmed controls: H1 remains an unaudited preview and is not annualized; COSCO approximately CNY50bn project is de-duplicated; military/Hudong-Zhonghua/unallocated group orders/weak target-price leads remain zero-credit; there is one valuation parent only
- Draft hygiene: no TODO, TBD, placeholder, pending-fill token or unresolved source ID in `main.tex`/sections; prose-led chapter openings and post-exhibit synthesis are present
- Layout repairs closed before final R2 freeze: ch09 three-scenario table and ch10 broker matrix were narrowed after right-edge overflow was identified
- Case-local verifier after R2 artifacts: `36 PASS / 3 FAIL`; checks 01-35 and 39 pass. Remaining failures are full review lifecycle, final sign-off and workflow evaluation
- Shared research gate after R2 closure: `97 PASS / 30 FAIL`; R2 lifecycle, zero open S/A, valuation and broker zero-weight exhaustion checks pass. Remaining failures are downstream R3/R4, final sign-off, workflow evaluation, manifest/final-score fields and the non-final case verifier
- R2 PASS is a cycle gate only. Publication remains `BLOCKED` pending R3 page-by-page render review, R4 final IC, workflow evaluation, final sign-off, dependency refreshes and `39 PASS / 0 FAIL`
- Structured findings: `review_findings_R2_draft.json`
- Repair/closure plan: `repair_plan_R2_draft.md/json`

## R3_render_compliance — 2026-07-22

- Reviewer: independent maker-checker using `research-report-review`, `exhibit-format-reviewer` and `pdf`; source files were read only
- R3 cycle status: `PASS`
- Institutional status: `INSTITUTIONAL_PASS`
- R3 cycle score: `92/100`
- Open R3 S/A/B: `0 / 0 / 3`
- Non-blocking B-Level findings: pages `26/35/47` are low-density orphan pages; the Appendix A sentence splits across pages `42-43`; the page-38 risk matrix is print-dense at `scriptsize`
- PDF state: `50` A4 pages, `726269` bytes, SHA-256 `e5812560ed01ac79f451a62bad789648c9abc399c2f870da122d40a60e573f66`; all `50` render PNGs are present at `910x1287`
- Visual scope: cover, English abstract, three-page contents, every chapter opening, all wide tables, four TikZ diagrams, one cycle chart, five longtables, appendices and final important-statement page were reviewed page by page
- Visual result: no blank page, publication-blocking orphan, clipping, overlap, missing glyph, mojibake, unreadable core exhibit or header/footer collision
- Critical layout closures: ch09 Bear/Base/Bull scenario table and ch10 broker matrix fit inside their exhibit boundaries; Appendix longtables continue cleanly and remain readable
- PDF integrity: all fonts are embedded/subsetted with Unicode maps; fresh `pdftotext -layout` output is byte-identical to `main_current_text.txt`
- Build evidence: two-pass MacTeX XeLaTeX and final project-CLI success at 50 pages; maximum residual Overfull is `0.24898pt`, with `>20pt COUNT=0`, and is non-material
- Reader-facing control: current `33.02`, target `33.07`, upside `+0.15%`, fair-value range `31.64-35.96`, action `中性偏多（持有/等待验证）` and the final disclaimer remain visible and consistent
- Case-local verifier after R3 artifacts: `36 PASS / 3 FAIL`; checks 01-35 and 39 pass, while R4 lifecycle, final sign-off and workflow evaluation remain open
- Shared research gate after R3 artifacts: `100 PASS / 29 FAIL`; R3 findings/repair and zero-open-S/A gates pass, while R4, final-signoff/workflow artifacts, manifest/final-score fields and the non-final case verifier remain open
- R3 PASS is a cycle gate only. The three B findings should be repaired before R4 or explicitly accepted as non-blocking final-signoff residuals. Publication remains `BLOCKED` pending R4 final IC, workflow evaluation, final sign-off, dependency refreshes and `39 PASS / 0 FAIL`
- Structured findings: `review_findings_R3_render_compliance.json`
- Repair/closure plan: `repair_plan_R3_render_compliance.md/json`

## R4_final_ic — 2026-07-22

- Reviewer: independent final investment-committee maker-checker using `research-report-review`; TeX, PDF and production code were not modified
- R4 cycle status: `PASS`
- Institutional status: `INSTITUTIONAL_PASS`
- Report publishability: `BLOCKED_PENDING_VERIFIER`
- Open R4 S/A/B: `0 / 0 / 0`
- Closed during R4: `R4-S-001` stale no-target/valuation-incomplete House text; `R4-A-001` stale canonical valuation pending status
- Final thesis/action: current `33.02`, target `33.07`, upside `+0.15%`, fair-value range `31.64-35.96`, action `中性偏多（持有/等待验证）`
- Scenario trace: Bear/Base/Bull `11.21 / 33.08 / 48.34`; 2026E-2028E Base parent NP `172.762156 / 216.489959 / 246.810914` 亿元 and EPS `2.295653 / 2.876705 / 3.279608`; `Model Reproducibility: PASS`
- Evidence boundary: the correctly disclosed COSCO project is approximately CNY50bn / 500亿元 across 87 vessels and receives zero incremental credit; military, Hudong-Zhonghua, unallocated group orders, asset injection and weak target leads also remain zero-credit
- Event discipline: positive gates are H1 parent/adjusted NP at least `101/99` 亿元, core GM at least `11.72%`, positive OCF and delivery near plan; hard downgrade gates are below `92/90`, GM below `10.5%`, major delivery/customer-financing problems or full-year OCF/NP below `0.8x` without recovery
- R3 residual acceptance: `R3-B-001` through `R3-B-003` are explicitly waived as non-blocking presentation polish; no valuation, action, risk or source conclusion is obscured
- Downgrade status: `downgrade_not_required_at_cutoff`; no further downgrade is required because the action already withholds new capital pending validation and no Street target enters valuation
- Preliminary sign-off: `final_signoff.md/json` written with `BLOCKED_PENDING_VERIFIER`; it must not be promoted to PASS until the case-local verifier is `39 PASS / 0 FAIL` and the shared research gate is clean
- Structured findings: `review_findings_R4_final_ic.json`
- Preliminary sign-off: `final_signoff.md/json`

Publishability Score: 92

## Market-Data Remediation Recheck — 2026-07-23

- Reviewer: independent maker-checker using `research-report-review`; data, model, prose and shared code were read only. This reviewer updated only the review, repair-plan and sign-off artifacts.
- Reviewed current PDF: `main.pdf`, 51 A4 pages, SHA-256 `847ce2676eb646fba6520ae1f0bf77aa96200918fb6db87f687ef0577dc04052`.
- Source recheck: `PR-02` raw `fqt=1` front-adjusted history has 727 daily rows from 2023-07-03 through 2026-07-22; `fqt=0/2` controls, exact endpoint and SHA-256 manifest are present. Cutoff volume, amount, turnover, circulating shares and market cap reconcile mechanically.
- Capital-positioning recheck: `PR-03` contains SSE 2026-07-21 daily margin detail, quarterly SSE Shanghai Connect holdings, 2026Q2 public-fund aggregate, a near-one-year Dragon-Tiger negative query and ticker-history query, plus raw responses and hashes.
- Definition controls: 75.2562 亿股 is labelled `流通 A 股本`, not strict free float. Strict free float is unavailable because no archived public source provides a uniform immediately-tradeable-holder classification. Daily Shanghai Connect net holding change is unavailable because the public single-security record is quarterly and the attempted daily endpoint returned a stored no-data response. Both are defined evidence boundaries, not omitted research data.
- Reader-facing checks: Chapter 12, Appendix A, source registry, claim audit and source-exhaustion log resolve `PR-02/PR-03` consistently. Quarterly holdings are not presented as daily flow; the Dragon-Tiger negative result is not presented as proof of zero market activity.
- Valuation/action check: new market evidence receives zero incremental fundamental valuation credit. Current CNY33.02, target CNY33.07, fair-value range CNY31.64-35.96, Bear/Base/Bull CNY11.21/33.08/48.34 and `中性偏多（持有/等待验证）` remain coherent.
- Render check: direct current-PDF renders of physical pages 36-39 (Chapter 12 and following chapter opening) show no clipped or overlapped table, broken glyph or unreadable source note. A full current 51-page rendered-set refresh has not been performed by this reviewer.
- New S/A findings: `0 / 0`.
- Current sign-off: `PENDING_FINAL_GATE_REFRESH`, not PASS.
- Required main-agent refresh: full 51-page render review; text-snapshot/font/overfull and dependent-manifest refresh; case-local verifier; shared research gate; workflow evaluator. Do not reuse the old 50-page PDF or the 2026-07-22 `39 PASS / 0 FAIL` / `133 PASS / 0 FAIL` results as current evidence.

## Historical Pre-Remediation Final Publication Gate — 2026-07-22

- Native workflow evaluation: `excellent`, `publishable=true`, `95/95` checks passed, score `100.0`, zero blocking failures.
- Case-local verifier: `39 PASS / 0 FAIL`.
- Shared research gate: `133 PASS / 0 FAIL`, `RESULT PASS`.
- Final sign-off: `PASS`; the three R3 presentation-only B findings remain explicitly waived, with no open S-Level or unwaived A-Level finding.

Publishability Score: 92

## Current-PDF Final Gate Refresh — 2026-07-23

- Scope: current `main.pdf`, 51 A4 pages, SHA-256 `847ce2676eb646fba6520ae1f0bf77aa96200918fb6db87f687ef0577dc04052`; no prior 50-page result is used as present-state evidence.
- Render refresh: `rendered/current-51` contains 51 PNGs. The cover, market-data pages 36--39, Appendix A source pages, final source/disclaimer page and PDF page/size metadata were rechecked; no clipping, overlap or glyph corruption was found.
- Workflow evaluator: `excellent`; `publishable=true`; `99/99`; score `100.0`; zero blocking failures.
- Case-local verifier: `39 PASS / 0 FAIL`.
- Shared research gate: `137 PASS / 0 FAIL / RESULT PASS`; the industry-chain verifier was correctly skipped because this is a single-stock report with one valuation parent.
- Final status: `PASS`. The market-data remediation has no open S/A finding. Any material evidence, model or layout change reopens this refresh requirement.
