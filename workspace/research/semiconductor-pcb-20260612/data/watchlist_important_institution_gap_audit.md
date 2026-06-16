# Watchlist Important-Institution Gap Audit

**Purpose:** Audit whether the six original watchlist tickers can be upgraded from `important_institution=False` using archived Eastmoney important-institution evidence.

## Conclusion

Keep `important_institution=False` for all six original watchlist tickers:

| Ticker | Name | Decision | Reason |
|---|---|---|---|
| 688519 | 南亚新材 | Keep False | No single-stock important-institution row in `stock_holdings` or `RPT_STOCK_DETAILS_CHANGE`; one basket-level social-security row mentions `688519` but cannot be allocated to the stock. |
| 002436 | 兴森科技 | Keep False | No visible single-stock important-institution row returned by archived Eastmoney important-institution data. |
| 301200 | 大族数控 | Keep False | No visible single-stock important-institution row returned by archived Eastmoney important-institution data. |
| 688630 | 芯碁微装 | Keep False | No visible single-stock important-institution row returned by archived Eastmoney important-institution data. |
| 300400 | 劲拓股份 | Keep False | No visible single-stock important-institution row returned by archived Eastmoney important-institution data. |
| 301377 | 鼎泰高科 | Keep False | No visible single-stock important-institution row returned by archived Eastmoney important-institution data. |

## Evidence Inspected

| Evidence file | Finding |
|---|---|
| `data/important_institution_holding_evidence.json` | `stock_holdings` contains only three single-stock rows: `002916`, `002463`, `600183`. |
| `data/important_institution_holding_evidence.md` | Published summary covers only `002916`, `002463`, `600183`. |
| `data/important_institution_detail_evidence.json` | Top-level keys are `002463`, `300476`, `002916`, `600183`, `603186`; no original watchlist tickers. |
| `data/important_institution_category_history_bridge.md` | Historical category coverage includes core names and `603186`, not the six original watchlist names. |

## Basket-Level False Positive

The Eastmoney `org_statistics` table contains a row for `全国社保基金六零一组合` where:

```text
SECURITY_CODE = 688516,301216,688519
SECURITY_NAME_ABBR = 奥特维,万凯新材,南亚新材
TOTAL_SHARES = 121,546,308
HOLD_MARKET_CAP = 4,079,868,026.71
TOTAL_SHARES_RATIO = 10.36720962
HOLD_COUNT = 11
```

This is a holder-level basket/statistics row, not a single-stock holding row. The shares, market cap and ratio are not attributable to `688519` alone. Therefore it is not used to mark Nanya as important-institution covered.

## Matrix Treatment

- `important_institution` remains `False` for `688519`, `002436`, `301200`, `688630`, `300400`, and `301377`.
- `fund_holder`, `circulating_holder`, and `fund_flow` remain separate public proxy fields and must not be used to backfill `important_institution`.

## Boundary

This audit does not prove that no important institution holds these stocks. It proves only that the tested public Eastmoney important-institution endpoints did not return attributable single-stock rows for them in the archived evidence set. Full institutional ownership still requires a paid database or issuer / fund disclosure beyond the current public corpus.
