# Independent Audit: R5 Public-NAV Proxy — 2026-08-15

## Executive Verdict

| Scope | State | Verdict |
|---|---|---|
| Sealed-source integrity | **PASS** | All retained bundle bytes, source hashes, raw-response hashes, page/row counts, request metadata, displayed dates, and positive NAV values reconcile. |
| Result-level arithmetic and rule implementation | **PASS** | The common panel, every rebalance, turnover/cost recurrence, annual values, rolling endpoints, and hurdle state independently reproduce. |
| Reported proxy state | **PASS** | `PUBLIC_NAV_PROXY_HURDLE_FALSIFIED` follows from both a failed complete-year test and failed rolling-five-year endpoints. |
| Formal feasibility / strategy evidence | **FAIL** | Retrospective public accumulated-NAV data are neither point-in-time nor executable market-price return evidence. |
| Overall independent audit | **CONDITIONAL** | The negative proxy record is numerically and procedurally reproducible, but it remains exploratory and cannot be promoted to a formal feasibility, product, allocation, or action conclusion. |

- Audit score: **92/100**
- Open S-Level: **0**
- Open A-Level: **0**
- Open B-Level: **0**
- Recommendation boundary: This is not a strategy recommendation, return forecast, product admission, allocation, or execution conclusion.

## Frozen Input Snapshot

| Artifact | SHA-256 |
|---|---|
| `analysis/r5_predeclared_public_nav_feasibility_protocol_20260815.json` | `35cb84604e6440d49c9d126003535ff4f120189c0f21ad00ba3c856e4e07217a` |
| `analysis/r5_public_nav_absolute_momentum_probe_20260815.json` | `9fa785b03db884ed1d0518e0682d7f45fb6536e13dc1ad5353b71deeb3050d1b` |
| `sources/probe-r5-public-etf-nav-20260815/manifest.json` | `017b3a69a9a9e40c2d0511d3e254551c61b565150d6c85b62282107ea08334cb` |
| `tools/run_r5_public_nav_absolute_momentum_probe.py` | `9f835e8ccf3524d501e6028c4ba31a822a0afe3f837dd749a3cb3f47f7d9d5a8` |

The result’s protocol, manifest, and derivation-script hashes exactly match this snapshot. Its Markdown/JSON summary pairs also reconcile on status, metrics, dates, and turnover disclosure.

Relevant read-only case verifiers also pass: `tools/verify_source_manifests.py` reports **SOURCE MANIFEST: PASS (104 files)** and `tools/verify_research_design_controls.py` reports **DESIGN CONTROLS: PASS (draft governance only; no entitlement, replay, admission, allocation or action)**.

The protocol correctly states `exploratory_post_observation_not_a_clean_preregistration`. Its post-result binding amendment and convention clarification explicitly say they do not repair the earlier observation or create an out-of-sample claim. The legacy filename containing `predeclared` must not be read as a clean pre-registration claim.

## Source Archive and Common-Panel Validation

All five raw bundles pass these checks: expected request template on every page, HTTP 200, sequential request/response page indices, constant reported total count, raw-response SHA-256, parseable and unique `FSRQ`, positive finite `LJJZ`, nondecreasing capture timestamps, manifest and freeze-control size/hash matches, and matching Markdown manifest row.

| Code | Pages | Rows | Displayed range | Bundle SHA-256 |
|---|---:|---:|---|---|
| 510300 | 174 | 3,472 | 2012-05-04–2026-08-14 | `cfba6bbc259309f3e295d1b875f3e541ed7496336ea2478fba7486177eeb67c5` |
| 510880 | 203 | 4,048 | 2010-01-04–2026-08-14 | `c92835538bf3bda69b8103930a0a56129ea435cec345df402d2691f37c2529bf` |
| 511010 | 164 | 3,269 | 2013-03-05–2026-08-14 | `367dff59ee1d5e8b1db5dc6c4e6680ef7f217c5be1235779a1259e7f43351d72` |
| 511990 | 201 | 4,003 | 2012-12-28–2026-08-14 | `6d99aa8f6e221c5a42cb238dbb3af478c93b32a36a2dc14d9852f32589ff9a31` |
| 518880 | 160 | 3,186 | 2013-07-18–2026-08-14 | `481cfbfea4de1979cbfd7a789ce8bfdd6b75bded53f3d53a3e562abfc9e9521f` |

The independent common-panel reconstruction is **3,186** positive observations from **2013-07-18** through **2026-08-14**, exactly matching the result. Excluded source rows reconcile to 510300/510880/511010/511990/518880 = **286/862/83/817/0**; all are pre-common-start rather than in-panel gaps.

## Independent Calculation Reconciliation

### Rule binding, timing, and turnover recurrence — PASS

