# Full-Market Valuation Coverage Audit

## Coverage

- Priority company models: 16/16
- Candidate valuation rows: 73/73
- Report-wide valuation rows: 117/117; 116 priceable and 1 IPO/formal boundary.
- Priceable candidate ranges: 72/73
- Not priceable: 1/73
- Deduplicated report-wide ledger: 117 rows
- Priceable report-wide rows: 116
- Explicitly not priceable report-wide rows: 1

## Reproducibility

- 601225: house EV 19.76; target 19.76; stored 19.76; upside -0.1379.
- 002379: house EV 22.07; target 22.42; stored 22.42; upside 0.5516.
- 600346: house EV 17.18; target 17.18; stored 17.18; upside 0.0880.
- 002738: house EV 57.53; target 57.53; stored 57.53; upside 0.1106.
- 002048: house EV 23.92; target 23.92; stored 23.92; upside 0.0382.
- 002532: house EV 16.54; target 16.54; stored 16.54; upside 0.4808.
- 600595: house EV 8.61; target 8.61; stored 8.61; upside 0.4495.
- 601360: house EV 3.60; target 3.60; stored 3.60; upside -0.6026.
- 600918: house EV 7.42; target 7.42; stored 7.42; upside 0.4000.
- 300014: house EV 64.92; target 66.13; stored 66.13; upside 0.2037.
- 000987: house EV 7.76; target 7.76; stored 7.76; upside -0.0408.
- 600120: house EV 4.75; target 4.75; stored 4.75; upside -0.0186.
- 000703: house EV 16.17; target 16.26; stored 16.26; upside 0.1843.
- 000301: house EV 18.54; target 18.54; stored 18.54; upside 0.4773.
- 002414: house EV 20.62; target 20.59; stored 20.59; upside 0.4064.
- 002558: house EV 31.45; target 31.45; stored 31.45; upside 0.0639.

## Evidence Boundary

- Priority rows are company-specific models with explicit catalysts and invalidation.
- Non-priority candidate rows are screening ranges based on H1 deducted profit, H2 calibration and industry-matched methods.
- House targets never masquerade as broker targets.
- A missing valid current price produces `not_priceable`, not a fabricated target.

Full-Market Valuation Coverage Reproducibility: PASS
