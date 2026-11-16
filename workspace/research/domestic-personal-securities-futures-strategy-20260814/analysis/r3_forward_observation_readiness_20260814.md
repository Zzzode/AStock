# R3：前瞻观察就绪度设计

- Artifact ID: `DPSFS-R3-FOR-v1`
- Case ID: `domestic-personal-securities-futures-strategy-20260814`
- 截止日：2026-08-14
- 状态：`not_ready_for_formal_forward_paper_observation`
- 研究边界：仅研究；`q=0`

## 核心结论

今天不能形成可行动的策略。UR01、UR02、UR03 的有权利、可审计、点时可得数据包尚未收集和独立验收；DPSFS-RP0-v10、数据合同、U0 至 T2 推导、规则簿和运行绑定记录也未构成可签署的正式冻结组合。因此，今天最多只能登记一个空白的前瞻接收与核对设计，不能声称已有正式回放、正式纸面观察、策略结果、适配性或推荐。

本设计严格区分两件事。前瞻接收观察是对未来到达资料的来源、时点、版本和覆盖度做追加式质量控制；它不运行规则，也不产生标的选择。正式纸面观察则只能在已验收资料、已签署冻结、正式回放及独立复算均完成后开始，并且仍只记录研究状态与证据覆盖。两者都不是推荐，均不改变 `q=0`。

前案 `income-target-5pct-return-3pct-cash-strategy-20260812` 仅作为冻结且不可继承的框架释放。其 PDF、验证结果、审阅结论、资料或冻结状态均不能替代本案的数据验收、规则冻结、正式回放或前瞻观察证据。

## 三种互斥模式

| 模式 | 允许内容 | 结果标签 | 不得提升为 |
|---|---|---|---|
| `MODE_0_DESIGN_ONLY` | 空白模板、字段映射、来源路径、预期日历、例外代码与冻结草案 | `design_only` | 资料验收、前瞻数据集、正式回放或纸面观察 |
| `MODE_1_FORWARD_INTAKE_QA` | 在未来取得书面权利后，对原始资料、点时可得性、版本和覆盖度做接收质量控制 | `intake_only_unaccepted` | 规则运行、历史回放或正式纸面观察 |
| `MODE_2_FORMAL_PAPER_OBSERVATION` | 仅在 UR01--UR04 验收、冻结后正式回放和独立复算均通过后，记录冻结日历内研究状态与覆盖证据 | `research_observation_only` | 自动推荐或 `q` 变更 |

MODE_1 允许未来资料的技术接收，但不允许将尚未验收的资料放入正式模型。MODE_2 是一个更晚的研究阶段，开始时间必须晚于签署冻结时间；任何较早资料只能继续保留为接收质量证据，不能回标。

## 冻结路径

第一层为 `FORWARD_INTAKE_BOUNDARY_FREEZE`。它冻结案例、`q=0`、观察模式、禁止输出、时区、变更责任人和独立审阅人。它可以在今天作为设计边界登记，但不产生正式运行。

第二层为 `FORWARD_INTAKE_PROTOCOL_FREEZE`，必须在第一笔未来资料到达前完成。它应冻结未来资料包和来源路径、书面权利引用、U0 快照或明确范围缺口、预期覆盖日历哈希、字段映射、`available_at` 定义、版本规则、原始清单架构、例外分类和接收频率。未经过此层冻结的资料可以保留为探针，但不能计入合格前瞻覆盖。

第三层为唯一的 `FORMAL_REPLAY_RUN_FREEZE`。只有在资料包、U0/T2 审计和规则材料已验收后，才可用 `replay_run_freeze_record` 绑定 `replay_run_id`、数据合同、U0 快照、推导审计、规则簿、正式协议、数据字典、输入清单、来源版本截止点、主日历、前瞻覆盖政策、风险控制、代码、运行环境和精确命令。文件路径、案例名称或事后报告哈希均不能替代行级绑定。

第四层为 `FORMAL_FORWARD_OBSERVATION_START_RECORD`。它只适用于 MODE_2，须在首个正式观察时点之前固定观察日历、预期配置元组、时长和观察数规则、例外升级政策、独立核对计划，以及“无外部指令”的声明。缺少该记录时，MODE_2 不得开始。

