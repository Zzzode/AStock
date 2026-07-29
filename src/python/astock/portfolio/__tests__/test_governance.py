import hashlib
import json
from datetime import datetime, timezone

import pytest

from astock.market_desk import RestrictedListAttestation, RestrictedListEntry, RestrictedListStore
from astock.portfolio.governance import (
    audit_paper_portfolio_governance,
    validate_governed_paper_entry,
    validate_governed_strategy_link,
)
from astock.research import ResearchEntry, ResearchLedger, ResearchObservation, ResearchStatus


def _active_plan_entry(ledger_path):
    plan = {
        "plan_id": "short-600460-20260728",
        "horizon": "short_term",
        "state": "active",
        "target": "600460",
        "thesis": "Test paper strategy.",
        "as_of": "2026-07-28T15:00:00+08:00",
        "entry_condition": "Condition is verified.",
        "invalidation_condition": "Risk condition breaks.",
        "review_at": "2026-07-29T15:00:00+08:00",
        "time_stop_at": "2026-08-07T15:00:00+08:00",
        "evidence_refs": ["snapshot:2026-07-28"],
    }
    entry = ResearchEntry(
        title="governed plan",
        thesis="test",
        targets=["600460"],
        target_type="strategy_plan",
        status=ResearchStatus.ACTIVE,
        metadata={"strategy_plan": plan},
    )
    entry.record_observation(
        ResearchObservation(
            observation_type="strategy_lifecycle_transition",
            note="released",
            observed_at=datetime.now(timezone.utc),
            evidence={
                "strategy_plan": plan,
                "release_assurance": {"verdict": "pass", "schema_version": "market-desk-paper-assurance.v1"},
            },
        )
    )
    return ResearchLedger(ledger_path).create(entry)


def test_governance_audit_blocks_linked_positions_without_retained_entry_evidence(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    entry = _active_plan_entry(ledger_path)
    portfolio = {
        "positions": {
            "600460": {
                "code": "600460",
                "strategy_entry_id": entry.entry_id,
                "strategy_plan_id": "short-600460-20260728",
            },
            "688001": {"code": "688001"},
        }
    }

    report = audit_paper_portfolio_governance(portfolio, ledger_path=ledger_path)

    assert report["governance_status"] == "blocked"
    assert report["governed_count"] == 0
    assert report["unlinked_legacy_count"] == 1
    assert report["entry_evidence_gap_count"] == 1
    assert report["entry_evidence_gap_positions"][0]["strategy_entry_id"] == entry.entry_id


def test_governed_link_requires_active_assured_matching_target(tmp_path):
    ledger_path = tmp_path / "ledger.json"
    entry = _active_plan_entry(ledger_path)

    link = validate_governed_strategy_link(
        entry_id=str(entry.entry_id), code="600460", ledger_path=ledger_path
    )

    assert link["strategy_entry_id"] == entry.entry_id
    assert link["release_assurance"]["verdict"] == "pass"


def test_governed_paper_entry_requires_frozen_entry_evidence_current_clearance_and_live_window(
    tmp_path, monkeypatch
):
    ledger_path = tmp_path / "ledger.json"
    entry = _active_plan_entry(ledger_path)
    raw_source_records = {"600460": {"code": "600460", "entry_condition": "confirmed"}}
    digest = hashlib.sha256(
        json.dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "raw_source_records": raw_source_records,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    archive_id = f"sha256:{digest}"
    archive_path = tmp_path / "entry-observation.json"
    archive_path.write_text(
        json.dumps(
            {
                "schema_version": "market_data_frozen_archive.v1",
                "source": "tushare_pro",
                "archive_id": archive_id,
                "raw_source_records": raw_source_records,
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY", "test-compliance-key")
    monkeypatch.setenv("RESTRICTED_LIST_SIGNING_KEY_ID", "test-compliance-authority")
    restricted_list_path = tmp_path / "restricted-list.json"
    store = RestrictedListStore(restricted_list_path)
    attestation = RestrictedListAttestation(
        source_type="compliance-source",
        source_ref="test-clearance",
        reviewed_by="compliance-officer",
        reviewed_at="2026-07-28T15:00:00+08:00",
        expires_at="2099-12-31T15:00:00+08:00",
    )
    store.attest_signed(
        attestation,
        key_id="test-compliance-authority",
        signing_key="test-compliance-key",
    )
    kwargs = {
        "entry_id": entry.entry_id,
        "code": "600460",
        "ledger_path": ledger_path,
        "entry_observed_at": "2026-07-28T16:00:00+08:00",
        "entry_observation_archive_path": archive_path,
        "restricted_list_path": restricted_list_path,
    }

    with pytest.raises(ValueError, match="entry-evidence-ref"):
        validate_governed_paper_entry(entry_evidence_refs=(), **kwargs)
    with pytest.raises(ValueError, match="review is due"):
        validate_governed_paper_entry(
            entry_evidence_refs=[f"entry-observation:{archive_id}"],
            entry_observed_at="2026-07-29T15:00:00+08:00",
            **{key: value for key, value in kwargs.items() if key != "entry_observed_at"},
        )

    entry_check = validate_governed_paper_entry(
        entry_evidence_refs=[f"entry-observation:{archive_id}"], **kwargs
    )
    assert entry_check["entry_evidence"]["observation_archive"]["archive_id"] == archive_id
    store.upsert(
        RestrictedListEntry(
            target="600460",
            status="restricted",
            source_type="compliance-source",
            source_ref="test-restricted",
            effective_at="2026-07-28T15:00:00+08:00",
            reviewed_by="compliance-officer",
            reviewed_at="2026-07-28T15:00:00+08:00",
            expires_at="2099-12-31T15:00:00+08:00",
        )
    )
    store.attest_signed(
        attestation,
        key_id="test-compliance-authority",
        signing_key="test-compliance-key",
    )
    with pytest.raises(ValueError, match="currently restricted"):
        validate_governed_paper_entry(
            entry_evidence_refs=[f"entry-observation:{archive_id}"], **kwargs
        )
