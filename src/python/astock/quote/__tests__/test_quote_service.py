"""Quote service tests"""

import asyncio

import pytest
import pytest_asyncio
import pandas as pd
from datetime import date
from unittest.mock import AsyncMock, patch
from typer.testing import CliRunner

from astock.quote import QuoteService, AkShareClient
from astock.utils import DataSourceError
from astock import cli
from astock.storage import DailyQuote


@pytest_asyncio.fixture
async def mock_db() -> AsyncMock:
    """Mock database"""
    db = AsyncMock()
    return db


@pytest.fixture
def client() -> AkShareClient:
    """Create client"""
    return AkShareClient()


@pytest.mark.asyncio
async def test_get_realtime_quote(client: AkShareClient) -> None:
    """Test getting realtime quote"""
    # This is an integration test that requires network connection
    try:
        result = await client.get_realtime_quote("000001")
        assert "code" in result
        assert "name" in result
        assert "price" in result
    except Exception as e:
        pytest.skip(f"Network unavailable: {e}")


@pytest.mark.asyncio
async def test_quote_service_get_realtime(mock_db: AsyncMock) -> None:
    """Test quote service getting realtime data"""
    service = QuoteService(mock_db)

    # AkShare (fallback_client) is now the preferred realtime source
    with patch.object(
        service.fallback_client,
        "get_realtime_quote",
        return_value={"code": "000001", "name": "平安银行", "price": 10.5},
    ):
        result = await service.get_realtime("000001")
        assert result["code"] == "000001"
        assert result["price"] == 10.5


@pytest.mark.asyncio
async def test_quote_service_get_realtime_retry_on_transient_error(
    mock_db: AsyncMock,
) -> None:
    """Test that transient network errors trigger retry"""
    service = QuoteService(mock_db)
    mock_get_or_set = AsyncMock(
        side_effect=[
            ConnectionError("Connection aborted"),
            {"code": "000001", "name": "平安银行", "price": 10.5},
        ]
    )
    with patch.object(service._cache, "get_or_set", new=mock_get_or_set):
        result = await service.get_realtime("000001")

    assert result["code"] == "000001"
    assert mock_get_or_set.await_count == 2


@pytest.mark.asyncio
async def test_get_realtime_quote_fallback_to_alternate_source(
    client: AkShareClient,
) -> None:
    """Test fallback to alternate data source when primary fails"""
    fallback_df = pd.DataFrame(
        [
            {
                "代码": "000001",
                "名称": "平安银行",
                "最新价": 10.5,
                "涨跌幅": 1.2,
                "涨跌额": 0.12,
                "成交量": 1000000,
                "成交额": 10000000,
                "最高": 10.8,
                "最低": 10.2,
                "今开": 10.3,
                "昨收": 10.38,
            }
        ]
    )

    # Single-stock Tencent/East Money endpoints return None so the test
    # exercises the full-market spot dataframe fallback path.
    with (
        patch.object(client, "_get_realtime_quote_tencent", return_value=None),
        patch.object(client, "_get_realtime_quote_eastmoney", return_value=None),
        patch(
            "astock.quote.akshare_client.ak.stock_zh_a_spot_em",
            side_effect=ConnectionError("em down"),
        ),
        patch(
            "astock.quote.akshare_client.ak.stock_zh_a_spot", return_value=fallback_df
        ),
    ):
        result = await client.get_realtime_quote("000001")

    assert result["code"] == "000001"
    assert result["name"] == "平安银行"
    assert result["price"] == 10.5


def test_quote_cli_handles_data_source_error_without_traceback() -> None:
    """Test quote command returns readable error on data source exception"""
    runner = CliRunner()

    with patch(
        "astock.cli.capabilities.get_quote",
        new=AsyncMock(
            side_effect=DataSourceError(
                "获取实时行情失败: 网络错误", source="akshare", code="000001"
            )
        ),
    ):
        result = runner.invoke(cli.app, ["quote", "000001", "--json"])

    assert result.exit_code == 1
    assert "Traceback" not in result.stdout
    assert "获取实时行情失败" in result.stdout


@pytest.mark.asyncio
async def test_quote_service_get_daily_retry_on_transient_error(
    mock_db: AsyncMock,
) -> None:
    """Test that transient network errors trigger retry when getting daily data"""
    service = QuoteService(mock_db)
    fallback_df = pd.DataFrame(
        [
            {
                "date": "2026-03-06",
                "open": 10.1,
                "high": 10.3,
                "low": 9.9,
                "close": 10.2,
                "volume": 1000000,
                "amount": 10000000,
            }
        ]
    )
    mock_get_or_set = AsyncMock(
        side_effect=[ConnectionError("daily down"), fallback_df]
    )
    with patch.object(service._cache, "get_or_set", new=mock_get_or_set):
        result = await service.get_daily("000001", save=False)

    assert not result.empty
    assert mock_get_or_set.await_count == 2


