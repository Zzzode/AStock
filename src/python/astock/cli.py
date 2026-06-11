"""Machine-readable CLI adapter for agent capabilities.

This module exists for skills that need a subprocess boundary.
Reusable logic belongs in astock.capabilities or service/domain modules.
"""

import asyncio
from contextlib import nullcontext, redirect_stdout
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from . import capabilities
from .backtest.backtest_cli import app as backtest_app
from .portfolio.portfolio_cli import app as portfolio_app
from .monitor.watch_cli import app as watch_app
from .storage import Database
from .quote import QuoteService
from .monitor import MonitorService
from .monitor.service_status import (
    ServiceStatusManager,
    get_uptime_info,
    format_duration,
)
from .config import ConfigManager, TradingStyle, RiskLevel, EmailConfig
from .learning import StyleAnalyzer
from .utils import DataSourceError, ValidationError

app = typer.Typer(name="astock")
console = Console()

# Default database path
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"

# Global monitor service instance
_monitor_service: Optional[MonitorService] = None


def _print_json(data: Any) -> None:
    """Output clean JSON to stdout, avoiding Rich or log pollution."""
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def _json_stdout_guard(enabled: bool):
    """In JSON mode, redirect third-party stdout noise to stderr."""
    return redirect_stdout(sys.stderr) if enabled else nullcontext()


def _run_async(coro: Any, json_output: bool) -> Any:
    """Run async task; isolate stdout noise in JSON mode."""
    with _json_stdout_guard(json_output):
        return asyncio.run(coro)


