#!/usr/bin/env python3
"""Independently reconstruct C17 from frozen SHFE exchange responses.

This auditor deliberately does not import the C17 diagnostic runner.  It reads
each retained compressed response itself, validates its hashes and reported
date, independently re-selects actual contracts and directions, then rebuilds
the entire marked value curve and all published aggregate rows.
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
PROTOCOL_PATH = CASE_DIR / "analysis" / "c17_diversified_actual_contract_settlement_protocol_20260815.json"
P02_PATH = CASE_DIR / "analysis" / "p02_shfe_actual_contract_product_diligence_20260815.json"
P03_PATH = CASE_DIR / "analysis" / "p03_shfe_expanded_actual_contract_product_diligence_20260815.json"
C17_PATH = CASE_DIR / "analysis" / "c17_diversified_actual_contract_settlement_diagnostic_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r05_independent_c17_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r05_independent_c17_audit_20260815.md"
EXPECTED_MANIFEST = "34e23ddf886bd1f1f6cb88610d8d730bd757c981b92b0aa51720c5471b1186d7"
EXPECTED_PROTOCOL = "35f4b5c07bdde384673eba9c9e92943eadd89ee5760cad59ff9b42ec4d63d0d0"
EXPECTED_P02 = "603c6bc79de06b40913f7ad48c18346ecb19dad0c09fe9493de90c9b90357499"
EXPECTED_P03 = "bf7deea405abc9957e2ef857921606d0488285a269dd5127e43dcc1b540dd9c6"
EXPECTED_C17 = "70dfbab252505aed3521ac278948620531ba5c3bb77788344289149925432ed8"
FAMILIES = ("AU", "CU", "RB", "RU", "SP")
WEIGHT = 0.2
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


def _close(left: Any, right: Any) -> bool:
    try:
        return math.isclose(float(left), float(right), abs_tol=TOLERANCE, rel_tol=0.0)
    except (TypeError, ValueError):
        return False


def _positive(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) and parsed > 0.0 else None


def _family(row: dict[str, Any]) -> str:
    return str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()


def _delivery_date(delivery_month: str) -> date:
    if len(delivery_month) != 4 or not delivery_month.isdigit():
        raise ValueError(f"invalid delivery month: {delivery_month!r}")
    return date(2000 + int(delivery_month[:2]), int(delivery_month[2:]), 15)


def _five_year_shift(value: date) -> date:
    try:
        return value.replace(year=value.year - 5)
    except ValueError:
        return value.replace(year=value.year - 5, day=28)


def _add_failure(failures: list[str], message: str) -> None:
    if message not in failures:
        failures.append(message)


def _build_raw_panel(
    failures: list[str],
) -> tuple[
    list[date],
    dict[date, dict[str, dict[str, dict[str, float | str]]]],
    dict[str, list[dict[str, float | str | date]]],
    dict[tuple[date, str], int],
    dict[str, int],
]:
    """Parse raw responses independently of the C17 implementation."""
    manifest = _read(MANIFEST_PATH)
    if _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST:
        _add_failure(failures, "source manifest hash changed")
    records = manifest.get("records")
    if not isinstance(records, list):
        _add_failure(failures, "source manifest records are not a list")
        return [], {}, {}, {}, {"manifest_records": 0, "compressed_hash_checks": 0, "raw_hash_checks": 0, "report_date_checks": 0}

    dates: list[date] = []
    panel: dict[date, dict[str, dict[str, dict[str, float | str]]]] = {}
    histories: dict[str, list[dict[str, float | str | date]]] = defaultdict(list)
    history_index: dict[tuple[date, str], int] = {}
    stats = {"manifest_records": len(records), "compressed_hash_checks": 0, "raw_hash_checks": 0, "report_date_checks": 0}
    seen_dates: set[date] = set()

    for record in sorted(records, key=lambda item: str(item.get("trade_date"))):
        try:
            current_date = date.fromisoformat(str(record["trade_date"]))
        except (KeyError, TypeError, ValueError):
            _add_failure(failures, f"invalid manifest trade date: {record!r}")
            continue
        if current_date in seen_dates:
            _add_failure(failures, f"duplicate manifest trade date: {current_date}")
            continue
        seen_dates.add(current_date)
        try:
            raw_path = REPO_ROOT / str(record["path"])
            raw_path.relative_to(SOURCE_DIR)
        except (KeyError, ValueError):
            _add_failure(failures, f"source path escapes retained source directory: {current_date}")
            continue
        if not raw_path.is_file():
            _add_failure(failures, f"retained source missing: {current_date}")
            continue
        compressed = raw_path.read_bytes()
        stats["compressed_hash_checks"] += 1
        if hashlib.sha256(compressed).hexdigest() != record.get("compressed_sha256"):
            _add_failure(failures, f"compressed source mismatch: {current_date}")
            continue
        try:
            raw = gzip.decompress(compressed)
        except OSError:
            _add_failure(failures, f"cannot decompress retained source: {current_date}")
            continue
        stats["raw_hash_checks"] += 1
        if hashlib.sha256(raw).hexdigest() != record.get("raw_sha256"):
            _add_failure(failures, f"raw source mismatch: {current_date}")
            continue
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            _add_failure(failures, f"raw source is not a valid JSON response: {current_date}")
            continue
        stats["report_date_checks"] += 1
        if str(payload.get("report_date") or "") != current_date.strftime("%Y%m%d"):
            _add_failure(failures, f"reported date differs from manifest date: {current_date}")
            continue
        rows = payload.get("o_curinstrument")
        if not isinstance(rows, list):
            _add_failure(failures, f"actual-contract rows unavailable: {current_date}")
            continue

        by_family: dict[str, dict[str, dict[str, float | str]]] = {family: {} for family in FAMILIES}
        for raw_row in rows:
            if not isinstance(raw_row, dict):
                continue
            family = _family(raw_row)
            delivery_month = str(raw_row.get("DELIVERYMONTH") or "").strip()
            if family not in by_family or delivery_month in {"", "小计", "合计"}:
                continue
            parsed = {
                field: _positive(raw_row.get(field))
                for field in ("SETTLEMENTPRICE", "OPENPRICE", "HIGHESTPRICE", "LOWESTPRICE", "VOLUME", "OPENINTEREST")
            }
            if any(value is None for value in parsed.values()):
                continue
            contract = f"{family}{delivery_month}"
            if contract in by_family[family]:
                _add_failure(failures, f"duplicate actual contract row: {current_date} {contract}")
                continue
            entry: dict[str, float | str] = {
                "contract": contract,
                "family": family,
                "delivery_month": delivery_month,
                "settlement": float(parsed["SETTLEMENTPRICE"]),
                "open": float(parsed["OPENPRICE"]),
                "high": float(parsed["HIGHESTPRICE"]),
                "low": float(parsed["LOWESTPRICE"]),
                "volume": float(parsed["VOLUME"]),
                "open_interest": float(parsed["OPENINTEREST"]),
            }
            history_index[(current_date, contract)] = len(histories[contract])
            histories[contract].append({"date": current_date, **entry})
            by_family[family][contract] = entry
        missing = [family for family in FAMILIES if not by_family[family]]
        if missing:
            _add_failure(failures, f"missing valid actual-contract family cells: {current_date} {','.join(missing)}")
            continue
        dates.append(current_date)
        panel[current_date] = by_family
    return dates, panel, histories, history_index, stats


def _select_actual_contract(
    protocol: dict[str, Any],
    signal_date: date,
    family: str,
    panel: dict[date, dict[str, dict[str, dict[str, float | str]]]],
    histories: dict[str, list[dict[str, float | str | date]]],
    history_index: dict[tuple[date, str], int],
) -> dict[str, Any]:
    """Re-apply the frozen eligibility, signal and rank rules."""
    weekly = protocol["weekly_signal"]
    requirements = weekly["required_history"]
    min_days = int(weekly["eligible_scheduled_days_to_delivery"]["minimum"])
    max_days = int(weekly["eligible_scheduled_days_to_delivery"]["maximum"])
    settle_count = int(requirements["same_actual_contract_valid_settlement_observations_including_signal"])
    ohlc_count = int(requirements["same_actual_contract_valid_ohlc_observations"])
    volume_count = int(requirements["same_actual_contract_volume_median_observations"])
    min_volume = float(requirements["minimum_median_volume"])
    min_interest = float(requirements["minimum_current_open_interest"])
    fast_lookback = int(weekly["fast_signal"]["lookback_valid_observations"])
    rejected: Counter[str] = Counter()
    candidates: list[dict[str, Any]] = []

    for cell in panel[signal_date][family].values():
        contract = str(cell["contract"])
        try:
            scheduled_days = (_delivery_date(str(cell["delivery_month"])) - signal_date).days
        except ValueError:
            rejected["invalid_delivery_month"] += 1
            continue
        if not min_days <= scheduled_days <= max_days:
            rejected["scheduled_delivery_window"] += 1
            continue
        if float(cell["open_interest"]) < min_interest:
            rejected["current_open_interest"] += 1
            continue
        end_index = history_index.get((signal_date, contract))
        if end_index is None:
            rejected["same_contract_settlement_history"] += 1
            continue
        observations = histories[contract][: end_index + 1]
        if len(observations) < settle_count:
            rejected["same_contract_settlement_history"] += 1
            continue
        recent_ohlc = observations[-ohlc_count:]
        if len(recent_ohlc) < ohlc_count or any(float(row["open"]) <= 0.0 or float(row["high"]) <= 0.0 or float(row["low"]) <= 0.0 for row in recent_ohlc):
            rejected["same_contract_ohlc_history"] += 1
            continue
        recent_volume = observations[-volume_count:]
        if len(recent_volume) < volume_count or median(float(row["volume"]) for row in recent_volume) < min_volume:
            rejected["median_volume"] += 1
            continue
        if len(observations) < fast_lookback + 1:
            rejected["same_contract_fast_history"] += 1
            continue
        slow = float(cell["settlement"]) / float(observations[-settle_count]["settlement"]) - 1.0
        fast = float(cell["settlement"]) / float(observations[-(fast_lookback + 1)]["settlement"]) - 1.0
        direction = 0
        if slow >= float(weekly["slow_signal"]["long_at_or_above"]) and fast >= float(weekly["fast_signal"]["long_at_or_above"]):
            direction = 1
        elif slow <= float(weekly["slow_signal"]["short_at_or_below"]) and fast <= float(weekly["fast_signal"]["short_at_or_below"]):
            direction = -1
        candidates.append(
            {
                **cell,
                "scheduled_days_to_delivery": scheduled_days,
                "slow_signal": slow,
                "fast_signal": fast,
                "direction": direction,
            }
        )

    if not candidates:
        return {
            "family": family,
            "contract": None,
            "direction": 0,
            "reason": "no_eligible_actual_contract",
            "rejection_counts": dict(sorted(rejected.items())),
        }
    candidates.sort(key=lambda row: (-float(row["open_interest"]), -float(row["volume"]), str(row["delivery_month"])))
    selected = candidates[0]
    return {
        "family": family,
        "contract": str(selected["contract"]),
        "direction": int(selected["direction"]),
        "reason": "selected_actual_contract",
        "eligible_candidate_count": len(candidates),
        "selection": selected,
    }


def _weekly_signal_dates(dates: list[date]) -> list[date]:
    latest: dict[tuple[int, int], date] = {}
    for current in dates:
        year, week, _ = current.isocalendar()
        latest[(year, week)] = current
    return sorted(latest.values())


def _annual_rows(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for year in sorted({current.year for current in dates}):
        dates_in_year = [current for current in dates if current.year == year]
        preceding = [current for current in dates if current < dates_in_year[0]]
        covered = bool(
            preceding
            and dates_in_year[0] <= date(year, 1, 7)
            and dates_in_year[-1] >= date(year, 12, 24)
            and all(current in curve for current in dates_in_year)
        )
        rows.append(
            {
                "year": year,
                "source_covered": covered,
                "gross_settlement_mark_change": None if not covered else curve[dates_in_year[-1]] / curve[preceding[-1]] - 1.0,
            }
        )
    return rows


def _rolling_rows(dates: list[date], curve: dict[date, float]) -> list[dict[str, Any]]:
    month_ends: dict[tuple[int, int], date] = {}
    for current in dates:
        month_ends[(current.year, current.month)] = current
    date_index = {current: index for index, current in enumerate(dates)}
    rows: list[dict[str, Any]] = []
    for end in month_ends.values():
        target = _five_year_shift(end)
        eligible_starts = [current for current in dates if current <= target]
        if not eligible_starts:
            continue
        start = eligible_starts[-1]
        intervals = date_index[end] - date_index[start]
        response_count = intervals + 1
        calendar_days = (end - start).days
        if response_count < 1200 or calendar_days <= 0:
            continue
        rows.append(
            {
                "start_date": start.isoformat(),
                "end_date": end.isoformat(),
                "retained_observation_intervals": intervals,
                "retained_response_count": response_count,
                "calendar_days": calendar_days,
                "annualized_gross_settlement_mark_change": (curve[end] / curve[start]) ** (365.2425 / calendar_days) - 1.0,
            }
        )
    return rows


def _check_selection(
    failures: list[str],
    signal_date: date,
    family: str,
    expected: dict[str, Any],
    published: Any,
) -> bool:
    """Compare contract identity, rank, direction and all selected mark fields."""
    if not isinstance(published, dict):
        _add_failure(failures, f"missing published family decision: {signal_date} {family}")
        return False
    if published.get("family") != family:
        _add_failure(failures, f"published family label differs: {signal_date} {family}")
    if published.get("contract") != expected.get("contract"):
        _add_failure(failures, f"actual-contract selection differs: {signal_date} {family}")
    if int(published.get("direction", 0)) != int(expected.get("direction", 0)):
        _add_failure(failures, f"direction differs: {signal_date} {family}")
    if published.get("reason") != expected.get("reason"):
        _add_failure(failures, f"selection reason differs: {signal_date} {family}")
    if expected.get("contract") is None:
        if published.get("rejection_counts") != expected.get("rejection_counts"):
            _add_failure(failures, f"eligibility rejection counts differ: {signal_date} {family}")
        return False

    if published.get("eligible_candidate_count") != expected.get("eligible_candidate_count"):
        _add_failure(failures, f"eligible actual-contract count differs: {signal_date} {family}")
    chosen = expected["selection"]
    published_selection = published.get("selection")
    if not isinstance(published_selection, dict):
        _add_failure(failures, f"published selected contract detail missing: {signal_date} {family}")
        return True
    exact_fields = ("contract", "family", "delivery_month", "direction", "scheduled_days_to_delivery")
    for field in exact_fields:
        if published_selection.get(field) != chosen.get(field):
            _add_failure(failures, f"selected contract field differs ({field}): {signal_date} {family}")
    numeric_fields = ("settlement", "open", "high", "low", "volume", "open_interest", "slow_signal", "fast_signal")
    for field in numeric_fields:
        if not _close(published_selection.get(field), chosen.get(field)):
            _add_failure(failures, f"selected contract metric differs ({field}): {signal_date} {family}")
    return True


def _audit() -> dict[str, Any]:
    failures: list[str] = []
    protocol = _read(PROTOCOL_PATH)
    published = _read(C17_PATH)
    if _sha256(PROTOCOL_PATH) != EXPECTED_PROTOCOL:
        _add_failure(failures, "frozen C17 protocol hash changed")
    if _sha256(C17_PATH) != EXPECTED_C17:
        _add_failure(failures, "published C17 diagnostic hash changed")
    if protocol.get("status") != "FROZEN_BEFORE_CALCULATION":
        _add_failure(failures, "C17 protocol is not frozen")
    if protocol.get("artifact_id") != "D5PT-C17-PROTOCOL-v2":
        _add_failure(failures, "C17 protocol source-control amendment version differs")
    if tuple(protocol.get("universe", {}).get("families", [])) != FAMILIES:
        _add_failure(failures, "C17 protocol family universe changed")
    if not _close(protocol.get("unitized_settlement_mark", {}).get("position_weight_per_active_family"), WEIGHT):
        _add_failure(failures, "C17 protocol diagnostic weight changed")
    if protocol.get("research_only") is not True or protocol.get("formal_decision_eligible") is not False or protocol.get("external_orders") is not False:
        _add_failure(failures, "C17 protocol action boundary changed")
    dependency = protocol.get("source_dependency", {})
    if dependency.get("legacy_product_diligence_sha256") != EXPECTED_P02 or dependency.get("expanded_product_diligence_sha256") != EXPECTED_P03:
        _add_failure(failures, "C17 protocol product-diligence controls differ")
    if _sha256(P02_PATH) != EXPECTED_P02 or _sha256(P03_PATH) != EXPECTED_P03:
        _add_failure(failures, "product-diligence artifact hash changed")
    identity_rule = str(protocol.get("universe", {}).get("contract_identity") or "")
    if "actual listed contract" not in identity_rule or "Continuous" not in identity_rule or "forbidden" not in identity_rule:
        _add_failure(failures, "C17 actual-contract / no-continuous-series boundary changed")

    if published.get("artifact_id") != "D5PT-C17-v1" or published.get("artifact_class") != "gross_actual_contract_settlement_mark_diagnostic":
        _add_failure(failures, "published C17 artifact identity changed")
    if published.get("research_only") is not True or published.get("formal_decision_eligible") is not False or published.get("external_orders") is not False or published.get("portfolio_q") != 0:
        _add_failure(failures, "published C17 action boundary changed")
    if published.get("protocol_control", {}).get("sha256") != EXPECTED_PROTOCOL:
        _add_failure(failures, "published C17 protocol control differs")
    if published.get("source_control", {}).get("product_diligence_sha256") != {"P02": EXPECTED_P02, "P03": EXPECTED_P03}:
        _add_failure(failures, "published C17 product-diligence control differs")

    dates, panel, histories, history_index, raw_stats = _build_raw_panel(failures)
    if not dates:
        _add_failure(failures, "no valid retained response dates for independent replay")
    if published.get("source_control", {}).get("manifest_sha256") != EXPECTED_MANIFEST:
        _add_failure(failures, "published C17 source manifest control differs")
    if published.get("source_control", {}).get("retained_dates") != len(dates):
        _add_failure(failures, "published retained-date count differs")

    published_signals_list = published.get("weekly_signal_records")
    if not isinstance(published_signals_list, list):
        _add_failure(failures, "published weekly signal records are unavailable")
        published_signals_list = []
    published_signals: dict[str, dict[str, Any]] = {}
    for row in published_signals_list:
        if not isinstance(row, dict) or not isinstance(row.get("signal_date"), str):
            _add_failure(failures, "malformed published weekly signal record")
            continue
        signal_key = str(row["signal_date"])
        if signal_key in published_signals:
            _add_failure(failures, f"duplicate published weekly signal: {signal_key}")
        published_signals[signal_key] = row

    weekly_dates = _weekly_signal_dates(dates)
    expected_signal_dates = weekly_dates[:-1]
    expected_signal_keys = {current.isoformat() for current in expected_signal_dates}
    if set(published_signals) != expected_signal_keys or len(published_signals_list) != len(expected_signal_dates):
        _add_failure(failures, "published weekly signal-date set differs")

    targets: dict[date, dict[str, tuple[str, float]]] = {}
    selection_checks = 0
    direction_checks = 0
    actual_contract_identity_checks = 0
    for signal_index, signal_date in enumerate(expected_signal_dates):
        row = published_signals.get(signal_date.isoformat())
        if row is None:
            continue
        effective_date = dates[dates.index(signal_date) + 1]
        if row.get("effective_date") != effective_date.isoformat():
            _add_failure(failures, f"effective date differs: {signal_date}")
        decisions = row.get("family_decisions")
        if not isinstance(decisions, list):
            _add_failure(failures, f"family decisions missing: {signal_date}")
            decisions = []
        decision_by_family = {str(decision.get("family")): decision for decision in decisions if isinstance(decision, dict)}
        if len(decisions) != len(FAMILIES) or set(decision_by_family) != set(FAMILIES):
            _add_failure(failures, f"published family-decision set differs: {signal_date}")
        target: dict[str, tuple[str, float]] = {}
        for family in FAMILIES:
            expected = _select_actual_contract(protocol, signal_date, family, panel, histories, history_index)
            selected = _check_selection(failures, signal_date, family, expected, decision_by_family.get(family))
            if selected:
                selection_checks += 1
                contract = str(expected["contract"])
                if not contract.startswith(family) or contract != f"{family}{expected['selection']['delivery_month']}":
                    _add_failure(failures, f"selected contract is not an actual family/delivery identity: {signal_date} {family}")
                actual_contract_identity_checks += 1
            direction = int(expected.get("direction", 0))
            if direction != 0 and expected.get("contract") is not None:
                direction_checks += 1
                target[family] = (str(expected["contract"]), WEIGHT * direction)
        if row.get("active_family_count") != len(target):
            _add_failure(failures, f"published active-family count differs: {signal_date}")
        if effective_date in targets:
            _add_failure(failures, f"duplicate reconstructed effective target: {effective_date}")
        targets[effective_date] = target

    curve: dict[date, float] = {}
    reconstructed_daily: list[dict[str, Any]] = []
    positions: dict[str, tuple[str, float]] = {}
    unit_value = 1.0
    peak = 1.0
    maximum_drawdown = 0.0
    marked_actual_contract_pairs = 0
    active_family_days = 0
    for index, current_date in enumerate(dates):
        gross_change = 0.0
        marked_families: list[str] = []
        if index:
            previous_date = dates[index - 1]
            for family, (contract, signed_weight) in positions.items():
                prior_mark = panel[previous_date][family].get(contract)
                current_mark = panel[current_date][family].get(contract)
                if prior_mark is None or current_mark is None:
                    _add_failure(failures, f"actual held-contract mark missing: {previous_date} {current_date} {family} {contract}")
                    continue
                if contract != f"{family}{prior_mark['delivery_month']}" or contract != f"{family}{current_mark['delivery_month']}":
                    _add_failure(failures, f"held mark is not an actual contract identity: {current_date} {family} {contract}")
                if not _close(abs(signed_weight), WEIGHT):
                    _add_failure(failures, f"held diagnostic weight differs: {current_date} {family}")
                gross_change += signed_weight * (float(current_mark["settlement"]) / float(prior_mark["settlement"]) - 1.0)
                marked_families.append(family)
                marked_actual_contract_pairs += 1
        if gross_change <= -1.0:
            _add_failure(failures, f"non-positive reconstructed unit value: {current_date}")
            break
        unit_value *= 1.0 + gross_change
        peak = max(peak, unit_value)
        maximum_drawdown = min(maximum_drawdown, unit_value / peak - 1.0)
        if current_date in targets:
            positions = targets[current_date]
        active_family_days += len(positions)
        curve[current_date] = unit_value
        reconstructed_daily.append(
            {
                "date": current_date.isoformat(),
                "gross_settlement_mark_change": gross_change,
                "unit_value": unit_value,
                "active_family_count_after_effective_target": len(positions),
                "marked_families_before_effective_target": marked_families,
            }
        )

    published_daily = published.get("daily_unitized_marks")
    daily_mismatches: Counter[str] = Counter()
    if not isinstance(published_daily, list):
        _add_failure(failures, "published daily marked curve is unavailable")
        published_daily = []
    if len(published_daily) != len(reconstructed_daily):
        _add_failure(failures, "published daily marked curve length differs")
    for index, expected_day in enumerate(reconstructed_daily):
        if index >= len(published_daily) or not isinstance(published_daily[index], dict):
            daily_mismatches["missing_or_malformed_day"] += 1
            continue
        actual_day = published_daily[index]
        if actual_day.get("date") != expected_day["date"]:
            daily_mismatches["date"] += 1
        if not _close(actual_day.get("gross_settlement_mark_change"), expected_day["gross_settlement_mark_change"]):
            daily_mismatches["gross_settlement_mark_change"] += 1
        if not _close(actual_day.get("unit_value"), expected_day["unit_value"]):
            daily_mismatches["unit_value"] += 1
        if actual_day.get("active_family_count_after_effective_target") != expected_day["active_family_count_after_effective_target"]:
            daily_mismatches["active_family_count_after_effective_target"] += 1
        if actual_day.get("marked_families_before_effective_target") != expected_day["marked_families_before_effective_target"]:
            daily_mismatches["marked_families_before_effective_target"] += 1
    for field, count in sorted(daily_mismatches.items()):
        _add_failure(failures, f"entire daily curve differs for {count} rows ({field})")

    annual = _annual_rows(dates, curve)
    published_annual = published.get("source_covered_calendar_years")
    if not isinstance(published_annual, list) or len(published_annual) != len(annual):
        _add_failure(failures, "published source-covered calendar-year rows differ")
        published_annual = published_annual if isinstance(published_annual, list) else []
    published_annual_by_year = {int(row["year"]): row for row in published_annual if isinstance(row, dict) and str(row.get("year", "")).isdigit()}
    for row in annual:
        actual = published_annual_by_year.get(int(row["year"]))
        if actual is None or actual.get("source_covered") != row["source_covered"]:
            _add_failure(failures, f"source-covered calendar-year flag differs: {row['year']}")
        elif row["gross_settlement_mark_change"] is None:
            if actual.get("gross_settlement_mark_change") is not None:
                _add_failure(failures, f"uncovered calendar-year value differs: {row['year']}")
        elif not _close(actual.get("gross_settlement_mark_change"), row["gross_settlement_mark_change"]):
            _add_failure(failures, f"calendar-year value differs: {row['year']}")

    rolling = _rolling_rows(dates, curve)
    published_rolling = published.get("rolling_five_calendar_year_endpoints")
    if not isinstance(published_rolling, list) or len(published_rolling) != len(rolling):
        _add_failure(failures, "published rolling endpoint count differs")
        published_rolling = published_rolling if isinstance(published_rolling, list) else []
    published_rolling_by_key = {
        (str(row.get("start_date")), str(row.get("end_date"))): row
        for row in published_rolling
        if isinstance(row, dict)
    }
    for row in rolling:
        key = (row["start_date"], row["end_date"])
        actual = published_rolling_by_key.get(key)
        if actual is None:
            _add_failure(failures, f"rolling endpoint missing: {row['end_date']}")
            continue
        for exact_field in ("retained_observation_intervals", "retained_response_count", "calendar_days"):
            if actual.get(exact_field) != row[exact_field]:
                _add_failure(failures, f"rolling endpoint field differs ({exact_field}): {row['end_date']}")
        if not _close(actual.get("annualized_gross_settlement_mark_change"), row["annualized_gross_settlement_mark_change"]):
            _add_failure(failures, f"rolling endpoint value differs: {row['end_date']}")

    calendar_days = (dates[-1] - dates[0]).days if dates else 0
    annualized = unit_value ** (365.2425 / calendar_days) - 1.0 if calendar_days > 0 else float("nan")
    metrics = published.get("full_period_metrics", {})
    for key, expected_value in {
        "start_date": dates[0].isoformat() if dates else None,
        "end_date": dates[-1].isoformat() if dates else None,
        "calendar_days": calendar_days,
    }.items():
        if metrics.get(key) != expected_value:
            _add_failure(failures, f"full-period metric differs ({key})")
    if not _close(metrics.get("final_unit_value"), unit_value):
        _add_failure(failures, "full-period final unit value differs")
    if not _close(metrics.get("annualized_gross_settlement_mark_change"), annualized):
        _add_failure(failures, "full-period annualized mark change differs")
    if not _close(metrics.get("maximum_drawdown"), maximum_drawdown):
        _add_failure(failures, "full-period maximum drawdown differs")

    annual_failures = [int(row["year"]) for row in annual if row["source_covered"] and float(row["gross_settlement_mark_change"]) < 0.05]
    rolling_passes = sum(float(row["annualized_gross_settlement_mark_change"]) >= 0.05 for row in rolling)
    expected_state = "HURDLE_NOT_MET_IN_GROSS_ACTUAL_CONTRACT_SETTLEMENT_DIAGNOSTIC" if annual_failures or rolling_passes != len(rolling) else "NO_NEGATIVE_OBSERVATION_IN_GROSS_NONEXECUTABLE_DIAGNOSTIC"
    screen = published.get("five_percent_research_diagnostic", {})
    if screen.get("complete_year_below_5pct") != annual_failures:
        _add_failure(failures, "strict screen source-covered-year summary differs")
    if screen.get("rolling_endpoint_count") != len(rolling) or screen.get("rolling_endpoint_at_or_above_5pct") != rolling_passes or screen.get("rolling_endpoint_below_5pct") != len(rolling) - rolling_passes:
        _add_failure(failures, "strict screen rolling summary differs")
    if screen.get("state") != expected_state:
        _add_failure(failures, "strict screen state differs or was promoted")

    summary = published.get("signal_summary", {})
    family_nonflat_counts = {family: 0 for family in FAMILIES}
    for signal_date in expected_signal_dates:
        row = published_signals.get(signal_date.isoformat(), {})
        for decision in row.get("family_decisions", []) if isinstance(row, dict) else []:
            if isinstance(decision, dict) and decision.get("family") in family_nonflat_counts and int(decision.get("direction", 0)) != 0:
                family_nonflat_counts[str(decision["family"])] += 1
    if summary.get("signal_events") != len(expected_signal_dates) or summary.get("effective_events") != len(targets) or summary.get("active_family_days_after_effective_target") != active_family_days or summary.get("family_signal_counts") != family_nonflat_counts:
        _add_failure(failures, "signal summary differs")

    return {
        "schema_version": "independent_c17_actual_contract_audit.v1",
        "artifact_id": "D5PT-R05-v1",
        "as_of": "2026-08-15",
        "result": "PASS" if not failures else "FAIL",
        "failures": failures,
        "source_control": {
            "manifest_path": _relative(MANIFEST_PATH),
            "manifest_sha256": _sha256(MANIFEST_PATH),
            "protocol_path": _relative(PROTOCOL_PATH),
            "protocol_sha256": _sha256(PROTOCOL_PATH),
            "published_c17_path": _relative(C17_PATH),
            "published_c17_sha256": _sha256(C17_PATH),
            "p02_product_diligence_sha256": _sha256(P02_PATH),
            "p03_product_diligence_sha256": _sha256(P03_PATH),
            **raw_stats,
            "raw_dates_reconstructed": len(dates),
        },
        "independent_reconstruction": {
            "weekly_signals": len(expected_signal_dates),
            "selected_actual_contract_direction_checks": selection_checks,
            "nonflat_direction_checks": direction_checks,
            "selected_actual_contract_identity_checks": actual_contract_identity_checks,
            "held_actual_contract_mark_pairs": marked_actual_contract_pairs,
            "entire_daily_curve_rows_compared": len(reconstructed_daily),
            "daily_curve_mismatch_counts": dict(sorted(daily_mismatches.items())),
            "final_unit_value": unit_value,
            "annualized_gross_settlement_mark_change": annualized,
            "maximum_drawdown": maximum_drawdown,
            "complete_year_below_5pct": annual_failures,
            "rolling_endpoint_count": len(rolling),
            "rolling_endpoint_at_or_above_5pct": rolling_passes,
        },
        "boundary": "The audit validates a bounded gross actual-contract settlement-mark calculation only. It does not establish fills, costs, margin, account access, investor net result, usable-strategy status or external action.",
    }


def _markdown(result: dict[str, Any]) -> str:
    reconstruction = result["independent_reconstruction"]
    source = result["source_control"]
    failures = "无。" if not result["failures"] else "\n".join(f"- {item}" for item in result["failures"])
    below = "、".join(str(year) for year in reconstruction["complete_year_below_5pct"]) or "无"
    return f"""# R05 独立审计：C17 多经济暴露实际合约结算价诊断

