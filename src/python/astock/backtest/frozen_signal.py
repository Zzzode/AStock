"""Immutable daily-bar inputs for deterministic single-name signal replays."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class FrozenSignalReplayInput:
    """A content-addressed daily-bar input, not an execution-grade data set."""

    code: str
    market_data: pd.DataFrame
    source: str
    observed_at: str
    archive_id: str
    raw_source_records: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "frozen_signal_replay_input.v1",
            "code": self.code,
            "market_data": _records(self.market_data),
            "source_manifest": {
                "schema_version": "frozen_signal_replay_sources.v1",
                "source": self.source,
                "as_of": self.observed_at,
                "archive_id": self.archive_id,
                "domains": {"eod_bars": self.source},
                "data_class": "frozen_daily_signal_input",
            },
            "price_basis": "unknown",
            "limitations": [
                "The archive freezes exact EOD bars for deterministic signal replay only.",
                "It does not establish point-in-time universe, halts, price limits, corporate actions, delistings, or capacity coverage.",
            ],
        }

    def write_frozen_archive(self, directory: Path) -> Path:
        """Write the exact raw replay input under its content hash."""
        digest = self.archive_id.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("frozen signal replay archive_id must be a sha256 digest")
        payload = {
            "schema_version": "market_data_frozen_archive.v1",
            "source": self.source,
            "archive_id": self.archive_id,
            "raw_source_records": self.raw_source_records,
        }
        if _content_hash(_archive_hash_input(payload)) != digest:
            raise ValueError("frozen signal replay archive_id does not match raw source records")
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
        )
        target_directory = Path(directory)
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / f"{digest}.json"
        if target.exists():
            if target.read_text(encoding="utf-8") != canonical:
                raise ValueError(f"frozen archive collision at {target}")
            return target
        temporary = target_directory / f".{digest}.tmp"
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(target)
        return target

    def write_replay_input(self, directory: Path) -> Path:
        """Persist the manifest that binds a replay command to its archive."""
        digest = self.archive_id.removeprefix("sha256:")
        target_directory = Path(directory)
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / f"{digest}.replay.json"
        canonical = json.dumps(
            self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
        )
        if target.exists():
            if target.read_text(encoding="utf-8") != canonical:
                raise ValueError(f"frozen replay-input collision at {target}")
            return target
        temporary = target_directory / f".{digest}.replay.tmp"
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(target)
        return target


def build_frozen_signal_replay_input(
    code: str,
    market_data: pd.DataFrame,
    *,
    source: str,
    observed_at: str | datetime | None = None,
) -> FrozenSignalReplayInput:
    """Normalize and bind exact daily bars before a deterministic replay."""
    normalized_code = str(code).strip()
    if not normalized_code:
        raise ValueError("frozen signal replay code is required")
    normalized_source = str(source).strip()
    if not normalized_source:
        raise ValueError("frozen signal replay source is required")
    frame = _normalize_daily_bars(market_data)
    timestamp = _normalize_timestamp(observed_at)
    raw_records = {
        "signal_replay": {
            "code": normalized_code,
            "observed_at": timestamp,
            "market_data": _records(frame),
        }
    }
    archive_id = "sha256:" + _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": normalized_source,
            "raw_source_records": raw_records,
        }
    )
    return FrozenSignalReplayInput(
        code=normalized_code,
        market_data=frame,
        source=normalized_source,
        observed_at=timestamp,
        archive_id=archive_id,
        raw_source_records=raw_records,
    )


def parse_frozen_signal_replay_input(value: Mapping[str, Any]) -> FrozenSignalReplayInput:
    """Validate an agent-safe frozen-input payload before signal replay."""
    if str(value.get("schema_version") or "") != "frozen_signal_replay_input.v1":
        raise ValueError("signal replay input must use frozen_signal_replay_input.v1")
    manifest = value.get("source_manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("signal replay input requires a source_manifest")
    if str(manifest.get("schema_version") or "") != "frozen_signal_replay_sources.v1":
        raise ValueError("signal replay input has an unsupported source manifest")
    code = str(value.get("code") or "").strip()
    source = str(manifest.get("source") or "").strip()
    archive_id = str(manifest.get("archive_id") or "").strip()
    observed_at = _normalize_timestamp(manifest.get("as_of"))
    raw_market_data = value.get("market_data")
    if not isinstance(raw_market_data, list):
        raise ValueError("signal replay input market_data must be a record list")
    packet = build_frozen_signal_replay_input(
        code,
        pd.DataFrame(raw_market_data),
        source=source,
        observed_at=observed_at,
    )
    if not archive_id:
        raise ValueError("signal replay input source manifest requires archive_id")
    if archive_id != packet.archive_id:
        raise ValueError("signal replay input archive_id does not match exact market_data")
    return packet


def _normalize_daily_bars(frame: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("signal replay market_data must be a DataFrame")
    required = {"date", "open", "high", "low", "close", "volume"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError("signal replay market_data lacks: " + ", ".join(missing))
    normalized = frame.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    if normalized["date"].isna().any():
        raise ValueError("signal replay market_data contains invalid dates")
    if normalized["date"].duplicated().any():
        raise ValueError("signal replay market_data contains duplicate dates")
    for column in ("open", "high", "low", "close", "volume"):
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    if normalized[["open", "high", "low", "close", "volume"]].isna().any().any():
        raise ValueError("signal replay market_data contains non-numeric OHLCV")
    if (normalized[["open", "high", "low", "close"]] <= 0).any().any():
        raise ValueError("signal replay market_data contains non-positive prices")
    if (normalized["volume"] < 0).any():
        raise ValueError("signal replay market_data contains negative volume")
    return normalized.sort_values("date", kind="stable").reset_index(drop=True)


def _normalize_timestamp(value: str | datetime | None) -> str:
    if value is None:
        timestamp = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        timestamp = value
    else:
        try:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("signal replay observed_at must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError("signal replay observed_at must include a timezone")
    return timestamp.astimezone(timezone.utc).isoformat()


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _archive_hash_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "market_data_frozen_archive.v1",
        "source": str(payload["source"]),
        "raw_source_records": payload["raw_source_records"],
    }


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
