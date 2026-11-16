#!/usr/bin/env python3
"""Independently audit C19's retained public data-source capture.

This verifier is intentionally self-contained: it does not import or execute
the C19 capture/verifier module.  It recomputes hashes from the raw files,
checks the manifest and C19 source-control binding, and confirms that C19
remains a conditional data-path review rather than a tested or actionable
bond strategy.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c19-official-bond-data-source-feasibility-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c19_bond_historical_data_source_feasibility_20260815.json"
MARKDOWN_PATH = CASE_DIR / "analysis" / "c19_bond_historical_data_source_feasibility_20260815.md"
OUTPUT_JSON = CASE_DIR / "analysis" / "r11_independent_c19_data_source_feasibility_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r11_independent_c19_data_source_feasibility_audit_20260815.md"

AS_OF = "2026-08-15"
EXPECTED_MANIFEST_SHA256 = "77e337a09c80906a143b15dcfc72f60631847a3f44d63aeea5a9e0a531ac9d41"
EXPECTED_FEASIBILITY_SHA256 = "c251dff603184f4fd6312f2a60764a5cfe97341051031fa6b39ec8338b1bb49f"
EXPECTED_CAPTURE_SCOPE = (
    "Public descriptions of candidate data products, field concepts and authorization boundaries only; "
    "not a license, data dictionary, historical delivery, individual eligibility record or return input."
)
EXPECTED_MANIFEST_BOUNDARY = (
    "These public pages only document potential products, field concepts and rights boundaries. "
    "They are not acquired historical bond data, a use-right grant, an eligibility record or a performance input."
)
EXPECTED_RECORDS: dict[str, dict[str, Any]] = {
    "sseinfo_historical_market_data_product": {
        "filename": "sseinfo_historical_market_data_product.html",
        "url": "https://www.sseinfo.com/services/assortment/historical/",
        "publisher": "SSE InfoNet",
        "content_type_prefix": "text/html",
        "bytes": 23029,
        "sha256": "dbae0135ca890931f4161f0b9c239029096dddb55015738f0c988fd92005a85f",
        "required_terms": ("行情历史数据", "快照数据", "逐笔成交", "日K线", "业务申请"),
    },
    "sseinfo_historical_data_interface_specification": {
        "filename": "sseinfo_historical_data_interface_specification.pdf",
        "url": "https://www.sseinfo.com/services/assortment/document/interface/c/10759166/files/4f38cae1022a4cfa8410bbc2702e2b95.pdf",
        "publisher": "SSE InfoNet",
        "content_type_prefix": "application/pdf",
        "bytes": 726725,
        "sha256": "45497cd472c5cd52e7aa5e5c989d8f56350397a5277ea7798aefc9dc208d8988",
        "required_terms": ("上海证券交易所历史数据接口说明书", "BondTick.csv", "产品状态订单", "自2021年12月1日启用"),
    },
    "sseinfo_fixed_income_market_data_product": {
        "filename": "sseinfo_fixed_income_market_data_product.html",
        "url": "https://www.sseinfo.com/services/assortment/income/",
        "publisher": "SSE InfoNet",
        "content_type_prefix": "text/html",
        "bytes": 23118,
        "sha256": "107c10a3a506b405c41108f2726598c4e12cf4731fe0bccc661b74aa0d865b55",
        "required_terms": ("固定收益行情", "公司债现券", "即时非匹配成交行情信息", "业务申请"),
    },
    "chinabond_valuation_query_surface": {
        "filename": "chinabond_valuation_query_surface.html",
        "url": "https://indices.chinabond.com.cn/cbweb-mn/val/val_query_list?locale=zh_CN",
        "publisher": "ChinaBond",
        "content_type_prefix": "text/html",
        "bytes": 81823,
        "sha256": "22e05769ac1d440a8d6a8c11262ce0603d5682adf14b021a256a23c4a6d2e2ef",
        "required_terms": ("估值日期", "日终估价全价", "日终应计利息", "估价净价"),
    },
    "chinabond_yield_methodology_surface": {
        "filename": "chinabond_yield_methodology_surface.html",
        "url": "https://valuation.chinabond.com.cn/cbweb-mn/int/int_yield_syl_doc",
        "publisher": "ChinaBond",
        "content_type_prefix": "text/html",
        "bytes": 9676,
        "sha256": "478dbbf6b532f12f0a48f2275820a87d704fa34cac41386bd1574fc47c4e8d60",
        "required_terms": ("中债收益率曲线", "交易所债券的成交数据", "交易所固定收益平台报价和成交数据"),
    },
    "sseinfo_authorization_statement": {
        "filename": "sseinfo_authorization_statement.html",
        "url": "https://www.sseinfo.com/aboutus/authstatement/",
        "publisher": "SSE InfoNet",
        "content_type_prefix": "text/html",
        "bytes": 19410,
        "sha256": "728c5f7d0bf41cdaef1008906f7ee57254b212f435545b21a5b1ecac697d35e4",
        "required_terms": ("授权声明", "未经证券交易所许可", "申请许可", "接收、使用或经营"),
    },
}
EXPECTED_TIER_IDS = {f"S19-0{number}" for number in range(1, 7)}
EXPECTED_RIGHTS_SOURCE_ID = "S19-07"
EXPECTED_FIELD_GROUP_COUNT = 7
EXPECTED_ACCEPTANCE_TEST_COUNT = 8
EXPECTED_UNRETAINED_T2_CANDIDATE_URLS = {
    "https://www.wind.com.cn/mobile/WFT/zh.html",
    "https://www.wind.com.cn/portal/zh/ClientApi/index.html",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _load_object(path: Path, label: str, failures: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        _failure(failures, f"cannot read {label}: {error}")
        return {}
    if not isinstance(payload, dict):
        _failure(failures, f"{label} is not a JSON object")
        return {}
    return payload


def _failure(failures: list[str], message: str) -> None:
    if message not in failures:
        failures.append(message)


def _compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _parse_iso_timestamp(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return True


def _extract_pdf_text(path: Path) -> tuple[str, str | None]:
    executable = shutil.which("pdftotext")
    if executable is None:
        return "", "pdftotext is unavailable"
    result = subprocess.run(
        [executable, "-layout", str(path), "-"],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or f"exit={result.returncode}"
        return "", f"pdftotext failed: {detail}"
    return result.stdout, None


def _source_content_check(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    raw = path.read_bytes()
    required_terms = [str(term) for term in expected["required_terms"]]
    is_pdf = path.suffix.lower() == ".pdf"
    text = ""
    extraction_error: str | None = None
    structure_ok = False
    if is_pdf:
        structure_ok = raw.startswith(b"%PDF-")
        text, extraction_error = _extract_pdf_text(path)
    else:
        text = raw.decode("utf-8", errors="replace")
        structure_ok = "<html" in text.lower() and "</html" in text.lower()
    compact_text = _compact(text)
    missing_terms = [term for term in required_terms if _compact(term) not in compact_text]
    text_presence_ok = extraction_error is None and len(text.strip()) >= 100 and not missing_terms
    return {
        "source_key": next(key for key, item in EXPECTED_RECORDS.items() if item["filename"] == path.name),
        "path": _relative(path),
        "format": "pdf" if is_pdf else "html",
        "structure_ok": structure_ok,
        "text_extraction_error": extraction_error,
        "text_characters": len(text),
        "required_terms": required_terms,
        "missing_terms": missing_terms,
        "text_presence_ok": text_presence_ok,
        "status": "PASS" if structure_ok and text_presence_ok else "FAIL",
    }


def _audit_manifest_and_raw(failures: list[str]) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    manifest_exists = MANIFEST_PATH.is_file()
    manifest_hash = _sha256(MANIFEST_PATH) if manifest_exists else None
    if not manifest_exists:
        _failure(failures, "C19 source manifest is missing")
    elif manifest_hash != EXPECTED_MANIFEST_SHA256:
        _failure(failures, "C19 source manifest SHA-256 differs from the frozen expected value")

    manifest = _load_object(MANIFEST_PATH, "C19 source manifest", failures) if manifest_exists else {}
    manifest_metadata_ok = (
        manifest.get("schema_version") == "c19_primary_source_capture.v1"
        and manifest.get("capture_id") == "D5PT-C19-SOURCE-CAPTURE-v1"
        and manifest.get("purpose")
        == "Preserve public primary-source descriptions of candidate lawful data paths; no license, extract, entitlement or historical test data is represented."
        and manifest.get("boundary") == EXPECTED_MANIFEST_BOUNDARY
    )
    if not manifest_metadata_ok:
        _failure(failures, "C19 source manifest metadata or boundary differs from the expected frozen capture")

    records = manifest.get("records")
    if not isinstance(records, list):
        _failure(failures, "C19 source manifest records are not a list")
        records = []

    record_by_key: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            _failure(failures, "C19 source manifest contains a non-object record")
            continue
        source_key = record.get("source_key")
        if not isinstance(source_key, str) or not source_key:
            _failure(failures, "C19 source manifest contains an invalid source_key")
            continue
        if source_key in record_by_key:
            _failure(failures, f"C19 source manifest has duplicate source_key: {source_key}")
            continue
        record_by_key[source_key] = record

    expected_keys = set(EXPECTED_RECORDS)
    actual_keys = set(record_by_key)
    if len(records) != len(EXPECTED_RECORDS):
        _failure(failures, "C19 source manifest does not retain exactly six records")
    if actual_keys != expected_keys:
        _failure(failures, "C19 source manifest source-key set differs from the frozen six-file capture")

    raw_rows: list[dict[str, Any]] = []
    content_rows: list[dict[str, Any]] = []
    listed_paths: set[Path] = set()
    for source_key in sorted(expected_keys):
        expected = EXPECTED_RECORDS[source_key]
        record = record_by_key.get(source_key)
        row: dict[str, Any] = {
            "source_key": source_key,
            "expected_filename": expected["filename"],
            "manifest_filename": None,
            "expected_bytes": expected["bytes"],
            "manifest_bytes": None,
            "actual_bytes": None,
            "expected_sha256": expected["sha256"],
            "manifest_sha256": None,
            "actual_sha256": None,
            "metadata_ok": False,
            "raw_integrity_ok": False,
            "status": "FAIL",
        }
        if record is None:
            _failure(failures, f"expected C19 record is absent: {source_key}")
            raw_rows.append(row)
            continue

        filename = record.get("filename")
        row["manifest_filename"] = filename
        row["manifest_bytes"] = record.get("bytes")
        row["manifest_sha256"] = record.get("sha256")
        raw_path = SOURCE_DIR / str(filename or "")
        try:
            path_within_source_dir = raw_path.resolve().parent == SOURCE_DIR.resolve()
        except OSError:
            path_within_source_dir = False
        if not path_within_source_dir:
            _failure(failures, f"C19 raw path escapes its source batch: {source_key}")
        else:
            listed_paths.add(raw_path.resolve())

        metadata_ok = (
            filename == expected["filename"]
            and record.get("url") == expected["url"]
            and record.get("final_url") == expected["url"]
            and record.get("publisher") == expected["publisher"]
            and record.get("expected_content_prefix") == expected["content_type_prefix"]
            and isinstance(record.get("content_type"), str)
            and record["content_type"].startswith(str(expected["content_type_prefix"]))
            and record.get("http_status") == 200
            and record.get("bytes") == expected["bytes"]
            and record.get("sha256") == expected["sha256"]
            and _parse_iso_timestamp(record.get("retrieved_at"))
        )
        row["metadata_ok"] = metadata_ok
        if not metadata_ok:
            _failure(failures, f"unexpected C19 capture metadata: {source_key}")

        if not raw_path.is_file():
            _failure(failures, f"C19 raw source file is missing: {source_key}")
            raw_rows.append(row)
            continue
        raw = raw_path.read_bytes()
        actual_hash = hashlib.sha256(raw).hexdigest()
        row["actual_bytes"] = len(raw)
        row["actual_sha256"] = actual_hash
        row["raw_integrity_ok"] = (
            len(raw) == expected["bytes"]
            and actual_hash == expected["sha256"]
            and len(raw) == record.get("bytes")
            and actual_hash == record.get("sha256")
        )
        if not row["raw_integrity_ok"]:
            _failure(failures, f"C19 raw source integrity mismatch: {source_key}")
        if metadata_ok and row["raw_integrity_ok"]:
            row["status"] = "PASS"
        raw_rows.append(row)

        content_row = _source_content_check(raw_path, expected)
        content_rows.append(content_row)
        if content_row["status"] != "PASS":
            _failure(failures, f"C19 source content-presence check failed: {source_key}")

    on_disk_raw = {
        path.resolve()
        for path in SOURCE_DIR.iterdir()
        if path.is_file() and path.name != MANIFEST_PATH.name
    } if SOURCE_DIR.is_dir() else set()
    raw_file_set_ok = on_disk_raw == listed_paths
    if not raw_file_set_ok:
        _failure(failures, "C19 raw files on disk do not exactly match the six manifest records")

    manifest_summary = {
        "path": _relative(MANIFEST_PATH),
        "expected_sha256": EXPECTED_MANIFEST_SHA256,
        "actual_sha256": manifest_hash,
        "expected_hash_match": manifest_hash == EXPECTED_MANIFEST_SHA256,
        "manifest_metadata_ok": manifest_metadata_ok,
        "record_count": len(records),
        "record_key_set_match": actual_keys == expected_keys,
        "raw_file_set_exact_match": raw_file_set_ok,
    }
    return manifest, raw_rows, content_rows, manifest_summary


def _collect_feasibility_urls(feasibility: dict[str, Any]) -> set[str]:
    urls: set[str] = set()
    tiers = feasibility.get("source_tiers")
    if isinstance(tiers, list):
        for tier in tiers:
            if not isinstance(tier, dict):
                continue
            url = tier.get("url")
            if isinstance(url, str):
                urls.add(url)
            multiple = tier.get("urls")
            if isinstance(multiple, list):
                urls.update(item for item in multiple if isinstance(item, str))
    rights_boundary = feasibility.get("rights_boundary")
    if isinstance(rights_boundary, dict) and isinstance(rights_boundary.get("url"), str):
        urls.add(rights_boundary["url"])
    return urls


def _audit_feasibility_binding(manifest: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    feasibility_exists = FEASIBILITY_PATH.is_file()
    feasibility_hash = _sha256(FEASIBILITY_PATH) if feasibility_exists else None
    if not feasibility_exists:
        _failure(failures, "C19 feasibility JSON is missing")
    elif feasibility_hash != EXPECTED_FEASIBILITY_SHA256:
        _failure(failures, "C19 feasibility JSON SHA-256 differs from the independently frozen expected value")
    feasibility = _load_object(FEASIBILITY_PATH, "C19 feasibility JSON", failures) if feasibility_exists else {}

    source_control = feasibility.get("source_control")
    if not isinstance(source_control, dict):
        source_control = {}
        _failure(failures, "C19 source_control is missing or invalid")
    expected_binding = {
        "path": _relative(MANIFEST_PATH),
        "sha256": EXPECTED_MANIFEST_SHA256,
    }
    manifest_binding_ok = (
        source_control.get("primary_source_capture_manifest") == expected_binding
        and MANIFEST_PATH.is_file()
        and _sha256(MANIFEST_PATH) == EXPECTED_MANIFEST_SHA256
    )
    if not manifest_binding_ok:
        _failure(failures, "C19 feasibility does not correctly bind the retained six-file manifest")
    capture_scope_ok = source_control.get("capture_scope") == EXPECTED_CAPTURE_SCOPE
    if not capture_scope_ok:
        _failure(failures, "C19 capture_scope is missing or weakened")

    tier_ids = {
        str(item.get("source_id"))
        for item in feasibility.get("source_tiers", [])
        if isinstance(item, dict)
    }
    rights_boundary = feasibility.get("rights_boundary")
    tier_structure_ok = (
        tier_ids == EXPECTED_TIER_IDS
        and isinstance(rights_boundary, dict)
        and rights_boundary.get("source_id") == EXPECTED_RIGHTS_SOURCE_ID
    )
    if not tier_structure_ok:
        _failure(failures, "C19 tiered-source structure or rights-boundary identifier differs")

    manifest_records = manifest.get("records") if isinstance(manifest.get("records"), list) else []
    manifest_urls = {
        record.get("url")
        for record in manifest_records
        if isinstance(record, dict) and isinstance(record.get("url"), str)
    }
    feasibility_urls = _collect_feasibility_urls(feasibility)
    captured_urls_referenced_ok = manifest_urls <= feasibility_urls
    if not captured_urls_referenced_ok:
        _failure(failures, "not every retained C19 source URL is referenced by the C19 feasibility record")

    unretained_urls = feasibility_urls - manifest_urls
    wind_tier = next(
        (
            item
            for item in feasibility.get("source_tiers", [])
            if isinstance(item, dict) and item.get("source_id") == "S19-06"
        ),
        None,
    )
    unretained_t2_disclosed_ok = (
        unretained_urls == EXPECTED_UNRETAINED_T2_CANDIDATE_URLS
        and isinstance(wind_tier, dict)
        and wind_tier.get("tier") == "T2_commercial_vendor_vendor_declared_scope"
        and wind_tier.get("admission_status") == "candidate_only_pending_contract_dictionary_and_independent_reconciliation"
    )
    if not unretained_t2_disclosed_ok:
        _failure(failures, "C19 has unexplained or incorrectly labelled feasibility URLs outside the six-file retained primary batch")

    field_matrix = feasibility.get("required_field_matrix")
    field_matrix_ok = (
        isinstance(field_matrix, list)
        and len(field_matrix) == EXPECTED_FIELD_GROUP_COUNT
        and all(
            isinstance(row, dict)
            and row.get("current_case_coverage") == "not_captured"
            and isinstance(row.get("blocking_gap"), str)
            and bool(row["blocking_gap"].strip())
            for row in field_matrix
        )
    )
    if not field_matrix_ok:
        _failure(failures, "C19 required-field matrix does not preserve every field as not_captured")

    acceptance_tests = feasibility.get("data_acquisition_acceptance_tests")
    acceptance_tests_ok = (
        isinstance(acceptance_tests, list)
        and len(acceptance_tests) == EXPECTED_ACCEPTANCE_TEST_COUNT
        and all(isinstance(item, str) and bool(item.strip()) for item in acceptance_tests)
    )
    if not acceptance_tests_ok:
        _failure(failures, "C19 data-acquisition acceptance tests are incomplete")

    amendment = feasibility.get("source_control_amendment")
    amendment_ok = (
        isinstance(amendment, dict)
        and amendment.get("previous_feasibility_sha256") == "9f595dfb467fbcc815661aa18ea7ad2725c7658c9693033492fe249cb8dbaaf7"
        and isinstance(amendment.get("reason"), str)
        and "does not change" in amendment["reason"]
        and "testability state" in amendment["reason"]
    )
    if not amendment_ok:
        _failure(failures, "C19 source-control amendment is incomplete or changes the feasibility boundary")

    return {
        "feasibility": feasibility,
        "path": _relative(FEASIBILITY_PATH),
        "expected_sha256": EXPECTED_FEASIBILITY_SHA256,
        "actual_sha256": feasibility_hash,
        "expected_hash_match": feasibility_hash == EXPECTED_FEASIBILITY_SHA256,
        "manifest_binding_ok": manifest_binding_ok,
        "capture_scope_ok": capture_scope_ok,
        "tier_structure_ok": tier_structure_ok,
        "captured_urls_referenced_ok": captured_urls_referenced_ok,
        "unretained_t2_candidate_urls": sorted(unretained_urls),
        "unretained_t2_disclosed_candidate_only_ok": unretained_t2_disclosed_ok,
        "required_field_matrix_ok": field_matrix_ok,
        "acceptance_tests_ok": acceptance_tests_ok,
        "source_control_amendment_ok": amendment_ok,
    }


def _audit_boundaries(feasibility: dict[str, Any], failures: list[str]) -> dict[str, Any]:
    action_boundary_ok = (
        feasibility.get("research_only") is True
        and feasibility.get("formal_decision_eligible") is False
        and feasibility.get("external_orders") is False
    )
    conditional_path_ok = feasibility.get("research_result") == "CONDITIONAL_LAWFUL_SOURCE_PATHS_IDENTIFIED"
    not_testable_ok = feasibility.get("current_route_status") == "not_testable"
    source_capture_status = feasibility.get("source_capture_status")
    source_capture_boundary_ok = (
        isinstance(source_capture_status, str)
        and "Six public" in source_capture_status
        and "No subscription was obtained" in source_capture_status
        and "no historical market-data extract was received" in source_capture_status
    )
    executive = feasibility.get("executive_conclusion")
    executive_boundary_ok = (
        isinstance(executive, str)
        and "not_testable" in executive
        and "bond selection" in executive
        and "performance calculation" in executive
        and "external action" in executive
    )
    not_allowed = feasibility.get("not_allowed")
    no_action_prohibitions_ok = (
        isinstance(not_allowed, list)
        and len(not_allowed) >= 3
        and any("Choose bonds" in item and "external action" in item for item in not_allowed if isinstance(item, str))
        and any("Replace missing event" in item and "tested" in item for item in not_allowed if isinstance(item, str))
    )
    next_gate = feasibility.get("next_research_gate")
    next_gate_ok = isinstance(next_gate, str) and "C18 direct company-bond route stays not_testable" in next_gate

    controls = {
        "action_boundary_ok": action_boundary_ok,
        "conditional_data_path_ok": conditional_path_ok,
        "not_testable_ok": not_testable_ok,
        "source_capture_boundary_ok": source_capture_boundary_ok,
        "executive_boundary_ok": executive_boundary_ok,
        "no_action_prohibitions_ok": no_action_prohibitions_ok,
        "next_research_gate_ok": next_gate_ok,
        "observed_research_result": feasibility.get("research_result"),
        "observed_route_status": feasibility.get("current_route_status"),
    }
    for name, passed in controls.items():
        if name.endswith("_ok") and not passed:
            _failure(failures, f"C19 boundary check failed: {name}")
    return controls


def _audit_markdown(failures: list[str]) -> dict[str, Any]:
    if not MARKDOWN_PATH.is_file():
        _failure(failures, "C19 feasibility markdown is missing")
        return {"path": _relative(MARKDOWN_PATH), "exists": False, "required_text_ok": False, "captured_urls_referenced_ok": False}
    text = MARKDOWN_PATH.read_text(encoding="utf-8")
    required_text = (
        "`CONDITIONAL_LAWFUL_SOURCE_PATHS_IDENTIFIED`",
        "`not_testable`",
        "未选择债券、未计算表现、未推断任何人的权限，也未形成外部动作",
        "公开页面可用于证明产品和字段方向，不能被当作已获得历史数据或使用权",
        "C18 的正确研究状态保持为 `not_testable`",
        "sources/c19-official-bond-data-source-feasibility-20260815/manifest.json",
    )
    missing_text = [item for item in required_text if item not in text]
    if missing_text:
        _failure(failures, "C19 feasibility markdown does not retain required conditional/not-testable/no-action language")
    captured_urls = {item["url"] for item in EXPECTED_RECORDS.values()}
    missing_urls = sorted(url for url in captured_urls if url not in text)
    if missing_urls:
        _failure(failures, "C19 feasibility markdown does not reference every retained capture URL")
    return {
        "path": _relative(MARKDOWN_PATH),
        "exists": True,
        "sha256": _sha256(MARKDOWN_PATH),
        "required_text_ok": not missing_text,
        "missing_required_text": missing_text,
        "captured_urls_referenced_ok": not missing_urls,
        "missing_captured_urls": missing_urls,
    }


def _write(path: Path, contents: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(path)


def _markdown(report: dict[str, Any]) -> str:
    manifest = report["source_manifest"]
    raw_rows = report["raw_file_integrity"]
    content_rows = {row["source_key"]: row for row in report["source_content_presence"]}
    binding = report["c19_feasibility_binding"]
    boundary = report["bounded_controls"]
    markdown_alignment = report["markdown_alignment"]
    lines = [
        "# R11 C19 公司债历史数据来源可行性独立审计",
        "",
        "## 审计结论",
        "",
        f"- 结果：`{report['result']}`。",
        "- 本审计独立重算 C19 清单及六份原始文件的 SHA-256；未导入或调用 C19 采集/核验器。",
        "- PASS 只证明保留的公开来源批次、C19 来源控制和受限研究边界保持一致。它不证明已取得数据许可、字段字典、历史样本、完整覆盖或任何个人交易资格。",
        f"- 观察到的 C19 状态：`{boundary['observed_research_result']}`；路线状态：`{boundary['observed_route_status']}`。",
        "- 不选择债券、不计算表现、不推断权限，也不产生外部动作。",
        "",
        "## 清单与六份原始文件",
        "",
        f"- 清单：`{manifest['path']}`。",
        f"- 冻结 SHA-256：`{manifest['expected_sha256']}`；实际：`{manifest['actual_sha256']}`；匹配：`{manifest['expected_hash_match']}`。",
        f"- 记录数：`{manifest['record_count']}`；来源键集合匹配：`{manifest['record_key_set_match']}`；磁盘原始文件集合精确匹配：`{manifest['raw_file_set_exact_match']}`。",
        "",
        "| source_key | 原始文件完整性 | 内容存在性 |",
        "|---|---:|---:|",
    ]
    for row in raw_rows:
        content_status = content_rows.get(row["source_key"], {}).get("status", "FAIL")
        lines.append(f"| `{row['source_key']}` | `{row['status']}` | `{content_status}` |")
    lines.extend(
        [
            "",
            "内容检查仅确认所保留文件的 HTML/PDF 结构及其可识别主题术语；它不把公开产品页、接口说明或授权声明升级为数据许可、历史交付或可回测数据集。",
            "",
            "## C19 来源控制和研究边界",
            "",
            f"- C19 文件：`{binding['path']}`。冻结 SHA-256 匹配：`{binding['expected_hash_match']}`。",
            f"- 清单绑定：`{binding['manifest_binding_ok']}`；留存范围：`{binding['capture_scope_ok']}`；六条来源/权利边界结构：`{binding['tier_structure_ok']}`。",
            f"- 每个已留存 URL 在 C19 中有引用：`{binding['captured_urls_referenced_ok']}`；所需字段均仍为 `not_captured`：`{binding['required_field_matrix_ok']}`；验收测试完整：`{binding['acceptance_tests_ok']}`。",
            "- 来源控制资格说明：C19 另列的两条 Wind T2 商业供应商 URL 不属于六份已冻结的一手批次；它们仍明确为 `candidate_only`，未被用作许可、历史交付或可测试性证明。该未留存 T2 路径是后续尽调限制，不影响本批次完整性或 `not_testable` 结论。",
            f"- 行动边界：`{boundary['action_boundary_ok']}`；条件数据路径：`{boundary['conditional_data_path_ok']}`；`not_testable` 边界：`{boundary['not_testable_ok']}`；禁止项：`{boundary['no_action_prohibitions_ok']}`。",
            f"- Markdown 同步：`{markdown_alignment['required_text_ok']}`；已留存 URL 引用完整：`{markdown_alignment['captured_urls_referenced_ok']}`。",
            "",
            "## 限定解释",
            "",
            "R11 没有获取受保护端点、许可数据或账户信息，也没有计算债券回报。它只确认 C19 仍是一个有条件的数据获取尽调路径；在书面权利、字段字典、样本和逐时点覆盖均得到独立验证前，C18 继续保持 `not_testable`、无债券选择、无行动。",
        ]
    )
    if report["failures"]:
        lines.extend(["", "## 失败项", "", *[f"- {item}" for item in report["failures"]]])
    return "\n".join(lines) + "\n"


def main() -> int:
    failures: list[str] = []
    manifest, raw_rows, content_rows, manifest_summary = _audit_manifest_and_raw(failures)
    binding = _audit_feasibility_binding(manifest, failures)
    boundary = _audit_boundaries(binding["feasibility"], failures)
    markdown_alignment = _audit_markdown(failures)

    report = {
        "schema_version": "r11_independent_c19_data_source_feasibility_audit.v1",
        "artifact_id": "D5PT-R11-C19-DATA-SOURCE-AUDIT-v1",
        "as_of": AS_OF,
        "audit_scope": {
            "independent_of_c19_capture_verifier": True,
            "checks": [
                "frozen C19 manifest hash and capture metadata",
                "all six retained raw-file sizes and SHA-256 values",
                "direct retained HTML/PDF structure and text-presence checks",
                "C19 source-control binding to the retained manifest",
                "conditional-data-path, not-testable, and no-action controls",
                "C19 markdown alignment with the retained source URLs and boundaries",
            ],
            "not_performed": [
                "data-license acquisition",
                "protected-endpoint retrieval",
                "bond selection",
                "performance calculation",
                "access or eligibility inference",
                "external action",
            ],
        },
        "result": "PASS" if not failures else "FAIL",
        "bounded_disposition": "C19 remains a conditional lawful data-acquisition diligence path. C18 remains not_testable; no bond, investor access conclusion, return result, or external action is admitted.",
        "source_manifest": manifest_summary,
        "raw_file_integrity": raw_rows,
        "source_content_presence": content_rows,
        "c19_feasibility_binding": {key: value for key, value in binding.items() if key != "feasibility"},
        "bounded_controls": boundary,
        "markdown_alignment": markdown_alignment,
        "failures": failures,
    }
    _write(OUTPUT_JSON, json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(report))
    print(f"R11 INDEPENDENT C19 DATA-SOURCE FEASIBILITY AUDIT: {report['result']}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
