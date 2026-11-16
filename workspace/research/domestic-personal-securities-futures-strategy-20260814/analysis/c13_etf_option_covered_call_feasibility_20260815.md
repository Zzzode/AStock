# C13 沪深300 ETF 备兑认购期权：可行性与固定规则 — 2026-08-15

- 工件：`DPSFS-C13-ETF-OPTION-CC-v1`；状态：**`RESEARCH_CANDIDATE_NOT_ACTION_READY`**；`portfolio_q=0`。
- 标的：`510300` Huatai-PineBridge CSI 300 ETF，对应上交所沪深300 ETF 认购期权。
- 这是一条备兑认购期权的研究路径，不是现在的交易指令，也不是稳定 5% 回报的证明。

## 经一手规则确认的机械约束

- 上市通知列明标准合约单位为 `公司行动调整前为 10,000 份 ETF`，到期月份为 `当月、下月及随后两个季月`，采用 `欧式，到期日行权` 与 `实物交割，除非交易所规则另有规定`。
- 除息等公司行动会调整未到期合约的代码、行权价和合约单位；被冻结的 2026-01-16 公告说明，备兑持仓也可能需要补足调整后的交割备用证券，否则有强行平仓风险。
- 期权权限、适当性、账户路由、交易状态和经纪商的备兑流程均是逐账户条件，不能从公开规则推定。

## 冻结的研究操作逻辑

1. 操作者独立确认当前适当性、权限等级、账户路由和经纪商备兑开仓功能；公开规则不能替代账户确认。
2. 当期交易所合约记录须证明精确合约、调整后单位、行权价、到期日、交易状态与交割条款。
3. 经纪商能够锁定精确的可交割 ETF 数量作为备兑备用证券；不允许裸卖或以保证金替代备兑。
4. 留存带时间戳的买卖报价、深度、交易状态、经纪商费税表和结算日历；任一字段缺失即 NO_ACTION。

- 系列选择：上一标准到期日完成结算后，检查当期交易所合约清单；在未调整的下月认购中，选择行权价不低于前一日 ETF 收盘价的最低挂牌行权价。没有合格存续合约，或公司行动改变交割物时，记录 NO_ACTION，不得改用其他规则。
- 数量：经纪商锁定的每一份当前精确合约单位的可交割 ETF，仅对应一张备兑认购；不得超过经纪商确认的备兑数量。
- 委托：仅在备兑锁定和报价质量门槛通过后使用限价委托。部分成交或未成交均保留为未完成状态，不得在研究中视为完成卖出。
- 到期与调整：在交易所最后交易／到期日前，以及每次标的分配或合约调整公告后，逐项核对合约代码、单位、行权价、交割物锁定、交收日和经纪商持仓状态。核对失败即停止该候选，不得虚构换月。

## 严格 5% 检验为何不能开展

当前结论为 **`NOT_FEASIBLE_FOR_RETURN_CLAIM`**。要计算每个完整年度和滚动五年的净结果，至少需要：

- `point_in_time_actual_contract_master_with_adjustments_and_lifecycle`
- `historical_option_bid_ask_depth_trades_and_official_settlement_by_contract`
- `underlying_total_return_distribution_and_trading_status_history`
- `dated_exchange_and_broker_fee_tax_margin_and_covered_reservation_rules`
- `execution_state_and_partial_fill_evidence`
- `account_permission_and_settlement_feasibility_evidence`
- `pre_frozen_replay_protocol_and_independent_audit`

上交所冻结材料解释了期权数据应有的合约、调整、状态、报价和结算字段，却没有在本研究中形成完整、时点正确且可审计的实际合约与成交包。因此不能把卖出期权收取的权利金误读成每年稳定的净收益，也不能生成任何回测数字或个人操作。

## 风险与结论

备兑认购仍承担 ETF 下跌；权利金会限制上行但不能消除下跌、流动性、调整、交割、账户和成交风险。C13 当前只保留为规则完整但数据与个人执行尚未闭合的研究候选；在严格 5% 目标下不具备可用性。来源与哈希见 [C13 source manifest](../sources/c13-sse-etf-option-rules-20260815/manifest.md)，机器副本见 [c13_etf_option_covered_call_feasibility_20260815.json](c13_etf_option_covered_call_feasibility_20260815.json)。
