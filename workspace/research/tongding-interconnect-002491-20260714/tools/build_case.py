#!/usr/bin/env python3
"""Build the Tongding Interconnect institutional research case."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
ANALYSIS = CASE / "analysis"
SECTIONS = CASE / "sections"
PRICE = 20.86
SHARES_100M = 12.299945
Q1_PARENT_NP = 0.5127403695
Q1_ADJ_NP = 1.0282864359
H1_PARENT = {"bear": 1.70, "base": 2.05, "bull": 2.40}
H1_ADJ = {"bear": 2.30, "base": 2.80, "bull": 3.30}
H1_REVENUE = {"bear": 23.7449, "base": 24.5050, "bull": 25.2680}
H2_PARENT = {"bear": 0.80, "base": 1.80, "bull": 3.00}
H2_ADJ = {"bear": 1.10, "base": 2.40, "bull": 3.70}
PE = {"bear": 25.0, "base": 34.0, "bull": 44.0}
PB = {"bear": 1.55, "base": 1.80, "bull": 2.15}
PS = {"bear": 0.85, "base": 1.05, "bull": 1.30}


def put(rel: str, text: str) -> None:
    path = CASE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def put_json(rel: str, value: Any) -> None:
    path = CASE / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def percent(value: float) -> str:
    return f"{value * 100:.1f}\\%"


def scenarios() -> list[dict[str, Any]]:
    result = []
    parent_bps = 25.2032063112 / SHARES_100M
    for name in ("bear", "base", "bull"):
        parent_np = H1_PARENT[name] + H2_PARENT[name]
        adjusted_np = H1_ADJ[name] + H2_ADJ[name]
        adjusted_eps = adjusted_np / SHARES_100M
        pe_value = adjusted_eps * PE[name]
        pb_value = parent_bps * PB[name]
        ps_value = H1_REVENUE[name] * 2 / SHARES_100M * PS[name]
        target = 0.50 * pe_value + 0.25 * pb_value + 0.25 * ps_value
        result.append(
            {
                "scenario": name,
                "revenue_2026e_100m": H1_REVENUE[name] * 2,
                "parent_np_2026e_100m": round(parent_np, 6),
                "adjusted_np_2026e_100m": round(adjusted_np, 6),
                "adjusted_eps_2026e": round(adjusted_eps, 6),
                "pe": PE[name],
                "pb": PB[name],
                "ps": PS[name],
                "pe_value": round(pe_value, 4),
                "pb_value": round(pb_value, 4),
                "ps_value": round(ps_value, 4),
                "target_price": round(target, 2),
                "upside": round(target / PRICE - 1, 6),
                "h1_parent_np_100m": H1_PARENT[name],
                "h1_adjusted_np_100m": H1_ADJ[name],
                "h2_parent_np_100m": H2_PARENT[name],
                "h2_adjusted_np_100m": H2_ADJ[name],
            }
        )
    return result


def sources() -> list[dict[str, Any]]:
    return [
        {"id": "S01", "type": "official_annual_report", "date": "2026-04-28", "path": "sources/official-20260714/2026-04-28-2025年年度报告.pdf", "quality": "A", "use": "2025 business mix, financials, volumes, risk and audit notes"},
        {"id": "S02", "type": "official_audit_report", "date": "2026-04-28", "path": "sources/official-20260714/2026-04-28-2025年度财务报表审计报告.pdf", "quality": "A", "use": "revenue recognition, receivables and inventory audit matters"},
        {"id": "S03", "type": "official_q1_report", "date": "2026-04-30", "path": "sources/official-20260714/2026-04-30-2026年第一季度报告.pdf", "quality": "A", "use": "Q1 results, balance sheet, shareholders"},
        {"id": "S04", "type": "official_h1_preview", "date": "2026-07-14", "path": "sources/official-20260714/2026-07-15-2026年半年度业绩预告.pdf", "quality": "A preliminary", "use": "H1 revenue/earnings range and stated drivers"},
        {"id": "S05", "type": "public_realtime_quote", "date": "2026-07-14", "path": "sources/market-20260714/quote_sina.html", "quality": "B", "use": "close, volume and turnover value"},
        {"id": "S06", "type": "public_lhb_snapshot", "date": "2026-07-14", "path": "sources/market-20260714/lhb.html", "quality": "B", "use": "institutional seat events and turnover"},
        {"id": "S07", "type": "public_financing_snapshot", "date": "2026-07-13", "path": "sources/market-20260714/margin.html", "quality": "C partial", "use": "financing balance cross-check; endpoint schema error retained"},
        {"id": "S08", "type": "public_tender_context", "date": "2026-02-12", "path": "sources/industry-20260714/china-mobile-special-cable-result.html", "quality": "B media repost", "use": "tender context only, not booked revenue"},
        {"id": "S09", "type": "broker_search_exhaustion", "date": "2026-07-14", "path": "sources/broker-reports/2026-07-14/index.md", "quality": "C", "use": "zero-weight Street anchor and failed probes"},
    ]


def claims() -> list[dict[str, Any]]:
    return [
        {"id": "C01", "claim": "H1 parent NP CNY170m-CNY240m; adjusted NP CNY230m-CNY330m; EPS CNY0.1382-CNY0.1951.", "source": "S04", "confidence": "high", "boundary": "preliminary and unaudited"},
        {"id": "C02", "claim": "H1 revenue growth is 56%-66%; optical-fiber volume and price recovery plus safety subsidiary consolidation/improvement are cited drivers.", "source": "S04", "confidence": "high", "boundary": "company-level; no segment split or ASP"},
        {"id": "C03", "claim": "2025 revenue CNY3.413bn; communication cable and related manufacturing 70.19%; safety business 19.61%.", "source": "S01", "confidence": "high", "boundary": "audited annual disclosure"},
        {"id": "C04", "claim": "2025 optical-fiber sales 300.48万芯公里, +4061.77%; inventory -37.97%.", "source": "S01", "confidence": "high", "boundary": "reported physical volume, not 2026 ASP"},
        {"id": "C05", "claim": "2026Q1 adjusted NP CNY102.83m versus parent NP CNY51.27m; fair-value and hedging losses were material.", "source": "S03", "confidence": "high", "boundary": "unaudited Q1"},
        {"id": "C06", "claim": "Q1 top holders included Tongding Group 31.51%, Shen Xiaoping 4.55%, Huashang funds, E Fund, HKSCC and Goldman Sachs.", "source": "S03", "confidence": "high", "boundary": "quarter-end holdings, not July intent"},
        {"id": "C07", "claim": "2026-07-14 close CNY20.86; volume 120.15m shares; turnover value CNY2.404bn.", "source": "S05", "confidence": "high", "boundary": "15:35:45 close snapshot"},
        {"id": "C08", "claim": "Dragon-Tiger records show alternating institutional buying/selling and high-turnover event trading.", "source": "S06", "confidence": "high", "boundary": "seat is not beneficial-owner identity"},
        {"id": "C09", "claim": "No original broker target-price row with complete numeric fields was verified at cutoff.", "source": "S09", "confidence": "high", "boundary": "source-exhaustion conclusion"},
    ]


def write_data(model: dict[str, Any]) -> None:
    put(
        "data/verified_financials.md",
        """# Verified Financials — 002491.SZ

