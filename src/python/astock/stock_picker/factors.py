"""Screening factors for valuation, quality, volatility, and market structure."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class FactorType(Enum):
    """Factor type"""

    VALUATION = "valuation"  # Valuation factors
    MOMENTUM = "momentum"  # Reserved for non-indicator price-structure research
    QUALITY = "quality"  # Quality factors
    VOLATILITY = "volatility"  # Volatility factors
    FINANCIAL = "financial"  # Financial factors
    CAPITAL_FLOW = "capital_flow"  # Capital flow factors
    MARKET_STRUCTURE = "market_structure"  # Price and liquidity structure factors


@dataclass
class Factor:
    """Factor definition"""

    key: str  # Factor key
    name: str  # Factor name
    type: FactorType  # Factor type
    description: str  # Factor description
    field: str  # Data field
    operator: str  # Comparison operator (lt, le, gt, ge, eq)
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
    # ============ Quality factors ============
    "high_volume": Factor(
        key="high_volume",
        name="Active Turnover",
        type=FactorType.QUALITY,
        description="Turnover rate above 2%",
        field="turnover_rate",
        operator="gt",
        threshold=2.0,
        weight=1.0,
    ),
    "volume_steady": Factor(
        key="volume_steady",
        name="Liquid Trading",
        type=FactorType.QUALITY,
        description="Daily traded value above 50 million",
        field="amount",
        operator="ge",
        threshold=50_000_000,
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
    # ============ Market-structure factors ============
    "range_expansion": Factor(
        key="range_expansion",
        name="Wide Daily Range",
        type=FactorType.MARKET_STRUCTURE,
        description="Intraday range is at least 5% of the closing price",
        field="daily_range_pct",
        operator="ge",
        threshold=0.05,
        weight=1.0,
    ),
    "close_near_high": Factor(
        key="close_near_high",
        name="Close Near Session High",
        type=FactorType.MARKET_STRUCTURE,
        description="Close is within 2% of the session high",
        field="close_to_high_pct",
        operator="ge",
        threshold=0.98,
        weight=1.0,
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
    "volume_steady",    # Minimum liquidity
]

# Value investing factor combination
VALUE_INVEST_FACTORS = [
    "pe_positive",
    "pe_very_low",
    "pb_very_low",
    "low_volatility",
]

# Growth momentum factor combination
GROWTH_MOMENTUM_FACTORS = [
    "high_volume",
    "range_expansion",
    "close_near_high",
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
