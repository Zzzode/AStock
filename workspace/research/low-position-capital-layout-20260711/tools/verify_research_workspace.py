#!/usr/bin/env python3
"""Verify the low-position capital-layout research case with 39 hard checks."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable


CASE_DIR = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> Any:
    return json.loads((CASE_DIR / relative_path).read_text())


def read_text(relative_path: str) -> str:
    return (CASE_DIR / relative_path).read_text(errors="ignore")


def pdf_pages() -> int:
    result = subprocess.run(
        ["pdfinfo", str(CASE_DIR / "main.pdf")],
        text=True,
        capture_output=True,
        check=True,
    )
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else 0


def pdf_title() -> str:
    result = subprocess.run(
        ["pdfinfo", str(CASE_DIR / "main.pdf")],
        text=True,
        capture_output=True,
        check=True,
    )
    match = re.search(r"^Title:\s+(.+)$", result.stdout, re.MULTILINE)
    return match.group(1).strip() if match else ""


def pdf_out_of_bounds_count() -> int:
    bbox_path = CASE_DIR / "rendered" / "bbox-layout.xml"
    subprocess.run(
        [
            "pdftotext",
            "-bbox-layout",
            str(CASE_DIR / "main.pdf"),
            str(bbox_path),
        ],
        check=True,
    )
    root = ET.parse(bbox_path).getroot()
    violations = 0
    for page in root.iter():
        if not page.tag.endswith("page"):
            continue
        width = float(page.attrib.get("width", 0))
        height = float(page.attrib.get("height", 0))
        for word in page.iter():
            if not word.tag.endswith("word"):
                continue
            x_min = float(word.attrib.get("xMin", word.attrib.get("xmin", 0)))
            y_min = float(word.attrib.get("yMin", word.attrib.get("ymin", 0)))
            x_max = float(word.attrib.get("xMax", word.attrib.get("xmax", 0)))
            y_max = float(word.attrib.get("yMax", word.attrib.get("ymax", 0)))
            if (
                x_min < -0.5
                or y_min < -0.5
                or x_max > width + 0.5
                or y_max > height + 0.5
            ):
                violations += 1
    return violations


def latex_build_is_clean() -> bool:
    xelatex = shutil.which("xelatex")
    if xelatex is None:
        fallback = Path("/Library/TeX/texbin/xelatex")
        xelatex = str(fallback) if fallback.exists() else None
    if xelatex is None:
        return False
    with tempfile.TemporaryDirectory(prefix="astock-latex-verify-") as temp_dir:
        command = [
            xelatex,
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={temp_dir}",
            "main.tex",
        ]
        for _ in range(2):
            completed = subprocess.run(
                command,
                cwd=CASE_DIR,
                text=True,
                capture_output=True,
                check=False,
            )
            if completed.returncode != 0:
                return False
        log_path = Path(temp_dir) / "main.log"
        if not log_path.exists():
            return False
        log_text = log_path.read_text(errors="ignore")
        return not any(
            token in log_text
            for token in (
                "Overfull",
                "Extra alignment tab",
                "Undefined control sequence",
                "Missing character",
                "LaTeX Error",
            )
        )


def verify_refresh_case() -> int:
    data_dir = CASE_DIR / "refresh-20260715" / "data"

    def refresh_json(name: str) -> Any:
        return json.loads((data_dir / name).read_text())

    screen = refresh_json("full_market_preview_screen_20260715.json")
    candidates = refresh_json("full_market_candidates_20260715.json")
    priority = refresh_json("full_market_priority_pool_20260715.json")
    evidence = refresh_json("full_market_valuation_evidence_20260715.json")
    candidate_models = refresh_json(
        "full_market_candidate_valuation_20260715.json"
    )
    candidate_audit = refresh_json(
        "full_market_candidate_valuation_audit_20260715.json"
    )
    recovery = refresh_json("valuation_recovery_601360_000042_20260715.json")
    priority_models = refresh_json(
        "full_market_priority_valuation_20260715.json"
    )
    selection_bridge = refresh_json("formal_selection_bridge_20260715.json")
    high_upside_audit = refresh_json(
        "high_upside_selection_audit_20260715.json"
    )
    high_upside_closure = refresh_json(
        "high_upside_evidence_closure_20260716.json"
    )
    formal = refresh_json("current_valuation_model_20260715.json")
    source_registry = refresh_json("source_registry_20260715.json")
    claim_audit = refresh_json("claim_audit_20260715.json")
    broker_consensus = load_json("data/broker_street_consensus_20260715.json")
    exhaustion = load_json("source_exhaustion_log.json")
    gate_manifest = load_json("gate_manifest.json")
    artifact_contract = load_json("artifact_contract.json")
    final_signoff = load_json("final_signoff.json")
    workflow_eval = load_json("research_workflow_eval.json")
    report_text = read_text("main_current_text.txt")
    compact_report_text = re.sub(r"\s+", "", report_text)
    high_upside_tickers = {
        "002432",
        "000623",
        "600739",
        "000685",
        "600150",
        "301308",
    }
    closure_rows = high_upside_closure["rows"]

    refresh_completed = subprocess.run(
        [sys.executable, "tools/verify_refresh_workspace.py"],
        cwd=CASE_DIR,
        text=True,
        capture_output=True,
        check=False,
    )
    refresh_output = refresh_completed.stdout + refresh_completed.stderr

    def review_lifecycle_closed() -> bool:
        for cycle in (
            "R0_evidence",
            "R1_model",
            "R2_draft",
            "R3_render_compliance",
            "R4_final_ic",
        ):
            payload = load_json(f"review_findings_{cycle}.json")
            if (
                payload.get("publishability_status") != "PASS"
                or payload.get("open_s_count") != 0
                or payload.get("open_a_count") != 0
            ):
                return False
            if any(
                row.get("status") not in {
                    "closed",
                    "verified",
                    "resolved",
                    "pass",
                }
                for row in payload.get("findings", [])
            ):
                return False
            if cycle != "R4_final_ic":
                if not (
                    (CASE_DIR / f"repair_plan_{cycle}.md").is_file()
                    and (CASE_DIR / f"repair_plan_{cycle}.json").is_file()
                ):
                    return False
        return True

    def formal_arithmetic_reconciles() -> bool:
        for row in formal["rows"]:
            house = round(
                row["bear"] * 0.30
                + row["base"] * 0.50
                + row["bull"] * 0.20,
                2,
            )
            target = round(
                house * (1 - row["external_weight"])
                + row["external_target"] * row["external_weight"],
                2,
            )
            if (
                abs(house - row["house_probability_value"]) >= 0.02
                or abs(target - row["probability_target"]) >= 0.02
                or abs(
                    row["probability_target"] / row["current_price"]
                    - 1
                    - row["upside"]
                )
                >= 0.002
                or not row["bear"] < row["current_price"]
            ):
                return False
        return True

    checks: list[tuple[str, Callable[[], bool]]] = [
        (
            "report deliverables exist",
            lambda: all(
                (CASE_DIR / path).is_file()
                for path in ("main.tex", "main.pdf", "main_current_text.txt")
            ),
        ),
        (
            "PDF metadata and final sign-off reconcile",
            lambda: pdf_title() == "A股盈利修复的再定价机会"
            and pdf_pages() == 53
            and pdf_pages() == final_signoff.get("page_count"),
        ),
        (
            "extracted PDF text is current and substantial",
            lambda: len(report_text) > 20_000
            and (CASE_DIR / "main_current_text.txt").stat().st_mtime
            >= (CASE_DIR / "main.pdf").stat().st_mtime - 2,
        ),
        (
            "deep refresh verifier passes",
            lambda: refresh_completed.returncode == 0
            and "SUMMARY 131 PASS / 0 FAIL" in refresh_output
            and "RESULT PASS" in refresh_output,
        ),
        (
            "official preview universe reconciles",
            lambda: screen["source_preview_row_count"] == 4429
            and screen["eligible_a_share_metric_row_count"] == 4339
            and screen["preview_company_count"] == 1680
            and screen["mapped_company_count"] == 1678,
        ),
        (
            "candidate priority and formal pools reconcile",
            lambda: len(candidates["rows"]) == 142
            and len(priority["rows"]) == 39
            and len(formal["rows"]) == 4,
        ),
        (
            "candidate evidence coverage reconciles",
            lambda: evidence["row_count"] == 142
            and evidence["financial_success_count"] == 142
            and evidence["report_metadata_count"] >= 137
            and evidence["report_pdf_count"] >= 137
            and evidence["target_extract_count"] >= 33,
        ),
        (
            "candidate model coverage and boundaries reconcile",
            lambda: candidate_models["row_count"] == 142
            and candidate_models["priceable_count"] == 141
            and candidate_models["not_priceable_count"] == 1,
        ),
        (
            "candidate model evidence governance is complete",
            lambda: all(
                row.get("evidence_quality") != "medium"
                and row.get("evidence_quality_basis")
                and row.get("broker_anchor_quality") is not None
                for row in candidate_models["rows"]
            ),
        ),
        (
            "candidate row-level valuation audit passes",
            lambda: candidate_audit["row_count"] == 142
            and candidate_audit["pass_count"] == 142
            and candidate_audit["fail_count"] == 0
            and all(
                row.get("audit_status") == "PASS"
                and row.get("formula")
                and row.get("denominator")
                and row.get("evidence_sources")
                for row in candidate_audit["rows"]
            ),
        ),
        (
            "valuation recovery packet is complete",
            lambda: len(recovery["rows"]) == 12
            and len({row["ticker"] for row in recovery["rows"]}) == 12
            and {"601360", "000042"}.issubset(
                {row["ticker"] for row in recovery["rows"]}
            )
            and all(
                all(
                    row.get("alternative_method", {})
                    .get("fair_value", {})
                    .get(scenario)
                    is not None
                    for scenario in ("bear", "base", "bull")
                )
                for row in recovery["rows"]
            ),
        ),
        (
            "priority model and formal-selection bridge reconcile",
            lambda: priority_models["row_count"] == 39
            and selection_bridge["priority_count"] == 39
            and selection_bridge["formal_count"] == 4
            and len(selection_bridge["rows"]) == 39,
        ),
        (
            "high-upside selection audit set and split reconcile",
            lambda: high_upside_audit["row_count"] == 6
            and high_upside_audit["priority_count"] == 3
            and high_upside_audit["not_priority_count"] == 3
            and high_upside_audit["formal_count"] == 0
            and {
                row["ticker"] for row in high_upside_audit["rows"]
            }
            == high_upside_tickers,
        ),
        (
            "Section 4.3 evidence closure covers all six tickers",
            lambda: high_upside_closure["row_count"] == 6
            and high_upside_closure["closure_count"] == 6
            and len(closure_rows) == 6
            and {row["ticker"] for row in closure_rows}
            == high_upside_tickers,
        ),
        (
            "Section 4.3 original corpus and paths are complete",
            lambda: all(
                row["metadata_report_count"] > 0
                and row["archived_original_pdf_count"] > 0
                and row["metadata_report_count"]
                >= row["archived_original_pdf_count"]
                and row.get("current_target_proof")
                and row.get("direct_evidence_paths")
                and all(
                    (CASE_DIR / path).exists()
                    for path in row["direct_evidence_paths"]
                )
                for row in closure_rows
            ),
        ),
        (
            "Section 4.3 external-anchor boundary is enforced",
            lambda: high_upside_closure[
                "current_positive_anchor_count"
            ]
            == 0
            and high_upside_closure["formal_upgrade_count"] == 0
            and all(
                row["current_original_target_count"] == 0
                and row["accepted_external_anchor"]["valuation_weight"]
                == 0.0
                for row in closure_rows
            )
            and next(
                row
                for row in candidate_models["rows"]
                if row["ticker"] == "600739"
            )["external_weight"]
            == 0.0,
        ),
        (
            "Section 4.3 admission and future-event boundaries are complete",
            lambda: high_upside_closure["priority_retained_count"] == 3
            and high_upside_closure["candidate_only_count"] == 3
            and all(
                not row["in_formal_pool"]
                and row.get("final_admission_decision")
                and row.get("remaining_event_validation")
                and len(row.get("closed_gaps") or []) == 4
                for row in closure_rows
            ),
        ),
        (
            "canonical data mirrors match refresh outputs",
            lambda: load_json(
                "data/high_upside_evidence_closure_20260716.json"
            )
            == high_upside_closure
            and load_json(
                "data/full_market_candidate_valuation_20260715.json"
            )
            == candidate_models
            and load_json(
                "data/full_market_priority_valuation_20260715.json"
            )
            == priority_models,
        ),
        (
            "Section 4.3 source artifacts are archived",
            lambda: all(
                (CASE_DIR / path).is_file()
                for path in (
                    "data/high_upside_evidence_closure_20260716.md",
                    "data/high_upside_evidence_closure_20260716.json",
                    "refresh-20260715/data/high_upside_evidence_closure_20260716.md",
                    "refresh-20260715/data/high_upside_evidence_closure_20260716.json",
                    "sources/high-upside-evidence-20260716/index.md",
                )
            ),
        ),
        (
            "source registry includes the Section 4.3 closure",
            lambda: len(source_registry["sources"]) == 7
            and any(
                row.get("source_id") == "R07"
                and "six of six gaps closed" in row.get("boundary", "")
                for row in source_registry["sources"]
            ),
        ),
        (
            "claim audit records verified closure and downgrade",
            lambda: any(
                row.get("claim_id") == "RC07"
                and row.get("status")
                == "verified_closed_with_downgrade"
                and set(row.get("high_upside_tickers") or [])
                == high_upside_tickers
                and row.get("formal_count") == 0
                for row in claim_audit["claims"]
            ),
        ),
        (
            "source exhaustion records ticker-level Section 4.3 outcomes",
            lambda: any(
                row.get("probe")
                == "Section 4.3 six-ticker high-upside evidence closure"
                and row.get("result")
                == "closed_with_zero_formal_upgrades"
                and set(row.get("tickers") or []) == high_upside_tickers
                and len(row.get("ticker_results") or []) == 6
                for row in exhaustion["entries"]
            ),
        ),
        (
            "gate manifest requires the Section 4.3 closure",
            lambda: {
                "refresh-20260715/data/high_upside_evidence_closure_20260716.json",
                "refresh-20260715/data/high_upside_evidence_closure_20260716.md",
                "sources/high-upside-evidence-20260716/index.md",
            }.issubset(set(gate_manifest["required_artifacts"]))
            and any(
                "all 6 100%+ upside rows have ticker-level evidence closure"
                in condition
                for condition in gate_manifest["pass_conditions"]
            ),
        ),
        (
            "artifact contract blocks shallow Section 4.3 closure",
            lambda: any(
                row.get("artifact")
                == "refresh-20260715/data/high_upside_evidence_closure_20260716.json"
                and row.get("blocking_if_missing") is True
                and "current target-field proof"
                in row.get("required_fields", [])
                and "future H2 event presented as completed evidence"
                in row.get("blocking_conditions", [])
                for row in artifact_contract["artifacts"]
            ),
        ),
        (
            "delta audit records root cause repair and prevention",
            lambda: all(
                token in read_text("analysis/delta_audit.md")
                for token in (
                    "Section 4.3",
                    "three auditable states",
                    "zero valuation weight",
                    "indvAimPriceL/T",
                )
            ),
        ),
        (
            "raw Eastmoney metadata preserves target fields",
            lambda: all(
                (
                    lambda packet: packet.get("ticker") == ticker
                    and len(packet.get("data") or [])
                    == next(
                        row["metadata_report_count"]
                        for row in closure_rows
                        if row["ticker"] == ticker
                    )
                    and "/report/list" in packet.get("request_url", "")
                    and all(
                        "indvAimPriceL" in item
                        and "indvAimPriceT" in item
                        for item in packet["data"]
                    )
                )(
                    load_json(
                        "sources/high-upside-evidence-20260716/"
                        f"eastmoney-report-metadata/{ticker}_report_list.json"
                    )
                )
                for ticker in high_upside_tickers
            ),
        ),
        (
            "weak public probes remain zero-weight",
            lambda: sum(len(row.get("cross_checks") or []) for row in closure_rows)
            == 3
            and all(
                check.get("valuation_weight") == 0.0
                and (
                    "media_repost" in check.get("source_class", "")
                    or "failed" in check.get("source_class", "")
                )
                and (CASE_DIR / check["source_path"]).is_file()
                for row in closure_rows
                for check in row.get("cross_checks") or []
            ),
        ),
        (
            "formal valuation universe and anchors are exact",
            lambda: {
                row["ticker"] for row in formal["rows"]
            }
            == {"000155", "000703", "002379", "300014"}
            and all(
                row.get("external_target") is not None
                and row.get("external_weight", 0) > 0
                and row.get("formal_anchor_eligible") is True
                and row.get("external_source")
                and (CASE_DIR / row["external_source"]).is_file()
                for row in formal["rows"]
            ),
        ),
        (
            "formal valuation arithmetic reconciles",
            formal_arithmetic_reconciles,
        ),
        (
            "broker consensus covers the formal universe with auditable anchors",
            lambda: {
                row["ticker"] for row in broker_consensus["rows"]
            }
            == {row["ticker"] for row in formal["rows"]}
            and all(
                row["source_quality"] == "original_pdf"
                and row["valuation_weight"] > 0
                and row["target_price"] != "not disclosed"
                and (CASE_DIR / row["source_path"]).is_file()
                for row in broker_consensus["rows"]
            ),
        ),
        (
            "valuation audit is reproducible",
            lambda: "Model Reproducibility: PASS"
            in read_text("analysis/valuation_audit.md")
            and all(
                (CASE_DIR / path).is_file()
                for path in (
                    "analysis/valuation_model.md",
                    "analysis/valuation_audit.md",
                    "data/current_valuation_model_compat_20260715.json",
                )
            ),
        ),
        (
            "growth risk and secondary-market artifacts are complete",
            lambda: all(
                (CASE_DIR / path).is_file()
                and (CASE_DIR / path).stat().st_size > 200
                for path in (
                    "analysis/growth_earnings_model.md",
                    "analysis/segment_forecast_bridge.md",
                    "analysis/implied_growth_sensitivity.md",
                    "analysis/risk_framework.md",
                    "analysis/secondary_market_analysis.md",
                    "data/growth_driver_model.json",
                )
            ),
        ),
        (
            "review lifecycle is closed",
            review_lifecycle_closed,
        ),
        (
            "final sign-off reconciles closure PDF and downgrade",
            lambda: final_signoff["signoff_status"] == "PASS"
            and final_signoff["publishability_score"] >= 90
            and final_signoff["open_s_count"] == 0
            and final_signoff["open_a_count"] == 0
            and final_signoff["verifier_results"][
                "high_upside_evidence_closure"
            ]
            == "6/6"
            and final_signoff["verifier_results"][
                "high_upside_current_positive_anchor_count"
            ]
            == 0
            and "House-only high-space priority models remain validation candidates"
            in final_signoff["downgrade_status"],
        ),
        (
            "workflow evaluation is publishable",
            lambda: workflow_eval.get("success") is True
            and workflow_eval.get("quality", {}).get("publishable") is True
            and workflow_eval.get("quality", {}).get(
                "blocking_failure_count"
            )
            == 0
            and workflow_eval.get("quality", {}).get("score", 0) >= 90,
        ),
        (
            "reader-facing Section 4.3 contains the verified conclusions",
            lambda: all(
                token in compact_report_text
                for token in (
                    "高空间样本的已核验证据与准入结论",
                    "闭环率为6/6",
                    "当前正权原始目标为0只",
                    "九安医疗70.28元",
                    "吉林敖东约18.02元",
                    "辽宁成大22.79元",
                    "中山公用10.50–11.11元",
                    "中国船舶31.36元",
                    "江波龙在原始API及已归档PDF语料中未找到目标价",
                )
            ),
        ),
        (
            "reader-facing report has no stale evidence placeholders",
            lambda: not any(
                token in report_text
                for token in (
                    "升级所需证据",
                    "高空间样本的升级证据",
                    "补齐目标价/价值区间",
                    "TODO",
                    "TBD",
                    "PLACEHOLDER",
                )
            ),
        ),
        (
            "PDF text stays inside page bounds",
            lambda: pdf_out_of_bounds_count() == 0,
        ),
        (
            "governance Markdown and JSON pairs are present and parseable",
            lambda: all(
                (CASE_DIR / f"{stem}.md").is_file()
                and (CASE_DIR / f"{stem}.json").is_file()
                for stem in (
                    "gate_manifest",
                    "artifact_contract",
                    "final_signoff",
                    "research_workflow_eval",
                    "source_exhaustion_log",
                )
            )
            and all(
                (CASE_DIR / f"data/{stem}.md").is_file()
                and (CASE_DIR / f"data/{stem}.json").is_file()
                for stem in (
                    "high_upside_evidence_closure_20260716",
                    "source_registry_20260715",
                    "claim_audit_20260715",
                    "broker_street_consensus_20260715",
                )
            ),
        ),
    ]
    if len(checks) != 39:
        raise RuntimeError(
            f"refresh case verifier must contain 39 checks, found {len(checks)}"
        )

    failures: list[str] = []
    for name, predicate in checks:
        try:
            passed = bool(predicate())
        except Exception as exc:
            passed = False
            name = f"{name}: {exc}"
        if passed:
            print(f"PASS {name}")
        else:
            print(f"FAIL {name}")
            failures.append(name)
    if failures and refresh_output:
        print("REFRESH VERIFIER TAIL")
        print("\n".join(refresh_output.splitlines()[-20:]))
    print(f"SUMMARY {len(checks) - len(failures)} PASS / {len(failures)} FAIL")
    print("RESULT PASS" if not failures else "RESULT FAIL")
    return 0 if not failures else 1


def main() -> int:
    refresh_verifier = CASE_DIR / "tools" / "verify_refresh_workspace.py"
    refresh_manifest = CASE_DIR / "refresh-20260715" / "refresh_manifest.json"
    if refresh_manifest.exists() and refresh_verifier.exists():
        return verify_refresh_case()

    sector = load_json("data/sector_scan_20260710.json")
    daily = load_json("data/raw_daily_tables_20260710.json")
    weekly = load_json("data/raw_weekly_tables_20260710.json")
    continuous = load_json("data/continuous_inflow_candidates_20260710.json")
    raw_preview = load_json("data/raw_a_share_h1_2026_preview_20260711.json")
    full_screen = load_json("data/full_market_preview_screen_20260712.json")
    candidates = load_json("data/full_market_preview_candidates_20260712.json")
    omission_audit = load_json("data/prior_universe_omission_audit_20260712.json")
    priority_pool = load_json("data/full_market_priority_pool_20260712.json")
    priority_evidence = load_json("data/full_market_priority_evidence_20260712.json")
    valuation_evidence = load_json("data/full_market_valuation_evidence_20260712.json")
    priority_valuation = load_json("data/full_market_priority_valuation_20260712.json")
    candidate_valuation = load_json("data/full_market_candidate_valuation_20260712.json")
    report_wide_valuation = load_json("data/report_wide_valuation_ledger_20260712.json")
    theme_only_evidence = load_json("data/theme_only_evidence_20260713.json")
    evidence_closure = load_json("data/report_wide_evidence_closure_20260713.json")
    evidence_boundaries = load_json("data/evidence_gap_inventory_20260713.json")
    valuation = load_json("data/current_valuation_model_20260711.json")
    broker = load_json("data/broker_street_consensus_20260711.json")
    conditional = load_json("data/conditional_watch_models_20260712.json")
    growth = load_json("data/growth_driver_model.json")
    hengrui_sotp = load_json("data/hengrui_sotp_model_20260712.json")
    company_cards = load_json("data/company_cards_20260711.json")
    preview_quality = load_json("data/earnings_preview_quality_20260711.json")
    preview_archive = load_json("data/earnings_preview_archive_20260711.json")
    preview_update = load_json("data/earnings_preview_update_20260715.json")
    broker_catalog = load_json("data/core_broker_report_catalog_20260711.json")
    broker_digests = load_json("data/core_broker_report_digests_20260711.json")
    source_registry = load_json("data/source_registry.json")
    claim_audit = load_json("data/claim_audit.json")
    exhaustion = load_json("source_exhaustion_log.json")
    final_signoff = (
        load_json("final_signoff.json")
        if (CASE_DIR / "final_signoff.json").exists()
        else {}
    )
    main_text = read_text("main_current_text.txt")
    sector_rows = sector["rows"]
    candidate_rows = candidates["rows"]
    priority_rows = priority_pool["rows"]
    valuation_rows = valuation["rows"]
    broker_rows = broker["rows"]
    conditional_rows = conditional["rows"]
    compact_text = re.sub(r"\s+", "", main_text)

    expected_valuation_tickers = {
        "601077",
        "000425",
        "601825",
        "600276",
        "601138",
    }
    expected_conditional_tickers = {"000063", "301308", "601225"}
    expected_dispositions = {
        "quiet_accumulation_priority": 1,
        "low_position_earnings_priority": 11,
        "launched_with_runway_candidate": 4,
        "earnings_validation_watch": 41,
        "earnings_delivered_price_advanced": 12,
        "watch_insufficient_price_history": 1,
        "earnings_decline_watch": 1,
        "exclude_nonrecurring_dominated": 2,
    }

    def disposition_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for row in rows:
            disposition = row["full_market_disposition"]
            counts[disposition] = counts.get(disposition, 0) + 1
        return counts

    def original_broker_sources_valid() -> bool:
        if {row["ticker"] for row in broker_rows} != expected_valuation_tickers:
            return False
        for row in broker_rows:
            source_path = CASE_DIR / row["source_path"]
            if (
                row["source_quality"] != "original_pdf"
                or row["valuation_weight"] <= 0
                or not source_path.is_file()
                or not source_path.read_bytes().startswith(b"%PDF")
            ):
                return False
        return True

    def hengrui_sotp_reconciles() -> bool:
        for scenario in hengrui_sotp["scenarios"].values():
            component_sum = sum(
                value
                for key, value in scenario.items()
                if key not in {"equity_value_100mn", "per_share_value"}
            )
            if abs(component_sum - scenario["equity_value_100mn"]) > 0.01:
                return False
            if (
                abs(
                    component_sum / hengrui_sotp["shares_100mn"]
                    - scenario["per_share_value"]
                )
                > 0.01
            ):
                return False
        return True

    def review_and_signoff_closed() -> bool:
        cycles = (
            "R0_evidence",
            "R1_model",
            "R2_draft",
            "R3_render_compliance",
            "R4_final_ic",
        )
        for cycle in cycles:
            payload = load_json(f"review_findings_{cycle}.json")
            if payload.get("publishability_status") != "PASS":
                return False
            if payload.get("open_s_count") != 0 or payload.get("open_a_count") != 0:
                return False
            if any(
                finding.get("status") not in {"closed", "verified", "resolved", "pass"}
                for finding in payload.get("findings", [])
            ):
                return False
        return (
            final_signoff.get("signoff_status") == "PASS"
            and final_signoff.get("publishability_score", 0) >= 90
            and final_signoff.get("open_s_count") == 0
            and final_signoff.get("open_a_count") == 0
        )

    def unique_exhibits() -> bool:
        active_source = read_text("main.tex") + "\n" + "\n".join(
            path.read_text(errors="ignore")
            for path in sorted((CASE_DIR / "sections").glob("final_*.tex"))
        )
        identifiers = re.findall(r"Exhibit\s+([A-Z]?\d+)", active_source)
        return len(identifiers) == 17 and len(set(identifiers)) == 17

    def expanded_valuation_reconciles() -> bool:
        if (
            priority_valuation["row_count"] != 16
            or candidate_valuation["row_count"] != 73
            or candidate_valuation["priceable_count"] != 72
            or candidate_valuation["not_priceable_count"] != 1
            or report_wide_valuation["row_count"] != 117
            or report_wide_valuation["priceable_count"] != 116
            or report_wide_valuation["not_priceable_count"] != 1
            or not evidence_closure_reconciles()
        ):
            return False
        for row in priority_valuation["rows"]:
            expected = round(
                row["bear"] * row["probabilities"]["bear"]
                + row["base"] * row["probabilities"]["base"]
                + row["bull"] * row["probabilities"]["bull"],
                2,
            )
            target = round(
                expected * (1 - row["external_weight"])
                + (row["external_target"] or expected) * row["external_weight"],
                2,
            )
            if (
                not row["bear"] < row["current_price"]
                or abs(target - row["probability_target"]) > 0.001
                or abs(
                    round(
                        row["probability_target"] / row["current_price"] - 1,
                        4,
                    )
                    - row["upside"]
                )
                > 0.0001
                or not row.get("catalyst")
                or not row.get("invalidation")
            ):
                return False
        for payload in (candidate_valuation, report_wide_valuation):
            if len({row["ticker"] for row in payload["rows"]}) != payload["row_count"]:
                return False
            for row in payload["rows"]:
                if row.get("probability_target") is None:
                    if not row.get("evidence_gap"):
                        return False
                elif not (
                    row["target_low"] < row["current_price"]
                    and row["target_low"]
                    <= row["probability_target"]
                    <= row["target_high"]
                ):
                    return False
        return True

    def evidence_closure_reconciles() -> bool:
        rows = evidence_closure["rows"]
        if (
            evidence_closure["row_count"] != 117
            or evidence_closure["closed_count"] != 114
            or evidence_closure["downgraded_count"] != 2
            or evidence_closure["formal_boundary_count"] != 1
            or evidence_closure["unresolved_material_gap_count"] != 0
            or evidence_boundaries["open_gap_count"] != 0
            or evidence_boundaries["row_count"] != 3
            or len({row["ticker"] for row in rows}) != 117
        ):
            return False
        for row in rows:
            if not (
                row.get("direct_evidence")
                and row.get("proxy_evidence")
                and row.get("checked_sources")
                and row.get("source_paths")
                and row.get("valuation_consequence")
                and row.get("closure_status")
            ):
                return False
            if (
                row["closure_status"] != "closed"
                and not row.get("formal_boundary")
            ):
                return False
        boundary_tickers = {
            row["ticker"]
            for row in rows
            if row["closure_status"] != "closed"
        }
        return boundary_tickers == {"000063", "301308", "688825"}

    checks: list[tuple[str, Callable[[], bool]]] = [
        (
            "main.tex and main.pdf exist",
            lambda: (CASE_DIR / "main.tex").is_file()
            and (CASE_DIR / "main.pdf").is_file(),
        ),
        (
            "PDF page count matches final sign-off",
            lambda: pdf_pages() == final_signoff.get("page_count"),
        ),
        (
            "PDF title is correct",
            lambda: pdf_title() == "A股全市场双机会曲线研究",
        ),
        (
            "extracted PDF text exists",
            lambda: len(main_text) > 20_000,
        ),
        (
            "sector universe has 31 unique names",
            lambda: sector["universe_count"] == 31
            and len(sector_rows) == 31
            and len({row["industry"] for row in sector_rows}) == 31,
        ),
        (
            "daily industry table covers 31 rows",
            lambda: sum(
                1
                for row in daily[0]["rows"]
                for offset in (0, 3)
                if len(row) >= offset + 3 and row[offset] != "-"
            )
            == 31,
        ),
        (
            "weekly industry table covers 31 rows",
            lambda: sum(
                1
                for row in weekly[-1]["rows"]
                for offset in (0, 3)
                if len(row) >= offset + 3 and row[offset] != "-"
            )
            == 31,
        ),
        (
            "continuous-inflow table has 30 rows",
            lambda: continuous["row_count"] == 30,
        ),
        (
            "raw preview and A-share scope audit reconcile",
            lambda: raw_preview["row_count"] == 949
            and len(raw_preview["rows"]) == 949
            and full_screen["eligible_a_share_metric_row_count"] == 937
            and full_screen["scope_excluded_metric_row_count"] == 12
            and full_screen["scope_excluded_security_count"] == 4
            and full_screen["scope_excluded_tickers"]
            == ["200029", "200468", "200725", "200992"],
        ),
        (
            "full-market preview mother universe is complete",
            lambda: full_screen["preview_company_count"] == 364
            and full_screen["mapped_company_count"] == 364
            and all(
                not row["ticker"].startswith(("200", "900"))
                for row in full_screen["rows"]
            ),
        ),
        (
            "full-market industry summary covers 31 rows",
            lambda: len(full_screen["industry_summary"]) == 31
            and {row["industry"] for row in full_screen["industry_summary"]}
            == {row["industry"] for row in sector_rows},
        ),
        (
            "high-impact screen has 73 unique A-share candidates",
            lambda: full_screen["high_impact_candidate_count"] == 73
            and candidates["row_count"] == 73
            and len(candidate_rows) == 73
            and len({row["ticker"] for row in candidate_rows}) == 73
            and all(
                not row["ticker"].startswith(("200", "900"))
                for row in candidate_rows
            ),
        ),
        (
            "candidate dispositions are complete and exact",
            lambda: disposition_counts(candidate_rows) == expected_dispositions,
        ),
        (
            "priority pool count, composition and eligibility are exact",
            lambda: priority_pool["row_count"] == 16
            and len(priority_rows) == 16
            and disposition_counts(priority_rows)
            == {
                "quiet_accumulation_priority": 1,
                "low_position_earnings_priority": 11,
                "launched_with_runway_candidate": 4,
            }
            and all(
                row["parent_np_yoy_midpoint_pct"] > 0
                and row["history_status"] == "full_year"
                for row in priority_rows
            ),
        ),
        (
            "priority evidence package is complete",
            lambda: priority_evidence["row_count"] == 16
            and priority_evidence["financial_success_count"] == 16
            and priority_evidence["report_pdf_count"] == 15
            and priority_evidence["failures"]
            == [
                {
                    "ticker": "600120",
                    "company": "浙江东方",
                    "stage": "metadata",
                    "error": "KeyError('infoCode')",
                }
            ],
        ),
        (
            "full-market valuation evidence is complete",
            lambda: valuation_evidence["row_count"] == 73
            and valuation_evidence["financial_success_count"] == 73
            and valuation_evidence["report_metadata_count"] == 71
            and valuation_evidence["report_pdf_count"] == 71
            and theme_only_evidence["row_count"] == 44
            and theme_only_evidence["financial_success_count"] == 44
            and theme_only_evidence["report_covered_count"] == 44
            and theme_only_evidence["valid_original_pdf_count"] == 44
            and theme_only_evidence["usable_eps_count"] == 42
            and theme_only_evidence["open_failure_count"] == 0,
        ),
        (
            "prior thematic-universe omission audit is complete",
            lambda: omission_audit["omitted_high_impact_count"] == 63
            and len(omission_audit["rows"]) == 63,
        ),
        (
            "official EPS and deducted-profit preview quality is present",
            lambda: all(
                row.get("h1_eps_source")
                and row.get("h1_deducted_profit_midpoint_100mn") is not None
                and row.get("q2_implied_net_profit_100mn") is not None
                and row.get("quality_class")
                for row in preview_quality["rows"]
            ),
        ),
        (
            "incremental 2026-07-15 preview archive is complete",
            lambda: preview_update["data_cutoff"] == "2026-07-15"
            and preview_update["archived_count"] == 9
            and preview_update["failure_count"] == 0
            and len(preview_update["rows"]) == 9
            and len({row["ticker"] for row in preview_update["rows"]}) == 9
            and all(
                row.get("local_pdf")
                and (CASE_DIR / row["local_pdf"]).is_file()
                and (CASE_DIR / row["local_pdf"]).read_bytes().startswith(b"%PDF")
                and row.get("local_text")
                and row.get("h1_parent_np_midpoint_100mn") is not None
                and row.get("h1_deducted_np_midpoint_100mn") is not None
                and row.get("q2_implied_net_profit_100mn") is not None
                and row.get("quality_class")
                and row.get("disposition")
                for row in preview_update["rows"]
            ),
        ),
        (
            "legacy company cards reflect five formal and two conditional names",
            lambda: company_cards["row_count"] == 54
            and sum(
                row["valuation_disposition"] == "current_price_core_model"
                for row in company_cards["rows"]
            )
            == 5
            and sum(
                row["valuation_disposition"].startswith("conditional_watch")
                for row in company_cards["rows"]
            )
            == 2,
        ),
        (
            "formal valuation universe is exact",
            lambda: len(valuation_rows) == 5
            and {row["ticker"] for row in valuation_rows}
            == expected_valuation_tickers,
        ),
        (
            "formal valuation market caps reconcile",
            lambda: all(
                abs(
                    row["market_cap_100mn_cny"]
                    - row["current_price"] * row["shares_100mn"]
                )
                < 0.02
                for row in valuation_rows
            ),
        ),
        (
            "formal scenario bands include genuine downside",
            lambda: all(
                row["bear"] < row["current_price"] < row["bull"]
                and row["bear"] < row["base"] < row["bull"]
                for row in valuation_rows
            ),
        ),
        (
            "formal scenario probabilities and expected values reconcile",
            lambda: all(
                abs(
                    row["bear_probability"]
                    + row["base_probability"]
                    + row["bull_probability"]
                    - 1
                )
                < 1e-9
                and abs(
                    round(
                        row["bear"] * row["bear_probability"]
                        + row["base"] * row["base_probability"]
                        + row["bull"] * row["bull_probability"],
                        2,
                    )
                    - row["scenario_expected_value"]
                )
                < 0.001
                for row in valuation_rows
            ),
        ),
        (
            "formal target arithmetic reconciles",
            lambda: all(
                abs(
                    round(
                        row["fundamental_weight"] * row["scenario_expected_value"]
                        + row["market_weight"] * row["market_implied_anchor"]
                        + row["broker_weight"] * row["broker_anchor"],
                        2,
                    )
                    - row["final_target"]
                )
                < 0.001
                and row["market_weight"] == 0
                for row in valuation_rows
            ),
        ),
        (
            "formal upside and weights reconcile",
            lambda: all(
                abs(
                    round(row["final_target"] / row["current_price"] - 1, 4)
                    - row["upside"]
                )
                < 0.0001
                and abs(
                    row["fundamental_weight"]
                    + row["market_weight"]
                    + row["broker_weight"]
                    - 1
                )
                < 1e-9
                for row in valuation_rows
            ),
        ),
        (
            "source-pure original-PDF Street anchors cover formal valuations",
            original_broker_sources_valid,
        ),
        (
            "conditional-watch universe and arithmetic are exact",
            lambda: {row["ticker"] for row in conditional_rows}
            == expected_conditional_tickers
            and all(
                abs(
                    round(
                        row["bear"] * row["probabilities"]["bear"]
                        + row["base"] * row["probabilities"]["base"]
                        + row["bull"] * row["probabilities"]["bull"],
                        2,
                    )
                    - row["probability_expected_value"]
                )
                < 0.001
                for row in conditional_rows
            ),
        ),
        (
            "Hengrui SOTP components reconcile",
            hengrui_sotp_reconciles,
        ),
        (
            "growth-driver models have institutional depth",
            lambda: len(growth["drivers"]) == 4
            and {row["ticker"] for row in growth["drivers"]}
            == {"600276", "601138", "000063", "301308"}
            and all(
                row.get("historical_bridge")
                and row.get("scenario_earnings_bridge")
                and row.get("current_price_implied_growth")
                and row.get("evidence_status")
                and row.get("direct_disclosure")
                and row.get("proxy_evidence")
                and row.get("checked_sources")
                and row.get("formal_boundary")
                and row.get("valuation_consequence")
                and row.get("valuation_credit")
                and row.get("next_quarter_validation_threshold")
                for row in growth["drivers"]
            ),
        ),
        (
            "expanded valuation coverage and arithmetic reconcile",
            expanded_valuation_reconciles,
        ),
        (
            "legacy thematic evidence archive is complete",
            lambda: broker_catalog["universe_count"] == 54
            and broker_catalog["priority_count"] == 28
            and len(broker_catalog["download_rows"]) == 56
            and not broker_catalog["failures"]
            and broker_digests["ticker_count"] == 28
            and broker_digests["report_count"] == 56
            and preview_archive["archived_count"] == 16
            and preview_archive["failure_count"] == 0,
        ),
        (
            "reader-facing report contains repaired hierarchy and downgrades",
            lambda: all(
                token in compact_text
                for token in (
                    "31行业",
                    "364家A股公司",
                    "73只",
                    "16只",
                    "五只正式估值",
                    "中兴、江波龙与陕西煤业条件观察",
                    "旧48.75元目标撤销",
                    "旧802.30元目标撤销",
                    "ModelReproducibility:PASS",
                    "16只优先股全部建立公司级",
                    "72只H1候选有公平价值区间",
                    "117只去重标的",
                    "7月15日半年报预告增量更新",
                    "新增归档9只",
                    "开放实质缺口为0",
                    "Full-MarketValuationCoverageReproducibility:PASS",
                )
            )
        ),
        (
            "reader-facing placeholders are absent",
            lambda: not any(
                token in compact_text for token in ("TODO", "TBD", "<Report", "暂列观察")
            ),
        ),
        (
            "valuation and growth audits pass",
            lambda: "Model Reproducibility: PASS"
            in read_text("analysis/valuation_audit.md")
            and "Full-Market Valuation Coverage Reproducibility: PASS"
            in read_text("analysis/valuation_audit.md")
            and "Gate status: PASS"
            in read_text("analysis/growth_earnings_model.md"),
        ),
        (
            "source registry, claim audit and exhaustion are complete",
            lambda: len(source_registry["sources"]) == 17
            and len(claim_audit["claims"]) == 17
            and len(exhaustion["entries"]) >= 9,
        ),
        (
            "ephemeral two-pass XeLaTeX build has no blocking diagnostics",
            latex_build_is_clean,
        ),
        (
            "PDF text stays inside page bounds",
            lambda: pdf_out_of_bounds_count() == 0,
        ),
        (
            "active exhibit identifiers are unique",
            unique_exhibits,
        ),
        (
            "review cycles and final sign-off are closed",
            review_and_signoff_closed,
        ),
    ]

    failures: list[str] = []
    for name, predicate in checks:
        try:
            passed = bool(predicate())
        except Exception as exc:
            passed = False
            name = f"{name}: {exc}"
        if passed:
            print(f"PASS {name}")
        else:
            print(f"FAIL {name}")
            failures.append(name)

    print(f"SUMMARY {len(checks) - len(failures)} PASS / {len(failures)} FAIL")
    print("RESULT PASS" if not failures else "RESULT FAIL")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
