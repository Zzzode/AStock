# R4 SSE ETF Public-Universe Readiness — 2026-08-15

## Conclusion

Conditional pass for a research-only current-list discovery snapshot; fail for
status-qualified, point-in-time, event-aware, rights-aware, or executable
cohort formation.

SSE FUND_LIST can enumerate a broad live listing snapshot using fundType and
subClass filters plus page numbers. The captured master request returned 893
records over 179 pages at a five-row page size. It cannot establish a
date-specific eligible or executable ETF cohort because the response has no
explicit lifecycle/trading status, source as-of timestamp/version, dated
events, rights/access, price, NAV, or execution fields.

Raw evidence and hashes are in
sources/probe-r4-sse-etf-universe-20260815/manifest.json. This file's
machine-readable twin is
analysis/r4_sse_etf_public_universe_readiness_20260815.json.

## Enumeration evidence

The filter used fundType=00 and subClass values
01,02,03,04,06,08,09,31,32,33,34,35,36,37,38. These are objective API codes;
the response does not embed a textual codebook.

| Query partition | Total | Pages at size 5 |
|---|---:|---:|
| All configured codes | 893 | 179 |
| 01,03,08,09,31 | 725 | 145 |
| 02,32,36,37 | 34 | 7 |
| 33,34,35 | 126 | 26 |
| 06,38 | 8 | 2 |
| Partition sum | 893 | — |

Master page one returned 510010, 510020, 510030, 510040, and 510050.
Master page two returned 510060, 510090, 510100, 510130, and 510140. The
sample pages are disjoint, demonstrating pagination advancement.

This is not a full 893-row archive. No server snapshot ID, query-as-of time,
or stable cursor is returned, so a full live-page pull can drift. The response
also duplicates rows in pageHelp.data and top-level result; downstream
collection must consume one representation only. The partition equality
supports no incremental subClass-04 count in this capture, not a permanent zero
or a formal taxonomy-completeness claim.

## Field readiness

| Field set | Observation | Readiness |
|---|---|---|
| Identity/classification | fundCode, fundType, subClass, listingDate, fundAbbr, secNameFull | Identifier-level discovery only |
| Issuer/administrator | companyName, fundManager, TRUSTEE_NAME | Identifier-level discovery only |
| Index metadata | INDEX_CODE and INDEX_NAME populated in master/equity/bond/cross-border samples; blank in all commodity samples | Conditional |
| Contact metadata | LAW_FIRM and CONTACT_MOBILE present but blank in every sample | Unusable |
| Status/time | No explicit status; queryDate empty; pageHelp.searchDate/startDate/endDate null | Fail |
| Market/execution | No price, NAV, IOPV, volume, bid/ask, depth, shares/float, fund size, market maker, fee, or holdings | Fail |
| Events/rights | No distribution/action/event history or investor/broker/settlement/tax/right fields | Fail |

## Limitations and R4 control

- PIT: No as-of/version, historical membership, effective-dated
  classification, lifecycle, or delisting status. It cannot create a
  survivorship-free formation/rebalance universe.

- Events: No dated distribution, split, merger, termination, index change,
  creation/redemption, suspension/resumption, or market-status record. It
  cannot reconcile total return.

- Rights: No investor/account eligibility, broker permission, quota,
  subscription/redemption entitlement, settlement/currency route, tax, or
  legal-access evidence. A listed identifier is not proof of access.

- Execution: No tradeable price, NAV/IOPV, spread/depth, volume, market status,
  lot, T+1/no-fill treatment, limit, commission, slippage, fill, or capacity
  evidence. It cannot demonstrate executability at any stated time or price.

Use is limited to a timestamped discovery snapshot and identifier seed for
independent follow-up research. It must not support a claim of legally or
historically complete all-current SSE ETF coverage, product selection,
allocation, holdings, orders, or return conclusions.

The next gate requires an authorized or independently archived PIT
listing-status source, dated event/corporate-action records, price/NAV and
market-status data, rights confirmation, and cost/liquidity evidence.
