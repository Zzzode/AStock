# Gate Manifest

| Field | Definition |
|---|---|
| case_id | desay-sv-002920-20260723 |
| report_type | single_stock_full_note |
| data_cutoff | 市场与研究：2026-07-23；财务：截至该日可得的最新定期披露 |
| coverage_pack | custom：智能汽车电子、软件定义汽车与Physical AI未来机会 |
| required_skills | equity-research, reports, supply-chain-research, growth-earnings-model, valuation, research-report-review, pdf |
| required_artifacts | 以 `gate_manifest.json` 的逐项清单为准 |
| review_cycles | R0_evidence → R1_model → R2_draft → R3_render_compliance → R4_final_ic |
| verifiers | case-local verifier；run_research_gates；capability workflow evaluation |
| depth_gates | evidence_depth；broker_consensus_depth；model_depth；valuation_depth；ic_readiness |
| downgrade_path | 客户链、订单、ASP、利用率、毛利率或估值锚不充分时，降为观察名单，不发布投资性目标价 |

## Pre-publish checklist

- [x] 证据深度：Physical AI一手产品、IR及生态合作来源已登记，且客户/数量/收入/毛利边界已复核。
- [x] 模型深度：Physical AI不进入基础EPS；以概率、条件经济学和折现率明确的独立期权层进入合并参考值。
- [x] 估值深度：基础价值CNY86.4、Physical AI风险调整期权CNY2.49和合并参考值CNY88.9均可追溯，且不混入主业P/E。
- [x] IC 可执行性：主业行动标签、Physical AI升级门槛、反证与下一季阈值明确。
- [x] R0-R4：未来机会更新后无开放 S 级或未豁免 A 级问题，所有验收基于同一 PDF/模型版本。
