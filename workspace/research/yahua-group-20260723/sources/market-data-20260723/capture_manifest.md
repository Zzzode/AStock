# Market-data capture manifest — 雅化集团（002497.SZ）

- **Capture date:** 2026-07-23 (Asia/Shanghai).
- **Provider:** Eastmoney `push2` / `push2his` interfaces. These are L2 market-data snapshots, not exchange-original daily files.
- **Purpose:** current-price anchor, a 2026-07-06 to 2026-07-23 event window, and a same-window lithium-peer / CSI 300 comparison. This material does not identify investor type, northbound holdings, margin balance, intraday order flow, or the cause of a price move.

| ID | File | Request | Coverage | SHA-256 | Use boundary |
|---|---|---|---|---|---|
| MKT-YH-Q-0723 | `eastmoney_quote_002497_20260723_raw.json` | `push2/stock/get`, `secid=0.002497` | 2026-07-23 close snapshot | `74077469c0ab22f7c59ad55fd9ac12c28b6791d809595e9efb3dda8a600a3621` | Price, turnover, market cap and L1 share-count cross-check only. |
| MKT-EVT-0723 | `eastmoney_event_window_20260706_20260723_raw.json` | `push2his/stock/kline/get`, daily bars | 雅化、天齐、赣锋、盛新与沪深 300，2026-07-06 to 2026-07-23 | `70763115938b2005bc1bfbebf322b5f421dc4c81a51cb9d1c1fd7c24294eed25` | Relative returns and liquidity context only; no causation or normalized peer valuation. |

## Interpretation safeguards

1. The response has no usable provider timestamp (`f124=0` in the quote response). The date is established by local capture date plus the final daily bar `2026-07-23`; it is not an intraday data stamp.
2. A disclosure-date return is an observation, not an announcement reaction. The disclosure-time audit is in `data/announcement_event_audit_20260723.md`.
3. The three lithium names are a cycle-sensitivity basket, not a comparable-company set for a direct P/E transfer. Their resource ownership, investment income and product mix differ materially from 雅化.
