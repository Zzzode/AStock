#!/usr/bin/env python3
"""Freeze primary SSE material for the C52 option-history source screen.

The capture evaluates public-source coverage only. It neither selects an ETF
or option contract nor establishes historical replay rights, account access,
or a trade instruction.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c52-sse-etf-option-history-route-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def fetch(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (research source capture)",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        },
    )
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
            "source_id": "C52-S01",
            "filename": "sse_option_daily_contract_page.html",
            "url": "https://www.sse.com.cn/assortment/options/disclo/preinfo/",
            "purpose": "Current SSE daily-option-contract display used to identify the public contract fields and to test whether an historical as-of interface is evidenced.",
        },
        {
            "source_id": "C52-S02",
            "filename": "sse_option_listing_adjustment_page.html",
            "url": "https://www.sse.com.cn/assortment/options/disclo/info/",
            "purpose": "SSE listing, delisting and adjustment disclosure page used only for dated contract-event evidence.",
        },
        {
            "source_id": "C52-S03",
            "filename": "sse_option_market_price_page.html",
            "url": "https://www.sse.com.cn/assortment/options/price/",
            "purpose": "Current SSE option-market display used to distinguish live/current fields from a date-queryable historical close or settlement panel.",
        },
        {
            "source_id": "C52-S04",
            "filename": "sse_option_information_query_script.js",
            "url": "https://www.sse.com.cn/xhtml/home/2021public/querySearch/search_stockOptionInformation_2021.js",
            "purpose": "Official client-side query implementation used to inspect public listing/adjustment and daily-contract query parameters.",
        },
        {
            "source_id": "C52-S05",
            "filename": "sse_20161128_50etf_dividend_option_adjustment_notice.html",
            "url": "https://www.sse.com.cn/assortment/options/guide/c/c_20161128_4207559.shtml",
            "purpose": "Dated SSE example of an ETF dividend-related option-contract adjustment; it is an event record, not a normalized total-return ledger.",
        },
        {
            "source_id": "C52-S06",
            "filename": "sseinfo_historical_data_product_page.html",
            "url": "https://www.sseinfo.com/services/assortment/historical/",
            "purpose": "SSE information-operator historical-data product page used only to distinguish a possible licensed future route from public current-page access.",
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
        "schema_version": "c52_sse_etf_option_history_source_manifest.v1",
        "artifact_id": "D5PT-C52-SOURCES-v1",
        "retrieved_at_utc": (
            existing_manifest.get("retrieved_at_utc")
            if existing_manifest
            else datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        ),
        "scope": "Primary-source capture for a public SSE ETF-option historical-data coverage screen only. It is not an option-chain delivery, a total-return ledger, a replay-right grant, an account record, or an action authorization.",
        "entries": entries,
    }
    content = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if not MANIFEST_PATH.exists() or MANIFEST_PATH.read_text(encoding="utf-8") != content:
        replace_manifest(content.encode("utf-8"))
    print(f"C52 source capture complete: {MANIFEST_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
