# AI 存储产业链深度研报 — 图表规划（Exhibit Plan）

> 规划日期：2026-06-23
> 研报结构：11 章 + 附录
> 规划原则：每个强结论对应一张图/表；一图一核心论点；优先使用 mermaid 架构图；考虑 PDF A4 单栏版式可读性
> 可视化目标：**图 ≥ 13 张** + **表 ≥ 10 张**（合计 ≥ 23 张核心展示）

---

## 一、图表总览

| 章节 | 图 | 表 | 合计 | 核心 mermaid |
|------|----|----|------|-------------|
| 第 1 章 投资委员会概要 | 1（资金流逻辑图） | 2（组合总表 + 核心数据速览） | 3 | 图 1-2 资金流逻辑图 |
| 第 2 章 执行摘要与 House View | 1（四主线共振框架图） | 1（共识 vs 分歧表） | 2 | |
| 第 3 章 全球存储产业链图谱 | 1（产业链全景架构图） | 1（环节价值量/毛利对标表） | 2 | 图 3-1 产业链架构图 |
| 第 4 章 AI 需求拆解 | 4（HBM 路线图 / CXL 拓扑 / TAM 堆叠柱 / 需求结构饼） | 2（HBM TAM 预测表 / DDR5+SSD+CXL TAM 表） | 6 | 图 4-1 HBM 路线图 / 图 4-2 CXL 拓扑 |
| 第 5 章 供需-价格周期与原厂 capex | 3（capex 堆叠柱 / 供需缺口桥 / 合约价折线） | 2（原厂 capex 表 / 季度供需缺口与合约价表） | 5 | 图 5-2 供需缺口桥 |
| 第 6 章 全球竞争格局与国产替代 | 1（三大原厂 HBM 份额饼） | 1（国产替代进度总表） | 2 | |
| 第 7 章 A 股映射标的深度 | 2（A 股市值分布 / AI 弹性 vs 估值散点） | 1（23 只标的多维总表） | 3 | |
| 第 8 章 估值模型与国际可比 | 2（核心 4 只 PE Band / 国际可比估值散点） | 2（国际可比估值表 / 核心标的三表预测与估值权重表） | 4 | |
| 第 9 章 卖方共识与 AStock 分歧 | 0 | 1（卖方共识矩阵） | 1 | |
| 第 10 章 风险矩阵与压力测试 | 1（风险矩阵热力图） | 1（压力测试情景表） | 2 | |
| 第 11 章 投资建议与组合构建 | 1（催化剂时间线 / 组合哑铃结构示意） | 1（核心组合触发条件表） | 2 | |
| Appendix | 0 | ≥ 4（来源注册表 / 估值审计表 / 数据验证摘要 / 详细财务表） | ≥ 4 | |
| **合计（正文）** | **13 图** | **15 表** | **28** | |
| **合计（含附录）** | **13 图** | **19 表** | **32** | |

> **mermaid 架构图清单（5 张必做）**：
> 1. 图 3-1 全球存储产业链全景图谱
> 2. 图 4-1 HBM 代际路线图（含容量/带宽/良率/单价四维度）
> 3. 图 4-2 CXL 内存池化拓扑图（服务器→交换机→内存池三层）
> 4. 图 5-2 DRAM/NAND 供需缺口桥接图（供给增量 vs 各端需求分解）
> 5. 图 1-2 资金流逻辑图（AI capex → 原厂 → 设备/材料 → A 股映射）

---

## 二、分章节详细规划

### 第 1 章 投资委员会概要

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 表 1-1 | 推荐组合与评级一览 / Recommended Portfolio & Ratings | 表格（三线表） | P0 | 待制作 | 核心 9 只 + 卫星 7 只的权重、评级、目标价区间、上/下行触发 | `valuation_model.md` + `house_view.md` + `verified_financials.md` | 章节开头"投资行动"节 | Phase 3 Valuation Modeler → Phase 4 LaTeX Writer |
| 表 1-2 | 核心数据速览 / Key Data Dashboard | 表格（紧凑信息板） | P0 | 待制作 | 板块估值分位、供需缺口、HBM TAM CAGR、国产替代率等 6-8 个关键数字一眼可见 | `industry_landscape.md` + `valuation_model.md` + `consensus_analysis.md` | "关键数据"节（表 1-1 之后） | Phase 3 House View Analyst → LaTeX Writer |
| **图 1-1** | **四大投资主线共振图 / Four-Thesis Convergence Framework** | **架构示意图 / mermaid flowchart** | P0 | 待制作 | **HBM 扩容 + DDR5 渗透 + CXL 商业化 + 国产替代**四主线共振，2026H2-2027 迎来量价齐升+格局重塑双击 | `house_view.md` 核心判断 | "投资论题"节，全报告视觉锚点 | Phase 2.5 House View Analyst → Exhibit Architect（本规划） → LaTeX Writer（mermaid） |
| **图 1-2** | **资金传导逻辑图 / Capital Flow Logic Map** | **mermaid flowchart（必须做）** | P0 | 待制作 | **AI 资本开支 → 三大原厂 capex → 设备/材料/封测环节 → A 股映射标的收入利润端**的因果链条可视化，向 IC 成员展示"钱从哪里来、价值在哪段落、A 股怎么兑现" | `industry_landscape.md`（capex 章节） + `supply_chain_matrix.md`（关系矩阵） | "投资逻辑传导"节，位于表 1-2 之后 | Phase 1 Industry Analyst → Exhibit Architect → LaTeX Writer（mermaid） |

**补充说明**：
- 图 1-1 和图 1-2 是 IC 成员"30 秒理解全报告"的关键视觉锚，必须在正文第一页露出。
- 图 1-2 为用户指定 5 张 mermaid 之一：左 Hyperscaler capex → 中 原厂 capex（DRAM/NAND/HBM）+ 代工厂先进封装 → 右 A 股各环节弹性（箭头线粗细对应价值传导系数）。

