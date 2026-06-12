"""Structured financial statement service.

Fetches income statement, balance sheet, and cash flow data via akshare,
normalizes into a canonical schema, and computes YoY/QoQ growth rates.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from functools import partial
from typing import Any, Optional

import akshare as ak
import pandas as pd

from ..utils import get_logger

logger = get_logger("financial_statements")

_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="fin_stmt_")
    return _executor


INCOME_INDICATORS = {
    "营业总收入": "total_revenue",
    "营业成本": "operating_cost",
    "净利润": "net_profit",
    "归母净利润": "net_profit_parent",
    "扣非净利润": "net_profit_deducted",
    "基本每股收益": "eps_basic",
}

BALANCE_INDICATORS = {
    "股东权益合计(净资产)": "equity",
    "资产负债率": "debt_ratio",
    "商誉": "goodwill",
    "每股净资产": "bps",
}

CASH_FLOW_INDICATORS = {
    "经营现金流量净额": "operating_cash_flow",
    "每股现金流": "cash_flow_per_share",
}

PROFITABILITY_INDICATORS = {
    "净资产收益率(ROE)": "roe",
    "总资产报酬率(ROA)": "roa",
    "毛利率": "gross_margin",
    "销售净利率": "net_margin",
    "营业利润率": "operating_margin",
}

GROWTH_INDICATORS = {
    "营业总收入增长率": "revenue_growth",
    "归属母公司净利润增长率": "profit_growth",
}

QUALITY_INDICATORS = {
    "经营活动净现金/销售收入": "ocf_to_revenue",
    "期间费用率": "expense_ratio",
    "流动比率": "current_ratio",
    "速动比率": "quick_ratio",
}

ALL_INDICATORS = {
    **INCOME_INDICATORS,
    **BALANCE_INDICATORS,
    **CASH_FLOW_INDICATORS,
    **PROFITABILITY_INDICATORS,
    **GROWTH_INDICATORS,
    **QUALITY_INDICATORS,
}


@dataclass
class FinancialPeriod:
    """One reporting period's financial data."""

    period: str  # e.g. "20241231"
    year: int
    quarter: int
    metrics: dict[str, Optional[float]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "period": self.period,
            "year": self.year,
            "quarter": self.quarter,
            "metrics": self.metrics,
        }


@dataclass
class FinancialStatements:
    """Complete financial statements for a stock."""

    code: str
    name: str
    periods: list[FinancialPeriod] = field(default_factory=list)
    yoy_growth: dict[str, Optional[float]] = field(default_factory=dict)
    qoq_growth: dict[str, Optional[float]] = field(default_factory=dict)
    fetched_at: datetime = field(default_factory=datetime.now)
    data_quality: str = "full"
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "name": self.name,
            "periods": [p.to_dict() for p in self.periods],
            "yoy_growth": self.yoy_growth,
            "qoq_growth": self.qoq_growth,
            "fetched_at": self.fetched_at.isoformat(),
            "data_quality": self.data_quality,
            "warnings": self.warnings,
        }

    def latest_period(self) -> Optional[FinancialPeriod]:
        return self.periods[0] if self.periods else None


