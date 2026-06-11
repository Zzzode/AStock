---
name: team
description: Use when user asks whether a stock is worth buying, selling, holding, or entering now, wants timing or position advice, or needs a multi-factor A-share decision with bull/bear arguments and risk assessment. Trigger on phrases like "should I buy", "good entry?", "hold or sell?", "position sizing", or "comprehensive analysis". Do not use for simple quote requests or pure technical-indicator interpretation when the user is not asking for a broader decision.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /team - Multi-Agent Collaborative Decision

Perform multi-role collaborative analysis on a single stock. Output actionable trading conclusions, contrarian arguments, and risk warnings. Save results to `data/sessions/`.

## Goal

- Preserve genuine multi-agent workflow
- Prefer native Claude Code Team / Agent Team capabilities
- If native Team API is unavailable or team creation fails, auto-fallback to `spawn_agent`
- No user intervention needed to switch modes; `/team` selects the runtime mode automatically

## Mode Selection

### Mode A: Native Team API (Preferred)

If the current runtime supports Claude Code Team / Agent Team:

1. Create `stock-<CODE>` team
2. Create core members
3. Send shared data packet to members
4. Collect and merge results

### Mode B: `spawn_agent` Fallback

If native Team API is unavailable, fails, or is unstable:

1. Create compatible members via `spawn_agent`
2. Send shared data packet and role tasks to each subagent
3. Wait for critical members if needed
4. Merge output in the same structure as native Team mode

## Core Principles

1. Call Python `team` backend first to generate the shared data packet, then dispatch role tasks
2. Subagents consume shared data first — avoid redundant data fetching
3. Only allow a role to fetch additional data when it genuinely lacks critical information
4. Each role must explicitly state whether it used a degraded path
5. Final report must include bull/bear arguments, key price levels, position sizing, and risk warnings
6. Multi-agent adds perspectives and arbitrates conflicts — it does NOT repeat base data fetching

## Step 1: Parse Task

Extract from user input:

- Stock code or stock name
- Question type: buy / sell / hold / position / scalp / swing / long-term / comprehensive

If the stock code cannot be determined, ask the user a brief clarifying question directly.

## Step 2: Preflight Check

Check first:

- Does `.venv/bin/python` exist?
- Does `data/stocks.db` exist?
- Can `astock.cli team` execute?
- Does the request need network access for live quotes?
- Does the request need official filings / policy information?

If local data pipeline is broken:

- Try network fetch once
- On failure, degrade to available daily data / cache / history
- Must note degradation and confidence adjustment in the final report

## Step 3: Generate Shared Data Packet

Use the unified entry point:

```bash
.venv/bin/python -m astock.cli team <CODE> --json --days 120 --question "<USER_QUESTION>"
```

This is Team's single data entry point. It returns:

- `summary` (packet status only — NOT a trading conclusion)
- `recommended_roles`
- `orchestration`
- `packet`
- `data_quality`
- `warnings`
- `session_path`

On success:

1. Read `orchestration.active_agent_ids` and `orchestration.merge_order`
2. Use `packet` as shared input for all roles
3. Note: Python provides no buy/sell advice; `summary` is not a decision
4. Multi-agent is responsible for full conclusion generation (bull/bear, position, risk, contrarian)

On failure with structured JSON:

1. Read `warnings`, `error`, `session_path`
2. Determine if limited conclusions can be drawn from degraded data
3. If error is network/sandbox, request elevation per `agent-resilience` rules

Only fall back to split commands if `astock.cli team` is unavailable or returns a clearly incomplete packet:

Team-Lead fetches base data first to reduce redundant requests:

```bash
.venv/bin/python -m astock.cli quote <CODE> --json
.venv/bin/python -m astock.cli analyze <CODE> --json --days 120
.venv/bin/python -m astock.cli screen --codes <CODE> --json
.venv/bin/python -m astock.cli feedback --json
cat data/config/default.json
```

Supplement when needed:

- Official filings / earnings reports
- Industry policy / regulatory information

Shared data packet must contain at minimum:

- Stock code and name
- Quote data
- Technical indicators and signals
- Screen snapshot and factor hits
- User style / risk preferences
- Data quality tier: `full_realtime` / `snapshot_degraded` / `daily_only` / `cache_only`
- Known gaps

## Step 4: Launch Core Team

Do NOT have all roles redundantly analyze base data from the start.

Read `recommended_roles` first:

- Keep at least `core`
- If Python backend suggests `short_term` / `swing` / `long_term` / `sentiment`, expand accordingly
- If user question is more specific than the data packet, prioritize user intent

Core team (prompt files in `.agents/team/`):

| Role | Prompt |
|------|--------|
| `market-analyst` | `.agents/team/market-analyst.md` |
| `fundamental-analyst` | `.agents/team/fundamental-analyst.md` |
| `industry-analyst` | `.agents/team/industry-analyst.md` |
| `risk-analyst` | `.agents/team/risk-analyst.md` |
| `contrarian-analyst` | `.agents/team/contrarian-analyst.md` |
| `report-collector` | `.agents/team/report-collector.md` |
| `report-analyzer` | `.agents/team/report-analyzer.md` |

