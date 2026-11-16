#!/usr/bin/env python3
"""Read-only structural check for the A01 legacy-strategy audit pair."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
AUDIT_MD = CASE_DIR / "analysis" / "a01_legacy_strategy_audit.md"
AUDIT_JSON = CASE_DIR / "analysis" / "a01_legacy_strategy_audit.json"
EXPECTED_CLASSIFICATIONS = {
    "inherit",
    "inherit_with_refresh",
    "inherit_methodology_only",
    "retire",
    "retire_as_strategy_target",
    "historical_candidates_only",
    "non_actionable_for_starter_universe",
    "retire_as_target_evidence",
    "non_actionable_for_current_implementation",
}
FIXED_AMOUNT_PATTERNS = (
    re.compile(r"\bCNY\s*\d", re.IGNORECASE),
    re.compile(r"[¥￥]\s*\d"),
    re.compile(r"\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\s*(?:元|万元)?"),
    re.compile(r"\b\d+(?:\.\d+)?\s*(?:万元|亿元)"),
)
FORBIDDEN_LANGUAGE_PATTERNS = (
    re.compile("\\u672c\\u91d1"),
    re.compile("pri" + "ncipal", re.IGNORECASE),
)


def walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_values(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_values(child)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def validate_source_refs(payload: dict[str, Any], errors: list[str]) -> None:
    ref_count = 0
    for value in walk_values(payload):
        if not isinstance(value, dict) or "path" not in value or "line_ranges" not in value:
            continue
        ref_count += 1
        path_value = value["path"]
        ranges = value["line_ranges"]
        if not isinstance(path_value, str) or not path_value.startswith("workspace/"):
            fail(errors, f"invalid repo-relative source path: {path_value!r}")
            continue
        source_path = REPO_ROOT / path_value
        if not source_path.is_file():
            fail(errors, f"missing source reference: {path_value}")
            continue
        line_count = len(source_path.read_text(encoding="utf-8").splitlines())
        if not isinstance(ranges, list) or not ranges:
            fail(errors, f"missing line ranges: {path_value}")
            continue
        for line_range in ranges:
            if (
                not isinstance(line_range, list)
                or len(line_range) != 2
                or not all(isinstance(item, int) for item in line_range)
            ):
                fail(errors, f"invalid line range {line_range!r}: {path_value}")
                continue
            start, end = line_range
            if start < 1 or end < start or end > line_count:
                fail(errors, f"out-of-range anchor {start}-{end}/{line_count}: {path_value}")
    if ref_count < 9:
        fail(errors, f"expected at least nine source-reference blocks, found {ref_count}")


def main() -> int:
    errors: list[str] = []
    if not AUDIT_MD.is_file():
        fail(errors, f"missing markdown audit: {AUDIT_MD}")
    if not AUDIT_JSON.is_file():
        fail(errors, f"missing JSON audit: {AUDIT_JSON}")
    if errors:
        print("FAIL: " + "; ".join(errors))
        return 1

    markdown = AUDIT_MD.read_text(encoding="utf-8")
    try:
        payload = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: invalid JSON audit: {exc}")
        return 1

    required_top_level = {
        "schema_version",
        "audit_id",
        "scope",
        "overall_decision",
        "decision_table",
        "minimal_implementation_universe",
        "required_current_evidence",
        "self_check",
    }
    missing = sorted(required_top_level.difference(payload))
    if missing:
        fail(errors, f"missing JSON keys: {', '.join(missing)}")

    decision_table = payload.get("decision_table")
    if not isinstance(decision_table, list) or len(decision_table) < 9:
        fail(errors, "decision table must contain at least nine rows")
    else:
        classifications = {row.get("classification") for row in decision_table if isinstance(row, dict)}
        unknown = sorted(item for item in classifications if item not in EXPECTED_CLASSIFICATIONS)
        if unknown:
            fail(errors, f"unknown decision classifications: {', '.join(unknown)}")
        required = {"inherit", "retire", "historical_candidates_only", "non_actionable_for_current_implementation"}
        absent = sorted(required.difference(classifications))
        if absent:
            fail(errors, f"missing material decision classifications: {', '.join(absent)}")

    universe = payload.get("minimal_implementation_universe", {})
    if universe.get("open_universe") is not True:
        fail(errors, "minimal universe must be explicitly open")
    roles = universe.get("roles")
    if not isinstance(roles, list) or len(roles) < 6:
        fail(errors, "minimal universe must define six role rows")
    required_roles = {"liquidity_and_settlement", "rate_bond_core", "equity_core", "gold_diversifier"}
    actual_roles = {row.get("role") for row in roles if isinstance(row, dict)}
    missing_roles = sorted(required_roles.difference(actual_roles))
    if missing_roles:
        fail(errors, f"missing starter roles: {', '.join(missing_roles)}")

    combined_text = markdown + "\n" + json.dumps(payload, ensure_ascii=False)
    for pattern in FIXED_AMOUNT_PATTERNS:
        if pattern.search(combined_text):
            fail(errors, "prohibited amount-language token detected")
    for pattern in FORBIDDEN_LANGUAGE_PATTERNS:
        if pattern.search(combined_text):
            fail(errors, "prohibited amount-language token detected")
    if "非保证性规划目标" not in combined_text:
        fail(errors, "non-guaranteed planning-goal disclosure missing")
    if "cash_distribution_or_reinvestment_target" not in json.dumps(payload):
        fail(errors, "cash-distribution/reinvestment target constraint missing")
    if "A01-D04" not in markdown or "A01-D05" not in markdown:
        fail(errors, "markdown decision table is incomplete")

    validate_source_refs(payload, errors)

    if errors:
        print("FAIL: " + "; ".join(errors))
        return 1
    print("PASS: a01 legacy strategy audit is structurally complete; source anchors resolve; no prohibited amount-language token detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
