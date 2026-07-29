"""User configuration management"""

from datetime import time
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class RiskLevel(str, Enum):
    """Risk level"""
    CONSERVATIVE = "conservative"  # Conservative
    MODERATE = "moderate"  # Moderate
    AGGRESSIVE = "aggressive"  # Aggressive


class TradingStyle(str, Enum):
    """Trading style"""
    DAY_TRADING = "day_trading"  # Day Trading
    SWING = "swing"  # Swing Trading
    TREND_FOLLOWING = "trend_following"  # Trend Following
    VALUE_INVESTING = "value_investing"  # Value Investing


class MarketDataMode(str, Enum):
    """Permitted market-data evidence lane for the current user profile."""

    PUBLIC_OBSERVATION = "public_observation"
    LICENSED_EOD = "licensed_eod"


class UserConfig(BaseModel):
    """User configuration"""

    user_id: str = "default"

    # Risk preference
    risk_level: RiskLevel = RiskLevel.MODERATE
    trading_style: TradingStyle = TradingStyle.SWING

    # Position control
    max_positions: int = 10  # Maximum number of positions
    position_size: float = 0.1  # Single stock position ratio (10%)

    # Sector preference
    preferred_sectors: list[str] = []  # Preferred sectors
    excluded_sectors: list[str] = []  # Excluded sectors

    # Price range
    min_price: Optional[float] = None  # Minimum price
    max_price: Optional[float] = None  # Maximum price

    # Alert settings
    alert_channels: list[str] = ["terminal"]  # Alert channels
    alert_time_start: time = time(9, 30)  # Alert start time
    alert_time_end: time = time(15, 0)  # Alert end time

    # Default settings
    default_capital: float = 100000.0  # Default capital
    default_strategy: str = "market_structure_review"  # Default strategy

    # Data-source policy
    # New and reset profiles must never opt into paid/licensed data implicitly.
    # A licensed lane is an explicit, auditable user policy change.
    market_data_mode: MarketDataMode = MarketDataMode.PUBLIC_OBSERVATION

    class Config:
        use_enum_values = False  # Keep enum types


class ConfigManager:
    """Configuration manager"""

    def __init__(self, config_dir: str = "data/config"):
        """Initialize configuration manager

        Args:
            config_dir: Configuration file directory
        """
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, UserConfig] = {}

    def _get_config_path(self, user_id: str) -> "Path":
        """Get configuration file path"""
        return self.config_dir / f"{user_id}.json"

    def load(self, user_id: str = "default") -> UserConfig:
        """Load user configuration

        Args:
            user_id: User ID

        Returns:
            User configuration object
        """
        import json

        # Check cache
        if user_id in self._cache:
            return self._cache[user_id]

        config_path = self._get_config_path(user_id)

        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Convert time strings to time objects
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
            # Create default configuration
            config = UserConfig(user_id=user_id)
            self.save(config)

        self._cache[user_id] = config
        return config

    def save(self, config: UserConfig) -> None:
        """Save user configuration

        Args:
            config: User configuration object
        """
        import json

        config_path = self._get_config_path(config.user_id)

        # Convert to dict and handle special types
        data = config.model_dump()
        data["alert_time_start"] = config.alert_time_start.isoformat()
        data["alert_time_end"] = config.alert_time_end.isoformat()
        data["risk_level"] = config.risk_level.value
        data["trading_style"] = config.trading_style.value
        data["market_data_mode"] = config.market_data_mode.value

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Update cache
        self._cache[config.user_id] = config

    def update(self, user_id: str, **kwargs: object) -> UserConfig:
        """Update user configuration

        Args:
            user_id: User ID
            **kwargs: Configuration fields to update

        Returns:
            Updated configuration object
        """
        config = self.load(user_id)

        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.save(config)
        return config

    def reset(self, user_id: str) -> UserConfig:
        """Reset user configuration to defaults

        Args:
            user_id: User ID

        Returns:
            Reset configuration object
        """
        config = UserConfig(user_id=user_id)
        self.save(config)
        return config
