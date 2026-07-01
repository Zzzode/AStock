---
name: supply-chain-research
description: Complete AStock supply-chain research workflow for equity research. Use when building or auditing industry-chain reports, upstream/downstream mapping, customer-chain evidence, full-chain universe construction, core-versus-satellite classification, product/process exposure, capacity/certification/order visibility, value-chain economics, revenue exposure, chain earnings bridges, or whenever equity-research, valuation, latex-writer, or research-report-review needs supply-chain evidence.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Supply-Chain Research

Build the evidence package that explains how an investment theme becomes revenue, margins, earnings, and valuation for each covered company. This skill is the authoritative supply-chain gate for full industry-chain research reports.

## Required Inputs

- Case directory under `workspace/research/<case-id>/`
- Theme, ticker universe if provided, report language, data cutoff, and selected industry coverage pack
- `research_brief.md`
- `analysis/template_brief.md`
- `data/report_catalog.md`
- `data/source_registry.md/json`
- `data/claim_audit.md/json`
- `source_exhaustion_log.md/json` when source probes already exist
- `data/verified_financials.md`
- `data/verified_market_data.md`
- Raw sources under the case-scoped `sources/` tree

If a required evidence item is unavailable, write `not found` or `not disclosed` with the source paths checked. Do not silently omit the field.

## Hard Rules

- Industry-chain reports start with the **full chain**, not with a short listed-stock pool.
- Non-listed, overseas, private, demand-anchor, low-purity, and unavailable nodes must be recorded instead of dropped.
- Demand anchors prove demand context only; they do not prove upstream revenue or orders.
- A listed ticker can enter the core valuation pool only when relationship evidence and value-chain economics can support valuation work.
- A missing chain block is a coverage gap, not an excuse to narrow the report after the fact.
- Core valuation eligibility requires all three: company-level product/process exposure, customer/platform/order/certification evidence, and value-chain economics that can explain revenue and margin conversion. If any one is missing, classify the ticker as `satellite_watch` or `watchlist only / insufficient evidence`.
- Evidence gaps must carry a valuation consequence. A gap that affects revenue, margin, EPS, or target price must set `blocks_valuation: true` and must be consumed by valuation and review.

## Procedure

1. **Define the full-chain taxonomy.**
   - Split the theme into all material upstream inputs, equipment, device/component layers, midstream products/processes, downstream customers/platforms/applications, and demand-verification anchors.
   - Apply the selected industry coverage pack from `workspace/templates/industry-coverage-packs/`.
   - Use Mermaid syntax for diagrams. Do not use ASCII diagrams.
   - Write `analysis/full_chain_taxonomy.md`.

2. **Build the full-chain universe.**
   - Create `data/full_chain_universe_<YYYYMMDD>.md/json`.
   - Include listed A-share names, HK/US/overseas leaders, private companies, demand anchors, low-purity names, and nodes where investable mapping is unavailable.
   - Every row must include `node_type`: `listed`, `overseas`, `private`, `demand_anchor`, `low_purity`, or `unavailable`.
   - Assign each node to `core_valuation`, `satellite_watch`, `demand_anchor`, `out_of_scope`, or `unavailable`.

3. **Build core-versus-satellite classification.**
   - Write `analysis/core_vs_satellite_universe.md`.
   - Explain why each core ticker is investable or why a satellite remains watchlist-only.
   - Separate direct beneficiaries from thematic diffusion names and from demand anchors.

4. **Build the coverage gap matrix.**
   - Write `analysis/coverage_gap_matrix.md`.
   - For every missing block or weakly evidenced node, record gap, reason, sources checked, next verification path, whether valuation is blocked, and expected upgrade trigger.
   - Use `blocks_valuation: true` when missing customer/order/ASP/capacity/utilization/margin evidence prevents company-level revenue, margin, EPS, or valuation credit.

5. **Map company relationships.**
   - For every covered ticker, map upstream input, product/process exposure, downstream customer/platform/application, and profit pool.
   - Classify every relationship as `confirmed`, `official-disclosed`, `broker-stated`, `media-stated`, `inferred`, `rumor`, or `not found`.
   - Preserve source path, original URL, date, source type, and evidence confidence.
   - Assign `source_tier`, `evidence_score`, `valuation_eligibility`, and `downgrade_trigger` to every relationship row.

6. **Quantify value-chain economics.**
   - Write `analysis/value_chain_economics.md`.
   - Capture value amount, ASP or price proxy, gross-margin / EBITDA-margin pool, supply-demand balance, capacity, utilization, yield or purity/specification, certification status, customer qualification, order/backlog visibility, capex, working capital, and price pass-through.
   - If economics are unavailable, mark valuation credit as `watchlist only / insufficient economics`.

7. **Build the earnings bridge.**
   - Connect chain evidence and value-chain economics to revenue, margin, earnings, and next-quarter validation thresholds.
   - Separate realized earnings drivers from optionality, sentiment, and long-duration localization narratives.

8. **Audit customer-chain claims.**
   - High-impact claims such as named customers, platform qualification, long-term orders, capacity, purity/specification, product revenue share, price pass-through, and localization substitution must enter `data/customer_chain_audit.md/json`.
   - Weak evidence can support watchlist language, not investable valuation credit.
   - Every core valuation ticker must have customer-chain audit fields for customer/platform, certification status, order/backlog, ASP or price proxy, capacity, utilization/yield, product revenue exposure, margin impact, evidence score, source tier, and downgrade trigger. Use `not disclosed` or `not found` rather than blanks.

