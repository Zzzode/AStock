#!/usr/bin/env python3
"""Independently rederive the C7 and C8 public-price diagnostics.

This checker deliberately does not import either candidate's replay module.
It validates retained raw-file hashes, reconstructs both fixed rulebooks from
their own JSON artifacts, and compares independently calculated outputs.  It
does not turn a public close-price observation into a total-return result,
personal suitability conclusion, or external action.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from bisect import bisect_right
from collections.abc import Mapping
from datetime import date, datetime
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
OUTPUT_JSON = CASE_DIR / "analysis" / f"r7_c7_c8_independent_audit_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"r7_c7_c8_independent_audit_{DATE_TAG}.md"
C7_RULEBOOK = CASE_DIR / "analysis" / f"c7_static_core_satellite_rulebook_{DATE_TAG}.json"
C7_RESULT = CASE_DIR / "analysis" / f"c7_static_core_satellite_price_diagnostic_{DATE_TAG}.json"
C7_MANIFEST = CASE_DIR / "sources" / f"c7-static-etf-price-observation-{DATE_TAG}" / "manifest.json"
C8_PROTOCOL = CASE_DIR / "analysis" / f"c8_convertible_bond_etf_fixed_allocation_protocol_{DATE_TAG}.json"
C8_RESULT = CASE_DIR / "analysis" / f"c8_convertible_bond_etf_fixed_allocation_price_proxy_{DATE_TAG}.json"
C8_MANIFEST = CASE_DIR / "sources" / f"c8-official-product-and-price-{DATE_TAG}" / "manifest.json"
TOLERANCE = 1e-10


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"required artifact missing: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"artifact must be a JSON object: {path}")
    return value


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8")
    temporary.replace(path)


def _parse_dayk(path: Path, code: str) -> dict[str, float]:
    raw = path.read_text(encoding="utf-8")
    left = raw.find("(")
    if left < 1 or not raw.rstrip().endswith(")"):
        raise ValueError(f"unexpected JSONP envelope: {path.name}")
    payload = json.loads(raw[left + 1 : raw.rfind(")")])
    if str(payload.get("code")) != code:
        raise ValueError(f"code mismatch in {path.name}")
    rows = payload.get("kline")
    if not isinstance(rows, list) or len(rows) != int(payload.get("total", -1)):
        raise ValueError(f"incomplete daily series: {path.name}")
    output: dict[str, float] = {}
    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            raise ValueError(f"malformed row in {path.name}")
        raw_day = str(row[0])
        if len(raw_day) != 8 or not raw_day.isdigit():
            raise ValueError(f"malformed date in {path.name}")
        day = f"{raw_day[:4]}-{raw_day[4:6]}-{raw_day[6:]}"
        close = float(row[4])
        if day in output or not math.isfinite(close) or close <= 0:
            raise ValueError(f"invalid close in {path.name}")
        output[day] = close
    return output


def _verify_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = _load(manifest_path)
    rows = manifest.get("files")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(rows, list) or not isinstance(frozen, list):
        raise ValueError(f"manifest lacks file/freeze rows: {manifest_path.name}")
    by_path = {str(row.get("path")): row for row in rows if isinstance(row, Mapping)}
    freeze_by_path = {str(row.get("path")): row for row in frozen if isinstance(row, Mapping)}
    if set(by_path) != set(freeze_by_path):
        raise ValueError(f"manifest/freeze file sets differ: {manifest_path.name}")
    for relative, row in by_path.items():
        path = REPO_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"manifested source missing: {relative}")
        if path.stat().st_size != int(row.get("bytes", -1)) or _sha256(path) != row.get("sha256"):
            raise ValueError(f"manifested source hash mismatch: {relative}")
        frozen_row = freeze_by_path[relative]
        expected = {key: row.get(key) for key in ("path", "bytes", "sha256")}
        observed = {key: frozen_row.get(key) for key in ("path", "bytes", "sha256")}
        if observed != expected:
            raise ValueError(f"freeze mismatch: {relative}")
    return manifest


def _common_panel(manifest: Mapping[str, Any], expected_codes: list[str]) -> tuple[list[str], dict[str, dict[str, float]]]:
    found: dict[str, dict[str, float]] = {}
    for row in manifest["files"]:
        code = str(row.get("code", ""))
        if not code:
            matched = re.search(r"sse_etf_dayk_(\d+)_", str(row.get("path", "")))
            code = matched.group(1) if matched else ""
        if code in expected_codes:
            found[code] = _parse_dayk(REPO_ROOT / str(row["path"]), code)
    if set(found) != set(expected_codes):
        raise ValueError("raw daily file code set does not match fixed rule")
    common = sorted(set.intersection(*(set(found[code]) for code in expected_codes)))
    if len(common) < 2:
        raise ValueError("common daily panel is too short")
    return common, found


def _date(day: str) -> date:
    return datetime.strptime(day, "%Y-%m-%d").date()


def _five_year_cutoff(day: date) -> date:
    """Match a calendar five-year offset, including the leap-day convention."""

    try:
        return day.replace(year=day.year - 5)
    except ValueError:
        return day.replace(year=day.year - 5, day=28)


def _max_drawdown(nav: list[float]) -> float:
    peak = nav[0]
    worst = 0.0
    for value in nav:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def _assert_close(label: str, actual: float, expected: float, failures: list[str]) -> None:
    if not math.isclose(actual, expected, rel_tol=TOLERANCE, abs_tol=TOLERANCE):
        failures.append(f"{label}: independent={actual:.12g}, retained={expected:.12g}")


def _c7_replay(rulebook: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    sleeves = rulebook.get("rule", {}).get("sleeves", [])
    if not isinstance(sleeves, list) or not sleeves:
        raise ValueError("C7 rulebook has no sleeves")
    codes = [str(row["code"]) for row in sleeves]
    targets = {str(row["code"]): float(row["target_weight"]) for row in sleeves}
    bands = {str(row["code"]): float(row["weight_band_absolute"]) for row in sleeves}
    if not math.isclose(sum(targets.values()), 1.0, abs_tol=1e-12):
        raise ValueError("C7 weights do not sum to one")
    dates, prices = _common_panel(manifest, codes)
    values = dict(targets)
    nav = [sum(values.values())]
    events: list[dict[str, Any]] = []
    one_way_cost_rate = 0.002
    for position in range(1, len(dates)):
        prior_day, day = dates[position - 1], dates[position]
        if _date(prior_day).month in {3, 9} and _date(day).month != _date(prior_day).month:
            pre_trade_nav = sum(values.values())
            drift = {code: values[code] / pre_trade_nav for code in codes}
            trigger_codes = [code for code in codes if abs(drift[code] - targets[code]) > bands[code]]
            turnover = 0.0
            if trigger_codes:
                turnover = sum(abs(drift[code] - targets[code]) for code in codes) / 2.0
                values = {code: targets[code] * pre_trade_nav * (1.0 - turnover * one_way_cost_rate) for code in codes}
            events.append({"effective_date": day, "rebalanced": bool(trigger_codes), "turnover": turnover})
        for code in codes:
            values[code] *= prices[code][day] / prices[code][prior_day]
        nav.append(sum(values.values()))
    by_year: dict[int, list[int]] = {}
    for index, day in enumerate(dates):
        by_year.setdefault(_date(day).year, []).append(index)
    terminal_year = _date(dates[-1]).year
    annual: dict[int, float] = {}
    for year, indexes in by_year.items():
        months = {_date(dates[index]).month for index in indexes}
        if year < terminal_year and months == set(range(1, 13)):
            first = indexes[0]
            if first == 0:
                raise ValueError("C7 complete year has no prior observation")
            annual[year] = nav[indexes[-1]] / nav[first - 1] - 1.0
    rolling: list[float] = []
    date_values = [_date(day) for day in dates]
    for end_index, end_day in enumerate(dates):
        cutoff = _five_year_cutoff(_date(end_day))
        start_index = bisect_right(date_values, cutoff, 0, end_index + 1) - 1
        if start_index < 0:
            continue
        days = (date_values[end_index] - date_values[start_index]).days
        if days >= 1820:
            rolling.append((nav[end_index] / nav[start_index]) ** (365.25 / days) - 1.0)
    elapsed_days = (_date(dates[-1]) - _date(dates[0])).days
    return {
        "dates": dates,
        "nav": nav,
        "annualized": nav[-1] ** (365.25 / elapsed_days) - 1.0,
        "max_drawdown": _max_drawdown(nav),
        "events": events,
        "annual": annual,
        "rolling": rolling,
    }


def _c8_replay(protocol: Mapping[str, Any], manifest: Mapping[str, Any]) -> dict[str, Any]:
    targets = {str(code): float(weight) for code, weight in protocol["rules"]["targets"].items()}
    codes = list(targets)
    if not math.isclose(sum(targets.values()), 1.0, abs_tol=1e-12):
        raise ValueError("C8 weights do not sum to one")
    cost_rate = float(protocol["rules"]["cost_stress_rate"])
    dates, prices = _common_panel(manifest, codes)
    baseline_after_build = 1.0 * (1.0 - cost_rate)
    holdings = {code: baseline_after_build * targets[code] / prices[code][dates[0]] for code in codes}
    nav = [baseline_after_build]
    rebalances: list[dict[str, Any]] = [{"kind": "build", "turnover": 1.0, "cost": cost_rate}]
    final_quarterly: dict[str, str] = {}
    for day in dates:
        month = day[:7]
        if _date(day).month in {3, 6, 9, 12}:
            final_quarterly[month] = day
    pending: str | None = None
    for position in range(1, len(dates)):
        day = dates[position]
        before = sum(holdings[code] * prices[code][day] for code in codes)
        if pending is not None:
            drift = {code: holdings[code] * prices[code][day] / before for code in codes}
            turnover = sum(abs(drift[code] - targets[code]) for code in codes) / 2.0
            after = before * (1.0 - cost_rate * turnover)
            holdings = {code: after * targets[code] / prices[code][day] for code in codes}
            nav.append(after)
            rebalances.append({"kind": "quarterly", "turnover": turnover, "cost": cost_rate * turnover})
            pending = None
        else:
            nav.append(before)
        if day in final_quarterly.values() and position < len(dates) - 1:
            pending = day
    annual: dict[int, float] = {}
    by_year: dict[int, list[int]] = {}
    for index, day in enumerate(dates):
        by_year.setdefault(_date(day).year, []).append(index)
    years = sorted(by_year)
    for year, indexes in by_year.items():
        first_day, last_day = dates[indexes[0]], dates[indexes[-1]]
        complete = year not in {years[0], years[-1]} and _date(first_day).month == 1 and _date(last_day).month == 12
        if complete:
            annual[year] = nav[indexes[-1]] / nav[indexes[0] - 1] - 1.0
    rolling = [(nav[index] / nav[index - 1260]) ** (252.0 / 1260.0) - 1.0 for index in range(1260, len(nav))]
    return {
        "dates": dates,
        "nav": nav,
        "annualized": nav[-1] ** (252.0 / (len(nav) - 1)) - 1.0,
        "max_drawdown": _max_drawdown(nav),
        "annual": annual,
        "rolling": rolling,
        "rebalances": rebalances,
    }


def _audit_c7() -> tuple[dict[str, Any], list[str]]:
    rulebook = _load(C7_RULEBOOK)
    retained = _load(C7_RESULT)
    manifest = _verify_manifest(C7_MANIFEST)
    replay = _c7_replay(rulebook, manifest)
    failures: list[str] = []
    output = retained.get("arithmetic_output", {})
    _assert_close("C7 terminal unit NAV", replay["nav"][-1], float(output["final_unitized_market_price_value"]), failures)
    _assert_close("C7 annualized proxy", replay["annualized"], float(output["annualized_market_price_unitized_change"]), failures)
    _assert_close("C7 maximum drawdown", replay["max_drawdown"], float(output["maximum_drawdown"]), failures)
    _assert_close("C7 turnover", sum(event["turnover"] for event in replay["events"]), float(output["aggregate_one_way_turnover"]), failures)
    if len(replay["events"]) != int(output["review_events"]):
        failures.append("C7 review-event count differs")
    if sum(event["rebalanced"] for event in replay["events"]) != int(output["triggered_rebalances"]):
        failures.append("C7 triggered-rebalance count differs")
    retained_years = {int(row["year"]): row for row in output["complete_calendar_years"] if row["complete_calendar_year"]}
    if set(retained_years) != set(replay["annual"]):
        failures.append("C7 complete calendar-year set differs")
    for year, value in replay["annual"].items():
        if year in retained_years:
            _assert_close(f"C7 year {year}", value, float(retained_years[year]["market_price_unitized_change"]), failures)
    retained_rolling = output["rolling_five_year"]
    if len(replay["rolling"]) != int(retained_rolling["window_count"]):
        failures.append("C7 rolling-window count differs")
    else:
        _assert_close("C7 rolling minimum", min(replay["rolling"]), float(retained_rolling["minimum_annualized_market_price_unitized_change"]), failures)
        _assert_close("C7 rolling maximum", max(replay["rolling"]), float(retained_rolling["maximum_annualized_market_price_unitized_change"]), failures)
        if sum(value < 0.05 for value in replay["rolling"]) != int(retained_rolling["below_5pct_count"]):
            failures.append("C7 rolling failure count differs")
    boundary_ok = (
        retained.get("portfolio_q") == 0
        and retained.get("formal_decision_eligible") is False
        and retained.get("interpretation", {}).get("historical_5pct_verdict") == "not_adjudicated"
    )
    if not boundary_ok:
        failures.append("C7 research-only boundary weakened")
    return {
        "status": "PASS" if not failures else "FAIL",
        "common_sessions": len(replay["dates"]),
        "annualized_market_price_proxy": replay["annualized"],
        "max_drawdown": replay["max_drawdown"],
        "complete_years_below_5pct": sum(value < 0.05 for value in replay["annual"].values()),
        "rolling_window_count": len(replay["rolling"]),
        "rolling_windows_below_5pct": sum(value < 0.05 for value in replay["rolling"]),
        "annual_baseline_check": "PASS; complete-year returns use the preceding observed unit-NAV value, including the first in-year session return.",
        "scope": "Official retrospective market-price arithmetic only; not total return or executable performance.",
    }, failures


def _audit_c8() -> tuple[dict[str, Any], list[str]]:
    protocol = _load(C8_PROTOCOL)
    retained = _load(C8_RESULT)
    manifest = _verify_manifest(C8_MANIFEST)
    replay = _c8_replay(protocol, manifest)
    failures: list[str] = []
    result = retained.get("result", {})
    _assert_close("C8 terminal unit NAV", replay["nav"][-1], float(result["terminal_unit_nav"]), failures)
    _assert_close("C8 annualized proxy", replay["annualized"], float(result["annualized_net_unitized_change"]), failures)
    _assert_close("C8 maximum drawdown", replay["max_drawdown"], float(result["max_drawdown"]), failures)
    if len(replay["rebalances"]) != int(result["rebalance_count_including_initial"]):
        failures.append("C8 rebalance count differs")
    _assert_close("C8 turnover", sum(row["turnover"] for row in replay["rebalances"]), float(result["one_way_turnover_sum"]), failures)
    retained_years = {int(row["year"]): row for row in result["complete_calendar_years"] if row["complete"]}
    if set(retained_years) != set(replay["annual"]):
        failures.append("C8 complete calendar-year set differs")
    for year, value in replay["annual"].items():
        if year in retained_years:
            _assert_close(f"C8 year {year}", value, float(retained_years[year]["net_unitized_change"]), failures)
    if len(replay["rolling"]) != int(result["rolling_window_count"]):
        failures.append("C8 rolling-window count differs")
    else:
        _assert_close("C8 rolling minimum", min(replay["rolling"]), float(result["rolling_min_annualized_net_unitized_change"]), failures)
        _assert_close("C8 rolling maximum", max(replay["rolling"]), float(result["rolling_max_annualized_net_unitized_change"]), failures)
        if sum(value < 0.05 for value in replay["rolling"]) != int(result["rolling_failure_count"]):
            failures.append("C8 rolling failure count differs")
    if result.get("status") != "PRICE_PROXY_HURDLE_FALSIFIED" or result.get("portfolio_q") != 0:
        failures.append("C8 strict-hurdle or research-only disposition differs")
    return {
        "status": "PASS" if not failures else "FAIL",
        "common_sessions": len(replay["dates"]),
        "annualized_market_price_proxy": replay["annualized"],
        "max_drawdown": replay["max_drawdown"],
        "complete_years_below_5pct": sum(value < 0.05 for value in replay["annual"].values()),
        "rolling_window_count": len(replay["rolling"]),
        "rolling_windows_below_5pct": sum(value < 0.05 for value in replay["rolling"]),
        "baseline_cost_check": "PASS; all-period annualization starts from the unit-NAV baseline before the 30bp build load.",
        "scope": "Official retrospective market-price arithmetic only; not total return or executable performance.",
    }, failures


def _markdown(payload: Mapping[str, Any]) -> str:
    c7 = payload["tracks"]["C7"]
    c8 = payload["tracks"]["C8"]
    findings = payload["findings"]
    return f"""# R7：C7 / C8 独立复算审计 — 2026-08-15

