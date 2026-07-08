---
name: exhibit-format-reviewer
description: 通用投行级研报图表/表格 · 格式 + 正确性审查 skill。面向任意 LaTeX XeLaTeX 研究报告（行业深度 / 单票点评 / 图表手册 / 投委会概要 / 估值年报 / 压力测试等），执行 exhibitbox 环境全量扫描（TikZ/pgfplots/tabularx/longtable），覆盖可见性、颜色宏污染、fontawesome5 宏 fallback、路径连通性、legend 语义匹配、数值单位交叉一致、重复图表、裁切重叠、安全间隙、对齐一致性、视觉语义邻近、Overfull hbox 硬门槛 12 大维度，输出分级 BLOCK / SIGNIFICANT / MINOR / NOTE 审查报告并给出 LaTeX 代码级修复。内置 6 个视觉检测探针（路径连通性、箭头-文字交叉、动态高度级联、对齐一致性、窄列溢出、视觉语义邻近）。独立于任何具体项目，不包含任何 AI 存储 / 半导体 / PCB 的硬编码。
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

## 12 大维度审查清单（项目无关）

| # | 维度 | 严重级 | 检测方法 |
|---|---|---|---|
| V-1 | **可见性**：fill 与 text 颜色对比度 <4:1（深蓝空块） | BLOCK | 扫描 `style/.style={...fill=<X>, color=<Y>...}`：若 X 与 Y 是同色系（navy/deepnavy、riskamber!8+navy 等）→ FAIL；另逐节点检查 `text=...` 与 `fill=...` 显式冲突 |
| V-2 | **符号乱码**：fontawesome5 宏 fallback | BLOCK | 所有 `\fa<大写字母开头>` → 在 preamble 里查是否 `\usepackage{fontawesome5}` + xeCJK 下的命名空间；查 .log 中 `LaTeX Font Warning` → 若有 → FAIL |
| V-3 | **文字裁切**：minimum height 不足 / text width 不足 / resizebox < 0.80 | BLOCK | 解析 style 的行数 × 行距 vs `minimum height`；`\resizebox{<ratio>}{!}` 的 ratio 下限检查 |
| V-4 🆕 | **路径连通性**：TikZ `-|`/`|-` 操作符语义误用导致连线悬空 | BLOCK | 对每条使用 `-|`/`|-` 的路径：(1) 解析起点节点锚点预期坐标；(2) 解析操作符语义；(3) 验证终点是否落在目标节点；若终点偏差 > 0.3cm → FAIL |
| S-1 | **语义色一致性**：legend ↔ 实际切片/柱色不匹配 | BLOCK（饼切片 swap）/ SIGNIFICANT（pgfplots cycle list 单色） | 饼图：`\def\a{90}` 角度起算 + scope 隔离验证；pgfplots：cycle list 条目数 vs `\addplot` 条目数；散点：dot fill % 匹配 legend cell fill % |
| S-2 | **数值单位一致性**：表 ↔ 图 ↔ 正文交叉 | SIGNIFICANT（±15% 不匹配）/ BLOCK（10× 数量级错） | 正则抽取所有金额 / 百分比数值，取同指标在三个载体的最近出现做容差校验；单位换算（亿 ↔ $B / ¥B / ¥亿）必须显式披露，未披露视为 FAIL |
| S-3 | **重复编号**：两个 exhibitbox 使用相同图号 | BLOCK | 全部 `图 表 X-Y` 编号频度排序 |
| S-4 🆕 | **视觉语义邻近**：注释元素与不相关数据框共享基线造成误导 | MEDIUM | 检测注释元素（箭头、callout、统计框）的锚点 y 是否与不相关数据元素偏差 < 0.1cm 且水平距离 < 2.0cm |
| L-1 | **Overfull hbox >20pt 计数** | BLOCK >0 | .log 正则提取 + 阈值过滤；静态降级：窄列 en-dash 区间值 / CJK 字符串宽度估算 |
| L-2 | **版式重叠**：节点坐标中心距离 < 两元素半宽之和 + 箭头-文字交叉 | MINOR（文字压边）/ SIGNIFICANT（核心结论覆盖）/ BLOCK（箭头切割文字） | tikz 节点坐标的 bounding box 对撞检查；**扩展**：箭头路径线段与文本节点 bbox 的相交检测 |
| L-3 🆕 | **对齐一致性**：同类样式节点水平/垂直位置严重不对齐 | HIGH | 按 style 名称分组，计算右边缘 x 坐标标准差；若 std > 1.0cm 且该组应对齐 → FAIL |
| L-4 🆕 | **安全间隙**：元素间最小视觉距离 < 0.3cm | BLOCK (<0.1cm) / SIGNIFICANT (<0.3cm) | 对所有元素对计算 gap = 中心距 - 半径和；< 0.1cm 视觉等同重叠，< 0.3cm 肉眼感知为"接触" |

