#!/usr/bin/env python3
"""Verify semiconductor PCB research workspace artifact consistency."""
from __future__ import annotations

import json
import hashlib
import csv
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BASE.parents[2]


def load_json(rel: str):
    return json.loads((BASE / rel).read_text(encoding="utf-8"))


def count_exists_rows() -> tuple[int, int]:
    rows = 0
    mismatches = 0
    for line in (BASE / "data_room_index.md").read_text(encoding="utf-8").splitlines():
        if not line.startswith("| `workspace/"):
            continue
        parts = [p.strip() for p in line.strip().strip("|").split("|")]
        if len(parts) >= 2 and parts[1] in {"True", "False"}:
            rows += 1
            raw_path = parts[0].strip("`")
            path_obj = Path(raw_path)
            if raw_path.startswith("workspace/"):
                path_obj = PROJECT_ROOT / raw_path
            elif not path_obj.is_absolute():
                path_obj = BASE / raw_path
            exists = path_obj.exists()
            if (parts[1] == "True") != exists:
                mismatches += 1
    return rows, mismatches


def verify_checksums() -> tuple[int, list[str]]:
    manifest = load_json("data/core_artifact_checksums_20260618.json")
    manifest_md = (BASE / "data/core_artifact_checksums_20260618.md").read_text(encoding="utf-8")
    problems: list[str] = []
    for item in manifest.get("files", []):
        path = BASE / item["path"]
        if not path.exists():
            problems.append(f"{item['path']}: missing")
            continue
        data = path.read_bytes()
        actual_size = len(data)
        actual_sha = hashlib.sha256(data).hexdigest()
        if actual_size != item.get("size_bytes") or actual_sha != item.get("sha256"):
            problems.append(
                f"{item['path']}: size {actual_size}!={item.get('size_bytes')} "
                f"or sha {actual_sha}!={item.get('sha256')}"
            )
        expected_md_row = f"| `{item['path']}` | {item.get('size_bytes')} | `{item.get('sha256')}` |"
        if expected_md_row not in manifest_md:
            problems.append(f"{item['path']}: missing or stale row in core_artifact_checksums_20260618.md")
    return len(manifest.get("files", [])), problems


def verify_request_pack_csv() -> tuple[int, list[str]]:
    request_pack = load_json("missing_data_request_pack.json")
    with (BASE / "missing_data_request_pack.csv").open(encoding="utf-8", newline="") as f:
        csv_rows = list(csv.DictReader(f))
    problems: list[str] = []
    json_rows = request_pack.get("requirements", [])
    csv_by_id = {row.get("requirement_id"): row for row in csv_rows}
    if len(csv_rows) != len(json_rows):
        problems.append(f"row count {len(csv_rows)}!={len(json_rows)}")
    for row in json_rows:
        req_id = row.get("id")
        csv_row = csv_by_id.get(req_id)
        if csv_row is None:
            problems.append(f"{req_id}: missing CSV row")
            continue
        comparisons = {
            "title": row.get("title", ""),
            "targets": " ; ".join(row.get("targets", [])),
            "required_fields": " ; ".join(row.get("required_fields", [])),
            "periods": " ; ".join(row.get("periods", [])),
            "preferred_sources": " ; ".join(row.get("preferred_sources", [])),
            "current_public_status": row.get("current_public_status", ""),
            "completion_test": row.get("completion_test", ""),
        }
        for field, expected in comparisons.items():
            if csv_row.get(field, "") != expected:
                problems.append(f"{req_id}: CSV {field} mismatch")
    return len(csv_rows), problems


def verify_request_pack_markdown() -> list[str]:
    request_pack = load_json("missing_data_request_pack.json")
    request_md = (BASE / "missing_data_request_pack.md").read_text(encoding="utf-8")
    required_terms = [
        "external_data_required",
        "public_sources_exhausted_through",
        "customer annual-report / SEC-style risk disclosures",
        "customer Form SD / conflict-minerals filings including NVIDIA",
        "NVIDIA Form SD memory/substrates/components and supplier-survey mechanics",
        "Tencent public Level-1 five-level quote-depth snapshot",
        "customer annual-risk disclosure recheck",
        "customer Form SD / conflict-minerals recheck",
    ]
    for item in request_pack.get("source_documents_needed", []):
        required_terms.extend(
            [
                str(item.get("document")),
                str(item.get("target")),
                str(item.get("why")),
            ]
        )
    for criterion in request_pack.get("completion_criteria", []):
        required_terms.append(str(criterion))
    return [f"missing_data_request_pack.md missing {term}" for term in required_terms if term not in request_md]


def verify_handoff_terms() -> list[str]:
    registry = (BASE / "data/source_registry.md").read_text(encoding="utf-8")
    templates = (BASE / "external_data_request_templates.md").read_text(encoding="utf-8")
    problems: list[str] = []
    registry_terms = [
        "M05",
        "CUST-CUR01",
        "CUST-AR01",
        "CUST-SD01",
        "CUST-MAT01",
        "Level-1 quote-depth snapshot",
        "Customer purchase-commitment matrix",
        "including NVIDIA",
    ]
    template_terms = [
        "current Amazon/Dell/Microsoft/Apple supplier-list routes",
        "customer annual-report / SEC-style risk disclosures",
        "customer Form SD / conflict-minerals filings including NVIDIA",
        "Tencent public Level-1 five-level quote-depth snapshot",
        "customer purchase-commitment matrix",
        "Full customs/BOL dataset",
        "complete shipper/consignee/product/quantity/value/date fields",
        "Public BOL pages are insufficient",
    ]
    for term in registry_terms:
        if term not in registry:
            problems.append(f"source_registry.md missing {term}")
    for term in template_terms:
        if term not in templates:
            problems.append(f"external_data_request_templates.md missing {term}")
    form_sd = (BASE / "data/customer_form_sd_conflict_minerals_recheck_20260618.md").read_text(encoding="utf-8")
    form_sd_terms = [
        "NVIDIA discloses a fabless and contract-manufacturing strategy",
        "surveyed 164 direct suppliers",
        "identified 246 processing facilities",
        "Alphabet external page probe",
        "returned HTTP 403",
    ]
    for term in form_sd_terms:
        if term not in form_sd:
            problems.append(f"customer_form_sd_conflict_minerals_recheck_20260618.md missing {term}")
    return problems


