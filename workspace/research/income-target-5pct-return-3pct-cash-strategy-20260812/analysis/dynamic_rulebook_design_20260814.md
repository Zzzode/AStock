# Dynamic Rulebook Design — OU-TR5-v1

- Date: 2026-08-14
- Scope: `total-return-open-universe-v3-20260814`
- Status: **draft-not-frozen methodology; no formal replay, product approval or action; `q=0`.**

## Correction and boundary

H1–H3 are research concepts, not pre-registered executable hypotheses. Exact field dictionaries, transformations, lags, tie rules, decision calendars, OOS cohorts, source contracts, tax convention and R1/R2 approval are absent. The companion document is a draft test-only strategy mapping: it does map members to unitized weights and residuals for a later test, but is not authorised, source-tested or independently approved.

An open research universe permits every qualifying onshore public instrument to be considered under a frozen PIT rule. It does not allow retrospective selection. A formal test must still create a finite PIT member set every decision date, without a permanent product list, asset-class quota, cash target, reinvestment mandate or action.

The only objective is ex-post: each predeclared complete rolling five-year OOS window must have annualised net TWRR of at least 5%. This is not a guarantee, forecast, annual floor, probability or implementation permission.

## Common hard gates

Before a result is viewed, freeze for each hypothesis: exact field names, source and units; transformations, winsorisation/standardisation and invalid-value treatment; universe filters and threshold; all ties; lag; decision/session calendar; start/end dates; non-overlapping OOS cohorts; and every rolling endpoint. No parameter may be selected using OOS results. Preserve PIT member list, `as_of`, `available_at`, source archive ID, status, special-treatment, halt/limit and publication-time evidence. Later restatements cannot fill historical gaps.

Use raw prices plus a complete event ledger or one verified total-return series; do not add receipts to a series already adjusted for them. Dated proportional costs, unitized mechanics and source-tested action adapters must pass R1/R2. B0/B1 need identical valuation dates, receipt treatment, cost convention and PIT eligibility evidence.

## Receipt-state accounting — identical for strategy, B0 and B1

Record every settled dividend, fund/REIT distribution, coupon and redemption once in an internal receipt ledger: event ID, instrument ID, entitlement timestamp, ex/effective date, payment/settlement timestamp, gross amount, tax/fee amount, net amount, source reference and return-basis flag.

Credit net amount to an internal marked receipt state on its actual payment/settlement timestamp. It remains at nominal marked value through the tested OOS cohort; no interim return or automatic reinvestment is assumed, and the draft mapping does not reassign it at later decisions. A different treatment would require a new frozen rulebook revision before testing. This is test accounting, not a cash target or reinvestment mandate. External withdrawal is outside the design and needs a separately documented TWRR subperiod break.

## H1 — PIT A-share QVIM membership (draft-not-frozen)

**Concept:** liquid A-share QVIM membership may differ from a passive eligible-universe comparator after cost; it does not assert a factor premium or target attainment.

| Required future freeze | Current draft / hard gate |
|---|---|
| Inputs | PIT A-share listing, ST/special-treatment, raw bars, volume, halt/limit, delisting, actions, original financial timestamps and controller/issuer maps. Missing field fails eligibility. **Gate:** no authorised PIT archive. |
| Dictionary | Exact quality/value/investment/momentum field names, accounting definitions, units, reporting period, restatement rule, negative/missing treatment, transforms, standardisation and ties. **Gate:** `QVIM` is undefined. |
| Lag / membership | Financial data usable no earlier than first official session after full timestamp plus one session; market inputs end prior close. When frozen: `QVIM > 0` **and** top-decile cutoff; ties stable PIT security ID ascending. This is the same positive gate required by the mapping. **Gate:** listing age, liquidity formula, top-decile population, calendar and OOS cohorts unfrozen. |
| Review / events / costs | Proposed quarter-end, next valid session, common no-fill rule; dated proportional venue/broker/registration/transfer/tax/spread/slippage/participation inputs and full action ledger. Unsupported actions block. **Gate:** not authorised/source-tested. |
| B0 / B1 / q | B0 is common protected-liquidity function; B1 same base eligible universe without QVIM ranking after mapping authorisation. No B0/B1, receipt ledger, mapping approval, R1/R2 or risk approval: `q=0`. |

