"""回测 CLI 命令"""

import asyncio
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from ..storage import Database
from ..quote import QuoteService
from .engine import BacktestEngine
from .strategies import STRATEGIES


app = typer.Typer(name="backtest", help="策略回测")
console = Console()

# 默认数据库路径
DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "stocks.db"


@app.command("run")
def run_backtest(
    code: str = typer.Argument(..., help="股票代码"),
    strategy: str = typer.Option(..., "--strategy", "-s", help="策略名称"),
    start_date: Optional[str] = typer.Option(None, "--start-date", help="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end-date", help="结束日期 (YYYY-MM-DD)"),
    capital: float = typer.Option(100000.0, "--capital", "-c", help="初始资金"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
):
    """运行策略回测"""
    # 验证策略名称
    if strategy not in STRATEGIES:
        console.print(f"[red]错误: 未知的策略名称 '{strategy}'[/red]")
        console.print(f"可用策略: {', '.join(STRATEGIES.keys())}")
        raise typer.Exit(1)

    # 解析日期
    if end_date:
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
    else:
        end_dt = date.today()

    if start_date:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
    else:
        start_dt = end_dt - timedelta(days=365)

    async def _run():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            # 获取历史数据
            service = QuoteService(db)
            df = await service.get_daily(code)

            if df.empty:
                return {"error": "无数据"}

            # 过滤日期范围
            if "date" in df.columns:
                df["date"] = df["date"].apply(
                    lambda x: datetime.strptime(x, "%Y-%m-%d").date()
                    if isinstance(x, str) else x
                )
                df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]
            else:
                # 使用索引作为日期
                df = df.iloc[-365:]

            if df.empty:
                return {"error": "指定日期范围内无数据"}

            # 运行回测
            engine = BacktestEngine()
            result = engine.run(
                df,
                strategy_name=strategy,
                initial_capital=capital,
            )
            result.code = code

            return result.to_dict()
        finally:
            await db.close()

    result = asyncio.run(_run())

    if json_output:
        console.print_json(data=result)
    else:
        if "error" in result:
            console.print(f"[red]错误: {result['error']}[/red]")
            raise typer.Exit(1)

        _display_result(result)


@app.command("list")
def list_strategies(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
):
    """列出可用策略"""
    strategies = [
        {"name": name, "description": cls.description}
        for name, cls in STRATEGIES.items()
    ]

    if json_output:
        console.print_json(data=strategies)
    else:
        table = Table(title="可用策略")
        table.add_column("名称", style="cyan")
        table.add_column("描述", style="green")

        for s in strategies:
            table.add_row(s["name"], s["description"])

        console.print(table)


def _display_result(result: dict):
    """显示回测结果"""
    # 收益指标面板
    total_return = result["total_return"]
    return_color = "green" if total_return >= 0 else "red"
    return_sign = "+" if total_return >= 0 else ""

    annual_return = result["annual_return"]
    annual_color = "green" if annual_return >= 0 else "red"
    annual_sign = "+" if annual_return >= 0 else ""

    panel_content = f"""[bold cyan]策略:[/bold cyan] {result['strategy']}
[bold cyan]回测区间:[/bold cyan] {result['start_date']} ~ {result['end_date']}

[bold yellow]收益指标[/bold yellow]
总收益率: [{return_color}]{return_sign}{total_return:.2f}%[/{return_color}]
年化收益: [{annual_color}]{annual_sign}{annual_return:.2f}%[/{annual_color}]
最大回撤: [red]-{result['max_drawdown']:.2f}%[/red]
夏普比率: {result['sharpe_ratio']:.2f}

[bold yellow]交易统计[/bold yellow]
初始资金: {result['initial_capital']:,.0f} 元
最终资金: {result['final_capital']:,.0f} 元
交易次数: {len(result['trades'])} 次
胜率: {result['win_rate']:.1f}%"""

    console.print(Panel(panel_content, title=f"回测结果 - {result['code']}"))

    # 交易记录表格
    trades = result["trades"]
    if trades:
        console.print("\n[bold yellow]交易记录:[/bold yellow]")
        table = Table()
        table.add_column("日期", style="cyan")
        table.add_column("信号", style="yellow")
        table.add_column("价格", style="white")
        table.add_column("股数", style="white")
        table.add_column("金额", style="green")
        table.add_column("手续费", style="dim")

        # 只显示最近 10 条记录
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
            console.print(f"[dim]... 共 {len(trades)} 条交易记录[/dim]")


if __name__ == "__main__":
    app()
