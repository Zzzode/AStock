# AI 存储产业链研报 · 图表格式 & 数据正确性全面审查报告
**Review Version**: R1（基于 PDF 2026-06-24 编译版 + 8 张用户截图对照）
**Reviewer Scope**: 图 2-1 / 3-1 / 4-2 / 5-1(×2) / 5-2 / 6-1 / 7-1 / 8-1 / 10-1，共 **10 张 TikZ/pgfplots 图表**
**Hard Acceptance Gates**: ① 文字可见性（fill ≠ text color）② 图例-填色语义一致性 ③ 数据与正文章节一致性 ④ 图例/轴标/脚注完整性 ⑤ Overfull \(\hbox > 20\mathrm{pt}\) 清零

---

## 0. 审查总览（traffic-light）

| # | 图号 | 图表标题 | 可见性 | 语义 | 数据 | 版式 | 严重级别 |
|---|---|---|---|---|---|---|---|
| 1 | 2-1 | AStock House View 四核心论点结构 | 🟡 局部 | 🟢 OK | 🟢 OK | 🔴 严重布局 | **P0 · HIGH** |
| 2 | 3-1 | 全球存储产业链全景图谱 | 🔴 全崩 | 🔴 图例反色 | 🔴 渲染坏码 | 🔴 全链路错位 | **P0 · CRITICAL** |
| 3 | 4-2 | CXL 内存池化拓扑架构图 | 🔴 2 块空白 | 🟢 OK | 🟡 部分缺失 | 🔴 严重 | **P0 · HIGH** |
| 4 | 5-1a | 原厂 Capex 堆叠柱（L9-91） | 🟢 OK | 🟡 缺柱上数字 | 🟡 柱顶标写错 | 🟢 OK | **P1 · MEDIUM** |
| 5 | 5-1b | 原厂 Capex 堆叠柱（L94-187） | 🟢 OK | 🟢 OK | 🟢 OK | 🟢 OK | P2 · LOW（重复图，建议删 5-1a） |
| 6 | 5-2 | DRAM/NAND 供需缺口桥接图 | 🔴 2 块空白 | 🟡 标文字截 | 🟢 OK | 🔴 数据标签被吞 | **P0 · HIGH** |
| 7 | 6-1 | 三大原厂 HBM 份额饼（×3） | 🟢 OK | 🔴 饼色反色！ | 🟢 OK | 🟡 字错位 | **P0 · HIGH** |
| 8 | 7-1 | A 股存储链市值分布（横柱） | 🟢 OK | 🔴 分类色环与全色冲突 | 🟡 轴与数值不符 | 🟡 长电/兆易序乱 | **P1 · MEDIUM** |
| 9 | 8-1 | A 股存储估值四象限 | 🟡 局部 | 🔴 图例点色全错 | 🟡 轴刻度丢失 | 🔴 象限文字重叠 | **P0 · HIGH** |
| 10 | 10-1 | 风险矩阵热力图 | 🔴 R1 气泡文字被吞 | 🟡 风险色与气泡色不匹配 | 🟢 OK | 🟡 轴标反转 | **P0 · HIGH** |

**CRITICAL 1 张 / HIGH 6 张 / MEDIUM 2 张 / LOW 1 张** —— **整体不通过（需 P0 全修复 + P1 半修复后再重审）。**

---

## 1. 问题总分类（跨图共性 Bug 优先修复）

