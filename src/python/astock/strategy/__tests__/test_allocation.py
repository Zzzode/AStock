from __future__ import annotations

from astock.strategy.allocation import AllocationPolicy, allocate_multi_sleeve


def _equity_proposal(weight: float = 0.30) -> dict[str, object]:
    return {
        "strategy_id": "ashare_factor_tilt",
        "strategy_version": "v1",
        "as_of": "2026-08-14T00:00:00+00:00",
        "targets": [
            {
                "code": "000001",
                "target_weight": weight,
                "source_ref": "fixture",
                "exchange": "szse",
                "market": "ashare",
                "trading_state_as_of": "2026-08-13T23:50:00+00:00",
                "rationale": "x",
            }
        ],
        "source_refs": ["fixture:factor"],
        "warnings": [],
        "research_only": True,
        "no_order_execution": True,
        "formal_decision_eligible": False,
    }


def _crypto_proposal() -> dict[str, object]:
    return {
        "strategy_id": "crypto_liquid_tsmom",
        "strategy_version": "v1",
        "as_of": "2026-08-15T00:00:00+00:00",
        "targets": [
            {
                "asset_class": "crypto",
                "asset_id": "BTC",
                "symbol": "BTC-USDT",
                "venue": "regulated-example-a",
                "market_type": "perpetual",
                "short_eligible": True,
                "target_weight": 0.08,
                "source_ref": "fixture:crypto-bars",
                "rationale": "fixture",
            },
            {
                "asset_class": "crypto",
                "asset_id": "ETH",
                "symbol": "ETH-USDT",
                "venue": "regulated-example-b",
                "market_type": "spot",
                "short_eligible": False,
                "target_weight": 0.08,
                "source_ref": "fixture:crypto-bars",
                "rationale": "fixture",
            },
        ],
        "source_refs": ["fixture:crypto-bars"],
        "warnings": [],
        "research_only": True,
        "no_order_execution": True,
        "formal_decision_eligible": False,
        "data_quality": "point_in_time_verified",
        "data_assurance": {"status": "point_in_time_verified"},
        "access_gate": {"status": "research_only"},
    }


def _futures_proposal(
    *,
    capital: float = 100.0,
    target_contracts: int = 1,
    margin_per_contract: float = 50.0,
) -> dict[str, object]:
    return {
        "strategy_id": "domestic_futures_cta_tsmom",
        "strategy_version": "v1",
        "as_of": "2026-08-14T00:00:00+00:00",
        "capital": capital,
        "targets": [
            {
                "instrument_id": "IF",
                "active_contract": "IF2609",
                "target_contracts": target_contracts,
                "margin_required": abs(target_contracts) * margin_per_contract,
                "margin_per_contract": margin_per_contract,
                "reference_price": 100.0,
                "contract_multiplier": 5.0,
                "initial_margin_rate": margin_per_contract / 500.0,
                "source_ref": "fixture:cta-target",
                "contract_facts": {
                    "active_contract": "IF2609",
                    "as_of": "2026-08-14T00:00:00+00:00",
                    "source_ref": "fixture:contract-facts",
                    "data_quality": "point_in_time_verified",
                    "point_in_time_coverage": "verified",
                    "trading_status": "tradable",
                },
            }
        ],
        "source_refs": ["fixture:cta-target", "fixture:contract-facts"],
        "warnings": [],
        "research_only": True,
        "no_order_execution": True,
        "formal_decision_eligible": False,
    }


