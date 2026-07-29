"""Tests for task scheduler."""

from datetime import datetime, timedelta, timezone

import pytest

from unittest.mock import AsyncMock, patch

from astock.scheduler import (
    EXCHANGE_TIMEZONE,
    JobFrequency,
    JobStatus,
    ScheduledJob,
    TaskScheduler,
    create_default_jobs,
    create_default_scheduler,
)


@pytest.fixture
def scheduler(tmp_path):
    return TaskScheduler(state_path=tmp_path / "state.json")


def _make_job(name: str, freq: JobFrequency) -> ScheduledJob:
    async def handler():
        return {"ok": True}
    return ScheduledJob(name=name, frequency=freq, handler=handler)


def test_register_and_status(scheduler):
    job = _make_job("test_job", JobFrequency.HOURLY)
    scheduler.register(job)
    status = scheduler.get_status()
    assert status["job_count"] == 1
    assert "test_job" in status["jobs"]
    assert status["jobs"]["test_job"]["frequency"] == "hourly"


def test_default_scheduler_exposes_the_same_control_topology_to_status_and_daemon(tmp_path) -> None:
    scheduler = create_default_scheduler(state_path=tmp_path / "state.json")

    assert {
        "record_public_market_desk_eod_observation",
        "record_public_market_desk_eod_discovery",
        "audit_market_desk_strategy_reviews",
        "audit_market_desk_discovery_research_queue",
        "audit_market_desk_postmortem_queue",
        "audit_market_desk_operational_readiness",
        "audit_market_desk_operating_maturity",
        "sync_research_to_monitor",
    } <= set(scheduler.get_status()["jobs"])
    assert scheduler.get_status()["jobs"]["audit_market_desk_operational_readiness"][
        "depends_on"
    ] == [
        "record_public_market_desk_eod_observation",
        "record_public_market_desk_eod_discovery",
        "audit_market_desk_strategy_reviews",
        "audit_market_desk_discovery_research_queue",
        "audit_market_desk_postmortem_queue",
    ]
    assert scheduler.get_status()["jobs"]["audit_market_desk_operating_maturity"][
        "depends_on"
    ] == ["audit_market_desk_operational_readiness"]
    assert scheduler._jobs["record_public_market_desk_eod_observation"].completion_verifier is not None
    assert scheduler._jobs["record_public_market_desk_eod_discovery"].completion_verifier is not None


def test_dependent_daily_control_reruns_when_predecessors_finish_later_same_session(
    scheduler,
) -> None:
    predecessor = _make_job("predecessor", JobFrequency.DAILY_AFTER_CLOSE)
    dependent = ScheduledJob(
        name="dependent",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_make_job("unused", JobFrequency.DAILY_AFTER_CLOSE).handler,
        depends_on=("predecessor",),
    )
    scheduler.register(predecessor)
    scheduler.register(dependent)
    prior_audit = datetime(2026, 7, 29, 10, 45, tzinfo=EXCHANGE_TIMEZONE)
    after_close = datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE)
    dependent.last_run = prior_audit
    predecessor.last_run = datetime(2026, 7, 29, 15, 7, tzinfo=EXCHANGE_TIMEZONE)

    assert scheduler._should_run(dependent, after_close) is True


def test_dependent_daily_control_does_not_rerun_when_audit_is_newer_than_predecessors(
    scheduler,
) -> None:
    predecessor = _make_job("predecessor", JobFrequency.DAILY_AFTER_CLOSE)
    dependent = ScheduledJob(
        name="dependent",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_make_job("unused", JobFrequency.DAILY_AFTER_CLOSE).handler,
        depends_on=("predecessor",),
    )
    scheduler.register(predecessor)
    scheduler.register(dependent)
    predecessor.last_run = datetime(2026, 7, 29, 15, 7, tzinfo=EXCHANGE_TIMEZONE)
    dependent.last_run = datetime(2026, 7, 29, 15, 9, tzinfo=EXCHANGE_TIMEZONE)

    assert scheduler._should_run(
        dependent, datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE)
    ) is False


def test_enable_disable(scheduler):
    job = _make_job("test_job", JobFrequency.DAILY_AFTER_CLOSE)
    scheduler.register(job)
    scheduler.disable("test_job")
    assert scheduler._jobs["test_job"].status == JobStatus.DISABLED
    scheduler.enable("test_job")
    assert scheduler._jobs["test_job"].status == JobStatus.IDLE