---

### 第 2 章 执行摘要与核心观点

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 表 2-1 | 市场共识 vs AStock 独立观点 / Consensus vs AStock House View | 对比表格（双栏） | P0 | 待制作 | 1) HBM 受益范围被高估（仅 SK 海力士实质受益）；2) 国产 HBM 节奏被提前 2 年；3) 设备/材料是更确定的二阶 beta | `house_view.md`（共识分歧节） + `claim_audit.md`（高影响声明分类） | 章节第二部分"与共识的差异" | Phase 2.5 House View Analyst → LaTeX Writer |
| 表 2-2 | 核心声明可信度分级 / High-Impact Claim Confidence Ranking | 表格（声明 × 证据等级 × 来源引用数） | P1 | 待制作 | 向读者透明披露哪些结论是 L1/L2 证据支撑、哪些是 L3/L4 推断 | `claim_audit.md` + `source_registry.md` | 章节末尾"证据透明度"节 | Phase 1 Source Governance Analyst → LaTeX Writer |

---

### 第 3 章 全球存储产业链图谱

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| **图 3-1** | **全球存储产业链全景图谱 / Global Memory Supply-Chain Architecture** | **mermaid graph TD（必须做）** | P0 | 待制作 | **上游设备材料 → 设计 → 晶圆制造 → 封测（含先进封装 CoWoS/TSV）→ 模组/主控 → 整机/云厂商**的七层架构，每层标注全球龙头与 A 股映射、各环节价值占比 | `industry_landscape.md`（产业链结构） + `supply_chain_matrix.md`（供需关系矩阵） | 章节开头，全章核心视觉 | Phase 1 Industry Analyst → Exhibit Architect → LaTeX Writer（mermaid） |
| 表 3-1 | 产业链各环节价值量 / 毛利率 / A 股对标 / 国产化率四维总表 / Segment Value & Margin & A-Share Peer Matrix | 表格 | P0 | 待制作 | 封测（CoWoS）和设备是附加值最高的环节；A 股在设备材料环节国产化率最低、弹性最大 | `industry_landscape.md` + `technology_architecture.md` + `verified_financials.md` | "环节价值分布"节，图 3-1 之后 | Phase 1 Industry Analyst → LaTeX Writer |
| 表 3-2 | 供应链关系矩阵（客户-供应商-收入敞口-可信度）/ Supply-Chain Relationship Matrix（Confidence-labeled） | 宽表格（tabularx） | P1 | 待制作 | 区分 confirmed / broker-stated / inferred / rumor 四级关系，不夸大 A 股与 HBM 的直接关联 | `supply_chain_matrix.md`（强制要求） + `customer_chain_bridge.md` | 正文放精简版，**完整版置 Appendix B** | Phase 1 Industry Analyst → LaTeX Writer（Appendix 长表用 longtable） |

---

### 第 4 章 AI 需求拆解

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| **图 4-1** | **HBM 代际路线图 / HBM Generation Roadmap（HBM2E→HBM3→HBM3E→HBM4→HBM4E）** | **mermaid timeline / gantt（必须做）** | P0 | 待制作 | 每代标注：容量（GB/栈）、带宽（GB/s）、良率区间、ASP（$/GB）、量产年、主导厂商；直观展示 HBM4 真正放量在 2027+ | `industry_landscape.md`（技术路线节） + `technology_architecture.md` | HBM 需求小节开头 | Phase 1 Industry Analyst → Exhibit Architect → LaTeX Writer（mermaid gantt） |
| **图 4-2** | **CXL 内存池化拓扑架构图 / CXL Memory Pooling Topology** | **mermaid flowchart（必须做）** | P0 | 待制作 | 从 Host CPU/GPU → CXL 交换机 → CXL 内存池（DRAM Box / Expansion / Tiering）三层拓扑；标注 A 股在主控（澜起）、模组（江波龙）、接口 IP 的卡位 | `industry_landscape.md`（CXL 章节） + `technology_architecture.md` | CXL 需求小节开头 | Phase 1 Industry Analyst → Exhibit Architect → LaTeX Writer（mermaid） |
| 图 4-3 | AI 存储 TAM 堆叠柱状图 2024-2027E / AI Memory TAM Stacked Bar（HBM vs DDR5 vs Enterprise SSD vs CXL） | 堆叠柱状图（金额，单位十亿美元） | P0 | 待制作 | HBM 是增速最快但绝对金额仍小于企业级 SSD 的细分；CXL 从 2026 起爆发 | `industry_landscape.md`（TAM 节） + 卖方 TAM 预测（L3） | TAM 总论节 | Phase 1 Industry Analyst → LaTeX Writer（pgfplots 或导入 PNG） |
| 图 4-4 | AI 存储需求结构饼图（按价值量，2026E） / AI Memory Demand Value Breakdown 2026E | 环形图 | P0 | 待制作 | HBM 占 AI 存储总价值 ~28-32%，DDR5 服务器级 ~35%，企业级 NVMe SSD ~25%，CXL ~5-8% | TAM 测算底稿（`data/` 下 TAM 明细表） | TAM 总论节，图 4-3 之后 | Phase 1 Industry Analyst → LaTeX Writer |
| 表 4-1 | HBM TAM 预测详表（代际 × 容量 × ASP × 出货量 × 金额，2024-2027E） / HBM TAM Forecast Detail | 表格（多行 × 多列，建议用 tabularx） | P0 | 待制作 | 2027E HBM TAM 达到 ~550-650 亿美元，CAGR ~70%；HBM3E 是 2026 主力，HBM4 2027 接棒 | `consensus_analysis.md`（各卖方 TAM 预测汇总） + `industry_landscape.md` | HBM 小节，图 4-1 之后 | Phase 2 Report Analyzer → LaTeX Writer |
| 表 4-2 | DDR5 / 企业级 NVMe SSD / CXL TAM 预测汇总表 / DDR5 & SSD & CXL TAM Summary | 表格 | P0 | 待制作 | DDR5 渗透从 2025 ~40% → 2027 ~75%；企业级 SSD 受益 CXL 分层；CXL 商业化元年在 2026H2 | `industry_landscape.md` + `consensus_analysis.md` | DDR5 / SSD / CXL 各小节末尾 | Phase 1 Industry Analyst → LaTeX Writer |

