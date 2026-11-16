# R1 开放资产池覆盖缺口矩阵 — 2026-08-14

## 结论与使用边界

本矩阵覆盖 `DPSFS-U0-v2` 登记的全部十个国内资产类别。它回答的是
“现有案例对每一类到底研究到了什么、还缺什么”，而不是把最容易取得资料
的 ETF、AU/CU/TA 探针变成默认策略资产池。

- 当前十类资产均为 `q=0`；没有已准入类别、产品、发行人、合约、权重、
  持有或操作。
- “无针对性本地证据”只表示本案例尚未归档该类的可用证据，并非该类在经济上
  被否定或排除。
- 下文“下一来源类别/归档路径”均为**未来取得材料后的预留位置**，不表示该
  来源已取得、具有数据权利、可个人交易，或可关闭任何未决要求。
- 未来原始数据一律须遵循 DAC 的规范目录：
  `sources/entitled-data/<provider>/<package_id>/<retrieval-date>/`；并保留
  `as_of`、`available_at`、来源发布时间、提取时间、修订、原始哈希与书面
  权利记录。现有的网页、接口说明、回溯样本或公开日线不能替代该路径。

现有证据编号及其严格边界见 `data/source_registry.json` 与
`data/claim_audit.json`；U0 的类别、最低字段和门槛见
`data/u0_domestic_universe_registry_20260814.json`。`C07` 已明确：现有材料
不支持可用策略、配置、持有清单或收益预期。

## 矩阵一：已覆盖事实与结构/经济/历史缺口

