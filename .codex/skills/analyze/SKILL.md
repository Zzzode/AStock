---
name: analyze
description: Use when user asks for technical analysis of a stock, including MA, MACD, KDJ, RSI, golden cross, death cross, trend strength, support/resistance, or technical entry/exit signals from a chart perspective. Trigger on phrases like "technical analysis", "analyze X", "moving average", "MACD", "RSI", "golden cross", "death cross", or "trend outlook". Do not use for simple price lookup or broader buy/sell decision advice involving position sizing or multi-factor judgment.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /analyze - Technical Analysis

Perform technical analysis on a stock. Python provides raw data and signal detection. **You perform the dynamic reasoning and analysis.**

## Execution Flow

### Step 1: Call Python to Fetch Data

```bash
.venv/bin/python -m astock.cli analyze <CODE> --json --days 100
```

### Step 2: Read Output Data

Python output contains:

| Field | Description |
|-------|------------|
| `indicators` | Current technical indicator values |
| `prev_indicators` | Previous day's indicators (for comparison) |
| `signals` | Detected signals (type, current value, bias) |
| `signal_stats` | Signal statistics (bull/bear counts) |
| `history` | Recent analysis history |
| `feedback_stats` | User feedback statistics (success rate) |
| `quote` | Real-time quote |

### Step 3: Perform Reasoning Analysis

**You are responsible for genuine analysis reasoning — not template filling.**

Analysis points:
1. **Indicator interpretation** — What do current values mean? How do they compare to yesterday?
2. **Signal analysis** — Are detected signals reliable? Do they need confirmation from other indicators?
3. **Historical comparison** — Have similar signals appeared recently? What happened then?
4. **Feedback reference** — What's the user's success rate on similar signals?
5. **Risk assessment** — What are the potential risks?
6. **Action recommendation** — Provide specific recommendations with reasoning

### Step 4: Output Analysis Report

**When the user requests a saved report or the analysis feeds into a larger research flow:**

Write LaTeX to:

```text
workspace/analyze/<CODE>-<YYYYMMDD>/
├── report.tex        # LaTeX source (use report-brief.tex template)
└── report.pdf        # Compiled PDF
```

Use template: `.agents/templates/report-brief.tex`
Compile: `.venv/bin/python -m astock.cli build-pdf workspace/analyze/<CODE>-<YYYYMMDD>/ --file report.tex`

**For quick interactive replies (default):** respond in conversation directly, no file output.

Report must include:
- Market overview
- Technical indicator analysis (with tables)
- Signal interpretation (your reasoning, not predefined text)
- Comprehensive assessment
- Action recommendations
- Risk warnings

## Error Handling

| Scenario | Action |
|----------|--------|
| Capability adapter fails | Retry once; on failure, degrade with `--days 60` |
| JSON parse fails | Try regex extraction of key indicators |
| Invalid stock code | Prompt user to confirm code |
| Insufficient data | Note data gaps; continue analysis on available portion |

## Important Reminders

1. **You are the analyst** — Python only provides data; analysis and judgment are yours
2. **No templates** — Reason dynamically from actual data; never use predefined interpretation text
3. **Be logical** — Analysis must have a logical chain; conclusions must have evidence
4. **Stay objective** — Point out factors on both sides; never present only one direction
5. **Risk awareness** — All judgments have uncertainty; always note risks
