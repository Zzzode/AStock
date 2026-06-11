# A-Share Agent Team Trading Analysis System

An **Agent Team-first** A-share analysis and decision-making project.  
Users ask natural language questions and the system automatically orchestrates multiple expert agents: fetching data, dividing analysis, cross-discussing, outputting recommendations, and continuously learning user preferences.

Skills and code are not the end product — they are the execution infrastructure for the Agent Team.

## Product Goals

- Agent-led: Orchestrator Agent coordinates the expert team
- Multi-expert collaboration: market, technical, risk, strategy, and style learning run in parallel
- Discussion before recommendations: generate multi-perspective conclusions first, then synthesize actionable advice
- Continuous personalization: update style profiles and recommendation parameters from user history
- Multi-entry: Agent Skills, Python CLI, and REST API share the same capability kernel

## Current Capabilities

- Quote lookup: real-time quotes + basic indicators
- Team analysis: shared data packet + agent-side reasoning and aggregated decisions
- Technical analysis: MA / MACD / KDJ / RSI signals
- Smart screening: candidate snapshots and factor hit details
- Strategy backtesting: strategy execution and performance metrics
- Monitoring & alerts: watch list + alert status/history
- Config & style: user preference management, style learning, personalized recommendations

## Agent Team Architecture

### Core Principles

1. **Agent first**: Users face an expert team, not individual commands
2. **Capability decoupling**: Agent orchestrates collaboration; Python provides deterministic capabilities
3. **Unified protocol**: structured output across modules for agent reasoning
4. **Evolvable**: can upgrade from single-agent to parallel review and debate mechanisms

### Layered Structure

1. **Interaction layer** (Agent Skills / Python CLI / REST API)  
2. **Agent orchestration layer** (Skills + subagent dispatch)  
3. **Capability execution layer** (`src/python/astock/*`)  
4. **Data & profile layer** (`data/*` + SQLite + user config)

### Entry Points

- **Agent Skills**: 10 skills — `team/equity-research/quote/analyze/screen/backtest/recommend/monitor/config/agent-resilience`
- **Python CLI**: full command set (`team/quote/analyze/screen/backtest/recommend/watch/alert/config`)
- **REST API**: `/quote`, `/analyze`, `/screen`, `/backtest`, `/recommend`, `/config`

## Installation

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python
```

## Quick Start

Full user documentation: [docs/user-guide.md](docs/user-guide.md)

### 1) Initialize

```bash
.venv/bin/python -m astock.cli init-db
```

### 2) Common Commands

```bash
# Team analysis
.venv/bin/python -m astock.cli team 000001 -q "Is now a good entry?" -d 120

# Quote
.venv/bin/python -m astock.cli quote 000001

# Technical analysis
.venv/bin/python -m astock.cli analyze 000001 -d 100

# Team feedback
.venv/bin/python -m astock.cli team-feedback 000001 -a watch_buy -o good -s ma_cross -n "Bounced after pullback, good timing"

# Stock screening
.venv/bin/python -m astock.cli screen --limit 10

# Backtesting
.venv/bin/python -m astock.cli backtest run 000001 --strategy ma_cross

# Recommendations
.venv/bin/python -m astock.cli recommend generate --user default

# Config & style
.venv/bin/python -m astock.cli config style

# Alert status
.venv/bin/python -m astock.cli alert status
```

`team` analysis outputs stage progress: quote fetch, technical analysis, strategy screening, feedback profile loading, conclusion aggregation.
Result panel includes three "reasoning trace" explainable evidence items; if strategy screening times out, it auto-degrades to neutral rather than failing the entire run.

### 3) Agent Skills

| Skill | Function | Example |
|-------|----------|---------|
| `/team` | Multi-expert collaborative analysis | `/team 000001` |
| `/equity-research` | Institutional research reports | "Write a research report on X" |
| `/quote` | Real-time quote lookup | `/quote 000001` |
| `/analyze` | Technical analysis | `/analyze 000001` |
| `/screen` | Smart stock screening | `/screen --limit 10` |
| `/backtest` | Strategy backtesting | `/backtest 000001 --strategy ma_cross` |
| `/recommend` | Personalized recommendations | `/recommend` |
| `/monitor` | Stock monitoring & alerts | `/monitor watch add 000001` |
| `/config` | Config & style learning | `/config style` |

## Typical Collaboration Flow

1. User asks a question (e.g., "Is Ping An Bank a good entry now?")
2. Python `team --json` generates a unified shared data packet (no trading conclusions)
3. Orchestrator Agent decomposes tasks and dispatches relevant experts based on the packet
4. Experts provide bull/bear arguments, position sizing, and risk advice from the data packet
5. Orchestrator aggregates conflicting views and delivers the final recommendation
6. Learning module records user feedback, updates style profile and config

## Agent Team MVP

- `team` command: single request triggers multi-expert collaborative analysis
- Python `team` output protocol: `summary`, `packet`, `data_quality`, `warnings`, `orchestration`
- Python does NOT output `experts/decision` — agent side owns reasoning and decision-making
- Python `screen/recommend` output candidate data packets only — no scoring, ranking, or recommendation conclusions
- Skill side consumes `team --json` first, then scales via Team API / subagent expansion
- Feedback write-back: `team-feedback` records recommendation outcomes, influencing risk preferences and strategy weights

## REST API

```bash
uvicorn astock.api:app --reload --port 8000
```

After starting, visit `http://localhost:8000/docs` for OpenAPI documentation.

## Project Structure

```
.
├── .agents/skills/               # Agent team protocols and capability entries
│   └── equity-research/          # Deep research (prompts, templates, checklists)
│       └── templates/            # Shared LaTeX templates (preamble, brief, full)
├── src/python/astock/
│   ├── cli.py                    # Python CLI capability entry
│   ├── api.py                    # FastAPI capability service entry
│   ├── quote/ analysis/ storage/
│   ├── stock_picker/ backtest/
│   ├── monitor/ recommend/
│   ├── config/ learning/ portfolio/
│   └── utils/
├── workspace/                    # All research outputs (LaTeX → PDF)
│   ├── team/                     # Quick decision reports
│   ├── research/                 # Deep equity research (git-tracked)
│   ├── backtest/                 # Backtest reports
│   └── recommend/                # Recommendation reports
├── data/                         # Runtime data (SQLite, config)
└── docs/                         # Design docs
```

## Testing

```bash
source .venv/bin/activate
cd src/python
pytest astock/ -v --cov=astock
ruff check astock/
black --check astock/
mypy astock/
```

## Strategy Notes

- Available strategies: `ma_cross`, `macd`
- Python capability layer exposes available strategies via API `/strategies`

## License

MIT License
