# 回放数据字典模板

- 字典：`DPSFS-DD-v8`，schema：`replay_data_dictionary_template.v8`，版本 8；继承 `DPSFS-DD-v7`。
- 状态：**仅模板，未冻结、不含数据。**
- 边界：研究用途；`portfolio_q=0`。本文件不构成数据权利、回放结果、配置、持仓或行动授权。

## 通用数据和冻结控制

所有表都适用相同的来源元组：`source_id`、`raw_sha256`、`source_revision`、`as_of`、`available_at`、供应商发布时间、本地接收时间、`normalization_run_id`、`quality_status` 和 `exception_id`。时间为带显式 UTC 偏移的 ISO-8601；货币与价格不得默认人民币；冻结会计输出不得使用二进制浮点数。数值缺失不得用哨兵值或零代替：除来源明确报零外，空值必须配合 `REJECTED`/`EXCEPTION` 和异常记录。

`replay_run_freeze_record` 是唯一的运行冻结父表。每张运行期表必须同时带有：

- `replay_run_id`
- `replay_run_freeze_record_sha256`

该复合键必须精确引用一个 `freeze_status=SIGNED` 的父行；父行的 canonical freeze-record hash、DD hash、输入清单 hash、source-revision cutoff、所有策略 hash 以及 DAC/RP 冻结 crosswalk 必须逐字节相同。无父行、父行未签署、哈希不同、crosswalk 不可解析或重复但值不同，均为 `INVALID`。

父行不得以近似别名代替 DAC/RP 的冻结字段。它必须直接保存 `replay_run_freeze_record_schema_version`、`data_contract_freeze_record_sha256`、`data_contract_sha256`、`protocol_id`、`protocol_version`、`protocol_sha256`、`freeze_timestamp`、`supersedes_if_any`、`data_dictionary_id` 和 `data_dictionary_schema_version`。其中 schema version 固定等于 `replay_run_freeze_record.v2`；两个 data-contract hash 分别等于 canonical freeze-record/contract hash；三个 `protocol_*` 分别等于 `formal_replay_protocol_*`；`freeze_timestamp=effective_from`；有前序签署运行时 `supersedes_if_any` 等于其 `replay_run_id`，否则为显式 null；`data_dictionary_id`/`data_dictionary_schema_version` 分别等于本文档顶层 `dictionary_id`/`schema_version`。

这种关系不是文字约定：`machine_validation_contract.frozen_run_crosswalk.byte_equality_map` 是逐条结构化映射。每条都包含唯一的父表 `{table_id,column}`、唯一的目标（同表字段，或含 `artifact_path` 和 JSON Pointer 的外部字段，或明确 SHA-256 artifact digest）、`cardinality=exactly_one` 及 `operator=equals_byte_for_byte`。只有父行 `SIGNED` 时映射激活；解析器必须将每个源/目标都恰好解析一次并逐字节比较，任何缺失、重复、近似别名或不匹配都为 `INVALID`。

父表逐项保存 DAC/RP 的完整冻结绑定：合同、规则书、正式回放协议、决策宇宙、U0 与 U0→T2 审计、DD、锁箱谓词/起止/暖机、输入清单、来源截点、代码提交、运行环境、精确命令、首次可看结果时间、风险包、状态矩阵、批准信息和变更控制；并增加以下独立策略 hash：

- `end_of_run_carry_cancel_policy_sha256`
- `endpoint_calculation_population_policy_sha256`
- `portfolio_unitization_positions_lots_cashflow_reconciliation_policy_sha256`
- `fill_leg_partial_fill_allocation_policy_sha256`
- `broker_tax_component_policy_sha256`
- `execution_settlement_state_policy_sha256`
- `prospective_state_configuration_coverage_policy_sha256`

