# 中国船舶（600150.SH）R1 估值模型

**估值日：** 2026-07-22  
**币种：** 人民币；金额单位除每股值外均为亿元  
**当前价 / 股本 / 市值：** 33.02 元 / 75.25621288 亿股 / 2,484.960149 亿元  
**结论：** `中性偏多（持有/等待验证） / event-driven validation`。公允价值区间 **31.64—35.96 元**，多锚最终目标价 **33.07 元**，按发布目标价相对现价 **+0.15%**。当前价格基本等于独立基础价值，新增资金应等待半年报把利润率、归属和现金转化同时坐实。

本模型使用冻结的增长盈利包，不重估其经营假设。主方法是 **2027E cycle-normalized PE**：2027E Base EPS 2.876705 元乘 11.5 倍得到 33.082108 元。2026E、2028E PE 与 OCF/归母只作交叉验证；货币资金不机械加回股权价值。原始券商 PDF 均无可用目标价，所有 Broker/Street 目标价 `valuation_weight=0`。

## Final Valuation Table

| Ticker | Current Price/Date | Shares | Market Cap | 2026E Revenue | 2026E NP/EPS | Method | Bear | Base | Bull | Final Target/Fair Value | Upside/Downside | Rating/Action | Evidence Quality |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|---:|---:|---|---|
| 600150.SH | 33.02 / 2026-07-22 | 75.25621288 亿股 | 2,484.960149 | 1,775.00 | 172.762156 / 2.295653 | 2027E 合并归母 cycle-normalized PE；2026/2028 与现金质量交叉 | 11.21 | 33.08 | 48.34 | **33.07；31.64—35.96** | **+0.15%** | 中性偏多（持有/等待验证）；event-driven validation | 中高：R0 PASS、算术可复算；倍数与持续期为 House 判断，目标价 Street 权重为 0 |

完整公式：

```text
Market cap = 33.02 × 75.25621288 = 2,484.960149
Base intrinsic value = 2.876705 × 11.5 = 33.0821075
Final target = 33.0821075 × 85% + 33.02 × 15% + Street × 0%
             = 33.072791375 ≈ 33.07
Published-target upside = 33.07 / 33.02 - 1 = +0.1514%
```

预期回报没有来自资产注入、军品或集团订单期权；它只来自冻结模型中的收入兑现、毛利改善与持续期。由于最终目标与现价几乎重合，当前不存在需要追价的估值缺口。

## Three-Tier Targets

| Ticker | Bull (Scenario) | Base (Method) | Bear (Floor) | Current | Bubble% |
|---|---|---|---|---:|---:|
| 600150.SH | 2027E Bull EPS 3.718618 × 13.0x = **48.342034**；需交付、价格/结构、毛利和 OCF 同时达上端 | 2027E Base EPS 2.876705 × 11.5x = **33.082108** | 2027E Bear EPS 1.245290 × 9.0x = **11.207610**；交付/毛利断裂并去评级 | 33.02 | **-0.19%** |

`Bubble% = (33.02 / 33.0821075 - 1) × 100% = -0.1877%`。这里的 Bear/Base/Bull 是完整经营情景与同一主方法的组合，不是目标价区间：压力情景下行 **-66.06%**，基础情景 **+0.19%**，乐观情景 **+46.40%**。基础公允区间另以 2027E Base EPS × 11.0—12.5x 得到 **31.643755—35.958813 元**。

Bull 采用卖方风格的上端兑现逻辑，但不使用任何券商目标价；其盈利与倍数组合显著偏乐观，因此只作情景上沿，不进入 Street 锚。

## Relative / PEG / PSG Comparison

冻结证据没有业务模式和口径均匹配的可复算同行组，因此不制造横向“相对低估”结论。下表按 PEG 从低到高排序，仅比较 600150 自身不同前瞻期；PEG/PSG 的低值会被 2026 低基数和利润率跃升机械压低，不是主估值依据。

| Ticker / Period | MCap | PE | PS | NP Growth | Revenue Growth | PEG | PSG | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 600150.SH 2026E | 2,484.96 | 14.38x | 1.400x | 120.12% | 16.79% | **0.120** | **0.083** | 低基数周期反弹，机械最便宜但不可作为决策倍数 |
| 600150.SH 2027E | 2,484.96 | 11.48x | 1.242x | 25.31% | 12.68% | **0.453** | **0.098** | 正常化主年度；仍须现金质量验证 |
| 600150.SH 2028E | 2,484.96 | 10.07x | 1.156x | 14.01% | 7.50% | **0.719** | **0.154** | 对高价订单持续期最敏感，House 显著低于 Street |

