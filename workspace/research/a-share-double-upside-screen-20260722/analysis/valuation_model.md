# Valuation Model

## Final Valuation Table

The formal valuation universe contains one name. 002497 passes the current-price, official-financial, company-driver, original-target, and model-reproducibility gates. Every other deep name is represented in the structured zero-weight companion packet.

| Ticker | Current | Bear | Base | Bull | Bull upside | Exact audit value | Reader range | Final upside | Action |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 002497 雅化集团 | 16.79 | 9.12 | 26.30 | 42.08 | 150.6% | 25.32 | 25-26 | 50.8% | Conditional core |

The exact value is retained only for reproducibility. The reader-facing output is CNY25-26. There is no base-case double.

## Three-Tier Targets

The 002497 scenarios vary shipments, lithium-price proxy, gross margin, opex/tax, net profit, EPS, and PE. Bear/base/bull use 90/120/130kt shipments, CNY1.14/2.63/3.34 EPS, and 8x/10x/12.6x PE, producing CNY9.12/26.30/42.08. Probabilities are 30%/50%/20%, producing a CNY24.302 operating-driver probability value.

002812's CNY30.96/67.08/103.20 range is retained only as a Dongwu-derived zero-weight sensitivity. The three values share one unverified 2027E EPS denominator and are not house targets.

## Relative / PEG / PSG Comparison

PEG is not primary because 2026 growth is measured from depressed cyclical bases. PSG cannot capture lithium inventory, hedge effects, separator utilization, or unit economics. Relative PE is used only after the earnings denominator is normalized. At the 002497 base EPS, a double requires 12.77x versus 10x in the base case.

## Seasonality Calibration

002497 H1 guidance of CNY1.10-1.30bn is not annualized. The base forecast requires CNY1.73-1.93bn in H2 and positive cash conversion. 002812 H1 guidance is evidence of recovery direction only; it is not a substitute for the missing 2027 operating bridge.

## Next-Quarter Threshold

002497 must deliver at least CNY1.73bn H2 parent profit, explain shipment, realized price, self-supply, inventory, and hedge effects, and move operating cash flow toward positive territory. 002812 remains zero weight until company evidence quantifies shipment, customer price, unit profit, effective utilization, yield, and cash conversion.

## Method and Assumption Bridge

002497 uses a cycle-adjusted operating-driver EPS/PE model. Civil explosives form a CNY0.50-0.60bn parent-profit floor; normalized lithium contribution varies by shipment and per-tonne economics. Inventory gains and hedge P&L receive zero normalized credit. 002812 has no positive-weight method while its company-driver gate is blocked.

## Market-Expectation Valuation Bridge

At CNY16.79, 002497 trades at 6.38x base 2026E EPS. A double to CNY33.58 requires 12.77x. The current price signals skepticism, but a five-month rerating still requires profit, cash, and cycle durability to validate together.

## Broker/Street Comparison

The original Dongwu reports state CNY42 for 002497 and CNY103 for 002812. Neither discloses the target horizon. The 002497 target receives a capped 10% external-anchor weight only after the company-driver gate passes. The 002812 target receives zero weight because its `blocks_valuation` gate remains active. Reports without explicit point targets receive zero external-target weight.

## Market-Implied Sentiment Anchor

The 002497 current price receives 10% weight. It prevents the recent drawdown from being treated as a free rerating opportunity. A zero-broker-weight, proportionally renormalized model produces CNY23.47; a 70% fundamental / 20% market / 10% broker mix produces CNY24.57; the main 80/10/10 model produces CNY25.32.

## Growth Earnings Dependency

002497 depends on lithium shipment, normalized per-tonne contribution, resource self-supply, gross margin, inventory and hedge normalization, and a stable civil-explosives floor. The base operating assumptions and the CNY42 external target partly come from the same Dongwu report; the external anchor is not independent confirmation.

## Full-Chain Classification Dependency

Driver-chain evidence is used only to validate company earnings. No downstream demand or capacity claim substitutes for company-specific shipment, price, margin, utilization, yield, or cash conversion. This rule is why 002812 remains zero weight despite an explicit point target.

## Zero-Weight Conditional Watch Scenarios

| Ticker | Current | Diagnostic bear | Diagnostic base | Diagnostic bull | Bull upside | Hard gate | Disposition |
|---|---:|---:|---:|---:|---:|---|---|
| 600150 中国船舶 | 33.02 | 29.0 | 50.1 | 68.9 | 108.7% | No explicit current target | Quality backup |
| 301308 江波龙 | 388.45 | 300 | 500 | 780 | 100.8% | Peak-cycle denominator; negative OCF | Observation |
| 002812 恩捷股份 | 47.84 | 30.96 | 67.08 | 103.20 | 115.7% | Company-driver evidence blocked | Zero-weight sensitivity |
| 002240 盛新锂能 | 27.65 | 21.6 | 39.2 | 59.0 | 113.5% | Cycle and negative OCF | Cycle backup |
| 300390 天华新能 | 55.88 | 56.4 | 79.8 | 102.4 | 83.3% | Bull below double hurdle | Observation |

The structured source of truth is `data/zero_weight_valuation_model_20260722.json`. These ranges are scenario diagnostics, never final targets.
