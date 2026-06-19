<!-- Recommended report placement: ch04 midstream_PCB node (光模块+光芯片 stacked vertical) + ch06 company card as a core AI-hardware candidate + ch08 valuation board (cross-check only, no AStock TP). -->

# Dongshan Precision (东山精密 002384) — Evidence Card

**Coverage role:** Candidate-name expansion beyond the 5 core tickers (002463 / 300476 / 002916 / 600183 / 603186). 002384 is **not** in the report's current core basket; this card is a scouting brief, not an AStock-rated position.

**Snapshot date:** 2026-06-18 (CLI quote/financials pulled this date).

---

## 1. Business positioning

| Dimension | Reading | Evidence tier |
|---|---|---|
| Industry rank | PCB 百强第 2 (industry league table) | Public / industry list |
| Primary segment | PCB (Multek overseas + domestic high-layer-count) | Company disclosures |
| Second engine | 光模块 + 光芯片 — via full acquisition of **索尔思光电 (Source Photonics)**, consolidated Oct 2025 | Public, M&A closed |
| Strategic framing | "AI-server PCB → 光芯片 → 高速光模块" vertical stack | Sell-side narrative |
| Flagged customer ties | 英特尔 AI-server PCB core supplier; edge-AI PCB #1 globally; Google ASIC link cited in market commentary | Public claim — customer name **not** confirmed in 002384's own filings (see §6) |

---

## 2. AI-PCB-chain exposure

- **Which segment:** PCB business is the cash cow — sell-side puts 2025 PCB revenue share at **~63.85%**, segment gross margin **~17.59%** (brocker PDF, dfcfw H3_AP202603301820859917). This is *lower* than 沪电/深南/胜宏's high-end PCB margins — 002384's PCB mix still carries legacy Multek consumer/communication load.
- **Layer-count upgrade:** AI-server PCB moving 12–16层 → **18–20+层**; 002384 positioned as beneficiary of layer-count and material upgrade cycle.
- **光模块/光芯片 stack:** 800G + 1.6T product line via 索尔思; 2026-06-16 announcement that subsidiary 索尔思 will invest **USD 1.2 bn** (~RMB 8.1 bn) in 光芯片/光模块 capacity expansion (news corpus, this card §CLI).
- **AI-server BOM 9–14% claim:** This is the *report-wide* PCB-value-chain anchor used in ch04; 002384 participates on the PCB leg (BOM share applies) **plus** a separate 光模块 leg (different BOM line, not additive to the 9–14% figure). Do **not** double-count when sizing 002384's AI-server exposure.
- **Google ASIC link:** Surfaced only in third-party commentary; not verified in 002384 annual report customer list. Treat as **needs-IR** until confirmed.

---

## 3. Financial snapshot (CLI: `astock.cli financials 002384`)

**Latest period: 20260331 (2026 Q1)** — official filing via CLI, **public / verified**.

| Metric | 2026Q1 | YoY |
|---|---:|---:|
| 营业收入 (total_revenue) | 13,137,636,263 (¥131.4 亿) | **+52.72%** |
| 营业成本 (operating_cost) | 11,800,615,115 (¥118.0 亿) | — |
| 归母净利润 (net_profit_parent) | 1,109,892,942 (¥11.10 亿) | **+143.47%** |
| 净利润 (net_profit) | 1,124,152,991 (¥11.24 亿) | +146.24% |
| 扣非净利润 (net_profit_deducted) | 1,059,278,408 (¥10.59 亿) | **+166.99%** |
| 经营性现金流 (operating_cash_flow) | 1,126,672,373 (¥11.27 亿) | −17.48% |
| EPS (basic) | ¥0.61 | — |
| BPS | ¥12.36 | — |
| 归母权益 (equity) | 22,892,650,196 (¥228.9 亿) | +18.02% |
| 商誉 (goodwill) | 4,769,259,362 (¥47.69 亿) | — |

**Annualized / TTM context (mixed sources — see §6 boundary):**
- 2025 full-year revenue **broke ¥40 bn** for the first time (证券时报 / search-corpus, **secondary, not CLI-verified**).
- Implied share count: 11.10 亿 / 0.61 ≈ **18.2 亿 shares**.
- Q1 毛利率 ≈ (13.14−11.80)/13.14 ≈ **10.2%** — *blended* (PCB + Multek + new 光模块 consolidation drags); notably **below** the sell-side's 17.59% PCB-only segment margin, confirming mix dilution.

---

## 4. Valuation signal (CLI: `astock.cli quote 002384`)

**Quote 2026-06-18:**
- Latest price **¥273.00**, Change **+6.26%** (+¥16.08), High 277.60 / Low 255.15, Turnover ¥213.11 亿.
- **Data quality: full_realtime.**

