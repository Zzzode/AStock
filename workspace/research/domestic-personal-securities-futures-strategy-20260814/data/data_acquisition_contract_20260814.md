# 数据采集合同 — DPSFS-DAC-v12

- 状态：**草案、未冻结；无授权、无正式回放、无配置或行动。**
- 机器可读权威：`data_acquisition_contract_20260814.json`，schema `data_acquisition_contract.v12`。
- 当前决定：UR01--UR05 均为 Open；所有对象保持 `q=0`。

## 冻结运行与 DD v8

未来运行必须冻结 `DPSFS-DD-v8`（`replay_data_dictionary_template.v8`）、规则书、DPSFS-RP0-v10、U0/推导、输入清单、版本截止、代码/环境/命令、锁箱及所有控制政策。唯一规范实体是已签署、不可变的 `replay_run_freeze_record`，绑定键为：

`replay_run_id` + `replay_run_freeze_record_sha256`

每个运行只有一个有效绑定；任何材料变更、序列化差异或事后绑定都必须创建新运行。所有运行域行的 **绑定字段** `replay_run_freeze_record_sha256` 必逐字节等于父冻结记录；行自身内容哈希仍独立，不能被强制等于父绑定哈希。无绑定、跨运行连接、不同绑定下重复业务键或通过文件路径推断绑定均为 INVALID。

冻结记录 schema 固定为 `replay_run_freeze_record.v2`；`data_contract_freeze_record_sha256=canonical_freeze_record_sha256`、`data_contract_sha256=contract_sha256`，且 `protocol_id`、`protocol_version`、`protocol_sha256` 分别逐字节等于 `formal_replay_protocol_id`、`formal_replay_protocol_version`、`formal_replay_protocol_sha256`。`freeze_timestamp=effective_from`，`supersedes_if_any` 仅为前一已签署运行 ID 或明确 `null`；字段名不得重复或用别名替换。

父记录还冻结 `fx_conversion_policy_id`/SHA、`master_calendar_daily_coverage_rule_id`/SHA 及 `unitization_method_id`/版本/SHA。三者分别约束 `frozen_fx_quote_conversion`、`master_calendar_daily_valuation_coverage` 和 `frozen_unitization_method_definition`；任何运行域 FX、日历覆盖或单位化方法行必须与父记录逐字节绑定。

行级绑定至少覆盖：

- `replay_candidate_endpoint_roster`、`replay_endpoint_population_audit`、`replay_endpoint_result`；
- `frozen_fx_quote_conversion`、`master_calendar_daily_valuation_coverage`、`frozen_unitization_method_definition`、`daily_portfolio_ledger`、`portfolio_unitization_ledger`、`portfolio_position_lot_mark_ledger`、`portfolio_cashflow_pnl_ledger`、`replay_reconciliation_residual`；
- `execution_order_ledger`、`execution_order_state_transition`、`execution_order_settlement_transition`、`execution_fill_ledger`、`execution_fill_ledger_event_link`、`execution_fee_tax_component`、`execution_feasibility_reservation`、`execution_cash_margin_settlement_ledger_event`、`cash_margin_collateral_transfer_pair`、`cash_collateral_role_applicability_audit`；
- `primary_holdout_start_state_manifest`、`primary_holdout_start_state_component`、`prospective_state_configuration_coverage_audit`。

## 端点总体、TWRR 与锁箱起始状态

端点须由 `replay_candidate_endpoint_roster`、`replay_endpoint_population_audit` 和 `replay_endpoint_result` 共同定义。名册使用 `master_calendar_id`/`master_calendar_sha256`、`candidate_generation_rule_id`/`candidate_generation_rule_sha256`、冻结的每日覆盖规则 ID/SHA、`calendar_anchor_at=a`、`selected_start_valuation_at=s`、`endpoint_end_valuation_at=e`、`window_start=s`、`window_end=e`、`elapsed_calendar_days`、起止日账本 ID、端点覆盖行数/已覆盖数/集合 hash/状态和 `expected_partition`；结果行逐字节携带同一覆盖证据。总体审计还须复核 evaluation-warmup 覆盖数/集合 hash/状态。锚点/起点/终点/天数均为规范审计字段，缺失、重复、越界或非覆盖会使端点 INCOMPLETE 或 INVALID，绝不可静默缩短窗口。

