#!/usr/bin/env python3
"""Capture primary SSE/CSRC sources for the C18 company-bond feasibility route.

The capture is a legal and data-availability preflight only.  It does not
select a bond, infer investor eligibility, calculate a return or create an
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
SOURCE_DIR = CASE_DIR / "sources" / "c18-official-sse-company-bond-feasibility-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
SOURCES = (
    {
        "source_key": "sse_company_bond_listing_rule",
        "filename": "sse_company_bond_listing_rule_20231020.html",
        "title": "Shanghai Stock Exchange Company Bond Listing Rules (2023 revision)",
        "publisher": "Shanghai Stock Exchange",
        "document_date": "2023-10-20",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/listing/corporatebond/c/c_20250520_10779480.shtml",
    },
    {
        "source_key": "sse_bond_investor_suitability_rule",
        "filename": "sse_bond_investor_suitability_rule_20231020.docx",
        "title": "Shanghai Stock Exchange Bond-Market Investor Suitability Management Measures (2023 revision)",
        "publisher": "Shanghai Stock Exchange",
        "document_date": "2023-10-20",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/trading/currency/c/10781044/files/6b56460dbbc344ec847beed5acedf76a.docx",
    },
    {
        "source_key": "csrc_company_bond_administration_measure",
        "filename": "csrc_company_bond_issuance_and_trading_measure_20210226.pdf",
        "title": "CSRC Company Bond Issuance and Trading Administration Measure",
        "publisher": "China Securities Regulatory Commission",
        "document_date": "2021-02-26",
        "url": "https://www.sse.com.cn/lawandrules/regulations/csrcorder/c/10747815/files/4030433c068d42eeaaf90845b23d8bc8.pdf",
    },
    {
        "source_key": "sse_company_bond_credit_risk_rule",
        "filename": "sse_company_bond_credit_risk_management_rule_20231020.html",
        "title": "Shanghai Stock Exchange Self-Regulatory Guideline No. 4: Credit Risk Management for Company Bonds and Asset-Backed Securities",
        "publisher": "Shanghai Stock Exchange",
        "document_date": "2023-10-20",
        "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/listing/corporatebond/c/c_20250604_10780814.shtml",
    },
    {
        "source_key": "sse_bond_information_portal",
        "filename": "sse_bond_information_portal_20260815.html",
        "title": "Shanghai Stock Exchange Bond Information Portal",
        "publisher": "Shanghai Stock Exchange",
        "document_date": None,
        "url": "https://bond.sse.com.cn/",
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
        raise RuntimeError(f"refusing to overwrite frozen source batch: {MANIFEST_PATH}")
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
                "capture_note": "First-party rules or venue portal captured for a feasibility preflight. It does not establish that any individual bond is ordinary-investor eligible, liquid, priced, creditworthy, available, suitable, return-producing or actionable.",
            }
        )
    manifest = {
        "schema_version": "c18_sse_company_bond_feasibility_source_manifest.v1",
        "capture_batch": "c18-official-sse-company-bond-feasibility-20260815",
        "case_id": CASE_DIR.name,
        "captured_at": captured_at,
        "source_quality": "dated_primary_regulatory_and_venue_sources",
        "purpose": "Preflight the legal, suitability, credit-risk and venue-information boundaries of a proposed direct listed-company-bond research route before any universe or bond is selected.",
        "records": records,
        "limitations": [
            "Rules and portals are not a historical bond master, transaction tape, full-price record, coupon schedule, rating history, credit-event record, tax record, broker route or settlement evidence.",
            "Eligibility is product-, investor- and time-specific. No source in this batch proves access for any person or any listed bond.",
            "This source batch does not select securities, calculate return, create a portfolio, establish a holding or authorize an external action.",
        ],
    }
    _write(MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(f"C18 company-bond source preflight: {len(records)} files")
    return 0


def _verify() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    expected = {str(source["source_key"]) for source in SOURCES}
    actual = {str(record.get("source_key")) for record in manifest.get("records", []) if isinstance(record, dict)}
    if actual != expected:
        failures.append("source-key set differs from frozen preflight")
    for record in manifest.get("records", []):
        if not isinstance(record, dict):
            failures.append("non-object manifest record")
            continue
        path = REPO_ROOT / str(record.get("path"))
        if not path.is_file():
            failures.append(f"missing source: {record.get('source_key')}")
            continue
        raw = path.read_bytes()
        if len(raw) != int(record.get("bytes", -1)) or _sha256(raw) != record.get("sha256"):
            failures.append(f"hash mismatch: {record.get('source_key')}")
    state = "PASS" if not failures else "FAIL"
    print(f"C18 COMPANY-BOND SOURCE PREFLIGHT: {state}")
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
