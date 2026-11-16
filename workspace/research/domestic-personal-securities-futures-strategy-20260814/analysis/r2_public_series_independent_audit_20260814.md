# R2 公开序列独立复审 — 2026-08-14

## 最终结论

- R2 研究性数值筛查的本轮会计、时点、年度衔接与来源完整性复审：**PASS（仅限研究性公开价格算术筛查）**。
- 上一轮的 R2-S-001、R2-A-001、R2-A-002、R2-A-003 及两个 B 级表述/面板问题均已在当前文件中复核为关闭；本审计范围内没有尚需修复的算术或密封来源控制缺陷。
- 正式策略资格仍为：**FAIL / 不具备**。当前结论绝不表示策略、产品、资产池、配置、持有或交易可用；仍须保持 q=0。

这里的 cash / 现金腿仅是自融资单位账本中的会计现金头寸和权重，用于核对买卖后净值是否守恒；它不表示面向用户的收入、分配或资金管理安排。

本次 PASS 只回答一个窄问题：在已冻结的两套公开市场价观察上，R2 输出是否按其披露的月度单位加现金会计规则、成本敏感性和来源控制生成。它不改变公开历史价并非 PIT、非总回报、非执行账本且覆盖受限的事实。

## 复审范围和方法

复审了当前版本的以下工件：

- analysis/r2_public_series_extended_probe_20260814.{md,json}
- tools/run_r2_extended_public_series_probe.py
- sources/probe-public-etf-extended-r2-20260814/ 的原始观察、manifest 和依赖记录
- analysis/r2_official_sse_etf_public_price_probe_20260814.{md,json}
- tools/run_r2_official_sse_etf_price_probe.py
- sources/probe-official-sse-etf-price-r2-20260814/ 的四个 SSE JSONP 原始响应、manifest 和依赖记录
- data/source_registry.json 中 P02 与 P03 的 sealed_manifest 记录

复审不评估数据授权、历史 available_at、复权、分派、NAV/IOPV、交易状态、费用税费、盘口、成交、容量、结算、产品准入、适当性、配置或订单。

## 五项修复核验

| 核验项 | 结论 | 独立证据 |
|---|---|---|
| 月度信号与下一观测日开盘执行 | PASS | 对两套原始 open/close 面板逐项重建 H01–H07 的首个自然月观测日信号、此前一观测日收盘价截止点、下一观测日开盘执行日、入选袖套与目标权重；每条月度决策账本一致。 |
| 单位、会计现金与自然漂移 | PASS | H01/20 bps 保留 2,903 条逐日 state；其余路径保留完整月度调仓账本。独立重演确认调仓之间 units 和 cash 不变、证券价值随价格自然漂移；逐日 close NAV 等于 cash 加全部证券市值。 |
| 漂移后证券加现金的单向换手 | PASS | 对 public 与 SSE 各 7 个假设、4 档成本，共 56 条路径独立重算。每次换手均为 0.5 × [证券漂移前权重与目标权重的绝对差之和 + 现金权重绝对差]；所有首笔换手均为 1.0。 |
| 自融资与年度衔接 | PASS | 每次调仓均核对 pre-trade open NAV − cost = post-trade open NAV；两套输出所有路径的最大绝对自融资误差不超过 4.44e-16。完整自然年使用上一观测日 NAV 承接；起始/截止年度明确标为不完整，且均未进入年度门槛。 |
| 密封来源、verify-only 与 SSE 独立性边界 | PASS | P02/P03 raw、冻结记录、依赖与 source_registry sealed manifest SHA 均匹配；两个 verify-only 实测通过且 case 工件哈希前后一致。SSE 明确复用 P02 的会计函数，仅做来源路径交叉，未被表述为独立模型验证。 |

H01–H07 的月度事件数依次为 144、144、144、147、138、144、144；每个假设均已在 0、10、20、50 bps 四档成本下重演。为控制体积，逐日 state 只保留在 H01 的 20 bps cost_sensitivity 条目中；同一条目的 primary_20bps 是去除逐日 state 的摘要。该保留策略已核对，未改变任何月度账本、净值、换手、成本或年度行。

## 密封来源与只读模式

| 来源 | manifest SHA-256 | 冻结原始文件 | 依赖 | 结论 |
|---|---|---:|---|---|
| P02 公共聚合观察 | c19651550f49052e6b16e8fbb527f29928f22e09c50f712e4a03960cd1c251cf | 1 | 先前公共观察，仅 descriptive_overlap_only，SHA 已核验 | PASS |
| P03 SSE 公开观察 | 53e181497040c4888eda1091800df4f536c34ebf61cff9795bda0f39921d8e8a | 4 | P02 原始观察，仅 descriptive_cross_source_overlap_only，SHA 已核验 | PASS |

