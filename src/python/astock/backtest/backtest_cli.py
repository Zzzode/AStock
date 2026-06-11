"""Backtest subprocess adapter commands."""

import asyncio
from contextlib import nullcontext, redirect_stdout
import json
import sys
from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .. import capabilities

app = typer.Typer(name="backtest", help="Strategy backtesting")
console = Console()

# Default database path
DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "stocks.db"


def _print_json(data: Any) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def _json_stdout_guard(enabled: bool):
    return redirect_stdout(sys.stderr) if enabled else nullcontext()


def _run_async(coro: Any, json_output: bool) -> Any:
    with _json_stdout_guard(json_output):
        return asyncio.run(coro)


@app.command("run")
def run_backtest(
    code: str = typer.Argument(..., help="Stock code"),
    strategy: str = typer.Option(..., "--strategy", "-s", help="Strategy name"),
    start_date: Optional[str] = typer.Option(
        None, "--start-date", help="Start date (YYYY-MM-DD)"
    ),
    end_date: Optional[str] = typer.Option(
        None, "--end-date", help="End date (YYYY-MM-DD)"
    ),
    capital: float = typer.Option(100000.0, "--capital", "-c", help="Initial capital"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Run strategy backtest"""

    async def _run() -> dict[str, Any]:
        return await capabilities.run_signal_backtest(
            code,
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            capital=capital,
            db_path=DB_PATH,
        )

    result = _run_async(_run(), json_output)

    if json_output:
        _print_json(result)
    else:
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            raise typer.Exit(1)

        _display_result(result)


@app.command("list")
def list_strategies(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """List available strategies"""
    strategies = capabilities.list_signal_strategies()

    if json_output:
        _print_json(strategies)
    else:
        table = Table(title="Available Strategies")
        table.add_column("Name", style="cyan")
        table.add_column("Description", style="green")

        for s in strategies:
            table.add_row(s["name"], s["description"])

        console.print(table)


def _display_result(result: dict[str, Any]) -> None:
    """Display backtest result"""
    # Return metrics panel
    total_return = result["total_return"]
    return_color = "green" if total_return >= 0 else "red"
    return_sign = "+" if total_return >= 0 else ""

    annual_return = result["annual_return"]
    annual_color = "green" if annual_return >= 0 else "red"
    annual_sign = "+" if annual_return >= 0 else ""

    panel_content = f"""[bold cyan]Strategy:[/bold cyan] {result['strategy']}
[bold cyan]Backtest period:[/bold cyan] {result['start_date']} ~ {result['end_date']}

[bold yellow]Return Metrics[/bold yellow]
Total return: [{return_color}]{return_sign}{total_return:.2f}%[/{return_color}]
Annualized return: [{annual_color}]{annual_sign}{annual_return:.2f}%[/{annual_color}]
Max drawdown: [red]-{result['max_drawdown']:.2f}%[/red]
Sharpe ratio: {result['sharpe_ratio']:.2f}

[bold yellow]Trade Statistics[/bold yellow]
Initial capital: {result['initial_capital']:,.0f} CNY
Final capital: {result['final_capital']:,.0f} CNY
Trade count: {len(result['trades'])}
Win rate: {result['win_rate']:.1f}%"""

    console.print(Panel(panel_content, title=f"Backtest Result - {result['code']}"))

    # Trade records table
    trades = result["trades"]
    if trades:
        console.print("\n[bold yellow]Trade Records:[/bold yellow]")
        table = Table()
        table.add_column("Date", style="cyan")
        table.add_column("Signal", style="yellow")
        table.add_column("Price", style="white")
        table.add_column("Shares", style="white")
        table.add_column("Amount", style="green")
        table.add_column("Commission", style="dim")

        # Show only the last 10 records
        for trade in trades[-10:]:
            signal_color = "green" if trade["signal"] == "buy" else "red"
            table.add_row(
                trade["date"],
                f"[{signal_color}]{trade['signal']}[/{signal_color}]",
                f"{trade['price']:.2f}",
                str(trade["shares"]),
                f"{trade['value']:,.0f}",
                f"{trade['commission']:.2f}",
            )

        console.print(table)

        if len(trades) > 10:
            console.print(f"[dim]... {len(trades)} trade records in total[/dim]")


if __name__ == "__main__":
    app()
