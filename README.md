# A-Share Investment Research and Market Intelligence System

Agent Team-first infrastructure for A-share investment opportunity research, market-board monitoring, technical analysis, capital-flow analysis, alerts, and research report production.

The system is designed for two workflows:

- **Investment opportunity research**: stocks, sectors, concepts, industry chains, catalysts, valuation, risks, broker reports, and research deliverables.
- **Market intelligence and monitoring**: real-time or near-real-time prices, technical signals, sector movement, market breadth, abnormal moves, alerts, and follow-up tracking.

This is **not** an automated trading, broker order-routing, OMS, or EMS system. "Order flow" refers to market-side data such as order book, quote depth, large trades, active buy/sell flow, and capital-flow signals.

## Capabilities

- Quote lookup with data-quality handling
- Multi-expert opportunity analysis via Agent Skills
- Technical analysis: MA, MACD, KDJ, RSI, support/resistance context
- Stock screening and personalized candidate pools
- Technical signal backtesting
- Watchlist monitoring, alerts, and alert history
- Paper portfolio and position tracking
- Broker-report collection and institutional-style equity research reports
- LaTeX/PDF report generation

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e src/python

.venv/bin/python -m astock.cli init-db
```

Use natural language in Claude Code / Codex, or call the Python CLI directly.

## Common Commands

```bash
# Opportunity analysis data packet
.venv/bin/python -m astock.cli team 000001 -q "Is this worth tracking as an investment opportunity?" --json

# Real-time quote
.venv/bin/python -m astock.cli quote 000001

# Technical analysis
.venv/bin/python -m astock.cli analyze 000001 -d 100

# Stock screening
.venv/bin/python -m astock.cli screen --limit 10

# Technical signal backtest
.venv/bin/python -m astock.cli backtest run 000001 --strategy ma_cross

# Candidate recommendation pool
.venv/bin/python -m astock.cli recommend generate --user default

# Monitoring status
.venv/bin/python -m astock.cli alert status
```

## Agent Skills

| Skill | Purpose |
|-------|---------|
| `/team` | Multi-expert investment opportunity analysis |
| `/equity-research` | Institutional research report production |
| `/quote` | Real-time quote lookup |
| `/analyze` | Technical analysis |
| `/screen` | Stock screening |
| `/backtest` | Technical signal backtesting |
| `/recommend` | Personalized candidate pools |
| `/monitor` | Watchlist and alerts |
| `/portfolio` | Paper portfolio and position tracking |
| `/reports` | Broker-report collection and archiving |
| `/config` | User preference and style configuration |
| `/evolve` | Agent and prompt quality audit |

Agent behavior, system boundaries, and report policies are defined in [AGENTS.md](AGENTS.md).

## Architecture

```text
Natural language / CLI / REST API
  -> Agent Skills and orchestration
  -> Python capability layer
  -> SQLite, config, workspace outputs
```

Core Python modules live in `src/python/astock/`:

- `quote/`, `analysis/`, `stock_picker/`, `backtest/`
- `monitor/`, `recommend/`, `portfolio/`, `memory/`
- `services/`, `storage/`, `config/`, `utils/`

Persistent outputs are written under `workspace/`. Runtime data lives under `data/`.

## REST API

```bash
uvicorn astock.api:app --reload --port 8000
```

OpenAPI docs: `http://localhost:8000/docs`

## Development

```bash
source .venv/bin/activate
cd src/python

pytest astock/ -v --cov=astock
ruff check astock/
black --check astock/
mypy astock/
```

## Documentation

- [AGENTS.md](AGENTS.md) - primary agent prompt and project instructions
- [docs/user-guide.md](docs/user-guide.md) - user guide
- [docs/plans/](docs/plans/) - design and implementation notes

## License

MIT License
