# C37 — Domestic ETF / Index Total-Return Source Route Gate

## Decision

**As of 2026-08-15 (Asia/Shanghai), the result is NO-GO for an actual historical test of a new domestic ETF investor-total-return hypothesis using a public-primary-source-only event ledger.** This is a source-governance result, not an investment view, product selection, allocation, performance result, or external-action instruction.

The narrow conclusion is that the reviewed public primary sources do not, in combination, close every required historical field: a point-in-time eligible universe and lifecycle history; an unambiguous return basis; dated distribution/corporate-action and term changes; historical fees and investor-specific taxes; observable executable prices and no-fill treatment; source-side availability/revision history; and retained-data/replay/derivation rights. This does **not** assert that no such source can exist anywhere. It says that no accepted source combination was identified and retained by this cutoff.

This is an independent data-route gate for a new domestic ETF/index research hypothesis. It does not re-run, amend, rescue, or select any existing candidate protocol. No ETF, index, manager, broker, account, or strategy rule is selected here.

| Route assessed | Status | Permitted conclusion |
|---|---|---|
| Historical ETF investor total-return and event ledger, public primary sources only | **NO_GO_PUBLIC_PRIMARY_HISTORICAL_TEST** | No actual historical test, return claim, valuation input, or strategy-operability conclusion. |
| Historical official total-/net-return index benchmark | **CONDITIONAL_NOT_ACCEPTED** | Could become a benchmark-only research input after a per-index data and rights contract is closed; it cannot stand in for ETF investor return. |
| Prospective public-primary observation ledger | **CONDITIONAL_OBSERVATION_ONLY** | A forward capture protocol may be designed after terms/rights confirmation. It cannot repair missing historical point-in-time data and produces no present action. |
| Licensed exchange/provider delivery | **OUTSIDE_PUBLIC_ONLY_SCOPE** | A possible later procurement route, conditional on written contract and actual field delivery; no entitlement or license is inferred here. |
| Current research disposition | **NO_ACTION** | No product/index selection, transaction, allocation, recommendation, or performance forecast. |

## Scope, cutoff, and evidence boundary

- Case: domestic-5pct-target-paper-strategy-20260815.
- Cutoff: 2026-08-15, Asia/Shanghai. Statements use only source routes reviewed by that date.
- Test object: a yet-unselected domestic ETF/index hypothesis. No calculation or historical return test was run.
- Public-primary route means a regulator, exchange, index-provider, fund-manager, or other first-party record. A public webpage is not automatically a retention, normalization, replay, derived-analysis, or independent-review entitlement.
- Retained evidence cited below remains in a sibling research case. C37 creates no raw-source archive and must not be read as upgrading those captures into a full dataset.
- No broker report, broker forecast, target price, or Street-consensus claim was used. Such evidence is not applicable to this source-route gate.

## Hard gates for an investor total-return ledger

An actual historical test is admissible only when all gates are closed for every included product/share class and all dates. A clean market-price proxy may be useful as an explicitly limited diagnostic, but it is not an investor total-return result.

| Gate | Required point-in-time field or control | Why it is non-substitutable | Current result |
|---|---|---|---|
| G1 universe and survivorship | Eligible universe at each decision time; listing, delisting, merger, termination, suspension/resumption, share-class and eligibility history | A live list cannot identify products that disappeared or were unavailable on the original date. | **Not closed** |
| G2 return basis | Explicit distinction among secondary-market price return, NAV return, accumulated-NAV return, total return, and net return; adjustment/reinvestment convention | Combining an adjusted series with cash distributions can double count. NAV cannot automatically be equated to the return received by a secondary-market investor. | **Not closed** |
| G3 events and terms | Dated, complete, versioned distribution, split/consolidation, fund-share, termination, fee, benchmark, and material-contract events | A return series cannot be independently reproduced without event dates, effective dates, and source precedence. | **Not closed** |
| G4 cost and tax | Historic management/custody and other fund costs as applicable; transaction fees, tax treatment, settlement, and investor/account assumptions | Public generic disclosures do not determine the cash outcome of a specific investor/account or historical trade. | **Not closed** |
| G5 executable market path | Decision-time market price, bid/ask or a conservative pre-declared fill rule, liquidity/depth, trading status, price limits, no-fill and settlement handling | End-of-day OHLCV alone cannot establish a fill or failure to fill. | **Not closed** |
| G6 point-in-time availability | Published-at, available-at, correction/revision history, retrieval timestamp, raw object hash, parser version | Retrospectively queried values do not prove what was knowable on the decision date. | **Not closed** |
| G7 rights and auditability | Written terms or contract confirming permitted retrieval, retention, normalization, replay, derived analysis, and independent review | Website browsing/download terms are not a dataset license or audit-right grant. | **Not established** |
| G8 pre-specification | Frozen universe, field dictionary, event precedence, cost assumptions, execution convention, test window, holdout, and failure rule before dataset access | Otherwise a later data choice can silently choose the result. | **Specification possible; actual test not certifiable** |

