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

## Resolved Anti-Patterns

(Patterns that were fixed and confirmed no longer occurring)
