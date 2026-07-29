---
name: team
description: Use when user asks for a multi-role A-share target analysis or target-aware portfolio review. Trigger on phrases like "worth tracking", "investment opportunity", "comprehensive analysis", "portfolio risk", "monitoring triggers", or "watchlist candidate". Route a whole-market trading plan, market regime, or sector-rotation request to `market-desk`, not this skill. Do not use for a simple quote request or a pure technical-indicator interpretation when the user is not asking for broader opportunity analysis.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /team - Multi-Agent Market and Opportunity Analysis

Perform multi-role collaborative analysis for a single A-share target or a target-aware portfolio review. Output evidence-labelled market context, opportunity research, conditional action plans, binding vetoes, monitoring triggers, contrarian arguments, and risk warnings. Save persistent research outputs only when their evidence quality supports follow-up.

When a target-aware request asks for a trading strategy, position action, or
return objective, run the same evidence-completion loop and minimum desk-team
review defined by `market-desk`; do not let the lighter target-research team
release a standalone trading answer.

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

1. Call the Python capability adapter first to generate the shared data packet, then dispatch role tasks
2. Subagents consume shared data first — avoid redundant data fetching
3. Only allow a role to fetch additional data when it genuinely lacks critical information
4. Each role must explicitly state whether it used a degraded path
5. Final report must include bull/bear arguments, key price levels, monitoring triggers, and risk warnings
6. Multi-agent adds perspectives and arbitrates conflicts — it does NOT repeat base data fetching
7. This is a research and decision-support workflow. No role places, routes, amends, or manages orders.
8. A data-quality, risk, quant-risk, execution-liquidity, or compliance `VETO` is binding. It can only produce `WATCH` or `REJECT` until remediated.

## Step 1: Parse Task

Extract from user input:

- Stock code or stock name
- Scope: `single_target` or `portfolio`
- Question type: opportunity research / watchlist tracking / market regime / sector rotation / short-term / swing / long-term / portfolio review / comprehensive

If the request is a whole-market trading plan, market regime, or sector-rotation task without a named target, invoke `market-desk` and stop this workflow. For `portfolio`, do not require a stock code only when the portfolio capability already supplies position data. If scope is `single_target` and the code cannot be determined, ask the user a brief clarifying question directly.

## Step 2: Preflight Check

Check first:

- Does `.venv/bin/python` exist?
- Does `data/stocks.db` exist?
- Can the Python capability adapter execute?
- Does the request need network access for live quotes?
- Does the request need official filings / policy information?

If local data pipeline is broken:

- Try network fetch once
- On failure, degrade to available daily data / cache / history
- Must note degradation and confidence adjustment in the final report

## Step 3: Generate Shared Data Packet

Build the whole-market observation packet first for every request. It is an observation packet, not a final recommendation:

```bash
.venv/bin/python -m astock.cli market-overview --json
```

The market packet must expose, or explicitly mark unavailable:

- observed timestamp, source, quality tier, warnings, and errors
- major-index and style-index movement
- breadth and price-limit participation
- turnover/liquidity context
- sector, concept, and ETF proxy observations where available

For `single_target` requests, then use the unified target capability adapter:

```bash
.venv/bin/python -m astock.cli team <CODE> --json --days 120 --question "<USER_QUESTION>"
```

The target adapter returns:

- `summary` (packet status only — NOT a final research conclusion)
- `recommended_roles`
- `orchestration`
- `packet`
- `data_quality`
- `warnings`
- `session_path`

On target-adapter success:

1. Read `orchestration.active_agent_ids` and `orchestration.merge_order`
2. Use `packet` as shared input for all roles
3. Note: Python provides no final recommendation; `summary` is not a conclusion
4. Multi-agent is responsible for full conclusion generation (bull/bear, monitoring triggers, risk, contrarian)

On target-adapter failure with structured JSON:

1. Read `warnings`, `error`, `session_path`
2. Determine if limited conclusions can be drawn from degraded data
3. If error is network/sandbox, request elevation per `agent-resilience` rules

