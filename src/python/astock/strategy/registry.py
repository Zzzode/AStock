"""Append-only local registry for strategy definitions and research runs.

The registry is intentionally small and SQLite-backed.  It records immutable
definition versions, lifecycle transitions, and paper/backtest runs so later
reviews can distinguish a strategy's evidence from a current manual decision.
It never contains credentials or order-routing functionality.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import StrategyAvailability, StrategyDefinition, StrategyLifecycle

_ALLOWED_TRANSITIONS: dict[str, tuple[str, ...]] = {
    StrategyLifecycle.DRAFT.value: (
        StrategyLifecycle.PAPER.value,
        StrategyLifecycle.DISABLED.value,
        StrategyLifecycle.RETIRED.value,
    ),
    StrategyLifecycle.PAPER.value: (
        StrategyLifecycle.REVIEW.value,
        StrategyLifecycle.DISABLED.value,
        StrategyLifecycle.RETIRED.value,
    ),
    StrategyLifecycle.REVIEW.value: (
        StrategyLifecycle.PAPER.value,
        StrategyLifecycle.DISABLED.value,
        StrategyLifecycle.RETIRED.value,
    ),
    StrategyLifecycle.DISABLED.value: (
        StrategyLifecycle.PAPER.value,
        StrategyLifecycle.RETIRED.value,
    ),
    StrategyLifecycle.RETIRED.value: (),
}


class StrategyRegistry:
    """Versioned strategy registry with append-only lifecycle/run evidence."""

    def __init__(self, path: str | Path = "data/strategy-registry.db") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def register_definition(
        self,
        definition: StrategyDefinition | Mapping[str, Any],
        *,
        source_ids: Sequence[str],
        registered_by: str = "agent",
        registered_at: str | datetime | None = None,
    ) -> dict[str, Any]:
        payload = _definition_payload(definition)
        strategy_id = _required_text(payload.get("strategy_id"), "strategy_id")
        version = _required_text(payload.get("version"), "version")
        lifecycle = _validated_lifecycle(payload.get("lifecycle"))
        normalized_sources = _source_ids(source_ids)
        if not normalized_sources:
            raise ValueError(
                "strategy definition requires at least one source identifier"
            )
        timestamp = _timestamp(registered_at)
        fingerprint = _fingerprint(payload)
        with self._connection() as connection:
            current = connection.execute(
                "SELECT fingerprint FROM strategy_definitions WHERE strategy_id=? AND version=?",
                (strategy_id, version),
            ).fetchone()
            if current is not None:
                if str(current[0]) != fingerprint:
                    raise ValueError(
                        "strategy id/version already exists with a different immutable definition"
                    )
                return self.get_definition(strategy_id, version)
            connection.execute(
                "INSERT INTO strategy_definitions(strategy_id, version, lifecycle, definition_json, source_ids_json, fingerprint, registered_at, registered_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    strategy_id,
                    version,
                    lifecycle,
                    _canonical_json(payload),
                    _canonical_json(normalized_sources),
                    fingerprint,
                    timestamp,
                    str(registered_by).strip() or "agent",
                ),
            )
            connection.execute(
                "INSERT INTO strategy_events(strategy_id, version, event_type, from_lifecycle, to_lifecycle, evidence_json, occurred_at, actor) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    strategy_id,
                    version,
                    "registered",
                    None,
                    lifecycle,
                    _canonical_json({"source_ids": normalized_sources}),
                    timestamp,
                    str(registered_by).strip() or "agent",
                ),
            )
        return self.get_definition(strategy_id, version)

    def get_definition(self, strategy_id: str, version: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT lifecycle, definition_json, source_ids_json, fingerprint, registered_at, registered_by FROM strategy_definitions WHERE strategy_id=? AND version=?",
                (str(strategy_id).strip(), str(version).strip()),
            ).fetchone()
        if row is None:
            raise ValueError("strategy definition/version was not found")
        definition = json.loads(str(row[1]))
        definition.update(
            {
                "lifecycle": str(row[0]),
                "source_ids": json.loads(str(row[2])),
                "fingerprint": str(row[3]),
                "registered_at": str(row[4]),
                "registered_by": str(row[5]),
                "research_only": True,
                "no_order_execution": True,
            }
        )
        return definition

    def list_definitions(self, *, lifecycle: str | None = None) -> list[dict[str, Any]]:
        sql = "SELECT strategy_id, version FROM strategy_definitions"
        arguments: tuple[Any, ...] = ()
        if lifecycle is not None:
            sql += " WHERE lifecycle=?"
            arguments = (_validated_lifecycle(lifecycle),)
        sql += " ORDER BY strategy_id, version"
        with self._connection() as connection:
            keys = connection.execute(sql, arguments).fetchall()
        return [self.get_definition(str(key[0]), str(key[1])) for key in keys]

    def transition_lifecycle(
        self,
        strategy_id: str,
        version: str,
        to_lifecycle: str | StrategyLifecycle,
        *,
        evidence: Mapping[str, Any],
        actor: str = "agent",
        occurred_at: str | datetime | None = None,
    ) -> dict[str, Any]:
        target = _validated_lifecycle(to_lifecycle)
        if not isinstance(evidence, Mapping) or not evidence:
            raise ValueError("lifecycle transition requires non-empty evidence")
        evidence_source_ids = _source_ids(_evidence_source_ids(evidence))
        if not evidence_source_ids:
            raise ValueError(
                "lifecycle transition evidence requires at least one source identifier"
            )
        current = self.get_definition(strategy_id, version)
        origin = str(current["lifecycle"])
        if target == origin:
            raise ValueError("lifecycle transition must change state")
        if target not in _ALLOWED_TRANSITIONS[origin]:
            raise ValueError(
                f"lifecycle transition {origin} -> {target} is not allowed"
            )
        timestamp = _timestamp(occurred_at)
        with self._connection() as connection:
            connection.execute(
                "UPDATE strategy_definitions SET lifecycle=? WHERE strategy_id=? AND version=?",
                (target, str(strategy_id).strip(), str(version).strip()),
            )
            connection.execute(
                "INSERT INTO strategy_events(strategy_id, version, event_type, from_lifecycle, to_lifecycle, evidence_json, occurred_at, actor) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    str(strategy_id).strip(),
                    str(version).strip(),
                    "lifecycle_transition",
                    origin,
                    target,
                    _canonical_json(
                        {**dict(evidence), "source_ids": evidence_source_ids}
                    ),
                    timestamp,
                    str(actor).strip() or "agent",
                ),
            )
        return self.get_definition(strategy_id, version)

    def record_run(
        self,
        strategy_id: str,
        version: str,
        run: Mapping[str, Any],
        *,
        source_ids: Sequence[str],
        run_type: str = "paper",
        recorded_at: str | datetime | None = None,
    ) -> dict[str, Any]:
        definition = self.get_definition(strategy_id, version)
        if not isinstance(run, Mapping) or not run:
            raise ValueError("run must be a non-empty object")
        normalized_sources = _source_ids(source_ids)
        if not normalized_sources:
            raise ValueError("strategy run requires at least one source identifier")
        normalized_run_type = _required_text(run_type, "run_type")
        timestamp = _timestamp(recorded_at)
        payload = dict(run)
        _validate_run_payload(payload, strategy_id=strategy_id, version=version)
        fingerprint = _fingerprint(
            {
                "strategy_id": strategy_id,
                "version": version,
                "run_type": normalized_run_type,
                "run": payload,
                "source_ids": normalized_sources,
            }
        )
        run_id = (
            "run_"
            + hashlib.sha256((fingerprint + timestamp).encode("utf-8")).hexdigest()[:20]
        )
        with self._connection() as connection:
            connection.execute(
                "INSERT INTO strategy_runs(run_id, strategy_id, version, lifecycle_at_run, run_type, run_json, source_ids_json, fingerprint, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    run_id,
                    str(strategy_id).strip(),
                    str(version).strip(),
                    str(definition["lifecycle"]),
                    normalized_run_type,
                    _canonical_json(payload),
                    _canonical_json(normalized_sources),
                    fingerprint,
                    timestamp,
                ),
            )
        return self.get_run(run_id)

    def get_run(self, run_id: str) -> dict[str, Any]:
        with self._connection() as connection:
            row = connection.execute(
                "SELECT run_id, strategy_id, version, lifecycle_at_run, run_type, run_json, source_ids_json, fingerprint, recorded_at FROM strategy_runs WHERE run_id=?",
                (str(run_id).strip(),),
            ).fetchone()
        if row is None:
            raise ValueError("strategy run was not found")
        return {
            "schema_version": "strategy_run_record.v1",
            "run_id": str(row[0]),
            "strategy_id": str(row[1]),
            "strategy_version": str(row[2]),
            "lifecycle_at_run": str(row[3]),
            "run_type": str(row[4]),
            "run": json.loads(str(row[5])),
            "source_ids": json.loads(str(row[6])),
            "fingerprint": str(row[7]),
            "recorded_at": str(row[8]),
            "research_only": True,
            "no_order_execution": True,
            "formal_decision_eligible": False,
        }

    def list_events(self, strategy_id: str, version: str) -> list[dict[str, Any]]:
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT event_type, from_lifecycle, to_lifecycle, evidence_json, occurred_at, actor FROM strategy_events WHERE strategy_id=? AND version=? ORDER BY event_id",
                (str(strategy_id).strip(), str(version).strip()),
            ).fetchall()
        return [
            {
                "event_type": str(row[0]),
                "from_lifecycle": row[1],
                "to_lifecycle": row[2],
                "evidence": json.loads(str(row[3])),
                "occurred_at": str(row[4]),
                "actor": str(row[5]),
            }
            for row in rows
        ]

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS strategy_definitions (
                    strategy_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    lifecycle TEXT NOT NULL,
                    definition_json TEXT NOT NULL,
                    source_ids_json TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    registered_at TEXT NOT NULL,
                    registered_by TEXT NOT NULL,
                    PRIMARY KEY (strategy_id, version)
                );
                CREATE TABLE IF NOT EXISTS strategy_events (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    from_lifecycle TEXT,
                    to_lifecycle TEXT,
                    evidence_json TEXT NOT NULL,
                    occurred_at TEXT NOT NULL,
                    actor TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS strategy_runs (
                    run_id TEXT PRIMARY KEY,
                    strategy_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    lifecycle_at_run TEXT NOT NULL,
                    run_type TEXT NOT NULL,
                    run_json TEXT NOT NULL,
                    source_ids_json TEXT NOT NULL,
                    fingerprint TEXT NOT NULL,
                    recorded_at TEXT NOT NULL
                );
                """)

    def _connection(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA foreign_keys=ON")
        return connection


def register_definition(
    path: str | Path,
    definition: StrategyDefinition | Mapping[str, Any],
    *,
    source_ids: Sequence[str],
    registered_by: str = "agent",
) -> dict[str, Any]:
    return StrategyRegistry(path).register_definition(
        definition, source_ids=source_ids, registered_by=registered_by
    )


def record_run(
    path: str | Path,
    strategy_id: str,
    version: str,
    run: Mapping[str, Any],
    *,
    source_ids: Sequence[str],
    run_type: str = "paper",
) -> dict[str, Any]:
    return StrategyRegistry(path).record_run(
        strategy_id, version, run, source_ids=source_ids, run_type=run_type
    )


def transition_lifecycle(
    path: str | Path,
    strategy_id: str,
    version: str,
    to_lifecycle: str | StrategyLifecycle,
    *,
    evidence: Mapping[str, Any],
    actor: str = "agent",
) -> dict[str, Any]:
    return StrategyRegistry(path).transition_lifecycle(
        strategy_id, version, to_lifecycle, evidence=evidence, actor=actor
    )


def _timestamp(value: str | datetime | None) -> str:
    if value is None:
        return datetime.now(UTC).isoformat()
    if isinstance(value, datetime):
        stamp = value
    else:
        try:
            stamp = datetime.fromisoformat(str(value))
        except ValueError as error:
            raise ValueError("timestamp must use ISO-8601") from error
    if stamp.tzinfo is None:
        raise ValueError("timestamp must include a timezone")
    return stamp.astimezone(UTC).isoformat()


def _source_ids(values: Sequence[str]) -> list[str]:
    if isinstance(values, (str, bytes)) or not isinstance(values, Sequence):
        raise TypeError("source_ids must be a sequence")
    return list(dict.fromkeys(_required_text(value, "source_id") for value in values))


def _definition_payload(
    definition: StrategyDefinition | Mapping[str, Any],
) -> dict[str, Any]:
    """Remove access-profile and registry metadata before version hashing."""

    payload = (
        definition.to_dict()
        if isinstance(definition, StrategyDefinition)
        else dict(definition)
    )
    for name in (
        "eligibility",
        "fingerprint",
        "profile_id",
        "registered_at",
        "registered_by",
        "source_ids",
    ):
        payload.pop(name, None)
    _validate_definition_payload(payload)
    payload["research_only"] = True
    payload["no_order_execution"] = True
    return payload


def _validate_definition_payload(payload: Mapping[str, Any]) -> None:
    """Require the immutable contract before a definition enters the registry."""

    schema_version = payload.get("schema_version")
    if (
        schema_version is not None
        and str(schema_version) != "personal_strategy_definition.v1"
    ):
        raise ValueError("strategy definition schema_version is invalid")
    for field_name in (
        "strategy_id",
        "version",
        "name",
        "family",
        "economic_engine",
        "personal_translation",
    ):
        _required_text(payload.get(field_name), field_name)
    try:
        StrategyAvailability(str(payload.get("availability")))
    except ValueError as error:
        raise ValueError("strategy definition availability is invalid") from error
    _validated_lifecycle(payload.get("lifecycle"))
    for field_name in (
        "asset_scope",
        "required_access",
        "required_data",
        "non_replicable_components",
        "risk_notes",
    ):
        value = payload.get(field_name)
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise TypeError(f"strategy definition {field_name} must be a sequence")
        if not all(str(item).strip() for item in value):
            raise ValueError(
                f"strategy definition {field_name} cannot contain empty values"
            )
    if (
        payload.get("research_only") is not True
        or payload.get("no_order_execution") is not True
    ):
        raise ValueError(
            "strategy definition must retain research_only and no_order_execution guards"
        )


def _validate_run_payload(
    payload: Mapping[str, Any],
    *,
    strategy_id: str,
    version: str,
) -> None:
    """Bind a stored run to the immutable definition that owns it."""

    if str(payload.get("strategy_id") or "").strip() != str(strategy_id).strip():
        raise ValueError(
            "strategy run strategy_id does not match the registered definition"
        )
    payload_version = str(
        payload.get("strategy_version") or payload.get("version") or ""
    ).strip()
    if payload_version != str(version).strip():
        raise ValueError(
            "strategy run version does not match the registered definition"
        )
    if (
        payload.get("research_only") is not True
        or payload.get("no_order_execution") is not True
    ):
        raise ValueError(
            "strategy run must retain research_only and no_order_execution guards"
        )


def _evidence_source_ids(evidence: Mapping[str, Any]) -> Sequence[str]:
    value = evidence.get("source_ids") or evidence.get("source_refs") or ()
    if isinstance(value, (str, bytes)):
        return (str(value),)
    if not isinstance(value, Sequence):
        raise TypeError("transition evidence source_ids must be a sequence")
    return [str(item) for item in value]


def _validated_lifecycle(value: Any) -> str:
    try:
        return StrategyLifecycle(str(value)).value
    except ValueError as error:
        raise ValueError("lifecycle is invalid") from error


def _required_text(value: Any, name: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{name} is required")
    return result


def _canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )


def _fingerprint(value: Any) -> str:
    return (
        "sha256:" + hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()
    )