def _approved_crypto_ledger(proposal: dict[str, object]) -> dict[str, object]:
    artifact_id = "crypto-review-001"
    targets = proposal["targets"]
    assert isinstance(targets, list)
    approved_legs = []
    for target in targets:
        assert isinstance(target, dict)
        target["validation_artifact_id"] = artifact_id
        approved_legs.append(
            {
                "asset_id": str(target["asset_id"]),
                "symbol": str(target["symbol"]),
                "venue": str(target["venue"]),
                "market_type": str(target["market_type"]),
                "direction": "long" if float(target["target_weight"]) >= 0 else "short",
            }
        )
    proposal["formal_decision_eligible"] = True
    proposal["access_gate"] = {"status": "validated", "artifact_id": artifact_id}
    proposal["crypto_allocation_artifact_id"] = artifact_id
    return {
        "validated_access_artifacts": [
            {
                "artifact_id": artifact_id,
                "status": "validated",
                "formal_decision_eligible": True,
                "data_quality": "point_in_time_verified",
                "validator_id": "fixture-independent-validator",
                "source_ref": "fixture:review-record",
                "artifact_hash": "sha256:fixture",
                "validated_at": "2026-08-14T00:00:00+00:00",
                "expires_at": "2026-08-16T00:00:00+00:00",
                "approved_legs": approved_legs,
                "blockers": [],
                "errors": [],
                "degraded": False,
            }
        ],
        "validate_crypto_allocation_artifact": lambda artifact, proposal: True,
    }


def test_allocator_caps_equity_and_separates_ledgers() -> None:
    result = allocate_multi_sleeve({"factor": _equity_proposal()})

    assert result["state"] == "active"
    assert result["ledgers"]["security"]["total_target_weight"] == 0.1
    assert result["ledgers"]["futures"]["targets"] == []
    assert result["capital_waterfall"]["residual_cash_fraction"] == 0.9


def test_allocator_hard_veto_zeroes_all_proposed_targets() -> None:
    result = allocate_multi_sleeve(
        {"factor": _equity_proposal()},
        risk_budget={"hard_veto": True, "reason": "drawdown"},
    )

    assert result["state"] == "frozen"
    assert result["ledgers"]["security"]["targets"] == []
    assert "drawdown" in result["blockers"][0]


def test_allocator_does_not_double_first_target_when_merging_sleeves() -> None:
    second = _equity_proposal(0.20)
    result = allocate_multi_sleeve({"factor": _equity_proposal(), "event": second})

    assert result["ledgers"]["security"]["targets"][0]["target_weight"] == 0.1


def test_allocator_blocks_a_sleeve_that_exceeds_its_declared_budget() -> None:
    oversized = _equity_proposal()
    oversized["targets"] = [
        {
            "code": "000001",
            "target_weight": 0.30,
            "source_ref": "fixture",
            "exchange": "szse",
            "market": "ashare",
            "trading_state_as_of": "2026-08-13T23:50:00+00:00",
            "rationale": "x",
        },
        {
            "code": "000002",
            "target_weight": 0.30,
            "source_ref": "fixture",
            "exchange": "szse",
            "market": "ashare",
            "trading_state_as_of": "2026-08-13T23:50:00+00:00",
            "rationale": "y",
        },
    ]
    blocked = allocate_multi_sleeve({"factor": oversized})

    assert blocked["state"] == "blocked"
    assert "exceeds max_sleeve_budget_fraction" in blocked["blockers"][0]


def test_allocator_blocks_when_all_sleeves_produce_no_targets() -> None:
    empty = _equity_proposal()
    empty["targets"] = []
    result = allocate_multi_sleeve({"factor": empty})

    assert result["state"] == "blocked"
    assert result["blockers"] == ["no sleeve produced an eligible paper target"]


def test_allocator_rejects_unregistered_or_mismatched_target_schema() -> None:
    proposal = _equity_proposal()
    proposal["strategy_id"] = "unregistered"
    blocked = allocate_multi_sleeve({"unknown": proposal})
    assert blocked["state"] == "blocked"
    assert "not registered for an allocatable target schema" in blocked["blockers"][0]

    mismatched = _equity_proposal()
    mismatched["targets"] = [
        {
            "asset_class": "crypto",
            "asset_id": "BTC",
            "symbol": "BTC-USDT",
            "venue": "fixture-venue",
            "market_type": "spot",
            "target_weight": 0.01,
            "source_ref": "fixture:crypto",
        }
    ]
    blocked = allocate_multi_sleeve({"factor": mismatched})
    assert blocked["state"] == "blocked"
    assert "incompatible with strategy_id" in blocked["blockers"][0]


