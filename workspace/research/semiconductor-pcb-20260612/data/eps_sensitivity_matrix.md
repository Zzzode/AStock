# EPS Sensitivity Matrix

**Source:** `editable_eps_model.json` operating lines and forecast lines.

**Method:** For companies with operating-line models, gross-margin, revenue and opex shocks are converted using base `NPP / operating profit`. For Huazheng, only a forecast-line revenue-shock proxy is shown because a full operating-line model is unavailable.

**Boundary:** This is a public-source annual sensitivity matrix, not a customer/platform bottom-up EPS bridge. It does not include named customer revenue, ASP, shipment, platform gross margin, depreciation schedules or working-capital detail.

## 2026E Sensitivity Summary

| Ticker | Source | Base NPP | GM -1pct | GM -2pct | Revenue -5pct | Opex +2pct revenue | Combined: revenue -5pct + GM -1pct |
|---|---|---:|---:|---:|---:|---:|---:|
| 002463 | 中邮证券 full PDF | 57.52亿 | 55.18亿 | 52.84亿 | 53.30亿 | 52.84亿 | 50.95亿 |
| 300476 | 开源证券 full PDF | 91.19亿 | 88.30亿 | 85.42亿 | 85.55亿 | 85.42亿 | 82.66亿 |
| 002916 | 太平洋证券 full PDF | 55.46亿 | 52.53亿 | 49.60亿 | 50.83亿 | 49.60亿 | 47.90亿 |
| 600183 | 太平洋证券 full PDF | 55.70亿 | 52.53亿 | 49.36亿 | 51.18亿 | 49.36亿 | 48.01亿 |
| 603186 | 浙商证券 forecast-line only | 5.73亿 | N/A | N/A | 5.44亿 | N/A | N/A |
| 002938 | 华泰证券 operating-line proxy | 57.22亿 | 52.95亿 | 48.67亿 | 52.15亿 | N/A | 47.88亿 |

## Full Matrix

| Ticker | Year | Revenue | Base NPP | GM | Net margin | GM -2pct NPP | Revenue -5pct NPP | Combined downside NPP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 002463 | 2026E | 266.67亿 | 57.52亿 | 36.10% | 21.60% | 52.84亿 | 53.30亿 | 50.95亿 |
| 002463 | 2027E | 377.97亿 | 88.79亿 | 37.40% | 23.50% | 82.18亿 | 82.61亿 | 79.30亿 |
| 002463 | 2028E | 526.60亿 | 129.29亿 | 38.30% | 24.60% | 120.09亿 | 120.48亿 | 115.88亿 |
| 300476 | 2026E | 328.16亿 | 91.19亿 | 39.10% | 27.80% | 85.42亿 | 85.55亿 | 82.66亿 |
| 300476 | 2027E | 549.70亿 | 154.41亿 | 38.50% | 28.10% | 144.74亿 | 145.10亿 | 140.27亿 |
| 300476 | 2028E | 769.30亿 | 222.88亿 | 39.30% | 29.00% | 209.34亿 | 209.58亿 | 202.81亿 |
| 002916 | 2026E | 315.98亿 | 55.46亿 | 31.65% | 17.55% | 49.60亿 | 50.83亿 | 47.90亿 |
| 002916 | 2027E | 402.90亿 | 75.45亿 | 32.62% | 18.73% | 68.05亿 | 69.41亿 | 65.71亿 |
| 002916 | 2028E | 501.46亿 | 97.25亿 | 33.13% | 19.39% | 88.03亿 | 89.61亿 | 85.00亿 |
| 600183 | 2026E | 391.48亿 | 55.70亿 | 28.49% | 14.23% | 49.36亿 | 51.18亿 | 48.01亿 |
| 600183 | 2027E | 514.85亿 | 78.56亿 | 30.16% | 15.26% | 70.36亿 | 72.38亿 | 68.27亿 |
| 600183 | 2028E | 629.84亿 | 101.69亿 | 31.06% | 16.15% | 91.69亿 | 93.92亿 | 88.92亿 |
| 603186 | 2026E | 73.43亿 | 5.73亿 | N/A | 7.80% | N/A | 5.44亿 | N/A |
| 603186 | 2027E | 95.53亿 | 8.03亿 | N/A | 8.41% | N/A | 7.63亿 | N/A |
| 002938 | 2026E | 471.91亿 | 57.22亿 | 23.71% | 12.13% | 48.67亿 | 52.15亿 | 47.88亿 |

## Interpretation

- 002463 and 002916 have relatively interpretable operating-line sensitivities because revenue, gross margin, operating profit and NPP are available across 2026E-2028E.
- 300476 has high base net margin and high sensitivity to revenue/gross-margin assumptions, consistent with the wider forecast range from different brokers.
- 600183 is highly sensitive to gross-margin assumptions because the CCL thesis is primarily a material-price/mix thesis.
- 603186 remains forecast-line only, although 2028E is now covered by the Zheshang annual-review PDF; the sensitivity is therefore still weaker than for the operating-line names.
- 002938 is upgraded to an operating-line proxy using Huatai's public forecast table, but it still lacks customer/platform bottom-up inputs.
- A top-tier customer/platform bottom-up model is not available from public sources without platform/customer revenue, ASP, shipment, segment margins, depreciation, tax and working-capital assumptions.
