"""个性化推荐服务"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

from ..config import UserConfig, TradingStyle, RiskLevel
from ..stock_picker import StockScreener, ScreenResult, FactorType


@dataclass
class Recommendation:
    """推荐结果"""
    code: str                           # 股票代码
    name: Optional[str]                 # 股票名称
    score: float                        # 综合得分
    matched_factors: list[str]          # 匹配的因子列表
    factor_scores: dict[str, float]     # 各因子得分
    suggested_strategies: list[str]     # 推荐策略
    risk_level: str                     # 风险等级
    style_match: float                  # 风格匹配度 (0-1)
    data: dict[str, Any]                # 原始数据
    recommended_at: datetime            # 推荐时间


class Recommender:
    """个性化推荐器"""

    # 交易风格对应的因子类型权重
    STYLE_FACTOR_WEIGHTS: dict[TradingStyle, dict[FactorType, float]] = {
        TradingStyle.DAY_TRADING: {
            FactorType.MOMENTUM: 2.0,
            FactorType.VOLATILITY: 1.5,
            FactorType.QUALITY: 1.0,
            FactorType.VALUATION: 0.5,
        },
        TradingStyle.SWING: {
            FactorType.MOMENTUM: 1.5,
            FactorType.QUALITY: 1.5,
            FactorType.VOLATILITY: 1.0,
            FactorType.VALUATION: 1.0,
        },
        TradingStyle.TREND_FOLLOWING: {
            FactorType.MOMENTUM: 2.0,
            FactorType.QUALITY: 1.5,
            FactorType.VALUATION: 1.0,
            FactorType.VOLATILITY: 0.8,
        },
        TradingStyle.VALUE_INVESTING: {
            FactorType.VALUATION: 2.0,
            FactorType.QUALITY: 1.5,
            FactorType.VOLATILITY: 0.5,
            FactorType.MOMENTUM: 0.5,
        },
    }

    # 交易风格对应的推荐策略
    STYLE_STRATEGIES: dict[TradingStyle, list[str]] = {
        TradingStyle.DAY_TRADING: [
            "突破策略",
            "量价配合",
            "短线波段",
        ],
        TradingStyle.SWING: [
            "波段交易",
            "回调买入",
            "趋势跟随",
        ],
        TradingStyle.TREND_FOLLOWING: [
            "趋势跟踪",
            "均线策略",
            "动量策略",
        ],
        TradingStyle.VALUE_INVESTING: [
            "价值投资",
            "定投策略",
            "分红策略",
        ],
    }

    # 风险等级对应的因子调整
    RISK_FACTOR_ADJUSTMENTS: dict[RiskLevel, dict[str, float]] = {
        RiskLevel.CONSERVATIVE: {
            "volatility_penalty": 0.5,      # 高波动惩罚
            "valuation_bonus": 0.3,         # 估值奖励
            "min_score_multiplier": 0.8,    # 最低得分倍率
        },
        RiskLevel.MODERATE: {
            "volatility_penalty": 0.2,
            "valuation_bonus": 0.1,
            "min_score_multiplier": 1.0,
        },
        RiskLevel.AGGRESSIVE: {
            "volatility_penalty": 0.0,
            "valuation_bonus": 0.0,
            "min_score_multiplier": 1.2,
        },
    }

    def __init__(self, screener: StockScreener):
        """初始化推荐器

        Args:
            screener: 股票选股器实例
        """
        self.screener = screener

    async def recommend(
        self,
        config: UserConfig,
        limit: int = 10
    ) -> list[Recommendation]:
        """生成个性化推荐

        Args:
            config: 用户配置
            limit: 返回数量限制

        Returns:
            推荐结果列表，按得分降序排列
        """
        # 1. 根据交易风格获取因子
        factors = self._get_factors_for_style(config.trading_style)

        # 2. 根据风险偏好调整因子
        adjusted_factors = self._adjust_factors_for_risk(
            factors,
            config.risk_level
        )

        # 3. 执行选股
        screen_results = await self.screener.screen(
            factors=adjusted_factors,
            limit=limit * 3,  # 获取更多结果以便过滤
        )

        # 4. 根据用户偏好过滤
        filtered_results = self._filter_by_preferences(screen_results, config)

        # 5. 生成推荐
        recommendations = []
        for result in filtered_results[:limit]:
            recommendation = self._create_recommendation(
                result,
                config.trading_style,
                config.risk_level
            )
            recommendations.append(recommendation)

        return recommendations

    def _get_factors_for_style(self, style: TradingStyle) -> list[str]:
        """根据交易风格获取因子

        Args:
            style: 交易风格

        Returns:
            因子键名列表
        """
        # 获取该风格的因子类型权重
        weights = self.STYLE_FACTOR_WEIGHTS.get(style, {})

        # 获取所有因子并按权重排序
        from ..stock_picker.factors import FACTORS, get_factors_by_type

        factor_keys = []
        for factor_type, weight in sorted(
            weights.items(),
            key=lambda x: x[1],
            reverse=True
        ):
            factors = get_factors_by_type(factor_type)
            factor_keys.extend([f.key for f in factors])

        # 如果没有匹配的因子，返回所有因子
        return factor_keys if factor_keys else list(FACTORS.keys())

    def _adjust_factors_for_risk(
        self,
        factors: list[str],
        risk: RiskLevel
    ) -> list[str]:
        """根据风险偏好调整因子

        Args:
            factors: 因子键名列表
            risk: 风险等级

        Returns:
            调整后的因子键名列表
        """
        adjustments = self.RISK_FACTOR_ADJUSTMENTS.get(risk, {})

        # 根据风险等级调整因子列表
        # 保守型：增加估值因子，减少波动因子
        # 激进型：增加动量因子，减少估值因子
        from ..stock_picker.factors import FACTORS

        adjusted = list(factors)

        if risk == RiskLevel.CONSERVATIVE:
            # 保守型：优先估值和质量因子
            valuation_factors = [k for k, f in FACTORS.items()
                               if f.type == FactorType.VALUATION]
            quality_factors = [k for k, f in FACTORS.items()
                              if f.type == FactorType.QUALITY]
            # 将估值和质量因子放在前面
            for f in valuation_factors + quality_factors:
                if f in adjusted:
                    adjusted.remove(f)
                    adjusted.insert(0, f)

        elif risk == RiskLevel.AGGRESSIVE:
            # 激进型：优先动量和波动因子
            momentum_factors = [k for k, f in FACTORS.items()
                               if f.type == FactorType.MOMENTUM]
            volatility_factors = [k for k, f in FACTORS.items()
                                  if f.type == FactorType.VOLATILITY]
            # 将动量和波动因子放在前面
            for f in momentum_factors + volatility_factors:
                if f in adjusted:
                    adjusted.remove(f)
                    adjusted.insert(0, f)

        return adjusted

    def _filter_by_preferences(
        self,
        results: list[ScreenResult],
        config: UserConfig
    ) -> list[ScreenResult]:
        """根据用户偏好过滤

        Args:
            results: 选股结果列表
            config: 用户配置

        Returns:
            过滤后的结果列表
        """
        filtered = []

        for result in results:
            # 价格过滤
            price = result.data.get("close", 0)
            if config.min_price is not None and price < config.min_price:
                continue
            if config.max_price is not None and price > config.max_price:
                continue

            # 行业过滤 (这里需要行业数据，暂时跳过)
            # TODO: 获取股票行业信息后实现

            filtered.append(result)

        return filtered

    def _suggest_strategies(
        self,
        code: str,
        style: TradingStyle
    ) -> list[str]:
        """推荐策略

        Args:
            code: 股票代码
            style: 交易风格

        Returns:
            推荐策略列表
        """
        return self.STYLE_STRATEGIES.get(style, ["趋势跟踪"])

    def _create_recommendation(
        self,
        result: ScreenResult,
        style: TradingStyle,
        risk: RiskLevel
    ) -> Recommendation:
        """创建推荐结果

        Args:
            result: 选股结果
            style: 交易风格
            risk: 风险等级

        Returns:
            推荐结果
        """
        # 计算风格匹配度
        style_match = self._calculate_style_match(result, style)

        # 获取推荐策略
        strategies = self._suggest_strategies(result.code, style)

        return Recommendation(
            code=result.code,
            name=result.name,
            score=result.score,
            matched_factors=result.matched_factors,
            factor_scores=result.factor_scores,
            suggested_strategies=strategies,
            risk_level=risk.value,
            style_match=style_match,
            data=result.data,
            recommended_at=datetime.now()
        )

    def _calculate_style_match(
        self,
        result: ScreenResult,
        style: TradingStyle
    ) -> float:
        """计算风格匹配度

        Args:
            result: 选股结果
            style: 交易风格

        Returns:
            匹配度 (0-1)
        """
        from ..stock_picker.factors import FACTORS

        # 获取该风格对应的因子类型权重
        weights = self.STYLE_FACTOR_WEIGHTS.get(style, {})

        if not weights:
            return 0.5  # 默认中等匹配度

        # 计算匹配度
        total_weight = 0.0
        matched_weight = 0.0

        for factor_key in result.matched_factors:
            factor = FACTORS.get(factor_key)
            if factor:
                type_weight = weights.get(factor.type, 1.0)
                total_weight += type_weight
                matched_weight += type_weight

        # 考虑所有因子的权重
        for factor in FACTORS.values():
            type_weight = weights.get(factor.type, 1.0)
            total_weight += type_weight * 0.5  # 未匹配因子也计入总权重

        if total_weight == 0:
            return 0.5

        return min(1.0, matched_weight / total_weight)
