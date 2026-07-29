"""Market event builder tests."""

from dataclasses import dataclass
from datetime import datetime, timezone

from astock.market_event import (
    EventDirection,
    EventSeverity,
    MarketEventType,
    build_alert_trigger_event,
    build_events_from_quote_payload,
    build_events_from_screen_payload,
    build_news_policy_event,
    build_sector_move_event,
    quality_from_payload,
)


def test_build_events_from_quote_payload() -> None:
    payload = {
        "code": "000001",
        "name": "Ping An Bank",
        "price": 15.5,
        "prev_close": 15.0,
        "volume": 3_000_000,
        "vol_ma5": 1_000_000,
        "main_net_inflow": 450_000_000,
        "data_quality": "full_realtime",
        "timestamp": "2026-06-12T10:30:00+00:00",
        "source": "akshare",
    }

    events = build_events_from_quote_payload(payload)
    event_types = {event.event_type for event in events}
    repeated = build_events_from_quote_payload(payload)

    assert event_types == {
        MarketEventType.PRICE_MOVE,
        MarketEventType.VOLUME_SPIKE,
        MarketEventType.FUND_FLOW_MOVE,
    }
    assert [event.id for event in events] == [event.id for event in repeated]

    price_event = next(
        event for event in events if event.event_type == MarketEventType.PRICE_MOVE
    )
    assert price_event.direction == EventDirection.BULLISH
    assert price_event.severity == EventSeverity.WATCH
    assert price_event.metrics["change_pct"] == 3.3333333333333335

    volume_event = next(
        event for event in events if event.event_type == MarketEventType.VOLUME_SPIKE
    )
    assert volume_event.severity == EventSeverity.IMPORTANT
    assert volume_event.metrics["volume_ratio"] == 3.0


@dataclass
class ScreenPayload:
    code: str
    name: str
    matched_factors: list[str]
    factor_checks: dict[str, dict[str, object]]
    screened_at: datetime


def test_build_events_from_screen_payload_maps_factor_types() -> None:
    payload = ScreenPayload(
        code="000001",
        name="Ping An Bank",
        matched_factors=[
            "range_expansion",
            "high_volume",
            "net_inflow",
            "pe_low",
        ],
        factor_checks={
            "range_expansion": {
                "name": "Range Expansion",
                "type": "market_structure",
                "field": "intraday_range_pct",
                "operator": "gte",
                "value": 4.2,
                "reference_value": 2.0,
                "weight": 2.0,
                "matched": True,
            },
            "high_volume": {
                "name": "High Volume",
                "type": "quality",
                "field": "volume",
                "value": 3_000_000,
                "reference_value": 1_000_000,
                "weight": 1.0,
                "matched": True,
            },
            "net_inflow": {
                "name": "Main Force Net Inflow",
                "type": "capital_flow",
                "field": "main_net_inflow",
                "value": 250_000_000,
                "reference_value": 0,
                "weight": 2.0,
                "matched": True,
            },
            "pe_low": {
                "name": "Low PE",
                "type": "valuation",
                "field": "pe",
                "value": 8.5,
                "reference_value": 30,
                "weight": 1.0,
                "matched": True,
            },
        },
        screened_at=datetime(2026, 6, 12, 10, 30, tzinfo=timezone.utc),
    )

    events = build_events_from_screen_payload(payload)
    by_key = {str(event.context["factor_key"]): event for event in events}

    assert by_key["range_expansion"].event_type == MarketEventType.ALERT_TRIGGER
    assert by_key["high_volume"].event_type == MarketEventType.VOLUME_SPIKE
    assert by_key["net_inflow"].event_type == MarketEventType.FUND_FLOW_MOVE
    assert by_key["pe_low"].event_type == MarketEventType.ALERT_TRIGGER
    assert by_key["net_inflow"].direction == EventDirection.BULLISH


def test_build_sector_alert_and_news_policy_events() -> None:
    sector = build_sector_move_event(
        {
            "sector_name": "Semiconductor",
            "change_pct": 2.1,
            "amount": 12_000_000_000,
            "updated_at": "2026-06-12T10:30:00+00:00",
        }
    )
    alert = build_alert_trigger_event(
        {
            "code": "000001",
            "signal_type": "price_breakout",
            "signal_name": "Price Breakout",
            "level": 1,
            "triggered_at": "2026-06-12T10:30:00+00:00",
        }
    )
    news = build_news_policy_event(
        {
            "category": "policy",
            "title": "Policy support for advanced manufacturing",
            "importance": "high",
            "sentiment": "positive",
            "published_at": "2026-06-12T09:00:00+00:00",
            "related_sectors": ["Semiconductor"],
        }
    )

    assert sector is not None
    assert sector.event_type == MarketEventType.SECTOR_MOVE
    assert alert.severity == EventSeverity.CRITICAL
    assert news.event_type == MarketEventType.NEWS_POLICY_EVENT
    assert news.direction == EventDirection.BULLISH
    assert "policy" in news.tags


def test_quality_from_payload_records_missing_observed_at_warning() -> None:
    quality = quality_from_payload(
        {"code": "000001", "data_quality": "full_realtime"},
        required_fields=("timestamp",),
        warnings=("missing_observed_at",),
    )

    assert quality.level.value == "degraded"
    assert quality.missing_fields == ("timestamp",)
    assert quality.warnings == ("missing_observed_at",)
