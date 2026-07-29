# Exhibit 格式与正确性审查 · R1

- 项目：中国船舶（600150.SH）深度研究
- 审查日期：2026-07-22
- 审查范围：49 个 `exhibitbox`、50 个 `tabularx`、5 个 `longtable`、4 个 TikZ；PDF 50 页
- Overfull 审计：修复前最大 77.34453pt；修复后最大 0.24898pt；`>20pt COUNT=0`
- FontAwesome 宏：0 处
- 结论：✅ `PUBLISH READY`；0 BLOCK / 0 SIGNIFICANT / 0 MINOR，1 NOTE

## 0. 审查总览

| 载体 | 文件与展项 | 视觉 | 数据/单位 | 版式 | 结论 |
|---|---|---:|---:|---:|---|
| English Abstract | `sections/abstract.tex` | PASS | PASS | PASS | 长数字串已改为可断行句式 |
| 投委会摘要 | `ch01`：核心估值、下一结果门槛、三情景动作 | PASS | PASS | PASS | 价格、目标、区间和动作一致 |
| 证据治理 | `ch02`：证据金字塔、关键主张治理 | PASS | PASS | PASS | 来源层级与估值许可清晰 |
| 重组边界 | `ch03`：时间线、股本桥、三口径 | PASS | PASS | PASS | TikZ 节点与连线可见 |
| 公司能力 | `ch04`：船厂、子公司、唯一估值母体 | PASS | PASS | PASS | 已消除章节末尾孤页 |
| 行业周期 | `ch05`：周期表、国家指标图、需求锚 | PASS | PASS | PASS | 长船型名已允许自然断行 |
| 产业链 | `ch06`：链条图、经济性、竞争、分类 | PASS | PASS | PASS | TikZ 宽度收敛，无裁切 |
| 订单兑现 | `ch07`：漏斗、收入桥、利润瀑布 | PASS | PASS | PASS | 图形连通，订单与收入单位不混用 |
| 财务质量 | `ch08`：财务进展、利润锚、营运资金、现金桥 | PASS | PASS | PASS | OCF、NP、亿元口径一致 |
| 盈利预测 | `ch09`：分析基线、PBT桥、三情景、敏感性 | PASS | PASS | PASS | 宽表已重构为页内 7 列 |
| 卖方预期 | `ch10`：券商矩阵、预期差 | PASS | PASS | PASS | 冗余质量列移入 source note，消除溢出 |
| 估值 | `ch11`：最终总表、方法、情景、隐含预期、多锚 | PASS | PASS | PASS | 33.02/33.07/+0.15% 一致 |
| 二级市场 | `ch12`：行情快照、执行纪律、结果日顺序 | PASS | PASS | PASS | 未制造技术位或缺失指标 |
| 风险与催化 | `ch13`：风险矩阵、催化剂、动作规则 | PASS | PASS | PASS | 概率、阈值、敏感性可读 |
| 来源附录 | `appA`：来源表、复核索引 | PASS | PASS | PASS | 仅有 0.249pt 非实质对齐溢出 |
| 模型附录 | `appB`：PBT-EPS、税率归属、H1残余、二维敏感性 | PASS | PASS | PASS | 模型单位与正文一致 |
| 边界附录 | `appC`：术语口径、零信用清单 | PASS | PASS | PASS | 免责声明与零计价边界完整 |

## 1. Bug Class 聚合与闭环

### Class H：Overfull 与窄列溢出

- `sections/abstract.tex` 原有不可断行的英文数字串，修复前 49.76746pt；已改为逗号分隔和短句，复核为 0。
- `sections/ch05_cycle.tex` 原 `Capesize/VLOC/Kamsarmax` 造成 20.44832pt；已改为中文顿号分隔，复核为 0。
- `sections/ch06_chain_competition.tex` 原 TikZ 横向尺寸造成 77.34453pt；节点宽度由 2.5cm 降至 2.1cm、间距由 0.55cm 降至 0.30cm，复核为 0。
- `sections/ch09_forecast.tex` 原三情景 8 列表右侧裁切；已拆除叙事列并重构为 7 列。
- `sections/ch10_consensus.tex` 原券商矩阵“质量”列裁切；质量语义移入 source note，表格重构为 7 列。