公式统一为 `PEG = current PE / parent-NP growth (%)`、`PSG = current PS / revenue growth (%)`。PB/ROE 因冻结 verified packet 未提供可复算归母权益/BPS 而标记 `not disclosed`。

## Seasonality Calibration

| Ticker | Q1 Actual | Q1 Historical% | Mechanical FY Stress | Full-Year Estimate | Calibrated PE |
|---|---:|---:|---:|---:|---:|
| 600150.SH | 2026Q1 归母 48.32 | 17.51%（2025Q1 重述 13.742 / 2025A 78.4838；单年观察） | 275.97；**仅压力测试，不采用** | 172.762156 / EPS 2.295653 | **14.38x** |

2026Q1 已占 Base 全年归母的 27.97%，反映交付和利润确认的季度偏斜；用单年历史占比外推会得到 275.97 亿元，明显高于冻结 Base，不能发布为预测。H1 预告 92—110 亿元同样不得乘二。季节校准后的估值分母仍是完整订单—交付—毛利—归属模型，而不是季度年化。

## Next-Quarter Threshold

| Ticker | Current MCap | Consensus / House PE | Next-Quarter Threshold | Risk if Miss |
|---|---:|---:|---|---|
| 600150.SH | 2,484.96 | Street 2026E 中位 14.11x；House 2026E 14.38x / 2027E 11.48x | 正式 H1 归母至少 **101**、扣非至少 **99**，对应 Q2 归母至少 **52.68**、扣非至少 **51.33**；核心业务 GM 不低于 **11.72%**；OCF 为正且存货/合同资产不异常扩张 | 低于预告下限 92/90、核心 GM 低于 10.5%，或现金与利润背离，切换 Bear / 下调倍数；不得以 H2“补回来”维持旧目标 |

2026 Base 全年归母 172.762156 亿元在 H1 中点 101 亿元后仍需 H2 实现 **71.762156 亿元**。全年 OCF/归母需至少 0.8x；Base 为 0.85x，2027E 改善至 0.95x。现金阈值不是附加故事，而是保留 11.5x 正常化倍数的必要条件。

## Method and Assumption Bridge

| Ticker | Primary Method | Secondary Check | Key Assumptions | Catalyst Needed | Invalidation Trigger |
|---|---|---|---|---|---|
| 600150.SH | 2027E 合并归母 EPS 2.876705 × 11.5x | 2026E 14x = 32.14；2028E 9x = 29.52；OCF/归母 0.85/0.95/1.00x；现价隐含利润率 | 有效交付、价格/结构、确认、Growth GM、少数股东归属按冻结 Base；军品/沪东中华/集团期权/弱目标价均为 0；中远项目不重复加总 | H1 利润高于中点、核心 GM ≥11.72%、OCF 为正、交付接近计划；之后按正式披露整体重跑 | H1 <92/90、核心 GM <10.5%、重大延期/撤单/融资或质保问题、全年 OCF/归母 <0.8x 且无回收路径 |

11.5x 的选择位于 2027E Base 的 11.0—12.5x研究区间中部，并与现价隐含 11.4784x 接近。2026E 14x 与 2028E 9x 分别给出 32.14 元和 29.52 元的期限交叉；它们说明当前价值依赖 2027 年正常化利润，而不是单季高点或无限期维持高倍数。货币资金 1,445.94 亿元不机械加回，因为冻结证据没有区分受限/经营现金，且 1,523.60 亿元合同负债反映客户预付款经济性。

## Market-Expectation Valuation Bridge

| Ticker / Year | Current Price | House Revenue | Revenue Growth | House NP/EPS | Expected Multiple | House Fair Value | Upside/Downside | Current-Implied NP/EPS | Embedded Expectation Gap | Driver |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 600150.SH 2026E | 33.02 | 1,775.00 | 16.79% | 172.762 / 2.295653 | 14.0x | 32.139 | -2.67% | 177.497 / 2.359 | +2.74% | Growth GM 约 17.16%，高于 Base 16.8%，或归属更优 |
| 600150.SH 2027E | 33.02 | 2,000.00 | 12.68% | 216.490 / 2.876705 | 11.0x | 31.644 | -4.17% | 225.905 / 3.002 | +4.35% | 综合 GM 约 17.85%，高于 Base 17.30%，且持续期不缩短 |
| 600150.SH 2028E | 33.02 | 2,150.00 | 7.50% | 246.811 / 3.279608 | 9.0x | 29.516 | -10.61% | 276.107 / 3.669 | +11.87% | 综合 GM 约 19.13%，高于 Base 17.52%，需要更久的高价订单释放 |