@pytest.mark.asyncio
async def test_run_once(scheduler):
    async def _handler():
        return {"result": 42}

    job = ScheduledJob(name="manual", frequency=JobFrequency.HOURLY, handler=_handler)
    scheduler.register(job)
    result = await scheduler.run_once("manual")
    assert result == {"result": 42}
    assert scheduler._jobs["manual"].run_count == 1
    assert scheduler.get_status()["jobs"]["manual"]["last_result"] == {"result": 42}


@pytest.mark.asyncio
async def test_manual_after_close_job_cannot_bypass_the_exchange_close_window(
    scheduler, monkeypatch
) -> None:
    handler = AsyncMock(return_value={"status": "recorded"})
    job = ScheduledJob(
        name="eod_control",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=handler,
    )
    scheduler.register(job)
    monkeypatch.setattr(
        "astock.scheduler._exchange_now",
        lambda: datetime(2026, 7, 29, 14, 59, tzinfo=EXCHANGE_TIMEZONE),
    )

    result = await scheduler.run_once("eod_control")

    assert result["status"] == "skipped"
    assert result["reason"] == "manual_run_not_permitted_by_schedule"
    assert job.last_run is None
    handler.assert_not_awaited()


@pytest.mark.asyncio
async def test_manual_after_close_job_cannot_bypass_dependencies(
    scheduler, monkeypatch
) -> None:
    predecessor = _make_job("predecessor", JobFrequency.DAILY_AFTER_CLOSE)
    handler = AsyncMock(return_value={"status": "ready"})
    dependent = ScheduledJob(
        name="dependent",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=handler,
        depends_on=("predecessor",),
    )
    scheduler.register(predecessor)
    scheduler.register(dependent)
    monkeypatch.setattr(
        "astock.scheduler._exchange_now",
        lambda: datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE),
    )

    result = await scheduler.run_once("dependent")

    assert result["status"] == "skipped"
    assert result["reason"] == "manual_run_not_permitted_by_schedule"
    assert result["dependency_blockers"] == [
        {"job": "predecessor", "reason": "never_successful"}
    ]
    assert dependent.last_run is None
    handler.assert_not_awaited()


@pytest.mark.asyncio
async def test_scheduler_persists_structured_last_result(tmp_path) -> None:
    state_path = tmp_path / "state.json"
    first = TaskScheduler(state_path=state_path)
    first.register(_make_job("control", JobFrequency.HOURLY))
    await first.run_once("control")

    resumed = TaskScheduler(state_path=state_path)
    resumed.register(_make_job("control", JobFrequency.HOURLY))
    resumed._load_state()

    assert resumed.get_status()["jobs"]["control"]["last_result"] == {"ok": True}


@pytest.mark.asyncio
async def test_scheduler_publishes_a_fresh_runtime_lease_to_status_readers(tmp_path) -> None:
    state_path = tmp_path / "state.json"
    daemon = TaskScheduler(state_path=state_path)
    daemon.register(_make_job("control", JobFrequency.HOURLY))
    await daemon.start()
    try:
        reader = TaskScheduler(state_path=state_path)
        reader.register(_make_job("control", JobFrequency.HOURLY))
        reader._load_state()

        assert daemon.get_status()["running"] is True
        assert reader.get_status()["running"] is True
        assert reader.get_status()["runtime"]["status"] == "running"
        assert reader.get_status()["runtime"]["pid_alive"] is True
        assert reader.get_status()["runtime"]["heartbeat_age_seconds"] is not None
    finally:
        await daemon.stop()

    stopped_reader = TaskScheduler(state_path=state_path)
    stopped_reader.register(_make_job("control", JobFrequency.HOURLY))
    stopped_reader._load_state()
    assert stopped_reader.get_status()["running"] is False
    assert stopped_reader.get_status()["runtime"]["status"] == "stopped"
    assert not list(tmp_path.glob(".state.json.tmp"))


