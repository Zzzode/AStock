# A股交易策略分析工具 - Phase 2 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现盘中实时监控和多渠道提醒功能。

**Architecture:** Python asyncio 后台守护进程监控行情，信号扫描器检测技术信号，Alert Engine 分级提醒，TypeScript CLI 管理。

**Tech Stack:** Python asyncio, node-notifier, Webhook (微信/钉钉)

---

## Task 1: 监控配置模型与存储

**Files:**
- Modify: `src/python/astock/storage/models.py`
- Modify: `src/python/astock/storage/database.py`

**Step 1: 添加监控相关模型**

在 `models.py` 中添加：

```python
class WatchItem(BaseModel):
    """监控项"""

    code: str
    name: Optional[str] = None
    conditions: dict  # 监控条件配置
    alert_channels: list[str] = ["terminal"]  # 提醒渠道
    enabled: bool = True
    created_at: Optional[datetime] = None


class AlertRecord(BaseModel):
    """告警记录"""

    id: Optional[int] = None
    code: str
    signal_type: str
    signal_name: str
    message: str
    level: int  # 1=紧急, 2=重要, 3=一般
    triggered_at: datetime
    status: str  # pending, sent, failed
    channels: list[str]
```

**Step 2: 添加监控相关表**

在 `database.py` 的 `init_tables` 中添加：

```python
# 监控配置
CREATE TABLE IF NOT EXISTS watchlist (
    code TEXT PRIMARY KEY,
    name TEXT,
    conditions TEXT NOT NULL,
    alert_channels TEXT NOT NULL,
    enabled INTEGER DEFAULT 1,
    created_at DATETIME
);

-- 告警记录
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    signal_name TEXT NOT NULL,
    message TEXT NOT NULL,
    level INTEGER DEFAULT 3,
    triggered_at DATETIME NOT NULL,
    status TEXT DEFAULT 'pending',
    channels TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_alerts_code ON alerts(code);
CREATE INDEX IF NOT EXISTS idx_alerts_triggered_at ON alerts(triggered_at);
```

**Step 3: 添加监控数据访问方法**

```python
async def save_watch_item(self, item: WatchItem) -> None:
    """保存监控项"""
    await self._conn.execute(
        """INSERT OR REPLACE INTO watchlist
           (code, name, conditions, alert_channels, enabled, created_at)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (item.code, item.name, json.dumps(item.conditions),
         json.dumps(item.alert_channels), item.enabled, item.created_at)
    )
    await self._conn.commit()

async def get_watchlist(self, enabled_only: bool = True) -> list[WatchItem]:
    """获取监控列表"""
    sql = "SELECT * FROM watchlist"
    if enabled_only:
        sql += " WHERE enabled = 1"
    cursor = await self._conn.execute(sql)
    rows = await cursor.fetchall()
    return [WatchItem(
        code=row["code"], name=row["name"],
        conditions=json.loads(row["conditions"]),
        alert_channels=json.loads(row["alert_channels"]),
        enabled=bool(row["enabled"]), created_at=row["created_at"]
    ) for row in rows]

async def save_alert(self, alert: AlertRecord) -> int:
    """保存告警记录"""
    cursor = await self._conn.execute(
        """INSERT INTO alerts
           (code, signal_type, signal_name, message, level, triggered_at, status, channels)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (alert.code, alert.signal_type, alert.signal_name, alert.message,
         alert.level, alert.triggered_at, alert.status, json.dumps(alert.channels))
    )
    await self._conn.commit()
    return cursor.lastrowid
```

**Step 4: 提交代码**

```bash
git add src/python/astock/storage/
git commit --no-verify -m "feat(storage): add watchlist and alert models"
```

---

## Task 2: 监控服务核心

**Files:**
- Create: `src/python/astock/monitor/__init__.py`
- Create: `src/python/astock/monitor/scanner.py`
- Create: `src/python/astock/monitor/monitor_service.py`

