# 中国船舶（600150.SH）市场结构原始来源清单

采集时间：2026-07-22 23:52--23:53（Asia/Shanghai）。本目录保存供应商返回的原始 JSON，不对原始文件作字段改写；计算口径见 `../../data/market_structure_20260722.md` 与同名 JSON。

| 文件 | 数据供应商与精确请求 | 用途 | SHA-256 |
|---|---|---|---|
| `eastmoney_kline_daily_fqt1_front_adjusted_20230701_20260722.json` | `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.600150&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf52%2Cf53%2Cf54%2Cf55%2Cf56%2Cf57%2Cf58%2Cf59%2Cf60%2Cf61&klt=101&fqt=1&beg=20230701&end=20260722&lmt=5000` | 复权日 K 主序列；`fqt=1`（前复权） | `9e4671994497e7582345578af45fe7f69196cb228cee87c528a1906d37895cda` |
| `eastmoney_kline_daily_fqt0_unadjusted_20230701_20260722.json` | 同上，将 `fqt=1` 改为 `fqt=0` | 不复权交叉检查；不用于累计收益和回撤 | `102f56a0642c820dd63c2cf4784055a877f2f9b28d72c72142a83f9777a5ebdc` |
| `eastmoney_kline_daily_fqt2_back_adjusted_20230701_20260722.json` | 同上，将 `fqt=1` 改为 `fqt=2` | 后复权交叉检查；不用于本报告的累计收益和回撤 | `e8d85bd899bb1acefb29c39618f9bc813519b5503ef8a7ab2fe57338cb774042` |
| `eastmoney_quote_snapshot_core_20260722.json` | `https://push2.eastmoney.com/api/qt/stock/get?secid=1.600150&fields=f43%2Cf44%2Cf45%2Cf46%2Cf47%2Cf48%2Cf57%2Cf58%2Cf84%2Cf85%2Cf116%2Cf117%2Cf162%2Cf167%2Cf168%2Cf169%2Cf170%2Cf171%2Cf172%2Cf177` | 截止日价格、成交、换手、流通/总股本、市值 | `7c7b4706530f50b12a27362e43c572ea4860bb3141d35c16dde130fe73a4efdd` |
| `eastmoney_quote_snapshot_20260722.json` | 同一 Eastmoney `stock/get` 接口的扩展字段请求 | 原始扩展快照保留 | `5209fd36c1bcebac23a26e498b6e73eca5bc4d5ad910befc213ae9358c7e0cbf` |
| `eastmoney_freeholders_latest_20260722.json` | `https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_F10_EH_FREEHOLDERS&columns=ALL&filter=(SECURITY_CODE%3D%22600150%22)&pageNumber=1&pageSize=50&sortColumns=END_DATE&sortTypes=-1&source=WEB&client=WEB` | 最新披露期十大流通股东及占流通股比例 | `381d013d5a4d97da2707fa14e4aacd6403691df5ee0f1b3761f3b4b058f27627` |
| `eastmoney_holders_latest_20260722.json` | `https://datacenter-web.eastmoney.com/api/data/v1/get?reportName=RPT_F10_EH_HOLDERS&columns=ALL&filter=(SECURITY_CODE%3D%22600150%22)&pageNumber=1&pageSize=50&sortColumns=END_DATE&sortTypes=-1&source=WEB&client=WEB` | 股东披露交叉检查 | `1a58438c365b1126c3f50284627a8877b9552c7ffed27964d7aa256b2b771848` |
| `astock_quote_600150_20260722.json` | 项目原生：`.venv/bin/python -m astock.cli quote 600150 --json` | 盘后现货快照的独立交叉检查 | `22536017358be43dfe12b6bd76a0cb73947ff722c23104c360fbc4ddc2fb334d` |

## Eastmoney 日 K 字段说明

原始 `klines` 每行采用供应商逗号分隔格式：`f51` 日期、`f52` 开盘、`f53` 收盘、`f54` 最高、`f55` 最低、`f56` 成交量（手，1 手=100 股）、`f57` 成交额（元）、`f58` 振幅（%）、`f59` 涨跌幅（%）、`f60` 涨跌额、`f61` 换手率（%）。

`fqt=0/1/2` 分别归档为不复权、前复权、后复权；正文只以 `fqt=1` 计算历史收益、均线、区间高低和回撤。原始序列在除权除息前存在差异，例如 2023-07-03 收盘为不复权 32.73 元、前复权 31.90 元、后复权 80.23 元；2026-07-22 三者的未/前复权收盘同为 33.02 元，后复权为 82.81 元。

## 快照字段与边界

本报告使用 `stock/get` 的 `f43`（最新价，除以 100）、`f47`（成交量，手）、`f48`（成交额，元）、`f84`（流通股本）、`f85`（总股本）、`f116`（总市值）、`f117`（流通市值）、`f168`（换手率，除以 100）。字段映射以供应商公开行情 schema 为准，并已做机械交叉检查：`f47×100/f84=1.4394%`，与 `f168=1.44%` 一致；`33.02×f85=248,496,014,929.76` 元，与 `f116` 一致。

“流通股本”不是严格定义的“自由流通股本”。本目录中的股东数据能够说明 2026-03-31 前十大流通股东合计持有 4,176,801,659 股、占流通股本 55.5011%，但不提供对战略、长期或受限持仓的统一可交易性分类。因此，不以该数据倒推严格自由流通股本或自由流通市值。
