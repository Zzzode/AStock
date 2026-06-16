# Deep Template Analysis: Global Top-Tier Research Reports

**Scope:** six publicly accessible institutional research/report PDFs collected under `workspace/templates/global-broker-research/pdfs/`.

**Purpose:** extract report-writing patterns, exhibit architecture, source/disclosure conventions, and reusable components for AStock research production.

## Executive Summary

Top-tier reports are not just long-form analysis. They are structured research products. Their common pattern is:

1. Start with a clear house view.
2. Turn each important judgment into an exhibit.
3. Separate observed data, forecasts, scenarios, and opinions.
4. Put source quality and disclosure in controlled places.
5. Make the first page or first spread a decision dashboard.

Our current AStock reports should move from:

`collect reports -> summarize broker views -> write LaTeX`

to:

`choose report type -> benchmark template -> build source registry -> form house view -> plan exhibits -> write -> render-review -> fix -> publish`.

## 1. J.P. Morgan Equity Research Note

**File:** `pdfs/jpm-equity-research-hulu-sample.pdf`  
**Type:** single-stock / asset-focused equity research note  
**Length:** 31 pages

### Structure

- Page 1: rating, ticker, current price, target price, thesis summary, key bullets, analyst block, price performance, company data.
- Page 2: follow-on summary and key argument expansion.
- Page 3: table of contents.
- Pages 4-10: operating and industry analysis using figures.
- Pages 11-20: valuation analysis and market sizing.
- Pages 21-27: investment thesis, valuation, risks, segment financials, SOTP, comparable companies.
- Pages 28-31: disclosures and regulatory language.

### Writing Pattern

- The report states a specific view immediately: rating + target price + why.
- It does not begin with a general industry essay.
- Each section advances one part of the valuation story.
- Figures are numbered, titled, and sourced.
- Risks are tied to the rating and target price, not generic risk lists.

### Reusable Components

- `investment_dashboard`: ticker, price, target, rating, upside/downside, data date.
- `key_takeaways`: three to five bullets, each tied to a forecast or catalyst.
- `operating_driver_pages`: subscriber/user/ARPU/segment revenue charts.
- `valuation_bridge`: value per user / comps / SOTP table.
- `rating_risk_box`: what would invalidate the rating and target.
- `disclosure_appendix`: conflicts, rating definitions, distribution disclosures.

### AStock Implications

For stock-level A-share reports, the first page must show current price, target framework, evidence quality, thesis, and downside conditions. A company chapter should not be pure prose; it should include operating metrics, valuation bridge, and risks to the thesis.

## 2. J.P. Morgan Guide to the Markets

**File:** `pdfs/jpm-guide-to-the-markets-asia.pdf`  
**Type:** market guide / chartbook  
**Length:** 92 pages

### Structure

- Page reference first.
- Regional economy pages.
- Global economy pages.
- Equity returns, earnings, valuations, sectors.
- Fixed income, FX, commodities, alternatives.
- Investing principles and disclosures.

### Writing Pattern

- Every page answers one market question.
- The chart is the main argument; prose is minimal.
- Sources are standardized and precise.
- Page titles are descriptive and self-contained.
- The guide is modular; pages can be reused in client conversations.

### Reusable Components

- `page_reference`: grouped navigation index.
- `single_question_chart_page`: one page, one market question, one primary chart.
- `valuation_comparison_chart`: PE/PB/yield/spread across regions/sectors.
- `return_decomposition`: returns split by earnings, multiples, dividends, currency.
- `cycle_chart`: returns by cycle stage.
- `source_note`: standardized bottom source block.

### AStock Implications

For data-heavy chapters, do not use dense longtables in the main body. Use chartbook style: one exhibit per claim. Put detail tables in appendices.

## 3. BlackRock BII Global Outlook in Charts

**File:** `pdfs/blackrock-bii-global-outlook-in-charts-us.pdf`  
**Type:** global outlook in charts  
**Length:** 28 pages

### Structure

- Cover includes capital-at-risk language.
- Early pages define mega forces and investment themes.
- The report proceeds through chart-led evidence.
- It repeats concise risk/disclosure language throughout.
- Ends with tactical/strategic views and full disclosures.

### Writing Pattern

