"""Bridge between research ledger and monitor service.

Syncs research entries' monitoring triggers to watch_items,
and feeds verification results back to remove/update monitoring rules.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ..research import ResearchEntry, ResearchLedger, ResearchStatus, ResearchTrigger
from ..storage import Database, WatchItem
from ..utils import get_logger

logger = get_logger("research_monitor_bridge")


async def sync_research_to_monitor(
    *,
    db_path: Optional[Path] = None,
    ledger_path: Optional[Path] = None,
) -> dict[str, Any]:
    """Sync active research entries' targets to watch_items.

    - Creates watch items for targets of ACTIVE/MONITORING entries
    - Sets conditions from monitoring_triggers
    - Removes watch items for INVALIDATED/CLOSED entries
    """
    from ..capabilities import DEFAULT_DB_PATH, DEFAULT_RESEARCH_LEDGER_PATH

    db_path = db_path or DEFAULT_DB_PATH
    ledger_path = ledger_path or DEFAULT_RESEARCH_LEDGER_PATH

    ledger = ResearchLedger(ledger_path)
    active = ledger.list_entries(status=ResearchStatus.ACTIVE, limit=200)
    monitoring = ledger.list_entries(status=ResearchStatus.MONITORING, limit=200)
    invalidated = ledger.list_entries(status=ResearchStatus.INVALIDATED, limit=200)
    closed = ledger.list_entries(status=ResearchStatus.CLOSED, limit=200)

    to_watch = active + monitoring
    to_remove = invalidated + closed

    db = Database(str(db_path))
    await db.connect()
    try:
        added: list[str] = []
        updated: list[str] = []
        removed: list[str] = []

        existing_items = await db.get_watch_items(enabled_only=False)
        existing_codes = {item.code for item in existing_items}

        for entry in to_watch:
            for target_code in entry.targets:
                conditions = _build_conditions(entry)
                if target_code not in existing_codes:
                    watch_item = WatchItem(
                        code=target_code,
                        name=entry.title[:50],
                        conditions=conditions,
                        alert_channels=["terminal"],
                        enabled=True,
                        created_at=datetime.now(),
                    )
                    await db.save_watch_item(watch_item)
                    added.append(target_code)
                    existing_codes.add(target_code)
                else:
                    existing_item = next(
                        (i for i in existing_items if i.code == target_code), None
                    )
                    if existing_item and conditions != existing_item.conditions:
                        merged_conditions = {**existing_item.conditions, **conditions}
                        updated_item = WatchItem(
                            code=target_code,
                            name=existing_item.name or entry.title[:50],
                            conditions=merged_conditions,
                            alert_channels=existing_item.alert_channels,
                            enabled=True,
                            created_at=existing_item.created_at,
                        )
                        await db.save_watch_item(updated_item)
                        updated.append(target_code)

        codes_to_remove = set()
        for entry in to_remove:
            for target_code in entry.targets:
                still_active = any(
                    target_code in e.targets for e in to_watch
                )
                if not still_active and target_code in existing_codes:
                    codes_to_remove.add(target_code)

        for code in codes_to_remove:
            await db.delete_watch_item(code)
            removed.append(code)

        return {
            "added": added,
            "updated": updated,
            "removed": removed,
            "total_watching": len(existing_codes) + len(added) - len(removed),
        }
    finally:
        await db.close()


async def handle_verification_feedback(
    *,
    code: str,
    hit_stop: bool,
    hit_target: bool,
    db_path: Optional[Path] = None,
) -> dict[str, Any]:
    """React to prediction verification results.

    - If stop was hit: disable the watch item
    - If target was hit: optionally update conditions (trailing stop)
    """
    from ..capabilities import DEFAULT_DB_PATH

    db_path = db_path or DEFAULT_DB_PATH
    db = Database(str(db_path))
    await db.connect()
    try:
        if hit_stop:
            await db.delete_watch_item(code)
            return {"action": "removed", "code": code, "reason": "stop_loss_hit"}
        elif hit_target:
            items = await db.get_watch_items(enabled_only=False)
            item = next((i for i in items if i.code == code), None)
            if item:
                new_conditions = dict(item.conditions)
                new_conditions["target_reached"] = True
                new_conditions["status"] = "trailing"
                updated = WatchItem(
                    code=code,
                    name=item.name,
                    conditions=new_conditions,
                    alert_channels=item.alert_channels,
                    enabled=True,
                    created_at=item.created_at,
                )
                await db.save_watch_item(updated)
                return {"action": "updated_trailing", "code": code}
        return {"action": "none", "code": code}
    finally:
        await db.close()


def _build_conditions(entry: ResearchEntry) -> dict[str, object]:
    """Convert research triggers to watch item conditions."""
    conditions: dict[str, object] = {}

    conditions["research_entry_id"] = entry.entry_id
    conditions["research_status"] = entry.status.value

    for trigger in entry.monitoring_triggers:
        key = f"trigger_{trigger.name}"
        conditions[key] = {
            "condition": trigger.condition,
            "direction": trigger.direction,
            "threshold": trigger.threshold,
            "metric": trigger.metric,
        }

    if entry.invalidation_conditions:
        conditions["invalidation"] = entry.invalidation_conditions

    return conditions
