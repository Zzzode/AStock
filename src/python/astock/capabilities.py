"""Agent capability kernel.

This module is the Python layer's stable contract for agents and skills.
It returns JSON-serializable data packets and does not provide a human UI.
CLI and API entry points should stay thin adapters over these functions.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional, cast

from .backtest.engine import BacktestEngine
from .backtest.strategies import STRATEGIES
from .config import ConfigManager
from .data import get_industry_service
from .data_provenance import DataProvenance, combine_provenance
from .market_event import (
    MarketEvent,
    build_alert_trigger_event,
    build_events_from_quote_payload,
    build_events_from_screen_payload,
    build_events_from_signal_payload,
    build_fund_flow_event,
    build_news_policy_event,
    build_sector_move_event,
)
from .memory import FeedbackLearner
from .quote import QuoteService
from .recommend import Recommender, RecommendResult
from .research import (
    ResearchEntry,
    ResearchLedger,
    ResearchObservation,
    ResearchStatus,
    ResearchTrigger,
)
from .services import AnalysisService, TeamAnalysisService
from .stock_picker import ScreenResult, StockScreener
from .storage import Database

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "stocks.db"
DEFAULT_RESEARCH_LEDGER_PATH = PROJECT_ROOT / "data" / "research-ledger.json"


def _resolve_db_path(db_path: Optional[Path] = None) -> Path:
    return db_path or DEFAULT_DB_PATH


def _resolve_research_ledger_path(ledger_path: Optional[Path] = None) -> Path:
    return ledger_path or DEFAULT_RESEARCH_LEDGER_PATH


def _parse_date(value: Optional[str | date], default: date) -> date:
    if value is None:
        return default
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _parse_datetime(value: Optional[str | datetime], default: datetime) -> datetime:
    if value is None:
        return default
    if isinstance(value, datetime):
        return value
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


def _parse_research_status(value: str | ResearchStatus) -> ResearchStatus:
    if isinstance(value, ResearchStatus):
        return value
    return ResearchStatus(value)


def _serialize_events(events: Sequence[MarketEvent]) -> list[dict[str, Any]]:
    return [cast(dict[str, Any], event.to_dict()) for event in events]


def _quality_tier_from_label(label: Any) -> str:
    normalized = str(label or "").strip().lower()
    mapping = {
        "full_realtime": "realtime",
        "realtime": "realtime",
        "snapshot": "snapshot",
        "snapshot_degraded": "degraded",
        "partial": "snapshot",
        "daily_only": "delayed",
        "delayed": "delayed",
        "cache_only": "cached",
        "cached": "cached",
        "degraded": "degraded",
        "unavailable": "unavailable",
    }
    return mapping.get(normalized, "degraded" if normalized else "unavailable")


def _as_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def _payload_timestamp(payload: Mapping[str, Any]) -> str | datetime | None:
    for key in (
        "timestamp",
        "observed_at",
        "updated_at",
        "analyzed_at",
        "screened_at",
        "scanned_at",
        "trade_date",
        "date",
    ):
        value = payload.get(key)
        if value:
            return cast(str | datetime, value)
    return None


def _payload_source(payload: Mapping[str, Any], default: str) -> str:
    for key in ("source", "data_source", "provider"):
        value = payload.get(key)
        if value:
            return str(value)
    return default


def _packet_provenance(
    *,
    source: str,
    quality_label: Any,
    payload: Optional[Mapping[str, Any]] = None,
    warnings: Optional[Sequence[str | Mapping[str, object]]] = None,
    errors: Optional[Sequence[str | Mapping[str, object]]] = None,
) -> dict[str, Any]:
    payload = payload or {}
    return create_data_provenance_record(
        source=source,
        quality_tier=_quality_tier_from_label(quality_label),
        timestamp=_payload_timestamp(payload),
        warnings=warnings,
        errors=errors,
    )


def _safe_market_events(
    payload: Mapping[str, Any] | Any,
    *,
    payload_type: str,
    source: Optional[str] = None,
) -> list[dict[str, Any]]:
    event_packet = build_market_event_packet(
        payload,
        payload_type=payload_type,
        source=source,
    )
    if not event_packet.get("success"):
        return []
    return cast(list[dict[str, Any]], event_packet.get("events", []))


def _enrich_quote_packet(quote: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(quote)
    source = _payload_source(result, "astock.quote_service")
    quality_label = result.get("data_quality", "unavailable")
    result["provenance"] = _packet_provenance(
        source=source,
        quality_label=quality_label,
        payload=result,
        warnings=[
            item
            for item in _as_string_list(result.get("warnings"))
            if item not in {"", "None"}
        ],
        errors=_as_string_list(result.get("error")),
    )
    result["market_events"] = _safe_market_events(
        result,
        payload_type="quote",
        source=source,
    )
    return result


def _enrich_analysis_packet(analysis: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(analysis)
    quote = result.get("quote")
    quote_packet = (
        _enrich_quote_packet(cast(Mapping[str, Any], quote))
        if isinstance(quote, Mapping)
        else {}
    )
    if quote_packet:
        result["quote"] = quote_packet

    quality = result.get("data_quality", {})
    analysis_quality = (
        cast(Mapping[str, Any], quality).get("daily", "daily_only")
        if isinstance(quality, Mapping)
        else "daily_only"
    )
    analysis_provenance = _packet_provenance(
        source="astock.analysis_service",
        quality_label=analysis_quality,
        payload=result,
        errors=_as_string_list(result.get("error")),
    )
    source_records = [analysis_provenance]
    if quote_packet.get("provenance"):
        source_records.append(cast(dict[str, Any], quote_packet["provenance"]))

    result["provenance"] = combine_data_provenance_records(
        source_records,
        source="astock.analysis_packet",
        timestamp=result.get("analyzed_at") or datetime.now().astimezone(),
    )

    signal_payload = {
        "code": result.get("code"),
        "name": result.get("name"),
        "latest": result.get("indicators", {}),
        "signals": result.get("signals", []),
        "data_quality": analysis_quality,
        "analyzed_at": result.get("analyzed_at"),
    }
    result["market_events"] = [
        *cast(list[dict[str, Any]], quote_packet.get("market_events", [])),
        *_safe_market_events(
            signal_payload,
            payload_type="signal",
            source="astock.analysis_service",
        ),
    ]
    return result


def _enrich_screen_result_packet(screen_result: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(screen_result)
    source = _payload_source(result, "astock.stock_picker")
    result["provenance"] = _packet_provenance(
        source=source,
        quality_label=result.get("data_quality", "daily_only"),
        payload=result,
        errors=_as_string_list(result.get("error")),
    )
    result["market_events"] = _safe_market_events(
        result,
        payload_type="screen",
        source=source,
    )
    return result


def _enrich_screen_packet(screen_packet: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(screen_packet)
    enriched_results = [
        _enrich_screen_result_packet(cast(Mapping[str, Any], item))
        for item in result.get("results", [])
        if isinstance(item, Mapping)
    ]
    result["results"] = enriched_results
    result["market_events"] = [
        event
        for item in enriched_results
        for event in cast(list[dict[str, Any]], item.get("market_events", []))
    ]
    result["provenance"] = _packet_provenance(
        source="astock.stock_picker",
        quality_label=result.get("data_quality", "daily_only"),
        payload=result,
        errors=_as_string_list(result.get("error")),
    )
    return result


def _enrich_team_packet(team_result: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(team_result)
    packet = dict(cast(Mapping[str, Any], result.get("packet", {})))

    quote = packet.get("quote")
    if isinstance(quote, Mapping):
        packet["quote"] = _enrich_quote_packet(cast(Mapping[str, Any], quote))

    analysis = packet.get("analysis")
    if isinstance(analysis, Mapping):
        packet["analysis"] = _enrich_analysis_packet(cast(Mapping[str, Any], analysis))

    screen = packet.get("screen")
    if isinstance(screen, Mapping):
        packet["screen"] = _enrich_screen_packet(cast(Mapping[str, Any], screen))

    market_events: list[dict[str, Any]] = []
    provenance_records: list[Mapping[str, object]] = []
    for key in ("quote", "analysis", "screen"):
        value = packet.get(key)
        if not isinstance(value, Mapping):
            continue
        provenance = value.get("provenance")
        if isinstance(provenance, Mapping):
            provenance_records.append(cast(Mapping[str, object], provenance))
        market_events.extend(cast(list[dict[str, Any]], value.get("market_events", [])))

    if provenance_records:
        packet["provenance"] = combine_data_provenance_records(
            provenance_records,
            source="astock.team_packet",
            timestamp=result.get("analyzed_at") or datetime.now().astimezone(),
        )
    else:
        packet["provenance"] = _packet_provenance(
            source="astock.team_packet",
            quality_label="unavailable" if result.get("error") else "degraded",
            payload=result,
            warnings=_as_string_list(result.get("warnings")),
            errors=_as_string_list(result.get("error")),
        )
    packet["market_events"] = market_events

    result["packet"] = packet
    result["provenance"] = packet["provenance"]
    result["market_events"] = market_events
    return result


def _serialize_screen_result(
    result: ScreenResult,
    industry: Optional[str] = None,
    industry_change: Optional[float] = None,
) -> dict[str, Any]:
    return {
        "code": result.code,
        "name": result.name,
        "matched_factors": result.matched_factors,
        "matched_factor_count": result.matched_factor_count,
        "factor_checks": result.factor_checks,
        "data": result.data,
        "industry": industry,
        "industry_change": industry_change,
        "screened_at": result.screened_at.isoformat(),
    }


def serialize_recommend_result(result: RecommendResult) -> dict[str, Any]:
    """Serialize a recommendation candidate-pool result."""
    return {
        "success": result.success,
        "total": result.total,
        "error": result.error,
        "config_used": result.config_used,
        "selection_context": result.selection_context,
        "candidates": [
            {
                "code": candidate.code,
                "name": candidate.name,
                "matched_factors": candidate.matched_factors,
                "matched_factor_count": candidate.matched_factor_count,
                "factor_checks": candidate.factor_checks,
                "industry": candidate.industry,
                "industry_change": candidate.industry_change,
                "data": candidate.data,
                "collected_at": candidate.collected_at.isoformat(),
            }
            for candidate in result.candidates
        ],
    }


def create_data_provenance_record(
    *,
    source: str,
    quality_tier: str,
    timestamp: Optional[str | datetime] = None,
    latency_ms: Optional[int | float] = None,
    fallback_path: Optional[Sequence[str] | str] = None,
    warnings: Optional[Sequence[str | Mapping[str, object]]] = None,
    errors: Optional[Sequence[str | Mapping[str, object]]] = None,
) -> dict[str, Any]:
    """Return a JSON-ready data provenance record for an agent packet."""
    record = DataProvenance(
        source=source,
        timestamp=timestamp or datetime.now().astimezone(),
        quality_tier=quality_tier,
        latency_ms=latency_ms,
        fallback_path=fallback_path or (),
        warnings=warnings or (),
        errors=errors or (),
    )
    return cast(dict[str, Any], record.to_dict())


def combine_data_provenance_records(
    records: Sequence[Mapping[str, object]],
    *,
    source: str,
    timestamp: Optional[str | datetime] = None,
    quality_tier: Optional[str] = None,
) -> dict[str, Any]:
    """Combine source provenance records for a derived agent packet."""
    parsed_records = [DataProvenance.from_dict(record) for record in records]
    combined = combine_provenance(
        parsed_records,
        source=source,
        timestamp=timestamp or datetime.now().astimezone(),
        quality_tier=quality_tier,
    )
    return cast(dict[str, Any], combined.to_dict())


def build_market_event_packet(
    payload: Mapping[str, Any] | Any,
    *,
    payload_type: str,
    source: Optional[str] = None,
    observed_at: Optional[str | datetime] = None,
    price_threshold_pct: float = 2.0,
    volume_threshold_ratio: float = 2.0,
    fund_flow_threshold_amount: float = 100_000_000.0,
    sector_threshold_pct: float = 1.5,
) -> dict[str, Any]:
    """Normalize raw market data into canonical market events."""
    normalized_type = payload_type.strip().lower()
    events: list[MarketEvent] = []

    if normalized_type == "quote":
        events = build_events_from_quote_payload(
            payload,
            source=source,
            observed_at=observed_at,
            price_threshold_pct=price_threshold_pct,
            volume_threshold_ratio=volume_threshold_ratio,
            fund_flow_threshold_amount=fund_flow_threshold_amount,
        )
    elif normalized_type == "screen":
        events = build_events_from_screen_payload(
            payload,
            source=source,
            observed_at=observed_at,
        )
    elif normalized_type in {"signal", "technical_signal"}:
        events = build_events_from_signal_payload(
            payload,
            source=source,
            observed_at=observed_at,
        )
    elif normalized_type == "sector":
        event = build_sector_move_event(
            payload,
            source=source,
            observed_at=observed_at,
            threshold_pct=sector_threshold_pct,
        )
        events = [event] if event else []
    elif normalized_type in {"fund_flow", "flow"}:
        event = build_fund_flow_event(
            payload,
            source=source,
            observed_at=observed_at,
            threshold_amount=fund_flow_threshold_amount,
        )
        events = [event] if event else []
    elif normalized_type == "alert":
        events = [
            build_alert_trigger_event(
                payload,
                source=source,
                observed_at=observed_at,
            )
        ]
    elif normalized_type in {"news", "policy", "news_policy"}:
        events = [
            build_news_policy_event(
                payload,
                source=source,
                observed_at=observed_at,
            )
        ]
    else:
        return {
            "success": False,
            "error": f"Unsupported market event payload_type: {payload_type}",
            "supported_payload_types": [
                "quote",
                "screen",
                "signal",
                "sector",
                "fund_flow",
                "alert",
                "news_policy",
            ],
            "events": [],
            "event_count": 0,
        }

    return {
        "success": True,
        "schema_version": "market_event.packet.v1",
        "payload_type": normalized_type,
        "event_count": len(events),
        "events": _serialize_events(events),
    }


def create_research_entry(
    *,
    title: str,
    thesis: str,
    targets: Sequence[str],
    target_type: str = "stock",
    catalysts: Optional[Sequence[str]] = None,
    risks: Optional[Sequence[str]] = None,
    monitoring_triggers: Optional[Sequence[Mapping[str, Any]]] = None,
    invalidation_conditions: Optional[Sequence[str]] = None,
    tags: Optional[Sequence[str]] = None,
    data_quality: Optional[Mapping[str, Any]] = None,
    source_refs: Optional[Sequence[Mapping[str, Any]]] = None,
    metadata: Optional[Mapping[str, Any]] = None,
    created_by: str = "agent",
    ledger_path: Optional[Path] = None,
    overwrite: bool = False,
) -> dict[str, Any]:
    """Create a persistent research opportunity entry for agent follow-up."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    entry = ResearchEntry(
        title=title,
        thesis=thesis,
        targets=list(targets),
        target_type=target_type,
        catalysts=list(catalysts or []),
        risks=list(risks or []),
        monitoring_triggers=[
            ResearchTrigger.from_dict(dict(trigger))
            for trigger in monitoring_triggers or []
        ],
        invalidation_conditions=list(invalidation_conditions or []),
        tags=list(tags or []),
        data_quality=dict(data_quality or {}),
        source_refs=[dict(item) for item in source_refs or []],
        metadata=dict(metadata or {}),
        created_by=created_by,
    )
    created = ResearchLedger(resolved_path).create(entry, overwrite=overwrite)
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "entry": created.to_dict(),
    }


