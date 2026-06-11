"""JSONL-backed market event storage for agent workflows."""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any, TypeAlias, cast

from .models import (
    EVENT_SCHEMA_VERSION,
    EventDirection,
    EventSeverity,
    MarketEvent,
    MarketEventType,
    SubjectType,
    coerce_datetime,
    normalize_direction,
    normalize_event_type,
    normalize_severity,
    normalize_subject_type,
)

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]
EventInput: TypeAlias = MarketEvent | Mapping[str, Any]


@dataclass(frozen=True)
class EventQuery:
    """Filter criteria for listing and replaying stored market events."""

    subject_code: str | None = None
    subject_name: str | None = None
    subject_type: SubjectType | str | None = None
    event_type: MarketEventType | str | None = None
    tag: str | None = None
    severity: EventSeverity | str | int | None = None
    direction: EventDirection | str | None = None
    start_at: datetime | str | int | float | None = None
    end_at: datetime | str | int | float | None = None
    limit: int | None = None


@dataclass(frozen=True)
class EventWriteResult:
    """Result returned when attempting to store a market event."""

    event_id: str
    inserted: bool
    path: str

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-ready write result."""

        return {
            "event_id": self.event_id,
            "inserted": self.inserted,
            "path": self.path,
        }


class EventStore:
    """Append-only JSONL event store with deterministic de-duplication."""

    def __init__(self, path: str | Path = "data/market-events.jsonl") -> None:
        self.path = Path(path)

    def add(self, event: EventInput) -> EventWriteResult:
        """Store one event if its id has not already been recorded."""

        record = normalize_event_record(event)
        event_id = require_text(record.get("id"), "id")
        if self.get(event_id) is not None:
            return EventWriteResult(
                event_id=event_id, inserted=False, path=str(self.path)
            )

        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            handle.write("\n")
        return EventWriteResult(event_id=event_id, inserted=True, path=str(self.path))

    def add_many(self, events: Iterable[EventInput]) -> dict[str, JSONValue]:
        """Store multiple events and return inserted / duplicate counts."""

        inserted = 0
        duplicate = 0
        event_ids: list[str] = []
        for event in events:
            result = self.add(event)
            event_ids.append(result.event_id)
            if result.inserted:
                inserted += 1
            else:
                duplicate += 1
        return {
            "inserted": inserted,
            "duplicate": duplicate,
            "total": inserted + duplicate,
            "event_ids": cast(JSONValue, event_ids),
            "path": str(self.path),
        }

    def get(self, event_id: str) -> dict[str, JSONValue] | None:
        """Return one event by id, or None when not found."""

        for event in self.iter_events():
            if event.get("id") == event_id:
                return event
        return None

    def iter_events(self) -> Iterable[dict[str, JSONValue]]:
        """Yield stored canonical event dictionaries in file order."""

        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                text = line.strip()
                if not text:
                    continue
                try:
                    raw = json.loads(text)
                except json.JSONDecodeError as exc:
                    msg = f"Invalid market event JSON at {self.path}:{line_number}"
                    raise ValueError(msg) from exc
                if not isinstance(raw, Mapping):
                    msg = f"Market event record must be an object at {self.path}:{line_number}"
                    raise ValueError(msg)
                yield normalize_event_record(raw)

    def list_events(
        self,
        query: EventQuery | None = None,
        *,
        subject_code: str | None = None,
        subject_name: str | None = None,
        subject_type: SubjectType | str | None = None,
        event_type: MarketEventType | str | None = None,
        tag: str | None = None,
        severity: EventSeverity | str | int | None = None,
        direction: EventDirection | str | None = None,
        start_at: datetime | str | int | float | None = None,
        end_at: datetime | str | int | float | None = None,
        limit: int | None = None,
        reverse: bool = False,
    ) -> list[dict[str, JSONValue]]:
        """List events matching filters, sorted by observed time."""

        merged_query = merge_query(
            query,
            subject_code=subject_code,
            subject_name=subject_name,
            subject_type=subject_type,
            event_type=event_type,
            tag=tag,
            severity=severity,
            direction=direction,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )
        matched = [
            event for event in self.iter_events() if event_matches(event, merged_query)
        ]
        matched.sort(key=event_sort_key, reverse=reverse)
        if merged_query.limit is not None:
            return matched[: max(merged_query.limit, 0)]
        return matched

    def replay_subject(
        self,
        *,
        subject_code: str | None = None,
        subject_name: str | None = None,
        subject_type: SubjectType | str | None = None,
        start_at: datetime | str | int | float | None = None,
        end_at: datetime | str | int | float | None = None,
        limit: int | None = None,
    ) -> list[dict[str, JSONValue]]:
        """Replay chronological events for a stock, sector, theme, or other subject."""

        events = self.list_events(
            subject_code=subject_code,
            subject_name=subject_name,
            subject_type=subject_type,
            start_at=start_at,
            end_at=end_at,
        )
        if limit is None:
            return events
        return events[-max(limit, 0) :]

    def aggregate(
        self,
        query: EventQuery | None = None,
        *,
        subject_code: str | None = None,
        subject_name: str | None = None,
        subject_type: SubjectType | str | None = None,
        event_type: MarketEventType | str | None = None,
        tag: str | None = None,
        severity: EventSeverity | str | int | None = None,
        direction: EventDirection | str | None = None,
        start_at: datetime | str | int | float | None = None,
        end_at: datetime | str | int | float | None = None,
        limit: int | None = None,
    ) -> dict[str, JSONValue]:
        """Aggregate matching events for market-board summaries."""

        events = self.list_events(
            query,
            subject_code=subject_code,
            subject_name=subject_name,
            subject_type=subject_type,
            event_type=event_type,
            tag=tag,
            severity=severity,
            direction=direction,
            start_at=start_at,
            end_at=end_at,
            limit=limit,
        )
        event_type_counts: dict[str, int] = {}
        severity_counts: dict[str, int] = {}
        direction_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}
        subject_counts: dict[str, dict[str, JSONValue]] = {}

        for event in events:
            increment(
                event_type_counts, optional_text(event.get("event_type"), "unknown")
            )
            increment(severity_counts, optional_text(event.get("severity"), "unknown"))
            increment(
                direction_counts, optional_text(event.get("direction"), "unknown")
            )
            for event_tag in event_tags(event):
                increment(tag_counts, event_tag)
            subject = event_subject(event)
            subject_key = subject_count_key(subject)
            if subject_key not in subject_counts:
                subject_counts[subject_key] = {
                    "count": 0,
                    "type": optional_text(subject.get("type"), "unknown"),
                    "code": optional_text_or_none(subject.get("code")),
                    "name": optional_text_or_none(subject.get("name")),
                    "market": optional_text_or_none(subject.get("market")),
                }
            count = cast(int, subject_counts[subject_key]["count"])
            subject_counts[subject_key]["count"] = count + 1

        return {
            "total": len(events),
            "event_type": counter_to_json(event_type_counts),
            "subject": cast(JSONValue, subject_counts),
            "tag": counter_to_json(tag_counts),
            "severity": counter_to_json(severity_counts),
            "direction": counter_to_json(direction_counts),
        }


def normalize_event_record(event: EventInput) -> dict[str, JSONValue]:
    """Convert a MarketEvent or canonical mapping into a JSON-ready record."""

    if isinstance(event, MarketEvent):
        record = event.to_dict()
    else:
        record = json_ready_dict(event)

    require_text(record.get("id"), "id")
    require_text(record.get("event_type"), "event_type")
    require_text(record.get("observed_at"), "observed_at")
    subject = record.get("subject")
    if not isinstance(subject, Mapping):
        raise ValueError("market event record requires subject object")

    normalized = dict(record)
    normalized.setdefault("schema_version", EVENT_SCHEMA_VERSION)
    normalized["subject"] = normalize_subject_record(subject)
    normalized["tags"] = cast(JSONValue, list(event_tags(normalized)))
    return normalized


def merge_query(
    query: EventQuery | None,
    *,
    subject_code: str | None,
    subject_name: str | None,
    subject_type: SubjectType | str | None,
    event_type: MarketEventType | str | None,
    tag: str | None,
    severity: EventSeverity | str | int | None,
    direction: EventDirection | str | None,
    start_at: datetime | str | int | float | None,
    end_at: datetime | str | int | float | None,
    limit: int | None,
) -> EventQuery:
    """Merge an optional EventQuery with explicit keyword overrides."""

    base = query or EventQuery()
    return EventQuery(
        subject_code=subject_code if subject_code is not None else base.subject_code,
        subject_name=subject_name if subject_name is not None else base.subject_name,
        subject_type=subject_type if subject_type is not None else base.subject_type,
        event_type=event_type if event_type is not None else base.event_type,
        tag=tag if tag is not None else base.tag,
        severity=severity if severity is not None else base.severity,
        direction=direction if direction is not None else base.direction,
        start_at=start_at if start_at is not None else base.start_at,
        end_at=end_at if end_at is not None else base.end_at,
        limit=limit if limit is not None else base.limit,
    )


def event_matches(event: Mapping[str, JSONValue], query: EventQuery) -> bool:
    """Return whether an event satisfies a query."""

    subject = event_subject(event)
    if (
        query.subject_code
        and optional_text_or_none(subject.get("code")) != query.subject_code
    ):
        return False
    if (
        query.subject_name
        and optional_text_or_none(subject.get("name")) != query.subject_name
    ):
        return False
    if query.subject_type is not None:
        expected_subject_type = normalize_subject_type(query.subject_type).value
        if optional_text(subject.get("type"), "unknown") != expected_subject_type:
            return False
    if query.event_type is not None:
        expected_event_type = normalize_event_type(query.event_type).value
        if optional_text(event.get("event_type"), "unknown") != expected_event_type:
            return False
    if query.tag and query.tag not in event_tags(event):
        return False
    if query.severity is not None:
        expected_severity = normalize_severity(query.severity).value
        if optional_text(event.get("severity"), "unknown") != expected_severity:
            return False
    if query.direction is not None:
        expected_direction = normalize_direction(query.direction).value
        if optional_text(event.get("direction"), "unknown") != expected_direction:
            return False

    observed_at = event_observed_at(event)
    start_at = coerce_datetime(query.start_at)
    end_at = coerce_datetime(query.end_at)
    if start_at and observed_at < start_at:
        return False
    if end_at and observed_at > end_at:
        return False
    return True


def event_sort_key(event: Mapping[str, JSONValue]) -> tuple[datetime, str]:
    """Sort events chronologically and then by id for stability."""

    return (event_observed_at(event), optional_text(event.get("id"), ""))


def event_observed_at(event: Mapping[str, JSONValue]) -> datetime:
    """Return a sortable observed_at value for one event."""

    return coerce_datetime(event.get("observed_at")) or datetime.min.replace(
        tzinfo=timezone.utc
    )


def event_subject(event: Mapping[str, JSONValue]) -> dict[str, JSONValue]:
    """Return the subject object from an event, or an empty subject."""

    subject = event.get("subject")
    if isinstance(subject, Mapping):
        return json_ready_dict(subject)
    return {
        "type": SubjectType.UNKNOWN.value,
        "code": None,
        "name": None,
        "market": None,
    }


def event_tags(event: Mapping[str, JSONValue]) -> tuple[str, ...]:
    """Return normalized tags from a stored event."""

    raw_tags = event.get("tags")
    if not isinstance(raw_tags, Sequence) or isinstance(
        raw_tags, (str, bytes, bytearray)
    ):
        return ()
    tags: list[str] = []
    seen: set[str] = set()
    for raw_tag in raw_tags:
        tag = optional_text_or_none(raw_tag)
        if tag and tag not in seen:
            tags.append(tag)
            seen.add(tag)
    return tuple(tags)


def subject_count_key(subject: Mapping[str, JSONValue]) -> str:
    """Build a stable aggregate key for a subject."""

    subject_type = optional_text(subject.get("type"), SubjectType.UNKNOWN.value)
    code = optional_text_or_none(subject.get("code"))
    name = optional_text_or_none(subject.get("name"))
    if code:
        return f"{subject_type}:{code}"
    if name:
        return f"{subject_type}:{name}"
    return subject_type


def normalize_subject_record(subject: Mapping[Any, Any]) -> dict[str, JSONValue]:
    """Normalize a subject mapping while preserving agent-visible fields."""

    subject_type = normalize_subject_type(optional_text(subject.get("type"), "unknown"))
    code = optional_text_or_none(subject.get("code"))
    name = optional_text_or_none(subject.get("name"))
    market = optional_text_or_none(subject.get("market"))
    key = code or name or subject_type.value
    normalized = json_ready_dict(subject)
    normalized.update(
        {
            "type": subject_type.value,
            "code": code,
            "name": name,
            "market": market,
            "key": key,
        }
    )
    return normalized


def require_text(value: JSONValue | Any, field_name: str) -> str:
    """Return a non-empty text value or raise a ValueError."""

    text = optional_text_or_none(value)
    if text is None:
        raise ValueError(f"market event record requires {field_name}")
    return text


def optional_text(value: JSONValue | Any, default: str) -> str:
    """Return stripped text, falling back to default for blank values."""

    text = optional_text_or_none(value)
    return text if text is not None else default


def optional_text_or_none(value: JSONValue | Any) -> str | None:
    """Return stripped text for scalar-ish values."""

    if value is None:
        return None
    text = str(value).strip()
    return text or None


def increment(counter: dict[str, int], key: str) -> None:
    """Increment a string-keyed counter."""

    counter[key] = counter.get(key, 0) + 1


def counter_to_json(counter: Mapping[str, int]) -> dict[str, JSONValue]:
    """Convert an integer counter into a JSONValue-compatible dictionary."""

    return {key: value for key, value in counter.items()}


def json_ready_dict(value: Mapping[Any, Any]) -> dict[str, JSONValue]:
    """Convert a mapping into a JSON-ready dictionary."""

    return {str(key): json_ready(item) for key, item in value.items()}


def json_ready(value: Any) -> JSONValue:
    """Convert common Python values into JSON-safe values."""

    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(key): json_ready(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [json_ready(item) for item in value]
    return str(value)
