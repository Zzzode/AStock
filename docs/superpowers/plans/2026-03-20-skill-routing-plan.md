# Skill Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Narrow the routing boundaries of `quote`, `analyze`, and `team` so each skill triggers on the right class of stock questions with less overlap.

**Architecture:** Keep the existing three-skill structure, but tighten each skill at the metadata and body-example level. The change is intentionally local: update frontmatter descriptions, auto-trigger examples, and nearby explanatory text so `quote` owns market snapshot queries, `analyze` owns technical-analysis queries, and `team` owns decision-oriented comprehensive analysis.

**Tech Stack:** Claude Code skill markdown files, YAML frontmatter, repository docs

---

## File map

- Modify: `.claude/skills/quote/skill.md` — tighten description and examples to real-time quote / market snapshot requests only
- Modify: `.claude/skills/analyze/skill.md` — make technical-analysis routing explicit and keep “分析一下XX” here
- Modify: `.claude/skills/team/skill.md` — narrow description to buy/sell/hold/timing/position multi-factor decisions and remove generic analysis triggers
- Reference: `docs/superpowers/specs/2026-03-20-skill-routing-design.md` — approved routing spec

## Exact change map

| File | Current content | Required change |
|------|-----------------|-----------------|
| `.claude/skills/quote/skill.md` | Frontmatter description includes `"000001现在怎么样"` | Replace the whole description with the exact spec text and remove this ambiguous pattern |
| `.claude/skills/quote/skill.md` | Auto-trigger table is already quote-oriented | Keep the existing four rows because they are quote-safe |
| `.claude/skills/quote/skill.md` | Optional interpretation says `"涨了吗"或"现在怎么样"` | Change this to `"涨了吗"或"今日表现如何"` |
| `.claude/skills/analyze/skill.md` | Frontmatter description is technical-analysis-oriented but narrower than the spec | Replace the whole description with the exact spec text; keep `"分析一下XX"` as the default technical-analysis trigger |
| `.claude/skills/analyze/skill.md` | Example `"分析一下平安银行"` already exists | Keep it; it is the canonical generic-analysis example |
| `.claude/skills/team/skill.md` | Frontmatter description includes `"分析一下XX"` and `"XX现在怎么样"` | Replace the whole description with the exact spec text and remove both ambiguous patterns |
| `.claude/skills/team/skill.md` | Top section lacks an explicit routing boundary note | Add a short note directly below the introductory paragraph stating that price questions belong to `quote`, pure technical questions belong to `analyze`, and this skill is for comprehensive buy/sell/hold/timing judgment |

### Task 1: Tighten `quote` skill routing

**Files:**
- Modify: `.claude/skills/quote/skill.md`
- Reference: `docs/superpowers/specs/2026-03-20-skill-routing-design.md`

- [ ] **Step 1: Read the current `quote` skill and locate overlapping trigger text**

Search for these exact strings in `.claude/skills/quote/skill.md`:
- `description:`
- `000001现在怎么样`
- `如果用户问的是"涨了吗"或"现在怎么样"`

Confirm the current description and body still include the broad phrase “现在怎么样”.

- [ ] **Step 2: Update the frontmatter description**

Replace the current description with exact text aligned to the spec:

```yaml
description: Use when user asks for a stock’s latest price, intraday change, volume, turnover, today’s performance, or a current market snapshot. Trigger on phrases like "现在多少钱", "最新价", "今日涨跌", "行情", "成交额", or "今天涨了吗". Do not use for technical analysis, indicator interpretation, or buy/sell decision questions.
```

- [ ] **Step 3: Keep the current auto-trigger table unchanged**

The existing table rows are already aligned with quote-only routing and should stay:
- "平安银行现在多少钱"
- "000001行情"
- "查一下茅台价格"
- "贵州茅台今天涨了吗"

Do not add any row equivalent to:
- "XX现在怎么样"

- [ ] **Step 4: Make the exact nearby explanatory-text replacement**

Find this sentence:

```markdown
如果用户问的是"涨了吗"或"现在怎么样"，提供简短解读：
```

Replace it with:

```markdown
如果用户问的是"涨了吗"或"今日表现如何"，提供简短解读：
```

- [ ] **Step 5: Re-read the edited file for routing consistency**

Verify the frontmatter, trigger table, and explanatory text all point to price / market snapshot behavior only.

### Task 2: Tighten `analyze` skill routing

**Files:**
- Modify: `.claude/skills/analyze/skill.md`
- Reference: `docs/superpowers/specs/2026-03-20-skill-routing-design.md`

- [ ] **Step 1: Read the current `analyze` skill and confirm its generic trigger coverage**

Search for these exact strings in `.claude/skills/analyze/skill.md`:
- `description:`
- `分析一下XX股票`
- `用户: 分析一下平安银行`
- `操作建议：`

Check that the current description includes technical indicators and that “分析一下XX股票” is present.

- [ ] **Step 2: Update the frontmatter description**

Replace the current description with exact text aligned to the spec:

