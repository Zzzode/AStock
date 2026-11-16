#!/usr/bin/env python3
"""Retain dated official route descriptions without inferring data entitlement."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = CASE_DIR / "sources" / "c49-official-authorized-data-route-20260815"
MANIFEST = SOURCE_DIR / "manifest.json"
AS_OF = "2026-08-15"
USER_AGENT = "AStockResearch/1.0 (archival research; no automated trading)"

RECORDS = (
    {
        "source_key": "sseinfo_authorization_statement",
        "filename": "sseinfo_authorization_statement.html",
        "publisher": "Shanghai Stock Exchange Information Network Co., Ltd.",
        "title": "Shanghai and Shenzhen exchange information authorization statement",
        "url": "https://www.sseinfo.com/aboutus/authstatement/",
        "role": "Shows that receiving, using or operating SSE/SZSE market information requires permission from the authorized information operators.",
    },
    {
        "source_key": "sseinfo_historical_data_product",
        "filename": "sseinfo_historical_data_product.html",
        "publisher": "Shanghai Stock Exchange Information Network Co., Ltd.",
        "title": "SSE historical market-data product description",
        "url": "https://www.sseinfo.com/services/assortment/historical/",
        "role": "Describes historical snapshots, trades, daily/minute bars, auction data, security master information and ETF IOPV as product categories, with an application link.",
    },
    {
        "source_key": "csrc_public_fund_disclosure_rule",
        "filename": "csrc_public_fund_disclosure_rule.html",
        "publisher": "China Securities Regulatory Commission",
        "title": "Administrative Measures on Information Disclosure by Publicly Offered Securities Investment Funds",
        "url": "https://www.csrc.gov.cn/csrc/c106256/c1653985/content.shtml",
        "role": "Defines public NAV, cumulative NAV, reports, material events and distribution disclosure as source facts, not a normalized investor-total-return or broker-execution ledger.",
    },
    {
        "source_key": "cffex_historical_data_service",
        "filename": "cffex_historical_data_service.html",
        "publisher": "China Financial Futures Exchange",
        "title": "CFFEX historical data service",
        "url": "https://www.cffex.com.cn/lssjfw/",
        "role": "Potential future authorized historical futures-data route only; no field or entitlement inference is permitted unless the page is retained and a written delivery is independently accepted.",
        "optional": True,
    },
    {
        "source_key": "cffex_historical_data_application_materials",
        "filename": "cffex_historical_data_application_materials.html",
        "publisher": "China Financial Futures Exchange",
        "title": "CFFEX historical-data application materials",
        "url": "https://www.cffex.com.cn/zlxz/",
        "role": "Potential future application/authorization locator only; it does not evidence a current right or a delivered historical dataset.",
        "optional": True,
    },
)


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml"})
    with urlopen(request, timeout=20) as response:
        return response.read()


def main() -> int:
    if MANIFEST.exists():
        raise SystemExit(f"Refusing to overwrite existing source manifest: {MANIFEST}")
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    captured_at = datetime.now(timezone.utc).isoformat()
    files: list[dict[str, object]] = []
    non_records: list[dict[str, object]] = []

    for record in RECORDS:
        path = SOURCE_DIR / str(record["filename"])
        if path.exists():
            payload = path.read_bytes()
            record_retrieved_at = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        else:
            try:
                payload = fetch(str(record["url"]))
            except Exception as error:  # optional official endpoints may be unavailable from this host
                if not record.get("optional"):
                    raise SystemExit(f"Required official source unavailable: {record['source_key']}: {error}") from error
                non_records.append(
                    {
                        "source_key": record["source_key"],
                        "url": record["url"],
                        "retrieved_at": captured_at,
                        "status": "not_retained_connection_error",
                        "error_type": type(error).__name__,
                        "use_limit": "This URL is a locator only and is not used as retained field, entitlement, version or execution evidence.",
                    }
                )
                continue
            record_retrieved_at = captured_at
            path.write_bytes(payload)
        files.append(
            {
                "source_key": record["source_key"],
                "path": f"workspace/research/domestic-5pct-target-paper-strategy-20260815/sources/c49-official-authorized-data-route-20260815/{path.name}",
                "publisher": record["publisher"],
                "title": record["title"],
                "url": record["url"],
                "retrieved_at": record_retrieved_at,
                "bytes": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
                "role": record["role"],
            }
        )

    manifest = {
        "schema_version": "c49_official_authorized_data_route_source_manifest.v1",
        "capture_batch": "c49-official-authorized-data-route-20260815",
        "case_id": "domestic-5pct-target-paper-strategy-20260815",
        "as_of": AS_OF,
        "captured_at": captured_at,
        "purpose": "Retain dated official descriptions of conditional authorized market-data routes and public disclosure facts for a source-governance feasibility recheck. This is not data procurement or acceptance.",
        "source_quality": "dated_primary_provider_and_regulatory_route_descriptions",
        "files": files,
        "non_records": non_records,
        "limitations": [
            "Product pages and authorization statements do not themselves grant a license, define a delivered historical field set, establish point-in-time availability/revision lineage, or prove use/replay rights.",
            "Public fund disclosures are source facts only and do not form a normalized investor-total-return, cash-flow, tax, settlement or broker-execution ledger.",
            "No record in this batch establishes broker or futures-company account eligibility, commissions, margin add-ons, order status, partial fills, settlement or tax.",
            "No record selects an instrument, calculates performance, establishes a stable outcome, or authorizes an external action."
        ],
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"manifest": str(MANIFEST), "retained_files": len(files), "non_records": len(non_records)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
