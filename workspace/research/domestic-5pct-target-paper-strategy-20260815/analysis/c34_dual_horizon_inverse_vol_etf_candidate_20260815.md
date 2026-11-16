# C34：双期限评分与逆波动 ETF 候选 — 价格代理诊断

- 工件 ID：`D5PT-C34-DUAL-HORIZON-INVERSE-VOL-v1`
- 截止日：`2026-08-14`
- 角色：`quant-risk-modeler`
- 风险模型状态：`VETO`
- 当前处置：`research_only`、`portfolio_q=0`、不发送外部订单。
- 结论：C34 已把双期限评分、严格回退比较、逆波动权重和次交易日时序写成可复算候选；但它的历史输入仅为回溯日价代理，公式形成于既有探索性观察之后，且严格滚动五年筛查 出现失败，不能作为稳定 5% 或实际行动依据。

## 1. 冻结前协议与精确动作卡

本次计算之前已经冻结协议：[c34_dual_horizon_inverse_vol_etf_protocol_20260815.md](c34_dual_horizon_inverse_vol_etf_protocol_20260815.md)，JSON 哈希为 `9d853055ef102e148fd5d265bbaadca56642f7c8de0da985ae00a315a8c25ac5`。它是与 C30 静态诊断和 R01 月度纸面规则相互独立的候选，绝不改写两者。

**完整性边界：** C34 公式是在先前公开价格的探索性观察之后才被形式化。上述“计算前冻结”只表示它先于本次正式复算被记录，状态为 `pre_formal_recompute_not_true_preregistration`，并非在底层观察之前的干净预注册。2020-01-01 至 2025-12-31 的时间顺序留出段仅为鲁棒性切片，**不是**干净、未见的样本外验证；它不能把任何正面代理数值升级为独立证据、收益承诺或外部行动依据。

| 袖套 | 代码 | 目标形成方式 |
|---|---|---|
| 权益 | `510300`、`510880` | 权益袖套获选后内部各占其袖套 50% |
| 国债 | `511010` | 获选后按逆波动权重进入 |
| 黄金 | `518880` | 获选后按逆波动权重进入 |
| 回退 | `511990` | 没有风险袖套获选或预热期时为 100% |

每月最后一个共同收盘日 `D` 后，对权益、国债、黄金和回退分别计算 126 与 252 个共同观察值的市场价变化，取均值为分数。风险袖套仅在分数**严格大于**回退分数时获选；相等即不获选。获选袖套按最近 60 个共同单期市场价变化的样本波动率倒数分配；权益份额再固定均分给两只股票 ETF。无任何获选袖套时，目标为 100% `511990`。

没有杠杆、空头、期货、期权、借入、相似 ETF 替换、主观覆盖、横截面排名或事后改参。预热期也固定为 100% 回退，直到 252 期分数与波动率输入完整。

## 2. 时序、成本与来源边界

决策只使用 `D` 收盘前的信息；最早代理变更在下一共同交易日 `E` 的开盘价。旧持有先承受 `D` 收盘至 `E` 开盘的变化，`E` 开盘才发生目标和说明性成本算术，新目标随后承受 `E` 开盘至收盘的变化。程序逐笔断言 `D < E`，禁止同日收盘执行与同一 K 线前视。

每次代理变化按单边换手扣 `20 bp`，首次回退入场亦包含。它只是说明性算术，不是手续费、税费、点差、冲击、基金费用、结算或成交。上交所输入被严格哈希核验，但为回溯获取且调整口径未说明；它**不是**总回报、净值回报、实际订单或个人可操作性证明。

| 代码 | 原始行数 | 首日 | 末日 | SHA-256 |
|---|---:|---|---|---|
| `510300` | 3456 | 2012-05-28 | 2026-08-14 | `9838250fb4fdaab55d8a0b6102ad8c9cf3d42c77ed1323b413b53ff8e2527a3b` |
| `510880` | 4757 | 2007-01-18 | 2026-08-14 | `63e71acfc5cf6d87e4f5ad5792d521c238927ff58e967767e32408924bae0859` |
| `511010` | 3255 | 2013-03-25 | 2026-08-14 | `a739e95a8cf5a526db283fa44173e672c05be429514e7a06d1e5923d799bbd81` |
| `518880` | 3173 | 2013-07-29 | 2026-08-14 | `05be8fb74d456c0975ac72804fa314db92273b568bee932bebf5670393733633` |
| `511990` | 3290 | 2013-01-28 | 2026-08-14 | `23a6e129d8f8449aaf778906ba35271a1d7edcb92c37995b03d219fd951d4a05` |