端点和会计的冻结控制也有直接字段及 crosswalk：`master_calendar_id`/`master_calendar_sha256`、`evaluation_interval_start/end`、`raw_data_coverage_start/end`、`candidate_generation_rule_id`/`candidate_generation_rule_sha256`、`candidate_endpoint_roster_id`/`candidate_endpoint_roster_sha256`、`expected_development_count`/`expected_crossing_count`、`endpoint_status_rule_id`/`endpoint_status_rule_sha256`、`reconciliation_expected_matrix_id`/`reconciliation_expected_matrix_sha256`、`fill_event_link_allocation_rule_id`/`fill_event_link_allocation_rule_sha256`、`fx_conversion_policy_id`/`fx_conversion_policy_sha256`、`master_calendar_daily_coverage_rule_id`/`master_calendar_daily_coverage_rule_sha256` 与 `unitization_method_id`/`unitization_method_version`/`unitization_method_sha256`。`replay_run_id` 亦逐字节映射到 canonical freeze record；`replay_run_freeze_record_sha256` 则以所有已声明父行字段（排除自身）的规范序列化重算并映射到 canonical record，不能以自引用或近似 hash 通过。

## 规范化表

| JSON `table_id` | 主键 | 核心字段/机器约束 |
|---|---|---|
| `replay_run_freeze_record` | 回放运行 | 完整 canonical freeze 交叉表、DAC/RP 同名冻结字段和逐字节 equality map、所有 ID/版本/hash、签署状态及本行 hash |
| `etf_instrument_master` | 证券、有效起点、修订 | 交易所、名称、上市/终止、状态与有效期 |
| `etf_market_session` | 证券、交易日、修订 | OHLC、昨收、量额、价格/金额货币和量单位 |
| `etf_nav_event` | 证券、NAV 日、公告时点、修订 | NAV、调整基准、IOPV、公告时间和货币 |
| `etf_corporate_action` | 证券、动作、除权/登记/支付日、修订 | 现金分配、调整因子、可用时间和货币 |
| `etf_tradability_session` | 证券、交易日、阶段、修订 | 可交易/停牌/涨跌停状态和限价 |
| `futures_contract_master` | 合约、有效起点、修订 | 实际挂牌合约、生命周期、乘数、跳动、报价单位/货币和交割方法 |
| `futures_market_session` | 合约、交易日、修订 | 结算、OHLC、成交、持仓及显式单位/货币 |
| `futures_effective_terms` | 合约/品种、术语、有效起点、修订 | 保证金、费用、限额、结算/交割等有日期术语 |
| `futures_tradability_session` | 合约、交易日、阶段、修订 | 交易、停牌、涨跌停、交割限制及换月状态 |
| `execution_broker_terms` | `broker_route_terms_id`、修订 | 类型化 route/account/instrument-or-product scope、有效期、辖区 FK、T+1、lot、现金/保证金预留与结算规则；不存合并费税 |
| `tax_jurisdiction` | 辖区、有效起点、修订 | 法域、税务机关、纳税人适用范围及有效期 |
| `broker_fee_term` | 费用术语、修订 | route-term FK、类型化 scope、单一 fee component、计费法、币种/基数、有效期 |
| `tax_levy_term` | 税/附加术语、修订 | route-term 和 `tax_jurisdiction` 复合 FK、类型化 scope、单一 TAX 或 LEVY、计税法、有效期 |
| `execution_market_snapshot` | 标的、报价时点、修订 | bid/ask、深度、报价年龄、状态、价格/数量单位 |
| `cash_collateral_terms` | 现金抵押术语、修订 | route/account、确定性 scope、兼容投影字段、币种、日计数、复利、起止/划拨截止；`COLLATERAL_TRANSFER` 行以有效期内的正数金额、币种、来源修订和来源证据冻结抵押划拨 |
| `cash_collateral_term_set_membership` | term-set、角色、术语、修订 | 不可变 term-set 与应用角色/有效期 |
| `execution_order_ledger` | 运行、订单 | 路由/术语、可交易性、数量、`execution_state` 与 `settlement_state`、fill/费用/事件/预留集合 hash、回放末日处置 |
| `execution_order_state_transition` | 运行、订单、序号 | 仅执行状态的连续状态机：`from_execution_state`/`to_execution_state` |
| `execution_order_settlement_transition` | 运行、订单、结算序号 | 仅结算状态的连续状态机：`from_settlement_state`/`to_settlement_state` |
| `execution_fill_ledger` | 运行、fill | 不可变逐笔 fill：累计/剩余成交量、匹配执行状态迁移、报价/深度/容量/冲击、结算与组件集合 hash |
| `execution_fill_ledger_event_link` | 运行、fill、事件 | fill 与成交结算/保证金/最终结算/费税事件的类型化链接及金额/币种 |
| `execution_fee_tax_component` | 运行、费税组件 | 一行一个组件和一个币种；fee 或 tax/levy 的有效期术语 FK；可按 fill 或订单分摊；唯一 FEES_TAX 事件 FK |
| `execution_feasibility_reservation` | 运行、预留 | 决策/提交/每笔 fill 时点的 T+1 lot、现金/保证金预留，pool、有效区间、状态、前后容量和 PASS/FAIL |
| `frozen_fx_quote_conversion` | 运行、FX quote | 唯一的冻结行级汇兑来源：from/to currency、rate、as-of、source revision、basis、舍入与 quote hash |
| `master_calendar_daily_valuation_coverage` | 运行、scope、日历 session | raw/evaluation/warmup 与每个候选 s–e 内每个合格主日历 session 的日估值覆盖行 |
| `frozen_unitization_method_definition` | 运行、方法、版本 | 外部现金流 pre-flow 定价、opening rule、公式、舍入和方法 hash |
| `daily_portfolio_ledger` | 运行、日账本 | 现金/融资/抵押/保证金/NAV、`fx_quote_set_sha256`、事件路由/NAV bridge 输入、单位化 ID、仓位/现金流/残差集合 hash |
| `portfolio_unitization_ledger` | 运行、单位化账本 | 冻结方法 ID/version/hash、前序 unit NAV、发行/赎回 pre-flow 定价、单位数、单位 NAV、日 NAV bridge 对账 |
| `portfolio_position_lot_mark_ledger` | 运行、估值时点、仓位、lot | lot 来源、经济开/平/期末数量、`ETF_SHARES`/`FUTURES_DAILY_MARGINED` 类型化标记公式、dated multiplier、行级 FX 后 marked value 与 P&L；日盯市 futures 的 marked value/P&L 均为零，名义金额仅作暴露参考 |
| `portfolio_cashflow_pnl_ledger` | 运行、现金流/P&L 组件 | 单一组件/币种、事件/fill/lot FK、唯一 frozen FX quote/identity 转换、来源和组件 hash |
| `replay_reconciliation_residual` | 运行、残差 | 单位化、仓位、现金流、事件、费税、FX、订单/fill、端点的 expected/actual/residual/tolerance/status |
| `execution_cash_margin_settlement_ledger_event` | 运行、事件 | 精确事件类型→角色、route term、订单/fill/日账本 FK、唯一 balance bucket/cashflow、gross 与实际 posted 金额、计算公式/输入 hash、FX、带 PAYABLE/RECEIVABLE 方向的未结残差与事件 hash |
| `cash_margin_collateral_transfer_pair` | 运行、划拨对 | 每个初始/维持保证金或抵押划拨的一负 CASH leg 与一正 MARGIN/COLLATERAL leg、同日/币种/时点、已 posted 金额、零 NAV 效应和 pair hash |
| `cash_collateral_role_applicability_audit` | 运行、上下文类型/ID、角色 | 每订单/事件每角色一行，必须/不适用的可验证结论及 term FK |
| `primary_holdout_start_state_manifest` | 运行、holdout 窗口 | 后锁箱状态组件 hash、规范化组件集合 hash/行数及完整性 |
| `primary_holdout_start_state_component` | 运行、holdout 窗口、组件、行引用 | 对单位化、仓位 lot/mark、现金流/P&L、残差及其他状态行的类型化 FK、后锁箱来源和行完整性 |
| `frozen_roll_delivery_expiry_parameter_state` | 运行、参数状态 | 规范化 roll、delivery、expiry 或决策参数状态的类型化来源、可用时点与行 hash |
| `replay_candidate_endpoint_roster` | 运行、候选端点 | a/s/e 时间语义、冻结 roster/input hash、首末日账本 FK、预期分区与唯一端点 |
| `replay_endpoint_population_audit` | 运行、端点总体审计 | roster/input hash、冻结与实际总体/分区/PASS-FAIL-INCOMPLETE-INVALID 计数、零候选状态、逐候选一次映射 |
| `replay_endpoint_result` | 运行、端点 | 候选 FK、a/s/e、首末日账本、单位 NAV TWRR、分区/状态、holdout manifest 与计算 hash |
| `endpoint_unit_nav_chain_member` | 运行、端点、链序号 | chain-linked unit-NAV 的有序成员、单位化 FK、前序 NAV/link factor 与成员 hash |
| `prospective_state_configuration_coverage_audit` | 运行、覆盖行 | 每个 class/route/term/scope/角色/交易/事件/执行路径/结算路径/残余/末日处置 tuple 的证据与 PASS/FAIL |

