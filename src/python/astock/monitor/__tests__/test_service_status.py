"""服务状态管理测试"""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

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
    """测试时长格式化"""

    def test_zero_seconds(self):
        assert format_duration(0) == "0分钟"

    def test_minutes_only(self):
        assert format_duration(120) == "2分钟"  # 2 minutes
        assert format_duration(180) == "3分钟"  # 3 minutes

    def test_hours_and_minutes(self):
        assert format_duration(3661) == "1小时1分钟"  # 1h 1m 1s

    def test_days_hours_minutes(self):
        assert format_duration(90120) == "1天1小时2分钟"  # 1d 1h 2m

    def test_days_only(self):
        assert format_duration(86400) == "1天"  # 1 day

    def test_negative_seconds(self):
        assert format_duration(-10) == "0分钟"


class TestServiceInstance:
    """测试服务实例"""

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
    """测试服务历史"""

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
    """测试服务状态"""

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
    """测试服务状态管理器"""

    @pytest.fixture
    def temp_status_path(self, tmp_path):
        """创建临时状态文件路径"""
        return tmp_path / "service_status.json"

    def test_record_start(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)
        instance = manager.record_start("test_instance", interval=30)

        assert instance.instance_id == "test_instance"
        assert instance.pid == os.getpid()
        assert instance.status == "running"
        assert instance.interval == 30

        # 验证文件已创建
        assert temp_status_path.exists()

    def test_record_stop(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # 先启动
        manager.record_start("test_instance")

        # 再停止
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

        # 启动两个实例
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

        # 获取不存在的实例
        not_found = manager.get_instance("nonexistent")
        assert not_found is None

    def test_get_history(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # 启动并停止
        manager.record_start("instance1")
        manager.record_stop("instance1")

        history = manager.get_history()
        assert len(history) == 1
        assert history[0].instance_id == "instance1"

    def test_max_history_limit(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)
        manager._save_status(ServiceStatus(max_history=3))

        # 创建 5 条历史记录
        for i in range(5):
            manager.record_start(f"instance{i}")
            manager.record_stop(f"instance{i}")

        history = manager.get_history()
        # 应该只保留最新的 3 条
        assert len(history) == 3
        # 最新的应该在前面
        assert history[0].instance_id == "instance4"

    def test_cleanup_stale_instances(self, temp_status_path):
        manager = ServiceStatusManager(status_path=temp_status_path)

        # 启动并停止
        manager.record_start("instance1")
        manager.record_stop("instance1")

        # 清理已停止的实例
        cleaned = manager.cleanup_stale_instances()
        assert cleaned >= 0


class TestGetUptimeInfo:
    """测试运行时长信息"""

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
