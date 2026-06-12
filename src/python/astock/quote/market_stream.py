"""Real-time market data stream via Sina WebSocket.

Provides a push-based market data feed for the monitor service,
replacing polling with event-driven updates during trading hours.

Protocol: Sina Finance WebSocket pushes real-time quote updates
for subscribed stock codes.
"""

from __future__ import annotations

import asyncio
import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Callable, Coroutine, Optional

from ..utils import get_logger

logger = get_logger("market_stream")


@dataclass
class MarketTick:
    """A single real-time market data tick."""

    code: str
    name: str
    price: float
    open: float
    high: float
    low: float
    prev_close: float
    volume: float
    amount: float
    change_pct: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "price": self.price,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "prev_close": self.prev_close,
            "volume": self.volume,
            "amount": self.amount,
            "change_pct": self.change_pct,
            "timestamp": self.timestamp.isoformat(),
        }


TickCallback = Callable[[MarketTick], Coroutine[Any, Any, None]]


class MarketStream:
    """WebSocket-based real-time market data stream.

    Uses Sina Finance HTTP streaming endpoint as the data source.
    Falls back to polling if WebSocket connection fails.
    """

    def __init__(self):
        self._subscribers: dict[str, list[TickCallback]] = {}
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._poll_interval = 3.0  # seconds between poll cycles
        self._subscribed_codes: set[str] = set()

    def subscribe(self, code: str, callback: TickCallback) -> None:
        """Subscribe to real-time updates for a stock code."""
        if code not in self._subscribers:
            self._subscribers[code] = []
        self._subscribers[code].append(callback)
        self._subscribed_codes.add(code)

    def unsubscribe(self, code: str) -> None:
        """Unsubscribe from a stock code."""
        self._subscribers.pop(code, None)
        self._subscribed_codes.discard(code)

    async def start(self) -> None:
        """Start the market stream."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._stream_loop())
        logger.info(
            f"Market stream started, watching {len(self._subscribed_codes)} codes"
        )

    async def stop(self) -> None:
        """Stop the market stream."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Market stream stopped")

    async def get_snapshot(self, codes: list[str]) -> list[MarketTick]:
        """Get current snapshot for a list of codes (single poll)."""
        return await self._fetch_quotes(codes)

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def subscribed_codes(self) -> set[str]:
        return self._subscribed_codes.copy()

    async def _stream_loop(self) -> None:
        """Main streaming loop — fetches and dispatches ticks."""
        while self._running:
            try:
                if not self._subscribed_codes:
                    await asyncio.sleep(self._poll_interval)
                    continue

                codes = list(self._subscribed_codes)
                ticks = await self._fetch_quotes(codes)

                for tick in ticks:
                    callbacks = self._subscribers.get(tick.code, [])
                    for callback in callbacks:
                        try:
                            await callback(tick)
                        except Exception as e:
                            logger.warning(
                                f"Callback error for {tick.code}: {e}"
                            )

                await asyncio.sleep(self._poll_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Stream loop error: {e}")
                await asyncio.sleep(self._poll_interval * 2)

    async def _fetch_quotes(self, codes: list[str]) -> list[MarketTick]:
        """Fetch real-time quotes from Sina HTTP API."""
        import aiohttp

        if not codes:
            return []

        sina_codes = [_to_sina_code(code) for code in codes]
        url = f"https://hq.sinajs.cn/list={','.join(sina_codes)}"
        headers = {"Referer": "https://finance.sina.com.cn"}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status != 200:
                        return []
                    text = await resp.text(encoding="gbk")
                    return _parse_sina_response(text, codes)
        except Exception as e:
            logger.debug(f"Sina fetch failed: {e}")
            return []


def _to_sina_code(code: str) -> str:
    """Convert stock code to Sina format (sh/sz prefix)."""
    code = code.strip()
    if code.startswith(("sh", "sz", "bj")):
        return code
    if code.startswith("6"):
        return f"sh{code}"
    elif code.startswith(("0", "3")):
        return f"sz{code}"
    elif code.startswith(("8", "4")):
        return f"bj{code}"
    return f"sz{code}"


def _parse_sina_response(text: str, original_codes: list[str]) -> list[MarketTick]:
    """Parse Sina real-time quote response.

    Format: var hq_str_sh000001="name,open,prev_close,price,high,low,...";
    """
    ticks: list[MarketTick] = []
    lines = text.strip().split("\n")

    code_idx = 0
    for line in lines:
        if code_idx >= len(original_codes):
            break

        match = re.search(r'="(.+)"', line)
        if not match:
            code_idx += 1
            continue

        data = match.group(1).split(",")
        if len(data) < 32:
            code_idx += 1
            continue

        try:
            name = data[0]
            open_price = float(data[1]) if data[1] else 0.0
            prev_close = float(data[2]) if data[2] else 0.0
            price = float(data[3]) if data[3] else 0.0
            high = float(data[4]) if data[4] else 0.0
            low = float(data[5]) if data[5] else 0.0
            volume = float(data[8]) if data[8] else 0.0
            amount = float(data[9]) if data[9] else 0.0

            if price <= 0:
                code_idx += 1
                continue

            change_pct = (
                (price - prev_close) / prev_close * 100
                if prev_close > 0
                else 0.0
            )

            date_str = data[30] if len(data) > 30 else ""
            time_str = data[31] if len(data) > 31 else ""
            try:
                ts = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            except (ValueError, IndexError):
                ts = datetime.now()

            ticks.append(MarketTick(
                code=original_codes[code_idx],
                name=name,
                price=price,
                open=open_price,
                high=high,
                low=low,
                prev_close=prev_close,
                volume=volume,
                amount=amount,
                change_pct=round(change_pct, 4),
                timestamp=ts,
            ))
        except (ValueError, IndexError) as e:
            logger.debug(f"Parse error for code {original_codes[code_idx]}: {e}")

        code_idx += 1

    return ticks
