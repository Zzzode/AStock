"""Service status management module

Manages monitor service startup time, running status, and other information.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Any
import fcntl

from ..utils import get_logger

logger = get_logger("service_status")

# Default status file path - data directory under project root
DEFAULT_STATUS_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "service_status.json"


@dataclass
class ServiceInstance:
    """Single service instance status"""
    instance_id: str  # Instance identifier
    pid: int  # Process ID
    start_time: str  # ISO format time
    stop_time: Optional[str] = None  # ISO format time
    status: str = "running"  # running, stopped
    interval: int = 60  # Scan interval (seconds)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceInstance":
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ServiceHistory:
    """Service history record"""
    instance_id: str
    pid: int
    start_time: str
    stop_time: str
    duration_seconds: float  # Running duration (seconds)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ServiceStatus:
    """Service status summary"""
    instances: list[ServiceInstance] = field(default_factory=list)
    history: list[ServiceHistory] = field(default_factory=list)
    max_history: int = 100  # Maximum history records

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "instances": [i.to_dict() for i in self.instances],
            "history": [h.to_dict() for h in self.history],
            "max_history": self.max_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceStatus":
        """Create from dictionary"""
        instances = [ServiceInstance.from_dict(i) for i in data.get("instances", [])]
        history = [ServiceHistory(**h) for h in data.get("history", [])]
        status = cls(instances=instances, history=history)
        status.max_history = data.get("max_history", 100)
        return status


class ServiceStatusManager:
    """Service status manager

    Manages monitor service start/stop status with persistent storage support.
    Supports multi-instance management with file locking for concurrency safety.
    """

    def __init__(self, status_path: Optional[Path] = None):
        """Initialize status manager

        Args:
            status_path: Status file path, defaults to data/service_status.json
        """
        self.status_path = status_path or DEFAULT_STATUS_PATH
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """Ensure data directory exists"""
        self.status_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_status(self) -> ServiceStatus:
        """Load service status

        Returns:
            Service status object
        """
        if not self.status_path.exists():
            return ServiceStatus()

        try:
            with open(self.status_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ServiceStatus.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load service status, using empty status: {e}")
            return ServiceStatus()

    def _save_status(self, status: ServiceStatus) -> None:
        """Save service status

        Args:
            status: Service status object
        """
        # Use file lock for concurrency safety
        with open(self.status_path, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(status.to_dict(), f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        logger.debug(f"Service status saved to {self.status_path}")

    def record_start(
        self, instance_id: str, interval: int = 60
    ) -> ServiceInstance:
        """Record service start

        Args:
            instance_id: Instance identifier
            interval: Scan interval (seconds)

        Returns:
            Newly created service instance
        """
        status = self._load_status()

        # Check if a running instance already exists
        for instance in status.instances:
            if instance.instance_id == instance_id and instance.status == "running":
                logger.warning(f"Instance {instance_id} is already running")
                return instance

        # Create new instance
        now = datetime.now()
        instance = ServiceInstance(
            instance_id=instance_id,
            pid=os.getpid(),
            start_time=now.isoformat(),
            status="running",
            interval=interval,
        )

        status.instances.append(instance)
        self._save_status(status)

        logger.info(f"Service start recorded: {instance_id}, PID: {instance.pid}")
        return instance

    def record_stop(self, instance_id: str) -> Optional[ServiceHistory]:
        """Record service stop

        Args:
            instance_id: Instance identifier

        Returns:
            Service history record, or None if instance not found
        """
        status = self._load_status()

        # Find running instance
        instance = None
        for i, inst in enumerate(status.instances):
            if inst.instance_id == instance_id and inst.status == "running":
                instance = status.instances.pop(i)
                break

        if not instance:
            logger.warning(f"Running instance not found: {instance_id}")
            return None

        # Update instance status
        now = datetime.now()
        instance.stop_time = now.isoformat()
        instance.status = "stopped"

        # Calculate running duration
        start_time = datetime.fromisoformat(instance.start_time)
        duration = (now - start_time).total_seconds()

        # Add to history
        history = ServiceHistory(
            instance_id=instance.instance_id,
            pid=instance.pid,
            start_time=instance.start_time,
            stop_time=instance.stop_time,
            duration_seconds=duration,
        )

        # Limit history record count
        status.history.insert(0, history)
        if len(status.history) > status.max_history:
            status.history = status.history[:status.max_history]

        self._save_status(status)

        logger.info(f"Service stop recorded: {instance_id}, uptime: {format_duration(duration)}")
        return history

    def get_running_instances(self) -> list[ServiceInstance]:
        """Get all running instances

        Returns:
            List of running instances
        """
        status = self._load_status()
        return [i for i in status.instances if i.status == "running"]

    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        """Get specified instance

        Args:
            instance_id: Instance identifier

        Returns:
            Service instance, or None if not found
        """
        status = self._load_status()
        for instance in status.instances:
            if instance.instance_id == instance_id:
                return instance
        return None

    def get_history(self, limit: int = 20) -> list[ServiceHistory]:
        """Get history records

        Args:
            limit: Return count limit

        Returns:
            List of history records
        """
        status = self._load_status()
        return status.history[:limit]

    def cleanup_stale_instances(self) -> int:
        """Clean up stopped instance records

        Returns:
            Number of instances cleaned up
        """
        status = self._load_status()
        original_count = len(status.instances)

        # Remove stopped instances
        status.instances = [i for i in status.instances if i.status == "running"]

        cleaned = original_count - len(status.instances)
        if cleaned > 0:
            self._save_status(status)
            logger.info(f"Cleaned up {cleaned} stopped instance records")

        return cleaned


def format_duration(seconds: float) -> str:
    """Format running duration

    Converts seconds to X days X hours X minutes format

    Args:
        seconds: Number of seconds

    Returns:
        Formatted duration string
    """
    if seconds < 0:
        return "0 minutes"

    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days} days")
    if hours > 0:
        parts.append(f"{hours} hours")
    if minutes > 0 or not parts:
        parts.append(f"{minutes} minutes")

    return " ".join(parts)


def get_uptime_info(instance: ServiceInstance) -> dict[str, Any]:
    """Get instance uptime information

    Args:
        instance: Service instance

    Returns:
        Dictionary containing uptime information
    """
    start_time = datetime.fromisoformat(instance.start_time)
    now = datetime.now()
    duration_seconds = (now - start_time).total_seconds()

    return {
        "start_time": instance.start_time,
        "start_time_formatted": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_seconds": duration_seconds,
        "uptime_formatted": format_duration(duration_seconds),
        "pid": instance.pid,
        "status": instance.status,
        "interval": instance.interval,
    }
