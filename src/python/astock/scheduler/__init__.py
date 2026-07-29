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
import os
import socket
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from enum import StrEnum
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional
from zoneinfo import ZoneInfo

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
    # Required for EOD controls that claim completion from immutable evidence.
    # The verifier validates the handler result independently before a skip or
    # recorded result can satisfy a downstream dependency.
    completion_verifier: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None
    depends_on: tuple[str, ...] = ()
    enabled: bool = True
    # ``last_run`` is the last successful completion, not an attempted run.
    # Keeping failures separate allows an after-close control to retry without
    # incorrectly treating a transient source outage as a completed daily job.
    last_run: Optional[datetime] = None
    # A deliberate skip (for example, an EOD packet outside a verified close)
    # is terminal for that session but must not satisfy downstream controls.
    last_skip_at: Optional[datetime] = None
    next_retry_at: Optional[datetime] = None
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
EXCHANGE_TIMEZONE = ZoneInfo("Asia/Shanghai")
RUNTIME_HEARTBEAT_MAX_AGE = timedelta(seconds=90)


class TaskScheduler:
    """Async task scheduler with configurable job frequencies."""

    def __init__(self, state_path: Optional[Path] = None):
        self.state_path = state_path or Path("data/scheduler-state.json")
        self._jobs: dict[str, ScheduledJob] = {}
        self._running = False
        self._task: Optional[asyncio.Task[None]] = None
        self._tick_interval = 30  # seconds between schedule checks
        self._runtime_state: dict[str, Any] = {}

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
        now = _exchange_now()
        self._runtime_state = {
            "status": "running",
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "started_at": now.isoformat(),
            "last_heartbeat": now.isoformat(),
        }
        self._save_state()
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
        self._runtime_state = {
            "status": "stopped",
            "hostname": socket.gethostname(),
            "stopped_at": _exchange_now().isoformat(),
        }
        self._save_state()
        logger.info("Scheduler stopped")

    async def run_once(self, name: str) -> dict[str, Any]:
        """Manually trigger one permitted job without bypassing EOD controls."""
        job = self._jobs.get(name)
        if not job:
            return {"error": f"Job not found: {name}"}
        if job.frequency == JobFrequency.DAILY_AFTER_CLOSE:
            now = _exchange_now()
            if not self._should_run(job, now):
                return {
                    "status": "skipped",
                    "reason": "manual_run_not_permitted_by_schedule",
                    "job": job.name,
                    "observed_at": now.isoformat(),
                    "dependency_blockers": self._dependency_blockers(job, now),
                }
        return await self._execute_job(job)

    def get_status(self) -> dict[str, Any]:
        """Get scheduler status."""
        runtime = self._runtime_health()
        reference_time = _exchange_now()
        return {
            "running": runtime["status"] == "running",
            "runtime": runtime,
            "job_count": len(self._jobs),
            "jobs": {
                name: {
                    "frequency": job.frequency.value,
                    "depends_on": list(job.depends_on),
                    "dependency_blockers": self._dependency_blockers(job, reference_time),
                    "enabled": job.enabled,
                    "status": job.status.value,
                    "last_run": job.last_run.isoformat() if job.last_run else None,
                    "last_skip_at": job.last_skip_at.isoformat() if job.last_skip_at else None,
                    "next_retry_at": job.next_retry_at.isoformat() if job.next_retry_at else None,
                    "run_count": job.run_count,
                    "error_count": job.error_count,
                    "last_error": job.last_error,
                    "last_result": job.last_result,
                }
                for name, job in self._jobs.items()
            },
        }

    async def _loop(self) -> None:
        while self._running:
            try:
                now = _exchange_now()
                self._touch_runtime_heartbeat(now)
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
        now = _as_exchange_time(now)
        if not self._dependencies_satisfied(job, now):
            return False
        if self._dependency_completion_requires_rerun(job, now):
            return True
        retry_at = (
            _as_exchange_time(job.next_retry_at)
            if job.next_retry_at is not None
            else None
        )
        if retry_at is not None and now < retry_at:
            return False
        if (
            job.frequency == JobFrequency.DAILY_AFTER_CLOSE
            and job.last_skip_at is not None
            and _as_exchange_time(job.last_skip_at).date() == now.date()
        ):
            return False
        if job.last_run is None:
            if job.frequency == JobFrequency.DAILY_AFTER_CLOSE:
                return now.time() >= MARKET_CLOSE
            return True

        last_run = _as_exchange_time(job.last_run)
        elapsed = now - last_run

        if job.frequency == JobFrequency.HOURLY:
            return elapsed >= timedelta(hours=1)
        elif job.frequency == JobFrequency.EVERY_5_MIN:
            return elapsed >= timedelta(minutes=5)
        elif job.frequency == JobFrequency.EVERY_30_MIN:
            return elapsed >= timedelta(minutes=30)
        elif job.frequency == JobFrequency.DAILY_AFTER_CLOSE:
            ran_today = last_run.date() == now.date()
            return not ran_today and now.time() >= MARKET_CLOSE
        return False

    def _dependency_completion_requires_rerun(
        self, job: ScheduledJob, now: datetime
    ) -> bool:
        """Re-run a dependent daily control after newer same-session inputs.

        A scheduler topology can be upgraded while a persisted state already
        contains a completion for the dependent control.  That historical
        completion cannot satisfy the new DAG if its predecessors completed
        later in the same exchange session.  Treat it as stale so the control
        is recomputed from the actual after-close evidence rather than being
        silently skipped until the next trading day.
        """
        if not job.depends_on or job.last_run is None:
            return False
        if job.frequency != JobFrequency.DAILY_AFTER_CLOSE:
            return False
        last_run = _as_exchange_time(job.last_run)
        if last_run.date() != now.date():
            return False
        predecessor_runs = [
            _as_exchange_time(self._jobs[name].last_run)
            for name in job.depends_on
            if name in self._jobs and self._jobs[name].last_run is not None
        ]
        return bool(predecessor_runs) and max(predecessor_runs) > last_run

    def _dependencies_satisfied(self, job: ScheduledJob, now: datetime) -> bool:
        """Require successful predecessor completion before a dependent control."""
        return not self._dependency_blockers(job, now)

    def _dependency_blockers(self, job: ScheduledJob, now: datetime) -> list[dict[str, str]]:
        """Explain why a dependent control cannot yet run."""
        blockers: list[dict[str, str]] = []
        for dependency_name in job.depends_on:
            dependency = self._jobs.get(dependency_name)
            if dependency is None:
                blockers.append({"job": dependency_name, "reason": "not_registered"})
                continue
            if dependency.status == JobStatus.RUNNING:
                blockers.append({"job": dependency_name, "reason": "running"})
                continue
            if dependency.last_run is None:
                blockers.append({"job": dependency_name, "reason": "never_successful"})
                continue
            if (
                dependency.frequency == JobFrequency.DAILY_AFTER_CLOSE
                and _as_exchange_time(dependency.last_run).date() != now.date()
            ):
                blockers.append({"job": dependency_name, "reason": "not_completed_for_session"})
        return blockers

    async def _execute_job(self, job: ScheduledJob) -> dict[str, Any]:
        job.status = JobStatus.RUNNING
        attempted_at = _exchange_now()
        job.run_count += 1
        try:
            result = await job.handler()
            completion_assurance = self._verify_completion(job, result)
            if completion_assurance is not None and completion_assurance.get("status") != "pass":
                failures = completion_assurance.get("failures", [])
                detail = "; ".join(str(item) for item in failures) or "unknown verifier failure"
                raise ValueError(f"completion verification failed: {detail}")
            if self._is_noncompletion_skip(result):
                job.last_skip_at = attempted_at
                job.next_retry_at = None
                job.last_result = result
                job.last_error = None
                job.status = JobStatus.IDLE
                logger.info(f"Job '{job.name}' skipped without completion evidence")
                self._save_state()
                return result
            job.last_run = attempted_at
            job.last_skip_at = None
            job.next_retry_at = None
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
            job.next_retry_at = attempted_at + _retry_delay(job.error_count)
            logger.error(f"Job '{job.name}' failed: {e}")
            self._save_state()
            return {"error": str(e)}

    @staticmethod
    def _verify_completion(
        job: ScheduledJob, result: Any
    ) -> Optional[dict[str, Any]]:
        """Run an EOD evidence verifier before recording scheduler completion."""
        if job.completion_verifier is None:
            return None
        if not isinstance(result, dict):
            return {"status": "blocked", "failures": ["job result is not a mapping"]}
        assurance = job.completion_verifier(result)
        if not isinstance(assurance, dict):
            return {"status": "blocked", "failures": ["completion verifier returned an invalid result"]}
        return assurance

    @staticmethod
    def _is_noncompletion_skip(result: Any) -> bool:
        """Return whether a handler deliberately skipped without EOD evidence.

        A repeated EOD job can safely reference an already verified archive via
        ``existing_archive_ids``.  Other ``skipped`` results have no current
        session evidence and therefore must not unblock an audit dependency.
        """
        if not isinstance(result, dict) or str(result.get("status") or "") != "skipped":
            return False
        existing_archives = result.get("existing_archive_ids")
        return not isinstance(existing_archives, list) or not existing_archives

    def _load_state(self) -> None:
        if not self.state_path.exists():
            return
        try:
            raw = json.loads(self.state_path.read_text(encoding="utf-8"))
            runtime = raw.get("runtime")
            self._runtime_state = dict(runtime) if isinstance(runtime, dict) else {}
            for name, state in raw.get("jobs", {}).items():
                if name in self._jobs:
                    job = self._jobs[name]
                    if state.get("last_run"):
                        job.last_run = _as_exchange_time(
                            datetime.fromisoformat(state["last_run"])
                        )
                    if state.get("last_skip_at"):
                        job.last_skip_at = _as_exchange_time(
                            datetime.fromisoformat(state["last_skip_at"])
                        )
                    if state.get("next_retry_at"):
                        job.next_retry_at = _as_exchange_time(
                            datetime.fromisoformat(state["next_retry_at"])
                        )
                    job.run_count = state.get("run_count", 0)
                    job.error_count = state.get("error_count", 0)
                    job.last_error = state.get("last_error")
                    persisted_result = state.get("last_result")
                    job.last_result = (
                        dict(persisted_result)
                        if isinstance(persisted_result, dict)
                        else None
                    )
                    persisted_status = state.get("status")
                    try:
                        job.status = JobStatus(
                            str(
                                persisted_status
                                or (
                                    JobStatus.FAILED
                                    if job.last_error and job.next_retry_at is not None
                                    else JobStatus.IDLE
                                )
                            )
                        )
                    except ValueError:
                        job.status = JobStatus.IDLE
        except Exception:
            pass

    def _save_state(self) -> None:
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "updated_at": _exchange_now().isoformat(),
            "runtime": self._runtime_state,
            "jobs": {
                name: {
                    "last_run": job.last_run.isoformat() if job.last_run else None,
                    "last_skip_at": job.last_skip_at.isoformat() if job.last_skip_at else None,
                    "next_retry_at": job.next_retry_at.isoformat() if job.next_retry_at else None,
                    "run_count": job.run_count,
                    "error_count": job.error_count,
                    "last_error": job.last_error,
                    "last_result": job.last_result,
                    "status": job.status.value,
                }
                for name, job in self._jobs.items()
            },
        }
        temporary_path = self.state_path.with_name(f".{self.state_path.name}.tmp")
        temporary_path.write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        temporary_path.replace(self.state_path)

    def _touch_runtime_heartbeat(self, now: datetime) -> None:
        """Persist a bounded liveness lease for out-of-process status readers."""
        self._runtime_state = {
            "status": "running",
            "pid": os.getpid(),
            "hostname": socket.gethostname(),
            "started_at": self._runtime_state.get("started_at", now.isoformat()),
            "last_heartbeat": now.isoformat(),
        }
        self._save_state()

    def _runtime_health(self) -> dict[str, Any]:
        """Return daemon liveness without trusting a stale PID alone."""
        runtime = dict(self._runtime_state)
        last_heartbeat = _parse_exchange_timestamp(runtime.get("last_heartbeat"))
        heartbeat_age_seconds = (
            max(0.0, (_exchange_now() - last_heartbeat).total_seconds())
            if last_heartbeat is not None
            else None
        )
        same_host = runtime.get("hostname") == socket.gethostname()
        pid = runtime.get("pid")
        pid_alive = _pid_is_alive(pid) if same_host else False
        fresh = (
            heartbeat_age_seconds is not None
            and heartbeat_age_seconds <= RUNTIME_HEARTBEAT_MAX_AGE.total_seconds()
        )
        declared_running = runtime.get("status") == "running"
        status = "running" if declared_running and same_host and pid_alive and fresh else (
            "stale" if declared_running else "stopped"
        )
        return {
            "status": status,
            "pid": pid,
            "hostname": runtime.get("hostname"),
            "started_at": runtime.get("started_at"),
            "last_heartbeat": runtime.get("last_heartbeat"),
            "heartbeat_age_seconds": heartbeat_age_seconds,
            "pid_alive": pid_alive,
            "same_host": same_host,
        }


