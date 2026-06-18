# Eastmoney Stock Connect Holding Recheck

**Run date:** 2026-06-17

**Source:** Eastmoney public DataCenter API (`RPT_MUTUAL_HOLDSTOCKNDATE_STA_NEW`, `RPT_MUTUAL_HOLDNDATE_DET_NEW`).

**Raw archive:** `workspace/research/semiconductor-pcb-20260612/data/raw_eastmoney_hsgt_holding_recheck_20260617`

## Summary

| Ticker | Name | Latest date | Holding shares | QoQ change | Participant count | Holding MV | A-share ratio | Detail rows | Top participant | Top participant shares | Top-5 MV share |
|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---:|
| 002463 | 沪电股份 | 2026-03-31 | 193,881,300.00 | 35.38% | 53.00 | 14,729,162,361.00 | 10.08% | 53 | 香港上海汇丰银行有限公司 | 95,819,827.00 | 94.33% |
| 300476 | 胜宏科技 | 2026-03-31 | 24,946,693.00 | -11.15% | 26.00 | 6,261,619,943.00 | 2.86% | 26 | 香港上海汇丰银行有限公司 | 13,583,022.00 | 92.81% |
| 002916 | 深南电路 | 2026-03-31 | 25,577,420.00 | 0.42% | 45.00 | 5,614,499,464.20 | 3.75% | 45 | 香港上海汇丰银行有限公司 | 10,741,118.00 | 93.19% |
| 600183 | 生益科技 | 2026-03-31 | 151,023,558.00 | 20.64% | 50.00 | 8,180,946,136.86 | 6.22% | 50 | 香港上海汇丰银行有限公司 | 78,951,959.00 | 89.55% |
| 603186 | 华正新材 | 2026-03-31 | 4,439,817.00 | 250.92% | 15.00 | 265,945,038.30 | 2.83% | 15 | 美林远东有限公司 | 1,627,221.00 | 82.27% |
| 002938 | 鹏鼎控股 | 2026-03-31 | 57,070,245.00 | -9.03% | 34.00 | 2,977,354,681.65 | 2.46% | 34 | 香港上海汇丰银行有限公司 | 26,693,456.00 | 95.75% |
| 688519 | 南亚新材 | 2026-03-31 | 1,467,526.00 | -10.81% | 12.00 | 190,455,524.28 | 0.63% | 12 | 香港上海汇丰银行有限公司 | 688,406.00 | 93.46% |
| 002436 | 兴森科技 | 2026-03-31 | 27,744,596.00 | -10.62% | 31.00 | 556,279,149.80 | 1.63% | 31 | 美国花旗银行 | 11,812,157.00 | 86.10% |
| 301200 | 大族数控 | 2026-03-31 | 4,375,572.00 | 29.00% | 16.00 | 709,717,778.40 | 0.90% | 16 | 渣打银行(香港)有限公司 | 2,357,672.00 | 98.63% |
| 688630 | 芯碁微装 | 2026-03-31 | 5,381,871.00 | 1,149.85% | 15.00 | 1,040,853,851.40 | 4.09% | 15 | 美国花旗银行 | 4,123,198.00 | 94.69% |
| 300400 | 劲拓股份 | 2026-03-31 | 2,445,364.00 | 133.36% | 10.00 | 57,221,517.60 | 1.01% | 10 | 摩根士丹利香港证券有限公司 | 866,700.00 | 89.55% |
| 301377 | 鼎泰高科 | 2026-03-31 | 5,857,928.00 | 93.38% | 18.00 | 1,130,345,786.88 | 1.43% | 18 | 香港上海汇丰银行有限公司 | 4,229,213.00 | 91.90% |

## Boundary

- This is Eastmoney public Stock Connect participant / custodian-level data, not beneficial-owner data.
- The latest public holding date returned by this interface is quarterly (`2026-03-31`) for the current universe, consistent with the HKEX quarterly disclosure boundary.
- This improves participant-level attribution versus aggregate HKEX holdings, but it still does not provide daily post-rule-change northbound changes, active/passive fund classification or terminal-grade realtime order flow.
