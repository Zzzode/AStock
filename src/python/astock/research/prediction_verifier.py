"""Auto-verification trigger for the prediction ledger.

Scans pending predictions whose deadline has passed, fetches actual price
data, runs verification, and records results. Designed to be called by
a cron job, the monitor service, or an agent skill.
"""

from __future__ import annotations

import asyncio
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from .prediction import (
    PredictionLedger,
    PredictionOutcome,
    PricePrediction,
    VerificationResult,
    verify_prediction,
)
from ..quote import QuoteService
from ..storage import Database
from ..research.postmortem import PostmortemRootCause, ResearchPostmortem
from ..research.ledger import ResearchLedger, ResearchObservation, ResearchStatus
from ..utils import get_logger

logger = get_logger("prediction_verifier")


async def run_verification_sweep(
    *,
    db_path: Optional[Path] = None,
    prediction_ledger_path: Optional[Path] = None,
    research_ledger_path: Optional[Path] = None,
    check_date: Optional[date] = None,
) -> dict[str, Any]:
    """Sweep all pending predictions due for verification.

    Returns a summary of what was verified.
    """
    from ..capabilities import DEFAULT_DB_PATH, DEFAULT_RESEARCH_LEDGER_PATH

    db_path = db_path or DEFAULT_DB_PATH
    prediction_path = prediction_ledger_path or Path(
        str(db_path).replace("stocks.db", "prediction-ledger.json")
    )
    research_path = research_ledger_path or DEFAULT_RESEARCH_LEDGER_PATH
    today = check_date or date.today()

    ledger = PredictionLedger(prediction_path)
    pending = ledger.list_pending(before_date=today)

    if not pending:
        return {
            "status": "ok",
            "checked_at": datetime.now().isoformat(),
            "pending_count": 0,
            "verified": [],
            "errors": [],
        }

    db = Database(str(db_path))
    await db.connect()
    try:
        quote_service = QuoteService(db)
        verified: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []

        for prediction in pending:
            try:
                result = await _verify_single(prediction, quote_service, today)
                ledger.record_verification(result)
                verified.append(result.to_dict())

                if prediction.research_entry_id:
                    _update_research_entry(
                        research_path, prediction, result
                    )
            except Exception as e:
                logger.warning(
                    f"Failed to verify {prediction.prediction_id}: {e}"
                )
                errors.append({
                    "prediction_id": prediction.prediction_id,
                    "error": str(e),
                })

        return {
            "status": "ok",
            "checked_at": datetime.now().isoformat(),
            "pending_count": len(pending),
            "verified_count": len(verified),
            "error_count": len(errors),
            "verified": verified,
            "errors": errors,
        }
    finally:
        await db.close()


async def _verify_single(
    prediction: PricePrediction,
    quote_service: QuoteService,
    today: date,
) -> VerificationResult:
    """Fetch price data and verify one prediction."""
    start_date = prediction.created_at.date()
    end_date = min(prediction.deadline or today, today)

    quotes = await quote_service.get_daily_data(
        prediction.code,
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
    )

    price_series: list[dict[str, Any]] = []
    if isinstance(quotes, list):
        for q in quotes:
            if hasattr(q, "date"):
                price_series.append({
                    "date": str(q.date),
                    "close": float(q.close),
                    "high": float(q.high),
                    "low": float(q.low),
                })
            elif isinstance(q, dict):
                price_series.append({
                    "date": str(q.get("date", "")),
                    "close": float(q.get("close", 0)),
                    "high": float(q.get("high", q.get("close", 0))),
                    "low": float(q.get("low", q.get("close", 0))),
                })

    return verify_prediction(prediction, price_series)


def _update_research_entry(
    research_ledger_path: Path,
    prediction: PricePrediction,
    result: VerificationResult,
) -> None:
    """Attach verification observation to the linked research entry."""
    try:
        research_ledger = ResearchLedger(research_ledger_path)
        entry = research_ledger.get(prediction.research_entry_id or "")
        if entry is None:
            return

        outcome_text = (
            f"Prediction verified: {result.outcome.value} "
            f"(change={result.price_change_pct:+.2f}%, "
            f"target_hit={result.hit_target}, stop_hit={result.hit_stop})"
        )

        status_after = None
        if result.outcome == PredictionOutcome.INCORRECT and result.hit_stop:
            status_after = ResearchStatus.INVALIDATED

        observation = ResearchObservation(
            observation_type="prediction_verification",
            note=outcome_text,
            evidence={
                "prediction_id": prediction.prediction_id,
                "outcome": result.outcome.value,
                "actual_price": result.actual_price,
                "price_change_pct": result.price_change_pct,
                "days_held": result.days_held,
            },
            status_after=status_after,
        )
        research_ledger.record_observation(
            prediction.research_entry_id or "", observation
        )
    except Exception as e:
        logger.warning(f"Failed to update research entry: {e}")


def run_verification_sweep_sync(
    *,
    db_path: Optional[Path] = None,
    prediction_ledger_path: Optional[Path] = None,
    research_ledger_path: Optional[Path] = None,
    check_date: Optional[date] = None,
) -> dict[str, Any]:
    """Synchronous wrapper for run_verification_sweep."""
    return asyncio.run(
        run_verification_sweep(
            db_path=db_path,
            prediction_ledger_path=prediction_ledger_path,
            research_ledger_path=research_ledger_path,
            check_date=check_date,
        )
    )
