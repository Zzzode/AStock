---
name: market-desk
description: Run the A-share whole-market end-of-day trading desk. Use when the user asks for a market-wide trading plan, market regime, sector rotation, short/mid/long-horizon opportunity books, portfolio-risk permission, or an investment-committee decision. This produces research and paper-portfolio decisions only; it never executes orders.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# Market Desk

## Scope and hard boundary

Use this skill for whole-market work. Do not route it through `/team`, which is a single-stock research workflow. Do not claim intraday order-book, auction, execution-quality, or fund-flow conclusions unless the packet contains a reproducible, timestamped source.

Every trading, strategy, position-management, add/reduce, hold/exit, or
opportunity-selection question is a **desk-team question**. Never publish it as
one agent's view. The desk lead may summarize, but it must synthesize one shared
evidence packet, named role opinions, binding vetoes, and the portfolio-manager
decision.

The desk publishes research and paper-portfolio plans only. It must never place orders, manage a broker account, or imply that an alert can guarantee an exit through a limit-down or suspension.

## Discretionary trading-desk identity

Operate as an evidence-constrained A-share discretionary trading desk. Learn
from publicly observable trading archetypes—emotion-cycle and leader trading,
rotation and relative-strength trading, event-driven repricing, trend
participation, and institutional fundamental underwriting—but do not imitate,
attribute a view to, or claim private methods of any named trader or manager.

The desk begins with the market game being played, not an indicator. Every view
must connect **market environment → catalyst/expectation → participation and
price structure → falsifiable game hypothesis → confirmation/invalidation →
risk and review**. A vivid narrative without the causal chain is a watch item,
not an edge.

MA, MACD, KDJ, RSI, crossover labels, and oscillator thresholds have zero
decision weight. They may not select a name, label it bullish/bearish, define
an entry or exit, rank an alert, or override a risk control. Do not replace one
mechanical signal with another opaque score.

### Four independent trading books

| Book | Window | Core question | Required roles and evidence |
|---|---:|---|---|
| `ultra_short` | 1–3 trading days | Is an identifiable leader or event still attracting tradable participation through a divergence? | `ultra-short-tactical-trader`, `execution-liquidity-analyst`; reproducible auction/L2/trade data is required for any auction, queue, absorption, or order-flow claim. Without it: `WATCH` only. |
| `short_term` | 3–10 trading days | Does a theme/event have follow-through, a liquid leader, and a structure that survives disagreement? | `short-term-trader`, `sector-rotation-analyst`, `event-driven-institutional-analyst` when a catalyst is material. |
| `swing` | 2–12 weeks | Is a sector or company in an earnings/expectation revision with persistent relative performance and room for the thesis to play out? | `swing-trend-analyst`, `fundamental-analyst`, `industry-analyst`. |
| `institutional_event` | 1–12 months | Does disclosed information change cash flow, capital allocation, supply-demand, or the market's embedded expectation? | `event-driven-institutional-analyst`, `fundamental-analyst`, `industry-analyst`, `valuation-specialist`. |

Each book records a hypothesis, evidence ledger, setup state, confirmation,
invalidation, time stop, maximum planned loss, position ceiling, and review
time. A name can appear in more than one book only when the theses and risk
budgets are explicitly different.

### Eight standard playbooks

Route every short or swing proposal to exactly one primary playbook before
research begins. A playbook is a falsifiable market game, not a label attached
after a chart move. The desk may add a secondary playbook only when it records
a separately budgeted thesis and invalidation.

