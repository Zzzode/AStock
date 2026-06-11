# A-Share Investment Research and Market Intelligence System

An intelligent A-share investment research and market intelligence system powered by AI agents. Skills trigger automatically via natural language. Python handles market data fetching and deterministic computation; the AI agent handles research analysis, market interpretation, monitoring conclusions, and report generation.

## Design Purpose

This project has two primary objectives:

1. **Investment opportunity research and analysis for A-share market targets**
   - Identify and evaluate potential investment opportunities across individual stocks, sectors, concepts, and industry chains.
   - Support fundamental research, industry-chain research, policy/catalyst analysis, broker-report synthesis, valuation discussion, risk review, and opportunity tracking.
   - Produce structured research conclusions, watchlist candidates, monitoring points, and persistent LaTeX/PDF research deliverables.

2. **Market intelligence, board monitoring, and market analysis**
   - Monitor real-time and near-real-time market conditions, including prices, technical signals, turnover, volume-price behavior, sector/concept movement, fund flows, and market breadth.
   - Analyze market-board conditions through technical analysis, capital-flow analysis, sector rotation, abnormal movement detection, and alert rules.
   - Help users understand what is moving, why it may be moving, and which research opportunities should be tracked further.

### System Boundary

- This is **not** an automated trading, order execution, or brokerage integration system.
- The system does **not** place orders, route orders, manage broker execution, or operate as an OMS/EMS.
- Trading-related terms in user questions are interpreted as investment research, opportunity evaluation, market monitoring, paper portfolio tracking, or risk analysis unless the user explicitly asks for external actions.
- "Order" and "order flow" in market-analysis contexts refer to market-side data such as order book, quote depth, large trades, active buy/sell flow, and capital-flow signals, not user brokerage orders.

## Runtime Model and Python Boundary

This repository is designed to run **inside an AI agent environment** such as Claude Code or Codex.

- The AI agent conversation is the user interface.
- Skills and agent role files are the orchestration layer.
- Python is a capability kernel for agents and skills, not a human-facing application.

### Python Capability Contract

Python must provide deterministic, structured capabilities only:

- Fetch market, research, configuration, memory, and monitoring data.
- Compute indicators, screen factors, backtest technical signals, build data packets, and compile PDFs.
- Return JSON-serializable dictionaries or data objects suitable for agent reasoning.
- Never be the final analysis voice for the user; the AI agent performs interpretation, synthesis, and final communication.
- Preserve source, timestamp, quality, warning, and fallback metadata for data used in user-facing conclusions.

Preferred Python integration path:

```python
from astock import capabilities
```

Current shell commands such as `.venv/bin/python -m astock.cli quote 000001 --json` are **machine adapters** for skills that need a subprocess boundary. They are not the product UI and should remain thin wrappers over `astock.capabilities`.

### Engineering Rules

- Put reusable business logic in `src/python/astock/services/`, domain modules, or `src/python/astock/capabilities.py`.
- Keep `src/python/astock/cli.py`, `api.py`, and subcommand files as thin adapters only.
- Do not add interactive Python prompts, terminal menus, dashboards, or human-facing UI flows.
- Do not duplicate orchestration logic in CLI/API adapters.
- New skills should call the capability kernel directly when possible; when shell execution is simpler, call CLI adapters with `--json`.
- Python output should be data packets with explicit `data_quality`, `warnings`, and `error` fields where applicable.

## Foundation Capability Rules

Top-level agents and skills should use the following foundation capabilities when they produce research or market-monitoring conclusions:

1. **Data provenance**
   - Use `astock.capabilities.create_data_provenance_record()` for source records and `combine_data_provenance_records()` for derived packets.
   - Every material market, fundamental, report, or monitoring data packet should expose `source`, `timestamp`, `quality_tier`, `fallback_path`, `warnings`, and `errors`.
   - If live data degrades to delayed, cached, or partial data, disclose that quality tier in the agent conclusion.

2. **Market event normalization**
   - Use `astock.capabilities.build_market_event_packet()` to convert quote, screen, signal, sector, fund-flow, alert, news, or policy payloads into canonical market events.
   - Agents should reason over event type, subject, severity, direction, metrics, context, tags, and quality instead of parsing ad hoc strings.
   - Market monitoring should distinguish observation from conclusion: Python emits events; agents explain why they matter.

3. **Research opportunity ledger**
   - Use `create_research_entry()`, `list_research_entries()`, `record_research_observation()`, and `update_research_status()` for investment opportunity lifecycle tracking.
   - Material conclusions should include thesis, targets, catalysts, risks, monitoring triggers, invalidation conditions, source references, and data quality.
   - Follow-up observations should update the ledger when triggers fire, evidence changes, or a thesis is invalidated.

