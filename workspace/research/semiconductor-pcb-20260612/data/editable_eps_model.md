# Editable EPS Model

**Status:** Editable forecast-line model built from downloaded broker PDFs. This is not a full operating segment model because customer-chain revenue assumptions are not fully disclosed.

| Ticker | Broker | 2026E revenue | 2027E revenue | 2028E revenue | 2026E NPP | 2027E NPP | 2028E NPP | 2026E EPS | 2027E EPS | 2028E EPS |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 002463 | 中邮证券 | 267 | 378 | 527 | 58 | 89 | 129 | 2.99 | 4.61 | 6.72 |
| 300476 | 开源证券 | 328.16 | 549.7 | 769.3 | 91.19 | 154.41 | 222.88 | 9.28 | 15.71 | 22.68 |
| 002916 | 太平洋 | 315.98 | N/A | N/A | 55.46 | 75.45 | 97.25 | 8.14 | 11.08 | 14.28 |
| 600183 | 太平洋 | 391.48 | 514.85 | 629.84 | 55.7 | 78.56 | 101.69 | 2.29 | 3.23 | 4.19 |
| 603186 | 浙商证券 | 73.43 | 95.53 | N/A | 5.73 | 8.03 | N/A | 4.04 | 5.65 | N/A |

## Sensitivity Design

- For each forecast year with NPP, the JSON includes plus/minus 10% NPP stress.
- Where revenue is available, the JSON also includes a net-margin-minus-2pct proxy.
- Supplemental broker PDFs add second-source model checks for 002463, 300476 and 002916, and a current 2025E-2027E model for 603186.
- Public sources do not disclose the full segment revenue, customer-chain revenue exposure, tax, share count, depreciation, capex and working-capital assumptions required for a customer/platform bottom-up EPS model.