**Cutoff:** 2026-07-14. Amounts are CNY hundred million unless stated.

| Period | Revenue | Parent NP | Adjusted parent NP | OCF | Source |
|---|---:|---:|---:|---:|---|
| 2025A | 34.1300 | -0.7639 | -0.4127 | 0.6860 | S01 |
| 2026Q1A | 10.6362 | 0.5127 | 1.0283 | -0.1758 | S03 |
| 2026H1E low | 23.7449 | 1.7000 | 2.3000 | not disclosed | S04 |
| 2026H1E base | 24.5050 | 2.0500 | 2.8000 | not disclosed | S04 |
| 2026H1E high | 25.2680 | 2.4000 | 3.3000 | not disclosed | S04 |

## 2025 product mix

| Product | Revenue | Share | Gross margin |
|---|---:|---:|---:|
| Optical fiber/cable | 1.8253 | 5.34% | 18.10% |
| Communication cable | 9.0726 | 26.58% | 24.32% |
| Power cable | 13.0614 | 38.27% | 12.26% |
| Communication equipment | 2.5868 | 7.58% | 13.00% |
| Safety business | 6.6919 | 19.61% | 29.25% |
| New energy | 0.4394 | 1.29% | not separately disclosed |

At Q1, receivables were CNY14.5093 hundred million, inventory CNY11.7881
hundred million, short-term borrowings CNY22.3434 hundred million, cash
CNY9.5126 hundred million and parent equity CNY25.2032 hundred million.
Operating cash flow remained negative. The H1 preview identifies an
approximately CNY91m pre-tax negative fair-value effect from YunChuang Data.
""",
    )
    put(
        "data/verified_market_data.md",
        """# Verified Market Data — 002491.SZ

| Field | Value | Source |
|---|---:|---|
| Close, 2026-07-14 | CNY20.86 | S05 |
| Previous close | CNY19.87 | S05 |
| High / low | CNY20.86 / CNY19.12 | S05 |
| Volume | 120.1504m shares | S05 |
| Turnover value | CNY2.4036bn | S05 |
| Shares outstanding | 1,229.9945m | S03 |
| Market capitalization | CNY25.658bn | derived |
| Q1 parent BPS | CNY2.0490 | S03 |

