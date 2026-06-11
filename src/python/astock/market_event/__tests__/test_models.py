"""Market event model tests."""

import json
from datetime import datetime, timezone

from astock.market_event import (
    DataQualityLevel,
    EventDirection,
    EventQuality,
    EventSeverity,
    EventSubject,
    MarketEvent,
    MarketEventType,
    SubjectType,
    normalize_direction,
    normalize_quality_level,
    normalize_severity,
)


def test_market_event_id_is_deterministic() -> None:
    observed_at = datetime(2026, 6, 12, 10, 30, tzinfo=timezone.utc)
    subject = EventSubject(type=SubjectType.STOCK, code="000001", name="Ping An Bank")

    first = MarketEvent(
        event_type=MarketEventType.PRICE_MOVE,
        subject=subject,
        title="000001 price move +3.00%",
        observed_at=observed_at,
        severity=EventSeverity.WATCH,
        direction=EventDirection.BULLISH,
        metrics={"change_pct": 3.0, "price": 10.3},
        source="test",
        dedupe_key="price_move",
    )
    second = MarketEvent(
        event_type=MarketEventType.PRICE_MOVE,
        subject=subject,
        title="000001 price move +3.00%",
        observed_at=observed_at,
        severity=EventSeverity.WATCH,
        direction=EventDirection.BULLISH,
        metrics={"price": 10.3, "change_pct": 3.0},
        source="test",
        dedupe_key="price_move",
    )

    assert first.id == second.id
    assert first.id.startswith("mevt_")


def test_market_event_to_dict_is_json_serializable() -> None:
    observed_at = datetime(2026, 6, 12, 10, 30, tzinfo=timezone.utc)
    event = MarketEvent(
        event_type=MarketEventType.TECHNICAL_SIGNAL,
        subject=EventSubject(type=SubjectType.STOCK, code="600000"),
        title="600000 technical signal",
        observed_at=observed_at,
        quality=EventQuality(
            level=DataQualityLevel.FULL,
            source="unit-test",
            as_of=observed_at,
            warnings=("sample",),
        ),
        metrics={"bad_number": float("nan"), "observed_at": observed_at},
        context={"levels": (1, 2, 3)},
        source="unit-test",
    )

    payload = event.to_dict()
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    metrics = payload["metrics"]

    assert isinstance(metrics, dict)
    assert metrics["bad_number"] is None
    assert metrics["observed_at"] == observed_at.isoformat()
    assert '"event_type": "technical_signal"' in encoded


def test_normalizers_handle_aliases_and_legacy_levels() -> None:
    assert normalize_direction("inflow") == EventDirection.BULLISH
    assert normalize_direction("outflow") == EventDirection.BEARISH
    assert normalize_severity(1) == EventSeverity.CRITICAL
    assert normalize_severity(2) == EventSeverity.IMPORTANT
    assert normalize_severity(3) == EventSeverity.WATCH
    assert normalize_quality_level("full_realtime") == DataQualityLevel.FULL
    assert normalize_quality_level("snapshot_degraded") == DataQualityLevel.DEGRADED
