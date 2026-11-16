# Raw Official Financials — 2026-08-11

**Scope:** 13 supplied tickers (the task wording says 14, but only 13 codes were supplied). Figures are exact CNY strings in the paired JSON; only official CNINFO API/PDF evidence was used. `600150` values were mechanically converted from its disclosure unit of CNY10,000, with native amounts retained in JSON.

## Data-quality boundary

- FY2025 and 2026Q1: issuer annual/quarterly reports; high-quality primary evidence. Q1 reports are unaudited where the issuer states so.
- 2026H1 actual filings exist only for `000703` and `301308` at the 2026-08-11 cutoff. Other available H1 evidence is an issuer preliminary range, not an actual result.
- `600739` and `600150`: no H1 interim report or title-matched H1 earnings preview found in archived CNINFO searches; see `sources/probe-20260811/h1_unavailability_probe_20260811.json`.
- Growth rates are deliberately not re-keyed in this first pass: multiple issuers restated comparatives. Use the cited headline-table source before asserting YoY growth.

## FY2025 and 2026Q1 reported metrics

| Ticker | Company | Period | Revenue | Attributable NP | Deducted NP | Operating CF | Official announcement |
|---|---|---|---:|---:|---:|---:|---|
| 000703 | 恒逸石化 | FY2025 | CNY113527493619.63 | CNY258331586.27 | CNY141243770.17 | CNY4625435458.61 | 1225104872 (2026-04-15) |
| 000703 | 恒逸石化 | 2026Q1 | CNY29948073038.54 | CNY1994792155.15 | CNY1939820963.77 | CNY-2573369108.63 | 1225104881 (2026-04-15) |
| 002379 | 宏桥控股 | FY2025 | CNY156720854229.71 | CNY17863539928.79 | CNY-369131323.85 | CNY23994898583.36 | 1225021359 (2026-03-21) |
| 002379 | 宏桥控股 | 2026Q1 | CNY40932856974.81 | CNY6757771302.83 | CNY6795854852.29 | CNY9237895186.86 | 1225180703 (2026-04-25) |
| 300014 | 亿纬锂能 | FY2025 | CNY61469630776.09 | CNY4134303670.89 | CNY3095709718.80 | CNY7492131666.79 | 1225045391 (2026-03-28) |
| 300014 | 亿纬锂能 | 2026Q1 | CNY20679868145.38 | CNY1446303779.36 | CNY1114674451.30 | CNY-365647426.63 | 1225182164 (2026-04-25) |
| 002497 | 雅化集团 | FY2025 | CNY8543171263.90 | CNY632380161.87 | CNY693585735.36 | CNY-569778007.60 | 1225181781 (2026-04-27) |
| 002497 | 雅化集团 | 2026Q1 | CNY2830218496.20 | CNY338821317.99 | CNY356555349.32 | CNY-430615777.34 | 1225181791 (2026-04-27) |
| 002432 | 九安医疗 | FY2025 | CNY1365588936.68 | CNY2266748271.38 | CNY2292144672.33 | CNY-166803216.90 | 1225246455 (2026-04-29) |
| 002432 | 九安医疗 | 2026Q1 | CNY301482711.39 | CNY293533252.50 | CNY345084121.26 | CNY-92475267.73 | 1225246465 (2026-04-29) |
| 000623 | 吉林敖东 | FY2025 | CNY2335191263.80 | CNY2395240134.98 | CNY2200066967.46 | CNY272258821.17 | 1225117576 (2026-04-18) |
| 000623 | 吉林敖东 | 2026Q1 | CNY514094926.10 | CNY865999722.23 | CNY869402802.47 | CNY10701377.15 | 1225254025 (2026-04-30) |
| 600739 | 辽宁成大 | FY2025 | CNY9901861758.74 | CNY736554408.16 | CNY776150205.08 | CNY337635427.09 | 1225179691 (2026-04-25) |
| 600739 | 辽宁成大 | 2026Q1 | CNY1991034487.76 | CNY550963441.10 | CNY554951092.47 | CNY-175879265.68 | 1225256597 (2026-04-30) |
| 000685 | 中山公用 | FY2025 | CNY4611966487.51 | CNY1879358032.92 | CNY1786345825.48 | CNY297655046.67 | 1225194087 (2026-04-25) |
| 000685 | 中山公用 | 2026Q1 | CNY1005926676.26 | CNY583327240.07 | CNY581445435.35 | CNY-26929243.60 | 1225254079 (2026-04-30) |
| 600150 | 中国船舶 | FY2025 | CNY151977991200 | CNY7848378200 | CNY6126096600 | CNY7766831700 | 1225261150 (2026-04-30) |
| 600150 | 中国船舶 | 2026Q1 | CNY43312405200 | CNY4832278000 | CNY4767343200 | CNY8151528800 | 1225261166 (2026-04-30) |
| 301308 | 江波龙 | FY2025 | CNY22766169990.55 | CNY1423298162.88 | CNY1289178618.90 | CNY-1201201037.10 | 1225214128 (2026-04-28) |
| 301308 | 江波龙 | 2026Q1 | CNY9908726244.41 | CNY3862236561.17 | CNY3942639469.07 | CNY-2874539454.35 | 1225214140 (2026-04-28) |
| 002812 | 恩捷股份 | FY2025 | CNY13632727136.01 | CNY142548339.91 | CNY110802429.81 | CNY1143637807.97 | 1225148267 (2026-04-23) |
| 002812 | 恩捷股份 | 2026Q1 | CNY3907690531.54 | CNY260308751.63 | CNY260959203.60 | CNY206660110.96 | 1225148276 (2026-04-23) |
| 002240 | 盛新锂能 | FY2025 | CNY5064315775.69 | CNY-888079510.10 | CNY-812336830.65 | CNY949962734.60 | 1225044105 (2026-03-28) |
| 002240 | 盛新锂能 | 2026Q1 | CNY3284048555.59 | CNY464035684.07 | CNY622318509.18 | CNY-667158854.50 | 1225255367 (2026-04-30) |
| 300390 | 天华新能 | FY2025 | CNY7548826104.54 | CNY402189233.13 | CNY150340015.73 | CNY-321825657.49 | 1225077003 (2026-04-02) |
| 300390 | 天华新能 | 2026Q1 | CNY3200150765.28 | CNY968906491.73 | CNY945718935.46 | CNY-183248547.52 | 1225160904 (2026-04-24) |

