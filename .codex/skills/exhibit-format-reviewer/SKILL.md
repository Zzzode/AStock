---
name: exhibit-format-reviewer
description: 通用投行级研报图表/表格 · 格式 + 正确性审查 skill。面向任意 LaTeX XeLaTeX 研究报告（行业深度 / 单票点评 / 图表手册 / 投委会概要 / 估值年报 / 压力测试等），执行 exhibitbox 环境全量扫描（TikZ/pgfplots/tabularx/longtable），覆盖可见性、颜色宏污染、fontawesome5 宏 fallback、legend 语义匹配、数值单位交叉一致、重复图表、裁切重叠、Overfull hbox 硬门槛 8 大维度，输出分级 BLOCK / SIGNIFICANT / MINOR / NOTE 审查报告并给出 LaTeX 代码级修复。独立于任何具体项目，不包含任何 AI 存储 / 半导体 / PCB 的硬编码。
---

# Exhibit Format & Correctness Reviewer · 通用投行级图表审查

**Scope**: 所有 XeLaTeX 编译的 LaTeX 研报，无论行业、主题、篇幅。  
**Design Goal**: 通用、无行业硬编码、可复用、输出可追踪。  
**Role companion**: `.agents/team/exhibit-format-reviewer.md`（审查员人格与详细检查清单）。

---

## When to Invoke

✅ **正确用法**（必须显式提供 `<project_root>`）：
```
/exhibit-format-reviewer  workspace/research/PCB-investment-2026Q2/
/exhibit-format-reviewer  workspace/research/quantitative-strategy-2026/
/exhibit-format-reviewer  <任意研报根目录，包含 sections/*.tex + main.tex>
```

✅ **自然语言触发**：
- "帮我审查这份研报的所有图表格式/正确性"
- "图表看起来有问题，做个全面的 reviewer"
- "render review / visual QA"
- 配合 `equity-research` skill 的 Render Review → Publish 阶段自动调用

❌ **不要用于**：
- 纯叙事 / 估值逻辑 / 合规来源审查 → `research-report-review`
- 纯估值算术 / 区间半宽 / 去单点 → `valuation-auditor`
- S-ID 可追溯 / 来源治理 → `source-governance-analyst`
- 乐观偏差 / 卖方 vs AStock 分歧 → `contrarian-analyst`

---

## 工作流（通用，对任意 `<project_root>`）

```
Step 1. 项目发现
  └─ 输入：<project_root>（绝对 or 相对）
     - 若缺：遍历 workspace/research/*/ 找最新 main.tex
  └─ 必须定位以下项，缺失告警但继续：
     (a) main.tex        → 章节结构 & preamble 入口
     (b) sections/*.tex  → 所有 exhibitbox 载体
     (c) *.log           → 若不存在则提示先跑 xelatex
     (d) <preamble>      → main.tex 中 \input{...preamble.tex} 路径
     (e) main.pdf / 截图 → 若有，做代码×视觉交叉校验（可选）
```

**Step 1 代码级发现命令**（项目无关，纯 bash）：
```bash
# 1. 列所有章节
find "$PROJ" -path "*/sections/*.tex" -type f | sort
# 2. 定位 preamble（从 main.tex 解析 \input 路径）
grep -oE '\\input\{[^}]+\}' "$PROJ/main.tex" | head -5
# 3. 列所有 exhibitbox 环境编号
grep -nE '\\begin\{exhibitbox\}\[图 [0-9]+-[0-9]+'  "$PROJ"/sections/*.tex
grep -nE '\\begin\{exhibitbox\}\[表 [0-9]+-[0-9]+'  "$PROJ"/sections/*.tex
# 4. 提取 Overfull 审计
grep -oE 'Overfull [^[]+ [0-9]+(\.[0-9]+)?pt too wide' "$PROJ"/*.log
# 5. 提取 fontawesome 宏
grep -rnE '\\fa[A-Z][a-zA-Z]+' "$PROJ"/sections/*.tex
```

```
Step 2. 枚举所有 exhibit（图 + 表 + 附录表）
  └─ 为每个 \begin{exhibitbox}[<编号> <标题>] 建立独立审查卡片：
     ID = 图 3-1 / 表 5-2 / 表 A-1 等
     File = 源文件 + 行号范围（自动 grep 匹配 \end{exhibitbox} 闭合）
     Type = tikz / pgfplots / tabularx / longtable / mixed
```