### Report Collection Integration

After shared data packet is ready, dispatch `report-collector` in parallel with other core roles:
- Input: stock code/name + sector + last 90 days
- Once catalog returns, feed it to `report-analyzer`
- Report Analyzer output feeds into the final merge: Street consensus view, divergence points, and blind spots supplement the team's own analysis

If report collection fails (no reports found, network error), degrade gracefully — note "no sell-side coverage" and proceed with internal analysis only.

## Step 5: Dynamic Expansion

Expand by user intent — do NOT launch all roles by default:

| Trigger Intent | Additional Roles |
|---------------|-----------------|
| Scalp, day trade, ultra-short | `scalper`, `momentum-trader` |
| Swing, 3-10 days | `swing-trader` |
| Long-term, value, buy-and-hold | `value-investor` |
| Sentiment, hot topics, fund flow | `sentiment-analyst` |

Only expand when the question genuinely requires it — avoid unnecessary data requests and wait time.

If `recommended_roles` is only `core`, do NOT force expansion.

## Step 6: Role Task Template

All roles use the same minimal task structure:

### Unified Requirements

- Read shared data packet first
- Prioritize `orchestration`, `packet`, `data_quality`, `warnings`
- If shared data is sufficient, do NOT re-fetch the same data
- If critical data is missing, one supplementary fetch is allowed
- If supplementary fetch fails, provide a degraded conclusion — never return empty

### Unified Output Structure

```text
Role: <ROLE>
Conclusion: <one-sentence conclusion>
Evidence:
- ...
- ...
Risks:
- ...
Key Levels:
- Support:
- Resistance:
Confidence: <0-100>
Degradation: <none / specific reason>
```

## Step 7: Team API vs `spawn_agent` Compatibility

### Native Team API Path

- Use native team / agent team to create team and members
- Send `astock.cli team --json` shared data packet to members
- Collect member outputs and merge

### `spawn_agent` Fallback Path

- Create one clearly-bounded subagent per role
- Each subagent only provides its own role conclusion — no cross-role overlap
- Team-lead handles final merge and report writing
- Avoid multiple subagents modifying the same file
- Subagents do NOT execute `quote/analyze/screen` by default unless team-lead identifies shared data gaps

## Step 8: Merge Rules

Final output must include:

1. Executive summary
2. Bull arguments
3. Bear arguments
4. Technical assessment
5. Fundamental / policy assessment
6. Street consensus (from report-analyzer: broker ratings, target prices, divergences, blind spots)
7. Key price levels
8. Position sizing recommendation
9. Risk warnings
10. Degradation notes
11. Consistency / conflict points with data packet quality constraints

When role opinions conflict:

- Do NOT force unify into a single-sided view
- State the conflict explicitly
- Indicate which side has stronger evidence

## Step 9: Save Report

Save final report as LaTeX to:

```text
workspace/team/<CODE>-<YYYYMMDD>/
├── report.tex        # LaTeX source (use report-brief.tex template)
├── report.pdf        # Compiled PDF
└── packet.json       # Raw data packet from Python
```

Use the shared brief template: `.agents/templates/report-brief.tex`

- Set `\reporttitle` to the stock name + code
- Set `\reportdate` to today's date
- Keep report concise (3-5 pages)
- Compile: `.venv/bin/python -m astock.cli build-pdf workspace/team/<CODE>-<YYYYMMDD>/ --file report.tex`

If Python `team` already generated `session_path`, save `packet.json` from that data.

Reports should be concise and actionable — avoid empty platitudes.

## Confidence & Degradation

Default baseline:

- Complete data, all roles active: `65-80`
- Daily data available but real-time degraded: subtract `5-10`
- Missing one of screening / fundamentals / policy: subtract `5-10`
- History cache only or obvious gaps: subtract `10-20`

Final report must explicitly state:

```text
⚠️ Degradation note: Due to <reason>, this analysis uses <approach>.
Confidence adjustment: <original> -> <current>
```

## Command Reference

```bash
.venv/bin/python -m astock.cli team <CODE> --json --days 120 --question "<USER_QUESTION>"
.venv/bin/python -m astock.cli quote <CODE> --json
.venv/bin/python -m astock.cli analyze <CODE> --json --days 120
.venv/bin/python -m astock.cli screen --codes <CODE> --json
.venv/bin/python -m astock.cli feedback --json
.venv/bin/python -m astock.cli memory recall --agent <NAME> --key <KEY> --json
cat data/config/default.json
```

## Prohibitions

- Do NOT assume native Team API is always available
- Do NOT bypass `astock.cli team --json` by having all roles redundantly fetch data
- Do NOT let all roles call the same data commands repeatedly
- Do NOT give one-sided conclusions without contrarian arguments
- Do NOT treat degraded data as if it were complete real-time market data
- Do NOT reference team-specific syntax that does not exist in the current repository
