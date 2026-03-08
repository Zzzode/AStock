"""FastAPI REST API 服务"""

from datetime import datetime
from pathlib import Path
from typing import Optional, List
import json

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..storage import Database
from ..quote import QuoteService
from ..analysis import TechnicalAnalyzer
from ..stock_picker import StockScreener
from ..backtest import BacktestEngine
from ..recommend import Recommender
from ..config import ConfigManager
from ..utils import get_logger, setup_logging

# 配置日志
setup_logging(level="INFO")
logger = get_logger("api")

# 创建应用
app = FastAPI(
    title="A股交易策略分析工具 API",
    description="基于 Agent Skills 的多 Agent A股交易策略分析工具 REST API",
    version="0.1.0",
)

# 跨域支持
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库路径
DB_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "stocks.db"


# ============ 依赖注入 ============


async def get_db():
    """获取数据库连接"""
    db = Database(str(DB_PATH))
    await db.connect()
    try:
        yield db
    finally:
        await db.close()


async def get_quote_service(db: Database = Depends(get_db)):
    """获取行情服务"""
    return QuoteService(db)


# ============ 响应模型 ============


class QuoteResponse(BaseModel):
    """行情响应"""

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
    """分析响应"""

    code: str
    signals: List[dict]
    latest: dict


class ScreenResult(BaseModel):
    """选股结果"""

    code: str
    name: Optional[str]
    score: float
    matched_factors: List[str]
    factor_scores: dict
    screened_at: str


class ScreenResponse(BaseModel):
    """选股响应"""

    total: int
    results: List[ScreenResult]


class BacktestResponse(BaseModel):
    """回测响应"""

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
    trades: List[dict]
    equity_curve: List[dict]


class ErrorResponse(BaseModel):
    """错误响应"""

    error: str
    message: str
    code: Optional[str] = None


# ============ API 路由 ============


@app.get("/")
async def root():
    """API 根路径"""
    return {
        "name": "A股交易策略分析工具 API",
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
):
    """获取股票实时行情"""
    try:
        result = await quote_service.get_realtime(code)
        return QuoteResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"股票代码不存在: {code}")
    except Exception as e:
        logger.error(f"获取行情失败: {code}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取行情失败: {str(e)}")


@app.get(
    "/analyze/{code}",
    response_model=AnalysisResponse,
    responses={404: {"model": ErrorResponse}},
)
async def analyze_stock(
    code: str,
    days: int = Query(100, ge=30, le=500, description="分析天数"),
    db: Database = Depends(get_db),
    quote_service: QuoteService = Depends(get_quote_service),
):
    """技术分析"""
    try:
        df = await quote_service.get_daily(code)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"无数据: {code}")

        analyzer = TechnicalAnalyzer(df)
        analyzer.add_all()
        result = analyzer.get_signals()

        return AnalysisResponse(code=code, **result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"技术分析失败: {code}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"技术分析失败: {str(e)}")


@app.get("/screen", response_model=ScreenResponse)
async def screen_stocks(
    factors: Optional[str] = Query(None, description="因子列表，逗号分隔"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    quote_service: QuoteService = Depends(get_quote_service),
):
    """选股"""
    try:
        screener = StockScreener(quote_service)

        factor_list = None
        if factors:
            factor_list = [f.strip() for f in factors.split(",")]

        results = await screener.screen(factors=factor_list, limit=limit)

        return ScreenResponse(
            total=len(results),
            results=[
                ScreenResult(
                    code=r.code,
                    name=r.name,
                    score=r.score,
                    matched_factors=r.matched_factors,
                    factor_scores=r.factor_scores,
                    screened_at=r.screened_at.isoformat(),
                )
                for r in results
            ],
        )
    except Exception as e:
        logger.error("选股失败", exc_info=True)
        raise HTTPException(status_code=500, detail=f"选股失败: {str(e)}")


@app.get("/backtest/{code}", response_model=BacktestResponse)
async def backtest_stock(
    code: str,
    strategy: str = Query("ma_cross", description="策略名称"),
    capital: float = Query(100000, ge=10000, description="初始资金"),
    quote_service: QuoteService = Depends(get_quote_service),
):
    """回测"""
    try:
        df = await quote_service.get_daily(code, save=False)

        if df.empty:
            raise HTTPException(status_code=404, detail=f"无数据: {code}")

        engine = BacktestEngine()
        result = engine.run(
            df,
            strategy_name=strategy,
            initial_capital=capital,
        )
        result.code = code

        return BacktestResponse(**result.to_dict())
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"回测失败: {code}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"回测失败: {str(e)}")


@app.get("/recommend")
async def get_recommendations(
    user_id: str = Query("default", description="用户ID"),
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    style: Optional[str] = Query(None, description="交易风格覆盖"),
    risk: Optional[str] = Query(None, description="风险等级覆盖"),
    quote_service: QuoteService = Depends(get_quote_service),
):
    """个性化推荐"""
    try:
        from ..recommend import Recommender
        from ..stock_picker import StockScreener

        screener = StockScreener(quote_service)
        recommender = Recommender(screener)

        options = {}
        if style:
            options["trading_style"] = style
        if risk:
            options["risk_level"] = risk

        result = await recommender.handle_recommend(
            user_id=user_id,
            limit=limit,
            options=options if options else None,
        )

        return result
    except Exception as e:
        logger.error("推荐失败", exc_info=True)
        raise HTTPException(status_code=500, detail=f"推荐失败: {str(e)}")


@app.get("/config")
async def get_config(
    user_id: str = Query("default", description="用户ID"),
):
    """获取用户配置"""
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
        logger.error("获取配置失败", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@app.put("/config")
async def update_config(
    user_id: str = Query("default", description="用户ID"),
    trading_style: Optional[str] = Query(None, description="交易风格"),
    risk_level: Optional[str] = Query(None, description="风险等级"),
    max_positions: Optional[int] = Query(None, description="最大持仓数"),
    position_size: Optional[float] = Query(None, description="单只仓位比例"),
):
    """更新用户配置"""
    try:
        from ..config import TradingStyle, RiskLevel

        config_manager = ConfigManager()

        updates = {}
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
        logger.error("更新配置失败", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@app.get("/strategies")
async def list_strategies():
    """列出所有可用策略"""
    from ..backtest.strategies import list_strategies

    return {"strategies": list_strategies()}


@app.get("/factors")
async def list_factors():
    """列出所有可用因子"""
    from ..stock_picker.factors import FACTORS, FactorType

    factors_by_type = {}
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
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
    }


# 启动命令: uvicorn astock.api:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
