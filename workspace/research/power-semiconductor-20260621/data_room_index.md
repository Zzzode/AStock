# Power Semiconductor Data Room Index

This index maps every collected evidence artifact to its role in the research report. Paths are relative to the project root unless otherwise noted.

## Official filings & financial data

| File | Exists | Purpose |
|---|---|---|
| `sources/official-company/` | True | 官方财报归档目录：10 家 A 股功率半导体公司，每家含 2025 年报（PDF+MD+元数据）、2026Q1 季报（PDF+MD+元数据）、16 期财务数据 JSON |
| `data/official_filing_archive_summary.md` | True | 官方财报档案汇总：10 家公司年报/季报元数据总表、文件大小、页数统计 |
| `data/official_financials_summary.md` | True | 核心财务指标汇总：10 家公司营收/净利/毛利率/ROE 等关键指标 3 年+1 季度总览 |
| `data/financial_detail_data.json` | True | 财务明细数据 v1（机器可读）：结构化财务指标数据 |
| `data/financial_detail_data_v2.json` | True | 财务明细数据 v2（机器可读）：扩展版结构化财务指标 |
| `data/filing_collection_results.json` | True | 财报收集结果元数据（机器可读）：收集状态、来源、时间戳 |
| `data/raw_financials.md` | True | 原始财务数据：10 家 A 股功率半导体公司 |
| `data/verified_financials.md` | True | 经验证财务数据，含官方来源交叉校验 |
| `data/raw_market_data.md` | True | 原始市场数据：价格、估值、同业比较 |
| `data/verified_market_data.md` | True | 经验证市场数据，含一致性检查 |

## Broker reports & consensus

| File | Exists | Purpose |
|---|---|---|
| `sources/broker-reports/2026-06-21/` | True | 卖方研报归档目录：17 篇研报（6 篇行业+11 篇公司），每篇含 PDF+摘要 MD |
| `data/full_report_archive_summary.md` | True | 卖方研报归档汇总：17 篇研报完整目录，含券商、分析师、页数、类型 |
| `data/report_catalog.md` | True | 研报精选目录：12 篇核心研报摘要索引 |
| `data/broker_target_price_history.md` | True | 机构目标价历史：8 家公司 2025Q1~2026Q2 目标价时间序列、评级、估值方法 |
| `data/consensus_analysis.md` | True | 一致预期分析：评级、目标价、盈利预测的市场共识 |

## Source governance

| File | Exists | Purpose |
|---|---|---|
| `data/source_registry.md` | True | 源注册登记表：L1-L6 六级可信度分层，注册来源清单 |
| `data/source_registry.json` | True | 机器可读源注册表 |
| `data/claim_audit.md` | True | 主张审计：所有核心主张的证据强度核查 |
| `source_exhaustion_log.md` | True | 数据源穷尽日志：9 大类、15+ 探针记录，说明数据缺口成因 |
| `source_exhaustion_log.json` | True | 机器可读源穷尽日志 |
| `data/unresolved_requirements.md` | True | 未解决需求清单：12 项未满足研究需求，标注阻碍类型与替代方案 |
| `data/unresolved_requirements.json` | True | 机器可读未解决需求清单 |

## Analysis outputs

| File | Exists | Purpose |
|---|---|---|
| `analysis/industry_landscape.md` | True | 行业格局：市场规模、价值链、竞争动态 |
| `analysis/house_view.md` | True | AStock 独立观点：自主判断 vs 市场共识 |
| `analysis/valuation_model.md` | True | 估值模型：PE/PS/PEG/EV-EBITDA 多方法 |
| `analysis/risk_framework.md` | True | 风险框架：9 大风险类别、情景分析、监控指标 |
| `analysis/supply_chain_matrix.md` | True | 供应链关系矩阵：上游材料设备→中游制造→下游应用全链路图谱，可信度分级 |
| `analysis/technology_architecture.md` | True | 技术架构分析：硅基/SiC/GaN 底层原理、工艺难点、封装演进、路线图 |
| `analysis/policy_geopolitical_analysis.md` | True | 政策地缘分析：大基金三期、出口管制、贸易壁垒、新能源政策联动、情景分析 |
| `analysis/secondary_market_analysis.md` | True | 二级市场分析：板块表现、资金流向、情绪指标、风格特征 |
| `data/earnings_expectations_vs_delivery.md` | True | 财务预期兑现分析：9 家公司 4 季度一致预期 vs 实际业绩的 Beat/Miss 追踪 |