- Strong house view: “mega forces are clashing.”
- Three themes are introduced early and drive the whole report.
- Each chart has a message, not just a title.
- Forecasts are framed as uncertain: “may not come to pass.”
- The report avoids fake precision when discussing structural shifts.

### Reusable Components

- `mega_force_header`: structural theme and market implication.
- `theme_cards`: three to five core themes with one-line investment meaning.
- `scenario_band`: uncertain forecast range rather than point estimate.
- `tactical_vs_strategic_views`: near-term vs long-term table.
- `risk_disclosure_banner`: visible but compact warning.

### AStock Implications

Thematic reports should start from our house view of the structural force, not from broker summaries. For AI PCB, the frame should be platform-chain migration, material bottleneck, and certification scarcity.

## 4. Capital Group Outlook

**File:** `pdfs/capitalgroup-2026-outlook-report.pdf`  
**Type:** annual outlook / long-term investment perspective  
**Length:** 20 pages

### Structure

- Long-term perspective cover.
- CIO/PM narrative.
- Macro perspectives.
- Equity opportunities.
- Fixed income opportunities.
- Source and disclosure notes.

### Writing Pattern

- The report is readable, opinionated, and balanced.
- Page titles are judgments: “A market pullback would not be surprising.”
- It uses charts to support a narrative, not to dump data.
- It balances opportunities and risks without sounding mechanical.

### Reusable Components

- `house_view_essay`: one-page narrative from the portfolio manager perspective.
- `theme_page`: title as a judgment, chart as evidence, paragraph as implication.
- `opportunity_map`: what to own, why, and what risk offsets it.
- `balanced_risk_note`: risk and opportunity in the same paragraph.

### AStock Implications

Our reports need stronger house view sections. Broker sources should support our thesis but should not be the grammar of the report. Replace “券商认为” paragraphs with “我们的判断是... 证据包括... 反证是...”.

## 5. Vanguard Economic and Market Outlook

**File:** `pdfs/vanguard-2026-economic-market-outlook.pdf`  
**Type:** economic and market outlook whitepaper  
**Length:** 28 pages

### Structure

- Cover with sharp thesis: “AI exuberance: Economic upside, stock market downside.”
- Contents page.
- Global outlook summary.
- AI outlook.
- Market and portfolio outlook.
- Regional economic outlooks.
- Model/disclosure appendix.

### Writing Pattern

- The title already contains the tension.
- Observed facts, forecasts, and risks are separated.
- Scenario probability and model assumptions are explicit.
- It states when market pricing may be too optimistic.
- It uses sober language and avoids overclaiming.

### Reusable Components

- `thesis_tension_title`: upside and downside in one sentence.
- `forecast_table`: growth, inflation, policy rate, key risk.
- `scenario_probability_table`: baseline/upside/downside.
- `model_assumptions_box`: what is forecast, observed, and uncertain.
- `valuation_warning`: how much optimism is already priced.

### AStock Implications

Valuation sections must distinguish observed data, broker forecast, our scenario, and rumor. If a company lacks 2026E net profit, do not draw a 2026E PE chart. If a target price is not comparable, mark it as not comparable.

## 6. AllianceBernstein Capital Markets Outlook

**File:** `pdfs/alliancebernstein-2q-2026-capital-markets-outlook.pdf`  
**Type:** quarterly capital markets outlook / cross-asset strategy  
**Length:** 50 pages

### Structure

- Cover.
- Timeline of previous outlook themes.
- Market intersection / current state.
- Macro, inflation, growth, labor, Fed.
- Equities, valuations, style, themes.
- Fixed income and credit.
- Appendix, risk notes, index definitions.

### Writing Pattern

- Uses a timeline to show intellectual continuity.
- Frames the current quarter as an intersection of forces.
- Every page has a market implication.
- It uses scenario charts and valuation ranges.
- It includes a large risk/disclosure section.

### Reusable Components

- `theme_timeline`: prior views and how current view evolved.
- `market_phase_map`: where we are in the cycle.
- `scenario_price_target_range`: earnings x multiple outcomes.
- `risk_heatmap`: probability vs impact.
- `cross_asset_linkage`: macro event -> asset class -> sector impact.

### AStock Implications

Quarterly A-share theme reports should include a market phase map, catalyst calendar, and scenario target range. For AI PCB, this means separating theme discovery, target price revision, earnings verification, and crowded unwind.

## Cross-Report Template Principles

### Principle 1: The first page must make the decision possible

