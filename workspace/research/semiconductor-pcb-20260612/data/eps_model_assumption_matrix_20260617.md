# EPS Model Assumption Matrix

**Run date:** 2026-06-17

**Purpose:** Unify public EPS model assumptions from official Q1 metrics, working-capital approximation and broker operating / forecast lines.

**Boundary:** This improves model discipline for tax, share count, cash conversion and working capital. It still does not provide named customer/platform revenue, ASP, shipments, platform margin, depreciation by project or full working-capital schedule.

## Q1 official and working-capital assumptions

| Ticker | Name | Q1 revenue | Q1 NPP | EPS | Implied shares | GM | Net margin | OCF/NPP | CCC days | Contract liability/revenue |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | 62.14亿 | 12.42亿 | 0.65 | 19.24亿 | 35.63% | 19.98% | 41.14% | 66.90 | 1.3% |
| 300476 | 胜宏科技 | 55.19亿 | 12.88亿 | 1.48 | 8.71亿 | 34.46% | 23.34% | 164.28% | 10.10 | 0.1% |
| 002916 | 深南电路 | 65.96亿 | 8.50亿 | 1.28 | 6.64亿 | 29.17% | 12.91% | 29.10% | 102.50 | 5.4% |
| 600183 | 生益科技 | 81.41亿 | 11.58亿 | 0.48 | 24.13亿 | 28.10% | 16.36% | 49.35% | 127.90 | 0.8% |
| 603186 | 华正新材 | 12.34亿 | 0.31亿 | 0.21 | 1.47亿 | 12.02% | 2.52% | 182.60% | 91.40 | 0.9% |
| 688519 | 南亚新材 | 18.32亿 | 1.50亿 | 0.66 | 2.27亿 | 15.20% | 8.19% | -44.05% | 101.10 | 0.8% |
| 002436 | 兴森科技 | 18.18亿 | 0.19亿 | 0.01 | 18.74亿 | 19.17% | -2.52% | -1318.28% | 85.20 | 2.1% |
| 301200 | 大族数控 | 19.55亿 | 3.23亿 | 0.73 | 4.42亿 | 33.12% | 16.64% | -199.94% | 174.90 | 10.5% |
| 688630 | 芯碁微装 | 5.15亿 | 1.08亿 | 0.83 | 1.31亿 | 40.94% | 21.06% | 151.82% | 257.60 | 23.0% |
| 300400 | 劲拓股份 | 1.69亿 | 0.26亿 | 0.11 | 2.33亿 | 39.66% | 15.16% | 43.89% | 118.60 | 38.1% |
| 301377 | 鼎泰高科 | 8.14亿 | 2.61亿 | 0.64 | 4.07亿 | 53.25% | 31.96% | -18.33% | 115.20 | 2.5% |
| 002938 | 鹏鼎控股 | 79.86亿 | 4.63亿 | 0.20 | 23.15亿 | 22.96% | 5.80% | 668.81% | 33.80 | 0.5% |

## Broker operating-line assumptions

| Ticker | Broker/source | Coverage | 2026E tax rate | 2026E OCF/NPP | 2026E FCF after capex | Share-count evidence |
|---|---|---|---:|---:|---:|---|
| 002463 | 中邮证券 full PDF | operating_line | 12.94% | 145.60% | 83.48亿 | 2026E: 19.398亿股, 2027E: 19.306亿股, 2028E: 19.196亿股 |
| 300476 | 开源证券 full PDF | operating_line | 11.99% | 12.29% | -16.37亿 | 2026E: 9.827亿股, 2027E: 9.829亿股, 2028E: 9.827亿股 |
| 002916 | 太平洋证券 full PDF | operating_line | 7.15% | 129.03% | N/A | 2026E: 6.813亿股, 2027E: 6.81亿股, 2028E: 6.81亿股 |
| 600183 | 太平洋证券 full PDF | operating_line | 10.78% | 110.81% | N/A | 2026E: 24.323亿股, 2027E: 24.322亿股, 2028E: 24.27亿股 |
| 603186 | 浙商证券 | forecast_line | N/A | N/A | N/A | 2025E: 1.415亿股, 2026E: 1.418亿股, 2027E: 1.421亿股 |
| 688519 | N/A | none | N/A | N/A | N/A | N/A |
| 002436 | N/A | none | N/A | N/A | N/A | N/A |
| 301200 | N/A | none | N/A | N/A | N/A | N/A |
| 688630 | N/A | none | N/A | N/A | N/A | N/A |
| 300400 | N/A | none | N/A | N/A | N/A | N/A |
| 301377 | N/A | none | N/A | N/A | N/A | N/A |
| 002938 | N/A | none | N/A | N/A | N/A | N/A |

## Interpretation

- Core operating-line names now have explicit public tax-rate and OCF/NPP assumptions from broker models where available.
- All 12 names have Q1 official margin, EPS, cash-conversion and working-capital approximation fields.
- FCF after capex normalizes broker capex to an outflow using `OCF - abs(capex)` because source models use mixed sign conventions.
- This fills the public model-base layer, but it remains insufficient for a true customer/platform bottom-up EPS model because named platform revenue, ASP, shipment, project depreciation and customer-specific working capital are not disclosed.
