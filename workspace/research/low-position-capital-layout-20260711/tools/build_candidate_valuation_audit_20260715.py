#!/usr/bin/env python3
"""Build a row-level valuation algorithm and evidence audit for every candidate."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = CASE_DIR / "refresh-20260715" / "data"
DATA_CUTOFF = "2026-07-15"
PROBABILITIES = {"bear": 0.30, "base": 0.50, "bull": 0.20}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def fmt(value: Any, digits: int = 2) -> str:
    if value is None:
        return "not disclosed"
    return f"{float(value):.{digits}f}"


def percent(value: Any) -> str:
    if value is None:
        return "not calculated"
    return f"{float(value) * 100:.1f}%"


def source_summary(row: dict[str, Any]) -> str:
    sources = [source for source in row.get("evidence_sources", []) if source]
    broker = row.get("latest_broker")
    report_date = row.get("latest_report_date")
    pieces = [
        "official H1 preview",
        "Q1 financial packet",
        "quote/adjusted K-line",
    ]
    if broker and report_date:
        pieces.append(f"{broker} report {report_date}")
    if sources:
        pieces.append(f"{len(sources)} archived source references")
    return "; ".join(pieces)


def probability_rationale() -> str:
    return (
        "30%/50%/20%是统一筛选先验：基准情景权重最高，同时保留熊市和牛市的实质性下行/上行贡献；"
        "它是House情景权重，不是经过统计估计的客观事件概率。"
    )


def evidence_role(row: dict[str, Any]) -> str:
    target = row.get("external_target")
    weight = float(row.get("external_weight") or 0.0)
    if target is not None and weight > 0:
        anchor = f"外部目标价{fmt(target)}元，赋予正权重{weight:.0%}"
    elif target is not None:
        anchor = f"外部目标价{fmt(target)}元，仅作背景，权重为0"
    else:
        anchor = "没有正权重外部目标锚，House价值不伪装为Street共识"
    return (
        f"官方半年报预告、Q1财务包和行情/K线提供事实输入；研报/来源用于分母或可比背景。"
        f"{anchor}。基础证据质量依据：{row.get('evidence_quality_basis', 'not disclosed')}；"
        f"外部锚状态：{row.get('broker_anchor_quality', 'not disclosed')}。"
    )


def rationale_for_eps_row(row: dict[str, Any], formula_type: str) -> dict[str, str]:
    industry = row.get("industry", "")
    if formula_type == "cycle_adjusted_eps_pe":
        method = (
            f"{industry}盈利受商品价格、运价、价差或利用率周期影响，因此使用周期调整EPS/PE区间，"
            "而不是把某一个季度的PE当作全年估值。H2转换比例用于检验当前周期能否延续。"
        )
        multiple = (
            "熊/基准/牛PE区间是针对该周期业务类型的House假设，不是外部券商目标价；"
            "熊值较低反映周期反转，牛值较高必须由价格、销量和现金流共同确认。"
        )
    elif formula_type == "growth_earnings_scenario_pe":
        method = (
            f"{industry}具有成长或盈利持续期特征，因此模型给盈利桥接配置较高PE区间，"
            "而不是直接给主题收入估值；价格和现金流检查防止把泛化成长叙事直接变成EPS。"
        )
        multiple = (
            "PE区间是House对成长持续期的情景判断；牛市情景要求业绩桥接和经营证据持续，"
            "不是市场一致目标价。"
        )
    else:
        method = (
            "该标的H1扣非利润为正且未触发恢复估值阻断，因此扣非EPS是最透明的筛选分母；"
            "情景桥接避免把一个H1数字直接当作全年点预测。"
        )
        multiple = (
            "PE区间按公司所属行业匹配，表达估值压缩/正常/重估三种情景；"
            "这是House筛选区间，正式升级前仍需当前可审计的Street区间。"
        )
    denominator = (
        "使用H1扣非利润以减少非经常性收益污染；股本由总市值/当前价反推；"
        "H2/H1转换比例是明确的季节性和交付假设，不是机械年化。"
    )
    return {
        "method": method,
        "denominator": denominator,
        "multiples": multiple,
        "probabilities": probability_rationale(),
        "evidence": evidence_role(row),
    }


def rationale_for_financial_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "method": (
            "金融公司主要通过净资产、ROE和盈利质量估值；PB保留资产负债表/ROE锚，"
            "PE提供独立盈利交叉检查，混合使用可以避免只依赖投资收益驱动的单季EPS。"
        ),
        "denominator": (
            "Q1 BPS作为资产分母，H1扣非EPS通过H2情景转换为熊/基准/牛盈利；"
            "这样将资产价值和盈利能力分开处理。"
        ),
        "multiples": (
            "PB 0.75/1.05/1.35倍分别代表资产质量压力/正常/重估；行业PE区间提供盈利交叉检查；"
            "这些是House区间，不是外部目标价。"
        ),
        "probabilities": probability_rationale(),
        "evidence": evidence_role(row),
    }


def rationale_for_recovery_row(row: dict[str, Any]) -> dict[str, str]:
    method_label = row.get("method", "")
    peers = "、".join(row.get("recovery_peer_set", [])) or "业务匹配可比公司"
    market = row.get("market_implied_metric") or {}
    if method_label.startswith("PS ") or method_label.startswith("PS on"):
        method = (
            "EPS暂时过于波动或接近零，因此收入作为主分母，再用公开共识和可比公司进行PS三角验证；"
            f"业务匹配可比包括{peers}。"
        )
    elif "PB" in method_label:
        method = (
            "该业务资产较重或受项目周期影响，因此资产价值/BPS和周期调整盈利比直接年化结算利润更稳定；"
            f"业务匹配可比包括{peers}。"
        )
    else:
        method = (
            "最新H1利润存在低基数、扭亏或周期扭曲，因此先正常化EPS，再套业务匹配PE区间；"
            f"业务匹配可比包括{peers}。"
        )
    denominator = (
        f"正常化分母为：{row.get('normalized_denominator')}；"
        "H1机械年化指标只作为市场隐含压力测试，不作为最终目标价分母。"
    )
    multiple = (
        "熊/基准/牛倍数分别表达下行、正常兑现和上行重估；"
        f"区间通过可比方法和当前价格隐含指标交叉检查（{market.get('sentiment', '未披露')}），"
        "因此只能作为条件性House价值。"
    )
    return {
        "method": method,
        "denominator": denominator,
        "multiples": multiple,
        "probabilities": probability_rationale(),
        "evidence": evidence_role(row),
    }


def exact_recovery_formula(row: dict[str, Any]) -> tuple[str, str]:
    probabilities = row.get("probabilities") or PROBABILITIES
    value_formula = (
        f"fair value = {fmt(row['bear'])}×{probabilities['bear']:.2f} + "
        f"{fmt(row['base'])}×{probabilities['base']:.2f} + "
        f"{fmt(row['bull'])}×{probabilities['bull']:.2f}"
    )
    anchor_weight = float(row.get("external_weight") or 0.0)
    anchor = row.get("external_target")
    if anchor is None or anchor_weight == 0:
        final_formula = (
            f"final target = House probability value = "
            f"{fmt(row['house_probability_value'])}"
        )
    else:
        final_formula = (
            f"final target = {fmt(row['house_probability_value'])}×{1 - anchor_weight:.2f} + "
            f"{fmt(anchor)}×{anchor_weight:.2f}"
        )
    return value_formula, final_formula


def audit_recovery_row(row: dict[str, Any]) -> dict[str, Any]:
    value_formula, final_formula = exact_recovery_formula(row)
    probabilities = row.get("probabilities") or PROBABILITIES
    recalculated_house = round(
        row["bear"] * probabilities["bear"]
        + row["base"] * probabilities["base"]
        + row["bull"] * probabilities["bull"],
        2,
    )
    anchor_weight = float(row.get("external_weight") or 0.0)
    anchor = row.get("external_target")
    recalculated_target = round(
        recalculated_house * (1 - anchor_weight)
        + (anchor if anchor is not None else recalculated_house) * anchor_weight,
        2,
    )
    recovery_anchor = row.get("recovery_anchor_type", "house_only_recovery")
    rationale = rationale_for_recovery_row(row)
    return {
        "ticker": row["ticker"],
        "company": row["company"],
        "industry": row["industry"],
        "model_tier": row["model_tier"],
        "method_label": row["method"],
        "formula_type": "recovery_alternative_method",
        "denominator": row.get("normalized_denominator"),
        "formula": value_formula,
        "formula_inputs": row.get("recovery_method_inputs") or {},
        "final_target_formula": final_formula,
        "scenario_inputs": {
            "bear": row["bear"],
            "base": row["base"],
            "bull": row["bull"],
            "probabilities": probabilities,
        },
        "recalculated_house_probability_value": recalculated_house,
        "reported_house_probability_value": row.get("house_probability_value"),
        "recalculated_probability_target": recalculated_target,
        "reported_probability_target": row.get("probability_target"),
        "reported_upside": row.get("upside"),
        "external_anchor_type": recovery_anchor,
        "external_anchor": anchor,
        "external_weight": anchor_weight,
        "evidence_quality": row.get("evidence_quality"),
        "legacy_evidence_quality": row.get("legacy_evidence_quality"),
        "evidence_quality_basis": row.get("evidence_quality_basis"),
        "broker_anchor_quality": row.get("broker_anchor_quality"),
        "formal_anchor_eligible": row.get("formal_anchor_eligible"),
        "evidence_sources": row.get("recovery_evidence_sources") or row.get("evidence_sources"),
        "evidence_summary": source_summary(row),
        "catalyst": row.get("catalyst"),
        "invalidation": row.get("invalidation"),
        "audit_status": (
            "PASS"
            if recalculated_house == row.get("house_probability_value")
            and recalculated_target == row.get("probability_target")
            and row.get("evidence_sources")
            else "FAIL"
        ),
        "audit_note": "Conditional recovery range; not a formal Street target.",
        "why_this_method": rationale["method"],
        "why_this_denominator": rationale["denominator"],
        "why_these_multiples": rationale["multiples"],
        "why_these_probabilities": rationale["probabilities"],
        "evidence_role": rationale["evidence"],
    }


def audit_financial_row(row: dict[str, Any]) -> dict[str, Any]:
    scenario_eps = row["scenario_eps"]
    multiples = row["multiples"]
    bps = row.get("q1_bps")
    pb_values = {
        scenario: round(float(bps) * multiple, 4)
        for scenario, multiple in zip(
            ("bear", "base", "bull"), (0.75, 1.05, 1.35)
        )
    }
    pe_values = {
        scenario: round(float(scenario_eps[scenario]) * float(multiples[index]), 4)
        for index, scenario in enumerate(("bear", "base", "bull"))
    }
    raw_values = {
        scenario: round(pb_values[scenario] * 0.65 + pe_values[scenario] * 0.35, 4)
        for scenario in ("bear", "base", "bull")
    }
    formula = (
        "scenario value = 65%×(Q1 BPS×PB multiple) + "
        "35%×(scenario EPS×PE multiple)"
    )
    final_formula = (
        f"House probability value = {fmt(row['bear'])}×0.30 + "
        f"{fmt(row['base'])}×0.50 + {fmt(row['bull'])}×0.20"
    )
    recalculated_house = round(
        row["bear"] * 0.30 + row["base"] * 0.50 + row["bull"] * 0.20, 2
    )
    external_weight = float(row.get("external_weight") or 0.0)
    external_target = row.get("external_target")
    recalculated_target = round(
        recalculated_house * (1 - external_weight)
        + (external_target if external_target is not None else recalculated_house)
        * external_weight,
        2,
    )
    rationale = rationale_for_financial_row(row)
    return {
        "ticker": row["ticker"],
        "company": row["company"],
        "industry": row["industry"],
        "model_tier": row["model_tier"],
        "method_label": "PB-ROE and earnings blended range",
        "formula_type": "financial_pb_pe_blend",
        "denominator": "Q1 BPS plus H1 deducted EPS bridged to H2",
        "formula": formula,
        "formula_inputs": {
            "q1_bps": bps,
            "shares_100mn": row.get("shares_100mn"),
            "h1_deducted_profit_100mn": row.get("h1_deducted_np_100mn"),
            "h1_deducted_eps": row.get("h1_deducted_eps"),
            "pb_multiples": {"bear": 0.75, "base": 1.05, "bull": 1.35},
            "scenario_eps": scenario_eps,
            "pe_multiples": multiples,
            "pb_component": pb_values,
            "pe_component": pe_values,
            "raw_blended_values": raw_values,
            "bear_cap_at_75pct_current_price": row.get("bear_cap_at_75pct_current_price"),
        },
        "final_target_formula": final_formula,
        "scenario_inputs": {
            "bear": row["bear"],
            "base": row["base"],
            "bull": row["bull"],
            "probabilities": PROBABILITIES,
        },
        "recalculated_house_probability_value": recalculated_house,
        "reported_house_probability_value": row.get("house_probability_value"),
        "recalculated_probability_target": recalculated_target,
        "reported_probability_target": row.get("probability_target"),
        "reported_upside": row.get("upside"),
        "external_anchor_type": "direct_broker_anchor"
        if external_target is not None
        else "house_only_screening",
        "external_anchor": external_target,
        "external_weight": external_weight,
        "evidence_quality": row.get("evidence_quality"),
        "legacy_evidence_quality": row.get("legacy_evidence_quality"),
        "evidence_quality_basis": row.get("evidence_quality_basis"),
        "broker_anchor_quality": row.get("broker_anchor_quality"),
        "formal_anchor_eligible": row.get("formal_anchor_eligible"),
        "evidence_sources": row.get("evidence_sources"),
        "evidence_summary": source_summary(row),
        "catalyst": row.get("catalyst"),
        "invalidation": row.get("invalidation"),
        "audit_status": (
            "PASS"
            if recalculated_house == row.get("house_probability_value")
            and recalculated_target == row.get("probability_target")
            and row.get("evidence_sources")
            else "FAIL"
        ),
        "audit_note": "Screening range only; not a formal rating.",
        "why_this_method": rationale["method"],
        "why_this_denominator": rationale["denominator"],
        "why_these_multiples": rationale["multiples"],
        "why_these_probabilities": rationale["probabilities"],
        "evidence_role": rationale["evidence"],
    }


def audit_eps_pe_row(row: dict[str, Any]) -> dict[str, Any]:
    scenario_eps = row["scenario_eps"]
    multiples = row["multiples"]
    raw_values = {
        scenario: round(float(scenario_eps[scenario]) * float(multiples[index]), 4)
        for index, scenario in enumerate(("bear", "base", "bull"))
    }
    formula = (
        "H1 deducted EPS = H1 deducted profit midpoint / shares; "
        "scenario EPS = H1 deducted EPS×(1+H2/H1 conversion); "
        "scenario value = scenario EPS×PE multiple; "
        "bear = min(raw bear, current price×75%)"
    )
    final_formula = (
        f"House probability value = {fmt(row['bear'])}×0.30 + "
        f"{fmt(row['base'])}×0.50 + {fmt(row['bull'])}×0.20"
    )
    recalculated_house = round(
        row["bear"] * 0.30 + row["base"] * 0.50 + row["bull"] * 0.20, 2
    )
    external_weight = float(row.get("external_weight") or 0.0)
    external_target = row.get("external_target")
    recalculated_target = round(
        recalculated_house * (1 - external_weight)
        + (external_target if external_target is not None else recalculated_house)
        * external_weight,
        2,
    )
    method_label = row.get("method") or "deducted-EPS scenario PE"
    formula_type = {
        "cycle-adjusted deducted-EPS PE": "cycle_adjusted_eps_pe",
        "growth-earnings scenario PE": "growth_earnings_scenario_pe",
        "deducted-EPS scenario PE": "deducted_eps_scenario_pe",
    }.get(method_label, "deducted_eps_scenario_pe")
    formula_prefix = {
        "cycle_adjusted_eps_pe": "周期调整EPS",
        "growth_earnings_scenario_pe": "成长盈利情景EPS",
        "deducted_eps_scenario_pe": "扣非EPS",
    }[formula_type]
    formula = (
        f"{formula_prefix} = H1扣非利润中值 / 股本；"
        "情景EPS = H1扣非EPS×(1+H2/H1转换比例)；"
        "情景价值 = 情景EPS×业务匹配PE；"
        "熊值 = min(原始熊值, 当前价×75%)"
    )
    rationale = rationale_for_eps_row(row, formula_type)
    return {
        "ticker": row["ticker"],
        "company": row["company"],
        "industry": row["industry"],
        "model_tier": row["model_tier"],
        "method_label": method_label,
        "formula_type": formula_type,
        "denominator": "H1 deducted EPS bridged with H2/H1 conversion",
        "formula": formula,
        "formula_inputs": {
            "shares_100mn": row.get("shares_100mn"),
            "h1_deducted_profit_100mn": row.get("h1_deducted_np_100mn"),
            "h1_deducted_eps": row.get("h1_deducted_eps"),
            "h2_conversion_ratios": row.get("h2_conversion_ratios"),
            "scenario_eps": scenario_eps,
            "pe_multiples": multiples,
            "raw_scenario_values": raw_values,
            "bear_cap_at_75pct_current_price": row.get("bear_cap_at_75pct_current_price"),
        },
        "final_target_formula": final_formula,
        "scenario_inputs": {
            "bear": row["bear"],
            "base": row["base"],
            "bull": row["bull"],
            "probabilities": PROBABILITIES,
        },
        "recalculated_house_probability_value": recalculated_house,
        "reported_house_probability_value": row.get("house_probability_value"),
        "recalculated_probability_target": recalculated_target,
        "reported_probability_target": row.get("probability_target"),
        "reported_upside": row.get("upside"),
        "external_anchor_type": "direct_broker_anchor"
        if external_target is not None
        else "house_only_screening",
        "external_anchor": external_target,
        "external_weight": external_weight,
        "evidence_quality": row.get("evidence_quality"),
        "legacy_evidence_quality": row.get("legacy_evidence_quality"),
        "evidence_quality_basis": row.get("evidence_quality_basis"),
        "broker_anchor_quality": row.get("broker_anchor_quality"),
        "formal_anchor_eligible": row.get("formal_anchor_eligible"),
        "evidence_sources": row.get("evidence_sources"),
        "evidence_summary": source_summary(row),
        "catalyst": row.get("catalyst"),
        "invalidation": row.get("invalidation"),
        "audit_status": (
            "PASS"
            if recalculated_house == row.get("house_probability_value")
            and recalculated_target == row.get("probability_target")
            and row.get("evidence_sources")
            else "FAIL"
        ),
        "audit_note": "Screening range only; not a formal rating.",
        "why_this_method": rationale["method"],
        "why_this_denominator": rationale["denominator"],
        "why_these_multiples": rationale["multiples"],
        "why_these_probabilities": rationale["probabilities"],
        "evidence_role": rationale["evidence"],
    }


def audit_boundary_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "ticker": row["ticker"],
        "company": row["company"],
        "industry": row["industry"],
        "model_tier": row["model_tier"],
        "method_label": "上市边界，不作二级市场估值",
        "formula_type": "listing_boundary",
        "denominator": "无二级市场当前价",
        "formula": "目标价/空间 = 不适用；待上市交易后重新建立当前价模型",
        "final_target_formula": "不适用",
        "scenario_inputs": {},
        "recalculated_house_probability_value": None,
        "reported_house_probability_value": None,
        "recalculated_probability_target": None,
        "reported_probability_target": None,
        "reported_upside": None,
        "external_anchor_type": "listing_boundary",
        "external_anchor": 8.66,
        "external_weight": 0.0,
        "evidence_quality": "low",
        "legacy_evidence_quality": "low",
        "evidence_quality_basis": "No observable secondary-market current price at cutoff.",
        "broker_anchor_quality": "listing_boundary",
        "formal_anchor_eligible": False,
        "evidence_sources": ["refresh-20260715/sources/market-20260715/tencent_quotes_01.txt"],
        "evidence_summary": "IPO发行价公告；截至数据截点无二级市场交易价格",
        "catalyst": "上市交易并形成可验证的市场价格",
        "invalidation": "上市推迟或发行条件发生变化",
        "audit_status": "PASS",
        "audit_note": "不属于漏填；当前价格不可用。",
        "why_this_method": "截至数据截点尚未开始二级市场交易，直接估算当前价会制造伪精确结果。",
        "why_this_denominator": "不存在可观察的二级市场当前价或交易市值。",
        "why_these_multiples": "上市前不适用；形成有效市场价格后再建立可比公司/盈利模型。",
        "why_these_probabilities": "尚未建立当前价模型，因此不适用。",
        "evidence_role": "仅使用IPO发行价和上市状态证据，不推断Street目标价。",
    }


def build_audit() -> dict[str, Any]:
    models = load_json(DATA_DIR / "full_market_candidate_valuation_20260715.json")["rows"]
    recovery_payload = load_json(
        DATA_DIR / "valuation_recovery_601360_000042_20260715.json"
    )
    recovery_map = {row["ticker"]: row for row in recovery_payload["rows"]}
    evidence_payload = load_json(DATA_DIR / "full_market_valuation_evidence_20260715.json")
    evidence_rows = evidence_payload["rows"]
    evidence_map = {row["ticker"]: row for row in evidence_rows}
    audit_rows: list[dict[str, Any]] = []
    for row in models:
        enriched_row = dict(row)
        source_row = evidence_map.get(row["ticker"], {})
        for field in ("q1_bps", "q1_ocf_100mn", "q1_revenue_100mn"):
            if enriched_row.get(field) is None:
                enriched_row[field] = source_row.get(field)
        if row.get("model_tier") == "recovery_conditional_model":
            enriched_row["recovery_method_inputs"] = (
                recovery_map.get(row["ticker"], {}).get("alternative_method") or {}
            )
            audit_rows.append(audit_recovery_row(enriched_row))
        elif row.get("model_tier") == "not_priceable":
            audit_rows.append(audit_boundary_row(enriched_row))
        elif row.get("method") == "PB-ROE and earnings blended range":
            audit_rows.append(audit_financial_row(enriched_row))
        else:
            audit_rows.append(audit_eps_pe_row(enriched_row))
    return {
        "schema_version": "astock.candidate_valuation_audit.refresh.v1",
        "data_cutoff": DATA_CUTOFF,
        "row_count": len(audit_rows),
        "pass_count": sum(row["audit_status"] == "PASS" for row in audit_rows),
        "fail_count": sum(row["audit_status"] == "FAIL" for row in audit_rows),
        "formula_type_counts": {
            formula_type: sum(row["formula_type"] == formula_type for row in audit_rows)
            for formula_type in sorted({row["formula_type"] for row in audit_rows})
        },
        "rows": audit_rows,
    }


def markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Candidate Valuation Audit — 2026-07-15",
        "",
        f"- Rows: {payload['row_count']}",
        f"- Audit status: {payload['pass_count']} PASS / {payload['fail_count']} FAIL",
        "- Every row has a formula type, denominator, scenario inputs, final-target formula, evidence references and audit status.",
        "",
        "| Ticker | Company | Formula type | Method | Target | Upside | Evidence quality | Status |",
        "|---|---|---|---|---:|---:|---|---|",
    ]
    models = load_json(DATA_DIR / "full_market_candidate_valuation_20260715.json")["rows"]
    model_map = {row["ticker"]: row for row in models}
    for row in payload["rows"]:
        model = model_map[row["ticker"]]
        target = (
            "listing boundary"
            if model.get("probability_target") is None
            else f"{model['probability_target']:.2f}"
        )
        upside = (
            "not calculated"
            if model.get("upside") is None
            else f"{model['upside']:.1%}"
        )
        lines.append(
            f"| {row['ticker']} | {row['company']} | {row['formula_type']} | "
            f"{row['method_label']} | {target} | {upside} | "
            f"{row['evidence_quality']} | {row['audit_status']} |"
        )
    lines.extend(["", "## Formula and Evidence Detail", ""])
    for row in payload["rows"]:
        lines.extend(
            [
                f"### {row['ticker']} {row['company']}",
                f"- Method: {row['method_label']}",
                f"- Denominator: {row['denominator']}",
                f"- Formula: {row['formula']}",
                f"- Final target formula: {row['final_target_formula']}",
                f"- Why this method: {row.get('why_this_method', 'not disclosed')}",
                f"- Why this denominator: {row.get('why_this_denominator', 'not disclosed')}",
                f"- Why these multiples: {row.get('why_these_multiples', 'not disclosed')}",
                f"- Why these probabilities: {row.get('why_these_probabilities', 'not disclosed')}",
                f"- Evidence role: {row.get('evidence_role', 'not disclosed')}",
                f"- Evidence: {row['evidence_summary']}",
                f"- Evidence paths: {'; '.join(source for source in row.get('evidence_sources', []) if source) or 'explicit listing boundary'}",
                f"- Audit: {row['audit_status']} — {row['audit_note']}",
                "",
            ]
        )
    return "\n".join(lines)


def main() -> None:
    payload = build_audit()
    write_json(DATA_DIR / "full_market_candidate_valuation_audit_20260715.json", payload)
    (DATA_DIR / "full_market_candidate_valuation_audit_20260715.md").write_text(
        markdown(payload) + "\n"
    )
    print(
        json.dumps(
            {
                "row_count": payload["row_count"],
                "pass_count": payload["pass_count"],
                "fail_count": payload["fail_count"],
                "formula_type_counts": payload["formula_type_counts"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
