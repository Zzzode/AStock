# R11 C19 公司债历史数据来源可行性独立审计

## 审计结论

- 结果：`PASS`。
- 本审计独立重算 C19 清单及六份原始文件的 SHA-256；未导入或调用 C19 采集/核验器。
- PASS 只证明保留的公开来源批次、C19 来源控制和受限研究边界保持一致。它不证明已取得数据许可、字段字典、历史样本、完整覆盖或任何个人交易资格。
- 观察到的 C19 状态：`CONDITIONAL_LAWFUL_SOURCE_PATHS_IDENTIFIED`；路线状态：`not_testable`。
- 不选择债券、不计算表现、不推断权限，也不产生外部动作。

## 清单与六份原始文件

- 清单：`workspace/research/domestic-5pct-target-paper-strategy-20260815/sources/c19-official-bond-data-source-feasibility-20260815/manifest.json`。
- 冻结 SHA-256：`77e337a09c80906a143b15dcfc72f60631847a3f44d63aeea5a9e0a531ac9d41`；实际：`77e337a09c80906a143b15dcfc72f60631847a3f44d63aeea5a9e0a531ac9d41`；匹配：`True`。
- 记录数：`6`；来源键集合匹配：`True`；磁盘原始文件集合精确匹配：`True`。

| source_key | 原始文件完整性 | 内容存在性 |
|---|---:|---:|
| `chinabond_valuation_query_surface` | `PASS` | `PASS` |
| `chinabond_yield_methodology_surface` | `PASS` | `PASS` |
| `sseinfo_authorization_statement` | `PASS` | `PASS` |
| `sseinfo_fixed_income_market_data_product` | `PASS` | `PASS` |
| `sseinfo_historical_data_interface_specification` | `PASS` | `PASS` |
| `sseinfo_historical_market_data_product` | `PASS` | `PASS` |

内容检查仅确认所保留文件的 HTML/PDF 结构及其可识别主题术语；它不把公开产品页、接口说明或授权声明升级为数据许可、历史交付或可回测数据集。

## C19 来源控制和研究边界

- C19 文件：`workspace/research/domestic-5pct-target-paper-strategy-20260815/analysis/c19_bond_historical_data_source_feasibility_20260815.json`。冻结 SHA-256 匹配：`True`。
- 清单绑定：`True`；留存范围：`True`；六条来源/权利边界结构：`True`。
- 每个已留存 URL 在 C19 中有引用：`True`；所需字段均仍为 `not_captured`：`True`；验收测试完整：`True`。
- 来源控制资格说明：C19 另列的两条 Wind T2 商业供应商 URL 不属于六份已冻结的一手批次；它们仍明确为 `candidate_only`，未被用作许可、历史交付或可测试性证明。该未留存 T2 路径是后续尽调限制，不影响本批次完整性或 `not_testable` 结论。
- 行动边界：`True`；条件数据路径：`True`；`not_testable` 边界：`True`；禁止项：`True`。
- Markdown 同步：`True`；已留存 URL 引用完整：`True`。

## 限定解释

R11 没有获取受保护端点、许可数据或账户信息，也没有计算债券回报。它只确认 C19 仍是一个有条件的数据获取尽调路径；在书面权利、字段字典、样本和逐时点覆盖均得到独立验证前，C18 继续保持 `not_testable`、无债券选择、无行动。
