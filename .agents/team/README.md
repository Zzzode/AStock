# Agent Team Roster

This directory contains reusable subagent role definitions. Skills in `.agents/skills/` reference these roles by name to compose their workflows.

## Roles

| Role | File | Description |
|------|------|-------------|
| Market Analyst | `market-analyst.md` | Market structure, volume-price dynamics, momentum, position assessment |
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

## Usage by Skills

| Skill | Roles Used |
|-------|-----------|
| `/team` | market-analyst, fundamental-analyst, risk-analyst, contrarian-analyst, report-collector, report-analyzer (+ expansion pool) |
| `/equity-research` | report-collector, report-analyzer, data-collector, data-verifier, industry-analyst, supply-chain-analyst via `/supply-chain-research`, growth-earnings-modeler via `/growth-earnings-model`, valuation-specialist via `/valuation`, risk-analyst, latex-writer, research-report-reviewer via `/research-report-review`, reviewer for chapter-level checks |
| `/analyze` | market-analyst (when producing formal report) |
| `/backtest` | latex-writer (when producing formal report) |
| `/recommend` | fundamental-analyst, risk-analyst, report-analyzer (subset for candidate evaluation) |
| `/reports` | report-collector (discovery + full-text download orchestration) |
| `/evolve` | internal-control (+ reads all other role files for audit) |

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

The role file is responsible for:
- The agent's identity and expertise
- Input/output contracts
- Quality standards and constraints
