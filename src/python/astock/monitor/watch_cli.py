"""监控管理 CLI"""

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
    code: str = typer.Argument(..., help="股票代码"),
    signals: Optional[str] = typer.Option(None, "--signals", "-s", help="监控的信号类型"),
    channels: str = typer.Option("terminal", "--channels", "-c", help="提醒渠道"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
) -> None:
    """添加监控"""
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
        console.print(f"[green]已添加监控: {code}[/green]")


@app.command("remove")
def remove_watch(
    code: str = typer.Argument(..., help="股票代码"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
) -> None:
    """移除监控"""
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
        console.print(f"[yellow]已移除监控: {code}[/yellow]")


@app.command("list")
def list_watch(json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")) -> None:
    """查看监控列表"""
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
            console.print("[dim]暂无监控项[/dim]")
            return

        table = Table(title=f"监控列表 ({len(items)}项)")
        table.add_column("代码", style="cyan")
        table.add_column("名称")
        table.add_column("状态")
        table.add_column("渠道")

        for item in items:
            status = "[green]启用[/green]" if item.get("enabled") else "[red]禁用[/red]"
            table.add_row(
                item["code"],
                item.get("name") or "-",
                status,
                ",".join(item.get("alert_channels", []))
            )

        console.print(table)


if __name__ == "__main__":
    app()
