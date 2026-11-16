#!/usr/bin/env python3
"""Independently rederive C10's narrow gross-cash diagnostic.

This audit deliberately does not import C10's capture or calculation modules.
It verifies frozen raw-file hashes and reconstructs the retained annual
arithmetic from the public SSE close and dividend-event inputs.  The audit does
not make the result a total-return record, a historical selection test, or an
external action.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RAW_DIR = CASE_DIR / "sources" / f"c10-direct-equity-price-dividend-probe-{DATE_TAG}"
MANIFEST_JSON = RAW_DIR / "manifest.json"
CANDIDATE_JSON = CASE_DIR / "analysis" / f"c10_direct_equity_quality_distribution_candidate_{DATE_TAG}.json"
DIAGNOSTIC_JSON = CASE_DIR / "analysis" / f"c10_stock_gross_cash_dividend_diagnostic_{DATE_TAG}.json"
OUTPUT_JSON = CASE_DIR / "analysis" / f"r9_c10_independent_diagnostic_audit_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"r9_c10_independent_diagnostic_audit_{DATE_TAG}.md"
EXPECTED_WEIGHTS = {"600519": 0.30, "600900": 0.30, "601398": 0.25, "601088": 0.15}
EXPECTED_YEARS = (2022, 2023, 2024, 2025)
TOLERANCE = 1e-12


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"required artifact absent: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"artifact must be a JSON object: {path}")
    return value


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
        raise ValueError("C10 manifest lacks file/freeze records")
    by_path = {str(row.get("path")): row for row in files if isinstance(row, Mapping)}
    frozen_by_path = {str(row.get("path")): row for row in frozen if isinstance(row, Mapping)}
    if set(by_path) != set(frozen_by_path):
        raise ValueError("C10 manifest and source-freeze sets differ")
    for relative, row in by_path.items():
        path = REPO_ROOT / relative
        if not path.is_file() or path.stat().st_size != int(row.get("bytes", -1)) or _sha256(path) != row.get("sha256"):
            raise ValueError(f"C10 raw source mismatch: {relative}")
        frozen_row = frozen_by_path[relative]
        if {key: row.get(key) for key in ("path", "bytes", "sha256")} != {key: frozen_row.get(key) for key in ("path", "bytes", "sha256")}:
            raise ValueError(f"C10 frozen-file record differs: {relative}")
    return manifest


def _jsonp(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    left, right = raw.find("("), raw.rfind(")")
    if left < 1 or right <= left:
        raise ValueError(f"C10 JSONP envelope malformed: {path.name}")
    value = json.loads(raw[left + 1 : right])
    if not isinstance(value, dict):
        raise ValueError(f"C10 JSONP root is not an object: {path.name}")
    return value


def _prices(code: str) -> list[tuple[int, float]]:
    payload = _jsonp(RAW_DIR / f"sse_dayk_{code}_latest2000.jsonp")
    rows = payload.get("kline")
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"C10 price series absent: {code}")
    result: list[tuple[int, float]] = []
    previous = -1
    for row in rows:
        if not isinstance(row, list) or len(row) < 5:
            raise ValueError(f"C10 price row malformed: {code}")
        day, close = int(row[0]), float(row[4])
        if day <= previous or not math.isfinite(close) or close <= 0.0:
            raise ValueError(f"C10 price values malformed: {code}")
        previous = day
        result.append((day, close))
    return result


def _dividend_cash(code: str, year: int) -> float:
    payload = _jsonp(RAW_DIR / f"sse_dividend_{code}_{year}.jsonp")
    rows = payload.get("result")
    if rows is None:
        rows = payload.get("pageHelp", {}).get("data")
    if not isinstance(rows, list):
        raise ValueError(f"C10 dividend rows absent: {code}/{year}")
    cash = 0.0
    for row in rows:
        if not isinstance(row, Mapping):
            raise ValueError(f"C10 dividend row malformed: {code}/{year}")
        raw_day, raw_dividend = row.get("A_DIV_DATE"), row.get("A_BEFR_TAX_DIV")
        if raw_day in (None, "-") or raw_dividend in (None, "-"):
            continue
        ex_day = int(raw_day)
        if not (year * 10_000 + 101 <= ex_day <= year * 10_000 + 1231):
            raise ValueError(f"C10 dividend event falls outside its queried year: {code}/{year}")
        value = float(raw_dividend)
        if not math.isfinite(value):
            raise ValueError(f"C10 dividend value malformed: {code}/{year}")
        cash += value
    return cash


def _component_return(code: str, year: int) -> tuple[float, float]:
    rows = _prices(code)
    first_day, last_day = year * 10_000 + 101, year * 10_000 + 1231
    prior = [row for row in rows if row[0] < first_day]
    observed = [row for row in rows if first_day <= row[0] <= last_day]
    if not prior or not observed:
        raise ValueError(f"C10 annual price coverage absent: {code}/{year}")
    start_close, end_close = prior[-1][1], observed[-1][1]
    cash = _dividend_cash(code, year)
    return end_close / start_close - 1.0, (end_close + cash) / start_close - 1.0


def _independent_replay() -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for year in EXPECTED_YEARS:
        price_return = 0.0
        gross_cash_return = 0.0
        for code, weight in EXPECTED_WEIGHTS.items():
            price, gross = _component_return(code, year)
            price_return += weight * price
            gross_cash_return += weight * gross
        result.append(
            {
                "year": year,
                "fixed_target_weight_gross_cash_dividend_return": gross_cash_return,
                "fixed_target_weight_price_only_return": price_return,
            }
        )
    return result


def _close(actual: float, expected: float) -> bool:
    return math.isclose(actual, expected, rel_tol=TOLERANCE, abs_tol=TOLERANCE)


def _compare(independent: list[dict[str, Any]], diagnostic: Mapping[str, Any], candidate: Mapping[str, Any], manifest: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    if diagnostic.get("candidate_definition", {}).get("weights") != EXPECTED_WEIGHTS:
        failures.append("diagnostic weights differ from independent fixed weights")
    if candidate.get("fixed_diligence_basket", {}).get("weights_for_diagnostic_only") != EXPECTED_WEIGHTS:
        failures.append("candidate weights differ from independent fixed weights")
    observed_rows = diagnostic.get("annual_results")
    if not isinstance(observed_rows, list) or len(observed_rows) != len(independent):
        failures.append("diagnostic annual-result count differs")
    else:
        for expected, observed in zip(independent, observed_rows, strict=True):
            if int(observed.get("year", -1)) != expected["year"]:
                failures.append(f"diagnostic annual year differs: {expected['year']}")
                continue
            for key in ("fixed_target_weight_gross_cash_dividend_return", "fixed_target_weight_price_only_return"):
                actual = observed.get(key)
                if not isinstance(actual, (float, int)) or not _close(float(actual), float(expected[key])):
                    failures.append(f"diagnostic annual arithmetic differs: {expected['year']}/{key}")
    failures_years = [row["year"] for row in independent if row["fixed_target_weight_gross_cash_dividend_return"] < 0.05]
    summary = diagnostic.get("annual_result_summary", {})
    if summary.get("calendar_years_below_5pct") != failures_years:
        failures.append("diagnostic below-5% calendar-year list differs")
    strict = candidate.get("strict_return_gate", {})
    if strict.get("verdict") != "NO_STRICT_GATE_PASS" or strict.get("falsifying_years") != failures_years:
        failures.append("candidate strict-gate conclusion differs from independent annual result")
    fingerprint = diagnostic.get("source_fingerprint", {})
    if fingerprint.get("manifest_sha256") != _sha256(MANIFEST_JSON):
        failures.append("diagnostic source-manifest hash differs")
    if manifest.get("capture_batch") != RAW_DIR.name:
        failures.append("C10 capture batch name differs")
    return failures


def _render(payload: Mapping[str, Any]) -> str:
    replay = payload["independent_result"]
    pct = lambda value: f"{100.0 * float(value):.2f}%"
    rows = "\n".join(
        f"| {row['year']} | {pct(row['fixed_target_weight_gross_cash_dividend_return'])} | {pct(row['fixed_target_weight_price_only_return'])} |"
        for row in replay
    )
    below = ", ".join(str(year) for year in payload["below_5pct_years"])
    return f"""# R9 C10 独立算术复核 — 2026-08-15

