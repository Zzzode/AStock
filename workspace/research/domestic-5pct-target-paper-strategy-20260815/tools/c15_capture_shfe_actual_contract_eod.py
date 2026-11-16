#!/usr/bin/env python3
"""Capture a bounded, hash-controlled SHFE actual-contract EOD research set.

This is deliberately a source-coverage project, not a futures backtest.  It
retrieves historical daily files after the fact, so it labels every retained
record as retrospective source access.  Raw exchange response bytes are kept
losslessly in gzip files and verified against their uncompressed SHA-256 hash.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c15-shfe-actual-contract-eod-2019-2025-20260815"
RAW_DIR = SOURCE_DIR / "daily"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
ATTEMPTS_PATH = SOURCE_DIR / "attempts.jsonl"
FAMILIES = ("AU", "CU", "RU")
START = date(2019, 1, 1)
END = date(2025, 12, 31)
PAUSE_SECONDS = 0.12
MAX_RETRIES = 3


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def _atomic_write_bytes(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def _atomic_write_json(path: Path, payload: object) -> None:
    _atomic_write_bytes(path, (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))


def _weekday_dates(start: date, end: date) -> list[date]:
    days: list[date] = []
    cursor = start
    while cursor <= end:
        if cursor.weekday() < 5:
            days.append(cursor)
        cursor += timedelta(days=1)
    return days


def _url(day: date) -> str:
    return f"https://www.shfe.cn/data/tradedata/future/dailydata/kx{day:%Y%m%d}.dat"


def _fetch(url: str) -> tuple[bytes | None, str | None]:
    last_error: str | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            request = Request(url, headers={"User-Agent": "AStock research source capture/1.0"})
            with urlopen(request, timeout=30) as response:
                raw = response.read()
            if b"safeline_bot_challenge" in raw or b"WEB \xe5\xba\x94\xe7\x94\xa8\xe9\x98\xb2\xe7\x81\xab\xe5\xa2\x99" in raw:
                return None, "refused_waf_challenge_body"
            return raw, None
        except HTTPError as error:
            last_error = f"http_{error.code}"
            if error.code in {400, 404}:
                break
        except (URLError, TimeoutError, OSError) as error:
            last_error = f"transport_{type(error).__name__}"
        if attempt < MAX_RETRIES:
            time.sleep(0.5 * attempt)
    return None, last_error or "unknown_fetch_failure"


def _family(row: dict[str, object]) -> str:
    value = str(row.get("PRODUCTGROUPID") or row.get("PRODUCTID") or "").strip().split("_")[0]
    return value.upper()


def _valid_payload(raw: bytes) -> tuple[dict[str, object] | None, str | None, int]:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "not_json", 0
    if not isinstance(payload, dict):
        return None, "not_object", 0
    rows = payload.get("o_curinstrument")
    if not isinstance(rows, list):
        return None, "missing_contract_rows", 0
    family_rows = [
        row
        for row in rows
        if isinstance(row, dict)
        and _family(row) in FAMILIES
        and str(row.get("DELIVERYMONTH") or "").strip() not in {"", "小计", "合计"}
    ]
    observed = {_family(row) for row in family_rows}
    if observed != set(FAMILIES):
        return None, "missing_candidate_family_rows", len(family_rows)
    essential = {"PRESETTLEMENTPRICE", "OPENPRICE", "HIGHESTPRICE", "LOWESTPRICE", "CLOSEPRICE", "SETTLEMENTPRICE", "VOLUME", "OPENINTEREST", "DELIVERYMONTH"}
    observed_fields = {key for row in family_rows for key in row}
    if not essential.issubset(observed_fields):
        return None, "missing_essential_eod_fields", len(family_rows)
    return payload, None, len(family_rows)


def _load_manifest() -> dict[str, object]:
    if not MANIFEST_PATH.is_file():
        return {
            "schema_version": "c15_shfe_actual_contract_eod_source_manifest.v1",
            "capture_batch": "c15-shfe-actual-contract-eod-2019-2025-20260815",
            "case_id": CASE_DIR.name,
            "source_quality": "primary_official_retrospective_actual_contract_eod_observation",
            "protocol_status": "in_progress_source_coverage_only_not_backtest",
            "scope": {
                "families": list(FAMILIES),
                "attempted_weekday_start": START.isoformat(),
                "attempted_weekday_end": END.isoformat(),
                "source_url_pattern": "https://www.shfe.cn/data/tradedata/future/dailydata/kxYYYYMMDD.dat",
            },
            "records": [],
            "non_records": [],
            "limitations": [
                "Every historical response is requested retrospectively; present retrieval does not establish original-date availability, immutability, revision history or data rights.",
                "The retained EOD responses do not supply bid/ask, depth, fill, broker commission, broker margin, position limit, account access, actual settlement route, delivery eligibility or investor return.",
                "This capture does not construct a continuous series, performance result, allocation, position or external action.",
            ],
        }
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _append_attempt(record: dict[str, object]) -> None:
    with ATTEMPTS_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _run() -> int:
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    manifest = _load_manifest()
    existing_records = {str(row["trade_date"]): row for row in manifest.get("records", []) if isinstance(row, dict) and row.get("trade_date")}
    existing_non_records = {str(row["trade_date"]): row for row in manifest.get("non_records", []) if isinstance(row, dict) and row.get("trade_date")}
    captured_at = datetime.now(timezone.utc).isoformat()
    weekdays = _weekday_dates(START, END)
    todo = [day for day in weekdays if day.isoformat() not in existing_records and day.isoformat() not in existing_non_records]
    for index, day in enumerate(todo, start=1):
        trade_date = day.isoformat()
        url = _url(day)
        raw, fetch_error = _fetch(url)
        attempt: dict[str, object] = {"trade_date": trade_date, "url": url, "attempted_at": datetime.now(timezone.utc).isoformat()}
        if raw is None:
            attempt["status"] = fetch_error or "fetch_failure"
            manifest["non_records"].append({**attempt, "classification": "no_valid_candidate_eod_response"})
            _append_attempt(attempt)
        else:
            payload, payload_error, family_rows = _valid_payload(raw)
            if payload is not None and str(payload.get("report_date") or "") != day.strftime("%Y%m%d"):
                payload, payload_error = None, "payload_report_date_mismatch"
            if payload is None:
                attempt.update({"status": payload_error or "invalid_payload", "raw_sha256": _sha256(raw), "raw_bytes": len(raw), "candidate_family_rows": family_rows})
                manifest["non_records"].append({**attempt, "classification": "no_valid_candidate_eod_response"})
                _append_attempt(attempt)
            else:
                raw_path = RAW_DIR / f"shfe_actual_contract_daily_{day:%Y%m%d}.json.gz"
                compressed = gzip.compress(raw, compresslevel=9, mtime=0)
                _atomic_write_bytes(raw_path, compressed)
                record = {
                    "trade_date": trade_date,
                    "url": url,
                    "retrieved_at": captured_at,
                    "retrieval_basis": "retrospective_source_access",
                    "path": _repo_path(raw_path),
                    "raw_bytes": len(raw),
                    "raw_sha256": _sha256(raw),
                    "compressed_bytes": len(compressed),
                    "compressed_sha256": _sha256(compressed),
                    "candidate_family_rows": family_rows,
                    "candidate_families": list(FAMILIES),
                    "payload_report_date": payload.get("report_date"),
                    "capture_note": "Losslessly compressed first-party EOD response retained after the fact. It proves a currently accessible historical source response and observed actual-contract fields, not original-date availability, data rights, fill, broker route, investor result or external action.",
                }
                manifest["records"].append(record)
                attempt.update({"status": "captured", "raw_sha256": record["raw_sha256"], "candidate_family_rows": family_rows})
                _append_attempt(attempt)
        if index % 25 == 0 or index == len(todo):
            manifest["records"].sort(key=lambda row: str(row["trade_date"]))
            manifest["non_records"].sort(key=lambda row: str(row["trade_date"]))
            manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
            manifest["progress"] = {"weekday_dates_total": len(weekdays), "attempted_or_resumed": len(existing_records) + len(existing_non_records) + index, "captured_valid_responses": len(manifest["records"]), "non_records": len(manifest["non_records"])}
            _atomic_write_json(MANIFEST_PATH, manifest)
            print(f"C15 progress {index}/{len(todo)}: captured={len(manifest['records'])} non_records={len(manifest['non_records'])}", flush=True)
        time.sleep(PAUSE_SECONDS)
    manifest["records"].sort(key=lambda row: str(row["trade_date"]))
    manifest["non_records"].sort(key=lambda row: str(row["trade_date"]))
    manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
    manifest["protocol_status"] = "retrospective_source_coverage_complete_not_backtest"
    manifest["progress"] = {"weekday_dates_total": len(weekdays), "attempted_or_resumed": len(weekdays), "captured_valid_responses": len(manifest["records"]), "non_records": len(manifest["non_records"])}
    _atomic_write_json(MANIFEST_PATH, manifest)
    print(f"C15 complete: captured={len(manifest['records'])} non_records={len(manifest['non_records'])}")
    return 0


def _verify() -> int:
    manifest = _load_manifest()
    failures: list[str] = []
    seen: set[str] = set()
    for row in manifest.get("records", []):
        if not isinstance(row, dict):
            failures.append("invalid manifest record")
            continue
        trade_date = str(row.get("trade_date"))
        if trade_date in seen:
            failures.append(f"duplicate date: {trade_date}")
        seen.add(trade_date)
        path = REPO_ROOT / str(row.get("path"))
        if not path.is_file():
            failures.append(f"missing raw file: {trade_date}")
            continue
        compressed = path.read_bytes()
        if len(compressed) != int(row.get("compressed_bytes", -1)) or _sha256(compressed) != row.get("compressed_sha256"):
            failures.append(f"compressed hash mismatch: {trade_date}")
            continue
        try:
            raw = gzip.decompress(compressed)
        except OSError:
            failures.append(f"cannot decompress: {trade_date}")
            continue
        if len(raw) != int(row.get("raw_bytes", -1)) or _sha256(raw) != row.get("raw_sha256"):
            failures.append(f"raw hash mismatch: {trade_date}")
            continue
        payload, error, family_rows = _valid_payload(raw)
        if error is not None or family_rows != int(row.get("candidate_family_rows", -1)):
            failures.append(f"payload validation mismatch: {trade_date}")
        elif payload is None or str(payload.get("report_date") or "") != trade_date.replace("-", ""):
            failures.append(f"payload report-date mismatch: {trade_date}")
    completion = manifest.get("progress", {})
    if completion.get("captured_valid_responses") != len(manifest.get("records", [])):
        failures.append("progress count differs from records")
    state = "PASS" if not failures else "FAIL"
    print(f"C15 SHFE SOURCE COVERAGE: {state} ({len(manifest.get('records', []))} retained daily responses)")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-only", action="store_true")
    arguments = parser.parse_args()
    return _verify() if arguments.verify_only else _run()


if __name__ == "__main__":
    raise SystemExit(main())
