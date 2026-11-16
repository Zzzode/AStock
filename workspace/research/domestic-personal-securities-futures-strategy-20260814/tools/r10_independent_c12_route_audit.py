#!/usr/bin/env python3
"""Independently audit C12's actual-contract route observations.

The audit parses frozen CFFEX CSV samples without importing C12's capture or
artifact-building module.  It checks raw hashes, actual-contract row counts,
leading-contract observations and the dated T-family screen.  It does not
create a cash/futures transaction, return series, or personal-access result.
"""

from __future__ import annotations

import calendar
import csv
import hashlib
import json
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
DATE_TAG = "20260815"
RAW_DIR = CASE_DIR / "sources" / f"c12-official-cash-futures-basis-{DATE_TAG}"
MANIFEST_JSON = RAW_DIR / "manifest.json"
ROUTE_JSON = CASE_DIR / "analysis" / f"c12_cffex_actual_contract_route_{DATE_TAG}.json"
RULEBOOK_JSON = CASE_DIR / "analysis" / f"c12_cash_futures_basis_rulebook_{DATE_TAG}.json"
FEASIBILITY_JSON = CASE_DIR / "analysis" / f"c12_cash_futures_basis_feasibility_{DATE_TAG}.json"
OUTPUT_JSON = CASE_DIR / "analysis" / f"r10_c12_independent_route_audit_{DATE_TAG}.json"
OUTPUT_MD = CASE_DIR / "analysis" / f"r10_c12_independent_route_audit_{DATE_TAG}.md"
SAMPLE_DATES = ("20160104", "20180102", "20200102", "20220104", "20240102", "20260814")
DECISION_DATE = date(2026, 8, 14)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"required artifact absent: {path}")
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"artifact is not a JSON object: {path}")
    return result