def verify_root_inventory() -> tuple[int, list[str]]:
    root_inv = load_json("data/root_artifact_inventory_20260618.json")
    problems: list[str] = []
    for item in root_inv.get("files", []):
        path = BASE / item["file"]
        if not path.exists():
            problems.append(f"{item['file']}: missing")
            continue
        actual_size = path.stat().st_size
        if actual_size != item.get("size_bytes"):
            problems.append(f"{item['file']}: size {actual_size}!={item.get('size_bytes')}")
        expected_md_row = f"| `{item['file']}` | `{item['type']}` | {item['size_bytes']} |"
        root_md = (BASE / "data/root_artifact_inventory_20260618.md").read_text(encoding="utf-8")
        if expected_md_row not in root_md:
            problems.append(f"{item['file']}: missing or stale row in root_artifact_inventory_20260618.md")
    return len(root_inv.get("files", [])), problems


def verify_top_level_data_inventory() -> tuple[int, list[str]]:
    data_inv = load_json("data/top_level_data_artifact_inventory_20260618.json")
    data_md = (BASE / "data/top_level_data_artifact_inventory_20260618.md").read_text(encoding="utf-8")
    problems: list[str] = []
    for item in data_inv.get("files", []):
        path = BASE / "data" / item["file"]
        if not path.exists():
            problems.append(f"{item['file']}: missing")
            continue
        actual_size = path.stat().st_size
        if actual_size != item.get("size_bytes"):
            problems.append(f"{item['file']}: size {actual_size}!={item.get('size_bytes')}")
        expected_md_row = (
            f"| `{item['file']}` | `{item['type']}` | {item['main_index_row']} | "
            f"{item['category']} | {item['size_bytes']} |"
        )
        if expected_md_row not in data_md:
            problems.append(f"{item['file']}: missing or stale row in top_level_data_artifact_inventory_20260618.md")
    return len(data_inv.get("files", [])), problems


def verify_source_inventory() -> tuple[int, list[str]]:
    source_inv = load_json("data/source_artifact_inventory_20260618.json")
    source_md = (BASE / "data/source_artifact_inventory_20260618.md").read_text(encoding="utf-8")
    problems: list[str] = []
    for item in source_inv.get("files", []):
        path = BASE / item["path"]
        if not path.exists():
            problems.append(f"{item['path']}: missing")
            continue
        actual_size = path.stat().st_size
        if actual_size != item.get("size_bytes"):
            problems.append(f"{item['path']}: size {actual_size}!={item.get('size_bytes')}")
        expected_md_row = f"| `{item['path']}` | `{item['type']}` | {item['size_bytes']} |"
        if expected_md_row not in source_md:
            problems.append(f"{item['path']}: missing or stale row in source_artifact_inventory_20260618.md")
    return len(source_inv.get("files", [])), problems


def verify_simple_inventory(json_rel: str, md_rel: str, base_dir: str, count_key: str) -> tuple[int, list[str]]:
    inventory = load_json(json_rel)
    inventory_md = (BASE / md_rel).read_text(encoding="utf-8")
    problems: list[str] = []
    for item in inventory.get("files", []):
        rel_path = item.get("path") or item.get("file")
        path = BASE / rel_path if str(rel_path).startswith(base_dir) else BASE / base_dir / rel_path
        if not path.exists():
            problems.append(f"{rel_path}: missing")
            continue
        actual_size = path.stat().st_size
        if actual_size != item.get("size_bytes"):
            problems.append(f"{rel_path}: size {actual_size}!={item.get('size_bytes')}")
        expected_md_row = f"| `{rel_path}` | `{item['type']}` | {item['size_bytes']} |"
        if expected_md_row not in inventory_md:
            problems.append(f"{rel_path}: missing or stale row in {Path(md_rel).name}")
    return len(inventory.get("files", [])), problems


def verify_ticker_matrix() -> tuple[int, list[str]]:
    matrix_json = load_json("ticker_evidence_coverage_matrix.json")
    matrix_md = (BASE / "ticker_evidence_coverage_matrix.md").read_text(encoding="utf-8")
    columns = [
        "ticker",
        "group",
        "broker_pdf",
        "official_filing",
        "structured_financial",
        "segment_customer",
        "historical_price",
        "valuation_history",
        "fund_holder",
        "circulating_holder",
        "important_institution",
        "fund_flow",
        "eps_model",
    ]
    md_rows: list[dict[str, object]] = []
    for line in matrix_md.splitlines():
        if not line.startswith("| ") or "---" in line or "ticker" in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(parts) != len(columns):
            continue
        row: dict[str, object] = {"ticker": parts[0], "group": parts[1]}
        for column, value in zip(columns[2:], parts[2:]):
            row[column] = value == "True"
        md_rows.append(row)
    problems: list[str] = []
    if md_rows != matrix_json:
        problems.append("ticker_evidence_coverage_matrix.md does not match JSON rows")
    if len(matrix_json) != 12:
        problems.append(f"row count {len(matrix_json)}!=12")
    if not any(row.get("ticker") == "002938" for row in matrix_json):
        problems.append("missing 002938")
    return len(matrix_json), problems


