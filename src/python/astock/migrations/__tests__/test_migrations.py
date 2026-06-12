"""Tests for migration system."""

import pytest
import aiosqlite

from astock.migrations import MigrationRunner, MigrationError


@pytest.fixture
def tmp_db(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def tmp_migrations(tmp_path):
    migrations_dir = tmp_path / "migrations"
    migrations_dir.mkdir()
    (migrations_dir / "001_init.sql").write_text(
        "CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT);"
    )
    (migrations_dir / "002_add_col.sql").write_text(
        "ALTER TABLE test_table ADD COLUMN value REAL;"
    )
    return migrations_dir


@pytest.mark.asyncio
async def test_run_pending(tmp_db, tmp_migrations):
    runner = MigrationRunner(tmp_db, tmp_migrations)
    result = await runner.run_pending()
    assert "001_init.sql" in result["applied"]
    assert "002_add_col.sql" in result["applied"]


@pytest.mark.asyncio
async def test_idempotent(tmp_db, tmp_migrations):
    runner = MigrationRunner(tmp_db, tmp_migrations)
    await runner.run_pending()
    result = await runner.run_pending()
    assert result["applied"] == []
    assert len(result["already_applied"]) == 2


@pytest.mark.asyncio
async def test_get_status(tmp_db, tmp_migrations):
    runner = MigrationRunner(tmp_db, tmp_migrations)
    status = await runner.get_status()
    assert len(status["pending"]) == 2
    assert status["applied"] == []

    await runner.run_pending()
    status = await runner.get_status()
    assert status["pending"] == []
    assert len(status["applied"]) == 2


@pytest.mark.asyncio
async def test_failed_migration(tmp_db, tmp_path):
    migrations_dir = tmp_path / "bad_migrations"
    migrations_dir.mkdir()
    (migrations_dir / "001_bad.sql").write_text("THIS IS NOT VALID SQL;")
    runner = MigrationRunner(tmp_db, migrations_dir)
    with pytest.raises(MigrationError):
        await runner.run_pending()


@pytest.mark.asyncio
async def test_partial_apply(tmp_db, tmp_path):
    migrations_dir = tmp_path / "partial"
    migrations_dir.mkdir()
    (migrations_dir / "001_ok.sql").write_text(
        "CREATE TABLE t1 (id INTEGER PRIMARY KEY);"
    )
    runner = MigrationRunner(tmp_db, migrations_dir)
    await runner.run_pending()

    (migrations_dir / "002_ok.sql").write_text(
        "CREATE TABLE t2 (id INTEGER PRIMARY KEY);"
    )
    result = await runner.run_pending()
    assert result["applied"] == ["002_ok.sql"]
    assert "001_ok.sql" in result["already_applied"]
