"""数据库模块测试"""

import pytest
import pytest_asyncio
from pathlib import Path
import tempfile

from astock.storage import Database, Stock, DailyQuote
from datetime import date


@pytest_asyncio.fixture
async def db():
    """创建临时数据库"""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        database = Database(str(db_path))
        await database.connect()
        await database.init_tables()
        yield database
        await database.close()


@pytest.mark.asyncio
async def test_init_tables(db: Database):
    """测试表初始化"""
    # 应该不会抛出异常
    await db.init_tables()


@pytest.mark.asyncio
async def test_save_and_get_stock(db: Database):
    """测试保存和获取股票信息"""
    stock = Stock(
        code="000001",
        name="平安银行",
        industry="银行"
    )
    await db.save_stock(stock)

    # 验证可以重复保存
    stock2 = Stock(code="000001", name="平安银行", industry="银行")
    await db.save_stock(stock2)


@pytest.mark.asyncio
async def test_save_and_get_daily_quotes(db: Database):
    """测试保存和获取日线行情"""
    quotes = [
        DailyQuote(
            code="000001",
            date=date(2024, 1, 1),
            open=10.0,
            high=10.5,
            low=9.8,
            close=10.2,
            volume=1000000,
            amount=10200000
        ),
        DailyQuote(
            code="000001",
            date=date(2024, 1, 2),
            open=10.2,
            high=10.8,
            low=10.1,
            close=10.6,
            volume=1200000,
            amount=12720000
        )
    ]
    await db.save_daily_quotes(quotes)

    result = await db.get_daily_quotes("000001", limit=10)
    assert len(result) == 2
    assert result[0].date == date(2024, 1, 2)  # 最新的在前