def verify_render_directory_index(rendered_inv: dict) -> list[str]:
    index_text = (BASE / "data_room_index.md").read_text(encoding="utf-8")
    current_dir = rendered_inv.get("full_render_sequence_check", {}).get("directory")
    problems: list[str] = []
    if current_dir and current_dir not in index_text:
        problems.append(f"data_room_index.md missing current render directory {current_dir}")
    expected_pages = rendered_inv.get("full_render_sequence_check", {}).get("expected_pages")
    current_row = f"workspace/research/semiconductor-pcb-20260612/{current_dir}` | {expected_pages} | Current full"
    if current_dir and current_row not in index_text:
        problems.append(f"data_room_index.md does not label {current_dir} as current full render")
    stale_current = "rendered/full-20260618-0323` | 71 | Full current"
    if stale_current in index_text:
        problems.append("data_room_index.md labels full-20260618-0323 as current")
    return problems


def verify_directory_count_tables() -> list[str]:
    index_text = (BASE / "data_room_index.md").read_text(encoding="utf-8")
    problems: list[str] = []
    section: str | None = None
    for line in index_text.splitlines():
        if line.startswith("## Rendered Review Directories"):
            section = "rendered"
            continue
        if line.startswith("## Raw Data Directories"):
            section = "raw"
            continue
        if line.startswith("## Source Directories"):
            section = "source"
            continue
        if line.startswith("## ") and section:
            section = None
            continue
        if not section or not line.startswith("| `workspace/") or "---" in line:
            continue
        parts = [part.strip() for part in line.strip().strip("|").split("|")]
        if section in {"rendered", "raw"} and len(parts) >= 2:
            rel = parts[0].strip("`")
            listed = int(parts[1])
            directory = PROJECT_ROOT / rel
            actual = len([p for p in directory.rglob("*") if p.is_file()]) if directory.exists() else -1
            if actual != listed:
                problems.append(f"{rel}: listed {listed} files, actual {actual}")
        elif section == "source" and len(parts) >= 3:
            rel = parts[0].strip("`")
            listed_pdf = int(parts[1])
            listed_md = int(parts[2])
            directory = PROJECT_ROOT / rel
            actual_pdf = len(list(directory.rglob("*.pdf"))) if directory.exists() else -1
            actual_md = len(list(directory.rglob("*.md"))) if directory.exists() else -1
            if actual_pdf != listed_pdf or actual_md != listed_md:
                problems.append(
                    f"{rel}: listed pdf/md {listed_pdf}/{listed_md}, actual {actual_pdf}/{actual_md}"
                )
    required_source_dirs = [
        "sources/probe-current-customer-supplier-lists-20260618",
        "sources/probe-customer-annual-risk-disclosures-20260618",
        "sources/probe-customer-form-sd-20260618",
        "sources/probe-upstream-supplier-lists-20260618",
        "sources/probe-hyperscaler-capex-20260618",
    ]
    for rel in required_source_dirs:
        index_rel = f"workspace/research/semiconductor-pcb-20260612/{rel}"
        if index_rel not in index_text:
            problems.append(f"data_room_index.md missing source directory {index_rel}")
    return problems


def verify_completion_summary(
    completion: dict,
    refs: dict,
    data_room: dict,
    json_validity: dict,
    quality: dict,
    blocker_consistency: dict,
    path_leak: dict,
    rendered_inv: dict,
    request_pack_rows: int,
    request_pack_md_problems: list[str],
    ticker_matrix_count: int,
    blocker_coverage: dict,
    source_exhaustion_consistency: dict,
    audit_markdown_summary_problems: list[str],
    consistency_markdown_summary_problems: list[str],
    customer_recheck_summary_problems: list[str],
    verifier_gate_description_problems: list[str],
    checksums_count: int,
) -> list[str]:
    summary = completion.get("verifier_summary", {})
    expected = {
        "pdf_pages": quality.get("pages"),
        "pdf_creation_date": quality.get("pdf_creation_date"),
        "pdf_file_size": quality.get("pdf_file_size"),
        "path_leak_matches": path_leak.get("matches"),
        "evidence_references_checked": refs.get("checked_references"),
        "evidence_reference_problems": refs.get("problem_count"),
        "data_room_exists_rows_checked": data_room.get("exists_rows_checked"),
        "data_room_mismatches": data_room.get("mismatches"),
        "top_level_data_files_checked": data_room.get("top_level_data_files_checked"),
        "source_files_checked": data_room.get("source_files_checked"),
        "raw_data_files_checked": data_room.get("raw_data_files_checked"),
        "rendered_files_checked": data_room.get("rendered_files_checked"),
        "full_render_sequence_valid": rendered_inv.get("full_render_sequence_check", {}).get("valid"),
        "blocker_request_pack_aligned": blocker_consistency.get("aligned"),
        "request_pack_csv_rows": request_pack_rows,
        "request_pack_markdown_current": not request_pack_md_problems,
        "ticker_coverage_matrix_rows": ticker_matrix_count,
        "blocker_evidence_problem_count": blocker_coverage.get("problem_count"),
        "source_exhaustion_aligned": source_exhaustion_consistency.get("aligned"),
        "audit_markdown_summaries_current": not audit_markdown_summary_problems,
        "consistency_markdown_summaries_current": not consistency_markdown_summary_problems,
        "customer_recheck_summaries_current": not customer_recheck_summary_problems,
        "verifier_gate_descriptions_current": not verifier_gate_description_problems,
        "core_checksum_files": checksums_count,
        "json_validity_files_checked": json_validity.get("json_files_checked"),
        "json_validity_invalid_files": json_validity.get("invalid_json_files"),
        "json_validity_html_error_captures": json_validity.get("invalid_by_classification", {}).get("html_error_capture_with_json_extension"),
        "json_validity_truncated_captures": json_validity.get("invalid_by_classification", {}).get("truncated_or_incomplete_json_capture"),
    }
    problems: list[str] = []
    for key, value in expected.items():
        if summary.get(key) != value:
            problems.append(f"{key}: summary {summary.get(key)!r}!={value!r}")
    return problems


