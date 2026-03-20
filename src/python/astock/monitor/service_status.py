"""服务状态管理模块

管理监控服务的启动时间、运行状态等信息。
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

# 默认状态文件路径 - 项目根目录下的 data 目录
DEFAULT_STATUS_PATH = Path(__file__).parent.parent.parent.parent.parent / "data" / "service_status.json"


@dataclass
class ServiceInstance:
    """单个服务实例状态"""
    instance_id: str  # 实例标识
    pid: int  # 进程ID
    start_time: str  # ISO 格式时间
    stop_time: Optional[str] = None  # ISO 格式时间
    status: str = "running"  # running, stopped
    interval: int = 60  # 扫描间隔(秒)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceInstance":
        """从字典创建"""
        return cls(**data)


@dataclass
class ServiceHistory:
    """服务历史记录"""
    instance_id: str
    pid: int
    start_time: str
    stop_time: str
    duration_seconds: float  # 运行时长(秒)

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return asdict(self)


@dataclass
class ServiceStatus:
    """服务状态汇总"""
    instances: list[ServiceInstance] = field(default_factory=list)
    history: list[ServiceHistory] = field(default_factory=list)
    max_history: int = 100  # 最大历史记录数

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "instances": [i.to_dict() for i in self.instances],
            "history": [h.to_dict() for h in self.history],
            "max_history": self.max_history,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ServiceStatus":
        """从字典创建"""
        instances = [ServiceInstance.from_dict(i) for i in data.get("instances", [])]
        history = [ServiceHistory(**h) for h in data.get("history", [])]
        status = cls(instances=instances, history=history)
        status.max_history = data.get("max_history", 100)
        return status


class ServiceStatusManager:
    """服务状态管理器

    负责管理监控服务的启动/停止状态，支持持久化存储。
    支持多实例管理，使用文件锁保证并发安全。
    """

    def __init__(self, status_path: Optional[Path] = None):
        """初始化状态管理器

        Args:
            status_path: 状态文件路径，默认为 data/service_status.json
        """
        self.status_path = status_path or DEFAULT_STATUS_PATH
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """确保数据目录存在"""
        self.status_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_status(self) -> ServiceStatus:
        """加载服务状态

        Returns:
            服务状态对象
        """
        if not self.status_path.exists():
            return ServiceStatus()

        try:
            with open(self.status_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return ServiceStatus.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"加载服务状态失败，使用空状态: {e}")
            return ServiceStatus()

    def _save_status(self, status: ServiceStatus) -> None:
        """保存服务状态

        Args:
            status: 服务状态对象
        """
        # 使用文件锁保证并发安全
        with open(self.status_path, "w", encoding="utf-8") as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            try:
                json.dump(status.to_dict(), f, ensure_ascii=False, indent=2)
            finally:
                fcntl.flock(f.fileno(), fcntl.LOCK_UN)
        logger.debug(f"服务状态已保存到 {self.status_path}")

    def record_start(
        self, instance_id: str, interval: int = 60
    ) -> ServiceInstance:
        """记录服务启动

        Args:
            instance_id: 实例标识
            interval: 扫描间隔(秒)

        Returns:
            新创建的服务实例
        """
        status = self._load_status()

        # 检查是否已存在运行中的实例
        for instance in status.instances:
            if instance.instance_id == instance_id and instance.status == "running":
                logger.warning(f"实例 {instance_id} 已在运行中")
                return instance

        # 创建新实例
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

        logger.info(f"记录服务启动: {instance_id}, PID: {instance.pid}")
        return instance

    def record_stop(self, instance_id: str) -> Optional[ServiceHistory]:
        """记录服务停止

        Args:
            instance_id: 实例标识

        Returns:
            服务历史记录，如果实例不存在则返回 None
        """
        status = self._load_status()

        # 查找运行中的实例
        instance = None
        for i, inst in enumerate(status.instances):
            if inst.instance_id == instance_id and inst.status == "running":
                instance = status.instances.pop(i)
                break

        if not instance:
            logger.warning(f"未找到运行中的实例: {instance_id}")
            return None

        # 更新实例状态
        now = datetime.now()
        instance.stop_time = now.isoformat()
        instance.status = "stopped"

        # 计算运行时长
        start_time = datetime.fromisoformat(instance.start_time)
        duration = (now - start_time).total_seconds()

        # 添加到历史记录
        history = ServiceHistory(
            instance_id=instance.instance_id,
            pid=instance.pid,
            start_time=instance.start_time,
            stop_time=instance.stop_time,
            duration_seconds=duration,
        )

        # 限制历史记录数量
        status.history.insert(0, history)
        if len(status.history) > status.max_history:
            status.history = status.history[:status.max_history]

        self._save_status(status)

        logger.info(f"记录服务停止: {instance_id}, 运行时长: {format_duration(duration)}")
        return history

    def get_running_instances(self) -> list[ServiceInstance]:
        """获取所有运行中的实例

        Returns:
            运行中的实例列表
        """
        status = self._load_status()
        return [i for i in status.instances if i.status == "running"]

    def get_instance(self, instance_id: str) -> Optional[ServiceInstance]:
        """获取指定实例

        Args:
            instance_id: 实例标识

        Returns:
            服务实例，如果不存在则返回 None
        """
        status = self._load_status()
        for instance in status.instances:
            if instance.instance_id == instance_id:
                return instance
        return None

    def get_history(self, limit: int = 20) -> list[ServiceHistory]:
        """获取历史记录

        Args:
            limit: 返回数量限制

        Returns:
            历史记录列表
        """
        status = self._load_status()
        return status.history[:limit]

    def cleanup_stale_instances(self) -> int:
        """清理已停止的实例记录

        Returns:
            清理的实例数量
        """
        status = self._load_status()
        original_count = len(status.instances)

        # 移除已停止的实例
        status.instances = [i for i in status.instances if i.status == "running"]

        cleaned = original_count - len(status.instances)
        if cleaned > 0:
            self._save_status(status)
            logger.info(f"清理了 {cleaned} 个已停止的实例记录")

        return cleaned


def format_duration(seconds: float) -> str:
    """格式化运行时长

    将秒数转换为 X天X小时X分钟 格式

    Args:
        seconds: 秒数

    Returns:
        格式化的时长字符串
    """
    if seconds < 0:
        return "0分钟"

    delta = timedelta(seconds=seconds)
    days = delta.days
    hours, remainder = divmod(delta.seconds, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}天")
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}分钟")

    return "".join(parts)


def get_uptime_info(instance: ServiceInstance) -> dict[str, Any]:
    """获取实例运行时长信息

    Args:
        instance: 服务实例

    Returns:
        包含运行时长信息的字典
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