The hard-gate rule is conjunctive: one material unresolved field makes the historical investor-total-return test inadmissible. No proxy, current product page, or generic disclosure is permitted to fill a missing gate silently.

## Reviewed primary-source routes and what they actually establish

The required source-registry fields are supplied here and in the machine-readable twin. The prescribed source-quality enum does not contain an official-exchange or official-regulator value. For registry compatibility, official exchange/regulator Tier-1 records are tagged official_filing while source_type preserves the precise authority; that tag does not mean an exchange market-data response is an issuer filing.

| ID | Source and original URL | Type / quality / tier | Retained evidence or capture status | Covers | Material limitation and valuation consequence |
|---|---|---|---|---|---|
| S01 | SSE ETF daily market-price endpoint: <https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{fundCode}?callback=c7probe&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=0&end=5000> | official_exchange_market_data_endpoint / official_filing / Tier 1 | Referenced retained manifest: sibling C7 capture, SHA-256 bb0550c4eaa207ece0eaa00c2410eff13516ade63bc859136a7848f1891822b0; captured 2026-08-14/15 | Retrospective daily OHLCV observations for sampled SSE ETFs | No adjustment basis, distribution/event ledger, NAV/IOPV, historical availability/revisions, status, depth/fills, costs/tax, or rights. **Watchlist only; blocks investor-return valuation.** |
| S02 | SSE fund-list page and FUND_LIST endpoint: <https://www.sse.com.cn/assortment/fund/list/> and <https://query.sse.com.cn/commonSoaQuery.do> | official_exchange_listing_endpoint / official_filing / Tier 1 | Referenced retained manifest: sibling R4 probe, SHA-256 908a1d8dffa5aafa8894411609d53642ecae588bbd2ffefc67b6030d2ba1d5ad; captured 2026-08-15 | Current live listing enumeration, identity/classification and some listing-date fields | No historical universe snapshot, lifecycle/status, delisting, suspension, stable as-of version, or retained full cohort. **Blocks valuation/test universe.** |
| S03 | CSRC Measures for Information Disclosure of Publicly Offered Securities Investment Funds: <https://www.csrc.gov.cn/csrc/c106256/c1653985/content.shtml> | official_regulatory_rule / official_filing / Tier 1 | Primary URL consulted; raw body was not copied into this case | Regulatory disclosure route; daily NAV and accumulated-NAV disclosure requirement for ordinary open funds, subject to the rule | A disclosure obligation is not a unified historical total-return/event database, a per-product completeness proof, or a secondary-market investor-return definition. **Watchlist only.** |
| S04 | CSRC 2020 notice identifying the fund electronic-disclosure route: <https://www.csrc.gov.cn/csrc/c101950/c1047975/1047975/files/%E9%99%84%E4%BB%B61_%E4%B8%AD%E5%9B%BD%E8%AF%81%E7%9B%91%E4%BC%9A%E5%86%B3%E5%AE%9A%E4%BF%AE%E6%94%B9%E7%9A%84%E8%A7%84%E8%8C%83%E6%80%A7%E6%96%87%E4%BB%B6.pdf> (identifies http://eid.csrc.gov.cn/fund) | official_regulatory_notice / official_filing / Tier 1 | Primary URL consulted; no complete EID archive/schema/rights capture accepted | Potential centralized route for fund operations and temporary disclosures | Completeness, immutable history, machine-readable schema, source timestamps, historical event coverage, and rights were not established. **Blocks valuation until closed.** |
| S05 | SSE ETF PCF disclosure page: <https://www.sse.com.cn/disclosure/fund/etflist/> | official_exchange_disclosure_page / official_filing / Tier 1 | Route observed; no full historical PCF/version archive accepted | Forward daily PCF source hierarchy; page states manager PCFs are disclosed before trading and exchange morning announcement controls on conflict | No accepted full historical archive, revision trail, event mapping, or replay rights. **Prospective watchlist only.** |
| S06 | China Securities Index governance / methodology route: <https://www.csindex.com.cn/#/about/governance/?lang=zh> | official_index_provider_route / industry_database / Tier 1 route | Route observed; no per-index historical level file, methodology version, or rights record retained | Shows the official index-provider route through which an exact price/total-return/net-return series definition would need to be obtained | No exact index code/variant, historical level delivery, rebalance/corporate-action file, vintage, or license was accepted. **Context only; index benchmark remains conditional.** |
| S07 | SSE Market Data Products — Historical Data: <https://english.sse.com.cn/markets/dataservice/products/> | official_exchange_data_product_page / official_filing / Tier 1 | Retained in sibling R3 route/rights manifest, file SHA-256 97ae19ecd969ec017290252e3cc5ca65f47054c1bd9edb40c594795fcbcd6a96 | Indicates a historical-data subscription route, including stated historical market-data categories | A product page does not establish ETF/event coverage, delivery, point-in-time fields, revisions, or a contract. **Blocks a public-only proof; licensed route is outside scope.** |
| S08 | SSE Website Legal Statement: <https://www.sse.com.cn/home/legal/>; SZSE Website Legal Statement: <https://www.szse.cn/application/laws/> | official_exchange_terms_page / official_filing / Tier 1 | Retained in sibling R3 route/rights manifest; file SHA-256 a19b622fc5b5baa6bea83804476dc908ff426ef244f3d3c589741a36419382e6 and 5398c463263421a98cbf90918dcaa16d6d70ef80f2052a9d0c19c1606ab27936 | Website browsing/download conditions and restrictions | The pages do not establish the required retention, replay, derivation, normalization, or independent-review rights. They do not prove use is unlawful; the required rights are **not established**. **Blocks valuation/test admission.** |
| S09 | AMAC public-fund disclosure rule route: <https://fg.amac.org.cn/governmentrules_3854/zcgz_gfxwj/gfxwj_gmjj/gfxwj_gmjj_xxpl/202003/t20200312_24756.html> | official_industry_rule / official_filing / Tier 1 | Primary URL consulted; no normalized historic event data retained | Periodic reporting includes disclosure expectations for distributions and tax-related items | Periodic disclosure is not a complete transaction-date, product/share-class, investor-specific event/tax ledger. **Watchlist only.** |