def verify_review_log_addendum() -> list[str]:
    review_log = (BASE / "review_log.md").read_text(encoding="utf-8")
    required_terms = [
        "2026-06-18 Current Final-State Addendum",
        "71-page PDF rebuilt at `Thu Jun 18 09:13:57 2026 CST`",
        "rendered/full-20260618-0913/",
        "tools/verify_research_workspace.py` now checks",
        "Explicit `Exists` rows: 263",
        "Top-level data files: 354",
        "Source files: 601",
        "Rendered files: 184",
        "Evidence references checked: 423",
        "Blocker evidence files checked: 64",
        "JSON files checked: 541",
        "blocked_by_unavailable_paid_or_non_public_data",
    ]
    return [f"review_log.md missing {term}" for term in required_terms if term not in review_log]


def verify_audit_markdown_summaries(refs: dict, blocker_coverage: dict, json_validity: dict) -> list[str]:
    problems: list[str] = []

    refs_md = (BASE / "data/evidence_reference_integrity_audit_20260618.md").read_text(encoding="utf-8")
    refs_terms = [
        f"**Checked references:** {refs.get('checked_references')}",
        f"**Problem count:** {refs.get('problem_count')}",
        str(refs.get("summary")),
        str(refs.get("boundary")),
    ]
    for term in refs_terms:
        if term not in refs_md:
            problems.append(f"evidence_reference_integrity_audit_20260618.md missing {term}")

    blocker_md = (BASE / "data/blocker_evidence_coverage_audit_20260618.md").read_text(encoding="utf-8")
    blocker_terms = [
        f"**Evidence files checked:** {blocker_coverage.get('evidence_files_checked')}",
        f"**Problem count:** {blocker_coverage.get('problem_count')}",
        str(blocker_coverage.get("boundary")),
    ]
    for row in blocker_coverage.get("rows", []):
        blocker_terms.append(
            f"| `{row['requirement']}` | {row['evidence_files']} | {row['covered']} | {row['problems']} |"
        )
    for term in blocker_terms:
        if term not in blocker_md:
            problems.append(f"blocker_evidence_coverage_audit_20260618.md missing {term}")

    json_md = (BASE / "data/json_validity_audit_20260618.md").read_text(encoding="utf-8")
    invalid_by_class = json_validity.get("invalid_by_classification", {})
    json_terms = [
        f"**JSON files checked:** {json_validity.get('json_files_checked')}",
        f"**Invalid JSON files:** {json_validity.get('invalid_json_files')}",
        f"**HTML error captures with `.json` extension:** {invalid_by_class.get('html_error_capture_with_json_extension')}",
        f"**Truncated or incomplete JSON captures:** {invalid_by_class.get('truncated_or_incomplete_json_capture')}",
        str(json_validity.get("boundary")),
    ]
    for term in json_terms:
        if term not in json_md:
            problems.append(f"json_validity_audit_20260618.md missing {term}")

    return problems


