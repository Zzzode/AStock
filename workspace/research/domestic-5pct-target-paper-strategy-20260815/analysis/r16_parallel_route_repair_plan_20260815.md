# R16 平行路线独立复核修复计划

- 来源复核：`analysis/r16_parallel_route_independent_review_20260815.json`。
- 当前状态：`all_repairs_independently_verified_closed`。
- 独立复核记录：`analysis/r17_r16_repair_independent_recheck_20260815.json`。
- 边界：本计划只修复披露语言、来源记录一致性和来源树卫生；不改变 C37、C39、C40--C42 的准入状态，不计算结果、不选标的，也不授权外部动作。

| 问题 | 严重性 | 负责方 | 修复工件 | 修复动作 | 独立复核要求 | 当前状态 |
|---|---|---|---|---|---|---|
| R16-S-001 | S | `research-prose-polish` | `analysis/c40_600519_equity_diligence_20260815.md` | 将读者可见的实质英文正文、标题、表格与解释标签译为中文；不改事实、数字、来源、限定语、风险、G0--G9 状态或 `NO_ACTION` 边界。 | 独立复核重新扫描读者文字并确认事实保持。 | `verified_closed` |
| R16-A-001 | A | `equity-research` / 来源治理 | `analysis/c40_600519_equity_diligence_20260815.json`、`data/source_registry.json` | 明确区分“已留存且哈希核验的查询响应”与“尚未验证的时间语义、公告 PDF 内容和同日可用性”；JSON 变更后更新 S46 哈希。 | 独立复核同时核验 C40-S05、归档清单、字段表述和 S46 哈希。 | `verified_closed` |
| R16-B-001 | B | `equity-research` / 来源治理 | `sources/probe-sse-600519-announcement-query-20260815/manifest.json` | 为空暂存目录增加零捕获清单，说明其不是证据来源，真实反爬探针位于另一目录。 | 独立复核确认该批次仍为空、未被引用且不构成证据。 | `verified_closed` |

任何修复作者都不能自行将问题标记为 `verified` 或 `closed`。R17 由独立、只读的 maker-checker 复读变更工件并记录三项核验均通过；这只关闭 R16 的披露与来源树修复项，不改变 C37、C39、C40--C42 的非准入、`NO_ACTION` 或发布阻断状态。
