"""Evidence-maturity tests for the non-executing public market desk."""

from astock import capabilities


def _readiness() -> dict[str, object]:
    return {
        "market_data_mode": "public_observation",
        "formal_paper_desk_status": "not_enabled",
        "active_strategy_entry_count": 0,
        "checks": {
            "observation_history": {
                "status": "pass",
                "valid_count": 2,
                "latest_valid_observed_at": "2026-07-28T15:10:00+08:00",
                "eod_valid_count": 2,
                "latest_valid_eod_observed_at": "2026-07-28T15:10:00+08:00",
            },
            "reproducible_reviews": {
                "counts": {"pass": 0, "public_frozen": 0, "blocked": 0, "other": 0}
            },
            "paper_portfolio_governance": {
                "status": "pass",
                "position_count": 0,
                "governed_count": 0,
                "exit_review_required_count": 0,
            },
            "quality_feedback": {"status": "not_ready", "assessed_entry_count": 0},
            "postmortem_control": {"status": "not_ready"},
        },
    }


def _scheduler_status(*, running: bool) -> dict[str, object]:
    return {
        "running": running,
        "runtime": {"status": "running" if running else "stopped"},
        "jobs": {
            "audit_market_desk_operational_readiness": {
                "dependency_blockers": [
                    {"job": "record_public_market_desk_eod_observation", "reason": "never_successful"}
                ]
            }
        },
    }


def test_maturity_reports_unexercised_controls_as_evidence_pending(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: _readiness())

    result = capabilities.assess_market_desk_operating_maturity(
        ledger_path=tmp_path / "ledger.json",
        observation_archive_directory=tmp_path / "observations",
        discovery_archive_directory=tmp_path / "discoveries",
        portfolio_path=tmp_path / "portfolio.json",
        scheduler_status=_scheduler_status(running=True),
    )

    assert result["maturity_status"] == "evidence_accumulating"
    assert result["requirements"]["whole_market_observation"]["status"] == "operational"
    assert result["requirements"]["whole_market_discovery"]["status"] == "evidence_pending"
    assert result["requirements"]["frozen_return_review"]["status"] == "evidence_pending"
    assert result["requirements"]["runtime_and_eod_controls"]["status"] == "evidence_pending"
    assert result["requirements"]["paper_portfolio_risk_control"]["status"] == "evidence_pending"
    assert result["requirements"]["formal_release_boundary"]["status"] == "not_enabled"
    assert result["no_order_execution"] is True


def test_maturity_blocks_when_scheduler_runtime_is_not_running(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: _readiness())

    result = capabilities.assess_market_desk_operating_maturity(
        ledger_path=tmp_path / "ledger.json",
        observation_archive_directory=tmp_path / "observations",
        discovery_archive_directory=tmp_path / "discoveries",
        portfolio_path=tmp_path / "portfolio.json",
        scheduler_status=_scheduler_status(running=False),
    )

    assert result["maturity_status"] == "blocked"
    assert result["requirements"]["runtime_and_eod_controls"]["status"] == "blocked"


def test_maturity_marks_eod_control_operational_only_after_dependencies_clear(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: _readiness())
    scheduler_status = _scheduler_status(running=True)
    scheduler_status["jobs"] = {
        "audit_market_desk_operational_readiness": {"dependency_blockers": []}
    }

    result = capabilities.assess_market_desk_operating_maturity(
        ledger_path=tmp_path / "ledger.json",
        observation_archive_directory=tmp_path / "observations",
        discovery_archive_directory=tmp_path / "discoveries",
        portfolio_path=tmp_path / "portfolio.json",
        scheduler_status=scheduler_status,
    )

    assert result["requirements"]["runtime_and_eod_controls"]["status"] == "operational"


def test_maturity_does_not_count_an_eod_discovery_source_outage_as_operating_evidence(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: _readiness())
    monkeypatch.setattr(
        capabilities,
        "get_public_market_desk_discovery_history",
        lambda **_: {
            "valid_count": 1,
            "eod_valid_count": 1,
            "usable_eod_valid_count": 0,
            "invalid_count": 0,
            "latest_valid_observed_at": "2026-07-28T15:05:00+08:00",
            "latest_valid_eod_observed_at": "2026-07-28T15:05:00+08:00",
            "latest_usable_eod_observed_at": None,
            "usable_eod_duplicate_run_dates": [],
            "archive_directory": str(tmp_path / "discoveries"),
        },
    )

    result = capabilities.assess_market_desk_operating_maturity(
        ledger_path=tmp_path / "ledger.json",
        observation_archive_directory=tmp_path / "observations",
        discovery_archive_directory=tmp_path / "discoveries",
        portfolio_path=tmp_path / "portfolio.json",
        scheduler_status=_scheduler_status(running=True),
    )

    assert result["requirements"]["whole_market_discovery"]["status"] == "evidence_pending"
    assert result["requirements"]["whole_market_discovery"]["evidence"]["eod_valid_archive_count"] == 1
    assert result["requirements"]["whole_market_discovery"]["evidence"]["usable_eod_valid_archive_count"] == 0


def test_maturity_blocks_duplicate_usable_eod_discovery_runs(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: _readiness())
    monkeypatch.setattr(
        capabilities,
        "get_public_market_desk_discovery_history",
        lambda **_: {
            "valid_count": 2,
            "eod_valid_count": 2,
            "usable_eod_valid_count": 2,
            "invalid_count": 0,
            "latest_valid_observed_at": "2026-07-28T15:10:00+08:00",
            "latest_valid_eod_observed_at": "2026-07-28T15:10:00+08:00",
            "latest_usable_eod_observed_at": "2026-07-28T15:10:00+08:00",
            "usable_eod_duplicate_run_dates": ["2026-07-28"],
            "archive_directory": str(tmp_path / "discoveries"),
        },
    )

    result = capabilities.assess_market_desk_operating_maturity(
        ledger_path=tmp_path / "ledger.json",
        observation_archive_directory=tmp_path / "observations",
        discovery_archive_directory=tmp_path / "discoveries",
        portfolio_path=tmp_path / "portfolio.json",
        scheduler_status=_scheduler_status(running=True),
    )

    discovery = result["requirements"]["whole_market_discovery"]
    assert discovery["status"] == "blocked"
    assert discovery["evidence"]["usable_eod_duplicate_run_dates"] == ["2026-07-28"]


def test_maturity_requires_a_governed_paper_position_before_claiming_risk_control_is_operational(
    tmp_path, monkeypatch
) -> None:
    readiness = _readiness()
    readiness["checks"]["paper_portfolio_governance"] = {
        "status": "pass",
        "position_count": 1,
        "governed_count": 1,
        "exit_review_required_count": 0,
    }
    monkeypatch.setattr(capabilities, "assess_market_desk_operational_readiness", lambda **_: readiness)

    result = capabilities.assess_market_desk_operating_maturity(
        ledger_path=tmp_path / "ledger.json",
        observation_archive_directory=tmp_path / "observations",
        discovery_archive_directory=tmp_path / "discoveries",
        portfolio_path=tmp_path / "portfolio.json",
        scheduler_status=_scheduler_status(running=True),
    )

    assert result["requirements"]["paper_portfolio_risk_control"]["status"] == "operational"