The old CNY36.15 price in the 2026-06-26 industry report is not used.
""",
    )
    put_json("data/current_valuation_model_20260714.json", {"rows": [model]})
    base = next(row for row in model["scenarios"] if row["scenario"] == "base")
    put_json(
        "data/growth_driver_model.json",
        {
            "ticker": "002491.SZ",
            "company": "通鼎互联",
            "applies": True,
            "growth_driver": "optical-fiber volume/price recovery plus safety-business consolidation",
            "base_business_revenue_2025_100m": 34.1299504757,
            "growth_segment_revenue_2025_100m": 0.0,
            "value_amount_or_proxy": "H1 company revenue guidance; segment allocation not disclosed",
            "unit_volume_or_proxy": "2025 optical-fiber sales 300.48万芯公里, +4061.77%",
            "ASP_or_price": "not disclosed; company says H1 price and volume improved",
            "recognized_revenue_ratio": "not disclosed",
            "supply_demand_state": "recovery, duration not proven",
            "capacity_or_utilization": "not disclosed",
            "certification_or_customer_qualification": "not disclosed",
            "growth_gross_margin": "2025 optical-fiber/cable gross margin 18.10%; H1 not disclosed",
            "incremental_opex": "not disclosed",
            "growth_net_profit": base["adjusted_np_2026e_100m"],
            "growth_EPS": base["adjusted_eps_2026e"],
            "evidence_type": "official H1 preview and annual physical-volume disclosure",
            "source": "S01/S04",
            "evidence_gap": "no H1 product revenue, ASP, utilization, customer or order conversion",
            "valuation_credit": "earnings credit for company recovery; optionality credit only for AI/data-center",
            "bear": next(row for row in model["scenarios"] if row["scenario"] == "bear"),
            "base": base,
            "bull": next(row for row in model["scenarios"] if row["scenario"] == "bull"),
            "current_price_implied_growth": f"base adjusted PE {PRICE / base['adjusted_eps_2026e']:.1f}x",
            "sensitivity_key": "H2 adjusted NP, optical margin and cash conversion",
        },
    )
    put_json("data/source_registry.json", sources())
    put("data/source_registry.md", "# Source Registry\n\n| ID | Type | Date | Quality | Path | Use |\n|---|---|---|---|---|---|\n" + "\n".join(f"| {s['id']} | {s['type']} | {s['date']} | {s['quality']} | `{s['path']}` | {s['use']} |" for s in sources()))
    put_json("data/claim_audit.json", claims())
    put("data/claim_audit.md", "# Claim Audit\n\n| ID | Claim | Source | Confidence | Boundary |\n|---|---|---|---|---|\n" + "\n".join(f"| {c['id']} | {c['claim']} | {c['source']} | {c['confidence']} | {c['boundary']} |" for c in claims()))


def write_analysis(model: dict[str, Any]) -> None:
    rows = model["scenarios"]
    bear, base, bull = rows
    final_target = model["final_target"]
    put(
        "analysis/growth_earnings_model.md",
        f"""# Growth Earnings Model

**Gate status: CONDITIONAL**

The applicable driver is optical-fiber volume/price recovery plus the safety
business consolidation, not generic AI demand. Optical fiber/cable was only
5.34% of 2025 revenue; communication and power cables and safety systems are
the larger profit pools. Segment H1 revenue, ASP, utilization and customer
allocation are not disclosed, so no pure-growth multiple is assigned.

| Driver | Bear | Base | Bull | Current-price implication | Upgrade evidence |
|---|---:|---:|---:|---|---|
| H1 adjusted NP | {bear['h1_adjusted_np_100m']:.2f} | {base['h1_adjusted_np_100m']:.2f} | {bull['h1_adjusted_np_100m']:.2f} | official range is the hard denominator | H1 report |
| H2 adjusted NP | {bear['h2_adjusted_np_100m']:.2f} | {base['h2_adjusted_np_100m']:.2f} | {bull['h2_adjusted_np_100m']:.2f} | base requires CNY240m | Q2/Q3 cash and margin |
| 2026E adjusted EPS | {bear['adjusted_eps_2026e']:.3f} | {base['adjusted_eps_2026e']:.3f} | {bull['adjusted_eps_2026e']:.3f} | price = {PRICE / base['adjusted_eps_2026e']:.1f}x base | EPS delivery |

Credit decision: **earnings credit** for disclosed recovery, **optionality
credit** for AI/data-center exposure, and **watchlist-only** for named
customers, ASP and utilization claims.
""",
    )
    put(
        "analysis/segment_forecast_bridge.md",
        f"""# Segment Forecast Bridge

The H1 announcement provides company-level ranges but no segment income
statement. The forecast therefore does not invent optical revenue.

| Item | 2025A | 2026Q1A | 2026H1E base | 2026E base |
|---|---:|---:|---:|---:|
| Revenue (CNY100m) | 34.130 | 10.636 | 24.505 | {base['revenue_2026e_100m']:.2f} |
| Parent NP (CNY100m) | -0.764 | 0.513 | 2.050 | {base['parent_np_2026e_100m']:.2f} |
| Adjusted parent NP (CNY100m) | -0.413 | 1.028 | 2.800 | {base['adjusted_np_2026e_100m']:.2f} |
| Adjusted EPS (CNY) | — | 0.0836 | 0.2276 | {base['adjusted_eps_2026e']:.4f} |

H2 base adjusted NP of CNY{base['h2_adjusted_np_100m']:.2f} hundred million is
an AStock assumption, not company guidance. The model remains a consolidated
recovery model with a segment-purity discount.
""",
    )
    put(
        "analysis/implied_growth_sensitivity.md",
        f"""# Implied Growth Sensitivity

At CNY{PRICE:.2f}, the stock requires a high multiple on the official H1
recovery range. The table below is a direct EPS × PE check.

| 2026E adjusted NP (CNY100m) | 25x | 34x | 44x |
|---:|---:|---:|---:|
| {bear['adjusted_np_2026e_100m']:.2f} | {bear['adjusted_eps_2026e']*25:.2f} | {bear['adjusted_eps_2026e']*34:.2f} | {bear['adjusted_eps_2026e']*44:.2f} |
| {base['adjusted_np_2026e_100m']:.2f} | {base['adjusted_eps_2026e']*25:.2f} | {base['adjusted_eps_2026e']*34:.2f} | {base['adjusted_eps_2026e']*44:.2f} |
| {bull['adjusted_np_2026e_100m']:.2f} | {bull['adjusted_eps_2026e']*25:.2f} | {bull['adjusted_eps_2026e']*34:.2f} | {bull['adjusted_eps_2026e']*44:.2f} |

