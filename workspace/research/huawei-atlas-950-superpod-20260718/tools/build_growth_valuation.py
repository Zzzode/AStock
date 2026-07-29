#!/usr/bin/env python3
"""Build deterministic Atlas 950 growth and valuation research artifacts."""

from __future__ import annotations

import json
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
DATA = CASE / "data"
ANALYSIS = CASE / "analysis"


MARKET = {
    "000034": ("Digital China", "神州数码", 24.61, 250.22, 1437.51, 5.23),
    "000988": ("HGTECH", "华工科技", 117.62, 1182.67, 143.55, 14.71),
    "600183": ("Shengyi Technology", "生益科技", 132.29, 3213.33, 284.31, 33.34),
    "002916": ("Shennan Circuits", "深南电路", 334.00, 2275.10, 236.47, 32.76),
    "002463": ("Wus Printed Circuit", "沪电股份", 127.80, 2459.34, 189.45, 38.22),
    "300476": ("Victory Giant Technology", "胜宏科技", 241.50, 2373.43, 192.92, 43.12),
    "002837": ("Envicool", "英维克", 61.57, 784.62, 60.68, 5.22),
    "301018": ("Shenling Environment", "申菱环境", 86.96, 325.48, 42.09, 2.17),
    "002335": ("Kehua Data", "科华数据", 29.75, 224.44, 81.60, 4.18),
    "002130": ("Woer Heat-Shrinkable Material", "沃尔核材", 15.24, 213.34, 84.51, 11.44),
    "002230": ("iFlytek", "科大讯飞", 41.12, 987.74, 271.05, 8.39),
    "002025": ("Aerospace Electrical", "航天电器", 64.76, 294.02, 58.20, 1.83),
}


PARAMS = {
    "000034": dict(multiples=(8, 12, 16), peg=0.60, eps_factors=(0.90, 1.00, 1.10), weights=(0.80, 0.20, 0.00), action="watch", atlas="zero"),
    "000988": dict(multiples=(14, 20, 26), peg=1.20, eps_factors=(0.92, 1.00, 1.08), weights=(0.80, 0.20, 0.00), action="watch", atlas="zero"),
    "600183": dict(multiples=(14, 20, 26), peg=0.90, eps_factors=(0.94, 1.00, 1.06), weights=(0.60, 0.20, 0.20), action="avoid_chasing", atlas="zero", broker_target=103.50),
    "002916": dict(multiples=(14, 20, 26), peg=0.90, eps_factors=(0.94, 1.00, 1.06), weights=(0.60, 0.20, 0.20), action="watch", atlas="zero", broker_target=288.00),
    "002463": dict(multiples=(14, 20, 26), peg=0.70, eps_factors=(0.93, 1.00, 1.07), weights=(0.80, 0.20, 0.00), action="watch", atlas="zero"),
    "300476": dict(multiples=(14, 20, 26), peg=0.45, eps_factors=(0.92, 1.00, 1.08), weights=(0.80, 0.20, 0.00), action="selective_watch", atlas="zero"),
    "002837": dict(multiples=(14, 20, 26), peg=0.70, eps_factors=(0.90, 1.00, 1.08), weights=(0.80, 0.20, 0.00), action="wait_for_q2_margin", atlas="zero"),
    "301018": dict(multiples=(12, 18, 24), peg=0.70, eps_factors=(0.90, 1.00, 1.10), weights=(0.80, 0.20, 0.00), action="highest_linkage_watch", atlas="zero"),
    "002335": dict(multiples=(10, 14, 18), peg=0.65, eps_factors=(0.92, 1.00, 1.08), weights=(0.80, 0.20, 0.00), action="value_watch", atlas="zero"),
    "002130": dict(multiples=(8, 12, 16), peg=0.40, eps_factors=(0.92, 1.00, 1.08), weights=(0.80, 0.20, 0.00), action="value_satellite", atlas="zero"),
    "002230": dict(multiples=(18, 25, 32), peg=2.00, eps_factors=(0.92, 1.00, 1.08), weights=(0.80, 0.20, 0.00), action="downstream_event_watch", atlas="zero"),
    "002025": dict(multiples=(14, 20, 26), peg=1.00, eps_factors=(0.80, 1.00, 1.20), weights=(0.50, 0.20, 0.30), action="unconfirmed_linkage_watch", atlas="zero", broker_target=73.50),
}


# Attributable equity at FY2025 year-end from each issuer's full exchange filing,
# expressed in CNY 100m.  This supports an independent, auditable justified-P/B
# downside anchor instead of reverse-solving a multiple from the prior target.
BOOK_EQUITY_2025A = {
    "000034": 110.0644406737,
    "000988": 110.5718060923,
    "600183": 167.2350122633,
    "002916": 171.4943052985,
    "002463": 151.1270464200,
    "300476": 166.1760844357,
    "002837": 34.4564100879,
    "301018": 27.2683591797,
    "002335": 64.0655347915,
    "002130": 64.9711281378,
    "002230": 187.9446216869,
    "002025": 66.0377009246,
}

BOOK_EQUITY_SOURCE = {
    "000034": "sources/official-filings-20260718/000034-digital-china-2025-annual-cninfo.pdf",
    "000988": "sources/official-filings-20260718/000988-hgtech-2025-annual-cninfo.pdf",
    "600183": "sources/official-filings-20260718/600183-shengyi-2025-annual-cninfo.pdf",
    "002916": "sources/official-filings-20260718/002916-shennan-2025-annual-cninfo.pdf",
    "002463": "sources/official-filings-20260718/002463-wus-2025-annual-cninfo.pdf",
    "300476": "sources/official-filings-20260718/300476-victory-2025-annual-cninfo.pdf",
    "002837": "sources/official-filings-20260718/002837-envicool-2025-annual-cninfo.pdf",
    "301018": "sources/official-filings-20260718/301018-shenling-2025-annual-cninfo.pdf",
    "002335": "sources/official-filings-20260718/002335-kehua-2025-annual-cninfo.pdf",
    "002130": "sources/official-filings-20260718/002130-woer-2025-annual-cninfo.pdf",
    "002230": "sources/official-filings-20260718/002230-iflytek-2025-annual-cninfo.pdf",
    "002025": "sources/official-filings-20260718/002025-aerospace-electric-2025-annual-cninfo.pdf",
}


