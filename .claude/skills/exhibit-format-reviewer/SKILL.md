---
name: exhibit-format-reviewer
description: 图表/表格格式与数据正确性审查。对 LaTeX XeLaTeX 研报中的 TikZ/pgfplots/tabularx/longtable 等所有 exhibit 执行投行级硬门槛审查：颜色宏污染/文字不可见、legend-切片/柱色语义一致、Overfull \(\hbox >20pt\) 清零、数值与正文及表格交叉一致、标签无裁切/重叠、pgfplots cycle list 正确、fontawesome 宏 fallback 阻断、重复图表清理。输出分级 Reviewer 报告并给出精准的 LaTeX 代码级修复建议。
---

# Exhibit Format & Correctness Reviewer

可复用的投行级图表/表格格式 + 正确性审查流水线。覆盖所有 LaTeX/XeLaTeX exhibit（TikZ 架构图/pgfplots 统计图/堆叠柱·饼·散点·气泡/tabularx 表/longtable 附录表/exhibitbox 外框）。

## When to Use

- 用户说"图表看起来有问题"、"这个蓝色块没有文字"、"颜色不对"、"表格超出边界"。
- 用户上传了 PDF 截图并明确要求"帮我审查一下图表格式/正确性"。
- LaTeX 一轮编译后，任何图表/表格的视觉检查环节（render review / visual QA）。
- Phase `Render Review`（equity-research skill 的写 → Render Review → Publish 阶段）。
- **不要用**于章节叙事结构、估值逻辑、投资观点审查——那些属于 `research-report-review` skill。

## 审查输入（必须先确认可用）

| Item | Required | Location |
|------|:---:|---|
| ① LaTeX 源文件（sections/ch*.tex，exhibitbox 环境内嵌的 tikz/tabularx/longtable） | ✅ | `<project>/sections/*.tex` |
| ② 模板 preamble（颜色宏、fontawesome5、tikz 全局 style、exhibitbox v6 双寄存器语义） | ✅ | `.agents/templates/preamble.tex` |
| ③ 编译日志（Overfull / Underfull 审计，fontawesome5 缺字 fallback 警告） | ✅ | `<project>/*.log` |
| ④ 用户提供的 PDF 截图（Image #2...#N）| 可选 | 用户消息附件 |
| ⑤ 同项目对应数据锚：表 5-1 财务数据、S-ID 来源注册表 | 可选 | `data/*.md` 或 sections 内联 |

如果 ① 缺失，先让用户提供 sections 目录或 `find -name "*.tex"` 定位；如果 ② 缺失，**必须**读取 preamble 再下任何颜色相关的结论。

## 审查清单（硬顺序，从上到下，任何 FAIL 即 BLOCK）

### 层级一：可见性 & 颜色硬门槛（BLOCK 级，任何 FAIL = 不可发布）

**V-1 fill=text 同色导致的"深蓝空块"病（TikZ 颜色宏继承污染）**
  - 扫描所有 `\tikzset`/`[` style 定义，识别含风险色（riskamber/riskred 等）的 style：`ashare`、`ashar`、`bal`、`subp` 等。
  - **触发模式**：父节点或 `\draw[->, navy]` 路径通过作用域把 `color=...`（`\textcolor` 的简写）覆盖到相邻子孙节点的 text。
  - **修复标准（双保险，缺一不可）**：
    1. style 定义中必须把颜色写死：`fill=white, draw=navy, text=deepnavy` 而不是 `fill=#1!8, color=navy`。
    2. 每个具体节点（A1~A6、Pool B/D 等）**逐节点显式**再写一遍 `fill=white, draw=navy, text=deepnavy`。
  - **覆盖的典型图**：ch01 图 1-2 资金传导、ch03 图 3-1 产业链七层、ch04 图 4-2 CXL 拓扑、ch05 图 5-2 供需桥接 BAL 块。

