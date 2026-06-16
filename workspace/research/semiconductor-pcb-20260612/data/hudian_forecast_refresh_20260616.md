# Hudian Forecast Refresh Evidence

**Run date:** 2026-06-16

**Purpose:** Record the forecast-line impact from two newly archived Hudian original PDFs and explain why the public-source forecast range widened after adding them.

## Source Documents

| Source | Local file | Date | Pages | Rating | Boundary |
|---|---|---|---:|---|---|
| 信达证券 | `workspace/reports/semiconductor-pcb-original-pdf-refresh-20260616/07-xinda-hudian-2025h1-ai-server-switch-20250822.pdf` | 2025-08-22 | 5 | 买入 | Domestic broker update; not Goldman original PDF. |
| 天风证券 | `workspace/reports/semiconductor-pcb-original-pdf-refresh-20260616/08-tianfeng-hudian-quarterly-growth-20260308.pdf` | 2026-03-08 | 4 | 增持 | Domestic broker update based on preliminary 2025 results; not Goldman original PDF. |

## Extracted Forecast Lines

| Source | Revenue 2025E | Revenue 2026E | Revenue 2027E | NPP 2025E | NPP 2026E | NPP 2027E | EPS 2025E | EPS 2026E | EPS 2027E |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 信达证券 | 178.79亿元 | 242.74亿元 | 282.72亿元 | 40.09亿元 | 55.66亿元 | 75.35亿元 | 2.08 | 2.89 | 3.92 |
| 天风证券 | 189.44亿元 | 255.15亿元 | 323.68亿元 | 38.22亿元 | 51.98亿元 | 67.78亿元 | 1.99 | 2.70 | 3.52 |

## Business Assumptions Added

| Source | Incremental operating evidence | EPS relevance |
|---|---|---|
| 信达证券 | 2025H1 revenue 84.94亿元, parent NPP 16.83亿元, PCB revenue 81.52亿元, PCB GM 36.47%; enterprise communications board revenue 65.32亿元; AI server/HPC PCB products +25.34% YoY and 23.13% of enterprise communications board revenue; high-speed switch/router PCB products +161.46% YoY and 53.00% of enterprise communications board revenue; Thailand base entered small-batch production and had two formal customer recognitions plus four ongoing certifications/imports. | Adds segment-mix and ramp evidence behind the 2025E-2027E forecast line. |
| 天风证券 | 2025 preliminary revenue 189.45亿元, parent NPP 38.22亿元; Q4 revenue 54.33亿元 and parent NPP 11.04亿元; 2026 high-end PCB project investment about 33亿元, planned annual incremental capacity 14万平方米 and annual incremental revenue 30.5亿元 after completion. | Adds preliminary result and capacity-expansion basis for a lower 2026E/2027E forecast line. |

## Forecast Range Impact

After adding Xinda and Tianfeng to the earlier Zhongyou / Zhongtai model set, Hudian's public-source forecast range becomes:

| Metric | 2026E low | 2026E high | 2027E low | 2027E high | 2028E low | 2028E high |
|---|---:|---:|---:|---:|---:|---:|
| Revenue | 242.74亿元 | 267.00亿元 | 255.15亿元 | 388.24亿元 | 527.00亿元 | 545.09亿元 |
| NPP | 51.98亿元 | 58.00亿元 | 67.78亿元 | 90.67亿元 | 129.00亿元 | 130.91亿元 |
| EPS | 2.70 | 2.99 | 3.52 | 4.71 | 6.72 | 6.80 |

## Interpretation

- The earlier two-source Hudian range appeared tight, but the added Xinda/Tianfeng model lines widen the low-end 2026E/2027E forecast materially.
- This improves forecast-risk disclosure and reduces overconfidence in a single high-growth earnings path.
- The model still does not provide customer/platform revenue, ASP, shipment, platform gross margin, depreciation schedule or working-capital assumptions.

## Report Treatment

- Use these lines in `data/forecast_range_analysis.md` and Exhibit 20b.
- Do not average them into an AStock target price.
- Do not treat them as Goldman original evidence or as customer/platform bottom-up EPS.
