#!/usr/bin/env python3
"""Independently rederive and audit C11's published-NAV proxy result.

The checker intentionally does not import C11's capture/replay module.  It
checks retained source hashes, parses the raw manager-published NAV series
itself, and compares a separately computed result with the retained C11
artifact.  It cannot turn the proxy into a holder result or external action.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RAW_DIR = CASE_DIR / "sources" / f"c11-market-neutral-fund-{DATE_TAG}"
MANIFEST_JSON = RAW_DIR / "manifest.json"
PROTOCOL_JSON = CASE_DIR / "analysis" / f"c11_market_neutral_single_fund_protocol_{DATE_TAG}.json"
RESULT_JSON = CASE_DIR / "analysis" / f"c11_market_neutral_fund_nav_proxy_{DATE_TAG}.json"
OUTPUT_JSON = CASE_DIR / "analysis" / f"r8_c11_independent_audit_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"r8_c11_independent_audit_{DATE_TAG}.md"
NAV_FILENAME = "008856_official_nav_all_20260815.js"
EXPECTED_FILES = {
    "008856_product_summary_20260529.pdf",
    "008856_open_notice_20260512.pdf",
    NAV_FILENAME,
    "008856_official_nav_history_page_20260815.html",
}
TOLERANCE = 1e-12


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"required artifact absent: {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"artifact must be a JSON object: {path}")
    return result


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def _verify_manifest() -> dict[str, Any]:
    manifest = _load(MANIFEST_JSON)
    files = manifest.get("files")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(files, list) or not isinstance(frozen, list):
        raise ValueError("C11 manifest lacks files or frozen files")
    file_by_path = {
        str(row.get("path")): row for row in files if isinstance(row, Mapping)
    }
    frozen_by_path = {
        str(row.get("path")): row for row in frozen if isinstance(row, Mapping)
    }
    if set(file_by_path) != set(frozen_by_path):
        raise ValueError("C11 manifest file and source-freeze path sets differ")
    if {Path(path).name for path in file_by_path} != EXPECTED_FILES:
        raise ValueError("C11 manifest does not contain the fixed four-source set")
    for relative, row in file_by_path.items():
        path = REPO_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"manifested C11 raw source absent: {relative}")
        if path.stat().st_size != int(row.get("bytes", -1)):
            raise ValueError(f"manifested C11 raw source byte mismatch: {relative}")
        if _sha256(path) != row.get("sha256"):
            raise ValueError(f"manifested C11 raw source hash mismatch: {relative}")
        frozen_row = frozen_by_path[relative]
        if {
            key: row.get(key) for key in ("path", "bytes", "sha256")
        } != {
            key: frozen_row.get(key) for key in ("path", "bytes", "sha256")
        }:
            raise ValueError(f"C11 source-freeze mismatch: {relative}")
    return manifest


def _parse_nav() -> tuple[list[str], list[float]]:
    raw_path = RAW_DIR / NAV_FILENAME
    payload = json.loads(raw_path.read_bytes().decode("gb18030"))
    dates = payload.get("ShowData")
    values = payload.get("leijiJingzhiName")
    if not isinstance(dates, list) or not isinstance(values, list) or len(dates) != len(values):
        raise ValueError("C11 raw NAV date/value arrays are not aligned")
    if len(dates) < 1261:
        raise ValueError("C11 raw NAV has insufficient observations")
    parsed_dates: list[str] = []
    parsed_values: list[float] = []
    prior: date | None = None
    for raw_day, raw_value in zip(dates, values, strict=True):
        if not isinstance(raw_day, str):
            raise ValueError("C11 raw NAV date is not text")
        try:
            day = date.fromisoformat(raw_day)
        except ValueError as exc:
            raise ValueError(f"C11 raw NAV date malformed: {raw_day!r}") from exc
        value = float(raw_value)
        if prior is not None and day <= prior:
            raise ValueError("C11 raw NAV dates are not strictly increasing")
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError("C11 raw cumulative NAV is invalid")
        prior = day
        parsed_dates.append(raw_day)
        parsed_values.append(value)
    return parsed_dates, parsed_values


def _complete_years(dates: list[str], values: list[float]) -> list[dict[str, Any]]:
    by_year: dict[int, list[int]] = {}
    for index, raw_day in enumerate(dates):
        by_year.setdefault(date.fromisoformat(raw_day).year, []).append(index)
    lower_year, upper_year = min(by_year), max(by_year)
    result: list[dict[str, Any]] = []
    for year, indexes in sorted(by_year.items()):
        first_index, last_index = indexes[0], indexes[-1]
        first_day, last_day = dates[first_index], dates[last_index]
        complete = (
            year not in {lower_year, upper_year}
            and first_day[5:7] == "01"
            and last_day[5:7] == "12"
            and first_index > 0
        )
        result.append(
            {
                "year": year,
                "first_observation": first_day,
                "last_observation": last_day,
                "complete": complete,
                "cumulative_nav_change": values[last_index] / values[first_index - 1] - 1.0 if complete else None,
            }
        )
    return result


def _max_drawdown(values: list[float]) -> float:
    peak = values[0]
    worst = 0.0
    for value in values:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1.0)
    return worst


def _independent_replay(protocol: Mapping[str, Any]) -> dict[str, Any]:
    if protocol.get("artifact_id") != "DPSFS-C11-MN-FUND-v1":
        raise ValueError("C11 protocol ID differs")
    if protocol.get("portfolio_q") != 0:
        raise ValueError("C11 protocol does not retain q=0")
    nav_test = protocol.get("nav_proxy_test")
    if not isinstance(nav_test, Mapping):
        raise ValueError("C11 protocol lacks NAV test")
    hurdle = float(nav_test.get("strict_hurdle", math.nan))
    if not math.isclose(hurdle, 0.05, abs_tol=TOLERANCE):
        raise ValueError("C11 protocol hurdle differs")
    dates, values = _parse_nav()
    if dates[0] != protocol.get("product", {}).get("contract_effective_date"):
        raise ValueError("C11 raw NAV start is not tied to the disclosed effective date")
    elapsed_days = (date.fromisoformat(dates[-1]) - date.fromisoformat(dates[0])).days
    annualized = (values[-1] / values[0]) ** (365.25 / elapsed_days) - 1.0
    years = _complete_years(dates, values)
    complete_years = [row for row in years if row["complete"]]
    lookback = 1260
    rolling = [
        {
            "start_date": dates[index - lookback],
            "end_date": dates[index],
            "annualized_cumulative_nav_change": (values[index] / values[index - lookback]) ** (252.0 / lookback) - 1.0,
        }
        for index in range(lookback, len(values))
    ]
    annual_failures = [row for row in complete_years if float(row["cumulative_nav_change"]) < hurdle]
    rolling_failures = [row for row in rolling if float(row["annualized_cumulative_nav_change"]) < hurdle]
    status = nav_test["fail_label"] if annual_failures or rolling_failures else nav_test["pass_label"]
    return {
        "status": status,
        "nav_observations": len(values),
        "first_observation": dates[0],
        "last_observation": dates[-1],
        "first_cumulative_nav": values[0],
        "terminal_cumulative_nav": values[-1],
        "elapsed_calendar_days": elapsed_days,
        "annualized_cumulative_nav_change": annualized,
        "maximum_drawdown_from_published_cumulative_nav": _max_drawdown(values),
        "complete_calendar_years": years,
        "complete_year_failure_count": len(annual_failures),
        "complete_year_failures": annual_failures,
        "rolling_window_observations": lookback,
        "rolling_window_count": len(rolling),
        "rolling_pass_count": len(rolling) - len(rolling_failures),
        "rolling_failure_count": len(rolling_failures),
        "rolling_min_annualized_cumulative_nav_change": min(
            (row["annualized_cumulative_nav_change"] for row in rolling), default=None
        ),
        "rolling_max_annualized_cumulative_nav_change": max(
            (row["annualized_cumulative_nav_change"] for row in rolling), default=None
        ),
        "rolling_failures": rolling_failures,
        "input_failures": [],
    }


def _compare(independent: Mapping[str, Any], retained: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    exact_keys = (
        "status",
        "nav_observations",
        "first_observation",
        "last_observation",
        "first_cumulative_nav",
        "terminal_cumulative_nav",
        "elapsed_calendar_days",
        "complete_calendar_years",
        "complete_year_failure_count",
        "complete_year_failures",
        "rolling_window_observations",
        "rolling_window_count",
        "rolling_pass_count",
        "rolling_failure_count",
        "rolling_failures",
        "input_failures",
    )
    for key in exact_keys:
        if independent.get(key) != retained.get(key):
            failures.append(f"retained result differs from independent result on {key}")
    numeric_keys = (
        "annualized_cumulative_nav_change",
        "maximum_drawdown_from_published_cumulative_nav",
        "rolling_min_annualized_cumulative_nav_change",
        "rolling_max_annualized_cumulative_nav_change",
    )
    for key in numeric_keys:
        observed, expected = independent.get(key), retained.get(key)
        if not isinstance(observed, (int, float)) or not isinstance(expected, (int, float)) or not math.isclose(float(observed), float(expected), rel_tol=TOLERANCE, abs_tol=TOLERANCE):
            failures.append(f"retained result differs from independent result on {key}")
    return failures


def _render(payload: Mapping[str, Any]) -> str:
    comparison = payload["comparison"]
    replay = payload["independent_result"]
    pct = lambda value: f"{100.0 * float(value):.2f}%"
    failed_years = ", ".join(str(row["year"]) for row in replay["complete_year_failures"]) or "无"
    return f"""# R8 C11 独立复核 — 2026-08-15

