#!/usr/bin/env python3
"""Verify C10 direct-equity diligence facts against frozen local inputs.

This is an integrity check only. A pass does not establish return, suitability,
data entitlement, executable liquidity, allocation approval, or an action.
"""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
DILIGENCE_PATH = CASE_DIR / "analysis/c10_direct_equity_quality_distribution_candidate_20260815.json"
DIAGNOSTIC_PATH = CASE_DIR / "analysis/c10_stock_gross_cash_dividend_diagnostic_20260815.json"
PRICE_DIR = CASE_DIR / "sources/c10-direct-equity-price-dividend-probe-20260815"
FIRST_PARTY_DIR = CASE_DIR / "sources/c10-direct-equity-first-party-20260815"

EXPECTED_CODES = ("600519", "600900", "601398", "601088")
EXPECTED_WEIGHTS = {
    "600519": 0.30,
    "600900": 0.30,
    "601398": 0.25,
    "601088": 0.15,
}
EXPECTED_YEARLY_GROSS_RESULTS = {
    2022: -0.0015359487341136888,
    2023: 0.13022341426359382,
    2024: 0.26154797397185703,
    2025: 0.02048252591528108,
}


def reject_duplicate_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_duplicate_object_keys)


def load_dayk(code: str) -> list[list[float]]:
    raw = (PRICE_DIR / f"sse_dayk_{code}_latest2000.jsonp").read_text(encoding="utf-8")
    start = raw.find("(")
    if start < 1 or not raw.endswith(")"):
        raise ValueError(f"unparseable JSONP for {code}")
    payload = json.loads(raw[start + 1 : -1])
    rows = payload.get("kline")
    if not isinstance(rows, list) or len(rows) < 20:
        raise ValueError(f"insufficient daily rows for {code}")
    return rows


def approx_equal(actual: float, expected: float, tolerance: float = 1e-8) -> bool:
    return abs(actual - expected) <= tolerance


def main() -> int:
    failures: list[str] = []
    try:
        diligence = load_json(DILIGENCE_PATH)
        diagnostic = load_json(DIAGNOSTIC_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print("C10 DIRECT EQUITY DILIGENCE: FAIL")
        print(f"cannot load canonical artifacts: {exc}")
        return 1

    if diligence.get("portfolio_q") != 0:
        failures.append("diligence must retain portfolio_q=0")
    if diligence.get("research_status") != "research_only_no_action":
        failures.append("diligence research status is not research-only/no-action")
    strict_gate = diligence.get("strict_return_gate", {})
    if strict_gate.get("verdict") != "NO_STRICT_GATE_PASS":
        failures.append("strict return gate must remain NO_STRICT_GATE_PASS")
    if strict_gate.get("falsifying_years") != [2022, 2025]:
        failures.append("strict return gate must retain the two falsifying years")

    basket = diligence.get("fixed_diligence_basket", {})
    if basket.get("weights_for_diagnostic_only") != EXPECTED_WEIGHTS:
        failures.append("diligence weights differ from the frozen diagnostic weights")
    cards = diligence.get("diligence_cards", [])
    cards_by_code = {
        card.get("code"): card for card in cards if isinstance(card, dict) and isinstance(card.get("code"), str)
    }
    if tuple(cards_by_code) != EXPECTED_CODES:
        failures.append("diligence cards must contain exactly the four expected codes in frozen order")

    excluded = diligence.get("excluded_probe", {})
    if excluded.get("code") != "600941" or excluded.get("status") != "excluded_from_the_four-name_basket_and_strict_return_test":
        failures.append("600941 source probe exclusion is absent or inconsistent")
    if not (FIRST_PARTY_DIR / "600941_china_mobile_2025_annual_report.pdf").is_file():
        failures.append("600941 exclusion source file is missing")

    diagnostic_weights = diagnostic.get("candidate_definition", {}).get("weights")
    if diagnostic_weights != EXPECTED_WEIGHTS:
        failures.append("diagnostic weights do not match the C10 frozen weights")
    diagnostic_years = {
        result.get("year"): result.get("fixed_target_weight_gross_cash_dividend_return")
        for result in diagnostic.get("annual_results", [])
        if isinstance(result, dict)
    }
    if set(diagnostic_years) != set(EXPECTED_YEARLY_GROSS_RESULTS):
        failures.append("diagnostic does not retain the expected complete calendar-year set")
    for year, expected in EXPECTED_YEARLY_GROSS_RESULTS.items():
        actual = diagnostic_years.get(year)
        if not isinstance(actual, (int, float)) or not approx_equal(float(actual), expected):
            failures.append(f"diagnostic gross result mismatch for {year}")

    annual_rows = diligence.get("negative_evidence", {}).get("annual_gross_cash_results", [])
    annual_by_year = {
        row.get("year"): row.get("fixed_target_weight_gross_cash_dividend_return")
        for row in annual_rows
        if isinstance(row, dict)
    }
    for year, expected in EXPECTED_YEARLY_GROSS_RESULTS.items():
        actual = annual_by_year.get(year)
        if not isinstance(actual, (int, float)) or not approx_equal(float(actual), expected):
            failures.append(f"diligence annual gross result mismatch for {year}")

    for code in EXPECTED_CODES:
        card = cards_by_code.get(code)
        if not isinstance(card, dict):
            continue
        try:
            rows = load_dayk(code)[-20:]
            raw_close = float(rows[-1][4])
            raw_volume_median = statistics.median(float(row[5]) for row in rows)
            amplitude_median = statistics.median(
                ((float(row[2]) / float(row[3])) - 1.0) * 100.0
                for row in rows
                if float(row[3]) != 0
            )
        except (IndexError, TypeError, ValueError, OSError, json.JSONDecodeError) as exc:
            failures.append(f"cannot derive daily snapshot for {code}: {exc}")
            continue
        snapshot = card.get("return_mechanism_and_snapshot", {})
        market = card.get("liquidity_and_market_structure_observation", {})
        if not approx_equal(float(snapshot.get("sse_raw_close_rmb", float("nan"))), raw_close):
            failures.append(f"raw close mismatch for {code}")
        if not approx_equal(float(market.get("median_raw_volume_field", float("nan"))), raw_volume_median):
            failures.append(f"raw volume median mismatch for {code}")
        if not approx_equal(float(market.get("median_intraday_amplitude_pct", float("nan"))), amplitude_median, 1e-4):
            failures.append(f"intraday amplitude median mismatch for {code}")

    prohibited_terms = ("\u672c\u91d1", "\u521d\u59cb\u8d44\u91d1")
    for path in (DILIGENCE_PATH, CASE_DIR / "analysis/c10_direct_equity_quality_distribution_candidate_20260815.md"):
        content = path.read_text(encoding="utf-8")
        for term in prohibited_terms:
            if term in content:
                failures.append(f"prohibited framing term {term!r} found in {path.name}")
        if re.search(r"保证.{0,16}5%|5%.{0,16}保证", content):
            failures.append(f"return-guarantee wording found in {path.name}")

    if failures:
        print("C10 DIRECT EQUITY DILIGENCE: FAIL")
        print("\n".join(failures))
        return 1
    print("C10 DIRECT EQUITY DILIGENCE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
