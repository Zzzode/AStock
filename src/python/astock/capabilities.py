"""Agent capability kernel.

This module is the Python layer's stable contract for agents and skills.
It returns JSON-serializable data packets and does not provide a human UI.
CLI and API entry points should stay thin adapters over these functions.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Optional, cast

from .backtest.engine import BacktestEngine
from .backtest.strategies import STRATEGIES
from .config import ConfigManager
from .data import get_industry_service
from .memory import FeedbackLearner
from .quote import QuoteService
from .recommend import Recommender, RecommendResult
from .services import AnalysisService, TeamAnalysisService
from .stock_picker import ScreenResult, StockScreener
from .storage import Database

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DB_PATH = PROJECT_ROOT / "data" / "stocks.db"


def _resolve_db_path(db_path: Optional[Path] = None) -> Path:
    return db_path or DEFAULT_DB_PATH


def _parse_date(value: Optional[str | date], default: date) -> date:
    if value is None:
        return default
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _serialize_screen_result(
    result: ScreenResult,
    industry: Optional[str] = None,
    industry_change: Optional[float] = None,
) -> dict[str, Any]:
    return {
        "code": result.code,
        "name": result.name,
        "matched_factors": result.matched_factors,
        "matched_factor_count": result.matched_factor_count,
        "factor_checks": result.factor_checks,
        "data": result.data,
        "industry": industry,
        "industry_change": industry_change,
        "screened_at": result.screened_at.isoformat(),
    }


def serialize_recommend_result(result: RecommendResult) -> dict[str, Any]:
    """Serialize a recommendation candidate-pool result."""
    return {
        "success": result.success,
        "total": result.total,
        "error": result.error,
        "config_used": result.config_used,
        "selection_context": result.selection_context,
        "candidates": [
            {
                "code": candidate.code,
                "name": candidate.name,
                "matched_factors": candidate.matched_factors,
                "matched_factor_count": candidate.matched_factor_count,
                "factor_checks": candidate.factor_checks,
                "industry": candidate.industry,
                "industry_change": candidate.industry_change,
                "data": candidate.data,
                "collected_at": candidate.collected_at.isoformat(),
            }
            for candidate in result.candidates
        ],
    }


async def initialize_database(
    *,
    skip_refresh: bool = False,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Initialize local storage for agent capabilities."""
    resolved_db_path = _resolve_db_path(db_path)
    resolved_db_path.parent.mkdir(parents=True, exist_ok=True)
    db = Database(str(resolved_db_path))
    await db.connect()
    try:
        await db.init_tables()
        loaded_count = 0
        if not skip_refresh:
            loaded_count = await QuoteService(db).refresh_stocks()
        return {
            "success": True,
            "loaded_count": loaded_count,
            "db_path": str(resolved_db_path),
        }
    finally:
        await db.close()


