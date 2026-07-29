"""Monitor service - with logging and error handling"""

import asyncio
from datetime import datetime, time
from pathlib import Path
from typing import Optional, Any, cast

from ..storage import Database, WatchItem, AlertRecord
from ..quote import QuoteService
from ..quote.market_stream import MarketStream
from ..utils import get_logger, DataSourceError, AlertError
from .scanner import SignalScanner
from .alert_engine import AlertEngine
from .alert_events import build_alert_market_event, encode_alert_message

logger = get_logger("monitor_service")

logger = get_logger("monitor_service")


class MonitorService:
    """Stock monitoring service"""

    def __init__(
        self,
        db: Database,
        quote_service: QuoteService,
        config_path: Optional[Path] = None,
    ):
        """
        Args:
            db: Database instance
            quote_service: Quote service instance
            config_path: Alert configuration file path
        """
        self.db = db
        self.quote_service = quote_service
        self.scanner = SignalScanner(quote_service)
        self.alert_engine = AlertEngine(config_path)
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._scan_interval = 60  # Scan interval (seconds)
        self._start_time: Optional[datetime] = None
        self._market_stream = MarketStream()
        self._stream_mode = True  # Use push-based stream when possible
        logger.debug("Monitor service initialization complete")

    async def start(self) -> None:
        """Start the monitor service"""
        if self._running:
            logger.warning("Monitor service is already running")
            return

        self._running = True
        self._start_time = datetime.now()
        self._task = asyncio.create_task(self._monitor_loop())
        logger.info(f"Monitor service started, scan interval: {self._scan_interval}s")

    async def stop(self) -> None:
        """Stop the monitor service"""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Monitor service stopped")

    async def _monitor_loop(self) -> None:
        """Monitor loop — uses MarketStream for push-based updates during trading hours,
        falls back to interval polling outside trading hours or on stream failure."""
        while self._running:
            try:
                if self._is_trading_time():
                    if self._stream_mode:
                        await self._stream_scan_cycle()
                    else:
                        await self._scan_watch_list()
                else:
                    logger.debug("Outside trading hours, waiting...")

                await asyncio.sleep(self._scan_interval)

            except asyncio.CancelledError:
                logger.debug("Monitor loop cancelled")
                break
            except Exception as e:
                logger.error(f"Monitor loop error: {e}", exc_info=True)
                await asyncio.sleep(self._scan_interval)

    async def _stream_scan_cycle(self) -> None:
        """Use MarketStream to fetch real-time snapshots for all watched codes."""
        try:
            watch_items = await self.db.get_watch_items(enabled_only=True)
        except Exception as e:
            logger.error(f"Failed to get watch list: {e}")
            return

        if not watch_items:
            return

        codes = [item.code for item in watch_items]
        ticks = await self._market_stream.get_snapshot(codes)

        if not ticks:
            logger.debug("Stream returned no ticks, falling back to scanner")
            await self._scan_watch_list()
            return

        tick_map = {tick.code: tick for tick in ticks}
        signal_count = 0

        for item in watch_items:
            tick = tick_map.get(item.code)
            if tick is None:
                continue
            try:
                result = await self.scanner.scan_stock(item.code)
                if result.get("signals"):
                    await self._handle_signal(item, result)
                    signal_count += 1
            except Exception as e:
                logger.warning(f"Stream scan error for {item.code}: {e}")

        if signal_count:
            logger.info(f"Stream cycle: {len(watch_items)} items, {signal_count} signals")

    def _is_trading_time(self) -> bool:
        """Check if current time is within trading hours

        A-share trading hours:
        - Morning: 9:30 - 11:30
        - Afternoon: 13:00 - 15:00

        Returns:
            Whether it is within trading hours
        """
        now = datetime.now()
        current_time = now.time()

        # Morning trading hours
        morning_start = time(9, 30)
        morning_end = time(11, 30)

        # Afternoon trading hours
        afternoon_start = time(13, 0)
        afternoon_end = time(15, 0)

        return (morning_start <= current_time <= morning_end) or (
            afternoon_start <= current_time <= afternoon_end
        )

    async def _scan_watch_list(self) -> None:
        """Scan the watch list"""
        # Get enabled watch items
        try:
            watch_items = await self.db.get_watch_items(enabled_only=True)
        except Exception as e:
            logger.error(f"Failed to get watch list: {e}", exc_info=True)
            return

        if not watch_items:
            logger.debug("Watch list is empty")
            return

        logger.info(f"Scanning {len(watch_items)} stocks...")

        # Parallel scan
        tasks = [self._scan_single_item(item) for item in watch_items]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Summarize results
        success_count = sum(1 for r in results if r is None or r is True)
        error_count = sum(1 for r in results if isinstance(r, Exception))
        signal_count = sum(1 for r in results if r is True)

        logger.info(
            f"Scan complete: success={success_count}, errors={error_count}, signals found={signal_count}"
        )

    async def _scan_single_item(self, item: WatchItem) -> bool | None | Exception:
        """Scan a single watch item

        Args:
            item: Watch item

        Returns:
            True if signal found, None if not, Exception if error
        """
        try:
            result = await self.scanner.scan_stock(item.code)

            # Handle detected signals
            if result.get("signals"):
                await self._handle_signal(item, result)
                return True
            return None

        except DataSourceError as e:
            logger.warning(f"Scan {item.code} data error: {e}")
            return cast(Exception, e)
        except Exception as e:
            logger.error(f"Scan {item.code} failed: {e}", exc_info=True)
            return e

    async def _handle_signal(
        self, item: WatchItem, scan_result: dict[str, Any]
    ) -> None:
        """Handle detected signals

        Args:
            item: Watch item
            scan_result: Scan result
        """
        signals = scan_result.get("signals", [])
        level = scan_result.get("level", 3)

        for signal in signals:
            try:
                triggered_at = datetime.now()
                message_text = str(signal.get("description", ""))
                signal_type = str(signal.get("type", "unknown"))
                signal_name = str(signal.get("name", "Unknown signal"))
                alert_payload = {
                    "code": item.code,
                    "name": item.name,
                    "signal_type": signal_type,
                    "signal_name": signal_name,
                    "message": message_text,
                    "level": level,
                    "triggered_at": triggered_at,
                    "status": "pending",
                    "channels": item.alert_channels,
                    "direction": signal.get("bias"),
                    "metrics": scan_result.get("latest", {}),
                    "data_quality": scan_result.get("data_quality", "partial"),
                }
                market_event = build_alert_market_event(
                    alert_payload,
                    source="monitor.signal_scanner",
                )

                # Create alert record
                record = AlertRecord(
                    code=item.code,
                    signal_type=signal_type,
                    signal_name=signal_name,
                    message=encode_alert_message(message_text, market_event),
                    level=level,
                    triggered_at=triggered_at,
                    status="pending",
                    channels=item.alert_channels,
                )

                # Save to database
                record_id = await self.db.save_alert_record(record)
                record.id = record_id

                logger.info(
                    f"Signal found: {item.code} - {signal.get('name', 'unknown')}"
                )

                # Send alert
                await self._send_alert(record, item)

            except Exception as e:
                logger.error(
                    f"Failed to handle signal: {item.code} - {signal.get('name')}: {e}",
                    exc_info=True,
                )

    async def _send_alert(self, record: AlertRecord, item: WatchItem) -> None:
        """Send alert notification

        Args:
            record: Alert record
            item: Watch item
        """
        try:
            # Use AlertEngine to send alert
            results = await self.alert_engine.send(record, record.channels)

            # Check send results
            success = all(results.values())
            status = "sent" if success else "failed"

            # Update alert status
            if record.id is not None:
                await self.db.update_alert_status(record.id, status)

            if success:
                logger.info(
                    f"Alert sent successfully: {record.code} - {record.signal_name}"
                )
            else:
                failed_channels = [k for k, v in results.items() if not v]
                logger.warning(
                    f"Alert partially failed: {record.code}, failed channels: {failed_channels}"
                )

        except Exception as e:
            logger.error(f"Failed to send alert: {e}", exc_info=True)
            raise AlertError(f"Failed to send alert: {e}") from e

    def set_scan_interval(self, seconds: int) -> None:
        """Set scan interval

        Args:
            seconds: Scan interval (seconds)
        """
        self._scan_interval = max(10, seconds)  # Minimum 10 seconds
        logger.info(f"Scan interval set to: {self._scan_interval}s")

    def get_status(self) -> dict[str, Any]:
        """Get service status"""
        return {
            "running": self._running,
            "scan_interval": self._scan_interval,
            "start_time": self._start_time.isoformat() if self._start_time else None,
        }
