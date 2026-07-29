---
name: portfolio
description: Use when user needs to manage their portfolio — view positions, record buy/sell trades, audit strategy-plan governance, import trade history, check risk metrics, or reset portfolio. Triggers on "my positions", "portfolio", "buy X shares", "sell X shares", "import trades", "portfolio risk", "portfolio governance", "what am I holding", "how is my portfolio doing".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /portfolio - Portfolio Management

Manage paper trading portfolio: record buys/sells, track positions and P/L, assess risk.

Use this skill only for ledger operations and factual portfolio views. If the
user asks what to hold, add, reduce, exit, rotate into, or how to pursue a
return target, invoke `market-desk` and its compulsory desk team first. A
single portfolio role or a raw risk metric must never answer that strategy
question.

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
.venv/bin/python -m astock.cli portfolio buy 000001 500 --price 12.50 \
  --strategy-entry-id <research-entry-id> --ledger-path data/research-ledger.json \
  --entry-observed-at <ISO-8601-with-timezone> \
  --entry-evidence-ref entry-observation:<sha256-archive-id> \
  --entry-observation-archive-path <frozen-market-archive.json> \
  --restricted-list-path data/restricted-list.json --json
```

If `--price` is omitted, uses latest real-time quote.

Every new paper buy must bind to an already active, independently assured
market-desk strategy-plan entry. This remains paper-only and never sends a
broker order.

The command blocks a new buy without `--strategy-entry-id`. `unlinked_legacy`
is reserved for pre-existing or externally imported historical paper records;
those records are preserved for audit but cannot be described as
investment-committee-governed positions and cannot be increased through `buy`.

The strategy link alone is not an entry authorization. Every paper buy must
also record the timezone-aware confirmation time, at least one evidence reference
that includes the exact content-addressed observation archive ID, and the path
to that verified archive. The confirmation must occur after the plan becomes
active and before its review/time-stop boundary. The current restricted-list
authority must have a verified signature and must not restrict the target at
the moment the paper entry is recorded.

### Sell

```bash
.venv/bin/python -m astock.cli portfolio sell 000001 300 --price 13.20 \
  --exit-reason risk_reduce \
  --exit-observed-at <ISO-8601-with-timezone> \
  --exit-evidence-ref exit-observation:<sha256-archive-id> \
  --exit-observation-archive-path <frozen-market-archive.json> \
  --ledger-path data/research-ledger.json --json
```

If `--price` is omitted, uses latest real-time quote.

For a governed position, an exit/reduction must retain the strategy identity,
an explicit exit reason, and hash-verifiable frozen observation evidence. The
exit is permitted even if the plan has already been invalidated or expired: it
reduces risk and must not be held up by a new compliance clearance. Every
governed exit is marked as requiring a later lifecycle review; recording the
sell does not silently close or invalidate the strategy plan.

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

For factor, correlation, liquidity-capacity, and scenario stress gates, pass an auditable JSON context:

```bash
.venv/bin/python -m astock.cli portfolio risk --context risk-context.json --json
```

The context must provide per-code factor exposures and average daily turnover, pair keys such as `600460|688001` under `correlations`, and at least one factor-shock map under `stress_scenarios`. Factor inputs may only enter from an approved `portfolio-factor-risk-context.v1`: taxonomy version, approver, approval/effective timestamps, source references per classification and scenario, and shocks limited to classified factors are mandatory. Price history cannot infer factor exposure or stress scenarios. Missing structural inputs are blockers, never zero risk.

### Portfolio Governance

```bash
.venv/bin/python -m astock.cli portfolio governance --json
```

This checks each position's link to an active strategy plan with a passing
release assurance and retained, hash-verifiable paper-entry evidence. It reports
`governed`, `unlinked_legacy`, invalid links, and `entry_evidence_gap` positions
separately. It also lists governed exits whose `exit_id` has not yet been cited
by a later strategy lifecycle review; these exits keep the governance result
blocked until reviewed. A pass does not verify a live quote, fill, or realized
performance.

### Reset Portfolio

```bash
.venv/bin/python -m astock.cli portfolio reset --capital 200000 --json
```

## Integration with Other Skills

- After a formal market-desk plan is active → record a governed paper buy with its strategy entry ID. An ordinary `/team` or `/recommend` idea is not sufficient.
- Trade history feeds into `config style` for trading style learning
- Risk metrics inform `/team` risk agent's position sizing recommendations

## Error Handling

| Scenario | Action |
|----------|--------|
| Insufficient cash for buy | Show available cash and suggest smaller position |
| No position for sell | Inform user of current holdings |
| CSV format error | Show expected column format |
| Price fetch fails | Ask user to provide price manually via `--price` |
