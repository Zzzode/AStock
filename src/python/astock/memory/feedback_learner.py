"""Feedback learner

Learns from user feedback to adjust analysis weights and confidence levels.
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

TEAM_FEEDBACK_FILE = Path("data/team-feedback.json")
LEGACY_FEEDBACK_FILE = Path("data/feedback.json")


def clamp(value: float, min_value: float, max_value: float) -> float:
    """Clamp value to a given range"""
    return min(max_value, max(min_value, value))


@dataclass
class FeedbackRecord:
    """Feedback record"""

    code: str                               # Stock code
    action: str                             # Suggested action
    outcome: str                            # Feedback result: good/bad
    strategy: Optional[str] = None          # Associated strategy/factor
    note: Optional[str] = None              # Additional notes
    signals: Optional[list[str]] = None     # Associated signals
    confidence: Optional[float] = None      # Confidence at the time
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyPerformance:
    """Strategy performance"""

    strategy: str
    total_count: int = 0
    good_count: int = 0
    bad_count: int = 0
    success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def update(self, outcome: str) -> None:
        """Update statistics"""
        self.total_count += 1
        if outcome == "good":
            self.good_count += 1
        else:
            self.bad_count += 1
        self.success_rate = self.good_count / self.total_count if self.total_count > 0 else 0
        self.last_updated = datetime.now()


@dataclass
class SignalPerformance:
    """Signal performance"""

    signal_type: str
    total_count: int = 0
    good_count: int = 0
    bad_count: int = 0
    success_rate: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)

    def update(self, outcome: str) -> None:
        """Update statistics"""
        self.total_count += 1
        if outcome == "good":
            self.good_count += 1
        else:
            self.bad_count += 1
        self.success_rate = self.good_count / self.total_count if self.total_count > 0 else 0
        self.last_updated = datetime.now()


class FeedbackLearner:
    """Learn from user feedback"""

    def __init__(self, data_path: Optional[Path] = None):
        """Initialize feedback learner

        Args:
            data_path: Data storage path, defaults to data/team-feedback.json
        """
        self.data_path = data_path or TEAM_FEEDBACK_FILE
        self._records: list[FeedbackRecord] = []
        self._strategy_performance: dict[str, StrategyPerformance] = {}
        self._signal_performance: dict[str, SignalPerformance] = {}
        self._loaded = False

    def _get_load_path(self) -> Path:
        """Get actual load path, compatible with legacy feedback.json"""
        if self.data_path.exists():
            return self.data_path

        if self.data_path == TEAM_FEEDBACK_FILE and LEGACY_FEEDBACK_FILE.exists():
            return LEGACY_FEEDBACK_FILE

        return self.data_path

    def _ensure_loaded(self) -> None:
        """Ensure data is loaded"""
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        """Load data from file"""
        load_path = self._get_load_path()
        if not load_path.exists():
            return

        try:
            with open(load_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Load records
            for record_data in data.get("records", []):
                record = FeedbackRecord(
                    code=record_data["code"],
                    action=record_data["action"],
                    outcome=record_data["outcome"],
                    strategy=record_data.get("strategy"),
                    note=record_data.get("note"),
                    signals=record_data.get("signals"),
                    confidence=record_data.get("confidence"),
                    created_at=datetime.fromisoformat(record_data["created_at"])
                    if record_data.get("created_at") else datetime.now(),
                )
                self._records.append(record)

            # Load strategy performance
            for strategy, perf_data in data.get("strategy_performance", {}).items():
                self._strategy_performance[strategy] = StrategyPerformance(
                    strategy=strategy,
                    total_count=perf_data.get("total_count", 0),
                    good_count=perf_data.get("good_count", 0),
                    bad_count=perf_data.get("bad_count", 0),
                    success_rate=perf_data.get("success_rate", 0),
                    last_updated=datetime.fromisoformat(perf_data["last_updated"])
                    if perf_data.get("last_updated") else datetime.now(),
                )

            # Load signal performance
            for signal, perf_data in data.get("signal_performance", {}).items():
                self._signal_performance[signal] = SignalPerformance(
                    signal_type=signal,
                    total_count=perf_data.get("total_count", 0),
                    good_count=perf_data.get("good_count", 0),
                    bad_count=perf_data.get("bad_count", 0),
                    success_rate=perf_data.get("success_rate", 0),
                    last_updated=datetime.fromisoformat(perf_data["last_updated"])
                    if perf_data.get("last_updated") else datetime.now(),
                )

        except Exception:
            pass

    def _save(self) -> None:
        """Save data to file"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "records": [
                {
                    "code": r.code,
                    "action": r.action,
                    "outcome": r.outcome,
                    "strategy": r.strategy,
                    "note": r.note,
                    "signals": r.signals,
                    "confidence": r.confidence,
                    "created_at": r.created_at.isoformat(),
                }
                for r in self._records
            ],
            "strategy_performance": {
                s: {
                    "total_count": p.total_count,
                    "good_count": p.good_count,
                    "bad_count": p.bad_count,
                    "success_rate": p.success_rate,
                    "last_updated": p.last_updated.isoformat(),
                }
                for s, p in self._strategy_performance.items()
            },
            "signal_performance": {
                s: {
                    "total_count": p.total_count,
                    "good_count": p.good_count,
                    "bad_count": p.bad_count,
                    "success_rate": p.success_rate,
                    "last_updated": p.last_updated.isoformat(),
                }
                for s, p in self._signal_performance.items()
            },
        }

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    async def record_feedback(
        self,
        code: str,
        action: str,
        outcome: str,
        strategy: Optional[str] = None,
        note: Optional[str] = None,
        signals: Optional[list[str]] = None,
        confidence: Optional[float] = None,
    ) -> FeedbackRecord:
        """Record feedback

        Args:
            code: Stock code
            action: Suggested action
            outcome: Feedback result
            strategy: Associated strategy
            note: Additional notes
            signals: Associated signals
            confidence: Confidence at the time

        Returns:
            Feedback record
        """
        self._ensure_loaded()

        record = FeedbackRecord(
            code=code,
            action=action,
            outcome=outcome,
            strategy=strategy,
            note=note,
            signals=signals,
            confidence=confidence,
        )

        self._records.append(record)

        # Update strategy performance
        if strategy:
            if strategy not in self._strategy_performance:
                self._strategy_performance[strategy] = StrategyPerformance(strategy=strategy)
            self._strategy_performance[strategy].update(outcome)

        # Update signal performance
        if signals:
            for signal in signals:
                if signal not in self._signal_performance:
                    self._signal_performance[signal] = SignalPerformance(signal_type=signal)
                self._signal_performance[signal].update(outcome)

        self._save()
        return record

    async def get_strategy_weights(self, user_id: str = "default") -> dict[str, float]:
        """Get strategy weights

        Calculate strategy weights based on historical feedback to adjust analysis confidence.

        Args:
            user_id: User ID

        Returns:
            Strategy weights dictionary
        """
        self._ensure_loaded()

        weights = {}
        for strategy, perf in self._strategy_performance.items():
            if perf.total_count >= 3:  # Require at least 3 feedback records to calculate weight
                # Weight based on success rate, range 0.5-1.5
                base_weight = 1.0
                adjustment = (perf.success_rate - 0.5) * 0.5  # -0.25 to +0.25
                weights[strategy] = base_weight + adjustment
            else:
                weights[strategy] = 1.0

        return weights

    async def get_team_feedback_profile(self, code: str) -> dict[str, Any]:
        """Get team feedback profile for a single stock"""
        self._ensure_loaded()

        records = [record for record in self._records if record.code == code]
        if not records:
            return {
                "sample_count": 0,
                "aggressiveness": 0.0,
                "caution": 0.0,
            }

        positive_buy = sum(
            1
            for record in records
            if record.action == "watch_buy" and record.outcome == "good"
        )
        negative_buy = sum(
            1
            for record in records
            if record.action == "watch_buy" and record.outcome == "bad"
        )
        positive_reduce = sum(
            1
            for record in records
            if record.action == "hold_or_reduce" and record.outcome == "good"
        )
        negative_reduce = sum(
            1
            for record in records
            if record.action == "hold_or_reduce" and record.outcome == "bad"
        )

        total = len(records)
        buy_signal = (positive_buy - negative_buy) / total if total > 0 else 0.0
        reduce_signal = (positive_reduce - negative_reduce) / total if total > 0 else 0.0

        return {
            "sample_count": total,
            "aggressiveness": clamp(buy_signal, -1.0, 1.0),
            "caution": clamp(reduce_signal, -1.0, 1.0),
        }

    async def get_global_profile(self, user_id: str = "default") -> dict[str, Any]:
        """Get global team feedback profile"""
        self._ensure_loaded()

        records = self._records
        if not records:
            return {
                "sample_count": 0,
                "risk_appetite": 0.0,
                "strategy_weights": {},
            }

        risk_signal = 0
        strategy_score: dict[str, int] = {}
        strategy_count: dict[str, int] = {}

        for record in records:
            if record.action == "watch_buy":
                risk_signal += 1 if record.outcome == "good" else -1
            elif record.action == "hold_or_reduce":
                risk_signal += -1 if record.outcome == "good" else 1

            if record.strategy and record.strategy.strip():
                strategy_score[record.strategy] = strategy_score.get(record.strategy, 0) + (
                    1 if record.outcome == "good" else -1
                )
                strategy_count[record.strategy] = strategy_count.get(record.strategy, 0) + 1

        strategy_weights: dict[str, float] = {}
        for strategy, score in strategy_score.items():
            count = strategy_count.get(strategy, 1)
            strategy_weights[strategy] = clamp(score / count, -1.0, 1.0)

        return {
            "sample_count": len(records),
            "risk_appetite": clamp(risk_signal / len(records), -1.0, 1.0),
            "strategy_weights": strategy_weights,
        }

    async def get_signal_accuracy(self, signal_type: str) -> Optional[float]:
        """Get signal accuracy

        Args:
            signal_type: Signal type

        Returns:
            Accuracy rate, or None if no data available
        """
        self._ensure_loaded()

        perf = self._signal_performance.get(signal_type)
        if perf and perf.total_count > 0:
            return perf.success_rate
        return None

    async def adjust_confidence(
        self,
        base_confidence: float,
        signals: list[str],
        strategy: Optional[str] = None,
    ) -> float:
        """Adjust confidence

        Adjust confidence based on historical feedback.

        Args:
            base_confidence: Base confidence
            signals: Signal list
            strategy: Strategy name

        Returns:
            Adjusted confidence
        """
        self._ensure_loaded()

        adjustment = 0.0

        # Adjust based on signal accuracy
        for signal in signals:
            accuracy = await self.get_signal_accuracy(signal)
            if accuracy is not None:
                # Accuracy above 50% increases confidence, below decreases
                adjustment += (accuracy - 0.5) * 0.1

        # Adjust based on strategy success rate
        if strategy:
            weights = await self.get_strategy_weights()
            strategy_weight = weights.get(strategy, 1.0)
            adjustment += (strategy_weight - 1.0) * 0.1

        # Apply adjustment, clamp to 0-1 range
        adjusted = base_confidence + adjustment
        return max(0.0, min(1.0, adjusted))

    async def get_feedback_summary(self, user_id: str = "default") -> dict[str, Any]:
        """Get feedback summary

        Args:
            user_id: User ID

        Returns:
            Feedback summary
        """
        self._ensure_loaded()

        total = len(self._records)
        if total == 0:
            return {
                "total": 0,
                "success_rate": None,
                "strategy_performance": {},
                "signal_performance": {},
            }

        good_count = sum(1 for r in self._records if r.outcome == "good")
        success_rate = good_count / total

        return {
            "total": total,
            "success_rate": round(success_rate, 2),
            "good_count": good_count,
            "bad_count": total - good_count,
            "strategy_performance": {
                s: {
                    "success_rate": round(p.success_rate, 2),
                    "total_count": p.total_count,
                }
                for s, p in self._strategy_performance.items()
                if p.total_count > 0
            },
            "signal_performance": {
                s: {
                    "success_rate": round(p.success_rate, 2),
                    "total_count": p.total_count,
                }
                for s, p in self._signal_performance.items()
                if p.total_count > 0
            },
        }
