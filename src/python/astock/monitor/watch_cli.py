"""Watch management CLI"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console
from rich.table import Table

from ..storage import Database, WatchItem

app = typer.Typer(name="watch")
console = Console()

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"


@app.command("add")
def add_watch(
    code: str = typer.Argument(..., help="Stock code"),
    signals: Optional[str] = typer.Option(None, "--signals", "-s", help="Signal types to monitor"),
    channels: str = typer.Option("terminal", "--channels", "-c", help="Alert channels"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output")
) -> None:
    """Add a watch item"""
    async def _add() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()

        conditions: dict[str, object] = {}
        if signals:
            conditions["signal_types"] = signals.split(",")

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
