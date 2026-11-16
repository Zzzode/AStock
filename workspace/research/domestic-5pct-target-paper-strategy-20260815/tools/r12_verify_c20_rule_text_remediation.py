#!/usr/bin/env python3
"""Verify the C20 v2 remediation for R10-SC-01 without using the capture verifier."""

from __future__ import annotations

import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from xml.etree import ElementTree


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c20-current-sse-rule-text-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
C20_PATH = CASE_DIR / "analysis" / "c20_domestic_public_reit_strategy_feasibility_20260815.json"
R13_PATH = CASE_DIR / "analysis" / "r13_r10_v1_scope_mismatch_correction_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r12_c20_rule_text_remediation_verification_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r12_c20_rule_text_remediation_verification_20260815.md"
EXPECTED_MANIFEST_SHA256 = "f0e710ef25872489d4ee697c58fb0bf73abd8c180f0d4115ce10aaf69e278829"
EXPECTED_R13_SHA256 = "59ef545fc892f645f9a5c68f01e9b6983698d5ab89968e276faa96a78936e0d8"
EXPECTED_LEGACY_R10_REEXECUTION_SHA256 = "3d3d7b897981269d96b64bf447911a07e32e9c65f9be43734433db6fb4026f8c"
EXPECTED_KEYS = {
    "sse_current_reit_business_rule_announcement",
    "sse_current_reit_business_rule_body",
    "sse_repeal_notice_for_2021_reit_rule",
    "sse_reit_investor_education_material",
    "sse_current_trading_rule_announcement",
    "sse_current_trading_rule_body",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml")
    root = ElementTree.fromstring(xml)
    return "".join(root.itertext())


def pdf_page_count(path: Path) -> int:
    result = subprocess.run(
        ["pdfinfo", str(path)],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "pdfinfo failed")
    for line in result.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":", 1)[1].strip())
    raise RuntimeError("page count not found")


