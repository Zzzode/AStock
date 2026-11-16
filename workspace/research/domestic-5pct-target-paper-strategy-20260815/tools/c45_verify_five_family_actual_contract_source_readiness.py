#!/usr/bin/env python3
"""Verify five-family SHFE actual-contract source readiness for C46.

This is a source-field and integrity audit.  It produces no signal, return,
position, allocation, or action result.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c15-shfe-actual-contract-eod-2019-2025-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c45_five_family_actual_contract_source_readiness_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c45_five_family_actual_contract_source_readiness_20260815.md"
EXPECTED_MANIFEST_SHA256 = "34e23ddf886bd1f1f6cb88610d8d730bd757c981b92b0aa51720c5471b1186d7"
FAMILIES = ("AU", "CU", "RB", "RU", "SP")
REQUIRED_FIELDS = ("OPENPRICE", "HIGHESTPRICE", "LOWESTPRICE", "SETTLEMENTPRICE", "VOLUME", "OPENINTEREST")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write(path: Path, contents: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(path)


def _positive(value: Any) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return math.isfinite(number) and number > 0.0


def _family(row: dict[str, Any]) -> str:
    return str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()


def _valid_delivery_month(value: Any) -> bool:
    string = str(value or "").strip()
    if len(string) != 4 or not string.isdigit():
        return False
    try:
        date(2000 + int(string[:2]), int(string[2:]), 15)
    except ValueError:
        return False
    return True


def _run() -> dict[str, Any]:
    if _sha256(MANIFEST_PATH) != EXPECTED_MANIFEST_SHA256:
        raise ValueError("C15 manifest hash changed")
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    family_stats: dict[str, dict[str, Any]] = {
        family: {
            "response_count_with_valid_actual_contract_row": 0,
            "valid_actual_contract_row_count": 0,
            "minimum_valid_actual_contract_rows_per_response": None,
            "maximum_valid_actual_contract_rows_per_response": 0,
            "first_observed_date": None,
            "last_observed_date": None,
        }
        for family in FAMILIES
    }
    missing_by_date: list[dict[str, Any]] = []
    records = sorted(manifest.get("records", []), key=lambda row: str(row["trade_date"]))
    for record in records:
        trade_date = date.fromisoformat(str(record["trade_date"]))
        raw_path = REPO_ROOT / str(record["path"])
        compressed = raw_path.read_bytes()
        if hashlib.sha256(compressed).hexdigest() != record.get("compressed_sha256"):
            raise ValueError(f"compressed source mismatch: {trade_date}")
        raw = gzip.decompress(compressed)
        if hashlib.sha256(raw).hexdigest() != record.get("raw_sha256"):
            raise ValueError(f"raw source mismatch: {trade_date}")
        payload = json.loads(raw.decode("utf-8"))
        if str(payload.get("report_date") or "") != trade_date.strftime("%Y%m%d"):
            raise ValueError(f"report date mismatch: {trade_date}")
        rows = payload.get("o_curinstrument")
        if not isinstance(rows, list):
            raise ValueError(f"missing contract rows: {trade_date}")
        valid_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            if not isinstance(row, dict):
                continue
            family = _family(row)
            if family not in family_stats or not _valid_delivery_month(row.get("DELIVERYMONTH")):
                continue
            if not all(_positive(row.get(field)) for field in REQUIRED_FIELDS):
                continue
            valid_by_family[family].append(row)
        missing = [family for family in FAMILIES if not valid_by_family[family]]
        if missing:
            missing_by_date.append({"trade_date": trade_date.isoformat(), "families": missing})
        for family in FAMILIES:
            valid_rows = valid_by_family[family]
            if not valid_rows:
                continue
            stats = family_stats[family]
            stats["response_count_with_valid_actual_contract_row"] += 1
            stats["valid_actual_contract_row_count"] += len(valid_rows)
            minimum = stats["minimum_valid_actual_contract_rows_per_response"]
            stats["minimum_valid_actual_contract_rows_per_response"] = len(valid_rows) if minimum is None else min(int(minimum), len(valid_rows))
            stats["maximum_valid_actual_contract_rows_per_response"] = max(int(stats["maximum_valid_actual_contract_rows_per_response"]), len(valid_rows))
            stats["first_observed_date"] = stats["first_observed_date"] or trade_date.isoformat()
            stats["last_observed_date"] = trade_date.isoformat()
    all_families_complete = not missing_by_date and all(
        stats["response_count_with_valid_actual_contract_row"] == len(records) for stats in family_stats.values()
    )
    return {
        "schema_version": "c45_five_family_actual_contract_source_readiness.v1",
        "artifact_id": "D5PT-C45-v1",
        "as_of": "2026-08-15",
        "result": "PASS" if all_families_complete else "FAIL",
        "research_only": True,
        "formal_decision_eligible": False,
        "external_orders": False,
        "source": {
            "manifest_path": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
            "manifest_sha256": EXPECTED_MANIFEST_SHA256,
            "first_retained_response": str(records[0]["trade_date"]),
            "last_retained_response": str(records[-1]["trade_date"]),
            "retained_response_count": len(records),
            "non_record_count": len(manifest.get("non_records", [])),
        },
        "families": list(FAMILIES),
        "required_actual_contract_fields": list(REQUIRED_FIELDS),
        "family_stats": family_stats,
        "missing_valid_row_by_date": missing_by_date,
        "limitations": [
            "Historical response files were retrieved retrospectively. Their integrity does not prove original-date availability, immutability, revision history, or data rights.",
            "Valid EOD rows establish only a limited actual-contract settlement-mark input. They do not establish bid/ask, depth, fills, fees, margin, collateral, limits, delivery, offset eligibility, broker access, or investor outcomes.",
            "The 128 retained HTTP 404 responses are non-records. This audit does not infer a complete exchange calendar from them.",
            "A PASS is a source-field readiness result only. It does not pass a performance test or admit a strategy for use.",
        ],
    }


def _render_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# C45 五家族实际合约日度来源就绪审计",
        "",
        f"- 结果：`{result['result']}`。",
        f"- 范围：{result['source']['first_retained_response']} 至 {result['source']['last_retained_response']} 的 {result['source']['retained_response_count']} 份哈希核验上期所日度响应。",
        "- 结论边界：本审计只核验五个家族在每份留存响应中是否存在带正值 OHLC、结算价、成交量和持仓量的实际合约行。它不计算表现、不构造持仓，也不放行任何外部动作。",
        "",
        "| 家族 | 有效响应 | 有效实际合约行 | 每响应最少/最多有效行 | 首末观察日 |",
        "|---|---:|---:|---:|---|",
    ]
    for family in result["families"]:
        row = result["family_stats"][family]
        lines.append(
            f"| {family} | {row['response_count_with_valid_actual_contract_row']} | {row['valid_actual_contract_row_count']} | "
            f"{row['minimum_valid_actual_contract_rows_per_response']}/{row['maximum_valid_actual_contract_rows_per_response']} | "
            f"{row['first_observed_date']} 至 {row['last_observed_date']} |"
        )
    lines.extend(
        [
            "",
            f"留存的 `{result['source']['non_record_count']}` 个 HTTP 404 非记录不被当作交易日或非交易日。若后续研究使用这些输入，仍需分别补齐逐时点可得性、实际末日/交割状态、保证金与限仓、费用、双边报价、成交、账户和结果记录。",
            "",
            "`PASS` 只代表有限的来源字段与完整性就绪，不能表示策略通过、收益达标、可用或可执行。",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    result = _run()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    _write(OUTPUT_MD, _render_markdown(result))
    print(f"{result['result']}: {OUTPUT_JSON.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
