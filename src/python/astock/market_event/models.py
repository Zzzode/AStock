"""Core market event models for A-share market intelligence.

This module is intentionally self-contained. It defines JSON-ready event
objects that can be produced by Python capability code and consumed by agents
or skills without depending on CLI, API, or storage layers.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Any, TypeAlias, cast

JSONScalar: TypeAlias = str | int | float | bool | None
JSONValue: TypeAlias = JSONScalar | list["JSONValue"] | dict[str, "JSONValue"]

EVENT_SCHEMA_VERSION = "market_event.v1"


class MarketEventType(StrEnum):
    """Supported market intelligence event types."""

    PRICE_MOVE = "price_move"
    VOLUME_SPIKE = "volume_spike"
    SECTOR_MOVE = "sector_move"
    FUND_FLOW_MOVE = "fund_flow_move"
    TECHNICAL_SIGNAL = "technical_signal"
    ALERT_TRIGGER = "alert_trigger"
    NEWS_POLICY_EVENT = "news_policy_event"


class SubjectType(StrEnum):
    """Entity type that an event is primarily about."""

    STOCK = "stock"
    SECTOR = "sector"
    THEME = "theme"
    INDEX = "index"
    MARKET = "market"
    POLICY = "policy"
    UNKNOWN = "unknown"


class EventDirection(StrEnum):
    """Directional interpretation for market intelligence."""

    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"
    MIXED = "mixed"
    UNKNOWN = "unknown"


class EventSeverity(StrEnum):
    """Severity used for ranking, alerting, and agent attention."""

    INFO = "info"
    WATCH = "watch"
    IMPORTANT = "important"
    CRITICAL = "critical"


class DataQualityLevel(StrEnum):
    """Data quality level attached to an event."""

    FULL = "full"
    PARTIAL = "partial"
    DELAYED = "delayed"
    DEGRADED = "degraded"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


_SEVERITY_RANK: dict[EventSeverity, int] = {
    EventSeverity.INFO: 0,
    EventSeverity.WATCH: 1,
    EventSeverity.IMPORTANT: 2,
    EventSeverity.CRITICAL: 3,
}

_QUALITY_RANK: dict[DataQualityLevel, int] = {
    DataQualityLevel.FULL: 0,
    DataQualityLevel.PARTIAL: 1,
    DataQualityLevel.DELAYED: 2,
    DataQualityLevel.DEGRADED: 3,
    DataQualityLevel.UNAVAILABLE: 4,
    DataQualityLevel.UNKNOWN: 5,
}

_QUALITY_ALIASES: dict[str, DataQualityLevel] = {
    "full_realtime": DataQualityLevel.FULL,
    "realtime": DataQualityLevel.FULL,
    "full": DataQualityLevel.FULL,
    "snapshot": DataQualityLevel.PARTIAL,
    "snapshot_degraded": DataQualityLevel.DEGRADED,
    "partial": DataQualityLevel.PARTIAL,
    "daily_only": DataQualityLevel.DELAYED,
    "delayed": DataQualityLevel.DELAYED,
    "degraded": DataQualityLevel.DEGRADED,
    "unavailable": DataQualityLevel.UNAVAILABLE,
    "unknown": DataQualityLevel.UNKNOWN,
}


@dataclass(frozen=True)
class EventSubject:
    """Primary market entity for a market event."""

    type: SubjectType = SubjectType.UNKNOWN
    code: str | None = None
    name: str | None = None
    market: str | None = "A-share"

    def __post_init__(self) -> None:
        object.__setattr__(self, "type", normalize_subject_type(self.type))
        object.__setattr__(self, "code", _clean_optional_text(self.code))
        object.__setattr__(self, "name", _clean_optional_text(self.name))
        object.__setattr__(self, "market", _clean_optional_text(self.market))

    @property
    def key(self) -> str:
        """Stable subject key used in event identity."""

        if self.code:
            return self.code
        if self.name:
            return self.name
        return self.type.value

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-ready subject dictionary."""

        return {
            "type": self.type.value,
            "code": self.code,
            "name": self.name,
            "market": self.market,
            "key": self.key,
        }