---

### 第 5 章 供需-价格周期与原厂 capex

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 图 5-1 | 原厂 capex 堆叠柱状图 2023-2027E / Memory Vendor Capex Stacked Bar（三星/SK 海力士/美光/铠侠/西数/长鑫/长江存储） | 堆叠柱状图（单位十亿美元，分 DRAM/NAND/HBM） | P0 | 待制作 | SK 海力士 capex 向 HBM 倾斜幅度最大；长鑫/长江存储 capex 绝对值虽小但增速最快 | `industry_landscape.md`（capex 节） + L1 财报（capex 分拆） + L3 卖方 capex 指引 | capex 总论节开头 | Phase 1 Industry Analyst → LaTeX Writer |
| **图 5-2** | **DRAM / NAND 供需缺口桥接图 / Supply-Demand Gap Bridge** | **mermaid 桥接图（must do）或 sankey** | P0 | 待制作 | **左侧供给增量**（原厂 wafer out × 良率提升 × bit growth）→ 中间供需平衡 → **右侧需求分解**（AI/服务器 / PC / 手机 / 汽车 / 其他），用桥接柱展示 2024Q1-2026Q4 分季度缺口 | `industry_landscape.md`（供需节） + L5 TrendForce/WSTS 供需数据 | 供需缺口节开头，全章核心 | Phase 1 Industry Analyst → Exhibit Architect → LaTeX Writer（mermaid 或 tikz） |
| 图 5-3 | DRAM / NAND 合约价走势图 2023Q1-2026Q4E / DRAM & NAND Contract Price Trend | 双折线图（分 DRAM DDR5 / NAND TLC），含历史 + 预测区间 | P0 | 待制作 | 2026H2 随 AI 拉动和原厂减产 discipline，DRAM 合约价进入上行通道；NAND 温和上涨 | L5 TrendForce / WSTS 历史合约价 + `industry_landscape.md`（价格预测节） | 价格周期节开头 | Phase 1 Industry Analyst → LaTeX Writer |
| 表 5-1 | 原厂 capex 指引、产能（wafer out）、产品结构、HBM 占比四维总表 / Vendor Capex & Capacity Matrix | 表格（7 家原厂 × 6 个指标） | P0 | 待制作 | 2026 年三大原厂 capex 合计超 1200 亿美元，其中 HBM 相关占比从 2024 年 ~18% → 2026E ~30% | `verified_financials.md`（海外可比 capex） + `industry_landscape.md` | capex 节，图 5-1 之后 | Phase 2 Data Verifier（financials） → LaTeX Writer |
| 表 5-2 | 分季度 DRAM/NAND 供需缺口与合约价预测（2024Q1-2026Q4） / Quarterly Supply-Demand Gap & Contract Price Forecast | 宽表格（tabularx，12 季 × 6 列） | P0 | 待制作 | 2026Q3 起 DRAM 缺口扩大至 -8~-12%，合约价 QoQ +8~+12% | L5 数据 + `industry_landscape.md` 测算底稿 | 供需节和价格节底部 | Phase 1 Industry Analyst → LaTeX Writer |

---

### 第 6 章 全球竞争格局与国产替代

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 图 6-1 | 三大原厂 HBM 产能份额饼图（2025E / 2026E / 2027E，三饼并列） / HBM Capacity Share: SK Hynix / Samsung / Micron | 环形饼图 × 3（并列比较） | P0 | 待制作 | SK 海力士维持 HBM 绝对龙头（2026E ~55-60% 份额），美光追赶，三星份额下滑 | `industry_landscape.md`（HBM 竞争格局） + L3 卖方深度 | HBM 格局节开头 | Phase 1 Industry Analyst → LaTeX Writer |
| 图 6-2 | 国产替代阶梯图（从 NOR → DRAM → NAND → HBM，横轴量产时间，纵轴技术难度） / Domestic Substitution Ladder | mermaid 阶梯图或柱 + 点线 | P1 | 待制作 | NOR（兆易）已突破 → DRAM（长鑫 17nm 量产 2024）→ NAND（长江 232L 2024）→ HBM（国产最早 2028+）；市场将国产 HBM 节奏提前了至少 2 年 | `house_view.md`（分歧点 2） + `technology_architecture.md` | 国产替代节开头 | Phase 2.5 House View Analyst → LaTeX Writer |
| 表 6-1 | 国产替代进度总表（长江存储 / 长鑫存储 / 兆易创新 / 北京君正 × 制程 / 产能 / 良率 / 受管制度 / 目标客户） / Domestic Substitution Progress Matrix | 表格 | P0 | 待制作 | 国产替代在 NOR/SRAM 已有竞争力，DRAM/NAND 在消费级可用、企业级认证中，HBM 仍是大片空白 | `technology_architecture.md` + `supply_chain_matrix.md` + 出口管制条款（L1/L4） | 国产替代节核心 | Phase 1 Industry Analyst → LaTeX Writer |

---