| U0 类别（当前状态） | 现有本地证据 ID | 现有材料严格支持什么 | 仍缺的结构与经济研究 | 仍缺的历史数据、事件与人口研究 |
|---|---|---|---|---|
| `DIRECT_A_SHARE_EQUITIES`（未研究） | 无针对性外部证据；仅 `DPSFS-U0-v2`、`SX08` 记录其人口缺口 | 仅证明直接 A 股仍在开放研究范围，不能据此命名发行人、行业或因子暴露 | 全市场证券身份、上市/退市/更名、ST 与停复牌状态；在冻结 U0 和按规则进入 T2 后，才可对逐一发行人补齐业务模式、行业链、财务/治理、资本结构与估值资料 | 时点化上市/退市/ST/停牌/涨跌停总体；OHLCV、自由流通量、分红/配股/拆并/并购/退市事件；每份披露的发布时间、修订与原始哈希 |
| `PUBLIC_REITS`（未研究） | 无针对性外部证据；仅 `DPSFS-U0-v2`、`SX08` 的治理性缺口记录 | 仅证明公募 REITs 未被排除，未证明任一基金、底层资产或分派经济性 | 基金份额/生命周期和管理人/原始权益人结构；底层资产类型、租约/收费、出租率/通行量、现金流、扩募、融资与关联方资料 | 完整产品总体及状态；价格、NAV、折溢价、分派和公司行动账本；底层运营指标与披露的可得时间、修订链 |
| `LISTED_EQUITY_ETFS`（证据待补） | `E03`、`E04`；通用机制 `E06`、服务说明 `E08`；`P01`（不可采纳的四 ETF 公开日线诊断） | 两只示例 ETF 的复制结构及披露费用；类别层面股票 ETF 的 T+1/手数机制；`P01` 只能证明公开序列口径未解，不能证明总回报或执行 | 全类别产品主表；指数方法、历史成分/调仓、基金看穿暴露、重叠与集中度；分红、证券出借及基金分配在总回报中的一次性记账 | PIT 产品主表；逐日价量、NAV/累计或复权 NAV、IOPV、现金事件、停牌/涨跌停/交易状态；历史成分、调仓和公告时间的对账 |
| `BOND_AND_MONEY_MARKET_ETFS`（证据待补） | `E01`、`E02`；`E06`–`E08`；`P01`（仅含 511010 的不可采纳诊断）；`M01`（仅国债曲线市场背景） | 两只示例基金的结构/披露费用，通用债券 ETF 机制；`M01` 只说明一次曲线观察，不能替代基金净回报、现金等价或防御性结论 | 指数/持仓、久期、凸性、收益/应计、信用与交易对手暴露；货币基金的收益入账、到期、回购/交易对手机制；申赎与基金分配的经济影响 | PIT 持仓/久期与事件记录；价格、NAV、IOPV、分配、申赎、状态及公告时间；各历史时点的信用/利率暴露和压力状态 |
| `GOLD_AND_OTHER_COMMODITY_ETFS`（证据待补） | `E05`；`E06`、`E08`；`P01`（仅含 518880 的不可采纳诊断） | 一只示例黄金 ETF 的底层暴露描述与披露费用；通用 ETF 机制；并不证明对冲、分散、低波动或成交质量 | 全类别产品主表；底层金/商品敞口、托管、估值、申赎/限制和费用传导；不得以“商品”标签推定经济角色 | PIT 底层敞口、NAV/IOPV、市场价、折溢价、价量、停牌/节假日错配及现金事件；与底层市场的可得时间和修订对账 |
| `EXCHANGE_LISTED_BONDS_AND_CONVERTIBLES`（未研究） | 无针对性外部证据；`M01` 不纳入本类证据，因为它不是单券、可转债或交易路径资料 | 仅证明该类保持开放；未支持任一场所、单券、可转债条款或可达性 | 全类身份、期限、票息、赎回/回售、转股、稀释、契约与信用事件；发行人现金流、融资与违约/重组研究 | PIT 单券总体及生命周期；净价/全价、应计、报价/深度、停牌/限价、票息/赎回/转股/信用事件及修订谱系 |
| `COMMODITY_FUTURES`（证据待补） | `F01`–`F06`、`D01`、`PX01`–`PX03` | `F05`/`F06` 证明两所各六个**回溯取得**日期存在实际合约 EOD 行；`F02` 说明字段概念；`F01`–`F04` 是适当性/信息权与服务边界；失败探针不提供合约事实 | 全商品品种与实际合约总体；每个有效日的合约规格、规则版本、保证金、费率、涨跌停、持仓和交割条款；各品种的供需、期限结构和合约经济须在通过人口/数据门槛后分别研究 | 每日完整实际合约横截面与生命周期；结算、量额、持仓、市场状态、有效规则/条款；原始 `available_at`、分页/预期计数和版本对账；不得用连续或事后主力序列代替 |
| `FINANCIAL_FUTURES`（未研究） | 无金融期货专属本地证据；`F01` 仅为一般期货适当性边界，`D01` 仅为候选数据字段文档 | 仅证明不能假定个人适当性或数据权限；没有中金所产品、合约、结算或历史资料进入案例 | 产品/实际合约主表；合约乘数、到期/交割/最终结算、保证金/限额/费率；标的、基差、展期与抵押品经济；不能用商品期货资料外推 | 完整 PIT 实际合约横截面、生命周期、结算、流动性/状态、有效规则和条款；原始可得时间/修订与书面权利 |
| `LISTED_OPTIONS`（未研究） | 无期权专属本地证据；`F01` 不能替代期权规则、链条或个人适当性事实 | 仅证明期权没有被静默排除，未证明任一标的、系列、行权或收益结构 | 逐标的完整链条、到期/行权价/调整、合约与交割规则；行权/指派、保证金、标的同步与收益/损失记账；任何期权策略的经济理由均尚未建立 | 包含到期合约的 PIT 期权链、报价/价差/深度、持仓、公司行动调整、行权/指派/结算事件、交易状态和可得时间 |
| `LEVERAGED_AND_INVERSE_LISTED_PRODUCTS`（未研究） | 无针对性外部证据 | 仅证明杠杆/反向结构尚未被研究；没有产品总体或条款能支持暴露判断 | 全类产品身份、杠杆/反向与重置条款、估值机制、公司行动、融资/衍生品敞口；必须建立独立经济与风险记账模块 | PIT 产品/生命周期、价格/NAV/事件、日度重置、停牌/限制、流动性和修订谱系；不可将名称或历史分配当作结构证明 |

## 矩阵二：执行、资格、风险与下一来源路径

