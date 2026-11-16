#!/usr/bin/env python3
"""Independently reconstruct C16 from frozen raw contracts and protocol.

This file intentionally does not import C16's runner.  It separately parses
the compressed exchange responses, re-selects every weekly actual contract,
rebuilds the marked book and compares the entire daily curve, annual rows and
five-calendar-year endpoints with the published C16 artifact.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import median
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c15-shfe-actual-contract-eod-2019-2025-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
PROTOCOL_PATH = CASE_DIR / "analysis" / "c16_actual_contract_settlement_diagnostic_protocol_20260815.json"
C16_PATH = CASE_DIR / "analysis" / "c16_actual_contract_settlement_diagnostic_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r04_independent_c16_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r04_independent_c16_audit_20260815.md"
EXPECTED_MANIFEST = "34e23ddf886bd1f1f6cb88610d8d730bd757c981b92b0aa51720c5471b1186d7"
EXPECTED_PROTOCOL = "132c34e21eaf868ff50d8654277296059faba9aa54f93498b8d4d571a0f4814c"
FAMILIES = ("AU", "CU", "RU")
TOLERANCE = 1e-10


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, contents: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(path)


def _relative(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _close(left: float, right: float) -> bool:
    return math.isclose(float(left), float(right), abs_tol=TOLERANCE, rel_tol=0.0)


def _positive(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) and parsed > 0.0 else None


def _family(row: dict[str, Any]) -> str:
    return str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()


def _delivery(delivery: str) -> date:
    return date(2000 + int(delivery[:2]), int(delivery[2:]), 15)


def _safe_year_shift(value: date) -> date:
    try:
        return value.replace(year=value.year - 5)
    except ValueError:
        return value.replace(year=value.year - 5, day=28)


def _build_raw_panel(failures: list[str]) -> tuple[list[date], dict[date, dict[str, dict[str, dict[str, float | str]]]], dict[str, list[dict[str, float | str | date]]]]:
    manifest = _read(MANIFEST_PATH)
    if _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST:
        failures.append("source manifest hash changed")
    dates: list[date] = []
    panel: dict[date, dict[str, dict[str, dict[str, float | str]]]] = {}
    history: dict[str, list[dict[str, float | str | date]]] = defaultdict(list)
    for record in sorted(manifest.get("records", []), key=lambda item: str(item.get("trade_date"))):
        trade_date = date.fromisoformat(str(record["trade_date"]))
        source_path = REPO_ROOT / str(record["path"])
        compressed = source_path.read_bytes()
        if hashlib.sha256(compressed).hexdigest() != record.get("compressed_sha256"):
            failures.append(f"compressed source mismatch: {trade_date}")
            continue
        raw = gzip.decompress(compressed)
        if hashlib.sha256(raw).hexdigest() != record.get("raw_sha256"):
            failures.append(f"raw source mismatch: {trade_date}")
            continue
        document = json.loads(raw.decode("utf-8"))
        if str(document.get("report_date") or "") != trade_date.strftime("%Y%m%d"):
            failures.append(f"reported date differs: {trade_date}")
            continue
        cells: dict[str, dict[str, dict[str, float | str]]] = {family: {} for family in FAMILIES}
        for raw_row in document.get("o_curinstrument", []):
            if not isinstance(raw_row, dict):
                continue
            family = _family(raw_row)
            delivery = str(raw_row.get("DELIVERYMONTH") or "").strip()
            if family not in cells or delivery in {"", "小计", "合计"}:
                continue
            parsed = {field: _positive(raw_row.get(field)) for field in ("SETTLEMENTPRICE", "OPENPRICE", "HIGHESTPRICE", "LOWESTPRICE", "VOLUME", "OPENINTEREST")}
            if any(value is None for value in parsed.values()):
                continue
            contract = f"{family}{delivery}"
            cell: dict[str, float | str] = {
                "contract": contract,
                "family": family,
                "delivery_month": delivery,
                "settlement": float(parsed["SETTLEMENTPRICE"]),
                "open": float(parsed["OPENPRICE"]),
                "high": float(parsed["HIGHESTPRICE"]),
                "low": float(parsed["LOWESTPRICE"]),
                "volume": float(parsed["VOLUME"]),
                "open_interest": float(parsed["OPENINTEREST"]),
            }
            if contract in cells[family]:
                failures.append(f"duplicate contract: {trade_date} {contract}")
                continue
            cells[family][contract] = cell
            history[contract].append({"date": trade_date, **cell})
        if any(not cells[family] for family in FAMILIES):
            failures.append(f"missing candidate family cells: {trade_date}")
            continue
        dates.append(trade_date)
        panel[trade_date] = cells
    return dates, panel, history


def _history_at(history: list[dict[str, float | str | date]], signal_date: date) -> list[dict[str, float | str | date]]:
    return [row for row in history if row["date"] <= signal_date]


def _select(protocol: dict[str, Any], signal_date: date, family: str, panel: dict[date, dict[str, dict[str, dict[str, float | str]]]], history: dict[str, list[dict[str, float | str | date]]]) -> dict[str, Any]:
    rule = protocol["weekly_signal"]
    requirement = rule["required_history"]
    eligible: list[dict[str, Any]] = []
    for cell in panel[signal_date][family].values():
        days = (_delivery(str(cell["delivery_month"])) - signal_date).days
        if not int(rule["eligible_scheduled_days_to_delivery"]["minimum"]) <= days <= int(rule["eligible_scheduled_days_to_delivery"]["maximum"]):
            continue
        if float(cell["open_interest"]) < float(requirement["minimum_current_open_interest"]):
            continue
        observations = _history_at(history[str(cell["contract"])], signal_date)
        needed = int(requirement["same_actual_contract_valid_settlement_observations_including_signal"])
        if len(observations) < needed:
            continue
        if len(observations[-int(requirement["same_actual_contract_valid_ohlc_observations"]):]) < int(requirement["same_actual_contract_valid_ohlc_observations"]):
            continue
        if median(float(row["volume"]) for row in observations[-int(requirement["same_actual_contract_volume_median_observations"]):]) < float(requirement["minimum_median_volume"]):
            continue
        slow = float(cell["settlement"]) / float(observations[-needed]["settlement"]) - 1.0
        fast_lookback = int(rule["fast_signal"]["lookback_valid_observations"])
        if len(observations) < fast_lookback + 1:
            continue
        fast = float(cell["settlement"]) / float(observations[-(fast_lookback + 1)]["settlement"]) - 1.0
        direction = 0
        if slow >= float(rule["slow_signal"]["long_at_or_above"]) and fast >= float(rule["fast_signal"]["long_at_or_above"]):
            direction = 1
        elif slow <= float(rule["slow_signal"]["short_at_or_below"]) and fast <= float(rule["fast_signal"]["short_at_or_below"]):
            direction = -1
        eligible.append({"contract": str(cell["contract"]), "delivery_month": str(cell["delivery_month"]), "open_interest": float(cell["open_interest"]), "volume": float(cell["volume"]), "slow": slow, "fast": fast, "direction": direction})
    if not eligible:
        return {"contract": None, "direction": 0}
    eligible.sort(key=lambda row: (-row["open_interest"], -row["volume"], row["delivery_month"]))
    return eligible[0]


def _weekly_dates(dates: list[date]) -> set[date]:
    weeks: dict[tuple[int, int], date] = {}
    for current in dates:
        year, week, _ = current.isocalendar()
        weeks[(year, week)] = current
    return set(weeks.values())


def _calculate_annual(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for year in sorted({value.year for value in dates}):
        relevant = [value for value in dates if value.year == year]
        prior = [value for value in dates if value < relevant[0]]
        source_covered = bool(
            prior
            and relevant[0] <= date(year, 1, 7)
            and relevant[-1] >= date(year, 12, 24)
            and all(value in curve for value in relevant)
        )
        result.append({"year": year, "source_covered": source_covered, "gross_settlement_mark_change": None if not source_covered else curve[relevant[-1]] / curve[prior[-1]] - 1.0})
    return result


def _calculate_rolling(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    end_by_month: dict[tuple[int, int], date] = {}
    for current in dates:
        end_by_month[(current.year, current.month)] = current
    positions = {current: index for index, current in enumerate(dates)}
    result: list[dict[str, Any]] = []
    for end in end_by_month.values():
        target = _safe_year_shift(end)
        candidates = [current for current in dates if current <= target]
        if not candidates:
            continue
        start = candidates[-1]
        intervals = positions[end] - positions[start]
        response_count = intervals + 1
        days = (end - start).days
        if response_count < 1200 or days <= 0:
            continue
        result.append({"start_date": start.isoformat(), "end_date": end.isoformat(), "retained_observation_intervals": intervals, "retained_response_count": response_count, "calendar_days": days, "annualized_gross_settlement_mark_change": (curve[end] / curve[start]) ** (365.2425 / days) - 1.0})
    return result


def _audit() -> dict[str, Any]:
    failures: list[str] = []
    protocol = _read(PROTOCOL_PATH)
    c16 = _read(C16_PATH)
    if _sha256(PROTOCOL_PATH) != EXPECTED_PROTOCOL:
        failures.append("frozen C16 protocol hash changed")
    if protocol.get("status") != "FROZEN_BEFORE_CALCULATION" or protocol.get("research_only") is not True:
        failures.append("C16 protocol boundary changed")
    if c16.get("research_only") is not True or c16.get("formal_decision_eligible") is not False or c16.get("external_orders") is not False or c16.get("portfolio_q") != 0:
        failures.append("C16 output action boundary changed")
    dates, panel, history = _build_raw_panel(failures)
    published_signals = {str(row["signal_date"]): row for row in c16.get("weekly_signal_records", [])}
    signal_dates = sorted(_weekly_dates(dates))
    expected_signal_dates = signal_dates[:-1]
    if set(published_signals) != {value.isoformat() for value in expected_signal_dates}:
        failures.append("published weekly signal-date set differs")
    targets: dict[date, dict[str, tuple[str, float]]] = {}
    direction_checks = 0
    for index, signal_date in enumerate(expected_signal_dates):
        published = published_signals.get(signal_date.isoformat())
        if published is None:
            continue
        effective = dates[dates.index(signal_date) + 1]
        if published.get("effective_date") != effective.isoformat():
            failures.append(f"effective date differs: {signal_date}")
        decisions = {str(row.get("family")): row for row in published.get("family_decisions", []) if isinstance(row, dict)}
        target: dict[str, tuple[str, float]] = {}
        for family in FAMILIES:
            expected = _select(protocol, signal_date, family, panel, history)
            actual = decisions.get(family, {})
            if actual.get("contract") != expected.get("contract") or int(actual.get("direction", 0)) != int(expected.get("direction", 0)):
                failures.append(f"selection differs: {signal_date} {family}")
            if expected.get("contract") is not None:
                selection = actual.get("selection", {})
                if not _close(selection.get("slow_signal", float("nan")), expected["slow"]) or not _close(selection.get("fast_signal", float("nan")), expected["fast"]):
                    failures.append(f"signal metric differs: {signal_date} {family}")
                direction_checks += 1
            if int(expected.get("direction", 0)) != 0 and expected.get("contract") is not None:
                target[family] = (str(expected["contract"]), float(expected["direction"]) / 3.0)
        targets[effective] = target
    curve: dict[date, float] = {}
    value = 1.0
    peak = 1.0
    drawdown = 0.0
    positions: dict[str, tuple[str, float]] = {}
    reconstructed_daily: dict[str, float] = {}
    for index, current in enumerate(dates):
        daily_change = 0.0
        if index:
            prior = dates[index - 1]
            for family, (contract, signed_weight) in positions.items():
                left = panel[prior][family].get(contract)
                right = panel[current][family].get(contract)
                if left is None or right is None:
                    failures.append(f"missing mark in independent replay: {prior} {current} {family} {contract}")
                    continue
                daily_change += signed_weight * (float(right["settlement"]) / float(left["settlement"]) - 1.0)
        value *= 1.0 + daily_change
        peak = max(peak, value)
        drawdown = min(drawdown, value / peak - 1.0)
        if current in targets:
            positions = targets[current]
        curve[current] = value
        reconstructed_daily[current.isoformat()] = value
    published_daily = {str(row["date"]): row for row in c16.get("daily_unitized_marks", [])}
    if set(published_daily) != set(reconstructed_daily):
        failures.append("published daily curve date set differs")
    for current, value_at_date in reconstructed_daily.items():
        if current not in published_daily or not _close(published_daily[current]["unit_value"], value_at_date):
            failures.append(f"daily unit value differs: {current}")
            break
    annual = _calculate_annual(dates, curve)
    published_annual = {int(row["year"]): row for row in c16.get("source_covered_calendar_years", [])}
    for row in annual:
        published = published_annual.get(row["year"])
        if published is None or published.get("source_covered") != row["source_covered"]:
            failures.append(f"annual row differs: {row['year']}")
        elif row["gross_settlement_mark_change"] is not None and not _close(published["gross_settlement_mark_change"], row["gross_settlement_mark_change"]):
            failures.append(f"annual value differs: {row['year']}")
    rolling = _calculate_rolling(dates, curve)
    published_rolling = {(row["start_date"], row["end_date"]): row for row in c16.get("rolling_five_calendar_year_endpoints", [])}
    if len(rolling) != len(published_rolling):
        failures.append("rolling endpoint count differs")
    for row in rolling:
        published = published_rolling.get((row["start_date"], row["end_date"]))
        if published is None or not _close(published["annualized_gross_settlement_mark_change"], row["annualized_gross_settlement_mark_change"]):
            failures.append(f"rolling value differs: {row['end_date']}")
    metrics = c16.get("full_period_metrics", {})
    if not _close(metrics.get("final_unit_value", float("nan")), value) or not _close(metrics.get("maximum_drawdown", float("nan")), drawdown):
        failures.append("full-period metric differs")
    annual_failures = [row["year"] for row in annual if row["source_covered"] and float(row["gross_settlement_mark_change"]) < 0.05]
    rolling_pass = sum(float(row["annualized_gross_settlement_mark_change"]) >= 0.05 for row in rolling)
    diagnostic = c16.get("five_percent_research_diagnostic", {})
    if diagnostic.get("complete_year_below_5pct") != annual_failures or diagnostic.get("rolling_endpoint_at_or_above_5pct") != rolling_pass or diagnostic.get("rolling_endpoint_count") != len(rolling):
        failures.append("strict-screen summary differs")
    if diagnostic.get("state") != "HURDLE_NOT_MET_IN_GROSS_ACTUAL_CONTRACT_SETTLEMENT_DIAGNOSTIC":
        failures.append("C16 screen state was promoted or changed")
    return {
        "schema_version": "independent_c16_actual_contract_audit.v1",
        "artifact_id": "D5PT-R04-v2",
        "as_of": "2026-08-15",
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_control": {"manifest_path": _relative(MANIFEST_PATH), "manifest_sha256": _sha256(MANIFEST_PATH), "protocol_path": _relative(PROTOCOL_PATH), "protocol_sha256": _sha256(PROTOCOL_PATH), "raw_dates_reconstructed": len(dates)},
        "independent_reconstruction": {"weekly_signals": len(expected_signal_dates), "selected_actual_contract_direction_checks": direction_checks, "final_unit_value": value, "maximum_drawdown": drawdown, "complete_year_below_5pct": annual_failures, "rolling_endpoint_count": len(rolling), "rolling_endpoint_at_or_above_5pct": rolling_pass},
        "boundary": "The audit validates a bounded gross settlement-mark calculation only. It does not establish fills, costs, margin, account access, investor net result, stable return or external action.",
    }


def _markdown(result: dict[str, Any]) -> str:
    reconstruction = result["independent_reconstruction"]
    failures = "无。" if not result["failures"] else "\n".join(f"- {item}" for item in result["failures"])
    years = "、".join(str(year) for year in reconstruction["complete_year_below_5pct"]) or "无"
    return f"""# R04 独立审计：C16 实际合约结算价诊断

- 审计结果：`{result['result']}`
- 方法：不导入 C16 运行程序，直接解压并核验全部 `{result['source_control']['raw_dates_reconstructed']}` 份留存交易所响应，独立重选每周实际合约、重建生效时点和每日结算价记账。

| 项目 | 独立结果 |
|---|---:|
| 周度信号 | {reconstruction['weekly_signals']} |
| 已复核的实际合约方向选择 | {reconstruction['selected_actual_contract_direction_checks']} |
| 期末单位化值 | {reconstruction['final_unit_value']:.4f} |
| 最大回撤 | {reconstruction['maximum_drawdown']:.2%} |
| 源覆盖全年低于 5% | {years} |
| 滚动五个日历年端点达到 5% | {reconstruction['rolling_endpoint_at_or_above_5pct']}/{reconstruction['rolling_endpoint_count']} |

## 未通过项

{failures}

复算通过只说明冻结协议、保留的实际合约结算价和已发布的 C16 算术相互一致。它不增加任何成交、费用、保证金、账户、个人净结果或稳定收益证据。
"""


def main() -> int:
    result = _audit()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"R04 independent C16 audit: {result['result']}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