任何范围、字段、来源、规则、日历、容差或时间语义的实质变化都应产生新版本与新冻结；不得原地覆盖旧批次或让后续版本回写旧观察。

## 来源接收与点时字段

所有原始对象应只追加、不可原地覆盖。每个预期时点必须留下成功、无资料、延迟、休市、失败尝试或来源例外之一，禁止静默缺行。历史日期但在之后才取得、且不能证明原始可得时间的资料，必须标为 `retrospective`，不得作为点时证据。敏感访问资料不写入案例，只保留权利证明引用和保管责任记录。

每个原始对象的清单至少包含：

- `package_id`、`provider`、`provider_product`、`source_url_or_endpoint`、`request_parameters_or_query_hash`
- `request_started_at`、`response_received_at`、`as_of`、`available_at`、`vendor_publication_at`
- `source_revision`、`local_revision_sequence`、`content_type`、`bytes`、`sha256`
- `entitlement_evidence_ref`、`retrieval_operator`、`expected_page_or_row_count`、`actual_page_or_row_count`、`quality_status`

规范化的逐字段事实还必须绑定 `record_key`、`parent_class_id`、`instrument_or_contract_id`、字段名、原始数值或明确不可用状态、单位/币种、有效或会话时点、来源事件键、上述时间元组、原始对象哈希、清单哈希、规范化版本与代码版本、规范化行哈希、可得性测试状态、质量状态和例外引用。标识符只作为数据键，不代表准入或研究优先级。

未来资料至少要覆盖四类事实：人口与生命周期；上市基金的市场、NAV/明确不可用状态、事件和状态；实际挂牌期货合约的生命周期、逐日横截面、有效条款、保证金/限制、交割和会话状态；以及有效日期、范围和版本明确的可观测实施状态。连续或事后主力序列不能替代实际合约资料。

原始对象、规范化数据和审计资料分别应遵循数据合同约定的路径：`sources/entitled-data/<provider>/<package_id>/<retrieval-date>/`、`data/normalized/<package_id>/<contract-version>/` 和 `governance/data-audit/<package_id>/<contract-version>/`。每次规范化必须保留输入清单哈希、代码提交、运行环境锁定、架构版本、输出哈希、转换时间和服务/操作责任。

## 账与核对架构

`forward_observation_register` 记录观察批次的模式、范围、`q`、冻结引用、起止时间、状态和发布限制。`raw_receipt_ledger` 逐对象记录接收、清单、时间、版本、质量状态和替代关系。`expected_coverage_ledger` 将每个母类别、字段族、来源路径和预期会话与实际资料、无资料或失败尝试逐一关联。

`normalized_pit_fact_ledger` 保存逐字段点时事实与原始对象、版本、可得性测试及规范化谱系。`exception_and_revision_ledger` 保留迟到、缺失、冲突、重复、版本替换和不可用状态；任何此类问题不得通过删除或覆盖清除。`cross_source_reconciliation_ledger` 在具备独立来源时，按预冻结的键和容差记录差异、处理状态、证据集哈希和审阅人。

只有 MODE_2 可以使用 `formal_paper_observation_ledger` 和 `prospective_configuration_coverage_ledger`。前者记录已冻结输入集、评估状态、覆盖状态、例外和结果发布锁；不记录外部指令。后者按冻结的母类别、路径、条款集、可交易状态、执行状态、结算状态、剩余处置和运行结束处置记录证据覆盖。每个 MODE_2 行必须携带相同的 `replay_run_id` 与 `replay_run_freeze_record_sha256`。

## 必须逐项通过的核对

1. `RC01_RECEIPT_AND_MANIFEST`：每个对象的清单、字节数、SHA-256、版本、权利引用和预期/实际数量完整且唯一；失败即为 `INCOMPLETE` 或 `INVALID`。

2. `RC02_POINT_IN_TIME`：任何正式研究事实的 `available_at` 不晚于允许评估时点，且 `as_of`、发布、接收和版本时间顺序可审计；迟到资料只能标为 `retrospective` 或例外。

3. `RC03_EXPECTED_COVERAGE`：冻结日历、人口/类别、字段族和来源路径的预期与实际数量逐项匹配；不完整范围必须标为 `coverage_restricted`，不能以便利子集替代。

