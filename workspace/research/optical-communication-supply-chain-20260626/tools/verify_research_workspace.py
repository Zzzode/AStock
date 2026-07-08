#!/usr/bin/env python3
"""Verify the optical communication research workspace."""
from __future__ import annotations

import json
import math
import re
import subprocess
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def load_json(rel: str):
    return json.loads((BASE / rel).read_text(encoding="utf-8"))


def text(rel: str) -> str:
    return (BASE / rel).read_text(encoding="utf-8", errors="ignore")


def has_pdf_pages() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return False, "main.pdf missing"
    proc = subprocess.run(["pdfinfo", str(pdf)], text=True, capture_output=True)
    if proc.returncode != 0:
        return False, "pdfinfo failed"
    m = re.search(r"Pages:\s+(\d+)", proc.stdout)
    if not m:
        return False, "page count missing"
    pages = int(m.group(1))
    return pages >= 40, f"pages={pages}"


def no_pattern_in_pdf(pattern: str) -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return False, "main.pdf missing"
    out = BASE / "main_current_text.txt"
    if not out.exists():
        proc = subprocess.run(["pdftotext", str(pdf), str(out)], text=True, capture_output=True)
        if proc.returncode != 0:
            return False, "pdftotext failed"
    body = out.read_text(encoding="utf-8", errors="ignore")
    return pattern not in body, f"pattern={pattern}"


def valuation_complete() -> tuple[bool, str]:
    model = load_json("data/current_valuation_model_20260626.json")
    required = [
        "code", "name", "current_price_cny", "shares_100mn", "market_cap_100mn_cny",
        "eps_2026e", "eps_2027e", "eps_2028e", "method", "bear_value_cny",
        "base_target_cny", "bull_value_cny", "fair_value_range_cny",
        "implied_upside", "rating_cn", "catalyst", "invalidation", "quality",
        "method_short", "valuation_style", "secondary_check", "valuation_weights",
        "base_components", "bear_components", "bull_components", "book_value_per_share",
        "sales_per_share_2027e", "expectation_value_cny", "expectation_upside",
        "expectation_components", "expectation_driver", "expected_revenue_growth_2027",
        "broker_source", "broker_rating", "broker_forecast_note", "broker_evidence_quality",
        "current_implied_pe_2026", "current_implied_ps_2026", "current_implied_pb",
        "trading_value_100mn_cny", "trading_value_percentile", "market_sentiment_score",
        "market_sentiment_regime", "sentiment_premium_vs_intrinsic", "market_anchor_value_cny",
        "final_anchor_weights", "final_anchor_weights_label", "final_target_cny",
        "final_upside", "market_action_logic", "embedded_expectation_gap",
    ]
    problems = []
    for row in model.get("rows", []):
        for key in required:
            if row.get(key) in (None, "", "n.a."):
                problems.append(f"{row.get('code')} missing {key}")
        target = row["base_components"]["weighted_value_cny"]
        bear = row["bear_components"]["weighted_value_cny"]
        bull = row["bull_components"]["weighted_value_cny"]
        upside = row["base_target_cny"] / row["current_price_cny"] - 1
        mcap = row["current_price_cny"] * row["shares_100mn"]
        if abs(target - row["base_target_cny"]) > 0.02:
            problems.append(f"{row['code']} target math")
        if abs(bear - row["bear_value_cny"]) > 0.02:
            problems.append(f"{row['code']} bear math")
        if abs(bull - row["bull_value_cny"]) > 0.02:
            problems.append(f"{row['code']} bull math")
        if abs(upside - row["implied_upside"]) > 0.0005:
            problems.append(f"{row['code']} upside math")
        if abs(mcap - row["market_cap_100mn_cny"]) > 0.05:
            problems.append(f"{row['code']} mcap math")
        expectation = row["expectation_components"]["weighted_value_cny"]
        expectation_upside = row["expectation_value_cny"] / row["current_price_cny"] - 1
        final_weights = row["final_anchor_weights"]
        final_target = (
            row["base_target_cny"] * final_weights["fundamental"]
            + row["market_anchor_value_cny"] * final_weights["market"]
            + (row.get("broker_anchor_value_cny") or 0.0) * final_weights["street"]
        )
        if row["market_sentiment_score"] >= 62 and row["sentiment_premium_vs_intrinsic"] >= 0.70:
            final_target = max(final_target, row["market_anchor_value_cny"])
        final_upside = row["final_target_cny"] / row["current_price_cny"] - 1
        if abs(expectation - row["expectation_value_cny"]) > 0.02:
            problems.append(f"{row['code']} expectation math")
        if abs(expectation_upside - row["expectation_upside"]) > 0.0005:
            problems.append(f"{row['code']} expectation upside math")
        if abs(final_target - row["final_target_cny"]) > 0.02:
            problems.append(f"{row['code']} final target math")
        if abs(final_upside - row["final_upside"]) > 0.0005:
            problems.append(f"{row['code']} final upside math")
    styles = {row.get("valuation_style") for row in model.get("rows", [])}
    if len(styles) < 4:
        problems.append(f"method profiles too narrow: {sorted(styles)}")
    return not problems and len(model.get("rows", [])) == 26, "; ".join(problems) or f"26 rows complete, styles={len(styles)}"