```
Step 3. 执行 8 大维度审查（见下一节）
  └─ 每个卡片单独过 8 维度 → 每条问题带
     - 严重级 (BLOCK/SIGNIFICANT/MINOR/NOTE)
     - 精确 file:line
     - 根因（代码级，用 Bug Class 名称）
     - 修复建议（含可直接 Copy→Paste 的 LaTeX snippet）
  └─ 聚合：按 Bug Class 跨 exhibit 去重、聚类
```

```
Step 4. 输出审查报告（Markdown）
  └─ 写入：<project_root>/governance/exhibit_format_review_R<N>.md
     （N = 若已有同目录 R<N> 存在，N+1；否则 R1）
  └─ 格式见 §输出格式
```

```
Step 5. [可选] 如果用户要求 "修复" 而非 "只审查"
  └─ 按 §修复顺序纪律 从 BLOCK→SIGNIFICANT→MINOR 逐类应用
  └─ 每类修完跑一次 xelatex 校验
  └─ 最后：两遍 xelatex → Overfull >20pt 硬断言 → SYNC push
```

---

## 8 大维度审查清单（项目无关）

| # | 维度 | 严重级 | 检测方法 |
|---|---|---|---|
| V-1 | **可见性**：fill 与 text 颜色对比度 <4:1（深蓝空块） | BLOCK | 扫描 `style/.style={...fill=<X>, color=<Y>...}`：若 X 与 Y 是同色系（navy/deepnavy、riskamber!8+navy 等）→ FAIL；另逐节点检查 `text=...` 与 `fill=...` 显式冲突 |
| V-2 | **符号乱码**：fontawesome5 宏 fallback | BLOCK | 所有 `\fa<大写字母开头>` → 在 preamble 里查是否 `\usepackage{fontawesome5}` + xeCJK 下的命名空间；查 .log 中 `LaTeX Font Warning` → 若有 → FAIL |
| V-3 | **文字裁切**：minimum height 不足 / text width 不足 / resizebox < 0.80 | BLOCK | 解析 style 的行数 × 行距 vs `minimum height`；`\resizebox{<ratio>}{!}` 的 ratio 下限检查 |
| S-1 | **语义色一致性**：legend ↔ 实际切片/柱色不匹配 | BLOCK（饼切片 swap）/ SIGNIFICANT（pgfplots cycle list 单色） | 饼图：`\def\a{90}` 角度起算 + scope 隔离验证；pgfplots：cycle list 条目数 vs `\addplot` 条目数；散点：dot fill % 匹配 legend cell fill % |
| S-2 | **数值单位一致性**：表 ↔ 图 ↔ 正文交叉 | SIGNIFICANT（±15% 不匹配）/ BLOCK（10× 数量级错） | 正则抽取所有金额 / 百分比数值，取同指标在三个载体的最近出现做容差校验；单位换算（亿 ↔ $B / ¥B / ¥亿）必须显式披露，未披露视为 FAIL |
| S-3 | **重复编号**：两个 exhibitbox 使用相同图号 | BLOCK | 全部 `图 表 X-Y` 编号频度排序 |
| L-1 | **Overfull hbox >20pt 计数** | BLOCK >0 | .log 正则提取 + 阈值过滤 |
| L-2 | **版式重叠**：节点坐标中心距离 < 两元素半宽之和 | MINOR（文字压边）/ SIGNIFICANT（核心结论覆盖） | tikz 节点坐标的 bounding box 对撞检查；散点气泡 / 四象限标签 / subp 框三层 典型模式 |

### Bug Class 库（通用，不绑定行业）

```
Class A: TikZ style 颜色宏污染（V-1 实现）
Class B: fontawesome5 宏 fallback 乱码（V-2）
Class C: legend ↔ 图形 颜色语义 swap（S-1 饼/柱）
Class D: 数值/单位 交叉不一致（S-2，含 10× 陷阱）
Class E: 重复 exhibit（S-3）
Class F: 文字裁切 （V-3，subp/气泡/卡片）
Class G: 版式元素重叠 （L-2，象限标签/气泡/callout）
Class H: Overfull hbox 超标 （L-1，中文+\slash+\allowbreak 修复库）
```

每个 Class 都配有通用 LaTeX 代码修复片段（见 §修复库），完全不依赖具体行业。

---

## 修复代码片段库（通用 LaTeX）

> 以下片段不包含任何 AI 存储/半导体/PCB 的行业词，可直接复制到任意研报的 preamble 或 exhibit。

