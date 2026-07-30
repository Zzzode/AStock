---
name: config
description: Use when user needs to manage preferences, set trading style, risk level, or analyze and learn trading patterns from history. Triggers on "set style", "change config", "view config", "learn my trading style", "risk preference settings".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /config - Configuration Management

Manage the current user's trading preference configuration.

## Common Commands

```bash
.venv/bin/python -m astock.cli config show
.venv/bin/python -m astock.cli config set risk_level aggressive
.venv/bin/python -m astock.cli config set trading_style swing
.venv/bin/python -m astock.cli config set decision_cadence eod_preplanned
.venv/bin/python -m astock.cli config set market_data_mode public_observation
.venv/bin/python -m astock.cli config style
.venv/bin/python -m astock.cli config reset
```

## Configuration Source

Primary sources:

- `data/config/default.json`
- `src/python/astock/config/`
- `src/python/astock/learning/style_analyzer.py`

Do NOT reference TypeScript config files that don't exist in this repository.

## Configuration Items

| Item | Description |
|------|------------|
| `risk_level` | `conservative` / `moderate` / `aggressive` |
| `trading_style` | `day_trading` / `swing` / `trend_following` / `value_investing` |
| `decision_cadence` | `eod_preplanned` (default: review after close and publish next-session conditions) / `intraday_microstructure` (requires reproducible intraday evidence) |
| `max_positions` | Maximum number of positions |
| `position_size` | Single position size ratio |
| `min_price` | Minimum price filter |
| `max_price` | Maximum price filter |
| `default_capital` | Default capital amount |
| `default_strategy` | Default strategy |
| `market_data_mode` | `public_observation` (AKShare research and paper suggestions) / `licensed_eod` (optional licensed replay and formal-release controls) |

## Error Handling

| Scenario | Action |
|----------|--------|
| Config item doesn't exist | List available config items |
| Invalid config value | Show valid range |
| Insufficient historical data | Note style learning is unreliable |
| Config file corrupted | Fall back to default config |
