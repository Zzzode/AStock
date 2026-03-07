"""CLI 入口"""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .storage import Database
from .quote import QuoteService
from .analysis import TechnicalAnalyzer


app = typer.Typer(name="astock")
console = Console()

# 默认数据库路径
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"


@app.command()
def quote(
    code: str = typer.Argument(..., help="股票代码"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """获取实时行情"""
    async def _get_quote():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            result = await service.get_realtime(code)
            return result
        finally:
            await db.close()

    result = asyncio.run(_get_quote())

    if json_output:
        console.print_json(data=result)
    else:
        table = Table(title=f"{result['name']} ({result['code']})")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="green")

        table.add_row("最新价", f"{result['price']:.2f}")
        table.add_row("涨跌幅", f"{result['change_percent']:.2f}%")
        table.add_row("涨跌额", f"{result['change']:.2f}")
        table.add_row("今开", f"{result['open']:.2f}")
        table.add_row("最高", f"{result['high']:.2f}")
        table.add_row("最低", f"{result['low']:.2f}")
        table.add_row("昨收", f"{result['prev_close']:.2f}")
        table.add_row("成交量", f"{result['volume']/10000:.0f}万手")
        table.add_row("成交额", f"{result['amount']/100000000:.2f}亿")

        console.print(table)


@app.command()
def analyze(
    code: str = typer.Argument(..., help="股票代码"),
    days: int = typer.Option(100, "--days", "-d", help="分析天数"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """技术分析"""
    async def _analyze():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            df = await service.get_daily(code)

            if df.empty:
                return {"error": "无数据"}

            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()
            return analyzer.get_signals()
        finally:
            await db.close()

    result = asyncio.run(_analyze())

    if json_output:
        console.print_json(data=result)
    else:
        # 显示技术指标
        latest = result.get("latest", {})

        panel_content = f"""
[bold cyan]价格指标[/bold cyan]
收盘价: {latest.get('close', 0):.2f}
MA5: {latest.get('ma5', 0):.2f}
MA10: {latest.get('ma10', 0):.2f}
MA20: {latest.get('ma20', 0):.2f}

[bold cyan]MACD[/bold cyan]
DIF: {latest.get('macd', 0):.4f}
DEA: {latest.get('macd_signal', 0):.4f}
柱: {latest.get('macd_hist', 0):.4f}

[bold cyan]KDJ[/bold cyan]
K: {latest.get('kdj_k', 0):.2f}
D: {latest.get('kdj_d', 0):.2f}
J: {latest.get('kdj_j', 0):.2f}

[bold cyan]RSI[/bold cyan]
RSI6: {latest.get('rsi6', 0):.2f}
"""
        console.print(Panel(panel_content, title=f"技术分析 - {code}"))

        # 显示信号
        signals = result.get("signals", [])
        if signals:
            console.print("\n[bold yellow]检测到的信号:[/bold yellow]")
            for signal in signals:
                color = "green" if signal["bias"] == "bullish" else "red"
                console.print(f"  [{color}]●[/{color}] {signal['name']}: {signal['description']}")
        else:
            console.print("\n[dim]暂无明显信号[/dim]")


@app.command()
def init_db():
    """初始化数据库"""
    async def _init():
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        db = Database(str(DB_PATH))
        await db.connect()
        await db.init_tables()

        service = QuoteService(db)
        count = await service.refresh_stocks()

        await db.close()
        return count

    count = asyncio.run(_init())
    console.print(f"[green]数据库初始化完成，已加载 {count} 只股票[/green]")


if __name__ == "__main__":
    app()