## 2026H1 status

| Ticker | Status | Revenue | Attributable NP | Deducted NP | OCF | Official announcement / gap |
|---|---|---:|---:|---:|---:|---|
| 000703 | interim_report | CNY67309305318.81 | CNY5901665221.78 | CNY5886084675.39 | CNY-487952906.18 | 1225467439 (2026-08-11) |
| 002379 | official_earnings_preview | not disclosed | CNY15000000000–16000000000 | CNY14900000000–15900000000 | not disclosed | 1225418343 (2026-07-11); preliminary |
| 300014 | official_earnings_preview | not disclosed | CNY3130084300–3370860100 | CNY2429625300–2603170000 | not disclosed | 1225371777 (2026-06-15); preliminary |
| 002497 | official_earnings_preview | not disclosed | CNY1100000000–1300000000 | CNY1125000000–1315000000 | not disclosed | 1225411869 (2026-07-07); preliminary |
| 002432 | official_earnings_preview | not disclosed | CNY2800000000–3400000000 | CNY2850000000–3450000000 | not disclosed | 1225424699 (2026-07-15); preliminary |
| 000623 | official_earnings_preview | not disclosed | CNY1922310000–2178620000 | CNY2088310000–2344620000 | not disclosed | 1225423188 (2026-07-15); preliminary |
| 600739 | not_found_in_official_search | not disclosed | not disclosed | not disclosed | not disclosed | CNINFO H1 report + preview searches: no result by cutoff |
| 000685 | official_earnings_preview | not disclosed | CNY1330955100–1546785700 | CNY1320224300–1534314700 | not disclosed | 1225423704 (2026-07-15); preliminary |
| 600150 | not_found_in_official_search | not disclosed | not disclosed | not disclosed | not disclosed | CNINFO H1 report + preview searches: no result by cutoff |
| 301308 | interim_report | CNY24088363284.95 | CNY10576875808.95 | CNY10047374676.56 | CNY-3151429914.77 | 1225467150 (2026-08-11) |
| 002812 | official_earnings_preview | not disclosed | CNY736000000–900000000 | CNY762000000–930000000 | not disclosed | 1225417346 (2026-07-10); preliminary |
| 002240 | official_earnings_preview | not disclosed | CNY1000000000–1200000000 | CNY1300000000–1500000000 | not disclosed | 1225415616 (2026-07-09); preliminary |
| 300390 | official_earnings_preview | not disclosed | CNY2200000000–2400000000 | CNY2161700000–2361700000 | not disclosed | 1225417014 (2026-07-10); preliminary |

