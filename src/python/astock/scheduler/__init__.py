"""Lightweight task scheduler for automated jobs.

Runs as an asyncio daemon that schedules recurring tasks:
- Prediction verification (daily after market close)
- Research trigger evaluation (hourly during trading)
- Data refresh (configurable)
- Report re-indexing (daily)

Designed to be started via CLI (`astock scheduler start`) or embedded
in the monitor service loop.
"""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

from ..utils import get_logger

logger = get_logger("scheduler")


class JobFrequency(StrEnum):
    HOURLY = "hourly"
    DAILY_AFTER_CLOSE = "daily_after_close"
    EVERY_5_MIN = "every_5_min"
    EVERY_30_MIN = "every_30_min"


class JobStatus(StrEnum):
    IDLE = "idle"
    RUNNING = "running"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ScheduledJob:
    """A recurring job definition."""

    name: str
    frequency: JobFrequency
    handler: Callable[[], Coroutine[Any, Any, dict[str, Any]]]
    enabled: bool = True
    last_run: Optional[datetime] = None
    last_result: Optional[dict[str, Any]] = None
    last_error: Optional[str] = None
    status: JobStatus = JobStatus.IDLE
    run_count: int = 0
    error_count: int = 0


@dataclass
class SchedulerState:
    """Persisted scheduler state."""

    jobs: dict[str, dict[str, Any]] = field(default_factory=dict)
    started_at: Optional[str] = None
    last_tick: Optional[str] = None


MARKET_CLOSE = time(15, 5)
MARKET_OPEN = time(9, 25)


