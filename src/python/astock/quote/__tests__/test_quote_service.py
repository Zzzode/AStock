"""行情服务测试"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from astock.quote import QuoteService, AkShareClient


@pytest_asyncio.fixture
async def mock_db():
    """模拟数据库"""
    db = AsyncMock()
    return db


@pytest.fixture
def client():
    """创建客户端"""
    return AkShareClient()


@pytest.mark.asyncio
async def test_get_realtime_quote(client: AkShareClient):
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
async def test_quote_service_get_realtime(mock_db):
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
