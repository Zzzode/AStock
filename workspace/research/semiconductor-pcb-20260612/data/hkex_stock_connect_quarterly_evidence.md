# HKEX Stock Connect Quarterly Shareholding Evidence

**Source:** HKEX / HKEXnews Stock Connect Northbound Shareholding Search By Date.

**Query date:** 2026-06-16

**Shareholding date:** 2026-03-31

**Raw HTML archive:**

- `data/raw_hkex_stock_connect/hkex_sz_20260331.html`
- `data/raw_hkex_stock_connect/hkex_sh_20260331.html`
- `data/raw_hkex_stock_connect/hkex_sz_post_20260331_returned_previous.html`
- `data/raw_hkex_stock_connect/hkex_sh_post_20260331_returned_previous.html`

**Boundary:** Starting from 2024-08-19, HKEX states that Stock Connect Northbound shareholding information is available only on a quarterly basis. The data below represents aggregate CCASS Participants' shareholdings as of the shareholding date. It is not beneficial-owner data, not broker-custodian-level data, and not terminal-grade realtime order flow.

## Target-universe coverage

| Ticker | Name | Market | HKEX stock code | CCASS shareholding | % of listed/traded A-shares |
|---|---|---|---:|---:|---:|
| 002463 | 沪电股份 | Shenzhen Connect | 72463 | 193,881,300 | 10.07% |
| 300476 | 胜宏科技 | Shenzhen Connect | 77476 | 24,946,693 | 2.85% |
| 002916 | 深南电路 | Shenzhen Connect | 72916 | 25,577,420 | 3.75% |
| 600183 | 生益科技 | Shanghai Connect | 90183 | 151,023,558 | 6.30% |
| 603186 | 华正新材 | Shanghai Connect | 93186 | 4,439,817 | 2.83% |
| 688519 | 南亚新材 | Shanghai Connect | 30519 | 1,467,526 | 0.62% |
| 002436 | 兴森科技 | Shenzhen Connect | 72436 | 27,744,596 | 1.63% |
| 301200 | 大族数控 | Shenzhen Connect | 78200 | 4,375,572 | 1.02% |
| 688630 | 芯碁微装 | Shanghai Connect | 30630 | 5,381,871 | 4.08% |
| 300400 | 劲拓股份 | Shenzhen Connect | 77400 | 2,445,364 | 1.00% |
| 301377 | 鼎泰高科 | Shenzhen Connect | 78377 | 5,857,928 | 1.42% |

## Quarter-on-quarter change

The HKEX form was also submitted with `txtShareholdingDate=2026/03/31`; the service returned the preceding available quarter, `2025/12/31`. The table below compares the two HKEX official quarterly snapshots.

| Ticker | Name | 2025/12/31 shares | 2025/12/31 pct | 2026/03/31 shares | 2026/03/31 pct | Share change | Pct-pt change |
|---|---|---:|---:|---:|---:|---:|---:|
| 002463 | 沪电股份 | 143,209,875 | 7.44% | 193,881,300 | 10.07% | +50,671,425 | +2.63 |
| 300476 | 胜宏科技 | 28,078,876 | 3.22% | 24,946,693 | 2.85% | -3,132,183 | -0.37 |
| 002916 | 深南电路 | 25,469,627 | 3.82% | 25,577,420 | 3.75% | +107,793 | -0.07 |
| 600183 | 生益科技 | 125,184,104 | 5.22% | 151,023,558 | 6.30% | +25,839,454 | +1.08 |
| 603186 | 华正新材 | 1,265,200 | 0.89% | 4,439,817 | 2.83% | +3,174,617 | +1.94 |
| 688519 | 南亚新材 | 1,645,332 | 0.70% | 1,467,526 | 0.62% | -177,806 | -0.08 |
| 002436 | 兴森科技 | 31,040,114 | 1.82% | 27,744,596 | 1.63% | -3,295,518 | -0.19 |
| 301200 | 大族数控 | 3,391,879 | 0.79% | 4,375,572 | 1.02% | +983,693 | +0.23 |
| 688630 | 芯碁微装 | 430,600 | 0.32% | 5,381,871 | 4.08% | +4,951,271 | +3.76 |
| 300400 | 劲拓股份 | 1,047,900 | 0.43% | 2,445,364 | 1.00% | +1,397,464 | +0.57 |
| 301377 | 鼎泰高科 | 3,029,291 | 0.73% | 5,857,928 | 1.42% | +2,828,637 | +0.69 |

## Interpretation

- HKEX official quarterly Stock Connect data now covers all 11 core/watchlist tickers for 2026Q1.
- The official HKEX table resolves the prior public-data gap where the AkShare/Eastmoney historical Stock Connect interface stopped at 2024-08-16 for most names and failed for 603186/300400.
- Hudian, Shengyi, Circuit Fabology and Shennan show the highest Stock Connect participation within the current coverage set.
- Quarter-on-quarter HKEX official data shows the largest absolute 2026Q1 northbound increases in Hudian and Shengyi, and the largest pct-point increases in Circuit Fabology, Hudian and Huazheng.
- This improves northbound positioning evidence, but it still does not identify beneficial owners, active/passive fund ownership, broker-custodian distribution, daily changes after 2024-08-19, or realtime order flow.
