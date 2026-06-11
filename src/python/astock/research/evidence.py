"""Research evidence packet models.

Evidence packets are JSON-serializable containers for the material that supports
or challenges a research thesis. They intentionally avoid storage dependencies
so agents can attach them to research ledgers, reports, and review workflows.
"""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, TypeAlias, cast

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]
JsonDict: TypeAlias = dict[str, JsonValue]

EVIDENCE_SCHEMA_VERSION = "research_evidence.v1"


class EvidenceStance(str, Enum):
    """Directional effect of an evidence item on a thesis."""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MIXED = "mixed"
    NEUTRAL = "neutral"
    REVIEW_REQUIRED = "review_required"

    @classmethod
    def parse(cls, value: "EvidenceStance | str | None") -> "EvidenceStance":
        """Parse a stance from enum, string, or empty value."""

        if isinstance(value, cls):
            return value
        if value is None:
            return cls.NEUTRAL
        normalized = str(value).strip().lower()
        aliases = {
            "support": cls.SUPPORTS,
            "positive": cls.SUPPORTS,
            "bullish": cls.SUPPORTS,
            "strengthen": cls.SUPPORTS,
            "strengthened": cls.SUPPORTS,
            "contradict": cls.CONTRADICTS,
            "negative": cls.CONTRADICTS,
            "bearish": cls.CONTRADICTS,
            "weaken": cls.CONTRADICTS,
            "weakened": cls.CONTRADICTS,
            "mixed": cls.MIXED,
            "neutral": cls.NEUTRAL,
            "unchanged": cls.NEUTRAL,
            "review": cls.REVIEW_REQUIRED,
            "review_required": cls.REVIEW_REQUIRED,
            "requires_review": cls.REVIEW_REQUIRED,
        }
        if normalized in aliases:
            return aliases[normalized]
        return cls(normalized)


