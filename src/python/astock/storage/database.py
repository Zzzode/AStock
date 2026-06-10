"""SQLite database management"""

import aiosqlite
from pathlib import Path
from typing import Optional

from .models import Stock, DailyQuote, WatchItem, AlertRecord, Trade


class Database:
    """Async SQLite database manager"""

    def __init__(self, db_path: str = "data/stocks.db"):
        self.db_path = Path(db_path)
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self) -> None:
        """Connect to database"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = await aiosqlite.connect(self.db_path)
        self._conn.row_factory = aiosqlite.Row

    async def close(self) -> None:
        """Close database connection"""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def init_tables(self) -> None:
        """Initialize database tables"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.executescript("""
            -- Stock basic information
            CREATE TABLE IF NOT EXISTS stocks (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                industry TEXT,
                list_date DATE
            );

            -- Daily quotes
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

            -- Create index
            CREATE INDEX IF NOT EXISTS idx_daily_quotes_date
                ON daily_quotes(date);

            -- Watch items
            CREATE TABLE IF NOT EXISTS watch_items (
                code TEXT PRIMARY KEY,
                name TEXT,
                conditions TEXT NOT NULL DEFAULT '{}',
                alert_channels TEXT NOT NULL DEFAULT '["terminal"]',
                enabled INTEGER NOT NULL DEFAULT 1,
                created_at DATETIME
            );

            -- Alert records
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

            -- Create alert record indexes
            CREATE INDEX IF NOT EXISTS idx_alert_records_code
                ON alert_records(code);
            CREATE INDEX IF NOT EXISTS idx_alert_records_triggered_at
                ON alert_records(triggered_at);
        """)
        await self._conn.commit()

    async def save_stock(self, stock: Stock) -> None:
        """Save stock information"""
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

    async def get_stock(self, code: str) -> Optional[Stock]:
        """Get single stock basic information"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        cursor = await self._conn.execute(
            """
            SELECT code, name, industry, list_date
            FROM stocks
            WHERE code = ?
            LIMIT 1
            """,
            (code,)
        )
        row = await cursor.fetchone()
        if row is None:
            return None

        return Stock(
            code=row["code"],
            name=row["name"],
            industry=row["industry"],
            list_date=row["list_date"],
        )

    async def save_daily_quotes(self, quotes: list[DailyQuote]) -> None:
        """Batch save daily quotes"""
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
        """Get daily quotes"""
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

    def get_trades(self, user_id: str) -> list[Trade]:
        return []

    # ==================== Watch item methods ====================

    async def save_watch_item(self, item: WatchItem) -> None:
        """Save watch item"""
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
        """Get all watch items"""
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
        """Delete watch item"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.execute(
            "DELETE FROM watch_items WHERE code = ?",
            (code,)
        )
        await self._conn.commit()

    # ==================== Alert record methods ====================

    async def save_alert_record(self, record: AlertRecord) -> int:
        """Save alert record, returns record ID"""
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
        return int(cursor.lastrowid or 0)

    async def get_alert_records(
        self,
        code: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> list[AlertRecord]:
        """Get alert records"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        import json
        conditions: list[str] = []
        params: list[object] = []

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
        """Update alert record status"""
        if not self._conn:
            raise RuntimeError("Database not connected")

        await self._conn.execute(
            "UPDATE alert_records SET status = ? WHERE id = ?",
            (status, record_id)
        )
        await self._conn.commit()
