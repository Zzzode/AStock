"""Content-addressed archives for public market-observation packets.

Public observations can be frozen and replayed exactly, but they do not become
licensed, execution-grade market data merely because their bytes are archived.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PUBLIC_OBSERVATION_SOURCE = "akshare_public"


@dataclass(frozen=True)
class PublicMarketObservationPacket:
    """One frozen public observation and its explicit research boundary."""

    observed_at: str
    archive_id: str
    raw_source_records: dict[str, Any]
    subject: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "public_market_observation.v1",
            "source_manifest": {
                "schema_version": "public_market_observation_sources.v1",
                "source": PUBLIC_OBSERVATION_SOURCE,
                "as_of": self.observed_at,
                "archive_id": self.archive_id,
                "subject": self.subject,
                "data_class": "public_observation",
            },
            "limitations": [
                "The archive proves the exact public observation packet used by the desk, not vendor authorization or exchange-grade completeness.",
                "It is eligible for observation replay and decision audit only; it is not a complete portfolio-backtest source manifest.",
            ],
        }

    def write_frozen_archive(self, directory: Path) -> Path:
        """Persist raw public records by content hash without mutable overwrite."""
        digest = self.archive_id.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("public observation archive_id must be a sha256 digest")
        payload = {
            "schema_version": "market_data_frozen_archive.v1",
            "source": PUBLIC_OBSERVATION_SOURCE,
            "archive_id": self.archive_id,
            "raw_source_records": self.raw_source_records,
        }
        if _content_hash(_archive_hash_input(payload)) != digest:
            raise ValueError("public observation archive_id does not match raw source records")
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


def build_public_market_observation_packet(
    *,
    subject: str,
    observation: Mapping[str, Any],
    observed_at: str | datetime | None = None,
) -> PublicMarketObservationPacket:
    """Bind a source-labelled public observation packet to immutable bytes."""
    normalized_subject = str(subject).strip()
    if not normalized_subject:
        raise ValueError("public observation subject is required")
    if not isinstance(observation, Mapping) or not observation:
        raise ValueError("public observation requires a nonempty mapping")
    timestamp = _normalize_timestamp(observed_at or observation.get("observed_at"))
    raw_records = {normalized_subject: dict(observation)}
    archive_id = "sha256:" + _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": PUBLIC_OBSERVATION_SOURCE,
            "raw_source_records": raw_records,
        }
    )
    return PublicMarketObservationPacket(
        observed_at=timestamp,
        archive_id=archive_id,
        raw_source_records=raw_records,
        subject=normalized_subject,
    )


def _normalize_timestamp(value: str | datetime | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(value, datetime):
        timestamp = value
    else:
        try:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("public observation observed_at must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError("public observation observed_at must include a timezone")
    return timestamp.astimezone(timezone.utc).isoformat()


def _archive_hash_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "market_data_frozen_archive.v1",
        "source": str(payload["source"]),
        "raw_source_records": payload["raw_source_records"],
    }


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