@dataclass(init=False)
class EvidenceItem:
    """One source-backed evidence item for a research thesis."""

    title: str
    source_refs: tuple[JsonDict, ...]
    collected_at: datetime
    data_quality: JsonDict
    provenance: tuple[JsonDict, ...]
    market_events: tuple[JsonDict, ...]
    notes: tuple[str, ...]
    tags: tuple[str, ...]
    stance: EvidenceStance
    item_type: str
    payload: JsonDict
    item_id: str
    schema_version: str

    def __init__(
        self,
        title: str,
        *,
        source_refs: Mapping[str, object] | Sequence[Mapping[str, object]] = (),
        collected_at: datetime | str | None = None,
        data_quality: Mapping[str, object] | None = None,
        provenance: Mapping[str, object] | Sequence[Mapping[str, object]] = (),
        market_events: Mapping[str, object] | Sequence[Mapping[str, object]] = (),
        notes: str | Sequence[str] = (),
        tags: str | Sequence[str] = (),
        stance: EvidenceStance | str | None = EvidenceStance.NEUTRAL,
        item_type: str = "generic",
        payload: Mapping[str, object] | None = None,
        item_id: str = "",
        schema_version: str = EVIDENCE_SCHEMA_VERSION,
    ) -> None:
        self.title = _clean_text(title, "Untitled evidence")
        self.source_refs = _coerce_mapping_tuple(source_refs)
        self.collected_at = _coerce_datetime(collected_at)
        self.data_quality = _json_ready_dict(data_quality or {})
        self.provenance = _coerce_mapping_tuple(provenance)
        self.market_events = _coerce_mapping_tuple(market_events)
        self.notes = _dedupe_text_tuple(notes)
        self.tags = _dedupe_text_tuple(tags)
        self.stance = EvidenceStance.parse(stance)
        self.item_type = _clean_text(item_type, "generic")
        self.payload = _json_ready_dict(payload or {})
        self.schema_version = _clean_text(schema_version, EVIDENCE_SCHEMA_VERSION)
        self.item_id = (
            item_id.strip()
            if item_id.strip()
            else make_evidence_item_id(
                title=self.title,
                source_refs=self.source_refs,
                collected_at=self.collected_at,
                item_type=self.item_type,
            )
        )

    def to_dict(self) -> JsonDict:
        """Return a JSON-ready dictionary."""

        return {
            "item_id": self.item_id,
            "schema_version": self.schema_version,
            "title": self.title,
            "item_type": self.item_type,
            "source_refs": list(self.source_refs),
            "collected_at": self.collected_at.isoformat(),
            "data_quality": self.data_quality,
            "provenance": list(self.provenance),
            "market_events": list(self.market_events),
            "notes": list(self.notes),
            "tags": list(self.tags),
            "stance": self.stance.value,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "EvidenceItem":
        """Create an evidence item from a mapping."""

        return cls(
            title=_required_str(data, "title"),
            source_refs=_coerce_mapping_input(data.get("source_refs", ())),
            collected_at=_optional_datetime_input(data.get("collected_at")),
            data_quality=_coerce_optional_mapping(data.get("data_quality")),
            provenance=_coerce_mapping_input(data.get("provenance", ())),
            market_events=_coerce_mapping_input(data.get("market_events", ())),
            notes=_coerce_text_input(data.get("notes", ())),
            tags=_coerce_text_input(data.get("tags", ())),
            stance=EvidenceStance.parse(
                _optional_str(data.get("stance")) or EvidenceStance.NEUTRAL
            ),
            item_type=str(data.get("item_type", "generic")),
            payload=_coerce_optional_mapping(data.get("payload")),
            item_id=str(data.get("item_id", "")),
            schema_version=str(data.get("schema_version", EVIDENCE_SCHEMA_VERSION)),
        )

    def to_json(self) -> str:
        """Serialize this item to deterministic JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "EvidenceItem":
        """Deserialize an evidence item from JSON."""

        data = json.loads(payload)
        if not isinstance(data, Mapping):
            raise ValueError("Evidence item JSON payload must be an object")
        return cls.from_dict(cast(Mapping[str, object], data))


@dataclass(init=False)
class EvidencePacket:
    """Evidence package attached to a research thesis or review cycle."""

    title: str
    targets: tuple[str, ...]
    collected_at: datetime
    source_refs: tuple[JsonDict, ...]
    data_quality: JsonDict
    provenance: tuple[JsonDict, ...]
    market_events: tuple[JsonDict, ...]
    notes: tuple[str, ...]
    tags: tuple[str, ...]
    items: tuple[EvidenceItem, ...]
    metadata: JsonDict
    packet_id: str
    schema_version: str

    def __init__(
        self,
        title: str,
        *,
        targets: str | Sequence[str] = (),
        collected_at: datetime | str | None = None,
        source_refs: Mapping[str, object] | Sequence[Mapping[str, object]] = (),
        data_quality: Mapping[str, object] | None = None,
        provenance: Mapping[str, object] | Sequence[Mapping[str, object]] = (),
        market_events: Mapping[str, object] | Sequence[Mapping[str, object]] = (),
        notes: str | Sequence[str] = (),
        tags: str | Sequence[str] = (),
        items: Sequence[EvidenceItem | Mapping[str, object]] = (),
        metadata: Mapping[str, object] | None = None,
        packet_id: str = "",
        schema_version: str = EVIDENCE_SCHEMA_VERSION,
    ) -> None:
        self.title = _clean_text(title, "Untitled evidence packet")
        self.targets = _dedupe_text_tuple(targets)
        self.collected_at = _coerce_datetime(collected_at)
        self.source_refs = _coerce_mapping_tuple(source_refs)
        self.data_quality = _json_ready_dict(data_quality or {})
        self.provenance = _coerce_mapping_tuple(provenance)
        self.market_events = _coerce_mapping_tuple(market_events)
        self.notes = _dedupe_text_tuple(notes)
        self.tags = _dedupe_text_tuple(tags)
        self.items = tuple(_coerce_evidence_item(item) for item in items)
        self.metadata = _json_ready_dict(metadata or {})
        self.schema_version = _clean_text(schema_version, EVIDENCE_SCHEMA_VERSION)
        self.packet_id = (
            packet_id.strip()
            if packet_id.strip()
            else make_evidence_packet_id(
                title=self.title,
                targets=self.targets,
                collected_at=self.collected_at,
            )
        )

    @property
    def all_source_refs(self) -> tuple[JsonDict, ...]:
        """Return packet and item source refs with deterministic de-duplication."""

        return _dedupe_json_dicts(
            (
                *self.source_refs,
                *(ref for item in self.items for ref in item.source_refs),
            )
        )

    @property
    def all_market_events(self) -> tuple[JsonDict, ...]:
        """Return packet and item market events with deterministic de-duplication."""

        return _dedupe_json_dicts(
            (
                *self.market_events,
                *(event for item in self.items for event in item.market_events),
            )
        )

    def to_dict(self) -> JsonDict:
        """Return a JSON-ready dictionary."""

        return {
            "packet_id": self.packet_id,
            "schema_version": self.schema_version,
            "title": self.title,
            "targets": list(self.targets),
            "collected_at": self.collected_at.isoformat(),
            "source_refs": list(self.source_refs),
            "data_quality": self.data_quality,
            "provenance": list(self.provenance),
            "market_events": list(self.market_events),
            "notes": list(self.notes),
            "tags": list(self.tags),
            "items": [item.to_dict() for item in self.items],
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "EvidencePacket":
        """Create an evidence packet from a mapping."""

        raw_items = data.get("items", data.get("evidence_items", ()))
        return cls(
            title=_required_str(data, "title"),
            targets=_coerce_text_input(data.get("targets", ())),
            collected_at=_optional_datetime_input(data.get("collected_at")),
            source_refs=_coerce_mapping_input(data.get("source_refs", ())),
            data_quality=_coerce_optional_mapping(data.get("data_quality")),
            provenance=_coerce_mapping_input(data.get("provenance", ())),
            market_events=_coerce_mapping_input(data.get("market_events", ())),
            notes=_coerce_text_input(data.get("notes", ())),
            tags=_coerce_text_input(data.get("tags", ())),
            items=_coerce_item_sequence(raw_items),
            metadata=_coerce_optional_mapping(data.get("metadata")),
            packet_id=str(data.get("packet_id", "")),
            schema_version=str(data.get("schema_version", EVIDENCE_SCHEMA_VERSION)),
        )

    def to_json(self) -> str:
        """Serialize this packet to deterministic JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "EvidencePacket":
        """Deserialize an evidence packet from JSON."""

        data = json.loads(payload)
        if not isinstance(data, Mapping):
            raise ValueError("Evidence packet JSON payload must be an object")
        return cls.from_dict(cast(Mapping[str, object], data))


def make_evidence_item_id(
    *,
    title: str,
    source_refs: Sequence[Mapping[str, object]],
    collected_at: datetime,
    item_type: str = "generic",
) -> str:
    """Build a deterministic ID for an evidence item."""

    identity = {
        "title": _clean_text(title, "Untitled evidence"),
        "item_type": _clean_text(item_type, "generic"),
        "source_refs": [_json_ready_dict(ref) for ref in source_refs],
        "collected_at": _coerce_datetime(collected_at).isoformat(),
    }
    digest = _stable_digest(identity, length=20)
    return f"evid_{digest}"


def make_evidence_packet_id(
    *,
    title: str,
    targets: Sequence[str],
    collected_at: datetime,
) -> str:
    """Build a deterministic ID for an evidence packet."""

    identity = {
        "title": _clean_text(title, "Untitled evidence packet"),
        "targets": sorted(_dedupe_text_tuple(targets)),
        "collected_at": _coerce_datetime(collected_at).isoformat(),
    }
    digest = _stable_digest(identity, length=20)
    return f"epkt_{digest}"


def _stable_digest(value: object, *, length: int) -> str:
    raw = json.dumps(_json_ready(value), ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def _coerce_evidence_item(
    value: EvidenceItem | Mapping[str, object],
) -> EvidenceItem:
    if isinstance(value, EvidenceItem):
        return value
    if isinstance(value, Mapping):
        return EvidenceItem.from_dict(value)
    raise TypeError(f"Unsupported evidence item type: {type(value).__name__}")


def _coerce_item_sequence(
    value: object,
) -> tuple[EvidenceItem | Mapping[str, object], ...]:
    if value is None:
        return ()
    if isinstance(value, (str, bytes, bytearray)):
        raise ValueError("Evidence items must be a sequence of objects")
    if not isinstance(value, Sequence):
        raise ValueError("Evidence items must be a sequence")
    return tuple(cast(Sequence[EvidenceItem | Mapping[str, object]], value))


def _coerce_mapping_input(
    value: object,
) -> Mapping[str, object] | Sequence[Mapping[str, object]]:
    if value is None:
        return ()
    if isinstance(value, Mapping):
        return cast(Mapping[str, object], value)
    if isinstance(value, (str, bytes, bytearray)):
        raise ValueError("Expected a mapping or sequence of mappings")
    if isinstance(value, Sequence):
        return tuple(
            cast(Mapping[str, object], item)
            for item in value
            if isinstance(item, Mapping)
        )
    raise ValueError("Expected a mapping or sequence of mappings")


def _coerce_mapping_tuple(
    value: Mapping[str, object] | Sequence[Mapping[str, object]],
) -> tuple[JsonDict, ...]:
    if isinstance(value, Mapping):
        return (_json_ready_dict(value),)
    if isinstance(value, (str, bytes, bytearray)):
        raise ValueError("Expected a mapping or sequence of mappings")
    return tuple(_json_ready_dict(item) for item in value)


def _coerce_optional_mapping(value: object) -> Mapping[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise ValueError("Expected a mapping")
    return cast(Mapping[str, object], value)


def _coerce_text_input(value: object) -> str | Sequence[str]:
    if value is None:
        return ()
    if isinstance(value, str):
        return value
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item) for item in value)
    raise ValueError("Expected text or a sequence of text")


def _dedupe_text_tuple(values: str | Sequence[str]) -> tuple[str, ...]:
    if isinstance(values, str):
        candidates: Sequence[str] = (values,)
    else:
        candidates = values
    result: list[str] = []
    seen: set[str] = set()
    for value in candidates:
        text = str(value).strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return tuple(result)


def _dedupe_json_dicts(values: Sequence[JsonDict]) -> tuple[JsonDict, ...]:
    result: list[JsonDict] = []
    seen: set[str] = set()
    for value in values:
        key = json.dumps(value, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            result.append(value)
            seen.add(key)
    return tuple(result)


def _coerce_datetime(value: datetime | str | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = value.strip()
    if not text:
        raise ValueError("Timestamp must not be empty")
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _optional_datetime_input(value: object) -> datetime | str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return str(value)


def _required_str(data: Mapping[str, object], key: str) -> str:
    value = data.get(key)
    if value is None:
        raise ValueError(f"Evidence payload requires {key}")
    return str(value)


def _optional_str(value: object) -> str | None:
    if value is None:
        return None
    normalized = str(value).strip()
    return normalized or None


def _clean_text(value: object, default: str) -> str:
    text = str(value).strip() if value is not None else ""
    return text or default


def _json_ready_dict(data: Mapping[str, object]) -> JsonDict:
    return {str(key): _json_ready(value) for key, value in data.items()}


def _json_ready(value: object) -> JsonValue:
    to_dict_method = getattr(value, "to_dict", None)
    if callable(to_dict_method):
        return _json_ready(to_dict_method())
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, datetime):
        return _coerce_datetime(value).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if is_dataclass(value) and not isinstance(value, type):
        return _json_ready(asdict(cast(Any, value)))
    if isinstance(value, Mapping):
        return _json_ready_dict(cast(Mapping[str, object], value))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)