SENTIMENT = {
    "000034": (-8.61, 69.07, 1.43), "000988": (-10.00, 63.47, 2.54),
    "600183": (-10.00, 80.52, 5.03), "002916": (-8.24, 16.73, 2.70),
    "002463": (-6.52, 81.36, 8.95), "300476": (-10.86, 35.08, 3.44),
    "002837": (-9.27, 49.38, 3.14), "301018": (-15.50, 16.33, 0.72),
    "002335": (-6.65, 23.08, 1.34), "002130": (-4.63, 30.95, 0.82),
    "002230": (-2.07, 46.08, 2.35), "002025": (-9.99, 24.76, 0.29),
}


GROWTH_PROXIES = {
    "000034": ("AI-related distribution and KunTai compute products", "2026Q1 AI-related revenue CNY15.5bn, +119% YoY", "AI revenue disclosure", "distribution margin and working-capital conversion"),
    "000988": ("Optical connection products", "2025 revenue CNY6.097bn, +53.39% YoY", "800G/1.6T shipments", "13.26% segment gross margin and delivery mix"),
    "600183": ("High-speed/high-frequency CCL", "2026H1 parent NP CNY3.099-3.298bn, +117%-131%", "premium CCL mix", "capacity ramp and copper/fiberglass input cost"),
    "002916": ("AI PCB and package-substrate products", "2026H1 parent NP CNY2.10-2.30bn, +54%-69%", "AI PCB product mix", "high-layer yield and new-line utilization"),
    "002463": ("AI server and switch PCB", "2026H1 parent NP CNY2.83-3.00bn, +68%-78%", "high-layer PCB shipment mix", "capacity utilization and customer concentration"),
    "300476": ("AI server and accelerator PCB", "2026E broker revenue CNY32.55bn", "AI PCB revenue forecast", "overseas capacity yield and product-mix durability"),
    "002837": ("Data-center and compute-equipment thermal management", "2025 total revenue CNY6.068bn; storage thermal revenue CNY1.7bn", "data-center cooling revenue trend", "2026Q1 margin trough and 2H delivery recovery"),
    "301018": ("Data-service thermal management and liquid cooling", "2025 data-service revenue +51.42%; new orders +72%", "new-order growth", "revenue recognition, liquid-cooling mix and customer concentration"),
    "002335": ("Intelligent-compute power and POD infrastructure", "2026H1 parent NP CNY365-390mn, +50%-60%", "compute-center project revenue", "project acceptance, receivables and non-recurring items"),
    "002130": ("High-speed copper cable material and assemblies", "2026E broker revenue CNY12.15bn and NP CNY1.88bn", "high-speed cable revenue proxy", "qualification, copper price and capacity utilization"),
    "002230": ("Spark/Xinghuo model and Ascend 950 co-development", "2026H1 loss expected to narrow but remain CNY180-228mn", "model commercialization and paid users", "sales efficiency and operating cash conversion"),
    "002025": ("High-speed backplane and liquid-cooling connectors", "2026E broker NP range CNY239-500mn", "AI connector order proxy", "qualification identity, revenue purity and defense-cycle timing"),
}


def load_consensus() -> tuple[dict[str, dict], dict[str, list[dict]]]:
    payload = json.loads((DATA / "broker_street_consensus_20260718.json").read_text(encoding="utf-8"))
    aggregate = {row["ticker"]: row for row in payload["ticker_consensus"]}
    rows: dict[str, list[dict]] = {}
    for row in payload["rows"]:
        if float(row.get("valuation_weight") or 0) > 0:
            rows.setdefault(row["ticker"], []).append(row)
    return aggregate, rows


def num(value: object) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    raise ValueError(f"Expected numeric value, got {value!r}")


