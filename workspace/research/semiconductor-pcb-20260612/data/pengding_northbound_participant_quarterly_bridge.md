# Pengding Northbound Participant Quarterly Bridge

**Source:** Eastmoney public data API `RPT_NORTH_ORG_HOLDDETAIL_NEW`.

**Raw archive:** `data/pengding_northbound_participant_quarterly_bridge.json`

**Boundary:** Public Stock Connect participant / custodian-level data. This is not beneficial-owner data, not an active/passive fund classification, and not terminal-grade institutional order-flow.

## Quarterly bridge

| Date | Rows | Total shares | Total MV | Top participant | Top participant shares | Top-5 MV share |
|---|---:|---:|---:|---|---:|---:|
| 2025-06-30 | 28 | 4780.62万股 | 15.31亿元 | 香港上海汇丰银行有限公司 | 2302.61万股 | 92.2% |
| 2025-09-30 | 34 | 8239.70万股 | 46.20亿元 | 香港上海汇丰银行有限公司 | 3935.45万股 | 94.5% |
| 2025-12-31 | 32 | 6273.41万股 | 31.73亿元 | 香港上海汇丰银行有限公司 | 3310.79万股 | 96.8% |
| 2026-03-31 | 34 | 5707.02万股 | 29.77亿元 | 香港上海汇丰银行有限公司 | 2669.35万股 | 95.8% |

## Interpretation

- From 2025Q2 to 2026Q1, participant-held shares changed by 926.41万股.
- From 2025Q4 to 2026Q1, participant-held shares changed by -566.38万股, consistent with HKEX aggregate quarterly decline.
- 2026Q1 top participant is 香港上海汇丰银行有限公司 with 2669.35万股; top-five participant MV share is 95.8%.
- Treat as custody-structure evidence only; do not infer beneficial-owner identity or active/passive ownership.