### 第 7 章 A 股映射标的深度

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 图 7-1 | A 股存储链市值分布（按环节分类，瀑布或横向条形） / A-Share Memory Chain Market-Cap Distribution by Segment | 横向条形图（23 只标的，颜色编码按产业链环节） | P0 | 待制作 | 设备（北方华创 / 中微）市值最大，封测其次，设计/模组偏小；A 股存储链缺少真正的存储原厂（长鑫/长江未上市） | `verified_market_data.md`（最新市值） + `industry_landscape.md`（环节分类） | 章节开头总览 | Phase 2 Data Verifier（market） → LaTeX Writer |
| 图 7-2 | AI 敞口 vs 当前估值散点图（X=AI 收入敞口%，Y=2026E PE，气泡=市值） / AI Exposure vs 2026E PE Scatter | 散点图 + 四象限（高-低敞口 × 高-低 PE） | P0 | 待制作 | 识别"高 AI 敞口 + PE 合理"的黄金象限（澜起等）和"低敞口 + 高 PE"的需规避区域 | `valuation_model.md` + `supply_chain_matrix.md`（AI 敞口估算） | 标的筛选节，各公司深度之前 | Phase 3 Valuation Modeler → LaTeX Writer |
| 表 7-1 | 23 只标的多维总表（代码 / 名称 / 环节 / AI 敞口 / 2025 营收 / 净利 / 毛利率 / 2026E PE / 卖方目标价 / 评级 / 触发条件） / 23-Name Multi-Dimension Matrix | 宽表格（`footnotesize` + tabularx，正文放精简 16 列版，**完整版置 Appendix C**） | P0 | 待制作 | 一张表看懂所有标的的核心基本面与估值定位 | `verified_financials.md` + `valuation_model.md` + `consensus_analysis.md`（卖方目标价） | 章节开头（精简版） | Phase 3 Valuation Modeler（聚合数据） → LaTeX Writer |

**补充说明**：各公司 2 页深度配"业务结构 + 财务数据"小表（约 23 × 2 = 46 个小表），归入 Appendix D 财务明细，正文只保留文字 + 关键 KPI。

---

### 第 8 章 估值模型与国际可比

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 图 8-1 | 核心 4 只 PE Band（澜起 / 兆易 / 北方华创 / 长电科技，近 3 年 PE 区间 + 当前位置） / PE Band for Top-4 Core Names | 折线图（每公司独立子图，含 ±1σ 通道） | P0 | 待制作 | 核心 4 只当前 PE 处于近 3 年 40-60% 分位，澜起估值已部分反映 CXL 预期，兆易仍处中低位 | `valuation_model.md`（历史估值节） + `long_horizon_valuation_history.json`（如有） | 章节开头"估值位置"节 | Phase 3 Valuation Modeler → LaTeX Writer |
| 图 8-2 | 国际可比估值散点（X=2026E 净利增速，Y=2026E PE，气泡=市值，分组：海外原厂 / 海外设备 / A 股核心） / Global Peer Valuation Scatter: PE vs Growth | 散点图 + 分组着色 + PEG=1 参考线 | P0 | 待制作 | A 股设备标的 PE 较海外设备溢价 ~2x，但增速也 ~2x；A 股设计/封测 PE 接近海外可比 + 国产替代溢价合理 | `valuation_model.md`（全球对比节） + `verified_financials.md`（海外可比） | 国际可比节核心 | Phase 3 Valuation Modeler → LaTeX Writer |
| 表 8-1 | 国际可比估值详表（海外 10 家 + A 股 9 家 × PE / PS / EV/EBITDA / PEG / 增速 / 市值） / Global Peer Valuation Table | 表格 | P0 | 待制作 | 海外原厂 PE 15-25x，A 股映射 PE 30-60x，溢价主因国产替代增速差 | `valuation_model.md`（全球对比节） | 国际可比节，图 8-2 之后 | Phase 3 Valuation Modeler → LaTeX Writer |
| 表 8-2 | 核心标的三表预测 + 估值方法权重 + 合理价值区间 / Core Names Forecast & Valuation Weight & Fair Value Range | 表格（每公司：营收/净利/EPS 三年预测 + PE/PS/EV-EBITDA 加权合理价） | P0 | 待制作 | **不发明目标价**，用卖方目标价区间 + 本模型加权区间，标注所有输入来源 | `valuation_model.md`（估值权重节） + `consensus_analysis.md`（卖方预测） + `valuation_audit.md`（校验后数字） | 章节核心，紧接 PE Band | Phase 3 Valuation Modeler → Phase 3 Valuation Auditor 校验 → LaTeX Writer |

---

### 第 9 章 卖方共识与 AStock 分歧

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 表 9-1 | 卖方共识矩阵（标的 × 券商 × 评级 × 目标价 × 核心逻辑 × 估值方法 × 报告日期） / Street Consensus Matrix | 宽表格（正文精简版，完整版 Appendix E），含评级色编码（买入/增持/中性/减持） | P0 | 待制作 | 作为独立观点的参照系，不是报告的声音；突出 AStock 与卖方在 **HBM 国产节奏 / 设备 capex 弹性 / 价格周期幅度** 三处分歧 | `consensus_analysis.md` + `broker_target_price_history.md`（如有） + `source_registry.md`（卖方来源编号） | 章节开头主表 | Phase 2 Report Analyzer → Phase 1 Source Governance Analyst（分级引用） → LaTeX Writer |
| 表 9-2 | 卖方目标价历史追踪（核心 6 只 × 近 6 次重要调升/调降） / Broker Target-Price History for Core 6 | 时间序列表格 | P1 | 待制作 | 卖方调升多集中在 2026Q1 AI capex 超预期后；追踪一致性预期变动方向 | `broker_target_price_history.md`（如有） | 章节末尾"预期演进"节 | Phase 2 Report Analyzer → LaTeX Writer |