**PE triangulation (rough — needs IR/Wind for precise TTM):**
- Naïve annualized 2026E EPS at Q1 run-rate = 0.61 × 4 = **¥2.44** → forward PE ≈ 273 / 2.44 ≈ **~112×**.
- If 2025 full-year EPS ~¥1.2 (search-corpus net ~¥22 亿 / 18.2 亿 shares, **not CLI-verified**) → TTM PE ≈ 273 / 1.2 ≈ **~227×**.
- **Read:** 002384 trades at a steep AI-PCB + 光模块 premium, well above the report's 5 core tickers (002463 / 002916 / 600183 latest PE 56–93× per `external_source_evidence.md`). The premium prices in (a) 索尔思 consolidation optionality and (b) 1.6T 光模块 capacity narrative. **High expectations risk** — any quarter of PCB margin slippage or 光模块 ramp delay is heavily punished.

---

## 5. Catalyst / flow signal (CLI: `astock.cli news 002384 --days 60`)

- 2026-06-16/17 cluster: **USD 1.2 bn 光芯片/光模块 capex** (子公司 索尔思) — single largest catalyst in window.
- 2026-06-15: **¥4.4 亿 主力资金 net inflow** in one session; 2026-06-16 northbound large net-buy list.
- 2026-06-04 龙虎榜 (LHB) appearance; 2026-06-02 午后涨停 (limit-up).
- 2026-06-17: 硅光 CW 激光芯片 R&D capability disclosed; external silicon-photonics partnerships + self-developed silicon-photonics module line.
- 2026-04-22: 分红 event (corpus head only — amount not parsed here).

**Read:** News flow is **光芯片/光模块-led, not PCB-led** — the rerating narrative has migrated from "high-layer PCB beneficiary" to "vertical 光模块 play." This is exactly the ch04 midstream-stacking thesis, but execution risk sits entirely on 索尔思 integration.

---

## 6. Evidence boundary (public vs needs-IR)

| Claim | Status | Action before any report inclusion |
|---|---|---|
| 2026Q1 financials | ✅ Public (CLI filing) | Usable as-is |
| Quote / flow / LHB | ✅ Public (CLI/exchange) | Usable |
| 索尔思 consolidation Oct 2025 | ✅ Public (M&A closed) | Usable |
| USD 1.2 bn capex (2026-06-16) | ✅ Public (announcement) | Usable, cite announcement |
| PCB rev share 63.85% / GM 17.59% | ⚠️ Sell-side PDF only | Re-check 002384 2025 annual report segment footnote |
| 2025 revenue >¥40 bn | ⚠️ Media, not CLI-verified | Pull 2025 annual via CLI / cninfo before quoting |
| **Google ASIC** customer tie | ❌ Third-party commentary only | **Needs IR** — must come from 002384 major-customer disclosure or Google supplier confirmation; **do not** print in report until verified |
| 英特尔 AI-server PCB supplier | ⚠️ Public claim, customer name not in filings | Flag as "market-recognized," not "filing-confirmed" |
| TTM EPS / precise PE | ❌ Derived, not CLI-sourced | Needs Wind/Choice or annual report before any target-price work |
| 光模块 BOM additivity to PCB 9–14% | ❌ Conceptual | Do not stack; treat as separate BOM line in ch04 |

---

## 7. Recommended placement (mapping to report structure)

- **ch04 (midstream PCB node):** Add 002384 as the **光模块/光芯片 vertical-stacking exhibit** alongside the PCB layer-count upgrade discussion. Use it to illustrate "PCB-only → PCB + 光模块一体化" — but explicitly separate the 光模块 BOM from the PCB BOM 9–14% anchor to avoid double-counting.
- **ch06 (company card):** Insert as a **core candidate** in the AI-hardware basket expansion (B-track 名单扩充), positioned as "PCB 百强 #2 + 光模块/光芯片 vertical," with the caveat that its blended GM (~10% Q1) is structurally below the high-end-PCB pure-plays.
- **ch08 (valuation board):** Cross-check entry only — show the ~110–230× PE band with explicit "high-expectations" tag; **no AStock target price** until 2025 annual + customer disclosure + 光模块 ramp KPIs are filed. Use the report's existing 5-ticker PE percentile table as the reference frame.

---

*Sources: WebSearch corpus (东方财富 PDF dfcfw H3_AP202603301820859917; 证券时报; 21财经; 国盛证券; 慧博); AStock CLI (`financials 002384` 20260331; `news 002384 --days 60`; `quote 002384` 2026-06-18). Customer-specific and TTM-EPS claims deferred to IR — see §6.*
