# Watchlist EPS Sensitivity Bridge

**Purpose:** Convert watchlist broker forecast-line evidence into a transparent sensitivity bridge. This improves the EPS-sensitivity layer for watchlist names, while preserving the boundary that this is not a customer/platform bottom-up EPS model.

**Source:** `data/watchlist_eps_model.md`, based on downloaded broker PDFs in `workspace/research/semiconductor-pcb-20260612/sources/broker-watchlist-20260615/`.

## 2026E NPP / EPS Stress

| Ticker | Source quality | 2026E NPP | NPP +10% | NPP -10% | 2026E EPS | EPS +10% | EPS -10% | Treatment |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 688519 | Broker forecast line with revenue / NPP / EPS | 4.90亿 | 5.39亿 | 4.41亿 | 2.09 | 2.30 | 1.88 | NPP and EPS sensitivity available. |
| 301200 | Broker forecast line with NPP / EPS | 15.36亿 | 16.90亿 | 13.82亿 | 3.18 | 3.50 | 2.86 | NPP and EPS sensitivity available; no revenue line. |
| 688630 | Broker forecast line with revenue / NPP / EPS | 5.09亿 | 5.60亿 | 4.58亿 | 3.86 | 4.25 | 3.47 | NPP and EPS sensitivity available. |
| 300400 | Broker forecast line with revenue / NPP / EPS | 2.61亿 | 2.87亿 | 2.35亿 | 1.07 | 1.18 | 0.96 | NPP and EPS sensitivity available. |
| 301377 | Broker forecast line with NPP / EPS | 9.04亿 | 9.94亿 | 8.14亿 | 2.20 | 2.42 | 1.98 | NPP and EPS sensitivity available; no revenue line. |
| 002436 | Forecast line with NPP / EPS after Huaxin-Kaiyuan refresh | 4.38亿 | 4.82亿 | 3.94亿 | 0.26 | 0.29 | 0.23 | NPP and EPS sensitivity now available; FCBGA ramp remains key risk. |

## 2027E / 2028E EPS Continuity

| Ticker | 2027E EPS | 2027E EPS +10% | 2027E EPS -10% | 2028E EPS | 2028E EPS +10% | 2028E EPS -10% | Read-through |
|---|---:|---:|---:|---:|---:|---:|---|
| 688519 | 3.45 | 3.80 | 3.11 | 5.57 | 6.13 | 5.01 | High forecast growth; sensitive to CCL cycle and high-speed material adoption. |
| 301200 | 5.16 | 5.68 | 4.64 | 6.50 | 7.15 | 5.85 | Drilling-equipment demand must sustain after AI PCB capex expansion. |
| 688630 | 5.36 | 5.90 | 4.82 | 7.43 | 8.17 | 6.69 | Equipment order and advanced-packaging penetration are key variables. |
| 300400 | 1.32 | 1.45 | 1.19 | N/A | N/A | N/A | 2028E missing; remains a shorter-horizon PCBA equipment proxy. |
| 301377 | 4.19 | 4.61 | 3.77 | 6.75 | 7.43 | 6.08 | High growth assumes drilling consumable demand and high-end mix continue. |
| 002436 | 0.44 | 0.48 | 0.40 | 0.76 | 0.84 | 0.68 | Upgraded Huaxin path; FCBGA ramp losses and substrate utilization remain the main risk. |

## Interpretation

- This bridge upgrades the watchlist EPS layer from a static forecast table to an explicit stress-test table.
- NPP and EPS sensitivity coverage is now available for all six original watchlist names.
- 002436 was upgraded from EPS-only to NPP/EPS coverage after adding Huaxin and Kaiyuan original PDFs plus Tonghuashun/Eastmoney consensus cross-checks.
- This is still not a full operating-line model. It lacks customer/platform revenue, ASP, shipments, segment margins, depreciation schedules, tax and working-capital assumptions.

## Boundary

Do not treat this table as a target-price model or a full bottom-up customer/platform EPS bridge. It is a forecast-line stress test derived from public broker report text.
