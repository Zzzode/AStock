"""Market-event helpers for monitor alert payloads."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from enum import StrEnum
from typing import Any, Mapping, cast

from astock.market_event import MarketEvent, build_alert_trigger_event

ALERT_MESSAGE_SCHEMA_VERSION = "monitor.alert_message.v1"


@dataclass(frozen=True)
class DecodedAlertMessage:
    """Decoded alert message envelope."""

    text: str
    market_event: dict[str, Any] | None = None


def build_alert_market_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str = "monitor.alert",
) -> dict[str, Any]:
    """Build a canonical market event from an AlertRecord-like payload."""

    data = _payload_to_dict(payload)
    decoded = decode_alert_message(str(data.get("message", "")))
    data["message"] = decoded.text
    event = build_alert_trigger_event(data, source=source)
    return cast(dict[str, Any], event.to_dict())


def encode_alert_message(
    text: str,
    market_event: MarketEvent | Mapping[str, Any] | None,
) -> str:
    """Encode alert text and market event into the existing message field."""

    if market_event is None:
        return text

    event_payload = (
        cast(dict[str, Any], market_event.to_dict())
        if isinstance(market_event, MarketEvent)
        else _json_ready_dict(market_event)
    )
    envelope = {
        "schema_version": ALERT_MESSAGE_SCHEMA_VERSION,
        "text": text,
        "market_event": event_payload,
    }
    return json.dumps(envelope, ensure_ascii=False, sort_keys=True)


def decode_alert_message(message: str) -> DecodedAlertMessage:
    """Decode a monitor alert message envelope, falling back to legacy text."""

    try:
        payload = json.loads(message)
    except (TypeError, ValueError):
        return DecodedAlertMessage(text=message)

    if not isinstance(payload, Mapping):
        return DecodedAlertMessage(text=message)
    if payload.get("schema_version") != ALERT_MESSAGE_SCHEMA_VERSION:
        return DecodedAlertMessage(text=message)

    text = payload.get("text")
    event = payload.get("market_event")
    return DecodedAlertMessage(
        text=str(text or ""),
        market_event=cast(dict[str, Any], event) if isinstance(event, dict) else None,
    )


def get_alert_message_text(message: str) -> str:
    """Return the human-readable alert text from legacy or envelope messages."""

    return decode_alert_message(message).text


def get_alert_market_event(message: str) -> dict[str, Any] | None:
    """Return the embedded market event payload, if present."""

    return decode_alert_message(message).market_event


def format_market_event_json(message: str, *, indent: int | None = None) -> str | None:
    """Return deterministic market-event JSON for notification payloads."""

    event = get_alert_market_event(message)
    if event is None:
        return None
    return json.dumps(event, ensure_ascii=False, sort_keys=True, indent=indent)


def _payload_to_dict(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    if isinstance(payload, Mapping):
        return dict(payload)

    model_dump = getattr(payload, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        return dict(dumped) if isinstance(dumped, Mapping) else {}

    raw = getattr(payload, "__dict__", None)
    return dict(raw) if isinstance(raw, Mapping) else {}


def _json_ready_dict(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _json_ready(item) for key, item in value.items()}


def _json_ready(value: Any) -> Any:
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return _json_ready_dict(value)
    if isinstance(value, (list, tuple)):
        return [_json_ready(item) for item in value]
    return value