---

### 第 10 章 风险矩阵与压力测试

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 图 10-1 | 风险矩阵热力图（X=发生概率，Y=影响程度，9 大风险气泡按严重度着色） / Risk Matrix Heatmap | 散点图/矩阵热力图（4 象限 × 绿/黄/橙/红） | P0 | 待制作 | **HBM ASP 大幅下滑（供过于求）** 和 **出口管制升级（设备断供）** 是红色高风险；NAND 价格战是橙色 | `risk_framework.md`（核心风险矩阵节） | 章节开头核心视觉 | Phase 3 Risk Analyst → Exhibit Architect → LaTeX Writer |
| 表 10-1 | 压力测试情景表（基准 / 乐观 / 悲观 × HBM ASP -30% / NAND QoQ -10% / 设备管制升级 / 人民币升值 5%） / Stress-Test Scenario Table | 表格（情景 × 触发 × 板块 EPS 影响 × 核心标的净利影响 × 估值调整 × 操作建议） | P0 | 待制作 | 悲观情景下核心组合 EPS 可能下修 15-25%，但估值下杀空间有限（已处中低分位） | `risk_framework.md`（情景分析节） + `valuation_model.md`（敏感度参数） | 情景测试节，图 10-1 之后 | Phase 3 Risk Analyst → LaTeX Writer |
| 表 10-2 | 风险监控指标体系（领先/同步/滞后 × 指标 × 频率 × 数据源 × 阈值） / Risk Monitoring Indicator Framework | 表格 | P1 | 待制作 | 给读者一整套"盯什么、多久盯、什么数值算变天"的追踪工具 | `risk_framework.md`（监控指标节） | 章节末尾"监控指引" | Phase 3 Risk Analyst → LaTeX Writer |

---

### 第 11 章 投资建议与组合构建

| 编号 | 标题（中 / En） | 类型 | 优先级 | 状态 | 支持的核心结论 | 数据来源表 / 依赖文件 | 在章节中的位置 | 负责制作的环节 |
|------|----------------|------|--------|------|---------------|----------------------|---------------|---------------|
| 图 11-1 | 催化剂日历时间线（2026Q3-2027Q4，按季度标注事件 + 弹性方向） / Catalyst Calendar Timeline | mermaid gantt 或 横向时间轴 | P0 | 待制作 | 2026Q4 是催化剂密集期（原厂 Q3 财报 + HBM3E 大规模出货 + 长江存储新一代产品发布） | `house_view.md`（催化剂节） + `risk_framework.md` | 章节开头"时点判断"节 | Phase 2.5 House View Analyst → LaTeX Writer（mermaid） |
| 图 11-2 | 组合构建哑铃结构示意（核心 60-70% / 卫星 20-30% / 主题 ≦ 10%） / Barbell Portfolio Construction | mermaid 金字塔或哑铃结构示意图 | P1 | 待制作 | 核心底仓（设备 + 封测龙头）保障确定性；卫星（CXL/模组/IP）提供弹性；小仓位主题（材料/载板）捕捉事件驱动 | `house_view.md`（组合构建节） | "组合构建思路"节 | Phase 2.5 House View Analyst → LaTeX Writer |
| 表 11-1 | 核心组合触发条件与失效条件 / Core Portfolio Triggers & Invalidation Conditions | 表格（每只标的：买入触发 / 加仓触发 / 减仓触发 / 清仓触发 / 观察指标） | P0 | 待制作 | 给 IC 明确的操作纪律，不做"死多头"；如澜起 DDR5 RCD 市占率低于 30% 立即下修评级 | `house_view.md`（触发节） + `risk_framework.md`（失效条件） | 章节末尾"操作纪律"节 | Phase 2.5 House View Analyst → LaTeX Writer |

---

## 三、强结论 → 图表 映射表（Strong Conclusion Coverage）

> 原则：每个强结论至少对应 1 张主图 + 1 张主表。来源：`house_view.md` 核心判断 / `industry_landscape.md` 关键结论 / `valuation_model.md` 估值结论 / `risk_framework.md` 风险结论。

| # | 强结论（Strong Conclusion） | 覆盖图表 | 缺失？ |
|---|---------------------------|---------|--------|
| SC-1 | **HBM 扩容 + DDR5 渗透 + CXL 商业化 + 国产替代四主线共振，2026H2-2027 迎来"量价齐升+格局重塑"双击** | 图 1-1 四主线框架图 + 图 4-3 TAM 堆叠柱 + 图 5-3 合约价折线 + 表 5-2 季度供需预测 | ✅ |
| SC-2 | HBM 是 AI 存储增速最快的细分，2027E TAM ~600 亿美元，但国产 HBM 节奏被市场提前至少 2 年 | 图 4-1 HBM 路线图 + 表 4-1 HBM TAM 详表 + 图 6-2 国产替代阶梯 + 表 6-1 国产替代进度表 | ✅ |
| SC-3 | 资金传导路径清晰：Hyperscaler capex ↑ → 原厂 capex ↑ → 设备/材料/封测最受益 | 图 1-2 资金流逻辑图 + 图 5-1 capex 堆叠柱 + 表 5-1 原厂 capex 产能表 | ✅ |
| SC-4 | DRAM 合约价 2026H2 进入上行通道，Q3 起缺口扩大至 -8~-12% | 图 5-2 供需缺口桥 + 图 5-3 合约价折线 + 表 5-2 季度供需与价格表 | ✅ |
| SC-5 | CXL 商业化元年在 2026H2，澜起科技是 A 股第一受益标的（RCD/CKD/CXL 主控卡位） | 图 4-2 CXL 拓扑图 + 表 4-2 TAM 汇总表 + 图 7-2 AI 敞口散点 + 表 8-2 合理价值区间 | ✅ |
| SC-6 | A 股设备（北方华创/中微/拓荆）是更确定的二阶 beta，不论 HBM 谁赢都要扩产 | 图 3-1 产业链架构（设备层位置） + 图 7-1 A 股市值分布 + 表 3-1 环节价值毛利率表 | ✅ |
| SC-7 | SK 海力士 HBM 绝对龙头（2026E ~55-60%），三大原厂格局短期不变 | 图 6-1 HBM 份额三饼 + 表 5-1 原厂 capex 结构 | ✅ |
| SC-8 | A 股估值较海外溢价 2x 左右，但被国产替代增速差部分解释；核心 4 只处近 3 年中低分位 | 图 8-1 核心 4 只 PE Band + 图 8-2 全球可比散点 + 表 8-1 全球估值表 | ✅ |
| SC-9 | 高 AI 敞口 + PE 合理的"黄金象限"标的是配置首选 | 图 7-2 AI 敞口 vs PE 散点 + 表 7-1 23 只总表 + 表 11-1 触发条件表 | ✅ |
| SC-10 | **HBM ASP 大幅下滑** 和 **出口管制升级** 是两个红色高风险；悲观情景下核心组合 EPS 下修 15-25% | 图 10-1 风险矩阵 + 表 10-1 压力测试表 + 表 10-2 监控指标体系 | ✅ |

