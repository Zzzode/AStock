"""Multi-source data consistency checker.

Cross-validates key financial metrics between quote service, financial
statements, and news pipeline to detect conflicts and stale data.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from ..utils import get_logger

logger = get_logger("consistency")


@dataclass
class ConsistencyConflict:
    """A detected data conflict between sources."""

    metric: str
    source_a: str
    value_a: Any
    source_b: str
    value_b: Any
    deviation_pct: Optional[float] = None
    severity: str = "warning"  # warning | error
    description: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "source_a": self.source_a,
            "value_a": self.value_a,
            "source_b": self.source_b,
            "value_b": self.value_b,
            "deviation_pct": self.deviation_pct,
            "severity": self.severity,
            "description": self.description,
        }


@dataclass
class DataFreshnessReport:
    """Freshness status of each data source."""

    source: str
    last_updated: Optional[datetime] = None
    age_seconds: Optional[float] = None
    status: str = "unknown"  # fresh | stale | unavailable

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "age_seconds": self.age_seconds,
            "status": self.status,
        }


async def check_data_consistency(
    code: str,
    *,
    quote_data: Optional[dict[str, Any]] = None,
    financial_data: Optional[dict[str, Any]] = None,
    news_data: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Cross-validate data from multiple sources for a stock.

    Checks:
    1. EPS consistency: financial EPS vs PE-implied EPS from quote
    2. Revenue growth: financial YoY vs news claims
    3. Price consistency: quote price vs financial-derived metrics
    4. Freshness: how old each data source is

    Args:
        code: Stock code
        quote_data: Output from get_quote() or get_realtime_quote()
        financial_data: Output from get_financial_statements()
        news_data: Output from get_corporate_events()
    """
    conflicts: list[ConsistencyConflict] = []
    freshness: list[DataFreshnessReport] = []
    warnings: list[str] = []

    # Check quote freshness
    if quote_data:
        quote_time = _parse_timestamp(quote_data.get("timestamp") or quote_data.get("trade_date"))
        freshness.append(_freshness_report("quote", quote_time))
    else:
        freshness.append(DataFreshnessReport(source="quote", status="unavailable"))

    # Check financial freshness
    if financial_data:
        fin_time = _parse_timestamp(financial_data.get("fetched_at"))
        freshness.append(_freshness_report("financial", fin_time))
    else:
        freshness.append(DataFreshnessReport(source="financial", status="unavailable"))

    # Check news freshness
    if news_data:
        news_time = _parse_timestamp(news_data.get("fetched_at"))
        freshness.append(_freshness_report("news", news_time))
    else:
        freshness.append(DataFreshnessReport(source="news", status="unavailable"))

    # Cross-validation: EPS from financial vs PE-implied from quote
    if quote_data and financial_data:
        conflicts.extend(_check_eps_consistency(quote_data, financial_data))
        conflicts.extend(_check_price_book_consistency(quote_data, financial_data))

    # Cross-validation: growth claims in news vs financial data
    if news_data and financial_data:
        conflicts.extend(_check_growth_claims(news_data, financial_data))

    return {
        "code": code,
        "checked_at": datetime.now().isoformat(),
        "conflicts": [c.to_dict() for c in conflicts],
        "conflict_count": len(conflicts),
        "freshness": [f.to_dict() for f in freshness],
        "warnings": warnings,
        "data_quality": _overall_quality(conflicts, freshness),
    }


