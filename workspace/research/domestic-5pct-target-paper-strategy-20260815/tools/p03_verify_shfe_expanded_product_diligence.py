#!/usr/bin/env python3
"""Verify P03's two dated exchange product sources and action boundary."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
MANIFEST_PATH = CASE_DIR / "sources" / "c17-official-shfe-expanded-product-diligence-20260815" / "manifest.json"
P03_PATH = CASE_DIR / "analysis" / "p03_shfe_expanded_actual_contract_product_diligence_20260815.json"
EXPECTED_MANIFEST = "dbc39e8c0d3789cb88d2267dca285b1b4cf58f1ca65e235471e0c250d8c12ec8"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    if not MANIFEST_PATH.is_file() or _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST:
        failures.append("C17 product source manifest mismatch")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = {str(row.get("family")): row for row in manifest.get("records", []) if isinstance(row, dict)}
    if set(records) != {"RB", "SP"}:
        failures.append("unexpected product source coverage")
    for family, record in records.items():
        path = REPO_ROOT / str(record["path"])
        if not path.is_file() or _sha256(path) != record.get("sha256"):
            failures.append(f"source mismatch: {family}")
    p03 = json.loads(P03_PATH.read_text(encoding="utf-8"))
    if p03.get("research_only") is not True or p03.get("formal_decision_eligible") is not False:
        failures.append("P03 action boundary changed")
    if p03.get("source_manifest", {}).get("sha256") != EXPECTED_MANIFEST:
        failures.append("P03 source control differs")
    if [row.get("family") for row in p03.get("products", [])] != ["RB", "SP"]:
        failures.append("P03 product cards differ")
    state = "PASS" if not failures else "FAIL"
    print(f"P03 EXPANDED SHFE PRODUCT DILIGENCE: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