@dataclass(frozen=True)
class EventQuality:
    """Data quality and provenance information for an event."""

    level: DataQualityLevel = DataQualityLevel.UNKNOWN
    source: str = "unknown"
    confidence: float = 1.0
    as_of: datetime | None = None
    latency_seconds: float | None = None
    warnings: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "level", normalize_quality_level(self.level))
        object.__setattr__(self, "source", _clean_text(self.source, "unknown"))
        object.__setattr__(self, "confidence", _clamp_float(self.confidence, 0.0, 1.0))
        object.__setattr__(self, "as_of", coerce_datetime(self.as_of))
        object.__setattr__(
            self,
            "latency_seconds",
            _clean_float(self.latency_seconds),
        )
        object.__setattr__(self, "warnings", _dedupe_text_tuple(self.warnings))
        object.__setattr__(
            self,
            "missing_fields",
            _dedupe_text_tuple(self.missing_fields),
        )

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-ready quality dictionary."""

        return {
            "level": self.level.value,
            "source": self.source,
            "confidence": self.confidence,
            "as_of": self.as_of.isoformat() if self.as_of else None,
            "latency_seconds": self.latency_seconds,
            "warnings": list(self.warnings),
            "missing_fields": list(self.missing_fields),
        }


@dataclass(frozen=True)
class MarketEvent:
    """Canonical market event consumed by agents and skills."""

    event_type: MarketEventType
    subject: EventSubject
    title: str
    observed_at: datetime
    severity: EventSeverity = EventSeverity.WATCH
    direction: EventDirection = EventDirection.UNKNOWN
    quality: EventQuality = field(default_factory=EventQuality)
    source: str = "unknown"
    metrics: Mapping[str, Any] = field(default_factory=dict)
    context: Mapping[str, Any] = field(default_factory=dict)
    tags: tuple[str, ...] = ()
    dedupe_key: str = ""
    id: str = ""
    schema_version: str = EVENT_SCHEMA_VERSION

    def __post_init__(self) -> None:
        event_type = normalize_event_type(self.event_type)
        observed_at = coerce_datetime(self.observed_at)
        if observed_at is None:
            observed_at = datetime.fromtimestamp(0, tz=timezone.utc)

        metrics = _json_ready_dict(self.metrics)
        context = _json_ready_dict(self.context)
        tags = _dedupe_text_tuple(self.tags)

        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "observed_at", observed_at)
        object.__setattr__(self, "severity", normalize_severity(self.severity))
        object.__setattr__(self, "direction", normalize_direction(self.direction))
        object.__setattr__(self, "source", _clean_text(self.source, "unknown"))
        object.__setattr__(self, "metrics", metrics)
        object.__setattr__(self, "context", context)
        object.__setattr__(self, "tags", tags)
        object.__setattr__(self, "dedupe_key", str(self.dedupe_key or ""))
        object.__setattr__(
            self,
            "schema_version",
            str(self.schema_version or EVENT_SCHEMA_VERSION),
        )

        if not self.id:
            event_id = create_event_id(
                event_type=event_type,
                subject=self.subject,
                observed_at=observed_at,
                source=self.source,
                dedupe_key=self.dedupe_key,
                metrics=metrics,
                schema_version=self.schema_version,
            )
            object.__setattr__(self, "id", event_id)

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-ready event dictionary."""

        return {
            "id": self.id,
            "schema_version": self.schema_version,
            "event_type": self.event_type.value,
            "title": self.title,
            "observed_at": self.observed_at.isoformat(),
            "severity": self.severity.value,
            "direction": self.direction.value,
            "subject": self.subject.to_dict(),
            "quality": self.quality.to_dict(),
            "source": self.source,
            "metrics": dict(self.metrics),
            "context": dict(self.context),
            "tags": list(self.tags),
            "dedupe_key": self.dedupe_key,
        }

    def to_json(self) -> str:
        """Serialize the event to deterministic JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)


def create_event_id(
    *,
    event_type: MarketEventType | str,
    subject: EventSubject,
    observed_at: datetime,
    source: str,
    dedupe_key: str = "",
    metrics: Mapping[str, Any] | None = None,
    schema_version: str = EVENT_SCHEMA_VERSION,
) -> str:
    """Create a deterministic event id from stable event identity fields."""

    normalized_observed_at = coerce_datetime(observed_at) or datetime.fromtimestamp(
        0,
        tz=timezone.utc,
    )
    identity = {
        "schema_version": schema_version,
        "event_type": normalize_event_type(event_type).value,
        "subject": subject.to_dict(),
        "observed_at": normalized_observed_at.isoformat(),
        "source": _clean_text(source, "unknown"),
        "dedupe_key": str(dedupe_key or ""),
        "metrics": _json_ready_dict(metrics or {}),
    }
    raw = json.dumps(
        identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]
    return f"mevt_{digest}"


def normalize_event_type(value: MarketEventType | str) -> MarketEventType:
    """Normalize a raw value into a market event type."""

    if isinstance(value, MarketEventType):
        return value
    return MarketEventType(str(value))


def normalize_subject_type(value: SubjectType | str) -> SubjectType:
    """Normalize a raw value into a subject type."""

    if isinstance(value, SubjectType):
        return value
    try:
        return SubjectType(str(value))
    except ValueError:
        return SubjectType.UNKNOWN


def normalize_direction(value: EventDirection | str | None) -> EventDirection:
    """Normalize a raw value into an event direction."""

    if isinstance(value, EventDirection):
        return value
    if value is None:
        return EventDirection.UNKNOWN
    normalized = str(value).strip().lower()
    aliases = {
        "up": EventDirection.BULLISH,
        "positive": EventDirection.BULLISH,
        "inflow": EventDirection.BULLISH,
        "bull": EventDirection.BULLISH,
        "bullish": EventDirection.BULLISH,
        "down": EventDirection.BEARISH,
        "negative": EventDirection.BEARISH,
        "outflow": EventDirection.BEARISH,
        "bear": EventDirection.BEARISH,
        "bearish": EventDirection.BEARISH,
        "neutral": EventDirection.NEUTRAL,
        "mixed": EventDirection.MIXED,
        "unknown": EventDirection.UNKNOWN,
    }
    return aliases.get(normalized, EventDirection.UNKNOWN)


def direction_from_signed_value(value: float | int | None) -> EventDirection:
    """Infer market direction from a signed numeric value."""

    cleaned = _clean_float(value)
    if cleaned is None:
        return EventDirection.UNKNOWN
    if cleaned > 0:
        return EventDirection.BULLISH
    if cleaned < 0:
        return EventDirection.BEARISH
    return EventDirection.NEUTRAL


def normalize_severity(value: EventSeverity | str | int | None) -> EventSeverity:
    """Normalize raw values and legacy alert levels into event severity."""

    if isinstance(value, EventSeverity):
        return value
    if value is None:
        return EventSeverity.WATCH
    if isinstance(value, int):
        return {
            0: EventSeverity.INFO,
            1: EventSeverity.CRITICAL,
            2: EventSeverity.IMPORTANT,
            3: EventSeverity.WATCH,
        }.get(value, EventSeverity.WATCH)

    normalized = str(value).strip().lower()
    aliases = {
        "normal": EventSeverity.WATCH,
        "low": EventSeverity.INFO,
        "medium": EventSeverity.WATCH,
        "high": EventSeverity.IMPORTANT,
        "urgent": EventSeverity.CRITICAL,
        "critical": EventSeverity.CRITICAL,
        "important": EventSeverity.IMPORTANT,
        "watch": EventSeverity.WATCH,
        "info": EventSeverity.INFO,
    }
    return aliases.get(normalized, EventSeverity.WATCH)


def severity_rank(severity: EventSeverity | str | int | None) -> int:
    """Return an integer rank for comparing severities."""

    return _SEVERITY_RANK[normalize_severity(severity)]


def max_severity(*values: EventSeverity | str | int | None) -> EventSeverity:
    """Return the highest severity from a sequence of values."""

    severities = [normalize_severity(value) for value in values]
    return max(severities, key=lambda item: _SEVERITY_RANK[item])


def severity_from_percent_change(
    change_pct: float | int | None,
    *,
    watch_pct: float = 2.0,
    important_pct: float = 5.0,
    critical_pct: float = 8.0,
) -> EventSeverity:
    """Classify severity from absolute percentage change."""

    cleaned = abs(_clean_float(change_pct) or 0.0)
    if cleaned >= critical_pct:
        return EventSeverity.CRITICAL
    if cleaned >= important_pct:
        return EventSeverity.IMPORTANT
    if cleaned >= watch_pct:
        return EventSeverity.WATCH
    return EventSeverity.INFO


def severity_from_volume_ratio(
    ratio: float | int | None,
    *,
    watch_ratio: float = 2.0,
    important_ratio: float = 3.0,
    critical_ratio: float = 5.0,
) -> EventSeverity:
    """Classify severity from volume ratio."""

    cleaned = _clean_float(ratio) or 0.0
    if cleaned >= critical_ratio:
        return EventSeverity.CRITICAL
    if cleaned >= important_ratio:
        return EventSeverity.IMPORTANT
    if cleaned >= watch_ratio:
        return EventSeverity.WATCH
    return EventSeverity.INFO


def severity_from_abs_amount(
    amount: float | int | None,
    *,
    watch_amount: float = 100_000_000.0,
    important_amount: float = 300_000_000.0,
    critical_amount: float = 1_000_000_000.0,
) -> EventSeverity:
    """Classify severity from absolute RMB amount."""

    cleaned = abs(_clean_float(amount) or 0.0)
    if cleaned >= critical_amount:
        return EventSeverity.CRITICAL
    if cleaned >= important_amount:
        return EventSeverity.IMPORTANT
    if cleaned >= watch_amount:
        return EventSeverity.WATCH
    return EventSeverity.INFO


def normalize_quality_level(value: DataQualityLevel | str | None) -> DataQualityLevel:
    """Normalize a data quality label."""

    if isinstance(value, DataQualityLevel):
        return value
    if value is None:
        return DataQualityLevel.UNKNOWN
    return _QUALITY_ALIASES.get(str(value).strip().lower(), DataQualityLevel.UNKNOWN)


def quality_rank(level: DataQualityLevel | str | None) -> int:
    """Return a rank where higher means worse quality."""

    return _QUALITY_RANK[normalize_quality_level(level)]


def coerce_datetime(value: Any) -> datetime | None:
    """Coerce common timestamp values into timezone-aware datetimes."""

    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        cleaned = _clean_float(value)
        if cleaned is None:
            return None
        return datetime.fromtimestamp(cleaned, tz=timezone.utc)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        if text.endswith("Z"):
            text = f"{text[:-1]}+00:00"
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=timezone.utc)
        return parsed
    return None


def _json_ready(value: Any) -> JSONValue:
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
    if is_dataclass(value):
        return _json_ready(asdict(cast(Any, value)))
    if isinstance(value, Mapping):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)


def _json_ready_dict(value: Mapping[str, Any]) -> dict[str, JSONValue]:
    return {str(key): _json_ready(item) for key, item in value.items()}


def _clean_optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_text(value: Any, default: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _clean_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        cleaned = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(cleaned):
        return None
    return cleaned


def _clamp_float(value: Any, lower: float, upper: float) -> float:
    cleaned = _clean_float(value)
    if cleaned is None:
        return lower
    return min(max(cleaned, lower), upper)


def _dedupe_text_tuple(values: Sequence[Any]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = str(value).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return tuple(result)