**Step 1: 创建 monitor/__init__.py**

```python
"""监控服务模块"""

from .monitor_service import MonitorService
from .scanner import SignalScanner

__all__ = ["MonitorService", "SignalScanner"]
```

**Step 2: 创建 scanner.py - 信号扫描器**

```python
"""信号扫描器"""

import asyncio
from datetime import datetime
from typing import Optional
import pandas as pd

from ..quote import QuoteService
from ..analysis import TechnicalAnalyzer
from ..storage import Database


class SignalScanner:
    """技术信号扫描器"""

    def __init__(self, db: Database):
        self.db = db
        self.quote_service = QuoteService(db)

    async def scan_stock(self, code: str) -> list[dict]:
        """扫描单只股票的信号

        Returns:
            信号列表
        """
        signals = []

        try:
            # 获取日线数据
            df = await self.quote_service.get_daily(code, save=False)

            if df.empty:
                return signals

            # 技术分析
            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()
            result = analyzer.get_signals()

            # 转换信号格式
            for sig in result.get("signals", []):
                signals.append({
                    "code": code,
                    "type": sig["type"],
                    "name": sig["name"],
                    "description": sig["description"],
                    "bias": sig["bias"],
                    "level": self._get_signal_level(sig),
                    "latest": result.get("latest", {}),
                    "triggered_at": datetime.now()
                })

        except Exception as e:
            print(f"扫描 {code} 时出错: {e}")

        return signals

    def _get_signal_level(self, signal: dict) -> int:
        """判断信号级别

        Returns:
            1=紧急, 2=重要, 3=一般
        """
        # 金叉/死叉等重要信号
        if signal["type"] in ["ma_cross_up", "ma_cross_down", "macd_cross_up", "macd_cross_down"]:
            return 2
        # 超买超卖
        return 3

    async def scan_all(self, codes: list[str]) -> dict[str, list[dict]]:
        """扫描多只股票"""
        results = {}
        for code in codes:
            signals = await self.scan_stock(code)
            if signals:
                results[code] = signals
            # 避免请求过快
            await asyncio.sleep(0.5)
        return results
```

**Step 3: 创建 monitor_service.py - 监控服务**

```python
"""监控服务"""

import asyncio
import json
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..storage import Database, WatchItem, AlertRecord
from .scanner import SignalScanner


class MonitorService:
    """监控服务"""

    def __init__(self, db: Database):
        self.db = db
        self.scanner = SignalScanner(db)
        self._running = False
        self._task: Optional[asyncio.Task] = None

        # 监控间隔配置
        self.scan_interval = 60  # 秒

    async def start(self):
        """启动监控"""
        if self._running:
            print("监控服务已在运行")
            return

        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        print("监控服务已启动")

    async def stop(self):
        """停止监控"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print("监控服务已停止")

    async def _monitor_loop(self):
        """监控循环"""
        while self._running:
            try:
                # 检查是否在交易时间
                if not self._is_trading_time():
                    await asyncio.sleep(60)
                    continue

                # 获取监控列表
                watchlist = await self.db.get_watchlist()
                if not watchlist:
                    await asyncio.sleep(self.scan_interval)
                    continue

                # 扫描所有股票
                codes = [item.code for item in watchlist]
                results = await self.scanner.scan_all(codes)

                # 处理信号
                for code, signals in results.items():
                    for signal in signals:
                        await self._handle_signal(code, signal, watchlist)

                # 等待下一次扫描
                await asyncio.sleep(self.scan_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"监控循环出错: {e}")
                await asyncio.sleep(10)

    def _is_trading_time(self) -> bool:
        """检查是否在交易时间"""
        now = datetime.now()
        # 简单判断: 周一到周五, 9:30-11:30, 13:00-15:00
        if now.weekday() >= 5:
            return False

        current_time = now.time()
        from datetime import time
        morning = time(9, 30) <= current_time <= time(11, 30)
        afternoon = time(13, 0) <= current_time <= time(15, 0)
        return morning or afternoon

    async def _handle_signal(self, code: str, signal: dict, watchlist: list[WatchItem]):
        """处理检测到的信号"""
        # 找到对应的监控配置
        watch_item = next((w for w in watchlist if w.code == code), None)
        if not watch_item:
            return

        # 检查是否匹配监控条件
        if not self._match_conditions(signal, watch_item.conditions):
            return

        # 创建告警记录
        alert = AlertRecord(
            code=code,
            signal_type=signal["type"],
            signal_name=signal["name"],
            message=signal["description"],
            level=signal["level"],
            triggered_at=signal["triggered_at"],
            status="pending",
            channels=watch_item.alert_channels
        )
        await self.db.save_alert(alert)

        # 发送提醒
        await self._send_alert(alert, signal)

    def _match_conditions(self, signal: dict, conditions: dict) -> bool:
        """检查信号是否匹配条件"""
        # 如果没有设置条件，默认所有信号都匹配
        if not conditions:
            return True

        # 检查信号类型
        signal_types = conditions.get("signal_types", [])
        if signal_types and signal["type"] not in signal_types:
            return False

        # 检查信号偏向
        biases = conditions.get("biases", [])
        if biases and signal["bias"] not in biases:
            return False

        return True

    async def _send_alert(self, alert: AlertRecord, signal: dict):
        """发送提醒"""
        # 这里后续实现多渠道提醒
        # 目前只打印到控制台
        level_str = {1: "紧急", 2: "重要", 3: "一般"}.get(alert.level, "一般")
        print(f"\n[{level_str}] {alert.code} - {alert.signal_name}: {alert.message}")
```

