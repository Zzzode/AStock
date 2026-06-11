"""JSON-serializable data provenance records.

This module is intentionally deterministic and side-effect free. Data adapters can
attach these records to capability packets so agents can reason about source,
freshness, quality, fallback behavior, and errors without parsing ad hoc strings.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import TypeAlias, cast

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]
JsonDict: TypeAlias = dict[str, JsonValue]
IssueInput: TypeAlias = "ProvenanceIssue | str | Mapping[str, object]"

SCHEMA_VERSION = "data_provenance.v1"


class QualityTier(str, Enum):
    """Ordered quality tier for source data."""

    REALTIME = "realtime"
    DELAYED = "delayed"
    SNAPSHOT = "snapshot"
    CACHED = "cached"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"

    @classmethod
    def parse(cls, value: "QualityTier | str") -> "QualityTier":
        """Parse a quality tier from an enum instance or string value."""
        if isinstance(value, cls):
            return value
        normalized = value.strip().lower()
        for tier in cls:
            if tier.value == normalized:
                return tier
        valid = ", ".join(tier.value for tier in cls)
        raise ValueError(f"Unknown quality tier {value!r}; expected one of: {valid}")

    @property
    def rank(self) -> int:
        """Return an ordinal score where higher means better quality."""
        return QUALITY_TIER_RANKS[self]


QUALITY_TIER_RANKS: dict[QualityTier, int] = {
    QualityTier.REALTIME: 100,
    QualityTier.DELAYED: 80,
    QualityTier.SNAPSHOT: 65,
    QualityTier.CACHED: 50,
    QualityTier.DEGRADED: 25,
    QualityTier.UNAVAILABLE: 0,
}


@dataclass(frozen=True, init=False)
class ProvenanceIssue:
    """Structured warning or error attached to a provenance record."""

    message: str
    code: str | None = None
    source: str | None = None
    details: JsonDict = field(default_factory=dict)

    def __init__(
        self,
        message: str,
        code: str | None = None,
        source: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> None:
        normalized_message = message.strip()
        if not normalized_message:
            raise ValueError("Provenance issue message must not be empty")
        object.__setattr__(self, "message", normalized_message)
        object.__setattr__(
            self, "code", code.strip() if code and code.strip() else None
        )
        object.__setattr__(
            self,
            "source",
            source.strip() if source and source.strip() else None,
        )
        object.__setattr__(self, "details", _normalize_json_dict(details or {}))

    def to_dict(self) -> JsonDict:
        """Return a JSON-ready dictionary."""
        data: JsonDict = {"message": self.message}
        if self.code is not None:
            data["code"] = self.code
        if self.source is not None:
            data["source"] = self.source
        if self.details:
            data["details"] = self.details
        return data

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ProvenanceIssue":
        """Create an issue from a mapping."""
        raw_message = data.get("message")
        if raw_message is None:
            raise ValueError("Provenance issue requires a message")
        raw_details = data.get("details", {})
        details = (
            cast(Mapping[str, object], raw_details)
            if isinstance(raw_details, Mapping)
            else {"value": raw_details}
        )
        return cls(
            message=str(raw_message),
            code=_optional_str(data.get("code")),
            source=_optional_str(data.get("source")),
            details=_normalize_json_dict(details),
        )


@dataclass(frozen=True, init=False)
class DataProvenance:
    """Source, freshness, quality, fallback, and issue metadata for a data value."""

    source: str
    timestamp: str
    quality_tier: QualityTier
    latency_ms: int | None
    fallback_path: tuple[str, ...]
    warnings: tuple[ProvenanceIssue, ...]
    errors: tuple[ProvenanceIssue, ...]
    schema_version: str

    def __init__(
        self,
        source: str,
        timestamp: datetime | str,
        quality_tier: QualityTier | str,
        latency_ms: int | float | None = None,
        fallback_path: Sequence[str] | str = (),
        warnings: Sequence[IssueInput] = (),
        errors: Sequence[IssueInput] = (),
        schema_version: str = SCHEMA_VERSION,
    ) -> None:
        normalized_source = source.strip()
        if not normalized_source:
            raise ValueError("Data provenance source must not be empty")

        object.__setattr__(self, "source", normalized_source)
        object.__setattr__(self, "timestamp", _normalize_timestamp(timestamp))
        object.__setattr__(self, "quality_tier", QualityTier.parse(quality_tier))
        object.__setattr__(self, "latency_ms", _normalize_latency_ms(latency_ms))
        object.__setattr__(
            self,
            "fallback_path",
            _normalize_fallback_path(fallback_path),
        )
        object.__setattr__(
            self,
            "warnings",
            tuple(_coerce_issue(issue, normalized_source) for issue in warnings),
        )
        object.__setattr__(
            self,
            "errors",
            tuple(_coerce_issue(issue, normalized_source) for issue in errors),
        )
        object.__setattr__(self, "schema_version", schema_version.strip())

    @property
    def ok(self) -> bool:
        """Return whether this data is usable without hard source errors."""
        return not self.errors and self.quality_tier is not QualityTier.UNAVAILABLE

    def to_dict(self) -> JsonDict:
        """Return a JSON-ready dictionary."""
        return {
            "schema_version": self.schema_version,
            "source": self.source,
            "timestamp": self.timestamp,
            "quality_tier": self.quality_tier.value,
            "quality_rank": self.quality_tier.rank,
            "latency_ms": self.latency_ms,
            "fallback_path": list(self.fallback_path),
            "warnings": [issue.to_dict() for issue in self.warnings],
            "errors": [issue.to_dict() for issue in self.errors],
            "ok": self.ok,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "DataProvenance":
        """Create a provenance record from a mapping."""
        source = _required_str(data, "source")
        timestamp = _required_str(data, "timestamp")
        quality_tier = _required_str(data, "quality_tier")

        fallback_path = _coerce_str_sequence(data.get("fallback_path", ()))
        warnings = _coerce_issue_sequence(data.get("warnings", ()))
        errors = _coerce_issue_sequence(data.get("errors", ()))

        return cls(
            source=source,
            timestamp=timestamp,
            quality_tier=quality_tier,
            latency_ms=_optional_number(data.get("latency_ms")),
            fallback_path=fallback_path,
            warnings=warnings,
            errors=errors,
            schema_version=str(data.get("schema_version", SCHEMA_VERSION)),
        )

    def to_json(self) -> str:
        """Serialize the record to stable JSON."""
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "DataProvenance":
        """Deserialize a record from JSON."""
        data = json.loads(payload)
        if not isinstance(data, Mapping):
            raise ValueError("Data provenance JSON payload must be an object")
        return cls.from_dict(cast(Mapping[str, object], data))

    def with_warning(
        self,
        message: str,
        code: str | None = None,
        source: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> "DataProvenance":
        """Return a copy with an additional warning."""
        issue = ProvenanceIssue(
            message=message,
            code=code,
            source=source or self.source,
            details=_normalize_json_dict(details or {}),
        )
        return self._copy(warnings=(*self.warnings, issue))

    def with_error(
        self,
        message: str,
        code: str | None = None,
        source: str | None = None,
        details: Mapping[str, object] | None = None,
    ) -> "DataProvenance":
        """Return a copy with an additional error."""
        issue = ProvenanceIssue(
            message=message,
            code=code,
            source=source or self.source,
            details=_normalize_json_dict(details or {}),
        )
        return self._copy(errors=(*self.errors, issue))

    def with_fallback(self, source: str) -> "DataProvenance":
        """Return a copy with a source appended to the fallback path."""
        normalized = source.strip()
        if not normalized:
            raise ValueError("Fallback source must not be empty")
        return self._copy(fallback_path=(*self.fallback_path, normalized))

    def with_quality(self, quality_tier: QualityTier | str) -> "DataProvenance":
        """Return a copy with a changed quality tier."""
        return self._copy(quality_tier=QualityTier.parse(quality_tier))

    def _copy(
        self,
        *,
        quality_tier: QualityTier | str | None = None,
        latency_ms: int | float | None = None,
        fallback_path: Sequence[str] | str | None = None,
        warnings: Sequence[IssueInput] | None = None,
        errors: Sequence[IssueInput] | None = None,
    ) -> "DataProvenance":
        return DataProvenance(
            source=self.source,
            timestamp=self.timestamp,
            quality_tier=quality_tier or self.quality_tier,
            latency_ms=self.latency_ms if latency_ms is None else latency_ms,
            fallback_path=(
                self.fallback_path if fallback_path is None else fallback_path
            ),
            warnings=self.warnings if warnings is None else warnings,
            errors=self.errors if errors is None else errors,
            schema_version=self.schema_version,
        )


def worst_quality_tier(tiers: Sequence[QualityTier | str]) -> QualityTier:
    """Return the lowest quality tier from a non-empty sequence."""
    if not tiers:
        raise ValueError("At least one quality tier is required")
    parsed = [QualityTier.parse(tier) for tier in tiers]
    return min(parsed, key=lambda tier: tier.rank)


def combine_provenance(
    records: Sequence[DataProvenance],
    *,
    source: str,
    timestamp: datetime | str,
    quality_tier: QualityTier | str | None = None,
) -> DataProvenance:
    """Combine multiple provenance records for a derived data packet."""
    if not records and quality_tier is None:
        raise ValueError("Cannot combine empty provenance without a quality tier")

    combined_quality = (
        QualityTier.parse(quality_tier)
        if quality_tier is not None
        else worst_quality_tier([record.quality_tier for record in records])
    )
    latency_values = [
        record.latency_ms for record in records if record.latency_ms is not None
    ]
    fallback_path = _unique_ordered(
        item for record in records for item in (record.source, *record.fallback_path)
    )
    warnings = tuple(issue for record in records for issue in record.warnings)
    errors = tuple(issue for record in records for issue in record.errors)

    return DataProvenance(
        source=source,
        timestamp=timestamp,
        quality_tier=combined_quality,
        latency_ms=max(latency_values) if latency_values else None,
        fallback_path=fallback_path,
        warnings=warnings,
        errors=errors,
    )


def _normalize_timestamp(value: datetime | str) -> str:
    if isinstance(value, datetime):
        timestamp = value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        return timestamp.isoformat()

    normalized = value.strip()
    if not normalized:
        raise ValueError("Data provenance timestamp must not be empty")
    parse_target = normalized.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(parse_target).isoformat()
    except ValueError as exc:
        raise ValueError(
            f"Data provenance timestamp must be ISO-8601: {value!r}"
        ) from exc


def _normalize_latency_ms(value: int | float | None) -> int | None:
    if value is None:
        return None
    if value < 0:
        raise ValueError("Latency must not be negative")
    return int(round(value))


def _normalize_fallback_path(value: Sequence[str] | str) -> tuple[str, ...]:
    if isinstance(value, str):
        items: tuple[str, ...] = (value,)
    else:
        items = tuple(value)
    normalized = tuple(item.strip() for item in items if item.strip())
    return _unique_ordered(normalized)


def _coerce_issue(value: IssueInput, default_source: str) -> ProvenanceIssue:
    if isinstance(value, ProvenanceIssue):
        return value
    if isinstance(value, str):
        return ProvenanceIssue(message=value, source=default_source)
    if isinstance(value, Mapping):
        return ProvenanceIssue.from_dict(value)
    raise TypeError(f"Unsupported provenance issue type: {type(value).__name__}")


def _coerce_issue_sequence(value: object) -> tuple[IssueInput, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if not isinstance(value, Sequence):
        raise ValueError("Provenance issue collection must be a sequence")
    return tuple(cast(Sequence[IssueInput], value))


def _coerce_str_sequence(value: object) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if not isinstance(value, Sequence):
        raise ValueError("Fallback path must be a string or sequence of strings")
    return tuple(str(item) for item in value)


def _required_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if value is None:
        raise ValueError(f"Data provenance requires {key}")
    return str(value)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _optional_number(value: object) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("latency_ms must be numeric")
    return value


def _normalize_json_dict(data: Mapping[str, object]) -> JsonDict:
    return {str(key): _json_ready(value) for key, value in data.items()}


def _json_ready(value: object) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, datetime):
        return _normalize_timestamp(value)
    if isinstance(value, Mapping):
        return _normalize_json_dict(cast(Mapping[str, object], value))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)


def _unique_ordered(values: Iterable[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return tuple(result)
