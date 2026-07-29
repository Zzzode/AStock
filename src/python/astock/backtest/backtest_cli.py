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
    walk_forward_train_bars: Optional[int] = typer.Option(
        None, "--walk-forward-train-bars", min=20, help="Fixed-parameter in-sample bars per fold."
    ),
    walk_forward_test_bars: Optional[int] = typer.Option(
        None, "--walk-forward-test-bars", min=1, help="Out-of-sample bars per fold."
    ),
    parameter_sets_path: Optional[Path] = typer.Option(
        None,
        "--parameter-sets-path",
        help="JSON array of candidate parameter objects; requires both walk-forward windows.",
    ),
    selection_metric: str = typer.Option(
        "total_return", "--selection-metric", help="Training-only parameter selection metric."
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Run strategy backtest"""

    async def _run() -> dict[str, Any]:
        candidate_parameter_sets = _read_parameter_sets(parameter_sets_path)
        return await capabilities.run_signal_backtest(
            code,
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            capital=capital,
            walk_forward_train_bars=walk_forward_train_bars,
            walk_forward_test_bars=walk_forward_test_bars,
            candidate_parameter_sets=candidate_parameter_sets,
            selection_metric=selection_metric,
            db_path=DB_PATH,
        )

    result = _run_async(_run(), json_output)

    if json_output:
        _print_json(result)
    else:
        if "error" in result:
            console.print(f"[red]Error: {result['error']}[/red]")
            raise typer.Exit(1)

        _display_backtest_result(result)


@app.command("freeze-local")
def freeze_local_signal_replay(
    code: str = typer.Argument(..., help="Stock code with locally persisted daily bars"),
    archive_directory: Path = typer.Option(
        DB_PATH.parent / "signal-replay-archives",
        "--archive-directory",
        help="Directory for immutable replay archives and their input manifests.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Freeze local daily bars before deterministic paper-signal replay."""

    async def _run() -> dict[str, Any]:
        return await capabilities.freeze_local_signal_replay_input(
            code,
            archive_directory=archive_directory,
            db_path=DB_PATH,
        )

    result = _run_async(_run(), json_output)
    if json_output:
        _print_json(result)
    else:
        console.print(f"Frozen signal input: {result.get('replay_input_path', 'not written')}")


@app.command("run-frozen")
def run_frozen_signal_replay(
    replay_input_path: Path = typer.Argument(..., help="Frozen .replay.json input manifest"),
    strategy: str = typer.Option(..., "--strategy", "-s", help="Strategy name"),
    capital: float = typer.Option(100000.0, "--capital", "-c", help="Initial capital"),
    source_archive_path: Optional[Path] = typer.Option(
        None,
        "--source-archive-path",
        help="Optional immutable raw archive; defaults to the sibling content-addressed JSON file.",
    ),
    walk_forward_train_bars: Optional[int] = typer.Option(
        None, "--walk-forward-train-bars", min=20, help="Rolling training bars per fold."
    ),
    walk_forward_test_bars: Optional[int] = typer.Option(
        None, "--walk-forward-test-bars", min=1, help="Out-of-sample bars per fold."
    ),
    parameter_sets_path: Optional[Path] = typer.Option(
        None,
        "--parameter-sets-path",
        help="JSON array of candidate parameter objects; enables training-only selection.",
    ),
    selection_metric: str = typer.Option(
        "total_return", "--selection-metric", help="Training-only parameter selection metric."
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Replay one source-frozen signal input without fetching market data."""
    try:
        replay_input = json.loads(replay_input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        if json_output:
            _print_json({"error": f"Unable to read frozen replay input: {error}"})
        else:
            console.print(f"[red]Unable to read frozen replay input: {error}[/red]")
        raise typer.Exit(1) from error
    manifest = replay_input.get("source_manifest") if isinstance(replay_input, dict) else None
    archive_id = str(manifest.get("archive_id") or "") if isinstance(manifest, dict) else ""
    archive_path = source_archive_path or replay_input_path.parent / (
        archive_id.removeprefix("sha256:") + ".json"
    )
    try:
        candidate_parameter_sets = _read_parameter_sets(parameter_sets_path)
        result = capabilities.run_frozen_signal_backtest(
            replay_input,
            strategy=strategy,
            capital=capital,
            source_archive_path=archive_path,
            walk_forward_train_bars=walk_forward_train_bars,
            walk_forward_test_bars=walk_forward_test_bars,
            candidate_parameter_sets=candidate_parameter_sets,
            selection_metric=selection_metric,
        )
    except ValueError as error:
        if json_output:
            _print_json({"error": str(error)})
        else:
            console.print(f"[red]Error: {error}[/red]")
        raise typer.Exit(1) from error
    if json_output:
        _print_json(result)
    else:
        _display_backtest_result(result)


@app.command("freeze-akshare-portfolio")
def freeze_akshare_portfolio_replay(
    codes: str = typer.Argument(..., help="Comma-separated A-share stock codes"),
    target_weights_path: Path = typer.Option(
        ..., "--target-weights-path", help="JSON file mapping rebalance dates to code weights."
    ),
    start_date: str = typer.Option(..., "--start-date", help="YYYY-MM-DD"),
    end_date: str = typer.Option(..., "--end-date", help="YYYY-MM-DD"),
    archive_directory: Path = typer.Option(
        DB_PATH.parent / "portfolio-replay-archives",
        "--archive-directory",
        help="Directory for immutable replay archives and input manifests.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Fetch AkShare bars and freeze a research-only portfolio replay input."""
    try:
        target_weights = json.loads(target_weights_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        if json_output:
            _print_json({"error": f"Unable to read target weights: {error}"})
        else:
            console.print(f"[red]Unable to read target weights: {error}[/red]")
        raise typer.Exit(1) from error
    if not isinstance(target_weights, dict):
        if json_output:
            _print_json({"error": "target weights JSON must be an object"})
        else:
            console.print("[red]target weights JSON must be an object[/red]")
        raise typer.Exit(1)

    async def _run() -> dict[str, Any]:
        return await capabilities.build_akshare_daily_portfolio_replay_input(
            [code.strip() for code in codes.split(",") if code.strip()],
            target_weights,
            start_date=start_date,
            end_date=end_date,
            archive_directory=archive_directory,
        )

    result = _run_async(_run(), json_output)
    if json_output:
        _print_json(result)
    else:
        console.print(f"Frozen portfolio input: {result.get('replay_input_path', 'not written')}")


@app.command("run-frozen-portfolio")
def run_frozen_portfolio_replay(
    replay_input_path: Path = typer.Argument(..., help="Frozen .portfolio.replay.json input manifest"),
    initial_capital: float = typer.Option(100_000.0, "--capital", "-c", help="Initial paper capital"),
    slippage_bps: float = typer.Option(0.0, "--slippage-bps", help="Paper slippage assumption in basis points"),
    max_participation_rate: Optional[float] = typer.Option(
        None, "--max-participation-rate", help="Optional max share of reported daily volume"
    ),
    source_archive_path: Optional[Path] = typer.Option(
        None,
        "--source-archive-path",
        help="Optional immutable raw archive; defaults to the sibling content-addressed JSON file.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Run an archived public-data paper portfolio replay without refetching."""
    try:
        replay_input = json.loads(replay_input_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        if json_output:
            _print_json({"error": f"Unable to read frozen portfolio input: {error}"})
        else:
            console.print(f"[red]Unable to read frozen portfolio input: {error}[/red]")
        raise typer.Exit(1) from error
    manifest = replay_input.get("source_manifest") if isinstance(replay_input, dict) else None
    archive_id = str(manifest.get("archive_id") or "") if isinstance(manifest, dict) else ""
    archive_path = source_archive_path or replay_input_path.parent / (
        archive_id.removeprefix("sha256:") + ".json"
    )
    result = capabilities.run_frozen_portfolio_backtest(
        replay_input,
        source_archive_path=archive_path,
        initial_capital=initial_capital,
        slippage_bps=slippage_bps,
        max_participation_rate=max_participation_rate,
    )
    if json_output:
        _print_json(result)
    else:
        console.print(
            f"Paper portfolio result: {result['total_return']:.2%}; "
            f"formal_decision_eligible={result['formal_decision_eligible']}"
        )


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


def _read_parameter_sets(path: Optional[Path]) -> Optional[list[dict[str, Any]]]:
    """Read an explicit, reproducible candidate set instead of inventing one."""
    if path is None:
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read parameter sets: {error}") from error
    if not isinstance(payload, list) or any(not isinstance(item, dict) for item in payload):
        raise ValueError("parameter sets must be a JSON array of objects")
    return payload


def _display_backtest_result(result: dict[str, Any]) -> None:
    if result.get("schema_version") in {
        "walk_forward_backtest.v1",
        "rolling_model_selection.v1",
    }:
        _display_walk_forward_result(result)
        return
    _display_result(result)


def _display_walk_forward_result(result: dict[str, Any]) -> None:
    label = (
        "Rolling Model Selection"
        if result.get("schema_version") == "rolling_model_selection.v1"
        else "Fixed-Parameter Walk-Forward"
    )
    console.print(
        Panel(
            "\n".join(
                [
                    f"[bold cyan]Strategy:[/bold cyan] {result['strategy']}",
                    f"[bold cyan]Folds:[/bold cyan] {result['fold_count']}",
                    f"[bold cyan]Mean OOS return:[/bold cyan] {result['mean_out_of_sample_return']:.2%}",
                    f"[bold cyan]Positive OOS folds:[/bold cyan] {result['positive_fold_ratio']:.1%}",
                    "[yellow]Research-only validation; not a continuous portfolio or tradability claim.[/yellow]",
                ]
            ),
            title=label,
        )
    )


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