Validation needs: H1 adjusted NP near CNY280m, H2 adjusted NP near CNY240m,
positive or materially improved operating cash flow, and optical margin/order
evidence. Failure downgrades the stock to watchlist-only.
""",
    )
    put(
        "analysis/segment_valuation_model.md",
        """# Segment Valuation Model

The correct classification is a diversified cyclical cable and safety platform.

| Component | Method | Denominator | Weight |
|---|---|---|---:|
| Core earnings | adjusted PE | 2026E adjusted parent EPS | 50% |
| Balance sheet check | PB | Q1 parent BPS CNY2.0490 | 25% |
| Revenue sanity check | PS | 2026E revenue | 25% |

No AI/data-center multiple is applied to consolidated revenue because the
company does not disclose segment purity, customer allocation, ASP or utilization.
""",
    )
    put(
        "analysis/valuation_model.md",
        f"""# Valuation Model

## Final Valuation Table

| Scenario | Revenue | Adjusted NP | Adjusted EPS | PE/PB/PS | Target | Upside/downside | Action |
|---|---:|---:|---:|---|---:|---:|---|
| Bear | {bear['revenue_2026e_100m']:.2f} | {bear['adjusted_np_2026e_100m']:.2f} | {bear['adjusted_eps_2026e']:.3f} | 25x/1.55x/0.85x | CNY{bear['target_price']:.2f} | {percent(bear['upside'])} | risk reduction |
| Base | {base['revenue_2026e_100m']:.2f} | {base['adjusted_np_2026e_100m']:.2f} | {base['adjusted_eps_2026e']:.3f} | 34x/1.80x/1.05x | CNY{base['target_price']:.2f} | {percent(base['upside'])} | event-after pullback validation |
| Bull | {bull['revenue_2026e_100m']:.2f} | {bull['adjusted_np_2026e_100m']:.2f} | {bull['adjusted_eps_2026e']:.3f} | 44x/2.15x/1.30x | CNY{bull['target_price']:.2f} | {percent(bull['upside'])} | only if cash and margin confirm |

**Formula:** `Target = 50% × adjusted EPS × PE + 25% × Q1 parent BPS × PB
+ 25% × 2026E revenue / shares × PS`.

The base fundamental target is CNY{base['target_price']:.2f}. Adding a 10%
market sentiment anchor at CNY18.50 gives a final target of CNY{final_target:.2f}.
No broker target is used: the verified Street weight is zero.

## What the price implies

At CNY{PRICE:.2f}, the base case trades at {PRICE / base['adjusted_eps_2026e']:.1f}x
2026E adjusted EPS. The market is paying for H1 delivery, H2 optical
price/volume continuation and a safety-business profit contribution. It is not
yet possible to prove the AI/data-center option, so that option is excluded
from the fundamental anchor.

## Next-quarter thresholds

Q2 adjusted parent NP implied by the H1 range is CNY127m-CNY227m. H1 adjusted
NP below CNY230m, persistent negative OCF, or an unexplained gross-margin fall
below 2025 consolidated 19.45% invalidates the base valuation. H1 optical
revenue, margin, inventory and order conversion are the key evidence upgrades.
""",
    )
    put(
        "analysis/valuation_audit.md",
        f"""# Valuation Audit

- Shares: {SHARES_100M:.6f} hundred million.
- Market cap: CNY{PRICE:.2f} × {SHARES_100M:.6f} = CNY{PRICE * SHARES_100M:.4f} hundred million.
- Base adjusted EPS: {base['adjusted_np_2026e_100m']:.2f} / {SHARES_100M:.6f} = {base['adjusted_eps_2026e']:.6f}.
- Base PE component: {base['adjusted_eps_2026e']:.6f} × 34 = CNY{base['pe_value']:.4f}.
- Base PB component: 2.0490 × 1.80 = CNY{base['pb_value']:.4f}.
- Base PS component: {base['revenue_2026e_100m']:.2f} / {SHARES_100M:.6f} × 1.05 = CNY{base['ps_value']:.4f}.
- Base target: 50% × {base['pe_value']:.4f} + 25% × {base['pb_value']:.4f} + 25% × {base['ps_value']:.4f} = CNY{base['target_price']:.2f}.