- The code now fails closed unless the protocol’s fixed universe, sleeve weights, 252-observation lookback, timing, eligibility inequality, 1,260-observation rolling interval, 20bp cost, turnover definition, and terminal-period rules match the implementation binding. The protocol’s parallel human-readable sections and the emitted result binding also match independently.
- R5-B-001 is closed: the protocol and binding state that the equity signal is a **fixed-base, buy-and-hold, equal-weighted level**, while selected equity targets reset to 50/50 only at strategy rebalances. The fail-closed fixture crosses the January 31-to-February 1 monthly boundary, returns `(1.0, 1.25, 2.125)`, and independently rejects both a monthly target-rebalanced counterfactual (`1.5625`) and a monthly base-reset counterfactual (`1.25`).
- R5-B-002 is now closed: the new 310-business-day integration fixture invokes `_simulate()`, creates genuine unequal equity drift before its second equity-only rebalance (510300/510880 = 55.16%/44.84%), records a 50/50 selected-equity target, and verifies the effective-date post-return constituent weights follow that reset target. An independent drift-preserving 70/30 target-application mutation fails with the reset-target assertion. All three self-tests run before derivation and are emitted as `PASS` in the result.
- All **144/144** rebalances independently reproduce. The first signal/effective pair is **2014-08-29 / 2014-09-01**; the last rebalance effective date is **2026-08-03**; the terminal panel observation is separately and correctly labeled **2026-08-14**.
- Every signal is the final common observation of its month; its target applies on the next common observation before that day’s NAV return. No same-day signal return occurs.
- For every record, eligible sleeves, target weights, pre-trade drift, `0.5 × Σ|drifted − target|` turnover, 20bp one-way illustrative cost, post-cost NAV, and next-period drift recurrence match the independent reconstruction.
- The newly published turnover summary also reconciles: **15.4270565569x** total one-way turnover, **5** zero-turnover events, and **3.08541138%** simple sum of per-event cost fractions. The result correctly says that the latter is neither a compounded drag nor an executable-cost estimate.

### Full-period and complete-calendar-year arithmetic — PASS

Independent reconstruction matches final unit NAV **2.2666887367**, annualized net unitized change **7.33577818%**, maximum drawdown **-22.81766581%**, and **2,913** simulation intervals.

2014 is correctly incomplete because the simulated curve begins on 2014-09-01. 2015–2025 are complete and exactly match the output: 2015 9.01668612%, 2016 -7.04016221%, 2017 10.31500916%, 2018 -3.87367832%, 2019 7.97632259%, 2020 10.18895491%, 2021 1.86507968%, 2022 1.37692237%, 2023 3.39722994%, 2024 10.88675094%, and 2025 20.18059310%. 2026 is correctly incomplete because the final common observation is 2026-08-14, not 2026-12-31.

The repaired terminal-period logic is conservative and correct: a future terminal calendar year is eligible only on December 31, and a terminal rolling month is eligible only on that calendar month’s end.

### Rolling 1,260-observation endpoint construction — PASS

All **82/82** output endpoints independently reconcile. Each contains exactly 1,260 common-observation intervals, starts and ends at curve observations, annualizes with `252 / 1260`, and ends at a completed calendar month. The incomplete August 2026 terminal month is excluded.

The first endpoint is 2014-09-03 to 2019-10-31 (6.74843088% annualized); the last is 2021-05-26 to 2026-07-31 (6.77519626%). The minimum is **0.60388692%**, maximum **9.10668931%**, and **45/82** meet the 5% hurdle.

### Falsified / non-falsified logic — PASS

The result correctly identifies both required failure conditions:

- At least one complete calendar-year metric is below 5% (2016, 2018, 2021, 2022, and 2023).
- At least one rolling-five-year endpoint is below 5%.

Accordingly, `PUBLIC_NAV_PROXY_HURDLE_FALSIFIED` is the correct outcome under this fixed proxy arithmetic. It is not a formal feasibility finding.

## Verified Repairs

- The former ambiguous `last_effective_date` field is replaced by distinct `last_rebalance_effective_date` and `terminal_panel_observation_date` fields.
- The protocol is machine-bound and its fixed fields are checked against the implementation before derivation.
- Malformed `FSRQ` or `LJJZ` now fails before any row is discarded.
- Reader-facing Markdown and JSON now disclose aggregate turnover and the non-executable meaning of the simple cost sum.
- Terminal-period eligibility logic now tests calendar completion rather than mechanically excluding every terminal year/month.
- The fixed-base equity-signal convention is explicit, machine-bound, tested across a monthly rebalance boundary, and emitted with a passing self-test.
- The selected-target control has both a passing selector test and an applied-rebalance integration test with unequal constituent drift and verified reset-derived effective-date weights.

## Remaining Non-Waivable Conditions

### Non-waivable condition: capture implementation provenance

The source freeze records capture-time script SHA `224681fd02cb1bc39704b5d6e8ce46ffe70e22d1d50af53483934119f0c75b58`, but the original capture script was not separately retained. The manifest/result transparently label this `capture_script_version_not_retained`, preserve the raw-response and bundle-hash controls, and do not claim capture-versus-derive code equivalence.

This does not invalidate the retained byte-level archive or the present independent reconstruction. It does prevent a stronger claim that the capture implementation itself is fully reproducible; it is one reason the audit remains conditional.

## Fundamental Public-Source and Market-Price Limitations

These are not arithmetic defects, and they cannot be cured by relabeling the output:

- Retrospective public aggregation does not establish point-in-time availability, revision lineage, field semantics, entitlement/data rights, or a complete total-return ledger.
- Displayed `LJJZ` accumulated NAV is not an exchange execution price. Market price/NAV/IOPV, bid/ask, depth, fills, halts, limits, lots, creation/redemption, fees, taxes, settlement, and suitability are not modeled.
- The five codes are representative research inputs, not U0, a historical population, a decision universe, or an allocation list; survivorship and current-availability bias remain.
- Earlier field/sample observation makes this an exploratory post-observation record. A positive result would not be independent out-of-sample or strategy evidence; the current negative result only prevents this fixed proxy rule from being described as “stable 5%.”

## Publishability

- Status: **CONDITIONAL** for this narrow R5 proxy audit; **not eligible** as formal feasibility or strategy evidence.
- Score: **92/100**
- Open S-Level: **0**
- Open A-Level: **0**
- Open B-Level: **0**
- Required next action: retain the stated non-waivable limitations. No change converts this historical public-NAV proxy into executable market-return evidence.