**V-2 fontawesome5 宏 fallback 成裸文本（`aExclamationTriangle` 病）**
  - `grep -rn "\\\\fa[A-Z]" sections/*.tex` 找出所有 `\faExclamationTriangle`、`\faCloud`、`\faYenSign`、`\faFlagCheckered` 等符号。
  - 任何在 PDF 中渲染为 `aExclamationTriangle`、`aCloud`、`aYenSign` 的符号 = **必须立即修复**。
  - **根因**：`\usepackage[fixed]{fontawesome5}` 的 fixed 选项 + xeCJK 下 Times New Roman 缺字 → `\faicon{exclamation-triangle}` 的破折号寻址失败，宏 fallback 成字符串前缀 `a` + camelCase 名称。
  - **修复（preamble 全局兜底 + 节点内双写）**：
    1. preamble 末尾加：`\def\faExclamationTriangle{\ensuremath{\blacktriangle}\kern-0.25em}`（或 `\faIcon[regular]{exclamation-triangle}`，注意命名空间从 `\faIcon` 走，从不走 `\fa` 驼峰变体）。
    2. 表/图里关键显式节点（如 ch03 L72 keystat、ch06 L107 国产HBM行首）写 `$\triangle$` math 版兜底。
  - **必须逐处核实**：用户截图中出现 `aExclamationTriangle` 字样 = BLOCK，不接受"再编译试试"。

**V-3 文字裁切（节点 minimum height 不足 / text width 不足 / resizebox 缩放不足）**
  - 扫描每个 style 的 `minimum height` × 行数 × 行距。规则：1 行中文 = `>= 0.85cm`（inner sep 2pt 时）；2 行 = `>= 1.1cm`；3 行 = `>= 1.4cm`。
  - `resizebox` 缩放比 < 0.85 触发告警（< 0.80 强制重排：加文字折行、减小字级、加宽 text width）。
  - **典型病**：ch02 图 2-1 `subp` 框首字被顶边切（`minimum height 0.8cm` 不够）、ch05 图 5-2 需求卡片右边 "补偿需求 +25%" 6 字整体被吞进右边框（`text width 3.2cm resize 0.80 × 卡片`）、ch10 图 10-1 R1 气泡顶部 "HBM ASP -30%" 2 行上半 2mm 被切（circle 内切正方形 = `size/√2`，三行字高 1.44cm 必须 > 内切边长）。
  - **FAIL 判定**：任何 1 字被裁切 = BLOCK。

### 层级二：语义正确性（SIGNIFICANT 级，不影响阅读但破坏专业信用）

**S-1 legend 颜色 ↔ 渲染图形颜色不一致（饼切片 swap、pgfplots cycle 单 addplot 全染一色）**
  - **饼图**：每张饼按角度从 `\def\a{90}` 起算，**每个 scope 必须首行重写 `\def\a{90}`**（不继承前一个 scope）；然后按 `fill=... slice={deg}` 顺序逐条对照 legend 行的颜色。
  - 特别陷阱：legend tabular 的 `\cellcolor{riskred!60}` 必须与对应 slice 的 `fill=riskred!80` 是同色系基色（riskred ≠ accentblue ≠ nvgreen）。**任何图实际颜色与 legend 不同 = 读者会完全读错数据 = SIGNIFICANT。**
  - **pgfplots 横/柱图**：`cycle list={{riskred!60}, {accentblue!60}, ...}` 必须配套 `\addplot` 条数 = cycle list 条数。如果只有 1 条 `\addplot` 但有 N 个 bar，所有 bar 全染 cycle[0] = **FAIL。修复拆成 N 个 `\addplot[fill=<color>]`**。
  - **散点/气泡图**：Tier 1 圆点 fill=`navy!30` 视觉上接近白灰，legend tabular 填色应与圆点描边同（`draw=deepnavy, fill=navy!65`）。legend 实际色块必须肉眼匹配最粗描边色。

**S-2 数值交叉一致性（表 ↔ 柱 ↔ 正文 × 10× 单位陷阱）**
  - **模式库（已知陷阱）**：
    1. 表 5-1 "420--440 亿美元" vs 图 5-1 Samsung 柱高 $62\$B$（620 亿美元）= **不匹配（差 180 亿 = 40%）**。
    2. 表 5-1 YMTC "3.5--4.5 亿美元" vs 图 5-1 YMTC+CXMT 叠加 $9\$B$（90 亿）= **10× 数量级冲突（最严重的一类）**。
    3. 柱上 `nodes near coords` 与 `symbolic y coords` 顺序错位（图 7-1 长电柱顶标 1,150，兆易标 890）。
  - **审查流程**：取图表中所有金额/市值/百分比数字，逐一与最近的表格对应行做 `±15%` 容差检查。**超容差 = SIGNIFICANT，差 10× = BLOCK。**
  - **单位标注规则**：Capex 使用 `\$B`（Billion USD）与正文「亿美元」（100M USD = 0.1B）必须全文统一，不允许混用 "亿美元" 与 "$B" 又不做 `×10` 换算说明。