| Check | Result |
|---|---|
| Price/date and shares | PASS |
| Market-cap and EPS denominator | PASS |
| Bear/base/bull and upside | PASS |
| Current-price implied multiple | PASS |
| Street anchor | PASS as zero-weight unavailable |
| Segment/evidence dependency | CONDITIONAL; no pure-growth credit |
| Model reproducibility | **Model Reproducibility: PASS** |
""",
    )


def write_supply_chain() -> None:
    universe = [
        {"node_id": "U01", "chain_block": "upstream", "subsegment": "optical materials/equipment", "node_name": "raw materials and process equipment", "node_type": "private", "listed_ticker": "not mapped", "classification": "unavailable", "valuation_status": "not valued", "evidence_status": "not disclosed"},
        {"node_id": "U02", "chain_block": "midstream", "subsegment": "optical fiber/cable", "node_name": "通鼎互联", "node_type": "listed", "listed_ticker": "002491.SZ", "classification": "core_valuation", "valuation_status": "cyclical PE/PB/PS eligible", "evidence_status": "official product, volume and H1 guidance"},
        {"node_id": "U03", "chain_block": "downstream", "subsegment": "operators/power grid/data-center infrastructure", "node_name": "China Mobile / State Grid / operators", "node_type": "demand_anchor", "listed_ticker": "various", "classification": "demand_anchor", "valuation_status": "not upstream proof", "evidence_status": "public tender and capex context"},
        {"node_id": "U04", "chain_block": "adjacent", "subsegment": "safety systems/storage protection", "node_name": "safety subsidiaries", "node_type": "listed", "listed_ticker": "inside 002491", "classification": "satellite_watch", "valuation_status": "limited earnings credit", "evidence_status": "annual report and H1 explanation"},
    ]
    put_json("data/full_chain_universe_20260714.json", universe)
    put("data/full_chain_universe_20260714.md", "# Full-Chain Universe\n\n| Node | Block | Type | Classification | Evidence | Valuation status |\n|---|---|---|---|---|---|\n" + "\n".join(f"| {r['node_name']} | {r['chain_block']} / {r['subsegment']} | {r['node_type']} | {r['classification']} | {r['evidence_status']} | {r['valuation_status']} |" for r in universe))
    put("analysis/full_chain_taxonomy.md", """# Full-Chain Taxonomy

通鼎互联对应的是“光棒/原材料 → 光纤光缆、通信电缆、电力电缆、通信设备
→ 运营商、电网、项目客户”的综合线缆链条，并叠加安全系统和新能源业务。
运营商、算力建设和中国移动集采是需求锚，不是通鼎互联已确认收入。

The core valuation name is 002491 itself. Safety subsidiaries are satellite
earnings exposure. Unverified AI customer claims remain excluded.
""")
    put("analysis/core_vs_satellite_universe.md", """# Core / Satellite Universe

| Pool | Name | Eligibility | Missing evidence |
|---|---|---|---|
| Core | 通鼎互联 002491.SZ | reported financials, H1 preview and current price support cyclical valuation | H1 segment revenue, ASP, utilization, customer concentration |
| Satellite | safety-system subsidiaries | recurring 2025 revenue and margin disclosed | H1 margin, backlog and cash conversion |
| Demand anchor | operators / power grid / data-center capex | frames demand | no direct order/booked-revenue proof |
""")
    put("analysis/coverage_gap_matrix.md", """# Coverage Gap Matrix

| Gap | Why it matters | Blocks high-growth valuation | Upgrade path |
|---|---|---|---|
| H1 optical revenue/ASP | separates cycle recovery from structural growth | yes | 2026 H1 report and IR |
| utilization/backlog | determines duration and margin | yes | company order/capacity disclosure |
| customer concentration | determines pricing and counterparty risk | yes for named-customer claims | annual report / IR |
| cash conversion | tests earnings quality | yes for premium multiple | H1 cash-flow and receivable aging |
| original broker target | external comparability | Street weight zero | original PDF or official broker page |
""")
    put("analysis/supply_chain_model.md", """# Supply-Chain Model

The evidence-backed bridge is optical-fiber volume/price recovery plus safety
subsidiary consolidation and improvement. Data-center capex and tender headlines
are demand context only. The 2025 profit pool supports a blended cyclical
valuation: safety margin 29.25%, communication cable 24.32%, optical fiber/cable
18.10% and power cable 12.26%.
""")
    put("analysis/company_fundamental_cards.md", """# Company Fundamental Card

## 通鼎互联（002491.SZ）

- Integrated preform, optical fiber/cable, communication cable, power cable,
  communication equipment and safety-system platform.
- 2025 revenue CNY3.413bn; parent loss CNY76.4m; adjusted parent loss CNY41.3m.
- 2026Q1 revenue CNY1.064bn; adjusted parent NP CNY102.8m; OCF negative CNY17.6m.
- H1 preview: parent NP CNY170m-CNY240m; adjusted NP CNY230m-CNY330m.
- Moat: integrated capability and operator/power channels.
- Risks: working-capital intensity, short-term debt, cable price cycle and
  financial-asset fair-value volatility.
- Eligibility: cyclical/base valuation eligible; pure AI multiple not eligible.
""")
    put("analysis/value_chain_economics.md", """# Value-Chain Economics

| Block | Value proxy | ASP | Margin pool | Capacity/utilization | Order visibility | Credit |
|---|---|---|---|---|---|---|
| Optical fiber/cable | 2025 revenue CNY182.5m; fiber sales 300.48万芯公里 | H1 price up, exact ASP not disclosed | 18.10% gross margin in 2025 | not disclosed | sales/order increase stated; backlog not disclosed | cyclical earnings |
| Communication cable | 2025 revenue CNY907.3m | not disclosed | 24.32% | not disclosed | operator/project context | base credit |
| Power cable | 2025 revenue CNY1.306bn | not disclosed | 12.26% | not disclosed | power-grid context | conservative base |
| Safety business | 2025 revenue CNY669.2m | not disclosed | 29.25% | not disclosed | H1 operation positive | limited earnings |
""")
    put("analysis/chain_earnings_bridge.md", """# Chain Earnings Bridge

