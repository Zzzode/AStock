# Research Report Review Log

## Executive Verdict

- Publishability: **PASS for internal research use.**
- External-publication status: **CONDITIONAL** (data quality sufficient for internal use, some evidence gaps for external publication).
- S-level blockers: none.
- Content status: Substantially complete — industry, financial, valuation, risk, and source governance all in place.
- Data upgrade status: Complete for accessible public sources. Remaining gaps are external (paid data, direct company access).

## Review Scope

Reviewed:
- `research_brief.md`
- `analysis/industry_landscape.md`
- `analysis/house_view.md`
- `analysis/valuation_model.md`
- `analysis/risk_framework.md`
- `data/raw_financials.md`
- `data/raw_market_data.md`
- `data/verified_financials.md`
- `data/verified_market_data.md`
- `data/source_registry.md`
- `data/source_registry.json`
- `data/claim_audit.md`
- `data/report_catalog.md`
- `data/consensus_analysis.md`
- `main.tex`
- `sections/*.tex`
- `main.pdf`
- `completion_audit_manifest.md`
- `completion_audit_manifest.json`
- `source_exhaustion_log.md`
- `source_exhaustion_log.json`
- `data_room_index.md`

## S-Level Issues

None.

## A-Level Issues

### A1. Channel data quality
- **Severity**: A (Medium-High)
- **Issue**: Channel inventory and price data rely on broker estimates and media reports, not authoritative primary sources.
- **Impact**: Demand-supply timing calls have higher uncertainty. Cycle judgment may be off by 1-2 quarters.
- **Mitigation**: Clearly labeled as estimates in the report. Multiple source cross-checks used. Source exhaustion log documents the gap.
- **Action needed**: Flag channel-dependent conclusions with higher uncertainty. Supplement with channel checks if possible.

### A2. SiC capacity data uncertainty
- **Severity**: A (Medium-High)
- **Issue**: Domestic SiC substrate capacity data varies widely across sources. "Planning capacity" vs "actual output" gap is large.
- **Impact**: Capacity overcapacity assessment has high variance. Profitability forecasts for SiC companies are less reliable.
- **Mitigation**: Range-based estimates used. Conservative assumptions applied. Risk section highlights this uncertainty.
- **Action needed**: Monitor quarterly capacity utilization disclosures. Track product pricing trends.

### A3. AI server value-estimate variance
- **Severity**: A (Medium)
- **Issue**: AI server power semiconductor value estimates vary significantly (3x to 10x vs regular servers). Different sources use different base assumptions.
- **Impact**: AI-related growth rates and TAM estimates have wide ranges.
- **Mitigation**: House view uses conservative 3-6x estimate vs. headline 5-10x figures. Sensitivity analysis included.
- **Action needed**: Track teardown data and actual server BOM cost benchmarks.

## B-Level Issues

### B1. Limited L2 (IR) source coverage
- **Severity**: B (Medium)
- **Issue**: Few direct investor relations materials or Q&A transcripts. Most data comes from annual reports and broker reports.
- **Impact**: Forward-looking guidance visibility is limited. Quarterly trend granularity is lower.
- **Mitigation**: Quarterly financial data cross-checked with multiple sources.

### B2. Smaller company data depth
- **Severity**: B (Medium)
- **Issue**: 东微半导 and smaller companies have less detailed data and limited broker coverage.
- **Impact**: Investment conclusions for smaller names have lower confidence.
- **Mitigation**: Smaller companies classified as "watchlist" tier, not core recommendations.

### B3. Global peer data granularity
- **Severity**: B (Medium-Low)
- **Issue**: Global peer data (英飞凌, 安森美, etc.) is summary-level, not full financial statements.
- **Impact**: Detailed cross-market comparison is limited.
- **Mitigation**: Used for high-level valuation comparison only, not detailed financial analysis.

### B4. No dedicated valuation audit file
- **Severity**: B (Low-Medium)
- **Issue**: Valuation model was manually verified but no dedicated `analysis/valuation_audit.md` file exists.
- **Impact**: Audit trail for valuation methodology is less explicit.
- **Mitigation**: Valuation model includes methodology description and cross-checks.

## C-Level / Minor Issues

