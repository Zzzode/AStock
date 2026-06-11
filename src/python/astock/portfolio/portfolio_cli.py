"""Portfolio management CLI"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..storage import Database
from ..quote import QuoteService
from .portfolio import Portfolio, PortfolioManager, PortfolioStats
from .risk_manager import RiskManager, RiskLimits

app = typer.Typer(name="portfolio", help="Portfolio management")
console = Console()

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"
PORTFOLIO_PATH = Path(__file__).parent.parent.parent.parent / "data" / "portfolio.json"


def _print_json(data: Any) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def _load_portfolio() -> dict[str, Any]:
    if PORTFOLIO_PATH.exists():
        with open(PORTFOLIO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "name": "default",
        "initial_capital": 100000.0,
        "cash": 100000.0,
        "positions": {},
        "trades": [],
        "created_at": datetime.now().isoformat(),
    }


def _save_portfolio(data: dict[str, Any]) -> None:
    PORTFOLIO_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PORTFOLIO_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.command("show")
def portfolio_show(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Show portfolio overview"""
    data = _load_portfolio()
    positions = data.get("positions", {})

    total_market_value = sum(
        p["shares"] * p["current_price"] for p in positions.values()
    )
    total_value = data["cash"] + total_market_value
    total_cost = sum(p["shares"] * p["cost_price"] for p in positions.values())
    total_pnl = total_market_value - total_cost
    pnl_percent = (total_value - data["initial_capital"]) / data["initial_capital"] * 100

    result = {
        "name": data["name"],
        "initial_capital": data["initial_capital"],
        "cash": data["cash"],
        "market_value": total_market_value,
        "total_value": total_value,
        "profit_loss": total_pnl,
        "profit_loss_percent": pnl_percent,
        "position_count": len(positions),
    }

    if json_output:
        _print_json(result)
    else:
        pnl_color = "green" if total_pnl >= 0 else "red"
        panel_content = (
            f"Initial capital: {data['initial_capital']:,.0f}\n"
            f"Cash: {data['cash']:,.0f}\n"
            f"Market value: {total_market_value:,.0f}\n"
            f"Total value: {total_value:,.0f}\n"
            f"P/L: [{pnl_color}]{total_pnl:+,.0f} ({pnl_percent:+.2f}%)[/{pnl_color}]\n"
            f"Positions: {len(positions)}"
        )
        console.print(Panel(panel_content, title="Portfolio Overview"))