def source_files_exist() -> tuple[bool, str]:
    reg = load_json("data/source_registry.json")
    captures = load_json("data/source_capture_manifest_20260626.json").get("captures", [])
    ok = len(reg.get("items", [])) >= 34 and len(captures) >= 34
    missing = [c["path"] for c in captures if not (BASE / c["path"]).exists()]
    return ok and not missing, f"sources={len(reg.get('items', []))}, captures={len(captures)}, missing={missing[:2]}"


def check_file(rel: str) -> tuple[bool, str]:
    path = BASE / rel
    return path.exists() and path.stat().st_size > 0, rel


def section_has_prose(rel: str) -> tuple[bool, str]:
    body = text(rel)
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", body))
    tables = body.count(r"\begin{exhibitbox}")
    return chinese_chars > 180 and body.find(r"\begin{exhibitbox}") > 0, f"chars={chinese_chars}, exhibits={tables}"


def full_chain_complete() -> tuple[bool, str]:
    body = text("sections/ch04_supply_chain.tex") + text("sections/ch05_demand.tex") + text("analysis/optical_chain_map.mmd")
    required = ["材料", "设备", "光芯片", "光器件", "光模块", "光纤光缆", "通信线缆", "高速线缆", "网络设备", "下游应用"]
    missing = [term for term in required if term not in body]
    return not missing, f"missing={missing}"


def full_chain_map_tickers_explicit() -> tuple[bool, str]:
    body = text("sections/ch04_supply_chain.tex")
    start = body.find(r"\begin{exhibitbox}[表：完整光通信产业链地图]")
    end = body.find(r"\end{exhibitbox}", start)
    block = body[start:end] if start >= 0 and end > start else ""
    required = [
        "通鼎互联(002491)",
        "永鼎股份(600105)",
        "兆龙互连(300913)",
        "意华股份(002897)",
        "神宇股份(300563)",
    ]
    missing = [term for term in required if term not in block]
    return not missing, f"missing={missing}"


def broker_and_expectation_present() -> tuple[bool, str]:
    body = text("sections/ch01_ic_summary.tex") + text("sections/ch07_sentiment.tex") + text("sections/ch08_valuation.tex")
    required = ["市场预期估值", "市场隐含预期与情绪锚", "综合目标价", "公开券商/一致预期", "2026E收入", "券商均值", "未披露字段不做推断"]
    missing = [term for term in required if term not in body]
    broker_rows = load_json("data/broker_consensus_snapshot_20260626.json").get("rows", [])
    expectation_rows = load_json("data/market_expectation_valuation_20260626.json").get("rows", [])
    sentiment_rows = load_json("data/market_sentiment_anchor_20260626.json").get("rows", [])
    if len(broker_rows) != 26:
        missing.append(f"broker_rows={len(broker_rows)}")
    if len(expectation_rows) != 26:
        missing.append(f"expectation_rows={len(expectation_rows)}")
    if len(sentiment_rows) != 26:
        missing.append(f"sentiment_rows={len(sentiment_rows)}")
    return not missing, f"missing={missing}"


def chinese_language_gate() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    out = BASE / "main_current_text.txt"
    if pdf.exists() and not out.exists():
        subprocess.run(["pdftotext", str(pdf), str(out)], text=True, capture_output=True)
    body = out.read_text(encoding="utf-8", errors="ignore") if out.exists() else text("main.tex")
    forbidden = [
        "Optical fiber/cable",
        "High-speed optical",
        "Business-model matched",
        "cycle-normalized",
        "customer qualification",
        "current price",
        "target price",
        "strongest earnings delivery",
    ]
    hits = [term for term in forbidden if term in body]
    return not hits, f"forbidden={hits}"


