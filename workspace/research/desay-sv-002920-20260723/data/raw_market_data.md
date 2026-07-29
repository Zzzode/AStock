# Raw Market Data — Desay SV (002920.SZ)

- Market cutoff: 2026-07-23, intraday. This is not an end-of-day closing snapshot.
- Currency: CNY. Market-cap figures are RMB bn; daily amount figures are RMB bn.
- Market-data sources are vendor structured feeds, not exchange end-of-day reference files. Two intraday snapshots differ because they were captured minutes apart; both are preserved rather than reconciled by assumption.

## Raw snapshots

| Snapshot | Time / date | Price | Change | Open | High | Low | Volume | Amount | Source / quality |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| M1 | 2026-07-23 13:30:12 CST | 83.29 | +1.10% | 82.26 | 83.46 | 80.87 | 3,406,263 shares | 0.2803 | `astock.cli market-snapshot 002920 --json`; Medium-high |
| M2 | 2026-07-23 intraday, collected immediately after M1 | 83.48 | +1.34% (+1.10) | 82.26 | 83.49 | 80.87 | 35,065 lots = 3,506,500 shares | 0.2887 | [Eastmoney quote endpoint](https://push2.eastmoney.com/api/qt/stock/get?secid=0.002920&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f84,f85,f116,f117,f164,f167,f168,f169,f170,f171); Medium |

M2 is the selected current-price anchor below because it includes shares, market cap and valuation fields. The M1/M2 price difference is an intraday timestamp difference; it is not an adjustment, corporate action, or data correction.

## Selected market snapshot (M2)

| Field | Value | Exact date / basis | Source | Limitation |
|---|---:|---|---|---|
| Price | RMB 83.48 | 2026-07-23 intraday | Eastmoney `f43` | Not an official closing price. |
| Day change | +1.34% / +RMB 1.10 | Versus RMB 82.38 prior close | Eastmoney `f170` / `f169` / `f60` | Intraday. |
| Intraday range | RMB 80.87–83.49; amplitude 3.18% | 2026-07-23 intraday | Eastmoney `f45` / `f44` / `f171` | Not a multi-day price range. |
| Trading amount | RMB 0.2887bn | 2026-07-23 intraday | Eastmoney `f48` | Partial-day amount. |
| Volume | 3.5065m shares | 2026-07-23 intraday | Eastmoney `f47` (lots) | Partial-day volume. |
| Turnover | 0.59% | 2026-07-23 intraday | Eastmoney `f168` | Partial-day rate. |
| Total shares | 596.8093m shares | Live quote field; reconciles to 2026Q1 share capital | Eastmoney `f84`; F2 | Live field rather than an exchange reference-share file. |
| Circulating shares | 596.6218m shares | Live quote field | Eastmoney `f85` | This is **circulating share capital**, not strict economically tradeable free float. |
| Total market cap | RMB 49.8216bn | Price × live total shares; vendor field | Eastmoney `f116` | Intraday. |
| Circulating market cap | RMB 49.8060bn | Price × live circulating shares; vendor field | Eastmoney `f117` | Intraday; not strict free-float market cap. |
| P/E (TTM) | 21.36x | Vendor live valuation field | Eastmoney `f164` | Vendor calculation methodology and timestamp; no forward PE is implied. |
| P/B | 3.29x | Vendor live valuation field | Eastmoney `f167` (scaled by 100) | Cross-check: price / 2026Q1 BPS 25.400256 ≈ 3.29x. |
| P/S | not disclosed | As of cutoff | — | Not calculated from a single quarter or presented as TTM. |
| 5-day average volume | not disclosed | As of cutoff | — | Historical daily endpoint was rate-limited; no partial-day or stale-volume proxy is used. |
| Northbound holding | not disclosed (current) | As of cutoff | — | No current official 深股通 holding extract was captured. A stale 2026-06-23 cached 1.76% field is deliberately not presented as current. |
| Lock-up / restricted-share schedule | not disclosed | As of cutoff | — | Cannot be inferred from share capital or top-ten shareholder tables. |

## Same-session benchmark performance

| Benchmark | Day change | Snapshot basis | Source / quality |
|---|---:|---|---|
| CSI 300 (000300) | +0.37% | 2026-07-23 intraday | [Eastmoney quote](https://push2.eastmoney.com/api/qt/stock/get?secid=1.000300&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170); Medium |
| Shenzhen Component (399001) | +0.79% | 2026-07-23 intraday | [Eastmoney quote](https://push2.eastmoney.com/api/qt/stock/get?secid=0.399001&fields=f43,f44,f45,f46,f47,f48,f57,f58,f60,f170); Medium |
| Desay SV (M2) | +1.34% | 2026-07-23 intraday | M2 above |

On this intraday basis only, 002920 outperformed CSI 300 by 0.97ppt and Shenzhen Component by 0.55ppt. This is a mechanical same-day comparison, not a relative-performance recommendation.

## Freshness and source-quality limits

- The latest complete live price/amount/share data is intraday. It must not be substituted for a 2026-07-23 official close.
- 1-week, 1-month, YTD and 1-year returns are **not disclosed in this packet** because a current daily-history extraction did not complete. An older 2026-06-23 runtime cache exists but is stale by 30 days and is excluded from current interval conclusions.
- Free float is not equated with `f85` circulating shares. No locked/strategic-holding adjustment has been estimated.