@app.command("positions")
def portfolio_positions(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Show all positions"""
    data = _load_portfolio()
    positions = data.get("positions", {})

    if json_output:
        _print_json({"positions": list(positions.values())})
    else:
        if not positions:
            console.print("[dim]No positions[/dim]")
            return

        table = Table(title="Current Positions")
        table.add_column("Code", style="cyan")
        table.add_column("Name")
        table.add_column("Shares", justify="right")
        table.add_column("Cost", justify="right")
        table.add_column("Current", justify="right")
        table.add_column("P/L", justify="right")
        table.add_column("P/L%", justify="right")

        for code, pos in positions.items():
            pnl = (pos["current_price"] - pos["cost_price"]) * pos["shares"]
            pnl_pct = (pos["current_price"] - pos["cost_price"]) / pos["cost_price"] * 100 if pos["cost_price"] > 0 else 0
            pnl_color = "green" if pnl >= 0 else "red"
            table.add_row(
                code,
                pos.get("name") or "-",
                f"{pos['shares']:.0f}",
                f"{pos['cost_price']:.2f}",
                f"{pos['current_price']:.2f}",
                f"[{pnl_color}]{pnl:+,.0f}[/{pnl_color}]",
                f"[{pnl_color}]{pnl_pct:+.2f}%[/{pnl_color}]",
            )

        console.print(table)


@app.command("buy")
def portfolio_buy(
    code: str = typer.Argument(..., help="Stock code"),
    shares: int = typer.Argument(..., help="Number of shares (must be multiple of 100)"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Buy price (default: latest quote)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Record a buy trade"""

    async def _get_price() -> float:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            result = await service.get_realtime(code)
            return result["price"]
        finally:
            await db.close()

    if price is None:
        price = asyncio.run(_get_price())

    data = _load_portfolio()
    required = shares * price

    if required > data["cash"]:
        msg = f"Insufficient cash: need {required:,.0f}, have {data['cash']:,.0f}"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    data["cash"] -= required
    positions = data.setdefault("positions", {})

    if code in positions:
        pos = positions[code]
        total_cost = pos["cost_price"] * pos["shares"] + price * shares
        total_shares = pos["shares"] + shares
        pos["cost_price"] = total_cost / total_shares
        pos["shares"] = total_shares
        pos["current_price"] = price
        pos["updated_at"] = datetime.now().isoformat()
    else:
        positions[code] = {
            "code": code,
            "name": None,
            "shares": shares,
            "cost_price": price,
            "current_price": price,
            "opened_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

    trade = {
        "code": code,
        "action": "buy",
        "shares": shares,
        "price": price,
        "amount": required,
        "timestamp": datetime.now().isoformat(),
    }
    data.setdefault("trades", []).append(trade)
    _save_portfolio(data)

    if json_output:
        _print_json(trade)
    else:
        console.print(f"[green]Bought {shares} shares of {code} @ {price:.2f} (total: {required:,.0f})[/green]")


@app.command("sell")
def portfolio_sell(
    code: str = typer.Argument(..., help="Stock code"),
    shares: int = typer.Argument(..., help="Number of shares to sell"),
    price: Optional[float] = typer.Option(None, "--price", "-p", help="Sell price (default: latest quote)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Record a sell trade"""

    async def _get_price() -> float:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            result = await service.get_realtime(code)
            return result["price"]
        finally:
            await db.close()

    if price is None:
        price = asyncio.run(_get_price())

    data = _load_portfolio()
    positions = data.get("positions", {})

    if code not in positions:
        msg = f"No position for {code}"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    pos = positions[code]
    if shares > pos["shares"]:
        msg = f"Insufficient shares: have {pos['shares']:.0f}, selling {shares}"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    proceeds = shares * price
    data["cash"] += proceeds
    pos["shares"] -= shares
    pos["current_price"] = price
    pos["updated_at"] = datetime.now().isoformat()

    if pos["shares"] <= 0:
        del positions[code]

    pnl = (price - pos["cost_price"]) * shares

    trade = {
        "code": code,
        "action": "sell",
        "shares": shares,
        "price": price,
        "amount": proceeds,
        "pnl": pnl,
        "timestamp": datetime.now().isoformat(),
    }
    data.setdefault("trades", []).append(trade)
    _save_portfolio(data)

    if json_output:
        _print_json(trade)
    else:
        pnl_color = "green" if pnl >= 0 else "red"
        console.print(f"[yellow]Sold {shares} shares of {code} @ {price:.2f} (proceeds: {proceeds:,.0f}, P/L: [{pnl_color}]{pnl:+,.0f}[/{pnl_color}])[/yellow]")


@app.command("trades")
def portfolio_trades(
    code: Optional[str] = typer.Argument(None, help="Stock code (optional filter)"),
    limit: int = typer.Option(20, "--limit", "-n", help="Number of records"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """View trade history"""
    data = _load_portfolio()
    trades = data.get("trades", [])

    if code:
        trades = [t for t in trades if t["code"] == code]

    trades = trades[-limit:]

    if json_output:
        _print_json({"trades": trades})
    else:
        if not trades:
            console.print("[dim]No trade records[/dim]")
            return

        table = Table(title="Trade History")
        table.add_column("Time", style="cyan")
        table.add_column("Code", style="white")
        table.add_column("Action")
        table.add_column("Shares", justify="right")
        table.add_column("Price", justify="right")
        table.add_column("Amount", justify="right")

        for t in trades:
            ts = t["timestamp"][:16].replace("T", " ")
            action_color = "green" if t["action"] == "buy" else "red"
            table.add_row(
                ts,
                t["code"],
                f"[{action_color}]{t['action']}[/{action_color}]",
                str(t["shares"]),
                f"{t['price']:.2f}",
                f"{t['amount']:,.0f}",
            )

        console.print(table)


@app.command("import")
def portfolio_import(
    file: str = typer.Argument(..., help="CSV file path (columns: date,code,action,shares,price)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Import trade records from CSV"""
    import csv

    file_path = Path(file)
    if not file_path.exists():
        msg = f"File not found: {file}"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    data = _load_portfolio()
    imported = 0

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            trade = {
                "code": row["code"].strip(),
                "action": row["action"].strip().lower(),
                "shares": int(float(row["shares"])),
                "price": float(row["price"]),
                "amount": int(float(row["shares"])) * float(row["price"]),
                "timestamp": row.get("date", datetime.now().isoformat()).strip(),
            }
            data.setdefault("trades", []).append(trade)
            imported += 1

    _save_portfolio(data)

    if json_output:
        _print_json({"imported": imported})
    else:
        console.print(f"[green]Imported {imported} trade records[/green]")


@app.command("risk")
def portfolio_risk(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Show portfolio risk metrics"""
    data = _load_portfolio()
    positions = data.get("positions", {})
    trades = data.get("trades", [])

    if not positions:
        if json_output:
            _print_json({"error": "No positions to assess"})
        else:
            console.print("[dim]No positions to assess[/dim]")
        return

    total_market_value = sum(p["shares"] * p["current_price"] for p in positions.values())
    total_value = data["cash"] + total_market_value

    max_pos_value = max((p["shares"] * p["current_price"] for p in positions.values()), default=0)
    concentration = max_pos_value / total_value if total_value > 0 else 0

    risk_manager = RiskManager()
    result = {
        "total_value": total_value,
        "position_count": len(positions),
        "concentration_risk": concentration,
        "max_single_position_pct": concentration * 100,
        "cash_ratio": data["cash"] / total_value * 100 if total_value > 0 else 100,
        "limit_checks": {
            "max_position_size": risk_manager.limits.max_position_size * 100,
            "max_positions": risk_manager.limits.max_positions,
            "stop_loss": risk_manager.limits.stop_loss_percent * 100,
            "take_profit": risk_manager.limits.take_profit_percent * 100,
        },
    }

    if json_output:
        _print_json(result)
    else:
        panel_content = (
            f"Total value: {total_value:,.0f}\n"
            f"Positions: {len(positions)}/{risk_manager.limits.max_positions}\n"
            f"Cash ratio: {result['cash_ratio']:.1f}%\n"
            f"Max single position: {concentration * 100:.1f}% (limit: {risk_manager.limits.max_position_size * 100:.0f}%)\n"
            f"Stop-loss: {risk_manager.limits.stop_loss_percent * 100:.0f}%\n"
            f"Take-profit: {risk_manager.limits.take_profit_percent * 100:.0f}%"
        )
        console.print(Panel(panel_content, title="Portfolio Risk Metrics"))


@app.command("reset")
def portfolio_reset(
    capital: float = typer.Option(100000.0, "--capital", "-c", help="Initial capital"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Reset portfolio to initial state"""
    data = {
        "name": "default",
        "initial_capital": capital,
        "cash": capital,
        "positions": {},
        "trades": [],
        "created_at": datetime.now().isoformat(),
    }
    _save_portfolio(data)

    if json_output:
        _print_json({"status": "reset", "capital": capital})
    else:
        console.print(f"[yellow]Portfolio reset with capital {capital:,.0f}[/yellow]")


if __name__ == "__main__":
    app()
