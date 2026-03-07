"""SQLite 数据库管理"""

import aiosqlite
from pathlib import Path
from typing import Optional

from .models import Stock, DailyQuote, WatchItem, AlertRecord


class Database:
    """异步 SQLite 数据库管理器"""

    def __init__(self, db_path: str = "data/stocks.db"):
        self.db_path = Path(db_path)
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """连接数据库"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row

    async def close(self) -> None:
        """关闭数据库连接"""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def init_tables(self) -> None:
        """初始化数据表"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.executescript("""
            -- 股票基础信息
            CREATE TABLE IF NOT EXISTS stocks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                list_date DATE
            );

            -- 日线行情
            CREATE TABLE IF NOT EXISTS daily_quotes (
                code TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL NOT NULL,
                high REAL NOT NULL,
                low REAL NOT NULL,
                close REAL NOT NULL,
                volume REAL NOT NULL,
                amount REAL NOT NULL,
                PRIMARY KEY (code, date)
            );

            -- 创建索引
            CREATE INDEX IF NOT EXISTS idx_daily_quotes_date
                ON daily_quotes(date);

            -- 监控项
            CREATE TABLE IF NOT EXISTS watch_items (
                code TEXT PRIMARY KEY,
                name TEXT,
                conditions TEXT NOT NULL DEFAULT '{}',
                alert_channels TEXT NOT NULL DEFAULT '["terminal"]',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME
            );

            -- 告警记录
            CREATE TABLE IF NOT EXISTS alert_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                signal_type TEXT NOT NULL,
                signal_name TEXT NOT NULL,
                message TEXT NOT NULL,
                level INTEGER NOT NULL DEFAULT 3,
                triggered_at DATETIME NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending',
                channels TEXT NOT NULL DEFAULT '[]'
            );

            -- 创建告警记录索引
            CREATE INDEX IF NOT EXISTS idx_alert_records_code
                ON alert_records(code);
            CREATE INDEX IF NOT EXISTS idx_alert_records_triggered_at
                ON alert_records(triggered_at);
        """)
        await self._conn.commit()

    async def save_stock(self, stock: Stock) -> None:
        """保存股票信息"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.execute(
            """
            INSERT OR REPLACE INTO stocks (code, name, industry, list_date)
            VALUES (?, ?, ?, ?)
            """,
            (stock.code, stock.name, stock.industry, stock.list_date)
        )
        await self._conn.commit()

    async def save_daily_quotes(self, quotes: list[DailyQuote]) -> None:
        """批量保存日线行情"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.executemany(
            """
            INSERT OR REPLACE INTO daily_quotes
                (code, date, open, high, low, close, volume, amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (q.code, q.date, q.open, q.high, q.low, q.close, q.volume, q.amount)
                for q in quotes
            ]
        )
        await self._conn.commit()

    async def get_daily_quotes(
        self, code: str, limit: int = 100
    ) -> list[DailyQuote]:
        """获取日线行情"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        cursor = await self._conn.execute(
            """
            SELECT code, date, open, high, low, close, volume, amount
            FROM daily_quotes
            WHERE code = ?
            ORDER BY date DESC
            LIMIT ?
            """,
            (code, limit)
        )
        rows = await cursor.fetchall()

        return [
            DailyQuote(
                code=row["code"],
                date=row["date"],
                open=row["open"],
                high=row["high"],
                low=row["low"],
                close=row["close"],
                volume=row["volume"],
                amount=row["amount"]
            )
            for row in rows
        ]

    # ==================== 监控项相关方法 ====================

    async def save_watch_item(self, item: WatchItem) -> None:
        """保存监控项"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        import json
        await self._conn.execute(
            """
            INSERT OR REPLACE INTO watch_items
                (code, name, conditions, alert_channels, enabled, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                item.code,
                item.name,
                json.dumps(item.conditions),
                json.dumps(item.alert_channels),
                1 if item.enabled else 0,
                item.created_at
            )
        )
        await self._conn.commit()

    async def get_watch_items(self, enabled_only: bool = True) -> list[WatchItem]:
        """获取所有监控项"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        import json
        if enabled_only:
            cursor = await self._conn.execute(
                "SELECT * FROM watch_items WHERE enabled = 1"
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM watch_items"
            )
        rows = await cursor.fetchall()

        return [
            WatchItem(
                code=row["code"],
                name=row["name"],
                conditions=json.loads(row["conditions"]),
                alert_channels=json.loads(row["alert_channels"]),
                enabled=bool(row["enabled"]),
                created_at=row["created_at"]
            )
            for row in rows
        ]

    async def delete_watch_item(self, code: str) -> None:
        """删除监控项"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.execute(
            "DELETE FROM watch_items WHERE code = ?",
            (code,)
        )
        await self._conn.commit()

    # ==================== 告警记录相关方法 ====================

    async def save_alert_record(self, record: AlertRecord) -> int:
        """保存告警记录，返回记录ID"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        import json
        cursor = await self._conn.execute(
            """
            INSERT INTO alert_records
                (code, signal_type, signal_name, message, level, triggered_at, status, channels)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record.code,
                record.signal_type,
                record.signal_name,
                record.message,
                record.level,
                record.triggered_at,
                record.status,
                json.dumps(record.channels)
            )
        )
        await self._conn.commit()
        return cursor.lastrowid

    async def get_alert_records(
        self,
        code: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list[AlertRecord]:
        """获取告警记录"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        import json
        conditions = []
        params = []

        if code:
            conditions.append("code = ?")
            params.append(code)
        if status:
            conditions.append("status = ?")
            params.append(status)

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        params.append(limit)

        cursor = await self._conn.execute(
            f"""
            SELECT * FROM alert_records
            WHERE {where_clause}
            ORDER BY triggered_at DESC
            LIMIT ?
            """,
            params
        )
        rows = await cursor.fetchall()

        return [
            AlertRecord(
                id=row["id"],
                code=row["code"],
                signal_type=row["signal_type"],
                signal_name=row["signal_name"],
                message=row["message"],
                level=row["level"],
                triggered_at=row["triggered_at"],
                status=row["status"],
                channels=json.loads(row["channels"])
            )
            for row in rows
        ]

    async def update_alert_status(self, record_id: int, status: str) -> None:
        """更新告警记录状态"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.execute(
            "UPDATE alert_records SET status = ? WHERE id = ?",
            (status, record_id)
        )
        await self._conn.commit()
