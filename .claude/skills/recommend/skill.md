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

Use the repository's real capability adapters:

```bash
cat data/config/default.json
.venv/bin/python -m astock.cli feedback --json
```

If no historical feedback exists:

- Continue with default config
- Explicitly tell user: "No historical feedback available — recommendations are based on default style and current market data"

### Step 2: Call Recommendation Capability Adapter

Use the current JSON subprocess adapter:

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

**When producing a formal recommendation report:**

Write LaTeX to:

```text
workspace/recommend/<YYYYMMDD>/
├── report.tex        # LaTeX source (use report-brief.tex template)
└── report.pdf        # Compiled PDF
```

Use template: `.agents/templates/report-brief.tex`
Include: user profile summary, candidate table with factor hits, per-stock reasoning, risk notes.
Compile: `.venv/bin/python -m astock.cli build-pdf workspace/recommend/<YYYYMMDD>/ --file report.tex`

**For quick interactive replies (default):** respond in conversation directly.

In either case, don't just list a table. Add at minimum:

- Why it might suit the user's current style
- Which factors and price/industry constraints support it
- What risks would invalidate this judgment

## Prediction Tracking

Every recommendation is a falsifiable forecast. After presenting a recommendation, the skill SHOULD close the loop: record a structured price prediction, periodically auto-verify it against actual prints, and feed the resulting accuracy statistics back into how subsequent candidates are weighted.

### Step A — Record a prediction after recommending

After giving a concrete recommendation (with a code and entry view), record a structured prediction so it can be scored later. `DIRECTION` is `bullish` / `bearish` / `neutral` (not `up`/`down`).

Minimal form:

```bash
.venv/bin/python -m astock.cli predict <code> <bullish|bearish|neutral> <entry_price>
```

Preferred form with full trade structure (use the numbers from the recommendation):

```bash
.venv/bin/python -m astock.cli predict 002463 bullish 147.00 \
  --target-price 160.00 \
  --stop-loss 140.00 \
  --horizon 30 \
  --confidence 0.6 \
  --thesis "matched_factors:breakout,volume; risk:stop 140" \
  --json
```

Notes:

- Pass `--json` to capture `prediction_id`, `deadline`, etc. Keep `--thesis` short but traceable (which factors, which risks).
- Set `--target-price` and `--stop-loss` to the levels actually cited to the user; never invent tighter numbers just to make the bet "safer" to score.
- For `neutral` / watch-list calls, still record with `--confidence` lowered and no target — an explicit "no edge" prediction is worth scoring too.

### Step B — Periodically verify pending predictions

Run auto-verification to settle predictions whose horizon has elapsed. Safe to run repeatedly; it only scores predictions past their deadline.

```bash
.venv/bin/python -m astock.cli verify-predictions
```

Add `--json` when piping into other tooling. Schedule this (cron, scheduled task, or a periodic skill pass) rather than running it inline on every recommendation — it is a batch operation over the whole pending set.

### Step C — Feed accuracy stats back into weighting

Consult aggregate accuracy before weighting factors and confidence in new recommendations:

```bash
.venv/bin/python -m astock.cli prediction-stats            # human-readable
.venv/bin/python -m astock.cli prediction-stats --json     # for programmatic use
.venv/bin/python -m astock.cli prediction-stats --code 002463 --json   # per-ticker view
```

Key fields: `accuracy`, `hit_rate`, `total_verified`, `pending`, plus correct/partial/incorrect breakdowns. Use them to:

- Down-weight factors / styles whose historical hit rate is weak.
- Calibrate `--confidence` on new predictions to the empirical accuracy band, not to gut feel.
- Flag tickers where the skill has been persistently wrong so the user is warned before re-recommending them.

If `total_verified` is 0 (cold start), say so to the user and rely on factor screening as usual — the feedback signal bootstraps as Step B settles predictions.

## Error Handling

| Scenario | Action |
|----------|--------|
| No feedback profile | Continue with default config |
| Recommend capability adapter fails | Retry once; on failure, explain the failure reason |
| No results | Relax price or style constraints and retry |
| Config file missing | Fall back to CLI default config |

## Related Files

- `src/python/astock/capabilities.py`
- `src/python/astock/cli.py` — JSON subprocess adapter
- `src/python/astock/recommend/recommender.py`
- `data/config/default.json`