### A-1 节点 style 颜色硬写（双保险）
```latex
% ❌ 旧（风险色污染）：ashare/.style={draw=riskamber, fill=riskamber!8, color=navy}
% ✅ 新（写死）：
ashare/.style={rectangle, rounded corners=4pt, draw=navy, fill=white,
  text width=2.0cm, align=center, minimum height=1.0cm,
  font=\bfseries\small, text=deepnavy, line width=0.8pt}
% 然后每个节点显式再写（双保险第二重）：
\node[ashare, fill=white, draw=navy, text=deepnavy] (A1) {文本};
```

### B-1 fontawesome5 全局兜底（preamble 尾部）
```latex
% 当 xeCJK + fontawesome5[fixed] 因缺字 fallback 成 aExclamationTriangle 时生效
\usepackage{etoolbox}
\ifcsundef{faExclamationTriangle}{
  \def\faExclamationTriangle{\ensuremath{\blacktriangle}\kern-0.25em}
}{}
\ifcsundef{faCloud}{
  \def\faCloud{\ensuremath{\clubsuit}\kern-0.1em}
}{}
% 继续按需添加 \faYenSign / \faFlagCheckered / \faMemory 等兜底
```

### C-1 饼图 scope 隔离（避免角度继承）
```latex
% 每张饼 scope 首行强制 \a=90
\begin{scope}[xshift=6.0cm]
  \def\a{90}  % ← 显式重置，不依赖外部
  \filldraw[fill=<C1>, ...] [slice={<D1>}]; \pgfmathsetmacro\a{\a+<D1>}
  ...
\end{scope}
```

### C-2 pgfplots 横柱分类色（避免 cycle list 单色）
```latex
% ❌ 旧：cycle list=6 色 + 1 条 addplot → 全染第一色
% ✅ 新：按类别拆 N 条 \addplot
\pgfplotscreateplotcyclelist{mktcap}{{fill=navy!30,draw=navy},{fill=nvgreen!30,draw=nvgreen},...}
\begin{axis}[cycle list name=mktcap, ...]
  \addplot+[fill=navy!30, draw=navy]  coordinates {(值, "标签1") (值, "标签2")}; % 设计/IP
  \addplot+[fill=nvgreen!30, draw=nvgreen]  coordinates {(值, "标签3") (值, "标签4")}; % 封测
  ...
  \legend{设计IP, 封测,...}
\end{axis}
```

### F-1 circle 节点内三行文字不溢出（内切正方形公式）
```latex
% 字高 h × 行数 N × 行距 1.2 ≤ minimum_size / √2
% 例：三行 10pt 字 ≈ 1.1×3×1.2 = 3.96cm > 2.2/1.414 = 1.56cm × 错
% ✅ 修正：
riskR/.style={circle, ..., minimum size=2.4cm, inner sep=3pt,
  align=center, font=\scriptsize\bfseries, text=deepnavy}
% 或压缩行距：
\node[riskR] {R1\\[-0.15em] HBM ASP -30\%\\[-0.15em] 供过于求};
```

### H-1 Overfull hbox 分级修复（从稳到激进）
1. 中英文混排的 `/` → `\slash` （例：YMTC/CXMT → YMTC\slash CXMT）
2. `+` → `\allowbreak+\allowbreak`（例：DRAM+SRAM → DRAM\allowbreak+\allowbreak SRAM）
3. p 列行内换行 `\\` → `\newline`
4. `\multicolumn{N}{l}` → `p{\dimexpr\sum(col_w)+2(N-1)\tabcolsep\relax}` 硬宽
5. 首列字宽超 p{cm}：p{1.8cm} → 精准按 字×字宽+2em 调节

---

## 分级定义（严格复用）

| 级别 | 发布阻塞 | 典型场景 |
|---|---|---|
| **BLOCK** | 必须修 | 读者直接看错结论：饼色 swap 全错 / 10× 单位 / 文字完全隐形 / 表号重复 / Overfull >20pt >0 |
| **SIGNIFICANT** | 合入下一版 | 专业度受损：数据差 >15%、legend 填色不匹配、pgfplots 单色、节点轻微裁切 |
| **MINOR** | 锦上添花 | 字间距微差、留白不均、线宽略细、辅助刻度缺失 |
| **NOTE** | 不阻塞 | 潜在优化（例：某轴标签日后可改竖排） |

---

## 输出格式（通用 Markdown）