### Bug Class A：TikZ `node/.style` 与 `ashare/.style` 颜色宏继承冲突 → **深蓝色块无文字（图 1-2 / 3-1 / 4-2 / 5-2）**
**根因（已在 preamble.tex v6 确认）**：`deepnavy` 被用作 fill=deepnavy!92，而字体 color=navy → 当某 style 通过 `\draw[->, navy]` 路径继承时，TikZ 作用域把临近节点的 `text=...` 覆盖为 `deepnavy`，最后一层节点的「fill 颜色 ≈ text 颜色」导致文字被同色背景吞噬。
- **已在图 1-2 修复（95b4080 → f5fdcfb）**：把 L121 `ashare/.style={draw=riskamber, fill=riskamber!8, color=navy}` → `{draw=navy, fill=white, text=deepnavy}`，并逐节点显式指定。
- **待修的同样 Bug**：图 3-1 L17 `ashar/.style={draw=riskamber, fill=riskamber!8, color=navy}`；图 4-2 L131 `ashare/.style={draw=riskred, fill=riskred!15, color=navy}`；图 5-2 L225 `bal/.style={…, text=white}, fill=navy!18（对比度不足，白字在浅蓝底上可见，但桥接图两侧空白块是 `ashare` 等价风格）。

### Bug Class B：TikZ `\faExclamationTriangle` / `\faYenSign` 等 FontAwesome5 符号在 XeLaTeX 下宏包 fallback 为 `aExclamationTriangle` 文本 —— **图 3-1 / 6-1 脚注 / 表 9-1 出现乱码**
**根因**：`preamble.tex` 中 `\usepackage[fixed]{fontawesome5}` 的 fixed 选项在 xeCJK 下有 0.08em 位移；当字体 Times New Roman 缺字时（U+2713 ✓ 就是如此），整个 fa* 系列通过 `\FA` 命名空间寻址，一旦命名未展开（例如 `\faExclamationTriangle` 内部 `\faicon{exclamation-triangle}` 的破折号），就会输出成 `aExclamationTriangle` 的裸文本。
- **截图实锤**：图 3-1 标题栏下方出现的绿色边框块内有文字 **"aExclamationTriangle A 股无原厂..."**；图 6-1 sourcenote 出现 **"⚠ AStock"** 实际是 `⚠` 字符但渲染失败。

### Bug Class C：饼图/柱状图**图例颜色与实际切片/柱色不一致**
- **图 6-1（最严重）**：legend 中「SK Hynix = 红 / Samsung = 蓝 / Micron = 绿」，但三张饼实际渲染：
  - SK Hynix slice 标 **"SK 60%"** → slice 是 **红色**（✓ 与 legend 一致）
  - **Samsung slice 标 "Samsung 24%" → 实际是绿色！**
  - **Micron slice 标 "Micron 12%" → 实际是蓝色！**
  - 结论：**Samsung 与 Micron 的颜色在 pgf pie 计算时被 swap 了**（风险：读者会把 27% Samsung 饼误读为 Micron）。
- **图 10-1 风险热力气泡**：R1/R2 标 RED 风险类但气泡色是 `riskamber!25`（橙黄），与图例 RED 粉红块不匹配。

### Bug Class D：pgfplots bar 轴标签 / `nodes near coords` 数值错误
- **图 7-1**：X 轴数值 vs 节点标出现 **顺序不匹配**：澜起 bar 长度约 x=1,680，但 nodes near coords 标 **"1,680"**；**但「长电科技」bar 明显比「兆易创新」短（实际长电 890 亿 vs 兆易 1,150 亿），截图中长电 bar 顶端标 "1,150" 而兆易 bar 顶端标 "890" → **nodes near coords 与 symbolic y coords 的顺序错位**。
- **图 5-1a（第一份 Capex 堆叠柱）**：L76 柱顶注 `2026E \$1200--1350B`，但 L34 注释 2026E 合计 = 62+32+18+11+9 = **\$132B**（千亿级，正确！）—— 但文字写的是 **"\$1200--1350B" 是错误单位**（应为 \$120--135B 或 原文「2026E 合计 $>\$1200\) 亿」（亿 ≈ Billion/10？需统一单位：全文写的是「\$亿」还是「B」？本文统一 1 亿 = 100M = 0.1B，所以 **$1,200 亿 = $120B**，与模型值 132B 区间一致，单位标注不一致属于显示 Bug 但数据无错）。
- **图 5-2 供需桥接 D1/D5 右侧**：卡片文字「单机存储 +80% YoY」「受管制补偿需求 +25%」都被右侧裁掉 3 字，resizebox 0.80\exhibitwidth 不足 → 缩放到 0.92 倍或拉宽 bal 节点。

### Bug Class E：**图表重复（图 5-1 出现两份几乎完全相同的堆叠柱）**
- 图 5-1 L9-91（第一份）：柱上无顶端累计数字，柱顶注是单行 `2026E $1200--1350B`
- 图 5-1 L94-187（第二份）：柱上有 79/89/106/**132★**/161 累计数字，柱顶注是「2026E 三大原厂 Capex >$1200 亿」
- **结论**：第一份是初稿，第二份是定稿。L9-91 必须整段删除，否则 PDF 出现两份编号相同的 "图 5-1"。

---

## 2. 分图逐项审查

---

### 🔴 CRITICAL · 图 3-1 全球存储产业链全景图谱

#### 版式 Bug（6 项）
1. **5 个深蓝色块无文字**：L1 `EUV/光刻 → ASML` 右边的 `A1 = A股·设备` 是深蓝空块；L2 `A2 = A股·设计`、L3 `A3 = A股间接`、L4 `A4 = A股·封测`、L5 `A5 = A股·模组`、L6 `A6 = A股·系统` 全部 **深蓝色空块无文字**（对应 Bug Class A，`ashar` style 同图 1-2）。
2. **乱码符号**：U1 下方出现浮动框 `aExclamationTriangle A 股无原厂 · 配置聚焦上游/接口/封测` — 应渲染为 `⚠ A股无原厂 · 配置聚焦上游/接口/封测`（Bug Class B）。
3. **L2 层条错位**：L2 存储设计层的绿条被上面的 "aExclamationTriangle" 浮框截断并覆盖，L2 标题下半部被吃。
4. **7 个层之间的主箭头（价值传导）全部被深蓝色 A* 节点向右 1cm 偏移**，箭头的 `(L\i.south) -- node[right=1pt]` 的节点字「价值传导」全部与 L2/L4/L6 的深蓝色空块重叠，字被吞噬。
5. **L7 下游应用卡片**："AI 训练集群 / MSFT·Meta·Google·AWS..." 的第一行 "AI 训练集群" 上方又出现一条深蓝宽条（对应 Bug Class A 的影响）。
6. **Layer 1 第四个卡片（硅片/光刻胶/特气）右侧**：`⚠ A股·设备` 标题栏的左侧一半文字与 `U4 卡片 (硅片/光刻胶/特气 ShinEtsu/JSR/Entegris 国产化 8-12%)` 右侧 2cm 完全重叠，视觉上两张卡片"粘"在一起。

#### 语义正确性
- L1 = 设备 10-12% | 材料 7-9% ✓；L2 = 8-10% ✓；L3 = 38-42%（价值最大） ✓；L4 = 先进 12-15% | 传统 5-7% ✓；L5 = 8-10% ✓；L7 = Capex 来源 ✓。
- **唯一语义歧义**：L6 = 整机集成「-」表示零增价值占比？但 AI 服务器整机 Dell/浪潮/华为毛利 <5%，建议写「[整机 <2%，不影响链上利润分配]」，避免读者误解为「无价值」。

#### 数据一致性（对照表 3-1 p{7 列} + 正文 Industry Landscape）
- EUV 国产化 <1% ✓（表 3-1 没有 EUV 单列，但设备 10-15% 总体一致）
- 澜起 RCD 全球 70% ✓（D3 卡片小字「澜起领先」→ 建议加粗「RCD 全球 ~70% ★」，与 ch01 图 1-2 的节点对齐）
- 长存/长鑫未上市 ✓

---

### 🔴 HIGH · 图 2-1 House View 四核心论点结构

#### 版式 Bug（5 项）
1. **论点一（红 HBM）的 2 个小卡片**：`国产 HBM ≥2028 · ▲ 市场误判节奏` / `SK海力士 55%+ · 三家原厂护城河极高` 卡片高度仅 0.4cm，中文首字被卡片顶边裁切掉一半 → `subp/.style minimum height` 从 0.8cm 升到 1.1cm，`inner sep` 从 2 → 4pt。
2. **论点三（琥珀 Q3）的 3 个小卡片**：同样首字被裁 + 卡片左对齐重叠（`标准品 bit growth ≤20% · 供给刚性` 左侧贴到论点 3 的黄框）。
3. **论点四（绿 CXL）的 2 个小卡片**：`澜起 CXL 收入 26 10亿 · 27 翻倍` 中 "26 10亿" 应为 **"26年 约10亿"**，数字格式不规范。
4. **四条弯曲箭头汇聚底部蓝块**：`AStock 结论：2026H2-2027 量价齐升双击 · 核心组合目标回报 +25-40%` 的 `+25-40%` 被压到第二行并与边框重叠 → 蓝块 `minimum height` 从 1.1cm → 1.4cm，`text width` 从 14cm → 14.4cm。
5. **「I·黄金象限 / II·底仓区」** 视觉上四个象限（论点框）与象限编号无对应关系 → 建议在四个论点框的左上角加 `Ⅰ/Ⅱ/Ⅲ/Ⅳ` 角标。

#### 数据一致性
- 论点 1 国产 HBM ≥2028 ✓（SC-7 B 级）；SK 海力士 55%+ ✓（HBM 市场 60→57→52 饼图一致）
- 论点 2 北华/中微/拓荆 国产化率 10%→25% ✓（表 6-1 分组行 20-30%）
- 论点 3 Q3 缺口 -8~-10%、QoQ +10%+ ✓（表 5-2 2026Q3E -6~-8% 与 QoQ +8-10%，差 2pt 属乐观/基准差，可接受）
- 论点 4 CXL 2026H2 8-10% ✓；澜起 10亿/20亿 ✓（ch04 §CXL 管理层指引一致）

---

### 🔴 HIGH · 图 4-2 CXL 拓扑架构图

#### 版式 Bug（4 项）
1. **Pool B / Pool D 两个 A 股卡位块空白（深蓝无文字）**：Bug Class A。Pool B 应显示「Pool B · Type 3 / ★ CXL MXC 控制器 / 澜起全球首发量产」；Pool D 应显示「Pool D · 模组/SSD / ★ 江波龙/深科技 / CXL 模组研发中」。
2. **Pool A 上方 Host 1 角 "PCIe 5.0/6.0 ... 32/64GT/s" 与 "□ A股核心卡位层" 两条红字/蓝字在 SW1/SW2 中间处被 Pool B 空白块重叠**，文字可见性仅约 60%。
3. **SW1→P1 连线**：`draw (SW1.south) -- (P1.north-|SW1.south)` 实际连接点 x 坐标在 SW1 正下方，但 P1（Pool A，Type 3）位置在 x=0.3，SW1 在 x=2.0 → 连线"从 Switch 1 正下方垂直插入 Pool A 中间"→ 应改为 `-|`（先竖后横）。
4. **H1 文本 "Blackwell / AMD" 与上方浮标 L1 "AI 数据中心 Host · CXL Root Complex" 之间的灰色箭头 0.8em 间隔过窄**，H1 的顶部 20% 被 L1 的基线覆盖。

#### 数据/语义
- Host 类型 4 类（Blackwell/AMD · Emerald Rapids · 国产AI · CPU-only）✓
- Switch：Broadcom/Astera · Microchip (PMCI) ✓
- Pool 类型：Type 3 Expansion · MXC 控制器 · Tiering (DDR5/CXL SSD) · 模组/SSD ✓ 全链路正确
- PCIe 5.0/6.0 × 32GT/s / 64GT/s ✓（CXL 3.1 = PCIe 6.0 × 64GT/s PAM4）
- **唯一语义缺项**：Pool C Tiering 卡片上未标「Samsung/Solidigm = 海外原厂 · A股无映射」，建议在 Tiering 左下角加 tiny 字「海外映射（非A股）」。

---

### 🟡 MEDIUM · 图 5-1 原厂 Capex 堆叠柱（双份）

#### 版式/重复 Bug（3 项）
1. **重复图**：L9-91（版本 A，无柱顶数字）与 L94-187（版本 B，有 79/89/106/132★/161）**同编号 "图 5-1"** → **删除 L9-91 整段**，保留第二份（版本 B 柱上有累计数更符合投行规范）。
2. **柱顶注文字与数值**：版本 B L170 `2026E 三大原厂 Capex >$1200 亿` 与柱上标 132（$B）单位不一致 → 统一：柱顶注写「> 1.2 万亿（\$120B+）」，或柱上标 79/89/106/**132★**/161 统一加 \$B 后缀。
3. **Y 轴单位**：L29 竖轴写 `Capex ($B)` ✓，但柱上数字是纯整数（132 → 读者会猜成亿？）→ 在柱上标数字后统一加 `B` 字 `\node[...] {$132^\textbf{B}★$}`。

#### 数据一致性
- 2023 = 40+18+9+7+5 = 79 $B ✓
- 2024 = 45+20+10+8+6 = 89 $B ✓
- 2025 = 52+25+13+9+7 = 106 $B ✓
- 2026E = 62+32+18+11+9 = **132 $B** ✓
- 2027E = 70+40+25+14+12 = 161 $B ✓
- **校验**：表 5-1 数值校验：Samsung 420-440 → 柱 62 (×10=620? 冲突!)
  - 🚨 **严重数据不匹配**：表 5-1 显示 Samsung 2026E 420-440「亿美元」→ 柱 62 ($B) = 620 亿美元
  - 表 5-1 显示 SK Hynix 250-280 亿美 → 柱 32 ($B) = 320 亿
  - Micron 表 165-190 亿 vs 柱 18 ($B) = 180 亿 ✓
  - Kioxia+WD 表 90-100 亿 vs 柱 11 ($B) = 110 亿 ✓
  - YMTC+CXMT 表 3.5-4.5 + 2.5-3.5 = 6-8 亿 vs 柱 9 ($B) = 90 亿 ❌ **完全 10× 差异！**
  - **判定**：柱图 L39-71 的单位应为 **\$10 亿（即 1 unit = $1B？那 62 = $62B，和表 5-1 Samsung 420-440「亿美元」= 42-44 $B 差 18 $B）**
  - **结论**：表 5-1 「2026E Capex 亿美元」列数值与 Capex 堆叠柱**单位系统冲突，至少一项有 10× 数量级错误**（最可能的是表 5-1 "2026E 420-440" 把十亿美元误写成亿美元）。**建议统一单位：全文 Samsung 2026E = $42-44B，柱图 62→42，SK 32→26，YMTC+CXMT 9→7，柱总高从 132→92；柱上标注 `92★`，柱顶注写「2026E 三大原厂 + YMTC/CXMT 合计 $920 亿」。**

---

### 🔴 HIGH · 图 5-2 DRAM/NAND 供需缺口桥接图

#### 版式 Bug（5 项）
1. **供给侧 4 张卡片**：Wafer Out 卡「2026E DRAM +18-20%」的「D」被裁；「HBM 良率 78-88%」的「8」被裁；「ASML/DUV 排产」卡的「A」被裁；「国内长存/长鑫管制」的「国」被裁 → `resizebox 0.80 → 0.90` 或所有 `sup/.style text width 3.2cm → 3.6cm`，`minimum height 1.0→1.2cm`。
2. **需求侧 5 张卡片右半被裁**：D1「AI 服务器 · HBM+DDR5 · 单机存储 +80% YoY」末 2 字 "YoY" 与右侧边距仅 0.2cm；D5「国内云 + 国产 AI 芯片 · 受管制补偿需求 +25%」的「补偿需求 +25%」6 字整体被吞进右边框。
3. **中间 bal 节点"供需基准"块**：L235 `bal/.style {fill=navy!18, text=white}` → **对比度不足**（浅蓝底白字视觉上与供给侧 accentblue 难以区分），应改为 `fill=navy, text=white` 深蓝底白字或 `fill=white, text=navy, draw=navy` 白底深框。
4. **供给侧 4 条 accentblue 箭头**：起点 `(\s.east)` 在卡片右边框，但终点 `(B.west-|\s.east)` 实际是在 `B.west` 垂线上，所有 4 条箭头终点堆在 bal 同一点 → 视觉上"4 条蓝线拧成一条"，桥接图失去逐项映射含义。应改为每条箭头从不同 Y 坐标进入 bal（S1→bal 上 30%，S4→bal 下 30%），或在 bal 左侧均匀分散。
5. **底部 BLOCK 治理说明**：L252 的长文本 `「核心驱动：供给 20% bit growth << 需求 30-35%... BLOCK 治理：C 级供需预测仅使用区间，严禁单点值」` 右侧最后 4 字「严禁单点值」与 tikzpicture 右边框重叠 0.5cm（resizebox 0.80 导致外注 11cm 与 tikz 宽度 9.28cm 冲突）。

#### 数据一致性
- 供给侧 4 项：bit growth DRAM +18-20% ✓（ch05 §2）；HBM 良率 78-88% ✓（ch06 §1 SK 85+ 三星 78-82 美光 75-80%）；ASML/DUV 排产 → 释放率 92%（合理，行业经验）；国内管制 → 有效供给率 85%（AStock 模型，\faExclamationTriangle 已标）。
- 需求侧 5 项：AI 服务器单机存储 +80% YoY ✓（ch04 §DDR5）；云端推理企业级 SSD +30% ✓；PC/AI PC + 手机 LPDDR5 +10-12% ✓；汽车/工业 +15% ✓；国内补偿 +25%（模型估计，属 BLOCK 级）。
- 平衡块数值：DRAM -6~-8%，NAND -3~-5% ✓（表 5-2 2026Q3E 基准缺口一致；取全年均值符合 BLOCK 门控）。

---

### 🔴 HIGH · 图 6-1 HBM 三张饼图（2025E / 2026E / 2027E）

#### 版式 Bug（3 项）
1. **饼切片上的文字与图例颜色 swap（最严重）**：
   - 2025E：SK 60%（红 ✓），Samsung 24% **绿**（legend Samsung = 蓝 ❌），Micron 12% **蓝**（legend Micron = 绿 ❌），灰色 4% "Other" 未在图例。
   - 2026E：SK 57%（红 ✓），Samsung 27% **绿**，Micron 15% **蓝**，灰 1%。
   - 2027E：SK 52%（红 ✓），Samsung 30% **绿**，Micron 18% **蓝**。
   - **根因**：ch06 §6-1 L21-32 的 pie 构建是 `\def\a{90}\fill[riskred]... +216`（SK）；`\pgfmathsetmacro\a{\a+216} \fill[accentblue]...+86.4`（Samsung）；`\pgfmathsetmacro\a{\a+86.4} \fill[nvgreen]...+43.2`（Micron）→ 顺序正确，但 legend tabular 中 L69-73：
     ```
     \cellcolor{riskred!60} & SK Hynix &
     \cellcolor{accentblue!60} & Samsung &
     \cellcolor{nvgreen!55} & Micron \\
     ```
     → **legend Samsung = 蓝（accentblue）、Micron = 绿（nvgreen）** ✓ 与 fill 一致！
   - **用户实际截图显示**：Samsung 饼切片实际是绿色、Micron 切片实际是蓝色 → **说明 XeLaTeX 渲染中 pie slice fill 的色号错位**。最可能的根因：pie/.style `slice/.insert path` 中 `pgfmathsetmacro\a` 在三张饼之间未被局部清零（scope 内 `\def\a{90}` 到第三张饼仍然生效，叠加 scope xshift 后的计算错误）。**修复建议**：在每个 `\begin{scope}[xshift=6.0cm]` 块首行重新 `\def\a{90}`，不依赖全局继承。
2. **标签文字错位**：2025E 「Micron 12%」在切片右下（蓝片），但 Samsung 绿片上的 Samsung 字被灰色 4% 片的 Other 标重叠 → 三星 24% 标签应从 300° 方向 1.2 半径移到 280° 1.35 半径。
3. **4% Other 切片缺图例项**：legend 只有 3 家原厂，2025E/2026E 各有 4%/1% 灰色小块，读者无法对应。加一行 `\cellcolor{steelgrey!60} & Other（铠侠/Solidigm）`。

#### 数据一致性
- 2025E：SK 60 / Samsung 24 / Micron 12 / Other 4 = 100% ✓
- 2026E：SK 57 / Samsung 27 / Micron 15 / Other 1 = 100% ✓
- 2027E：SK 52 / Samsung 30 / Micron 18 = 100% ✓（无 Other 是合理，三巨头扩大份额）
- 与 ch06 §1 正文「SK 保持龙头，三星/美光分别以 HBM4/1β 追赶」一致 ✓

---

### 🟡 MEDIUM · 图 7-1 A 股存储链市值分布（横柱）

#### 版式 Bug（4 项）
1. **pgfplots 分类 legend 与所有柱填色冲突**：legend 写「设计/IP=navy、封测=nvgreen、模组/SSD=riskred、材料=riskamber、设备=accentblue、主控=steelgrey」共 6 类，但 **15 根柱全部是 navy!30 单色**（用户截图 15 根柱全淡蓝灰）→ 根因：`cycle list` 有 6 色，但只有 1 个 `\addplot` 块 → pgfplots 只会取 cycle list 第一项（navy!30）填充全部 15 柱。
   - **修法**：拆成 6 个 `\addplot`，每个 `\addplot[fill=X, draw=X!80] coordinates {(Y值, X标签)}` 按类别分组，对应 legend 的 6 色。
2. **Y 轴 symbolic coords 顺序与柱顶端数字标注错位**：
   - Y 顺序（从下往上）：北京君正(220)→芯原(310)→华天(380)→全志(280)→南大(320)→沪硅(650)→拓荆(580)→江波龙(820)→深科技(560)→通富(690)→兆易(1150)→长电(890)→中微(1420)→澜起(1680)→北华(3450)
   - 但用户截图柱顶数字顺序是：「220(君正) / 310(芯原) / 380(华天) / 280(全志) / 320(南大) / 650(沪硅) / 580(拓荆) / 820(江波龙) / **560(深科技)** / **690(通富)** / **1,150(兆易)** / **890(长电)** / 1,420(中微) / 1,680(澜起) / 3,450(北华)」
   - **前 8 条正确，后 7 条错位！**（兆易柱应 >1,000，但实际长度只到 800 刻度附近，长电柱反而到约 1,100 → 意味着 symbolic 坐标的坐标映射顺序与 `\addplot coordinates {…}` 数据顺序不一致）。
   - **修法**：`symbolic y coords` 严格按 `\addplot coordinates` 条目顺序逐字对应，禁止手动重排。
3. **X 轴标题与柱底注重合**：X 轴标题「总市值（亿元人民币…）」写在 `below=0.5cm of xlabel` 下方，但用户截图中柱图底部来源说明 text width=14cm 又叠加在最下方，两者仅 0.3em 间隔 → 底注下移 1em。
4. **legend 位置**：legend anchor=south east 在 (0.98, 0.02) 实际上盖在「南大光电 280 亿」柱尾上 → 移到 `at={(0.5, -0.1)}, anchor=north` 底部居中横排 legend。

#### 数据一致性（对照表 7-1 财务 & Wind）
- 澜起 1,680 亿 ✓（表 7-1 2,900？不，表 7-1 列是「26E 市值（亿）」= PE × 净利 = 42×33 = 1,386？表 7-1 第 4 列「25营收(亿)」75，第 5 列净利 32-35，第 7 列 26E PE 42x → 26E 市值 = PE × 净利 = 42×(32-35)=1,344~1,470 亿，**但图 7-1 写 1,680 亿（今日收盘市值）**。
- 北华创 3,450 亿 ✓（表 7-1 3,450 亿 完全一致）；中微 1,420 亿 ✓；长电 890 亿 ✓（表 7-1 市值 890 亿）；兆易 1,150 亿 ✓（表 7-1 第 5 列？表 7-1 第 3 列 AI 敞口 8-12%、第 4 列营收 92 亿、PE 36x → 合理）
- **单位一致性结论**：图 7-1 = 当前（2026-06-23）收盘总市值，表 7-1 第 4-7 列 = 2025A 营收/净利 / PE 26E，两者数据体系不同，应在图题中标注「注：本图为 2026-06-23 收盘总市值（亿人民币，现价），非 26E 合理估值」，避免读者用现价与表 7-1 PE 交叉推断产生矛盾。

---

### 🔴 HIGH · 图 8-1 估值四象限

#### 版式 Bug（6 项）
1. **象限文字严重重叠**：用户截图中「I · 黄金象限 · 高确定+高性价比」、「II · 底仓区 · 高确定+合理估值」、「III · 规避区 · 低确定+偏高估」、「IV · 弹性区 · 中确定+高弹性」**4 条文字在图中心（5.5, 5.5）十字交汇点相互挤成一堆**，仅「I · 黄金象限」一行顶部可见，其余 3 行被覆盖或穿透 → 根因：L27-30 四个节点的 anchor 全部设置在 (5.5,5.5)，但 `above right` 和 `above left` 和 `below left` 和 `below right` 是从 (5.5,5.5) 同一点往 4 个方向，但实际 tikz 坐标系中 x 和 y 范围仅 0~11，所以「above right」仍会靠中心（文字宽度 10cm 超出边界）。
   - **修法**：四条文字分别锚到各象限中心（I=(8.3,8.3)、II=(2.7,8.3)、III=(2.7,2.7)、IV=(8.3,2.7)），去掉与对角象限的交叉。
2. **象限十字线颜色问题**：L23-24 `\draw[grid]` 两条十字线 steelgrey!40 dashed ✓，但在视觉上与节点文字颜色对比不足，应加粗到 0.8pt。
3. **点颜色分类与 legend 全错**：legend 写「核心 Tier 1 = 深蓝圆点 / 卫星 Tier 2 = 绿色圆点 / 主题层 = 橙色圆点」，但用户截图中：
   - 澜起（Tier 1，应深蓝）**实际是淡蓝空心圆**
   - 北华创（Tier 1，应深蓝）**实际是淡蓝空心圆**
   - 江波龙标「★ 性价比之王 18x」应是卫星 Tier 2（绿色）但实际是**绿色圆圈带绿色外框**（正确 ✓）
   - 长电/通富/深科技/兆易（应 Tier 2 绿色）**实际是淡绿半透明圆点**（近似 ✓）
   - 沪硅/南大光电（主题层，应橙）**实际是浅橙半透明圆点** ✓
   - **根因**：L14 dot/.style 定义 `fill=#1!30, draw=#1` 填充只有 30% 透明度，视觉上接近白色；且 Tier 1 的 #1=navy → navy!30 就是淡蓝灰，legend 中 tabular 填色用的是实心 `\cellcolor{navy!30}` 但渲染上与圆点的 draw 边框颜色不对应 → **修法：Tier 1 dot fill 升到 navy!60 或直接实心 draw=deepnavy fill=navy!40**。
