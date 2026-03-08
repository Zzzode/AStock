"""因子定义"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Optional


class FactorType(Enum):
    """因子类型"""
    VALUATION = "valuation"      # 估值因子
    MOMENTUM = "momentum"        # 动量因子
    QUALITY = "quality"          # 质量因子
    VOLATILITY = "volatility"    # 波动因子


@dataclass
class Factor:
    """因子定义"""
    key: str                     # 因子键名
    name: str                    # 因子名称
    type: FactorType             # 因子类型
    description: str             # 因子描述
    field: str                   # 数据字段
    operator: str                # 比较操作符 (lt, le, gt, ge, eq, cross_up, cross_down)
    threshold: Any               # 阈值
    weight: float = 1.0          # 权重
    value_extractor: Optional[str] = None  # 值提取器


# 预定义因子
FACTORS: dict[str, Factor] = {
    # 估值因子
    "pe_low": Factor(
        key="pe_low",
        name="低市盈率",
        type=FactorType.VALUATION,
        description="市盈率小于30倍",
        field="pe",
        operator="lt",
        threshold=30,
        weight=1.0
    ),
    "pb_low": Factor(
        key="pb_low",
        name="低市净率",
        type=FactorType.VALUATION,
        description="市净率小于3倍",
        field="pb",
        operator="lt",
        threshold=3,
        weight=1.0
    ),

    # 动量因子
    "ma20_above": Factor(
        key="ma20_above",
        name="站上20日线",
        type=FactorType.MOMENTUM,
        description="收盘价站上20日均线",
        field="close",
        operator="gt",
        threshold="ma20",  # 引用其他字段
        weight=1.5
    ),
    "ma5_cross_ma20": Factor(
        key="ma5_cross_ma20",
        name="MA5金叉MA20",
        type=FactorType.MOMENTUM,
        description="5日均线上穿20日均线",
        field="ma5",
        operator="cross_up",
        threshold="ma20",
        weight=2.0
    ),

    # 质量因子
    "high_volume": Factor(
        key="high_volume",
        name="放量",
        type=FactorType.QUALITY,
        description="成交量大于5日均量2倍",
        field="volume",
        operator="gt",
        threshold="vol_ma5_2x",  # 需要计算
        weight=1.0
    ),

    # 波动因子
    "low_volatility": Factor(
        key="low_volatility",
        name="低波动",
        type=FactorType.VOLATILITY,
        description="20日波动率小于3%",
        field="volatility_20",
        operator="lt",
        threshold=0.03,
        weight=1.0
    ),
}


def get_factor(key: str) -> Optional[Factor]:
    """获取因子

    Args:
        key: 因子键名

    Returns:
        因子对象，不存在返回 None
    """
    return FACTORS.get(key)


def get_factors_by_type(factor_type: FactorType) -> list[Factor]:
    """按类型获取因子

    Args:
        factor_type: 因子类型

    Returns:
        该类型的因子列表
    """
    return [f for f in FACTORS.values() if f.type == factor_type]
