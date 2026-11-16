# Verified Market Data — 2026-08-12

**Result:** `10 / 10` named products reconcile to their locally archived SSE snapshots. Identity, date, time, last price, volume, amount and OHLC fields were checked without transformation.

**Result for implementation:** `NOT_APPROVED; q=0`. The verification is deliberately narrow. It does not establish bid–ask spread, quote depth, IOPV/same-session NAV, 20-session capacity, creation/redemption state, broker commission, tax, settlement or account eligibility. Price/NAV comparisons in the valuation packet are therefore historical, date-mismatched diagnostics only.

See [verified_market_data_20260812.json](verified_market_data_20260812.json) and the raw packet for the full control record.