```yaml
description: Use when user asks for technical analysis of a stock, including MA, MACD, KDJ, RSI, golden cross, death cross, trend strength, support/resistance, or technical entry/exit signals from a chart perspective. Trigger on phrases like "技术分析", "分析一下XX", "均线", "MACD", "RSI", "金叉", "死叉", or "趋势怎么看". Do not use for simple price lookup or broader buy/sell decision advice involving position sizing or multi-factor judgment.
```

- [ ] **Step 3: Keep technical-analysis examples and avoid decision-routing examples**

Ensure the examples stay focused on technical interpretation. Keep or reinforce examples like:
- "分析一下平安银行"
- "000001技术分析"
- "茅台MACD"

Do not add examples centered on:
- whether the stock is worth buying now
- position sizing
- comprehensive bull/bear decision support

- [ ] **Step 4: Keep the existing `操作建议` block unchanged unless you introduce decision-oriented wording**

Search for the `操作建议：` section in `.claude/skills/analyze/skill.md`. Leave the current example in place because it is framed as technical-signal interpretation. Only edit this section if your earlier description changes accidentally introduce portfolio, 仓位, or multi-factor decision language; if that happens, rewrite the local wording so it stays technical-analysis-first.

- [ ] **Step 5: Re-read the edited file for routing consistency**

Verify the frontmatter and examples clearly anchor `analyze` as the default handler for “分析一下XX” and technical-indicator queries.

### Task 3: Tighten `team` skill routing

**Files:**
- Modify: `.claude/skills/team/skill.md`
- Reference: `docs/superpowers/specs/2026-03-20-skill-routing-design.md`

- [ ] **Step 1: Read the current `team` description and identify conflicting triggers**

Search for these exact strings in `.claude/skills/team/skill.md`:
- `description:`
- `分析一下XX`
- `XX现在怎么样`
- `# /team - 全明星投资研究团队`

Confirm that the current file still includes generic triggers such as “分析一下XX” and “XX现在怎么样”.

- [ ] **Step 2: Update the frontmatter description**

Replace the current description with exact text aligned to the spec:

```yaml
description: Use when user asks whether a stock is worth buying, selling, holding, or entering now, wants timing or position advice, or needs a multi-factor A-share decision with bull/bear arguments and risk assessment. Trigger on phrases like "适合买吗", "现在能不能买", "要不要卖", "怎么看仓位", or "综合分析下值不值得参与". Do not use for simple quote requests or pure technical-indicator interpretation when the user is not asking for a broader decision.
```

- [ ] **Step 3: Make the exact trigger cleanup in the description layer**

The current frontmatter description contains these patterns that must be removed:
- "分析一下XX"
- "XX现在怎么样"

After replacing the whole description with the exact spec text, the trigger examples should instead be decision-oriented only, such as:
- "XX股票适合买吗"
- "现在能不能买"
- "要不要卖"
- "怎么看仓位"

- [ ] **Step 4: Add the exact boundary note below the introductory paragraph**

Insert this exact note directly below the introduction paragraph under `# /team - 全明星投资研究团队`:

```markdown
> 边界说明：价格与行情快照问题优先使用 `/quote`，纯技术指标与走势研判优先使用 `/analyze`，本技能只用于买卖时机、持有判断、仓位建议和多维度综合决策。
```

Keep the note concise and local; do not refactor the rest of the large file.

- [ ] **Step 5: Re-read the edited file for routing consistency**

Verify the frontmatter, top-of-file description, and any trigger examples all align with decision-oriented comprehensive analysis only.

### Task 4: Verify the three-skill split against the spec

**Files:**
- Review: `.claude/skills/quote/skill.md`
- Review: `.claude/skills/analyze/skill.md`
- Review: `.claude/skills/team/skill.md`
- Reference: `docs/superpowers/specs/2026-03-20-skill-routing-design.md`

- [ ] **Step 1: Read the approved spec side-by-side with the edited skills**

Compare each edited skill against the exact routing boundaries in the spec.

- [ ] **Step 2: Check the ambiguity policy**

Confirm:
- “分析一下XX” remains with `analyze`
- “XX现在怎么样” is removed from all three trigger lists and examples

- [ ] **Step 3: Run a manual prompt sanity check**

Validate this expected mapping conceptually:
- “平安银行现在多少钱” → `quote`
- “分析一下平安银行” → `analyze`
- “平安银行现在适合买吗” → `team`

- [ ] **Step 4: Review the git diff**

Inspect the diff to ensure only the intended routing text changed, with no unrelated edits.

Run: `git diff -- .claude/skills/quote/skill.md .claude/skills/analyze/skill.md .claude/skills/team/skill.md docs/superpowers/specs/2026-03-20-skill-routing-design.md docs/superpowers/plans/2026-03-20-skill-routing-plan.md`

Expected: only skill-routing wording and plan/spec document changes appear.

- [ ] **Step 5: Prepare completion summary**

Summarize the final routing split in one short block for the user before any optional review or commit workflow.
