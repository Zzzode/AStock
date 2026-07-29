"""Integrity tests for immutable public market-desk observation history."""

import json

from astock.market_data import build_public_market_observation_packet
from astock.market_desk import (
    build_public_desk_observation_run,
    create_public_desk_observation_exception_review,
    list_public_desk_observation_runs,
    verify_public_desk_observation_run,
)


def _write_valid_run(
    tmp_path,
    observed_at: str = "2026-07-28T15:10:00+08:00",
    *,
    market_session_state: str = "after_close",
    calendar_basis: str = "exchange_calendar",
):
    source_packet = build_public_market_observation_packet(
        subject="market_rotation",
        observation={
            "observed_at": observed_at,
            "data_quality": "snapshot",
            "rankings": {"industries": []},
        },
    )
    source_path = source_packet.write_frozen_archive(tmp_path / "rotation")
    rotation = source_packet.to_dict()
    rotation["source_archive_path"] = str(source_path)
    run = build_public_desk_observation_run(
        market_overview={
            "schema_version": "market_desk_overview.v1",
            "snapshot": {
                "observed_at": observed_at,
                "market_session": {
                    "state": market_session_state,
                    "calendar_basis": calendar_basis,
                },
            },
            "regime": {"regime": "defensive_rotation"},
        },
        rotation_observation=rotation,
        operational_readiness={
            "observation_desk_status": "ready",
            "formal_paper_desk_status": "blocked",
        },
    )
    return run.write(tmp_path / "runs")


def test_verify_public_desk_observation_run_checks_record_and_source_hashes(tmp_path) -> None:
    path = _write_valid_run(tmp_path)

    result = verify_public_desk_observation_run(path)

    assert result["status"] == "pass"
    assert result["rotation_source_assurance"]["status"] == "pass"
    assert result["eod_validation"]["status"] == "pass"


def test_history_does_not_count_intraday_observations_as_eod_evidence(tmp_path) -> None:
    path = _write_valid_run(
        tmp_path,
        "2026-07-28T10:10:00+08:00",
        market_session_state="continuous_morning",
    )

    verification = verify_public_desk_observation_run(path)
    history = list_public_desk_observation_runs(tmp_path / "runs")

    assert verification["status"] == "pass"
    assert verification["eod_validation"]["status"] == "not_eod"
    assert history["valid_count"] == 1
    assert history["eod_valid_count"] == 0
    assert history["latest_valid_eod_observed_at"] is None


def test_history_reports_tampered_records_and_duplicate_run_dates(tmp_path) -> None:
    first = _write_valid_run(tmp_path)
    second = tmp_path / "runs" / "tampered.json"
    payload = json.loads(first.read_text(encoding="utf-8"))
    payload["operation"] = "invalid"
    second.write_text(json.dumps(payload), encoding="utf-8")

    history = list_public_desk_observation_runs(tmp_path / "runs")

    assert history["run_count"] == 2
    assert history["valid_count"] == 1
    assert history["invalid_count"] == 1
    assert history["duplicate_run_dates"] == ["2026-07-28"]


def test_exception_review_resolves_only_the_exact_valid_duplicate_set(tmp_path) -> None:
    first = _write_valid_run(tmp_path, "2026-07-28T15:10:00+08:00")
    second = _write_valid_run(tmp_path, "2026-07-28T15:12:00+08:00")
    archive_ids = [
        json.loads(first.read_text(encoding="utf-8"))["archive_id"],
        json.loads(second.read_text(encoding="utf-8"))["archive_id"],
    ]
    review = create_public_desk_observation_exception_review(
        session_date="2026-07-28",
        archive_ids=archive_ids,
        canonical_archive_id=archive_ids[0],
        reviewer="operations-control",
        reason="The second run was a controlled replay of the first public observation workflow.",
        evidence_refs=["ops-ticket:fixture"],
        reviewed_at="2026-07-28T16:00:00+08:00",
    )
    review.write(tmp_path / "exceptions")

    history = list_public_desk_observation_runs(
        tmp_path / "runs", exception_directory=tmp_path / "exceptions"
    )

    assert history["valid_duplicate_run_dates"] == ["2026-07-28"]
    assert history["resolved_duplicate_run_dates"] == ["2026-07-28"]
    assert history["unresolved_valid_duplicate_run_dates"] == []