## 关键状态、逐笔成交和费税规则

执行状态和结算状态完全分表、分矩阵。执行状态仅为 `CREATED`、`SUBMITTED`、`PARTIAL`、`FILLED`、`PARTIAL_EXPIRED`、`PARTIAL_CANCELLED`、`NO_FILL`、`EXPIRED`、`CANCELLED`、`REJECTED`、`FAILED`、`NOT_SUBMITTED`；因此 `SUBMITTED`、`FAILED` 与 `CANCELLED` 都是合法的**执行**状态。结算状态严格且仅为 `NOT_APPLICABLE`、`PENDING`、`PARTIALLY_SETTLED`、`SETTLED`、`FAILED`；`SETTLED` 绝不是执行状态，运行末日处置也绝不是结算状态。执行链从 `CREATED` 开始，连续编号、相邻衔接、时间非递减，最后状态等于订单的 `execution_state`。结算链独立连续，最后状态等于订单的 `settlement_state`。

`REJECTED_PRE_SUBMISSION` 必须是 `CREATED->REJECTED`、无提交时间、无成交；`NOT_SUBMITTED` 必须是 `CREATED->NOT_SUBMITTED`、无提交/拒绝/成交/到期时间。零成交的提交后运行失败只能使用 `SUBMITTED->FAILED`。部分成交只能在有正成交且小于提交量时存在；后续部分成交使用 `PARTIAL->PARTIAL`。部分成交的运行失败或取消必须使用 `PARTIAL->PARTIAL_CANCELLED`，并有 `partial_failure_or_cancellation_code`、取消时点及残余取消原因；禁止 `PARTIAL->FAILED` 与 `PARTIAL->CANCELLED`。运行结束时，任何未终结订单必须仅由 `end_of_run_order_disposition` 按已冻结规则显式取消、到期，或以 hash 绑定的 opening-state manifest 结转；不允许隐式 carry。

