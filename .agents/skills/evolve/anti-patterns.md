# Anti-Patterns Registry

Detected patterns that degrade system quality. Updated by `/evolve` after user-approved audits.

## Format

| ID | Pattern | First Detected | Frequency | Severity | Mitigation | Status |
|----|---------|---------------|-----------|----------|------------|--------|

## Active Anti-Patterns

| ID | Pattern | First Detected | Frequency | Severity | Mitigation | Status |
|----|---------|---------------|-----------|----------|------------|--------|
| AP-001 | Full industry-chain reports relied on generic industry analysis and concept-stock tables instead of a standalone supply-chain evidence gate. | 2026-06-28 | 1 | S | Add `supply-chain-research` skill, `supply-chain-analyst`, required relationship/company-card/earnings-bridge artifacts, and reviewer gates. | Active |
| AP-002 | High-growth or AI valuation narratives converted shipment, order, ASP, TAM, capacity, or one-quarter momentum directly into valuation credit without a standalone revenue-to-EPS precision model. | 2026-06-28 | 1 | S | Add `growth-earnings-model` skill, `growth-earnings-modeler`, required base/growth split, unit/order/ASP/proxy-to-EPS artifacts, current-price-implied sensitivity, and valuation/reviewer gates. | Active |
| AP-003 | Research cases passed mechanical artifact/review gates while remaining institutionally shallow: weak evidence penetration, shallow profit-pool economics, incomplete company EPS bridge, weak valuation anchors, or non-actionable IC summary. | 2026-06-30 | 1 | A | Add field-level artifact contracts, depth gates, shallow-artifact severity rules, residual-risk conflict checks, and regression tests for mechanical PASS / institutional FAIL. | Active |
| AP-004 | Chinese research prose used contrast-template rhetoric (including authored comparative uses of `不是`, `没有`, `最难……`, `而非`, `而不是`, and negative-stack variants) after a generic “formulaic contrasts” rule failed to make the prohibition testable. | 2026-08-15 | 4 | A | Ban the patterns in writer and prose-polish instructions; require an R2 literal scan that flags every authored `不是` and `没有` occurrence, `analysis/prose_style_audit.md/json`, A-Level closure, and a regression test. Immutable quotations, legal/regulatory text, and source titles require explicit labeling. | Active |

## Resolved Anti-Patterns

(Patterns that were fixed and confirmed no longer occurring)