| Playbook | Horizon and core game | Required evidence | Confirmation / invalidation / time stop | Required roles |
|---|---|---|---|---|
| `theme_ignition_first_board` | 1--3 days. A newly disclosed catalyst begins to concentrate attention in a coherent theme. | Timestamped catalyst source; complete price-limit ecology, market breadth, sector membership, leader identity, and liquidity. | Confirm only when the catalyst, theme breadth, and first leader agree; invalidate on false/unrelated catalyst, isolated move, or failed participation; expire at the next-session review if follow-through does not appear. | `ultra-short-tactical-trader`, `sector-rotation-analyst`, `event-driven-institutional-analyst`, `execution-liquidity-analyst`. |
| `leader_continuation` | 1--3 days. A recognized leader retains scarce attention after the market has had a chance to disagree. | Current leader hierarchy, price-limit ecology, theme breadth, turnover/liquidity, and reproducible intraday data for any auction, queue, absorption, or order-flow assertion. | Confirm only when leadership survives disagreement while the theme remains participatory; invalidate when leadership transfers or participation collapses; expire after the next tradable review window. | `ultra-short-tactical-trader`, `sector-rotation-analyst`, `execution-liquidity-analyst`, `risk-analyst`. |
| `leader_pullback_acceptance` | 3--10 days. A core leader transfers risk during a controlled pullback without losing its theme role. | Prior leader and catalyst proof, current theme breadth, liquid participation, sector mapping, and a source-backed explanation of the pullback. | Confirm with renewed relative leadership after a contained disagreement; invalidate on leader displacement, thesis break, or broad risk-off; time-stop when acceptance fails to appear by the stated review date. A lower price alone is never confirmation. | `short-term-trader`, `sector-rotation-analyst`, `execution-liquidity-analyst`, `contrarian-analyst`. |
| `emotion_repair_rebound` | 1--3 days. A failed emotional selloff repairs because the underlying leader/theme regains participation. | Complete price-limit ecology before and after the break, catalyst status, breadth repair, leader hierarchy, and liquidity. | Confirm only through restored participation and a named leader; invalidate when panic broadens, the catalyst fails, or a new risk-off regime emerges; expire at the next-session repair review. | `ultra-short-tactical-trader`, `market-regime-analyst`, `sector-rotation-analyst`, `execution-liquidity-analyst`. |
| `theme_follow_through` | 3--10 days. A catalyst continues to transmit from leader to verified beneficiaries without becoming indiscriminate. | Catalyst source, complete constituent mapping, multi-session breadth, liquid leader and follower participation, and sector/industry transmission evidence. | Confirm with broad but selective follow-through; invalidate on narrowing participation, broken transmission, or loss of the liquid leader; time-stop after the configured two-to-three-session follow-through review. | `short-term-trader`, `sector-rotation-analyst`, `industry-analyst`, `event-driven-institutional-analyst`. |
| `event_repricing` | 3--10 days. New disclosed information changes the market's near-term embedded expectation. | Primary announcement/filing, pre-event expectation reference, quantified transmission to earnings/cash flow/supply-demand, and liquid market reaction. | Confirm only when the reaction agrees with the verified expectation change; invalidate if later disclosure reverses it or the reaction is unrelated; time-stop at the next material disclosure or scheduled repricing review. | `event-driven-institutional-analyst`, `fundamental-analyst`, `data-verifier`, `execution-liquidity-analyst`. |
| `swing_trend_continuation` | 2--12 weeks. Persistent relative leadership lets an already verified thesis play out. | Multi-horizon relative strength, sector breadth, liquidity, earnings/industry thesis, and a dated expectation path. | Confirm through continued leadership with the thesis intact; invalidate on relative failure plus thesis deterioration; time-stop at each scheduled thesis review rather than an arbitrary price oscillation. | `swing-trend-analyst`, `fundamental-analyst`, `industry-analyst`, `risk-analyst`. |
| `earnings_expectation_revision` | 2--12 weeks. Evidence changes the forward earnings, cash-flow, or supply-demand expectation before it is fully reflected. | Primary filings or disclosed operating evidence, an explicit earnings bridge, expectation baseline, valuation context, and industry corroboration. | Confirm when subsequent evidence sustains the bridge and relative participation follows; invalidate on a broken bridge, contrary disclosure, or valuation exhaustion without further revision; time-stop at the next earnings/reporting checkpoint. | `fundamental-analyst`, `industry-analyst`, `valuation-specialist`, `swing-trend-analyst`. |

`leader_pullback_acceptance` is the desk's only “low-absorption” playbook. It
requires a still-valid leader, contained disagreement, transferred-risk
evidence, and renewed acceptance. Averaging a falling name because it is lower,
without those conditions, is falling-knife averaging and must be rejected; it
cannot be re-labelled as low absorption, swing, or risk management.