The S01, S02, S07, and S08 source descriptions are anchored to retained first-party manifests, not to an assertion that the original services grant a reusable historical dataset. S03–S06 and S09 are recorded as primary-route evidence, but their raw bodies were not newly archived in this case; that absence is itself a reproducibility limitation.

## Coverage matrix

| Required ledger field | Public-primary route observed | Evidence status | Why it cannot be promoted | Gate effect |
|---|---|---|---|---|
| Point-in-time ETF universe, lifecycle and survivorship | SSE FUND_LIST current endpoint | Partial | Live enumeration had no reliable historical as-of snapshot, lifecycle state, delisting, or full archived cohort. | G1 fails |
| Daily secondary-market OHLCV | SSE dayk endpoint | Partial | Retrospective sample supports daily OHLCV observation only; adjustment/event/available-at semantics are absent. | G2/G5/G6 fail |
| NAV and accumulated NAV | CSRC disclosure rule and manager/e-disclosure route | Partial | Rule establishes a disclosure obligation, not a collected, versioned, complete historical file by product/share class. | G2/G3/G6 fail |
| Distributions, splits, term/fee changes, termination | Fund-manager notices, exchange notices, EID route, PCF route | Partial | No complete event inventory, precedence rule, historical archive, or effective-date/revision record was accepted. | G3/G6 fail |
| Fund fees and historic terms | Prospectus/contract/manager disclosures are potential primary records | Partial | No product-neutral historical fee/term ledger is frozen; fee change dates and accrual conventions remain unclosed. | G3/G4 fail |
| Tax | Fund and regulatory disclosure routes | Missing for the required use | No investor/account/date-specific tax dataset or treatment hierarchy was established. | G4 fails |
| Total-/net-return index levels | CSI methodology/index-provider route; possible contracted data route | Partial | No exact variant, historical levels, constituent/event vintage, or rights package. | G2/G3/G6/G7 fail |
| IOPV, trading status, price limits, suspension and market microstructure | Exchange ETF/market pages provide current route surfaces | Partial | No historical, versioned IOPV/status/depth or decision-time executable record accepted. | G5/G6 fail |
| Bid/ask, depth, fills/no-fills, brokerage costs and settlement | No public primary historical ledger accepted | Missing | Exchange closing prices and generic rules cannot prove a historical fill or individual cost/settlement result. | G4/G5 fail |
| Source rights and reviewability | SSE/SZSE terms plus SSE data-product route | Not established | No written grant or contract evidences permitted retention, replay, derivation, normalization, or independent review. | G7 fails |

