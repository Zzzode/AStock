# Valuation Model

## Method

Because Eastmoney realtime quotes failed but Tencent quote feed refreshed all current-universe tickers again on 2026-06-18, this report uses the latest public quote anchors plus a scenario framework and local public-source forecast range rather than publishing new target prices.

Inputs:

- Tencent 2026-06-18 quote refetch / 2026-06-17 embedded timestamp snapshot for price, total market capitalization, PE and PB.
- Broker-stated net profit forecasts where directly present in downloaded PDFs or local text.
- Broker-stated target prices where directly present in local text.
- Local forecast range table in `data/forecast_range_analysis.md`.

## Broker Target and Rating Table

| Company | Broker/source | Date | Rating | Target / method | Comparability |
|---|---|---|---|---|---|
| 沪电股份 | Goldman / Sina reproduction | 2026-05-24 | Buy | CNY 142, based on 23x 2027E EPS | Comparable to A-share price, but source is article reproduction. |
| 胜宏科技 | JPM / Sina reproduction | 2026-06-09 | Overweight | HKD 600 for H-share | Not directly comparable to A-share price or CNY market cap. |
| 生益科技 | Goldman / Sina reproduction and archived snapshot | 2026-05-22 | Buy | CNY 127.4 / 146.3 referenced in snapshot | Comparable only if target basis/date verified. |
| 深南电路 | CMBI PDF; Guohai / Hibor abstract | 2026-03 / 2026-05 | Buy | CMBI TP RMB288; based on PCB 33x 2026E PE and substrate 42x 2026E PE average | Use as sourced broker target; not AStock TP. |
| 华正新材 | Zheshang PDF; Shenwan / CFI | 2026-01 / 2026-04 | Buy | Zheshang model gives 2025E-2027E revenue/NPP/EPS/PE; no 2028E | Use forecast PE only. |

## Indicative PE Anchors

| Company | Market cap used | Forecast | Indicative PE | Interpretation |
|---|---:|---:|---:|---|
| 深南电路 | CNY 269.939bn | 2026E / 2027E / 2028E NP CNY 5.546bn / 7.545bn / 9.725bn | 48.6x / 35.8x / 27.8x | Refreshed mcap raises the delivery bar; multiple falls only if forecasts hold. |
| 华正新材 | CNY 32.308bn | 2026E / 2027E NP CNY 0.573bn / 0.803bn | 56.4x / 40.2x | Refreshed mcap shows higher valuation burden; 2028E and customer split remain missing. |
| 胜宏科技 | CNY 303.208bn | 2026E / 2027E / 2028E NP range in `forecast_range_analysis.md` | 2026E range about 25.3x-33.2x; 2027E range about 15.4x-19.6x | Still attractive if high-end forecasts are met, but range is wide because GPU/ASIC ramp assumptions differ. |

## Local Forecast Range

| Company | Source count | 2026E NPP range | 2027E NPP range | Interpretation |
|---|---:|---:|---:|---|
| 沪电股份 | 2 | CNY 5.745-5.800bn | CNY 8.900-9.067bn | Tight range; strongest forecast consistency among core names. |
| 胜宏科技 | 2 | CNY 9.119-12.005bn | CNY 15.441-19.743bn | Wide range; high sensitivity to GPU/ASIC ramp assumptions. |
| 深南电路 | 2 | CNY 5.048-5.546bn | CNY 6.838-7.545bn | Moderate range; substrate ramp and depreciation matter. |
| 生益科技 | 2 | CNY 3.083-5.570bn | CNY 7.856bn single-source | Older Guohai model vs newer Pacific model shows revision risk. |
| 华正新材 | 1 | CNY 0.573bn | CNY 0.803bn | Current model coverage added, but still single-source. |

See `data/forecast_range_analysis.md` for full revenue/NPP/EPS ranges.

## Scenario Framework

| Scenario | Conditions | Segment preference |
|---|---|---|
| Bull | AI capex and Rubin/ASIC ramps stay on schedule; CCL tightness persists; high-end capacity remains qualified-scarce. | High-end PCB and CCL leaders outperform; equipment beta works. |
| Base | AI demand grows but supply response and valuation absorb part of upside. | Core names with verified delivery; avoid paying for unverified optionality. |
| Bear | Capex pause, architecture shift, or CCL price reversal. | Reduce high-beta PCB/equipment; keep only names with non-AI earnings support. |

## Target-Price Discipline

The report does not create new target prices. It uses broker targets as sourced evidence and scenario logic as AStock judgment.