```markdown
# Exhibit 格式 & 正确性审查 · R1
项目: <project_root 的 base name>
审查日期: <YYYY-MM-DD>
覆盖: 图 N 张 · 表 M 张 · 附录表 K 张

## 0. 审查总览（traffic-light 矩阵）
| # | 编号 | 标题 | 文件:行 | 类型 | 可见性 | 语义 | 数据 | 版式 | 严重级 |
|---|---|---|---|---|---|---|---|---|---|

## 1. 问题分类总览（Bug Class A-H 跨 exhibit 聚合）
### Bug Class <字母>：<名称>
- 根因（LaTeX 代码级通用解释）
- 影响的 exhibit 清单：图 X-Y / 表 X-Y ...
- 标准修法：（§修复代码片段库对应项引用 + 具体 LaTeX 代码）

## 2. 分 exhibit 逐项审查
### [图 X-Y] <标题>
#### 版式 Bug（N 项）
1. <ID>: <现象> → <根因 Bug Class> → <精确 file:line 范围> → <修复 LaTeX 片段>
#### 语义正确性
#### 数据一致性（对照最近的表 X-Y + 正文 §X.X 交叉）

## 3. 修复优先级排序（P0 BLOCK / P1 SIGNIFICANT / P2 MINOR）
| ID | exhibit | 修复项 | 估算修改量 | Bug Class |
|---|---|---|---|---|

## 4. PASS 项（已全量核实无问题 · 避免重复审查）
- 列所有 PASS 的图 × / 表 × + 说明

## 5. 二次验收 5 条硬标准（下一轮审查必须全满足）
1. Overfull \(\hbox > 20pt\) COUNT=0
2. 可见性：所有节点 fill 与 text 对比度 >4:1（WCAG 最低）
3. 语义色：legend tabular fill % ↔ 各切片/柱最外描边色 肉眼 100% 匹配
4. 数据：表 ↔ 图 ↔ 正文同一指标 ±15% 容差内，亿/$B 单位换算全文显式披露
5. 裁切：所有含字符的元素 bounding box 外侧 ≥ 0.5em 留白
```

---

## 修复顺序纪律（通用 · 从根到叶子）

```
P0-00 preamble 全局兜底（Class B fontawesome / Class A 颜色宏全局）
  ↓
P0-01 重复 exhibit 清理（Class E：删旧版 / 重编号）
  ↓
P0-02 Class A 空蓝块 fill=text 同色（影响图最多的共性病）
  ↓
P0-03 Class B aExclamationTriangle fallback 乱码（"明显坏了"）
  ↓
P0-04 Class D 数值/单位交叉一致性（最严重的实质错）
  ↓
P0-05 Class C 颜色语义 swap（饼切片 / pgfplots cycle list）
  ↓
P0-06 Class F 裁切（subp / 气泡 / 卡片）
  ↓
P0-07 Class G 元素重叠（象限标签 / 气泡 / callout）
  ↓
P0-08 Class H Overfull >20pt 清零
  ↓
二遍 XeLaTeX → Overfull 硬断言 → 视觉核对 → Git SYNC push
```

---

## 约束（继承全仓库永久安全规则）

1. **Git push 必须 `--force-with-lease`（禁裸 `--force`）**。
2. 治理白名单（**绝对不可进入 staged**）：
   - `data/*.md` / `data/*.json`
   - `completion_audit_manifest.*`
   - `_r<N>_*`（文件名开头匹配正则）
3. `sources/broker-reports/` PRIMARY 目录不可修改（含任何子路径）。
4. 审查报告和 commit message 中**绝不泄露 PDF 的绝对路径**（只写 `main.pdf` / `<project>/main.pdf` 的相对路径）。
5. 审查报告的输出目录：**强制** `<project_root>/governance/`，绝不落入白名单或 PRIMARY。

---

## Skill 成熟度与演化

**v1.0**（首次入库）：
- 8 维度 × 8 Bug Class × 修复片段库 × 严格分级 × 标准输出模板
- 配套 `.agents/team/exhibit-format-reviewer.md` role 文件
- 已在 AI 存储产业链深度研报（20260624）实战验证：10 张图 × 8 章节识别 15 个问题 + 12 BLOCK 修复清单

**v1.1 Roadmap**：
- 自动化正则扫描脚本（bash/python）：自动枚举所有 exhibit → 输出 JSON 卡片
- Overfull 审计行 → 自动定位最窄列 / 最长词
- pgfplots cycle list 条目数与 `\addplot` 自动计数匹配

---
**调用方式**：在任何对话里写 `/exhibit-format-reviewer <研报路径>`。
