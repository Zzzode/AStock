# 建滔积层板 (01888.HK) — Evidence Card

<!--
Recommended placement:
  - ch04 supply_chain (产业链图谱 + 公司关系矩阵): 作为全球 CCL 龙头、量价风向标/AH 锚，必须补入"高频高速 CCL"环节与生益/华正/南亚的全球竞争坐标；当前 ch04 仅列 A 股 CCL，缺全球定价锚，01888 正是该锚。
  - ch06 companies (公司章 watchlist / AH 锚注脚): 不作 A 股持仓推荐，作为"港股 CCL 风向标 + A/H 估值锚"列入 watchlist/参照系卡，类似胜宏 H 股桥的处理范式（非可比 A 股价格，仅作公开外资情景上沿与产业链验证）。
  - ch08 valuation (估值章 + 情景表): 港股目标价区间（国信 82.33--89.39 / 花旗 120 港元）作为高端 CCL 涨价情景的"港股信号灯"引用；CCL 涨价 >50% 是高端 CCL/AI PCB 估值上行的外生确认，写入图表21/22 的全球估值分歧佐证。
Boundary: 港股标的，CLI financials 不支持 HK（01888.HK 返回 NoneType 错误），财报数据来自公开年报/研报转载（非原始 PDF 比对）。非本报告 A 股持仓推荐；仅作产业链锚 + 估值信号 + watchlist。Rubin/optical 敞口为结构性推断，无已确认订单披露。
-->

**Ticker:** 01888.HK（港交所主板，港股通标的）
**调研日期:** 2026-06-18
**Card type:** 港股上游 CCL 风向标 / AH 估值锚扩充调研（watchlist + 产业链参照系，非 A 股持仓）
**Source kernel:** `astock.cli news 01888.HK --days 60`（OK，返回公司事件流）+ WebSearch 公开年报/研报转载。`astock.cli financials 01888.HK` **不支持 HK 代码**（返回 `Failed to fetch financial data: 'NoneType' object is not subscriptable`），财务数据改取公开年报/券商研报。

---

## 1. 业务定位 (Business Positioning)

- **全球覆铜板（CCL）龙头**：建滔积层板（Kingboard Laminates Holdings）2006 年 12 月上市，是全球最大 CCL 制造商之一，亦是 **A 股 CCL 三家（生益 600183 / 华正 603186 / 南亚 688519）的全球定价锚与量价风向标**。
- **垂直一体化护城河**：覆盖铜箔 → 玻璃纤维布 → 环氧树脂 → 覆铜板全产业链，一体化程度在 CCL 全球龙头中仅次于台光电（台光）。毛利率水平行业中仅次于台光，优于台燿、生益等同业。
- **业务结构**：建滔积层板（01888）专注覆铜板（CCL），覆铜板盈利贡献占主导；与母公司建滔集团（00148.HK，含 PCB/化工/物业多元业务）做了明确切分。普通 FR-4 覆铜板占 01888 营收 **七成以上**，高端 low-loss / ultra-low-loss 占比持续提升。
- **议价权**：下游 PCB 厂商高度分散（全球前十大 CCL 2024 年占比约 77%，ch04 已有热力图证据），建滔作为龙头在涨价周期中成本传导能力显著强于下游 PCB。

---

## 2. AI-PCB 链敞口 (AI-PCB-Chain Exposure)

### 2.1 业务分部与 AI 相关性
| 分部 | 2024 营业额 | AI-PCB 链角色 |
|---|---:|---|
| 覆铜板（CCL） | **183.05 亿港元**（+11% YoY） | 核心。AI 服务器 / 交换机 / 光模块基材；high-M-grade low-loss 主战场 |
| 其他（铜箔/玻纤布/树脂内部配套） | 一体化内部消化 | 垂直一体化成本优势来源 |