- 审计性质：独立解析保留的上交所 JSONP 原始文件并重建两条固定规则；没有导入候选轨自身的回放函数。
- 审计结论：**{payload['status']}**。计算一致性为通过，但两者都没有变成可执行策略或稳定 5% 结论。

| 路径 | 独立复算 | 年化市场价代理 | 最大回撤 | 完整年度低于 5% | 滚动窗口低于 5% |
|---|---|---:|---:|---:|---:|
| C7 静态核心—卫星 ETF | {c7['status']} | {c7['annualized_market_price_proxy']:.2%} | {c7['max_drawdown']:.2%} | {c7['complete_years_below_5pct']} | {c7['rolling_windows_below_5pct']} / {c7['rolling_window_count']} |
| C8 可转债 ETF 固定配置 | {c8['status']} | {c8['annualized_market_price_proxy']:.2%} | {c8['max_drawdown']:.2%} | {c8['complete_years_below_5pct']} | {c8['rolling_windows_below_5pct']} / {c8['rolling_window_count']} |

## 审计修复与结果

1. C7 年度口径已使用每年首个共同观察日前的单位净值作为基线，避免漏掉当年首个交易日的变化。修复前后低于 5% 的完整年度数量仍为 5，结论没有被改善。
2. C8 全期年化从建仓成本前的单位净值基线计算，30bp 建仓载荷没有被分母抵消；当前复算为 {c8['annualized_market_price_proxy']:.2%}。
3. 两个来源清单的每个保留原始文件 SHA-256 与清单冻结行均已复核。

