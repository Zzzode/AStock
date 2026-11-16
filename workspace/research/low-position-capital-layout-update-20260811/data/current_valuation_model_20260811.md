# Current Valuation Disposition — 2026-08-11 Update

This update publishes **no new house price target**. All 13 covered names have an explicit current-price valuation-eligibility disposition; the four primary names are shown first, with broker targets used only as external references.

| Ticker | 8/10 close | External reference only | Updated status | Blocking evidence |
|---|---:|---:|---|---|
| 000703 恒逸石化 | 18.18 | CNY16.50–17.60 | Remove from low-position list | At adjusted one-year high; H1 OCF negative. |
| 002379 宏桥控股 | 19.76 | CNY29.00 | Event-driven validation | H1 preview; adjusted-NP/statutory-NP mismatch; no H1 OCF. |
| 300014 亿纬锂能 | 55.22 | CNY77 / CNY103, not averaged | Event-driven validation | H1 preview, Q1 OCF negative, target and denominator dispersion. |
| 002497 雅化集团 | 19.09 | CNY42.00 | Highest-upside monitoring priority | H1 preview, FY/Q1 OCF negative, H2 and cash bridge still unproven. |

The historical high-upside group is separately classified in [high_upside_recheck_20260811.md](high_upside_recheck_20260811.md). No historic scenario value is rolled into a current house target.

## Full-Coverage Zero-Target Dispositions

| Group | Tickers | Current disposition |
|---|---|---|
| Historical high-upside recheck | 002432, 000623, 600739, 000685, 600150, 301308 | Watchlist only; each row records the current close, evidence gap, zero house weights and a re-entry validation condition. |
| Conditional / cycle watch | 002812, 002240, 300390 | Watchlist only or zero-weight sensitivity; no price target or positive broker blend weight. |

The paired broker packet uses `not disclosed` rather than a null price/upside field for genuine no-target rows. This is an explicit source gap, never a zero price, target or return assumption.

The paired JSON uses an explicit `not_published` field disposition for FY2026 revenue/NP/EPS, bear/base/bull, final target and upside. These are intentionally not zero values: the current evidence does not support independent house scenarios. All three house-target blend weights are therefore 0.00; the separately disclosed broker `external_anchor_weight_cap` remains an evidence-quality cap rather than a valuation or portfolio weight.