## Notable issuer disclosures / caveats

| Ticker | Period | Issuer disclosure note |
|---|---|---|
| 000703 | 2026H1 | 2026H1 comparatives were restated for an accounting-policy change and a same-control business combination. |
| 002379 | 2026H1 | 2026H1 forecast: aluminum selling prices rose and interest expense fell; comparatives are restated after the Hontuo same-control merger. The forecast is unaudited. |
| 300014 | 2026H1 | 2026H1 forecast: the company says revenue is expected to rise about 60% YoY, while it identifies higher supply-chain costs as a pressure it is mitigating. The forecast is unaudited. |
| 002497 | 2026H1 | 2026H1 forecast: lithium-salt prices, volume and ASP rose; the company also cites production-efficiency/cost-control actions. The forecast is unaudited. |
| 002432 | 2026H1 | 2026H1 forecast: the stated driver is appreciation in underlying technology-investment valuations. The issuer explicitly warns of uncertain investment return, low liquidity and potentially prolonged/failed exits. |
| 000623 | 2026H1 | 2026H1 forecast: the company cites higher investment income as the main driver. The forecast is unaudited. |
| 600739 | FY2025 | FY2025 disclosure attributes NP growth to higher associate-company investment income; it attributes OCF decline to trade settlement timing and lower biopharma collection, and says historical revenue was adjusted from gross to net presentation for part of trading activity. |
| 000685 | 2026H1 | 2026H1 forecast: the company cites operating efficiency and higher investment income, while noting a complex policy/competitive environment. The forecast is unaudited. |
| 600150 | FY2025 | FY2025 disclosure cites more/high-priced vessel deliveries and build efficiency; it separately states OCF declined as production/in-progress inputs increased. Comparative periods were restated for the China State Shipbuilding/China Shipbuilding Industry same-control merger. |
| 301308 | 2026H1 | 2026H1 reported attributable NP is positive while reported operating cash flow is negative; this packet records the reported figures only and makes no cash-conversion conclusion. |
| 002812 | 2026H1 | 2026H1 forecast: the issuer cites battery-separator demand, higher sales volume, cost control and a price recovery; figures are unaudited preliminary data. |
| 002240 | 2026H1 | 2026H1 forecast: the issuer cites higher lithium-salt prices and release of Indonesia capacity; figures are unaudited preliminary data. |
| 300390 | 2026H1 | 2026H1 forecast: lithium-material volume/price improved with energy-storage and power-battery demand; comparative data are restated for a same-control acquisition, and figures are unaudited. |

## Source archive

- Search-response captures and selected PDFs: `sources/official-20260811/`.
- Exact values, source URLs, source pages, archive paths, quality, native units, conversions, and gaps: `data/raw_financials_20260811.json`.
- No media source was used as a filing substitute.