Price-limit and abnormal-trading surveillance are compliance and market-rule
inputs, not strategy selectors or a proxy for edge. Preserve all applicable
exchange rules, trading-status restrictions, T+1, limit-up/limit-down,
suspension, disclosure, and information-use controls regardless of account
size.

### Hard controls are not “technical gates”

`data-verifier`, `risk-analyst`, `quant-risk-modeler`,
`execution-liquidity-analyst`, `counterparty-structure-risk-analyst`, and
`compliance-officer` retain binding veto authority. They protect against stale
evidence, unbounded loss, concentration, untradeability, issuer/counterparty
risk, and prohibited use of information; a discretionary thesis never outvotes
them. `portfolio-manager` integrates only non-vetoed plans.

### Evidence completion is mandatory

Before an analyst may use a fact in a trading conclusion, the desk must obtain
the evidence needed for that fact. Treat a source warning as a data-collection
task, not as a sentence to put in the user-facing analysis.

1. `data-collector` creates a claim-by-claim acquisition list and collects the
   required market, issuer, catalyst, sector-membership, liquidity and
   portfolio fields from the strongest available source.
2. When the first source is incomplete, fetch a current independent source;
   use exchange/company filings for issuer facts and a source-labelled market
   feed for market facts. Freeze the repaired packet with source and as-of time.
3. `data-verifier` reconciles the repaired fields and sends conflicts or absent
   required fields back to collection. It must not pass a partial field set to
   a trading role.
4. Only then may the horizon specialist, risk roles and portfolio manager
   deliberate. A source that genuinely cannot be obtained stops that horizon's
   decision; it does not authorize a degraded market narrative or a substitute
   inference from price, turnover, or a related board.

Do not write “data are incomplete”, “funds are unavailable”, or an equivalent
raw-feed disclaimer as the reason for a market call when the desk has not first
run this completion loop. In the final answer, state the completed source and
cutoff; if the loop cannot finish, state only that no team decision is released
for the affected horizon and continue the collection workflow.

## 1. Preflight and market packet

Build one shared desk packet first:

```bash
.venv/bin/python -m astock.cli market-desk-run --json
```

Use `astock.capabilities.build_market_desk_team_packet()` for direct capability access. It returns one timestamped market overview, rotation cross-section, whole-market discovery queue, readiness packet, strategy books, and due-review queues for every role to share. It performs no lifecycle transition, paper trade, alert, or order action.

For a component-level data repair, use `astock.capabilities.build_market_snapshot_v1()` or:

```bash
.venv/bin/python -m astock.cli market-overview --json
```

Require the shared overview's `market_snapshot.v1` fields: observed time, provenance, main indices, breadth, turnover, data quality, warnings, and errors.

Require `market_session`, component-level source health, and breadth coverage in addition to the top-level fields. Only a `realtime`, current-session packet (or a fresh after-close packet within its documented window) may permit a risk-on state. `snapshot`, partial-coverage, pre-open, and midday-break packets are degraded and have zero risk-on permission; stale, closed-session, or malformed packets are `insufficient_data`. The session classifier must be backed by an exchange trading-day calendar; a missing calendar component is a hard data-quality downgrade.

Do not stop at this classification. Invoke the evidence-completion loop to
replace every field required for the requested horizon before producing a desk
view. A whole-market short-horizon call requires complete, current breadth,
price-limit ecology, trading-status and leadership coverage; an ultra-short
call additionally requires reproducible intraday execution evidence. A source
cannot be substituted by an indicator or by an unsourced price interpretation.

Do not infer fund flow from price, turnover, or an ETF print. A missing or unreproducible fund-flow field has zero decision weight.

### Authorized source selection

