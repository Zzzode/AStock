# Valuation Model — Allocation Eligibility Only

## Eligibility and Evidence Boundary

No current-price target is issued for cash, index funds, gold or public REITs. The table below distinguishes the Tier-1 evidence for product identity from the controlled allocation decision and the currently unavailable execution evidence. It reports whether a sleeve could enter the strategic allocation after the dated execution-day controls, rather than pretending that an ETF or asset class has a company-style target price.

| Sleeve | Primary method | Bear / Base / Bull | Final target | Conditional model action | Evidence boundary |
|---|---|---|---|---|---|
| Protected liquidity / trading cash | V-internal liquidity target and product controls | not_applicable | not_applicable | CNY40,000 protected reserve and CNY10,000 capped staging cash after account checks | S05 supports the deposit boundary; allocation/cap is controlled; no execution packet is run. |
| Government bonds | duration and quality limit | not_applicable | not_applicable | CNY70,000 511010 only if execution-day q=1 | S08 supports product identity; current price, IOPV, spread and liquidity are unavailable. |
| Dividend equity | diversified total-return / concentration test | not_applicable | not_applicable | CNY30,000 510880 and conditional CNY30,000 512890 in scheduled tranches | S09/S10/S16 support limited identity/concentration context; dated combined holdings and trading evidence are unavailable. |
| Gold ETF | capped diversifier | not_applicable | not_applicable | CNY20,000 518880 only if execution-day q=1 | S11 supports product structure; current price, IOPV, spread and liquidity are unavailable. |
| Public REITs | project cash-flow and premium screen | not_applicable | not_applicable | watch only; CNY0 at launch | S15 supports general mechanism; no project selection or execution evidence exists. |

## Three-Tier Targets

The three tiers are the conservative, base and growth allocation variants in `analysis/allocation_model.md`; they are not security price targets. A change between tiers requires a change in mandate horizon, drawdown capacity or the liquidity target inside $V$, not a one-day market move.

## Relative / PEG / PSG Comparison

PE, PEG, PSG and issuer-comparison methods are not applicable to a strategic multi-asset allocation. The relevant relative comparison is role overlap: cash versus money fund, direct government bonds versus bond ETF, dividend factor versus broader equity factor, and gold versus leveraged derivatives.

## Seasonality Calibration

No earnings-seasonality assumption is used. Annual contributions are allocated only by the post-contribution $V^+=V+C$ target-gap waterfall, active-vector limits and product eligibility, not by a calendar return forecast or an external cash-coverage test. A failed eligibility check uses the protected-liquidity fallback and does not increase staging cash above CNY10,000.

## Next-Quarter Threshold

The next review checks the liquidity sleeves inside $V$, ETF look-through concentration, product legal-document updates, bond duration/credit drift, gold premium/discount, and REIT project disclosures. The required sources, timestamps, q status and controlled premium/discount, spread and liquidity thresholds are defined in data/execution_eligibility_policy_20260812.json, whose current status is not_run. There is no EPS threshold in this report.

## Method and Assumption Bridge

User-stated mandate horizon and loss tolerance → liquidity floor inside $V$ → target weights → six-month deployment → threshold-based rebalancing. A later spending mandate requires a separate plan; it does not deduct an external reserve from $V$. The method is transparent and produces no implied price or upside figure.

## Market-Expectation Valuation Bridge

Current market expectation is intentionally not modeled because a verified current price/NAV/flow packet is unavailable. Execution is conditional on a complete fresh packet with current-session price, IOPV/reference, premium/discount, spread, liquidity, account/lot feasibility and, for 512890, dated combined holdings. The report therefore makes no current value claim.

## Broker/Street Comparison

No broker target-price anchor is used. ETF/product examples are identified through official product documents, and all broker weights are zero because no fund or issuer target price supports a strategic allocation decision.

## Market-Implied Sentiment Anchor

Sentiment weight is zero. It cannot be inferred from a high yield, recent return, price, turnover or a narrative without a reproducible current observation packet.

## Growth Earnings Dependency

No high-growth revenue, unit, ASP, order or EPS credit is used. This report does not use a growth-earnings model.

## Full-Chain Classification Dependency

Not applicable. This is a retail multi-asset allocation report and contains no issuer target-price conclusion.
