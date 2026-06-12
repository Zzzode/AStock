"""SQLite schema migration system.

A lightweight, file-based migration system that tracks applied migrations
in a `_migrations` table. Each migration is a numbered SQL file in a
migrations directory.

Usage:
    from astock.migrations import MigrationRunner
    runner = MigrationRunner("data/stocks.db")
    await runner.run_pending()
"""

from __future__ import annotations

import aiosqlite
from datetime import datetime
from pathlib import Path
from typing import Optional

from ..utils import get_logger

logger = get_logger("migrations")

MIGRATIONS_DIR = Path(__file__).parent / "versions"


class MigrationRunner:
    """Applies ordered SQL migrations to a SQLite database."""

    def __init__(
        self,
        db_path: str | Path,
        migrations_dir: Optional[Path] = None,
    ):
        self.db_path = Path(db_path)
        self.migrations_dir = migrations_dir or MIGRATIONS_DIR

    async def run_pending(self) -> dict[str, list[str]]:
        """Apply all pending migrations.

        Returns dict with 'applied' and 'already_applied' lists.
        """
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        async with aiosqlite.connect(self.db_path) as conn:
            await self._ensure_migrations_table(conn)
            applied = await self._get_applied(conn)
            available = self._get_available()

            newly_applied: list[str] = []
            for migration in available:
                if migration.name in applied:
                    continue
                logger.info(f"Applying migration: {migration.name}")
                sql = migration.read_text(encoding="utf-8")
                try:
                    await conn.executescript(sql)
                    await conn.execute(
                        "INSERT INTO _migrations (name, applied_at) VALUES (?, ?)",
                        (migration.name, datetime.now().isoformat()),
                    )
                    await conn.commit()
                    newly_applied.append(migration.name)
                except Exception as e:
                    logger.error(f"Migration {migration.name} failed: {e}")
                    raise MigrationError(
                        f"Failed to apply {migration.name}: {e}"
                    ) from e

            return {
                "applied": newly_applied,
                "already_applied": sorted(applied),
            }

    async def get_status(self) -> dict[str, list[str]]:
        """Check migration status without applying."""
        if not self.db_path.exists():
            available = self._get_available()
            return {
                "pending": [m.name for m in available],
                "applied": [],
            }

        async with aiosqlite.connect(self.db_path) as conn:
            await self._ensure_migrations_table(conn)
            applied = await self._get_applied(conn)
            available = self._get_available()
            pending = [m.name for m in available if m.name not in applied]
            return {
                "pending": pending,
                "applied": sorted(applied),
            }

    def _get_available(self) -> list[Path]:
        """Get all migration files sorted by name."""
        if not self.migrations_dir.exists():
            return []
        migrations = sorted(
            self.migrations_dir.glob("*.sql"),
            key=lambda p: p.name,
        )
        return migrations

    async def _ensure_migrations_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS _migrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                applied_at TEXT NOT NULL
            )
        """)
        await conn.commit()

    async def _get_applied(self, conn: aiosqlite.Connection) -> set[str]:
        cursor = await conn.execute("SELECT name FROM _migrations")
        rows = await cursor.fetchall()
        return {row[0] for row in rows}


class MigrationError(Exception):
    """Raised when a migration fails to apply."""