年化净 TWRR 必基于 `end_unit_nav / start_unit_nav`（或等价的链式单位 NAV）计算；存在外部现金流时绝不允许用总 NAV 比率。`endpoint_calculation_sha256` 必覆盖单位 NAV、外部现金流处理和公式。

端点状态由冻结的 `endpoint_status_rule_id`/`endpoint_status_rule_sha256`（`DPSFS-ENDPOINT-STATUS-v1`）及 `endpoint_calculation_population_policy_sha256` 机械校验：先判 `INVALID`，再判 `INCOMPLETE`，其余 `annualized_net_twrr >= 0.05` 为 `PASS`、`< 0.05` 为 `FAIL`；只允许 `UNIT_NAV_RATIO` 或 `CHAIN_LINKED_UNIT_NAV`，后者须以 `endpoint_unit_nav_chain_member`、`twrr_unit_nav_chain_member_count` 和链 hash 完整复算。`no-failed-settlement-in-endpoint-state` 与 `failed-settlement-contract-pass` 也是冻结谓词：任何 FAILED 结算、配对转移或未结算断言失败均使端点 INVALID，绝不能 PASS。冻结的 `candidate_endpoint_roster_id`/SHA、生成规则、a/s/e 和 `expected_partition` 必与每个结果行逐字节一致，`endpoint_partition=expected_partition`。总体审计必须证明：预期端点数 = 实际数 = 唯一名册数，预期/实际三个分区计数均一致，`status_count_total=pass_count+fail_count+incomplete_count+invalid_count=actual_candidate_endpoint_count`、`count_residual=0` 且 `population_reconciliation_status=PASS`；零数、短缺、重复、漏行或不一致必须保留并阻止通过。PRIMARY_HOLDOUT 还要求实际数 = 冻结预期数且至少 126 个、所有端点 PASS；CROSSING 绝不替代样本外结果。

每个 PRIMARY_HOLDOUT 起始状态必须由 `primary_holdout_start_state_manifest` 和规范化 `primary_holdout_start_state_component` 成员行建立，对应绑定的单位化、仓位/批次/标记、现金流/P&L、残差账本或明确中性重置证据。仅有汇总 NAV 或散列不足；发展期状态不得带入锁箱。

## 单位化、批次、保留与对账

`portfolio_unitization_ledger` 使用冻结的 `unitization_method_id`/版本/SHA、`prior_unitization_ledger_id`、`valuation_at`、`ledger_currency`、`opening_units`、`units_issued`、`units_redeemed`、`closing_units`、`external_cashflow_amount`、`external_flow_pricing_unit_nav`、`nav_before_external_cashflow`、`nav_after_external_cashflow`、`unit_nav` 和 `unitization_calculation_input_set_sha256`。唯一最先的 OPENING 行才可无前序且 opening_units=0；每个非 OPENING 行必须引用按 `valuation_at` 再 `unitization_ledger_id` 排序的即时前序，前序估值时点严格更早，且 opening_units 精确等于前序 closing_units。重置、缺口、回退或替代前序均为 INVALID。`frozen_unitization_method_definition` 固定外部流时点、开局规则、舍入和公式；`daily_portfolio_ledger.nav_bridge_input_set_sha256` 必将单位、仓位/批次标记、现金流/P&L 与事件路由连接起来。外部流在预流估值后处理；零/负 NAV 或单位数禁止静默 rebase，也不得被计为绩效。

`portfolio_position_lot_mark_ledger` 必分开 `economic_closing_quantity`、`eligible_to_sell_quantity`、`active_sell_reservation_quantity` 和 `available_to_sell_quantity`，并以 `available_to_sell_from` 表达 T+1 可卖起点，且保留期货乘数/合约主数据、估值公式、账本币种标记值和冻结 FX quote/舍入。未成交卖出保留只能减少可卖能力，不能减少经济仓位、标记市值或 NAV。ETF 的 `position_side` 只能为 LONG 或 FLAT，ETF `OPEN_SHORT`/`CLOSE_SHORT` 订单或成交路径以及 SHORT 持仓均禁止，因为借券模型不在范围内。`execution_feasibility_reservation` 必有 `reservation_context_type` 的 DECISION/SUBMISSION/FILL 上下文、适用时的 `fill_id`、保留池、`eligible_pool_balance_before`、`preexisting_active_reservation_quantity_or_amount`、`new_reservation_quantity_or_amount` 和 `eligible_pool_balance_after`；同一现金、保证金或 T+1 批次不得合计重复保留。交易时点必须可验证整数批量、T+1、现金、抵押品和保证金可行性。