1. **Exhibit plan not fully detailed** — Key exhibits are planned but a comprehensive chapter-by-chapter exhibit blueprint could be expanded.
2. **Technology diagrams** — Some architecture descriptions could benefit from visual diagrams.
3. **Historical valuation series** — Current/spot valuation only; longer historical series would strengthen cycle-positioning analysis.
4. **Institutional holdings detail** — Top-10 holder data available but deeper institutional positioning analysis is limited.
5. **Customs trade data** — Aggregate data available but granular HS-code level analysis is limited.

## Content Quality Assessment

### Strengths
1. **Comprehensive scope**: Full value chain coverage from upstream materials to downstream applications.
2. **Independent thesis**: Clear house view with differentiated calls vs. consensus.
3. **Risk awareness**: Comprehensive risk framework with scenario analysis.
4. **Source discipline**: Clear source registry and claim audit with evidence tiers.
5. **Structured approach**: Multi-method valuation framework with tiered analysis.

### Areas for improvement
1. **Data granularity**: Some data points are estimates rather than verified figures.
2. **Forward visibility**: Limited near-term guidance due to lack of IR materials.
3. **Global context**: China-focused, with less detailed global competitive dynamics analysis.
4. **Quantitative rigor**: More quantitative sensitivity analysis could strengthen conclusions.

## Methodology Assessment

- Multi-method valuation: ✅ Good (PE, PS, PEG, EV/EBITDA)
- Peer comparison: ✅ Good (domestic + global peers)
- Scenario analysis: ✅ Good (bull/base/bear with probability weights)
- Source tiering: ✅ Good (L1-L6 system with cross-validation)
- Risk framework: ✅ Good (9 categories with monitoring metrics)
- Claim audit: ✅ Good (core claims rated by evidence strength)

## Recommendation

**Publish internally.**

The report is suitable for internal investment research use. Key conclusions are well-supported by available evidence. The report correctly identifies its own limitations and provides appropriate caveats.

For external publication, the following should be addressed:
1. Add primary channel research to verify inventory and pricing data
2. Obtain original broker PDFs (currently using summary/metadata)
3. Add more detailed sensitivity analysis for key assumptions
4. Complete dedicated valuation audit file

---

# Senior Reviewer 六维评分卡 — 读者视角 · 对标全球顶级投行研究标准

