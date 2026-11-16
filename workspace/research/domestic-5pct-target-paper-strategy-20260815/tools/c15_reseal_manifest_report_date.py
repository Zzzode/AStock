#!/usr/bin/env python3
"""Correct C15 source metadata by rebuilding it from immutable raw responses.

The former manifest recorded a static UI field as a date-like value.  This
utility preserves a hash-bound pre-correction snapshot, verifies every gzip
payload and raw hash, then replaces that field with each response's real
``report_date``.  It never changes a raw response, URL, retrieval record or
source hash.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
SOURCE_DIR = CASE_DIR / "sources" / "c15-shfe-actual-contract-eod-2019-2025-20260815"
MANIFEST_PATH = SOURCE_DIR / "manifest.json"
PRE_CORRECTION_PATH = SOURCE_DIR / "manifest_v1_pre_metadata_correction.json"


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write(path: Path, raw: bytes) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(raw)
    temporary.replace(path)


def main() -> int:
    original = MANIFEST_PATH.read_bytes()
    manifest = json.loads(original)
    if manifest.get("metadata_correction", {}).get("status") == "completed":
        print("C15 manifest reseal: already completed")
        return 0
    if PRE_CORRECTION_PATH.exists():
        raise RuntimeError(f"pre-correction snapshot already exists: {PRE_CORRECTION_PATH}")
    _write(PRE_CORRECTION_PATH, original)
    corrected = 0
    for record in manifest.get("records", []):
        raw_path = REPO_ROOT / str(record["path"])
        compressed = raw_path.read_bytes()
        if len(compressed) != int(record["compressed_bytes"]) or _sha256(compressed) != record["compressed_sha256"]:
            raise ValueError(f"compressed source mismatch: {record['trade_date']}")
        raw = gzip.decompress(compressed)
        if len(raw) != int(record["raw_bytes"]) or _sha256(raw) != record["raw_sha256"]:
            raise ValueError(f"raw source mismatch: {record['trade_date']}")
        payload = json.loads(raw.decode("utf-8"))
        report_date = str(payload.get("report_date") or "")
        expected = str(record["trade_date"]).replace("-", "")
        if report_date != expected:
            raise ValueError(f"report-date mismatch: {record['trade_date']} {report_date}")
        record.pop("payload_date_field", None)
        record["payload_report_date"] = report_date
        corrected += 1
    manifest["schema_version"] = "c15_shfe_actual_contract_eod_source_manifest.v2"
    manifest["metadata_correction"] = {
        "status": "completed",
        "corrected_at": datetime.now(timezone.utc).isoformat(),
        "reason": "A static response UI field was previously recorded as a date-like field. The manifest now records the raw response report_date, which matches each requested trade_date.",
        "previous_manifest_path": str(PRE_CORRECTION_PATH.relative_to(REPO_ROOT)),
        "previous_manifest_sha256": _sha256(original),
        "raw_response_files_changed": False,
        "urls_changed": False,
        "retrieval_records_changed": False,
        "records_revalidated": corrected,
    }
    _write(MANIFEST_PATH, (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    print(f"C15 manifest reseal: corrected {corrected} records; new sha256={_sha256(MANIFEST_PATH.read_bytes())}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
