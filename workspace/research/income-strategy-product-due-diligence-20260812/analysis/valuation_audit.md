# Valuation Audit — Cross-Asset Diagnostic

## Scope and result

The model is reproducible as a diagnostic: nine price-versus-historical-NAV arithmetic rows recalculated from source prices and explicitly dated NAVs; 508096 is intentionally blocked. This is not a finding that current valuation is known, and it does not approve an allocation.

## Arithmetic checks

For the nine comparable diagnostic rows, the calculation is price divided by dated NAV per unit minus one. Recalculation tolerance is 0.01 percentage points. Values are: 511010 +0.24%, 510880 +13.49%, 512890 +8.64%, 508069 +6.62%, 508011 +49.85%, 508068 +29.08%, 508077 +13.78%, 508055 +23.23% and 508080 -11.99%. The earlier NAV date and audit status are retained in every row. 508096 has no formula because its annual-report NAV figures are unreconciled.

## Forecast, target and comparability checks

- 2026E revenue, net profit, EPS, PE/PEG/PSG, share count and market cap are not applicable or not sufficient for this heterogeneous product universe; no issuer model is inferred.
- Target price, fair-value range and implied upside/downside are all explicitly not published.
- Same-session NAV/IOPV is absent for ETFs; current project-value/NAV bridges are absent for REITs. Therefore every mechanical ratio is a historical diagnostic, not a current premium/discount.
- Broker packet has ten rows and every valuation weight is 0.0; no weak source enters an anchor.

## Scenario and market-anchor checks

Bear/base/bull target bands are withheld because their required valuation drivers are missing. Market price is a point observation, not a market-implied cash-flow model. One-day volume/amount cannot serve as liquidity capacity or sentiment weight. Quarterly REIT distribution data are neither forecast cash nor a valuation denominator.

## Method fit and fake-precision checks

- Treasury ETF requires interest-rate sensitivity and IOPV work, not equity PE.
- Equity ETFs require current holdings, tracking and cash-quality work, not a generic dividend yield extrapolation.
- Public REITs require current asset valuation, project cash-flow, debt/capex and valuation-date bridges, not annualized Q2 distributions.
- 508096 requires NAV reconciliation before any price/NAV work.
- No target or allocation is produced, avoiding false precision.

## Reproducibility disposition

Model Reproducibility: PASS

PASS applies only to the disclosed date-mismatched diagnostic arithmetic and no-target controls. It does not mean valuation sufficiency, cash-target proof, strategy-return proof, implementation approval or live execution authorization. All ten actions remain WATCHLIST ONLY / q=0.
