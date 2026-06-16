# Pengding Market Positioning Evidence

**Sources:** Yahoo Finance chart API; Eastmoney `push2his` fund-flow daykline.

**Boundary:** Public daily price and fund-flow proxy. This is not terminal-grade order flow, not beneficial-owner positioning and not complete institutional holdings. Valuation percentile is stored separately in `data/pengding_valuation_history.md`.

## Price performance

| Ticker | Records | First date | Last date | First adj close | Last adj close | Period return | Max drawdown | Data quality |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| 002938 | 279 | 2025-04-21 | 2026-06-15 | 27.63 | 104.64 | 278.76% | -33.32% | daily_price_yahoo |

## Eastmoney fund-flow proxy

| Ticker | Name | Records | Latest date | Latest main net inflow | 30-row sum main net inflow | Latest close | Latest pct chg |
|---|---|---:|---:|---:|---:|---:|---:|
| 002938 | 鹏鼎控股 | 30 | 2026-06-15 | -5.56亿元 | -10.14亿元 | 104.64 | 3.07% |

## Interpretation

- Pengding now has the same public price-performance and Eastmoney daily fund-flow proxy treatment as the existing watchlist names.
- Price performance should be read together with official delivery evidence: 2025 automotive/server/other board revenue grew 106.67% YoY, but 2026Q1 revenue/profit declined slightly YoY.
- Pengding valuation percentile was later refreshed through AkShare/Baidu and is stored in `data/pengding_valuation_history.md`; read the price and fund-flow data together with that valuation evidence.
