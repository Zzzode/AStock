# Eastmoney Northbound Participant Detail Evidence

**Source:** Eastmoney public data API `RPT_NORTH_ORG_HOLDDETAIL_NEW`.

**Raw archive:** `data/eastmoney_northbound_participant_detail_20260331.json`

**Date:** 2026-03-31

**Boundary:** This is public Stock Connect participant / custodian-level data, not beneficial-owner data and not a complete paid terminal institutional-positioning database. Several percentage-change fields can look extreme when the prior base is small; use share count and market value first.

## Top participant summary

| Ticker | Name | Rows | Total MV | Total shares | Top participant | Top participant shares | Top participant MV | Top-5 MV share |
|---|---|---:|---:|---:|---|---:|---:|---:|
| 002463 | 沪电股份 | 52 | 147.29亿元 | 19,388.13万股 | 香港上海汇丰银行有限公司 | 9,581.98万股 | 72.79亿元 | 94.3% |
| 300476 | 胜宏科技 | 25 | 62.62亿元 | 2,494.67万股 | 香港上海汇丰银行有限公司 | 1,358.30万股 | 34.09亿元 | 92.8% |
| 002916 | 深南电路 | 44 | 56.14亿元 | 2,557.74万股 | 香港上海汇丰银行有限公司 | 1,074.11万股 | 23.58亿元 | 93.2% |
| 600183 | 生益科技 | 49 | 81.81亿元 | 15,102.36万股 | 香港上海汇丰银行有限公司 | 7,895.20万股 | 42.77亿元 | 89.6% |
| 603186 | 华正新材 | 15 | 2.66亿元 | 443.98万股 | 美林远东有限公司 | 162.72万股 | 0.97亿元 | 82.3% |
| 688519 | 南亚新材 | 12 | 1.90亿元 | 146.75万股 | 香港上海汇丰银行有限公司 | 68.84万股 | 0.89亿元 | 93.5% |
| 002436 | 兴森科技 | 31 | 5.56亿元 | 2,774.46万股 | 美国花旗银行 | 1,181.22万股 | 2.37亿元 | 86.1% |
| 301200 | 大族数控 | 16 | 7.10亿元 | 437.56万股 | 渣打银行(香港)有限公司 | 235.77万股 | 3.82亿元 | 98.6% |
| 688630 | 芯碁微装 | 15 | 10.41亿元 | 538.19万股 | 美国花旗银行 | 412.32万股 | 7.97亿元 | 94.7% |
| 300400 | 劲拓股份 | 10 | 0.57亿元 | 244.54万股 | 摩根士丹利香港证券有限公司 | 86.67万股 | 0.20亿元 | 89.5% |
| 301377 | 鼎泰高科 | 18 | 11.30亿元 | 585.79万股 | 香港上海汇丰银行有限公司 | 422.92万股 | 8.16亿元 | 91.9% |

## Interpretation

- Participant concentration is high: the top-five participant market-value share is above 80% for all 11 covered names.
- HSBC is the largest participant for Hudian, Shenghong, Shennan, Shengyi, Nanya and Dtech.
- Citi is the largest participant for Fastprint and Circuit Fabology; Standard Chartered is the largest participant for Han's CNC; Morgan Stanley is the largest participant for Jintuo; Merrill Lynch Far East is the largest participant for Huazheng.
- This improves public northbound custody-structure evidence, but it still cannot identify beneficial owners or active/passive fund exposure.
