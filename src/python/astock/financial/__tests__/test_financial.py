"""Tests for financial statement service (unit tests)."""

import pytest

from astock.financial import (
    FinancialPeriod,
    FinancialStatements,
    _compute_yoy,
    _compute_qoq,
    _month_to_quarter,
    _safe_float,
)


def test_month_to_quarter():
    assert _month_to_quarter(3) == 1
    assert _month_to_quarter(6) == 2
    assert _month_to_quarter(9) == 3
    assert _month_to_quarter(12) == 4
    assert _month_to_quarter(1) == 1


def test_safe_float():
    assert _safe_float(1.5) == 1.5
    assert _safe_float("3.14") == 3.14
    assert _safe_float(None) is None
    assert _safe_float("N/A") is None


def test_compute_qoq():
    periods = [
        FinancialPeriod(
            period="20240630", year=2024, quarter=2,
            metrics={"total_revenue": 200, "net_profit": 50},
        ),
        FinancialPeriod(
            period="20240331", year=2024, quarter=1,
            metrics={"total_revenue": 180, "net_profit": 45},
        ),
    ]
    qoq = _compute_qoq(periods)
    assert qoq["total_revenue"] == pytest.approx(11.11, abs=0.01)
    assert qoq["net_profit"] == pytest.approx(11.11, abs=0.01)


def test_compute_yoy():
    periods = [
        FinancialPeriod(
            period="20240630", year=2024, quarter=2,
            metrics={"total_revenue": 200, "net_profit": 50},
        ),
        FinancialPeriod(
            period="20240331", year=2024, quarter=1,
            metrics={"total_revenue": 190, "net_profit": 48},
        ),
        FinancialPeriod(
            period="20230630", year=2023, quarter=2,
            metrics={"total_revenue": 160, "net_profit": 40},
        ),
    ]
    yoy = _compute_yoy(periods)
    assert yoy["total_revenue"] == 25.0
    assert yoy["net_profit"] == 25.0


def test_compute_yoy_no_match():
    periods = [
        FinancialPeriod(
            period="20240630", year=2024, quarter=2,
            metrics={"total_revenue": 200},
        ),
        FinancialPeriod(
            period="20240331", year=2024, quarter=1,
            metrics={"total_revenue": 190},
        ),
    ]
    yoy = _compute_yoy(periods)
    assert yoy == {}


def test_financial_statements_to_dict():
    stmt = FinancialStatements(
        code="000001",
        name="平安银行",
        periods=[
            FinancialPeriod(
                period="20240630", year=2024, quarter=2,
                metrics={"total_revenue": 200},
            ),
        ],
        yoy_growth={"total_revenue": 10.0},
        qoq_growth={"total_revenue": 5.0},
        data_quality="full",
    )
    d = stmt.to_dict()
    assert d["code"] == "000001"
    assert len(d["periods"]) == 1
    assert d["yoy_growth"]["total_revenue"] == 10.0
