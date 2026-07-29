# Valuation Audit — Full-Market Refresh

## Arithmetic

- Candidate rows: 142.
- Priority rows: 39.
- Formal rows: 4.
- Positive formal validation models: 3.
- Downside discipline models: 1.
- All formal bear values below current price: True.
- All formal probability targets recalculate: True.
- All formal upside values recalculate: True.
- All formal probability weights equal 30%/50%/20%: True.
- All formal final-target weights reconcile: True.

## Evidence and Model Boundary

- Q1 financial coverage: 142/142.
- Broker metadata coverage: 137/142.
- Broker PDF coverage: 137/142.
- Extracted target fields: 33/142.
- Candidate rows without current positive external anchor: 122/142.
- Formal rows with negative Q1 OCF: 3; these must stay validation models until cash conversion improves.
- Dynamic screening ranges are not equivalent to formal company-specific targets.
- Probability target formula and formal-row substitution values are disclosed in Chapter 3 and `refresh-20260715/data/current_valuation_model_20260715.json`.
- The 4 formal rows are current-price validation models and require independent IC review before any publication language stronger than watch/validation.

## Upside / Downside Outlier Review

| Bucket | Ticker | Company | Upside | Anchor quality | Action implication |
|---|---|---|---:|---|---|
| Top upside | 002432 | 九安医疗 | 323.4% | original_pdf_no_target_or_not_disclosed | high-upside model candidate / validate before entry |
| Top upside | 000623 | 吉林敖东 | 317.0% | original_pdf_no_target_or_not_disclosed | high-upside model candidate / validate before entry |
| Top upside | 600739 | 辽宁成大 | 300.0% | stale_or_aging_target_zero_to_low_weight | high-upside model candidate / validate before entry |
| Top upside | 000685 | 中山公用 | 162.8% | original_pdf_no_target_or_not_disclosed | high-upside model candidate / validate before entry |
| Top upside | 600150 | 中国船舶 | 142.9% | original_pdf_no_target_or_not_disclosed | high-upside model candidate / validate before entry |
| Top downside | 002174 | 游族网络 | -95.4% | original_pdf_no_target_or_not_disclosed | avoid / insufficient valuation quality |
| Top downside | 301377 | 鼎泰高科 | -87.1% | original_pdf_no_target_or_not_disclosed | high valuation risk / avoid chasing |
| Top downside | 002221 | 东华能源 | -81.4% | original_pdf_no_target_or_not_disclosed | avoid / insufficient valuation quality |
| Top downside | 002611 | 东方精工 | -81.2% | original_pdf_no_target_or_not_disclosed | avoid / insufficient valuation quality |
| Top downside | 301200 | 大族数控 | -74.4% | original_pdf_no_target_or_not_disclosed | high valuation risk / avoid chasing |

## IC Readiness Conclusion

- Positive formal rows are validation models, not direct allocation calls.
- Rows with missing or stale external anchors remain candidate/watch rows even when base evidence quality is high.
- Growth or AI-related valuation credit is conditional unless unit/order/ASP/customer or segment-purity evidence is available.
- Any upgrade from validation to portfolio action requires H2 deducted-profit delivery, operating-cash-flow confirmation, and a current auditable external anchor.

Model Reproducibility: PASS
