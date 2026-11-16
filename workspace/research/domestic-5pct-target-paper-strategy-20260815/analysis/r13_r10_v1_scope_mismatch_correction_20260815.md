# R13 R10 v1 审计范围错配更正记录

- 结果：`PASS_SCOPE_MISMATCH_DOCUMENTED`。
- R10 的历史断言针对 C20 v1：四个现行规则引用应为 URL-only。C20 v2 正是通过留存这些规则正文修复该缺口。
- 因而，遗留 R10 在 C20 v2 上的 `FAIL` 仅来自已失效的 URL-only 断言，不可被解释为 C20 v2 的来源控制倒退。该原始重跑输出被保留以便审计追溯。
- 本记录不重建或冒充 v1 的独立审计；R12 单独核验 v2 的规则正文留存。两者都不构成策略测试、选品、资格判断或外部动作。

| 检查 | 结果 | 说明 |
|---|---|---|
| legacy R10 re-execution retained unchanged | PASS | 3d3d7b897981269d96b64bf447911a07e32e9c65f9be43734433db6fb4026f8c |
| legacy R10 identifies the then-current C20 v2 input | PASS | 81d6c9fae8cc7f8c6069f0e84e2a5b3a2c6ae6dcf1068bd31dc85d682b9d5fad |
| legacy R10 failure is exclusively the obsolete URL-only assertion | PASS | ['R10-S03: C20 transparently labels all current-rule rechecks as URL-only'] |
| legacy R10 retained-source and no-action checks still passed | PASS | inherited-source/scope status |
| C20 remains the remediated v2 artifact | PASS | D5PT-C20-FEASIBILITY-v2 |
| C20 records the R10-SC-01 remediation rationale | PASS | {'reason': 'R10-SC-01 found that the four current-rule rechecks in v1 were URL-only. v2 retains the four public pages and two linked rule bodies in a separate immutable source batch and binds its manifest. The legacy R10 v1 checker was later re-executed against v2; R13 preserves and corrects that scope mismatch rather than treating its obsolete URL-only assertion as a new defect. This changes no route, product selection, universe, return test, result, eligibility inference or action boundary.', 'previous_feasibility_sha256': '21f4ce8c90c68ed1acca106ea7261e109dd184736a2f7b4a8f19a81eec649f4a', 'reassessment_required': True} |
| C20 v2 deliberately uses retained rather than URL-only rule states | PASS | ['retained_in_c20_current_rule_source_batch', 'retained_in_c20_current_rule_source_batch', 'retained_in_c20_current_rule_source_batch', 'retained_in_c20_current_rule_source_batch'] |
| current-rule source batch remains immutable | PASS | f0e710ef25872489d4ee697c58fb0bf73abd8c180f0d4115ce10aaf69e278829 |
| C20 v2 retains no-selection/no-test/no-action controls | PASS | scope/disposition fields |

## 边界

这是一条审计来源沿革更正：它只说明为什么不能把遗留 R10 的机械失败当作当前缺口。C20 仍缺逐时点总体、可审计总回报、成本、执行和资格材料，因此仍未测试、未准入且无动作。
