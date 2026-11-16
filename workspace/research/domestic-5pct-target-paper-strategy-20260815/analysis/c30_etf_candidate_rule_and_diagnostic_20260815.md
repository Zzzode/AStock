# C30：五 ETF 静态候选规则与市场价代理诊断

- 工件 ID：`D5PT-C30-ETF-LAB-v1`
- 截止日：`2026-08-14`
- 角色：`quant-risk-modeler`
- 风险模型状态：`VETO`
- 当前处置：`research_only`、`portfolio_q=0`、`external_investment_action_authorized=false`。
- 结论：C30 形成了明确、低频、五只 ETF 的纸面研究候选；但公开日线只能支持受限市场价代理算术，不能证明投资者总回报、成交、个人可操作性或稳定 5%，因此不准入、更不授权任何实际投资动作。

## 1. 预先冻结的候选与动作卡

本计算前冻结的协议：[c30_etf_candidate_protocol_20260815.md](c30_etf_candidate_protocol_20260815.md)。其哈希为 `8c408cdde956ac148a869c2a69d84182e2df93f9a069d4957c57fa8e1d69f154`；候选由经济暴露预算确定，**未按本次或既有历史得分选出**。

| 产品 | P01 中的角色 | 固定目标 |
|---|---|---:|
| `510300` | broad China equity; one half of equity sleeve | 20% |
| `510880` | dividend-style China equity; other half of equity sleeve | 20% |
| `511010` | five-year government-bond exposure | 40% |
| `518880` | domestic gold-spot-related exposure | 10% |
| `511990` | money-market-tool exposure; not account cash | 10% |

经济意图是 40% 国内权益、40% 五年期国债相关暴露、10% 国内黄金相关暴露和 10% 货币市场工具暴露；它不是相关性、流动性、避险、分红、现金流或 5% 结果的承诺。`511990` 是 ETF 暴露，不是账户现金。

**冻结动作：** 在每年六月和十二月最后一个共同交易日收盘后记录已有漂移权重；最早于下一共同交易日的开盘价代理恢复上述固定权重。计算没有使用市场信号、择时、排名或事后换产品。该 C30 静态诊断**不替代、不修改** R01 的月度动态纸面动作卡。

## 2. 严格的次交易日代理时序与成本边界

若决策日为 `D`，有效日为 `E`，现有持仓先承受 `D` 收盘至 `E` 开盘的市场价代理变化；仅在 `E` 开盘时计算目标交易与成本；新目标才承受 `E` 开盘至收盘变化。首次建仓同样在共同面板第一天收盘之后的下一共同开盘。每条事件均通过严格的 `D < E` 断言，禁止同日收盘成交和同一根 K 线前视。

基准成本是每次单边换手 `20 bp` 的机械算术载荷（首次 100% 入场也计入），并非已观察到的佣金、税费、点差、冲击、基金费用、结算或成交。原始输入为回溯抓取的上交所日线，来源清单与哈希见 `workspace/research/domestic-personal-securities-futures-strategy-20260814/sources/c7-static-etf-price-observation-20260815/manifest.json`；共同面板为 2013-07-29 至 2026-08-14 的 3173 个交易日。

**降级说明：** 这些输入没有点时点可得性、复权/总回报、分配和基金事件账本，也没有买卖价、深度、IOPV 历史、停复牌、涨跌停、费用税费、成交、结算、账户或容量资料。因此下列数值是“未确认调整口径的市场价代理”，不是总回报或可执行净回报。

## 3. 基准市场价代理结果（不可当作总回报）

| 指标 | 受限代理值 |
|---|---:|
| 首次有效日 / 终止日 | 2013-07-30 / 2026-08-14 |
| 期末单位值 | 1.9010 |
| 年化市场价代理变化（含示例成本） | 5.05% |
| 年化日度代理波动 | 8.28% |
| 最大回撤代理 | -21.40%（峰值 2015-06-12，谷值 2016-01-28） |
| 最差单交易日代理变化 | -4.28%（2015-06-25 至 2015-06-26） |
| 最差 20 交易日代理变化 | -16.03%（2015-06-09 至 2015-07-08） |
| 调仓次数 / 单边换手（含首次） | 26 / 1.8054 |
| 累计示例成本分数算术和 | 0.36% |
| 受限 5% 价格代理筛查 | `REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN` |

### 完整自然年

| 年份 | 首个 / 最后代理点 | 完整 | 市场价代理变化（含示例成本） | ≥5%（仅受限筛查） |
|---:|---|:---:|---:|:---:|
| 2013 | 2013-07-30 | 2013-12-31 | 否 | 0.02% | — |
| 2014 | 2014-01-02 | 2014-12-31 | 是 | 24.98% | 是 |
| 2015 | 2015-01-05 | 2015-12-31 | 是 | 5.86% | 是 |
| 2016 | 2016-01-04 | 2016-12-30 | 是 | -0.72% | 否 |
| 2017 | 2017-01-03 | 2017-12-29 | 是 | 7.15% | 是 |
| 2018 | 2018-01-02 | 2018-12-28 | 是 | -5.71% | 否 |
| 2019 | 2019-01-02 | 2019-12-31 | 是 | 12.16% | 是 |
| 2020 | 2020-01-02 | 2020-12-31 | 是 | 6.87% | 是 |
| 2021 | 2021-01-04 | 2021-12-31 | 是 | 1.08% | 否 |
| 2022 | 2022-01-04 | 2022-12-30 | 是 | -2.84% | 否 |
| 2023 | 2023-01-03 | 2023-12-29 | 是 | 1.11% | 否 |
| 2024 | 2024-01-02 | 2024-12-31 | 是 | 10.95% | 是 |
| 2025 | 2025-01-02 | 2025-12-31 | 是 | 7.47% | 是 |
| 2026 | 2026-01-05 | 2026-08-14 | 否 | 0.34% | — |