## Source-exhaustion record

This table is the C37 mirror of an exhaustion log. It intentionally does not create or alter the case-level source_exhaustion_log files owned elsewhere.

| Probe ID | Query or target | Source attempted | Result | Reason unresolved | Artifacts saved | Next verification path | Blocks valuation/test? | Owner |
|---|---|---|---|---|---|---|---|---|
| E01 | Historical, status-qualified domestic ETF universe | SSE FUND_LIST | Current endpoint enumeration demonstrated; no historical snapshot accepted | No source as-of version, lifecycle, delisting or full historical cohort | Sibling R4 manifest (SHA-256 908a…d5ad) | Obtain an authorized, date-stamped historical master with life-cycle events and replay rights | Yes | Future data-governance owner |
| E02 | Secondary-market return basis and adjustment events | SSE dayk | Retrospective OHLCV observation demonstrated | Adjustment convention, events, availability/revisions and executable path absent | Sibling C7 manifest (SHA-256 bb05…2b0) | Obtain provider field dictionary plus dated event/adjustment and available-at history | Yes | Future market-data owner |
| E03 | NAV, accumulated NAV, distribution and fund-event ledger | CSRC rule / EID route / manager notices | Disclosure obligations and routes identified | No complete product/share-class event archive, source precedence, dates, or version history accepted | URLs only in C37; no raw C37 archive | Before any product selection, retain complete official notices/terms/NAV history with hashes and timestamps | Yes | Future fund-disclosure owner |
| E04 | Total-/net-return index benchmark series | CSI route and historical-data route | Concept and provider route identified | No exact index variant, levels, methodology/corporate-action version, vintage, or rights package | URLs only in C37 | Obtain per-index official historical delivery and methodology/version files under accepted rights | Yes | Future index-data owner |
| E05 | Retention/replay/derivation/audit rights | SSE/SZSE terms; SSE/SSEInfo data service routes | Public terms and potential paid route identified | Neither establishes a user-specific data license or audit rights | Sibling R3 manifest (SHA-256 91a2…9f45) | Written permission/contract defining scope, storage, derived use, replay and reviewer access | Yes | Future legal/data-governance owner |
| E06 | Decision-time executable price, costs, settlement and no-fill | Exchange market surfaces; no broker/account record | No accepted historical transaction-level ledger | Closing OHLCV is not a fill; account-specific commission/tax/settlement cannot be inferred | None | Freeze conservative fill/no-fill rule and obtain allowed source records; account-specific facts remain outside public-only proof | Yes | Future execution-data owner |
| E07 | Historical IOPV, status, halts/resumptions and limits | Exchange ETF/market pages and PCF route | Current/forward route surface observed | No historic versioned IOPV/status archive or replay evidence | No accepted archive | Forward-capture raw daily objects and seek historical delivery | Yes | Future market-data owner |
| E08 | Investor-specific tax treatment | Regulatory/fund disclosure routes | General disclosure route only | Treatment can vary by instrument, date, investor/account and transaction; no governing ledger frozen | URLs only in C37 | Obtain dated authoritative tax treatment and explicitly scoped account assumptions before any test | Yes | Future tax-governance owner |

