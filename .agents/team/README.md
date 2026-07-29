# Agent Team Roster

This directory contains reusable subagent role definitions. Skills in `.agents/skills/` reference these roles by name to compose their workflows.

## Roles

| Role | File | Description |
|------|------|-------------|
| Market Analyst | `market-analyst.md` | Discretionary market structure, auction, relative-strength, and price-volume acceptance assessment |
| Market Regime Analyst | `market-regime-analyst.md` | Market-state classification from breadth, liquidity, volatility, and leadership |
| Sector Rotation Analyst | `sector-rotation-analyst.md` | Sector/theme relative strength, participation, catalysts, and crowding |
| Short-Term Trader | `short-term-trader.md` | Conditional 1-10 trading-day catalyst, cohort, auction and liquidity research setups |
| Ultra-Short Tactical Trader | `ultra-short-tactical-trader.md` | Conditional 1-3 day leader, catalyst, auction and limit-ecology research setups |
| Event-Driven Institutional Analyst | `event-driven-institutional-analyst.md` | Verifies whether corporate, earnings, policy, supply or macro events change expectations |
| Counterparty Structure Risk Analyst | `counterparty-structure-risk-analyst.md` | Binding gate for float, supply, liquidity, corporate-action, and unsupported participant assumptions |
| Swing Trend Analyst | `swing-trend-analyst.md` | Conditional 2-12 week structure, leadership, earnings and supply-demand assessment |
| Portfolio Manager | `portfolio-manager.md` | Investment-committee decision, allocation research plan, and portfolio risk budget |
| Quant Risk Modeler | `quant-risk-modeler.md` | Concentration, scenario, methodology, and model-risk review |
| Execution & Liquidity Analyst | `execution-liquidity-analyst.md` | Tradability, T+1, price-limit, suspension, and liquidity review |
| Compliance Officer | `compliance-officer.md` | Research-only boundary, source disclosure, conflict, and compliance review |
| Fundamental Analyst | `fundamental-analyst.md` | Valuation, earnings, operations, order flow |
| Industry Analyst | `industry-analyst.md` | TAM, competitive landscape, supply chain, policy, macro |
| Supply Chain Analyst | `supply-chain-analyst.md` | Upstream/downstream relationships, customer-chain evidence, revenue exposure, earnings bridge |
| Growth Earnings Modeler | `growth-earnings-modeler.md` | High-growth/AI/order/unit/ASP earnings precision model before valuation |
| Risk Analyst | `risk-analyst.md` | Risk matrix, ESG/compliance, Devil's Advocate, stress tests, position sizing |
| Contrarian Analyst | `contrarian-analyst.md` | Counterarguments, failure scenarios, bear case construction |
| Data Collector | `data-collector.md` | Structured financial and market data gathering |
| Data Verifier | `data-verifier.md` | Cross-verify all data against official sources |
| Report Collector | `report-collector.md` | Collect sell-side broker research reports, output structured catalog |
| Report Analyzer | `report-analyzer.md` | Synthesize broker reports into consensus matrix, divergences, blind spots |
| Valuation Specialist | `valuation-specialist.md` | Runs the standalone valuation skill and owns valuation model + audit artifacts |
| Valuation Modeler | `valuation-modeler.md` | PE/PEG/PS/DCF models, three-tier targets, scenario analysis |
| LaTeX Writer | `latex-writer.md` | Professional IB-style LaTeX/PDF report production |
| Reviewer | `reviewer.md` | Generic chapter/research quality gate aligned to R0-R4 review cycles |
| Research Report Reviewer | `research-report-reviewer.md` | Full equity-research review workflow owner for evidence, model, draft, render/compliance, and final IC sign-off |
| Internal Control | `internal-control.md` | System quality audit, prompt review, feedback patterns, sync verification |
| Template Benchmark Analyst | `template-benchmark-analyst.md` | Selects the institutional report archetype before drafting |
| Exhibit Architect | `exhibit-architect.md` | Converts conclusions into evidence-led charts, tables, and decision exhibits |
| Source Governance Analyst | `source-governance-analyst.md` | Controls source hierarchy, claim audit, and valuation eligibility |
| House View Analyst | `house-view-analyst.md` | Separates AStock's own thesis from broker consensus |
| Valuation Auditor | `valuation-auditor.md` | Independently audits valuation arithmetic and false precision |
| Visual Layout Reviewer | `visual-layout-reviewer.md` | Reviews rendered PDFs for readability, clipping, overlap, and exhibit integrity |

