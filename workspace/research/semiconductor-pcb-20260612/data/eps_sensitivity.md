# EPS / Net Profit Sensitivity Framework

**Base inputs:** latest structured financial period plus archived market-cap snapshot. Market cap unit is CNY 100mn from `current_market_snapshot.md`.

| Ticker | Latest NPP | Snapshot market cap | Implied latest-period P/NPP | +10% NPP | -10% NPP | Margin -2pct proxy | Data quality |
|---|---:|---:|---:|---:|---:|---:|---|
| 002463 | 12.42亿元 | 2407.36亿元 | 193.8x | 176.2x | 215.4x | 215.4x | structured_financial + archived_market_cap |
| 300476 | 12.88亿元 | 2831.00亿元 | 219.7x | 199.8x | 244.1x | 240.3x | structured_financial + archived_market_cap |
| 002916 | 8.50亿元 | 2522.95亿元 | 296.7x | 269.8x | 329.7x | 351.2x | structured_financial + archived_market_cap |
| 600183 | 11.58亿元 | 3622.40亿元 | 312.8x | 284.3x | 347.5x | 363.9x | structured_financial + archived_market_cap |
| 603186 | 0.31亿元 | 267.01亿元 | 863.5x | 785.0x | 959.5x | 4282.3x | structured_financial + archived_market_cap |

## Interpretation Rules

- This is not a target-price model.
- Latest-period P/NPP is not annualized and must not be compared directly to annual PE.
- The margin -2pct proxy subtracts 2% of latest-period revenue from latest-period net profit parent, approximating gross-margin sensitivity before tax/expense effects.
- A full top-tier model still requires segment revenue, annual EPS forecasts, share count and customer-chain revenue exposure.
