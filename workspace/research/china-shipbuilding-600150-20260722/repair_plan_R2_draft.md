# R2 Draft Repair Plan — Final Maker-Checker

- Case: `china-shipbuilding-600150-20260722`
- R2 cycle status: `PASS`
- Institutional status: `INSTITUTIONAL_PASS`
- Report publishability: `BLOCKED` pending R3, R4, workflow evaluation, final sign-off and `39 PASS / 0 FAIL`
- R2 score: `94/100`
- Open: `0 S / 0 A / 0 B`
- Closed before final freeze: `R2-S-001`, `R2-A-001` through `R2-A-006`

## No open R2 repair actions

The final independent draft maker-checker verified:

1. One complete final valuation exhibit now covers the sole valuation parent, price/date, market cap, 2026E-2028E NP/EPS, method, scenarios, target/range, upside, action, catalysts, invalidation, evidence quality and all zero-credit boundaries.
2. The analytical Base residual is explicitly reconciled as `206.99 = 186.17 + 20.82` hundred million yuan and is not presented as a disclosed company segment.
3. The reader-facing earnings bridge now reproduces PBT, tax, consolidated net profit, minority interest, parent net profit and EPS for 2026E-2028E Base and discloses Bear/Bull tax and attribution assumptions.
4. The market-expectation bridge now shows House fair values and upside/downside at each observation multiple in addition to current-price-implied earnings gaps and driver requirements.
5. The risk matrix defines probability/impact bands, hard thresholds, available earnings/value sensitivities and explicit `not estimable`/`zero-credit` handling for unavailable evidence.
6. The scenario and broker comparison tables were narrowed so their essential fields fit within the source exhibit widths; final rendered-page confirmation remains an R3 responsibility.
7. Current price/target/upside/action remain `33.02 / 33.07 / +0.15% / 中性偏多（持有/等待验证）`. The fair-value range remains `31.64-35.96`; Bear/Base/Bull remain `11.21 / 33.08 / 48.34`.
8. H1 is an unaudited preview and is not annualized; the COSCO project is de-duplicated; 600150.SH is the only valuation parent; military, Hudong-Zhonghua, unallocated group orders and weak target-price leads remain zero-credit.
9. `main.tex` plus all 17 section files contain no TODO, TBD, placeholder or unresolved source ID.

## Residual constraints carried into R3-R4

- R2 approval covers the reader-facing draft logic and source structure. It is not rendered-page or publication sign-off.
- The final 50-page PDF must be inspected page by page in R3 for clipping, overflow, overlap, orphan pages, density and exhibit readability.
- Ship-level ASP, schedule, utilization, payment milestones, customer financing and cost pass-through remain unavailable; the report must keep consolidated-only scenario valuation.
- Original Street target prices remain unavailable; broker target-price weight must remain zero.
- Before publication, complete R3, R4, workflow evaluation, `final_signoff.md/json`, dependency refreshes and the mandatory case-local `39 PASS / 0 FAIL` verifier result.

## Reopen triggers

Reopen R2 if a downstream edit:

1. changes `33.02 / 33.07 / +0.15%`, `31.64-35.96`, the Bear/Base/Bull values or the hold/wait action without regenerating the model package;
2. removes any required field from the consolidated final valuation exhibit;
3. reintroduces the `186.17` versus `206.99` Base-label ambiguity or breaks the PBT-to-EPS bridge;
4. annualizes Q1/H1 or directly converts backlog/order value into revenue or EPS;
5. adds the COSCO project a second time or assigns value to military, Hudong-Zhonghua, group orders or weak target-price leads;
6. creates a second valuation parent or separate yard/ship-type SOTP;
7. weakens risk thresholds or removes quantified sensitivities;
8. reintroduces clipped/overflowing core exhibits or table-only recommendation logic.

## Market-Data Remediation Recheck — 2026-07-23

Status: `DRAFT_RECHECK_PASS_PENDING_FINAL_GATE_REFRESH`; no open S/A issue.

Chapter 12 and Appendix A now cite `PR-02/PR-03` with dates, source tiers and frequency boundaries. The report uses only the labelled `fqt=1` history for return, drawdown and moving-average claims; calls 75.2562 亿股 `流通 A 股本`; and prevents quarterly Shanghai Connect/fund stock or a Dragon-Tiger negative query from becoming same-day institutional flow. The market package changes execution discipline only and carries zero incremental fundamental-valuation credit, so the CNY33.02 / CNY33.07 / CNY31.64--35.96 / hold-wait package remains unchanged.

Required next step: refresh the current 51-page render, dependent inventories/manifests, case-local/shared gates and workflow evaluation. Do not cite historical 50-page gate output as current validation.