4. **轴刻度丢失**：Y 轴左侧标 B / B+A / A+，但刻度值（B=3 / B+=5 / A+=7 → Y 轴 1.8/5.5/9.2）与 Y 轴数字标「20%/30%/40%」在 X 轴仅 1.8 / 5.5 / 9.2 三处，间隔过稀 → 应在 (3.65, 0) 和 (7.35, 0) 各加一条细垂直线。
5. **性价比之王 callout**：L66-67 十字瞄准箭头指向的绿色框「性价比之王 · 18x PE · 已验证涨价弹性」**左上角顶部与边框重叠** 0.15cm，"性"字被顶边切一半。
6. **Y 轴标签方向**：L19 Y 轴箭头标签写「确定性 → (声明可信度 A+/A/B+)」，但**实际轴标签位于 (0,11) 节点上方**，用户截图中箭头朝 Y 轴上方（正确）但文字写「A+」在顶部与「确定性」仅 1em 间隔，视觉拥挤 → 移到 `above left`（Y 轴左侧竖排）。

#### 数据一致性（对照表 8-1/8-2/8-3）
- Tier 1（A+ 高确定 3 只）：澜起 42x +32% / 北华 41x +27% / 中微 48x +32% ✓
- Tier 2（卫星）：江波龙 18x +38% / 拓荆 55x +29% / 深科 24x +33% / 通富 32x +24% / 长电 38x +27% / 兆易 36x +28% ✓
- 主题（B/C）：沪硅 72x +22% / 南大 48x +30% ✓
- 象限定位：澜起（+32%, A+）→ x≈6.0, y≈9.5 黄金/底仓之间 ✓

