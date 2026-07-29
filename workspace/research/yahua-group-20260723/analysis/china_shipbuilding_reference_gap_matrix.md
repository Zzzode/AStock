# 中国船舶完整单票覆盖基准：雅化集团只读差距矩阵

**比较日期：** 2026-07-23  
**比较目的：** 以 `china-shipbuilding-600150-20260722` 已签发的 `single_stock_full_research` 合同、模型、估值与签发链为基准，界定雅化集团当前版本若要在正式 H1 后重建为完整单票覆盖，哪些工作可现在准备、哪些必须等正式 H1、哪些船舶行业字段不应照搬。  
**只读声明：** 本文件不修改 `main.tex`、`sections/`、现有雅化证据包、模型、门禁或签发文件；它不是对当前 19 页事件研究的降级判定。

## 先行结论

雅化当前版本满足的是 `earnings_preview_event_research`，而不是中船案例的 `single_stock_full_research`。其“无自有全年 EPS、目标价、上行空间或评级”是正式 H1 前的**正确边界**，不是可用模板补齐的缺页。中船能够签发完整单票研究，是因为其合并口径收入—交付/结构—毛利—归母—EPS 桥、三情景与估值锚已经建立，并在 51 页 PDF、R4 和双重门禁中闭环；雅化当前证据明确止于合并业绩预告和外部预测交叉。

因此，正确路径不是把船舶报告的估值表复制给雅化，而是：先完善可用的历史、市场和来源治理；正式 H1 发布后，以实际三表、分部/单位经济与现金转换建立新模型，再启动新的完整覆盖 R0--R4。正式 H1 是必要条件，不保证充分：若其中仍缺锂盐量—价—成本、民爆订单/回款或分部利润，完整覆盖仍须维持 `watchlist only / insufficient evidence`，不得以外部 EPS 代填。

## 分类定义

| 分类 | 含义 |
|---|---|
| **可立即补齐** | 仅使用现有 2025 年报、2026Q1、业绩预告、原始券商 PDF、已归档市场数据或可立即追加的公开资料即可完成；不得因此生成自有全年 EPS 或目标价。 |
| **只能在正式 H1 后补齐** | 正式 H1 报告是必要输入。即使 H1 已发，如分部、销量、ASP、成本、订单或现金转换仍未披露，该项仍不能假定完成。 |
| **行业不适用** | 中船案例的船舶专属定义、单位或监管/交付结构不能迁移；可采用其“驱动—确认—现金—估值信用”方法，但必须换成雅化的锂盐和民爆字段。 |

## 逐项对比

