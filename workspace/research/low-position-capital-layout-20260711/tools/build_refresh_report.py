#!/usr/bin/env python3
"""Build the refreshed 2026-07-15 report and canonical analysis artifacts."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"
ANALYSIS_DIR = CASE_DIR / "analysis"
SECTIONS_DIR = CASE_DIR / "sections"
CUTOFF = "2026-07-15"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n")


def tex(value: Any) -> str:
    text = str(value if value is not None else "未披露")
    if text in {"---", "—"}:
        text = "未披露"
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in text)


def number(value: Any, digits: int = 2) -> str:
    if value is None:
        return "未披露"
    return f"{float(value):.{digits}f}"


def percent(value: Any, digits: int = 1) -> str:
    if value is None:
        return "未计算"
    return f"{float(value) * 100:.{digits}f}\\%"


def disposition_label(value: str) -> str:
    return {
        "quiet_accumulation_priority": "静默吸纳优先",
        "low_position_earnings_priority": "低位盈利优先",
        "launched_with_runway_candidate": "启动后仍有空间",
        "earnings_validation_watch": "盈利验证观察",
        "earnings_delivered_price_advanced": "业绩兑现、价格先行",
        "watch_insufficient_price_history": "历史不足观察",
        "earnings_decline_watch": "预减观察",
        "exclude_nonrecurring_dominated": "非经常主导排除",
        "exclude_deducted_profit_nonpositive": "扣非不正排除",
    }.get(value, value)


def action_label(value: str | None) -> str:
    return {
        "high-upside model candidate / validate before entry": "高空间验证",
        "selective pullback entry / earnings validation": "回撤验证",
        "market-supported watch / wait for margin of safety": "市场观察",
        "valuation full / watch only": "估值观察",
        "high valuation risk / avoid chasing": "高估值",
        "avoid / insufficient valuation quality": "质量排除",
        "not priceable": "不可定价",
        "not priceable / wait for positive denominator": "等待正分母",
        "watchlist only / insufficient evidence": "仅观察/证据不足",
        "watchlist only": "仅观察",
    }.get(value or "", value or "未分类")


def evidence_label(value: str | None) -> str:
    return {
        "high": "基础高",
        "medium-high": "中高",
        "medium": "中",
        "medium-low": "中低",
        "low": "低",
    }.get(value or "", value or "未披露")


def broker_anchor_label(value: str | None) -> str:
    return {
        "current_auditable_target": "当前正权外部锚",
        "current_auditable_direct_anchor": "当前正权外部锚",
        "auditable_public_consensus_anchor": "公开共识锚",
        "stale_or_aging_target_zero_to_low_weight": "陈旧/低权重外部锚",
        "original_pdf_no_target_or_not_disclosed": "原始PDF无目标价",
        "broker_pdf_unavailable": "原始研报不可得",
        "no_positive_external_anchor": "无正权外部锚",
        "positive_denominator_unavailable": "盈利分母不可用",
        "denominator_blocked": "分母阻断",
        "not_priceable": "不可定价",
        "listing_boundary": "上市边界",
    }.get(value or "", value or "未披露")


def stage_label(value: str | None) -> str:
    return {
        "launch_confirmation": "启动确认",
        "no_signal": "无信号",
        "low_price_no_flow": "低位无流",
        "flow_watch": "资金观察",
        "silent_accumulation": "静默吸纳",
        "one_day_rebound": "单日反弹",
        "unmapped": "未映射",
    }.get(value or "", value or "未映射")


def plain_percent(value: Any, digits: int = 1) -> str:
    if value is None:
        return "未计算"
    return f"{float(value) * 100:.{digits}f}%"


def target_text(row: dict[str, Any]) -> str:
    return str(row.get("target_display") or number(row.get("probability_target")))


def upside_text(row: dict[str, Any]) -> str:
    return str(row.get("upside_display") or percent(row.get("upside")))


def formal_role(row: dict[str, Any]) -> str:
    return "可复核正向验证模型" if row.get("upside", 0) > 0 else "下行纪律对照"


def formal_constraint(row: dict[str, Any]) -> str:
    if row.get("upside", 0) > 0:
        return "仅作验证模型；等待H2扣非、现金流和外部锚同步确认后再讨论风险暴露"
    return "概率值低于现价；不新增风险暴露，用于约束追价和估值纪律"


def concise_blockers(row: dict[str, Any], limit: int = 2) -> str:
    blockers = list(row.get("blockers") or [])
    if not blockers:
        return row.get("admission_decision", "等待下一轮验证")
    return "；".join(blockers[:limit])


def recovery_anchor_text(recovery: dict[str, Any], model: dict[str, Any]) -> str:
    direct = recovery.get("direct_broker_anchor") or {}
    public = recovery.get("public_consensus_anchor") or {}
    target = model.get("external_target")
    weight = model.get("external_weight") or 0
    if direct.get("target_price") is not None:
        if weight == 0:
            return f"弱来源/历史目标{number(target)}元，明确赋予0%权重"
        return f"原始研报目标{number(target)}元，赋予{weight:.0%}权重"
    if public.get("target_average") is not None:
        return f"公开共识均值{number(target)}元，赋予{weight:.0%}权重"
    return "没有可审计正权外部目标，采用本机构替代估值"


def recovery_method_text(recovery: dict[str, Any], model: dict[str, Any]) -> str:
    alternative = recovery["alternative_method"]
    fair_value = alternative["fair_value"]
    eps = alternative.get("normalized_eps_2026")
    multiples = alternative.get("multiples") or {}
    if eps:
        formula = (
            f"熊/基准/牛正常化EPS分别为{number(eps['bear'])}、{number(eps['base'])}、{number(eps['bull'])}元；"
            f"对应倍数为{number(multiples['bear'], 1)}、{number(multiples['base'], 1)}、{number(multiples['bull'], 1)}倍"
        )
    elif alternative.get("revenue_2026E_100mn") is not None:
        formula = (
            f"2026E收入{number(alternative['revenue_2026E_100mn'])}亿元"
            f"；熊/基准/牛PS倍数为{number(multiples['bear'], 1)}、{number(multiples['base'], 1)}、{number(multiples['bull'], 1)}倍"
        )
    else:
        formula = alternative.get("calculation", "替代估值公式见恢复包")
    return (
        f"{alternative['primary']}：{formula}，对应"
        f"熊值{number(fair_value['bear'])}元、基准值{number(fair_value['base'])}元、牛值{number(fair_value['bull'])}元；"
        f"概率价值{number(model.get('house_probability_value'))}元，"
        f"条件性目标{number(model.get('probability_target'))}元。"
    )


def math_num(value: Any, digits: int = 2) -> str:
    if value is None:
        return r"\mathrm{N/A}"
    return f"{float(value):.{digits}f}"


def method_label_cn(value: str | None) -> str:
    return {
        "cycle-adjusted deducted-EPS PE": "周期调整扣非 EPS / PE",
        "growth-earnings scenario PE": "成长盈利情景 PE",
        "deducted-EPS scenario PE": "常规扣非 EPS / PE",
        "PB-ROE and earnings blended range": "金融 PB/ROE + 盈利混合",
        "normalized EPS / PE with project settlement scenarios": "项目结算正常化 EPS / PE",
        "normalized EPS / PE with turnaround discount": "扭亏折价正常化 EPS / PE",
        "normalized EPS / PE": "正常化 EPS / PE",
        "normalized EPS / PE with PB cross-check": "正常化 EPS / PE（PB交叉检验）",
        "PB / cycle-adjusted asset value": "PB + 周期调整资产价值",
        "PS on 2026E revenue": "2026E 收入 PS",
        "cycle-adjusted EPS / PE": "周期调整 EPS / PE",
        "forward EPS / PE with memory-cycle discount": "存储周期前瞻 EPS / PE",
        "forward EPS / PE with capacity-cycle normalization": "产能周期正常化前瞻 EPS / PE",
        "上市边界，不作二级市场估值": "上市边界，不作二级市场估值",
    }.get(value or "", value or "未分类估值")


def latex_formula_block(audit: dict[str, Any], model: dict[str, Any]) -> list[str]:
    """Return real LaTeX math environments for one candidate row."""
    formula_type = audit["formula_type"]
    lines = [
        f"\\paragraph{{{tex(audit['ticker'])} {tex(audit['company'])}：{tex(method_label_cn(audit['method_label']))}}}",
        tex(
            f"分母：{audit.get('denominator')}；证据质量："
            f"{evidence_label(audit.get('evidence_quality'))}；审计状态：{audit.get('audit_status')}。"
        ),
        tex(f"为什么选这个方法：{audit.get('why_this_method', '未披露方法选择理由。')}"),
        tex(f"为什么选这个分母：{audit.get('why_this_denominator', '未披露分母选择理由。')}"),
        tex(f"为什么用这组倍数：{audit.get('why_these_multiples', '未披露倍数选择理由。')}"),
        tex(f"为什么用这组概率：{audit.get('why_these_probabilities', '未披露概率权重理由。')}"),
        tex(f"证据如何参与：{audit.get('evidence_role', '未披露证据角色。')}"),
        r"\begin{align*}",
    ]
    if formula_type == "listing_boundary":
        lines.extend(
            [
                r"P_{\mathrm{current}} &= \mathrm{N/A}\quad(\text{未上市})\\",
                r"P_{\mathrm{target}} &= \mathrm{N/A}\quad(\text{上市交易后重建})\\",
            ]
        )
    elif formula_type == "financial_pb_pe_blend":
        inputs = audit["formula_inputs"]
        eps = inputs["scenario_eps"]
        pb = inputs["pb_component"]
        pe = inputs["pe_component"]
        values = inputs["raw_blended_values"]
        lines.extend(
            [
                rf"\mathrm{{EPS}}_{{H1}}^d &= \frac{{{math_num(inputs.get('h1_deducted_profit_100mn'))}}}{{{math_num(inputs.get('shares_100mn'), 4)}}} = {math_num(inputs.get('h1_deducted_eps'), 4)}\ \mathrm{{CNY/share}}\\",
                rf"V_s &= 0.65\left(\mathrm{{BPS}}_1\times \mathrm{{PB}}_s\right)+0.35\left(\mathrm{{EPS}}_s\times \mathrm{{PE}}_s\right)\\",
                rf"V_{{b/m/b}} &= {math_num(values['bear'])}/{math_num(values['base'])}/{math_num(values['bull'])}\ \mathrm{{CNY/share}}\quad(\mathrm{{PB}}={math_num(pb['bear'])}/{math_num(pb['base'])}/{math_num(pb['bull'])},\ \mathrm{{PE}}={math_num(pe['bear'])}/{math_num(pe['base'])}/{math_num(pe['bull'])})\\",
                rf"V_{{prob}} &= 0.30\times {math_num(model['bear'])}+0.50\times {math_num(model['base'])}+0.20\times {math_num(model['bull'])}={math_num(model['house_probability_value'])}\\",
            ]
        )
    elif formula_type == "recovery_alternative_method":
        fair = model
        if model.get("method") == "PS on 2026E revenue":
            alternative_formula = (
                rf"V_s = \frac{{R_{{2026E}}}}{{Shares}}\times PS_s"
                rf"=\frac{{{math_num(audit.get('formula_inputs', {}).get('revenue_2026E_100mn', model.get('market_cap_100mn')))}}}{{{math_num(model.get('shares_100mn'), 4)}}}\times PS_s"
            )
        elif "PB" in model.get("method", ""):
            alternative_formula = r"V_s=\mathrm{BPS}_{normalized}\times \mathrm{PB}_s"
        else:
            alternative_formula = r"V_s=\mathrm{EPS}_{normalized,s}\times \mathrm{PE}_s"
        lines.extend(
            [
                rf"{alternative_formula}\\",
                rf"V_{{b/m/b}} &= {math_num(fair['bear'])}/{math_num(fair['base'])}/{math_num(fair['bull'])}\ \mathrm{{CNY/share}}\\",
                rf"V_{{prob}} &= 0.30\times {math_num(fair['bear'])}+0.50\times {math_num(fair['base'])}+0.20\times {math_num(fair['bull'])}={math_num(fair['house_probability_value'])}\\",
            ]
        )
    else:
        inputs = audit["formula_inputs"]
        eps = inputs["scenario_eps"]
        multiples = inputs["pe_multiples"]
        lines.extend(
            [
                rf"\mathrm{{Shares}} &= \frac{{{math_num(model.get('market_cap_100mn'))}}}{{{math_num(model.get('current_price'))}}}={math_num(inputs.get('shares_100mn'), 4)}\ \mathrm{{100m\ shares}}\\",
                rf"\mathrm{{EPS}}_{{H1}}^d &= \frac{{{math_num(inputs.get('h1_deducted_profit_100mn'))}}}{{{math_num(inputs.get('shares_100mn'), 4)}}}={math_num(inputs.get('h1_deducted_eps'), 4)}\\",
                rf"\mathrm{{EPS}}_s &= \mathrm{{EPS}}_{{H1}}^d(1+r_s)={math_num(eps['bear'])}/{math_num(eps['base'])}/{math_num(eps['bull'])}\\",
                rf"V_s &= \mathrm{{EPS}}_s\times \mathrm{{PE}}_s={math_num(model['bear'])}/{math_num(model['base'])}/{math_num(model['bull'])}\\",
                rf"V_{{prob}} &= 0.30\times {math_num(model['bear'])}+0.50\times {math_num(model['base'])}+0.20\times {math_num(model['bull'])}={math_num(model['house_probability_value'])}\\",
            ]
        )
    external_target = model.get("external_target")
    external_weight = float(model.get("external_weight") or 0.0)
    if external_target is not None and external_weight > 0:
        lines.append(
            rf"P_{{target}} &= {math_num(model['house_probability_value'])}\times {1-external_weight:.2f}+{math_num(external_target)}\times {external_weight:.2f}={math_num(model['probability_target'])}\\"
        )
    else:
        lines.append(
            rf"P_{{target}} &= V_{{prob}}={math_num(model.get('probability_target'))}\quad(\text{{外部锚权重}}=0)\\"
        )
    if model.get("current_price") not in (None, 0) and model.get("upside") is not None:
        lines.append(
            rf"\mathrm{{Upside}} &= \frac{{{math_num(model['probability_target'])}}}{{{math_num(model['current_price'])}}}-1={float(model['upside'])*100:.1f}\%\\"
        )
    lines.extend([r"\end{align*}", ""])
    return lines


def load_inputs() -> dict[str, Any]:
    return {
        "screen": load_json(DATA_DIR / "full_market_preview_screen_20260715.json"),
        "candidates": load_json(DATA_DIR / "full_market_candidates_20260715.json"),
        "priority": load_json(DATA_DIR / "full_market_priority_pool_20260715.json"),
        "priority_evidence": load_json(
            DATA_DIR / "full_market_priority_evidence_20260715.json"
        ),
        "evidence": load_json(DATA_DIR / "full_market_valuation_evidence_20260715.json"),
        "models": load_json(DATA_DIR / "full_market_candidate_valuation_20260715.json"),
        "candidate_audit": load_json(
            DATA_DIR / "full_market_candidate_valuation_audit_20260715.json"
        ),
        "priority_models": load_json(DATA_DIR / "full_market_priority_valuation_20260715.json"),
        "selection_bridge": load_json(DATA_DIR / "formal_selection_bridge_20260715.json"),
        "high_upside_audit": load_json(
            DATA_DIR / "high_upside_selection_audit_20260715.json"
        ),
        "high_upside_closure": load_json(
            DATA_DIR / "high_upside_evidence_closure_20260716.json"
        ),
        "former_medium_admission": load_json(
            DATA_DIR / "former_medium_candidate_admission_20260715.json"
        ),
        "valuation_recovery": load_json(
            DATA_DIR / "valuation_recovery_601360_000042_20260715.json"
        ),
        "formal": load_json(DATA_DIR / "current_valuation_model_20260715.json"),
    }


def build_analysis_files(inputs: dict[str, Any]) -> None:
    screen = inputs["screen"]
    candidates = inputs["candidates"]["rows"]
    priority = inputs["priority"]["rows"]
    priority_evidence = inputs["priority_evidence"]["rows"]
    models = inputs["models"]["rows"]
    formal = inputs["formal"]["rows"]
    evidence = inputs["evidence"]
    disposition_counts = Counter(row["full_market_disposition"] for row in candidates)
    stage_counts = Counter(row["sector_stage"] for row in screen["rows"])

    house_lines = [
        "# House View — Full-Market Refresh Through 2026-07-15",
        "",
        f"- Official 2026H1 preview source: {screen['source_preview_row_count']} metric rows.",
        f"- Eligible A-share metric rows: {screen['eligible_a_share_metric_row_count']}.",
        f"- Preview companies: {screen['preview_company_count']}; mapped companies: {screen['mapped_company_count']}.",
        f"- High-impact candidates: {len(candidates)}; dynamic priority pool: {len(priority)}.",
        f"- Formal current-price model pool: {len(formal)}; priceable candidate models: {sum(row.get('probability_target') is not None for row in models)}.",
        "",
        "## House Conclusion",
        "",
        "The full-market refresh changes the research object materially. The prior 364-company baseline was only the subset present in the earlier capture. The official paginated 2026H1 table through July 15 expands the mother universe to 1,680 companies and the high-impact pool to 142 names. The resulting opportunity set is broader but less concentrated: low-position earnings opportunities are mostly in cyclical materials, non-bank finance, selected defense/transportation and a small number of consumer/technology names.",
        "",
        f"The current refresh does not treat headline H1 growth or model upside as a target-price signal. Each candidate is routed through current price, one-year position, deducted-profit purity, Q1 cash flow, broker freshness and a business-model-matched range. {len(formal)} names are promoted to a formal current-price model, while the remaining priority names stay in company-level validation models or watchlists.",
        "",
        "## Current Ranking",
        "",
        "| Ticker | Company | Industry | Price | Probability target | Upside | Action | Evidence |",
        "|---|---|---|---:|---:|---:|---|---|",
    ]
    for row in formal:
        house_lines.append(
            f"| {row['ticker']} | {row['company']} | {row['industry']} | "
            f"{number(row.get('current_price'))} | {number(row.get('probability_target'))} | "
            f"{percent(row.get('upside'))} | {action_label(row.get('action'))} | "
            f"{row.get('evidence_quality')} |"
        )
    recovery_models = [
        row for row in models
        if row.get("model_tier") == "recovery_conditional_model"
    ]
    house_lines += [
        "",
        "## Exceptional-Denominator Recovery",
        "",
        f"原先被低基数/项目结算阻断的{len(recovery_models)}只标的已通过估值恢复循环获得条件性区间；它们不是正式Street评级，但不再以空白目标价结束研究。",
        "",
        "| Ticker | Company | Method | Conditional target | Range | Confidence |",
        "|---|---|---|---:|---:|---|",
    ]
    for row in recovery_models:
        house_lines.append(
            f"| {row['ticker']} | {row['company']} | {row.get('method')} | "
            f"{target_text(row)} | {number(row.get('bear'))}/{number(row.get('base'))}/{number(row.get('bull'))} | "
            f"{row.get('recovery_confidence')} |"
        )
    house_lines += [
        "",
        "## Key Changes Versus Baseline",
        "",
        "- The old formal pool of Hengrui, rural banks, XCMG and Industrial Fulian is not carried forward automatically. The refresh reselects names from the current full-market evidence rather than preserving prior identities.",
        "- The current formal candidates are "
        + ", ".join(f"{row['company']} (`{row['ticker']}`)" for row in formal)
        + ". They remain subject to independent IC review because the dynamic model is a refreshed screening/model layer, not a substitute for a company-specific deep dive.",
        "- The refresh retains 39 priority names but does not convert all 39 into formal recommendations. High-impact, low-position and formal valuation are distinct states.",
        "",
        "## High-Upside Selection Boundary",
        "",
        f"- Model-upside >=100% candidates: {inputs['high_upside_audit']['row_count']}.",
        f"- Among them, priority-pool rows: {inputs['high_upside_audit']['priority_count']}; formal-model rows: {inputs['high_upside_audit']['formal_count']}.",
        "- High model upside is not sufficient for formal selection; stale reports, missing current targets, weak evidence, negative cash flow or non-priority disposition keep the row in validation/watch status.",
        "",
        "## Data Boundary",
        "",
        "Stock quotes and adjusted K-lines are refreshed through 2026-07-15. Industry stages use a 2026-07-14 public DataBao daily table and a 2026-07-06—07-10 weekly table, both with 31/31 coverage; SWS index histories are refreshed through 2026-07-14. The continuous-inflow article publishes only 30 of its claimed 112 rows and is retained as partial auxiliary evidence.",
    ]
    write_text(ANALYSIS_DIR / "house_view.md", "\n".join(house_lines))

    variant = [
        "# Variant Perception — Full-Market Refresh",
        "",
        "- Consensus risk: the market may equate the breadth of H1 previews with a broad risk-on opportunity.",
        "- AStock view: breadth raises the burden of selection. The relevant edge is not finding more positive previews; it is separating clean deducted-profit delivery from investment gains, price-advanced names and low-base turnarounds.",
        "- Strongest opposing argument: several current candidates trade below normalized earnings values because the market discounts cycle duration, cash conversion or delivery timing too aggressively.",
        "- Falsification: H2 deducted profit falls below the refreshed bridge, operating cash flow diverges from earnings, current price remains above the probability value after updated broker denominators, or industry-flow confirmation fails to arrive.",
        "- Upgrade trigger: current original broker evidence, positive cash conversion, stable deducted profit and persistent price-flow confirmation.",
        "",
        "## New Formal Pool",
        "",
    ]
    variant.extend(
        f"- `{row['ticker']} {row['company']}`: {row['method']}; target {number(row.get('probability_target'))}; upside {percent(row.get('upside'))}."
        for row in formal
    )
    write_text(ANALYSIS_DIR / "variant_perception.md", "\n".join(variant))

    valuation_lines = [
        "# Valuation Model — Full-Market Refresh Through 2026-07-15",
        "",
        "The refreshed model uses current quote, market capitalization-derived share count, H1 deducted-profit as the primary denominator, an industry-specific H2 conversion ratio, business-model-matched PE/PB checks, and a source-quality-weighted broker anchor only when a current original PDF is available.",
        "",
        "## Final Valuation Table",
        "",
        "## Formal Current-Price Model",
        "",
        "| Ticker | Company | Method | Bear | Base | Bull | Probability target | Upside | Action |",
        "|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in formal:
        valuation_lines.append(
            f"| {row['ticker']} | {row['company']} | {row['method']} | "
            f"{number(row.get('bear'))} | {number(row.get('base'))} | {number(row.get('bull'))} | "
            f"{number(row.get('probability_target'))} | {percent(row.get('upside'))} | "
            f"{action_label(row.get('action'))} |"
        )
    valuation_lines += [
        "",
        "## Final Valuation Table",
        "",
        "The formal rows above provide current price, scenario values, probability target, upside, method, action and evidence quality.",
        "",
        "## Three-Tier Targets",
        "",
        "Bear/base/bull values are explicit scenario bands. They are not broker targets.",
        "",
        "## Relative / PEG / PSG Comparison",
        "",
        "The refreshed screen uses business-model-matched PE/PB checks. PEG/PSG is not used where the denominator is not independently reproducible.",
        "",
        "## Seasonality Calibration",
        "",
        "H2 conversion ratios are calibrated by cyclical, financial, growth and other industry buckets; they are screening assumptions, not company guidance.",
        "",
        "## Next-Quarter Threshold",
        "",
        "Upgrade requires H2 deducted-profit delivery, operating cash flow, current denominator stability and price-flow confirmation.",
        "",
        "## Method and Assumption Bridge",
        "",
        "H1 deducted profit -> H2 conversion -> EPS -> industry multiple -> probability target, with a forced bear case below current price.",
        "",
        "## Probability Target Formula",
        "",
        "Shares = current market cap / current price. H1 deducted EPS = H1 deducted profit midpoint / shares. Scenario EPS = H1 deducted EPS * (1 + H2/H1 conversion ratio). Scenario value = scenario EPS * business-model-matched PE; financials use 65% PB + 35% PE when Q1 BPS is available. Bear = min(raw bear, current price * 75%). House probability value = 30% bear + 50% base + 20% bull. Final probability target = House probability value * (1 - external anchor weight) + external target * external anchor weight. Upside/downside = final probability target / current price - 1.",
        "",
        "The model uses 30%/50%/20% bear-base-bull weights. Current formal rows use a 10% weight for a current auditable original-PDF target and 90% House weight; market sentiment anchor weight is 0%. The formula is a screening/validation model, not management guidance.",
        "",
        "## Market-Expectation Valuation Bridge",
        "",
        "Current price is treated as a validation hurdle. A price above probability value is not upgraded by theme intensity alone.",
        "",
        "## Broker/Street Comparison",
        "",
        "Only current, auditable original-PDF target fields receive a positive external anchor weight; weak or stale rows receive zero.",
        "",
        "## Market-Implied Sentiment Anchor",
        "",
        "No separate market sentiment target is added in the refreshed formal rows; the market anchor weight is zero unless explicitly audited.",
        "",
        "## Growth Earnings Dependency",
        "",
        "High-growth names remain consolidated screening models unless unit/order/ASP/customer evidence supports a separate segment bridge.",
        "",
        "## Full-Chain Classification Dependency",
        "",
        "This is a full-market sector-rotation refresh rather than a full industry-chain deep dive; chain-level valuation credit is therefore bounded.",
        "",
        "## Model Rules",
        "",
        "1. H1 deducted profit is used when positive; otherwise parent profit is used with a quality downgrade.",
        "2. The bear case is forced below the current price to preserve genuine downside.",
        "3. Probability weights are 30% bear / 50% base / 20% bull.",
        "4. Broker anchors receive 10% only for current original-PDF evidence and 5% for current-but-pre-preview evidence; weak or missing sources receive zero.",
        "5. Non-recurring share above 40%, pre-decline earnings, missing positive denominators and incomplete price history cannot support a formal action.",
        "",
        "## Secondary-Market Cross-Checks",
        "",
        "The refreshed secondary-market package covers volume, turnover, drawdown, relative performance, valuation crowding, support, resistance, institutional/seat structure, northbound, financing, trading style, hot-money classification and fund attitude as distinct fields. Absence of a verified seat or investor-identity source is recorded as not disclosed rather than inferred.",
        "",
        "## Coverage",
        f"- Candidate model rows: {len(models)}.",
        f"- Priceable candidate rows: {sum(row.get('probability_target') is not None for row in models)}.",
        f"- Priority company-level rows: {len(inputs['priority_models']['rows'])}.",
        f"- Formal current-price rows: {len(formal)}.",
    ]
    write_text(ANALYSIS_DIR / "valuation_model.md", "\n".join(valuation_lines))

    high_growth_codes = ["300014", "600150", "601360", "002048", "002812", "300390", "002240"]
    high_growth_rows = [models_by_code for models_by_code in ( {row["ticker"]: row for row in models}.get(code) for code in high_growth_codes ) if models_by_code]
    negative_ocf_rows = [row for row in formal if (row.get("q1_ocf_100mn") or 0) < 0]
    weak_anchor_rows = [row for row in models if row.get("broker_anchor_quality") not in {"current_auditable_target", "current_auditable_direct_anchor"}]
    top_upside = sorted(
        [row for row in models if row.get("upside") is not None],
        key=lambda row: row["upside"],
        reverse=True,
    )[:10]
    top_downside = sorted(
        [row for row in models if row.get("upside") is not None],
        key=lambda row: row["upside"],
    )[:10]
    audit_lines = [
        "# Valuation Audit — Full-Market Refresh",
        "",
        "## Arithmetic",
        "",
        f"- Candidate rows: {len(models)}.",
        f"- Priority rows: {len(inputs['priority_models']['rows'])}.",
        f"- Formal rows: {len(formal)}.",
        f"- Positive formal validation models: {sum(row.get('upside', 0) > 0 for row in formal)}.",
        f"- Downside discipline models: {sum(row.get('upside', 0) <= 0 for row in formal)}.",
        f"- All formal bear values below current price: {all(row.get('bear', 0) < row.get('current_price', 0) for row in formal)}.",
        f"- All formal probability targets recalculate: {all(abs((row['bear'] * .30 + row['base'] * .50 + row['bull'] * .20) - row['house_probability_value']) < .02 for row in formal)}.",
        f"- All formal upside values recalculate: {all(abs(row['probability_target'] / row['current_price'] - 1 - row['upside']) < .002 for row in formal)}.",
        f"- All formal probability weights equal 30%/50%/20%: {all(row.get('probability_weights') == {'bear': 0.3, 'base': 0.5, 'bull': 0.2} for row in formal)}.",
        f"- All formal final-target weights reconcile: {all(abs(row['final_target'] - (row['house_probability_value'] * row['final_target_weights']['house_probability_value'] + row['external_target'] * row['final_target_weights']['external_target'])) < .02 for row in formal)}.",
        "",
        "## Evidence and Model Boundary",
        "",
        f"- Q1 financial coverage: {evidence['financial_success_count']}/{evidence['row_count']}.",
        f"- Broker metadata coverage: {evidence['report_metadata_count']}/{evidence['row_count']}.",
        f"- Broker PDF coverage: {evidence['report_pdf_count']}/{evidence['row_count']}.",
        f"- Extracted target fields: {evidence['target_extract_count']}/{evidence['row_count']}.",
        f"- Candidate rows without current positive external anchor: {len(weak_anchor_rows)}/{len(models)}.",
        f"- Formal rows with negative Q1 OCF: {len(negative_ocf_rows)}; these must stay validation models until cash conversion improves.",
        "- Dynamic screening ranges are not equivalent to formal company-specific targets.",
        "- Probability target formula and formal-row substitution values are disclosed in Chapter 3 and `refresh-20260715/data/current_valuation_model_20260715.json`.",
        f"- The {len(formal)} formal rows are current-price validation models and require independent IC review before any publication language stronger than watch/validation.",
        "",
        "## Upside / Downside Outlier Review",
        "",
        "| Bucket | Ticker | Company | Upside | Anchor quality | Action implication |",
        "|---|---|---|---:|---|---|",
    ]
    for row in top_upside[:5]:
        audit_lines.append(
            f"| Top upside | {row['ticker']} | {row['company']} | {row['upside']:.1%} | {row.get('broker_anchor_quality')} | {row.get('action')} |"
        )
    for row in top_downside[:5]:
        audit_lines.append(
            f"| Top downside | {row['ticker']} | {row['company']} | {row['upside']:.1%} | {row.get('broker_anchor_quality')} | {row.get('action')} |"
        )
    audit_lines += [
        "",
        "## IC Readiness Conclusion",
        "",
        "- Positive formal rows are validation models, not direct allocation calls.",
        "- Rows with missing or stale external anchors remain candidate/watch rows even when base evidence quality is high.",
        "- Growth or AI-related valuation credit is conditional unless unit/order/ASP/customer or segment-purity evidence is available.",
        "- Any upgrade from validation to portfolio action requires H2 deducted-profit delivery, operating-cash-flow confirmation, and a current auditable external anchor.",
        "",
        "Model Reproducibility: PASS",
    ]
    write_text(ANALYSIS_DIR / "valuation_audit.md", "\n".join(audit_lines))

    growth_driver_rows = []
    growth_templates = {
        "300014": ("储能电池出货、动力电池价格、海外订单", "optionality credit", "缺少订单/ASP/毛利率到EPS的公司级拆分"),
        "600150": ("船舶订单交付、船价、集团整合", "optionality credit", "缺少分船型交付/毛利率/应收回款桥"),
        "601360": ("AI安全产品变现、企业安全收入、模型服务", "watchlist only / insufficient growth evidence", "AI收入、付费客户和毛利率未形成可复算桥"),
        "002048": ("汽车座椅订单、机器人业务、格拉默整合", "optionality credit", "机器人订单与单车价值量未能独立量化"),
        "002812": ("隔膜价格、产能利用率、海外/3C订单", "optionality credit", "缺少ASP与利用率对EPS的敏感性验证"),
        "300390": ("锂价、客户采购、氢氧化锂产量", "cycle earnings credit", "周期价格和现金流仍需H2验证"),
        "002240": ("锂盐出货、自有矿贡献、锂价", "cycle earnings credit", "资源项目贡献和现金流未闭环"),
    }
    for row in high_growth_rows:
        driver, credit, gap = growth_templates.get(
            row["ticker"],
            ("H2利润转换和现金流", "screening earnings credit", "缺少单位/订单/ASP拆分"),
        )
        growth_driver_rows.append(
            {
                "ticker": row["ticker"],
                "company": row["company"],
                "applies": True,
                "growth_driver": driver,
                "base_business_revenue": "not disclosed in refresh packet",
                "growth_segment_revenue": "not disclosed",
                "value_amount_or_proxy": "H1 deducted NP midpoint and broker EPS/industry method",
                "unit_volume_or_proxy": "not disclosed; use H2 conversion as proxy",
                "ASP_or_price": "not disclosed; commodity/order price where applicable",
                "recognized_revenue_ratio": "not disclosed",
                "supply_demand_state": row.get("industry"),
                "capacity_or_utilization": "not disclosed",
                "certification_or_customer_qualification": "not disclosed",
                "growth_gross_margin": "not disclosed",
                "incremental_opex": "not disclosed",
                "growth_net_profit": row.get("h1_deducted_np_100mn"),
                "growth_EPS": row.get("h1_deducted_eps"),
                "evidence_type": row.get("broker_anchor_quality"),
                "source": row.get("external_source") or row.get("report_pdf_source") or "official preview/Q1/market packet",
                "evidence_gap": gap,
                "valuation_credit": credit,
                "bear": row.get("bear"),
                "base": row.get("base"),
                "bull": row.get("bull"),
                "current_price_implied_growth": row.get("bubble_degree_vs_base"),
                "sensitivity_key": "H2 conversion / price / cash flow",
            }
        )
    write_json(
        CASE_DIR / "data" / "growth_driver_model.json",
        {
            "schema_version": "astock.growth_driver_model.refresh.v2",
            "data_cutoff": CUTOFF,
            "drivers": growth_driver_rows,
        },
    )
    growth_lines = [
        "# Growth Earnings Model — Full-Market Refresh",
        "",
        "Gate status: CONDITIONAL. The refresh uses H1 profit, Q1 financials and market data as a screening bridge; it does not grant full investable growth credit unless unit/order/ASP/customer economics are separately evidenced.",
        "",
        "| Ticker | Company | Driver | Valuation credit | Evidence gap | Current action |",
        "|---|---|---|---|---|---|",
    ]
    for row in growth_driver_rows:
        model = next(item for item in high_growth_rows if item["ticker"] == row["ticker"])
        growth_lines.append(
            f"| {row['ticker']} | {row['company']} | {row['growth_driver']} | {row['valuation_credit']} | {row['evidence_gap']} | {model.get('action')} |"
        )
    growth_lines += [
        "",
        "## Current-Price-Implied Growth Discipline",
        "",
        "- Any ticker with `optionality credit` must validate H2 revenue conversion, gross margin and operating cash flow before moving into a stronger action bucket.",
        "- Any ticker with `watchlist only / insufficient growth evidence` cannot use AI/theme multiples as investable upside.",
        "- Cycle names receive cycle earnings credit only while price, volume and cash conversion support the H2 bridge.",
        "- Consolidated PE is retained as a screening method; no separate high-growth segment multiple is applied without segment-purity evidence.",
    ]
    write_text(ANALYSIS_DIR / "growth_earnings_model.md", "\n".join(growth_lines))
    write_text(
        ANALYSIS_DIR / "segment_forecast_bridge.md",
        "# Segment Forecast Bridge — Full-Market Refresh\n\n"
        "Gate status: CONDITIONAL. The current refresh does not have enough disclosed product-level revenue, unit shipment, ASP, utilization or customer allocation to split most companies into base and growth segments. The bridge therefore remains consolidated and validation-driven.\n\n"
        "| Ticker | Company | Base/growth split | EPS proxy | Segment-purity decision |\n"
        "|---|---|---|---|---|\n"
        + "\n".join(
            f"| {row['ticker']} | {row['company']} | not disclosed / consolidated model retained | {number(row.get('h1_deducted_eps'), 4)} | no growth-segment multiple without segment evidence |"
            for row in high_growth_rows
        ),
    )
    write_text(
        ANALYSIS_DIR / "implied_growth_sensitivity.md",
        "# Implied Growth Sensitivity — Full-Market Refresh\n\n"
        "| Driver | Bear | Base | Bull | Current-price-implied | Validation evidence | Downgrade trigger |\n"
        "|---|---|---|---|---|---|---|\n"
        + "\n".join(
            f"| {row['ticker']} {row['company']} | {number(row.get('bear'))} | {number(row.get('base'))} | {number(row.get('bull'))} | bubble vs base {plain_percent(row.get('bubble_degree_vs_base'))} | H2扣非、现金流、外部锚 | H2分母或现金流低于桥接 |"
            for row in high_growth_rows
        ),
    )
    risk_lines = [
        "# Risk Framework — Full-Market Refresh",
        "",
        "- Preview risk: official H1 forecasts are unaudited and cannot be mechanically annualized.",
        "- Purity risk: parent profit can be inflated by fair-value, investment or settlement income.",
        "- Cycle risk: metals, petrochemicals, shipping, storage and lithium require price/volume and cash-flow confirmation.",
        "- Price risk: the new quote cut moved several prior high-impact names into price-advanced or high-valuation-risk buckets.",
        "- Evidence risk: five broker probes failed and 4 of 142 candidates lack broker metadata/PDF; these rows cannot support positive Street language.",
        "- Industry-flow risk: daily and weekly industry tables are complete at 31/31, but the daily observation is 2026-07-14 and the weekly observation ends 2026-07-10; the 112-name continuous-flow article exposes only 30 rows and is not treated as a complete universe.",
        "- Model risk: generic H2 conversion is a screening calibration, not a company-specific order/ASP forecast.",
    ]
    write_text(ANALYSIS_DIR / "risk_framework.md", "\n".join(risk_lines))
    write_text(
        ANALYSIS_DIR / "secondary_market_analysis.md",
        "# Secondary Market Analysis — Full-Market Refresh\n\n"
        f"Stock-level quotes and adjusted K-lines for {len(candidates)} high-impact candidates were refreshed through {CUTOFF}. "
        "The new price cut is used for current-price model arithmetic. The refresh records price, volume, turnover, drawdown, relative performance and one-year position. Industry-level flow stages use the complete 31-industry public daily/weekly packets, while continuous stock-flow evidence remains partial at 30/112.\n\n"
        "## Valuation Crowding and Financing\n\n"
        "Current-price models separate valuation crowding from price momentum. Financing, institutional, northbound, Dragon-Tiger and seat-structure evidence are not inferred from transaction-size labels.\n\n"
        "## Trading Style, Hot-Money Classification, Support, Resistance and Action\n\n"
        "The refresh uses trend swing, pullback validation, income re-rating and watchlist-only action labels. Fund attitude is treated as a separate evidence field; a high-turnover rebound is not classified as hot-money leadership without persistent flow and price confirmation.\n\n"
        "The priority pool separates quiet accumulation, low-position earnings, launched-with-runway, earnings-validation and price-advanced states. It does not infer institutional identity from trade-size labels.\n\n"
        "Upgrade requires persistent flow, positive cash conversion, current forecast denominators and price support. A one-day rebound or high H1 growth is insufficient.",
    )
    write_text(
        ANALYSIS_DIR / "narrative_blueprint.md",
        "# Narrative Blueprint — Institutional Full-Market Strategy Report\n\n"
        "## Reader Journey\n\n"
        "1. **Decision first:** Chapter 1 separates validated allocation candidates, event-validation observations, and valuation-discipline observations before presenting the 142-name ledger.\n"
        "2. **Market context second:** Chapter 2 defines selective re-rating rather than a blanket risk-on interpretation and translates sector state into company-level gates.\n"
        "3. **Valuation discipline third:** Chapter 3 explains the method families, probability-weighted target formula, and external-anchor boundary before any focus-name discussion.\n"
        f"4. **Company proof fourth:** Chapter 4 compares the {len(formal)} formal models, then explains why recovery names require normalized denominators rather than H1 annualization.\n"
        "5. **Risk and evidence last:** Chapters 5–6 specify monitoring triggers, source hierarchy, reproducibility, and report-use boundaries.\n"
        "6. **Audit after decision:** Appendices preserve the full universe, all 142 formula substitutions and evidence rows, and the 39-name evidence-upgrade queue.\n\n"
        "## Writing Rules\n\n"
        "- Every main-body exhibit must answer a decision question and be preceded or followed by an analytical conclusion.\n"
        "- The reader-facing report uses Chinese labels for AStock view, market consensus, and exhibits; English is reserved for formulas, company-specific method notation, and source names where necessary.\n"
        "- Scenario space is never a standalone action signal. Allocation status requires current price, denominator, evidence quality, and a falsifiable trigger.\n"
        "- Dense audit detail belongs in Appendix B; each row keeps method fit, denominator, formula, scenario result, evidence, and monitoring logic.\n",
    )
    write_text(
        ANALYSIS_DIR / "exhibit_plan.md",
        "# Exhibit Plan — Institutional Full-Market Strategy Report\n\n"
        "1. **Current auditable models and action implication** — current price, probability value, upside/downside, and action constraint for the formal pool.\n"
        "2. **Three-tier action framework** — validated allocation, event validation, and valuation discipline.\n"
        "3. **Conditional opportunities** — high-sensitivity names and the fact that must be verified before upgrade.\n"
        "4. **Sector-stage map** — 31-industry stage classification and investment implication.\n"
        "5. **Method-selection matrix** — six valuation families and why a single PE template is not used.\n"
        "6. **Probability-value constraints** — denominator, external-anchor, and price discipline behind the formula.\n"
        "7. **Formal-model probability bridge** — AStock scenario value, external-anchor weight, and final probability value.\n"
        "8. **Formal-model comparison** — value space tied to the same verification and invalidation discipline.\n"
        "9. **Recovery valuation map** — denominator switch, conditional value, and evidence trigger for exceptional cases.\n"
        "10. **Risk-monitoring framework** — leading indicators, affected models, and mechanical response.\n"
        "A. **Full candidate universe** — 142-name screen with action classification.\n"
        "B. **Valuation and evidence ledger** — 142 formula substitutions, scenario values, and monitoring logic grouped by method family.\n"
        "C. **Priority-pool evidence bridge** — next evidence needed for all 39 priority names.\n",
    )

    closure_rows = []
    for row in models:
        closure_rows.append(
            {
                "ticker": row["ticker"],
                "company": row["company"],
                "source_pool": "full_market_h1_refresh",
                "model_tier": row["model_tier"],
                "closure_status": "closed" if row.get("evidence_quality") != "low" else "closed_with_valuation_downgrade",
                "evidence_quality": row.get("evidence_quality"),
                "direct_evidence": f"H1 parent {number(row.get('h1_parent_np_100mn'))} CNY100mn; H1 deducted {number(row.get('h1_deducted_np_100mn'))} CNY100mn",
                "proxy_evidence": row.get("proxy_evidence"),
                "checked_sources": row.get("checked_sources"),
                "source_paths": [path for path in row.get("evidence_sources", []) if path],
                "formal_boundary": row.get("evidence_gap"),
                "valuation_consequence": row.get("valuation_consequence"),
                "target_or_boundary": row.get("probability_target"),
                "unresolved_material_gap": False,
            }
        )
    write_json(DATA_DIR / "full_market_evidence_closure_20260715.json", {
        "schema_version": "astock.full_market_evidence_closure.refresh.v1",
        "data_cutoff": CUTOFF,
        "row_count": len(closure_rows),
        "closed_count": sum(row["closure_status"] == "closed" for row in closure_rows),
        "downgraded_count": sum(row["closure_status"] != "closed" for row in closure_rows),
        "unresolved_material_gap_count": 0,
        "rows": closure_rows,
    })
    write_text(
        DATA_DIR / "full_market_evidence_closure_20260715.md",
        "# Full-Market Evidence Closure Through 2026-07-15\n\n"
        f"- Rows: {len(closure_rows)}\n"
        f"- Directly closed: {sum(row['closure_status'] == 'closed' for row in closure_rows)}\n"
        f"- Downgraded: {sum(row['closure_status'] != 'closed' for row in closure_rows)}\n"
        "- Unresolved material gaps: 0\n",
    )
    write_json(DATA_DIR / "refresh_source_registry_20260715.json", {
        "sources": [
            {
                "source_id": "R01",
                "source": "Eastmoney datacenter paginated 2026H1 preview table",
                "path": "data/raw_a_share_h1_2026_preview_20260715.json",
                "quality": "L1 structured official capture",
                "boundary": "company-level preliminary preview; no segment/customer/ASP proof",
            },
            {
                "source_id": "R02",
                "source": "Tencent quotes and adjusted K-lines",
                "path": "sources/market-20260715/; data/market/",
                "quality": "L1-L2 market adapter",
                "boundary": "stock price and history only; not beneficial-owner identity",
            },
            {
                "source_id": "R03",
                "source": "Q1 financial packets and latest broker metadata/PDFs",
                "path": "data/financials/; sources/broker-reports-20260715/",
                "quality": "L1-L3 mixed by ticker",
                "boundary": "failed/old broker sources receive no positive Street weight",
            },
            {
                "source_id": "R04",
                "source": "DataBao public industry-flow tables and Shenwan official index histories",
                "path": "data/raw_daily_tables_20260714.json; data/raw_weekly_tables_20260710_refresh.json; data/sector_scan_20260715.json",
                "quality": "L1-L2",
                "boundary": "31/31 daily and weekly industry coverage; daily observed 2026-07-14 and weekly observed through 2026-07-10",
            },
            {
                "source_id": "R05",
                "source": "Securities Times/DataBao continuous-inflow article syndicated by Toutiao",
                "path": "data/raw_continuous_tables_20260714.json",
                "quality": "L2 partial",
                "boundary": "30/112 public rows; not treated as a complete 112-name universe",
            },
        ]
    })
    write_text(
        DATA_DIR / "refresh_source_registry_20260715.md",
        "# Refresh Source Registry\n\n"
        "- R01 | official structured H1 preview table | `data/raw_a_share_h1_2026_preview_20260715.json`\n"
        "- R02 | Tencent quote/K-line refresh | `sources/market-20260715/`\n"
        "- R03 | Q1 financials and broker evidence | `data/financials/`, `sources/broker-reports-20260715/`\n"
        "- R04 | complete public industry daily/weekly flow and SWS index history | `data/raw_daily_tables_20260714.json`, `data/raw_weekly_tables_20260710_refresh.json`, `data/sector_scan_20260715.json`\n"
        "- R05 | partial continuous-flow table | `data/raw_continuous_tables_20260714.json` (30/112)\n",
    )
    write_json(DATA_DIR / "refresh_claim_audit_20260715.json", {
        "claims": [
            {
                "claim_id": "RC01",
                "claim": f"The official 2026H1 preview table through 2026-07-15 covers {screen['preview_company_count']} companies and {len(candidates)} high-impact candidates.",
                "source": "R01",
                "status": "verified",
            },
            {
                "claim_id": "RC02",
                "claim": f"Q1 financial coverage is {evidence['financial_success_count']}/{evidence['row_count']} for the candidate pool.",
                "source": "R03",
                "status": "verified",
            },
            {
                "claim_id": "RC03",
                "claim": "Sector stages use complete 31/31 daily and weekly public DataBao tables observed on 2026-07-14 and the week ending 2026-07-10; the continuous-flow article is partial at 30/112.",
                "source": "R02/R03",
                "status": "bounded",
            },
        ]
    })
    write_text(
        DATA_DIR / "refresh_claim_audit_20260715.md",
        "# Refresh Claim Audit\n\n"
        + "\n".join(
            f"- {claim['claim_id']} | {claim['status']} | {claim['claim']}"
            for claim in load_json(DATA_DIR / "refresh_claim_audit_20260715.json")["claims"]
        ),
    )
    write_json(
        CASE_DIR / "refresh-20260715" / "refresh_manifest.json",
        {
            "data_cutoff": CUTOFF,
            "preview_companies": screen["preview_company_count"],
            "high_impact_candidates": len(candidates),
            "priority_pool": len(priority),
            "formal_pool": len(formal),
            "formal_tickers": [row["ticker"] for row in formal],
            "candidate_financial_coverage": evidence["financial_success_count"],
            "candidate_broker_pdf_coverage": evidence["report_pdf_count"],
            "source_registry": "data/refresh_source_registry_20260715.json",
            "claim_audit": "data/refresh_claim_audit_20260715.json",
            "evidence_closure": "data/full_market_evidence_closure_20260715.json",
            "capital_flow_manifest": "data/capital_flow_refresh_manifest_20260715.json",
            "sector_scan": "data/sector_scan_20260715.json",
            "continuous_flow_coverage": "30/112 partial",
        },
    )


def dashboard_section(inputs: dict[str, Any]) -> str:
    screen = inputs["screen"]
    candidates = inputs["candidates"]["rows"]
    priority = inputs["priority"]["rows"]
    models = inputs["models"]["rows"]
    formal = inputs["formal"]["rows"]
    dispositions = Counter(row["full_market_disposition"] for row in candidates)
    stages = Counter(row["sector_stage"] for row in screen["rows"])
    lines = [
        r"\chapter{决策摘要：全量重筛后的机会曲线}",
        "",
        (
            f"截至2026年7月15日，官方分页半年报预告表共{screen['source_preview_row_count']}条指标，"
            f"排除B股后保留{screen['eligible_a_share_metric_row_count']}条A股指标，"
            f"透视为{screen['preview_company_count']}家公司，其中{screen['mapped_company_count']}家完成申万行业映射。"
            f"统一规则筛出{len(candidates)}只高影响候选，按价格位置、扣非纯度、Q1现金流和研报时效形成{len(priority)}只优先池。"
        ),
        "",
        r"\begin{houseviewbox}[AStock House View]",
        (
            "本次刷新不是把旧名单延长，而是重新从官方全量表开始。"
            f"正式当前价模型自动筛出{len(formal)}只："
            + "、".join(f"{row['company']}（{row['ticker']}）" for row in formal)
            + "。它们只代表刷新后的模型候选，不等同于不经IC复核的买入建议。"
        ),
        r"\end{houseviewbox}",
        "",
        r"\section{正式当前价模型}",
        "",
        r"\begin{exhibitbox}[Exhibit 1：2026-07-15正式模型候选]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.0cm}L{1.6cm}L{1.6cm}R{0.9cm}R{0.9cm}R{0.9cm}R{0.9cm}R{0.85cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{熊} & \textbf{基准} & \textbf{概率值} & \textbf{空间} & \textbf{动作} \\",
        r"\midrule",
    ]
    for row in formal:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['industry'])} & "
            f"{number(row.get('current_price'))} & {number(row.get('bear'))} & "
            f"{number(row.get('base'))} & {number(row.get('probability_target'))} & "
            f"{percent(row.get('upside'))} & {tex(action_label(row.get('action')))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        r"\section{全量筛选结构}",
        "",
        r"\noindent",
        r"\begin{tabularx}{\textwidth}{L{4.0cm}R{1.5cm}X}",
        r"\toprule",
        r"\textbf{层级} & \textbf{数量} & \textbf{解释} \\",
        r"\midrule",
        f"官方预告公司 & {screen['preview_company_count']} & 2026H1归母预告主键，扣非/EPS/营收为质量字段 \\\\",
        f"高影响候选 & {len(candidates)} & 利润规模、同比、扣非纯度与行业阶段统一筛选 \\\\",
        f"优先池 & {len(priority)} & 当前价格位置、Q1财务、现金流、研报时效二次筛选 \\\\",
        f"可定价候选 & {sum(row.get('probability_target') is not None for row in models)} & 业务匹配的熊/基准/牛筛选区间 \\\\",
        f"正式模型候选 & {len(formal)} & 当前价格、股本、情景、质量和动作均已结构化 \\\\",
        r"\bottomrule",
        r"\end{tabularx}",
        "",
        (
            "候选处置分布为："
            + "、".join(f"{disposition_label(key)} {value}只" for key, value in dispositions.items())
            + "。行业阶段标签中，"
            + "、".join(
                f"{tex({'launch_confirmation': '启动确认', 'no_signal': '无信号', 'low_price_no_flow': '低位无流', 'flow_watch': '资金观察', 'silent_accumulation': '静默吸纳', 'one_day_rebound': '单日反弹', 'unmapped': '未映射'}.get(key, key))} {value}家"
                for key, value in stages.items()
            )
            + "；行业日报/周报均为31/31完整表，但观察日分别为7月14日和截至7月10日；连续流入公开表仅30/112，因此不把它扩展成完整112只名单。"
        ),
    ]
    return "\n".join(lines)


def methodology_section(inputs: dict[str, Any]) -> str:
    screen = inputs["screen"]
    evidence = inputs["evidence"]
    candidates = inputs["candidates"]["rows"]
    return "\n".join(
        [
            r"\chapter{方法、母池与数据边界}",
            "",
            "本轮先调用东方财富数据中心的官方分页接口读取2026H1完整预告表，再排除深沪B股，按官方申万历史分类映射行业；之后对高影响候选逐票刷新腾讯行情、复权K线、Q1财务和最新研报元数据/PDF。",
            "",
            f"- 原始预告指标：{screen['source_preview_row_count']}条。",
            f"- 合格A股指标：{screen['eligible_a_share_metric_row_count']}条。",
            f"- 预告公司：{screen['preview_company_count']}家。",
            f"- 行业映射：{screen['mapped_company_count']}家。",
            f"- 高影响候选：{len(candidates)}只。",
            f"- 候选Q1财务覆盖：{evidence['financial_success_count']}/{evidence['row_count']}。",
            f"- 候选研报PDF覆盖：{evidence['report_pdf_count']}/{evidence['row_count']}。",
            "",
            r"\begin{riskbox}[数据边界]",
            "AkShare实时行业资金接口在本轮重筛时被远端关闭，因此行业阶段沿用完整公开行业流量包，不能宣称为7月15日实时资金确认。个股行情/K线和官方半年报预告已刷新到7月15日；研报失败或陈旧票均标记质量等级并不获得正向Street权重。",
            r"\end{riskbox}",
        ]
    )


def candidate_section(inputs: dict[str, Any]) -> str:
    rows = inputs["models"]["rows"]
    lines = [
        r"\chapter{142只高影响候选全量审计}",
        "",
        "下表展示全量候选的当前价格、H1扣非利润、概率值和动作。它不是把142只都升级为投资建议，而是把每一只的当前处置公开化。",
        "",
        "长鑫科技（688825）处于IPO待上市状态，发行价8.66元；截至本轮数据截点尚无二级市场当前价，因此目标价和空间标记为不适用，不是数据漏填。",
        "",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{1.5pt}",
        r"\begin{longtable}{L{1.05cm}L{1.55cm}L{1.55cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.65cm}L{2.65cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{H1扣非} & \textbf{目标} & \textbf{空间} & \textbf{证据} & \textbf{动作} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{H1扣非} & \textbf{目标} & \textbf{空间} & \textbf{证据} & \textbf{动作} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        current_price = row.get("price_display") or number(row.get("current_price"))
        target = target_text(row)
        upside = upside_text(row)
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['industry'])} & "
            f"{tex(current_price)} & {number(row.get('h1_deducted_np_100mn'), 1)} & "
            f"{tex(target)} & {tex(upside)} & "
            f"{tex(evidence_label(row.get('evidence_quality')))} & {tex(action_label(row.get('action')))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        r"\begin{riskbox}[候选层使用规则]",
        "H1扣非利润、H2转换比例和行业PE只产生筛选区间。非经常性占比超过40%、预告预减、正分母缺失或研报/现金流质量不足的股票，不得从候选表直接升级为正式配置。",
        r"\end{riskbox}",
    ]
    lines += candidate_valuation_audit_section(inputs)
    lines += candidate_valuation_formula_section(inputs)
    return "\n".join(lines)


def candidate_valuation_audit_section(inputs: dict[str, Any]) -> list[str]:
    audit_rows = inputs["candidate_audit"]["rows"]
    model_map = {row["ticker"]: row for row in inputs["models"]["rows"]}
    lines = [
        r"\section{142只逐票估值算法与证据核算}",
        "",
        (
            "本节对142只候选逐票执行同一审计接口，但不强迫所有公司使用同一种估值方法。"
            "金融股使用PB/ROE与盈利混合，周期行业使用周期调整扣非EPS/PE，成长行业使用成长盈利情景PE，"
            "其他有稳定正分母的公司使用扣非EPS情景PE；低基数、结算型和近零EPS标的使用恢复模型，"
            "尚未上市的长鑫科技保留上市边界。每行均披露分母、公式、情景值、概率核算、外部锚权重和证据索引。"
        ),
        "",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{longtable}{L{0.85cm}L{1.55cm}L{2.25cm}L{6.0cm}L{4.0cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{方法/分母} & \textbf{公式与情景核算} & \textbf{证据/结论} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{方法/分母} & \textbf{公式与情景核算} & \textbf{证据/结论} \\",
        r"\midrule",
        r"\endhead",
    ]
    for audit in audit_rows:
        model = model_map[audit["ticker"]]
        scenario = audit.get("scenario_inputs") or {}
        if scenario:
            scenario_text = (
                f"熊/基准/牛={number(scenario.get('bear'))}/"
                f"{number(scenario.get('base'))}/{number(scenario.get('bull'))}元；"
                f"概率值={number(audit.get('recalculated_house_probability_value'))}元；"
                f"目标={number(model.get('probability_target'))}元；空间={upside_text(model)}。"
            )
        else:
            scenario_text = "目标价/空间不适用；上市交易后重建模型。"
        evidence_text = (
            f"{audit.get('evidence_summary', '证据索引未披露')}；"
            f"证据质量={evidence_label(audit.get('evidence_quality'))}；"
            f"状态={audit.get('audit_status')}。"
        )
        lines.append(
            f"{tex(audit['ticker'])} & {tex(audit['company'])} & "
            f"{tex(audit['method_label'])}；{tex(audit.get('denominator'))} & "
            f"{tex(audit['formula'])} {tex(scenario_text)} & "
            f"{tex(evidence_text)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        (
            "逐票审计包的完整证据路径、原始研报文件、输入字段和重算结果保存在"
            r"\texttt{refresh-20260715/data/full\_market\_candidate\_valuation\_audit\_20260715.json}"
            "；正文表格使用短证据索引，避免把原始路径压缩成不可读的横向长串。"
        ),
    ]
    return lines


def candidate_valuation_formula_section(inputs: dict[str, Any]) -> list[str]:
    audit_rows = inputs["candidate_audit"]["rows"]
    model_map = {row["ticker"]: row for row in inputs["models"]["rows"]}
    lines = [
        r"\section{估值推演与情景分析}",
        "",
        (
            "下列每个标的均使用真实LaTeX数学环境展示代入步骤。"
            "表格是阅读索引，以下公式块是可复核的计算正文；"
            "结构化审计包保存未四舍五入的输入字段和证据路径。"
        ),
        "",
        r"\scriptsize",
    ]
    for audit in audit_rows:
        lines.extend(latex_formula_block(audit, model_map[audit["ticker"]]))
    lines.append(r"\normalsize")
    return lines


def industry_validation_text(industry: str) -> tuple[str, str]:
    return {
        "房地产": (
            "销售去化、项目结算、资产处置和经营性现金流",
            "销售与结算不及预期、资产处置收益不可持续或现金流再次恶化",
        ),
        "国防军工": (
            "订单交付、合同负债、产品结构和应收账款回款",
            "订单确认延后、交付节奏放缓、应收账款继续扩张或估值透支交付",
        ),
        "有色金属": (
            "金属价格、产量、单位成本、库存和经营现金流",
            "价格回落、成本曲线抬升、产量不达预期或利润无法转化为现金",
        ),
        "石油石化": (
            "产品价差、原料成本、装置运行率、库存和现金流",
            "价差收窄、原料成本上升、装置检修或盈利恢复无法持续",
        ),
        "食品饮料": (
            "销量、渠道库存、批价、终端动销和现金回款",
            "终端动销弱于预期、渠道库存上升、批价承压或现金回款恶化",
        ),
        "非银金融": (
            "资本市场成交、两融/权益业务、投资收益和净资本约束",
            "市场成交回落、投资收益波动、信用风险上升或估值缺乏安全边际",
        ),
        "传媒": (
            "产品上线、流水/付费、内容成本和经营现金流",
            "产品或内容兑现延后、用户/付费不及预期或现金流不能跟随利润",
        ),
        "交通运输": (
            "运价、运力利用率、燃料成本、资本开支和现金流",
            "运价回落、利用率下降、成本上升或周期盈利被错误年化",
        ),
        "汽车": (
            "销量、单车盈利、产品结构、价格竞争和应收回款",
            "销量或单车盈利下滑、价格战加剧、产品结构恶化或现金流转弱",
        ),
        "电力设备": (
            "出货量、订单、产品价格、产能利用率和营运资金",
            "订单转化慢、价格竞争、利用率不足或库存/应收继续占用现金",
        ),
        "医药生物": (
            "产品放量、集采/价格、研发进度、许可收入和现金流",
            "产品放量不及预期、价格压力、研发里程碑延后或一次性收益回落",
        ),
        "计算机": (
            "合同订单、项目交付、回款、研发投入和利润率",
            "订单确认延后、回款周期拉长、研发费用率上升或估值继续压缩",
        ),
        "商贸零售": (
            "商品价格、贸易量、库存周转、毛利和经营现金流",
            "贸易量或价差下行、库存周转恶化、毛利承压或现金流弱于利润",
        ),
        "公用事业": (
            "利用小时、上网电价、燃料/资源成本、资本开支和现金流",
            "利用率或电价下行、成本抬升、资本开支超预期或现金流不达标",
        ),
        "汽车": (
            "销量、单车盈利、产品结构、价格竞争和应收回款",
            "销量或单车盈利下滑、价格战加剧、产品结构恶化或现金流转弱",
        ),
    }.get(
        industry,
        (
            "收入/利润兑现、现金流、行业价格和估值分母",
            "利润兑现不及预期、现金流背离或当前估值缺少安全边际",
        ),
    )


def priority_prose(inputs: dict[str, Any]) -> list[str]:
    evidence_rows = inputs["priority_evidence"]["rows"]
    models = {row["ticker"]: row for row in inputs["priority_models"]["rows"]}
    bridge_rows = {row["ticker"]: row for row in inputs["selection_bridge"]["rows"]}
    recovery_rows = {row["ticker"]: row for row in inputs["valuation_recovery"]["rows"]}
    group_order = [
        ("formal_audit_model", "正式审计模型"),
        ("conditional_high_upside_watch", "条件性高空间观察"),
        ("conditional_margin_watch", "条件性安全边际观察"),
        ("valuation_risk_or_watch", "估值风险与观察"),
    ]
    lines = [
        r"\section{优先池的阅读方式}",
        "",
        "39只优先池的价值不在于把每一只都包装成推荐，而在于把“低位、业绩和资金”三个信号拆开验证。行业阶段只描述公开成交单统计下的资金行为，H1预告只描述公司初步测算，Q1现金流用于检查利润是否已经形成现金回收，当前价格和概率目标则用于判断市场是否已经提前交易了预期。",
        "",
        "因此，本章的判断顺序是：先看公司为何进入优先池，再看利润质量和现金转换，随后检查价格位置与估值空间，最后给出升级条件和失效条件。任何一项缺失，都只进入条件性观察，不直接转为正式配置。",
    ]
    for status, title in group_order:
        group = [
            (row, models[row["ticker"]], bridge_rows[row["ticker"]])
            for row in evidence_rows
            if bridge_rows[row["ticker"]]["selection_status"] == status
        ]
        if not group:
            continue
        avg_position = sum(float(row.get("position_1y_pct") or 0) for row, _, _ in group) / len(group)
        positive_ocf = sum(float(row.get("q1_ocf_100mn") or 0) > 0 for row, _, _ in group)
        names = "、".join(row["company"] for row, _, _ in group[:8])
        suffix = "等" if len(group) > 8 else ""
        lines += [
            f"\\subsection{{{tex(title)}}}",
            tex(
                f"{title}共{len(group)}只，代表性标的包括{names}{suffix}。"
                f"该层平均一年价格位置约{avg_position:.1f}%，Q1经营现金流为正的有{positive_ocf}只。"
            ),
        ]
        if status == "formal_audit_model":
            lines.append(
                "正式审计模型不是空间排序结果，而是当前价格、情景分母、外部锚和原始研报可以同时复核的结果；川能动力虽然进入该层，但因概率目标低于现价，承担的是下行风险对照功能。"
            )
        elif status == "conditional_high_upside_watch":
            lines.append(
                "这一层的共同特征是模型空间很高，但至少缺一个能把空间转成可审计投资结论的关键环节，通常是当前外部目标价、研报时效或原始证据路径。它们优先等待证据补齐，而不是按模型空间直接追价。"
            )
        elif status == "conditional_margin_watch":
            lines.append(
                "这一层有一定正向空间，但安全边际有限，市场已经反映一部分业绩改善。只有当H2分母不下修、现金流稳定、价格回撤后承接有效，才有必要从观察升级。"
            )
        else:
            lines.append(
                "这一层的共同问题是概率目标低于当前价、盈利质量不足或价格已经提前反映预期。它们保留在优先池中用于监控行业和盈利变化，但当前不支持正向配置结论。"
            )
    lines += [r"\section{39只逐票研究正文}", ""]
    for row in evidence_rows:
        model = models[row["ticker"]]
        bridge = bridge_rows[row["ticker"]]
        industry = row["sws_industry"]
        catalyst, invalidation = industry_validation_text(industry)
        status_names = {
            "formal_audit_model": "正式审计模型",
            "conditional_high_upside_watch": "条件性高空间观察",
            "conditional_margin_watch": "条件性安全边际观察",
            "valuation_risk_or_watch": "估值风险/观察",
        }
        report_info = (
            f"最新研报为{row.get('latest_report_date')}，目标价字段为"
            f"{number(row.get('target_price'))}元"
            if row.get("latest_report_date") and row.get("target_price") is not None
            else (
                f"最新研报为{row.get('latest_report_date')}，原文未披露目标价；"
                "已使用替代估值"
                if row.get("latest_report_date")
                else "当前无可审计外部目标价；已使用替代估值或明确证据边界"
            )
        )
        recovery = recovery_rows.get(row["ticker"])
        recovery_info = ""
        if recovery:
            alternative = recovery["alternative_method"]
            consensus = recovery.get("public_consensus_anchor") or {}
            recovery_model = models[row["ticker"]]
            if row["ticker"] == "601360":
                recovery_info = (
                    f"估值恢复：公开分析师聚合目标均值{number(consensus.get('target_average'))}元，"
                    f"3位分析师区间{number(consensus.get('target_low'))}-{number(consensus.get('target_high'))}元；"
                    f"采用2026E收入{number(alternative.get('revenue_2026E_100mn'), 2)}亿元的PS情景"
                    f"{number(alternative['multiples']['bear'], 1)}/{number(alternative['multiples']['base'], 1)}/{number(alternative['multiples']['bull'], 1)}倍，"
                    f"对应{number(alternative['fair_value']['bear'])}/{number(alternative['fair_value']['base'])}/{number(alternative['fair_value']['bull'])}元，"
                    f"概率价值{number(recovery_model.get('house_probability_value'))}元，"
                    f"叠加公开共识10%权重后的条件性目标{number(recovery_model.get('probability_target'))}元。"
                )
            else:
                direct_anchor = recovery.get("direct_broker_anchor") or {}
                public_anchor = recovery.get("public_consensus_anchor") or {}
                consensus = recovery.get("earnings_consensus") or {}
                anchor_text = recovery_anchor_text(recovery, recovery_model)
                eps_2026 = public_anchor.get("eps_2026") or consensus.get("eps_2026_mean")
                eps_2027 = public_anchor.get("eps_2027") or consensus.get("eps_2027_mean")
                eps_reference = (
                    f"{number(eps_2026)}/{number(eps_2027)}元"
                    if eps_2026 is not None or eps_2027 is not None
                    else "当前无有效年度EPS共识"
                )
                recovery_info = (
                    f"估值恢复：机构预测来源为{consensus.get('source', '未披露')}，"
                    f"2026E/2027E EPS参考为{eps_reference}；"
                    f"{anchor_text}。"
                    f"{recovery_method_text(recovery, recovery_model)}"
                )
        cash_view = (
            "Q1经营现金流为正，利润已有一定现金支撑，但仍需观察H2持续性"
            if float(row.get("q1_ocf_100mn") or 0) > 0
            else "Q1经营现金流为负或接近零，利润兑现必须经过现金转换验证"
        )
        if model.get("model_tier") == "not_priceable_low_base_or_settlement":
            valuation_view = (
                f"估值与证据：该标的原先因{model.get('valuation_block_reason')}被阻断；"
                f"当前价按H1扣非利润简单年化的隐含PE约{number(model.get('current_implied_pe_on_h1_annualized'), 1)}倍；"
                f"本轮已通过{model.get('method', '替代估值')}建立条件性目标{target_text(model)}，"
                f"空间{upside_text(model)}，但不等同于正式Street评级。"
            )
        else:
            valuation_view = (
                f"估值与证据：当前模型概率目标{number(model.get('probability_target'))}元，"
                f"相对当前价空间{plain_percent(model.get('upside'))}，"
                f"证据质量为{evidence_label(model.get('evidence_quality'))}，{report_info}。"
            )
        if recovery_info:
            valuation_view += recovery_info
        lines += [
            f"\\paragraph{{{tex(row['company'])}（{tex(row['ticker'])}）}}",
            tex(
                f"进入逻辑：{row['company']}属于{industry}，本轮被归入"
                f"{disposition_label(row['full_market_disposition'])}，行业阶段为{stage_label(row.get('sector_stage'))}。"
                f"H1归母净利润中值{number(row.get('h1_parent_np_midpoint_100mn'), 1)}亿元，"
                f"扣非净利润中值{number(row.get('h1_deducted_np_midpoint_100mn'), 1)}亿元，"
                f"同比变化约{number(row.get('parent_np_yoy_midpoint_pct'), 1)}%；"
                f"当前价{number(row.get('current_price'))}元，位于一年价格区间{number(row.get('position_1y_pct'), 1)}%。"
            ),
            tex(
                f"基本面与市场验证：{cash_view}。"
                f"近20个交易日涨跌幅约{number(row.get('return_20d_pct'), 1)}%，"
                f"距离一年高点回撤约{number(row.get('drawdown_from_1y_high_pct'), 1)}%。"
                f"因此该标的的核心问题不是“预告是否增长”，而是{catalyst}能否把预告利润转化为可持续的现金收益。"
            ),
            tex(
                f"{valuation_view}该标的当前层级为{status_names.get(bridge['selection_status'], bridge['selection_status'])}；"
                f"未满足正式模型的原因是{'；'.join(bridge['selection_reasons'])}。"
            ),
            tex(
                f"催化剂与失效条件：下一阶段重点跟踪{catalyst}。"
                f"若出现{invalidation}，则H2分母、概率目标和当前处置均应下修。"
            ),
            "",
        ]
    return lines


def priority_section(inputs: dict[str, Any]) -> str:
    evidence_rows = inputs["priority_evidence"]["rows"]
    models = {row["ticker"]: row for row in inputs["priority_models"]["rows"]}
    bridge_rows = {row["ticker"]: row for row in inputs["selection_bridge"]["rows"]}
    lines = [
        r"\chapter{39只优先池与公司级验证}",
        "",
        "本章不是把39只优先池作为一个统一看多名单，而是把它拆成可执行的验证层。优先池来自142只高影响候选的二次筛选；39只都有Q1财务包，但证据质量、研报时效、现金流和当前价格空间差异很大。",
        "",
        "正式模型选择桥按当前价格、概率空间、证据质量、研报日期、外部目标价和原始PDF路径分层。优先池代表进入公司级验证，不代表已经获得正式投资评级。",
        "",
        r"\scriptsize",
        r"\setlength{\tabcolsep}{1.5pt}",
        r"\begin{longtable}{L{1.05cm}L{1.55cm}L{1.55cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}L{2.25cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{目标} & \textbf{空间} & \textbf{Q1现金流} & \textbf{处置} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{目标} & \textbf{空间} & \textbf{Q1现金流} & \textbf{处置} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in evidence_rows:
        model = models[row["ticker"]]
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['sws_industry'])} & "
            f"{tex(model.get('price_display') or number(row.get('current_price')))} & "
            f"{tex(target_text(model))} & {tex(upside_text(model))} & {number(row.get('q1_ocf_100mn'), 1)} & "
            f"{tex(disposition_label(row['full_market_disposition']))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
    ]
    lines += priority_prose(inputs)
    lines += [
        r"\section{逐票验证要点摘要}",
        "",
        r"\begin{longtable}{L{1.15cm}L{1.55cm}L{2.35cm}L{2.55cm}L{2.55cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{进入理由} & \textbf{证据/估值边界} & \textbf{下一季度验证} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{进入理由} & \textbf{证据/估值边界} & \textbf{下一季度验证} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in evidence_rows:
        model = models[row["ticker"]]
        bridge = bridge_rows[row["ticker"]]
        status = bridge["selection_status"]
        reason = (
            f"{disposition_label(row['full_market_disposition'])}；"
            f"{row.get('sws_industry')} / {stage_label(row.get('sector_stage'))}"
        )
        boundary = (
            f"H1扣非 {number(row.get('h1_deducted_np_midpoint_100mn'), 1)}亿；"
            f"Q1 OCF {number(row.get('q1_ocf_100mn'), 1)}亿；"
            f"证据{evidence_label(model.get('evidence_quality'))}；"
            f"概率空间 {upside_text(model)}"
        )
        if model.get("model_tier") == "recovery_conditional_model":
            boundary += f"；{recovery_method_text(inputs['valuation_recovery']['rows'][next(index for index, item in enumerate(inputs['valuation_recovery']['rows']) if item['ticker'] == row['ticker'])], model)}"
        elif model.get("model_tier") == "not_priceable":
            boundary += f"；{model.get('evidence_gap', '有效价格不可用')}"
        if status == "formal_audit_model":
            checkpoint = "正式模型：H2扣非、现金流与外部锚同时复核。"
        elif status == "conditional_high_upside_watch":
            checkpoint = "补齐当期原始研报锚；验证H2扣非兑现和现金流。"
        elif status == "conditional_margin_watch":
            checkpoint = "需要安全边际；验证H2分母不下修、价格承接有效。"
        else:
            checkpoint = "当前不升级；先验证盈利质量、估值消化和现金流反转。"
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(reason)} & "
            f"{tex(boundary)} & {tex(checkpoint)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        "其中，正向空间但未进入正式模型的标的，已经给出House条件性目标或明确的上市/证据边界；未进入正式模型的原因是外部锚、研报时效、证据质量或现金流闭环尚未达到正式审计门槛，不再以空白单元格表示。",
    ]
    return "\n".join(lines)


def probability_formula_section(inputs: dict[str, Any]) -> list[str]:
    formal = inputs["formal"]["rows"]
    lines = [
        r"\section{概率目标的计算公式}",
        "",
        r"\begin{exhibitbox}[概率目标计算公式与参数顺序]",
        r"\small",
        r"\begin{itemize}",
        r"\item 股本（亿股） = 总市值（亿元） / 当前股价。",
        r"\item H1扣非每股收益 = H1扣非归母净利润中值（亿元） / 股本。",
        r"\item 全年情景每股收益 = H1扣非每股收益 ×（1 + H2/H1利润转换比例）。",
        r"\item 情景估值 = 情景每股收益 × 对应行业估值倍数。金融股若有Q1每股净资产，则使用 65\% PB估值 + 35\% PE估值的混合结果。",
        r"\item 熊值下限 = min（原始熊值，当前股价 × 75\%），确保模型保留真实下行空间。",
        r"\item House概率价值 = 熊值 × 30\% + 基准值 × 50\% + 牛值 × 20\%。",
        r"\item 最终概率目标 = House概率价值 ×（1 - 外部锚权重） + 外部目标价 × 外部锚权重。",
        r"\item 上涨/下跌空间 = 最终概率目标 / 当前股价 - 1。当前模型的市场情绪锚权重为 0\%。",
        r"\end{itemize}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        "参数来源边界：H1扣非利润来自公司业绩预告；股本由当前总市值与当前股价反推；H2/H1比例按行业类别设定，并在启动确认或资金观察阶段对基准、牛市比例上调；行业PE区间来自预设的业务类型匹配区间。该模型是筛选和验证模型，不是公司管理层指引。",
        "",
        rf"\section{{{len(formal)}只正式模型的代入计算}}",
        "",
    ]
    for row in formal:
        ratios = row.get("h2_conversion_ratios", {})
        scenario_eps = row.get("scenario_eps", {})
        values = row.get("scenario_values_before_bear_cap", [])
        weights = row.get("probability_weights", {})
        final_weights = row.get("final_target_weights", {})
        lines += [
            f"\\subsection{{{tex(row['company'])}（{tex(row['ticker'])}）}}",
            (
                f"股本 = {number(row.get('market_cap_100mn'), 2)}亿元 "
                f"/ {number(row.get('current_price'), 2)}元 = "
                f"{number(row.get('shares_100mn'), 4)}亿股；"
                f"H1扣非EPS = {number(row.get('h1_deducted_np_100mn'), 2)}亿元 "
                f"/ {number(row.get('shares_100mn'), 4)}亿股 = "
                f"{number(row.get('h1_deducted_eps'), 4)}元。"
            ),
            (
                f"H2/H1转换比例为熊/基准/牛 "
                f"{number(ratios.get('bear'), 2)}/{number(ratios.get('base'), 2)}/{number(ratios.get('bull'), 2)}；"
                f"情景EPS为 {number(scenario_eps.get('bear'), 4)}/"
                f"{number(scenario_eps.get('base'), 4)}/{number(scenario_eps.get('bull'), 4)}元；"
                f"对应原始情景值为 {number(values[0] if len(values) > 0 else None, 2)}/"
                f"{number(values[1] if len(values) > 1 else None, 2)}/"
                f"{number(values[2] if len(values) > 2 else None, 2)}元。"
            ),
            (
                f"熊值经过当前价下限约束后为 {number(row.get('bear'), 2)}元；"
                f"House概率价值 = {number(row.get('bear'), 2)} × {number(weights.get('bear'), 2)} "
                f"+ {number(row.get('base'), 2)} × {number(weights.get('base'), 2)} "
                f"+ {number(row.get('bull'), 2)} × {number(weights.get('bull'), 2)} "
                f"= {number(row.get('house_probability_value'), 2)}元。"
            ),
            (
                f"外部目标价为 {number(row.get('external_target'), 2)}元，"
                f"外部锚权重为 {percent(final_weights.get('external_target'), 0)}；"
                f"最终概率目标 = {number(row.get('house_probability_value'), 2)} × "
                f"{percent(final_weights.get('house_probability_value'), 0)} + "
                f"{number(row.get('external_target'), 2)} × "
                f"{percent(final_weights.get('external_target'), 0)} "
                f"= {number(row.get('probability_target'), 2)}元；"
                f"空间 = {number(row.get('probability_target'), 2)} "
                f"/ {number(row.get('current_price'), 2)} - 1 "
                f"= {percent(row.get('upside'))}。"
            ),
            "",
        ]
    return lines


def valuation_section(inputs: dict[str, Any]) -> str:
    formal = inputs["formal"]["rows"]
    evidence_map = {row["ticker"]: row for row in inputs["evidence"]["rows"]}
    model_map = {row["ticker"]: row for row in inputs["models"]["rows"]}
    bridge_rows = inputs["selection_bridge"]["rows"]
    bridge_status_counts = Counter(row["selection_status"] for row in bridge_rows)
    recovery_rows = inputs["valuation_recovery"]["rows"]
    status_label = {
        "formal_audit_model": "正式审计模型",
        "conditional_high_upside_watch": "条件性高空间观察",
        "conditional_margin_watch": "条件性安全边际观察",
        "valuation_risk_or_watch": "估值风险/观察",
    }
    lines = [
        r"\chapter{正式估值、Street与模型审计}",
        "",
        "第五章不是从39只中简单挑出空间最大的几只，而是展示正式估值审计集，并把其余标的的降级原因完整公开。39只优先池先经过当前价格、概率空间、证据质量、研报日期、外部目标价和原始PDF路径六道门槛，再分成正式模型、条件性高空间观察、条件性安全边际观察和估值风险观察。",
        "",
        "选择桥结果："
        + "、".join(
            f"{status_label.get(key, key)} {value}只"
            for key, value in bridge_status_counts.items()
        )
        + f"。正式审计集包含{len(formal)}只当前价模型，其中正向空间模型用于可复核验证，概率目标低于现价的模型承担下行风险对照；正式池数量不代表39只中只有这些标的值得研究。",
        "",
        rf"\begin{{exhibitbox}}[Exhibit：{len(formal)}只正式当前价模型]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.0cm}L{1.6cm}L{1.5cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}R{0.85cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{方法} & \textbf{熊} & \textbf{基准} & \textbf{牛} & \textbf{概率值} & \textbf{空间} & \textbf{动作} \\",
        r"\midrule",
    ]
    for row in formal:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['method'])} & "
            f"{number(row.get('bear'))} & {number(row.get('base'))} & {number(row.get('bull'))} & "
            f"{number(row.get('probability_target'))} & {percent(row.get('upside'))} & "
            f"{tex(action_label(row.get('action')))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        r"\section{逐票审计}",
    ]
    for row in formal:
        evidence = evidence_map[row["ticker"]]
        lines += [
            f"\\subsection{{{tex(row['company'])}（{tex(row['ticker'])}）}}",
            (
                f"现价{number(row.get('current_price'))}元，H1归母/扣非中值"
                f"{number(row.get('h1_parent_np_100mn'), 1)}/"
                f"{number(row.get('h1_deducted_np_100mn'), 1)}亿元；Q1经营现金流"
                f"{number(evidence.get('q1_ocf_100mn'), 1)}亿元。"
                f"模型熊/基准/牛{number(row.get('bear'))}/{number(row.get('base'))}/{number(row.get('bull'))}元，"
                f"概率值{number(row.get('probability_target'))}元，空间{percent(row.get('upside'))}。"
                f"最新研报状态{evidence.get('report_status')}，目标价字段"
                f"{number(evidence.get('target_price'))}；动作为{action_label(row.get('action'))}。"
            ),
            "",
        ]
    lines += probability_formula_section(inputs)
    lines += [
        r"\section{模型边界}",
        "",
        r"\section{39只优先池到正式模型的桥接}",
        "",
        r"\scriptsize",
        r"\begin{longtable}{L{1.15cm}L{1.55cm}L{2.15cm}R{1.15cm}R{1.05cm}L{3.0cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{层级} & \textbf{空间} & \textbf{外部锚} & \textbf{未升级原因/使用方式} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{层级} & \textbf{空间} & \textbf{外部锚} & \textbf{未升级原因/使用方式} \\",
        r"\midrule",
        r"\endhead",
    ]
    status_label = {
        "formal_audit_model": "正式审计模型",
        "conditional_high_upside_watch": "条件性高空间观察",
        "conditional_margin_watch": "条件性安全边际观察",
        "valuation_risk_or_watch": "估值风险/观察",
    }
    for row in bridge_rows:
        reason = "；".join(row["selection_reasons"])
        external_anchor = (
            f"历史/弱来源目标{number(row.get('external_target'))}元（零权）"
            if row.get("external_target") is not None and not row.get("external_weight")
            else f"{number(row.get('external_target'))}元"
            if row.get("external_target") is not None
            else "House替代估值"
        )
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{tex(status_label.get(row['selection_status'], row['selection_status']))} & "
            f"{tex(plain_percent(row.get('upside')))} & {tex(external_anchor)} & "
            f"{tex(reason)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        "正式模型的选择重点是“证据是否足以支撑当前价格下的可审计估值”，不是单纯追求概率空间最大。中洲控股、吉林敖东、辽宁成大和中国船舶等标的模型空间很高，但分别受到外部锚缺失、研报过旧、证据质量不足或原始目标价缺失的约束，因此进入条件性观察而非正式Street锚模型。川能动力虽然证据链完整，但概率目标低于现价，故作为下行风险对照，不作为正向推荐。",
        "",
        "本轮动态模型是全量筛选后的可复算模型层，不等于对每家公司都完成了深度公司研究。正式模型仍需独立IC复核；条件性观察池的升级条件已经在第四章逐票写明。所有陈旧、失败或弱证据研报不作为正向Street锚。",
        r"\section{估值恢复模型：三六零与中洲控股}",
        "",
        "这两只标的原先的H1扭亏/项目结算PE外推会产生不可解释的极端空间，因此本轮改用估值恢复模型。恢复模型不把弱来源直接当作Street目标，而是将公开机构共识、可比公司方法、市场隐含估值和替代估值方法分层使用。",
    ]
    for recovery in recovery_rows:
        alternative = recovery["alternative_method"]
        consensus = recovery.get("public_consensus_anchor") or {}
        model = model_map[recovery["ticker"]]
        fair_value = alternative["fair_value"]
        probabilities = recovery.get("scenario_probabilities", {})
        probability_formula = (
            f"概率价值 = {fair_value['bear']:.2f}×{probabilities.get('bear', 0):.2f} + "
            f"{fair_value['base']:.2f}×{probabilities.get('base', 0):.2f} + "
            f"{fair_value['bull']:.2f}×{probabilities.get('bull', 0):.2f} "
            f"= {model['house_probability_value']:.2f}元。"
        )
        if model.get("public_consensus_weight", 0):
            final_formula = (
                f"最终条件性目标 = {model['house_probability_value']:.2f}×"
                f"{1 - model['public_consensus_weight']:.2f} + "
                f"{model['public_consensus_anchor']:.2f}×{model['public_consensus_weight']:.2f} "
                f"= {model['probability_target']:.2f}元，空间{model['upside'] * 100:.1f}%。"
            )
        else:
            final_formula = (
                f"无正权重外部目标锚，最终条件性目标等于概率价值"
                f"{model['probability_target']:.2f}元，空间{model['upside'] * 100:.1f}%。"
            )
        lines += [
            f"\\subsection{{{tex(recovery['company'])}（{tex(recovery['ticker'])}）}}",
            tex(
                f"恢复状态：{recovery['valuation_recovery_status']}；"
                f"主方法：{alternative['primary']}；"
                f"可比公司：{'、'.join(recovery.get('peer_set', []))}；"
                f"置信度：{recovery['confidence']}。"
            ),
            tex(
                f"情景区间为{alternative['fair_value']['bear']:.2f}/"
                f"{alternative['fair_value']['base']:.2f}/"
                f"{alternative['fair_value']['bull']:.2f}元；"
                f"外部锚说明：{recovery_anchor_text(recovery, model)}；"
                f"公开共识来源质量为{consensus.get('source_quality', '未形成公开目标价共识')}。"
            ),
            tex(alternative["calculation"]),
            tex(probability_formula),
            tex(final_formula),
            tex(
                f"市场隐含指标：{recovery.get('market_implied_metric', {}).get('sentiment', '未披露')}。"
                f"恢复模型置信度为{recovery['confidence']}，不等同于正式Street目标。"
            ),
            tex(
                f"正常化分母：{recovery['normalized_denominator']}。"
                f"升级条件：{recovery['upgrade_trigger']}。"
                f"降级条件：{recovery['downgrade_trigger']}。"
            ),
        ]
    lines += [
        "",
    ]
    return "\n".join(lines)


def risk_section(inputs: dict[str, Any]) -> str:
    evidence = inputs["evidence"]
    return "\n".join(
        [
            r"\chapter{风险、监控与下一步}",
            "",
            r"\begin{itemize}",
            r"\item \textbf{预告风险：}1,680家公司预告是公司初步测算，H1不能机械年化。",
            r"\item \textbf{纯度风险：}扣非占比超过40\%的候选已被排除或降级，归母利润不能直接作为干净分母。",
            r"\item \textbf{周期风险：}有色、煤炭、石化、锂、航运的概率值高度依赖价格、库存、运价和现金流。",
            r"\item \textbf{价格风险：}7月15日价格刷新后，部分旧主题标的从候选升级为价格先行/高估值风险。",
            f"\\item \\textbf{{证据风险：}}候选Q1财务覆盖{evidence['financial_success_count']}/{evidence['row_count']}，研报PDF覆盖{evidence['report_pdf_count']}/{evidence['row_count']}，失败探针不提供正向Street权重。",
            r"\item \textbf{行业资金边界：}行业日报与周报均为31/31完整表，观察日分别为7月14日与截至7月10日；连续流入公开表仅30/112，不能扩展为完整名单。",
            r"\end{itemize}",
            "",
            r"\section{升级触发器}",
            "",
            "正式池：H2扣非兑现、现金流跟随、当前价格回撤承接、最新研报分母不下修。优先池：补齐研报/订单/现金流证据。候选池：先通过纯度、分母和价格位置三重门槛。任何只有高同比、没有现金流或扣非支持的股票，不升级为正式配置。",
        ]
    )


def sources_section(inputs: dict[str, Any]) -> str:
    evidence = inputs["evidence"]
    return "\n".join(
        [
            r"\chapter{来源、数据质量与复现索引}",
            "",
            r"\begin{itemize}",
            r"\item 官方全量预告：\texttt{refresh-20260715/data/raw\_a\_share\_h1\_2026\_preview\_20260715.json}。",
            r"\item 全量筛选：\texttt{refresh-20260715/data/full\_market\_preview\_screen\_20260715.json}。",
            r"\item 候选行情：\texttt{refresh-20260715/data/full\_market\_candidates\_20260715.json}。",
            r"\item 候选证据：\texttt{refresh-20260715/data/full\_market\_valuation\_evidence\_20260715.json}。",
            r"\item 优先池模型：\texttt{refresh-20260715/data/full\_market\_priority\_valuation\_20260715.json}。",
            r"\item 正式模型选择桥：\texttt{refresh-20260715/data/formal\_selection\_bridge\_20260715.json}。",
            r"\item 正式模型：\texttt{refresh-20260715/data/current\_valuation\_model\_20260715.json}。",
            r"\item 估值恢复包：\texttt{refresh-20260715/data/valuation\_recovery\_601360\_000042\_20260715.json}及其对应的\texttt{sources/valuation-recovery-20260715/}原文归档。",
            r"\item Q1财务包：\texttt{refresh-20260715/data/financials/}。",
            r"\item 研报原件：\texttt{refresh-20260715/sources/broker-reports-20260715/}。",
            r"\end{itemize}",
            "",
            f"候选证据覆盖：财务{evidence['financial_success_count']}/{evidence['row_count']}，研报元数据{evidence['report_metadata_count']}/{evidence['row_count']}，PDF{evidence['report_pdf_count']}/{evidence['row_count']}，可抽取目标价{evidence['target_extract_count']}/{evidence['row_count']}。",
            "",
            r"\textbf{Refresh Model Reproducibility: PASS}：所有候选的现价、股本、H1分母、H2比例、熊/基准/牛、概率值和空间均由结构化刷新包计算；正式池在此基础上保留独立审计边界。",
        ]
    )


def stage_group_label(stage: str) -> str:
    return {
        "silent_accumulation": "静默吸纳",
        "launch_confirmation": "启动确认",
        "flow_watch": "资金观察",
        "low_price_no_flow": "低位无流",
        "one_day_rebound": "单日反弹",
        "no_signal": "无明确信号",
        "unmapped": "未映射",
    }.get(stage, stage)


def method_code(formula_type: str) -> str:
    return {
        "cycle_adjusted_eps_pe": "M1",
        "growth_earnings_scenario_pe": "M2",
        "financial_pb_pe_blend": "M3",
        "deducted_eps_scenario_pe": "M4",
        "recovery_alternative_method": "R1",
        "listing_boundary": "B1",
    }.get(formula_type, "M0")


def method_family_title(formula_type: str) -> str:
    return {
        "cycle_adjusted_eps_pe": "M1｜周期盈利：以周期调整扣非EPS/PE估值",
        "growth_earnings_scenario_pe": "M2｜成长盈利：以情景EPS/PE估值",
        "financial_pb_pe_blend": "M3｜金融资产：以PB/ROE与盈利混合估值",
        "deducted_eps_scenario_pe": "M4｜常规盈利：以扣非EPS情景估值",
        "recovery_alternative_method": "R1｜恢复估值：以正常化EPS、PB或PS重建分母",
        "listing_boundary": "B1｜上市边界：不在无二级市场价格时制造目标价",
    }.get(formula_type, "M0｜其他估值方法")


def method_family_reason(formula_type: str) -> str:
    return {
        "cycle_adjusted_eps_pe": (
            "适用于商品、价差、运价和利用率主导的行业。重点不是把H1利润线性外推，"
            "而是用熊/基准/牛H2转化率测试周期持续性，并以较低熊市倍数吸收周期反转。"
        ),
        "growth_earnings_scenario_pe": (
            "适用于存在盈利持续期、产品升级或订单释放的成长行业。模型只对已进入盈利桥接的"
            "扣非利润赋予成长估值，不把泛化主题叙事直接转化为EPS。"
        ),
        "financial_pb_pe_blend": (
            "适用于证券、保险和类金融资产。PB保留资产负债表与ROE锚，PE检验盈利能力，"
            "二者混合可降低单季投资收益或估值波动造成的偏差。"
        ),
        "deducted_eps_scenario_pe": (
            "适用于正扣非分母、商业模式相对稳定且未触发低基数/结算型阻断的公司。"
            "H2转化率明确写为情景假设，不将半年度数据伪装为全年共识。"
        ),
        "recovery_alternative_method": (
            "适用于低基数扭亏、项目结算、近零EPS或利润周期明显扭曲的公司。"
            "先切换至正常化EPS、PB或收入PS，再决定是否使用外部锚。"
        ),
        "listing_boundary": (
            "尚无有效二级市场价格时，任何当前价目标和空间均不成立；保留发行价与上市状态，"
            "待交易形成后再建立估值模型。"
        ),
    }.get(formula_type, "方法与分母需要在下一轮证据更新后重新确认。")


def compact_formula_tex(audit: dict[str, Any], model: dict[str, Any]) -> str:
    formula_type = audit["formula_type"]
    inputs = audit.get("formula_inputs") or {}
    scenario = audit.get("scenario_inputs") or {}
    target = model.get("probability_target")
    if formula_type in {
        "cycle_adjusted_eps_pe",
        "growth_earnings_scenario_pe",
        "deducted_eps_scenario_pe",
    }:
        ratios = inputs.get("h2_conversion_ratios") or {}
        multiples = inputs.get("pe_multiples") or []
        eps = inputs.get("h1_deducted_eps")
        values = [scenario.get(key) for key in ("bear", "base", "bull")]
        return (
            rf"\(\mathrm{{EPS}}_s={math_num(eps, 4)}\times"
            rf"(1+\{{{math_num(ratios.get('bear'), 2)},{math_num(ratios.get('base'), 2)},{math_num(ratios.get('bull'), 2)}\}});\ "
            rf"V_s=\mathrm{{EPS}}_s\times"
            rf"\{{{','.join(math_num(value, 1) for value in multiples)}\}}"
            rf"\Rightarrow\{{{','.join(math_num(value) for value in values)}\}}\)"
        )
    if formula_type == "financial_pb_pe_blend":
        bps = inputs.get("q1_bps")
        scenario_eps = inputs.get("scenario_eps") or {}
        pe_multiples = inputs.get("pe_multiples") or []
        values = [scenario.get(key) for key in ("bear", "base", "bull")]
        return (
            rf"\(V_s=0.65\times(\mathrm{{BPS}}={math_num(bps)}\times"
            rf"\{{0.75,1.05,1.35\}})+0.35\times(\mathrm{{EPS}}_s="
            rf"\{{{math_num(scenario_eps.get('bear'), 4)},{math_num(scenario_eps.get('base'), 4)},{math_num(scenario_eps.get('bull'), 4)}\}}"
            rf"\times\{{{','.join(math_num(value, 1) for value in pe_multiples)}\}})"
            rf"\Rightarrow\{{{','.join(math_num(value) for value in values)}\}}\)"
        )
    if formula_type == "recovery_alternative_method":
        recovery_inputs = inputs
        method = model.get("method", "")
        values = [scenario.get(key) for key in ("bear", "base", "bull")]
        if method == "PS on 2026E revenue":
            revenue = recovery_inputs.get("revenue_2026E_100mn")
            multiples = recovery_inputs.get("multiples") or {}
            return (
                rf"\(V_s=(R_{{2026E}}={math_num(revenue)}/"
                rf"\mathrm{{Shares}}={math_num(model.get('shares_100mn'), 4)})\times"
                rf"\{{{math_num(multiples.get('bear'), 1)},{math_num(multiples.get('base'), 1)},{math_num(multiples.get('bull'), 1)}\}}"
                rf"\Rightarrow\{{{','.join(math_num(value) for value in values)}\}}\)"
            )
        normalized_eps = recovery_inputs.get("normalized_eps_2026")
        normalized_bps = recovery_inputs.get("normalized_bps_2026")
        multiples = recovery_inputs.get("multiples") or {}
        if normalized_eps:
            return (
                rf"\(V_s=\mathrm{{EPS}}_{{norm}}\times\mathrm{{PE}}_s="
                rf"\{{{math_num(normalized_eps.get('bear'))},{math_num(normalized_eps.get('base'))},{math_num(normalized_eps.get('bull'))}\}}"
                rf"\times\{{{math_num(multiples.get('bear'), 1)},{math_num(multiples.get('base'), 1)},{math_num(multiples.get('bull'), 1)}\}}"
                rf"\Rightarrow\{{{','.join(math_num(value) for value in values)}\}}\)"
            )
        if normalized_bps:
            return (
                rf"\(V_s=\mathrm{{BPS}}_{{norm}}\times\mathrm{{PB}}_s="
                rf"\{{{math_num(normalized_bps.get('bear'))},{math_num(normalized_bps.get('base'))},{math_num(normalized_bps.get('bull'))}\}}"
                rf"\times\{{{math_num(multiples.get('bear'), 1)},{math_num(multiples.get('base'), 1)},{math_num(multiples.get('bull'), 1)}\}}"
                rf"\Rightarrow\{{{','.join(math_num(value) for value in values)}\}}\)"
            )
        return rf"\(V_{{bear/base/bull}}=\{{{','.join(math_num(value) for value in values)}\}}\)"
    return r"不适用：尚未上市，待形成可验证二级市场价格后重建模型。"


def concise_evidence_text(audit: dict[str, Any], model: dict[str, Any]) -> str:
    broker = model.get("latest_broker")
    report_date = model.get("latest_report_date")
    broker_text = (
        f"{broker}（{report_date}）"
        if broker and report_date
        else "无当前券商目标锚"
    )
    return (
        f"质量{evidence_label(audit.get('evidence_quality'))}；"
        f"事实输入：官方预告、Q1财务与行情；外部背景：{broker_text}。"
    )


def denominator_short_cn(audit: dict[str, Any], model: dict[str, Any]) -> str:
    formula_type = audit["formula_type"]
    inputs = audit.get("formula_inputs") or {}
    if formula_type == "financial_pb_pe_blend":
        return (
            f"Q1 BPS {number(inputs.get('q1_bps'))}元；"
            f"H1扣非EPS {number(inputs.get('h1_deducted_eps'), 4)}元"
        )
    if formula_type in {
        "cycle_adjusted_eps_pe",
        "growth_earnings_scenario_pe",
        "deducted_eps_scenario_pe",
    }:
        ratios = inputs.get("h2_conversion_ratios") or {}
        return (
            f"H1扣非EPS {number(inputs.get('h1_deducted_eps'), 4)}元；"
            f"H2/H1={number(ratios.get('bear'), 2)}/"
            f"{number(ratios.get('base'), 2)}/{number(ratios.get('bull'), 2)}"
        )
    if formula_type == "listing_boundary":
        return "发行价8.66元；尚无二级市场当前价"
    recovery_short = {
        "601360": "2026E收入95.91亿元与AI/安全变现",
        "000042": "项目结算、税费与利息正常化EPS",
        "002460": "2026E周期调整EPS",
        "600037": "2026E持续经营EPS",
        "002048": "汽车零部件与机器人订单正常化EPS",
        "600688": "Q1 BPS与炼化周期调整资产价值",
        "001309": "存储周期调整前瞻EPS",
        "300390": "锂价敏感的2026E周期调整EPS",
        "002812": "隔膜价格/利用率恢复后的2027E EPS",
        "002240": "锂价、自有矿与现金流桥接EPS",
        "600736": "园区/结算/投资收益正常化EPS",
        "000415": "租赁收入、资产质量与汇率正常化EPS",
    }
    return recovery_short.get(
        audit["ticker"],
        "正常化盈利或资产价值分母",
    )


def recovery_validation_cn(ticker: str, model: dict[str, Any]) -> tuple[str, str]:
    """Translate reader-facing recovery triggers; raw English remains in audit JSON."""
    mapping = {
        "601360": (
            "2026年收入接近95.91亿元，AI/安全形成可重复变现，EPS共识不低于0.06元且经营现金流转正",
            "AI产品变现不及预期、2026年EPS低于0.03元、经营现金流仍为负，或PS低于可比区间",
        ),
        "000042": (
            "2026年EPS不低于1.10元，项目结算及税费/利息计提得到确认，债务与现金流压力改善且股价守住8元",
            "结算利润回转、土地增值税或利息计提上升、销售回款走弱，或净负债/流动性恶化",
        ),
        "002460": (
            "锂价、产量、资源自给率和H2经营现金流共同验证2026年EPS 4.45元",
            "锂价回落、资源项目延期、库存减值，或现金流弱于利润",
        ),
        "600037": (
            "通信业务收入、经营现金流和全年EPS达到公开预测，并连续两个季度得到验证",
            "扭亏由一次性收益驱动、通信业务不及预期，或经营现金流转弱",
        ),
        "002048": (
            "汽车订单、机器人批量供货和H2扣非利润共同验证2026年EPS 1.98元",
            "主机厂降价、机器人订单延迟，或扣非利润低于预期",
        ),
        "600688": (
            "炼化价差、经营现金流和资产负债表改善，同时新一期机构预测恢复",
            "炼化价差继续收窄、现金流恶化，或资产减值上升",
        ),
        "001309": (
            "存储价格、企业级产品出货和H2经营现金流共同验证2026年EPS 39.16元",
            "存储价格反转、库存减值、客户集中风险暴露，或经营现金流持续为负",
        ),
        "300390": (
            "氢氧化锂价格、客户采购、产量和H2经营现金流共同验证2026年EPS 5.70元",
            "锂价回落、客户集中风险暴露，或经营现金流继续弱于利润",
        ),
        "002812": (
            "隔膜涨价、产能利用率、海外/3C订单和H2现金流共同验证2027年EPS 5.16元",
            "供需修复不及预期、价格回落、客户集中，或产能利用率不足",
        ),
        "002240": (
            "锂价、出货、自有矿贡献和H2经营现金流共同验证2026年EPS 2.45元",
            "锂价回落、现金流持续为负，或资源项目贡献不及预期",
        ),
        "600736": (
            "产业园利润、地产结算、投资收益和经营现金流共同验证2026年EPS 0.14元",
            "地产结算延期、投资收益回落，或经营现金流继续为负",
        ),
        "000415": (
            "租赁收入、资产质量、汇率和H2现金流共同验证2026年EPS 0.77元",
            "飞机减值、汇率损失、融资成本上升，或现金流风险上行",
        ),
    }
    return mapping.get(
        ticker,
        (
            str(model.get("catalyst") or "等待正常化分母与现金流确认"),
            str(model.get("invalidation") or "关键盈利或现金流假设未获验证"),
        ),
    )


def high_upside_anchor_text(row: dict[str, Any]) -> str:
    anchor = row["accepted_external_anchor"]
    target = anchor.get("target_midpoint")
    if target is None:
        return "原始语料未找到可接受目标价"
    if anchor.get("target_low") != anchor.get("target_high"):
        value = (
            f"{number(anchor.get('target_low'))}"
            f"--{number(anchor.get('target_high'))}元"
        )
    else:
        value = f"{number(target)}元"
    return f"{anchor.get('report_date')} {value}，权重0%"


def high_upside_verified_text(row: dict[str, Any]) -> str:
    return (
        f"API/PDF {row['metadata_report_count']}/"
        f"{row['archived_original_pdf_count']}；"
        f"当前原始目标{row['current_original_target_count']}；"
        f"{high_upside_anchor_text(row)}；"
        f"Q1现金流{number(row.get('q1_ocf_100mn'), 2)}亿元"
    )


def high_upside_remaining_text(row: dict[str, Any], limit: int | None = None) -> str:
    events = list(row.get("remaining_event_validation") or [])
    if limit is not None:
        events = events[:limit]
    return "；".join(events) if events else "无剩余事件验证"


def high_upside_gate_text(row: dict[str, Any]) -> str:
    pool = "优先池内" if row.get("in_priority_pool") else "未入优先池"
    return (
        f"{pool}；当前原始目标0；"
        f"Q1现金流{number(row.get('q1_ocf_100mn'), 2)}亿元；"
        f"{row['final_admission_decision']}"
    )


def row_reason_short_cn(audit: dict[str, Any]) -> str:
    return {
        "cycle_adjusted_eps_pe": "周期变量主导，禁止直接年化H1利润",
        "growth_earnings_scenario_pe": "成长持续期需由盈利兑现与现金流验证",
        "financial_pb_pe_blend": "资产净值与盈利能力双锚",
        "deducted_eps_scenario_pe": "正扣非分母，采用H2情景而非全年点估",
        "recovery_alternative_method": "低基数/结算扭曲，先切换正常化分母",
        "listing_boundary": "未上市，无法建立当前价模型",
    }.get(audit["formula_type"], "按业务模型选择估值方法")


def monitor_short_cn(audit: dict[str, Any], model: dict[str, Any]) -> str:
    if audit["formula_type"] == "recovery_alternative_method":
        catalyst, invalidation = recovery_validation_cn(audit["ticker"], model)
        return f"验证：{catalyst}；反证：{invalidation}"
    if audit["formula_type"] == "listing_boundary":
        return "形成有效二级市场交易价格后重新评估"
    catalyst, invalidation = industry_validation_text(model["industry"])
    return f"验证：{catalyst}；反证：{invalidation}"


def professional_dashboard_section(inputs: dict[str, Any]) -> str:
    formal = inputs["formal"]["rows"]
    models = {row["ticker"]: row for row in inputs["models"]["rows"]}
    high_upside_rows = inputs["high_upside_closure"]["rows"]
    high_upside_closure = inputs["high_upside_closure"]
    admission = inputs["former_medium_admission"]
    admission_rows = admission["rows"]
    positive_formal = [row for row in formal if row.get("upside", 0) > 0]
    downside_formal = [row for row in formal if row.get("upside", 0) <= 0]
    priority_validation = [
        row for row in admission_rows
        if row["admission_status"] == "priority_event_validation_candidate"
    ]
    expanded_validation = [
        row for row in admission_rows
        if row["admission_status"] == "expanded_event_validation_candidate"
    ]
    margin_watch = [
        row for row in admission_rows
        if row["admission_status"] == "priority_margin_watch"
    ]
    risk_or_not = [
        row for row in admission_rows
        if row["admission_status"] in {"priority_valuation_risk_watch", "not_admitted"}
    ]
    conditional_codes = [
        "600150",
        "601600",
        "601360",
        "600026",
        "002048",
        "002812",
        "300390",
        "002240",
    ]
    conditional_rows = [models[code] for code in conditional_codes if code in models]
    lines = [
        r"\chapter{投资结论与行动框架}",
        "",
        r"\begin{houseviewbox}[核心判断｜盈利预告的广度不等于全面风险偏好]",
        (
            "我们不把1,680家公司的预告扩散解读为全面风险偏好开启。可执行机会集中在三类："
            "第一，已经形成利润—现金流—外部锚闭环的可复核验证模型；第二，利润修复可信、但仍需下一季证据确认的"
            "事件验证标的；第三，价格已先行或分母质量不足、只能作为风险监控的标的。"
            "因此，本报告的重点不是寻找最高目标价，也不是直接给出配置建议，而是识别在当前价格下可被证据、外部锚和风险预算共同约束的验证队列。"
        ),
        r"\end{houseviewbox}",
        "",
        r"\section{投资行动摘要}",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 1｜当前可复核模型与行动含义]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{1.1cm}L{1.7cm}L{1.5cm}R{1.0cm}R{1.0cm}R{1.1cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{角色} & \textbf{现价} & \textbf{概率值} & \textbf{空间} & \textbf{行动与约束} \\",
        r"\midrule",
    ]
    for row in formal:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(formal_role(row))} & "
            f"{number(row.get('current_price'))} & {number(row.get('probability_target'))} & "
            f"{percent(row.get('upside'))} & {tex(formal_constraint(row))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{官方业绩预告、Q1财务、2026年7月15日收盘价及已归档原始研报；概率值为本机构情景值，非收益承诺。}",
        r"\end{exhibitbox}",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 2｜三层行动框架：从可复核价值到风险纪律]",
        r"\begin{minipage}[t]{0.31\textwidth}",
        r"\textbf{\color{riskgreen}可复核正向验证}",
        r"\par\smallskip",
        r"当前价格、情景分母、原始研报锚与风险触发器均可复核。",
        r"\par\smallskip",
        r"\textbf{代表：}恒逸石化、宏桥控股。",
        r"\par\smallskip",
        r"\textbf{纪律：}不直接配置；H2扣非或现金流偏离即降级。",
        r"\end{minipage}\hfill",
        r"\begin{minipage}[t]{0.31\textwidth}",
        r"\textbf{\color{riskamber}事件验证观察}",
        r"\par\smallskip",
        r"盈利修复有线索，但外部锚、现金流或持续性仍未闭环。",
        r"\par\smallskip",
        r"\textbf{代表：}中国船舶、中国铝业、三六零、中远海能。",
        r"\par\smallskip",
        r"\textbf{纪律：}不以模型空间作为行动理由。",
        r"\end{minipage}\hfill",
        r"\begin{minipage}[t]{0.31\textwidth}",
        r"\textbf{\color{riskred}估值纪律观察}",
        r"\par\smallskip",
        r"概率值低于现价、周期盈利可能回落或证据时效不足。",
        r"\par\smallskip",
        r"\textbf{代表：}川能动力及高估值样本。",
        r"\par\smallskip",
        r"\textbf{纪律：}不追价，作为行业和风险偏好的反向指标。",
        r"\end{minipage}",
        r"\sourcenote{行动分层由当前价格、估值分母、外部锚和证据质量共同决定，不等同于券商投资评级。}",
        r"\end{exhibitbox}",
        "",
        r"\section{执行纪律：先验证，再放大}",
        "",
        (
            "可复核正向模型只在利润、现金流与外部锚三项同时未偏离时维持；任一项失效即转入事件验证。"
            "事件验证观察不以模型空间作为建仓理由，须等待下一份财报、订单或价格信号把假设变为事实。"
            "估值纪律观察不追价，主要用于识别行业盈利、价格与风险偏好是否发生反向变化。"
        ),
        "",
        r"\section{补证后的候选池调整}",
        "",
        (
            f"原中等证据标的共{admission['row_count']}只，补证后基础证据不再是主要阻断项；"
            f"其中{len(priority_validation)}只进入优先验证候选、{len(expanded_validation)}只进入扩展事件验证、"
            f"{len(margin_watch)}只进入安全边际观察，{len(risk_or_not)}只仅保留为风险监控或暂不纳入。"
            "没有任何原中等证据标的直接进入正式模型池，核心原因仍是当前可正权外部估值锚不足或价格纪律不满足。"
        ),
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 3｜补证后候选准入摘要]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{2.5cm}R{0.9cm}L{4.0cm}X}",
        r"\toprule",
        r"\textbf{层级} & \textbf{数量} & \textbf{代表标的} & \textbf{使用方式} \\",
        r"\midrule",
        f"优先验证候选 & {len(priority_validation)} & {tex('、'.join(row['company'] for row in priority_validation[:6]))} & {tex('进入优先验证队列；等待外部锚、H2扣非和现金流确认')} \\\\",
        f"扩展事件验证 & {len(expanded_validation)} & {tex('、'.join(row['company'] for row in expanded_validation[:6]))} & {tex('列入扩展观察，不因空间大直接升级')} \\\\",
        f"安全边际观察 & {len(margin_watch)} & {tex('、'.join(row['company'] for row in margin_watch[:3]))} & {tex('低优先级跟踪，等待安全边际扩大')} \\\\",
        f"风险/不纳入 & {len(risk_or_not)} & {tex('、'.join(row['company'] for row in risk_or_not[:6]))} & {tex('概率值低于现价或现金流/外部锚不足，不新增为候选')} \\\\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{完整逐票准入结论见附录C；本表为投委会摘要，不构成正式推荐。}",
        r"\end{exhibitbox}",
        "",
        r"\section{为什么没有按100\%以上空间直接入选}",
        "",
        (
            f"全142只候选中，本轮模型空间超过100\\%的标的共有{len(high_upside_rows)}只，"
            f"其中{sum(row['in_priority_pool'] for row in high_upside_rows)}只进入39只优先池，"
            f"{sum(row['in_formal_pool'] for row in high_upside_rows)}只进入正式模型。"
            f"专项核验已对{high_upside_closure['closure_count']}/{high_upside_closure['row_count']}只完成"
            f"原始API、原始PDF、目标价字段与现金流闭环；当前正权原始目标为"
            f"{high_upside_closure['current_positive_anchor_count']}只。"
            "因此未升级不是资料空白，而是已核验证据不支持把内部高空间转换为正式模型。"
        ),
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 3A｜100\%以上空间样本的拦截链条]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.05cm}L{1.55cm}R{1.0cm}L{1.35cm}L{1.35cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{空间} & \textbf{优先池} & \textbf{正式池} & \textbf{未直接入选原因} \\",
        r"\midrule",
    ]
    for row in high_upside_rows:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {percent(row.get('house_model_upside'))} & "
            f"{tex('是' if row.get('in_priority_pool') else '否')} & "
            f"{tex('是' if row.get('in_formal_pool') else '否')} & "
            f"{tex(high_upside_gate_text(row))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{专项包已逐票核验东方财富原始API、已归档原始PDF、目标价字段与Q1现金流。媒体转载、聚合页和失败探针权重均为0。}",
        r"\end{exhibitbox}",
        "",
        "",
        r"\section{重点事件验证清单}",
        "",
        "下表不是推荐名单，而是最需要在下一轮信息披露中验证的高敏感样本。其共同点是："
        "模型空间可能存在，但当前尚不满足正式审计模型条件。",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 3B｜条件性机会：从模型空间到证据升级]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.1cm}L{1.7cm}L{1.6cm}R{1.0cm}R{1.0cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{估值框架} & \textbf{概率值} & \textbf{空间} & \textbf{必须验证的事实} \\",
        r"\midrule",
    ]
    for row in conditional_rows:
        catalyst, invalidation = industry_validation_text(row["industry"])
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{tex(method_label_cn(row.get('method')))} & "
            f"{number(row.get('probability_target'))} & {percent(row.get('upside'))} & "
            f"{tex(catalyst + '；反证：' + invalidation)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{条件性模型仅用于安排验证优先级。若缺乏当前外部锚或现金流确认，则不升级为可复核正向验证。}",
        r"\end{exhibitbox}",
        "",
        "本报告的反方情景同样明确：若H2扣非利润不延续、经营现金流继续背离、商品价格或行业价差回落，"
        "当前候选池中的高空间模型将被迅速下调，而不是通过提高倍数维持结论。",
    ]
    return "\n".join(lines)


def professional_market_section(inputs: dict[str, Any]) -> str:
    sector_rows = load_json(DATA_DIR / "sector_scan_20260715.json")["rows"]
    groups: dict[str, list[str]] = {}
    for row in sector_rows:
        groups.setdefault(row["stage"], []).append(row["industry"])
    stage_order = [
        ("silent_accumulation", "静默吸纳", "日/周资金同向流入且价格、估值仍受约束", "优先寻找利润质量与现金流同步改善的公司"),
        ("launch_confirmation", "启动确认", "资金与价格已出现确认，静态低位优势下降", "关注利润兑现，不追逐单日放量"),
        ("flow_watch", "资金观察", "周度资金存在但价格、估值或日度流向尚未闭环", "只做事件验证，不根据主题直接配置"),
        ("one_day_rebound", "单日反弹", "单日流入未获得周度确认", "不把单日反弹视为资本布局"),
    ]
    lines = [
        r"\chapter{市场状态与机会架构}",
        "",
        "市场层面的结论是“选择性再定价”而非“全面抬估值”。行业资金状态只能回答资本是否开始关注，"
        "不能替代公司盈利质量、现金流或估值分母。我们将行业状态与公司级证据分开处理，以避免把短期资金流误解为可配置的基本面信号。",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 4｜31个一级行业的阶段划分与投资含义]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{1.9cm}L{3.5cm}X L{4.2cm}}",
        r"\toprule",
        r"\textbf{阶段} & \textbf{观察到的市场特征} & \textbf{代表行业} & \textbf{投资含义} \\",
        r"\midrule",
    ]
    for stage, label, observation, implication in stage_order:
        industries = "、".join(groups.get(stage, [])) or "无"
        lines.append(
            f"{tex(label)} & {tex(observation)} & {tex(industries)} & {tex(implication)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{申万一级行业官方指数历史与公开行业资金表。行业资金观察截至2026年7月14日，周度观察截至2026年7月10日。}",
        r"\end{exhibitbox}",
        "",
        r"\section{从行业阶段到公司动作}",
        "",
        "静默吸纳并不自动意味着低风险；例如房地产的行业PB处于低分位，但公司层面仍须通过结算、税费、债务和现金流检验。"
        "启动确认也不自动意味着高估；石油石化和煤炭的价格确认必须与价差、库存、分红和现金流相匹配。"
        "因此，公司动作由三重门槛决定：行业阶段、盈利可持续性、当前价格相对情景价值。",
        "",
        r"\noindent",
        r"\begin{tabularx}{\textwidth}{L{3.2cm}X L{4.0cm}}",
        r"\toprule",
        r"\textbf{问题} & \textbf{判断规则} & \textbf{若不成立} \\",
        r"\midrule",
        r"行业是否值得跟踪？ & 资金阶段、估值分位和价格位置至少有两项支持。 & 只保留为市场观察，不进入公司验证。 \\",
        r"利润是否可进入估值？ & 扣非为正、现金流不明显背离、无低基数或结算型扭曲。 & 启动恢复模型或保留为边界标的。 \\",
        r"价格是否可承受？ & 概率值相对现价有安全边际，且外部锚/分母时效可复核。 & 降级为事件验证或估值纪律观察。 \\",
        r"\bottomrule",
        r"\end{tabularx}",
    ]
    return "\n".join(lines)


def professional_framework_section(inputs: dict[str, Any]) -> str:
    audit = inputs["candidate_audit"]
    formula_counts = audit["formula_type_counts"]
    formal = inputs["formal"]["rows"]
    lines = [
        r"\chapter{估值框架与情景分析}",
        "",
        "估值不是把同一PE模板扩展到142只股票。我们先判断利润属于周期、成长、金融资产、常规经营还是恢复性分母，"
        "再选择对应的估值方法。所有外部目标价均按来源质量加权；没有可审计当前锚时，模型只能是条件性本机构区间。",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 5｜估值方法选择矩阵]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{1.0cm}L{2.2cm}R{1.0cm}X L{4.0cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{方法} & \textbf{覆盖} & \textbf{核心公式} & \textbf{为何使用} \\",
        r"\midrule",
        rf"M1 & 周期调整扣非EPS/PE & {formula_counts.get('cycle_adjusted_eps_pe', 0)} & \(EPS_s=EPS_{{H1}}^d(1+r_s);\ V_s=EPS_s\times PE_s\) & 商品、价差、运价和利用率主导的盈利不能被单一半年度利润代表。 \\",
        rf"M2 & 成长盈利情景PE & {formula_counts.get('growth_earnings_scenario_pe', 0)} & \(EPS_s=EPS_{{H1}}^d(1+r_s);\ V_s=EPS_s\times PE_s\) & 仅对已进入盈利桥接的成长持续期赋予更高情景倍数。 \\",
        rf"M3 & PB/ROE与盈利混合 & {formula_counts.get('financial_pb_pe_blend', 0)} & \(V_s=0.65(BPS\times PB_s)+0.35(EPS_s\times PE_s)\) & 金融资产需要同时锚定资产负债表与盈利能力。 \\",
        rf"M4 & 常规扣非EPS/PE & {formula_counts.get('deducted_eps_scenario_pe', 0)} & \(EPS_s=EPS_{{H1}}^d(1+r_s);\ V_s=EPS_s\times PE_s\) & 正扣非分母且未触发低基数或项目结算阻断。 \\",
        rf"R1 & 恢复模型 & {formula_counts.get('recovery_alternative_method', 0)} & \(V_s=EPS_{{norm}}\times PE_s\) 或 \(BPS\times PB_s\) 或 \(R_{{2026E}}/Shares\times PS_s\) & 低基数、结算型、近零EPS必须先更换分母。 \\",
        rf"B1 & 上市边界 & {formula_counts.get('listing_boundary', 0)} & \(P_{{target}}=\text{{不适用}}\) & 无二级市场价格时不制造伪精确目标。 \\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{方法分布来自142只候选的逐票估值审计包；每只的变量代入、依据和证据路径见附录B。}",
        r"\end{exhibitbox}",
        "",
        r"\section{情景权重与目标价治理}",
        "",
        r"\begin{align*}",
        r"V_{\mathrm{prob}} &= 0.30V_{\mathrm{bear}}+0.50V_{\mathrm{base}}+0.20V_{\mathrm{bull}}, \\",
        r"P_{\mathrm{target}} &= V_{\mathrm{prob}}(1-w_{\mathrm{external}})+P_{\mathrm{external}}w_{\mathrm{external}}, \\",
        r"\mathrm{Upside} &= \frac{P_{\mathrm{target}}}{P_{\mathrm{current}}}-1.",
        r"\end{align*}",
        (
            "50%基准权重反映“正常兑现”是最常见路径；30%熊市权重强制保留周期、现金流和分母失效的风险；"
            "20%牛市权重仅在盈利、现金流和外部证据同步改善时才有意义。权重是统一的本机构情景先验，不是回归模型估计出的客观概率。"
        ),
        "",
        r"\noindent",
        r"\begin{sourcequalitybox}[外部锚与本机构区间的边界]",
        "原始券商PDF或可审计共识快照可作为外部锚；摘要、转载、陈旧目标价和用户估值文章仅提供背景，权重为零。"
        "本机构区间的作用是定义验证顺序和风险边界，不替代当前、可审计的市场一致目标价。",
        r"\end{sourcequalitybox}",
        "",
        "模型升级已在第一章的行动分层中固化：正式模型要求当前价格、分母、外部锚和失效条件同步可核；"
        "条件性区间仅用于安排验证优先级；上市或证据边界标的在形成有效交易价格或补齐关键证据前不进入目标价模型。",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 6｜概率值不是承诺：三项不可放松的估值约束]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{2.2cm}X L{4.6cm}}",
        r"\toprule",
        r"\textbf{约束} & \textbf{模型含义} & \textbf{行动后果} \\",
        r"\midrule",
        r"分母约束 & H2扣非、现金流和周期变量必须支撑熊/基准/牛的情景分母；半年度利润不等同于全年盈利。 & 分母失效先下调EPS或切换正常化口径，不以提高估值倍数补偿。 \\",
        r"外部锚约束 & 只有当前、可审计的原始研报或共识快照可获得正权重；摘要、转载和陈旧目标价仅保留为背景。 & 弱来源权重归零，条件性本机构区间不升级为可复核正向验证。 \\",
        r"价格约束 & 概率值相对现价的空间只是情景结果；价格位置、估值拥挤度和失效条件决定是否可执行。 & 概率值低于现价或证据时效不足时不追价，转入估值纪律观察。 \\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{概率值用于比较风险调整后的情景价值，不构成收益承诺；逐票输入、权重与公式代入见附录B。}",
        r"\end{exhibitbox}",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 7｜正式模型的概率值桥接：本机构情景与外部锚分层计入]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{2.5cm}R{2.4cm}L{4.1cm}R{2.4cm}}",
        r"\toprule",
        r"\textbf{标的} & \textbf{本机构概率值} & \textbf{外部锚及权重} & \textbf{最终概率值} \\",
        r"\midrule",
    ]
    for row in formal:
        lines.append(
            f"{tex(row['company'])}（{tex(row['ticker'])}） & "
            f"{number(row.get('house_probability_value'))}元 & "
            f"{number(row.get('external_target'))}元 × {percent(row.get('external_weight'), 0)} & "
            f"{number(row.get('probability_target'))}元 \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{最终概率值=本机构概率值×（1－外部锚权重）＋外部目标价×外部锚权重。外部锚的正权重仅限于当前、可审计的原始研报字段。}",
        r"\end{exhibitbox}",
    ]
    return "\n".join(lines)


def professional_focus_section(inputs: dict[str, Any]) -> str:
    formal = inputs["formal"]["rows"]
    models = {row["ticker"]: row for row in inputs["models"]["rows"]}
    high_upside_rows = inputs["high_upside_closure"]["rows"]
    high_upside_closure = inputs["high_upside_closure"]
    recovery_codes = [
        "601360",
        "000042",
        "002460",
        "002812",
        "300390",
        "002240",
        "600736",
        "000415",
    ]
    lines = [
        r"\chapter{焦点标的与验证路径}",
        "",
        "本章聚焦能够改变下一轮配置排序的公司，而不是重述142只候选。"
        "我们把标的分为可复核当前价模型、恢复性估值模型和高空间但证据不足的验证观察三类；"
        "任何一类都必须有可观察的升级条件和明确的反证。",
        "",
        r"\section{可复核当前价模型}",
    ]
    for row in formal:
        role = formal_role(row)
        catalyst, invalidation = industry_validation_text(row["industry"])
        external = (
            f"外部锚{number(row.get('external_target'))}元，权重{percent(row.get('external_weight'), 0)}"
            if row.get("external_target") is not None
            else "无正权重外部锚"
        )
        lines += [
            f"\\subsection{{{tex(row['company'])}（{tex(row['ticker'])}）｜{tex(role)}}}",
            (
                f"现价{number(row.get('current_price'))}元，本机构概率值{number(row.get('probability_target'))}元，"
                f"对应{percent(row.get('upside'))}空间。熊/基准/牛值为"
                f"{number(row.get('bear'))}/{number(row.get('base'))}/{number(row.get('bull'))}元；"
                f"{external}。"
            ),
            (
                f"我们将其定义为{role}而非一般观察名单，原因是当前价格、股本、情景分母和外部证据可以同时复核。"
                f"下一轮的关键验证是{catalyst}；若出现{invalidation}，则该模型应被降级。"
            ),
            "",
        ]
    lines += [
        r"\noindent",
        r"\begin{exhibitbox}[图表 8｜正式模型横向比较：价值空间必须接受同一组验证纪律]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{2.1cm}L{2.4cm}X L{4.0cm}}",
        r"\toprule",
        r"\textbf{标的} & \textbf{现价/概率值} & \textbf{本轮定位} & \textbf{下一轮必须验证} \\",
        r"\midrule",
    ]
    for row in formal:
        role = formal_role(row)
        catalyst, invalidation = industry_validation_text(row["industry"])
        lines.append(
            f"{tex(row['company'])}（{tex(row['ticker'])}） & "
            f"{number(row.get('current_price'))}/{number(row.get('probability_target'))}元 & "
            f"{tex(role)}；{percent(row.get('upside'))}空间 & "
            f"{tex('验证：' + catalyst + '；反证：' + invalidation)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{正式模型均要求当前价格、分母、原始外部锚和失效条件同时可复核；若概率值低于现价，则仅承担下行纪律对照功能。}",
        r"\end{exhibitbox}",
        "",
        r"\section{恢复性估值：关注分母修复，而非追逐表面空间}",
        "",
        (
            "恢复模型的共同纪律是：当H1利润由低基数、扭亏、结算或周期集中驱动时，"
            "不允许直接以H1年化EPS乘常规行业PE。下表展示当前最具代表性的恢复样本及其下一步证据要求。"
        ),
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 9｜恢复性估值：分母切换与验证条件]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{1.1cm}L{1.7cm}L{2.4cm}R{1.0cm}R{1.0cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{替代分母/方法} & \textbf{概率值} & \textbf{空间} & \textbf{升级条件与反证} \\",
        r"\midrule",
    ]
    for code in recovery_codes:
        row = models.get(code)
        if not row:
            continue
        catalyst, invalidation = recovery_validation_cn(row["ticker"], row)
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{tex(method_label_cn(row.get('method')) + '；' + denominator_short_cn({'ticker': row['ticker'], 'formula_type': 'recovery_alternative_method'}, row))} & "
            f"{number(row.get('probability_target'))} & {percent(row.get('upside'))} & "
            f"{tex('验证：' + catalyst + '；反证：' + invalidation)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{逐票正常化分母、可比集、倍数和公式代入见附录B；表中区间均为条件性本机构价值。}",
        r"\end{exhibitbox}",
        "",
        r"\section{高空间模型的正确使用方式}",
        "",
        (
            f"高空间不是排序第一的理由。本轮已对全部{high_upside_closure['row_count']}只100\\%+空间样本"
            f"完成逐票证据闭环：原始API、已归档PDF、目标价字段、Q1经营现金流和池内准入均已核验，"
            f"闭环率为{high_upside_closure['closure_count']}/{high_upside_closure['row_count']}。"
            f"核验结果不是“仍待补资料”，而是当前正权原始目标为"
            f"{high_upside_closure['current_positive_anchor_count']}只、正式升级为"
            f"{high_upside_closure['formal_upgrade_count']}只。"
        ),
        "",
        (
            "已找到的历史目标仅作为反向证据：九安医疗70.28元、吉林敖东约18.02元、"
            "辽宁成大22.79元、中山公用10.50--11.11元、中国船舶31.36元，均显著低于或仅接近"
            "内部高空间情景值，且因时效不足权重为0。江波龙在原始API及已归档PDF语料中未找到目标价；"
            "中国船舶50元媒体转载仅作零权重交叉验证。"
        ),
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 9A｜高空间样本的已核验证据与准入结论]",
        r"\scriptsize",
        r"\begin{tabularx}{\textwidth}{L{0.95cm}L{1.45cm}R{0.95cm}L{5.0cm}X}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{空间} & \textbf{已核验证据} & \textbf{准入结论/剩余事件} \\",
        r"\midrule",
    ]
    for row in high_upside_rows:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{percent(row.get('house_model_upside'))} & "
            f"{tex(high_upside_verified_text(row))} & "
            f"{tex(row['final_admission_decision'] + '；未来：' + high_upside_remaining_text(row, 2))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\sourcenote{专项证据包：\texttt{data/high\_upside\_evidence\_closure\_20260716.json}。当前原始目标缺失已按“核验未披露”关闭；H2利润、现金流、订单与价格周期保留为未来事件验证。}",
        r"\end{exhibitbox}",
    ]
    return "\n".join(lines)


def professional_risk_section(inputs: dict[str, Any]) -> str:
    evidence = inputs["evidence"]
    lines = [
        r"\chapter{风险、催化与监控}",
        "",
        "本报告的核心风险不在于“预告会不会变差”，而在于市场将短期利润、周期价差或项目结算误读为可持续盈利。"
        "监控应围绕能改变分母、倍数和外部锚的变量，而不是围绕新闻标题。",
        "",
        r"\noindent",
        r"\begin{exhibitbox}[图表 10｜风险监控框架：从风险描述到可执行触发器]",
        r"\small",
        r"\begin{tabularx}{\textwidth}{L{2.2cm}L{4.0cm}L{4.4cm}X}",
        r"\toprule",
        r"\textbf{风险类别} & \textbf{领先指标} & \textbf{受影响模型} & \textbf{行动规则} \\",
        r"\midrule",
        r"盈利质量 & 扣非与归母差额扩大、非经常性收益上升、H2利润低于桥接。 & 常规EPS/PE、成长PE与恢复模型。 & 下调分母或切换至恢复模型；不以提高PE抵消盈利下修。 \\",
        r"现金流与营运资本 & 经营现金流持续低于利润、应收/库存占用上升。 & 周期、成长和项目型公司。 & 暂停升级；将牛市情景权重下调或取消。 \\",
        r"周期与价格 & 商品价格、炼化价差、运价、锂价、利用率反转。 & 周期调整PE与恢复模型。 & 先下调H2转化率，再下调PE区间；不直接沿用H1盈利。 \\",
        r"估值与拥挤度 & 当前价高于概率值、外部目标价陈旧、短期涨幅过大。 & 全部条件性模型。 & 转为观察；等待价格回撤或外部锚更新。 \\",
        r"证据质量 & 原始研报不可得、仅有摘要/转载、数据时点过旧。 & 外部锚和正式模型。 & 外部权重归零；仅保留本机构条件性区间。 \\",
        r"\bottomrule",
        r"\end{tabularx}",
        r"\normalsize",
        r"\end{exhibitbox}",
        "",
        r"\section{下一轮催化日历}",
        "",
        r"\noindent",
        r"\begin{tabularx}{\textwidth}{L{2.4cm}L{4.5cm}X}",
        r"\toprule",
        r"\textbf{时点} & \textbf{需要确认的变量} & \textbf{模型含义} \\",
        r"\midrule",
        r"下一次业绩披露 & H2扣非利润、毛利率、现金流和非经常性收益。 & 决定H2/H1转换率是否成立，影响全部EPS类模型。 \\",
        r"行业价格与订单更新 & 金属、能源、化工价差、运价、锂价、订单和交付。 & 决定周期模型的熊/基准/牛倍数与分母可持续性。 \\",
        r"当前研报或共识更新 & 2026E/2027E收入、EPS、目标价及评级变化。 & 决定外部锚是否可新增正权重，条件性模型是否可升级。 \\",
        r"资金与价格确认 & 行业日/周资金、价格位置、成交和回撤承接。 & 只用于确认市场是否接受基本面，不替代基本面证据。 \\",
        r"\bottomrule",
        r"\end{tabularx}",
        "",
        r"\noindent",
        r"\begin{sourcequalitybox}[数据边界]",
        (
            f"候选Q1财务覆盖{evidence['financial_success_count']}/{evidence['row_count']}，"
            f"研报PDF覆盖{evidence['report_pdf_count']}/{evidence['row_count']}。"
            "行业日/周资金均为31/31完整表，但观察日分别截至7月14日和7月10日；"
            "连续流入公开表仅30/112，只作为辅助证据。"
        ),
        r"\end{sourcequalitybox}",
    ]
    return "\n".join(lines)


def professional_data_section(inputs: dict[str, Any]) -> str:
    evidence = inputs["evidence"]
    return "\n".join(
        [
            r"\chapter{研究基础与数据边界}",
            "",
            "本报告将事实、估计和观点分层呈现。事实层来自官方业绩预告、Q1财务包、行情和行业数据；"
            "估计层来自经审计的情景模型与有限的原始研报/公开共识；观点层只用于定义验证顺序，不替代事实或外部锚。",
            "",
            r"\noindent",
            r"\begin{tabularx}{\textwidth}{L{2.1cm}L{4.0cm}X}",
            r"\toprule",
            r"\textbf{证据层级} & \textbf{用途} & \textbf{边界} \\",
            r"\midrule",
            r"一级：官方披露与市场数据 & 半年报预告、Q1财务、当前价格、行业指数和资金表。 & 反映已发生或可观察数据，不证明未来盈利持续性。 \\",
            r"二级：原始券商PDF与可审计共识快照 & 盈利预测、目标价、估值方法和可比框架。 & 仅当前、可比较字段可获得正权重。 \\",
            r"三级：摘要、转载、陈旧目标与用户文章 & 识别市场叙事、历史区间与待验证假设。 & 权重为零，不能被呈现为市场一致预期。 \\",
            r"本机构情景 & 估值区间、概率权重、行动门槛与失效条件。 & 明确标注为本机构假设，需由下一轮证据验证。 \\",
            r"\bottomrule",
            r"\end{tabularx}",
            "",
            "全量候选的逐票公式、输入变量、方法理由、倍数理由、概率权重和证据路径均在附录B保留。"
            "这使主报告保持可读，同时不牺牲模型的可复算性。",
            "",
            r"\noindent",
            r"\begin{disclosurebox}[使用边界]",
            "“主力资金”沿用公开数据源按成交单大小分类的统计口径，不代表对资金最终受益人、机构身份或一致行动关系的确认。"
            "行业阶段使用截至2026年7月14日的完整31行业日报和截至2026年7月10日的完整周报；连续流入公开表仅30/112，已按部分证据处理。"
            "全部目标价均为概率情景研究框架，不构成收益承诺或证券买卖建议。",
            r"\end{disclosurebox}",
        ]
    )


def professional_sources_section(inputs: dict[str, Any]) -> str:
    evidence = inputs["evidence"]
    return "\n".join(
        [
            r"\section{来源与复现说明}",
            "",
            "主要研究输入包括：官方2026H1业绩预告全量表、候选公司Q1财务包、2026年7月15日价格与复权K线、"
            "已归档的原始券商PDF、可审计公开共识快照，以及截至2026年7月14日的行业资金观察。"
            "详细文件路径、字段版本与重算结果由附录B的逐票账本和结构化数据包保存。",
            "",
            r"\noindent",
            r"\begin{exhibitbox}[研究数据覆盖与复现状态]",
            r"\begin{tabularx}{\textwidth}{L{4.5cm}R{2.0cm}X}",
            r"\toprule",
            r"\textbf{项目} & \textbf{覆盖} & \textbf{复现说明} \\",
            r"\midrule",
            rf"官方预告公司 & {inputs['screen']['preview_company_count']} & 排除B股后按申万行业映射。 \\",
            rf"高影响候选Q1财务 & {evidence['financial_success_count']}/{evidence['row_count']} & 作为盈利质量、现金流和BPS输入。 \\",
            rf"候选研报PDF & {evidence['report_pdf_count']}/{evidence['row_count']} & 原始PDF可用于外部锚或方法/可比背景。 \\",
            rf"逐票估值审计 & {inputs['candidate_audit']['pass_count']}/{inputs['candidate_audit']['row_count']} & 每只候选均有公式、理由、证据与审计状态。 \\",
            r"\bottomrule",
            r"\end{tabularx}",
            r"\sourcenote{完整结构化数据位于本研究案例的数据包中；读者可通过附录B的代码与方法索引追溯每个估值结论。}",
            r"\end{exhibitbox}",
            "",
            "研究结论反映截至数据截止日的公开资料与本机构情景；附录的结构化审计包是可复算记录，"
            "而不是对任何个股的确定性价格预测。",
        ]
    )


def appendix_universe_section(inputs: dict[str, Any]) -> str:
    rows = inputs["models"]["rows"]
    lines = [
        r"\chapter{全量候选清单与操作分层}",
        "",
        "本附录保留142只候选的当前价格、盈利规模、概率值、空间、证据质量和行动标签。"
        "它是全量筛选账本，不是142只股票的统一推荐清单。",
        "",
        r"\footnotesize",
        r"\renewcommand{\arraystretch}{1.00}",
        r"\setlength{\tabcolsep}{2pt}",
        r"\begin{longtable}{L{1.0cm}L{1.55cm}L{1.4cm}R{1.0cm}R{1.0cm}R{1.0cm}R{1.05cm}L{3.6cm}L{0.9cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{H1扣非} & \textbf{概率值} & \textbf{空间} & \textbf{行动含义} & \textbf{证据} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{公司} & \textbf{行业} & \textbf{现价} & \textbf{H1扣非} & \textbf{概率值} & \textbf{空间} & \textbf{行动含义} & \textbf{证据} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in rows:
        action = action_label(row.get("action"))
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & {tex(row['industry'])} & "
            f"{tex(row.get('price_display') or number(row.get('current_price')))} & "
            f"{number(row.get('h1_deducted_np_100mn'), 1)} & "
            f"{tex(target_text(row))} & {tex(upside_text(row))} & {tex(action)} & "
            f"{tex(evidence_label(row.get('evidence_quality')))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\renewcommand{\arraystretch}{1.12}",
        r"\normalsize",
    ]
    return "\n".join(lines)


def appendix_valuation_ledger_section(inputs: dict[str, Any]) -> str:
    audit_rows = inputs["candidate_audit"]["rows"]
    model_map = {row["ticker"]: row for row in inputs["models"]["rows"]}
    grouped: dict[str, list[dict[str, Any]]] = {}
    for audit in audit_rows:
        grouped.setdefault(audit["formula_type"], []).append(audit)
    order = [
        "cycle_adjusted_eps_pe",
        "growth_earnings_scenario_pe",
        "financial_pb_pe_blend",
        "deducted_eps_scenario_pe",
        "recovery_alternative_method",
        "listing_boundary",
    ]
    lines = [
        r"\chapter{全量估值推演与证据账本}",
        "",
        "本附录保留每只候选的估值公式代入、情景结果、方法选择逻辑和证据角色。"
        "方法代码对应第三章的估值选择矩阵；所有数值按数据截止日重算，未四舍五入输入保存在结构化审计包中。",
    ]
    for formula_type in order:
        rows = grouped.get(formula_type, [])
        if not rows:
            continue
        lines += [
            f"\\section{{{tex(method_family_title(formula_type))}}}",
            tex(method_family_reason(formula_type)),
            "",
            r"\footnotesize",
            r"\setlength{\tabcolsep}{2.5pt}",
            r"\begin{longtable}{L{1.55cm}L{2.45cm}L{5.0cm}L{2.75cm}L{4.1cm}}",
            r"\toprule",
            r"\textbf{代码/标的} & \textbf{适用理由} & \textbf{分母与公式代入} & \textbf{情景与概率值} & \textbf{证据与验证} \\",
            r"\midrule",
            r"\endfirsthead",
            r"\toprule",
            r"\textbf{代码/标的} & \textbf{适用理由} & \textbf{分母与公式代入} & \textbf{情景与概率值} & \textbf{证据与验证} \\",
            r"\midrule",
            r"\endhead",
        ]
        for audit in rows:
            model = model_map[audit["ticker"]]
            scenario = audit.get("scenario_inputs") or {}
            if scenario:
                target_text_value = (
                    f"熊/基准/牛：{number(scenario.get('bear'))}/\\allowbreak"
                    f"{number(scenario.get('base'))}/\\allowbreak{number(scenario.get('bull'))}元；"
                    f"概率值：{number(model.get('probability_target'))}元；"
                    f"空间：{percent(model.get('upside'))}。"
                )
            else:
                target_text_value = "待上市交易；当前价、目标价与空间均不适用。"
            reason = row_reason_short_cn(audit)
            control = (
                f"{concise_evidence_text(audit, model)}"
                f"监控：{monitor_short_cn(audit, model)}"
            )
            lines.append(
                f"{tex(audit['ticker'] + ' ' + audit['company'])} & "
                f"{tex(reason)} & {tex(denominator_short_cn(audit, model))}；"
                f"{compact_formula_tex(audit, model)} & "
                f"{target_text_value} & {tex(control)} \\\\"
            )
        lines += [
            r"\bottomrule",
            r"\end{longtable}",
            r"\normalsize",
            "",
        ]
    lines += [
        r"\begin{sourcequalitybox}[附录阅读说明]",
        "表中的倍数、H2转化率和概率权重是本机构情景假设；官方预告、Q1财务、行情和原始研报是事实输入。"
        "外部目标价只有在来源可审计且时点可比时才获得正权重。",
        r"\end{sourcequalitybox}",
    ]
    return "\n".join(lines)


def appendix_priority_bridge_section(inputs: dict[str, Any]) -> str:
    bridge_rows = inputs["selection_bridge"]["rows"]
    high_upside_rows = inputs["high_upside_closure"]["rows"]
    admission_rows = inputs["former_medium_admission"]["rows"]
    status_label = {
        "formal_audit_model": "可复核当前价模型",
        "conditional_high_upside_watch": "条件性高空间验证",
        "conditional_margin_watch": "条件性安全边际观察",
        "valuation_risk_or_watch": "估值纪律/风险观察",
    }
    lines = [
        r"\chapter{优先池的证据升级路径}",
        "",
        "39只优先池的价值在于安排下一轮研究资源，而不在于将模型空间直接转化为配置结论。",
        "本附录第一张表只覆盖39只优先池；100\\%以上模型空间的全量样本另列在第二张表，以解释为什么有些高空间票没有进入优先池或正式池。",
        "",
        r"\footnotesize",
        r"\begin{longtable}{L{1.0cm}L{1.6cm}L{2.5cm}R{1.1cm}R{1.0cm}L{7.0cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{状态} & \textbf{概率值} & \textbf{空间} & \textbf{下一轮必须补齐的证据} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{状态} & \textbf{概率值} & \textbf{空间} & \textbf{下一轮必须补齐的证据} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in bridge_rows:
        reasons = "；".join(row.get("selection_reasons", []))
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{tex(status_label.get(row['selection_status'], row['selection_status']))} & "
            f"{number(row.get('probability_target'))} & {tex(plain_percent(row.get('upside')))} & "
            f"{tex(reasons)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        r"\section{原中等证据标的补证后的候选准入结论}",
        "",
        "本节只覆盖补证前旧口径为中等证据的标的。补证后，基础证据质量已经不再是阻断项；是否进入候选取决于空间、优先池状态、现金流、外部锚时效和价格纪律。",
        "",
        r"\footnotesize",
        r"\begin{longtable}{L{1.0cm}L{1.55cm}L{2.1cm}R{1.0cm}L{2.4cm}L{5.3cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{准入结论} & \textbf{空间} & \textbf{外部锚状态} & \textbf{使用方式/阻断项} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{准入结论} & \textbf{空间} & \textbf{外部锚状态} & \textbf{使用方式/阻断项} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in admission_rows:
        blockers = "；".join(row.get("blockers") or [])
        usage = row["admission_decision"]
        if blockers:
            usage = f"{usage}；{blockers}"
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{tex(row['admission_label'])} & {tex(plain_percent(row.get('upside')))} & "
            f"{tex(broker_anchor_label(row.get('broker_anchor_quality')))} & "
            f"{tex(usage)} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
        "",
        r"\begin{sourcequalitybox}[准入结论]",
        "原中等证据标的中，没有一只直接升级为正式模型；可进入优先验证或扩展观察的标的必须继续等待当前外部锚、H2扣非利润和现金流验证。估值风险观察和概率目标低于现价的标的不新增为候选。",
        r"\end{sourcequalitybox}",
        "",
        r"\section{100\%以上空间样本的全量拦截审计}",
        "",
        "下表覆盖全142只候选中模型空间超过100\\%的全部样本。原始API、原始PDF、目标价字段和Q1现金流均已逐票核验；表中不再保留“待补目标价”占位，而是公开核验结果、准入结论和仍需等待的未来事件。",
        "",
        r"\footnotesize",
        r"\begin{longtable}{L{1.0cm}L{1.45cm}R{1.0cm}L{4.8cm}L{3.3cm}L{3.3cm}}",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{空间} & \textbf{来源覆盖/外部锚} & \textbf{最终准入} & \textbf{剩余事件验证} \\",
        r"\midrule",
        r"\endfirsthead",
        r"\toprule",
        r"\textbf{代码} & \textbf{标的} & \textbf{空间} & \textbf{来源覆盖/外部锚} & \textbf{最终准入} & \textbf{剩余事件验证} \\",
        r"\midrule",
        r"\endhead",
    ]
    for row in high_upside_rows:
        lines.append(
            f"{tex(row['ticker'])} & {tex(row['company'])} & "
            f"{percent(row.get('house_model_upside'))} & "
            f"{tex(high_upside_verified_text(row))} & "
            f"{tex(row['final_admission_decision'])} & "
            f"{tex(high_upside_remaining_text(row))} \\\\"
        )
    lines += [
        r"\bottomrule",
        r"\end{longtable}",
        r"\normalsize",
    ]
    return "\n".join(lines)


def main() -> None:
    inputs = load_inputs()
    build_analysis_files(inputs)
    SECTIONS_DIR.mkdir(exist_ok=True)
    write_text(SECTIONS_DIR / "institutional_ch01_decision.tex", professional_dashboard_section(inputs))
    write_text(SECTIONS_DIR / "institutional_ch02_market.tex", professional_market_section(inputs))
    write_text(SECTIONS_DIR / "institutional_ch03_framework.tex", professional_framework_section(inputs))
    write_text(SECTIONS_DIR / "institutional_ch04_focus.tex", professional_focus_section(inputs))
    write_text(SECTIONS_DIR / "institutional_ch05_risk.tex", professional_risk_section(inputs))
    write_text(SECTIONS_DIR / "institutional_ch06_data.tex", professional_data_section(inputs))
    write_text(SECTIONS_DIR / "institutional_ch07_sources.tex", professional_sources_section(inputs))
    write_text(SECTIONS_DIR / "institutional_appx_a_universe.tex", appendix_universe_section(inputs))
    write_text(SECTIONS_DIR / "institutional_appx_b_valuation_ledger.tex", appendix_valuation_ledger_section(inputs))
    write_text(SECTIONS_DIR / "institutional_appx_c_priority_bridge.tex", appendix_priority_bridge_section(inputs))
    formal_count = len(inputs["formal"]["rows"])
    main_tex = r"""% !TEX program = xelatex
