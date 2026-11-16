#!/usr/bin/env python3
"""Check R01's fixed definition, M01 boundary, P01 dependency and ledger schema."""

from __future__ import annotations

import csv
import json
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
RULE = CASE_DIR / "analysis" / "r01_monthly_dynamic_etf_paper_rulebook_20260815.json"
RULE_MD = CASE_DIR / "analysis" / "r01_monthly_dynamic_etf_paper_rulebook_20260815.md"
P01 = CASE_DIR / "analysis" / "p01_core_etf_product_diligence_20260815.json"
M01 = CASE_DIR / "analysis" / "m01_dynamic_market_price_proxy_20260815.json"
LEDGER_JSON = CASE_DIR / "data" / "r01_paper_observation_ledger_template.json"
LEDGER_CSV = CASE_DIR / "data" / "r01_paper_observation_ledger_template.csv"
CODES = {"510300", "510880", "511010", "518880", "511990"}
FORBIDDEN = ("本金", "初始资金", "初始金额", "initial capital", "initial_capital", "principal", "starting amount")


def _check_weights(vector: dict[str, float]) -> bool:
    return set(vector) == CODES and abs(sum(float(value) for value in vector.values()) - 1.0) < 1e-8 and all(float(value) >= 0.0 for value in vector.values())


def main() -> int:
    failures: list[str] = []
    for path in (RULE, RULE_MD, P01, M01, LEDGER_JSON, LEDGER_CSV):
        if not path.is_file():
            failures.append(f"missing R01 dependency: {path.name}")
    if not failures:
        rule = json.loads(RULE.read_text(encoding="utf-8"))
        p01 = json.loads(P01.read_text(encoding="utf-8"))
        m01 = json.loads(M01.read_text(encoding="utf-8"))
        ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
        if rule.get("artifact_id") != "D5PT-R01-v1":
            failures.append("unexpected R01 ID")
        if rule.get("status") != "paper_benchmark_only_not_stable_return_admission":
            failures.append("R01 must remain a paper benchmark rather than stable-return admission")
        if rule.get("external_orders") is not False or rule.get("annual_or_rolling_floor") != "not asserted":
            failures.append("R01 operating or return boundary changed")
        if set(rule.get("universe", {}).get("equity", {}).get("codes", [])) != {"510300", "510880"}:
            failures.append("R01 equity sleeve differs")
        if rule.get("universe", {}).get("bond", {}).get("code") != "511010" or rule.get("universe", {}).get("gold", {}).get("code") != "518880" or rule.get("universe", {}).get("fallback", {}).get("code") != "511990":
            failures.append("R01 fixed sleeves differ")
        matrix = rule.get("target_matrix", {})
        if set(matrix) != {"equity_bond_gold", "equity_bond", "equity_gold", "bond_gold", "equity", "bond", "gold", "none"}:
            failures.append("R01 target state set differs")
        for name, vector in matrix.items():
            if not isinstance(vector, dict) or not _check_weights(vector):
                failures.append(f"invalid target vector: {name}")
        if p01.get("status") != "paper_admission_pending":
            failures.append("P01 status does not preserve paper-admission boundary")
        if m01.get("five_percent_research_diagnostic", {}).get("state") != "HURDLE_NOT_MET_IN_EXPLORATORY_PRICE_PROXY":
            failures.append("M01 boundary differs; R01 must not be promoted")
        if set(ledger.get("required_fields", [])) != set(next(csv.reader(LEDGER_CSV.read_text(encoding="utf-8").splitlines()))):
            failures.append("ledger JSON/CSV fields differ")
        if "no_action" not in ledger.get("allowed_paper_fill_status", []):
            failures.append("ledger lacks no-action status")
    for path in (RULE, RULE_MD, LEDGER_JSON, LEDGER_CSV):
        if path.is_file():
            lower = path.read_text(encoding="utf-8").lower()
            for term in FORBIDDEN:
                if term.lower() in lower:
                    failures.append(f"forbidden reader term in {path.name}")
    if failures:
        print("R01 MONTHLY ETF PAPER RULEBOOK: FAIL")
        print("\n".join(failures))
        return 1
    print("R01 MONTHLY ETF PAPER RULEBOOK: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