### Skill-specific companion

`exhibit-format-reviewer.md` is the dedicated companion for the
`/exhibit-format-reviewer` skill. It is intentionally invoked by that skill
rather than registered as a generic desk role; it has publication-blocking
format and numerical-consistency authority within its narrow exhibit scope.

## Usage by Skills

| Skill | Roles Used |
|-------|-----------|
| `/team` | market-regime-analyst, market-analyst, fundamental-analyst, industry-analyst, risk-analyst, data-verifier, contrarian-analyst, report-collector, report-analyzer; expands to sector-rotation-analyst, short-term-trader, swing-trend-analyst, portfolio-manager, quant-risk-modeler, execution-liquidity-analyst, and compliance-officer only when the request and data support them |
| `/market-desk` | market-regime-analyst, sector-rotation-analyst, data-verifier, market-analyst, ultra-short-tactical-trader or short-term-trader, swing-trend-analyst, event-driven-institutional-analyst, fundamental-analyst, industry-analyst, counterparty-structure-risk-analyst, execution-liquidity-analyst, quant-risk-modeler, risk-analyst, contrarian-analyst, portfolio-manager, compliance-officer |
| `/equity-research` | report-collector, report-analyzer, data-collector, data-verifier, industry-analyst, supply-chain-analyst via `/supply-chain-research`, growth-earnings-modeler via `/growth-earnings-model`, valuation-specialist via `/valuation`, risk-analyst, latex-writer, research-report-reviewer via `/research-report-review`, reviewer for chapter-level checks |
| `/analyze` | market-analyst (when producing formal report) |
| `/backtest` | latex-writer (when producing formal report) |
| `/recommend` | fundamental-analyst, risk-analyst, report-analyzer (subset for candidate evaluation) |
| `/reports` | report-collector (discovery + full-text download orchestration) |
| `/evolve` | internal-control (+ reads all other role files for audit) |
| `/exhibit-format-reviewer` | exhibit-format-reviewer (publication-blocking LaTeX exhibit format and numerical-consistency review) |

## Role File Format

Each role file follows this structure:

```markdown
# Role Name
## Identity (who you are, one paragraph)
## Capabilities (what you can do)
## Input Contract (what you expect to receive)
## Output Contract (structured output format)
## Constraints (what you must NOT do)
```

## How Skills Reference Roles

In a skill's orchestration section:
```
Dispatch agent with prompt from: .agents/team/<role-name>.md
```

The skill is responsible for:
- Deciding WHICH roles to activate
- Defining the ORDER of execution
- Specifying how outputs are MERGED
- Setting the OUTPUT FORMAT for the final deliverable

## Trading Desk Decision Rights

The trading-desk roles provide research and conditional plans only. They never place, route, amend, or manage orders.

### Team-only strategy contract

Every trading strategy, market opportunity, security selection, portfolio
add/reduce/hold/exit, or return-target question is a team decision. No role may
publish a standalone trading answer. The desk lead first distributes one shared,
completed evidence packet; the final synthesis names the participating roles,
their dissent, and every binding veto.

Evidence completion precedes deliberation. `data-collector` must obtain every
field needed by the requested horizon from current source-labelled records;
`data-verifier` independently reconciles it and returns any conflict or absent
field for repair. Analysts do not turn a source defect into a market conclusion,
an indicator proxy, or an “insufficient-data” rationale. If a required source
cannot be acquired after the defined source escalation, the desk releases no
decision for that horizon and keeps collection open.

- `data-verifier` can block actionable use of stale, conflicting, unverified, or materially incomplete evidence.
- `risk-analyst`, `quant-risk-modeler`, `execution-liquidity-analyst`, `counterparty-structure-risk-analyst`, and `compliance-officer` can issue a veto within their stated contracts.
- `portfolio-manager` must treat every veto as binding and can output only `WATCH` or `REJECT` until the blocker is remediated.
- A user's high risk tolerance does not waive data quality, legal, liquidity, or portfolio-risk constraints.
- MA, MACD, KDJ, RSI, crossover, and overbought/oversold labels are prohibited as entries, exits, screeners, alerts, gates, or risk permissions. They cannot replace timestamped market-structure, catalyst, liquidity, risk, or provenance evidence.

The role file is responsible for:
- The agent's identity and expertise
- Input/output contracts
- Quality standards and constraints