| ID | 中船完整覆盖基准与具体文件 | 雅化当前状态与具体文件 | 分类 | 只读结论与后续验收条件 |
|---|---|---|---|---|
| G01 报告身份与合同 | `china-shipbuilding-600150-20260722/research_brief.md` 定义 40--60 页完整单票覆盖；`gate_manifest.json` 要求 evidence/full-chain/broker/model/valuation/secondary-market/IC 七类深度门禁；`artifact_contract.json` 将增长模型、估值、签发设为阻断工件。 | `yahua-group-20260723/research_brief.md`、`gate_manifest.json` 和 `artifact_contract.json` 明确是 H1 前事件研究，完整估值字段为不适用，报告在正式 H1 时失效。 | 只能在正式 H1 后补齐 | 不应静默把 `report_type` 改成完整覆盖。H1 后须新建或实质重写完整覆盖合同：定义数据截止、估值父主体、七类深度门禁、降级路径和新的 R0--R4；未完成前当前版本仍仅是事件研究。 |
| G02 来源治理与缺口消费 | 中船 `artifact_contract.json` 对 `data/source_registry.*`、`data/claim_audit.*`、`source_exhaustion_log.*` 要求全部估值材料可追溯，且未解决缺口必须进入模型限制/敏感性；`analysis/coverage_gap_matrix.md` 由 R0--R1 消费。 | 雅化已有 `data/source_registry.*`、`data/claim_audit.*`、`source_exhaustion_log.*` 与 `analysis/coverage_gap_matrix.md`；G01--G05 已明确利用率、客户量价、自给率、H1 三表和券商目标缺口。 | 可立即补齐 | 可以立即把现有缺口逐项映射到未来模型的“允许方法、禁止方法、所需敏感性、责任人”。但这只是防止伪精度，不能把未披露项目变成预测输入。H1 后要为新增披露逐条更新来源和估值后果。 |
| G03 历史财务、分部与资产负债表底稿 | 中船 `artifact_contract.json` 要求经审计历史、季度/H1、分部、订单、现金流、债务、资本开支、客户预收和股本/口径勾稽；其 `analysis/growth_earnings_model.md` 以已验证基期进入模型。 | 雅化 `data/verified_financials.md` 已有 2023A--2025A、2026Q1 的收入、利润、现金流、资产负债、存货和 capex 代理；`analysis/company_fundamental_cards.md` 已列 2025 锂盐/民爆基数、负经营现金流和库存。正式 H1 目前没有收入、现金流、资产负债、存货或 capex。 | 可立即补齐 | 现在可补全年/季度的分部收入、毛利、债务、股本、少数股东、所得税和历史营运资本底稿，并与年报页码逐项勾稽。不得把 H1 预告利润代替 H1 三表；正式 H1 相关字段仍列为 `not disclosed`。 |
| G04 锂盐与民爆的收入—毛利—现金—EPS 桥 | 中船 `analysis/growth_earnings_model.md` 形成“交付/结构—收入确认—毛利—费用—归母—EPS”公式、Bear/Base/Bull、现金转换与可复算敏感性；`analysis/chain_earnings_bridge.md` 禁止把订单直接转收入。 | 雅化 `analysis/growth_earnings_model.md`、`analysis/segment_forecast_bridge.md`、`analysis/chain_earnings_bridge.md` 明确停止在 H1 预告：未披露锂盐销量、ASP、单位成本、分部利润、民爆订单/回款及 H1 现金转换；`data/growth_driver_model.json` 将 house EPS、情景、目标和评级列为不适用。 | 只能在正式 H1 后补齐 | 正式 H1 后必须至少建立“锂盐销量/产品结构 × 实现 ASP − 单位成本 + 民爆产品/爆破服务收入、毛利、费用、税费、少数股东 → 归母/EPS”桥，并以 OCF、应收、存货、合同/项目回款交叉验证。H1 若只给合并利润而不提供等效桥，仍不得生成 FY EPS。 |
| G05 价值链、客户和资源的估值信用 | 中船 `analysis/value_chain_economics.md`、`data/supply_chain_relationships.*`、`data/customer_chain_audit.*` 对价格、成本、产能、利用率、订单、客户、现金和估值使用逐行设限；缺口不允许换算为订单或 SOTP。 | 雅化 `analysis/value_chain_economics.md`、`data/customer_chain_audit.*`、`data/supply_chain_relationships.*` 已把锂盐实际利用率/成本/客户分配、资源自给率、民爆订单/回款列为未披露并给零或验证型信用。 | 可立即补齐 | 可立即加强每条客户、资源和项目关系的原始来源、主体边界、披露日期、允许用途与禁止用途；对未披露字段应保留零信用。具名客户收入、实际自供比例和项目订单不应凭“长期合作”补齐；只有公司/客户正式披露后才可升级为模型输入。 |
| G06 Street 与外部预期 | 中船 `data/broker_street_consensus_20260722.*` 和 `artifact_contract.json` 要求覆盖预测、评级、目标、方法、来源质量和估值权重；弱来源为零权重，Street 只作外部锚。 | 雅化 `data/broker_street_consensus_20260723.md` 已归档东吴、国信、开源三份完整原始 PDF；预测可交叉，但全部 `valuation_weight=0.0`，东吴 42 元仅为单一外部观点。 | 可立即补齐 | 可立即按完整覆盖合同补充报告日期、股本口径、预测修订、方法可比性和来源穷尽记录，并在正式 H1 后刷新覆盖。即使后续目标价不完整，完整覆盖也可用独立模型与零权重 Street 比较；不得将单一 42 元或外部 EPS 直接升级成雅化目标价。 |
| G07 二级市场结构与资金证据 | 中船 `data/market_structure_20260722.*`、`data/capital_positioning_20260722.*` 及合同要求前复权日 K、量额换手、两融、陆股通/基金频率边界、龙虎榜负查询和原始路径。 | 雅化 `analysis/secondary_market_analysis.md` 只使用 20 日价格、成交额和换手率，并明确没有指数/同业回报、座席、北向、两融或基金数据，因此不作资金流结论。 | 可立即补齐 | 可立即归档可复算的长周期复权日 K、指数/同业相对表现、两融、陆股通、基金持仓与龙虎榜查询，并严格标注日频/季频和不可得字段。该工作只完善交易位置与风险监控，不能替代 H1 基本面桥或提高目标价信用。 |
| G08 全年盈利情景、现价隐含与敏感性 | 中船 `analysis/growth_earnings_model.md` 与 `analysis/implied_growth_sensitivity.md` 以独立收入/毛利/现金假设形成 2026E--2028E Bear/Base/Bull、现价隐含经营要求和降级阈值。 | 雅化 `analysis/growth_earnings_model.md` 明确不设置自有三情景；`analysis/valuation_audit.md` 仅审计市场价格与外部 EPS 的机械 PE，并明确该算术不是估值。 | 只能在正式 H1 后补齐 | H1 后先完成 G04 的输入桥，才可建立 FY 及后续年度的熊/基/牛。每一情景须有销量/ASP/成本、民爆收入/毛利/回款、税费/少数股东和现金转换假设，现价隐含结果只作验证尺；禁止 H1×2 或以锂价、设计产能、客户名单替代驱动。 |
| G09 多锚估值、目标价与行动 | 中船 `analysis/valuation_model.md` 及 `data/current_valuation_model_20260722.json` 提供价格/股本/市值、预测、业务匹配主方法、交叉验证、三情景、公允区间、目标价、上/下行与行动；`analysis/valuation_audit.md` 要求 `Model Reproducibility: PASS`。 | 雅化 `analysis/valuation_model.md` 和 `analysis/valuation_audit.md` 正确将 target、upside、house EPS 写为 `null`，只保留 16.79 元与外部 EPS 的 6.38--8.35x 机械 PE。 | 只能在正式 H1 后补齐 | 只有 G04/G08 在正式 H1 后通过，并完成价格—股本—市值、预测、方法匹配、情景、内在/市场/Street 锚、权重、目标/区间、风险和失效条件的复算，才可发布目标价或行动。若量价成本桥未闭合，保持 `watchlist only / insufficient evidence`，而不是以现价、外部目标或零上行填字段。 |
| G10 预期差、行动与正式签发 | 中船 `analysis/house_view.md`、`analysis/variant_perception.md`、`analysis/risk_framework.md` 和 `final_signoff.md/json` 使独立观点、反方、失效条件、估值行动、51 页当前 PDF、39/39 案例验证和共享门禁一致。 | 雅化 `analysis/house_view.md`、`analysis/variant_perception.md`、`analysis/risk_framework.md` 的行动是事件观察；`final_signoff.md/json` 为 `PASS_EVENT_RESEARCH_ONLY`，19 页 PDF 在正式 H1 立即失效。 | 只能在正式 H1 后补齐 | 现在可预写“升级/等待/停止跟踪”所需字段与反方问题；正式 H1 后必须让独立观点、全年模型、估值、风险、R0--R4、当前 PDF 和签发同一版本一致，并重跑全部门禁。不能把事件研究的签发状态外推为完整覆盖 PASS。 |
| G11 成品结构、篇幅与渲染 | 中船 `artifact_contract.json` 对完整单票报告要求 40--60 页、IC 摘要、模型、估值、市场、风险和证据附录；其 `final_signoff.md` 绑定当前 51 页 PDF、渲染集和 SHA-256。 | 雅化 `analysis/template_brief.md`、`analysis/exhibit_plan.md`、`analysis/narrative_blueprint.md` 为事件研究设计；`main.pdf` 19 页，`visual_review.md` 已按事件研究通过。 | 只能在正式 H1 后补齐 | 可立即为未来完整报告规划展品和章节，但不应为了达到页数把当前事件研究扩写为伪完整覆盖。正式 H1 后应使用新模型和新证据构建新 PDF、渲染集、文本快照、哈希与视觉复核。 |
| G12 船舶专属单位经济与交付约束 | 中船合同和模型使用船型/船价、DWT、船位、交付排程、船级/验收、钢材和设备成本、船东预付款、军品/集团订单及重组口径。 | 雅化的实质经济变量是锂盐销量、产品结构、实现 ASP、精矿/转化成本、实际自供、民爆许可利用率、爆破项目进度与回款；其目前在 `analysis/value_chain_economics.md` 和 `analysis/chain_earnings_bridge.md` 中多数为未披露。 | 行业不适用 | 不复制 DWT、船位、造船订单转收入、船东预付款或军品 SOTP。可迁移的是方法：每个行业驱动均须经过“可验证经营量—收入—毛利—现金—归母/EPS—估值信用”的链条；未披露的雅化对应字段保持零信用。 |