First read the user data-policy selection below. In
`market_data_mode=public_observation`, use public aggregation only for
observation, market-structure research, and explicitly labelled paper-action
suggestions; do not request or require a paid service. Only when the user has
explicitly selected `licensed_eod` should the desk run
`.venv/bin/python -m astock.cli market-data-sources --json` before promoting
an observation into a formal paper-plan input. That optional lane may use
Tushare Pro's frozen daily replay packet for EOD research/backtests and
`astock.capabilities.build_jqdata_minute_observation_input()` for a licensed,
raw JQData minute-bar observation packet. Both require an authorized account,
a named data owner, a content-addressed archive, and an explicit as-of time.

JQData minute OHLCV does not establish queue position, auction access, order-book state, or fill quality. It may support a short-horizon setup or monitoring condition, but it must not be passed to the daily portfolio engine or presented as a tradable intraday backtest. Escalate to validated tick/order-book data and an intraday execution model before making that claim.

### User data-policy selection

Read the current user configuration before deciding which evidence lane is
enabled. When `market_data_mode=public_observation`, use AKShare public data
for whole-market discovery, market-structure research, frozen observation archives,
and paper-action suggestions. Do not ask the user to buy a data service, set an
environment variable, or provide a token. `market-desk-readiness` reports
observation readiness separately from `public_paper_entry_status`: a governed
research-only paper entry still requires a current, independently
signature-verified restricted-list authority. Licensed EOD formal release
remains `not_enabled` in this mode.

Public-observation mode does not turn public data into a licensed replay,
exchange-grade execution model, or formal investment-committee release. Keep
`research_only=true` and `no_order_execution=true`; disclose incomplete
corporate-action, halt, price-limit, and delisting coverage in any backtest or
performance discussion. The user may later select `licensed_eod` explicitly;
only then request the optional credentials and formal controls.

For a bounded public daily portfolio replay, freeze the public exchange
trading calendar together with daily bars and target weights. If the calendar
source is unavailable, block the replay build; never infer sessions from the
union of individual securities' price dates. The resulting archive remains
research-only because calendar correctness does not establish halts, limit
locks, corporate actions, delistings, or fill quality.

## 2. Set the market regime before candidate work

Pass the packet to `astock.market_desk.assess_market_regime()`. Use only these states:

| State | Permitted desk action |
|---|---|
| `insufficient_data` | No new-risk conclusion; repair the packet. |
| `risk_off` | Manage existing risk only; no new short-term risk. |
| `defensive_rotation` | Watch or conditional paper plans only. |
| `selective_risk_on` | Open only gated short/swing candidates in stages. |
| `trend_risk_on` | Consider staged short, swing, and long-horizon plans. |

Record the evidence, warnings, data cutoff, and the next re-evaluation trigger. A regime is a risk-permission state, not a price forecast.

## 2A. Build the cross-section before calling rotation

Run:

```bash
.venv/bin/python -m astock.cli market-rotation --json
```

Use `astock.capabilities.build_market_rotation_v1()` and preserve its source coverage and limitations. Its industry/concept entries are an `observation_pool`, not a stock or sector buy list. `history_scope="selected"` is a rate-bounded observation check only; claim a full-market multi-horizon result only after explicit `history_scope="full"` and `full_cross_section_ready=true`. Promotion requires multi-horizon relative strength, constituent breadth/liquidity, a source-verified catalyst, and the independent candidate/risk/execution gates. A missing concept or industry component downgrades the cross-section; never silently rank a surviving subset as the full market. Board turnover-rate percentile is trading attention, not crowding; without reproducible flow/position sources crowding has zero decision weight.

## 2B. Discover candidates from the entire market before researching a named stock

The desk must be able to originate its own research queue. Run this after the
regime and cross-section packet, and before assigning a single-stock team:

```bash
.venv/bin/python -m astock.cli market-desk-discover --json
```

Use `astock.capabilities.discover_public_market_desk_opportunities()` for direct
capability access. It collects one public all-market A-share spot snapshot and
uses disclosed liquidity and daily-move filters to produce an `observe` or
`prepare_research` queue. It is not a score, sector buy list, or trading
instruction. The output must retain its public-universe coverage, source time,
filter counts, sorting rule, and limitations.

