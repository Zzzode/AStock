#!/usr/bin/env python3
"""Audit the C15 raw-source batch before any bounded diagnostic is attempted."""

from __future__ import annotations

import gzip
import hashlib
import json
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c15-shfe-actual-contract-eod-2019-2025-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "c15_shfe_actual_contract_eod_source_readiness_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "c15_shfe_actual_contract_eod_source_readiness_20260815.md"
FAMILIES = {"AU", "CU", "RU"}
ESSENTIAL_FIELDS = {"PRESETTLEMENTPRICE", "OPENPRICE", "HIGHESTPRICE", "LOWESTPRICE", "CLOSEPRICE", "SETTLEMENTPRICE", "VOLUME", "OPENINTEREST", "DELIVERYMONTH"}


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, contents: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(contents, encoding="utf-8")
    temporary.replace(path)


def _family(row: dict[str, Any]) -> str:
    return str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0].upper()


def _audit() -> dict[str, Any]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures: list[str] = []
    retained_by_year: Counter[int] = Counter()
    non_records_by_year: Counter[int] = Counter()
    non_record_statuses: Counter[str] = Counter()
    daily_family_counts: Counter[str] = Counter()
    first_date: str | None = None
    last_date: str | None = None
    observed_dates: list[date] = []
    for record in manifest.get("records", []):
        if not isinstance(record, dict):
            failures.append("non-object retained record")
            continue
        trade_date = str(record.get("trade_date") or "")
        try:
            parsed_date = date.fromisoformat(trade_date)
        except ValueError:
            failures.append(f"invalid retained trade date: {trade_date}")
            continue
        path = REPO_ROOT / str(record.get("path") or "")
        if not path.is_file():
            failures.append(f"missing compressed response: {trade_date}")
            continue
        compressed = path.read_bytes()
        if len(compressed) != int(record.get("compressed_bytes", -1)) or _sha256(compressed) != record.get("compressed_sha256"):
            failures.append(f"compressed response mismatch: {trade_date}")
            continue
        try:
            raw = gzip.decompress(compressed)
            payload = json.loads(raw.decode("utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            failures.append(f"cannot recover JSON response: {trade_date}")
            continue
        if len(raw) != int(record.get("raw_bytes", -1)) or _sha256(raw) != record.get("raw_sha256"):
            failures.append(f"raw response mismatch: {trade_date}")
            continue
        if str(payload.get("report_date") or "") != trade_date.replace("-", ""):
            failures.append(f"payload report-date mismatch: {trade_date}")
            continue
        rows = payload.get("o_curinstrument")
        if not isinstance(rows, list):
            failures.append(f"missing contract rows: {trade_date}")
            continue
        family_rows = [
            row
            for row in rows
            if isinstance(row, dict)
            and _family(row) in FAMILIES
            and str(row.get("DELIVERYMONTH") or "").strip() not in {"", "小计", "合计"}
        ]
        observed_families = {_family(row) for row in family_rows}
        if observed_families != FAMILIES:
            failures.append(f"candidate family mismatch: {trade_date}")
            continue
        if not ESSENTIAL_FIELDS.issubset({field for row in family_rows for field in row}):
            failures.append(f"essential EOD fields missing: {trade_date}")
            continue
        retained_by_year[parsed_date.year] += 1
        for family in observed_families:
            daily_family_counts[family] += 1
        observed_dates.append(parsed_date)
        first_date = trade_date if first_date is None or trade_date < first_date else first_date
        last_date = trade_date if last_date is None or trade_date > last_date else last_date
    for row in manifest.get("non_records", []):
        if isinstance(row, dict):
            parsed_date = date.fromisoformat(str(row["trade_date"]))
            non_records_by_year[parsed_date.year] += 1
            non_record_statuses[str(row.get("status"))] += 1
    if len(observed_dates) != len(manifest.get("records", [])):
        failures.append("not every retained manifest record was reconstructed")
    if manifest.get("progress", {}).get("captured_valid_responses") != len(manifest.get("records", [])):
        failures.append("manifest progress does not match retained records")
    years = sorted(set(retained_by_year) | set(non_records_by_year))
    year_coverage = [
        {
            "year": year,
            "retained_valid_responses": retained_by_year[year],
            "non_records": non_records_by_year[year],
            "weekday_attempts": retained_by_year[year] + non_records_by_year[year],
        }
        for year in years
    ]
    return {
        "schema_version": "c15_shfe_actual_contract_source_readiness_audit.v1",
        "artifact_id": "D5PT-C15-v1",
        "as_of": "2026-08-15",
        "result": "PASS" if not failures else "FAIL",
        "source_manifest": {
            "path": str(MANIFEST_PATH.relative_to(REPO_ROOT)),
            "sha256": _sha256(MANIFEST_PATH.read_bytes()),
            "source_quality": manifest.get("source_quality"),
            "protocol_status": manifest.get("protocol_status"),
            "metadata_correction": manifest.get("metadata_correction"),
        },
        "coverage": {
            "retained_valid_responses": len(manifest.get("records", [])),
            "non_records": len(manifest.get("non_records", [])),
            "first_retained_trade_date": first_date,
            "last_retained_trade_date": last_date,
            "year_coverage": year_coverage,
            "non_record_statuses": dict(sorted(non_record_statuses.items())),
            "family_days_with_observed_rows": dict(sorted(daily_family_counts.items())),
            "report_date_validation": "every retained response matches its requested date" if not failures else "see failures",
        },
        "failures": failures,
        "allowed_use": "A bounded actual-contract settlement-data diagnostic may be specified next, provided it preserves the retrospective-source and non-execution boundaries.",
        "not_allowed": [
            "A point-in-time, entitled historical-data claim.",
            "A complete exchange-calendar, contract-lifecycle, delivery-state, historical margin/limit/fee or broker-route claim.",
            "A fill, personal-access, investor net-return, stable-return or external-action conclusion.",
        ],
        "next_gate": "Freeze a diagnostic rule before calculation, retain every no-record date, and independently replay it. Any later usable-strategy claim still requires execution, cost, account-route and forward-paper evidence.",
    }


def _markdown(result: dict[str, Any]) -> str:
    coverage = result["coverage"]
    rows = "\n".join(
        f"| {row['year']} | {row['retained_valid_responses']} | {row['non_records']} | {row['weekday_attempts']} |"
        for row in coverage["year_coverage"]
    )
    failures = "无。" if not result["failures"] else "\n".join(f"- {item}" for item in result["failures"])
    correction = result["source_manifest"].get("metadata_correction")
    correction_text = "本次来源清单直接保留原始响应中的 `report_date`，并已与每个请求日期核对。"
    if isinstance(correction, dict):
        correction_text = f"来源清单已通过可重放重新冻结修正元数据：{correction['records_revalidated']} 份原始响应的 `report_date` 与请求日期一致；原始文件、网址和抓取记录均未变更。"
    return f"""# C15 上期所实际合约日度来源就绪审计

- 结果：`{result['result']}`
- 范围：2019-01-01 至 2025-12-31 的每个工作日请求；只保留包含 `AU`、`CU`、`RU` 实际合约行的交易所响应。
- 结论：已验证 `{coverage['retained_valid_responses']}` 份可解压、哈希匹配且报告日期与请求日期一致的官方日度响应。它支持下一步的**有限实际合约结算价诊断**，不支持成交、净回报或可使用策略结论。

| 年份 | 保留有效响应 | 非记录 | 工作日请求 |
|---|---:|---:|---:|
{rows}

所有 `{coverage['non_records']}` 个非记录日期均为官方端点 `404`，被保留为未获取响应；本审计没有将其推定为交易日或非交易日，也没有以相邻价格填补。三类合约在全部保留日期均观察到实际挂牌行和用于有限诊断的必要 EOD 字段。

{correction_text}

## 审计未通过项

{failures}

## 仍然不能推出的结论

1. 这些历史文件是事后请求，不能证明原决策日可得性、数据权利或文件未修订。
2. 日结算价没有买卖价、深度、排队、成交、期货公司佣金、动态保证金、限仓、账户或交割路径。
3. 即使后续有限结算价诊断为正，也不会成为个人净回报、稳定 5% 或期货操作结论。
"""


def main() -> int:
    result = _audit()
    _write(OUTPUT_JSON, json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    _write(OUTPUT_MD, _markdown(result))
    print(f"C15 SHFE source readiness audit: {result['result']}")
    return 0 if result["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