def _write(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def _verify_manifest() -> dict[str, Any]:
    manifest = _load(MANIFEST_JSON)
    files = manifest.get("files")
    frozen = manifest.get("source_freeze", {}).get("frozen_files")
    if not isinstance(files, list) or not isinstance(frozen, list):
        raise ValueError("C12 manifest lacks file/freeze rows")
    by_path = {str(row.get("path")): row for row in files if isinstance(row, Mapping)}
    frozen_by_path = {str(row.get("path")): row for row in frozen if isinstance(row, Mapping)}
    if set(by_path) != set(frozen_by_path):
        raise ValueError("C12 manifest and source-freeze paths differ")
    for relative, row in by_path.items():
        path = REPO_ROOT / relative
        if not path.is_file() or path.stat().st_size != int(row.get("bytes", -1)) or _sha256(path) != row.get("sha256"):
            raise ValueError(f"C12 raw source mismatch: {relative}")
        frozen_row = frozen_by_path[relative]
        if {key: row.get(key) for key in ("path", "bytes", "sha256")} != {key: frozen_row.get(key) for key in ("path", "bytes", "sha256")}:
            raise ValueError(f"C12 source-freeze record differs: {relative}")
    return manifest


def _family(contract: str) -> str | None:
    if contract.startswith("TF") and contract[2:].isdigit():
        return "TF"
    if contract.startswith("TS") and contract[2:].isdigit():
        return "TS"
    if contract.startswith("TL") and contract[2:].isdigit():
        return "TL"
    if contract.startswith("T") and contract[1:].isdigit():
        return "T"
    return None


def _num(raw: str) -> float | None:
    raw = raw.strip()
    return None if raw in {"", "--", "null", "None"} else float(raw)


def _actual_rows(day: str) -> list[dict[str, Any]]:
    path = RAW_DIR / f"cffex_actual_contract_daily_{day}.csv"
    rows = list(csv.reader(path.read_bytes().decode("gb18030").splitlines()))
    if not rows or "合约代码" not in rows[0][0]:
        raise ValueError(f"C12 CSV header malformed: {day}")
    result: list[dict[str, Any]] = []
    for row in rows[1:]:
        if not row:
            continue
        contract = row[0].strip().upper()
        family = _family(contract)
        if family is None:
            continue
        if len(row) < 11:
            raise ValueError(f"C12 short contract row: {day}/{contract}")
        result.append(
            {
                "contract": contract,
                "family": family,
                "open": _num(row[1]),
                "high": _num(row[2]),
                "low": _num(row[3]),
                "volume": _num(row[4]),
                "turnover": _num(row[5]),
                "open_interest": _num(row[6]),
                "open_interest_change": _num(row[7]),
                "close": _num(row[8]),
                "settlement": _num(row[9]),
                "previous_settlement": _num(row[10]),
            }
        )
    return result


def _leading(rows: list[dict[str, Any]], family: str) -> dict[str, Any] | None:
    candidates = [
        row for row in rows
        if row["family"] == family
        and row["settlement"] is not None
        and row["volume"] is not None
        and row["open_interest"] is not None
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda row: (-float(row["open_interest"]), -float(row["volume"]), str(row["contract"])))[0]


def _second_friday(contract: str) -> date:
    digits = contract[2:] if contract.startswith(("TF", "TS", "TL")) else contract[1:]
    if len(digits) != 4 or not digits.isdigit():
        raise ValueError(f"unexpected actual contract code: {contract}")
    year, month = 2000 + int(digits[:2]), int(digits[2:])
    fridays = [week[calendar.FRIDAY] for week in calendar.monthcalendar(year, month) if week[calendar.FRIDAY]]
    return date(year, month, fridays[1])


def _independent_route() -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None]:
    samples: list[dict[str, Any]] = []
    current_t_rows: list[dict[str, Any]] = []
    for day in SAMPLE_DATES:
        rows = _actual_rows(day)
        counts = {family: sum(row["family"] == family for row in rows) for family in ("T", "TF", "TS", "TL")}
        samples.append(
            {
                "trade_date": f"{day[:4]}-{day[4:6]}-{day[6:]}",
                "actual_contract_rows_by_family": counts,
                "leading_t": _leading(rows, "T"),
                "leading_tf": _leading(rows, "TF"),
            }
        )
        if day == "20260814":
            current_t_rows = [row for row in rows if row["family"] == "T"]
    screened: list[dict[str, Any]] = []
    for row in current_t_rows:
        last_trade = _second_friday(row["contract"])
        days = (last_trade - DECISION_DATE).days
        screened.append(
            {
                **row,
                "scheduled_last_trade_date": last_trade.isoformat(),
                "scheduled_days_to_last_trade": days,
                "eligible_for_dated_research_screen": (
                    60 <= days <= 150
                    and row["settlement"] is not None and float(row["settlement"]) > 0.0
                    and row["volume"] is not None and float(row["volume"]) > 0.0
                    and row["open_interest"] is not None and float(row["open_interest"]) > 0.0
                ),
            }
        )
    eligible = [row for row in screened if row["eligible_for_dated_research_screen"]]
    selected = sorted(eligible, key=lambda row: (-float(row["open_interest"]), -float(row["volume"]), str(row["contract"])))[0] if eligible else None
    return samples, screened, selected


def _compare(samples: list[dict[str, Any]], screen: list[dict[str, Any]], selected: dict[str, Any] | None, route: Mapping[str, Any], rulebook: Mapping[str, Any], feasibility: Mapping[str, Any], manifest: Mapping[str, Any]) -> list[str]:
    failures: list[str] = []
    retained_samples = route.get("actual_contract_source_route", {}).get("samples")
    if not isinstance(retained_samples, list) or len(retained_samples) != len(samples):
        failures.append("C12 retained sample count differs")
    else:
        for expected, observed in zip(samples, retained_samples, strict=True):
            for key in ("trade_date", "actual_contract_rows_by_family", "leading_t", "leading_tf"):
                if expected.get(key) != observed.get(key):
                    failures.append(f"C12 retained sample differs: {expected['trade_date']}/{key}")
    retained_screen = route.get("dated_t_family_research_screen", {})
    if retained_screen.get("all_actual_t_rows") != screen:
        failures.append("C12 dated T screen differs")
    if retained_screen.get("selected_actual_contract") != selected:
        failures.append("C12 dated selected actual contract differs")
    if selected is None or selected.get("contract") != "T2612":
        failures.append("independent C12 dated screen did not select T2612")
    if rulebook.get("status") != "RESEARCH_SPECIFICATION_NOT_ACTION_READY":
        failures.append("C12 rulebook status differs")
    if feasibility.get("status") != "NOT_FEASIBLE_FOR_STRICT_5PCT_OR_PERSONAL_EXECUTION":
        failures.append("C12 feasibility status differs")
    if manifest.get("capture_batch") != RAW_DIR.name:
        failures.append("C12 capture batch name differs")
    return failures


