#!/usr/bin/env python3
"""Verify the source chain and core controls of P01 ETF product diligence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
JSON_PATH = CASE_DIR / "analysis" / "p01_core_etf_product_diligence_20260815.json"
MD_PATH = CASE_DIR / "analysis" / "p01_core_etf_product_diligence_20260815.md"
EXPECTED = {"510300", "510880", "511010", "518880", "511990"}
FORBIDDEN_READER_TERMS = ("本金", "初始资金", "初始金额", "initial capital", "initial_capital", "principal", "starting amount")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    if not JSON_PATH.is_file() or not MD_PATH.is_file():
        failures.append("P01 product artifacts are missing")
    if not failures:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        if data.get("artifact_id") != "D5PT-P01-v1":
            failures.append("unexpected P01 artifact ID")
        if data.get("status") != "paper_admission_pending" or data.get("formal_decision_eligible") is not False:
            failures.append("P01 status must remain paper-admission pending and not decision eligible")
        products = data.get("products", [])
        if {row.get("code") for row in products} != EXPECTED:
            failures.append("P01 product code set differs from fixed rule")
        for row in products:
            source = row.get("source", {})
            path = REPO_ROOT / str(source.get("path", ""))
            if not path.is_file():
                failures.append(f"missing product source for {row.get('code')}")
            elif _sha256(path) != source.get("sha256"):
                failures.append(f"product source digest mismatch for {row.get('code')}")
        manifest = REPO_ROOT / str(data.get("source_manifest", {}).get("path", ""))
        if not manifest.is_file():
            failures.append("P01 source manifest is absent")
        elif _sha256(manifest) != data.get("source_manifest", {}).get("sha256"):
            failures.append("P01 source manifest digest mismatch")
    for path in (JSON_PATH, MD_PATH):
        if path.is_file():
            text = path.read_text(encoding="utf-8").lower()
            for term in FORBIDDEN_READER_TERMS:
                if term.lower() in text:
                    failures.append(f"forbidden reader term {term!r} in {path.name}")
    if failures:
        print("P01 CORE ETF DILIGENCE: FAIL")
        print("\n".join(failures))
        return 1
    print("P01 CORE ETF DILIGENCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
