# C7 Static ETF Price-Observation Manifest

- Batch: `c7-static-etf-price-observation-20260815`
- Capture time: `2026-08-14T17:59:56.934228+00:00`
- Method: read-only anonymous HTTPS requests to SSE's public daily-price endpoint; no credentials, account access, data purchase, bypass or trading action.
- Protocol status: `exploratory_post_observation_not_clean_preregistration`.
- Boundary: these are retrospectively retrieved official market-price bars. They do **not** prove historic availability, adjustment basis, total return, distributions, events, NAV/IOPV, current product state, data entitlement, costs, tradability, settlement, broker route, account permission or fills.

| Code | Rows / reported total | First date | Last date | SHA-256 |
|---|---:|---|---|---|
| 510300 | 3456 / 3456 | 20120528 | 20260814 | `9838250fb4fdaab55d8a0b6102ad8c9cf3d42c77ed1323b413b53ff8e2527a3b` |
| 510500 | 3259 / 3259 | 20130315 | 20260814 | `562936692f7f6ce6e140c900fac9600e867f6d68d4ffbc2adea590641683a8d5` |
| 510880 | 4757 / 4757 | 20070118 | 20260814 | `63e71acfc5cf6d87e4f5ad5792d521c238927ff58e967767e32408924bae0859` |
| 511010 | 3255 / 3255 | 20130325 | 20260814 | `a739e95a8cf5a526db283fa44173e672c05be429514e7a06d1e5923d799bbd81` |
| 511990 | 3290 / 3290 | 20130128 | 20260814 | `23a6e129d8f8449aaf778906ba35271a1d7edcb92c37995b03d219fd951d4a05` |
| 518880 | 3173 / 3173 | 20130729 | 20260814 | `05be8fb74d456c0975ac72804fa314db92273b568bee932bebf5670393733633` |

The request uses `begin=0&end=5000`; the returned response reports that every
retained code's full available response fits within that range. This proves
only response completeness as declared by the endpoint at capture, not a
complete historical investor-return or execution ledger.
