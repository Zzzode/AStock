# New-Names Holdings / Fund-Flow Proxy Evidence (14 Expanded Coverage)

**Run date:** 2026-06-20

**Purpose:** Fetch real holdings / fund-flow proxy data for the 14 expanded-coverage names added in ch09 图表9-36/9-37, using the same public akshare / eastmoney proxies the core 12 names already rely on (`eastmoney_fund_flow_evidence`, `eastmoney_hsgt_individual_em`, `stock_fund_stock_holder`, `RPTA_WEB_RZRQ_GGMX`, `stock_lhb_detail_em`). Each cell is labelled **obtained** or **gated (reason)** — nothing fabricated.

**Boundary (same as core 12 names):** These are public proxies only. They do **not** equal terminal-grade order flow, beneficial-owner northbound positioning, or complete active/passive institutional positioning. The northbound individual series is frozen at 2024-08-16 (same frozen page-shell the core 12 names hit — see `eastmoney_hsgt_public_api_probe_20260618.md`); it is a historical baseline, not a current-quarter holding. Fund-holder counts come from the public single-stock fund-holder endpoint (holder rows, not CNInfo heavy-holding rank) and the latest disclosure date differs by name (2026-03-31 for most; 2025-12-31 for 300576 / 002636 whose Q1 disclosures were not yet in the public feed). Margin coverage uses the same `RPTA_WEB_RZRQ_GGMX` report as the core names; names not in the marginable universe return empty.

**01888.HK 建滔积层板:** HK-listed, not an A-share code. All five A-share proxies (eastmoney fund-flow / northbound / fund-holder / margin / LHB) are A-share-only endpoints and do not cover HK tickers — recorded as **gated (HK-listed, A-share endpoints n/a)**, consistent with the core report's HK-name handling.

## Per-code proxy matrix

| 代码 | 名称 | Fund-flow (30d) | Northbound (individual) | Fund holdings (public holder rows) | Margin (融资融券) | Dragon-Tiger (近90d) |
|---|---|---|---|---|---|---|
| 002384 | 东山精密 | **obtained** — 30行，30日主力净流-100.88亿，最新(06-18)主力-0.47亿 | **gated** — 历史行冻结于2024-08-16（页面壳冻结，同核心12标的） | **obtained** — 996行，最新2026-03-31，合计持股市值1016.54亿 | **obtained** — 06-17融资余额141.39亿，余额占比3.97\% | **obtained** — 7次上榜 |
| 601138 | 工业富联 | **obtained** — 30行，30日主力净流-43.55亿，最新(06-18)主力+45.68亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 995行，最新2026-03-31，合计持股市值697.91亿 | **obtained** — 06-18融资余额105.07亿，占比0.68\% | **gated** — 近90d 0次上榜（非异常交易日） |
| 603256 | 宏和科技 | **obtained** — 30行，30日主力净流+1.62亿，最新(06-18)主力-2.62亿 | **gated** — 历史行冻结于2024-08-16（仅156行历史） | **obtained** — 865行，最新2026-03-31，合计持股市值40.76亿 | **gated** — `RPTA_WEB_RZRQ_GGMX`返回空数据（非两融标的） | **obtained** — 5次上榜 |
| 601208 | 东材科技 | **obtained** — 30行，30日主力净流-22.53亿，最新(06-18)主力-2.11亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 992行，最新2026-03-31，合计持股市值84.43亿 | **obtained** — 06-18融资余额31.88亿，占比4.22\% | **obtained** — 1次上榜 |
| 688630 | 芯碁微装 | **obtained** — 30行，30日主力净流-0.16亿，最新(06-18)主力+0.20亿 | **gated** — 历史行冻结于2024-08-16（仅290行历史） | **obtained** — 992行，最新2026-03-31，合计持股市值88.88亿 | **obtained** — 06-18融资余额10.94亿，占比1.65\% | **obtained** — 2次上榜 |
| 603228 | 景旺电子 | **obtained** — 30行，30日主力净流-13.22亿，最新(06-18)主力-0.74亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 998行，最新2026-03-31，合计持股市值179.12亿 | **obtained** — 06-18融资余额26.25亿，占比3.32\% | **gated** — 近90d 0次上榜 |
| 300308 | 中际旭创 | **obtained** — 30行，30日主力净流-50.84亿，最新(06-18)主力+24.12亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 994行，最新2026-03-31，合计持股市值1832.77亿 | **obtained** — 06-17融资余额430.27亿，占比3.04\% | **gated** — 近90d 0次上榜 |
| 002080 | 中材科技 | **obtained** — 30行，30日主力净流-10.85亿，最新(06-18)主力-4.48亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 998行，最新2026-03-31，合计持股市值121.98亿 | **obtained** — 06-17融资余额20.96亿，占比1.52\% | **obtained** — 5次上榜 |
| 301217 | 铜冠铜箔 | **obtained** — 30行，30日主力净流-11.38亿，最新(06-18)主力+3.29亿 | **gated** — 历史行冻结于2024-08-16（仅348行历史） | **obtained** — 990行，最新2026-03-31，合计持股市值21.77亿 | **obtained** — 06-17融资余额13.98亿，占比0.93\% | **obtained** — 6次上榜 |
| 300576 | 容大感光 | **obtained** — 30行，30日主力净流-3.10亿，最新(06-18)主力-0.94亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 249行，最新2025-12-31，合计持股市值5.47亿 | **obtained** — 06-17融资余额6.31亿，占比4.87\% | **obtained** — 1次上榜 |
| 002636 | 金安国纪 | **obtained** — 30行，30日主力净流-9.05亿，最新(06-18)主力-0.48亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 976行，最新2025-12-31，合计持股市值14.30亿 | **obtained** — 06-17融资余额18.77亿，占比2.71\% | **obtained** — 9次上榜 |
| 600176 | 中国巨石 | **obtained** — 30行，30日主力净流-19.14亿，最新(06-18)主力-12.05亿 | **gated** — 历史行冻结于2024-08-16 | **obtained** — 998行，最新2026-03-31，合计持股市值123.76亿 | **obtained** — 06-18融资余额34.77亿，占比1.62\% | **obtained** — 1次上榜 |
| 603002 | 宏昌电子 | **obtained** — 30行，30日主力净流-2.20亿，最新(06-18)主力-3.31亿 | **gated** — 历史行冻结于2024-08-16（仅156行历史） | **obtained** — 473行，最新2026-03-31，合计持股市值24.20亿 | **gated** — `RPTA_WEB_RZRQ_GGMX`返回空数据（非两融标的） | **obtained** — 3次上榜 |
| 01888.HK | 建滔积层板 | **gated (港股，A-share端点不适用)** | **gated (港股)** | **gated (港股)** | **gated (港股)** | **gated (港股)** |

