"""Fund-flow anomaly detection tests."""

import json

from astock.market_event import (
    EventDirection,
    MarketEventType,
    build_fund_flow_anomaly_packet,
    detect_market_anomalies,
    normalize_fund_flow_snapshot,
)


def test_normalize_fund_flow_snapshot_is_json_ready() -> None:
    snapshot = normalize_fund_flow_snapshot(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "price": 15.5,
            "prev_close": 15.0,
            "volume": 3_000_000,
            "vol_ma5": 1_000_000,
            "main_net_inflow": 250_000_000,
            "timestamp": "2026-06-12T10:30:00+00:00",
            "source": "akshare",
        }
    )
    packet = snapshot.to_dict()

    assert packet["subject"]["type"] == "stock"
    assert packet["subject"]["code"] == "000001"
    assert packet["metrics"]["net_flow"] == 250_000_000
    assert packet["metrics"]["change_pct"] == 3.3333333333333335
    assert packet["metrics"]["volume_ratio"] == 3.0
    json.dumps(packet, ensure_ascii=False)


def test_stock_snapshot_keeps_stock_subject_when_theme_context_exists() -> None:
    snapshot = normalize_fund_flow_snapshot(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "industry": "Banking",
            "theme": "High dividend",
            "net_flow": 120_000_000,
            "timestamp": "2026-06-12T10:30:00+00:00",
        }
    )

    assert snapshot.subject.type.value == "stock"
    assert snapshot.subject.code == "000001"
    assert snapshot.context["industry"] == "Banking"
    assert snapshot.context["theme"] == "High dividend"


def test_detects_inflow_anomaly() -> None:
    events = detect_market_anomalies(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "change_pct": 1.2,
            "net_flow": 180_000_000,
            "timestamp": "2026-06-12T10:30:00+00:00",
        }
    )
    flow_event = next(
        event for event in events if event.context["anomaly_type"] == "fund_flow_surge"
    )

    assert flow_event.event_type == MarketEventType.FUND_FLOW_MOVE
    assert flow_event.direction == EventDirection.BULLISH
    assert flow_event.metrics["net_flow"] == 180_000_000


def test_detects_outflow_anomaly() -> None:
    events = detect_market_anomalies(
        {
            "code": "000002",
            "name": "Vanke A",
            "change_pct": -0.8,
            "net_flow": -220_000_000,
            "timestamp": "2026-06-12T10:30:00+00:00",
        }
    )
    flow_event = next(
        event
        for event in events
        if event.context["anomaly_type"] == "fund_flow_outflow"
    )

    assert flow_event.event_type == MarketEventType.FUND_FLOW_MOVE
    assert flow_event.direction == EventDirection.BEARISH
    assert flow_event.metrics["net_flow"] == -220_000_000


def test_detects_flow_price_divergence() -> None:
    events = detect_market_anomalies(
        {
            "code": "600519",
            "name": "Kweichow Moutai",
            "change_pct": -1.6,
            "net_flow": 350_000_000,
            "timestamp": "2026-06-12T10:30:00+00:00",
        }
    )
    divergence = next(
        event
        for event in events
        if event.context["anomaly_type"] == "flow_price_divergence"
    )

    assert divergence.event_type == MarketEventType.FUND_FLOW_MOVE
    assert divergence.direction == EventDirection.MIXED
    assert divergence.context["divergence_type"] == "inflow_price_weakness"


def test_detects_sector_rotation() -> None:
    events = detect_market_anomalies(
        {
            "subject_type": "sector",
            "sector_name": "Semiconductor",
            "change_pct": 1.8,
            "net_flow": 480_000_000,
            "sector_rank_delta": 8,
            "rotation_sectors": ["Semiconductor", "AI Hardware"],
            "timestamp": "2026-06-12T10:30:00+00:00",
        }
    )
    rotation = next(
        event for event in events if event.context["anomaly_type"] == "sector_rotation"
    )

    assert rotation.event_type == MarketEventType.SECTOR_MOVE
    assert rotation.subject.type.value == "sector"
    assert rotation.metrics["sector_rank_delta"] == 8


def test_empty_payload_has_no_signal() -> None:
    packet = build_fund_flow_anomaly_packet(
        {
            "code": "000001",
            "name": "Ping An Bank",
            "change_pct": 0.2,
            "net_flow": 10_000_000,
            "volume_ratio": 1.1,
            "timestamp": "2026-06-12T10:30:00+00:00",
        }
    )

    assert packet["event_count"] == 0
    assert packet["market_events"] == []
