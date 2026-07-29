"""Auditable restricted-list governance for research-only desk decisions."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


@dataclass(frozen=True)
class RestrictedListEntry:
    """One externally sourced restricted-list or clearance record."""

    target: str
    status: str
    source_type: str
    source_ref: str
    effective_at: str
    reviewed_by: str
    reviewed_at: str
    expires_at: str | None = None
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.target.strip():
            raise ValueError("restricted-list entry requires a target")
        if self.status not in {"restricted", "cleared"}:
            raise ValueError("restricted-list status must be restricted or cleared")
        for key, value in (
            ("source_type", self.source_type),
            ("source_ref", self.source_ref),
            ("reviewed_by", self.reviewed_by),
        ):
            if not str(value).strip():
                raise ValueError(f"restricted-list entry requires {key}")
        effective = _parse_timestamp(self.effective_at, "effective_at")
        reviewed = _parse_timestamp(self.reviewed_at, "reviewed_at")
        expires = _parse_timestamp(self.expires_at, "expires_at") if self.expires_at else None
        if reviewed < effective:
            raise ValueError("restricted-list reviewed_at cannot precede effective_at")
        if expires is not None and expires < reviewed:
            raise ValueError("restricted-list expires_at cannot precede reviewed_at")

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "status": self.status,
            "source_type": self.source_type,
            "source_ref": self.source_ref,
            "effective_at": self.effective_at,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "expires_at": self.expires_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RestrictedListEntry":
        return cls(
            target=str(value.get("target") or "").strip(),
            status=str(value.get("status") or "").strip(),
            source_type=str(value.get("source_type") or "").strip(),
            source_ref=str(value.get("source_ref") or "").strip(),
            effective_at=str(value.get("effective_at") or "").strip(),
            reviewed_by=str(value.get("reviewed_by") or "").strip(),
            reviewed_at=str(value.get("reviewed_at") or "").strip(),
            expires_at=(str(value["expires_at"]).strip() if value.get("expires_at") else None),
            notes=str(value.get("notes") or "").strip(),
        )


@dataclass(frozen=True)
class RestrictedListAttestation:
    """A list-level review, including an explicitly empty current list."""

    source_type: str
    source_ref: str
    reviewed_by: str
    reviewed_at: str
    expires_at: str
    notes: str = ""

    def __post_init__(self) -> None:
        for key, value in (
            ("source_type", self.source_type),
            ("source_ref", self.source_ref),
            ("reviewed_by", self.reviewed_by),
        ):
            if not str(value).strip():
                raise ValueError(f"restricted-list attestation requires {key}")
        reviewed = _parse_timestamp(self.reviewed_at, "reviewed_at")
        expires = _parse_timestamp(self.expires_at, "expires_at")
        if expires < reviewed:
            raise ValueError("restricted-list attestation expires_at cannot precede reviewed_at")

    def to_dict(self) -> dict[str, str]:
        return {
            "source_type": self.source_type,
            "source_ref": self.source_ref,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at,
            "expires_at": self.expires_at,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "RestrictedListAttestation":
        return cls(
            source_type=str(value.get("source_type") or "").strip(),
            source_ref=str(value.get("source_ref") or "").strip(),
            reviewed_by=str(value.get("reviewed_by") or "").strip(),
            reviewed_at=str(value.get("reviewed_at") or "").strip(),
            expires_at=str(value.get("expires_at") or "").strip(),
            notes=str(value.get("notes") or "").strip(),
        )


class RestrictedListStore:
    """JSON-backed, source-labelled restricted-list authority.

    An empty list is permitted only when it has a current explicit clearance
    record. A missing, malformed, or expired list is not a clearance.
    """

    def __init__(self, path: Path) -> None:
        self.path = path

    def upsert(self, entry: RestrictedListEntry) -> RestrictedListEntry:
        payload = self._load_payload()
        entries = {item.target: item for item in self.list_entries()}
        entries[entry.target] = entry
        attestation = payload.get("attestation") if payload else None
        if not isinstance(attestation, Mapping):
            attestation = RestrictedListAttestation(
                source_type=entry.source_type,
                source_ref=entry.source_ref,
                reviewed_by=entry.reviewed_by,
                reviewed_at=entry.reviewed_at,
                expires_at=entry.expires_at or entry.reviewed_at,
                notes="Derived from first source-labelled restricted-list entry.",
            ).to_dict()
        self._save(entries.values(), attestation)
        return entry

    def attest(self, attestation: RestrictedListAttestation) -> RestrictedListAttestation:
        self._save(self.list_entries(), attestation.to_dict())
        return attestation

    def attest_signed(
        self,
        attestation: RestrictedListAttestation,
        *,
        key_id: str,
        signing_key: str,
    ) -> RestrictedListAttestation:
        """Write a compliance-authority attestation with a verifiable MAC.

        The shared key belongs in the external compliance/KMS boundary, never
        in the list file. Any later local edit invalidates the signature.
        """
        normalized_key_id = str(key_id).strip()
        if not normalized_key_id or not str(signing_key):
            raise ValueError("signed restricted-list attestation requires key_id and signing_key")
        entries = self.list_entries()
        signature = _sign_payload(entries, attestation.to_dict(), normalized_key_id, signing_key)
        self._save(entries, attestation.to_dict(), signature=signature)
        return attestation

    def import_signed_payload(
        self,
        payload: Mapping[str, Any],
        *,
        signature_key: str | None = None,
        signature_key_id: str | None = None,
    ) -> dict[str, Any]:
        """Accept only a complete externally signed compliance-list payload."""
        if str(payload.get("schema_version") or "") != "market-desk-restricted-list.v1":
            raise ValueError("signed restricted-list payload has an invalid schema_version")
        try:
            RestrictedListAttestation.from_dict(payload.get("attestation", {}))
        except ValueError as error:
            raise ValueError(f"signed restricted-list payload has an invalid attestation: {error}") from error
        if self._entries_from_payload(payload) is None:
            raise ValueError("signed restricted-list payload has invalid entries")
        key = signature_key if signature_key is not None else os.environ.get("RESTRICTED_LIST_SIGNING_KEY")
        key_id = signature_key_id if signature_key_id is not None else os.environ.get("RESTRICTED_LIST_SIGNING_KEY_ID")
        if _signature_status(payload, key, key_id) != "verified":
            raise ValueError("signed restricted-list payload signature cannot be verified")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(dict(payload), ensure_ascii=False, indent=2), encoding="utf-8")
        return self.health(signature_key=key, signature_key_id=key_id)

    def list_entries(self) -> list[RestrictedListEntry]:
        payload = self._load_payload()
        if payload is None:
            return []
        return self._entries_from_payload(payload) or []

    @staticmethod
    def _entries_from_payload(
        payload: Mapping[str, Any],
    ) -> list[RestrictedListEntry] | None:
        try:
            return [
                RestrictedListEntry.from_dict(item)
                for item in payload.get("entries", [])
                if isinstance(item, Mapping)
            ]
        except ValueError:
            return None

    def health(
        self,
        *,
        now: datetime | None = None,
        signature_key: str | None = None,
        signature_key_id: str | None = None,
    ) -> dict[str, Any]:
        current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
        payload = self._load_payload()
        if payload is None:
            return {"status": "missing", "signature_status": "missing", "active_targets": [], "stale_targets": [], "version": None}
        try:
            attestation = RestrictedListAttestation.from_dict(payload.get("attestation", {}))
        except ValueError:
            return {"status": "invalid_or_unattested", "signature_status": "invalid", "active_targets": [], "stale_targets": [], "version": None}
        signature_status = _signature_status(
            payload,
            signature_key if signature_key is not None else os.environ.get("RESTRICTED_LIST_SIGNING_KEY"),
            signature_key_id if signature_key_id is not None else os.environ.get("RESTRICTED_LIST_SIGNING_KEY_ID"),
        )
        attestation_expires = _parse_timestamp(attestation.expires_at, "expires_at")
        if attestation_expires < current:
            return {"status": "stale", "signature_status": signature_status, "active_targets": [], "stale_targets": [], "entry_count": 0, "version": _payload_version(payload)}
        entries = self.list_entries()
        active: list[str] = []
        stale: list[str] = []
        for entry in entries:
            expires = _parse_timestamp(entry.expires_at, "expires_at") if entry.expires_at else None
            if expires is not None and expires < current:
                stale.append(entry.target)
            elif entry.status == "restricted":
                active.append(entry.target)
        return {
            "status": "current" if not stale else "stale",
            "signature_status": signature_status,
            "active_targets": sorted(active),
            "stale_targets": sorted(stale),
            "entry_count": len(entries),
            "version": _payload_version(payload),
        }

    def _load_payload(self) -> dict[str, Any] | None:
        if not self.path.exists():
            return None
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return {}
        return payload if payload.get("schema_version") == "market-desk-restricted-list.v1" else {}

    def _save(
        self,
        entries: Any,
        attestation: Mapping[str, Any],
        *,
        signature: Mapping[str, Any] | None = None,
    ) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = {
            "schema_version": "market-desk-restricted-list.v1",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "attestation": dict(attestation),
            "entries": [item.to_dict() for item in sorted(entries, key=lambda item: item.target)],
        }
        if signature is not None:
            payload["signature"] = dict(signature)
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def _parse_timestamp(value: str | None, field_name: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"restricted-list {field_name} must be ISO-8601") from exc
    if parsed.tzinfo is None:
        raise ValueError(f"restricted-list {field_name} must include a timezone offset")
    return parsed


def _payload_version(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _sign_payload(
    entries: list[RestrictedListEntry],
    attestation: Mapping[str, Any],
    key_id: str,
    signing_key: str,
) -> dict[str, str]:
    content = _signature_content(entries, attestation)
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    value = hmac.new(signing_key.encode("utf-8"), content.encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "algorithm": "hmac-sha256",
        "key_id": key_id,
        "content_hash": content_hash,
        "value": value,
    }


def _signature_status(
    payload: Mapping[str, Any],
    signing_key: str | None,
    signing_key_id: str | None,
) -> str:
    signature = payload.get("signature")
    if not isinstance(signature, Mapping):
        return "unsigned"
    if str(signature.get("algorithm") or "") != "hmac-sha256":
        return "invalid"
    if not str(signature.get("key_id") or "").strip() or not str(signature.get("value") or "").strip():
        return "invalid"
    if not signing_key or not signing_key_id:
        return "unverified"
    if not hmac.compare_digest(str(signature.get("key_id") or ""), signing_key_id):
        return "invalid"
    entries = RestrictedListStore._entries_from_payload(payload)
    if entries is None:
        return "invalid"
    content = _signature_content(entries, payload.get("attestation", {}))
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    expected = hmac.new(signing_key.encode("utf-8"), content.encode("utf-8"), hashlib.sha256).hexdigest()
    return (
        "verified"
        if hmac.compare_digest(str(signature.get("content_hash") or ""), content_hash)
        and hmac.compare_digest(str(signature.get("value") or ""), expected)
        else "invalid"
    )


def _signature_content(entries: list[RestrictedListEntry], attestation: Mapping[str, Any]) -> str:
    return json.dumps(
        {
            "attestation": dict(attestation),
            "entries": [item.to_dict() for item in sorted(entries, key=lambda item: item.target)],
        },
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
