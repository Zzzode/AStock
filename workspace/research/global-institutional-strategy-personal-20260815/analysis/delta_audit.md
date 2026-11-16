# Delta Audit — Chinese Prose Template Rule

## Trigger

User feedback on 2026-08-15: `禁止不是 - 而是 最难 而非这种写作方法，写进研报规则里面`.

## Scope Decision

The user subsequently authorized a full rewrite of the reader-facing report. Follow-up reviews identified a remaining double-denial construction and then a paired-negative frame using `没有`; the TeX source was revised again under exhaustive authored-`不是` / `没有` scans. The PDF, R2/R3/R4 records, and all case gates were reopened for the current reissue.

## Original Miss

The workflow described formulaic contrasts generically, but did not name the prohibited Chinese templates, prescribe a lexical scan, require a style-audit artifact, or block R2 closure. The first repair scan remained too narrow because it matched fixed pairings but did not require review of every authored `不是` occurrence. The second repair then left a paired-negative `没有` frame outside that token scope.

## Affected Legacy Examples

| File | Location | Observed pattern | Disposition |
|---|---|---|---|
| `sections/ch08_common_controls.tex` | line 33 | contrast-template sentence | Rewritten and verified clear. |
| `sections/ch03_institution_map.tex` | line 41 | `最难……` plus `而非` | Rewritten and verified clear. |
| `sections/ch04_applicability.tex` | line 24 | `最重要……不是……而是……` | Rewritten and verified clear. |
| `sections/ch07_event_rulebook.tex` | title | `不是……而是……` | Rewritten and verified clear. |

## Responsible Workflow Gap

- Root skills: `research-prose-polish`, `equity-research`, and `research-report-review`.
- Drafting role: `latex-writer`.
- Review role: `research-report-reviewer`.
- Missing gate: an R2 reader-prose hard gate with a zero eligible-hit threshold.

## Prevention Rule Added

For Chinese reader-facing prose, the named contrast-template patterns and their close variants are prohibited across titles, body copy, captions, table introductions, and callouts. The R2 scan now conservatively reviews every authored `不是` and `没有` occurrence, together with paired-negative stacks. Immutable direct quotations, legal/regulatory text, and source titles are the only exceptions and require clear labeling. Before R2, the workflow requires a literal scan and `analysis/prose_style_audit.md/json`; each non-exempt hit is an A-Level `reader_prose_template_ban` finding and blocks R2, R3, R4, and publication until repaired.

## Files Changed

- `.agents/skills/research-prose-polish/SKILL.md` and `.codex/skills/research-prose-polish/SKILL.md`
- `.agents/skills/equity-research/SKILL.md` and `.codex/skills/equity-research/SKILL.md`
- `.agents/skills/research-report-review/SKILL.md` and `.codex/skills/research-report-review/SKILL.md`
- `.agents/team/latex-writer.md` and `.codex/agents/latex-writer.toml`
- `.agents/team/research-report-reviewer.md` and `.codex/agents/research-report-reviewer.toml`
- `.agents/skills/evolve/anti-patterns.md` and `.codex/skills/evolve/anti-patterns.md`
- `src/python/astock/quality/__tests__/test_research_prose_rules.py`
- `main.tex` and `sections/*.tex`

## Validation

See `prose_style_audit.md/json` for reissue scan evidence and `../skill_evolution_log.md/json` for mirror, regression, and workspace-gate evidence.
