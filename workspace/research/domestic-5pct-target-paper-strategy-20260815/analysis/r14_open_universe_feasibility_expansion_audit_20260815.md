# R14 开放研究池新增路线边界审计

- 结果：`PASS`。
- 范围：C21 公募 REIT、C22 公司债、C23 开放式公募基金、C24 境内直接股票的数据与权利可行性备忘录。
- 本审计只核查工件的边界与声明一致性；不验证外部网页、不授予数据权利、不建立总体、不选品、不计算收益，也不产生行动。

| 检查 | 结果 | 说明 |
|---|---|---|
| C21 artifacts exist | PASS | c21_public_reit_historical_data_route_research_20260815.json, c21_public_reit_historical_data_route_research_20260815.md |
| C21 JSON object | PASS | c21_public_reit_historical_data_route_research_20260815.json |
| C21 declared conditional status | PASS | CONDITIONAL_LAWFUL_MULTI_SOURCE_ROUTE_IDENTIFIED_NOT_C20_TEST_ADMITTED |
| C21 Markdown mirrors no-action boundary | PASS | c21_public_reit_historical_data_route_research_20260815.md |
| C21 reader wording excludes restricted amount terms | PASS | c21_public_reit_historical_data_route_research_20260815.md |
| C21 records primary-source locators | PASS | url_count=29 |
| C22 artifacts exist | PASS | c22_company_bond_historical_data_route_research_20260815.json, c22_company_bond_historical_data_route_research_20260815.md |
| C22 JSON object | PASS | c22_company_bond_historical_data_route_research_20260815.json |
| C22 declared conditional status | PASS | CONDITIONAL_LAWFUL_MULTI_SOURCE_ROUTE_IDENTIFIED_NOT_TEST_ADMITTED |
| C22 Markdown mirrors no-action boundary | PASS | c22_company_bond_historical_data_route_research_20260815.md |
| C22 reader wording excludes restricted amount terms | PASS | c22_company_bond_historical_data_route_research_20260815.md |
| C22 records primary-source locators | PASS | url_count=11 |
| C23 artifacts exist | PASS | c23_open_ended_public_fund_data_feasibility_20260815.json, c23_open_ended_public_fund_data_feasibility_20260815.md |
| C23 JSON object | PASS | c23_open_ended_public_fund_data_feasibility_20260815.json |
| C23 declared conditional status | PASS | CONDITIONAL_PRODUCT_LEVEL_DATA_PATHS_IDENTIFIED_NOT_YET_TESTABLE |
| C23 Markdown mirrors no-action boundary | PASS | c23_open_ended_public_fund_data_feasibility_20260815.md |
| C23 reader wording excludes restricted amount terms | PASS | c23_open_ended_public_fund_data_feasibility_20260815.md |
| C23 records primary-source locators | PASS | url_count=13 |
| C24 artifacts exist | PASS | c24_direct_ashare_equity_data_feasibility_20260815.json, c24_direct_ashare_equity_data_feasibility_20260815.md |
| C24 JSON object | PASS | c24_direct_ashare_equity_data_feasibility_20260815.json |
| C24 declared conditional status | PASS | CONDITIONAL_LAWFUL_MULTI_SOURCE_ROUTE_IDENTIFIED_NOT_TEST_ADMITTED |
| C24 Markdown mirrors no-action boundary | PASS | c24_direct_ashare_equity_data_feasibility_20260815.md |
| C24 reader wording excludes restricted amount terms | PASS | c24_direct_ashare_equity_data_feasibility_20260815.md |
| C24 records primary-source locators | PASS | url_count=38 |
| C21 preserves no-selection/no-test/no-action fields | PASS | C21 controls |
| C21 treats URLs as locators rather than a rights grant | PASS | C21 rights boundary |
| C22 preserves no-selection/no-test/no-action fields | PASS | C22 controls |
| C22 keeps universe, realized-event, and rights blockers | PASS | C22 field and source boundary |
| C23 preserves no-selection/no-test/no-action fields | PASS | C23 controls |
| C23 confines the five-percent reference to a research hurdle | PASS | A long-run research hurdle only; not a guarantee, minimum return, or product promise. |
| C23 requires data-rights/sample gate before a rule design | PASS | C23-GATE-1 |
| C24 preserves no-selection/no-test/no-action fields | PASS | C24 controls |
| C24 distinguishes Shanghai/Shenzhen A shares from the separate BSE gate | PASS | {'asset_route': 'direct mainland listed equities; base scope is Shanghai/Shenzhen A shares, with BSE treated as a separately explicit domestic-stock coverage gate', 'base_scope': ['Shanghai Stock Exchange Main Board', 'Shanghai Stock Exchange STAR Market', 'Shenzhen Stock Exchange Main Board', 'Shenzhen Stock Exchange ChiNext Market'], 'separately_explicit_domestic_stock_coverage_gate': ['Beijing Stock Exchange'], 'non_silent_exclusion_rule': 'A frozen future protocol must explicitly record a dated, auditable reason for every excluded market, board, or security class before any computation. If it claims to cover BSE or a full domestic-stock scope, BSE must be covered by verified data; if it is limited to Shanghai/Shenzhen A shares, that scope limitation must be explicit. Current listings, surviving names, and data scarcity may not silently define the historical universe.', 'no_stock_selection': True} |
| C24 requires full per-stock institutional diligence | PASS | gate_count=8 |
