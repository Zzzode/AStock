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
.venv/bin/python -m astock.cli backtest run 000001 --strategy ma_cross --start-date 2025-03-20 --end-date 2026-03-20 --capital 100000
```

For fixed-parameter rolling out-of-sample checks, require both windows:

```bash
.venv/bin/python -m astock.cli backtest run 000001 --strategy ma_cross --walk-forward-train-bars 120 --walk-forward-test-bars 20 --json
```

This is not parameter optimization or a continuous portfolio simulation. Treat it as a required robustness check, not proof of a tradable edge.

When evaluating a predeclared set of strategy parameters, use a JSON array of parameter objects. The engine records every candidate's training result, chooses a parameter set using only the preceding training window, then evaluates that set in the disjoint test window:

```bash
.venv/bin/python -m astock.cli backtest run 000001 --strategy ma_cross --walk-forward-train-bars 120 --walk-forward-test-bars 20 --parameter-sets-path parameters.json --selection-metric total_return --json
```

This produces `rolling_model_selection.v1`, including content fingerprints of the exact candidate set, strategy implementation, and execution engine. It does not establish that the search space was pre-registered, that the chosen metric is economically valid, or that a daily-bar result is tradable. Report its test folds, candidate set, and limitations; never collapse them into an investable recommendation. For frozen inputs, use the same flags with `backtest run-frozen` so the model-selection record is bound to the archived bars.

For a multi-asset paper portfolio, use `astock.capabilities.run_portfolio_backtest()` rather than combining single-stock results. It requires point-in-time target weights, an exchange trading calendar, a historical universe reference for every target date, and per-code daily `date/open/close/tradable` data. A formal reproducibility claim additionally requires a frozen `universe_snapshots` record for every target date: matching `as_of_date`, reference, archive ID, and actual member list; targets outside that list are rejected. Targets dated D execute at the next available global open; the simulator enforces cash, A-share lot sizes, costs, T+1 settlement, price-limit/halts no-fill states, and no synthetic fills through unavailable opens.

### Data-policy boundary

Read the current user configuration before selecting a data path. When
`market_data_mode=public_observation`, do not request a Tushare, JQData, Wind,
or other paid credential. Use the AKShare-backed `backtest freeze-public` /
`backtest run-frozen` research flow when available, keep the exact raw inputs
frozen, and label every result `research_only=true`. It can support repeatable
research discussion, but it cannot substantiate complete point-in-time
universe, corporate-action, halt, price-limit, delisting, capacity, or formal
paper-release claims. Do not report it as a formal reproducible portfolio
backtest.

Only when the user explicitly selects `licensed_eod` may the licensed replay
instructions below be used. In that mode, request the appropriate credential
only if it is already available to the runtime; never ask the user to enter a
terminal or paste a secret into the chat.

For the broad listing universe, build each snapshot with `astock.capabilities.build_tushare_listing_universe_snapshot(as_of_date=..., archive_directory=...)`, freeze its raw archive, then apply the strategy's source-labelled investability filters. Pass the resulting `source_archive_path` to `run_portfolio_backtest`; a matching source ID without loadable, hash-verified archive bytes is structurally labelled but not fully reproducible. A listing universe is not itself an investable universe: ST, suspension, liquidity, price-limit, board, and strategy restrictions remain separate controls.

For a subprocess boundary, use `.venv/bin/python -m astock.cli freeze-tushare-daily <TS_CODE> --start-date <DATE> --end-date <DATE> --archive-directory <DIR> --json` and `.venv/bin/python -m astock.cli freeze-tushare-universe --as-of-date <DATE> --archive-directory <DIR> --json`. Both fail closed without authorized credentials and never print them.

Do not claim a reproducible replay without `portfolio_backtest_sources.v1`: it must identify a frozen archive, an authorized data owner, and eligible sources for calendar, EOD bars, halts, price limits, corporate actions, and delistings. Public aggregation remains observation-only. To claim corporate-action or delisting coverage, use raw/unadjusted prices and supply source-labelled event records. A `delistings=covered` run must contain a source-labelled status record for every code; any code delisted during the replay requires an explicit cash-delisting settlement event, because status alone cannot value the holding. The engine supports only cash dividends, integer share distributions, and cash delisting settlements. Rights issues, mergers, spin-offs, and other non-standard events must block or use a dedicated event adapter.

Set `slippage_bps` and a conservative `max_participation_rate` with per-code daily `volume` when discussing capacity. If either is absent, the result must retain the corresponding execution/capacity limitation and cannot be evidence of a tradable edge.

### List Available Strategies

```bash
.venv/bin/python -m astock.cli backtest list --json
```

## Available Strategies

- `ma_cross` — MA Crossover (golden cross buy, death cross sell)
- `macd` — MACD Cross (histogram sign change)
- `rsi` — RSI Overbought/Oversold

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

## Saving Results

When producing a formal backtest report:

```text
workspace/backtest/<CODE>-<strategy>-<YYYYMMDD>/
├── report.tex        # LaTeX source (use report-brief.tex template)
├── report.pdf        # Compiled PDF
└── result.json       # Raw backtest output from Python
```

Use template: `.agents/templates/report-brief.tex`
Include: strategy parameters table, metrics table, trade log summary, commentary.
Compile: `.venv/bin/python -m astock.cli build-pdf workspace/backtest/<CODE>-<strategy>-<YYYYMMDD>/ --file report.tex`

For quick interactive replies: respond in conversation directly.

## Error Handling

| Scenario | Action |
|----------|--------|
| Invalid strategy name | List available strategies |
| Invalid date range | Fall back to most recent year |
| Insufficient data | Shorten range and explain |
| Capability adapter timeout | Shorten range and retry once |