### 2.2 AI 服务器 / Rubin / 光模块相关性
- **AI 服务器**：high-M-grade（M6/M8/M9 级）ultra-low-loss 覆铜板需求爆发，是 2024--2026 业绩核心驱动；建滔为全球少数能量产 high-M-grade 的 CCL 厂之一（与台光、生益、斗山、松下同列第一梯队）。
- **Rubin（前瞻性）**：Rubin 为 NVIDIA Blackwell 之后下一代 GPU 架构，对应更高速率 PCB 基材（M10+ / ultra-low-Df）。建滔作为 NVIDIA AI 服务器 PCB 基板核心 CCL 供应商（通过下游 PCB 厂间接进入），是 Rubin 放量下 CCL 端弹性最大的港股标的。
- **光模块 / 800G/1.6T**：高速 CCL 亦是 800G/1.6T 光模块母板与交换机板的关键基材，与 ch04 光模块需求节点联动。
- ⚠️ **证据边界**："Rubin 专用 CCL 订单/收入"无公开披露；high-M-grade 具体 ASP、客户平台单价、销量均未在 01888 公开年报中拆分。上述为基于全球 CCL 龙头地位 + 涨价周期的结构性推断，非已确认订单。

### 2.3 涨价周期（AI-PCB 链最强外生信号）
- **2025H2--2026 累计提价 >50%**（普通 FR-4 + high-M-grade 双线涨价），是 ch04 CCL 涨价叙事、ch08 估值上行情景的最强公开佐证。
- 光大证券指出 AI 基础设施对 CCL 需求强劲，**强周期预计至少延续至 2027 年**。

---

## 3. 财务快照 (Financial Snapshot)

**⚠️ CLI 边界：** `astock.cli financials 01888.HK` **不支持港股**（AkShare financial abstracts 仅覆盖 A 股）。下表数据来自公开年报/券商研报转载（同花顺 F10 / 证券时报 / 国信研报），**非原始 PDF 比对，数据质量 = 公开转载（E2/E3）**。

| 指标 | 2025 全年（港元） | 同比 | 备注 |
|---|---:|---:|---|
| 营业额 | **~204 亿** | **+10%** | 覆铜板部门 183 亿为主 |
| 毛利润 | ~39.9 亿 | +21.7% | — |
| 毛利率 | **~19.6%** | +1.9 pct | 仅次于台光；A 股生益 2025 报 ~28% 因含 PCB 子公司口径不可比 |
| 股东应占净利润 | **~24.4 亿** | **+84%** | 利润弹性远大于收入（一体化 + 涨价） |
| 2026--2028E 归母净利 CAGR（国信） | **~45.6%** | — | 券商模型，非官方 |

**A/H 锚参照：** 建滔积层板 01888 专注 CCL，可与 A 股生益（600183，CCL+PCB 子公司）、华正（603186，高速 CCL/CBF/BT）做 CCL 环节全球坐标对比，但**口径不可直接比较**（建滔纯 CCL，生益含 PCB 子公司，华正规模小得多）。作"全球 CCL 量价风向标"引用，不作 A 股价格隐含上行/下行。

---

## 4. 估值信号 (Valuation Signal)

| 来源 | 评级 | 目标价（港元） | 依据 / 备注 |
|---|---|---:|---|
| 国信证券（首次覆盖，2025-06-17） | 优于大市 | **82.33 -- 89.39** | 全球 CCL 龙头 + 垂直一体化；2026--28E 归母净利 CAGR 45.6% |
| 花旗 | 买入 | **120**（上调） | 覆铜板 6 月均价涨幅超预期；此前版本 66 / 51 港元 |
| 市场表现（年内） | — | 股价一度飙升 **+570%**；52 周区间 8.76 -- 58.85 港元 | 半年市值暴涨约 2200 亿港元 |
| 港股通资金 | — | 南向连续 8 日净买入，累计 **96.53 亿港元**，股价 +78.93% | A 股资金端对港股 CCL 龙头的定价参与 |
| 股息率 | — | ~0.74% | 增长股属性，非高息 |

**信号解读：** 建滔目标价区间（国信 82--89 / 花旗 120 港元）与 A 股生益（高盛 217.6 元 / 花旗 195 元，见 ch08 图表21）构成 **CCL 环节 A/H 双锚**。建滔涨幅 +570% + 涨价 >50% 是 ch08 估值上行情景"高端 CCL 紧缺延续"的最强公开确认；反之若建滔涨价见顶/股价反转，则是 A 股 CCL/PCB 估值拥挤度预警信号。

