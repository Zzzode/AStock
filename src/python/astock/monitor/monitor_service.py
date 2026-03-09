"""监控服务 - 带日志和错误处理"""

import asyncio
from datetime import datetime, time
from pathlib import Path
from typing import Optional, Any

from ..storage import Database, WatchItem, AlertRecord
from ..quote import QuoteService
from ..utils import get_logger, DataSourceError, AlertError
from .scanner import SignalScanner
from .alert_engine import AlertEngine

logger = get_logger("monitor_service")


class MonitorService:
    """股票监控服务"""

    def __init__(
        self,
        db: Database,
        quote_service: QuoteService,
        config_path: Optional[Path] = None,
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
        self._task: Optional[asyncio.Task[None]] = None
        self._scan_interval = 60  # 扫描间隔(秒)
        self._start_time: Optional[datetime] = None
        logger.debug("监控服务初始化完成")

    async def start(self) -> None:
        """启动监控服务"""
        if self._running:
            logger.warning("监控服务已在运行中")
            return

        self._running = True
        self._start_time = datetime.now()
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"监控服务已启动，扫描间隔: {self._scan_interval}秒")

    async def stop(self) -> None:
        """停止监控服务"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("监控服务已停止")

    async def _monitor_loop(self) -> None:
        """监控循环"""
        while self._running:
            try:
                # 检查是否在交易时间
                if self._is_trading_time():
                    await self._scan_watch_list()
                else:
                    logger.debug("非交易时间，等待...")

                # 等待下一次扫描
                await asyncio.sleep(self._scan_interval)

            except asyncio.CancelledError:
                logger.debug("监控循环被取消")
                break
            except Exception as e:
                logger.error(f"监控循环错误: {e}", exc_info=True)
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

        return (morning_start <= current_time <= morning_end) or (
            afternoon_start <= current_time <= afternoon_end
        )

    async def _scan_watch_list(self) -> None:
        """扫描监控列表"""
        # 获取启用的监控项
        try:
            watch_items = await self.db.get_watch_items(enabled_only=True)
        except Exception as e:
            logger.error(f"获取监控列表失败: {e}", exc_info=True)
            return

        if not watch_items:
            logger.debug("监控列表为空")
            return

        logger.info(f"扫描 {len(watch_items)} 只股票...")

        # 并行扫描
        tasks = [self._scan_single_item(item) for item in watch_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        success_count = sum(1 for r in results if r is None or r is True)
        error_count = sum(1 for r in results if isinstance(r, Exception))
        signal_count = sum(1 for r in results if r is True)

        logger.info(
            f"扫描完成: 成功={success_count}, 错误={error_count}, 发现信号={signal_count}"
        )

    async def _scan_single_item(self, item: WatchItem) -> bool | None | Exception:
        """扫描单个监控项

        Args:
            item: 监控项

        Returns:
            True 如果发现信号，None 如果没有，Exception 如果出错
        """
        try:
            result = await self.scanner.scan_stock(item.code)

            # 处理检测到的信号
            if result.get("signals"):
                await self._handle_signal(item, result)
                return True
            return None

        except DataSourceError as e:
            logger.warning(f"扫描 {item.code} 数据错误: {e}")
            return e
        except Exception as e:
            logger.error(f"扫描 {item.code} 失败: {e}", exc_info=True)
            return e

    async def _handle_signal(self, item: WatchItem, scan_result: dict[str, Any]) -> None:
        """处理检测到的信号

        Args:
            item: 监控项
            scan_result: 扫描结果
        """
        signals = scan_result.get("signals", [])
        level = scan_result.get("level", 3)

        for signal in signals:
            try:
                # 创建告警记录
                record = AlertRecord(
                    code=item.code,
                    signal_type=signal.get("type", "unknown"),
                    signal_name=signal.get("name", "未知信号"),
                    message=signal.get("description", ""),
                    level=level,
                    triggered_at=datetime.now(),
                    status="pending",
                    channels=item.alert_channels,
                )

                # 保存到数据库
                record_id = await self.db.save_alert_record(record)
                record.id = record_id

                logger.info(f"发现信号: {item.code} - {signal.get('name', 'unknown')}")

                # 发送提醒
                await self._send_alert(record, item)

            except Exception as e:
                logger.error(
                    f"处理信号失败: {item.code} - {signal.get('name')}: {e}",
                    exc_info=True,
                )

    async def _send_alert(self, record: AlertRecord, item: WatchItem) -> None:
        """发送告警提醒

        Args:
            record: 告警记录
            item: 监控项
        """
        try:
            # 使用 AlertEngine 发送告警
            results = await self.alert_engine.send(record, record.channels)

            # 检查发送结果
            success = all(results.values())
            status = "sent" if success else "failed"

            # 更新告警状态
            if record.id is not None:
                await self.db.update_alert_status(record.id, status)

            if success:
                logger.info(f"告警发送成功: {record.code} - {record.signal_name}")
            else:
                failed_channels = [k for k, v in results.items() if not v]
                logger.warning(
                    f"告警发送部分失败: {record.code}, 失败渠道: {failed_channels}"
                )

        except Exception as e:
            logger.error(f"发送告警失败: {e}", exc_info=True)
            raise AlertError(f"发送告警失败: {e}") from e

    def set_scan_interval(self, seconds: int) -> None:
        """设置扫描间隔

        Args:
            seconds: 扫描间隔(秒)
        """
        self._scan_interval = max(10, seconds)  # 最小10秒
        logger.info(f"扫描间隔已设置为: {self._scan_interval}秒")

    def get_status(self) -> dict[str, Any]:
        """获取服务状态"""
        return {
            "running": self._running,
            "scan_interval": self._scan_interval,
            "start_time": self._start_time.isoformat() if self._start_time else None,
        }
