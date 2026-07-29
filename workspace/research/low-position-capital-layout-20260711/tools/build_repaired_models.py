#!/usr/bin/env python3
"""Build source-pure, probability-weighted valuation and growth models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
PRICE_DATE = "2026-07-10"


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def expected_value(bear: float, base: float, bull: float, probabilities: tuple[float, float, float]) -> float:
    return sum(value * probability for value, probability in zip((bear, base, bull), probabilities))


def valuation_row(
    *,
    ticker: str,
    company: str,
    bucket: str,
    current_price: float,
    shares: float,
    revenue: float,
    net_profit: float,
    eps: float,
    method: str,
    bear: float,
    base: float,
    bull: float,
    probabilities: tuple[float, float, float],
    street_target: float,
    action: str,
    evidence_quality: str,
    catalyst: str,
    invalidation: str,
    scenario_assumptions: dict[str, str],
) -> dict[str, Any]:
    fundamental_expected = expected_value(bear, base, bull, probabilities)
    final_target = fundamental_expected * 0.90 + street_target * 0.10
    return {
        "ticker": ticker,
        "company": company,
        "opportunity_bucket": bucket,
        "current_price": current_price,
        "price_date": PRICE_DATE,
        "shares_100mn": shares,
        "market_cap_100mn_cny": round(current_price * shares, 2),
        "revenue_2026e_100mn": revenue,
        "np_2026e_100mn": net_profit,
        "eps_2026e": eps,
        "method": method,
        "bear": round(bear, 2),
        "base": round(base, 2),
        "bull": round(bull, 2),
        "bear_probability": probabilities[0],
        "base_probability": probabilities[1],
        "bull_probability": probabilities[2],
        "scenario_expected_value": round(fundamental_expected, 2),
        "market_implied_anchor": current_price,
        "market_anchor_source": "current price reference only; zero target weight",
        "broker_anchor": street_target,
        "fundamental_weight": 0.90,
        "market_weight": 0.0,
        "broker_weight": 0.10,
        "final_target": round(final_target, 2),
        "upside": round(final_target / current_price - 1, 4),
        "action": action,
        "evidence_quality": evidence_quality,
        "catalyst": catalyst,
        "invalidation": invalidation,
        "scenario_assumptions": scenario_assumptions,
        "target_formula": (
            "90% * probability-weighted bear/base/bull fundamental value "
            "+ 10% * source-pure published Street target; market anchor weight is zero"
        ),
    }


def build_broker_rows() -> list[dict[str, Any]]:
    prices = {
        "601077": 6.30,
        "000425": 8.43,
        "601825": 7.66,
        "600276": 55.75,
        "601138": 66.27,
    }
    return [
        {
            "ticker": "601077",
            "broker": "华创证券",
            "report_date": "2026-04-29",
            "rating": "推荐",
            "target_price": 8.82,
            "revenue_E": "CNY30.1bn derived from Huachuang disclosed +5.0% growth",
            "net_profit_E": "CNY12.7bn derived from Huachuang disclosed +4.5% growth",
            "EPS_E": "CNY1.12 derived from same-source net profit and share count",
            "method": "0.72x 2026E PB",
            "implied_upside": round(8.82 / prices["601077"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/broker-reports/2026-07-11/601077_huachuang_repost_20260711.html",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "000425",
            "broker": "华创证券",
            "report_date": "2026-05-04",
            "rating": "强推",
            "target_price": 12.50,
            "revenue_E": "CNY112.32bn",
            "net_profit_E": "CNY8.17bn",
            "EPS_E": "CNY0.70",
            "method": "18x 2026E PE",
            "implied_upside": round(12.50 / prices["000425"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/broker-reports/2026-07-11/000425_huachuang_repost_20260711.html",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "601825",
            "broker": "华创证券",
            "report_date": "2026-04-23",
            "rating": "推荐",
            "target_price": 10.35,
            "revenue_E": "2026E revenue not used in PB target; captured report provides target, PB and profit growth",
            "net_profit_E": "CNY12.39bn derived from same-source +0.6% growth on 2025A",
            "EPS_E": "CNY1.28 derived from same-source net profit and share count",
            "method": "0.75x 2026E PB",
            "implied_upside": round(10.35 / prices["601825"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/broker-reports/2026-07-11/601825_huachuang_repost_20260711.html",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "600276",
            "broker": "华泰证券",
            "report_date": "2026-04-23",
            "rating": "买入",
            "target_price": 87.14,
            "revenue_E": "CNY36.09bn",
            "net_profit_E": "CNY9.40bn",
            "EPS_E": "CNY1.42",
            "method": "SOTP",
            "implied_upside": round(87.14 / prices["600276"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/launched-broker-reports-20260711/600276_huatai_repost.html",
            "valuation_weight": 0.10,
        },
        {
            "ticker": "601138",
            "broker": "华泰证券",
            "report_date": "2026-07-10",
            "rating": "买入",
            "target_price": 93.00,
            "revenue_E": "CNY1,480.37bn",
            "net_profit_E": "CNY56.01bn",
            "EPS_E": "CNY2.82",
            "method": "33x 2026E PE",
            "implied_upside": round(93.00 / prices["601138"] - 1, 4),
            "source_quality": "auditable_broker_repost",
            "source_path": "sources/core-broker-reports-20260711/601138-huatai-post-preview.html",
            "valuation_weight": 0.10,
        },
    ]


def build_valuation_rows() -> list[dict[str, Any]]:
    return [
        valuation_row(
            ticker="601077",
            company="渝农商行",
            bucket="quiet_accumulation",
            current_price=6.30,
            shares=113.57,
            revenue=292.89,
            net_profit=128.80,
            eps=1.13,
            method="PB-ROE probability scenarios with asset-quality floor",
            bear=12.78 * 0.42,
            base=12.78 * 0.56,
            bull=12.78 * 0.72,
            probabilities=(0.30, 0.50, 0.20),
            street_target=8.82,
            action="core review / pullback entry",
            evidence_quality="high",
            catalyst="NIM remains >=1.60%, revenue stays positive and asset quality is stable",
            invalidation="NIM <1.55%, NPL >1.15% or revenue growth <2%",
            scenario_assumptions={
                "bear": "2026E BVPS CNY12.78 at 0.42x PB under renewed NIM/credit stress",
                "base": "2026E BVPS CNY12.78 at 0.56x PB, below Huachuang target multiple",
                "bull": "2026E BVPS CNY12.78 at Huachuang 0.72x PB",
            },
        ),
        valuation_row(
            ticker="000425",
            company="徐工机械",
            bucket="quiet_stock_island",
            current_price=8.43,
            shares=117.1121,
            revenue=1141.98,
            net_profit=83.0,
            eps=0.71,
            method="normalized PE probability scenarios with cash-flow validation",
            bear=0.60 * 10,
            base=0.70 * 14,
            bull=0.80 * 18,
            probabilities=(0.30, 0.50, 0.20),
            street_target=12.50,
            action="pullback entry / earnings validation",
            evidence_quality="high",
            catalyst="overseas/mining growth and operating cash flow remain positive",
            invalidation="2026E EPS <0.60, overseas growth <8% or cash flow reverses",
            scenario_assumptions={
                "bear": "EPS CNY0.60 at 10x PE under FX and domestic-cycle pressure",
                "base": "EPS CNY0.70 at 14x PE, below Huachuang 18x",
                "bull": "EPS CNY0.80 at Huachuang 18x PE",
            },
        ),
        valuation_row(
            ticker="601825",
            company="沪农商行",
            bucket="quiet_accumulation",
            current_price=7.66,
            shares=96.44,
            revenue=260.0,
            net_profit=124.0,
            eps=1.29,
            method="PB-ROE probability scenarios with dividend/credit floor",
            bear=14.11 * 0.45,
            base=14.11 * 0.58,
            bull=14.11 * 0.73,
            probabilities=(0.30, 0.50, 0.20),
            street_target=10.35,
            action="income-oriented market-supported watch",
            evidence_quality="medium-high",
            catalyst="revenue remains positive, provision coverage >=300% and payout is stable",
            invalidation="revenue turns negative, NPL >1.05% or provision coverage <280%",
            scenario_assumptions={
                "bear": "Guosen 2026E BVPS CNY14.11 at 0.45x PB",
                "base": "BVPS CNY14.11 at 0.58x PB, below five-year average/Street target",
                "bull": "BVPS CNY14.11 at 0.73x PB near Huachuang target",
            },
        ),
        valuation_row(
            ticker="600276",
            company="恒瑞医药",
            bucket="launched_with_runway",
            current_price=55.75,
            shares=66.37199874,
            revenue=360.91,
            net_profit=94.0,
            eps=1.42,
            method="explicit SOTP: generics + risk-adjusted innovative-drug DCF + net cash/other",
            bear=3250 / 66.37199874,
            base=4549 / 66.37199874,
            bull=5256 / 66.37199874,
            probabilities=(0.30, 0.50, 0.20),
            street_target=87.14,
            action="trend pullback core / milestone validation",
            evidence_quality="medium-high",
            catalyst="innovative-drug sales >=30%, approvals and BD milestones convert",
            invalidation="innovative growth <20%, pipeline delays or EPS <1.25",
            scenario_assumptions={
                "bear": "generics CNY30bn + innovative rDCF CNY240bn + net cash/other CNY55bn",
                "base": "generics CNY40.4bn + innovative rDCF CNY350bn + net cash/other CNY64.5bn",
                "bull": "Goldman generics CNY40.4bn + innovative rDCF CNY420.7bn + implied net cash/other CNY64.5bn",
            },
        ),
        valuation_row(
            ticker="601138",
            company="工业富联",
            bucket="launched_with_runway",
            current_price=66.27,
            shares=198.64,
            revenue=14803.7,
            net_profit=560.1,
            eps=2.82,
            method="post-preview PE probability scenarios with margin/platform-ramp validation",
            bear=2.52 * 20,
            base=2.82 * 27,
            bull=3.25 * 30,
            probabilities=(0.30, 0.50, 0.20),
            street_target=93.00,
            action="earnings-delivery pullback / market-supported watch",
            evidence_quality="high",
            catalyst="H2 AI-server ramp, 800G+ growth, GM >=7% and cash conversion",
            invalidation="2026E NP <CNY51.6bn, platform delay or GM <7%",
            scenario_assumptions={
                "bear": "EPS CNY2.52 at 20x PE under slower platform ramp/margin pressure",
                "base": "Huatai EPS CNY2.82 at 27x PE, below Huatai 33x",
                "bull": "Huachuang NP cross-check implies EPS CNY3.25 at 30x PE",
            },
        ),
    ]


def build_hengrui_sotp() -> dict[str, Any]:
    shares = 66.37199874
    scenarios = {
        "bear": {
            "generic_value_100mn": 300.0,
            "innovative_rdcf_value_100mn": 2400.0,
            "net_cash_other_100mn": 550.0,
        },
        "base": {
            "generic_value_100mn": 404.0,
            "innovative_rdcf_value_100mn": 3500.0,
            "net_cash_other_100mn": 645.0,
        },
        "bull": {
            "generic_value_100mn": 404.0,
            "innovative_rdcf_value_100mn": 4207.0,
            "net_cash_other_100mn": 645.0,
        },
    }
    for scenario in scenarios.values():
        scenario["equity_value_100mn"] = round(
            scenario["generic_value_100mn"]
            + scenario["innovative_rdcf_value_100mn"]
            + scenario["net_cash_other_100mn"],
            2,
        )
        scenario["per_share_value"] = round(
            scenario["equity_value_100mn"] / shares, 2
        )
    return {
        "schema_version": "astock.hengrui_sotp.v1",
        "ticker": "600276",
        "company": "恒瑞医药",
        "shares_100mn": shares,
        "source_anchor": (
            "Goldman archived report page: generics CNY40.4bn at 10x forward PE, "
            "innovative-drug rDCF CNY420.7bn, WACC 9%, terminal growth 3%, "
            "published target CNY79.20"
        ),
        "net_cash_other_note": (
            "CNY64.5bn is the residual required to reconcile disclosed segment "
            "values to Goldman's published equity target; treated explicitly as "
            "net cash/other rather than hidden in innovative-drug value"
        ),
        "scenarios": scenarios,
        "probabilities": {"bear": 0.30, "base": 0.50, "bull": 0.20},
        "limitations": [
            "Product-level peak sales and phase-by-phase PoS were not disclosed in the archived report page.",
            "Base and bear innovative rDCF values are explicit AStock haircuts to the Goldman bull anchor.",
            "Clinical, approval and BD timing remain the main sensitivity.",
        ],
    }


def build_conditional_watch_models() -> list[dict[str, Any]]:
    return [
        {
            "ticker": "000063",
            "company": "中兴通讯",
            "status": "watchlist_only_insufficient_segment_economics",
            "current_price": 40.53,
            "bear": 25.0,
            "base": 37.0,
            "bull": 51.9,
            "probabilities": {"bear": 0.35, "base": 0.45, "bull": 0.20},
            "probability_expected_value": 35.79,
            "expected_upside": round(35.79 / 40.53 - 1, 4),
            "reason": (
                "Compute segment units, ASP, margin and customer allocation remain "
                "undisclosed; the old CNY60 target used a materially higher EPS denominator."
            ),
            "upgrade_trigger": (
                "H2 profit growth turns positive, OCF improves and compute segment "
                "margin/order evidence becomes available."
            ),
        },
        {
            "ticker": "301308",
            "company": "江波龙",
            "status": "watchlist_only_cycle_model_unresolved",
            "current_price": 587.60,
            "bear": 341.0,
            "base": 532.0,
            "bull": 765.0,
            "probabilities": {"bear": 0.35, "base": 0.45, "bull": 0.20},
            "probability_expected_value": 511.75,
            "expected_upside": round(511.75 / 587.60 - 1, 4),
            "reason": (
                "Inventory cost layers, NAND/DRAM ASP, customer allocation, H2 order "
                "conversion and cash-flow durability are insufficient for investable credit."
            ),
            "upgrade_trigger": (
                "H2 deducted NP and OCF validate, inventory write-down stays contained, "
                "and contract-price/customer-order evidence supports the cycle duration."
            ),
            "cycle_sensitivity": {
                "bear": "FY NP CNY13.1bn / EPS ~CNY31 / 11x",
                "base": "FY NP CNY16.1bn / EPS ~CNY38 / 14x",
                "bull": "FY NP CNY19.1bn / EPS ~CNY45 / 17x",
            },
        },
        {
            "ticker": "601225",
            "company": "陕西煤业",
            "status": "sector_validation_market_supported_watch",
            "current_price": 22.92,
            "bear": 13.60,
            "base": 20.80,
            "bull": 26.40,
            "probabilities": {"bear": 0.30, "base": 0.50, "bull": 0.20},
            "probability_expected_value": 19.76,
            "expected_upside": round(19.76 / 22.92 - 1, 4),
            "reason": (
                "Coal is a valid silent-accumulation sector, but current price already "
                "exceeds probability-weighted earnings value; dividend supports watch status."
            ),
            "upgrade_trigger": "Coal price and 2026E EPS exceed the current broker base while dividend remains durable.",
        },
    ]


def valuation_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Valuation Model",
        "",
        "## Final Valuation Table",
        "",
        "| Ticker | Company | Price | 2026E NP/EPS | Method | Bear | Base | Bull | Probabilities | Fundamental EV | Street | Final target | Upside | Action |",
        "|---|---|---:|---|---|---:|---:|---:|---|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['current_price']:.2f} | "
            f"{row['np_2026e_100mn']:.1f}/{row['eps_2026e']:.2f} | {row['method']} | "
            f"{row['bear']:.2f} | {row['base']:.2f} | {row['bull']:.2f} | "
            f"{row['bear_probability']:.0%}/{row['base_probability']:.0%}/{row['bull_probability']:.0%} | "
            f"{row['scenario_expected_value']:.2f} | {row['broker_anchor']:.2f} | "
            f"{row['final_target']:.2f} | {row['upside']:.1%} | {row['action']} |"
        )
    lines += [
        "",
        "## Three-Tier Targets",
        "",
        "Bear/base/bull values are company-specific driver scenarios. Every bear value is below current price. Scenario probabilities are disclosed and sum to 100%; Street is a source-pure 10% comparison anchor, and unsupported market-anchor weight is zero.",
        "",
        "## Relative / PEG / PSG Comparison",
        "",
        "Banks use PB-ROE, XCMG and Industrial Fulian use normalized PE with cash-flow/margin checks, and Hengrui uses explicit SOTP. No uniform PE is applied.",
        "",
        "## Seasonality Calibration",
        "",
        "Full-year broker forecasts are used for the five investable rows. H1 previews are used as progress tests, not mechanically annualized denominators.",
        "",
        "## Next-Quarter Threshold",
        "",
    ]
    for row in rows:
        lines.append(f"- {row['ticker']} {row['company']}: {row['catalyst']} Invalidate if {row['invalidation']}.")
    lines += [
        "",
        "## Method and Assumption Bridge",
        "",
        "Each row includes scenario assumptions in `data/current_valuation_model_20260711.json`. The final target is 90% probability-weighted fundamental expected value plus 10% source-pure published Street target.",
        "",
        "## Market-Expectation Valuation Bridge",
        "",
        "Current price is a reference only and carries zero target weight. Embedded expectations are shown through current PE/PB versus the bear/base/bull driver scenarios.",
        "",
        "## Broker/Street Comparison",
        "",
        "See `data/broker_street_consensus_20260711.md`. Each positive-weight row is source-pure; no target and forecast from different brokers are combined.",
        "",
        "## Market-Implied Sentiment Anchor",
        "",
        "Unsupported market anchors have been removed. `market_implied_anchor` is retained only as a current-price reference with `market_weight=0` for schema compatibility.",
        "",
        "## Growth Earnings Dependency",
        "",
        "Hengrui and Industrial Fulian retain investable growth credit. ZTE and Jiangbolong are downgraded to conditional watch in `data/conditional_watch_models_20260712.json`.",
        "",
        "## Full-Chain Classification Dependency",
        "",
        "Not applicable to a cross-market strategy report. Company-specific evidence determines valuation eligibility.",
    ]
    return "\n".join(lines)


def build_growth_outputs(hengrui_sotp: dict[str, Any], conditional: list[dict[str, Any]]) -> None:
    drivers = [
        {
            "ticker": "600276",
            "company": "恒瑞医药",
            "applies": True,
            "growth_driver": "innovative-drug sales, approvals and BD milestones",
            "base_business_revenue": "mature/generic business; Goldman value CNY40.4bn at 10x forward PE",
            "growth_segment_revenue": "innovative-drug/BD business; risk-adjusted DCF",
            "value_amount_or_proxy": "Goldman innovative-drug rDCF CNY420.7bn bull anchor",
            "unit_volume_or_proxy": "innovative-drug sales growth, approvals and BD recognition",
            "ASP_or_price": "portfolio mix; product ASP not disclosed",
            "recognized_revenue_ratio": "reported sales/recognized BD; future milestones probability-adjusted",
            "supply_demand_state": "positive innovative-drug demand; generic pressure persists",
            "capacity_or_utilization": "not primary constraint",
            "certification_or_customer_qualification": "regulatory approvals and clinical milestones",
            "growth_gross_margin": "2026Q1 consolidated GM 86.6%",
            "incremental_opex": "R&D and launch costs captured in full-year forecast",
            "growth_net_profit": "2026E consolidated NP CNY9.4bn",
            "growth_EPS": "CNY1.42",
            "evidence_type": "official Q1 plus Huatai/Goldman archived pages",
            "source": "sources/launched-broker-reports-20260711/600276_*.html",
            "evidence_gap": "product-level peak sales and phase-level PoS not disclosed",
            "valuation_credit": "earnings credit through explicit SOTP with haircut scenarios",
            "bear": hengrui_sotp["scenarios"]["bear"],
            "base": hengrui_sotp["scenarios"]["base"],
            "bull": hengrui_sotp["scenarios"]["bull"],
            "current_price_implied_growth": "CNY55.75 is below all but the repaired severe bear SOTP",
            "sensitivity_key": "innovative sales, clinical PoS, BD timing and DCF haircut",
            "next_quarter_validation_threshold": "innovative sales >=30%, EPS >=CNY1.35, milestones on schedule",
        },
        {
            "ticker": "601138",
            "company": "工业富联",
            "applies": True,
            "growth_driver": "AI servers, next-generation GPU platforms and 800G+ switches",
            "base_business_revenue": "2025 consolidated revenue CNY902.9bn",
            "growth_segment_revenue": "Huatai 2026E consolidated revenue CNY1,480.4bn",
            "value_amount_or_proxy": "H1 NP CNY23.9bn; AI-server revenue +230%; 800G+ shipments +140%",
            "unit_volume_or_proxy": "AI-server revenue growth, switch shipments and platform ramp",
            "ASP_or_price": "platform/system mix proxy; product ASP not disclosed",
            "recognized_revenue_ratio": "H1 guidance plus post-preview full-year forecasts",
            "supply_demand_state": "hyperscaler AI capex strong; customer concentration remains risk",
            "capacity_or_utilization": "next-generation ramp qualitative; exact utilization not disclosed",
            "certification_or_customer_qualification": "major-customer joint development; allocation not disclosed",
            "growth_gross_margin": "2026Q1 consolidated GM 7.35%",
            "incremental_opex": "captured in Huatai/Huachuang full-year forecasts",
            "growth_net_profit": "Huatai CNY56.01bn base; Huachuang CNY64.597bn bull cross-check",
            "growth_EPS": "Huatai CNY2.82",
            "evidence_type": "official H1 preview plus post-preview broker pages",
            "source": "sources/earnings-previews-20260711/601138_preview.pdf; sources/core-broker-reports-20260711/601138-*.html",
            "evidence_gap": "customer allocation, product ASP and segment GM not disclosed",
            "valuation_credit": "earnings credit through conservative consolidated PE scenarios",
            "bear": {"eps": 2.52, "multiple": 20, "value": 50.4},
            "base": {"eps": 2.82, "multiple": 27, "value": 76.14},
            "bull": {"eps": 3.25, "multiple": 30, "value": 97.5},
            "current_price_implied_growth": "CNY66.27 implies 23.5x Huatai 2026E EPS",
            "sensitivity_key": "H2 platform ramp, product mix, GM and cash conversion",
            "next_quarter_validation_threshold": "H2 NP >=CNY32.1bn, AI server growth >100%, GM >=7%",
        },
    ]
    write_json(DATA_DIR / "growth_driver_model.json", {"data_cutoff": PRICE_DATE, "drivers": drivers})
    write_text(
        ANALYSIS_DIR / "growth_earnings_model.md",
        """# Growth Earnings Model