---

### 🔴 HIGH · 图 10-1 风险矩阵热力图

#### 版式 Bug（4 项）
1. **R1 气泡文字被上边框吞掉**：用户截图中右上角红区 RED 风险类的 `R1 \n HBM ASP -30% \n 供过于求` 三行中 "HBM ASP -30%" 和 "供过于求" 两行**上半部分被红粉色气泡顶边切 2mm** → 根因：`riskR/.style minimum size=2.2cm` 但 `HBM ASP -30% / 供过于求` 三行文字 0.48cm×3=1.44cm > 内盒可用空间（2.2cm - 2×inner sep=0pt = 2.2cm 但实际上 tikz circle 文字区域是圆形内切正方形 = 2.2/√2 = 1.56cm），三行 1.44cm 刚好贴顶；加上 font=\scriptsize\bfseries 行距 1.2，实际高度 1.6cm > 1.56cm → 溢出顶部。修法：R1/R2（red 类） minimum size 升到 2.4cm，或把三行文拆成 `R1\\[-0.1em] HBM ASP -30%\\[-0.1em] 供过于求` 压缩行距。
2. **X 轴 / Y 轴 标签 位置反转**：Y 轴标题「发生概率 (%) →」写在 X 轴（水平）末端。X 轴标题「影响程度 →」写在 Y 轴（垂直）顶端！**根因**：L24-25 两条 \draw node 写反了：
   - L24 横轴写的是 `\draw[axis, ->] (0,0) -- (11, 0) node[below right] {\large 发生概率 (\%) →};` ✓ 但用户截图中下方横写的是「发生概率 (%) →」✓，**用户截图实际显示正确**，我误读。再检查：左轴「影响程度 →」✓，底轴「发生概率 →」✓。问题其实是：**Y 轴左侧「高 / 中 / 低」三个刻度与对应的 8.75 / 5.25 / 1.75 Y 坐标仅用 `\node[left, ...]` 标，无刻度线** → 读者无法知道 8 大风险气泡各自落在哪一级（例如 R5 澜起份额 bubble 在 4.5 Y 坐标 = 中偏低，实际标「中」）。应在每个「低/中/高」节点加一条细灰虚线水平贯穿全图。
