import pytest

from astock.strategy import PersonalAccessProfile, list_personal_strategy_catalog


def _catalog_by_id(
    profile: PersonalAccessProfile | None = None,
) -> dict[str, dict[str, object]]:
    return {
        str(item["strategy_id"]): item
        for item in list_personal_strategy_catalog(profile)
    }


def _futures_profile() -> PersonalAccessProfile:
    return PersonalAccessProfile.from_mapping(
        {
            "profile_id": "dated-domestic-futures",
            "futures_eligible": True,
            "futures_access_evidence": {
                "as_of": "2026-08-15",
                "source_ref": "fixture:broker-permission",
                "data_entitlement_source_ref": "fixture:market-data-entitlement",
                "permitted_exchanges": ["shfe"],
                "eligible_instruments": ["up"],
            },
        }
    )


def _crypto_profile() -> PersonalAccessProfile:
    return PersonalAccessProfile.from_mapping(
        {
            "profile_id": "dated-non-mainland-crypto-research",
            "lawful_crypto_market_access": True,
            "residency_jurisdiction": "SG",
            "crypto_access_evidence": {
                "as_of": "2026-08-15T00:00:00+00:00",
                "source_ref": "fixture:jurisdiction-review",
                "data_entitlement_source_ref": "fixture:crypto-data-entitlement",
                "custody_review_source_ref": "fixture:custody-review",
                "approved_venues": ["venue-a"],
                "permitted_market_types": ["spot", "perpetual"],
                "short_eligible_venues": ["venue-a"],
            },
        }
    )


def test_catalog_allows_domestic_futures_cta_only_when_futures_eligibility_is_recorded() -> (
    None
):
    unavailable = _catalog_by_id(PersonalAccessProfile())
    available = _catalog_by_id(_futures_profile())

    assert (
        unavailable["domestic_futures_cta_tsmom"]["eligibility"]["status"] == "blocked"
    )
    assert (
        available["domestic_futures_cta_tsmom"]["eligibility"]["status"]
        == "paper_eligible"
    )
    assert (
        available["domestic_futures_calendar_relative_value"]["eligibility"]["status"]
        == "research_only"
    )
    assert (
        available["global_market_neutral_stat_arb"]["eligibility"]["status"]
        == "blocked"
    )
    assert "institutional market structure" in " ".join(
        available["global_market_neutral_stat_arb"]["eligibility"]["blockers"]
    )


def test_catalog_covers_the_expanded_taxonomy_without_claiming_institutional_portability() -> (
    None
):
    default_catalog = _catalog_by_id()
    globally_documented = _catalog_by_id(
        PersonalAccessProfile(lawful_global_market_access=True)
    )

    assert {
        "global_macro_risk_balanced_allocation",
        "pe_style_public_market_underwriting",
        "private_credit_real_assets_underwriting",
        "public_merger_event_research",
        "ashare_factor_tilt",
        "domestic_futures_cta_tsmom",
        "domestic_futures_calendar_relative_value",
        "global_market_neutral_stat_arb",
        "global_carry_relative_value",
        "volatility_dispersion",
    } <= set(default_catalog)
    assert (
        default_catalog["global_macro_risk_balanced_allocation"]["eligibility"][
            "status"
        ]
        == "blocked"
    )
    assert (
        globally_documented["global_macro_risk_balanced_allocation"]["eligibility"][
            "status"
        ]
        == "research_only"
    )
    assert (
        default_catalog["pe_style_public_market_underwriting"]["eligibility"]["status"]
        == "research_only"
    )
    assert (
        default_catalog["private_credit_real_assets_underwriting"]["eligibility"][
            "status"
        ]
        == "research_only"
    )
    assert (
        default_catalog["public_merger_event_research"]["eligibility"]["status"]
        == "research_only"
    )
    assert (
        default_catalog["domestic_futures_calendar_relative_value"]["eligibility"][
            "status"
        ]
        == "blocked"
    )
    assert (
        default_catalog["global_carry_relative_value"]["eligibility"]["status"]
        == "blocked"
    )
    assert (
        default_catalog["volatility_dispersion"]["eligibility"]["status"] == "blocked"
    )


def test_catalog_has_a_non_mutable_market_translation_for_every_strategy() -> None:
    entries = list_personal_strategy_catalog(_futures_profile())
    for entry in entries:
        translation = entry["market_translation"]
        assert translation["research_only"] is True
        assert translation["no_order_execution"] is True
        assert translation["institutional_archetypes"]
        assert translation["personal_protocol"]
        assert translation["reference_urls"]
        assert translation["china_mainland"]["status"]
        assert translation["crypto_market"]["status"]

    catalog = _catalog_by_id(_futures_profile())
    assert (
        catalog["domestic_futures_cta_tsmom"]["market_translation"]["china_mainland"][
            "status"
        ]
        == "paper_implemented_if_account_and_contract_eligible"
    )
    assert (
        catalog["crypto_liquid_tsmom"]["market_translation"]["china_mainland"]["status"]
        == "not_a_personal_implementation_route"
    )
    catalog["ashare_factor_tilt"]["market_translation"]["personal_protocol"].append(
        "mutation"
    )
    fresh = _catalog_by_id(_futures_profile())
    assert (
        "mutation"
        not in fresh["ashare_factor_tilt"]["market_translation"]["personal_protocol"]
    )


def test_crypto_catalog_requires_a_self_attested_access_fact_but_never_treats_it_as_legal_clearance() -> (
    None
):
    inferred = _catalog_by_id(
        PersonalAccessProfile(
            lawful_global_market_access=True,
            permitted_markets=("global_crypto",),
        )
    )["crypto_liquid_tsmom"]
    declared_profile = _crypto_profile()
    declared = _catalog_by_id(declared_profile)["crypto_liquid_tsmom"]

    assert inferred["eligibility"]["status"] == "blocked"
    assert "self-attested lawful crypto-market access is not recorded" in " ".join(
        inferred["eligibility"]["blockers"]
    )
    assert declared_profile.to_dict()["lawful_crypto_market_access"] is True
    assert declared["eligibility"]["status"] == "research_only"
    assert declared["eligibility"]["availability"] == "research_only"
    assert "not a legal conclusion" in declared["eligibility"]["legal_access_notice"]
    assert "China mainland" in declared["eligibility"]["legal_access_notice"]


def test_catalog_rejects_string_boolean_and_undocumented_futures_contract_access() -> (
    None
):
    with pytest.raises(ValueError, match="futures_eligible must be boolean"):
        PersonalAccessProfile.from_mapping({"futures_eligible": "false"})

    incomplete = _catalog_by_id(PersonalAccessProfile(futures_eligible=True))
    assert (
        incomplete["domestic_futures_cta_tsmom"]["eligibility"]["status"] == "blocked"
    )
    assert "dated broker/exchange instrument eligibility evidence" in " ".join(
        incomplete["domestic_futures_cta_tsmom"]["eligibility"]["blockers"]
    )