def test_allocator_blocks_arbitrary_research_only_crypto_json() -> None:
    result = allocate_multi_sleeve({"crypto": _crypto_proposal()})

    assert result["state"] == "blocked"
    assert result["ledgers"]["crypto"]["targets"] == []
    assert "not formally decision-eligible" in " ".join(result["blockers"])


def test_allocator_blocks_crypto_without_external_trusted_validator() -> None:
    proposal = _crypto_proposal()
    ledger = _approved_crypto_ledger(proposal)
    ledger.pop("validate_crypto_allocation_artifact")

    result = allocate_multi_sleeve({"crypto": proposal}, crypto_ledger=ledger)

    assert result["state"] == "blocked"
    assert "external trusted artifact validator" in " ".join(result["blockers"])


def test_allocator_preserves_crypto_legs_and_reports_gross_counterparty_exposure() -> None:
    proposal = _crypto_proposal()
    targets = proposal["targets"]
    assert isinstance(targets, list)
    targets[0]["target_weight"] = 0.04
    targets[0]["market_type"] = "spot"
    targets[0]["short_eligible"] = False
    targets[1]["target_weight"] = -0.04
    targets[1]["market_type"] = "perpetual"
    targets[1]["short_eligible"] = True
    targets.append(
        {
            "asset_class": "crypto",
            "asset_id": "BTC",
            "symbol": "BTC-USDT",
            "venue": "regulated-example-a",
            "market_type": "perpetual",
            "short_eligible": True,
            "target_weight": -0.04,
            "source_ref": "fixture:crypto-bars",
            "rationale": "separate counterparty fixture",
        }
    )
    ledger = _approved_crypto_ledger(proposal)

    result = allocate_multi_sleeve({"crypto": proposal}, crypto_ledger=ledger)

    assert result["state"] == "active"
    crypto_targets = result["ledgers"]["crypto"]["targets"]
    assert len(crypto_targets) == 3
    assert abs(result["ledgers"]["crypto"]["total_gross_target_weight"] - 0.1) <= 2e-8
    assert result["ledgers"]["crypto"]["net_target_weight"] < 0
    legs = result["ledgers"]["crypto"]["exposure_by_venue_market_direction"]
    assert {(item["venue"], item["market_type"], item["direction"]) for item in legs} == {
        ("regulated-example-a", "spot", "long"),
        ("regulated-example-a", "perpetual", "short"),
        ("regulated-example-b", "perpetual", "short"),
    }
    counterparties = result["ledgers"]["crypto"]["counterparty_exposures"]
    assert len(counterparties) == 2
    assert all(item["gross_target_weight"] > 0 for item in counterparties)
    venue_a = next(item for item in counterparties if item["venue"] == "regulated-example-a")
    assert venue_a["gross_target_weight"] > abs(venue_a["net_target_weight"])


def test_allocator_blocks_crypto_target_without_a_venue() -> None:
    proposal = _crypto_proposal()
    ledger = _approved_crypto_ledger(proposal)
    target = proposal["targets"][0]
    assert isinstance(target, dict)
    target.pop("venue")

    result = allocate_multi_sleeve({"crypto": proposal}, crypto_ledger=ledger)

    assert result["state"] == "blocked"
    assert "crypto targets require asset_id, symbol, venue, market_type, and source_ref" in result["blockers"][0]


def test_allocator_requires_a_common_nav_for_any_futures_sleeve() -> None:
    result = allocate_multi_sleeve({"cta": _futures_proposal()})

    assert result["state"] == "blocked"
    assert result["blockers"] == ["futures allocation requires risk_budget.allocation_capital"]


