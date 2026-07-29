---
name: monitor
description: Use when user needs to manage stock monitoring — add/remove watch items, set observable price, liquidity, or range conditions, start/stop the monitoring service, check status, or view historical alerts. Also covers scheduled/periodic patrols via the task scheduler (scheduler health, start daemon, run jobs). Triggers on "watch this stock", "add monitor", "set alert for", "notify me when price hits X", "start monitoring", "stop monitoring", "alert history", "what alerts fired", "view watch list", "scheduler status", "scheduled patrol", "run scheduler job". Never configure MA, MACD, KDJ, RSI, or crossover alerts.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /monitor - Stock Monitoring & Alerts

Unified skill for managing stock watch lists, running the monitoring service, and viewing alert history.

An alert is only an observation. If the user asks what an alert means for a
trade, position, strategy, add/reduce, or exit, escalate to `market-desk` for a
compulsory team decision after evidence completion; never infer action from the
monitoring role alone.

## Watch List Management

### Add Watch Item

```bash
.venv/bin/python -m astock.cli watch add <CODE> --signals "price_dislocation,volume_spike" --channels terminal
```

### Remove Watch Item

```bash
.venv/bin/python -m astock.cli watch remove <CODE>
```

### View Watch List

```bash
.venv/bin/python -m astock.cli watch list --json
```

### Observable Alert Types

The `--signals` parameter accepts comma-separated, reproducible market-structure alert types:

- `price_dislocation` — a large close-to-close move
- `range_expansion` — unusually wide session range
- `volume_spike` — turnover materially above the preceding 20-session median

Example:

```bash
.venv/bin/python -m astock.cli watch add 000001 --signals "range_expansion,volume_spike" --channels terminal
```

An alert is an observation, not a buy, sell, add, reduce, or risk-permission signal. It must be read with the catalyst, market regime, liquidity, and risk context.

## Service Lifecycle

### Start Monitoring

```bash
.venv/bin/python -m astock.cli alert start --json
```

### Stop Monitoring

```bash
.venv/bin/python -m astock.cli alert stop --json
```

### Check Status

```bash
.venv/bin/python -m astock.cli alert status --json
```

## Scheduled Patrols

monitor supports scheduled/periodic market patrols via the task scheduler. The scheduler runs registered jobs on a recurring schedule — e.g. periodic watch-list scans or market patrols during trading hours — so monitoring continues without a foreground terminal.

### Check Scheduler Health

```bash
.venv/bin/python -m astock.cli scheduler-status           # human-readable
.venv/bin/python -m astock.cli scheduler-status --json    # machine-readable
```

The same status is also reachable through the `scheduler` group:

```bash
.venv/bin/python -m astock.cli scheduler status --json
```

Output reports whether the daemon is `Running` and the number of registered jobs. `Running: False` with `Jobs: 0` means no patrols are scheduled.

### Manage the Scheduler Daemon

`scheduler` is a command group with three subcommands:

| Subcommand | Purpose |
|------------|---------|
| `scheduler start` | Start the scheduler daemon (`--foreground` default, or `--background`; `--json` for structured output) |
| `scheduler status` | Show scheduler status from saved state (`--json`) |
| `scheduler run-job <JOB_NAME>` | Manually trigger a single registered job by name (`--json`) |

Exact forms:

```bash
.venv/bin/python -m astock.cli scheduler start --foreground --json
.venv/bin/python -m astock.cli scheduler start --background --json
.venv/bin/python -m astock.cli scheduler status --json
.venv/bin/python -m astock.cli scheduler run-job <JOB_NAME> --json
```

Note: this version of the CLI exposes `start` / `status` / `run-job` only — there is no `list` / `add` / `remove` subcommand for managing job registrations; jobs are registered in code (see `src/python/astock/scheduler/`).

## Alert History

```bash
.venv/bin/python -m astock.cli alert history --json
.venv/bin/python -m astock.cli alert history 000001 --json
```

### Foundation Capability Example

When an alert fires, normalize it as a market event. If it relates to an active
research thesis, append the event as a ledger observation:

```python
from astock import capabilities

alert_event_packet = capabilities.build_market_event_packet(
    alert_payload,
    payload_type="alert",
    source="astock.cli alert",
)
capabilities.record_research_observation(
    entry_id,
    observation_type="alert_trigger",
    note="Monitoring alert fired for tracked thesis.",
    evidence=alert_event_packet,
    status_after="monitoring",
)
```

## Alert Channels

- `terminal` — Terminal output (default)
- `notify` — System notification

## How It Works

1. User adds stocks to the watch list with observable price/liquidity/range conditions
2. Monitoring service scans watch list periodically during trading hours (9:30-11:30, 13:00-15:00)
3. SignalScanner detects reproducible market-structure dislocations
4. AlertEngine dispatches alerts via configured channels
5. Alert records are saved to the database

## Error Handling

| Scenario | Action |
|----------|--------|
| Invalid stock code | Prompt user to confirm code |
| Condition syntax error | Show correct syntax examples |
| Watch item already exists | Ask user whether to overwrite |
| Service fails to start | Check port conflict; notify user |
| No alert history | Inform user no alerts have fired |
| Service already running | Show status; don't restart |
| Database read/write fails | Retry once; on failure, notify user |

## Related Files

- `src/python/astock/capabilities.py` — Agent capability kernel
- `src/python/astock/cli.py` — JSON subprocess adapter (alert + watch commands)
- `src/python/astock/monitor/monitor_service.py` — Monitoring service
- `src/python/astock/monitor/watch_cli.py` — Watch management CLI
- `src/python/astock/monitor/scanner.py` — Signal scanner
- `src/python/astock/monitor/alert_engine.py` — Alert engine