- 复核对象：C10 四名固定研究篮子的原始收盘价加税前现金分配诊断。
- 结果：**`{payload['audit_status']}`**；复核程序未导入 C10 的抓取或计算模块。
- 已逐一复算的低于 5% 年份：`{below}`。

| 年份 | 独立重算的收盘价加现金分配变化 | 独立重算的仅收盘价变化 |
|---:|---:|---:|
{rows}

本复核只确认冻结原始文件、公式和 C10 留存算术的一致性。它不改变 C10 的限制：标的是事后选取，价格调整口径未披露，分配事件不构成完整权益／支付／税费账本，且没有报价、深度、成交、结算或账户记录。因此，两个低于线年份只能否证该窄口径诊断，不能被写成个人总回报、股票筛选有效性或外部操作。

受检字段一致 `{payload['comparison']['match_count']}` 项，差异 `{payload['comparison']['failure_count']}` 项。机器副本：[r9_c10_independent_diagnostic_audit_20260815.json](r9_c10_independent_diagnostic_audit_20260815.json)。
"""


def main() -> int:
    manifest = _verify_manifest()
    diagnostic = _load(DIAGNOSTIC_JSON)
    candidate = _load(CANDIDATE_JSON)
    independent = _independent_replay()
    failures = _compare(independent, diagnostic, candidate, manifest)
    payload: dict[str, Any] = {
        "audit_id": "DPSFS-R9-C10-INDEPENDENT-v1",
        "as_of": "2026-08-15",
        "audit_status": "PASS" if not failures else "FAIL",
        "independence_boundary": "The audit directly parses frozen C10 raw files and does not import C10 code.",
        "raw_source_manifest": {
            "path": str(MANIFEST_JSON.relative_to(REPO_ROOT)),
            "sha256": _sha256(MANIFEST_JSON),
            "capture_batch": manifest.get("capture_batch"),
            "file_count": len(manifest.get("files", [])),
        },
        "independent_result": independent,
        "below_5pct_years": [row["year"] for row in independent if row["fixed_target_weight_gross_cash_dividend_return"] < 0.05],
        "comparison": {"match_count": 9 - len(failures), "failure_count": len(failures), "failures": failures},
        "audit_boundary": "A local source-hash and arithmetic audit does not establish point-in-time data, investor total return, an executable fill, suitability, return guarantee, allocation, holding, or external action.",
    }
    _write(OUTPUT_JSON, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _render(payload))
    if failures:
        print("R9 C10 INDEPENDENT AUDIT: FAIL")
        print("\n".join(failures))
        return 1
    print("R9 C10 INDEPENDENT AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
