#!/usr/bin/env python3
"""Verify C18's source-preflight binding and no-action state."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
MANIFEST_PATH = CASE_DIR / "sources" / "c18-official-sse-company-bond-feasibility-20260815" / "manifest.json"
AUGMENTATION_MANIFEST_PATH = CASE_DIR / "sources" / "c18-official-sse-company-bond-rule-text-augmentation-20260815" / "manifest.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c18_direct_sse_company_bond_ladder_feasibility_20260815.json"
EXPECTED_MANIFEST = "0ef9a473ae98c5fafcb6f4cb92e8785ab5a2eb220f3c7c0ce41e42617872b908"
EXPECTED_AUGMENTATION_MANIFEST = "863fc638ccd443c3f5c22355094e6b326a52967f5943d1d65eee64fc0d951a69"
EXPECTED_KEYS = {
    "sse_company_bond_listing_rule",
    "sse_bond_investor_suitability_rule",
    "csrc_company_bond_administration_measure",
    "sse_company_bond_credit_risk_rule",
    "sse_bond_information_portal",
}
EXPECTED_AUGMENTATION_KEYS = {
    "sse_company_bond_listing_rule_body",
    "sse_company_bond_credit_risk_rule_body",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    failures: list[str] = []
    if not MANIFEST_PATH.is_file() or _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST:
        failures.append("C18 source manifest mismatch")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    records = {str(row.get("source_key")): row for row in manifest.get("records", []) if isinstance(row, dict)}
    if set(records) != EXPECTED_KEYS:
        failures.append("C18 source-key coverage differs")
    for key, record in records.items():
        path = REPO_ROOT / str(record.get("path"))
        if not path.is_file() or _sha256(path) != record.get("sha256"):
            failures.append(f"source hash mismatch: {key}")
    if not AUGMENTATION_MANIFEST_PATH.is_file() or _sha256(AUGMENTATION_MANIFEST_PATH) != EXPECTED_AUGMENTATION_MANIFEST:
        failures.append("C18 rule-text augmentation manifest mismatch")
    augmentation = json.loads(AUGMENTATION_MANIFEST_PATH.read_text(encoding="utf-8"))
    augmentation_records = {str(row.get("source_key")): row for row in augmentation.get("records", []) if isinstance(row, dict)}
    if set(augmentation_records) != EXPECTED_AUGMENTATION_KEYS:
        failures.append("C18 rule-text augmentation coverage differs")
    for key, record in augmentation_records.items():
        path = REPO_ROOT / str(record.get("path"))
        if not path.is_file() or _sha256(path) != record.get("sha256"):
            failures.append(f"rule-text source hash mismatch: {key}")
    report = json.loads(FEASIBILITY_PATH.read_text(encoding="utf-8"))
    source_control = report.get("source_control", {})
    if source_control.get("initial_preflight_manifest", {}).get("sha256") != EXPECTED_MANIFEST:
        failures.append("C18 feasibility initial-preflight source control differs")
    if source_control.get("rule_text_augmentation_manifest", {}).get("sha256") != EXPECTED_AUGMENTATION_MANIFEST:
        failures.append("C18 feasibility rule-text source control differs")
    if report.get("status") != "SOURCE_PREFLIGHT_PASS_HISTORICAL_UNIVERSE_AND_RETURN_TEST_NOT_READY":
        failures.append("C18 feasibility status changed")
    if report.get("research_only") is not True or report.get("formal_decision_eligible") is not False or report.get("external_orders") is not False or report.get("portfolio_q") != 0:
        failures.append("C18 action boundary changed")
    current = report.get("current_disposition", {})
    if current.get("state") != "NO_BOND_SELECTED_NO_HISTORICAL_TEST_NO_ACTION":
        failures.append("C18 current disposition changed")
    if report.get("strict_screen_boundary", {}).get("current_result") != "NOT_TESTABLE_FOR_RETURN":
        failures.append("C18 return-test boundary changed")
    state = "PASS" if not failures else "FAIL"
    print(f"C18 COMPANY-BOND FEASIBILITY: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