@pytest.mark.asyncio
async def test_loading_state_before_manual_run_preserves_other_job_history(tmp_path) -> None:
    state_path = tmp_path / "state.json"
    first = TaskScheduler(state_path=state_path)
    first.register(_make_job("first", JobFrequency.HOURLY))
    first.register(_make_job("second", JobFrequency.HOURLY))
    await first.run_once("first")

    resumed = TaskScheduler(state_path=state_path)
    resumed.register(_make_job("first", JobFrequency.HOURLY))
    resumed.register(_make_job("second", JobFrequency.HOURLY))
    resumed._load_state()
    await resumed.run_once("second")

    final = TaskScheduler(state_path=state_path)
    final.register(_make_job("first", JobFrequency.HOURLY))
    final.register(_make_job("second", JobFrequency.HOURLY))
    final._load_state()
    assert final._jobs["first"].run_count == 1
    assert final._jobs["second"].run_count == 1


@pytest.mark.asyncio
async def test_run_once_not_found(scheduler):
    result = await scheduler.run_once("nonexistent")
    assert "error" in result


@pytest.mark.asyncio
async def test_failed_job(scheduler):
    async def _handler():
        raise ValueError("something broke")

    job = ScheduledJob(name="failing", frequency=JobFrequency.HOURLY, handler=_handler)
    scheduler.register(job)
    result = await scheduler.run_once("failing")
    assert "error" in result
    assert scheduler._jobs["failing"].error_count == 1
    assert scheduler._jobs["failing"].status == JobStatus.FAILED
    assert scheduler._jobs["failing"].last_run is None
    assert scheduler._jobs["failing"].next_retry_at is not None


@pytest.mark.asyncio
async def test_failed_after_close_job_retries_without_counting_failure_as_completion(
    scheduler, monkeypatch
):
    calls = 0

    async def _handler():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise ConnectionError("temporary source outage")
        return {"status": "recorded"}

    job = ScheduledJob(
        name="after_close_desk",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_handler,
    )
    scheduler.register(job)
    monkeypatch.setattr(
        "astock.scheduler._exchange_now",
        lambda: datetime(2026, 7, 28, 15, 10, tzinfo=EXCHANGE_TIMEZONE),
    )

    first = await scheduler.run_once("after_close_desk")
    assert "error" in first
    assert job.last_run is None
    assert job.next_retry_at is not None

    job.next_retry_at = datetime(2026, 7, 28, 15, 10)
    assert scheduler._should_run(job, datetime(2026, 7, 28, 15, 9)) is False
    assert scheduler._should_run(job, datetime(2026, 7, 28, 15, 10)) is True

    second = await scheduler.run_once("after_close_desk")
    assert second == {"status": "recorded"}
    assert calls == 2
    assert job.last_run is not None
    assert job.next_retry_at is None
    assert job.status == JobStatus.IDLE


@pytest.mark.asyncio
async def test_eod_skip_without_archive_does_not_count_as_completion_or_unblock_dependents(
    scheduler, monkeypatch
) -> None:
    attempted_at = datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE)
    monkeypatch.setattr("astock.scheduler._exchange_now", lambda: attempted_at)

    async def _skipped_observation() -> dict[str, str]:
        return {
            "status": "skipped",
            "reason": "verified_exchange_after_close_required",
        }

    async def _readiness() -> dict[str, str]:
        return {"status": "ready"}

    observation = ScheduledJob(
        name="observation", frequency=JobFrequency.DAILY_AFTER_CLOSE, handler=_skipped_observation
    )
    readiness = ScheduledJob(
        name="readiness",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_readiness,
        depends_on=("observation",),
    )
    scheduler.register(observation)
    scheduler.register(readiness)

    result = await scheduler.run_once("observation")

    assert result["status"] == "skipped"
    assert observation.last_run is None
    assert observation.last_skip_at == attempted_at
    assert scheduler._should_run(observation, attempted_at) is False
    assert scheduler._should_run(
        observation, attempted_at + timedelta(days=1)
    ) is True
    assert scheduler._should_run(readiness, attempted_at) is False
    assert scheduler.get_status()["jobs"]["readiness"]["dependency_blockers"] == [
        {"job": "observation", "reason": "never_successful"}
    ]


@pytest.mark.asyncio
async def test_eod_skip_with_verified_existing_archive_counts_as_completion(
    scheduler, monkeypatch
) -> None:
    attempted_at = datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE)
    monkeypatch.setattr("astock.scheduler._exchange_now", lambda: attempted_at)

    async def _existing_observation() -> dict[str, object]:
        return {
            "status": "skipped",
            "reason": "valid_eod_observation_exists_for_session_date",
            "existing_archive_ids": ["sha256:verified-eod-archive"],
        }

    job = ScheduledJob(
        name="observation", frequency=JobFrequency.DAILY_AFTER_CLOSE, handler=_existing_observation
    )
    scheduler.register(job)

    await scheduler.run_once("observation")

    assert job.last_run == attempted_at
    assert job.last_skip_at is None


