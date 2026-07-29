# Normalized Broker Report Catalog

## Collection Metadata

- Collection date: 2026-07-18
- Scope: Huawei Atlas 950 / SuperPoD / domestic compute / AIDC chain
- Primary window: 2026-01-19 to 2026-07-18
- Landmark extension: 2023-01-01 to 2026-07-18 for 002261
- Unique reports: 38
- Original broker PDFs archived: 38
- Extracted report texts: 38
- Priority ticker coverage: 14 / 14
- Fresh-window priority ticker coverage: 13 / 14

The source index is [`sources/broker-reports/2026-07-18/index.md`](../sources/broker-reports/2026-07-18/index.md). The normalized forecast rows are in [`data/broker_street_consensus_20260718.md`](./broker_street_consensus_20260718.md) and its JSON twin.

## Source Governance Defaults

Unless a row explicitly states otherwise:

- `source_form`: `original_pdf`
- `source_quality`: `original_pdf`
- `evidence_tier`: `primary`
- `download_status`: `downloaded`
- `exhaustion_reason`: `null`
- `valuation_weight`: `1.0` for ticker reports used in the Street packet
- `confidence`: `medium` when the report date is more than 30 days before the collection date; report 03 is `high`

Eastmoney is the discovery and mirror layer, not the research author. Each downloaded PDF is broker-branded and preserves the broker's original analyst, rating, forecast table, methodology, risk disclosure, and legal disclaimer.

## Report Register

