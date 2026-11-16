#!/usr/bin/env python3
"""Freeze primary SSE material for a bounded ETF-collar route screen.

The capture establishes rule and data-interface boundaries only.  It does not
select an ETF or option series, calculate a return, verify an account, or
authorize any trade.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c51-sse-etf-option-collar-scope-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 (research source capture)"})
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
    temporary = MANIFEST_PATH.with_name(f".{MANIFEST_PATH.name}.tmp")
    temporary.write_bytes(payload)
    temporary.replace(MANIFEST_PATH)


def main() -> int:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    sources = (
        {
            "source_id": "C51-S01",
            "filename": "sse_option_investor_suitability_page.html",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781453.shtml",
            "purpose": "SSE landing page and current-effectiveness context for the stock-option investor-suitability guideline.",
        },
        {
            "source_id": "C51-S02",
            "filename": "sse_option_investor_suitability_guideline.docx",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/10781453/files/733e45a7625f460facc66cff7ddcfc8b.docx",
            "purpose": "Official SSE suitability-guideline text used only to distinguish rule-level strategy definitions from account-specific entitlement.",
        },
        {
            "source_id": "C51-S03",
            "filename": "sse_stock_option_trading_rule_page.html",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781448.shtml",
            "purpose": "SSE landing page and current-effectiveness context for the stock-option trading rule.",
        },
        {
            "source_id": "C51-S04",
            "filename": "sse_stock_option_trading_rule.docx",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/10781448/files/0c0f89e74e9c4a5b9aa3a7acafdf5119.docx",
            "purpose": "Official SSE trading-rule text on covered opening, locked covered securities, order validity and contract adjustments.",
        },
        {
            "source_id": "C51-S05",
            "filename": "sse_market_data_file_exchange_specification.pdf",
            "url": "https://www.sse.com.cn/services/tradingtech/development/c/10810429/files/ca36291a287242698ad505bce1a7efcc.pdf",
            "purpose": "SSE interface specification showing that option reference, real-time, closing-price and combination-strategy data fields exist; it is not a historical-data entitlement, execution ledger or replay-right grant.",
        },
    )

    existing_manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8")) if MANIFEST_PATH.exists() else None
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
        payload = fetch(item["url"])
        write_new(path, payload)
        entries.append(
            {
                "source_id": item["source_id"],
                "filename": item["filename"],
                "url": item["url"],
                "purpose": item["purpose"],
                "sha256": sha256(payload),
                "byte_count": len(payload),
                "retrieval_mode": "public_primary_source_get",
            }
        )

    manifest = {
        "schema_version": "c51_sse_etf_option_collar_source_manifest.v1",
        "artifact_id": "D5PT-C51-SOURCES-v1",
        "retrieved_at_utc": (
            existing_manifest.get("retrieved_at_utc")
            if existing_manifest
            else datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        ),
        "scope": "Primary-source capture for a rule-level ETF-collar route screen only. It is not an actual option-chain dataset, a historical performance dataset, an account entitlement record, or an action authorization.",
        "entries": entries,
    }
    content = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if not MANIFEST_PATH.exists() or MANIFEST_PATH.read_text(encoding="utf-8") != content:
        replace_manifest(content.encode("utf-8"))
    print(f"C51 source capture complete: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