> **覆盖率检查**：10/10 强结论均有 ≥1 图 + ≥1 表支撑。无缺失。

---

## 四、优先级汇总

### P0 — 必做（核心结论可视化，未完成不得进入 LaTeX）

| 编号 | 图表 | 类型 | 章节 | 制作方式 |
|------|------|------|------|---------|
| 表 1-1 | 推荐组合与评级一览 | 表格 | Ch1 | LaTeX tabular |
| 表 1-2 | 核心数据速览 | 紧凑表格 | Ch1 | LaTeX tabular |
| 图 1-1 | 四大主线共振框架 | **mermaid** | Ch1 | LaTeX → mermaid → 导出 PDF 嵌入 |
| 图 1-2 | 资金传导逻辑图 | **mermaid** | Ch1 | LaTeX → mermaid → 导出 PDF 嵌入 |
| 表 2-1 | 共识 vs AStock 观点 | 对比表格 | Ch2 | LaTeX tabular |
| 图 3-1 | 全球存储产业链全景图谱 | **mermaid graph TD** | Ch3 | LaTeX → mermaid → 导出 PDF 嵌入 |
| 表 3-1 | 环节价值/毛利/对标/国产化率 | 表格 | Ch3 | LaTeX tabular |
| 图 4-1 | HBM 代际路线图 | **mermaid gantt** | Ch4 | LaTeX → mermaid → 导出 PDF 嵌入 |
| 图 4-2 | CXL 内存池化拓扑 | **mermaid flowchart** | Ch4 | LaTeX → mermaid → 导出 PDF 嵌入 |
| 图 4-3 | AI 存储 TAM 堆叠柱状图 | 柱状图 | Ch4 | pgfplots / Python matplotlib 导出 PNG |
| 图 4-4 | AI 存储需求结构饼图 | 环形图 | Ch4 | pgfplots |
| 表 4-1 | HBM TAM 预测详表 | 表格 | Ch4 | LaTeX tabular |
| 表 4-2 | DDR5+SSD+CXL TAM 表 | 表格 | Ch4 | LaTeX tabular |
| 图 5-1 | 原厂 capex 堆叠柱状 | 柱状图 | Ch5 | pgfplots |
| 图 5-2 | 供需缺口桥接图 | **mermaid / tikz** | Ch5 | mermaid bridge 或 sankey 导出 |
| 图 5-3 | DRAM/NAND 合约价折线 | 双折线 | Ch5 | pgfplots |
| 表 5-1 | 原厂 capex/产能表 | 表格 | Ch5 | LaTeX tabular |
| 表 5-2 | 季度供需-合约价预测表 | 宽表 | Ch5 | tabularx |
| 图 6-1 | HBM 产能份额三饼图 | 饼图 × 3 | Ch6 | pgfplots（minipage 并列） |
| 表 6-1 | 国产替代进度总表 | 表格 | Ch6 | LaTeX tabular |
| 图 7-1 | A 股市值分布 | 横向条形 | Ch7 | pgfplots |
| 图 7-2 | AI 敞口 vs 估值散点 | 散点图 | Ch7 | pgfplots |
| 表 7-1 | 23 只多维总表（精简） | 宽表 | Ch7 | `footnotesize` + tabularx |
| 图 8-1 | 核心 4 只 PE Band | 折线 × 4 subplot | Ch8 | pgfplots subfigure |
| 图 8-2 | 国际可比估值散点 | 散点图 | Ch8 | pgfplots |
| 表 8-1 | 国际可比估值表 | 表格 | Ch8 | LaTeX tabular |
| 表 8-2 | 核心标的预测+估值权重 | 表格 | Ch8 | LaTeX tabular |
| 表 9-1 | 卖方共识矩阵（精简） | 宽表 | Ch9 | tabularx + 评级颜色 |
| 图 10-1 | 风险矩阵热力图 | 矩阵散点 | Ch10 | pgfplots / tikz matrix |
| 表 10-1 | 压力测试情景表 | 表格 | Ch10 | LaTeX tabular |
| 图 11-1 | 催化剂时间线 | **mermaid gantt** | Ch11 | mermaid 导出 |
| 表 11-1 | 组合触发/失效条件 | 表格 | Ch11 | LaTeX tabular |

> **P0 小计：13 图 + 17 表 = 30 张核心展示。** 超过"≥12 图 + 10 表"要求。

### P1 — 重要补充（增强报告专业度，建议完成）

