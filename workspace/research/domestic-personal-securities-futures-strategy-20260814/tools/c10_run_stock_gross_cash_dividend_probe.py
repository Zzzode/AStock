#!/usr/bin/env python3
"""Run C10's deliberately narrow fixed-stock gross cash-dividend diagnostic.

This is a negative-evidence test only.  It must never be represented as an
investor total-return backtest, a point-in-time selection simulation, or an
execution record.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c10-direct-equity-price-dividend-probe-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_PATH = CASE_DIR / "analysis" / "c10_stock_gross_cash_dividend_diagnostic_20260815.json"
WEIGHTS = {
    "600519": 0.30,
    "600900": 0.30,
    "601398": 0.25,
    "601088": 0.15,
}
YEARS = (2022, 2023, 2024, 2025)
NAMES = {
    "600519": "贵州茅台",
    "600900": "长江电力",
    "601398": "工商银行",
    "601088": "中国神华",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _parse_jsonp(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    start = raw.find("(") + 1
    end = raw.rfind(")")
    if start <= 0 or end <= start:
        raise ValueError(f"invalid JSONP: {path}")
    parsed = json.loads(raw[start:end])
    if not isinstance(parsed, dict):
        raise ValueError(f"JSONP object missing: {path}")
    return parsed


def _source_file(name: str) -> Path:
    path = SOURCE_DIR / name
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def _prices(code: str) -> list[list[float]]:
    parsed = _parse_jsonp(_source_file(f"sse_dayk_{code}_latest2000.jsonp"))
    rows = parsed.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"price rows unavailable: {code}")
    result: list[list[float]] = []
    for row in rows:
        if not (isinstance(row, list) and len(row) >= 5):
            raise ValueError(f"malformed price row: {code}")
        result.append([float(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4])])
    return result


def _dividends(code: str, year: int) -> list[dict[str, Any]]:
    parsed = _parse_jsonp(_source_file(f"sse_dividend_{code}_{year}.jsonp"))
    rows = parsed.get("result")
    if rows is None:
        rows = parsed.get("pageHelp", {}).get("data")
    if not isinstance(rows, list):
        raise ValueError(f"dividend rows unavailable: {code}/{year}")
    result: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError(f"malformed dividend row: {code}/{year}")
        if row.get("A_DIV_DATE") in (None, "-") or row.get("A_BEFR_TAX_DIV") in (None, "-"):
            continue
        result.append(
            {
                "ex_date": int(row["A_DIV_DATE"]),
                "record_date": str(row.get("A_REG_DATE", "")),
                "gross_cash_dividend_per_share": float(row["A_BEFR_TAX_DIV"]),
            }
        )
    return result


def _annual_component(code: str, year: int) -> dict[str, Any]:
    rows = _prices(code)
    start_boundary = year * 10_000 + 101
    end_boundary = year * 10_000 + 1231
    prior = [row for row in rows if row[0] < start_boundary]
    in_year = [row for row in rows if start_boundary <= row[0] <= end_boundary]
    if not prior or not in_year:
        raise ValueError(f"incomplete price window: {code}/{year}")
    start = prior[-1]
    end = in_year[-1]
    events = _dividends(code, year)
    cash = sum(event["gross_cash_dividend_per_share"] for event in events)
    price_only_return = end[4] / start[4] - 1.0
    gross_cash_return = (end[4] + cash) / start[4] - 1.0
    return {
        "code": code,
        "name": NAMES[code],
        "target_weight": WEIGHTS[code],
        "start_date": int(start[0]),
        "start_close": start[4],
        "end_date": int(end[0]),
        "end_close": end[4],
        "gross_cash_dividend_per_share": cash,
        "dividend_events": events,
        "price_only_return": price_only_return,
        "gross_cash_dividend_return": gross_cash_return,
    }


def _input_fingerprint() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    relevant_paths = {
        _relative(_source_file(f"sse_dayk_{code}_latest2000.jsonp"))
        for code in WEIGHTS
    }
    relevant_paths |= {
        _relative(_source_file(f"sse_dividend_{code}_{year}.jsonp"))
        for code in WEIGHTS
        for year in YEARS
    }
    records = [
        {key: item[key] for key in ("path", "bytes", "sha256")}
        for item in files
        if item.get("path") in relevant_paths
    ]
    if len(records) != len(relevant_paths):
        raise ValueError("source manifest misses a diagnostic input")
    return {
        "manifest_path": _relative(MANIFEST_PATH),
        "manifest_sha256": _sha256(MANIFEST_PATH),
        "raw_input_files": sorted(records, key=lambda item: item["path"]),
    }


def _build() -> dict[str, Any]:
    annual: list[dict[str, Any]] = []
    for year in YEARS:
        components = [_annual_component(code, year) for code in WEIGHTS]
        price_only = sum(item["target_weight"] * item["price_only_return"] for item in components)
        gross_cash = sum(
            item["target_weight"] * item["gross_cash_dividend_return"] for item in components
        )
        annual.append(
            {
                "year": year,
                "components": components,
                "fixed_target_weight_price_only_return": price_only,
                "fixed_target_weight_gross_cash_dividend_return": gross_cash,
            }
        )
    gross_cash_returns = [item["fixed_target_weight_gross_cash_dividend_return"] for item in annual]
    failing = [
        item["year"]
        for item in annual
        if item["fixed_target_weight_gross_cash_dividend_return"] < 0.05
    ]
    return {
        "artifact_id": "DPSFS-C10-PRICE-DIVIDEND-DIAGNOSTIC-v1",
        "artifact_class": "exploratory_historical_negative_evidence",
        "case_id": "domestic-personal-securities-futures-strategy-20260814",
        "as_of": "2026-08-15",
        "candidate_definition": {
            "type": "fixed four-name direct-A-share gross-cash diagnostic",
            "weights": WEIGHTS,
            "weight_sum": sum(WEIGHTS.values()),
            "calendar_reset": "fixed target weights assumed at the prior calendar-year close for arithmetic only",
            "cash_treatment": "gross cash dividends credited to the annual result without reinvestment, tax, cost, or fill assumptions",
            "selection_status": "chosen after the observed history; this is not a clean preregistration or a point-in-time selection simulation",
        },
        "input_boundary": {
            "price": "official SSE retrospectively retrieved raw daily closes; adjustment basis undisclosed",
            "dividends": "official SSE code/year cash-dividend event queries; incomplete corporate-action, payment, tax and entitlement ledger",
            "execution": "none: no bid/ask, depth, suspension state, fees, taxes, fills, settlement, account permission, or broker record",
        },
        "annual_results": annual,
        "annual_result_summary": {
            "complete_calendar_years": list(YEARS),
            "gross_cash_dividend_return_minimum": min(gross_cash_returns),
            "gross_cash_dividend_return_median": statistics.median(gross_cash_returns),
            "calendar_years_below_5pct": failing,
        },
        "strict_5pct_gate": {
            "criterion": "every complete calendar year and every complete rolling five-year annualized endpoint must be at or above 5% after all relevant investor-level effects",
            "calendar_year_condition": "falsified_for_this_exploratory_gross_cash_diagnostic" if failing else "not_falsified_by_this_diagnostic",
            "falsifying_years": failing,
            "rolling_five_year_condition": "not_adjudicated: only four complete calendar years are represented and the inputs are not a total-return/PIT/execution dataset",
            "verdict": (
                "NO_STRICT_GATE_PASS: at least one complete calendar year is below 5% in the gross cash-dividend diagnostic; "
                "the missing formal inputs independently prohibit a validation claim."
                if failing
                else "NOT_VALIDATED: no formal total-return/PIT/execution dataset is present."
            ),
        },
        "non_waivable_limitations": [
            "Raw SSE close adjustment basis is undisclosed. The price-plus-cash arithmetic cannot be called investor total return.",
            "The candidate was selected after the observed history; positive observations would have no validation force.",
            "The calculation omits tax, fees, bid/ask spread, market impact, no fills, suspension/resumption, settlement, and all account-specific effects.",
            "A negative calendar-year result is adverse evidence for the strict claim, not an estimate of any individual's realised outcome.",
        ],
        "source_fingerprint": _input_fingerprint(),
    }


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _write(result: dict[str, Any]) -> None:
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _verify(result: dict[str, Any]) -> None:
    if not OUTPUT_PATH.is_file():
        raise FileNotFoundError(OUTPUT_PATH)
    stored = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
    if _canonical(stored) != _canonical(result):
        raise ValueError("C10 gross cash-dividend diagnostic differs from a fresh recomputation")
    gate = result["strict_5pct_gate"]
    if gate["calendar_year_condition"] != "falsified_for_this_exploratory_gross_cash_diagnostic":
        raise ValueError("C10 diagnostic no longer shows the required negative calendar-year evidence")


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--run", action="store_true")
    mode.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    result = _build()
    if arguments.run:
        _write(result)
    _verify(result)
    print("C10 STOCK GROSS CASH-DIVIDEND DIAGNOSTIC: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
