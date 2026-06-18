# Secondary Market Analysis

Market data now uses the Tencent 2026-06-18 quote refetch, with embedded 2026-06-17 post-close timestamps, for current public price, total market capitalization, PE and PB. Eastmoney realtime failed, so this remains a public quote proxy rather than terminal-grade valuation.

| Signal | Availability | Treatment |
|---|---|---|
| Current price | Public proxy | Tencent 2026-06-18 refetch / 2026-06-17 embedded timestamp snapshot |
| Market cap | Public proxy | Tencent 2026-06-18 total market-cap field |
| Valuation percentile | Public proxy | Baidu/AkShare/Yahoo historical valuation and price proxies |
| Fund flow | Public proxy | Eastmoney dayline and intraday fund-flow proxies; not terminal-grade order flow |
| Stock Connect | Public proxy | HKEX quarterly and Eastmoney participant/custodian bridge; no beneficial-owner data |
| Margin financing | Public proxy + partial official | Eastmoney public margin proxies; SSE official data for Shanghai names; SZSE official route still resets/timeouts locally |

Secondary-market evidence is useful for crowding and risk triggers only. It does not prove fundamental demand, institutional ownership, beneficial-owner positioning, active/passive fund labels or terminal-grade order flow.