def test_allocator_rejects_mismatched_futures_proposal_capital() -> None:
    result = allocate_multi_sleeve(
        {"cta": _futures_proposal(capital=120.0)},
        risk_budget={"allocation_capital": 100.0},
    )

    assert result["state"] == "blocked"
    assert "does not match risk_budget.allocation_capital" in result["blockers"][0]


def test_allocator_integer_sizes_futures_before_margin_and_drops_zero_contracts() -> None:
    result = allocate_multi_sleeve(
        {"cta": _futures_proposal(capital=100.0, target_contracts=1, margin_per_contract=50.0)},
        risk_budget={"allocation_capital": 100.0},
    )

    assert result["state"] == "active"
    assert result["ledgers"]["futures"]["targets"] == []
    assert result["ledgers"]["futures"]["total_margin_fraction"] == 0.0
    assert result["capital_waterfall"]["residual_cash_fraction"] == 1.0


def test_allocator_recalculates_margin_from_per_contract_facts_not_declared_total() -> None:
    proposal = _futures_proposal(capital=1_000.0, target_contracts=2, margin_per_contract=50.0)
    raw_target = proposal["targets"][0]
    assert isinstance(raw_target, dict)
    raw_target["margin_required"] = 1.0

    result = allocate_multi_sleeve({"cta": proposal}, risk_budget={"allocation_capital": 1_000.0})

    assert result["state"] == "blocked"
    assert "does not equal integer contracts times point-in-time margin_per_contract" in result["blockers"][0]


def test_allocator_reconciles_equity_crypto_and_futures_in_one_cash_waterfall() -> None:
    equity = _equity_proposal(0.70)
    crypto = _crypto_proposal()
    crypto_targets = crypto["targets"]
    assert isinstance(crypto_targets, list)
    crypto_targets[:] = [crypto_targets[0]]
    crypto_targets[0]["target_weight"] = 0.10
    ledger = _approved_crypto_ledger(crypto)
    policy = AllocationPolicy(
        max_total_equity_weight=0.70,
        max_single_equity_weight=0.70,
        max_total_crypto_weight=0.10,
        max_single_crypto_weight=0.10,
        max_total_cash_asset_weight=0.80,
        max_total_futures_margin_fraction=0.25,
        max_sleeve_budget_fraction=1.0,
    )
    result = allocate_multi_sleeve(
        {
            "factor": equity,
            "crypto": crypto,
            "cta": _futures_proposal(capital=100.0, target_contracts=1, margin_per_contract=25.0),
        },
        crypto_ledger=ledger,
        risk_budget={"allocation_capital": 100.0},
        policy=policy,
    )

    assert result["state"] == "active"
    waterfall = result["capital_waterfall"]
    assert waterfall["equity_cash_commitment_fraction"] == 0.65625
    assert waterfall["crypto_gross_collateral_fraction"] == 0.09375
    assert waterfall["futures_margin_collateral_fraction"] == 0.25
    assert waterfall["total_committed_fraction"] == 1.0
    assert waterfall["residual_cash_fraction"] == 0.0
    assert waterfall["equity_cash_commitment"] == 65.625
    assert waterfall["futures_margin_collateral"] == 25.0


def test_allocator_blocks_futures_without_dated_margin_facts() -> None:
    proposal = _futures_proposal()
    target = proposal["targets"][0]
    assert isinstance(target, dict)
    target.pop("contract_facts")

    result = allocate_multi_sleeve({"cta": proposal}, risk_budget={"allocation_capital": 100.0})

    assert result["state"] == "blocked"
    assert result["blockers"] == ["cta: futures target requires dated contract_facts"]


def test_allocator_blocks_a_negative_spot_target_after_gate_validation() -> None:
    proposal = _crypto_proposal()
    target = proposal["targets"][1]
    assert isinstance(target, dict)
    target["target_weight"] = -0.08
    ledger = _approved_crypto_ledger(proposal)

    result = allocate_multi_sleeve({"crypto": proposal}, crypto_ledger=ledger)

    assert result["state"] == "blocked"
    assert "short-eligible perpetual market" in result["blockers"][0]