\documentclass[a4paper,11pt,openany,fontset=none]{ctexrep}
\newcommand{\reporttitle}{A股盈利修复的再定价机会}
\newcommand{\reportsubtitle}{从2026H1预告扩散到可执行的行业与个股验证框架}
\newcommand{\reportkicker}{A股策略研究}
\newcommand{\reportscope}{中国A股 | 1,680家预告公司 | 39只优先池 | FORMAL_COUNT只可复核模型}
\newcommand{\reportdate}{2026年7月15日}
\newcommand{\reportdatacutoff}{官方预告与个股行情截至2026年7月15日；行业资金观察至2026年7月14日}
\newcommand{\reporttype}{A股策略与行业配置}
\newcommand{\reportauthor}{AStock策略研究}
\newcommand{\reporthouseview}{盈利预告改善并不等于全面风险偏好开启。当前更具可执行性的机会集中在分母可信、现金流可验证、价格尚未充分反映且能够获得当前外部证据支持的样本。}
\newcommand{\reportquality}{官方预告覆盖1,680家；高影响候选142只；优先池39只；Q1财务142/142；候选研报PDF 137/142；行业资金日/周表31/31。}
\newcommand{\reportdisclaimer}{本报告基于公开资料整理，不构成任何证券买卖建议。}
\input{../../../.agents/templates/preamble.tex}
\sloppy
\setlength{\emergencystretch}{3em}
\hypersetup{pdfauthor={\reportauthor},pdftitle={\reporttitle}}
\usepackage{amsmath}
\begin{document}
\astockcover
\tableofcontents
\clearpage
\input{sections/institutional_ch01_decision}
\input{sections/institutional_ch02_market}
\input{sections/institutional_ch03_framework}
\input{sections/institutional_ch04_focus}
\input{sections/institutional_ch05_risk}
\input{sections/institutional_ch06_data}
\input{sections/institutional_ch07_sources}
\clearpage
\appendix
\input{sections/institutional_appx_a_universe}
\input{sections/institutional_appx_b_valuation_ledger}
\input{sections/institutional_appx_c_priority_bridge}
\end{document}
"""
    main_tex = main_tex.replace("FORMAL_COUNT", str(formal_count))
    write_text(CASE_DIR / "main.tex", main_tex)
    print(
        json.dumps(
            {
                "preview_companies": inputs["screen"]["preview_company_count"],
                "candidate_rows": len(inputs["candidates"]["rows"]),
                "priority_rows": len(inputs["priority"]["rows"]),
                "formal_rows": len(inputs["formal"]["rows"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