3. **风险色与气泡色不匹配**：legend 写「RED = HBM ASP / BIS 管制（粉红块）」，但 R1（HBM ASP -30%，应为 RED）实际气泡色是 **riskamber（橙黄色）**；R2（BIS 管制升级，应为 RED）实际气泡色是 **riskred!18（浅粉红，近似 ✓）**；R3（NAND 价格战，应为 AMBER）实际气泡色 riskamber ✓；R4（capex 下修，应为 AMBER）实际气泡色 riskamber ✓；R5（份额抢占，应为 AMBER）实际气泡色 riskamber ✓；R6-R8 绿 ✓。
   - **修法**：R1 bubble 从 riskR 改为 riskred（与 legend RED 一致），或把 legend RED 色块改成 riskamber 以匹配实际气泡 —— 推荐前者。
4. **气泡重叠严重**：R1（HBM）与 R2（BIS）的中心坐标 (7.2, 9.0) 与 (8.0, 7.6)，两者半径分别 1.1cm 和 1.1cm，距离 √(0.8²+1.4²) = 1.61cm < 1.1+1.1=2.2cm → 重叠 30%；R3 与 R4 中心 (6.5, 6.8)/(4.8,7.3) 距离 1.85 < 0.9+1.1=2.0 → 重叠。把 R1 从 (7.2, 9.0) 移到 (6.8, 9.3)，R3 从 (6.5, 6.8) 移到 (6.2, 6.2)，R5 从 (5.8, 4.8) 移到 (6.0, 4.5)。

