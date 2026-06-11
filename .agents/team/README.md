# Agent Team Roster

This directory contains reusable subagent role definitions. Skills in `.agents/skills/` reference these roles by name to compose their workflows.

## Roles

| Role | File | Description |
|------|------|-------------|
| Market Analyst | `market-analyst.md` | Market structure, volume-price dynamics, momentum, position assessment |
| Fundamental Analyst | `fundamental-analyst.md` | Valuation, earnings, operations, order flow |
| Industry Analyst | `industry-analyst.md` | TAM, competitive landscape, supply chain, policy, macro |
| Risk Analyst | `risk-analyst.md` | Risk matrix, ESG/compliance, Devil's Advocate, stress tests, position sizing |
| Contrarian Analyst | `contrarian-analyst.md` | Counterarguments, failure scenarios, bear case construction |
| Data Collector | `data-collector.md` | Structured financial and market data gathering |
| Data Verifier | `data-verifier.md` | Cross-verify all data against official sources |
| Valuation Modeler | `valuation-modeler.md` | PE/PEG/PS/DCF models, three-tier targets, scenario analysis |
| LaTeX Writer | `latex-writer.md` | Professional IB-style LaTeX/PDF report production |
| Reviewer | `reviewer.md` | Quality gate with S/A/B severity, publication blocking authority |

## Usage by Skills

| Skill | Roles Used |
|-------|-----------|
| `/team` | market-analyst, fundamental-analyst, risk-analyst, contrarian-analyst (+ expansion pool) |
| `/equity-research` | data-collector, data-verifier, industry-analyst, valuation-modeler, risk-analyst, latex-writer, reviewer |
| `/analyze` | market-analyst (when producing formal report) |
| `/backtest` | latex-writer (when producing formal report) |
| `/recommend` | fundamental-analyst, risk-analyst (subset for candidate evaluation) |

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
