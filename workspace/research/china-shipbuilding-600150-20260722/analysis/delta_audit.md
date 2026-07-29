# Delta Audit — Market-Structure and Positioning Coverage

## User Correction

The delivered report used generic absence wording for continuous adjusted K-line history, free-float shares, turnover, margin financing and securities lending, Shanghai-Hong-Kong Stock Connect holdings, public-fund ownership, and Dragon-Tiger List activity. These are required secondary-market inputs, not permissible omissions when structured market sources can be queried.

## Original Miss and Root Cause

| Dimension | Original miss | Failed artifact / gate | Responsible workflow owner | Severity |
|---|---|---|---|---|
| Adjusted continuous K-line | No archived, adjustment-labelled price series or calculated trend/drawdown table | `data/verified_market_data.md`; secondary-market depth accepted keyword-only prose | equity-research / data-collector / data-verifier | S |
| Free float and turnover | No dated free-float-share / free-float-market-cap basis and no daily or rolling turnover context | `data/verified_market_data.md`; `analysis/secondary_market_analysis.md` | data-collector / data-verifier | A |
| Margin trading and Stock Connect | No balance/flow/holding time series, period basis, or source hierarchy | `data/verified_market_data.md`; market-sentiment bridge | data-collector / market-analyst | A |
| Fund ownership and Dragon-Tiger List | No disclosure-period ownership snapshot or explicit lookback query with a negative-result boundary | `data/verified_market_data.md`; secondary-market analysis | data-collector / market-analyst | A |

The immediate root cause is that the single-stock market-depth check validated the presence of English keywords in `analysis/secondary_market_analysis.md`, not source-backed fields, dated series, or a negative-search record. The R2/R4 reviewer then treated that shallow artifact as complete. This is a mechanical PASS / institutional FAIL.

## Repair Scope

| Required evidence | New primary artifact | Source standard | Reader-facing destination |
|---|---|---|---|
| Adjustment-labelled daily K-line, returns, drawdown, moving averages | `data/market_structure_20260722.md/json` | Raw structured response archived; adjustment method and date range explicit | New market-structure section and exhibits |
| Free float, free-float market cap, turnover, volume and amount | `data/market_structure_20260722.md/json` | Dated exchange/structured-market source, units reconciled | New market-structure section and valuation sentiment bridge |
| Margin financing/securities lending and Stock Connect series | `data/capital_positioning_20260722.md/json` | Official preferred; fallback tier and endpoint explicit | New capital-positioning section and risk/trigger table |
| Fund ownership and Dragon-Tiger List search | `data/capital_positioning_20260722.md/json` | Latest disclosure period / defined lookback window, including a documented negative result | New capital-positioning section |

## Files to Change

- `data/market_structure_20260722.md/json`
- `data/capital_positioning_20260722.md/json`
- `data/verified_market_data.md`
- `data/source_registry.md/json`
- `data/claim_audit.md/json`
- `analysis/secondary_market_analysis.md`
- `analysis/house_view.md`, `analysis/valuation_model.md`, and `analysis/risk_framework.md` where data change the action or monitoring thresholds
- Reader-facing LaTeX sections, `main.pdf`, R2/R3/R4 findings, sign-off, workflow evaluation and verifier records

## Prevention Rule (Proposed, Not Yet Applied to Prompts)

For a single-stock full note, the secondary-market gate must require source-backed, dated fields for an adjustment-labelled continuous K-line, free-float shares, turnover, margin financing/securities lending, Stock Connect, latest fund holding disclosure, and a Dragon-Tiger List lookback. `not found` is valid only with an archived query, time range, source and consequence; keyword presence is never evidence.

## Repair Completion Evidence

| Original gap | Completion evidence | Corrected reader-facing treatment |
|---|---|---|
| 连续复权K线 | 727日、`fqt=1`前复权原始序列，`fqt=0/2`对照和哈希均归档 | 发布收益、回撤、均线和区间，并明确不是总回报 |
| 流通/换手 | 截止日流通A股本75.2562亿、换手1.44%、5/20/60日均值，量价股本已勾稽 | 发布“流通A股本”；严格自由流通没有统一分类，不伪造数值 |
| 融资融券/沪股通 | 上交所日度两融与季度沪股通原始响应；日频沪股通负响应归档 | 两融按7月21日，沪股通按6月30日季度存量；不跨频率解释 |
| 基金/龙虎榜 | 2026Q2基金聚合持仓和近一年龙虎榜/全历史日期响应归档 | 发布报告期、家数/股数/市值与已定义的负查询边界 |

本次案例已把新的证据包、来源注册、主张审计、市场分析和第12章连通。下一步只能是基于更新后的PDF完成新的独立R2--R4审阅和验收，不能恢复旧版PDF的PASS状态。

镜像skill/prompt规则仍未自动修改：本次用户要求是修复本报告。若要将本案例的字段级门槛上升为仓库级规则，需要用户授权一并修改两个镜像skill树和共享质量门。