def _check_eps_consistency(
    quote_data: dict[str, Any], financial_data: dict[str, Any]
) -> list[ConsistencyConflict]:
    """Compare financial EPS with PE-implied EPS."""
    conflicts = []

    price = _safe_float(quote_data.get("price") or quote_data.get("close"))
    pe = _safe_float(quote_data.get("pe") or quote_data.get("pe_ttm"))

    periods = financial_data.get("periods", [])
    fin_eps = None
    if periods:
        fin_eps = _safe_float(periods[0].get("metrics", {}).get("eps_basic"))

    if price and pe and pe > 0:
        implied_eps = price / pe
        if fin_eps and fin_eps != 0:
            deviation = abs(implied_eps - fin_eps) / abs(fin_eps) * 100
            if deviation > 20:
                conflicts.append(ConsistencyConflict(
                    metric="eps",
                    source_a="quote_pe_implied",
                    value_a=round(implied_eps, 4),
                    source_b="financial_statement",
                    value_b=fin_eps,
                    deviation_pct=round(deviation, 2),
                    severity="warning" if deviation < 50 else "error",
                    description=f"EPS deviation {deviation:.1f}%: PE-implied={implied_eps:.4f} vs reported={fin_eps}",
                ))

    return conflicts


def _check_price_book_consistency(
    quote_data: dict[str, Any], financial_data: dict[str, Any]
) -> list[ConsistencyConflict]:
    """Check PB ratio consistency."""
    conflicts = []

    price = _safe_float(quote_data.get("price") or quote_data.get("close"))
    pb = _safe_float(quote_data.get("pb"))

    periods = financial_data.get("periods", [])
    bps = None
    if periods:
        bps = _safe_float(periods[0].get("metrics", {}).get("bps"))

    if price and pb and pb > 0 and bps:
        implied_bps = price / pb
        deviation = abs(implied_bps - bps) / abs(bps) * 100
        if deviation > 20:
            conflicts.append(ConsistencyConflict(
                metric="bps",
                source_a="quote_pb_implied",
                value_a=round(implied_bps, 4),
                source_b="financial_statement",
                value_b=bps,
                deviation_pct=round(deviation, 2),
                severity="warning",
                description=f"BPS deviation {deviation:.1f}%",
            ))

    return conflicts


def _check_growth_claims(
    news_data: dict[str, Any], financial_data: dict[str, Any]
) -> list[ConsistencyConflict]:
    """Check if earnings forecast claims match financial growth data."""
    conflicts = []

    yoy = financial_data.get("yoy_growth", {})
    reported_profit_growth = yoy.get("net_profit")

    for event in news_data.get("events", []):
        if event.get("event_type") != "earnings_forecast":
            continue
        raw = event.get("raw_data", {})
        change_ratio = _safe_float(raw.get("change_ratio"))

        if change_ratio is not None and reported_profit_growth is not None:
            deviation = abs(change_ratio - reported_profit_growth)
            if deviation > 15:
                conflicts.append(ConsistencyConflict(
                    metric="profit_growth",
                    source_a="earnings_forecast",
                    value_a=change_ratio,
                    source_b="financial_yoy",
                    value_b=reported_profit_growth,
                    deviation_pct=round(deviation, 2),
                    severity="warning",
                    description=f"Profit growth: forecast={change_ratio}% vs actual YoY={reported_profit_growth}%",
                ))
            break

    return conflicts


def _freshness_report(source: str, timestamp: Optional[datetime]) -> DataFreshnessReport:
    if timestamp is None:
        return DataFreshnessReport(source=source, status="unknown")
    age = (datetime.now() - timestamp).total_seconds()
    status = "fresh" if age < 3600 else "stale" if age < 86400 else "very_stale"
    return DataFreshnessReport(
        source=source,
        last_updated=timestamp,
        age_seconds=age,
        status=status,
    )


def _overall_quality(
    conflicts: list[ConsistencyConflict],
    freshness: list[DataFreshnessReport],
) -> str:
    error_conflicts = [c for c in conflicts if c.severity == "error"]
    stale_sources = [f for f in freshness if f.status in ("stale", "very_stale")]
    unavailable = [f for f in freshness if f.status == "unavailable"]

    if error_conflicts or len(unavailable) >= 2:
        return "degraded"
    elif conflicts or stale_sources:
        return "partial"
    return "consistent"


def _parse_timestamp(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except (ValueError, TypeError):
        return None


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        f = float(value)
        return f if f == f else None  # NaN check
    except (ValueError, TypeError):
        return None