## IR materials

| File | Exists | Purpose |
|---|---|---|
| `sources/ir-materials/` | True | IR 材料归档目录：7 家公司投资者关系活动记录，含电话会议、调研、业绩说明会 |
| `data/ir_materials_summary.md` | True | IR 材料汇总：7 家公司调研活动统计、参与机构数、核心信息要点 |
| `data/ir_guidance_summary.md` | True | 业绩指引汇总：管理层公开展望，含营收/毛利率/产能/客户等指引信息 |
| `sources/ir-materials/survey_summary.json` | True | 调研数据汇总（机器可读）：结构化机构调研统计 |

## Probes & failed sources

| File | Exists | Purpose |
|---|---|---|
| `sources/probe-failed/` | True | 探针失败记录目录：12 份失败探针档案，含渠道数据、国际券商、付费数据三大类 |
| `data/channel_data_probe.md` | True | 渠道数据探针：价格指数、库存、进出口、出货数据获取尝试记录 |
| `data/global_broker_access_probe.md` | True | 国际投行研报探针：高盛/大摩/小摩/瑞银等 7 家国际机构获取状态 |
| `data/paid_data_access_audit.md` | True | 付费数据访问审计：Wind/Choice/iFinD/Tushare/Bloomberg 等平台覆盖评估 |
| `sources/probe-failed/channel_huaqiangbei_index.md` | True | 华强北价格指数探针：SKU 级价格数据不可得原因记录 |
| `sources/probe-failed/channel_ic_insights.md` | True | IC Insights/WSTS 数据探针：细分市场数据付费门槛记录 |
| `sources/probe-failed/channel_inventory_data.md` | True | 渠道库存数据探针：权威库存天数数据缺失原因 |
| `sources/probe-failed/customer_revenue_split.md` | True | 客户收入拆分探针：平台级收入拆分不可得原因 |
| `sources/probe-failed/customs_trade_data.md` | True | 海关贸易数据探针：细分品类进出口数据获取限制 |
| `sources/probe-failed/global_broker_goldman.md` | True | 高盛研报探针失败记录 |
| `sources/probe-failed/global_broker_jp_morgan.md` | True | 摩根大通研报探针失败记录 |
| `sources/probe-failed/global_broker_morgan_stanley.md` | True | 摩根士丹利研报探针失败记录 |
| `sources/probe-failed/global_broker_ubs.md` | True | 瑞银研报探针失败记录 |
| `sources/probe-failed/paid_bloomberg_terminal.md` | True | Bloomberg 终端探针失败记录 |
| `sources/probe-failed/paid_tushare_ifind.md` | True | Tushare/iFinD 探针失败记录 |
| `sources/probe-failed/paid_wind_terminal.md` | True | Wind 终端探针失败记录 |

## Report output

| File | Exists | Purpose |
|---|---|---|
| `research_brief.md` | True | 研究简报：范围、问题、方法论 |
| `main.tex` | True | LaTeX 主文件 |
| `sections/` | True | 章节源文件（11+ 节） |
| `main.pdf` | True | 编译完成 PDF 报告（48 页） |
| `rendered/` | True | 渲染图片 / 图表目录（约 33 张页面渲染图） |
| `analysis/exhibit_plan.md` | True | 图表规划：10 章 ~58 个图表的完整规划清单，含已有/建议补充 |
| `analysis/template_brief.md` | True | 模板对标分析：对标高盛/中金/中信等顶级研报模板的结构对标 |
| `analysis/visual_review.md` | True | 视觉版式审核：PDF 格式、排版、可读性质量评估报告 |