def verify_consistency_markdown_summaries(
    blocker_consistency: dict,
    source_exhaustion_consistency: dict,
    hygiene: dict,
    path_leak: dict,
    paid_access: dict,
) -> list[str]:
    problems: list[str] = []
    request_pack = load_json("missing_data_request_pack.json")

    blocker_md = (BASE / "data/blocker_request_pack_consistency_20260618.md").read_text(encoding="utf-8")
    expected_request_pack = {
        "request_pack_status": request_pack.get("status"),
        "public_sources_exhausted_through": request_pack.get("public_sources_exhausted_through"),
        "source_documents_needed_count": len(request_pack.get("source_documents_needed", [])),
        "completion_criteria_count": len(request_pack.get("completion_criteria", [])),
    }
    for key, expected in expected_request_pack.items():
        if blocker_consistency.get(key) != expected:
            problems.append(f"blocker_request_pack_consistency_20260618.json {key} {blocker_consistency.get(key)!r}!={expected!r}")
    blocker_terms = [
        f"**Aligned:** {blocker_consistency.get('aligned')}",
        f"Status | `{blocker_consistency.get('status')}` |",
        f"Request pack status | `{blocker_consistency.get('request_pack_status')}` |",
        f"Public sources exhausted through | `{blocker_consistency.get('public_sources_exhausted_through')}` |",
        f"Source documents needed count | {blocker_consistency.get('source_documents_needed_count')} |",
        f"Completion criteria count | {blocker_consistency.get('completion_criteria_count')} |",
        str(blocker_consistency.get("boundary")),
    ]
    for blocker_id in blocker_consistency.get("blocker_ids", []):
        blocker_terms.append(str(blocker_id))
    for request_id in blocker_consistency.get("request_pack_ids", []):
        blocker_terms.append(str(request_id))
    for term in blocker_terms:
        if term not in blocker_md:
            problems.append(f"blocker_request_pack_consistency_20260618.md missing {term}")

    source_md = (BASE / "data/source_exhaustion_consistency_20260618.md").read_text(encoding="utf-8")
    source_terms = [
        f"**Aligned:** {source_exhaustion_consistency.get('aligned')}",
        f"| Sections | {source_exhaustion_consistency.get('md_section_count')} | {source_exhaustion_consistency.get('json_section_count')} | {source_exhaustion_consistency.get('checks', {}).get('section_count_match')} |",
        f"| Rows | {source_exhaustion_consistency.get('md_row_count')} | {source_exhaustion_consistency.get('json_row_count')} | {source_exhaustion_consistency.get('checks', {}).get('row_count_match')} |",
        f"| Unique evidence refs | {source_exhaustion_consistency.get('md_unique_evidence_refs')} | {source_exhaustion_consistency.get('json_unique_evidence_refs')} | {source_exhaustion_consistency.get('checks', {}).get('unique_refs_match')} |",
        str(source_exhaustion_consistency.get("boundary")),
    ]
    for term in source_terms:
        if term not in source_md:
            problems.append(f"source_exhaustion_consistency_20260618.md missing {term}")

    hygiene_md = (BASE / "data/pdf_text_hygiene_check_20260618.md").read_text(encoding="utf-8")
    hygiene_terms = [
        f"**Result:** {hygiene.get('result')}",
        f"**Total matches:** {hygiene.get('total_matches')}",
    ]
    for pattern, count in hygiene.get("matches_by_pattern", {}).items():
        hygiene_terms.append(f"| `{pattern}` | {count} |")
    for term in hygiene_terms:
        if term not in hygiene_md:
            problems.append(f"pdf_text_hygiene_check_20260618.md missing {term}")

    path_md = (BASE / "data/pdf_path_leakage_check_20260618.md").read_text(encoding="utf-8")
    path_terms = [f"**Matches:** {path_leak.get('matches')}"]
    for pattern, count in path_leak.get("matches_by_pattern", {}).items():
        path_terms.append(f"| `{pattern}` | {count} |")
    for term in path_terms:
        if term not in path_md:
            problems.append(f"pdf_path_leakage_check_20260618.md missing {term}")

    paid_md = (BASE / "data/paid_access_recheck_20260618.md").read_text(encoding="utf-8")
    for module in paid_access.get("modules", []):
        expected_status = "available" if module.get("available") else "unavailable"
        if module.get("available"):
            expected_row = f"| {module['module']} | {expected_status} | {module.get('version')} |"
        else:
            expected_row = f"| {module['module']} | {expected_status} | not installed / not found |"
        if expected_row not in paid_md:
            problems.append(f"paid_access_recheck_20260618.md missing {expected_row}")
    paid_terms = [
        str(paid_access.get("home_config_search")).replace(
            "No market-data credential files found; only false positives for wind/window/tailwind/unwind paths.",
            "Home-directory config search found no market-data or customs/BOL credential files.",
        ),
        str(paid_access.get("boundary")),
    ]
    for term in paid_terms:
        if term not in paid_md:
            problems.append(f"paid_access_recheck_20260618.md missing {term}")

    return problems


def verify_customer_recheck_summaries(current_lists: dict, annual_risk: dict, form_sd: dict) -> list[str]:
    problems: list[str] = []

    current_md = (BASE / "data/current_customer_supplier_list_recheck_20260618.md").read_text(encoding="utf-8")
    current_terms = [
        current_lists.get("raw_archive"),
        "Open Supply Hub list id `3316`",
        "March 2026 review date",
        "Dell current public supplier list",
        "Tripod, Gold Circuit, Hannstar and Delton",
        current_lists.get("remaining_gap"),
    ]
    for source in current_lists.get("sources", []):
        if source.get("archive"):
            current_terms.append(Path(source["archive"]).name)
        if source.get("text"):
            current_terms.append(Path(source["text"]).name)
    for term in current_terms:
        if term and str(term) not in current_md:
            problems.append(f"current_customer_supplier_list_recheck_20260618.md missing {term}")

    annual_md = (BASE / "data/customer_annual_risk_disclosure_recheck_20260618.md").read_text(encoding="utf-8")
    annual_terms = [
        annual_risk.get("raw_archive"),
        "manufacturing purchase obligations of USD56.2bn",
        "purchase commitments of USD149.1bn",
        "purchase commitments of USD109.953bn",
        "purchase obligations of USD18.8bn",
        annual_risk.get("targeted_absence_checks", {}).get("result"),
        annual_risk.get("remaining_gap"),
    ]
    for source in annual_risk.get("sources", []):
        for key in ("filing", "text", "excerpt", "submissions_json"):
            if source.get(key):
                annual_terms.append(Path(source[key]).name)
    for term in annual_terms:
        if term and str(term) not in annual_md:
            problems.append(f"customer_annual_risk_disclosure_recheck_20260618.md missing {term}")

    form_sd_md = (BASE / "data/customer_form_sd_conflict_minerals_recheck_20260618.md").read_text(encoding="utf-8")
    form_sd_terms = [
        form_sd.get("raw_archive"),
        "Microsoft surveyed 79 Devices direct suppliers with a 100% CMRT response rate",
        "Dell covered branded hardware, peripherals, server, storage and networking products",
        "NVIDIA discloses a fabless and contract-manufacturing strategy",
        "surveyed 164 direct suppliers",
        "identified 246 processing facilities",
        "Alphabet external page probe",
        "returned HTTP 403",
        form_sd.get("targeted_absence_checks", {}).get("result"),
        form_sd.get("remaining_gap"),
    ]
    for source in form_sd.get("sources", []):
        for key in ("filing", "exhibit", "text", "submissions_json", "external_page_probe"):
            if source.get(key):
                form_sd_terms.append(Path(source[key]).name)
    for artifact in form_sd.get("excluded_artifacts", []):
        if artifact.get("path"):
            form_sd_terms.append(Path(artifact["path"]).name)
        if artifact.get("reason"):
            form_sd_terms.append(artifact["reason"])
    for term in form_sd_terms:
        if term and str(term) not in form_sd_md:
            problems.append(f"customer_form_sd_conflict_minerals_recheck_20260618.md missing {term}")

    return problems


