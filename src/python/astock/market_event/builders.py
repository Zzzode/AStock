"""Helper builders for market events from capability payloads."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any, cast

from .models import (
    DataQualityLevel,
    EventDirection,
    EventQuality,
    EventSeverity,
    EventSubject,
    MarketEvent,
    MarketEventType,
    SubjectType,
    coerce_datetime,
    direction_from_signed_value,
    normalize_direction,
    normalize_quality_level,
    normalize_severity,
    severity_from_abs_amount,
    severity_from_percent_change,
    severity_from_volume_ratio,
)

_EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)


def build_events_from_quote_payload(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
    price_threshold_pct: float = 2.0,
    volume_threshold_ratio: float = 2.0,
    fund_flow_threshold_amount: float = 100_000_000.0,
) -> list[MarketEvent]:
    """Build market events from a quote-like payload."""

    builders = (
        build_price_move_event(
            payload,
            source=source,
            observed_at=observed_at,
            threshold_pct=price_threshold_pct,
        ),
        build_volume_spike_event(
            payload,
            source=source,
            observed_at=observed_at,
            threshold_ratio=volume_threshold_ratio,
        ),
        build_fund_flow_event(
            payload,
            source=source,
            observed_at=observed_at,
            threshold_amount=fund_flow_threshold_amount,
        ),
    )
    return [event for event in builders if event is not None]


def build_price_move_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
    threshold_pct: float = 2.0,
) -> MarketEvent | None:
    """Build a price-move event from a quote payload when threshold is met."""

    data = payload_to_dict(payload)
    change_pct = _extract_percent_change(data)
    if change_pct is None or abs(change_pct) < threshold_pct:
        return None

    price = _first_float(data, "price", "close", "latest_price", "current", "最新价")
    prev_close = _first_float(data, "prev_close", "pre_close", "previous_close", "昨收")
    change_amount = _first_float(data, "change", "change_amount", "涨跌额")
    event_source = _source_from_payload(data, source, "quote")
    event_time, warnings = _resolve_observed_at(data, observed_at)

    subject = _stock_subject(data)
    name_part = f" {subject.name}" if subject.name else ""
    title = f"{subject.key}{name_part} price move {change_pct:+.2f}%"
    metrics = {
        "price": price,
        "prev_close": prev_close,
        "change_pct": change_pct,
        "change_amount": change_amount,
    }

    return MarketEvent(
        event_type=MarketEventType.PRICE_MOVE,
        subject=subject,
        title=title,
        observed_at=event_time,
        severity=severity_from_percent_change(change_pct, watch_pct=threshold_pct),
        direction=direction_from_signed_value(change_pct),
        quality=quality_from_payload(
            data,
            source=event_source,
            observed_at=event_time,
            warnings=warnings,
        ),
        source=event_source,
        metrics=metrics,
        context={"raw_change_pct": change_pct},
        tags=("quote", "price"),
        dedupe_key="price_move",
    )


def build_volume_spike_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
    threshold_ratio: float = 2.0,
) -> MarketEvent | None:
    """Build a volume-spike event from a quote payload when threshold is met."""

    data = payload_to_dict(payload)
    ratio = _extract_volume_ratio(data)
    if ratio is None or ratio < threshold_ratio:
        return None

    volume = _first_float(data, "volume", "vol", "成交量")
    avg_volume = _first_float(
        data,
        "vol_ma5",
        "volume_ma5",
        "avg_volume_5d",
        "average_volume",
    )
    change_pct = _extract_percent_change(data)
    event_source = _source_from_payload(data, source, "quote")
    event_time, warnings = _resolve_observed_at(data, observed_at)
    subject = _stock_subject(data)

    return MarketEvent(
        event_type=MarketEventType.VOLUME_SPIKE,
        subject=subject,
        title=f"{subject.key} volume spike {ratio:.2f}x",
        observed_at=event_time,
        severity=severity_from_volume_ratio(ratio, watch_ratio=threshold_ratio),
        direction=direction_from_signed_value(change_pct),
        quality=quality_from_payload(
            data,
            source=event_source,
            observed_at=event_time,
            warnings=warnings,
        ),
        source=event_source,
        metrics={
            "volume": volume,
            "avg_volume": avg_volume,
            "volume_ratio": ratio,
            "change_pct": change_pct,
        },
        context={"basis": "volume_ratio"},
        tags=("quote", "volume"),
        dedupe_key="volume_spike",
    )


def build_sector_move_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
    threshold_pct: float = 1.5,
) -> MarketEvent | None:
    """Build a sector move event from sector market data."""

    data = payload_to_dict(payload)
    change_pct = _extract_percent_change(data)
    if change_pct is None or abs(change_pct) < threshold_pct:
        return None

    event_source = _source_from_payload(data, source, "sector")
    event_time, warnings = _resolve_observed_at(data, observed_at)
    subject = _sector_subject(data)

    return MarketEvent(
        event_type=MarketEventType.SECTOR_MOVE,
        subject=subject,
        title=f"{subject.key} sector move {change_pct:+.2f}%",
        observed_at=event_time,
        severity=severity_from_percent_change(change_pct, watch_pct=threshold_pct),
        direction=direction_from_signed_value(change_pct),
        quality=quality_from_payload(
            data,
            source=event_source,
            observed_at=event_time,
            warnings=warnings,
        ),
        source=event_source,
        metrics={
            "change_pct": change_pct,
            "amount": _first_float(data, "amount", "turnover", "成交额"),
            "stock_count": _first_float(data, "stock_count", "count"),
        },
        context={
            "leading_stocks": _jsonable_list(
                _first_value(data, "leading_stocks", "leaders", "领涨股")
            ),
            "lagging_stocks": _jsonable_list(
                _first_value(data, "lagging_stocks", "laggards", "领跌股")
            ),
        },
        tags=("sector", "price"),
        dedupe_key="sector_move",
    )


def build_fund_flow_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
    threshold_amount: float = 100_000_000.0,
) -> MarketEvent | None:
    """Build a fund-flow event from stock, sector, or market payloads."""

    data = payload_to_dict(payload)
    net_flow = _extract_net_flow(data)
    if net_flow is None or abs(net_flow) < threshold_amount:
        return None

    event_source = _source_from_payload(data, source, "fund_flow")
    event_time, warnings = _resolve_observed_at(data, observed_at)
    subject = _fund_flow_subject(data)
    direction = direction_from_signed_value(net_flow)
    flow_word = "inflow" if direction == EventDirection.BULLISH else "outflow"

    return MarketEvent(
        event_type=MarketEventType.FUND_FLOW_MOVE,
        subject=subject,
        title=f"{subject.key} fund {flow_word} {net_flow:,.0f}",
        observed_at=event_time,
        severity=severity_from_abs_amount(
            net_flow,
            watch_amount=threshold_amount,
        ),
        direction=direction,
        quality=quality_from_payload(
            data,
            source=event_source,
            observed_at=event_time,
            warnings=warnings,
        ),
        source=event_source,
        metrics={
            "net_flow": net_flow,
            "net_flow_ratio": _first_float(
                data,
                "net_flow_ratio",
                "main_net_inflow_ratio",
                "flow_ratio",
            ),
            "amount": _first_float(data, "amount", "turnover", "成交额"),
            "unit": "CNY",
        },
        context={"flow_direction": flow_word},
        tags=("fund_flow",),
        dedupe_key="fund_flow_move",
    )


def build_alert_trigger_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> MarketEvent:
    """Build an alert-trigger event from an AlertRecord-like payload."""

    data = payload_to_dict(payload)
    event_source = _source_from_payload(data, source, "alert")
    event_time, warnings = _resolve_observed_at(data, observed_at)
    subject = _stock_subject(data)
    signal_type = str(_first_value(data, "signal_type", "type") or "alert")
    signal_name = str(_first_value(data, "signal_name", "name") or signal_type)

    return MarketEvent(
        event_type=MarketEventType.ALERT_TRIGGER,
        subject=subject,
        title=f"{subject.key} alert triggered: {signal_name}",
        observed_at=event_time,
        severity=normalize_severity(_first_value(data, "level", "severity")),
        direction=normalize_direction(_first_value(data, "direction", "bias")),
        quality=quality_from_payload(
            data,
            source=event_source,
            observed_at=event_time,
            warnings=warnings,
        ),
        source=event_source,
        metrics=_numeric_mapping(_first_value(data, "metrics", "conditions") or {}),
        context={
            "signal_type": signal_type,
            "signal_name": signal_name,
            "message": _first_value(data, "message", "description"),
            "channels": _jsonable_list(_first_value(data, "channels")),
            "status": _first_value(data, "status"),
        },
        tags=("alert",),
        dedupe_key=f"alert:{signal_type}",
    )


def build_news_policy_event(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> MarketEvent:
    """Build a news or policy event from a headline-like payload."""

    data = payload_to_dict(payload)
    event_source = _source_from_payload(data, source, "news")
    event_time, warnings = _resolve_observed_at(data, observed_at)
    category = str(_first_value(data, "category", "type", "event_type") or "news")
    subject = _news_subject(data, category)
    title = str(_first_value(data, "title", "headline", "name") or "News/policy event")
    direction = normalize_direction(
        _first_value(data, "sentiment", "bias", "direction")
    )
    severity = normalize_severity(
        _first_value(data, "severity", "importance", "impact_level", "level")
    )

    return MarketEvent(
        event_type=MarketEventType.NEWS_POLICY_EVENT,
        subject=subject,
        title=title,
        observed_at=event_time,
        severity=severity,
        direction=direction,
        quality=quality_from_payload(
            data,
            source=event_source,
            observed_at=event_time,
            warnings=warnings,
        ),
        source=event_source,
        metrics=_numeric_mapping(_first_value(data, "metrics") or {}),
        context={
            "category": category,
            "summary": _first_value(data, "summary", "content", "description"),
            "url": _first_value(data, "url", "link"),
            "related_codes": _jsonable_list(
                _first_value(data, "related_codes", "codes")
            ),
            "related_sectors": _jsonable_list(
                _first_value(data, "related_sectors", "sectors")
            ),
        },
        tags=_news_tags(category),
        dedupe_key=f"news_policy:{category}:{title}",
    )


def build_events_from_screen_payload(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> list[MarketEvent]:
    """Build factor-hit events from a screen result payload."""

    data = payload_to_dict(payload)
    factor_checks = _first_value(data, "factor_checks")
    if not isinstance(factor_checks, Mapping):
        factor_checks = {}

    matched = _first_value(data, "matched_factors")
    if isinstance(matched, list):
        matched_factors = [str(item) for item in matched]
    else:
        matched_factors = [
            str(key)
            for key, value in factor_checks.items()
            if isinstance(value, Mapping) and value.get("matched")
        ]

    event_source = _source_from_payload(data, source, "screen")
    event_time, warnings = _resolve_observed_at(data, observed_at)
    subject = _stock_subject(data)
    events: list[MarketEvent] = []

    for factor_key in matched_factors:
        check = factor_checks.get(factor_key, {})
        if not isinstance(check, Mapping):
            check = {}
        factor_type = str(_first_value(check, "type") or "screen").lower()
        factor_name = str(_first_value(check, "name") or factor_key)
        weight = _first_float(check, "weight") or 0.0
        value = _first_float(check, "value")
        event_type = _screen_factor_event_type(factor_type, check, factor_key)

        if event_type == MarketEventType.FUND_FLOW_MOVE and value is not None:
            severity = severity_from_abs_amount(value)
        elif event_type == MarketEventType.VOLUME_SPIKE:
            severity = severity_from_volume_ratio(_screen_volume_ratio(data, check))
        else:
            severity = _severity_from_weight(weight)

        events.append(
            MarketEvent(
                event_type=event_type,
                subject=subject,
                title=f"{subject.key} screen factor matched: {factor_name}",
                observed_at=event_time,
                severity=severity,
                direction=direction_from_signed_value(weight),
                quality=quality_from_payload(
                    data,
                    source=event_source,
                    observed_at=event_time,
                    warnings=warnings,
                ),
                source=event_source,
                metrics={
                    "value": value,
                    "reference_value": _first_float(check, "reference_value"),
                    "previous_value": _first_float(check, "previous_value"),
                    "previous_reference_value": _first_float(
                        check,
                        "previous_reference_value",
                    ),
                    "weight": weight,
                    "matched": True,
                },
                context={
                    "factor_key": factor_key,
                    "factor_type": factor_type,
                    "field": _first_value(check, "field"),
                    "operator": _first_value(check, "operator"),
                    "threshold": _first_value(check, "threshold"),
                    "description": _first_value(check, "description"),
                },
                tags=("screen", factor_type, factor_key),
                dedupe_key=f"screen:{factor_key}",
            )
        )

    return events


def quality_from_payload(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | None = None,
    required_fields: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
) -> EventQuality:
    """Build event quality metadata from common payload fields."""

    data = payload_to_dict(payload)
    missing_fields = tuple(
        field for field in required_fields if _first_value(data, field) in (None, "")
    )
    raw_level = _first_value(data, "data_quality", "quality", "quality_level")
    level = normalize_quality_level(raw_level)
    if missing_fields and level in (DataQualityLevel.FULL, DataQualityLevel.UNKNOWN):
        level = DataQualityLevel.DEGRADED
    elif level == DataQualityLevel.UNKNOWN:
        level = DataQualityLevel.PARTIAL

    confidence = _first_float(data, "confidence", "quality_score")
    if confidence is None:
        confidence = 0.7 if missing_fields else 1.0

    as_of = (
        coerce_datetime(_first_value(data, "as_of", "updated_at", "timestamp"))
        or observed_at
    )

    return EventQuality(
        level=level,
        source=source or _source_from_payload(data, None, "unknown"),
        confidence=confidence,
        as_of=as_of,
        latency_seconds=_first_float(data, "latency_seconds", "latency"),
        warnings=warnings,
        missing_fields=missing_fields,
    )


def payload_to_dict(payload: Mapping[str, Any] | Any) -> dict[str, Any]:
    """Convert supported payload objects into a shallow dictionary."""

    if isinstance(payload, Mapping):
        return dict(payload)
    if is_dataclass(payload):
        result = asdict(cast(Any, payload))
        return result if isinstance(result, dict) else {}
    raw = getattr(payload, "__dict__", None)
    return dict(raw) if isinstance(raw, Mapping) else {}


def _resolve_observed_at(
    data: Mapping[str, Any],
    explicit: datetime | str | None,
) -> tuple[datetime, tuple[str, ...]]:
    observed_at = coerce_datetime(explicit) or coerce_datetime(
        _first_value(
            data,
            "observed_at",
            "timestamp",
            "datetime",
            "time",
            "updated_at",
            "scanned_at",
            "screened_at",
            "triggered_at",
            "published_at",
            "date",
            "trade_date",
        )
    )
    if observed_at is None:
        return _EPOCH, ("missing_observed_at",)
    return observed_at, ()


def _stock_subject(data: Mapping[str, Any]) -> EventSubject:
    return EventSubject(
        type=SubjectType.STOCK,
        code=_clean_code(_first_value(data, "code", "stock_code", "symbol")),
        name=_clean_string(_first_value(data, "name", "stock_name", "简称")),
    )


def _sector_subject(data: Mapping[str, Any]) -> EventSubject:
    return EventSubject(
        type=SubjectType.SECTOR,
        code=_clean_string(_first_value(data, "sector_code", "code", "板块代码")),
        name=_clean_string(
            _first_value(data, "sector_name", "industry", "name", "板块名称")
        ),
    )


def _fund_flow_subject(data: Mapping[str, Any]) -> EventSubject:
    if _first_value(data, "sector_name", "industry", "板块名称") is not None:
        return _sector_subject(data)
    if _first_value(data, "code", "stock_code", "symbol") is not None:
        return _stock_subject(data)
    return EventSubject(type=SubjectType.MARKET, name="A-share market")


def _news_subject(data: Mapping[str, Any], category: str) -> EventSubject:
    if _first_value(data, "code", "stock_code", "symbol") is not None:
        return _stock_subject(data)
    if _first_value(data, "sector_name", "industry", "板块名称") is not None:
        return _sector_subject(data)
    if "policy" in category.lower() or "政策" in category:
        return EventSubject(type=SubjectType.POLICY, name="Policy")
    return EventSubject(type=SubjectType.MARKET, name="A-share market")


def _extract_percent_change(data: Mapping[str, Any]) -> float | None:
    direct_keys = (
        "change_pct",
        "change_percent",
        "pct_chg",
        "pct_change",
        "涨跌幅",
    )
    direct = _first_float(data, *direct_keys)
    if direct is not None:
        return direct

    rate = _first_float(data, "change_rate", "return")
    if rate is not None:
        return rate * 100 if abs(rate) <= 1 else rate

    price = _first_float(data, "price", "close", "latest_price", "current", "最新价")
    prev_close = _first_float(data, "prev_close", "pre_close", "previous_close", "昨收")
    if price is None or prev_close is None or prev_close == 0.0:
        return None
    return (price - prev_close) / prev_close * 100


def _extract_volume_ratio(data: Mapping[str, Any]) -> float | None:
    ratio = _first_float(data, "volume_ratio", "vol_ratio", "量比")
    if ratio is not None:
        return ratio

    volume = _first_float(data, "volume", "vol", "成交量")
    avg_volume = _first_float(
        data,
        "vol_ma5",
        "volume_ma5",
        "avg_volume_5d",
        "average_volume",
    )
    if volume is None or avg_volume is None or avg_volume == 0.0:
        return None
    return volume / avg_volume


def _extract_net_flow(data: Mapping[str, Any]) -> float | None:
    return _first_float(
        data,
        "net_flow",
        "net_inflow",
        "main_net_inflow",
        "large_net_inflow",
        "north_net_inflow",
        "fund_flow",
        "资金净流入",
    )


def _screen_factor_event_type(
    factor_type: str,
    check: Mapping[str, Any],
    factor_key: str,
) -> MarketEventType:
    field = str(_first_value(check, "field") or "").lower()
    key = factor_key.lower()
    if factor_type == "capital_flow" or "inflow" in key or "flow" in field:
        return MarketEventType.FUND_FLOW_MOVE
    if "volume" in field or "volume" in key or key == "high_volume":
        return MarketEventType.VOLUME_SPIKE
    return MarketEventType.ALERT_TRIGGER


def _screen_volume_ratio(
    data: Mapping[str, Any], check: Mapping[str, Any]
) -> float | None:
    direct = _extract_volume_ratio(data)
    if direct is not None:
        return direct

    value = _first_float(check, "value")
    reference = _first_float(check, "reference_value")
    if value is None or reference is None or reference == 0.0:
        return None
    return value / reference


def _severity_from_weight(weight: float) -> EventSeverity:
    magnitude = abs(weight)
    if magnitude >= 2.0:
        return EventSeverity.IMPORTANT
    if magnitude >= 1.0:
        return EventSeverity.WATCH
    return EventSeverity.INFO


def _numeric_mapping(value: Mapping[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    for key, item in value.items():
        numeric = _coerce_float(item)
        if numeric is not None:
            result[str(key)] = numeric
    return result


def _source_from_payload(
    data: Mapping[str, Any],
    explicit: str | None,
    default: str,
) -> str:
    if explicit:
        return explicit
    source = _first_value(data, "source", "data_source", "provider")
    return str(source or default)


def _first_value(data: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data:
            value = data[key]
            if value is not None:
                return value
    return None


def _first_float(data: Mapping[str, Any], *keys: str) -> float | None:
    return _coerce_float(_first_value(data, *keys))


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clean_code(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _jsonable_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _news_tags(category: str) -> tuple[str, ...]:
    tags = ["news"]
    lowered = category.lower()
    if "policy" in lowered or "政策" in category:
        tags.append("policy")
    return tuple(tags)
