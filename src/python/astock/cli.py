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
from .recommend import Recommender
from .config import ConfigManager, TradingStyle, RiskLevel
from .learning import StyleAnalyzer


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


# ============ Recommend 命令组 ============

recommend_app = typer.Typer(name="recommend", help="个性化推荐")
app.add_typer(recommend_app, name="recommend")


@recommend_app.callback(invoke_without_command=True)
def recommend_callback(ctx: typer.Context):
    """个性化推荐"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(recommend_generate)


@recommend_app.command("generate")
def recommend_generate(
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    limit: int = typer.Option(10, "--limit", "-n", help="返回数量"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="交易风格覆盖"),
    risk: Optional[str] = typer.Option(None, "--risk", "-r", help="风险等级覆盖"),
    min_price: Optional[float] = typer.Option(None, "--min-price", help="最低价格"),
    max_price: Optional[float] = typer.Option(None, "--max-price", help="最高价格"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """生成个性化推荐"""
    async def _recommend():
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            screener = StockScreener(quote_service)
            recommender = Recommender(screener)

            # 构建选项
            options = {}
            if style:
                options["trading_style"] = style
            if risk:
                options["risk_level"] = risk
            if min_price is not None:
                options["min_price"] = min_price
            if max_price is not None:
                options["max_price"] = max_price

            result = await recommender.handle_recommend(
                user_id=user_id,
                limit=limit,
                options=options if options else None
            )

            return result
        finally:
            await db.close()

    result = asyncio.run(_recommend())

    if json_output:
        console.print_json(data={
            "success": result.success,
            "total": result.total,
            "error": result.error,
            "config_used": result.config_used,
            "recommendations": [
                {
                    "code": r.code,
                    "name": r.name,
                    "score": r.score,
                    "matched_factors": r.matched_factors,
                    "suggested_strategies": r.suggested_strategies,
                    "risk_level": r.risk_level,
                    "style_match": r.style_match,
                    "recommended_at": r.recommended_at.isoformat()
                }
                for r in result.recommendations
            ]
        })
    else:
        if not result.success:
            console.print(f"[red]推荐生成失败: {result.error}[/red]")
            return

        if not result.recommendations:
            console.print("[dim]未找到符合条件的股票推荐[/dim]")
            return

        # 显示配置信息
        if result.config_used:
            config_panel = f"""
用户: {result.config_used.get('user_id', 'default')}
交易风格: {result.config_used.get('trading_style', 'swing')}
风险等级: {result.config_used.get('risk_level', 'moderate')}
价格范围: {result.config_used.get('min_price') or '-'} ~ {result.config_used.get('max_price') or '-'}
"""
            console.print(Panel(config_panel.strip(), title="推荐配置"))

        # 显示推荐结果
        table = Table(title=f"个性化推荐 (共 {result.total} 只)")
        table.add_column("排名", style="dim", width=4)
        table.add_column("代码", style="cyan", width=8)
        table.add_column("名称", style="white", width=10)
        table.add_column("得分", style="yellow", width=6)
        table.add_column("风格匹配", style="green", width=8)
        table.add_column("推荐策略", style="magenta")

        for i, r in enumerate(result.recommendations, 1):
            strategies_str = ",".join(r.suggested_strategies[:2])
            if len(r.suggested_strategies) > 2:
                strategies_str += "..."
            table.add_row(
                str(i),
                r.code,
                r.name or "-",
                f"{r.score:.1f}",
                f"{r.style_match:.0%}",
                strategies_str
            )

        console.print(table)


@recommend_app.command("config")
def recommend_config(
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    style: Optional[str] = typer.Option(None, "--style", "-s", help="交易风格"),
    risk: Optional[str] = typer.Option(None, "--risk", "-r", help="风险等级"),
    min_price: Optional[float] = typer.Option(None, "--min-price", help="最低价格"),
    max_price: Optional[float] = typer.Option(None, "--max-price", help="最高价格"),
    reset: bool = typer.Option(False, "--reset", help="重置为默认配置"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """管理推荐配置"""
    config_manager = ConfigManager()

    if reset:
        config = config_manager.reset(user_id)
        if json_output:
            console.print_json(data=config.model_dump())
        else:
            console.print(f"[green]已重置用户 {user_id} 的配置为默认值[/green]")
        return

    # 加载当前配置
    config = config_manager.load(user_id)

    # 更新配置
    updates = {}
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
        # 转换为可序列化的字典
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        console.print_json(data=config_data)
    else:
        panel_content = f"""
