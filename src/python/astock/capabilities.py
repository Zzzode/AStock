"""Agent capability kernel.

This module is the Python layer's stable contract for agents and skills.
It returns JSON-serializable data packets and does not provide a human UI.
CLI and API entry points should stay thin adapters over these functions.
"""

from __future__ import annotations

import hashlib
import json
import os
import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import fields
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional, cast

from .backtest.engine import BacktestEngine
from .backtest.model_validation import run_rolling_model_selection
from .backtest.frozen_signal import (
    build_frozen_signal_replay_input,
    parse_frozen_signal_replay_input,
)
from .backtest.frozen_portfolio import (
    build_frozen_portfolio_replay_input,
    parse_frozen_portfolio_replay_input,
)
from .backtest.portfolio_engine import PortfolioBacktestEngine
from .backtest.strategies import STRATEGIES
from .config import ConfigManager
from .data import (
    IndustryChainNode,
    MarketMapStore,
    MarketSubjectMapping,
    get_industry_service,
)
from .data_provenance import DataProvenance, combine_provenance
from .market_event import (
    EventStore,
    FundFlowThresholds,
    MarketEvent,
    build_alert_trigger_event,
    build_events_from_quote_payload,
    build_events_from_screen_payload,
    build_fund_flow_anomaly_packet as _build_fund_flow_anomaly_packet,
    build_fund_flow_event,
    build_news_policy_event,
    build_sector_move_event,
    detect_market_anomalies as _detect_market_anomalies,
    normalize_fund_flow_snapshot as _normalize_fund_flow_snapshot,
)
from .market_data import (
    JQDataMinuteAdapter,
    TushareProBacktestAdapter,
    build_public_market_observation_packet,
    verify_frozen_market_archive,
)
from .market_snapshot import MarketSnapshotService
from .market_rotation import (
    MarketRotationService,
    build_rotation_crowding_proxy,
    verify_rotation_history_evidence,
)
from .market_desk import (
    StrategyPlan,
    StrategyState,
    StrategyHorizon,
    record_strategy_plan_review,
    assess_market_regime,
    decide_investment_committee,
    evaluate_candidate_gate,
    evaluate_playbook,
    evaluate_observation_action,
    get_playbook,
    list_playbooks,
    transition_strategy_plan,
    review_paper_decision,
    RestrictedListEntry,
    RestrictedListStore,
    verify_paper_desk_release,
    build_public_desk_observation_run,
    create_public_desk_observation_exception_review,
    list_public_desk_observation_runs,
)
from .market_desk.discovery import (
    PublicMarketDiscoveryService,
    list_public_market_discovery_archives,
    verify_public_market_discovery_archive,
)
from .memory import FeedbackLearner
from .quote import AkShareClient, QuoteService
from .portfolio import PortfolioRiskInputBuilder
from .portfolio.governance import audit_paper_portfolio_governance
from .quality import (
    check_prompt_drift as _check_prompt_drift,
    evaluate_research_case_quality as _evaluate_research_case_quality,
    evaluate_report_quality as _evaluate_report_quality,
    evaluate_skill_response_cases as _evaluate_skill_response_cases,
    evaluate_source_health as _evaluate_source_health,
)
from .recommend import Recommender, RecommendResult
from .research import (
    EvidenceItem,
    EvidencePacket,
    EvidenceStance,
    PostmortemRootCause,
    ResearchEntry,
    ResearchLedger,
    ResearchLedgerIndex,
    ResearchObservation,
    ResearchPostmortem,
    ResearchStatus,
    ResearchTrigger,
    review_thesis,
)
from .services import AnalysisService, TeamAnalysisService
from .stock_picker import ScreenResult, StockScreener
from .storage import Database

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "stocks.db"
DEFAULT_RESEARCH_LEDGER_PATH = PROJECT_ROOT / "data" / "research-ledger.json"
DEFAULT_MARKET_EVENT_STORE_PATH = PROJECT_ROOT / "data" / "market-events.jsonl"
DEFAULT_MARKET_MAP_PATH = PROJECT_ROOT / "data" / "market-map.json"
DEFAULT_RESTRICTED_LIST_PATH = PROJECT_ROOT / "data" / "restricted-list.json"
DEFAULT_PORTFOLIO_PATH = PROJECT_ROOT / "data" / "portfolio.json"


def _resolve_db_path(db_path: Optional[Path] = None) -> Path:
    return db_path or DEFAULT_DB_PATH


def _resolve_research_ledger_path(ledger_path: Optional[Path] = None) -> Path:
    return ledger_path or DEFAULT_RESEARCH_LEDGER_PATH


def _resolve_market_event_store_path(event_store_path: Optional[Path] = None) -> Path:
    return event_store_path or DEFAULT_MARKET_EVENT_STORE_PATH


def _resolve_market_map_path(market_map_path: Optional[Path] = None) -> Path:
    return market_map_path or DEFAULT_MARKET_MAP_PATH


def _default_prompt_drift_pairs(
    root_path: Optional[Path] = None,
) -> list[dict[str, Any]]:
    root = root_path or PROJECT_ROOT
    agents_root = root / ".agents" / "skills"
    codex_root = root / ".codex" / "skills"
    if not agents_root.exists():
        return []

    pairs: list[dict[str, Any]] = []
    for skill_dir in sorted(agents_root.iterdir()):
        if not skill_dir.is_dir():
            continue
        agents_file = _first_existing_path(
            skill_dir / "skill.md",
            skill_dir / "SKILL.md",
        )
        codex_file = _first_existing_path(
            codex_root / skill_dir.name / "SKILL.md",
            codex_root / skill_dir.name / "skill.md",
        )
        if agents_file is None and codex_file is None:
            continue
        pairs.append(
            {
                "name": skill_dir.name,
                "left": str(agents_file or skill_dir / "skill.md"),
                "right": str(codex_file or codex_root / skill_dir.name / "SKILL.md"),
            }
        )
    return pairs


def _first_existing_path(*paths: Path) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


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