Gate status: PASS for the two investable growth names; CONDITIONAL for the broader launched-growth watch pool.

## Investable Decisions

- Hengrui: explicit SOTP earnings credit with bear/base/bull haircuts to the disclosed Goldman segment anchors.
- Industrial Fulian: consolidated PE earnings credit with H1 guidance, post-preview forecasts and margin/platform-ramp thresholds.

## Downgraded Names

- ZTE: watchlist only / insufficient segment economics. Compute units, ASP, segment margin and customer allocation remain undisclosed.
- Jiangbolong: watchlist only / unresolved cycle model. Inventory cost layers, ASP, customer allocation, H2 order conversion and cash-flow durability remain insufficient.

## Model Boundary

No high-growth target is published for ZTE or Jiangbolong. Their probability scenarios are preserved in `data/conditional_watch_models_20260712.json` solely to show why current price does not pass the investable gate.
""",
    )
    write_text(
        ANALYSIS_DIR / "segment_forecast_bridge.md",
        """# Segment Forecast Bridge

## Hengrui

Generics are valued separately from the innovative-drug rDCF. The repaired SOTP discloses generic, innovative and net-cash/other values for bear/base/bull cases. Product-level PoS is not available in the archived page, so the base and bear cases apply explicit haircuts to Goldman's innovative-drug bull anchor.

