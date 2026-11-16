#!/usr/bin/env python3
"""Read-only consistency checks for C12 cash/futures-basis artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_MANIFEST = CASE_DIR / "sources" / "c12-official-cash-futures-basis-20260815" / "manifest.json"
ROUTE_PATH = CASE_DIR / "analysis" / "c12_cffex_actual_contract_route_20260815.json"
RULEBOOK_PATH = CASE_DIR / "analysis" / "c12_cash_futures_basis_rulebook_20260815.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c12_cash_futures_basis_feasibility_20260815.json"
MARKDOWN_PATHS = (
    CASE_DIR / "analysis" / "c12_cffex_actual_contract_route_20260815.md",
    CASE_DIR / "analysis" / "c12_cash_futures_basis_rulebook_20260815.md",
    CASE_DIR / "analysis" / "c12_cash_futures_basis_feasibility_20260815.md",
)


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
    route = _load(ROUTE_PATH)
    rulebook = _load(RULEBOOK_PATH)
    feasibility = _load(FEASIBILITY_PATH)

    _require(
        source.get("source_quality")
        == "primary_official_rule_product_disclosure_and_retrospective_actual_contract_samples",
        "source-quality label changed",
        failures,
    )
    files = source.get("files", [])
    _require(len(files) == 14, "source manifest must retain 14 files", failures)
    actual_csvs = [entry for entry in files if str(entry.get("format")) == "csv"]
    _require(len(actual_csvs) == 6, "source manifest must retain six actual-contract CSV samples", failures)
    for entry in files:
        path = REPO_ROOT / str(entry.get("path", ""))
        _require(path.is_file(), f"missing source file: {path}", failures)
        if path.is_file():
            raw = path.read_bytes()
            _require(len(raw) == entry.get("bytes"), f"source size mismatch: {path}", failures)
            _require(_sha256(raw) == entry.get("sha256"), f"source hash mismatch: {path}", failures)
    expected_freeze = [
        {"path": entry.get("path"), "bytes": entry.get("bytes"), "sha256": entry.get("sha256")}
        for entry in files
    ]
    _require(
        source.get("source_freeze", {}).get("frozen_files") == expected_freeze,
        "source-freeze rows differ from manifest rows",
        failures,
    )

    source_route = route.get("actual_contract_source_route", {})
    _require(
        source_route.get("status") == "SIX_RETROSPECTIVE_SAMPLES_OBSERVED_NOT_REPLAY_READY",
        "actual-contract route must remain a six-sample non-replay observation",
        failures,
    )
    _require(route.get("not_a_backtest") is True, "route must remain non-backtest", failures)
    _require(route.get("portfolio_q") == 0, "route portfolio_q must be zero", failures)
    samples = source_route.get("samples", [])
    _require(len(samples) == 6, "route must retain six samples", failures)
    selection = route.get("dated_t_family_research_screen", {})
    selected = selection.get("selected_actual_contract") or {}
    _require(selected.get("contract") == "T2612", "dated actual-T observation must remain T2612", failures)
    _require(
        selection.get("interpretation", {}).get("order_or_position") == "none",
        "dated screen must retain no order or position",
        failures,
    )
    _require(
        selection.get("interpretation", {}).get("return_or_backtest") == "none",
        "dated screen must retain no return/backtest",
        failures,
    )

    _require(
        rulebook.get("status") == "RESEARCH_SPECIFICATION_NOT_ACTION_READY",
        "rulebook must remain research-only and not action-ready",
        failures,
    )
    _require(rulebook.get("portfolio_q") == 0, "rulebook portfolio_q must be zero", failures)
    _require(rulebook.get("formal_decision_eligible") is False, "rulebook must not be decision eligible", failures)
    _require(rulebook.get("orders_or_positions") == "none", "rulebook must retain no order or position", failures)
    target = rulebook.get("target_requirement", {})
    _require("5%" in target.get("hard_standard", ""), "rulebook missing hard 5% standard", failures)
    _require("not measured" in target.get("evidence_status", ""), "rulebook must not claim a measured return", failures)
    etf = rulebook.get("candidate_route", {}).get("exchange_traded_etf_substitute", {})
    _require(
        etf.get("classification") == "RELATIVE_VALUE_HEDGE_ONLY_NOT_DELIVERY_LINKED",
        "ETF substitute must remain non-delivery-linked",
        failures,
    )
    gate_ids = [entry.get("id") for entry in rulebook.get("no_action_gates", [])]
    _require(
        gate_ids == [f"C12-G{number}" for number in range(1, 10)],
        "rulebook no-action gates must retain C12-G1 through C12-G9",
        failures,
    )
    _require(
        all(entry.get("current_state") == "FAIL" for entry in rulebook.get("no_action_gates", [])),
        "no action gate may be passed under the current evidence",
        failures,
    )

    _require(
        feasibility.get("status") == "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION",
        "feasibility decision must remain NOT_FEASIBLE",
        failures,
    )
    _require(feasibility.get("portfolio_q") == 0, "feasibility portfolio_q must be zero", failures)
    _require(feasibility.get("formal_decision_eligible") is False, "feasibility must not be decision eligible", failures)
    _require(feasibility.get("return_result") is None, "feasibility must have no return result", failures)
    _require(feasibility.get("backtest_run") is False, "feasibility must retain no backtest", failures)
    _require(feasibility.get("orders_or_positions") == "none", "feasibility must retain no order or position", failures)
    blocker_ids = [entry.get("id") for entry in feasibility.get("blocking_requirements", [])]
    _require(
        blocker_ids == [f"C12-B{number}" for number in range(1, 11)],
        "feasibility blockers must retain C12-B1 through C12-B10",
        failures,
    )
    conclusion = feasibility.get("conclusion", {})
    for required_key in ("strict_target", "personal_execution", "cash_bond_delivery_route", "etf_substitute"):
        _require("NOT_FEASIBLE" in conclusion.get(required_key, ""), f"missing NOT_FEASIBLE conclusion: {required_key}", failures)
    _require(
        "No external order" in feasibility.get("no_action_statement", ""),
        "feasibility must retain an external-action prohibition",
        failures,
    )

    prohibited = (
        "本" + "金",
        "初始" + "资金",
        "initial " + "capital",
        "pri" + "ncipal",
        "starting " + "amount",
    )
    candidate_non_source_paths = [
        *sorted((CASE_DIR / "analysis").glob("c12_*")),
        *sorted((CASE_DIR / "tools").glob("c12_*")),
    ]
    for path in candidate_non_source_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore").lower()
        for phrase in prohibited:
            _require(
                phrase.lower() not in text,
                f"prohibited initial-amount framing in non-source artifact {path.name}: {phrase}",
                failures,
            )
    for markdown in MARKDOWN_PATHS:
        _require(markdown.is_file(), f"reader-facing markdown missing: {markdown}", failures)
    if failures:
        print("C12 CASH/FUTURES BASIS: FAIL")
        print("\n".join(failures))
        return 1
    print("C12 CASH/FUTURES BASIS: PASS")
    print("status=NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION")
    print("actual_contract_route=SIX_RETROSPECTIVE_SAMPLES_OBSERVED_NOT_REPLAY_READY")
    print("dated_t_observation=T2612")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
