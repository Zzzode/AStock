---
name: growth-earnings-model
description: Complete AStock high-growth earnings precision modeling workflow for equity research. Use when valuing or auditing AI, semiconductor, robotics, new energy, high-growth hardware/software, order-driven, unit-volume-driven, ASP-driven, segment-SOTP, revenue-multiple, PEG/PSG, or "sales/shipments expected to double" investment narratives, and whenever equity-research or valuation needs to convert theme growth into revenue, gross profit, net profit, EPS, and valuation sensitivity.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Growth Earnings Model

Build the precision earnings bridge that explains how a high-growth narrative becomes revenue, margin, EPS, and valuation. This skill is the authoritative gate between supply-chain evidence and valuation when market value depends on AI-related, order-driven, shipment-driven, ASP-driven, or segment-mix growth.

## Required Inputs

- Case directory under `workspace/research/<case-id>/`
- Ticker universe, report language, and data cutoff
- `data/verified_financials.md`
- `data/verified_market_data.md`
- `data/source_registry.md`
- `data/claim_audit.md`
- `data/consensus_analysis.md` or public broker/consensus snapshot when available
- Supply-chain outputs when this is an industry-chain report:
	  - `analysis/supply_chain_model.md`
	  - `analysis/company_fundamental_cards.md`
	  - `analysis/value_chain_economics.md`
	  - `analysis/chain_earnings_bridge.md`
	  - `data/supply_chain_relationships.md/json`
	  - `data/customer_chain_audit.md/json`

If a driver cannot be evidenced, write `not disclosed`, `not found`, or `insufficient evidence`. Do not fill unit volume, ASP, AI revenue share, margin, customer allocation, or order conversion with unsupported assumptions.

## Procedure

1. **Classify whether precision modeling is required.**
   - Required when the investment case depends on high growth, AI or other theme-related revenue, shipments, units, ASP, order/backlog conversion, customer allocation, segment mix, operating leverage, PEG/PSG, PS/SOTP, or a claim such as "this quarter revenue/sales/orders will double."
   - If a ticker is stable, cyclical, asset-heavy, or yield-like and does not depend on high-growth segment re-rating, mark `not applicable` with reason.

2. **Separate base business from growth business.**
   - Split reported revenue, gross profit, net profit, EPS, and valuation denominator into base business and growth driver segments.
   - For mixed companies, isolate the high-growth segment before assigning high-growth multiples. Do not apply AI or high-growth multiples to the whole company unless the report proves segment purity.

3. **Build the unit economics bridge.**
   - Use the formula:

```text
growth revenue = units or shipments * ASP * recognized revenue ratio
growth gross profit = growth revenue * gross margin
growth operating profit = growth gross profit - incremental opex - depreciation/amortization
growth net profit = growth operating profit * (1 - tax rate) + equity-method contribution where applicable
growth EPS = growth net profit / shares
```

	   - When direct unit volume is unavailable, use the best evidenced proxy: order value, backlog, capacity, utilization, customer allocation, shipment schedule, bill of materials share, or segment revenue disclosure.
	   - Record which proxy is used and why it is defensible.

4. **Validate value-chain economics before EPS credit.**
   - Consume or create `analysis/value_chain_economics.md`.
   - Record value amount, ASP or price proxy, margin pool, supply/demand balance, capacity, utilization/yield, certification/customer qualification, order/backlog visibility, and price pass-through.
   - A high-growth segment can receive EPS or valuation credit only when value-chain economics can explain both revenue conversion and margin conversion.
   - If economics are unavailable, label the driver `watchlist only / insufficient economics`.

5. **Run scenario and sensitivity math.**
   - Build bear/base/bull cases for units, ASP, conversion ratio, gross margin, opex intensity, tax, and valuation multiple.
   - Show sensitivity to the driver that matters most, such as shipments, ASP, AI revenue share, customer concentration, order conversion, or margin.
   - Calculate what the current price implies: implied growth revenue, implied units/ASP, implied margin, implied EPS, and the number of quarters required to justify the market price.

