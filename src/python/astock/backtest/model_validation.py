"""Auditable rolling model-selection checks for research-only signal strategies.

This module intentionally separates parameter selection from the legacy
fixed-parameter walk-forward check.  Each parameter set is ranked using only
the preceding training window and then evaluated in a disjoint test window.
It is a reproducible research control, not evidence that a daily-bar signal is
tradable or ready for capital allocation.
"""

from __future__ import annotations

import json
import hashlib
import inspect
import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import pandas as pd

from .engine import BacktestEngine, BacktestResult
from .strategies import get_strategy


_MAX_PARAMETER_CANDIDATES = 64
_SELECTION_METRICS = {"total_return", "sharpe_ratio"}


@dataclass(frozen=True)
class ModelSelectionFold:
    """One fully recorded training-selection and out-of-sample evaluation."""

    fold_index: int
    training_start: str
    training_end: str
    testing_start: str
    testing_end: str
    selected_parameters: dict[str, Any]
    selection_metric: str
    candidate_training_results: list[dict[str, Any]]
    out_of_sample_result: BacktestResult

    def to_dict(self) -> dict[str, Any]:
        return {
            "fold_index": self.fold_index,
            "training_start": self.training_start,
            "training_end": self.training_end,
            "testing_start": self.testing_start,
            "testing_end": self.testing_end,
            "selected_parameters": dict(self.selected_parameters),
            "selection_metric": self.selection_metric,
            "candidate_training_results": [dict(item) for item in self.candidate_training_results],
            "out_of_sample_result": self.out_of_sample_result.to_dict(),
        }


@dataclass(frozen=True)
class RollingModelSelectionResult:
    """Result of rolling, training-only parameter selection."""

    strategy: str
    train_bars: int
    test_bars: int
    selection_metric: str
    candidate_set_fingerprint: str
    strategy_implementation_fingerprint: str
    execution_engine_fingerprint: str
    candidate_parameter_sets: list[dict[str, Any]]
    folds: list[ModelSelectionFold]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        returns = [fold.out_of_sample_result.total_return / 100.0 for fold in self.folds]
        compounded = math.prod(1.0 + value for value in returns) - 1.0 if returns else 0.0
        return {
            "schema_version": "rolling_model_selection.v1",
            "strategy": self.strategy,
            "train_bars": self.train_bars,
            "test_bars": self.test_bars,
            "selection_metric": self.selection_metric,
            "candidate_set_fingerprint": self.candidate_set_fingerprint,
            "strategy_implementation_fingerprint": self.strategy_implementation_fingerprint,
            "execution_engine_fingerprint": self.execution_engine_fingerprint,
            "candidate_parameter_sets": [dict(item) for item in self.candidate_parameter_sets],
            "fold_count": len(self.folds),
            "mean_out_of_sample_return": (
                sum(returns) / len(returns) if returns else 0.0
            ),
            "compound_out_of_sample_return": compounded,
            "positive_fold_ratio": (
                sum(value > 0 for value in returns) / len(returns) if returns else 0.0
            ),
            "folds": [fold.to_dict() for fold in self.folds],
            "warnings": list(self.warnings),
            "research_only": True,
            "no_order_execution": True,
            "formal_decision_eligible": False,
        }