### 6 个视觉检测探针（详细算法）

#### Probe 1: tikz_path_connectivity_probe
**检测目标**：TikZ `-|`/`|-` 坐标操作符语义误用导致的连线悬空

**检测逻辑**：
```
扫描所有 \draw 命令中使用 -| 或 |- 的路径：
  对每条路径：
    1. 解析起点节点锚点（如 \h.south）的预期 y/x 坐标
    2. 解析 -|/|- 操作符的语义：
       - A-|B = 取 A 的 x + B 的 y
       - A|-B = 取 B 的 x + A 的 y
    3. 计算实际终点坐标
    4. 验证终点是否落在目标节点上：
       - 垂直连接场景：终点 y 与目标节点 y 偏差 > 0.3cm → FAIL
       - 一般场景：终点距目标节点边界 > 0.5cm → FAIL
```

**经典陷阱**：
```latex
% ❌ 错误：(SW1.north-|\h.south) 实际是 x=SW1.north.x, y=H.south.y
% 结果：在 Host 底部画了一条水平短线，终点悬空在 (2.0, -0.65)
% 距 SW1.north 的 y=-1.65 有 1.0cm 间隙！
\draw[->] (\h.south) -- (SW1.north-|\h.south);

% ✅ 正确：使用 |- 或显式路由
\draw[->] (\h.south) |- (SW1.north);
% 或
\draw[->] (\h.south) -- ++(0,-0.3) -| (SW1.north);
```

#### Probe 2: arrow_text_intersection_probe
**检测目标**：箭头路径穿越文本节点内部，直接切割文字

**检测逻辑**：
```
提取所有箭头路径（\draw[->] 或含 arrow style 的 \draw）的几何路径线段
提取所有文本节点的 bounding box (x, y, width, height)
对每条箭头：
  对每个非源/目标节点的 bbox：
    计算箭头路径线段与 bbox 的交集
    若交集长度 > 节点高度的 20% → FAIL（箭头切割文字）
特别关注：垂直箭头与同列子框的重叠
```

**典型案例**：图2-1中 TH1→CONCL 箭头（bend right=-30）沿 x=0 垂直下行，精确穿过 TH1_sub1（国产HBM≥2028）和 TH1_sub2（SK海力士55%+）的几何中心，穿越距离 = 子框高度 1.10cm

**修复方案**：使用正交路由绕过文字列
```latex
\draw[arrow] (TH1.south) -- ++(0, -0.35) -| ([xshift=2.5cm]CONCL.north west);
```

#### Probe 3: dynamic_height_cascade_probe
**检测目标**：text width 不足导致文字意外换行，节点实际高度 > minimum height，进而与下方元素碰撞

**检测逻辑**：
```
对每个 TikZ 节点：
  根据 text width、font size、文本内容（含 \\ 手动换行 + 自动换行估算）
  计算实际渲染高度：
    H_actual = ceil(estimated_lines) × line_height × font_size
  若 H_actual > minimum_height → 标记为「动态撑高节点」
  计算该节点底边与下方最近元素顶边的间隙
  若间隙 < 0.3cm → 标记为「级联碰撞风险」
```

**典型案例**：图1-1 D1 框 text width=2.3cm，内容「SK Hynix 良率 85%+\\B100/B200 放量」第二行自动换行变为 3 行，实际高度 ≈1.05cm > minimum height=1.0cm，底部 y=-2.85 与 OUT 框顶部 y=-3.05 间隙仅 0.02cm

#### Probe 4: alignment_consistency_probe
**检测目标**：同类样式节点的水平位置严重不对齐

