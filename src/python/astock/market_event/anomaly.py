"""Fund-flow snapshot normalization and deterministic anomaly detection."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from .builders import payload_to_dict, quality_from_payload
from .models import (
    EventDirection,
    EventQuality,
    EventSeverity,
    EventSubject,
    JSONValue,
    MarketEvent,
    MarketEventType,
    SubjectType,
    coerce_datetime,
    direction_from_signed_value,
    max_severity,
    normalize_subject_type,
    severity_from_abs_amount,
    severity_from_percent_change,
    severity_from_volume_ratio,
)

_EPOCH = datetime.fromtimestamp(0, tz=timezone.utc)


@dataclass(frozen=True)
class FundFlowThresholds:
    """Thresholds used by deterministic anomaly detection."""

    price_breakout_pct: float = 3.0
    volume_spike_ratio: float = 2.5
    fund_flow_amount: float = 100_000_000.0
    fund_flow_ratio: float = 3.0
    flow_price_divergence_amount: float = 100_000_000.0
    flow_price_divergence_pct: float = 1.0
    sector_rotation_amount: float = 200_000_000.0
    sector_rotation_pct: float = 1.0
    sector_rotation_rank_delta: float = 5.0
    sector_rotation_score: float = 0.7
    risk_release_score: float = 0.7
    risk_release_limit_down_drop: float = 10.0


@dataclass(frozen=True)
class FundFlowSnapshot:
    """Canonical JSON-ready stock, sector, index, or market fund-flow snapshot."""

    subject: EventSubject
    observed_at: datetime
    source: str
    quality: EventQuality
    metrics: Mapping[str, JSONValue] = field(default_factory=dict)
    context: Mapping[str, JSONValue] = field(default_factory=dict)

    @property
    def net_flow(self) -> float | None:
        """Return the primary net-flow amount in CNY when available."""

        return _metric_float(self.metrics, "net_flow")

    @property
    def change_pct(self) -> float | None:
        """Return percentage price change when available."""

        return _metric_float(self.metrics, "change_pct")

    @property
    def volume_ratio(self) -> float | None:
        """Return volume expansion ratio when available."""

        return _metric_float(self.metrics, "volume_ratio")

    def to_dict(self) -> dict[str, JSONValue]:
        """Return a JSON-ready snapshot packet."""

        return {
            "subject": self.subject.to_dict(),
            "observed_at": self.observed_at.isoformat(),
            "source": self.source,
            "quality": self.quality.to_dict(),
            "metrics": dict(self.metrics),
            "context": dict(self.context),
        }


def normalize_fund_flow_snapshot(
    payload: Mapping[str, Any] | Any,
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> FundFlowSnapshot:
    """Normalize a raw stock, sector, index, or market fund-flow payload."""

    data = payload_to_dict(payload)
    event_source = source or _clean_string(_first_value(data, "source", "provider"))
    event_source = event_source or "fund_flow"
    event_time = _resolve_observed_at(data, observed_at)
    subject = _subject_from_payload(data)
    metrics = _normalize_metrics(data)

    quality = quality_from_payload(
        data,
        source=event_source,
        observed_at=event_time,
        warnings=() if event_time != _EPOCH else ("missing_observed_at",),
    )

    context = _json_ready_mapping(
        {
            "snapshot_type": subject.type.value,
            "industry": _first_value(data, "industry", "industry_name"),
            "sector_name": _first_value(data, "sector_name"),
            "theme": _first_value(data, "theme", "concept", "concept_name"),
            "leaders": _json_ready_sequence(
                _first_value(data, "leaders", "leading_stocks", "top_stocks")
            ),
            "laggards": _json_ready_sequence(
                _first_value(data, "laggards", "lagging_stocks")
            ),
            "rotation_sectors": _json_ready_sequence(
                _first_value(data, "rotation_sectors", "leading_sectors")
            ),
            "risk_release": _first_value(
                data,
                "risk_release",
                "is_risk_release",
                "market_risk_release",
            ),
        }
    )

    return FundFlowSnapshot(
        subject=subject,
        observed_at=event_time,
        source=event_source,
        quality=quality,
        metrics=metrics,
        context=context,
    )


def normalize_fund_flow_snapshots(
    payloads: Iterable[Mapping[str, Any] | Any],
    *,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> list[FundFlowSnapshot]:
    """Normalize multiple fund-flow payloads into snapshot packets."""

    return [
        normalize_fund_flow_snapshot(
            payload,
            source=source,
            observed_at=observed_at,
        )
        for payload in payloads
    ]


def detect_market_anomalies(
    payload: Mapping[str, Any] | Any,
    *,
    thresholds: FundFlowThresholds | None = None,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> list[MarketEvent]:
    """Detect deterministic market anomalies from one fund-flow payload."""

    snapshot = normalize_fund_flow_snapshot(
        payload,
        source=source,
        observed_at=observed_at,
    )
    return detect_market_anomalies_from_snapshot(
        snapshot,
        thresholds=thresholds,
    )


def detect_market_anomalies_from_snapshot(
    snapshot: FundFlowSnapshot,
    *,
    thresholds: FundFlowThresholds | None = None,
) -> list[MarketEvent]:
    """Detect deterministic market anomalies from a normalized snapshot."""

    limits = thresholds or FundFlowThresholds()
    events: list[MarketEvent] = []

    price_event = _detect_price_breakout(snapshot, limits)
    if price_event is not None:
        events.append(price_event)

    volume_event = _detect_volume_spike(snapshot, limits)
    if volume_event is not None:
        events.append(volume_event)

    flow_event = _detect_fund_flow_move(snapshot, limits)
    if flow_event is not None:
        events.append(flow_event)

    divergence_event = _detect_flow_price_divergence(snapshot, limits)
    if divergence_event is not None:
        events.append(divergence_event)

    rotation_event = _detect_sector_rotation(snapshot, limits)
    if rotation_event is not None:
        events.append(rotation_event)

    risk_release_event = _detect_risk_release(snapshot, limits)
    if risk_release_event is not None:
        events.append(risk_release_event)

    return events


def build_fund_flow_anomaly_packet(
    payload: Mapping[str, Any] | Any,
    *,
    thresholds: FundFlowThresholds | None = None,
    source: str | None = None,
    observed_at: datetime | str | None = None,
) -> dict[str, JSONValue]:
    """Return a JSON-ready snapshot plus detected canonical market events."""

    snapshot = normalize_fund_flow_snapshot(
        payload,
        source=source,
        observed_at=observed_at,
    )
    events = detect_market_anomalies_from_snapshot(
        snapshot,
        thresholds=thresholds,
    )
    return {
        "snapshot": snapshot.to_dict(),
        "market_events": market_events_to_packet(events),
        "event_count": len(events),
    }


def market_events_to_packet(
    events: Iterable[MarketEvent],
) -> list[dict[str, JSONValue]]:
    """Convert market events into JSON-ready dictionaries."""

    return [event.to_dict() for event in events]


def _detect_price_breakout(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> MarketEvent | None:
    change_pct = snapshot.change_pct
    if change_pct is None or abs(change_pct) < thresholds.price_breakout_pct:
        return None

    if change_pct > 0:
        anomaly_type = "price_breakout"
        title = f"{snapshot.subject.key} price breakout {change_pct:+.2f}%"
    else:
        anomaly_type = "price_breakdown"
        title = f"{snapshot.subject.key} price breakdown {change_pct:+.2f}%"

    return _build_event(
        snapshot,
        event_type=MarketEventType.PRICE_MOVE,
        title=title,
        severity=severity_from_percent_change(
            change_pct,
            watch_pct=thresholds.price_breakout_pct,
        ),
        direction=direction_from_signed_value(change_pct),
        metrics=_pick_metrics(
            snapshot,
            "price",
            "prev_close",
            "change_pct",
            "turnover",
            "net_flow",
        ),
        context={"anomaly_type": anomaly_type},
        tags=("anomaly", "price", anomaly_type),
        dedupe_key=f"anomaly:{anomaly_type}",
    )


def _detect_volume_spike(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> MarketEvent | None:
    ratio = snapshot.volume_ratio
    if ratio is None or ratio < thresholds.volume_spike_ratio:
        return None

    return _build_event(
        snapshot,
        event_type=MarketEventType.VOLUME_SPIKE,
        title=f"{snapshot.subject.key} volume spike {ratio:.2f}x",
        severity=severity_from_volume_ratio(
            ratio,
            watch_ratio=thresholds.volume_spike_ratio,
        ),
        direction=direction_from_signed_value(snapshot.change_pct),
        metrics=_pick_metrics(
            snapshot,
            "volume",
            "avg_volume",
            "volume_ratio",
            "change_pct",
            "net_flow",
        ),
        context={"anomaly_type": "volume_spike"},
        tags=("anomaly", "volume"),
        dedupe_key="anomaly:volume_spike",
    )


def _detect_fund_flow_move(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> MarketEvent | None:
    net_flow = snapshot.net_flow
    net_flow_ratio = _metric_float(snapshot.metrics, "net_flow_ratio")
    has_amount_signal = (
        net_flow is not None and abs(net_flow) >= thresholds.fund_flow_amount
    )
    has_ratio_signal = (
        net_flow_ratio is not None and abs(net_flow_ratio) >= thresholds.fund_flow_ratio
    )
    if not has_amount_signal and not has_ratio_signal:
        return None

    direction = direction_from_signed_value(
        net_flow if net_flow is not None else net_flow_ratio
    )
    anomaly_type = "fund_flow_surge"
    if direction == EventDirection.BEARISH:
        anomaly_type = "fund_flow_outflow"

    amount_severity = severity_from_abs_amount(
        net_flow,
        watch_amount=thresholds.fund_flow_amount,
    )
    severity = amount_severity if has_amount_signal else EventSeverity.WATCH

    flow_word = "inflow" if direction == EventDirection.BULLISH else "outflow"
    return _build_event(
        snapshot,
        event_type=MarketEventType.FUND_FLOW_MOVE,
        title=f"{snapshot.subject.key} fund {flow_word} anomaly",
        severity=severity,
        direction=direction,
        metrics=_pick_metrics(
            snapshot,
            "net_flow",
            "net_flow_ratio",
            "main_net_inflow",
            "large_net_inflow",
            "north_net_inflow",
            "turnover",
            "change_pct",
        ),
        context={
            "anomaly_type": anomaly_type,
            "flow_direction": flow_word,
            "amount_threshold": thresholds.fund_flow_amount,
            "ratio_threshold": thresholds.fund_flow_ratio,
        },
        tags=("anomaly", "fund_flow", anomaly_type),
        dedupe_key=f"anomaly:{anomaly_type}",
    )


def _detect_flow_price_divergence(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> MarketEvent | None:
    net_flow = snapshot.net_flow
    change_pct = snapshot.change_pct
    if net_flow is None or change_pct is None:
        return None
    if abs(net_flow) < thresholds.flow_price_divergence_amount:
        return None
    if abs(change_pct) < thresholds.flow_price_divergence_pct:
        return None

    bullish_flow_falling_price = net_flow > 0 and change_pct < 0
    bearish_flow_rising_price = net_flow < 0 and change_pct > 0
    if not bullish_flow_falling_price and not bearish_flow_rising_price:
        return None

    if bullish_flow_falling_price:
        divergence_type = "inflow_price_weakness"
        title = f"{snapshot.subject.key} inflow with price weakness"
    else:
        divergence_type = "outflow_price_strength"
        title = f"{snapshot.subject.key} outflow with price strength"

    return _build_event(
        snapshot,
        event_type=MarketEventType.FUND_FLOW_MOVE,
        title=title,
        severity=max_severity(
            severity_from_abs_amount(
                net_flow,
                watch_amount=thresholds.flow_price_divergence_amount,
            ),
            severity_from_percent_change(
                change_pct,
                watch_pct=thresholds.flow_price_divergence_pct,
            ),
        ),
        direction=EventDirection.MIXED,
        metrics=_pick_metrics(
            snapshot,
            "net_flow",
            "net_flow_ratio",
            "change_pct",
            "price",
            "prev_close",
            "turnover",
        ),
        context={
            "anomaly_type": "flow_price_divergence",
            "divergence_type": divergence_type,
            "amount_threshold": thresholds.flow_price_divergence_amount,
            "price_threshold_pct": thresholds.flow_price_divergence_pct,
        },
        tags=("anomaly", "fund_flow", "divergence"),
        dedupe_key=f"anomaly:flow_price_divergence:{divergence_type}",
    )


def _detect_sector_rotation(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> MarketEvent | None:
    if snapshot.subject.type not in {
        SubjectType.SECTOR,
        SubjectType.THEME,
        SubjectType.MARKET,
    }:
        return None

    net_flow = snapshot.net_flow
    change_pct = snapshot.change_pct
    rank_delta = _metric_float(snapshot.metrics, "sector_rank_delta")
    rotation_score = _metric_float(snapshot.metrics, "sector_rotation_score")
    rotation_count = _metric_float(snapshot.metrics, "rotation_sector_count")

    amount_rotation = (
        net_flow is not None
        and abs(net_flow) >= thresholds.sector_rotation_amount
        and change_pct is not None
        and abs(change_pct) >= thresholds.sector_rotation_pct
    )
    rank_rotation = (
        rank_delta is not None
        and abs(rank_delta) >= thresholds.sector_rotation_rank_delta
    )
    score_rotation = (
        rotation_score is not None
        and rotation_score >= thresholds.sector_rotation_score
    )
    list_rotation = rotation_count is not None and rotation_count >= 2
    if (
        not amount_rotation
        and not rank_rotation
        and not score_rotation
        and not list_rotation
    ):
        return None

    direction = _rotation_direction(net_flow, change_pct, rank_delta, rotation_score)
    return _build_event(
        snapshot,
        event_type=MarketEventType.SECTOR_MOVE,
        title=f"{snapshot.subject.key} sector rotation anomaly",
        severity=_rotation_severity(snapshot, thresholds),
        direction=direction,
        metrics=_pick_metrics(
            snapshot,
            "net_flow",
            "change_pct",
            "sector_rank",
            "sector_rank_delta",
            "sector_rotation_score",
            "rotation_sector_count",
            "turnover",
        ),
        context={
            "anomaly_type": "sector_rotation",
            "rotation_sectors": snapshot.context.get("rotation_sectors", []),
        },
        tags=("anomaly", "sector", "rotation"),
        dedupe_key="anomaly:sector_rotation",
    )


def _detect_risk_release(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> MarketEvent | None:
    explicit = _truthy(snapshot.context.get("risk_release"))
    score = _metric_float(snapshot.metrics, "risk_release_score")
    limit_down_change = _metric_float(snapshot.metrics, "limit_down_count_change")
    panic_change = _metric_float(snapshot.metrics, "panic_index_change")

    score_signal = score is not None and score >= thresholds.risk_release_score
    limit_down_signal = (
        limit_down_change is not None
        and limit_down_change <= -thresholds.risk_release_limit_down_drop
    )
    panic_signal = panic_change is not None and panic_change < 0
    if not explicit and not score_signal and not limit_down_signal and not panic_signal:
        return None

    return _build_event(
        snapshot,
        event_type=MarketEventType.ALERT_TRIGGER,
        title=f"{snapshot.subject.key} risk release anomaly",
        severity=EventSeverity.IMPORTANT if score_signal else EventSeverity.WATCH,
        direction=EventDirection.BULLISH,
        metrics=_pick_metrics(
            snapshot,
            "risk_release_score",
            "limit_down_count",
            "limit_down_count_change",
            "panic_index",
            "panic_index_change",
            "change_pct",
            "net_flow",
        ),
        context={"anomaly_type": "risk_release"},
        tags=("anomaly", "risk", "risk_release"),
        dedupe_key="anomaly:risk_release",
    )


def _build_event(
    snapshot: FundFlowSnapshot,
    *,
    event_type: MarketEventType,
    title: str,
    severity: EventSeverity,
    direction: EventDirection,
    metrics: Mapping[str, JSONValue],
    context: Mapping[str, JSONValue],
    tags: tuple[str, ...],
    dedupe_key: str,
) -> MarketEvent:
    return MarketEvent(
        event_type=event_type,
        subject=snapshot.subject,
        title=title,
        observed_at=snapshot.observed_at,
        severity=severity,
        direction=direction,
        quality=snapshot.quality,
        source=snapshot.source,
        metrics=metrics,
        context={
            **context,
            "snapshot_type": snapshot.subject.type.value,
        },
        tags=tags,
        dedupe_key=dedupe_key,
    )


def _normalize_metrics(data: Mapping[str, Any]) -> dict[str, JSONValue]:
    metrics = {
        "price": _first_float(data, "price", "close", "latest_price", "current"),
        "prev_close": _first_float(data, "prev_close", "pre_close", "previous_close"),
        "change_pct": _extract_change_pct(data),
        "volume": _first_float(data, "volume", "vol"),
        "avg_volume": _first_float(
            data,
            "avg_volume",
            "average_volume",
            "vol_ma5",
            "volume_ma5",
        ),
        "volume_ratio": _extract_volume_ratio(data),
        "turnover": _first_float(data, "turnover", "amount"),
        "net_flow": _extract_net_flow(data),
        "net_flow_ratio": _first_float(
            data,
            "net_flow_ratio",
            "main_net_inflow_ratio",
            "flow_ratio",
        ),
        "main_net_inflow": _first_float(data, "main_net_inflow", "main_net_flow"),
        "large_net_inflow": _first_float(data, "large_net_inflow"),
        "north_net_inflow": _first_float(data, "north_net_inflow"),
        "retail_net_inflow": _first_float(data, "retail_net_inflow"),
        "sector_rank": _first_float(data, "sector_rank", "rank"),
        "sector_rank_delta": _first_float(
            data,
            "sector_rank_delta",
            "rank_delta",
            "rank_change",
        ),
        "sector_rotation_score": _first_float(data, "sector_rotation_score"),
        "rotation_sector_count": _rotation_sector_count(data),
        "risk_release_score": _first_float(data, "risk_release_score"),
        "limit_down_count": _first_float(data, "limit_down_count"),
        "limit_down_count_change": _first_float(data, "limit_down_count_change"),
        "panic_index": _first_float(data, "panic_index"),
        "panic_index_change": _first_float(data, "panic_index_change"),
    }
    return _json_ready_mapping(metrics)


def _subject_from_payload(data: Mapping[str, Any]) -> EventSubject:
    explicit_type = _first_value(data, "subject_type", "type")
    subject_type = normalize_subject_type(explicit_type) if explicit_type else None
    if subject_type == SubjectType.UNKNOWN:
        subject_type = None
    code = _clean_string(
        _first_value(
            data,
            "code",
            "stock_code",
            "symbol",
            "sector_code",
            "index_code",
        )
    )
    name = _clean_string(
        _first_value(
            data,
            "name",
            "stock_name",
            "sector_name",
            "industry",
            "index_name",
            "theme",
        )
    )

    if subject_type is None:
        if _first_value(data, "code", "stock_code", "symbol") is not None:
            subject_type = SubjectType.STOCK
        elif _first_value(data, "sector_name", "industry", "sector_code") is not None:
            subject_type = SubjectType.SECTOR
        elif _first_value(data, "theme", "concept", "concept_name") is not None:
            subject_type = SubjectType.THEME
        elif _first_value(data, "index_code", "index_name") is not None:
            subject_type = SubjectType.INDEX
        else:
            subject_type = SubjectType.MARKET

    if subject_type == SubjectType.MARKET and name is None:
        name = "A-share market"

    return EventSubject(
        type=subject_type,
        code=code,
        name=name,
    )


def _resolve_observed_at(
    data: Mapping[str, Any],
    explicit: datetime | str | None,
) -> datetime:
    return (
        coerce_datetime(explicit)
        or coerce_datetime(
            _first_value(
                data,
                "observed_at",
                "timestamp",
                "datetime",
                "time",
                "updated_at",
                "as_of",
                "date",
                "trade_date",
            )
        )
        or _EPOCH
    )


def _extract_change_pct(data: Mapping[str, Any]) -> float | None:
    direct = _first_float(
        data,
        "change_pct",
        "change_percent",
        "pct_chg",
        "pct_change",
    )
    if direct is not None:
        return direct

    rate = _first_float(data, "change_rate", "return")
    if rate is not None:
        return rate * 100 if abs(rate) <= 1 else rate

    price = _first_float(data, "price", "close", "latest_price", "current")
    prev_close = _first_float(data, "prev_close", "pre_close", "previous_close")
    if price is None or prev_close is None or prev_close == 0.0:
        return None
    return (price - prev_close) / prev_close * 100


def _extract_volume_ratio(data: Mapping[str, Any]) -> float | None:
    ratio = _first_float(data, "volume_ratio", "vol_ratio")
    if ratio is not None:
        return ratio

    volume = _first_float(data, "volume", "vol")
    avg_volume = _first_float(
        data,
        "avg_volume",
        "average_volume",
        "vol_ma5",
        "volume_ma5",
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
    )


def _rotation_sector_count(data: Mapping[str, Any]) -> float | None:
    direct = _first_float(data, "rotation_sector_count", "leading_sector_count")
    if direct is not None:
        return direct
    sectors = _first_value(data, "rotation_sectors", "leading_sectors")
    if isinstance(sectors, list | tuple):
        return float(len(sectors))
    return None


def _rotation_direction(
    net_flow: float | None,
    change_pct: float | None,
    rank_delta: float | None,
    rotation_score: float | None,
) -> EventDirection:
    if net_flow is not None and net_flow != 0:
        return direction_from_signed_value(net_flow)
    if change_pct is not None and change_pct != 0:
        return direction_from_signed_value(change_pct)
    if rank_delta is not None and rank_delta != 0:
        return EventDirection.BULLISH if rank_delta > 0 else EventDirection.BEARISH
    if rotation_score is not None:
        return EventDirection.BULLISH
    return EventDirection.MIXED


def _rotation_severity(
    snapshot: FundFlowSnapshot,
    thresholds: FundFlowThresholds,
) -> EventSeverity:
    return max_severity(
        severity_from_abs_amount(
            snapshot.net_flow,
            watch_amount=thresholds.sector_rotation_amount,
        ),
        severity_from_percent_change(
            snapshot.change_pct,
            watch_pct=thresholds.sector_rotation_pct,
        ),
    )


def _pick_metrics(snapshot: FundFlowSnapshot, *keys: str) -> dict[str, JSONValue]:
    return {
        key: value for key in keys if (value := snapshot.metrics.get(key)) is not None
    }


def _metric_float(metrics: Mapping[str, JSONValue], key: str) -> float | None:
    return _coerce_float(metrics.get(key))


def _json_ready_mapping(values: Mapping[str, Any]) -> dict[str, JSONValue]:
    return {
        key: converted
        for key, value in values.items()
        if (converted := _json_ready(value)) is not None
    }


def _json_ready_sequence(value: Any) -> list[JSONValue]:
    if value is None:
        return []
    if isinstance(value, list | tuple):
        return [_json_ready(item) for item in value if _json_ready(item) is not None]
    converted = _json_ready(value)
    return [] if converted is None else [converted]


def _json_ready(value: Any) -> JSONValue:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, Mapping):
        return _json_ready_mapping(value)
    if isinstance(value, list | tuple):
        return _json_ready_sequence(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, str | int | bool):
        return value
    return str(value)


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


def _clean_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}
