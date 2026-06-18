# Eastmoney Stock Connect Public API Probe

**Run date:** 2026-06-18

**Purpose:** Test whether additional public Eastmoney / AkShare Stock Connect endpoints can improve the remaining positioning gap beyond the already archived quarterly participant/custodian bridge.

**Raw archive:** `data/raw_eastmoney_hsgt_public_api_probe_20260618/`

## Routes Tested

| Route | Underlying report / page | Test window | Result | Interpretation |
|---|---|---|---|---|
| AkShare `stock_hsgt_individual_detail_em` | `RPT_MUTUAL_HOLD_DET` | 2026-03-01 to 2026-06-17 for sample tickers | Wrapper returned `NoneType`; direct API returned `返回数据为空` for 002463. | No usable post-rule-change single-stock daily detail recovered. |
| AkShare `stock_hsgt_institution_statistics_em` | `PRT_MUTUAL_ORG_STA` | 2026-06-01 to 2026-06-17 | Wrapper returned `NoneType`; direct API returned `返回数据为空`. | No daily institution-statistics coverage recovered. |
| AkShare `stock_hsgt_stock_statistics_em` | `RPT_MUTUAL_STOCK_HOLDRANKS` | 2026-06-17 and 2026-03-31 | Wrapper returned `NoneType`; direct API returned `返回数据为空`. | No current daily stock-statistics rows recovered. |
| AkShare `stock_hsgt_hold_stock_em` / page shell | `RPT_MUTUAL_STOCK_NORTHSTA`; `data.eastmoney.com/hsgtcg/list.html` | 2026-06-17, 2026-06-16, 2026-03-31 and 2024-08-16; intervals 1/3/5/10/M/Q/Y | Page shell archived, but page title date shows `2024-08-16`. Direct API returned `服务器繁忙` (`code=9701`) for all tested date/interval combinations. | This route does not currently improve beyond the already archived 2024-08-16 historical AkShare baseline and 2026Q1 Eastmoney quarterly bridge. |
| AkShare `stock_hsgt_hist_em` | aggregate northbound flow history | Latest rows through 2026-06-17 | Aggregate table returns rows, but buy/sell/net fields are null in the latest post-rule-change rows. | Useful as market-wide route boundary only; not single-stock positioning or order flow. |

## Key Evidence

- `raw_eastmoney_hsgtcg_list_20260618.html` archives the Eastmoney Stock Connect holding page shell; it shows `个股排行（2024-08-16）`.
- `raw_eastmoney_hsgt_public_api_probe_20260618/summary.json` records 31 direct endpoint probes.
- `RPT_MUTUAL_STOCK_NORTHSTA` returned `服务器繁忙` (`code=9701`) for every tested date/interval.
- `RPT_MUTUAL_HOLD_DET`, `PRT_MUTUAL_ORG_STA` and `RPT_MUTUAL_STOCK_HOLDRANKS` returned `返回数据为空` (`code=9201`) for the tested current windows.

## Boundary

This public API pass closes another possible public Stock Connect route, but it does not recover daily post-rule-change northbound changes, beneficial-owner positioning, active/passive institutional ownership, or terminal-grade order flow. The strongest current public evidence remains the archived Eastmoney 2026Q1 participant/custodian bridge plus public total-holding history through 2024-08-16.
