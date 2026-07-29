# Verified market data — 雅化集团（002497.SZ）

**As of:** 2026-07-23 close, Asia/Shanghai. Price and turnover are L2 Eastmoney snapshot data; total share count is L1 issuer disclosure cross-checked with the L2 snapshot. All returns are deterministic close-to-close calculations from the archived daily bars.

| Metric | Verified value | Evidence / permitted use |
|---|---:|---|
| Latest close | CNY17.75 | MKT-YH-Q-0723; current-price denominator. |
| Total shares | 1,152,562,520 | SHARE-26 L1; matches L2 `f84`. |
| Total market cap | CNY20.458bn | CNY17.75 × total shares; matches L2 `f116`. |
| Free-float shares / market cap | 1.060bn / CNY18.808bn | L2 only; do not elevate to L1. |
| 2026-07-23 amount / turnover | CNY0.837bn / 4.50% | Liquidity description only. |
| 2026-07-06 → 2026-07-07 | +10.00% | Observed one-day move; disclosure-time causality is unconfirmed. |
| 2026-07-06 → 2026-07-23 | -20.79% | Against equal-weight lithium observation basket -22.68% and CSI 300 -2.77%. |
| 2026-07-07 → 2026-07-23 | -27.99% | Underperformed equal-weight lithium observation basket by 5.24 percentage points. |
| 2026-07-07 → 2026-07-23 peak-to-cutoff drawdown | -27.99% | Same as disclosed-date close to cutoff, not a 52-week drawdown. |

## Event-language control

The CNINFO metadata proves a **7 July disclosure date**, but not precise intraday publication time. The report may state: “雅化在业绩预告披露日收涨 10.0%，其后截至 7 月 23 日回落 28.0%。” It may not state: “业绩预告导致/推动 7 月 7 日涨停。”

## Model-use control

1. The CNY17.75 close and CNY20.458bn equity value can be used as the valuation-date denominator.
2. Market price does not validate external EPS, H2 earnings persistence or a target multiple.
3. The peer basket establishes sector drawdown context only. It cannot supply a direct valuation multiple, beta, or alpha conclusion.

Source paths: `sources/market-data-20260723/eastmoney_quote_002497_20260723_raw.json`, `sources/market-data-20260723/eastmoney_event_window_20260706_20260723_raw.json`, `sources/official-financial-20260723/002497_2025_profit_distribution_implementation.pdf`, and `data/announcement_event_audit_20260723.md`.
