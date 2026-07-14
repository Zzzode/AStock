# Valuation Algorithm and Reproducibility

## 1. Inputs

The model uses the 2026-07-14 13:27 realtime price of CNY260.37, 18.31607532 hundred-million shares, a CNY199.87 auditable broker target, a CNY225 market-sentiment anchor, and weights of 75% fundamental / 15% Street / 10% market. All model monetary inputs below are in CNY100m unless stated otherwise.

## 2. SOTP formula

For each segment:

`Segment Value = Segment Net Profit × Segment Multiple`

The non-optical fixed value is:

`252.0 + 462.0 + 18.2 + 52.8 + 1.5 = 786.5`

The fundamental anchor is:

`Fundamental Anchor = (786.5 + Optical NP × Optical PE − 182.0) / 18.31607532`

The CNY182.0 conservatism overlay equals 4.75% of gross SOTP value. It is a transparent reserve for capex, financing cost, working capital and unproven utilization; it is not silently presented as net debt.

The base case is:

`(786.5 + 95.0 × 32 − 182.0) / 18.31607532 = CNY198.96`

Final target:

`198.96 × 75% + 199.87 × 15% + 225.00 × 10% = CNY201.70`

Upside/downside:

`201.70 / 260.37 − 1 = -22.53%`

## 3. Optical sensitivity

| Optical 2027E NP CNY100m | 26x fundamental | 32x fundamental | 38x fundamental | 26x final target | 32x final target | 38x final target |
|---:|---:|---:|---:|---:|---:|---:|
| 80 | 146.57 | 172.77 | 198.98 | 162.40 | 182.06 | 201.71 |
| 95 | 167.86 | 198.98 | 230.10 | 178.37 | 201.71 | 225.05 |
| 110 | 189.15 | 225.18 | 261.22 | 194.34 | 221.37 | 248.39 |

The table makes the valuation dependency visible: the current CNY260.37 price is above even the 2027 optical NP CNY110bn / 38x PE fundamental cell. It can only be justified by further profit growth, a higher multiple, or both.

## 4. H1 update treatment

The official H1 preview of CNY29-30bn parent net profit in CNY100m units improves 2026E denominator confidence. The midpoint completes 43.38% of House CNY6800m 2026E net profit, leaving CNY3850m for H2. Because the preview does not split optical revenue, margin or data-center investment returns, it validates the company-level earnings bridge but does not change the 2027 SOTP.
