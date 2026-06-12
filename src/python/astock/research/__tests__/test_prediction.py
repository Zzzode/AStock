"""Tests for prediction ledger and verification."""

import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from astock.research.prediction import (
    PredictionDirection,
    PredictionLedger,
    PredictionOutcome,
    PricePrediction,
    VerificationResult,
    verify_prediction,
)


@pytest.fixture
def tmp_ledger(tmp_path):
    return PredictionLedger(tmp_path / "predictions.json")


def test_create_and_list(tmp_ledger):
    pred = PricePrediction(
        code="000001",
        direction=PredictionDirection.BULLISH,
        entry_price=12.0,
        target_price=14.0,
        stop_loss=11.0,
        horizon_days=30,
    )
    tmp_ledger.create(pred)
    items = tmp_ledger.list_all()
    assert len(items) == 1
    assert items[0]["code"] == "000001"
    assert items[0]["direction"] == "bullish"


def test_list_pending(tmp_ledger):
    past = PricePrediction(
        code="000001",
        direction=PredictionDirection.BULLISH,
        entry_price=10.0,
        horizon_days=1,
        created_at=datetime.now() - timedelta(days=5),
    )
    future = PricePrediction(
        code="000002",
        direction=PredictionDirection.BEARISH,
        entry_price=20.0,
        horizon_days=60,
    )
    tmp_ledger.create(past)
    tmp_ledger.create(future)

    pending = tmp_ledger.list_pending()
    assert len(pending) == 1
    assert pending[0].code == "000001"


def test_verify_bullish_correct():
    pred = PricePrediction(
        code="000001",
        direction=PredictionDirection.BULLISH,
        entry_price=10.0,
        target_price=12.0,
    )
    price_series = [
        {"date": "2024-01-01", "close": 10.5, "high": 10.8, "low": 10.0},
        {"date": "2024-01-02", "close": 11.5, "high": 12.0, "low": 11.0},
        {"date": "2024-01-03", "close": 12.5, "high": 12.5, "low": 11.8},
    ]
    result = verify_prediction(pred, price_series)
    assert result.outcome == PredictionOutcome.CORRECT
    assert result.hit_target is True


def test_verify_bullish_incorrect():
    pred = PricePrediction(
        code="000001",
        direction=PredictionDirection.BULLISH,
        entry_price=10.0,
        stop_loss=9.0,
    )
    price_series = [
        {"date": "2024-01-01", "close": 9.5, "high": 10.0, "low": 8.5},
    ]
    result = verify_prediction(pred, price_series)
    assert result.outcome == PredictionOutcome.INCORRECT
    assert result.hit_stop is True


def test_verify_bearish_correct():
    pred = PricePrediction(
        code="000001",
        direction=PredictionDirection.BEARISH,
        entry_price=20.0,
        target_price=17.0,
    )
    price_series = [
        {"date": "2024-01-01", "close": 19.0, "high": 20.0, "low": 18.5},
        {"date": "2024-01-02", "close": 17.5, "high": 18.0, "low": 16.5},
    ]
    result = verify_prediction(pred, price_series)
    assert result.outcome == PredictionOutcome.CORRECT
    assert result.hit_target is True


def test_accuracy_stats(tmp_ledger):
    pred = PricePrediction(
        code="000001",
        direction=PredictionDirection.BULLISH,
        entry_price=10.0,
    )
    tmp_ledger.create(pred)
    tmp_ledger.record_verification(VerificationResult(
        prediction_id=pred.prediction_id or "",
        outcome=PredictionOutcome.CORRECT,
        actual_price=11.0,
        price_change_pct=10.0,
    ))
    stats = tmp_ledger.get_accuracy_stats()
    assert stats["total_verified"] == 1
    assert stats["correct"] == 1
    assert stats["accuracy"] == 1.0


def test_empty_price_series():
    pred = PricePrediction(
        code="000001",
        direction=PredictionDirection.BULLISH,
        entry_price=10.0,
    )
    result = verify_prediction(pred, [])
    assert result.outcome == PredictionOutcome.EXPIRED
