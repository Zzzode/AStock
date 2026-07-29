"""Optional REST adapter for agent capabilities."""

from datetime import datetime
from pathlib import Path
from typing import Optional, Any, AsyncIterator

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .storage import Database
from .quote import QuoteService
from .stock_picker import StockScreener
from .backtest import BacktestEngine
from .config import ConfigManager
from .utils import get_logger, setup_logging

# Configure logging
setup_logging(level="INFO")
logger = get_logger("api")

# Create application
app = FastAPI(
    title="A-Share Agent Capability API",
    description="Optional REST adapter over the A-share agent capability layer",
    version="0.1.0",
)

# CORS support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database path
DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "stocks.db"


# ============ Dependency Injection ============


async def get_db() -> AsyncIterator[Database]:
    """Get database connection"""
    db = Database(str(DB_PATH))
    await db.connect()
    try:
        yield db
    finally:
        await db.close()


async def get_quote_service(db: Database = Depends(get_db)) -> QuoteService:
    """Get quote service"""
    return QuoteService(db)


# ============ Response Models ============


class QuoteResponse(BaseModel):
    """Quote response"""

    code: str
    name: str
    price: float
    change_percent: float
    change: float
    volume: float
    amount: float
    high: float
    low: float
    open: float
    prev_close: float


class AnalysisResponse(BaseModel):
    """Raw price-and-volume observation response."""

    code: str
    latest: dict[str, Any]
    previous: dict[str, Any]


class ScreenResult(BaseModel):
    """Screening result"""

    code: str
    name: Optional[str]
    matched_factors: list[str]
    matched_factor_count: int
    factor_checks: dict[str, dict[str, Any]]
    data: dict[str, Any] = Field(default_factory=dict)
    screened_at: str


class ScreenResponse(BaseModel):
    """Screening response"""

    total: int
    requested_factors: list[str] = Field(default_factory=list)
    results: list[ScreenResult]


class BacktestResponse(BaseModel):
    """Backtest response"""

    code: str
    strategy: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    trades: list[dict[str, Any]]
    equity_curve: list[dict[str, Any]]


class ErrorResponse(BaseModel):
    """Error response"""

    error: str
    message: str
    code: Optional[str] = None


# ============ API Routes ============


@app.get("/")
async def root() -> dict[str, Any]:
    """API root endpoint"""
    return {
        "name": "A-Share Agent Capability API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": [
            "/quote/{code}",
            "/analyze/{code}",
            "/screen",
            "/backtest/{code}",
            "/recommend",
            "/config",
        ],
    }


@app.get(
    "/quote/{code}",
    response_model=QuoteResponse,
    responses={404: {"model": ErrorResponse}},
)
async def get_quote(
    code: str,
    quote_service: QuoteService = Depends(get_quote_service),
) -> QuoteResponse:
    """Get real-time stock quote"""
    try:
        result = await quote_service.get_realtime(code)
        return QuoteResponse(**result)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Stock code not found: {code}")
    except Exception as e:
        logger.error(f"Failed to get quote: {code}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get quote: {str(e)}")


@app.get(
    "/analyze/{code}",
    response_model=AnalysisResponse,
    responses={404: {"model": ErrorResponse}},
)
async def analyze_stock(
    code: str,
    days: int = Query(100, ge=30, le=500, description="Number of days to analyze"),
    db: Database = Depends(get_db),
    quote_service: QuoteService = Depends(get_quote_service),
) -> AnalysisResponse:
    """Return raw daily observations without directional signal labels."""
    try:
        df = await quote_service.get_daily(code, limit=days)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data: {code}")

        latest = df.iloc[-1].to_dict()
        previous = df.iloc[-2].to_dict() if len(df) > 1 else latest
        return AnalysisResponse(code=code, latest=latest, previous=previous)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Technical analysis failed: {code}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Technical analysis failed: {str(e)}"
        )


@app.get("/screen", response_model=ScreenResponse)
async def screen_stocks(
    factors: Optional[str] = Query(None, description="Factor list, comma-separated"),
    limit: int = Query(10, ge=1, le=100, description="Number of results to return"),
    quote_service: QuoteService = Depends(get_quote_service),
) -> ScreenResponse:
    """Stock screening"""
    try:
        screener = StockScreener(quote_service)

        factor_list = None
        if factors:
            factor_list = [f.strip() for f in factors.split(",")]

        results = await screener.screen(factors=factor_list, limit=limit)

        return ScreenResponse(
            total=len(results),
            requested_factors=factor_list or [],
            results=[
                ScreenResult(
                    code=r.code,
                    name=r.name,
                    matched_factors=r.matched_factors,
                    matched_factor_count=r.matched_factor_count,
                    factor_checks=r.factor_checks,
                    data=r.data,
                    screened_at=r.screened_at.isoformat(),
                )
                for r in results
            ],
        )
    except Exception as e:
        logger.error("Stock screening failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Stock screening failed: {str(e)}")


