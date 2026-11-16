#!/usr/bin/env python3
"""Capture C10 dated primary issuer, exchange, and market-observation sources.

The capture intentionally preserves only documents needed to substantiate the
C10 direct-equity research candidate.  It neither evaluates a trade nor calls
an order or brokerage interface.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
RAW_DIR = CASE_DIR / "sources" / "c10-direct-equity-first-party-20260815"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
HEADERS = {"User-Agent": "Mozilla/5.0 (C10 direct-equity research; read-only)"}
SSE_HEADERS = {
    **HEADERS,
    "Referer": "https://www.sse.com.cn/market/price-trends/stocks/",
}


DOCUMENTS: tuple[dict[str, str], ...] = (
    {
        "code": "600941",
        "name": "China Mobile Limited",
        "filename": "600941_china_mobile_2025_annual_report.pdf",
        "publisher": "Hong Kong Exchanges and Clearing Limited",
        "title": "China Mobile Limited Annual Report 2025",
        "document_date": "2026-04-23",
        "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0423/2026042300752.pdf",
        "authority": "official_exchange_disclosure_for_dual-listed_issuer",
    },
    {
        "code": "600900",
        "name": "China Yangtze Power Co., Ltd.",
        "filename": "600900_china_yangtze_power_2025_annual_report.pdf",
        "publisher": "China Yangtze Power Co., Ltd.",
        "title": "China Yangtze Power Co., Ltd. 2025 Annual Report",
        "document_date": "2026-04-30",
        "url": "https://www.cypc.com.cn/cypc/attachDir/2026/05/2026051815345898336.pdf",
        "authority": "official_issuer_investor_relations_disclosure",
    },
    {
        "code": "601398",
        "name": "Industrial and Commercial Bank of China Limited",
        "filename": "601398_icbc_2025_annual_report_a.pdf",
        "publisher": "Industrial and Commercial Bank of China Limited",
        "title": "Industrial and Commercial Bank of China Limited 2025 Annual Report (A shares)",
        "document_date": "2026-03-27",
        "url": "https://v.icbc.com.cn/userfiles/resources/icbcltd/download/2026/2025AnnualReportA.pdf",
        "authority": "official_issuer_investor_relations_disclosure",
    },
    {
        "code": "601088",
        "name": "China Shenhua Energy Company Limited",
        "filename": "601088_china_shenhua_2025_annual_report.pdf",
        "publisher": "Hong Kong Exchanges and Clearing Limited",
        "title": "China Shenhua Energy Company Limited 2025 Annual Report",
        "document_date": "2026-03-30",
        "url": "https://www1.hkexnews.hk/listedco/listconews/sehk/2026/0330/2026033003748.pdf",
        "authority": "official_exchange_disclosure_for_dual-listed_issuer",
    },
)

RULE_DOCUMENT = {
    "filename": "sse_trading_rules_2026.docx",
    "publisher": "Shanghai Stock Exchange",
    "title": "Shanghai Stock Exchange Trading Rules (2026 Revision)",
    "document_date": "2026-04-24",
    "effective_date": "2026-07-06",
    "url": (
        "https://big5.sse.com.cn/site/cht/www.sse.com.cn/lawandrules/"
        "sselawsrules2025/stocks/exchange/c/10816482/files/"
        "959da0158c65434daa8a43a6e32be7ba.docx"
    ),
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(content)
    temporary.replace(path)


def _runtime() -> dict[str, str]:
    try:
        git_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        git_commit = "not_available"
    return {
        "git_commit_at_runtime": git_commit,
        "script_path": _relative(Path(__file__).resolve()),
        "script_sha256": _sha256(Path(__file__).resolve()),
        "python_version": sys.version.split()[0],
        "platform": platform.platform(),
        "requests_version": str(getattr(requests, "__version__", "not_reported")),
    }


def _download_binary(url: str, headers: dict[str, str]) -> bytes:
    response = requests.get(url, headers=headers, timeout=120)
    response.raise_for_status()
    if len(response.content) < 500:
        raise ValueError(f"document response is unexpectedly small: {url}")
    return response.content


def _parse_jsonp(payload: bytes) -> dict[str, Any]:
    text = payload.decode("utf-8")
    start = text.find("(") + 1
    end = text.rfind(")")
    if start <= 0 or end <= start:
        raise ValueError("SSE dayk response is not JSONP")
    parsed = json.loads(text[start:end])
    if not isinstance(parsed, dict) or not isinstance(parsed.get("total"), int):
        raise ValueError("SSE dayk response does not contain total")
    return parsed


def _capture_dayk(code: str, captured_at: str) -> dict[str, Any]:
    url = f"https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{code}"
    common_params = {
        "callback": "c10probe",
        "select": "date,open,high,low,close,volume",
    }
    overview = requests.get(
        url,
        params={**common_params, "begin": "0", "end": "1"},
        headers=SSE_HEADERS,
        timeout=30,
    )
    overview.raise_for_status()
    total = _parse_jsonp(overview.content)["total"]
    begin = max(total - 60, 0)
    response = requests.get(
        url,
        params={**common_params, "begin": str(begin), "end": str(total)},
        headers=SSE_HEADERS,
        timeout=30,
    )
    response.raise_for_status()
    parsed = _parse_jsonp(response.content)
    rows = parsed.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"SSE dayk response has no rows for {code}")
    filename = f"sse_dayk_{code}_latest60.jsonp"
    path = RAW_DIR / filename
    _atomic_write(path, response.content)
    return {
        "path": _relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "publisher": "Shanghai Stock Exchange",
        "title": f"SSE A-share daily market-price response for {code}, most recent 60 returned rows",
        "document_date": "retrospective response captured 2026-08-15",
        "url": response.url,
        "referer": SSE_HEADERS["Referer"],
        "format": "jsonp",
        "retrieved_at": captured_at,
        "response_rows": len(rows),
        "response_total": total,
        "first_row_date": str(rows[0][0]),
        "last_row_date": str(rows[-1][0]),
        "capture_note": (
            "Official retrospective daily market-price response. It supplies neither adjusted total "
            "return nor historic available_at, corporate actions, market status, quotes, depth, "
            "fees, taxes, fills, settlement, account permission, or execution evidence."
        ),
    }


def _capture() -> None:
    if RAW_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C10 source batch already exists")
    RAW_DIR.mkdir(parents=True, exist_ok=False)
    captured_at = datetime.now(timezone.utc).isoformat()
    files: list[dict[str, Any]] = []
    for item in DOCUMENTS:
        path = RAW_DIR / item["filename"]
        content = _download_binary(item["url"], HEADERS)
        if not content.startswith(b"%PDF"):
            raise ValueError(f"issuer/exchange document is not a PDF: {item['url']}")
        _atomic_write(path, content)
        files.append(
            {
                "path": _relative(path),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
                "publisher": item["publisher"],
                "title": item["title"],
                "code": item["code"],
                "issuer": item["name"],
                "document_date": item["document_date"],
                "url": item["url"],
                "format": "pdf",
                "authority": item["authority"],
                "retrieved_at": captured_at,
                "capture_note": (
                    "Dated audited issuer or official-exchange disclosure captured read-only. It "
                    "does not establish current price, personal tax, account eligibility, liquidity, "
                    "fill, settlement, allocation, holding, or investment action."
                ),
            }
        )
    rule_path = RAW_DIR / RULE_DOCUMENT["filename"]
    rule_content = _download_binary(RULE_DOCUMENT["url"], HEADERS)
    if not rule_content.startswith(b"PK"):
        raise ValueError("SSE trading-rule document is not a DOCX")
    _atomic_write(rule_path, rule_content)
    files.append(
        {
            "path": _relative(rule_path),
            "bytes": rule_path.stat().st_size,
            "sha256": _sha256(rule_path),
            "publisher": RULE_DOCUMENT["publisher"],
            "title": RULE_DOCUMENT["title"],
            "document_date": RULE_DOCUMENT["document_date"],
            "effective_date": RULE_DOCUMENT["effective_date"],
            "url": RULE_DOCUMENT["url"],
            "format": "docx",
            "authority": "official_exchange_rule",
            "retrieved_at": captured_at,
            "capture_note": (
                "Exchange rule text is a market-level mechanics reference. It does not confirm an "
                "individual account's entitlement, broker route, fee, tax, quote, fill, or settlement."
            ),
        }
    )
    for item in DOCUMENTS:
        files.append(_capture_dayk(item["code"], captured_at))
    manifest = {
        "capture_batch": RAW_DIR.name,
        "captured_at": captured_at,
        "case_id": "domestic-personal-securities-futures-strategy-20260814",
        "purpose": (
            "C10 direct A-share quality/dividend candidate: dated issuer quality, cash-flow and "
            "distribution facts; exchange mechanics; and narrow market-observation context."
        ),
        "source_quality": "primary_official_issuer_exchange_and_retrospective_market_observation",
        "research_only": True,
        "formal_replay_eligible": False,
        "files": files,
        "limitations": [
            "This is a four-name diligence pack, not a current complete A-share universe, a security screen, or proof that these names are the best available choices.",
            "Annual-report facts are bounded by their report dates. Proposed distributions can change or fail to be implemented and do not establish a future cash amount or return.",
            "The retained daily-price records are retrospective, unadjusted-basis-undisclosed market observations and are not investor total-return, point-in-time, cost, tax, fill, or settlement evidence.",
            "No broker account, personal suitability, tax treatment, market-data entitlement, quote, depth, order, or execution check is supplied.",
        ],
        "source_freeze": {
            "schema_version": "research_source_freeze_control.v1",
            "seal_status": "case_local_hash_control_only",
            "sealed_at": captured_at,
            "frozen_files": [
                {key: entry[key] for key in ("path", "bytes", "sha256")}
                for entry in files
            ],
            "runtime_provenance": _runtime(),
            "boundary": (
                "Case-local hash control detects a raw-file mismatch only. It is not external "
                "notarization, total-return proof, point-in-time data proof, entitlement, or execution validation."
            ),
        },
    }
    _atomic_write(
        MANIFEST_JSON,
        (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    _atomic_write(
        MANIFEST_MD,
        (
            "# C10 Direct-Equity First-Party Source Manifest\n\n"
            f"- Capture time: `{captured_at}`.\n"
            "- Scope: four dated issuer/exchange annual reports, one current SSE rule document, and four narrow SSE daily-price observations.\n"
            "- Boundary: research evidence only; not a complete universe, total-return replay, personal execution record, or action approval.\n"
        ).encode("utf-8"),
    )


def _verify() -> None:
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    frozen = manifest.get("source_freeze", {}).get("frozen_files", [])
    expected_frozen = [
        {key: entry[key] for key in ("path", "bytes", "sha256")} for entry in files
    ]
    if frozen != expected_frozen:
        raise ValueError("C10 source-freeze record differs from manifest files")
    for entry in files:
        path = REPO_ROOT / entry["path"]
        if not path.is_file() or path.stat().st_size != entry["bytes"]:
            raise ValueError(f"C10 source size mismatch: {path}")
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"C10 source SHA-256 mismatch: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.capture:
        _capture()
    _verify()
    print("C10 DIRECT-EQUITY SOURCE CAPTURE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
