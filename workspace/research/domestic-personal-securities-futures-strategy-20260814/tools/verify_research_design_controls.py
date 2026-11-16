#!/usr/bin/env python3
"""Validate draft data, universe and replay-design controls.

This checker verifies only that the successor case documents its unresolved
requirements consistently. A PASS never indicates data entitlement, a valid
replay, product admission, allocation or investment action.
"""

from __future__ import annotations

import json
import sys
import csv
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]


def reject_duplicate_object_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def load_json(relative_path: str) -> Any:
    return json.loads(
        (CASE_DIR / relative_path).read_text(encoding="utf-8"),
        object_pairs_hook=reject_duplicate_object_keys,
    )


def load_text(relative_path: str) -> str:
    return (CASE_DIR / relative_path).read_text(encoding="utf-8")


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def contains_text(value: Any, expected: str) -> bool:
    return expected in json.dumps(value, ensure_ascii=False)


def require_texts(
    value: Any, expected_values: tuple[str, ...], context: str, failures: list[str]
) -> None:
    for expected in expected_values:
        require(
            contains_text(value, expected),
            f"{context} missing required control: {expected}",
            failures,
        )


def column_names(table: Any) -> set[str]:
    columns = table.get("columns", []) if isinstance(table, dict) else []
    return {
        column[0]
        for column in columns
        if isinstance(column, list) and column and isinstance(column[0], str)
    }


def require_table_columns(
    table_by_id: dict[str, Any],
    table_id: str,
    expected_columns: set[str],
    failures: list[str],
) -> None:
    actual_columns = column_names(table_by_id.get(table_id, {}))
    missing = expected_columns - actual_columns
    require(
        not missing,
        f"{table_id} missing required machine-testable columns: {', '.join(sorted(missing))}",
        failures,
    )


