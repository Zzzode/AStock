---
name: agent-resilience
description: Core resilience capabilities for all agents - pre-execution checks, retry strategies, self-healing, and graceful degradation. Automatically included in all agent prompts. Also covers environment/data-source preflight checks before quote, analyze, screen, team, or recommend.
---

# Agent Resilience Protocol

This is an execution checklist, not a conceptual manifesto. All agents handle problems in this order.

## 0. Pre-execution Check (Preflight)

Before depending on live quotes or external data, run a quick check:

```bash
ls -la .venv/bin/python data data/stocks.db
```

Also assess:

- Does `data/config/default.json` exist?
- Does the command likely need network access?
- Is the request time-sensitive ("latest", "now", "today")?

**Decision rules:**

- Local environment complete, no fresh external data needed → proceed directly
- Local environment complete, request depends on live market data → prepare for network execution
- Data source clearly unavailable → prepare degradation path

**Recommended degradation paths:**

- `quote` fails → switch to daily data and valuation snapshot from `analyze`
- `screen` fails → switch to single-stock evaluation or reduce factors
- `team` fails → keep multi-agent but share a single degraded data packet

## 1. Classify the Error

Categorize failures into four types:

- Network / data source errors
- Parameter errors
- Permission / sandbox errors
- Code or logic errors

## 2. Retry Rules

| Error Type | Action |
|-----------|--------|
| Network timeout | Retry up to 3 times with exponential backoff |
| Data source anomaly | Retry up to 2 times; then switch to backup source or degrade |
| Parameter error | Fix parameter and retry immediately |
| Permission / sandbox error | Do NOT blindly retry; request network access or elevated permissions per environment |

## 3. Degradation Priority Order

1. Complete real-time quotes
2. Degraded snapshot
3. Daily technical analysis
4. Cache / historical records

Principles:

- Partial data > no data
- Explicit degradation > pretending completeness
- Limited conclusions > empty conclusions

## 4. Permission Strategy

When a critical command fails due to sandbox network restrictions:

- Request network access / elevated execution directly
- Do NOT spin repeatedly inside the sandbox

## 5. Output Requirements

When using a degraded path, must state:

```text
⚠️ Degradation note: Due to <reason>, this run uses <degraded approach>.
Confidence adjustment: <original> -> <current>
```

## 6. Memory & Reuse

Only consider writing to memory or creating a new skill when a problem is recurring AND the repository genuinely needs persistent knowledge.

Do NOT auto-expand skills just because of one ordinary failure.

## 7. Pre-completion Checklist

- Did I run the preflight check?
- Did I classify the error type?
- Did I retry a reasonable number of times?
- Did I request elevation when appropriate?
- Did I explicitly note degradation and confidence adjustments?