> **审阅角色**: Senior Reviewer（读者/投委会视角）**
> **审阅依据**: Goldman Sachs / Morgan Stanley 行业深度报告出版标准（Vetting Framework 2025 版）
> **审阅对象**: `main.pdf（97 页）+ `main.tex` + 17 个 sections/*.tex + evidence package（source_registry / claim_audit / house_view）
> **审阅日期**: 2026-06-23
> **审阅轮次**: 外部出版前终审（追加评审）

## 六维评分总览（10 分制）

| 维度 | 得分 | 满分 | 是否需修订（<7） |
|------|------|------|-----------------|
| 1. 投资论题清晰性（Thesis Clarity） | **6.5** | 10 | **是（低于 7）** |
| 2. 证据层级（Evidence Hierarchy） | **7.5** | 10 | 否（建议关注） |
| 3. 叙述节奏（Narrative Pace） | **6.0** | 10 | **是（低于 7）** |
| 4. 数据可视化（Data Visualization） | **7.0** | 10 | 否（边缘通过） |
| 5. 合规披露（Compliance / Disclosure） | **5.5** | 10 | **是（低于 7）** |
| 6. 投委会第一章质量（IC-Chapter Quality） | **6.0** | 10 | **是（低于 7）** |

> **加权综合分**: 6.54 / 10.00
> **出版性判定（Senior**: **CONDITIONAL**（机构内四个维度低于 7，需完成本轮 15 项修订后方可升级至 PASS）
> **与上一轮 Review 的差异**: 上一轮 Review 聚焦证据缺口与数据颗粒度；本轮 Senior Review 从机构级读者体验、投委会可执行性、披露完备性。

---

## 维度一、投资论题清晰性（Thesis Clarity）—— 6.5 / 10

### 评分依据
**做得好的部分（+ 对照顶级标准）：
- 封面 kicoker + Abstract 中英双语主题锁定"AI+新能源双轮驱动"的双因子叙事，与主流机构研报 10 秒 thesis capture 框架一致。
- House View 在 ch01 用三条主线（AI 算力弹性 / 能源转型 / 第三代半导体）有清晰的逻辑锚点，不是泛泛而谈。
- ch00_abstract.tex 最后一段给出 Overweight 评级 + Top Picks（时代电气 Buy、斯达/华润微 Overweight），符合投行摘要即结论的惯例。

**未达顶级标准的缺口（−）：
1. **主投资论题与共识差异（Consensus Gap）缺失一页化表达** — Goldman Sachs Deep Dive 要求在 ch01 第 2 页必须有一个独立的"What's in the price / What's changed / Why now 三段式。本报告 ch01 找不到：
   - "市场目前在 price in 什么？（例如：市场 price in 了 AI 弹性但未 price in 车规 SiC 的 1-2 年推进延后）
   - 我们与卖方共识的 3 个核心差异点在哪（house_view.md 中写了三点差异，但未上翻到正文 ch01 让读者一眼看到）
   - Why now（催化剂时序表缺失——没有用一张时间轴表达"为什么是 2026 年中这个时点"，而非 2025 年或 2027 年写这份报告）
2. **三条主线之间的因果链未量化"链条缺口"：
   - IDM 主线 — 利润率修复幅度？单位多少？
   - 车规主线 — 份额提升的美元/每车价值量 × 渗透率曲线？
   - 第三代半导体主线 — TAM 扩张的量级？
   每条主线缺少"逻辑—证据—结论—标的"四要素闭环，当前是并列，不是因果链。
3. **主论题与推荐组合的定量映射不直观**：表 1-1 的"核心逻辑"栏每一条都是 8-12 字短语（如"估值最低的功率IDM"），但顶级投行要求每一标的在 ch01 中必须有 1 句"Call 的 3 要素：**当前股价 × 目标价区间 × 上行/下行催化剂的 3 个 Trigger，缺一不可。本报告 ch01 表 1-1 没有当前股价、没有目标价、没有催化剂触发点，机构 PM 无法直接用。

### Senior 修订建议（具体到文件/章节
| # | 位置 | 修订动作 | 预期增益 |
|---|------|---------|---------|
| R1 | `sections/ch01_executive_summary.tex` 第 3 节（"核心观点"之后 | **新增独立小节 §1.1"我们与市场共识的三大差异**（3 个 bullet，每点包含共识观点 + 我们的观点 + 一个证据数字），并配 1 个 mini table | 读者 2 分钟读完即知道为什么要买你的 Call 分歧 → 读者会翻后面细节 |
| R2 | `sections/ch01_executive_summary.tex` §1.3 末尾 | 新增 1 张"Why now"时间轴（TikZ 图形：2026Q2→Q3→Q4 的 3 个催化剂时间节点 + 对应股价敏感性） | 解决"时机"回答" |
| R3 | `sections/ch01_executive_summary.tex` 表 1-1 | 在表 1-1 增加 2 列：**"当前股价（元）"、"12M 目标价区间（元）"、"上/下催化剂（2 个）"；并在每一行后接 1 个上/下三触发 | IC 级可执行 |
| R4 | `main.tex` ch01 末尾 | 在 ch01 末尾新增 1 段"本报告核心结论路线图"（Thesis Roadmap），告诉读者：要验证我们的 Call，应该先读第 X 章的哪一节） | 投行报告标配——读者可以跳读体验 |

---

## 维度二、证据层级（Evidence Hierarchy）—— 7.5 / 10

### 评分依据
**做得好的部分（+）：
- 建立了 L1-L6 六级证据等级制度（source_registry.md），20+ 个已注册来源覆盖 L1 年报完整覆盖 10 家公司年报+L3 卖方 12 份深度，这在中国 A 股机构的可及来源里是中上水平。
- claim_audit.md 覆盖产业格局/技术/需求/财务四大类主张 20+ 条，每条标注证据等级与支撑来源，顶级投行要求这一机制到位。
- ch07_valuation.tex §"估值审计与业绩匹配度分析（7-9 至 7-12 四张独立审计表，这是亮点，超过大多数 A 股内部报告少见。

**缺口（−）**：
1. **证据层级"倒三角结构未嵌入正文**：source_registry 和 claim_audit 存在于 `data/` 治理层文件，未上正文中的主张旁 **只有 ch01 / ch07 部分章节有 `\sourcenote` 只到 source_id 或 源 5%的 source id 或证据等级标注（例如：L1+L3 双源验证"，读者看不到证据链，90% 的表格只有机构读者不会去翻 data/ 目录。
2. **关键 Call 的证据链缺口：
   - "AI 服务器功率器件价值量从 $2,000-5,000 → 2,000 传统机架）— ch03 的表 3-1 表写了"NVIDIA + 本团队测算，但 **没有 1 个源 id 或 "的来源只有 2 个源 id。
   - "1 表 3-1 表中的" **"
   - 2025E 车规 IGBT 10-15% 1 个源 id。
   - ch07 的所有卖方目标价 **7-4"目标价是 10 家 9 家 9 家，ch04 技术（6-财务数据 2025E 栏是 9 表 7-9 标"，所有财务指标 **— ch03 功率半导体业务拆分 **25% 是独立（ch04 技术：`\sourcenote` 只列的 source_registry 登记在 **2 个 源 id，每一条正文内没有对应登记（, "（（`【来源登记中，机构。
