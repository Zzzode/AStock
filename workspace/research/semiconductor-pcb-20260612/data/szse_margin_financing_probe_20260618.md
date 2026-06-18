# SZSE Official Margin Financing Probe Refresh

**Run date:** 2026-06-18

**Purpose:** Retry Shenzhen Stock Exchange official margin-financing routes for Shenzhen-listed report names, after the prior 2026-06-16 probe identified official endpoints but did not retrieve durable data.

**Raw archive:** `data/raw_szse_margin_probe_20260618/`

## Routes Retested

| Route | Parameters | Result | Treatment |
|---|---|---|---|
| AkShare `stock_margin_detail_szse` | `date=20260617` | `ConnectionResetError(54, connection reset by peer)` | No durable data. |
| AkShare `stock_margin_szse` | `date=20260617` | `ConnectionResetError(54, connection reset by peer)` | No durable data. |
| AkShare `stock_margin_underlying_info_szse` | `date=20260617` | `ConnectionResetError(54, connection reset by peer)` | No durable data. |
| SZSE `ShowReport/data` | `CATALOGID=1837_xxpl`, `TABKEY=tab1`, dates `2026-06-17`, `2026-06-16`, `2026-06-13` | `curl` returned HTTP code `000` with connection reset. | No durable data. |
| SZSE `ShowReport/data` | `CATALOGID=1837_xxpl`, `TABKEY=tab2`, dates `2026-06-17`, `2026-06-16`, `2026-06-13` | `curl` returned HTTP code `000` with connection reset. | No durable data. |
| SZSE `ShowReport/data` | `CATALOGID=1834_xxpl`, `TABKEY=tab1`, dates `2026-06-17`, `2026-06-16`, `2026-06-13` | `curl` returned HTTP code `000` with timeout or connection reset. | No durable data. |

## Boundary

The official SZSE endpoint remains identified, but the current environment still cannot download stable official Shenzhen margin-financing detail, summary or underlying-security data. This refresh therefore does not improve numeric Shenzhen-listed margin coverage. Existing Eastmoney public proxy remains the usable Shenzhen-listed margin-financing source, and this evidence does not close terminal-grade order flow, beneficial-owner positioning, active/passive fund labels or complete institutional ownership.