def investment_advice_depth() -> tuple[bool, str]:
    body = text("sections/ch10_investment.tex")
    required = [
        "最终投资结论",
        "最终组合建议矩阵",
        "重点标的最终执行清单",
        "情景、动作与复盘纪律",
        "下一次更新检查清单",
        "研究权重",
        "加仓/上修条件",
        "降级/退出条件",
        "中际旭创",
        "新易盛",
        "中天科技",
        "长飞光纤",
        "通鼎互联",
    ]
    missing = [term for term in required if term not in body]
    prose_chars = len(re.sub(r"\\[a-zA-Z]+|[{}\\\\&%_$#^~]", "", body))
    if prose_chars < 2600:
        missing.append(f"chars={prose_chars}")
    return not missing, f"missing={missing}"


def post_cutoff_preview_present() -> tuple[bool, str]:
    preview = load_json("data/earnings_preview_h1_2026_20260706.json")
    census = load_json("data/optical_preview_census_20260706.json")
    previews = preview.get("previews", {})
    in_universe = [c for c, p in previews.items() if p.get("coverage") in {"covered", "watch_pool"}]
    ok = (
        "600105" in previews and "301165" in previews and "603618" in previews
        and len(in_universe) >= 3
        and census.get("universe_size") == 36
        and census.get("previews_in_universe") == 3
        and "stock_yjyg_em" in census.get("method", "")
    )
    return ok, f"in_universe={len(in_universe)}, universe={census.get('universe_size')}"


def post_cutoff_disclosure_in_pdf() -> tuple[bool, str]:
    pdf = BASE / "main.pdf"
    if not pdf.exists():
        return False, "main.pdf missing"
    out = BASE / "main_current_text.txt"
    if not out.exists():
        proc = subprocess.run(["pdftotext", str(pdf), str(out)], text=True, capture_output=True)
        if proc.returncode != 0:
            return False, "pdftotext failed"
    body = out.read_text(encoding="utf-8", errors="ignore")
    needed = ["业绩预告", "数据截止", "2026-07-06"]
    missing = [t for t in needed if t not in body]
    return not missing, f"missing={missing}"


def frozen_baseline_intact() -> tuple[bool, str]:
    market = load_json("data/raw_market_data_20260626.json")
    model = load_json("data/current_valuation_model_20260626.json")
    yd = next((r for r in model.get("rows", []) if r["code"] == "600105"), None)
    ok = (
        market.get("run_date") == "2026-06-26"
        and len(market.get("quotes", {})) == 26
        and model.get("run_date") == "2026-06-26"
        and yd is not None
        and yd.get("rating_cn") == "中性观察"
        and abs(yd.get("final_upside", 0) + 0.30) < 0.02
    )
    return ok, f"600105 rating={yd.get('rating_cn') if yd else None}, upside={round(yd.get('final_upside'), 3) if yd else None}"


def preview_revision_dual_view() -> tuple[bool, str]:
    rev = load_json("data/earnings_preview_revision_20260706.json")
    revisions = rev.get("revisions", [])
    yd = next((r for r in revisions if r["code"] == "600105"), None)
    ok = (
        rev.get("cutoff") == "2026-06-26"
        and yd is not None
        and "frozen" in yd and "revised" in yd
        and yd["revised"]["eps_2026e"] > yd["frozen"]["eps_2026e"]
        and rev.get("seasonality_assumption") is not None
    )
    return ok, f"revisions={len(revisions)}, has_600105={yd is not None}"


def valuation_reproducibility() -> tuple[bool, str]:
    body = text("analysis/valuation_audit.md")
    ok = "Model Reproducibility: PASS" in body and "价格/股本核对表" in body and "MECHANICAL_PASS_INSTITUTIONAL_FAIL" in body
    return ok, "reproducibility PASS + reconciliation + downgrade"