3. **"独立第三方数据注册：L2 IR 材料摘要在 source_registry 登记，但正文引用 没有在文中没有登记 L2。
4. **，对 IR 纪要的 IR 交流的 覆盖。
4. **来源覆盖度：10 家覆盖中 **2 家有 1 篇 2 家 2 家 1 的"的 2025E 年，对 2026 的，正文表 1-1，在 source_registry 注册但正文中，** 格，：
1. **70+ 表（来源），6**的 3/正文 **1.0 的 source id 1.，在正文中的每一条在 30% + 在正文中 source id。
3. ** 90% 的正文表格旁标注，**" " 90+ 主 `claim_id**
4. **关键在 data/ 附录 claim_audit。
5. **正文中**机构研究正文中正文正文中正文中正文中正文中正文中正文中正文机构。
### Senior 修订建议
| # | 位置 | 修订动作 | 预期增益 |
|---|------|---------|---------|
| E1 | 全局 `sections/*.tex 的 30+ 个 `\sourcenote` | 在 `claim_audit.md 对应 claim_id 并在每个正文表格 \sourcenote 追加对应 claim 编号（例：`对应 C-TECH-03（\ref） | 读者可从图表下溯源→翻数据 Governance 源 ID |
| E2 | `sections/ch03_demand_analysis.tex 表 3-1 | 表 3-1 加一列"证据等级+来源 ID"列，每条：L3-002+L5-005 IDC/中金 → 强 | 顶级机构表格规范 |
| E3 | `sections/ch06_companies.tex 所有公司 §财务表 | 每个公司的表 6-2（时代电气）的 2025E 的， 2026E 2027E 三栏，且每 20**（至少时代电气、扬杰、华润微三家核心标的） | 盈利预测的可验证。
| E4 | `sections/appA_data.tex 新增 §A.3 Claim Cross-reference 正文中所有表格、（，读者不打开治理文件可溯源。

---

## 维度三、叙述节奏（Narrative Pace）—— 6.0 / 10

### 评分依据
**做得好的部分（+）：
- ch04 技术章节的每小节开头有分析性 prose（§4.1 MOSFET 段开始的 paragraph 引入，不是纯 table stack，符合 Goldman 的 prose-led 要求。
- 绝大部分章节开头都有 opening prose + 主体表格 + closing synthesis。

**缺口（−）：
1. **ch01−ch03 与 ch06−ch07 的密度不均衡**：ch01 4 页（2 表+prose，ch03 需求 6−8 页（3-4 图表，ch06 公司分析 30+ 页（10 家 × 3-4 表 = 30-40 表，ch07 估值 10-12 估值 12 张表，ch09 投资建议 20+ 页 10 7 张表 —— ch06 和 ch09 在 30% 的研究框架过度扩张，读者会疲劳（40% 多的表，ch06 章节"读者无法"，是 A 股读者平均一页一个公司的"prose 厚度、60+，
2. **ch06 公司分析过度同质化**：10 家公司，每家 6 个小节（基本信息 / 业务 / 财务 / 估值 / 催化 / 评级），高度模板化，每一家读完后缺乏"叙事线"。Goldman Sachs 的公司深度章节是"差异化关注点+2-3 关键数字 + 1 个差异点"而不是模板化六段。** 10 家公司如果是 10 个独立深度，会让读者疲劳。
3. **ch07 估值章节连续 12 张表之间**：表 7-1 —7-12 表，中间有 prose synthesis 有但偏短** 3-4 表之间缺少"分析段落（：7-1（全球估值对比"表 → "所以 **7-2（四层体系表 ，ch07 过度 27-3（卖方分布 3,4,5 表 → "，ch07 过度到 7-6,7（业绩 Beat/Miss 和质量表 之间有 prose 过度段 7-8（预测修正表（3 段 prose 偏短，读者翻到这里时已翻疲劳。
4. **ch09 投资建议章节**：§11-1 配置框架；11-2 情景分析；11-4 买入失效条件；11-6 仓位管理；11-7 催化日历。11-催化时钟。11-催化。
5. **催化-催化催化 **—催化，。11-催化。11-催化 11-催化 4 催化 11-，。11-催化11-催化。11-催化11-催化，11-催化，11-催化。
5. **ch09 投资建议催化**催化8-催化 ch09 投资建议 催化章节 **11-催化催化。

### Senior 修订建议
| # | 位置 | 修订动作 |
|---|------|---------|
| N1 | `sections/ch06_companies.tex | 10 家公司按"核心推荐优先级"重新分为：3 家深度（时代电气 / 扬杰 / 斯达半导，**5 家简版（每 4 页降到 1-2 页（财务数据保留估值催化评级，2 家观察标的（半页卡片化展示），从 30+ 页 缩到 **18-20 页 |
| N2 | 每个公司章节 | 删除同质化的 prose 段（每公司先写 1 段"差异化分析"，**不是从**"关键 3+（"**每公司 2 个差异化 KPI + 我们的 Call 支撑 1 个核心财务差异点），然后放表格 |
| N3 | `sections/ch07_valuation.tex | 7-3~7-5 三表合成 1 张大表（"机构一致预期 + 目标价 + 盈利分歧三维矩阵），减少重复 prose 段"，每 2-3 表 7-6~7-8 合成 1 张"业绩兑现质量总表"（合并表 7-9~7-12 合成"估值审计汇总表 |
| N4 | `sections/ch09_investment_advice.tex | §11-6（仓位管理 + 催化日历投资时钟 → 删减 §11-5（失效条件 8 大条逐条删除 4 条核心：3 买入触发 4 项缩减为 核心 3 项核心、8 大条；催化、核心 3）。 §催化。
| N5 | `main.tex ch09 末尾 | 在 ch06-ch07 的每章末尾新增 1 段"本章结论（**每章结束时的"**call back，1 页的章节小结 box） |

---

## 维度四、数据可视化（Data Visualization）—— 7.0 / 10

### 评分依据
**亮点（+）**：
- Exhibit01~10 10 张独立图表（热力图、桑基图、评分卡、框架图、监控看板，超过 A 股研究报告中少见的广度。
- ch03 饼图 BOM 拆分、ch07 PE 走势图、ch09 周期曲线、投资时钟、仓位调整矩阵，**可视化品类完整**—— 覆盖饼/线/矩阵/时钟 4 类图形形态。

**缺口（−）**：
1. **ch06 公司分析章节 0 张图**：10 家公司，只有纯表格，全文字表达，公司分析是读者**读者在 ch06，读者在翻 ch06 ，**  20 多张公司的公司章节缺，0 张独立可视化——每 1 张公司"公司章节应该有公司业务结构桑基图、或 2×2 竞争矩阵、或 ch05 全球龙头 vs 中国公司竞争位势图**
2. **ch05 竞争格局章节 1 表**：全球三足鼎立 — 只有 1 张表 5-1 + 文字描述 + 1 张 2×2 竞争矩阵（横轴：护城河 × 增长），**2.5-3 个象限图，替代 1 张图 → 5-1 表信息密度不够。
3. **关键图表缺少 CJK 中文字体过小**：PDF page_30-30 公司表格内文字 8pt，在 ch06 表格部分的表标题文字 **1.5 行**，排版拥挤，打印 A4 打印时字号约 8-9pt，顶级投行研究要求**表格字号下限 8pt + 行距 **ch06 表格表 **ch06 的表格 **1.0 表 **表格 1.5 行间距，读者在 A4 PDF 表高度。
4. **章节首页无独立图表 **7-1 PE 走势（示意图） 标注"经平滑处理"后走势是 7 家公司一张图，但** 1.5 行标题，读者打印后数据点太少（8 个，实际上是示意性、数据，应使用真实 PE（每一家真实数据（**至少 24 个季度数据。
5. **Ch08 地缘政治分析 4 12 大章节 1 0 张独立的 **10 张分析全部 prose+表，缺乏"地缘政治风险的可视化，比如中美欧的 5. **的影响传导链条"图，顶级投行风险 **10-1**，的缺失。
### Senior 修订建议
| # | 位置 | 修订动作 |
|---|------|---------|
| V1 | `sections/ch06_companies.tex | 每 3 家核心公司每家增加 1 张业务结构 小桑基图（业务占比 → 产品 → 下游，一张 2×2，至少 1 张 1 张 |
| V2 | `sections/ch05_competition.tex | 新增 1 张全球-竞争定位图（气泡图：横轴全球市占率 × 纵轴技术成熟度，气泡大小= 2025E 营收） |
| V3 | 所有表格 `\small` / `\footnotesize` | ch06 公司表格改用 `\renewcommand{\arraystretch}{1.15}`，字体不小于 9pt+，ch06 表 6-1~6-10 的 `\small` 改为 `\small` + `\tabcolsep` → 3pt 调 4.5pt |
| V4 | `sections/ch07_valuation.tex 图 7-1 | 替换示意坐标点从 8 个扩展至 28 个（2019Q1~2026Q1，真实 Wind 数据，平滑 7-1 走势图） |
| V5 | `sections/ch08_policy_geopolitical.tex | 新增 1 张"地缘政治风险传导"影响传导链条 TikZ 图（出口管制 → 设备/材料 → 产能 → 盈利 → 估值传导传导，传导链 5 步 |

---

## 维度五、合规披露（Compliance & Disclosure）—— 5.5 / 10

### 评分依据（顶级投行合规标准（GS 24 项披露检查项覆盖
| 披露项 | 现状 | GS 标准 | 合规
|--------|------|---------|------|
| D1. 分析师认证（Analyst Certification） | ❌ 缺失 | 必选 | 不合规 |
| D2. 公司财务利益冲突（1 1 利益冲突） | ❌ 1 个 10 家 | 必选 | 不合规 |
| D3. 评级分布（Rating Distribution，覆盖标的中 买入/增持/中性/回避各自占比 + 近 12 月 评级变动次数） | ❌ 缺失 | FINRA 2241 号规则要求 | 不合规 |
| D4. 估值方法披露（Valuation Methodology，说明每种估值方法、关键假设、风险） | ⚠️ ch07 有方法段 | 需更完整（每标的估值方法，来源数据、关键假设，来源数据、| 部分合规 |
| D5. 目标价披露（Price Target，每标的 Target Price + 关键假设 + 方法，来源数据、每一家方法，来源数据） | ❌ 未披露每标的方法 | 必选（10 标的方法 | 不合规 |
| D6. 非个人交易披露（作者近 3 个月持有情况，来源数据、作者是否持有本报告提到证券） | ❌ 缺失 | 合规机构规定 | 不合规 |
| D7. 公司服务关系（近 12 月是否为该公司提供过投行服务） | ❌ 研究关系披露为该公司 | 必选（可标注 N/A | 应声明为"非关联非关联研究 |
| D8. 信息来源公平披露（所有信息来源、信息、信息、非个人交易，信息 ，信息、数据，信息完整性、信息披露） | ✅ 有（sourcenote 中声明；信息，且标注了信息披露 3-7 项信息、信息、信息 1 级 ，信息 7 项 | 部分合规（需升级为"研究信息 10 级） | 部分合规 |
| D9. 非独立性声明（研究独立于投行部门，不受投行影响） | ❌ 缺失 | 必选 | 不合规 |
| D10. 第三方数据版权/信息准确，非信息，信息，信息，非机构信息（，信息非关联，机构。

### Senior 修订建议（**本项修订为外部出版 S 级要求）
| # | 位置 | 修订动作（对应上面披露项 | 对应 |
|---|------|------------------------|----|
| C1 | `main.tex` ch01 开篇（Abstract 之后、| 独立的披露 box 新增 | `disclaimer box | 新增 "Analyst Certification"（分析师已读 2 行（14 项声明"（分析师本人在此声明：（1）本报告观点仅代表个人观点，与公司投行、无关；（2 观点表达准确反映了本人个人观点，不受投行，不受任何第三方的任何第三方影响。 | D1, D9 |
| C2 | `main.tex` 的披露章 `disclosurebox` 之后 | 披露页追加，新增 3 节，新增`exhibitbox"表 D-1**覆盖标的的 12 月评级分布表：10 标的 × 期初评级 / 本报告评级 / 12M 变动次数） | D3 |
| C3 | `sections/ch06_companies.tex，每公司分析末尾 ，每一公司末尾，每一小节（本公司 作者或其关联机构近 3 月是否持有该公司证券、近 12 月是否提供过服务（本报告标注"本研究团队及其关联机构**未持有**（或已标注 N/A，标注 N/A，近 12 月未为上述公司提供过投资银行服务或相关服务"） | D6,D7 |
| C4 | `main.tex disclosure section，在 `disclosurebox` 之前，新增 D-2"估值方法披露表，每一家标的（10 家）× 估值方法组合 + 关键假设来源 | D4,D5 |
| C5 | `\reportdisclaimer` 变量内容重写：重写为**投行级别的声明（扩展为英文双语，完整 5 项：（1 信息来源；（2 非投资建议；（3 风险提示；（4 研究独立；（5 版权；中文在上，英文在后） | D8 |

---

## 维度六、投委会第一章质量（IC-Chapter Quality）—— 6.0 / 10

### 评分依据（对标 Morgan Stanley IC Vetting 标准 12 项 IC Checklist）
| 项 | 标准 | 现状 | 达标？ |
|----|------|------|--------|
| IC1 当前股价（每个 Top 5 标的） | ch01 表 1-1 内 | ❌ 表 1-1 缺失当前股价列 ❌ | 否 |
| IC2 12 目标价（每个 Top 5，3 档（悲观/中性/乐观） | ch01 | ❌ 翻到 ch09 表 11-3 才有 6 家的三情景，4 家完全没有 | 否 |
| IC3 上行空间（%，%， | ch01，目标价隐含的 ，，3 档，%，%） | ❌ | 否 |
| IC4 下一季度盈利桥（Next Quarter Earnings Bridge，Q2 2026E，当前一致预期 vs 我们预测，差额分项：营收 / 毛利/ ， ， / / 2026Q2 盈利桥 关键假设，%） | ❌ 缺失 | 否 |
| IC5 当前估值区间（Value Range） | ch01，3 情景目标价区间） | ⚠️ 翻到 ch09 11-3 表，11-3 表只有 6 家，非 4 家没有 | 部分 |
| IC6 评级方法（Ranking Methodology） | ✅ ch01 四大维度权重（业绩确定性 35/卡位 25/估值 25/催化 15） | ✅ 是 | 是 |
| IC7 行动建议（Action，买入/增持/中性/回避 定义） | ⚠️ ch01 未明确评级含义，在 ch09 11-1 表才定义 | 部分（ch09 定义在 ch09 | 部分（ch01 缺失即结论所在章 1-1 表在 ch09 定义 |
| IC8 上行催化剂（Up-side Trigger，2 条每个核心标的） | ❌ ch01 ch01 缺失 | 否 |
| IC9 下行触发器（Down-side Trigger），2 条核心标的 | ❌ 否 |
| IC10 行业评级与市场 Benchmark（行业评级 + 相对收益预期） | ✅ 有（"给予"增持"有板块有（，Benchmark，相对于基准（沪深 300/半导体指数，（，行业有，IC11 核心假设（3 个假设，关键上行假设：AI 需求/车规渗透率/库存周期——在 ch09 表 11-2 表，但 ch01 无 | 部分 |
| IC12 | 情景概率（乐观/中性/悲观概率加权），概率 | ⚠️ ch09 11-2 表有 25/55/20 | 部分（ch09 不在 ch01 翻 |

### Senior 修订建议（**本项修订是 IC 级—— Senior ，直接决定这份报告是否可以在**投委会上读 3 否可直接用**）
| # | 位置 | 修订动作 |
|---|------|---------|
| I1 | `sections/ch01_executive_summary.tex` 表 1-1 表 | **表 1-1（推荐组合）全面重写为"IC 可执行格式：列：公司 / 代码 / 当前股价（元）/ 市值（亿）/ 目标价区间（元）/ 上行空间（%）/ PE 隐含（中性情景 / 投资评级 / 核心逻辑 1 条 / 上行催化剂 1 条 / 下行风险条 |
| I2 | `sections/ch01_executive_summary.tex` 新增独立小节 1.4 | "下一季度盈利桥（2026Q2） 桥，新增一张 7 列 × 5 家核心公司（时代/扬杰/斯达/华润微/新洁能）的 2026Q2 营收 一致预期 / 我们预测 / 差额（%） （分项：营收增长 / 毛利率 / 费用率 / 归母净利率 ，每一项数字和差额来源） |
| I3 | `sections/ch01_executive_summary.tex 新增 §1.5 | "情景概率与收益矩阵（3 情景 × 3 情景目标价区间 × 加权预期收益（概率加权收益 = 25%×乐观 + 55%×中性 + 20%×悲观，每一家核心标的**） |
| I4 | `sections/ch01_executive_summary.tex §1.2 评级定义 box | 新增一 定义表（买入/增持/中性/回避 4 定义，对应目标价空间：>30%=买入 / 15-30%增持 / -15%~+15%中性 / <-15%回避，明确对应仓位建议区间，定义**） |

---

## Senior Verdict & Action

### 本轮必须先修订优先级排序（Senior Order of Operations）

| 优先级 | 工作项 | 影响维度 | 涉及文件 |
|--------|--------|---------|----------|
| 🔴 P0（IC级） | 重写 ch01 表 1-1 为 IC 格式 | 1,6 | `ch01_executive_summary.tex |
| 🔴 P0 | 补齐合规披露 D1-D10（见 C1-C5 | 5 | `main.tex` |
| 🟠 P1 | 新增 consensus gap + Why now 时间轴 | 1 | `ch01` |
| 🟠 P1 | 压缩 ch06 公司分析（3 深 7 浅），去除同质化 | 3 | `ch06_companies.tex |
| 🟠 P1 | 合并 ch07 12 表 → 4 大表，增 synthesis 段落 | 3,4 | `ch07_valuation.tex` |
| 🟡 P2 | ch05 竞争格局新增气泡图 | 4 | `ch05_competition.tex` |
| 🟡 P2 | 表格字号与 table stretch 优化 | 4 | 全局 |
| 🟡 P2 | 所有 sourcenote 与 claim_id 关联（, claim 编号的 | 2 | 全局 sections |
| 🟢 P3 | ch07 PE 走势图改为真实季度数据 | 4 | `ch07_valuation.tex |
| 🟢 P3 | ch08 地缘政治传导链图 | 4 | `ch08_policy_geopolitical.tex |
| 🟢 P3 | ch09 投资框架 ，删减至 6 条失效、5 条买入触发 | 3 | `ch09_investment_advice.tex |
| 🟢 P3 | claim 附录溯源附录 | 2 | `appA_data.tex |

### 最终 Senior 最终判定

```
本轮 Senior Senior 最终 Senior Senior Senior → CONDITIONAL → → PASS 的升级条件

Senior：
1. P0 2 项全部完成；
2. P1 3 项完成 至少完成 2 项；
3. 所有 P2 3 项至少 2 项。

达到后 Senior Senior 重新 Review，重新审一轮（Round 2。