def verify_verifier_gate_descriptions() -> list[str]:
    source_exhaustion_json = load_json("source_exhaustion_log.json")
    source_exhaustion_json_text = json.dumps(source_exhaustion_json, ensure_ascii=False)
    data_room_json = load_json("data/data_room_index_integrity_audit_20260618.json")
    data_room_gates = data_room_json.get("enhanced_gates", [])
    files_and_terms = {
        "completion_audit_manifest.md": [
            "ticker coverage matrix alignment",
            "audit Markdown summaries",
            "consistency Markdown summaries",
            "customer recheck Markdown summaries",
            "Markdown/JSON summary alignment",
        ],
        "source_exhaustion_log.md": [
            "ticker coverage matrix alignment",
            "audit Markdown summaries",
            "consistency Markdown summaries",
            "customer recheck Markdown summaries",
        ],
        "source_exhaustion_log.json": [
            "ticker coverage matrix alignment",
            "audit Markdown summaries",
            "consistency Markdown summaries",
            "customer recheck Markdown summaries",
        ],
        "data/data_room_index_integrity_audit_20260618.md": [
            "Ticker coverage matrix alignment",
            "audit Markdown summaries",
            "consistency Markdown summaries",
            "customer recheck Markdown summaries",
        ],
        "data/data_room_index_integrity_audit_20260618.json": [
            "current full render validity",
            "inventory mismatch fields and mismatch_details",
            "core artifact checksums and checksum Markdown alignment",
            "request-pack CSV/JSON mirroring",
            "source-registry/template handoff terms",
            "ticker coverage matrix alignment",
            "audit Markdown summaries",
            "consistency Markdown summaries",
            "customer recheck Markdown summaries",
        ],
        "review_log.md": [
            "ticker coverage matrix alignment",
            "audit Markdown summaries",
            "consistency Markdown summaries",
            "customer recheck Markdown summaries",
        ],
    }
    problems: list[str] = []
    for rel, terms in files_and_terms.items():
        if rel == "source_exhaustion_log.json":
            text = source_exhaustion_json_text
        elif rel == "data/data_room_index_integrity_audit_20260618.json":
            text = "\n".join(str(gate) for gate in data_room_gates)
        else:
            text = (BASE / rel).read_text(encoding="utf-8")
        for term in terms:
            if term not in text:
                problems.append(f"{rel} missing verifier gate description {term}")
    return problems