def main() -> int:
    checks: list[dict[str, object]] = []
    failures: list[str] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    check("manifest frozen hash", sha256(MANIFEST_PATH) == EXPECTED_MANIFEST_SHA256, sha256(MANIFEST_PATH))
    key_map = {str(item.get("source_key")): item for item in records if isinstance(item, dict)}
    check("six expected source keys", set(key_map) == EXPECTED_KEYS, f"keys={len(key_map)}")
    raw_failures: list[str] = []
    for key, record in key_map.items():
        raw = SOURCE_DIR / str(record.get("filename") or "")
        if not raw.is_file() or raw.stat().st_size != record.get("bytes") or sha256(raw) != record.get("sha256"):
            raw_failures.append(key)
    check("raw file size and hash integrity", not raw_failures, ", ".join(raw_failures) or "all matched")

    html_requirements = {
        "sse_current_reit_business_rule_announcement": ("公开募集不动产投资信托基金", "同时废止"),
        "sse_repeal_notice_for_2021_reit_rule": ("已废止",),
        "sse_current_trading_rule_announcement": ("交易规则", "2026年"),
    }
    html_failures: list[str] = []
    for key, terms in html_requirements.items():
        text = (SOURCE_DIR / str(key_map[key]["filename"])).read_text(encoding="utf-8", errors="ignore")
        if any(term not in text for term in terms):
            html_failures.append(key)
    check("retained HTML text presence", not html_failures, ", ".join(html_failures) or "all matched")

    docx_requirements = {
        "sse_current_reit_business_rule_body": ("公开募集不动产投资信托基金", "普通投资者", "风险揭示书"),
        "sse_current_trading_rule_body": ("上海证券交易所交易规则", "最小变动单位", "100"),
    }
    docx_failures: list[str] = []
    for key, terms in docx_requirements.items():
        try:
            text = docx_text(SOURCE_DIR / str(key_map[key]["filename"]))
            if any(term not in text for term in terms):
                docx_failures.append(key)
        except Exception:
            docx_failures.append(key)
    check("retained DOCX body text presence", not docx_failures, ", ".join(docx_failures) or "all matched")

    pdf_failure = ""
    try:
        education_path = SOURCE_DIR / str(key_map["sse_reit_investor_education_material"]["filename"])
        if not education_path.read_bytes().startswith(b"%PDF-") or pdf_page_count(education_path) != 2:
            pdf_failure = "unexpected PDF container or page count"
    except Exception as exc:
        pdf_failure = str(exc)
    check("retained education PDF container", not pdf_failure, pdf_failure or "two-page scanned source; text is not machine-extractable")

    c20 = json.loads(C20_PATH.read_text(encoding="utf-8"))
    r13 = json.loads(R13_PATH.read_text(encoding="utf-8"))
    capture_control = c20.get("source_control", {}).get("current_rule_capture_manifest", {})
    r13_control = c20.get("source_control", {}).get("r13_r10_v1_scope_correction", {})
    legacy_r10_trace = c20.get("source_control", {}).get("legacy_r10_v1_verifier_reexecution_trace", {})
    check("C20 v2 identifier", c20.get("artifact_id") == "D5PT-C20-FEASIBILITY-v2", str(c20.get("artifact_id")))
    check(
        "C20 binds current-rule manifest",
        capture_control.get("path") == str(MANIFEST_PATH.relative_to(REPO_ROOT)) and capture_control.get("sha256") == EXPECTED_MANIFEST_SHA256,
        str(capture_control),
    )
    check(
        "C20 binds R13 scope correction",
        r13_control.get("path") == str(R13_PATH.relative_to(REPO_ROOT)) and r13_control.get("sha256") == EXPECTED_R13_SHA256 and sha256(R13_PATH) == EXPECTED_R13_SHA256,
        str(r13_control),
    )
    check(
        "R13 correctly qualifies the legacy R10 re-execution",
        r13.get("result") == "PASS_SCOPE_MISMATCH_DOCUMENTED"
        and r13.get("historical_boundary", {}).get("historical_gap_id") == "R10-SC-01"
        and r13.get("legacy_artifact", {}).get("sha256") == EXPECTED_LEGACY_R10_REEXECUTION_SHA256,
        str(r13.get("result")),
    )
    check(
        "C20 retains the legacy R10 scope-mismatch trace",
        legacy_r10_trace.get("sha256") == EXPECTED_LEGACY_R10_REEXECUTION_SHA256
        and "scope-mismatch" in str(legacy_r10_trace.get("role") or ""),
        str(legacy_r10_trace),
    )
    amendment = c20.get("source_control_amendment", {})
    check(
        "R10-SC-01 remediation recorded",
        amendment.get("previous_feasibility_sha256") == "21f4ce8c90c68ed1acca106ea7261e109dd184736a2f7b4a8f19a81eec649f4a" and "R10-SC-01" in str(amendment.get("reason") or ""),
        str(amendment),
    )
    live_checks = c20.get("source_control", {}).get("live_primary_rule_recheck", [])
    retained_count = sum(1 for item in live_checks if isinstance(item, dict) and item.get("retention_state") == "retained_in_c20_current_rule_source_batch")
    check("all four rule references are retained", retained_count == 4, f"retained={retained_count}")
    scope = c20.get("scope_control", {})
    disposition = c20.get("current_disposition", {})
    action_boundary = (
        c20.get("research_only") is True
        and c20.get("formal_decision_eligible") is False
        and c20.get("external_orders") is False
        and c20.get("portfolio_q") == 0
        and scope.get("product_selected") is False
        and scope.get("universe_selected") is False
        and scope.get("historical_strategy_selected") is False
        and scope.get("return_test_run") is False
        and scope.get("return_result") is None
        and scope.get("eligibility_inference") is False
        and disposition.get("state") == "NO_STRATEGY_TEST_ADMISSION_NO_PRODUCT_SELECTION_NO_ACTION"
    )
    check("C20 retains no-selection/no-test/no-action boundary", action_boundary, "scope and disposition fields")
    check(
        "R13 preserves the historical R10 source-gap provenance",
        r13.get("historical_boundary", {}).get("reported_pre_amendment_result") == "PASS_WITH_OPEN_SOURCE_CONTROL_GAP",
        str(r13.get("historical_boundary", {}).get("reported_pre_amendment_result")),
    )

    report = {
        "schema_version": "r12_c20_rule_text_remediation_verification.v1",
        "artifact_id": "D5PT-R12-C20-REMEDIATION-VERIFICATION-v1",
        "as_of": "2026-08-15",
        "verification_type": "post-R10 deterministic remediation verification; it does not replace the historical v1 audit and uses R13 to prevent a post-remediation legacy rerun from being misread",
        "result": "PASS" if not failures else "FAIL",
        "r10_gap": "R10-SC-01 URL-only current-rule source control",
        "remediation_state": "CLOSED_FOR_CURRENT_RULE_TEXT_RETENTION" if not failures else "OPEN",
        "checks": checks,
        "failures": failures,
        "boundary": "Closing the rule-text retention gap does not create a point-in-time universe, total-return ledger, cost record, fill record, individual eligibility conclusion, product selection, return result or external action.",
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# R12 C20 规则正文留存修复核验",
        "",
        f"- 结果：`{report['result']}`；R10-SC-01 的规则正文留存缺口：`{report['remediation_state']}`。",
        "- 这是 R10 后的确定性修复核验；R13 说明为什么遗留 v1 校验器在 C20 v2 上的机械失败不能被当作当前缺口。",
        "- 它只关闭当前规则文本的留存缺口；不形成总体、总回报、成本、成交、资格、选品、收益结果或外部动作。",
        "",
        "| 检查 | 结果 | 说明 |",
        "|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['name']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |")
    if failures:
        lines.extend(["", "## 失败项", "", *[f"- {failure}" for failure in failures]])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"R12 C20 RULE-TEXT REMEDIATION VERIFICATION: {report['result']}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
