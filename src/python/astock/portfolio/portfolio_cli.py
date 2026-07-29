"""Portfolio management CLI"""

import asyncio
import hashlib
from functools import lru_cache
import json
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Any

import typer
import akshare as ak
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..storage import Database
from ..quote import QuoteService
from .risk_manager import RiskManager
from .factor_governance import validate_factor_risk_context
from .governance import (
    audit_paper_portfolio_governance,
    validate_governed_paper_entry,
    validate_governed_paper_exit,
)

app = typer.Typer(name="portfolio", help="Portfolio management")
console = Console()

PROJECT_ROOT = Path(__file__).resolve().parents[4]
LEGACY_DATA_DIR = Path(__file__).resolve().parents[3] / "data"
DATA_DIR = PROJECT_ROOT / "data"
DB_PATH = DATA_DIR / "stocks.db"
PORTFOLIO_PATH = DATA_DIR / "portfolio.json"
LEGACY_PORTFOLIO_PATH = LEGACY_DATA_DIR / "portfolio.json"
DEFAULT_RESEARCH_LEDGER_PATH = PORTFOLIO_PATH.parent / "research-ledger.json"
DEFAULT_RESTRICTED_LIST_PATH = DATA_DIR / "restricted-list.json"


def _print_json(data: Any) -> None:
    sys.stdout.write(json.dumps(data, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")


def _load_portfolio() -> dict[str, Any]:
    if PORTFOLIO_PATH.exists():
        with open(PORTFOLIO_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # The original nested CLI path resolved to ``src/data``. Preserve existing
    # paper records on first use, but save all future updates to the canonical
    # project-root data directory shared by the market desk and research ledger.
    if LEGACY_PORTFOLIO_PATH.exists():
        with open(LEGACY_PORTFOLIO_PATH, "r", encoding="utf-8") as f:
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


def _resolve_trade_day(value: Optional[str]) -> date:
    if value is None:
        return datetime.now().date()
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise typer.BadParameter("trade-date must be YYYY-MM-DD") from exc


@lru_cache(maxsize=1)
def _exchange_trading_days() -> frozenset[date]:
    """Load the exchange calendar; lack of an authority blocks paper settlement."""
    frame = ak.tool_trade_date_hist_sina()
    column = next((name for name in ("trade_date", "日期", "date") if name in frame.columns), None)
    if column is None:
        raise ValueError("Exchange trading-calendar source has no date column")
    days = frozenset(
        parsed.date()
        for value in frame[column]
        if not pd.isna(parsed := pd.to_datetime(value, errors="coerce"))
    )
    if not days:
        raise ValueError("Exchange trading-calendar source has no usable dates")
    return days


def _require_trading_day(value: date, days: frozenset[date]) -> None:
    if value not in days:
        raise ValueError(f"{value.isoformat()} is not an exchange trading day")


def _next_trading_day(value: date, days: frozenset[date]) -> date:
    candidates = sorted(day for day in days if day > value)
    if not candidates:
        raise ValueError("Exchange trading calendar has no next trading day")
    return candidates[0]


def _refresh_sellable_shares(position: dict[str, Any], trade_day: date) -> None:
    """Apply the paper-portfolio T+1 settlement approximation.

    Exchange holidays are deliberately not inferred here; callers must supply
    a verified trading date for historical records.  Same-day shares are never
    sellable, and legacy positions without lot data are treated as settled.
    """
    if "available_shares" not in position:
        position["available_shares"] = int(position.get("shares", 0))
        position["unsettled_lots"] = []
        return
    unsettled = position.get("unsettled_lots", [])
    remaining: list[dict[str, Any]] = []
    for lot in unsettled if isinstance(unsettled, list) else []:
        available_on = lot.get("available_on") if isinstance(lot, dict) else None
        lot_shares = int(lot.get("shares", 0)) if isinstance(lot, dict) else 0
        try:
            settled = available_on is not None and date.fromisoformat(str(available_on)) <= trade_day
        except ValueError:
            settled = False
        if settled:
            position["available_shares"] = int(position.get("available_shares", 0)) + lot_shares
        else:
            remaining.append(lot)
    position["unsettled_lots"] = remaining


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
    stop_distance_pct: Optional[float] = typer.Option(None, "--stop-distance-pct", help="Planned loss distance from entry, e.g. 0.08"),
    sector: Optional[str] = typer.Option(None, "--sector", help="Sector label for risk aggregation"),
    theme: Optional[str] = typer.Option(None, "--theme", help="Theme label for risk aggregation"),
    horizon: str = typer.Option("long_term", "--horizon", help="Risk horizon: short_term, swing, or long_term"),
    overnight_stress_pct: Optional[float] = typer.Option(None, "--overnight-stress-pct", help="Worst planned overnight-gap loss percentage"),
    limit_down_stress_pct: Optional[float] = typer.Option(None, "--limit-down-stress-pct", help="Worst planned limit-down loss percentage"),
    strategy_entry_id: Optional[str] = typer.Option(
        None,
        "--strategy-entry-id",
        help="Active market-desk strategy entry required for every new paper buy.",
    ),
    ledger_path: Optional[Path] = typer.Option(
        None, "--ledger-path", help="Research ledger used to verify strategy_entry_id."
    ),
    entry_observed_at: Optional[str] = typer.Option(
        None,
        "--entry-observed-at",
        help="Timezone-aware timestamp when the plan entry condition was confirmed.",
    ),
    entry_evidence_ref: Optional[list[str]] = typer.Option(
        None,
        "--entry-evidence-ref",
        help="Evidence reference for the confirmed entry condition; repeatable and must name the observation archive ID.",
    ),
    entry_observation_archive_path: Optional[Path] = typer.Option(
        None,
        "--entry-observation-archive-path",
        help="Verified frozen market-data archive supporting the entry condition.",
    ),
    restricted_list_path: Optional[Path] = typer.Option(
        None,
        "--restricted-list-path",
        help="Current signed restricted-list authority required at paper entry.",
    ),
    trade_date: Optional[str] = typer.Option(None, "--trade-date", help="Paper trade date (YYYY-MM-DD) for T+1 settlement"),
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

    trade_day = _resolve_trade_day(trade_date)
    if shares <= 0 or shares % 100 != 0:
        msg = "Shares must be a positive multiple of 100 for an A-share paper buy"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    if stop_distance_pct is not None and not 0 < stop_distance_pct < 1:
        msg = "stop-distance-pct must be between 0 and 1"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    normalized_horizon = horizon.strip().lower()
    if normalized_horizon not in {"short_term", "swing", "long_term"}:
        msg = "horizon must be short_term, swing, or long_term"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)
    for label, value in (
        ("overnight-stress-pct", overnight_stress_pct),
        ("limit-down-stress-pct", limit_down_stress_pct),
    ):
        if value is not None and not 0 < value <= 1:
            msg = f"{label} must be between 0 and 1"
            if json_output:
                _print_json({"error": msg})
            else:
                console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
    if normalized_horizon in {"short_term", "swing"} and (
        overnight_stress_pct is None or limit_down_stress_pct is None
    ):
        msg = "short_term and swing paper buys require overnight-stress-pct and limit-down-stress-pct"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)
    try:
        trading_days = _exchange_trading_days()
        _require_trading_day(trade_day, trading_days)
        available_on = _next_trading_day(trade_day, trading_days)
    except (OSError, ValueError, RuntimeError) as error:
        msg = f"Paper buy blocked: exchange calendar unavailable or invalid ({error})"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    governed_link: Optional[dict[str, Any]] = None
    if not strategy_entry_id:
        msg = (
            "Paper buy blocked: new paper buys require an active, independently assured "
            "market-desk strategy_entry_id"
        )
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)
    try:
        governed_link = validate_governed_paper_entry(
            entry_id=strategy_entry_id,
            code=code,
            ledger_path=ledger_path or DEFAULT_RESEARCH_LEDGER_PATH,
            entry_observed_at=entry_observed_at or "",
            entry_evidence_refs=entry_evidence_ref or (),
            entry_observation_archive_path=entry_observation_archive_path,
            restricted_list_path=restricted_list_path or DEFAULT_RESTRICTED_LIST_PATH,
        )
    except ValueError as error:
        msg = f"Governed paper buy blocked: {error}"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

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

    positions = data.setdefault("positions", {})
    if governed_link and code in positions:
        existing_entry_id = str(positions[code].get("strategy_entry_id") or "").strip()
        if existing_entry_id != governed_link["strategy_entry_id"]:
            msg = "Governed paper buy cannot attach a strategy plan to an unlinked or differently linked existing position"
            if json_output:
                _print_json({"error": msg})
            else:
                console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)
    for position in positions.values():
        _refresh_sellable_shares(position, trade_day)
    total_value = data["cash"] + sum(
        position["shares"] * position["current_price"] for position in positions.values()
    )
    existing_position_value = (
        positions[code]["shares"] * positions[code]["current_price"]
        if code in positions
        else 0.0
    )
    risk_manager = RiskManager()
    position_ok, position_message = risk_manager.check_position_limit(
        total_value,
        existing_position_value,
        required,
    )
    projected_positions = [
        {
            "code": position_code,
            "market_value": (
                position["shares"] * position["current_price"]
                + (required if position_code == code else 0.0)
            ),
            "stop_distance_pct": (
                stop_distance_pct
                if position_code == code and stop_distance_pct is not None
                else position.get("stop_distance_pct")
            ),
            "sector": sector if position_code == code and sector else position.get("sector"),
            "theme": theme if position_code == code and theme else position.get("theme"),
            "horizon": normalized_horizon if position_code == code else position.get("horizon"),
            "overnight_stress_pct": overnight_stress_pct if position_code == code else position.get("overnight_stress_pct"),
            "limit_down_stress_pct": limit_down_stress_pct if position_code == code else position.get("limit_down_stress_pct"),
        }
        for position_code, position in positions.items()
    ]
    if code not in positions:
        projected_positions.append(
            {
                "code": code,
                "market_value": required,
                "stop_distance_pct": stop_distance_pct,
                "sector": sector,
                "theme": theme,
                "horizon": normalized_horizon,
                "overnight_stress_pct": overnight_stress_pct,
                "limit_down_stress_pct": limit_down_stress_pct,
            }
        )
    effective_stop = max(
        stop_distance_pct or risk_manager.limits.stop_loss_percent,
        overnight_stress_pct or 0.0,
        limit_down_stress_pct or 0.0,
    )
    risk_budget = risk_manager.assess_risk_budget(
        positions=projected_positions,
        cash=float(data["cash"] - required),
        planned_new_risk=required * effective_stop,
    )
    blockers = ([position_message] if not position_ok else []) + risk_budget.blockers
    if blockers:
        msg = "Paper buy blocked by risk limits"
        payload = {"error": msg, "blockers": blockers, "risk_budget": risk_budget.to_dict()}
        if json_output:
            _print_json(payload)
        else:
            console.print(f"[red]{msg}: {'; '.join(blockers)}[/red]")
        raise typer.Exit(1)

    data["cash"] -= required

    if code in positions:
        pos = positions[code]
        total_cost = pos["cost_price"] * pos["shares"] + price * shares
        total_shares = pos["shares"] + shares
        pos["cost_price"] = total_cost / total_shares
        pos["shares"] = total_shares
        pos["current_price"] = price
        if stop_distance_pct is not None:
            pos["stop_distance_pct"] = stop_distance_pct
        if sector:
            pos["sector"] = sector
        if theme:
            pos["theme"] = theme
        pos["horizon"] = normalized_horizon
        pos["overnight_stress_pct"] = overnight_stress_pct
        pos["limit_down_stress_pct"] = limit_down_stress_pct
        if governed_link:
            pos["strategy_entry_id"] = governed_link["strategy_entry_id"]
            pos["strategy_plan_id"] = governed_link["strategy_plan_id"]
            pos["governance_status"] = "governed"
            pos.setdefault("entry_evidence_history", []).append(governed_link["entry_evidence"])
        pos.setdefault("unsettled_lots", []).append(
            {"shares": shares, "available_on": available_on.isoformat()}
        )
        pos["updated_at"] = datetime.now().isoformat()
    else:
        positions[code] = {
            "code": code,
            "name": None,
            "shares": shares,
            "cost_price": price,
            "current_price": price,
            "stop_distance_pct": stop_distance_pct,
            "sector": sector,
            "theme": theme,
            "horizon": normalized_horizon,
            "overnight_stress_pct": overnight_stress_pct,
            "limit_down_stress_pct": limit_down_stress_pct,
            "available_shares": 0,
            "unsettled_lots": [
                {"shares": shares, "available_on": available_on.isoformat()}
            ],
            "opened_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "strategy_entry_id": governed_link["strategy_entry_id"],
            "strategy_plan_id": governed_link["strategy_plan_id"],
            "governance_status": "governed",
            "entry_evidence_history": [governed_link["entry_evidence"]],
        }

    trade = {
        "code": code,
        "action": "buy",
        "shares": shares,
        "price": price,
        "amount": required,
        "trade_date": trade_day.isoformat(),
        "settlement": "T+1 exchange-calendar settlement",
        "timestamp": datetime.now().isoformat(),
        "strategy_entry_id": governed_link["strategy_entry_id"],
        "strategy_plan_id": governed_link["strategy_plan_id"],
        "governance_status": "governed",
        "entry_evidence": governed_link["entry_evidence"],
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
    exit_reason: Optional[str] = typer.Option(
        None, "--exit-reason", help="Reason for a governed paper-position reduction or exit."
    ),
    exit_observed_at: Optional[str] = typer.Option(
        None, "--exit-observed-at", help="Timezone-aware timestamp when the exit condition was observed."
    ),
    exit_evidence_ref: Optional[list[str]] = typer.Option(
        None,
        "--exit-evidence-ref",
        help="Evidence reference for the paper exit; repeatable and must name the observation archive ID.",
    ),
    exit_observation_archive_path: Optional[Path] = typer.Option(
        None,
        "--exit-observation-archive-path",
        help="Verified frozen market-data archive supporting the paper exit.",
    ),
    ledger_path: Optional[Path] = typer.Option(
        None, "--ledger-path", help="Research ledger used to verify a governed paper-position exit."
    ),
    trade_date: Optional[str] = typer.Option(None, "--trade-date", help="Paper trade date (YYYY-MM-DD) for T+1 settlement"),
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

    trade_day = _resolve_trade_day(trade_date)
    if shares <= 0:
        msg = "Shares must be positive for an A-share paper sell"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)
    try:
        _require_trading_day(trade_day, _exchange_trading_days())
    except (OSError, ValueError, RuntimeError) as error:
        msg = f"Paper sell blocked: exchange calendar unavailable or invalid ({error})"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

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
    _refresh_sellable_shares(pos, trade_day)
    if shares > pos["shares"]:
        msg = f"Insufficient shares: have {pos['shares']:.0f}, selling {shares}"
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)
    if shares > pos.get("available_shares", 0):
        msg = (
            f"T+1 restriction: only {pos.get('available_shares', 0):.0f} shares are sellable "
            f"on {trade_day.isoformat()}"
        )
        if json_output:
            _print_json({"error": msg})
        else:
            console.print(f"[red]{msg}[/red]")
        raise typer.Exit(1)

    governed_exit: Optional[dict[str, Any]] = None
    strategy_entry_id = str(pos.get("strategy_entry_id") or "").strip()
    if strategy_entry_id:
        try:
            governed_exit = validate_governed_paper_exit(
                entry_id=strategy_entry_id,
                code=code,
                ledger_path=ledger_path or DEFAULT_RESEARCH_LEDGER_PATH,
                exit_reason=exit_reason or "",
                exit_observed_at=exit_observed_at or "",
                exit_evidence_refs=exit_evidence_ref or (),
                exit_observation_archive_path=exit_observation_archive_path,
            )
        except ValueError as error:
            msg = f"Governed paper sell blocked: {error}"
            if json_output:
                _print_json({"error": msg})
            else:
                console.print(f"[red]{msg}[/red]")
            raise typer.Exit(1)

    if governed_exit:
        exit_evidence = dict(governed_exit["exit_evidence"])
        exit_identity = {
            "strategy_entry_id": governed_exit["strategy_entry_id"],
            "strategy_plan_id": governed_exit["strategy_plan_id"],
            "code": code,
            "shares": shares,
            "price": price,
            "trade_date": trade_day.isoformat(),
            "observed_at": exit_evidence["observed_at"],
            "observation_archive_id": exit_evidence["observation_archive"]["archive_id"],
        }
        exit_evidence["exit_id"] = "paper-exit:sha256:" + hashlib.sha256(
            json.dumps(exit_identity, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        governed_exit["exit_evidence"] = exit_evidence

    proceeds = shares * price
    data["cash"] += proceeds
    pos["shares"] -= shares
    pos["available_shares"] -= shares
    pos["current_price"] = price
    pos["updated_at"] = datetime.now().isoformat()
    if governed_exit:
        pos.setdefault("exit_evidence_history", []).append(governed_exit["exit_evidence"])

    position_closed = pos["shares"] <= 0
    if position_closed:
        del positions[code]

    pnl = (price - pos["cost_price"]) * shares

    trade = {
        "code": code,
        "action": "sell",
        "shares": shares,
        "price": price,
        "amount": proceeds,
        "pnl": pnl,
        "trade_date": trade_day.isoformat(),
        "timestamp": datetime.now().isoformat(),
        "strategy_entry_id": governed_exit["strategy_entry_id"] if governed_exit else strategy_entry_id or None,
        "strategy_plan_id": governed_exit["strategy_plan_id"] if governed_exit else pos.get("strategy_plan_id"),
        "governance_status": "governed_exit" if governed_exit else pos.get("governance_status", "unlinked_legacy"),
        "exit_evidence": governed_exit["exit_evidence"] if governed_exit else None,
        "position_closed": position_closed,
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
    context: Optional[str] = typer.Option(
        None,
        "--context",
        help="JSON risk context: per-code factor/liquidity inputs, correlations, and stress scenarios.",
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Show portfolio risk metrics"""
    data = _load_portfolio()
    positions = data.get("positions", {})

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
    risk_context: dict[str, Any] = {}
    if context:
        context_path = Path(context)
        if not context_path.exists():
            message = f"Risk context file not found: {context}"
            if json_output:
                _print_json({"error": message})
            else:
                console.print(f"[red]{message}[/red]")
            raise typer.Exit(1)
        try:
            loaded_context = json.loads(context_path.read_text(encoding="utf-8"))
            if not isinstance(loaded_context, dict):
                raise ValueError("root must be a JSON object")
            risk_context = loaded_context
        except (OSError, ValueError, json.JSONDecodeError) as error:
            message = f"Invalid risk context: {error}"
            if json_output:
                _print_json({"error": message})
            else:
                console.print(f"[red]{message}[/red]")
            raise typer.Exit(1)
    position_context = risk_context.get("positions", {})
    if not isinstance(position_context, dict):
        position_context = {}
    governed_factor_inputs: dict[str, Any] = {}
    if context:
        try:
            governed = validate_factor_risk_context(
                risk_context,
                required_codes=sorted(str(code) for code in positions),
            )
        except ValueError as error:
            message = f"Invalid governed factor risk context: {error}"
            if json_output:
                _print_json({"error": message})
            else:
                console.print(f"[red]{message}[/red]")
            raise typer.Exit(1)
        governed_factor_inputs = governed.to_risk_inputs()
    risk_positions = [
        {
            "code": code,
            "market_value": position["shares"] * position["current_price"],
            "stop_distance_pct": position.get("stop_distance_pct"),
            "sector": position.get("sector"),
            "theme": position.get("theme"),
            "horizon": position.get("horizon"),
            "overnight_stress_pct": position.get("overnight_stress_pct"),
            "limit_down_stress_pct": position.get("limit_down_stress_pct"),
            **(
                {
                    **(
                        position_context.get(code, {})
                        if isinstance(position_context.get(code), dict)
                        else {}
                    ),
                    "factor_exposures": governed_factor_inputs.get("factor_exposures", {}).get(code, {}),
                }
            ),
        }
        for code, position in positions.items()
    ]
    risk_budget = risk_manager.assess_risk_budget(
        positions=risk_positions,
        cash=float(data["cash"]),
    )
    structural_risk = risk_manager.assess_portfolio_structure(
        positions=risk_positions,
        cash=float(data["cash"]),
        correlations=(
            risk_context.get("correlations")
            if isinstance(risk_context.get("correlations"), dict)
            else None
        ),
        stress_scenarios=governed_factor_inputs.get("stress_scenarios") or None,
    )
    result = {
        "total_value": total_value,
        "position_count": len(positions),
        "concentration_risk": concentration,
        "max_single_position_pct": concentration * 100,
        "cash_ratio": data["cash"] / total_value * 100 if total_value > 0 else 100,
        "limit_checks": {
            "max_position_size": risk_manager.limits.max_position_size * 100,
            "max_positions": risk_manager.limits.max_positions,
            "max_theme_exposure": risk_manager.limits.max_theme_exposure * 100,
            "stop_loss": risk_manager.limits.stop_loss_percent * 100,
            "max_portfolio_stress_loss": risk_manager.limits.max_portfolio_stress_loss * 100,
            "take_profit": risk_manager.limits.take_profit_percent * 100,
        },
        "risk_budget": risk_budget.to_dict(),
        "structural_risk": structural_risk.to_dict(),
    }

    if json_output:
        _print_json(result)
    else:
        panel_content = (
            f"Total value: {total_value:,.0f}\n"
            f"Positions: {len(positions)}/{risk_manager.limits.max_positions}\n"
            f"Cash ratio: {result['cash_ratio']:.1f}%\n"
            f"Max single position: {concentration * 100:.1f}% (limit: {risk_manager.limits.max_position_size * 100:.0f}%)\n"
            f"Planned-loss budget: {risk_budget.planned_loss_ratio * 100:.1f}%\n"
            f"Stress-loss budget: {risk_budget.stressed_loss_ratio * 100:.1f}%\n"
            f"Risk blockers: {len(risk_budget.blockers)}\n"
            f"Structural blockers: {len(structural_risk.blockers)}\n"
            f"Stop-loss fallback: {risk_manager.limits.stop_loss_percent * 100:.0f}%\n"
            f"Take-profit: {risk_manager.limits.take_profit_percent * 100:.0f}%"
        )
        console.print(Panel(panel_content, title="Portfolio Risk Metrics"))


@app.command("governance")
def portfolio_governance(
    ledger_path: Optional[Path] = typer.Option(
        None, "--ledger-path", help="Research ledger used to audit strategy-plan links."
    ),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON output"),
) -> None:
    """Audit whether paper positions are linked to assured desk strategy plans."""
    result = audit_paper_portfolio_governance(
        _load_portfolio(), ledger_path=ledger_path or DEFAULT_RESEARCH_LEDGER_PATH
    )
    if json_output:
        _print_json(result)
        return
    console.print(
        f"[bold]Paper Portfolio Governance: {result['governance_status']}[/bold] "
        f"({result['governed_count']} governed, "
        f"{result['unlinked_legacy_count']} unlinked legacy, "
        f"{result['invalid_link_count']} invalid, "
        f"{result['entry_evidence_gap_count']} entry-evidence gaps, "
        f"{result['exit_review_required_count']} exit reviews due)"
    )


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