9. **Block or pass the supply-chain gate.**
   - Mark `PASS` only when the full-chain universe exists, all coverage-pack blocks are mapped, every core valuation ticker has a company card and relationship row, and valuation-relevant economics are explicit.
   - Mark `CONDITIONAL` when rows exist but key fields are `not found` and those gaps are disclosed in the coverage gap matrix.
   - Mark `BLOCKED` when the report cannot distinguish direct beneficiaries from thematic diffusion names, when the full-chain universe is missing, or when a core valuation ticker lacks relationship evidence.

## Required Outputs

Write all outputs in the case directory:

- `data/full_chain_universe_<YYYYMMDD>.md`
- `data/full_chain_universe_<YYYYMMDD>.json`
- `analysis/full_chain_taxonomy.md`
- `analysis/core_vs_satellite_universe.md`
- `analysis/coverage_gap_matrix.md`
- `analysis/supply_chain_model.md`
- `analysis/company_fundamental_cards.md`
- `analysis/value_chain_economics.md`
- `analysis/chain_earnings_bridge.md`
- `data/supply_chain_relationships.md`
- `data/supply_chain_relationships.json`
- `data/customer_chain_audit.md`
- `data/customer_chain_audit.json`

`data/full_chain_universe_<YYYYMMDD>.md/json` must include these fields:

```text
node_id | chain_block | subsegment | node_name | node_type | listed_ticker | market | company_status | chain_role | product_or_service | demand_anchor_or_customer | evidence_status | source_count | strongest_source | evidence_gap | classification | valuation_status | next_verification_path | upgrade_trigger
```

`node_type` enum:

```text
listed | overseas | private | demand_anchor | low_purity | unavailable
```

`analysis/core_vs_satellite_universe.md` must include:

- Core valuation pool with valuation eligibility reason and source count.
- Satellite watch pool with missing evidence and upgrade trigger.
- Demand anchors with demand role and why they are not upstream-beneficiary proof.
- Excluded / unavailable nodes and the reason for exclusion.

`analysis/coverage_gap_matrix.md` must include:

```text
gap_id | chain_block | missing_node_or_field | why_it_matters | sources_checked | reason_unresolved | next_verification_path | blocks_valuation | owner_skill_or_role
```

`data/supply_chain_relationships.md/json` must include these fields:

```text
ticker | company | chain_layer | node_type | upstream_input | product_or_process | downstream_customer_or_platform | relationship_type | confidence | source_tier | evidence_score | revenue_exposure | capacity_or_certification | order_visibility | ASP_or_price_proxy | utilization_or_yield | margin_or_earnings_impact | source | evidence_gap | valuation_eligibility | downgrade_trigger | used_in_valuation
```

`data/customer_chain_audit.md/json` must include these fields for every high-impact claim and every core valuation ticker:

```text
ticker | company | customer_or_platform | claim_type | product_or_process | certification_status | order_or_backlog | ASP_or_price_proxy | capacity | utilization_or_yield | revenue_exposure | margin_impact | source_tier | evidence_score | source | evidence_gap | blocks_valuation | downgrade_trigger | adopted_wording
```

`analysis/company_fundamental_cards.md` must include one card per core valuation ticker and any satellite ticker explicitly covered in the report:

- Chain role and directness.
- Product/process exposure.
- Upstream input dependency.
- Downstream customer/platform/application evidence.
- Revenue exposure and product mix.
- Capacity, purity/specification, certification, and order visibility.
- Recent revenue, net profit, margin, cash flow, inventory/debt, and capex observations where available.
- Moat and substitution risk.
- Valuation relevance and what evidence is still missing.
- Core-pool eligibility decision: `eligible`, `watchlist only / insufficient customer evidence`, `watchlist only / insufficient economics`, or `unavailable`.

`analysis/value_chain_economics.md` must include:

```text
chain_block | value_amount_or_proxy | ASP_or_price_proxy | margin_pool | supply_demand_state | capacity | utilization_or_yield | customer_certification | order_or_backlog_visibility | economics_source | evidence_gap | valuation_credit
```

`analysis/chain_earnings_bridge.md` must include:

- Theme-level profit-pool bridge.
- Ticker-level earnings bridge.
- Next-quarter validation thresholds.
- Evidence needed to upgrade or downgrade valuation credit.

## Interfaces

- `equity-research` must run this skill before the house-view, growth-earnings, valuation, risk, exhibit, writing, and review gates in full industry-chain reports.
- `growth-earnings-model` must consume `analysis/value_chain_economics.md` when converting high-growth themes into EPS.
- `valuation` must consume the full-chain package, core-versus-satellite classification, and value-chain economics when selecting business-model methods, catalysts, invalidation, and next-quarter thresholds.
- `latex-writer` must include the full-chain universe, coverage gaps, value-chain economics, supply-chain model, company cards, and earnings bridge in reader-facing Chinese prose when the report language is Chinese.
- `research-report-review` must treat missing required full-chain or supply-chain outputs as publication blockers for full industry-chain reports.

## Constraints

- Do not write generic “beneficiary” labels without relationship evidence.
- Do not treat downstream demand anchors as proof of upstream revenue.
- Do not turn capacity into revenue without utilization, customer qualification, order, or pricing evidence.
- Do not give valuation credit for named customers, platforms, certifications, or orders unless the claim is in `customer_chain_audit`.
- Do not proceed with investable recommendations if the covered ticker lacks both a company card and relationship row.
- Do not keep a ticker in the core valuation pool when `coverage_gap_matrix` or `customer_chain_audit` marks customer/order/ASP/capacity/utilization/margin evidence as `blocks_valuation: true`.
- Do not omit private, overseas, unavailable, or low-purity nodes just because they are not direct A-share valuation candidates.
- Preserve project workspace conventions: raw sources stay under `sources/`; normalized packets stay under `data/`; analyst synthesis stays under `analysis/`.