| U0 类别 | 尚缺执行与资格事实 | 尚缺风险研究 | 下一来源类别与规范归档路径 | 当前决策 |
|---|---|---|---|---|
| `DIRECT_A_SHARE_EQUITIES` | 日期化券商路由、T+1、税费、手数、涨跌停/停牌、报价/深度、无成交与可卖份额证据；不得推定账户或资格 | 市场、行业、财务/治理、集中度、流动性、停牌/退市和极端状态的可验证压力记录 | 先以 `RQP-U0` 取得交易所一级人口与历史状态；随后为已通过 U0→T2 的类别在新 DAC 版本定义股票专属数据包，原始材料仅可置于 `sources/entitled-data/<provider>/<new-equity-package-id>/<retrieval-date>/`，执行材料置于 `sources/entitled-data/<provider>/EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；不得命名股票、筛选、配置或操作 |
| `PUBLIC_REITS` | 场所/账户路由、税费、交易/结算、报价/深度、停牌和无成交证据；不假设个人可交易 | 底层资产经营下滑、分派、融资/再融资、估值、流动性、管理人/原始权益人和扩募风险 | 先走 `RQP-U0` 的官方产品/披露人口；再在新 DAC 版本定义 REIT 专属 PIT/事件包，归档为 `sources/entitled-data/<provider>/<new-reit-package-id>/<retrieval-date>/`；路由/成本走 `.../EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；无基金、无权重、无操作 |
| `LISTED_EQUITY_ETFS` | 产品/会话级 T+1、手数、税费、路由、报价时间、价差/深度、停牌/涨跌停和保守无成交证据 | 指数/成分变化、因子与行业集中、重叠、折溢价、跟踪偏离、流动性和跨资产压力 | `RQP-U0` + `RQP-UR01` 的 ETF 主表/事件账本：`sources/entitled-data/<provider>/ETF_PIT_EVENT_LEDGER/<retrieval-date>/`；`RQP-UR03` 的执行账本：`sources/entitled-data/<provider>/EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；示例 510300/510880 不是准入名单 |
| `BOND_AND_MONEY_MARKET_ETFS` | 会话级交易/结算、路由、税费、报价/深度、申赎状态和无成交证据；通用 T+0/T+1 描述不足以确定单品种机制 | 利率/久期、信用/交易对手、应计/估值、折溢价、流动性、赎回和压力情景；不得称为现金等价 | 与 ETF 相同的 `RQP-U0`、`RQP-UR01` 和 `RQP-UR03` 路径：`sources/entitled-data/<provider>/ETF_PIT_EVENT_LEDGER/<retrieval-date>/` 与 `sources/entitled-data/<provider>/EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；511990/511010 均无准入或结算角色 |
| `GOLD_AND_OTHER_COMMODITY_ETFS` | 产品/会话级路由、税费、手数、报价/深度、暂停与节假日错配、无成交证据 | 底层价格/托管/估值、折溢价、流动性、节假日错配及与其他资产的联合压力；不得预设分散效果 | `RQP-U0` + `RQP-UR01`：`sources/entitled-data/<provider>/ETF_PIT_EVENT_LEDGER/<retrieval-date>/`；执行证据：`sources/entitled-data/<provider>/EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；518880 只是研究探针 |
| `EXCHANGE_LISTED_BONDS_AND_CONVERTIBLES` | 场所与个人路由是否可达、日期化税费/结算、报价/深度、停牌/限价、无成交和资格边界 | 信用、利率、流动性、转股/赎回/回售、契约、发行人与重组风险的事件压力记录 | 先用 `RQP-U0` 建立场所总体；由于当前 DAC 未定义本类数据包，须先经新 DAC 版本批准 `new-bond-convertible-package-id`，再归档至 `sources/entitled-data/<provider>/<new-bond-convertible-package-id>/<retrieval-date>/`；执行材料须进 `.../EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；无单券、可转债、配置或操作 |
| `COMMODITY_FUTURES` | 券商/交易所的日期化费率、保证金、路由、适当性边界、报价/深度/冲击或保守无成交、限价锁定、交割与结算证据；不假定个人资格 | 交割、展期、基差、保证金追缴、限价锁定、流动性、合约集中和跨品种压力 | `RQP-U0` + `RQP-UR02`：`sources/entitled-data/<provider>/FUTURES_ACTUAL_CONTRACT_LEDGER/<retrieval-date>/`；`RQP-UR03`：`sources/entitled-data/<provider>/EXECUTION_AND_COST_LEDGER/<retrieval-date>/`；有效规则/条款必须与实际合约/会话一同归档 | `q=0`；AU/CU/TA 无已选合约、风险预算或操作 |
| `FINANCIAL_FUTURES` | 交易所/券商的路线、适当性、保证金、费率、限额、报价/深度、交割/最终结算和无成交证据；不能把 CFFEX 历史数据服务线索当成授权 | 基差、展期、保证金/流动性、限价、结算、标的相关性和压力风险 | 先以 `RQP-U0` 建立人口；当前 `FUTURES_ACTUAL_CONTRACT_LEDGER` 的范围只覆盖 AU/CU/TA，金融期货须在新 DAC 版本新建或经独立扩展批准后使用 `sources/entitled-data/<provider>/<new-financial-futures-package-id>/<retrieval-date>/`，执行仍须有 `.../EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；无金融期货比较、合约或操作 |
| `LISTED_OPTIONS` | 期权场所/券商路线、适当性、保证金、费率、报价/深度、行权/指派/结算与无成交证据 | 收益非线性、行权/指派、跳空、流动性、到期和公司行动调整的完整压力与账务影响 | 先以 `RQP-U0` 建立期权人口；当前 DAC 和请求包没有期权链专属包，须先定义并获准 `new-options-chain-package-id`，再归档至 `sources/entitled-data/<provider>/<new-options-chain-package-id>/<retrieval-date>/`；执行资料须进 `.../EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；无期权系列、策略、权重或操作 |
| `LEVERAGED_AND_INVERSE_LISTED_PRODUCTS` | 产品/会话级路由、资格、税费、报价/深度、重置日、停牌/限额与无成交资料 | 路径依赖、日度重置、杠杆、融资/衍生品、折溢价、流动性及尾部风险；须独立核算，不能复用普通 ETF 结论 | 先以 `RQP-U0` 建立产品结构人口；当前不存在对应 DAC 包，须先以新 DAC 版本定义 `new-leveraged-inverse-package-id` 和独立风险模块，原始材料仅可归档至 `sources/entitled-data/<provider>/<new-leveraged-inverse-package-id>/<retrieval-date>/`，执行资料另入 `.../EXECUTION_AND_COST_LEDGER/<retrieval-date>/` | `q=0`；无产品、无策略映射、无操作 |