def growth_earnings_present() -> tuple[bool, str]:
    driver = load_json("data/growth_driver_model.json")
    rows = driver.get("rows", [])
    has_impl = any(r.get("current_price_implied_np_cagr_3y") is not None for r in rows)
    model_body = text("analysis/valuation_model.md")
    ok = (
        len(rows) == 26
        and has_impl
        and "成长盈利依赖" in model_body
        and "季节性校准" in model_body
        and "现价隐含" in text("analysis/implied_growth_sensitivity.md")
    )
    return ok, f"driver_rows={len(rows)}, implied_present={has_impl}"


def broker_street_downgrade_present() -> tuple[bool, str]:
    packet = load_json("data/broker_street_consensus_20260626.json")
    body = text("data/broker_street_consensus_20260626.md")
    ok = (
        packet.get("signoff_downgrade") == "MECHANICAL_PASS_INSTITUTIONAL_FAIL"
        and packet.get("coverage_universe") == 26
        and "not disclosed" in body
    )
    return ok, f"downgrade={packet.get('signoff_downgrade')}, universe={packet.get('coverage_universe')}"


def valuation_gate_sections() -> tuple[bool, str]:
    body = text("analysis/valuation_model.md")
    required = ["季节性校准", "下一季度阈值", "成长盈利依赖", "全链条分类依赖", "市场隐含预期与情绪锚", "市场预期估值桥", "方法与假设桥"]
    missing = [s for s in required if s not in body]
    ch08 = text("sections/ch08_valuation.tex")
    ch08_required = ["估值哲学与门禁", "分母正常化", "业绩预告", "成长盈利拆分与现价隐含增速", "券商/Street 对照与发布降级", "业务模型—估值方法匹配矩阵"]
    ch08_missing = [s for s in ch08_required if s not in ch08]
    return not missing and not ch08_missing, f"model_missing={missing}, ch08_missing={ch08_missing}"


def preview_in_valuation() -> tuple[bool, str]:
    """The covered name with H1 guidance (600105) must have its guidance folded
    into the valuation denominator: 2026E EPS lifted above the Q1-annualized
    basis, and ch08 must state the guidance is computed into valuation."""
    model = load_json("data/current_valuation_model_20260626.json")
    yd = next((r for r in model.get("rows", []) if r["code"] == "600105"), None)
    ch08 = text("sections/ch08_valuation.tex")
    ok = (
        yd is not None
        and yd.get("eps_basis") == "h1_guidance"
        and yd.get("has_h1_guidance") is True
        and yd.get("eps_2026e", 0) > 0.6  # guidance lifts EPS well above the 0.45 q1-annualized basis
        and "业绩预告已计入估值" in ch08
    )
    return ok, f"600105 eps_basis={yd.get('eps_basis') if yd else None}, eps26={round(yd.get('eps_2026e'),3) if yd else None}"


