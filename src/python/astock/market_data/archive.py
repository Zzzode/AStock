"""Verification for content-addressed frozen market-data archives."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping


def verify_frozen_market_archive(
    path: str | Path | None,
    *,
    expected_archive_id: str | None = None,
    expected_source: str | None = None,
) -> dict[str, Any]:
    """Verify that a local archive exists and matches its raw-record hash.

    A declared archive ID is useful provenance, but it is not reproducibility
    evidence until the immutable bytes can be loaded and recomputed.
    """
    if path is None or not str(path).strip():
        return _blocked("A frozen market-data archive path is required for a reproducibility claim.")
    archive_path = Path(path)
    if not archive_path.is_file():
        return _blocked(f"Frozen market-data archive does not exist: {archive_path}")
    try:
        payload = json.loads(archive_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return _blocked(f"Frozen market-data archive cannot be parsed: {error}")
    if not isinstance(payload, Mapping):
        return _blocked("Frozen market-data archive must be a JSON object.")
    if payload.get("schema_version") != "market_data_frozen_archive.v1":
        return _blocked("Frozen market-data archive has an unsupported schema_version.")
    source = str(payload.get("source") or "").strip()
    archive_id = str(payload.get("archive_id") or "").strip()
    raw_records = payload.get("raw_source_records")
    if not source or not archive_id or not isinstance(raw_records, Mapping):
        return _blocked("Frozen market-data archive requires source, archive_id, and raw_source_records.")
    if expected_archive_id and archive_id != expected_archive_id:
        return _blocked("Frozen market-data archive ID does not match the supplied source manifest.")
    if expected_source and source != expected_source:
        return _blocked("Frozen market-data archive source does not match the supplied source manifest.")
    digest = archive_id.removeprefix("sha256:")
    if len(digest) != 64:
        return _blocked("Frozen market-data archive_id must be a sha256 digest.")
    computed = _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": source,
            "raw_source_records": raw_records,
        }
    )
    if computed != digest:
        return _blocked("Frozen market-data archive raw records do not match archive_id.")
    return {
        "status": "pass",
        "archive_path": str(archive_path),
        "archive_id": archive_id,
        "source": source,
        "failures": [],
    }


def _blocked(failure: str) -> dict[str, Any]:
    return {"status": "blocked", "failures": [failure]}


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
