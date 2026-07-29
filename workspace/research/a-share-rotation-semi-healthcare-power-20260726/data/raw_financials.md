# 原始财务证据：初始广义观察池

- **案例**：`a-share-rotation-semi-healthcare-power-20260726`
- **编制日**：2026-07-26
- **财务截止口径**：FY2025、2026Q1，以及截至 2026-07-26 已披露的 2026H1 业绩预告、快报或中报。
- **用途限制**：本文件只记录 Phase-1 原始证据的可得性与观察池边界；不含估值、盈利预测、公司排序或投资结论。

## 结论先行：尚无可采集的公司财务表

`research_brief.md` 明确写明“Core valuation pool at intake: None”，且截至本次采集没有交付最终或临时的证券代码清单。因此没有对任何公司运行财务抓取，也没有填入收入、利润、EPS、现金流、订单、产能或估值字段。把指数成分或新闻中出现的公司反向当作本案覆盖标的，会把“主题暴露”误写成“公司级证据”，故不这样处理。

| 初始观察模块 | 可复现的官方篮子定义 | 样本/范围 | 财务可得状态 | 该定义不能证明的事项 |
|---|---|---:|---|---|
| 半导体材料与设备 | 中证半导体材料设备主题指数（931743） | 最多 40 只；材料、制造设备、封测设备 | **未采集：缺少公司清单** | 单个公司收入、客户、国产替代份额、订单与利润率 |
| 光模块/通信比较组 | 中证光通信主题指数（931723） | 50 只；光模块及元器件、光纤光缆、数据中心、运营商 | **未采集：缺少公司清单** | 光模块与 PCB 的利润池、成本转嫁或个股盈利比较 |
| 创新药海外 BD 观察组 | 上证科创板创新药指数（950161） | 最多 30 只；创新药研发及药物研发/开发/生产服务 | **未采集：缺少公司清单和逐笔 BD 交易清单** | 首付款/里程碑/特许权使用费、会计确认时点及 EPS 转换 |
| 电力/电力设备 | 中证全指电力设备指数（931932） | 273 只（2026-06-30 factsheet） | **未采集：缺少公司清单** | 订单到收入转化、毛利率、现金回款及电网/新能源需求传导 |
| PCB 比较组 | 本次仅有主题要求，无官方 PCB 篮子或公司清单 | 未定义 | **未采集** | 任何 PCB 财务、价格、稼动率或盈利结论 |

## 已冻结的主题边界来源

| Source ID | 文件 | 发布者/日期 | 原始 URL | 质量 | 可用证据与限制 |
|---|---|---|---|---|---|
| FIN-01 | `sources/official-policy-20260726/202312-CSI-931743-semiconductor-material-equipment-methodology.pdf` | 中证指数有限公司；2023-12，V1.1 | `https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/20231208180655-931743_Index_Methodology_cn.pdf` | 高（指数编制方一手文件） | 定义材料/设备候选空间和流动性筛选；不是公司财报或经营证据。SHA-256 `85f2ee4e976171e24f0405562cfdb139d69fcbede9fa4aa2c0064cd5d9ab1d7d`。 |
| FIN-02 | `sources/official-policy-20260726/202310-CSI-931723-optical-communication-methodology.pdf` | 中证指数有限公司；2023-10，V1.0 | `https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/931723_Index_Methodology_cn.pdf` | 高（指数编制方一手文件） | 定义光通信比较空间；指数还含数据中心及运营商，不能被等同为纯光模块。SHA-256 `6e3c1d3fc92c66a36f457ff3d8405c8427fe609c630d9aac2a95990d7389f5df`。 |
| FIN-03 | `sources/official-policy-20260726/202408-SSE-950161-star-innovative-drug-methodology.pdf` | 上交所/中证指数文件；2024-08，V1.0 | `https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/950161_Index_Methodology_cn.pdf` | 高（交易所指数方法论） | 定义科创板创新药观察空间；不识别海外 BD 对手方、支付条款或确认会计期间。SHA-256 `03f83198b76c9fe8605e732bb20d6c71153b3266a067c4948f320603c0b6fe32`。 |
| FIN-04 | `sources/official-policy-20260726/20260130-CSI-931932-power-equipment-factsheet.pdf` | 中证指数有限公司；factsheet 标注 2026-06-30 | `https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/indices/detail/files/zh_CN/931932factsheet.pdf` | 高（指数编制方一手文件） | 记录 931932 的行业口径、273 个样本和截至 2026-06-30 的静态指标；不是 2026-07-24 收盘数据，也不是公司财务表。SHA-256 `264dd92795b04b7f5f8b2a4244863abc5e7bfbe4bf67ed0941ebcbe671d0fa0d`。 |

## 数据质量、缺口与后续最低动作

- **公司级财务完整度：0/未定义。** 这不是零业绩或零覆盖，而是尚未批准任何覆盖代码。
- **不能用本文件做的事：** 估值、盈利预测、行业收入汇总、订单转收入、BD 收益归属，或“设备/材料优于光模块/PCB”的财务判断。
- **进入验证阶段前必须补齐：** 每个模块至少提供证券代码、交易所、纳入理由和报告期；创新药模块还需逐笔 BD 公告 URL/日期/对手方；随后仅从巨潮、交易所或公司 IR 的原始公告提取公司财务。
- **时间风险：** 2026H1 公告并非所有公司在 2026-07-26 前均已披露；即使后续给出代码，缺失项目也必须写作“未披露”，不能以前期或卖方估计替代。