def _retry_delay(error_count: int) -> timedelta:
    """Return bounded exponential retry delay for transient desk failures."""
    attempts = max(1, int(error_count))
    return timedelta(minutes=min(5 * (2 ** (attempts - 1)), 60))


def _exchange_now() -> datetime:
    """Return the A-share desk clock in its market timezone."""
    return datetime.now(EXCHANGE_TIMEZONE)


def _as_exchange_time(value: datetime) -> datetime:
    """Normalize legacy naive state as Shanghai time and convert aware values."""
    if value.tzinfo is None:
        return value.replace(tzinfo=EXCHANGE_TIMEZONE)
    return value.astimezone(EXCHANGE_TIMEZONE)


def _parse_exchange_timestamp(value: Any) -> Optional[datetime]:
    """Parse one persisted timestamp as an exchange-zone datetime."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return _as_exchange_time(datetime.fromisoformat(value))
    except ValueError:
        return None


def _pid_is_alive(value: Any) -> bool:
    """Check a local process ID without treating malformed values as live."""
    try:
        pid = int(value)
        if pid <= 0:
            return False
        os.kill(pid, 0)
        return True
    except (TypeError, ValueError, OSError):
        return False


def _verify_eod_archive_completion(
    result: dict[str, Any],
    *,
    archive_verifier: Callable[[str], dict[str, Any]],
    history_reader: Callable[[], dict[str, Any]],
) -> dict[str, Any]:
    """Independently verify an EOD archive before accepting job completion."""
    status = str(result.get("status") or "")
    if status == "recorded":
        archive_path = str(result.get("source_archive_path") or "").strip()
        archive_id = str(result.get("archive_id") or "").strip()
        if not archive_path or not archive_id:
            return {
                "status": "blocked",
                "failures": ["recorded EOD result lacks source_archive_path or archive_id"],
            }
        verification = archive_verifier(archive_path)
        if (
            verification.get("status") != "pass"
            or str(verification.get("archive_id") or "") != archive_id
            or not isinstance(verification.get("eod_validation"), dict)
            or verification["eod_validation"].get("status") != "pass"
        ):
            return {
                "status": "blocked",
                "failures": ["recorded EOD archive failed integrity, identity, or close-session verification"],
            }
        return {"status": "pass", "archive_ids": [archive_id]}
    if status != "skipped":
        return {"status": "blocked", "failures": ["EOD result has no recorded or idempotent-skip status"]}
    archive_ids = result.get("existing_archive_ids")
    if not isinstance(archive_ids, list) or not archive_ids:
        return {"status": "blocked", "failures": ["idempotent EOD skip lacks archive IDs"]}
    expected_ids = {str(value).strip() for value in archive_ids if str(value).strip()}
    if len(expected_ids) != len(archive_ids):
        return {"status": "blocked", "failures": ["idempotent EOD skip has malformed archive IDs"]}
    history = history_reader()
    records = history.get("records") if isinstance(history, dict) else None
    if not isinstance(records, list):
        return {"status": "blocked", "failures": ["EOD archive history is unavailable"]}
    verified_ids = {
        str(record.get("archive_id") or "")
        for record in records
        if isinstance(record, dict)
        and record.get("status") == "pass"
        and isinstance(record.get("eod_validation"), dict)
        and record["eod_validation"].get("status") == "pass"
    }
    missing_ids = sorted(expected_ids - verified_ids)
    if missing_ids:
        return {
            "status": "blocked",
            "failures": [f"idempotent EOD skip references unverified archives: {', '.join(missing_ids)}"],
        }
    return {"status": "pass", "archive_ids": sorted(expected_ids)}


def _verify_public_eod_observation_completion(result: dict[str, Any]) -> dict[str, Any]:
    """Verify public observation completion against content-addressed EOD evidence."""
    from ..capabilities import get_public_market_desk_observation_history
    from ..market_desk import verify_public_desk_observation_run

    return _verify_eod_archive_completion(
        result,
        archive_verifier=verify_public_desk_observation_run,
        history_reader=get_public_market_desk_observation_history,
    )


def _verify_public_eod_discovery_completion(result: dict[str, Any]) -> dict[str, Any]:
    """Verify public discovery completion against content-addressed EOD evidence."""
    from ..capabilities import get_public_market_desk_discovery_history
    from ..market_desk.discovery import verify_public_market_discovery_archive

    assurance = _verify_eod_archive_completion(
        result,
        archive_verifier=verify_public_market_discovery_archive,
        history_reader=get_public_market_desk_discovery_history,
    )
    if assurance.get("status") != "pass":
        return assurance
    archive_ids = set(assurance.get("archive_ids") or [])
    history = get_public_market_desk_discovery_history()
    records = history.get("records") if isinstance(history, dict) else None
    if not isinstance(records, list):
        return {
            "status": "blocked",
            "failures": ["public discovery history is unavailable for coverage verification"],
        }
    unusable = [
        archive_id
        for archive_id in archive_ids
        if not any(
            isinstance(record, dict)
            and str(record.get("archive_id") or "") == archive_id
            and isinstance(record.get("coverage_validation"), dict)
            and record["coverage_validation"].get("status") == "pass"
            for record in records
        )
    ]
    if unusable:
        return {
            "status": "blocked",
            "failures": [
                "EOD discovery archive lacks a usable public all-market cross-section: "
                + ", ".join(sorted(unusable))
            ],
        }
    return assurance


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

    async def _record_public_market_desk_eod_observation() -> dict[str, Any]:
        from ..capabilities import run_public_market_desk_eod_observation
        return await run_public_market_desk_eod_observation()

    async def _record_public_market_desk_eod_discovery() -> dict[str, Any]:
        from ..capabilities import run_public_market_desk_eod_discovery
        return await run_public_market_desk_eod_discovery()

    async def _audit_market_desk_strategy_reviews() -> dict[str, Any]:
        from ..capabilities import get_market_desk_review_queue
        return get_market_desk_review_queue()

    async def _audit_market_desk_discovery_research_queue() -> dict[str, Any]:
        from ..capabilities import get_market_desk_discovery_research_queue
        return get_market_desk_discovery_research_queue()

    async def _audit_market_desk_postmortem_queue() -> dict[str, Any]:
        from ..capabilities import get_market_desk_postmortem_queue
        return get_market_desk_postmortem_queue()

    async def _audit_market_desk_operational_readiness() -> dict[str, Any]:
        from ..capabilities import assess_market_desk_operational_readiness
        return assess_market_desk_operational_readiness()

    async def _audit_market_desk_operating_maturity() -> dict[str, Any]:
        from ..capabilities import assess_market_desk_operating_maturity
        return assess_market_desk_operating_maturity()

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
        ScheduledJob(
            name="record_public_market_desk_eod_observation",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_record_public_market_desk_eod_observation,
            completion_verifier=_verify_public_eod_observation_completion,
        ),
        ScheduledJob(
            name="record_public_market_desk_eod_discovery",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_record_public_market_desk_eod_discovery,
            completion_verifier=_verify_public_eod_discovery_completion,
        ),
        ScheduledJob(
            name="audit_market_desk_strategy_reviews",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_audit_market_desk_strategy_reviews,
        ),
        ScheduledJob(
            name="audit_market_desk_discovery_research_queue",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_audit_market_desk_discovery_research_queue,
        ),
        ScheduledJob(
            name="audit_market_desk_postmortem_queue",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_audit_market_desk_postmortem_queue,
        ),
        ScheduledJob(
            name="audit_market_desk_operational_readiness",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_audit_market_desk_operational_readiness,
            depends_on=(
                "record_public_market_desk_eod_observation",
                "record_public_market_desk_eod_discovery",
                "audit_market_desk_strategy_reviews",
                "audit_market_desk_discovery_research_queue",
                "audit_market_desk_postmortem_queue",
            ),
        ),
        ScheduledJob(
            name="audit_market_desk_operating_maturity",
            frequency=JobFrequency.DAILY_AFTER_CLOSE,
            handler=_audit_market_desk_operating_maturity,
            depends_on=("audit_market_desk_operational_readiness",),
        ),
    ]


def create_default_scheduler(*, state_path: Optional[Path] = None) -> TaskScheduler:
    """Build the one canonical scheduler topology used by every entry point.

    Status and manual-run commands must register the same jobs as the daemon;
    otherwise an empty, freshly constructed scheduler makes operating history
    invisible.  The monitor bridge is part of the topology because it carries
    research lifecycle changes into the observation layer.
    """
    from .bridge import sync_research_to_monitor

    scheduler = TaskScheduler(state_path=state_path)
    for job in create_default_jobs():
        scheduler.register(job)

    async def _sync_bridge() -> dict[str, Any]:
        return await sync_research_to_monitor()

    scheduler.register(
        ScheduledJob(
            name="sync_research_to_monitor",
            frequency=JobFrequency.EVERY_30_MIN,
            handler=_sync_bridge,
        )
    )
    return scheduler
