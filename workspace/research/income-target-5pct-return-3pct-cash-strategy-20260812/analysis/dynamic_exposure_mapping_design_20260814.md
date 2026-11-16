# Dynamic Exposure-Mapping Design — OU-TR5-v1

- Date: 2026-08-14
- Scope: `total-return-open-universe-v3-20260814`
- Status: **draft test-only strategy mapping; not authorised, source-tested or independently approved; `q=0`.**

## What this artifact does and does not do

This artifact **does** specify draft test-only member-to-unitized-weight, residual, concentration, receipt-state and no-fill algorithms for H1–H3. It supplies a future strategy-mapping component, rather than only a membership concept. It does not name or approve a current product or portfolio, set a cash-income constraint, prescribe reinvestment or authorize action; it does specify a draft future selection rule for `PL(t)`.

Open universe means every qualifying onshore public instrument can be assessed under a frozen PIT rule. It does not mean a fixed list or retrospective selection. A formal strategy still needs a finite member set and deterministic weights every decision date. This mapping is draft-only because companion H1–H3 rules and sources have not been frozen or authorised.

## Common draft mapping algorithm

For active member `i`, the later authorised rulebook calculates a positive finite score `a_i` and 63-session realised total-return volatility `sigma_63,i` ending prior official close. Starting weight is `w_i = a_i / sum(a_i)`. Repeatedly apply: (1) 10% per listed security; (2) 20% per PIT controller/issuer group; (3) 20% per PIT economic-underlying group; and (4) reallocate excess pro rata by `a_i` only to uncapped members. Unallocable value is residual.

Economic-underlying groups are concentration controls, not asset-class quotas: same PIT look-through issuer, benchmark constituent, project, sponsor/manager, tenant/offtaker or other common-risk entity. No class is required to appear or receives preset weight. Formulas remain draft until field dictionaries and group taxonomy pass R1.

## Protected-liquidity residual function

`PL(t)` is a deterministic eligibility function, not a named holding. It may select only a record classified within the formal scope—A-shares, listed ETFs, public REITs, direct sovereign bonds or direct interbank bonds—and may receive residual/no-member unitized value only when its historical record has legal/operational access classification; security/return-stream ID; source archive ID; `as_of`; `available_at`; issuer/guarantor IDs; product terms; remaining term; modified duration; valuation price/NAV/accrued-interest basis plus timestamp; settlement terms; dated proportional cost/tax fields; trading/suspension/default-like/stale-valuation state; and complete coupon/distribution/redemption/action records.

It must be markable under strategy total-return convention and cannot breach existing issuer/guarantor cap. Future frozen ties are shortest remaining term, lower modified duration, then stable source ID ascending. Missing fields or no passing record makes `PL(t)=unavailable`; the replay is invalid and no synthetic return is used. These exact fields are currently unavailable, so `PL(t)` is not source-tested and cannot support a result.

## Receipt-state accounting — identical for strategy, B0 and B1

Every settled dividend, fund/REIT distribution, coupon or redemption is recorded once with event ID, instrument ID, entitlement timestamp, ex/effective date, payment/settlement timestamp, gross amount, tax/fee amount, net amount, source reference and return-basis flag. Credit net amount once to internal marked receipt state at actual payment/settlement timestamp.

The receipt state stays at nominal marked value through the tested OOS cohort; no interim return or automatic reinvestment is assumed, and this draft mapping does not reassign it at later decisions. A different treatment would require a new frozen rulebook revision before testing. This is accounting, not a cash target or reinvestment mandate. An external withdrawal is outside this test-only design and requires a separately documented TWRR subperiod break.

## No-fill, exit and event state

Calculate after designated close; a paper target is eligible no earlier than next permitted session. Halt, limit lock, missing valid opening mark, settlement restriction or participation shortfall leaves prior marked state and target difference in residual/receipt state. Never manufacture a fill, substitute, stop exit or retrospective exit. Reconsider differences only under same then-current rule. Delisting needs source-labelled cash settlement. Rights, mergers, spin-offs, conversions, restructurings and unsupported actions block replay until source-tested adapters exist.

## H1 draft mapping — PIT A-share QVIM

- Membership consistency: H1 membership requires `QVIM > 0` and top-decile rank. Therefore `a_i = QVIM_i / sigma_63,i`; no non-positive QVIM member reaches mapping.
- Clock: proposed quarter-end close, then next permitted session.
- B1: H1 base-eligible PIT universe before QVIM rank, `a_i = 1 / sigma_63,i`, identical caps, receipt state, costs and `PL(t)`.
- Required map: security ID, controller/issuer group, exposure type, underlying ID/PIT weight, source archive ID, `as_of`, `available_at`.
- `q=0`: QVIM dictionary, PIT archive, group map, costs, receipt ledger, `PL(t)`, B0/B1 and R1/R2/risk approval absent.

## H2 draft mapping — earnings repricing

- Membership score: after frozen positive-surprise eligibility, `a_i = positive_surprise_i / sigma_63,i`.
- Clock: proposed valid public-event review with next permitted-session target; active-event refresh follows official close.
- B1: same PIT base event universe/frozen active window without surprise rank, `a_i = 1 / sigma_63,i`, identical caps, state, receipt treatment and `PL(t)`.
- Required map: H1 fields plus immutable announcement ID and complete publication/revision linkage; multiple events in one group share cap.
- `q=0`: surprise dictionary, PIT consensus/publication archive, action/cost ledger, `PL(t)`, B0/B1 and R1/R2/risk approval absent.

## H3 draft mapping — permitted-class total-return trend

**Scope only:** A-shares, listed ETFs, public REITs, direct sovereign bonds and direct interbank bonds. Another class requires a new authorised data contract and frozen rulebook revision.

- Membership score: after frozen strictly-positive 252-minus-21-session total-return eligibility, `a_i = TR_(252 minus 21),i / sigma_63,i`.
- Clock: proposed month-end close, then next permitted session.
- B1: same PIT base eligible universe/valid lookback without trend filter, `a_i = 1 / sigma_63,i`, identical caps, receipt treatment, costs and `PL(t)`.
- Required map: all H1 fields; pooled instruments need benchmark constituent IDs/PIT weights; REIT-like structures need material project, sponsor/manager, tenant/offtaker and refinancing-counterparty IDs/PIT weights. Missing field means ineligible, not independent.
- `q=0`: no cross-instrument total-return/coupon/action archive, look-through map, instrument adapter, `PL(t)`, B0/B1 or R1/R2/risk approval.

## B0, R1/R2 and formal admission

B0 is the same 100% `PL(t)` functional comparator under identical receipt, valuation and proportional-cost rules; it is unavailable. B1 is the matched comparator per hypothesis. Neither is frozen. R1 must approve formula hash, field definitions, caps, group taxonomy, `PL(t)`, receipt state, no-fill state and B0/B1 algorithms. R2 must approve authorised immutable PIT archives, source-tested action adapters, dated costs, unitized-engine reconciliation and walk-forward dry run. Until source authorisation, R1, R2 and independent risk gates pass, this remains a draft test-only strategy mapping and `q=0`.

Machine-readable twin: `data/dynamic_exposure_mapping_design_20260814.json`.
