#!/usr/bin/env python3
"""Capture dated primary SHFE rule pages for C17's added families.

This batch expands product diligence only.  It does not calculate a return,
select a contract, place an order or establish an account route.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c17-official-shfe-expanded-product-diligence-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
SOURCES = (
    {
        "family": "RB",
        "filename": "shfe_rb_contract_rules_20260101.html",
        "title": "Shanghai Futures Exchange rebar futures business rules",
        "document_date": "2026-01-01",
        "url": "https://www.shfe.cn/regulation/exchangerules/productrules/202512/t20251231_829962.html",
    },
    {
        "family": "SP",
        "filename": "shfe_sp_contract_rules_20260101.html",
        "title": "Shanghai Futures Exchange bleached softwood kraft pulp futures business rules",
        "document_date": "2026-01-01",
        "url": "https://www.shfe.cn/regulation/exchangerules/productrules/202512/t20251231_829972.html",
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
    if b"safeline_bot_challenge" in raw or b"WEB \xe5\xba\x94\xe7\x94\xa8\xe9\x98\xb2\xe7\x81\xab\xe5\xa2\x99" in raw:
        raise ValueError(f"refusing WAF challenge response: {url}")
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
                "family": source["family"],
                "path": _repo_path(path),
                "url": source["url"],
                "title": source["title"],
                "document_date": source["document_date"],
                "retrieved_at": captured_at,
                "bytes": len(raw),
                "sha256": _sha256(raw),
                "capture_note": "Dated first-party exchange rule text. It documents product mechanics and exchange-level risk parameters only; it does not establish historic session conditions, broker terms, personal access, fill, position, return or action.",
            }
        )
    manifest = {
        "schema_version": "c17_shfe_expanded_product_source_manifest.v1",
        "capture_batch": "c17-official-shfe-expanded-product-diligence-20260815",
        "case_id": CASE_DIR.name,
        "captured_at": captured_at,
        "source_quality": "dated_primary_exchange_product_rules",
        "purpose": "Dated product mechanism and risk diligence for the RB and SP families added to the C17 research universe.",
        "records": records,
        "limitations": [
            "The current dated rules do not establish historical effective margin, price-limit, fee, calendar, delivery-state or broker conditions across 2019--2025.",
            "The records do not establish personal product access, order fill, capacity, cost, account route, investor return or an external action.",
        ],
    }
    _write(MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(f"C17 product-source capture: {len(records)} files")
    return 0


def _verify() -> int:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    for record in manifest.get("records", []):
        path = REPO_ROOT / str(record["path"])
        if not path.is_file():
            failures.append(f"missing {record['family']}")
            continue
        raw = path.read_bytes()
        if len(raw) != int(record["bytes"]) or _sha256(raw) != record["sha256"]:
            failures.append(f"hash mismatch {record['family']}")
    state = "PASS" if not failures else "FAIL"
    print(f"C17 EXPANDED PRODUCT SOURCE: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    return _verify() if arguments.verify_only else _capture()


if __name__ == "__main__":
    raise SystemExit(main())
