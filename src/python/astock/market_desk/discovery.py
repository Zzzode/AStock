"""Public-data, whole-market opportunity discovery for the market desk.

The discovery lane is deliberately upstream of research and portfolio
decisions.  It turns one public A-share spot snapshot into a transparent,
liquid observation pool; it does not manufacture a trading signal, a theme
thesis, or an order-like instruction.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from ..market_data import (
    EASTMONEY_A_SHARE_SPOT_SOURCE,
    fetch_eastmoney_a_share_spot,
    fetch_sina_a_share_spot,
    SINA_A_SHARE_SPOT_SOURCE,
    verify_frozen_market_archive,
)


SCHEMA_VERSION = "market-desk-public-discovery.v1"
SOURCE = EASTMONEY_A_SHARE_SPOT_SOURCE
FALLBACK_SOURCE = SINA_A_SHARE_SPOT_SOURCE
DEFAULT_MIN_AMOUNT = 200_000_000.0
DEFAULT_MIN_CHANGE_PCT = 3.0


def verify_public_market_discovery_archive(path: str | Path) -> dict[str, Any]:
    """Verify a frozen public discovery archive and its research boundary."""
    archive_path = Path(path)
    assurance = verify_frozen_market_archive(
        archive_path, expected_source="akshare_public"
    )
    if assurance.get("status") != "pass":
        return {
            "status": "blocked",
            "archive_path": str(archive_path),
            "failures": list(assurance.get("failures") or ["archive verification failed"]),
        }
    try:
        archive = json.loads(archive_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {
            "status": "blocked",
            "archive_path": str(archive_path),
            "failures": [f"archive cannot be read: {error}"],
        }
    records = archive.get("raw_source_records") if isinstance(archive, Mapping) else None
    discovery = records.get("market_desk_discovery") if isinstance(records, Mapping) else None
    if not isinstance(discovery, Mapping):
        return _blocked_discovery_archive(archive_path, "archive does not contain market_desk_discovery")
    if discovery.get("schema_version") != SCHEMA_VERSION:
        return _blocked_discovery_archive(archive_path, "archive has an unsupported discovery schema")
    if discovery.get("formal_decision_eligible") is not False or discovery.get("research_only") is not True or discovery.get("no_order_execution") is not True:
        return _blocked_discovery_archive(archive_path, "archive does not retain public research-only boundaries")
    observed_at = str(discovery.get("observed_at") or "")
    if not _is_timezone_timestamp(observed_at):
        return _blocked_discovery_archive(archive_path, "archive lacks a timezone-aware observed_at")
    candidates = discovery.get("candidates")
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        return _blocked_discovery_archive(archive_path, "archive candidates must be a list")
    if any(
        not isinstance(candidate, Mapping)
        or candidate.get("formal_decision_eligible") is not False
        or candidate.get("no_order_execution") is not True
        for candidate in candidates
    ):
        return _blocked_discovery_archive(archive_path, "archive candidate boundaries are invalid")
    eod_validation = _validate_eod_discovery_payload(discovery, observed_at)
    return {
        "status": "pass",
        "archive_path": str(archive_path),
        "archive_id": archive.get("archive_id"),
        "observed_at": observed_at,
        "candidate_count": len(candidates),
        "source_assurance": assurance,
        "eod_validation": eod_validation,
        "coverage_validation": _validate_discovery_coverage(discovery),
        "failures": [],
    }


def list_public_market_discovery_archives(directory: str | Path) -> dict[str, Any]:
    """Audit all frozen public discovery archives without changing any state."""
    archive_directory = Path(directory)
    records = [
        verify_public_market_discovery_archive(path)
        for path in sorted(archive_directory.glob("*.json"))
    ] if archive_directory.is_dir() else []
    valid_records = [record for record in records if record.get("status") == "pass"]
    valid_eod_records = [
        record
        for record in valid_records
        if isinstance(record.get("eod_validation"), Mapping)
        and record["eod_validation"].get("status") == "pass"
    ]
    usable_eod_records = [
        record
        for record in valid_eod_records
        if isinstance(record.get("coverage_validation"), Mapping)
        and record["coverage_validation"].get("status") == "pass"
    ]
    daily_counts: dict[str, int] = {}
    for record in valid_records:
        observed_at = str(record.get("observed_at") or "")
        if len(observed_at) >= 10:
            day = observed_at[:10]
            daily_counts[day] = daily_counts.get(day, 0) + 1
    observed = sorted(
        str(record["observed_at"])
        for record in valid_records
        if isinstance(record.get("observed_at"), str)
    )
    eod_observed = sorted(
        str(record["observed_at"])
        for record in valid_eod_records
        if isinstance(record.get("observed_at"), str)
    )
    usable_eod_observed = sorted(
        str(record["observed_at"])
        for record in usable_eod_records
        if isinstance(record.get("observed_at"), str)
    )
    eod_daily_counts: dict[str, int] = {}
    for record in valid_eod_records:
        observed_at = str(record.get("observed_at") or "")
        if len(observed_at) >= 10:
            day = observed_at[:10]
            eod_daily_counts[day] = eod_daily_counts.get(day, 0) + 1
    usable_eod_daily_counts: dict[str, int] = {}
    for record in usable_eod_records:
        observed_at = str(record.get("observed_at") or "")
        if len(observed_at) >= 10:
            day = observed_at[:10]
            usable_eod_daily_counts[day] = usable_eod_daily_counts.get(day, 0) + 1
    return {
        "schema_version": "market-desk-public-discovery-history.v1",
        "archive_directory": str(archive_directory),
        "run_count": len(records),
        "valid_count": len(valid_records),
        "invalid_count": len(records) - len(valid_records),
        "latest_valid_observed_at": observed[-1] if observed else None,
        "eod_valid_count": len(valid_eod_records),
        "latest_valid_eod_observed_at": eod_observed[-1] if eod_observed else None,
        "usable_eod_valid_count": len(usable_eod_records),
        "latest_usable_eod_observed_at": (
            usable_eod_observed[-1] if usable_eod_observed else None
        ),
        "valid_eod_daily_run_counts": eod_daily_counts,
        "usable_eod_daily_run_counts": usable_eod_daily_counts,
        "usable_eod_duplicate_run_dates": sorted(
            day for day, count in usable_eod_daily_counts.items() if count > 1
        ),
        "valid_daily_run_counts": daily_counts,
        "duplicate_run_dates": sorted(day for day, count in daily_counts.items() if count > 1),
        "records": records,
        "research_only": True,
        "no_order_execution": True,
    }


def _validate_eod_discovery_payload(
    discovery: Mapping[str, Any], observed_at: str
) -> dict[str, str]:
    """Classify a valid discovery archive as EOD only with session evidence."""
    eod_session = discovery.get("eod_session")
    if not isinstance(eod_session, Mapping):
        return {"status": "not_eod", "reason": "eod_session_metadata_missing"}
    state = str(eod_session.get("state") or "").strip()
    calendar_basis = str(eod_session.get("calendar_basis") or "").strip()
    session_date = str(eod_session.get("session_date") or "").strip()
    if state != "after_close":
        return {"status": "not_eod", "reason": f"market_session_state={state or 'missing'}"}
    if calendar_basis != "exchange_calendar":
        return {"status": "not_eod", "reason": f"calendar_basis={calendar_basis or 'missing'}"}
    if not observed_at.startswith(session_date) or len(session_date) != 10:
        return {"status": "not_eod", "reason": "session_date_does_not_match_observed_at"}
    return {"status": "pass", "reason": "verified_exchange_after_close"}


def _validate_discovery_coverage(discovery: Mapping[str, Any]) -> dict[str, Any]:
    """Require an actual public cross-section before closing an EOD discovery control.

    An immutable archive of a source outage is valuable operational evidence,
    but it is not proof that the desk actually searched the market.  This
    check deliberately does *not* require a returned candidate: a valid
    all-market scan can correctly find no names passing its disclosed filters.
    """
    source = discovery.get("source")
    universe = source.get("universe_snapshot") if isinstance(source, Mapping) else None
    if not isinstance(universe, Mapping):
        return {
            "status": "blocked",
            "reason": "universe_snapshot_metadata_missing",
        }
    data_quality = str(universe.get("data_quality") or "")
    coverage = universe.get("coverage")
    if data_quality not in {"public_snapshot", "public_snapshot_degraded"}:
        return {
            "status": "blocked",
            "reason": f"universe_data_quality={data_quality or 'missing'}",
        }
    if not isinstance(coverage, Mapping):
        return {"status": "blocked", "reason": "universe_coverage_missing"}
    try:
        source_rows = int(coverage.get("source_row_count") or 0)
        eligible_rows = int(coverage.get("eligible_a_share_count") or 0)
    except (TypeError, ValueError):
        return {"status": "blocked", "reason": "universe_coverage_counts_invalid"}
    if source_rows <= 0 or eligible_rows <= 0:
        return {
            "status": "blocked",
            "reason": "usable_public_cross_section_missing",
            "source_row_count": source_rows,
            "eligible_a_share_count": eligible_rows,
        }
    return {
        "status": "pass",
        "reason": "usable_public_cross_section_verified",
        "data_quality": data_quality,
        "source_row_count": source_rows,
        "eligible_a_share_count": eligible_rows,
    }


class PublicMarketDiscoveryService:
    """Collect a bounded public whole-market snapshot and build observations."""

    def __init__(
        self,
        *,
        spot_fetcher: Callable[[], pd.DataFrame] | None = None,
        fallback_spot_fetcher: Callable[[], pd.DataFrame] | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        # An injected primary fetcher remains single-source unless the caller
        # explicitly injects its fallback too. This keeps deterministic tests
        # and failure simulations from silently making live network calls.
        if spot_fetcher is not None:
            self._spot_fetchers = [(SOURCE, spot_fetcher)]
            if fallback_spot_fetcher is not None:
                self._spot_fetchers.append((FALLBACK_SOURCE, fallback_spot_fetcher))
        else:
            self._spot_fetchers = [
                (SOURCE, fetch_eastmoney_a_share_spot),
                (FALLBACK_SOURCE, fallback_spot_fetcher or fetch_sina_a_share_spot),
            ]
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def build_universe_snapshot(self) -> dict[str, Any]:
        """Fetch one all-market public snapshot with explicit coverage limits."""
        observed_at = self._now().astimezone(timezone.utc).isoformat()
        frame: pd.DataFrame | None = None
        active_source = ""
        fallback_path: list[str] = []
        errors: list[dict[str, str]] = []
        for source, fetcher in self._spot_fetchers:
            # Each adapter already probes its own public mirrors. Repeating a
            # failed all-market fetch here merely multiplies latency and delays
            # the disclosed fallback, so the outer desk retries once per lane.
            for attempt in range(1):
                try:
                    candidate = await asyncio.wait_for(
                        asyncio.to_thread(fetcher),
                        timeout=15 if source == SOURCE else 30,
                    )
                    if not isinstance(candidate, pd.DataFrame) or candidate.empty:
                        raise ValueError("public all-market spot source returned no rows")
                    frame = candidate
                    active_source = source
                    break
                except Exception as error:
                    errors.append(
                        {
                            "source": source,
                            "attempt": str(attempt + 1),
                            "type": type(error).__name__,
                            "message": str(error),
                        }
                    )
            if frame is not None:
                break
            fallback_path.append(source)

        if frame is None:
            return {
                "schema_version": "market-desk-public-universe-snapshot.v1",
                "observed_at": observed_at,
                "source": SOURCE,
                "data_quality": "unavailable",
                "rows": [],
                "coverage": {
                    "source_row_count": 0,
                    "eligible_a_share_count": 0,
                    "status": "unavailable",
                    "universe_definition": "public A-share spot response",
                },
                "warnings": [
                    "Public all-market spot sources were unavailable after bounded retries; discovery is blocked."
                ],
                "errors": errors,
            }

        rows = [_normalise_row(row) for _, row in frame.iterrows()]
        eligible_rows = [row for row in rows if _is_eligible_a_share(row)]
        used_fallback = active_source != SOURCE
        warnings = [
            "Public spot coverage is an observation universe, not a point-in-time eligible listing universe.",
            "The snapshot has no source-verified fund-flow, position, order-book, or execution data.",
        ]
        if used_fallback:
            warnings.append(
                "Degradation note: the primary public all-market source failed; this run uses the Sina public snapshot and remains observation-only."
            )
        return {
            "schema_version": "market-desk-public-universe-snapshot.v1",
            "observed_at": observed_at,
            "source": active_source,
            "data_quality": "public_snapshot_degraded" if used_fallback else "public_snapshot",
            "rows": eligible_rows,
            "coverage": {
                "source_row_count": len(frame),
                "eligible_a_share_count": len(eligible_rows),
                "status": "partial_public_universe",
                "fallback_path": fallback_path,
                "universe_definition": (
                    "Shanghai, Shenzhen, and Beijing A-share code families in one public spot response; "
                    "not a licensed point-in-time listing universe."
                ),
            },
            "warnings": warnings,
            "errors": errors,
        }

    def discover(
        self,
        *,
        market_overview: Mapping[str, Any],
        rotation: Mapping[str, Any],
        universe_snapshot: Mapping[str, Any],
        candidate_limit: int = 20,
        min_amount: float = DEFAULT_MIN_AMOUNT,
        min_change_pct: float = DEFAULT_MIN_CHANGE_PCT,
    ) -> dict[str, Any]:
        """Create research observations using disclosed, non-composite filters."""
        if candidate_limit < 1 or candidate_limit > 100:
            raise ValueError("candidate_limit must be between 1 and 100")
        if min_amount < 0:
            raise ValueError("min_amount must be non-negative")

        regime = _regime(market_overview)
        rows = universe_snapshot.get("rows")
        source_rows = rows if isinstance(rows, Sequence) and not isinstance(rows, str) else []
        normalized_rows = [dict(row) for row in source_rows if isinstance(row, Mapping)]
        liquid = [row for row in normalized_rows if _number(row.get("amount")) >= min_amount]
        moved = [row for row in liquid if _number(row.get("change_pct")) >= min_change_pct]
        moved.sort(
            key=lambda row: (-_number(row.get("change_pct")), -_number(row.get("amount")), str(row.get("code") or ""))
        )

        source_quality = str(universe_snapshot.get("data_quality") or "unavailable")
        discovery_status = (
            "prepare_research"
            if regime in {"selective_risk_on", "trend_risk_on"}
            and source_quality == "public_snapshot"
            else "observe"
        )
        candidates = [
            _candidate_card(
                row,
                index=index,
                discovery_status=discovery_status,
                observed_at=str(universe_snapshot.get("observed_at") or ""),
                min_amount=min_amount,
                min_change_pct=min_change_pct,
            )
            for index, row in enumerate(moved[:candidate_limit], start=1)
        ]

        warnings = _string_items(universe_snapshot.get("warnings"))
        warnings.extend(_string_items(rotation.get("warnings")))
        warnings.extend(_string_items(market_overview.get("regime", {}).get("warnings") if isinstance(market_overview.get("regime"), Mapping) else []))
        warnings.extend(
            [
                "Candidates are sorted only by disclosed daily change and turnover after liquidity filters; no alpha score or buy ranking is claimed.",
                "Rotation observations are not mapped to stocks without a source-verified stock-to-sector relationship.",
                "Every candidate remains research-only and must pass independent evidence, risk, execution, compliance, and IC gates before a paper-plan decision.",
            ]
        )
        if regime in {"insufficient_data", "risk_off"}:
            warnings.append("Current market regime permits no new risk; discovery output is observation only.")
        if not normalized_rows:
            warnings.append("No usable public all-market rows were available; no candidate may be promoted.")

        return {
            "schema_version": SCHEMA_VERSION,
            "observed_at": universe_snapshot.get("observed_at"),
            "market_regime": regime,
            "discovery_lane": "public_observation",
            "formal_decision_eligible": False,
            "research_only": True,
            "no_order_execution": True,
            "candidate_status_contract": ["observe", "prepare_research"],
            "selection_rule": {
                "universe": universe_snapshot.get("coverage", {}),
                "required": {
                    "minimum_amount": min_amount,
                    "minimum_change_pct": min_change_pct,
                    "exclude_st_and_delisting_markers": True,
                },
                "sort": ["change_pct descending", "amount descending", "code ascending"],
                "not_used": ["fund_flow", "crowding", "positioning", "order_book", "composite_alpha_score"],
            },
            "screening_counts": {
                "eligible_public_rows": len(normalized_rows),
                "liquid_rows": len(liquid),
                "movement_rows": len(moved),
                "returned_candidates": len(candidates),
            },
            "market_overview": {
                "schema_version": market_overview.get("schema_version"),
                "regime": market_overview.get("regime", {}),
            },
            "rotation_context": _rotation_context(rotation),
            "source": {
                "universe_snapshot": {
                    "source": universe_snapshot.get("source"),
                    "observed_at": universe_snapshot.get("observed_at"),
                    "data_quality": source_quality,
                    "coverage": universe_snapshot.get("coverage", {}),
                },
                "market_overview_schema": market_overview.get("schema_version"),
                "rotation_schema": rotation.get("schema_version"),
            },
            "candidates": candidates,
            "promotion_requirements": [
                "Source-verified stock-to-sector mapping and catalyst evidence.",
                "A separately sourced technical entry and invalidation condition.",
                "Explicit maximum-loss, position-limit, T+1, limit-down, suspension, and overnight-gap risk controls.",
                "Data verifier, risk, execution-liquidity, compliance, and investment-committee controls.",
            ],
            "warnings": list(dict.fromkeys(warnings)),
            "errors": list(universe_snapshot.get("errors") or []),
        }


def _normalise_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "code": _text(_pick(row, "代码", "code")),
        "name": _text(_pick(row, "名称", "name")),
        "last_price": _number_or_none(_pick(row, "最新价", "last_price", "price")),
        "change_pct": _number_or_none(_pick(row, "涨跌幅", "change_pct")),
        "amount": _number_or_none(_pick(row, "成交额", "amount")),
        "turnover_rate": _number_or_none(_pick(row, "换手率", "turnover_rate")),
        "volume_ratio": _number_or_none(_pick(row, "量比", "volume_ratio")),
        "pe": _number_or_none(_pick(row, "市盈率-动态", "pe")),
        "pb": _number_or_none(_pick(row, "市净率", "pb")),
    }


def _candidate_card(
    row: Mapping[str, Any], *, index: int, discovery_status: str, observed_at: str, min_amount: float, min_change_pct: float
) -> dict[str, Any]:
    code = str(row.get("code") or "")
    return {
        "candidate_id": f"public-discovery:{code}:{observed_at[:10] or 'unknown'}",
        "code": code,
        "name": row.get("name"),
        "discovery_status": discovery_status,
        "formal_decision_eligible": False,
        "research_only": True,
        "no_order_execution": True,
        "observation": dict(row),
        "selection_explanation": (
            f"Public all-market snapshot met amount >= {min_amount:g} and daily change >= {min_change_pct:g}%; "
            f"listed at disclosed sort position {index}."
        ),
        "next_step": (
            "Start independent research and risk review before considering any paper-plan candidate."
            if discovery_status == "prepare_research"
            else "Observe only; do not add new risk until the market-permission and evidence gates improve."
        ),
    }


def _rotation_context(rotation: Mapping[str, Any]) -> dict[str, Any]:
    pool = rotation.get("observation_pool")
    observations = pool if isinstance(pool, Sequence) and not isinstance(pool, str) else []
    return {
        "schema_version": rotation.get("schema_version"),
        "observed_at": rotation.get("observed_at"),
        "data_quality": rotation.get("data_quality"),
        "observation_count": len(observations),
        "mapping_status": "not_mapped_to_discovery_candidates",
        "limitation": "Board observations remain a market context only until a source-verified stock-to-sector mapping is supplied.",
    }


def _is_eligible_a_share(row: Mapping[str, Any]) -> bool:
    code = str(row.get("code") or "")
    name = str(row.get("name") or "").upper()
    if len(code) != 6 or "ST" in name or "退" in name:
        return False
    # Include the Beijing Stock Exchange families (920/430/83/87/88) while
    # keeping Shenzhen/Shanghai B shares (200/900) outside the A-share desk.
    return (
        code[0] in {"0", "3", "6"}
        or code.startswith("92")
        or code.startswith("43")
        or code.startswith("83")
        or code.startswith("87")
        or code.startswith("88")
    )


def _regime(overview: Mapping[str, Any]) -> str:
    value = overview.get("regime")
    if isinstance(value, Mapping):
        return str(value.get("regime") or "insufficient_data")
    return "insufficient_data"


def _string_items(value: object) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        return []
    result: list[str] = []
    for item in value:
        if isinstance(item, Mapping):
            message = item.get("message")
            if message:
                result.append(str(message))
        elif item:
            result.append(str(item))
    return result


def _pick(row: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in row:
            return row[key]
    return None


def _text(value: Any) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def _number_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if pd.notna(parsed) else None


def _number(value: Any) -> float:
    return _number_or_none(value) or 0.0


def _is_timezone_timestamp(value: str) -> bool:
    try:
        timestamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return timestamp.tzinfo is not None


def _blocked_discovery_archive(archive_path: Path, failure: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "archive_path": str(archive_path),
        "failures": [failure],
    }
