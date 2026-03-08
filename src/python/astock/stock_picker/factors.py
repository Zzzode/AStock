"""扩展因子定义 - 财务/情绪/资金流向/技术因子"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class FactorType(Enum):
    """因子类型"""

    VALUATION = "valuation"  # 估值因子
    MOMENTUM = "momentum"  # 动量因子
    QUALITY = "quality"  # 质量因子
    VOLATILITY = "volatility"  # 波动因子
    FINANCIAL = "financial"  # 财务因子
    SENTIMENT = "sentiment"  # 情绪因子
    CAPITAL_FLOW = "capital_flow"  # 资金流向因子
    TECHNICAL = "technical"  # 技术因子


@dataclass
class Factor:
    """因子定义"""

    key: str  # 因子键名
    name: str  # 因子名称
    type: FactorType  # 因子类型
    description: str  # 因子描述
    field: str  # 数据字段
    operator: str  # 比较操作符 (lt, le, gt, ge, eq, cross_up, cross_down)
    threshold: Any  # 阈值
    weight: float = 1.0  # 权重
    value_extractor: Optional[str] = None  # 值提取器


# 预定义因子
FACTORS: dict[str, Factor] = {
    # ============ 估值因子 ============
    "pe_low": Factor(
        key="pe_low",
        name="低市盈率",
        type=FactorType.VALUATION,
        description="市盈率小于30倍",
        field="pe",
        operator="lt",
        threshold=30,
        weight=1.0,
    ),
    "pb_low": Factor(
        key="pb_low",
        name="低市净率",
        type=FactorType.VALUATION,
        description="市净率小于3倍",
        field="pb",
        operator="lt",
        threshold=3,
        weight=1.0,
    ),
    "pe_reasonable": Factor(
        key="pe_reasonable",
        name="合理市盈率",
        type=FactorType.VALUATION,
        description="市盈率在10-30倍之间",
        field="pe",
        operator="ge",
        threshold=10,
        weight=0.8,
    ),
    # ============ 动量因子 ============
    "ma20_above": Factor(
        key="ma20_above",
        name="站上20日线",
        type=FactorType.MOMENTUM,
        description="收盘价站上20日均线",
        field="close",
        operator="gt",
        threshold="ma20",
        weight=1.5,
    ),
    "ma5_cross_ma20": Factor(
        key="ma5_cross_ma20",
        name="MA5金叉MA20",
        type=FactorType.MOMENTUM,
        description="5日均线上穿20日均线",
        field="ma5",
        operator="cross_up",
        threshold="ma20",
        weight=2.0,
    ),
    "ma10_cross_ma30": Factor(
        key="ma10_cross_ma30",
        name="MA10金叉MA30",
        type=FactorType.MOMENTUM,
        description="10日均线上穿30日均线",
        field="ma10",
        operator="cross_up",
        threshold="ma30",
        weight=1.8,
    ),
    "price_above_ma5": Factor(
        key="price_above_ma5",
        name="站上5日线",
        type=FactorType.MOMENTUM,
        description="收盘价站上5日均线",
        field="close",
        operator="gt",
        threshold="ma5",
        weight=1.0,
    ),
    "ma_trend_up": Factor(
        key="ma_trend_up",
        name="均线多头排列",
        type=FactorType.MOMENTUM,
        description="MA5>MA10>MA20 多头排列",
        field="ma5",
        operator="gt",
        threshold="ma10",
        weight=2.5,
    ),
    # ============ 质量因子 ============
    "high_volume": Factor(
        key="high_volume",
        name="放量",
        type=FactorType.QUALITY,
        description="成交量大于5日均量2倍",
        field="volume",
        operator="gt",
        threshold="vol_ma5_2x",
        weight=1.0,
    ),
    "volume_steady": Factor(
        key="volume_steady",
        name="量能稳定",
        type=FactorType.QUALITY,
        description="成交量在5日均量附近",
        field="volume",
        operator="ge",
        threshold="vol_ma5",
        weight=0.8,
    ),
    # ============ 波动因子 ============
    "low_volatility": Factor(
        key="low_volatility",
        name="低波动",
        type=FactorType.VOLATILITY,
        description="20日波动率小于3%",
        field="volatility_20",
        operator="lt",
        threshold=0.03,
        weight=1.0,
    ),
    "medium_volatility": Factor(
        key="medium_volatility",
        name="适中波动",
        type=FactorType.VOLATILITY,
        description="20日波动率在3%-5%之间",
        field="volatility_20",
        operator="ge",
        threshold=0.03,
        weight=0.7,
    ),
    # ============ 财务因子 ============
    "roe_high": Factor(
        key="roe_high",
        name="高ROE",
        type=FactorType.FINANCIAL,
        description="净资产收益率大于15%",
        field="roe",
        operator="gt",
        threshold=0.15,
        weight=2.0,
    ),
    "profit_growth": Factor(
        key="profit_growth",
        name="利润增长",
        type=FactorType.FINANCIAL,
        description="净利润增长率大于20%",
        field="profit_growth_rate",
        operator="gt",
        threshold=0.20,
        weight=1.8,
    ),
    "revenue_growth": Factor(
        key="revenue_growth",
        name="营收增长",
        type=FactorType.FINANCIAL,
        description="营收增长率大于15%",
        field="revenue_growth_rate",
        operator="gt",
        threshold=0.15,
        weight=1.5,
    ),
    "debt_ratio_low": Factor(
        key="debt_ratio_low",
        name="低负债率",
        type=FactorType.FINANCIAL,
        description="资产负债率小于50%",
        field="debt_ratio",
        operator="lt",
        threshold=0.50,
        weight=1.2,
    ),
    "current_ratio_good": Factor(
        key="current_ratio_good",
        name="流动比率健康",
        type=FactorType.FINANCIAL,
        description="流动比率大于1.5",
        field="current_ratio",
        operator="gt",
        threshold=1.5,
        weight=1.0,
    ),
    # ============ 情绪因子 ============
    "rsi_oversold": Factor(
        key="rsi_oversold",
        name="RSI超卖",
        type=FactorType.SENTIMENT,
        description="RSI6小于30，超卖区域",
        field="rsi6",
        operator="lt",
        threshold=30,
        weight=1.5,
    ),
    "rsi_overbought": Factor(
        key="rsi_overbought",
        name="RSI超买",
        type=FactorType.SENTIMENT,
        description="RSI6大于70，超买区域",
        field="rsi6",
        operator="gt",
        threshold=70,
        weight=-1.0,  # 负权重，表示风险
    ),
    "rsi_neutral": Factor(
        key="rsi_neutral",
        name="RSI中性",
        type=FactorType.SENTIMENT,
        description="RSI在30-70之间，情绪中性",
        field="rsi6",
        operator="ge",
        threshold=30,
        weight=0.5,
    ),
    "kdj_oversold": Factor(
        key="kdj_oversold",
        name="KDJ超卖",
        type=FactorType.SENTIMENT,
        description="KDJ的J值小于20，超卖区域",
        field="kdj_j",
        operator="lt",
        threshold=20,
        weight=1.5,
    ),
    "kdj_overbought": Factor(
        key="kdj_overbought",
        name="KDJ超买",
        type=FactorType.SENTIMENT,
        description="KDJ的J值大于80，超买区域",
        field="kdj_j",
        operator="gt",
        threshold=80,
        weight=-1.0,
    ),
    # ============ 资金流向因子 ============
    "net_inflow": Factor(
        key="net_inflow",
        name="主力净流入",
        type=FactorType.CAPITAL_FLOW,
        description="主力资金净流入",
        field="main_net_inflow",
        operator="gt",
        threshold=0,
        weight=2.0,
    ),
    "large_inflow": Factor(
        key="large_inflow",
        name="大单净流入",
        type=FactorType.CAPITAL_FLOW,
        description="大单净流入大于0",
        field="large_net_inflow",
        operator="gt",
        threshold=0,
        weight=1.5,
    ),
    "north_inflow": Factor(
        key="north_inflow",
        name="北向资金流入",
        type=FactorType.CAPITAL_FLOW,
        description="北向资金净流入",
        field="north_net_inflow",
        operator="gt",
        threshold=0,
        weight=1.8,
    ),
    # ============ 技术因子 ============
    "macd_golden_cross": Factor(
        key="macd_golden_cross",
        name="MACD金叉",
        type=FactorType.TECHNICAL,
        description="MACD柱状线由负转正",
        field="macd_hist",
        operator="gt",
        threshold=0,
        weight=2.0,
    ),
    "macd_dead_cross": Factor(
        key="macd_dead_cross",
        name="MACD死叉",
        type=FactorType.TECHNICAL,
        description="MACD柱状线由正转负",
        field="macd_hist",
        operator="lt",
        threshold=0,
        weight=-1.5,
    ),
    "macd_above_zero": Factor(
        key="macd_above_zero",
        name="MACD零轴上方",
        type=FactorType.TECHNICAL,
        description="MACD在零轴上方运行",
        field="macd",
        operator="gt",
        threshold=0,
        weight=1.2,
    ),
    "kdj_golden_cross": Factor(
        key="kdj_golden_cross",
        name="KDJ金叉",
        type=FactorType.TECHNICAL,
        description="K线上穿D线",
        field="kdj_k",
        operator="cross_up",
        threshold="kdj_d",
        weight=1.8,
    ),
    "boll_lower_support": Factor(
        key="boll_lower_support",
        name="布林下轨支撑",
        type=FactorType.TECHNICAL,
        description="股价触及布林下轨",
        field="close",
        operator="le",
        threshold="boll_lower",
        weight=1.5,
    ),
    "boll_upper_pressure": Factor(
        key="boll_upper_pressure",
        name="布林上轨压力",
        type=FactorType.TECHNICAL,
        description="股价触及布林上轨",
        field="close",
        operator="ge",
        threshold="boll_upper",
        weight=-0.5,
    ),
    "breakout_high": Factor(
        key="breakout_high",
        name="突破前高",
        type=FactorType.TECHNICAL,
        description="股价突破20日新高",
        field="close",
        operator="ge",
        threshold="high_20d",
        weight=2.5,
    ),
}


def get_factor(key: str) -> Optional[Factor]:
    """获取因子"""
    return FACTORS.get(key)


def get_factors_by_type(factor_type: FactorType) -> list[Factor]:
    """按类型获取因子"""
    return [f for f in FACTORS.values() if f.type == factor_type]


def get_all_factor_types() -> list[FactorType]:
    """获取所有因子类型"""
    return list(FactorType)


def get_factor_keys_by_type(factor_type: FactorType) -> list[str]:
    """按类型获取因子键名列表"""
    return [k for k, f in FACTORS.items() if f.type == factor_type]
