# C9 Actual-Contract Source Route and Dated Selection Snapshot

- Status: **source route observed; not replay-ready**; `portfolio_q=0`.
- Source: six retrospectively captured first-party SHFE daily files, bound in `sources/c9-official-shfe-commodity-contracts-20260815/manifest.json`.
- Boundary: this is neither a continuous series nor a backtest, order, position, allocation or return result.

## Actual-contract route samples

| Trade date | Total rows | CU actual rows | AU actual rows | RU actual rows | Essential EOD fields observed | Turnover field observed |
|---|---:|---:|---:|---:|---|---|
| 2016-01-04 | 176 | 12 | 8 | 10 | yes | no |
| 2018-01-02 | 176 | 12 | 8 | 10 | yes | no |
| 2020-01-02 | 236 | 12 | 8 | 10 | yes | no |
| 2022-01-04 | 266 | 12 | 8 | 10 | yes | yes |
| 2024-01-02 | 304 | 12 | 8 | 10 | yes | yes |
| 2026-08-14 | 333 | 12 | 8 | 10 | yes | yes |

Every sample contains prior settlement, OHLC, settlement, volume, open interest and delivery month. Turnover appears in the later schema but not the 2016--2020 samples, which is a source-schema limitation rather than an inferred zero. The files were retrieved retrospectively and do not establish point-in-time availability, a complete contract lifecycle, effective risk parameters, costs, fills, account access or P&L.

## 2026-08-14 dated selection illustration

Fixed illustration rule: select only an actual contract with a positive settlement, volume and open interest, a scheduled expiry 90--270 calendar days away, then rank by official EOD open interest, volume and earliest delivery month. The source page permits holiday adjustments to the 15th-day last-trade date; the selected dates below are weekday dates and must still be exchange-calendar checked before any live application.

| Family | Selected actual contract | Settlement | Volume | Open interest | Scheduled last trade | Days |
|---|---|---:|---:|---:|---|---:|
| CU | CU2612 | 107090.0 | 5180 | 60362 | 2026-12-15 | 123 |
| AU | AU2612 | 947.22 | 42872 | 98284 | 2026-12-15 | 123 |
| RU | RU2701 | 17740.0 | 155968 | 110329 | 2027-01-15 | 154 |

No 65-session signal history, personal access, broker margin, quote, fill or trade is asserted. The selection is a reproducible observation only.
