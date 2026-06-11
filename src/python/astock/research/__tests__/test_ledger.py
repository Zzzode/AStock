from datetime import datetime
from pathlib import Path

import pytest

from astock.research import (
    ResearchEntry,
    ResearchLedger,
    ResearchObservation,
    ResearchStatus,
    ResearchTrigger,
)
from astock.research.ledger import make_research_id


def test_research_entry_roundtrip() -> None:
    created_at = datetime(2026, 6, 12, 10, 30)
    entry = ResearchEntry(
        title="Bank sector re-rating",
        thesis="Low valuation plus improving credit impulse may support follow-up.",
        targets=["000001", "600000"],
        catalysts=["credit data rebound"],
        risks=["NIM compression"],
        monitoring_triggers=[
            ResearchTrigger(
                name="sector flow confirmation",
                condition="bank sector fund flow ranks top 3 for two sessions",
                metric="sector_flow_rank",
                threshold=3,
            )
        ],
        invalidation_conditions=["sector underperforms CSI 300 for five sessions"],
        tags=["bank", "value"],
        data_quality={"quote": "daily_only"},
        created_at=created_at,
        updated_at=created_at,
    )

    payload = entry.to_dict()
    restored = ResearchEntry.from_dict(payload)

    assert restored.entry_id == entry.entry_id
    assert restored.targets == ["000001", "600000"]
    assert restored.monitoring_triggers[0].name == "sector flow confirmation"
    assert restored.data_quality["quote"] == "daily_only"


def test_ledger_create_list_and_observe(tmp_path: Path) -> None:
    ledger = ResearchLedger(tmp_path / "ledger.json")
    entry = ResearchEntry(
        title="AI hardware pullback watch",
        thesis="Track leaders after a volume-backed pullback.",
        targets=["300001"],
        tags=["ai", "hardware"],
    )

    created = ledger.create(entry)
    loaded = ledger.get(created.entry_id or "")

    assert loaded is not None
    assert loaded.title == "AI hardware pullback watch"
    assert ledger.list_entries(target="300001")[0].entry_id == created.entry_id
    assert ledger.list_entries(tag="ai")[0].entry_id == created.entry_id

    updated = ledger.record_observation(
        created.entry_id or "",
        ResearchObservation(
            observation_type="trigger_check",
            note="Volume confirmation failed; downgrade to monitoring only.",
            evidence={"volume_ratio": 0.8},
            status_after=ResearchStatus.MONITORING,
        ),
    )

    assert updated.status == ResearchStatus.MONITORING
    assert updated.observations[0].evidence["volume_ratio"] == 0.8

    reloaded = ResearchLedger(tmp_path / "ledger.json")
    entries = reloaded.list_entries(status=ResearchStatus.MONITORING)
    assert len(entries) == 1
    assert entries[0].observations[0].note.startswith("Volume confirmation failed")


def test_ledger_rejects_duplicate_entry(tmp_path: Path) -> None:
    created_at = datetime(2026, 6, 12, 9, 0)
    entry = ResearchEntry(
        title="Duplicate thesis",
        thesis="Same target and title at the same time creates same ID.",
        targets=["000001"],
        created_at=created_at,
        updated_at=created_at,
    )
    duplicate = ResearchEntry(
        title="Duplicate thesis",
        thesis="Different wording but same ID seed.",
        targets=["000001"],
        created_at=created_at,
        updated_at=created_at,
    )
    ledger = ResearchLedger(tmp_path / "ledger.json")

    ledger.create(entry)
    with pytest.raises(ValueError):
        ledger.create(duplicate)


def test_make_research_id_is_stable_for_sorted_targets() -> None:
    created_at = datetime(2026, 6, 12, 9, 0)

    first = make_research_id(
        targets=["600000", "000001"],
        title="Bank thesis",
        created_at=created_at,
    )
    second = make_research_id(
        targets=["000001", "600000"],
        title="Bank thesis",
        created_at=created_at,
    )

    assert first == second
    assert first.startswith("research-20260612-")