def _parse_research_statuses(
    values: Optional[Sequence[str | ResearchStatus] | str | ResearchStatus],
) -> list[ResearchStatus] | None:
    if values is None:
        return None
    if isinstance(values, (str, ResearchStatus)):
        return [_parse_research_status(values)]
    return [_parse_research_status(value) for value in values]


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
    timestamp_warnings = _as_string_list(result.get("warnings"))
    if _payload_timestamp(result) is None:
        # Public quote endpoints do not always expose the provider observation
        # time.  Preserve that distinction: timestamp the local observation and
        # surface a warning instead of emitting an epoch event timestamp.
        result["observed_at"] = datetime.now().astimezone().isoformat()
        timestamp_warnings.append(
            "Provider timestamp unavailable; assigned local observation timestamp."
        )
    result["provenance"] = _packet_provenance(
        source=source,
        quality_label=quality_label,
        payload=result,
        warnings=[
            item
            for item in timestamp_warnings
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

    result["market_events"] = [
        *cast(list[dict[str, Any]], quote_packet.get("market_events", [])),
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


def create_industry_chain_node(
    *,
    chain: str,
    stage: str,
    role: str = "",
    upstream: Optional[Sequence[str]] = None,
    downstream: Optional[Sequence[str]] = None,
    related_industries: Optional[Sequence[str]] = None,
    weight: Optional[float] = None,
    source_refs: Optional[Sequence[str]] = None,
) -> dict[str, Any]:
    """Build one JSON-ready industry-chain relationship node."""
    node = IndustryChainNode(
        chain=chain,
        stage=stage,
        role=role,
        upstream=list(upstream or []),
        downstream=list(downstream or []),
        related_industries=list(related_industries or []),
        weight=weight,
        source_refs=list(source_refs or []),
    )
    return {"success": True, "node": node.to_dict()}


def create_market_subject_mapping(
    mapping: Mapping[str, Any] | MarketSubjectMapping,
    *,
    market_map_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Create a persistent stock-to-market-relationship mapping."""
    resolved_path = _resolve_market_map_path(market_map_path)
    saved = MarketMapStore(resolved_path).create(mapping)
    return {
        "success": True,
        "market_map_path": str(resolved_path),
        "mapping": saved.to_dict(),
        "packet": saved.to_packet(),
    }


def upsert_market_subject_mapping(
    mapping: Mapping[str, Any] | MarketSubjectMapping,
    *,
    market_map_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Create or replace one stock-to-market-relationship mapping."""
    resolved_path = _resolve_market_map_path(market_map_path)
    saved = MarketMapStore(resolved_path).upsert(mapping)
    return {
        "success": True,
        "market_map_path": str(resolved_path),
        "mapping": saved.to_dict(),
        "packet": saved.to_packet(),
    }


def get_market_subject_mapping(
    code: str | int,
    *,
    market_map_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return one stored market relationship mapping by stock code."""
    resolved_path = _resolve_market_map_path(market_map_path)
    store = MarketMapStore(resolved_path)
    mapping = store.get(code)
    return {
        "success": mapping is not None,
        "market_map_path": str(resolved_path),
        "mapping": mapping.to_dict() if mapping else None,
        "packet": mapping.to_packet() if mapping else store.resolve(code),
    }


def list_market_subject_mappings(
    *,
    industry: Optional[str] = None,
    sector: Optional[str] = None,
    theme: Optional[str] = None,
    concept: Optional[str] = None,
    chain: Optional[str] = None,
    stage: Optional[str] = None,
    limit: Optional[int] = 100,
    market_map_path: Optional[Path] = None,
) -> dict[str, Any]:
    """List stock relationship mappings by industry, sector, theme, concept, or chain."""
    resolved_path = _resolve_market_map_path(market_map_path)
    store = MarketMapStore(resolved_path)
    has_filter = any([industry, sector, theme, concept, chain, stage])
    mappings = (
        store.filter(
            industry=industry,
            sector=sector,
            theme=theme,
            concept=concept,
            chain=chain,
            stage=stage,
        )
        if has_filter
        else store.list_mappings()
    )
    total = len(mappings)
    if limit is not None:
        mappings = mappings[: max(limit, 0)]

    return {
        "success": True,
        "market_map_path": str(resolved_path),
        "total": total,
        "returned": len(mappings),
        "mappings": [mapping.to_dict() for mapping in mappings],
        "packets": [mapping.to_packet() for mapping in mappings],
    }


def resolve_market_subject_context(
    code: str | int,
    *,
    market_map_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return an agent-facing relationship packet for one stock code."""
    resolved_path = _resolve_market_map_path(market_map_path)
    packet = MarketMapStore(resolved_path).resolve(code)
    return {
        "success": True,
        "market_map_path": str(resolved_path),
        **packet,
    }


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


def _parse_fund_flow_thresholds(
    thresholds: Optional[Mapping[str, Any] | FundFlowThresholds],
) -> FundFlowThresholds | None:
    if thresholds is None or isinstance(thresholds, FundFlowThresholds):
        return thresholds

    allowed_fields = {field.name for field in fields(FundFlowThresholds)}
    kwargs: dict[str, float] = {}
    for key, value in thresholds.items():
        if key not in allowed_fields or value is None:
            continue
        try:
            kwargs[key] = float(value)
        except (TypeError, ValueError) as exc:
            msg = f"fund-flow threshold must be numeric: {key}"
            raise ValueError(msg) from exc
    return FundFlowThresholds(**kwargs)


def normalize_fund_flow_snapshot_packet(
    payload: Mapping[str, Any] | Any,
    *,
    source: Optional[str] = None,
    observed_at: Optional[str | datetime] = None,
) -> dict[str, Any]:
    """Normalize a fund-flow payload into an agent-facing snapshot packet."""
    snapshot = _normalize_fund_flow_snapshot(
        payload,
        source=source,
        observed_at=observed_at,
    )
    return {
        "success": True,
        "schema_version": "fund_flow.snapshot.v1",
        "snapshot": snapshot.to_dict(),
    }


def build_fund_flow_anomaly_packet(
    payload: Mapping[str, Any] | Any,
    *,
    thresholds: Optional[Mapping[str, Any] | FundFlowThresholds] = None,
    source: Optional[str] = None,
    observed_at: Optional[str | datetime] = None,
) -> dict[str, Any]:
    """Detect market-board anomalies and return canonical event packets."""
    packet = _build_fund_flow_anomaly_packet(
        payload,
        thresholds=_parse_fund_flow_thresholds(thresholds),
        source=source,
        observed_at=observed_at,
    )
    return {
        "success": True,
        "schema_version": "fund_flow.anomaly_packet.v1",
        "payload_type": "fund_flow_anomaly",
        **dict(packet),
    }


def detect_market_anomalies(
    payload: Mapping[str, Any] | Any,
    *,
    thresholds: Optional[Mapping[str, Any] | FundFlowThresholds] = None,
    source: Optional[str] = None,
    observed_at: Optional[str | datetime] = None,
) -> dict[str, Any]:
    """Alias for fund-flow anomaly detection through the capability kernel."""
    events = _detect_market_anomalies(
        payload,
        thresholds=_parse_fund_flow_thresholds(thresholds),
        source=source,
        observed_at=observed_at,
    )
    return {
        "success": True,
        "schema_version": "fund_flow.anomaly_packet.v1",
        "payload_type": "fund_flow_anomaly",
        "event_count": len(events),
        "market_events": _serialize_events(events),
    }


def record_market_events(
    events: Sequence[Mapping[str, Any] | MarketEvent],
    *,
    event_store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Persist canonical market events with ID de-duplication."""
    resolved_path = _resolve_market_event_store_path(event_store_path)
    result = EventStore(resolved_path).add_many(events)
    return {
        "success": True,
        "event_store_path": str(resolved_path),
        **result,
    }


def list_market_events(
    *,
    subject_code: Optional[str] = None,
    subject_name: Optional[str] = None,
    subject_type: Optional[str] = None,
    event_type: Optional[str] = None,
    tag: Optional[str] = None,
    severity: Optional[str | int] = None,
    direction: Optional[str] = None,
    start_at: Optional[str | datetime] = None,
    end_at: Optional[str | datetime] = None,
    limit: Optional[int] = 100,
    reverse: bool = False,
    event_store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """List stored market events for board replay and agent context."""
    resolved_path = _resolve_market_event_store_path(event_store_path)
    events = EventStore(resolved_path).list_events(
        subject_code=subject_code,
        subject_name=subject_name,
        subject_type=subject_type,
        event_type=event_type,
        tag=tag,
        severity=severity,
        direction=direction,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
        reverse=reverse,
    )
    return {
        "success": True,
        "event_store_path": str(resolved_path),
        "total": len(events),
        "events": events,
    }


def aggregate_market_events(
    *,
    subject_code: Optional[str] = None,
    subject_name: Optional[str] = None,
    subject_type: Optional[str] = None,
    event_type: Optional[str] = None,
    tag: Optional[str] = None,
    severity: Optional[str | int] = None,
    direction: Optional[str] = None,
    start_at: Optional[str | datetime] = None,
    end_at: Optional[str | datetime] = None,
    limit: Optional[int] = None,
    event_store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Aggregate stored market events for market-board summaries."""
    resolved_path = _resolve_market_event_store_path(event_store_path)
    aggregate = EventStore(resolved_path).aggregate(
        subject_code=subject_code,
        subject_name=subject_name,
        subject_type=subject_type,
        event_type=event_type,
        tag=tag,
        severity=severity,
        direction=direction,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )
    return {
        "success": True,
        "event_store_path": str(resolved_path),
        "aggregate": aggregate,
    }


def replay_market_subject_events(
    *,
    subject_code: Optional[str] = None,
    subject_name: Optional[str] = None,
    subject_type: Optional[str] = None,
    start_at: Optional[str | datetime] = None,
    end_at: Optional[str | datetime] = None,
    limit: Optional[int] = None,
    event_store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Replay chronological events for one stock, sector, theme, or market subject."""
    resolved_path = _resolve_market_event_store_path(event_store_path)
    events = EventStore(resolved_path).replay_subject(
        subject_code=subject_code,
        subject_name=subject_name,
        subject_type=subject_type,
        start_at=start_at,
        end_at=end_at,
        limit=limit,
    )
    return {
        "success": True,
        "event_store_path": str(resolved_path),
        "total": len(events),
        "events": events,
    }


def create_evidence_packet(
    *,
    title: str,
    targets: Optional[str | Sequence[str]] = None,
    source_refs: Optional[Mapping[str, object] | Sequence[Mapping[str, object]]] = None,
    data_quality: Optional[Mapping[str, object]] = None,
    provenance: Optional[Mapping[str, object] | Sequence[Mapping[str, object]]] = None,
    market_events: Optional[
        Mapping[str, object] | Sequence[Mapping[str, object]]
    ] = None,
    notes: Optional[str | Sequence[str]] = None,
    tags: Optional[str | Sequence[str]] = None,
    items: Optional[Sequence[Mapping[str, object] | EvidenceItem]] = None,
    metadata: Optional[Mapping[str, object]] = None,
    collected_at: Optional[str | datetime] = None,
) -> dict[str, Any]:
    """Build a JSON-ready evidence packet for research review workflows."""
    packet = EvidencePacket(
        title=title,
        targets=targets or (),
        collected_at=collected_at,
        source_refs=source_refs or (),
        data_quality=data_quality,
        provenance=provenance or (),
        market_events=market_events or (),
        notes=notes or (),
        tags=tags or (),
        items=items or (),
        metadata=metadata,
    )
    return {
        "success": True,
        "packet": packet.to_dict(),
        "all_source_refs": list(packet.all_source_refs),
        "all_market_events": list(packet.all_market_events),
    }


def create_evidence_item(
    *,
    title: str,
    source_refs: Optional[Mapping[str, object] | Sequence[Mapping[str, object]]] = None,
    data_quality: Optional[Mapping[str, object]] = None,
    provenance: Optional[Mapping[str, object] | Sequence[Mapping[str, object]]] = None,
    market_events: Optional[
        Mapping[str, object] | Sequence[Mapping[str, object]]
    ] = None,
    notes: Optional[str | Sequence[str]] = None,
    tags: Optional[str | Sequence[str]] = None,
    stance: str | EvidenceStance | None = EvidenceStance.NEUTRAL,
    item_type: str = "generic",
    payload: Optional[Mapping[str, object]] = None,
    collected_at: Optional[str | datetime] = None,
) -> dict[str, Any]:
    """Build one JSON-ready evidence item for a research packet."""
    item = EvidenceItem(
        title=title,
        source_refs=source_refs or (),
        collected_at=collected_at,
        data_quality=data_quality,
        provenance=provenance or (),
        market_events=market_events or (),
        notes=notes or (),
        tags=tags or (),
        stance=stance,
        item_type=item_type,
        payload=payload,
    )
    return {
        "success": True,
        "item": item.to_dict(),
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


def _serialize_research_index(index: ResearchLedgerIndex) -> dict[str, Any]:
    return cast(dict[str, Any], index.to_dict())


def get_research_ledger_index(
    *,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return a lightweight research-ledger index for planning and review."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    index = ResearchLedger(resolved_path).build_index()
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "index": _serialize_research_index(index),
    }


def query_research_entries(
    *,
    statuses: Optional[Sequence[str | ResearchStatus] | str | ResearchStatus] = None,
    targets: Optional[Sequence[str] | str] = None,
    tags: Optional[Sequence[str] | str] = None,
    text: Optional[str] = None,
    limit: int = 50,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Query research ledger entries by lifecycle, target, tags, or text."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    entries = ResearchLedger(resolved_path).query_entries(
        statuses=_parse_research_statuses(statuses),
        targets=_as_string_list(targets),
        tags=_as_string_list(tags),
        text=text,
        limit=limit,
    )
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "total": len(entries),
        "entries": [entry.to_dict() for entry in entries],
    }


def find_research_duplicate_candidates(
    *,
    targets: Sequence[str] | str,
    title: Optional[str] = None,
    tags: Optional[Sequence[str] | str] = None,
    limit: int = 10,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Find overlapping research entries before creating a new thesis."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    candidates = ResearchLedger(resolved_path).find_duplicate_candidates(
        targets=_as_string_list(targets),
        title=title,
        tags=_as_string_list(tags),
        limit=limit,
    )
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "total": len(candidates),
        "candidates": candidates,
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


def record_research_postmortem(
    entry_id: str,
    *,
    outcome: str,
    root_cause: str | PostmortemRootCause = PostmortemRootCause.UNKNOWN,
    expected: str = "",
    actual: str = "",
    error_analysis: str = "",
    lessons: Optional[Sequence[str]] = None,
    evidence: Optional[Mapping[str, Any]] = None,
    status_after: Optional[str | ResearchStatus] = None,
    reviewed_at: Optional[str | datetime] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Record a structured counterfactual/postmortem review on a thesis."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    postmortem = ResearchPostmortem(
        entry_id=entry_id,
        outcome=outcome,
        root_cause=root_cause,
        expected=expected,
        actual=actual,
        error_analysis=error_analysis,
        lessons=tuple(lessons or ()),
        evidence=dict(evidence or {}),
        reviewed_at=_parse_datetime(reviewed_at, datetime.now()),
    )
    observation = ResearchObservation(
        observation_type="postmortem",
        note=f"Postmortem recorded: {postmortem.outcome}",
        observed_at=postmortem.reviewed_at,
        evidence={"postmortem": postmortem.to_dict()},
        status_after=(
            _parse_research_status(status_after) if status_after is not None else None
        ),
    )
    entry = ResearchLedger(resolved_path).record_observation(entry_id, observation)
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "postmortem": postmortem.to_dict(),
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


def review_research_entry(
    entry_id: str,
    *,
    evidence_packets: Optional[Sequence[Mapping[str, object] | EvidencePacket]] = None,
    evidence_items: Optional[Sequence[Mapping[str, object] | EvidenceItem]] = None,
    observations: Optional[Sequence[Mapping[str, object] | ResearchObservation]] = None,
    reviewed_at: Optional[str | datetime] = None,
    apply_suggested_status: bool = False,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Review one research thesis against structured evidence."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_path)
    entry = ledger.get(entry_id)
    if entry is None:
        return {
            "success": False,
            "ledger_path": str(resolved_path),
            "error": f"Research entry not found: {entry_id}",
            "review": None,
        }

    review = review_thesis(
        entry,
        evidence_packets=evidence_packets or (),
        evidence_items=evidence_items or (),
        observations=observations,
        reviewed_at=reviewed_at,
    )
    updated_entry: dict[str, Any] | None = None
    if apply_suggested_status and review.suggested_status is not None:
        updated_entry = ledger.update_status(
            entry_id, review.suggested_status
        ).to_dict()

    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "review": review.to_dict(),
        "entry": updated_entry or entry.to_dict(),
        "status_updated": updated_entry is not None,
    }


def evaluate_data_source_health(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Evaluate source latency, degradation, warning, and failure patterns."""
    return {
        "success": True,
        "health": _evaluate_source_health(records),
    }


def check_system_prompt_drift(
    *,
    file_pairs: Optional[Sequence[Mapping[str, Any]]] = None,
    root_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Compare duplicated prompt files for drift."""
    pairs = (
        list(file_pairs)
        if file_pairs is not None
        else _default_prompt_drift_pairs(root_path)
    )
    return {
        "success": True,
        "drift": _check_prompt_drift(pairs, root_path=root_path),
    }


def evaluate_research_report_quality(
    report_text: str,
    *,
    checks: Optional[Mapping[str, Sequence[str]]] = None,
) -> dict[str, Any]:
    """Evaluate whether a report includes core research-quality elements."""
    return {
        "success": True,
        "quality": _evaluate_report_quality(report_text, checks=checks),
    }


def evaluate_research_case_quality(case_dir: str | Path) -> dict[str, Any]:
    """Evaluate artifact-level research-case quality gates."""
    return {
        "success": True,
        "quality": _evaluate_research_case_quality(case_dir),
    }


def evaluate_skill_boundary_cases(
    cases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Run deterministic skill-boundary eval cases."""
    return {
        "success": True,
        "evaluation": _evaluate_skill_response_cases(cases),
    }


async def initialize_database(
    *,
    skip_refresh: bool = False,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Initialize local storage for agent capabilities."""
    resolved_db_path = _resolve_db_path(db_path)
    resolved_db_path.parent.mkdir(parents=True, exist_ok=True)

    from .migrations import MigrationRunner
    runner = MigrationRunner(resolved_db_path)
    migration_result = await runner.run_pending()

    db = Database(str(resolved_db_path))
    await db.connect()
    try:
        loaded_count = 0
        if not skip_refresh:
            loaded_count = await QuoteService(db).refresh_stocks()
        return {
            "success": True,
            "loaded_count": loaded_count,
            "db_path": str(resolved_db_path),
            "migrations_applied": migration_result.get("applied", []),
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
    walk_forward_train_bars: Optional[int] = None,
    walk_forward_test_bars: Optional[int] = None,
    candidate_parameter_sets: Optional[Sequence[Mapping[str, Any]]] = None,
    selection_metric: str = "total_return",
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run a bounded technical-signal replay from locally persisted bars.

    This legacy single-name entry point deliberately never refreshes market
    data.  Network fetches during a backtest make the result timing-dependent
    and irreproducible.  A local cache still lacks a source-frozen manifest, so
    its output is labelled as research-only until a frozen replay input is
    supplied to the portfolio engine.
    """
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
        import pandas as pd

        quotes = await db.get_daily_quotes(code, limit=10_000)
        if not quotes:
            return {
                "error": "No locally persisted daily bars; freeze a source-labelled replay packet before running a backtest.",
                "data_assurance": {
                    "status": "blocked",
                    "source": "local_cache",
                    "failures": ["No local bars are available and network refresh is forbidden during backtest."],
                },
            }
        df = pd.DataFrame(
            [
                {
                    "date": quote.date,
                    "open": quote.open,
                    "high": quote.high,
                    "low": quote.low,
                    "close": quote.close,
                    "volume": quote.volume,
                    "amount": quote.amount,
                }
                for quote in quotes
            ]
        ).sort_values("date", kind="stable").reset_index(drop=True)

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

        if (walk_forward_train_bars is None) != (walk_forward_test_bars is None):
            return {"error": "walk-forward train and test bars must be supplied together"}
        if candidate_parameter_sets is not None and walk_forward_train_bars is None:
            return {
                "error": "candidate_parameter_sets requires walk-forward train and test bars"
            }
        if walk_forward_train_bars is not None and walk_forward_test_bars is not None:
            if candidate_parameter_sets is not None:
                result = run_rolling_model_selection(
                    df,
                    strategy_name=strategy,
                    candidate_parameter_sets=candidate_parameter_sets,
                    train_bars=walk_forward_train_bars,
                    test_bars=walk_forward_test_bars,
                    selection_metric=selection_metric,
                    initial_capital=capital,
                    transfer_fee_rate=0.00001 if code.startswith(("6", "9")) else 0.0,
                )
                return _label_local_signal_backtest(result.to_dict())
            result = BacktestEngine().run_walk_forward(
                df,
                strategy_name=strategy,
                train_bars=walk_forward_train_bars,
                test_bars=walk_forward_test_bars,
                initial_capital=capital,
                transfer_fee_rate=0.00001 if code.startswith(("6", "9")) else 0.0,
            )
            return _label_local_signal_backtest(result.to_dict())
        result = BacktestEngine().run(
            df,
            strategy_name=strategy,
            initial_capital=capital,
            transfer_fee_rate=0.00001 if code.startswith(("6", "9")) else 0.0,
        )
        result.code = code
        return _label_local_signal_backtest(result.to_dict())
    finally:
        await db.close()


def _label_local_signal_backtest(result: Mapping[str, Any]) -> dict[str, Any]:
    """Prevent cached single-name backtests from implying frozen-data replay."""
    labelled = dict(result)
    warnings = list(labelled.get("warnings") or [])
    warnings.append(
        "This signal replay used locally persisted bars only; it has no frozen source manifest and is not eligible for a reproducibility or execution-edge claim."
    )
    labelled["warnings"] = warnings
    labelled["data_assurance"] = {
        "status": "blocked",
        "source": "local_cache",
        "failures": [
            "Local bars are not bound to a source-frozen archive, historical universe, corporate-action, halt, price-limit, or delisting manifest."
        ],
    }
    labelled["research_only"] = True
    labelled["no_order_execution"] = True
    return labelled


async def freeze_local_signal_replay_input(
    code: str,
    *,
    archive_directory: str | Path | None = None,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Freeze locally persisted daily bars before a deterministic signal replay.

    The local cache provenance remains explicitly limited.  This function makes
    its exact bytes reproducible; it does not infer a commercial source or
    fill missing corporate-action and execution-event coverage.
    """
    import pandas as pd

    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        quotes = await db.get_daily_quotes(code, limit=10_000)
        if not quotes:
            raise ValueError("No locally persisted daily bars are available to freeze")
        frame = pd.DataFrame(
            [
                {
                    "date": quote.date,
                    "open": quote.open,
                    "high": quote.high,
                    "low": quote.low,
                    "close": quote.close,
                    "volume": quote.volume,
                    "amount": quote.amount,
                }
                for quote in quotes
            ]
        )
    finally:
        await db.close()
    packet = build_frozen_signal_replay_input(code, frame, source="local_cache")
    result = packet.to_dict()
    if archive_directory is not None:
        target_directory = Path(archive_directory)
        result["source_archive_path"] = str(packet.write_frozen_archive(target_directory))
        result["replay_input_path"] = str(packet.write_replay_input(target_directory))
    return result


def run_frozen_signal_backtest(
    replay_input: Mapping[str, Any],
    *,
    strategy: str,
    capital: float = 100_000.0,
    source_archive_path: str | Path | None = None,
    walk_forward_train_bars: int | None = None,
    walk_forward_test_bars: int | None = None,
    candidate_parameter_sets: Sequence[Mapping[str, Any]] | None = None,
    selection_metric: str = "total_return",
) -> dict[str, Any]:
    """Replay a content-addressed signal input without any market-data fetch."""
    if strategy not in STRATEGIES:
        return {
            "error": f"Unknown strategy name '{strategy}'",
            "available_strategies": list(STRATEGIES.keys()),
        }
    packet = parse_frozen_signal_replay_input(replay_input)
    archive_assurance = verify_frozen_market_data_archive(
        source_archive_path,
        expected_archive_id=packet.archive_id,
        expected_source=packet.source,
    )
    if (walk_forward_train_bars is None) != (walk_forward_test_bars is None):
        raise ValueError("walk-forward train and test bars must be supplied together")
    if candidate_parameter_sets is not None and walk_forward_train_bars is None:
        raise ValueError("candidate_parameter_sets requires walk-forward train and test bars")
    if walk_forward_train_bars is not None and walk_forward_test_bars is not None:
        if candidate_parameter_sets is not None:
            result = run_rolling_model_selection(
                packet.market_data,
                strategy_name=strategy,
                candidate_parameter_sets=candidate_parameter_sets,
                train_bars=walk_forward_train_bars,
                test_bars=walk_forward_test_bars,
                selection_metric=selection_metric,
                initial_capital=capital,
                transfer_fee_rate=0.00001 if packet.code.startswith(("6", "9")) else 0.0,
            ).to_dict()
        else:
            result = BacktestEngine().run_walk_forward(
                packet.market_data,
                strategy_name=strategy,
                train_bars=walk_forward_train_bars,
                test_bars=walk_forward_test_bars,
                initial_capital=capital,
                transfer_fee_rate=0.00001 if packet.code.startswith(("6", "9")) else 0.0,
            ).to_dict()
    else:
        result = BacktestEngine().run(
            packet.market_data,
            strategy_name=strategy,
            initial_capital=capital,
            transfer_fee_rate=0.00001 if packet.code.startswith(("6", "9")) else 0.0,
        ).to_dict()
    result["code"] = packet.code
    result["data_assurance"] = {
        "status": "pass" if archive_assurance["status"] == "pass" else "blocked",
        "scope": "exact_input_replay",
        "source": packet.source,
        "archive_assurance": archive_assurance,
    }
    result["methodology_assurance"] = {
        "status": "blocked",
        "failures": [
            "Frozen daily bars alone do not cover historical universe, halts, price limits, corporate actions, delistings, or capacity."
        ],
    }
    result["research_only"] = True
    result["no_order_execution"] = True
    warnings = list(result.get("warnings") or [])
    warnings.append(
        "This result is deterministic for its archived input only; it is not a full execution-grade or institutional portfolio-backtest claim."
    )
    result["warnings"] = warnings
    return cast(dict[str, Any], result)


def run_frozen_portfolio_backtest(
    replay_input: Mapping[str, Any],
    *,
    source_archive_path: str | Path | None = None,
    initial_capital: float = 100_000.0,
    slippage_bps: float = 0.0,
    max_participation_rate: float | None = None,
) -> dict[str, Any]:
    """Replay one frozen public daily-bar portfolio input without refetching.

    A passing ``data_assurance`` means the archive bytes match this exact
    input. It is intentionally independent from, and weaker than, the
    portfolio engine's source/reproducibility assurance.
    """
    packet = parse_frozen_portfolio_replay_input(replay_input)
    archive_assurance = verify_frozen_market_archive(
        source_archive_path,
        expected_archive_id=packet.archive_id,
        expected_source=packet.source,
    )
    result = run_portfolio_backtest(
        packet.market_data,
        packet.target_weights,
        universe_references=packet.universe_references,
        trading_calendar=packet.trading_calendar,
        coverage_manifest={
            "corporate_actions": "unverified",
            "delistings": "unverified",
            "price_limits": "unverified",
            "halts": "unverified",
        },
        source_manifest=packet.to_dict()["portfolio_source_manifest"],
        price_basis="forward_adjusted_or_unknown",
        slippage_bps=slippage_bps,
        max_participation_rate=max_participation_rate,
        initial_capital=initial_capital,
    )
    result["data_assurance"] = {
        "status": "pass" if archive_assurance["status"] == "pass" else "blocked",
        "scope": "exact_input_replay",
        "source": packet.source,
        "archive_assurance": archive_assurance,
    }
    result["methodology_assurance"] = {
        "status": "blocked",
        "failures": [
            "Public daily bars and supplied weights do not establish point-in-time universe, halts, price limits, corporate actions, delistings, or capacity.",
            "Daily-bar execution is a paper assumption and cannot establish fill quality or tradability through limit locks.",
        ],
    }
    result["formal_decision_eligible"] = False
    result["research_only"] = True
    result["no_order_execution"] = True
    warnings = list(result.get("warnings") or [])
    warnings.append(
        "This public-data result is deterministic only for the archived input; it is not a formal portfolio-backtest, investment-committee, or trading claim."
    )
    result["warnings"] = list(dict.fromkeys(warnings))
    return result


async def build_akshare_daily_portfolio_replay_input(
    codes: Sequence[str],
    target_weights: Mapping[str, Mapping[str, float]],
    *,
    start_date: str,
    end_date: str,
    archive_directory: str | Path | None = None,
    observed_at: str | datetime | None = None,
) -> dict[str, Any]:
    """Fetch and freeze AkShare EOD bars for a bounded paper-only replay.

    Each observed daily bar is explicitly treated as an assumed tradable open
    for the simulator. This is not an assertion that the stock was fillable at
    that open; halt and limit-lock coverage remains unverified and blocks any
    formal portfolio-backtest or investment-decision claim.
    """
    import pandas as pd

    normalized_codes = [str(code).strip() for code in codes if str(code).strip()]
    if not normalized_codes or len(set(normalized_codes)) != len(normalized_codes):
        raise ValueError("codes must contain unique nonempty stock codes")
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    except ValueError as error:
        raise ValueError("start_date and end_date must use YYYY-MM-DD") from error
    if start > end:
        raise ValueError("start_date must not be later than end_date")
    client = AkShareClient()
    frames, calendar = await asyncio.gather(
        asyncio.gather(
            *(client.get_daily_quotes(code, start, end) for code in normalized_codes)
        ),
        asyncio.to_thread(_fetch_akshare_exchange_trading_calendar, start, end),
    )
    market_data: dict[str, Any] = {}
    for code, frame in zip(normalized_codes, frames, strict=True):
        if not hasattr(frame, "columns") or frame.empty:
            raise ValueError(f"AkShare returned no daily bars for {code}")
        normalized = frame.copy()
        normalized["tradable"] = True
        normalized["execution_status"] = "tradable"
        market_data[code] = normalized
    references = {
        str(pd.Timestamp(day).normalize().date()): "akshare_public:unverified-universe:"
        + str(pd.Timestamp(day).normalize().date())
        for day in target_weights
    }
    packet = build_frozen_portfolio_replay_input(
        market_data,
        target_weights,
        trading_calendar=calendar,
        universe_references=references,
        trading_calendar_source="akshare.tool_trade_date_hist_sina",
        observed_at=observed_at,
    )
    result = packet.to_dict()
    result["execution_assumption"] = "daily_bar_presence_assumed_tradable"
    result["research_only"] = True
    result["formal_decision_eligible"] = False
    result["no_order_execution"] = True
    if archive_directory is not None:
        directory = Path(archive_directory)
        result["source_archive_path"] = str(packet.write_frozen_archive(directory))
        result["replay_input_path"] = str(packet.write_replay_input(directory))
    return result


def _fetch_akshare_exchange_trading_calendar(start: date, end: date) -> list[str]:
    """Load the public exchange calendar used by a bounded paper replay.

    Do not infer sessions from a union of securities' daily-bar dates: that
    would make T+1 settlement and next-session execution silently depend on
    suspensions, listings, or missing observations.  This remains public,
    research-only data and does not claim formal historical event coverage.
    """
    import akshare as ak
    import pandas as pd

    frame = ak.tool_trade_date_hist_sina()
    column = next(
        (name for name in ("trade_date", "日期", "date") if name in frame.columns),
        None,
    )
    if column is None:
        raise ValueError("AkShare exchange calendar has no supported date column")
    days = sorted(
        {
            parsed.date()
            for value in frame[column]
            if not pd.isna(parsed := pd.to_datetime(value, errors="coerce"))
            and start <= parsed.date() <= end
        }
    )
    if len(days) < 2:
        raise ValueError(
            "AkShare exchange calendar has fewer than two sessions in the requested replay range"
        )
    return [day.isoformat() for day in days]


async def build_akshare_public_portfolio_review_evidence(
    replay_input: Mapping[str, Any],
    *,
    source_archive_path: str | Path,
    benchmark_id: str,
    evaluation_start: str,
    evaluation_end: str,
    archive_directory: str | Path,
    initial_capital: float = 100_000.0,
    slippage_bps: float = 0.0,
    max_participation_rate: float | None = None,
) -> dict[str, Any]:
    """Create a public-frozen, benchmarked review packet for one replay.

    The portfolio return is recomputed from the supplied content-addressed
    input. The benchmark is a separately fetched public index close series;
    both derived returns are frozen together in a second archive for a bounded
    research review. This cannot establish formal performance evidence.
    """
    import asyncio

    packet = parse_frozen_portfolio_replay_input(replay_input)
    replay = run_frozen_portfolio_backtest(
        replay_input,
        source_archive_path=source_archive_path,
        initial_capital=initial_capital,
        slippage_bps=slippage_bps,
        max_participation_rate=max_participation_rate,
    )
    if replay["data_assurance"]["status"] != "pass":
        raise ValueError("public portfolio review requires a verified frozen replay archive")
    start = _parse_public_review_timestamp(evaluation_start, "evaluation_start")
    end = _parse_public_review_timestamp(evaluation_end, "evaluation_end")
    if end <= start:
        raise ValueError("evaluation_end must be later than evaluation_start")
    normalized_benchmark = _normalize_akshare_benchmark_id(benchmark_id)
    benchmark_frame = await asyncio.to_thread(
        _fetch_akshare_benchmark_daily,
        normalized_benchmark,
        start.date().isoformat(),
        end.date().isoformat(),
    )
    benchmark_return, benchmark_records = _public_benchmark_return(
        benchmark_frame, start.date().isoformat(), end.date().isoformat()
    )
    benchmark_source = str(
        benchmark_frame.attrs.get("market_data_source", "akshare.stock_zh_index_daily_em")
    )
    benchmark_fallback_path = list(
        benchmark_frame.attrs.get("market_data_fallback_path", [benchmark_source])
    )
    implementation_cost_return = sum(
        float(trade.get("costs") or 0.0) for trade in replay.get("trades") or []
    ) / float(replay["initial_capital"])
    observation = {
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "portfolio_replay": {
            "input_archive_id": packet.archive_id,
            "total_return": replay["total_return"],
            "implementation_cost_return": implementation_cost_return,
            "data_assurance": replay["data_assurance"],
        },
        "benchmark": {
            "benchmark_id": str(benchmark_id).strip(),
            "akshare_symbol": normalized_benchmark,
            "source": benchmark_source,
            "fallback_path": benchmark_fallback_path,
            "evaluation_start": start.isoformat(),
            "evaluation_end": end.isoformat(),
            "return": benchmark_return,
            "daily_closes": benchmark_records,
        },
    }
    frozen = build_public_market_observation_packet(
        subject="frozen_public_portfolio_review",
        observation=observation,
        observed_at=observation["observed_at"],
    )
    archive_path = frozen.write_frozen_archive(Path(archive_directory))
    archive_id = frozen.archive_id
    return {
        "schema_version": "public_frozen_portfolio_review_evidence.v1",
        "evidence_status": "public_frozen",
        "source_archive_path": str(archive_path),
        "review_inputs": {
            "gross_paper_return": replay["total_return"],
            "implementation_cost_return": implementation_cost_return,
            "benchmark_return": benchmark_return,
        },
        "return_evidence": {
            "source": "akshare_public",
            "archive_id": archive_id,
            "source_archive_path": str(archive_path),
            "paper_return_ref": f"frozen-portfolio:{packet.archive_id}:{archive_id}",
            "benchmark_return_ref": f"akshare-index:{benchmark_id}:{archive_id}",
            "evaluation_start": start.isoformat(),
            "evaluation_end": end.isoformat(),
            "benchmark_id": str(benchmark_id).strip(),
            "portfolio_input_archive_id": packet.archive_id,
        },
        "limitations": [
            "This is a public-frozen research review, not formal decision or portfolio-backtest evidence.",
            "The benchmark and portfolio inputs do not establish point-in-time universe, halts, price limits, corporate actions, delistings, or fill quality.",
        ],
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }


def _normalize_akshare_benchmark_id(benchmark_id: str) -> str:
    normalized = str(benchmark_id).strip().lower().replace(".", "")
    if normalized in {"000300sh", "000300"}:
        return "sh000300"
    if normalized in {"000905sh", "000905"}:
        return "sh000905"
    if normalized in {"000852sh", "000852"}:
        return "sh000852"
    if normalized.startswith(("sh", "sz", "csi", "bj")) and normalized[2:].isdigit():
        return normalized
    raise ValueError("benchmark_id must identify a supported A-share index, such as 000300.SH")


def _fetch_akshare_benchmark_daily(
    benchmark_symbol: str, start_date: str, end_date: str
) -> Any:
    """Fetch public index bars with a bounded AkShare source fallback."""
    import akshare as ak

    failures: list[str] = []
    for attempt in range(2):
        try:
            frame = ak.stock_zh_index_daily_em(
                symbol=benchmark_symbol,
                start_date=start_date.replace("-", ""),
                end_date=end_date.replace("-", ""),
            )
        except Exception as error:
            failures.append(
                f"akshare.stock_zh_index_daily_em attempt {attempt + 1}: {type(error).__name__}: {error}"
            )
        else:
            frame.attrs["market_data_source"] = "akshare.stock_zh_index_daily_em"
            frame.attrs["market_data_fallback_path"] = [
                "akshare.stock_zh_index_daily_em"
            ]
            return frame
    try:
        frame = ak.stock_zh_index_daily(symbol=benchmark_symbol)
    except Exception as error:
        failures.append(
            f"akshare.stock_zh_index_daily: {type(error).__name__}: {error}"
        )
        raise ValueError(
            "AkShare benchmark sources are unavailable: " + "; ".join(failures)
        ) from error
    frame.attrs["market_data_source"] = "akshare.stock_zh_index_daily"
    frame.attrs["market_data_fallback_path"] = [
        "akshare.stock_zh_index_daily_em",
        "akshare.stock_zh_index_daily",
    ]
    return frame


def _parse_public_review_timestamp(value: str, field_name: str) -> datetime:
    try:
        timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(f"{field_name} must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError(f"{field_name} must include a timezone")
    return timestamp


def _public_benchmark_return(
    frame: Any, start_date: str, end_date: str
) -> tuple[float, list[dict[str, Any]]]:
    import pandas as pd

    if not hasattr(frame, "columns") or not {"date", "close"}.issubset(frame.columns):
        raise ValueError("AkShare benchmark response requires date and close columns")
    normalized = frame[["date", "close"]].copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.normalize()
    normalized["close"] = pd.to_numeric(normalized["close"], errors="coerce")
    normalized = normalized.dropna().sort_values("date")
    normalized = normalized[
        (normalized["date"] >= pd.Timestamp(start_date))
        & (normalized["date"] <= pd.Timestamp(end_date))
    ]
    if len(normalized) < 2 or (normalized["close"] <= 0).any():
        raise ValueError("AkShare benchmark response lacks at least two valid closes for the review interval")
    result = float(normalized.iloc[-1]["close"] / normalized.iloc[0]["close"] - 1)
    records = json.loads(normalized.to_json(orient="records", date_format="iso"))
    return result, records


def run_portfolio_backtest(
    market_data: Mapping[str, Any],
    target_weights: Mapping[str, Mapping[str, float]],
    *,
    universe_references: Mapping[str, str],
    trading_calendar: Sequence[str],
    universe_snapshots: Optional[Mapping[str, Mapping[str, Any]]] = None,
    coverage_manifest: Optional[Mapping[str, str]] = None,
    source_manifest: Optional[Mapping[str, Any]] = None,
    source_archive_path: Optional[str] = None,
    corporate_actions: Optional[Mapping[str, Sequence[Mapping[str, Any]]]] = None,
    delisting_status: Optional[Mapping[str, Mapping[str, Any]]] = None,
    price_basis: str = "unknown",
    slippage_bps: float = 0.0,
    max_participation_rate: Optional[float] = None,
    initial_capital: float = 100_000.0,
) -> dict[str, Any]:
    """Run a point-in-time, multi-asset paper-portfolio backtest.

    Each frame must provide ``date``, ``open``, ``close``, and a
    suspension-aware ``tradable`` flag. This deterministic research simulator
    never places orders. ``trading_calendar`` is the source-labelled exchange
    session sequence used for next-open and T+1 timing.
    """
    import pandas as pd

    normalized_frames: dict[str, Any] = {}
    for code, frame in market_data.items():
        if hasattr(frame, "columns"):
            normalized_frames[str(code)] = frame
        elif isinstance(frame, Sequence) and not isinstance(frame, (str, bytes, bytearray)):
            normalized_frames[str(code)] = pd.DataFrame(list(frame))
        else:
            raise ValueError("portfolio backtest market_data values must be DataFrame-like or record sequences")
    return PortfolioBacktestEngine().run(
        normalized_frames,
        target_weights,
        universe_references=universe_references,
        universe_snapshots=universe_snapshots,
        trading_calendar=trading_calendar,
        coverage_manifest=coverage_manifest,
        source_manifest=source_manifest,
        source_archive_path=source_archive_path,
        corporate_actions=corporate_actions,
        delisting_status=delisting_status,
        price_basis=price_basis,
        slippage_bps=slippage_bps,
        max_participation_rate=max_participation_rate,
        initial_capital=initial_capital,
    ).to_dict()


def build_tushare_daily_replay_input(
    codes: Sequence[str],
    *,
    start_date: str,
    end_date: str,
    user_id: str = "default",
    token: Optional[str] = None,
    data_owner: Optional[str] = None,
    archive_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Fetch a frozen, JSON-ready Tushare daily replay input package.

    The caller must have authorized Tushare access. This helper never falls
    back to public aggregation because that would invalidate replay provenance.
    """
    require_licensed_market_data_mode(user_id=user_id)
    packet = TushareProBacktestAdapter(token=token, data_owner=data_owner).build_daily_replay_packet(
        codes, start_date=start_date, end_date=end_date
    )
    result = packet.to_dict()
    if archive_directory is not None:
        result["source_archive_path"] = str(packet.write_frozen_archive(Path(archive_directory)))
    return result


def build_tushare_listing_universe_snapshot(
    *,
    as_of_date: str,
    user_id: str = "default",
    token: Optional[str] = None,
    data_owner: Optional[str] = None,
    archive_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Build a frozen source-labelled listing-universe snapshot for a target day."""
    require_licensed_market_data_mode(user_id=user_id)
    packet = TushareProBacktestAdapter(token=token, data_owner=data_owner).build_listing_universe_snapshot(
        as_of_date=as_of_date
    )
    result = packet.to_dict()
    if archive_directory is not None:
        result["source_archive_path"] = str(packet.write_frozen_archive(Path(archive_directory)))
    return result


def build_jqdata_minute_observation_input(
    codes: Sequence[str],
    *,
    start_time: str,
    end_time: str,
    user_id: str = "default",
    username: Optional[str] = None,
    password: Optional[str] = None,
    data_owner: Optional[str] = None,
    archive_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Fetch source-frozen JQData minute observations for short-horizon research.

    The output must not be passed to the daily portfolio engine or presented
    as an execution backtest: it contains bar observations, not order-book or
    queue/fill evidence.
    """
    require_licensed_market_data_mode(user_id=user_id)
    packet = JQDataMinuteAdapter(
        username=username, password=password, data_owner=data_owner
    ).build_minute_observation_packet(
        codes, start_time=start_time, end_time=end_time
    )
    result = packet.to_dict()
    if archive_directory is not None:
        result["source_archive_path"] = str(packet.write_frozen_archive(Path(archive_directory)))
    return result


def verify_frozen_market_data_archive(
    archive_path: str | Path,
    *,
    expected_archive_id: Optional[str] = None,
    expected_source: Optional[str] = None,
) -> dict[str, Any]:
    """Verify immutable market-data bytes before a reproducibility claim."""
    from .market_data import verify_frozen_market_archive

    return verify_frozen_market_archive(
        archive_path,
        expected_archive_id=expected_archive_id,
        expected_source=expected_source,
    )


def list_market_data_source_governance() -> dict[str, Any]:
    """List allowed source roles and configured credential availability.

    This is a governance inventory only. It neither opens a vendor connection
    nor exposes credential values.
    """
    from .data_provenance import list_market_data_source_governance as _list_sources

    return _list_sources()


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
    data["market_data_mode"] = config.market_data_mode.value
    return cast(dict[str, Any], data)


def require_licensed_market_data_mode(*, user_id: str = "default") -> None:
    """Fail closed unless the profile explicitly enables licensed market data.

    Credentials, installed client packages, and direct capability calls do not
    constitute authorization.  The user-facing policy remains the controlling
    boundary so public-observation profiles never invoke paid sources by
    accident.
    """
    policy = load_user_config(user_id)
    mode = str(policy.get("market_data_mode") or "public_observation")
    if mode != "licensed_eod":
        raise ValueError(
            "Licensed market-data capability is disabled for this profile: "
            f"market_data_mode={mode}. Explicitly set licensed_eod only after "
            "the applicable data authorization has been approved."
        )


# ---------------------------------------------------------------------------
# Prediction Ledger capabilities
# ---------------------------------------------------------------------------

DEFAULT_PREDICTION_LEDGER_PATH = PROJECT_ROOT / "data" / "prediction-ledger.json"


def _resolve_prediction_ledger_path(path: Optional[Path] = None) -> Path:
    return path or DEFAULT_PREDICTION_LEDGER_PATH


def create_prediction(
    *,
    code: str,
    direction: str,
    entry_price: float,
    target_price: Optional[float] = None,
    stop_loss: Optional[float] = None,
    horizon_days: int = 30,
    confidence: float = 0.5,
    thesis_summary: str = "",
    research_entry_id: Optional[str] = None,
    tags: Optional[list[str]] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Create a structured prediction in the prediction ledger."""
    from .research.prediction import (
        PredictionDirection,
        PredictionLedger,
        PricePrediction,
    )

    ledger = PredictionLedger(_resolve_prediction_ledger_path(ledger_path))
    prediction = PricePrediction(
        code=code,
        direction=PredictionDirection(direction),
        entry_price=entry_price,
        target_price=target_price,
        stop_loss=stop_loss,
        horizon_days=horizon_days,
        confidence=confidence,
        thesis_summary=thesis_summary,
        research_entry_id=research_entry_id,
        tags=tags or [],
    )
    ledger.create(prediction)
    return prediction.to_dict()


def list_predictions(
    *,
    code: Optional[str] = None,
    outcome: Optional[str] = None,
    limit: int = 50,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """List predictions with optional filters."""
    from .research.prediction import PredictionLedger, PredictionOutcome

    ledger = PredictionLedger(_resolve_prediction_ledger_path(ledger_path))
    outcome_enum = PredictionOutcome(outcome) if outcome else None
    items = ledger.list_all(code=code, outcome=outcome_enum, limit=limit)
    return {"predictions": items, "count": len(items)}


def get_prediction_accuracy(
    *,
    code: Optional[str] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Get prediction accuracy statistics."""
    from .research.prediction import PredictionLedger

    ledger = PredictionLedger(_resolve_prediction_ledger_path(ledger_path))
    return ledger.get_accuracy_stats(code=code)


async def run_prediction_verification(
    *,
    db_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
    research_ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run auto-verification sweep on all pending predictions."""
    from .research.prediction_verifier import run_verification_sweep

    return await run_verification_sweep(
        db_path=db_path or DEFAULT_DB_PATH,
        prediction_ledger_path=_resolve_prediction_ledger_path(ledger_path),
        research_ledger_path=research_ledger_path,
    )


# ---------------------------------------------------------------------------
# Financial Statements capabilities
# ---------------------------------------------------------------------------


async def get_financial_statements(
    code: str,
    *,
    periods: int = 8,
) -> dict[str, Any]:
    """Fetch structured financial statements with YoY/QoQ growth."""
    from .financial import FinancialStatementService

    service = FinancialStatementService()
    result = await service.get_statements(code, periods=periods)
    return result.to_dict()


# ---------------------------------------------------------------------------
# News/Announcement Pipeline capabilities
# ---------------------------------------------------------------------------


async def get_corporate_events(
    code: str,
    *,
    days: int = 90,
    include_news: bool = True,
    include_earnings: bool = True,
    include_dividends: bool = True,
) -> dict[str, Any]:
    """Fetch all corporate events (news, earnings, dividends) for a stock."""
    from .news import NewsPipeline

    pipeline = NewsPipeline()
    return await pipeline.get_all_events(
        code,
        days=days,
        include_news=include_news,
        include_earnings=include_earnings,
        include_dividends=include_dividends,
    )


async def get_stock_news(
    code: str,
    *,
    limit: int = 20,
) -> dict[str, Any]:
    """Fetch recent news for a stock."""
    from .news import NewsPipeline

    pipeline = NewsPipeline()
    events = await pipeline.get_stock_news(code, limit=limit)
    return {
        "code": code,
        "events": [e.to_dict() for e in events],
        "count": len(events),
    }


# ---------------------------------------------------------------------------
# Report Vector Store capabilities
# ---------------------------------------------------------------------------


DEFAULT_REPORT_VECTOR_STORE_PATH = PROJECT_ROOT / "data" / "report-vectors.json"


def index_report_document(
    doc_id: str,
    text: str,
    *,
    metadata: Optional[dict[str, Any]] = None,
    chunk_size: int = 500,
    store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Index a research report for semantic search."""
    from .report_search import ReportVectorStore

    store = ReportVectorStore(store_path or DEFAULT_REPORT_VECTOR_STORE_PATH)
    chunk_count = store.index_document(
        doc_id, text, metadata=metadata, chunk_size=chunk_size
    )
    return {"doc_id": doc_id, "chunks_indexed": chunk_count}


def search_reports(
    query: str,
    *,
    top_k: int = 5,
    doc_filter: Optional[str] = None,
    store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Semantic search over indexed research reports."""
    from .report_search import ReportVectorStore

    store = ReportVectorStore(store_path or DEFAULT_REPORT_VECTOR_STORE_PATH)
    results = store.search(query, top_k=top_k, doc_filter=doc_filter)
    return {
        "query": query,
        "results": [r.to_dict() for r in results],
        "count": len(results),
    }


def get_report_store_stats(
    *,
    store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Get vector store statistics."""
    from .report_search import ReportVectorStore

    store = ReportVectorStore(store_path or DEFAULT_REPORT_VECTOR_STORE_PATH)
    return store.get_stats()


# ---------------------------------------------------------------------------
# Migration capabilities
# ---------------------------------------------------------------------------


async def run_migrations(
    *,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run pending database migrations."""
    from .migrations import MigrationRunner

    runner = MigrationRunner(db_path or DEFAULT_DB_PATH)
    return await runner.run_pending()


async def get_migration_status(
    *,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Check migration status."""
    from .migrations import MigrationRunner

    runner = MigrationRunner(db_path or DEFAULT_DB_PATH)
    return await runner.get_status()


# ---------------------------------------------------------------------------
# Task Scheduler capabilities
# ---------------------------------------------------------------------------


async def start_scheduler() -> dict[str, Any]:
    """Start the task scheduler with default jobs."""
    from .scheduler import create_default_scheduler

    scheduler = create_default_scheduler()

    await scheduler.start()
    return scheduler.get_status()


def get_scheduler_status() -> dict[str, Any]:
    """Get scheduler status (for CLI)."""
    from .scheduler import create_default_scheduler

    scheduler = create_default_scheduler()
    scheduler._load_state()
    return scheduler.get_status()


# ---------------------------------------------------------------------------
# Research-Monitor Bridge capabilities
# ---------------------------------------------------------------------------


async def sync_research_monitor(
    *,
    db_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Sync research entries to watch items."""
    from .scheduler.bridge import sync_research_to_monitor
    return await sync_research_to_monitor(
        db_path=db_path or DEFAULT_DB_PATH,
        ledger_path=ledger_path,
    )


# ---------------------------------------------------------------------------
# Data Consistency capabilities
# ---------------------------------------------------------------------------


async def check_data_consistency(
    code: str,
    *,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run cross-source data consistency check for a stock."""
    from .quality.consistency import check_data_consistency as _check

    quote_data = None
    financial_data = None
    news_data = None

    try:
        quote_data = await get_quote(code, db_path=db_path or DEFAULT_DB_PATH)
    except Exception:
        pass

    try:
        financial_data = await get_financial_statements(code, periods=4)
    except Exception:
        pass

    try:
        news_data = await get_corporate_events(code, days=90)
    except Exception:
        pass

    return await _check(
        code,
        quote_data=quote_data,
        financial_data=financial_data,
        news_data=news_data,
    )


# ---------------------------------------------------------------------------
# Market Stream capabilities
# ---------------------------------------------------------------------------


async def get_market_snapshot(codes: list[str]) -> dict[str, Any]:
    """Get real-time snapshot for multiple stocks via Sina stream."""
    from .quote.market_stream import MarketStream

    stream = MarketStream()
    ticks = await stream.get_snapshot(codes)
    return {
        "ticks": [t.to_dict() for t in ticks],
        "count": len(ticks),
        "fetched_at": datetime.now().isoformat(),
    }


async def build_market_snapshot_v1(
    *,
    etf_codes: Sequence[str] = (),
    industry_codes: Sequence[str] = (),
) -> dict[str, Any]:
    """Return the source-labelled whole-market ``market_snapshot.v1`` packet.

    This is an observation packet, not a trading recommendation.  It contains
    no inferred fund-flow fields; unavailable source components are reported in
    ``warnings``/``errors`` and reflected in ``data_quality``.
    """
    return await MarketSnapshotService().build_snapshot(
        etf_codes=etf_codes,
        industry_codes=industry_codes,
    )


async def build_market_rotation_v1(
    *,
    include_concepts: bool = True,
    observation_limit: int = 20,
    history_validation_limit: int = 0,
    history_scope: str = "selected",
    history_concurrency: int = 8,
) -> dict[str, Any]:
    """Return a source-labelled industry/concept observation cross-section.

    The packet ranks only current source-provided change data. It does not
    infer multi-horizon leadership, fund flow, crowding, or stock candidates.
    """
    return await MarketRotationService().build_cross_section(
        include_concepts=include_concepts,
        observation_limit=observation_limit,
        history_validation_limit=history_validation_limit,
        history_scope=history_scope,
        history_concurrency=history_concurrency,
    )


async def freeze_public_market_rotation_observation(
    *,
    include_concepts: bool = True,
    observation_limit: int = 20,
    archive_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Freeze one public market-rotation packet for later decision audit.

    The result is replayable public observation evidence. It is deliberately
    not promoted to an execution-grade historical backtest input.
    """
    rotation = await build_market_rotation_v1(
        include_concepts=include_concepts,
        observation_limit=observation_limit,
    )
    packet = build_public_market_observation_packet(
        subject="market_rotation",
        observation=rotation,
    )
    result = packet.to_dict()
    result["market_rotation"] = rotation
    if archive_directory is not None:
        result["source_archive_path"] = str(
            packet.write_frozen_archive(Path(archive_directory))
        )
    return result


def verify_frozen_public_market_rotation_history_evidence(
    source_archive_path: str | Path,
) -> dict[str, Any]:
    """Verify a frozen public rotation archive and recompute its returns.

    This is an audit capability for public research observations.  A successful
    result proves internal replayability of the retained board-history inputs,
    not that the public source is authorized for formal paper decisions.
    """
    assurance = verify_frozen_market_archive(
        source_archive_path, expected_source="akshare_public"
    )
    if assurance.get("status") != "pass":
        return {
            "schema_version": "market-rotation-frozen-history-assurance.v1",
            "status": "blocked",
            "source_archive_assurance": assurance,
            "history_evidence": {"status": "not_checked", "failures": ["source archive is invalid"]},
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }
    try:
        payload = json.loads(Path(source_archive_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "schema_version": "market-rotation-frozen-history-assurance.v1",
            "status": "blocked",
            "source_archive_assurance": assurance,
            "history_evidence": {"status": "not_checked", "failures": [f"archive cannot be read: {error}"]},
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }
    raw_records = payload.get("raw_source_records") if isinstance(payload, Mapping) else None
    rotation = raw_records.get("market_rotation") if isinstance(raw_records, Mapping) else None
    evidence = (
        verify_rotation_history_evidence(rotation)
        if isinstance(rotation, Mapping)
        else {"status": "blocked", "failures": ["archive does not contain market_rotation"]}
    )
    return {
        "schema_version": "market-rotation-frozen-history-assurance.v1",
        "status": "pass" if evidence.get("status") in {"pass", "not_requested"} else "blocked",
        "source_archive_assurance": assurance,
        "history_evidence": evidence,
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }


def build_market_rotation_crowding_proxy_v1(
    rotation: Mapping[str, Any],
    observations: Sequence[Mapping[str, Any]],
    *,
    lookback_observations: int = 5,
) -> dict[str, Any]:
    """Build a zero-promotion-weight, flow-persistence risk proxy."""
    return build_rotation_crowding_proxy(
        rotation, observations, lookback_observations=lookback_observations
    )


async def build_portfolio_risk_inputs_v1(
    codes: Sequence[str],
    *,
    lookback: int = 60,
    factor_risk_context: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Build source-labelled correlation and liquidity inputs for a portfolio."""
    return await PortfolioRiskInputBuilder().build(
        codes, lookback=lookback, factor_risk_context=factor_risk_context
    )


async def build_market_desk_overview(
    *,
    etf_codes: Sequence[str] = (),
    industry_codes: Sequence[str] = (),
) -> dict[str, Any]:
    """Build a whole-market observation packet and its risk-permission state.

    The result is research support for the end-of-day market desk. It is not a
    trading instruction and it does not infer unavailable fund-flow data.
    """
    snapshot = await build_market_snapshot_v1(
        etf_codes=etf_codes,
        industry_codes=industry_codes,
    )
    assessment = assess_market_regime(snapshot)
    return {
        "schema_version": "market_desk_overview.v1",
        "snapshot": snapshot,
        "regime": assessment.to_dict(),
    }


async def discover_public_market_desk_opportunities(
    *,
    include_concepts: bool = True,
    observation_limit: int = 20,
    candidate_limit: int = 20,
    min_amount: float = 200_000_000.0,
    min_change_pct: float = 3.0,
    market_map_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Discover whole-market public-data research observations.

    This is deliberately not a candidate gate and cannot release a formal
    paper-plan decision.  It combines broad-market permission, board context,
    and one public A-share universe snapshot into a transparent work queue for
    the research team.
    """
    service = PublicMarketDiscoveryService()
    market_overview, rotation, universe_snapshot = await asyncio.gather(
        build_market_desk_overview(),
        build_market_rotation_v1(
            include_concepts=include_concepts,
            observation_limit=observation_limit,
        ),
        service.build_universe_snapshot(),
    )
    discovery = service.discover(
        market_overview=market_overview,
        rotation=rotation,
        universe_snapshot=universe_snapshot,
        candidate_limit=candidate_limit,
        min_amount=min_amount,
        min_change_pct=min_change_pct,
    )
    return _attach_discovery_market_subject_context(
        discovery, market_map_path=market_map_path
    )


async def build_market_desk_team_packet(
    *,
    include_concepts: bool = True,
    observation_limit: int = 20,
    candidate_limit: int = 20,
    min_amount: float = 200_000_000.0,
    min_change_pct: float = 3.0,
    market_map_path: Optional[Path] = None,
    user_id: str = "default",
    ledger_path: Optional[Path] = None,
    restricted_list_path: Optional[Path] = None,
    portfolio_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Build one shared whole-market packet for the complete research desk.

    This is the executable handoff between public market observation and the
    agent team.  It intentionally performs no lifecycle transition, paper
    trade, alert, or order action.  All roles receive the same timestamped
    inputs, which prevents a portfolio manager or a short-term role from
    silently working from a different market snapshot than the data verifier.
    """
    discovery_service = PublicMarketDiscoveryService()
    overview, rotation, universe_snapshot = await asyncio.gather(
        build_market_desk_overview(),
        build_market_rotation_v1(
            include_concepts=include_concepts,
            observation_limit=observation_limit,
        ),
        discovery_service.build_universe_snapshot(),
    )
    discovery = discovery_service.discover(
        market_overview=overview,
        rotation=rotation,
        universe_snapshot=universe_snapshot,
        candidate_limit=candidate_limit,
        min_amount=min_amount,
        min_change_pct=min_change_pct,
    )
    discovery = _attach_discovery_market_subject_context(
        discovery, market_map_path=market_map_path
    )
    readiness = assess_market_desk_operational_readiness(
        user_id=user_id,
        ledger_path=ledger_path,
        restricted_list_path=restricted_list_path,
        portfolio_path=portfolio_path,
    )
    strategy_books = get_market_desk_strategy_books(ledger_path=ledger_path)
    review_queue = get_market_desk_review_queue(ledger_path=ledger_path)
    postmortem_queue = get_market_desk_postmortem_queue(ledger_path=ledger_path)
    snapshot = overview.get("snapshot") if isinstance(overview, Mapping) else {}
    observed_at = snapshot.get("observed_at") if isinstance(snapshot, Mapping) else None
    return {
        "schema_version": "market-desk-team-packet.v1",
        "observed_at": observed_at,
        "market_data_mode": readiness["market_data_mode"],
        "market_overview": overview,
        "rotation": rotation,
        "whole_market_discovery": discovery,
        "operational_readiness": readiness,
        "strategy_books": strategy_books,
        "review_queue": review_queue,
        "postmortem_queue": postmortem_queue,
        "playbook_catalog": list_market_desk_playbooks(),
        "team_orchestration": {
            "shared_packet_contract": "Every role must use this packet before supplementary evidence collection.",
            "sequence": [
                "market-regime-analyst",
                "sector-rotation-analyst",
                "data-verifier",
                "short-term-trader and execution-liquidity-analyst when the regime permits",
                "swing-trend-analyst, fundamental-analyst, and industry-analyst",
                "valuation-specialist and house-view-analyst for long horizon",
                "quant-risk-modeler, risk-analyst, portfolio-manager, and contrarian-analyst",
                "compliance-officer final boundary check",
            ],
            "binding_veto_roles": [
                "data-verifier",
                "risk-analyst",
                "quant-risk-modeler",
                "execution-liquidity-analyst",
                "compliance-officer",
            ],
            "candidate_books": {
                "ultra_short": "1-3 trading days; require reproducible intraday execution data before a leader, auction, board, or emotional-repair setup may advance beyond watch.",
                "short_term": "1-10 trading days; only conditional setups with T+1, liquidity, price-limit, suspension, and overnight stress controls.",
                "swing": "2-12 weeks; require market regime, rotation, earnings/catalyst, and trend evidence.",
                "long_term": "6-24 months; require valuation, earnings quality, industry, and contrarian evidence.",
            },
            "prohibited_actions": [
                "order placement",
                "broker account access",
                "unsupported fund-flow or order-book claims",
                "promotion of a discovery observation directly to a paper position",
            ],
        },
        "next_controls": {
            "candidate_gate": "Every selected observation must pass universe, data, edge, risk, execution, and compliance gates before IC review.",
            "ic": "IC requires five named control assessments, evidence references, decision owner, and model versions.",
            "paper_entry": "A governed research-only paper entry additionally requires a valid active strategy, frozen entry observation, and current signed restricted-list authority.",
        },
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }


def list_market_desk_playbooks() -> dict[str, Any]:
    """Return the desk's eight standard research-only A-share playbooks."""
    return {
        "schema_version": "market-desk-playbook-catalog.v1",
        "playbooks": list_playbooks(),
        "research_only": True,
        "no_order_execution": True,
    }


def evaluate_market_desk_playbook(
    playbook_id: str,
    evidence: Mapping[str, Any],
    *,
    regime: str,
) -> dict[str, Any]:
    """Check one evidence packet against a named discretionary playbook.

    The result only determines whether the research setup can proceed to the
    desk's separate candidate and investment-committee controls. It cannot
    place, route, or amend an order.
    """
    return evaluate_playbook(playbook_id, evidence, regime)


def _attach_discovery_market_subject_context(
    discovery: Mapping[str, Any], *, market_map_path: Optional[Path]
) -> dict[str, Any]:
    """Attach stored, source-referenced market relationships to observations.

    Relationship mappings are not an alpha factor and never change the
    discovery ranking.  They simply allow research agents to begin from a
    documented industry/theme context rather than infer one from a ticker name.
    """
    result = dict(discovery)
    candidates = result.get("candidates")
    if not isinstance(candidates, list):
        result["market_subject_mapping_coverage"] = {
            "mapped_candidate_count": 0,
            "unmapped_candidate_count": 0,
            "mapping_status": "no_candidates",
        }
        return result
    store = MarketMapStore(_resolve_market_map_path(market_map_path))
    mapped = 0
    enriched: list[dict[str, Any]] = []
    for candidate in candidates:
        item = dict(candidate) if isinstance(candidate, Mapping) else {"raw_candidate": candidate}
        context = store.resolve(str(item.get("code") or ""))
        source_refs = context.get("source_refs") if isinstance(context, Mapping) else []
        is_mapped = bool(
            isinstance(context, Mapping)
            and context.get("found") is True
            and isinstance(source_refs, list)
            and source_refs
        )
        item["market_subject_context"] = context
        item["market_subject_mapping_status"] = (
            "source_mapped" if is_mapped else "mapping_required"
        )
        mapped += int(is_mapped)
        enriched.append(item)
    result["candidates"] = enriched
    result["market_subject_mapping_coverage"] = {
        "mapped_candidate_count": mapped,
        "unmapped_candidate_count": len(enriched) - mapped,
        "mapping_status": "source_referenced_context_only",
        "decision_weight": 0,
    }
    warnings = list(result.get("warnings") or [])
    if len(enriched) > mapped:
        warnings.append(
            "One or more discovery observations lacks a source-referenced market-subject mapping; sector/theme context must be verified before research promotion."
        )
    result["warnings"] = list(dict.fromkeys(str(warning) for warning in warnings))
    return result


async def record_public_market_desk_discovery(
    *,
    include_concepts: bool = True,
    observation_limit: int = 20,
    candidate_limit: int = 20,
    min_amount: float = 200_000_000.0,
    min_change_pct: float = 3.0,
    eod_session: Optional[Mapping[str, Any]] = None,
    archive_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Freeze one public whole-market discovery queue for research audit.

    The immutable record preserves the full public-universe snapshot and the
    selection rule that produced the queue.  It deliberately remains outside
    the formal candidate and paper-plan release paths.
    """
    discovery = await discover_public_market_desk_opportunities(
        include_concepts=include_concepts,
        observation_limit=observation_limit,
        candidate_limit=candidate_limit,
        min_amount=min_amount,
        min_change_pct=min_change_pct,
    )
    if eod_session is not None:
        discovery = {**discovery, "eod_session": dict(eod_session)}
    packet = build_public_market_observation_packet(
        subject="market_desk_discovery",
        observation=discovery,
    )
    result = dict(discovery)
    result.update(packet.to_dict())
    destination = Path(
        archive_directory or PROJECT_ROOT / "data" / "market-desk-discovery-archives"
    )
    result["source_archive_path"] = str(packet.write_frozen_archive(destination))
    result["operation"] = "record_public_discovery_only"
    result["limitations"] = [
        *list(result.get("limitations") or []),
        "The frozen record proves the public discovery inputs and selection rule, not formal-candidate eligibility or a paper-plan release.",
    ]
    return result


async def enrich_public_discovery_industry_context(
    discovery_archive_path: str | Path,
    *,
    mapping_archive_directory: str | Path,
    market_map_path: Optional[Path] = None,
    candidate_limit: int = 20,
) -> dict[str, Any]:
    """Freeze public industry context for candidates from one discovery archive.

    This is a research-routing bridge, not a theme classifier or a candidate
    approval.  It accepts only a hash-verified public discovery archive and
    freezes the normalized industry lookup before persisting any mapping.
    """
    if candidate_limit < 1 or candidate_limit > 100:
        raise ValueError("candidate_limit must be between 1 and 100")
    archive_path = Path(discovery_archive_path)
    assurance = verify_public_market_discovery_archive(archive_path)
    if assurance.get("status") != "pass":
        raise ValueError(
            "industry enrichment requires a verified public discovery archive: "
            + "; ".join(str(item) for item in assurance.get("failures") or ())
        )
    try:
        payload = json.loads(archive_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to read verified discovery archive: {error}") from error
    raw_records = payload.get("raw_source_records") if isinstance(payload, Mapping) else None
    discovery = raw_records.get("market_desk_discovery") if isinstance(raw_records, Mapping) else None
    candidates = discovery.get("candidates") if isinstance(discovery, Mapping) else None
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes, bytearray)):
        raise ValueError("verified discovery archive lacks a candidate list")
    selected = [item for item in candidates if isinstance(item, Mapping)][:candidate_limit]
    observed_at = str(discovery.get("observed_at") or "") if isinstance(discovery, Mapping) else ""
    service = get_industry_service()
    await service.initialize()
    lookups: list[dict[str, Any]] = []
    failures: list[dict[str, str]] = []
    for candidate in selected:
        code = str(candidate.get("code") or "").strip()
        if not code:
            failures.append({"code": "", "reason": "discovery candidate lacks code"})
            continue
        try:
            stock_industry = await asyncio.wait_for(
                service.get_stock_industry(code), timeout=15
            )
        except Exception as error:
            failures.append({"code": code, "reason": f"industry lookup failed: {error}"})
            continue
        if stock_industry is None or not str(stock_industry.industry).strip():
            failures.append({"code": code, "reason": "industry lookup returned no usable industry"})
            continue
        lookups.append(
            {
                "code": stock_industry.code,
                "name": stock_industry.name or str(candidate.get("name") or ""),
                "industry": stock_industry.industry,
                "industry_code": stock_industry.industry_code,
                "industry_change": stock_industry.industry_change,
                "source_adapter": "akshare.stock_individual_info_em",
            }
        )
    observation = {
        "schema_version": "market-desk-public-industry-enrichment.v1",
        "observed_at": observed_at,
        "source_discovery_archive_id": assurance["archive_id"],
        "source_discovery_archive_path": str(archive_path),
        "industry_lookups": lookups,
        "lookup_failures": failures,
        "research_only": True,
        "formal_decision_eligible": False,
        "no_order_execution": True,
    }
    packet = build_public_market_observation_packet(
        subject="market_desk_public_industry_enrichment",
        observation=observation,
        observed_at=observed_at,
    )
    mapping_archive_path = packet.write_frozen_archive(Path(mapping_archive_directory))
    store = MarketMapStore(_resolve_market_map_path(market_map_path))
    stored: list[dict[str, Any]] = []
    for lookup in lookups:
        code = str(lookup["code"])
        mapping = MarketSubjectMapping(
            code=code,
            name=str(lookup["name"]),
            industry=str(lookup["industry"]),
            industry_code=(
                str(lookup["industry_code"])
                if lookup.get("industry_code") is not None
                else None
            ),
            source_refs=[
                f"public-industry-enrichment:{packet.archive_id}:{code}",
                f"source-discovery:{assurance['archive_id']}",
            ],
            updated_at=packet.observed_at,
        )
        stored.append(store.upsert(mapping).to_dict())
    return {
        "schema_version": "market-desk-public-industry-enrichment-result.v1",
        "source_discovery_archive_assurance": assurance,
        "mapping_archive_id": packet.archive_id,
        "mapping_archive_path": str(mapping_archive_path),
        "market_map_path": str(store.path),
        "requested_candidate_count": len(selected),
        "mapped_count": len(stored),
        "failed_count": len(failures),
        "mappings": stored,
        "failures": failures,
        "research_only": True,
        "formal_decision_eligible": False,
        "no_order_execution": True,
        "warnings": [
            "Public industry mappings route research only; they do not establish a catalyst, theme exposure, or formal candidate eligibility.",
            "Only the linked frozen discovery and enrichment archives support this mapping context.",
        ],
    }


async def run_public_market_desk_eod_discovery(
    *,
    include_concepts: bool = True,
    observation_limit: int = 20,
    candidate_limit: int = 20,
    min_amount: float = 200_000_000.0,
    min_change_pct: float = 3.0,
    archive_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Record one public discovery archive only after a verified market close.

    The scheduler uses this idempotent job for an evidence-bound daily research
    queue. A skipped result writes no archive and cannot affect strategy or
    portfolio state.
    """
    overview = await build_market_desk_overview()
    snapshot = overview.get("snapshot")
    session = snapshot.get("market_session") if isinstance(snapshot, Mapping) else None
    session_state = str(session.get("state") if isinstance(session, Mapping) else "")
    calendar_basis = str(session.get("calendar_basis") if isinstance(session, Mapping) else "")
    if session_state != "after_close" or calendar_basis != "exchange_calendar":
        return {
            "schema_version": "market-desk-public-eod-discovery-job.v1",
            "status": "skipped",
            "reason": "verified_exchange_after_close_required",
            "market_overview": overview,
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }
    destination = Path(
        archive_directory or PROJECT_ROOT / "data" / "market-desk-discovery-archives"
    )
    observed_at = str(snapshot.get("observed_at") or "") if isinstance(snapshot, Mapping) else ""
    session_date = observed_at[:10]
    history = list_public_market_discovery_archives(destination)
    existing_ids = [
        str(record.get("archive_id") or "")
        for record in history["records"]
        if record.get("status") == "pass"
        and isinstance(record.get("eod_validation"), Mapping)
        and record["eod_validation"].get("status") == "pass"
        and isinstance(record.get("coverage_validation"), Mapping)
        and record["coverage_validation"].get("status") == "pass"
        and str(record.get("observed_at") or "").startswith(session_date)
    ]
    if session_date and existing_ids:
        return {
            "schema_version": "market-desk-public-eod-discovery-job.v1",
            "status": "skipped",
            "reason": "valid_eod_discovery_exists_for_session_date",
            "observed_at": observed_at,
            "existing_archive_ids": existing_ids,
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }
    result = await record_public_market_desk_discovery(
        include_concepts=include_concepts,
        observation_limit=observation_limit,
        candidate_limit=candidate_limit,
        min_amount=min_amount,
        min_change_pct=min_change_pct,
        eod_session={
            "state": session_state,
            "calendar_basis": calendar_basis,
            "session_date": session_date,
            "market_overview_observed_at": observed_at,
        },
        archive_directory=destination,
    )
    return {
        **result,
        "job_schema_version": "market-desk-public-eod-discovery-job.v1",
        "status": "recorded",
    }


def get_public_market_desk_discovery_history(
    *, archive_directory: Optional[str | Path] = None
) -> dict[str, Any]:
    """Return an integrity-checked history of public discovery records."""
    return list_public_market_discovery_archives(
        archive_directory or PROJECT_ROOT / "data" / "market-desk-discovery-archives"
    )


def promote_public_market_desk_discovery_candidate(
    *,
    source_archive_path: str | Path,
    candidate_id: str,
    ledger_path: Optional[Path] = None,
    created_by: str = "market-desk",
    market_map_path: Optional[Path] = None,
    mapping_archive_path: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Create one monitoring research entry from a frozen public discovery.

    Promotion is intentionally explicit and creates a monitoring entry only.
    It cannot form a strategy plan, candidate approval, or paper position.
    """
    archive_path = Path(source_archive_path)
    assurance = verify_frozen_market_data_archive(
        archive_path,
        expected_source="akshare_public",
    )
    if assurance.get("status") != "pass":
        failures = assurance.get("failures")
        detail = "; ".join(str(item) for item in failures) if isinstance(failures, list) else "unknown archive verification failure"
        raise ValueError(f"public discovery archive is not verifiable: {detail}")
    try:
        archive = json.loads(archive_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"public discovery archive cannot be read: {error}") from error
    records = archive.get("raw_source_records") if isinstance(archive, Mapping) else None
    discovery = records.get("market_desk_discovery") if isinstance(records, Mapping) else None
    if not isinstance(discovery, Mapping):
        raise ValueError("archive does not contain a market_desk_discovery record")
    if discovery.get("schema_version") != "market-desk-public-discovery.v1":
        raise ValueError("archive contains an unsupported discovery schema")
    if discovery.get("formal_decision_eligible") is not False or discovery.get("no_order_execution") is not True:
        raise ValueError("discovery archive must retain research-only and no-order boundaries")
    candidates = discovery.get("candidates")
    selected = next(
        (
            dict(candidate)
            for candidate in candidates if isinstance(candidate, Mapping)
            and str(candidate.get("candidate_id") or "") == str(candidate_id).strip()
        ),
        None,
    ) if isinstance(candidates, Sequence) and not isinstance(candidates, (str, bytes)) else None
    if selected is None:
        raise ValueError("candidate_id was not found in the verified discovery archive")
    if selected.get("formal_decision_eligible") is not False or selected.get("no_order_execution") is not True:
        raise ValueError("selected discovery candidate has an invalid decision boundary")
    code = str(selected.get("code") or "").strip()
    if len(code) != 6 or not code.isdigit():
        raise ValueError("selected discovery candidate must contain a six-digit stock code")
    mapping_archive_assurance: Optional[dict[str, Any]] = None
    if selected.get("market_subject_mapping_status") != "source_mapped":
        if mapping_archive_path is None:
            raise ValueError(
                "selected discovery candidate requires a source-referenced market-subject mapping; "
                "a later industry mapping requires its verified frozen mapping_archive_path"
            )
        mapping_archive_assurance = _verify_public_discovery_industry_enrichment_archive(
            mapping_archive_path,
            discovery_archive_id=str(assurance["archive_id"]),
            code=code,
        )
        refreshed_context = MarketMapStore(
            _resolve_market_map_path(market_map_path)
        ).resolve(code)
        refreshed_refs = (
            refreshed_context.get("source_refs")
            if isinstance(refreshed_context, Mapping)
            else None
        )
        discovery_ref = f"source-discovery:{assurance['archive_id']}"
        enrichment_ref = (
            f"public-industry-enrichment:{mapping_archive_assurance['archive_id']}:{code}"
        )
        if (
            isinstance(refreshed_context, Mapping)
            and refreshed_context.get("found") is True
            and isinstance(refreshed_refs, list)
            and discovery_ref in refreshed_refs
            and enrichment_ref in refreshed_refs
        ):
            selected["market_subject_context"] = refreshed_context
            selected["market_subject_mapping_status"] = "source_mapped"
    mapping_context = selected.get("market_subject_context")
    mapping_refs = (
        mapping_context.get("source_refs") if isinstance(mapping_context, Mapping) else None
    )
    if (
        selected.get("market_subject_mapping_status") != "source_mapped"
        or not isinstance(mapping_context, Mapping)
        or mapping_context.get("found") is not True
        or not isinstance(mapping_refs, list)
        or not mapping_refs
    ):
        raise ValueError(
            "selected discovery candidate requires a source-referenced market-subject mapping before research promotion"
        )
    resolved_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_path)
    duplicate_candidates = ledger.find_duplicate_candidates(
        targets=[code], tags=["public-discovery"], limit=20
    )
    if duplicate_candidates:
        existing = duplicate_candidates[0]["entry"]
        return {
            "success": True,
            "status": "already_promoted",
            "ledger_path": str(resolved_path),
            "entry": existing,
            "source_archive_assurance": assurance,
            "mapping_archive_assurance": mapping_archive_assurance,
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }

    source_manifest = discovery.get("source_manifest")
    observation = selected.get("observation")
    name = str(selected.get("name") or code).strip()
    entry = ResearchEntry(
        title=f"Public discovery monitoring: {name} ({code})",
        thesis=(
            "A source-frozen public whole-market snapshot selected this target for "
            "research observation under disclosed liquidity and daily-move filters; "
            "this is not an investment thesis or a paper-position recommendation."
        ),
        targets=[code],
        target_type="public_discovery_observation",
        status=ResearchStatus.MONITORING,
        catalysts=[],
        risks=[
            "Public snapshot selection may be transient and has no source-verified fund-flow, positioning, or order-book evidence.",
            "The attached market-subject mapping is research context only and does not establish a causal catalyst.",
            "No candidate, risk, execution, compliance, or investment-committee gate has been completed.",
        ],
        monitoring_triggers=[
            ResearchTrigger(
                name="research_evidence_gate",
                condition="Collect source-verified catalyst and risk evidence before any candidate-gate evaluation.",
                direction="watch",
                source="market-desk-public-discovery",
            )
        ],
        invalidation_conditions=[
            "Verified follow-up evidence does not support a distinct thesis, catalyst, or liquid eligible universe.",
            "The source-frozen discovery archive fails integrity verification.",
        ],
        tags=["market-desk", "public-discovery", "research-only"],
        data_quality={
            "source": "akshare_public",
            "quality_tier": "public_observation",
            "formal_decision_eligible": False,
            "source_archive_assurance": assurance,
        },
        source_refs=[
            {
                "source": "akshare_public",
                "archive_id": str(archive.get("archive_id") or ""),
                "archive_path": str(archive_path),
                "subject": "market_desk_discovery",
                "candidate_id": str(selected.get("candidate_id") or ""),
            }
        ],
        metadata={
            "public_discovery": {
                "candidate": selected,
                "selection_rule": discovery.get("selection_rule", {}),
                "source_manifest": source_manifest if isinstance(source_manifest, Mapping) else {},
                "source_archive_path": str(archive_path),
            }
        },
        created_by=created_by,
    )
    created = ledger.create(entry)
    return {
        "success": True,
        "status": "promoted_to_monitoring",
        "ledger_path": str(resolved_path),
        "entry": created.to_dict(),
        "source_archive_assurance": assurance,
        "mapping_archive_assurance": mapping_archive_assurance,
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }


def _verify_public_discovery_industry_enrichment_archive(
    path: str | Path,
    *,
    discovery_archive_id: str,
    code: str,
) -> dict[str, Any]:
    """Verify that a public mapping archive truly belongs to this candidate."""
    archive_path = Path(path)
    assurance = verify_frozen_market_data_archive(
        archive_path, expected_source="akshare_public"
    )
    if assurance.get("status") != "pass":
        raise ValueError(
            "industry mapping archive is not verifiable: "
            + "; ".join(str(item) for item in assurance.get("failures") or ())
        )
    try:
        archive = json.loads(archive_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"industry mapping archive cannot be read: {error}") from error
    records = archive.get("raw_source_records") if isinstance(archive, Mapping) else None
    enrichment = (
        records.get("market_desk_public_industry_enrichment")
        if isinstance(records, Mapping)
        else None
    )
    if not isinstance(enrichment, Mapping):
        raise ValueError("industry mapping archive lacks a public enrichment record")
    if enrichment.get("schema_version") != "market-desk-public-industry-enrichment.v1":
        raise ValueError("industry mapping archive has an unsupported enrichment schema")
    if str(enrichment.get("source_discovery_archive_id") or "") != discovery_archive_id:
        raise ValueError("industry mapping archive does not link to the selected discovery archive")
    lookups = enrichment.get("industry_lookups")
    if not isinstance(lookups, Sequence) or isinstance(lookups, (str, bytes, bytearray)):
        raise ValueError("industry mapping archive lacks industry lookup records")
    if not any(isinstance(item, Mapping) and str(item.get("code") or "") == code for item in lookups):
        raise ValueError("industry mapping archive does not contain the selected discovery code")
    return assurance


async def run_public_market_desk_observation(
    *,
    etf_codes: Sequence[str] = (),
    industry_codes: Sequence[str] = (),
    include_concepts: bool = True,
    observation_limit: int = 20,
    archive_directory: Optional[str | Path] = None,
    rotation_archive_directory: Optional[str | Path] = None,
    ledger_path: Optional[Path] = None,
    restricted_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Record one whole-market public-data desk observation.

    This is the daily operating lane for public data: it freezes the rotation
    input, retains the source-labelled market overview, and records readiness.
    It does not evaluate a stock candidate or create an order-like action.
    """
    overview, frozen_rotation = await asyncio.gather(
        build_market_desk_overview(
            etf_codes=etf_codes,
            industry_codes=industry_codes,
        ),
        freeze_public_market_rotation_observation(
            include_concepts=include_concepts,
            observation_limit=observation_limit,
            archive_directory=rotation_archive_directory
            or PROJECT_ROOT / "data" / "market-observation-archives",
        ),
    )
    rotation_archive_assurance = _verify_public_rotation_observation_archive(
        frozen_rotation
    )
    frozen_rotation = {
        **frozen_rotation,
        "source_archive_assurance": rotation_archive_assurance,
    }
    readiness = assess_market_desk_operational_readiness(
        ledger_path=ledger_path,
        restricted_list_path=restricted_list_path,
        observation_archive_directory=archive_directory,
    )
    run = build_public_desk_observation_run(
        market_overview=overview,
        rotation_observation=frozen_rotation,
        operational_readiness=readiness,
    )
    result = run.to_dict()
    result["rotation_archive_assurance"] = rotation_archive_assurance
    result["source_archive_path"] = str(
        run.write(archive_directory or PROJECT_ROOT / "data" / "market-desk-observation-runs")
    )
    return result


async def run_public_market_desk_eod_observation(
    *,
    etf_codes: Sequence[str] = (),
    industry_codes: Sequence[str] = (),
    include_concepts: bool = True,
    observation_limit: int = 20,
    archive_directory: Optional[str | Path] = None,
    rotation_archive_directory: Optional[str | Path] = None,
    ledger_path: Optional[Path] = None,
    restricted_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run the scheduled public EOD observation only after a verified close.

    A scheduler must not manufacture a daily record on weekends, holidays, or
    before close.  A skipped result is successful control behavior, not an
    EOD observation and never creates a source archive.
    """
    overview = await build_market_desk_overview(
        etf_codes=etf_codes,
        industry_codes=industry_codes,
    )
    snapshot = overview.get("snapshot")
    session = snapshot.get("market_session") if isinstance(snapshot, Mapping) else None
    session_state = str(session.get("state") if isinstance(session, Mapping) else "").strip()
    calendar_basis = str(session.get("calendar_basis") if isinstance(session, Mapping) else "").strip()
    if session_state != "after_close" or calendar_basis != "exchange_calendar":
        return {
            "schema_version": "market-desk-public-eod-observation-job.v1",
            "status": "skipped",
            "reason": "verified_exchange_after_close_required",
            "market_overview": overview,
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }

    observation_directory = Path(
        archive_directory or PROJECT_ROOT / "data" / "market-desk-observation-runs"
    )
    observed_at = (
        str(snapshot.get("observed_at") or "") if isinstance(snapshot, Mapping) else ""
    )
    session_date = observed_at[:10]
    existing_history = list_public_desk_observation_runs(observation_directory)
    existing_records = [
        record
        for record in existing_history["records"]
        if record.get("status") == "pass"
        and isinstance(record.get("eod_validation"), Mapping)
        and record["eod_validation"].get("status") == "pass"
        and str(record.get("observed_at") or "").startswith(session_date)
    ]
    if session_date and existing_records:
        return {
            "schema_version": "market-desk-public-eod-observation-job.v1",
            "status": "skipped",
            "reason": "valid_eod_observation_exists_for_session_date",
            "observed_at": observed_at,
            "existing_archive_ids": [
                str(record.get("archive_id") or "") for record in existing_records
            ],
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
        }

    frozen_rotation = await freeze_public_market_rotation_observation(
        include_concepts=include_concepts,
        observation_limit=observation_limit,
        archive_directory=rotation_archive_directory
        or PROJECT_ROOT / "data" / "market-observation-archives",
    )
    rotation_archive_assurance = _verify_public_rotation_observation_archive(
        frozen_rotation
    )
    frozen_rotation = {
        **frozen_rotation,
        "source_archive_assurance": rotation_archive_assurance,
    }
    readiness = assess_market_desk_operational_readiness(
        ledger_path=ledger_path,
        restricted_list_path=restricted_list_path,
        observation_archive_directory=observation_directory,
    )
    run = build_public_desk_observation_run(
        market_overview=overview,
        rotation_observation=frozen_rotation,
        operational_readiness=readiness,
    )
    result = run.to_dict()
    result.update(
        {
            "job_schema_version": "market-desk-public-eod-observation-job.v1",
            "status": "recorded",
            "source_archive_path": str(
                run.write(observation_directory)
            ),
            "rotation_archive_assurance": rotation_archive_assurance,
        }
    )
    return result


def _verify_public_rotation_observation_archive(
    frozen_rotation: Mapping[str, Any],
) -> dict[str, Any]:
    """Independently validate the rotation source archive before desk binding."""
    manifest = frozen_rotation.get("source_manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("public desk observation requires a rotation source manifest")
    archive_path = frozen_rotation.get("source_archive_path")
    archive_id = str(manifest.get("archive_id") or "").strip()
    source = str(manifest.get("source") or "").strip()
    assurance = verify_frozen_market_data_archive(
        str(archive_path or ""),
        expected_archive_id=archive_id or None,
        expected_source=source or None,
    )
    if assurance.get("status") != "pass":
        failures = assurance.get("failures")
        detail = (
            "; ".join(str(item) for item in failures)
            if isinstance(failures, Sequence) and not isinstance(failures, (str, bytes))
            else "unknown verification failure"
        )
        raise ValueError(f"public desk observation requires a valid frozen rotation archive: {detail}")
    return assurance


def get_public_market_desk_observation_history(
    *,
    archive_directory: Optional[str | Path] = None,
    exception_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Return integrity-checked public market-desk observation history."""
    return list_public_desk_observation_runs(
        archive_directory or PROJECT_ROOT / "data" / "market-desk-observation-runs",
        exception_directory=exception_directory,
    )


def resolve_public_market_desk_observation_duplicate(
    *,
    session_date: str,
    archive_ids: Sequence[str],
    canonical_archive_id: str,
    reviewer: str,
    reason: str,
    evidence_refs: Sequence[str],
    reviewed_at: Optional[str | datetime] = None,
    archive_directory: Optional[str | Path] = None,
    exception_directory: Optional[str | Path] = None,
) -> dict[str, Any]:
    """Write an immutable evidence-bound review of duplicate desk records."""
    observation_directory = Path(
        archive_directory or PROJECT_ROOT / "data" / "market-desk-observation-runs"
    )
    history = list_public_desk_observation_runs(observation_directory)
    valid_ids = {
        str(record.get("archive_id") or "")
        for record in history["records"]
        if record.get("status") == "pass"
        and str(record.get("observed_at") or "").startswith(session_date)
    }
    submitted_ids = {str(value).strip() for value in archive_ids if str(value).strip()}
    if submitted_ids != valid_ids:
        raise ValueError("exception review archive_ids must exactly match all valid records for session_date")
    review = create_public_desk_observation_exception_review(
        session_date=session_date,
        archive_ids=archive_ids,
        canonical_archive_id=canonical_archive_id,
        reviewer=reviewer,
        reason=reason,
        evidence_refs=evidence_refs,
        reviewed_at=reviewed_at,
    )
    review_path = review.write(
        exception_directory
        or observation_directory.parent / "market-desk-observation-exceptions"
    )
    return {
        "success": True,
        "review": review.to_dict(),
        "review_path": str(review_path),
        "research_only": True,
        "no_order_execution": True,
    }


def evaluate_market_desk_candidate(
    candidate: Mapping[str, Any],
    *,
    regime: str,
    control_assessments: Optional[Mapping[str, Any]] = None,
    restricted_targets: Sequence[str] = (),
    restricted_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Evaluate the five mandatory paper-plan candidate gates."""
    candidate_with_compliance, effective_restricted = _candidate_with_restricted_list_context(
        candidate,
        restricted_targets=restricted_targets,
        restricted_list_path=restricted_list_path,
    )
    return evaluate_candidate_gate(
        candidate_with_compliance,
        regime=regime,
        control_assessments=control_assessments,
        restricted_targets=effective_restricted,
    ).to_dict()


def evaluate_market_desk_observation_action(
    candidate: Mapping[str, Any], *, regime: str
) -> dict[str, Any]:
    """Return a conditional research action from labelled observation data.

    This is the no-broker, no-order lane for daily technical instructions. It
    cannot produce a formal IC decision or an active paper-plan release.
    """
    return evaluate_observation_action(candidate, regime=regime).to_dict()


def decide_market_desk_investment_committee(
    candidate: Mapping[str, Any],
    *,
    candidate_id: str,
    regime: str,
    control_assessments: Mapping[str, Any],
    decision_owner: str,
    evidence_refs: Sequence[str] = (),
    model_versions: Optional[Mapping[str, Any]] = None,
    decided_at: Optional[str] = None,
    restricted_targets: Sequence[str] = (),
    restricted_list_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Create the authoritative investment-committee decision packet.

    This is a paper-desk record only. It validates mandatory control roles and
    emits no brokerage or order-execution action.
    """
    candidate_with_compliance, effective_restricted = _candidate_with_restricted_list_context(
        candidate,
        restricted_targets=restricted_targets,
        restricted_list_path=restricted_list_path,
    )
    return decide_investment_committee(
        candidate_with_compliance,
        candidate_id=candidate_id,
        regime=regime,
        control_assessments=control_assessments,
        decision_owner=decision_owner,
        evidence_refs=evidence_refs,
        model_versions=model_versions,
        decided_at=decided_at,
        restricted_targets=effective_restricted,
    ).to_dict()


def upsert_market_desk_restricted_list_entry(
    entry: Mapping[str, Any], *, restricted_list_path: Optional[Path] = None
) -> dict[str, Any]:
    """Record an externally sourced restricted-list or clearance record."""
    resolved_path = restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH
    stored = RestrictedListStore(resolved_path).upsert(RestrictedListEntry.from_dict(entry))
    health = RestrictedListStore(resolved_path).health()
    return {"success": True, "restricted_list_path": str(resolved_path), "entry": stored.to_dict(), "health": health}


def get_market_desk_restricted_list_health(
    *, restricted_list_path: Optional[Path] = None
) -> dict[str, Any]:
    """Return currency and active-target state for the restricted-list authority."""
    resolved_path = restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH
    return {"restricted_list_path": str(resolved_path), **RestrictedListStore(resolved_path).health()}


def import_signed_market_desk_restricted_list(
    payload: Mapping[str, Any], *, restricted_list_path: Optional[Path] = None
) -> dict[str, Any]:
    """Import a compliance-authority payload only when its configured MAC verifies."""
    resolved_path = restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH
    health = RestrictedListStore(resolved_path).import_signed_payload(payload)
    return {"success": True, "restricted_list_path": str(resolved_path), "health": health}


def verify_market_desk_paper_release(
    *,
    snapshot: Mapping[str, Any],
    rotation: Mapping[str, Any],
    candidate: Mapping[str, Any],
    ic_decision: Mapping[str, Any],
    strategy_plan: Mapping[str, Any],
    risk_budget: Mapping[str, Any],
    structural_risk: Mapping[str, Any],
    restricted_list_health: Mapping[str, Any],
    require_full_rotation: bool = False,
    decision_review: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Independently verify completeness of a paper-desk release package."""
    return verify_paper_desk_release(
        snapshot=snapshot,
        rotation=rotation,
        candidate=candidate,
        ic_decision=ic_decision,
        strategy_plan=strategy_plan,
        risk_budget=risk_budget,
        structural_risk=structural_risk,
        restricted_list_health=restricted_list_health,
        require_full_rotation=require_full_rotation,
        decision_review=decision_review,
    ).to_dict()


def _candidate_with_restricted_list_context(
    candidate: Mapping[str, Any],
    *,
    restricted_targets: Sequence[str],
    restricted_list_path: Optional[Path],
) -> tuple[dict[str, Any], tuple[str, ...]]:
    """Attach the persistent list's currency state without mutating caller data."""
    resolved_path = restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH
    health = RestrictedListStore(resolved_path).health()
    copied = dict(candidate)
    copied["restricted_list_snapshot"] = {
        "status": health.get("status"),
        "signature_status": health.get("signature_status"),
        "active_targets": list(health.get("active_targets") or ()),
        "version": health.get("version"),
    }
    compliance = copied.get("compliance")
    if isinstance(compliance, Mapping):
        copied_compliance = dict(compliance)
        copied_compliance["restricted_list_current"] = health["status"] == "current"
        copied["compliance"] = copied_compliance
    effective_targets = tuple(
        sorted(
            {
                *(str(item).strip() for item in restricted_targets if str(item).strip()),
                *(str(item).strip() for item in health["active_targets"] if str(item).strip()),
            }
        )
    )
    return copied, effective_targets


def create_market_desk_strategy_plan(
    plan: Mapping[str, Any],
    *,
    title: str,
    tags: Sequence[str] = (),
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Persist an observation-stage strategy plan in the research ledger."""
    strategy_plan = StrategyPlan.from_dict(plan)
    if strategy_plan.state != StrategyState.OBSERVATION:
        raise ValueError("new persisted strategy plans must start in observation")
    if strategy_plan.playbook_id is not None:
        definition = get_playbook(strategy_plan.playbook_id)
        if definition.horizon != strategy_plan.horizon.value:
            raise ValueError(
                "strategy plan horizon must match its market-desk playbook: "
                f"{strategy_plan.playbook_id} requires {definition.horizon}"
            )
    entry = ResearchEntry(
        title=title,
        thesis=strategy_plan.thesis,
        targets=[strategy_plan.target],
        target_type="strategy_plan",
        status=ResearchStatus.MONITORING,
        invalidation_conditions=[strategy_plan.invalidation_condition],
        tags=list(tags),
        source_refs=[{"reference": reference} for reference in strategy_plan.evidence_refs],
        metadata={"strategy_plan": strategy_plan.to_dict()},
        created_by="market-desk",
    )
    resolved_path = _resolve_research_ledger_path(ledger_path)
    created = ResearchLedger(resolved_path).create(entry)
    return {"success": True, "ledger_path": str(resolved_path), "entry": created.to_dict()}


def get_market_desk_strategy_books(
    *,
    ledger_path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Return the desk's persisted ultra-short, short, swing, and long research books.

    This is a read-only operational view over the research ledger. It reports
    review and time-stop status, but it never transitions a plan, approves a
    candidate, or creates an order instruction.
    """
    resolved_path = _resolve_research_ledger_path(ledger_path)
    reference_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    books: dict[str, list[dict[str, Any]]] = {
        StrategyHorizon.ULTRA_SHORT.value: [],
        StrategyHorizon.SHORT_TERM.value: [],
        StrategyHorizon.SWING.value: [],
        StrategyHorizon.LONG_TERM.value: [],
    }

    ignored_entries: list[str] = []
    for entry in ResearchLedger(resolved_path).list_entries(limit=10_000):
        plan_payload: Any = entry.metadata.get("strategy_plan")
        for observation in reversed(entry.observations):
            observed_plan = observation.evidence.get("strategy_plan")
            if isinstance(observed_plan, Mapping):
                plan_payload = observed_plan
                break
        if not isinstance(plan_payload, Mapping):
            continue
        try:
            plan = StrategyPlan.from_dict(plan_payload)
        except (TypeError, ValueError):
            ignored_entries.append(str(entry.entry_id))
            continue
        review_due = _market_desk_timestamp_due(plan.review_at, reference_time)
        time_stop_due = (
            _market_desk_timestamp_due(plan.time_stop_at, reference_time)
            if plan.time_stop_at
            else False
        )
        card = {
            "entry_id": entry.entry_id,
            "title": entry.title,
            "ledger_status": entry.status.value,
            "plan": plan.to_dict(),
            "review_due": review_due,
            "time_stop_due": time_stop_due,
            "attention": (
                "time_stop_due"
                if time_stop_due and plan.state in {StrategyState.OBSERVATION, StrategyState.WATCH, StrategyState.CONDITIONAL, StrategyState.ACTIVE}
                else "review_due"
                if review_due and plan.state in {StrategyState.OBSERVATION, StrategyState.WATCH, StrategyState.CONDITIONAL, StrategyState.ACTIVE}
                else "none"
            ),
        }
        books[plan.horizon.value].append(card)
    for cards in books.values():
        cards.sort(
            key=lambda card: (
                card["attention"] != "time_stop_due",
                card["attention"] != "review_due",
                str(card["plan"]["review_at"]),
                str(card["entry_id"]),
            )
        )
    return {
        "schema_version": "market-desk-strategy-books.v1",
        "as_of": reference_time.isoformat(),
        "ledger_path": str(resolved_path),
        "books": books,
        "book_counts": {horizon: len(cards) for horizon, cards in books.items()},
        "ignored_malformed_entry_ids": ignored_entries,
        "research_only": True,
        "no_order_execution": True,
        "warnings": [
            "This is a read-only paper-research view; it does not approve candidates or submit orders.",
            "A due review or time stop requires an explicit lifecycle review; this view does not alter plan state.",
        ],
    }


def get_market_desk_review_queue(
    *,
    ledger_path: Optional[Path] = None,
    now: Optional[datetime] = None,
) -> dict[str, Any]:
    """Return due strategy reviews without mutating a paper-plan lifecycle."""
    books = get_market_desk_strategy_books(ledger_path=ledger_path, now=now)
    due: list[dict[str, Any]] = []
    for horizon, cards in books["books"].items():
        for card in cards:
            attention = str(card.get("attention") or "none")
            if attention == "none":
                continue
            due.append(
                {
                    "entry_id": card["entry_id"],
                    "horizon": horizon,
                    "target": card["plan"]["target"],
                    "state": card["plan"]["state"],
                    "attention": attention,
                    "review_at": card["plan"]["review_at"],
                    "time_stop_at": card["plan"].get("time_stop_at"),
                }
            )
    due.sort(
        key=lambda item: (
            item["attention"] != "time_stop_due",
            str(item["review_at"]),
            str(item["entry_id"]),
        )
    )
    return {
        "schema_version": "market-desk-review-queue.v1",
        "as_of": books["as_of"],
        "ledger_path": books["ledger_path"],
        "due_count": len(due),
        "time_stop_due_count": sum(
            item["attention"] == "time_stop_due" for item in due
        ),
        "review_due_count": sum(item["attention"] == "review_due" for item in due),
        "due": due,
        "research_only": True,
        "no_order_execution": True,
        "warnings": [
            "This queue does not extend reviews, change plan state, approve candidates, or execute orders.",
            "Every due item requires an explicit evidence-bound lifecycle review.",
        ],
    }


def get_market_desk_postmortem_queue(
    *,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """List evidence-backed underperformance reviews that need a postmortem.

    The queue is deliberately read-only.  It neither guesses a root cause nor
    records a postmortem automatically.  A resolving postmortem must be
    recorded after the review and explicitly name that review's frozen archive
    anchor in ``evidence.review_anchor`` (or ``evidence.evidence_refs``).
    """
    resolved_path = _resolve_research_ledger_path(ledger_path)
    due: list[dict[str, Any]] = []
    reviewed_count = 0
    evidence_repair_count = 0
    for entry in ResearchLedger(resolved_path).list_entries(limit=10_000):
        for position, observation in enumerate(entry.observations):
            review = observation.evidence.get("paper_decision_review")
            if not isinstance(review, Mapping):
                continue
            if str(review.get("outcome") or "") != "underperformed":
                continue
            reviewed_count += 1
            return_evidence = review.get("return_evidence")
            archive_id = (
                str(return_evidence.get("archive_id") or "").strip()
                if isinstance(return_evidence, Mapping)
                else ""
            )
            evidence_status = str(review.get("evidence_status") or "blocked")
            if evidence_status not in {"pass", "public_frozen"} or not archive_id:
                evidence_repair_count += 1
                due.append(
                    {
                        "entry_id": entry.entry_id,
                        "target": entry.targets[0] if entry.targets else "",
                        "attention": "review_evidence_repair_required",
                        "review_observed_at": observation.observed_at.isoformat(),
                        "evidence_status": evidence_status,
                        "required_review_anchor": None,
                    }
                )
                continue
            review_anchor = f"paper-review:{archive_id}"
            if _has_postmortem_review_anchor(entry.observations[position + 1 :], review_anchor):
                continue
            due.append(
                {
                    "entry_id": entry.entry_id,
                    "target": entry.targets[0] if entry.targets else "",
                    "attention": "postmortem_required",
                    "review_observed_at": observation.observed_at.isoformat(),
                    "evidence_status": evidence_status,
                    "required_review_anchor": review_anchor,
                    "active_return": review.get("active_return"),
                    "benchmark_id": review.get("benchmark_id"),
                }
            )
    due.sort(key=lambda item: (str(item["review_observed_at"]), str(item["entry_id"])))
    return {
        "schema_version": "market-desk-postmortem-queue.v1",
        "ledger_path": str(resolved_path),
        "underperformance_review_count": reviewed_count,
        "due_count": len(due),
        "postmortem_required_count": sum(
            item["attention"] == "postmortem_required" for item in due
        ),
        "review_evidence_repair_count": evidence_repair_count,
        "due": due,
        "research_only": True,
        "no_order_execution": True,
        "warnings": [
            "This queue creates no postmortem and changes no lifecycle state.",
            "A postmortem must state a human-reviewed root cause and explicitly anchor the relevant frozen paper-review evidence.",
        ],
    }


def _has_postmortem_review_anchor(
    observations: Sequence[ResearchObservation], review_anchor: str
) -> bool:
    """Return whether a later postmortem explicitly binds this review."""
    for observation in observations:
        postmortem = observation.evidence.get("postmortem")
        if not isinstance(postmortem, Mapping):
            continue
        evidence = postmortem.get("evidence")
        if not isinstance(evidence, Mapping):
            continue
        raw_refs = evidence.get("evidence_refs")
        extra_anchors = (
            {
                str(value).strip()
                for value in raw_refs
                if str(value).strip()
            }
            if isinstance(raw_refs, Sequence)
            and not isinstance(raw_refs, (str, bytes, bytearray))
            else set()
        )
        anchors = {str(evidence.get("review_anchor") or "").strip(), *extra_anchors}
        if review_anchor in anchors:
            return True
    return False


def get_market_desk_discovery_research_queue(
    *,
    ledger_path: Optional[Path] = None,
    now: Optional[datetime] = None,
    review_sla_hours: int = 48,
) -> dict[str, Any]:
    """List overdue or integrity-failed public-discovery research entries.

    A public discovery promotion is only an observation handoff. This queue
    makes the next research review due date and archive integrity explicit; it
    never changes a ledger entry, promotes a candidate, or opens a paper plan.
    """
    if review_sla_hours < 1 or review_sla_hours > 24 * 30:
        raise ValueError("review_sla_hours must be between 1 and 720")
    resolved_path = _resolve_research_ledger_path(ledger_path)
    reference_time = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    due: list[dict[str, Any]] = []
    monitored_count = 0
    for entry in ResearchLedger(resolved_path).list_entries(limit=10_000):
        if entry.target_type != "public_discovery_observation":
            continue
        if entry.status not in {ResearchStatus.MONITORING, ResearchStatus.ACTIVE}:
            continue
        monitored_count += 1
        discovery_metadata = entry.metadata.get("public_discovery")
        archive_path = (
            discovery_metadata.get("source_archive_path")
            if isinstance(discovery_metadata, Mapping)
            else None
        )
        assurance = verify_public_market_discovery_archive(str(archive_path or ""))
        created_at = entry.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        else:
            created_at = created_at.astimezone(timezone.utc)
        review_due_at = created_at + timedelta(hours=review_sla_hours)
        latest_triage = next(
            (
                observation
                for observation in reversed(entry.observations)
                if observation.observation_type == "discovery_triage"
            ),
            None,
        )
        reviewed = latest_triage is not None or any(
            observation.observation_type == "discovery_research_review"
            for observation in entry.observations
        )
        if latest_triage is not None:
            next_review_at = latest_triage.evidence.get("next_review_at")
            if isinstance(next_review_at, str):
                try:
                    parsed_next_review = _parse_datetime(next_review_at, reference_time)
                    review_due_at = (
                        parsed_next_review.replace(tzinfo=timezone.utc)
                        if parsed_next_review.tzinfo is None
                        else parsed_next_review.astimezone(timezone.utc)
                    )
                except ValueError:
                    review_due_at = reference_time
        attention = (
            "source_integrity_failed"
            if assurance.get("status") != "pass"
            else "research_review_due"
            if not reviewed and reference_time >= review_due_at
            else "none"
        )
        if attention == "none":
            continue
        due.append(
            {
                "entry_id": entry.entry_id,
                "target": entry.targets[0] if entry.targets else None,
                "title": entry.title,
                "ledger_status": entry.status.value,
                "attention": attention,
                "created_at": created_at.isoformat(),
                "review_due_at": review_due_at.isoformat(),
                "source_archive_path": str(archive_path or ""),
                "source_archive_assurance": assurance,
                "reviewed": reviewed,
            }
        )
    due.sort(
        key=lambda item: (
            item["attention"] != "source_integrity_failed",
            str(item["review_due_at"]),
            str(item["entry_id"]),
        )
    )
    return {
        "schema_version": "market-desk-discovery-research-queue.v1",
        "as_of": reference_time.isoformat(),
        "ledger_path": str(resolved_path),
        "review_sla_hours": review_sla_hours,
        "monitored_count": monitored_count,
        "due_count": len(due),
        "source_integrity_failed_count": sum(
            item["attention"] == "source_integrity_failed" for item in due
        ),
        "research_review_due_count": sum(
            item["attention"] == "research_review_due" for item in due
        ),
        "due": due,
        "research_only": True,
        "no_order_execution": True,
        "warnings": [
            "A due review requires explicit source-backed research evidence or an invalidation/closure observation.",
            "This queue never changes lifecycle state, promotes a candidate, creates a strategy plan, or executes an order.",
        ],
    }


def record_market_desk_discovery_triage(
    entry_id: str,
    *,
    action: str,
    reviewer: str,
    reason: str,
    evidence_refs: Sequence[str],
    next_review_at: Optional[str | datetime] = None,
    reviewed_at: Optional[str | datetime] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Append an evidence-bound triage review to a public discovery entry.

    Triage is intentionally a research-lifecycle operation: it can continue
    monitoring on a bounded next review, invalidate the observation, or close
    it. It cannot create a candidate gate, strategy plan, paper position, or
    order instruction.
    """
    normalized_action = str(action).strip().lower()
    if normalized_action not in {"continue_research", "invalidate", "close"}:
        raise ValueError("action must be continue_research, invalidate, or close")
    normalized_reviewer = str(reviewer).strip()
    normalized_reason = str(reason).strip()
    normalized_refs = [str(reference).strip() for reference in evidence_refs if str(reference).strip()]
    if not normalized_reviewer or not normalized_reason or not normalized_refs:
        raise ValueError("triage requires reviewer, reason, and at least one evidence reference")
    reference_time = _parse_datetime(reviewed_at, datetime.now(timezone.utc))
    if reference_time.tzinfo is None:
        raise ValueError("reviewed_at must include a timezone")
    reference_time = reference_time.astimezone(timezone.utc)
    parsed_next_review: Optional[datetime] = None
    if normalized_action == "continue_research":
        if next_review_at is None:
            raise ValueError("continue_research requires next_review_at")
        parsed_next_review = _parse_datetime(next_review_at, reference_time)
        if parsed_next_review.tzinfo is None:
            raise ValueError("next_review_at must include a timezone")
        parsed_next_review = parsed_next_review.astimezone(timezone.utc)
        if parsed_next_review <= reference_time:
            raise ValueError("next_review_at must be later than reviewed_at")
        if parsed_next_review > reference_time + timedelta(days=30):
            raise ValueError("next_review_at must be within 30 days of reviewed_at")
    elif next_review_at is not None:
        raise ValueError("terminal triage actions must not set next_review_at")

    resolved_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_path)
    entry = ledger.get(entry_id)
    if entry is None:
        raise ValueError("research entry was not found")
    if entry.target_type != "public_discovery_observation":
        raise ValueError("triage only applies to public_discovery_observation entries")
    if entry.status not in {ResearchStatus.MONITORING, ResearchStatus.ACTIVE}:
        raise ValueError("triage requires an active or monitoring discovery entry")
    discovery_metadata = entry.metadata.get("public_discovery")
    archive_path = (
        discovery_metadata.get("source_archive_path")
        if isinstance(discovery_metadata, Mapping)
        else None
    )
    assurance = verify_public_market_discovery_archive(str(archive_path or ""))
    if normalized_action == "continue_research" and assurance.get("status") != "pass":
        failures = assurance.get("failures")
        detail = "; ".join(str(item) for item in failures) if isinstance(failures, Sequence) else "unknown archive failure"
        raise ValueError(f"continue_research requires a verified discovery archive: {detail}")

    status_after = (
        ResearchStatus.INVALIDATED
        if normalized_action == "invalidate"
        else ResearchStatus.CLOSED
        if normalized_action == "close"
        else None
    )
    observation = ResearchObservation(
        observation_type="discovery_triage",
        note=normalized_reason,
        observed_at=reference_time,
        evidence={
            "action": normalized_action,
            "reviewer": normalized_reviewer,
            "evidence_refs": normalized_refs,
            "next_review_at": parsed_next_review.isoformat() if parsed_next_review else None,
            "source_archive_path": str(archive_path or ""),
            "source_archive_assurance": assurance,
        },
        status_after=status_after,
    )
    updated = ledger.record_observation(entry_id, observation)
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "entry": updated.to_dict(),
        "triage_action": normalized_action,
        "source_archive_assurance": assurance,
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
    }


def assess_market_desk_operational_readiness(
    *,
    user_id: str = "default",
    ledger_path: Optional[Path] = None,
    restricted_list_path: Optional[Path] = None,
    observation_archive_directory: Optional[str | Path] = None,
    portfolio_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Audit the observation, governed-public-paper, and formal paper lanes.

    A public observation desk may be operational without licensed historical
    data. A governed public-paper entry still needs a current, independently
    verifiable restricted-list authority. Formal candidate publication and
    reproducible post-trade review are deliberately reported separately so
    neither is implied by observation readiness.
    """
    user_config = load_user_config(user_id)
    market_data_mode = str(user_config.get("market_data_mode") or "public_observation")
    public_observation_mode = market_data_mode == "public_observation"
    source_governance = list_market_data_source_governance()
    sources = source_governance["sources"]
    observation_sources = [
        item["source_id"]
        for item in sources
        if not item["credential_required"] and not item["decision_eligible"]
    ]
    configured_decision_sources = [
        item["source_id"]
        for item in sources
        if item["decision_eligible"] and item["configured"]
    ]
    formal_eod_sources = [
        item["source_id"]
        for item in sources
        if (
            item["decision_eligible"]
            and item["configured"]
            and {"trading_calendar", "eod_bars"}.issubset(set(item["domains"]))
        )
    ]
    data_owner_configured = bool(os.environ.get("MARKET_DATA_ATTESTED_BY", "").strip())
    restricted_health = RestrictedListStore(
        restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH
    ).health()
    observation_history = list_public_desk_observation_runs(
        observation_archive_directory
        or PROJECT_ROOT / "data" / "market-desk-observation-runs"
    )
    resolved_ledger_path = _resolve_research_ledger_path(ledger_path)
    resolved_portfolio_path = portfolio_path or DEFAULT_PORTFOLIO_PATH
    portfolio_governance = _audit_market_desk_portfolio_governance(
        portfolio_path=resolved_portfolio_path,
        ledger_path=resolved_ledger_path,
    )
    postmortem_queue = get_market_desk_postmortem_queue(
        ledger_path=resolved_ledger_path
    )
    entries = ResearchLedger(resolved_ledger_path).list_entries(limit=10_000)
    strategy_entries = 0
    active_strategy_entries = 0
    quality_feedback_entry_ids: set[str] = set()
    invalid_quality_feedback_entry_ids: set[str] = set()
    review_counts = {"pass": 0, "public_frozen": 0, "blocked": 0, "other": 0}
    for entry in entries:
        for position, observation in enumerate(entry.observations):
            if observation.observation_type != "quality_feedback":
                continue
            feedback = observation.evidence.get("quality_feedback")
            if _quality_feedback_is_anchored(
                feedback,
                _quality_feedback_evidence_anchors(entry.observations[:position]),
            ):
                quality_feedback_entry_ids.add(str(entry.entry_id))
            else:
                invalid_quality_feedback_entry_ids.add(str(entry.entry_id))
        if entry.target_type != "strategy_plan":
            continue
        strategy_entries += 1
        if entry.status == ResearchStatus.ACTIVE:
            active_strategy_entries += 1
        for observation in entry.observations:
            review = observation.evidence.get("paper_decision_review")
            if not isinstance(review, Mapping):
                continue
            evidence_status = str(review.get("evidence_status") or "other")
            if evidence_status in review_counts:
                review_counts[evidence_status] += 1
            else:
                review_counts["other"] += 1

    formal_data_ready = bool(formal_eod_sources) and data_owner_configured
    compliance_ready = (
        str(restricted_health.get("status") or "") == "current"
        and str(restricted_health.get("signature_status") or "") == "verified"
    )
    observation_history_status = (
        "warning"
        if observation_history["invalid_count"]
        or observation_history["unresolved_valid_duplicate_run_dates"]
        else "pass"
        if observation_history["valid_count"]
        else "not_ready"
    )
    checks = {
        "observation_data": {
            "status": "pass" if observation_sources else "blocked",
            "sources": observation_sources,
            "message": "Public source-labelled data supports observation-only technical actions.",
        },
        "observation_history": {
            "status": observation_history_status,
            "run_count": observation_history["run_count"],
            "valid_count": observation_history["valid_count"],
            "invalid_count": observation_history["invalid_count"],
            "latest_valid_observed_at": observation_history["latest_valid_observed_at"],
            "eod_valid_count": observation_history["eod_valid_count"],
            "latest_valid_eod_observed_at": observation_history["latest_valid_eod_observed_at"],
            "duplicate_run_dates": observation_history["duplicate_run_dates"],
            "resolved_duplicate_run_dates": observation_history["resolved_duplicate_run_dates"],
            "unresolved_valid_duplicate_run_dates": observation_history["unresolved_valid_duplicate_run_dates"],
            "message": (
                "Immutable public observation history is internally verified."
                if observation_history_status == "pass"
                else "No verified public observation run exists yet."
                if observation_history_status == "not_ready"
                else "Observation history has invalid or duplicate records; retain evidence and resolve the operating exception."
            ),
        },
        "formal_decision_data": {
            "status": "not_enabled" if public_observation_mode else "pass" if formal_data_ready else "blocked",
            "configured_decision_sources": configured_decision_sources,
            "configured_eod_sources": formal_eod_sources,
            "data_owner_attestation_configured": data_owner_configured,
            "message": (
                "The user profile explicitly selects public-observation research; licensed EOD release is not enabled."
                if public_observation_mode
                else "An authorized decision-capable EOD source and accountable data owner are configured."
                if formal_data_ready
                else "Formal decisions require an authorized source with both EOD-bar and trading-calendar coverage, plus a data-owner attestation."
            ),
        },
        "compliance_authority": {
            "status": "pass" if compliance_ready else "blocked",
            "restricted_list_health": restricted_health,
            "message": (
                "Restricted-list authority is current and signature-verified."
                if compliance_ready
                else "A governed paper entry requires a current, signature-verified restricted-list authority; observation-only research remains available."
            ),
        },
        "reproducible_reviews": {
            "status": "pass" if review_counts["pass"] else "not_ready",
            "counts": review_counts,
            "message": "Only formal reviews with verified frozen return archives count as reproducible performance evidence; public_frozen reviews remain research-only audit evidence.",
        },
        "quality_feedback": {
            "status": (
                "warning"
                if invalid_quality_feedback_entry_ids
                else "pass"
                if quality_feedback_entry_ids
                else "not_ready"
            ),
            "assessed_entry_count": len(quality_feedback_entry_ids),
            "invalid_entry_count": len(invalid_quality_feedback_entry_ids),
            "invalid_entry_ids": sorted(invalid_quality_feedback_entry_ids),
            "message": (
                "Research quality assessments are linked to their underlying ledger entries."
                if quality_feedback_entry_ids and not invalid_quality_feedback_entry_ids
                else "One or more quality assessments lacks a prior, persisted review or postmortem anchor."
                if invalid_quality_feedback_entry_ids
                else "No evidence-bound research quality feedback has been recorded yet."
            ),
        },
        "postmortem_control": {
            "status": (
                "warning"
                if postmortem_queue["due_count"]
                else "pass"
                if postmortem_queue["underperformance_review_count"]
                else "not_ready"
            ),
            "underperformance_review_count": postmortem_queue[
                "underperformance_review_count"
            ],
            "due_count": postmortem_queue["due_count"],
            "postmortem_required_count": postmortem_queue[
                "postmortem_required_count"
            ],
            "review_evidence_repair_count": postmortem_queue[
                "review_evidence_repair_count"
            ],
            "message": (
                "Every evidence-backed underperformance review has a later explicitly anchored postmortem."
                if postmortem_queue["underperformance_review_count"]
                and not postmortem_queue["due_count"]
                else "One or more underperformance reviews needs evidence repair or an explicitly anchored postmortem."
                if postmortem_queue["due_count"]
                else "No underperformance review has been observed yet; postmortem control has no operational sample."
            ),
        },
        "paper_portfolio_governance": {
            "status": (
                "blocked"
                if portfolio_governance["governance_status"] == "blocked"
                else "pass"
            ),
            "portfolio_path": str(resolved_portfolio_path),
            "position_count": portfolio_governance.get("position_count"),
            "governed_count": portfolio_governance.get("governed_count", 0),
            "unlinked_legacy_count": portfolio_governance.get("unlinked_legacy_count", 0),
            "invalid_link_count": portfolio_governance.get("invalid_link_count", 0),
            "entry_evidence_gap_count": portfolio_governance.get("entry_evidence_gap_count", 0),
            "exit_review_required_count": portfolio_governance.get("exit_review_required_count", 0),
            "message": (
                "Open paper positions and recorded exits satisfy the strategy-link, evidence, and lifecycle-review controls."
                if portfolio_governance["governance_status"] == "pass"
                else "No open paper position or governed exit is awaiting portfolio-governance review."
                if portfolio_governance["governance_status"] == "not_ready"
                else portfolio_governance.get("error")
                or "Paper portfolio contains unlinked, invalid, evidence-gap, or unreviewed-exit records."
            ),
        },
    }
    formal_ready = (
        formal_data_ready
        and compliance_ready
        and checks["paper_portfolio_governance"]["status"] == "pass"
    )
    public_paper_entry_ready = (
        checks["observation_data"]["status"] == "pass"
        and compliance_ready
        and checks["paper_portfolio_governance"]["status"] == "pass"
    )
    return {
        "schema_version": "market-desk-operational-readiness.v1",
        "market_data_mode": market_data_mode,
        "observation_desk_status": "ready" if checks["observation_data"]["status"] == "pass" else "blocked",
        "public_paper_desk_status": "ready" if public_paper_entry_ready else "blocked",
        "public_paper_entry_status": "ready" if public_paper_entry_ready else "blocked",
        "formal_paper_desk_status": "not_enabled" if public_observation_mode else "ready" if formal_ready else "blocked",
        "checks": checks,
        "strategy_entry_count": strategy_entries,
        "active_strategy_entry_count": active_strategy_entries,
        "ledger_path": str(resolved_ledger_path),
        "portfolio_path": str(resolved_portfolio_path),
        "research_only": True,
        "no_order_execution": True,
    }


def assess_market_desk_operating_maturity(
    *,
    user_id: str = "default",
    ledger_path: Optional[Path] = None,
    restricted_list_path: Optional[Path] = None,
    observation_archive_directory: Optional[str | Path] = None,
    discovery_archive_directory: Optional[str | Path] = None,
    portfolio_path: Optional[Path] = None,
    scheduler_status: Optional[Mapping[str, Any]] = None,
) -> dict[str, Any]:
    """Assess whether the public market desk has operating evidence, not just code.

    This is deliberately stricter than readiness.  A control can be correctly
    implemented yet remain ``evidence_pending`` until immutable public
    archives, lifecycle reviews, and feedback/postmortem records demonstrate
    that it has been exercised.  It does not enable formal release or order
    execution in public-observation mode.
    """
    readiness = assess_market_desk_operational_readiness(
        user_id=user_id,
        ledger_path=ledger_path,
        restricted_list_path=restricted_list_path,
        observation_archive_directory=observation_archive_directory,
        portfolio_path=portfolio_path,
    )
    resolved_ledger_path = _resolve_research_ledger_path(ledger_path)
    discovery_history = get_public_market_desk_discovery_history(
        archive_directory=discovery_archive_directory
        or PROJECT_ROOT / "data" / "market-desk-discovery-archives"
    )
    books = get_market_desk_strategy_books(ledger_path=resolved_ledger_path)
    review_queue = get_market_desk_review_queue(ledger_path=resolved_ledger_path)
    postmortem_queue = get_market_desk_postmortem_queue(ledger_path=resolved_ledger_path)
    runtime = dict(scheduler_status or get_scheduler_status())
    readiness_checks = readiness["checks"]
    review_counts = dict(readiness_checks["reproducible_reviews"]["counts"])
    public_review_count = int(review_counts.get("public_frozen") or 0)
    formal_review_count = int(review_counts.get("pass") or 0)
    exercised_review_count = public_review_count + formal_review_count
    strategy_count = sum(int(value) for value in books["book_counts"].values())
    scheduler_running = runtime.get("running") is True
    eod_readiness_dependency_blockers = (
        runtime.get("jobs", {})
        .get("audit_market_desk_operational_readiness", {})
        .get("dependency_blockers", [])
    )
    eod_control_status = (
        "blocked"
        if not scheduler_running
        else "evidence_pending"
        if eod_readiness_dependency_blockers
        else "operational"
    )
    requirements = {
        "whole_market_observation": {
            "status": (
                "operational"
                if readiness_checks["observation_history"]["status"] == "pass"
                and int(readiness_checks["observation_history"].get("eod_valid_count") or 0) > 0
                else "blocked"
                if readiness_checks["observation_history"]["status"] == "warning"
                else "evidence_pending"
            ),
            "evidence": {
                "valid_archive_count": readiness_checks["observation_history"]["valid_count"],
                "latest_valid_observed_at": readiness_checks["observation_history"]["latest_valid_observed_at"],
                "eod_valid_archive_count": readiness_checks["observation_history"].get("eod_valid_count", 0),
                "latest_valid_eod_observed_at": readiness_checks["observation_history"].get("latest_valid_eod_observed_at"),
            },
            "message": "Whole-market public observation requires immutable, integrity-checked EOD archives.",
        },
        "whole_market_discovery": {
            "status": (
                "operational"
                if int(discovery_history.get("usable_eod_valid_count") or 0) > 0
                and int(discovery_history.get("invalid_count") or 0) == 0
                and not discovery_history.get("usable_eod_duplicate_run_dates")
                else "blocked"
                if int(discovery_history.get("invalid_count") or 0) > 0
                or discovery_history.get("usable_eod_duplicate_run_dates")
                else "evidence_pending"
            ),
            "evidence": {
                "valid_archive_count": discovery_history.get("valid_count", 0),
                "eod_valid_archive_count": discovery_history.get("eod_valid_count", 0),
                "invalid_archive_count": discovery_history.get("invalid_count", 0),
                "latest_valid_observed_at": discovery_history.get("latest_valid_observed_at"),
                "latest_valid_eod_observed_at": discovery_history.get("latest_valid_eod_observed_at"),
                "usable_eod_valid_archive_count": discovery_history.get("usable_eod_valid_count", 0),
                "latest_usable_eod_observed_at": discovery_history.get("latest_usable_eod_observed_at"),
                "usable_eod_duplicate_run_dates": discovery_history.get("usable_eod_duplicate_run_dates", []),
                "archive_directory": discovery_history.get("archive_directory"),
            },
            "message": "Whole-market discovery requires one verified EOD archive with an actual usable public cross-section; a duplicate usable EOD run is an operating exception. Discovery archives create research leads only, never candidates, recommendations, or orders.",
        },
        "strategy_lifecycle": {
            "status": "operational" if strategy_count and not review_queue["due_count"] else "blocked" if review_queue["due_count"] else "evidence_pending",
            "evidence": {
                "strategy_plan_count": strategy_count,
                "active_strategy_plan_count": readiness["active_strategy_entry_count"],
                "book_counts": books["book_counts"],
                "review_due_count": review_queue["due_count"],
            },
            "message": "A strategy lifecycle is evidenced only after persisted plans are reviewed on time; any public-mode active plan remains research-only and still requires a signed compliance authority.",
        },
        "paper_portfolio_risk_control": {
            "status": (
                "operational"
                if readiness_checks["paper_portfolio_governance"]["status"] == "pass"
                and (
                    int(readiness_checks["paper_portfolio_governance"]["position_count"] or 0) > 0
                    or int(readiness_checks["paper_portfolio_governance"]["governed_count"] or 0) > 0
                )
                else "evidence_pending"
                if readiness_checks["paper_portfolio_governance"]["status"] == "pass"
                else "blocked"
            ),
            "evidence": {
                "position_count": readiness_checks["paper_portfolio_governance"]["position_count"],
                "governed_count": readiness_checks["paper_portfolio_governance"]["governed_count"],
                "exit_review_required_count": readiness_checks["paper_portfolio_governance"]["exit_review_required_count"],
            },
            "message": "The control is operational only after it has governed at least one paper position; an empty portfolio leaves the control available but unexercised.",
        },
        "frozen_return_review": {
            "status": "operational" if exercised_review_count else "evidence_pending",
            "evidence": {
                "public_frozen_review_count": public_review_count,
                "formal_frozen_review_count": formal_review_count,
            },
            "message": "Public-frozen reviews are research-only evidence. Formal performance publication remains unavailable without a licensed EOD lane.",
        },
        "feedback_and_postmortem": {
            "status": (
                "blocked"
                if postmortem_queue["due_count"]
                else "operational"
                if readiness_checks["quality_feedback"]["status"] == "pass"
                and readiness_checks["postmortem_control"]["status"] == "pass"
                and int(postmortem_queue["underperformance_review_count"] or 0) > 0
                else "evidence_pending"
            ),
            "evidence": {
                "quality_feedback_entry_count": readiness_checks["quality_feedback"]["assessed_entry_count"],
                "underperformance_review_count": postmortem_queue["underperformance_review_count"],
                "postmortem_due_count": postmortem_queue["due_count"],
            },
            "message": "A postmortem control is not proven until a frozen underperformance review and an anchored feedback/postmortem loop exist.",
        },
        "runtime_and_eod_controls": {
            "status": eod_control_status,
            "evidence": {
                "runtime": runtime.get("runtime", {}),
                "eod_readiness_dependency_blockers": eod_readiness_dependency_blockers,
            },
            "message": (
                "The runtime is live, but the current session's ordered EOD dependency chain has not completed."
                if eod_control_status == "evidence_pending"
                else "The scheduler is not running, so EOD controls cannot be relied upon."
                if eod_control_status == "blocked"
                else "The live scheduler completed the current session's ordered EOD dependency chain."
            ),
        },
        "formal_release_boundary": {
            "status": "not_enabled" if readiness["market_data_mode"] == "public_observation" else readiness["formal_paper_desk_status"],
            "evidence": {
                "market_data_mode": readiness["market_data_mode"],
                "formal_paper_desk_status": readiness["formal_paper_desk_status"],
            },
            "message": "Public-observation mode intentionally excludes licensed-data formal releases and all order execution.",
        },
    }
    material_statuses = [
        item["status"]
        for name, item in requirements.items()
        if name != "formal_release_boundary"
    ]
    maturity_status = (
        "blocked"
        if "blocked" in material_statuses
        else "operating_proof_established"
        if all(status == "operational" for status in material_statuses)
        else "evidence_accumulating"
    )
    return {
        "schema_version": "market-desk-operating-maturity.v1",
        "maturity_status": maturity_status,
        "market_data_mode": readiness["market_data_mode"],
        "requirements": requirements,
        "readiness": readiness,
        "research_only": True,
        "formal_decision_eligible": False,
        "no_order_execution": True,
        "warnings": [
            "This audit reports operating evidence; it does not infer skill quality from a ready control or a small sample.",
            "No paid data source, terminal credential, broker integration, or order-routing capability is required or enabled for this public-observation desk.",
        ],
    }


def _market_desk_timestamp_due(value: str, reference_time: datetime) -> bool:
    timestamp = _parse_datetime(value, reference_time)
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    return timestamp.astimezone(timezone.utc) <= reference_time


def _audit_market_desk_portfolio_governance(
    *, portfolio_path: Path, ledger_path: Path
) -> dict[str, Any]:
    """Load and audit the live paper portfolio for desk release controls."""
    try:
        if portfolio_path.exists():
            raw_portfolio = json.loads(portfolio_path.read_text(encoding="utf-8"))
            if not isinstance(raw_portfolio, Mapping):
                raise ValueError("portfolio root must be a JSON object")
            return audit_paper_portfolio_governance(raw_portfolio, ledger_path=ledger_path)
        return audit_paper_portfolio_governance(
            {"positions": {}, "trades": []}, ledger_path=ledger_path
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        return {
            "governance_status": "blocked",
            "position_count": None,
            "governed_count": 0,
            "unlinked_legacy_count": 0,
            "invalid_link_count": 0,
            "entry_evidence_gap_count": 0,
            "exit_review_required_count": 0,
            "error": f"Portfolio governance input cannot be audited: {error}",
        }


def transition_market_desk_strategy_plan(
    entry_id: str,
    *,
    next_state: str,
    reason: str,
    observed_at: Optional[str | datetime] = None,
    ic_decision: Optional[Mapping[str, Any]] = None,
    release_inputs: Optional[Mapping[str, Any]] = None,
    restricted_list_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
    portfolio_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Advance a persisted strategy plan through its auditable lifecycle."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_path)
    entry = ledger.get(entry_id)
    if entry is None:
        raise KeyError(f"Research entry not found: {entry_id}")
    plan_payload = entry.metadata.get("strategy_plan")
    for observation in reversed(entry.observations):
        candidate = observation.evidence.get("strategy_plan")
        if isinstance(candidate, Mapping):
            plan_payload = candidate
            break
    if not isinstance(plan_payload, Mapping):
        raise ValueError("research entry has no market-desk strategy plan")
    current_plan = StrategyPlan.from_dict(plan_payload)
    desired_state = StrategyState(next_state)
    release_assurance: Optional[dict[str, Any]] = None
    frozen_release_package: Optional[dict[str, Any]] = None
    if desired_state == StrategyState.ACTIVE:
        _validate_active_ic_before_release(current_plan, ic_decision)
        if not isinstance(release_inputs, Mapping):
            raise ValueError("active strategy plans require authoritative release_inputs")
        portfolio_governance = _audit_market_desk_portfolio_governance(
            portfolio_path=portfolio_path or DEFAULT_PORTFOLIO_PATH,
            ledger_path=resolved_path,
        )
        if portfolio_governance["governance_status"] == "blocked":
            raise ValueError(
                "active strategy plan release is blocked by paper-portfolio governance gaps"
            )
        prospective_plan = current_plan.to_dict()
        prospective_plan["state"] = StrategyState.ACTIVE.value
        health = RestrictedListStore(restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH).health()
        candidate_with_compliance = _candidate_with_restricted_list_context(
                _required_release_packet(release_inputs, "candidate"),
                restricted_targets=(),
                restricted_list_path=restricted_list_path,
            )[0]
        frozen_release_package = {
            "schema_version": "market-desk-release-package.v1",
            "snapshot": dict(_required_release_packet(release_inputs, "snapshot")),
            "rotation": dict(_required_release_packet(release_inputs, "rotation")),
            "candidate": candidate_with_compliance,
            "risk_budget": dict(_required_release_packet(release_inputs, "risk_budget")),
            "structural_risk": dict(_required_release_packet(release_inputs, "structural_risk")),
            "restricted_list_health": health,
            "portfolio_governance": portfolio_governance,
            "require_full_rotation": bool(release_inputs.get("require_full_rotation", False)),
        }
        if isinstance(release_inputs.get("decision_review"), Mapping):
            frozen_release_package["decision_review"] = dict(release_inputs["decision_review"])
        frozen_release_package["content_hashes"] = {
            key: _content_hash(value)
            for key, value in frozen_release_package.items()
            if key not in {"schema_version", "content_hashes"}
        }
        frozen_release_package["package_hash"] = _content_hash(
            {key: value for key, value in frozen_release_package.items() if key != "package_hash"}
        )
        report = verify_paper_desk_release(
            snapshot=frozen_release_package["snapshot"],
            rotation=frozen_release_package["rotation"],
            candidate=candidate_with_compliance,
            ic_decision=ic_decision or {},
            strategy_plan=prospective_plan,
            risk_budget=frozen_release_package["risk_budget"],
            structural_risk=frozen_release_package["structural_risk"],
            restricted_list_health=health,
            require_full_rotation=frozen_release_package["require_full_rotation"],
            decision_review=frozen_release_package.get("decision_review"),
        )
        release_assurance = report.to_dict()
        if report.verdict != "pass":
            raise ValueError(f"active strategy plan release assurance failed: {report.blockers[0]}")
    transitioned = transition_strategy_plan(
        current_plan,
        next_state,
        reason=reason,
        observed_at=(
            _parse_datetime(observed_at, datetime.now()).isoformat()
            if observed_at is not None
            else None
        ),
        ic_decision=ic_decision,
        release_assurance=release_assurance,
    )
    status_after = {
        StrategyState.ACTIVE: ResearchStatus.ACTIVE,
        StrategyState.INVALIDATED: ResearchStatus.INVALIDATED,
        StrategyState.CLOSED: ResearchStatus.CLOSED,
        StrategyState.EXPIRED: ResearchStatus.CLOSED,
    }.get(transitioned.state, ResearchStatus.MONITORING)
    observation = ResearchObservation(
        observation_type="strategy_lifecycle_transition",
        note=f"Strategy plan transitioned to {transitioned.state.value}: {reason}",
        observed_at=_parse_datetime(observed_at, datetime.now()),
        evidence={
            "strategy_plan": transitioned.to_dict(),
            "ic_decision": dict(ic_decision) if ic_decision else None,
            "release_assurance": release_assurance,
            "release_package": frozen_release_package,
        },
        status_after=status_after,
    )
    updated = ledger.record_observation(entry_id, observation)
    return {"success": True, "ledger_path": str(resolved_path), "entry": updated.to_dict()}


def record_market_desk_strategy_review(
    entry_id: str,
    *,
    reviewer: str,
    reason: str,
    evidence_refs: Sequence[str],
    next_review_at: str,
    observed_at: Optional[str | datetime] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Persist an evidence-bound continuation review for a paper strategy.

    This records why a nonterminal paper plan remains under research and when
    it must next be reviewed. It cannot activate a plan, reset a due time stop,
    place an order, or bypass the release assurance path.
    """
    resolved_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_path)
    entry = ledger.get(entry_id)
    if entry is None:
        raise KeyError(f"Research entry not found: {entry_id}")
    plan_payload: Any = entry.metadata.get("strategy_plan")
    for observation in reversed(entry.observations):
        candidate = observation.evidence.get("strategy_plan")
        if isinstance(candidate, Mapping):
            plan_payload = candidate
            break
    if not isinstance(plan_payload, Mapping):
        raise ValueError("research entry has no market-desk strategy plan")
    plan = StrategyPlan.from_dict(plan_payload)
    review_timestamp = _parse_datetime(observed_at, datetime.now())
    reviewed = record_strategy_plan_review(
        plan,
        reviewer=reviewer,
        reason=reason,
        evidence_refs=evidence_refs,
        next_review_at=next_review_at,
        observed_at=review_timestamp.isoformat(),
    )
    observation = ResearchObservation(
        observation_type="strategy_lifecycle_review",
        note=f"Strategy plan continuation review by {reviewer}: {reason}",
        observed_at=review_timestamp,
        evidence={
            "strategy_plan": reviewed.to_dict(),
            "reviewer": reviewer,
            "evidence_refs": list(evidence_refs),
            "research_only": True,
            "no_order_execution": True,
        },
    )
    updated = ledger.record_observation(entry_id, observation)
    return {"success": True, "ledger_path": str(resolved_path), "entry": updated.to_dict()}


def _required_release_packet(release_inputs: Mapping[str, Any], name: str) -> Mapping[str, Any]:
    packet = release_inputs.get(name)
    if not isinstance(packet, Mapping):
        raise ValueError(f"active strategy plans require release_inputs.{name}")
    return packet


def _content_hash(value: Any) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _validate_active_ic_before_release(plan: StrategyPlan, decision: Optional[Mapping[str, Any]]) -> None:
    """Fail missing or malformed IC evidence before inspecting release attachments."""
    if not isinstance(decision, Mapping):
        raise ValueError("active strategy plans require an IC decision record")
    if str(decision.get("candidate_id") or "") != plan.plan_id:
        raise ValueError("active strategy plans require an IC decision bound to the strategy plan")


def record_market_desk_paper_decision_review(
    entry_id: str,
    *,
    ic_decision: Mapping[str, Any],
    evaluation_start: str,
    evaluation_end: str,
    benchmark_id: str,
    gross_paper_return: float,
    implementation_cost_return: float,
    benchmark_return: float,
    return_evidence: Optional[Mapping[str, Any]] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Persist a benchmarked, version-bound paper-decision review on its plan."""
    resolved_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_path)
    entry = ledger.get(entry_id)
    if entry is None:
        raise KeyError(f"Research entry not found: {entry_id}")
    plan_payload = entry.metadata.get("strategy_plan")
    for observation in reversed(entry.observations):
        candidate = observation.evidence.get("strategy_plan")
        if isinstance(candidate, Mapping):
            plan_payload = candidate
            break
    if not isinstance(plan_payload, Mapping):
        raise ValueError("research entry has no market-desk strategy plan")
    review = review_paper_decision(
        entry_id=entry_id,
        strategy_plan=plan_payload,
        ic_decision=ic_decision,
        evaluation_start=evaluation_start,
        evaluation_end=evaluation_end,
        benchmark_id=benchmark_id,
        gross_paper_return=gross_paper_return,
        implementation_cost_return=implementation_cost_return,
        benchmark_return=benchmark_return,
        return_evidence=return_evidence,
    )
    observation = ResearchObservation(
        observation_type="paper_decision_review",
        note=(
            f"Paper decision review {review.outcome.value}: "
            f"active_return={review.active_return:+.2%} vs {review.benchmark_id}."
        ),
        observed_at=datetime.fromisoformat(review.evaluation_end),
        evidence={"paper_decision_review": review.to_dict(), "ic_decision": dict(ic_decision)},
    )
    updated = ledger.record_observation(entry_id, observation)
    return {
        "success": True,
        "ledger_path": str(resolved_path),
        "review": review.to_dict(),
        "entry": updated.to_dict(),
    }


# ---------------------------------------------------------------------------
# Research Quality Feedback capabilities
# ---------------------------------------------------------------------------


def record_quality_feedback(
    *,
    entry_id: str,
    catalyst_outcomes: Optional[list[dict[str, Any]]] = None,
    risk_outcomes: Optional[list[dict[str, Any]]] = None,
    unpredicted_risks: Optional[list[dict[str, Any]]] = None,
    agent_scores: Optional[list[dict[str, Any]]] = None,
    notes: str = "",
    evidence_refs: Optional[Sequence[str]] = None,
    store_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Record a research quality assessment bound to its research lifecycle."""
    from .quality.feedback import (
        AgentRoleScore,
        CatalystOutcome,
        QualityFeedbackStore,
        ResearchQualityReport,
        RiskOutcome,
    )

    resolved_ledger_path = _resolve_research_ledger_path(ledger_path)
    ledger = ResearchLedger(resolved_ledger_path)
    entry_before_feedback = ledger.get(entry_id)
    if entry_before_feedback is None:
        raise KeyError(f"Research entry not found: {entry_id}")
    normalized_evidence_refs = [
        str(value).strip() for value in (evidence_refs or ()) if str(value).strip()
    ]
    if not normalized_evidence_refs:
        raise ValueError("quality feedback requires at least one evidence reference")
    anchors = _quality_feedback_evidence_anchors(entry_before_feedback.observations)
    if not _quality_feedback_is_anchored(
        {"evidence_refs": normalized_evidence_refs}, anchors
    ):
        raise ValueError(
            "quality feedback requires an evidence reference to a prior persisted "
            "paper review or postmortem on the same research entry"
        )
    report = ResearchQualityReport(
        entry_id=entry_id,
        catalyst_outcomes=[
            CatalystOutcome.from_dict(c) for c in (catalyst_outcomes or [])
        ],
        risk_outcomes=[
            RiskOutcome.from_dict(r) for r in (risk_outcomes or [])
        ],
        unpredicted_risks=[
            RiskOutcome.from_dict(r) for r in (unpredicted_risks or [])
        ],
        agent_scores=[
            AgentRoleScore.from_dict(a) for a in (agent_scores or [])
        ],
        notes=notes,
        evidence_refs=normalized_evidence_refs,
    )
    serialized_report = report.to_dict()
    observation = ResearchObservation(
        observation_type="quality_feedback",
        note=(
            "Research quality feedback recorded"
            + (f": {notes}" if notes else ".")
        ),
        observed_at=_parse_datetime(serialized_report["assessed_at"], datetime.now()),
        evidence={"quality_feedback": serialized_report},
    )
    entry = ledger.record_observation(entry_id, observation)
    store = QualityFeedbackStore(
        store_path or (PROJECT_ROOT / "data" / "quality-feedback.json")
    )
    store.record_quality_report(report)
    return {
        **serialized_report,
        "ledger_path": str(resolved_ledger_path),
        "entry": entry.to_dict(),
    }


def _quality_feedback_evidence_anchors(
    observations: Sequence[ResearchObservation],
) -> set[str]:
    """Return review/postmortem IDs that can support a quality assessment.

    Quality scores must come after an observable outcome.  These anchors make
    the relationship explicit and prevent an arbitrary prose reference from
    making a synthetic feedback sample appear operationally valid.
    """
    anchors: set[str] = set()
    for observation in observations:
        review = observation.evidence.get("paper_decision_review")
        if isinstance(review, Mapping):
            status = str(review.get("evidence_status") or "")
            evidence = review.get("return_evidence")
            archive_id = (
                str(evidence.get("archive_id") or "").strip()
                if isinstance(evidence, Mapping)
                else ""
            )
            if status in {"pass", "public_frozen"} and archive_id:
                anchors.add(f"paper-review:{archive_id}")
        postmortem = observation.evidence.get("postmortem")
        if isinstance(postmortem, Mapping):
            postmortem_id = str(postmortem.get("postmortem_id") or "").strip()
            if postmortem_id:
                anchors.add(f"postmortem:{postmortem_id}")
    return anchors


def _quality_feedback_is_anchored(
    feedback: Any, anchors: set[str]
) -> bool:
    if not isinstance(feedback, Mapping) or not anchors:
        return False
    refs = feedback.get("evidence_refs")
    if not isinstance(refs, Sequence) or isinstance(refs, (str, bytes)):
        return False
    return bool({str(value).strip() for value in refs if str(value).strip()} & anchors)


def get_quality_stats(
    *,
    store_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Get aggregate research quality statistics."""
    from .quality.feedback import QualityFeedbackStore

    store = QualityFeedbackStore(
        store_path or (PROJECT_ROOT / "data" / "quality-feedback.json")
    )
    return store.get_aggregate_stats()


# ---------------------------------------------------------------------------
# Earnings Calendar capabilities
# ---------------------------------------------------------------------------


async def get_earnings_calendar(
    *,
    period: str = "2025年报",
    codes: Optional[list[str]] = None,
    upcoming_only: bool = False,
    days_ahead: int = 30,
) -> dict[str, Any]:
    """Fetch earnings disclosure calendar."""
    from .financial.earnings_calendar import get_earnings_calendar as _get_cal
    return await _get_cal(
        period=period,
        codes=codes,
        upcoming_only=upcoming_only,
        days_ahead=days_ahead,
    )