常规结算从 `NOT_APPLICABLE->PENDING` 开始。仅当存在正成交、同一时点的结算事件及来源证据，且 `transition_reason_code=DOCUMENTED_INSTANTANEOUS_CLEARING` 时，才允许直接 `NOT_APPLICABLE->SETTLED`；其余情形不得绕过 `PENDING`。

`FAILED` 是终结的结算失败而非可忽略标签：失败事件不得已有 posted/paid 金额或交割/平仓效果，必须有异常/来源引用并与订单结算状态机的终态相符。`endpoint_status_rule.invalidity_predicates.no-failed-settlement-in-endpoint-state` 对整个运行显式要求不存在 `FAILED` 结算状态或事件；任一失败均为 `INVALID`，绝不能使端点 `PASS`。

每笔 fill 都必须保留时间、数量、单位、价格、价格币种、名义金额、取价依据、`cumulative_filled_quantity`、`remaining_submitted_quantity`、对应的执行状态迁移序号/边/时点以及 fill hash，并通过 `execution_fill_ledger_event_link` 连接至相关事件。`gross_notional` 不是自由输入：ETF 必须使用乘数 1，futures 必须引用有效合约主数据的 dated multiplier，并以 `fill_quantity × fill_price × multiplier` 按 `ROUND_HALF_EVEN` 重算；`ABSOLUTE` 或 signed-cashflow 的方向符号固定。订单成交量为各 fill 数量之和；订单价格为同币种数量加权平均价。容量不能只按单行计算：每笔 fill 还必须保存由标的、对手方侧、单位、as-of、修订、snapshot ID 与 partition 构成的 typed capacity key 及跨**所有订单**的 `capacity_consumption_sequence`。该 sequence 必须等于 `(capacity_snapshot_as_of, fill_at, fill_id)` 的时间序 rank；此前消耗量只可汇总这个 tuple 严格更早的 fill，累计不得超过同一固定 available quantity；两个订单不能各自将同一深度的此前消耗记为零。`FILL_TIME_QUOTE` 的 fill 不得超过记录的深度容量，保守代理必须使用显式的保守 partition，不能冒充报价深度。终结的取消、到期、拒绝、失败、无成交或部分终结状态后不得再有 fill。