- 复核对象：`DPSFS-C11-MN-NAVPROXY-v1`，固定产品 `008856`。
- 结果：**`{payload['audit_status']}`**；复核脚本未导入 C11 的抓取或回放模块。
- 原始输入：4 个冻结的华夏基金一手文件，其中累计净值序列有 `{replay['nav_observations']}` 个观察，`{replay['first_observation']}` 至 `{replay['last_observation']}`。

## 独立重算结果

- 标签：`{replay['status']}`。
- 全期日历年化累计净值变化：`{pct(replay['annualized_cumulative_nav_change'])}`；累计净值最大回撤：`{pct(replay['maximum_drawdown_from_published_cumulative_nav'])}`。
- 完整年度低于 5% 的年份：`{failed_years}`。
- 滚动 `1,260` 观察间隔通过 `{replay['rolling_pass_count']}/{replay['rolling_window_count']}`，范围 `{pct(replay['rolling_min_annualized_cumulative_nav_change'])}` 至 `{pct(replay['rolling_max_annualized_cumulative_nav_change'])}`。

## 审计边界

本复核验证本地冻结文件、累计净值日期/数值结构，以及独立算术与 C11 留存结果的一致性。它不能验证历史页面发布时点、持有人申赎费用、确认日、渠道可用性、开放期、交易结果或未来表现。该路径仍是严格门槛下的否证，不能转化为持有、申赎、配置或外部行动。

