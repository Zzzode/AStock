---
name: research-prose-polish
description: Polish Chinese or English equity-research prose without changing facts, numbers, citations, valuation conclusions, risks, or compliance boundaries. Use for a post-draft editorial pass, research-report repair, or review of generic AI-style, promotional, template-like, or meta-writing language, including requests such as 去 AI 味, 去模板腔, 润色研报, and polish this report.
---

# Research Prose Polish

Refine reader-facing research prose so it is direct, specific, causal, and appropriate for an institutional investor. This is an evidence-preserving editorial pass, not an AI-detector-evasion tool and not a creative-writing exercise.

Design note: independently adapted for AStock from the editorial problem framing of [humanizer-zh](https://github.com/op7418/humanizer-zh) (MIT), with research-specific rules authored here.

## Non-Negotiable Evidence Boundary

Before editing, preserve every material:

- number, unit, date, ticker, company name, price, forecast, target, and scenario;
- source, source-quality label, attribution, quotation, citation, and uncertainty qualifier;
- investment conclusion, action label, catalyst, risk, invalidation trigger, and recommendation boundary;
- explicit evidence gap, including not disclosed, unavailable, insufficient evidence, and watchlist-only language;
- LaTeX command, label, cross-reference, formula, table calculation, and source note.

Never add a fact, customer relationship, source, causal mechanism, expert view, or confidence level that is not already supported by the research pack. Never delete a material hedge merely because it sounds cautious. Route a factual ambiguity to the evidence owner instead of smoothing it away.

## Chinese Rhetorical-Template Prohibition

For authored Chinese reader-facing text, the following contrast-template constructions are prohibited:

- any authored use of `不是` or `没有` that frames a comparative, contrastive, or double-denial construction; the R2 scan conservatively flags every authored `不是` occurrence and every authored `没有` occurrence for disposition, including `不是……而是……`, `并非……而是……`, `绝非……而是……`, `不是 X，而是 Y`, and `没有……也没有……`;
- `最难……`, `最重要……不是……`, `真正/关键……不是……`, and closely related importance-first contrast templates;
- `而非` or `而不是` used as a contrastive flourish.
- `不是……也不是……`, `既不是……也不是……`, `既非……也非……`, `既不……也不……`, `没有……也没有……`, and equivalent negative-stack framing.

This rule covers body text, chapter and exhibit titles, captions, callout boxes, table introductions, and conclusions. State the affirmative claim directly, then give the evidence, mechanism, condition, or investment implication. If a contrast is genuinely material, use separately evidenced sentences; do not retain or substitute a near-equivalent rhetorical wrapper. The literal `不是` / `没有` scan is intentionally conservative: an immutable quotation, legal/regulatory text, or source title may remain only under the documented exception protocol.

The only exception is immutable verbatim material: a direct quotation, legal or regulatory text, or a source title. Mark that material clearly as quoted or sourced and do not use the exception to preserve author-written prose.

Before R2, run a literal first-pass scan across authored reader-facing `.tex` files and any available release-text extraction:

```bash
rg -n -P '不是|没有|最难|而非|(?:并非|绝非)[^。！？；\\n]{0,96}(?:而是|也(?:不是|非|不))|既非[^。！？；\\n]{0,96}也非|(?:既)?不[^。！？；\\n]{0,96}也不|(?:无|未)[^。！？；\\n]{0,96}也(?:无|未)' main.tex sections/
```

Inspect every hit, record the path, matched text, disposition, and any immutable-text exception in `analysis/prose_style_audit.md/json`. Every eligible hit is an A-Level `reader_prose_template_ban` finding. R2 cannot close until the eligible-hit count is zero.

## Modes

### Writer or Repair Mode

Use after the evidence, model, and valuation facts are locked; edit only reader-facing narrative, exhibit introductions and syntheses, captions, and table explanations. Return the revised prose and a concise fact-preservation check.

### Read-Only Review Mode

Identify exact locations, the pattern, its reader impact, and a safe repair direction. Do not edit the report. Style issues are normally B-Level; escalate to A-Level when wording obscures a material thesis, valuation, risk, source-quality distinction, or uncertainty. Unsupported evidence or a changed conclusion is a substantive issue, not a prose issue.

## Editorial Workflow

1. Establish the scope.
   - Read the draft together with the relevant research brief, house view, claim audit, source registry, valuation output, and risk output.
   - For a full research case, work after the first complete draft and before the R2 draft review. For a repair plan, edit only the named sections and return them to the same review cycle.
   - Preserve the requested language. Chinese reports remain Chinese except for allowed proper nouns, tickers, formulas, abbreviations, source titles, URLs, and short bilingual captions.

2. Create a preservation list.
   - Mark material claims and their supporting source or artifact before rewriting.
   - Treat numbers, dates, evidence-quality labels, action labels, and falsification triggers as immutable unless the owning research skill corrects them.
   - Leave direct quotations, legal disclosures, source titles, and table cells untouched unless the user explicitly requests a substantive revision.

3. Scan for editorial patterns.
   - Replace inflated importance claims, generic legacy statements, and grand conclusions with the observable mechanism, financial consequence, or remove them.
   - Remove promotional adjectives, marketing language, and unsupported superlatives. Prefer a precise operating fact or a disclosed evidence gap.
   - Replace vague attribution such as “experts believe” with the named source and date already present; otherwise retain an honest qualifier or remove the unsupported assertion.
   - Remove chatbot residue and author-facing meta-language, including greeting/closing filler, “this report will,” process narration, knowledge-cutoff disclaimers, and instructions to the reader.
   - Tighten filler transitions, formulaic contrasts, redundant three-item lists, noun-heavy abstractions, repeated sentence openings, and generic optimistic endings when they add no analytical content.
   - Apply the Chinese Rhetorical-Template Prohibition before any other tone edit. Do not use a synonym or a punctuation change to preserve a prohibited structure.
   - Keep a real three-part list when all three items are distinct and material. Do not force variation at the expense of precision.
   - Replace a table or exhibit summary with causal synthesis: what changed, why it matters, and the valuation, risk, or monitoring implication.

4. Rewrite conservatively.
   - Prefer a specific subject, active verb, and evidence-linked result.
   - State causality only when the underlying source supports causality; otherwise use an appropriately limited association or observation.
   - Vary rhythm naturally, but retain a formal, measured institutional voice. Do not add first-person voice, humor, emotional color, invented anecdotes, or deliberately messy structure.
   - Preserve valid domain terminology. Do not replace technical precision with casual language merely to sound less templated.

5. Run the fact-preservation check.
   - Re-read every materially changed paragraph against its source artifact.
   - Confirm all numerical tokens, citations, source-quality qualifiers, target prices, action labels, risks, and invalidation triggers are unchanged.
   - Confirm the edit did not strengthen a recommendation, conceal an evidence gap, change the scope of a claim, or damage LaTeX structure.
   - If a clean rewrite is impossible without changing meaning, keep the original text and flag the issue for the relevant research owner.

## Institutional Style Standard

Aim for a report that sounds written by a careful analyst:

- Start paragraphs with the investment question or judgment, then show evidence and implication.
- Use concrete facts, mechanisms, and explicit uncertainties instead of ornamental framing.
- Keep tables and exhibits inside an argument; add interpretation before or after them rather than restating every cell.
- Make conclusions conditional where the evidence is conditional.
- Keep the house view distinguishable from broker views, source summaries, and unverified market commentary.

Do not apply consumer-marketing or personal-essay conventions. A polished research report must remain sober, attributable, and auditable.

## Output Contract

In writer or repair mode, provide:

1. Revised text or the edited reader-facing section.
2. A short list of material editorial changes.
3. Fact-preservation status: PASS, or BLOCKED with the unresolved claim/source issue.

In read-only review mode, provide findings with:

- file and section;
- observed pattern and reader impact;
- severity;
- safe repair direction;
- owner: research-prose-polish for prose-only work, or the substantive source/model/valuation owner when wording exposes an evidence problem.

For full equity-research reports, return prose-only repairs to R2 draft review. Do not self-certify the report as publishable.