费税不存在合并的双组件值或“fees and tax”金额。`execution_fee_tax_component` 的每行仅有一个组件和一个币种，且只能是 `COMMISSION`、`EXCHANGE_FEE`、`CLEARING_FEE`、`OTHER_FEE`、`TAX` 或 `LEVY`。费用行必须有 `broker_fee_term` FK；税/附加行必须有 `tax_levy_term` 与辖区 FK。`term_calculated_amount` 与 `term_output_currency` 必须先按有效术语计算；若再转换币种，组件本身必须以 `fx_quote_id` 精确引用 `frozen_fx_quote_conversion`，保存 rate/source/as-of/quote hash/basis/`ROUND_HALF_EVEN` precision，并令 `amount=ROUND_HALF_EVEN(term_calculated_amount×quote rate)`。同币种时所有 pre-event FX 字段均为 null 且 amount 等于 term output。组件经此转换后才可映射到一个 `FEES_TAX` 事件；`PER_FILL` 组件必须有 `fill_id` 并通过该 fill 的 event link 直连。`PER_ORDER` 只有在同时保留 `order_level_exception_reference`、来源、费用时点和 allocation rule ID/hash 时才可用，且该规则必须把精确术语金额/币种分配到事件或 fill，不得双计。所有方向均按币种对账。

## 事件、角色、可行性和对账规则

事件到角色的映射是固定的：

| `event_type` | `application_role` |
|---|---|
| `CASH_ACCRUAL` | `CASH_BALANCE` |
| `DEBIT_ACCRUAL` | `DEBIT_BALANCE` |
| `COLLATERAL_ACCRUAL` | `COLLATERAL` |
| `COLLATERAL_TRANSFER` | `COLLATERAL` |
| `MARGIN_TRANSFER_CASH_LEG` | `CASH_BALANCE` |
| `TRADE_SETTLEMENT` | `TRADE_SETTLEMENT` |
| `INITIAL_MARGIN` | `INITIAL_MARGIN` |
| `MAINTENANCE_MARGIN` | `MAINTENANCE_MARGIN` |
| `VARIATION_MARGIN` | `VARIATION_MARGIN` |
| `FINAL_SETTLEMENT` | `FINAL_SETTLEMENT` |
| `FEES_TAX` | `NOT_APPLICABLE_FEE_TAX` |

非 `FEES_TAX` 事件只能使用现金/抵押术语并映射同名角色；`FEES_TAX` 仅使用 broker-fee 或 tax-levy 术语，现金/抵押定价字段必须为空，且仍须形成现金余额角色审计。每笔订单和每个事件均有每角色一行的适用性审计；scope 以 `CONTRACT → INSTRUMENT → INSTRUMENT_CATEGORY → ACCOUNT_WIDE` 的唯一最高优先级解析。

`execution_fill_ledger_event_link` 不只是引用表。冻结的 `fill_event_link_allocation_rule` 给出唯一的 event-type ↔ link-role 矩阵：成交结算、初始/维持/变动保证金、最终结算和费税只能分别使用相应 role；三种 accrual 及两种 paired-transfer 事件不可链接。每个可链接 event/currency 的 `SUM(linked_amount)` 必须精确等于**由其 `event_calculation_formula_id`/hash/input-set 重算的** event amount，link currency 必须等于 event currency，且 event 的 link-set hash 与有序逐行 hash 集合一致。ETF 成交结算由 fill notional 与 dated term 计算；futures 的交易结算现金腿严格为零，只有带独立金额、来源引用及 formula ID 的非名义调整才可形成事件。初始/维持保证金由填单或持仓基数、dated term 和 multiplier 计算；futures 变动/最终结算必须为有向合约数 × multiplier × `(current_settlement_price-prior_settlement_price)`（外加仅有明确 dated term 的最终调整）。每笔 fill 各 role 的成交结算/保证金/最终结算/费用税费义务也必须精确对该计算义务；重复、遗漏或过度分配均为 `INVALID`。

