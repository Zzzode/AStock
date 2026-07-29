# Valuation Audit

Model Reproducibility: PASS

## Eligibility and Coverage Contract

- Positive-weight packet: `data/current_valuation_model_20260722.json`, containing only 002497.
- Structured zero-weight companion: `data/zero_weight_valuation_model_20260722.json`, containing 600150, 301308, 002812, 002240, and 300390.
- 002812 remains `blocks_valuation=true`; CNY103 and the CNY30.96/67.08/103.20 sensitivity receive zero weight and no probability.

## Arithmetic and Share Reconciliation

- 002497 market cap: CNY16.79 x 1.15256bn shares = CNY19.352bn.
- Bear: CNY1.31bn parent NP / 1.15256bn shares = CNY1.14 EPS; 8x = CNY9.12.
- Base: CNY3.035bn / 1.15256bn = CNY2.63 EPS; 10x = CNY26.30.
- Bull: CNY3.85bn / 1.15256bn = CNY3.34 EPS; 12.6x = CNY42.08 after rounded-input reconciliation.
- Operating-driver probability value: 30% x 9.12 + 50% x 26.30 + 20% x 42.08 = CNY24.302.
- Exact blended value: 80% x 24.302 + 10% x 16.79 + 10% x 42.00 = CNY25.3206, reported as CNY25.32 for audit and CNY25-26 for readers.
- Exact upside: 25.32 / 16.79 - 1 = 50.80%.

## Driver and Denominator Audit

The three 002497 scenarios vary shipments, price proxy, revenue, gross margin, opex/tax burden, parent net profit, EPS, and PE. The base reconciles to the original broker forecast within rounding. Inventory gains and hedge P&L receive zero normalized credit. The civil-explosives floor and lithium contribution are shown separately.

The 002812 sensitivity is not independent house evidence because all three values reuse one broker's 2027E EPS. It cannot receive positive weight until company-level shipment, realized unit profit, utilization, yield, customer price, and cash evidence close the gate.

## Weight and Source-Overlap Audit

002497 weights are 80% operating-driver probability value, 10% current price, and 10% external target; they sum to 100%. The base driver inputs and external target partially share the same Dongwu source, so the 10% anchor is a transparent Street comparison rather than independent confirmation.

- Zero external-target weight, proportionally renormalized: CNY23.47.
- 70% driver / 20% market / 10% external: CNY24.57.
- Main 80% / 10% / 10% mix: CNY25.32.

The reader conclusion does not change: no base-case double.

## Target-Horizon and Timing Audit

The CNY42 and CNY103 report targets have no disclosed horizon. Neither is labeled a 2026-12-31 target. A five-month timing haircut is expressed through the 20% bull probability for 002497 and by assigning 002812 zero formal weight.

## Zero-Weight Row Audit

Every remaining deep name has a structured row with current price, diagnostic scenarios, source quality, missing fields, hard gate, recovery-loop status, action, and downgrade action. None has a positive final-target weight.

## Fake-Precision Audit

Exact values are retained in JSON and this audit only. The report presents CNY25-26 as the formal reader range. 002812's exact sensitivities are explicitly labeled broker-derived and zero weight.

## Checklist Conclusion

Shares, market cap, operating scenarios, EPS denominators, probabilities, anchor weights, source overlap, target horizon, zero-weight coverage, driver gates, and current-price upside all reconcile. Reproducibility remains PASS after the eligibility downgrade.