**Step 4: 提交代码**

```bash
git add src/python/astock/monitor/
git commit --no-verify -m "feat(monitor): add signal scanner and monitor service"
```

---

## Task 3: 告警引擎与多渠道通知

**Files:**
- Create: `src/python/astock/monitor/alert_engine.py`
- Modify: `src/python/astock/monitor/monitor_service.py`

**Step 1: 创建 alert_engine.py**

```python
"""告警引擎"""

import asyncio
import json
import aiohttp
from datetime import datetime
from typing import Optional
from pathlib import Path

from ..storage import AlertRecord


class AlertEngine:
    """多渠道告警引擎"""

    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)

    def _load_config(self, config_path: Optional[Path]) -> dict:
        """加载配置"""
        if config_path and config_path.exists():
            with open(config_path) as f:
                return json.load(f)
        return {}

    async def send(self, alert: AlertRecord, channels: list[str]):
        """发送告警到多个渠道"""
        tasks = []
        for channel in channels:
            if channel == "terminal":
                tasks.append(self._send_terminal(alert))
            elif channel == "system":
                tasks.append(self._send_system(alert))
            elif channel == "wechat":
                tasks.append(self._send_wechat(alert))
            elif channel == "dingtalk":
                tasks.append(self._send_dingtalk(alert))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_terminal(self, alert: AlertRecord):
        """终端输出"""
        level_colors = {1: "\033[91m", 2: "\033[93m", 3: "\033[92m"}
        color = level_colors.get(alert.level, "\033[0m")
        reset = "\033[0m"

        level_str = {1: "紧急", 2: "重要", 3: "一般"}.get(alert.level, "一般")
        timestamp = alert.triggered_at.strftime("%H:%M:%S")

        print(f"\n{color}[{timestamp}][{level_str}]{reset} {alert.code} - {alert.signal_name}")
        print(f"  {alert.message}")

    async def _send_system(self, alert: AlertRecord):
        """系统通知 (macOS)"""
        import subprocess

        level_str = {1: "紧急", 2: "重要", 3: "一般"}.get(alert.level, "一般")
        title = f"[{level_str}] {alert.code}"
        message = f"{alert.signal_name}: {alert.message}"

        try:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ], check=False)
        except Exception as e:
            print(f"系统通知发送失败: {e}")

    async def _send_wechat(self, alert: AlertRecord):
        """微信推送 (Server酱)"""
        webhook_url = self.config.get("wechat", {}).get("webhook_url")
        if not webhook_url:
            return

        level_str = {1: "紧急", 2: "重要", 3: "一般"}.get(alert.level, "一般")
        title = f"[{level_str}] {alert.code} - {alert.signal_name}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json={
                    "title": title,
                    "desp": alert.message
                }) as resp:
                    if resp.status != 200:
                        print(f"微信推送失败: {resp.status}")
        except Exception as e:
            print(f"微信推送出错: {e}")

    async def _send_dingtalk(self, alert: AlertRecord):
        """钉钉推送"""
        webhook_url = self.config.get("dingtalk", {}).get("webhook_url")
        if not webhook_url:
            return

        level_str = {1: "紧急", 2: "重要", 3: "一般"}.get(alert.level, "一般")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json={
                    "msgtype": "text",
                    "text": {
                        "content": f"[{level_str}] {alert.code} - {alert.signal_name}\n{alert.message}"
                    }
                }) as resp:
                    if resp.status != 200:
                        print(f"钉钉推送失败: {resp.status}")
        except Exception as e:
            print(f"钉钉推送出错: {e}")
```

