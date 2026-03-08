"""用户配置管理"""

from dataclasses import dataclass, field
from datetime import time
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RiskLevel(str, Enum):
    """风险等级"""
    CONSERVATIVE = "conservative"  # 保守型
    MODERATE = "moderate"  # 稳健型
    AGGRESSIVE = "aggressive"  # 激进型


class TradingStyle(str, Enum):
    """交易风格"""
    DAY_TRADING = "day_trading"  # 日内交易
    SWING = "swing"  # 波段交易
    TREND_FOLLOWING = "trend_following"  # 趋势跟踪
    VALUE_INVESTING = "value_investing"  # 价值投资


class UserConfig(BaseModel):
    """用户配置"""

    user_id: str = "default"

    # 风险偏好
    risk_level: RiskLevel = RiskLevel.MODERATE
    trading_style: TradingStyle = TradingStyle.SWING

    # 仓位控制
    max_positions: int = 10  # 最大持仓数量
    position_size: float = 0.1  # 单只股票仓位比例 (10%)

    # 行业偏好
    preferred_sectors: list[str] = []  # 偏好行业
    excluded_sectors: list[str] = []  # 排除行业

    # 价格范围
    min_price: Optional[float] = None  # 最低价格
    max_price: Optional[float] = None  # 最高价格

    # 告警设置
    alert_channels: list[str] = ["terminal"]  # 告警渠道
    alert_time_start: time = time(9, 30)  # 告警开始时间
    alert_time_end: time = time(15, 0)  # 告警结束时间

    # 默认设置
    default_capital: float = 100000.0  # 默认资金
    default_strategy: str = "ma_cross"  # 默认策略

    class Config:
        use_enum_values = False  # 保持枚举类型


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_dir: str = "data/config"):
        """初始化配置管理器

        Args:
            config_dir: 配置文件目录
        """
        from pathlib import Path
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, UserConfig] = {}

    def _get_config_path(self, user_id: str) -> "Path":
        """获取配置文件路径"""
        return self.config_dir / f"{user_id}.json"

    def load(self, user_id: str = "default") -> UserConfig:
        """加载用户配置

        Args:
            user_id: 用户ID

        Returns:
            用户配置对象
        """
        import json

        # 检查缓存
        if user_id in self._cache:
            return self._cache[user_id]

        config_path = self._get_config_path(user_id)

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 转换时间字符串为 time 对象
                if "alert_time_start" in data and isinstance(data["alert_time_start"], str):
                    parts = data["alert_time_start"].split(":")
                    h, m = int(parts[0]), int(parts[1])
                    data["alert_time_start"] = time(h, m)
                if "alert_time_end" in data and isinstance(data["alert_time_end"], str):
                    parts = data["alert_time_end"].split(":")
                    h, m = int(parts[0]), int(parts[1])
                    data["alert_time_end"] = time(h, m)
                config = UserConfig(**data)
        else:
            # 创建默认配置
            config = UserConfig(user_id=user_id)
            self.save(config)

        self._cache[user_id] = config
        return config

    def save(self, config: UserConfig) -> None:
        """保存用户配置

        Args:
            config: 用户配置对象
        """
        import json

        config_path = self._get_config_path(config.user_id)

        # 转换为字典并处理特殊类型
        data = config.model_dump()
        data["alert_time_start"] = config.alert_time_start.isoformat()
        data["alert_time_end"] = config.alert_time_end.isoformat()
        data["risk_level"] = config.risk_level.value
        data["trading_style"] = config.trading_style.value

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # 更新缓存
        self._cache[config.user_id] = config

    def update(self, user_id: str, **kwargs) -> UserConfig:
        """更新用户配置

        Args:
            user_id: 用户ID
            **kwargs: 要更新的配置项

        Returns:
            更新后的配置对象
        """
        config = self.load(user_id)

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.save(config)
        return config

    def reset(self, user_id: str) -> UserConfig:
        """重置用户配置为默认值

        Args:
            user_id: 用户ID

        Returns:
            重置后的配置对象
        """
        config = UserConfig(user_id=user_id)
        self.save(config)
        return config
