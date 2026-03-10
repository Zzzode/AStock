"""CLI 入口"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .storage import Database
from .quote import QuoteService
from .analysis import TechnicalAnalyzer
from .monitor import MonitorService
from .monitor.service_status import ServiceStatusManager, get_uptime_info, format_duration
from .stock_picker import StockScreener
from .recommend import Recommender
from .config import ConfigManager, TradingStyle, RiskLevel, EmailConfig
from .learning import StyleAnalyzer
from .utils import DataSourceError, ValidationError


app = typer.Typer(name="astock")
console = Console()

# 默认数据库路径
DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"

# 全局监控服务实例
_monitor_service: Optional[MonitorService] = None


@app.command()
def quote(
    code: str = typer.Argument(..., help="股票代码"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """获取实时行情"""

    async def _get_quote() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            result = await service.get_realtime(code)
            return result
        finally:
            await db.close()

    try:
        result = asyncio.run(_get_quote())
    except (ValidationError, DataSourceError) as e:
        if json_output:
            console.print_json(data={"error": str(e)})
        else:
            console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        if json_output:
            console.print_json(data={"error": f"获取实时行情失败: {e}"})
        else:
            console.print(f"[red]错误: 获取实时行情失败: {e}[/red]")
        raise typer.Exit(1)

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
        table.add_row("成交量", f"{result['volume'] / 10000:.0f}万手")
        table.add_row("成交额", f"{result['amount'] / 100000000:.2f}亿")

        console.print(table)


@app.command()
def analyze(
    code: str = typer.Argument(..., help="股票代码"),
    days: int = typer.Option(100, "--days", "-d", help="分析天数"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """技术分析"""

    async def _analyze() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            service = QuoteService(db)
            df = await service.get_daily(code, limit=days)

            if df.empty:
                return {"error": "无数据"}

            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()
            return analyzer.get_signals()
        finally:
            await db.close()

    try:
        result = asyncio.run(_analyze())
    except (ValidationError, DataSourceError) as e:
        if json_output:
            console.print_json(data={"error": str(e)})
        else:
            console.print(f"[red]错误: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        if json_output:
            console.print_json(data={"error": f"技术分析失败: {e}"})
        else:
            console.print(f"[red]错误: 技术分析失败: {e}[/red]")
        raise typer.Exit(1)

    if json_output:
        console.print_json(data=result)
    else:
        # 显示技术指标
        latest = result.get("latest", {})

        panel_content = f"""
[bold cyan]价格指标[/bold cyan]
收盘价: {latest.get("close", 0):.2f}
MA5: {latest.get("ma5", 0):.2f}
MA10: {latest.get("ma10", 0):.2f}
MA20: {latest.get("ma20", 0):.2f}

[bold cyan]MACD[/bold cyan]
DIF: {latest.get("macd", 0):.4f}
DEA: {latest.get("macd_signal", 0):.4f}
柱: {latest.get("macd_hist", 0):.4f}

[bold cyan]KDJ[/bold cyan]
K: {latest.get("kdj_k", 0):.2f}
D: {latest.get("kdj_d", 0):.2f}
J: {latest.get("kdj_j", 0):.2f}

[bold cyan]RSI[/bold cyan]
RSI6: {latest.get("rsi6", 0):.2f}
"""
        console.print(Panel(panel_content, title=f"技术分析 - {code}"))

        # 显示信号
        signals = result.get("signals", [])
        if signals:
            console.print("\n[bold yellow]检测到的信号:[/bold yellow]")
            for signal in signals:
                color = "green" if signal["bias"] == "bullish" else "red"
                console.print(
                    f"  [{color}]●[/{color}] {signal['name']}: {signal['description']}"
                )
        else:
            console.print("\n[dim]暂无明显信号[/dim]")


@app.command()
def init_db(
    skip_refresh: bool = typer.Option(False, "--skip-refresh", help="跳过刷新股票数据"),
) -> None:
    """初始化数据库"""

    async def _init() -> int:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        db = Database(str(DB_PATH))
        await db.connect()
        await db.init_tables()

        count = 0
        if not skip_refresh:
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
def alert_callback(ctx: typer.Context) -> None:
    """监控告警管理"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(alert_status)