**检测逻辑**：
```
按 style 名称对所有 TikZ 节点分组（如 ashar、subp、thesis 等）
对每组节点：
  计算每个节点的：
    - 左边缘 x_left = node_x - text_width/2（或 minimum_width/2）
    - 右边缘 x_right = node_x + text_width/2
    - 中心 x_center = node_x
  计算统计量：
    - std(x_left), std(x_right), std(x_center)
  若某组节点的右边缘标准差 > 1.0cm 且该组节点在视觉上应对齐 → FAIL
  特别标记：使用 right=of 相对定位但前置节点数量不同导致的阶梯状错落
```

**典型案例**：图3-1中 6 个 A 股映射标签（ashar 样式），因各层前置节点数量不同（L1 有 4 个、L2 有 3 个、L3-L6 有 2 个），A1 右边缘距 L1 左边缘 14.2cm，A3-A6 右边缘仅 8.4cm，最大水平偏差 5.8cm

#### Probe 5: narrow_column_overflow_probe
**检测目标**：窄列中含 en-dash 区间值或 CJK 字符串导致的溢出（纯静态分析，无需 .log）

**检测逻辑**：
```
对每个 p{<width>} 列定义：
  扫描该列所有单元格内容，识别已知超宽元素：
    (1) en-dash 区间值：\d+--\d+
        估算宽度：每个数字 ≈ 0.6 × font_size，en-dash ≈ 2 × 数字宽
        例："367--1224" ≈ (3+4)×0.6×fontsize + 2×0.6×fontsize = 9×0.6×fontsize
    (2) CJK 字符串：每字宽度 ≈ font_size × 1.0
    (3) 长英文专有名词
  对每个匹配项估算渲染宽度 W_est
  若 W_est > column_width × 0.95 → 标记为「列宽溢出风险」

对 multicolumn：
  计算实际跨越列的自然宽度：
    W_natural = Σ(col_width) + 2×(N-1)×tabcolsep
  若 multicolumn 指定的 p-width 与 W_natural 偏差 > 0.5cm → 标记为「multicolumn 宽度不匹配」
```

**典型案例**：表1-1 区间列 p{0.85cm}，但「367--1224」估算宽度 1.11cm，溢出 0.26cm；汇总行评级列「标配偏积极」4 个 CJK 字符估算宽度 0.98cm > p{0.85cm}

#### Probe 6: visual_semantic_proximity_probe
**检测目标**：视觉邻近造成的语义误导

**检测逻辑**：
```
对所有注释类元素（箭头、callout、统计框、sourcenote）：
  检查其视觉锚点（起点 y 坐标、中心 y 坐标）是否与不相关数据元素的基线/中心意外对齐：
    判定条件：
      (1) 注释元素的锚点 y 坐标与某数据框的锚点 y 坐标偏差 < 0.1cm（共享基线）
      (2) 两者在语义上无直接关联（通过节点名称和内容判断）
      (3) 水平间距 < 2.0cm（视觉上可感知为关联）
  同时检测：箭头终点是否未锚定到任何条形/节点元素
    （终点 y 坐标不在任何已知数据元素的 bounding box 范围内）
```

**典型案例**：图4-1中 BIS 管制箭头起点 y=0.2 与 ASP 说明框中心 y=0.2 完全相同，水平间距仅 1.3cm，读者容易误以为"BIS 管制影响 ASP 价格"。此外箭头向上指向空白区域（HBM4E 与国产 HBM 之间），未明确锚定到任何条形元素

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
Class I: TikZ 路径连通性失效 （V-4，-|/|- 语义误用）🆕
Class J: 箭头-文字交叉 （L-2 扩展，箭头切割文字）🆕
Class K: 动态高度级联碰撞 （V-3 扩展，text width 不足导致）🆕
Class L: 同类元素对齐异常 （L-3，阶梯状错落）🆕
Class M: 视觉语义误导 （S-4，基线意外对齐）🆕
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