@pytest.mark.asyncio
async def test_get_daily_skips_a_hung_unbounded_primary_source_and_uses_akshare(
    mock_db: AsyncMock,
) -> None:
    service = QuoteService(mock_db)
    service._daily_source_timeout_seconds = 0.01

    async def never_returns(*_: object, **__: object) -> pd.DataFrame:
        await asyncio.Event().wait()
        raise AssertionError("unreachable")

    fallback_df = pd.DataFrame(
        [{"date": "2026-03-06", "open": 10.1, "high": 10.3, "low": 9.9, "close": 10.2, "volume": 1_000, "amount": 10_200}]
    )
    service.primary_client.get_daily_quotes = AsyncMock(side_effect=never_returns)
    service.fallback_client.get_daily_quotes = AsyncMock(return_value=fallback_df)

    result = await asyncio.wait_for(
        service.get_daily("600123", save=False, limit=10), timeout=0.1
    )

    assert result.equals(fallback_df)
    service.primary_client.get_daily_quotes.assert_not_awaited()
    service.fallback_client.get_daily_quotes.assert_awaited_once()


def test_analyze_cli_handles_data_source_error_without_traceback() -> None:
    """Test analyze command returns readable error on data source exception"""
    runner = CliRunner()

    with patch(
        "astock.cli.capabilities.analyze_stock",
        new=AsyncMock(
            side_effect=DataSourceError(
                "获取日线数据失败: 网络错误", source="akshare", code="000001"
            )
        ),
    ):
        result = runner.invoke(cli.app, ["analyze", "000001", "--json"])

    assert result.exit_code == 1
    assert "Traceback" not in result.stdout
    assert "获取日线数据失败" in result.stdout


@pytest.mark.asyncio
async def test_quote_service_get_daily_fallback_to_db_when_network_fails(
    mock_db: AsyncMock,
) -> None:
    service = QuoteService(mock_db)
    mock_db.get_daily_quotes = AsyncMock(
        return_value=[
            DailyQuote(
                code="000001",
                date=date(2026, 3, 5),
                open=10.0,
                high=10.2,
                low=9.8,
                close=10.1,
                volume=1000000,
                amount=10000000,
            ),
            DailyQuote(
                code="000001",
                date=date(2026, 3, 6),
                open=10.1,
                high=10.3,
                low=9.9,
                close=10.2,
                volume=1100000,
                amount=11000000,
            ),
        ]
    )
    with patch.object(
        service._cache,
        "get_or_set",
        new=AsyncMock(side_effect=ConnectionError("daily down")),
    ):
        result = await service.get_daily("000001", save=False, limit=10)

    assert len(result) == 2
    assert list(result["date"]) == [date(2026, 3, 5), date(2026, 3, 6)]


@pytest.mark.asyncio
async def test_get_daily_quotes_uses_timeout_bound_eastmoney_history(client: AkShareClient) -> None:
    history_df = pd.DataFrame(
        [
            {
                "date": "2026-03-05",
                "open": 10.0,
                "high": 10.2,
                "low": 9.8,
                "close": 10.1,
                "volume": 1000000,
                "amount": 10000000,
            }
        ]
    )

    with patch(
        "astock.quote.akshare_client.ak.stock_zh_a_hist", return_value=history_df
    ) as history:
        result = await client.get_daily_quotes("600589")

    assert history.call_args.kwargs["timeout"] == client._daily_history_timeout_seconds
    assert not result.empty
    assert list(result.columns) == [
        "date",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
    ]


@pytest.mark.asyncio
async def test_get_daily_quotes_filters_string_dates_before_normalization(
    client: AkShareClient,
) -> None:
    daily = pd.DataFrame(
        [
            {"date": "2026-03-04", "open": 9.0, "high": 9.2, "low": 8.9, "close": 9.1, "volume": 1_000, "amount": 9_100},
            {"date": "2026-03-05", "open": 10.0, "high": 10.2, "low": 9.8, "close": 10.1, "volume": 1_000, "amount": 10_100},
            {"date": "2026-03-06", "open": 11.0, "high": 11.2, "low": 10.8, "close": 11.1, "volume": 1_000, "amount": 11_100},
        ]
    )

    with patch("astock.quote.akshare_client.ak.stock_zh_a_hist", return_value=daily):
        result = await client.get_daily_quotes(
            "600589", start_date=date(2026, 3, 5), end_date=date(2026, 3, 5)
        )

    assert result["date"].tolist() == ["2026-03-05"]


@pytest.mark.asyncio
async def test_get_daily_quotes_filters_python_date_values_before_normalization(
    client: AkShareClient,
) -> None:
    daily = pd.DataFrame(
        [
            {"date": date(2026, 3, 4), "open": 9.0, "high": 9.2, "low": 8.9, "close": 9.1, "volume": 1_000, "amount": 9_100},
            {"date": date(2026, 3, 5), "open": 10.0, "high": 10.2, "low": 9.8, "close": 10.1, "volume": 1_000, "amount": 10_100},
            {"date": date(2026, 3, 6), "open": 11.0, "high": 11.2, "low": 10.8, "close": 11.1, "volume": 1_000, "amount": 11_100},
        ]
    )

    result = client._filter_by_date(daily, start_date=date(2026, 3, 5), end_date=date(2026, 3, 5))

    assert result["date"].tolist() == [date(2026, 3, 5)]
