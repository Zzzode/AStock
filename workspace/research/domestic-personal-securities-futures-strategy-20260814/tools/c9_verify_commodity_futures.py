#!/usr/bin/env python3
"""Read-only consistency checks for C9 commodity-futures candidate artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_MANIFEST = CASE_DIR / "sources" / "c9-official-shfe-commodity-contracts-20260815" / "manifest.json"
RULEBOOK_PATH = CASE_DIR / "analysis" / "c9_commodity_actual_contract_trend_rulebook_20260815.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c9_commodity_actual_contract_feasibility_20260815.json"
SNAPSHOT_PATH = CASE_DIR / "analysis" / "c9_actual_contract_snapshot_20260815.json"


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def main() -> int:
    failures: list[str] = []
    source = _load(SOURCE_MANIFEST)
    rulebook = _load(RULEBOOK_PATH)
    feasibility = _load(FEASIBILITY_PATH)
    snapshot = _load(SNAPSHOT_PATH)

    _require(source.get("source_quality") == "primary_official_rule_text_and_retrospective_actual_contract_sample", "source quality label changed", failures)
    _require(len(source.get("files", [])) == 10, "C9 source manifest must contain ten retained official files", failures)
    for entry in source.get("files", []):
        path = REPO_ROOT / str(entry.get("path", ""))
        _require(path.is_file(), f"missing source file: {path}", failures)
        if path.is_file():
            raw = path.read_bytes()
            _require(len(raw) == entry.get("bytes"), f"source size mismatch: {path}", failures)
            _require(_sha256(raw) == entry.get("sha256"), f"source hash mismatch: {path}", failures)
    frozen = source.get("source_freeze", {}).get("frozen_files", [])
    expected_frozen = [
        {"path": x.get("path"), "bytes": x.get("bytes"), "sha256": x.get("sha256")}
        for x in source.get("files", [])
    ]
    _require(frozen == expected_frozen, "source freeze rows differ from source manifest", failures)

    _require(rulebook.get("status") == "RESEARCH_CANDIDATE_NOT_ACTION_READY", "rulebook status is not research-only", failures)
    _require(rulebook.get("portfolio_q") == 0, "rulebook portfolio_q must be zero", failures)
    _require(rulebook.get("formal_decision_eligible") is False, "rulebook must not be decision eligible", failures)
    _require(rulebook.get("orders_or_positions") == "none", "rulebook must retain no orders or positions", failures)
    _require(rulebook.get("return_objective", {}).get("annualized_hurdle") == "5%", "rulebook must describe the 5% target as a hurdle", failures)
    _require(rulebook.get("return_objective", {}).get("evidence_status") == "not measured because an actual-contract historical replay is not currently supported", "rulebook must not claim measured returns", failures)
    families = [item.get("family") for item in rulebook.get("product_families", [])]
    _require(families == ["CU", "AU", "RU"], "rulebook product basket must remain CU/AU/RU", failures)
    selection = rulebook.get("contract_selection_and_roll", {})
    eligibility = selection.get("eligible_actual_contract", [])
    eligibility_text = json.dumps(eligibility, ensure_ascii=False)
    for required in ("90 to 270", "65 valid prior settlements", "20 valid OHLC", "20-session median volume"):
        _require(required in eligibility_text, f"rulebook selection control missing: {required}", failures)
    _require("30 calendar days" in selection.get("delivery_firewall", ""), "rulebook delivery firewall changed", failures)
    signal = rulebook.get("signal", {})
    _require(signal.get("decision_rule", {}).get("long") == "slow_return >= +4% and fast_return >= 0%", "long signal changed", failures)
    _require(signal.get("decision_rule", {}).get("short") == "slow_return <= -4% and fast_return <= 0%", "short signal changed", failures)
    constraints = rulebook.get("risk_unit_and_target_position", {}).get("portfolio_constraints", [])
    constraints_text = json.dumps(constraints, ensure_ascii=False)
    for required in ("0.25%", "0.75%", "20%", "125%"):
        _require(required in constraints_text, f"risk constraint missing: {required}", failures)
    _require(rulebook.get("execution", {}).get("order_type") == "Limit only; no market order and no price-chasing after the window.", "limit-only control changed", failures)

    _require(feasibility.get("status") == "NOT_FEASIBLE_FOR_RETURN_CLAIM_OR_PERSONAL_ACTION_YET", "feasibility status changed", failures)
    _require(feasibility.get("portfolio_q") == 0, "feasibility portfolio_q must be zero", failures)
    _require(feasibility.get("formal_decision_eligible") is False, "feasibility must not be decision eligible", failures)
    _require(feasibility.get("return_result") is None and feasibility.get("backtest_run") is False, "feasibility must retain no return test", failures)
    blocker_ids = [row.get("id") for row in feasibility.get("blocking_requirements", [])]
    _require(blocker_ids == ["C9-B1", "C9-B2", "C9-B3", "C9-B4", "C9-B5", "C9-B6"], "blocking-requirement set changed", failures)

    snapshot_status = snapshot.get("actual_contract_source_route", {}).get("status")
    _require(snapshot_status == "SIX_RETROSPECTIVE_SAMPLES_OBSERVED_NOT_REPLAY_READY", "actual-contract source route status changed", failures)
    selection_rows = snapshot.get("dated_selection_snapshot", {}).get("selected_contracts", [])
    selected = [row.get("selected_contract") for row in selection_rows]
    _require(selected == ["CU2612", "AU2612", "RU2701"], "dated selection snapshot differs from frozen source calculation", failures)
    _require(snapshot.get("not_a_backtest") is True and snapshot.get("portfolio_q") == 0, "snapshot must remain a non-backtest research artifact", failures)

    prohibited = ("本金", "初始资金", "initial capital", "starting amount")
    for path in (RULEBOOK_PATH, FEASIBILITY_PATH):
        text = path.read_text(encoding="utf-8").lower()
        for phrase in prohibited:
            _require(phrase.lower() not in text, f"prohibited initial-amount framing in {path.name}: {phrase}", failures)

    if failures:
        print("C9 COMMODITY FUTURES: FAIL")
        print("\n".join(failures))
        return 1
    print("C9 COMMODITY FUTURES: PASS")
    print("status=RESEARCH_CANDIDATE_NOT_ACTION_READY")
    print("return_test=NOT_RUN")
    print("actual_contract_snapshot=CU2612,AU2612,RU2701")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
