"""Immutable operating records for the public-data market observation desk.

These records make a daily observation reproducible as an exact research
artifact. They do not upgrade public data into formal-decision data and never
carry an order or a paper-plan release.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from ..market_data import verify_frozen_market_archive


@dataclass(frozen=True)
class PublicDeskObservationRun:
    """One content-addressed, observation-only market-desk operating record."""

    archive_id: str
    observed_at: str
    market_overview: dict[str, Any]
    rotation_observation: dict[str, Any]
    operational_readiness: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-public-observation-run.v1",
            "archive_id": self.archive_id,
            "observed_at": self.observed_at,
            "operation": "record_observation_only",
            "market_overview": self.market_overview,
            "rotation_observation": self.rotation_observation,
            "operational_readiness": self.operational_readiness,
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
            "limitations": [
                "This record is a public-data observation artifact, not a formal investment-committee decision or active paper-plan release.",
                "The frozen rotation archive proves the exact public rotation packet; the embedded market overview retains its own source and quality metadata.",
            ],
        }

    def write(self, directory: Path) -> Path:
        """Write an immutable content-addressed operating record."""
        payload = self.to_dict()
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
        )
        digest = self.archive_id.removeprefix("sha256:")
        if len(digest) != 64 or _sha256(_hash_input(payload)) != digest:
            raise ValueError("public desk observation archive_id does not match its record")
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        destination = directory / f"{digest}.json"
        if destination.exists():
            if destination.read_text(encoding="utf-8") != canonical:
                raise ValueError(f"public desk observation archive collision at {destination}")
            return destination
        temporary = directory / f".{digest}.tmp"
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(destination)
        return destination


@dataclass(frozen=True)
class PublicDeskObservationExceptionReview:
    """Immutable human review of duplicate valid public desk observations."""

    review_id: str
    session_date: str
    archive_ids: tuple[str, ...]
    canonical_archive_id: str
    reviewer: str
    reason: str
    evidence_refs: tuple[str, ...]
    reviewed_at: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "market-desk-public-observation-exception-review.v1",
            "review_id": self.review_id,
            "session_date": self.session_date,
            "archive_ids": list(self.archive_ids),
            "canonical_archive_id": self.canonical_archive_id,
            "reviewer": self.reviewer,
            "reason": self.reason,
            "evidence_refs": list(self.evidence_refs),
            "reviewed_at": self.reviewed_at,
            "research_only": True,
            "no_order_execution": True,
        }

    def write(self, directory: str | Path) -> Path:
        payload = self.to_dict()
        canonical = json.dumps(
            payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
        )
        digest = self.review_id.removeprefix("sha256:")
        if len(digest) != 64 or _sha256(_exception_hash_input(payload)) != digest:
            raise ValueError("public desk observation exception review_id does not match its record")
        target_directory = Path(directory)
        target_directory.mkdir(parents=True, exist_ok=True)
        destination = target_directory / f"{digest}.json"
        if destination.exists():
            if destination.read_text(encoding="utf-8") != canonical:
                raise ValueError(f"public desk observation exception review collision at {destination}")
            return destination
        temporary = target_directory / f".{digest}.tmp"
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(destination)
        return destination


def build_public_desk_observation_run(
    *,
    market_overview: Mapping[str, Any],
    rotation_observation: Mapping[str, Any],
    operational_readiness: Mapping[str, Any],
) -> PublicDeskObservationRun:
    """Bind one daily desk record to its captured public-data evidence."""
    overview = dict(market_overview)
    rotation = dict(rotation_observation)
    readiness = dict(operational_readiness)
    snapshot = overview.get("snapshot")
    observed_at = str(snapshot.get("observed_at") if isinstance(snapshot, Mapping) else "").strip()
    if not observed_at:
        raise ValueError("market overview must include snapshot.observed_at")
    manifest = rotation.get("source_manifest")
    if not isinstance(manifest, Mapping) or not str(manifest.get("archive_id") or "").strip():
        raise ValueError("rotation observation must include a frozen source manifest")
    record = {
        "schema_version": "market-desk-public-observation-run.v1",
        "observed_at": observed_at,
        "market_overview": overview,
        "rotation_observation": rotation,
        "operational_readiness": readiness,
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }
    return PublicDeskObservationRun(
        archive_id="sha256:" + _sha256(record),
        observed_at=observed_at,
        market_overview=overview,
        rotation_observation=rotation,
        operational_readiness=readiness,
    )


def create_public_desk_observation_exception_review(
    *,
    session_date: str,
    archive_ids: list[str] | tuple[str, ...],
    canonical_archive_id: str,
    reviewer: str,
    reason: str,
    evidence_refs: list[str] | tuple[str, ...],
    reviewed_at: str | datetime | None = None,
) -> PublicDeskObservationExceptionReview:
    """Create a review that resolves one exact set of duplicate valid runs."""
    try:
        normalized_date = date.fromisoformat(session_date).isoformat()
    except ValueError as error:
        raise ValueError("session_date must be an ISO-8601 calendar date") from error
    normalized_ids = tuple(sorted({str(value).strip() for value in archive_ids if str(value).strip()}))
    canonical_id = str(canonical_archive_id).strip()
    if len(normalized_ids) < 2:
        raise ValueError("exception review requires at least two duplicate archive_ids")
    if canonical_id not in normalized_ids:
        raise ValueError("canonical_archive_id must be one of archive_ids")
    normalized_reviewer = str(reviewer).strip()
    normalized_reason = str(reason).strip()
    normalized_refs = tuple(str(value).strip() for value in evidence_refs if str(value).strip())
    if not normalized_reviewer or not normalized_reason or not normalized_refs:
        raise ValueError("exception review requires reviewer, reason, and at least one evidence reference")
    timestamp = _normalize_review_timestamp(reviewed_at)
    record = {
        "schema_version": "market-desk-public-observation-exception-review.v1",
        "session_date": normalized_date,
        "archive_ids": list(normalized_ids),
        "canonical_archive_id": canonical_id,
        "reviewer": normalized_reviewer,
        "reason": normalized_reason,
        "evidence_refs": list(normalized_refs),
        "reviewed_at": timestamp,
        "research_only": True,
        "no_order_execution": True,
    }
    return PublicDeskObservationExceptionReview(
        review_id="sha256:" + _sha256(record),
        session_date=normalized_date,
        archive_ids=normalized_ids,
        canonical_archive_id=canonical_id,
        reviewer=normalized_reviewer,
        reason=normalized_reason,
        evidence_refs=normalized_refs,
        reviewed_at=timestamp,
    )


def verify_public_desk_observation_run(path: str | Path) -> dict[str, Any]:
    """Verify a desk-run record and its linked frozen rotation evidence."""
    source_path = Path(path)
    if not source_path.is_file():
        return _blocked(f"Public desk observation record does not exist: {source_path}")
    try:
        payload = json.loads(source_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return _blocked(f"Public desk observation record cannot be parsed: {error}")
    if not isinstance(payload, Mapping):
        return _blocked("Public desk observation record must be a JSON object.")
    declared_observed_at = payload.get("observed_at")
    if not isinstance(declared_observed_at, str) or len(declared_observed_at) < 10:
        declared_observed_at = None
    if payload.get("schema_version") != "market-desk-public-observation-run.v1":
        return _blocked(
            "Public desk observation record has an unsupported schema_version.",
            declared_observed_at=declared_observed_at,
        )
    archive_id = str(payload.get("archive_id") or "").strip()
    digest = archive_id.removeprefix("sha256:")
    if len(digest) != 64 or _sha256(_hash_input(payload)) != digest:
        return _blocked(
            "Public desk observation record content does not match archive_id.",
            declared_observed_at=declared_observed_at,
        )
    if payload.get("operation") != "record_observation_only":
        return _blocked(
            "Public desk observation record has an invalid operation.",
            declared_observed_at=declared_observed_at,
        )
    if payload.get("formal_decision_eligible") is not False or payload.get("no_order_execution") is not True:
        return _blocked(
            "Public desk observation record must retain research-only decision and execution boundaries.",
            declared_observed_at=declared_observed_at,
        )
    rotation = payload.get("rotation_observation")
    if not isinstance(rotation, Mapping):
        return _blocked(
            "Public desk observation record lacks rotation observation evidence.",
            declared_observed_at=declared_observed_at,
        )
    manifest = rotation.get("source_manifest")
    if not isinstance(manifest, Mapping):
        return _blocked(
            "Public desk observation record lacks the rotation source manifest.",
            declared_observed_at=declared_observed_at,
        )
    source_assurance = verify_frozen_market_archive(
        rotation.get("source_archive_path"),
        expected_archive_id=str(manifest.get("archive_id") or "") or None,
        expected_source=str(manifest.get("source") or "") or None,
    )
    if source_assurance.get("status") != "pass":
        failures = source_assurance.get("failures", [])
        detail = "; ".join(str(item) for item in failures) if isinstance(failures, list) else "unknown source verification failure"
        return _blocked(
            f"Linked rotation source archive failed verification: {detail}",
            declared_observed_at=declared_observed_at,
        )
    eod_validation = _validate_eod_observation_payload(payload)
    return {
        "status": "pass",
        "archive_path": str(source_path),
        "archive_id": archive_id,
        "observed_at": payload.get("observed_at"),
        "declared_observed_at": declared_observed_at,
        "rotation_source_assurance": source_assurance,
        "eod_validation": eod_validation,
        "failures": [],
    }


def list_public_desk_observation_runs(
    directory: str | Path, *, exception_directory: str | Path | None = None
) -> dict[str, Any]:
    """Audit all immutable desk-run records in an archive directory."""
    archive_directory = Path(directory)
    paths = sorted(archive_directory.glob("*.json")) if archive_directory.is_dir() else []
    records: list[dict[str, Any]] = []
    declared_daily_counts: dict[str, int] = {}
    valid_daily_counts: dict[str, int] = {}
    for path in paths:
        verification = verify_public_desk_observation_run(path)
        observed_at = verification.get("declared_observed_at")
        if isinstance(observed_at, str) and len(observed_at) >= 10:
            day = observed_at[:10]
            declared_daily_counts[day] = declared_daily_counts.get(day, 0) + 1
            if verification.get("status") == "pass":
                valid_daily_counts[day] = valid_daily_counts.get(day, 0) + 1
        records.append(verification)
    valid_count = sum(record.get("status") == "pass" for record in records)
    valid_eod_records = [
        record
        for record in records
        if record.get("status") == "pass"
        and isinstance(record.get("eod_validation"), Mapping)
        and record["eod_validation"].get("status") == "pass"
    ]
    observed = sorted(
        str(record["observed_at"])
        for record in records
        if record.get("status") == "pass" and isinstance(record.get("observed_at"), str)
    )
    valid_records_by_day: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        observed_at = record.get("observed_at")
        if record.get("status") == "pass" and isinstance(observed_at, str) and len(observed_at) >= 10:
            valid_records_by_day.setdefault(observed_at[:10], []).append(record)
    valid_eod_records_by_day: dict[str, list[dict[str, Any]]] = {}
    for record in valid_eod_records:
        observed_at = record.get("observed_at")
        if isinstance(observed_at, str) and len(observed_at) >= 10:
            valid_eod_records_by_day.setdefault(observed_at[:10], []).append(record)
    valid_duplicate_days = sorted(
        day for day, day_records in valid_records_by_day.items() if len(day_records) > 1
    )
    review_directory = Path(exception_directory) if exception_directory is not None else archive_directory.parent / "market-desk-observation-exceptions"
    reviews = _list_valid_exception_reviews(review_directory)
    resolved_duplicate_days: list[str] = []
    for day in valid_duplicate_days:
        current_ids = {str(record.get("archive_id") or "") for record in valid_records_by_day[day]}
        if any(
            review["session_date"] == day
            and set(review["archive_ids"]) == current_ids
            and review["canonical_archive_id"] in current_ids
            for review in reviews
        ):
            resolved_duplicate_days.append(day)
    unresolved_valid_duplicate_days = sorted(set(valid_duplicate_days) - set(resolved_duplicate_days))
    return {
        "schema_version": "market-desk-public-observation-history.v1",
        "archive_directory": str(archive_directory),
        "run_count": len(records),
        "valid_count": valid_count,
        "invalid_count": len(records) - valid_count,
        "latest_valid_observed_at": observed[-1] if observed else None,
        "eod_valid_count": len(valid_eod_records),
        "latest_valid_eod_observed_at": (
            max(str(record["observed_at"]) for record in valid_eod_records)
            if valid_eod_records
            else None
        ),
        "valid_eod_daily_run_counts": {
            day: len(day_records)
            for day, day_records in sorted(valid_eod_records_by_day.items())
        },
        "declared_daily_run_counts": declared_daily_counts,
        "valid_daily_run_counts": valid_daily_counts,
        "duplicate_run_dates": sorted(
            day for day, count in declared_daily_counts.items() if count > 1
        ),
        "valid_duplicate_run_dates": valid_duplicate_days,
        "resolved_duplicate_run_dates": resolved_duplicate_days,
        "unresolved_valid_duplicate_run_dates": unresolved_valid_duplicate_days,
        "exception_review_directory": str(review_directory),
        "valid_exception_review_count": len(reviews),
        "records": records,
        "research_only": True,
        "no_order_execution": True,
    }


def _validate_eod_observation_payload(payload: Mapping[str, Any]) -> dict[str, str]:
    """Classify a valid record as EOD only with exchange-calendar evidence.

    Direct intraday observation records remain valid research artifacts, but
    must not satisfy the scheduled after-close control or be counted as EOD
    operating evidence.
    """
    overview = payload.get("market_overview")
    snapshot = overview.get("snapshot") if isinstance(overview, Mapping) else None
    session = snapshot.get("market_session") if isinstance(snapshot, Mapping) else None
    if not isinstance(session, Mapping):
        return {
            "status": "not_eod",
            "reason": "market_session_metadata_missing",
        }
    state = str(session.get("state") or "").strip()
    calendar_basis = str(session.get("calendar_basis") or "").strip()
    if state != "after_close":
        return {
            "status": "not_eod",
            "reason": f"market_session_state={state or 'missing'}",
        }
    if calendar_basis != "exchange_calendar":
        return {
            "status": "not_eod",
            "reason": f"calendar_basis={calendar_basis or 'missing'}",
        }
    return {
        "status": "pass",
        "reason": "verified_exchange_after_close",
    }


def _hash_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: payload[key]
        for key in (
            "schema_version",
            "observed_at",
            "market_overview",
            "rotation_observation",
            "operational_readiness",
            "formal_decision_eligible",
            "research_only",
            "no_order_execution",
        )
    }


def _exception_hash_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: payload[key]
        for key in (
            "schema_version",
            "session_date",
            "archive_ids",
            "canonical_archive_id",
            "reviewer",
            "reason",
            "evidence_refs",
            "reviewed_at",
            "research_only",
            "no_order_execution",
        )
    }


def _normalize_review_timestamp(value: str | datetime | None) -> str:
    if value is None:
        return datetime.now(timezone.utc).isoformat()
    if isinstance(value, datetime):
        timestamp = value
    else:
        try:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("reviewed_at must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError("reviewed_at must include a timezone")
    return timestamp.astimezone(timezone.utc).isoformat()


def _list_valid_exception_reviews(directory: Path) -> list[dict[str, Any]]:
    reviews: list[dict[str, Any]] = []
    if not directory.is_dir():
        return reviews
    for path in sorted(directory.glob("*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, Mapping):
            continue
        review_id = str(payload.get("review_id") or "")
        digest = review_id.removeprefix("sha256:")
        try:
            integrity_ok = _sha256(_exception_hash_input(payload)) == digest
        except KeyError:
            integrity_ok = False
        if (
            payload.get("schema_version") != "market-desk-public-observation-exception-review.v1"
            or len(digest) != 64
            or not integrity_ok
            or payload.get("research_only") is not True
            or payload.get("no_order_execution") is not True
        ):
            continue
        archive_ids = payload.get("archive_ids")
        if not isinstance(archive_ids, list) or len(archive_ids) < 2:
            continue
        canonical_archive_id = str(payload.get("canonical_archive_id") or "")
        if canonical_archive_id not in archive_ids:
            continue
        reviews.append(
            {
                "review_id": review_id,
                "session_date": str(payload.get("session_date") or ""),
                "archive_ids": [str(value) for value in archive_ids],
                "canonical_archive_id": canonical_archive_id,
            }
        )
    return reviews


def _sha256(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _blocked(
    failure: str, *, declared_observed_at: str | None = None
) -> dict[str, Any]:
    return {
        "status": "blocked",
        "declared_observed_at": declared_observed_at,
        "failures": [failure],
    }