卖出/平仓前必须以 `execution_feasibility_reservation` 验证可卖 lot 和 T+1 到期时间；买入/开仓必须验证现金购买力和所有触发的保证金预留。每笔订单必须有 `DECISION` 预留观测，已提交订单还必须有 `SUBMISSION` 观测，每笔 fill 必须有带 `fill_id` 的 `FILL` 观测；`context_at` 必须分别等于 decision/submitted/fill 时点，且来源观测不得晚于该时点。预留记录含 typed pool snapshot ID/time/unit-currency、跨 pool snapshot 的全局 sequence、状态、有效区间、预留前 eligible balance、此前活跃预留、新预留和预留后余额。该 sequence 必须等于 `(reservation_pool_snapshot_at, context_at, reservation_id)` 的时间序 rank；`preexisting_active` 只可由该 tuple 严格更早、并在当前上下文前活跃的预留精确汇总。`PASS` 必须满足 `0 <= new <= eligible_before - preexisting_active` 且 `eligible_after >= 0`。即使 FILL 时行状态变为 `CONSUMED`，也必须标记为 `active_immediately_before_context=true` 并进入该汇总，不能逃避 pool 限额。每个 lot pool 只分配一个 lot，且活跃分配不得超过该 lot 的 `eligible_to_sell_quantity`。任何 `FAIL`、`INCOMPLETE` 或 `INVALID` 都阻断相应提交/成交。

单位化账本、仓位/lot/marks、现金流/P&L 和残差表均按逐行显式币种/单位对账。`frozen_fx_quote_conversion` 是唯一行级 FX 来源：每个非本位币现金流、事件、标记或 pre-event fee/tax component 必须引用一个精确的 quote（币种方向、rate、as-of、source revision、basis、`ROUND_HALF_EVEN` precision 和 quote hash）；同币种只能使用 rate=1 且 quote FK 为 null。`daily_portfolio_ledger.fx_quote_set_sha256` 必须等于实际引用的非 identity quote（含当日关联 fee/tax component）的规范有序集合。

每个 `execution_cash_margin_settlement_ledger_event` 都有一个且仅一个 `balance_effect_bucket`（`CASH`、`DEBIT`、`COLLATERAL` 或 `MARGIN`）、gross `ledger_currency_amount`、实际 `posted_balance_effect_ledger_currency_amount`、以及一个 `cashflow_pnl_id`。该事件→现金流链接是双向一对一：事件进入对应余额桶一次，事件关联的现金流组件只作证据、不得再计入同一余额桶。交易结算和费税只能进入 `CASH`；`DEBIT` 仅允许非负 `DEBIT_ACCRUAL`。未结结算以 `PAYABLE` 或 `RECEIVABLE` 明确方向：只有未 posted 的余额以 payable 为负、receivable 为正进入 NAV，一笔已 posted/paid 金额绝不重复进入 bridge。

`INITIAL_MARGIN`、`MAINTENANCE_MARGIN` 与 `COLLATERAL_TRANSFER` 必须各自归属一个不可变 `cash_margin_collateral_transfer_pair`：一条负 `MARGIN_TRANSFER_CASH_LEG` 进入 CASH，另一条正 reserve leg 进入 MARGIN 或 COLLATERAL；两腿同运行、日账本、币种与时点，且均为实际 posted 金额，故净 NAV 效应恰为零。抵押划拨 reserve leg 还必须引用有效的 `cash_collateral_terms.term_type=COLLATERAL_TRANSFER`、正数金额/币种、来源修订/证据及 `COLLATERAL` 角色成员。变动保证金和最终结算不属于这种资产划拨对。

关键方程包括：

