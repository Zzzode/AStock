#!/usr/bin/env python3
"""Run the frozen C17 five-family actual-contract settlement-mark diagnostic.

This implementation deliberately accepts only actual SHFE contract rows.  It
does not create a continuous series, model fills or costs, or turn a research
calculation into an external action.
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
READINESS_PATH = CASE_DIR / "analysis" / "c15_shfe_actual_contract_eod_source_readiness_20260815.json"
P02_PATH = CASE_DIR / "analysis" / "p02_shfe_actual_contract_product_diligence_20260815.json"
P03_PATH = CASE_DIR / "analysis" / "p03_shfe_expanded_actual_contract_product_diligence_20260815.json"
PROTOCOL_PATH = CASE_DIR / "analysis" / "c17_diversified_actual_contract_settlement_protocol_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c17_diversified_actual_contract_settlement_diagnostic_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c17_diversified_actual_contract_settlement_diagnostic_20260815.md"
EXPECTED_MANIFEST_SHA256 = "34e23ddf886bd1f1f6cb88610d8d730bd757c981b92b0aa51720c5471b1186d7"
EXPECTED_READINESS_SHA256 = "5413d17d4db0654432d1e25e462dd51fd9c2a4591e94ee573f5cf4da70885470"
EXPECTED_PROTOCOL_SHA256 = "35f4b5c07bdde384673eba9c9e92943eadd89ee5760cad59ff9b42ec4d63d0d0"
EXPECTED_P03_SOURCE_SHA256 = "dbc39e8c0d3789cb88d2267dca285b1b4cf58f1ca65e235471e0c250d8c12ec8"
EXPECTED_P02_SHA256 = "603c6bc79de06b40913f7ad48c18346ecb19dad0c09fe9493de90c9b90357499"
EXPECTED_P03_SHA256 = "bf7deea405abc9957e2ef857921606d0488285a269dd5127e43dcc1b540dd9c6"
FAMILIES = ("AU", "CU", "RB", "RU", "SP")
WEIGHT = 0.2


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


def _family(row: dict[str, Any]) -> str:
    return str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()


def _positive(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0.0 else None


def _delivery_date(delivery: str) -> date:
    if len(delivery) != 4 or not delivery.isdigit():
        raise ValueError(f"invalid delivery month: {delivery!r}")
    return date(2000 + int(delivery[:2]), int(delivery[2:]), 15)


def _leap_safe_replace(value: date, year: int) -> date:
    try:
        return value.replace(year=year)
    except ValueError:
        return value.replace(year=year, day=28)


def _load_protocol() -> dict[str, Any]:
    if _sha256(PROTOCOL_PATH) != EXPECTED_PROTOCOL_SHA256:
        raise ValueError("C17 frozen protocol hash changed")
    protocol = _read(PROTOCOL_PATH)
    if protocol.get("status") != "FROZEN_BEFORE_CALCULATION":
        raise ValueError("C17 protocol is not frozen")
    if protocol.get("research_only") is not True or protocol.get("formal_decision_eligible") is not False or protocol.get("external_orders") is not False:
        raise ValueError("C17 research boundary changed")
    dependency = protocol.get("source_dependency", {})
    if dependency.get("actual_contract_manifest_sha256") != EXPECTED_MANIFEST_SHA256:
        raise ValueError("C17 actual-contract source dependency changed")
    if dependency.get("source_readiness_audit_sha256") != EXPECTED_READINESS_SHA256:
        raise ValueError("C17 source readiness dependency changed")
    if dependency.get("expanded_product_source_manifest_sha256") != EXPECTED_P03_SOURCE_SHA256:
        raise ValueError("C17 expanded-product source dependency changed")
    if dependency.get("legacy_product_diligence_sha256") != EXPECTED_P02_SHA256 or dependency.get("expanded_product_diligence_sha256") != EXPECTED_P03_SHA256:
        raise ValueError("C17 product-diligence artifact dependency changed")
    if tuple(protocol.get("universe", {}).get("families", [])) != FAMILIES:
        raise ValueError("C17 universe changed")
    if float(protocol.get("unitized_settlement_mark", {}).get("position_weight_per_active_family", 0.0)) != WEIGHT:
        raise ValueError("C17 diagnostic weight changed")
    return protocol


def _load_product_diligence() -> dict[str, str]:
    p02 = _read(P02_PATH)
    p03 = _read(P03_PATH)
    if p02.get("artifact_id") != "D5PT-P02-v1" or p02.get("research_only") is not True or p02.get("formal_decision_eligible") is not False:
        raise ValueError("C17 inherited product diligence boundary changed")
    if p03.get("artifact_id") != "D5PT-P03-v1" or p03.get("research_only") is not True or p03.get("formal_decision_eligible") is not False:
        raise ValueError("C17 expanded product diligence boundary changed")
    if p03.get("source_manifest", {}).get("sha256") != EXPECTED_P03_SOURCE_SHA256:
        raise ValueError("C17 P03 source control changed")
    hashes = {"P02": _sha256(P02_PATH), "P03": _sha256(P03_PATH)}
    if hashes != {"P02": EXPECTED_P02_SHA256, "P03": EXPECTED_P03_SHA256}:
        raise ValueError("C17 product-diligence artifact hash changed")
    return hashes


def _load_panel() -> tuple[list[date], dict[date, dict[str, dict[str, dict[str, Any]]]], dict[str, list[dict[str, Any]]], dict[tuple[date, str], int]]:
    if _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST_SHA256:
        raise ValueError("C15 manifest hash changed")
    readiness = _read(READINESS_PATH)
    if _sha256(READINESS_PATH) != EXPECTED_READINESS_SHA256 or readiness.get("result") != "PASS":
        raise ValueError("C15 source readiness audit is not the frozen passing record")
    manifest = _read(MANIFEST_PATH)
    panel: dict[date, dict[str, dict[str, dict[str, Any]]]] = {}
    histories: dict[str, list[dict[str, Any]]] = defaultdict(list)
    history_index: dict[tuple[date, str], int] = {}
    for record in sorted(manifest.get("records", []), key=lambda row: str(row["trade_date"])):
        current_date = date.fromisoformat(str(record["trade_date"]))
        raw_path = REPO_ROOT / str(record["path"])
        compressed = raw_path.read_bytes()
        if hashlib.sha256(compressed).hexdigest() != record.get("compressed_sha256"):
            raise ValueError(f"compressed source mismatch: {current_date}")
        raw = gzip.decompress(compressed)
        if hashlib.sha256(raw).hexdigest() != record.get("raw_sha256"):
            raise ValueError(f"raw source mismatch: {current_date}")
        payload = json.loads(raw.decode("utf-8"))
        if str(payload.get("report_date") or "") != current_date.strftime("%Y%m%d"):
            raise ValueError(f"report date mismatch: {current_date}")
        per_family: dict[str, dict[str, dict[str, Any]]] = {family: {} for family in FAMILIES}
        rows = payload.get("o_curinstrument")
        if not isinstance(rows, list):
            raise ValueError(f"missing contract rows: {current_date}")
        for raw_row in rows:
            if not isinstance(raw_row, dict):
                continue
            family = _family(raw_row)
            delivery = str(raw_row.get("DELIVERYMONTH") or "").strip()
            if family not in per_family or delivery in {"", "小计", "合计"}:
                continue
            settlement = _positive(raw_row.get("SETTLEMENTPRICE"))
            open_price = _positive(raw_row.get("OPENPRICE"))
            high = _positive(raw_row.get("HIGHESTPRICE"))
            low = _positive(raw_row.get("LOWESTPRICE"))
            volume = _positive(raw_row.get("VOLUME"))
            open_interest = _positive(raw_row.get("OPENINTEREST"))
            if None in {settlement, open_price, high, low, volume, open_interest}:
                continue
            contract = f"{family}{delivery}"
            if contract in per_family[family]:
                raise ValueError(f"duplicate actual contract: {current_date} {contract}")
            fields = {
                "contract": contract,
                "family": family,
                "delivery_month": delivery,
                "settlement": float(settlement),
                "open": float(open_price),
                "high": float(high),
                "low": float(low),
                "volume": float(volume),
                "open_interest": float(open_interest),
            }
            per_family[family][contract] = fields
            history_index[(current_date, contract)] = len(histories[contract])
            histories[contract].append({"date": current_date, **fields})
        missing = [family for family in FAMILIES if not per_family[family]]
        if missing:
            raise ValueError(f"family has no valid actual-contract rows: {current_date} {','.join(missing)}")
        panel[current_date] = per_family
    return sorted(panel), panel, histories, history_index


def _select_family(
    protocol: dict[str, Any],
    signal_date: date,
    family: str,
    panel: dict[date, dict[str, dict[str, dict[str, Any]]]],
    histories: dict[str, list[dict[str, Any]]],
    history_index: dict[tuple[date, str], int],
) -> dict[str, Any]:
    weekly = protocol["weekly_signal"]
    history_rules = weekly["required_history"]
    minimum_days = int(weekly["eligible_scheduled_days_to_delivery"]["minimum"])
    maximum_days = int(weekly["eligible_scheduled_days_to_delivery"]["maximum"])
    settlement_required = int(history_rules["same_actual_contract_valid_settlement_observations_including_signal"])
    ohlc_required = int(history_rules["same_actual_contract_valid_ohlc_observations"])
    volume_required = int(history_rules["same_actual_contract_volume_median_observations"])
    minimum_volume = float(history_rules["minimum_median_volume"])
    minimum_interest = float(history_rules["minimum_current_open_interest"])
    candidates: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    for contract, current in panel[signal_date][family].items():
        days = (_delivery_date(str(current["delivery_month"])) - signal_date).days
        if not minimum_days <= days <= maximum_days:
            reasons["scheduled_delivery_window"] += 1
            continue
        if float(current["open_interest"]) < minimum_interest:
            reasons["current_open_interest"] += 1
            continue
        history = histories[contract][: history_index[(signal_date, contract)] + 1]
        if len(history) < settlement_required:
            reasons["same_contract_settlement_history"] += 1
            continue
        latest_ohlc = history[-ohlc_required:]
        if len(latest_ohlc) < ohlc_required or any(float(item["open"]) <= 0 or float(item["high"]) <= 0 or float(item["low"]) <= 0 for item in latest_ohlc):
            reasons["same_contract_ohlc_history"] += 1
            continue
        latest_volumes = history[-volume_required:]
        if len(latest_volumes) < volume_required or median(float(item["volume"]) for item in latest_volumes) < minimum_volume:
            reasons["median_volume"] += 1
            continue
        slow = float(current["settlement"]) / float(history[-settlement_required]["settlement"]) - 1.0
        fast_lookback = int(weekly["fast_signal"]["lookback_valid_observations"])
        if len(history) < fast_lookback + 1:
            reasons["same_contract_fast_history"] += 1
            continue
        fast = float(current["settlement"]) / float(history[-(fast_lookback + 1)]["settlement"]) - 1.0
        direction = 0
        if slow >= float(weekly["slow_signal"]["long_at_or_above"]) and fast >= float(weekly["fast_signal"]["long_at_or_above"]):
            direction = 1
        elif slow <= float(weekly["slow_signal"]["short_at_or_below"]) and fast <= float(weekly["fast_signal"]["short_at_or_below"]):
            direction = -1
        candidates.append({**current, "scheduled_days_to_delivery": days, "slow_signal": slow, "fast_signal": fast, "direction": direction})
    if not candidates:
        return {"family": family, "contract": None, "direction": 0, "reason": "no_eligible_actual_contract", "rejection_counts": dict(sorted(reasons.items()))}
    candidates.sort(key=lambda row: (-float(row["open_interest"]), -float(row["volume"]), str(row["delivery_month"])))
    selected = candidates[0]
    return {"family": family, "contract": selected["contract"], "direction": int(selected["direction"]), "reason": "selected_actual_contract", "selection": selected, "eligible_candidate_count": len(candidates)}


def _weekly_signal_dates(dates: list[date]) -> set[date]:
    latest: dict[tuple[int, int], date] = {}
    for current in dates:
        year, week, _ = current.isocalendar()
        latest[(year, week)] = current
    return set(latest.values())


def _annual_rows(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in sorted({current.year for current in dates}):
        in_year = [current for current in dates if current.year == year]
        prior = [current for current in dates if current < in_year[0]]
        source_covered = bool(prior and in_year[0] <= date(year, 1, 7) and in_year[-1] >= date(year, 12, 24) and all(current in curve for current in in_year))
        rows.append({"year": year, "source_covered": source_covered, "gross_settlement_mark_change": None if not source_covered else curve[in_year[-1]] / curve[prior[-1]] - 1.0})
    return rows


def _rolling_rows(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    month_ends: dict[tuple[int, int], date] = {}
    for current in dates:
        month_ends[(current.year, current.month)] = current
    positions = {current: index for index, current in enumerate(dates)}
    rows: list[dict[str, Any]] = []
    for end in month_ends.values():
        target = _leap_safe_replace(end, end.year - 5)
        start_candidates = [current for current in dates if current <= target]
        if not start_candidates:
            continue
        start = start_candidates[-1]
        intervals = positions[end] - positions[start]
        response_count = intervals + 1
        calendar_days = (end - start).days
        if response_count < 1200 or calendar_days <= 0:
            continue
        rows.append({
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "retained_observation_intervals": intervals,
            "retained_response_count": response_count,
            "calendar_days": calendar_days,
            "annualized_gross_settlement_mark_change": (curve[end] / curve[start]) ** (365.2425 / calendar_days) - 1.0,
        })
    return rows


def _run() -> dict[str, Any]:
    protocol = _load_protocol()
    product_hashes = _load_product_diligence()
    dates, panel, histories, history_index = _load_panel()
    weekly_dates = _weekly_signal_dates(dates)
    pending: dict[date, dict[str, dict[str, Any]]] = {}
    positions: dict[str, dict[str, Any]] = {}
    signals: list[dict[str, Any]] = []
    daily_rows: list[dict[str, Any]] = []
    curve: dict[date, float] = {}
    unit_value = 1.0
    peak = 1.0
    max_drawdown = 0.0
    effective_events = 0
    active_family_days = 0
    for index, current_date in enumerate(dates):
        gross_change = 0.0
        marked_families: list[str] = []
        if index > 0:
            previous_date = dates[index - 1]
            for family, position in positions.items():
                contract = str(position["contract"])
                previous = panel[previous_date][family].get(contract)
                current = panel[current_date][family].get(contract)
                if previous is None or current is None:
                    raise ValueError(f"missing settlement mark for held actual contract: {family} {contract} {previous_date} {current_date}")
                gross_change += float(position["signed_weight"]) * (float(current["settlement"]) / float(previous["settlement"]) - 1.0)
                marked_families.append(family)
        if gross_change <= -1.0:
            raise ValueError(f"non-positive unit value at {current_date}")
        unit_value *= 1.0 + gross_change
        peak = max(peak, unit_value)
        max_drawdown = min(max_drawdown, unit_value / peak - 1.0)
        if current_date in pending:
            positions = pending.pop(current_date)
            effective_events += 1
        if current_date in weekly_dates and index + 1 < len(dates):
            decisions = [_select_family(protocol, current_date, family, panel, histories, history_index) for family in FAMILIES]
            target: dict[str, dict[str, Any]] = {}
            for decision in decisions:
                if int(decision["direction"]) != 0:
                    target[str(decision["family"])] = {"contract": str(decision["contract"]), "signed_weight": WEIGHT * int(decision["direction"])}
            next_date = dates[index + 1]
            if next_date in pending:
                raise ValueError(f"duplicate effective target: {next_date}")
            pending[next_date] = target
            signals.append({"signal_date": current_date.isoformat(), "effective_date": next_date.isoformat(), "family_decisions": decisions, "active_family_count": len(target)})
        active_family_days += len(positions)
        curve[current_date] = unit_value
        daily_rows.append({"date": current_date.isoformat(), "gross_settlement_mark_change": gross_change, "unit_value": unit_value, "active_family_count_after_effective_target": len(positions), "marked_families_before_effective_target": marked_families})
    if pending:
        raise ValueError("unapplied terminal target")
    annual = _annual_rows(dates, curve)
    rolling = _rolling_rows(dates, curve)
    covered = [row for row in annual if row["source_covered"]]
    annual_failures = [int(row["year"]) for row in covered if float(row["gross_settlement_mark_change"]) < 0.05]
    rolling_passes = sum(float(row["annualized_gross_settlement_mark_change"]) >= 0.05 for row in rolling)
    rolling_failures = len(rolling) - rolling_passes
    calendar_days = (dates[-1] - dates[0]).days
    annualized = unit_value ** (365.2425 / calendar_days) - 1.0
    state = "HURDLE_NOT_MET_IN_GROSS_ACTUAL_CONTRACT_SETTLEMENT_DIAGNOSTIC" if annual_failures or rolling_failures else "NO_NEGATIVE_OBSERVATION_IN_GROSS_NONEXECUTABLE_DIAGNOSTIC"
    return {
        "schema_version": "c17_diversified_actual_contract_settlement_diagnostic.v1",
        "artifact_id": "D5PT-C17-v1",
        "as_of": "2026-08-15",
        "artifact_class": "gross_actual_contract_settlement_mark_diagnostic",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "portfolio_q": 0,
        "protocol_control": {"path": _relative(PROTOCOL_PATH), "sha256": _sha256(PROTOCOL_PATH), "status": protocol["status"]},
        "source_control": {
            "manifest_path": _relative(MANIFEST_PATH),
            "manifest_sha256": _sha256(MANIFEST_PATH),
            "readiness_audit_path": _relative(READINESS_PATH),
            "readiness_audit_sha256": _sha256(READINESS_PATH),
            "product_diligence_sha256": product_hashes,
            "retained_dates": len(dates),
        },
        "signal_summary": {
            "signal_events": len(signals),
            "effective_events": effective_events,
            "active_family_days_after_effective_target": active_family_days,
            "family_signal_counts": {family: sum(1 for record in signals if any(decision["family"] == family and decision["direction"] != 0 for decision in record["family_decisions"])) for family in FAMILIES},
        },
        "full_period_metrics": {"start_date": dates[0].isoformat(), "end_date": dates[-1].isoformat(), "calendar_days": calendar_days, "final_unit_value": unit_value, "annualized_gross_settlement_mark_change": annualized, "maximum_drawdown": max_drawdown},
        "source_covered_calendar_years": annual,
        "rolling_five_calendar_year_endpoints": rolling,
        "five_percent_research_diagnostic": {
            "threshold": 0.05,
            "complete_year_below_5pct": annual_failures,
            "rolling_endpoint_count": len(rolling),
            "rolling_endpoint_at_or_above_5pct": rolling_passes,
            "rolling_endpoint_below_5pct": rolling_failures,
            "state": state,
            "allowed_interpretation": "A gross settlement-mark screen only. It is not total return, executable P&L, a personal result, a stable-return conclusion or a futures action.",
        },
        "daily_unitized_marks": daily_rows,
        "weekly_signal_records": signals,
        "hard_limitations": [
            "Historical source access is retrospective and does not establish point-in-time availability, data rights or absence of revision.",
            "The calendar-15th delivery approximation is not an exchange-adjusted final-trading-day, delivery or status record.",
            "Settlement marks are not bid/ask quotes, fills or attainable executions; no cost, margin, collateral, tax, limit-lock, delivery or broker condition is modeled.",
            "Fractional equal-notional diagnostic sleeves are not contract quantities and cannot be converted into an order size without separate account, margin and risk evidence.",
        ],
        "conclusion": "C17 is deliberately limited to a gross actual-contract settlement-mark diagnostic. Its screen state neither authorizes action nor admits a usable strategy.",
    }


def _markdown(result: dict[str, Any]) -> str:
    metrics = result["full_period_metrics"]
    diagnostic = result["five_percent_research_diagnostic"]
    annual_lines: list[str] = []
    for row in result["source_covered_calendar_years"]:
        value = "n/a" if row["gross_settlement_mark_change"] is None else f"{row['gross_settlement_mark_change']:.2%}"
        annual_lines.append(f"| {row['year']} | {'是' if row['source_covered'] else '否'} | {value} |")
    annual = "\n".join(annual_lines)
    rolling = result["rolling_five_calendar_year_endpoints"]
    rolling_min = min((float(row["annualized_gross_settlement_mark_change"]) for row in rolling), default=None)
    rolling_max = max((float(row["annualized_gross_settlement_mark_change"]) for row in rolling), default=None)
    rolling_range = "n/a" if rolling_min is None else f"{rolling_min:.2%} 至 {rolling_max:.2%}"
    failures = "、".join(str(year) for year in diagnostic["complete_year_below_5pct"]) or "无"
    return f'''# C17 多经济暴露实际合约结算价诊断

- 状态：`{diagnostic['state']}`；`portfolio_q=0`。
- 方法：按冻结方案从 `AU`、`CU`、`RB`、`RU`、`SP` 的**实际挂牌合约**重建每周信号，并以后一份留存响应的结算价标记。没有使用连续主力曲线。
- 严格边界：这是毛额、非成交的结算价诊断；不含费用、买卖价、成交、保证金、抵押收益、限仓、交割、税费或账户条件。

## 诊断结果

| 项目 | 结果 |
|---|---:|
| 覆盖区间 | {metrics['start_date']} 至 {metrics['end_date']} |
| 留存交易所日期 | {result['source_control']['retained_dates']} |
| 周度信号 / 生效事件 | {result['signal_summary']['signal_events']} / {result['signal_summary']['effective_events']} |
| 期末单位化值 | {metrics['final_unit_value']:.4f} |
| 全期年化毛额结算价变化 | {metrics['annualized_gross_settlement_mark_change']:.2%} |
| 最大回撤 | {metrics['maximum_drawdown']:.2%} |
| 源覆盖全年低于 5% | {failures} |
| 滚动五个日历年端点 | {diagnostic['rolling_endpoint_at_or_above_5pct']}/{diagnostic['rolling_endpoint_count']} 达到 5%；范围 {rolling_range} |

| 年份 | 源覆盖全年 | 毛额结算价变化 |
|---|---|---:|
{annual}

## 解释与处置

这是一条与 C16 分开的五类经济暴露假设，不是通过事后改参来修复 C16。严格筛选的状态只回答冻结的实际合约结算价计算中是否出现反例，不能代表个人成交、净结果或未来表现。

无论结果为正或负，C17 都不能直接放行为可使用策略。若出现反例，应保留该失败记录并转向不同、预先冻结的新假设；若未出现反例，也只能补齐实际交易日历、交割状态、动态保证金/限仓/费用、期货公司通道、买卖价与无成交处理，并完成独立复算和前瞻纸面记录。

本文件不授权任何期货、证券或其他外部动作。
'''


def main() -> int:
    result = _run()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"C17 diversified actual-contract settlement diagnostic: {result['five_percent_research_diagnostic']['state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