For whole-market requests, do not fabricate target-level factors. Keep unavailable breadth, sector, concept, or ETF fields explicitly unavailable. For target requests, only fall back to split capability adapters if `astock.cli team` is unavailable or returns a clearly incomplete packet:

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

The combined shared packet must contain at minimum:

- Stock code and name
- Quote data
- Timestamped daily price-volume observations and a recent bar history
- Screen snapshot and factor hits
- User style / risk preferences
- Data quality tier: `full_realtime` / `snapshot_degraded` / `daily_only` / `cache_only`
- Known gaps

For whole-market scope, omit target-specific fields rather than substituting a stale single-stock snapshot. For portfolio scope, add only positions, cash, cost basis, constraints, and horizon that the user supplied or the portfolio capability returned.

Foundation post-processing:

- Preserve or create data provenance records for material quote, price-volume, screen, report, and policy inputs.
- Normalize abnormal price, volume, sector, fund-flow, alert, news, and policy observations through `astock.capabilities.build_market_event_packet()`.
- Resolve stock-to-sector/theme/industry-chain context through `astock.capabilities.resolve_market_subject_context()` when relationship context affects the thesis.
- Detect board-monitoring anomalies through `astock.capabilities.build_fund_flow_anomaly_packet()` when the packet includes fund-flow, volume, rotation, or risk-release fields.
- Use canonical market events as shared evidence for role agents; do not ask each role to parse raw strings independently.

Minimal foundation example:

```python
from astock import capabilities

quote_provenance = capabilities.create_data_provenance_record(
    source="astock.cli team.packet.quote",
    quality_tier="realtime",
)
structure_provenance = capabilities.create_data_provenance_record(
    source="astock.cli team.packet.analysis",
    quality_tier="snapshot",
)
packet_provenance = capabilities.combine_data_provenance_records(
    [quote_provenance, structure_provenance],
    source="team.shared_packet",
)
quote_events = capabilities.build_market_event_packet(
    packet.get("quote", {}),
    payload_type="quote",
    source="team.shared_packet",
)
market_context = (
    capabilities.resolve_market_subject_context(packet["code"])
    if packet.get("code")
    else {"found": False, "warnings": ["missing_code"]}
)
anomaly_packet = capabilities.build_fund_flow_anomaly_packet(
    packet.get("fund_flow") or packet.get("quote", {}),
    source="team.shared_packet",
)
```

## Step 4: Launch Core Team

Do NOT have all roles redundantly analyze base data from the start.

Read `recommended_roles` for target-specific expansion, then select registered roles from the following decision table. Never dispatch an ID that is absent from `.agents/team/agents.json`.

| Scope / evidence need | Required registered roles |
|---|---|
| Every whole-market or comprehensive request | `market-regime-analyst`, `sector-rotation-analyst`, `data-verifier`, `risk-analyst`, `contrarian-analyst` |
| Single-target structure | `market-analyst` |
| 1–3 day tactical request with verified auction/L2/trade data | `ultra-short-tactical-trader`, `execution-liquidity-analyst` |
| Catalyst, earnings surprise, policy, restructuring, or expectation-gap request | `event-driven-institutional-analyst`, `fundamental-analyst` |
| Single-target earnings / industry thesis | `fundamental-analyst`, `industry-analyst` |
| Sell-side consensus is material | `report-collector`, then `report-analyzer` |
| Portfolio or allocation plan | `portfolio-manager`, `quant-risk-modeler`, `execution-liquidity-analyst`, `counterparty-structure-risk-analyst`, `compliance-officer` |

If a required input for a role is absent, dispatch it only to identify the missing evidence and return `CONDITIONAL` or `VETO`; do not encourage it to fill gaps with unsupported assumptions.

Core and decision-gate roles (prompt files in `.agents/team/`):