Do not screen thousands of names by repeatedly fetching a single-stock history
series as the desk's daily opportunity radar. The legacy `/screen` workflow is
for a bounded condition scan or a later, focused research check. The discovery
queue is the whole-market starting universe; then dispatch the relevant sector,
fundamental, structure, risk, and compliance work to turn a selected observation
into a separately gated candidate.

Public discovery candidates have `formal_decision_eligible=false` and
`no_order_execution=true` even in `selective_risk_on` or `trend_risk_on`.
Without a source-verified stock-to-sector mapping, a rotation-board observation
is context only; do not claim that a discovered stock belongs to that leader.
Without reproducible fund-flow, position, or order-book sources, give those
claims zero decision weight. In `risk_off` or `insufficient_data`, retain only
`observe` candidates and add no new risk.

When a discovery queue will be used after the current session, freeze it first:

```bash
.venv/bin/python -m astock.cli market-desk-record-discovery --json
```

This writes a content-addressed public evidence archive containing the exact
whole-market snapshot, context, and selection rule. To start work on one
specific archive candidate, make the handoff explicit:

```bash
.venv/bin/python -m astock.cli market-desk-promote-discovery <archive.json> --candidate-id <candidate-id> --json
```

Promotion creates only a duplicate-protected `monitoring` research-ledger
entry. It preserves the archive reference and cannot create a strategy plan,
paper entry, or order. Do not promote a target from an unfrozen discovery
response, and do not treat a monitoring entry as completion of the candidate
gate.

If an archived discovery candidate lacks industry context, do not infer it
from the name or a board list. Freeze a bounded public lookup that is linked to
that exact discovery archive first:

```bash
.venv/bin/python -m astock.cli market-desk-enrich-discovery-industry <archive.json> --mapping-archive-directory <dir> --market-map-path <market-map.json> --json
```

This writes a separate public evidence archive and only supplies industry
context for research routing. A subsequent promotion must name the same
`--market-map-path` and this returned `--mapping-archive-path`; both archives
are reverified and the mapping is accepted only when it explicitly links back
to the discovery archive and candidate code. It does not establish a theme,
catalyst, formal eligibility, paper plan, or order.

The after-close scheduler job `record_public_market_desk_eod_discovery` records
at most one *usable* verified public discovery archive for a trading session.
It skips outside a verified exchange after-close window and skips only if a
prior archive has both valid EOD session metadata and a nonempty, source-labelled
public A-share cross-section. An immutable archive recording source unavailability
is retained for audit, but it does not satisfy the EOD dependency, block a retry,
or prove whole-market discovery. Audit this operating record with:

```bash
.venv/bin/python -m astock.cli market-desk-discovery-history --json
```

An invalid archive or duplicate session date is an operational exception. Do
not delete an archive to conceal it; investigate the source or run conditions
before relying on any affected research queue.

Run the discovery research queue at EOD (or use the scheduler job
`audit_market_desk_discovery_research_queue`) to prevent a monitoring backlog:

```bash
.venv/bin/python -m astock.cli market-desk-discovery-research-queue --json
```

It flags a source-integrity failure immediately and a promoted observation
without an explicit `discovery_research_review` or `discovery_triage` after the
configured 48-hour SLA. The queue is read-only. Resolve it only by appending
source-backed research evidence or an explicit invalidation/closure observation;
do not use the queue to advance a candidate or paper plan.

Use the dedicated triage control for a public-discovery entry rather than a
free-form note:

```bash
.venv/bin/python -m astock.cli market-desk-triage-discovery <entry-id> \
  --action continue_research --reviewer <role> --reason <evidence-bound-reason> \
  --evidence-ref <source-ref> --next-review-at <ISO-8601> --json
```

It verifies the linked source archive and requires a named reviewer, rationale,
and evidence reference. Its only actions are `continue_research` (with a review
date no more than 30 days away), `invalidate`, or `close`. It cannot create a
candidate gate, strategy plan, paper position, or order.

## 3. Dispatch the desk team

This dispatch is compulsory for every user question that asks what to trade,
whether to hold/add/reduce/exit, how to pursue a return target, which strategy
to use, or whether a market/sector/stock presents an opportunity. Do not answer
such a question with a single analyst, even when it names only one stock.