P02 原始观察 SHA-256 为 c08eeb5f45417d96e5fa8dc19b9d6fb559382a7f4dc5cace84faca36a4c3aabd。P03 四个 SSE 原始响应的 SHA-256 分别为：

- 510300：1e69b85008c1e9159c4042dcf9ac5f838a4aeb35076a8fe80cd9b368e474a79b
- 510880：a9fd44e5cbac886d40b9964c0daecb12a11410a44dd6c85ae5b9b8d119e4edfa
- 511010：05cb174414a62f259a08b34d09c3f55c0ea0433b26ed05b5a258a0e597e6e32d
- 518880：564fe8b85756a8f7e4f8b233cd4bb62c8bd2541c3f0bf24979813885bb56f585

两个 manifest 均记录为 explicit_post_capture_migration，因此它们是 case-local 篡改检测控制，而不是原始抓取时点的外部公证、数据权利或 PIT 证明。该边界已披露，且 R2 没有以此准入策略。

实测时以 PYTHONDONTWRITEBYTECODE=1 运行两个 verify-only 模式；每个脚本均成功验证 raw、冻结记录、manifest dependencies 以及 source_registry 的 sealed_manifest_sha256。运行前后，相关 manifest、派生 JSON/Markdown 与 source_registry 的 SHA-256 完全一致。当前输出 JSON 哈希为：

- public：7da423204daae0a3a33242cab5895241526f02ed33026ca2ebe5c553bcf63cb5
- SSE：4db6e56aea46c78b6529e1ca8d78460741cc3d2d1466db97e3c0855742e15c7e

代码静态复核也确认：两个 refresh-derived 分支先调用 sealed-source 验证，之后只写派生输出，不写 source manifest；public 见第 1012–1017 行，SSE 见第 675–680 行。未运行 refresh-derived，以避免在本次只改审计文件的任务中改写派生工件。

## SSE 的正确定位

SSE 脚本在第 27、448、451 与 456 行导入并复用 public screen 的市场面板、月度调仓和自融资评价函数。SSE 结果因此不能作为会计模型的独立复核；它只用不同的公开发布路径重做同一规则的价格路径观察。当前 Markdown、JSON 与代码均明确该限制，故不构成误导性独立性声明。

## 已关闭问题

| 原问题 | 关闭状态 | 复核依据 |
|---|---|---|
| R2-S-001：月度规则与自融资/换手不一致 | verified_closed | 当前单位加现金模拟、漂移权重换手、交易成本、每日状态和 56 条路径独立重演均一致。 |
| R2-A-001：年度子期间漏掉跨年首段收益 | verified_closed | annual rows 使用上一观测日 NAV；首尾不完整年明确标记并排除年度门槛。 |
| R2-A-002：来源冻结和 verify-only 可被重写 | verified_closed | 原始文件、冻结记录、依赖、P02/P03 registry seal 均被强制验证；verify-only 实测无 case 工件写入；refresh-derived 分支不写 manifest。 |
| R2-A-003：重叠输入未列入 manifest | verified_closed | P02 与 P03 manifest 都有带 SHA、角色、质量与局限的 dependencies 记录，且运行时校验。 |
| R2-B-001：探索性与预热期表述不精确 | verified_closed | 协议已表明 retrospective / exploratory / not independently pre-registered，并明确完整 lookback 后等到下一个月度边界。 |
| R2-B-002：公共面板缺少呈现状态 | verified_closed | 两份输出均保存全日期、逐资产 present/unknown 状态和 common_valid_observation_session。 |

## 仍然不能作出的推断

- 两套公开市场价观察均不能变成投资者总回报、正式历史回放或可执行策略表现。
- 公开来源的密封哈希不证明历史可得时间、版本链、复权、基金事件、价格可交易性、成本、容量或成交。
- 四只 ETF 只是覆盖受限的比较袖套，不是开放 U0、未来决策资产池、产品清单或配置建议。
- SSE 与公共聚合来源的数值接近不能独立验证模型，也不能验证价格口径。
- 当前“无算术幸存者”只是在该受限研究筛查中的观察，不能外推为开放资产池的失败或任何收益结论。

## 状态要求

维持 q=0、not_usable 和无行动状态。本轮可引用的结论仅为“R2 公开价格研究筛查的已披露会计与来源控制已通过复审”；不得将其改写为投资策略已通过、收益达标、现金目标已实现、产品可买、可以配置或可以交易。