def main() -> int:
    checks = []
    for rel in [
        "research_brief.md", "main.tex", "review_log.md", "data_room_index.md",
        "completion_audit_manifest.json", "completion_audit_manifest.md",
        "source_exhaustion_log.json", "source_exhaustion_log.md",
        "data/raw_market_data_20260626.json", "data/raw_financials_20260626.json",
        "data/raw_market_data.md", "data/raw_financials.md",
        "data/verified_market_data.md", "data/verified_financials.md",
        "data/source_registry.json", "data/source_registry.md",
        "data/claim_audit.json", "data/claim_audit.md",
        "data/industry_universe_coverage.json", "data/industry_universe_coverage.md",
        "data/current_valuation_model_20260626.json", "data/current_valuation_model_20260626.md",
        "data/market_sentiment_anchor_20260626.json", "data/market_sentiment_anchor_20260626.md",
        "data/market_expectation_valuation_20260626.json", "data/market_expectation_valuation_20260626.md",
        "data/broker_consensus_snapshot_20260626.json", "data/broker_consensus_snapshot_20260626.md",
        "data/consensus_analysis.md", "data/broker_target_price_history.md",
        "data/earnings_expectations_vs_delivery.md", "analysis/valuation_model.md",
        "analysis/broker_comparison.md", "analysis/valuation_audit.md", "analysis/industry_landscape.md",
        "analysis/house_view.md", "analysis/risk_framework.md",
        "analysis/template_brief.md", "analysis/exhibit_plan.md",
        "analysis/optical_chain_map.mmd", "sections/app_source_audit.tex",
        "sections/app_research_workplan.tex",
        "sections/ch11_earnings_preview.tex",
        "data/earnings_preview_h1_2026_20260706.json", "data/earnings_preview_h1_2026_20260706.md",
        "data/optical_preview_census_20260706.json", "data/optical_preview_census_20260706.md",
        "data/earnings_preview_revision_20260706.json", "data/earnings_preview_revision_20260706.md",
        "analysis/growth_earnings_model.md", "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md", "data/growth_driver_model.json",
        "data/broker_street_consensus_20260626.json", "data/broker_street_consensus_20260626.md",
    ]:
        checks.append((f"file:{rel}", *check_file(rel)))
    for idx in range(1, 11):
        rel = f"sections/ch{idx:02d}_" + [
            "ic_summary", "evidence", "technology", "supply_chain", "demand",
            "companies", "sentiment", "valuation", "risks", "investment",
        ][idx - 1] + ".tex"
        checks.append((f"section_prose:{idx}", *section_has_prose(rel)))
    checks.extend([
        ("valuation_complete", *valuation_complete()),
        ("source_files_exist", *source_files_exist()),
        ("pdf_pages", *has_pdf_pages()),
        ("pdf_no_TODO", *no_pattern_in_pdf("TODO")),
        ("pdf_no_placeholder", *no_pattern_in_pdf("<Report Title>")),
        ("pdf_has_valuation", "目标价" in text("sections/ch08_valuation.tex") and "隐含空间" in text("sections/ch08_valuation.tex"), "valuation terms"),
        ("pdf_has_disclaimer", "不构成任何证券买卖建议" in text("main.tex"), "disclaimer"),
        ("mermaid_used", "flowchart LR" in text("analysis/optical_chain_map.mmd"), "Mermaid flowchart"),
        ("broker_targets_not_substitute", "不作为估值输入" in text("sections/ch07_sentiment.tex"), "broker boundary"),
        ("source_boundary", "未披露" in text("sections/ch02_evidence.tex") and "券商数据只用于识别市场预期" in text("sections/ch02_evidence.tex"), "source boundary"),
        ("broker_and_expectation_present", *broker_and_expectation_present()),
        ("chinese_language_gate", *chinese_language_gate()),
        ("full_chain_complete", *full_chain_complete()),
        ("full_chain_map_tickers_explicit", *full_chain_map_tickers_explicit()),
        ("watchlist_present", "罗博特科" in text("sections/ch04_supply_chain.tex") and "观察池" in text("sections/ch04_supply_chain.tex"), "equipment watchlist"),
        ("tongding_present", "通鼎互联" in text("sections/ch04_supply_chain.tex") and "002491" in text("data/current_valuation_model_20260626.md"), "Tongding included"),
        ("industry_universe_present", "产业链标的覆盖" in text("data/industry_universe_coverage.md") and "特发信息" in text("data/industry_universe_coverage.md"), "coverage and watchlist"),
        ("research_workplan_present", "全链条调研问题库" in text("sections/app_research_workplan.tex") and "更新触发规则" in text("sections/app_research_workplan.tex"), "research workplan"),
        ("investment_advice_depth", *investment_advice_depth()),
        ("raw_quote_count", len(load_json("data/raw_market_data_20260626.json").get("quotes", {})) == 26, "26 quotes"),
        ("raw_financial_count", len(load_json("data/raw_financials_20260626.json").get("financials", {})) == 26, "26 financial packets"),
        ("weighted_upside_present", math.isfinite(load_json("data/current_valuation_model_20260626.json").get("weighted_base_upside")), "weighted upside"),
        ("post_cutoff_preview_present", *post_cutoff_preview_present()),
        ("post_cutoff_disclosure_in_pdf", *post_cutoff_disclosure_in_pdf()),
        ("frozen_baseline_intact", *frozen_baseline_intact()),
        ("preview_revision_dual_view", *preview_revision_dual_view()),
        ("valuation_reproducibility", *valuation_reproducibility()),
        ("growth_earnings_present", *growth_earnings_present()),
        ("broker_street_downgrade_present", *broker_street_downgrade_present()),
        ("valuation_gate_sections", *valuation_gate_sections()),
        ("preview_in_valuation", *preview_in_valuation()),
    ])
    pass_count = 0
    fail_count = 0
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        if ok:
            pass_count += 1
        else:
            fail_count += 1
        print(f"{status}: {name} - {detail}")
    print(f"SUMMARY: PASS={pass_count} FAIL={fail_count}")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