- 审计结果：`{result['result']}`
- 方法：不导入 C17 运行程序，直接解压、逐份核验留存交易所响应，并独立重选实际合约、重建每个留存日期的结算价记账。

| 项目 | 独立结果 |
|---|---:|
| 留存交易所响应 / 压缩哈希 / 原始哈希 / 报告日期核验 | {source['raw_dates_reconstructed']} / {source['compressed_hash_checks']} / {source['raw_hash_checks']} / {source['report_date_checks']} |
| 周度信号 | {reconstruction['weekly_signals']} |
| 已复核的实际合约选择及方向 | {reconstruction['selected_actual_contract_direction_checks']} |
| 非平向方向检查 | {reconstruction['nonflat_direction_checks']} |
| 实际合约持有标记对 | {reconstruction['held_actual_contract_mark_pairs']} |
| 全部每日曲线比较行数 | {reconstruction['entire_daily_curve_rows_compared']} |
| 期末单位化值 | {reconstruction['final_unit_value']:.4f} |
| 全期年化毛额结算价变化 | {reconstruction['annualized_gross_settlement_mark_change']:.2%} |
| 最大回撤 | {reconstruction['maximum_drawdown']:.2%} |
| 源覆盖全年低于 5% | {below} |
| 滚动五个日历年端点达到 5% | {reconstruction['rolling_endpoint_at_or_above_5pct']}/{reconstruction['rolling_endpoint_count']} |

## 未通过项

{failures}

审计通过只说明冻结协议、保留的实际合约结算价与已发布 C17 算术相互一致。它不增加成交、费用、保证金、账户、个人净结果或可使用策略的证据，也不授权任何外部动作。
"""


def main() -> int:
    result = _audit()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"R05 independent C17 audit: {result['result']}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
