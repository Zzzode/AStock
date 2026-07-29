# 中国船舶（600150.SH）Segment Valuation Model

**口径结论：** 本案例只有一个 valuation parent：`600150.SH`。全部船厂、设备企业及其他经营子公司都是 **consolidated components**，不构成独立 investable ticker。本文使用分析性 segment 桥理解合并 `revenue` 与 `net profit`，但不做子公司 `SOTP`，不赋 standalone `multiple`；所有 `sensitivity` 最终回到 600150 合并 EPS，`validation trigger` 由正式半年报和后续交付数据触发。

## Parent / Component Boundary

| Node | Machine classification | Equity treatment | Allowed valuation use | Prohibited use |
|---|---|---|---|---|
| N15 / 600150.SH | sole `core_valuation` node / valuation parent | 唯一可估值上市权益 | 合并收入、毛利、归母净利润、EPS 与 cycle-normalized PE | 无 |
| 下属船厂、设备与其他经营子公司 | `consolidated_component` | 已包含在 600150 合并报表 | 交付、价格/结构、毛利和现金敏感性 | 单独目标价、子公司 multiple、加总 SOTP |
| 中国动力等参股边界 | equity-boundary context | 不作为合并 revenue 归属 | 只作边界说明 | 把参股公司收入并入 600150 |
| 沪东中华、未披露军品及集团期权 | perimeter exclusion / option only | 未进入已验证上市公司盈利桥 | 监控正式公告 | 资产注入 SOTP、军品 SOTP、集团订单溢价 |

R0 PASS 已确认机器分类恰好只有一个 valuation parent。中远约 500 亿元/87 艘项目由 600150 子公司承建，但包含意向成分，且已在聚合订单/在手口径内；它只验证客户和订单质量，增量 revenue、net profit、EPS 与估值信用均为 0。

## Analytical Segment Bridge

Growth / Base 拆分是研究分析口径，不是公司新披露分部：

| 2025A analytical segment | Revenue | Gross margin | Gross profit | Role |
|---|---:|---:|---:|---|
| Growth：船舶造修及海洋工程 | 1,312.7873 | 11.72% | 153.86 | 由有效交付 DWT、价格/结构与收入确认驱动 |
| Base：配套、机电及其他 | 206.9926 | 18.04% | 37.34 | 合并底盘；不证明独立业务纯度 |
| Consolidated total | 1,519.7799 | 12.58% | 191.19 | 与合并利润表机械勾稽 |

```text
Growth revenue_t
= effective delivery DWT_t
× 95.981524 CNY100m per million DWT revenue-intensity proxy
× price/mix index_t
× recognized revenue ratio_t

Consolidated parent net profit_t
= [consolidated gross profit - operating expenses - impairment
   + finance/investment/other net]
× (1 - tax rate)
× (1 - minority interest share)
```

95.981524 亿元/百万 DWT 是含造船、修船、海工和进度确认的 revenue-intensity proxy，不是船型 ASP。未披露的逐船 ASP、排程、利用率、付款节点、成本传导和质保风险阻断船型/船厂 SOTP。

## Scenario Revenue and Margin

| Scenario / Year | Growth Revenue | Base Revenue | Consolidated Revenue | Growth GM | Base GM | Consolidated GM |
|---|---:|---:|---:|---:|---:|---:|
| Bear 2026 | 1,442.49 | 210.00 | 1,652.487134 | 14.0% | 15.5% | 14.1906% |
| Bear 2027 | 1,426.28 | 215.00 | 1,641.275854 | 13.5% | 15.5% | 13.7620% |
| Bear 2028 | 1,441.22 | 225.00 | 1,666.216339 | 12.8% | 15.0% | 13.0971% |
| Base 2026 | 1,552.41 | 222.59 | 1,775.000000 | 16.8% | 16.0% | 16.6997% |
| Base 2027 | 1,779.28 | 220.72 | 2,000.000000 | 17.5% | 15.7% | 17.3014% |
| Base 2028 | 1,916.74 | 233.26 | 2,150.000000 | 17.8% | 15.2% | 17.5179% |
| Bull 2026 | 1,708.11 | 226.89 | 1,935.000000 | 18.5% | 16.5% | 18.2655% |
| Bull 2027 | 1,960.33 | 244.67 | 2,205.000000 | 19.5% | 17.0% | 19.2226% |
| Bull 2028 | 2,188.38 | 259.62 | 2,448.000000 | 20.2% | 17.5% | 19.9137% |

## Consolidated Net Profit and Valuation

Growth 与 Base 没有可验证的税、少数股东、投资收益和费用分配，因此不发布 segment net profit 或 standalone EPS。只有合并归母可以进入 multiple：

