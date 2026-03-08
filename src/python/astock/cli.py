"""CLI 入口"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .storage import Database
from .quote import QuoteService
from .analysis import TechnicalAnalyzer
from .monitor import MonitorService
from .stock_picker import StockScreener


app = typer.Typer(name="astock")
console = Console()

# 默认数据库路径
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"

# 全局监控服务实例
_monitor_service: Optional[MonitorService] = None


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


# ============ Alert 命令组 ============

alert_app = typer.Typer(name="alert", help="监控告警管理")
app.add_typer(alert_app, name="alert")


@alert_app.callback(invoke_without_command=True)
def alert_callback(ctx: typer.Context):
    """监控告警管理"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(alert_status)


@alert_app.command("start")
def alert_start(
    interval: int = typer.Option(60, "--interval", "-i", help="扫描间隔(秒)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """启动监控服务"""
    async def _start():
        global _monitor_service

        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            _monitor_service = MonitorService(db, quote_service)
            _monitor_service.set_scan_interval(interval)
            await _monitor_service.start()

            # 获取监控股票数量
            watch_items = await db.get_watch_items(enabled_only=True)

            return {
                "status": "started",
                "interval": interval,
                "watch_count": len(watch_items)
            }
        finally:
            # 注意: 不关闭 db，因为监控服务需要持续使用
            pass

    result = asyncio.run(_start())

    if json_output:
        console.print_json(data=result)
    else:
        console.print(f"[green]监控服务已启动[/green]")
        console.print(f"扫描间隔: {result['interval']}秒")
        console.print(f"监控股票: {result['watch_count']}只")


@alert_app.command("stop")
def alert_stop(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """停止监控服务"""
    async def _stop():
        global _monitor_service

        if _monitor_service:
            await _monitor_service.stop()
            _monitor_service = None
            return {"status": "stopped"}
        return {"status": "not_running"}

    result = asyncio.run(_stop())

    if json_output:
        console.print_json(data=result)
    else:
        if result["status"] == "stopped":
            console.print("[yellow]监控服务已停止[/yellow]")
        else:
            console.print("[dim]监控服务未运行[/dim]")


@alert_app.command("status")
def alert_status(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """查看监控状态"""
    async def _status():
        global _monitor_service

        db = Database(str(DB_PATH))
        await db.connect()
        try:
            # 获取监控股票数量
            watch_items = await db.get_watch_items(enabled_only=True)

            # 获取今日告警数量
            today = datetime.now().date()
            alerts = await db.get_alert_records(limit=100)
            today_alerts = [
                a for a in alerts
                if a.triggered_at.date() == today
            ]

            return {
                "running": _monitor_service is not None and _monitor_service._running,
                "interval": _monitor_service._scan_interval if _monitor_service else 60,
                "watch_count": len(watch_items),
                "today_alerts": len(today_alerts),
                "start_time": None  # TODO: 记录启动时间
            }
        finally:
            await db.close()

    result = asyncio.run(_status())

    if json_output:
        console.print_json(data=result)
    else:
        status_text = "[green]运行中[/green]" if result["running"] else "[dim]已停止[/dim]"
        panel_content = f"""
状态: {status_text}
扫描间隔: {result['interval']}秒
监控股票: {result['watch_count']}只
今日告警: {result['today_alerts']}条
"""
        console.print(Panel(panel_content.strip(), title="监控服务状态"))


@alert_app.command("history")
def alert_history(
    code: Optional[str] = typer.Argument(None, help="股票代码(可选)"),
    limit: int = typer.Option(10, "--limit", "-n", help="显示数量"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """查看历史告警"""
    async def _history():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            alerts = await db.get_alert_records(limit=limit)

            # 按股票代码过滤
            if code:
                alerts = [a for a in alerts if a.code == code]

            return {
                "alerts": [
                    {
                        "id": a.id,
                        "code": a.code,
                        "signal_type": a.signal_type,
                        "signal_name": a.signal_name,
                        "message": a.message,
                        "level": a.level,
                        "triggered_at": a.triggered_at.isoformat(),
                        "status": a.status
                    }
                    for a in alerts
                ]
            }
        finally:
            await db.close()

    result = asyncio.run(_history())

    if json_output:
        console.print_json(data=result)
    else:
        alerts = result["alerts"]

        if not alerts:
            console.print("[dim]暂无告警记录[/dim]")
            return

        title = f"历史告警记录 ({code})" if code else "历史告警记录"
        table = Table(title=title)
        table.add_column("时间", style="cyan")
        table.add_column("股票", style="white")
        table.add_column("信号类型", style="yellow")
        table.add_column("描述", style="green")
        table.add_column("状态", style="dim")

        for alert in alerts:
            triggered_at = datetime.fromisoformat(alert["triggered_at"])
            time_str = triggered_at.strftime("%m-%d %H:%M")
            status_color = "green" if alert["status"] == "sent" else "yellow"
            table.add_row(
                time_str,
                alert["code"],
                alert["signal_name"],
                alert["message"][:20] + "..." if len(alert["message"]) > 20 else alert["message"],
                f"[{status_color}]{alert['status']}[/{status_color}]"
            )

        console.print(table)


@app.command()
def screen(
    factors: Optional[str] = typer.Argument(None, help="因子列表，逗号分隔"),
    limit: int = typer.Option(10, "--limit", "-n", help="返回数量"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """股票选股"""
    async def _screen():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            screener = StockScreener(quote_service)

            # 解析因子列表
            factor_list = None
            if factors:
                factor_list = [f.strip() for f in factors.split(",")]

            results = await screener.screen(factors=factor_list, limit=limit)

            return {
                "total": len(results),
                "results": [
                    {
                        "code": r.code,
                        "name": r.name,
                        "score": r.score,
                        "matched_factors": r.matched_factors,
                        "factor_scores": r.factor_scores,
                        "screened_at": r.screened_at.isoformat()
                    }
                    for r in results
                ]
            }
        finally:
            await db.close()

    result = asyncio.run(_screen())

    if json_output:
        console.print_json(data=result)
    else:
        if not result["results"]:
            console.print("[dim]未找到符合条件的股票[/dim]")
            return

        table = Table(title=f"选股结果 (共 {result['total']} 只)")
        table.add_column("排名", style="dim", width=4)
        table.add_column("代码", style="cyan", width=8)
        table.add_column("名称", style="white", width=10)
        table.add_column("得分", style="yellow", width=6)
        table.add_column("匹配因子", style="green")

        for i, r in enumerate(result["results"], 1):
            factors_str = ",".join(r["matched_factors"][:3])
            if len(r["matched_factors"]) > 3:
                factors_str += "..."
            table.add_row(
                str(i),
                r["code"],
                r["name"] or "-",
                f"{r['score']:.1f}",
                factors_str
            )

        console.print(table)


if __name__ == "__main__":
    app()
