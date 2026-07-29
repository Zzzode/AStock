"""A-share industry/concept cross-section observation contract.

The service ranks only metrics actually supplied by the source.  A one-day
sector move is an observation, not a durable rotation conclusion or a trade.
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Awaitable, Callable, Mapping
from datetime import date, datetime, timedelta, timezone
from threading import Lock
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import akshare as ak
import pandas as pd
from akshare.stock_feature import stock_board_industry_ths

from ..data_provenance import DataProvenance, QualityTier

FrameFetcher = Callable[[], Awaitable[pd.DataFrame]]
HistoryFetcher = Callable[[str, str, date, date], Awaitable[pd.DataFrame]]

SCHEMA_VERSION = "market_rotation.v1"
EASTMONEY_BOARD_SOURCE = "eastmoney.push2.board_list"
INDUSTRY_SOURCE = EASTMONEY_BOARD_SOURCE
CONCEPT_SOURCE = EASTMONEY_BOARD_SOURCE
THS_INDUSTRY_SOURCE = "akshare.stock_board_industry_summary_ths"
EASTMONEY_BOARD_HOSTS = ("17.push2.eastmoney.com", "79.push2.eastmoney.com", "push2.eastmoney.com")
_AKSHARE_TQDM_LOCK = Lock()


class MarketRotationService:
    """Build a source-labelled, same-cutoff industry/concept ranking packet."""

    def __init__(
        self,
        *,
        industry_fetcher: FrameFetcher | None = None,
        concept_fetcher: FrameFetcher | None = None,
        history_fetcher: HistoryFetcher | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._industry_fetcher = industry_fetcher or self._fetch_industries
        self._concept_fetcher = concept_fetcher or self._fetch_concepts
        self._history_fetcher = history_fetcher or self._fetch_history
        self._now = now or (lambda: datetime.now(timezone.utc))

    async def build_cross_section(
        self,
        *,
        include_concepts: bool = True,
        observation_limit: int = 20,
        history_validation_limit: int = 0,
        history_scope: str = "selected",
        history_concurrency: int = 8,
    ) -> dict[str, Any]:
        """Return market-wide rankings and a non-investable observation pool.

        ``selected`` history validation enriches a rate-bounded observation
        subset. ``full`` validates every normalized industry/concept row and
        makes its coverage explicit; a partial full run is never presented as
        a full-market multi-horizon ranking.
        """
        observed_at = self._now().astimezone(timezone.utc).isoformat()
        warnings: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        results = await asyncio.gather(
            self._industry_fetcher(),
            self._concept_fetcher() if include_concepts else _empty_frame(),
            return_exceptions=True,
        )
        industry_result, concept_result = results
        industry_source, industry_fallback_path = self._frame_source(
            industry_result, INDUSTRY_SOURCE
        )
        concept_source, concept_fallback_path = self._frame_source(
            concept_result, CONCEPT_SOURCE
        )
        for component, source, fallback_path in (
            ("industry", industry_source, industry_fallback_path),
            ("concept", concept_source, concept_fallback_path),
        ):
            if fallback_path:
                warnings.append(
                    {
                        "code": "component_fallback_active",
                        "message": (
                            f"{component.title()} observations use public fallback "
                            f"{source}; treat them as a degraded snapshot."
                        ),
                        "source": source,
                    }
                )
        industries = self._normalize_component(
            result=industry_result,
            component="industry",
            source=industry_source,
            fallback_path=industry_fallback_path,
            observed_at=observed_at,
            warnings=warnings,
            errors=errors,
        )
        concepts = self._normalize_component(
            result=concept_result,
            component="concept",
            source=concept_source,
            fallback_path=concept_fallback_path,
            observed_at=observed_at,
            warnings=warnings,
            errors=errors,
            requested=include_concepts,
        )
        components = {"industries": industries["health"], "concepts": concepts["health"]}
        quality = self._quality_tier(components, include_concepts=include_concepts)
        rankings = {
            "industries": industries["rows"],
            "concepts": concepts["rows"],
        }
        self._annotate_turnover_attention(rankings)
        history_validation = await self._validate_history(
            rankings,
            limit=history_validation_limit,
            scope=history_scope,
            concurrency=history_concurrency,
            cutoff=self._now().date(),
            warnings=warnings,
        )
        components["history_validation"] = history_validation
        observations = self._observation_pool(rankings, limit=observation_limit)
        fallback_path = tuple(
            dict.fromkeys((*industry_fallback_path, *concept_fallback_path))
        )
        provenance = DataProvenance(
            source="market_rotation_v1",
            timestamp=observed_at,
            quality_tier=quality,
            fallback_path=fallback_path,
            warnings=warnings,
            errors=errors,
        ).to_dict()
        provenance["components"] = components
        return {
            "schema_version": SCHEMA_VERSION,
            "observed_at": observed_at,
            "data_quality": quality.value,
            "ranking_basis": {
                "metric": "intraday_change_pct",
                "horizons_available": ["intraday", "5d", "20d", "60d"],
                "history_validation": history_validation,
                "turnover_attention": self._turnover_attention_summary(rankings),
                "crowding_evidence": {
                    "status": "unavailable",
                    "decision_weight": 0,
                    "required_sources": [
                        "source-verified fund flow",
                        "margin/short-interest or holder-position history",
                        "constituent-level turnover and float-adjusted ownership",
                    ],
                    "limitations": [
                        "Board turnover-rate percentiles measure current trading attention, not investor crowding.",
                        "No crowding conclusion is emitted without a reproducible position or flow source.",
                    ],
                },
                "limitations": [
                    "Multi-day returns exist only for explicitly history-validated observations; full-scope claims require full coverage.",
                    "No source-verified fund-flow, crowding, or constituent breadth is inferred.",
                    "Observation-pool entries are not investment candidates until separately gated.",
                ],
            },
            "rankings": rankings,
            "observation_pool": observations,
            "warnings": warnings,
            "errors": errors,
            "provenance": provenance,
        }

    async def _fetch_industries(self) -> pd.DataFrame:
        """Fetch industries through a bounded board-list endpoint.

        AkShare's industry-list adapter may expand constituents with a progress
        bar, which breaks the capability kernel's JSON contract and can turn a
        single cross-section request into an unbounded operation.  The direct
        East Money board list supplies the exact fields this service ranks. A
        Tonghuashun public summary remains a visibly degraded fallback.
        """
        try:
            frame = await asyncio.to_thread(
                self._fetch_eastmoney_board_list, "m:90 t:2 f:!50"
            )
            frame.attrs["market_rotation_source"] = EASTMONEY_BOARD_SOURCE
            frame.attrs["market_rotation_fallback_path"] = ()
            return frame
        except Exception as primary_error:
            try:
                frame = await asyncio.wait_for(
                    asyncio.to_thread(_fetch_tonghuashun_industry_summary), timeout=10
                )
                if not isinstance(frame, pd.DataFrame) or frame.empty:
                    raise ValueError("Tonghuashun industry response has no rows")
            except Exception as fallback_error:
                raise RuntimeError(
                    "industry board fetch failed via direct East Money and "
                    f"Tonghuashun public fallback: {type(primary_error).__name__}; "
                    f"{type(fallback_error).__name__}"
                ) from fallback_error
            frame.attrs["market_rotation_source"] = THS_INDUSTRY_SOURCE
            frame.attrs["market_rotation_fallback_path"] = (THS_INDUSTRY_SOURCE,)
            return frame

    async def _fetch_concepts(self) -> pd.DataFrame:
        """Fetch concepts from the direct public board endpoint.

        AkShare's concept-list adapter emits a progress bar while it expands
        constituent requests. That pollutes every ``--json`` desk command and
        can take materially longer than a cross-section observation needs.
        The direct East Money list is already the bounded fallback adapter for
        this service; using it here preserves the same public-data boundary
        while keeping the capability kernel machine-readable.
        """
        frame = await asyncio.to_thread(
            self._fetch_eastmoney_board_list, "m:90 t:3 f:!50"
        )
        frame.attrs["market_rotation_source"] = EASTMONEY_BOARD_SOURCE
        frame.attrs["market_rotation_fallback_path"] = ()
        return frame

    @staticmethod
    def _fetch_eastmoney_board_list(filter_expression: str) -> pd.DataFrame:
        """Read a public East Money board list without unbounded adapter retries."""
        fields = "f2,f3,f8,f12,f14,f20,f104,f105,f128,f136"
        last_error: Exception | None = None
        for host in EASTMONEY_BOARD_HOSTS:
            query = urlencode(
                {
                    "pn": "1",
                    "pz": "500",
                    "po": "1",
                    "np": "1",
                    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
                    "fltt": "2",
                    "invt": "2",
                    "fid": "f3",
                    "fs": filter_expression,
                    "fields": fields,
                }
            )
            request = Request(
                f"https://{host}/api/qt/clist/get?{query}",
                headers={"User-Agent": "Mozilla/5.0"},
            )
            try:
                with urlopen(request, timeout=5) as response:  # nosec B310 - fixed hosts
                    payload = json.loads(response.read().decode("utf-8", errors="replace"))
                rows = payload.get("data", {}).get("diff", [])
                if not isinstance(rows, list) or not rows:
                    raise ValueError("East Money board response has no rows")
                return pd.DataFrame(
                    [
                        {
                            "板块代码": row.get("f12"),
                            "板块名称": row.get("f14"),
                            "涨跌幅": row.get("f3"),
                            "换手率": row.get("f8"),
                            "总市值": row.get("f20"),
                            "上涨家数": row.get("f104"),
                            "下跌家数": row.get("f105"),
                            "领涨股票": row.get("f128"),
                            "领涨股票-涨跌幅": row.get("f136"),
                        }
                        for row in rows
                        if isinstance(row, Mapping)
                    ]
                )
            except Exception as error:
                last_error = error
        raise RuntimeError("All configured East Money board mirrors failed") from last_error

    @staticmethod
    def _frame_source(result: object, default_source: str) -> tuple[str, tuple[str, ...]]:
        if not isinstance(result, pd.DataFrame):
            return default_source, ()
        return (
            str(result.attrs.get("market_rotation_source") or default_source),
            tuple(
                str(value)
                for value in result.attrs.get("market_rotation_fallback_path", ())
            ),
        )

    async def _fetch_history(
        self, component: str, name: str, start_date: date, end_date: date
    ) -> pd.DataFrame:
        if component == "industry":
            return await asyncio.to_thread(
                ak.stock_board_industry_hist_em,
                symbol=name,
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                period="日k",
                adjust="",
            )
        return await asyncio.to_thread(
            ak.stock_board_concept_hist_em,
            symbol=name,
            period="daily",
            start_date=start_date.strftime("%Y%m%d"),
            end_date=end_date.strftime("%Y%m%d"),
            adjust="",
        )

    async def _validate_history(
        self,
        rankings: Mapping[str, list[dict[str, Any]]],
        *,
        limit: int,
        scope: str,
        concurrency: int,
        cutoff: date,
        warnings: list[dict[str, Any]],
    ) -> dict[str, Any]:
        normalized_scope = str(scope).strip().lower()
        if normalized_scope not in {"selected", "full"}:
            raise ValueError("history_scope must be selected or full")
        if concurrency < 1:
            raise ValueError("history_concurrency must be at least one")
        if normalized_scope == "selected" and limit <= 0:
            return {
                "status": "not_requested",
                "scope": "selected",
                "requested_count": 0,
                "verified_count": 0,
                "verified_60d_count": 0,
                "coverage_ratio": 0.0,
                "source_records": [],
                "source_record_count": 0,
                "cutoff_date": cutoff.isoformat(),
                "evidence_status": "not_requested",
                "lookbacks": [5, 20, 60],
            }
        requests: list[tuple[str, dict[str, Any]]] = []
        for component, rows in rankings.items():
            requested_rows = rows if normalized_scope == "full" else rows[:limit]
            requests.extend((component, row) for row in requested_rows)
        semaphore = asyncio.Semaphore(concurrency)

        async def validate_one(
            component: str, row: dict[str, Any]
        ) -> tuple[
            str,
            dict[str, Any],
            dict[str, float | None] | None,
            dict[str, Any] | None,
            Exception | None,
        ]:
            try:
                async with semaphore:
                    history_component = "industry" if component == "industries" else "concept"
                    frame = await self._history_fetcher(
                        history_component,
                        str(row["name"]),
                        cutoff - timedelta(days=150),
                        cutoff,
                    )
                returns = _multi_horizon_returns(frame, cutoff=cutoff)
                return (
                    component,
                    row,
                    returns,
                    {
                        "component": component,
                        "name": str(row["name"]),
                        "code": row.get("code"),
                        "source": str(row["source"]),
                        "records": _frame_source_records(frame),
                    },
                    None,
                )
            except Exception as error:
                return component, row, None, None, error

        outcomes = await asyncio.gather(
            *(validate_one(component, row) for component, row in requests)
        )
        verified = 0
        verified_60d = 0
        source_records: list[dict[str, Any]] = []
        by_component: dict[str, dict[str, int]] = {
            "industries": {"requested": 0, "verified": 0, "verified_60d": 0},
            "concepts": {"requested": 0, "verified": 0, "verified_60d": 0},
        }
        for component, row, returns, evidence, error in outcomes:
            by_component[component]["requested"] += 1
            if error is not None or returns is None:
                warnings.append(
                    {
                        "code": "history_validation_unavailable",
                        "message": f"History validation failed for {component} {row['name']}.",
                        "source": row["source"],
                        "details": {
                            "error_type": type(error).__name__ if error else "UnknownError",
                            "message": str(error) if error else "unknown error",
                        },
                    }
                )
                continue
            row["multi_horizon_return_pct"] = returns
            row["history_validation_status"] = (
                "verified" if returns["60d"] is not None else "insufficient_history"
            )
            if evidence is not None:
                source_records.append(evidence)
            if returns["5d"] is not None:
                verified += 1
                by_component[component]["verified"] += 1
            if returns["60d"] is not None:
                verified_60d += 1
                by_component[component]["verified_60d"] += 1
        requested = len(requests)
        fully_verified = requested > 0 and verified_60d == requested
        return {
            "status": "available" if fully_verified else "partial",
            "scope": normalized_scope,
            "requested_count": requested,
            "verified_count": verified,
            "verified_60d_count": verified_60d,
            "coverage_ratio": round(verified / requested, 6) if requested else 0.0,
            "coverage_60d_ratio": round(verified_60d / requested, 6) if requested else 0.0,
            "full_cross_section_ready": normalized_scope == "full" and fully_verified,
            "components": by_component,
            "cutoff_date": cutoff.isoformat(),
            "source_records": source_records,
            "source_record_count": len(source_records),
            "evidence_status": "embedded_source_records",
            "lookbacks": [5, 20, 60],
        }

    @staticmethod
    def _normalize_component(
        *,
        result: object,
        component: str,
        source: str,
        fallback_path: tuple[str, ...],
        observed_at: str,
        warnings: list[dict[str, Any]],
        errors: list[dict[str, Any]],
        requested: bool = True,
    ) -> dict[str, Any]:
        if not requested:
            return {"rows": [], "health": {"component": component, "source": source, "status": "not_requested", "coverage_ratio": 1.0, "quality_tier": "unavailable", "observed_at": observed_at}}
        if isinstance(result, Exception):
            errors.append({"code": f"{component}_unavailable", "message": f"{component.title()} source was unavailable.", "source": source, "details": {"error_type": type(result).__name__, "message": str(result)}})
            return {"rows": [], "health": {"component": component, "source": source, "status": "unavailable", "coverage_ratio": 0.0, "quality_tier": "unavailable", "observed_at": observed_at}}
        if not isinstance(result, pd.DataFrame) or result.empty:
            warnings.append({"code": f"{component}_empty", "message": f"{component.title()} source returned no rows.", "source": source})
            return {"rows": [], "health": {"component": component, "source": source, "status": "unavailable", "coverage_ratio": 0.0, "quality_tier": "unavailable", "observed_at": observed_at}}
        name_column = _first_column(result, "板块名称", "板块", "名称", "name")
        code_column = _first_column(result, "板块代码", "代码", "code")
        change_column = _first_column(result, "涨跌幅", "change_percent", "change_pct")
        if name_column is None or change_column is None:
            warnings.append({"code": f"{component}_schema_incomplete", "message": f"{component.title()} source lacks a name or change-percent column.", "source": source})
            return {"rows": [], "health": {"component": component, "source": source, "status": "unavailable", "coverage_ratio": 0.0, "quality_tier": "unavailable", "observed_at": observed_at}}
        normalized: list[dict[str, Any]] = []
        for _, row in result.iterrows():
            change = _float_or_none(row.get(change_column))
            name = str(row.get(name_column) or "").strip()
            if not name or change is None:
                continue
            normalized.append({
                "name": name,
                "code": str(row.get(code_column) or "").strip() if code_column else None,
                "change_pct": change,
                "turnover_rate_pct": _float_or_none(
                    row.get(_first_column(result, "换手率", "turnover_rate") or "")
                ),
                "market_cap": _float_or_none(
                    row.get(_first_column(result, "总市值", "market_cap") or "")
                ),
                "advances": _int_or_none(
                    row.get(_first_column(result, "上涨家数", "advances") or "")
                ),
                "declines": _int_or_none(
                    row.get(_first_column(result, "下跌家数", "declines") or "")
                ),
                "leading_stock": str(
                    row.get(_first_column(result, "领涨股票", "leading_stock") or "")
                ).strip() or None,
                "leading_stock_change_pct": _float_or_none(
                    row.get(
                        _first_column(
                            result, "领涨股票-涨跌幅", "leading_stock_change_pct"
                        )
                        or ""
                    )
                ),
                "source": source,
            })
            advances = normalized[-1]["advances"]
            declines = normalized[-1]["declines"]
            normalized[-1]["participation_ratio"] = (
                round(advances / (advances + declines), 6)
                if advances is not None and declines is not None and advances + declines > 0
                else None
            )
        normalized.sort(key=lambda item: (-item["change_pct"], item["name"]))
        for rank, row in enumerate(normalized, start=1):
            row["rank"] = rank
        coverage = round(len(normalized) / len(result), 6) if len(result) else 0.0
        status = "available" if coverage >= 0.98 else "partial"
        quality_tier = (
            "realtime"
            if status == "available" and not fallback_path
            else "snapshot"
        )
        return {
            "rows": normalized,
            "health": {
                "component": component,
                "source": source,
                "status": status,
                "source_row_count": len(result),
                "ranked_row_count": len(normalized),
                "coverage_ratio": coverage,
                "quality_tier": quality_tier,
                "fallback_path": list(fallback_path),
                "observed_at": observed_at,
            },
        }

    @staticmethod
    def _annotate_turnover_attention(
        rankings: Mapping[str, list[dict[str, Any]]]
    ) -> None:
        """Annotate observable turnover percentiles without calling them crowding."""
        for rows in rankings.values():
            available = sorted(
                (row for row in rows if row["turnover_rate_pct"] is not None),
                key=lambda row: (float(row["turnover_rate_pct"]), row["name"]),
            )
            denominator = len(available)
            for index, row in enumerate(available, start=1):
                row["turnover_attention_percentile"] = (
                    round(index / denominator, 6) if denominator else None
                )
            for row in rows:
                row.setdefault("turnover_attention_percentile", None)

    @staticmethod
    def _turnover_attention_summary(
        rankings: Mapping[str, list[dict[str, Any]]]
    ) -> dict[str, Any]:
        components: dict[str, dict[str, Any]] = {}
        for component, rows in rankings.items():
            available = sum(row["turnover_rate_pct"] is not None for row in rows)
            components[component] = {
                "observed_count": available,
                "universe_count": len(rows),
                "coverage_ratio": round(available / len(rows), 6) if rows else 0.0,
                "metric": "board_turnover_rate_percentile",
                "interpretation": "trading_attention_only",
            }
        return {"components": components, "decision_weight": 0}

    @staticmethod
    def _observation_pool(rankings: Mapping[str, list[dict[str, Any]]], *, limit: int) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        for component, rows in rankings.items():
            for row in rows[:max(0, limit)]:
                participation = row["participation_ratio"]
                selected.append({
                    "subject_type": "industry" if component == "industries" else "concept",
                    "name": row["name"],
                    "code": row["code"],
                    "rank": row["rank"],
                    "change_pct": row["change_pct"],
                    "participation_ratio": participation,
                    "turnover_rate_pct": row["turnover_rate_pct"],
                    "turnover_attention_percentile": row[
                        "turnover_attention_percentile"
                    ],
                    "breadth_status": (
                        "broad" if participation is not None and participation >= 0.60
                        else ("narrow_or_mixed" if participation is not None else "unavailable")
                    ),
                    "multi_horizon_return_pct": row.get("multi_horizon_return_pct"),
                    "history_validation_status": row.get(
                        "history_validation_status", "not_requested"
                    ),
                    "status": "observation",
                    "promotion_requirements": [
                        "multi-horizon relative strength",
                        "constituent breadth and liquidity",
                        "source-verified catalyst",
                        "independent risk and execution gates",
                    ],
                })
        return selected

    @staticmethod
    def _quality_tier(components: Mapping[str, Mapping[str, Any]], *, include_concepts: bool) -> QualityTier:
        required = [components["industries"]]
        if include_concepts:
            required.append(components["concepts"])
        return QualityTier.REALTIME if all(item.get("quality_tier") == "realtime" for item in required) else (QualityTier.SNAPSHOT if any(item.get("status") in {"available", "partial"} for item in required) else QualityTier.UNAVAILABLE)


async def _empty_frame() -> pd.DataFrame:
    return pd.DataFrame()


def _first_column(frame: pd.DataFrame, *candidates: str) -> str | None:
    return next((candidate for candidate in candidates if candidate in frame.columns), None)


def _float_or_none(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if pd.notna(parsed) else None


def _int_or_none(value: object) -> int | None:
    parsed = _float_or_none(value)
    return int(parsed) if parsed is not None and parsed >= 0 else None


def _multi_horizon_returns(
    frame: pd.DataFrame, *, cutoff: date
) -> dict[str, float | None]:
    """Compute returns from an ordered, de-duplicated, cutoff-bounded series."""
    close_column = _first_column(frame, "收盘", "close")
    date_column = _first_column(frame, "日期", "date", "datetime")
    if close_column is None or date_column is None:
        raise ValueError("Historical board data requires date and close columns")
    series: dict[date, float] = {}
    for raw_day, raw_close in zip(frame[date_column], frame[close_column], strict=True):
        parsed_day = pd.to_datetime(raw_day, errors="coerce")
        close = _float_or_none(raw_close)
        if pd.isna(parsed_day) or close is None or close <= 0:
            continue
        day = parsed_day.date()
        if day <= cutoff:
            series[day] = close
    if not series:
        raise ValueError("Historical board data has no usable observations at or before cutoff")
    latest_day = max(series)
    if latest_day < cutoff - timedelta(days=7):
        raise ValueError("Historical board data is stale relative to the requested cutoff")
    closes = [series[day] for day in sorted(series)]
    if not closes:
        raise ValueError("Historical board data has no usable closes")
    latest = closes[-1]
    return {
        f"{lookback}d": (
            round((latest / closes[-(lookback + 1)] - 1) * 100, 6)
            if len(closes) > lookback
            else None
        )
        for lookback in (5, 20, 60)
    }


def verify_rotation_history_evidence(rotation: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute reported board returns from embedded source-derived records.

    A rotation packet is still public observation data.  This verifier only
    establishes that its 5/20/60-day figures can be regenerated from the
    frozen records retained in the packet; it does not attest source licensing,
    point-in-time membership, or execution suitability.
    """
    if str(rotation.get("schema_version") or "") != SCHEMA_VERSION:
        return _history_evidence_blocked("unsupported rotation schema")
    ranking_basis = rotation.get("ranking_basis")
    if not isinstance(ranking_basis, Mapping):
        return _history_evidence_blocked("rotation packet lacks ranking_basis")
    validation = ranking_basis.get("history_validation")
    if not isinstance(validation, Mapping):
        return _history_evidence_blocked("rotation packet lacks history_validation")
    if str(validation.get("evidence_status") or "") == "not_requested":
        return {
            "status": "not_requested",
            "verified_source_record_count": 0,
            "failures": [],
        }
    try:
        cutoff = date.fromisoformat(str(validation.get("cutoff_date") or ""))
    except ValueError:
        return _history_evidence_blocked("history validation cutoff_date is invalid")
    source_records = validation.get("source_records")
    if not isinstance(source_records, list):
        return _history_evidence_blocked("history validation source_records must be a list")
    if int(validation.get("source_record_count") or 0) != len(source_records):
        return _history_evidence_blocked("history validation source_record_count does not match records")
    rankings = rotation.get("rankings")
    if not isinstance(rankings, Mapping):
        return _history_evidence_blocked("rotation packet lacks rankings")

    failures: list[str] = []
    recomputed_with_5d = 0
    for evidence in source_records:
        if not isinstance(evidence, Mapping):
            failures.append("history source record is not an object")
            continue
        component = str(evidence.get("component") or "")
        name = str(evidence.get("name") or "")
        source = str(evidence.get("source") or "")
        records = evidence.get("records")
        if component not in {"industries", "concepts"} or not name or not source:
            failures.append("history source record lacks component, name, or source")
            continue
        if not isinstance(records, list) or not records:
            failures.append(f"history source record has no rows for {component}:{name}")
            continue
        rows = rankings.get(component)
        if not isinstance(rows, list):
            failures.append(f"rotation rankings lack component {component}")
            continue
        row = next(
            (
                candidate
                for candidate in rows
                if isinstance(candidate, Mapping)
                and str(candidate.get("name") or "") == name
                and str(candidate.get("source") or "") == source
            ),
            None,
        )
        if row is None:
            failures.append(f"history source record cannot be matched to ranking {component}:{name}")
            continue
        try:
            recomputed = _multi_horizon_returns(pd.DataFrame(records), cutoff=cutoff)
        except (TypeError, ValueError) as error:
            failures.append(f"history source record cannot be recomputed for {component}:{name}: {error}")
            continue
        reported = row.get("multi_horizon_return_pct")
        if not isinstance(reported, Mapping) or any(
            reported.get(label) != value for label, value in recomputed.items()
        ):
            failures.append(f"reported history return does not match source records for {component}:{name}")
            continue
        if recomputed["5d"] is not None:
            recomputed_with_5d += 1

    reported_verified = int(validation.get("verified_count") or 0)
    if reported_verified != recomputed_with_5d:
        failures.append("history validation verified_count does not match recomputed source records")
    return {
        "status": "pass" if not failures else "blocked",
        "verified_source_record_count": len(source_records) - sum(
            1 for failure in failures if failure.startswith("history source record")
        ),
        "recomputed_verified_count": recomputed_with_5d,
        "failures": failures,
    }


def _frame_source_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Retain every source row used by a history-return calculation."""
    return [
        {str(column): _source_json_value(value) for column, value in row.items()}
        for row in frame.to_dict(orient="records")
    ]


def _source_json_value(value: Any) -> Any:
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return None
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            pass
    return value


def _history_evidence_blocked(failure: str) -> dict[str, Any]:
    return {"status": "blocked", "verified_source_record_count": 0, "failures": [failure]}


def _fetch_tonghuashun_industry_summary() -> pd.DataFrame:
    """Call the bounded public fallback without leaking third-party progress UI."""
    with _AKSHARE_TQDM_LOCK:
        original_factory = stock_board_industry_ths.get_tqdm
        stock_board_industry_ths.get_tqdm = lambda *args, **kwargs: (
            lambda iterable, *unused_args, **unused_kwargs: iterable
        )
        try:
            return stock_board_industry_ths.stock_board_industry_summary_ths()
        finally:
            stock_board_industry_ths.get_tqdm = original_factory
