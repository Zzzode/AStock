"""行情服务测试"""

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
    """模拟数据库"""
    db = AsyncMock()
    return db


@pytest.fixture
def client() -> AkShareClient:
    """创建客户端"""
    return AkShareClient()


@pytest.mark.asyncio
async def test_get_realtime_quote(client: AkShareClient) -> None:
    """测试获取实时行情"""
    # 这是一个集成测试，需要网络连接
    try:
        result = await client.get_realtime_quote("000001")
        assert "code" in result
        assert "name" in result
        assert "price" in result
    except Exception as e:
        pytest.skip(f"网络不可用: {e}")


@pytest.mark.asyncio
async def test_quote_service_get_realtime(mock_db: AsyncMock) -> None:
    """测试行情服务获取实时数据"""
    service = QuoteService(mock_db)

    with patch.object(
        service.client,
        "get_realtime_quote",
        return_value={"code": "000001", "name": "平安银行", "price": 10.5}
    ):
        result = await service.get_realtime("000001")
        assert result["code"] == "000001"
        assert result["price"] == 10.5


@pytest.mark.asyncio
async def test_quote_service_get_realtime_retry_on_transient_error(mock_db: AsyncMock) -> None:
    """测试临时网络错误会重试"""
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
async def test_get_realtime_quote_fallback_to_alternate_source(client: AkShareClient) -> None:
    """测试主数据源失败时回退备用数据源"""
    fallback_df = pd.DataFrame([
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
    ])

    with (
        patch("astock.quote.akshare_client.ak.stock_zh_a_spot_em", side_effect=ConnectionError("em down")),
        patch("astock.quote.akshare_client.ak.stock_zh_a_spot", return_value=fallback_df),
    ):
        result = await client.get_realtime_quote("000001")

    assert result["code"] == "000001"
    assert result["name"] == "平安银行"
    assert result["price"] == 10.5


def test_quote_cli_handles_data_source_error_without_traceback() -> None:
    """测试 quote 命令遇到数据源异常时返回可读错误"""
    runner = CliRunner()

    with patch(
        "astock.cli.QuoteService.get_realtime",
        new=AsyncMock(side_effect=DataSourceError("获取实时行情失败: 网络错误", source="akshare", code="000001")),
    ):
        result = runner.invoke(cli.app, ["quote", "000001", "--json"])

    assert result.exit_code == 1
    assert "Traceback" not in result.stdout
    assert "获取实时行情失败" in result.stdout


@pytest.mark.asyncio
async def test_quote_service_get_daily_retry_on_transient_error(mock_db: AsyncMock) -> None:
    """测试获取日线遇到临时网络错误会重试"""
    service = QuoteService(mock_db)
    fallback_df = pd.DataFrame([
        {
            "date": "2026-03-06",
            "open": 10.1,
            "high": 10.3,
            "low": 9.9,
            "close": 10.2,
            "volume": 1000000,
            "amount": 10000000,
        }
    ])
    mock_get_or_set = AsyncMock(side_effect=[ConnectionError("daily down"), fallback_df])
    with patch.object(service._cache, "get_or_set", new=mock_get_or_set):
        result = await service.get_daily("000001", save=False)

    assert not result.empty
    assert mock_get_or_set.await_count == 2


def test_analyze_cli_handles_data_source_error_without_traceback() -> None:
    """测试 analyze 命令遇到数据源异常时返回可读错误"""
    runner = CliRunner()

    with patch(
        "astock.cli.QuoteService.get_daily",
        new=AsyncMock(side_effect=DataSourceError("获取日线数据失败: 网络错误", source="akshare", code="000001")),
    ):
        result = runner.invoke(cli.app, ["analyze", "000001", "--json"])

    assert result.exit_code == 1
    assert "Traceback" not in result.stdout
    assert "获取日线数据失败" in result.stdout


@pytest.mark.asyncio
async def test_quote_service_get_daily_fallback_to_db_when_network_fails(mock_db: AsyncMock) -> None:
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
async def test_get_daily_quotes_fallback_to_daily_source(client: AkShareClient) -> None:
    fallback_df = pd.DataFrame(
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

    with (
        patch("astock.quote.akshare_client.ak.stock_zh_a_hist", side_effect=ConnectionError("em down")),
        patch("astock.quote.akshare_client.ak.stock_zh_a_daily", return_value=fallback_df),
    ):
        result = await client.get_daily_quotes("600589")

    assert not result.empty
    assert list(result.columns) == ["date", "open", "high", "low", "close", "volume", "amount"]