### I-1 TikZ 路径连通性修复（`-|`/`|-` 语义陷阱）🆕
```latex
% ❌ 错误：-| 操作符导致连线悬空
% 语义：(SW1.north-|\h.south) = x=SW1.north.x, y=H.south.y
% 结果：在 Host 底部画水平短线，终点距 Switch 1.0cm
\foreach \h in {H1,H2,H3,H4} {
  \draw[line, accentblue] (\h.south) -- (SW1.north-|\h.south);
}

% ✅ 正确方案1：使用 |-（先垂直后水平）
\foreach \h in {H1,H2,H3,H4} {
  \draw[line, accentblue] (\h.south) |- (SW1.north);
}

% ✅ 正确方案2：显式正交路由（更可控）
\foreach \h in {H1,H2,H3,H4} {
  \draw[line, accentblue] (\h.south) -- ++(0,-0.3) -| (SW1.north);
}
```

### J-1 箭头-文字交叉修复（正交路由绕过文字列）🆕
```latex
% ❌ 错误：bend right 箭头垂直穿越子框列
% 箭头沿 x=0 下行，切割 TH1_sub1（国产HBM≥2028）和 TH1_sub2（SK海力士55%+）
\draw[arrow, bend right=-30] (TH1.south) to (CONCL.north);

% ✅ 正确：正交路由 + xshift 偏移，绕过文字列
\node[...CONCL...] at (4.5, -4.8) {...};
\draw[arrow] (TH1.south) -- ++(0, -0.35) -| ([xshift=2.5cm]CONCL.north west);
\draw[arrow] (TH2.south) -- ++(0, -0.35) -| ([xshift=-2.5cm]CONCL.north east);
\draw[arrow] (TH3.south) -- ++(0, -0.35) -| ([xshift=2.5cm]CONCL.north west);
\draw[arrow] (TH4.south) -- ++(0, -0.35) -| ([xshift=-2.5cm]CONCL.north east);
```

### K-1 动态高度级联修复（text width 充足性）🆕
```latex
% ❌ 问题：text width=2.3cm 导致 3 行文字，实际高度 > minimum height=1.0cm
% 级联导致与下方 OUT 框间隙仅 0.02cm
driver/.style={..., text width=2.3cm, minimum height=1cm, ...}
\node[driver, below=of T1] (D1) {SK Hynix 良率 85\%+\\B100/B200 放量};
\node[...OUT...] at (6.3,-3.6) {...};

% ✅ 修复方案1：增加 text width（首选）
driver/.style={..., text width=2.6cm, minimum height=1cm, ...}

% ✅ 修复方案2：增加下方元素的 y 偏移
\node[...OUT...] at (6.3,-4.4) {...};

% ✅ 修复方案3：同时增加 node distance
\begin{tikzpicture}[node distance=1.4cm and 0.6cm, ...]
```

### L-1 对齐一致性修复（绝对坐标或统一锚点）🆕
```latex
% ❌ 问题：right=of 相对定位，前置节点数不同 → 阶梯状错落
\node[node] (U1) {...};  % L1 第1个
\node[node, right=of U1] (U2) {...};  % L1 第2个
\node[node, right=of U2] (U3) {...};  % L1 第3个
\node[node, right=of U3] (U4) {...};  % L1 第4个
\node[ashar, right=of U4] (A1) {A股·设备};  % A1 在 x≈11.5

\node[node] (D1) {...};  % L2 第1个
\node[node, right=of D1] (D2) {...};  % L2 第2个
\node[node, right=of D2] (D3) {...};  % L2 第3个
\node[ashar, right=of D3] (A2) {A股·设计};  % A2 在 x≈8.4，与 A1 偏差 3.1cm

% ✅ 修复方案1：使用绝对 x 坐标
\node[ashar] (A1) at (12.0, <y1>) {A股·设备};
\node[ashar] (A2) at (12.0, <y2>) {A股·设计};
% ... 所有 A 股标签统一 x=12.0

% ✅ 修复方案2：统一锚点到层标题右边缘
\node[ashar, right=0.2cm of L1.east, anchor=west] (A1) {A股·设备};
\node[ashar, right=0.2cm of L2.east, anchor=west] (A2) {A股·设计};
```