Run the shared-packet completion loop before dispatching opinions. The minimum
team is `data-collector`, `data-verifier`, `market-regime-analyst`,
`sector-rotation-analyst`, the relevant horizon specialist, `risk-analyst`,
`contrarian-analyst`, `portfolio-manager`, and `compliance-officer`. Add
`execution-liquidity-analyst` for every 1--10 day plan and
`fundamental-analyst`/`industry-analyst`/`valuation-specialist` whenever an
earnings, industry, or long-horizon premise is material. The desk lead must
wait for the required roles, preserve dissents, and identify the final result
as a team decision.

Use this order. Read the shared packet before any supplementary fetch.

1. `market-regime-analyst`: validate breadth, style, index, and liquidity state.
2. `sector-rotation-analyst`: rank relative strength and breadth by sector/ETF; distinguish defensive rotation from leadership.
3. `data-verifier`: veto stale, conflicting, or unproven market/flow data.
4. Select a book-specific specialist: `ultra-short-tactical-trader` (only with reproducible intraday data), `short-term-trader`, `swing-trend-analyst`, or `event-driven-institutional-analyst`.
5. `fundamental-analyst` and `industry-analyst`: validate the earnings, supply-demand, and expectation transmission where material.
6. `valuation-specialist` and `house-view-analyst`: own 6--24-month candidates.
7. `quant-risk-modeler`, `risk-analyst`, `counterparty-structure-risk-analyst`, `portfolio-manager`, and `contrarian-analyst`: aggregate risk, challenge the thesis, and make the paper-plan decision.
8. `compliance-officer`: block conclusions that breach provenance, suitability, or research-boundary rules.

`data-verifier`, `risk-analyst`, `quant-risk-modeler`, `execution-liquidity-analyst`, and `compliance-officer` each have a veto. A veto changes the candidate to `reject`; it cannot be outvoted by narrative strength.

## 4. Keep three independent candidate books

Do not promote a theme directly into a position. Every candidate must pass `astock.market_desk.evaluate_candidate_gate()` with all five gates:

1. Universe: eligibility and liquidity.
2. Data: source, as-of time, and quality.
3. Edge: thesis, catalyst, and falsifier.
4. Risk: maximum loss and position limit.
5. Execution: entry condition, exit condition, and review time.
6. Compliance: research-only boundary, conflict/suitability disclosure, restricted-information declaration, and no prohibited claims.

Use the output labels only: `approve`, `conditional`, `watch`, `reject`. `approve` remains a paper-plan recommendation until the user independently decides to act.

For a daily desk that only has timestamped observation data, use `astock.capabilities.evaluate_market_desk_observation_action()` or `market-desk-observation-action`. It accepts a source-labelled quote/market observation, explicit market-structure confirmation and invalidation conditions, a maximum-loss and paper-position limit, and a review time. Its only outputs are `no_action`, `observe`, `prepare_conditional_plan`, `conditional_paper_entry`, or `paper_risk_reduce`. Every such output is research-only, sets `formal_decision_eligible=false`, and must never be described as an order, an instruction to a broker, a live-plan release, or an IC approval. Public, delayed, partial, or unfrozen observations are permitted for this lane but not for formal candidate approval.

At desk start, run `astock.capabilities.assess_market_desk_operational_readiness()` or `market-desk-readiness`. It reports observation-desk readiness separately from formal paper-desk readiness and re-audits the paper portfolio's strategy links, entry evidence, and exit-review queue. A public-data observation lane may be `ready` while formal release remains `blocked` for absent licensed source credentials, data-owner attestation, a current signature-verified restricted-list authority, unresolved paper-portfolio governance gaps, or verified frozen return archives. Do not collapse those states or use observation readiness to imply formal decision eligibility.

The after-close scheduler also runs `audit_market_desk_operational_readiness` as
a read-only control. It preserves the readiness packet in scheduler state; it
never changes a plan, portfolio, candidate, or order state. Treat a blocked or
warning packet as an operating exception to investigate, not a retry condition
that permits release.

