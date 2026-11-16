# R1 Continuation Research — Static-Vector Falsification and T1 Queue

## Decision status

The work has progressed beyond a generic framework, but it has not produced a
usable allocation. The R1 public-price test falsifies a simple static
four-ETF vector as evidence for the conditional 5% five-year total-return
objective. The result is intentionally a negative research result: a full
sample annualized price result does not offset the existence of incomplete
five-year windows below the threshold, and the input is not a total-return or
execution-grade data set.

Current portfolio action remains **none**. T2, T3 and T4 are empty and every
candidate remains `q=0`.

## What was tested

`data/public_price_screening_replay_20260814.{json,md}` binds a public,
unadjusted market-price observation archive for `510300`, `510880`, `511010`
and `518880` to a simple 25% each, quarterly marked vector. It reports the
price-only result, not a fund-NAV, total-return, net-of-cost or fill result.

The failure criterion is deliberately conservative: every complete rolling
five-year price window would need to reach 5% before even the weaker price
proxy could be considered supportive. It did not. This rules out promoting the
static vector; it does not identify a replacement, forecast a future outcome
or create a portfolio instruction.

## Official-index cross-check

To avoid treating one ETF mix as the whole opportunity set, a second,
predeclared public discovery screen used the official CSI history endpoint for
two equity total-return indices and four already-published equity--bond index
rules. The protocol was frozen before retrieval in
`data/official_index_discovery_protocol_20260814.{json,md}`; raw responses are
hash-bound under `sources/probe-csi-index-20260814/`.

This more favourable but still weak screen gives the same decision: **none of
the six published index-value paths clears every observed rolling five-year
window.** The 30/70 published constant-proportion index is closest (967 of 999
windows at or above 5%), but still has 32 misses and a 4.43% minimum. The
CSI Dividend Total Return Index has 46 misses (3.57% minimum); CSI 300 Total
Return has 960 misses (-2.29% minimum). The risk-parity and 10/90--20/80
constant-proportion references also miss the threshold. See
`data/official_index_discovery_20260814.{json,md}` for every aggregate result.

The result is not a product backtest: there are no ETF tracking deviations,
costs, taxes, account access, market-status or execution assumptions. It
therefore rejects these published rules as evidence for the stronger objective
but does not rule out later dynamic, point-in-time research under OU-TR5.

## Open-universe consequence

The correct response is not to optimize weights after observing this result.
It is to keep the research universe open and to use a finite, source-backed
T1 queue only for structured diligence. `data/t1_research_queue_20260814.{json,md}`
contains eleven deliberately diverse nominees across direct equities, equity
ETFs, direct sovereign/treasury/cash structures and public REITs. R0 primary
packets are now captured in three separate immutable archives and summarised
in `data/direct_equity_r0_fact_pack_20260814.{json,md}`,
`data/fund_sovereign_r0_fact_pack_20260814.{json,md}` and
`data/reit_r0_fact_pack_20260814.{json,md}`. A name on the queue has no
approved weight, no live recommendation and no execution permission.

The direct-equity workstream is material rather than decorative: the first
three research nominees are `000333.SZ`, `600900.SH` and `600036.SH`, chosen
for distinct manufacturing/overseas, hydrology/power and bank credit/capital
research models. A later
strategy cannot claim an open universe while treating every issuer as an ETF
look-through. Each direct stock requires filing reconciliation, an earnings
bridge, three-scenario current-price valuation, governance/industry/risk work,
liquidity review, catalysts and invalidation conditions before a T2 comparison.

The extension adds two useful exclusions from false evidence, not any asset
allocation. First, the direct sovereign `260008` was issued in April 2026 and
therefore cannot have a realised five-year history at this cutoff. Second, the
three current REIT research nominees listed in 2022--24 and likewise cannot
support a realised rolling-five-year test. Their fund NAV, distributable cash,
reported cash-flow distribution rates and project operating performance remain
important R0 facts, but none is a substitute for listed-holder market-price
total return.

## Next falsifiable rulebook

The next model must be frozen before its outcome is viewed. The proposed
research rulebook identifier is `OU-TR5-v1`, with no accepted performance
result yet. It must specify:

1. T0 eligibility, T2 construction, availability timestamp and every
   selection/substitution exclusion.
2. Weight, rebalancing, drift, cash-residual, order-delay and no-fill rules.
3. Raw-price plus event-ledger total-return treatment; each distribution,
   tax and fee is recorded once.
4. Dated, instrument-specific cost, tax, settlement, spread, participation
   and market-status rules.
5. B0 protected-liquidity and B1 passive-blend comparators using the same
   calendar and accounting convention.
6. A development/holdout separation and a prospective paper-validation phase.

If a proposed T2 rule or any complete predeclared five-year cohort fails the
5% research objective, the failure is recorded; it is not repaired by a
retrospective universe change, a distribution assumption, or a forced market
allocation.

## Post-rulebook continuation state

The follow-on dynamic documents now make the research path explicit without
pretending that it has passed an implementation test.

- `analysis/dynamic_rulebook_design_20260814.md` and
  `analysis/dynamic_exposure_mapping_design_20260814.md` define three
  **draft-not-frozen** test hypotheses and their test-only unitized mapping.
  They state membership, concentration, residual/no-fill and receipt-state
  treatment, but require a future independent freeze before any result is
  viewed. They do not name a current holding or authorize an action.
- `analysis/data_source_feasibility_r1_20260814.md` turns the data limitation
  into a field-level hard gate. A formal cohort would need authorized PIT price,
  event, eligibility, protected-liquidity and common-risk/look-through records;
  no entitlement or complete archive exists today.
- Evidence-limited R1 issuer/product diligence now covers all eleven T1
  nominees in the direct-equity, fund/sovereign and public-REIT group memos.
  The work identifies exact operating, governance, valuation and market-access
  gates, but no name has passed R1, entered T2 or acquired an approved weight.

## Hard blockers

- Public daily price data do not establish total return, point-in-time
  membership, halts, limits, corporate actions, delistings, capacity or fills.
- A strategy result must separate unitized proportional-cost research from
  account-specific lot, minimum-fee, tax and market-depth assessment.
- China-market settlement and turnover rules are product-specific; a generic
  ETF or T+1 assumption is not sufficient.
- Public REIT cash-flow distributions, a fund coupon or a money-market label
  do not create a separate objective or prove liquidity, total return or
  accessibility.
- The current 100-share-lot portfolio engine is not a valid substitute for a
  scale-neutral total-return test. The formal path needs a unitized engine plus
  ETF, REIT, bond and non-standard event coverage; see
  `data/replay_feasibility_and_gap_assessment_20260814.{json,md}`.

The required next outcome is a documented, falsifiable T2 research protocol
and evidence pack—not an unsupported allocation table.