### M-1 视觉语义邻近修复（避免误导性基线对齐）🆕
```latex
% ❌ 问题：BIS 箭头起点 y=0.2 与 ASP 框中心 y=0.2 完全对齐
% 水平间距仅 1.3cm，读者误以为"BIS 影响 ASP"
\draw[->, thick, riskred] (10.0, 0.2) -- node[above] {BIS 管制关键节点} (10.0, 1.4);
\node[...ASP...] at (0.2, 0.2) {ASP：HBM2E $8--12/GB...};

% ✅ 修复方案1：偏移箭头 x 坐标到空白区域
\draw[->, thick, riskred] (11.5, 0.2) -- node[above] {BIS 管制关键节点} (11.5, 1.4);
% 现在箭头在 2027/2028 年份线之间，不与任何数据条共享视觉锚点

% ✅ 修复方案2：添加显式标签澄清关系
\node[font=\tiny, color=riskred, below] at (11.5, 0.2) {管制时点};
```

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
P0-04 Class I TikZ 路径连通性失效（12条箭头全悬空=整张图废了）🆕
  ↓
P0-05 Class D 数值/单位交叉一致性（最严重的实质错）
  ↓
P0-06 Class C 颜色语义 swap（饼切片 / pgfplots cycle list）
  ↓
P0-07 Class J 箭头-文字交叉（箭头切割核心论点文字）🆕
  ↓
P0-08 Class F 裁切（subp / 气泡 / 卡片）
  ↓
P0-09 Class K 动态高度级联碰撞（text width 不足导致）🆕
  ↓
P0-10 Class G 元素重叠（象限标签 / 气泡 / callout）
  ↓
P0-11 Class L 对齐异常（同类标签阶梯状错落）🆕
  ↓
P0-12 Class M 视觉语义误导（基线意外对齐）🆕
  ↓
P0-13 Class H Overfull >20pt 清零
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

**v1.0**（首次入库，2026-06-24）：
- 8 维度 × 8 Bug Class × 修复片段库 × 严格分级 × 标准输出模板
- 配套 `.agents/team/exhibit-format-reviewer.md` role 文件
- 已在 AI 存储产业链深度研报（20260624）实战验证：10 张图 × 8 章节识别 15 个问题 + 12 BLOCK 修复清单

**v2.0**（重大升级，2026-07-04）🆕：
- **维度扩展**：8 → 12 维度，新增 V-4（路径连通性）、L-3（对齐一致性）、L-4（安全间隙）、S-4（视觉语义邻近）
- **探针系统**：内置 6 个视觉检测探针
  1. tikz_path_connectivity_probe - 检测 `-|`/`|-` 语义误用
  2. arrow_text_intersection_probe - 检测箭头切割文字
  3. dynamic_height_cascade_probe - 检测 text width 导致的级联碰撞
  4. alignment_consistency_probe - 检测同类元素对齐异常
  5. narrow_column_overflow_probe - 静态检测窄列溢出
  6. visual_semantic_proximity_probe - 检测误导性视觉布局
- **Bug Class 扩展**：8 → 13 个（新增 I-M 类）
- **修复库扩展**：新增 I-1 到 M-1 共 5 类修复模式
- **根因改进**：解决了 v1.0 的 5 个系统性漏洞
  1. 从「渲染输出中心」转向「源代码中心」审查
  2. 重叠检测从 bounding box 对撞扩展到箭头-线段相交
  3. 引入「元素意图」理解（同类标签应对齐、箭头应连接）
  4. 表格列宽检查支持纯静态分析（不依赖 .log）
  5. 新增安全间隙概念（0.3cm 视觉可分辨阈值）
- **实战验证**：在 AI 存储产业链深度研报 v2 中发现并修复：
  - 图4-2 CXL拓扑图 12 条连线全部悬空（CRITICAL）
  - 图2-1 箭头穿越 4 个子框文字（HIGH）
  - 图1-1 驱动框与结论框间隙 0.02cm（HIGH）
  - 图7-1 图例遮挡数据标签（HIGH）
  - 图3-1 6 个 A 股标签水平偏差 5.8cm（MEDIUM）

**v2.1 Roadmap**：
- 自动化正则扫描脚本（bash/python）：自动枚举所有 exhibit → 输出 JSON 卡片
- Overfull 审计行 → 自动定位最窄列 / 最长词
- pgfplots cycle list 条目数与 `\addplot` 自动计数匹配
- 路径连通性探针的自动化实现（解析 TikZ 坐标计算）

---
**调用方式**：在任何对话里写 `/exhibit-format-reviewer <研报路径>`。
