# Skill Evolution Log

- case_id: aidc-supply-chain-20260630
- evolution_date: 2026-06-30
- trigger: AIDC report quality feedback after mechanical gate pass
- failure_mode: Mechanical gates passed, but institutional research depth remained insufficient.
- root_cause: Skills and deterministic gates emphasized artifact existence, closed review lifecycle, and final sign-off status more than field-level evidence depth, model depth, valuation depth, and IC readiness.

## Changes Applied

| Area | Files | Prevention |
|---|---|---|
| Evolve trigger | `.agents/skills/evolve/SKILL.md`, `.codex/skills/evolve/SKILL.md` | Route repeated report-depth feedback to equity-research, review, supply-chain, growth, and valuation skill audits |
| Equity workflow | `.agents/skills/equity-research/SKILL.md`, `.codex/skills/equity-research/SKILL.md` | Require field-level artifact contract, depth gates, shallow-artifact rule, downgrade path, IC readiness, residual-risk consistency |
| Review gate | `.agents/skills/research-report-review/SKILL.md`, `.codex/skills/research-report-review/SKILL.md` | Add mechanical PASS / institutional FAIL, residual-risk conflict, shallow-artifact severity, reopen rules, R4 IC strong review |
| Domain skills | supply-chain, growth-earnings, valuation skills | Add customer-chain evidence scores, EPS bridge, segment-purity gate, price/share validation, method matrix, Street/multi-anchor requirements |
| Role prompts | selected `.agents/team/*.md` and `.codex/agents/*.toml` | Align source governance, supply-chain, growth, valuation, reviewer, and internal-control behavior |
| Coverage pack | `workspace/templates/industry-coverage-packs/aidc.md` | Add AIDC profit-pool fields, required exhibits, and evidence downgrade rules |
| Deterministic gates | `src/python/astock/quality/checks.py`, `workspace/research/tools/run_research_gates.py` | Add artifact contract depth checks, gate depth checks, residual-risk conflict checks, and industry-depth checks |
| Regression tests | `src/python/astock/quality/__tests__/test_checks.py`, `src/python/astock/__tests__/test_capability_foundations.py` | Add shallow-pass negative case and update positive fixtures |

## Regression Evidence

- `evaluate_research_case_quality()` now fails an industry-chain case that has PASS final sign-off but shallow growth model and material customer/order/ASP/utilization residual risk.
- `run_research_gates.py` now checks field-level artifact contracts, depth gates, industry-chain depth, and residual-risk conflicts.
- Mirror synchronization must be verified with `cmp` for all changed `.agents/skills` and `.codex/skills` files.

## Remaining Case Work

This evolution closes the workflow-prevention gap. The AIDC report itself still requires separate research repair before publication: customer-chain evidence, product-level ASP, utilization/order economics, full broker target history, company EPS bridge, valuation-anchor refresh, and IC chapter rewrite.