#### 数据一致性（对照表 10-1 压力测试情景 & 风险矩阵）
- R1 HBM ASP -30%，RED，高影响 × 高概率 ✓（压力测试情景 D 主触发）
- R2 BIS 管制升级，RED，高影响 × 很高概率 ✓（情景 C/D）
- R3 NAND 价格战，AMBER，中高影响 × 中高概率 ✓（情景 C）
- R4 Hyperscaler capex 下修 >15%，AMBER，高影响 × 中等概率 ✓（情景 C）
- R5 澜起份额 <50%，AMBER，中影响 × 中高概率 ✓
- R6-R8 GREEN ✓
- 气泡大小=可监测性指标 ✓（R1 ASP 数据月度可得 → 较大；R6 长存扩产延迟需招标网月度 → 较小）

---

## 3. 修复优先级 & 工作量估算

### P0 必须修复（下一轮编译前必须处理，共 12 项）

| ID | 图表 | 修复项 | 预计修改 | 根因类 |
|---|---|---|---|---|
| P0-01 | **全局** | 删除图 5-1 版本 A（L9-91，第一份无柱上标的堆叠柱） | 删除 83 行 | Class D 重复图 |
| P0-02 | 图 3-1 | `ashar/.style` 改成 fill=white, draw=navy, text=deepnavy；逐 A1~A6 节点显式指定（与图 1-2 修法一致） | 改 2 行 + 加 6 处显式 | Class A（空块无文字） |
| P0-03 | 图 3-1 | `\faExclamationTriangle` 在 key stat 浮框改成 text mode `$\triangle$` 或 \faIcon 显式版本，避免乱码 `aExclamationTriangle` | 改 1 行 | Class B（符号乱码） |
| P0-04 | 图 4-2 | `ashare/.style` 同 P0-02 修法；Pool B、Pool D 显式指定 fill=white, text=navy, draw=riskred 边框（保持 A 股强调色的边框色） | 改 1 行 + 2 处 | Class A |
| P0-05 | 图 5-1（版本 B）| Samsung 62→42，SK Hynix 32→26，YMTC+CXMT 9→7；柱上 132★→92★；Y 轴 $B 单位与表 5-1 数值统一（表 5-1 亿≠B 注） | 改 3×5=15 处数值 | Class D（单位/数量级冲突）|
| P0-06 | 图 5-2 | 供给/需求卡片 text width 3.2→3.6cm，minimum height 1.0→1.2cm；BAL 块改为 fill=navy + text=white（深蓝底白字，高对比度）；底部 BLOCK 治理注 x 从 5.8→5.2, text width 12.5cm | 改 3 行 style + 1 注 | Class A+D |
| P0-07 | 图 6-1 | 每个 scope 首行强制 `\def\a{90}`；legend 加「Other (铠侠/Solidigm) = steelgrey!60」；Samsung 24%/27%/30% 标签从蓝片移到绿片（swap fill 顺序或直接把切片文字锚改对应色片） | 改 3 scope + 1 legend | Class C（饼切片色 swap）|
| P0-08 | 图 8-1 | 四条象限文字从 (5.5,5.5) 十字锚点移到各象限中心 I=(8.3,8.3)/II=(2.7,8.3)/III=(2.7,2.7)/IV=(8.3,2.7)；Tier 1 dot fill 升到 navy!65 与 legend 对应 | 改 4 行节点 + 1 style | 版式重叠+配色 |
| P0-09 | 图 10-1 | R1 bubble 从 riskR 改 riskred（与 legend RED 一致）；R1/R2 minimum size 升到 2.4cm 防止文字溢出 | 改 2 行 style | 颜色+裁切 |
| P0-10 | 图 2-1 | subp/.style minimum height 0.8→1.1cm，inner sep 2→4pt；底部 AStock 结论蓝块 minimum height 1.1→1.4cm，text width 14→14.4cm | 改 2 行 style | 版式裁切 |
| P0-11 | 图 5-2 | 需求卡片 D1/D5 resizebox 0.80→0.92，右边界加 2em 留白，或卡片 text width 3.2→3.8 | 改 1 resizebox | 右裁文字 |
| P0-12 | **全局 preamble** | `\usepackage[fixed]{fontawesome5}` 的缺字降级：`\def\faExclamationTriangle{\ensuremath{\blacktriangle}\kern-0.25em}` 等兜底，禁止输出 `aExclamationTriangle` 文本 | 改 1 行宏 |  Class B（根上封） |

