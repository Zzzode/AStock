# Valuation Coverage Reconciliation

This artifact reconciles the panoramic AIDC stock pool to the published target-price combo.

| Step | Count | Meaning | Gate consequence |
|---|---:|---|---|
| Full-chain nodes | 85 | Industry-chain nodes from upstream compute to downstream demand anchors | Must be mapped before valuation narrowing |
| Full-pool mapped companies | 173 | Deduplicated A-share / listed / investable mappings from full-chain nodes | Every row needs company-level valuation disposition |
| Core valuation candidates | 58 | Companies mapped to at least one core valuation node | Every row needs company-level card and valuation disposition |
| Original target-price combo | 18 | Rows in current_valuation_model_20260630 with current-price, financial, Street/broker and model reproducibility package | These retain the original three-anchor target-price model |
| Extended target-price/fair-value combo | 38 | Previously unmodeled core candidates now refreshed with current price, share count, 2026E denominator and scenario reproducibility; split into 13 explicit broker-target, 24 house fair-value and 1 PS/SOTP models | These receive explicit target price/upside in the expanded core-candidate model |
| Explicit watchlist downgrades | 3 | Rows with insufficient positive EPS/model denominator or legacy no-Street treatment | These are kept as watchlist-only and excluded from investable target-price recommendations |

The target-price combo is now split by evidence quality: explicit broker-target rows publish broker-calibrated targets; house fair-value rows publish AStock fair values without Street weight; PS/SOTP rows publish milestone targets; insufficient-denominator rows are explicit downgrades rather than unresolved placeholders.
