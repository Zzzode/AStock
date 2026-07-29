"""JQData adapter for source-frozen A-share minute-bar observations.

Minute bars are useful for a short-horizon desk, but they are not a substitute
for tick/order-book data or an executable intraday backtest.  This adapter
therefore produces an observation packet only; consumers must retain that
boundary in their conclusions.
"""

from __future__ import annotations

import hashlib
import json
import os
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Any

import pandas as pd


_REQUIRED_BAR_COLUMNS = {"date", "open", "high", "low", "close", "volume"}


@dataclass(frozen=True)
class JQDataMinuteObservationPacket:
    """A content-addressed, source-labelled minute-bar observation packet."""

    market_data: dict[str, pd.DataFrame]
    source_manifest: dict[str, Any]
    price_basis: str
    raw_source_records: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Return an agent-safe JSON representation of the packet."""
        return {
            "schema_version": "jqdata_minute_observation.v1",
            "market_data": {code: _records(frame) for code, frame in self.market_data.items()},
            "source_manifest": self.source_manifest,
            "price_basis": self.price_basis,
            "limitations": [
                "Minute OHLCV does not prove queue position, auction access, or fill quality.",
                "This packet is not an intraday execution backtest input.",
            ],
        }

    def write_frozen_archive(self, directory: Path) -> Path:
        """Persist the exact vendor responses without overwriting a collision."""
        archive_id = str(self.source_manifest["archive_id"])
        digest = archive_id.removeprefix("sha256:")
        if len(digest) != 64:
            raise ValueError("JQData source manifest has an invalid archive_id")
        expected_digest = _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "jqdata",
                "raw_source_records": self.raw_source_records,
            }
        )
        if digest != expected_digest:
            raise ValueError("JQData source manifest archive_id does not match raw source records")
        payload = {
            "schema_version": "market_data_frozen_archive.v1",
            "source": "jqdata",
            "archive_id": archive_id,
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


class JQDataMinuteAdapter:
    """Fetch licensed JQData minute bars and freeze their exact response."""

    def __init__(
        self,
        *,
        username: str | None = None,
        password: str | None = None,
        data_owner: str | None = None,
        client: Any | None = None,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._username = (username if username is not None else os.environ.get("JQDATA_USERNAME", "")).strip()
        self._password = (password if password is not None else os.environ.get("JQDATA_PASSWORD", "")).strip()
        self._data_owner = (
            data_owner if data_owner is not None else os.environ.get("MARKET_DATA_ATTESTED_BY", "")
        ).strip()
        self._client = client
        self._now = now or (lambda: datetime.now(timezone.utc))

    def build_minute_observation_packet(
        self,
        codes: Sequence[str],
        *,
        start_time: str | datetime | pd.Timestamp,
        end_time: str | datetime | pd.Timestamp,
    ) -> JQDataMinuteObservationPacket:
        """Fetch raw, unadjusted one-minute bars for the requested JQData codes."""
        normalized_codes = _normalize_codes(codes)
        if not normalized_codes:
            raise ValueError("at least one JQData security code is required")
        start = _normalize_timestamp(start_time, "start_time")
        end = _normalize_timestamp(end_time, "end_time")
        if start >= end:
            raise ValueError("start_time must be earlier than end_time")
        client = self._resolve_client()

        market_data: dict[str, pd.DataFrame] = {}
        raw_components: dict[str, Any] = {}
        for code in normalized_codes:
            raw_bars = client.get_bars(
                code,
                unit="1m",
                fields=["date", "open", "high", "low", "close", "volume", "money"],
                include_now=False,
                start_dt=start.to_pydatetime(),
                end_dt=end.to_pydatetime(),
                fq_ref_date=None,
                skip_paused=False,
            )
            bars = _as_frame(raw_bars, f"get_bars:{code}")
            raw_components[code] = _records(bars)
            market_data[code] = _normalize_minute_bars(code, bars, start, end)

        observed_at = self._now().astimezone(timezone.utc).isoformat()
        archive_id = "sha256:" + _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "jqdata",
                "raw_source_records": raw_components,
            }
        )
        return JQDataMinuteObservationPacket(
            market_data=market_data,
            source_manifest={
                "schema_version": "intraday_observation_sources.v1",
                "as_of": observed_at,
                "archive_id": archive_id,
                "domains": {"minute_bars": "jqdata"},
                "license_attestation": {"authorized": True, "attested_by": self._data_owner},
            },
            price_basis="raw",
            raw_source_records=raw_components,
        )

    def _resolve_client(self) -> Any:
        if self._client is not None:
            if not self._data_owner:
                raise ValueError("MARKET_DATA_ATTESTED_BY is required for licensed JQData observations")
            return self._client
        if not self._username or not self._password:
            raise ValueError("JQDATA_USERNAME and JQDATA_PASSWORD are required for licensed JQData observations")
        if not self._data_owner:
            raise ValueError("MARKET_DATA_ATTESTED_BY is required for licensed JQData observations")
        try:
            import jqdatasdk  # type: ignore[import-not-found]
        except ImportError as error:
            raise RuntimeError("Install the optional JQData dependency before requesting minute observations") from error
        authenticated = jqdatasdk.auth(self._username, self._password)
        if authenticated is False:
            raise RuntimeError("JQData authentication was rejected")
        return jqdatasdk


def _normalize_codes(codes: Sequence[str]) -> list[str]:
    normalized: list[str] = []
    for raw_code in codes:
        code = str(raw_code).strip().upper()
        if not code or not code.endswith((".XSHG", ".XSHE")):
            raise ValueError("JQData minute codes must be qualified, e.g. 600460.XSHG or 000001.XSHE")
        if code not in normalized:
            normalized.append(code)
    return normalized


def _normalize_timestamp(value: str | datetime | pd.Timestamp, name: str) -> pd.Timestamp:
    timestamp = pd.Timestamp(value)
    if pd.isna(timestamp):
        raise ValueError(f"{name} must be an ISO timestamp")
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert("Asia/Shanghai").tz_localize(None)
    return timestamp


def _as_frame(value: Any, name: str) -> pd.DataFrame:
    if not isinstance(value, pd.DataFrame):
        raise ValueError(f"JQData {name} did not return a DataFrame")
    return value.copy()


def _normalize_minute_bars(code: str, bars: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    missing = _REQUIRED_BAR_COLUMNS.difference(bars.columns)
    if missing:
        raise ValueError(f"JQData get_bars:{code} response lacks columns: {', '.join(sorted(missing))}")
    normalized = bars.copy()
    normalized["date"] = pd.to_datetime(normalized["date"], errors="coerce")
    if normalized["date"].isna().any():
        raise ValueError(f"JQData get_bars:{code} contains invalid minute timestamps")
    normalized = normalized[(normalized["date"] >= start) & (normalized["date"] <= end)]
    if normalized.empty:
        raise ValueError(f"JQData get_bars:{code} contains no bars in the requested interval")
    if normalized["date"].duplicated().any():
        raise ValueError(f"JQData get_bars:{code} contains duplicate minute timestamps")
    if not normalized["date"].is_monotonic_increasing:
        normalized = normalized.sort_values("date", kind="stable")
    invalid_sessions = [timestamp for timestamp in normalized["date"] if not _is_a_share_continuous_session(timestamp)]
    if invalid_sessions:
        raise ValueError(f"JQData get_bars:{code} contains bars outside A-share continuous sessions")
    for column in ("open", "high", "low", "close", "volume"):
        normalized[column] = pd.to_numeric(normalized[column], errors="coerce")
    if normalized[["open", "high", "low", "close", "volume"]].isna().any().any():
        raise ValueError(f"JQData get_bars:{code} contains non-numeric OHLCV values")
    if (normalized["volume"] < 0).any():
        raise ValueError(f"JQData get_bars:{code} contains negative volume")
    result_columns = ["date", "open", "high", "low", "close", "volume"]
    if "money" in normalized.columns:
        normalized["money"] = pd.to_numeric(normalized["money"], errors="coerce")
        result_columns.append("money")
    return normalized[result_columns].reset_index(drop=True)


def _is_a_share_continuous_session(timestamp: pd.Timestamp) -> bool:
    value = timestamp.time()
    return time(9, 30) <= value <= time(11, 30) or time(13, 0) <= value <= time(15, 0)


def _records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return json.loads(frame.to_json(orient="records", date_format="iso"))


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
