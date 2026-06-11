---
name: quote
description: Use when user asks for a stock's latest price, intraday change, volume, turnover, today's performance, or a current market snapshot. Trigger on phrases like "what's the price", "latest quote", "how did it do today", "market snapshot", or "volume today". Do not use for technical analysis, indicator interpretation, or buy/sell decision questions.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /quote - Quote Lookup

Query the latest quote for a single stock, with explicit data quality disclosure.

## Execution Flow

### Step 1: Confirm Code

- 6-digit number: use directly
- Stock name: try common name-to-code mapping first
- If uncertain: ask user a brief clarifying question

### Step 2: Call Python Capability Adapter

Use the current JSON subprocess adapter:

```bash
.venv/bin/python -m astock.cli quote <CODE> --json
```

### Step 2b: Foundation Capability Example

When the quote is used as evidence in a user-facing conclusion, wrap it with
provenance and normalize any abnormal quote move into events:

```python
from astock import capabilities

quote_provenance = capabilities.create_data_provenance_record(
    source="astock.cli quote",
    quality_tier="realtime",  # map degraded snapshots to "snapshot"/"degraded"
)
quote_events = capabilities.build_market_event_packet(
    quote_payload,
    payload_type="quote",
    source="astock.cli quote",
)
```

### Step 3: Assess Data Quality

Differentiate in output:

- `full_realtime`: price, change%, volume, etc. are all complete
- `snapshot_degraded`: name/valuation available but order book fields are 0 or clearly missing
- `daily_only`: only daily or analytical data available — cannot provide reliable intraday snapshot

If degraded, must explicitly state "this is not a complete real-time snapshot".

### Step 4: Output

Include at minimum:

- Name and code
- Latest price / change %
- Volume or turnover
- One brief interpretation sentence

## Error Handling

| Scenario | Action |
|----------|--------|
| Code does not exist | Prompt user to confirm code |
| Data source timeout | Retry once; on failure, note real-time quote unavailable |
| Outside trading hours | Note this is last trading day's data |
| Order book fields missing | Treat as degraded data — do not pretend it's complete real-time |
