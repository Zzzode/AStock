"""数据库模块测试"""

import pytest
import pytest_asyncio
from pathlib import Path
import tempfile

from astock.storage import Database, Stock, DailyQuote, WatchItem, AlertRecord
from datetime import date, datetime


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


@pytest.mark.asyncio
async def test_save_and_get_watch_items(db: Database):
    """测试保存和获取监控项"""
    item = WatchItem(
        code="000001",
        name="平安银行",
        conditions={"price_above": 10.0, "volume_ratio": 2.0},
        alert_channels=["terminal", "email"],
        enabled=True,
        created_at=datetime(2024, 1, 1, 10, 0, 0)
    )
    await db.save_watch_item(item)

    # 获取所有启用的监控项
    items = await db.get_watch_items(enabled_only=True)
    assert len(items) == 1
    assert items[0].code == "000001"
    assert items[0].conditions == {"price_above": 10.0, "volume_ratio": 2.0}
    assert items[0].alert_channels == ["terminal", "email"]
    assert items[0].enabled is True

    # 获取所有监控项（包括禁用的）
    all_items = await db.get_watch_items(enabled_only=False)
    assert len(all_items) == 1


@pytest.mark.asyncio
async def test_update_watch_item(db: Database):
    """测试更新监控项"""
    item = WatchItem(code="000001", name="平安银行")
    await db.save_watch_item(item)

    # 更新监控项
    updated_item = WatchItem(
        code="000001",
        name="平安银行(更新)",
        conditions={"new_condition": True},
        enabled=False
    )
    await db.save_watch_item(updated_item)

    items = await db.get_watch_items(enabled_only=False)
    assert len(items) == 1
    assert items[0].name == "平安银行(更新)"
    assert items[0].conditions == {"new_condition": True}
    assert items[0].enabled is False


@pytest.mark.asyncio
async def test_delete_watch_item(db: Database):
    """测试删除监控项"""
    item = WatchItem(code="000001", name="平安银行")
    await db.save_watch_item(item)

    await db.delete_watch_item("000001")

    items = await db.get_watch_items(enabled_only=False)
    assert len(items) == 0


@pytest.mark.asyncio
async def test_save_and_get_alert_records(db: Database):
    """测试保存和获取告警记录"""
    record = AlertRecord(
        code="000001",
        signal_type="technical",
        signal_name="金叉",
        message="MACD金叉信号触发",
        level=2,
        triggered_at=datetime(2024, 1, 1, 10, 30, 0),
        status="pending",
        channels=["terminal"]
    )
    record_id = await db.save_alert_record(record)
    assert record_id is not None

    # 获取告警记录
    records = await db.get_alert_records()
    assert len(records) == 1
    assert records[0].code == "000001"
    assert records[0].signal_type == "technical"
    assert records[0].signal_name == "金叉"
    assert records[0].level == 2
    assert records[0].status == "pending"


@pytest.mark.asyncio
async def test_get_alert_records_by_code(db: Database):
    """测试按股票代码获取告警记录"""
    record1 = AlertRecord(
        code="000001",
        signal_type="technical",
        signal_name="信号1",
        message="消息1",
        triggered_at=datetime(2024, 1, 1, 10, 0, 0)
    )
    record2 = AlertRecord(
        code="000002",
        signal_type="technical",
        signal_name="信号2",
        message="消息2",
        triggered_at=datetime(2024, 1, 1, 11, 0, 0)
    )
    await db.save_alert_record(record1)
    await db.save_alert_record(record2)

    # 按代码筛选
    records = await db.get_alert_records(code="000001")
    assert len(records) == 1
    assert records[0].code == "000001"


@pytest.mark.asyncio
async def test_get_alert_records_by_status(db: Database):
    """测试按状态获取告警记录"""
    record1 = AlertRecord(
        code="000001",
        signal_type="technical",
        signal_name="信号1",
        message="消息1",
        triggered_at=datetime(2024, 1, 1, 10, 0, 0),
        status="pending"
    )
    record2 = AlertRecord(
        code="000001",
        signal_type="technical",
        signal_name="信号2",
        message="消息2",
        triggered_at=datetime(2024, 1, 1, 11, 0, 0),
        status="sent"
    )
    await db.save_alert_record(record1)
    await db.save_alert_record(record2)

    # 按状态筛选
    pending_records = await db.get_alert_records(status="pending")
    assert len(pending_records) == 1
    assert pending_records[0].status == "pending"


@pytest.mark.asyncio
async def test_update_alert_status(db: Database):
    """测试更新告警记录状态"""
    record = AlertRecord(
        code="000001",
        signal_type="technical",
        signal_name="信号",
        message="消息",
        triggered_at=datetime(2024, 1, 1, 10, 0, 0),
        status="pending"
    )
    record_id = await db.save_alert_record(record)

    # 更新状态
    await db.update_alert_status(record_id, "sent")

    # 验证更新
    records = await db.get_alert_records(code="000001")
    assert len(records) == 1
    assert records[0].status == "sent"
