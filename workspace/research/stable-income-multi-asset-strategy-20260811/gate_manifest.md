# Gate Manifest — Stable-Income Multi-Asset Strategy

| Field | Value |
|---|---|
| Case ID | `stable-income-multi-asset-strategy-20260811` |
| Case profile | `strategic_allocation` |
| Scope ID | `strategic-allocation-etf-first-v2-20260811` |
| Report type | Conditional strategic multi-asset allocation research note |
| Data cutoff | 2026-08-11; the active scope uses only complete locally archived rule, exchange and product materials |
| Framework | Fixed-CNY200,000, ETF/asset-layer-first risk budget |
| Direct stock at launch | 0%; any later sleeve only replaces red-dividend ETF exposure, total at most 15% and single issuer at most 5% |
| REITs at launch | 0%; at most 5% in aggregate and 2% per project only after three independent projects pass all activation gates, funded from rate bonds |
| Return/cash policy | 3%--6% is formula-only, five-year-plus nominal total-return sensitivity; $r$ never estimates cash, and only receipt-evidenced after-tax, after-fee $D_0$ is recorded and reinvested |
| Execution state | Eligibility policy is `not_run`; all ETF sleeves remain $q=0$ until current-session evidence and required look-through pass |
| Drawdown policy | Planning stress does not trigger action; only documented external-flow-adjusted $DD_t$ may invoke the -12%/-18% controls |
| Issuer target-price policy | None |
| Publication state | PASS for a conditional research framework after hash-bound independent R0--R4 review. Execution remains `not_run` with all ETF $q=0$; a current-session eligibility packet is required before any implementation and is not a publication prerequisite. |

## Active artifact graph

The active reader source is `main.tex` plus these exact sections:

1. `sections/ch01_decision.tex`
2. `sections/ch02_stock_pool.tex`
3. `sections/ch03_portfolio.tex`
4. `sections/ch04_returns.tex`
5. `sections/ch05_compounding.tex`
6. `sections/ch06_risk.tex`
7. `sections/ch07_execution.tex`
8. `sections/app_sources.tex`

The canonical structured packets are `data/portfolio_return_model_20260811.json`, `data/model_portfolio_implementation_20260812.json`, `data/execution_eligibility_policy_20260812.json`, `data/source_archive_status.json`, `data/current_valuation_model_20260811.json`, and `data/build_provenance_20260812_actionability.json`. `raw_market_data_20260811`, `raw_quote_snapshot_20260811`, `dividend_evidence_20260811` and `high_dividend_stock_pool_20260811` are retained only as retired legacy audit packets and cannot support current-scope conclusions. Earlier provenance packets and superseded renders are also history, not current-release evidence.

## Pass conditions

1. Material active-scope claims resolve to dated locally archived source records with explicit quality and limitations; retired legacy packets cannot re-enter a current conclusion.
2. Direct-stock and REIT activation gates, caps and initial zero weights reconcile across the scope brief, allocation model, return model and reader source.
3. No point return, issuer target price, fixed cash distribution, order instruction, suitability certification or performance guarantee is presented.
4. The fixed CNY200,000 allocation and stress arithmetic are reproducible.
5. Every active sleeve has a reader-facing designated model instrument (or explicit cash/deposit implementation), target amount, staged action, execution-day validation gate and deterministic protected-liquidity fallback; generic representative examples do not satisfy this condition.
6. Eligibility remains `not_run` until every required current-session product, market-quality, account and combined-holdings field passes; missing data fails $q$ and never creates a substitute trade or cash-cap breach.
7. Formula-only $r$ sensitivity, receipt-evidenced $D_0$ cash and scenario stress remain distinct; scenario output cannot trigger the observed-$DD_t$ controls.
8. The current source, PDF, extracted text, full render set, visual review and R0--R4 records carry matching scope and artifact identity; author build evidence is not a substitute for an independent R3 review.
9. All declared applicable checks pass with zero unresolved S-level and unwaived A-level findings before publication.
