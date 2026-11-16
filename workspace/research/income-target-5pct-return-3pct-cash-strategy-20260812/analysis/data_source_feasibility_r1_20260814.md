# R1 Data-Source Feasibility — 2026-08-14

## Outcome

An authorized, point-in-time replay is not yet feasible. Its formal scope is limited to A-shares, listed ETFs, public REITs and direct sovereign/interbank bonds. The official evidence shows that public exchange, manager, depository and market-infrastructure documents can validate product terms and sampled events, but they do not by themselves establish a complete historical PIT archive or the right to ingest, retain and derive data. No subscription, licence, API right, authorized vendor relationship or archive right is presumed. All quantities remain `q=0`.

The target, if the gates are eventually satisfied, is only a unitized and scale-neutral ex-post replay of predeclared rolling five-year cohorts using net TWRR. It does not introduce a product, allocation, cash-income objective, automatic-reinvestment assumption or execution authorization.

## Documented sources and boundaries

| Official source | What it documents | What it does not establish |
|---|---|---|
| SSE public-data catalogue | Public categories for calendar, suspensions, dividends/bonus issues, fund data, ETF creation-redemption lists, public-REIT NAV/market data and bond data. | A complete versioned historical archive, PIT availability history, bulk-use terms or derived-data permission. |
| SZSE technical services | Market-data interface and technical-service channels. | This research's entitlement to retain a Shenzhen-listed historical PIT archive. |
| CSI 300 methodology | Daily TRI/NTRI, cash-dividend tax treatment, reference-price adjustments and constituent-maintenance mechanics. | Investor-level product return, trade costs, or a licensed historical constituent/value archive. |
| CFETS market-data service | Interbank quotation, trade-related, basic, benchmark and historic data coverage. CFETS says written authorization is required for use. | Permission for this case; public bond notices cannot replace a licensed price/quote history. |
| ChinaBond terms | ChinaBond index/data-product channels and need for separate written application in stated benchmark/product contexts. | The exact rights to use, retain and derive the data needed here. |
| ChinaClear interface specification | Semantics for distribution, interest, bond-redemption and conversion fields. | Public or research access to the historical participant event archive. |

## Hard acceptance matrix

| Required block | Minimum PIT fields | Public official role | Formal-replay acceptance evidence | Status |
|---|---|---|---|---|
| Security master | ID, venue, structure, list/delist/status history, `as_of`, `available_at`, revisions | Reconcile individual exchange/issuer changes | Authorized historical-version archive, field dictionary, hashes and written internal research/derivation right | Blocked |
| Protected-liquidity selector `PL(t)` | Formal-scope classification; legal/operational-access classification and flag; default-like/credit-event state and flag; remaining term; duration and definition; event/valuation-staleness flags and thresholds; PIT source timestamps; `as_of`, `available_at`, revisions | Reconcile isolated maturity, duration, event and valuation facts | Entitled PIT selector-input archive, field definitions/flags, explicit not-applicable taxonomy codes and historical `PL(t)` reconstruction samples | Blocked |
| Common-risk / 20% issuer-controller-look-through mapping | Issuer, guarantor, controller, beneficial-owner; underlying constituents/weights; sponsor/manager/project/tenant/offtaker/refinancing-counterparty; crosswalk; aggregation taxonomy/version | Reconcile selected legal, ownership and project relationships | Entitled, versioned PIT relationship graph, constituent snapshots, identifier crosswalk and aggregation/cap-taxonomy evidence | Blocked |
| A-share / listed ETF / public-REIT EOD data | Raw OHLC, volume, turnover, pre-close, halt, limits, session and correction flags | Exchange-page cross-check | Entitled SSE+SZSE PIT archive, revision policy and raw payload manifest | Blocked |
| Actions / distributions | Announcement/ex/record/payment dates, cash/share/rights terms, tax, cancellation/revision | Primary issuer/exchange/CSDC event reconciliation | Complete normalized event ledger linked to source documents | Blocked |
| ETF / public-REIT mechanics | NAV, market close, distributions, splits, creation/redemption lists, IOPV if used, project capital events | Manager and SSE legal-document validation | Dated product-event archive joined to market prices | Blocked |
| Direct sovereign / interbank bonds | Terms, coupon/accrual/redemption, EOD clean/dirty price/yield, quotes, `as_of`, `available_at` | MOF/CFETS notice validation; ChinaBond reference checks | CFETS or authorized-provider written licence plus price/accrual/coupon archive | Blocked |
| Benchmark TRI / membership | Version, TRI/NTRI type, levels, members, weights, dates, tax/action convention | CSI methodology validation | Provider confirmation and historical constituent/value archive | Blocked |
| Costs / execution | Effective fee/tax schedule, quote/spread method, liquidity, settlement, no-fill state | Rules/mechanics reconciliation | Authorized fee schedule and entitled quotes; predeclared scale-neutral fill model | Blocked |
| Provenance | Owner, source request ID, `as_of`, `available_at`, retrieval, hash, licence, retention/revision | Publication-date cross-check | Accountable owner attestation and immutable archive | Blocked |

## Non-negotiable gates

1. A written entitlement must cover the authorized user/intermediary, fields, the formal scope, historical and PIT coverage, internal research purpose, retention, archival/derived-output rights, restrictions, limits and expiry.
2. Each required field must be covered for the formal scope only: A-shares, listed ETFs, public REITs and direct sovereign/interbank bonds. A missing event or field blocks its cohort.
3. At each timestamp `t`, a dynamic `PL(t)` candidate must be classified into one of the four formal-scope classes. It must also have PIT legal/operational-access classification and flag, and PIT default-like/credit-event definition and state flag. The access flag must distinguish eligible, restricted, suspended, unavailable and unknown states; it does not assert research data or trading entitlement. An out-of-scope, unknown or missing state blocks the cohort.
4. At each timestamp `t`, dynamic `PL(t)` must use remaining term, duration, event-staleness and valuation-staleness fields. Each must be an entitled PIT value, or an explicitly taxonomy-coded not-applicable state with a documented source basis. Unknown, stale, carried-forward or unversioned values are missing.
5. The 20% issuer/controller/look-through cap requires entitled PIT mapping for issuer, guarantor, controller, beneficial owner, underlying constituents and weights, plus each applicable fund/REIT sponsor, manager, project, tenant, offtaker and refinancing counterparty. A versioned identifier crosswalk and aggregation taxonomy must make the cap reproducible at `t`.
6. Every input must preserve `as_of` and `available_at`, revision history, raw records and content hashes.
7. Return reconciliation must pass a cash distribution, share action, rights/non-standard event, ETF/REIT distribution, halt/limit lock and sovereign coupon/redemption sample without double counting.
8. The unitized scale-neutral replay must use authorized fee/tax inputs and an entitled, frozen quote/spread/slippage method, preserving settlement and no-fill states.

If any applicable field required by `PL(t)` or the common-risk mapping is absent, or if a `PL(t)` candidate is out of formal scope, no partially observed cohort may be admitted. It cannot be proxy-filled or assumed to pass the 20% cap; it remains blocked and `q=0`.

Raw documentation and hashes: `sources/probe-data-source-continuation-20260814/manifest.json`. Field-level matrix: `data/data_source_feasibility_r1_20260814.json`.

Conclusion: official public documents are valid primary reconciliation evidence, not a substitute for a licensed/authorized PIT data system. No entitlement is evidenced; the protected-liquidity and common-risk/look-through field block is not passed; and `q=0` remains binding.