6. **Decide valuation credit.**
   - Give **earnings credit** only when unit/order/customer/margin evidence supports revenue and profit conversion.
   - Give **optionality credit** when product/customer evidence exists but conversion or margin is not yet proven.
   - Give **watchlist-only credit** when the report only has generic AI demand, downstream TAM, or market rumor.
   - Block valuation upside from the growth segment if the model cannot distinguish growth-segment economics from base business economics.

7. **Audit the model.**
   - Recalculate revenue = units * ASP, gross profit = revenue * margin, EPS = net profit / shares, implied PE/PS/PEG/PSG, and upside/downside.
   - Flag fake precision, unsupported segment purity, unsupported customer allocation, double-counting supply-chain revenue, and inconsistent units.

## Required Outputs

Write all outputs in the case directory:

- `analysis/growth_earnings_model.md`
- `analysis/value_chain_economics.md` when the supply-chain skill has not already produced a usable file
- `analysis/segment_forecast_bridge.md`
- `analysis/implied_growth_sensitivity.md`
- `data/growth_driver_model.json`

`data/growth_driver_model.json` must include:

```text
ticker | company | applies | growth_driver | base_business_revenue | growth_segment_revenue | value_amount_or_proxy | unit_volume_or_proxy | ASP_or_price | recognized_revenue_ratio | supply_demand_state | capacity_or_utilization | certification_or_customer_qualification | growth_gross_margin | incremental_opex | growth_net_profit | growth_EPS | evidence_type | source | evidence_gap | valuation_credit | bear | base | bull | current_price_implied_growth | sensitivity_key
```

`analysis/growth_earnings_model.md` must include:

- Gate status: `PASS`, `CONDITIONAL`, or `BLOCKED`
- Which tickers require precision modeling and why
- Base business versus growth business split
- Value-chain economics bridge: value amount, ASP/price proxy, margin pool, supply/demand, capacity/utilization, customer certification, and order visibility
- Unit/order/ASP/revenue/margin/EPS bridge
- Scenario results and valuation credit decision
- Current-price-implied growth and evidence needed to validate or break it

`analysis/segment_forecast_bridge.md` must include:

- Reported segment baseline
- Growth segment forecast by quarter or fiscal year
- Bridge from growth segment revenue to company-level revenue, net profit, EPS, and valuation method

`analysis/implied_growth_sensitivity.md` must include:

- Sensitivity tables for units/shipments, ASP, margin, conversion ratio, and valuation multiple
- What needs to be true for current price, base target, and bull target
- Evidence required to upgrade or downgrade valuation credit

## Interfaces

- `equity-research` must run this skill before `valuation` whenever covered tickers have high-growth, AI, shipment, ASP, order, or segment-mix valuation narratives.
- `valuation` must consume this skill's outputs before assigning high-growth multiples, PEG/PSG, PS/SOTP, sentiment weights, or growth-segment upside.
- `latex-writer` must include the growth earnings bridge and implied growth sensitivity in reader-facing Chinese prose when the report language is Chinese.
- `research-report-review` must treat missing required growth-earnings outputs as publication blockers when investable valuation depends on high-growth claims.

## Constraints

- Do not use generic AI demand, TAM, downstream capex, or theme heat as proof of company revenue.
- Do not apply a high-growth multiple to consolidated revenue when only one segment is growing.
- Do not turn capacity into revenue without utilization, customer allocation, orders, shipment schedule, price, or conversion evidence.
- Do not turn value-chain participation into EPS credit without value amount, ASP/price proxy, margin pool, supply/demand, and customer/order evidence or an explicit gap label.
- Do not annualize one strong quarter into a full-year denominator without seasonality and order durability.
- Do not give investable upside from a growth segment without current price, explicit driver math, scenario range, implied growth, and source-quality labels.
- For Chinese reports, write reader-facing conclusions, model interpretation, catalysts, invalidation triggers, and caveats in Chinese.
