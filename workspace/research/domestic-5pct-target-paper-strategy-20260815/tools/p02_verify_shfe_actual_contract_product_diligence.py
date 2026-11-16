#!/usr/bin/env python3
"""Verify the inherited primary-source control for P02."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
STRICT_CASE = CASE_DIR.parent / "domestic-personal-securities-futures-strategy-20260814"
MANIFEST_PATH = STRICT_CASE / "sources" / "c9-official-shfe-commodity-contracts-20260815" / "manifest.json"
P02_PATH = CASE_DIR / "analysis" / "p02_shfe_actual_contract_product_diligence_20260815.json"
EXPECTED_MANIFEST_SHA256 = "a639271b0159f5ce26bf5bd6efaf996e2b6722de16cf5d5efbda721f18bb4cd4"
EXPECTED_FILES = {
    "shfe_cu_contract_rules_20260101.html",
    "shfe_au_contract_rules_20260101.html",
    "shfe_ru_contract_rules_20260101.html",
    "shfe_risk_control_rules_20260706.html",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    if not MANIFEST_PATH.is_file() or _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST_SHA256:
        failures.append("official C9 source manifest mismatch")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    recorded = {Path(str(row.get("path", ""))).name: row for row in manifest.get("files", []) if isinstance(row, dict)}
    if not EXPECTED_FILES.issubset(recorded):
        failures.append("required product-rule files missing from manifest")
    for filename in EXPECTED_FILES.intersection(recorded):
        path = REPO_ROOT / str(recorded[filename]["path"])
        if not path.is_file() or _sha256(path) != recorded[filename].get("sha256"):
            failures.append(f"frozen source mismatch: {filename}")
    p02 = json.loads(P02_PATH.read_text(encoding="utf-8"))
    if p02.get("status") != "dated_exchange_product_facts_verified; not_admitted_for_action":
        failures.append("P02 status changed")
    if p02.get("research_only") is not True or p02.get("formal_decision_eligible") is not False:
        failures.append("P02 research boundary changed")
    if p02.get("source_manifest", {}).get("sha256") != EXPECTED_MANIFEST_SHA256:
        failures.append("P02 source hash differs")
    if [row.get("family") for row in p02.get("products", [])] != ["CU", "AU", "RU"]:
        failures.append("P02 product coverage changed")
    state = "PASS" if not failures else "FAIL"
    print(f"P02 SHFE ACTUAL-CONTRACT DILIGENCE: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