## Language Policy

- **English first**: All code, comments, commit messages, skill definitions, and internal documentation must be in English.
- **Chinese output OK**: User-facing reports, analysis conclusions, and conversational replies may be in Chinese when the user communicates in Chinese.

## Quick Start

```bash
# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python

# Initialize database
.venv/bin/python -m astock.cli init-db

# Use natural language directly in Claude Code / Codex
# No separate Python UI is needed — the AI agent IS the user interface
```

## Usage

### Natural Language (Recommended)

Talk to the agent naturally — skills trigger automatically:

```
User: Is Ping An Bank worth tracking as an investment opportunity?
Agent: Let me run a multi-expert collaborative analysis...
[Calls Python to fetch data]
- Python returns shared data packet
- Agent combines market, technical, risk, and contrarian perspectives

User: Find me some undervalued stocks with golden cross signals
Agent: Screening stocks with your criteria...
[Calls Python capability adapter]

User: Backtest the MA signal on Ping An Bank
Agent: Running MA crossover backtest...
[Calls Python capability adapter]
```

### Slash Commands

```
/quote 000001           # Quote lookup
/analyze 000001         # Technical analysis
/screen --limit 20      # Smart stock screening
/team 000001            # Multi-expert collaboration
```

## Skills

| Skill | Function | Natural Language Trigger Examples |
|-------|----------|----------------------------------|
| /team | Multi-expert collaborative analysis | "Is X worth tracking?" / "Is X a good opportunity?" |
| /equity-research | Institutional research report production | "Write a research report" / "Industry chain analysis" |
| /quote | Real-time quote lookup | "What's the price of X?" / "Latest quote" |
| /analyze | Technical analysis | "Analyze X technicals" / "Any signals on X?" |
| /screen | Smart stock screening | "Find me some stocks" / "Screen for value" |
| /backtest | Strategy backtesting | "Backtest MA strategy" |
| /recommend | Personalized recommendations | "Recommend some stocks for me" |
| /monitor | Stock monitoring & alerts | "Watch this stock" / "Start monitoring" / "Alert history" |
| /config | Configuration management | `/config style` |
| /portfolio | Paper portfolio and position tracking | "My positions" / "Record X shares" / "Portfolio risk" |
| /reports | Research report collection & archiving | "Collect reports on X" / "Download research reports" / "收集研报" |
| /evolve | Internal control & system evolution | "Audit agents" / "System health check" / "What's not working?" |

## Agent Team Workflow

When you ask about investment opportunities or market-monitoring conclusions, the system collaborates automatically:

```
User input: "Is Ping An Bank worth tracking as an investment opportunity?"
    ↓
Agent parses intent, identifies stock code and question type
    ↓
Calls Python capability adapter to fetch data:
└── .venv/bin/python -m astock.cli team 000001 --json --question "..."
    ↓
Agent reasons over shared data packet:
├── Reads summary / packet / data_quality / warnings directly
├── Market Agent: Interprets market momentum and position
├── Fundamental/Policy Agent: Supplements with filings, earnings, policy info
├── Risk Agent: Reviews downside scenarios, invalidation points, and monitoring triggers
└── Contrarian Agent: Provides counterarguments
    ↓
Outputs: research conclusion, opportunity rating, tracking triggers, risk warnings, contrarian arguments
```

Constraints:

- `team` returns the shared data packet only — does not output final research conclusions directly
- `screen` returns candidate snapshots and factor hit details only
- `recommend` returns user preferences and candidate pool data — agent makes final selection

## User Feedback Loop

After analysis, you can provide feedback on results:

```
Agent: Was this analysis helpful? You can provide feedback:
- "Worked out well" — reinforces this type of research conclusion or monitoring trigger
- "Not accurate" — adjusts future analysis weights
```

Record feedback:
```bash
.venv/bin/python -m astock.cli team-feedback 000001 --action watch_buy --outcome good --strategy ma_cross --note "Tracked after signal, follow-up result met expectations"
```

## Project Structure