## What can be pre-specified now, and what cannot

A research protocol can be written now, but it cannot make an actual historical test clean merely by declaring rules after discovering incomplete data. The following data contract must be signed off before any calculation:

1. Freeze the hypothesis, eligible universe definition, start/end dates, decision timing, reconstitution frequency, holdout, and all failure/no-action rules before access to the final dataset.
2. Assign one primary source and one documented fallback for each product/share-class/date field; record source URL, document id, published_at, available_at, retrieved_at, HTTP metadata, content hash, parser version, and source version.
3. Define a mutually exclusive return basis. For a secondary-market ETF investor result, retain market-price convention, cash distribution treatment, reinvestment timing, tax convention, fee convention, and a prohibition on combining adjusted price with separately reinvested distributions unless the provider documents that convention.
4. Build an event ledger with announce, ex-date, record date, payable date, effective date, source precedence, prior/new terms, correction/revision link, and non-applicability reason.
5. Build a universe ledger with inception, listing, suspension, resumption, delisting, merger, termination, share-class conversion, eligibility and source version.
6. Freeze an execution convention that can fail: decision-time field availability, price timestamp, bid/ask or conservative fallback, liquidity/depth threshold, price limit, no-fill, partial-fill, fees, taxes, T+1/settlement, and missing-data response.
7. Obtain written data-use terms sufficient for retention, normalization, reproducible replay, derived analysis, and independent review. If not granted, the test remains inadmissible even if public pages can be viewed.
8. Preserve an immutable raw and normalized archive, a data-dictionary hash, an event-reconciliation log, and an independent rerun procedure.

At present, only the prose specification portion of this list can be pre-declared. The closed field set, point-in-time availability, legal/use boundary, and historical event corpus are absent. Accordingly, a historical result cannot be described as a pre-specified, reproducible test.

## Conditional prospective capture route — observation only

If and only if written terms permit the required use, a forward observation ledger could begin without selecting a product or making an external action. Each daily capture would retain raw official objects, source URL, HTTP status and headers, retrieved_at, published_at, available_at when stated, SHA-256, parser version, and a human-readable exception note.

| Daily/when-issued object | Primary route to capture | Minimum fields | Boundary |
|---|---|---|---|
| Universe and status | Exchange listing and trading-status records | code/share class, status, listing/lifecycle event, source timestamp/version | Must include disappeared products and corrections, not only current rows. |
| Market observation | Exchange quote/market data | timestamped price, bid/ask if available, volume/turnover, limits, halt/status | Do not call it executable without a predeclared fill/no-fill rule and sufficient fields. |
| Fund-value observation | Fund manager / official fund disclosure route | NAV, accumulated NAV, share class, publication time, source document/version | Do not equate with secondary-market investor return without an explicit basis. |
| ETF creation/redemption file | Exchange PCF and controlling exchange announcement | PCF version, publication time, source precedence, changes/corrections | PCF is not a replacement for investor distributions, costs, or historical IOPV. |
| Corporate-action and distribution event | Manager, trustee and exchange official notices | event type, announce/ex/record/pay/effective dates, amount, tax basis, terms, correction link | Reconcile every event before any return calculation. |
| Index benchmark | Index-provider methodology and level file | exact variant, level date, publication time, methodology/version, rebalance/event record | Benchmark-only; never relabel as ETF investor total return. |
| Cost, tax and settlement | Applicable official/broker/account records within permitted scope | dated fee schedule, tax rule, settlement rule, account-specific exception | Account-specific facts cannot be inferred from public generic pages. |