### Class F/G：裁切、重叠与孤页

- `sections/ch04_company_capability.tex` 章节末句曾单独占一页；删除重复尾段后，章节自然收口，无孤页。
- `sections/ch06_chain_competition.tex` 初稿 TikZ 使用单反斜线换行，触发 undefined control sequence；改为 `\\`，同时缩窄节点后文字和箭头均未交叉。
- `main.tex` 增加 `amsmath`，解决 `equation*` 环境缺失的构建阻断。

### Class A/B/C/I/J/L/M：未触发

- 无 FontAwesome 宏或字体 fallback。
- 无 fill/text 同色节点；四张 TikZ 的文字、边框和填充对比清晰。
- 无 `-|` / `|-` 路径语义风险；箭头均落在目标节点，未切割非目标文字。
- 无饼图图例、pgfplots cycle-list 或散点图颜色映射错配。
- 无重复 exhibit 标题；同类表格边界和节点对齐一致。

## 2. 分 exhibit 复核结论

- `ch01`（3）：核心估值与动作、下一季度盈利与质量门槛、情景/条件/监测等价行为——PASS。
- `ch02`（2）：证据金字塔与允许用途、关键主张治理——PASS。
- `ch03`（3）：吸收合并关键节点、股本与每股口径桥、三种财务口径不可拼接——PASS。
- `ch04`（3）：主要船厂能力地图、主要子公司经营观察、唯一估值母体与观察节点——PASS。
- `ch05`（3）：全球造船周期仪表盘、中国造船三大指标、需求锚/船型/脆弱点——PASS。
- `ch06`（4）：需求锚到现金、价值链经济性、产品竞争、全链条分类——PASS。
- `ch07`（3）：订单漏斗、收入桥、利润瀑布——PASS。
- `ch08`（4）：财务进展、收入利润锚、营运资金、现金转化——PASS。
- `ch09`（4）：分析基线、Base盈利桥、三情景、二维敏感性——PASS。
- `ch10`（2）：公开券商预测、共识与分歧——PASS。
- `ch11`（5）：最终估值总表、方法桥、三情景、预期桥、多锚权重——PASS。
- `ch12`（3）：行情快照、执行纪律、结果日更新——PASS。
- `ch13`（3）：风险热度、催化剂、投委会规则——PASS。
- `appA`（1）、`appB`（4）、`appC`（2）：来源、模型与边界附录——PASS。

## 3. 修复优先级与状态

| 优先级 | 修复项 | Bug Class | 状态 |
|---|---|---|---|
| P0 | XeLaTeX undefined control sequence / missing equation environment | F/H | CLOSED |
| P0 | TikZ 77.34pt 与英文 49.77pt Overfull | H | CLOSED |
| P0 | ch09/ch10 宽表右侧裁切 | H/F | CLOSED |
| P1 | ch04 单句孤页 | G | CLOSED |
| P3 | appA longtable 0.249pt alignment | NOTE | ACCEPTED；低于 20pt 硬门槛且肉眼不可见 |

## 4. PASS 清单

- 两遍 MacTeX XeLaTeX：0 error；最终项目 CLI 构建成功，50 页。
- Overfull `>20pt`：0。
- 可见性：所有 TikZ 节点 fill/text 对比合格，无空色块。
- 路径：四张 TikZ 连通，箭头未穿越非目标文字。
- 数值：现价、股本、市值、盈利、目标价、区间、订单和国家 DWT 单位与正文/表/图一致。
- 裁切：抽检封面、摘要、目录、四张 TikZ、宽表、最终估值、风险矩阵与尾页，均无边界裁切。
- 语义：图形不把集团、军品、卫星公司或需求锚误表示为 600150 的收入/估值信用。

## 5. 二次验收硬标准

1. Overfull `>20pt COUNT=0`：PASS。
2. 节点 fill/text 对比度与可见性：PASS。
3. 图例/颜色语义：N/A；无需要映射的多序列图例。
4. 表/图/正文数值与单位：PASS。
5. 文字、节点和表格边界安全间隙：PASS。