用户ID: {config.user_id}
交易风格: {config.trading_style.value}
风险等级: {config.risk_level.value}
最大持仓: {config.max_positions}
单只仓位: {config.position_size:.0%}
价格范围: {config.min_price or '-'} ~ {config.max_price or '-'}
偏好行业: {', '.join(config.preferred_sectors) or '-'}
排除行业: {', '.join(config.excluded_sectors) or '-'}
"""
        console.print(Panel(panel_content.strip(), title=f"用户配置: {user_id}"))

        # 显示可选项
        console.print("\n[bold]可选交易风格:[/bold]")
        for s in TradingStyle:
            marker = "*" if s == config.trading_style else " "
            console.print(f"  {marker} {s.value}")

        console.print("\n[bold]可选风险等级:[/bold]")
        for r in RiskLevel:
            marker = "*" if r == config.risk_level else " "
            console.print(f"  {marker} {r.value}")


# ============ Config 命令组 ============

config_app = typer.Typer(name="config", help="配置管理")
app.add_typer(config_app, name="config")


@config_app.callback(invoke_without_command=True)
def config_callback(ctx: typer.Context):
    """配置管理"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(config_show)


@config_app.command("show")
def config_show(
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """显示当前配置"""
    config_manager = ConfigManager()
    config = config_manager.load(user_id)

    if json_output:
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        console.print_json(data=config_data)
    else:
        panel_content = f"""
用户ID: {config.user_id}
交易风格: {config.trading_style.value}
风险等级: {config.risk_level.value}
最大持仓: {config.max_positions}
单只仓位: {config.position_size:.0%}
价格范围: {config.min_price or '-'} ~ {config.max_price or '-'}
偏好行业: {', '.join(config.preferred_sectors) or '-'}
排除行业: {', '.join(config.excluded_sectors) or '-'}
提醒渠道: {', '.join(config.alert_channels)}
默认资金: {config.default_capital:,.0f}
默认策略: {config.default_strategy}
"""
        console.print(Panel(panel_content.strip(), title=f"用户配置: {user_id}"))


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="配置项名称"),
    value: str = typer.Argument(..., help="配置值"),
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """设置配置项"""
    config_manager = ConfigManager()

    # 解析配置值
    parsed_value = _parse_config_value(key, value)
    if parsed_value is None:
        console.print(f"[red]未知的配置项: {key}[/red]")
        raise typer.Exit(1)

    config = config_manager.update(user_id, **{key: parsed_value})

    if json_output:
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        console.print_json(data=config_data)
    else:
        console.print(f"[green]已更新配置: {key} = {value}[/green]")


def _parse_config_value(key: str, value: str):
    """解析配置值"""
    # 风险等级
    if key == "risk_level":
        for r in RiskLevel:
            if r.value == value:
                return r
        return None

    # 交易风格
    if key == "trading_style":
        for s in TradingStyle:
            if s.value == value:
                return s
        return None

    # 数值类型
    if key in ["max_positions", "position_size", "min_price", "max_price", "default_capital"]:
        try:
            if key in ["max_positions"]:
                return int(value)
            return float(value)
        except ValueError:
            return None

    # 字符串列表类型
    if key in ["alert_channels", "preferred_sectors", "excluded_sectors"]:
        return [v.strip() for v in value.split(",")]

    # 字符串类型
    if key in ["default_strategy"]:
        return value

    return None


@config_app.command("style")
def config_style(
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """分析并学习交易风格"""
    config_manager = ConfigManager()
    analyzer = StyleAnalyzer()

    # 执行分析并更新配置
    analysis = analyzer.update_user_config(user_id, config_manager)

    if json_output:
        console.print_json(data={
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
        })
    else:
        panel_content = f"""
交易风格: {analysis.trading_style.value}
风险等级: {analysis.risk_level.value}
交易频率: {analysis.trade_frequency:.1f} 次/月
平均持仓: {analysis.avg_holding_days:.1f} 天
总交易数: {analysis.total_trades}
胜率: {analysis.win_rate:.1%}
盈亏比: {analysis.profit_loss_ratio:.2f}
总盈亏: {analysis.total_profit:,.2f}
偏好行业: {', '.join(analysis.preferred_sectors) or '-'}
置信度: {analysis.confidence:.0%}
"""
        console.print(Panel(panel_content.strip(), title=f"风格分析: {user_id}"))

        if analysis.confidence > 0.5:
            console.print("[green]配置已根据分析结果自动更新[/green]")
        else:
            console.print("[yellow]数据不足，未更新配置（需要更多交易记录）[/yellow]")


@config_app.command("reset")
def config_reset(
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """重置为默认配置"""
    config_manager = ConfigManager()
    config = config_manager.reset(user_id)

    if json_output:
        config_data = config.model_dump()
        config_data["alert_time_start"] = config.alert_time_start.isoformat()
        config_data["alert_time_end"] = config.alert_time_end.isoformat()
        config_data["trading_style"] = config.trading_style.value
        config_data["risk_level"] = config.risk_level.value
        console.print_json(data=config_data)
    else:
        console.print(f"[yellow]已重置用户 {user_id} 的配置为默认值[/yellow]")


# ============ Backtest 命令组 ============

from .backtest.backtest_cli import app as backtest_app
app.add_typer(backtest_app, name="backtest")


if __name__ == "__main__":
    app()