The first page should contain:

- Report type and date.
- Data cutoff.
- House view.
- Current price / valuation state for investable reports.
- Core upside and downside drivers.
- Evidence quality warning if sources are mixed.

### Principle 2: Every strong conclusion needs an exhibit

Examples:

- Customer-chain thesis -> platform-chain heatmap.
- Valuation conclusion -> price target / PE / scenario exhibit.
- Earnings acceleration -> quarterly bridge.
- Source reliability -> evidence pyramid.
- Risk conclusion -> probability-impact heatmap.
- Catalyst conclusion -> timeline.

### Principle 3: Source quality belongs in a registry, not in every main table

Main body should present our view. Source quality should be visible but not dominate the reading experience. Use appendix tables and footnotes:

- official filing
- original broker PDF
- broker abstract
- media repost
- third-party preview
- search snippet
- rumor
- corpus gap

### Principle 4: Separate observed, forecast, scenario, and rumor

Every number should be tagged internally as:

- observed actual
- company guidance
- broker forecast
- our scenario
- market rumor / unverified

### Principle 5: Do not produce fake precision

Do not plot:

- PE if earnings forecast is unavailable.
- target upside if target price is for another share class.
- platform earnings bridge if customer-chain contribution is unknown.

### Principle 6: Long tables are appendices, not main arguments

Main chapters should use:

- heatmaps
- bridge charts
- timelines
- scatter plots
- scorecards
- network maps
- scenario bands

Long audit tables should be in appendices.

## Recommended AStock Report Components

| Component | Purpose | Inspired By |
|---|---|---|
| `investment_dashboard` | First-page decision view | JPM single-stock note |
| `page_reference` | Navigation for chartbook reports | JPM Guide |
| `house_view_box` | Our own thesis | Capital Group / BlackRock |
| `evidence_pyramid` | Source quality overview | BlackRock/Vanguard discipline |
| `platform_chain_heatmap` | Customer-chain durability | AI PCB needs |
| `valuation_scorecard` | PE/upside/current price snapshot | JPM + AB |
| `quarterly_bridge` | Q1/Q2/H2 earnings pressure | Vanguard scenario discipline |
| `scenario_band` | Bull/base/bear valuation | Vanguard / AB |
| `risk_heatmap` | Probability vs impact | AB |
| `catalyst_timeline` | Event monitoring | AB |
| `claim_audit` | Source traceability | Our Cosmos3 appendix pattern |
| `disclosure_appendix` | Compliance | JPM / BlackRock |

## Required Agent / Skill Changes

### Add `template-benchmark-analyst`

Selects the correct report model before writing:

- single-stock note
- industry deep dive
- thematic chartbook
- annual outlook
- capital markets outlook

Output: `template_brief.md`.

### Add `exhibit-architect`

Converts every strong conclusion into an exhibit.

Output: `exhibit_plan.md`.

### Add `source-governance-analyst`

Controls evidence hierarchy and claim audit.

Output: `source_registry.md`, `claim_audit.md`.

### Add `house-view-analyst`

Forms our own thesis rather than repeating broker views.

Output: `house_view.md`.

### Add `valuation-auditor`

Checks PE, target, scenario, share class, and forecast consistency.

Output: `valuation_audit.md`.

### Add `visual-layout-reviewer`

Reviews rendered PDF pages, not just TeX source.

Output: `visual_review.md`.

## Updated Equity Research Workflow

Recommended production flow:

1. Scope report type.
2. Template benchmark.
3. Source registry and claim audit.
4. House view.
5. Data collection and verification.
6. Exhibit plan.
7. Analysis and valuation.
8. LaTeX writing.
9. Rendered PDF visual review.
10. Institutional review.
11. Publish.

## What This Means for the PCB Report

The PCB report should use a hybrid of:

- BlackRock-style mega-force framing: AI capex and platform-chain migration.
- JPM Guide-style chartbook exhibits: customer-chain heatmaps, valuation dashboards, risk maps.
- Vanguard-style scenario discipline: observed vs forecast vs scenario vs rumor.
- JPM equity note-style stock pages: each core stock needs price, target, Q2 bridge, chain exposure, risk to thesis.
- AB-style catalyst timeline and market phase map.

It should not read like a collection of broker summaries. It should read like our own house view supported by auditable evidence and professional exhibits.