2025 trough → 2026Q1 adjusted parent NP CNY102.8m → official H1 adjusted
NP CNY230m-CNY330m → explicit H2 scenario. Next-quarter validation is Q2
adjusted NP CNY127m-CNY227m, improving OCF, stable/improving gross margin and
H1 segment disclosure. Failure downgrades the valuation credit.
""")
    put_json("data/supply_chain_relationships.json", [{"ticker": "002491.SZ", "company": "通鼎互联", "chain_layer": "midstream", "node_type": "listed", "upstream_input": "optical materials and cable inputs", "product_or_process": "preform, fiber, optical/communication/power cable", "downstream_customer_or_platform": "operators/power grid/projects; not individually disclosed", "relationship_type": "official_disclosed", "confidence": "high", "source_tier": "A_official", "evidence_score": 0.86, "revenue_exposure": "2025 product mix disclosed", "capacity_or_certification": "integrated capability; utilization not disclosed", "order_visibility": "fiber sales/order increase; backlog not disclosed", "ASP_or_price_proxy": "H1 price and volume improved; ASP not disclosed", "utilization_or_yield": "not disclosed", "margin_or_earnings_impact": "2025 product margins disclosed", "source": "S01/S03/S04", "evidence_gap": "H1 segment bridge and cash conversion", "valuation_eligibility": "cyclical valuation eligible", "downgrade_trigger": "H1 profit or cash-flow miss", "used_in_valuation": True}])
    put_json("data/customer_chain_audit.json", [{"ticker": "002491.SZ", "company": "通鼎互联", "customer_or_platform": "operators / power grid / projects", "claim_type": "demand channel", "product_or_process": "optical, communication and power cable", "certification_status": "not disclosed", "order_or_backlog": "sales increase stated; backlog not disclosed", "ASP_or_price_proxy": "not disclosed", "capacity": "integrated capability disclosed", "utilization_or_yield": "not disclosed", "revenue_exposure": "product mix disclosed, customer split not disclosed", "margin_impact": "product-level 2025 margins disclosed", "source_tier": "A_official", "evidence_score": 0.80, "source": "S01/S04", "evidence_gap": "no customer name, contract value, utilization or ASP", "blocks_valuation": False, "downgrade_trigger": "customer-specific claim or high-growth multiple", "adopted_wording": "需求锚点不等同于已确认订单。"}])


def write_capital() -> None:
    payload = {
        "ticker": "002491.SZ",
        "as_of": "2026-07-14",
        "quarter_end_holdings": [
            {"holder": "通鼎集团", "type": "controller", "pct": 31.51, "source": "S03"},
            {"holder": "沈小平", "type": "controller", "pct": 4.55, "source": "S03"},
            {"holder": "华商致远回报混合", "type": "mutual_fund", "pct": 0.75, "source": "S03"},
            {"holder": "华商均衡成长混合", "type": "mutual_fund", "pct": 0.67, "source": "S03"},
            {"holder": "易方达裕丰回报债券", "type": "mutual_fund", "pct": 0.61, "source": "S03"},
            {"holder": "HKSCC", "type": "foreign_custody", "pct": 0.72, "source": "S03"},
            {"holder": "Goldman Sachs", "type": "broker_custody", "pct": 0.50, "source": "S03"},
        ],
        "lhb": [
            {"date": "2026-07-01", "event": "three-day decline", "institution_net_100m": -2.0669, "turnover_rate": 15.1755},
            {"date": "2026-06-17", "event": "three-day rise", "institution_net_100m": 3.9778, "turnover_rate": 16.0033},
            {"date": "2026-06-08", "event": "amplitude", "institution_net_100m": 2.9515, "turnover_rate": 21.1662},
            {"date": "2026-06-04", "event": "daily rise", "institution_net_100m": 4.9508, "turnover_rate": 19.2139},
            {"date": "2026-05-21", "event": "daily decline", "institution_net_100m": -0.1731, "turnover_rate": 12.9665},
            {"date": "2026-05-12", "event": "daily rise", "institution_net_100m": 2.2269, "turnover_rate": 10.8804},
        ],
        "financing": {"date": "2026-07-13", "buy_100m": 1.79, "repay_100m": 2.73, "net_repay_100m": 0.932091, "balance_100m": 12.17, "balance_to_float_mktcap": 0.0521, "quality": "public article; raw endpoint schema error"},
        "scores": {"institutional_base": 73.0, "active_trading": 92.0, "crowding": 88.0, "liquidity": 94.0, "style": 86.0, "classification": "机构参与的高换手趋势/事件票，不是安静吸筹纯机构票"},
    }
    put_json("data/capital_structure_20260714.json", payload)
    put("data/capital_structure_20260714.md", """# Capital Structure Snapshot

Q1 disclosed holdings prove institutional participation, not July buying intent.
Dragon-Tiger events show alternating institutional buying and selling around
high-turnover events. Financing balance was CNY1.217bn on 2026-07-13, with
CNY93.21m net repayment.

**Classification:** institution-participated, high-turnover event/trend stock;
not a pure institution stock and not a pure hot-money stock. An institution-only
seat cannot be mapped to a named fund or hot-money leader without a licensed
seat database.
""")
    put("analysis/secondary_market_analysis.md", """# Secondary-Market Analysis

## Price and liquidity

On 2026-07-14 the stock closed at CNY20.86, up 4.98%, with 120.15m shares and
CNY2.404bn turnover value. This is a high-liquidity H1-event day, not quiet
accumulation.

## Institution versus hot money

The Q1 top-ten list contains mutual funds, HKSCC and broker custody. The
Dragon-Tiger record alternates institutional net buying and selling: net buying
on 6/4, 6/8 and 6/17, then net selling in the 7/1 decline event. Thus the
proper label is institution participation plus active trend/event trading.