## 建议的重建顺序（不构成当前版本修改指令）

1. **H1 前可做：** 完成 G02、G03、G05、G06、G07 的资料归档、字段标准化和缺口—模型限制映射；所有输出保持“事件研究/非评级”标签。
2. **正式 H1 发布日：** 先核验收入、利润、现金流、资产负债、应收、存货、资本开支和分部解释；将预告与正式值差异记录为新的 R0 证据判断。
3. **H1 后但不自动通过：** 仅在锂盐和民爆的收入—成本—现金桥可复算时完成 G04、G08、G09；否则签发 `watchlist only / insufficient evidence`。
4. **完整覆盖签发：** 新合同、R0--R4、当前 PDF/渲染、案例验证器和共享研究门禁均针对同一 H1 后版本通过，才可进入完整单票覆盖的目标价/评级讨论。

## 样本与雅化文件索引

- **中船基准合同与范围：** `workspace/research/china-shipbuilding-600150-20260722/research_brief.md`、`gate_manifest.md/json`、`artifact_contract.md/json`。
- **中船模型、估值与签发：** `analysis/growth_earnings_model.md`、`analysis/segment_valuation_model.md`、`analysis/implied_growth_sensitivity.md`、`analysis/valuation_model.md`、`analysis/valuation_audit.md`、`data/current_valuation_model_20260722.json`、`final_signoff.md/json`、`research_workflow_eval.md/json`。
- **雅化当前边界与证据：** `workspace/research/yahua-group-20260723/research_brief.md`、`gate_manifest.md/json`、`artifact_contract.md/json`、`data/verified_financials.md`、`analysis/company_fundamental_cards.md`、`analysis/value_chain_economics.md`、`analysis/chain_earnings_bridge.md`、`analysis/growth_earnings_model.md`、`analysis/segment_forecast_bridge.md`、`analysis/valuation_model.md`、`analysis/valuation_audit.md`、`analysis/secondary_market_analysis.md`、`data/broker_street_consensus_20260723.md`、`final_signoff.md/json`。
