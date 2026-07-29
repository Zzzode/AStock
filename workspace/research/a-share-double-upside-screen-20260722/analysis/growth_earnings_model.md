# Growth Earnings Model

## Modeling Boundary

The model separates base business from growth drivers and never converts a broad theme directly into EPS. A positive-weight scenario must vary operating drivers, gross profit, opex/tax, net profit, EPS, and valuation. Inventory gains and hedge P&L receive zero normalized credit.

## 002497 雅化集团 — Positive-Weight Driver Bridge

The civil-explosives business is the earnings floor. Lithium shipment, realized-price proxy, normalized per-tonne contribution, and self-supply are the growth variables. The original Dongwu report anchors the base case at about 120kt shipments, CNY17.052bn revenue, 27.04% gross margin, CNY3.032bn parent net profit, and CNY2.63 EPS. Bear and bull parameters are explicit AStock judgments rather than company guidance.

| Scenario | Lithium shipments | Lithium price proxy | Consolidated revenue | Gross margin / gross profit | Opex, tax and other burden | Civil-explosives parent-profit floor | Normalized lithium parent-profit contribution | Parent NP | EPS | PE / value |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Bear | 90kt | CNY120k/t | CNY12.0bn | 20.0% / CNY2.40bn | CNY1.09bn | CNY0.50bn | CNY0.81bn, or CNY9k/t | CNY1.31bn | CNY1.14 | 8x / CNY9.12 |
| Base | 120kt | CNY165k/t | CNY17.052bn | 27.04% / CNY4.611bn | CNY1.576bn | CNY0.575bn | CNY2.46bn, or CNY20.5k/t | CNY3.035bn | CNY2.63 | 10x / CNY26.30 |
| Bull | 130kt | CNY180k/t | CNY19.5bn | 28.5% / CNY5.558bn | CNY1.708bn | CNY0.60bn | CNY3.25bn, or CNY25k/t | CNY3.85bn | CNY3.34 | 12.6x / CNY42.08 |

The base parent-profit bridge reconciles to the broker's CNY3.032bn forecast within rounding. The bull no longer reaches CNY42 solely by applying 16x to the same CNY2.63 denominator; it requires higher volume, normalized per-tonne contribution, gross profit, and EPS. H1 guidance of CNY1.10-1.30bn still requires at least CNY1.73bn in H2 to reach the base forecast. Positive H2 operating cash conversion is a separate gate.

## 002812 恩捷股份 — Zero-Weight Sensitivity

The original Dongwu report forecasts more than 16bn sqm of 2026 shipments, CNY2.279bn 2026E parent NP, CNY5.068bn 2027E parent NP, and CNY5.16 2027E EPS. The CNY30.96/CNY67.08/CNY103.20 range is a mechanical 6x/13x/20x sensitivity on that one EPS denominator. Company filings confirm recovery direction but do not quantify the customer price, shipment, realized unit profit, effective utilization, new-line yield, or cash bridge needed to rebuild the denominator independently. `blocks_valuation=true` therefore remains active: no probability, blended target, or expected upside is published.

## Structured Zero-Weight Watch Models

`data/zero_weight_valuation_model_20260722.json` is the canonical companion packet for 600150, 301308, 002812, 002240, and 300390. It records current price, diagnostic bear/base/bull values, source quality, missing fields, recovery-loop status, hard gate, and downgrade action for each name. These rows are monitoring diagnostics, not final targets.

## Cross-Model Validation

Only 002497 passes the company-level valuation gate and receives a formal blended range. The five zero-weight rows remain useful for monitoring operating thresholds, but no theme, external point target, or house-only range can override a driver or cash-conversion blocker.
