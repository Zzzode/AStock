"""Regression coverage for the cache-only signal-backtest entry point."""

from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import pandas as pd
import pytest

from astock import capabilities
from astock.backtest import build_frozen_signal_replay_input


@pytest.mark.asyncio
async def test_signal_backtest_uses_local_history_without_invoking_quote_network(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path,
) -> None:
    start = date(2026, 1, 2)
    quotes = [
        SimpleNamespace(
            date=start + timedelta(days=index),
            open=10.0 + index * 0.01,
            high=10.2 + index * 0.01,
            low=9.8 + index * 0.01,
            close=10.0 + index * 0.01,
            volume=1_000.0,
            amount=10_000.0,
        )
        for index in range(80)
    ]
    database = MagicMock()
    database.connect = AsyncMock()
    database.close = AsyncMock()
    database.get_daily_quotes = AsyncMock(return_value=quotes)
    monkeypatch.setattr(capabilities, "Database", lambda _: database)
    monkeypatch.setattr(
        capabilities,
        "QuoteService",
        MagicMock(side_effect=AssertionError("network quote service must not be used")),
    )

    result = await capabilities.run_signal_backtest(
        "600460",
        strategy="ma_cross",
        start_date="2026-01-02",
        end_date="2026-03-31",
        db_path=tmp_path / "stocks.db",
    )

    assert "error" not in result
    assert result["data_assurance"]["status"] == "blocked"
    assert result["data_assurance"]["source"] == "local_cache"
    database.get_daily_quotes.assert_awaited_once_with("600460", limit=10_000)


def test_frozen_signal_replay_verifies_exact_archived_input(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-02", periods=80, freq="B"),
            "open": [10.0 + index * 0.01 for index in range(80)],
            "high": [10.2 + index * 0.01 for index in range(80)],
            "low": [9.8 + index * 0.01 for index in range(80)],
            "close": [10.0 + index * 0.01 for index in range(80)],
            "volume": [1_000.0] * 80,
        }
    )
    packet = build_frozen_signal_replay_input(
        "600460",
        frame,
        source="local_cache",
        observed_at="2026-07-28T15:00:00+08:00",
    )
    archive_path = packet.write_frozen_archive(tmp_path)
    assert packet.write_replay_input(tmp_path).name.endswith(".replay.json")

    result = capabilities.run_frozen_signal_backtest(
        packet.to_dict(),
        strategy="ma_cross",
        source_archive_path=archive_path,
    )

    assert result["data_assurance"]["status"] == "pass"
    assert result["data_assurance"]["scope"] == "exact_input_replay"
    assert result["methodology_assurance"]["status"] == "blocked"
    assert result["research_only"] is True


def test_frozen_signal_replay_binds_rolling_model_selection_to_archive(tmp_path) -> None:
    frame = pd.DataFrame(
        {
            "date": pd.date_range("2026-01-02", periods=100, freq="B"),
            "open": [10.0 + index * 0.03 for index in range(100)],
            "high": [10.2 + index * 0.03 for index in range(100)],
            "low": [9.8 + index * 0.03 for index in range(100)],
            "close": [10.0 + index * 0.03 + ((index % 7) - 3) * 0.1 for index in range(100)],
            "volume": [1_000.0] * 100,
        }
    )
    packet = build_frozen_signal_replay_input(
        "600460", frame, source="local_cache", observed_at="2026-07-28T15:00:00+08:00"
    )
    archive_path = packet.write_frozen_archive(tmp_path)

    result = capabilities.run_frozen_signal_backtest(
        packet.to_dict(),
        strategy="ma_cross",
        source_archive_path=archive_path,
        walk_forward_train_bars=40,
        walk_forward_test_bars=20,
        candidate_parameter_sets=[
            {"short_period": 3, "long_period": 8},
            {"short_period": 5, "long_period": 15},
        ],
    )

    assert result["schema_version"] == "rolling_model_selection.v1"
    assert result["data_assurance"]["status"] == "pass"
    assert result["formal_decision_eligible"] is False
    assert result["folds"][0]["training_end"] < result["folds"][0]["testing_start"]