## Governance & audit

| File | Exists | Purpose |
|---|---|---|
| `completion_audit_manifest.md` | True | 完成度审计清单 |
| `completion_audit_manifest.json` | True | 机器可读完成度审计清单 |
| `data_room_index.md` | True | 本文件——资料室索引 |
| `review_log.md` | True | 评审日志：质量评估记录 |
| `analysis/valuation_audit.md` | True | 估值审计：PE/PB/市值等估值数据的数学校验与一致性检查 |

## Tools & utilities

| File | Exists | Purpose |
|---|---|---|
| `tools/` | True | 工具与脚本目录 |
| `tools/verify_research_workspace.py` | True | 研究工作区验证脚本 |

## Ticker universe coverage matrix

| Ticker | Name | Official filings | Financial data | Market data | IR materials | Broker coverage | Target price history | Earnings beat/miss | Source depth |
|---|---|---|---|---|---|---|---|---|---|
| 688187 | 时代电气 | ✅ Full | ✅ Full | ✅ Full | ✅ Rich (3 events, ~60机构) | ✅ High (industry+company) | ✅ Yes | ✅ Yes | Deep |
| 603290 | 斯达半导 | ✅ Full | ✅ Full | ✅ Full | ⚠️ Limited (公告仅) | ✅ Medium (industry coverage) | ✅ Yes | ✅ Yes | Deep |
| 688396 | 华润微 | ✅ Full | ✅ Full | ✅ Full | ✅ Rich (7 events, 284机构次) | ✅ High (2 company reports) | ✅ Yes | ✅ Yes | Good |
| 600460 | 士兰微 | ✅ Full | ✅ Full | ✅ Full | ✅ Moderate (1 event) | ✅ High (3 company reports) | ✅ Yes | ✅ Yes | Good |
| 300373 | 扬杰科技 | ✅ Full | ✅ Full | ✅ Full | ✅ Rich (6 events, 326机构次) | ✅ High (3 company reports) | ✅ Yes | ✅ Yes | Deep |
| 600703 | 三安光电 | ✅ Full | ✅ Full | ✅ Full | ❌ None | ✅ Medium (industry coverage) | ✅ Yes | ✅ Yes | Good |
| 688234 | 天岳先进 | ✅ Full | ✅ Full | ✅ Full | ✅ Moderate (4 events, 141机构次) | ✅ High (2 company reports) | ✅ Yes | ✅ Yes | Good |
| 605111 | 新洁能 | ✅ Full | ✅ Full | ✅ Full | ⚠️ Limited (公告仅) | ✅ Medium (industry coverage) | ✅ Yes | ✅ Yes | Good |
| 688261 | 东微半导 | ✅ Full | ✅ Full | ✅ Full | ❌ None | ⚠️ Limited | ❌ No | ✅ Yes | Moderate |
| 688368 | 晶丰明源 | ✅ Full | ✅ Full | ✅ Full | ❌ None | ⚠️ Limited | ❌ No | ✅ Yes | Moderate |

### Global peers

| Ticker | Name | Market data | Coverage |
|---|---|---|---|
| IFNNY | 英飞凌 | ✅ | Good |
| ON | 安森美 | ✅ | Good |
| STM | 意法半导体 | ✅ | Good |
| WOLF | Wolfspeed | ✅ | Good |
| NVTS | Navitas | ✅ | Moderate |
| TXN | TI | ✅ | Good |
| MPWR | MPS | ✅ | Moderate |

### Coverage legend

- **Official filings**: 2025 年报 + 2026Q1 季报 + 16 期财务序列
- **IR materials**: Rich (3+ 次含问答的调研) / Moderate (1-2 次) / Limited (公告类) / None
- **Broker coverage**: High (2+ 篇公司研报 + 行业覆盖) / Medium (行业覆盖 + 点评) / Limited
- **Source depth**: Deep (多维度数据交叉验证) / Good / Moderate
