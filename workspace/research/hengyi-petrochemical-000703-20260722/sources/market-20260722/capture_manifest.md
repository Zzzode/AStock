# 恒逸石化市场与结构化数据抓取清单

抓取日期：2026-07-22（Asia/Shanghai）  
数据截止：实时盘口截至 2026-07-22 13:52；完整日线截至 2026-07-21。

| 文件 | 能力/适配器 | 口径 | 质量与限制 |
|---|---|---|---|
| `astock_quote_000703_20260722.json` | `astock.cli quote` / `astock.capabilities.get_quote()` | 2026-07-22 13:52 实时行情 | `full_realtime`；PE、PB、总市值、流通市值返回 0，均不采用 |
| `astock_market_snapshot_000703_20260722.json` | `astock.cli market-snapshot` / Sina stream | 2026-07-22 13:51:51 盘口、股数成交量与金额 | 盘中快照，不是收盘价 |
| `akshare_sina_qfq_daily_000703_20250722_20260722.json` | `akshare.stock_zh_a_daily` / Sina Finance | 前复权日线，242 个完整交易日 | 截止 2026-07-21；2026-07-22 盘中行情单独保存 |
| `astock_financials_000703_20260722.json` | `astock.cli financials` / `akshare.stock_financial_abstract` | 12 个报告期结构化财务摘要 | 仅作交叉核验，最终数值以巨潮原始财报为准 |
| `astock_news_000703_20260722.json` | `astock.cli news` | 365 日公司事件与新闻发现包 | 二手新闻不支持已核验财务数值；公告类事件回到巨潮 PDF |
| `provenance_20260722.json` | `astock.capabilities.create_data_provenance_record()` / `combine_data_provenance_records()` | 全部数据包来源、时间、质量和警告 | 机器可读 provenance |

## 失败与降级记录

- `astock.cli analyze 000703 --json` 返回空输出，未形成可审计历史行情包。
- `QuoteService.get_daily()` 公开服务路径在本次环境中也未返回可序列化输出。
- 按项目数据采集约定降级到其既有 AkShare/Sina 历史行情适配器；日线源和前复权口径已显式写入原始 JSON。

