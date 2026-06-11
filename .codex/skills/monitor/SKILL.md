---
name: monitor
description: Use when user needs to manage stock monitoring — add/remove watch items, set price or signal conditions, start/stop the monitoring service, check status, or view historical alerts. Triggers on "watch this stock", "add monitor", "set alert for", "notify me when price hits X", "start monitoring", "stop monitoring", "alert history", "what alerts fired", "view watch list".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /monitor - Stock Monitoring & Alerts

Unified skill for managing stock watch lists, running the monitoring service, and viewing alert history.

## Watch List Management

### Add Watch Item

```bash
.venv/bin/python -m astock.cli watch add <CODE> --signals "macd,rsi" --channels terminal
```

### Remove Watch Item

```bash
.venv/bin/python -m astock.cli watch remove <CODE>
```

### View Watch List

```bash
.venv/bin/python -m astock.cli watch list --json
```

### Condition Syntax

Supported conditions (`--cond` parameter):

| Condition | Description | Example |
|-----------|------------|---------|
| `price>X` | Price above X | `--cond "price>100"` |
| `price<X` | Price below X | `--cond "price<50"` |
| `change_percent>X` | Gain exceeds X% | `--cond "change_percent>5"` |
| `change_percent<X` | Loss exceeds X% | `--cond "change_percent<-3"` |
| `volume>X` | Volume exceeds X | `--cond "volume>1000000"` |

Multiple conditions (comma-separated):

```bash
.venv/bin/python -m astock.cli watch add 000001 --cond "price>10,change_percent>3"
```

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

## Alert History

```bash
.venv/bin/python -m astock.cli alert history --json
.venv/bin/python -m astock.cli alert history 000001 --json
```

## Alert Channels

- `terminal` — Terminal output (default)
- `notify` — System notification

## How It Works

1. User adds stocks to the watch list with signal/price conditions
2. Monitoring service scans watch list periodically during trading hours (9:30-11:30, 13:00-15:00)
3. SignalScanner detects technical signals matching conditions
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

- `src/python/astock/cli.py` — CLI entry (alert + watch commands)
- `src/python/astock/monitor/monitor_service.py` — Monitoring service
- `src/python/astock/monitor/watch_cli.py` — Watch management CLI
- `src/python/astock/monitor/scanner.py` — Signal scanner
- `src/python/astock/monitor/alert_engine.py` — Alert engine
