# 正式回放协议要求 — DPSFS-RP0-v10

- 状态：**仅为要求；未冻结、不可运行。**
- 机器可读权威：`formal_replay_protocol_requirements_20260814.json`，schema `formal_replay_protocol_requirements.v10`。
- 当前决定：无正式结果、配置、持仓或行动，`q=0`。

## 历史门槛与端点证据

严格历史研究门槛是每个完整合资格的滚动五历年端点均达到年化净 TWRR 5%。端点年化必须用 `end_unit_nav / start_unit_nav`（或等价链式单位 NAV）计算；有外部现金流时禁止使用总 NAV 比率。`endpoint_calculation_sha256` 必覆盖单位 NAV、外部现金流处理、日期和公式。

每个候选端点有 `master_calendar_id`/`master_calendar_sha256`、`candidate_generation_rule_id`/`candidate_generation_rule_sha256`、冻结每日覆盖规则 ID/SHA、`calendar_anchor_at=a`、`selected_start_valuation_at=s`、`endpoint_end_valuation_at=e`、`window_start=s`、`window_end=e`、`elapsed_calendar_days`、`required_window_calendar_days`、起止日账本 ID、端点覆盖行数/已覆盖数/集合 hash/状态、`expected_partition`、名册与输入 SHA；结果行必须逐字节携带这些覆盖证据。总体审计还须复核 evaluation-warmup 覆盖数/集合 hash/状态。预期数 = 实际数 = 唯一名册数；预期/实际分区及状态计数均须复核到实际数，`count_residual=0` 且 `population_reconciliation_status=PASS`。零数、短缺、漏行、重复、缺会话、FAIL、INCOMPLETE、INVALID 均不能通过。PRIMARY_HOLDOUT 还要求实际数 = 冻结预期数 ≥126 且全部 PASS；CROSSING 绝不代替样本外。

`endpoint_status` 为冻结的 `endpoint_status_rule_id`/`endpoint_status_rule_sha256`（`DPSFS-ENDPOINT-STATUS-v1`）及 `endpoint_calculation_population_policy_sha256` 下的机械结果：先判 `INVALID`，再判 `INCOMPLETE`，其余 `annualized_net_twrr >= 0.05` 为 `PASS`、`< 0.05` 为 `FAIL`；仅允许 `UNIT_NAV_RATIO` 或 `CHAIN_LINKED_UNIT_NAV`，后者必须以 `endpoint_unit_nav_chain_member`、`twrr_unit_nav_chain_member_count` 和链 hash 完整复算。`no-failed-settlement-in-endpoint-state` 与 `failed-settlement-contract-pass` 是同一冻结状态规则的硬谓词：FAILED 结算、配对转移或未结算合同失败一律使端点 INVALID，绝不能 PASS。冻结的 `candidate_endpoint_roster_id`/SHA、生成规则、a/s/e 和 `expected_partition` 必逐字节传递至结果行，且 `endpoint_partition=expected_partition`。

这只是历史路径约束，不是保证、预测、概率或个人适当性结论。重叠端点不是独立样本；非重叠和制度/压力汇总只能辅助披露，不能替代全端点门槛。

## 冻结运行、DD v8 与行级绑定

正式运行必须使用 `DPSFS-DD-v8`、DPSFS-DAC-v12、DPSFS-RP0-v10 和唯一已签署的 `replay_run_freeze_record`。该实体以 `replay_run_id` + `replay_run_freeze_record_sha256` 绑定规则书、U0、输入、代码/环境/命令、锁箱和全部政策。其 SHA 是对**排除 hash 字段本身**的规范冻结序列化/独立冻结工件的哈希，不允许自指计算。

记录 schema 固定为 `replay_run_freeze_record.v2`：`data_contract_freeze_record_sha256=canonical_freeze_record_sha256`、`data_contract_sha256=contract_sha256`，且 `protocol_id`/版本/SHA 分别等于 `formal_replay_protocol_id`/版本/SHA；`freeze_timestamp=effective_from`，`supersedes_if_any` 仅为前一已签署运行 ID 或明确 `null`。冻结字段为唯一集合，重复名称、别名或同名异值均拒绝签署。

父记录还必须冻结 `fx_conversion_policy_id`/SHA、`master_calendar_daily_coverage_rule_id`/SHA 及 `unitization_method_id`/版本/SHA。`frozen_fx_quote_conversion`、`master_calendar_daily_valuation_coverage` 与 `frozen_unitization_method_definition` 的运行域行均与该父记录逐字节绑定。

每个运行域行的绑定字段 `replay_run_freeze_record_sha256` 必逐字节等于父冻结记录；行自身内容哈希保持独立。该规则覆盖冻结 FX、每日日历覆盖、冻结单位化方法、端点名册/总体/结果、日账本、单位化/仓位/批次/现金流/残差、订单/执行转换/结算转换/成交/事件/费用组件/可行性保留、`cash_margin_collateral_transfer_pair`、锁箱起始状态及其规范化成员、前瞻覆盖审计。缺绑定、跨运行 join、不同绑定下重复键或事后绑定均为 INVALID。