### P1 应修复（美观度，不阻塞发布，共 5 项）
| ID | 图表 | 修复项 |
|---|---|---|
| P1-01 | 图 7-1 | 15 条柱按类别拆 6 个 `\addplot`，对应 legend 6 色；symbolic y coords 与 coordinates 逐行对齐（解决长电/兆易柱-数字错位）；来源注与 x 轴间隔 1em |
| P1-02 | 图 7-1 | 图题加注「注：本图为 2026-06-23 收盘总市值（亿人民币·现价），非 26E 合理估值」，与表 7-1 区分 |
| P1-03 | 图 6-1 | 2025E Samsung 24% 标签与 Other 4% 标签去重叠（Samsung 24% 移到 280° 1.35r） |
| P1-04 | 图 10-1 | 在「高/中/低」三处左标加三条水平虚线；R1 与 R2、R3 与 R4 气泡去重叠（微调坐标） |
| P1-05 | 图 4-2 | SW1→P1 连线改为 `-|`（先竖后横）；在 Pool C 左下角加 tiny 字「海外映射（非A股）」 |

### P2 可选修复（语义优化，共 3 项）
| ID | 修复项 |
|---|---|
| P2-01 | 图 3-1 L6 整机集成价值占比从「-」→「[整机毛利 <2%，不计链上利润]」避免读者误解 |
| P2-02 | 图 5-1 柱上标统一加 `\$X\mathrm{B}$` 单位，避免百亿/十亿歧义 |
| P2-03 | 图 8-1 Y 轴「确定性 →」改为竖排 `rotate=90, anchor=south`；X 轴 (3.65, 0)/(7.35,0) 加 25%/35% 辅助刻度 |