## 不能跳过的闭环顺序

1. **人口先于点名。** 对所有十类执行 `RQP-U0`：冻结来源、查询、覆盖计数、
   历史终止状态与 U0→T2 推导审计。未有接受的数据/回放模块的类别不能借由
   方便的产品样本进入 T2。
2. **数据与权利先于结果。** ETF 三类只能在 `ETF_PIT_EVENT_LEDGER` 通过后研究
   总回报；当前商品期货只能在 `FUTURES_ACTUAL_CONTRACT_LEDGER` 通过后研究
   实际合约。除 ETF 三类与当前商品期货范围外，其余六类没有已定义的专属原始数据包，需先修订 DAC，不能借用
   ETF、AU/CU/TA 或公开连续序列的结论。
3. **执行/资格与风险不可补写。** 所有进入纸面回放的类别都要有
   `EXECUTION_AND_COST_LEDGER`、日期化规则/费用/报价或保守无成交模型，以及
   独立的风险和前瞻纸面核对；这不假定任何个人的账户、适当性、税务或交易权限。
4. **结果盲冻结后才可比较。** 只有数据包验收、U0→T2、规则书、协议和数据字典
   均已冻结，才可运行单位化、成本感知的回放；之后仍须通过全端点、主留出期和
   独立审查。任何一项失败都使相关类别保持 `q=0`。

## 本矩阵与现有证据的关系

- ETF 细化缺口以 `analysis/etf_r1_product_diligence_20260814.md` 为准；本矩阵
  将其放回开放资产池，未把五只示例基金扩展为正式名单。
- 商品期货细化缺口以 `analysis/futures_r1_feasibility_20260814.md` 为准；本矩阵
  没有将 AU/CU/TA 的六日回溯样本扩展为全商品或金融期货的证据。
- 收益来源的经济地图见 `analysis/return_source_feasibility_20260814.md`；它不是
  配置、绩效预测或任何类别的豁免。
- 未决门槛仍由 `unresolved_requirements.json`（UR01--UR05）和
  `source_exhaustion_log.json`（SX01--SX10）控制。本文件不关闭任何门槛。