def run_rolling_model_selection(
    df: pd.DataFrame,
    strategy_name: str,
    *,
    candidate_parameter_sets: Sequence[Mapping[str, Any]],
    train_bars: int,
    test_bars: int,
    selection_metric: str = "total_return",
    initial_capital: float = 100_000.0,
    commission_rate: float = 0.0003,
    stamp_duty_rate: float = 0.0005,
    transfer_fee_rate: float = 0.00001,
) -> RollingModelSelectionResult:
    """Select parameters on rolling training windows, then test them unseen.

    Training and test windows are contiguous and non-overlapping within each
    fold.  Test folds are independent paper evaluations: positions are not
    carried between them, so compounded fold returns are a diagnostic summary,
    not a continuous portfolio return.
    """
    if train_bars < 20 or test_bars < 1:
        raise ValueError("rolling model selection requires at least 20 train bars and one test bar")
    if len(df) <= train_bars:
        raise ValueError("rolling model selection data does not contain an out-of-sample bar")
    metric = str(selection_metric).strip().lower()
    if metric not in _SELECTION_METRICS:
        raise ValueError("selection_metric must be one of: " + ", ".join(sorted(_SELECTION_METRICS)))
    candidates = _normalise_candidate_parameter_sets(candidate_parameter_sets)
    candidate_set_fingerprint = "sha256:" + hashlib.sha256(
        json.dumps(candidates, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    strategy_implementation_fingerprint = _implementation_fingerprint(
        get_strategy(strategy_name).__class__
    )
    execution_engine_fingerprint = _implementation_fingerprint(BacktestEngine)
    folds: list[ModelSelectionFold] = []
    for fold_index, test_start_index in enumerate(range(train_bars, len(df), test_bars), start=1):
        test_end_index = min(test_start_index + test_bars, len(df))
        train_start_index = test_start_index - train_bars
        training_frame = df.iloc[train_start_index:test_start_index].copy()
        candidate_results = [
            _candidate_training_result(
                training_frame,
                strategy_name=strategy_name,
                parameters=parameters,
                initial_capital=initial_capital,
                selection_metric=metric,
                commission_rate=commission_rate,
                stamp_duty_rate=stamp_duty_rate,
                transfer_fee_rate=transfer_fee_rate,
            )
            for parameters in candidates
        ]
        chosen = min(candidate_results, key=lambda item: _selection_sort_key(item, metric))
        selected_parameters = dict(chosen["parameters"])
        evaluation_frame = df.iloc[train_start_index:test_end_index].copy()
        out_of_sample = BacktestEngine().run(
            evaluation_frame,
            strategy_name=strategy_name,
            initial_capital=initial_capital,
            strategy_params=selected_parameters,
            evaluation_start_index=train_bars,
            commission_rate=commission_rate,
            stamp_duty_rate=stamp_duty_rate,
            transfer_fee_rate=transfer_fee_rate,
        )
        folds.append(
            ModelSelectionFold(
                fold_index=fold_index,
                training_start=_date_text(training_frame.iloc[0]["date"]),
                training_end=_date_text(training_frame.iloc[-1]["date"]),
                testing_start=_date_text(evaluation_frame.iloc[train_bars]["date"]),
                testing_end=_date_text(evaluation_frame.iloc[-1]["date"]),
                selected_parameters=selected_parameters,
                selection_metric=metric,
                candidate_training_results=candidate_results,
                out_of_sample_result=out_of_sample,
            )
        )
    return RollingModelSelectionResult(
        strategy=strategy_name,
        train_bars=train_bars,
        test_bars=test_bars,
        selection_metric=metric,
        candidate_set_fingerprint=candidate_set_fingerprint,
        strategy_implementation_fingerprint=strategy_implementation_fingerprint,
        execution_engine_fingerprint=execution_engine_fingerprint,
        candidate_parameter_sets=candidates,
        folds=folds,
        warnings=[
            "Each fold selects parameters from its preceding training window only; no test-window metric enters parameter selection.",
            "Test folds are independent marked-to-market paper evaluations; their compounded return is not a continuous portfolio simulation.",
            "Candidate sets are supplied by the researcher and are not a proof that the search space was pre-registered or exhaustive.",
            "Daily-bar limitations remain: no point-in-time universe, limit-up/down, suspensions, liquidity capacity, corporate actions, delistings, or fill-quality controls.",
        ],
    )


def _normalise_candidate_parameter_sets(
    values: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if isinstance(values, (str, bytes, bytearray)) or not isinstance(values, Sequence):
        raise ValueError("candidate_parameter_sets must be a non-empty list of parameter objects")
    if not values or len(values) > _MAX_PARAMETER_CANDIDATES:
        raise ValueError(f"candidate_parameter_sets must contain between 1 and {_MAX_PARAMETER_CANDIDATES} entries")
    normalized: list[dict[str, Any]] = []
    fingerprints: set[str] = set()
    for value in values:
        if not isinstance(value, Mapping):
            raise ValueError("every candidate parameter set must be an object")
        candidate = {str(key): item for key, item in value.items()}
        try:
            fingerprint = json.dumps(candidate, sort_keys=True, separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError) as error:
            raise ValueError("candidate parameter sets must be JSON-serializable finite values") from error
        if fingerprint in fingerprints:
            raise ValueError("candidate_parameter_sets must not contain duplicate parameter sets")
        fingerprints.add(fingerprint)
        normalized.append(json.loads(fingerprint))
    return normalized


def _candidate_training_result(
    training_frame: pd.DataFrame,
    *,
    strategy_name: str,
    parameters: Mapping[str, Any],
    initial_capital: float,
    selection_metric: str,
    commission_rate: float,
    stamp_duty_rate: float,
    transfer_fee_rate: float,
) -> dict[str, Any]:
    result = BacktestEngine().run(
        training_frame,
        strategy_name=strategy_name,
        initial_capital=initial_capital,
        strategy_params=dict(parameters),
        commission_rate=commission_rate,
        stamp_duty_rate=stamp_duty_rate,
        transfer_fee_rate=transfer_fee_rate,
    )
    return {
        "parameters": dict(parameters),
        "selection_value": float(getattr(result, selection_metric)),
        "total_return": result.total_return,
        "max_drawdown": result.max_drawdown,
        "sharpe_ratio": result.sharpe_ratio,
        "trade_count": len(result.trades),
    }


def _selection_sort_key(result: Mapping[str, Any], metric: str) -> tuple[float, float, float, str]:
    # ``min`` chooses the highest metric, then lower drawdown, then higher
    # Sharpe, and finally a stable canonical parameter representation.
    return (
        -float(result["selection_value"]),
        float(result["max_drawdown"]),
        -float(result["sharpe_ratio"]),
        json.dumps(result["parameters"], sort_keys=True, separators=(",", ":")),
    )


def _date_text(value: Any) -> str:
    timestamp = pd.Timestamp(value)
    if pd.isna(timestamp):
        raise ValueError("rolling model selection requires valid date values")
    return timestamp.date().isoformat()


def _implementation_fingerprint(subject: object) -> str:
    """Bind the validation record to the strategy or engine source in use."""
    try:
        source = inspect.getsource(subject)
    except (OSError, TypeError) as error:
        raise ValueError("unable to fingerprint the strategy implementation") from error
    return "sha256:" + hashlib.sha256(source.encode("utf-8")).hexdigest()
