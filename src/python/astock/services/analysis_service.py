"""Price-and-volume observation service.

This service returns raw, timestamped market observations.  It deliberately
does not turn indicator thresholds into directional signals or trade labels.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..storage import Database
from ..quote import QuoteService


@dataclass
class FullAnalysisResult:
    """Raw price-and-volume observations for discretionary analysis."""

    code: str
    name: Optional[str] = None

    # Latest and previous daily bars.  The historical series is intentionally
    # left uninterpreted for the desk's market-structure roles.
    indicators: dict[str, Any] = field(default_factory=dict)
    prev_indicators: dict[str, Any] = field(default_factory=dict)

    # Quote data
    quote: dict[str, Any] = field(default_factory=dict)

    # Data quality
    data_quality: dict[str, Any] = field(default_factory=dict)

    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    days: int = 100
    error: Optional[str] = None


class AnalysisService:
    """Analysis service - provides raw data and context"""

    def __init__(
        self,
        db: Database,
        quote_service: Optional[QuoteService] = None,
    ):
        self.db = db
        self._quote_service = quote_service

    @property
    def quote_service(self) -> QuoteService:
        if not self._quote_service:
            self._quote_service = QuoteService(self.db)
        return self._quote_service

    async def analyze(
        self,
        code: str,
        days: int = 100,
    ) -> FullAnalysisResult:
        """Return raw daily bars and a current quote without trade labels.

        Args:
            code: Stock code
            days: Number of days to analyze
        Returns:
            Price-and-volume observations and source-quality metadata.
        """
        try:
            # Fetch historical data
            df = await self.quote_service.get_daily(code, limit=days)

            if df.empty:
                return FullAnalysisResult(
                    code=code,
                    error="No data available",
                    days=days,
                )

            # Get latest and previous day's data
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest

            # Convert to dictionary
            latest_dict = self._series_to_dict(latest)
            prev_dict = self._series_to_dict(prev)

            # Get real-time quote
            quote = {}
            try:
                quote = await self.quote_service.get_realtime(code)
            except Exception:
                pass

            # The quote endpoint already provides the display name.  Do not issue
            # an additional stock-list request merely to populate it: some public
            # fallback clients perform that remote lookup without a timeout.
            name = quote.get("name") if quote else None

            data_quality = {
                "daily": "daily_only",
                "quote": quote.get("data_quality", "unavailable") if quote else "unavailable",
            }

            return FullAnalysisResult(
                code=code,
                name=name,
                indicators=latest_dict,
                prev_indicators=prev_dict,
                quote=quote,
                data_quality=data_quality,
                days=days,
            )

        except Exception as e:
            return FullAnalysisResult(
                code=code,
                error=str(e),
                days=days,
            )

    def _series_to_dict(self, series) -> dict[str, Any]:
        """Convert pandas Series to dict, handling NaN and special types"""
        import math
        import numpy as np
        from datetime import date, datetime

        result = {}
        for key, value in series.items():
            if isinstance(value, float):
                if math.isnan(value) or np.isinf(value):
                    result[key] = None
                else:
                    result[key] = float(value)
            elif isinstance(value, (np.integer, np.floating)):
                if np.isinf(value):
                    result[key] = None
                else:
                    result[key] = float(value) if isinstance(value, np.floating) else int(value)
            elif isinstance(value, date):
                result[key] = value.isoformat()
            elif isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, str):
                result[key] = value
            else:
                try:
                    # Attempt to convert to string
                    result[key] = str(value)
                except Exception:
                    result[key] = None
        return result

    def _clean_for_json(self, obj: Any) -> Any:
        """Clean data to make it JSON-serializable"""
        import math
        import numpy as np
        from datetime import date, datetime

        if isinstance(obj, dict):
            return {k: self._clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_for_json(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        elif isinstance(obj, (np.integer, np.floating)):
            if np.isinf(obj):
                return None
            return float(obj) if isinstance(obj, np.floating) else int(obj)
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        else:
            return obj

    def to_dict(self, result: FullAnalysisResult) -> dict[str, Any]:
        """Convert to serializable dictionary"""
        raw = {
            "code": result.code,
            "name": result.name,
            "indicators": result.indicators,
            "prev_indicators": result.prev_indicators,
            "quote": result.quote,
            "data_quality": result.data_quality,
            "analyzed_at": result.analyzed_at.isoformat(),
            "days": result.days,
            "error": result.error,
        }
        return self._clean_for_json(raw)
