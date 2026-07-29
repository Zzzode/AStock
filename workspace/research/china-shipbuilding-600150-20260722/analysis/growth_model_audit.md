# 中国船舶增长盈利模型审计

**审计对象：** `analysis/growth_earnings_model.md`、`analysis/earnings_forecast.md`、`data/growth_earnings_model_20260722.json`、`data/growth_earnings_model_current.json`  
**数据截止：** 2026-07-22  
**模型口径：** 同控合并后的 600150 持续经营口径  
**Gate Status：** `CONDITIONAL`  
**Model Reproducibility：** `PASS`

`Model Reproducibility: PASS`

`CONDITIONAL` 指逐船 ASP、排程、利用率、付款节点和成本传导仍未披露，故只允许合并口径年度情景；`PASS` 仅指模型披露的数学关系已复算通过，不代表上述证据缺口已经消失。

## 审计结论

| 检查 | 结果 | 结论 |
|---|---|---|
| 法定口径 | 2025A 使用重述持续经营口径；未把 legacy 2024 与合并后 2025 拼接 | PASS |
| 股本 | 2026E 起统一使用 75.25621288 亿股；2025A 保留披露加权股本逻辑 | PASS |
| Base / Growth | 2025A growth 1,312.7873 + base 206.9926 = 1,519.7799 | PASS |
| 订单治理 | 4,674.51 亿元 gross backlog 仅作覆盖校验；未直接计入收入 | PASS |
| 交付到收入 | 有效 DWT × 2025 收入强度 × 价格/结构 × 确认系数 | PASS |
| 毛利 | Growth 毛利 + Base 毛利 = 合并毛利 | PASS |
| 归母与 EPS | PBT→税→合并净利润→少数股东→归母→EPS 全链可复算 | PASS |
| H1 | 使用 92—110 亿元预告做残余检验，未采用 H1×2 或 Q1×4 | PASS |
| 现金 | OCF/归母、营运资金投入、资本开支和 FCF 可复算 | PASS |
| Street | 仅使用 5 份合并后原始报告；合并前预测和弱目标价为 0 权重 | PASS |
| 零信用边界 | 军品、集团未分配订单、沪东中华、弱目标价未进入任何情景 | PASS |
| JSON twins | 两个结构化文件字节一致 | PASS |

## 关键复算

### 1. 当前市值

```text
33.02 元/股 × 75.25621288 亿股 = 2,484.960149 亿元
```

### 2. 2025A Base / Growth 与毛利

```text
growth revenue = 1,312.7873
base revenue   = 1,519.7799 - 1,312.7873 = 206.9926
total revenue  = 1,312.7873 + 206.9926 = 1,519.7799

total gross profit
= 1,519.7799 - 1,328.5858
= 191.1941

growth gross profit
= 1,312.7873 × 11.72%
= 153.8587
```

Base gross profit 为总毛利减 Growth 毛利，包含配套/机电/其他主营和非主营分产品表的其他营业收入；这不是独立可估值分部。

### 3. 2026 Base 收入

```text
2025 revenue-intensity proxy
= 1,312.7873 / 13.6775
= 95.981524 亿元 / 百万 DWT

2026 growth revenue
= 16.2 × 95.981524 × 1.04 × 0.96
= 1,552.412854

2026 total revenue
= 1,552.412854 + 222.587146
= 1,775.000000
```

`95.981524` 是收入确认强度，不是船型 ASP。2025 年末在手订单换算只作覆盖检查：`1,552.412854 / 4,674.51 = 33.2%`；该比率没有被当作法定履约进度或固定年度摊销率。

### 4. 2026 Base 毛利到归母

```text
growth gross profit = 1,552.412854 × 16.8% = 260.805360
base gross profit   =   222.587146 × 16.0% =  35.613943
gross profit        = 296.419303
gross margin        = 296.419303 / 1,775 = 16.6997%

profit before tax
= 296.419303 - 128.0 - 3.0 + 36.5
= 201.919303

consolidated net profit
= 201.919303 × (1 - 8.0%)
= 185.765759

parent net profit
= 185.765759 × (1 - 7.0%)
= 172.762156

EPS
= 172.762156 / 75.25621288
= 2.295653 元/股

PE
= 33.02 / 2.295653
= 14.3837x
```

### 5. 2026 Base 现金

```text
OCF = 172.762156 × 0.85 = 146.847832

working-capital investment
= consolidated net profit + D&A + other non-cash/reclassification - OCF
= 185.765759 + 50.0 - 15.0 - 146.847832
= 73.917926

FCF = 146.847832 - 50.0 capex = 96.847832
```

OCF/归母是现金转化观察指标，不代表归母利润与合并经营现金流在会计口径上完全同源。

### 6. 当前价隐含

