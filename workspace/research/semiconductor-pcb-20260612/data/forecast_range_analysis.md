# Forecast Range Analysis

**Purpose:** Convert downloaded broker PDF model lines into a multi-source forecast range. This improves the report from single-point broker forecasts toward top-tier consensus discipline, while still avoiding a fake full Street Consensus label.

**Boundary:** This is a local public-source forecast range, not Wind/Choice consensus. It only includes forecasts that were directly extracted from downloaded PDFs or locally archived text.

## Coverage

| Ticker | Sources used | Forecast range quality | Main limitation |
|---|---|---|---|
| 002463 | 中邮证券, 中泰证券, 信达证券, 天风证券 | Four-source 2026E-2027E revenue/NPP/EPS range; 2028E two-source range | Customer/platform revenue split still missing; newer 2026 preliminary-result model lines pull the low end lower. |
| 300476 | 开源证券, 国盛证券 | Two-source 2026E-2027E range; 2028E single-source | Issuer-confirmed named-customer revenue still missing. |
| 002916 | 太平洋, CMBI | Two-source NPP/EPS range for 2026E-2028E; revenue range partly single-source | Substrate/customer ramp assumptions not fully disclosed. |
| 600183 | 太平洋, 国海证券 | 2026E range shows large model-date dispersion; 2027E-2028E single-source | M8/M9/M10 revenue share and pricing not disclosed. |
| 603186 | 浙商证券深度, 浙商年报点评 | Two-source 2026E-2027E forecast-line range; 2028E now covered by annual-review model | Full customer/platform split and full operating-line source audit still missing. |

## Forecast Range Table

| Ticker | Metric | 2026E low | 2026E high | 2027E low | 2027E high | 2028E low | 2028E high |
|---|---|---:|---:|---:|---:|---:|---:|
| 002463 | Revenue (亿元) | 242.74 | 267.00 | 255.15 | 388.24 | 527.00 | 545.09 |
| 002463 | NPP (亿元) | 51.98 | 58.00 | 67.78 | 90.67 | 129.00 | 130.91 |
| 002463 | EPS (元) | 2.70 | 2.99 | 3.52 | 4.71 | 6.72 | 6.80 |
| 300476 | Revenue (亿元) | 328.16 | 370.29 | 549.70 | 598.77 | 769.30 | 769.30 |
| 300476 | NPP (亿元) | 91.19 | 120.05 | 154.41 | 197.43 | 222.88 | 222.88 |
| 300476 | EPS (元) | 9.28 | 13.79 | 15.71 | 22.68 | 22.68 | 22.68 |
| 002916 | Revenue (亿元) | 306.93 | 315.98 | 378.26 | 378.26 | 464.49 | 464.49 |
| 002916 | NPP (亿元) | 50.48 | 55.46 | 68.38 | 75.45 | 86.87 | 97.25 |
| 002916 | EPS (元) | 7.57 | 8.14 | 10.26 | 11.08 | 13.03 | 14.28 |
| 600183 | Revenue (亿元) | 276.82 | 391.48 | 514.85 | 514.85 | 629.84 | 629.84 |
| 600183 | NPP (亿元) | 30.83 | 55.70 | 78.56 | 78.56 | 101.69 | 101.69 |
| 600183 | EPS (元) | N/A | 2.29 | 3.23 | 3.23 | 4.19 | 4.19 |
| 603186 | Revenue (亿元) | 73.43 | 73.43 | 95.53 | 95.53 | 134.27 | 134.27 |
| 603186 | NPP (亿元) | 5.73 | 5.73 | 8.02 | 8.03 | 10.54 | 10.54 |
| 603186 | EPS (元) | 3.65 | 4.04 | 5.12 | 5.65 | 6.72 | 6.72 |

## Interpretation

- 002463 no longer looks like a tight two-source range after adding Xinda and Tianfeng: the low-end 2026E/2027E profit lines are materially lower than the older high-growth models. This improves forecast-risk disclosure but does not solve the missing customer/platform split.
- 300476 has the widest growth dispersion among core PCB names, consistent with high-beta GPU/ASIC exposure and high dependence on customer ramp assumptions.
- 002916 has relatively tight 2026E revenue/NPP range and an explicit CMBI target-price methodology, improving valuation audit quality.
- 600183 shows model-date dispersion: the older Guohai 2024E-2026E model is materially below the newer Pacific 2026E-2028E model. Use it as evidence of forecast revision risk, not as equal-weight consensus.
- 603186 is upgraded again after adding the 2026 Zheshang annual-review PDF: 2028E revenue/NPP/EPS are now covered, and the 2026E/2027E EPS range reveals basis differences between model dates. It still lacks customer/platform bottom-up assumptions.

## Use in Report

- Use ranges to discuss forecast uncertainty and valuation discipline.
- Do not average ranges into an AStock target price.
- Do not treat single-source lines as consensus.
- Keep customer/platform EPS bridge marked as incomplete until revenue by customer/platform is disclosed.