`portfolio_cashflow_pnl_ledger` 以原子 `component_type`/`component_origin_type`/`effective_at` 行记录金额、`ledger_currency`/`ledger_currency_amount`、`fx_quote_id`/SHA/汇率/观察时点/舍入、`ledger_event_id`、`fill_id`、`position_id`、`lot_id` 与来源。仓位标记也必须保留同一 FX 证据、账本币种标记值及期货乘数/合约主数据/估值公式。`replay_reconciliation_residual` 以 `daily_ledger_id`、`reconciliation_matrix_row_id`、公式/来源集合 hash、`reconciliation_scope`、`reconciliation_component`、`expected_amount`、`actual_amount`、`residual_amount`、`tolerance_amount` 和 `reconciliation_input_sha256` 保留残差。冻结的 `reconciliation_expected_matrix_id`/SHA 要求每个日账本的 mandatory/conditional 集合、行数和集合 hash 完全对齐；未对账残差不可净额隐藏。

期货采用 `FUTURES_DAILY_MARGINED`：`marked_value`、账本币种标记值和 `unrealized_pnl` 均为零；`futures_daily_margin_notional_reference` 仅为暴露参考，绝不进入 NAV 或 TWRR。变动/最终结算必须由前/后结算价、数量和冻结乘数计算，并以一条事件及 `cashflow_pnl_id` 入账。期货 `TRADE_SETTLEMENT` 的名义结算现金腿默认为零，只有具有来源的 `futures_non_notional_adjustment_amount` 可作为独立非名义调整，绝不能用成交总名义替代现金或 NAV。

## 执行、状态、成交腿与费用税费

执行和结算为独立状态域。执行状态含 `SUBMITTED`、`FAILED`、`CANCELLED` 等；结算状态仅为 `NOT_APPLICABLE`、`PENDING`、`PARTIALLY_SETTLED`、`SETTLED`、`FAILED`。已成交结算失败保持 `execution_state=FILLED` 与 `settlement_state=FAILED`。正成交默认从 `PENDING` 开始；仅在正成交时点、`transition_reason_code=DOCUMENTED_INSTANTANEOUS_CLEARING` 且有结算事件/来源证据时允许 `NOT_APPLICABLE->SETTLED`。执行转换仅在 `execution_order_state_transition` 中使用 `from_execution_state`/`to_execution_state`/`transition_at`；结算转换仅在 `execution_order_settlement_transition` 中使用对应结算字段，二者不得混用。`PARTIAL->FAILED` 和 `PARTIAL->CANCELLED` 禁止，必须以 `PARTIAL_EXPIRED` 或 `PARTIAL_CANCELLED` 收尾。

运行结束每个订单有 `NO_OPEN_ORDER`、`CANCELLED_AT_RUN_END`、`EXPIRED_AT_RUN_END` 或经 `end_of_run_carry_cancel_policy_sha256` 允许并链接下一运行起始清单的 `CARRIED_WITH_OPENING_STATE`。结转不构成成交或结算、不得跨入 PRIMARY_HOLDOUT；撤销/到期不抹去已成交腿、费用税费或结算义务。

正成交由不可变 `execution_fill_ledger` 的连续序列构成，要求 `fill_id`、`fill_sequence`、成交时点、数量/单位、`cumulative_filled_quantity`、`remaining_submitted_quantity`、`gross_notional`/币种/符号约定、`execution_price_basis`、报价或保守代理、容量快照的合约/方向/时点/分区/消费序列以及结算链接。每个 fill 必引用或序列绑定相符的执行状态转换，时点、累计/剩余量必须一致，撤销/到期不得早于之后的成交。订单汇总必须等于成交腿精确之和。

`execution_fill_ledger_event_link` 的 `linked_amount` 必按 `replay_run_id`、`ledger_event_id`、`linked_currency` 加总至事件 `amount`，且 `linked_currency=currency`；`fill_event_link_set_sha256`、link role 与事件类型、每 fill 的成交结算/保证金/最终结算/费用税费义务、重复分配均由冻结的 `fill_event_link_allocation_rule_id`/SHA 校验。任一未守恒或重复分配均为 INVALID。

执行模型须冻结报价/深度、流动性容量、已消耗容量、冲击模型或保守代理的来源/哈希；任何 fill 不得超过剩余展示或模型容量，`FILL_TIME_QUOTE` 不得越过容量，证据不足时只能保守代理或 no-fill。