@pytest.mark.asyncio
async def test_eod_existing_archive_skip_fails_when_completion_verification_rejects_it(
    scheduler, monkeypatch
) -> None:
    attempted_at = datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE)
    monkeypatch.setattr("astock.scheduler._exchange_now", lambda: attempted_at)

    async def _existing_observation() -> dict[str, object]:
        return {
            "status": "skipped",
            "reason": "valid_eod_observation_exists_for_session_date",
            "existing_archive_ids": ["sha256:unverified"],
        }

    def _reject(_: dict[str, object]) -> dict[str, object]:
        return {"status": "blocked", "failures": ["archive verification failed"]}

    job = ScheduledJob(
        name="observation",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_existing_observation,
        completion_verifier=_reject,
    )
    scheduler.register(job)

    result = await scheduler.run_once("observation")

    assert "error" in result
    assert "completion verification failed" in result["error"]
    assert job.last_run is None
    assert job.last_skip_at is None
    assert job.status == JobStatus.FAILED


@pytest.mark.asyncio
async def test_after_close_dependency_waits_for_same_session_predecessor(
    scheduler, monkeypatch
) -> None:
    async def _record_observation() -> dict[str, object]:
        return {"status": "recorded"}

    async def _readiness() -> dict[str, object]:
        return {"status": "ready"}

    observation = ScheduledJob(
        name="observation",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_record_observation,
    )
    readiness = ScheduledJob(
        name="readiness",
        frequency=JobFrequency.DAILY_AFTER_CLOSE,
        handler=_readiness,
        depends_on=("observation",),
    )
    scheduler.register(observation)
    scheduler.register(readiness)
    after_close = datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE)
    monkeypatch.setattr("astock.scheduler._exchange_now", lambda: after_close)

    assert scheduler._should_run(readiness, after_close) is False
    blockers = scheduler.get_status()["jobs"]["readiness"]["dependency_blockers"]
    assert blockers == [{"job": "observation", "reason": "never_successful"}]
    await scheduler.run_once("observation")
    assert scheduler._should_run(readiness, after_close) is True
    assert scheduler.get_status()["jobs"]["readiness"]["dependency_blockers"] == []


@pytest.mark.asyncio
async def test_failed_job_status_and_retry_are_visible_after_scheduler_restart(
    tmp_path, monkeypatch
) -> None:
    state_path = tmp_path / "state.json"

    async def _handler():
        raise ConnectionError("source timeout")

    failed = TaskScheduler(state_path=state_path)
    failed.register(
        ScheduledJob(name="eod_control", frequency=JobFrequency.DAILY_AFTER_CLOSE, handler=_handler)
    )
    monkeypatch.setattr(
        "astock.scheduler._exchange_now",
        lambda: datetime(2026, 7, 29, 15, 10, tzinfo=EXCHANGE_TIMEZONE),
    )
    await failed.run_once("eod_control")

    restored = TaskScheduler(state_path=state_path)
    restored.register(_make_job("eod_control", JobFrequency.DAILY_AFTER_CLOSE))
    restored._load_state()
    status = restored.get_status()["jobs"]["eod_control"]

    assert status["status"] == "failed"
    assert status["last_error"] == "source timeout"
    assert status["next_retry_at"] is not None


def test_should_run_hourly(scheduler):
    job = _make_job("hourly_job", JobFrequency.HOURLY)
    scheduler.register(job)
    now = datetime.now()

    # Never run before → should run
    assert scheduler._should_run(job, now) is True

    # Just ran → should not run
    job.last_run = now
    assert scheduler._should_run(job, now) is False

    # Ran 2 hours ago → should run
    job.last_run = now - timedelta(hours=2)
    assert scheduler._should_run(job, now) is True


def test_daily_after_close_schedule_uses_shanghai_exchange_time(scheduler) -> None:
    job = _make_job("eod", JobFrequency.DAILY_AFTER_CLOSE)
    scheduler.register(job)

    assert scheduler._should_run(
        job, datetime(2026, 7, 28, 7, 4, tzinfo=timezone.utc)
    ) is False
    assert scheduler._should_run(
        job, datetime(2026, 7, 28, 7, 5, tzinfo=timezone.utc)
    ) is True


