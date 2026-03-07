"""监控服务"""

import asyncio
from datetime import datetime, time
from pathlib import Path
from typing import Optional

from ..storage import Database, WatchItem, AlertRecord
from ..quote import QuoteService
from .scanner import SignalScanner
from .alert_engine import AlertEngine


class MonitorService:
    """股票监控服务"""

    def __init__(
        self,
        db: Database,
        quote_service: QuoteService,
        config_path: Optional[Path] = None
    ):
        """
        Args:
            db: 数据库实例
            quote_service: 行情服务实例
            config_path: 告警配置文件路径
        """
        self.db = db
        self.quote_service = quote_service
        self.scanner = SignalScanner(quote_service)
        self.alert_engine = AlertEngine(config_path)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._scan_interval = 60  # 扫描间隔(秒)

    async def start(self) -> None:
        """启动监控服务"""
        if self._running:
            return

        self._running = True
        self._task = asyncio.create_task(self._monitor_loop())
        print(f"[MonitorService] 监控服务已启动")

    async def stop(self) -> None:
        """停止监控服务"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        print(f"[MonitorService] 监控服务已停止")

    async def _monitor_loop(self) -> None:
        """监控循环"""
        while self._running:
            try:
                # 检查是否在交易时间
                if self._is_trading_time():
                    await self._scan_watch_list()
                else:
                    print(f"[MonitorService] 非交易时间，等待...")

                # 等待下一次扫描
                await asyncio.sleep(self._scan_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[MonitorService] 监控循环错误: {e}")
                await asyncio.sleep(self._scan_interval)

    def _is_trading_time(self) -> bool:
        """检查当前是否在交易时间

        A股交易时间：
        - 上午: 9:30 - 11:30
        - 下午: 13:00 - 15:00

        Returns:
            是否在交易时间
        """
        now = datetime.now()
        current_time = now.time()

        # 上午交易时间
        morning_start = time(9, 30)
        morning_end = time(11, 30)

        # 下午交易时间
        afternoon_start = time(13, 0)
        afternoon_end = time(15, 0)

        return (
            (morning_start <= current_time <= morning_end) or
            (afternoon_start <= current_time <= afternoon_end)
        )

    async def _scan_watch_list(self) -> None:
        """扫描监控列表"""
        # 获取启用的监控项
        watch_items = await self.db.get_watch_items(enabled_only=True)

        if not watch_items:
            return

        print(f"[MonitorService] 扫描 {len(watch_items)} 只股票...")

        for item in watch_items:
            try:
                result = await self.scanner.scan_stock(item.code)

                # 处理检测到的信号
                if result.get("signals"):
                    await self._handle_signal(item, result)

            except Exception as e:
                print(f"[MonitorService] 扫描 {item.code} 失败: {e}")

    async def _handle_signal(self, item: WatchItem, scan_result: dict) -> None:
        """处理检测到的信号

        Args:
            item: 监控项
            scan_result: 扫描结果
        """
        signals = scan_result.get("signals", [])
        level = scan_result.get("level", 3)

        for signal in signals:
            # 创建告警记录
            record = AlertRecord(
                code=item.code,
                signal_type=signal.get("type", "unknown"),
                signal_name=signal.get("name", "未知信号"),
                message=signal.get("description", ""),
                level=level,
                triggered_at=datetime.now(),
                status="pending",
                channels=item.alert_channels
            )

            # 保存到数据库
            record_id = await self.db.save_alert_record(record)
            record.id = record_id

            # 发送提醒
            await self._send_alert(record, item)

    async def _send_alert(self, record: AlertRecord, item: WatchItem) -> None:
        """发送告警提醒

        Args:
            record: 告警记录
            item: 监控项
        """
        # 使用 AlertEngine 发送告警
        results = await self.alert_engine.send(record, record.channels)

        # 检查发送结果
        success = all(results.values())
        status = "sent" if success else "failed"

        # 更新告警状态
        await self.db.update_alert_status(record.id, status)

    def set_scan_interval(self, seconds: int) -> None:
        """设置扫描间隔

        Args:
            seconds: 扫描间隔(秒)
        """
        self._scan_interval = max(10, seconds)  # 最小10秒
