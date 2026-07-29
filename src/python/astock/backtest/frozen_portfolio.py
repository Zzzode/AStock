"""Immutable public-data inputs for bounded paper-portfolio replays.

This module binds the exact daily bars, target weights, and calendar used by a
portfolio simulation to content-addressed bytes.  It deliberately does not
claim that public daily bars cover the execution-critical event domains needed
for a formal historical portfolio backtest.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


PUBLIC_PORTFOLIO_SOURCE = "akshare_public"


@dataclass(frozen=True)
class FrozenPortfolioReplayInput:
    """Content-addressed input for a bounded multi-asset paper replay."""

    market_data: dict[str, pd.DataFrame]
    target_weights: dict[str, dict[str, float]]
    universe_references: dict[str, str]
    trading_calendar: list[str]
    trading_calendar_source: str
    source: str
    observed_at: str
    archive_id: str
    raw_source_records: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "frozen_portfolio_replay_input.v1",
            "market_data": {
                code: _records(frame) for code, frame in self.market_data.items()
            },
            "target_weights": self.target_weights,
            "universe_references": self.universe_references,
            "trading_calendar": self.trading_calendar,
            "trading_calendar_source": self.trading_calendar_source,
            "source_manifest": {
                "schema_version": "frozen_portfolio_replay_sources.v1",
                "source": self.source,
                "as_of": self.observed_at,
                "archive_id": self.archive_id,
                "data_class": "frozen_public_daily_portfolio_input",
            },
            "portfolio_source_manifest": {
                "schema_version": "portfolio_backtest_sources.v1",
                "as_of": self.observed_at,
                "archive_id": self.archive_id,
                "domains": {
                    "trading_calendar": self.source,
                    "eod_bars": self.source,
                    "halts": self.source,
                    "price_limits": self.source,
                    "corporate_actions": self.source,
                    "delistings": self.source,
                },
                "calendar_source": self.trading_calendar_source,
            },
            "coverage_manifest": {
                "corporate_actions": "unverified",
                "delistings": "unverified",
                "price_limits": "unverified",
                "halts": "unverified",
            },
            "price_basis": "forward_adjusted_or_unknown",
            "limitations": [
                "The archive proves exact public daily-bar inputs and supplied weights only.",
                "Bar existence is treated as a paper execution assumption; it does not prove tradability, fill quality, or limit-lock availability.",
                "The input does not establish point-in-time universe, halts, price limits, corporate actions, delistings, or capacity coverage.",
            ],
        }

    def write_frozen_archive(self, directory: Path) -> Path:
        digest = self.archive_id.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("frozen portfolio replay archive_id must be a sha256 digest")
        payload = {
            "schema_version": "market_data_frozen_archive.v1",
            "source": self.source,
            "archive_id": self.archive_id,
            "raw_source_records": self.raw_source_records,
        }
        if _content_hash(_archive_hash_input(payload)) != digest:
            raise ValueError("frozen portfolio replay archive_id does not match raw source records")
        return _write_content_addressed(directory, f"{digest}.json", payload)

    def write_replay_input(self, directory: Path) -> Path:
        digest = self.archive_id.removeprefix("sha256:")
        return _write_content_addressed(directory, f"{digest}.portfolio.replay.json", self.to_dict())


def build_frozen_portfolio_replay_input(
    market_data: Mapping[str, pd.DataFrame],
    target_weights: Mapping[str, Mapping[str, float]],
    *,
    trading_calendar: Sequence[str],
    universe_references: Mapping[str, str],
    source: str = PUBLIC_PORTFOLIO_SOURCE,
    trading_calendar_source: str = "caller_supplied",
    observed_at: str | datetime | None = None,
) -> FrozenPortfolioReplayInput:
    """Normalize exact public daily inputs before a paper-only replay."""
    normalized_source = str(source).strip()
    if normalized_source != PUBLIC_PORTFOLIO_SOURCE:
        raise ValueError("frozen public portfolio replay source must be akshare_public")
    normalized_data = {
        str(code).strip(): _normalize_market_frame(str(code).strip(), frame)
        for code, frame in market_data.items()
    }
    if not normalized_data or any(not code for code in normalized_data):
        raise ValueError("frozen portfolio replay requires nonempty market data")
    calendar = _normalize_calendar(trading_calendar)
    normalized_calendar_source = str(trading_calendar_source).strip()
    if not normalized_calendar_source:
        raise ValueError("frozen portfolio replay requires a trading_calendar_source")
    weights = _normalize_target_weights(target_weights, normalized_data, calendar)
    references = _normalize_universe_references(universe_references, weights)
    timestamp = _normalize_timestamp(observed_at)
    raw_records = {
        "portfolio_replay": {
            "market_data": {
                code: _records(frame) for code, frame in normalized_data.items()
            },
            "target_weights": weights,
            "universe_references": references,
            "trading_calendar": calendar,
            "observed_at": timestamp,
        }
    }
    archive_id = "sha256:" + _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": normalized_source,
            "raw_source_records": raw_records,
        }
    )
    return FrozenPortfolioReplayInput(
        market_data=normalized_data,
        target_weights=weights,
        universe_references=references,
        trading_calendar=calendar,
        trading_calendar_source=normalized_calendar_source,
        source=normalized_source,
        observed_at=timestamp,
        archive_id=archive_id,
        raw_source_records=raw_records,
    )


def parse_frozen_portfolio_replay_input(
    value: Mapping[str, Any],
) -> FrozenPortfolioReplayInput:
    """Validate an agent-safe frozen public portfolio input payload."""
    if str(value.get("schema_version") or "") != "frozen_portfolio_replay_input.v1":
        raise ValueError("portfolio replay input must use frozen_portfolio_replay_input.v1")
    manifest = value.get("source_manifest")
    if not isinstance(manifest, Mapping):
        raise ValueError("portfolio replay input requires a source_manifest")
    if str(manifest.get("schema_version") or "") != "frozen_portfolio_replay_sources.v1":
        raise ValueError("portfolio replay input has an unsupported source manifest")
    raw_data = value.get("market_data")
    if not isinstance(raw_data, Mapping):
        raise ValueError("portfolio replay input market_data must be a mapping")
    packet = build_frozen_portfolio_replay_input(
        {
            str(code): pd.DataFrame(records)
            for code, records in raw_data.items()
            if isinstance(records, list)
        },
        value.get("target_weights") if isinstance(value.get("target_weights"), Mapping) else {},
        trading_calendar=value.get("trading_calendar") if isinstance(value.get("trading_calendar"), list) else (),
        universe_references=value.get("universe_references") if isinstance(value.get("universe_references"), Mapping) else {},
        source=str(manifest.get("source") or ""),
        trading_calendar_source=str(value.get("trading_calendar_source") or "caller_supplied"),
        observed_at=manifest.get("as_of"),
    )
    archive_id = str(manifest.get("archive_id") or "").strip()
    if not archive_id or archive_id != packet.archive_id:
        raise ValueError("portfolio replay input archive_id does not match exact replay inputs")
    return packet


def _normalize_market_frame(code: str, frame: pd.DataFrame) -> pd.DataFrame:
    if not code:
        raise ValueError("portfolio replay market-data code is required")
    if not isinstance(frame, pd.DataFrame):
        raise ValueError(f"portfolio replay market data for {code} must be a DataFrame")
    required = {"date", "open", "close", "tradable", "execution_status"}
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(
            f"portfolio replay market data for {code} lacks: " + ", ".join(missing)
        )
    columns = ["date", "open", "close", "tradable", "execution_status"]
    if "volume" in frame.columns:
        columns.append("volume")
    normalized = frame[columns].copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce").dt.normalize()
    if normalized["date"].isna().any() or normalized["date"].duplicated().any():
        raise ValueError(f"portfolio replay market data for {code} has invalid or duplicate dates")
    for column in ("open", "close"):
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    if normalized[["open", "close"]].isna().any().any() or (normalized[["open", "close"]] <= 0).any().any():
        raise ValueError(f"portfolio replay market data for {code} has invalid prices")
    if "volume" in normalized:
        normalized["volume"] = pd.to_numeric(normalized["volume"], errors="coerce")
        if normalized["volume"].isna().any() or (normalized["volume"] < 0).any():
            raise ValueError(f"portfolio replay market data for {code} has invalid volume")
    normalized["tradable"] = normalized["tradable"].astype(bool)
    normalized["execution_status"] = normalized["execution_status"].astype(str).str.strip().str.lower()
    if not normalized["execution_status"].isin(
        {"tradable", "halted", "limit_up_locked", "limit_down_locked", "unknown"}
    ).all():
        raise ValueError(f"portfolio replay market data for {code} has invalid execution_status")
    return normalized.sort_values("date", kind="stable").reset_index(drop=True)


def _normalize_calendar(value: Sequence[str]) -> list[str]:
    if isinstance(value, (str, bytes)):
        raise ValueError("portfolio replay trading_calendar must be a sequence")
    parsed = [pd.Timestamp(day).normalize() for day in value]
    if len(parsed) < 2 or any(pd.isna(day) for day in parsed) or len(set(parsed)) != len(parsed):
        raise ValueError("portfolio replay trading_calendar requires at least two unique valid sessions")
    return [day.date().isoformat() for day in sorted(parsed)]


def _normalize_target_weights(
    value: Mapping[str, Mapping[str, float]],
    market_data: Mapping[str, pd.DataFrame],
    calendar: Sequence[str],
) -> dict[str, dict[str, float]]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError("portfolio replay requires target_weights")
    calendar_set = set(calendar)
    normalized: dict[str, dict[str, float]] = {}
    for raw_date, raw_weights in value.items():
        day = pd.Timestamp(raw_date).normalize().date().isoformat()
        if day not in calendar_set or not isinstance(raw_weights, Mapping):
            raise ValueError("portfolio replay target weights require calendar dates and code-weight mappings")
        weights = {str(code): float(weight) for code, weight in raw_weights.items()}
        if any(code not in market_data for code in weights) or any(weight < 0 or weight > 1 for weight in weights.values()):
            raise ValueError("portfolio replay target weights contain an unknown code or invalid weight")
        if sum(weights.values()) > 1 + 1e-9:
            raise ValueError("portfolio replay target weights exceed 100%")
        normalized[day] = weights
    return dict(sorted(normalized.items()))


def _normalize_universe_references(
    value: Mapping[str, str], target_weights: Mapping[str, Mapping[str, float]]
) -> dict[str, str]:
    references = {str(day): str(ref).strip() for day, ref in value.items()}
    missing = [day for day in target_weights if not references.get(day)]
    if missing:
        raise ValueError("portfolio replay target dates require explicit universe_references")
    return {day: references[day] for day in sorted(target_weights)}


def _normalize_timestamp(value: str | datetime | None) -> str:
    if value is None:
        timestamp = datetime.now(timezone.utc)
    elif isinstance(value, datetime):
        timestamp = value
    else:
        try:
            timestamp = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError as error:
            raise ValueError("portfolio replay observed_at must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError("portfolio replay observed_at must include a timezone")
    return timestamp.astimezone(timezone.utc).isoformat()


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _archive_hash_input(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "market_data_frozen_archive.v1",
        "source": str(payload["source"]),
        "raw_source_records": payload["raw_source_records"],
    }


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_content_addressed(directory: Path, filename: str, value: Mapping[str, Any]) -> Path:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    target_directory = Path(directory)
    target_directory.mkdir(parents=True, exist_ok=True)
    target = target_directory / filename
    if target.exists():
        if target.read_text(encoding="utf-8") != canonical:
            raise ValueError(f"frozen replay collision at {target}")
        return target
    temporary = target_directory / f".{filename}.tmp"
    temporary.write_text(canonical, encoding="utf-8")
    temporary.replace(target)
    return target