| 编号 | 图表 | 类型 | 章节 |
|------|------|------|------|
| 表 2-2 | 核心声明可信度分级 | 表格 | Ch2 |
| 表 3-2 | 供应链关系矩阵（精简版） | 宽表 | Ch3（完整版入附录） |
| 图 6-2 | 国产替代阶梯图 | mermaid 阶梯图 | Ch6 |
| 表 9-2 | 卖方目标价历史追踪 | 时间表 | Ch9 |
| 表 10-2 | 风险监控指标体系 | 表格 | Ch10 |
| 图 11-2 | 组合哑铃结构示意 | mermaid 示意图 | Ch11 |

### P2 — 可选增强（如有时间锦上添花）

| 编号 | 图表 | 类型 | 章节 |
|------|------|------|------|
| 图 4-5 | 分原厂 HBM 营收占比折线（2024Q1-2027Q4E） | 多折线 | Ch4 |
| 图 5-4 | 原厂库存天数 vs 合约价领先-滞后关系 | 双轴折线 | Ch5 |
| 图 7-3 | 核心 4 只北向持仓变化热力图 | 热力图 | Ch7 |
| 图 8-3 | 估值历史分位"温度计"色带 | 色带图 | Ch8 |

---

## 五、视觉设计规范

### 5.1 mermaid 架构图专项规范（5 张必做）

| 图号 | 图名 | 推荐 mermaid 类型 | 配色建议 | 备注 |
|------|------|------------------|---------|------|
| 图 1-2 | 资金流逻辑图 | `flowchart LR`（左→右，节点分三段） | 箭头粗细按价值量编码（粗=大额，细=小额），红箭头=AI 特有的增量路径 | 必须标注"HBM-only capex"这一关键分支 |
| 图 3-1 | 产业链全景 | `graph TD`（上→下，7 层节点） | 每层不同色系（设备=蓝，材料=青，设计=绿，制造=黄，封测=橙，模组=红，云=紫）；A 股标的用方框 + 边框加粗 | 每个节点标注"全球龙头 / A 股映射 / 价值占比%"三个字段 |
| 图 4-1 | HBM 代际路线 | `gantt` 或 `timeline` | 横轴年份，纵轴每代一行，柱上标注容量/带宽/ASP/良率/主导厂 5 个参数 | 给 2028+ 国产 HBM 虚线柱并标注"预测/AStock 评估"，突出与市场的分歧 |
| 图 4-2 | CXL 拓扑 | `flowchart TD`（顶层 GPU/CPU → 中间 CXL Switch → 底层 3 类 Memory Pool） | 节点图标建议（如用 `faMemory` 等 fontawesome）；A 股卡位的芯片（澜起 RCD/CXL ctrl、芯原 IP）用红色高亮节点 | 标注每段带宽（PCIe 5.0 → CXL 3.0） |
| 图 5-2 | 供需缺口桥 | `sankey` 或自定义 `flowchart` 桥结构 | 左边流入=供给增量（蓝系），中间平衡柱，右边流出=需求端分解（暖色系）；缺口=右-左，正=供过于求绿，负=供不应求红 | 分季度 × 4 组并列，或年度 × 3 组 |

### 5.2 通用配色

- **主色**：海军蓝 Navy `#003366` — 存储行业主基调
- **AI 增量色**：洋红 `#CC2266` — 突出 AI 相关增量数据
- **国产替代色**：金橙 `#E8880C` — 国产化率 / 国内厂商数据
- **正向色**：绿 `#2E8B57` — 低估 / 机会 / 超预期
- **警示色**：琥珀 `#C88400` — 风险中性
- **危险色**：红 `#C0392B` — 高风险 / 高估 / 下修

### 5.3 版式规范

- PDF A4 单栏，图表宽度 `\linewidth`（约 15cm）；必要时 `\small` / `\footnotesize`
- 编号规范：`图 <章号>-<序号>` / `表 <章号>-<序号>`；中英双语标题（上中下次英小一号斜体）
- 每张图/表底部必须有 **Source** 行：`Source: <来源编号>（见表 A-1 来源注册） / AStock 测算`
- 预测数据必须加 "E" 后缀，区间用 `~` 连接（如 `2026E PE 30~40x`），**禁止虚假精度**
- 表格采用三线表；关键行（核心标的/悲观情景）加浅底色

---

## 六、附录表格规划

### 应放入附录的长表格（正文只保留精简版）

| Appendix | 编号 | 标题 | 行数 | 理由 | 正文引用 |
|----------|------|------|------|------|---------|
| A | 表 A-1 | 来源注册登记表（含 L1-L6 全部来源编号、名称、日期、可信度） | ~60 行 | 强制合规要求 | 每张图表的 Source 行 |
| A | 表 A-2 | 估值审计表（每个估值方法假设校验、PE = Price/EPS 算术检查） | ~30 行 | 强制合规要求 | Ch8 表 8-2 "详见表 A-2 估值审计" |
| B | 表 B-1 | 供应链关系矩阵完整版（23 标的 × 客户 × 收入敞口 × 可信度四级） | ~60 行 | 表格过宽（>8 列） | Ch3 表 3-2 "详见表 B-1" |
| C | 表 C-1 | 23 只标的多维总表完整版（含 5 年财务历史） | 23 行 × 18 列 | 18 列过宽 | Ch7 表 7-1 "详见表 C-1" |
| D | 表 D-1 ~ D-23 | 各标的业务结构 + 财务数据小表 | 23 × 2 表 | 数量多，正文嵌入会打断叙事 | Ch7 各公司深度 "财务明细见附录 D" |
| E | 表 E-1 | 卖方共识矩阵完整版（所有评级/目标价历史） | ~80 行 | 过密过长 | Ch9 表 9-1 "详见表 E-1" |
| F | 表 F-1 | 数据验证摘要（原始 → 核验，核对率和未核实条目） | ~20 行 | 工作流证据 | 报告末尾合规声明 |