### 月末滚动五年

月末滚动五年端点共 98 个，其中 19 个不低于 5%、79 个低于 5%，年化市场价代理区间为 0.36% 至 7.85%。

“≥5%”只描述这个代理数值与研究线的关系，绝不表示稳定、保底、未来预测或个人净收益。若任一完整年度或滚动五年窗口低于 5%，协议将其记为**有限市场价代理筛查的拒绝**；即便全数高于 5%，也不能绕过总回报和执行缺口。

## 4. 预先声明的鲁棒性 / 突变族（不选优）

以下全部是在看结果前冻结的离散变体。`base` 始终是候选，其他结果仅显示对权重、日历和成本算术的依赖；不得从中挑选年化最高者、回撤最低者或“幸存者”。

| 变体 | 年化市场价代理变化 | 最大回撤 | 完整年度 <5% | 滚动五年 <5% | 有限筛查 |
|---|---:|---:|---:|---:|---|
| base | 5.05% | -21.40% | 5/12 | 79/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |
| low_equity_30 | 4.67% | -16.07% | 5/12 | 86/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |
| high_equity_50 | 5.39% | -26.39% | 5/12 | 77/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |
| annual_cadence | 4.88% | -22.29% | 6/12 | 84/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |
| quarterly_cadence | 5.07% | -20.43% | 5/12 | 82/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |
| zero_cost | 5.08% | -21.38% | 5/12 | 78/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |
| cost_stress_50bp | 5.01% | -21.42% | 5/12 | 79/98 | REJECTED_BY_LIMITED_PRICE_PROXY_SCREEN |

该族没有估计 alpha、相关性、VaR、容量或未来回报；它也不是干净样本外研究，因为协议是在已有公开观察之后形成。

## 5. 场景与无法界定的损失

1. **历史最大回撤代理：** 依据基准机械路径为 -21.40%。这不是投资者回撤，也不是未来损失上限。
2. **同步 10% 风险腿跳空的纯算术敏感性：** 若 510300、510880、511010 与 518880 都在任何再平衡前同步下跌 10%，而 511990 不变，按目标权重的单期算术损失为 -9.00%。价格限制、停牌、流动性、关联性、点差和退出能力均未被假设为已知。
3. **权重突变方向性检查：** `low_equity_30` 与 `high_equity_50` 的最大回撤代理分别为 -16.07% 与 -26.39%；这些不证明更低或更高权益具有稳定风险优势。
4. **跌停、停牌与未成交压力：** `UNAVAILABLE`。留存日线没有产品状态、涨跌停、订单簿、深度或实际成交记录，不能计算无法调仓或无法退出时的损失扩大；不得把日收盘或次日开盘代理当作可成交事实。

缺失真实组合规模、损失预算、流动性需求、仓位上限、可成交价格与未成交账本，故无法把这些百分比转换为可界定的个人损失或容量结论。

## 6. 纸面操作的 `no_action` 闸门

历史代理没有测试以下分支。未来任何纸面动作必须先获得当前正式文件、状态、账户/适当性、可用资金和份额、费用税费、结算、带时间戳的报价与深度，以及适用的 IOPV。买入只在 `ask ≤ IOPV × 1.003`、卖出只在 `bid ≥ IOPV × 0.997` 时才可提交限价纸面订单；100 份最小申报单位和 0.001 元最小变动只是需要再次核验的类别参考。

- Missing current product, legal-document, temporary-announcement, market-status, account, fee, tax, settlement, quote, depth, IOPV where applicable, or reconciliation evidence.
- Halt, delisting, price limit, material product change, account or settlement failure, unavailable funds/shares, or either equity leg not checked.
- Lot/tick failure, partial fill, rejection, no fill, or inability to reconcile a prior paper ledger.

任何失败都保持既有纸面持仓并记录 `no_action`；不得自动替换 ETF、假设成交、用收盘价补写成交、预支未结算款或把类别性 T+0/T+1 提示当成具体账户事实。

## 7. 量化风险闸门

**Role:** quant-risk-modeler  
**Risk Model Status:** VETO  
**Conclusion:** The fixed five-ETF price proxy may describe a transparent historical arithmetic path, but missing total-return, liquidity, execution, portfolio-loss-budget and forward-paper inputs prevent a bounded-loss or personally operable-strategy conclusion.  
**Confidence:** 94 / 100  
**Degradation:** Retrospective official market-price input only; actual total-return and execution data are absent.

**Exposure Findings:**

- 单一代码 `511010` 的目标集中度为 40%；40% 权益中的两只产品均为中国股票风险来源，不可视为已证明的低相关分散。
- 债券、黄金与货币市场 ETF 各有利率、估值、信用、折溢价、流动性和产品事件风险；本文件不把它们称为无风险或自动避险。
- 公开日价代理没有任何盘口、容量或实际交易记录，因此不能作为交易许可。

**Required Controls:**

- Keep status at research-only / portfolio_q=0; do not use the proxy to authorize an external action.
- Obtain a rights-cleared point-in-time total-return and fund-event ledger, with an execution/cost/tax/settlement ledger, before testing the 5 percent hurdle formally.
- Before any future paper action, record current product status, account/appropriateness, bid/ask/depth, IOPV where applicable, lots, fees/taxes, settlement, and no-fill outcomes; fail closed to no_action.
- Define the actual portfolio value, loss budget, concentration limits, liquidity needs, and a six-month forward paper ledger before any review of operability.

**最终边界：** 5% 不是保证；本工件不授权实际投资、下单、开户、申购、赎回或任何外部行动。
