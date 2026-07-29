# Broker / Street Evidence Packet — 2026-07-26

## Boundary

Six dated original broker PDFs were archived, one per provisional company evidence-test ticker. This is **not** an all-Street consensus: it is a selected, auditable broker-evidence set with no licensed population, no cross-broker mean and no current-price valuation pack. All rows have `valuation_weight = 0.00` and no company is rated or promoted to a core valuation pool.

Five reports disclose forecasts and a rating but no explicit target price. Their displayed current-price P/E is not reverse-engineered into a target. The one explicit target belongs to a 2025-02-28 report on 688506 and is stale at the 2026-07-26 cutoff; it is historical context only.

## Dated broker readings

| Ticker | Broker / date | Stated rating | 2026E revenue / NP / EPS | Explicit target / method | Evidence boundary | Weight |
|---|---|---|---|---|---|---:|
| 002371 北方华创 | 东吴证券, 2026-05-02 | 买入（维持） | CNY50,503m / 6,881m / 9.49 | Not disclosed; current-price P/E only | Original PDF supports the broker forecast, not a customer/order/acceptance or margin/cash bridge. | 0.00 |
| 688012 中微公司 | 爱建证券, 2026-03-03 | 买入（维持） | CNY16,203m / 3,158m / 5.04 | Not disclosed; current-price P/E only | Original PDF supports the broker forecast, not a current target or product/customer qualification evidence. | 0.00 |
| 600276 恒瑞医药 | 中邮证券, 2026-05-07 | 买入（维持） | CNY35,669m / 9,302.84m / 1.40 | Not disclosed; current-price P/E only | BD revenue context is not an asset-level recognition, probability, cost, royalty or cash-realisation bridge. | 0.00 |
| 688506 百利天恒 | 华泰研究, 2025-02-28 | 买入（维持） | CNY2,277m / -9.46m / -0.02 | CNY308.37; DCF, WACC 6.8%, perpetual growth 3.0% | Explicit target is materially stale and cannot be treated as a current target or consensus. | 0.00 |
| 002028 思源电气 | 东吴证券, 2026-04-25 | 买入（维持） | CNY27,610m / 4,609m / 5.89 | Not disclosed; current-price P/E only | Overseas-order narrative requires order, delivery, acceptance, receivable/cash and margin evidence. | 0.00 |
| 600406 国电南瑞 | 东吴证券, 2026-04-30 | 买入（维持） | CNY75,805m / 9,184m / 1.14 | Not disclosed; current-price P/E only | Power trend requires tender share and order-to-cash/margin proof before valuation use. | 0.00 |

`revenue_E` and `net_profit_E` in the JSON use CNY million; `EPS_E` uses CNY per share. Full 2027E/2028E tables, report metadata and source paths are in [`broker_street_consensus_20260726.json`](./broker_street_consensus_20260726.json).

## Evidence locations

| Ticker | Original PDF | Extracted text |
|---|---|---|
| 002371 | `sources/broker-core-20260726/002371-dongwu-20260502.pdf` | `sources/broker-core-20260726/002371-dongwu-20260502.txt` |
| 688012 | `sources/broker-core-20260726/688012-aijian-20260303.pdf` | `sources/broker-core-20260726/688012-aijian-20260303.txt` |
| 600276 | `sources/broker-core-20260726/600276-zhongyou-20260507.pdf` | `sources/broker-core-20260726/600276-zhongyou-20260507.txt` |
| 688506 | `sources/broker-core-20260726/688506-huatai-20250301.pdf` | `sources/broker-core-20260726/688506-huatai-20250301.txt` |
| 002028 | `sources/broker-core-20260726/002028-dongwu-20260425.pdf` | `sources/broker-core-20260726/002028-dongwu-20260425.txt` |
| 600406 | `sources/broker-core-20260726/600406-dongwu-20260430.pdf` | `sources/broker-core-20260726/600406-dongwu-20260430.txt` |

The `sources/probe-20260726/600406-*` files preserve the failed first direct-PDF identifier and the public metadata capture that exposed the correct document identifier. They are a retrieval audit trail, not evidence used for valuation.

## Non-use rule

- Do not call the six selected reports “Street consensus”.
- Do not average their forecasts across companies or infer targets from displayed P/E.
- Do not use the 688506 2025 target as a current target or calculate upside without a frozen price.
- Do not convert a positive broker rating into an AStock rating; the AStock case remains `watchlist only / insufficient evidence`.
