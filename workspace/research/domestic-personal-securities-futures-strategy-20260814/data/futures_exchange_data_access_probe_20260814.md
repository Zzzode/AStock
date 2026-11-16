# Futures Actual-Contract EOD Data-Access Probe

- Status: **actual-contract paths observed; not replay ready**; `q=0`.
- Method: direct official daily-file requests, with six date samples from 2016--2026.
- Historical provenance: every source sample was retrieved retrospectively at 2026-08-14T14:41:26+08:00; direct paths were revalidated at 2026-08-14T07:07:34.823238+00:00. This is source-access evidence, not original-date point-in-time availability.
- Scope: source-access verification only; it is not a P&L test.

## SHFE samples

| Date | All contract rows | AU/CU/RB rows | Varieties |
|---|---:|---:|---|
| 2016-01-04 | 176 | 32 | AU, CU, RB |
| 2018-01-02 | 176 | 32 | AU, CU, RB |
| 2020-01-02 | 236 | 32 | AU, CU, RB |
| 2022-01-04 | 266 | 32 | AU, CU, RB |
| 2024-01-02 | 304 | 32 | AU, CU, RB |
| 2026-08-13 | 333 | 32 | AU, CU, RB |

## CZCE samples

| Date | TA/CF/MA rows | Varieties |
|---|---:|---|
| 2016-01-04 | 30 | CF, MA, TA |
| 2018-01-02 | 30 | CF, MA, TA |
| 2020-01-02 | 30 | CF, MA, TA |
| 2022-01-04 | 30 | CF, MA, TA |
| 2024-01-02 | 30 | CF, MA, TA |
| 2026-08-13 | 30 | CF, MA, TA |

All twelve raw samples are archived under `sources/probe-exchange-data-r0-20260814/` and are hash-bound in its manifest. The query output confirms actual listed-contract rows and EOD price/settlement/liquidity fields, not a continuous series. It does not establish a complete frozen archive, contract lifecycle, price-limit state, historical margin, broker cost, bid/ask, fill, delivery eligibility or a strategy result.
