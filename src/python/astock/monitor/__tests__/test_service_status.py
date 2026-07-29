"""Service status management tests"""

import os
from datetime import datetime

import pytest

from astock.monitor.service_status import (
    ServiceStatusManager,
    ServiceInstance,
    ServiceHistory,
    ServiceStatus,
    format_duration,
    get_uptime_info,
)


class TestFormatDuration:
    """Test duration formatting"""

    def test_zero_seconds(self):
        assert format_duration(0) == "0 minutes"

    def test_minutes_only(self):
        assert format_duration(120) == "2 minutes"
        assert format_duration(180) == "3 minutes"

    def test_hours_and_minutes(self):
        assert format_duration(3661) == "1 hours 1 minutes"  # 1h 1m 1s

    def test_days_hours_minutes(self):
        assert format_duration(90120) == "1 days 1 hours 2 minutes"  # 1d 1h 2m

    def test_days_only(self):
        assert format_duration(86400) == "1 days"  # 1 day

    def test_negative_seconds(self):
        assert format_duration(-10) == "0 minutes"


class TestServiceInstance:
    """Test service instance"""

    def test_to_dict(self):
        instance = ServiceInstance(
            instance_id="test",
            pid=12345,
            start_time="2024-01-01T00:00:00",
            status="running",
            interval=60,
        )
        data = instance.to_dict()
        assert data["instance_id"] == "test"
        assert data["pid"] == 12345
        assert data["status"] == "running"

    def test_from_dict(self):
        data = {
            "instance_id": "test",
            "pid": 12345,
            "start_time": "2024-01-01T00:00:00",
            "stop_time": None,
            "status": "running",
            "interval": 60,
        }
        instance = ServiceInstance.from_dict(data)
        assert instance.instance_id == "test"
        assert instance.pid == 12345


class TestServiceHistory:
    """Test service history"""

    def test_to_dict(self):
        history = ServiceHistory(
            instance_id="test",
            pid=12345,
            start_time="2024-01-01T00:00:00",
            stop_time="2024-01-01T01:00:00",
            duration_seconds=3600,
        )
        data = history.to_dict()
        assert data["instance_id"] == "test"
        assert data["duration_seconds"] == 3600


class TestServiceStatus:
    """Test service status"""

    def test_to_dict(self):
        status = ServiceStatus()
        data = status.to_dict()
        assert "instances" in data
        assert "history" in data
        assert data["instances"] == []

    def test_from_dict(self):
        data = {
            "instances": [
                {
                    "instance_id": "test",
                    "pid": 12345,
                    "start_time": "2024-01-01T00:00:00",
                    "stop_time": None,
                    "status": "running",
                    "interval": 60,
                }
            ],
            "history": [
                {
                    "instance_id": "test",
                    "pid": 12345,
                    "start_time": "2024-01-01T00:00:00",
                    "stop_time": "2024-01-01T01:00:00",
                    "duration_seconds": 3600,
                }
            ],
            "max_history": 100,
        }
        status = ServiceStatus.from_dict(data)
        assert len(status.instances) == 1
        assert len(status.history) == 1


class TestServiceStatusManager:
    """Test service status manager"""

    @pytest.fixture
    def temp_status_path(self, tmp_path):
        """Create temporary status file path"""
        return tmp_path / "service_status.json"

    def test_record_start(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)
        instance = manager.record_start("test_instance", interval=30)

        assert instance.instance_id == "test_instance"
        assert instance.pid == os.getpid()
        assert instance.status == "running"
        assert instance.interval == 30

        # Verify file was created
        assert temp_status_path.exists()

    def test_record_stop(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # Start first
        manager.record_start("test_instance")

        # Then stop
        history = manager.record_stop("test_instance")

        assert history is not None
        assert history.instance_id == "test_instance"
        assert history.duration_seconds >= 0

    def test_stop_nonexistent_instance(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)
        history = manager.record_stop("nonexistent")
        assert history is None

    def test_get_running_instances(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # Start two instances
        manager.record_start("instance1")
        manager.record_start("instance2")

        running = manager.get_running_instances()
        assert len(running) == 2

    def test_get_instance(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)
        manager.record_start("test_instance")

        instance = manager.get_instance("test_instance")
        assert instance is not None
        assert instance.instance_id == "test_instance"

        # Get nonexistent instance
        not_found = manager.get_instance("nonexistent")
        assert not_found is None

    def test_get_history(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # Start and stop
        manager.record_start("instance1")
        manager.record_stop("instance1")

        history = manager.get_history()
        assert len(history) == 1
        assert history[0].instance_id == "instance1"

    def test_max_history_limit(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)
        manager._save_status(ServiceStatus(max_history=3))

        # Create 5 history records
        for i in range(5):
            manager.record_start(f"instance{i}")
            manager.record_stop(f"instance{i}")

        history = manager.get_history()
        # Should only keep the latest 3
        assert len(history) == 3
        # Most recent should be first
        assert history[0].instance_id == "instance4"

    def test_cleanup_stale_instances(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # Start and stop
        manager.record_start("instance1")
        manager.record_stop("instance1")

        # Clean up stopped instances
        cleaned = manager.cleanup_stale_instances()
        assert cleaned >= 0


class TestGetUptimeInfo:
    """Test uptime info retrieval"""

    def test_get_uptime_info(self):
        instance = ServiceInstance(
            instance_id="test",
            pid=12345,
            start_time=datetime.now().isoformat(),
            status="running",
            interval=60,
        )

        info = get_uptime_info(instance)
        assert "start_time" in info
        assert "start_time_formatted" in info
        assert "uptime_seconds" in info
        assert "uptime_formatted" in info
        assert "pid" in info
        assert info["pid"] == 12345
        assert info["status"] == "running"
