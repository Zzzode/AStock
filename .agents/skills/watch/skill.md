---
name: watch
description: Use when user needs to add, remove, or view stock monitoring items with price or volume conditions. Triggers on "add monitor", "watch this stock", "set alert for", "notify me when price hits X", "remove monitor", "view watch list".
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /watch - Stock Watch Management

Manage the stock watch list. Supports adding, removing, and viewing monitored items.

## Usage

```
/watch <command> [options]
```

## Commands

| Command | Description | Example |
|---------|------------|---------|
| `add` | Add to watch list | `/watch add 000001 --cond "price>10"` |
| `remove` | Remove from watch list | `/watch remove 000001` |
| `list` | View watch list | `/watch list` |

## Examples

### Add Watch Item

```
/watch add 000001                          # Add Ping An Bank to watch list
/watch add 600519 --cond "price>1800"      # Watch Kweichow Moutai for price above 1800
/watch add 000858 --cond "change_percent>5"  # Watch Wuliangye for 5%+ gain
```

### Remove Watch Item

```
/watch remove 000001    # Remove Ping An Bank
/watch remove 600519    # Remove Kweichow Moutai
```

### View Watch List

```
/watch list    # Show all watch items
```

## Condition Syntax

Supported conditions (`--cond` parameter):

| Condition | Description | Example |
|-----------|------------|---------|
| `price>X` | Price above X | `--cond "price>100"` |
| `price<X` | Price below X | `--cond "price<50"` |
| `change_percent>X` | Gain exceeds X% | `--cond "change_percent>5"` |
| `change_percent<X` | Loss exceeds X% | `--cond "change_percent<-3"` |
| `volume>X` | Volume exceeds X | `--cond "volume>1000000"` |

Multiple conditions (comma-separated):

```
/watch add 000001 --cond "price>10,change_percent>3"
```

## Alert Channels

When watch triggers, alerts can be sent via:

- `terminal` — Terminal output (default)
- `notify` — System notification

```
/watch add 000001 --channel terminal --channel notify
```

## Output Format

### Watch Added

```
Watch added: Ping An Bank (000001)
  Condition: price > 10.00
  Channel: terminal
```

### Watch List

```
Current Watch List (3 items)
┌──────────────────────────────────────────────────────────────┐
│  Code     Name              Condition               Status   │
├──────────────────────────────────────────────────────────────┤
│  000001   Ping An Bank      price>10               Active   │
│  600519   Kweichow Moutai   change_percent>5       Active   │
│  000858   Wuliangye         price>150,volume>1M    Active   │
└──────────────────────────────────────────────────────────────┘
```

## Related Files

- `src/python/astock/monitor/watch_cli.py` — Watch management CLI
- `src/python/astock/storage/models.py` — Data model (WatchItem)

## Error Handling

| Scenario | Action |
|----------|--------|
| Invalid stock code | Prompt user to confirm code |
| Condition syntax error | Show correct syntax examples |
| Watch item already exists | Ask user whether to overwrite |
| Database write fails | Retry once; on failure, suggest trying later |
