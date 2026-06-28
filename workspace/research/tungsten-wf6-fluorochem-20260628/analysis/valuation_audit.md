# Valuation Audit

## Arithmetic Checks

- Status: PASS
- Rows checked: 18
- Issues: none

## Forecast Availability

- Status: PASS
- 2026E revenue, net profit and EPS are available for all 18 covered tickers through Q1 seasonality calibration.
- Limitation: forecasts are AStock comparable estimates from 2026Q1/2025A, not paid Wind/Choice consensus.

## Target Price Comparability

- Status: PASS with limitation
- Public broker target anchors found: 1 ticker(s).
- Missing paid consensus is disclosed as `not disclosed`; broker targets are not used as AStock targets.

## Final Valuation Completeness

- Status: PASS
- Missing fields: none

## Scenario Bands

- Status: PASS
- Issues: none

## Market-Implied Sentiment Anchor

- Status: PASS
- Every ticker has intrinsic/base value, market anchor, final weights, final target, sentiment premium and action logic.

## Fake Precision Flags

- Target prices are shown to two decimals in machine tables because the model is per-share; prose interpretation should use ranges and action labels.
- Q1 annualization is not treated as paid consensus. It is a comparability bridge and must be refreshed after Q2.
- Electronic-specialty-gas names with high sentiment premium are event-driven validation assets, not automatically undervalued stocks.

## Required Fixes

- Gate status: PASS
- Before any future publication update, refresh quotes, Q2 thresholds, broker/Street comparison and source registry.
