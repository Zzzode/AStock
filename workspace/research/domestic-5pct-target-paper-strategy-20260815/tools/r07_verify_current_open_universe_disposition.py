#!/usr/bin/env python3
"""Verify the source controls and no-action boundary of R07."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
R07_PATH = CASE_DIR / "analysis" / "r07_current_open_universe_disposition_20260815.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    report = json.loads(R07_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    if report.get("current_decision", {}).get("state") != "NO_ADMITTED_USABLE_STRATEGY":
        failures.append("current decision changed")
    if report.get("research_only") is not True or report.get("formal_decision_eligible") is not False or report.get("external_orders") is not False or report.get("portfolio_q") != 0:
        failures.append("action boundary changed")
    for name, control in report.get("source_control", {}).items():
        if not isinstance(control, dict):
            failures.append(f"invalid source control: {name}")
            continue
        path = CASE_DIR / str(control.get("path"))
        if not path.is_file() or _sha256(path) != control.get("sha256"):
            failures.append(f"source control mismatch: {name}")
    rows = {str(row.get("candidate_id")): row for row in report.get("completed_current_case_routes", []) if isinstance(row, dict)}
    if set(rows) != {"R01", "C16", "C17", "C18", "C20"}:
        failures.append("current route set changed")
    if rows.get("C16", {}).get("disposition", "").find("not admitted") < 0 or rows.get("C17", {}).get("disposition", "").find("not admitted") < 0:
        failures.append("actual-contract non-admission changed")
    if rows.get("C18", {}).get("strict_screen") != "NOT_TESTABLE_FOR_RETURN":
        failures.append("C18 testability boundary changed")
    if rows.get("C20", {}).get("strict_screen") != "NOT_TESTED_NOT_ADMITTED":
        failures.append("C20 testability boundary changed")
    exploratory = {
        str(row.get("candidate_id")): row
        for row in report.get("exploratory_open_universe_routes", [])
        if isinstance(row, dict)
    }
    if set(exploratory) != {"C23", "C24"}:
        failures.append("exploratory open-universe route set changed")
    if exploratory.get("C23", {}).get("strict_screen") != "NOT_TESTABLE_FOR_RETURN":
        failures.append("C23 testability boundary changed")
    if exploratory.get("C24", {}).get("strict_screen") != "NOT_TESTABLE_FOR_RETURN":
        failures.append("C24 testability boundary changed")
    state = "PASS" if not failures else "FAIL"
    print(f"R07 CURRENT OPEN-UNIVERSE DISPOSITION: {state}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