@app.command()
def quote(
    code: str = typer.Argument(..., help="Stock code"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Get real-time quote"""

    async def _get_quote() -> dict[str, Any]:
        return await capabilities.get_quote(code, db_path=DB_PATH)

    try:
        result = _run_async(_get_quote(), json_output)
    except (ValidationError, DataSourceError) as e:
        if json_output:
            _print_json({"error": str(e)})
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        if json_output:
            _print_json({"error": f"Failed to get real-time quote: {e}"})
        else:
            console.print(f"[red]Error: Failed to get real-time quote: {e}[/red]")
        raise typer.Exit(1)

    if json_output:
        _print_json(result)
    else:
        table = Table(title=f"{result['name']} ({result['code']})")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Latest Price", f"{result['price']:.2f}")
        table.add_row("Change %", f"{result['change_percent']:.2f}%")
        table.add_row("Change", f"{result['change']:.2f}")
        table.add_row("Open", f"{result['open']:.2f}")
        table.add_row("High", f"{result['high']:.2f}")
        table.add_row("Low", f"{result['low']:.2f}")
        table.add_row("Prev Close", f"{result['prev_close']:.2f}")
        table.add_row("Volume", f"{result['volume'] / 10000:.0f}0k lots")
        table.add_row("Turnover", f"{result['amount'] / 100000000:.2f}B")

        console.print(table)
        if result.get("data_quality"):
            console.print(f"[dim]Data quality: {result['data_quality']}[/dim]")


@app.command()
def analyze(
    code: str = typer.Argument(..., help="Stock code"),
    days: int = typer.Option(100, "--days", "-d", help="Number of days to analyze"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Technical analysis - outputs raw data and signals for LLM reasoning"""

    async def _analyze() -> dict[str, Any]:
        return await capabilities.analyze_stock(code, days=days, db_path=DB_PATH)

    try:
        result = _run_async(_analyze(), json_output)
    except (ValidationError, DataSourceError) as e:
        if json_output:
            _print_json({"error": str(e)})
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        if json_output:
            _print_json({"error": f"Technical analysis failed: {e}"})
        else:
            console.print(f"[red]Error: Technical analysis failed: {e}[/red]")
        raise typer.Exit(1)

    # Check for errors
    if result.get("error"):
        if json_output:
            _print_json(result)
        else:
            console.print(f"[red]Error: {result['error']}[/red]")
        raise typer.Exit(1)

    if json_output:
        _print_json(result)
    else:
        # Display stock name
        name = result.get("name")
        title = (
            f"Technical Analysis - {name} ({code})"
            if name
            else f"Technical Analysis - {code}"
        )

        # Display technical indicators
        indicators = result.get("indicators", {})
        prev_indicators = result.get("prev_indicators", {})

        panel_content = f"""
[bold cyan]Price Indicators[/bold cyan]
Close: {indicators.get("close", 0):.2f}  (Previous: {prev_indicators.get("close", 0):.2f})
MA5: {indicators.get("ma5", 0):.2f}
MA10: {indicators.get("ma10", 0):.2f}
MA20: {indicators.get("ma20", 0):.2f}

[bold cyan]MACD[/bold cyan]
DIF: {indicators.get("macd", 0):.4f}
DEA: {indicators.get("macd_signal", 0):.4f}
Histogram: {indicators.get("macd_hist", 0):.4f}

[bold cyan]KDJ[/bold cyan]
K: {indicators.get("kdj_k", 0):.2f}
D: {indicators.get("kdj_d", 0):.2f}
J: {indicators.get("kdj_j", 0):.2f}

[bold cyan]RSI[/bold cyan]
RSI6: {indicators.get("rsi6", 0):.2f}
"""
        console.print(Panel(panel_content, title=title))

        # Display signals
        signals = result.get("signals", [])
        signal_stats = result.get("signal_stats", {})

        if signals:
            console.print(
                f"\n[bold yellow]Detected Signals ({signal_stats.get('bullish_count', 0)} bullish/{signal_stats.get('bearish_count', 0)} bearish):[/bold yellow]"
            )
            for signal in signals:
                bias_color = "green" if signal.get("bias") == "bullish" else "red"
                current = signal.get("current", {})
                current_str = ", ".join(
                    f"{k}={v:.2f}" if isinstance(v, float) else f"{k}={v}"
                    for k, v in current.items()
                )
                console.print(
                    f"  [{bias_color}]●[/{bias_color}] {signal.get('name', signal.get('type'))}: {current_str}"
                )

        # Display historical context
        history = result.get("history", {})
        if history.get("recent_analyses"):
            console.print("\n[bold dim]Recent Analysis History:[/bold dim]")
            for h in history["recent_analyses"][:3]:
                signals_str = ", ".join(h.get("signals", []))
                console.print(f"  {h.get('date', '')}: {signals_str}")

        # Display feedback statistics
        feedback_stats = result.get("feedback_stats", {})
        if feedback_stats.get("overall"):
            overall = feedback_stats["overall"]
            console.print("\n[bold dim]User Feedback Statistics:[/bold dim]")
            console.print(
                f"  Total samples: {overall.get('total', 0)}, Success rate: {overall.get('success_rate', 0):.0%}"
            )

        # Display quote
        quote = result.get("quote", {})
        if quote:
            console.print("\n[bold cyan]Real-time Quote:[/bold cyan]")
            console.print(
                f"  Latest price: {quote.get('price', 0):.2f}  Change: {quote.get('change_percent', 0):+.2f}%"
            )
            console.print(f"  Turnover: {quote.get('amount', 0) / 100000000:.2f}B")
            if quote.get("data_quality"):
                console.print(f"  Data quality: {quote.get('data_quality')}")

        data_quality = result.get("data_quality", {})
        if data_quality:
            console.print("\n[bold dim]Data Quality:[/bold dim]")
            console.print(f"  Daily: {data_quality.get('daily', 'unknown')}")
            console.print(f"  Quote: {data_quality.get('quote', 'unknown')}")


@app.command()
def team(
    code: str = typer.Argument(..., help="Stock code"),
    question: str = typer.Option(
        "Is now a good time to enter?", "--question", "-q", help="Analysis question"
    ),
    days: int = typer.Option(100, "--days", "-d", help="Number of days to analyze"),
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Team comprehensive analysis"""

    async def _team() -> dict[str, Any]:
        return await capabilities.build_team_packet(
            code,
            question=question,
            days=days,
            user_id=user_id,
            db_path=DB_PATH,
        )

    try:
        result = _run_async(_team(), json_output)
    except (ValidationError, DataSourceError) as e:
        if json_output:
            _print_json({"error": str(e)})
        else:
            console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        if json_output:
            _print_json({"error": f"Team analysis failed: {e}"})
        else:
            console.print(f"[red]Error: Team analysis failed: {e}[/red]")
        raise typer.Exit(1)

    if result.get("error"):
        if json_output:
            _print_json(result)
        else:
            console.print(f"[red]Error: {result['error']}[/red]")
        raise typer.Exit(1)

    if json_output:
        _print_json(result)
        return

    orchestration = result.get("orchestration", {})
    active_agents = orchestration.get("active_agent_ids", [])
    summary_panel = (
        f"Target: {result.get('name') or code} ({result['code']})\n"
        f"Question: {result['question']}\n"
        f"Status: {result['summary']}\n"
        f"Recommended expansion: {', '.join(result.get('recommended_roles', ['core']))}\n"
        f"Active roles: {', '.join(active_agents) if active_agents else 'core'}"
    )
    console.print(Panel(summary_panel, title="Agent Team Data Packet"))

    packet = result.get("packet", {})
    packet_table = Table(title="Data Packet Status")
    packet_table.add_column("Module", style="cyan")
    packet_table.add_column("Available", style="green", width=8)
    packet_table.add_column("Note", style="white")

    for module in ["quote", "analysis", "screen", "config", "profiles"]:
        exists = module in packet
        packet_table.add_row(
            module,
            "yes" if exists else "no",
            "-" if exists else "missing",
        )

    console.print(packet_table)

    warnings = result.get("warnings", [])
    if warnings:
        console.print("\n[bold red]Risk Warnings:[/bold red]")
        for item in warnings:
            console.print(f"  - {item}")

    data_quality = result.get("data_quality", {})
    if data_quality:
        console.print("\n[bold dim]Data Quality:[/bold dim]")
        console.print(f"  Quote: {data_quality.get('quote', 'unknown')}")
        analysis_quality = data_quality.get("analysis", {})
        if analysis_quality:
            console.print(f"  Daily: {analysis_quality.get('daily', 'unknown')}")
        screen_quality = data_quality.get("screen", {})
        if screen_quality:
            console.print(
                f"  Strategy: {screen_quality.get('data_quality', 'unknown')}"
            )

    lead_rules = orchestration.get("lead_rules", [])
    if lead_rules:
        console.print("\n[bold cyan]Execution Principles:[/bold cyan]")
        for item in lead_rules:
            console.print(f"  - {item}")

    if result.get("session_path"):
        console.print(f"\n[dim]Session saved: {result['session_path']}[/dim]")


@app.command()
def init_db(
    skip_refresh: bool = typer.Option(
        False, "--skip-refresh", help="Skip refreshing stock data"
    ),
) -> None:
    """Initialize database"""

    async def _init() -> int:
        result = await capabilities.initialize_database(
            skip_refresh=skip_refresh,
            db_path=DB_PATH,
        )
        return int(result["loaded_count"])

    count = asyncio.run(_init())
    console.print(f"[green]Database initialized, loaded {count} stocks[/green]")


# ============ Alert Command Group ============

alert_app = typer.Typer(name="alert", help="Monitor alert management")
app.add_typer(alert_app, name="alert")


@alert_app.callback(invoke_without_command=True)
def alert_callback(ctx: typer.Context) -> None:
    """Monitor alert management"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(alert_status)


@alert_app.command("start")
def alert_start(
    interval: int = typer.Option(
        60, "--interval", "-i", help="Scan interval (seconds)"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Start monitor service"""

    async def _start() -> dict[str, Any]:
        global _monitor_service

        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            _monitor_service = MonitorService(db, quote_service)
            _monitor_service.set_scan_interval(interval)
            await _monitor_service.start()

            # Record start time
            status_manager = ServiceStatusManager()
            instance = status_manager.record_start("default", interval=interval)

            # Get monitored stock count
            watch_items = await db.get_watch_items(enabled_only=True)

            return {
                "status": "started",
                "interval": interval,
                "watch_count": len(watch_items),
                "instance_id": instance.instance_id,
                "pid": instance.pid,
                "start_time": instance.start_time,
            }
        finally:
            # Note: do not close db because monitor service needs continuous access
            pass

    result = _run_async(_start(), json_output)

    if json_output:
        _print_json(result)
    else:
        console.print("[green]Monitor service started[/green]")
        console.print(f"Scan interval: {result['interval']}s")
        console.print(f"Monitored stocks: {result['watch_count']}")
        console.print(f"Service PID: {result['pid']}")
        start_dt = datetime.fromisoformat(result["start_time"])
        console.print(f"Start time: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")


@alert_app.command("stop")
def alert_stop(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Stop monitor service"""

    async def _stop() -> dict[str, Any]:
        global _monitor_service

        if _monitor_service:
            await _monitor_service.stop()
            _monitor_service = None

            # Record stop time
            status_manager = ServiceStatusManager()
            history = status_manager.record_stop("default")

            if history:
                return {
                    "status": "stopped",
                    "duration": format_duration(history.duration_seconds),
                    "duration_seconds": history.duration_seconds,
                }
            return {"status": "stopped", "duration": None}
        return {"status": "not_running"}

    result = _run_async(_stop(), json_output)

    if json_output:
        _print_json(result)
    else:
        if result["status"] == "stopped":
            console.print("[yellow]Monitor service stopped[/yellow]")
            if result.get("duration"):
                console.print(f"Uptime: {result['duration']}")
        else:
            console.print("[dim]Monitor service not running[/dim]")


@alert_app.command("status")
def alert_status(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """View monitor status"""

    async def _status() -> dict[str, Any]:
        global _monitor_service

        db = Database(str(DB_PATH))
        await db.connect()
        try:
            # Get monitored stock count
            watch_items = await db.get_watch_items(enabled_only=True)

            # Get today's alert count
            today = datetime.now().date()
            alerts = await db.get_alert_records(limit=100)
            today_alerts = [a for a in alerts if a.triggered_at.date() == today]

            # Get service status info
            status_manager = ServiceStatusManager()
            instance = status_manager.get_instance("default")

            uptime_info = None
            if instance:
                uptime_info = get_uptime_info(instance)

            return {
                "running": _monitor_service is not None and _monitor_service._running,
                "interval": _monitor_service._scan_interval if _monitor_service else 60,
                "watch_count": len(watch_items),
                "today_alerts": len(today_alerts),
                "uptime": uptime_info,
            }
        finally:
            await db.close()

    result = _run_async(_status(), json_output)

    if json_output:
        _print_json(result)
    else:
        status_text = (
            "[green]Running[/green]" if result["running"] else "[dim]Stopped[/dim]"
        )

        # Build status panel content
        panel_lines = [
            f"Status: {status_text}",
            f"Scan interval: {result['interval']}s",
            f"Monitored stocks: {result['watch_count']}",
            f"Today's alerts: {result['today_alerts']}",
        ]

        # Add uptime info
        if result.get("uptime"):
            uptime = result["uptime"]
            panel_lines.append(f"Start time: {uptime['start_time_formatted']}")
            panel_lines.append(f"Uptime: {uptime['uptime_formatted']}")
            panel_lines.append(f"Service PID: {uptime['pid']}")

        console.print(Panel("\n".join(panel_lines), title="Monitor Service Status"))


@alert_app.command("history")
def alert_history(
    code: Optional[str] = typer.Argument(None, help="Stock code (optional)"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number to display"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """View alert history"""

    async def _history() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            alerts = await db.get_alert_records(limit=limit)

            # Filter by stock code
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
                        "status": a.status,
                    }
                    for a in alerts
                ]
            }
        finally:
            await db.close()

    result = _run_async(_history(), json_output)

    if json_output:
        _print_json(result)
    else:
        alerts = result["alerts"]

        if not alerts:
            console.print("[dim]No alert records[/dim]")
            return

        title = f"Alert History ({code})" if code else "Alert History"
        table = Table(title=title)
        table.add_column("Time", style="cyan")
        table.add_column("Stock", style="white")
        table.add_column("Signal Type", style="yellow")
        table.add_column("Description", style="green")
        table.add_column("Status", style="dim")

        for alert in alerts:
            triggered_at = datetime.fromisoformat(alert["triggered_at"])
            time_str = triggered_at.strftime("%m-%d %H:%M")
            status_color = "green" if alert["status"] == "sent" else "yellow"
            table.add_row(
                time_str,
                alert["code"],
                alert["signal_name"],
                (
                    alert["message"][:20] + "..."
                    if len(alert["message"]) > 20
                    else alert["message"]
                ),
                f"[{status_color}]{alert['status']}[/{status_color}]",
            )

        console.print(table)


@alert_app.command("service-history")
def alert_service_history(
    limit: int = typer.Option(10, "--limit", "-n", help="Number to display"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """View service start/stop history"""

    status_manager = ServiceStatusManager()
    history = status_manager.get_history(limit=limit)

    if json_output:
        _print_json(
            {
                "history": [
                    {
                        "instance_id": h.instance_id,
                        "pid": h.pid,
                        "start_time": h.start_time,
                        "stop_time": h.stop_time,
                        "duration_seconds": h.duration_seconds,
                        "duration_formatted": format_duration(h.duration_seconds),
                    }
                    for h in history
                ]
            }
        )
    else:
        if not history:
            console.print("[dim]No service history records[/dim]")
            return

        table = Table(title="Service Start/Stop History")
        table.add_column("Instance ID", style="cyan", width=12)
        table.add_column("PID", style="white", width=8)
        table.add_column("Start Time", style="green", width=20)
        table.add_column("Stop Time", style="yellow", width=20)
        table.add_column("Duration", style="magenta")

        for h in history:
            start_dt = datetime.fromisoformat(h.start_time)
            stop_dt = datetime.fromisoformat(h.stop_time)
            table.add_row(
                h.instance_id,
                str(h.pid),
                start_dt.strftime("%Y-%m-%d %H:%M:%S"),
                stop_dt.strftime("%Y-%m-%d %H:%M:%S"),
                format_duration(h.duration_seconds),
            )

        console.print(table)


@app.command()
def screen(
    factors: Optional[str] = typer.Argument(None, help="Factor list, comma-separated"),
    codes: Optional[str] = typer.Option(
        None, "--codes", "-c", help="Specify stock codes, comma-separated"
    ),
    industry: Optional[str] = typer.Option(
        None,
        "--industry",
        "-i",
        help="Filter by industry, multiple industries comma-separated",
    ),
    exclude_industry: Optional[str] = typer.Option(
        None,
        "--exclude-industry",
        help="Exclude industries, multiple industries comma-separated",
    ),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Stock screening"""

    async def _screen() -> dict[str, Any]:
        factor_list = [item.strip() for item in factors.split(",")] if factors else None
        code_list = (
            [item.strip() for item in codes.split(",") if item.strip()]
            if codes
            else None
        )
        include_industries = (
            [item.strip() for item in industry.split(",")] if industry else None
        )
        exclude_industries = (
            [item.strip() for item in exclude_industry.split(",")]
            if exclude_industry
            else None
        )
        return await capabilities.screen_stocks(
            factors=factor_list,
            codes=code_list,
            include_industries=include_industries,
            exclude_industries=exclude_industries,
            limit=limit,
            db_path=DB_PATH,
        )

    result = _run_async(_screen(), json_output)

    if json_output:
        _print_json(result)
    else:
        if not result["results"]:
            console.print("[dim]No stocks matching criteria found[/dim]")
            return

        if result.get("mode") == "single_stock":
            console.print("[dim]Mode: single stock evaluation (daily factors)[/dim]")
        if result.get("data_quality"):
            console.print(f"[dim]Data quality: {result['data_quality']}[/dim]")

        table = Table(title=f"Screening Results (total {result['total']})")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("Code", style="cyan", width=8)
        table.add_column("Name", style="white", width=10)
        table.add_column("Industry", style="magenta", width=8)
        table.add_column("Hits", style="yellow", width=6)
        table.add_column("Matched Factors", style="green")

        for i, r in enumerate(result["results"], 1):
            factors_str = ",".join(r["matched_factors"][:3])
            if len(r["matched_factors"]) > 3:
                factors_str += "..."
            industry = r.get("industry") or "-"
            table.add_row(
                str(i),
                r["code"],
                r["name"] or "-",
                industry,
                str(r.get("matched_factor_count", len(r["matched_factors"]))),
                factors_str or "-",
            )

        console.print(table)


# ============ Recommend Command Group ============

recommend_app = typer.Typer(name="recommend", help="Personalized recommendations")
app.add_typer(recommend_app, name="recommend")


@recommend_app.callback(invoke_without_command=True)
def recommend_callback(ctx: typer.Context) -> None:
    """Personalized recommendations"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(recommend_generate)


@recommend_app.command("generate")
def recommend_generate(
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results"),
    style: Optional[str] = typer.Option(
        None, "--style", "-s", help="Trading style override"
    ),
    risk: Optional[str] = typer.Option(
        None, "--risk", "-r", help="Risk level override"
    ),
    min_price: Optional[float] = typer.Option(
        None, "--min-price", help="Minimum price"
    ),
    max_price: Optional[float] = typer.Option(
        None, "--max-price", help="Maximum price"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Generate personalized recommendations"""

    async def _recommend() -> dict[str, Any]:
        options: dict[str, object] = {}
        if style:
            options["trading_style"] = style
        if risk:
            options["risk_level"] = risk
        if min_price is not None:
            options["min_price"] = min_price
        if max_price is not None:
            options["max_price"] = max_price

        return await capabilities.build_recommendation_pool(
            user_id=user_id,
            limit=limit,
            options=options if options else None,
            db_path=DB_PATH,
        )

    result = _run_async(_recommend(), json_output)

    if json_output:
        _print_json(result)
    else:
        if not result["success"]:
            console.print(
                f"[red]Recommendation generation failed: {result['error']}[/red]"
            )
            return

        if not result["candidates"]:
            console.print("[dim]No candidate stocks matching criteria found[/dim]")
            return

        # Display config info
        if result["config_used"]:
            config_used = result["config_used"]
            config_panel = f"""
User: {config_used.get("user_id", "default")}
Trading style: {config_used.get("trading_style", "swing")}
Risk level: {config_used.get("risk_level", "moderate")}
Price range: {config_used.get("min_price") or "-"} ~ {config_used.get("max_price") or "-"}
"""
            console.print(Panel(config_panel.strip(), title="Recommendation Config"))

        # Display recommendation results
        table = Table(title=f"Candidate Stock Pool (total {result['total']})")
        table.add_column("Rank", style="dim", width=4)
        table.add_column("Code", style="cyan", width=8)
        table.add_column("Name", style="white", width=10)
        table.add_column("Industry", style="magenta", width=8)
        table.add_column("Hits", style="yellow", width=6)
        table.add_column("Matched Factors", style="green")

        for i, candidate in enumerate(result["candidates"], 1):
            factors_str = ",".join(candidate["matched_factors"][:2])
            if len(candidate["matched_factors"]) > 2:
                factors_str += "..."
            table.add_row(
                str(i),
                candidate["code"],
                candidate["name"] or "-",
                candidate["industry"] or "-",
                str(candidate["matched_factor_count"]),
                factors_str or "-",
            )

        console.print(table)


@recommend_app.command("config")
def recommend_config(
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="Trading style"),
    risk: Optional[str] = typer.Option(None, "--risk", "-r", help="Risk level"),
    min_price: Optional[float] = typer.Option(
        None, "--min-price", help="Minimum price"
    ),
    max_price: Optional[float] = typer.Option(
        None, "--max-price", help="Maximum price"
    ),
    reset: bool = typer.Option(False, "--reset", help="Reset to default config"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Manage recommendation config"""
    config_manager = ConfigManager()

    if reset:
        config = config_manager.reset(user_id)
        if json_output:
            _print_json(config.model_dump())
        else:
            console.print(f"[green]Reset user {user_id} config to defaults[/green]")
        return

    # Load current config
    config = config_manager.load(user_id)

    # Update config
    updates: dict[str, object] = {}
    if style:
        for s in TradingStyle:
            if s.value == style:
                updates["trading_style"] = s
                break
    if risk:
        for r in RiskLevel:
            if r.value == risk:
                updates["risk_level"] = r
                break
    if min_price is not None:
        updates["min_price"] = min_price
    if max_price is not None:
        updates["max_price"] = max_price

    if updates:
        config = config_manager.update(user_id, **updates)

    if json_output:
        # Convert to serializable dict
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        _print_json(config_data)
    else:
        panel_content = f"""
User ID: {config.user_id}
Trading style: {config.trading_style.value}
Risk level: {config.risk_level.value}
Max positions: {config.max_positions}
Position size: {config.position_size:.0%}
Price range: {config.min_price or "-"} ~ {config.max_price or "-"}
Preferred sectors: {", ".join(config.preferred_sectors) or "-"}
Excluded sectors: {", ".join(config.excluded_sectors) or "-"}
"""
        console.print(Panel(panel_content.strip(), title=f"User Config: {user_id}"))

        # Display available options
        console.print("\n[bold]Available trading styles:[/bold]")
        for s in TradingStyle:
            marker = "*" if s == config.trading_style else " "
            console.print(f"  {marker} {s.value}")

        console.print("\n[bold]Available risk levels:[/bold]")
        for r in RiskLevel:
            marker = "*" if r == config.risk_level else " "
            console.print(f"  {marker} {r.value}")


# ============ Config Command Group ============

config_app = typer.Typer(name="config", help="Configuration management")
app.add_typer(config_app, name="config")


@config_app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context) -> None:
    """Configuration management"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(config_show)


@config_app.command("show")
def config_show(
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Show current configuration"""
    config_manager = ConfigManager()
    config = config_manager.load(user_id)

    if json_output:
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        _print_json(config_data)
    else:
        panel_content = f"""
User ID: {config.user_id}
Trading style: {config.trading_style.value}
Risk level: {config.risk_level.value}
Max positions: {config.max_positions}
Position size: {config.position_size:.0%}
Price range: {config.min_price or "-"} ~ {config.max_price or "-"}
Preferred sectors: {", ".join(config.preferred_sectors) or "-"}
Excluded sectors: {", ".join(config.excluded_sectors) or "-"}
Alert channels: {", ".join(config.alert_channels)}
Default capital: {config.default_capital:,.0f}
Default strategy: {config.default_strategy}
"""
        console.print(Panel(panel_content.strip(), title=f"User Config: {user_id}"))


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Set a configuration item"""
    config_manager = ConfigManager()

    # Parse config value
    parsed_value = _parse_config_value(key, value)
    if parsed_value is None:
        console.print(f"[red]Unknown configuration key: {key}[/red]")
        raise typer.Exit(1)

    config = config_manager.update(user_id, **{key: parsed_value})

    if json_output:
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        _print_json(config_data)
    else:
        console.print(f"[green]Configuration updated: {key} = {value}[/green]")


def _parse_config_value(key: str, value: str) -> Optional[object]:
    """Parse configuration value"""
    # Risk level
    if key == "risk_level":
        for r in RiskLevel:
            if r.value == value:
                return r
        return None

    # Trading style
    if key == "trading_style":
        for s in TradingStyle:
            if s.value == value:
                return s
        return None

    # Numeric types
    if key in [
        "max_positions",
        "position_size",
        "min_price",
        "max_price",
        "default_capital",
    ]:
        try:
            if key in ["max_positions"]:
                return int(value)
            return float(value)
        except ValueError:
            return None

    # String list types
    if key in ["alert_channels", "preferred_sectors", "excluded_sectors"]:
        return [v.strip() for v in value.split(",")]

    # String types
    if key in ["default_strategy"]:
        return value

    return None


@config_app.command("style")
def config_style(
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Analyze and learn trading style"""
    config_manager = ConfigManager()
    analyzer = StyleAnalyzer()

    # Perform analysis and update config
    analysis = analyzer.update_user_config(user_id, config_manager)

    if json_output:
        _print_json(
            {
                "user_id": analysis.user_id,
                "trading_style": analysis.trading_style.value,
                "risk_level": analysis.risk_level.value,
                "trade_frequency": analysis.trade_frequency,
                "avg_holding_days": analysis.avg_holding_days,
                "total_trades": analysis.total_trades,
                "win_rate": analysis.win_rate,
                "profit_loss_ratio": analysis.profit_loss_ratio,
                "total_profit": analysis.total_profit,
                "preferred_sectors": analysis.preferred_sectors,
                "confidence": analysis.confidence,
            }
        )
    else:
        panel_content = f"""
Trading style: {analysis.trading_style.value}
Risk level: {analysis.risk_level.value}
Trade frequency: {analysis.trade_frequency:.1f} trades/month
Avg holding period: {analysis.avg_holding_days:.1f} days
Total trades: {analysis.total_trades}
Win rate: {analysis.win_rate:.1%}
Profit/loss ratio: {analysis.profit_loss_ratio:.2f}
Total P&L: {analysis.total_profit:,.2f}
Preferred sectors: {", ".join(analysis.preferred_sectors) or "-"}
Confidence: {analysis.confidence:.0%}
"""
        console.print(Panel(panel_content.strip(), title=f"Style Analysis: {user_id}"))

        if analysis.confidence > 0.5:
            console.print(
                "[green]Configuration automatically updated based on analysis[/green]"
            )
        else:
            console.print(
                "[yellow]Insufficient data, config not updated (more trade records needed)[/yellow]"
            )


@config_app.command("reset")
def config_reset(
    user_id: str = typer.Option("default", "--user", "-u", help="User ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Reset to default configuration"""
    config_manager = ConfigManager()
    config = config_manager.reset(user_id)

    if json_output:
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        _print_json(config_data)
    else:
        console.print(
            f"[yellow]Reset user {user_id} configuration to defaults[/yellow]"
        )


# ============ Email Configuration Commands ============

email_app = typer.Typer(name="email", help="Email configuration management")
config_app.add_typer(email_app, name="email")


@email_app.callback(invoke_without_command=True)
def email_callback(ctx: typer.Context) -> None:
    """Email configuration management"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(email_show)


@email_app.command("show")
def email_show(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Show email configuration"""
    email_config = EmailConfig.from_env()

    if json_output:
        _print_json(email_config.to_dict())
    else:
        if email_config.is_configured():
            panel_content = f"""
SMTP server: {email_config.smtp_host}:{email_config.smtp_port}
Encryption: {"SSL" if email_config.use_ssl else "TLS" if email_config.use_tls else "None"}
Sender: {email_config.sender_name} <{email_config.sender_email}>
Recipients: {", ".join(email_config.recipients)}
Subject prefix: {email_config.subject_prefix}
"""
            console.print(Panel(panel_content.strip(), title="Email Configuration"))
        else:
            console.print("[yellow]Email not configured[/yellow]")
            console.print(
                "Please set the following environment variables or use 'config email set' command:"
            )
            console.print(
                "  EMAIL_SMTP_HOST     - SMTP server address (default: smtp.qq.com)"
            )
            console.print("  EMAIL_SMTP_PORT     - SMTP port (default: 465)")
            console.print("  EMAIL_USE_SSL       - Use SSL (default: true)")
            console.print("  EMAIL_SENDER        - Sender email address")
            console.print("  EMAIL_PASSWORD      - Sender password/auth code")
            console.print("  EMAIL_RECIPIENTS    - Recipient list (comma-separated)")


@email_app.command("set")
def email_set(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Set email configuration item

    Configuration is saved to data/config.json under the email section.
    Note: Sensitive information (e.g., passwords) should be set via EMAIL_PASSWORD env var.

    Available keys:
        smtp_host      - SMTP server address
        smtp_port      - SMTP port
        use_ssl        - Use SSL (true/false)
        use_tls        - Use TLS (true/false)
        sender_email   - Sender email address
        sender_password - Sender password/auth code
        sender_name    - Sender display name
        recipients     - Recipient list (comma-separated)
        subject_prefix - Email subject prefix
    """
    # Load existing config
    config_path = Path("data/config.json")
    config_data = {}

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            console.print(f"[red]Failed to load config file: {e}[/red]")
            raise typer.Exit(1)

    # Ensure email config section exists
    if "email" not in config_data:
        config_data["email"] = {}

    # Parse and set config value
    email_key_map = {
        "smtp_host": "smtp_host",
        "smtp_port": "smtp_port",
        "use_ssl": "use_ssl",
        "use_tls": "use_tls",
        "sender_email": "sender_email",
        "sender_password": "sender_password",
        "sender_name": "sender_name",
        "recipients": "recipients",
        "subject_prefix": "subject_prefix",
    }

    if key not in email_key_map:
        console.print(f"[red]Unknown email configuration key: {key}[/red]")
        console.print(f"Available keys: {', '.join(email_key_map.keys())}")
        raise typer.Exit(1)

    # Type conversion
    if key in ["smtp_port"]:
        try:
            config_data["email"][email_key_map[key]] = int(value)
        except ValueError:
            console.print(f"[red]Invalid port number: {value}[/red]")
            raise typer.Exit(1)
    elif key in ["use_ssl", "use_tls"]:
        config_data["email"][email_key_map[key]] = value.lower() == "true"
    elif key == "recipients":
        config_data["email"][email_key_map[key]] = [v.strip() for v in value.split(",")]
    else:
        config_data["email"][email_key_map[key]] = value

    # Save config
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        console.print(f"[green]Email configuration updated: {key}[/green]")
    except Exception as e:
        console.print(f"[red]Failed to save config: {e}[/red]")
        raise typer.Exit(1)


@email_app.command("test")
def email_test(
    recipient: Optional[str] = typer.Option(None, "--to", "-t", help="Test recipient"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Send test email"""
    from .storage import AlertRecord
    from .monitor.alert_engine import send_email_notification

    # Load email config
    email_config = EmailConfig.from_env()

    # If test recipient specified, temporarily use that recipient
    if recipient:
        email_config.recipients = [recipient]

    if not email_config.is_configured():
        console.print("[red]Email not configured, please set up email info first[/red]")
        console.print(
            "Use 'config email set' command or set environment variables to configure"
        )
        raise typer.Exit(1)

    # Create test alert record
    test_alert = AlertRecord(
        id=0,
        code="TEST",
        signal_type="test",
        signal_name="Test Signal",
        message="This is a test email to verify the email notification feature is working correctly.",
        level=3,
        triggered_at=datetime.now(),
        status="pending",
        channels=["email"],
    )

    try:
        asyncio.run(send_email_notification(test_alert, email_config))
        if json_output:
            _print_json({"success": True, "recipients": email_config.recipients})
        else:
            console.print("[green]Test email sent successfully[/green]")
            console.print(f"Recipients: {', '.join(email_config.recipients)}")
    except Exception as e:
        if json_output:
            _print_json({"success": False, "error": str(e)})
        else:
            console.print(f"[red]Failed to send test email: {e}[/red]")
        raise typer.Exit(1)


@email_app.command("reset")
def email_reset(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Reset email configuration"""
    config_path = Path("data/config.json")

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            if "email" in config_data:
                del config_data["email"]

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)

                console.print("[yellow]Email configuration reset[/yellow]")
            else:
                console.print("[dim]Email configuration does not exist[/dim]")
        except Exception as e:
            console.print(f"[red]Failed to reset config: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[dim]Config file does not exist[/dim]")


app.add_typer(backtest_app, name="backtest")


app.add_typer(portfolio_app, name="portfolio")


app.add_typer(watch_app, name="watch")


# ============ Team Feedback Command ============


@app.command("team-feedback")
def team_feedback(
    code: str = typer.Argument(..., help="Stock code"),
    action: str = typer.Option(
        ..., "--action", "-a", help="Suggested action: watch_buy/wait/hold_or_reduce"
    ),
    outcome: str = typer.Option(
        ..., "--outcome", "-o", help="Feedback outcome: good/bad"
    ),
    strategy: Optional[str] = typer.Option(
        None, "--strategy", "-s", help="Associated strategy/factor"
    ),
    signals: Optional[str] = typer.Option(
        None, "--signals", help="Associated signals, comma-separated"
    ),
    note: Optional[str] = typer.Option(None, "--note", "-n", help="Additional notes"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Record Agent Team recommendation feedback for preference learning"""

    async def _record() -> dict[str, Any]:
        from .memory import FeedbackLearner

        learner = FeedbackLearner()
        signals_list = [s.strip() for s in signals.split(",")] if signals else None
        record = await learner.record_feedback(
            code=code,
            action=action,
            outcome=outcome,
            strategy=strategy,
            note=note,
            signals=signals_list,
        )
        return {
            "code": record.code,
            "action": record.action,
            "outcome": record.outcome,
            "strategy": record.strategy,
            "signals": record.signals,
            "note": record.note,
            "created_at": record.created_at.isoformat(),
        }

    # Validate parameters
    if action not in ["watch_buy", "wait", "hold_or_reduce"]:
        console.print(f"[red]Invalid action: {action}[/red]")
        console.print("Available options: watch_buy, wait, hold_or_reduce")
        raise typer.Exit(1)

    if outcome not in ["good", "bad"]:
        console.print(f"[red]Invalid outcome: {outcome}[/red]")
        console.print("Available options: good, bad")
        raise typer.Exit(1)

    result = _run_async(_record(), json_output)

    if json_output:
        _print_json(result)
    else:
        console.print(f"[green]Feedback recorded: {code} {action} {outcome}[/green]")


@app.command("feedback")
def feedback_show(
    code: Optional[str] = typer.Argument(None, help="Stock code (optional)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """View user feedback profile"""

    async def _show() -> dict[str, Any]:
        from .memory import FeedbackLearner

        learner = FeedbackLearner()
        summary = await learner.get_feedback_summary()
        return summary

    result = _run_async(_show(), json_output)

    if json_output:
        _print_json(result)
    else:
        if result.get("total", 0) == 0:
            console.print("[dim]No feedback records[/dim]")
            return

        # Display profile
        console.print(
            Panel(
                f"Samples: {result['total']}\n"
                f"Success rate: {result['success_rate']:.0%}\n"
                f"Positive: {result.get('good_count', 0)}\n"
                f"Negative: {result.get('bad_count', 0)}",
                title=f"User Profile {'- ' + code if code else ''}",
            )
        )

        # Display strategy performance
        strategy_perf = result.get("strategy_performance", {})
        if strategy_perf:
            console.print("\n[bold]Strategy Performance:[/bold]")
            for strategy, perf in strategy_perf.items():
                rate = perf.get("success_rate", 0)
                color = "green" if rate >= 0.5 else "red"
                console.print(
                    f"  {strategy}: [{color}]{rate:.0%}[/{color}] ({perf.get('total_count', 0)} times)"
                )

        # Display signal performance
        signal_perf = result.get("signal_performance", {})
        if signal_perf:
            console.print("\n[bold]Signal Performance:[/bold]")
            for signal, perf in list(signal_perf.items())[:5]:
                rate = perf.get("success_rate", 0)
                color = "green" if rate >= 0.5 else "red"
                console.print(
                    f"  {signal}: [{color}]{rate:.0%}[/{color}] ({perf.get('total_count', 0)} times)"
                )


# ============ Memory Command Group ============

memory_app = typer.Typer(name="memory", help="Agent memory management")
app.add_typer(memory_app, name="memory")


@memory_app.command("store")
def memory_store(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    key: str = typer.Option(..., "--key", "-k", help="Key"),
    value: str = typer.Option(..., "--value", "-v", help="Value"),
    session: str = typer.Option("default", "--session", "-s", help="Session ID"),
    user: str = typer.Option("default", "--user", "-u", help="User ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Store agent memory"""

    async def _store() -> dict[str, Any]:
        from .memory import MemoryStore

        store = MemoryStore()
        await store.store(
            agent_name=agent,
            session_id=session,
            user_id=user,
            key=key,
            value=value,
        )
        return {"status": "stored", "agent": agent, "key": key, "value": value}

    result = _run_async(_store(), json_output)

    if json_output:
        _print_json(result)
    else:
        console.print(f"[green]Memory stored: {agent}/{key}[/green]")


@memory_app.command("recall")
def memory_recall(
    agent: str = typer.Option(..., "--agent", "-a", help="Agent name"),
    key: str = typer.Option(..., "--key", "-k", help="Key"),
    user: str = typer.Option("default", "--user", "-u", help="User ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of results"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Recall agent memory"""

    async def _recall() -> list[dict[str, Any]]:
        from .memory import MemoryStore

        store = MemoryStore()
        entries = await store.recall(
            agent_name=agent,
            user_id=user,
            key=key,
            limit=limit,
        )
        return entries

    entries = _run_async(_recall(), json_output)

    if json_output:
        _print_json({"entries": entries})
    else:
        if not entries:
            console.print("[dim]No memories found[/dim]")
            return

        console.print(f"[bold]{agent}/{key} memories:[/bold]")
        for entry in entries:
            created = entry.get("created_at", "")[:19]
            console.print(f"  [{created}] {entry.get('value')}")


@memory_app.command("history")
def memory_history(
    agent: Optional[str] = typer.Option(
        None, "--agent", "-a", help="Agent name (optional)"
    ),
    user: str = typer.Option("default", "--user", "-u", help="User ID"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of results"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """View session history"""

    async def _history() -> list[dict[str, Any]]:
        from .memory import MemoryStore

        store = MemoryStore()
        entries = await store.get_session_history(
            user_id=user,
            agent_name=agent,
            limit=limit,
        )
        return entries

    entries = _run_async(_history(), json_output)

    if json_output:
        _print_json({"entries": entries})
    else:
        if not entries:
            console.print("[dim]No history records[/dim]")
            return

        table = Table(title=f"Session History ({agent or 'All Agents'})")
        table.add_column("Time", style="cyan", width=19)
        table.add_column("Agent", style="white", width=15)
        table.add_column("Key", style="yellow", width=15)
        table.add_column("Value", style="green")

        for entry in entries:
            created = entry.get("created_at", "")[:19]
            table.add_row(
                created,
                entry.get("agent_name", ""),
                entry.get("key", ""),
                str(entry.get("value", ""))[:50],
            )

        console.print(table)


@memory_app.command("clear")
def memory_clear(
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent name"),
    user: Optional[str] = typer.Option(None, "--user", "-u", help="User ID"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="Key"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Clear memories"""

    async def _clear() -> int:
        from .memory import MemoryStore

        store = MemoryStore()
        count = await store.clear(
            agent_name=agent,
            user_id=user,
            key=key,
        )
        return count

    count = _run_async(_clear(), json_output)

    if json_output:
        _print_json({"cleared": count})
    else:
        console.print(f"[yellow]Cleared {count} memories[/yellow]")


@app.command("build-pdf")
def build_pdf(
    path: str = typer.Argument(
        ..., help="Directory containing .tex file, or path to a .tex file"
    ),
    tex_file: Optional[str] = typer.Option(
        None, "--file", "-f", help="Specific .tex filename (default: main.tex)"
    ),
    clean: bool = typer.Option(
        True, "--clean/--no-clean", help="Remove build artifacts after compilation"
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Compile LaTeX to PDF using XeLaTeX (two passes for TOC/refs)"""
    import shutil
    import subprocess

    target = Path(path)
    if target.is_file() and target.suffix == ".tex":
        work_dir = target.parent
        tex_name = target.name
    elif target.is_dir():
        work_dir = target
        tex_name = tex_file or "main.tex"
    else:
        console.print(
            f"[red]Error: '{path}' is not a valid directory or .tex file[/red]"
        )
        raise typer.Exit(1)

    tex_path = work_dir / tex_name
    if not tex_path.exists():
        console.print(f"[red]Error: {tex_path} not found[/red]")
        raise typer.Exit(1)

    xelatex = shutil.which("xelatex")
    if not xelatex:
        msg = "xelatex not found. Install TeX Live: brew install --cask mactex-no-gui"
        if json_output:
            _print_json({"success": False, "error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    cmd = [xelatex, "-interaction=nonstopmode", "-halt-on-error", tex_name]
    pdf_name = tex_name.replace(".tex", ".pdf")
    artifacts = [".aux", ".log", ".out", ".toc", ".fls", ".fdb_latexmk", ".synctex.gz"]

    if not json_output:
        console.print(f"[blue]Compiling {tex_path}...[/blue]")

    success = True
    error_msg = ""

    for pass_num in (1, 2):
        result = subprocess.run(
            cmd,
            cwd=str(work_dir),
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            success = False
            log_path = work_dir / tex_name.replace(".tex", ".log")
            if log_path.exists():
                log_content = log_path.read_text(errors="replace")
                errors = [
                    line for line in log_content.splitlines() if line.startswith("!")
                ]
                error_msg = "\n".join(errors[:10]) if errors else result.stderr[-500:]
            else:
                error_msg = result.stderr[-500:]
            break

    pdf_path = work_dir / pdf_name
    page_count = 0
    if success and pdf_path.exists():
        try:
            content = pdf_path.read_bytes()
            page_count = content.count(b"/Type /Page") - content.count(b"/Type /Pages")
        except Exception:
            pass

    if clean and success:
        stem = tex_name.replace(".tex", "")
        for ext in artifacts:
            artifact = work_dir / (stem + ext)
            if artifact.exists():
                artifact.unlink()

    if json_output:
        _print_json(
            {
                "success": success,
                "pdf": str(pdf_path) if success else None,
                "pages": page_count,
                "error": error_msg if not success else None,
            }
        )
    else:
        if success:
            console.print(f"[green]✓ Built: {pdf_path} ({page_count} pages)[/green]")
        else:
            console.print("[red]✗ Build failed[/red]")
            if error_msg:
                console.print(f"[dim]{error_msg}[/dim]")


@app.command("sync-agents")
def sync_agents(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Sync .agents/ source of truth to .claude/ and .codex/ discovery directories"""
    import shutil

    project_root = Path(__file__).parent.parent.parent.parent
    agents_dir = project_root / ".agents"
    claude_dir = project_root / ".claude"
    codex_dir = project_root / ".codex"

    team_dir = agents_dir / "team"
    skills_dir = agents_dir / "skills"
    config_path = team_dir / "agents.json"

    if not config_path.exists():
        console.print(f"[red]Error: {config_path} not found[/red]")
        raise typer.Exit(1)

    config = json.loads(config_path.read_text())
    changes = {"claude_agents": 0, "codex_agents": 0, "skills_synced": 0}

    # --- Generate .claude/agents/*.md ---
    claude_agents_dir = claude_dir / "agents"
    if claude_agents_dir.exists():
        shutil.rmtree(claude_agents_dir)
    claude_agents_dir.mkdir(parents=True)

    for name, meta in config.items():
        prompt_file = team_dir / f"{name}.md"
        if not prompt_file.exists():
            continue
        content = prompt_file.read_text()
        tools_str = ", ".join(meta["tools"])
        output = f"""---
name: {name}
description: {meta['description']}
tools: {tools_str}
model: sonnet
---

{content}"""
        (claude_agents_dir / f"{name}.md").write_text(output)
        changes["claude_agents"] += 1

    # --- Generate .codex/agents/*.toml ---
    codex_agents_dir = codex_dir / "agents"
    if codex_agents_dir.exists():
        shutil.rmtree(codex_agents_dir)
    codex_agents_dir.mkdir(parents=True)

    for name, meta in config.items():
        prompt_file = team_dir / f"{name}.md"
        if not prompt_file.exists():
            continue
        content = prompt_file.read_text()
        sandbox = meta.get("sandbox_mode", "read-only")
        output = f'''name = "{name}"
description = "{meta['description']}"
sandbox_mode = "{sandbox}"
developer_instructions = """
{content}
"""
'''
        (codex_agents_dir / f"{name}.toml").write_text(output)
        changes["codex_agents"] += 1

    # --- Sync skills ---
    for target in [claude_dir / "skills", codex_dir / "skills"]:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(skills_dir, target)
    changes["skills_synced"] = len(list(skills_dir.glob("*/SKILL.md")))

    if json_output:
        _print_json({"success": True, **changes})
    else:
        console.print(
            f"[green]✓ Synced {changes['claude_agents']} agents to .claude/agents/[/green]"
        )
        console.print(
            f"[green]✓ Synced {changes['codex_agents']} agents to .codex/agents/[/green]"
        )
        console.print(
            f"[green]✓ Synced {changes['skills_synced']} skills to .claude/skills/ and .codex/skills/[/green]"
        )


if __name__ == "__main__":
    app()