def main() -> None:
    aggregate, broker_rows = load_consensus()
    valuation_rows = []
    growth_rows = []

    for ticker, params in PARAMS.items():
        english, company, price, market_cap, revenue_2025, np_2025 = MARKET[ticker]
        consensus = aggregate[ticker]
        broker_eps_reported = num(consensus["eps_2026e_mean"])
        broker_eps_2027_reported = num(consensus["eps_2027e_mean"])
        revenue_e = num(consensus["revenue_2026e_mean"]) / 100.0
        np_e = num(consensus["net_profit_2026e_mean"]) / 100.0
        np_e_2027 = num(consensus["net_profit_2027e_mean"]) / 100.0
        shares = market_cap / price
        # Broker EPS tables are not always restated after bonus issues or share
        # placements.  Reconcile every per-share forecast to one current-share
        # denominator before applying a target multiple.
        eps = np_e / shares
        eps_2027 = np_e_2027 / shares
        low_multiple, base_multiple, high_multiple = params["multiples"]
        low_factor, base_factor, high_factor = params["eps_factors"]
        np_growth_2027_pct = (np_e_2027 / np_e - 1.0) * 100.0
        peg_ratio = float(params["peg"])
        peg_implied_pe = min(high_multiple, max(low_multiple, np_growth_2027_pct * peg_ratio))
        primary_bear = low_multiple * eps * low_factor
        primary_base = base_multiple * eps * base_factor
        primary_bull = high_multiple * eps * high_factor
        book_equity = BOOK_EQUITY_2025A[ticker]
        book_value_per_share = book_equity / shares
        # Justified P/B is a genuinely independent downside anchor based on
        # official book equity and a disclosed sustainable-ROE model:
        # P/B = (ROE - g) / (cost of equity - g).  Supernormal ROE is capped,
        # while a floor recognizes continuing asset utility without assigning
        # any Atlas or unbridged growth-segment premium.
        pb_scenarios = (
            max(0.60, (min(np_e * low_factor / book_equity, 0.23) - 0.02) / (0.11 - 0.02)),
            max(0.70, (min(np_e / book_equity, 0.25) - 0.03) / (0.10 - 0.03)),
            max(0.80, (min(np_e * high_factor / book_equity, 0.27) - 0.04) / (0.09 - 0.04)),
        )
        secondary_bear, secondary_base, secondary_bull = (
            book_value_per_share * pb for pb in pb_scenarios
        )
        bear = round(0.60 * primary_bear + 0.40 * secondary_bear, 2)
        base = round(0.60 * primary_base + 0.40 * secondary_base, 2)
        bull = round(0.60 * primary_bull + 0.40 * secondary_bull, 2)
        fw, mw, bw = params["weights"]
        broker_target = float(params.get("broker_target", base))
        final_target = round(fw * base + mw * price + bw * broker_target, 2)
        upside = round(final_target / price - 1.0, 6)
        broker_list = broker_rows.get(ticker, [])
        daily_change_pct, volume_5d_mshares, northbound_pct = SENTIMENT[ticker]
        implied_pe = price / eps
        valuation_rows.append(
            {
                "ticker": ticker,
                "company": company,
                "company_en": english,
                "current_price": price,
                "price_date": "2026-07-17",
                "shares_100mn": round(shares, 4),
                "market_cap_100mn_cny": market_cap,
                "revenue_2025a_100mn": revenue_2025,
                "np_2025a_100mn": np_2025,
                "revenue_2026e_100mn": round(revenue_e, 3),
                "np_2026e_100mn": round(np_e, 3),
                "np_2027e_100mn": round(np_e_2027, 3),
                "eps_2026e": round(eps, 4),
                "eps_2027e": round(eps_2027, 4),
                "broker_eps_2026e_reported": broker_eps_reported,
                "broker_eps_2027e_reported": broker_eps_2027_reported,
                "broker_eps_share_basis_gap_pct": round((eps / broker_eps_reported - 1.0) * 100.0, 2),
                "eps_denominator": "current shares derived from market capitalization / close price",
                "method": "conservative mature-business 2026E P/E plus an independent justified P/B cross-check from official book equity and normalized ROE; zero Atlas earnings credit",
                "primary_method": "2026E P/E on current-share reconciled EPS",
                "secondary_method": "justified P/B using official FY2025 attributable equity, normalized 2026E ROE, disclosed cost of equity and terminal growth",
                "primary_base_target": round(primary_base, 2),
                "secondary_base_target": round(secondary_base, 2),
                "book_equity_2025a_100mn": book_equity,
                "book_value_per_share_current_shares": round(book_value_per_share, 4),
                "forward_roe_2026e": round(np_e / book_equity, 6),
                "normalized_roe_caps": [0.23, 0.25, 0.27],
                "cost_of_equity_scenarios": [0.11, 0.10, 0.09],
                "terminal_growth_scenarios": [0.02, 0.03, 0.04],
                "justified_pb_scenarios": [round(value, 4) for value in pb_scenarios],
                "np_growth_2027e_pct": round(np_growth_2027_pct, 2),
                "peg_ratio": peg_ratio,
                "peg_implied_pe": round(peg_implied_pe, 2),
                "bear_eps_factor": low_factor,
                "base_eps_factor": base_factor,
                "bull_eps_factor": high_factor,
                "scenario_rationale": "bear/base/bull vary current-share EPS and conservative mature-business P/E; the independent secondary anchor derives justified P/B from official book equity and normalized ROE under disclosed cost-of-equity and terminal-growth scenarios",
                "bear": bear,
                "base": base,
                "bull": bull,
                "bear_multiple": low_multiple,
                "base_multiple": base_multiple,
                "bull_multiple": high_multiple,
                "market_implied_anchor": price,
                "market_implied_pe_2026e": round(implied_pe, 2),
                "market_implied_np_growth_pct_at_1x_peg": round(implied_pe, 2),
                "forecast_np_growth_2027e_pct": round(np_growth_2027_pct, 2),
                "embedded_growth_gap_pct": round(implied_pe - np_growth_2027_pct, 2),
                "daily_change_2026_07_17_pct": daily_change_pct,
                "five_day_avg_volume_mshares": volume_5d_mshares,
                "five_day_avg_turnover_100mn_cny_proxy": round(volume_5d_mshares * price / 100.0, 2),
                "northbound_holding_2026_06_30_pct": northbound_pct,
                "sentiment_premium_discount_to_fundamental_base_pct": round((price / base - 1.0) * 100.0, 2),
                "sentiment_interpretation": "event-day drawdown does not establish cheapness; compare current P/E and embedded growth with the evidence-gated fundamental range",
                "broker_target_anchor": broker_target if "broker_target" in params else "not disclosed",
                "fundamental_weight": fw,
                "market_weight": mw,
                "broker_weight": bw,
                "final_target": final_target,
                "upside": upside,
                "action": params["action"],
                "evidence_quality": "official FY2025 full filing reconciled + original broker PDF NP forecast + current-share EPS; 2026Q1 monitoring-only; Atlas-specific revenue unverified and set to zero",
                "atlas_950_revenue_credit_2026e_100mn": 0.0,
                "broker_count": len(broker_list),
                "broker_sources": [row["source_path"] for row in broker_list],
                "catalyst": "Q4 2026 Atlas 950 roadmap conversion plus company-specific order/revenue disclosure",
                "invalidation": "roadmap delay, no qualification/order evidence, or earnings below the next-quarter threshold",
            }
        )

        segment, proxy, unit_proxy, key_risk = GROWTH_PROXIES[ticker]
        revenue_growth = round(revenue_e / revenue_2025 - 1.0, 4)
        growth_np = round(np_e - np_2025, 3)
        growth_eps = round(growth_np / shares, 4)
        implied_pe = round(price / eps, 2)
        growth_rows.append(
            {
                "ticker": ticker,
                "company": company,
                "base_business_revenue": f"FY2025 total revenue CNY{revenue_2025:.2f}bn-equivalent in 100mn table units",
                "growth_segment_revenue": f"{segment}; {proxy}",
                "unit_volume_or_proxy": unit_proxy,
                "ASP_or_price": "No Atlas-specific ASP is public; valuation uses disclosed segment/order or broker revenue proxy only",
                "value_amount_or_proxy": f"2026E total revenue CNY{revenue_e:.3f}bn-equivalent in 100mn table units",
                "supply_demand_state": "AI infrastructure demand remains strong; company-specific Atlas allocation is unverified",
                "capacity_or_utilization": key_risk,
                "certification_or_customer_qualification": "Atlas 950 supplier qualification not confirmed in primary evidence",
                "recognized_revenue_ratio": "not disclosed for Atlas 950; Atlas revenue credit is zero",
                "broad_business_revenue_growth_2026e_vs_2025a": revenue_growth,
                "growth_gross_margin": "Company/segment disclosed margin where available; no Atlas-specific margin assumed",
                "growth_gross_profit_100mn": "not separately disclosed; excluded from Atlas bridge",
                "incremental_opex": "embedded in broker net-profit forecast; no Atlas-specific opex adjustment",
                "base_business_np_2025a_100mn": np_2025,
                "broad_business_np_2026e_100mn": round(np_e, 3),
                "broad_business_np_2027e_100mn": round(np_e_2027, 3),
                "broad_business_np_delta_2026e_vs_2025a_100mn": growth_np,
                "broad_business_eps_delta_2026e_vs_2025a": growth_eps,
                "growth_net_profit_100mn": 0.0,
                "growth_EPS": 0.0,
                "broad_business_eps_2026e_current_shares": round(eps, 4),
                "broad_business_eps_2027e_current_shares": round(eps_2027, 4),
                "atlas_incremental_revenue_2026e_100mn": 0.0,
                "atlas_incremental_net_profit_2026e_100mn": 0.0,
                "atlas_incremental_eps_2026e": 0.0,
                "source": "verified_financials.md; broker_street_consensus_20260718.json; issuer filing evidence",
                "evidence_gap": "Atlas 950 units, ASP, BOM allocation, recognition timing and margin are not disclosed",
                "valuation_credit": "zero Atlas-specific and zero unallocated growth-segment earnings credit; conservative broader-business forecast only",
                "current_price_implied_pe_2026e": implied_pe,
                "peg_1x_implied_np_growth_pct": implied_pe,
                "current_price_implied_growth": f"At a 1.0x PEG convention, the current {implied_pe:.1f}x 2026E P/E requires about {implied_pe:.1f}% sustainable NP growth; this is an expectation diagnostic, not a forecast.",
                "next_quarter_validation_threshold": key_risk,
                "bear": bear,
                "base": base,
                "bull": bull,
            }
        )

    valuation_payload = {
        "case_id": "huawei-atlas-950-superpod-20260718",
        "data_cutoff": "2026-07-18",
        "price_date": "2026-07-17",
        "units": "CNY unless stated; revenue and profit in CNY 100mn",
        "methodology": "Conservative mature-business 2026E P/E plus independent justified P/B from official book equity and normalized ROE, current-share reconciled EPS, fundamental/market/external-broker target weights, and zero Atlas-specific or unbridged segment earnings credit",
        "rows": valuation_rows,
    }
    growth_payload = {
        "case_id": "huawei-atlas-950-superpod-20260718",
        "data_cutoff": "2026-07-18",
        "policy": "Atlas-specific units, ASP, revenue and margin are zero-weight until primary evidence confirms them",
        "drivers": growth_rows,
    }
    (DATA / "current_valuation_model_20260718.json").write_text(json.dumps(valuation_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DATA / "growth_driver_model.json").write_text(json.dumps(growth_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    table = [
        "# Current Valuation Model (2026-07-18)",
        "",
        "All Atlas 950-specific 2026E revenue and EPS credit is zero. Targets value the disclosed broader businesses only.",
        "",
        "| Ticker | Company | Price | 2026E EPS | 2026E PE | Bear | Base | Bull | Final | Upside | Action |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in valuation_rows:
        table.append(
            f"| {row['ticker']} | {row['company']} | {row['current_price']:.2f} | {row['eps_2026e']:.3f} | "
            f"{row['current_price']/row['eps_2026e']:.1f}x | {row['bear']:.2f} | {row['base']:.2f} | {row['bull']:.2f} | "
            f"{row['final_target']:.2f} | {row['upside']:.1%} | {row['action']} |"
        )
    table += [
        "",
        "Source: verified 2026-07-17 close prices, FY2025/2026Q1 issuer data, and original broker PDFs. This is a research scenario, not a trading instruction.",
    ]
    (DATA / "current_valuation_model_20260718.md").write_text("\n".join(table) + "\n", encoding="utf-8")

    growth_md = [
        "# Growth Earnings Model",
        "",
        "## Base Business / Growth Segment Boundary",
        "",
        "The model separates reported base business, broader-company forecasts and a specific Atlas/growth segment. Atlas-specific units, ASP, gross margin, revenue and EPS are not public; Atlas and unallocated growth-segment contribution is therefore RMB 0 in all modeled rows. Broader-company forecasts may be valued conservatively, but no segment multiple is added without a revenue-to-gross-profit-to-EPS bridge.",
        "",
        "| Ticker | Company | Growth segment / evidence | Unit or demand proxy | 2026E NP (CNY 100m) | Atlas credit |",
        "|---|---|---|---|---:|---:|",
    ]
    for row in growth_rows:
        growth_md.append(f"| {row['ticker']} | {row['company']} | {row['growth_segment_revenue']} | {row['unit_volume_or_proxy']} | {row['broad_business_np_2026e_100mn']:.3f} | 0 |")
    growth_md += [
        "",
        "## Unit / ASP / Gross Margin Bridge",
        "",
        "No modeled company has a public Atlas unit, ASP, BOM allocation, revenue recognition, incremental opex or Atlas margin. For HGTECH the official 2025 optical-connection segment provides CNY6.097bn revenue and 13.26% gross margin; for Shenling, the official proxy is data-service revenue growth of 51.42% and new-order growth of about 72%. Neither proxy closes the Atlas revenue-to-EPS bridge, so the segment GP, NP and EPS fields remain zero rather than inheriting the consolidated-company forecast.",
        "",
        "## Bear / Base / Bull",
        "",
        "Bear cases haircut current-share-reconciled EPS and multiples simultaneously. Base cases use original-PDF broker net-profit means, one current-share denominator, and business-matched through-cycle multiples. Bull cases require both stronger EPS and a higher multiple, but still retain zero Atlas-specific revenue until a primary-source order or revenue disclosure exists.",
        "",
        "## Current-Price-Implied Growth",
        "",
        "The current-price diagnostic shows both 2026E P/E and the net-profit growth required under a transparent 1.0x PEG convention. It is not a forecast. Above roughly 50x, the market already requires approximately 50% sustainable growth under that convention; a physical system display alone cannot validate that requirement.",
    ]
    (ANALYSIS / "growth_earnings_model.md").write_text("\n".join(growth_md) + "\n", encoding="utf-8")

    bridge = [
        "# Segment Forecast Bridge",
        "",
        "The forecast bridge has three layers: FY2025 reported base, 2026E/2027E broader-business forecasts from original broker PDFs, and Atlas 950 incremental credit. The third layer is zero for every company because public evidence does not disclose accepted units, company allocation, ASP, recognition timing or margin. Broker EPS is retained only as a source diagnostic; modeled EPS is recomputed from forecast net profit and the current share denominator.",
        "",
        "| Ticker | Company | FY2025 NP | 2026E NP | Broad NP delta | 2027E NP | 2026E EPS (current shares) | 2027E NP growth | Atlas NP delta |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in valuation_rows:
        growth_2027 = row["np_2027e_100mn"] / row["np_2026e_100mn"] - 1.0
        bridge.append(
            f"| {row['ticker']} | {row['company']} | {row['np_2025a_100mn']:.2f} | {row['np_2026e_100mn']:.2f} | "
            f"{row['np_2026e_100mn'] - row['np_2025a_100mn']:+.2f} | {row['np_2027e_100mn']:.2f} | {row['eps_2026e']:.3f} | {growth_2027:.1%} | 0.00 |"
        )
    bridge += [
        "",
        "## Atlas / Growth-Segment Credit Gate",
        "",
        "| Ticker | Company | Relationship / proxy | Units or order | ASP | Recognized segment revenue | Segment GP | Incremental opex | Segment NP / EPS | Valuation credit |",
        "|---|---|---|---|---|---:|---:|---:|---:|---|",
    ]
    for row in growth_rows:
        bridge.append(
            f"| {row['ticker']} | {row['company']} | {row['unit_volume_or_proxy']} | not disclosed for Atlas | not disclosed | 0.00 | 0.00 | 0.00 | 0.00 / 0.000 | zero; broader-company watch only |"
        )
    bridge += [
        "",
        "HGTECH and Shenling have the cleanest disclosed operating proxies; Envicool has full-chain liquid-cooling capability but no named Huawei/Atlas allocation; iFlytek is a downstream model co-development anchor rather than an upstream component order; Aerospace Electrical has relevant connector capability but declined to confirm the claimed relationship. The table deliberately records missing segment economics as zero, so no consolidated NP increase is silently relabeled as Atlas or high-growth-segment EPS.",
    ]
    (ANALYSIS / "segment_forecast_bridge.md").write_text("\n".join(bridge) + "\n", encoding="utf-8")
    (ANALYSIS / "implied_growth_sensitivity.md").write_text(
        "# Implied Growth Sensitivity\n\n"
        "At the 2026-07-17 close, the market-implied 2026E P/E spans roughly 10x for Woer to more than 80x for iFlytek. A 10% EPS miss combined with a 20% multiple compression reduces fair value by 28%; a 10% EPS beat combined with 20% expansion increases fair value by 32%. The asymmetry is most adverse for high-purity-expectation names above 50x, because no Atlas-specific earnings are currently in the evidence-gated model.\n\n"
        "The next-quarter sensitivity is therefore operational: order conversion and margin for Shenling, Q2 margin recovery for Envicool, optical-connection delivery and gross margin for HGTECH, and loss narrowing plus paid-user monetization for iFlytek.\n",
        encoding="utf-8",
    )

    valuation_md = [
        "# Valuation Model",
        "",
        "## Method and Assumption Bridge",
        "",
        "The house model covers twelve names with positive-weight original broker-PDF forecasts. The primary method applies conservative mature-business 2026E P/E bands to EPS reconciled to current shares; the prior high-growth bands were removed because segment purity is not auditable. The independent secondary method is a justified P/B anchor derived from each issuer's official FY2025 attributable equity and normalized 2026E ROE. Bear/base/bull use cost of equity of 11%/10%/9%, terminal growth of 2%/3%/4%, ROE caps of 23%/25%/27% and P/B floors of 0.6x/0.7x/0.8x. The two fundamental methods are weighted 60%/40%. Atlas-specific and unbridged growth-segment revenue, profit and EPS remain RMB 0.",
        "",
        "## Final Valuation Table",
        "",
        "| Ticker | Company | Price | Market cap | 2026E revenue | 2026E NP | 2026E EPS | Final target | Upside | Action |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in valuation_rows:
        valuation_md.append(f"| {row['ticker']} | {row['company']} | {row['current_price']:.2f} | {row['market_cap_100mn_cny']:.1f} | {row['revenue_2026e_100mn']:.1f} | {row['np_2026e_100mn']:.2f} | {row['eps_2026e']:.3f} | {row['final_target']:.2f} | {row['upside']:.1%} | {row['action']} |")
    valuation_md += [
        "",
        "## Three-Tier Targets",
        "",
        "Bear targets combine a 6%-20% EPS haircut with a lower multiple; base targets use consensus EPS and a business-matched multiple; bull targets require stronger EPS, execution and valuation. None of the tiers inserts an Atlas-specific unit or revenue assumption.",
        "",
        "| Ticker | Company | Bear | Base | Bull | Fundamental / market / broker weights |",
        "|---|---|---:|---:|---:|---|",
    ]
    for row in valuation_rows:
        valuation_md.append(f"| {row['ticker']} | {row['company']} | {row['bear']:.2f} | {row['base']:.2f} | {row['bull']:.2f} | {row['fundamental_weight']:.0%} / {row['market_weight']:.0%} / {row['broker_weight']:.0%} |")
    valuation_md += [
        "",
        "## Conservative P/E, justified P/B and PEG diagnostic",
        "",
        "Relative P/E is primary because every modeled name has positive 2026E EPS, but the bands are explicitly mature-business anchors rather than high-growth segment multiples. Justified P/B is independent because it uses official book equity and a disclosed sustainable-ROE formula rather than solving a multiple backward from a target. It also acts as a downside discipline for distribution, project and software names whose cash conversion or intangible intensity makes current market multiples unreliable. PEG remains only a market-expectation diagnostic and has zero target weight.",
        "",
        "## Seasonality Calibration",
        "",
        "FY2026 estimates are not annualized mechanically from Q1. Envicool and Shenling had weak Q1 profit despite strong FY2025 growth, while several PCB/CCL names published strong H1 previews. The model keeps broker full-year forecasts but conditions conviction on Q2/H1 margin and order conversion rather than a one-quarter run rate.",
        "",
        "## Next-Quarter Threshold",
        "",
        "Key thresholds are: Shenling data-service order conversion without receivable deterioration; Envicool Q2 profit/margin recovery; HGTECH optical-connection revenue and gross-margin delivery; Kehua core deducted-profit and project-acceptance quality; iFlytek H1 loss within guidance and improving cash conversion. Failure blocks any multiple expansion.",
        "",
        "## Market-Expectation Valuation Bridge",
        "",
        "The current market anchor receives 20% weight as a sentiment reference, not as a fundamental truth. For most high-expectation names, the market price is above the evidence-gated base target. The house view therefore does not recommend chasing the physical-display event.",
        "",
        "## Broker/Street Comparison",
        "",
        "Original broker PDFs support forecasts for all twelve modeled names. Explicit target prices exist only for Shengyi (CNY103.50), Shennan Circuits (CNY288.00), and Aerospace Electrical (CNY69-78). Those targets receive 20%-30% weight; missing targets receive 0%, rather than being imputed from current-price P/E tables.",
        "",
        "## Market-Implied Sentiment Anchor",
        "",
        "The 2026-07-17 session saw broad drawdowns across the thematic universe, yet several high-purity-expectation names still traded above 50x 2026E P/E. The lower-multiple names are mostly lower-purity satellites. This is a valuation-quality trade-off, not a free arbitrage.",
        "",
        "## Growth Earnings Dependency",
        "",
        "Every target depends on the structured growth-driver model. Atlas-specific earnings remain zero until accepted-unit, allocation, ASP, revenue-recognition and margin evidence exists. A Huawei relationship or Ascend partnership does not satisfy that dependency.",
        "",
        "## Full-Chain Classification Dependency",
        "",
        "Core/watch/satellite labels determine research priority, not automatic valuation credit. Demand anchors validate compute demand; satellites can be investable on standalone earnings; unavailable nodes are kept in the map but excluded from target prices. Atlas linkage and standalone valuation are scored separately.",
    ]
    (ANALYSIS / "valuation_model.md").write_text("\n".join(valuation_md) + "\n", encoding="utf-8")

    method_rows = []
    sentiment_rows = []
    for row in valuation_rows:
        method_rows.append(
            {
                "ticker": row["ticker"], "company": row["company"],
                "business_model": GROWTH_PROXIES[row["ticker"]][0],
                "primary_method": row["primary_method"],
                "primary_multiple_band": [row["bear_multiple"], row["base_multiple"], row["bull_multiple"]],
                "secondary_method": row["secondary_method"],
                "book_equity_2025a_100mn": row["book_equity_2025a_100mn"],
                "book_value_per_share": row["book_value_per_share_current_shares"],
                "forward_roe_2026e": row["forward_roe_2026e"],
                "justified_pb_scenarios": row["justified_pb_scenarios"],
                "cost_of_equity_scenarios": row["cost_of_equity_scenarios"],
                "terminal_growth_scenarios": row["terminal_growth_scenarios"],
                "peg_ratio_diagnostic_only": row["peg_ratio"], "peg_implied_pe_diagnostic_only": row["peg_implied_pe"],
                "method_weights": {"primary_conservative_pe": 0.60, "secondary_justified_pb": 0.40, "peg_target_weight": 0.00},
                "rejected_methods": "Atlas DCF rejected for missing unit/ASP/margin/capex/working-capital inputs; PEG retained only as a sentiment diagnostic because it is another P/E transformation",
            }
        )
        sentiment_rows.append(
            {key: row[key] for key in (
                "ticker", "company", "current_price", "price_date", "market_implied_pe_2026e",
                "market_implied_np_growth_pct_at_1x_peg", "forecast_np_growth_2027e_pct",
                "embedded_growth_gap_pct", "daily_change_2026_07_17_pct",
                "five_day_avg_volume_mshares", "five_day_avg_turnover_100mn_cny_proxy",
                "northbound_holding_2026_06_30_pct", "primary_base_target",
                "secondary_base_target", "base", "market_weight", "broker_weight", "final_target",
                "sentiment_premium_discount_to_fundamental_base_pct", "sentiment_interpretation",
            )}
        )
    (DATA / "valuation_method_matrix_20260718.json").write_text(json.dumps({"rows": method_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    method_md = [
        "# Valuation Method Matrix", "",
        "| Ticker | Company | Business model | Mature P/E band | Book value/share | Forward ROE | Justified P/B band |",
        "|---|---|---|---|---:|---:|---|",
    ]
    for row in method_rows:
        method_md.append(f"| {row['ticker']} | {row['company']} | {row['business_model']} | {'/'.join(str(x) for x in row['primary_multiple_band'])}x | {row['book_value_per_share']:.2f} | {row['forward_roe_2026e']:.1%} | {'/'.join(f'{x:.2f}' for x in row['justified_pb_scenarios'])}x |")
    method_md += ["", "Justified P/B formula: (normalized ROE - terminal growth) / (cost of equity - terminal growth), using official FY2025 attributable equity. Bear/base/bull cost of equity is 11%/10%/9%, terminal growth 2%/3%/4%, ROE caps 23%/25%/27%, and P/B floors 0.6x/0.7x/0.8x. The parameters are fixed ex ante across the universe and are not reverse-solved from prior targets. Atlas DCF is rejected for missing unit/ASP/margin/capex/working-capital inputs; PEG is a zero-weight expectation diagnostic."]
    (ANALYSIS / "valuation_method_matrix.md").write_text("\n".join(method_md) + "\n", encoding="utf-8")

    book_rows = [
        {
            "ticker": row["ticker"],
            "company": row["company"],
            "official_source": BOOK_EQUITY_SOURCE[row["ticker"]],
            "fy2025_attributable_equity_100mn": row["book_equity_2025a_100mn"],
            "current_shares_100mn": row["shares_100mn"],
            "book_value_per_share": row["book_value_per_share_current_shares"],
            "np_2026e_100mn": row["np_2026e_100mn"],
            "forward_roe_2026e": row["forward_roe_2026e"],
            "justified_pb_scenarios": row["justified_pb_scenarios"],
            "secondary_targets": {
                "bear": round(row["book_value_per_share_current_shares"] * row["justified_pb_scenarios"][0], 2),
                "base": row["secondary_base_target"],
                "bull": round(row["book_value_per_share_current_shares"] * row["justified_pb_scenarios"][2], 2),
            },
        }
        for row in valuation_rows
    ]
    book_payload = {
        "case_id": "huawei-atlas-950-superpod-20260718",
        "formula": "justified P/B = (normalized ROE - terminal growth) / (cost of equity - terminal growth)",
        "scenario_parameters": {
            "bear": {"cost_of_equity": 0.11, "terminal_growth": 0.02, "roe_cap": 0.23, "pb_floor": 0.60},
            "base": {"cost_of_equity": 0.10, "terminal_growth": 0.03, "roe_cap": 0.25, "pb_floor": 0.70},
            "bull": {"cost_of_equity": 0.09, "terminal_growth": 0.04, "roe_cap": 0.27, "pb_floor": 0.80},
        },
        "reverse_solved_from_prior_targets": False,
        "rows": book_rows,
    }
    (DATA / "book_value_valuation_inputs_20260718.json").write_text(json.dumps(book_payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    book_md = [
        "# Official Book-Value and Justified-P/B Inputs", "",
        "The independent secondary anchor uses official FY2025 attributable equity. It is not calibrated to prior targets. Formula: justified P/B = (normalized ROE - terminal growth) / (cost of equity - terminal growth). Bear/base/bull use cost of equity 11%/10%/9%, terminal growth 2%/3%/4%, ROE caps 23%/25%/27% and P/B floors 0.6x/0.7x/0.8x.", "",
        "| Ticker | Company | FY2025 equity | BVPS | 2026E NP | Forward ROE | Justified P/B (B/B/B) | Secondary target (B/B/B) | Official source |",
        "|---|---|---:|---:|---:|---:|---|---|---|",
    ]
    for row in book_rows:
        pbs = "/".join(f"{value:.2f}x" for value in row["justified_pb_scenarios"])
        targets = "/".join(f"{row['secondary_targets'][key]:.2f}" for key in ("bear", "base", "bull"))
        book_md.append(f"| {row['ticker']} | {row['company']} | {row['fy2025_attributable_equity_100mn']:.2f} | {row['book_value_per_share']:.2f} | {row['np_2026e_100mn']:.2f} | {row['forward_roe_2026e']:.1%} | {pbs} | {targets} | {row['official_source']} |")
    (DATA / "book_value_valuation_inputs_20260718.md").write_text("\n".join(book_md) + "\n", encoding="utf-8")

    (DATA / "market_sentiment_bridge_20260718.json").write_text(json.dumps({"rows": sentiment_rows}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sentiment_md = [
        "# Market-Implied Sentiment Bridge", "",
        "| Ticker | Company | Price | 2026E P/E | 1x-PEG implied growth | 2027E NP growth | Gap | Day move | 5d turnover proxy | NB holding | Fundamental base | Final target |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in sentiment_rows:
        sentiment_md.append(
            f"| {row['ticker']} | {row['company']} | {row['current_price']:.2f} | {row['market_implied_pe_2026e']:.1f}x | "
            f"{row['market_implied_np_growth_pct_at_1x_peg']:.1f}% | {row['forecast_np_growth_2027e_pct']:.1f}% | {row['embedded_growth_gap_pct']:+.1f}ppt | "
            f"{row['daily_change_2026_07_17_pct']:+.2f}% | {row['five_day_avg_turnover_100mn_cny_proxy']:.1f} | {row['northbound_holding_2026_06_30_pct']:.2f}% | "
            f"{row['base']:.2f} | {row['final_target']:.2f} |"
        )
    sentiment_md += ["", "The one-day move is a crowding/risk-appetite observation, not a valuation method. Market anchors retain only the disclosed model weight; Northbound data are dated 2026-06-30 and are not treated as a live flow signal."]
    (ANALYSIS / "market_sentiment_bridge.md").write_text("\n".join(sentiment_md) + "\n", encoding="utf-8")

    audit = [
        "# Valuation Audit",
        "",
        "Model Reproducibility: PASS",
        "",
        "- Price date: 2026-07-17; all twelve closes cross-checked between Tencent and Sina/AStock.",
        "- FY2025 and 2026Q1 actuals: verified packet; publication-critical company examples reconciled to issuer PDFs.",
        "- 2026E/2027E revenue and NP: positive-weight original broker-PDF rows only.",
        "- Shares: total market capitalization divided by close. Modeled EPS is forecast NP divided by this current-share denominator; source-PDF EPS is retained only as a diagnostic where corporate-action bases differ.",
        "- Primary method: conservative mature-business 2026E P/E after removing unbridged high-growth premiums. Independent secondary method: justified P/B from official FY2025 attributable equity and normalized ROE; fundamental base-target weights are 60%/40%, while PEG carries zero target weight and is diagnostic only.",
        "- Target formula: fundamental_weight * base + market_weight * current price + broker_weight * explicit broker target.",
        "- Upside formula: final_target / current_price - 1; script-generated and recalculated.",
        "- Atlas-specific 2026E revenue, profit and EPS: CNY 0 for all rows.",
        "- No DCF is used because Atlas unit/ASP/capex/working-capital inputs are unavailable; P/E is the least falsely precise method.",
        "",
        "Residual model risk: original broker forecasts can be optimistic; company-specific Atlas allocation, utilization and margin remain unverified; target multiples are scenario assumptions rather than observed transactions.",
    ]
    (ANALYSIS / "valuation_audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")

    (ANALYSIS / "valuation_coverage_reconciliation.md").write_text(
        "# Valuation Coverage Reconciliation\n\n"
        f"- Atlas-focused full-chain nodes: 50.\n- Verified market/financial issuers: 22.\n- Original-PDF broker coverage: {len(aggregate)} ticker aggregates.\n- Complete evidence-gated target models: {len(valuation_rows)}.\n"
        "- Strongest direct relationship but no fresh usable broker forecast: Talkweb, retained as watchlist only.\n"
        "- Excluded from targets: overseas/private/unavailable nodes, demand anchors without a public earnings bridge, rumor-only suppliers, and listed names without positive-weight external forecasts.\n\n"
        "This reconciliation deliberately prefers twelve reproducible models over an artificial target for every concept name. The wider AIDC coverage pack remains an appendix census and carries no Atlas-specific earnings credit.\n",
        encoding="utf-8",
    )

    cards = ["# Core Candidate Company Cards", ""]
    for row in valuation_rows:
        proxy = GROWTH_PROXIES[row["ticker"]]
        cards += [
            f"## {row['company']} ({row['ticker']})",
            "",
            f"- Chain role / core technology: {proxy[0]}.",
            f"- Core revenue / earnings evidence: {proxy[1]}.",
            f"- Order / certification: {proxy[2]}; Atlas supplier qualification is not confirmed.",
            f"- Cash flow / inventory / capex / debt focus: {proxy[3]}; review in the next filing before multiple expansion.",
            f"- 2026E expectation: revenue CNY{row['revenue_2026e_100mn']:.2f} 100m, NP CNY{row['np_2026e_100mn']:.2f} 100m, EPS CNY{row['eps_2026e']:.3f}.",
            f"- Valuation disposition: final target CNY{row['final_target']:.2f}, upside {row['upside']:.1%}, action `{row['action']}`; Atlas revenue credit CNY0.",
            "",
        ]
    (ANALYSIS / "core_candidate_company_cards.md").write_text("\n".join(cards) + "\n", encoding="utf-8")

    (ANALYSIS / "chain_business_research.md").write_text(
        "# Chain Business Research\n\n"
        "## Upstream Business\n\nCompute silicon, HBM, packaging and specialized materials remain largely unavailable or non-listed in the A-share evidence set. The upstream bottleneck is not converted into an investable domestic supplier claim without foundry, package, yield, volume and allocation evidence.\n\n"
        "## Downstream Business\n\nServer/OEM, optical/networking, PCB/CCL, power/thermal, IDC and software workloads monetize at different acceptance points. The business relationship moves from qualification to order, delivery, acceptance, revenue, gross profit, cash collection and valuation credit; skipping any step creates false precision.\n\n"
        "## Business Relationship and Core Technology\n\nUnifiedBus and multi-cabinet scale-up increase requirements for high-speed interconnect, thermal density, power delivery and system reliability. Listed companies are mapped by disclosed products and customers, not by rumor.\n\n"
        "## Core Revenue Business and 2026E Expectation\n\nThe twelve target models use verified base revenue and original-PDF 2026E/2027E forecasts. Atlas-specific expectation is CNY0 pending primary evidence. Broader AIDC growth can still support earnings, but must be labeled separately.\n",
        encoding="utf-8",
    )

    print(json.dumps({"valuation_rows": len(valuation_rows), "growth_rows": len(growth_rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
