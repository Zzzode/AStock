"""Agent 记忆存储模块

提供跨 session 持久化的记忆存储，供 Claude Code subagent 访问。
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """记忆条目"""

    agent_name: str           # Agent 名称
    session_id: str           # 会话 ID
    user_id: str              # 用户 ID
    key: str                  # 键
    value: Any                # 值
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "key": self.key,
            "value": self.value,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        """从字典创建"""
        return cls(
            agent_name=data["agent_name"],
            session_id=data["session_id"],
            user_id=data["user_id"],
            key=data["key"],
            value=data["value"],
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
        )


class MemoryStore:
    """Agent 记忆存储 - 跨 session 持久化"""

    def __init__(self, data_path: Optional[Path] = None):
        """初始化记忆存储

        Args:
            data_path: 数据存储路径，默认为 data/memory.json
        """
        self.data_path = data_path or Path("data/memory.json")
        self._cache: dict[str, list[MemoryEntry]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """确保数据已加载"""
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        """从文件加载记忆"""
        if not self.data_path.exists():
            self._cache = {}
            return

        try:
            with open(self.data_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self._cache = {}
            for key, entries in data.items():
                self._cache[key] = [MemoryEntry.from_dict(e) for e in entries]
        except Exception:
            self._cache = {}

    def _save(self) -> None:
        """保存记忆到文件"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for key, entries in self._cache.items():
            data[key] = [e.to_dict() for e in entries]

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _make_key(self, agent_name: str, user_id: str, key: str) -> str:
        """生成存储键"""
        return f"{agent_name}:{user_id}:{key}"

    async def store(
        self,
        agent_name: str,
        session_id: str,
        user_id: str,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
    ) -> None:
        """存储记忆

        Args:
            agent_name: Agent 名称
            session_id: 会话 ID
            user_id: 用户 ID
            key: 键
            value: 值
            ttl_seconds: 过期时间（秒），None 表示永不过期
        """
        self._ensure_loaded()

        expires_at = None
        if ttl_seconds:
            expires_at = datetime.now() + timedelta(seconds=ttl_seconds)

        entry = MemoryEntry(
            agent_name=agent_name,
            session_id=session_id,
            user_id=user_id,
            key=key,
            value=value,
            expires_at=expires_at,
        )

        storage_key = self._make_key(agent_name, user_id, key)
        if storage_key not in self._cache:
            self._cache[storage_key] = []

        # 添加新条目
        self._cache[storage_key].append(entry)
        self._save()

    async def recall(
        self,
        agent_name: str,
        user_id: str,
        key: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """回忆记忆

        Args:
            agent_name: Agent 名称
            user_id: 用户 ID
            key: 键
            limit: 返回数量限制

        Returns:
            记忆条目列表，按时间倒序
        """
        self._ensure_loaded()

        storage_key = self._make_key(agent_name, user_id, key)
        entries = self._cache.get(storage_key, [])

        # 过滤过期条目
        now = datetime.now()
        valid_entries = [
            e for e in entries
            if e.expires_at is None or e.expires_at > now
        ]

        # 按时间倒序排列
        valid_entries.sort(key=lambda x: x.created_at, reverse=True)

        return [e.to_dict() for e in valid_entries[:limit]]

    async def get_latest(
        self,
        agent_name: str,
        user_id: str,
        key: str,
    ) -> Optional[Any]:
        """获取最新的记忆值

        Args:
            agent_name: Agent 名称
            user_id: 用户 ID
            key: 键

        Returns:
            最新的记忆值，如果没有则返回 None
        """
        entries = await self.recall(agent_name, user_id, key, limit=1)
        if entries:
            return entries[0].get("value")
        return None

    async def get_session_history(
        self,
        user_id: str,
        agent_name: Optional[str] = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        """获取会话历史

        Args:
            user_id: 用户 ID
            agent_name: Agent 名称（可选，不指定则返回所有）
            limit: 返回数量限制

        Returns:
            会话历史列表
        """
        self._ensure_loaded()

        all_entries = []
        for storage_key, entries in self._cache.items():
            for entry in entries:
                if entry.user_id == user_id:
                    if agent_name is None or entry.agent_name == agent_name:
                        all_entries.append(entry)

        # 过滤过期条目
        now = datetime.now()
        valid_entries = [
            e for e in all_entries
            if e.expires_at is None or e.expires_at > now
        ]

        # 按时间倒序排列
        valid_entries.sort(key=lambda x: x.created_at, reverse=True)

        return [e.to_dict() for e in valid_entries[:limit]]

    async def clear(
        self,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> int:
        """清除记忆

        Args:
            agent_name: Agent 名称（可选）
            user_id: 用户 ID（可选）
            key: 键（可选）

        Returns:
            清除的条目数量
        """
        self._ensure_loaded()

        keys_to_delete = []
        count = 0

        for storage_key in list(self._cache.keys()):
            parts = storage_key.split(":", 2)
            if len(parts) != 3:
                continue

            entry_agent, entry_user, entry_key = parts

            # 检查是否匹配
            match = True
            if agent_name and entry_agent != agent_name:
                match = False
            if user_id and entry_user != user_id:
                match = False
            if key and entry_key != key:
                match = False

            if match:
                count += len(self._cache[storage_key])
                keys_to_delete.append(storage_key)

        for k in keys_to_delete:
            del self._cache[k]

        if keys_to_delete:
            self._save()

        return count


# 需要导入 timedelta
from datetime import timedelta