- `closing_units = opening_units + units_issued - units_redeemed`
- 每个运行恰有一个且时间序第一条 `OPENING`；其 `opening_units=0`、无 prior 行、正 seed `external_cashflow_amount`、`units_issued=closing_units`、`units_redeemed=0` 且 `nav_before_external_cashflow=0`。之后每一条 MARK/ISSUE/REDEEM/FINAL 必须精确引用按 `(valuation_at, unitization_ledger_id)` 紧邻的前一行，`opening_units=prior.closing_units` 且 `prior_unit_nav=prior.unit_nav`；不允许重置单位数、跳跃或时间倒退
- `total_nav = cash_balance - debit_balance + collateral_balance + margin_balance + SUM(marked_value_ledger_currency) + SUM(unsettled_net_nav_ledger_currency_amount where settlement_obligation_status IN (UNSETTLED, PARTIALLY_SETTLED))`；payable residual 为负、receivable residual 为正
- `NAV_BRIDGE` 证明后流 `total_nav`；`nav_before_external_cashflow = total_nav - SUM(非事件 EXTERNAL_CAPITAL 的 ledger-currency amount)`，而 `nav_after_external_cashflow = nav_before_external_cashflow + external_cashflow_amount = daily_portfolio_ledger.total_nav`
- ISSUE/REDEEM 单位数必须以冻结的 `PRE_FLOW_PRIOR_UNIT_NAV` 方法按 `ABS(external_cashflow_amount)/external_flow_pricing_unit_nav` 计算并指定舍入；`prior_unit_nav` 必须等于上一条单位化行，除 OPENING 外
- ETF 仅可为 `LONG`/`FLAT`，且禁止 `OPEN_SHORT`/`CLOSE_SHORT`（本模板不定义借券证据）；ETF `marked_value = quantity × mark_price`。日盯市 futures 的 `marked_value`、`marked_value_ledger_currency` 与 `unrealized_pnl` 均为零；`position_side_sign × contracts × mark_price × dated multiplier` 仅作为不进入 NAV/TWRR 的 exposure reference，P&L 只能经变动保证金或最终结算进入
- `economic_closing_quantity = economic_opening_quantity + economic_quantity_opened - economic_quantity_closed`
- `available_to_sell_quantity = eligible_to_sell_quantity - active_sell_reservation_quantity`
- 活跃卖出预留绝不减少经济仓位、`marked_value` 或 NAV
- `residual_amount = actual_amount - expected_amount`
- 仅当 `ABS(residual_amount) <= tolerance_amount` 时残差可为 `PASS`

每个日账本还必须由冻结的 `reconciliation_expected_matrix` 生成一套完整 residual 行：至少包括现金、融资、抵押/保证金、经济仓位的 marked value、强制 `NAV_BRIDGE` 与单位化/NAV；有适用来源时另含 FX、fill 和 fee/tax。每一行都绑定 matrix row、formula ID/hash 和实际解析的 source-set hash；日账本的 expected/actual row count 与 expected/actual ordered set hash 必须精确相等。空残差集或通过少列行来得到“零残差”均为 `INVALID`。

## 端点总体和前瞻覆盖

每个候选端点先进入 `replay_candidate_endpoint_roster`。其时间只有一套 a/s/e 语义：`calendar_anchor_at=a`（冻结五年历日锚）、`selected_start_valuation_at=s`（不晚于 a 的最后一个合格估值）、`endpoint_end_valuation_at=e`（端点结束估值），且必须 `s<e`、`elapsed_calendar_days=e-s>0`。兼容字段 `window_start` 只能等于 s，`window_end` 只能等于 e；`start_daily_ledger_id`/`end_daily_ledger_id` 及 `start_unitization_ledger_id`/`end_unitization_ledger_id` 必须分别引用 s/e 的日账本和单位化账本，起止 unit NAV 必须与该单位化行逐字节相等。roster/result/population 必须共用冻结的 `master_calendar_id`/hash、candidate-generation rule ID/hash 和 master-calendar daily-coverage rule ID/hash；population 还必须逐字节复现 evaluation interval 与 raw-data coverage。`candidate_roster_generation_contract` 要求生成候选集合、排序、逐行 hash、roster hash、预期/实际分区计数均精确匹配，不能增删候选。

`master_calendar_daily_valuation_coverage` 不是区间边界检查：它为 raw-data/evaluation/warmup 范围内以及每个候选 s–e 内**每一个合格主日历 session**生成一行。`COVERED` 必须精确引用该 session 的唯一 daily ledger；`MISSING` 使 scope 为 `INCOMPLETE`，`INVALID` 使其为 `INVALID`。候选/result 的 `endpoint_window_coverage_row_count`、`endpoint_window_covered_count`、set hash 和 status，及 population audit 的 evaluation/warmup 对应 count/hash/status 均必须由这些行生成。任何一处覆盖不为 `PASS`，候选不能为 ELIGIBLE、端点不能为 PASS。