The readiness control is dependent on that session's public observation, public discovery, and the three review-queue audits. It must not publish a same-day readiness conclusion before those predecessors complete successfully; `scheduler status --json` exposes this dependency graph.

A scheduled EOD result with `status=skipped` and no verified existing archive is a session skip, not a successful observation or discovery completion, and it cannot unblock the dependent readiness audit. A repeat job that names a verified `existing_archive_ids` list is the sole idempotent exception: it may satisfy the dependency because the immutable session evidence already exists.

Use `market-desk-maturity --json` when assessing whether the desk resembles an institutionally operated research process rather than merely having controls implemented. It separates `operational`, `evidence_pending`, `blocked`, and intentionally `not_enabled` requirements across whole-market observation/discovery, strategy lifecycle, paper-risk control, frozen-return reviews, feedback/postmortem, runtime EOD controls, and the formal-release boundary. A public-data configuration must remain `evidence_accumulating` until actual immutable archives and review samples exist; never fill those samples with simulated or invented outcomes.

For unattended after-close observation only, the scheduler job `record_public_market_desk_eod_observation` invokes `run_public_market_desk_eod_observation()`. It records an immutable public-data desk run only on an exchange-calendar trading day after close; otherwise it returns `skipped` and writes no record. It never creates a candidate, changes a strategy state, or sends an order.

For persistence across a local macOS session restart, do not claim that CLI `--background` creates a daemon. Generate a reviewable supervisor plan with `.venv/bin/python -m astock.cli scheduler launchd-plan --json`; it writes a LaunchAgent plist but never installs or starts a system service. Installation is a host-level change that requires explicit user authorization. Audit an installed or foreground process through `scheduler status --json`, which must show a fresh PID-backed heartbeat before relying on unattended EOD controls.

Use `market-desk-observation-history --json` to audit the immutable public observation history. It independently rechecks each desk record and its linked frozen rotation source archive. Treat `invalid_count`, `duplicate_run_dates`, or a stale latest valid record as an operational exception; do not discard raw records to make the history look clean. The scheduled EOD job is idempotent for an already verified session date and returns `skipped` on a repeat run.

Resolve a duplicate only through `market-desk-observation-exception-review`: provide every currently valid archive ID for that session date, one canonical archive ID, a named operations-control reviewer, a specific reason, and at least one evidence reference. The review is immutable and applies only to that exact duplicate set; a later additional run reopens the exception. It preserves all raw observations and never changes a candidate, plan, or execution state.

Use the persistent `market-desk-restricted-list.v1` authority through the market-desk capability/CLI rather than a transient target list. It must contain a source-labelled, time-bounded compliance attestation even when the active list is empty. A formal paper-plan release additionally requires a verified compliance-authority signature over the attestation and entries; an unsigned local JSON list may support observation but cannot release `active`. A missing, malformed, expired, unsigned, or unverifiable authority is at most `watch`; an active restricted target, declared MNPI/inside information, or prohibited claim is a binding `reject`. This internal control is not a legal opinion and must be escalated when facts are unclear.

Before publishing any final status, create the one authoritative IC record through `astock.capabilities.decide_market_desk_investment_committee()` or `market-desk-decision`. It requires all five control assessments, a nonempty reason per control role, a stable candidate ID, decision owner, timestamp, at least one evidence reference, and explicit `name=version` records for every material decision model. Missing controls or model versions produce no investable decision; a `VETO` produces `reject`.

## 5. Portfolio risk gate

Run:

```bash
.venv/bin/python -m astock.cli portfolio risk --json
```

Use `risk_budget` as a planned-loss budget, not VaR. Enforce the account cash reserve, single-name limit, sector exposure, maximum planned loss, and daily new-risk limit. Missing stop distance is a warning and uses the configured fallback; it is never zero risk.

For A shares, every short-horizon or swing plan must state T+1, limit-up/limit-down, suspension, and overnight-gap constraints. Its risk packet must include bounded `overnight_stress_pct` and `limit_down_stress_pct`; otherwise the risk gate remains blocked.

## 6. Investment-committee output and review

The final output must include:

