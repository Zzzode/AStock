"""Public-data adapter for bounded domestic-futures CTA research.

The adapter uses AkShare's public continuous-contract history only to create a
source-labelled research packet.  It explicitly does not assert that a
continuous series is a point-in-time rollable contract, that all historical
orders could fill, or that its fields meet a licensed backtest standard.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

from .models import FuturesInstrumentSpec

PUBLIC_DOMESTIC_FUTURES_SOURCE = "akshare_public_sina_continuous_futures"


async def build_public_domestic_futures_cta_input(
    symbols: Sequence[str],
    *,
    start_date: str,
    end_date: str,
    instrument_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    archive_directory: str | Path | None = None,
    observed_at: str | datetime | None = None,
) -> dict[str, Any]:
    """Fetch and freeze a bounded public continuous-futures research packet.

    The caller supplies each instrument's current multiplier, margin and group
    facts through ``instrument_overrides``.  This avoids silently applying a
    generic exchange margin rate or treating an aggregated source as contract
    master data.
    """

    normalized_symbols = [
        str(symbol).strip().upper() for symbol in symbols if str(symbol).strip()
    ]
    if not normalized_symbols or len(set(normalized_symbols)) != len(
        normalized_symbols
    ):
        raise ValueError(
            "symbols must contain unique non-empty continuous-futures identifiers"
        )
    _validate_date(start_date, "start_date")
    _validate_date(end_date, "end_date")
    if start_date > end_date:
        raise ValueError("start_date must not be later than end_date")
    overrides = instrument_overrides or {}
    if set(overrides).difference(normalized_symbols):
        raise ValueError("instrument_overrides contains a symbol outside symbols")
    timestamp = _normalize_timestamp(observed_at)
    frames = await asyncio.gather(
        *(
            asyncio.to_thread(
                _fetch_sina_continuous_futures, symbol, start_date, end_date
            )
            for symbol in normalized_symbols
        )
    )
    market_data: dict[str, list[dict[str, Any]]] = {}
    instruments: dict[str, dict[str, Any]] = {}
    for symbol, frame in zip(normalized_symbols, frames, strict=True):
        override = dict(overrides.get(symbol) or {})
        instrument_id = str(override.pop("instrument_id", symbol)).strip()
        if not instrument_id:
            raise ValueError(f"{symbol} requires an instrument_id")
        requested_lifecycle_coverage = (
            str(override.pop("contract_lifecycle_coverage", "proxy")).strip().lower()
        )
        if requested_lifecycle_coverage != "proxy":
            raise ValueError(
                f"{symbol} is public continuous-series data and must retain "
                "contract_lifecycle_coverage='proxy'; it cannot be declared verified"
            )
        normalized_frame = _normalize_public_frame(frame, instrument_id)
        latest = normalized_frame.iloc[-1]
        spec_value = {
            "instrument_id": instrument_id,
            "active_contract": str(override.pop("active_contract", symbol)).strip(),
            "exchange": str(override.pop("exchange", "unknown")).strip(),
            "group": str(override.pop("group", "unclassified")).strip(),
            "currency": str(override.pop("currency", "CNY")).strip(),
            "multiplier": override.pop("multiplier", None),
            "tick_size": override.pop("tick_size", None),
            "initial_margin_rate": override.pop("initial_margin_rate", None),
            "maintenance_margin_rate": override.pop("maintenance_margin_rate", None),
            "as_of": str(override.pop("as_of", latest["date"][:10])).strip(),
            "source_ref": str(override.pop("source_ref", "")).strip(),
            "max_contracts": override.pop("max_contracts", None),
            "contract_lifecycle_coverage": "proxy",
        }
        if override:
            raise ValueError(
                f"{symbol} contains unsupported instrument override fields: "
                + ", ".join(sorted(override))
            )
        missing = [
            name
            for name in (
                "multiplier",
                "tick_size",
                "initial_margin_rate",
                "maintenance_margin_rate",
                "source_ref",
            )
            if spec_value[name] is None or not str(spec_value[name]).strip()
        ]
        if missing:
            raise ValueError(
                f"{symbol} requires dated contract facts in instrument_overrides: "
                + ", ".join(missing)
            )
        spec = FuturesInstrumentSpec.from_mapping(spec_value)
        market_data[instrument_id] = normalized_frame.to_dict(orient="records")
        instruments[instrument_id] = spec.to_dict()
    raw_source_records = {
        "symbols": normalized_symbols,
        "start_date": start_date,
        "end_date": end_date,
        "observed_at": timestamp,
        "market_data": market_data,
        "instruments": instruments,
    }
    archive_id = "sha256:" + _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": PUBLIC_DOMESTIC_FUTURES_SOURCE,
            "raw_source_records": raw_source_records,
        }
    )
    payload = {
        "schema_version": "public_domestic_futures_cta_input.v1",
        "market_data": market_data,
        "instruments": instruments,
        "raw_source_records": raw_source_records,
        "source_manifest": {
            "schema_version": "public_domestic_futures_cta_sources.v1",
            "source": PUBLIC_DOMESTIC_FUTURES_SOURCE,
            "as_of": timestamp,
            "archive_id": archive_id,
            "domains": {
                "continuous_bars": PUBLIC_DOMESTIC_FUTURES_SOURCE,
                "liquidity_proxy": PUBLIC_DOMESTIC_FUTURES_SOURCE,
                "contract_facts": "caller_source_labelled",
            },
        },
        "limitations": [
            "Public continuous-contract histories are used as a research signal proxy, not proof of historical executable contract rolls.",
            "Contract multiplier, tick, margin, position limits, expiry and broker eligibility must be dated caller-supplied facts before a proposal is produced.",
            "The input does not provide licensed point-in-time contracts, exchange risk-control states, full curves, historical bid/ask, or fill-quality evidence.",
            "The public continuous-series archive is intentionally blocked from P&L replay; it can only support source inspection until dated actual-contract roll coverage is supplied.",
        ],
        "research_only": True,
        "no_order_execution": True,
        "formal_decision_eligible": False,
    }
    if archive_directory is not None:
        target_directory = Path(archive_directory)
        archive_path = _write_archive(
            target_directory,
            source=PUBLIC_DOMESTIC_FUTURES_SOURCE,
            archive_id=archive_id,
            raw_source_records=raw_source_records,
        )
        replay_path = _write_replay_input(target_directory, archive_id, payload)
        payload["source_archive_path"] = str(archive_path)
        payload["replay_input_path"] = str(replay_path)
    return payload


def parse_public_domestic_futures_cta_input(value: Mapping[str, Any]) -> dict[str, Any]:
    """Verify an in-memory public CTA input before a deterministic replay."""

    if (
        not isinstance(value, Mapping)
        or str(value.get("schema_version") or "")
        != "public_domestic_futures_cta_input.v1"
    ):
        raise ValueError(
            "CTA replay input must use public_domestic_futures_cta_input.v1"
        )
    manifest = value.get("source_manifest")
    if (
        not isinstance(manifest, Mapping)
        or str(manifest.get("source") or "") != PUBLIC_DOMESTIC_FUTURES_SOURCE
    ):
        raise ValueError(
            "CTA replay input requires the expected public source manifest"
        )
    market_data = value.get("market_data")
    instruments = value.get("instruments")
    raw_source_records = value.get("raw_source_records")
    if (
        not isinstance(market_data, Mapping)
        or not isinstance(instruments, Mapping)
        or not isinstance(raw_source_records, Mapping)
    ):
        raise TypeError(
            "CTA replay input requires market_data, instruments, and raw_source_records mappings"
        )
    expected_archive_id = "sha256:" + _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": PUBLIC_DOMESTIC_FUTURES_SOURCE,
            "raw_source_records": raw_source_records,
        }
    )
    if str(manifest.get("archive_id") or "") != expected_archive_id:
        raise ValueError(
            "CTA replay input archive_id does not match its raw source records"
        )
    if (
        raw_source_records.get("market_data") != market_data
        or raw_source_records.get("instruments") != instruments
    ):
        raise ValueError(
            "CTA replay input market_data or instruments do not match its raw source records"
        )
    normalized_instruments = {
        str(instrument_id): _public_proxy_instrument(specification)
        for instrument_id, specification in instruments.items()
    }
    return {
        "market_data": dict(market_data),
        "instruments": normalized_instruments,
        "source_archive_ids": [str(manifest.get("archive_id") or "")],
    }


def _public_proxy_instrument(value: Any) -> dict[str, Any]:
    """Ensure even legacy public archives cannot upgrade themselves to executable facts."""

    if not isinstance(value, Mapping):
        raise TypeError("CTA replay instruments must be mappings")
    normalized = dict(value)
    normalized["contract_lifecycle_coverage"] = "proxy"
    return normalized


def _fetch_sina_continuous_futures(
    symbol: str, start_date: str, end_date: str
) -> pd.DataFrame:
    import akshare as ak

    try:
        frame = ak.futures_main_sina(
            symbol=symbol,
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
        )
    except Exception as error:
        raise ValueError(
            f"public continuous-futures fetch failed for {symbol}: {type(error).__name__}: {error}"
        ) from error
    if not isinstance(frame, pd.DataFrame) or frame.empty:
        raise ValueError(
            f"public continuous-futures source returned no bars for {symbol}"
        )
    return frame


def _normalize_public_frame(frame: pd.DataFrame, instrument_id: str) -> pd.DataFrame:
    columns = {
        "日期": "date",
        "开盘价": "open",
        "收盘价": "close",
        "动态结算价": "settlement",
        "成交量": "volume",
        "持仓量": "open_interest",
    }
    normalized = frame.rename(
        columns={
            source: target
            for source, target in columns.items()
            if source in frame.columns
        }
    )
    required = {"date", "open", "close", "settlement", "volume", "open_interest"}
    missing = sorted(required.difference(normalized.columns))
    if missing:
        raise ValueError(
            f"public continuous-futures source for {instrument_id} lacks: "
            + ", ".join(missing)
        )
    normalized = normalized[
        ["date", "open", "close", "settlement", "volume", "open_interest"]
    ].copy()
    normalized["date"] = pd.to_datetime(
        normalized["date"], errors="coerce"
    ).dt.normalize()
    for name in ("open", "close", "settlement", "volume", "open_interest"):
        normalized[name] = pd.to_numeric(normalized[name], errors="coerce")
    normalized = normalized.dropna().sort_values("date", kind="stable")
    if (
        normalized.empty
        or normalized["date"].duplicated().any()
        or (normalized[["open", "close", "settlement"]] <= 0).any().any()
    ):
        raise ValueError(
            f"public continuous-futures source contains invalid data for {instrument_id}"
        )
    normalized["tradable"] = True
    normalized["execution_status"] = "tradable"
    # A caller must replace this proxy with exchange/broker expiry facts.  A
    # very large value prevents accidental interpretation as a near-delivery
    # contract while the explicit warning remains in the packet.
    normalized["days_to_expiry"] = 9_999
    normalized["date"] = normalized["date"].dt.strftime("%Y-%m-%d")
    return normalized.reset_index(drop=True)


def _validate_date(value: str, field_name: str) -> None:
    try:
        datetime.fromisoformat(str(value)).date()
    except ValueError as error:
        raise ValueError(f"{field_name} must use YYYY-MM-DD") from error


def _normalize_timestamp(value: str | datetime | None) -> str:
    if value is None:
        timestamp = datetime.now(UTC)
    elif isinstance(value, datetime):
        timestamp = value
    else:
        try:
            timestamp = datetime.fromisoformat(str(value))
        except ValueError as error:
            raise ValueError("observed_at must be ISO-8601") from error
    if timestamp.tzinfo is None:
        raise ValueError("observed_at must include a timezone")
    return timestamp.astimezone(UTC).isoformat()


def _content_hash(value: Mapping[str, Any]) -> str:
    canonical = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _write_archive(
    directory: Path,
    *,
    source: str,
    archive_id: str,
    raw_source_records: Mapping[str, Any],
) -> Path:
    digest = archive_id.removeprefix("sha256:")
    payload = {
        "schema_version": "market_data_frozen_archive.v1",
        "source": source,
        "archive_id": archive_id,
        "raw_source_records": raw_source_records,
    }
    return _write_content_addressed(directory, f"{digest}.json", payload)


def _write_replay_input(
    directory: Path, archive_id: str, payload: Mapping[str, Any]
) -> Path:
    return _write_content_addressed(
        directory, f"{archive_id.removeprefix('sha256:')}.cta.replay.json", payload
    )


def _write_content_addressed(
    directory: Path, filename: str, payload: Mapping[str, Any]
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / filename
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
    )
    if target.exists():
        if target.read_text(encoding="utf-8") != canonical:
            raise ValueError(f"frozen archive collision at {target}")
        return target
    temporary = directory / f".{filename}.tmp"
    temporary.write_text(canonical, encoding="utf-8")
    temporary.replace(target)
    return target
