#!/usr/bin/env python3
"""Independently verify the R03 open-universe bridge disposition."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
STRICT_CASE = CASE_DIR.parent / "domestic-personal-securities-futures-strategy-20260814"
R11_PATH = STRICT_CASE / "analysis" / "r11_open_universe_candidate_disposition_20260815.json"
R12_PATH = STRICT_CASE / "analysis" / "r12_independent_r11_disposition_audit_20260815.json"
M01_PATH = CASE_DIR / "analysis" / "m01_dynamic_market_price_proxy_20260815.json"
R01_PATH = CASE_DIR / "analysis" / "r01_monthly_dynamic_etf_paper_rulebook_20260815.json"
R02_PATH = CASE_DIR / "analysis" / "r02_independent_m01_r01_audit_20260815.json"
R03_PATH = CASE_DIR / "analysis" / "r03_open_universe_bridge_disposition_20260815.json"
EXPECTED = {
    R11_PATH: "219cb4a2862111fac1920f8d84d4094e4770472a454657031530d41737f76660",
    R12_PATH: "2f4cd06b789f251b336ab0b1e4f53ab0817a7c259ec3992bdd7b0753aeb296b2",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def main() -> int:
    failures: list[str] = []
    for path, expected in EXPECTED.items():
        if not path.is_file() or _sha256(path) != expected:
            failures.append(f"sealed predecessor mismatch: {path.name}")
    try:
        r11, r12, m01, r01, r02, r03 = (_read(path) for path in (R11_PATH, R12_PATH, M01_PATH, R01_PATH, R02_PATH, R03_PATH))
    except (OSError, json.JSONDecodeError) as error:
        failures.append(f"required artifact cannot be read: {error}")
        r11 = r12 = m01 = r01 = r02 = r03 = {}
    expected_rows = {str(row.get("candidate_id")) for row in r11.get("rows", []) if isinstance(row, dict)}
    output_rows = {str(row.get("candidate_id")) for row in r03.get("inherited_representative_routes", []) if isinstance(row, dict)}
    if expected_rows != set(f"C{n}" for n in range(7, 15)) or output_rows != expected_rows:
        failures.append("candidate coverage differs from sealed R11")
    if r12.get("audit_status") != "PASS" or r02.get("result") != "PASS":
        failures.append("independent audit status is not passing")
    if any(row.get("admission_decision") != "不准入" or row.get("portfolio_q") != 0 for row in r11.get("rows", []) if isinstance(row, dict)):
        failures.append("sealed predecessor contains a promoted route")
    current = r03.get("current_paper_candidate", {})
    m01_years = [
        int(row["year"])
        for row in m01.get("complete_calendar_years", [])
        if row.get("complete") and float(row["market_price_proxy_change_after_illustrative_cost"]) < 0.05
    ]
    m01_rolling = m01.get("rolling_five_year_endpoints", [])
    m01_pass = sum(float(row["annualized_market_price_proxy_change_after_illustrative_cost"]) >= 0.05 for row in m01_rolling)
    observed = current.get("observed_proxy", {})
    if observed.get("annual_failure_years") != m01_years or observed.get("rolling_five_year_endpoints_at_or_above_5pct") != m01_pass or observed.get("rolling_five_year_endpoint_count") != len(m01_rolling):
        failures.append("R01 proxy facts differ from M01")
    if r01.get("status") != "paper_benchmark_only_not_stable_return_admission" or r01.get("external_orders") is not False or r01.get("annual_or_rolling_floor") != "not asserted":
        failures.append("R01 boundary changed")
    decision = r03.get("current_decision", {})
    if decision.get("status") != "NO_ADMITTED_USABLE_STRATEGY" or decision.get("portfolio_q") != 0 or decision.get("formal_decision_eligible") is not False or decision.get("external_orders") is not False:
        failures.append("R03 decision boundary changed")
    source_control = r03.get("source_control", {})
    if source_control.get("predecessor_r11", {}).get("path") != _relative(R11_PATH) or source_control.get("predecessor_r11", {}).get("sha256") != _sha256(R11_PATH):
        failures.append("R03 R11 source control differs")
    if source_control.get("predecessor_r12", {}).get("path") != _relative(R12_PATH) or source_control.get("predecessor_r12", {}).get("sha256") != _sha256(R12_PATH):
        failures.append("R03 R12 source control differs")
    result = "PASS" if not failures else "FAIL"
    print(f"R03 OPEN-UNIVERSE DISPOSITION: {result}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
