from __future__ import annotations

import json

import numpy as np
import pandas as pd
from astock.strategy import CryptoTimeSeriesMomentumConfig
from astock.strategy.crypto import _build_crypto_time_series_momentum_proposal


def _bars(
    *,
    direction: float,
    periods: int = 100,
    start: float = 100.0,
    venue_source: str = "fixture:ohlcv",
) -> list[dict[str, object]]:
    timestamps = pd.date_range("2026-01-01T00:00:00Z", periods=periods, freq="24h")
    returns = direction * 0.004 + np.sin(np.arange(periods) / 5.0) * 0.0005
    close = start * np.exp(np.cumsum(returns))
    return [
        {
            "timestamp": timestamp.isoformat(),
            "available_at": (timestamp + pd.Timedelta(hours=1)).isoformat(),
            "open": float(price * 0.999),
            "high": float(price * 1.002),
            "low": float(price * 0.998),
            "close": float(price),
            "volume": 100_000.0,
            "quote_volume": float(price * 100_000.0),
            "tradable": True,
            "source_ref": venue_source,
        }
        for timestamp, price in zip(timestamps, close, strict=True)
    ]


def _asset(
    asset_id: str,
    symbol: str,
    venue: str,
    market_type: str,
    *,
    point_in_time_coverage: str = "verified",
    is_stablecoin: bool = False,
) -> dict[str, object]:
    return {
        "asset_id": asset_id,
        "symbol": symbol,
        "venue": venue,
        "market_type": market_type,
        "quote_currency": "USDT",
        "source_ref": f"fixture:asset:{asset_id}",
        "metadata_as_of": "2026-04-10T01:00:00+00:00",
        "data_quality": "point_in_time_verified",
        "point_in_time_coverage": point_in_time_coverage,
        "eligible": True,
        "trading_status": "tradable",
        "short_eligible": market_type == "perpetual",
        "is_stablecoin": is_stablecoin,
        "listing_age_days": 1_000,
    }


def _funding(asset_id: str) -> list[dict[str, object]]:
    timestamps = pd.date_range(end="2026-04-10T00:00:00Z", periods=5, freq="8h")
    return [
        {
            "timestamp": timestamp.isoformat(),
            "available_at": (timestamp + pd.Timedelta(minutes=5)).isoformat(),
            "funding_rate": 0.0001,
            "source_ref": f"fixture:funding:{asset_id}",
            "data_quality": "point_in_time_verified",
        }
        for timestamp in timestamps
    ]


def _config(**updates: object) -> CryptoTimeSeriesMomentumConfig:
    values: dict[str, object] = {
        "signal_windows": (7, 21, 63),
        "signal_weights": (0.4, 0.35, 0.25),
        "volatility_lookback": 20,
        "minimum_history": 90,
        "entry_threshold": 0.10,
        "exit_threshold": 0.05,
        "annual_target_volatility": 0.20,
        "max_single_asset_exposure": 0.20,
        "max_total_gross_exposure": 0.45,
        "max_exchange_gross_exposure": 0.30,
        "minimum_bar_quote_volume": 1_000.0,
        "minimum_listing_age_days": 30,
        "maximum_bar_age_hours": 30.0,
        "maximum_metadata_age_hours": 36.0,
        "maximum_funding_age_hours": 30.0,
    }
    values.update(updates)
    return CryptoTimeSeriesMomentumConfig(**values)


def _as_of() -> str:
    return "2026-04-10T02:00:00+00:00"


def test_crypto_proposal_generates_source_labelled_signed_paper_targets() -> None:
    market_data = {
        "BTC-PERP": _bars(direction=1.0, venue_source="fixture:btc-bars"),
        "ETH-SPOT": _bars(direction=1.0, start=50.0, venue_source="fixture:eth-bars"),
        "SOL-PERP": _bars(direction=-1.0, start=200.0, venue_source="fixture:sol-bars"),
    }
    assets = {
        "BTC-PERP": _asset("BTC-PERP", "BTC/USDT:USDT", "venue-a", "perpetual"),
        "ETH-SPOT": _asset("ETH-SPOT", "ETH/USDT", "venue-b", "spot"),
        "SOL-PERP": _asset("SOL-PERP", "SOL/USDT:USDT", "venue-c", "perpetual"),
    }
    result = _build_crypto_time_series_momentum_proposal(
        market_data,
        assets,
        as_of=_as_of(),
        funding_data={
            "BTC-PERP": _funding("BTC-PERP"),
            "SOL-PERP": _funding("SOL-PERP"),
        },
        config=_config(),
        source_refs=["fixture:proposal-input"],
        source_archive_ids=["sha256:crypto-fixture"],
    )

    targets = {target["asset_id"]: target for target in result["targets"]}
    assert targets["BTC-PERP"]["target_weight"] > 0
    assert targets["ETH-SPOT"]["target_weight"] > 0
    assert targets["SOL-PERP"]["target_weight"] < 0
    assert all(
        target["asset_class"] == "crypto"
        and target["asset_id"]
        and target["symbol"]
        and target["venue"]
        and target["source_ref"]
        for target in result["targets"]
    )
    assert result["gross_target_weight"] <= 0.45 + 1e-8
    assert result["cash_residual"]["target_weight"] == result["cash_weight"]
    assert result["data_quality"] == "point_in_time_verified"
    assert result["research_only"] is True
    assert result["no_order_execution"] is True
    json.dumps(result)


