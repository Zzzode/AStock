"""Analysis service

Provides raw technical indicator data and context information without any interpretation.
Interpretation is performed by the LLM via dynamic reasoning.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..storage import Database
from ..quote import QuoteService
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.interpretation import detect_signals, calculate_statistics
from ..memory import MemoryStore, FeedbackLearner


@dataclass
class FullAnalysisResult:
    """Full analysis result - raw data + context"""

    code: str
    name: Optional[str] = None

    # Raw indicator data
    indicators: dict[str, Any] = field(default_factory=dict)

    # Previous day's indicators (for comparison)
    prev_indicators: dict[str, Any] = field(default_factory=dict)

    # Detected signals (type and values only, no interpretation)
    signals: list[dict[str, Any]] = field(default_factory=list)

    # Signal statistics
    signal_stats: dict[str, Any] = field(default_factory=dict)

    # Historical context
    history: dict[str, Any] = field(default_factory=dict)

    # User feedback statistics
    feedback_stats: dict[str, Any] = field(default_factory=dict)

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
        memory_store: Optional[MemoryStore] = None,
        feedback_learner: Optional[FeedbackLearner] = None,
    ):
        self.db = db
        self._quote_service = quote_service
        self._memory_store = memory_store
        self._feedback_learner = feedback_learner

    @property
    def quote_service(self) -> QuoteService:
        if not self._quote_service:
            self._quote_service = QuoteService(self.db)
        return self._quote_service

    @property
    def memory_store(self) -> MemoryStore:
        if not self._memory_store:
            self._memory_store = MemoryStore()
        return self._memory_store

    @property
    def feedback_learner(self) -> FeedbackLearner:
        if not self._feedback_learner:
            self._feedback_learner = FeedbackLearner()
        return self._feedback_learner

    async def analyze(
        self,
        code: str,
        days: int = 100,
        include_context: bool = True,
    ) -> FullAnalysisResult:
        """Perform technical analysis, output raw data + context

        Args:
            code: Stock code
            days: Number of days to analyze
            include_context: Whether to include historical and feedback context

        Returns:
            Raw data + context
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

            # Calculate technical indicators
            analyzer = TechnicalAnalyzer(df)
            analyzer.add_all()
            df_with_indicators = analyzer.df

            # Get latest and previous day's data
            latest = df_with_indicators.iloc[-1]
            prev = df_with_indicators.iloc[-2] if len(df_with_indicators) > 1 else latest

            # Convert to dictionary
            latest_dict = self._series_to_dict(latest)
            prev_dict = self._series_to_dict(prev)

            # Detect signals
            signals = detect_signals(latest_dict, prev_dict)

            # Calculate signal statistics
            signal_stats = calculate_statistics(signals)

            # Get stock name
            name = None
            try:
                stock_info = await self.quote_service.get_stock_info(code)
                name = stock_info.get("name") if stock_info else None
            except Exception:
                pass

            # Get real-time quote
            quote = {}
            try:
                quote = await self.quote_service.get_realtime(code)
            except Exception:
                pass

            data_quality = {
                "daily": "daily_only",
                "quote": quote.get("data_quality", "unavailable") if quote else "unavailable",
            }

            # Get context
            history = {}
            feedback_stats = {}

            if include_context:
                # Get historical analysis records
                try:
                    history_entries = await self.memory_store.recall(
                        agent_name="technical-analyst",
                        user_id="default",
                        key=f"analysis:{code}",
                        limit=5,
                    )
                    if history_entries:
                        history["recent_analyses"] = [
                            {
                                "date": e.get("created_at", "")[:10],
                                "signals": e.get("value", {}).get("signals", []),
                            }
                            for e in history_entries
                        ]
                except Exception:
                    pass

                # Get signal feedback statistics
                try:
                    feedback_summary = await self.feedback_learner.get_feedback_summary()
                    if feedback_summary.get("total", 0) > 0:
                        feedback_stats["overall"] = {
                            "total": feedback_summary.get("total"),
                            "success_rate": feedback_summary.get("success_rate"),
                        }

                    # Success rate per signal type
                    signal_perf = feedback_summary.get("signal_performance", {})
                    if signal_perf:
                        feedback_stats["signals"] = signal_perf
                except Exception:
                    pass

            # Store this analysis
            try:
                await self.memory_store.store(
                    agent_name="technical-analyst",
                    session_id=datetime.now().strftime("%Y%m%d"),
                    user_id="default",
                    key=f"analysis:{code}",
                    value={
                        "signals": [s["type"] for s in signals],
                        "signal_stats": signal_stats,
                        "indicators": latest_dict,
                    },
                )
            except Exception:
                pass

            return FullAnalysisResult(
                code=code,
                name=name,
                indicators=latest_dict,
                prev_indicators=prev_dict,
                signals=signals,
                signal_stats=signal_stats,
                history=history,
                feedback_stats=feedback_stats,
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
            "signals": result.signals,
            "signal_stats": result.signal_stats,
            "history": result.history,
            "feedback_stats": result.feedback_stats,
            "quote": result.quote,
            "data_quality": result.data_quality,
            "analyzed_at": result.analyzed_at.isoformat(),
            "days": result.days,
            "error": result.error,
        }
        return self._clean_for_json(raw)
