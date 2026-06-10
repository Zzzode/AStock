---
name: recommend
description: Use when user needs personalized stock recommendations based on trading style, risk preference, investment strategy, or asks "recommend some stocks", "what stocks suit me", "suggestions based on my style". Triggers when user wants personalized investment suggestions.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /recommend - Personalized Recommendations

Generate personalized conclusions based on user configuration and candidate pool data.
Python returns only user preferences, screening context, and candidate stock data — no direct recommendations.

## Execution Flow

### Step 1: Read User Profile

Use the repository's real entry points:

```bash
cat data/config/default.json
.venv/bin/python -m astock.cli feedback --json
```

If no historical feedback exists:

- Continue with default config
- Explicitly tell user: "No historical feedback available — recommendations are based on default style and current market data"

### Step 2: Call Recommendation Command

Use the explicit subcommand:

```bash
.venv/bin/python -m astock.cli recommend generate --json --limit 5
```

With user-specified style or risk:

```bash
.venv/bin/python -m astock.cli recommend generate --json --style swing --risk moderate --limit 5
```

### Step 3: Parse Results

Focus on:

- `config_used`
- `selection_context`
- `candidates[].matched_factors`
- `candidates[].factor_checks`
- `candidates[].industry`
- `candidates[].data`

### Step 4: Output Recommendations

Don't just list a table. Add at minimum:

- Why it might suit the user's current style
- Which factors and price/industry constraints support it
- What risks would invalidate this judgment

## Error Handling

| Scenario | Action |
|----------|--------|
| No feedback profile | Continue with default config |
| Recommend command fails | Retry once; on failure, explain the failure reason |
| No results | Relax price or style constraints and retry |
| Config file missing | Fall back to CLI default config |

## Related Files

- `src/python/astock/cli.py`
- `src/python/astock/recommend/recommender.py`
- `data/config/default.json`
