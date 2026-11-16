# ETF Public-Series Admissibility Diagnostic

- Status: **not admissible** as stable-5% total-return evidence; `q=0`.
- Source: `sources/probe-public-etf-price-r0-20260814/e69a5fc85d6b19f71a5ace6738bc0c3c0b32835b7829fc54fcc7d34453640dda.portfolio.replay.json` (`SHA-256 8829c0a065aa688c874212500c345c7dd92aff6c88b2bba760f7de7921b15217`).
- Source-declared basis: `forward_adjusted_or_unknown`.
- Protocol: exploratory post-source diagnostic; neither predeclared nor frozen.
- Boundary: frozen tier-3 public daily bars. No independently verified market-price,
  NAV, distribution, corporate-action, tax, tradability or execution ledger exists.

At the 10-bps turnover sensitivity, the arithmetic public-series diagnostic is
5.09%; 281
of 611 complete rolling five-year public-series windows
are below 5%, with a 3.88%
minimum. These descriptive outputs cannot confirm or reject an investor
total-return result because the source adjustment basis is unresolved.

| One-way turnover cost (bps) | Annualized public-series change | Maximum drawdown | 5Y windows below 5% |
|---:|---:|---:|---:|
| 0 | 5.21% | -12.38% | 226 / 611 |
| 5 | 5.15% | -12.44% | 256 / 611 |
| 10 | 5.09% | -12.49% | 281 / 611 |
| 20 | 4.97% | -12.60% | 311 / 611 |

The diagnostic uses the previous observed close at the first observed session
of each month, applies a one-session delay, and mechanically maps up to two
risk sleeves from 510300/510880/518880 alongside 511010. It is not an
allocation instruction, a pre-registered test or a strategy result.
