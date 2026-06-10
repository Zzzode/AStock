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
| /quote | Real-time quote lookup | "What's the price of X?" / "Latest quote" |
| /analyze | Technical analysis | "Analyze X technicals" / "Any signals on X?" |
| /screen | Smart stock screening | "Find me some stocks" / "Screen for value" |
| /backtest | Strategy backtesting | "Backtest MA strategy" |
| /recommend | Personalized recommendations | "Recommend some stocks for me" |
| /config | Configuration management | `/config style` |

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
├── cli.py                  # CLI entry point
├── quote/                  # Quote service
├── analysis/               # Technical analysis
├── stock_picker/           # Stock screener
├── backtest/               # Backtest engine
├── recommend/              # Recommendation system
└── monitor/                # Monitoring service

.agents/skills/             # Skill definition files
├── team/skill.md           # Multi-expert collaboration
├── quote/skill.md          # Quote lookup
├── analyze/skill.md        # Technical analysis
├── screen/skill.md         # Smart screening
├── backtest/skill.md       # Strategy backtesting
└── recommend/skill.md      # Personalized recommendations

data/                       # Data storage
├── team-feedback.json      # User feedback
└── sessions/               # Session records
```

## Skill File Conventions

Each skill is an executable instruction file:
- `description` field is used for natural language intent matching
- `<SUBAGENT-STOP>` directive prevents nested invocation
- Clear execution flow and Python CLI invocation patterns

## Development Guidelines

- Python code goes in `src/python/astock/`
- Skills are instruction files guiding agent behavior
- All operations are done through the AI agent — no separate CLI needed
- **English first** for all code and internal docs; Chinese OK for user-facing output