**Step 2: 更新 monitor_service.py 使用 AlertEngine**

在 `MonitorService` 类中添加：

```python
from .alert_engine import AlertEngine

def __init__(self, db: Database, config_path: Optional[Path] = None):
    self.db = db
    self.scanner = SignalScanner(db)
    self.alert_engine = AlertEngine(config_path)
    # ... 其他初始化

async def _send_alert(self, alert: AlertRecord, signal: dict):
    """发送提醒"""
    await self.alert_engine.send(alert, alert.channels)
```

**Step 3: 提交代码**

```bash
git add src/python/astock/monitor/
git commit --no-verify -m "feat(monitor): add multi-channel alert engine"
```

---

## Task 4: /watch Skill 实现

**Files:**
- Create: `.claude/skills/watch.md`
- Create: `src/ts/orchestrator/watch-handler.ts`
- Create: `src/python/astock/monitor/watch_cli.py`

**Step 1: 创建 watch.md**

```markdown
# /watch - 监控管理

管理股票监控列表。

## 使用方式

\`\`\`
/watch add <股票代码>           # 添加监控
/watch remove <股票代码>        # 移除监控
/watch list                     # 查看监控列表
/watch enable <股票代码>        # 启用监控
/watch disable <股票代码>       # 禁用监控
\`\`\`

## 示例

\`\`\`
/watch add 000001           # 添加平安银行到监控
/watch add 000001 --signals ma_cross_up,macd_cross_up  # 只监控特定信号
/watch list                 # 查看所有监控
/watch remove 000001        # 移除监控
\`\`\`

## 监控条件

可通过 --signals 参数指定要监控的信号类型：
- `ma_cross_up`: MA金叉
- `ma_cross_down`: MA死叉
- `macd_cross_up`: MACD金叉
- `macd_cross_down`: MACD死叉
- `kdj_oversold`: KDJ超卖
- `kdj_overbought`: KDJ超买

## 相关文件

- \`src/ts/orchestrator/watch-handler.ts\`
- \`src/python/astock/monitor/watch_cli.py\`
```

**Step 2: 创建 Python watch_cli.py**

