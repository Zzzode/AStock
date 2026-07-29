#!/usr/bin/env python3
"""Build dynamic valuation layers from the 2026-07-15 full-market refresh."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
DATA_CUTOFF = "2026-07-15"
PROBABILITIES = (0.30, 0.50, 0.20)

CYCLICAL = {"煤炭", "有色金属", "石油石化", "基础化工", "交通运输", "钢铁"}
FINANCIAL = {"非银金融", "银行"}
GROWTH = {"电子", "计算机", "电力设备", "国防军工", "传媒", "医药生物", "通信"}
PE_RANGES = {
    "煤炭": (7.0, 9.0, 11.0),
    "有色金属": (8.0, 12.0, 16.0),
    "石油石化": (6.0, 9.0, 12.0),
    "基础化工": (10.0, 14.0, 18.0),
    "电力设备": (16.0, 22.0, 28.0),
    "电子": (18.0, 26.0, 34.0),
    "计算机": (18.0, 28.0, 38.0),
    "机械设备": (14.0, 20.0, 28.0),
    "国防军工": (25.0, 35.0, 45.0),
    "交通运输": (8.0, 12.0, 16.0),
    "传媒": (10.0, 14.0, 18.0),
    "医药生物": (18.0, 25.0, 32.0),
    "汽车": (12.0, 16.0, 20.0),
    "环保": (12.0, 18.0, 24.0),
    "公用事业": (9.0, 13.0, 17.0),
    "通信": (18.0, 26.0, 34.0),
}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def load_recovery_packet() -> dict[str, dict[str, Any]]:
    path = DATA_DIR / "valuation_recovery_601360_000042_20260715.json"
    if not path.exists():
        return {}
    packet = load_json(path)
    return {row["ticker"]: row for row in packet.get("rows", [])}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def probability_value(values: tuple[float, float, float]) -> float:
    return round(sum(value * probability for value, probability in zip(values, PROBABILITIES)), 2)


def action(upside: float, disposition: str) -> str:
    if disposition in {
        "exclude_nonrecurring_dominated",
        "earnings_decline_watch",
        "watch_insufficient_price_history",
    }:
        return "avoid / insufficient valuation quality"
    if upside >= 0.30:
        return "high-upside model candidate / validate before entry"
    if upside >= 0.15:
        return "selective pullback entry / earnings validation"
    if upside >= 0:
        return "market-supported watch / wait for margin of safety"
    if upside >= -0.15:
        return "valuation full / watch only"
    return "high valuation risk / avoid chasing"


def evidence_quality(row: dict[str, Any]) -> str:
    if row.get("q1_revenue_100mn") is None or row.get("current_price") is None:
        return "low"
    if row.get("local_pdf"):
        return "high"
    return "medium-low"


def legacy_evidence_quality(row: dict[str, Any]) -> str:
    if row.get("q1_revenue_100mn") is None or row.get("current_price") is None:
        return "low"
    if row.get("report_status") == "current" and row.get("local_pdf"):
        return "high" if row.get("target_price") is not None else "medium-high"
    if row.get("report_status") in {"aging", "stale"} and row.get("local_pdf"):
        return "medium"
    return "medium-low"


def evidence_quality_basis(row: dict[str, Any]) -> str:
    if row.get("q1_revenue_100mn") is None or row.get("current_price") is None:
        return "missing current price or Q1 financial packet"
    if row.get("local_pdf"):
        return (
            "official H1 preview + Q1 financial packet + current quote/K-line + "
            "archived original broker PDF; broker-anchor usability is governed separately"
        )
    return "official H1 preview + Q1 financial packet + current quote/K-line; broker evidence unavailable"


def valuation_method(row: dict[str, Any]) -> tuple[str, tuple[float, float, float]]:
    industry = row["sws_industry"]
    if industry in FINANCIAL and row.get("q1_bps"):
        return "PB-ROE and earnings blended range", (8.0, 11.0, 14.0)
    if industry in CYCLICAL:
        return "cycle-adjusted deducted-EPS PE", PE_RANGES.get(industry, (10.0, 14.0, 18.0))
    if industry in GROWTH:
        return "growth-earnings scenario PE", PE_RANGES.get(industry, (16.0, 22.0, 28.0))
    return "deducted-EPS scenario PE", PE_RANGES.get(industry, (12.0, 18.0, 24.0))


def denominator_block_reason(row: dict[str, Any]) -> str | None:
    preview_type = str(row.get("preview_type") or "")
    industry = str(row.get("sws_industry") or "")
    yoy = row.get("parent_np_yoy_midpoint_pct")
    if preview_type == "扭亏":
        return "低基数扭亏：H1正利润不能直接年化为稳定盈利分母"
    if industry == "房地产" and yoy is not None and float(yoy) >= 200:
        return "房地产结算型高增长：竣工交付与项目结算可能造成利润期间性集中"
    return None


def recovery_model(row: dict[str, Any], recovery: dict[str, Any]) -> dict[str, Any]:
    current = float(row["current_price"])
    market_cap = float(row["total_market_cap_100mn"])
    shares = market_cap / current
    alternative = recovery["alternative_method"]
    fair_value = alternative["fair_value"]
    probabilities = recovery.get("scenario_probabilities", {"bear": 0.30, "base": 0.50, "bull": 0.20})
    house_value = round(
        fair_value["bear"] * probabilities["bear"]
        + fair_value["base"] * probabilities["base"]
        + fair_value["bull"] * probabilities["bull"],
        2,
    )
    public_consensus = recovery.get("public_consensus_anchor") or {}
    direct_anchor = recovery.get("direct_broker_anchor") or {}
    public_anchor = public_consensus.get("target_average")
    direct_target = direct_anchor.get("target_price")
    direct_weight = float(direct_anchor.get("valuation_weight") or 0.0)
    anchor_target = direct_target if direct_target is not None else public_anchor
    anchor_weight = direct_weight if direct_target is not None else (
        float(recovery.get("consensus_weight") or 0.10)
        if public_anchor is not None
        else 0.0
    )
    report_pdf_source = row.get("local_pdf")
    target_source_gap = None
    if direct_target is None and public_anchor is None:
        target_source_gap = (
            "原始研报已归档但未披露目标价/合理价值区间"
            if report_pdf_source
            else "未取得本地原始研报证据路径"
        )
    final_target = round(
        house_value * (1 - anchor_weight)
        + (anchor_target or house_value) * anchor_weight,
        2,
    )
    quality = (
        "high"
        if any(source for source in (
            direct_anchor.get("source_path"),
            public_consensus.get("source_path"),
            (recovery.get("earnings_consensus") or {}).get("source_path"),
            (recovery.get("peer_metrics") or {}).get("source_path"),
            report_pdf_source,
        ))
        else evidence_quality(row)
    )
    return {
        "ticker": row["ticker"],
        "company": row["company"],
        "industry": row["sws_industry"],
        "disposition": row["full_market_disposition"],
        "model_tier": "recovery_conditional_model",
        "valuation_status": "conditional recovery model; not a formal rating",
        "current_price": current,
        "price_display": f"{current:.2f}元",
        "price_date": DATA_CUTOFF,
        "shares_100mn": round(shares, 4),
        "market_cap_100mn": market_cap,
        "h1_parent_np_100mn": row.get("h1_parent_np_midpoint_100mn"),
        "h1_deducted_np_100mn": row.get("h1_deducted_np_midpoint_100mn"),
        "h1_deducted_eps": round(float(row["h1_deducted_np_midpoint_100mn"]) / shares, 4),
        "method": alternative["primary"],
        "multiples": alternative.get("multiples"),
        "bear": fair_value["bear"],
        "base": fair_value["base"],
        "bull": fair_value["bull"],
        "target_low": fair_value["bear"],
        "target_high": fair_value["bull"],
        "probabilities": probabilities,
        "probability_weights": probabilities,
        "house_probability_value": house_value,
        "external_target": direct_target if direct_target is not None else public_anchor,
        "external_weight": anchor_weight,
        "external_source": (
            direct_anchor.get("source_path")
            if direct_target is not None
            else public_consensus.get("source_path")
        ),
        "report_pdf_source": report_pdf_source,
        "target_source_gap": target_source_gap,
        "external_quality": (
            direct_anchor.get("source_quality")
            if direct_target is not None
            else public_consensus.get("source_quality", "house_only_recovery")
        ),
        "public_consensus_anchor": public_anchor,
        "public_consensus_weight": anchor_weight if direct_target is None else 0.0,
        "direct_broker_weight": direct_weight,
        "recovery_anchor_type": (
            "direct_broker_anchor"
            if direct_target is not None
            else "public_consensus_anchor"
            if public_anchor is not None
            else "house_only_recovery"
        ),
        "market_weight": 0.0,
        "final_target_weights": {
            "house_probability_value": round(1 - anchor_weight, 4),
            "external_target": anchor_weight if direct_target is not None else 0.0,
            "public_consensus_anchor": anchor_weight if direct_target is None else 0.0,
            "market_implied_anchor": 0.0,
        },
        "probability_target": final_target,
        "target_display": f"{final_target:.0f}元",
        "upside": round(final_target / current - 1, 4),
        "upside_display": f"{final_target / current - 1:.1%}",
        "bubble_degree_vs_base": round(current / fair_value["base"] - 1, 4),
        "action": action(round(final_target / current - 1, 4), row["full_market_disposition"]),
        "evidence_quality": quality,
        "legacy_evidence_quality": legacy_evidence_quality(row),
        "evidence_quality_basis": recovery.get("evidence_quality_basis")
        or evidence_quality_basis(row),
        "broker_anchor_quality": (
            "current_auditable_direct_anchor"
            if direct_target is not None and direct_weight > 0
            else "auditable_public_consensus_anchor"
            if public_anchor is not None
            else "no_positive_external_anchor"
        ),
        "formal_anchor_eligible": bool(direct_target is not None and direct_weight > 0),
        "latest_broker": row.get("latest_broker"),
        "latest_report_date": row.get("latest_report_date"),
        "latest_2026e_eps": (recovery.get("earnings_consensus") or {}).get("eps_2026_mean")
        or (recovery.get("public_consensus_anchor") or {}).get("eps_2026"),
        "q1_ocf_100mn": row.get("q1_ocf_100mn"),
        "valuation_recovery_status": recovery["valuation_recovery_status"],
        "recovery_confidence": recovery["confidence"],
        "recovery_peer_set": recovery.get("peer_set", []),
        "market_implied_metric": recovery.get("market_implied_metric"),
        "normalized_denominator": recovery.get("normalized_denominator"),
        "recovery_scenario_range": recovery.get("scenario_range"),
        "recovery_upgrade_trigger": recovery.get("upgrade_trigger"),
        "recovery_downgrade_trigger": recovery.get("downgrade_trigger"),
        "recovery_evidence_sources": [
            direct_anchor.get("source_path"),
            public_consensus.get("source_path"),
            (recovery.get("earnings_consensus") or {}).get("source_path"),
            (recovery.get("peer_metrics") or {}).get("source_path"),
            recovery.get("alternative_method", {}).get("source"),
        ],
        "catalyst": recovery.get("upgrade_trigger"),
        "invalidation": recovery.get("downgrade_trigger"),
        "next_quarter_threshold": recovery.get("upgrade_trigger"),
        "evidence_sources": ["data/valuation_recovery_601360_000042_20260715.json"],
        "checked_sources": "official H1 preview, Q1 financial packet, current quote/K-line, public consensus, peer method and market-implied metrics",
        "proxy_evidence": recovery.get("normalized_denominator"),
        "valuation_consequence": "Conditional recovery range; not formal Street valuation and not a guaranteed target.",
        "evidence_gap": None,
    }


def generic_model(row: dict[str, Any], recovery_packet: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    recovery = (recovery_packet or {}).get(row["ticker"])
    if recovery:
        return recovery_model(row, recovery)
    current = row.get("current_price")
    market_cap = row.get("total_market_cap_100mn")
    if not current or not market_cap:
        listing_status = (
            "未上市；发行价8.66元，暂无二级市场当前价"
            if row["ticker"] == "688825"
            else "有效当前价或市值不可用"
        )
        return {
            "ticker": row["ticker"],
            "company": row["company"],
            "industry": row["sws_industry"],
            "disposition": row["full_market_disposition"],
            "model_tier": "not_priceable",
            "valuation_status": "not priceable / valid current market price unavailable",
            "current_price": current,
            "price_display": listing_status,
            "probability_target": None,
            "target_low": None,
            "target_high": None,
            "upside": None,
            "target_display": "不适用；待上市交易",
            "upside_display": "不适用",
            "action": "not priceable",
            "evidence_quality": "low",
            "legacy_evidence_quality": "low",
            "evidence_quality_basis": listing_status,
            "broker_anchor_quality": "not_priceable",
            "formal_anchor_eligible": False,
            "evidence_gap": listing_status,
        }
    shares = float(market_cap) / float(current)
    h1_parent = row.get("h1_parent_np_midpoint_100mn")
    h1_deducted = row.get("h1_deducted_np_midpoint_100mn")
    denominator = h1_deducted if h1_deducted is not None and h1_deducted > 0 else h1_parent
    h1_eps = float(denominator) / shares if denominator and shares else None
    if h1_eps is None:
        return {
            "ticker": row["ticker"],
            "company": row["company"],
            "industry": row["sws_industry"],
            "disposition": row["full_market_disposition"],
            "model_tier": "not_priceable",
            "valuation_status": "positive H1 denominator unavailable",
            "current_price": current,
            "price_display": f"{current:.2f}元",
            "probability_target": None,
            "target_low": None,
            "target_high": None,
            "upside": None,
            "target_display": "条件性估值未建立",
            "upside_display": "暂不计算",
            "action": "not priceable / wait for positive denominator",
            "evidence_quality": evidence_quality(row),
            "legacy_evidence_quality": legacy_evidence_quality(row),
            "evidence_quality_basis": evidence_quality_basis(row),
            "broker_anchor_quality": "positive_denominator_unavailable",
            "formal_anchor_eligible": False,
            "evidence_gap": "positive H1 deducted-profit or parent-profit denominator unavailable",
        }
    block_reason = denominator_block_reason(row)
    if block_reason:
        annualized_eps = h1_eps * 2.0
        current_implied_pe = float(current) / annualized_eps if annualized_eps > 0 else None
        return {
            "ticker": row["ticker"],
            "company": row["company"],
            "industry": row["sws_industry"],
            "disposition": row["full_market_disposition"],
            "model_tier": "not_priceable_low_base_or_settlement",
            "valuation_status": "watchlist only / low-base or settlement denominator not reliable",
            "current_price": current,
            "price_date": DATA_CUTOFF,
            "shares_100mn": round(shares, 4),
            "market_cap_100mn": market_cap,
            "h1_parent_np_100mn": h1_parent,
            "h1_deducted_np_100mn": h1_deducted,
            "h1_deducted_eps": round(h1_eps, 4),
            "annualized_h1_deducted_eps_proxy": round(annualized_eps, 4),
            "current_implied_pe_on_h1_annualized": round(current_implied_pe, 2)
            if current_implied_pe is not None
            else None,
            "probability_target": None,
            "target_low": None,
            "target_high": None,
            "upside": None,
            "action": "watchlist only / insufficient evidence",
            "evidence_quality": evidence_quality(row),
            "legacy_evidence_quality": legacy_evidence_quality(row),
            "evidence_quality_basis": evidence_quality_basis(row),
            "broker_anchor_quality": "denominator_blocked",
            "formal_anchor_eligible": False,
            "valuation_block_reason": block_reason,
            "evidence_gap": block_reason,
            "catalyst": "verified recurring earnings, cash conversion and a matched NAV/PE/PS valuation method",
            "invalidation": "H1 profit proves non-recurring, settlement timing reverses or cash conversion remains weak",
            "checked_sources": "official H1 preview, Q1 financial packet, current quote/K-line and latest broker metadata",
            "valuation_consequence": "Do not publish a PE probability target until the denominator is recurring or a matched asset/revenue model is built.",
        }
    if row["sws_industry"] in CYCLICAL:
        h2_ratios = (0.55, 0.85, 1.15)
    elif row["sws_industry"] in FINANCIAL:
        h2_ratios = (0.70, 1.00, 1.25)
    elif row["sws_industry"] in GROWTH:
        h2_ratios = (0.70, 1.00, 1.30)
    else:
        h2_ratios = (0.65, 0.90, 1.20)
    if row["sector_stage"] in {"launch_confirmation", "flow_watch"}:
        h2_ratios = (h2_ratios[0], h2_ratios[1] + 0.05, h2_ratios[2] + 0.10)
    eps_values = [h1_eps * (1 + ratio) for ratio in h2_ratios]
    if row.get("latest_2026e_eps") and row.get("report_status") in {"current", "aging"}:
        eps_values[1] = max(eps_values[1], float(row["latest_2026e_eps"]))
    method, multiples = valuation_method(row)
    if row["sws_industry"] in FINANCIAL and row.get("q1_bps"):
        pb_values = [float(row["q1_bps"]) * multiple for multiple in (0.75, 1.05, 1.35)]
        pe_values = [eps_values[index] * multiples[index] for index in range(3)]
        values = [pb_values[index] * 0.65 + pe_values[index] * 0.35 for index in range(3)]
    else:
        values = [eps_values[index] * multiples[index] for index in range(3)]
    scenario_values_before_bear_cap = [round(value, 2) for value in values]
    values = sorted(scenario_values_before_bear_cap)
    bear_cap = round(float(current) * 0.75, 2)
    values[0] = round(min(values[0], bear_cap), 2)
    house_value = probability_value(tuple(values))
    external_target = row.get("target_price")
    external_weight = (
        0.10
        if external_target and row.get("report_status") == "current"
        else 0.0
    )
    final_target = round(house_value * (1 - external_weight) + (external_target or house_value) * external_weight, 2)
    upside = round(final_target / float(current) - 1, 4)
    return {
        "ticker": row["ticker"],
        "company": row["company"],
        "industry": row["sws_industry"],
        "disposition": row["full_market_disposition"],
        "model_tier": "screening_house_range",
        "valuation_status": "priceable screening range; not a formal rating",
        "current_price": current,
        "price_display": f"{current:.2f}元",
        "target_display": f"{final_target:.0f}元",
        "upside_display": f"{upside:.1%}",
        "price_date": DATA_CUTOFF,
        "shares_100mn": round(shares, 4),
        "market_cap_100mn": market_cap,
        "h1_parent_np_100mn": h1_parent,
        "h1_deducted_np_100mn": h1_deducted,
        "h1_deducted_eps": round(h1_eps, 4),
        "forecast_eps_bear": round(eps_values[0], 4),
        "forecast_eps_base": round(eps_values[1], 4),
        "forecast_eps_bull": round(eps_values[2], 4),
        "h2_conversion_ratios": {
            "bear": h2_ratios[0],
            "base": h2_ratios[1],
            "bull": h2_ratios[2],
        },
        "scenario_eps": {
            "bear": round(eps_values[0], 4),
            "base": round(eps_values[1], 4),
            "bull": round(eps_values[2], 4),
        },
        "method": method,
        "multiples": multiples,
        "scenario_values_before_bear_cap": scenario_values_before_bear_cap,
        "bear_cap_at_75pct_current_price": bear_cap,
        "bear": values[0],
        "base": values[1],
        "bull": values[2],
        "probabilities": {"bear": 0.30, "base": 0.50, "bull": 0.20},
        "house_probability_value": house_value,
        "probability_weights": {
            "bear": PROBABILITIES[0],
            "base": PROBABILITIES[1],
            "bull": PROBABILITIES[2],
        },
        "external_target": external_target,
        "external_weight": external_weight,
        "external_source": row.get("local_pdf") if external_target else None,
        "report_pdf_source": row.get("local_pdf"),
        "target_source_gap": None
        if external_target
        else (
            "原始研报已归档但未披露目标价/合理价值区间"
            if row.get("local_pdf")
            else "未取得本地原始研报证据路径"
        ),
        "external_quality": "auditable_broker_pdf" if external_target else "not_disclosed_or_zero_weight",
        "target_low": values[0],
        "probability_target": final_target,
        "final_target_weights": {
            "house_probability_value": round(1.0 - external_weight, 4),
            "external_target": round(external_weight, 4),
        },
        "target_high": values[2],
        "upside": upside,
        "bubble_degree_vs_base": round(float(current) / values[1] - 1, 4),
        "action": action(upside, row["full_market_disposition"]),
        "evidence_quality": evidence_quality(row),
        "legacy_evidence_quality": legacy_evidence_quality(row),
        "evidence_quality_basis": evidence_quality_basis(row),
        "broker_anchor_quality": (
            "current_auditable_target"
            if external_target and row.get("report_status") == "current"
            else "stale_or_aging_target_zero_to_low_weight"
            if external_target
            else "original_pdf_no_target_or_not_disclosed"
            if row.get("local_pdf")
            else "broker_pdf_unavailable"
        ),
        "formal_anchor_eligible": bool(
            external_target and row.get("report_status") == "current"
        ),
        "latest_broker": row.get("latest_broker"),
        "latest_report_date": row.get("latest_report_date"),
        "latest_2026e_eps": row.get("latest_2026e_eps"),
        "q1_ocf_100mn": row.get("q1_ocf_100mn"),
        "report_vs_preview": row.get("report_vs_preview"),
        "catalyst": "H1 deducted-profit delivery, H2 conversion and current-price re-rating",
        "invalidation": "H2 profit, cash flow or deducted-profit quality misses the bridge",
        "evidence_sources": [
            "data/full_market_valuation_evidence_20260715.json",
            row.get("local_pdf"),
        ],
        "checked_sources": "official H1 preview, Q1 financial packet, current quote/K-line and latest broker metadata",
        "proxy_evidence": "H1 deducted-profit purity, Q1 cash flow, H2 calibration and price position",
        "valuation_consequence": "Screening range only; no formal rating.",
        "evidence_gap": None,
    }


def formal_model(row: dict[str, Any], generic: dict[str, Any], is_formal: bool = True) -> dict[str, Any]:
    result = dict(generic)
    if not is_formal:
        result["formal_review_status"] = "priority validation candidate; independent review required"
        return result
    if generic.get("model_tier") == "not_priceable_low_base_or_settlement":
        result["formal_review_status"] = "blocked denominator; watchlist only"
        result["formal_pool_candidate"] = False
        result["market_cap_100mn_cny"] = result.get("market_cap_100mn")
        result["revenue_2026e_100mn"] = None
        result["np_2026e_100mn"] = None
        result["eps_2026e"] = None
        result["market_implied_anchor"] = result.get("current_price")
        result["fundamental_weight"] = 0.0
        result["market_weight"] = 0.0
        result["broker_weight"] = 0.0
        result["broker_anchor"] = None
        result["scenario_expected_value"] = None
        result["final_target"] = None
        result["next_quarter_threshold"] = (
            "Recurring profit, cash conversion and a matched valuation denominator must be established"
        )
        return result
    result["model_tier"] = "formal_current_price_model"
    result["valuation_status"] = "formal current-price-based model from refreshed evidence"
    result["action"] = result["action"].replace("screening", "formal")
    result["formal_review_status"] = "formal pool candidate; independent IC review required"
    result["market_cap_100mn_cny"] = result.get("market_cap_100mn")
    result["revenue_2026e_100mn"] = None
    result["np_2026e_100mn"] = (
        result.get("forecast_eps_base", 0) * result.get("shares_100mn", 0)
        if result.get("forecast_eps_base") is not None
        else None
    )
    result["eps_2026e"] = result.get("forecast_eps_base")
    result["market_implied_anchor"] = result.get("current_price")
    result["fundamental_weight"] = 1.0 - float(result.get("external_weight") or 0)
    result["market_weight"] = 0.0
    result["broker_weight"] = float(result.get("external_weight") or 0)
    result["broker_anchor"] = result.get("external_target")
    result["scenario_expected_value"] = result.get("house_probability_value")
    result["final_target"] = result.get("probability_target")
    result["next_quarter_threshold"] = (
        "H2 deducted profit, operating cash flow and refreshed broker denominator remain on track"
    )
    result["scenario_assumptions"] = {
        "bear": "H2 conversion and valuation multiple compress; current-price downside is explicit.",
        "base": "H1 deducted profit converts through the industry-calibrated H2 bridge.",
        "bull": "H2 conversion, cash flow and current broker denominator remain supportive.",
    }
    return result


def formal_exclusion_reasons(row: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    if row.get("valuation_block_reason"):
        reasons.append(str(row["valuation_block_reason"]))
    if row.get("evidence_quality") != "high":
        reasons.append("基础证据链不足以支持正式模型")
    if not row.get("formal_anchor_eligible"):
        reasons.append("缺少当前可正权使用的外部估值锚")
    if row.get("disposition") in {"exclude_nonrecurring_dominated", "earnings_decline_watch"}:
        reasons.append("盈利质量或业绩方向不满足正式模型")
    if not row.get("latest_report_date") or row.get("latest_report_date") < "2026-04-01":
        reasons.append("最新研报缺失或早于2026-04-01")
    if row.get("external_target") is None:
        if row.get("report_pdf_source"):
            reasons.append("原始研报已归档但未披露目标价/合理价值区间")
        else:
            reasons.append("公开源检索未取得可审计外部目标价/合理价值区间")
            reasons.append("公开源检索未取得本地原始研报证据路径")
    if row.get("upside") is not None and row["upside"] < 0:
        reasons.append("概率目标低于当前价，仅保留为下行风险对照")
    return reasons


def build_formal_selection_bridge(
    priority_models: list[dict[str, Any]], formal: list[dict[str, Any]]
) -> dict[str, Any]:
    formal_codes = {row["ticker"] for row in formal}
    rows: list[dict[str, Any]] = []
    for row in priority_models:
        reasons = formal_exclusion_reasons(row)
        if row["ticker"] in formal_codes:
            status = "formal_audit_model"
            reasons = (
                ["正式模型：当前价格、情景估值、外部锚和原始研报证据均可复核"]
                if row.get("upside", 0) >= 0
                else ["正式下行风险对照：证据链完整，但概率目标低于当前价"]
            )
        elif row.get("upside") is not None and row["upside"] >= 0.15:
            status = "conditional_high_upside_watch"
        elif row.get("upside") is not None and row["upside"] >= 0:
            status = "conditional_margin_watch"
        else:
            status = "valuation_risk_or_watch"
        rows.append(
            {
                "ticker": row["ticker"],
                "company": row["company"],
                "industry": row["industry"],
                "current_price": row.get("current_price"),
                "probability_target": row.get("probability_target"),
                "upside": row.get("upside"),
                "evidence_quality": row.get("evidence_quality"),
                "latest_report_date": row.get("latest_report_date"),
                "external_target": row.get("external_target"),
                "external_source": row.get("external_source"),
                "report_pdf_source": row.get("report_pdf_source"),
                "target_source_gap": row.get("target_source_gap"),
                "disposition": row.get("disposition"),
                "selection_status": status,
                "selection_reasons": reasons,
                "action": row.get("action"),
            }
        )
    return {
        "schema_version": "astock.formal_selection_bridge.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "priority_count": len(rows),
        "formal_count": len(formal),
        "formal_tickers": sorted(formal_codes),
        "status_counts": {
            status: sum(row["selection_status"] == status for row in rows)
            for status in sorted({row["selection_status"] for row in rows})
        },
        "rows": rows,
    }


def high_upside_selection_audit(
    candidate_models: list[dict[str, Any]],
    priority_models: list[dict[str, Any]],
    formal: list[dict[str, Any]],
    threshold: float = 1.0,
) -> dict[str, Any]:
    priority_codes = {row["ticker"] for row in priority_models}
    formal_codes = {row["ticker"] for row in formal}
    allowed_priority_dispositions = {
        "quiet_accumulation_priority",
        "low_position_earnings_priority",
        "launched_with_runway_candidate",
    }
    rows: list[dict[str, Any]] = []
    for row in sorted(
        (
            item for item in candidate_models
            if item.get("upside") is not None and item["upside"] >= threshold
        ),
        key=lambda item: item["upside"],
        reverse=True,
    ):
        reasons: list[str] = []
        if row["ticker"] not in priority_codes:
            reasons.append(
                "未进入39只优先池：当前处置为"
                f"{row.get('disposition')}，优先池仅接收"
                + "/".join(sorted(allowed_priority_dispositions))
            )
        reasons.extend(formal_exclusion_reasons(row))
        if row["ticker"] in formal_codes:
            status = "formal_model"
            reasons = ["已进入正式模型；高空间同时通过证据、时效和外部锚门槛"]
        elif row["ticker"] in priority_codes:
            status = "priority_high_upside_not_formal"
        else:
            status = "candidate_high_upside_not_priority"
        upgrade_evidence: list[str] = []
        if row["ticker"] not in priority_codes:
            upgrade_evidence.append("先重新进入优先池：价格位置、行业阶段或处置标签需满足优先池规则")
        if row.get("latest_report_date") is None or row.get("latest_report_date") < "2026-04-01":
            upgrade_evidence.append("补齐2026-04-01之后的原始券商研报或可审计共识快照")
        if row.get("external_target") is None:
            upgrade_evidence.append("补齐当前可审计目标价/合理价值区间，摘要、转载和用户估值不计入正权重")
        if row.get("evidence_quality") != "high":
            upgrade_evidence.append("补齐基础证据链：当前PDF、目标字段、分母和来源路径需可复核")
        if not row.get("formal_anchor_eligible"):
            upgrade_evidence.append("补齐可正权使用的当前外部估值锚")
        if row.get("q1_ocf_100mn") is not None and row["q1_ocf_100mn"] <= 0:
            upgrade_evidence.append("验证经营现金流改善，避免利润空间仅来自会计分母")
        if not upgrade_evidence:
            upgrade_evidence.append("等待H2扣非利润、现金流和外部锚同步更新后复核")
        rows.append(
            {
                "ticker": row["ticker"],
                "company": row["company"],
                "industry": row["industry"],
                "current_price": row.get("current_price"),
                "probability_target": row.get("probability_target"),
                "upside": row.get("upside"),
                "evidence_quality": row.get("evidence_quality"),
                "latest_report_date": row.get("latest_report_date"),
                "latest_broker": row.get("latest_broker"),
                "external_target": row.get("external_target"),
                "external_source": row.get("external_source"),
                "report_pdf_source": row.get("report_pdf_source"),
                "disposition": row.get("disposition"),
                "model_tier": row.get("model_tier"),
                "q1_ocf_100mn": row.get("q1_ocf_100mn"),
                "legacy_evidence_quality": row.get("legacy_evidence_quality"),
                "evidence_quality_basis": row.get("evidence_quality_basis"),
                "broker_anchor_quality": row.get("broker_anchor_quality"),
                "formal_anchor_eligible": row.get("formal_anchor_eligible"),
                "in_priority_pool": row["ticker"] in priority_codes,
                "in_formal_pool": row["ticker"] in formal_codes,
                "selection_status": status,
                "hard_gate_reasons": list(dict.fromkeys(reasons)),
                "required_upgrade_evidence": list(dict.fromkeys(upgrade_evidence)),
            }
        )
    return {
        "schema_version": "astock.high_upside_selection_audit.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "upside_threshold": threshold,
        "row_count": len(rows),
        "formal_count": sum(row["in_formal_pool"] for row in rows),
        "priority_count": sum(row["in_priority_pool"] for row in rows),
        "not_priority_count": sum(not row["in_priority_pool"] for row in rows),
        "status_counts": {
            status: sum(row["selection_status"] == status for row in rows)
            for status in sorted({row["selection_status"] for row in rows})
        },
        "rows": rows,
    }


def high_upside_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# High-Upside Selection Audit Through 2026-07-15",
        "",
        f"- Upside threshold: {payload['upside_threshold']:.0%}",
        f"- Rows: {payload['row_count']}",
        f"- In priority pool: {payload['priority_count']}",
        f"- In formal pool: {payload['formal_count']}",
        "",
        "| Ticker | Company | Upside | Priority | Formal | Evidence | Latest report | External target | Why not formal | Required upgrade evidence |",
        "|---|---|---:|---|---|---|---|---:|---|---|",
    ]
    for row in payload["rows"]:
        latest = row.get("latest_report_date") or "not found"
        target = row.get("external_target")
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['upside']:.1%} | "
            f"{'Y' if row['in_priority_pool'] else 'N'} | "
            f"{'Y' if row['in_formal_pool'] else 'N'} | "
            f"{row.get('evidence_quality')} | {latest} | "
            f"{target if target is not None else 'not disclosed'} | "
            f"{'; '.join(row['hard_gate_reasons'])} | "
            f"{'; '.join(row['required_upgrade_evidence'])} |"
        )
    return "\n".join(lines)


def former_medium_candidate_admission(
    candidate_models: list[dict[str, Any]],
    priority_models: list[dict[str, Any]],
    formal: list[dict[str, Any]],
    selection_bridge: dict[str, Any],
) -> dict[str, Any]:
    priority_codes = {row["ticker"] for row in priority_models}
    formal_codes = {row["ticker"] for row in formal}
    bridge_map = {row["ticker"]: row for row in selection_bridge["rows"]}
    rows: list[dict[str, Any]] = []
    for row in sorted(
        (item for item in candidate_models if item.get("legacy_evidence_quality") == "medium"),
        key=lambda item: item.get("upside") if item.get("upside") is not None else -999,
        reverse=True,
    ):
        bridge = bridge_map.get(row["ticker"], {})
        if row["ticker"] in formal_codes:
            admission_status = "formal_model_candidate"
            admission_label = "正式模型候选"
            admission_decision = "进入正式模型池"
        elif bridge.get("selection_status") == "conditional_high_upside_watch":
            admission_status = "priority_event_validation_candidate"
            admission_label = "优先验证候选"
            admission_decision = "进入优先验证候选池"
        elif bridge.get("selection_status") == "conditional_margin_watch":
            admission_status = "priority_margin_watch"
            admission_label = "安全边际观察"
            admission_decision = "进入观察候选池"
        elif bridge.get("selection_status") == "valuation_risk_or_watch":
            admission_status = "priority_valuation_risk_watch"
            admission_label = "估值风险观察"
            admission_decision = "保留监控，不新增为候选"
        elif row.get("upside") is not None and row["upside"] >= 0.15 and row.get("evidence_quality") == "high":
            admission_status = "expanded_event_validation_candidate"
            admission_label = "扩展事件验证候选"
            admission_decision = "可进入扩展观察候选池"
        elif row.get("upside") is not None and row["upside"] >= 0 and row.get("evidence_quality") == "high":
            admission_status = "expanded_watch_candidate"
            admission_label = "扩展观察候选"
            admission_decision = "可进入低优先级观察"
        else:
            admission_status = "not_admitted"
            admission_label = "暂不纳入"
            admission_decision = "暂不进入新增候选"
        blockers = list(bridge.get("selection_reasons") or [])
        if not row.get("formal_anchor_eligible"):
            blockers.append("缺少当前可正权使用的外部估值锚")
        if row.get("q1_ocf_100mn") is not None and row["q1_ocf_100mn"] <= 0:
            blockers.append("经营现金流仍需验证")
        if row.get("upside") is not None and row["upside"] < 0:
            blockers.append("概率目标低于现价")
        rows.append(
            {
                "ticker": row["ticker"],
                "company": row["company"],
                "industry": row["industry"],
                "admission_status": admission_status,
                "admission_label": admission_label,
                "admission_decision": admission_decision,
                "in_priority_pool": row["ticker"] in priority_codes,
                "in_formal_pool": row["ticker"] in formal_codes,
                "current_price": row.get("current_price"),
                "probability_target": row.get("probability_target"),
                "upside": row.get("upside"),
                "evidence_quality": row.get("evidence_quality"),
                "legacy_evidence_quality": row.get("legacy_evidence_quality"),
                "broker_anchor_quality": row.get("broker_anchor_quality"),
                "formal_anchor_eligible": row.get("formal_anchor_eligible"),
                "latest_report_date": row.get("latest_report_date"),
                "external_target": row.get("external_target"),
                "q1_ocf_100mn": row.get("q1_ocf_100mn"),
                "action": row.get("action"),
                "blockers": list(dict.fromkeys(blockers)),
                "upgrade_trigger": row.get("next_quarter_threshold")
                or row.get("catalyst")
                or "H2扣非利润、现金流与外部估值锚同步验证",
            }
        )
    return {
        "schema_version": "astock.former_medium_candidate_admission.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(rows),
        "admitted_count": sum(
            row["admission_status"]
            in {
                "formal_model_candidate",
                "priority_event_validation_candidate",
                "priority_margin_watch",
                "expanded_event_validation_candidate",
                "expanded_watch_candidate",
            }
            for row in rows
        ),
        "not_admitted_count": sum(row["admission_status"] == "not_admitted" for row in rows),
        "status_counts": {
            status: sum(row["admission_status"] == status for row in rows)
            for status in sorted({row["admission_status"] for row in rows})
        },
        "rows": rows,
    }


def former_medium_admission_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Former Medium Evidence Candidate Admission Audit Through 2026-07-15",
        "",
        f"- Rows: {payload['row_count']}",
        f"- Admitted to candidate/watch pools: {payload['admitted_count']}",
        f"- Not admitted: {payload['not_admitted_count']}",
        "",
        "| Ticker | Company | Admission | Upside | Broker anchor | Formal eligible | Decision | Blockers |",
        "|---|---|---|---:|---|---|---|---|",
    ]
    for row in payload["rows"]:
        upside = "not calculated" if row.get("upside") is None else f"{row['upside']:.1%}"
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['admission_label']} | "
            f"{upside} | {row.get('broker_anchor_quality')} | "
            f"{row.get('formal_anchor_eligible')} | {row['admission_decision']} | "
            f"{'; '.join(row.get('blockers') or [])} |"
        )
    return "\n".join(lines)


def markdown(title: str, rows: list[dict[str, Any]]) -> str:
    lines = [f"# {title}", "", f"- Data cutoff: {DATA_CUTOFF}", f"- Rows: {len(rows)}", "",
             "| Ticker | Company | Industry | Price | Bear | Base | Bull | Target | Upside | Action | Evidence |",
             "|---|---|---|---:|---:|---:|---:|---:|---:|---|---|"]
    for row in rows:
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['industry']} | "
            f"{row.get('current_price', '-')} | {row.get('bear', '-')} | "
            f"{row.get('base', '-')} | {row.get('bull', '-')} | "
            f"{row.get('probability_target', '-')} | {row.get('upside', '-'):.1%} | "
            f"{row.get('action')} | {row.get('evidence_quality')} |"
            if row.get("upside") is not None
            else f"| {row['ticker']} | {row['company']} | {row['industry']} | - | - | - | - | - | - | {row.get('action')} | {row.get('evidence_quality')} |"
        )
    return "\n".join(lines)


def main() -> None:
    evidence = load_json(DATA_DIR / "full_market_valuation_evidence_20260715.json")
    candidate_pool = load_json(DATA_DIR / "full_market_candidates_20260715.json")
    priority_pool = load_json(DATA_DIR / "full_market_priority_pool_20260715.json")["rows"]
    evidence_map = {row["ticker"]: row for row in evidence["rows"]}
    priority_codes = {row["ticker"] for row in priority_pool}
    recovery_packet = load_recovery_packet()
    candidate_models = [
        generic_model(evidence_map[row["ticker"]], recovery_packet)
        for row in candidate_pool["rows"]
    ]
    candidate_map = {row["ticker"]: row for row in candidate_models}
    priority_models = [
        formal_model(candidate_map[row["ticker"]], candidate_map[row["ticker"]], False)
        for row in priority_pool
        if row["ticker"] in candidate_map
    ]
    priority_models.sort(key=lambda row: row.get("upside") if row.get("upside") is not None else -999, reverse=True)
    formal_candidates = [
        row for row in priority_models
        if row.get("upside") is not None
        and row.get("evidence_quality") == "high"
        and row.get("disposition") not in {"exclude_nonrecurring_dominated", "earnings_decline_watch"}
        and row.get("latest_report_date")
        and row.get("latest_report_date") >= "2026-04-01"
        and row.get("external_target") is not None
        and row.get("external_source")
        and row.get("formal_anchor_eligible")
    ]
    formal_generic = formal_candidates[:5]
    formal = [
        formal_model(row, row, True)
        for row in formal_generic
    ]
    formal_by_ticker = {row["ticker"]: row for row in formal}
    for row in priority_models:
        row["formal_pool_candidate"] = row["ticker"] in {item["ticker"] for item in formal}
        row["formal_selection_reasons"] = formal_exclusion_reasons(row)
        row["formal_selection_status"] = (
            "formal_audit_model"
            if row["formal_pool_candidate"]
            else "conditional_high_upside_watch"
            if row.get("upside") is not None and row["upside"] >= 0.15
            else "conditional_margin_watch"
            if row.get("upside") is not None and row["upside"] >= 0
            else "valuation_risk_or_watch"
        )
        if row["ticker"] in formal_by_ticker:
            row.update(formal_by_ticker[row["ticker"]])
    write_json(DATA_DIR / "full_market_priority_valuation_20260715.json", {
        "schema_version": "astock.full_market_priority_valuation.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(priority_models),
        "formal_pool_count": len(formal),
        "formal_pool_tickers": [row["ticker"] for row in formal],
        "rows": priority_models,
    })
    write_text(DATA_DIR / "full_market_priority_valuation_20260715.md", markdown("Full-Market Priority Valuation Through 2026-07-15", priority_models))
    selection_bridge = build_formal_selection_bridge(priority_models, formal)
    write_json(DATA_DIR / "formal_selection_bridge_20260715.json", selection_bridge)
    write_text(
        DATA_DIR / "formal_selection_bridge_20260715.md",
        "# Formal Model Selection Bridge Through 2026-07-15\n\n"
        f"- Priority pool: {selection_bridge['priority_count']}\n"
        f"- Formal audit models: {selection_bridge['formal_count']}\n"
        + "\n".join(
            f"- {row['ticker']} {row['company']} | {row['selection_status']} | "
            f"upside={row['upside']} | reasons={'; '.join(row['selection_reasons'])}"
            for row in selection_bridge["rows"]
        ),
    )
    high_upside_audit = high_upside_selection_audit(
        candidate_models,
        priority_models,
        formal,
    )
    write_json(DATA_DIR / "high_upside_selection_audit_20260715.json", high_upside_audit)
    write_text(
        DATA_DIR / "high_upside_selection_audit_20260715.md",
        high_upside_markdown(high_upside_audit),
    )
    former_medium_admission = former_medium_candidate_admission(
        candidate_models,
        priority_models,
        formal,
        selection_bridge,
    )
    write_json(
        DATA_DIR / "former_medium_candidate_admission_20260715.json",
        former_medium_admission,
    )
    write_text(
        DATA_DIR / "former_medium_candidate_admission_20260715.md",
        former_medium_admission_markdown(former_medium_admission),
    )
    write_json(DATA_DIR / "full_market_candidate_valuation_20260715.json", {
        "schema_version": "astock.full_market_candidate_valuation.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(candidate_models),
        "priceable_count": sum(row.get("probability_target") is not None for row in candidate_models),
        "not_priceable_count": sum(row.get("probability_target") is None for row in candidate_models),
        "rows": candidate_models,
    })
    write_text(DATA_DIR / "full_market_candidate_valuation_20260715.md", markdown("Full-Market Candidate Valuation Through 2026-07-15", candidate_models))
    # Report-wide refresh currently consists of the full candidate universe; legacy theme names
    # are handled separately by the report builder and are never mixed into the candidate count.
    write_json(DATA_DIR / "report_wide_valuation_ledger_20260715.json", {
        "schema_version": "astock.report_wide_valuation_ledger.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(candidate_models),
        "priceable_count": sum(row.get("probability_target") is not None for row in candidate_models),
        "not_priceable_count": sum(row.get("probability_target") is None for row in candidate_models),
        "rows": candidate_models,
    })
    write_text(DATA_DIR / "report_wide_valuation_ledger_20260715.md", markdown("Report-Wide Valuation Ledger Through 2026-07-15", candidate_models))
    write_json(DATA_DIR / "current_valuation_model_20260715.json", {
        "schema_version": "astock.current_valuation_model.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(formal),
        "rows": formal,
    })
    write_text(DATA_DIR / "current_valuation_model_20260715.md", markdown("Formal Current-Price Valuation Through 2026-07-15", formal))
    print(json.dumps({
        "candidate_models": len(candidate_models),
        "priority_models": len(priority_models),
        "formal_models": len(formal),
        "formal_tickers": [row["ticker"] for row in formal],
        "priceable_candidates": sum(row.get("probability_target") is not None for row in candidate_models),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
