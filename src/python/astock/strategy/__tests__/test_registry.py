from pathlib import Path

import pytest
from astock.strategy.catalog import (
    get_personal_strategy_definition,
    strategy_catalog_entry,
)
from astock.strategy.models import PersonalAccessProfile
from astock.strategy.registry import StrategyRegistry


def test_registry_versions_transitions_and_retains_disabled_run(tmp_path: Path) -> None:
    registry = StrategyRegistry(tmp_path / "registry.db")
    definition = get_personal_strategy_definition("domestic_futures_cta_tsmom")
    registered = registry.register_definition(
        definition,
        source_ids=["catalog:domestic_futures_cta_tsmom:v1"],
        registered_at="2026-08-14T00:00:00+00:00",
    )
    assert registered["lifecycle"] == "paper"
    disabled = registry.transition_lifecycle(
        definition.strategy_id,
        definition.version,
        "disabled",
        evidence={"reason": "review", "source_ids": ["review:fixture"]},
        occurred_at="2026-08-14T01:00:00+00:00",
    )
    assert disabled["lifecycle"] == "disabled"
    run = registry.record_run(
        definition.strategy_id,
        definition.version,
        {
            "strategy_id": definition.strategy_id,
            "strategy_version": definition.version,
            "result": "archival replay",
            "research_only": True,
            "no_order_execution": True,
        },
        source_ids=["archive:abc"],
        recorded_at="2026-08-14T02:00:00+00:00",
    )
    assert run["lifecycle_at_run"] == "disabled"
    assert run["no_order_execution"] is True


def test_registry_refuses_mutable_redefinition_and_invalid_transition(
    tmp_path: Path,
) -> None:
    registry = StrategyRegistry(tmp_path / "registry.db")
    definition = get_personal_strategy_definition("ashare_factor_tilt")
    registry.register_definition(definition, source_ids=["catalog:factor"])
    changed = definition.to_dict()
    changed["name"] = "different"
    with pytest.raises(ValueError, match="different immutable"):
        registry.register_definition(changed, source_ids=["catalog:factor"])
    with pytest.raises(ValueError, match="not allowed"):
        registry.transition_lifecycle(
            definition.strategy_id,
            definition.version,
            "review",
            evidence={"reason": "skip", "source_ids": ["review:fixture"]},
        )


def test_registry_requires_a_source_for_lifecycle_evidence(tmp_path: Path) -> None:
    registry = StrategyRegistry(tmp_path / "registry.db")
    definition = get_personal_strategy_definition("ashare_factor_tilt")
    registry.register_definition(definition, source_ids=["catalog:factor"])
    with pytest.raises(ValueError, match="source identifier"):
        registry.transition_lifecycle(
            definition.strategy_id,
            definition.version,
            "paper",
            evidence={"reason": "reviewed"},
        )


def test_registry_does_not_hash_access_profile_eligibility_as_definition(
    tmp_path: Path,
) -> None:
    registry = StrategyRegistry(tmp_path / "registry.db")
    definition = get_personal_strategy_definition("domestic_futures_cta_tsmom")
    first = strategy_catalog_entry(
        definition, PersonalAccessProfile(futures_eligible=False)
    )
    second = strategy_catalog_entry(
        definition, PersonalAccessProfile(futures_eligible=True)
    )
    registry.register_definition(first, source_ids=["catalog:cta"])
    registered = registry.register_definition(second, source_ids=["catalog:cta"])
    assert registered["strategy_id"] == definition.strategy_id


def test_registry_rejects_incomplete_definition_and_cross_strategy_run(
    tmp_path: Path,
) -> None:
    registry = StrategyRegistry(tmp_path / "registry.db")
    with pytest.raises(ValueError, match="economic_engine"):
        registry.register_definition(
            {
                "strategy_id": "unsafe",
                "version": "v1",
                "name": "unsafe",
                "family": "unsafe",
                "availability": "conditional",
                "lifecycle": "paper",
                "research_only": True,
                "no_order_execution": True,
            },
            source_ids=["fixture:definition"],
        )

    definition = get_personal_strategy_definition("ashare_factor_tilt")
    registry.register_definition(definition, source_ids=["catalog:factor"])
    with pytest.raises(ValueError, match="strategy_id does not match"):
        registry.record_run(
            definition.strategy_id,
            definition.version,
            {
                "strategy_id": "another_strategy",
                "strategy_version": definition.version,
                "research_only": True,
                "no_order_execution": True,
            },
            source_ids=["fixture:run"],
        )
