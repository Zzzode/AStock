---
name: backtest
description: Use when user needs to backtest trading strategies, evaluate strategy performance, analyze historical trading results, or compare different strategies. Triggers on "backtest X strategy", "how does this strategy perform", "MA strategy historical results", "test X strategy on Y stock", "strategy backtest".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /backtest - Strategy Backtesting

Backtest a specified strategy on a specified stock's historical data.

## Parameters

Required:

- Stock code
- Strategy name

Optional:

- `--start-date`
- `--end-date`
- `--capital`

If key parameters are missing, ask the user a brief clarifying question directly.

## Invocation

```bash
.venv/bin/python -m astock.cli backtest 000001 --strategy ma_cross --start-date 2025-03-20 --end-date 2026-03-20 --capital 100000
```

## Available Strategies

- `ma_cross`
- `macd`

## Key Output Metrics

- Total return
- Annualized return
- Maximum drawdown
- Sharpe ratio
- Trade count
- Win rate
- Profit/loss ratio

Don't just paste numbers. Add at minimum:

- What market conditions this strategy suits best
- Whether the drawdown is acceptable
- Any obvious flaws

## Error Handling

| Scenario | Action |
|----------|--------|
| Invalid strategy name | List available strategies |
| Invalid date range | Fall back to most recent year |
| Insufficient data | Shorten range and explain |
| CLI timeout | Shorten range and retry once |