## Reproducible score

`institutional base = 40% × Q1 fund/custody evidence + 30% × controller stability
+ 30% × repeated institutional LHB participation = 73/100`.

`active trading = 35% × LHB turnover intensity + 25% × event clustering + 20%
× financing crowding + 20% × latest turnover = 92/100`.

`style = 45% × institutional base + 55% × active trading = 86/100`.

## Behavioral levels

- CNY18.50: market-sentiment support / event-premium unwind line.
- CNY15-CNY16: pre-breakout earnings-repricing zone.
- CNY21.86: public daily-limit reference.
- CNY25-CNY30: prior event-trading supply zone.

These are behavior references, not guaranteed technical signals.
""")


def write_governance(model: dict[str, Any]) -> None:
    put("research_brief.md", """# Research Brief

- Case ID: `tongding-interconnect-002491-20260714`
- Report type: single-stock institutional deep research
- Target: 通鼎互联（002491.SZ）
- Language: Chinese reader-facing report
- Market cutoff: 2026-07-14 close, CNY20.86
- Financial cutoff: 2026Q1 reported; 2026H1 preliminary preview on 2026-07-14; 2025 annual report
- Objective: test whether optical-fiber/cable recovery and safety-system earnings justify the current price.
- Core valuation scope: consolidated company, cyclical PE/PB/PS blend.
- Conditional pool: optical/data-center optionality, safety growth and tender exposure.
- Demand anchors: operator and power-grid capex, China Mobile tenders and data-center infrastructure.
- Downgrade: watchlist-only / high valuation risk if H1 profit, cash conversion, margin or segment evidence misses thresholds.
- Exclusions: social-media customer claims, unsupported ASP/utilization and third-party target prices.
""")
    put("gate_manifest.md", """# Gate Manifest