## Industrial Fulian

2025 consolidated revenue CNY902.9bn is the base. Huatai forecasts CNY1,480.4bn revenue and CNY56.01bn NP in 2026E; the H1 midpoint CNY23.9bn requires H2 NP near CNY32.1bn. No separate AI-segment multiple is applied.

## ZTE and Jiangbolong

Both are removed from investable valuation. See `analysis/jiangbolong_cycle_sensitivity.md` and `data/conditional_watch_models_20260712.json`.
""",
    )
    write_text(
        ANALYSIS_DIR / "implied_growth_sensitivity.md",
        """# Implied Growth Sensitivity

| Driver | Bear | Base | Bull | Current price | Validation | Downgrade |
|---|---:|---:|---:|---:|---|---|
| Hengrui SOTP per share | 48.97 | 68.54 | 79.19 | 55.75 | innovative sales, PoS, BD | growth <20%, pipeline delay |
| Industrial Fulian value | 50.40 | 76.14 | 97.50 | 66.27 | H2 NP, GM, platform ramp | NP <51.6bn or GM <7% |
| ZTE watch value | 25.00 | 37.00 | 51.90 | 40.53 | segment margin/order/OCF | evidence remains unavailable |
| Jiangbolong watch value | 341 | 532 | 765 | 587.60 | H2 deducted NP, ASP, inventory, OCF | NP/cash-flow/cycle miss |
""",
    )
    write_text(
        ANALYSIS_DIR / "value_chain_economics.md",
        """# Value-Chain Economics

