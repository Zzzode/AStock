"""SQLite 数据库管理"""

import aiosqlite
from pathlib import Path
from typing import Optional

from .models import Stock, DailyQuote


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
