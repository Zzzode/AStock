# Fund and Sovereign R0 Fact Pack — 2026-08-14

Scope: 512500, 510880, 511010, 511880, and 260008. Every candidate remains `q=0`. The sole test is conditional/ex-post rolling five-year cost-aware TWRR >=5%; this is not a cash-income objective and contains no allocation, recommendation, automatic-reinvestment, or execution instruction.

Data quality is high for the product and instrument facts because the raw files are official primary disclosures. It is insufficient for T2 return validation. The preferred local `astock` CLI could not load because the virtual environment lacks the `astock` module; primary manager/exchange/official-market disclosures were used.

| Code | Instrument | Official product/instrument fact | Return-evidence boundary | T2 |
|---|---|---|---|---|
| 512500 | 华夏中证500ETF | Equity ETF; tracks CSI 500; normal constituent/substitute-stock minimum is 90% of NAV; management/custody fees are 0.15%/0.05% p.a. | The Q2 2026 report records a 43.79% five-year fund net-value growth rate through 2026-06-30. It is not validated investor-level, cost-aware rolling TWRR. | Blocked |
| 510880 | 华泰柏瑞上证红利ETF | Equity ETF; complete replication of the SSE Dividend Index, subject to its disclosed liquidity exception. | Its 2024 Q4 report records 45.05% five-year fund net-value growth as of 2024-12-31 and says fund indicators exclude holder subscription/trading costs. It is stale and not cost-aware investor TWRR. | Blocked |
| 511010 | 国泰上证5年期国债ETF | Government-bond ETF; optimized sampling of the SSE 5-Year Treasury Bond Index; at least 90% of NAV in index constituent/substitute government bonds; 0.15%/0.05% p.a. management/custody fees. | No captured investor total-return series or historical realized trading-cost data. Published fee terms do not establish actual execution cost. | Blocked |
| 511880 | 银华日利 / 银华交易型货币市场基金 A类 | Exchange-traded money-market fund; invests in cash and permitted short-dated money-market instruments; reported A-share fund-level comprehensive operating expense ratio is 0.64% p.a. | Product summary warns that secondary-market price can differ from NAV and that trading cost/liquidity can affect investor return. Its charts stop at 2023-12-31. | Blocked |
| 260008 | 26附息国债08 | MOF five-year fixed-rate sovereign bond, CNY100 face value, 1.5000% annual coupon, interest from 2026-04-15 and redemption on 2031-04-15. | Coupon and reopening price are terms, not a total-return series. The specific bond has less than five years of life as of the cutoff. | Hard blocked |

## Exact T2 blockers

1. No candidate has an archived and reconcilable investor-level total-return series that accounts for NAV, exchange price where relevant, distributions/corporate actions, and the report's no-automatic-reinvestment convention.
2. No historical executable cost series has been obtained: actual broker commission schedule, bid-ask spread, slippage/impact, route-specific creation/redemption or custody costs, and applicable taxes/fees. Fund expense ratios are not execution costs.
3. No reproducible rolling-five-year observation window, pricing time, TWRR cash-flow convention, or rebalancing convention is supplied.
4. 260008 was first issued in April 2026; the specific bond fails the five-year-history prerequisite mechanically at the case cutoff.

Raw-source file and hash metadata: `sources/official-fund-sovereign-continuation-20260814/manifest.json`. This pack does not prove a T2 pass or fail for the ETF candidates and does not authorize any action.