## 单位化、起始状态和可行性

外部现金流在预流估值后按单位 NAV 申赎单位；`portfolio_unitization_ledger` 以冻结的 `unitization_method_id`/版本/SHA、`prior_unitization_ledger_id`、`valuation_at`、`ledger_currency`、`opening_units`、`units_issued`、`units_redeemed`、`closing_units`、`external_cashflow_amount`、`external_flow_pricing_unit_nav`、`nav_before_external_cashflow`、`nav_after_external_cashflow`、`unit_nav` 和 `unitization_calculation_input_set_sha256` 记录。唯一最先的 OPENING 行才可无前序且 opening_units=0；每个非 OPENING 行必须连接按 `valuation_at` 再 `unitization_ledger_id` 的即时前序，前序时点严格更早，且 opening_units 等于前序 closing_units。重置、缺口、回退或替代前序均为 INVALID。`frozen_unitization_method_definition` 冻结外部流时点、开局规则、舍入和公式，日账本 `nav_bridge_input_set_sha256` 将单位、标记仓位/批次、现金流/P&L 与有符号事件连接。冻结的 `reconciliation_expected_matrix_id`/SHA 逐日要求 mandatory/conditional 残差行、行数和集合 hash 对齐。零/负 NAV 或单位数不允许静默重置。锁箱起始状态需同时有 `primary_holdout_start_state_manifest` 和 `primary_holdout_start_state_component`；后者以 `component_type`、`component_row_reference`、`referenced_table_id`、适用账本外键、来源时间/状态、`referenced_row_sha256` 与成员哈希逐行证明，而非只有汇总散列；`frozen_roll_delivery_expiry_parameter_state` 也必须绑定；发展期状态不得带入。

`portfolio_position_lot_mark_ledger` 必分开 `economic_closing_quantity`、`eligible_to_sell_quantity`、`active_sell_reservation_quantity` 与 `available_to_sell_quantity`，并以 `available_to_sell_from` 表达 T+1 可卖起点，记录期货乘数/合约主数据、估值公式、账本币种标记值与冻结 FX quote/舍入。未成交卖出保留只影响可卖能力，绝不能降低经济仓位、标记市值或 NAV。ETF 的 `position_side` 只能是 LONG 或 FLAT；SHORT 和所有 ETF `OPEN_SHORT`/`CLOSE_SHORT` 订单或成交路径均为禁止，因为借券模型不在范围内。`execution_feasibility_reservation` 要求 `reservation_context_type` 的 DECISION/SUBMISSION/FILL 上下文、适用时的 `fill_id`、现金/保证金/T+1 批次保留池以及 before/preexisting/new/after 余额；不得超过可用余额或重复保留同一池。整数批量、T+1、现金、抵押品和保证金均须在交易时点可验证。

期货采用 `FUTURES_DAILY_MARGINED`：`marked_value`、账本币种标记值和 `unrealized_pnl` 均为零；`futures_daily_margin_notional_reference` 仅为暴露参考，绝不进入 NAV/TWRR。变动/最终结算以先前/当前结算价、数量和冻结乘数计算，必须只通过相连事件与 `cashflow_pnl_id` 计一次。期货 `TRADE_SETTLEMENT` 的名义结算现金腿为零，唯一例外是具有来源的 `futures_non_notional_adjustment_amount`；它绝不可用成交总名义替代现金或 NAV。

## 执行、结算、成交腿和成本

执行与结算为独立状态域。执行域含 `SUBMITTED`、`FAILED`、`CANCELLED` 等；结算域仅为 `NOT_APPLICABLE`、`PENDING`、`PARTIALLY_SETTLED`、`SETTLED`、`FAILED`。正成交默认从 `PENDING` 开始；仅在正成交时点、`transition_reason_code=DOCUMENTED_INSTANTANEOUS_CLEARING` 且有结算事件/来源证据时允许 `NOT_APPLICABLE->SETTLED`。`execution_order_state_transition` 仅存 `from_execution_state` / `to_execution_state` / `transition_at`；`execution_order_settlement_transition` 仅存对应结算字段。已成交结算失败保持 FILLED + settlement FAILED，不能混域；`PARTIAL->FAILED` 和 `PARTIAL->CANCELLED` 禁止，必须以 `PARTIAL_EXPIRED` 或 `PARTIAL_CANCELLED` 收尾。

每个订单在运行结束有 `NO_OPEN_ORDER`、`CANCELLED_AT_RUN_END`、`EXPIRED_AT_RUN_END` 或在冻结政策允许时 `CARRIED_WITH_OPENING_STATE`；后者必须链接下一运行的哈希绑定起始状态、不能跨入 PRIMARY_HOLDOUT，且不等同成交/结算。

