from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from astock.strategy.cta import run_frozen_public_domestic_futures_cta_backtest
from astock.strategy.data import (
    build_public_domestic_futures_cta_input,
    parse_public_domestic_futures_cta_input,
)


def _raw_frame() -> pd.DataFrame:
    dates = pd.date_range("2025-01-02", periods=170, freq="B")
    price = [100 + index * 0.2 for index in range(len(dates))]
    return pd.DataFrame(
        {
            "日期": dates,
            "开盘价": price,
            "收盘价": price,
            "动态结算价": price,
            "成交量": [100_000] * len(dates),
            "持仓量": [200_000] * len(dates),
        }
    )


@pytest.mark.asyncio
async def test_public_cta_input_freezes_and_detects_tampering(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(
        "astock.strategy.data._fetch_sina_continuous_futures",
        lambda *_: _raw_frame(),
    )
    overrides = {
        "RB0": {
            "instrument_id": "RB0",
            "active_contract": "RB0",
            "exchange": "shfe",
            "group": "black",
            "currency": "CNY",
            "multiplier": 10,
            "tick_size": 1,
            "initial_margin_rate": 0.12,
            "maintenance_margin_rate": 0.10,
            "source_ref": "fixture:dated-contract-facts",
        }
    }

    packet = await build_public_domestic_futures_cta_input(
        ["RB0"],
        start_date="2025-01-01",
        end_date="2025-12-31",
        instrument_overrides=overrides,
        archive_directory=tmp_path,
        observed_at="2025-10-01T15:00:00+08:00",
    )

    parsed = parse_public_domestic_futures_cta_input(packet)
    assert parsed["source_archive_ids"] == [packet["source_manifest"]["archive_id"]]
    assert parsed["instruments"]["RB0"]["contract_lifecycle_coverage"] == "proxy"
    assert Path(packet["source_archive_path"]).exists()
    assert packet["instruments"]["RB0"]["contract_lifecycle_coverage"] == "proxy"

    packet["market_data"]["RB0"][0]["close"] = 99.0
    with pytest.raises(ValueError, match="raw source records"):
        parse_public_domestic_futures_cta_input(packet)


@pytest.mark.asyncio
async def test_public_cta_input_refuses_to_upgrade_continuous_series_to_verified(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "astock.strategy.data._fetch_sina_continuous_futures",
        lambda *_: _raw_frame(),
    )
    with pytest.raises(ValueError, match="cannot be declared verified"):
        await build_public_domestic_futures_cta_input(
            ["RB0"],
            start_date="2025-01-01",
            end_date="2025-12-31",
            instrument_overrides={
                "RB0": {
                    "instrument_id": "RB0",
                    "active_contract": "RB0",
                    "exchange": "shfe",
                    "group": "black",
                    "currency": "CNY",
                    "multiplier": 10,
                    "tick_size": 1,
                    "initial_margin_rate": 0.12,
                    "maintenance_margin_rate": 0.10,
                    "source_ref": "fixture:dated-contract-facts",
                    "contract_lifecycle_coverage": "verified",
                }
            },
            observed_at="2025-10-01T15:00:00+08:00",
        )


def test_public_cta_parser_downcasts_legacy_verified_instrument_to_proxy() -> None:
    packet = {
        "schema_version": "public_domestic_futures_cta_input.v1",
        "market_data": {"RB0": [{"date": "2026-01-01"}]},
        "instruments": {"RB0": {"contract_lifecycle_coverage": "verified"}},
    }
    packet["raw_source_records"] = {
        "market_data": packet["market_data"],
        "instruments": packet["instruments"],
    }
    from astock.strategy.data import _content_hash

    packet["source_manifest"] = {
        "source": "akshare_public_sina_continuous_futures",
        "archive_id": "sha256:"
        + _content_hash(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "akshare_public_sina_continuous_futures",
                "raw_source_records": packet["raw_source_records"],
            }
        ),
    }
    parsed = parse_public_domestic_futures_cta_input(packet)
    assert parsed["instruments"]["RB0"]["contract_lifecycle_coverage"] == "proxy"


def test_frozen_public_cta_replay_is_blocked_without_actual_contract_roll_data(
    tmp_path: Path,
) -> None:
    packet = {
        "schema_version": "public_domestic_futures_cta_input.v1",
        "market_data": {"RB0": [{"date": "2026-01-01"}]},
        "instruments": {"RB0": {"contract_lifecycle_coverage": "proxy"}},
    }
    packet["raw_source_records"] = {
        "market_data": packet["market_data"],
        "instruments": packet["instruments"],
    }
    from astock.strategy.data import _content_hash

    archive_id = "sha256:" + _content_hash(
        {
            "schema_version": "market_data_frozen_archive.v1",
            "source": "akshare_public_sina_continuous_futures",
            "raw_source_records": packet["raw_source_records"],
        }
    )
    packet["source_manifest"] = {
        "source": "akshare_public_sina_continuous_futures",
        "archive_id": archive_id,
    }
    archive_path = tmp_path / f"{archive_id.removeprefix('sha256:')}.json"
    archive_path.write_text(
        __import__("json").dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "akshare_public_sina_continuous_futures",
                "archive_id": archive_id,
                "raw_source_records": packet["raw_source_records"],
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    result = run_frozen_public_domestic_futures_cta_backtest(
        packet,
        source_archive_path=str(archive_path),
        initial_capital=1_000_000,
    )
    assert result["data_assurance"]["status"] == "blocked"
    assert result["trades"] == []
