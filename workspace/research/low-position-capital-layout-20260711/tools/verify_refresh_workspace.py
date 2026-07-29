#!/usr/bin/env python3
"""Verify the rolling 2026-07-15 full-market refresh."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REFRESH_DIR = CASE_DIR / "refresh-20260715"
DATA_DIR = REFRESH_DIR / "data"


def load(name: str) -> Any:
    return json.loads((DATA_DIR / name).read_text())


def main() -> int:
    screen = load("full_market_preview_screen_20260715.json")
    candidates = load("full_market_candidates_20260715.json")
    priority = load("full_market_priority_pool_20260715.json")
    evidence = load("full_market_valuation_evidence_20260715.json")
    candidate_models = load("full_market_candidate_valuation_20260715.json")
    recovery_packet = load("valuation_recovery_601360_000042_20260715.json")
    candidate_audit = load("full_market_candidate_valuation_audit_20260715.json")
    priority_models = load("full_market_priority_valuation_20260715.json")
    selection_bridge = load("formal_selection_bridge_20260715.json")
    high_upside_audit = load("high_upside_selection_audit_20260715.json")
    high_upside_closure = load("high_upside_evidence_closure_20260716.json")
    former_medium_admission = load("former_medium_candidate_admission_20260715.json")
    formal = load("current_valuation_model_20260715.json")
    capital_manifest = load("capital_flow_refresh_manifest_20260715.json")
    sector_scan = load("sector_scan_20260715.json")
    continuous = load("raw_continuous_tables_20260714.json")[0]
    root_candidate_models = json.loads(
        (CASE_DIR / "data" / "full_market_candidate_valuation_20260715.json").read_text()
    )
    root_priority_models = json.loads(
        (CASE_DIR / "data" / "full_market_priority_valuation_20260715.json").read_text()
    )
    checks: list[tuple[str, bool]] = []
    checks.append(("full official preview rows", screen["source_preview_row_count"] == 4429))
    checks.append(("eligible A-share rows", screen["eligible_a_share_metric_row_count"] == 4339))
    checks.append(("preview company count", screen["preview_company_count"] == 1680))
    checks.append(("industry mapping coverage", screen["mapped_company_count"] == 1678))
    checks.append(("high-impact candidate count", len(candidates["rows"]) == 142))
    checks.append(("priority count", len(priority["rows"]) == 39))
    checks.append(("candidate Q1 financial coverage", evidence["financial_success_count"] == 142))
    checks.append(("candidate report metadata coverage", evidence["report_metadata_count"] >= 137))
    checks.append(("candidate broker PDF coverage", evidence["report_pdf_count"] >= 137))
    checks.append(("candidate target extraction coverage", evidence["target_extract_count"] >= 33))
    checks.append(("candidate model coverage", len(candidate_models["rows"]) == 142))
    checks.append((
        "candidate evidence quality has no medium",
        all(row.get("evidence_quality") != "medium" for row in candidate_models["rows"]),
    ))
    checks.append((
        "candidate evidence quality basis complete",
        all(
            row.get("evidence_quality") != "high"
            or (row.get("evidence_quality_basis") and row.get("broker_anchor_quality") is not None)
            for row in candidate_models["rows"]
        ),
    ))
    checks.append(("candidate row-level audit coverage", candidate_audit["row_count"] == 142 and len(candidate_audit["rows"]) == 142))
    checks.append(("candidate row-level audit pass", candidate_audit["pass_count"] == 142 and candidate_audit["fail_count"] == 0 and all(row.get("audit_status") == "PASS" for row in candidate_audit["rows"])))
    checks.append((
        "candidate audit evidence quality has no medium",
        all(row.get("evidence_quality") != "medium" for row in candidate_audit["rows"]),
    ))
    checks.append((
        "candidate audit evidence basis complete",
        all(
            row.get("evidence_quality") != "high"
            or (row.get("evidence_quality_basis") and row.get("broker_anchor_quality") is not None)
            for row in candidate_audit["rows"]
        ),
    ))
    checks.append(("candidate audit formula fields complete", all(row.get("formula_type") and row.get("denominator") and row.get("formula") and row.get("final_target_formula") and row.get("evidence_sources") for row in candidate_audit["rows"] if row.get("formula_type") != "listing_boundary") and all(row.get("formula") and row.get("audit_note") for row in candidate_audit["rows"])))
    checks.append(("candidate audit rationale fields complete", all(row.get("why_this_method") and row.get("why_this_denominator") and row.get("why_these_multiples") and row.get("why_these_probabilities") and row.get("evidence_role") for row in candidate_audit["rows"])))
    checks.append(("priceable candidate count", candidate_models["priceable_count"] == 141))
    checks.append(("unpriceable candidate count", candidate_models["not_priceable_count"] == 1))
    recovery_by_ticker = {row["ticker"]: row for row in recovery_packet["rows"]}
    checks.append(("valuation recovery packet coverage", len(recovery_by_ticker) == 12 and {"601360", "000042"}.issubset(recovery_by_ticker)))
    checks.append(
        (
            "000042 recovery arithmetic",
            all(
                abs(
                    recovery_by_ticker["000042"]["alternative_method"]["normalized_eps_2026"][scenario]
                    * recovery_by_ticker["000042"]["alternative_method"]["multiples"][scenario]
                    - recovery_by_ticker["000042"]["alternative_method"]["fair_value"][scenario]
                )
                < 0.001
                for scenario in ("bear", "base", "bull")
            ),
        )
    )
    checks.append(
        (
            "all recovery rows have conditional ranges",
            all(
                row.get("alternative_method", {}).get("fair_value", {}).get("bear") is not None
                and row.get("alternative_method", {}).get("fair_value", {}).get("base") is not None
                and row.get("alternative_method", {}).get("fair_value", {}).get("bull") is not None
                for row in recovery_packet["rows"]
            ),
        )
    )
    checks.append(("all candidate rows have target or explicit boundary", all(
        row.get("probability_target") is not None
        or row.get("target_display") in {"不适用；待上市交易", "暂无正分母，暂不建立目标区间", "恢复估值未覆盖"}
        for row in candidate_models["rows"]
    )))
    checks.append(("priority model coverage", len(priority_models["rows"]) == 39))
    checks.append((
        "priority evidence quality has no medium",
        all(row.get("evidence_quality") != "medium" for row in priority_models["rows"]),
    ))
    checks.append((
        "root candidate valuation mirror has no medium",
        len(root_candidate_models.get("rows", [])) == len(candidate_models["rows"])
        and all(row.get("evidence_quality") != "medium" for row in root_candidate_models["rows"]),
    ))
    checks.append((
        "root priority valuation mirror has no medium",
        len(root_priority_models.get("rows", [])) == len(priority_models["rows"])
        and all(row.get("evidence_quality") != "medium" for row in root_priority_models["rows"]),
    ))
    checks.append(("formal selection bridge coverage", selection_bridge["priority_count"] == 39 and len(selection_bridge["rows"]) == 39))
    checks.append(("formal selection bridge has conditional rows", selection_bridge["status_counts"].get("conditional_high_upside_watch", 0) > 0))
    checks.append(("formal selection bridge has downside/watch rows", selection_bridge["status_counts"].get("valuation_risk_or_watch", 0) > 0))
    closure_rows = high_upside_closure["rows"]
    checks.append((
        "high-upside evidence closure coverage",
        high_upside_audit["row_count"] == 6
        and high_upside_closure["row_count"] == 6
        and high_upside_closure["closure_count"] == 6
        and len(closure_rows) == 6
        and {row["ticker"] for row in closure_rows}
        == {row["ticker"] for row in high_upside_audit["rows"]}
        and (CASE_DIR / "data" / "high_upside_evidence_closure_20260716.json").exists()
        and (CASE_DIR / "data" / "high_upside_evidence_closure_20260716.md").exists()
        and (CASE_DIR / "sources" / "high-upside-evidence-20260716" / "index.md").exists(),
    ))
    checks.append((
        "high-upside evidence closure priority split",
        high_upside_audit["priority_count"] == 3
        and high_upside_audit["not_priority_count"] == 3
        and high_upside_closure["priority_retained_count"] == 3
        and high_upside_closure["candidate_only_count"] == 3,
    ))
    checks.append((
        "high-upside evidence closure formal boundary",
        high_upside_audit["formal_count"] == 0
        and high_upside_closure["formal_upgrade_count"] == 0
        and high_upside_closure["current_positive_anchor_count"] == 0
        and all(not row["in_formal_pool"] for row in closure_rows)
        and all(
            float(row["accepted_external_anchor"]["valuation_weight"]) == 0.0
            for row in closure_rows
        )
        and next(
            row for row in candidate_models["rows"] if row["ticker"] == "600739"
        )["external_weight"] == 0.0,
    ))
    checks.append((
        "high-upside evidence closure fields",
        all(
            row.get("metadata_report_count", 0) > 0
            and row.get("archived_original_pdf_count", 0) > 0
            and row.get("current_original_target_count") == 0
            and row.get("current_target_proof")
            and len(row.get("closed_gaps") or []) == 4
            and row.get("remaining_event_validation")
            and row.get("final_admission_decision")
            and row.get("direct_evidence_paths")
            and all((CASE_DIR / path).exists() for path in row["direct_evidence_paths"])
            for row in closure_rows
        ),
    ))
    checks.append((
        "former medium admission coverage",
        former_medium_admission["row_count"] == 48
        and len(former_medium_admission["rows"]) == 48
        and all(row.get("legacy_evidence_quality") == "medium" for row in former_medium_admission["rows"]),
    ))
    checks.append((
        "former medium admission has no formal rows",
        former_medium_admission["status_counts"].get("formal_model_candidate", 0) == 0,
    ))
    checks.append((
        "former medium admission decisions complete",
        all(row.get("admission_decision") and row.get("admission_label") for row in former_medium_admission["rows"]),
    ))
    checks.append(("formal model count", len(formal["rows"]) == selection_bridge["formal_count"] == 4))
    checks.append(("daily industry flow coverage", capital_manifest["daily_coverage"] == "31/31"))
    checks.append(("weekly industry flow coverage", capital_manifest["weekly_coverage"] == "31/31"))
    checks.append(("sector scan count", sector_scan["universe_count"] == 31))
    checks.append(("sector scan current observation", sector_scan["flow_observation_date"] == "2026-07-14"))
    checks.append(("continuous flow partial boundary", continuous["coverage_count"] == 30 and continuous["coverage_expected"] == 112 and continuous["parse_status"] == "partial"))
    checks.append(("formal ticker set", {row["ticker"] for row in formal["rows"]} == {"000155", "000703", "002379", "300014"}))
    checks.append(("formal external anchors", all(row.get("external_target") is not None for row in formal["rows"]))
    )
    checks.append(("formal downside", all(row["bear"] < row["current_price"] for row in formal["rows"])))
    checks.append(
        (
            "formal probability arithmetic",
            all(
                abs(
                    round(row["bear"] * 0.30 + row["base"] * 0.50 + row["bull"] * 0.20, 2)
                    - row["house_probability_value"]
                )
                < 0.02
                for row in formal["rows"]
            ),
        )
    )
    checks.append(
        (
            "formal upside arithmetic",
            all(
                abs(row["probability_target"] / row["current_price"] - 1 - row["upside"]) < 0.002
                for row in formal["rows"]
            ),
        )
    )
    checks.append(
        (
            "formal probability weights",
            all(
                row.get("probability_weights")
                == {"bear": 0.3, "base": 0.5, "bull": 0.2}
                for row in formal["rows"]
            ),
        )
    )
    checks.append(
        (
            "formal final-target weights",
            all(
                abs(
                    row["final_target"]
                    - (
                        row["house_probability_value"]
                        * row["final_target_weights"]["house_probability_value"]
                        + row["external_target"]
                        * row["final_target_weights"]["external_target"]
                    )
                )
                < 0.02
                for row in formal["rows"]
            ),
        )
    )
    for rel in (
        "main.tex",
        "main.pdf",
        "main_current_text.txt",
        "analysis/house_view.md",
        "analysis/variant_perception.md",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/growth_earnings_model.md",
        "analysis/segment_forecast_bridge.md",
        "analysis/implied_growth_sensitivity.md",
        "analysis/risk_framework.md",
        "analysis/secondary_market_analysis.md",
        "analysis/narrative_blueprint.md",
        "analysis/exhibit_plan.md",
        "refresh-20260715/refresh_manifest.json",
        "refresh-20260715/data/full_market_candidate_valuation_audit_20260715.json",
        "refresh-20260715/data/full_market_candidate_valuation_audit_20260715.md",
        "refresh-20260715/data/high_upside_selection_audit_20260715.json",
        "refresh-20260715/data/high_upside_selection_audit_20260715.md",
        "refresh-20260715/data/former_medium_candidate_admission_20260715.json",
        "refresh-20260715/data/former_medium_candidate_admission_20260715.md",
    ):
        checks.append((f"exists {rel}", (CASE_DIR / rel).exists()))
    checks.append(("exists formal selection bridge", (DATA_DIR / "formal_selection_bridge_20260715.json").exists()))
    report_text = (CASE_DIR / "main_current_text.txt").read_text(errors="ignore")
    compact_report_text_for_tokens = re.sub(r"\s+", "", report_text)
    for token in (
        "1,680",
        "142",
        "39",
        "141",
        "137/142",
        "1",
        "13.10",
        "8.54",
        "恒逸石化",
        "宏桥控股",
        "川能动力",
        "三六零",
        "中洲控股",
        "赣锋锂业",
        "德明利",
        "天华新能",
        "恩捷股份",
        "盛新锂能",
        "苏州高新",
        "渤海租赁",
        "投资结论与行动框架",
        "三层行动框架",
        "为什么没有按100%以上空间直接入选",
        "100%以上空间样本的拦截链条",
        "高空间样本的已核验证据与准入结论",
        "100%以上空间样本的全量拦截审计",
        "原中等证据标的补证后的候选准入结论",
        "准入结论",
        "重点事件验证清单",
        "市场状态与机会架构",
        "估值框架与情景分析",
        "情景权重与目标价治理",
        "外部锚与本机构区间的边界",
        "焦点标的与验证路径",
        "正式模型横向比较",
        "恢复性估值",
        "风险、催化与监控",
        "研究基础与数据边界",
        "来源与复现说明",
        "全量候选清单与操作分层",
        "全量估值推演与证据账本",
        "优先池的证据升级路径",
        "适用理由",
        "分母与公式代入",
        "情景与概率值",
        "证据与验证",
        "本机构情景",
        "熊/基准/牛",
        "31/31",
        "30/112",
    ):
        token_compact = re.sub(r"\s+", "", token)
        checks.append((
            f"report contains {token}",
            token in report_text or token_compact in compact_report_text_for_tokens,
        ))
    checks.append((
        "report avoids high-upside raw status labels",
        all(
            token not in report_text
            for token in (
                "earnings_validation_watch",
                "launched_with_runway_candidate",
                "low_position_earnings_priority",
                "quiet_accumulation_priority",
            )
        ),
    ))
    checks.append(("no unfinished markers", not re.search(r"\b(?:TODO|TBD|PLACEHOLDER)\b", report_text)))
    checks.append(("report cover does not show stale 138/142 PDF coverage", "138/142" not in report_text))
    checks.append(("no visual target-price blanks", "目标价字段为—" not in report_text and "目标价字段为---" not in report_text))
    checks.append(("no unitless undisclosed EPS blanks", "未披露元" not in report_text))
    compact_report_text = re.sub(r"\s+", "", report_text)
    checks.append(
        (
            "listing boundary is explicit",
            all(
                token in compact_report_text
                for token in ("长鑫科技", "发行价8.66元", "尚未上市", "不适用")
            ),
        )
    )
    checks.append(
        (
            "reader-facing report avoids internal English work labels",
            all(
                token not in report_text
                for token in ("House", "Street", "Exhibit", "candidate_valuation_audit")
            ),
        )
    )

    with tempfile.TemporaryDirectory(prefix="astock-refresh-latex-") as temp:
        command = [
            "/Library/TeX/texbin/xelatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={temp}",
            "main.tex",
        ]
        outputs = []
        return_codes = []
        for _ in range(2):
            completed = subprocess.run(command, cwd=CASE_DIR, text=True, capture_output=True, check=False)
            outputs.append(completed.stdout + completed.stderr)
            return_codes.append(completed.returncode)
        diagnostics = "\n".join(outputs)
        temp_pdf = Path(temp) / "main.pdf"
        if temp_pdf.exists():
            pdfinfo = subprocess.run(
                ["pdfinfo", str(temp_pdf)],
                text=True,
                capture_output=True,
                check=False,
            )
        else:
            pdfinfo = subprocess.CompletedProcess(args=["pdfinfo"], returncode=1, stdout="", stderr="missing temp pdf")
        checks[-1] = (
            "two-pass XeLaTeX",
            all(code == 0 for code in return_codes)
            and "Overfull" not in diagnostics
            and "Undefined control sequence" not in diagnostics
            and "Missing character" not in diagnostics
            and "LaTeX Error" not in diagnostics
            and "Extra alignment tab" not in diagnostics
            and pdfinfo.returncode == 0
            and not pdfinfo.stderr.strip(),
        )

    failures = [name for name, passed in checks if not passed]
    for name, passed in checks:
        print(("PASS " if passed else "FAIL ") + name)
    print(f"SUMMARY {len(checks) - len(failures)} PASS / {len(failures)} FAIL")
    print("RESULT PASS" if not failures else "RESULT FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