def test_loading_legacy_naive_state_interprets_timestamps_in_shanghai(tmp_path) -> None:
    state_path = tmp_path / "state.json"
    state_path.write_text(
        '{"jobs":{"eod":{"last_run":"2026-07-28T15:05:00","run_count":1}}}',
        encoding="utf-8",
    )
    scheduler = TaskScheduler(state_path=state_path)
    scheduler.register(_make_job("eod", JobFrequency.DAILY_AFTER_CLOSE))
    scheduler._load_state()

    assert scheduler._jobs["eod"].last_run is not None
    assert scheduler._jobs["eod"].last_run.utcoffset() == timedelta(hours=8)


@pytest.mark.asyncio
async def test_default_jobs_include_nonexecuting_public_eod_desk_observation() -> None:
    job = next(
        job for job in create_default_jobs()
        if job.name == "record_public_market_desk_eod_observation"
    )
    expected = {"status": "recorded", "formal_decision_eligible": False, "no_order_execution": True}
    with patch(
        "astock.capabilities.run_public_market_desk_eod_observation",
        new=AsyncMock(return_value=expected),
    ) as record:
        result = await job.handler()

    assert job.frequency == JobFrequency.DAILY_AFTER_CLOSE
    assert result == expected
    record.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_default_jobs_include_nonexecuting_public_eod_discovery() -> None:
    job = next(
        job for job in create_default_jobs()
        if job.name == "record_public_market_desk_eod_discovery"
    )
    expected = {"status": "recorded", "formal_decision_eligible": False, "no_order_execution": True}
    with patch(
        "astock.capabilities.run_public_market_desk_eod_discovery",
        new=AsyncMock(return_value=expected),
    ) as record:
        result = await job.handler()

    assert job.frequency == JobFrequency.DAILY_AFTER_CLOSE
    assert result == expected
    record.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_default_jobs_include_nonmutating_strategy_review_queue_audit() -> None:
    job = next(
        job for job in create_default_jobs()
        if job.name == "audit_market_desk_strategy_reviews"
    )
    expected = {"due_count": 0, "research_only": True, "no_order_execution": True}
    with patch(
        "astock.capabilities.get_market_desk_review_queue",
        return_value=expected,
    ) as audit:
        result = await job.handler()

    assert job.frequency == JobFrequency.DAILY_AFTER_CLOSE
    assert result == expected
    audit.assert_called_once_with()


@pytest.mark.asyncio
async def test_default_jobs_include_nonmutating_discovery_research_queue_audit() -> None:
    job = next(
        job for job in create_default_jobs()
        if job.name == "audit_market_desk_discovery_research_queue"
    )
    expected = {"due_count": 0, "research_only": True, "no_order_execution": True}
    with patch(
        "astock.capabilities.get_market_desk_discovery_research_queue",
        return_value=expected,
    ) as audit:
        result = await job.handler()

    assert job.frequency == JobFrequency.DAILY_AFTER_CLOSE
    assert result == expected
    audit.assert_called_once_with()


@pytest.mark.asyncio
async def test_default_jobs_include_nonmutating_operational_readiness_audit() -> None:
    job = next(
        job for job in create_default_jobs()
        if job.name == "audit_market_desk_operational_readiness"
    )
    expected = {
        "formal_paper_desk_status": "blocked",
        "research_only": True,
        "no_order_execution": True,
    }
    with patch(
        "astock.capabilities.assess_market_desk_operational_readiness",
        return_value=expected,
    ) as audit:
        result = await job.handler()

    assert job.frequency == JobFrequency.DAILY_AFTER_CLOSE
    assert result == expected
    audit.assert_called_once_with()


@pytest.mark.asyncio
async def test_default_jobs_include_nonmutating_operating_maturity_audit() -> None:
    job = next(
        job for job in create_default_jobs()
        if job.name == "audit_market_desk_operating_maturity"
    )
    expected = {
        "maturity_status": "evidence_accumulating",
        "research_only": True,
        "no_order_execution": True,
    }
    with patch(
        "astock.capabilities.assess_market_desk_operating_maturity",
        return_value=expected,
    ) as audit:
        result = await job.handler()

    assert job.frequency == JobFrequency.DAILY_AFTER_CLOSE
    assert job.depends_on == ("audit_market_desk_operational_readiness",)
    assert result == expected
    audit.assert_called_once_with()