def get_research_entry(
    entry_id: str,
    *,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return one research ledger entry by ID."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    entry = ResearchLedger(resolved_path).get(entry_id)
    return {
        "success": entry is not None,
        "ledger_path": str(resolved_path),
        "entry": entry.to_dict() if entry else None,
    }


def list_research_entries(
    *,
    status: Optional[str | ResearchStatus] = None,
    target: Optional[str] = None,
    tag: Optional[str] = None,
    limit: int = 50,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """List research ledger entries for agent planning and follow-up."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    parsed_status = _parse_research_status(status) if status is not None else None
    entries = ResearchLedger(resolved_path).list_entries(
        status=parsed_status,
        target=target,
        tag=tag,
        limit=limit,
    )
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "total": len(entries),
        "entries": [entry.to_dict() for entry in entries],
    }


def record_research_observation(
    entry_id: str,
    *,
    observation_type: str,
    note: str,
    observed_at: Optional[str | datetime] = None,
    evidence: Optional[Mapping[str, Any]] = None,
    status_after: Optional[str | ResearchStatus] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Append follow-up evidence to a research ledger entry."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    observation = ResearchObservation(
        observation_type=observation_type,
        note=note,
        observed_at=_parse_datetime(observed_at, datetime.now()),
        evidence=dict(evidence or {}),
        status_after=(
            _parse_research_status(status_after) if status_after is not None else None
        ),
    )
    entry = ResearchLedger(resolved_path).record_observation(entry_id, observation)
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "entry": entry.to_dict(),
    }


def update_research_status(
    entry_id: str,
    status: str | ResearchStatus,
    *,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Update the lifecycle state for a research ledger entry."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    entry = ResearchLedger(resolved_path).update_status(
        entry_id,
        _parse_research_status(status),
    )
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "entry": entry.to_dict(),
    }


async def initialize_database(
    *,
    skip_refresh: bool = False,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Initialize local storage for agent capabilities."""
    resolved_db_path = _resolve_db_path(db_path)
    resolved_db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(str(resolved_db_path))
    await db.connect()
    try:
        await db.init_tables()
        loaded_count = 0
        if not skip_refresh:
            loaded_count = await QuoteService(db).refresh_stocks()
        return {
            "success": True,
            "loaded_count": loaded_count,
            "db_path": str(resolved_db_path),
        }
    finally:
        await db.close()


async def get_quote(code: str, *, db_path: Optional[Path] = None) -> dict[str, Any]:
    """Fetch a real-time or degraded quote packet."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        quote = cast(dict[str, Any], await QuoteService(db).get_realtime(code))
        return _enrich_quote_packet(quote)
    finally:
        await db.close()


async def analyze_stock(
    code: str,
    *,
    days: int = 100,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return technical-analysis data for agent reasoning."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        service = AnalysisService(db)
        result = await service.analyze(code, days=days)
        return _enrich_analysis_packet(cast(dict[str, Any], service.to_dict(result)))
    finally:
        await db.close()


async def build_team_packet(
    code: str,
    *,
    question: str,
    days: int = 100,
    user_id: str = "default",
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return the unified packet consumed by the Agent team."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        service = TeamAnalysisService(db)
        result = await service.analyze(
            code, question=question, days=days, user_id=user_id
        )
        return _enrich_team_packet(cast(dict[str, Any], service.to_dict(result)))
    finally:
        await db.close()


async def screen_stocks(
    *,
    factors: Optional[list[str]] = None,
    codes: Optional[list[str]] = None,
    include_industries: Optional[list[str]] = None,
    exclude_industries: Optional[list[str]] = None,
    limit: int = 10,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return stock-screening snapshots and factor hit details."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        quote_service = QuoteService(db)
        screener = StockScreener(quote_service)
        results = await screener.screen(factors=factors, codes=codes, limit=limit)

        industry_service = get_industry_service()
        await industry_service.initialize(allow_stale_cache=bool(codes))

        if include_industries or exclude_industries:
            result_codes = [result.code for result in results]
            filtered_codes = await industry_service.filter_by_industry(
                result_codes,
                include_industries=include_industries,
                exclude_industries=exclude_industries,
            )
            results = [result for result in results if result.code in filtered_codes]

        enriched_results: list[dict[str, Any]] = []
        for result in results:
            stock_industry = await industry_service.get_stock_industry(result.code)
            result_packet = _serialize_screen_result(
                result,
                industry=stock_industry.industry if stock_industry else None,
                industry_change=(
                    stock_industry.industry_change if stock_industry else None
                ),
            )
            enriched_results.append(_enrich_screen_result_packet(result_packet))

        return {
            "provenance": _packet_provenance(
                source="astock.stock_picker",
                quality_label="daily_only",
                warnings=[],
            ),
            "market_events": [
                event
                for item in enriched_results
                for event in cast(
                    list[dict[str, Any]],
                    item.get("market_events", []),
                )
            ],
            "total": len(enriched_results),
            "mode": "single_stock" if codes else "market_scan",
            "data_quality": "daily_only",
            "requested_factors": factors or [],
            "results": enriched_results,
        }
    finally:
        await db.close()


async def build_recommendation_pool(
    *,
    user_id: str = "default",
    limit: int = 10,
    options: Optional[dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return personalized candidate-pool data without final recommendations."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        quote_service = QuoteService(db)
        screener = StockScreener(quote_service)
        industry_service = get_industry_service()
        await industry_service.initialize()
        recommender = Recommender(screener, industry_service)
        result = await recommender.handle_recommend(
            user_id=user_id,
            limit=limit,
            options=options,
        )
        return serialize_recommend_result(result)
    finally:
        await db.close()


async def run_signal_backtest(
    code: str,
    *,
    strategy: str,
    start_date: Optional[str | date] = None,
    end_date: Optional[str | date] = None,
    capital: float = 100000.0,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run historical technical-signal backtesting for agent evaluation."""
    if strategy not in STRATEGIES:
        return {
            "error": f"Unknown strategy name '{strategy}'",
            "available_strategies": list(STRATEGIES.keys()),
        }

    end_dt = _parse_date(end_date, date.today())
    start_dt = _parse_date(start_date, end_dt - timedelta(days=365))

    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        df = await QuoteService(db).get_daily(code)
        if df.empty:
            return {"error": "No data"}

        if "date" in df.columns:
            df["date"] = df["date"].apply(
                lambda item: (
                    datetime.strptime(item, "%Y-%m-%d").date()
                    if isinstance(item, str)
                    else item
                )
            )
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]
        else:
            df = df.iloc[-365:]

        if df.empty:
            return {"error": "No data in the specified date range"}

        result = BacktestEngine().run(
            df,
            strategy_name=strategy,
            initial_capital=capital,
        )
        result.code = code
        return cast(dict[str, Any], result.to_dict())
    finally:
        await db.close()


def list_signal_strategies() -> list[dict[str, str]]:
    """Return available backtest strategy metadata."""
    return [
        {"name": name, "description": strategy.description}
        for name, strategy in STRATEGIES.items()
    ]


async def record_team_feedback(
    code: str,
    *,
    action: str,
    outcome: str,
    strategy: Optional[str] = None,
    signals: Optional[list[str]] = None,
    note: Optional[str] = None,
) -> dict[str, Any]:
    """Record outcome feedback for future agent reasoning."""
    record = await FeedbackLearner().record_feedback(
        code=code,
        action=action,
        outcome=outcome,
        strategy=strategy,
        signals=signals,
        note=note,
    )
    return {
        "code": record.code,
        "action": record.action,
        "outcome": record.outcome,
        "strategy": record.strategy,
        "signals": record.signals,
        "note": record.note,
        "created_at": record.created_at.isoformat(),
    }


def load_user_config(user_id: str = "default") -> dict[str, Any]:
    """Load user config as a JSON-ready dictionary."""
    config = ConfigManager().load(user_id)
    data = config.model_dump()
    data["trading_style"] = config.trading_style.value
    data["risk_level"] = config.risk_level.value
    return cast(dict[str, Any], data)