Forward capture is not retroactive point-in-time evidence. It can help construct a later observation record, but cannot repair past survivorship, revisions, data availability, event history, execution, or rights gaps. It therefore remains CONDITIONAL_OBSERVATION_ONLY, not a strategy result.

## Claim audit

Every high-impact statement below has a confidence label and adopted wording. None may enter valuation or a main research conclusion as a stronger statement.

| Claim | Company | Customer/platform | Source file | Original URL | Source type | Source quality | Confidence | Used in valuation? | Adopted wording |
|---|---|---|---|---|---|---|---|---|---|
| C37-CL-01: official daily price route | No issuer/fund selected | SSE ETF market-data endpoint | Sibling C7 manifest, SHA-256 bb0550c4eaa207ece0eaa00c2410eff13516ade63bc859136a7848f1891822b0 | <https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{fundCode}?callback=c7probe&select=date%2Copen%2Chigh%2Clow%2Cclose%2Cvolume&begin=0&end=5000> | official_exchange_market_data_endpoint | official_filing | High | No — blocks investor-return valuation | “The retained SSE endpoint evidence supports retrospective daily OHLCV observation for sampled ETFs; it does not establish a point-in-time total-return, event, execution, or rights ledger.” |
| C37-CL-02: current universe route | No issuer/fund selected | SSE FUND_LIST | Sibling R4 manifest, SHA-256 908a1d8dffa5aafa8894411609d53642ecae588bbd2ffefc67b6030d2ba1d5ad | <https://query.sse.com.cn/commonSoaQuery.do> | official_exchange_listing_endpoint | official_filing | High | No — blocks universe admission | “The captured endpoint supports a current live listing enumeration, not a date-specific eligible universe or survivorship history.” |
| C37-CL-03: NAV disclosure route | No issuer/fund selected | CSRC fund-disclosure system | Not locally retained in C37; official rule URL recorded | <https://www.csrc.gov.cn/csrc/c106256/c1653985/content.shtml> | official_regulatory_rule | official_filing | Medium-high | No — watchlist only | “The rule supports an official NAV/accumulated-NAV disclosure route for ordinary open funds; it does not by itself supply a complete historical product-level investor total-return ledger.” |
| C37-CL-04: index benchmark source route | No issuer/index selected | CSI | Not locally retained in C37; official route URL recorded | <https://www.csindex.com.cn/#/about/governance/?lang=zh> | official_index_provider_route | industry_database | Medium | No — benchmark conditional only | “The official index-provider route identifies where an exact index series definition would need to be obtained; no exact price/total-return/net-return variant, historical level file, vintage, or rights package has been accepted here.” |
| C37-CL-05: public-primary historical ETF investor test | No issuer/fund selected | All reviewed routes | This C37 gate and exhaustion record | See S01–S09 | synthesized_source_governance_assessment | corpus_gap | High | No — blocks valuation/test | “As of the cutoff, no reviewed public-primary source combination closes all hard gates for an actual historical ETF investor-total-return/event-ledger test.” |
| C37-CL-06: action boundary | No issuer/fund/index selected | Not applicable | Research brief and this C37 | Not applicable | scope_control | corpus_gap | High | No | “C37 selects no product or index and gives no allocation, transaction, recommendation, or return expectation.” |

## Final governance recommendation

**NO-GO. Do not compute, publish, or rely on a historical ETF investor-total-return result for the new hypothesis under the reviewed public-primary-only route.** Keep the work at source-route research. A pure official total-/net-return index series may be evaluated later only as a separately labelled benchmark after its exact series, historical delivery, methodology/version record, point-in-time availability, and rights are independently closed. A forward raw-source capture plan may be prepared only after rights confirmation; it remains observation-only and does not constitute a product decision or external action.

### Limitations

1. This is not a legal opinion. It records that necessary rights were not established from reviewed public pages; it does not label any use unlawful.
2. No full historical ETF universe, event archive, broker cost file, investor tax ledger, or market microstructure dataset was purchased, requested, or received.
3. A primary URL without a retained raw body is weaker reproducibility evidence than a hashed local capture and is deliberately not treated as a closed field.
4. No inference about future availability, performance, suitability, or investability is permitted from this document.