现价不是在支付“订单存在”本身，而是在支付利润率继续上移、现金回收改善和盈利持续期延长。若这些条件不能由正式披露验证，市场隐含盈利缺口将通过盈利下修或倍数压缩消化。

## Broker/Street Comparison

| Ticker | Broker/Source | Date | Rating | Target | 2026E Revenue | 2026E NP/EPS | Method/Multiple | Street Upside | AStock Gap | Evidence Quality |
|---|---|---:|---|---:|---:|---:|---|---:|---|---|
| 600150.SH | 华源证券原始 PDF | 2026-07-14 | 买入 | not disclosed | 1,735.01 | 181.98 / 2.42 | 报告价 13.97x；无目标价 | not disclosed | House NP -5.1%；目标价不可比 | 原始 PDF；forecast weight 1，valuation weight 0 |
| 600150.SH | 诚通证券原始 PDF | 2026-05-06 | 强烈推荐 | not disclosed | 1,782.37 | 170.90 / 2.27 | 报告价 18.1x；无目标价 | not disclosed | House NP +1.1%；目标价不可比 | 原始 PDF；forecast weight 1，valuation weight 0 |
| 600150.SH | 东吴证券原始 PDF | 2026-05-05 | 买入 | not disclosed | 1,880.07 | 200.36 / 2.66 | 报告价 15.69x；无目标价 | not disclosed | House NP -13.8%；目标价不可比 | 原始 PDF；forecast weight 1，valuation weight 0 |
| 600150.SH | 华源证券原始 PDF | 2026-05-01 | 买入 | not disclosed | 1,735.01 | 176.38 / 2.34 | 报告价 17.82x；无目标价 | not disclosed | House NP -2.1%；目标价不可比 | 原始 PDF；forecast weight 1，valuation weight 0 |
| 600150.SH | 国金证券原始 PDF | 2026-04-29 | 买入 | not disclosed | 1,924.07 | 165.50 / 2.199 | 报告价 18.72x；无目标价 | not disclosed | House NP +4.4%；目标价不可比 | 原始 PDF；forecast weight 1，valuation weight 0 |
| 600150.SH | 华泰证券第三方预览 | 2026-05-03 | 买入 | 58.96 | not disclosed | not disclosed / 2.68 | 22x PE 线索 | +78.6% | AStock target -43.9% | `third_party_preview`；**valuation weight 0** |
| 600150.SH | 国泰海通 AG-04 | not disclosed | not disclosed | not disclosed | not disclosed | not disclosed | not disclosed | not disclosed | 不可比 | `not_found` / 404；**valuation weight 0** |

Street 当前五份预测的 2026/2027/2028 归母中位数为 176.38/235.38/299.43 亿元，House 为 172.76/216.49/246.81 亿元。差异随期限扩大，说明本模型不复制卖方对高毛利持续期的假设。13 份原始 PDF 没有可用目标价，因此 Broker/Street anchor 为 `not disclosed`，最终权重严格为 0。

## Market-Implied Sentiment Anchor

| Ticker | Current Price | Intrinsic Value | Current-Implied PE/PS/PB | Trading Value Percentile | Sentiment Regime | Market Anchor | Broker Anchor | Final Weights | Final Target | Premium/Discount | Action Logic |
|---|---:|---:|---|---|---|---:|---|---|---:|---:|---|
| 600150.SH | 33.02 | 33.0821 | 2026E 14.38x/1.400x；2027E 11.48x/1.242x；PB not disclosed | not disclosed；当日成交额 36.04 亿元、涨 0.18% | 13/13 原始报告正向但仅 4 家券商重复覆盖；事件验证期 | 33.02 | not disclosed / 0 weight | Fundamental 85% / Market 15% / Broker 0% | **33.0728** | 现价对内在价值 -0.19% | **fundamentally near fair / event-driven validation**；持有等待验证，不因单一内在价值差机械卖出 |

市场锚只取可观察现价，不额外资本化“军品、沪东中华、集团订单”叙事。新增市场结构包显示，前复权口径下1年收益为-3.84%、最大收盘回撤-22.89%，截至日33.02元低于MA10至MA250，成交换手1.44%；两融日度回落、沪股通和基金季度存量上升的频率并不一致。因此这些数据只用于执行风险和市场状态校验，不追加基本面估值权重，市场锚仍为15%。若利润、毛利与现金三项同步超预期，应重跑基本面而不是上调市场权重；若情绪溢价破裂，Bear 显示非对称下行。见 `PR-02/PR-03`。

