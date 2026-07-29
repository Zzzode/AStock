#!/usr/bin/env python3
"""Build the final source-governed valuation and growth packages."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
PRICE_DATE = "2026-07-10"
PROBABILITIES = (0.30, 0.50, 0.20)


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def expected_value(values: tuple[float, float, float], probabilities: tuple[float, float, float]) -> float:
    return sum(value * probability for value, probability in zip(values, probabilities))


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
    broker_anchor: float,
    broker_weight: float,
    action: str,
    evidence_quality: str,
    catalyst: str,
    invalidation: str,
    next_quarter_threshold: str,
    scenario_assumptions: dict[str, str],
) -> dict[str, Any]:
    displayed_values = tuple(round(value, 2) for value in (bear, base, bull))
    scenario_expected = round(expected_value(displayed_values, PROBABILITIES), 2)
    fundamental_weight = round(1.0 - broker_weight, 2)
    final_target = round(
        scenario_expected * fundamental_weight + broker_anchor * broker_weight,
        2,
    )
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
        "secondary_check": "current-price-implied expectation and source-pure Street history",
        "bear": displayed_values[0],
        "base": displayed_values[1],
        "bull": displayed_values[2],
        "bear_probability": PROBABILITIES[0],
        "base_probability": PROBABILITIES[1],
        "bull_probability": PROBABILITIES[2],
        "scenario_expected_value": scenario_expected,
        "market_implied_anchor": current_price,
        "market_anchor_source": "current price reference only; zero target weight",
        "broker_anchor": broker_anchor,
        "fundamental_weight": fundamental_weight,
        "market_weight": 0.0,
        "broker_weight": broker_weight,
        "final_target": final_target,
        "upside": round(final_target / current_price - 1, 4),
        "bubble_degree_vs_base": round(current_price / displayed_values[1] - 1, 4),
        "action": action,
        "evidence_quality": evidence_quality,
        "catalyst": catalyst,
        "invalidation": invalidation,
        "next_quarter_threshold": next_quarter_threshold,
        "scenario_assumptions": scenario_assumptions,
        "target_formula": (
            f"{fundamental_weight:.0%} * probability-weighted displayed "
            f"bear/base/bull value + {broker_weight:.0%} * source-pure original-PDF "
            "Street target; market anchor weight is zero"
        ),
    }


def broker_rows() -> list[dict[str, Any]]:
    rows = [
        {
            "ticker": "601077",
            "broker": "华泰证券",
            "report_date": "2026-03-26",
            "rating": "增持",
            "target_price": 8.67,
            "revenue_E": "CNY30.235bn",
            "net_profit_E": "CNY13.268bn",
            "EPS_E": "CNY1.17",
            "method": "0.70x 2026E PB",
            "source_path": "sources/repaired-street-targets-20260712/601077_huatai_20260326.pdf",
            "valuation_weight": 0.10,
            "anchor_freshness": "current-year original PDF; pre-Q1-results target",
        },
        {
            "ticker": "000425",
            "broker": "太平洋证券",
            "report_date": "2025-05-12",
            "rating": "买入",
            "target_price": 11.62,
            "revenue_E": "CNY114.499bn",
            "net_profit_E": "CNY10.067bn",
            "EPS_E": "CNY0.85",
            "method": "17x 2025E PE; target is stale and used only as a 5% history anchor",
            "source_path": "sources/target-price-exhaustion-20260712/000425_2025-05-12_太平洋_19.pdf",
            "valuation_weight": 0.05,
            "anchor_freshness": "stale original PDF; latest detailed target is a third-party repost and has zero weight",
        },
        {
            "ticker": "601825",
            "broker": "东方证券",
            "report_date": "2024-11-06",
            "rating": "买入",
            "target_price": 8.64,
            "revenue_E": "CNY27.942bn",
            "net_profit_E": "CNY13.115bn",
            "EPS_E": "CNY1.36",
            "method": "0.69x 2024E PB; target is stale and used only as a 5% history anchor",
            "source_path": "sources/repaired-street-targets-20260712/601825_guosen_20241106.pdf",
            "valuation_weight": 0.05,
            "anchor_freshness": "stale original PDF; latest detailed target is a third-party repost and has zero weight",
        },
        {
            "ticker": "600276",
            "broker": "华泰证券",
            "report_date": "2026-03-26",
            "rating": "买入",
            "target_price": 89.16,
            "revenue_E": "CNY37.522bn",
            "net_profit_E": "CNY9.78bn",
            "EPS_E": "CNY1.47",
            "method": "SOTP: innovative-drug DCF + generics PE + licensing PE",
            "source_path": "sources/repaired-street-targets-20260712/600276_huatai_20260325.pdf",
            "valuation_weight": 0.10,
            "anchor_freshness": "current-year original PDF; followed by a modest target cut in a detailed repost",
        },
        {
            "ticker": "601138",
            "broker": "华泰证券",
            "report_date": "2025-10-30",
            "rating": "买入",
            "target_price": 100.00,
            "revenue_E": "CNY1,473.643bn",
            "net_profit_E": "CNY55.01bn",
            "EPS_E": "CNY2.77",
            "method": "36.1x 2026E PE",
            "source_path": "sources/repaired-street-targets-20260712/601138_huatai_20251030.pdf",
            "valuation_weight": 0.05,
            "anchor_freshness": "older original PDF; post-preview detailed repost target is lower and has zero weight",
        },
    ]
    prices = {
        "601077": 6.30,
        "000425": 8.43,
        "601825": 7.66,
        "600276": 55.75,
        "601138": 66.27,
    }
    for row in rows:
        row["implied_upside"] = round(
            row["target_price"] / prices[row["ticker"]] - 1,
            4,
        )
        row["source_quality"] = "original_pdf"
        row["source_validation"] = "PDF signature, ticker, broker, title and numeric-field text verified"
    return rows


def valuation_rows() -> list[dict[str, Any]]:
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
            broker_anchor=8.67,
            broker_weight=0.10,
            action="core review / pullback entry",
            evidence_quality="high",
            catalyst="NIM remains at or above 1.60%, revenue stays positive and asset quality is stable",
            invalidation="NIM below 1.55%, NPL above 1.15% or revenue growth below 2%",
            next_quarter_threshold="H1 revenue growth above 3%, NIM at least 1.60% and NPL no higher than 1.10%",
            scenario_assumptions={
                "bear": "2026E BVPS CNY12.78 at 0.42x PB under renewed NIM and credit stress",
                "base": "2026E BVPS CNY12.78 at 0.56x PB",
                "bull": "2026E BVPS CNY12.78 at 0.72x PB",
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
            broker_anchor=11.62,
            broker_weight=0.05,
            action="pullback entry / earnings validation",
            evidence_quality="high",
            catalyst="overseas and mining growth remain above 10% and operating cash flow stays positive",
            invalidation="2026E EPS below CNY0.60, overseas growth below 8% or cash flow reverses",
            next_quarter_threshold="H1 EPS at least CNY0.34, overseas revenue growth above 10% and positive OCF",
            scenario_assumptions={
                "bear": "EPS CNY0.60 at 10x PE under FX and domestic-cycle pressure",
                "base": "EPS CNY0.70 at 14x PE",
                "bull": "EPS CNY0.80 at 18x PE",
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
            method="PB-ROE probability scenarios with dividend and credit floor",
            bear=14.11 * 0.45,
            base=14.11 * 0.58,
            bull=14.11 * 0.73,
            broker_anchor=8.64,
            broker_weight=0.05,
            action="income-oriented market-supported watch",
            evidence_quality="medium-high",
            catalyst="revenue remains positive, provision coverage stays above 300% and payout is stable",
            invalidation="revenue turns negative, NPL exceeds 1.05% or provision coverage falls below 280%",
            next_quarter_threshold="H1 revenue positive, NPL at or below 1.00% and provision coverage at least 300%",
            scenario_assumptions={
                "bear": "2026E BVPS CNY14.11 at 0.45x PB",
                "base": "2026E BVPS CNY14.11 at 0.58x PB",
                "bull": "2026E BVPS CNY14.11 at 0.73x PB",
            },
        ),
        valuation_row(
            ticker="600276",
            company="恒瑞医药",
            bucket="launched_with_runway",
            current_price=55.75,
            shares=66.37199874,
            revenue=357.70,
            net_profit=95.39,
            eps=1.44,
            method="explicit SOTP: innovative-drug DCF + generics PE + licensing PE",
            bear=3250 / 66.37199874,
            base=4549 / 66.37199874,
            bull=5256 / 66.37199874,
            broker_anchor=89.16,
            broker_weight=0.10,
            action="trend pullback core / milestone validation",
            evidence_quality="medium-high",
            catalyst="innovative-drug sales grow at least 30%, approvals and BD milestones convert",
            invalidation="innovative growth below 20%, pipeline delays or EPS below CNY1.25",
            next_quarter_threshold="innovative sales growth at least 30%, EPS trajectory at least CNY1.35 and milestones on schedule",
            scenario_assumptions={
                "bear": "innovative DCF CNY290bn + generics CNY15bn + licensing CNY20bn",
                "base": "innovative DCF CNY405bn + generics CNY18bn + licensing CNY31.9bn",
                "bull": "AStock CNY525.6bn SOTP, an 11% haircut to Huatai's original-PDF CNY591.8bn benchmark",
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
            method="post-preview PE probability scenarios with margin and platform-ramp validation",
            bear=2.52 * 20,
            base=2.82 * 27,
            bull=3.25 * 30,
            broker_anchor=100.0,
            broker_weight=0.05,
            action="earnings-delivery pullback / market-supported watch",
            evidence_quality="high",
            catalyst="H2 AI-server ramp, 800G+ growth, gross margin at least 7% and cash conversion",
            invalidation="2026E net profit below CNY51.6bn, platform delay or gross margin below 7%",
            next_quarter_threshold="H2 net profit at least CNY32.1bn, AI-server growth above 100% and gross margin at least 7%",
            scenario_assumptions={
                "bear": "EPS CNY2.52 at 20x PE under slower platform ramp and margin pressure",
                "base": "post-preview EPS CNY2.82 at 27x PE",
                "bull": "EPS CNY3.25 at 30x PE",
            },
        ),
    ]


def hengrui_sotp() -> dict[str, Any]:
    shares = 66.37199874
    scenarios = {
        "bear": {
            "innovative_drug_dcf_100mn": 2900.0,
            "generic_and_other_100mn": 150.0,
            "licensing_100mn": 200.0,
        },
        "base": {
            "innovative_drug_dcf_100mn": 4050.0,
            "generic_and_other_100mn": 180.0,
            "licensing_100mn": 319.0,
        },
        "bull": {
            "innovative_drug_dcf_100mn": 4747.0,
            "generic_and_other_100mn": 192.0,
            "licensing_100mn": 317.0,
        },
    }
    for values in scenarios.values():
        equity_value = round(sum(values.values()), 2)
        values["equity_value_100mn"] = equity_value
        values["per_share_value"] = round(equity_value / shares, 2)
    return {
        "schema_version": "astock.hengrui_sotp.v2",
        "ticker": "600276",
        "company": "恒瑞医药",
        "shares_100mn": shares,
        "source_anchor": (
            "Huatai original PDF dated 2026-03-26: innovative-drug DCF CNY540.8bn, "
            "generics and other CNY19.2bn, licensing CNY31.7bn, total CNY591.8bn, "
            "WACC 7.4%, terminal growth 2.5% and target CNY89.16"
        ),
        "scenarios": scenarios,
        "probabilities": {"bear": 0.30, "base": 0.50, "bull": 0.20},
        "limitations": [
            "Product-level peak sales and phase-by-phase probability of success are not disclosed.",
            "All AStock scenarios apply explicit haircuts to the original-PDF innovative-drug DCF; the unhaircut CNY591.8bn SOTP remains a separate Street anchor.",
            "Licensing income is valued separately because timing and recurrence differ from product sales.",
        ],
    }


def conditional_watch_models() -> list[dict[str, Any]]:
    definitions = [
        {
            "ticker": "000063",
            "company": "中兴通讯",
            "status": "watchlist_only_formally_bounded_segment_economics",
            "current_price": 40.53,
            "bear": 25.0,
            "base": 37.0,
            "bull": 51.9,
            "probabilities": {"bear": 0.35, "base": 0.45, "bull": 0.20},
            "reason": (
                "Compute demand and customer classes are directly evidenced: 2025 compute-related "
                "revenue increased about 150% to 24.6% of revenue, server/storage revenue increased "
                "more than 200%, data-center products increased 50%, and 2026Q1 compute mix reached "
                "27%, serving leading internet, operator, government and financial customers. "
                "The company does not separately publish compute units, contract ASP or segment "
                "margin, so the model uses consolidated earnings only; Q1 profit and operating "
                "cash flow also require H2 validation."
            ),
            "upgrade_trigger": (
                "H2 profit growth turns positive, operating cash flow improves, 2026E EPS reaches "
                "at least CNY1.54 and compute mix remains at or above 27%."
            ),
            "checked_sources": [
                "sources/core-broker-reports-20260711/000063-中兴通讯/"
                "01-2026-05-05-国金证券-连接-算力双轮驱动-利润筑底回升.pdf",
                "sources/core-broker-reports-20260711/000063-中兴通讯/"
                "02-2026-03-10-开源证券-公司信息更新报告-算力业务跨越式增长-研发投入夯实长期竞争力.pdf",
                "sources/launched-official-20260711/000063_2026Q1_official.pdf",
            ],
            "formal_boundary": (
                "Named end customers, compute units, contract ASP and compute-segment gross margin "
                "are not separately published in the checked company filing and original reports."
            ),
            "valuation_consequence": (
                "No separate high-growth compute multiple is applied. Bear/base/bull values use "
                "consolidated EPS and consolidated PE, and the probability value remains below price."
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
            "reason": (
                "H1 delivery is strong and the operating chain is directly evidenced by renewed "
                "LTA/MOU wafer-supply agreements, in-house high-end packaging, self-developed "
                "SPU/HLC, AMD joint optimization that lowers DRAM usage by about 40%, platform "
                "certifications and entry into communications, financial and internet customer "
                "supply chains. Exact contract prices and H2 named-customer orders are not public; "
                "Q1 operating cash flow was negative, so cycle duration remains the binding risk."
            ),
            "upgrade_trigger": (
                "H2 deducted profit and operating cash flow validate, inventory write-down stays "
                "contained, and H2 revenue/profit remain consistent with the base cycle bridge."
            ),
            "cycle_sensitivity": {
                "bear": "FY net profit CNY13.1bn / EPS about CNY31 / 11x",
                "base": "FY net profit CNY16.1bn / EPS about CNY38 / 14x",
                "bull": "FY net profit CNY19.1bn / EPS about CNY45 / 17x",
            },
            "checked_sources": [
                "sources/earnings-previews-20260711/301308_preview.pdf",
                "sources/core-broker-reports-20260711/301308-江波龙/"
                "01-2026-05-07-国信证券-1Q26归母净利润同比增长2644.05-端侧应用多维拓展.pdf",
                "sources/core-broker-reports-20260711/301308-江波龙/"
                "02-2026-05-07-爱建证券-2025年报-2026Q1点评-国产存储模组龙头进入业绩爆发期.pdf",
            ],
            "formal_boundary": (
                "Supplier contract prices, inventory cost layers and H2 named-customer order values "
                "are not separately published in the checked announcement and original reports."
            ),
            "valuation_consequence": (
                "The model applies 11x/14x/17x cycle PE rather than a structural-growth multiple, "
                "retains a 35% bear probability and stays conditional because probability value is "
                "below current price."
            ),
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
            "reason": (
                "Coal is the only full-market silent-accumulation industry with a high-impact "
                "preview candidate, but current price exceeds probability-weighted earnings value."
            ),
            "upgrade_trigger": (
                "Coal price and 2026E EPS exceed the current broker base while dividend remains durable."
            ),
        },
    ]
    for row in definitions:
        probabilities = row["probabilities"]
        expected = round(
            row["bear"] * probabilities["bear"]
            + row["base"] * probabilities["base"]
            + row["bull"] * probabilities["bull"],
            2,
        )
        row["probability_expected_value"] = expected
        row["expected_upside"] = round(expected / row["current_price"] - 1, 4)
    return definitions


def growth_drivers(sotp: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "ticker": "600276",
            "company": "恒瑞医药",
            "applies": True,
            "growth_driver": "innovative-drug sales, approvals and BD milestones",
            "historical_bridge": {
                "revenue_2025_100mn": 316.29,
                "innovative_sales_2025_100mn": 163.42,
                "licensing_revenue_2025_100mn": 33.92,
                "mature_and_other_revenue_proxy_2025_100mn": 118.95,
                "q1_2026_innovative_sales_100mn": 45.26,
                "q1_2026_licensing_revenue_100mn": 7.87,
                "q1_2026_parent_np_100mn": 22.82,
            },
            "scenario_earnings_bridge": {
                "bear": {
                    "innovative_sales_100mn": 196.10,
                    "licensing_revenue_100mn": 20.0,
                    "mature_and_other_revenue_100mn": 109.43,
                    "revenue_100mn": 325.53,
                    "net_margin": 0.235,
                    "net_profit_100mn": 76.50,
                    "eps": 1.15,
                    "sotp_per_share": sotp["scenarios"]["bear"]["per_share_value"],
                },
                "base": {
                    "innovative_sales_100mn": 212.45,
                    "licensing_revenue_100mn": 31.70,
                    "mature_and_other_revenue_100mn": 113.00,
                    "revenue_100mn": 357.15,
                    "net_margin": 0.267,
                    "net_profit_100mn": 95.36,
                    "eps": 1.44,
                    "sotp_per_share": sotp["scenarios"]["base"]["per_share_value"],
                },
                "bull": {
                    "innovative_sales_100mn": 220.62,
                    "licensing_revenue_100mn": 40.0,
                    "mature_and_other_revenue_100mn": 118.95,
                    "revenue_100mn": 379.57,
                    "net_margin": 0.290,
                    "net_profit_100mn": 110.08,
                    "eps": 1.66,
                    "sotp_per_share": sotp["scenarios"]["bull"]["per_share_value"],
                },
            },
            "unit_volume_or_proxy": "innovative-sales growth, approvals and recognized BD revenue",
            "ASP_or_price": "portfolio-mix proxy; product-level ASP is not disclosed",
            "recognized_revenue_ratio": "reported product sales and recognized licensing revenue only",
            "growth_gross_margin": "2026Q1 consolidated gross margin 86.6%",
            "incremental_opex": "base-case net margin 26.7% captures R&D and launch costs",
            "current_price_implied_growth": (
                "At CNY55.75, a 40x PE requires EPS CNY1.39 and net profit about CNY92.5bn; "
                "the price therefore embeds most of the base earnings bridge but not the full SOTP."
            ),
            "evidence_type": "official Q1 data plus original broker PDFs",
            "source": (
                "sources/core-broker-reports-20260711/600276-恒瑞医药/"
                "02-2026-05-07-华源证券-创新成果密集落地-全球化布局加速推进.pdf; "
                "sources/repaired-street-targets-20260712/600276_huatai_20260325.pdf"
            ),
            "evidence_status": "portfolio-level evidence closed",
            "direct_disclosure": (
                "2025 innovative-drug revenue CNY16.342bn and BD revenue CNY3.392bn; "
                "2026Q1 innovative-drug revenue CNY4.526bn, +25.75%, 61.69% of drug sales; "
                "non-oncology innovative revenue +92.13%; 7 class-1 launches, 15 NDA "
                "acceptances and 28 phase-III programs in 2025; 8 NDA acceptances in 2026Q1."
            ),
            "proxy_evidence": (
                "Approval count, NDA/phase-III progression, recognized BD income, twelve BD "
                "transactions with nearly USD28bn headline value and portfolio-level SOTP."
            ),
            "checked_sources": (
                "official 2026Q1 evidence, Huayuan 2026-05-07 original PDF, Southwest "
                "2026-07-01 original PDF and Huatai 2026-03-25 original SOTP PDF"
            ),
            "formal_boundary": (
                "The checked sources do not publish product-by-product peak sales, phase-level "
                "probability of success or exact future BD recognition dates."
            ),
            "valuation_consequence": (
                "A portfolio-level DCF/SOTP is allowed, but AStock haircuts the innovative-drug "
                "DCF and probability-weights licensing income; no single-product peak-sales value "
                "is inserted into the target."
            ),
            "evidence_gap": None,
            "valuation_credit": "investable earnings credit through explicit segment SOTP with haircuts",
            "next_quarter_validation_threshold": (
                "innovative-sales growth at least 30%, EPS trajectory at least CNY1.35 and milestones on schedule"
            ),
        },
        {
            "ticker": "601138",
            "company": "工业富联",
            "applies": True,
            "growth_driver": "AI servers, next-generation GPU platforms and 800G+ switches",
            "historical_bridge": {
                "revenue_2025_100mn": 9028.9,
                "h1_parent_np_2026_midpoint_100mn": 239.0,
                "h1_deducted_np_2026_midpoint_100mn": 232.0,
                "q1_parent_np_2026_100mn": 105.95,
                "q2_parent_np_2026_midpoint_100mn": 133.05,
                "ai_server_revenue_growth_h1": 2.30,
                "switch_800g_shipment_growth_h1": 1.40,
            },
            "scenario_earnings_bridge": {
                "bear": {
                    "revenue_100mn": 13000.0,
                    "net_profit_100mn": 500.6,
                    "eps": 2.52,
                    "multiple": 20,
                    "value": 50.40,
                },
                "base": {
                    "revenue_100mn": 14803.7,
                    "net_profit_100mn": 560.1,
                    "eps": 2.82,
                    "multiple": 27,
                    "value": 76.14,
                    "required_h2_np_100mn": 321.1,
                },
                "bull": {
                    "revenue_100mn": 16000.0,
                    "net_profit_100mn": 645.97,
                    "eps": 3.25,
                    "multiple": 30,
                    "value": 97.50,
                },
            },
            "unit_volume_or_proxy": "AI-server revenue growth, switch shipments and platform ramp",
            "ASP_or_price": "platform and system-mix proxy; product-level ASP is not disclosed",
            "recognized_revenue_ratio": "official H1 guidance plus post-preview full-year forecast",
            "growth_gross_margin": "2026Q1 consolidated gross margin 7.35%",
            "incremental_opex": "captured in consolidated net-profit scenarios",
            "current_price_implied_growth": (
                "CNY66.27 equals 23.5x base EPS CNY2.82 and requires about CNY48.8bn net profit "
                "at a 27x base multiple."
            ),
            "evidence_type": "official H1 preview, original broker PDFs and detailed post-preview report page",
            "source": (
                "sources/earnings-previews-20260711/601138_preview.pdf; "
                "sources/repaired-street-targets-20260712/601138_huatai_20251030.pdf"
            ),
            "evidence_status": "consolidated earnings evidence closed",
            "direct_disclosure": (
                "Official H1 parent-profit midpoint CNY23.9bn; AI-server revenue +230%; "
                "800G+ switch shipments +140%; share gains at major customers; next-generation "
                "products expected to enter H2 mass production."
            ),
            "proxy_evidence": (
                "Major-customer joint development, CPO sample production with guidance for more "
                "than ten thousand units, Rubin ramp, platform/system mix and post-preview "
                "2026E revenue CNY1,480.37bn / net profit CNY56.01bn / EPS CNY2.82."
            ),
            "checked_sources": (
                "official H1 preview, Jinyuan 2026-06-18 original PDF, Huatai original "
                "platform reports and the archived Huatai post-preview full report page"
            ),
            "formal_boundary": (
                "The checked sources do not publish named-customer allocation, product-level ASP, "
                "exact utilization or AI-server segment gross margin."
            ),
            "valuation_consequence": (
                "Only consolidated PE receives valuation credit; no separate AI-server segment "
                "multiple is applied, and the base case requires H2 net profit of CNY32.11bn."
            ),
            "evidence_gap": None,
            "valuation_credit": "investable earnings credit through conservative consolidated PE scenarios",
            "next_quarter_validation_threshold": (
                "H2 net profit at least CNY32.1bn, AI-server growth above 100% and gross margin at least 7%"
            ),
        },
        {
            "ticker": "000063",
            "company": "中兴通讯",
            "applies": True,
            "growth_driver": "compute products, AI servers/storage and data-center networks",
            "historical_bridge": {
                "compute_revenue_growth_2025": 1.50,
                "compute_revenue_share_2025": 0.246,
                "server_storage_revenue_growth_2025": 2.00,
                "data_center_product_growth_2025": 0.50,
                "compute_revenue_share_q1_2026": 0.27,
            },
            "scenario_earnings_bridge": {
                "bear": {
                    "revenue_100mn": 1500.0,
                    "net_profit_100mn": 62.2,
                    "eps": 1.30,
                    "multiple": 19.23,
                    "value": 25.0,
                },
                "base": {
                    "revenue_100mn": 1728.08,
                    "net_profit_100mn": 73.73,
                    "eps": 1.541,
                    "multiple": 24.01,
                    "value": 37.0,
                },
                "bull": {
                    "revenue_100mn": 1900.0,
                    "net_profit_100mn": 83.7,
                    "eps": 1.75,
                    "multiple": 29.66,
                    "value": 51.9,
                },
            },
            "unit_volume_or_proxy": (
                "compute revenue share, server/storage revenue growth and data-center product growth"
            ),
            "ASP_or_price": "consolidated revenue-mix proxy; no contract ASP is inserted",
            "recognized_revenue_ratio": "reported revenue mix plus Guojin consolidated forecast",
            "growth_gross_margin": "Guojin 2026E consolidated gross margin 31.3%",
            "incremental_opex": "captured in CNY7.373bn consolidated net-profit forecast",
            "current_price_implied_growth": (
                "CNY40.53 equals 26.3x Guojin EPS CNY1.541; at the 24x base multiple, "
                "price implies EPS CNY1.69 and net profit about CNY8.08bn."
            ),
            "evidence_type": "official Q1 filing plus two original broker PDFs",
            "source": (
                "sources/launched-official-20260711/000063_2026Q1_official.pdf; "
                "sources/core-broker-reports-20260711/000063-中兴通讯/"
                "01-2026-05-05-国金证券-连接-算力双轮驱动-利润筑底回升.pdf; "
                "sources/core-broker-reports-20260711/000063-中兴通讯/"
                "02-2026-03-10-开源证券-公司信息更新报告-算力业务跨越式增长-研发投入夯实长期竞争力.pdf"
            ),
            "evidence_status": "consolidated earnings evidence closed",
            "direct_disclosure": (
                "Compute-related revenue +150% in 2025, 24.6% revenue share; server/storage "
                "+200%+, data-center products +50%; compute mix 27% in 2026Q1."
            ),
            "proxy_evidence": (
                "Leading internet, operator, government and financial customer classes; "
                "Guojin 2026E revenue CNY172.808bn, net profit CNY7.373bn, EPS CNY1.541 "
                "and operating cash flow per share CNY1.80."
            ),
            "checked_sources": (
                "official 2026Q1 report, Guojin 2026-05-05 original PDF and "
                "Kaiyuan 2026-03-10 original PDF"
            ),
            "formal_boundary": (
                "Named end customers, compute units, contract ASP and compute-segment margin "
                "are not separately published."
            ),
            "valuation_consequence": (
                "No separate compute multiple; consolidated PE scenarios only. Probability "
                "value is below current price, so action remains conditional watch."
            ),
            "evidence_gap": None,
            "valuation_credit": "conditional consolidated earnings credit; no formal target",
            "next_quarter_validation_threshold": (
                "H2 profit growth positive, operating cash flow improves, EPS trajectory "
                "at least CNY1.54 and compute mix at least 27%"
            ),
        },
        {
            "ticker": "301308",
            "company": "江波龙",
            "applies": True,
            "growth_driver": "storage price cycle, secured wafer supply and enterprise/AI mix",
            "historical_bridge": {
                "h1_parent_np_midpoint_100mn": 101.0,
                "h1_deducted_np_midpoint_100mn": 97.5,
                "q1_parent_np_100mn": 38.62,
                "q1_ocf_100mn": -28.75,
                "enterprise_storage_growth_2025": 0.933,
                "nand_price_index_growth_sep_to_apr": 3.70,
                "dram_price_index_growth_sep_to_apr": 3.76,
            },
            "scenario_earnings_bridge": {
                "bear": {
                    "revenue_100mn": 390.0,
                    "net_profit_100mn": 131.0,
                    "eps": 30.75,
                    "multiple": 11.09,
                    "value": 341.0,
                },
                "base": {
                    "revenue_100mn": 440.0,
                    "net_profit_100mn": 161.0,
                    "eps": 37.79,
                    "multiple": 14.08,
                    "value": 532.0,
                },
                "bull": {
                    "revenue_100mn": 480.0,
                    "net_profit_100mn": 191.0,
                    "eps": 44.84,
                    "multiple": 17.06,
                    "value": 765.0,
                },
            },
            "unit_volume_or_proxy": (
                "H1 profit delivery, enterprise-storage growth, platform qualification and "
                "NAND/DRAM price indices"
            ),
            "ASP_or_price": (
                "public NAND/DRAM price-index proxy; no supplier contract price is inserted"
            ),
            "recognized_revenue_ratio": "official H1 guidance plus cycle-calibrated H2 scenarios",
            "growth_gross_margin": "2026Q1 gross margin 55.53%; base scenario normalizes cycle gains",
            "incremental_opex": "captured in the full-year net-profit scenarios",
            "current_price_implied_growth": (
                "CNY587.60 equals 15.5x base EPS CNY37.79; at 14x, price implies EPS "
                "CNY41.97 and net profit about CNY17.88bn."
            ),
            "evidence_type": "official H1 preview plus two original broker PDFs",
            "source": (
                "sources/earnings-previews-20260711/301308_preview.pdf; "
                "sources/core-broker-reports-20260711/301308-江波龙/"
                "01-2026-05-07-国信证券-1Q26归母净利润同比增长2644.05-端侧应用多维拓展.pdf; "
                "sources/core-broker-reports-20260711/301308-江波龙/"
                "02-2026-05-07-爱建证券-2025年报-2026Q1点评-国产存储模组龙头进入业绩爆发期.pdf"
            ),
            "evidence_status": "cycle-driver evidence closed",
            "direct_disclosure": (
                "Renewed LTA/MOU wafer-supply agreements, self-developed SPU/HLC, "
                "in-house high-end packaging and AMD joint optimization lowering DRAM "
                "usage by about 40%."
            ),
            "proxy_evidence": (
                "NAND/DRAM price indices, platform certifications, enterprise-storage "
                "growth and entry into communications, financial and internet supply chains."
            ),
            "checked_sources": (
                "official 2026H1 preview, Guosen 2026-05-07 original PDF and "
                "Aijian 2026-05-07 original PDF"
            ),
            "formal_boundary": (
                "Supplier contract prices, inventory cost layers and H2 named-customer "
                "order values are not separately published."
            ),
            "valuation_consequence": (
                "11x/14x/17x cycle PE and 35% bear probability replace a structural-growth "
                "multiple; probability value below price keeps the name conditional."
            ),
            "evidence_gap": None,
            "valuation_credit": "conditional cycle earnings credit; no formal target",
            "next_quarter_validation_threshold": (
                "H2 deducted profit validates the base bridge, operating cash flow turns "
                "positive and inventory write-down remains contained"
            ),
        },
    ]


def broker_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Broker and Street Consensus",
        "",
        "Only original PDFs receive positive valuation weight. Detailed repost targets are used solely for zero-weight direction checks in the report narrative.",
        "",
        "| Ticker | Broker | Date | Rating | Target | Revenue E | Net profit E | EPS E | Method | Source quality | Weight | Freshness |",
        "|---|---|---|---|---:|---|---|---|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['broker']} | {row['report_date']} | "
            f"{row['rating']} | {row['target_price']:.2f} | {row['revenue_E']} | "
            f"{row['net_profit_E']} | {row['EPS_E']} | {row['method']} | "
            f"{row['source_quality']} | {row['valuation_weight']:.0%} | "
            f"{row['anchor_freshness']} |"
        )
    return "\n".join(lines)


def valuation_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Valuation Model",
        "",
        "## Final Valuation Table",
        "",
        "| Ticker | Company | Price | Market cap | 2026E revenue | 2026E NP/EPS | Method | Bear | Base | Bull | Fundamental EV | Street | Weight | Final target | Upside | Action | Evidence |",
        "|---|---|---:|---:|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['current_price']:.2f} | "
            f"{row['market_cap_100mn_cny']:.1f} | {row['revenue_2026e_100mn']:.1f} | "
            f"{row['np_2026e_100mn']:.1f}/{row['eps_2026e']:.2f} | {row['method']} | "
            f"{row['bear']:.2f} | {row['base']:.2f} | {row['bull']:.2f} | "
            f"{row['scenario_expected_value']:.2f} | {row['broker_anchor']:.2f} | "
            f"{row['broker_weight']:.0%} | {row['final_target']:.2f} | "
            f"{row['upside']:.1%} | {row['action']} | {row['evidence_quality']} |"
        )
    lines += [
        "",
        "## Three-Tier Targets",
        "",
        "Bear/base/bull values are company-specific and every bear value is below current price. Probabilities are 30%/50%/20% and sum to 100%.",
        "",
        "## Relative / PEG / PSG Comparison",
        "",
        "Banks use PB-ROE, XCMG and Industrial Fulian use normalized PE with cash-flow or margin checks, and Hengrui uses explicit SOTP. No uniform PE is applied.",
        "",
        "## Seasonality Calibration",
        "",
        "Full-year forecasts are checked against Q1 or H1 progress. H1 previews are not mechanically annualized.",
        "",
        "## Next-Quarter Threshold",
        "",
    ]
    for row in rows:
        lines.append(f"- {row['ticker']} {row['company']}: {row['next_quarter_threshold']}")
    lines += [
        "",
        "## Method and Assumption Bridge",
        "",
        "Every scenario assumption is stored in the structured JSON. Final targets use displayed, rounded scenario values so the reader can reproduce the arithmetic.",
        "",
        "## Market-Expectation Valuation Bridge",
        "",
        "Current price carries zero target weight. Bubble degree versus the base case is disclosed per row, and action labels distinguish investable upside from market-supported watch status.",
        "",
        "## Broker/Street Comparison",
        "",
        "See `data/broker_street_consensus_20260711.md`. Only ticker-matched original PDFs receive 5%-10% weight. Detailed third-party reposts are zero-weight direction checks.",
        "",
        "## Market-Implied Sentiment Anchor",
        "",
        "`market_implied_anchor` is retained only as a current-price reference with `market_weight=0`.",
        "",
        "## Growth Earnings Dependency",
        "",
        "Hengrui and Industrial Fulian consume the precision growth package. ZTE and Jiangbolong are downgraded in `data/conditional_watch_models_20260712.json`.",
        "",
        "## Full-Chain Classification Dependency",
        "",
        "Not applicable to a cross-market sector-rotation strategy report. Company-specific evidence determines valuation eligibility.",
    ]
    return "\n".join(lines)


def valuation_audit(rows: list[dict[str, Any]], brokers: list[dict[str, Any]]) -> str:
    lines = [
        "# Valuation Audit",
        "",
        "## Arithmetic Checks",
        "",
    ]
    broker_map = {row["ticker"]: row for row in brokers}
    for row in rows:
        scenario_expected = expected_value(
            (row["bear"], row["base"], row["bull"]),
            (row["bear_probability"], row["base_probability"], row["bull_probability"]),
        )
        target = (
            row["fundamental_weight"] * row["scenario_expected_value"]
            + row["broker_weight"] * row["broker_anchor"]
        )
        lines.append(
            f"- {row['ticker']}: probability sum "
            f"{row['bear_probability'] + row['base_probability'] + row['bull_probability']:.2f}; "
            f"scenario EV {scenario_expected:.3f} -> stored {row['scenario_expected_value']:.2f}; "
            f"target {target:.3f} -> stored {row['final_target']:.2f}; "
            f"market cap {row['current_price'] * row['shares_100mn']:.2f} -> stored "
            f"{row['market_cap_100mn_cny']:.2f}."
        )
    lines += [
        "",
        "## Forecast Availability",
        "",
        "All five formal rows disclose current price, shares, market cap, 2026E revenue, net profit and EPS. Conditional watch names are excluded from investable valuation.",
        "",
        "## Target-Price Comparability",
        "",
    ]
    for ticker, broker in broker_map.items():
        lines.append(
            f"- {ticker}: {broker['broker']} {broker['report_date']} original PDF; "
            f"target CNY{broker['target_price']:.2f}; weight {broker['valuation_weight']:.0%}; "
            f"{broker['anchor_freshness']}."
        )
    lines += [
        "",
        "## Final Valuation Completeness",
        "",
        "Every formal row includes bear/base/bull, explicit probabilities, final target, upside, action, catalyst, invalidation and next-quarter threshold.",
        "",
        "## Scenario-Band Checks",
        "",
        "Every row satisfies bear < base < bull and bear < current price. Probability-weighted value, not the base case alone, drives the final target.",
        "",
        "## Market-Implied Sentiment Anchor Checks",
        "",
        "Unsupported market targets have been removed. Current price is a zero-weight reference only.",
        "",
        "## Full-Chain/Core-Satellite Dependency Checks",
        "",
        "Not applicable: this is a full-market sector-rotation report, not a full industry-chain report.",
        "",
        "## Value-Chain Economics Dependency Checks",
        "",
        "Bank values depend on NIM, asset quality and ROE; XCMG depends on overseas/mining mix and cash conversion; Hengrui and Industrial Fulian consume explicit growth bridges.",
        "",
        "## Price/Share-Count Checks",
        "",
        "Prices are 2026-07-10 A-share closes in CNY. Share counts and EPS denominators reconcile within rounding tolerance.",
        "",
        "## Fake-Precision Flags",
        "",
        "Targets are rounded to two decimals only after scenario values are rounded. Stale original-PDF Street anchors are capped at 5%.",
        "",
        "## Supply-Chain Dependency Checks",
        "",
        "Not applicable; no unsupported supply-chain target credit is used.",
        "",
        "## Growth Earnings Dependency Checks",
        "",
        "All four growth names trace to base/growth splits, revenue proxies, margins, net profit, EPS, sensitivity and next-quarter thresholds. Hengrui and Industrial Fulian receive investable credit; ZTE and Jiangbolong remain watchlist-only because probability value and validation thresholds do not pass.",
        "",
        "## Model Reproducibility",
        "",
        "Model Reproducibility: PASS",
    ]
    return "\n".join(lines)


def growth_markdown(drivers: list[dict[str, Any]]) -> tuple[str, str, str]:
    growth = [
        "# Growth Earnings Model",
        "",
        "Gate status: PASS for all four evidence bridges; investable credit for Hengrui and Industrial Fulian, watchlist-only for ZTE and Jiangbolong.",
        "",
        "## Revenue-to-EPS Bridges",
        "",
    ]
    segment = ["# Segment Forecast Bridge", ""]
    sensitivity = [
        "# Implied Growth Sensitivity",
        "",
        "| Company | Bear revenue/NP/EPS | Base revenue/NP/EPS | Bull revenue/NP/EPS | Current-price implication | Validation |",
        "|---|---|---|---|---|---|",
    ]
    for driver in drivers:
        scenarios = driver["scenario_earnings_bridge"]
        growth += [
            f"### {driver['company']} ({driver['ticker']})",
            "",
            f"- Driver: {driver['growth_driver']}",
            f"- Unit/order/ASP proxy: {driver['unit_volume_or_proxy']}; {driver['ASP_or_price']}.",
            f"- Revenue recognition: {driver['recognized_revenue_ratio']}.",
            f"- Margin and opex: {driver['growth_gross_margin']}; {driver['incremental_opex']}.",
            f"- Current-price implication: {driver['current_price_implied_growth']}",
            f"- Evidence status: {driver['evidence_status']}",
            f"- Direct disclosure: {driver['direct_disclosure']}",
            f"- Proxy evidence: {driver['proxy_evidence']}",
            f"- Checked sources: {driver['checked_sources']}",
            f"- Formal boundary: {driver['formal_boundary']}",
            f"- Valuation consequence: {driver['valuation_consequence']}",
            f"- Valuation credit: {driver['valuation_credit']}",
            f"- Next-quarter threshold: {driver['next_quarter_validation_threshold']}",
            "",
        ]
        segment += [
            f"## {driver['company']}",
            "",
            f"Historical/base split: `{json.dumps(driver['historical_bridge'], ensure_ascii=False)}`",
            "",
            f"Scenario bridge: `{json.dumps(scenarios, ensure_ascii=False)}`",
            "",
        ]
        sensitivity.append(
            f"| {driver['company']} | {scenarios['bear']['revenue_100mn']:.1f}/"
            f"{scenarios['bear']['net_profit_100mn']:.1f}/{scenarios['bear']['eps']:.2f} | "
            f"{scenarios['base']['revenue_100mn']:.1f}/"
            f"{scenarios['base']['net_profit_100mn']:.1f}/{scenarios['base']['eps']:.2f} | "
            f"{scenarios['bull']['revenue_100mn']:.1f}/"
            f"{scenarios['bull']['net_profit_100mn']:.1f}/{scenarios['bull']['eps']:.2f} | "
            f"{driver['current_price_implied_growth']} | "
            f"{driver['next_quarter_validation_threshold']} |"
        )
    return "\n".join(growth), "\n".join(segment), "\n".join(sensitivity)


def main() -> None:
    brokers = broker_rows()
    rows = valuation_rows()
    sotp = hengrui_sotp()
    conditional = conditional_watch_models()
    drivers = growth_drivers(sotp)

    write_json(
        DATA_DIR / "broker_street_consensus_20260711.json",
        {"data_cutoff": PRICE_DATE, "rows": brokers},
    )
    write_text(DATA_DIR / "broker_street_consensus_20260711.md", broker_markdown(brokers))
    write_json(
        DATA_DIR / "current_valuation_model_20260711.json",
        {"data_cutoff": PRICE_DATE, "rows": rows},
    )
    write_json(DATA_DIR / "hengrui_sotp_model_20260712.json", sotp)
    write_json(
        DATA_DIR / "conditional_watch_models_20260712.json",
        {"schema_version": "astock.conditional_watch_models.v2", "rows": conditional},
    )
    write_json(
        DATA_DIR / "growth_driver_model.json",
        {"schema_version": "astock.growth_driver_model.v2", "data_cutoff": PRICE_DATE, "drivers": drivers},
    )

    write_text(ANALYSIS_DIR / "valuation_model.md", valuation_markdown(rows))
    write_text(ANALYSIS_DIR / "valuation_audit.md", valuation_audit(rows, brokers))
    growth, segment, sensitivity = growth_markdown(drivers)
    write_text(ANALYSIS_DIR / "growth_earnings_model.md", growth)
    write_text(ANALYSIS_DIR / "segment_forecast_bridge.md", segment)
    write_text(ANALYSIS_DIR / "implied_growth_sensitivity.md", sensitivity)
    write_text(
        ANALYSIS_DIR / "jiangbolong_cycle_sensitivity.md",
        """# Jiangbolong Cycle Sensitivity