| Role | Prompt |
|------|--------|
| `market-regime-analyst` | `.agents/team/market-regime-analyst.md` |
| `sector-rotation-analyst` | `.agents/team/sector-rotation-analyst.md` |
| `data-verifier` | `.agents/team/data-verifier.md` |
| `market-analyst` | `.agents/team/market-analyst.md` |
| `ultra-short-tactical-trader` | `.agents/team/ultra-short-tactical-trader.md` |
| `event-driven-institutional-analyst` | `.agents/team/event-driven-institutional-analyst.md` |
| `fundamental-analyst` | `.agents/team/fundamental-analyst.md` |
| `industry-analyst` | `.agents/team/industry-analyst.md` |
| `risk-analyst` | `.agents/team/risk-analyst.md` |
| `contrarian-analyst` | `.agents/team/contrarian-analyst.md` |
| `report-collector` | `.agents/team/report-collector.md` |
| `report-analyzer` | `.agents/team/report-analyzer.md` |
| `portfolio-manager` | `.agents/team/portfolio-manager.md` |
| `quant-risk-modeler` | `.agents/team/quant-risk-modeler.md` |
| `execution-liquidity-analyst` | `.agents/team/execution-liquidity-analyst.md` |
| `counterparty-structure-risk-analyst` | `.agents/team/counterparty-structure-risk-analyst.md` |
| `compliance-officer` | `.agents/team/compliance-officer.md` |

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
| Whole-market regime, risk appetite, or market selloff | `market-regime-analyst`, `sector-rotation-analyst` |
| 1-3 trading days with verified auction/L2/trade data | `ultra-short-tactical-trader`, `execution-liquidity-analyst` |
| Short-term, 3-10 trading days | `short-term-trader`, `execution-liquidity-analyst` |
| Swing or trend, 2-12 weeks | `swing-trend-analyst`, `quant-risk-modeler` |
| Earnings, policy, restructuring, commodity, or disclosed event | `event-driven-institutional-analyst`, `fundamental-analyst` |
| Long-term, value, or research tracking | `fundamental-analyst`, `industry-analyst`, `valuation-modeler` when valuation evidence is requested |
| Portfolio construction, cash posture, or reallocation | `portfolio-manager`, `quant-risk-modeler`, `execution-liquidity-analyst`, `counterparty-structure-risk-analyst`, `compliance-officer` |
| Sector heat, themes, or fund-flow claims | `sector-rotation-analyst`, `data-verifier` |

Only expand when the question genuinely requires it — avoid unnecessary data requests and wait time.

Treat backend suggestions such as `short_term`, `swing`, `long_term`, or `sentiment` as routing hints, not role IDs. Map them only through this registered-role table.

## Step 6: Role Task Template

All roles use the same minimal task structure:

### Unified Requirements

- Read shared data packet first
- Prioritize `orchestration`, `packet`, `data_quality`, `warnings`
- If shared data is sufficient, do NOT re-fetch the same data
- If critical data is missing, one supplementary fetch is allowed
- If supplementary fetch fails, provide a degraded conclusion — never return empty
- State the data timestamp and whether a result is observation-only, conditional, or actionable.
- A role with a veto contract must output `PASS`, `CONDITIONAL`, or `VETO` and name the exact blocker/remediation.
- Do not infer real-time execution feasibility from daily, cached, or unknown-freshness data.
- MA, MACD, KDJ, RSI, crossover labels, and oscillator thresholds have zero decision weight. Do not use them for a conclusion, ranking, alert, entry, exit, or veto.

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

### Required Decision Sequence

1. `data-verifier` checks material facts and data freshness before an actionable conclusion.
2. `market-regime-analyst` constrains permitted market risk posture; `sector-rotation-analyst` then ranks observation pools.
3. Target and horizon specialists evaluate only eligible opportunities.
4. `risk-analyst`, `quant-risk-modeler`, `execution-liquidity-analyst`, `counterparty-structure-risk-analyst`, and `compliance-officer` independently issue gates when allocation or execution feasibility is requested.
5. `portfolio-manager` merges only non-vetoed conclusions. Any veto requires `WATCH` or `REJECT` and a remediation path.

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
- Dispatch decision-gate roles after their necessary inputs exist; do not parallelize a portfolio approval ahead of data verification or risk review.

## Step 8: Merge Rules

Final output must include:

1. Executive summary
2. Bull arguments
3. Bear arguments
4. Trading-structure and game-hypothesis assessment
5. Fundamental / policy assessment
6. Street consensus (from report-analyzer: broker ratings, target prices, divergences, blind spots)
7. Key price levels
8. Position sizing recommendation
9. Risk warnings
10. Degradation notes
11. Consistency / conflict points with data packet quality constraints
12. Market regime and permitted risk posture
13. Sector rotation: leading, improving, weakening, and unconfirmed pools
14. Veto ledger: role, status, blocker, remediation, and impact on IC status
15. Portfolio decision status: `APPROVE`, `CONDITIONAL`, `WATCH`, or `REJECT` when a portfolio action was requested

When role opinions conflict:

- Do NOT force unify into a single-sided view
- State the conflict explicitly
- Indicate which side has stronger evidence

Do not upgrade a conclusion to actionable if the data verifier, risk, quant-risk, execution-liquidity, or compliance role issued `VETO`. Preserve its dissent in the final report.

## Step 9: Save Report

For a single-target request, save a final report as LaTeX to:

```text
workspace/research/quick/<CODE>-<YYYYMMDD>/
├── report.tex        # LaTeX source (use report-brief.tex template)
├── report.pdf        # Compiled PDF
└── packet.json       # Raw data packet from Python
```

Use the shared brief template: `.agents/templates/report-brief.tex`

- Set `\reporttitle` to the stock name + code
- Set `\reportdate` to today's date
- Keep report concise (3-5 pages)
- Compile: `.venv/bin/python -m astock.cli build-pdf workspace/research/quick/<CODE>-<YYYYMMDD>/ --file report.tex`

If Python `team` already generated `session_path`, save `packet.json` from that data.

For a whole-market or portfolio request, use the canonical case directory selected by the coordinator under `workspace/research/`, preserve the market packet and veto ledger in `data/`, and do not create a target-named quick report without a target.

Reports should be concise and actionable — avoid empty platitudes.

## Step 10: Persist Research Ledger When Material

If the final conclusion identifies a material investment opportunity, watchlist candidate, or invalidated thesis, update the research ledger through `astock.capabilities`:

- `get_research_ledger_index()`, `query_research_entries()`, or `find_research_duplicate_candidates()` before creating a new thesis.
- `create_research_entry()` for a new thesis with targets, catalysts, risks, monitoring triggers, invalidation conditions, source references, and data quality.
- `record_research_observation()` when a follow-up trigger fires or evidence changes.
- `record_research_postmortem()` when a thesis was wrong or completed and needs counterfactual review.
- `update_research_status()` when the thesis moves to `monitoring`, `invalidated`, `closed`, or `archived`.

Minimal ledger example:

```python
from astock import capabilities

duplicates = capabilities.find_research_duplicate_candidates(
    targets=["000001"],
    title="000001 watchlist thesis",
    tags=["watchlist"],
)
ledger_result = capabilities.create_research_entry(
    title="000001 watchlist thesis",
    thesis="Opportunity thesis based on team evidence, catalysts, and risks.",
    targets=["000001"],
    catalysts=["Catalyst observed in shared packet"],
    risks=["Risk identified by risk and contrarian roles"],
    monitoring_triggers=[
        {"name": "breakout confirmation", "condition": "price holds above resistance"}
    ],
    invalidation_conditions=["Thesis fails if key support breaks on volume"],
    tags=["watchlist"],
    data_quality=packet_provenance,
    source_refs=[{"source": "team.shared_packet", "path": session_path}],
)
```

Do not store casual one-off quote lookups. Persist only conclusions that need follow-up tracking.

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
.venv/bin/python -m astock.cli market-overview --json
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
- Do NOT let all roles call the same data adapters repeatedly
- Do NOT give one-sided conclusions without contrarian arguments
- Do NOT treat degraded data as if it were complete real-time market data
- Do NOT reference or dispatch an unregistered role ID
- Do NOT treat a high stated loss tolerance as a waiver of data quality, risk, liquidity, or compliance gates
- Do NOT provide intraday scalping, same-day round-trip, order-routing, or fill-guarantee instructions