| Scenario / Year | Consolidated Parent NP | EPS | OCF/NP | Valuation role |
|---|---:|---:|---:|---|
| Bear 2027 | 93.715809 | 1.245290 | 0.65x | 1.245290 × 9.0x = **11.207610** |
| Base 2026 | 172.762156 | 2.295653 | 0.85x | 14x 交叉 = **32.139142** |
| Base 2027 | 216.489959 | 2.876705 | 0.95x | 主方法：2.876705 × 11.5x = **33.082108** |
| Base 2028 | 246.810914 | 3.279608 | 1.00x | 9x 交叉 = **29.516472** |
| Bull 2027 | 279.849133 | 3.718618 | 1.10x | 3.718618 × 13.0x = **48.342034** |

多锚目标沿用估值主表：

```text
33.0821075 × fundamental 85%
+ 33.02 × market 15%
+ not-disclosed Street target × broker 0%
= 33.072791375 ≈ published final target 33.07
Published upside = 33.07 / 33.02 - 1 = +0.1514%
```

对应动作严格为 **中性偏多（持有/等待验证） / event-driven validation**，不是买入。

## Why Segment / SOTP Is Blocked

| Missing input | Blocked method | What remains allowed |
|---|---|---|
| 逐船价格、合同排程、船型毛利 | ship-type ASP / contract SOTP | 合并价格/结构与 GM sensitivity |
| 逐厂收入、net profit、utilization、capex 与现金归属 | yard-level SOTP / subsidiary multiple | 合并交付和现金转化情景 |
| 军品订单、利润和上市公司归属 | military SOTP | 能力背景，估值 0 信用 |
| 沪东中华交易范围、价格、盈利和股本影响 | injection SOTP | perimeter exclusion，估值 0 信用 |
| 集团未分配订单 | group-order option value | 监控，不进入 revenue/EPS |
| 可靠原始券商目标价 | Street target anchor | Street 盈利预测对照；broker weight 0 |

对子公司使用独立 multiple 再与 600150 合并价值相加，会对同一 revenue 和 net profit 重复计价。即便 Growth 占比接近 90%，也不能把合并公司改分类为“纯高成长分部”并套用 PS/PEG 溢价。

## Sensitivity and Validation Trigger

冻结增长模型给出的 2026 Growth GM sensitivity 为：在其余变量保持 Base、确认系数 0.96 时，Growth GM 每变化 1 个百分点，归母净利润约变化 13.28 亿元，EPS 约变化 0.176 元；按 11.5x 观察，相当于每股价值约变化 **2.02 元**。该敏感性只用于合并压力测试，不代表 Growth standalone value。

| Variable | Bear | Base | Bull | Validation trigger | Downgrade trigger |
|---|---:|---:|---:|---|---|
| 2026 effective delivery | 15.5m DWT | 16.2m DWT | 16.8m DWT | 正式交付接近 16.5m DWT 计划 | 明显低于计划且非船型差异 |
| Price/mix index | 1.01 | 1.04 | 1.07 | 收入强度、船型结构正式披露 | 高端占比或收入强度回落 |
| Recognized revenue ratio | 0.96 | 0.96 | 0.99 | 收入、合同资产与交付同步 | 存货/合同资产增加但 revenue 不确认 |
| 2026 Growth GM | 14.0% | 16.8% | 18.5% | H1 核心业务 GM ≥11.72%并改善 | 正式口径 <10.5%或同比逆转 |
| OCF/parent NP | 0.55x | 0.85x | 1.05x | H1 OCF 为正；全年 ≥0.8x | 全年 <0.8x且无次期回收 |

正式 2026H1 的 validation trigger 是归母至少 101 亿元、扣非至少 99 亿元、核心业务 GM 不低于 11.72%、OCF 为正且营运资金没有异常堆积。任一关键口径破坏合并数学勾稽时，segment、盈利和 valuation 必须整体重跑，不能只替换目标价。

## Model Boundary Verdict

- `segment/SOTP`: **blocked** for subsidiaries, yards, ship types, military and injection options.
- `revenue`: only consolidated scenario revenue receives valuation credit.
- `net profit`: only consolidated parent net profit/EPS is valued.
- `multiple`: only 600150.SH receives the 2027E cycle-normalized PE.
- `sensitivity`: delivery, price/mix, recognition, Growth GM and OCF conversion.
- `validation trigger`: formal H1 profit, margin, cash conversion and delivery evidence.

该边界保证 600150 是唯一 valuation parent，子公司始终保持 consolidated components，不产生重复估值。