---

## 5. 证据边界 (Evidence Boundary: Public vs Needs-IR)

### 已有公开证据
- 营业额 / 净利 / 毛利率：年报公开（同花顺 F10 / 证券时报转载）。
- 涨价周期（>50%）：多家券商与媒体公开报道，方向一致。
- 港股通资金流：交易所/证券时报公开。
- 券商目标价（国信 / 花旗）：研报公开，但本卡引用多为**转载非原始 PDF**（与胜宏 H 股 JPM 转载同处理范式，仅作公开外资情景上沿）。

### 需 IR / 非公开
- **分部级**：high-M-grade（M6/M8/M9/M10）CCL 的具体 ASP、销量、客户平台单价、毛利率 —— 年报未拆分，需 IR 或付费数据库（CMBI / TrendForce CCL tracker）。
- **客户平台级**：NVIDIA Hopper/Blackwell/Rubin 各平台 CCL 用量与单价 —— 无公开披露。
- **产能级**：high-M-grade 产能 / 利用率 / 在建项目经济性 —— 年报未给项目级桥，需 IR。
- **CLI 结构化数据**：01888.HK 无法通过 `astock.cli financials` 获取（港股不在 AkShare 覆盖范围），所有财务数字均来自公开转载，未经原始 PDF 比对，**数据质量上限 E2/E3**。

### 与本报告的接口
- **ch04**：作为"高频高速 CCL"环节的全球龙头锚补入产业链图谱与公司关系矩阵（当前仅 A 股，缺全球坐标）。
- **ch06**：watchlist / AH 锚注脚卡，**非 A 股持仓推荐**；处理范式参照胜宏 H 股桥（不作 A 股价格可比）。
- **ch08**：港股目标价 + 涨价 >50% 作为高端 CCL 估值上行情景的外生确认信号写入估值分歧表 / 情景表。

---

## Sources

- [同花顺 F10 - 建滔积层板 01888 基本面](https://basic.10jqka.com.cn/176/HK1888/)
- [证券时报 - 建滔积层板 2025 年度业绩](https://www.stcn.com/article/detail/3678621.html)
- [国信证券研报 - 建滔积层板优于大市，目标价 82.33--89.39 港元（钛媒体转载）](https://www.tmtpost.com/nictation/8031302.html)
- [AAStocks - 建滔积层板股价飙升 570%，光大证券指 AI 强周期延续至 2027](https://www.aastocks.com/sc/stocks/analysis/stock-aafn-con/01888/GLH/GLH2504833L/hk-stock-news)
- [富途牛牛圈 - 建滔积层板 AI 周期破局股（FR-4 占七成，2025H2--2026 累计涨价 >50%）](http://www.moomoo.com/hans/community/feed/fundamental-analysis-jiantao-laminate-01888-an-ai-cycle-breakout-stock-116724242317318)
- [证券时报 - 南向资金连续 8 日净买入建滔系 96.53 亿港元](https://www.stcn.com/article/detail/3967330.html)
- [Yahoo Finance / SL886 - 花旗上调建滔积层板目标价至 120 港元](https://hk.finance.yahoo.com/news/%E5%BB%BA%E6%BB%91%E7%A9%8D%E5%B1%A4%E6%9D%BF-01888-hk-%E5%8D%87%E8%BF%877-%E5%89%B5%E6%96%B0%E9%AB%98-024425418.html)
- [新浪财经研报 - 建滔积层板 AI 驱动高端材料跃迁](https://stock.finance.sina.com.cn/hkstock/view/hk_report.php?reportid=833210012645)
- CLI: `astock.cli news 01888.HK --days 60`（公司事件流 OK；2026-06-17 港股 PCB 概念低开、建滔积层板跌 5%；南向资金大举抛售阿里/中海油追涨建滔系）
- CLI 边界: `astock.cli financials 01888.HK` → `Failed to fetch financial data: 'NoneType' object is not subscriptable`（港股不覆盖）
