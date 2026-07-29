# Verified Market Data — Desay SV (002920.SZ)

## Verification result

**Status: PASS for intraday quote fields; limited for historical, northbound and lock-up fields.** The project-native market snapshot (M1) and Eastmoney structured quote (M2) agree on the trading day, prior close, open and low, and show a normal intraday price/volume progression. M2 share count reconciles to the 2026Q1 reported share capital within the known 187,500-share circulating-versus-total difference.

| Item | Verified value | Verification | Confidence |
|---|---:|---|---|
| Current price anchor | RMB 83.48 intraday | M2 plus M1 captured minutes earlier at RMB 83.29 | Medium-high for intraday quote; not an EOD close |
| Prior close | RMB 82.38 | M1 and M2 agree | Medium-high |
| Intraday high / low | RMB 83.49 / RMB 80.87 | M2; M1 high RMB 83.46, low RMB 80.87 | Medium-high |
| Total shares | 596.8093m | M2 `f84` = 2026Q1 reported share capital | High |
| Circulating shares | 596.6218m | M2 `f85`; difference to total shares is 187,500 | Medium |
| Total market cap | RMB 49.8216bn | M2 vendor field; mechanically consistent with M2 price × total shares | Medium-high |
| P/E TTM | 21.36x | M2 `f164`; not a forward multiple | Medium |
| P/B | 3.29x | M2 `f167` and price / reported 2026Q1 BPS cross-check | Medium-high |
| Current northbound holding | not disclosed | No current official 深股通 extract collected | Not available |
| Strict free float / current lock-up | not disclosed | No official locked/strategic holding schedule collected | Not available |

## Verified-use boundaries

- Use RMB 83.48 only with the label **2026-07-23 intraday**, and show M1 (RMB 83.29 at 13:30:12 CST) if an exact intraday timestamp is material.
- Do not infer 5-day average volume, multi-week return, free float, lock-up, northbound holding or forward valuation from the available intraday snapshot.
- The benchmark comparison is valid only for the same intraday snapshot: 002920 +1.34%, CSI 300 +0.37%, Shenzhen Component +0.79%.
- A valuation model should refresh price, shares, P/E and P/B immediately before final publication if the report is issued after this data cutoff.

## Data-quality label

`market_quote: medium-high intraday; market_cap_and_shares: medium-high; valuation_multiples: medium; historical_intervals/northbound/lockup: not disclosed.`
