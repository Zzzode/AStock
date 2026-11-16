#!/usr/bin/env python3
"""Capture public primary-source pages that describe C19 candidate data paths."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
OUTPUT_DIR = CASE_DIR / "sources" / "c19-official-bond-data-source-feasibility-20260815"
MANIFEST_PATH = OUTPUT_DIR / "manifest.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c19_bond_historical_data_source_feasibility_20260815.json"
SOURCES = (
    {
        "source_key": "sseinfo_historical_market_data_product",
        "filename": "sseinfo_historical_market_data_product.html",
        "url": "https://www.sseinfo.com/services/assortment/historical/",
        "publisher": "SSE InfoNet",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "sseinfo_historical_data_interface_specification",
        "filename": "sseinfo_historical_data_interface_specification.pdf",
        "url": "https://www.sseinfo.com/services/assortment/document/interface/c/10759166/files/4f38cae1022a4cfa8410bbc2702e2b95.pdf",
        "publisher": "SSE InfoNet",
        "expected_content_prefix": "application/pdf",
    },
    {
        "source_key": "sseinfo_fixed_income_market_data_product",
        "filename": "sseinfo_fixed_income_market_data_product.html",
        "url": "https://www.sseinfo.com/services/assortment/income/",
        "publisher": "SSE InfoNet",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "chinabond_valuation_query_surface",
        "filename": "chinabond_valuation_query_surface.html",
        "url": "https://indices.chinabond.com.cn/cbweb-mn/val/val_query_list?locale=zh_CN",
        "publisher": "ChinaBond",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "chinabond_yield_methodology_surface",
        "filename": "chinabond_yield_methodology_surface.html",
        "url": "https://valuation.chinabond.com.cn/cbweb-mn/int/int_yield_syl_doc",
        "publisher": "ChinaBond",
        "expected_content_prefix": "text/html",
    },
    {
        "source_key": "sseinfo_authorization_statement",
        "filename": "sseinfo_authorization_statement.html",
        "url": "https://www.sseinfo.com/aboutus/authstatement/",
        "publisher": "SSE InfoNet",
        "expected_content_prefix": "text/html",
    },
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def capture() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []
    for source in SOURCES:
        request = Request(str(source["url"]), headers={"User-Agent": "AStock-research-source-capture/1.0"})
        with urlopen(request, timeout=45) as response:  # noqa: S310 -- fixed HTTPS primary-source URLs.
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
                "sha256": digest(path),
            }
        )
    manifest = {
        "schema_version": "c19_primary_source_capture.v1",
        "capture_id": "D5PT-C19-SOURCE-CAPTURE-v1",
        "purpose": "Preserve public primary-source descriptions of candidate lawful data paths; no license, extract, entitlement or historical test data is represented.",
        "records": records,
        "boundary": "These public pages only document potential products, field concepts and rights boundaries. They are not acquired historical bond data, a use-right grant, an eligibility record or a performance input.",
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"C19 source capture: PASS ({len(records)} records)")
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
        if path.stat().st_size != record.get("bytes") or digest(path) != record.get("sha256"):
            failures.append(f"hash mismatch {path.name}")
    feasibility = json.loads(FEASIBILITY_PATH.read_text(encoding="utf-8"))
    control = feasibility.get("source_control", {}).get("primary_source_capture_manifest", {})
    if control.get("path") != str(MANIFEST_PATH.relative_to(REPO_ROOT)):
        failures.append("feasibility manifest path mismatch")
    if control.get("sha256") != digest(MANIFEST_PATH):
        failures.append("feasibility manifest hash mismatch")
    if feasibility.get("current_route_status") != "not_testable":
        failures.append("C19 testability boundary changed")
    if feasibility.get("research_only") is not True or feasibility.get("formal_decision_eligible") is not False or feasibility.get("external_orders") is not False:
        failures.append("C19 action boundary changed")
    state = "PASS" if not failures else "FAIL"
    print(f"C19 source capture verification: {state}")
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