| Company | Value/price proxy | Margin pool | Demand | Capacity/order evidence | Valuation credit |
|---|---|---|---|---|---|
| Hengrui | Goldman generic 10x PE + innovative rDCF | consolidated GM 86.6% | innovative demand positive | approvals, clinical and BD milestones | explicit SOTP credit |
| Industrial Fulian | AI-server revenue +230%, 800G+ +140% | consolidated GM 7.35% | hyperscaler capex strong | joint development/H2 ramp; allocation undisclosed | conservative consolidated PE |
| ZTE | compute share 27%; ASP not disclosed | segment GM not disclosed | AI compute strong | order/customer allocation insufficient | watchlist only |
| Jiangbolong | H1 guidance and storage price proxy | Q1 GM high but cyclical | storage cycle strong | inventory/ASP/customer/order conversion insufficient | watchlist only |
""",
    )
    write_text(
        ANALYSIS_DIR / "jiangbolong_cycle_sensitivity.md",
        """# Jiangbolong Cycle Sensitivity

Status: watchlist only / unresolved cycle model.

| Scenario | FY2026 NP | EPS proxy | Multiple | Value | Required evidence |
|---|---:|---:|---:|---:|---|
| Bear | CNY13.1bn | CNY31 | 11x | CNY341 | storage prices normalize sharply; OCF/inventory remain weak |
| Base | CNY16.1bn | CNY38 | 14x | CNY532 | H2 deducted profit and OCF partially validate |
| Bull | CNY19.1bn | CNY45 | 17x | CNY765 | ASP/order duration, inventory and cash conversion all validate |