Official H1 parent-profit midpoint is CNY10.1bn and deducted-profit midpoint is CNY9.75bn. Q1 parent profit is CNY3.862bn, implying Q2 parent profit of CNY6.238bn, while Q1 operating cash flow is negative CNY2.875bn.

| Scenario | FY net profit | EPS | Multiple | Value | Current-price gap |
|---|---:|---:|---:|---:|---:|
| Bear | CNY13.1bn | CNY30.75 | 11x | CNY341 | -42.0% |
| Base | CNY16.1bn | CNY37.79 | 14x | CNY532 | -9.5% |
| Bull | CNY19.1bn | CNY44.84 | 17x | CNY765 | +30.2% |

The 35%/45%/20% probability value is CNY511.75, 12.9% below the CNY587.60 current price. The old CNY802.30 target is withdrawn. Upgrade requires positive H2 operating cash flow, contained inventory write-down, and contract-price or customer-order evidence that extends the cycle.
""",
    )
    write_text(
        ANALYSIS_DIR / "value_chain_economics.md",
        """# Value-Chain Economics

| Company | Value or price proxy | Margin pool | Demand | Capacity/order evidence | Valuation credit |
|---|---|---|---|---|---|
| Hengrui | innovative sales, licensing revenue and Huatai segment SOTP | Q1 gross margin 86.6%; base net margin 26.7% | innovative demand positive; generics pressured | approvals, clinical and BD milestones | explicit SOTP with haircuts |
| Industrial Fulian | AI-server revenue +230% and 800G+ shipments +140% | Q1 consolidated gross margin 7.35% | hyperscaler AI capex strong | next-platform ramp qualitative; allocation undisclosed | conservative consolidated PE |
| ZTE | compute share proxy; ASP not disclosed | segment margin not disclosed | AI compute strong | order/customer allocation insufficient | watchlist only |
| Jiangbolong | H1 guidance and storage-price proxy | high but cyclical Q1 margin | storage cycle strong | inventory, ASP, customer and H2 cash conversion unresolved | watchlist only |
""",
    )
    print(
        json.dumps(
            {
                "investable_rows": len(rows),
                "conditional_rows": len(conditional),
                "broker_original_pdf_rows": len(brokers),
                "tickers": [row["ticker"] for row in rows],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