def main() -> int:
    checks: list[tuple[str, bool, str]] = []

    unresolved = load_json("unresolved_requirements.json")
    completion = load_json("completion_audit_manifest.json")
    data_room = load_json("data/data_room_index_integrity_audit_20260618.json")
    refs = load_json("data/evidence_reference_integrity_audit_20260618.json")
    root_inv = load_json("data/root_artifact_inventory_20260618.json")
    data_inv = load_json("data/top_level_data_artifact_inventory_20260618.json")
    source_inv = load_json("data/source_artifact_inventory_20260618.json")
    raw_inv = load_json("data/raw_data_artifact_inventory_20260618.json")
    rendered_inv = load_json("data/rendered_artifact_inventory_20260618.json")
    hygiene = load_json("data/pdf_text_hygiene_check_20260618.json")
    path_leak = load_json("data/pdf_path_leakage_check_20260618.json")
    checksums_count, checksum_problems = verify_checksums()
    request_pack_rows, request_pack_problems = verify_request_pack_csv()
    request_pack_md_problems = verify_request_pack_markdown()
    handoff_term_problems = verify_handoff_terms()
    root_inventory_count, root_inventory_problems = verify_root_inventory()
    data_inventory_count, data_inventory_problems = verify_top_level_data_inventory()
    source_inventory_count, source_inventory_problems = verify_source_inventory()
    raw_inventory_count, raw_inventory_problems = verify_simple_inventory(
        "data/raw_data_artifact_inventory_20260618.json",
        "data/raw_data_artifact_inventory_20260618.md",
        "data",
        "raw_data_files",
    )
    rendered_inventory_count, rendered_inventory_problems = verify_simple_inventory(
        "data/rendered_artifact_inventory_20260618.json",
        "data/rendered_artifact_inventory_20260618.md",
        "rendered",
        "rendered_files",
    )
    ticker_matrix_count, ticker_matrix_problems = verify_ticker_matrix()
    render_index_problems = verify_render_directory_index(rendered_inv)
    directory_count_problems = verify_directory_count_tables()

    json_validity = load_json("data/json_validity_audit_20260618.json")
    quality = load_json("data/report_quality_eval.json")
    blocker_consistency = load_json("data/blocker_request_pack_consistency_20260618.json")
    blocker_coverage = load_json("data/blocker_evidence_coverage_audit_20260618.json")
    source_exhaustion_consistency = load_json("data/source_exhaustion_consistency_20260618.json")
    paid_access = load_json("data/paid_access_recheck_20260618.json")
    current_lists = load_json("data/current_customer_supplier_list_recheck_20260618.json")
    annual_risk = load_json("data/customer_annual_risk_disclosure_recheck_20260618.json")
    form_sd = load_json("data/customer_form_sd_conflict_minerals_recheck_20260618.json")
    review_log_problems = verify_review_log_addendum()
    audit_markdown_summary_problems = verify_audit_markdown_summaries(
        refs,
        blocker_coverage,
        json_validity,
    )
    consistency_markdown_summary_problems = verify_consistency_markdown_summaries(
        blocker_consistency,
        source_exhaustion_consistency,
        hygiene,
        path_leak,
        paid_access,
    )
    customer_recheck_summary_problems = verify_customer_recheck_summaries(
        current_lists,
        annual_risk,
        form_sd,
    )
    verifier_gate_description_problems = verify_verifier_gate_descriptions()
    completion_summary_problems = verify_completion_summary(
        completion,
        refs,
        data_room,
        json_validity,
        quality,
        blocker_consistency,
        path_leak,
        rendered_inv,
        request_pack_rows,
        request_pack_md_problems,
        ticker_matrix_count,
        blocker_coverage,
        source_exhaustion_consistency,
        audit_markdown_summary_problems,
        consistency_markdown_summary_problems,
        customer_recheck_summary_problems,
        verifier_gate_description_problems,
        checksums_count,
    )

    exists_rows, exists_mismatches = count_exists_rows()
    checks.append(("exists row count matches audit", exists_rows == data_room.get("exists_rows_checked"), f"actual={exists_rows} audit={data_room.get('exists_rows_checked')}"))
    checks.append(("exists row mismatches zero", exists_mismatches == data_room.get("mismatches") == 0, f"actual={exists_mismatches} audit={data_room.get('mismatches')}"))

    checks.append(("root files count", len([p for p in BASE.iterdir() if p.is_file()]) == root_inv.get("root_files"), str(root_inv.get("root_files"))))
    checks.append(("root inventory sizes", not root_inventory_problems and root_inventory_count == root_inv.get("root_files"), f"files={root_inventory_count} problems={len(root_inventory_problems)}"))
    checks.append(("top-level data files count", len([p for p in (BASE / "data").iterdir() if p.is_file()]) == data_inv.get("top_level_data_files"), str(data_inv.get("top_level_data_files"))))
    checks.append(("top-level data inventory sizes", not data_inventory_problems and data_inventory_count == data_inv.get("top_level_data_files"), f"files={data_inventory_count} problems={len(data_inventory_problems)}"))
    checks.append(("source files count", len([p for p in (BASE / "sources").rglob("*") if p.is_file()]) == source_inv.get("source_files"), str(source_inv.get("source_files"))))
    checks.append(("source inventory sizes", not source_inventory_problems and source_inventory_count == source_inv.get("source_files"), f"files={source_inventory_count} problems={len(source_inventory_problems)}"))
    checks.append(("raw data files count", len([p for p in (BASE / "data").glob("raw_*") if p.is_dir() for p in p.rglob("*") if p.is_file()]) == raw_inv.get("raw_data_files"), str(raw_inv.get("raw_data_files"))))
    checks.append(("raw data inventory sizes", not raw_inventory_problems and raw_inventory_count == raw_inv.get("raw_data_files"), f"files={raw_inventory_count} problems={len(raw_inventory_problems)}"))
    checks.append(("rendered files count", len([p for p in (BASE / "rendered").rglob("*") if p.is_file()]) == rendered_inv.get("rendered_files"), str(rendered_inv.get("rendered_files"))))
    checks.append(("rendered inventory sizes", not rendered_inventory_problems and rendered_inventory_count == rendered_inv.get("rendered_files"), f"files={rendered_inventory_count} problems={len(rendered_inventory_problems)}"))
    inventory_mismatch_fields = [
        "top_level_report_artifacts_missing_from_index",
        "top_level_data_files_missing_from_inventory",
        "top_level_data_inventory_extra_files",
        "top_level_data_inventory_size_mismatches",
        "source_files_missing_from_inventory",
        "source_inventory_extra_files",
        "source_inventory_size_mismatches",
        "rendered_files_missing_from_inventory",
        "rendered_inventory_extra_files",
        "rendered_inventory_size_mismatches",
        "raw_data_files_missing_from_inventory",
        "raw_data_inventory_extra_files",
        "raw_data_inventory_size_mismatches",
        "source_directory_count_mismatches",
    ]
    inventory_problem_total = sum(int(data_room.get(field, 0) or 0) for field in inventory_mismatch_fields)
    checks.append(("inventory mismatch fields zero", inventory_problem_total == 0 and not data_room.get("mismatch_details"), f"problem_total={inventory_problem_total} details={len(data_room.get('mismatch_details', []))}"))
    checks.append(("data-room directory count tables", not directory_count_problems, f"problems={len(directory_count_problems)}"))
    full_render = rendered_inv.get("full_render_sequence_check", {})
    checks.append(("current full render valid", full_render.get("valid") is True and full_render.get("actual_pages") == quality.get("pages"), f"{full_render.get('directory')} pages={full_render.get('actual_pages')} valid={full_render.get('valid')}"))
    checks.append(("render directory index current", not render_index_problems, f"problems={len(render_index_problems)}"))

    checks.append(("completion decision", completion.get("decision") == "do_not_mark_complete", str(completion.get("decision"))))
    checks.append(("completion verifier summary", not completion_summary_problems, f"problems={len(completion_summary_problems)}"))
    checks.append(("review log current addendum", not review_log_problems, f"problems={len(review_log_problems)}"))
    checks.append(("unresolved status", unresolved.get("status") == "blocked_by_unavailable_paid_or_non_public_data", str(unresolved.get("status"))))
    checks.append(("evidence reference problems", refs.get("problem_count") == 0, str(refs.get("problem_count"))))
    checks.append(("blocker request pack aligned", blocker_consistency.get("aligned") is True, str(blocker_consistency.get("aligned"))))
    checks.append(("request pack CSV mirrors JSON", not request_pack_problems and request_pack_rows == 3, f"rows={request_pack_rows} problems={len(request_pack_problems)}"))
    checks.append(("request pack Markdown current", not request_pack_md_problems, f"problems={len(request_pack_md_problems)}"))
    checks.append(("handoff registry/template terms", not handoff_term_problems, f"problems={len(handoff_term_problems)}"))
    checks.append(("ticker coverage matrix", not ticker_matrix_problems and ticker_matrix_count == 12, f"rows={ticker_matrix_count} problems={len(ticker_matrix_problems)}"))
    checks.append(("blocker evidence coverage", blocker_coverage.get("problem_count") == 0, str(blocker_coverage.get("problem_count"))))
    checks.append(("source exhaustion consistency", source_exhaustion_consistency.get("aligned") is True, str(source_exhaustion_consistency.get("aligned"))))
    checks.append(("audit Markdown summaries current", not audit_markdown_summary_problems, f"problems={len(audit_markdown_summary_problems)}"))
    checks.append(("consistency Markdown summaries current", not consistency_markdown_summary_problems, f"problems={len(consistency_markdown_summary_problems)}"))
    checks.append(("customer recheck summaries current", not customer_recheck_summary_problems, f"problems={len(customer_recheck_summary_problems)}"))
    checks.append(("verifier gate descriptions current", not verifier_gate_description_problems, f"problems={len(verifier_gate_description_problems)}"))
    checks.append(("pdf text hygiene", hygiene.get("result") == "pass" and hygiene.get("total_matches") == 0, f"{hygiene.get('result')} matches={hygiene.get('total_matches')}"))
    checks.append(("pdf path leakage", path_leak.get("matches") == 0, str(path_leak.get("matches"))))
    checks.append(("core checksum manifest", not checksum_problems and checksums_count == 14, f"files={checksums_count} problems={len(checksum_problems)}"))
    checks.append(("report quality pages", quality.get("pages") >= 71, str(quality.get("pages"))))
    checks.append(("json validity audit", json_validity.get("invalid_json_files") == 14 and json_validity.get("invalid_by_classification", {}).get("html_error_capture_with_json_extension") == 13 and json_validity.get("invalid_by_classification", {}).get("truncated_or_incomplete_json_capture") == 1, f"invalid={json_validity.get('invalid_json_files')}"))

    pdfinfo = subprocess.check_output(["pdfinfo", str(BASE / "main.pdf")], text=True)
    checks.append(("pdfinfo pages", f"Pages:           {quality.get('pages')}" in pdfinfo, f"Pages: {quality.get('pages')}"))
    checks.append(("pdfinfo creation date", str(quality.get("pdf_creation_date")) in pdfinfo, f"CreationDate {quality.get('pdf_creation_date')}"))

    failures = [(name, detail) for name, ok, detail in checks if not ok]
    for name, ok, detail in checks:
        status = "PASS" if ok else "FAIL"
        print(f"{status}: {name} ({detail})")

    if failures:
        print("\nFailures:")
        for name, detail in failures:
            print(f"- {name}: {detail}")
        if checksum_problems:
            print("\nChecksum problems:")
            for problem in checksum_problems:
                print(f"- {problem}")
        if request_pack_problems:
            print("\nRequest pack CSV problems:")
            for problem in request_pack_problems:
                print(f"- {problem}")
        if request_pack_md_problems:
            print("\nRequest pack Markdown problems:")
            for problem in request_pack_md_problems:
                print(f"- {problem}")
        if handoff_term_problems:
            print("\nHandoff term problems:")
            for problem in handoff_term_problems:
                print(f"- {problem}")
        if root_inventory_problems:
            print("\nRoot inventory problems:")
            for problem in root_inventory_problems:
                print(f"- {problem}")
        if data_inventory_problems:
            print("\nTop-level data inventory problems:")
            for problem in data_inventory_problems:
                print(f"- {problem}")
        if source_inventory_problems:
            print("\nSource inventory problems:")
            for problem in source_inventory_problems:
                print(f"- {problem}")
        if raw_inventory_problems:
            print("\nRaw data inventory problems:")
            for problem in raw_inventory_problems:
                print(f"- {problem}")
        if rendered_inventory_problems:
            print("\nRendered inventory problems:")
            for problem in rendered_inventory_problems:
                print(f"- {problem}")
        if ticker_matrix_problems:
            print("\nTicker matrix problems:")
            for problem in ticker_matrix_problems:
                print(f"- {problem}")
        if render_index_problems:
            print("\nRender directory index problems:")
            for problem in render_index_problems:
                print(f"- {problem}")
        if directory_count_problems:
            print("\nDirectory count table problems:")
            for problem in directory_count_problems:
                print(f"- {problem}")
        if completion_summary_problems:
            print("\nCompletion summary problems:")
            for problem in completion_summary_problems:
                print(f"- {problem}")
        if review_log_problems:
            print("\nReview log problems:")
            for problem in review_log_problems:
                print(f"- {problem}")
        if audit_markdown_summary_problems:
            print("\nAudit Markdown summary problems:")
            for problem in audit_markdown_summary_problems:
                print(f"- {problem}")
        if consistency_markdown_summary_problems:
            print("\nConsistency Markdown summary problems:")
            for problem in consistency_markdown_summary_problems:
                print(f"- {problem}")
        if customer_recheck_summary_problems:
            print("\nCustomer recheck summary problems:")
            for problem in customer_recheck_summary_problems:
                print(f"- {problem}")
        if verifier_gate_description_problems:
            print("\nVerifier gate description problems:")
            for problem in verifier_gate_description_problems:
                print(f"- {problem}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