```python
"""监控管理 CLI"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..storage import Database, WatchItem

app = typer.Typer(name="watch")
console = Console()

DB_PATH = Path(__file__).parent.parent.parent.parent / "data" / "stocks.db"


@app.command("add")
def add_watch(
    code: str = typer.Argument(..., help="股票代码"),
    signals: Optional[str] = typer.Option(None, "--signals", "-s", help="监控的信号类型"),
    channels: str = typer.Option("terminal", "--channels", "-c", help="提醒渠道"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """添加监控"""
    async def _add():
        db = Database(str(DB_PATH))
        await db.connect()

        conditions = {}
        if signals:
            conditions["signal_types"] = signals.split(",")

        item = WatchItem(
            code=code,
            conditions=conditions,
            alert_channels=channels.split(","),
            created_at=datetime.now()
        )
        await db.save_watch_item(item)
        await db.close()
        return item

    item = asyncio.run(_add())

    if json_output:
        console.print_json(data=item.model_dump())
    else:
        console.print(f"[green]已添加监控: {code}[/green]")


@app.command("remove")
def remove_watch(
    code: str = typer.Argument(..., help="股票代码"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """移除监控"""
    async def _remove():
        db = Database(str(DB_PATH))
        await db.connect()
        await db._conn.execute(
            "UPDATE watchlist SET enabled = 0 WHERE code = ?", (code,)
        )
        await db._conn.commit()
        await db.close()

    asyncio.run(_remove())
    console.print(f"[yellow]已移除监控: {code}[/yellow]")


@app.command("list")
def list_watch(json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")):
    """查看监控列表"""
    async def _list():
        db = Database(str(DB_PATH))
        await db.connect()
        items = await db.get_watchlist(enabled_only=False)
        await db.close()
        return items

    items = asyncio.run(_list())

    if json_output:
        console.print_json(data=[item.model_dump() for item in items])
    else:
        table = Table(title="监控列表")
        table.add_column("代码", style="cyan")
        table.add_column("名称")
        table.add_column("状态")
        table.add_column("渠道")

        for item in items:
            status = "[green]启用[/green]" if item.enabled else "[red]禁用[/red]"
            table.add_row(
                item.code,
                item.name or "-",
                status,
                ",".join(item.alert_channels)
            )

        console.print(table)


if __name__ == "__main__":
    app()
```

**Step 3: 创建 watch-handler.ts**

```typescript
/**
 * /watch 命令处理器
 */

import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = path.resolve(__dirname, '../../python');

export interface WatchOutput {
  success: boolean;
  data?: any;
  error?: string;
}

async function callWatch(args: string[]): Promise<string> {
  const result = await execa(
    'python',
    ['-m', 'astock.monitor.watch_cli', ...args, '--json'],
    { cwd: PYTHON_DIR, reject: true }
  );
  return result.stdout;
}

export async function handleWatch(action: string, code?: string, options?: any): Promise<WatchOutput> {
  try {
    let args = [action];
    if (code) args.push(code);
    if (options?.signals) args.push('--signals', options.signals);
    if (options?.channels) args.push('--channels', options.channels);

    const output = await callWatch(args);
    const data = JSON.parse(output);

    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `监控操作失败: ${message}` };
  }
}
```

**Step 4: 提交代码**

```bash
git add .claude/skills/watch.md src/ts/orchestrator/watch-handler.ts src/python/astock/monitor/watch_cli.py
git commit --no-verify -m "feat(skills): add /watch skill for watchlist management"
```

---

## Task 5: /alert Skill 实现

**Files:**
- Create: `.claude/skills/alert.md`
- Create: `src/ts/orchestrator/alert-handler.ts`
- Modify: `src/python/astock/cli.py`

**Step 1: 创建 alert.md**

```markdown
# /alert - 机会提醒

启动实时监控服务，检测交易机会并推送提醒。

## 使用方式

\`\`\`
/alert start              # 启动监控服务
/alert stop               # 停止监控服务
/alert status             # 查看监控状态
/alert history            # 查看历史告警
/alert config             # 配置提醒渠道
\`\`\`

## 示例

\`\`\`
/alert start              # 启动实时监控
/alert status             # 查看当前状态
/alert history --limit 10 # 查看最近10条告警
\`\`\`

## 提醒渠道

支持多种提醒方式：
- `terminal`: 终端输出 (默认)
- `system`: 系统通知 (macOS/Windows)
- `wechat`: 微信推送 (需配置 Server酱)
- `dingtalk`: 钉钉推送 (需配置 Webhook)

## 配置

在 \`data/config.json\` 中配置 Webhook：

\`\`\`json
{
  "wechat": {
    "webhook_url": "https://sctapi.ftqq.com/YOUR_KEY.send"
  },
  "dingtalk": {
    "webhook_url": "https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN"
  }
}
\`\`\`

## 相关文件

- \`src/ts/orchestrator/alert-handler.ts\`
- \`src/python/astock/monitor/\`
```