TWRR 不能自报：`machine_validation_contract.endpoint_status_rule`（由父行 rule ID/hash 绑定）以完整精度重算 `UNIT_NAV_RATIO`：`((end_unit_nav/start_unit_nav)^(365.2425/elapsed_calendar_days)-1)`，再以 `ROUND_HALF_EVEN` 保留 12 位小数；`CHAIN_LINKED_UNIT_NAV` 则只能使用有序、首尾分别绑定 s/e 单位化行、成员数和 chain hash 均相等的 `endpoint_unit_nav_chain_member` 集合。存在外部现金流时禁止 total-NAV ratio。该规则还以数值阈值 `0.05`、`>=` 比较和 `INVALID → INCOMPLETE → PASS/FAIL` 的优先序产生 `endpoint_status`；`annualized_net_twrr` 必须等于重算结果，不能用任意数字标成 PASS。

`replay_endpoint_population_audit` 将冻结期待计数与 DEVELOPMENT、PRIMARY_HOLDOUT、CROSSING 的实际计数逐项核对；`pass_count + fail_count + incomplete_count + invalid_count` 也必须精确等于实际候选数。`zero_candidate_status` 只有在实际/期待均为零时才可为 `ZERO_EXPECTED`，而 `PASS` 必须为 `NOT_ZERO`。计数为零、短缺、hash 不同、状态计数不平、候选未映射或多次映射，均不得为 `PASS`。

PRIMARY_HOLDOUT 还必须有一个 `integrity_status=PASS` 的后锁箱 start-state manifest 与谓词审计。hash 本身不能充当状态来源：`primary_holdout_start_state_component` 必须逐行引用单位化、仓位 lot/mark、现金流/P&L、残差或其他规范化状态表，记录 typed FK、行 hash、可用时间、后锁箱来源和行完整性。`OPEN_ORDER_TRANSITION_ROW` 还必须有 execution/settlement domain 和精确 transition sequence；`ROLL_DELIVERY_EXPIRY_PARAMETER_ROW` 必须引用 `frozen_roll_delivery_expiry_parameter_state` 的单一 typed 行。manifest 的组件行数/集合 hash 必须与这些成员精确一致。任何开发期状态 carry、前锁箱来源、仅有未引用 hash、组件行缺失/不一致或无类型 transition/parameter FK 都会使端点成为 `CROSSING` 或 `INVALID`。

`prospective_state_configuration_coverage_audit` 必须覆盖冻结期望的每个 class、route/term set、scope、cash/collateral role、交易类型、事件、执行模型/可交易路径、执行/结算状态、部分成交余量和末日处置。只有带证据且审核 `PASS` 的 `OBSERVED`、`ACCEPTED_CONSERVATIVE` 或 `SOURCE_PROVEN_NOT_APPLICABLE` 可满足必需行；`UNRESOLVED`、`FAILED`、遗漏 tuple 或非 PASS 审核均阻断可用性。

JSON 中的 `machine_validation_contract` 提供运行表清单、冻结复合 FK、typed freeze crosswalk、a/s/e 时间约定、candidate-roster generator、端点 status/TWRR 公式、容量与预留 pool snapshot、`fx_conversion_contract`、`master_calendar_daily_valuation_coverage_contract`、`unitization_method_contract`、`position_mark_valuation_contract`、`event_balance_routing_and_nav_bridge_contract`、`paired_transfer_conservation_contract`、`unsettled_settlement_payable_receivable_contract`、事件映射、fill-event calculated-obligation conservation、预期对账矩阵、两套状态矩阵、可执行对账方程、重复 JSON key 拒绝、准入规则和 `hash_serialization_contract`。哈希一律以 UTF-8、字典键按字典序、标量规范化、显式 null、数组按主键/已命名 natural key 排序后计算。`replay_run_freeze_record_sha256` 对该冻结行全部已声明字段（**排除自身**）做 SHA-256；它与子行的绑定值相同。每一个行、组件、成员、manifest、计算、事件、fill、候选、总体或集合 `*_sha256` 也必须明确其组成字段/成员、采用相同的规范排序并排除自身字段；绝不要求独立 hash 与冻结 hash 相等。任何主键、必填字段、条件非空、外键、hash、状态迁移、容量、预留、FX、事件路由/NAV bridge、单位化、日历覆盖、残差、端点总体或前瞻覆盖失败时，端点只能为 `INCOMPLETE`/`INVALID`；本模板始终保持 `q=0`。
