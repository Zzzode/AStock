---
name: evolve
description: Use when user reports repeated quality problems, negative feedback, bad report structure, prompt/agent failures, asks why behavior was not automatic, or wants to audit agents, improve prompts, review feedback patterns, check system health, detect drift, sync agents, or trigger internal control.
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

# /evolve - Internal Control & System Evolution

Orchestrate the internal-control agent to audit system quality, detect drift, and propose improvements. All agent capabilities live in `.agents/team/internal-control.md` — this skill only defines the pipeline.

## When to Trigger

| Condition | Scope | Priority |
|-----------|-------|----------|
| User explicitly requests audit | As specified by user | Immediate |
| User reports report/agent quality problems after a substantial task | `feedback_analysis` + likely `single_skill` / `single_role` | Immediate |
| User asks why a quality-control behavior did not trigger automatically | `single_skill:evolve` + `sync_check` | Immediate |
| Repeated corrections in the same dimension during a report/research workflow | `feedback_analysis` + relevant `single_role` / `single_skill` | Immediate |
| User points out a material research-report gap after delivery, such as missing industry-chain block, missing core ticker, weak evidence, bad report structure, or incomplete gate | `feedback_analysis` + `single_skill:equity-research` + relevant domain skill/role | Immediate |
| Periodic (user asks "system health") | `full_system` | On demand |

## Step 1: Determine Audit Scope

Parse user intent to determine:
- **Scope**: `full_system` | `single_role:<name>` | `single_skill:<name>` | `feedback_analysis` | `sync_check`
- **Trigger**: what prompted this audit
- **Depth**: quick scan | thorough audit

If unclear, default to `feedback_analysis` for negative feedback and add the most relevant `single_skill` / `single_role` based on the failure. Do not ask unless the scope would be destructive or expensive.

For research-report feedback, create or require `analysis/delta_audit.md` in the affected case before rewriting the report or prompts. It must map:
- User correction.
- Original miss.
- Missing artifact or gate.
- Responsible skill/role.
- New evidence or sources collected.
- Files changed.
- Prevention rule added to the relevant skill.

## Step 2: Gather Audit Data

### Foundation Quality Checks

Use `astock.capabilities` for deterministic checks before dispatching the
internal-control agent:

```python
from astock import capabilities

prompt_drift = capabilities.check_system_prompt_drift()
source_health = capabilities.evaluate_data_source_health(provenance_records)
skill_eval = capabilities.evaluate_skill_boundary_cases(eval_cases)
report_quality = capabilities.evaluate_research_report_quality(report_text)
case_quality = capabilities.evaluate_research_case_quality(case_dir)
```

Attach these packets to the internal-control prompt when available. If a packet
cannot be built because the required inputs are unavailable, record the missing
input and continue with the remaining checks.

For research-report workflow feedback, also run the hard publication gate when
the affected case directory exists:

```bash
python3 workspace/research/tools/run_research_gates.py workspace/research/<case>
```

If `run_research_gates.py` fails, treat the failed gate as the audit anchor and
map it to the responsible skill, role, artifact, repair plan, and prevention
rule before changing prompts.

### For `feedback_analysis`:

```bash
.venv/bin/python -m astock.cli feedback --json
.venv/bin/python -m astock.cli memory history --limit 50 --json
```

### For `sync_check`:

Read and cross-reference:
- `.agents/team/agents.json` (registered roles)
- `.agents/team/README.md` (documented roster)
- `.agents/team/*.md` (actual role files that exist on disk)
- `.agents/skills/*/SKILL.md` (skill files referencing roles)
- `AGENTS.md` (root documentation)

### For `single_role:<name>`:

Read the role file + grep workspace/ for recent outputs from that role + check memory.

### For `full_system`:

Combine all of the above.

## Step 3: Dispatch Internal Control Agent

Dispatch with prompt from: `.agents/team/internal-control.md`

Provide:
- Trigger context and scope
- All gathered audit data from Step 2
- Relevant role/skill file contents
- Feedback summary (if applicable)

The agent produces its structured Audit Report per its Output Contract.

## Step 4: Present Findings

Display the Audit Report:
1. Executive summary (1-2 sentences)
2. S-level findings — highlighted prominently
3. A-level findings
4. B-level findings
5. Proposed changes (with diffs)
6. Anti-patterns detected
7. Metrics dashboard
8. For report-feedback audits, the `analysis/delta_audit.md` path and prevention-rule changes

## Step 5: Human Approval Gate

**CRITICAL: Never auto-apply changes unless the user explicitly asked to update skills/prompts/agents in the same turn.**

For each proposed change, present the diff and ask the user whether to apply. If the user explicitly asked to update skills/prompts/agents, apply the focused change directly and report it. Otherwise, only after explicit approval:
- Apply the approved diff to the target file
- Update `.agents/skills/evolve/anti-patterns.md` if new patterns detected
- Update both `.agents/skills/...` and `.codex/skills/...` mirrors when a skill prevention rule changes
- Store audit results in memory:

```bash
.venv/bin/python -m astock.cli memory store --agent internal-control --session <YYYYMMDD> --key "audit:latest" --value '<JSON summary>' --json
```

## Step 6: Record Audit History

After completion, store summary for trend tracking:

```bash
.venv/bin/python -m astock.cli memory store --agent internal-control --session <YYYYMMDD> --key "audit:<scope>" --value '{"scope":"<scope>","s_count":<n>,"a_count":<n>,"b_count":<n>,"changes_applied":<n>,"date":"<YYYY-MM-DD>"}' --json
```

## Quick Audit Mode

For a fast post-task check (suggested after team/equity-research with negative feedback):

1. Run only `feedback_analysis` scope
2. Identify if the same strategy/signal has failed 3+ times
3. If pattern detected, suggest specific prompt adjustment
4. Present one-liner suggestion (no full report)

## Command Reference

```bash
.venv/bin/python -m astock.cli feedback --json
.venv/bin/python -m astock.cli memory recall --agent internal-control --key "audit:latest" --json
.venv/bin/python -m astock.cli memory history --limit 50 --json
.venv/bin/python -m astock.cli memory store --agent internal-control --session <DATE> --key <KEY> --value '<JSON>' --json
```

## Prohibitions

- Do NOT auto-apply any changes without explicit user approval
- Do NOT audit trading conclusions or financial data (other roles' domain)
- Do NOT run full_system audit unless user explicitly requests it (expensive)
- Do NOT suggest changes to files outside .agents/, AGENTS.md, or data/config/
- For research-report feedback, targeted changes to the affected `workspace/research/<case>/analysis/delta_audit.md`, `workspace/research/<case>/gate_manifest.*`, `workspace/research/<case>/artifact_contract.*`, `workspace/research/<case>/review_findings_*.json`, `workspace/research/<case>/repair_plan_*.md/json`, `workspace/research/<case>/final_signoff.*`, `workspace/research/<case>/research_workflow_eval.*`, `workspace/templates/industry-coverage-packs/`, and mirrored `.codex/skills/...` files are allowed when the user explicitly asked to update the research-report workflow.
- Do NOT inflate severity to make findings seem more important
- Do NOT propose changes that contradict the project's Language Policy or Document Format Policy
- Do NOT run as a background daemon. In interactive agent work, negative user feedback and repeated correction requests are user initiation and should route to this skill.
