---
name: alert
description: Use when user needs to start or stop monitoring service, check monitoring status, or view historical alert records. Triggers on "start monitoring", "stop monitoring", "monitoring status", "view alerts", "alert history", "what alerts fired".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /alert - Monitoring & Alert Management

Manage the stock monitoring service. Supports starting, stopping, and viewing historical alerts.

## Usage

```
/alert <command> [options]
```

## Commands

| Command | Description | Example |
|---------|------------|---------|
| `start` | Start monitoring service | `/alert start` |
| `stop` | Stop monitoring service | `/alert stop` |
| `status` | View monitoring status | `/alert status` |
| `history` | View alert history | `/alert history` |
| `history <code>` | View alerts for specific stock | `/alert history 000001` |

## Examples

### Start Monitoring

```
/alert start

Monitoring service started
Scan interval: 60s
Monitored stocks: 5
```

### Stop Monitoring

```
/alert stop

Monitoring service stopped
```

### View Status

```
/alert status

Monitoring Service Status
┌─────────────────────────────────────────┐
│  Status: Running                         │
│  Scan interval: 60s                      │
│  Monitored stocks: 5                     │
│  Today's alerts: 3                       │
│  Started at: 2026-03-08 09:30:00         │
└─────────────────────────────────────────┘
```

### View Alert History

```
/alert history

Alert History (last 10)
┌──────────────────────────────────────────────────────────────────┐
│  Time            Stock           Signal          Description      │
├──────────────────────────────────────────────────────────────────┤
│  03-08 10:15    Ping An Bank    MACD Cross Up   DIF crossed DEA  │
│  03-08 09:45    Kweichow Moutai RSI Oversold   RSI below 30     │
│  03-07 14:30    Wuliangye       MACD Cross Down DIF crossed DEA  │
└──────────────────────────────────────────────────────────────────┘
```

## Alert Channels

When monitoring triggers, alerts can be sent via:

- `terminal` — Terminal output (default)
- `notify` — System notification

Set alert channel via `/watch add` command.

## How It Works

1. After service starts, periodically scans stocks in the watch list
2. Uses SignalScanner to detect technical signals
3. On signal detection, sends alerts via AlertEngine
4. Alert records are saved to the database

## Notes

- Monitoring only runs during trading hours (9:30-11:30, 13:00-15:00)
- Recommend starting before market open
- Scan interval is configurable

## Related Files

- `src/python/astock/cli.py` — Python CLI entry point
- `src/python/astock/monitor/monitor_service.py` — Monitoring service
- `src/python/astock/monitor/scanner.py` — Signal scanner
- `src/python/astock/monitor/alert_engine.py` — Alert engine

## Error Handling

| Scenario | Action |
|----------|--------|
| Service fails to start | Check port conflict; notify user |
| No alert history | Inform user no alerts have fired |
| Service already running | Show status; don't restart |
| Database read fails | Use in-memory data and notify |
