"""Deterministic thesis review helpers for research ledger entries."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, cast

from .evidence import EvidenceItem, EvidencePacket, EvidenceStance, JsonDict, JsonValue
from .ledger import ResearchEntry, ResearchObservation, ResearchStatus


class ThesisReviewClassification(str, Enum):
    """Review classification for a research thesis."""

    UNCHANGED = "unchanged"
    STRENGTHENED = "strengthened"
    WEAKENED = "weakened"
    INVALIDATED = "invalidated"
    REVIEW_REQUIRED = "review_required"


def _now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass
class ThesisReview:
    """Structured output of a deterministic thesis review."""

    entry_id: str
    classification: ThesisReviewClassification
    summary: str
    reviewed_at: datetime = field(default_factory=_now)
    reasons: list[str] = field(default_factory=list)
    matched_invalidation_conditions: list[str] = field(default_factory=list)
    supporting_evidence_ids: list[str] = field(default_factory=list)
    contradicting_evidence_ids: list[str] = field(default_factory=list)
    review_required_evidence_ids: list[str] = field(default_factory=list)
    evidence_packet_ids: list[str] = field(default_factory=list)
    observation_count: int = 0
    suggested_status: Optional[ResearchStatus] = None
    metadata: JsonDict = field(default_factory=dict)

    def to_dict(self) -> JsonDict:
        """Return a JSON-ready dictionary."""

        return {
            "entry_id": self.entry_id,
            "classification": self.classification.value,
            "summary": self.summary,
            "reviewed_at": _coerce_datetime(self.reviewed_at).isoformat(),
            "reasons": list(self.reasons),
            "matched_invalidation_conditions": list(
                self.matched_invalidation_conditions
            ),
            "supporting_evidence_ids": list(self.supporting_evidence_ids),
            "contradicting_evidence_ids": list(self.contradicting_evidence_ids),
            "review_required_evidence_ids": list(self.review_required_evidence_ids),
            "evidence_packet_ids": list(self.evidence_packet_ids),
            "observation_count": self.observation_count,
            "suggested_status": (
                self.suggested_status.value if self.suggested_status else None
            ),
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "ThesisReview":
        """Create a thesis review from a mapping."""

        suggested_status = data.get("suggested_status")
        return cls(
            entry_id=str(data["entry_id"]),
            classification=ThesisReviewClassification(str(data["classification"])),
            summary=str(data["summary"]),
            reviewed_at=_coerce_datetime(data.get("reviewed_at")),
            reasons=_string_list(data.get("reasons", ())),
            matched_invalidation_conditions=_string_list(
                data.get("matched_invalidation_conditions", ())
            ),
            supporting_evidence_ids=_string_list(
                data.get("supporting_evidence_ids", ())
            ),
            contradicting_evidence_ids=_string_list(
                data.get("contradicting_evidence_ids", ())
            ),
            review_required_evidence_ids=_string_list(
                data.get("review_required_evidence_ids", ())
            ),
            evidence_packet_ids=_string_list(data.get("evidence_packet_ids", ())),
            observation_count=_int_value(data.get("observation_count", 0)),
            suggested_status=(
                ResearchStatus(str(suggested_status)) if suggested_status else None
            ),
            metadata=_json_ready_dict(_mapping_or_empty(data.get("metadata"))),
        )

    def to_json(self) -> str:
        """Serialize this review to deterministic JSON."""

        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True)

    @classmethod
    def from_json(cls, payload: str) -> "ThesisReview":
        """Deserialize a thesis review from JSON."""

        data = json.loads(payload)
        if not isinstance(data, Mapping):
            raise ValueError("Thesis review JSON payload must be an object")
        return cls.from_dict(cast(Mapping[str, object], data))


def review_thesis(
    entry: ResearchEntry,
    *,
    evidence_packets: Sequence[EvidencePacket | Mapping[str, object]] = (),
    evidence_items: Sequence[EvidenceItem | Mapping[str, object]] = (),
    observations: Sequence[ResearchObservation | Mapping[str, object]] | None = None,
    reviewed_at: datetime | str | None = None,
) -> ThesisReview:
    """Classify whether evidence changes a research entry's thesis.

    The helper is intentionally rule-based. It only changes classification when
    evidence or observations provide explicit structured signals.
    """

    packets = tuple(_coerce_packet(packet) for packet in evidence_packets)
    standalone_items = tuple(_coerce_item(item) for item in evidence_items)
    review_observations = _coerce_observations(
        entry.observations if observations is None else observations
    )
    all_items = (
        *standalone_items,
        *(item for packet in packets for item in packet.items),
    )

    support_ids: list[str] = []
    contradict_ids: list[str] = []
    review_required_ids: list[str] = []
    matched_conditions: list[str] = []
    reasons: list[str] = []

    if entry.status == ResearchStatus.INVALIDATED:
        reasons.append("Research entry status is already invalidated.")

    for observation in review_observations:
        observation_id = f"observation:{observation.observed_at.isoformat()}"
        if observation.status_after == ResearchStatus.INVALIDATED:
            reasons.append("Observation set status_after to invalidated.")
            matched_conditions.append("observation_status_after")
        evidence = observation.evidence
        stance = _extract_stance(evidence)
        if stance == EvidenceStance.SUPPORTS:
            support_ids.append(observation_id)
        elif stance == EvidenceStance.CONTRADICTS:
            contradict_ids.append(observation_id)
        elif stance in {EvidenceStance.MIXED, EvidenceStance.REVIEW_REQUIRED}:
            review_required_ids.append(observation_id)
        if _truthy_flag(evidence, _INVALIDATION_FLAGS):
            reasons.append("Observation evidence explicitly triggered invalidation.")
            matched_conditions.append("observation_invalidation_flag")
        if _truthy_flag(evidence, _REVIEW_FLAGS):
            review_required_ids.append(observation_id)
        matched_conditions.extend(
            _matched_conditions(entry.invalidation_conditions, _text_blob(evidence))
        )

    for packet in packets:
        if _has_degraded_quality(packet.data_quality) or any(
            _has_degraded_quality(record) for record in packet.provenance
        ):
            review_required_ids.append(packet.packet_id)
            reasons.append(
                f"Evidence packet has degraded provenance: {packet.packet_id}."
            )
        if _truthy_flag(packet.metadata, _INVALIDATION_FLAGS):
            matched_conditions.append(f"packet:{packet.packet_id}")
            reasons.append(
                f"Evidence packet triggered invalidation: {packet.packet_id}."
            )
        matched_conditions.extend(
            _matched_conditions(entry.invalidation_conditions, _packet_text(packet))
        )

    for item in all_items:
        if item.stance == EvidenceStance.SUPPORTS:
            support_ids.append(item.item_id)
        elif item.stance == EvidenceStance.CONTRADICTS:
            contradict_ids.append(item.item_id)
        elif item.stance in {EvidenceStance.MIXED, EvidenceStance.REVIEW_REQUIRED}:
            review_required_ids.append(item.item_id)

        if _has_degraded_quality(item.data_quality) or any(
            _has_degraded_quality(record) for record in item.provenance
        ):
            review_required_ids.append(item.item_id)
            reasons.append(f"Evidence item has degraded provenance: {item.item_id}.")

        if _truthy_flag(item.payload, _INVALIDATION_FLAGS):
            matched_conditions.append(f"item:{item.item_id}")
            reasons.append(f"Evidence item triggered invalidation: {item.item_id}.")
        if _truthy_flag(item.payload, _REVIEW_FLAGS):
            review_required_ids.append(item.item_id)

        matched_conditions.extend(
            _matched_conditions(entry.invalidation_conditions, _item_text(item))
        )

    support_ids = _dedupe(support_ids)
    contradict_ids = _dedupe(contradict_ids)
    review_required_ids = _dedupe(review_required_ids)
    matched_conditions = _dedupe(matched_conditions)
    packet_ids = _dedupe([packet.packet_id for packet in packets])

    if entry.status == ResearchStatus.INVALIDATED or matched_conditions:
        classification = ThesisReviewClassification.INVALIDATED
        suggested_status: Optional[ResearchStatus] = ResearchStatus.INVALIDATED
        summary = (
            "Thesis is invalidated by lifecycle status, observations, or evidence."
        )
    elif review_required_ids:
        classification = ThesisReviewClassification.REVIEW_REQUIRED
        suggested_status = None
        summary = "Thesis requires review because evidence is mixed or data quality is degraded."
    elif len(contradict_ids) > len(support_ids):
        classification = ThesisReviewClassification.WEAKENED
        suggested_status = None
        summary = "Thesis is weakened by more contradicting than supporting evidence."
    elif support_ids and len(support_ids) > len(contradict_ids):
        classification = ThesisReviewClassification.STRENGTHENED
        suggested_status = None
        summary = "Thesis is strengthened by supporting evidence."
    else:
        classification = ThesisReviewClassification.UNCHANGED
        suggested_status = None
        summary = "No structured evidence changed the thesis."

    if not reasons:
        reasons.append(summary)
    if support_ids:
        reasons.append(f"Supporting evidence count: {len(support_ids)}.")
    if contradict_ids:
        reasons.append(f"Contradicting evidence count: {len(contradict_ids)}.")

    return ThesisReview(
        entry_id=entry.entry_id or "",
        classification=classification,
        summary=summary,
        reviewed_at=_coerce_datetime(reviewed_at),
        reasons=_dedupe(reasons),
        matched_invalidation_conditions=matched_conditions,
        supporting_evidence_ids=support_ids,
        contradicting_evidence_ids=contradict_ids,
        review_required_evidence_ids=review_required_ids,
        evidence_packet_ids=packet_ids,
        observation_count=len(review_observations),
        suggested_status=suggested_status,
        metadata={
            "target_count": len(entry.targets),
            "evidence_item_count": len(all_items),
            "evidence_packet_count": len(packets),
        },
    )


_INVALIDATION_FLAGS = frozenset(
    {
        "invalidation_triggered",
        "invalidated",
        "thesis_invalidated",
        "triggered_invalidation",
    }
)
_REVIEW_FLAGS = frozenset({"requires_review", "review_required", "manual_review"})
_DEGRADED_QUALITY_VALUES = frozenset(
    {"degraded", "unavailable", "failed", "failure", "error"}
)


def _coerce_packet(value: EvidencePacket | Mapping[str, object]) -> EvidencePacket:
    if isinstance(value, EvidencePacket):
        return value
    if isinstance(value, Mapping):
        return EvidencePacket.from_dict(value)
    raise TypeError(f"Unsupported evidence packet type: {type(value).__name__}")


def _coerce_item(value: EvidenceItem | Mapping[str, object]) -> EvidenceItem:
    if isinstance(value, EvidenceItem):
        return value
    if isinstance(value, Mapping):
        return EvidenceItem.from_dict(value)
    raise TypeError(f"Unsupported evidence item type: {type(value).__name__}")


def _coerce_observations(
    values: Sequence[ResearchObservation | Mapping[str, object]],
) -> tuple[ResearchObservation, ...]:
    observations: list[ResearchObservation] = []
    for value in values:
        if isinstance(value, ResearchObservation):
            observations.append(value)
        elif isinstance(value, Mapping):
            observations.append(
                ResearchObservation.from_dict(cast(dict[str, Any], value))
            )
        else:
            raise TypeError(f"Unsupported observation type: {type(value).__name__}")
    return tuple(observations)


def _extract_stance(data: Mapping[str, Any]) -> EvidenceStance:
    for key in ("stance", "thesis_impact", "impact"):
        raw = data.get(key)
        if raw is not None:
            try:
                return EvidenceStance.parse(str(raw))
            except ValueError:
                return EvidenceStance.NEUTRAL
    return EvidenceStance.NEUTRAL


def _truthy_flag(data: Mapping[str, Any], keys: frozenset[str]) -> bool:
    for key in keys:
        value = data.get(key)
        if isinstance(value, bool) and value:
            return True
        if isinstance(value, str) and value.strip().lower() in {"1", "true", "yes"}:
            return True
    return False


def _has_degraded_quality(data: Mapping[str, Any]) -> bool:
    if not data:
        return False
    ok_value = data.get("ok")
    if ok_value is False:
        return True
    errors = data.get("errors")
    if isinstance(errors, Sequence) and not isinstance(errors, (str, bytes, bytearray)):
        if len(errors) > 0:
            return True
    for key in ("quality_tier", "level", "quality", "data_quality"):
        value = data.get(key)
        if isinstance(value, str) and value.strip().lower() in _DEGRADED_QUALITY_VALUES:
            return True
        if isinstance(value, Mapping) and _has_degraded_quality(value):
            return True
    return any(
        _has_degraded_quality(value)
        for value in data.values()
        if isinstance(value, Mapping)
    )


def _matched_conditions(conditions: Sequence[str], text: str) -> list[str]:
    if not conditions or not text.strip():
        return []
    normalized_text = _normalize_text(text)
    matches: list[str] = []
    for condition in conditions:
        normalized_condition = _normalize_text(condition)
        if not normalized_condition:
            continue
        if normalized_condition in normalized_text:
            matches.append(condition)
            continue
        tokens = [
            token for token in re.split(r"\W+", normalized_condition) if len(token) > 2
        ]
        if len(tokens) >= 3:
            hit_count = sum(1 for token in tokens if token in normalized_text)
            if hit_count >= max(2, round(len(tokens) * 0.6)):
                matches.append(condition)
    return matches


def _item_text(item: EvidenceItem) -> str:
    return " ".join(
        (
            item.title,
            " ".join(item.notes),
            " ".join(item.tags),
            _text_blob(item.payload),
            _text_blob(item.market_events),
        )
    )


def _packet_text(packet: EvidencePacket) -> str:
    return " ".join(
        (
            packet.title,
            " ".join(packet.notes),
            " ".join(packet.tags),
            _text_blob(packet.metadata),
            _text_blob(packet.market_events),
        )
    )


def _text_blob(value: object) -> str:
    return json.dumps(_json_ready(value), ensure_ascii=False, sort_keys=True)


def _normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.casefold()).strip()


def _dedupe(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = value.strip()
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _string_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value]
    raise ValueError("Expected a string or sequence of strings")


def _int_value(value: object) -> int:
    if isinstance(value, bool):
        raise ValueError("Expected an integer, not boolean")
    if isinstance(value, (int, float, str)):
        return int(value)
    raise ValueError("Expected an integer-compatible value")


def _mapping_or_empty(value: object) -> Mapping[str, object]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("Expected a mapping")
    return cast(Mapping[str, object], value)


def _json_ready_dict(data: Mapping[str, object]) -> JsonDict:
    return {str(key): _json_ready(value) for key, value in data.items()}


def _json_ready(value: object) -> JsonValue:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, datetime):
        return _coerce_datetime(value).isoformat()
    if isinstance(value, Mapping):
        return _json_ready_dict(cast(Mapping[str, object], value))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)


def _coerce_datetime(value: datetime | str | object | None) -> datetime:
    if value is None:
        return _now()
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    text = str(value).strip()
    if not text:
        return _now()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
