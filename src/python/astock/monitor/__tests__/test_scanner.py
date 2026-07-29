"""Market-structure scanner tests."""

from unittest.mock import AsyncMock

import pandas as pd
import pytest

from astock.monitor.scanner import SignalScanner


@pytest.mark.asyncio
async def test_scanner_emits_only_market_structure_alert_categories() -> None:
    history = pd.DataFrame(
        {
            "open": [100.0] * 21,
            "high": [101.0] * 21,
            "low": [99.0] * 21,
            "close": [100.0] * 21,
            "volume": [100.0] * 21,
            "amount": [10_000.0] * 21,
        }
    )
    history.loc[20] = {
        "open": 100.0,
        "high": 108.0,
        "low": 99.0,
        "close": 107.0,
        "volume": 300.0,
        "amount": 30_000.0,
    }
    quote_service = AsyncMock()
    quote_service.get_daily.return_value = history

    result = await SignalScanner(quote_service).scan_stock("000001")

    assert {signal["type"] for signal in result["signals"]} == {
        "price_dislocation",
        "range_expansion",
        "volume_spike",
    }
    assert result["level"] == 1
    emitted = " ".join(signal["type"] for signal in result["signals"]).lower()
    assert all(token not in emitted for token in ("ma", "macd", "kdj", "rsi"))
