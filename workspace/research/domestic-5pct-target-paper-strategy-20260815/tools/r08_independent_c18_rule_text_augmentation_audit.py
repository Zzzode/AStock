#!/usr/bin/env python3
"""Independently audit C18's supplementary SSE rule-text source batch.

This auditor is intentionally self-contained.  It does not import the C18
capture or feasibility verifier, choose a bond, infer an investor's access,
calculate a performance result, or initiate an external action.  Its PASS is
limited to source integrity, DOCX text presence, and the retained v2
not-testable/no-action controls.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
INITIAL_SOURCE_DIR = CASE_DIR / "sources" / "c18-official-sse-company-bond-feasibility-20260815"
AUGMENTATION_SOURCE_DIR = CASE_DIR / "sources" / "c18-official-sse-company-bond-rule-text-augmentation-20260815"
INITIAL_MANIFEST_PATH = INITIAL_SOURCE_DIR / "manifest.json"
AUGMENTATION_MANIFEST_PATH = AUGMENTATION_SOURCE_DIR / "manifest.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c18_direct_sse_company_bond_ladder_feasibility_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r08_independent_c18_rule_text_augmentation_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r08_independent_c18_rule_text_augmentation_audit_20260815.md"

EXPECTED_INITIAL_MANIFEST_SHA256 = "0ef9a473ae98c5fafcb6f4cb92e8785ab5a2eb220f3c7c0ce41e42617872b908"
EXPECTED_AUGMENTATION_MANIFEST_SHA256 = "863fc638ccd443c3f5c22355094e6b326a52967f5943d1d65eee64fc0d951a69"
EXPECTED_FEASIBILITY_SHA256 = "4f6668c828b2e6ca4349b630150cd9a00050971e9411030444bfe2a1b5f66cfb"

EXPECTED_AUGMENTATION_RECORDS = {
    "sse_company_bond_listing_rule_body": {
        "filename": "sse_company_bond_listing_rule_20231020.docx",
        "bytes": 48332,
        "sha256": "367614be7f44286f5022bb086eeb5b5d040fdd1c21593361c9f436ec39b6c9fd",
        "terms": (
            "上海证券交易所公司债券上市规则",
            "分类管理",
            "差异化的交易机制",
            "投资者适当性制度",
        ),
    },
    "sse_company_bond_credit_risk_rule_body": {
        "filename": "sse_company_bond_credit_risk_management_rule_20231020.docx",
        "bytes": 91634,
        "sha256": "8e0d2b23f6c973237b55d803b5ee87f532c3facae303e6c1280eff3d42729455",
        "terms": (
            "公司债券和资产支持证券信用风险管理",
            "信用风险监测与预警",
            "信用风险应对与处置",
            "投资者权益保护机制安排",
        ),
    },
}

EXPECTED_FEASIBILITY_SOURCE_KEYS = {
    "sse_company_bond_listing_rule",
    "sse_bond_investor_suitability_rule",
    "csrc_company_bond_administration_measure",
    "sse_company_bond_credit_risk_rule",
    "sse_bond_information_portal",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _docx_text(path: Path) -> tuple[str, dict[str, Any]]:
    """Extract text directly from the required DOCX XML body.

    The result is deliberately only a text-presence observation.  It does not
    interpret the rules as evidence of any person's access to any security.
    """

    if not zipfile.is_zipfile(path):
        raise ValueError("raw source is not a ZIP/DOCX file")
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        if "word/document.xml" not in names:
            raise ValueError("DOCX has no word/document.xml")
        xml_bytes = archive.read("word/document.xml")
    root = ET.fromstring(xml_bytes)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{namespace}p"):
        words = [node.text or "" for node in paragraph.iter(f"{namespace}t")]
        joined = "".join(words).strip()
        if joined:
            paragraphs.append(joined)
    text = "\n".join(paragraphs)
    return text, {
        "zip_container": True,
        "word_document_xml_present": True,
        "document_xml_bytes": len(xml_bytes),
        "paragraph_count": len(paragraphs),
        "text_characters": len(text),
    }


def _failure(failures: list[str], message: str) -> None:
    if message not in failures:
        failures.append(message)


def _manifest_and_raw_checks(failures: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, Any]]:
    manifest_hash = _sha256(AUGMENTATION_MANIFEST_PATH)
    if manifest_hash != EXPECTED_AUGMENTATION_MANIFEST_SHA256:
        _failure(failures, "augmentation manifest SHA-256 differs from the frozen expected value")
    manifest = _read_object(AUGMENTATION_MANIFEST_PATH)

    if manifest.get("schema_version") != "c18_sse_company_bond_rule_text_augmentation_manifest.v1":
        _failure(failures, "augmentation manifest schema version is unexpected")
    if manifest.get("case_id") != "domestic-5pct-target-paper-strategy-20260815":
        _failure(failures, "augmentation manifest case ID is unexpected")
    if manifest.get("source_quality") != "dated_primary_exchange_rule_text":
        _failure(failures, "augmentation manifest source quality is unexpected")

    records = manifest.get("records")
    if not isinstance(records, list):
        _failure(failures, "augmentation manifest records are not a list")
        return manifest, [], {"manifest_sha256": manifest_hash, "record_key_set_match": False}

    record_by_key: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            _failure(failures, "augmentation manifest contains a non-object record")
            continue
        source_key = record.get("source_key")
        if not isinstance(source_key, str) or not source_key:
            _failure(failures, "augmentation manifest record has no valid source_key")
            continue
        if source_key in record_by_key:
            _failure(failures, f"duplicate augmentation source_key: {source_key}")
            continue
        record_by_key[source_key] = record

    expected_keys = set(EXPECTED_AUGMENTATION_RECORDS)
    actual_keys = set(record_by_key)
    if actual_keys != expected_keys:
        _failure(failures, "augmentation source-key set differs from the frozen two-document set")

    rows: list[dict[str, Any]] = []
    manifest_paths: set[Path] = set()
    for source_key in sorted(expected_keys):
        expectation = EXPECTED_AUGMENTATION_RECORDS[source_key]
        record = record_by_key.get(source_key)
        row: dict[str, Any] = {
            "source_key": source_key,
            "expected_filename": expectation["filename"],
            "manifest_path": None,
            "expected_bytes": expectation["bytes"],
            "manifest_bytes": None,
            "actual_bytes": None,
            "expected_sha256": expectation["sha256"],
            "manifest_sha256": None,
            "actual_sha256": None,
            "metadata_ok": False,
            "raw_integrity_ok": False,
            "status": "FAIL",
        }
        if record is None:
            _failure(failures, f"expected augmentation record absent: {source_key}")
            rows.append(row)
            continue

        raw_path = REPO_ROOT / str(record.get("path") or "")
        row["manifest_path"] = str(record.get("path") or "")
        row["manifest_bytes"] = record.get("bytes")
        row["manifest_sha256"] = record.get("sha256")
        try:
            raw_path.relative_to(AUGMENTATION_SOURCE_DIR)
        except ValueError:
            _failure(failures, f"augmentation raw path escapes its source batch: {source_key}")
        else:
            manifest_paths.add(raw_path)

        metadata_fields_ok = (
            raw_path.name == expectation["filename"]
            and record.get("bytes") == expectation["bytes"]
            and record.get("sha256") == expectation["sha256"]
            and record.get("publisher") == "Shanghai Stock Exchange"
            and record.get("document_date") == "2023-10-20"
            and isinstance(record.get("url"), str)
            and record["url"].startswith("https://www.sse.com.cn/")
            and isinstance(record.get("capture_note"), str)
            and bool(record["capture_note"].strip())
        )
        row["metadata_ok"] = metadata_fields_ok
        if not metadata_fields_ok:
            _failure(failures, f"unexpected metadata in augmentation record: {source_key}")

        if not raw_path.is_file():
            _failure(failures, f"augmentation raw file is missing: {source_key}")
            rows.append(row)
            continue
        raw = raw_path.read_bytes()
        row["actual_bytes"] = len(raw)
        row["actual_sha256"] = hashlib.sha256(raw).hexdigest()
        row["raw_integrity_ok"] = (
            row["actual_bytes"] == expectation["bytes"]
            and row["actual_sha256"] == expectation["sha256"]
            and row["actual_bytes"] == record.get("bytes")
            and row["actual_sha256"] == record.get("sha256")
        )
        if not row["raw_integrity_ok"]:
            _failure(failures, f"augmentation raw integrity mismatch: {source_key}")
        if row["metadata_ok"] and row["raw_integrity_ok"]:
            row["status"] = "PASS"
        rows.append(row)

    on_disk_docx = {path.resolve() for path in AUGMENTATION_SOURCE_DIR.glob("*.docx")}
    listed_docx = {path.resolve() for path in manifest_paths}
    no_unlisted_or_missing_docx = on_disk_docx == listed_docx
    if not no_unlisted_or_missing_docx:
        _failure(failures, "DOCX files on disk do not exactly match augmentation manifest records")

    return manifest, rows, {
        "path": _relative(AUGMENTATION_MANIFEST_PATH),
        "expected_sha256": EXPECTED_AUGMENTATION_MANIFEST_SHA256,
        "actual_sha256": manifest_hash,
        "expected_hash_match": manifest_hash == EXPECTED_AUGMENTATION_MANIFEST_SHA256,
        "record_key_set_match": actual_keys == expected_keys,
        "all_docx_on_disk_listed": no_unlisted_or_missing_docx,
    }


def _docx_text_checks(records: dict[str, Any], failures: list[str]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for source_key in sorted(EXPECTED_AUGMENTATION_RECORDS):
        expectation = EXPECTED_AUGMENTATION_RECORDS[source_key]
        record = records.get(source_key)
        row: dict[str, Any] = {
            "source_key": source_key,
            "path": None,
            "zip_container": False,
            "word_document_xml_present": False,
            "document_xml_bytes": None,
            "paragraph_count": None,
            "text_characters": None,
            "required_terms": list(expectation["terms"]),
            "missing_terms": list(expectation["terms"]),
            "text_presence_ok": False,
            "status": "FAIL",
        }
        if not isinstance(record, dict):
            _failure(failures, f"cannot inspect missing augmentation DOCX record: {source_key}")
            outputs.append(row)
            continue
        raw_path = REPO_ROOT / str(record.get("path") or "")
        row["path"] = _relative(raw_path) if raw_path.exists() else str(record.get("path") or "")
        try:
            text, metadata = _docx_text(raw_path)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
            _failure(failures, f"cannot extract DOCX body for {source_key}: {exc}")
            outputs.append(row)
            continue
        row.update(metadata)
        compact = _compact(text)
        missing = [term for term in expectation["terms"] if term not in compact]
        row["missing_terms"] = missing
        row["text_presence_ok"] = (
            bool(metadata["zip_container"])
            and bool(metadata["word_document_xml_present"])
            and int(metadata["paragraph_count"]) > 0
            and int(metadata["text_characters"]) >= 500
            and not missing
        )
        if not row["text_presence_ok"]:
            _failure(failures, f"DOCX text-presence check failed: {source_key}")
        else:
            row["status"] = "PASS"
        outputs.append(row)
    return outputs


def _feasibility_v2_checks(failures: list[str]) -> dict[str, Any]:
    observed_hash = _sha256(FEASIBILITY_PATH)
    if observed_hash != EXPECTED_FEASIBILITY_SHA256:
        _failure(failures, "C18 feasibility v2 SHA-256 differs from the independently frozen value")
    feasibility = _read_object(FEASIBILITY_PATH)

    source_control = feasibility.get("source_control")
    strict_screen = feasibility.get("strict_screen_boundary")
    disposition = feasibility.get("current_disposition")
    amendment = feasibility.get("source_control_amendment")
    findings = feasibility.get("bounded_primary_source_findings")
    blockers = feasibility.get("missing_blocking_evidence")
    predeclared = feasibility.get("predeclared_research_hypothesis_not_yet_frozen_for_test")

    structural_ok = (
        feasibility.get("schema_version") == "c18_direct_sse_company_bond_ladder_feasibility.v1"
        and feasibility.get("artifact_id") == "D5PT-C18-FEASIBILITY-v2"
        and feasibility.get("status") == "SOURCE_PREFLIGHT_PASS_HISTORICAL_UNIVERSE_AND_RETURN_TEST_NOT_READY"
        and feasibility.get("research_only") is True
        and feasibility.get("formal_decision_eligible") is False
        and feasibility.get("external_orders") is False
    )
    if not structural_ok:
        _failure(failures, "C18 feasibility file does not retain the expected v2 structural boundary")

    initial_binding_ok = (
        isinstance(source_control, dict)
        and source_control.get("initial_preflight_manifest") == {
            "path": _relative(INITIAL_MANIFEST_PATH),
            "sha256": EXPECTED_INITIAL_MANIFEST_SHA256,
        }
        and _sha256(INITIAL_MANIFEST_PATH) == EXPECTED_INITIAL_MANIFEST_SHA256
    )
    augmentation_binding_ok = (
        isinstance(source_control, dict)
        and source_control.get("rule_text_augmentation_manifest") == {
            "path": _relative(AUGMENTATION_MANIFEST_PATH),
            "sha256": EXPECTED_AUGMENTATION_MANIFEST_SHA256,
        }
        and _sha256(AUGMENTATION_MANIFEST_PATH) == EXPECTED_AUGMENTATION_MANIFEST_SHA256
    )
    if not initial_binding_ok:
        _failure(failures, "C18 feasibility v2 does not correctly bind the initial preflight manifest")
    if not augmentation_binding_ok:
        _failure(failures, "C18 feasibility v2 does not correctly bind the rule-text augmentation manifest")

    source_keys = source_control.get("records_used") if isinstance(source_control, dict) else None
    source_keys_ok = isinstance(source_keys, list) and set(source_keys) == EXPECTED_FEASIBILITY_SOURCE_KEYS
    if not source_keys_ok:
        _failure(failures, "C18 feasibility v2 source-control record set is unexpected")

    amendment_ok = (
        isinstance(amendment, dict)
        and amendment.get("reassessment_required") is True
        and isinstance(amendment.get("reason"), str)
        and bool(amendment["reason"].strip())
        and isinstance(amendment.get("previous_feasibility_sha256"), str)
        and bool(re.fullmatch(r"[0-9a-f]{64}", amendment["previous_feasibility_sha256"]))
    )
    if not amendment_ok:
        _failure(failures, "C18 feasibility v2 source-control amendment is incomplete")

    finding_boundaries_ok = (
        isinstance(findings, list)
        and len(findings) == 3
        and all(
            isinstance(finding, dict)
            and isinstance(finding.get("finding"), str)
            and bool(finding["finding"].strip())
            and isinstance(finding.get("source_keys"), list)
            and bool(finding["source_keys"])
            and isinstance(finding.get("boundary"), str)
            and bool(finding["boundary"].strip())
            for finding in findings
        )
    )
    if not finding_boundaries_ok:
        _failure(failures, "C18 feasibility v2 has incomplete bounded primary-source findings")

    screen_boundary_ok = (
        isinstance(strict_screen, dict)
        and strict_screen.get("current_result") == "NOT_TESTABLE_FOR_RETURN"
        and isinstance(strict_screen.get("reason"), str)
        and bool(strict_screen["reason"].strip())
        and isinstance(strict_screen.get("five_percent_role"), str)
        and "not a guaranteed annual result" in strict_screen["five_percent_role"]
    )
    if not screen_boundary_ok:
        _failure(failures, "C18 feasibility v2 no-test result boundary is missing or weakened")

    no_action_boundary_ok = (
        isinstance(disposition, dict)
        and disposition.get("state") == "NO_BOND_SELECTED_NO_HISTORICAL_TEST_NO_ACTION"
        and isinstance(disposition.get("next_research_gate"), str)
        and bool(disposition["next_research_gate"].strip())
        and isinstance(disposition.get("prohibitions"), list)
        and any("Do not infer ordinary-investor access" in item for item in disposition["prohibitions"] if isinstance(item, str))
        and any("Do not select a bond" in item and "create an order" in item for item in disposition["prohibitions"] if isinstance(item, str))
    )
    if not no_action_boundary_ok:
        _failure(failures, "C18 feasibility v2 no-action boundary is missing or weakened")

    missing_inputs_ok = (
        isinstance(blockers, list)
        and len(blockers) >= 5
        and all(isinstance(item, str) and bool(item.strip()) for item in blockers)
        and isinstance(predeclared, dict)
        and isinstance(predeclared.get("governance"), str)
        and "No historical download" in predeclared["governance"]
        and "independent-review protocol" in predeclared["governance"]
    )
    if not missing_inputs_ok:
        _failure(failures, "C18 feasibility v2 missing-input or pre-test governance control is incomplete")

    return {
        "path": _relative(FEASIBILITY_PATH),
        "expected_sha256": EXPECTED_FEASIBILITY_SHA256,
        "actual_sha256": observed_hash,
        "expected_hash_match": observed_hash == EXPECTED_FEASIBILITY_SHA256,
        "structural_v2_boundary_ok": structural_ok,
        "initial_manifest_binding_ok": initial_binding_ok,
        "augmentation_manifest_binding_ok": augmentation_binding_ok,
        "source_control_record_set_ok": source_keys_ok,
        "source_control_amendment_ok": amendment_ok,
        "bounded_finding_controls_ok": finding_boundaries_ok,
        "not_testable_boundary_ok": screen_boundary_ok,
        "no_action_boundary_ok": no_action_boundary_ok,
        "missing_input_and_pretest_governance_ok": missing_inputs_ok,
        "observed_current_result": strict_screen.get("current_result") if isinstance(strict_screen, dict) else None,
        "observed_disposition": disposition.get("state") if isinstance(disposition, dict) else None,
    }


def _markdown(result: dict[str, Any]) -> str:
    manifest = result["augmentation_manifest"]
    feasibility = result["feasibility_v2"]
    lines = [
        "# R08 C18 规则正文补充来源独立审计",
        "",
        "## 审计结论",
        "",
        f"- 结果：`{result['result']}`。",
        "- PASS 仅表示：补充来源清单、两份原始 DOCX、规则正文文本存在性，以及 C18 v2 的受限边界均通过本独立审计。",
        "- 它不表示可选择任何债券、可推断任何人的权限、可进行历史表现测试或可作出外部动作。",
        "- 当前路线仍是 `NOT_TESTABLE_FOR_RETURN`，且状态仍为 `NO_BOND_SELECTED_NO_HISTORICAL_TEST_NO_ACTION`。",
        "",
        "## 补充来源清单与原始文件",
        "",
        f"- 清单：`{manifest['path']}`。",
        f"- SHA-256：`{manifest['actual_sha256']}`（冻结值匹配：`{manifest['expected_hash_match']}`）。",
        f"- 来源键集合匹配：`{manifest['record_key_set_match']}`；磁盘 DOCX 与清单一一对应：`{manifest['all_docx_on_disk_listed']}`。",
        "",
        "| source_key | 文件完整性 | DOCX 正文存在性 |",
        "|---|---:|---:|",
    ]
    text_by_key = {item["source_key"]: item for item in result["docx_text_presence"]}
    for row in result["raw_file_integrity"]:
        text_row = text_by_key.get(row["source_key"], {})
        lines.append(
            f"| `{row['source_key']}` | `{row['status']}` | `{text_row.get('status', 'FAIL')}` |"
        )

    lines.extend(
        [
            "",
            "两份 DOCX 均由其 `word/document.xml` 直接解析；审计检查 DOCX 容器、正文 XML、段落和足以识别文档主题的规则术语。该检查只确认文本存在，不将规则表述延伸为逐债券、逐日期或逐投资者的可交易性结论。",
            "",
            "## C18 v2 绑定与边界",
            "",
            f"- 可行性文件：`{feasibility['path']}`。",
            f"- 可行性文件 SHA-256 冻结值匹配：`{feasibility['expected_hash_match']}`。",
            f"- 初始预检清单绑定：`{feasibility['initial_manifest_binding_ok']}`；规则正文补充清单绑定：`{feasibility['augmentation_manifest_binding_ok']}`。",
            f"- v2 结构边界：`{feasibility['structural_v2_boundary_ok']}`；来源修订记录：`{feasibility['source_control_amendment_ok']}`。",
            f"- 未测试边界：`{feasibility['not_testable_boundary_ok']}`；无动作边界：`{feasibility['no_action_boundary_ok']}`。",
            f"- 观察到的结果状态：`{feasibility['observed_current_result']}`；观察到的处置状态：`{feasibility['observed_disposition']}`。",
            "",
            "## 结论边界",
            "",
            "补充批次修复的是先前公告页未单独留存规则正文附件的来源控制缺口；它没有补齐历史债券母体、全价与成交、现金流和信用事件、逐时点适当性、费用结算或成交处理资料。因此仍不得把该路线写成可使用策略，或将规则文本当作历史测试数据。",
            "",
            "## 审计范围外事项",
            "",
            "- 未选择债券，未形成标的清单。",
            "- 未计算收益、表现或回测结果。",
            "- 未推断任何人的资格、账户权限或可参与范围。",
            "- 未创建订单或实施任何外部动作。",
        ]
    )
    if result["failures"]:
        lines.extend(["", "## 失败项", ""])
        lines.extend(f"- {failure}" for failure in result["failures"])
    return "\n".join(lines) + "\n"


def _write(path: Path, contents: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(path)


def main() -> int:
    failures: list[str] = []
    try:
        augmentation_manifest, raw_rows, manifest_summary = _manifest_and_raw_checks(failures)
        records = augmentation_manifest.get("records")
        record_by_key = {
            str(record.get("source_key")): record
            for record in records
            if isinstance(record, dict) and isinstance(record.get("source_key"), str)
        } if isinstance(records, list) else {}
        text_rows = _docx_text_checks(record_by_key, failures)
        feasibility_summary = _feasibility_v2_checks(failures)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _failure(failures, f"audit runtime error: {exc}")
        raw_rows = []
        text_rows = []
        manifest_summary = {
            "path": _relative(AUGMENTATION_MANIFEST_PATH),
            "expected_sha256": EXPECTED_AUGMENTATION_MANIFEST_SHA256,
            "actual_sha256": None,
            "expected_hash_match": False,
            "record_key_set_match": False,
            "all_docx_on_disk_listed": False,
        }
        feasibility_summary = {
            "path": _relative(FEASIBILITY_PATH),
            "expected_sha256": EXPECTED_FEASIBILITY_SHA256,
            "actual_sha256": None,
            "expected_hash_match": False,
            "structural_v2_boundary_ok": False,
            "initial_manifest_binding_ok": False,
            "augmentation_manifest_binding_ok": False,
            "source_control_record_set_ok": False,
            "source_control_amendment_ok": False,
            "bounded_finding_controls_ok": False,
            "not_testable_boundary_ok": False,
            "no_action_boundary_ok": False,
            "missing_input_and_pretest_governance_ok": False,
            "observed_current_result": None,
            "observed_disposition": None,
        }

    result = {
        "schema_version": "r08_independent_c18_rule_text_augmentation_audit.v1",
        "artifact_id": "D5PT-R08-C18-AUGMENTATION-AUDIT-v1",
        "as_of": "2026-08-15",
        "audit_scope": {
            "independent_of_c18_verifier": True,
            "checks": [
                "frozen augmentation manifest hash and metadata",
                "raw DOCX file size and SHA-256",
                "direct DOCX word/document.xml text-presence checks",
                "C18 feasibility v2 binds both source manifests",
                "C18 feasibility v2 retains not-testable and no-action boundaries",
            ],
            "not_performed": [
                "bond selection",
                "access inference",
                "performance calculation",
                "external action",
            ],
        },
        "result": "PASS" if not failures else "FAIL",
        "bounded_disposition": "C18 remains not testable and admits no bond or external action.",
        "augmentation_manifest": manifest_summary,
        "raw_file_integrity": raw_rows,
        "docx_text_presence": text_rows,
        "feasibility_v2": feasibility_summary,
        "failures": failures,
    }
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"R08 independent C18 rule-text augmentation audit: {result['result']}")
    if failures:
        for failure in failures:
            print(f"- {failure}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
