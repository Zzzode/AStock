"""Market event store tests."""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

from astock.market_event import (
    EventDirection,
    EventQuery,
    EventSeverity,
    EventStore,
    EventSubject,
    MarketEvent,
    MarketEventType,
    SubjectType,
)


def make_event(
    *,
    event_type: MarketEventType,
    subject: EventSubject,
    observed_at: datetime,
    severity: EventSeverity = EventSeverity.WATCH,
    direction: EventDirection = EventDirection.UNKNOWN,
    tags: tuple[str, ...] = (),
    title: str = "market event",
    source: str = "unit-test",
) -> MarketEvent:
    return MarketEvent(
        event_type=event_type,
        subject=subject,
        title=title,
        observed_at=observed_at,
        severity=severity,
        direction=direction,
        source=source,
        tags=tags,
        metrics={"change_pct": 3.0},
        dedupe_key=title,
    )


def seed_store(path: Path) -> tuple[EventStore, list[MarketEvent]]:
    store = EventStore(path)
    events = [
        make_event(
            event_type=MarketEventType.PRICE_MOVE,
            subject=EventSubject(
                type=SubjectType.STOCK,
                code="000001",
                name="Ping An Bank",
            ),
            observed_at=datetime(2026, 6, 12, 9, 31, tzinfo=timezone.utc),
            severity=EventSeverity.IMPORTANT,
            direction=EventDirection.BULLISH,
            tags=("quote", "price"),
            title="000001 price breakout",
        ),
        make_event(
            event_type=MarketEventType.VOLUME_SPIKE,
            subject=EventSubject(
                type=SubjectType.STOCK,
                code="000001",
                name="Ping An Bank",
            ),
            observed_at=datetime(2026, 6, 12, 9, 35, tzinfo=timezone.utc),
            severity=EventSeverity.WATCH,
            direction=EventDirection.BULLISH,
            tags=("quote", "volume"),
            title="000001 volume spike",
        ),
        make_event(
            event_type=MarketEventType.SECTOR_MOVE,
            subject=EventSubject(type=SubjectType.SECTOR, name="Semiconductor"),
            observed_at=datetime(2026, 6, 12, 9, 33, tzinfo=timezone.utc),
            severity=EventSeverity.WATCH,
            direction=EventDirection.BEARISH,
            tags=("sector", "price"),
            title="Semiconductor sector pullback",
        ),
        make_event(
            event_type=MarketEventType.NEWS_POLICY_EVENT,
            subject=EventSubject(type=SubjectType.THEME, name="AI Computing"),
            observed_at=datetime(2026, 6, 12, 9, 40, tzinfo=timezone.utc),
            severity=EventSeverity.CRITICAL,
            direction=EventDirection.BULLISH,
            tags=("policy", "theme"),
            title="AI Computing policy catalyst",
        ),
    ]
    for event in events:
        assert store.add(event).inserted is True
    return store, events


def test_event_store_add_dedupes_and_accepts_dicts(tmp_path: Path) -> None:
    store, events = seed_store(tmp_path / "events.jsonl")
    first = events[0]

    duplicate = store.add(first)
    dict_duplicate = store.add(first.to_dict())
    persisted = EventStore(tmp_path / "events.jsonl")

    assert duplicate.inserted is False
    assert dict_duplicate.inserted is False
    assert len(persisted.list_events()) == 4
    assert persisted.get(first.id) == first.to_dict()


def test_event_store_filters_by_core_dimensions(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path / "events.jsonl")

    stock_events = store.list_events(subject_code="000001")
    sector_events = store.list_events(
        subject_name="Semiconductor",
        subject_type=SubjectType.SECTOR,
    )
    theme_events = store.list_events(subject_type="theme")
    price_events = store.list_events(event_type=MarketEventType.PRICE_MOVE)
    price_tag_events = store.list_events(tag="price")
    important_events = store.list_events(severity="important")
    bullish_events = store.list_events(direction=EventDirection.BULLISH)
    window_events = store.list_events(
        start_at="2026-06-12T09:33:00+00:00",
        end_at="2026-06-12T09:35:00+00:00",
    )

    assert [event["event_type"] for event in stock_events] == [
        "price_move",
        "volume_spike",
    ]
    assert [event["event_type"] for event in sector_events] == ["sector_move"]
    assert [event["event_type"] for event in theme_events] == ["news_policy_event"]
    assert len(price_events) == 1
    assert {event["event_type"] for event in price_tag_events} == {
        "price_move",
        "sector_move",
    }
    assert [event["event_type"] for event in important_events] == ["price_move"]
    assert len(bullish_events) == 3
    assert [event["event_type"] for event in window_events] == [
        "sector_move",
        "volume_spike",
    ]


def test_event_store_query_limit_reverse_and_replay(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path / "events.jsonl")

    newest = store.list_events(EventQuery(limit=2), reverse=True)
    stock_replay = store.replay_subject(subject_code="000001")
    sector_replay = store.replay_subject(
        subject_name="Semiconductor",
        subject_type="sector",
    )
    theme_replay = store.replay_subject(
        subject_name="AI Computing", subject_type="theme"
    )
    latest_stock = store.replay_subject(subject_code="000001", limit=1)

    assert [event["event_type"] for event in newest] == [
        "news_policy_event",
        "volume_spike",
    ]
    assert [event["event_type"] for event in stock_replay] == [
        "price_move",
        "volume_spike",
    ]
    assert [event["event_type"] for event in sector_replay] == ["sector_move"]
    assert [event["event_type"] for event in theme_replay] == ["news_policy_event"]
    assert [event["event_type"] for event in latest_stock] == ["volume_spike"]


def test_event_store_aggregates_market_board_dimensions(tmp_path: Path) -> None:
    store, _ = seed_store(tmp_path / "events.jsonl")

    aggregate = store.aggregate()
    price_aggregate = store.aggregate(tag="price")
    subjects = cast(dict[str, dict[str, Any]], aggregate["subject"])

    assert aggregate["total"] == 4
    assert aggregate["event_type"] == {
        "news_policy_event": 1,
        "price_move": 1,
        "sector_move": 1,
        "volume_spike": 1,
    }
    assert aggregate["severity"] == {"critical": 1, "important": 1, "watch": 2}
    assert aggregate["direction"] == {"bearish": 1, "bullish": 3}
    assert aggregate["tag"] == {
        "policy": 1,
        "price": 2,
        "quote": 2,
        "sector": 1,
        "theme": 1,
        "volume": 1,
    }
    assert isinstance(subjects, dict)
    assert subjects["stock:000001"]["count"] == 2
    assert subjects["sector:Semiconductor"]["count"] == 1
    assert subjects["theme:AI Computing"]["count"] == 1
    assert price_aggregate["total"] == 2