## H2 — timestamped earnings-repricing membership (draft-not-frozen)

**Concept:** public earnings information may differ from a passive event comparator after cost; it does not assume consensus availability, drift or an exit price.

| Required future freeze | Current draft / hard gate |
|---|---|
| Inputs | Immutable exchange/CNINFO ID, full publication timestamp/time zone, original reported metric, historical consensus snapshot timestamp, PIT status/bar/volume/halt/limit/controller/action data. **Gate:** no licensed consensus or complete revision-time archive. |
| Dictionary | Reported metric, consensus statistic, units, sign, share/one-off adjustments, denominator/zero handling, batch definition, standardisation and ties. **Gate:** `positive_surprise` is undefined. |
| Lag / membership | Use latest consensus demonstrably available strictly before full publication time; no target before next permitted session. When frozen: `positive_surprise > 0`, top-decile in a fully defined batch, stable announcement-ID ascending ties. **Gate:** holiday/batch, freshness, expiry, invalidation and OOS rules unfrozen. |
| Review / events / costs | Proposed event review/20-session expiry, common receipt/action/no-fill/cost rules; corrections/restatements/withdrawals need immutable linkage and frozen treatment. **Gate:** not authorised/source-tested. |
| B0 / B1 / q | B0 common protected-liquidity function; B1 same base event universe without surprise ranking after mapping authorisation. No records/mapping/B0/B1/R1/R2/risk approval: `q=0`. |

## H3 — total-return trend membership (draft-not-frozen)

**Permitted scope only:** A-shares, listed ETFs, public REITs, and direct sovereign/interbank bonds. Any added class requires a new authorised data contract and a rulebook revision.

**Concept:** total-return trend across only these classes may differ from a passive eligible-universe comparator after cost; it does not claim prediction or require any class to appear.

| Required future freeze | Current draft / hard gate |
|---|---|
| Inputs | PIT security/access master; raw price+event or verified total-return series; halts/limits/delistings/liquidity; ETF/REIT distributions; direct sovereign/interbank bond coupon, accrued-interest, maturity/redemption and valuation records; PIT look-through map. **Gate:** no authorised cross-instrument archive. |
| Dictionary | Exact 252/21 session calculation, venue calendar, total-return basis, non-common calendar, stale-price, accrued-interest, new-listing, missing-bar and tied-signal treatment. **Gate:** signal undefined. |
| Lag / membership | Inputs end prior official close; use only events available at cut-off. When frozen: strictly positive signal, full valid lookback and stable security-ID ascending ties. **Gate:** universe/calendar/OOS cohort rules unfrozen. |
| Review / B0/B1 / q | Proposed month-end/next valid session and common receipt/action/no-fill rules. B0 common protected-liquidity function; B1 same base universe without trend filter after mapping authorisation. No archive/mapping/costs/B0/B1/R1/R2/risk approval: `q=0`. |

## Precise missing data fields

`PL(t)` needs historical legal/operational access classification, security/return-stream ID, source archive ID, `as_of`, `available_at`, issuer and guarantor IDs, documented remaining term and modified duration, product terms, valuation price/NAV/accrued-interest basis and timestamp, settlement terms, dated proportional cost/tax fields, trading/suspension/default-like/stale-valuation state, and coupon/distribution/redemption/action records.

Every overlap record needs security ID, controller/issuer-group ID, exposure type, underlying ID and PIT weight, benchmark constituent IDs/weights for pooled instruments, and, where material, project/sponsor-manager/tenant-offtaker/refinancing-counterparty IDs/weights; each needs source archive ID, `as_of` and `available_at`. Missing look-through means ineligible, not independent.

## Formal admission

No hypothesis is pre-registered or testable until its frozen rules, authorised source manifest, receipt reconciliation, source-tested action adapters, **authorised and independently approved** draft mapping, B0/B1, R1/R2 and independent risk gates pass. Then disclose every predeclared complete OOS cohort and rolling-five-year endpoint, including every miss. Until then: `q=0`.

Machine-readable twin: `data/dynamic_rulebook_design_20260814.json`.
