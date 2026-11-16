#!/usr/bin/env python3
"""Capture current SSE public-REIT rule pages and the referenced rule bodies for C20."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
OUTPUT_DIR = CASE_DIR / "sources" / "c20-current-sse-rule-text-20260815"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c20_domestic_public_reit_strategy_feasibility_20260815.json"
SOURCES = (
    {
        "source_key": "sse_current_reit_business_rule_announcement",
        "filename": "sse_current_reit_business_rule_announcement_20251231.html",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/reits/c/c_20251231_10803729.shtml",
        "publisher": "Shanghai Stock Exchange",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "sse_current_reit_business_rule_body",
        "filename": "sse_current_reit_business_rule_20251231.docx",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/reits/c/10803729/files/b257f7fd523949308787c3e6d4b5b5f9.docx",
        "publisher": "Shanghai Stock Exchange",
        "expected_content_prefix": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
    {
        "source_key": "sse_repeal_notice_for_2021_reit_rule",
        "filename": "sse_repeal_notice_for_2021_reit_rule_20250609.html",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/repeal/rules/c/c_20250609_10804035.shtml",
        "publisher": "Shanghai Stock Exchange",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "sse_reit_investor_education_material",
        "filename": "sse_reit_investor_education_material.pdf",
        "url": "https://edu.sse.com.cn/REITS/document/c/10608582/files/1b8f787ec537440db979406640606415.pdf",
        "publisher": "Shanghai Stock Exchange",
        "expected_content_prefix": "application/pdf",
    },
    {
        "source_key": "sse_current_trading_rule_announcement",
        "filename": "sse_current_trading_rule_announcement_20260424.html",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/c_20260424_10816482.shtml",
        "publisher": "Shanghai Stock Exchange",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "sse_current_trading_rule_body",
        "filename": "sse_current_trading_rule_20260424.docx",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/stocks/exchange/c/10816482/files/959da0158c65434daa8a43a6e32be7ba.docx",
        "publisher": "Shanghai Stock Exchange",
        "expected_content_prefix": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    },
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for source in SOURCES:
        request = Request(str(source["url"]), headers={"User-Agent": "AStock-research-source-capture/1.0"})
        with urlopen(request, timeout=45) as response:  # noqa: S310 -- fixed HTTPS exchange URLs.
            body = response.read()
            content_type = str(response.headers.get_content_type() or "")
            status = int(getattr(response, "status", 200))
            final_url = str(response.geturl())
        expected = str(source["expected_content_prefix"])
        if status != 200 or not content_type.startswith(expected) or not body:
            raise RuntimeError(f"unexpected response for {source['source_key']}: {status} {content_type}")
        path = OUTPUT_DIR / str(source["filename"])
        path.write_bytes(body)
        records.append(
            {
                **source,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "final_url": final_url,
                "http_status": status,
                "content_type": content_type,
                "bytes": len(body),
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema_version": "c20_current_sse_rule_text_capture.v1",
        "capture_id": "D5PT-C20-CURRENT-RULE-CAPTURE-v1",
        "purpose": "Retain the current SSE rule pages and their referenced rule bodies used for C20 rule-version and general-mechanics context.",
        "records": records,
        "boundary": "The capture proves only the retained rule text and metadata. It does not establish rule continuity for every prior date, a specific investor's eligibility, cost, liquidity, fill or settlement outcome, a product selection, a return result or an action.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"C20 current-rule source capture: PASS ({len(records)} records)")
    return 0


def verify() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    records = manifest.get("records", [])
    if not isinstance(records, list) or len(records) != len(SOURCES):
        failures.append("unexpected record count")
    expected_keys = {str(item["source_key"]) for item in SOURCES}
    actual_keys = {str(item.get("source_key")) for item in records if isinstance(item, dict)}
    if actual_keys != expected_keys:
        failures.append("source key set mismatch")
    for record in records:
        if not isinstance(record, dict):
            failures.append("invalid record")
            continue
        path = OUTPUT_DIR / str(record.get("filename") or "")
        if not path.is_file():
            failures.append(f"missing {path.name}")
            continue
        if path.stat().st_size != record.get("bytes") or sha256(path) != record.get("sha256"):
            failures.append(f"hash mismatch {path.name}")
    feasibility = json.loads(FEASIBILITY_PATH.read_text(encoding="utf-8"))
    control = feasibility.get("source_control", {}).get("current_rule_capture_manifest", {})
    if control.get("path") != str(MANIFEST_PATH.relative_to(REPO_ROOT)):
        failures.append("feasibility manifest path mismatch")
    if control.get("sha256") != sha256(MANIFEST_PATH):
        failures.append("feasibility manifest hash mismatch")
    if feasibility.get("scope_control", {}).get("return_test_run") is not False or feasibility.get("scope_control", {}).get("return_result") is not None:
        failures.append("C20 return-test boundary changed")
    current = feasibility.get("current_disposition", {})
    if current.get("state") != "NO_STRATEGY_TEST_ADMISSION_NO_PRODUCT_SELECTION_NO_ACTION":
        failures.append("C20 no-action disposition changed")
    state = "PASS" if not failures else "FAIL"
    print(f"C20 current-rule source capture verification: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    return verify() if args.verify_only else capture()


if __name__ == "__main__":
    raise SystemExit(main())