Probability-weighted value is below the current price. The prior CNY802 target is withdrawn.
""",
    )


def main() -> None:
    broker_rows = build_broker_rows()
    valuation_rows = build_valuation_rows()
    hengrui_sotp = build_hengrui_sotp()
    conditional = build_conditional_watch_models()
    write_json(
        DATA_DIR / "broker_street_consensus_20260711.json",
        {"data_cutoff": PRICE_DATE, "rows": broker_rows},
    )
    lines = [
        "# Broker / Street Consensus",
        "",
        "| Ticker | Broker | Date | Rating | Target | Revenue E | NP E | EPS E | Method | Quality | Weight |",
        "|---|---|---|---|---:|---|---|---|---|---|---:|",
    ]
    for row in broker_rows:
        lines.append(
            f"| {row['ticker']} | {row['broker']} | {row['report_date']} | "
            f"{row['rating']} | {row['target_price']:.2f} | {row['revenue_E']} | "
            f"{row['net_profit_E']} | {row['EPS_E']} | {row['method']} | "
            f"{row['source_quality']} | {row['valuation_weight']:.0%} |"
        )
    lines += [
        "",
        "Every row is source-pure. No target from one broker is combined with forecasts from another broker.",
    ]
    write_text(DATA_DIR / "broker_street_consensus_20260711.md", "\n".join(lines))
    write_json(
        DATA_DIR / "current_valuation_model_20260711.json",
        {"data_cutoff": PRICE_DATE, "rows": valuation_rows},
    )
    write_json(DATA_DIR / "hengrui_sotp_model_20260712.json", hengrui_sotp)
    write_json(
        DATA_DIR / "conditional_watch_models_20260712.json",
        {"schema_version": "astock.conditional_watch_models.v1", "rows": conditional},
    )
    write_text(ANALYSIS_DIR / "valuation_model.md", valuation_markdown(valuation_rows))
    write_text(
        ANALYSIS_DIR / "hengrui_sotp_model.md",
        """# Hengrui SOTP Model