**S-3 图表重复编号（两个 `\begin{exhibitbox}[图 5-1 ...]`）**
  - `grep -oE "图 [0-9]+-[0-9]+" sections/*.tex | sort` → 任何编号出现两次 = **BLOCK（读者交叉引用全崩）**。
  - 保留规则：选柱上有数字标注、数据更新的那一版（版本 B > 版本 A）。

### 层级三：版式 & 空间（MINOR 级，影响专业观感）

**L-1 Overfull \(\hbox > 20pt\) 清零（投行硬门槛）**
  - **审计命令**（从 .log 提取）：
    ```
    grep -oE "[0-9]+\.[0-9]+pt too wide" main.log | grep -oE "^[0-9]+\.[0-9]+" | sort -rn -u | awk '$1>20'
    ```
  - **FAIL 计数 > 0 = BLOCK**。10–20pt 为宽松 PASS；<10pt 完全忽略。
  - **修复库（按匹配度从高到低）**：
    1. 中英文混排的 `/` → `\slash`（YMTC/CXMT → YMTC\slash CXMT）。
    2. 中英文混排的 `+` → `\allowbreak+\allowbreak`（DRAM+SRAM → DRAM\allowbreak+\allowbreak SRAM）。
    3. p 列内 `\\` → `\newline`（p 列把 `\\` 当行终止）。
    4. `\multicolumn{N}{l}` → `p{\dimexpr\sum(col_w)+2(N-1)\tabcolsep\relax}` 写死硬宽。
    5. 首列汉字数超出 p{cm}：从 `p{1.8cm}` 精准调到 `p{N字×字宽+2em}`。

**L-2 元素重叠（象限标签十字交汇、气泡重叠、callout 截断）**
  - **图 8-1 四象限标签典型**：四条标签 `above right/left` 全部锚在同一点 (5.5,5.5) → 中心十字交汇点 4 行文字相互覆盖。**修复：把四条锚分别移到 (8.3,8.3)/(2.7,8.3)/(2.7,2.7)/(8.3,2.7) 各象限中心。**
  - **图 10-1 气泡重叠**：两两气泡中心距离 < 两半径之和 = 视觉融合。修复：各气泡 center 微调 0.3–0.5 坐标；legend 移到不覆盖 R1/R2。
  - **图 2-1 subp 三重叠框**：`\foreach \y {...} \node[subp=...] {\strut}` 先画 3 个空占位，再写 2 个实 subp → 实空叠在一起视觉毛躁。**修复：弃用 `\foreach` 空占位，只在实际文本位置画实心框。**

### 层级四：观察项（NOTE 级，可不修但写入报告）

- p 列中 `表 8-3` 列首有换行破字（B+A 刻度写成 "B+A" 实际应 "B+/A"）。
- 图 3-1 L6 整机集成价值占比从 "-" 改为 "毛利 <2%，不计链上利润" 的明确说明（避免歧义）。
- X 轴辅助刻度线缺失（25%/75% 分位无刻度 → 加细虚线）。

## 严重级别定义

| 级别 | 含义 | 发布要求 |
|---|---|---|
| **BLOCK** | 读者直接看错结论（颜色 swap、10× 数量级错、文字完全看不见） | 必须修复后才能发布 |
| **SIGNIFICANT** | 专业度受损（数据差 >15%、legend 标注不一致、重复图） | 合入下一版 |
| **MINOR** | 版式毛躁（裁字 1pt 内、留白不均、线细） | 锦上添花 |
| **NOTE** | 潜在的下一轮优化项 | 不阻塞 |

> 注意：BLOCK 级 **至少包含** V-1/V-2/V-3 全 PASS + S-2 无 10× 错 + S-3 无重复 + L-1 >20pt 清零。

## 输出格式（严格一致，便于代码级修复）

