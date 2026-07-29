"""Analysis service regression tests."""

from datetime import date, timedelta
from unittest.mock import AsyncMock

import numpy as np
import pandas as pd
import pytest

from astock.services.analysis_service import AnalysisService


def _daily_frame() -> pd.DataFrame:
    """Return deterministic daily price-and-volume observations."""
    count = 100
    close = 10 + np.linspace(0, 2, count)
    dates = [date(2026, 1, 1) + timedelta(days=index) for index in range(count)]
    return pd.DataFrame(
        {
            "date": dates,
            "open": close - 0.1,
            "high": close + 0.2,
            "low": close - 0.2,
            "close": close,
            "volume": np.full(count, 1_000_000),
        }
    )


@pytest.mark.asyncio
async def test_analysis_uses_quote_name_without_remote_stock_info_lookup() -> None:
    """Price observations must not block on an unbounded stock-list request."""
    quote_service = AsyncMock()
    quote_service.get_daily.return_value = _daily_frame()
    quote_service.get_realtime.return_value = {
        "code": "600460",
        "name": "士兰微",
        "price": 28.79,
        "data_quality": "full_realtime",
    }
    quote_service.get_stock_info.side_effect = AssertionError(
        "analysis must not fetch the remote stock list for a display name"
    )

    service = AnalysisService(
        AsyncMock(),
        quote_service=quote_service,
    )

    result = await service.analyze("600460")

    assert result.error is None
    assert result.name == "士兰微"
    assert result.indicators["close"] == pytest.approx(12.0)
    assert "rsi6" not in result.indicators
    quote_service.get_stock_info.assert_not_awaited()