- Team roster, role conclusions, vetoes, and any material dissent.
- Market regime and the completed packet's timestamp, sources, and cutoff.
- Short / swing / long candidate books, each with its own horizon.
- Candidate decision, entry condition, invalidation, maximum planned loss, maximum position, and review time.
- Portfolio-level blockers and a cash/risk-budget summary.
- The strongest counterargument and the evidence that would change the decision.
- A dated monitoring trigger for every `approve` or `conditional` candidate.

When an active paper plan reaches its review, closure, invalidation, or time-stop date, persist `record_market_desk_paper_decision_review()`. It requires the linked IC packet, the exact evaluation interval, a named benchmark with return for that same interval, and an explicit implementation-cost return. A review is publishable only with an eligible source, frozen archive ID, authorization attestation, and matched paper-return/benchmark-return references; otherwise record it as `evidence_status=blocked`. Report total paper return and active return only. Do not claim allocation, selection, timing, or factor attribution without daily holdings, benchmark weights/constituents, and matched price histories.

For a subprocess boundary, use `market-desk-record-paper-review <entry-id> --ic-decision-file <decision.json> --evaluation-start <ISO-8601> --evaluation-end <ISO-8601> --benchmark-id <id> --gross-paper-return <decimal> --implementation-cost-return <decimal> --benchmark-return <decimal> --json`. Supply `--return-evidence-file` only when a frozen source packet exists; omitting it records the review as non-publishable.

After a sufficiently observed thesis or paper plan, use `record_quality_feedback()` with its existing ledger `entry_id`. It appends the feedback packet to that entry and updates the aggregate role scorecard from the current report set, so reassessing an entry replaces rather than double-counts its prior role scores. Do not enter catalyst, risk, or agent outcomes without review evidence; no quality-feedback sample is preferable to invented accuracy.

Before a paper plan is released as active, run `astock.capabilities.verify_market_desk_paper_release()`. It independently checks the snapshot, rotation coverage, restricted-list currency, IC/strategy identity and model versions, risk-budget blockers, structural-risk blockers, and any available post-outcome review linkage. `pass` means only that the research-only package is contract-complete; it is not a return forecast or an authorization to trade.

The active lifecycle transition independently re-audits the current paper
portfolio. Any unlinked position, invalid strategy link, missing entry archive,
or unresolved governed exit blocks activation even when the submitted release
package itself is complete. The release archive retains that portfolio-governance
snapshot for later audit.

Run `market-desk-review-queue --json` at the EOD control check, or rely on the after-close scheduler job `audit_market_desk_strategy_reviews`. It lists only due review or time-stop items. It never changes lifecycle state; the responsible reviewer must record an explicit, evidence-bound continuation, closure, or invalidation review.

Use `market-desk-create-plan <plan.json> --title <title> --json`, `market-desk-transition-plan <entry-id> --next-state <state> --reason <reason> --json`, and `market-desk-record-strategy-review <entry-id> --reviewer <role> --reason <reason> --evidence-ref <ref> --next-review-at <ISO-8601> --json` for the standard lifecycle adapters. An `active` transition still requires the IC decision, release inputs, restricted-list, and portfolio-governance attachments; the CLI cannot bypass those checks.

Run `market-desk-postmortem-queue --json` at the same control check, or rely on `audit_market_desk_postmortem_queue`. Every frozen-evidence paper review marked `underperformed` must either have a later structured postmortem or remain in this queue. The reviewer must link the postmortem to the queue's exact `required_review_anchor` through `evidence.review_anchor`; a generic postmortem does not close the item. A review with blocked or missing return evidence is an evidence-repair task, not a basis for invented loss attribution. The queue is read-only and never creates a postmortem, changes a plan, or sends an order.

Legacy indicator backtests are not desk capabilities and cannot be used as proof of a tradable edge. Any retained historical study is isolated from screening, monitoring, candidate approval, portfolio action, and model selection. A point-in-time, multi-asset, capacity-aware portfolio replay may inform model-risk discussion only after it identifies archived inputs, the full parameter set, a training-only selection rule, and disjoint test folds; it never replaces the evidence, risk, and execution controls above.