共同日价面板为 2013-07-29 至 2026-08-14，共 3173 个日期。

## 3. 基准候选：开发、留出与全样本上下文

开发窗口固定为 2014-12-31 至 2019-12-31；留出窗口固定为 2020-01-01 至 2025-12-31。模型没有在开发结果后选择某一突变；留出结果也不是交易许可。

| 窗口 | 年化市场价代理变化 | 完整年度 <5% | 滚动五年 <5% | 代理基线 → 末端 | 有限筛查 |
|---|---:|---:|---:|---|---|
| Development | 5.65% | 3/5 | 0/1 | 2014-12-31 → 2019-12-31 | `REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN` |
| Holdout | 4.69% | 4/6 | 10/12 | 2019-12-31 → 2025-12-31 | `REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN` |
| Full sample | 5.55% | 7/12 | 43/98 | 2013-07-30 → 2026-08-14 | `REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN` |

**严格滚动五年 5% 代理筛查失败：** 43/98 个全样本端点低于 5%。

全样本期末单位值为 2.0197，年化市场价代理变化为 5.55%，最大回撤代理为 -8.64%（2026-01-29 至 2026-03-23）。最差单期代理变化为 -4.94%（2026-01-30 至 2026-02-02），最差 20 期代理变化为 -6.43%（2026-03-03 至 2026-03-31）。共 158 个信号/入场记录，累计单边换手 17.4732，说明性成本分数算术和为 3.49%。

全样本月末滚动五年端点 98 个，其中 43 个低于 5%，区间为 3.88% 至 7.52%。

## 4. 全样本完整自然年

| 年份 | 首日 | 末日 | 完整 | 市场价代理变化 | ≥5%（仅有限筛查） |
|---:|---|---|:---:|---:|:---:|
| 2013 | 2013-07-30 | 2013-12-31 | 否 | 0.04% | — |
| 2014 | 2014-01-02 | 2014-12-31 | 是 | 10.80% | 是 |
| 2015 | 2015-01-05 | 2015-12-31 | 是 | 6.15% | 是 |
| 2016 | 2016-01-04 | 2016-12-30 | 是 | 1.33% | 否 |
| 2017 | 2017-01-03 | 2017-12-29 | 是 | 12.97% | 是 |
| 2018 | 2018-01-02 | 2018-12-28 | 是 | 3.18% | 否 |
| 2019 | 2019-01-02 | 2019-12-31 | 是 | 4.99% | 否 |
| 2020 | 2020-01-02 | 2020-12-31 | 是 | 5.30% | 是 |
| 2021 | 2021-01-04 | 2021-12-31 | 是 | 4.72% | 否 |
| 2022 | 2022-01-04 | 2022-12-30 | 是 | 2.87% | 否 |
| 2023 | 2023-01-03 | 2023-12-29 | 是 | 4.40% | 否 |
| 2024 | 2024-01-02 | 2024-12-31 | 是 | 6.10% | 是 |
| 2025 | 2025-01-02 | 2025-12-31 | 是 | 4.75% | 否 |
| 2026 | 2026-01-05 | 2026-08-14 | 否 | 4.69% | — |

以上年度和滚动结果仅是未确认调整口径的价格代理。5% 是研究阈值，不是保证、年度下限、预测或适当性结论。

## 5. 预先声明的突变族（无选优）

下表完整显示基准、126-only、252-only、60×80% 的 48 期波动和 60×120% 的 72 期波动变体。每格的“年/滚”均为低于 5% 的计数，不允许按较高年化或较低回撤挑选任一变体。

