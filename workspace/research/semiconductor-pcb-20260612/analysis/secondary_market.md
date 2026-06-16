# Secondary-Market and Catalyst Analysis

## Data Boundary

Market data now uses the Tencent 2026-06-16 quote snapshot for current public price, total market capitalization, PE and PB. Eastmoney realtime failed, so this remains a public quote proxy rather than terminal-grade valuation.

## Secondary-Market Signals Available

| Signal | Available? | Comment |
|---|---|---|
| Current price | Public proxy | Tencent 2026-06-16 intraday quote snapshot |
| Market cap | Public proxy | Tencent 2026-06-16 total market-cap field |
| PE from broker forecasts | Public proxy | Core names have broker forecast lines; some are multi-source ranges |
| Relative performance | Public proxy | Yahoo daily price series covers core and watchlist names |
| Valuation percentile | Public proxy | Baidu one-year PE/PB percentile covers core and watchlist names |
| Institutional positioning | Public proxy | Official holders, Sina holders, important-institution data and Eastmoney dayline fund-flow proxy are available; terminal-grade positioning is unavailable |
| Liquidity / turnover | Not complete | Snapshot mentions turnover readable but not systematically extracted |

## Crowding Read-Through

- Huazheng New Materials: updated Zheshang model implies 2026E/2027E PE about 56.4x/40.2x on the refreshed Tencent market cap; the old archived-mcap warning is now superseded.
- Shenghong Technology: indicative PE looks attractive if 2026-2028 profit forecasts are accurate, but the forecast range is wide and H-share target is not directly comparable to A-share.
- Shennan Circuits: 2026E/2027E/2028E PE moves from 44.4x to 32.3x to 23.7x if forecasts are met; this is a delivery-driven de-rating path.
- Shengyi Technology: target references are below the refreshed Tencent price, implying that public target upside has been absorbed by the market.

## Catalyst Calendar

| Catalyst | Why it matters | What to verify |
|---|---|---|
| 2026 interim / quarterly reports | First financial checkpoint after the AI PCB re-rating | Revenue growth, gross margin, capex, backlog, cash flow |
| NVIDIA Rubin / Rubin Ultra platform detail | Defines board count, material grade, backplane/midplane route | Supplier exposure, PCB value content, M9 demand |
| North American ASIC / TPU ramp | Validates the non-NVIDIA demand leg | HDI demand, customer diversification, order visibility |
| M8/M9 CCL price and lead time | Tests material bottleneck thesis | ASP durability, pass-through, margin capture |
| Equipment order backlog | Tests capex second-derivative thesis | Drilling, LDI, electroplating and consumables orders |

## Conclusion

The report should not claim the sector is cheap or expensive as a whole. It can state that valuation dispersion and evidence quality differ sharply, and that the next upgrade must come from earnings delivery and customer-chain verification rather than narrative strength alone.