class FinancialStatementService:
    """Service for fetching and computing financial statements."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[FinancialStatements, float]] = {}
        self._cache_ttl = 3600.0  # 1 hour

    async def get_statements(
        self,
        code: str,
        *,
        periods: int = 8,
    ) -> FinancialStatements:
        """Fetch structured financial statements for a stock.

        Args:
            code: Stock code (e.g. "000001")
            periods: Number of recent reporting periods to return
        """
        import time

        cache_key = f"{code}:{periods}"
        cached = self._cache.get(cache_key)
        if cached and (time.time() - cached[1]) < self._cache_ttl:
            return cached[0]

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            _get_executor(),
            partial(self._fetch_sync, code, periods),
        )
        self._cache[cache_key] = (result, time.time())
        return result

    def _fetch_sync(self, code: str, max_periods: int) -> FinancialStatements:
        """Synchronous fetch and parse."""
        warnings: list[str] = []
        try:
            df = ak.stock_financial_abstract(symbol=code)
        except Exception as e:
            logger.warning(f"Failed to fetch financial data for {code}: {e}")
            return FinancialStatements(
                code=code,
                name="",
                data_quality="unavailable",
                warnings=[f"Data fetch failed: {e}"],
            )

        if df.empty:
            return FinancialStatements(
                code=code,
                name="",
                data_quality="unavailable",
                warnings=["Empty response from data source"],
            )

        period_columns = [
            col for col in df.columns
            if col not in ("选项", "指标") and col.isdigit() and len(col) == 8
        ]
        period_columns = sorted(period_columns, reverse=True)[:max_periods]

        indicator_map = {}
        for _, row in df.iterrows():
            cn_name = str(row["指标"]).strip()
            if cn_name in ALL_INDICATORS:
                en_name = ALL_INDICATORS[cn_name]
                indicator_map[en_name] = row

        periods_list: list[FinancialPeriod] = []
        for period_col in period_columns:
            year = int(period_col[:4])
            month = int(period_col[4:6])
            quarter = _month_to_quarter(month)

            metrics: dict[str, Optional[float]] = {}
            for en_name, row in indicator_map.items():
                raw_value = row.get(period_col)
                metrics[en_name] = _safe_float(raw_value)

            periods_list.append(FinancialPeriod(
                period=period_col,
                year=year,
                quarter=quarter,
                metrics=metrics,
            ))

        yoy = _compute_yoy(periods_list)
        qoq = _compute_qoq(periods_list)

        name = self._get_stock_name(code)

        if len(periods_list) < 2:
            warnings.append("Insufficient periods for growth calculation")

        return FinancialStatements(
            code=code,
            name=name,
            periods=periods_list,
            yoy_growth=yoy,
            qoq_growth=qoq,
            data_quality="full" if periods_list else "unavailable",
            warnings=warnings,
        )

    def _get_stock_name(self, code: str) -> str:
        try:
            df = ak.stock_individual_info_em(symbol=code)
            if df is not None and not df.empty:
                name_row = df[df["item"] == "股票简称"]
                if not name_row.empty:
                    return str(name_row.iloc[0]["value"])
        except Exception:
            pass
        return ""


def _month_to_quarter(month: int) -> int:
    if month <= 3:
        return 1
    elif month <= 6:
        return 2
    elif month <= 9:
        return 3
    return 4


def _safe_float(value: Any) -> Optional[float]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _compute_yoy(periods: list[FinancialPeriod]) -> dict[str, Optional[float]]:
    """Compute year-over-year growth using latest period vs same period last year."""
    if len(periods) < 2:
        return {}

    latest = periods[0]
    same_period_last_year = None
    for p in periods[1:]:
        if p.quarter == latest.quarter and p.year == latest.year - 1:
            same_period_last_year = p
            break

    if same_period_last_year is None:
        return {}

    return _growth_between(latest, same_period_last_year)


def _compute_qoq(periods: list[FinancialPeriod]) -> dict[str, Optional[float]]:
    """Compute quarter-over-quarter growth using latest vs previous period."""
    if len(periods) < 2:
        return {}
    return _growth_between(periods[0], periods[1])


def _growth_between(
    current: FinancialPeriod, previous: FinancialPeriod
) -> dict[str, Optional[float]]:
    """Compute growth rates between two periods for key absolute metrics."""
    growth_metrics = [
        "total_revenue", "net_profit", "net_profit_parent",
        "net_profit_deducted", "operating_cash_flow", "equity",
    ]
    result: dict[str, Optional[float]] = {}
    for metric in growth_metrics:
        curr_val = current.metrics.get(metric)
        prev_val = previous.metrics.get(metric)
        if curr_val is not None and prev_val is not None and prev_val != 0:
            result[metric] = round((curr_val - prev_val) / abs(prev_val) * 100, 2)
        else:
            result[metric] = None
    return result
