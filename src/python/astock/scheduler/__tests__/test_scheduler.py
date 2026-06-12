"""Tests for task scheduler."""

import asyncio
from datetime import datetime, timedelta

import pytest

from astock.scheduler import (
    JobFrequency,
    JobStatus,
    ScheduledJob,
    TaskScheduler,
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