def _render(payload: Mapping[str, Any]) -> str:
    selected = payload["independent_selected_contract"]
    lines = "\n".join(
        f"| {item['trade_date']} | {item['actual_contract_rows_by_family']['T']} | {item['actual_contract_rows_by_family']['TF']} | {item['leading_t']['contract'] if item['leading_t'] else 'n/a'} | {item['leading_tf']['contract'] if item['leading_tf'] else 'n/a'} |"
        for item in payload["independent_samples"]
    )
    return f"""# R10 C12 实际合约路径独立复核 — 2026-08-15

- 结果：**`{payload['audit_status']}`**；复核程序未导入 C12 的抓取或生成模块。
- 2026-08-14 冻结筛选独立选择：`{selected['contract'] if selected else 'none'}`，仅为实际合约来源路径观察。

| 日期 | T 行数 | TF 行数 | T 持仓量领先合约 | TF 持仓量领先合约 |
|---|---:|---:|---|---|
{lines}

复核确认六个冻结 CSV 的哈希、实际合约行计数、领先合约和固定 60--150 日筛选与 C12 留存结果一致。它没有也不能构造现金券交割篮子、转换因子历史、融资／回购／保证金／费税、两腿报价和成交、账户／托管路径或五年收益。C12 因此仍是严格门槛下不可用的研究候选，不是基差交易指令。

受检字段一致 `{payload['comparison']['match_count']}` 项，差异 `{payload['comparison']['failure_count']}` 项。机器副本：[r10_c12_independent_route_audit_20260815.json](r10_c12_independent_route_audit_20260815.json)。
"""


def main() -> int:
    manifest = _verify_manifest()
    route, rulebook, feasibility = _load(ROUTE_JSON), _load(RULEBOOK_JSON), _load(FEASIBILITY_JSON)
    samples, screen, selected = _independent_route()
    failures = _compare(samples, screen, selected, route, rulebook, feasibility, manifest)
    payload: dict[str, Any] = {
        "audit_id": "DPSFS-R10-C12-INDEPENDENT-v1",
        "as_of": "2026-08-15",
        "audit_status": "PASS" if not failures else "FAIL",
        "independence_boundary": "The audit parses frozen CFFEX CSV files directly and does not import C12 code.",
        "raw_source_manifest": {"path": str(MANIFEST_JSON.relative_to(REPO_ROOT)), "sha256": _sha256(MANIFEST_JSON), "capture_batch": manifest.get("capture_batch"), "file_count": len(manifest.get("files", []))},
        "independent_samples": samples,
        "independent_t_screen": screen,
        "independent_selected_contract": selected,
        "comparison": {"match_count": 13 - len(failures), "failure_count": len(failures), "failures": failures},
        "audit_boundary": "A local hash and source-route audit cannot prove cash/futures paired execution, personal access, a return result, a guarantee, allocation, holding, or external action.",
    }
    _write(OUTPUT_JSON, json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    _write(OUTPUT_MD, _render(payload))
    if failures:
        print("R10 C12 INDEPENDENT ROUTE AUDIT: FAIL")
        print("\n".join(failures))
        return 1
    print("R10 C12 INDEPENDENT ROUTE AUDIT: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