| ID | Ticker / scope | Broker | Analyst(s) | Date | Exact report title | Type | Rating | Target | Source URL | Local evidence | Confidence |
|---:|---|---|---|---|---|---|---|---|---|---|---|
| 01 | 000034 | 开源证券 | 刘逍遥 | 2026-04-30 | 公司信息更新报告：收入快速增长，AI相关业务高质量发展 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604301821801378.html) | [PDF](../sources/broker-reports/2026-07-18/01-000034-AP202604301821801378.pdf) / [TXT](../sources/broker-reports/2026-07-18/01-000034-AP202604301821801378.txt) | medium |
| 02 | 002261 | 民生证券 | 吕伟, 郭新宇 | 2024-04-28 | 2023年年报及2024年一季报点评：拥抱华为布局AI软硬件，打开长期成长空间 | landmark_earnings_review | 推荐（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202404271631498557.html) | [PDF](../sources/broker-reports/2026-07-18/02-002261-AP202404271631498557.pdf) / [TXT](../sources/broker-reports/2026-07-18/02-002261-AP202404271631498557.txt) | medium; stale |
| 03 | 000988 | 太平洋证券 | 宋辰超 | 2026-06-21 | 业绩稳步增长，AI光联接加速放量 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202606211823707850.html) | [PDF](../sources/broker-reports/2026-07-18/03-000988-AP202606211823707850.pdf) / [TXT](../sources/broker-reports/2026-07-18/03-000988-AP202606211823707850.txt) | high |
| 04 | 000988 | 国金证券 | 张真桢 | 2026-05-05 | 光模块业务营收翻倍，积极扩产备货 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202605051821967959.html) | [PDF](../sources/broker-reports/2026-07-18/04-000988-AP202605051821967959.pdf) / [TXT](../sources/broker-reports/2026-07-18/04-000988-AP202605051821967959.txt) | medium |
| 05 | 000988 | 国金证券 | 张真桢 | 2026-03-27 | 光连接业务放量，前瞻布局领先技术 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603271820790519.html) | [PDF](../sources/broker-reports/2026-07-18/05-000988-AP202603271820790519.pdf) / [TXT](../sources/broker-reports/2026-07-18/05-000988-AP202603271820790519.txt) | medium |
| 06 | 002281 | 华鑫证券 | 庄宇, 张璐 | 2026-03-30 | 公司动态研究报告：打造AI全栈光互连解决方案，持续加码核心能力建设 | initiation | 买入（首次） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603301820858162.html) | [PDF](../sources/broker-reports/2026-07-18/06-002281-AP202603301820858162.pdf) / [TXT](../sources/broker-reports/2026-07-18/06-002281-AP202603301820858162.txt) | medium |
| 07 | 600183 | 太平洋证券 | 张世杰, 李珏晗 | 2026-05-27 | 产品结构优化，业绩爆发式增长 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202605271822915980.html) | [PDF](../sources/broker-reports/2026-07-18/07-600183-AP202605271822915980.pdf) / [TXT](../sources/broker-reports/2026-07-18/07-600183-AP202605271822915980.txt) | medium |
| 08 | 600183 | 西南证券 | 胡杨, 王书龙 | 2026-05-19 | 2026年一季报点评：全面拥抱AI浪潮，业绩弹性持续释放 | initiation | 买入（首次） | CNY103.50 | [detail](https://data.eastmoney.com/report/info/AP202605191822431344.html) | [PDF](../sources/broker-reports/2026-07-18/08-600183-AP202605191822431344.pdf) / [TXT](../sources/broker-reports/2026-07-18/08-600183-AP202605191822431344.txt) | medium |
| 09 | 600183 | 国元证券 | 彭琦 | 2026-05-06 | 2025年年报及26Q1季报点评：AI需求驱动产品升级，高端材料与PCB共振成长 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202605061821983612.html) | [PDF](../sources/broker-reports/2026-07-18/09-600183-AP202605061821983612.pdf) / [TXT](../sources/broker-reports/2026-07-18/09-600183-AP202605061821983612.txt) | medium |
| 10 | 002916 | 太平洋证券 | 张世杰, 李珏晗 | 2026-03-26 | AI算力+存储产品共驱25年业绩超预期增长 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603261820758345.html) | [PDF](../sources/broker-reports/2026-07-18/10-002916-AP202603261820758345.pdf) / [TXT](../sources/broker-reports/2026-07-18/10-002916-AP202603261820758345.txt) | medium |
| 11 | 002916 | 中银证券 | 苏凌瑶, 茅珈恺 | 2026-03-17 | AI、通信、汽车三轮驱动PCB高增，封装基板加速突破 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603171820605311.html) | [PDF](../sources/broker-reports/2026-07-18/11-002916-AP202603171820605311.pdf) / [TXT](../sources/broker-reports/2026-07-18/11-002916-AP202603171820605311.txt) | medium |
| 12 | 002916 | 招银国际 | Kevin Zhang, Aaron Guo | 2026-03-16 | AI-led PCB growth with substrate upside ahead | earnings_review | 买入（维持） | CNY288.00 | [detail](https://data.eastmoney.com/report/info/AP202603161820576271.html) | [PDF](../sources/broker-reports/2026-07-18/12-002916-AP202603161820576271.pdf) / [TXT](../sources/broker-reports/2026-07-18/12-002916-AP202603161820576271.txt) | medium |
| 13 | 002463 | 中邮证券 | 万玮, 吴文吉 | 2026-04-24 | 高速交换机业务高增，产能扩张蓄力长期成长 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604241821528775.html) | [PDF](../sources/broker-reports/2026-07-18/13-002463-AP202604241821528775.pdf) / [TXT](../sources/broker-reports/2026-07-18/13-002463-AP202604241821528775.txt) | medium |
| 14 | 002463 | 中银证券 | 苏凌瑶, 茅珈恺 | 2026-04-15 | 乘AI与高速运算东风，业绩增长动能强劲 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604151821233085.html) | [PDF](../sources/broker-reports/2026-07-18/14-002463-AP202604151821233085.pdf) / [TXT](../sources/broker-reports/2026-07-18/14-002463-AP202604151821233085.txt) | medium |
| 15 | 002463 | 信达证券 | 莫文宇 | 2026-04-15 | 沪电股份26Q1业绩预告点评：AI算力景气度持续验证，高端产能释放在即 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604151821219015.html) | [PDF](../sources/broker-reports/2026-07-18/15-002463-AP202604151821219015.pdf) / [TXT](../sources/broker-reports/2026-07-18/15-002463-AP202604151821219015.txt) | medium |
| 16 | 002463 | 东莞证券 | 罗炜斌 | 2026-04-02 | 2025年报点评：AI驱动业绩增长，盈利能力提升 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604021820982346.html) | [PDF](../sources/broker-reports/2026-07-18/16-002463-AP202604021820982346.pdf) / [TXT](../sources/broker-reports/2026-07-18/16-002463-AP202604021820982346.txt) | medium |
| 17 | 002463 | 华金证券 | 熊军, 王延森 | 2026-03-31 | 核心业务景气延续，业绩与盈利能力同步提升 | earnings_review | 增持（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603311820915887.html) | [PDF](../sources/broker-reports/2026-07-18/17-002463-AP202603311820915887.pdf) / [TXT](../sources/broker-reports/2026-07-18/17-002463-AP202603311820915887.txt) | medium |
| 18 | 002463 | 太平洋证券 | 张世杰, 李珏晗 | 2026-03-30 | 数据通讯板驱动25年业绩高增，国内外产能加速布局 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603301820877667.html) | [PDF](../sources/broker-reports/2026-07-18/18-002463-AP202603301820877667.pdf) / [TXT](../sources/broker-reports/2026-07-18/18-002463-AP202603301820877667.txt) | medium |
| 19 | 300476 | 开源证券 | 陈蓉芳, 刘琦 | 2026-04-30 | 公司信息更新报告：2026Q1业绩同环比增长，产能建设加快推进中 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604301821801387.html) | [PDF](../sources/broker-reports/2026-07-18/19-300476-AP202604301821801387.pdf) / [TXT](../sources/broker-reports/2026-07-18/19-300476-AP202604301821801387.txt) | medium |
| 20 | 300476 | 东莞证券 | 罗炜斌 | 2026-04-29 | 深度报告：卡位优势明显，充分受益AI PCB浪潮 | initiation | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604291821740007.html) | [PDF](../sources/broker-reports/2026-07-18/20-300476-AP202604291821740007.pdf) / [TXT](../sources/broker-reports/2026-07-18/20-300476-AP202604291821740007.txt) | medium |
| 21 | 300476 | 中邮证券 | 万玮, 吴文吉 | 2026-04-19 | 高端PCB突破，全球化产能落地 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604191821319954.html) | [PDF](../sources/broker-reports/2026-07-18/21-300476-AP202604191821319954.pdf) / [TXT](../sources/broker-reports/2026-07-18/21-300476-AP202604191821319954.txt) | medium |
| 22 | 300476 | 东莞证券 | 罗炜斌 | 2026-04-01 | 2025年报点评：全年业绩高增，AI PCB成长逻辑明确 | earnings_review | 买入 | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604011820950863.html) | [PDF](../sources/broker-reports/2026-07-18/22-300476-AP202604011820950863.pdf) / [TXT](../sources/broker-reports/2026-07-18/22-300476-AP202604011820950863.txt) | medium |
| 23 | 002837 | 国金证券 | 张真桢 | 2026-04-24 | Q1利润短期承压，液冷增长强劲 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604241821526861.html) | [PDF](../sources/broker-reports/2026-07-18/23-002837-AP202604241821526861.pdf) / [TXT](../sources/broker-reports/2026-07-18/23-002837-AP202604241821526861.txt) | medium |
| 24 | 002837 | 开源证券 | 殷晟路, 蒋颖, 杜致远 | 2026-04-22 | 公司信息更新报告：液冷龙头沉潜蓄势，看好下半年液冷兑现 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604221821435857.html) | [PDF](../sources/broker-reports/2026-07-18/24-002837-AP202604221821435857.pdf) / [TXT](../sources/broker-reports/2026-07-18/24-002837-AP202604221821435857.txt) | medium |
| 25 | 301018 | 国金证券 | 姚遥 | 2026-04-29 | 业绩符合预期，在手订单充沛、液冷业务蓄势待发 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604291821723936.html) | [PDF](../sources/broker-reports/2026-07-18/25-301018-AP202604291821723936.pdf) / [TXT](../sources/broker-reports/2026-07-18/25-301018-AP202604291821723936.txt) | medium |
| 26 | 301018 | 国金证券 | 姚遥 | 2026-04-26 | 算力、能源双轮驱动，温控业务迈入高增周期 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604261821593938.html) | [PDF](../sources/broker-reports/2026-07-18/26-301018-AP202604261821593938.pdf) / [TXT](../sources/broker-reports/2026-07-18/26-301018-AP202604261821593938.txt) | medium |
| 27 | 002335 | 东吴证券 | 曾朵红, 郭亚男 | 2026-04-27 | 2025年报及2026年一季报点评：智算中心技术客户储备充分有望高增、新能源加大海外扩张持续修复 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604271821646522.html) | [PDF](../sources/broker-reports/2026-07-18/27-002335-AP202604271821646522.pdf) / [TXT](../sources/broker-reports/2026-07-18/27-002335-AP202604271821646522.txt) | medium |
| 28 | 002130 | 山西证券 | 张天 | 2026-02-10 | 产能业绩稳步释放，铜连接龙头市场地位稳固 | earnings_review | 买入-A（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202602101819851833.html) | [PDF](../sources/broker-reports/2026-07-18/28-002130-AP202602101819851833.pdf) / [TXT](../sources/broker-reports/2026-07-18/28-002130-AP202602101819851833.txt) | medium |
| 29 | electronic industry | 万联证券 | 夏清莹, 陈达 | 2026-03-09 | 电子行业跟踪报告：华为发布新一代算力底座，LCD TV面板价格延续上涨 | industry_follow_up | 强于大市（维持） | Not applicable | [detail](https://data.eastmoney.com/report/info/AP202603091820410783.html) | [PDF](../sources/broker-reports/2026-07-18/29-industry-AP202603091820410783.pdf) / [TXT](../sources/broker-reports/2026-07-18/29-industry-AP202603091820410783.txt) | medium |
| 30 | liquid cooling industry | 华源证券 | 李泽, 陈佳敏 | 2026-04-12 | 汽车行业周报：关注26年起国产超节点液冷新增量 | industry_follow_up | 看好（维持） | Not applicable | [detail](https://data.eastmoney.com/report/info/AP202604121821141903.html) | [PDF](../sources/broker-reports/2026-07-18/30-industry-AP202604121821141903.pdf) / [TXT](../sources/broker-reports/2026-07-18/30-industry-AP202604121821141903.txt) | medium |
| 31 | 002025 | 华鑫证券 | 庄宇, 宋子豪, 何鹏程, 石俊烨 | 2026-03-21 | 公司动态研究报告：Token通胀推动国产AI算力需求增长，高速连接器厂商有望再乘东风 | initiation | 买入（首次） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202603221820687820.html) | [PDF](../sources/broker-reports/2026-07-18/31-002025-AP202603221820687820.pdf) / [TXT](../sources/broker-reports/2026-07-18/31-002025-AP202603221820687820.txt) | medium |
| 32 | 688629 | 山西证券 | 张天 | 2026-02-13 | 国产超节点项目储备丰富，高速线模组加速放量 | earnings_review | 买入-B（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202602131819921088.html) | [PDF](../sources/broker-reports/2026-07-18/32-688629-AP202602131819921088.pdf) / [TXT](../sources/broker-reports/2026-07-18/32-688629-AP202602131819921088.txt) | medium |
| 33 | 002230 | 信达证券 | 傅晓烺 | 2026-05-08 | 盈利能力提升，AI大模型商业化加速落地 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202605081822079900.html) | [PDF](../sources/broker-reports/2026-07-18/33-002230-AP202605081822079900.pdf) / [TXT](../sources/broker-reports/2026-07-18/33-002230-AP202605081822079900.txt) | medium |
| 34 | 002230 | 中邮证券 | 孙业亮, 刘聪颖 | 2026-02-03 | 经营质量显著改善，C端业务打开增长天花板 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202602031819566735.html) | [PDF](../sources/broker-reports/2026-07-18/34-002230-AP202602031819566735.pdf) / [TXT](../sources/broker-reports/2026-07-18/34-002230-AP202602031819566735.txt) | medium |
| 35 | 002025 | 国信证券 | 李聪, 石昆仑 | 2026-06-11 | 防务互连与驱动核心供应商，AI算力开辟新增长极 | initiation_update | 优于大市（维持） | CNY69-78 | [detail](https://data.eastmoney.com/report/info/AP202606111823464572.html) | [PDF](../sources/broker-reports/2026-07-18/35-002025-AP202606111823464572.pdf) / [TXT](../sources/broker-reports/2026-07-18/35-002025-AP202606111823464572.txt) | medium |
| 36 | 002025 | 国信证券 | 李聪, 石昆仑 | 2026-05-06 | 防务互连与驱动核心供应商，AI算力开辟新增长极 | initiation | 优于大市（首次） | CNY67-81 | [detail](https://data.eastmoney.com/report/info/AP202605061821983338.html) | [PDF](../sources/broker-reports/2026-07-18/36-002025-AP202605061821983338.pdf) / [TXT](../sources/broker-reports/2026-07-18/36-002025-AP202605061821983338.txt) | medium |
| 37 | 002025 | 中航证券 | 王玉茜, 严慧, 滕明滔, 方晓明, 张超 | 2026-04-23 | 2025年报点评：订货创历史新高，战新产业布局取得较好成效 | earnings_review | 买入（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202605271822913868.html) | [PDF](../sources/broker-reports/2026-07-18/37-002025-AP202605271822913868.pdf) / [TXT](../sources/broker-reports/2026-07-18/37-002025-AP202605271822913868.txt) | medium |
| 38 | 002025 | 山西证券 | 骆志伟, 李通 | 2026-04-15 | 战新市场拓展见成效，把握新赛道发展机遇 | earnings_review | 增持-A（维持） | Not disclosed | [detail](https://data.eastmoney.com/report/info/AP202604151821239820.html) | [PDF](../sources/broker-reports/2026-07-18/38-002025-AP202604151821239820.pdf) / [TXT](../sources/broker-reports/2026-07-18/38-002025-AP202604151821239820.txt) | medium |

## Core Thesis and Exact Data-Point Register

The report title in the register is retained as the title-level core thesis. The following high-value data points are copied from the original text; no AStock forecast is mixed into this catalog.

- ID 01: 2026Q1 AI-related business revenue was approximately CNY15.5bn, up 119% year on year; the report also names the KunTai A989 I3 supernode server based on the Kunpeng + Ascend route.
- ID 03: 2026E-2028E net profit is CNY2.471bn / CNY3.334bn / CNY4.058bn; risk flags are order timing, optical-module material shortages, and industry competition.
- ID 08: the broker assigns 45x 2026E P/E and CNY103.50 target price.
- ID 12: the broker assigns CNY288 target price based on 38x FY26E P/E, using a blended 33x PCB / 42x substrate peer framework; reported upside is 15.1%.
- ID 29: Atlas 950 SuperPoD uses 64 cards per cabinet unit and supports up to 8,192 NPU cards.
- ID 31: the report states Atlas 950 SuperPoD is expected in 2026Q4, supports 8,192 Ascend cards, and uses a full-liquid-cooling architecture without an air-cooled option.
- ID 32: 910C / 950 / 960 / 970 interconnect bandwidth is 784GB/s / 2TB/s / 2.2TB/s / 4TB/s; signed high-speed line-module orders reached CNY620mn as of 2025-10-27.
- ID 35: 2026E-2028E net profit is CNY387mn / CNY539mn / CNY610mn and the reasonable value range is CNY69-78.
- ID 33: 2026E-2028E EPS is CNY0.49 / CNY0.65 / CNY0.84; the valuation table shows 101.75x / 76.64x / 59.59x P/E.

## Risk-Flag Register

Exact risk wording is preserved in every local text. Repeated report-level risks include demand underperformance, customer qualification delay, capacity ramp delay, raw-material inflation, supply constraints, and intensified competition. Material report-specific examples:

- ID 02: `国产AI服务器采购不及预期；新业务拓展不及预期；同业竞争加剧的风险。`
- ID 03: `订单落地节奏不及预期、光模块物料紧缺、行业竞争加剧。`
- ID 08: `市场竞争加剧、AI需求不及预期、客户导入不及预期等风险。`
- ID 24: `储能温控行业竞争加剧、数据中心风冷及液冷产品放量不及预期、产能扩张风险、财务费用风险、大客户依赖风险、汇兑风险、应收账款坏账风险。`
- ID 28: risks include customer self-production of copper cables, alternative supplier introduction, 448G pricing, Rubin platform design changes, and raw-material cost pass-through.
- ID 32: risks include AI-server shipment underperformance, supernode delay due to protocol/supply-chain immaturity, capacity-yield ramp underperformance, defense procurement timing, and the 2026-06-29 lock-up expiry.

## Explicit Gaps

1. `002261 fresh original report`: `not_found`. Eastmoney returned zero rows in the 180-day window. The 2024 landmark PDF is archived but receives valuation weight zero and has no 2027E forecast.
2. `Target price`: available only for 600183, 002916, and 002025. Other targets remain `not disclosed`.
3. `002230 linkage`: official Ascend 950 downstream co-development evidence is outside this broker packet; the two broker reports are used only for Street forecasts and rating context.
4. `002025 linkage`: the broker corpus supports high-speed backplane, liquid-cooling interconnect, AI-compute and Atlas 950 demand exposure, but does not establish a Huawei-specific supplier relationship.

## Consensus Snapshot

- Usable latest-per-broker weighted ticker reports: 30.
- Bullish / positive: 30.
- Neutral: 0.
- Bearish: 0.
- Zero-weight rows: four superseded same-broker updates, the stale 002261 landmark report, and the explicit fresh-report `not_found` gap row.
- Target price observations: 600183 CNY103.50; 002916 CNY288.00; 002025 CNY67-81 and CNY69-78.
- Main divergence points: 000988 2027E revenue, 002837 2027E profit, and 002025 2026E-2027E earnings.