def test_crypto_proposal_blocks_bar_not_available_at_point_in_time_cutoff() -> None:
    bars = _bars(direction=1.0)
    bars[-1]["available_at"] = "2026-04-10T03:00:00+00:00"
    result = _build_crypto_time_series_momentum_proposal(
        {"BTC-PERP": bars},
        {"BTC-PERP": _asset("BTC-PERP", "BTC/USDT:USDT", "venue-a", "perpetual")},
        as_of=_as_of(),
        funding_data={"BTC-PERP": _funding("BTC-PERP")},
        config=_config(),
    )

    assert result["targets"] == []
    assert result["data_quality"] == "blocked"
    assert result["blockers"][0]["gate"] == "point_in_time"
    assert "not available" in result["blockers"][0]["reason"]


def test_crypto_proposal_blocks_perpetual_when_required_funding_is_missing() -> None:
    result = _build_crypto_time_series_momentum_proposal(
        {
            "BTC-PERP": _bars(direction=1.0),
            "ETH-SPOT": _bars(direction=1.0, start=50.0),
        },
        {
            "BTC-PERP": _asset("BTC-PERP", "BTC/USDT:USDT", "venue-a", "perpetual"),
            "ETH-SPOT": _asset("ETH-SPOT", "ETH/USDT", "venue-b", "spot"),
        },
        as_of=_as_of(),
        config=_config(),
    )

    assert [target["asset_id"] for target in result["targets"]] == ["ETH-SPOT"]
    assert result["data_quality"] == "degraded"
    assert any(blocker["gate"] == "funding_quality" for blocker in result["blockers"])


def test_crypto_proposal_applies_exchange_concentration_cap() -> None:
    result = _build_crypto_time_series_momentum_proposal(
        {
            "BTC-SPOT": _bars(direction=1.0),
            "ETH-SPOT": _bars(direction=1.0, start=50.0),
        },
        {
            "BTC-SPOT": _asset("BTC-SPOT", "BTC/USDT", "venue-a", "spot"),
            "ETH-SPOT": _asset("ETH-SPOT", "ETH/USDT", "venue-a", "spot"),
        },
        as_of=_as_of(),
        config=_config(max_exchange_gross_exposure=0.22),
    )

    concentration = result["venue_concentration"]
    assert concentration == [
        {
            "venue": "venue-a",
            "gross_exposure": 0.22,
            "uncapped_gross_exposure": 0.4,
            "max_exchange_gross_exposure": 0.22,
            "status": "capped",
        }
    ]
    assert (
        sum(abs(target["target_weight"]) for target in result["targets"]) <= 0.22 + 1e-8
    )


def test_crypto_proposal_enforces_asset_point_in_time_eligibility() -> None:
    result = _build_crypto_time_series_momentum_proposal(
        {"USDT-SPOT": _bars(direction=1.0)},
        {
            "USDT-SPOT": _asset(
                "USDT-SPOT",
                "USDT/USDC",
                "venue-a",
                "spot",
                point_in_time_coverage="partial",
                is_stablecoin=True,
            )
        },
        as_of=_as_of(),
        config=_config(),
    )

    assert result["targets"] == []
    assert result["data_quality"] == "blocked"
    assert result["blockers"][0]["gate"] == "asset_eligibility"
    assert "stablecoins" in result["blockers"][0]["reason"]


def test_crypto_proposal_rejects_naive_24x7_bar_timestamps() -> None:
    bars = _bars(direction=1.0)
    for row in bars:
        row["timestamp"] = str(row["timestamp"]).replace("+00:00", "")
    result = _build_crypto_time_series_momentum_proposal(
        {"ETH-SPOT": bars},
        {"ETH-SPOT": _asset("ETH-SPOT", "ETH/USDT", "venue-a", "spot")},
        as_of=_as_of(),
        config=_config(),
    )

    assert result["targets"] == []
    assert result["blockers"][0]["gate"] == "point_in_time"
    assert "timezone-aware" in result["blockers"][0]["reason"]
