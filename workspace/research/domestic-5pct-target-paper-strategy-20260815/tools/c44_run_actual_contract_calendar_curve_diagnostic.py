#!/usr/bin/env python3
"""Run the frozen C43 actual-contract calendar-curve diagnostic.

The tool is intentionally a gross settlement-mark calculation.  It accepts
only hash-verified SHFE actual-contract records and refuses to invent
execution, funding, margin, or account facts.
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
PROTOCOL_PATH = CASE_DIR / "analysis" / "c43_actual_contract_calendar_curve_protocol_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c44_actual_contract_calendar_curve_diagnostic_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c44_actual_contract_calendar_curve_diagnostic_20260815.md"

EXPECTED_MANIFEST_SHA256 = "34e23ddf886bd1f1f6cb88610d8d730bd757c981b92b0aa51720c5471b1186d7"
EXPECTED_READINESS_SHA256 = "5413d17d4db0654432d1e25e462dd51fd9c2a4591e94ee573f5cf4da70885470"
EXPECTED_P02_SHA256 = "603c6bc79de06b40913f7ad48c18346ecb19dad0c09fe9493de90c9b90357499"
EXPECTED_P03_SHA256 = "bf7deea405abc9957e2ef857921606d0488285a269dd5127e43dcc1b540dd9c6"
EXPECTED_PROTOCOL_SHA256 = "0e44296ac4c2c78ca6697e03a148d19f0643b2825a65a20b0087399096174efe"
FAMILIES = ("AU", "CU", "RB", "RU", "SP")


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
        raise ValueError("C43 frozen protocol hash changed")
    protocol = _read(PROTOCOL_PATH)
    if protocol.get("status") != "FROZEN_BEFORE_CALCULATION":
        raise ValueError("C43 protocol is not frozen")
    if protocol.get("research_only") is not True or protocol.get("formal_decision_eligible") is not False or protocol.get("external_orders") is not False:
        raise ValueError("C43 research boundary changed")
    if tuple(protocol.get("universe", {}).get("families", [])) != FAMILIES:
        raise ValueError("C43 universe changed")
    dependency = protocol.get("source_dependency", {})
    expected_dependencies = {
        "actual_contract_manifest_sha256": EXPECTED_MANIFEST_SHA256,
        "source_readiness_audit_sha256": EXPECTED_READINESS_SHA256,
        "legacy_product_diligence_sha256": EXPECTED_P02_SHA256,
        "expanded_product_diligence_sha256": EXPECTED_P03_SHA256,
    }
    if {key: dependency.get(key) for key in expected_dependencies} != expected_dependencies:
        raise ValueError("C43 source dependency changed")
    return protocol


def _load_panel() -> tuple[list[date], dict[date, dict[str, dict[str, dict[str, Any]]]], dict[str, list[dict[str, Any]]], dict[tuple[date, str], int]]:
    if _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST_SHA256:
        raise ValueError("C15 manifest hash changed")
    readiness = _read(READINESS_PATH)
    if _sha256(READINESS_PATH) != EXPECTED_READINESS_SHA256 or readiness.get("result") != "PASS":
        raise ValueError("C15 source readiness audit is not the frozen passing record")
    if _sha256(P02_PATH) != EXPECTED_P02_SHA256 or _sha256(P03_PATH) != EXPECTED_P03_SHA256:
        raise ValueError("C43 product-diligence artifact hash changed")

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
            volume = _positive(raw_row.get("VOLUME"))
            open_interest = _positive(raw_row.get("OPENINTEREST"))
            if None in {settlement, volume, open_interest}:
                continue
            contract = f"{family}{delivery}"
            if contract in per_family[family]:
                raise ValueError(f"duplicate actual contract: {current_date} {contract}")
            fields = {
                "contract": contract,
                "family": family,
                "delivery_month": delivery,
                "settlement": float(settlement),
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


def _eligible_leg(
    *,
    current: dict[str, Any],
    signal_date: date,
    history: list[dict[str, Any]],
    minimum_days: int,
    maximum_days: int,
    history_required: int,
    minimum_median_volume: float,
    minimum_open_interest: float,
) -> tuple[dict[str, Any] | None, str | None]:
    scheduled_days = (_delivery_date(str(current["delivery_month"])) - signal_date).days
    if not minimum_days <= scheduled_days <= maximum_days:
        return None, "scheduled_delivery_window"
    if float(current["open_interest"]) < minimum_open_interest:
        return None, "current_open_interest"
    if len(history) < history_required:
        return None, "same_actual_contract_history"
    recent = history[-history_required:]
    if any(float(item["settlement"]) <= 0.0 or float(item["volume"]) <= 0.0 for item in recent):
        return None, "same_actual_contract_fields"
    if median(float(item["volume"]) for item in recent) < minimum_median_volume:
        return None, "median_volume"
    return {
        **current,
        "scheduled_days_to_delivery": scheduled_days,
        "median_volume": float(median(float(item["volume"]) for item in recent)),
    }, None


def _select_pair(
    protocol: dict[str, Any],
    signal_date: date,
    family: str,
    panel: dict[date, dict[str, dict[str, dict[str, Any]]]],
    histories: dict[str, list[dict[str, Any]]],
    history_index: dict[tuple[date, str], int],
) -> dict[str, Any]:
    settings = protocol["monthly_pair_signal"]
    requirements = settings["required_same_actual_contract_history"]
    history_required = int(requirements["valid_settlement_and_volume_observations_including_signal"])
    minimum_median_volume = float(requirements["minimum_median_volume"])
    minimum_open_interest = float(requirements["minimum_current_open_interest"])
    near_settings = settings["near_leg"]["scheduled_days_to_delivery"]
    far_settings = settings["deferred_leg"]["scheduled_days_to_delivery"]
    near: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    reasons: Counter[str] = Counter()
    for contract, current in panel[signal_date][family].items():
        history = histories[contract][: history_index[(signal_date, contract)] + 1]
        candidate, issue = _eligible_leg(
            current=current,
            signal_date=signal_date,
            history=history,
            minimum_days=int(near_settings["minimum"]),
            maximum_days=int(near_settings["maximum"]),
            history_required=history_required,
            minimum_median_volume=minimum_median_volume,
            minimum_open_interest=minimum_open_interest,
        )
        if candidate is not None:
            near.append(candidate)
        elif issue is not None:
            reasons[f"near:{issue}"] += 1
        candidate, issue = _eligible_leg(
            current=current,
            signal_date=signal_date,
            history=history,
            minimum_days=int(far_settings["minimum"]),
            maximum_days=int(far_settings["maximum"]),
            history_required=history_required,
            minimum_median_volume=minimum_median_volume,
            minimum_open_interest=minimum_open_interest,
        )
        if candidate is not None:
            deferred.append(candidate)
        elif issue is not None:
            reasons[f"deferred:{issue}"] += 1
    pairs = [(near_leg, deferred_leg) for near_leg in near for deferred_leg in deferred if near_leg["delivery_month"] < deferred_leg["delivery_month"]]
    if not pairs:
        return {
            "family": family,
            "status": "no_eligible_pair",
            "near_candidate_count": len(near),
            "deferred_candidate_count": len(deferred),
            "rejection_counts": dict(sorted(reasons.items())),
        }
    pairs.sort(
        key=lambda item: (
            -min(float(item[0]["open_interest"]), float(item[1]["open_interest"])),
            -min(float(item[0]["median_volume"]), float(item[1]["median_volume"])),
            str(item[0]["delivery_month"]),
            str(item[1]["delivery_month"]),
        )
    )
    near_leg, deferred_leg = pairs[0]
    if float(near_leg["settlement"]) > float(deferred_leg["settlement"]):
        direction = 1
        direction_label = "long_near_short_deferred"
    elif float(near_leg["settlement"]) < float(deferred_leg["settlement"]):
        direction = -1
        direction_label = "short_near_long_deferred"
    else:
        direction = 0
        direction_label = "flat_equal_settlement"
    return {
        "family": family,
        "status": "selected_actual_pair",
        "near_candidate_count": len(near),
        "deferred_candidate_count": len(deferred),
        "pair_candidate_count": len(pairs),
        "near": near_leg,
        "deferred": deferred_leg,
        "direction": direction,
        "direction_label": direction_label,
    }


def _monthly_signal_dates(dates: list[date]) -> list[date]:
    latest: dict[tuple[int, int], date] = {}
    for current_date in dates:
        latest[(current_date.year, current_date.month)] = current_date
    return sorted(latest.values())


def _annual_rows(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in sorted({value.year for value in dates}):
        in_year = [value for value in dates if value.year == year]
        prior = [value for value in dates if value < in_year[0]]
        source_covered = bool(
            prior
            and in_year[0] <= date(year, 1, 7)
            and in_year[-1] >= date(year, 12, 24)
            and prior[-1] in curve
            and all(value in curve for value in in_year)
        )
        value = curve[in_year[-1]] / curve[prior[-1]] - 1.0 if source_covered else None
        rows.append({"year": year, "source_covered": source_covered, "gross_settlement_mark_change": value})
    return rows


def _rolling_rows(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    month_ends: dict[tuple[int, int], date] = {}
    for current_date in dates:
        month_ends[(current_date.year, current_date.month)] = current_date
    date_position = {value: index for index, value in enumerate(dates)}
    rows: list[dict[str, Any]] = []
    for end_date in month_ends.values():
        if end_date not in curve:
            continue
        target = _leap_safe_replace(end_date, end_date.year - 5)
        starts = [value for value in dates if value <= target and value in curve]
        if not starts:
            continue
        start_date = starts[-1]
        retained_intervals = date_position[end_date] - date_position[start_date]
        response_count = retained_intervals + 1
        calendar_days = (end_date - start_date).days
        if response_count < 1200 or calendar_days <= 0:
            continue
        annualized = (curve[end_date] / curve[start_date]) ** (365.2425 / calendar_days) - 1.0
        rows.append(
            {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "retained_observation_intervals": retained_intervals,
                "retained_response_count": response_count,
                "calendar_days": calendar_days,
                "annualized_gross_settlement_mark_change": annualized,
            }
        )
    return rows


def _serialize_target(selection: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": selection["family"],
        "near_contract": selection["near"]["contract"],
        "deferred_contract": selection["deferred"]["contract"],
        "direction": selection["direction"],
        "direction_label": selection["direction_label"],
        "near_settlement": selection["near"]["settlement"],
        "deferred_settlement": selection["deferred"]["settlement"],
        "near_scheduled_days_to_delivery": selection["near"]["scheduled_days_to_delivery"],
        "deferred_scheduled_days_to_delivery": selection["deferred"]["scheduled_days_to_delivery"],
        "near_median_volume": selection["near"]["median_volume"],
        "deferred_median_volume": selection["deferred"]["median_volume"],
        "near_open_interest": selection["near"]["open_interest"],
        "deferred_open_interest": selection["deferred"]["open_interest"],
    }


def _run() -> dict[str, Any]:
    protocol = _load_protocol()
    dates, panel, histories, history_index = _load_panel()
    index_by_date = {current_date: index for index, current_date in enumerate(dates)}
    signal_dates = _monthly_signal_dates(dates)
    signal_records: list[dict[str, Any]] = []
    start_signal: date | None = None
    pending: dict[date, dict[str, dict[str, Any]]] = {}
    incompleteness: dict[str, Any] | None = None

    for signal_date in signal_dates:
        selections = {family: _select_pair(protocol, signal_date, family, panel, histories, history_index) for family in FAMILIES}
        complete = all(selection.get("status") == "selected_actual_pair" for selection in selections.values())
        record = {
            "signal_date": signal_date.isoformat(),
            "all_families_complete": complete,
            "families": selections,
        }
        signal_records.append(record)
        if start_signal is None:
            if complete:
                start_signal = signal_date
            else:
                continue
        if signal_date == dates[-1]:
            continue
        if not complete:
            incompleteness = record
            break
        effective_date = dates[index_by_date[signal_date] + 1]
        pending[effective_date] = {family: _serialize_target(selection) for family, selection in selections.items()}

    common = {
        "schema_version": "c44_actual_contract_calendar_curve_diagnostic.v1",
        "artifact_id": "D5PT-C44-v1",
        "as_of": "2026-08-15",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "protocol": {"path": _relative(PROTOCOL_PATH), "sha256": EXPECTED_PROTOCOL_SHA256},
        "source_dependency": {
            "actual_contract_manifest_path": _relative(MANIFEST_PATH),
            "actual_contract_manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "source_readiness_audit_path": _relative(READINESS_PATH),
            "source_readiness_audit_sha256": EXPECTED_READINESS_SHA256,
            "P02_sha256": EXPECTED_P02_SHA256,
            "P03_sha256": EXPECTED_P03_SHA256,
        },
        "source_interval": {"first_retained_response": dates[0].isoformat(), "last_retained_response": dates[-1].isoformat(), "retained_response_count": len(dates)},
        "signal_records": signal_records,
        "limitations": [
            "Historical exchange responses were retrieved retrospectively and do not prove original-date availability, immutability, revision history, or data rights.",
            "The calculation uses actual-contract settlement marks only. It does not include bid/ask, depth, fills, fees, margin, collateral, taxes, limits, delivery, offset eligibility, account access, or investor returns.",
            "The scheduled delivery boundary is a calendar approximation, not a dated exchange final-trading-day, delivery-state, position-limit, or broker-close-out record.",
            "This diagnostic never creates an external action or admits a usable strategy, regardless of its arithmetic result.",
        ],
    }
    if start_signal is None:
        return {
            **common,
            "status": "NOT_DECIDABLE_NO_COMMON_WARMUP_PAIR",
            "portfolio_q": 0,
            "action": "NO_ACTION",
            "reason": "No monthly signal supplied a valid actual-contract pair for every frozen family after the required history warmup.",
        }
    if incompleteness is not None:
        return {
            **common,
            "status": "NOT_DECIDABLE_INCOMPLETE_MONTHLY_PAIR",
            "portfolio_q": 0,
            "action": "NO_ACTION",
            "warmup_complete_signal_date": start_signal.isoformat(),
            "incomplete_signal": incompleteness,
            "reason": "A frozen family lacked a valid actual-contract pair at a later monthly signal. The protocol requires a stop rather than a substitute, threshold change, or inferred fill.",
        }

    positions: dict[str, dict[str, Any]] = {}
    unit_value = 1.0
    maximum_value = 1.0
    maximum_drawdown = 0.0
    curve: dict[date, float] = {}
    daily_rows: list[dict[str, Any]] = []
    first_effective: date | None = None
    for index, current_date in enumerate(dates):
        gross_change = 0.0
        marked_families: list[str] = []
        if positions:
            if index == 0:
                raise ValueError("cannot mark a position on the first source response")
            previous_date = dates[index - 1]
            for family, target in positions.items():
                near_contract = str(target["near_contract"])
                far_contract = str(target["deferred_contract"])
                prior_near = panel[previous_date][family].get(near_contract)
                current_near = panel[current_date][family].get(near_contract)
                prior_far = panel[previous_date][family].get(far_contract)
                current_far = panel[current_date][family].get(far_contract)
                if None in {prior_near, current_near, prior_far, current_far}:
                    raise ValueError(f"missing held actual-contract settlement mark: {family} {near_contract}/{far_contract} {previous_date} {current_date}")
                direction = int(target["direction"])
                leg_weight = float(protocol["unitized_gross_settlement_mark"]["leg_weight"])
                near_change = float(current_near["settlement"]) / float(prior_near["settlement"]) - 1.0
                far_change = float(current_far["settlement"]) / float(prior_far["settlement"]) - 1.0
                gross_change += direction * leg_weight * (near_change - far_change)
                marked_families.append(family)
        if gross_change <= -1.0:
            raise ValueError(f"non-positive unit value at {current_date}")
        unit_value *= 1.0 + gross_change
        maximum_value = max(maximum_value, unit_value)
        maximum_drawdown = min(maximum_drawdown, unit_value / maximum_value - 1.0)
        if current_date in pending:
            positions = pending[current_date]
            if first_effective is None:
                first_effective = current_date
        if first_effective is not None:
            curve[current_date] = unit_value
            daily_rows.append(
                {
                    "date": current_date.isoformat(),
                    "gross_settlement_mark_change": gross_change,
                    "unit_value": unit_value,
                    "marked_family_count": len(marked_families),
                    "installed_new_target": current_date in pending,
                }
            )
    if first_effective is None:
        return {
            **common,
            "status": "NOT_DECIDABLE_NO_EFFECTIVE_PAIR",
            "portfolio_q": 0,
            "action": "NO_ACTION",
            "warmup_complete_signal_date": start_signal.isoformat(),
            "reason": "The source interval ended before the first valid next-session target could become effective.",
        }
    annual = _annual_rows(dates, curve)
    rolling = _rolling_rows(dates, curve)
    covered_annual = [row for row in annual if row["source_covered"]]
    annual_failures = [row for row in covered_annual if float(row["gross_settlement_mark_change"]) < 0.05]
    rolling_failures = [row for row in rolling if float(row["annualized_gross_settlement_mark_change"]) < 0.05]
    status = "HURDLE_NOT_MET_IN_GROSS_ACTUAL_CONTRACT_SETTLEMENT_DIAGNOSTIC" if annual_failures or rolling_failures else "NO_GROSS_SCREEN_COUNTEREXAMPLE_NOT_ADMITTED"
    return {
        **common,
        "status": status,
        "portfolio_q": 0,
        "action": "NO_ACTION",
        "warmup_complete_signal_date": start_signal.isoformat(),
        "first_effective_target_date": first_effective.isoformat(),
        "final_unit_value": unit_value,
        "full_interval_annualized_gross_settlement_mark_change": (unit_value ** (365.2425 / (dates[-1] - first_effective).days) - 1.0),
        "maximum_drawdown": maximum_drawdown,
        "annual_rows": annual,
        "rolling_five_year_rows": rolling,
        "strict_research_screen": {
            "threshold": 0.05,
            "covered_calendar_year_count": len(covered_annual),
            "annual_failure_years": [row["year"] for row in annual_failures],
            "rolling_endpoint_count": len(rolling),
            "rolling_failure_count": len(rolling_failures),
            "rolling_failure_range": (
                {
                    "minimum": min(float(row["annualized_gross_settlement_mark_change"]) for row in rolling_failures),
                    "maximum": max(float(row["annualized_gross_settlement_mark_change"]) for row in rolling_failures),
                }
                if rolling_failures
                else None
            ),
        },
        "daily_rows": daily_rows,
    }


def _format_percent(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100.0:.2f}%"


def _render_markdown(result: dict[str, Any]) -> str:
    status = str(result["status"])
    lines = ["# C44 实际合约期限结构诊断", "", f"- 状态：`{status}`；`portfolio_q=0`；当前动作：`NO_ACTION`。"]
    if status.startswith("NOT_DECIDABLE"):
        lines.extend([f"- 原因：{result['reason']}", "", "该结果不允许替换品种、放松门槛、填补数据或假定成交。它不产生外部操作。"])
        return "\n".join(lines) + "\n"
    lines.extend(
        [
            "- 方法：依据 C43 冻结规则，按月选择同品种近期/远期实际挂牌合约，并在下一留存响应后以相邻结算价标记等名义多空配对；没有使用连续、主力、合成或拼接序列。",
            "- 严格边界：这是毛额、非成交的结算价诊断；不含费用、买卖价、成交、保证金、抵押收益、限仓、交割、税费或账户条件。",
            "",
            "## 诊断结果",
            "",
            "| 项目 | 结果 |",
            "|---|---:|",
            f"| 覆盖区间 | {result['first_effective_target_date']} 至 {result['source_interval']['last_retained_response']} |",
            f"| 留存交易所日期 | {result['source_interval']['retained_response_count']} |",
            f"| 期末单位化值 | {result['final_unit_value']:.4f} |",
            f"| 全区间年化毛额结算价变化 | {_format_percent(result['full_interval_annualized_gross_settlement_mark_change'])} |",
            f"| 最大回撤 | {_format_percent(result['maximum_drawdown'])} |",
            f"| 源覆盖全年低于 5% | {'、'.join(str(year) for year in result['strict_research_screen']['annual_failure_years']) or '无'} |",
            f"| 滚动五年端点 | {result['strict_research_screen']['rolling_failure_count']}/{result['strict_research_screen']['rolling_endpoint_count']} 低于 5% |",
            "",
            "| 年份 | 源覆盖全年 | 毛额结算价变化 |",
            "|---|---|---:|",
        ]
    )
    for row in result["annual_rows"]:
        lines.append(f"| {row['year']} | {'是' if row['source_covered'] else '否'} | {_format_percent(row['gross_settlement_mark_change'])} |")
    lines.extend(
        [
            "",
            "## 解释与处置",
            "",
            "本诊断只检验冻结的同品种期限结构假设是否在实际合约结算价的有限计算中出现严格筛选反例。它不回答个人实际成交、净结果或未来表现。",
            "",
            "无论该毛额诊断结果为正或负，均不得转换为可使用策略、稳定 5%、净结果或操作指令。若严格筛选出现反例，必须保留失败记录，不得调参、替换品种或以其他路线抵消；若未出现反例，仍须以有权使用、逐时点的合约、交易日、动态保证金/限仓/费用、买卖价、成交和交割数据完成独立复算与前瞻纸面记录。",
            "",
            "本文件不授权任何期货、证券或其他外部动作。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    result = _run()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    _write(OUTPUT_MD, _render_markdown(result))
    print(f"{result['status']}: {_relative(OUTPUT_JSON)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