## Coverage tally (13 A-share codes; HK excluded)

- **Fund-flow (30d):** 13/13 obtained (eastmoney `fflow/daykline`, `lmt=30`).
- **Northbound (individual):** 0/13 current — all gated at 2024-08-16 frozen page-shell (identical boundary to core 12 names; the `RPT_MUTUAL_STOCK_NORTHSTA` / current holding-rank APIs remain server-busy/empty per `eastmoney_hsgt_public_api_probe_20260618.md`). Historical baseline rows obtained for all 13 but are stale.
- **Fund holdings (public holder rows):** 13/13 obtained. Latest disclosure 2026-03-31 for 11 names; 2025-12-31 for 300576 / 002636 (Q1 not yet in public feed at run time).
- **Margin (融资融券):** 11/13 obtained. 603256 宏和科技 + 603002 宏昌电子 return empty — not in the marginable underlying universe (gated: not an RZRQ underlying).
- **Dragon-Tiger (近90d, 2026-03-22 to 2026-06-20):** 13/13 queried. 9 names on-list (002384 7, 603256 5, 601208 1, 688630 2, 002080 5, 301217 6, 300576 1, 002636 9, 600176 1, 603002 3); 4 names 0 on-list days in window (601138, 603228, 300308 — large caps / demand indicators; reasonable).

## Interpretation

- The 13 A-share new names now carry the same five proxy dimensions as the core 12, with one structural difference: **northbound individual is uniformly frozen at 2024-08-16** (no current-quarter northbound holding proxy for any of the 13, same as the core names' frozen page-shell boundary).
- **Fund holdings (public holder rows) is the strongest new dimension** — 13/13 obtained, and the magnitudes are large for the demand indicators (中际旭创 1832.77亿, 东山精密 1016.54亿, 工业富联 697.91亿), confirming these are heavily-held names but do not by themselves distinguish active vs passive or indicate crowding direction without the CNInfo heavy-holding rank the core 5 names have.
- **Margin crowding is highest among small/mid material names** by balance-to-float ratio: 容大感光 4.87\%, 东材科技 4.22\%, 东山精密 3.97\%, 景旺电子 3.32\%, 中际旭创 3.04\% — directionally consistent with the report's "theme crowding + leverage" thesis, but these are single-date balances, not the 300-row long-window bridge the core names have.
- **30-day fund-flow is uniformly net-outflow** for 12/13 names (only 宏和科技 +1.62亿 modestly positive), suggesting the late-cycle distribution / chip-loosening pattern the report already documents for the core names extends across the expanded universe; the demand indicators (工业富联 +45.68亿, 中际旭创 +24.12亿 on the latest day) show the largest single-day inflow reversals.
- **Dragon-Tiger** confirms retail/active-trading intensity is concentrated in the small-cap material names (金安国纪 9次, 东山精密 7次, 铜冠铜箔 6次, 宏和科技 5次, 中材科技 5次), while large-cap demand indicators did not appear on the LHB in the window.

## Source / method

- Fund-flow: `curl https://push2his.eastmoney.com/api/qt/stock/fflow/daykline/get?secid={m}.{code}&lmt=30&...` with browser UA (same method as `eastmoney_fund_flow_evidence.md`); raw JSON in `raw_eastmoney_fund_flow_newnames/`.
- Northbound: `ak.stock_hsgt_individual_em(symbol=code)`; raw JSON in `raw_eastmoney_hsgt_newnames/`.
- Fund holdings: `ak.stock_fund_stock_holder(symbol=code)` (single-stock public fund holder rows); raw JSON in `raw_eastmoney_fund_holder_newnames/`.
- Margin: `RPTA_WEB_RZRQ_GGMX` via eastmoney datacenter-web (same report as `raw_eastmoney_margin/`); raw JSON in `raw_eastmoney_margin_newnames/`.
- Dragon-Tiger: `ak.stock_lhb_detail_em(start_date="20260322", end_date="20260620")` filtered by code; raw JSON in `raw_eastmoney_lhb_newnames/`.

All raw JSON archived under `data/raw_eastmoney_*_newnames/`. Aggregated machine-readable summary in `data/new_names_holdings_proxy_20260620.json`.