每个 `execution_fee_tax_component` 直接分摊到一个 `fill_id`（或显式订单级例外），类型只能为 `COMMISSION`、`EXCHANGE_FEE`、`CLEARING_FEE`、`OTHER_FEE`、`TAX`、`LEVY`。组件有有效的经纪/税费条款外键、来源版本、路由/账户/范围/有效期/币种，税/征费还有辖区。`term_calculated_amount`/`term_output_currency` 转至 `amount`/`currency` 时必须引用 `frozen_fx_quote_conversion` 的 `fx_quote_id`/SHA、汇率和舍入规则；金额精确等于条款金额乘冻结汇率后的声明舍入，币种相同的 identity 情况也必须显式留存同一 quote/basis 证据。合并组件、隐含零额、空币种或未解决辖区禁止。

事件类型严格为 `CASH_ACCRUAL`、`DEBIT_ACCRUAL`、`COLLATERAL_ACCRUAL`、`COLLATERAL_TRANSFER`、`MARGIN_TRANSFER_CASH_LEG`、`TRADE_SETTLEMENT`、`INITIAL_MARGIN`、`MAINTENANCE_MARGIN`、`VARIATION_MARGIN`、`FINAL_SETTLEMENT`、`FEES_TAX`。每个 `execution_cash_margin_settlement_ledger_event` 还须有 `balance_effect_bucket`/符号、原始和实际 `posted_balance_effect_ledger_currency_amount`、FX quote/舍入、公式及输入集合 hash，以及适用时的前/后结算价、计算数量、转移 pair/leg、gross/posted/outstanding、应付/应收方向、signed 未结 NAV 和 `cashflow_pnl_id`。`TRADE_SETTLEMENT` 与 `FEES_TAX` 只能进 CASH，DEBIT 只允许非负 `DEBIT_ACCRUAL` 负债增加，禁止隐性融资。每项 INITIAL/MAINTENANCE margin 或 collateral 转移必须加入 `cash_margin_collateral_transfer_pair`：同日、同币、同刻一条负 CASH leg 和一条正 MARGIN/COLLATERAL leg，金额相加及 `net_nav_effect` 均为零且状态 PAIRED；`COLLATERAL_TRANSFER` 必有已生效、含来源版本/引用的正额 `cash_collateral_terms.term_type=COLLATERAL_TRANSFER`。未结净 NAV = 应收 − 应付，只进日 NAV bridge 一次；FAILED 必为零 posted/paid、outstanding=gross、有方向及最终 FAILED 转换/来源证据，不能伪装已结算、交割完成或 PASS。`effective_at`、来源、订单/成交/转换时点须因果有序，日账本 `event_balance_routing_set_sha256` 必证明每一有符号事件只入账一次。`FEES_TAX` 映射 `NOT_APPLICABLE_FEE_TAX`，其 `CASH_BALANCE` 适用性另经 role 审计；不得以收益或保证金条款为费用税费定价。

## 数据包、前瞻覆盖与入口

ETF PIT、实际期货合约与执行成本包均须具备授权、原始/规范化血缘、available-at、版本和独立对账。事后获取但无历史 available-at 的数据是 retrospective，不是 PIT；连续/事后主力合约不能替代实际合约 P&L/滚动。

`prospective_state_configuration_coverage_audit` 以 `replay_run_id` + `coverage_row_id` 为键，并要求唯一 `configuration_tuple_sha256`。每个适用的父类、路由/条款、范围/role、交易/事件、执行模型/可交易路径、执行/结算/残余/结尾状态必须有一行。只有 `OBSERVED`、`ACCEPTED_CONSERVATIVE`、`SOURCE_PROVEN_NOT_APPLICABLE` 且有证据并 `review_status=PASS` 可满足要求；`UNRESOLVED`、`FAILED`、非 PASS 或缺失预期 tuple 都是阻塞。60 日和 10 个观测只是必要条件；零阻塞只在哈希绑定表中 `coverage_disposition in {UNRESOLVED,FAILED}`、`review_status != PASS` 和缺失预期 tuple 三类计数均为零时成立，不能叙述声明或删行取得。

UR01--UR04 以及独立 UR05 风险/纸面/覆盖审查全部通过前，正式回放不得开始；在此之前没有绩效、产品准入、配置、持仓或行动结论，`q=0`。
