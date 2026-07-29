"""Tests for training-only rolling parameter selection."""

import pandas as pd
import pytest

from astock.backtest.model_validation import run_rolling_model_selection


@pytest.fixture
def daily_bars() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=100, freq="B")
    close = [10 + index * 0.04 + ((index % 9) - 4) * 0.15 for index in range(len(dates))]
    return pd.DataFrame(
        {
            "date": dates,
            "open": [value * 1.001 for value in close],
            "high": [value * 1.01 for value in close],
            "low": [value * 0.99 for value in close],
            "close": close,
            "volume": [1_000_000] * len(dates),
        }
    )


def test_rolling_selection_records_all_training_candidates_and_disjoint_test_windows(
    daily_bars: pd.DataFrame,
) -> None:
    result = run_rolling_model_selection(
        daily_bars,
        "ma_cross",
        candidate_parameter_sets=[
            {"short_period": 3, "long_period": 8},
            {"short_period": 5, "long_period": 15},
        ],
        train_bars=40,
        test_bars=20,
    )

    payload = result.to_dict()
    assert payload["schema_version"] == "rolling_model_selection.v1"
    assert payload["fold_count"] == 3
    assert payload["candidate_set_fingerprint"].startswith("sha256:")
    assert payload["strategy_implementation_fingerprint"].startswith("sha256:")
    assert payload["execution_engine_fingerprint"].startswith("sha256:")
    assert payload["research_only"] is True
    assert payload["formal_decision_eligible"] is False
    assert len(payload["candidate_parameter_sets"]) == 2
    for fold in payload["folds"]:
        assert fold["training_end"] < fold["testing_start"]
        assert len(fold["candidate_training_results"]) == 2
        assert fold["selected_parameters"] in payload["candidate_parameter_sets"]
        assert fold["out_of_sample_result"]["start_date"] == fold["testing_start"]


def test_rolling_selection_rejects_duplicate_or_invalid_search_space(
    daily_bars: pd.DataFrame,
) -> None:
    with pytest.raises(ValueError, match="duplicate"):
        run_rolling_model_selection(
            daily_bars,
            "ma_cross",
            candidate_parameter_sets=[{}, {}],
            train_bars=40,
            test_bars=20,
        )
    with pytest.raises(ValueError, match="selection_metric"):
        run_rolling_model_selection(
            daily_bars,
            "ma_cross",
            candidate_parameter_sets=[{}],
            train_bars=40,
            test_bars=20,
            selection_metric="best-looking-result",
        )


def test_rolling_selection_carries_execution_cost_assumptions_to_each_fold(
    daily_bars: pd.DataFrame,
) -> None:
    result = run_rolling_model_selection(
        daily_bars,
        "ma_cross",
        candidate_parameter_sets=[{"short_period": 3, "long_period": 8}],
        train_bars=40,
        test_bars=20,
        transfer_fee_rate=0.00001,
    )

    assert all(
        fold.out_of_sample_result.execution_assumptions.transfer_fee_rate == 0.00001
        for fold in result.folds
    )
