---
name: portfolio
description: Use when user needs to manage their portfolio — view positions, record buy/sell trades, import trade history, check risk metrics, or reset portfolio. Triggers on "my positions", "portfolio", "buy X shares", "sell X shares", "import trades", "portfolio risk", "what am I holding", "how is my portfolio doing".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /portfolio - Portfolio Management

Manage paper trading portfolio: record buys/sells, track positions and P/L, assess risk.

## Commands

### Show Portfolio Overview

```bash
.venv/bin/python -m astock.cli portfolio show --json
```

### View Positions

```bash
.venv/bin/python -m astock.cli portfolio positions --json
```

### Buy

```bash
.venv/bin/python -m astock.cli portfolio buy 000001 500 --price 12.50 --json
```

If `--price` is omitted, uses latest real-time quote.

### Sell

```bash
.venv/bin/python -m astock.cli portfolio sell 000001 300 --price 13.20 --json
```

If `--price` is omitted, uses latest real-time quote.

### View Trade History

```bash
.venv/bin/python -m astock.cli portfolio trades --json
.venv/bin/python -m astock.cli portfolio trades 000001 --limit 10 --json
```

### Import Trades from CSV

```bash
.venv/bin/python -m astock.cli portfolio import /path/to/trades.csv --json
```

CSV format: `date,code,action,shares,price`

### Portfolio Risk Metrics

```bash
.venv/bin/python -m astock.cli portfolio risk --json
```

Returns: total value, position count, concentration risk, cash ratio, limit checks.

### Reset Portfolio

```bash
.venv/bin/python -m astock.cli portfolio reset --capital 200000 --json
```

## Integration with Other Skills

- After `/team` or `/recommend` analysis suggests a buy → user can execute via `portfolio buy`
- Trade history feeds into `config style` for trading style learning
- Risk metrics inform `/team` risk agent's position sizing recommendations

## Error Handling

| Scenario | Action |
|----------|--------|
| Insufficient cash for buy | Show available cash and suggest smaller position |
| No position for sell | Inform user of current holdings |
| CSV format error | Show expected column format |
| Price fetch fails | Ask user to provide price manually via `--price` |
