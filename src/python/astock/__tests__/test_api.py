"""API adapter boundary tests."""

import pytest
from fastapi import HTTPException

from astock.api import backtest_stock


@pytest.mark.asyncio
async def test_backtest_requires_an_explicit_legacy_study_strategy() -> None:
    with pytest.raises(HTTPException) as raised:
        await backtest_stock(
            "000001",
            strategy=None,
            capital=100_000,
            quote_service=object(),
        )

    assert raised.value.status_code == 400
    assert "must be explicit" in str(raised.value.detail)
