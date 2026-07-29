"""Watch management CLI"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console
from rich.table import Table

from ..storage import Database, WatchItem

app = typer.Typer(name="watch")
console = Console()

PROJECT_ROOT = Path(__file__).resolve().parents[4]
LEGACY_DB_PATH = Path(__file__).resolve().parents[3] / "data" / "stocks.db"
CANONICAL_DB_PATH = PROJECT_ROOT / "data" / "stocks.db"
DB_PATH = CANONICAL_DB_PATH if CANONICAL_DB_PATH.exists() or not LEGACY_DB_PATH.exists() else LEGACY_DB_PATH
STRUCTURE_ALERT_TYPES = frozenset(
    {"price_dislocation", "range_expansion", "volume_spike"}
)


def normalize_watch_alert_types(raw: str) -> list[str]:
    """Validate watch-list alerts against the production structure scanner."""
    alert_types = [item.strip() for item in raw.split(",") if item.strip()]
    unknown = sorted(set(alert_types) - STRUCTURE_ALERT_TYPES)
    if unknown:
        supported = ", ".join(sorted(STRUCTURE_ALERT_TYPES))
        raise typer.BadParameter(
            f"unsupported alert type(s): {', '.join(unknown)}; supported: {supported}"
        )
    return alert_types


@app.command("add")
def add_watch(
    code: str = typer.Argument(..., help="Stock code"),
    signals: Optional[str] = typer.Option(
        None,
        "--signals",
        "-s",
        help="Observable market-structure alert types to monitor",
    ),
    channels: str = typer.Option("terminal", "--channels", "-c", help="Alert channels"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output")
) -> None:
    """Add a watch item"""
    async def _add() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()

        conditions: dict[str, object] = {}
        if signals:
            conditions["signal_types"] = normalize_watch_alert_types(signals)

        item = WatchItem(
            code=code,
            conditions=conditions,
            alert_channels=channels.split(","),
            created_at=datetime.now()
        )
        await db.save_watch_item(item)
        await db.close()
        return item.model_dump()

    result = asyncio.run(_add())

    if json_output:
        console.print_json(data=result)
    else:
        console.print(f"[green]Watch added: {code}[/green]")


@app.command("remove")
def remove_watch(
    code: str = typer.Argument(..., help="Stock code"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output")
) -> None:
    """Remove a watch item"""
    async def _remove() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()
        conn = db._conn
        if conn is None:
            raise RuntimeError("Database not connected")
        await conn.execute(
            "UPDATE watch_items SET enabled = 0 WHERE code = ?", (code,)
        )
        await conn.commit()
        await db.close()
        return {"code": code, "removed": True}

    result = asyncio.run(_remove())

    if json_output:
        console.print_json(data=result)
    else:
        console.print(f"[yellow]Watch removed: {code}[/yellow]")


@app.command("list")
def list_watch(json_output: bool = typer.Option(False, "--json", "-j", help="JSON output")) -> None:
    """View watch list"""
    async def _list() -> list[dict[str, Any]]:
        db = Database(str(DB_PATH))
        await db.connect()
        items = await db.get_watch_items(enabled_only=False)
        await db.close()
        return [item.model_dump() for item in items]

    items = asyncio.run(_list())

    if json_output:
        console.print_json(data=items)
    else:
        if not items:
            console.print("[dim]No watch items[/dim]")
            return

        table = Table(title=f"Watch List ({len(items)} items)")
        table.add_column("Code", style="cyan")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Channels")

        for item in items:
            status = "[green]Enabled[/green]" if item.get("enabled") else "[red]Disabled[/red]"
            table.add_row(
                item["code"],
                item.get("name") or "-",
                status,
                ",".join(item.get("alert_channels", []))
            )

        console.print(table)


if __name__ == "__main__":
    app()
