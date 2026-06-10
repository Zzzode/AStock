---
name: screen
description: Use when user needs to screen or filter stocks based on technical indicators, valuation factors, or custom criteria. Triggers on "find stocks", "screen for", "filter by", "which stocks have golden cross", "pick some stocks" or when user asks for stock selection based on specific conditions.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /screen - Smart Stock Screening

Execute screening using factors that actually exist in this repository.
Python returns only candidate stock snapshots and factor hit details — no composite scoring or ranking.

## Execution Flow

### Step 1: Parse Conditions

Common mappings:

| User Condition | Recommended Factors |
|---------------|-------------------|
| Undervalued, cheap | `pe_low,pb_low` |
| Deeply undervalued | `pe_very_low,pb_very_low` |
| MA golden cross | `ma5_cross_ma20` |
| Above 20-day MA | `ma20_above` |
| High volume | `high_volume` |
| Oversold bounce | `rsi_oversold,kdj_oversold` |

Do NOT use factor names that don't exist in this repository.

### Step 2: Call CLI

```bash
.venv/bin/python -m astock.cli screen --json --limit 10
.venv/bin/python -m astock.cli screen pe_low,pb_low,ma5_cross_ma20 --json --limit 10
.venv/bin/python -m astock.cli screen --codes 000001 --json
```

### Step 3: Parse Results and Complete Agent Reasoning

Key Python output fields:

- `requested_factors`
- `results[].matched_factors`
- `results[].matched_factor_count`
- `results[].factor_checks`
- `results[].data`

When replying to user, supplement with at minimum:

- Code and name
- Which conditions hit / which missed
- What the hit combination implies
- Risk points and invalidation conditions

If screening a single stock, frame it as a "condition hit snapshot" — not a "strategy match score".

## Error Handling

| Scenario | Action |
|----------|--------|
| Invalid factor name | List actually available factors |
| Full-market screen timeout | Reduce factor count or narrow scope |
| Single-stock screen fails | Fall back to `analyze` + valuation snapshot |
| Data source timeout | Use cache and note it |

## Related Files

- `src/python/astock/cli.py`
- `src/python/astock/stock_picker/screener.py`
- `src/python/astock/stock_picker/factors.py`
