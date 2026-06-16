# Important Institution Category History Bridge

**Source:** Eastmoney DataCenter `RPT_STOCK_DETAILS_CHANGE`, archived in `data/important_institution_detail_evidence.json`.

**Purpose:** Improve public holding-data depth by aggregating visible important-institution holder rows by ticker, institution category and report date. This complements official top-ten holders, CNInfo fund-heavy holding, Sina fund-holder proxies and Stock Connect participant/custodian data.

## 2026Q1 visible institution category snapshot

| Ticker | Name | Org type | Holders | Shares | Market cap (CNY) | Share ratio sum |
|---|---|---|---:|---:|---:|---:|
| 002463 | 沪电股份 | 社保基金 | 2 | 21,435,841 | 1,628,480,840.77 | 1.1139% |
| 002916 | 深南电路 | 基本养老基金 | 1 | 2,800,002 | 614,628,439.02 | 0.4111% |
| 002916 | 深南电路 | 社保基金 | 2 | 4,946,070 | 1,085,711,825.70 | 0.7261% |
| 600183 | 生益科技 | 社保基金 | 1 | 7,918,228 | 428,930,410.76 | 0.3260% |

## 2026Q1 visible holder rows

| Ticker | Name | Report date | Org type | Holder | Shares | Market cap (CNY) | Share ratio | Change type |
|---|---|---|---|---|---:|---:|---:|---|
| 002463 | 沪电股份 | 2026-03-31 | 社保基金 | 全国社保基金一零九组合 | 11,580,547 | 879,774,155.59 | 0.6018% | 不变 |
| 002463 | 沪电股份 | 2026-03-31 | 社保基金 | 富国基金管理有限公司-社保基金2101组合 | 9,855,294 | 748,706,685.18 | 0.5121% | 新进 |
| 002916 | 深南电路 | 2026-03-31 | 基本养老基金 | 基本养老保险基金八零二组合 | 2,800,002 | 614,628,439.02 | 0.4111% | 新进 |
| 002916 | 深南电路 | 2026-03-31 | 社保基金 | 全国社保基金一一三组合 | 2,123,581 | 466,147,265.31 | 0.3118% | 新进 |
| 002916 | 深南电路 | 2026-03-31 | 社保基金 | 富国基金管理有限公司-社保基金2101组合 | 2,822,489 | 619,564,560.39 | 0.4144% | 减少 |
| 600183 | 生益科技 | 2026-03-31 | 社保基金 | 全国社保基金五零二组合 | 7,918,228 | 428,930,410.76 | 0.3260% | 新进 |

## Historical category coverage in archived rows

| Ticker | Name | Org type | First date | Latest date | Row count | Notes |
|---|---|---|---|---|---:|---|
| 002463 | 沪电股份 | 国家队 | 2015-09-30 | 2021-06-30 | 24 | Long historical state-team proxy; not current. |
| 002463 | 沪电股份 | 基本养老基金 | 2017-09-30 | 2024-09-30 | 8 | Historical pension-fund rows; no 2026Q1 pension row in this endpoint. |
| 002463 | 沪电股份 | 基金资产管理计划 | 2015-09-30 | 2015-09-30 | 10 | 2015 asset-management-plan rows only. |
| 002463 | 沪电股份 | 社保基金 | 2011-12-31 | 2026-03-31 | 27 | Includes current 2026Q1 social-security rows. |
| 002916 | 深南电路 | 其他 | 2025-06-30 | 2025-06-30 | 1 | Single category row. |
| 002916 | 深南电路 | 基本养老基金 | 2024-06-30 | 2026-03-31 | 4 | Includes current 2026Q1 pension row. |
| 002916 | 深南电路 | 社保基金 | 2018-09-30 | 2026-03-31 | 14 | Includes current 2026Q1 social-security rows. |
| 300476 | 胜宏科技 | 基本养老基金 | 2019-09-30 | 2023-06-30 | 14 | Historical pension-fund rows; no 2026Q1 category row in this endpoint. |
| 300476 | 胜宏科技 | 社保基金 | 2017-09-30 | 2024-12-31 | 30 | Historical social-security rows; no 2026Q1 category row in this endpoint. |
| 600183 | 生益科技 | 国家队 | 2015-09-30 | 2021-03-31 | 24 | Long historical state-team proxy; not current. |
| 600183 | 生益科技 | 基金 | 2015-12-31 | 2015-12-31 | 1 | Single old fund row. |
| 600183 | 生益科技 | 社保基金 | 2004-06-30 | 2026-03-31 | 48 | Includes current 2026Q1 social-security row. |
| 603186 | 华正新材 | 社保基金 | 2017-06-30 | 2025-09-30 | 15 | Historical social-security rows; no 2026Q1 category row in this endpoint. |

## Boundary

- This is visible public important-institution disclosure, not a complete institutional ownership database.
- Absence of a ticker/category row in 2026Q1 does not prove no institution held the stock; it only means no visible row was returned by this public endpoint.
- It does not provide beneficial-owner Stock Connect data, official active/passive fund classification, terminal-grade order flow or intraday flow.
- Use as a public category-holding proxy only.