| 变体 | 开发（年化；年/滚失败） | 留出（年化；年/滚失败） | 全样本（年化；年/滚失败） | 最大回撤代理 |
|---|---|---|---|---:|
| base | 5.65%; 年 3/5; 滚 0/1 | 4.69%; 年 4/6; 滚 10/12 | 5.55%; 年 7/12; 滚 43/98 | -8.64% |
| score_126_only | 6.79%; 年 1/5; 滚 0/1 | 3.65%; 年 3/6; 滚 12/12 | 5.51%; 年 4/12; 滚 60/98 | -9.45% |
| score_252_only | 3.75%; 年 3/5; 滚 1/1 | 4.79%; 年 3/6; 滚 10/12 | 4.73%; 年 6/12; 滚 88/98 | -11.47% |
| vol_48 | 5.61%; 年 3/5; 滚 0/1 | 4.60%; 年 5/6; 滚 11/12 | 5.53%; 年 8/12; 滚 45/98 | -9.73% |
| vol_72 | 5.63%; 年 2/5; 滚 0/1 | 4.45%; 年 5/6; 滚 11/12 | 5.42%; 年 7/12; 滚 47/98 | -9.15% |

该敏感度族不估计 alpha、相关性、VaR、容量或未来结果，也不是独立样本外证明。

## 6. 场景、操作闸门与未界定风险

1. **历史最大回撤代理：** -8.64%，不是投资者回撤或未来损失上限。
2. **全部活跃风险袖套下跌 10% 的算术压力：** 在下次调仓前的单期影响范围为 0% 至 -10%，取决于当期冻结信号是否仅在回退或配置了风险袖套；它不是预测或损失边界。
3. **跌停、停牌与未成交：** `UNAVAILABLE`。日线没有状态、价格限制、订单簿、深度或成交记录，不能量化无法调仓或退出时的影响。

未来纸面记录必须保留产品文件和公告、状态、账户/适当性、可用份额和资金、费率税费、结算、带时间戳报价与深度，以及适用的 IOPV。买入只在 `ask ≤ IOPV × 1.003`，卖出只在 `bid ≥ IOPV × 0.997` 时进入限价纸面流程。下列任一情形为 `no_action`，不得假设成交或替换标的：

- Missing current product, legal-document, temporary-announcement, market-status, account, fee, tax, settlement, quote, depth, IOPV where applicable, or reconciliation evidence.
- Halt, delisting, price limit, material product change, account or settlement failure, unavailable shares/funds, invalid price/score/volatility, or either equity leg not checked.
- Lot/tick failure, partial fill, rejection, no fill, or inability to reconcile a prior paper ledger.

## 7. 量化风险闸门

**Role:** quant-risk-modeler  
**Risk Model Status:** VETO  
**Conclusion:** The dynamic proxy has explicit signals, next-session timing, and a frozen sensitivity family, but missing total-return, liquidity, execution, account, risk-budget and forward-paper inputs prevent a bounded-loss or personally operable-strategy conclusion.  
**Confidence:** 95 / 100  
**Degradation:** Retrospective official market-price input only; actual total-return and execution data are absent.

**Exposure Findings:**

- 任一动态时点可能把目标集中到国债或黄金单一袖套；规则没有相关性、容量或集中度安全证明。
- 权益袖套中的两个 ETF 同属国内股票风险，50/50 并不证明低相关或危机保护。
- `511990` 是货币市场工具 ETF 暴露，不等同账户现金或损失消除机制。

**Required Controls:**

- Keep research_only and portfolio_q=0; do not use the proxy to send or support an external order.
- Acquire a rights-cleared point-in-time total-return, distribution, and fund-event ledger plus dated execution, cost, tax, settlement, status, and no-fill records.
- For any future paper record, fail closed to no_action unless current product, account, status, quote/depth, IOPV where applicable, lot, fee/tax, and settlement evidence are complete.
- Define user loss budget, concentration limits, liquidity needs, and a continuous forward-paper ledger before considering any operability review.

**最终边界：** 本工件不承诺 5%，不授权账户动作、外部订单、申购、赎回或任何实际投资行动。
