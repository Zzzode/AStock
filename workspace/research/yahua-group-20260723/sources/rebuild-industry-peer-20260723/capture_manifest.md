# 行业、价格与同业重建证据抓取清单

- 抓取日期：2026-07-23（Asia/Shanghai）。
- 本目录保留来源文件与由 PDF 机械提取的检索文本；`.txt` 不能替代原始 PDF。
- 质量分级：交易所/发行人披露为 L1；政府部门/行业协会原始网页为 L2；独立价格机构与媒体转述为 L3；券商观点另见案例既有 `sources/broker-reports/2026-07-23/`，不在本目录复存。

| ID | 本地文件 | 原始地址 | 发布日 | 质量 | 可用事实与限制 | SHA-256 |
|---|---|---|---|---|---|---|
| PEER-TQ-Q1 | `tianqi_2026q1_1225206465.pdf` | `https://static.cninfo.com.cn/finalpage/2026-04-28/1225206465.PDF` | 2026-04-28 | L1 | 天齐锂业 2026Q1 收入、利润及量价原因；含 SQM 投资收益，不能当作纯锂盐可比 | `564694f0e95dcef3472e4a0607e562a25401763d7d874cba91cb507e048391ab` |
| PEER-SX-Q1 | `shengxin_2026q1_e4ce76bc.pdf` | `https://disc.static.szse.cn/disc/disk03/finalpage/2026-04-30/e4ce76bc-d31f-4b54-a9df-12bf46856b4c.PDF` | 2026-04-30 | L1 | 盛新锂能 2026Q1 收入、利润、量价与印尼出货表述；未披露可直接用于雅化的单位盈利 | `3d5d299733672aa929a3fc57601ab05f6b4fd389ee036e03df64d12105ed6ff9` |
| PEER-GF-P | `ganfeng_2026q1_preview_1225111388.pdf` | `https://static.cninfo.com.cn/finalpage/2026-04-17/1225111388.PDF` | 2026-04-17 | L1 | 赣锋锂业 Q1 利润预告、量价与资源成本表述；为预告而非最终季报，且含 PLS 公允价值收益 | `c14f14d6d4def499dadc7e7910eee93d7a6389935724ea04853186729d3fe737` |
| PEER-EST-TQ | `eastmoney_SZ002466_profit_forecast.json` | `https://emweb.eastmoney.com/PC_HSF10/ProfitForecast/PageAjax?code=SZ002466` | 抓取 2026-07-23 | L2 聚合 | 9 家机构的天齐 2026E 聚合字段；机构样本、更新时间、方法与币种/口径须以接口字段为准，不是发行人指引 | `7268cb7a1ec01d2258a416e9c9a5138f70a4987622430ce3094cc96469aac9f5` |
| PEER-EST-GF | `eastmoney_SZ002460_profit_forecast.json` | `https://emweb.eastmoney.com/PC_HSF10/ProfitForecast/PageAjax?code=SZ002460` | 抓取 2026-07-23 | L2 聚合 | 11 家机构的赣锋 2026E 聚合字段；不能与雅化同口径直接估值比较 | `2c296286195dd0dce1bf35d83c718efd386be54147d41f263cde2654f875eef7` |
| PEER-EST-SX | `eastmoney_SZ002240_profit_forecast.json` | `https://emweb.eastmoney.com/PC_HSF10/ProfitForecast/PageAjax?code=SZ002240` | 抓取 2026-07-23 | L2 聚合 | 5 家机构的盛新 2026E 聚合字段；不是已实现业绩或雅化的盈利锚 | `d96779161de81ac6c97e059962c07897db448930ea79c77b0572fa5be81aeaa6` |
| PRICE-SMM-25D | `smm_2025_december_lithium_spot.html` | `https://news.smm.cn/news/103731790` | 2026-01-28 | L3 | SMM 回顾的 2025-12-31 电池级碳酸锂现货均价；页面为 gzip 编码原始响应，读取时须解压 | `bf64cea5f3d3853860b5376b820a58bf753cab083df6ffc33587256f12f06171` |
| PRICE-CNMN-26J | `cnmn_2026_07_01_lithium_spot.html` | `https://www.cnmn.com.cn/ShowNews1.aspx?id=471989` | 2026-07-01 | L3 | 2026-07-01 上海金属报价中电池级碳酸锂区间/均价；单日现货报价，不是年度均价 | `176a643d90cf746bc2fb6969124ce4bbabd37f6185be3deca8a318e5b2a04d94` |
| PRICE-MKT-26H1 | `wuhan_finance_2026_06_lithium_market.html` | `https://jrj.wuhan.gov.cn/ztzl_57/xyrd/dcczbsc/202606/t20260630_2814830.shtml` | 2026-06-30 | L3 | 对期现价格、供给扰动及回调的新闻性转述；不是官方现货基准，也不能用于公司成本 | `4187ee93aee9bc9b2e18d49379dc1aaa6beb46156dd8f98bd1da0446e64cf89d` |
| PRICE-SMM-26H1 | `smm_2026h1_lithium_review.html` | `https://news.smm.cn/news/103999601` | 2026-07-10 | L3 | SMM 对 2026H1 现货、产量、进口、仓单与需求的回顾；含模型/调研口径，不能替代交易所或公司结算数据 | `99d21e344acff410bc4029f353f45a0b0d888fd52ceedf075de7a1b7451da1c7` |
| PRICE-SMM-26J | `smm_2026_07_06_lithium_daily.html` | `https://news.smm.cn/news/103990016` | 2026-07-06 | L3 | 7 月初期现市场日评；未在公开摘要中给出可核验的当日现货绝对值，不能充作 7 月 23 日点位 | `65b1502c007096ae5a758febd414db3173008d881472e9e5d738cc0485067839` |
| DEMAND-CAAM-26H1 | `people_2026h1_nev_sales.html` | `https://finance.people.com.cn/n1/2026/0709/c1004-40756926.html` | 2026-07-09 | L2 | 人民网转述中汽协 2026H1 新能源车产销量与出口；不是锂盐实际采购或库存数据 | `29e595842586a741e3ac127f6f9beabf6f775533b090209520b0aeca91801dfc` |
| MINEPOL-MIIT-25 | `miit_2025_mining_explosives_safety.html` | `https://www.miit.gov.cn/xwfb/gxdt/sjdt/art/2025/art_4f4f2bfc73d0434d8cfe83f4a6225253.html` | 2025-04-30 | L2 | 民爆安全、改造与监管要求；不提供全国需求、雅化订单或份额 | `7609dce3ffd6559464f5c9bc3867b8f85c04551ec333c0f933abb04df02837ea` |
| MINEACT-XLGL-25 | `xilingol_2025_civil_explosives_activity.html` | `https://gxj.xlgl.gov.cn/gxj/xwdt/gxyw/2026011218080215250/index.html` | 2026-01-12 | L2 | 锡林郭勒盟 2025 年工业炸药生产、销售的区域性活动样本；不可外推为全国或雅化表现 | `63fedc463576bd12c5935539c2c3288f6e425392a7e326ecf6bab51a79a4393a` |

## 读取提示

1. `smm_2025_december_lithium_spot.html` 保存为服务端返回的 gzip 字节流；使用 `gzip -dc` 检视，未做人工改写。
2. 同业前三份 PDF 的 `.txt` 为 `pdftotext -layout` 生成的检索衍生物。
3. 所有价格来源均为市场报价或新闻转述，不能替代雅化集团的实际 ASP、结算价、矿石成本或套保损益披露。
