#!/usr/bin/env python3
"""Freeze primary SSE material for the C50 general-repo yield-floor screen.

This is a source capture only.  It neither computes a strategy result nor
asserts that a historical or future return hurdle has been met.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c50-sse-general-repo-screen-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
REFERER = "https://bond.sse.com.cn/data/standard/repocurve/onerepo/"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str, *, referer: str | None = None) -> bytes:
    headers = {"User-Agent": "Mozilla/5.0 (research source capture)"}
    if referer:
        headers["Referer"] = referer
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:
        return response.read()


def write_new(path: Path, payload: bytes) -> None:
    if path.exists():
        if path.read_bytes() != payload:
            raise RuntimeError(f"refusing to overwrite a different frozen source: {path}")
        return
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(path)


def replace_manifest(payload: bytes) -> None:
    """Update only the manifest after immutable raw-file checks have passed."""
    temporary = MANIFEST_PATH.with_name(f".{MANIFEST_PATH.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(MANIFEST_PATH)


def main() -> int:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    query = urlencode(
        {
            "jsonCallBack": "callback",
            "isPagination": "false",
            "sqlId": "COMMON_BOND_HGDPSYLQX_L",
            "TRADEDATE": "2026-08-14",
        }
    )
    sources = (
        {
            "source_id": "C50-S01",
            "filename": "sse_general_repo_personal_inverse_participation.html",
            "url": "https://bond.sse.com.cn/market/tradingm/strepo/",
            "purpose": "SSE explanation of general pledged repo mechanics, personal inverse-repo participation, matching, central clearing, and fee statement.",
            "referer": None,
        },
        {
            "source_id": "C50-S02",
            "filename": "sse_general_repo_trading_guideline.html",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/trading/currency/c/c_20250606_10781048.shtml",
            "purpose": "SSE publication page linking the current general-repo trading guideline.",
            "referer": None,
        },
        {
            "source_id": "C50-S03",
            "filename": "sse_204001_curve_page_20260814.html",
            "url": REFERER,
            "purpose": "SSE 204001 public curve page at capture, retaining the displayed date stamp and recent rate observations.",
            "referer": None,
        },
        {
            "source_id": "C50-S04",
            "filename": "sse_204001_fixing_query_20260814.jsonp",
            "url": f"https://query.sse.com.cn/commonQuery.do?{query}",
            "purpose": "SSE public query response for the five observations ending 2026-08-14; used only to identify the official quoted annualized rate at the observation date.",
            "referer": REFERER,
        },
        {
            "source_id": "C50-S05",
            "filename": "sse_general_repo_trading_guideline.docx",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/bond/trading/currency/c/10781048/files/9c80d6d104164618b79f679aff8de1da.docx",
            "purpose": "Attached SSE trading guideline text on repo term, code, settlement, annualized-rate formula, and daily fixing publication.",
            "referer": None,
        },
    )

    existing_manifest = (
        json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if MANIFEST_PATH.exists()
        else None
    )
    existing_by_id = {
        str(entry.get("source_id")): entry
        for entry in existing_manifest.get("entries", [])
        if isinstance(entry, dict)
    } if existing_manifest else {}
    entries = []
    for item in sources:
        path = SOURCE_DIR / item["filename"]
        existing = existing_by_id.get(item["source_id"])
        if existing:
            if existing.get("filename") != item["filename"] or existing.get("url") != item["url"]:
                raise RuntimeError(f"frozen source identity mismatch: {item['source_id']}")
            payload = path.read_bytes()
            if existing.get("sha256") != sha256(payload):
                raise RuntimeError(f"frozen source digest mismatch: {item['source_id']}")
            entries.append({**existing, "purpose": item["purpose"]})
            continue
        payload = fetch(item["url"], referer=item["referer"])
        write_new(path, payload)
        entries.append({
            "source_id": item["source_id"],
            "filename": item["filename"],
            "url": item["url"],
            "purpose": item["purpose"],
            "sha256": sha256(payload),
            "byte_count": len(payload),
            "retrieval_mode": "public_primary_source_get",
        })

    manifest = {
        "schema_version": "c50_sse_general_repo_source_manifest.v1",
        "artifact_id": "D5PT-C50-SOURCES-v1",
        "retrieved_at_utc": (
            existing_manifest.get("retrieved_at_utc")
            if existing_manifest
            else datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        ),
        "scope": "Primary-source capture for a mechanism and yield-floor pre-screen only. It is not an execution record, a personal-account entitlement record, or a historical-performance dataset.",
        "entries": entries,
    }
    content = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if not MANIFEST_PATH.exists() or MANIFEST_PATH.read_text(encoding="utf-8") != content:
        replace_manifest(content.encode("utf-8"))
    print(f"C50 source capture complete: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