class TaskScheduler:
    """Async task scheduler with configurable job frequencies."""

    def __init__(self, state_path: Optional[Path] = None):
        self.state_path = state_path or Path("data/scheduler-state.json")
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._tick_interval = 30  # seconds between schedule checks

    def register(self, job: ScheduledJob) -> None:
        """Register a job with the scheduler."""
        self._jobs[job.name] = job

    def unregister(self, name: str) -> None:
        if name in self._jobs:
            del self._jobs[name]

    def enable(self, name: str) -> None:
        if name in self._jobs:
            self._jobs[name].enabled = True
            self._jobs[name].status = JobStatus.IDLE

    def disable(self, name: str) -> None:
        if name in self._jobs:
            self._jobs[name].enabled = False
            self._jobs[name].status = JobStatus.DISABLED

    async def start(self) -> None:
        """Start the scheduler loop."""
        if self._running:
            return
        self._running = True
        self._load_state()
        self._task = asyncio.create_task(self._loop())
        logger.info(f"Scheduler started with {len(self._jobs)} jobs")

    async def stop(self) -> None:
        """Stop the scheduler."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._save_state()
        logger.info("Scheduler stopped")

    async def run_once(self, name: str) -> dict[str, Any]:
        """Manually trigger a single job."""
        job = self._jobs.get(name)
        if not job:
            return {"error": f"Job not found: {name}"}
        return await self._execute_job(job)

    def get_status(self) -> dict[str, Any]:
        """Get scheduler status."""
        return {
            "running": self._running,
            "job_count": len(self._jobs),
            "jobs": {
                name: {
                    "frequency": job.frequency.value,
                    "enabled": job.enabled,
                    "status": job.status.value,
                    "last_run": job.last_run.isoformat() if job.last_run else None,
                    "run_count": job.run_count,
                    "error_count": job.error_count,
                    "last_error": job.last_error,
                }
                for name, job in self._jobs.items()
            },
        }

    async def _loop(self) -> None:
        while self._running:
            try:
                now = datetime.now()
                for job in self._jobs.values():
                    if not job.enabled or job.status == JobStatus.RUNNING:
                        continue
                    if self._should_run(job, now):
                        asyncio.create_task(self._execute_job(job))
                await asyncio.sleep(self._tick_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}")
                await asyncio.sleep(self._tick_interval)

    def _should_run(self, job: ScheduledJob, now: datetime) -> bool:
        if job.last_run is None:
            if job.frequency == JobFrequency.DAILY_AFTER_CLOSE:
                return now.time() >= MARKET_CLOSE
            return True

        elapsed = now - job.last_run

        if job.frequency == JobFrequency.HOURLY:
            return elapsed >= timedelta(hours=1)
        elif job.frequency == JobFrequency.EVERY_5_MIN:
            return elapsed >= timedelta(minutes=5)
        elif job.frequency == JobFrequency.EVERY_30_MIN:
            return elapsed >= timedelta(minutes=30)
        elif job.frequency == JobFrequency.DAILY_AFTER_CLOSE:
            ran_today = job.last_run.date() == now.date()
            return not ran_today and now.time() >= MARKET_CLOSE
        return False

    async def _execute_job(self, job: ScheduledJob) -> dict[str, Any]:
        job.status = JobStatus.RUNNING
        job.last_run = datetime.now()
        job.run_count += 1
        try:
            result = await job.handler()
            job.last_result = result
            job.last_error = None
            job.status = JobStatus.IDLE
            logger.info(f"Job '{job.name}' completed successfully")
            self._save_state()
            return result
        except Exception as e:
            job.last_error = str(e)
            job.error_count += 1
            job.status = JobStatus.FAILED
            logger.error(f"Job '{job.name}' failed: {e}")
            self._save_state()
            return {"error": str(e)}

    def _load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            for name, state in raw.get("jobs", {}).items():
                if name in self._jobs:
                    job = self._jobs[name]
                    if state.get("last_run"):
                        job.last_run = datetime.fromisoformat(state["last_run"])
                    job.run_count = state.get("run_count", 0)
                    job.error_count = state.get("error_count", 0)
        except Exception:
            pass

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "updated_at": datetime.now().isoformat(),
            "jobs": {
                name: {
                    "last_run": job.last_run.isoformat() if job.last_run else None,
                    "run_count": job.run_count,
                    "error_count": job.error_count,
                    "last_error": job.last_error,
                }
                for name, job in self._jobs.items()
            },
        }
        self.state_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )


# ---------------------------------------------------------------------------
# Trigger evaluation engine
# ---------------------------------------------------------------------------


async def evaluate_research_triggers(
    *,
    db_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Evaluate monitoring_triggers in active research entries against current data.

    Checks price-based triggers (breakout above/below threshold) and returns
    which triggers fired.
    """
    from ..capabilities import DEFAULT_DB_PATH, DEFAULT_RESEARCH_LEDGER_PATH
    from ..research import ResearchLedger, ResearchObservation, ResearchStatus
    from ..storage import Database
    from ..quote import QuoteService

    db_path = db_path or DEFAULT_DB_PATH
    ledger_path = ledger_path or DEFAULT_RESEARCH_LEDGER_PATH

    ledger = ResearchLedger(ledger_path)
    active_entries = ledger.list_entries(status=ResearchStatus.ACTIVE, limit=100)
    monitoring_entries = ledger.list_entries(status=ResearchStatus.MONITORING, limit=100)
    all_entries = active_entries + monitoring_entries

    if not all_entries:
        return {"checked": 0, "triggered": []}

    db = Database(str(db_path))
    await db.connect()
    try:
        quote_service = QuoteService(db)
        triggered: list[dict[str, Any]] = []

        for entry in all_entries:
            if not entry.monitoring_triggers:
                continue

            for target_code in entry.targets:
                try:
                    quote = await quote_service.get_realtime_quote(target_code)
                except Exception:
                    continue

                if not quote or not isinstance(quote, dict):
                    continue

                current_price = float(quote.get("price", 0) or 0)
                if current_price <= 0:
                    continue

                for trigger in entry.monitoring_triggers:
                    fired = _evaluate_single_trigger(trigger, current_price)
                    if fired:
                        triggered.append({
                            "entry_id": entry.entry_id,
                            "target": target_code,
                            "trigger_name": trigger.name,
                            "condition": trigger.condition,
                            "current_price": current_price,
                            "threshold": trigger.threshold,
                        })
                        observation = ResearchObservation(
                            observation_type="trigger_fired",
                            note=f"Trigger '{trigger.name}' fired: price={current_price}, condition='{trigger.condition}'",
                            evidence={
                                "trigger_name": trigger.name,
                                "price": current_price,
                                "threshold": trigger.threshold,
                            },
                        )
                        try:
                            ledger.record_observation(entry.entry_id or "", observation)
                        except Exception:
                            pass

        return {
            "checked": len(all_entries),
            "triggered": triggered,
            "triggered_count": len(triggered),
        }
    finally:
        await db.close()


def _evaluate_single_trigger(trigger: Any, current_price: float) -> bool:
    """Evaluate a single trigger against current price."""
    if trigger.threshold is None:
        return False

    direction = (trigger.direction or "").lower()
    condition = (trigger.condition or "").lower()

    if "above" in condition or "突破" in condition or direction == "above":
        return current_price >= trigger.threshold
    elif "below" in condition or "跌破" in condition or direction == "below":
        return current_price <= trigger.threshold
    elif "cross" in condition:
        return current_price >= trigger.threshold

    return False


# ---------------------------------------------------------------------------
# Default job factory
# ---------------------------------------------------------------------------


def create_default_jobs() -> list[ScheduledJob]:
    """Create the default set of scheduled jobs."""

    async def _verify_predictions() -> dict[str, Any]:
        from ..capabilities import run_prediction_verification
        return await run_prediction_verification()

    async def _evaluate_triggers() -> dict[str, Any]:
        return await evaluate_research_triggers()

    async def _check_earnings_calendar() -> dict[str, Any]:
        from ..capabilities import get_earnings_calendar
        return await get_earnings_calendar(upcoming_only=True, days_ahead=7)

    return [
        ScheduledJob(
            name="verify_predictions",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_verify_predictions,
        ),
        ScheduledJob(
            name="evaluate_triggers",
            frequency=JobFrequency.HOURLY,
            handler=_evaluate_triggers,
        ),
        ScheduledJob(
            name="check_earnings_calendar",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_check_earnings_calendar,
        ),
    ]