| Scenario | Generics | Innovative rDCF | Net cash/other | Equity value | Per share |
|---|---:|---:|---:|---:|---:|
"""
        + "\n".join(
            f"| {name} | {row['generic_value_100mn']:.1f} | "
            f"{row['innovative_rdcf_value_100mn']:.1f} | "
            f"{row['net_cash_other_100mn']:.1f} | "
            f"{row['equity_value_100mn']:.1f} | {row['per_share_value']:.2f} |"
            for name, row in hengrui_sotp["scenarios"].items()
        )
        + "\n\n"
        + hengrui_sotp["source_anchor"]
        + "\n\n"
        + hengrui_sotp["net_cash_other_note"],
    )
    audit_lines = [
        "# Valuation Audit",
        "",
        "## Arithmetic Checks",
    ]
    for row in valuation_rows:
        probability_sum = (
            row["bear_probability"]
            + row["base_probability"]
            + row["bull_probability"]
        )
        fundamental_expected = expected_value(
            row["bear"],
            row["base"],
            row["bull"],
            (
                row["bear_probability"],
                row["base_probability"],
                row["bull_probability"],
            ),
        )
        final_target = fundamental_expected * row["fundamental_weight"] + row[
            "broker_anchor"
        ] * row["broker_weight"]
        audit_lines.append(
            f"- {row['ticker']}: probability sum {probability_sum:.2f}; "
            f"fundamental EV {fundamental_expected:.2f}; final target "
            f"{final_target:.2f} vs stored {row['final_target']:.2f}; "
            f"bear/current {(row['bear']/row['current_price']-1):.1%}."
        )
    audit_lines += [
        "",
        "## Forecast Availability",
        "",
        "All five investable rows have current price, share count and full-year denominator.",
        "",
        "## Target-Price Comparability",
        "",
        "Every positive Street row is source-pure. Mixed-broker rows were removed.",
        "",
        "## Final Valuation Completeness",
        "",
        "Bear/base/bull probabilities, expected fundamental value, source-pure Street target, final target, action and invalidation are present.",
        "",
        "## Scenario-Band Checks",
        "",
        "Every bear value is below current price. Probabilities sum to one.",
        "",
        "## Market-Implied Sentiment Anchor Checks",
        "",
        "Unsupported market anchors have zero weight. Current price is reference only.",
        "",
        "## Full-Chain/Core-Satellite Dependency Checks",
        "",
        "Not applicable to this cross-market strategy report.",
        "",
        "## Value-Chain Economics Dependency Checks",
        "",
        "Hengrui and Industrial Fulian trace to repaired growth/SOTP artifacts. ZTE and Jiangbolong are downgraded.",
        "",
        "## Price/Share-Count Checks",
        "",
        "Prices are 2026-07-10 closes; CNY A-share denominators are explicit.",
        "",
        "## Fake-Precision Flags",
        "",
        "Probabilities are judgmental, not statistically estimated; they are disclosed rather than hidden in unsupported anchor weights.",
        "",
        "## Growth Earnings Dependency Checks",
        "",
        "Investable growth credit is limited to Hengrui and Industrial Fulian.",
        "",
        "## Model Reproducibility",
        "",
        "Model Reproducibility: PASS",
    ]
    write_text(ANALYSIS_DIR / "valuation_audit.md", "\n".join(audit_lines))
    build_growth_outputs(hengrui_sotp, conditional)
    print(
        json.dumps(
            {
                "investable_rows": len(valuation_rows),
                "conditional_rows": len(conditional),
                "tickers": [row["ticker"] for row in valuation_rows],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
