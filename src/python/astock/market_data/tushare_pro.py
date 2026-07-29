"""Tushare Pro adapter for source-labelled daily A-share portfolio replay.

The adapter is intentionally optional: importing the AStock capability layer
does not require a Tushare installation or a token.  A live call fails closed
unless both an authorized token and accountable data owner are configured.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


@dataclass(frozen=True)
class TushareBacktestPacket:
    """Frozen raw-market replay inputs emitted by one vendor query batch."""

    market_data: dict[str, pd.DataFrame]
    trading_calendar: list[str]
    corporate_actions: dict[str, list[dict[str, Any]]]
    delisting_status: dict[str, dict[str, Any]]
    source_manifest: dict[str, Any]
    price_basis: str
    raw_source_records: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return an agent-safe JSON packet; frames become record arrays."""
        return {
            "schema_version": "tushare_daily_replay_input.v1",
            "market_data": {
                code: _records(frame) for code, frame in self.market_data.items()
            },
            "trading_calendar": self.trading_calendar,
            "corporate_actions": self.corporate_actions,
            "delisting_status": self.delisting_status,
            "source_manifest": self.source_manifest,
            "price_basis": self.price_basis,
        }

    def write_frozen_archive(self, directory: Path) -> Path:
        """Persist the exact vendor responses under their content hash.

        Reusing an existing content-addressed file is allowed only when its
        bytes deserialize to the identical archive envelope. This deliberately
        avoids a mutable "latest" snapshot and never overwrites a conflict.
        """
        archive_id = str(self.source_manifest["archive_id"])
        digest = archive_id.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("Tushare source manifest has an invalid archive_id")
        expected_digest = _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "raw_source_records": self.raw_source_records,
            }
        )
        if digest != expected_digest:
            raise ValueError("Tushare source manifest archive_id does not match raw source records")
        payload = {
            "schema_version": "market_data_frozen_archive.v1",
            "source": "tushare_pro",
            "archive_id": archive_id,
            "raw_source_records": self.raw_source_records,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        target_directory = Path(directory)
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / f"{digest}.json"
        if target.exists():
            existing = target.read_text(encoding="utf-8")
            if existing != canonical:
                raise ValueError(f"frozen archive collision at {target}")
            return target
        temporary = target_directory / f".{digest}.tmp"
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(target)
        return target


@dataclass(frozen=True)
class TushareUniverseSnapshotPacket:
    """A frozen historical listing-universe snapshot derived from stock master data."""

    as_of_date: str
    members: list[str]
    source_ref: str
    archive_id: str
    raw_source_records: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return one ``universe_snapshots``-compatible record."""
        return {
            "as_of_date": self.as_of_date,
            "source_ref": self.source_ref,
            "archive_id": self.archive_id,
            "members": self.members,
        }

    def write_frozen_archive(self, directory: Path) -> Path:
        """Persist the raw master-data responses under their content hash."""
        digest = self.archive_id.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("Tushare universe snapshot has an invalid archive_id")
        expected_digest = _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "raw_source_records": self.raw_source_records,
            }
        )
        if digest != expected_digest:
            raise ValueError("Tushare universe snapshot archive_id does not match raw source records")
        payload = {
            "schema_version": "market_data_frozen_archive.v1",
            "source": "tushare_pro",
            "archive_id": self.archive_id,
            "raw_source_records": self.raw_source_records,
        }
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        target_directory = Path(directory)
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / f"{digest}.json"
        if target.exists():
            if target.read_text(encoding="utf-8") != canonical:
                raise ValueError(f"frozen archive collision at {target}")
            return target
        temporary = target_directory / f".{digest}.tmp"
        temporary.write_text(canonical, encoding="utf-8")
        temporary.replace(target)
        return target


class TushareProBacktestAdapter:
    """Fetch a daily replay packet from an authorized Tushare Pro client."""

    def __init__(
        self,
        *,
        token: str | None = None,
        data_owner: str | None = None,
        client: Any | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._token = (token if token is not None else os.environ.get("TUSHARE_TOKEN", "")).strip()
        self._data_owner = (
            data_owner if data_owner is not None else os.environ.get("MARKET_DATA_ATTESTED_BY", "")
        ).strip()
        self._client = client
        self._now = now or (lambda: datetime.now(timezone.utc))

    def build_daily_replay_packet(
        self,
        codes: Sequence[str],
        *,
        start_date: str,
        end_date: str,
    ) -> TushareBacktestPacket:
        """Fetch raw daily bars and execution-critical events for listed codes."""
        normalized_codes = _normalize_codes(codes)
        if not normalized_codes:
            raise ValueError("at least one Tushare ts_code is required")
        start = _normalize_date(start_date, "start_date")
        end = _normalize_date(end_date, "end_date")
        if start > end:
            raise ValueError("start_date must not be later than end_date")
        client = self._resolve_client()
        calendar_frame = _as_frame(
            client.trade_cal(exchange="", start_date=start, end_date=end, is_open="1"),
            "trade_cal",
        )
        _require_columns(calendar_frame, {"cal_date"}, "trade_cal")
        calendar = sorted(str(item) for item in calendar_frame["cal_date"].dropna().astype(str).unique())
        if len(calendar) < 2:
            raise ValueError("Tushare trade calendar returned fewer than two open sessions")

        market_data: dict[str, pd.DataFrame] = {}
        corporate_actions: dict[str, list[dict[str, Any]]] = {}
        delisting_status: dict[str, dict[str, Any]] = {}
        raw_components: dict[str, Any] = {"trade_cal": _records(calendar_frame)}
        for code in normalized_codes:
            daily = _as_frame(
                client.daily(
                    ts_code=code,
                    start_date=start,
                    end_date=end,
                    fields="ts_code,trade_date,open,high,low,close,vol",
                ),
                f"daily:{code}",
            )
            limits = _as_frame(
                client.stk_limit(ts_code=code, start_date=start, end_date=end),
                f"stk_limit:{code}",
            )
            suspensions = _as_frame(
                client.suspend_d(ts_code=code, start_date=start, end_date=end),
                f"suspend_d:{code}",
            )
            dividends = _as_frame(
                client.dividend(ts_code=code),
                f"dividend:{code}",
            )
            listing = _as_frame(
                client.stock_basic(ts_code=code, fields="ts_code,list_status,delist_date"),
                f"stock_basic:{code}",
            )
            raw_components[code] = {
                "daily": _records(daily),
                "stk_limit": _records(limits),
                "suspend_d": _records(suspensions),
                "dividend": _records(dividends),
                "stock_basic": _records(listing),
            }
            market_data[code] = _build_market_frame(daily, limits, suspensions, calendar)
            events = _build_dividend_events(code, dividends, calendar, start, end)
            if events:
                corporate_actions[code] = events
            delisting_status[code] = _normalize_listing_status(code, listing)

        observed_at = self._now().astimezone(timezone.utc).isoformat()
        archive_id = "sha256:" + _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "raw_source_records": raw_components,
            }
        )
        domains = {
            "trading_calendar": "tushare_pro",
            "eod_bars": "tushare_pro",
            "halts": "tushare_pro",
            "price_limits": "tushare_pro",
            "corporate_actions": "tushare_pro",
            "delistings": "tushare_pro",
        }
        source_manifest = {
            "schema_version": "portfolio_backtest_sources.v1",
            "as_of": observed_at,
            "archive_id": archive_id,
            "domains": domains,
            "license_attestation": {
                "authorized": True,
                "attested_by": self._data_owner,
            },
        }
        return TushareBacktestPacket(
            market_data=market_data,
            trading_calendar=calendar,
            corporate_actions=corporate_actions,
            delisting_status=delisting_status,
            source_manifest=source_manifest,
            price_basis="raw",
            raw_source_records=raw_components,
        )

    def build_listing_universe_snapshot(self, *, as_of_date: str) -> TushareUniverseSnapshotPacket:
        """Build a point-in-time listing universe from active and retired masters.

        This establishes listing membership, not an investable universe.  A
        strategy must still apply its own liquidity, ST, suspension, and other
        eligibility filters before creating target weights.
        """
        as_of = _normalize_date(as_of_date, "as_of_date")
        client = self._resolve_client()
        raw_records: dict[str, Any] = {}
        frames: list[pd.DataFrame] = []
        for list_status in ("L", "D", "P", "G"):
            frame = _as_frame(
                client.stock_basic(
                    exchange="",
                    list_status=list_status,
                    fields="ts_code,list_status,list_date,delist_date",
                ),
                f"stock_basic:{list_status}",
            )
            _require_columns(frame, {"ts_code", "list_status", "list_date", "delist_date"}, f"stock_basic:{list_status}")
            raw_records[f"stock_basic:{list_status}"] = _records(frame)
            frames.append(frame)
        master = pd.concat(frames, ignore_index=True).drop_duplicates("ts_code", keep="last")
        members = _listing_members_as_of(master, as_of)
        if not members:
            raise ValueError(f"Tushare stock master produced no listing-universe members for {as_of}")
        archive_id = "sha256:" + _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "raw_source_records": raw_records,
            }
        )
        return TushareUniverseSnapshotPacket(
            as_of_date=as_of,
            members=members,
            source_ref=f"tushare_pro.stock_basic:{as_of}",
            archive_id=archive_id,
            raw_source_records=raw_records,
        )

    def _resolve_client(self) -> Any:
        if self._client is not None:
            if not self._data_owner:
                raise ValueError("MARKET_DATA_ATTESTED_BY is required for licensed Tushare replay data")
            return self._client
        if not self._token:
            raise ValueError("TUSHARE_TOKEN is required for licensed Tushare replay data")
        if not self._data_owner:
            raise ValueError("MARKET_DATA_ATTESTED_BY is required for licensed Tushare replay data")
        try:
            import tushare  # type: ignore[import-not-found]
        except ImportError as error:
            raise RuntimeError("Install the optional Tushare dependency before requesting Tushare replay data") from error
        return tushare.pro_api(self._token)


def _normalize_codes(codes: Sequence[str]) -> list[str]:
    normalized = []
    for raw_code in codes:
        code = str(raw_code).strip().upper()
        if not code or "." not in code:
            raise ValueError("Tushare replay codes must be qualified ts_code values such as 600460.SH")
        if code not in normalized:
            normalized.append(code)
    return normalized


def _normalize_date(value: str, name: str) -> str:
    parsed = pd.Timestamp(value)
    if pd.isna(parsed):
        raise ValueError(f"{name} must be YYYYMMDD or ISO date")
    return parsed.strftime("%Y%m%d")


def _as_frame(value: Any, name: str) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise ValueError(f"Tushare {name} did not return a DataFrame")
    return value.copy()


def _require_columns(frame: pd.DataFrame, columns: set[str], name: str) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise ValueError(f"Tushare {name} response lacks columns: {', '.join(sorted(missing))}")


def _build_market_frame(
    daily: pd.DataFrame,
    limits: pd.DataFrame,
    suspensions: pd.DataFrame,
    calendar: Sequence[str],
) -> pd.DataFrame:
    _require_columns(daily, {"trade_date", "open", "high", "low", "close", "vol"}, "daily")
    rows = daily.copy()
    rows["trade_date"] = rows["trade_date"].astype(str)
    rows = rows.drop_duplicates("trade_date", keep="last").set_index("trade_date")
    limit_rows = limits.copy()
    if not limit_rows.empty:
        _require_columns(limit_rows, {"trade_date", "up_limit", "down_limit"}, "stk_limit")
        limit_rows["trade_date"] = limit_rows["trade_date"].astype(str)
        limit_rows = limit_rows.drop_duplicates("trade_date", keep="last").set_index("trade_date")
    suspension_days = _suspension_event_days(suspensions)
    normalized: list[dict[str, Any]] = []
    for date in calendar:
        if date not in rows.index:
            continue
        row = rows.loc[date]
        open_price = _numeric(row.get("open"), f"daily open {date}")
        high = _numeric(row.get("high"), f"daily high {date}")
        low = _numeric(row.get("low"), f"daily low {date}")
        close = _numeric(row.get("close"), f"daily close {date}")
        volume = _numeric(row.get("vol"), f"daily volume {date}") * 100
        status = "halted" if volume <= 0 else "tradable"
        if status == "tradable" and date in suspension_days:
            # Tushare records a suspension event for the date, but its daily
            # endpoint does not prove whether the opening auction was usable.
            # A source-correct replay must not invent a next-open fill here.
            status = "unknown"
        if status == "tradable" and date in limit_rows.index:
            limit = limit_rows.loc[date]
            up_limit = _numeric_or_none(limit.get("up_limit"))
            down_limit = _numeric_or_none(limit.get("down_limit"))
            if up_limit is not None and _same_price(open_price, high, low, close, up_limit):
                status = "limit_up_locked"
            elif down_limit is not None and _same_price(open_price, high, low, close, down_limit):
                status = "limit_down_locked"
        normalized.append(
            {
                "date": pd.Timestamp(date),
                "open": open_price,
                "close": close,
                "volume": volume,
                "tradable": status == "tradable",
                "execution_status": status,
            }
        )
    if not normalized:
        raise ValueError("Tushare daily response contains no replayable sessions")
    return pd.DataFrame(normalized)


def _suspension_event_days(frame: pd.DataFrame) -> set[str]:
    if frame.empty:
        return set()
    _require_columns(frame, {"trade_date", "suspend_type"}, "suspend_d")
    return {
        str(row.get("trade_date") or "").strip()
        for _, row in frame.iterrows()
        if str(row.get("suspend_type") or "").strip().upper() == "S"
        and str(row.get("trade_date") or "").strip()
    }


def _build_dividend_events(
    code: str,
    frame: pd.DataFrame,
    calendar: Sequence[str],
    start: str,
    end: str,
) -> list[dict[str, Any]]:
    if frame.empty:
        return []
    required = {"pay_date", "cash_div_tax"}
    _require_columns(frame, required, "dividend")
    sessions = set(calendar)
    events: list[dict[str, Any]] = []
    for index, row in frame.iterrows():
        pay_date = str(row.get("pay_date") or "").strip()
        cash = _numeric_or_none(row.get("cash_div_tax"))
        if pay_date and pay_date in sessions and start <= pay_date <= end and cash is not None and cash > 0:
            events.append(
                {
                    "event_id": f"tushare:{code}:cash_dividend:{pay_date}:{index}",
                    "type": "cash_dividend",
                    "effective_date": pay_date,
                    "cash_per_share": cash,
                    "source_ref": f"tushare_pro.dividend:{code}:{pay_date}",
                }
            )
        ex_date = str(row.get("ex_date") or "").strip()
        share_components = (
            _numeric_or_none(row.get("stk_div")) or 0.0,
            _numeric_or_none(row.get("stk_bo_rate")) or 0.0,
            _numeric_or_none(row.get("stk_co_rate")) or 0.0,
        )
        share_factor = 1 + sum(share_components)
        if ex_date and ex_date in sessions and start <= ex_date <= end and share_factor > 1:
            events.append(
                {
                    "event_id": f"tushare:{code}:share_distribution:{ex_date}:{index}",
                    "type": "share_distribution",
                    "effective_date": ex_date,
                    "share_factor": share_factor,
                    "source_ref": f"tushare_pro.dividend:{code}:{ex_date}",
                    "sequence": 1,
                }
            )
    return events


def _normalize_listing_status(code: str, frame: pd.DataFrame) -> dict[str, Any]:
    if frame.empty:
        return {
            "code": code,
            "list_status": "unknown",
            "delist_date": None,
            "source_ref": f"tushare_pro.stock_basic:{code}",
        }
    _require_columns(frame, {"list_status"}, "stock_basic")
    row = frame.iloc[-1]
    raw_date = row.get("delist_date")
    return {
        "code": code,
        "list_status": str(row.get("list_status") or "unknown").strip().upper(),
        "delist_date": str(raw_date).strip() if pd.notna(raw_date) and str(raw_date).strip() else None,
        "source_ref": f"tushare_pro.stock_basic:{code}",
    }


def _listing_members_as_of(frame: pd.DataFrame, as_of: str) -> list[str]:
    records: list[str] = []
    for _, row in frame.iterrows():
        code = str(row.get("ts_code") or "").strip().upper()
        list_date = str(row.get("list_date") or "").strip()
        delist_date = str(row.get("delist_date") or "").strip()
        if not code or not list_date:
            continue
        if list_date > as_of:
            continue
        if delist_date and delist_date <= as_of:
            continue
        records.append(code)
    return sorted(set(records))


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _numeric(value: Any, label: str) -> float:
    parsed = _numeric_or_none(value)
    if parsed is None:
        raise ValueError(f"{label} must be numeric")
    return parsed


def _numeric_or_none(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if pd.notna(parsed) else None


def _same_price(*values: float) -> bool:
    return max(values) - min(values) <= 1e-8
