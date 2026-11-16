#!/usr/bin/env python3
"""Capture linked primary rule-text attachments missing from C18's first batch.

This is an immutable source-control augmentation.  It preserves the initial
preflight batch and does not add a bond universe, historical data, result or
external action.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c18-official-sse-company-bond-rule-text-augmentation-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
SOURCES = (
    {
        "source_key": "sse_company_bond_listing_rule_body",
        "filename": "sse_company_bond_listing_rule_20231020.docx",
        "title": "Shanghai Stock Exchange Company Bond Listing Rules (2023 revision), rule text attachment",
        "publisher": "Shanghai Stock Exchange",
        "document_date": "2023-10-20",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/listing/corporatebond/c/10779480/files/19830feba95f4053910eb9bbf994a703.docx",
    },
    {
        "source_key": "sse_company_bond_credit_risk_rule_body",
        "filename": "sse_company_bond_credit_risk_management_rule_20231020.docx",
        "title": "Shanghai Stock Exchange Self-Regulatory Guideline No. 4: Credit Risk Management for Company Bonds and Asset-Backed Securities, rule text attachment",
        "publisher": "Shanghai Stock Exchange",
        "document_date": "2023-10-20",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/listing/corporatebond/c/10780814/files/ba835303bc0a40119745ed67abd365eb.docx",
    },
)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def _fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "AStock research evidence capture/1.0"})
    with urlopen(request, timeout=45) as response:
        raw = response.read()
    if not raw or b"safeline_bot_challenge" in raw or b"WEB \xe5\xba\x94\xe7\x94\xa8\xe9\x98\xb2\xe7\x81\xab\xe5\xa2\x99" in raw:
        raise ValueError(f"refusing empty or WAF response: {url}")
    return raw


def _repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _capture() -> int:
    if MANIFEST_PATH.exists():
        raise RuntimeError(f"refusing to overwrite immutable source augmentation: {MANIFEST_PATH}")
    SOURCE_DIR.mkdir(parents=True, exist_ok=False)
    captured_at = datetime.now(timezone.utc).isoformat()
    records: list[dict[str, object]] = []
    for source in SOURCES:
        raw = _fetch(str(source["url"]))
        path = SOURCE_DIR / str(source["filename"])
        _write(path, raw)
        records.append(
            {
                "source_key": source["source_key"],
                "path": _repo_path(path),
                "url": source["url"],
                "title": source["title"],
                "publisher": source["publisher"],
                "document_date": source["document_date"],
                "retrieved_at": captured_at,
                "bytes": len(raw),
                "sha256": _sha256(raw),
                "capture_note": "First-party rule-text attachment captured to complete the source-control chain. It supplies rule text only; it does not establish historic bond eligibility, price, cash flow, credit quality, execution or an action.",
            }
        )
    manifest = {
        "schema_version": "c18_sse_company_bond_rule_text_augmentation_manifest.v1",
        "capture_batch": "c18-official-sse-company-bond-rule-text-augmentation-20260815",
        "case_id": CASE_DIR.name,
        "captured_at": captured_at,
        "source_quality": "dated_primary_exchange_rule_text",
        "purpose": "Add the linked SSE listing and credit-risk rule-text attachments absent from the initial C18 preflight batch without changing its data or action boundary.",
        "records": records,
        "limitations": [
            "The attachments are current rule texts, not historic point-in-time bond masters, prices, cash flows, ratings, credit events, broker records or settlement evidence.",
            "They do not establish bond-specific or person-specific suitability, availability, performance or an external action.",
        ],
    }
    _write(MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(f"C18 rule-text augmentation: {len(records)} files")
    return 0


def _verify() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    expected_keys = {str(source["source_key"]) for source in SOURCES}
    records = {str(row.get("source_key")): row for row in manifest.get("records", []) if isinstance(row, dict)}
    if set(records) != expected_keys:
        failures.append("source-key coverage differs")
    for key, record in records.items():
        path = REPO_ROOT / str(record.get("path"))
        if not path.is_file() or _sha256(path.read_bytes()) != record.get("sha256"):
            failures.append(f"source hash mismatch: {key}")
    state = "PASS" if not failures else "FAIL"
    print(f"C18 RULE-TEXT AUGMENTATION: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    return _verify() if arguments.verify_only else _capture()


if __name__ == "__main__":
    raise SystemExit(main())
