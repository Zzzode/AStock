# A-Share Agent Team Trading Analysis System

An intelligent stock analysis system powered by AI agents. Skills trigger automatically via natural language. Python handles data fetching and deterministic computation; the AI agent handles analysis, reasoning, and conclusion generation.

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
# No separate CLI needed — the AI agent IS the user interface
```

## Usage

### Natural Language (Recommended)

Talk to the agent naturally — skills trigger automatically:

```
User: Is Ping An Bank a good buy right now?
Agent: Let me run a multi-expert collaborative analysis...
[Calls Python to fetch data]
- Python returns shared data packet
- Agent combines market, technical, risk, and contrarian perspectives

User: Find me some undervalued stocks with golden cross signals
Agent: Screening stocks with your criteria...
[Calls Python screen command]

User: Backtest the MA strategy on Ping An Bank
Agent: Running MA crossover backtest...
[Calls Python backtest command]
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
| /team | Multi-expert collaborative analysis | "Should I buy X?" / "Is X a good entry?" |
| /equity-research | Institutional research report production | "Write a research report" / "Industry chain analysis" |
| /quote | Real-time quote lookup | "What's the price of X?" / "Latest quote" |
| /analyze | Technical analysis | "Analyze X technicals" / "Any signals on X?" |
| /screen | Smart stock screening | "Find me some stocks" / "Screen for value" |
| /backtest | Strategy backtesting | "Backtest MA strategy" |
| /recommend | Personalized recommendations | "Recommend some stocks for me" |
| /monitor | Stock monitoring & alerts | "Watch this stock" / "Start monitoring" / "Alert history" |
| /config | Configuration management | `/config style` |
| /portfolio | Portfolio management | "My positions" / "Buy X shares" / "Portfolio risk" |
| /reports | Research report collection & archiving | "Collect reports on X" / "Download research reports" / "收集研报" |
| /evolve | Internal control & system evolution | "Audit agents" / "System health check" / "What's not working?" |

## Agent Team Workflow

When you ask about stock trading decisions, the system collaborates automatically:

```
User input: "Is Ping An Bank a good buy right now?"
    ↓
Agent parses intent, identifies stock code and question type
    ↓
Calls Python script to fetch data:
└── .venv/bin/python -m astock.cli team 000001 --json --question "..."
    ↓
Agent reasons over shared data packet:
├── Reads summary / packet / data_quality / warnings directly
├── Market Agent: Interprets market momentum and position
├── Fundamental/Policy Agent: Supplements with filings, earnings, policy info
├── Risk Agent: Adjusts position sizing and stop-loss/take-profit
└── Contrarian Agent: Provides counterarguments
    ↓
Outputs: decision recommendation, risk warnings, contrarian arguments
```

Constraints:

- `team` returns the shared data packet only — does not output trading conclusions directly
- `screen` returns candidate snapshots and factor hit details only
- `recommend` returns user preferences and candidate pool data — agent makes final selection

## User Feedback Loop

After analysis, you can provide feedback on results:

```
Agent: Was this analysis helpful? You can provide feedback:
- "Worked out well" — reinforces this type of recommendation
- "Not accurate" — adjusts future analysis weights
```

Record feedback:
```bash
.venv/bin/python -m astock.cli team-feedback 000001 --action watch_buy --outcome good --strategy ma_cross --note "Executed, returns met expectations"
```

## Project Structure

```
src/python/astock/          # Python capability layer (core)
├── cli.py                  # CLI entry point (includes build-pdf)
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
- Clear execution flow and Python CLI invocation patterns

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
- Skills are instruction files guiding agent behavior
- All operations are done through the AI agent — no separate CLI needed
- **English first** for all code and internal docs; Chinese OK for user-facing output
