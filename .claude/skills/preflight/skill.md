---
name: preflight
description: Use before quote, analyze, screen, team, or recommend when the task depends on current market data or external data sources. Checks environment, database, network/data-source availability, and chooses whether to proceed, request network access, or degrade.
---

# /preflight - Data & Environment Pre-check

Quick pre-check before depending on live quotes or external data. Reduces repeated failures in the main flow.

## Check Items

```bash
ls -la .venv/bin/python data data/stocks.db
```

When needed, also check:

- Does `data/config/default.json` exist?
- Does the command likely need network access?
- Is the request time-sensitive ("latest", "now", "today")?

## Decision Rules

- Local environment complete and no fresh external data needed: proceed directly
- Local environment complete but request depends on live market data: prepare for network execution
- Data source clearly unavailable: prepare degradation path

## Recommended Degradation Paths

- `quote` fails: switch to daily data and valuation snapshot from `analyze`
- `screen` fails: switch to single-stock evaluation or reduce factors
- `team` fails: keep multi-agent but share a single degraded data packet

## Output

Pre-check conclusion should be concise:

- Whether environment is complete
- Whether network access is needed
- Available degradation options
