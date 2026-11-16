#!/usr/bin/env python3
"""Independently verify the frozen C14 public-infrastructure-REIT artifacts."""

from __future__ import annotations

import hashlib
import json
import math
import re
from datetime import date
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c14-public-infrastructure-reit-508000-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
RULEBOOK_PATH = CASE_DIR / "analysis" / "c14_public_reit_rulebook_20260815.json"
FEASIBILITY_PATH = CASE_DIR / "analysis" / "c14_public_reit_feasibility_20260815.json"
MARKDOWN_PATHS = (
    CASE_DIR / "analysis" / "c14_public_reit_rulebook_20260815.md",
    CASE_DIR / "analysis" / "c14_public_reit_feasibility_20260815.md",
)
HURDLE = 0.05


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def parse_jsonp(path: Path, callback: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    matched = re.fullmatch(rf"{re.escape(callback)}\((.*)\)", text, flags=re.DOTALL)
    if not matched:
        raise ValueError(f"unexpected JSONP: {path.name}")
    return json.loads(matched.group(1))


def previous_or_same(prices: dict[date, float], target: date) -> tuple[date, float]:
    observed = max(day for day in prices if day <= target)
    return observed, prices[observed]


def add_years(observed: date, years: int) -> date:
    price_payload: dict[str, Any] = {}
    distribution_payload: dict[str, Any] = {}
    nav_payload: dict[str, Any] = {}
    try:
        return observed.replace(year=observed.year + years)
    except ValueError:
        return observed.replace(year=observed.year + years, month=2, day=28)


def cash_between(distributions: list[tuple[date, float]], start: date, end: date) -> float:
    return sum(value for exright, value in distributions if start < exright <= end)


def main() -> int:
    failures: list[str] = []
    required_paths = (MANIFEST_PATH, RULEBOOK_PATH, FEASIBILITY_PATH, *MARKDOWN_PATHS)
    for path in required_paths:
        require(path.is_file(), f"missing required C14 artifact: {path}", failures)
    if failures:
        print("C14 PUBLIC REIT: FAIL")
        print("\n".join(failures))
        return 1

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    files = manifest.get("files", [])
    frozen = manifest.get("source_freeze", {}).get("frozen_files", [])
    require(len(files) == 10, "C14 source manifest must retain exactly ten sources", failures)
    require(len(frozen) == len(files), "C14 source freeze count differs", failures)
    manifest_by_path = {item.get("path"): item for item in files}
    frozen_by_path = {item.get("path"): item for item in frozen}
    require(set(manifest_by_path) == set(frozen_by_path), "C14 manifest/freeze path sets differ", failures)
    for path_key, entry in manifest_by_path.items():
        raw_path = REPO_ROOT / str(path_key)
        require(raw_path.is_file(), f"C14 retained source absent: {path_key}", failures)
        if raw_path.is_file():
            require(raw_path.stat().st_size == entry.get("bytes"), f"C14 retained source size differs: {path_key}", failures)
            require(sha256(raw_path) == entry.get("sha256"), f"C14 retained source hash differs: {path_key}", failures)
            require(
                {key: entry.get(key) for key in ("path", "bytes", "sha256")}
                == {key: frozen_by_path.get(path_key, {}).get(key) for key in ("path", "bytes", "sha256")},
                f"C14 retained source freeze differs: {path_key}",
                failures,
            )

    price_path = SOURCE_DIR / "sse_508000_daily_market_price_begin0_end5000.jsonp"
    distribution_path = SOURCE_DIR / "sse_508000_distribution_history_page1.jsonp"
    nav_path = SOURCE_DIR / "sse_508000_nav_history_page1.jsonp"
    try:
        price_payload = parse_jsonp(price_path, "c14price")
        distribution_payload = parse_jsonp(distribution_path, "c14distribution")
        nav_payload = parse_jsonp(nav_path, "c14nav")
        prices = {
            date(int(str(row[0])[:4]), int(str(row[0])[4:6]), int(str(row[0])[6:])): float(row[4])
            for row in price_payload["kline"]
        }
        distributions = sorted(
            [
                (date.fromisoformat(str(row["exrightDate"])), float(row["fundDividends"]))
                for row in distribution_payload["result"]
            ]
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        failures.append(f"C14 raw data parse failed: {error}")
        prices = {}
        distributions = []
        nav_payload = {}

    require(price_payload.get("code") == "508000", "C14 price source code differs", failures)
    require(len(prices) == 1250, "C14 price source row count differs", failures)
    if prices:
        require(min(prices) == date(2021, 6, 21), "C14 price first date differs", failures)
        require(max(prices) == date(2026, 8, 14), "C14 price last date differs", failures)
    require(len(distributions) == 9, "C14 distribution source row count differs", failures)
    require(nav_payload.get("pageHelp", {}).get("total") == 0, "C14 NAV endpoint snapshot must remain empty", failures)

    rulebook = json.loads(RULEBOOK_PATH.read_text(encoding="utf-8"))
    feasibility = json.loads(FEASIBILITY_PATH.read_text(encoding="utf-8"))
    manifest_digest = sha256(MANIFEST_PATH)
    for payload, label in ((rulebook, "rulebook"), (feasibility, "feasibility")):
        require(payload.get("source_manifest", {}).get("sha256") == manifest_digest, f"C14 {label} manifest hash differs", failures)
        require(payload.get("portfolio_q") == 0, f"C14 {label} portfolio_q differs", failures)

    require(
        feasibility.get("status") == "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION",
        "C14 feasibility status differs",
        failures,
    )
    require(feasibility.get("formal_decision_eligible") is False, "C14 must remain formally ineligible", failures)
    require(feasibility.get("return_result") is None, "C14 must retain no personal net return result", failures)
    require(feasibility.get("backtest_run") is True, "C14 bounded replay run flag differs", failures)
    strict = feasibility.get("strict_5pct_test", {})
    require(strict.get("net_after_cost_status") == "NOT_ESTABLISHED_AND_NOT_ADMITTED", "C14 net strict-test state differs", failures)

    if prices and distributions:
        reconstructed_annual: dict[int, float] = {}
        for year in range(2022, 2026):
            start_day, start_close = previous_or_same(prices, date(year, 1, 1))
            end_day, end_close = previous_or_same(prices, date(year, 12, 31))
            reconstructed_annual[year] = (end_close + cash_between(distributions, start_day, end_day)) / start_close - 1.0
        expected_annual = {2022: 0.08268456375838906, 2023: -0.30670434112509637, 2024: 0.031084706784208604, 2025: 0.03843075715967048}
        for year, expected in expected_annual.items():
            require(abs(reconstructed_annual[year] - expected) < 1e-12, f"C14 independent annual recomputation differs: {year}", failures)

        replay_annual = rulebook.get("frozen_replay", {}).get("annual_rows", [])
        require(len(replay_annual) == 4, "C14 derived annual rows differ", failures)
        for row in replay_annual:
            year = row.get("year")
            require(year in reconstructed_annual, f"C14 unexpected annual row: {year}", failures)
            if year in reconstructed_annual:
                require(abs(float(row.get("gross_cost_free_cash_return", 0.0)) - reconstructed_annual[year]) < 1e-12, f"C14 stored annual replay differs: {year}", failures)

        rolling_values: list[float] = []
        cutoff = date(2026, 8, 14)
        for start_day in sorted(prices):
            nominal_end = add_years(start_day, 5)
            if nominal_end > cutoff:
                continue
            end_day, end_close = previous_or_same(prices, nominal_end)
            gross_factor = (end_close + cash_between(distributions, start_day, end_day)) / prices[start_day]
            rolling_values.append(math.pow(gross_factor, 1.0 / 5.0) - 1.0)
        require(len(rolling_values) == 40, "C14 independent rolling-window count differs", failures)
        require(all(value < HURDLE for value in rolling_values), "C14 independent rolling window unexpectedly meets gross hurdle", failures)
        gross = strict.get("gross_cost_free_diagnostic", {})
        require(gross.get("rolling_five_year_window_count") == 40, "C14 stored rolling-window count differs", failures)
        require(gross.get("rolling_five_year_failure_count") == 40, "C14 stored rolling failure count differs", failures)

    prohibited = ("本金", "初始资金", "initial capital", "initial_capital", "starting amount", "principal")
    for path in (*MARKDOWN_PATHS, RULEBOOK_PATH, FEASIBILITY_PATH):
        text = path.read_text(encoding="utf-8").lower()
        for term in prohibited:
            require(term.lower() not in text, f"C14 forbidden scope phrase {term!r}: {path.name}", failures)

    if failures:
        print("C14 PUBLIC REIT: FAIL")
        print("\n".join(failures))
        return 1
    print("C14 PUBLIC REIT: PASS")
    print("status=NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION")
    print("annual_gross_cost_free_failures=3")
    print("rolling_five_year_gross_cost_free_failures=40/40")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