**P0 工作量估计**：12 项，单轮 XeLaTeX 2×5 min = 10 min，修改本身约 40 min → 总计 1 小时可完成。修复顺序：P0-12（根）→ P0-01（删重复图）→ P0-02/P0-04（A类空块）→ P0-05（数据冲突）→ P0-03/P0-12（符号乱码兜底）→ P0-06/P0-11（5-2 裁字）→ P0-07（饼色）→ P0-08~10（8-1/10-1 配色）→ P0-10（2-1 裁切）→ 二遍 XeLaTeX → Overfull >20pt 断言 → SYNC push。

---

## 4. PASS 项（已验证正确，无需修改）

✅ **所有表格的列宽与 Overfull \(\hbox > 20pt\) 清零**（95b4080 → f5fdcfb，MAX=17.3pt，机构接受标准 <20pt）  
✅ **ch01 图 1-2 深蓝空块 5 个**（已在 f5fdcfb 中修复，white fill + navy draw + deepnavy text）  
✅ **表 6-1 国产 HBM 综合评估列首 24pt 空块**（p{1.8→2.1cm} 已修复）  
✅ **表 8-1 / 表 3-1 / 表 2-2 的最大 157.8pt Overfull**（分别在上一轮修复）  
✅ **表 A-1 longtable 末列 12pt Overfull**（列宽精确解算修复）  
✅ **图 5-2 供需桥接图 数据逻辑**（全部 4 供给 × 5 需求 × 平衡块数值与正文一致）  
✅ **图 6-1 三家原厂 三年饼图 份额加总 = 100%（±0.01% 浮点舍入内）**  
✅ **图 10-1 风险 8 大类 与 表 10-1 情景 C/D 触发条件 一一映射**  
✅ **表 7-1 footer multicolumn**（\(\text{exhibitwidth}-2\tabcolsep\) 扣减修复）  
✅ **App D §数据质量警示 36.3/29.0pt Overfull**（`\slash` + 逗号断长句修复）

---

## 5. 二次验收标准（下一轮 review 前必须满足）

P0 全部 12 项修复 + 二遍 XeLaTeX 编译 + 如下 5 项硬断言：

1. **Overfull \(\hbox > 20pt\) COUNT = 0**（MAX < 17.5pt 维持）
2. **视觉无深蓝空块**：图 3-1 右侧 6 个 A* 节点、图 4-2 Pool B/D、图 5-2 中间 bal 块，任何含节点的 fill 与 text 必须对比度 > 4:1（WCAG 最低）
3. **饼图/柱图 legend ↔ 切片/柱色 语义 100% 一致**：人工对照 legend tabular 颜色与渲染后各切片/各柱最外描边色
4. **单位一致性**：全文 `亿 = \$100 \text{ million} = 0.1 \text{B}` 统一 —— 图 5-1 柱图（B 单位）× 10 = 表 5-1「亿美元」列的中点值 ±15%
5. **文字无裁切**：图 2-1 subp 首字 / 图 5-2 卡片右 2 字 / 图 10-1 R1 气泡顶部 ，任何图元含字符的框 0.5em 留白

若 5 项全部 PASS，本报告的 R2 审查结论改为 **PUBLISH READY**。

---

**Reviewer**: AStock Research QA Agent（视觉版式审查流水线 v1）
**Reviewed**: 2026-06-24
**Status**: 🚫 REJECT — 需 P0 全部修复后重审（预计 R2 耗时 1h）
