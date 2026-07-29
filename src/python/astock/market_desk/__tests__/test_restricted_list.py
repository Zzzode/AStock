"""Tests for persistent, source-labelled restricted-list governance."""

import json
from pathlib import Path

from astock import capabilities
from astock.market_desk import (
    RestrictedListAttestation,
    RestrictedListEntry,
    RestrictedListStore,
)


def _entry(target: str, status: str = "restricted") -> RestrictedListEntry:
    return RestrictedListEntry(
        target=target,
        status=status,
        source_type="compliance_attestation",
        source_ref="compliance:2026-07-28",
        effective_at="2026-07-28T09:00:00+08:00",
        reviewed_by="compliance-officer",
        reviewed_at="2026-07-28T09:00:00+08:00",
        expires_at="2026-08-28T09:00:00+08:00",
    )


def test_store_reports_missing_stale_and_current_restricted_targets(tmp_path: Path) -> None:
    path = tmp_path / "restricted-list.json"
    store = RestrictedListStore(path)
    assert store.health()["status"] == "missing"

    store.upsert(_entry("600460"))
    health = store.health()
    assert health["status"] == "current"
    assert health["active_targets"] == ["600460"]


def test_current_empty_list_requires_an_explicit_attestation(tmp_path: Path) -> None:
    store = RestrictedListStore(tmp_path / "restricted-list.json")
    store.attest(
        RestrictedListAttestation(
            source_type="compliance_attestation",
            source_ref="compliance:2026-07-28",
            reviewed_by="compliance-officer",
            reviewed_at="2026-07-28T09:00:00+08:00",
            expires_at="2026-08-28T09:00:00+08:00",
        )
    )
    health = store.health()
    assert health["status"] == "current"
    assert health["active_targets"] == []


def test_signed_attestation_requires_matching_compliance_key(tmp_path: Path) -> None:
    store = RestrictedListStore(tmp_path / "restricted-list.json")
    attestation = RestrictedListAttestation(
        source_type="compliance_attestation",
        source_ref="compliance:2026-07-28",
        reviewed_by="compliance-officer",
        reviewed_at="2026-07-28T09:00:00+08:00",
        expires_at="2026-08-28T09:00:00+08:00",
    )
    store.attest_signed(attestation, key_id="compliance-kms-v1", signing_key="test-secret")

    assert store.health(signature_key="test-secret", signature_key_id="compliance-kms-v1")["signature_status"] == "verified"
    assert store.health(signature_key="wrong-secret", signature_key_id="compliance-kms-v1")["signature_status"] == "invalid"
    assert store.health(signature_key="test-secret", signature_key_id="wrong-key-id")["signature_status"] == "invalid"
    assert store.health()["signature_status"] == "unverified"


def test_signed_payload_import_rejects_tampering(tmp_path: Path) -> None:
    source = RestrictedListStore(tmp_path / "source.json")
    source.attest_signed(
        RestrictedListAttestation(
            source_type="compliance_attestation",
            source_ref="compliance:2026-07-28",
            reviewed_by="compliance-officer",
            reviewed_at="2026-07-28T09:00:00+08:00",
            expires_at="2026-08-28T09:00:00+08:00",
        ),
        key_id="compliance-kms-v1",
        signing_key="test-secret",
    )
    payload = json.loads(source.path.read_text(encoding="utf-8"))
    target = RestrictedListStore(tmp_path / "target.json")
    health = target.import_signed_payload(
        payload, signature_key="test-secret", signature_key_id="compliance-kms-v1"
    )
    assert health["signature_status"] == "verified"

    payload["entries"].append(_entry("600460").to_dict())
    try:
        target.import_signed_payload(
            payload, signature_key="test-secret", signature_key_id="compliance-kms-v1"
        )
    except ValueError as error:
        assert "cannot be verified" in str(error)
    else:
        raise AssertionError("tampered signed payload must be rejected")


def test_capability_blocks_missing_or_active_restricted_list(tmp_path: Path) -> None:
    candidate = {
        "targets": ["600460"],
        "compliance": {
            "research_only_disclosure": True,
            "no_execution_instruction": True,
            "conflicts_disclosed": True,
            "suitability_disclosure": True,
            "restricted": False,
            "mnpi_or_inside_information": False,
            "prohibited_claims": [],
        },
    }
    path = tmp_path / "restricted-list.json"
    missing = capabilities.evaluate_market_desk_candidate(
        candidate, regime="trend_risk_on", restricted_list_path=path
    )
    assert missing["decision"] == "watch"
    assert "compliance" in missing["failed_gates"]

    RestrictedListStore(path).upsert(_entry("600460"))
    blocked = capabilities.evaluate_market_desk_candidate(
        candidate, regime="trend_risk_on", restricted_list_path=path
    )
    assert blocked["decision"] == "reject"
    assert "restricted" in blocked["control_blockers"][0].lower()