```markdown
# Exhibit 格式 & 正确性审查 R<revision>

## 0. 审查总览（traffic-light × 所有图表）
| # | 图号 | 标题 | 可见性 | 语义 | 数据 | 版式 | 级别 |
|---|---|---|---|---|---|---|---|

## 1. 问题总分类（跨图共性 Bug，按 Class A/B/C/D/E 聚合）

### Bug Class A：<名称>
- 根因（代码级）
- 影响的图表清单
- 标准修法（含 LaTeX 代码片段）

### Bug Class B：<名称>
...

## 2. 分图逐项审查（每个 exhibitbox 一张，含：版式 Bug 清单/语义正确性/数据一致性）

### [图 x-y] 标题
#### 版式 Bug（N 项）
1. ID: 现象 → 根因 → 修复代码（精确到具体行号范围）
#### 语义正确性
#### 数据一致性（对照表 <x-y> + 正文 §<章节号>）

## 3. 修复优先级排序（P0 BLOCK / P1 SIGNIFICANT / P2 MINOR）
| ID | 图表 | 修复项 | 预计修改量 |
|---|---|---|---|

## 4. PASS 项（避免重复审查）
- 已核实正确的所有 exhibit 列表 + 说明

## 5. 二次验收硬标准（下轮 review 必须全满足）
1. Overfull \(\hbox > 20pt\) COUNT=0
2. 视觉无深蓝空块（对比度 >4:1，WCAG 最低）
3. legend ↔ 切片/柱色 语义 100% 一致
4. 表 ↔ 图单位一致、数值 ±15%（单位换算必须显式披露）
5. 任何图元含字符的框 >= 0.5em 留白（无裁切）
```

输出位置：`<project>/governance/exhibit_format_review_R<N>.md`（**绝对不可**落入 `data/` 白名单、`sources/broker-reports/` PRIMARY 目录）。

## 修复顺序纪律（从根上到叶子）

```
P0-00 preamble 全局兜底（fontawesome 宏定义 / style 颜色死硬）
  ↓
P0-01 重复图表清理（删旧版 / 合并重编号）
  ↓
P0-02 Class A（空蓝块 / fill=text 同色 —— 影响图最多的共性病）
  ↓
P0-03 Class B（aExclamationTriangle fallback 乱码 —— 读者可见的 "明显坏了"）
  ↓
P0-04 S-2 数值/单位一致性（最严重的实质错误）
  ↓
P0-05 S-1 颜色 swap（饼切片 / pgfplots cycle list）
  ↓
P0-06 V-3 裁切（subp / BAL / 气泡 / 卡片）
  ↓
P0-07 L-2 元素重叠（象限标签 / 气泡 / callout）
  ↓
P0-08 L-1 Overfull >20pt 清零
  ↓
二遍 XeLaTeX → Overfull >20pt 计数断言 → 视觉核对 → SYNC push
```

## 与其他 skill 的分界

| 需求 | 对应 skill |
|---|---|
| 章节叙事/估值逻辑/合规来源 | `research-report-review` |
| **图表/表格格式 + 正确性（本 skill）** | `exhibit-format-reviewer` |
| 估值模型算术 / 区间半宽 / 去单点 | `valuation-auditor` |
| 来源治理 / S-ID 可追溯 / C 级主张零进入估值 | `source-governance-analyst` |
| 乐观偏差 / 卖方 vs AStock 分歧 / 概率加权 | `contrarian-analyst` |

## 约束（继承全仓库永久安全规则）

1. **Git push 必须 `--force-with-lease`，禁裸 `--force`**。
2. 治理白名单：`data/*.md/json`、`completion_audit_manifest.*`、`_r<N>_*` —— **绝对不可修改、不可 staged**。
3. `sources/broker-reports/` PRIMARY 目录不可变。
4. 任何对外发布路径（sourcenote、日志、commit message）**绝对不泄露 PDF 的绝对路径**。
5. 白名单零触碰断言：`git status --porcelain` 的 staged 文件中 **不得** 出现 `data/` 前缀、`sources/broker-reports/` 前缀，也不得出现 `_r\d+_`。

---
**Skill Maturity**: v1.0（实战于 AI 存储产业链研报 20260624 版，已识别 7 Class × 15 Bug × 修复 10+ 张图表 20+ 个节点）
**Design Goal**: 后续所有 LaTeX 研报的 Render Review 阶段默认调用，形成 "写 → 编译 → reviewer → 修 → 再编译 → 发布" 的工程化闭环。