比较结果：`{comparison['match_count']}` 个受检字段一致，`{comparison['failure_count']}` 个差异。机器副本：[r8_c11_independent_audit_20260815.json](r8_c11_independent_audit_20260815.json)。
"""


def main() -> int:
    manifest = _verify_manifest()
    protocol = _load(PROTOCOL_JSON)
    retained = _load(RESULT_JSON)
    retained_result = retained.get("result")
    if not isinstance(retained_result, Mapping):
        raise ValueError("C11 retained artifact lacks a result mapping")
    independent = _independent_replay(protocol)
    failures = _compare(independent, retained_result)
    source_record = retained.get("source_manifest", {})
    if source_record.get("sha256") != _sha256(MANIFEST_JSON):
        failures.append("C11 retained artifact source-manifest hash differs")
    payload: dict[str, Any] = {
        "audit_id": "DPSFS-R8-C11-INDEPENDENT-v1",
        "as_of": "2026-08-15",
        "audit_status": "PASS" if not failures else "FAIL",
        "independence_boundary": "The audit parses frozen raw NAV directly and does not import C11 capture/replay code.",
        "raw_source_manifest": {
            "path": str(MANIFEST_JSON.relative_to(REPO_ROOT)),
            "sha256": _sha256(MANIFEST_JSON),
            "capture_batch": manifest.get("capture_batch"),
            "file_count": len(manifest.get("files", [])),
        },
        "comparison": {
            "match_count": 20 - len(failures),
            "failure_count": len(failures),
            "failures": failures,
        },
        "independent_result": independent,
        "audit_boundary": "A local hash and arithmetic audit cannot establish historical publication timing, a holder result, dealing availability, suitability, a return guarantee, or action.",
    }
    _write(OUTPUT_JSON, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _render(payload))
    if failures:
        print("R8 C11 INDEPENDENT AUDIT: FAIL")
        print("\n".join(failures))
        return 1
    print("R8 C11 INDEPENDENT AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
