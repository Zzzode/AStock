"""Agent memory storage module

Provides cross-session persistent memory storage accessible by Claude Code subagents.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


@dataclass
class MemoryEntry:
    """Memory entry"""

    agent_name: str           # Agent name
    session_id: str           # Session ID
    user_id: str              # User ID
    key: str                  # Key
    value: Any                # Value
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convert to dictionary"""
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
        """Create from dictionary"""
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
    """Agent memory storage - cross-session persistence"""

    def __init__(self, data_path: Optional[Path] = None):
        """Initialize memory store

        Args:
            data_path: Data storage path, defaults to data/memory.json
        """
        self.data_path = data_path or Path("data/memory.json")
        self._cache: dict[str, list[MemoryEntry]] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Ensure data is loaded"""
        if not self._loaded:
            self._load()
            self._loaded = True

    def _load(self) -> None:
        """Load memory from file"""
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
        """Save memory to file"""
        self.data_path.parent.mkdir(parents=True, exist_ok=True)

        data = {}
        for key, entries in self._cache.items():
            data[key] = [e.to_dict() for e in entries]

        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _make_key(self, agent_name: str, user_id: str, key: str) -> str:
        """Generate storage key"""
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
        """Store memory

        Args:
            agent_name: Agent name
            session_id: Session ID
            user_id: User ID
            key: Key
            value: Value
            ttl_seconds: Expiration time (seconds), None means never expires
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

        # Add new entry
        self._cache[storage_key].append(entry)
        self._save()

    async def recall(
        self,
        agent_name: str,
        user_id: str,
        key: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Recall memory

        Args:
            agent_name: Agent name
            user_id: User ID
            key: Key
            limit: Return count limit

        Returns:
            List of memory entries, sorted by time descending
        """
        self._ensure_loaded()

        storage_key = self._make_key(agent_name, user_id, key)
        entries = self._cache.get(storage_key, [])

        # Filter expired entries
        now = datetime.now()
        valid_entries = [
            e for e in entries
            if e.expires_at is None or e.expires_at > now
        ]

        # Sort by time descending
        valid_entries.sort(key=lambda x: x.created_at, reverse=True)

        return [e.to_dict() for e in valid_entries[:limit]]

    async def get_latest(
        self,
        agent_name: str,
        user_id: str,
        key: str,
    ) -> Optional[Any]:
        """Get the latest memory value

        Args:
            agent_name: Agent name
            user_id: User ID
            key: Key

        Returns:
            Latest memory value, or None if not found
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
        """Get session history

        Args:
            user_id: User ID
            agent_name: Agent name (optional, returns all if not specified)
            limit: Return count limit

        Returns:
            Session history list
        """
        self._ensure_loaded()

        all_entries = []
        for storage_key, entries in self._cache.items():
            for entry in entries:
                if entry.user_id == user_id:
                    if agent_name is None or entry.agent_name == agent_name:
                        all_entries.append(entry)

        # Filter expired entries
        now = datetime.now()
        valid_entries = [
            e for e in all_entries
            if e.expires_at is None or e.expires_at > now
        ]

        # Sort by time descending
        valid_entries.sort(key=lambda x: x.created_at, reverse=True)

        return [e.to_dict() for e in valid_entries[:limit]]

    async def clear(
        self,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        key: Optional[str] = None,
    ) -> int:
        """Clear memory

        Args:
            agent_name: Agent name (optional)
            user_id: User ID (optional)
            key: Key (optional)

        Returns:
            Number of entries cleared
        """
        self._ensure_loaded()

        keys_to_delete = []
        count = 0

        for storage_key in list(self._cache.keys()):
            parts = storage_key.split(":", 2)
            if len(parts) != 3:
                continue

            entry_agent, entry_user, entry_key = parts

            # Check if matching
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


# Need to import timedelta
from datetime import timedelta
