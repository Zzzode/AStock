# 雅化集团（002497.SZ）财务与市场证据抓取清单

- 抓取日期：2026-07-23（Asia/Shanghai）。
- 财务披露优先级：公司在巨潮资讯网/深交所披露的原始 PDF（L1）；同名 `.txt` 是本地以 `pdftotext -layout` 从该 PDF 生成的检索衍生物，不能替代 PDF。
- 行情优先级：东方财富行情接口的原始 JSON（L2 市场数据快照，并非交易所正式披露）。接口在本次抓取时最新可得日为 2026-07-22；因此不得将其写成 2026-07-23 收盘价。
- 金额：财务原文均为人民币元；股数为股；行情接口的成交量为手（100 股/手）。

| 证据 ID | 文件 | 披露/数据日期 | 原始下载地址 | 用途 | SHA-256 |
|---|---|---|---|---|---|
| FIN-23A | `002497_2023_annual_report.pdf`（263 页） | 2024-04-26 | `https://static.cninfo.com.cn/finalpage/2024-04-26/1219832431.PDF` | 2023 审计财务报表 | `4057b7f546951bcdeaeb40ff7495154f41a20aae1c34746a02f2dcb05beef332` |
| FIN-24A | `002497_2024_annual_report.pdf`（270 页） | 2025-04-29（报告落款 2025-04-28） | `https://disc.static.szse.cn/disc/disk03/finalpage/2025-04-28/42dc4baf-863b-4297-aab3-84b317034f91.PDF` | 2024 审计财务报表 | `0e35aade14c3c008baab845bedaa3efe02ed46d476b2bae7a27b81243b253368` |
| FIN-25A | `002497_2025_annual_report.pdf`（254 页） | 2026-04-27 | `https://static.cninfo.com.cn/finalpage/2026-04-27/1225181781.PDF` | 2025 审计财务报表、分部与股本 | `11c4f9cd1cad31837315426c29cf0e1dd572b92adbca7b55d8d055406273efea` |
| FIN-26Q1 | `002497_2026_q1_report.pdf`（13 页） | 2026-04-27 | `https://static.cninfo.com.cn/finalpage/2026-04-27/1225181791.PDF` | 2026Q1 未审计财务数据 | `88b8bac313ba1b7945b92c970e456384d35e19d8f6aee03cc101fb6a7df11f7c` |
| FIN-26H1P | `002497_2026_h1_earnings_preview.pdf`（2 页） | 2026-07-07 | `https://static.cninfo.com.cn/finalpage/2026-07-07/1225411869.PDF` | 2026H1 业绩预告（未经审计） | `2270a14dad2e9b99c61f9bdf4c675ec336c07df45716204571d0e56849a56ff9` |
| SHARE-26 | `002497_2025_profit_distribution_implementation.pdf`（3 页） | 2026-06-13（公告落款 2026-06-12） | `https://disc.static.szse.cn/download/disc/disk03/finalpage/2026-06-13/8ad1831b-aa75-4194-95ff-244fe44fbec6.PDF` | 2026-06-18 总股本与回购专户股数复核 | `abbbc391b168d6948d7df659855ed6e314afa0684bfe87245c7950cac88b8e5b` |
| MKT-Q-0723 | `eastmoney_quote_002497_20260723.json` | 抓取 2026-07-23；字段反映最新可得 2026-07-22 | `https://push2.eastmoney.com/api/qt/stock/get?secid=0.002497&fields=f43,f44,f45,f46,f47,f48,f50,f57,f58,f60,f84,f85,f116,f117,f124,f162,f167,f168,f169,f170` | 价格、当日成交、市值、股本交叉核验 | `ad88c9b901af571f22740e2d726ea20e3d7717beb71e07e460cf9ba8ae14ce66` |
| MKT-K-0623 | `eastmoney_daily_kline_002497_20260601_20260723.json` | 2026-06-01 至 2026-07-22 | `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=0.002497&klt=101&fqt=0&beg=20260601&end=20260723&fields1=f1,f2,f3,f4,f5,f6&fields2=f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62` | 区间高低点、20 日成交活跃度 | `2c41d8a3848b3a0897d2bdc7c04d232ce921503f948ac4c47436b4d8b324ddb2` |

## 复核方法与限制

1. 年报的主要会计数据表与合并资产负债表、合并现金流量表相互核对；四期年报之间相邻年度的可比数也进行了交叉核验。
2. `购建固定资产、无形资产和其他长期资产支付的现金` 是现金流量口径的资本开支代理项，不等同于会计口径固定资产净增加额。
3. 2026H1 只有业绩预告：营业收入、经营现金流、资产负债表、存货及资本开支均为 **not disclosed**，不可用 2026Q1 或预测值代填。
4. 行情 JSON 的 `f124` 返回 `0`，未提供源内时间戳；以本地抓取时间与日线最后一根 `2026-07-22` 共同限定数据时点。行情未取得交易所原始逐笔/日行情文件，不能声称为交易所 L1 行情。