```text
2026 implied parent NP at 14x = 2,484.960149 / 14 = 177.497154
2027 implied parent NP at 11x = 2,484.960149 / 11 = 225.905468
2028 implied parent NP at  9x = 2,484.960149 /  9 = 276.106683
```

在其他基础假设不变且少数股东占合并净利润固定为 7% 时，上述 2026/2027/2028 结果分别要求 growth GM 约 17.16%、综合 GM 约 17.85%和综合 GM 约 19.13%。三项均高于 House Base；2028 隐含要求尤其显著高于 House Base 17.52%。

## 三情景数学一致性

对每个情景、每个年度均执行以下恒等式，容差为 0.01 亿元或 0.0001 元/股：

1. `growth_revenue + base_revenue = revenue`
2. `growth_revenue × growth_GM + base_revenue × base_GM = gross_profit`
3. `gross_profit / revenue = gross_margin`
4. `gross_profit - operating_expenses - impairment + other_net = PBT`
5. `PBT × (1-tax_rate) = consolidated_net_profit`
6. `consolidated_net_profit × (1-minority_share) = parent_net_profit`
7. `parent_net_profit / 75.25621288 = EPS`
8. `33.02 / EPS = current_PE`
9. `parent_net_profit × OCF_conversion = OCF`
10. `OCF - capex = simplified_FCF`

9 个情景年度组合全部通过；Markdown 展示值为四舍五入，JSON 保留至少 6 位小数。

## Street 对照审计

| 年度 | House 归母 | Street 均值 | Street 中位 | House vs 均值 | House vs 中位 |
|---|---:|---:|---:|---:|---:|
| 2026E | 172.7622 | 179.02 | 176.38 | -3.50% | -2.05% |
| 2027E | 216.4900 | 238.55 | 235.38 | -9.25% | -8.03% |
| 2028E | 246.8109 | 298.08 | 299.43 | -17.20% | -17.57% |

Street 样本为 `BR-01—BR-05`；4 份合并前 44.7243 亿股报告不进入当前横截面。华泰 58.96 元仅为第三方预览且权重 0；国泰海通 47 元线索没有可审计正文，所有预测、倍数、目标价和上行字段均不得进入模型。

## R0 blocked_method / required_sensitivity 消费审计

| 缺口 | 被禁止方法 | 已采用方法 | 已消费敏感性 | 结果 |
|---|---|---|---|---|
| 逐船排程缺失 | gross backlog 直线摊销 | 合并年度有效交付 | DWT、确认系数 | PASS |
| 船型 ASP 缺失 | DWT×船型 ASP | 2025 收入强度代理 | 价格/结构指数 | PASS |
| 利用率缺失 | 名义产能资本化 | 实际/计划交付约束 | Bear/Base/Bull DWT | PASS |
| 付款节点缺失 | 合同负债直接推现金 | OCF/归母与营运资金桥 | 0.55x—1.15x | PASS |
| 成本传导缺失 | 假设船价完全转毛利 | 分业务毛利率情景 | 2026 Growth GM 14.0%—18.5%及二维表 | PASS |
| 撤单条款缺失 | 总在手订单直接收入/EPS | 覆盖校验、无滚存 | 确认系数 0.92—1.00 | PASS |
| 中远 500 亿元/87 艘含意向 | 单独叠加订单或 EPS | 归属确认、聚合口径内去重 | 增量信用 0 | PASS |
| 军品/集团项目/沪东中华 | 独立 SOTP 或期权加值 | 仅监测 | 全情景 0 信用 | PASS |

## 假精度与残余风险

- 交付 DWT、价格/结构指数、确认系数、税率和少数股东占比均为研究假设，不得写成公司指引。
- 2025 收入强度包含修船、海工和履约进度差异，不能叫“单船 ASP”或用于逐船估值。
- 2026Q1 少数股东占合并净利润约 6.54%；Base 使用 7%，Bear 使用 15%/18%/20%，Bull 使用 4%，不把单季结构永久化。若后续回到 2025A 约 25.35%的较高水平，应直接下调归母利润而非调高分部估值。
- 2025 OCF/归母接近 1 倍不否定其同比下降；生产爬坡的绝对营运资金需求仍是核心风险。
- 2028 Base 的利润增长依赖毛利率小幅上升与费用效率，若正式披露不能验证，需降低正常化盈利和估值倍数。
- 模型不输出目标价；现价隐含倍数只是交给估值模块的约束，不可直接当作投资结论。

## 发布条件

R1 模型数学已通过，但发布仍要求：R0 复审达到 0 个开放 S、0 个开放未豁免 A；R1 估值模块独立复算并消费本模型；正式报告明确所有零信用边界。任何后续数据变化都必须同步更新两个 JSON twins、两份模型正文和本审计。
