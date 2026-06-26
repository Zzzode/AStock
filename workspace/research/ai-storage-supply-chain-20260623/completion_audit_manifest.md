# Completion Audit Manifest - Full Valuation - 20260626

- **Decision**: `full_valuation_update`
- **Gate**: `FULL_VALUATION_PASS`
- **Report date**: 2026-06-26
- **Data cutoff**: 2026-06-26 close; source refresh 2026-06-26
- **Reader-facing action**: `组合低配；覆盖标的中性/减持`
- **Target-price status**: published current model target prices, ranges, upside/downside, and ratings

## Valuation Summary

| Item | Result |
|---|---:|
| Weighted base upside | -17.0% |
| Covered tickers | 11 |
| Target-price rows | 11 |
| Watchlist-only rows | 0 |
| Source registry records | 40 |
| Source captures / probes | 23 |
| Captured files | 18 |
| HTTP-error probe files | 4 |
| Failed probes | 1 |

## Verifier Result

- `tools/verify_ai_storage.py`: PASS=126 / FAIL=0 / ADVISORY=2.

## Governance Notes

- The valuation-reset manifest is superseded for publication use.
- Current source of truth is `data/current_valuation_model_20260626.json`.
- Source admission rule: no target-price uplift enters the model unless the source has URL/archive, timestamp/hash or stable identity, and explicit claim-audit boundary.
- The current PDF is an internal full-valuation research report with target prices and ratings, not a trading instruction.
