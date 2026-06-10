"""Personalized candidate pool service

Python only collects candidate data based on user configuration; it does not output
recommendation conclusions. Final ranking, selection, and suggestions are handled by the Agent.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..config import UserConfig, TradingStyle, RiskLevel, ConfigManager
from ..stock_picker import StockScreener, ScreenResult, FactorType
from ..data import IndustryService, StockIndustry
from ..stock_picker.factors import get_factors_by_type


@dataclass
class RecommendCandidate:
    """Recommendation candidate data"""

    code: str
    name: Optional[str]
    matched_factors: list[str]
    matched_factor_count: int
    factor_checks: dict[str, dict[str, Any]]
    industry: Optional[str]
    industry_change: Optional[float]
    data: dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)


@dataclass
class RecommendResult:
    """Recommendation request result"""

    success: bool
    candidates: list[RecommendCandidate] = field(default_factory=list)
    total: int = 0
    config_used: Optional[dict[str, Any]] = None
    selection_context: dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    generated_at: datetime = field(default_factory=datetime.now)


class Recommender:
    """Personalized candidate pool builder"""

    STYLE_FACTOR_ORDER: dict[TradingStyle, list[FactorType]] = {
        TradingStyle.DAY_TRADING: [
            FactorType.MOMENTUM,
            FactorType.VOLATILITY,
            FactorType.QUALITY,
            FactorType.VALUATION,
        ],
        TradingStyle.SWING: [
            FactorType.MOMENTUM,
            FactorType.QUALITY,
            FactorType.VOLATILITY,
            FactorType.VALUATION,
        ],
        TradingStyle.TREND_FOLLOWING: [
            FactorType.MOMENTUM,
            FactorType.QUALITY,
            FactorType.VALUATION,
            FactorType.VOLATILITY,
        ],
        TradingStyle.VALUE_INVESTING: [
            FactorType.VALUATION,
            FactorType.QUALITY,
            FactorType.VOLATILITY,
            FactorType.MOMENTUM,
        ],
    }

    RISK_FACTOR_OVERLAY: dict[RiskLevel, list[FactorType]] = {
        RiskLevel.CONSERVATIVE: [FactorType.VALUATION, FactorType.QUALITY],
        RiskLevel.MODERATE: [],
        RiskLevel.AGGRESSIVE: [FactorType.MOMENTUM, FactorType.VOLATILITY],
    }

    def __init__(
        self,
        screener: StockScreener,
        industry_service: Optional[IndustryService] = None,
    ):
        self.screener = screener
        self.industry_service = industry_service

    async def build_candidate_pool(
        self,
        config: UserConfig,
        limit: int = 10,
    ) -> tuple[list[RecommendCandidate], dict[str, Any]]:
        """Build candidate pool without recommendation ranking"""
        factors = self._get_factors_for_style(config.trading_style)
        adjusted_factors = self._adjust_factors_for_risk(factors, config.risk_level)

        screen_results = await self.screener.screen(
            factors=adjusted_factors,
            limit=max(limit * 5, limit),
        )

        filtered_results = await self._filter_by_preferences(screen_results, config)
        candidates = []
        for result in filtered_results[:limit]:
            candidates.append(await self._create_candidate(result))

        context = {
            "style": config.trading_style.value,
            "risk": config.risk_level.value,
            "screen_factor_keys": adjusted_factors,
            "price_range": {
                "min": config.min_price,
                "max": config.max_price,
            },
            "preferred_sectors": list(config.preferred_sectors or []),
            "excluded_sectors": list(config.excluded_sectors or []),
            "prefilter_candidate_count": len(screen_results),
            "postfilter_candidate_count": len(filtered_results),
            "returned_candidate_count": len(candidates),
        }
        return candidates, context

    def _get_factors_for_style(self, style: TradingStyle) -> list[str]:
        """Get factor list based on trading style"""
        factor_types = self.STYLE_FACTOR_ORDER.get(style, [])
        factor_keys: list[str] = []

        for factor_type in factor_types:
            factor_keys.extend(f.key for f in get_factors_by_type(factor_type))

        return factor_keys

    def _adjust_factors_for_risk(
        self,
        factors: list[str],
        risk: RiskLevel,
    ) -> list[str]:
        """Reorder factor list based on risk preference without scoring adjustment"""
        overlays = self.RISK_FACTOR_OVERLAY.get(risk, [])
        if not overlays:
            return factors

        overlay_keys: list[str] = []
        for factor_type in overlays:
            overlay_keys.extend(f.key for f in get_factors_by_type(factor_type))

        adjusted: list[str] = []
        for key in overlay_keys + factors:
            if key not in adjusted:
                adjusted.append(key)
        return adjusted

    async def _filter_by_preferences(
        self,
        results: list[ScreenResult],
        config: UserConfig,
    ) -> list[ScreenResult]:
        """Apply deterministic filtering based on user explicit preferences"""
        filtered = []

        for result in results:
            price = result.data.get("close", 0)
            if config.min_price is not None and price < config.min_price:
                continue
            if config.max_price is not None and price > config.max_price:
                continue

            if self.industry_service and (
                config.preferred_sectors or config.excluded_sectors
            ):
                stock_industry = await self._get_stock_industry(result.code)
                if stock_industry:
                    if (
                        config.preferred_sectors
                        and stock_industry.industry not in config.preferred_sectors
                    ):
                        continue
                    if (
                        config.excluded_sectors
                        and stock_industry.industry in config.excluded_sectors
                    ):
                        continue

            filtered.append(result)

        return filtered

    async def _get_stock_industry(self, code: str) -> Optional[StockIndustry]:
        if not self.industry_service:
            return None
        return await self.industry_service.get_stock_industry(code)

    async def _create_candidate(self, result: ScreenResult) -> RecommendCandidate:
        """Create candidate data object"""
        industry = None
        industry_change = None
        if self.industry_service:
            stock_industry = await self._get_stock_industry(result.code)
            if stock_industry:
                industry = stock_industry.industry
                industry_change = stock_industry.industry_change

        return RecommendCandidate(
            code=result.code,
            name=result.name,
            matched_factors=result.matched_factors,
            matched_factor_count=result.matched_factor_count,
            factor_checks=result.factor_checks,
            industry=industry,
            industry_change=industry_change,
            data=result.data,
            collected_at=datetime.now(),
        )

    async def handle_recommend(
        self,
        config: Optional[UserConfig] = None,
        user_id: str = "default",
        limit: int = 10,
        options: Optional[dict[str, Any]] = None,
    ) -> RecommendResult:
        """Handle recommendation request and return candidate pool data packet"""
        try:
            if config is None:
                config_manager = ConfigManager()
                config = config_manager.load(user_id)

            if options:
                config = self._apply_options(config, options)

            candidates, selection_context = await self.build_candidate_pool(config, limit)

            return RecommendResult(
                success=True,
                candidates=candidates,
                total=len(candidates),
                config_used={
                    "user_id": config.user_id,
                    "trading_style": config.trading_style.value,
                    "risk_level": config.risk_level.value,
                    "min_price": config.min_price,
                    "max_price": config.max_price,
                    "preferred_sectors": list(config.preferred_sectors or []),
                    "excluded_sectors": list(config.excluded_sectors or []),
                },
                selection_context=selection_context,
            )

        except Exception as e:
            return RecommendResult(success=False, error=str(e))

    def _apply_options(self, config: UserConfig, options: dict[str, Any]) -> UserConfig:
        """Apply option overrides to configuration"""
        config_data = config.model_dump()

        if "trading_style" in options:
            style_str = options["trading_style"]
            for style in TradingStyle:
                if style.value == style_str:
                    config_data["trading_style"] = style
                    break

        if "risk_level" in options:
            risk_str = options["risk_level"]
            for risk in RiskLevel:
                if risk.value == risk_str:
                    config_data["risk_level"] = risk
                    break

        if "min_price" in options:
            config_data["min_price"] = options["min_price"]
        if "max_price" in options:
            config_data["max_price"] = options["max_price"]

        if "sectors" in options:
            config_data["preferred_sectors"] = options["sectors"]

        return UserConfig(**config_data)