async def get_quote(code: str, *, db_path: Optional[Path] = None) -> dict[str, Any]:
    """Fetch a real-time or degraded quote packet."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        return cast(dict[str, Any], await QuoteService(db).get_realtime(code))
    finally:
        await db.close()


async def analyze_stock(
    code: str,
    *,
    days: int = 100,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return technical-analysis data for agent reasoning."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        service = AnalysisService(db)
        result = await service.analyze(code, days=days)
        return cast(dict[str, Any], service.to_dict(result))
    finally:
        await db.close()


async def build_team_packet(
    code: str,
    *,
    question: str,
    days: int = 100,
    user_id: str = "default",
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return the unified packet consumed by the Agent team."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        service = TeamAnalysisService(db)
        result = await service.analyze(
            code, question=question, days=days, user_id=user_id
        )
        return cast(dict[str, Any], service.to_dict(result))
    finally:
        await db.close()


async def screen_stocks(
    *,
    factors: Optional[list[str]] = None,
    codes: Optional[list[str]] = None,
    include_industries: Optional[list[str]] = None,
    exclude_industries: Optional[list[str]] = None,
    limit: int = 10,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return stock-screening snapshots and factor hit details."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        quote_service = QuoteService(db)
        screener = StockScreener(quote_service)
        results = await screener.screen(factors=factors, codes=codes, limit=limit)

        industry_service = get_industry_service()
        await industry_service.initialize(allow_stale_cache=bool(codes))

        if include_industries or exclude_industries:
            result_codes = [result.code for result in results]
            filtered_codes = await industry_service.filter_by_industry(
                result_codes,
                include_industries=include_industries,
                exclude_industries=exclude_industries,
            )
            results = [result for result in results if result.code in filtered_codes]

        enriched_results: list[dict[str, Any]] = []
        for result in results:
            stock_industry = await industry_service.get_stock_industry(result.code)
            enriched_results.append(
                _serialize_screen_result(
                    result,
                    industry=stock_industry.industry if stock_industry else None,
                    industry_change=(
                        stock_industry.industry_change if stock_industry else None
                    ),
                )
            )

        return {
            "total": len(enriched_results),
            "mode": "single_stock" if codes else "market_scan",
            "data_quality": "daily_only",
            "requested_factors": factors or [],
            "results": enriched_results,
        }
    finally:
        await db.close()


async def build_recommendation_pool(
    *,
    user_id: str = "default",
    limit: int = 10,
    options: Optional[dict[str, Any]] = None,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Return personalized candidate-pool data without final recommendations."""
    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        quote_service = QuoteService(db)
        screener = StockScreener(quote_service)
        industry_service = get_industry_service()
        await industry_service.initialize()
        recommender = Recommender(screener, industry_service)
        result = await recommender.handle_recommend(
            user_id=user_id,
            limit=limit,
            options=options,
        )
        return serialize_recommend_result(result)
    finally:
        await db.close()


async def run_signal_backtest(
    code: str,
    *,
    strategy: str,
    start_date: Optional[str | date] = None,
    end_date: Optional[str | date] = None,
    capital: float = 100000.0,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Run historical technical-signal backtesting for agent evaluation."""
    if strategy not in STRATEGIES:
        return {
            "error": f"Unknown strategy name '{strategy}'",
            "available_strategies": list(STRATEGIES.keys()),
        }

    end_dt = _parse_date(end_date, date.today())
    start_dt = _parse_date(start_date, end_dt - timedelta(days=365))

    db = Database(str(_resolve_db_path(db_path)))
    await db.connect()
    try:
        df = await QuoteService(db).get_daily(code)
        if df.empty:
            return {"error": "No data"}

        if "date" in df.columns:
            df["date"] = df["date"].apply(
                lambda item: (
                    datetime.strptime(item, "%Y-%m-%d").date()
                    if isinstance(item, str)
                    else item
                )
            )
            df = df[(df["date"] >= start_dt) & (df["date"] <= end_dt)]
        else:
            df = df.iloc[-365:]

        if df.empty:
            return {"error": "No data in the specified date range"}

        result = BacktestEngine().run(
            df,
            strategy_name=strategy,
            initial_capital=capital,
        )
        result.code = code
        return cast(dict[str, Any], result.to_dict())
    finally:
        await db.close()


def list_signal_strategies() -> list[dict[str, str]]:
    """Return available backtest strategy metadata."""
    return [
        {"name": name, "description": strategy.description}
        for name, strategy in STRATEGIES.items()
    ]


async def record_team_feedback(
    code: str,
    *,
    action: str,
    outcome: str,
    strategy: Optional[str] = None,
    signals: Optional[list[str]] = None,
    note: Optional[str] = None,
) -> dict[str, Any]:
    """Record outcome feedback for future agent reasoning."""
    record = await FeedbackLearner().record_feedback(
        code=code,
        action=action,
        outcome=outcome,
        strategy=strategy,
        signals=signals,
        note=note,
    )
    return {
        "code": record.code,
        "action": record.action,
        "outcome": record.outcome,
        "strategy": record.strategy,
        "signals": record.signals,
        "note": record.note,
        "created_at": record.created_at.isoformat(),
    }


def load_user_config(user_id: str = "default") -> dict[str, Any]:
    """Load user config as a JSON-ready dictionary."""
    config = ConfigManager().load(user_id)
    data = config.model_dump()
    data["trading_style"] = config.trading_style.value
    data["risk_level"] = config.risk_level.value
    return cast(dict[str, Any], data)