### 正文 vs 附录划分规则

- 正文表格 ≤ 10 行 × 8 列；超过入附录
- mermaid 架构图与定量图表（柱状/折线/散点/饼）一律正文展示，是核心视觉
- 来源注册/审计类/明细类一律入附录
- 正文中引用附录时用 `（详见附录 <字母> 表 <编号>）` 字样

---

## 七、负责制作的环节总览（Pipeline Mapping）

> 便于 orchestrator 在 Phase 3→4 交接时追踪交付物。

| Pipeline 阶段 | 负责的图表范围 | 验收条件 |
|--------------|---------------|---------|
| **Phase 1 Data Collector (financials)** | 表 5-1（财务数据底）、表 7-1 基础列、表 8-1（海外可比）、附录 D | 所有 ticker 三表数据齐全（≥95%） |
| **Phase 1 Data Collector (market)** | 图 7-1 市值数据、图 8-1 PE Band 历史、图 8-2 散点基础数据 | 近 3 年日频行情与市值 |
| **Phase 1 Industry Analyst** | 图 3-1（产业链）、图 4-1（HBM 路线）、图 4-2（CXL 拓扑）、图 4-3/4-4（TAM 图）、图 5-1/5-2/5-3（供需价格图）、图 6-1/6-2（格局图）、表 3-1、表 4-1/4-2、表 5-1/5-2、表 6-1、表 3-2 矩阵 | 所有行业数据有 L3+ 来源；mermaid 草案在分析阶段完成 |
| **Phase 1 Source Governance Analyst** | 附录 A 表 A-1（来源注册）、表 2-2（声明可信度）、表 9-1/表 E-1 来源编号 | ≥20 个卖方/行业来源注册完毕，L1/L2 ≥ 40% |
| **Phase 2 Data Verifier (all)** | 附录 F 表 F-1（验证摘要）、表 8-2 数值校验 | >95% 算术核对通过 |
| **Phase 2 Report Analyzer** | 表 4-1/4-2 TAM 共识、表 9-1/表 E-1 共识矩阵、表 9-2 目标价历史 | ≥10 份卖方报告归类完成 |
| **Phase 2.5 House View Analyst** | 图 1-1（四主线）、图 1-2（资金流）、表 1-1/1-2、表 2-1、图 11-1（催化剂）、图 11-2（哑铃）、表 11-1 | 每个强结论在 house_view 中有出处 |
| **Phase 3 Valuation Modeler** | 图 8-1 PE Band、图 8-2 估值散点、图 7-2 敞口散点、表 8-1、表 8-2、表 7-1（估值列） | PE = Price/EPS 等算术 100% 正确 |
| **Phase 3 Risk Analyst** | 图 10-1 风险矩阵、表 10-1 压力测试、表 10-2 监控体系 | 情景参数可追溯到历史类似事件 |
| **Phase 3 Valuation Auditor** | 附录 A 表 A-2（估值审计） | 所有估值逻辑再验算一遍 |
| **Phase 3 Exhibit Architect（本文件）** | 全规划文件 + 强结论映射表 + 视觉规范 | 覆盖 100% 强结论；≥12 图 + ≥10 表；mermaid 5 张全部列明 |
| **Phase 4 LaTeX Writer** | 最终渲染：所有图表嵌入正文 + 附录，版式 + Source 行 + 中英标题 | XeLaTeX 零 error；每个 P0 图表编号与本文件一致 |
| **Phase 4.5 Visual Layout Reviewer** | PDF 页级检查：图表裁切、跨页、字号、长表 longtable | 无图表被截断；无表格溢出页宽 |

---

## 八、下一步行动建议

### 本周必须完成（进入 LaTeX 前置条件 — 7 项）

1. **5 张 mermaid 架构图完成初稿**（图 1-2 / 3-1 / 4-1 / 4-2 / 5-2）— 由 Industry Analyst 提供数据节点，LaTeX Writer 渲染测试
2. **表 8-2 核心标的预测+估值权重完成**（Valuation Modeler），并经 Valuation Auditor 验算（表 A-2）
3. **表 5-2 季度供需-合约价表定稿**（Industry Analyst），支撑 SC-3、SC-4
4. **表 6-1 国产替代进度表定稿**（Industry Analyst），尤其是 HBM 国产节奏数据必须标注 "⚠️ inferred + 管制 L4"
5. **图 7-2 AI 敞口 vs 估值散点的数据准备**（Valuation Modeler），用于核心筛选逻辑
6. **表 9-1 卖方共识矩阵精简版**（Report Analyzer），确保每个目标价都有来源编号
7. **表 10-1 压力测试情景参数校准**（Risk Analyst），与估值模型联动

### 下阶段优化（LaTeX 写作并行 — 5 项）

8. 图 5-1 capex 堆叠柱 + 图 5-3 合约价折线（需要历史合约价数据，可先用卖方公开图占位并标注 "Source: TrendForce 2026"）
9. 图 8-1 PE Band（需要近 3 年行情；如暂无，先用近 1 年 + 标注 "数据窗口有限"）
10. 图 6-1 HBM 份额饼图（三家原厂数据，可从卖方报告抽取）
11. 图 10-1 风险矩阵（Risk Analyst 量化各风险的概率/影响分，0-10）
12. 附录全部长表迁移为 longtable / tabularx

### 可选增强（PDF 渲染后调优）

13. 图 4-5 原厂 HBM 营收占比折线
14. 图 5-4 库存-价格领先滞后关系
15. 图 8-3 估值分位温度计
16. 图 7-3 北向持仓热力图