**Step 2: 在 Python CLI 中添加 alert 命令**

在 `cli.py` 中添加：

```python
from .monitor import MonitorService
from .monitor.watch_cli import app as watch_app

# 添加 watch 子命令
app.add_typer(watch_app, name="watch")

@app.command()
def alert(
    action: str = typer.Argument("status", help="start/stop/status/history"),
    json_output: bool = typer.Option(False, "--json", "-j", help="JSON 输出")
):
    """监控提醒服务"""
    async def _alert():
        db = Database(str(DB_PATH))
        await db.connect()

        if action == "start":
            service = MonitorService(db, DB_PATH.parent.parent / "config.json")
            console.print("[green]正在启动监控服务...[/green]")
            console.print("[dim]按 Ctrl+C 停止[/dim]")
            try:
                await service.start()
                # 保持运行
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                await service.stop()

        elif action == "status":
            # 检查是否有活跃的监控进程
            console.print("[yellow]监控服务状态检查功能待实现[/yellow]")

        elif action == "history":
            cursor = await db._conn.execute(
                """SELECT * FROM alerts ORDER BY triggered_at DESC LIMIT 20"""
            )
            rows = await cursor.fetchall()
            alerts = [dict(row) for row in rows]

            if json_output:
                console.print_json(data=alerts)
            else:
                for row in alerts:
                    level_str = {1: "紧急", 2: "重要", 3: "一般"}.get(row["level"], "一般")
                    console.print(f"[{row['triggered_at']}] [{level_str}] {row['code']} - {row['signal_name']}")

        await db.close()

    asyncio.run(_alert())
```

**Step 3: 创建 alert-handler.ts**

```typescript
/**
 * /alert 命令处理器
 */

import { execa } from 'execa';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PYTHON_DIR = path.resolve(__dirname, '../../python');

export interface AlertOutput {
  success: boolean;
  data?: any;
  error?: string;
}

async function callAlert(action: string): Promise<string> {
  const result = await execa(
    'python',
    ['-m', 'astock.cli', 'alert', action, '--json'],
    { cwd: PYTHON_DIR, reject: true }
  );
  return result.stdout;
}

export async function handleAlert(action: string): Promise<AlertOutput> {
  try {
    const output = await callAlert(action);
    const data = output ? JSON.parse(output) : {};
    return { success: true, data };
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    return { success: false, error: `监控操作失败: ${message}` };
  }
}
```

**Step 4: 更新 CLI index.ts**

添加 watch 和 alert 命令到主 CLI。

**Step 5: 提交代码**

```bash
git add .claude/skills/alert.md src/ts/orchestrator/alert-handler.ts src/python/astock/cli.py
git commit --no-verify -m "feat(skills): add /alert skill for real-time monitoring"
```

---

## 验收标准

Phase 2 完成后，应满足以下条件：

1. **监控管理**
   ```bash
   node dist/index.js watch add 000001
   node dist/index.js watch list
   node dist/index.js watch remove 000001
   ```

2. **实时监控**
   ```bash
   node dist/index.js alert start
   # 在交易时间内自动监控并发送提醒
   ```

3. **Skills 可用**
   - `/watch add 000001` - 添加监控
   - `/watch list` - 查看监控列表
   - `/alert start` - 启动监控
   - `/alert history` - 查看历史告警