def main() -> int:
    failures: list[str] = []

    source_ids = {
        item["source_id"]
        for item in load_json("data/source_registry.json")
        if "source_id" in item
    }
    unresolved = load_json("unresolved_requirements.json")
    unresolved_by_id = {
        item["id"]: item for item in unresolved.get("requirements", [])
    }

    contract = load_json("data/data_acquisition_contract_20260814.json")
    for field in (
        "contract_id",
        "schema_version",
        "version",
        "status",
        "portfolio_q",
        "data_dictionary_template",
        "freeze_control",
        "entitlement_control",
        "universe_coverage_control",
        "global_provenance_controls",
        "packages",
        "requirement_closure_matrix",
        "entry_gate_to_formal_replay",
    ):
        require(field in contract, f"data contract missing {field}", failures)
    require(
        contract.get("status") == "draft_not_frozen_no_entitlement_no_replay",
        "data contract status must remain draft/not frozen/no entitlement/no replay",
        failures,
    )
    require(
        contract.get("portfolio_q") == 0,
        "data contract must retain portfolio_q=0",
        failures,
    )
    require(
        set(contract.get("source_dependencies", [])) <= source_ids,
        "data contract has an unresolved source dependency",
        failures,
    )
    require(
        contract.get("freeze_control", {}).get("state") == "not_frozen",
        "data contract freeze state must remain not_frozen",
        failures,
    )
    require(
        contract.get("entitlement_control", {}).get("state") == "not_obtained",
        "data contract entitlement state must remain not_obtained",
        failures,
    )
    require(
        contract.get("contract_id") == "DPSFS-DAC-v12"
        and contract.get("schema_version") == "data_acquisition_contract.v12"
        and contract.get("version") == 12,
        "data contract must be the versioned DPSFS-DAC-v12 draft",
        failures,
    )
    require(
        contract.get("data_dictionary_template", {}).get("dictionary_id") == "DPSFS-DD-v8",
        "data contract must bind the DPSFS-DD-v8 dictionary template",
        failures,
    )
    require(
        contract.get("data_dictionary_template", {}).get("status")
        == "template_not_frozen_no_data",
        "data contract dictionary template must remain not frozen/no data",
        failures,
    )
    freeze_fields = contract.get("freeze_control", {}).get(
        "required_freeze_record", {}
    ).get("required_fields", [])
    for field in (
        "formal_replay_protocol_id",
        "formal_replay_protocol_version",
        "formal_replay_protocol_sha256",
        "u0_snapshot_sha256",
        "u0_to_t2_derivation_audit_sha256",
        "data_dictionary_sha256",
        "risk_feasibility_control_sha256",
        "order_state_transition_matrix_sha256",
        "expected_candidate_endpoint_count",
        "expected_primary_holdout_candidate_endpoint_count",
        "replay_run_freeze_record_sha256",
        "endpoint_calculation_population_policy_sha256",
        "portfolio_unitization_positions_lots_cashflow_reconciliation_policy_sha256",
        "fill_leg_partial_fill_allocation_policy_sha256",
        "broker_tax_component_policy_sha256",
        "execution_settlement_state_policy_sha256",
        "prospective_state_configuration_coverage_policy_sha256",
    ):
        require(
            field in freeze_fields,
            f"data-contract freeze record missing {field}",
            failures,
        )

    require_texts(
        contract.get("revision_history", []),
        (
            '"version": 12',
            "robust interpretation",
            "primary-holdout predicate/invalidation",
            "usable-strategy/risk-feasibility",
            "endpoint",
            "reservation",
        ),
        "data-contract version history",
        failures,
    )
    require_texts(
        contract.get("universe_coverage_control", {}),
        (
            "U0 snapshot hash",
            "class-specific accepted data package",
            "coverage-restricted",
            "manual nomination",
        ),
        "data-contract universe coverage control",
        failures,
    )

    access_feasibility = load_json("data/data_access_feasibility_20260814.json")
    for field in (
        "assessment_id",
        "scope",
        "authoritative_design_references",
        "data_quality",
        "formal_replay_decision",
        "nonqualifying_routes",
        "prospective_official_acquisition_paths",
        "required_packages",
        "least_expansive_external_prerequisite",
        "open_follow_on_gates",
    ):
        require(
            field in access_feasibility,
            f"data-access feasibility audit missing {field}",
            failures,
        )
    require(
        access_feasibility.get("portfolio_q") == 0,
        "data-access feasibility audit must retain portfolio_q=0",
        failures,
    )
    access_decision = access_feasibility.get("formal_replay_decision", {})
    require(
        access_decision.get("credential_free_route_qualifies") is False
        and access_decision.get("already_archived_route_qualifies") is False
        and access_decision.get("formal_replay_ready") is False,
        "data-access feasibility audit must not admit a credential-free or archived route",
        failures,
    )
    require_texts(
        access_feasibility.get("authoritative_design_references", []),
        ("DPSFS-DAC-v12", "DPSFS-U0-v2"),
        "data-access feasibility design references",
        failures,
    )
    require_texts(
        access_feasibility,
        (
            "UR01",
            "UR02",
            "UR03",
            "historic availability",
            "q=0",
            "not assert that no provider anywhere can supply",
            "CFFEX_HISTORICAL_DATA_SERVICE",
            "not a present authorization",
        ),
        "data-access feasibility audit",
        failures,
    )

    request_pack = load_json("missing_data_request_pack.json")
    for field in (
        "request_pack_id",
        "status",
        "external_contact_initiated",
        "credentials_requested",
        "portfolio_q",
        "requests",
        "csv_projection",
        "no_action_boundary",
    ):
        require(field in request_pack, f"missing-data request pack missing {field}", failures)
    require(
        request_pack.get("status") == "draft_request_specification_not_sent"
        and request_pack.get("external_contact_initiated") is False
        and request_pack.get("credentials_requested") is False
        and request_pack.get("portfolio_q") == 0,
        "missing-data request pack must remain not sent, credential-free and q=0",
        failures,
    )
    request_by_id = {
        request.get("request_id"): request
        for request in request_pack.get("requests", [])
        if isinstance(request, dict)
    }
    expected_request_ids = {
        "RQP-UR01",
        "RQP-UR02",
        "RQP-UR03",
        "RQP-U0",
        "RQP-OPEN-CLASS-MODULES",
    }
    require(
        len(request_by_id) == len(request_pack.get("requests", []))
        and set(request_by_id) == expected_request_ids,
        "missing-data request pack must contain exactly the governed five request rows",
        failures,
    )
    open_class_request = request_by_id.get("RQP-OPEN-CLASS-MODULES", {})
    open_class_ids = {
        item
        for item in open_class_request.get("u0_class_mapping", [])
        if isinstance(item, str)
    }
    if not open_class_ids:
        open_class_ids = set(
            open_class_request.get("u0_class_mapping", "").split(";")
        ) - {""}
    expected_open_class_ids = {
        "DIRECT_A_SHARE_EQUITIES",
        "PUBLIC_REITS",
        "EXCHANGE_LISTED_BONDS_AND_CONVERTIBLES",
        "FINANCIAL_FUTURES",
        "LISTED_OPTIONS",
        "LEVERAGED_AND_INVERSE_LISTED_PRODUCTS",
    }
    require(
        open_class_request.get("requirement_id") == "U0"
        and open_class_request.get("package_id")
        == "OPEN_CLASS_MODULE_DEFINITION_AND_CAPABILITY_RESPONSE"
        and open_class_ids == expected_open_class_ids
        and open_class_request.get("current_status")
        == "draft_module_definition_request_not_sent_no_DAC_package",
        "open-class module request must cover exactly the six unpacketized U0 classes without creating a DAC package",
        failures,
    )
    require_texts(
        open_class_request,
        (
            "它不是当前权利证明",
            "未来版本控制的 DAC 修订",
            "均不能使原始行、类别或产品合格",
            "保持 q=0",
        ),
        "open-class module request boundary",
        failures,
    )
    csv_projection = request_pack.get("csv_projection", {})
    csv_path = CASE_DIR / "missing_data_request_pack.csv"
    with csv_path.open(encoding="utf-8", newline="") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        csv_rows = list(csv_reader)
        csv_columns = csv_reader.fieldnames or []
    require(
        csv_columns == csv_projection.get("columns", [])
        and len(csv_rows) == csv_projection.get("row_count")
        and csv_rows == csv_projection.get("rows", []),
        "missing-data CSV projection must match the JSON projection exactly",
        failures,
    )

    package_by_id = {
        package.get("package_id"): package for package in contract.get("packages", [])
    }
    for package_id in (
        "ETF_PIT_EVENT_LEDGER",
        "FUTURES_ACTUAL_CONTRACT_LEDGER",
        "EXECUTION_AND_COST_LEDGER",
    ):
        require(
            package_id in package_by_id,
            f"data contract missing required package {package_id}",
            failures,
        )
    require(
        contains_text(package_by_id.get("ETF_PIT_EVENT_LEDGER", {}), "IOPV"),
        "ETF package must include IOPV or explicit unavailable-state control",
        failures,
    )
    require(
        contains_text(package_by_id.get("EXECUTION_AND_COST_LEDGER", {}), "available_to_sell_from"),
        "execution package must include dated T+1 availability control",
        failures,
    )
    require_texts(
        package_by_id.get("FUTURES_ACTUAL_CONTRACT_LEDGER", {}),
        (
            "contract_multiplier_tick_quote_unit_price_currency_trading_session_and_final_settlement_method",
            "initial_margin_maintenance_margin_variation_margin_transfer_timestamp_final_settlement_or_delivery_cashflow",
        ),
        "futures package",
        failures,
    )
    require_texts(
        package_by_id.get("EXECUTION_AND_COST_LEDGER", {}),
        (
            "quote_timestamp",
            "cash_yield_debit_financing_collateral_yield_margin_and_settlement_transfer_timing",
            "cash_collateral_term_id_term_set_role_applicability_audit_scope_type_precedence_route_account_day_count_compounding_accrual_period_and_transfer_cutoff",
            "execution_state_settlement_state",
            "immutable_execution_fill_ledger",
            "minimum_observation_rule",
            "material_difference_definition",
        ),
        "execution package",
        failures,
    )
    prospective = package_by_id.get("EXECUTION_AND_COST_LEDGER", {}).get(
        "collection_and_quality", {}
    ).get("prospective_reconciliation", {})
    require(
        prospective.get("minimum_calendar_duration_days") == 60,
        "prospective reconciliation must require 60 elapsed calendar days",
        failures,
    )
    require(
        prospective.get("minimum_distinct_observations") == 10,
        "prospective reconciliation must require 10 distinct observations",
        failures,
    )
    require_texts(
        prospective.get("minimum_observation_rule", ""),
        ("both thresholds", "60 calendar days", "AND", "10 distinct"),
        "prospective reconciliation minimum-observation rule",
        failures,
    )
    require_texts(
        prospective.get("unit_consistency_rule", ""),
        ("same stated unit and currency", "cross-unit comparison is prohibited"),
        "prospective reconciliation unit-consistency rule",
        failures,
    )
    materiality_by_field = prospective.get("materiality_by_field", {})
    require(
        {
            "order_state_and_quantity",
            "execution_price",
            "fees_and_tax",
            "margin_collateral_and_funding",
            "quote_and_impact",
            "route_and_market_status",
        }
        <= set(materiality_by_field),
        "prospective reconciliation lacks a field-level materiality rule",
        failures,
    )
    require_texts(
        prospective.get("material_difference_definition", ""),
        ("materiality_by_field", "No aggregate offset"),
        "prospective reconciliation material-difference definition",
        failures,
    )
    require(
        contains_text(contract.get("global_provenance_controls", {}), "normalization_code_commit"),
        "data contract must bind normalized data to transformation code",
        failures,
    )

    matrix = {
        item.get("id"): item for item in contract.get("requirement_closure_matrix", [])
    }
    expected_urs = {"UR01", "UR02", "UR03", "UR04", "UR05"}
    require(
        set(matrix) == expected_urs,
        "data contract closure matrix must cover exactly UR01-UR05",
        failures,
    )
    for requirement_id in expected_urs:
        entry = matrix.get(requirement_id, {})
        require(
            entry.get("status") == "open",
            f"{requirement_id} must remain open in data contract",
            failures,
        )
        for field in (
            "owner",
            "evidence_artifacts",
            "acceptance_test",
            "pass_threshold",
            "verifier",
            "exit_condition",
        ):
            require(
                bool(entry.get(field)),
                f"{requirement_id} closure matrix missing {field}",
                failures,
            )
        require(
            requirement_id in unresolved_by_id,
            f"{requirement_id} is missing from unresolved requirements",
            failures,
        )

    require_texts(
        matrix.get("UR04", {}),
        (
            "primary-holdout predicate",
            "non-overlapping-window",
            "state-transition matrix",
            "risk-and-feasibility control pack",
        ),
        "UR04 closure matrix",
        failures,
    )
    require_texts(
        matrix.get("UR05", {}),
        (
            "risk-and-feasibility control pass/fail audit",
            "every frozen risk-and-feasibility control passes",
            "usable-strategy conjunctive status",
        ),
        "UR05 closure matrix",
        failures,
    )

    ur03_fields = unresolved_by_id.get("UR03", {}).get("fields", [])
    ur04_fields = unresolved_by_id.get("UR04", {}).get("fields", [])
    ur05_fields = unresolved_by_id.get("UR05", {}).get("fields", [])
    for required_field in (
        "rolling-window and annualization definition",
        "endpoint status and missing-window policy",
        "unitized internal/external cash-flow accounting",
        "execution/no-fill state machine",
        "formal replay protocol ID/version/SHA-256",
        "nonpositive-NAV and no-rebase treatment",
        "minimum candidate-endpoint count and zero-count policy",
        "expected-versus-actual candidate-endpoint equality rule",
        "CROSSING policy and endpoint-partition reconciliation",
        "primary-holdout/development/crossing result populations",
        "nonempty expected-versus-actual primary-holdout endpoint rule",
        "executable primary-holdout window predicate and post-freeze invalidation rule",
        "overlap-dependence boundary plus deterministic non-overlapping and regime/stress summaries",
        "frozen allowed order-state-transition matrix and ledger reconciliation",
        "hash-bound risk-and-feasibility control pack with numerical limits, measurement, escalation and pass/fail rules",
        "conjunctive usable-strategy status audit",
        "U0-to-T2 derivation audit and class-module coverage label",
    ):
        require(required_field in ur04_fields, f"UR04 missing {required_field}", failures)
    for required_field in (
        "U0 population and class-neutral universe audit",
        "both calendar-duration and distinct-observation thresholds plus field-level material-difference and escalation policy",
        "per-control risk/feasibility, stress, liquidity/capacity and route/suitability pass/fail review",
    ):
        require(required_field in ur05_fields, f"UR05 missing {required_field}", failures)
    for required_field in (
        "order side/timestamps/route/quote snapshot and settlement causality",
        "cash/collateral term-set identity, route-account scope and accrual terms",
        "monotonic order-state-transition ledger",
    ):
        require(required_field in ur03_fields, f"UR03 missing {required_field}", failures)

    u0 = load_json("data/u0_domestic_universe_registry_20260814.json")
    require(
        u0.get("status") == "draft_population_governance_only",
        "U0 registry must remain population governance only",
        failures,
    )
    require(u0.get("portfolio_q") == 0, "U0 registry must retain portfolio_q=0", failures)
    require(
        u0.get("registry_id") == "DPSFS-U0-v2"
        and u0.get("registry_version") == 2
        and u0.get("schema_version") == "domestic_universe_registry.v2",
        "U0 registry must be the versioned DPSFS-U0-v2 draft",
        failures,
    )
    require(
        u0.get("freeze_control", {}).get("state") == "not_frozen",
        "U0 registry freeze state must remain not_frozen",
        failures,
    )
    class_by_id = {entry.get("class_id"): entry for entry in u0.get("classes", [])}
    required_classes = {
        "DIRECT_A_SHARE_EQUITIES",
        "PUBLIC_REITS",
        "LISTED_EQUITY_ETFS",
        "BOND_AND_MONEY_MARKET_ETFS",
        "GOLD_AND_OTHER_COMMODITY_ETFS",
        "EXCHANGE_LISTED_BONDS_AND_CONVERTIBLES",
        "COMMODITY_FUTURES",
        "FINANCIAL_FUTURES",
        "LISTED_OPTIONS",
        "LEVERAGED_AND_INVERSE_LISTED_PRODUCTS",
    }
    require(
        required_classes <= set(class_by_id),
        "U0 registry is missing an in-scope domestic asset class",
        failures,
    )
    for class_id, entry in class_by_id.items():
        require(entry.get("q") == 0, f"U0 class {class_id} must remain q=0", failures)
        require(
            entry.get("status") in {"unresearched", "evidence_pending"},
            f"U0 class {class_id} cannot be data-qualified or excluded",
            failures,
        )
        require(
            bool(entry.get("candidate_primary_population_source")),
            f"U0 class {class_id} missing primary population path",
            failures,
        )

    dictionary = load_json("data/replay_data_dictionary_template_20260814.json")
    require(
        dictionary.get("dictionary_id") == "DPSFS-DD-v8"
        and dictionary.get("schema_version") == "replay_data_dictionary_template.v8"
        and dictionary.get("version") == 8,
        "replay data dictionary must be the versioned DPSFS-DD-v8 template",
        failures,
    )
    require(
        dictionary.get("status") == "template_not_frozen_no_data",
        "replay data dictionary must remain a no-data template",
        failures,
    )
    require(
        dictionary.get("portfolio_q") == 0,
        "replay data dictionary must retain portfolio_q=0",
        failures,
    )
    table_by_id = {table.get("table_id"): table for table in dictionary.get("tables", [])}
    required_table_ids = {
        "replay_run_freeze_record",
        "etf_instrument_master",
        "etf_market_session",
        "etf_nav_event",
        "etf_corporate_action",
        "etf_tradability_session",
        "futures_contract_master",
        "futures_market_session",
        "futures_effective_terms",
        "futures_tradability_session",
        "execution_broker_terms",
        "tax_jurisdiction",
        "broker_fee_term",
        "tax_levy_term",
        "execution_market_snapshot",
        "cash_collateral_terms",
        "cash_collateral_term_set_membership",
        "execution_order_ledger",
        "execution_order_state_transition",
        "execution_order_settlement_transition",
        "execution_fill_ledger",
        "execution_fill_ledger_event_link",
        "execution_fee_tax_component",
        "execution_feasibility_reservation",
        "frozen_fx_quote_conversion",
        "master_calendar_daily_valuation_coverage",
        "frozen_unitization_method_definition",
        "daily_portfolio_ledger",
        "portfolio_unitization_ledger",
        "portfolio_position_lot_mark_ledger",
        "portfolio_cashflow_pnl_ledger",
        "replay_reconciliation_residual",
        "execution_cash_margin_settlement_ledger_event",
        "cash_margin_collateral_transfer_pair",
        "cash_collateral_role_applicability_audit",
        "primary_holdout_start_state_manifest",
        "primary_holdout_start_state_component",
        "frozen_roll_delivery_expiry_parameter_state",
        "replay_candidate_endpoint_roster",
        "replay_endpoint_population_audit",
        "replay_endpoint_result",
        "endpoint_unit_nav_chain_member",
        "prospective_state_configuration_coverage_audit",
    }
    require(
        required_table_ids <= set(table_by_id),
        "replay data dictionary is missing a required normalized table",
        failures,
    )
    require_texts(
        dictionary,
        (
            "IOPV",
            "contract_multiplier",
            "INITIAL_MARGIN",
            "quote_timestamp",
            "quote_age_seconds",
            "CASH_YIELD",
            "available_to_sell_from",
            "calendar_anchor_at",
            "selected_start_valuation_at",
            "endpoint_end_valuation_at",
            "cumulative_filled_quantity",
            "reservation_pool_id",
            "term_output_currency",
        ),
        "replay data dictionary",
        failures,
    )
    cash_columns = column_names(table_by_id.get("cash_collateral_terms", {}))
    require(
        {
            "broker_route_id",
            "clearing_or_account_entity_id",
            "applicable_instrument_category_or_contract_id",
            "day_count_basis",
            "compounding_convention",
            "accrual_start_at",
            "accrual_end_at",
            "transfer_cutoff_at",
            "cash_collateral_term_id",
            "term_type",
            "rate_or_timing_value",
            "rate_or_timing_value_unit",
            "source_revision",
            "source_reference",
        }
        <= cash_columns,
        "cash/collateral table lacks route, scope or accrual controls",
        failures,
    )
    require_texts(
        table_by_id.get("cash_collateral_terms", {}),
        (
            "COLLATERAL_TRANSFER",
            "positive_decimal_currency_amount_when_term_type_is_COLLATERAL_TRANSFER",
            "dated cash/collateral term source evidence",
        ),
        "cash/collateral term table",
        failures,
    )
    order_columns = column_names(table_by_id.get("execution_order_ledger", {}))
    require(
        {
            "broker_route_id",
            "execution_side",
            "filled_at",
            "expires_at",
            "settlement_at",
            "settlement_state",
            "quote_timestamp",
            "quote_source_revision",
            "broker_terms_source_revision",
            "cash_collateral_terms_source_revision",
            "cash_collateral_term_set_id",
        }
        <= order_columns,
        "order ledger lacks quote-to-fill, route or settlement causality fields",
        failures,
    )
    require_texts(
        dictionary.get("cross_table_validation_rules", []),
        (
            "execution_broker_terms",
            "execution_market_snapshot composite key",
            "ORDER_TIME_QUOTE",
            "Cash/collateral role-to-term mapping is mandatory",
            "execution_order_state_transition",
            "execution_order_settlement_transition",
            "event_type-to-application_role mapping",
            "prospective_state_configuration_coverage_audit",
        ),
        "replay data dictionary cross-table validation rules",
        failures,
    )
    transition_columns = column_names(table_by_id.get("execution_order_state_transition", {}))
    require(
        {
            "transition_sequence",
            "from_execution_state",
            "to_execution_state",
            "transition_at",
            "transition_reason",
            "replay_run_freeze_record_sha256",
        }
        <= transition_columns,
        "execution-state transition table lacks required monotonic audit fields",
        failures,
    )
    settlement_transition_columns = column_names(
        table_by_id.get("execution_order_settlement_transition", {})
    )
    require(
        {
            "settlement_transition_sequence",
            "from_settlement_state",
            "to_settlement_state",
            "transition_at",
            "transition_reason",
            "replay_run_freeze_record_sha256",
        }
        <= settlement_transition_columns,
        "settlement-state transition table lacks separate monotonic audit fields",
        failures,
    )

    require_table_columns(
        table_by_id,
        "replay_run_freeze_record",
        {
            "replay_run_id",
            "replay_run_freeze_record_sha256",
            "canonical_freeze_record_sha256",
            "replay_run_freeze_record_schema_version",
            "data_contract_freeze_record_sha256",
            "data_contract_sha256",
            "freeze_status",
            "contract_id",
            "formal_replay_protocol_id",
            "data_dictionary_sha256",
            "input_manifest_sha256",
            "source_revision_cutoff",
            "replay_code_commit",
            "runtime_environment_lock_or_hash",
            "exact_run_command",
            "first_permitted_outcome_view_at",
            "expected_candidate_endpoint_count",
            "expected_primary_holdout_candidate_endpoint_count",
            "master_calendar_id",
            "master_calendar_sha256",
            "evaluation_interval_start",
            "evaluation_interval_end",
            "raw_data_coverage_start",
            "raw_data_coverage_end",
            "candidate_generation_rule_id",
            "candidate_generation_rule_sha256",
            "candidate_endpoint_roster_id",
            "candidate_endpoint_roster_sha256",
            "expected_development_count",
            "expected_crossing_count",
            "endpoint_status_rule_id",
            "endpoint_status_rule_sha256",
            "reconciliation_expected_matrix_id",
            "reconciliation_expected_matrix_sha256",
            "fill_event_link_allocation_rule_id",
            "fill_event_link_allocation_rule_sha256",
            "fx_conversion_policy_id",
            "fx_conversion_policy_sha256",
            "master_calendar_daily_coverage_rule_id",
            "master_calendar_daily_coverage_rule_sha256",
            "unitization_method_id",
            "unitization_method_version",
            "unitization_method_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "execution_order_ledger",
        {
            "replay_run_freeze_record_sha256",
            "submission_path",
            "execution_model_id",
            "execution_price_basis",
            "execution_state",
            "settlement_state",
            "fill_count",
            "fee_tax_component_count",
            "settlement_event_count",
            "feasibility_reservation_set_sha256",
            "fill_capacity_set_sha256",
            "end_of_run_order_disposition",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "execution_fill_ledger",
        {
            "replay_run_freeze_record_sha256",
            "order_id",
            "fill_sequence",
            "fill_at",
            "fill_quantity",
            "cumulative_filled_quantity",
            "remaining_submitted_quantity",
            "execution_transition_sequence",
            "execution_transition_from_state",
            "execution_transition_to_state",
            "liquidity_capacity_basis",
            "liquidity_capacity_snapshot_id",
            "capacity_instrument_or_contract_id",
            "capacity_side",
            "capacity_snapshot_as_of",
            "capacity_snapshot_source_revision",
            "capacity_partition_id",
            "capacity_consumption_sequence",
            "opposite_side_available_quantity",
            "prior_consumed_quantity",
            "incremental_consumed_quantity",
            "remaining_opposite_side_capacity",
            "impact_model_or_proxy_id",
            "fill_price",
            "fill_price_currency",
            "gross_notional",
            "gross_notional_currency",
            "contract_multiplier",
            "contract_master_effective_from",
            "contract_master_source_revision",
            "notional_sign_convention",
            "fill_hash_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "execution_fee_tax_component",
        {
            "replay_run_freeze_record_sha256",
            "order_id",
            "fill_id",
            "charge_basis",
            "order_level_exception_reference",
            "order_level_source_reference",
            "order_level_charge_at",
            "order_level_allocation_rule_id",
            "order_level_allocation_rule_sha256",
            "component_type",
            "amount",
            "currency",
            "term_calculated_amount",
            "term_output_currency",
            "currency_conversion_required",
            "fx_conversion_rate",
            "fx_source_reference",
            "fx_observation_at",
            "fx_quote_sha256",
            "broker_fee_term_id",
            "tax_levy_term_id",
            "tax_jurisdiction_id",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "execution_feasibility_reservation",
        {
            "replay_run_freeze_record_sha256",
            "order_id",
            "reservation_type",
            "reservation_context_type",
            "fill_id",
            "context_at",
            "lot_id",
            "available_to_sell_from",
            "reservation_pool_id",
            "reservation_pool_snapshot_id",
            "reservation_pool_snapshot_at",
            "reservation_pool_snapshot_unit_or_currency",
            "reservation_pool_snapshot_sequence",
            "reservation_status",
            "active_immediately_before_context",
            "eligible_pool_balance_before",
            "preexisting_active_reservation_quantity_or_amount",
            "new_reservation_quantity_or_amount",
            "eligible_pool_balance_after",
            "feasibility_status",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "frozen_fx_quote_conversion",
        {
            "replay_run_freeze_record_sha256",
            "fx_quote_id",
            "fx_conversion_policy_id",
            "fx_conversion_policy_sha256",
            "from_currency",
            "to_currency",
            "fx_conversion_rate",
            "fx_observation_at",
            "fx_source_reference",
            "fx_source_revision",
            "conversion_basis",
            "rounding_mode",
            "rounding_decimal_places",
            "source_quote_raw_sha256",
            "fx_quote_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "master_calendar_daily_valuation_coverage",
        {
            "replay_run_freeze_record_sha256",
            "coverage_scope_type",
            "coverage_scope_id",
            "candidate_endpoint_id",
            "master_calendar_id",
            "master_calendar_sha256",
            "master_calendar_daily_coverage_rule_id",
            "master_calendar_daily_coverage_rule_sha256",
            "master_calendar_session_at",
            "coverage_interval_start",
            "coverage_interval_end",
            "daily_ledger_id",
            "coverage_status",
            "coverage_row_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "frozen_unitization_method_definition",
        {
            "replay_run_freeze_record_sha256",
            "unitization_method_id",
            "unitization_method_version",
            "unitization_method_sha256",
            "external_flow_timing",
            "opening_state_rule_id",
            "opening_state_rule_sha256",
            "rounding_mode",
            "rounding_decimal_places",
            "formula_definition",
            "method_row_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "daily_portfolio_ledger",
        {
            "replay_run_freeze_record_sha256",
            "valuation_at",
            "ledger_currency",
            "cash_balance",
            "debit_balance",
            "collateral_balance",
            "margin_balance",
            "total_nav",
            "fx_conversion_policy_id",
            "fx_conversion_policy_sha256",
            "fx_quote_set_sha256",
            "unitization_ledger_id",
            "positions_lots_marks_sha256",
            "cashflow_pnl_set_sha256",
            "event_balance_routing_set_sha256",
            "nav_bridge_input_set_sha256",
            "expected_reconciliation_row_count",
            "actual_reconciliation_residual_row_count",
            "expected_reconciliation_matrix_set_sha256",
            "reconciliation_residual_set_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "portfolio_unitization_ledger",
        {
            "replay_run_freeze_record_sha256",
            "daily_ledger_id",
            "unitization_method_id",
            "unitization_method_version",
            "unitization_method_sha256",
            "prior_unitization_ledger_id",
            "prior_unit_nav",
            "opening_units",
            "units_issued",
            "units_redeemed",
            "closing_units",
            "unitization_event_type",
            "nav_before_external_cashflow",
            "external_cashflow_amount",
            "external_flow_pricing_unit_nav",
            "nav_after_external_cashflow",
            "unit_nav",
            "unitization_calculation_input_set_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "portfolio_position_lot_mark_ledger",
        {
            "replay_run_freeze_record_sha256",
            "daily_ledger_id",
            "position_id",
            "lot_id",
            "origin_fill_id",
            "available_to_sell_from",
            "economic_closing_quantity",
            "eligible_to_sell_quantity",
            "active_sell_reservation_quantity",
            "available_to_sell_quantity",
            "instrument_category",
            "position_side",
            "mark_price",
            "marked_value",
            "futures_contract_multiplier",
            "futures_contract_master_effective_from",
            "futures_contract_master_source_revision",
            "valuation_formula_type",
            "futures_daily_margin_notional_reference",
            "mark_value_currency",
            "ledger_currency",
            "marked_value_ledger_currency",
            "fx_quote_id",
            "fx_quote_sha256",
            "fx_conversion_rate",
            "fx_rounding_mode",
            "fx_rounding_decimal_places",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "portfolio_cashflow_pnl_ledger",
        {
            "replay_run_freeze_record_sha256",
            "daily_ledger_id",
            "component_type",
            "component_origin_type",
            "amount",
            "currency",
            "ledger_currency",
            "ledger_currency_amount",
            "fx_quote_id",
            "fx_quote_sha256",
            "fx_conversion_rate",
            "fx_rounding_mode",
            "fx_rounding_decimal_places",
            "ledger_event_id",
            "fill_id",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "replay_reconciliation_residual",
        {
            "replay_run_freeze_record_sha256",
            "daily_ledger_id",
            "reconciliation_matrix_row_id",
            "reconciliation_scope",
            "reconciliation_component",
            "reconciliation_formula_id",
            "reconciliation_formula_sha256",
            "expected_source_set_sha256",
            "expected_amount",
            "actual_amount",
            "residual_amount",
            "tolerance_amount",
            "reconciliation_status",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "execution_cash_margin_settlement_ledger_event",
        {
            "replay_run_freeze_record_sha256",
            "daily_ledger_id",
            "event_type",
            "balance_effect_bucket",
            "balance_effect_sign",
            "application_role",
            "pricing_reference_type",
            "fee_tax_component_id",
            "fee_tax_component_type",
            "broker_fee_term_id",
            "tax_levy_term_id",
            "tax_jurisdiction_id",
            "amount",
            "currency",
            "ledger_currency",
            "ledger_currency_amount",
            "posted_balance_effect_ledger_currency_amount",
            "instrument_or_contract_id",
            "instrument_category",
            "futures_non_notional_adjustment_amount",
            "futures_non_notional_adjustment_reference",
            "fx_quote_id",
            "fx_quote_sha256",
            "fx_conversion_rate",
            "event_calculation_formula_id",
            "event_calculation_formula_sha256",
            "event_calculation_input_set_sha256",
            "transfer_pair_id",
            "transfer_leg_type",
            "settlement_obligation_status",
            "settlement_outstanding_direction",
            "settlement_gross_obligation_ledger_currency_amount",
            "settlement_posted_or_paid_ledger_currency_amount",
            "settlement_outstanding_ledger_currency_amount",
            "unsettled_obligation_ledger_currency_amount",
            "unsettled_receivable_ledger_currency_amount",
            "unsettled_net_nav_ledger_currency_amount",
            "cashflow_pnl_id",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "cash_margin_collateral_transfer_pair",
        {
            "replay_run_freeze_record_sha256",
            "transfer_pair_id",
            "daily_ledger_id",
            "transfer_kind",
            "cash_leg_ledger_event_id",
            "reserve_leg_ledger_event_id",
            "cash_leg_ledger_currency_amount",
            "reserve_leg_ledger_currency_amount",
            "net_nav_effect",
            "transfer_pair_status",
            "transfer_pair_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "replay_candidate_endpoint_roster",
        {
            "replay_run_freeze_record_sha256",
            "candidate_endpoint_roster_id",
            "candidate_endpoint_roster_sha256",
            "candidate_input_manifest_sha256",
            "calendar_anchor_at",
            "selected_start_valuation_at",
            "endpoint_end_valuation_at",
            "elapsed_calendar_days",
            "start_daily_ledger_id",
            "end_daily_ledger_id",
            "start_unitization_ledger_id",
            "end_unitization_ledger_id",
            "master_calendar_daily_coverage_rule_id",
            "master_calendar_daily_coverage_rule_sha256",
            "endpoint_window_coverage_row_count",
            "endpoint_window_covered_count",
            "endpoint_window_coverage_set_sha256",
            "endpoint_window_coverage_status",
            "expected_partition",
            "assigned_endpoint_id",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "replay_endpoint_population_audit",
        {
            "replay_run_freeze_record_sha256",
            "candidate_endpoint_roster_id",
            "candidate_endpoint_roster_sha256",
            "evaluation_interval_start",
            "evaluation_interval_end",
            "raw_data_coverage_start",
            "raw_data_coverage_end",
            "master_calendar_id",
            "master_calendar_sha256",
            "master_calendar_daily_coverage_rule_id",
            "master_calendar_daily_coverage_rule_sha256",
            "evaluation_warmup_coverage_row_count",
            "evaluation_warmup_covered_count",
            "evaluation_warmup_coverage_set_sha256",
            "evaluation_warmup_coverage_status",
            "expected_candidate_endpoint_count",
            "actual_candidate_endpoint_count",
            "expected_development_count",
            "actual_development_count",
            "expected_primary_holdout_count",
            "actual_primary_holdout_count",
            "expected_crossing_count",
            "actual_crossing_count",
            "pass_count",
            "fail_count",
            "incomplete_count",
            "invalid_count",
            "status_count_total",
            "zero_candidate_status",
            "count_residual",
            "population_reconciliation_status",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "replay_endpoint_result",
        {
            "replay_run_freeze_record_sha256",
            "candidate_endpoint_id",
            "candidate_endpoint_roster_id",
            "candidate_endpoint_roster_sha256",
            "master_calendar_id",
            "master_calendar_sha256",
            "master_calendar_daily_coverage_rule_id",
            "master_calendar_daily_coverage_rule_sha256",
            "calendar_anchor_at",
            "selected_start_valuation_at",
            "endpoint_end_valuation_at",
            "elapsed_calendar_days",
            "start_daily_ledger_id",
            "end_daily_ledger_id",
            "start_unitization_ledger_id",
            "end_unitization_ledger_id",
            "endpoint_window_coverage_row_count",
            "endpoint_window_covered_count",
            "endpoint_window_coverage_set_sha256",
            "endpoint_window_coverage_status",
            "start_total_nav",
            "end_total_nav",
            "start_unit_nav",
            "end_unit_nav",
            "twrr_calculation_method",
            "twrr_unit_nav_chain_sha256",
            "twrr_unit_nav_chain_member_count",
            "endpoint_status_rule_id",
            "endpoint_status_rule_sha256",
            "annualized_net_twrr",
            "endpoint_partition",
            "endpoint_status",
            "primary_holdout_start_state_manifest_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "endpoint_unit_nav_chain_member",
        {
            "replay_run_freeze_record_sha256",
            "endpoint_id",
            "chain_sequence",
            "chain_member_role",
            "twrr_unit_nav_chain_sha256",
            "unitization_ledger_id",
            "valuation_at",
            "unit_nav",
            "prior_unitization_ledger_id",
            "prior_unit_nav",
            "link_return_factor",
            "chain_member_hash_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "primary_holdout_start_state_manifest",
        {
            "replay_run_freeze_record_sha256",
            "primary_holdout_window_id",
            "state_reset_at",
            "start_state_component_row_count",
            "start_state_component_set_sha256",
            "integrity_status",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "primary_holdout_start_state_component",
        {
            "replay_run_freeze_record_sha256",
            "primary_holdout_window_id",
            "component_type",
            "component_row_reference",
            "referenced_table_id",
            "component_source_available_at",
            "post_lockbox_provenance_status",
            "component_integrity_status",
            "referenced_row_sha256",
        },
        failures,
    )
    require_table_columns(
        table_by_id,
        "prospective_state_configuration_coverage_audit",
        {
            "replay_run_freeze_record_sha256",
            "configuration_tuple_sha256",
            "parent_class_id",
            "broker_route_terms_id",
            "cash_collateral_term_set_id",
            "application_role",
            "material_transaction_type",
            "event_type",
            "execution_state",
            "settlement_state",
            "end_of_run_order_disposition",
            "coverage_disposition",
            "review_status",
        },
        failures,
    )
    machine_contract = dictionary.get("machine_validation_contract", {})
    require(
        set(machine_contract.get("run_dependent_table_ids", []))
        == {
            "execution_order_ledger",
            "execution_order_state_transition",
            "execution_order_settlement_transition",
            "execution_fill_ledger",
            "execution_fill_ledger_event_link",
            "execution_fee_tax_component",
            "execution_feasibility_reservation",
            "frozen_fx_quote_conversion",
            "master_calendar_daily_valuation_coverage",
            "frozen_unitization_method_definition",
            "daily_portfolio_ledger",
            "portfolio_unitization_ledger",
            "portfolio_position_lot_mark_ledger",
            "portfolio_cashflow_pnl_ledger",
            "replay_reconciliation_residual",
            "execution_cash_margin_settlement_ledger_event",
            "cash_margin_collateral_transfer_pair",
            "cash_collateral_role_applicability_audit",
            "primary_holdout_start_state_manifest",
            "primary_holdout_start_state_component",
            "frozen_roll_delivery_expiry_parameter_state",
            "replay_candidate_endpoint_roster",
            "replay_endpoint_population_audit",
            "replay_endpoint_result",
            "endpoint_unit_nav_chain_member",
            "prospective_state_configuration_coverage_audit",
        },
        "dictionary run-dependent row-binding inventory is incomplete or contains an ungoverned table",
        failures,
    )
    require(
        machine_contract.get("run_binding_foreign_key", {}).get("parent_table")
        == "replay_run_freeze_record",
        "dictionary must bind run-dependent rows to replay_run_freeze_record",
        failures,
    )
    require(
        machine_contract.get("run_binding_foreign_key", {}).get("child_columns")
        == ["replay_run_id", "replay_run_freeze_record_sha256"],
        "dictionary must expose the exact composite run-binding child key",
        failures,
    )
    run_dependent_tables = machine_contract.get("run_dependent_table_ids", [])
    require(
        len(run_dependent_tables) == len(set(run_dependent_tables)),
        "dictionary run-dependent row-binding inventory contains a duplicate table",
        failures,
    )
    for table_id in run_dependent_tables:
        require_table_columns(
            table_by_id,
            table_id,
            {"replay_run_id", "replay_run_freeze_record_sha256"},
            failures,
        )
    hash_contract = machine_contract.get("hash_serialization_contract", {})
    require(
        bool(hash_contract.get("canonical_encoding"))
        and "excluding that hash field itself"
        in hash_contract.get("universal_self_hash_exclusion_rule", "")
        and "except replay_run_freeze_record_sha256"
        in hash_contract.get("named_row_hash_field_contracts", {}).get(
            "replay_run_freeze_record_sha256", ""
        ),
        "dictionary must define a canonical non-self-referential hash serialization contract",
        failures,
    )
    endpoint_status_rule = machine_contract.get("endpoint_status_rule", {})
    require(
        endpoint_status_rule.get("threshold", {}).get("value") == 0.05
        and endpoint_status_rule.get("threshold", {}).get("pass_operator")
        == "greater_than_or_equal"
        and endpoint_status_rule.get("result_enforcement", {}).get("endpoint_status_operator")
        == "equals_first_matching_status_by_rank",
        "dictionary must bind the 5% endpoint threshold to a recomputed status rule",
        failures,
    )
    require(
        endpoint_status_rule.get("twrr_recomputation", {}).get("direct_unit_nav_ratio", {}).get(
            "formula"
        )
        == "((end_unit_nav/start_unit_nav)^(365.2425/elapsed_calendar_days)-1)",
        "dictionary must provide the exact direct unit-NAV annualization formula",
        failures,
    )
    endpoint_invalidity_predicate_ids = {
        predicate.get("predicate_id")
        for predicate in endpoint_status_rule.get("invalidity_predicates", [])
        if isinstance(predicate, dict)
    }
    require(
        {
            "no-failed-settlement-in-endpoint-state",
            "failed-settlement-contract-pass",
        }
        <= endpoint_invalidity_predicate_ids,
        "endpoint status must explicitly invalidate a FAILED settlement path",
        failures,
    )
    require(
        endpoint_status_rule.get("twrr_recomputation", {}).get("chain_linked_unit_nav", {}).get(
            "member_table"
        )
        == "endpoint_unit_nav_chain_member",
        "dictionary must bind chain-linked TWRR to normalized ordered unit-NAV members",
        failures,
    )
    require(
        machine_contract.get("liquidity_capacity_consumption_contract", {}).get(
            "failure_status"
        )
        == "INVALID"
        and machine_contract.get("reservation_pool_snapshot_contract", {}).get(
            "failure_status"
        )
        == "INVALID",
        "dictionary capacity and reservation contracts must invalidate an infeasible row",
        failures,
    )
    require(
        machine_contract.get("json_object_key_uniqueness_rule"),
        "dictionary must require duplicate JSON object-key rejection",
        failures,
    )
    crosswalk = machine_contract.get("frozen_run_crosswalk", {})
    required_crosswalk_parent_fields = {
        "replay_run_id",
        "replay_run_freeze_record_schema_version",
        "replay_run_freeze_record_sha256",
        "data_contract_freeze_record_sha256",
        "data_contract_sha256",
        "protocol_id",
        "protocol_version",
        "protocol_sha256",
        "freeze_timestamp",
        "supersedes_if_any",
        "data_dictionary_id",
        "data_dictionary_schema_version",
        "data_dictionary_sha256",
        "master_calendar_id",
        "master_calendar_sha256",
        "evaluation_interval_start",
        "evaluation_interval_end",
        "raw_data_coverage_start",
        "raw_data_coverage_end",
        "candidate_generation_rule_id",
        "candidate_generation_rule_sha256",
        "candidate_endpoint_roster_id",
        "candidate_endpoint_roster_sha256",
        "expected_development_count",
        "expected_crossing_count",
        "endpoint_status_rule_id",
        "endpoint_status_rule_sha256",
        "reconciliation_expected_matrix_id",
        "reconciliation_expected_matrix_sha256",
        "fill_event_link_allocation_rule_id",
        "fill_event_link_allocation_rule_sha256",
        "fx_conversion_policy_id",
        "fx_conversion_policy_sha256",
        "master_calendar_daily_coverage_rule_id",
        "master_calendar_daily_coverage_rule_sha256",
        "unitization_method_id",
        "unitization_method_version",
        "unitization_method_sha256",
    }
    require(
        crosswalk.get("canonical_parent_schema_version")
        == "replay_run_freeze_record.v2",
        "dictionary frozen-run crosswalk must name the canonical parent schema",
        failures,
    )
    require(
        set(crosswalk.get("required_parent_fields", []))
        == required_crosswalk_parent_fields,
        "dictionary frozen-run crosswalk parent-field set is incomplete or contains an ungoverned field",
        failures,
    )
    byte_equality_map = crosswalk.get("byte_equality_map", [])
    mapped_parent_fields = {
        entry.get("canonical_parent_ref", {}).get("column")
        for entry in byte_equality_map
        if isinstance(entry, dict)
    }
    require(
        mapped_parent_fields == required_crosswalk_parent_fields,
        "dictionary frozen-run crosswalk does not map exactly its canonical parent-field set",
        failures,
    )
    for entry in byte_equality_map:
        parent_ref = entry.get("canonical_parent_ref", {}) if isinstance(entry, dict) else {}
        target_ref = entry.get("target_ref", {}) if isinstance(entry, dict) else {}
        require(
            isinstance(entry, dict)
            and parent_ref.get("table_id") == "replay_run_freeze_record"
            and parent_ref.get("column") in required_crosswalk_parent_fields
            and entry.get("operator") == "equals_byte_for_byte"
            and entry.get("cardinality") == "exactly_one"
            and target_ref.get("kind") in {"table_column", "table_row", "json_pointer", "artifact_digest"}
            and target_ref.get("cardinality") == "exactly_one",
            "dictionary frozen-run crosswalk contains a non-machine-resolvable equality map",
            failures,
        )
    require(
        crosswalk.get("map_activation", {}).get("value") == "SIGNED"
        and crosswalk.get("map_resolution_validation", {}).get("failure_status")
        == "INVALID",
        "dictionary frozen-run crosswalk must activate only when signed and invalidate mismatches",
        failures,
    )
    require(
        machine_contract.get("event_type_application_role_mapping", {})
        == {
            "CASH_ACCRUAL": "CASH_BALANCE",
            "DEBIT_ACCRUAL": "DEBIT_BALANCE",
            "COLLATERAL_ACCRUAL": "COLLATERAL",
            "COLLATERAL_TRANSFER": "COLLATERAL",
            "MARGIN_TRANSFER_CASH_LEG": "CASH_BALANCE",
            "TRADE_SETTLEMENT": "TRADE_SETTLEMENT",
            "INITIAL_MARGIN": "INITIAL_MARGIN",
            "MAINTENANCE_MARGIN": "MAINTENANCE_MARGIN",
            "VARIATION_MARGIN": "VARIATION_MARGIN",
            "FINAL_SETTLEMENT": "FINAL_SETTLEMENT",
            "FEES_TAX": "NOT_APPLICABLE_FEE_TAX",
        },
        "dictionary must expose the exact event-type-to-application-role mapping",
        failures,
    )
    position_mark_contract = machine_contract.get("position_mark_valuation_contract", {})
    futures_mark_formulas = [
        formula
        for formula in position_mark_contract.get("formulas", [])
        if isinstance(formula, dict)
        and formula.get("valuation_formula_type") == "FUTURES_DAILY_MARGINED"
    ]
    require(
        len(futures_mark_formulas) == 1
        and futures_mark_formulas[0].get("operator") == "all_true"
        and {
            "marked_value=0",
            "marked_value_ledger_currency=0",
            "futures_daily_margin_notional_reference_is_exposure_only_and_is_excluded_from_NAV_and_TWRR",
            "variation_margin_or_final_settlement_is_the_only_futures_mark_to_market_P_and_L_path",
        }
        <= set(futures_mark_formulas[0].get("assertions", []))
        and position_mark_contract.get("failure_status") == "INVALID",
        "futures must be daily-margined zero-NAV exposure records with P&L only through variation/final settlement",
        failures,
    )
    routing_contract = machine_contract.get("event_balance_routing_and_nav_bridge_contract", {})
    expected_event_buckets = {
        "CASH_ACCRUAL": "CASH",
        "DEBIT_ACCRUAL": "DEBIT",
        "COLLATERAL_ACCRUAL": "COLLATERAL",
        "COLLATERAL_TRANSFER": "COLLATERAL",
        "MARGIN_TRANSFER_CASH_LEG": "CASH",
        "TRADE_SETTLEMENT": "CASH",
        "INITIAL_MARGIN": "MARGIN",
        "MAINTENANCE_MARGIN": "MARGIN",
        "VARIATION_MARGIN": "MARGIN",
        "FINAL_SETTLEMENT": "CASH",
        "FEES_TAX": "CASH",
    }
    actual_event_buckets = {
        rule.get("event_type"): rule.get("allowed_bucket")
        for rule in routing_contract.get("exclusive_balance_bucket_rules", [])
        if isinstance(rule, dict)
    }
    routing_assertions = {
        item.get("operator")
        for item in routing_contract.get("routing_assertions", [])
        if isinstance(item, dict)
    }
    nav_bridge = routing_contract.get("daily_nav_bridge", {})
    require(
        actual_event_buckets == expected_event_buckets
        and {
            "trade_settlement_and_fee_tax_enter_CASH_once_only; DEBIT is reserved for nonnegative DEBIT_ACCRUAL and no hidden financing draw/repayment is permitted",
            "INITIAL_MARGIN_MAINTENANCE_MARGIN_and_COLLATERAL_TRANSFER_require_exactly_one_immutable_cash_margin_collateral_transfer_pair_with_one_negative_CASH_LEG_and_one_positive_MARGIN_or_COLLATERAL_leg; the paired net_nav_effect is zero",
            "VARIATION_MARGIN_and_FINAL_SETTLEMENT_are_mark_to_market_P_and_L_legs_not_asset-transfer pairs and must follow their calculated settlement-delta formula",
        }
        <= routing_assertions
        and nav_bridge.get("formula")
        == "total_nav = cash_balance - debit_balance + collateral_balance + margin_balance + SUM(marked_value_ledger_currency) + SUM(unsettled_net_nav_ledger_currency_amount)"
        and nav_bridge.get("failure_status") == "INVALID",
        "cash/debit/margin routing must prevent hidden financing, pair asset transfers and bridge signed unsettled balances exactly once",
        failures,
    )
    paired_transfer_contract = machine_contract.get("paired_transfer_conservation_contract", {})
    paired_transfer_kinds = {
        (
            rule.get("reserve_event_type"),
            rule.get("transfer_kind"),
            rule.get("reserve_bucket"),
            rule.get("cash_event_type"),
            rule.get("cash_bucket"),
        )
        for rule in paired_transfer_contract.get("required_pairs", [])
        if isinstance(rule, dict)
    }
    paired_transfer_assertions = {
        item.get("operator")
        for item in paired_transfer_contract.get("pair_assertions", [])
        if isinstance(item, dict)
    }
    require(
        paired_transfer_contract.get("pair_table")
        == "cash_margin_collateral_transfer_pair"
        and paired_transfer_contract.get("event_table")
        == "execution_cash_margin_settlement_ledger_event"
        and paired_transfer_kinds
        == {
            ("INITIAL_MARGIN", "INITIAL_MARGIN", "MARGIN", "MARGIN_TRANSFER_CASH_LEG", "CASH"),
            ("MAINTENANCE_MARGIN", "MAINTENANCE_MARGIN", "MARGIN", "MARGIN_TRANSFER_CASH_LEG", "CASH"),
            ("COLLATERAL_TRANSFER", "COLLATERAL_TRANSFER", "COLLATERAL", "MARGIN_TRANSFER_CASH_LEG", "CASH"),
        }
        and {
            "cash_leg_ledger_currency_amount_plus_reserve_leg_ledger_currency_amount_equals_zero",
            "pair.net_nav_effect_equals_zero_and_pair.transfer_pair_status_equals_PAIRED",
            "no_INITIAL_MARGIN_MAINTENANCE_MARGIN_or_COLLATERAL_TRANSFER_event_may_exist_without_exactly_one_pair",
        }
        <= paired_transfer_assertions
        and paired_transfer_contract.get("failure_status") == "INVALID",
        "cash, margin and collateral transfers must be represented by a zero-NAV paired-transfer conservation contract",
        failures,
    )
    unsettled_contract = machine_contract.get(
        "unsettled_settlement_payable_receivable_contract", {}
    )
    failed_settlement_assertion = unsettled_contract.get("failed_settlement_assertion", {})
    failed_settlement_rows = [
        row
        for row in unsettled_contract.get("gross_posted_outstanding_assertions", [])
        if isinstance(row, dict)
        and row.get("when") == "settlement_obligation_status_is_FAILED"
    ]
    require(
        unsettled_contract.get("event_table")
        == "execution_cash_margin_settlement_ledger_event"
        and len(failed_settlement_rows) == 1
        and failed_settlement_rows[0].get("endpoint_effect") == "INVALID"
        and failed_settlement_assertion.get("when", {}).get(
            "settlement_obligation_status"
        )
        == "FAILED"
        and failed_settlement_assertion.get("endpoint_status") == "INVALID"
        and failed_settlement_assertion.get("admissibility") == "BLOCKED"
        and unsettled_contract.get("failure_status") == "INVALID",
        "FAILED settlement must retain a zero-posted outstanding obligation and invalidate the endpoint",
        failures,
    )
    fill_event_rule = machine_contract.get("fill_event_link_allocation_rule", {})
    collateral_transfer_formula = fill_event_rule.get(
        "event_calculation_formulas", {}
    ).get("COLLATERAL_TRANSFER_FROM_DATED_TERM", {})
    futures_trade_formula = fill_event_rule.get(
        "event_calculation_formulas", {}
    ).get("TRADE_SETTLEMENT_FUTURES_NON_NOTIONAL_ADJUSTMENT_ONLY", {})
    require(
        collateral_transfer_formula.get("event_type") == "COLLATERAL_TRANSFER"
        and {
            "cash_collateral_terms.term_type=COLLATERAL_TRANSFER",
            "cash_collateral_terms.rate_or_timing_value",
            "cash_collateral_terms.rate_or_timing_value_unit",
            "cash_collateral_terms.source_revision",
            "cash_collateral_terms.source_reference",
            "cash_collateral_term_set_membership.application_role=COLLATERAL",
        }
        <= set(collateral_transfer_formula.get("inputs", []))
        and "positive dated COLLATERAL_TRANSFER term value"
        in collateral_transfer_formula.get("formula", "")
        and futures_trade_formula.get("event_type") == "TRADE_SETTLEMENT"
        and "futures trade-principal notional cash leg is exactly zero"
        in futures_trade_formula.get("formula", ""),
        "collateral transfers and futures trade settlement require distinct dated non-fictitious amount sources",
        failures,
    )

    derivation_audit = load_json("data/u0_to_t2_derivation_audit_requirements_20260814.json")
    require(
        derivation_audit.get("audit_id") == "DPSFS-U0T2-v1",
        "U0-to-T2 audit ID must be DPSFS-U0T2-v1",
        failures,
    )
    require(
        derivation_audit.get("status") == "requirements_only_not_generated_not_frozen",
        "U0-to-T2 audit must remain requirements-only/not generated/not frozen",
        failures,
    )
    require(
        derivation_audit.get("portfolio_q") == 0,
        "U0-to-T2 audit must retain portfolio_q=0",
        failures,
    )
    require_texts(
        derivation_audit,
        (
            "u0_snapshot_sha256",
            "parent_class_id",
            "selection_rule_id_and_sha256",
            "every_failed_gate_or_inclusion_reason",
            "manual_override_id_or_null",
            "coverage-restricted",
            "0 manual nomination",
        ),
        "U0-to-T2 derivation audit",
        failures,
    )

    t2 = load_json("data/t2_candidate_universe_20260814.json")
    require(
        t2.get("status") == "draft_comparison_universe_not_frozen",
        "draft T2 comparison universe must remain not frozen",
        failures,
    )
    require(t2.get("portfolio_q") == 0, "draft T2 must retain portfolio_q=0", failures)
    t2_audit = t2.get("u0_derivation_audit", {})
    require(
        t2_audit.get("required_audit_id") == "DPSFS-U0T2-v1",
        "draft T2 must identify its required U0-to-T2 audit",
        failures,
    )
    require(
        t2_audit.get("required_registry_id") == "DPSFS-U0-v2"
        and t2_audit.get("required_registry_version") == 2,
        "draft T2 must bind the current U0 registry ID/version",
        failures,
    )
    require(
        t2_audit.get("status") == "not_generated_no_frozen_u0_snapshot",
        "draft T2 must not imply a generated U0 derivation audit",
        failures,
    )
    require(
        t2_audit.get("coverage_label") == "draft_probe_not_open_universe_test",
        "draft T2 must retain its probe/not-open-universe label",
        failures,
    )
    candidate_ids = [item.get("id") for item in t2.get("candidates", [])]
    require(
        len(candidate_ids) == len(set(candidate_ids)),
        "draft T2 contains duplicate candidate IDs",
        failures,
    )
    for item in t2.get("candidates", []):
        item_id = item.get("id", "<missing ID>")
        require(item.get("current_q") == 0, f"draft T2 item {item_id} must remain q=0", failures)
        require(
            item.get("parent_class_id") in class_by_id,
            f"draft T2 item {item_id} has no U0 parent class",
            failures,
        )

    protocol = load_json("data/formal_replay_protocol_requirements_20260814.json")
    require(
        protocol.get("status") == "requirements_only_not_frozen_not_runnable",
        "replay protocol must remain requirements-only/not frozen/not runnable",
        failures,
    )
    require(protocol.get("portfolio_q") == 0, "replay protocol must retain portfolio_q=0", failures)
    require(
        protocol.get("protocol_id") == "DPSFS-RP0-v10",
        "replay protocol ID must be DPSFS-RP0-v10",
        failures,
    )
    require(protocol.get("protocol_version") == 10, "replay protocol version must be 10", failures)
    require(
        protocol.get("schema_version") == "formal_replay_protocol_requirements.v10",
        "replay protocol schema version must be v10",
        failures,
    )
    require(
        protocol.get("protocol_freeze_control", {}).get("state") == "not_frozen",
        "replay protocol freeze state must remain not_frozen",
        failures,
    )
    protocol_freeze_fields = protocol.get("protocol_freeze_control", {}).get(
        "required_freeze_fields", []
    )
    for field in (
        "protocol_id",
        "protocol_version",
        "protocol_sha256",
        "u0_to_t2_derivation_audit_sha256",
        "primary_holdout_window_predicate_sha256",
        "order_state_transition_matrix_sha256",
        "risk_feasibility_control_sha256",
        "expected_candidate_endpoint_count",
        "expected_primary_holdout_candidate_endpoint_count",
        "replay_run_freeze_record_schema_version",
        "data_dictionary_id",
        "data_dictionary_schema_version",
        "endpoint_calculation_population_policy_sha256",
        "portfolio_unitization_positions_lots_cashflow_reconciliation_policy_sha256",
        "fill_leg_partial_fill_allocation_policy_sha256",
        "broker_tax_component_policy_sha256",
        "execution_settlement_state_policy_sha256",
        "prospective_state_configuration_coverage_policy_sha256",
    ):
        require(
            field in protocol_freeze_fields,
            f"replay protocol freeze control missing {field}",
            failures,
        )
    require(
        protocol.get("objective_boundary", {}).get("research_criterion")
        == "The strict historical research hurdle is that every complete eligible rolling five-calendar-year endpoint has annualized net TWRR at or above 5%.",
        "replay protocol has an altered or ambiguous strict research criterion",
        failures,
    )
    run_binding = protocol.get("replay_run_binding_and_bound_row_requirement", {})
    require(
        run_binding.get("required_dictionary", {}).get("dictionary_id")
        == "DPSFS-DD-v8",
        "replay protocol must bind DPSFS-DD-v8 as its required dictionary",
        failures,
    )
    protocol_bound_row_tables = run_binding.get("bound_row_tables", [])
    require(
        len(protocol_bound_row_tables) == len(set(protocol_bound_row_tables))
        and set(protocol_bound_row_tables) == set(run_dependent_tables),
        "replay protocol bound-row inventory must exactly equal the dictionary run-dependent table inventory",
        failures,
    )
    require(
        run_binding.get("bound_row_required_fields")
        == ["replay_run_id", "replay_run_freeze_record_sha256"],
        "replay protocol must require the exact composite frozen-run child binding",
        failures,
    )
    require_texts(
        run_binding,
        (
            "replay_run_freeze_record_sha256",
            "excluding that hash field itself",
            "DPSFS-DAC-v12",
            "DPSFS-RP0-v10",
            "DPSFS-DD-v8",
            "primary_holdout_start_state_component",
            "execution_order_state_transition",
            "execution_cash_margin_settlement_ledger_event",
        ),
        "replay protocol frozen-run binding",
        failures,
    )
    status_policy = protocol.get("window_and_twr_definition", {}).get(
        "rolling_window_rule", {}
    ).get("status_policy", {})
    rolling_rule = protocol.get("window_and_twr_definition", {}).get(
        "rolling_window_rule", {}
    )
    require(
        set(status_policy) == {"PASS", "FAIL", "INCOMPLETE", "INVALID"},
        "replay protocol must expose all endpoint statuses",
        failures,
    )
    for field in (
        "reporting_population",
        "valid_calculation",
        "missing_endpoint_policy",
        "strict_result_rule",
        "minimum_candidate_endpoint_count",
        "minimum_candidate_endpoint_rationale",
        "zero_candidate_endpoint_status",
        "expected_candidate_endpoint_match_rule",
        "endpoint_partition_reconciliation_rule",
        "endpoint_count_requirement",
    ):
        require(
            bool(rolling_rule.get(field)),
            f"replay protocol missing rolling-window control {field}",
            failures,
        )
    require(
        rolling_rule.get("minimum_candidate_endpoint_count") == 252,
        "replay protocol must require 252 all-history candidate endpoints",
        failures,
    )
    require(
        rolling_rule.get("zero_candidate_endpoint_status") == "INCOMPLETE",
        "replay protocol must classify a zero endpoint population as INCOMPLETE",
        failures,
    )
    for field in (
        "calendar_anchor",
        "start_selection",
        "annualization",
        "endpoint_calculation_and_population_audit",
    ):
        require(
            bool(rolling_rule.get(field)),
            f"replay protocol missing a/s/e or endpoint-population control {field}",
            failures,
        )
    require_texts(
        rolling_rule.get("annualization", ""),
        (
            "end_unit_nav / start_unit_nav",
            "total-NAV ratio is prohibited",
            "endpoint_calculation_sha256",
        ),
        "replay protocol unit-NAV annualization",
        failures,
    )
    require_texts(
        rolling_rule.get("endpoint_calculation_and_population_audit", {}),
        (
            "calendar_anchor_at",
            "selected_start_valuation_at",
            "endpoint_end_valuation_at",
            "window_start",
            "window_end",
            "pass_count",
            "fail_count",
            "incomplete_count",
            "invalid_count",
            "zero_candidate_status",
        ),
        "replay protocol a/s/e endpoint-population audit",
        failures,
    )
    require_texts(
        rolling_rule.get("expected_candidate_endpoint_match_rule", ""),
        ("actual_candidate_endpoint_count", "frozen expected_candidate_endpoint_count", "INCOMPLETE"),
        "replay protocol expected-versus-actual endpoint-count rule",
        failures,
    )
    require_texts(
        rolling_rule.get("minimum_candidate_endpoint_rationale", ""),
        ("252", "Overlap", "not make endpoint rows independent evidence"),
        "replay protocol all-history endpoint-minimum rationale",
        failures,
    )
    require_texts(
        rolling_rule.get("endpoint_partition_reconciliation_rule", ""),
        (
            "exactly once",
            "DEVELOPMENT",
            "PRIMARY_HOLDOUT",
            "CROSSING",
            "INVALID",
        ),
        "replay protocol endpoint-partition reconciliation rule",
        failures,
    )
    require_texts(
        rolling_rule,
        (
            "expected_candidate_endpoint_count",
            "actual_candidate_endpoint_count",
            "zero",
            "cannot pass",
            "differs from the frozen expected count",
        ),
        "replay protocol rolling-window rule",
        failures,
    )
    unitization = protocol.get("window_and_twr_definition", {}).get(
        "portfolio_unitization", {}
    )
    require_texts(
        unitization,
        (
            "issue or redeem units",
            "No silent rebase",
            "zero or negative",
            "not a personal net-result claim",
        ),
        "replay protocol unitization",
        failures,
    )
    pre_result = protocol.get("pre_result_freeze_and_blinding", {})
    require_texts(
        pre_result.get("required_bindings", []),
        (
            "formal replay protocol ID, version and SHA-256",
            "U0-to-T2 derivation-audit SHA-256",
            "expected candidate-endpoint count",
            "expected primary-holdout candidate-endpoint count",
        ),
        "replay protocol freeze bindings",
        failures,
    )
    require_texts(
        pre_result.get("result_population_rule", ""),
        (
            "DEVELOPMENT",
            "PRIMARY_HOLDOUT",
            "CROSSING",
            "Every candidate endpoint is in exactly one table",
            "plus CROSSING",
            "CROSSING endpoint vetoes the all-history hurdle",
        ),
        "replay protocol result-population rule",
        failures,
    )
    require_texts(
        pre_result.get("primary_holdout_endpoint_rule", ""),
        (
            "expected_primary_holdout_candidate_endpoint_count",
            "that common count is at least 126",
            "actual_primary_holdout_candidate_endpoint_count",
            "no independent out-of-sample or validated-strategy result",
        ),
        "replay protocol primary-holdout endpoint rule",
        failures,
    )
    require_texts(
        pre_result.get("validated_result_rule", ""),
        ("all-history strict hurdle", "PRIMARY_HOLDOUT strict hurdle", "descriptive only"),
        "replay protocol validated-result rule",
        failures,
    )
    require_texts(
        pre_result.get("primary_holdout_window_predicate", ""),
        (
            "window_start",
            "frozen maximum input-lookback/warmup interval",
            "available_at",
            "cannot enter PRIMARY_HOLDOUT by endpoint date alone",
        ),
        "replay protocol primary-holdout window predicate",
        failures,
    )
    require_texts(
        pre_result.get("holdout_invalidation_rule", ""),
        (
            "invalidates the prior PRIMARY_HOLDOUT result",
            "new lockbox interval",
            "cost/execution model",
        ),
        "replay protocol primary-holdout invalidation rule",
        failures,
    )
    require_texts(
        pre_result.get("usable_strategy_status_rule", ""),
        (
            "all-history strict hurdle",
            "PRIMARY_HOLDOUT strict hurdle",
            "risk-and-feasibility control pack",
            "prospective paper-reconciliation gate",
            "severity-S",
            "q=0",
            "not a return guarantee",
        ),
        "replay protocol usable-strategy status rule",
        failures,
    )
    require_texts(
        protocol.get("interpretation_and_robustness_controls", {}),
        (
            "not an independent sample size",
            "non-overlapping",
            "regime/stress",
            "cannot replace the all-endpoint hurdle",
            "never be described as independent confirmation",
        ),
        "replay protocol interpretation/robustness controls",
        failures,
    )
    universe_controls = protocol.get("universe_derivation_and_scope_control", {})
    require_texts(
        universe_controls,
        (
            "parent_class_id",
            "accepted data package",
            "coverage-restricted",
            "manual nomination",
        ),
        "replay protocol universe derivation control",
        failures,
    )
    require_texts(
        protocol.get("options_rule_requirements", {}),
        ("exercise", "assignment", "full option-chain", "no-fill"),
        "replay protocol options control",
        failures,
    )
    require_texts(
        protocol.get("cost_execution_and_accounting_controls", {}),
        (
            "quote timestamp",
            "Cash yield",
            "initial/maintenance margin",
            "broker route, clearing/account entity",
            "personal net tax",
            "remaining displayed/model capacity",
            "TAX or LEVY",
            "FEES_TAX",
            "CASH_BALANCE applicability",
        ),
        "replay protocol cost and accounting control",
        failures,
    )
    transition_matrix = protocol.get("cost_execution_and_accounting_controls", {}).get(
        "order_state_transition_matrix_requirement", {}
    )
    require(
        set(transition_matrix.get("execution_states", []))
        == {
            "CREATED",
            "SUBMITTED",
            "PARTIAL",
            "PARTIAL_EXPIRED",
            "PARTIAL_CANCELLED",
            "FILLED",
            "NO_FILL",
            "EXPIRED",
            "CANCELLED",
            "REJECTED",
            "NOT_SUBMITTED",
            "FAILED",
        },
        "replay protocol execution-state matrix is not exactly aligned to the dictionary",
        failures,
    )
    require(
        set(transition_matrix.get("settlement_states", []))
        == {"NOT_APPLICABLE", "PENDING", "PARTIALLY_SETTLED", "SETTLED", "FAILED"},
        "replay protocol settlement-state matrix is inconsistent with the data dictionary",
        failures,
    )
    require_texts(
        transition_matrix,
        (
            "CREATED->SUBMITTED, REJECTED or NOT_SUBMITTED",
            "SUBMITTED->PARTIAL, FILLED, NO_FILL, EXPIRED, CANCELLED, REJECTED or FAILED",
            "PARTIAL->PARTIAL, FILLED, PARTIAL_EXPIRED or PARTIAL_CANCELLED",
            "PARTIAL->FAILED and PARTIAL->CANCELLED are forbidden",
            "NOT_APPLICABLE->SETTLED",
            "DOCUMENTED_INSTANTANEOUS_CLEARING",
            "Execution and settlement transition sequences are independently nondecreasing",
            "end_of_run_order_disposition",
            "versioned replacement",
        ),
        "replay protocol state-transition matrix",
        failures,
    )
    risk_feasibility = protocol.get("risk_and_feasibility_controls", {})
    require_texts(
        risk_feasibility,
        (
            "Before any outcome is viewed",
            "maximum drawdown",
            "concentration",
            "margin",
            "liquidity, capacity",
            "no-fill",
            "instrument-specific legal, broker-route and suitability evidence",
            "blocks usable-strategy status",
        ),
        "replay protocol risk-and-feasibility controls",
        failures,
    )
    require_texts(
        protocol.get("mandatory_outputs", {}).get("endpoint_count_fields", []),
        (
            "expected candidate-endpoint count",
            "actual candidate-endpoint count",
            "expected/actual primary-holdout candidate-endpoint count and primary-holdout status",
            "PASS/FAIL/INCOMPLETE/INVALID counts",
            "zero-count or shortfall status",
            "reconciled all-history endpoint total and partition exception state",
        ),
        "replay protocol endpoint-count outputs",
        failures,
    )
    require_texts(
        protocol.get("mandatory_outputs", {}).get("supplemental_outputs", []),
        (
            "deterministic non-overlapping-window selection audit",
            "PRIMARY_HOLDOUT predicate audit",
            "Order-state-transition matrix",
            "Frozen risk-and-feasibility control pack",
        ),
        "replay protocol supplemental outputs",
        failures,
    )
    require_texts(
        protocol.get("formal_run_entry_conditions", []),
        (
            "The protocol ID, version and SHA-256",
            "zero, shortfall or count mismatch produces INCOMPLETE",
            "at least 252 candidate rolling endpoints",
            "PRIMARY_HOLDOUT strict hurdle requires",
            ">= 126",
            "Every U0 parent class represented in T2",
            "CROSSING is disclosed separately and vetoes the all-history hurdle",
            "post-lockbox start-state policy",
            "allowed order-state-transition matrix",
            "state/configuration coverage matrix",
            "risk-and-feasibility control pack",
            "usable-strategy status",
        ),
        "replay protocol formal-run entry conditions",
        failures,
    )
    require_texts(
        protocol.get("listed_security_rule_requirements", {}).get(
            "mandatory_order_ledger_fields", []
        ),
        (
            "broker-route identifier",
            "execution side",
            "submitted, filled, expiry, cancellation and settlement timestamps/states",
            "quote-snapshot or conservative-proxy composite key",
            "cash-collateral term-set identifier",
            "order-state-transition ledger reference",
        ),
        "replay protocol listed-security order-ledger requirements",
        failures,
    )
    for test_name in (
        "Point-in-time timestamp assertion for every decision input.",
        "Event-adjustment no-double-count reconciliation.",
        "Actual-contract chain and roll-trail test.",
        "Deterministic rerun test: identical frozen inputs produce identical decisions, order ledger, daily NAV and endpoint table.",
    ):
        require(
            test_name in protocol.get("mandatory_anti_leakage_tests", []),
            f"replay protocol missing mandatory test: {test_name}",
        failures,
    )

    dac_accounting = contract.get("paired_transfer_settlement_and_futures_mtm_control", {})
    rp_accounting = protocol.get("cost_execution_and_accounting_controls", {}).get(
        "paired_transfer_settlement_and_futures_mtm_requirement", {}
    )
    for field in (
        "dictionary_tables",
        "cash_margin_collateral_transfer_pair_required_fields",
        "cash_collateral_terms_required_fields",
    ):
        require(
            dac_accounting.get(field) == rp_accounting.get(field),
            f"data contract and replay protocol disagree on {field}",
            failures,
        )
    require(
        dac_accounting.get("paired_transfer_conservation_contract", {}).get(
            "event_matrix"
        )
        == rp_accounting.get("paired_transfer_conservation_contract", {}).get(
            "event_matrix"
        ),
        "data contract and replay protocol disagree on the required cash/margin/collateral pair matrix",
        failures,
    )
    require(
        set(dac_accounting.get("dictionary_tables", []))
        == {
            "execution_cash_margin_settlement_ledger_event",
            "cash_margin_collateral_transfer_pair",
            "cash_collateral_terms",
            "portfolio_position_lot_mark_ledger",
            "daily_portfolio_ledger",
            "portfolio_cashflow_pnl_ledger",
        },
        "data contract must bind all accounting-control tables to the formal replay schema",
        failures,
    )
    require_table_columns(
        table_by_id,
        "cash_margin_collateral_transfer_pair",
        set(dac_accounting.get("cash_margin_collateral_transfer_pair_required_fields", [])),
        failures,
    )
    require_table_columns(
        table_by_id,
        "cash_collateral_terms",
        set(dac_accounting.get("cash_collateral_terms_required_fields", [])),
        failures,
    )
    require_texts(
        dac_accounting,
        (
            "MARGIN_TRANSFER_CASH_LEG",
            "posted_balance_effect_ledger_currency_amount",
            "COLLATERAL_TRANSFER",
            "FUTURES_DAILY_MARGINED",
            "FAILED",
            "INVALID",
        ),
        "data-contract paired-transfer, settlement and futures controls",
        failures,
    )
    require_texts(
        rp_accounting,
        (
            "MARGIN_TRANSFER_CASH_LEG",
            "posted_balance_effect_ledger_currency_amount",
            "COLLATERAL_TRANSFER",
            "FUTURES_DAILY_MARGINED",
            "FAILED",
            "INVALID",
        ),
        "replay-protocol paired-transfer, settlement and futures controls",
        failures,
    )

    for legacy_token in (
        "window_start_anchor_at",
        "selected_valuation_at",
        "fill_leg_sequence",
        "fill_timestamp",
        "delta_filled_quantity",
        "residual_quantity",
        "commission_component_amount",
        "tax_levy_component_amount",
        "TAX_OR_LEVY",
        "SETTLEMENT_FAILED",
        "CARRIED_TO_NEXT_RUN",
        "CANCELLED_AT_END_OF_RUN",
        "DPSFS-DAC-v10 or later",
    ):
        require(
            not contains_text(protocol, legacy_token),
            f"replay protocol retains a legacy/incompatible control token: {legacy_token}",
            failures,
        )

    gate_manifest = load_json("gate_manifest.json")
    required_artifacts = set(gate_manifest.get("required_artifacts", []))
    for path in (
        "data/data_acquisition_contract_20260814.json",
        "data/data_access_feasibility_20260814.json",
        "data/u0_domestic_universe_registry_20260814.json",
        "data/formal_replay_protocol_requirements_20260814.json",
        "data/replay_data_dictionary_template_20260814.json",
        "data/u0_to_t2_derivation_audit_requirements_20260814.json",
        "analysis/return_source_feasibility_20260814.md",
        "analysis/r1_open_universe_coverage_gap_20260814.md",
        "analysis/r1_primary_source_route_catalog_20260814.md",
        "review_findings_R1_model.json",
        "repair_plan_R1_model.md",
        "repair_plan_R1_model.json",
    ):
        require(path in required_artifacts, f"gate manifest missing {path}", failures)
    require(
        "tools/verify_research_design_controls.py"
        in " ".join(gate_manifest.get("verifiers", [])),
        "gate manifest does not register design-controls verifier",
        failures,
    )

    artifact_contract = load_json("artifact_contract.json")
    artifact_text = json.dumps(artifact_contract, ensure_ascii=False)
    require(
        artifact_contract.get("artifact_contract_version") == "v6",
        "artifact contract must be refreshed to v6 for the R1 lifecycle and open-universe coverage",
        failures,
    )
    for artifact_name in (
        "data/data_acquisition_contract_20260814.{md,json}",
        "data/data_access_feasibility_20260814.{md,json}",
        "data/u0_domestic_universe_registry_20260814.{md,json}",
        "data/u0_to_t2_derivation_audit_requirements_20260814.{md,json}",
        "data/formal_replay_protocol_requirements_20260814.{md,json}",
        "data/replay_data_dictionary_template_20260814.{md,json}",
        "analysis/r1_open_universe_coverage_gap_20260814.md and analysis/r1_primary_source_route_catalog_20260814.md",
        "review_findings_R1_model.json and repair_plan_R1_model.{md,json}",
    ):
        require(
            artifact_name in artifact_text,
            f"artifact contract missing {artifact_name}",
            failures,
        )

    r1_review = load_json("review_findings_R1_model.json")
    require(
        r1_review.get("schema_version") == "r1_model_review.v1"
        and r1_review.get("case_id")
        == "domestic-personal-securities-futures-strategy-20260814"
        and r1_review.get("cycle") == "R1_model",
        "R1 findings must identify the current R1 model-review lifecycle",
        failures,
    )
    require(
        r1_review.get("initial_publishability_status") == "BLOCKED"
        and r1_review.get("post_repair_status") == "BLOCKED",
        "R1 review must remain blocked before entitlement, replay and prospective reconciliation",
        failures,
    )
    r1_findings_by_id = {
        finding.get("issue_id"): finding
        for finding in r1_review.get("findings", [])
        if isinstance(finding, dict)
    }
    for issue_id in (
        "R1-S-001",
        "R1-S-002",
        "R1-S-003",
        "R1-S-004",
        "R1-S-005",
        "R1-S-006",
        "R1-S-007",
        "R1-A-001",
    ):
        finding = r1_findings_by_id.get(issue_id, {})
        for field in (
            "cycle",
            "severity",
            "owner_skill",
            "owner_agent",
            "artifact",
            "evidence",
            "fix_required",
            "blocking_gate",
            "status",
            "verifier_ref",
            "reopened_count",
        ):
            require(
                field in finding,
                f"R1 finding {issue_id} is missing required lifecycle field {field}",
                failures,
            )
    require(
        {
            issue_id
            for issue_id in ("R1-S-001", "R1-S-002", "R1-S-003", "R1-S-004")
            if r1_findings_by_id.get(issue_id, {}).get("status") == "closed"
        }
        == {"R1-S-001", "R1-S-002", "R1-S-003", "R1-S-004"},
        "R1 static accounting-schema repairs require independently verified closure",
        failures,
    )
    require(
        {
            issue_id
            for issue_id in ("R1-S-005", "R1-S-006", "R1-S-007")
            if r1_findings_by_id.get(issue_id, {}).get("status") == "open"
        }
        == {"R1-S-005", "R1-S-006", "R1-S-007"},
        "R1 external entitlement, replay and prospective-reconciliation blockers must remain open",
        failures,
    )
    require(
        r1_findings_by_id.get("R1-A-001", {}).get("status") == "closed",
        "R1 open-universe coverage finding must be independently closed after the source-route repair check",
        failures,
    )
    require_texts(
        r1_review.get("final_repair_check", {}),
        (
            "PASS_FOR_STATIC_DESIGN_CONTROLS_ONLY",
            "26 run-dependent tables",
            "38 fields",
            "14 static accounting and valuation checks passed",
            "does not establish a data entitlement",
        ),
        "R1 final static-design repair check",
        failures,
    )
    require_texts(
        r1_review.get("current_decision", ""),
        ("non-investable", "q=0", "No product", "return result"),
        "R1 current decision",
        failures,
    )
    require_texts(
        r1_review.get("source_route_repair_check", {}),
        (
            "PASS_FOR_OPEN_UNIVERSE_SOURCE_ROUTE_BOUNDARY_ONLY",
            "All ten U0 classes",
            "six-class statement",
            "did not test current external URL availability",
        ),
        "R1 open-universe source-route repair check",
        failures,
    )
    require_texts(
        r1_review.get("open_class_request_pack_check", {}),
        (
            "PASS_FOR_REQUEST_SPECIFICATION_BOUNDARY_ONLY",
            "Eleven static checks passed",
            "not sent",
            "does not create a current DAC-v12 package",
            "R1-S-005 remains open",
            "did not test any future provider capability",
        ),
        "R1 open-class request-pack boundary check",
        failures,
    )
    r1_plan = load_json("repair_plan_R1_model.json")
    require(
        r1_plan.get("schema_version") == "r1_model_repair_plan.v1"
        and r1_plan.get("cycle") == "R1_model"
        and r1_plan.get("status")
        == "static_design_repairs_verified_external_gates_open_not_investable",
        "R1 repair plan must retain the static-only, non-investable status",
        failures,
    )
    r1_task_by_id = {
        task.get("id"): task for task in r1_plan.get("tasks", []) if isinstance(task, dict)
    }
    for task_id in (
        "R1-RP-001",
        "R1-RP-002",
        "R1-RP-003",
        "R1-RP-004",
        "R1-RP-005",
        "R1-RP-006",
        "R1-RP-007",
        "R1-RP-008",
    ):
        require(task_id in r1_task_by_id, f"R1 repair plan is missing {task_id}", failures)
    require(
        all(
            r1_task_by_id.get(task_id, {}).get("status") == "verified"
            for task_id in ("R1-RP-001", "R1-RP-002", "R1-RP-003", "R1-RP-004", "R1-RP-008")
        )
        and r1_task_by_id.get("R1-RP-005", {}).get("status")
        == "external_prerequisite_open",
        "R1 repair plan must separate verified design repairs from the open external prerequisite",
        failures,
    )
    require_texts(
        r1_plan.get("hard_boundary", ""),
        ("q=0", "allocation", "return claim", "return guarantee"),
        "R1 repair-plan boundary",
        failures,
    )

    open_universe_gap = load_text("analysis/r1_open_universe_coverage_gap_20260814.md")
    source_route_catalog = load_text("analysis/r1_primary_source_route_catalog_20260814.md")
    for class_id in required_classes:
        require(
            class_id in open_universe_gap and class_id in source_route_catalog,
            f"R1 open-universe documents omit U0 class {class_id}",
            failures,
        )
    for route_id in (f"R{index:02d}" for index in range(1, 18)):
        require(
            route_id in source_route_catalog,
            f"R1 primary-source route catalog omits {route_id}",
            failures,
        )
    require_texts(
        open_universe_gap,
        ("全部十个", "q=0", "并非该类在经济上", "被否定或排除", "不能跳过的闭环顺序"),
        "R1 open-universe coverage gap",
        failures,
    )
    require_texts(
        source_route_catalog,
        ("R01`--`R17", "不是数据交付", "因而它们不能关闭", "UR01--UR05", "所有类别继续 `q=0`"),
        "R1 primary-source route catalog",
        failures,
    )

    markdown_expectations = {
        "data/data_acquisition_contract_20260814.md": (
            "DPSFS-DAC-v12",
            "UR01--UR05",
            "q=0",
            "replay_run_freeze_record",
            "frozen_fx_quote_conversion",
            "cash_margin_collateral_transfer_pair",
            "FUTURES_DAILY_MARGINED",
            "COLLATERAL_TRANSFER",
            "FAILED",
        ),
        "data/u0_domestic_universe_registry_20260814.md": (
            "DPSFS-U0-v2",
            "q=0",
            "Leveraged/inverse",
        ),
        "data/formal_replay_protocol_requirements_20260814.md": (
            "DPSFS-RP0-v10",
            "q=0",
            "CROSSING",
            "replay_run_freeze_record",
            "DPSFS-DAC-v12",
            "PRIMARY_HOLDOUT",
            "execution_fill_ledger",
            "cash_margin_collateral_transfer_pair",
            "FUTURES_DAILY_MARGINED",
            "COLLATERAL_TRANSFER",
            "FAILED",
        ),
        "data/data_access_feasibility_20260814.md": (
            "DPSFS-DAC-v12",
            "UR01、UR02、UR03",
            "q=0",
            "不据此断言市场上不存在",
            "中金所历史数据服务",
            "今天能按日期提供查询，不等于",
        ),
        "data/replay_data_dictionary_template_20260814.md": (
            "DPSFS-DD-v8",
            "IOPV",
            "replay_run_freeze_record",
            "execution_fill_ledger",
            "frozen_fx_quote_conversion",
            "cash_margin_collateral_transfer_pair",
            "FUTURES_DAILY_MARGINED",
            "COLLATERAL_TRANSFER",
            "FAILED",
        ),
        "data/u0_to_t2_derivation_audit_requirements_20260814.md": (
            "DPSFS-U0T2-v1",
            "q=0",
            "coverage-restricted",
        ),
        "data/t2_candidate_universe_20260814.md": (
            "DPSFS-U0T2-v1",
            "q=0",
            "coverage-restricted",
        ),
        "analysis/r1_open_universe_coverage_gap_20260814.md": (
            "DPSFS-U0-v2",
            "RQP-U0",
            "UR01--UR05",
            "q=0",
        ),
        "analysis/r1_primary_source_route_catalog_20260814.md": (
            "DPSFS-U0-v2",
            "R01",
            "R17",
            "UR01--UR05",
            "q=0",
        ),
        "repair_plan_R1_model.md": (
            "R1-S-005",
            "R1-S-007",
            "q=0",
            "独立审计",
        ),
    }
    for path, expectations in markdown_expectations.items():
        text = load_text(path)
        for expected in expectations:
            require(
                expected in text,
                f"Markdown/JSON twin {path} missing required synchronized control: {expected}",
                failures,
            )

    for markdown_path in CASE_DIR.rglob("*.md"):
        if "sources" in markdown_path.relative_to(CASE_DIR).parts:
            continue
        require(
            "本金" not in markdown_path.read_text(encoding="utf-8"),
            f"non-source case document must not reintroduce a principal-amount discussion: {markdown_path.relative_to(CASE_DIR)}",
            failures,
        )

    if failures:
        print("DESIGN CONTROLS: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print(
        "DESIGN CONTROLS: PASS "
        "(draft governance only; no entitlement, replay, admission, allocation or action)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