## Growth Earnings Dependency

| Dependency | Frozen Input | Valuation Use | Credit / Block |
|---|---|---|---|
| Base / Growth split | 2025A Growth revenue 1,312.7873，Base revenue 206.9926 | 驱动 2026—2028 合并 revenue、margin、net profit | 仅 consolidated earnings credit；不拆独立 EPS |
| Unit / proxy | 有效交付 DWT；2025 revenue-intensity proxy 95.981524 亿元/百万 DWT | 与价格/结构指数、确认系数共同生成 Growth revenue | 不是船型 ASP，不可外推逐船价值 |
| Recognition / margin | recognized revenue ratio；Growth GM Bear/Base/Bull 14.0%/16.8%/18.5%（2026） | 直接进入毛利、税、少数股东与 EPS 桥 | 必须由正式收入、合同资产和毛利验证 |
| Opex / cash | 2026 Base operating expenses 128；OCF/NP 0.85x | 约束 multiple 是否保留 | 全年 OCF/NP <0.8x 触发去评级 |
| Current-implied growth | 14x 2026 需归母 177.50、Growth GM 约17.16%；11x 2027 需归母225.91 | 衡量当前已定价的毛利/归属缺口 | 不把市场热度替代 EPS 证据 |
| Prohibited option credit | 军品、沪东中华、集团未分配订单、弱目标价 | 不进入 revenue、net profit、multiple 或 target | 全部 0 |
| COSCO project | 约 500 亿元/87 艘、含意向成分、属于 600150 子公司聚合披露 | 只作去重订单质量与客户证据 | 增量 revenue/EPS/target credit = 0 |

增长模型当前为 `CONDITIONAL`，但已 `Model Reproducibility: PASS`。R1 估值不改其 Bear/Base/Bull；只在合并层面选择正常化年度和倍数。任何高增长倍数、PEG/PSG 或 SOTP 信用均不得脱离 `analysis/growth_earnings_model.md`、`analysis/segment_forecast_bridge.md`、`analysis/implied_growth_sensitivity.md` 与 `data/growth_driver_model.json`。

## Full-Chain Classification Dependency

R0 已 `PASS`，机器分类只有一个可估值母体：`N15 / 600150.SH`。江南造船、大连造船、外高桥造船、广船国际、黄埔文冲、武昌造船、北海造船等经营实体均是 **consolidated components**，不是独立 investable ticker，也不允许把子公司收入或利润再加到 600150 合并数。

| Full-chain status | Valuation consequence |
|---|---|
| 600150.SH = sole valuation parent / core_valuation node | 只对合并归母 EPS 使用 cycle-normalized PE |
| 子公司 = consolidated components | 不做子公司 standalone multiple，不做船厂 SOTP |
| 船型 ASP、船厂 utilization、逐厂 revenue/net profit 未披露 | segment/SOTP 被阻断；只允许合并 sensitivity |
| 在手订单与中远项目已在聚合口径 | 只支持可见性和去重；不直接增加 revenue/EPS |
| 军品、沪东中华、集团期权缺少上市公司盈利桥 | 所有情景 0 信用；只有正式公告和可复算盈利桥才能解除 |

因此，产业链分类对估值的作用是约束边界，而不是提供额外溢价。完整分部处理见 `analysis/segment_valuation_model.md`；估值算术和权重审计见 `analysis/valuation_audit.md`。

## Valuation Recovery Record

| Field | Result |
|---|---|
| valuation_recovery_status | 完成：周期正常化 PE + 市场隐含预期 + 现金质量交叉 |
| direct_broker_anchor | not disclosed；weight 0 |
| public_consensus_anchor | 只作盈利预测对照；目标价 weight 0 |
| peer_set / peer_metrics | 冻结证据未提供匹配同行；not disclosed，不宣称相对折价 |
| market_implied_metric | 2027E House Base PE 11.4784x |
| alternative_method | 2026E/2028E PE 与 OCF conversion 交叉 |
| normalized_denominator | 2027E 合并归母 EPS 2.876705 |
| scenario_range | 11.207610—48.342034；基础公允区间 31.643755—35.958813 |
| confidence | 算术中高；倍数/持续期中等 |
| upgrade_trigger | H1 高于中点、核心 GM ≥11.72%、OCF 正、交付按计划 |
| downgrade_trigger | H1 <92/90、GM <10.5%、交付/撤单/融资问题或 OCF/NP <0.8x |

**证据边界：** 本文件仅使用本案例 R0 PASS 结论、House/variant、verified market/financial、Broker/Street packet 和冻结 growth 模型；未新增外部来源。