4. `RC04_REVISION_AND_IMMUTABILITY`：更正产生新对象与新版本链，规范化行可追溯至唯一原始哈希；版本链断裂或事后覆盖使受影响资料无效。

5. `RC05_CROSS_SOURCE`：可获得时按预冻结规则核对主、次来源；未解决冲突不得任意选择有利数值。

6. `RC06_FORMAL_BINDING`：MODE_2 的每个观察、覆盖和例外行均与唯一签署的运行冻结逐字节一致；缺失、失配或事后绑定均无效。

7. `RC07_PROSPECTIVE_CONFIGURATION_COVERAGE`：每个预期配置元组恰有一行，且只有 `OBSERVED`、`ACCEPTED_CONSERVATIVE` 或 `SOURCE_PROVEN_NOT_APPLICABLE` 并通过复核才可满足要求。`UNRESOLVED`、`FAILED`、缺失元组或非 `PASS` 状态均阻断完成。

8. `RC08_INDEPENDENT_RECONCILIATION`：独立审阅者从不可变来源副本重算清单、可得性、覆盖、版本、哈希和例外；任何未解释差异保持开放。

## 首批前瞻里程碑

| 里程碑 | 前提证据 | 唯一允许结论 | 不能证明 |
|---|---|---|---|
| `F0_DESIGN_REGISTERED` | 本设计、`q=0` 和禁止输出确认 | 前瞻观察设计已登记 | 资料包、前瞻数据集、正式回放、纸面观察或推荐 |
| `F1_RIGHTS_AND_INTAKE_PROTOCOL_FROZEN` | 未来书面权利、资料包定义、日历、字段映射、例外规则和第二层冻结 | 可开始 MODE_1 接收质量控制 | 数据包验收或正式输入 |
| `F2_FIRST_FORWARD_RECEIPT_VALIDATED` | 第一笔未来原始对象、清单、时间元组、哈希、版本和覆盖行 | 第一笔前瞻接收的技术谱系已核对 | 历史 PIT、完整覆盖、策略结果或正式纸面观察 |
| `F3_FORWARD_COVERAGE_QUALITY_REVIEW` | 预冻结期间内的完整预期行、失败尝试、版本链与独立核对 | 可评估接收质量，未验收行仍为 `intake_only_unaccepted` | UR01--UR03 关闭或正式运行资格 |
| `F4_FORMAL_INPUT_AND_RUN_FREEZE_ELIGIBILITY` | UR01--UR04 独立验收、U0/T2 推导、规则簿、协议、字典、输入清单和签署运行冻结 | 可按冻结程序进行正式回放与独立复算 | 前瞻纸面观察已经开始或推荐 |
| `F5_FORMAL_PAPER_OBSERVATION_BEGINS` | 正式回放与独立复算通过、第四层冻结、观察日历和预期配置元组 | 可开始 MODE_2 研究专用观察 | `q` 变化、适配性、收益结论或推荐 |
| `F6_PROSPECTIVE_RECONCILIATION_COMPLETE` | 每个代表母类别至少 60 个日历日、10 次不同合格观察，且 RC01--RC08 独立核对无未解决阻断行 | 前瞻纸面核对可提交独立审阅 | 自动策略可用性、准入或推荐；`q` 仍为 0，除非后续治理另作独立决定 |

## 结论与资料依据

本案今天没有可行动策略，且没有任何可以替代正式输入、正式冻结和独立核对的快捷路径。最严格且最小的前进方式是先冻结接收边界，未来取得权利后从 MODE_1 的原始资料接收开始，完整保留点时、版本、哈希、覆盖和例外；只有在资料验收、正式冻结、回放和独立复算之后，才可进入 MODE_2 的研究专用纸面观察。前瞻纸面观察与推荐是两种不同的产物，前者不输出任何外部指令，也不会自行改变 `q=0`。

本设计依据 `research_brief.md`、`unresolved_requirements.json`、`data/data_access_feasibility_20260814.json`、`data/data_acquisition_contract_20260814.json`、`data/formal_replay_protocol_requirements_20260814.json`、`data/replay_data_dictionary_template_20260814.json` 和 `analysis/r2_candidate_prioritization_and_next_test_20260814.json`。