```
src/python/astock/          # Python capability layer (core)
├── capabilities.py         # Agent/skill capability kernel
├── cli.py                  # Machine adapter for JSON subprocess calls
├── data_provenance/        # Source, freshness, quality, fallback metadata
├── market_event/           # Canonical market-monitoring event model
├── research/               # Research opportunity lifecycle ledger
├── quote/                  # Quote service
├── analysis/               # Technical analysis
├── stock_picker/           # Stock screener
├── backtest/               # Backtest engine
├── recommend/              # Recommendation system
└── monitor/                # Monitoring service

.agents/
├── team/                   # Shared subagent role definitions (reusable across skills)
│   ├── README.md           # Roster overview + usage guide
│   ├── market-analyst.md
│   ├── fundamental-analyst.md
│   ├── industry-analyst.md
│   ├── risk-analyst.md
│   ├── contrarian-analyst.md
│   ├── data-collector.md
│   ├── data-verifier.md
│   ├── report-collector.md
│   ├── report-analyzer.md
│   ├── valuation-modeler.md
│   ├── latex-writer.md
│   ├── reviewer.md
│   └── internal-control.md
├── templates/              # Shared LaTeX templates
│   ├── preamble.tex        # IB-style formatting (all reports)
│   ├── report-brief.tex    # Lightweight (team/analyze/backtest/recommend)
│   └── report-main.tex     # Full research report (equity-research)
└── skills/                 # Skill = orchestration logic (which roles, what order)
    ├── team/skill.md
    ├── equity-research/    # Deep research orchestration
    │   ├── skill.md
    │   ├── checklists/
    │   └── references/
    ├── quote/skill.md
    ├── analyze/skill.md
    ├── screen/skill.md
    ├── backtest/skill.md
    ├── recommend/skill.md
    ├── monitor/skill.md
    ├── config/skill.md
    ├── portfolio/skill.md
    ├── reports/skill.md
    ├── evolve/skill.md
    └── agent-resilience/skill.md

workspace/                  # All research outputs (LaTeX → PDF)
├── team/<CODE>-<YYYYMMDD>/          # Quick decision reports
├── research/<topic>-<YYYYMMDD>/     # Deep equity research
├── reports/<sector>/<YYYYMMDD>/     # Archived broker research reports
├── backtest/<CODE>-<strat>-<YYYYMMDD>/ # Backtest reports
└── recommend/<YYYYMMDD>/            # Recommendation reports

data/                       # Runtime data (mostly gitignored)
├── config/default.json     # User preferences
└── stocks.db               # SQLite database
```


## Skill File Conventions

Each skill is an executable instruction file:
- `description` field is used for natural language intent matching
- `<SUBAGENT-STOP>` directive prevents nested invocation
- Clear execution flow and Python capability invocation patterns

### Skill Copy Synchronization Policy

The repository keeps two runtime skill trees:

- `.agents/skills/` is the shared agent prompt source for Claude-style runtimes.
- `.codex/skills/` is the Codex runtime mirror.

For any behavior, workflow, command, or foundation-capability change:

- Update both copies in the same change set.
- Keep paired skill files byte-identical except for required path/name casing differences.
- Prefer concise examples in `SKILL.md` / `skill.md`; do not create separate skill README files.
- Verify drift before finishing:

```bash
cmp -s .agents/skills/quote/skill.md .codex/skills/quote/SKILL.md
cmp -s .agents/skills/analyze/skill.md .codex/skills/analyze/SKILL.md
cmp -s .agents/skills/screen/skill.md .codex/skills/screen/SKILL.md
cmp -s .agents/skills/team/skill.md .codex/skills/team/SKILL.md
cmp -s .agents/skills/monitor/SKILL.md .codex/skills/monitor/SKILL.md
```

## Document Format Policy

All persistent reports and analysis documents MUST be written in LaTeX and compiled to PDF.

- **Engine**: XeLaTeX (for CJK support)
- **Shared preamble**: `.agents/templates/preamble.tex`
- **Brief template**: `.agents/templates/report-brief.tex` (for team/analyze/backtest/recommend)
- **Full template**: `.agents/templates/report-main.tex` (for equity-research deep reports)
- **Compile**: `.venv/bin/python -m astock.cli build-pdf <directory-or-tex-file>`

Scope:
- Final deliverables (team reports, analysis reports, backtest summaries, recommendations) → `.tex` → `.pdf`
- Quick terminal outputs (quote, screen, monitor) remain JSON — they are not documents
- Intermediate data files (data packets, verified tables) stay as `.md` or `.json`
- Interactive conversational replies go directly to terminal — no LaTeX for chat

## Development Guidelines

- Python code goes in `src/python/astock/`
- Python code is a capability layer for agents and skills; it is not a standalone user interface.
- Expose reusable operations through `astock.capabilities`; keep CLI/API wrappers thin and machine-readable.
- Skills are instruction files guiding agent behavior
- All user-facing operations are done through the AI agent — no separate Python UI is needed
- **English first** for all code and internal docs; Chinese OK for user-facing output
