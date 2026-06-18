# Fund Holder Full Type Recheck

**Run date:** 2026-06-17

**Sources:** AkShare `stock_fund_stock_holder`; AkShare `fund_name_em`.

**Boundary:** This maps latest visible single-stock fund holder rows to Eastmoney public fund types where available, then falls back to name-rule buckets. It is still not Wind/Choice official active/passive classification and does not cover funds absent from the public holder endpoint.

## Coverage

| Ticker | Name | Period | Rows | Type mapped | Total MV | Main buckets |
|---|---|---|---:|---:|---:|---|
| 002463 | 沪电股份 | 2026-03-31 | 540 | 100.0% | 314.60亿元 | active_or_equity_type: 258.82亿元 (82.27%); passive_or_index_type: 50.48亿元 (16.05%); bond_or_fixed_income_type: 5.28亿元 (1.68%); active_like_name_rule: 0.02亿元 (0.01%) |
| 300476 | 胜宏科技 | 2026-03-31 | 373 | 99.46% | 170.39亿元 | active_or_equity_type: 108.19亿元 (63.5%); passive_or_index_type: 61.68亿元 (36.2%); bond_or_fixed_income_type: 0.48亿元 (0.28%); active_like_name_rule: 0.04亿元 (0.02%) |
| 002916 | 深南电路 | 2026-03-31 | 199 | 100.0% | 128.97亿元 | active_or_equity_type: 119.41亿元 (92.58%); passive_or_index_type: 6.71亿元 (5.2%); bond_or_fixed_income_type: 2.86亿元 (2.22%); active_like_name_rule: 0.00亿元 (0.0%) |
| 600183 | 生益科技 | 2026-03-31 | 286 | 100.0% | 62.46亿元 | active_or_equity_type: 60.93亿元 (97.54%); bond_or_fixed_income_type: 0.81亿元 (1.3%); passive_or_index_type: 0.72亿元 (1.15%); active_like_name_rule: 0.01亿元 (0.01%) |
| 603186 | 华正新材 | 2026-03-31 | 18 | 100.0% | 1.67亿元 | active_or_equity_type: 0.83亿元 (49.89%); bond_or_fixed_income_type: 0.61亿元 (36.33%); passive_or_index_type: 0.23亿元 (13.59%); active_like_name_rule: 0.00亿元 (0.19%) |
| 688519 | 南亚新材 | 2026-03-31 | 67 | 97.01% | 22.39亿元 | active_or_equity_type: 21.09亿元 (94.2%); bond_or_fixed_income_type: 1.21亿元 (5.39%); active_like_name_rule: 0.05亿元 (0.22%); passive_or_index_type: 0.04亿元 (0.19%) |
| 002436 | 兴森科技 | 2026-03-31 | 32 | 100.0% | 4.18亿元 | active_or_equity_type: 1.88亿元 (45.07%); passive_or_index_type: 1.28亿元 (30.61%); bond_or_fixed_income_type: 1.02亿元 (24.31%) |
| 301200 | 大族数控 | 2026-03-31 | 96 | 100.0% | 18.47亿元 | active_or_equity_type: 16.73亿元 (90.59%); bond_or_fixed_income_type: 1.11亿元 (6.0%); passive_or_index_type: 0.63亿元 (3.4%) |
| 688630 | 芯碁微装 | 2026-03-31 | 158 | 98.73% | 22.81亿元 | active_or_equity_type: 21.88亿元 (95.9%); passive_or_index_type: 0.89亿元 (3.91%); active_like_name_rule: 0.04亿元 (0.18%); bond_or_fixed_income_type: 0.00亿元 (0.01%) |
| 300400 | 劲拓股份 | 2025-12-31 | 145 | 100.0% | 1.10亿元 | active_or_equity_type: 0.71亿元 (64.73%); passive_or_index_type: 0.38亿元 (34.76%); bond_or_fixed_income_type: 0.01亿元 (0.51%) |
| 301377 | 鼎泰高科 | 2026-03-31 | 72 | 100.0% | 52.81亿元 | active_or_equity_type: 45.10亿元 (85.4%); bond_or_fixed_income_type: 7.16亿元 (13.55%); passive_or_index_type: 0.55亿元 (1.05%) |

## Interpretation

- The public fund-holder layer now has a full latest-period type recheck for all visible rows returned by `stock_fund_stock_holder`.
- Most rows still lack a formal Eastmoney fund-type field in `fund_name_em`, so the residual classification uses the existing name-rule buckets.
- This improves the public active/passive-style read-through but does not satisfy the strict requirement for official active/passive ownership labels from a paid terminal database.
