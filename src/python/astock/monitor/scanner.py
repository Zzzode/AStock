"""Market-structure monitor scanner."""

from datetime import datetime
from typing import Any

from ..quote import QuoteService


class SignalScanner:
    """Scan observable price, liquidity, and volatility dislocations.

    This scanner deliberately does not call ``TechnicalAnalyzer``. MA, MACD,
    KDJ, RSI, and similar indicator outputs are analysis aids, not production
    monitoring signals or alert-priority inputs.
    """

    _HISTORY_WINDOW = 20

    def __init__(self, quote_service: QuoteService):
        self.quote_service = quote_service

    async def scan_stock(self, code: str) -> dict[str, Any]:
        """Scan a stock for market-structure observations."""
        try:
            df = await self.quote_service.get_daily(code, save=False)

            if df.empty or len(df) < self._HISTORY_WINDOW + 1:
                return {
                    "code": code,
                    "signals": [],
                    "level": 0,
                    "error": "Insufficient data",
                }

            latest = df.iloc[-1]
            history = df.iloc[-(self._HISTORY_WINDOW + 1):-1]
            previous = df.iloc[-2]

            close = float(latest["close"])
            previous_close = float(previous["close"])
            high = float(latest["high"])
            low = float(latest["low"])
            volume = float(latest["volume"])
            amount = float(latest.get("amount", 0) or 0)
            change_pct = (
                (close - previous_close) / previous_close
                if previous_close > 0
                else 0.0
            )
            range_pct = (high - low) / previous_close if previous_close > 0 else 0.0
            median_volume = float(history["volume"].median())
            volume_multiple = volume / median_volume if median_volume > 0 else None

            signals = self._build_market_structure_signals(
                change_pct=change_pct,
                range_pct=range_pct,
                volume_multiple=volume_multiple,
            )

            return {
                "code": code,
                "signals": signals,
                "level": self._get_signal_level(signals),
                "latest": {
                    "close": close,
                    "previous_close": previous_close,
                    "change_pct": change_pct,
                    "high": high,
                    "low": low,
                    "volume": volume,
                    "amount": amount,
                    "daily_range_pct": range_pct,
                    "volume_multiple_20d_median": volume_multiple,
                },
                "scanned_at": datetime.now(),
            }

        except Exception as exc:
            return {
                "code": code,
                "signals": [],
                "level": 0,
                "error": str(exc),
            }

    async def scan_all(self, codes: list[str]) -> list[dict[str, Any]]:
        """Scan multiple stocks."""
        return [await self.scan_stock(code) for code in codes]

    def _build_market_structure_signals(
        self,
        *,
        change_pct: float,
        range_pct: float,
        volume_multiple: float | None,
    ) -> list[dict[str, Any]]:
        """Turn raw, reproducible dislocations into monitor observations."""
        signals: list[dict[str, Any]] = []
        bias = "bullish" if change_pct > 0 else "bearish"

        if abs(change_pct) >= 0.07:
            signals.append(
                {
                    "type": "price_dislocation",
                    "name": "Large Price Dislocation",
                    "description": "Daily price move exceeded 7%.",
                    "bias": bias,
                    "priority": 2,
                }
            )

        if range_pct >= 0.07:
            signals.append(
                {
                    "type": "range_expansion",
                    "name": "Wide Intraday Range",
                    "description": "Intraday range exceeded 7% of the prior close.",
                    "bias": bias,
                    "priority": 2,
                }
            )

        if volume_multiple is not None and volume_multiple >= 2.0:
            signals.append(
                {
                    "type": "volume_spike",
                    "name": "Volume Dislocation",
                    "description": "Volume exceeded twice the prior 20-session median.",
                    "bias": bias,
                    "priority": 2,
                }
            )

        if len(signals) >= 2:
            for signal in signals:
                signal["priority"] = 1

        return signals

    def _get_signal_level(self, signals: list[dict[str, Any]]) -> int:
        """Return the highest structural-alert priority, or zero for no alert."""
        priorities: list[int] = []
        for signal in signals:
            priority = signal.get("priority")
            if isinstance(priority, int):
                priorities.append(priority)
        return min(priorities) if priorities else 0
