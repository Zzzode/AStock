"""Earnings calendar data source.

Fetches upcoming and past earnings disclosure dates from akshare,
allowing the scheduler to trigger verification and data refresh
around specific reporting events.
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta
from functools import partial
from typing import Any, Optional

import akshare as ak
import pandas as pd

from ..utils import get_logger

logger = get_logger("earnings_calendar")

_executor: Optional[ThreadPoolExecutor] = None


def _get_executor() -> ThreadPoolExecutor:
    global _executor
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="earnings_")
    return _executor


async def get_earnings_calendar(
    *,
    period: str = "2025年报",
    codes: Optional[list[str]] = None,
    upcoming_only: bool = False,
    days_ahead: int = 30,
) -> dict[str, Any]:
    """Fetch earnings disclosure calendar.

    Args:
        period: Reporting period (e.g. "2025年报", "2025三季报", "2025中报", "2025一季报")
        codes: Filter by specific stock codes (None = all)
        upcoming_only: Only return stocks with disclosure date in the future
        days_ahead: When upcoming_only=True, look this many days ahead

    Returns:
        Calendar data packet with disclosure dates and schedule.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        _get_executor(),
        partial(_fetch_sync, period, codes, upcoming_only, days_ahead),
    )


def _fetch_sync(
    period: str,
    codes: Optional[list[str]],
    upcoming_only: bool,
    days_ahead: int,
) -> dict[str, Any]:
    try:
        df = ak.stock_report_disclosure(market="沪深京", period=period)
    except Exception as e:
        logger.warning(f"Failed to fetch earnings calendar: {e}")
        return {
            "period": period,
            "entries": [],
            "error": str(e),
            "data_quality": "unavailable",
        }

    if df is None or df.empty:
        return {
            "period": period,
            "entries": [],
            "data_quality": "unavailable",
        }

    if codes:
        code_set = set(codes)
        df = df[df["股票代码"].astype(str).isin(code_set)]

    today = date.today()
    entries: list[dict[str, Any]] = []

    for _, row in df.iterrows():
        code = str(row.get("股票代码", ""))
        name = str(row.get("股票简称", ""))
        first_date = _parse_date(row.get("首次预约"))
        actual_date = _parse_date(row.get("实际披露"))

        disclosure_date = actual_date or first_date
        if disclosure_date is None:
            continue

        if upcoming_only:
            cutoff = today + timedelta(days=days_ahead)
            if disclosure_date < today or disclosure_date > cutoff:
                continue

        status = "disclosed" if actual_date and actual_date <= today else "scheduled"

        entries.append({
            "code": code,
            "name": name,
            "scheduled_date": first_date.isoformat() if first_date else None,
            "actual_date": actual_date.isoformat() if actual_date else None,
            "disclosure_date": disclosure_date.isoformat(),
            "status": status,
            "days_until": (disclosure_date - today).days,
        })

    entries.sort(key=lambda x: x["disclosure_date"])

    return {
        "period": period,
        "fetched_at": datetime.now().isoformat(),
        "total_entries": len(entries),
        "entries": entries,
        "data_quality": "full",
    }


def _parse_date(value: Any) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.date()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
