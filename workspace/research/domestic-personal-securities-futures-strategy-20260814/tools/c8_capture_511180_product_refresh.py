#!/usr/bin/env python3
"""Retain a dated issuer-published 511180 product-summary refresh for C8."""

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
RAW_DIR = CASE_DIR / "sources" / "c8-official-511180-product-refresh-20260815"
RAW_PATH = RAW_DIR / "511180_product_summary_20251209.pdf"
MANIFEST_JSON = RAW_DIR / "manifest.json"
MANIFEST_MD = RAW_DIR / "manifest.md"
URL = (
    "https://www.hftfund.com/upload/fck/userfiles/file/1765245214322-"
    "511180_%E6%B5%B7%E5%AF%8C%E9%80%9A%E4%B8%8A%E8%AF%81%E6%8A%95%E8%B5%84%E7%BA%A7"
    "%E5%8F%AF%E8%BD%AC%E5%80%BA%E5%8F%8A%E5%8F%AF%E4%BA%A4%E6%8D%A2%E5%80%BA%E5%88%B8"
    "%E4%BA%A4%E6%98%93%E5%9E%8B%E5%BC%80%E6%94%BE%E5%BC%8F%E6%8C%87%E6%95%B0%E8%AF%81"
    "%E5%88%B8%E6%8A%95%E8%B5%84%E5%9F%BA%E9%87%91%E5%9F%BA%E9%87%91%E4%BA%A7%E5%93%81"
    "%E8%B5%84%E6%96%99%E6%A6%82%E8%A6%81%E6%9B%B4%E6%96%B0.pdf"
)
HEADERS = {"User-Agent": "Mozilla/5.0 (C8 issuer-document capture; read-only)"}


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
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True
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


def _record() -> dict[str, Any]:
    return {
        "path": _relative(RAW_PATH),
        "bytes": RAW_PATH.stat().st_size,
        "sha256": _sha256(RAW_PATH),
        "publisher": "Haifutong Fund Management Co., Ltd.",
        "title": "511180 Haifutong SSE Investment Grade Convertible Bond and Exchangeable Bond ETF product summary update",
        "document_date": "2025-12-09",
        "url": URL,
        "format": "pdf",
        "capture_note": "Issuer-published dated disclosure retained by read-only HTTPS. It does not establish current terms, account access, market price, liquidity, total return, costs, fills, allocation, holding, or action.",
    }


def _capture() -> None:
    if RAW_DIR.exists() or MANIFEST_JSON.exists():
        raise FileExistsError("C8 511180 refresh batch already exists")
    response = requests.get(URL, headers=HEADERS, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(f"Issuer PDF download failed: HTTP {response.status_code}")
    if not response.content.startswith(b"%PDF") or len(response.content) < 500:
        raise ValueError("Issuer response is not a usable PDF")
    RAW_DIR.mkdir(parents=True, exist_ok=False)
    _atomic_write(RAW_PATH, response.content)
    record = _record()
    captured_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "capture_batch": RAW_DIR.name,
        "captured_at": captured_at,
        "purpose": "C8 dated first-party issuer refresh for 511180 product-diligence facts only.",
        "source_quality": "primary_official_issuer_disclosure",
        "files": [record],
        "limitations": [
            "The document date, not capture date, bounds its product facts.",
            "It is not proof of current account eligibility, market price, NAV/IOPV, liquidity, total return, costs, fills, allocation, holding, or action.",
        ],
        "source_freeze": {
            "schema_version": "research_source_freeze_control.v1",
            "seal_status": "case_local_hash_control",
            "sealed_at": captured_at,
            "frozen_files": [{key: record[key] for key in ("path", "bytes", "sha256")}],
            "runtime_provenance": _runtime(),
            "boundary": "Case-local hash control detects raw-file mismatch only; it is not external notarization, entitlement, or execution validation.",
        },
    }
    _atomic_write(MANIFEST_JSON, (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    _atomic_write(
        MANIFEST_MD,
        (
            "# C8 511180 Issuer Product-Summary Refresh Manifest\n\n"
            f"- Document date: `2025-12-09`; capture time: `{captured_at}`.\n"
            f"- Raw PDF: `{RAW_PATH.name}`; SHA-256: `{record['sha256']}`.\n"
            "- Boundary: a dated issuer document, not a current-action or investor-return record.\n"
        ).encode("utf-8"),
    )


def _verify() -> None:
    manifest = json.loads(MANIFEST_JSON.read_text(encoding="utf-8"))
    record = manifest["files"][0]
    if not RAW_PATH.is_file() or RAW_PATH.stat().st_size != record["bytes"] or _sha256(RAW_PATH) != record["sha256"]:
        raise ValueError("C8 511180 refresh source hash check failed")
    frozen = manifest["source_freeze"]["frozen_files"]
    if frozen != [{key: record[key] for key in ("path", "bytes", "sha256")}]:
        raise ValueError("C8 511180 refresh source-freeze record differs")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--capture", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    if arguments.capture:
        _capture()
    _verify()
    print("C8 511180 PRODUCT REFRESH: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
