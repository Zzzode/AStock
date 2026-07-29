"""CLI regression tests for scheduler operating controls."""

import json

from typer.testing import CliRunner

from astock.cli import app


def test_scheduler_background_mode_is_rejected_instead_of_reporting_a_dead_daemon() -> None:
    result = CliRunner().invoke(app, ["scheduler", "start", "--background", "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["background_supported"] is False
    assert "process supervisor" in payload["error"]


def test_scheduler_status_registers_the_operational_desk_jobs() -> None:
    result = CliRunner().invoke(app, ["scheduler", "status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["job_count"] >= 8
    assert "record_public_market_desk_eod_discovery" in payload["jobs"]
    assert "audit_market_desk_strategy_reviews" in payload["jobs"]
