# Artifact Contract

| Artifact | Required fields | Minimum depth | Blocking condition | Review / verifier |
|---|---|---|---|---|
| `data/source_registry.md/json` | id, URL, time, quality, tier, boundary | Primary platform or corporate project-link source; use boundary per material claim | 无原始资料的项目关系归因 | R0 / source-registry fields |
| `data/claim_audit.md/json` | claim, confidence, wording, restriction | 项目关系与题材联想分开 | 未核验主张进入行动结论 | R0 / claim-audit fields |
| `data/raw_market_data.md` | cutoff, sources, breadth, turnover, warnings | 同日收盘快照及执行限制 | 快照被当作可成交数据 | R0 / market-packet presence |
| `analysis/theme_gate_scorecard.md/json` | gate, field, pass test, cadence, failed action | 五项同时门槛；D+1/D+2收盘判定 | 主观豁免门槛 | R2 / scorecard complete |
| `analysis/tactical_preplan.md` | gates, scenarios, invalidation, time stop, access constraint | D+1--D+5状态；无创业板路径单列 | 未过门槛即升级纸面计划 | R2 / preplan invalidation |
| `analysis/daily_theme_evidence_packet_template.md` | as-of, members, prices, mapping source, catalyst source | 一收盘一数据包；缺字段即失败 | 混用日期或未映射数据 | R2 / packet template |
| `main.tex/main.pdf` | narrative, sources, conditions, risks, disclaimer | 关键事实旁标资料ID；条件化预案 | 无依据的交易指令 | R3 / build and visual review |
| `final_signoff.md/json` | downgrade, issues, residual risks, PDF path | 报告发布与纸面入场分离；S/A已关闭 | 在纸面入场阻断下给出入场许可 | R4 / signoff blockers |
