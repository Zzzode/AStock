"""Watch-list alert-type boundary tests."""

import pytest
import typer

from astock.monitor.watch_cli import normalize_watch_alert_types


def test_watch_list_accepts_only_reproducible_structure_alerts() -> None:
    assert normalize_watch_alert_types("price_dislocation, volume_spike") == [
        "price_dislocation",
        "volume_spike",
    ]


@pytest.mark.parametrize("legacy_type", ["ma", "macd", "kdj", "rsi"])
def test_watch_list_rejects_legacy_indicator_alerts(legacy_type: str) -> None:
    with pytest.raises(typer.BadParameter, match="unsupported alert type"):
        normalize_watch_alert_types(legacy_type)
