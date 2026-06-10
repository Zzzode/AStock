"""Signal scanner"""

from datetime import datetime
from typing import Optional, Any

import pandas as pd

from ..quote import QuoteService
from ..analysis import TechnicalAnalyzer


class SignalScanner:
    """Technical signal scanner"""

    def __init__(self, quote_service: QuoteService):
        """
        Args:
            quote_service: Quote service instance
        """
        self.quote_service = quote_service

    async def scan_stock(self, code: str) -> dict[str, Any]:
        """Scan technical signals for a single stock

        Args:
            code: Stock code

        Returns:
            Scan result containing signal list and level
        """
        try:
            # Get daily data
            df = await self.quote_service.get_daily(code, save=False)

            if df.empty or len(df) < 30:
                return {
                    "code": code,
                    "signals": [],
                    "level": 0,
                    "error": "Insufficient data"
                }

            # Calculate technical indicators
            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()

            # Get signals
            result = analyzer.get_signals()
            signals = result.get("signals", [])

            # Determine signal level
            level = self._get_signal_level(signals)

            return {
                "code": code,
                "signals": signals,
                "level": level,
                "latest": result.get("latest", {}),
                "scanned_at": datetime.now()
            }

        except Exception as e:
            return {
                "code": code,
                "signals": [],
                "level": 0,
                "error": str(e)
            }

    async def scan_all(self, codes: list[str]) -> list[dict[str, Any]]:
        """Scan multiple stocks

        Args:
            codes: List of stock codes

        Returns:
            List of scan results
        """
        results = []
        for code in codes:
            result = await self.scan_stock(code)
            results.append(result)
        return results

    def _get_signal_level(self, signals: list[dict[str, Any]]) -> int:
        """Determine signal level

        Signal level rules:
        - 1 (Critical): Multiple strong buy/sell signals detected
        - 2 (Important): Trend signals such as golden cross/death cross detected
        - 3 (Normal): Reference signals such as overbought/oversold

        Args:
            signals: List of signals

        Returns:
            Signal level (1=Critical, 2=Important, 3=Normal, 0=No signal)
        """
        if not signals:
            return 0

        # Group by signal type
        bullish_signals = [s for s in signals if s.get("bias") == "bullish"]
        bearish_signals = [s for s in signals if s.get("bias") == "bearish"]

        # Critical level: multiple signals in the same direction
        if len(bullish_signals) >= 2 or len(bearish_signals) >= 2:
            return 1

        # Important level: crossover signals detected
        cross_signals = [
            s for s in signals
            if "cross" in s.get("type", "")
        ]
        if cross_signals:
            return 2

        # Normal level: other signals
        return 3