@alert_app.command("start")
def alert_start(
    interval: int = typer.Option(60, "--interval", "-i", help="扫描间隔(秒)"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """启动监控服务"""

    async def _start() -> dict[str, Any]:
        global _monitor_service

        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            _monitor_service = MonitorService(db, quote_service)
            _monitor_service.set_scan_interval(interval)
            await _monitor_service.start()

            # 记录启动时间
            status_manager = ServiceStatusManager()
            instance = status_manager.record_start("default", interval=interval)

            # 获取监控股票数量
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
            # 注意: 不关闭 db，因为监控服务需要持续使用
            pass

    result = asyncio.run(_start())

    if json_output:
        console.print_json(data=result)
    else:
        console.print(f"[green]监控服务已启动[/green]")
        console.print(f"扫描间隔: {result['interval']}秒")
        console.print(f"监控股票: {result['watch_count']}只")
        console.print(f"服务PID: {result['pid']}")
        start_dt = datetime.fromisoformat(result['start_time'])
        console.print(f"启动时间: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}")


@alert_app.command("stop")
def alert_stop(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """停止监控服务"""

    async def _stop() -> dict[str, Any]:
        global _monitor_service

        if _monitor_service:
            await _monitor_service.stop()
            _monitor_service = None

            # 记录停止时间
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

    result = asyncio.run(_stop())

    if json_output:
        console.print_json(data=result)
    else:
        if result["status"] == "stopped":
            console.print("[yellow]监控服务已停止[/yellow]")
            if result.get("duration"):
                console.print(f"运行时长: {result['duration']}")
        else:
            console.print("[dim]监控服务未运行[/dim]")


@alert_app.command("status")
def alert_status(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """查看监控状态"""

    async def _status() -> dict[str, Any]:
        global _monitor_service

        db = Database(str(DB_PATH))
        await db.connect()
        try:
            # 获取监控股票数量
            watch_items = await db.get_watch_items(enabled_only=True)

            # 获取今日告警数量
            today = datetime.now().date()
            alerts = await db.get_alert_records(limit=100)
            today_alerts = [a for a in alerts if a.triggered_at.date() == today]

            # 获取服务状态信息
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

    result = asyncio.run(_status())

    if json_output:
        console.print_json(data=result)
    else:
        status_text = (
            "[green]运行中[/green]" if result["running"] else "[dim]已停止[/dim]"
        )

        # 构建状态面板内容
        panel_lines = [
            f"状态: {status_text}",
            f"扫描间隔: {result['interval']}秒",
            f"监控股票: {result['watch_count']}只",
            f"今日告警: {result['today_alerts']}条",
        ]

        # 添加运行时长信息
        if result.get("uptime"):
            uptime = result["uptime"]
            panel_lines.append(f"启动时间: {uptime['start_time_formatted']}")
            panel_lines.append(f"运行时长: {uptime['uptime_formatted']}")
            panel_lines.append(f"服务PID: {uptime['pid']}")

        console.print(Panel("\n".join(panel_lines), title="监控服务状态"))


@alert_app.command("history")
def alert_history(
    code: Optional[str] = typer.Argument(None, help="股票代码(可选)"),
    limit: int = typer.Option(10, "--limit", "-n", help="显示数量"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """查看历史告警"""

    async def _history() -> dict[str, Any]:
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
                        "status": a.status,
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
                alert["message"][:20] + "..."
                if len(alert["message"]) > 20
                else alert["message"],
                f"[{status_color}]{alert['status']}[/{status_color}]",
            )

        console.print(table)


@alert_app.command("service-history")
def alert_service_history(
    limit: int = typer.Option(10, "--limit", "-n", help="显示数量"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """查看服务启动/停止历史"""

    status_manager = ServiceStatusManager()
    history = status_manager.get_history(limit=limit)

    if json_output:
        console.print_json(
            data={
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
            console.print("[dim]暂无服务历史记录[/dim]")
            return

        table = Table(title="服务启动/停止历史")
        table.add_column("实例ID", style="cyan", width=12)
        table.add_column("PID", style="white", width=8)
        table.add_column("启动时间", style="green", width=20)
        table.add_column("停止时间", style="yellow", width=20)
        table.add_column("运行时长", style="magenta")

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
    factors: Optional[str] = typer.Argument(None, help="因子列表，逗号分隔"),
    codes: Optional[str] = typer.Option(
        None, "--codes", "-c", help="指定股票代码，逗号分隔"
    ),
    industry: Optional[str] = typer.Option(
        None, "--industry", "-i", help="按行业筛选，支持多个行业用逗号分隔"
    ),
    exclude_industry: Optional[str] = typer.Option(
        None, "--exclude-industry", help="排除指定行业，支持多个行业用逗号分隔"
    ),
    limit: int = typer.Option(10, "--limit", "-n", help="返回数量"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """股票选股"""

    async def _screen() -> dict[str, Any]:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            screener = StockScreener(quote_service)

            # 解析因子列表
            factor_list = None
            if factors:
                factor_list = [f.strip() for f in factors.split(",")]

            code_list = None
            if codes:
                code_list = [item.strip() for item in codes.split(",") if item.strip()]

            results = await screener.screen(
                factors=factor_list, codes=code_list, limit=limit
            )

            # 行业筛选
            if industry or exclude_industry:
                from .data import get_industry_service
                industry_service = get_industry_service()
                await industry_service.initialize()

                include_industries = [i.strip() for i in industry.split(",")] if industry else None
                exclude_industries = [i.strip() for i in exclude_industry.split(",")] if exclude_industry else None

                # 获取所有结果的股票代码
                result_codes = [r.code for r in results]
                filtered_codes = await industry_service.filter_by_industry(
                    result_codes,
                    include_industries=include_industries,
                    exclude_industries=exclude_industries,
                )
                # 过滤结果
                results = [r for r in results if r.code in filtered_codes]

            # 获取行业信息
            from .data import get_industry_service
            industry_service = get_industry_service()
            await industry_service.initialize()

            enriched_results = []
            for r in results:
                stock_industry = await industry_service.get_stock_industry(r.code)
                enriched_results.append({
                    "code": r.code,
                    "name": r.name,
                    "score": r.score,
                    "matched_factors": r.matched_factors,
                    "factor_scores": r.factor_scores,
                    "industry": stock_industry.industry if stock_industry else None,
                    "industry_change": stock_industry.industry_change if stock_industry else None,
                    "screened_at": r.screened_at.isoformat(),
                })

            return {
                "total": len(enriched_results),
                "results": enriched_results,
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
        table.add_column("行业", style="magenta", width=8)
        table.add_column("得分", style="yellow", width=6)
        table.add_column("匹配因子", style="green")

        for i, r in enumerate(result["results"], 1):
            factors_str = ",".join(r["matched_factors"][:3])
            if len(r["matched_factors"]) > 3:
                factors_str += "..."
            industry = r.get("industry") or "-"
            table.add_row(
                str(i), r["code"], r["name"] or "-", industry, f"{r['score']:.1f}", factors_str
            )

        console.print(table)


# ============ Recommend 命令组 ============

recommend_app = typer.Typer(name="recommend", help="个性化推荐")
app.add_typer(recommend_app, name="recommend")


@recommend_app.callback(invoke_without_command=True)
def recommend_callback(ctx: typer.Context) -> None:
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
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """生成个性化推荐"""

    async def _recommend() -> Any:
        db = Database(str(DB_PATH))
        await db.connect()
        try:
            quote_service = QuoteService(db)
            screener = StockScreener(quote_service)

            # 初始化行业服务
            from .data import get_industry_service
            industry_service = get_industry_service()
            await industry_service.initialize()

            recommender = Recommender(screener, industry_service)

            # 构建选项
            options: dict[str, object] = {}
            if style:
                options["trading_style"] = style
            if risk:
                options["risk_level"] = risk
            if min_price is not None:
                options["min_price"] = min_price
            if max_price is not None:
                options["max_price"] = max_price

            result = await recommender.handle_recommend(
                user_id=user_id, limit=limit, options=options if options else None
            )

            return result
        finally:
            await db.close()

    result = asyncio.run(_recommend())

    if json_output:
        console.print_json(
            data={
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
                        "industry": r.industry,
                        "industry_change": r.industry_change,
                        "recommended_at": r.recommended_at.isoformat(),
                    }
                    for r in result.recommendations
                ],
            }
        )
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
用户: {result.config_used.get("user_id", "default")}
交易风格: {result.config_used.get("trading_style", "swing")}
风险等级: {result.config_used.get("risk_level", "moderate")}
价格范围: {result.config_used.get("min_price") or "-"} ~ {result.config_used.get("max_price") or "-"}
"""
            console.print(Panel(config_panel.strip(), title="推荐配置"))

        # 显示推荐结果
        table = Table(title=f"个性化推荐 (共 {result.total} 只)")
        table.add_column("排名", style="dim", width=4)
        table.add_column("代码", style="cyan", width=8)
        table.add_column("名称", style="white", width=10)
        table.add_column("行业", style="magenta", width=8)
        table.add_column("得分", style="yellow", width=6)
        table.add_column("风格匹配", style="green", width=8)
        table.add_column("推荐策略", style="dim")

        for i, r in enumerate(result.recommendations, 1):
            strategies_str = ",".join(r.suggested_strategies[:2])
            if len(r.suggested_strategies) > 2:
                strategies_str += "..."
            table.add_row(
                str(i),
                r.code,
                r.name or "-",
                r.industry or "-",
                f"{r.score:.1f}",
                f"{r.style_match:.0%}",
                strategies_str,
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
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
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
价格范围: {config.min_price or "-"} ~ {config.max_price or "-"}
偏好行业: {", ".join(config.preferred_sectors) or "-"}
排除行业: {", ".join(config.excluded_sectors) or "-"}
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
def config_callback(ctx: typer.Context) -> None:
    """配置管理"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(config_show)


@config_app.command("show")
def config_show(
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
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
价格范围: {config.min_price or "-"} ~ {config.max_price or "-"}
偏好行业: {", ".join(config.preferred_sectors) or "-"}
排除行业: {", ".join(config.excluded_sectors) or "-"}
提醒渠道: {", ".join(config.alert_channels)}
默认资金: {config.default_capital:,.0f}
默认策略: {config.default_strategy}
"""
        console.print(Panel(panel_content.strip(), title=f"用户配置: {user_id}"))


@config_app.command("set")
def config_set(
    key: str = typer.Argument(..., help="配置项名称"),
    value: str = typer.Argument(..., help="配置值"),
    user_id: str = typer.Option("default", "--user", "-u", help="用户ID"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
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


def _parse_config_value(key: str, value: str) -> Optional[object]:
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
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """分析并学习交易风格"""
    config_manager = ConfigManager()
    analyzer = StyleAnalyzer()

    # 执行分析并更新配置
    analysis = analyzer.update_user_config(user_id, config_manager)

    if json_output:
        console.print_json(
            data={
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
交易风格: {analysis.trading_style.value}
风险等级: {analysis.risk_level.value}
交易频率: {analysis.trade_frequency:.1f} 次/月
平均持仓: {analysis.avg_holding_days:.1f} 天
总交易数: {analysis.total_trades}
胜率: {analysis.win_rate:.1%}
盈亏比: {analysis.profit_loss_ratio:.2f}
总盈亏: {analysis.total_profit:,.2f}
偏好行业: {", ".join(analysis.preferred_sectors) or "-"}
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
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
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


# ============ Email 配置命令 ============

email_app = typer.Typer(name="email", help="邮件配置管理")
config_app.add_typer(email_app, name="email")


@email_app.callback(invoke_without_command=True)
def email_callback(ctx: typer.Context) -> None:
    """邮件配置管理"""
    if ctx.invoked_subcommand is None:
        ctx.invoke(email_show)


@email_app.command("show")
def email_show(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """显示邮件配置"""
    email_config = EmailConfig.from_env()

    if json_output:
        console.print_json(data=email_config.to_dict())
    else:
        if email_config.is_configured():
            panel_content = f"""
SMTP服务器: {email_config.smtp_host}:{email_config.smtp_port}
加密方式: {"SSL" if email_config.use_ssl else "TLS" if email_config.use_tls else "无"}
发件人: {email_config.sender_name} <{email_config.sender_email}>
收件人: {", ".join(email_config.recipients)}
主题前缀: {email_config.subject_prefix}
"""
            console.print(Panel(panel_content.strip(), title="邮件配置"))
        else:
            console.print("[yellow]邮件未配置[/yellow]")
            console.print("请设置以下环境变量或使用 'config email set' 命令配置:")
            console.print("  EMAIL_SMTP_HOST     - SMTP服务器地址 (默认: smtp.qq.com)")
            console.print("  EMAIL_SMTP_PORT     - SMTP端口 (默认: 465)")
            console.print("  EMAIL_USE_SSL       - 使用SSL (默认: true)")
            console.print("  EMAIL_SENDER        - 发件人邮箱")
            console.print("  EMAIL_PASSWORD      - 发件人密码/授权码")
            console.print("  EMAIL_RECIPIENTS    - 收件人列表(逗号分隔)")


@email_app.command("set")
def email_set(
    key: str = typer.Argument(..., help="配置项名称"),
    value: str = typer.Argument(..., help="配置值"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """设置邮件配置项

    配置项保存到 data/config.json 文件中的 email 部分。
    注意: 敏感信息(如密码)建议使用环境变量 EMAIL_PASSWORD 设置。

    可用配置项:
        smtp_host      - SMTP服务器地址
        smtp_port      - SMTP端口
        use_ssl        - 使用SSL (true/false)
        use_tls        - 使用TLS (true/false)
        sender_email   - 发件人邮箱
        sender_password - 发件人密码/授权码
        sender_name    - 发件人显示名称
        recipients     - 收件人列表(逗号分隔)
        subject_prefix - 邮件主题前缀
    """
    # 加载现有配置
    config_path = Path("data/config.json")
    config_data = {}

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)
        except Exception as e:
            console.print(f"[red]加载配置文件失败: {e}[/red]")
            raise typer.Exit(1)

    # 确保 email 配置存在
    if "email" not in config_data:
        config_data["email"] = {}

    # 解析并设置配置值
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
        console.print(f"[red]未知的邮件配置项: {key}[/red]")
        console.print(f"可用配置项: {', '.join(email_key_map.keys())}")
        raise typer.Exit(1)

    # 类型转换
    if key in ["smtp_port"]:
        try:
            config_data["email"][email_key_map[key]] = int(value)
        except ValueError:
            console.print(f"[red]无效的端口号: {value}[/red]")
            raise typer.Exit(1)
    elif key in ["use_ssl", "use_tls"]:
        config_data["email"][email_key_map[key]] = value.lower() == "true"
    elif key == "recipients":
        config_data["email"][email_key_map[key]] = [v.strip() for v in value.split(",")]
    else:
        config_data["email"][email_key_map[key]] = value

    # 保存配置
    config_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
        console.print(f"[green]已更新邮件配置: {key}[/green]")
    except Exception as e:
        console.print(f"[red]保存配置失败: {e}[/red]")
        raise typer.Exit(1)


@email_app.command("test")
def email_test(
    recipient: Optional[str] = typer.Option(None, "--to", "-t", help="测试收件人"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """发送测试邮件"""
    from .storage import AlertRecord
    from .monitor.alert_engine import send_email_notification

    # 加载邮件配置
    email_config = EmailConfig.from_env()

    # 如果指定了测试收件人，临时使用该收件人
    if recipient:
        email_config.recipients = [recipient]

    if not email_config.is_configured():
        console.print("[red]邮件未配置，请先设置邮箱信息[/red]")
        console.print("使用 'config email set' 命令或设置环境变量进行配置")
        raise typer.Exit(1)

    # 创建测试告警记录
    test_alert = AlertRecord(
        id=0,
        code="TEST",
        signal_type="test",
        signal_name="测试信号",
        message="这是一封测试邮件，用于验证邮件推送功能是否正常工作。",
        level=3,
        triggered_at=datetime.now(),
        status="pending",
        channels=["email"],
    )

    try:
        asyncio.run(send_email_notification(test_alert, email_config))
        if json_output:
            console.print_json(data={"success": True, "recipients": email_config.recipients})
        else:
            console.print(f"[green]测试邮件发送成功[/green]")
            console.print(f"收件人: {', '.join(email_config.recipients)}")
    except Exception as e:
        if json_output:
            console.print_json(data={"success": False, "error": str(e)})
        else:
            console.print(f"[red]测试邮件发送失败: {e}[/red]")
        raise typer.Exit(1)


@email_app.command("reset")
def email_reset(
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出"),
) -> None:
    """重置邮件配置"""
    config_path = Path("data/config.json")

    if config_path.exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = json.load(f)

            if "email" in config_data:
                del config_data["email"]

                with open(config_path, "w", encoding="utf-8") as f:
                    json.dump(config_data, f, ensure_ascii=False, indent=2)

                console.print("[yellow]已重置邮件配置[/yellow]")
            else:
                console.print("[dim]邮件配置不存在[/dim]")
        except Exception as e:
            console.print(f"[red]重置配置失败: {e}[/red]")
            raise typer.Exit(1)
    else:
        console.print("[dim]配置文件不存在[/dim]")


# ============ Backtest 命令组 ============

from .backtest.backtest_cli import app as backtest_app

app.add_typer(backtest_app, name="backtest")


# ============ Watch 命令组 ============

from .monitor.watch_cli import app as watch_app

app.add_typer(watch_app, name="watch")


if __name__ == "__main__":
    app()
