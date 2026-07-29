# Raw market data — 雅化集团（002497.SZ）

**Data cutoff:** 2026-07-23 close, Asia/Shanghai. The current snapshot and event-window raw payloads are archived in `sources/market-data-20260723/`; they supersede the pre-close 2026-07-22 snapshot for valuation-date calculations. Eastmoney is L2 market data, not an exchange-original daily-file source.

## Latest close snapshot — 2026-07-23

| Raw field | Meaning | Raw value | Display value |
|---|---|---:|---:|
| `f43` | close, scaled by 100 | 1775 | CNY17.75 |
| `f60` | prior close, scaled by 100 | 1679 | CNY16.79 |
| `f44` / `f45` / `f46` | high / low / open, scaled by 100 | 1809 / 1686 / 1713 | CNY18.09 / 16.86 / 17.13 |
| `f169` / `f170` | price change / percentage change, scaled by 100 | 96 / 572 | +CNY0.96 / +5.72% |
| `f47` / `f48` / `f168` | volume / amount / turnover | 476,322 / 836,782,228.09 / 450 | 476,322 lots / CNY0.837bn / 4.50% |
| `f84` / `f85` | total / free-float shares | 1,152,562,520 / 1,059,587,615 | 1.153bn / 1.060bn shares |
| `f116` / `f117` | total / free-float market cap | 20,457,984,730.00 / 18,807,680,166.25 | CNY20.458bn / CNY18.808bn |

`f124=0`; consequently, the provider response supplies no usable intraday timestamp. The date is established by the capture date and final daily bar, not a time-of-day assertion.

## Disclosure-window daily observations — not an event-causality test

| Date | Close | Daily return | Turnover | Amount | Observation only |
|---|---:|---:|---:|---:|---|
| 2026-07-06 | 22.41 | +2.47% | 5.44% | CNY1.296bn | Day before catalogue disclosure date. |
| 2026-07-07 | 24.65 | +10.00% | 1.67% | CNY0.437bn | Disclosure-date close; precise release timing unconfirmed. |
| 2026-07-08 | 22.19 | -9.98% | 12.25% | CNY3.000bn | High-turnover reversal day. |
| 2026-07-09 | 20.20 | -8.97% | 11.60% | CNY2.517bn | Continuation of negative price path. |
| 2026-07-10 | 18.70 | -7.43% | 10.44% | CNY2.139bn | Continuation of negative price path. |
| 2026-07-23 | 17.75 | +5.72% | 4.50% | CNY0.837bn | Cutoff close / valuation denominator. |

## Market-cap cross-check

`CNY17.75 × 1,152,562,520 shares = CNY20,457,984,730`, matching field `f116` exactly. The share count is independently supported by `SHARE-26` (L1 issuer corporate-action disclosure); the price is L2.

## What this raw packet does not contain

- Exchange-original daily bars, intraday disclosures, order-book data, fund-flow direction, northbound holdings, margin-balance data or institutional ownership changes.
- A causality test connecting the earnings preview to any observed price return.
- A directly comparable index for civil explosives or a normalized peer valuation set.