每个正成交为不可变 `execution_fill_ledger` 的连续 `fill_sequence`，记录 `fill_id`、时点、数量/单位、`cumulative_filled_quantity`、`remaining_submitted_quantity`、价格/币种、`gross_notional`/符号约定、`execution_price_basis`、报价/代理、容量快照的合约/方向/时点/分区/消费序列、冲击证据及结算链接。每个 fill 必引用或序列绑定匹配的执行状态转换；累计/剩余量与时点一致，撤销/到期不得早于之后成交。订单金额、数量、费用、税费和结算须等于成交腿之和。

`execution_fill_ledger_event_link` 的 `linked_amount` 必按 `replay_run_id`、`ledger_event_id`、`linked_currency` 加总至事件 `amount`，且 `linked_currency=currency`；`fill_event_link_set_sha256`、link role 与事件类型、每 fill 的成交结算/保证金/最终结算/费用税费义务以及重复分配均由冻结的 `fill_event_link_allocation_rule_id`/SHA 校验。任何不守恒或重复分配均为 INVALID。

执行模型须冻结报价/深度、容量、已消耗容量、冲击模型或保守代理的来源/哈希。fill 不得超过剩余展示或模型容量；`FILL_TIME_QUOTE` 不得越过容量，证据不足只能保守代理或 no-fill。

每个 `execution_fee_tax_component` 直接分配给 `fill_id`（或显式订单级例外），类型仅为 `COMMISSION`、`EXCHANGE_FEE`、`CLEARING_FEE`、`OTHER_FEE`、`TAX`、`LEVY`。条款外键、来源版本、路由/账户/范围/有效期/币种及税费辖区必须有效。`term_calculated_amount`/`term_output_currency` 至 `amount`/`currency` 的转换必须引用 `frozen_fx_quote_conversion` 的 `fx_quote_id`/SHA、汇率和舍入；金额精确等于冻结汇率乘条款金额后的声明舍入，币种相同的 identity 情况也必须显式保留 quote/basis 证据。

事件仅使用 `CASH_ACCRUAL`、`DEBIT_ACCRUAL`、`COLLATERAL_ACCRUAL`、`COLLATERAL_TRANSFER`、`MARGIN_TRANSFER_CASH_LEG`、`TRADE_SETTLEMENT`、`INITIAL_MARGIN`、`MAINTENANCE_MARGIN`、`VARIATION_MARGIN`、`FINAL_SETTLEMENT`、`FEES_TAX`。每项事件记录一个 bucket/sign、原始与实际 `posted_balance_effect_ledger_currency_amount`、冻结 FX、公式/输入 hash，以及适用时的结算价、数量、transfer pair/leg、gross/posted/outstanding、应付/应收方向、signed 未结 NAV 和 `cashflow_pnl_id`。TRADE_SETTLEMENT/FEES_TAX 只入 CASH；DEBIT 仅为非负 DEBIT_ACCRUAL 负债增加。INITIAL/MAINTENANCE margin 与 COLLATERAL_TRANSFER 必有 `cash_margin_collateral_transfer_pair`：同日、同币、同刻一条负 CASH leg 和一条正 MARGIN/COLLATERAL leg，金额相加和 `net_nav_effect` 均为零且状态 PAIRED。Collateral leg 必使用有来源版本/引用的、已生效的 `cash_collateral_terms.term_type=COLLATERAL_TRANSFER` 正额值。未结净 NAV = 应收 − 应付并只进 bridge 一次；FAILED 必为零 posted/paid、outstanding=gross、有方向及最终 FAILED 转换/来源，不能伪装已结算或让端点 PASS。`effective_at`、来源、成交与状态转换时点必须因果有序，`event_balance_routing_set_sha256` 与残差对账须证明每个有符号事件只入账一次。`FEES_TAX` 严格映射 `NOT_APPLICABLE_FEE_TAX`，而其 CASH_BALANCE 适用性另做 role 审计；所有事件均须连至订单/成交（适用时）、账本、币种与来源。

## 前瞻覆盖、入口与 Q0

`prospective_state_configuration_coverage_audit` 的键为运行+覆盖行，且同一运行的 `configuration_tuple_sha256` 唯一。每个适用父类、路由/条款、范围/role、交易/事件、执行模型/可交易性、执行/结算/残余/结尾路径都需要一行。只有 `OBSERVED`、`ACCEPTED_CONSERVATIVE`、`SOURCE_PROVEN_NOT_APPLICABLE` 且有证据、`review_status=PASS` 才合格；`UNRESOLVED`、`FAILED`、非 PASS 或漏 tuple 是阻塞。60 日/10 观测只是必要条件；零阻塞仅在哈希绑定表的 `coverage_disposition in {UNRESOLVED,FAILED}`、`review_status != PASS` 和缺失预期 tuple 三类计数均为零时成立。

正式回放必须先满足授权、PIT/血缘、U0/T2、类模块、冻结规则/风险包、端点/锁箱、反泄露、执行/成本/可行性和独立 R0/R1/风险审查。研究用途“可用策略”标签只能在所有这些条件和零阻塞覆盖共同通过时才可能出现；否则始终 `q=0`，也不构成投资行动。
