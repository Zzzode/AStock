from __future__ import annotations

import pytest

from astock import capabilities


def test_crypto_capability_fails_closed_without_explicit_legal_access_attestation() -> (
    None
):
    with pytest.raises(ValueError, match="lawful_crypto_market_access"):
        capabilities.build_crypto_time_series_momentum_proposal(
            {},
            {},
            as_of="2026-08-15T00:00:00Z",
            access_profile={"profile_id": "mainland-default"},
        )


def test_crypto_capability_rejects_a_china_mainland_personal_route() -> None:
    with pytest.raises(ValueError, match="China-mainland residents"):
        capabilities.build_crypto_time_series_momentum_proposal(
            {},
            {},
            as_of="2026-08-15T00:00:00Z",
            access_profile={
                "lawful_crypto_market_access": True,
                "residency_jurisdiction": "CN",
                "crypto_access_evidence": {
                    "as_of": "2026-08-15T00:00:00+00:00",
                    "source_ref": "fixture:jurisdiction",
                    "data_entitlement_source_ref": "fixture:data",
                    "custody_review_source_ref": "fixture:custody",
                    "approved_venues": ["fixture-venue"],
                    "permitted_market_types": ["spot"],
                },
            },
        )


def test_crypto_capability_preserves_the_non_inference_access_gate(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _proposal(*args: object, **kwargs: object) -> dict[str, object]:
        assert args == ({}, {"BTC": {"venue": "venue-a", "market_type": "spot"}})
        assert kwargs["as_of"] == "2026-08-15T00:00:00Z"
        return {"warnings": [], "research_only": True, "no_order_execution": True}

    monkeypatch.setattr(
        capabilities, "_build_crypto_time_series_momentum_proposal", _proposal
    )

    result = capabilities.build_crypto_time_series_momentum_proposal(
        {},
        {"BTC": {"venue": "venue-a", "market_type": "spot"}},
        as_of="2026-08-15T00:00:00Z",
        access_profile={
            "profile_id": "lawfully-documented-outside-mainland",
            "lawful_crypto_market_access": True,
            "residency_jurisdiction": "SG",
            "crypto_access_evidence": {
                "as_of": "2026-08-15T00:00:00+00:00",
                "source_ref": "fixture:jurisdiction-review",
                "data_entitlement_source_ref": "fixture:data-entitlement",
                "custody_review_source_ref": "fixture:custody-review",
                "approved_venues": ["venue-a"],
                "permitted_market_types": ["spot"],
            },
        },
    )

    assert result["access_gate"]["status"] == "research_only"
    assert "not a legal conclusion" in result["access_gate"]["notice"]
    assert "China-mainland" in result["warnings"][-1]


def test_futures_capability_rejects_string_boolean_and_requires_instrument_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    instrument = {
        "instrument_id": "IF",
        "active_contract": "IF2609",
        "exchange": "cffex",
        "group": "financial",
        "currency": "CNY",
        "multiplier": 300,
        "tick_size": 0.2,
        "initial_margin_rate": 0.12,
        "maintenance_margin_rate": 0.10,
        "as_of": "2026-08-15",
        "source_ref": "fixture:contract-master",
        "contract_lifecycle_coverage": "verified",
    }
    with pytest.raises(ValueError, match="futures_eligible must be boolean"):
        capabilities.build_domestic_futures_cta_proposal(
            {},
            {"IF": instrument},
            capital=100_000,
            access_profile={"futures_eligible": "false"},
        )

    def _proposal(*args: object, **kwargs: object) -> dict[str, object]:
        assert args == ({}, {"IF": instrument})
        return {"warnings": [], "research_only": True, "no_order_execution": True}

    monkeypatch.setattr(capabilities, "_build_domestic_futures_cta_proposal", _proposal)
    result = capabilities.build_domestic_futures_cta_proposal(
        {},
        {"IF": instrument},
        capital=100_000,
        access_profile={
            "futures_eligible": True,
            "futures_access_evidence": {
                "as_of": "2026-08-15",
                "source_ref": "fixture:broker-permission",
                "data_entitlement_source_ref": "fixture:data-entitlement",
                "permitted_exchanges": ["cffex"],
                "eligible_instruments": ["if"],
            },
        },
    )

    assert result["access_gate"]["futures_eligible"] is True
    assert result["access_gate"]["evidence"]["eligible_instruments"] == ["if"]
