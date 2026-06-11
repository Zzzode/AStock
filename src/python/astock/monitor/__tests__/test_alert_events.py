"""Monitor alert market-event tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

import pytest

from astock.monitor.alert_engine import _build_dingtalk_payload
from astock.monitor.alert_events import (
    ALERT_MESSAGE_SCHEMA_VERSION,
    build_alert_market_event,
    decode_alert_message,
    encode_alert_message,
)
from astock.monitor.monitor_service import MonitorService
from astock.storage import AlertRecord, WatchItem


def test_alert_record_like_payload_roundtrips_market_event() -> None:
    alert = AlertRecord(
        id=1,
        code="000001",
        signal_type="ma_cross",
        signal_name="MA cross",
        message="MA5 crossed above MA20",
        level=2,
        triggered_at=datetime(2026, 6, 12, 10, 30, 0),
        status="pending",
        channels=["terminal"],
    )

    market_event = build_alert_market_event(alert)
    encoded_message = encode_alert_message(alert.message, market_event)
    stored_alert = alert.model_copy(update={"message": encoded_message})

    envelope = json.loads(stored_alert.message)
    decoded = decode_alert_message(stored_alert.message)

    assert envelope["schema_version"] == ALERT_MESSAGE_SCHEMA_VERSION
    assert decoded.text == "MA5 crossed above MA20"
    assert decoded.market_event is not None
    assert decoded.market_event["schema_version"] == "market_event.v1"
    assert decoded.market_event["event_type"] == "alert_trigger"
    assert decoded.market_event["subject"]["code"] == "000001"
    assert decoded.market_event["context"]["message"] == "MA5 crossed above MA20"
    json.dumps(decoded.market_event, ensure_ascii=False)


def test_dingtalk_payload_sends_embedded_market_event() -> None:
    market_event = build_alert_market_event(
        {
            "code": "000001",
            "signal_type": "volume_spike",
            "signal_name": "Volume spike",
            "message": "Volume expanded sharply",
            "level": 1,
            "triggered_at": datetime(2026, 6, 12, 10, 31, 0),
            "channels": ["dingtalk"],
            "metrics": {"volume_ratio": 3.2},
        }
    )
    alert = AlertRecord(
        id=2,
        code="000001",
        signal_type="volume_spike",
        signal_name="Volume spike",
        message=encode_alert_message("Volume expanded sharply", market_event),
        level=1,
        triggered_at=datetime(2026, 6, 12, 10, 31, 0),
        status="pending",
        channels=["dingtalk"],
    )

    payload = _build_dingtalk_payload(alert)
    markdown = payload["markdown"]["text"]

    assert "Volume expanded sharply" in markdown
    assert "Market Event" in markdown
    assert '"schema_version": "market_event.v1"' in markdown
    assert '"event_type": "alert_trigger"' in markdown


@pytest.mark.asyncio  # type: ignore[untyped-decorator]
async def test_monitor_service_stores_and_sends_alert_market_event(
    tmp_path: Path,
) -> None:
    class FakeDB:
        def __init__(self) -> None:
            self.saved_record: AlertRecord | None = None
            self.updated_status: tuple[int, str] | None = None

        async def save_alert_record(self, record: AlertRecord) -> int:
            self.saved_record = record
            return 42

        async def update_alert_status(self, record_id: int, status: str) -> None:
            self.updated_status = (record_id, status)

    class FakeAlertEngine:
        def __init__(self) -> None:
            self.sent_record: AlertRecord | None = None
            self.sent_channels: list[str] | None = None

        async def send(
            self,
            alert: AlertRecord,
            channels: list[str] | None = None,
        ) -> dict[str, bool]:
            self.sent_record = alert
            self.sent_channels = channels
            return {channel: True for channel in channels or ["terminal"]}

    config_file = tmp_path / "config.json"
    config_file.write_text("{}", encoding="utf-8")
    db = FakeDB()
    engine = FakeAlertEngine()
    service = MonitorService(
        db=cast(Any, db),
        quote_service=cast(Any, object()),
        config_path=config_file,
    )
    service.alert_engine = cast(Any, engine)

    item = WatchItem(
        code="000001",
        name="Ping An Bank",
        alert_channels=["terminal", "dingtalk"],
    )
    scan_result = {
        "signals": [
            {
                "type": "ma_cross",
                "name": "MA cross",
                "description": "MA5 crossed above MA20",
                "bias": "bullish",
            }
        ],
        "level": 2,
        "latest": {"close": 12.34, "ma5": 12.2, "ma20": 12.1},
        "data_quality": "full",
    }

    await service._handle_signal(item, scan_result)

    assert db.saved_record is not None
    assert db.saved_record.id == 42
    decoded = decode_alert_message(db.saved_record.message)
    assert decoded.text == "MA5 crossed above MA20"
    assert decoded.market_event is not None
    assert decoded.market_event["source"] == "monitor.signal_scanner"
    assert decoded.market_event["subject"]["code"] == "000001"
    assert decoded.market_event["subject"]["name"] == "Ping An Bank"
    assert decoded.market_event["direction"] == "bullish"
    assert decoded.market_event["metrics"]["close"] == 12.34
    assert engine.sent_record is db.saved_record
    assert engine.sent_channels == ["terminal", "dingtalk"]
    assert db.updated_status == (42, "sent")
