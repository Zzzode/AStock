"""Prediction ledger with auto-verification trigger.

Extends the research ledger by storing structured predictions (direction,
target price, time horizon) and providing a verification engine that
compares predictions against actual market outcomes.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Optional


class PredictionDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class PredictionOutcome(StrEnum):
    PENDING = "pending"
    CORRECT = "correct"
    PARTIALLY_CORRECT = "partially_correct"
    INCORRECT = "incorrect"
    EXPIRED = "expired"


@dataclass
class PricePrediction:
    """A single structured price/direction prediction."""

    code: str
    direction: PredictionDirection
    entry_price: float
    target_price: Optional[float] = None
    stop_loss: Optional[float] = None
    horizon_days: int = 30
    confidence: float = 0.5
    thesis_summary: str = ""
    research_entry_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[date] = None
    prediction_id: Optional[str] = None

    def __post_init__(self) -> None:
        if self.deadline is None:
            self.deadline = (self.created_at + timedelta(days=self.horizon_days)).date()
        if self.prediction_id is None:
            self.prediction_id = _make_prediction_id(self)

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "code": self.code,
            "direction": self.direction.value,
            "entry_price": self.entry_price,
            "target_price": self.target_price,
            "stop_loss": self.stop_loss,
            "horizon_days": self.horizon_days,
            "confidence": self.confidence,
            "thesis_summary": self.thesis_summary,
            "research_entry_id": self.research_entry_id,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "deadline": self.deadline.isoformat() if self.deadline else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PricePrediction":
        deadline_raw = data.get("deadline")
        deadline = date.fromisoformat(deadline_raw) if deadline_raw else None
        return cls(
            prediction_id=data.get("prediction_id"),
            code=str(data["code"]),
            direction=PredictionDirection(data["direction"]),
            entry_price=float(data["entry_price"]),
            target_price=data.get("target_price"),
            stop_loss=data.get("stop_loss"),
            horizon_days=int(data.get("horizon_days", 30)),
            confidence=float(data.get("confidence", 0.5)),
            thesis_summary=str(data.get("thesis_summary", "")),
            research_entry_id=data.get("research_entry_id"),
            tags=list(data.get("tags", [])),
            created_at=datetime.fromisoformat(data["created_at"]),
            deadline=deadline,
        )


@dataclass
class VerificationResult:
    """Outcome of checking a prediction against actual price data."""

    prediction_id: str
    outcome: PredictionOutcome
    actual_price: float
    price_change_pct: float
    max_favorable: float = 0.0
    max_adverse: float = 0.0
    hit_target: bool = False
    hit_stop: bool = False
    days_held: int = 0
    verified_at: datetime = field(default_factory=datetime.now)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "prediction_id": self.prediction_id,
            "outcome": self.outcome.value,
            "actual_price": self.actual_price,
            "price_change_pct": self.price_change_pct,
            "max_favorable": self.max_favorable,
            "max_adverse": self.max_adverse,
            "hit_target": self.hit_target,
            "hit_stop": self.hit_stop,
            "days_held": self.days_held,
            "verified_at": self.verified_at.isoformat(),
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VerificationResult":
        return cls(
            prediction_id=str(data["prediction_id"]),
            outcome=PredictionOutcome(data["outcome"]),
            actual_price=float(data["actual_price"]),
            price_change_pct=float(data["price_change_pct"]),
            max_favorable=float(data.get("max_favorable", 0)),
            max_adverse=float(data.get("max_adverse", 0)),
            hit_target=bool(data.get("hit_target", False)),
            hit_stop=bool(data.get("hit_stop", False)),
            days_held=int(data.get("days_held", 0)),
            verified_at=datetime.fromisoformat(data["verified_at"]),
            notes=str(data.get("notes", "")),
        )


class PredictionLedger:
    """JSON-backed prediction storage with verification lifecycle."""

    def __init__(self, data_path: Optional[Path] = None):
        self.data_path = data_path or Path("data/prediction-ledger.json")
        self._predictions: dict[str, PricePrediction] = {}
        self._verifications: dict[str, VerificationResult] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        if not self.data_path.exists():
            self._predictions = {}
            self._verifications = {}
            return
        try:
            raw = json.loads(self.data_path.read_text(encoding="utf-8"))
            self._predictions = {
                str(item["prediction_id"]): PricePrediction.from_dict(item)
                for item in raw.get("predictions", [])
            }
            self._verifications = {
                str(item["prediction_id"]): VerificationResult.from_dict(item)
                for item in raw.get("verifications", [])
            }
        except Exception:
            self._predictions = {}
            self._verifications = {}

    def _save(self) -> None:
        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": "prediction-ledger.v1",
            "updated_at": datetime.now().isoformat(),
            "predictions": [
                p.to_dict()
                for p in sorted(
                    self._predictions.values(),
                    key=lambda x: x.created_at,
                    reverse=True,
                )
            ],
            "verifications": [
                v.to_dict()
                for v in sorted(
                    self._verifications.values(),
                    key=lambda x: x.verified_at,
                    reverse=True,
                )
            ],
        }
        self.data_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def create(self, prediction: PricePrediction) -> PricePrediction:
        self._ensure_loaded()
        if prediction.prediction_id is None:
            raise ValueError("Prediction must have an ID")
        self._predictions[prediction.prediction_id] = prediction
        self._save()
        return prediction

    def get(self, prediction_id: str) -> Optional[PricePrediction]:
        self._ensure_loaded()
        return self._predictions.get(prediction_id)

    def list_pending(self, *, before_date: Optional[date] = None) -> list[PricePrediction]:
        """List predictions due for verification."""
        self._ensure_loaded()
        today = before_date or date.today()
        results = []
        for p in self._predictions.values():
            if p.prediction_id in self._verifications:
                continue
            if p.deadline and p.deadline <= today:
                results.append(p)
        results.sort(key=lambda x: x.deadline or date.max)
        return results

    def list_all(
        self,
        *,
        code: Optional[str] = None,
        outcome: Optional[PredictionOutcome] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """List predictions with verification status."""
        self._ensure_loaded()
        items = []
        for p in self._predictions.values():
            if code and p.code != code:
                continue
            verification = self._verifications.get(p.prediction_id or "")
            if outcome and (
                not verification or verification.outcome != outcome
            ):
                continue
            record = p.to_dict()
            record["verification"] = verification.to_dict() if verification else None
            items.append(record)
        items.sort(key=lambda x: x["created_at"], reverse=True)
        return items[:limit]

    def record_verification(self, result: VerificationResult) -> None:
        self._ensure_loaded()
        self._verifications[result.prediction_id] = result
        self._save()

    def get_accuracy_stats(
        self, *, code: Optional[str] = None
    ) -> dict[str, Any]:
        """Compute accuracy statistics."""
        self._ensure_loaded()
        total = 0
        correct = 0
        partial = 0
        incorrect = 0
        expired = 0
        pending = 0

        for p in self._predictions.values():
            if code and p.code != code:
                continue
            v = self._verifications.get(p.prediction_id or "")
            if v is None:
                pending += 1
                continue
            total += 1
            if v.outcome == PredictionOutcome.CORRECT:
                correct += 1
            elif v.outcome == PredictionOutcome.PARTIALLY_CORRECT:
                partial += 1
            elif v.outcome == PredictionOutcome.INCORRECT:
                incorrect += 1
            elif v.outcome == PredictionOutcome.EXPIRED:
                expired += 1

        accuracy = correct / total if total > 0 else 0.0
        return {
            "total_verified": total,
            "pending": pending,
            "correct": correct,
            "partially_correct": partial,
            "incorrect": incorrect,
            "expired": expired,
            "accuracy": round(accuracy, 4),
            "hit_rate": round((correct + partial) / total, 4) if total > 0 else 0.0,
        }


def verify_prediction(
    prediction: PricePrediction,
    price_series: list[dict[str, Any]],
) -> VerificationResult:
    """Verify a prediction against actual price data.

    Args:
        prediction: The original prediction
        price_series: List of {"date": "YYYY-MM-DD", "close": float, "high": float, "low": float}
                      covering the period from prediction.created_at to deadline.
    """
    if not price_series:
        return VerificationResult(
            prediction_id=prediction.prediction_id or "",
            outcome=PredictionOutcome.EXPIRED,
            actual_price=prediction.entry_price,
            price_change_pct=0.0,
            notes="No price data available for verification",
        )

    entry = prediction.entry_price
    latest = price_series[-1]
    actual_price = float(latest["close"])
    change_pct = (actual_price - entry) / entry * 100 if entry > 0 else 0.0

    max_high = max(float(bar.get("high", bar["close"])) for bar in price_series)
    min_low = min(float(bar.get("low", bar["close"])) for bar in price_series)

    if prediction.direction == PredictionDirection.BULLISH:
        max_favorable = (max_high - entry) / entry * 100 if entry > 0 else 0.0
        max_adverse = (entry - min_low) / entry * 100 if entry > 0 else 0.0
    elif prediction.direction == PredictionDirection.BEARISH:
        max_favorable = (entry - min_low) / entry * 100 if entry > 0 else 0.0
        max_adverse = (max_high - entry) / entry * 100 if entry > 0 else 0.0
    else:
        max_favorable = 0.0
        max_adverse = max(abs(change_pct), 0.0)

    hit_target = False
    if prediction.target_price and prediction.direction == PredictionDirection.BULLISH:
        hit_target = max_high >= prediction.target_price
    elif prediction.target_price and prediction.direction == PredictionDirection.BEARISH:
        hit_target = min_low <= prediction.target_price

    hit_stop = False
    if prediction.stop_loss and prediction.direction == PredictionDirection.BULLISH:
        hit_stop = min_low <= prediction.stop_loss
    elif prediction.stop_loss and prediction.direction == PredictionDirection.BEARISH:
        hit_stop = max_high >= prediction.stop_loss

    outcome = _classify_outcome(prediction, change_pct, hit_target, hit_stop)
    days_held = len(price_series)

    return VerificationResult(
        prediction_id=prediction.prediction_id or "",
        outcome=outcome,
        actual_price=actual_price,
        price_change_pct=round(change_pct, 4),
        max_favorable=round(max_favorable, 4),
        max_adverse=round(max_adverse, 4),
        hit_target=hit_target,
        hit_stop=hit_stop,
        days_held=days_held,
    )


def _classify_outcome(
    prediction: PricePrediction,
    change_pct: float,
    hit_target: bool,
    hit_stop: bool,
) -> PredictionOutcome:
    if hit_target:
        return PredictionOutcome.CORRECT
    if hit_stop:
        return PredictionOutcome.INCORRECT

    if prediction.direction == PredictionDirection.BULLISH:
        if change_pct >= 5.0:
            return PredictionOutcome.CORRECT
        elif change_pct >= 0:
            return PredictionOutcome.PARTIALLY_CORRECT
        else:
            return PredictionOutcome.INCORRECT
    elif prediction.direction == PredictionDirection.BEARISH:
        if change_pct <= -5.0:
            return PredictionOutcome.CORRECT
        elif change_pct <= 0:
            return PredictionOutcome.PARTIALLY_CORRECT
        else:
            return PredictionOutcome.INCORRECT
    else:
        if abs(change_pct) <= 3.0:
            return PredictionOutcome.CORRECT
        else:
            return PredictionOutcome.PARTIALLY_CORRECT


def _make_prediction_id(prediction: PricePrediction) -> str:
    seed = f"{prediction.code}|{prediction.direction.value}|{prediction.entry_price}|{prediction.created_at.isoformat()}"
    digest = hashlib.sha1(seed.encode("utf-8")).hexdigest()[:12]
    return f"pred-{prediction.created_at.strftime('%Y%m%d')}-{digest}"
