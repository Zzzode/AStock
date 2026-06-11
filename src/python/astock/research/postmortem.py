"""Structured postmortem packets for failed or completed research theses."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class PostmortemRootCause(StrEnum):
    """Primary root-cause category for a thesis review."""

    DATA_QUALITY = "data_quality"
    LOGIC_ERROR = "logic_error"
    TIMING = "timing"
    RISK_ASSUMPTION = "risk_assumption"
    CATALYST_MISS = "catalyst_miss"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ResearchPostmortem:
    """Counterfactual review packet for one research thesis."""

    entry_id: str
    outcome: str
    root_cause: PostmortemRootCause = PostmortemRootCause.UNKNOWN
    expected: str = ""
    actual: str = ""
    error_analysis: str = ""
    lessons: tuple[str, ...] = ()
    evidence: Mapping[str, Any] = field(default_factory=dict)
    reviewed_at: datetime = field(default_factory=datetime.now)
    postmortem_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "entry_id", _clean_text(self.entry_id))
        object.__setattr__(self, "outcome", _clean_text(self.outcome))
        object.__setattr__(self, "root_cause", _parse_root_cause(self.root_cause))
        object.__setattr__(self, "expected", _clean_text(self.expected))
        object.__setattr__(self, "actual", _clean_text(self.actual))
        object.__setattr__(self, "error_analysis", _clean_text(self.error_analysis))
        object.__setattr__(self, "lessons", _dedupe_text_tuple(self.lessons))
        if not self.postmortem_id:
            object.__setattr__(self, "postmortem_id", make_postmortem_id(self))

    def to_dict(self) -> dict[str, Any]:
        return {
            "postmortem_id": self.postmortem_id,
            "entry_id": self.entry_id,
            "outcome": self.outcome,
            "root_cause": self.root_cause.value,
            "expected": self.expected,
            "actual": self.actual,
            "error_analysis": self.error_analysis,
            "lessons": list(self.lessons),
            "evidence": dict(self.evidence),
            "reviewed_at": self.reviewed_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ResearchPostmortem":
        return cls(
            postmortem_id=str(data.get("postmortem_id", "")),
            entry_id=str(data.get("entry_id", "")),
            outcome=str(data.get("outcome", "")),
            root_cause=_parse_root_cause(data.get("root_cause")),
            expected=str(data.get("expected", "")),
            actual=str(data.get("actual", "")),
            error_analysis=str(data.get("error_analysis", "")),
            lessons=_dedupe_text_tuple(_sequence_from_value(data.get("lessons"))),
            evidence=(
                dict(data.get("evidence", {}))
                if isinstance(data.get("evidence"), Mapping)
                else {}
            ),
            reviewed_at=datetime.fromisoformat(str(data["reviewed_at"])),
        )


def make_postmortem_id(postmortem: ResearchPostmortem) -> str:
    """Create a stable postmortem ID from core review fields."""
    seed = "|".join(
        [
            postmortem.entry_id,
            postmortem.outcome,
            postmortem.root_cause.value,
            postmortem.reviewed_at.isoformat(),
        ]
    )
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"postmortem-{postmortem.reviewed_at.strftime('%Y%m%d')}-{digest}"


def _parse_root_cause(value: Any) -> PostmortemRootCause:
    if isinstance(value, PostmortemRootCause):
        return value
    try:
        return PostmortemRootCause(str(value))
    except ValueError:
        return PostmortemRootCause.UNKNOWN


def _clean_text(value: Any) -> str:
    return str(value or "").strip()


def _dedupe_text_tuple(values: Sequence[Any]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        text = _clean_text(value)
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return tuple(result)


def _sequence_from_value(value: Any) -> tuple[Any, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(value)
    return (value,)
