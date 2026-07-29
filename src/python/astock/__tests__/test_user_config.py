"""Safety defaults for user market-data policy."""

import json
from pathlib import Path

from astock.config import ConfigManager, MarketDataMode, UserConfig


def test_new_and_reset_profiles_default_to_public_observation(tmp_path) -> None:
    manager = ConfigManager(config_dir=str(tmp_path))

    assert UserConfig().market_data_mode is MarketDataMode.PUBLIC_OBSERVATION
    assert manager.load("new-user").market_data_mode is MarketDataMode.PUBLIC_OBSERVATION
    assert manager.reset("new-user").market_data_mode is MarketDataMode.PUBLIC_OBSERVATION


def test_default_strategy_is_not_a_mechanical_indicator_strategy(tmp_path) -> None:
    manager = ConfigManager(config_dir=str(tmp_path))

    config = manager.load("new-user")

    assert config.default_strategy == "market_structure_review"
    assert config.default_strategy not in {
        "ma_cross",
        "macd",
        "kdj",
        "rsi",
    }


def test_checked_in_default_config_avoids_mechanical_strategy() -> None:
    config_path = Path(__file__).parents[4] / "data" / "config" / "default.json"
    checked_in_config = json.loads(config_path.read_text(encoding="utf-8"))

    assert checked_in_config["default_strategy"] == "market_structure_review"
