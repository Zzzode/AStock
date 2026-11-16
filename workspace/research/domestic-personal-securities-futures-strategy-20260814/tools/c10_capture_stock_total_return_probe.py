#!/usr/bin/env python3
"""Capture the narrow official inputs for C10's gross cash-dividend diagnostic.

The resulting records are deliberately a diagnostic source bundle, not a
point-in-time total-return database or an order/execution record.
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
RAW_DIR = CASE_DIR / "sources" / "c10-direct-equity-price-dividend-probe-20260815"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
HEADERS = {"User-Agent": "Mozilla/5.0 (C10 price/dividend research; read-only)"}
SSE_PRICE_HEADERS = {
    **HEADERS,
    "Referer": "https://www.sse.com.cn/market/price-trends/stocks/",
}
SSE_DIVIDEND_HEADERS = {
    **HEADERS,
    "Referer": "https://www.sse.com.cn/market/stockdata/dividends/dividend/index_his.shtml",
}
CODES = {
    "600519": "Kweichow Moutai Co., Ltd.",
    "600900": "China Yangtze Power Co., Ltd.",
    "601398": "Industrial and Commercial Bank of China Limited",
    "601088": "China Shenhua Energy Company Limited",
}
YEARS = (2022, 2023, 2024, 2025)
MOUTAI_REPORT = {
    "code": "600519",
    "filename": "600519_kweichow_moutai_2025_annual_report.pdf",
    "publisher": "Kweichow Moutai Co., Ltd.",
    "title": "Kweichow Moutai Co., Ltd. 2025 Annual Report",
    "document_date": "2026-04-17",
    "url": "https://www.moutaichina.com/mtgf/articleFileDir/2026-04/17/07cf01cc11a14ea18cfadf9ebe2a4eb3.pdf",
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


def _parse_jsonp(payload: bytes) -> dict[str, Any]:
    text = payload.decode("utf-8")
    start = text.find("(") + 1
    end = text.rfind(")")
    if start <= 0 or end <= start:
        raise ValueError("SSE response is not JSONP")
    parsed = json.loads(text[start:end])
    if not isinstance(parsed, dict):
        raise ValueError("SSE response JSON is not an object")
    return parsed


def _record(path: Path, **details: Any) -> dict[str, Any]:
    return {
        "path": _relative(path),
        "bytes": path.stat().st_size,
        "sha256": _sha256(path),
        **details,
    }


def _capture_price(code: str, captured_at: str) -> dict[str, Any]:
    url = f"https://yunhq.sse.com.cn:32042/v1/sh1/dayk/{code}"
    common = {"callback": "c10tr", "select": "date,open,high,low,close,volume"}
    first = requests.get(
        url,
        params={**common, "begin": "0", "end": "1"},
        headers=SSE_PRICE_HEADERS,
        timeout=30,
    )
    first.raise_for_status()
    overview = _parse_jsonp(first.content)
    total = overview.get("total")
    if not isinstance(total, int) or total < 1:
        raise ValueError(f"SSE dayk total missing for {code}")
    begin = max(total - 2_000, 0)
    response = requests.get(
        url,
        params={**common, "begin": str(begin), "end": str(total)},
        headers=SSE_PRICE_HEADERS,
        timeout=60,
    )
    response.raise_for_status()
    parsed = _parse_jsonp(response.content)
    rows = parsed.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"SSE dayk rows missing for {code}")
    path = RAW_DIR / f"sse_dayk_{code}_latest2000.jsonp"
    _atomic_write(path, response.content)
    return _record(
        path,
        publisher="Shanghai Stock Exchange",
        title=f"SSE A-share daily market-price response for {code}, latest 2,000 returned rows",
        code=code,
        issuer=CODES[code],
        document_date="retrospective response captured 2026-08-15",
        url=response.url,
        referer=SSE_PRICE_HEADERS["Referer"],
        format="jsonp",
        retrieved_at=captured_at,
        response_rows=len(rows),
        response_total=total,
        first_row_date=str(rows[0][0]),
        last_row_date=str(rows[-1][0]),
        capture_note=(
            "Official retrospective daily market-price response. Adjustment basis, historic available_at, "
            "corporate-action completeness, bid/ask, depth, market status, costs, tax, fills, settlement, "
            "account permission and entitlement are not supplied."
        ),
    )


def _capture_dividend(code: str, year: int, captured_at: str) -> dict[str, Any]:
    url = "https://query.sse.com.cn/commonQuery.do"
    params = {
        "jsonCallBack": "c10div",
        "sqlId": "COMMON_SSE_SJ_GPSJ_FHSG_SSGSFHQK_L",
        "CONDITION_AG": "1",
        "A_STOCK_CODE": code,
        "A_REG_DATE": str(year),
        "page_size": "100",
        "page_no": "1",
        "isPagination": "true",
    }
    response = requests.get(url, params=params, headers=SSE_DIVIDEND_HEADERS, timeout=30)
    response.raise_for_status()
    parsed = _parse_jsonp(response.content)
    rows = parsed.get("result")
    if rows is None:
        rows = parsed.get("pageHelp", {}).get("data")
    if not isinstance(rows, list):
        raise ValueError(f"SSE dividend rows missing for {code}/{year}")
    path = RAW_DIR / f"sse_dividend_{code}_{year}.jsonp"
    _atomic_write(path, response.content)
    return _record(
        path,
        publisher="Shanghai Stock Exchange",
        title=f"SSE A-share cash-dividend event query for {code}, record-date year {year}",
        code=code,
        issuer=CODES[code],
        document_date=f"record-date filter {year}; retrospective response captured 2026-08-15",
        url=response.url,
        referer=SSE_DIVIDEND_HEADERS["Referer"],
        format="jsonp",
        retrieved_at=captured_at,
        response_rows=len(rows),
        capture_note=(
            "Official retrospective event-query response. It is a code/year response, not a complete "
            "corporate-action, tax, payment, reinvestment, adjustment, investor-lot, or execution ledger."
        ),
    )


def _capture() -> None:
    if RAW_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C10 price/dividend source batch already exists")
    RAW_DIR.mkdir(parents=True, exist_ok=False)
    captured_at = datetime.now(timezone.utc).isoformat()
    files: list[dict[str, Any]] = []
    report_path = RAW_DIR / MOUTAI_REPORT["filename"]
    report_response = requests.get(MOUTAI_REPORT["url"], headers=HEADERS, timeout=120)
    report_response.raise_for_status()
    if not report_response.content.startswith(b"%PDF"):
        raise ValueError("Moutai issuer annual report is not a PDF")
    _atomic_write(report_path, report_response.content)
    files.append(
        _record(
            report_path,
            publisher=MOUTAI_REPORT["publisher"],
            title=MOUTAI_REPORT["title"],
            code=MOUTAI_REPORT["code"],
            issuer=CODES[MOUTAI_REPORT["code"]],
            document_date=MOUTAI_REPORT["document_date"],
            url=MOUTAI_REPORT["url"],
            format="pdf",
            authority="official_issuer_investor_relations_disclosure",
            retrieved_at=captured_at,
            capture_note=(
                "Dated issuer annual report captured read-only. It does not establish current price, "
                "tax, account eligibility, liquidity, fill, settlement, allocation, holding, or action."
            ),
        )
    )
    for code in CODES:
        files.append(_capture_price(code, captured_at))
        for year in YEARS:
            files.append(_capture_dividend(code, year, captured_at))
    manifest = {
        "capture_batch": RAW_DIR.name,
        "captured_at": captured_at,
        "case_id": "domestic-personal-securities-futures-strategy-20260814",
        "purpose": (
            "C10 exploratory historical gross cash-dividend diagnostic for a fixed four-name direct "
            "A-share research candidate."
        ),
        "source_quality": "primary_official_issuer_exchange_retrospective_price_and_event_observation",
        "research_only": True,
        "formal_replay_eligible": False,
        "files": files,
        "limitations": [
            "The records are retrieved after the observation periods and do not establish original-date availability, revisions, or a point-in-time research dataset.",
            "The raw daily-price endpoint does not disclose its adjustment convention; a calculated price-plus-cash result is only a diagnostic, not investor total return.",
            "The dividend endpoint does not establish complete corporate actions, payment success, tax, reinvestment, or entitlement at an investor-lot level.",
            "There is no cost, spread, market-impact, no-fill, settlement, account-permission, or broker ledger; positive results may not be treated as validation.",
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
                "notarization, entitlement, a point-in-time proof, total-return validation, or execution validation."
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
            "# C10 Direct-Equity Price-and-Dividend Diagnostic Source Manifest\n\n"
            f"- Capture time: `{captured_at}`.\n"
            "- Scope: Moutai annual report; four raw SSE price panels; and four code/year dividend-event panels for each of 2022--2025.\n"
            "- Boundary: exploratory gross-cash diagnostic only; not a PIT total-return replay, product admission, allocation approval, or action instruction.\n"
        ).encode("utf-8"),
    )


def _verify() -> None:
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    expected_frozen = [
        {key: entry[key] for key in ("path", "bytes", "sha256")} for entry in files
    ]
    if manifest.get("source_freeze", {}).get("frozen_files") != expected_frozen:
        raise ValueError("C10 price/dividend source-freeze record differs from manifest files")
    for entry in files:
        path = REPO_ROOT / entry["path"]
        if not path.is_file() or path.stat().st_size != entry["bytes"]:
            raise ValueError(f"C10 price/dividend source size mismatch: {path}")
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"C10 price/dividend source SHA-256 mismatch: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.capture:
        _capture()
    _verify()
    print("C10 PRICE/DIVIDEND SOURCE CAPTURE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
