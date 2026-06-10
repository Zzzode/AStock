"""Extended factor definitions - financial/sentiment/capital flow/technical factors"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class FactorType(Enum):
    """Factor type"""

    VALUATION = "valuation"  # Valuation factors
    MOMENTUM = "momentum"  # Momentum factors
    QUALITY = "quality"  # Quality factors
    VOLATILITY = "volatility"  # Volatility factors
    FINANCIAL = "financial"  # Financial factors
    SENTIMENT = "sentiment"  # Sentiment factors
    CAPITAL_FLOW = "capital_flow"  # Capital flow factors
    TECHNICAL = "technical"  # Technical factors


@dataclass
class Factor:
    """Factor definition"""

    key: str  # Factor key
    name: str  # Factor name
    type: FactorType  # Factor type
    description: str  # Factor description
    field: str  # Data field
    operator: str  # Comparison operator (lt, le, gt, ge, eq, cross_up, cross_down)
    threshold: Any  # Threshold value
    weight: float = 1.0  # Weight
    value_extractor: Optional[str] = None  # Value extractor


# Predefined factors
FACTORS: dict[str, Factor] = {
    # ============ Valuation factors ============
    "pe_low": Factor(
        key="pe_low",
        name="Low PE",
        type=FactorType.VALUATION,
        description="PE ratio below 30x",
        field="pe",
        operator="lt",
        threshold=30,
        weight=1.0,
    ),
    "pb_low": Factor(
        key="pb_low",
        name="Low PB",
        type=FactorType.VALUATION,
        description="PB ratio below 3x",
        field="pb",
        operator="lt",
        threshold=3,
        weight=1.0,
    ),
    "pe_reasonable": Factor(
        key="pe_reasonable",
        name="Reasonable PE",
        type=FactorType.VALUATION,
        description="PE ratio between 10-30x",
        field="pe",
        operator="ge",
        threshold=10,
        weight=0.8,
    ),
    # High dividend valuation factor
    "pe_very_low": Factor(
        key="pe_very_low",
        name="Very Low PE",
        type=FactorType.VALUATION,
        description="PE ratio below 15x (high dividend characteristic)",
        field="pe",
        operator="lt",
        threshold=15,
        weight=1.5,
    ),
    "pb_very_low": Factor(
        key="pb_very_low",
        name="Very Low PB",
        type=FactorType.VALUATION,
        description="PB ratio below 1.5x (high dividend characteristic)",
        field="pb",
        operator="lt",
        threshold=1.5,
        weight=1.2,
    ),
    "pe_positive": Factor(
        key="pe_positive",
        name="Positive PE",
        type=FactorType.VALUATION,
        description="PE ratio above 0 (profitable company)",
        field="pe",
        operator="gt",
        threshold=0,
        weight=0.5,
    ),
    # ============ Momentum factors ============
    "ma20_above": Factor(
        key="ma20_above",
        name="Above MA20",
        type=FactorType.MOMENTUM,
        description="Close price above 20-day moving average",
        field="close",
        operator="gt",
        threshold="ma20",
        weight=1.5,
    ),
    "ma5_cross_ma20": Factor(
        key="ma5_cross_ma20",
        name="MA5 Golden Cross MA20",
        type=FactorType.MOMENTUM,
        description="5-day MA crosses above 20-day MA",
        field="ma5",
        operator="cross_up",
        threshold="ma20",
        weight=2.0,
    ),
    "ma10_cross_ma30": Factor(
        key="ma10_cross_ma30",
        name="MA10 Golden Cross MA30",
        type=FactorType.MOMENTUM,
        description="10-day MA crosses above 30-day MA",
        field="ma10",
        operator="cross_up",
        threshold="ma30",
        weight=1.8,
    ),
    "price_above_ma5": Factor(
        key="price_above_ma5",
        name="Above MA5",
        type=FactorType.MOMENTUM,
        description="Close price above 5-day moving average",
        field="close",
        operator="gt",
        threshold="ma5",
        weight=1.0,
    ),
    "ma_trend_up": Factor(
        key="ma_trend_up",
        name="Bullish MA Alignment",
        type=FactorType.MOMENTUM,
        description="MA5 > MA10 > MA20 bullish alignment",
        field="ma5",
        operator="gt",
        threshold="ma10",
        weight=2.5,
    ),
    # ============ Quality factors ============
    "high_volume": Factor(
        key="high_volume",
        name="High Volume",
        type=FactorType.QUALITY,
        description="Volume greater than 2x of 5-day average volume",
        field="volume",
        operator="gt",
        threshold="vol_ma5_2x",
        weight=1.0,
    ),
    "volume_steady": Factor(
        key="volume_steady",
        name="Steady Volume",
        type=FactorType.QUALITY,
        description="Volume near 5-day average volume",
        field="volume",
        operator="ge",
        threshold="vol_ma5",
        weight=0.8,
    ),
    # ============ Volatility factors ============
    "low_volatility": Factor(
        key="low_volatility",
        name="Low Volatility",
        type=FactorType.VOLATILITY,
        description="20-day volatility below 3%",
        field="volatility_20",
        operator="lt",
        threshold=0.03,
        weight=1.0,
    ),
    "medium_volatility": Factor(
        key="medium_volatility",
        name="Medium Volatility",
        type=FactorType.VOLATILITY,
        description="20-day volatility between 3%-5%",
        field="volatility_20",
        operator="ge",
        threshold=0.03,
        weight=0.7,
    ),
    # ============ Financial factors ============
    "roe_high": Factor(
        key="roe_high",
        name="High ROE",
        type=FactorType.FINANCIAL,
        description="Return on equity above 15%",
        field="roe",
        operator="gt",
        threshold=0.15,
        weight=2.0,
    ),
    "profit_growth": Factor(
        key="profit_growth",
        name="Profit Growth",
        type=FactorType.FINANCIAL,
        description="Net profit growth rate above 20%",
        field="profit_growth_rate",
        operator="gt",
        threshold=0.20,
        weight=1.8,
    ),
    "revenue_growth": Factor(
        key="revenue_growth",
        name="Revenue Growth",
        type=FactorType.FINANCIAL,
        description="Revenue growth rate above 15%",
        field="revenue_growth_rate",
        operator="gt",
        threshold=0.15,
        weight=1.5,
    ),
    "debt_ratio_low": Factor(
        key="debt_ratio_low",
        name="Low Debt Ratio",
        type=FactorType.FINANCIAL,
        description="Debt-to-asset ratio below 50%",
        field="debt_ratio",
        operator="lt",
        threshold=0.50,
        weight=1.2,
    ),
    "current_ratio_good": Factor(
        key="current_ratio_good",
        name="Healthy Current Ratio",
        type=FactorType.FINANCIAL,
        description="Current ratio above 1.5",
        field="current_ratio",
        operator="gt",
        threshold=1.5,
        weight=1.0,
    ),
    # ============ Sentiment factors ============
    "rsi_oversold": Factor(
        key="rsi_oversold",
        name="RSI Oversold",
        type=FactorType.SENTIMENT,
        description="RSI6 below 30, oversold zone",
        field="rsi6",
        operator="lt",
        threshold=30,
        weight=1.5,
    ),
    "rsi_overbought": Factor(
        key="rsi_overbought",
        name="RSI Overbought",
        type=FactorType.SENTIMENT,
        description="RSI6 above 70, overbought zone",
        field="rsi6",
        operator="gt",
        threshold=70,
        weight=-1.0,  # Negative weight indicates risk
    ),
    "rsi_neutral": Factor(
        key="rsi_neutral",
        name="RSI Neutral",
        type=FactorType.SENTIMENT,
        description="RSI between 30-70, neutral sentiment",
        field="rsi6",
        operator="ge",
        threshold=30,
        weight=0.5,
    ),
    "kdj_oversold": Factor(
        key="kdj_oversold",
        name="KDJ Oversold",
        type=FactorType.SENTIMENT,
        description="KDJ J-value below 20, oversold zone",
        field="kdj_j",
        operator="lt",
        threshold=20,
        weight=1.5,
    ),
    "kdj_overbought": Factor(
        key="kdj_overbought",
        name="KDJ Overbought",
        type=FactorType.SENTIMENT,
        description="KDJ J-value above 80, overbought zone",
        field="kdj_j",
        operator="gt",
        threshold=80,
        weight=-1.0,
    ),
    # ============ Capital flow factors ============
    "net_inflow": Factor(
        key="net_inflow",
        name="Main Force Net Inflow",
        type=FactorType.CAPITAL_FLOW,
        description="Main force capital net inflow",
        field="main_net_inflow",
        operator="gt",
        threshold=0,
        weight=2.0,
    ),
    "large_inflow": Factor(
        key="large_inflow",
        name="Large Order Net Inflow",
        type=FactorType.CAPITAL_FLOW,
        description="Large order net inflow above 0",
        field="large_net_inflow",
        operator="gt",
        threshold=0,
        weight=1.5,
    ),
    "north_inflow": Factor(
        key="north_inflow",
        name="Northbound Capital Inflow",
        type=FactorType.CAPITAL_FLOW,
        description="Northbound capital net inflow",
        field="north_net_inflow",
        operator="gt",
        threshold=0,
        weight=1.8,
    ),
    # ============ Technical factors ============
    "macd_golden_cross": Factor(
        key="macd_golden_cross",
        name="MACD Golden Cross",
        type=FactorType.TECHNICAL,
        description="MACD histogram turns from negative to positive",
        field="macd_hist",
        operator="gt",
        threshold=0,
        weight=2.0,
    ),
    "macd_dead_cross": Factor(
        key="macd_dead_cross",
        name="MACD Death Cross",
        type=FactorType.TECHNICAL,
        description="MACD histogram turns from positive to negative",
        field="macd_hist",
        operator="lt",
        threshold=0,
        weight=-1.5,
    ),
    "macd_above_zero": Factor(
        key="macd_above_zero",
        name="MACD Above Zero",
        type=FactorType.TECHNICAL,
        description="MACD running above zero line",
        field="macd",
        operator="gt",
        threshold=0,
        weight=1.2,
    ),
    "kdj_golden_cross": Factor(
        key="kdj_golden_cross",
        name="KDJ Golden Cross",
        type=FactorType.TECHNICAL,
        description="K line crosses above D line",
        field="kdj_k",
        operator="cross_up",
        threshold="kdj_d",
        weight=1.8,
    ),
    "boll_lower_support": Factor(
        key="boll_lower_support",
        name="Bollinger Lower Band Support",
        type=FactorType.TECHNICAL,
        description="Price touches Bollinger lower band",
        field="close",
        operator="le",
        threshold="boll_lower",
        weight=1.5,
    ),
    "boll_upper_pressure": Factor(
        key="boll_upper_pressure",
        name="Bollinger Upper Band Resistance",
        type=FactorType.TECHNICAL,
        description="Price touches Bollinger upper band",
        field="close",
        operator="ge",
        threshold="boll_upper",
        weight=-0.5,
    ),
    "breakout_high": Factor(
        key="breakout_high",
        name="Breakout High",
        type=FactorType.TECHNICAL,
        description="Price breaks 20-day high",
        field="close",
        operator="ge",
        threshold="high_20d",
        weight=2.5,
    ),
}


def get_factor(key: str) -> Optional[Factor]:
    """Get a factor by key"""
    return FACTORS.get(key)


def get_factors_by_type(factor_type: FactorType) -> list[Factor]:
    """Get factors by type"""
    return [f for f in FACTORS.values() if f.type == factor_type]


def get_all_factor_types() -> list[FactorType]:
    """Get all factor types"""
    return list(FactorType)


def get_factor_keys_by_type(factor_type: FactorType) -> list[str]:
    """Get factor key list by type"""
    return [k for k, f in FACTORS.items() if f.type == factor_type]


# ============ Preset factor combinations ============

# High dividend screening factor combination (reasonable valuation + growth)
HIGH_DIVIDEND_FACTORS = [
    "pe_positive",      # Profitable company
    "pe_very_low",      # PE < 15, low valuation
    "pb_very_low",      # PB < 1.5, low valuation
    "ma20_above",       # Above 20-day MA, uptrend
    "macd_above_zero",  # MACD above zero line
    "volume_steady",    # Steady volume
]

# Value investing factor combination
VALUE_INVEST_FACTORS = [
    "pe_positive",
    "pe_very_low",
    "pb_very_low",
    "low_volatility",
    "ma_trend_up",
]

# Growth momentum factor combination
GROWTH_MOMENTUM_FACTORS = [
    "ma5_cross_ma20",
    "macd_golden_cross",
    "high_volume",
    "ma_trend_up",
]


def get_preset_factors(preset_name: str) -> list[str]:
    """Get preset factor combination

    Args:
        preset_name: Preset name (high_dividend, value, growth)

    Returns:
        List of factor keys
    """
    presets = {
        "high_dividend": HIGH_DIVIDEND_FACTORS,
        "value": VALUE_INVEST_FACTORS,
        "growth": GROWTH_MOMENTUM_FACTORS,
    }
    return presets.get(preset_name, [])
