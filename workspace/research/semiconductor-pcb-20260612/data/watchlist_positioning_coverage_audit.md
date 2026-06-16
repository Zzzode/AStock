# Watchlist Positioning Coverage Audit

**Purpose:** Reconcile `ticker_evidence_coverage_matrix.md` with the actual public positioning and flow evidence already archived for the six original watchlist tickers. The goal is to avoid leaving stale false negatives in the coverage matrix while preserving the boundary that public proxies are not terminal-grade positioning.

## Watchlist Coverage Snapshot

| Ticker | Fund holders | Circulating holders | Daily fund-flow proxy | Margin financing | Block trade | Dragon-Tiger List | Lock-up expiry | Important institution visible rows | Matrix treatment |
|---|---|---|---|---|---|---|---|---|---|
| 688519 | Yes | Yes | Yes, 30 rows | Yes, 300 rows | Yes | Yes | Yes | No current visible row | `fund_flow=True`; `important_institution=False` |
| 002436 | Yes | Yes | Yes, 30 rows | Yes, 300 rows | Yes | Yes | Yes | No current visible row | `fund_flow=True`; `important_institution=False` |
| 301200 | Yes | Yes | Yes, 30 rows | Yes, 300 rows | Yes | Yes | Yes | No current visible row | `fund_flow=True`; `important_institution=False` |
| 688630 | Yes | Yes | Yes, 30 rows | Yes, 300 rows | Yes | Yes | Yes | No current visible row | `fund_flow=True`; `important_institution=False` |
| 300400 | Yes | Yes | Yes, 30 rows | Empty / unavailable | Empty / unavailable | Yes | Yes | No current visible row | `fund_flow=True`; `important_institution=False` |
| 301377 | Yes | Yes | Yes, 30 rows | Yes, 300 rows | Yes | Yes | Yes | No current visible row | `fund_flow=True`; `important_institution=False` |

## Evidence Files

- `data/watchlist_holder_evidence.md`: Sina fund holders and circulating holders cover 6/6 watchlist tickers.
- `data/eastmoney_fund_flow_evidence.md`: Eastmoney daily fund-flow proxy covers 6/6 watchlist tickers with 30 rows each through 2026-06-15.
- `data/eastmoney_margin_financing_evidence.md`: margin-financing evidence covers 5/6 original watchlist tickers; Jintuo (`300400`) returned empty rows.
- `data/eastmoney_block_trade_evidence.md`: block-trade evidence covers 5/6 original watchlist tickers; Jintuo (`300400`) returned empty rows.
- `data/eastmoney_lhb_evidence.md`: Dragon-Tiger List abnormal-trading proxy covers 6/6 original watchlist tickers.
- `data/eastmoney_lockup_expiry_evidence.md`: lock-up expiry / future supply-pressure proxy covers 6/6 original watchlist tickers.
- `data/important_institution_category_history_bridge.md`: public important-institution detail rows cover core names and Huazheng history, but not the six original watchlist tickers in the visible 2026Q1 snapshot.

## Matrix Decision

- Set `fund_flow=True` for all six original watchlist tickers because public daily fund-flow proxy exists for all six, with additional abnormal-trading and lock-up evidence.
- Keep `important_institution=False` for all six original watchlist tickers because visible important-institution category rows were not returned by the public endpoint.
- Do not reinterpret fund-holder rows or HKCC/circulating-holder rows as "important institution" coverage. They are separate public holder proxies.

## Boundary

This audit improves public-source positioning coverage, but it does not close the strict unresolved requirement for terminal-grade positioning and order flow. The remaining missing data still includes real-time order flow, official active/passive classification, complete institutional holdings, daily post-rule-change northbound changes and beneficial-owner northbound positioning.