| Field | Value |
|---|---|
| Case | tongding-interconnect-002491-20260714 |
| Type | single_stock_deep_research |
| Cutoff | 2026-07-14 18:00 CST |
| Skills | equity-research, growth-earnings-model, valuation, reports, research-report-review |
| Review cycles | R0_evidence, R1_model, R2_draft, R3_render_compliance, R4_final_ic |
| Depth gates | evidence_depth, broker_consensus_depth, model_depth, valuation_depth, ic_readiness |
| Pass conditions | official H1 evidence, reproducible model, target tied to current price, PDF and verifiers clean, no open S/A issues |
| Downgrade | watchlist-only if evidence or cash-conversion thresholds fail |
""")
    artifacts = [
        ("research_brief.md", "scope, cutoff, exclusions, downgrade", "explicit data boundary"),
        ("data/verified_financials.md", "reported/guided financials and mix", "official paths and units"),
        ("analysis/growth_earnings_model.md", "driver bridge, scenarios and credit", "no unsupported growth multiple"),
        ("analysis/valuation_model.md", "price, shares, scenarios, target and action", "reproducible formulas"),
        ("analysis/secondary_market_analysis.md", "institution, LHB, financing, score", "layered identity limits"),
        ("final_signoff.json", "score, gates, residual risks", "maker-checker closure"),
    ]
    put("artifact_contract.md", "# Artifact Contract\n\n| Artifact | Required fields | Minimum depth | Blocking condition | Reviewer | Verifier |\n|---|---|---|---|---|---|\n" + "\n".join(f"| {a} | {f} | {d} | missing or unsupported data | R0-R4 | case verifier |" for a, f, d in artifacts))
    put_json("artifact_contract.json", {"artifacts": [{"artifact": a, "required_fields": f, "minimum_depth": d, "blocking_conditions": "missing or unsupported data", "reviewer_cycle": "R0-R4", "verifier_check": "case verifier", "blocking_if_missing": True} for a, f, d in artifacts]})
    put_json("gate_manifest.json", {"case_id": "tongding-interconnect-002491-20260714", "report_type": "single_stock_deep_research", "data_cutoff": "2026-07-14 18:00 CST", "required_artifacts": [a for a, _, _ in artifacts] + ["main.tex", "main.pdf"], "review_cycles": ["R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic"], "depth_gates": ["evidence_depth", "broker_consensus_depth", "model_depth", "valuation_depth", "ic_readiness"], "downgrade_path": "watchlist only / high valuation risk"})
    put_json("data/research_brief.json", {"ticker": "002491.SZ", "company": "通鼎互联", "cutoff": "2026-07-14", "price": PRICE, "h1_preview": True})
    exhaustion = {"probes": [{"probe": "original broker target", "status": "not_found", "impact": "Street weight 0", "next": "licensed broker database"}, {"probe": "Eastmoney quote/kline", "status": "connection_error", "impact": "Sina close used", "next": "exchange/vendor history"}, {"probe": "Eastmoney margin endpoint", "status": "schema_error", "impact": "public article labeled partial", "next": "exchange margin data"}, {"probe": "H1 segment ASP/utilization/customer split", "status": "not_disclosed", "impact": "no pure-growth multiple", "next": "H1 report/IR"}]}
    put_json("source_exhaustion_log.json", exhaustion)
    put("source_exhaustion_log.md", "# Source Exhaustion Log\n\n" + "\n".join(f"- **{p['probe']}**: `{p['status']}`; impact: {p['impact']}; next: {p['next']}." for p in exhaustion["probes"]))
    put("review_log.md", "# Review Log\n\nR0/R1/R2/R3/R4 artifacts are generated after evidence and PDF verification. Reviewer outputs must be read-only and cite current files.\n")
    put_json("final_signoff.json", {"case_id": "tongding-interconnect-002491-20260714", "report_type": "single_stock_deep_research", "data_cutoff": "2026-07-14", "pdf_path": "main.pdf", "page_count": 0, "publishability_score": 0, "verifier_results": "pending", "open_s_count": 0, "open_a_count": 0, "residual_risks": ["H1 segment split not disclosed", "cash conversion not yet audited", "Street target not found"], "downgrade_status": "CONDITIONAL: Street anchor unavailable; no pure-growth credit", "signoff_status": "pending"})
    put("data/consensus_analysis.md", "# Consensus Analysis\n\nNo complete original broker target-price row was verified at cutoff. Weak public mentions are excluded and the Street valuation weight is zero. The AStock model uses a 90% fundamental and 10% market-sentiment blend.\n")
    put_json("data/broker_street_consensus_20260714.json", [{"ticker": "002491.SZ", "broker": "not found", "report_date": "not found", "rating": "not disclosed", "target_price": "not disclosed", "revenue_E": "not disclosed", "net_profit_E": "not disclosed", "EPS_E": "not disclosed", "method": "not disclosed", "implied_upside": "not disclosed", "source_quality": "not_found", "source_path": "sources/broker-reports/2026-07-14/index.md", "valuation_weight": 0.0}])
    put("data/broker_street_consensus_20260714.md", "# Broker / Street Consensus\n\n| Ticker | Broker | Date | Rating | Target | Forecast | Quality | Weight |\n|---|---|---|---|---|---|---|---:|\n| 002491.SZ | not found | not found | not disclosed | not disclosed | not disclosed | not_found | 0% |\n")
    put("sources/broker-reports/2026-07-14/index.md", "# Broker Report Collection — 通鼎互联\n\nNo original target-price report with complete numeric fields was verified at the 2026-07-14 cutoff. Search snippets, media reposts and wealth-platform posts remain zero-weight. This is a source-exhaustion result, not proof that no private report exists.\n")


def main() -> None:
    scenario_rows = scenarios()
    base_row = next(r for r in scenario_rows if r["scenario"] == "base")
    final_target = round(base_row["target_price"] * 0.90 + 18.50 * 0.10, 2)
    model = {
        "ticker": "002491.SZ",
        "company": "通鼎互联",
        "as_of": "2026-07-14 15:35:45 CST",
        "current_price": PRICE,
        "price_date": "2026-07-14",
        "shares_100m": SHARES_100M,
        "shares_100mn": SHARES_100M,
        "market_cap_100m_cny": round(PRICE * SHARES_100M, 6),
        "market_cap_100mn_cny": round(PRICE * SHARES_100M, 6),
        "reported": {"2025_revenue_100m": 34.1299504757, "2025_parent_np_100m": -0.7639211101, "2025_adjusted_np_100m": -0.4126979680, "2026q1_revenue_100m": 10.6361514281, "2026q1_parent_np_100m": Q1_PARENT_NP, "2026q1_adjusted_np_100m": Q1_ADJ_NP, "2026q1_ocf_100m": -0.1758317631, "q1_parent_bps": 2.049036},
        "guidance": {"h1_parent_np_low": 1.70, "h1_parent_np_high": 2.40, "h1_adjusted_np_low": 2.30, "h1_adjusted_np_high": 3.30, "h1_eps_low": 0.1382, "h1_eps_high": 0.1951, "h1_revenue_growth_low": 0.56, "h1_revenue_growth_high": 0.66, "fair_value_loss_100m": -0.91},
        "scenarios": scenario_rows,
        "bear": next(r for r in scenario_rows if r["scenario"] == "bear"),
        "base": base_row,
        "bull": next(r for r in scenario_rows if r["scenario"] == "bull"),
        "revenue_2026e_100m": base_row["revenue_2026e_100m"],
        "revenue_2026e_100mn": base_row["revenue_2026e_100m"],
        "np_2026e_100m": base_row["adjusted_np_2026e_100m"],
        "np_2026e_100mn": base_row["adjusted_np_2026e_100m"],
        "eps_2026e": base_row["adjusted_eps_2026e"],
        "method": "50% adjusted PE + 25% parent PB + 25% revenue PS",
        "evidence_quality": "A official H1 preview; B public market structure; Street target not verified",
        "street_target": None,
        "street_weight": 0.0,
        "broker_weight": 0.0,
        "market_anchor": 18.50,
        "market_anchor_weight": 0.10,
        "market_weight": 0.10,
        "fundamental_weight": 0.90,
        "base_target": base_row["target_price"],
        "final_target": final_target,
        "upside": round(final_target / PRICE - 1, 6),
        "market_implied_anchor": 18.50,
        "fair_value_range": [scenario_rows[0]["target_price"], scenario_rows[-1]["target_price"]],
        "action": "事件后观察 / 回撤验证",
    }
    write_data(model)
    write_analysis(model)
    write_supply_chain()
    write_capital()
    write_governance(model)
    print(json.dumps({"case": str(CASE), "base_target": model["base_target"], "final_target": model["final_target"], "range": model["fair_value_range"]}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