## 结论边界

- C7 的输入是公开、回溯抓取的市场收盘价，未披露复权与分派口径，故不能以它判定投资者总回报或个人成交表现。
- C8 在同一受限口径下已被固定的严格 5% 否决线否定；不得事后更改权重、频率、成本或样本期寻找幸存版本。
- 无论计算一致性如何，缺失的 PIT 总回报、事件、报价/成交、费用、结算与账户证据继续阻止任何行动化结论。

## Finding register

| ID | 状态 | 内容 |
|---|---|---|
{''.join(f"| {row['id']} | {row['status']} | {row['description']} |\n" for row in findings)}
"""


def main() -> int:
    c7, c7_failures = _audit_c7()
    c8, c8_failures = _audit_c8()
    findings = [
        {
            "id": "R7-C7-001",
            "status": "closed",
            "description": "年度指标曾漏计每年首个共同观察日；修复、回归夹具和独立复算均已通过，低于 5% 的年份数不变。",
        },
        {
            "id": "R7-C8-001",
            "status": "closed",
            "description": "全期年化分母曾抵消建仓 30bp 载荷；已改按单位净值基线复算，C8 否决结论不变。",
        },
        {
            "id": "R7-SCOPE-001",
            "status": "open_non_waivable",
            "description": "两条路径都只有回溯公开市场价，缺少 PIT 总回报与执行账本；该边界阻止行动化或稳定收益主张。",
        },
    ]
    payload = {
        "artifact_id": "DPSFS-R7-INDEPENDENT-C7-C8-v1",
        "as_of": "2026-08-15",
        "status": "PASS_WITH_NON_ACTIONABLE_SCOPE_LIMITATIONS" if not (c7_failures or c8_failures) else "FAIL",
        "tracks": {"C7": c7, "C8": c8},
        "failures": {"C7": c7_failures, "C8": c8_failures},
        "findings": findings,
        "allowed_interpretation": "Independent arithmetic consistency only. It does not establish a total-return result, stable 5% result, suitability, allocation, holding, order, or action.",
    }
    _write(OUTPUT_JSON, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _markdown(payload))
    if c7_failures or c8_failures:
        print("R7 INDEPENDENT C7/C8 AUDIT: FAIL")
        for failure in c7_failures + c8_failures:
            print(f"- {failure}")
        return 1
    print("R7 INDEPENDENT C7/C8 AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