@app.get("/backtest/{code}", response_model=BacktestResponse)
async def backtest_stock(
    code: str,
    strategy: Optional[str] = Query(
        None,
        description="Explicit legacy-study strategy; excluded from market-desk decisions",
    ),
    capital: float = Query(100000, ge=10000, description="Initial capital"),
    quote_service: QuoteService = Depends(get_quote_service),
) -> BacktestResponse:
    """Run an explicitly requested historical study, never a desk decision gate."""
    try:
        if not strategy:
            raise HTTPException(
                status_code=400,
                detail="strategy must be explicit; no indicator strategy is a market-desk default",
            )
        df = await quote_service.get_daily(code, save=False)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"No data: {code}")

        engine = BacktestEngine()
        result = engine.run(
            df,
            strategy_name=strategy,
            initial_capital=capital,
        )
        result.code = code

        trades = [trade.to_dict() for trade in result.trades]
        return BacktestResponse(
            code=code,
            strategy=result.strategy,
            start_date=result.start_date.isoformat(),
            end_date=result.end_date.isoformat(),
            initial_capital=result.initial_capital,
            final_capital=result.final_capital,
            total_return=result.total_return,
            annual_return=result.annual_return,
            max_drawdown=result.max_drawdown,
            sharpe_ratio=result.sharpe_ratio,
            win_rate=result.win_rate,
            trades=trades,
            equity_curve=result.equity_curve,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Backtest failed: {code}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@app.get("/recommend")
async def get_recommendations(
    user_id: str = Query("default", description="User ID"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    style: Optional[str] = Query(None, description="Trading style override"),
    risk: Optional[str] = Query(None, description="Risk level override"),
    quote_service: QuoteService = Depends(get_quote_service),
) -> Any:
    """Personalized recommendations"""
    try:
        from .recommend import Recommender
        from .stock_picker import StockScreener

        screener = StockScreener(quote_service)
        recommender = Recommender(screener)

        options: dict[str, str] = {}
        if style:
            options["trading_style"] = style
        if risk:
            options["risk_level"] = risk

        result = await recommender.handle_recommend(
            user_id=user_id,
            limit=limit,
            options=options if options else None,
        )

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
    except Exception as e:
        logger.error("Recommendation failed", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")


@app.get("/config")
async def get_config(
    user_id: str = Query("default", description="User ID"),
) -> dict[str, Any]:
    """Get user configuration"""
    try:
        config_manager = ConfigManager()
        config = config_manager.load(user_id)

        return {
            "user_id": config.user_id,
            "trading_style": config.trading_style.value,
            "risk_level": config.risk_level.value,
            "max_positions": config.max_positions,
            "position_size": config.position_size,
            "min_price": config.min_price,
            "max_price": config.max_price,
            "preferred_sectors": config.preferred_sectors,
            "excluded_sectors": config.excluded_sectors,
        }
    except Exception as e:
        logger.error("Failed to get config", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get config: {str(e)}")


@app.put("/config")
async def update_config(
    user_id: str = Query("default", description="User ID"),
    trading_style: Optional[str] = Query(None, description="Trading style"),
    risk_level: Optional[str] = Query(None, description="Risk level"),
    max_positions: Optional[int] = Query(None, description="Maximum positions"),
    position_size: Optional[float] = Query(None, description="Position size ratio"),
) -> dict[str, Any]:
    """Update user configuration"""
    try:
        from .config import TradingStyle, RiskLevel

        config_manager = ConfigManager()

        updates: dict[str, object] = {}
        if trading_style:
            for s in TradingStyle:
                if s.value == trading_style:
                    updates["trading_style"] = s
                    break
        if risk_level:
            for r in RiskLevel:
                if r.value == risk_level:
                    updates["risk_level"] = r
                    break
        if max_positions is not None:
            updates["max_positions"] = max_positions
        if position_size is not None:
            updates["position_size"] = position_size

        if updates:
            config = config_manager.update(user_id, **updates)
        else:
            config = config_manager.load(user_id)

        return {"success": True, "config": config.model_dump()}
    except Exception as e:
        logger.error("Failed to update config", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to update config: {str(e)}"
        )


@app.get("/strategies")
async def list_strategies() -> dict[str, Any]:
    """List all available strategies"""
    from .backtest.strategies import list_strategies

    return {"strategies": list_strategies()}


@app.get("/factors")
async def list_factors() -> dict[str, Any]:
    """List all available factors"""
    from .stock_picker.factors import FACTORS

    factors_by_type: dict[str, list[dict[str, Any]]] = {}
    for key, factor in FACTORS.items():
        type_name = factor.type.value
        if type_name not in factors_by_type:
            factors_by_type[type_name] = []
        factors_by_type[type_name].append(
            {
                "key": factor.key,
                "name": factor.name,
                "description": factor.description,
                "weight": factor.weight,
            }
        )

    return {"factors": factors_by_type}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


# Start command: uvicorn astock.api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
