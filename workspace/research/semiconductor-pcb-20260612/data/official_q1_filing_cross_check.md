# Official Q1 Filing Cross-Check

**Purpose:** Map the normalized 2026Q1 financial checkpoint to archived official Q1 report text/PDF evidence. This is an audit layer over `official_financials_summary.md`.

**Source directory:** `workspace/research/semiconductor-pcb-20260612/sources/official-q1-20260615/`

| Ticker | Name | Revenue evidence | NPP evidence | OCF evidence | EPS | ROE | Source lines / caveat |
|---|---|---:|---:|---:|---:|---:|---|
| 002463 | 沪电股份 | 6,214,156,406 | 1,242,081,367 | 511,016,585 | 0.6455 | 7.81% | lines 41-49, 341, 408 |
| 300476 | 胜宏科技 | 5,519,485,066.85 | 1,288,427,592.46 | 2,116,658,463.16 | 1.48 | 7.62% | lines 46-58, 523, 674 |
| 002916 | 深南电路 | 6,595,587,902.38 | 850,230,796.58 | 247,409,844.58 | 1.28 | 4.83% | lines 46-58, 452, 595 |
| 600183 | 生益科技 | 8,141,455,910.40 | 1,158,139,324.56 | 546,349,825.06 | 0.48 | 6.68% | lines 43-65, 419, 846 |
| 603186 | 华正新材 | 1,234,291,571.69 | 30,920,963.67 | 56,462,565.34 | 0.21 | 1.59% | lines 43-63, 458, 562 |
| 688519 | 南亚新材 | 1,832,161,085.00 | 150,132,663.11 | -66,130,126.72 | 0.66 | 5.08% | lines 40-56, 440, 556 |
| 002436 | 兴森科技 | 1,818,166,949.77 | 18,744,694.13 | -247,107,316.08 | 0.01 | 0.35% | lines 47-59, 504, 655 |
| 301200 | 大族数控 | 1,955,152,850.95 | 322,917,809.55 | -645,629,809.30 | 0.73 | 3.74% | lines 46-58, 191-204, 331, 505, 661 |
| 688630 | 芯碁微装 | 514,721,784.95 | 108,392,641.70 | 164,561,893.24 | 0.83 | 4.59% | lines 41-57, 453, 589 |
| 300400 | 劲拓股份 | 168,818,040.83 | 25,599,300.97 | 11,235,303.93 | 0.11 | 3.52% | lines 36-44, 384, 493 |
| 301377 | 鼎泰高科 | 814,116,509.93 | 260,575,088.03 | -47,761,070.73 | 0.64 | 9.38% | lines 44-52, 405, 553 |
| 002938 | 鹏鼎控股 | 7,986,000,000 | 463,000,000 | 3,097,000,000 | 0.20 | N/A | archived separately; see `data/pengding_official_filing_evidence.md` and Q1 report lines 56-57, 451, 563-566 |

## Audit Notes

- Revenue, net-profit-parent, EPS, ROE and operating cash-flow lines are directly visible in text extraction for the covered reports where disclosed, though some line labels wrap across multiple PDF text lines. Pengding's ROE is left N/A in the normalized table because the extracted Q1 source used for the manual bridge did not provide a comparable ROE line in the same normalized format.
- A full external-publication audit should still manually compare against the PDF tables because PDF text extraction can split labels and values across lines.
- The original PDF and extracted text are archived, so any external publication can perform line-by-line manual validation.
- Q1 reports do not disclose named customer/platform revenue split.
