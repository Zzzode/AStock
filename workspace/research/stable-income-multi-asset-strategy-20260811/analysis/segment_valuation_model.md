# Segment Valuation Model — Asset-Class Suitability, Not Security Price Targets

This report has no company-specific price target. The **segment valuation depth** below converts the role of each asset sleeve into a verifiable economic test. In this context, **SOTP**, **revenue**, **net profit**, **multiple**, and security-level earnings are `not_applicable`; they are deliberately not invented for index funds, cash or gold.

| Segment / sleeve | Economic driver | Valuation or allocation test | Sensitivity | Validation trigger |
|---|---|---|---|---|
| Protected liquidity / trading cash | immediate nominal capital access inside $V$ | target weight, CNY500,000 deposit-insurance boundary where applicable, withdrawal terms and non-deposit haircut | institution concentration, inflation, maturity mismatch | protected sleeve and trading-cash cap remain within the active vector; funds/ETFs are not treated as deposits |
| Government-bond sleeve | coupon, duration and yield curve | duration/rate-shock sensitivity rather than a PE multiple | +100bp rate shock, premium/discount | disclosed duration and high-quality exposure remain within mandate |
| Dividend-equity sleeve | distributable cash flow and sector composition | total-return and payout-quality review, not trailing yield alone | dividend cuts, financial/cyclical concentration | merged ETF holdings pass concentration limits |
| Gold sleeve | domestic gold spot price | strategic 10% risk-budget cap, not DCF/SOTP | real rates, RMB, geopolitical shock | non-levered spot ETF and normal premium/discount |
| REIT sleeve | asset operating cash flow | project cash-flow, debt and distribution-quality review | occupancy/traffic, refinancing, premium | default 0%; three independent approved projects, <=2% each and <=5% total cap |

The model is reproducible because all target weights, ranges, scenario shocks and arithmetic are explicitly supplied in `analysis/allocation_model.md` and `analysis/scenario_model.md`. It does not claim an intrinsic value, revenue forecast, net profit forecast, EPS, target price or multiple for any fund.
