"""Research opportunity ledger.

The ledger stores structured investment research hypotheses for agents.
It is intentionally deterministic and JSON-backed so it can be used by
skills without introducing a database migration before the schema stabilizes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional


class ResearchStatus(str, Enum):
    """Lifecycle state for a research opportunity."""

    ACTIVE = "active"
    MONITORING = "monitoring"
    INVALIDATED = "invalidated"
    CLOSED = "closed"
    ARCHIVED = "archived"


@dataclass
class ResearchTrigger:
    """Condition that should be monitored after a research conclusion."""

    name: str
    condition: str
    direction: str = "watch"
    metric: Optional[str] = None
    threshold: Optional[float] = None
    source: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "condition": self.condition,
            "direction": self.direction,
            "metric": self.metric,
            "threshold": self.threshold,
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchTrigger":
        return cls(
            name=str(data["name"]),
            condition=str(data["condition"]),
            direction=str(data.get("direction", "watch")),
            metric=data.get("metric"),
            threshold=data.get("threshold"),
            source=data.get("source"),
        )


@dataclass
class ResearchObservation:
    """Follow-up evidence or review attached to a research entry."""

    observation_type: str
    note: str
    observed_at: datetime = field(default_factory=datetime.now)
    evidence: dict[str, Any] = field(default_factory=dict)
    status_after: Optional[ResearchStatus] = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_type": self.observation_type,
            "note": self.note,
            "observed_at": self.observed_at.isoformat(),
            "evidence": self.evidence,
            "status_after": self.status_after.value if self.status_after else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchObservation":
        status_after = data.get("status_after")
        return cls(
            observation_type=str(data["observation_type"]),
            note=str(data["note"]),
            observed_at=datetime.fromisoformat(data["observed_at"]),
            evidence=dict(data.get("evidence", {})),
            status_after=ResearchStatus(status_after) if status_after else None,
        )


@dataclass
class ResearchEntry:
    """Structured opportunity thesis that agents can track over time."""

    title: str
    thesis: str
    targets: list[str]
    target_type: str = "stock"
    status: ResearchStatus = ResearchStatus.ACTIVE
    catalysts: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    monitoring_triggers: list[ResearchTrigger] = field(default_factory=list)
    invalidation_conditions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    data_quality: dict[str, Any] = field(default_factory=dict)
    source_refs: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    observations: list[ResearchObservation] = field(default_factory=list)
    created_by: str = "agent"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    entry_id: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.targets:
            raise ValueError("ResearchEntry requires at least one target")
        if self.entry_id is None:
            self.entry_id = make_research_id(
                targets=self.targets,
                title=self.title,
                created_at=self.created_at,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "title": self.title,
            "thesis": self.thesis,
            "targets": self.targets,
            "target_type": self.target_type,
            "status": self.status.value,
            "catalysts": self.catalysts,
            "risks": self.risks,
            "monitoring_triggers": [
                trigger.to_dict() for trigger in self.monitoring_triggers
            ],
            "invalidation_conditions": self.invalidation_conditions,
            "tags": self.tags,
            "data_quality": self.data_quality,
            "source_refs": self.source_refs,
            "metadata": self.metadata,
            "observations": [
                observation.to_dict() for observation in self.observations
            ],
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResearchEntry":
        return cls(
            entry_id=data.get("entry_id"),
            title=str(data["title"]),
            thesis=str(data["thesis"]),
            targets=list(data["targets"]),
            target_type=str(data.get("target_type", "stock")),
            status=ResearchStatus(data.get("status", ResearchStatus.ACTIVE.value)),
            catalysts=list(data.get("catalysts", [])),
            risks=list(data.get("risks", [])),
            monitoring_triggers=[
                ResearchTrigger.from_dict(item)
                for item in data.get("monitoring_triggers", [])
            ],
            invalidation_conditions=list(data.get("invalidation_conditions", [])),
            tags=list(data.get("tags", [])),
            data_quality=dict(data.get("data_quality", {})),
            source_refs=list(data.get("source_refs", [])),
            metadata=dict(data.get("metadata", {})),
            observations=[
                ResearchObservation.from_dict(item)
                for item in data.get("observations", [])
            ],
            created_by=str(data.get("created_by", "agent")),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )

    def record_observation(self, observation: ResearchObservation) -> None:
        """Attach a follow-up observation and optionally update status."""
        self.observations.append(observation)
        if observation.status_after is not None:
            self.status = observation.status_after
        self.updated_at = max(datetime.now(), observation.observed_at)


@dataclass(frozen=True)
class ResearchLedgerIndex:
    """Lightweight query index and lifecycle summary for the research ledger."""

    generated_at: datetime
    entry_count: int
    status_counts: dict[str, int]
    target_counts: dict[str, int]
    tag_counts: dict[str, int]
    target_type_counts: dict[str, int]
    observation_type_counts: dict[str, int]
    entries: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "research-ledger-index.v1",
            "generated_at": self.generated_at.isoformat(),
            "entry_count": self.entry_count,
            "status_counts": self.status_counts,
            "target_counts": self.target_counts,
            "tag_counts": self.tag_counts,
            "target_type_counts": self.target_type_counts,
            "observation_type_counts": self.observation_type_counts,
            "entries": self.entries,
        }


class ResearchLedger:
    """JSON-backed research opportunity ledger."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or Path("data/research-ledger.json")
        self._entries: dict[str, ResearchEntry] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        if not self.data_path.exists():
            self._entries = {}
            return
        try:
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
            self._entries = {
                str(item["entry_id"]): ResearchEntry.from_dict(item)
                for item in raw.get("entries", [])
            }
        except Exception:
            self._entries = {}

    def _save(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "research-ledger.v1",
            "updated_at": datetime.now().isoformat(),
            "entries": [
                entry.to_dict()
                for entry in sorted(
                    self._entries.values(),
                    key=lambda item: item.updated_at,
                    reverse=True,
                )
            ],
        }
        self.data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def create(self, entry: ResearchEntry, *, overwrite: bool = False) -> ResearchEntry:
        """Create a ledger entry."""
        self._ensure_loaded()
        if entry.entry_id is None:
            raise ValueError("Research entry must have an ID")
        if not overwrite and entry.entry_id in self._entries:
            raise ValueError(f"Research entry already exists: {entry.entry_id}")
        self._entries[entry.entry_id] = entry
        self._save()
        return entry

    def get(self, entry_id: str) -> Optional[ResearchEntry]:
        """Get one entry by ID."""
        self._ensure_loaded()
        return self._entries.get(entry_id)

    def list_entries(
        self,
        *,
        status: Optional[ResearchStatus] = None,
        target: Optional[str] = None,
        tag: Optional[str] = None,
        limit: int = 50,
    ) -> list[ResearchEntry]:
        """List entries by optional filters."""
        self._ensure_loaded()
        entries = list(self._entries.values())
        if status is not None:
            entries = [entry for entry in entries if entry.status == status]
        if target is not None:
            entries = [entry for entry in entries if target in entry.targets]
        if tag is not None:
            entries = [entry for entry in entries if tag in entry.tags]
        entries.sort(key=lambda entry: entry.updated_at, reverse=True)
        return entries[:limit]

    def query_entries(
        self,
        *,
        statuses: Optional[list[ResearchStatus]] = None,
        targets: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
        text: Optional[str] = None,
        limit: int = 50,
    ) -> list[ResearchEntry]:
        """Query entries using lightweight in-memory indexes and text matching."""
        self._ensure_loaded()
        entries = list(self._entries.values())
        status_filter = set(statuses or [])
        target_filter = {_normalize_text(target) for target in targets or []}
        tag_filter = {_normalize_text(tag) for tag in tags or []}
        text_filter = _normalize_text(text)

        matched: list[ResearchEntry] = []
        for entry in entries:
            if status_filter and entry.status not in status_filter:
                continue
            entry_targets = {_normalize_text(target) for target in entry.targets}
            if target_filter and not target_filter.intersection(entry_targets):
                continue
            entry_tags = {_normalize_text(tag) for tag in entry.tags}
            if tag_filter and not tag_filter.issubset(entry_tags):
                continue
            if text_filter and text_filter not in _entry_search_text(entry):
                continue
            matched.append(entry)

        matched.sort(key=lambda entry: entry.updated_at, reverse=True)
        return matched[:limit]

    def build_index(self) -> ResearchLedgerIndex:
        """Build a JSON-ready lightweight index for agent planning."""
        self._ensure_loaded()
        entries = sorted(
            self._entries.values(),
            key=lambda entry: entry.updated_at,
            reverse=True,
        )
        status_counts: dict[str, int] = {}
        target_counts: dict[str, int] = {}
        tag_counts: dict[str, int] = {}
        target_type_counts: dict[str, int] = {}
        observation_type_counts: dict[str, int] = {}

        cards: list[dict[str, Any]] = []
        for entry in entries:
            _increment(status_counts, entry.status.value)
            _increment(target_type_counts, entry.target_type)
            for target in entry.targets:
                _increment(target_counts, target)
            for tag in entry.tags:
                _increment(tag_counts, tag)
            for observation in entry.observations:
                _increment(observation_type_counts, observation.observation_type)
            cards.append(_entry_index_card(entry))

        return ResearchLedgerIndex(
            generated_at=datetime.now(),
            entry_count=len(entries),
            status_counts=status_counts,
            target_counts=target_counts,
            tag_counts=tag_counts,
            target_type_counts=target_type_counts,
            observation_type_counts=observation_type_counts,
            entries=cards,
        )

    def find_duplicate_candidates(
        self,
        *,
        targets: list[str],
        title: Optional[str] = None,
        tags: Optional[list[str]] = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Find likely duplicate or overlapping research entries."""
        self._ensure_loaded()
        target_set = {_normalize_text(target) for target in targets}
        tag_set = {_normalize_text(tag) for tag in tags or []}
        normalized_title = _normalize_text(title)
        candidates: list[dict[str, Any]] = []

        for entry in self._entries.values():
            entry_targets = {_normalize_text(target) for target in entry.targets}
            target_overlap = sorted(target_set.intersection(entry_targets))
            entry_tags = {_normalize_text(tag) for tag in entry.tags}
            tag_overlap = sorted(tag_set.intersection(entry_tags))
            title_match = bool(
                normalized_title and normalized_title == _normalize_text(entry.title)
            )
            title_token_overlap = _title_token_overlap(normalized_title, entry.title)
            score = (
                len(target_overlap) * 3
                + len(tag_overlap)
                + (3 if title_match else 0)
                + title_token_overlap
            )
            if score <= 0:
                continue
            candidates.append(
                {
                    "score": score,
                    "entry": _entry_index_card(entry),
                    "overlap": {
                        "targets": target_overlap,
                        "tags": tag_overlap,
                        "title_match": title_match,
                        "title_token_overlap": title_token_overlap,
                    },
                }
            )

        candidates.sort(
            key=lambda item: (
                int(item["score"]),
                str(item["entry"]["updated_at"]),
            ),
            reverse=True,
        )
        return candidates[:limit]

    def record_observation(
        self,
        entry_id: str,
        observation: ResearchObservation,
    ) -> ResearchEntry:
        """Attach a follow-up observation to an existing entry."""
        self._ensure_loaded()
        entry = self._entries.get(entry_id)
        if entry is None:
            raise KeyError(f"Research entry not found: {entry_id}")
        entry.record_observation(observation)
        self._save()
        return entry

    def update_status(self, entry_id: str, status: ResearchStatus) -> ResearchEntry:
        """Update the lifecycle status for an entry."""
        self._ensure_loaded()
        entry = self._entries.get(entry_id)
        if entry is None:
            raise KeyError(f"Research entry not found: {entry_id}")
        entry.status = status
        entry.updated_at = datetime.now()
        self._save()
        return entry


def make_research_id(
    *,
    targets: list[str],
    title: str,
    created_at: datetime,
) -> str:
    """Build a stable short ID for a research entry."""
    seed = "|".join(sorted(targets)) + "|" + title + "|" + created_at.isoformat()
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"research-{created_at.strftime('%Y%m%d')}-{digest}"


def _entry_index_card(entry: ResearchEntry) -> dict[str, Any]:
    return {
        "entry_id": entry.entry_id,
        "title": entry.title,
        "targets": list(entry.targets),
        "target_type": entry.target_type,
        "status": entry.status.value,
        "tags": list(entry.tags),
        "catalyst_count": len(entry.catalysts),
        "risk_count": len(entry.risks),
        "trigger_count": len(entry.monitoring_triggers),
        "observation_count": len(entry.observations),
        "created_at": entry.created_at.isoformat(),
        "updated_at": entry.updated_at.isoformat(),
    }


def _entry_search_text(entry: ResearchEntry) -> str:
    parts = [
        entry.title,
        entry.thesis,
        entry.target_type,
        *entry.targets,
        *entry.catalysts,
        *entry.risks,
        *entry.invalidation_conditions,
        *entry.tags,
    ]
    return " ".join(_normalize_text(part) for part in parts)


def _normalize_text(value: object) -> str:
    return str(value or "").strip().lower()


def _increment(counter: dict[str, int], key: str) -> None:
    normalized = str(key or "").strip()
    if not normalized:
        return
    counter[normalized] = counter.get(normalized, 0) + 1


def _title_token_overlap(query_title: str, existing_title: str) -> int:
    if not query_title:
        return 0
    query_tokens = {token for token in query_title.split() if len(token) >= 3}
    existing_tokens = {
        token for token in _normalize_text(existing_title).split() if len(token) >= 3
    }
    return len(query_tokens.intersection(existing_tokens))
