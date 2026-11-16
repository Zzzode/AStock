#!/usr/bin/env python3
"""Independently validate current-case source, claim, ledger and no-action controls."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


CASE_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = CASE_DIR.parents[2]
AS_OF = "2026-08-15"
SOURCE_REGISTRY = CASE_DIR / "data" / "source_registry.json"
CLAIM_AUDIT = CASE_DIR / "data" / "claim_audit.json"
LEDGER = CASE_DIR / "data" / "research_ledger.json"
R07 = CASE_DIR / "analysis" / "r07_current_open_universe_disposition_20260815.json"
R14 = CASE_DIR / "analysis" / "r14_open_universe_feasibility_expansion_audit_20260815.json"
ARTIFACT_CONTRACT = CASE_DIR / "artifact_contract.json"
GATE_MANIFEST = CASE_DIR / "gate_manifest.json"
C33 = CASE_DIR / "analysis" / "c33_integrated_candidate_strategy_20260815.json"
C34 = CASE_DIR / "analysis" / "c34_dual_horizon_inverse_vol_etf_candidate_20260815.json"
C35 = CASE_DIR / "analysis" / "c35_c34_operational_action_card_20260815.json"
C36 = CASE_DIR / "analysis" / "c36_c31_source_crosscheck_20260815.json"
C37 = CASE_DIR / "analysis" / "c37_domestic_etf_total_return_source_route_20260815.json"
C38 = CASE_DIR / "analysis" / "c38_direct_equity_institutional_research_route_20260815.json"
C39 = CASE_DIR / "analysis" / "c39_independent_strategy_hypothesis_protocol_20260815.json"
C40 = CASE_DIR / "analysis" / "c40_600519_equity_diligence_20260815.json"
C41 = CASE_DIR / "analysis" / "c41_600900_equity_diligence_20260815.json"
C42 = CASE_DIR / "analysis" / "c42_601088_equity_diligence_20260815.json"
C43 = CASE_DIR / "analysis" / "c43_actual_contract_calendar_curve_protocol_20260815.json"
C44 = CASE_DIR / "analysis" / "c44_actual_contract_calendar_curve_diagnostic_20260815.json"
C45 = CASE_DIR / "analysis" / "c45_five_family_actual_contract_source_readiness_20260815.json"
C46 = CASE_DIR / "analysis" / "c46_actual_contract_calendar_curve_source_control_protocol_20260815.json"
C47 = CASE_DIR / "analysis" / "c47_source_controlled_calendar_curve_diagnostic_20260815.json"
C48 = CASE_DIR / "analysis" / "c48_current_environment_data_capability_audit_20260815.json"
C49 = CASE_DIR / "analysis" / "c49_official_authorized_data_route_recheck_20260815.json"
C50 = CASE_DIR / "analysis" / "c50_sse_general_repo_yield_floor_screen_20260815.json"
C51 = CASE_DIR / "analysis" / "c51_sse_etf_option_collar_scope_screen_20260815.json"
C52 = CASE_DIR / "analysis" / "c52_sse_etf_option_history_route_screen_20260815.json"
C53 = CASE_DIR / "analysis" / "c53_equity_led_domestic_target_strategy_protocol_20260815.json"
C53_LEDGER_TEMPLATE = CASE_DIR / "data" / "c53_quarterly_paper_observation_ledger_template_20260815.json"
C53_LEDGER_CSV = CASE_DIR / "data" / "c53_quarterly_paper_observation_ledger_template_20260815.csv"
R16_REPAIR_PLAN = CASE_DIR / "analysis" / "r16_parallel_route_repair_plan_20260815.json"
R17_RECHECK = CASE_DIR / "analysis" / "r17_r16_repair_independent_recheck_20260815.json"
R18_C49_AUDIT = CASE_DIR / "analysis" / "r18_c49_independent_source_audit_20260815.json"
R19_C50_AUDIT = CASE_DIR / "analysis" / "r19_c50_independent_source_audit_20260815.json"
R20_C51_INITIAL_AUDIT = CASE_DIR / "analysis" / "r20_c51_initial_independent_source_audit_20260815.json"
R20_C51_REPAIR_PLAN = CASE_DIR / "analysis" / "r20_c51_repair_plan_20260815.json"
R21_C51_RECHECK = CASE_DIR / "analysis" / "r21_c51_repair_independent_recheck_20260815.json"
R22_C52_AUDIT = CASE_DIR / "analysis" / "r22_c52_independent_source_audit_20260815.json"
R23_C52_GOVERNANCE_RECHECK = CASE_DIR / "analysis" / "r23_c52_governance_registration_independent_recheck_20260815.json"
C33_LEDGER_TEMPLATE = CASE_DIR / "data" / "c33_forward_paper_ledger_template_20260815.json"
OUTPUT_JSON = CASE_DIR / "analysis" / "r09_research_control_record_audit_20260815.json"
OUTPUT_MD = CASE_DIR / "analysis" / "r09_research_control_record_audit_20260815.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def resolve(path_text: str) -> Path:
    path = Path(path_text)
    return REPO_ROOT / path if path_text.startswith("workspace/") else CASE_DIR / path


def main() -> int:
    failures: list[str] = []
    checks: list[dict[str, Any]] = []

    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    registry = load_json(SOURCE_REGISTRY)
    claims = load_json(CLAIM_AUDIT)
    ledger = load_json(LEDGER)
    r07 = load_json(R07)
    records = registry.get("records", [])
    source_ids = [str(item.get("source_id")) for item in records if isinstance(item, dict)]
    unique_ids = len(source_ids) == len(set(source_ids)) and all(source_ids)
    check("unique source IDs", unique_ids, f"count={len(source_ids)}")

    source_file_failures: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            source_file_failures.append("non-object record")
            continue
        source_id = str(record.get("source_id") or "")
        path = resolve(str(record.get("path") or ""))
        if not path.is_file():
            source_file_failures.append(f"{source_id}: missing path")
            continue
        expected_hash = str(record.get("sha256") or "")
        if expected_hash and sha256(path) != expected_hash:
            source_file_failures.append(f"{source_id}: sha256 mismatch")
    check("registered source files and stated hashes", not source_file_failures, "; ".join(source_file_failures[:8]) or "all matched")

    claimed_ids = {
        str(source_id)
        for claim in claims.get("claims", [])
        if isinstance(claim, dict)
        for source_id in claim.get("source_ids", [])
    }
    check("claim sources resolve", bool(claimed_ids) and claimed_ids <= set(source_ids), f"claims={len(claimed_ids)} sources={len(source_ids)}")

    source_markdown = (CASE_DIR / "data" / "source_registry.md").read_text(encoding="utf-8")
    claim_markdown = (CASE_DIR / "data" / "claim_audit.md").read_text(encoding="utf-8")
    missing_source_rows = [source_id for source_id in source_ids if f"| {source_id} |" not in source_markdown]
    claim_ids = [str(item.get("claim_id")) for item in claims.get("claims", []) if isinstance(item, dict)]
    missing_claim_rows = [claim_id for claim_id in claim_ids if f"| {claim_id} |" not in claim_markdown]
    check("source markdown mirrors IDs", not missing_source_rows, ", ".join(missing_source_rows) or "all present")
    check("claim markdown mirrors IDs", not missing_claim_rows, ", ".join(missing_claim_rows) or "all present")

    required_ledger = {
        "C16 三类上期所实际合约周度趋势诊断": "closed",
        "C17 五类上期所实际合约周度趋势诊断": "closed",
        "C18 上交所公开公司债短久期信用梯可行性": "monitoring",
        "C20 境内公募 REIT 路线严格研究测试准备度": "monitoring",
        "C23 境内公募开放式基金数据与纸面测试可行性": "monitoring",
        "C24 境内直接股票数据与纸面研究可行性": "monitoring",
        "C34 五 ETF 双期限逆波动纸面候选": "monitoring",
        "C38 provisional direct-equity institutional research queue": "monitoring",
        "C39 audited cash-flow realization cohort hypothesis": "monitoring",
        "C46 five-family SHFE calendar-curve actual-contract diagnostic": "closed",
        "C50 SSE general-repo yield-floor screen": "closed",
        "C51 SSE ETF-collar option non-duplication and data-contract screen": "monitoring",
        "C53 权益主导五 ETF 季度纸面协议草案": "monitoring",
    }
    ledger_entries = {
        str(item.get("title")): item
        for item in ledger.get("entries", [])
        if isinstance(item, dict)
    }
    ledger_failures: list[str] = []
    for title, expected_status in required_ledger.items():
        entry = ledger_entries.get(title)
        if not entry:
            ledger_failures.append(f"missing {title}")
            continue
        metadata = entry.get("metadata", {}) if isinstance(entry.get("metadata"), dict) else {}
        if entry.get("status") != expected_status:
            ledger_failures.append(f"{title}: status")
        if metadata.get("external_orders") is not False or metadata.get("portfolio_q") != 0:
            ledger_failures.append(f"{title}: action boundary")
    check("C16/C17/C18/C20/C23/C24/C34/C38/C39/C46/C50/C51/C53 ledger lifecycle and action boundary", not ledger_failures, "; ".join(ledger_failures) or "all matched")

    r07_controls = r07.get("source_control", {}) if isinstance(r07.get("source_control"), dict) else {}
    r07_failures: list[str] = []
    for name, control in r07_controls.items():
        if not isinstance(control, dict):
            r07_failures.append(f"{name}: invalid control")
            continue
        path = CASE_DIR / str(control.get("path") or "")
        expected_hash = str(control.get("sha256") or "")
        if not path.is_file() or not expected_hash or sha256(path) != expected_hash:
            r07_failures.append(f"{name}: source control mismatch")
    check("R07 source controls", not r07_failures, "; ".join(r07_failures) or "all matched")
    decision = r07.get("current_decision", {}) if isinstance(r07.get("current_decision"), dict) else {}
    check("R07 no-admission decision", decision.get("state") == "NO_ADMITTED_USABLE_STRATEGY", str(decision.get("state")))
    check(
        "R07 action boundary",
        r07.get("research_only") is True and r07.get("formal_decision_eligible") is False and r07.get("external_orders") is False and r07.get("portfolio_q") == 0,
        "research_only/formal_decision_eligible/external_orders/portfolio_q",
    )

    r14 = load_json(R14)
    check("R14 open-universe feasibility boundary audit", r14.get("result") == "PASS", str(r14.get("result")))

    governance_pairs = (
        ("source_exhaustion_log", CASE_DIR / "source_exhaustion_log.json", CASE_DIR / "source_exhaustion_log.md"),
        ("missing_data_request_pack", CASE_DIR / "missing_data_request_pack.json", CASE_DIR / "missing_data_request_pack.md"),
        ("unresolved_requirements", CASE_DIR / "unresolved_requirements.json", None),
    )
    governance_failures: list[str] = []
    for name, json_path, markdown_path in governance_pairs:
        if not json_path.is_file():
            governance_failures.append(f"missing {name}.json")
        if markdown_path is not None and not markdown_path.is_file():
            governance_failures.append(f"missing {name}.md")
    check("research-blocker governance artifacts", not governance_failures, "; ".join(governance_failures) or "all present")
    source_exhaustion = load_json(CASE_DIR / "source_exhaustion_log.json")
    request_pack = load_json(CASE_DIR / "missing_data_request_pack.json")
    unresolved = load_json(CASE_DIR / "unresolved_requirements.json")
    contract = load_json(ARTIFACT_CONTRACT)
    gate_manifest = load_json(GATE_MANIFEST)
    check("source exhaustion retains open blockers", source_exhaustion.get("status") == "open_research_blockers_preserved_no_strategy_admitted", str(source_exhaustion.get("status")))
    check("request pack does not authorize acquisition", request_pack.get("status") == "external_data_or_rights_required_before_any_strategy_test", str(request_pack.get("status")))
    check("unresolved requirements retain no-admission blocker", unresolved.get("status") == "research_building_no_strategy_admitted", str(unresolved.get("status")))
    check("artifact contract remains non-release", contract.get("release_status") == "not_publish_bound", str(contract.get("release_status")))

    c37 = load_json(C37)
    c38 = load_json(C38)
    c39 = load_json(C39)
    c40 = load_json(C40)
    c41 = load_json(C41)
    c42 = load_json(C42)
    c43 = load_json(C43)
    c44 = load_json(C44)
    c45 = load_json(C45)
    c46 = load_json(C46)
    c47 = load_json(C47)
    c48 = load_json(C48)
    c49 = load_json(C49)
    c50 = load_json(C50)
    c51 = load_json(C51)
    c52 = load_json(C52)
    c53 = load_json(C53)
    c53_ledger_template = load_json(C53_LEDGER_TEMPLATE)
    r16_repair_plan = load_json(R16_REPAIR_PLAN)
    r17_recheck = load_json(R17_RECHECK)
    r18_c49_audit = load_json(R18_C49_AUDIT)
    r19_c50_audit = load_json(R19_C50_AUDIT)
    r20_c51_initial_audit = load_json(R20_C51_INITIAL_AUDIT)
    r20_c51_repair_plan = load_json(R20_C51_REPAIR_PLAN)
    r21_c51_recheck = load_json(R21_C51_RECHECK)
    r22_c52_audit = load_json(R22_C52_AUDIT)
    r23_c52_governance_recheck = load_json(R23_C52_GOVERNANCE_RECHECK)
    c37_decision = c37.get("decision", {}) if isinstance(c37.get("decision"), dict) else {}
    c37_ledger = c37_decision.get("historical_etf_investor_total_return_event_ledger", {})
    c37_gates = c37.get("hard_gates", [])
    c37_gate_statuses = [str(item.get("status")) for item in c37_gates if isinstance(item, dict)]
    check(
        "C37 public-primary historical-test no-go boundary",
        c37.get("research_only") is True
        and c37.get("external_orders") is False
        and c37.get("no_product_selection") is True
        and c37.get("no_index_selection") is True
        and c37.get("no_return_calculation_run") is True
        and isinstance(c37_ledger, dict)
        and c37_ledger.get("status") == "NO_GO_PUBLIC_PRIMARY_HISTORICAL_TEST"
        and len(c37_gate_statuses) == 8
        and all(status != "closed" for status in c37_gate_statuses),
        f"ledger={c37_ledger.get('status') if isinstance(c37_ledger, dict) else None}; gates={c37_gate_statuses}",
    )
    c38_subjects = c38.get("candidate_subjects", [])
    c38_subject_statuses = [str(item.get("candidate_status")) for item in c38_subjects if isinstance(item, dict)]
    c38_decision = c38.get("decision", {}) if isinstance(c38.get("decision"), dict) else {}
    check(
        "C38 direct-equity queue non-admission boundary",
        c38.get("status") == "CONDITIONAL_RESEARCH_QUEUE_ONLY_NOT_ADMITTED"
        and c38.get("research_only") is True
        and c38.get("external_orders") is False
        and c38.get("portfolio_q") == 0
        and len(c38_subject_statuses) == 3
        and set(c38_subject_statuses) == {"NON_ADMITTED_RESEARCH_SUBJECT"}
        and c38_decision.get("historical_test_or_strategy_admission") == "NO_ACTION",
        f"status={c38.get('status')}; subjects={c38_subject_statuses}; admission={c38_decision.get('historical_test_or_strategy_admission')}",
    )
    c39_splits = [str(item.get("id")) for item in c39.get("test_splits", []) if isinstance(item, dict)]
    c39_disposition = c39.get("current_disposition", {}) if isinstance(c39.get("current_disposition"), dict) else {}
    check(
        "C39 preregistered no-action protocol boundary",
        c39.get("status") == "NO_ACTION"
        and c39.get("risk_model_status") == "VETO"
        and c39.get("research_only") is True
        and c39.get("external_orders") is False
        and c39.get("live_product_selection") is False
        and c39.get("actionable_weights_or_notionals") is False
        and c39.get("performance_stated") is False
        and c39_splits == ["P0", "P1", "P2", "P3", "P4", "F1"]
        and c39_disposition.get("status") == "NO_ACTION",
        f"status={c39.get('status')}; risk={c39.get('risk_model_status')}; splits={c39_splits}",
    )
    c53_expected_weights = {
        "510300": 0.25,
        "510880": 0.25,
        "511010": 0.25,
        "518880": 0.10,
        "511990": 0.15,
    }
    c53_rule = c53.get("operating_rule", {}) if isinstance(c53.get("operating_rule"), dict) else {}
    c53_controls = c53.get("risk_controls", {}) if isinstance(c53.get("risk_controls"), dict) else {}
    c53_decision = c53.get("decision", {}) if isinstance(c53.get("decision"), dict) else {}
    c53_forward_ledger = c53.get("forward_paper_ledger", {}) if isinstance(c53.get("forward_paper_ledger"), dict) else {}
    c53_ledger_binding = c53_ledger_template.get("rule_binding", {}) if isinstance(c53_ledger_template.get("rule_binding"), dict) else {}
    c53_ledger_rules = c53_ledger_template.get("rules", {}) if isinstance(c53_ledger_template.get("rules"), dict) else {}
    check(
        "C53 equity-led draft protocol remains non-admitted and fail-closed",
        c53.get("schema_version") == "d5pt_c53_equity_led_paper_protocol.v1"
        and c53.get("artifact_id") == "D5PT-C53-EQUITY-LED-PAPER-PROTOCOL-v1"
        and c53.get("status") == "DRAFT_PAPER_PROTOCOL_NOT_ADMITTED"
        and c53.get("research_only") is True
        and c53.get("formal_decision_eligible") is False
        and c53.get("external_orders") is False
        and c53.get("portfolio_q") == 0
        and c53.get("target_weights") == c53_expected_weights
        and c53_rule.get("rebalance_trigger") == "At least one absolute actual-weight deviation is strictly greater than 5 percentage points."
        and c53_rule.get("hard_failure_action") == "NO_ACTION or operational_pause; no substitution, assumed fill, same-day close fill or invented exit price."
        and c53_controls.get("amber_drawdown") == -0.12
        and c53_controls.get("red_drawdown") == -0.18
        and c53_decision.get("state") == "PAPER_PROTOCOL_DRAFT_ONLY"
        and c53_decision.get("action") == "NO_ACTION",
        f"status={c53.get('status')}; weights={c53.get('target_weights')}; action={c53_decision.get('action')}",
    )
    c53_ledger_instrument_fields = set(c53_ledger_template.get("instrument_required_fields", []))
    c53_ledger_cycle_fields = set(c53_ledger_template.get("cycle_required_fields", []))
    c53_ledger_csv_header = C53_LEDGER_CSV.read_text(encoding="utf-8").splitlines()[0] if C53_LEDGER_CSV.is_file() else ""
    check(
        "C53 bound quarterly ledger is reconstructible and empty",
        c53_forward_ledger.get("path") == "data/c53_quarterly_paper_observation_ledger_template_20260815.json"
        and c53_forward_ledger.get("status") == "template_only_no_observations"
        and c53_forward_ledger.get("minimum_complete_cycles") == 6
        and c53_ledger_template.get("schema_version") == "c53_quarterly_paper_observation_ledger.v1"
        and c53_ledger_template.get("artifact_id") == "D5PT-C53-QUARTERLY-PAPER-LEDGER-TEMPLATE-v1"
        and c53_ledger_template.get("status") == "template_only_no_observations"
        and c53_ledger_template.get("research_only") is True
        and c53_ledger_template.get("external_orders") is False
        and c53_ledger_binding.get("protocol_artifact_id") == c53.get("artifact_id")
        and c53_ledger_binding.get("protocol_path") == "analysis/c53_equity_led_domestic_target_strategy_protocol_20260815.json"
        and c53_ledger_binding.get("target_weights") == c53_expected_weights
        and c53_ledger_binding.get("rebalance_band_absolute_percentage_points") == 5
        and c53_ledger_binding.get("buy_protection") == c53_rule.get("price_protection", {}).get("buy")
        and c53_ledger_binding.get("sell_protection") == c53_rule.get("price_protection", {}).get("sell")
        and {"normalized_paper_unit_index", "portfolio_valuation_timestamp"} <= c53_ledger_cycle_fields
        and {"paper_units_before", "valuation_timestamp", "valuation_price", "position_mark_reference", "actual_weight_before", "weight_deviation_percentage_points"} <= c53_ledger_instrument_fields
        and c53_ledger_rules.get("actual_weight_reconstruction") == "paper_units_before times valuation_price at a common valuation timestamp, divided by the aggregate recorded paper-unit value"
        and c53_ledger_rules.get("equity_pair_must_pass_atomically") is True
        and c53_ledger_rules.get("no_product_substitution") is True
        and c53_ledger_rules.get("no_assumed_fill") is True
        and c53_ledger_rules.get("no_external_order") is True
        and c53_ledger_template.get("observations") == []
        and c53_ledger_csv_header.startswith("cycle_id,observation_date,observation_close_timestamp,effective_session,code,target_weight,paper_units_before,valuation_timestamp,valuation_price,position_mark_reference,actual_weight_before"),
        f"template={c53_ledger_template.get('status')}; observations={len(c53_ledger_template.get('observations', []))}; csv_header={c53_ledger_csv_header}",
    )
    c43_invalidation = c43.get("invalidation", {}) if isinstance(c43.get("invalidation"), dict) else {}
    check(
        "C43/C44 source-control invalidation boundary",
        c43.get("status") == "INVALIDATED_PRECALCULATION_SOURCE_CONTROL_GAP"
        and c44.get("status") == "VOID_PRECALCULATION_SOURCE_CONTROL_GAP"
        and c43.get("research_only") is True
        and c43.get("formal_decision_eligible") is False
        and c44.get("research_only") is True
        and c44.get("external_orders") is False
        and c44.get("portfolio_q") == 0
        and c43_invalidation.get("original_preliminary_output_sha256") == c44.get("original_preliminary_output_sha256")
        and "final_unit_value" not in c44,
        f"C43={c43.get('status')}; C44={c44.get('status')}",
    )
    c45_family_stats = c45.get("family_stats", {}) if isinstance(c45.get("family_stats"), dict) else {}
    c45_complete = all(
        isinstance(c45_family_stats.get(family), dict)
        and c45_family_stats[family].get("response_count_with_valid_actual_contract_row") == 1699
        for family in ("AU", "CU", "RB", "RU", "SP")
    )
    check(
        "C45 five-family limited source-field readiness",
        c45.get("result") == "PASS"
        and c45.get("research_only") is True
        and c45.get("formal_decision_eligible") is False
        and c45.get("external_orders") is False
        and c45.get("source", {}).get("retained_response_count") == 1699
        and c45_complete,
        f"result={c45.get('result')}; families={sorted(c45_family_stats)}",
    )
    c46_amendment = c46.get("source_control_amendment", {}) if isinstance(c46.get("source_control_amendment"), dict) else {}
    c46_unchanged_rule = all(
        c43.get(field) == c46.get(field)
        for field in ("universe", "monthly_pair_signal", "unitized_gross_settlement_mark", "evaluation", "prohibitions")
    )
    check(
        "C46 frozen source-control binding",
        c46.get("status") == "FROZEN_BEFORE_CALCULATION"
        and c46.get("research_only") is True
        and c46.get("formal_decision_eligible") is False
        and c46.get("external_orders") is False
        and c46_amendment.get("source_readiness_sha256") == sha256(C45)
        and c46_amendment.get("source_readiness_result") == "PASS"
        and c46.get("source_dependency", {}).get("source_readiness_audit_sha256") == sha256(C45)
        and c46_unchanged_rule,
        f"status={c46.get('status')}; C45 binding={c46_amendment.get('source_readiness_sha256')}",
    )
    c47_preflight = c47.get("source_control_preflight", {}) if isinstance(c47.get("source_control_preflight"), dict) else {}
    incomplete_signal = c47.get("incomplete_signal", {}) if isinstance(c47.get("incomplete_signal"), dict) else {}
    incomplete_families = incomplete_signal.get("families", {}) if isinstance(incomplete_signal.get("families"), dict) else {}
    check(
        "C47 source-controlled frozen-pair stop and no-result boundary",
        c47.get("status") == "NOT_DECIDABLE_INCOMPLETE_MONTHLY_PAIR"
        and c47.get("research_only") is True
        and c47.get("formal_decision_eligible") is False
        and c47.get("external_orders") is False
        and c47.get("portfolio_q") == 0
        and c47_preflight.get("C45_sha256") == sha256(C45)
        and c47_preflight.get("C46_sha256") == sha256(C46)
        and incomplete_signal.get("signal_date") == "2024-06-28"
        and incomplete_families.get("CU", {}).get("status") == "no_eligible_pair"
        and incomplete_families.get("RU", {}).get("status") == "no_eligible_pair"
        and incomplete_families.get("SP", {}).get("status") == "no_eligible_pair"
        and "final_unit_value" not in c47,
        f"status={c47.get('status')}; stop={incomplete_signal.get('signal_date')}",
    )
    c48_decision = c48.get("decision", {}) if isinstance(c48.get("decision"), dict) else {}
    c48_environment = c48.get("environment_findings", {}) if isinstance(c48.get("environment_findings"), dict) else {}
    check(
        "C48 current-environment formal-data boundary",
        c48.get("status") == "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT"
        and c48.get("research_only") is True
        and c48.get("formal_decision_eligible") is False
        and c48.get("external_orders") is False
        and c48.get("portfolio_q") == 0
        and c48_environment.get("configured_market_data_mode") == "public_observation"
        and c48_environment.get("licensed_provider_credentials_or_attestation_present") is False
        and c48_decision.get("state") == "NO_FORMAL_STRATEGY_TEST_OR_ADMISSION"
        and c48_decision.get("action") == "NO_ACTION",
        f"status={c48.get('status')}; mode={c48_environment.get('configured_market_data_mode')}",
    )
    c49_source_control = c49.get("source_control", {}) if isinstance(c49.get("source_control"), dict) else {}
    c49_manifest = c49_source_control.get("retained_primary_manifest", {}) if isinstance(c49_source_control.get("retained_primary_manifest"), dict) else {}
    c49_prior = c49_source_control.get("prior_current_environment_audit", {}) if isinstance(c49_source_control.get("prior_current_environment_audit"), dict) else {}
    c49_manifest_path = resolve(str(c49_manifest.get("path") or ""))
    c49_archive_failures: list[str] = []
    if not c49_manifest_path.is_file():
        c49_archive_failures.append("missing manifest")
    else:
        c49_source_manifest = load_json(c49_manifest_path)
        c49_files = c49_source_manifest.get("files", [])
        c49_non_records = c49_source_manifest.get("non_records", [])
        if c49_source_manifest.get("capture_batch") != "c49-official-authorized-data-route-20260815":
            c49_archive_failures.append("capture batch")
        if not isinstance(c49_files, list) or len(c49_files) != 3:
            c49_archive_failures.append("retained file count")
        else:
            for file_record in c49_files:
                if not isinstance(file_record, dict):
                    c49_archive_failures.append("invalid file record")
                    break
                file_path = resolve(str(file_record.get("path") or ""))
                expected_file_hash = str(file_record.get("sha256") or "")
                if not file_path.is_file() or not expected_file_hash or sha256(file_path) != expected_file_hash:
                    c49_archive_failures.append(f"source integrity {file_record.get('source_key')}")
                    break
        if not isinstance(c49_non_records, list) or len(c49_non_records) != 2 or any(
            not isinstance(item, dict) or item.get("status") != "not_retained_connection_error" for item in c49_non_records
        ):
            c49_archive_failures.append("CFFEX locator treatment")
    check("C49 retained-source archive integrity", not c49_archive_failures, "; ".join(c49_archive_failures) or "all matched")
    c49_decision = c49.get("decision", {}) if isinstance(c49.get("decision"), dict) else {}
    c49_gate_recheck = c49.get("current_gate_recheck", {}) if isinstance(c49.get("current_gate_recheck"), dict) else {}
    check(
        "C49 official authorized-route boundary",
        c49.get("status") == "CONDITIONAL_AUTHORIZED_DATA_ROUTE_DISCOVERY_NO_CURRENT_ACCEPTED_DELIVERY"
        and c49.get("research_only") is True
        and c49.get("formal_decision_eligible") is False
        and c49.get("external_orders") is False
        and c49.get("portfolio_q") == 0
        and c49_manifest_path.is_file()
        and c49_manifest.get("sha256") == sha256(c49_manifest_path)
        and not c49_archive_failures
        and c49_prior.get("sha256") == sha256(C48)
        and c49_gate_recheck.get("C48_status") == "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT"
        and c49_decision.get("state") == "NO_FORMAL_STRATEGY_TEST_OR_ADMISSION"
        and c49_decision.get("action") == "NO_ACTION",
        f"status={c49.get('status')}; C48={c49_gate_recheck.get('C48_status')}",
    )
    c50_source_control = c50.get("source_control", {}) if isinstance(c50.get("source_control"), dict) else {}
    c50_manifest_path = resolve(str(c50_source_control.get("manifest") or ""))
    c50_source_failures: list[str] = []
    expected_c50_ids = {"C50-S01", "C50-S02", "C50-S03", "C50-S04", "C50-S05"}
    if not c50_manifest_path.is_file():
        c50_source_failures.append("missing source manifest")
    else:
        c50_manifest = load_json(c50_manifest_path)
        c50_entries = c50_manifest.get("entries", [])
        c50_by_id = {
            str(item.get("source_id")): item
            for item in c50_entries
            if isinstance(item, dict)
        }
        if set(c50_by_id) != expected_c50_ids:
            c50_source_failures.append("source ID coverage")
        else:
            for source_id, item in c50_by_id.items():
                path = c50_manifest_path.parent / str(item.get("filename") or "")
                expected_hash = str(item.get("sha256") or "")
                if not path.is_file() or not expected_hash or sha256(path) != expected_hash:
                    c50_source_failures.append(f"source integrity {source_id}")
                    break
        if c50_manifest.get("artifact_id") != "D5PT-C50-SOURCES-v1":
            c50_source_failures.append("manifest identity")
    c50_observation = c50.get("dated_official_observation", {}) if isinstance(c50.get("dated_official_observation"), dict) else {}
    c50_screen = c50.get("strict_hurdle_screen", {}) if isinstance(c50.get("strict_hurdle_screen"), dict) else {}
    c50_decision = c50.get("decision", {}) if isinstance(c50.get("decision"), dict) else {}
    c50_relation = c50.get("relationship_to_c48", {}) if isinstance(c50.get("relationship_to_c48"), dict) else {}
    check(
        "C50 primary-source yield-floor and non-admission boundary",
        c50.get("status") == "NOT_ADMITTED_NO_STABLE_5PCT_YIELD_FLOOR"
        and c50.get("research_only") is True
        and c50.get("formal_decision_eligible") is False
        and c50.get("external_orders") is False
        and c50.get("portfolio_q") == 0
        and c50_manifest_path.is_file()
        and not c50_source_failures
        and set(c50_source_control.get("source_ids", [])) == expected_c50_ids
        and c50_observation.get("source_date") == "2026-08-14"
        and c50_observation.get("quoted_annualized_rate_pct") == 1.391
        and c50_observation.get("same_response_rate_7day_pct") == 1.414
        and c50_screen.get("current_official_one_day_quote_below_5pct") is True
        and c50_screen.get("current_official_same_response_rate_7day_below_5pct") is True
        and c50_screen.get("contractual_or_rule_based_5pct_floor_evidenced") is False
        and c50_screen.get("historical_full_year_or_rolling_five_year_test_performed") is False
        and c50_screen.get("admission_result") == "fail"
        and c50_relation.get("c48_status") == "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT"
        and c50_decision.get("action") == "NO_ACTION",
        f"status={c50.get('status')}; C50 source failures={c50_source_failures}",
    )
    c51_source_control = c51.get("source_control", {}) if isinstance(c51.get("source_control"), dict) else {}
    c51_manifest_path = resolve(str(c51_source_control.get("manifest") or ""))
    expected_c51_sources = {
        "C51-S01": {
            "filename": "sse_option_investor_suitability_page.html",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781453.shtml",
            "sha256": "e79cda6747d18ae145fbb2de8e6dd0bbc909969c2af4717976d7a6644c53a5c0",
        },
        "C51-S02": {
            "filename": "sse_option_investor_suitability_guideline.docx",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/10781453/files/733e45a7625f460facc66cff7ddcfc8b.docx",
            "sha256": "81992a8ec243c6829fbc43f194836d05277905cda551dbaccab961e4447a28a0",
        },
        "C51-S03": {
            "filename": "sse_stock_option_trading_rule_page.html",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/c_20250610_10781448.shtml",
            "sha256": "ddafdc569fe845cfb5e612e07006288629680433d9dd72bdb4e5ff5a2956b540",
        },
        "C51-S04": {
            "filename": "sse_stock_option_trading_rule.docx",
            "url": "https://www.sse.com.cn/lawandrules/sselawsrules2025/option/c/10781448/files/0c0f89e74e9c4a5b9aa3a7acafdf5119.docx",
            "sha256": "fff3aaeb338da5d1e1a5892ab7601d79393dd33659b01cb0595b214e2df4a8a9",
        },
        "C51-S05": {
            "filename": "sse_market_data_file_exchange_specification.pdf",
            "url": "https://www.sse.com.cn/services/tradingtech/development/c/10810429/files/ca36291a287242698ad505bce1a7efcc.pdf",
            "sha256": "233d98bdc1faf26cd3940495bac37f6603b6b328e049a2e81244efc394a154c2",
        },
    }
    c51_source_failures: list[str] = []
    if not c51_manifest_path.is_file():
        c51_source_failures.append("missing source manifest")
    else:
        c51_manifest = load_json(c51_manifest_path)
        c51_entries = c51_manifest.get("entries", [])
        c51_by_id = {
            str(item.get("source_id")): item
            for item in c51_entries
            if isinstance(item, dict)
        }
        if c51_manifest.get("artifact_id") != "D5PT-C51-SOURCES-v1":
            c51_source_failures.append("manifest identity")
        if sha256(c51_manifest_path) != "993e481ff1f04a03e1f1e02c2ed1253dd64f5a31e32a15c2df4cebd8c2934914":
            c51_source_failures.append("manifest digest")
        if set(c51_by_id) != set(expected_c51_sources):
            c51_source_failures.append("source ID coverage")
        else:
            for source_id, expected in expected_c51_sources.items():
                item = c51_by_id[source_id]
                if any(item.get(field) != value for field, value in expected.items()):
                    c51_source_failures.append(f"manifest fields {source_id}")
                    break
                path = c51_manifest_path.parent / expected["filename"]
                if not path.is_file() or sha256(path) != expected["sha256"]:
                    c51_source_failures.append(f"source integrity {source_id}")
                    break
    c51_payoff = c51.get("payoff_boundary", {}) if isinstance(c51.get("payoff_boundary"), dict) else {}
    c51_screen = c51.get("strict_hurdle_screen", {}) if isinstance(c51.get("strict_hurdle_screen"), dict) else {}
    c51_relation = c51.get("relationship_to_c48", {}) if isinstance(c51.get("relationship_to_c48"), dict) else {}
    c51_decision = c51.get("decision", {}) if isinstance(c51.get("decision"), dict) else {}
    c51_taxonomy = c51.get("taxonomy", {}) if isinstance(c51.get("taxonomy"), dict) else {}
    c51_c13 = c51_source_control.get("predecessor_c13", {}) if isinstance(c51_source_control.get("predecessor_c13"), dict) else {}
    c51_c13_path = resolve(str(c51_c13.get("path") or ""))
    c51_c13_valid = False
    if c51_c13_path.is_file() and sha256(c51_c13_path) == "f2859c71d8cbd57eeb6eee211a1e3700c7d16e3694ed3127ce12c07931ada434":
        c51_c13_data = load_json(c51_c13_path)
        c51_c13_valid = (
            c51_c13.get("sha256") == sha256(c51_c13_path)
            and c51_c13.get("status") == "RESEARCH_CANDIDATE_NOT_ACTION_READY"
            and c51_c13.get("strict_5pct_test_status") == "NOT_FEASIBLE_FOR_RETURN_CLAIM"
            and c51_c13_data.get("status") == "RESEARCH_CANDIDATE_NOT_ACTION_READY"
            and c51_c13_data.get("strict_5pct_test", {}).get("status") == "NOT_FEASIBLE_FOR_RETURN_CLAIM"
        )
    check(
        "C51 distinct collar source, formula and non-admission boundary",
        c51.get("status") == "NOT_ADMITTED_OPTIONS_FAMILY_NO_NEW_USABLE_ROUTE"
        and c51.get("research_only") is True
        and c51.get("formal_decision_eligible") is False
        and c51.get("external_orders") is False
        and c51.get("portfolio_q") == 0
        and c51_manifest_path.is_file()
        and not c51_source_failures
        and c51_source_control.get("manifest_sha256") == sha256(c51_manifest_path)
        and c51_source_control.get("source_hashes") == {source_id: expected["sha256"] for source_id, expected in expected_c51_sources.items()}
        and c51_c13_valid
        and c51_taxonomy.get("existing_covered_call_C13", {}).get("current_disposition") == "RETAIN_CLOSED_NOT_TESTABLE_FOR_RETURN_CLAIM"
        and c51_payoff.get("collar_terminal_value") == "min(S_T, K_C) + max(K_P - S_T, 0) + C - P"
        and c51_payoff.get("collar_compact_terminal_value_only_when_K_P_le_K_C") == "max(K_P, min(S_T, K_C)) + C - P"
        and c51_payoff.get("formula_provenance") == "Generic derivative payoff algebra only; it is not an SSE rule, market-data-interface or exchange formula."
        and "K_P <= K_C" in str(c51_payoff.get("interpretation"))
        and c51_screen.get("contractual_or_rule_based_positive_five_percent_floor_evidenced") is False
        and c51_screen.get("historical_full_year_or_rolling_five_year_test_performed") is False
        and c51_screen.get("pre_frozen_contract_selection_and_roll_rule_present") is False
        and c51_screen.get("admission_result") == "fail"
        and c51_relation.get("c48_status") == "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT"
        and c51_decision.get("action") == "NO_ACTION",
        f"status={c51.get('status')}; source failures={c51_source_failures}; predecessor={c51_c13_valid}",
    )

    c52_source_control = c52.get("source_control", {}) if isinstance(c52.get("source_control"), dict) else {}
    c52_manifest_path = resolve(str(c52_source_control.get("manifest") or ""))
    expected_c52_sources = {
        "C52-S01": {
            "filename": "sse_option_daily_contract_page.html",
            "url": "https://www.sse.com.cn/assortment/options/disclo/preinfo/",
            "byte_count": 27119,
            "sha256": "174776f4d6a0c205565d540b747fca6058a9717753588cd35564eb799c7072e1",
        },
        "C52-S02": {
            "filename": "sse_option_listing_adjustment_page.html",
            "url": "https://www.sse.com.cn/assortment/options/disclo/info/",
            "byte_count": 28397,
            "sha256": "e8d9755ee343ab44724ecfa95a681216a8f564b6e1c2b20a3d369b0a604912cb",
        },
        "C52-S03": {
            "filename": "sse_option_market_price_page.html",
            "url": "https://www.sse.com.cn/assortment/options/price/",
            "byte_count": 27349,
            "sha256": "5b7f88565d943aa1503811b774b98e9d82815e67dc0be0f79669e2fe1b04091e",
        },
        "C52-S04": {
            "filename": "sse_option_information_query_script.js",
            "url": "https://www.sse.com.cn/xhtml/home/2021public/querySearch/search_stockOptionInformation_2021.js",
            "byte_count": 48079,
            "sha256": "d3fe735a30cad061375ce03441522dcbe48b32a899b67b09fee08412a6452eb7",
        },
        "C52-S05": {
            "filename": "sse_20161128_50etf_dividend_option_adjustment_notice.html",
            "url": "https://www.sse.com.cn/assortment/options/guide/c/c_20161128_4207559.shtml",
            "byte_count": 33470,
            "sha256": "a968a1a9a30897a5a1e7c796d3e8a3357c672f694004cd1a047bc88668a1e38d",
        },
        "C52-S06": {
            "filename": "sseinfo_historical_data_product_page.html",
            "url": "https://www.sseinfo.com/services/assortment/historical/",
            "byte_count": 23029,
            "sha256": "dbae0135ca890931f4161f0b9c239029096dddb55015738f0c988fd92005a85f",
        },
    }
    expected_c52_dependencies = {
        "c48": {
            "path": "workspace/research/domestic-5pct-target-paper-strategy-20260815/analysis/c48_current_environment_data_capability_audit_20260815.json",
            "sha256": "dd61020103246458545b3bf1367115529c9285c4a80c07c853f3a3706731f4ce",
            "status": "NO_FORMAL_HISTORICAL_ROUTE_AVAILABLE_IN_CURRENT_ENVIRONMENT",
        },
        "c49": {
            "path": "workspace/research/domestic-5pct-target-paper-strategy-20260815/analysis/c49_official_authorized_data_route_recheck_20260815.json",
            "sha256": "990a20b9ab5a8d855656b3e642848d55f17b4394f28c07568cdbedfc9f5317b3",
            "status": "CONDITIONAL_AUTHORIZED_DATA_ROUTE_DISCOVERY_NO_CURRENT_ACCEPTED_DELIVERY",
        },
        "c51": {
            "path": "workspace/research/domestic-5pct-target-paper-strategy-20260815/analysis/c51_sse_etf_option_collar_scope_screen_20260815.json",
            "sha256": "114d4ee9795ba94f50a23b3aecd321fe15b8ebdc2decacfb6dc5d1023ff86f1c",
            "status": "NOT_ADMITTED_OPTIONS_FAMILY_NO_NEW_USABLE_ROUTE",
        },
    }
    c52_source_failures: list[str] = []
    c52_manifest: dict[str, Any] = {}
    if not c52_manifest_path.is_file():
        c52_source_failures.append("missing source manifest")
    else:
        c52_manifest = load_json(c52_manifest_path)
        c52_entries = c52_manifest.get("entries", [])
        c52_by_id = {
            str(item.get("source_id")): item
            for item in c52_entries
            if isinstance(item, dict)
        }
        if c52_manifest.get("artifact_id") != "D5PT-C52-SOURCES-v1":
            c52_source_failures.append("manifest identity")
        if c52_manifest.get("retrieved_at_utc") != "2026-08-15T06:41:33+00:00":
            c52_source_failures.append("manifest retrieval timestamp")
        if sha256(c52_manifest_path) != "92fdb7356454e21c203ea88baf6d3a7fee1d03e7fde576901d2e1ccc50de0c76":
            c52_source_failures.append("manifest digest")
        if set(c52_by_id) != set(expected_c52_sources):
            c52_source_failures.append("source ID coverage")
        else:
            for source_id, expected in expected_c52_sources.items():
                item = c52_by_id[source_id]
                if any(item.get(field) != value for field, value in expected.items()):
                    c52_source_failures.append(f"manifest fields {source_id}")
                    break
                path = c52_manifest_path.parent / expected["filename"]
                if not path.is_file() or path.stat().st_size != expected["byte_count"] or sha256(path) != expected["sha256"]:
                    c52_source_failures.append(f"source integrity {source_id}")
                    break
    c52_dependencies = c52_source_control.get("dependencies", {}) if isinstance(c52_source_control.get("dependencies"), dict) else {}
    c52_dependency_failures: list[str] = []
    if set(c52_dependencies) != set(expected_c52_dependencies):
        c52_dependency_failures.append("dependency coverage")
    else:
        for dependency_id, expected in expected_c52_dependencies.items():
            dependency = c52_dependencies.get(dependency_id, {})
            if not isinstance(dependency, dict) or any(dependency.get(field) != value for field, value in expected.items()):
                c52_dependency_failures.append(f"dependency fields {dependency_id}")
                continue
            path = resolve(expected["path"])
            if not path.is_file() or sha256(path) != expected["sha256"] or load_json(path).get("status") != expected["status"]:
                c52_dependency_failures.append(f"dependency integrity {dependency_id}")
    c52_findings = c52.get("public_source_findings", {}) if isinstance(c52.get("public_source_findings"), dict) else {}
    c52_daily = c52_findings.get("daily_contract_display", {}) if isinstance(c52_findings.get("daily_contract_display"), dict) else {}
    c52_coverage = c52.get("coverage_matrix", [])
    c52_required_components = [
        "Point-in-time actual option contract master",
        "Historical option close/settlement and decision-time bid/ask/depth panel",
        "ETF distribution, option-adjustment and lifecycle mapping",
        "Historical data rights, available-at/version chain and independent replay rights",
        "Broker/account eligibility, order state, fills, fees, settlement and cash movements",
    ]
    c52_coverage_components = [str(item.get("required_component")) for item in c52_coverage if isinstance(item, dict)]
    c52_relationship = c52.get("relationship_to_existing_controls", {}) if isinstance(c52.get("relationship_to_existing_controls"), dict) else {}
    c52_screen = c52.get("strict_hurdle_boundary", {}) if isinstance(c52.get("strict_hurdle_boundary"), dict) else {}
    c52_decision = c52.get("decision", {}) if isinstance(c52.get("decision"), dict) else {}
    check(
        "C52 public-source archive, historical-data boundary and no-action controls",
        c52.get("status") == "PUBLIC_SSE_OPTION_SOURCE_ROUTE_INSUFFICIENT_FOR_C51_REPLAY"
        and c52.get("research_only") is True
        and c52.get("formal_decision_eligible") is False
        and c52.get("external_orders") is False
        and c52.get("portfolio_q") == 0
        and c52_manifest_path.is_file()
        and not c52_source_failures
        and c52_source_control.get("manifest_sha256") == sha256(c52_manifest_path)
        and c52_source_control.get("source_ids") == list(expected_c52_sources)
        and c52_source_control.get("source_hashes") == {source_id: expected["sha256"] for source_id, expected in expected_c52_sources.items()}
        and not c52_dependency_failures
        and len(c52_coverage) == len(c52_required_components)
        and c52_coverage_components == c52_required_components
        and all(isinstance(item, dict) and item.get("formal_gate_closed") is False for item in c52_coverage)
        and c52_daily.get("captured_query_parameters") == ["expireDate", "securityId", "pagination"]
        and c52_daily.get("historical_as_of_parameter_in_captured_daily_query") is False
        and "does not claim that no other SSE route could exist" in str(c52_daily.get("bounded_interpretation"))
        and c52_relationship.get("c48_status") == expected_c52_dependencies["c48"]["status"]
        and c52_relationship.get("c49_status") == expected_c52_dependencies["c49"]["status"]
        and c52_relationship.get("c51_status") == expected_c52_dependencies["c51"]["status"]
        and "does not close C48" in str(c52_relationship.get("effect"))
        and c52_screen.get("contractual_or_rule_based_positive_five_percent_floor_evidenced") is False
        and c52_screen.get("historical_net_total_return_test_performed") is False
        and c52_decision.get("state") == "NO_PUBLIC_REPLAY_OR_ADMISSION_PATH"
        and c52_decision.get("action") == "NO_ACTION",
        f"status={c52.get('status')}; source failures={c52_source_failures}; dependency failures={c52_dependency_failures}",
    )
    c52_registry_records = {
        str(record.get("source_id")): record
        for record in records
        if isinstance(record, dict) and str(record.get("source_id")) in {"S61", "S62"}
    }
    c52_claim_records = {
        str(claim.get("claim_id")): claim
        for claim in claims.get("claims", [])
        if isinstance(claim, dict) and str(claim.get("claim_id")) in {"CL34", "CL35"}
    }
    check(
        "C52/R22 source-registry and claim-audit registration",
        set(c52_registry_records) == {"S61", "S62"}
        and c52_registry_records["S61"].get("path") == "analysis/c52_sse_etf_option_history_route_screen_20260815.json"
        and c52_registry_records["S61"].get("sha256") == "49dddcdc0e1c6927df6a794464d1a7640c99bdf55d25474e6f032fed6f7609da"
        and c52_registry_records["S61"].get("case_source_manifest") == str(c52_manifest_path.relative_to(REPO_ROOT))
        and c52_registry_records["S61"].get("case_source_manifest_sha256") == "92fdb7356454e21c203ea88baf6d3a7fee1d03e7fde576901d2e1ccc50de0c76"
        and c52_registry_records["S62"].get("path") == "analysis/r22_c52_independent_source_audit_20260815.json"
        and c52_registry_records["S62"].get("sha256") == "4daf702ed8e2a65d135a8a5d55beb2071cbc939cd2b87f6663c416319b56fda1"
        and set(c52_claim_records) == {"CL34", "CL35"}
        and c52_claim_records["CL34"].get("source_ids") == ["S53", "S54", "S58", "S61"]
        and c52_claim_records["CL35"].get("source_ids") == ["S53", "S54", "S58", "S61", "S62"],
        f"registry={sorted(c52_registry_records)}; claims={sorted(c52_claim_records)}",
    )
    r16_items = r16_repair_plan.get("items", [])
    r16_statuses = {
        str(item.get("issue_id")): str(item.get("status"))
        for item in r16_items
        if isinstance(item, dict)
    }
    r17_checks = r17_recheck.get("checks", [])
    r17_statuses = {
        str(item.get("issue_id")): str(item.get("status"))
        for item in r17_checks
        if isinstance(item, dict)
    }
    r17_final = r17_recheck.get("final_decision", {}) if isinstance(r17_recheck.get("final_decision"), dict) else {}
    check(
        "R16/R17 independent repair-closure boundary",
        r16_repair_plan.get("plan_status") == "all_repairs_independently_verified_closed"
        and r16_repair_plan.get("independent_recheck_artifact") == "analysis/r17_r16_repair_independent_recheck_20260815.json"
        and r16_repair_plan.get("recheck_required") is False
        and {"R16-S-001", "R16-A-001", "R16-B-001"} <= set(r16_statuses)
        and all(r16_statuses[issue_id] == "verified_closed" for issue_id in ("R16-S-001", "R16-A-001", "R16-B-001"))
        and all(r17_statuses.get(issue_id) == "verified_closed" for issue_id in ("R16-S-001", "R16-A-001", "R16-B-001"))
        and r17_recheck.get("finding_counts", {}).get("new_S") == 0
        and r17_recheck.get("finding_counts", {}).get("new_A") == 0
        and r17_recheck.get("finding_counts", {}).get("new_B") == 0
        and r17_final.get("repairs_closed") is True
        and r17_final.get("strategy_admitted") is False
        and r17_final.get("security_admitted") is False
        and r17_final.get("external_action_authorized") is False
        and r17_final.get("publication_status") == "BLOCKED",
        f"plan={r16_repair_plan.get('plan_status')}; recheck={r17_final.get('repairs_closed')}",
    )
    r18_counts = r18_c49_audit.get("finding_counts", {}) if isinstance(r18_c49_audit.get("finding_counts"), dict) else {}
    r18_final = r18_c49_audit.get("final_decision", {}) if isinstance(r18_c49_audit.get("final_decision"), dict) else {}
    r18_check_ids = {
        str(item.get("check_id"))
        for item in r18_c49_audit.get("checks", [])
        if isinstance(item, dict) and item.get("result") == "PASS"
    }
    check(
        "R18 independent C49 source-audit boundary",
        r18_c49_audit.get("reviewer", {}).get("mode") == "independent_read_only_maker_checker"
        and {"R18-C-001", "R18-C-002", "R18-C-003", "R18-C-004"} <= r18_check_ids
        and r18_counts.get("S") == 0
        and r18_counts.get("A") == 0
        and r18_counts.get("B") == 0
        and r18_final.get("c49_source_boundary_accepted") is True
        and r18_final.get("c48_status_unchanged") is True
        and r18_final.get("strategy_admitted") is False
        and r18_final.get("external_action_authorized") is False,
        f"findings={r18_counts}; C48 unchanged={r18_final.get('c48_status_unchanged')}",
    )
    r19_counts = r19_c50_audit.get("finding_counts", {}) if isinstance(r19_c50_audit.get("finding_counts"), dict) else {}
    r19_final = r19_c50_audit.get("final_decision", {}) if isinstance(r19_c50_audit.get("final_decision"), dict) else {}
    r19_c48_binding = r19_c50_audit.get("c48_binding", {}) if isinstance(r19_c50_audit.get("c48_binding"), dict) else {}
    r19_check_ids = {
        str(item.get("check_id"))
        for item in r19_c50_audit.get("primary_source_claim_checks", [])
        if isinstance(item, dict) and item.get("result") == "PASS"
    }
    check(
        "R19 independent C50 source-audit boundary",
        r19_c50_audit.get("reviewer", {}).get("mode") == "independent_maker_checker"
        and {"R19-C-001", "R19-C-002", "R19-C-003", "R19-C-004", "R19-C-005"} <= r19_check_ids
        and r19_counts.get("S") == 0
        and r19_counts.get("A") == 0
        and r19_counts.get("B") == 0
        and r19_final.get("audit_recommendation") == "PASS"
        and r19_final.get("actionability_status") == "VETO"
        and r19_final.get("review_acceptance_is_not_route_admission") is True
        and r19_final.get("strategy_admitted") is False
        and r19_final.get("external_action_authorized") is False
        and r19_c48_binding.get("unchanged") is True
        and r19_c48_binding.get("C50_does_not_close_C48") is True,
        f"findings={r19_counts}; actionability={r19_final.get('actionability_status')}; C48 unchanged={r19_c48_binding.get('unchanged')}",
    )
    r20_counts = r20_c51_initial_audit.get("finding_counts", {}) if isinstance(r20_c51_initial_audit.get("finding_counts"), dict) else {}
    r20_final = r20_c51_initial_audit.get("final_decision", {}) if isinstance(r20_c51_initial_audit.get("final_decision"), dict) else {}
    r20_c48_binding = r20_c51_initial_audit.get("c48_binding", {}) if isinstance(r20_c51_initial_audit.get("c48_binding"), dict) else {}
    r20_required_next = r20_c51_initial_audit.get("required_next_control", {}) if isinstance(r20_c51_initial_audit.get("required_next_control"), dict) else {}
    r20_check_ids = {
        str(item.get("check_id"))
        for item in r20_c51_initial_audit.get("primary_source_claim_checks", [])
        if isinstance(item, dict) and str(item.get("result", "")).startswith("PASS")
    }
    r20_a = r20_c51_initial_audit.get("findings", {}).get("A", []) if isinstance(r20_c51_initial_audit.get("findings"), dict) else []
    r20_b = r20_c51_initial_audit.get("findings", {}).get("B", []) if isinstance(r20_c51_initial_audit.get("findings"), dict) else []
    r20_repair_items = {
        str(item.get("finding_id")): item
        for item in r20_c51_repair_plan.get("items", [])
        if isinstance(item, dict)
    }
    check(
        "R20 C51 initial audit preserves open findings and required R21",
        r20_c51_initial_audit.get("reviewer", {}).get("mode") == "independent_maker_checker"
        and {"R20-C-001", "R20-C-002", "R20-C-003", "R20-C-004", "R20-C-005"} <= r20_check_ids
        and r20_counts.get("S") == 0
        and r20_counts.get("A") == 1
        and r20_counts.get("B") == 1
        and r20_counts.get("M") == 4
        and isinstance(r20_a, list)
        and len(r20_a) == 1
        and r20_a[0].get("finding_id") == "R20-A-001"
        and r20_a[0].get("status") == "OPEN"
        and isinstance(r20_b, list)
        and len(r20_b) == 1
        and r20_b[0].get("finding_id") == "R20-B-001"
        and r20_b[0].get("status") == "OPEN"
        and r20_final.get("audit_recommendation") == "FAIL_PENDING_REPAIR_AND_INDEPENDENT_RECHECK"
        and r20_final.get("actionability_status") == "VETO"
        and r20_final.get("review_acceptance_is_not_route_admission") is True
        and r20_final.get("strategy_admitted") is False
        and r20_final.get("external_action_authorized") is False
        and r20_c48_binding.get("unchanged") is True
        and r20_c48_binding.get("C51_does_not_close_C48") is True
        and r20_required_next.get("control_id") == "R21"
        and r20_required_next.get("must_be_separate_from_R20") is True,
        f"findings={r20_counts}; audit={r20_final.get('audit_recommendation')}; next={r20_required_next.get('control_id')}",
    )
    check(
        "R20 C51 repair plan preserves independent-closure boundary",
        r20_c51_repair_plan.get("source_audit", {}).get("sha256") == sha256(R20_C51_INITIAL_AUDIT)
        and r20_c51_repair_plan.get("plan_status") == "repairs_implemented_pending_independent_R21_recheck"
        and r20_repair_items.get("R20-A-001", {}).get("status") == "implemented_pending_independent_R21_recheck"
        and r20_repair_items.get("R20-B-001", {}).get("status") == "implemented_pending_independent_R21_recheck"
        and "R20-M-001" in r20_repair_items
        and "R20-M-004" in r20_repair_items
        and r20_c51_repair_plan.get("validation_run_by_repair_owner", {}).get("result") == "local_repair_validation_passed_not_independent_closure",
        f"plan={r20_c51_repair_plan.get('plan_status')}; repairs={sorted(r20_repair_items)}",
    )
    r21_snapshot = r21_c51_recheck.get("review_snapshot", {}) if isinstance(r21_c51_recheck.get("review_snapshot"), dict) else {}
    r21_r20_binding = r21_c51_recheck.get("r20_and_repair_plan_binding", {}) if isinstance(r21_c51_recheck.get("r20_and_repair_plan_binding"), dict) else {}
    r21_payoff = r21_c51_recheck.get("payoff_math_recheck", {}) if isinstance(r21_c51_recheck.get("payoff_math_recheck"), dict) else {}
    r21_generated = r21_c51_recheck.get("generated_artifact_and_boundary_checks", {}) if isinstance(r21_c51_recheck.get("generated_artifact_and_boundary_checks"), dict) else {}
    r21_disposition = r21_c51_recheck.get("r20_finding_disposition", {}) if isinstance(r21_c51_recheck.get("r20_finding_disposition"), dict) else {}
    r21_counts = r21_c51_recheck.get("finding_counts", {}) if isinstance(r21_c51_recheck.get("finding_counts"), dict) else {}
    r21_c48_binding = r21_c51_recheck.get("c48_binding", {}) if isinstance(r21_c51_recheck.get("c48_binding"), dict) else {}
    r21_final = r21_c51_recheck.get("final_decision", {}) if isinstance(r21_c51_recheck.get("final_decision"), dict) else {}
    check(
        "R21 independent C51 formula/source-control recheck boundary",
        r21_c51_recheck.get("reviewer", {}).get("mode") == "independent_maker_checker"
        and r21_c51_recheck.get("reviewer", {}).get("review_type") == "separate_read_only_repair_recheck"
        and r21_snapshot.get("c51_builder_sha256") == sha256(CASE_DIR / "tools" / "c51_build_sse_etf_option_collar_scope_screen.py")
        and r21_snapshot.get("c51_json_sha256") == sha256(C51)
        and r21_snapshot.get("c51_markdown_sha256") == sha256(CASE_DIR / "analysis" / "c51_sse_etf_option_collar_scope_screen_20260815.md")
        and r21_snapshot.get("source_manifest_sha256") == sha256(c51_manifest_path)
        and r21_snapshot.get("predecessor_c13_sha256") == sha256(c51_c13_path)
        and r21_snapshot.get("r20_initial_audit_sha256") == sha256(R20_C51_INITIAL_AUDIT)
        and r21_snapshot.get("r20_repair_plan_sha256") == sha256(R20_C51_REPAIR_PLAN)
        and r21_snapshot.get("c48_sha256") == sha256(C48)
        and r21_r20_binding.get("r20_initial_audit", {}).get("historical_record_preserved") is True
        and r21_r20_binding.get("repair_plan", {}).get("references_exact_r20_hash") is True
        and r21_r20_binding.get("repair_plan", {}).get("current_output_hashes_match_review_snapshot") is True
        and r21_payoff.get("general_formula") == "min(S_T, K_C) + max(K_P - S_T, 0) + C - P"
        and r21_payoff.get("compact_formula_condition") == "K_P <= K_C"
        and r21_payoff.get("universal_identity_test", "").startswith("PASS")
        and r21_payoff.get("conditioned_identity_test", "").startswith("PASS")
        and r21_payoff.get("nonordered_counterexample_preserved", {}).get("direct_and_general_value") == 100
        and r21_payoff.get("nonordered_counterexample_preserved", {}).get("compact_value") == 150
        and r21_generated.get("builder_result_matches_current_json_exactly") is True
        and r21_generated.get("markdown_function_matches_current_markdown_exactly") is True
        and r21_generated.get("combo_schema_limitation_explicit") is True
        and r21_generated.get("reader_facing_prohibited_principal_term_present") is False
        and r21_generated.get("invented_historical_result_present") is False
        and r21_generated.get("personal_account_entitlement_claim_present") is False
        and r21_generated.get("trade_instruction_present") is False
        and r21_disposition.get("R20-A-001", {}).get("R21_status") == "CLOSED_BY_INDEPENDENT_RECHECK"
        and r21_disposition.get("R20-B-001", {}).get("R21_status") == "CLOSED_BY_INDEPENDENT_RECHECK"
        and r21_counts.get("S") == 0
        and r21_counts.get("A") == 0
        and r21_counts.get("B") == 0
        and r21_counts.get("M") == 4
        and r21_c48_binding.get("unchanged") is True
        and r21_c48_binding.get("C51_does_not_close_C48") is True
        and r21_final.get("audit_recommendation") == "PASS_SOURCE_AND_REPAIR_BOUNDED_ONLY"
        and r21_final.get("actionability_status") == "VETO"
        and r21_final.get("review_acceptance_is_not_route_admission") is True
        and r21_final.get("strategy_admitted") is False
        and r21_final.get("external_action_authorized") is False,
        f"findings={r21_counts}; audit={r21_final.get('audit_recommendation')}; actionability={r21_final.get('actionability_status')}",
    )

    r22_snapshot = r22_c52_audit.get("review_snapshot", {}) if isinstance(r22_c52_audit.get("review_snapshot"), dict) else {}
    expected_r22_snapshot = {
        "capture_script": {
            "path": "tools/c52_capture_sse_etf_option_history_sources.py",
            "byte_count": 6227,
            "sha256": "2903bdc210124935f1a37ed4a86583986ba6cb741893ba64b25b8d962bdaedbc",
        },
        "builder_script": {
            "path": "tools/c52_build_sse_etf_option_history_route_screen.py",
            "byte_count": 21857,
            "sha256": "b0f77fd085167336c0b079f0f7b39e617c50350dd68b4ba2564b982c7a324404",
        },
        "c52_json": {
            "path": "analysis/c52_sse_etf_option_history_route_screen_20260815.json",
            "byte_count": 8615,
            "sha256": "49dddcdc0e1c6927df6a794464d1a7640c99bdf55d25474e6f032fed6f7609da",
        },
        "c52_markdown": {
            "path": "analysis/c52_sse_etf_option_history_route_screen_20260815.md",
            "byte_count": 4128,
            "sha256": "f890d10257a943684f330b336f9d9d37cea3ec3beaefbebe2518de5a33812312",
        },
    }
    r22_snapshot_failures: list[str] = []
    if set(r22_snapshot) != set(expected_r22_snapshot):
        r22_snapshot_failures.append("snapshot coverage")
    else:
        for snapshot_id, expected in expected_r22_snapshot.items():
            snapshot = r22_snapshot.get(snapshot_id, {})
            path = CASE_DIR / expected["path"]
            if not isinstance(snapshot, dict) or any(snapshot.get(field) != value for field, value in expected.items()):
                r22_snapshot_failures.append(f"snapshot fields {snapshot_id}")
                continue
            if not path.is_file() or path.stat().st_size != expected["byte_count"] or sha256(path) != expected["sha256"]:
                r22_snapshot_failures.append(f"snapshot integrity {snapshot_id}")

    r22_source_manifest = r22_c52_audit.get("source_manifest", {}) if isinstance(r22_c52_audit.get("source_manifest"), dict) else {}
    r22_raw_integrity = r22_source_manifest.get("raw_file_integrity", [])
    r22_raw_by_id = {
        str(item.get("source_id")): item
        for item in r22_raw_integrity
        if isinstance(item, dict)
    }
    r22_raw_failures: list[str] = []
    if (
        r22_source_manifest.get("path") != str(c52_manifest_path.relative_to(REPO_ROOT))
        or r22_source_manifest.get("artifact_id") != "D5PT-C52-SOURCES-v1"
        or r22_source_manifest.get("retrieved_at_utc") != "2026-08-15T06:41:33+00:00"
        or r22_source_manifest.get("byte_count") != 3411
        or r22_source_manifest.get("sha256") != "92fdb7356454e21c203ea88baf6d3a7fee1d03e7fde576901d2e1ccc50de0c76"
        or not c52_manifest_path.is_file()
        or c52_manifest_path.stat().st_size != 3411
        or sha256(c52_manifest_path) != "92fdb7356454e21c203ea88baf6d3a7fee1d03e7fde576901d2e1ccc50de0c76"
    ):
        r22_raw_failures.append("source manifest snapshot")
    if len(r22_raw_integrity) != len(expected_c52_sources) or set(r22_raw_by_id) != set(expected_c52_sources):
        r22_raw_failures.append("raw source coverage")
    else:
        for source_id, expected in expected_c52_sources.items():
            raw_record = r22_raw_by_id[source_id]
            if (
                raw_record.get("filename") != expected["filename"]
                or raw_record.get("byte_count") != expected["byte_count"]
                or raw_record.get("sha256") != expected["sha256"]
                or raw_record.get("integrity") != "PASS"
            ):
                r22_raw_failures.append(f"raw snapshot fields {source_id}")
                break
            path = c52_manifest_path.parent / expected["filename"]
            if not path.is_file() or path.stat().st_size != expected["byte_count"] or sha256(path) != expected["sha256"]:
                r22_raw_failures.append(f"raw snapshot integrity {source_id}")
                break

    expected_r22_dependency_paths = {
        "c48": "analysis/c48_current_environment_data_capability_audit_20260815.json",
        "c49": "analysis/c49_official_authorized_data_route_recheck_20260815.json",
        "c51": "analysis/c51_sse_etf_option_collar_scope_screen_20260815.json",
    }
    r22_dependencies = r22_c52_audit.get("dependency_integrity", {}) if isinstance(r22_c52_audit.get("dependency_integrity"), dict) else {}
    r22_dependency_failures: list[str] = []
    if set(r22_dependencies) != set(expected_c52_dependencies):
        r22_dependency_failures.append("dependency coverage")
    else:
        for dependency_id, expected in expected_c52_dependencies.items():
            dependency = r22_dependencies.get(dependency_id, {})
            expected_path = expected_r22_dependency_paths[dependency_id]
            path = CASE_DIR / expected_path
            if (
                not isinstance(dependency, dict)
                or dependency.get("path") != expected_path
                or dependency.get("sha256") != expected["sha256"]
                or dependency.get("status") != expected["status"]
                or dependency.get("integrity") != "PASS"
                or not path.is_file()
                or dependency.get("byte_count") != path.stat().st_size
                or sha256(path) != expected["sha256"]
            ):
                r22_dependency_failures.append(f"dependency integrity {dependency_id}")

    r22_checks = r22_c52_audit.get("checks", [])
    r22_check_results = {
        str(item.get("check_id")): str(item.get("result"))
        for item in r22_checks
        if isinstance(item, dict)
    }
    expected_r22_check_results = {
        "R22-C-001": "PASS",
        "R22-C-002": "PASS",
        "R22-C-003": "PASS_WITH_LIMITATION",
        "R22-C-004": "PASS",
        "R22-C-005": "PASS",
    }
    r22_findings = r22_c52_audit.get("findings", {}) if isinstance(r22_c52_audit.get("findings"), dict) else {}
    r22_m_findings = r22_findings.get("M", []) if isinstance(r22_findings.get("M"), list) else []
    r22_m_ids = {
        str(item.get("finding_id"))
        for item in r22_m_findings
        if isinstance(item, dict)
    }
    r22_counts = r22_c52_audit.get("finding_counts", {}) if isinstance(r22_c52_audit.get("finding_counts"), dict) else {}
    r22_boundary = r22_c52_audit.get("boundary_conclusion", {}) if isinstance(r22_c52_audit.get("boundary_conclusion"), dict) else {}
    r22_final = r22_c52_audit.get("final_decision", {}) if isinstance(r22_c52_audit.get("final_decision"), dict) else {}
    check(
        "R22 independent C52 frozen-snapshot, source-integrity and VETO boundary",
        r22_c52_audit.get("schema_version") == "d5pt_r22_c52_independent_source_audit.v1"
        and r22_c52_audit.get("artifact_id") == "D5PT-R22-C52-INDEPENDENT-SOURCE-AUDIT-v1"
        and sha256(R22_C52_AUDIT) == "4daf702ed8e2a65d135a8a5d55beb2071cbc939cd2b87f6663c416319b56fda1"
        and r22_c52_audit.get("reviewer", {}).get("mode") == "independent_read_only_maker_checker"
        and not r22_snapshot_failures
        and not r22_raw_failures
        and not r22_dependency_failures
        and len(r22_checks) == len(expected_r22_check_results)
        and r22_check_results == expected_r22_check_results
        and r22_counts == {"S": 0, "A": 0, "B": 0, "M": 4}
        and r22_findings.get("S") == []
        and r22_findings.get("A") == []
        and r22_findings.get("B") == []
        and r22_m_ids == {"R22-M-001", "R22-M-002", "R22-M-003", "R22-M-004"}
        and r22_boundary.get("c48_status_unchanged") is True
        and r22_boundary.get("c49_conditional_route_unchanged") is True
        and r22_boundary.get("c51_not_admitted_unchanged") is True
        and r22_boundary.get("positive_five_percent_floor_accepted") is False
        and r22_boundary.get("historical_result_accepted") is False
        and r22_boundary.get("data_rights_granted") is False
        and r22_boundary.get("strategy_admitted") is False
        and r22_boundary.get("product_or_parameter_selected") is False
        and r22_boundary.get("external_action_authorized") is False
        and r22_final.get("audit_recommendation") == "PASS_SOURCE_CONTROL_AND_BOUNDARY_ONLY"
        and r22_final.get("actionability_status") == "VETO"
        and "does not close C48" in str(r22_final.get("statement")),
        f"snapshot failures={r22_snapshot_failures}; raw failures={r22_raw_failures}; dependency failures={r22_dependency_failures}; findings={r22_counts}; actionability={r22_final.get('actionability_status')}",
    )

    r23_snapshot = r23_c52_governance_recheck.get("snapshot", {}) if isinstance(r23_c52_governance_recheck.get("snapshot"), dict) else {}
    r23_r22_historical = r23_snapshot.get("r22_historical_record", {}) if isinstance(r23_snapshot.get("r22_historical_record"), dict) else {}
    r23_r22_historical_valid = (
        r23_r22_historical.get("json_path") == "analysis/r22_c52_independent_source_audit_20260815.json"
        and r23_r22_historical.get("json_byte_count") == 11520
        and r23_r22_historical.get("json_sha256") == "4daf702ed8e2a65d135a8a5d55beb2071cbc939cd2b87f6663c416319b56fda1"
        and r23_r22_historical.get("markdown_path") == "analysis/r22_c52_independent_source_audit_20260815.md"
        and r23_r22_historical.get("markdown_byte_count") == 4576
        and r23_r22_historical.get("markdown_sha256") == "6ced9aca81d039fdf9ebcb6b641ec6dc5fc5106eb8c8d82aab7a77e86e23b358"
        and R22_C52_AUDIT.stat().st_size == 11520
        and sha256(R22_C52_AUDIT) == "4daf702ed8e2a65d135a8a5d55beb2071cbc939cd2b87f6663c416319b56fda1"
        and (CASE_DIR / "analysis" / "r22_c52_independent_source_audit_20260815.md").stat().st_size == 4576
        and sha256(CASE_DIR / "analysis" / "r22_c52_independent_source_audit_20260815.md") == "6ced9aca81d039fdf9ebcb6b641ec6dc5fc5106eb8c8d82aab7a77e86e23b358"
    )
    r23_r09_historical = r23_snapshot.get("r09_final_stable_snapshot", {}) if isinstance(r23_snapshot.get("r09_final_stable_snapshot"), dict) else {}
    expected_r23_r09_historical = {
        "stability_check": "Identical SHA-256 values observed across three reads over four seconds after the R09 writer confirmed completion.",
        "script_path": "tools/r09_verify_research_control_records.py",
        "script_byte_count": 84291,
        "script_sha256": "2a03c718752cca52a721b6262129ac9368af21db14cd5065796d1085036068c1",
        "json_path": "analysis/r09_research_control_record_audit_20260815.json",
        "json_byte_count": 22477,
        "json_sha256": "2b141cc83722f65b09508b7cae4e203e35de04078cc1da19ee8c2eed6040bee0",
        "markdown_path": "analysis/r09_research_control_record_audit_20260815.md",
        "markdown_byte_count": 18427,
        "markdown_sha256": "98fc930a9138d781d81cccb9e2897e395e498a322ae8bf2a7f4a989f195cc33d",
        "result": "PASS",
        "failed_check_count": 0,
        "total_check_count": 66,
    }
    # R23 pins the prior completed R09 record. Do not compare this historical
    # snapshot with the current R09 source or output, which this verifier regenerates.
    r23_r09_historical_valid = all(
        r23_r09_historical.get(field) == value
        for field, value in expected_r23_r09_historical.items()
    )
    r23_checks = r23_c52_governance_recheck.get("checks", [])
    r23_check_results = {
        str(item.get("check_id")): str(item.get("result"))
        for item in r23_checks
        if isinstance(item, dict)
    }
    expected_r23_check_results = {
        "R23-C-001": "PASS",
        "R23-C-002": "PASS",
        "R23-C-003": "PASS",
        "R23-C-004": "PASS",
        "R23-C-005": "PASS",
    }
    r23_m004 = r23_c52_governance_recheck.get("r22_m004_disposition", {}) if isinstance(r23_c52_governance_recheck.get("r22_m004_disposition"), dict) else {}
    r23_findings = r23_c52_governance_recheck.get("findings", {}) if isinstance(r23_c52_governance_recheck.get("findings"), dict) else {}
    r23_m_findings = r23_findings.get("M", []) if isinstance(r23_findings.get("M"), list) else []
    r23_m_by_id = {
        str(item.get("finding_id")): item
        for item in r23_m_findings
        if isinstance(item, dict)
    }
    r23_counts = r23_c52_governance_recheck.get("finding_counts", {}) if isinstance(r23_c52_governance_recheck.get("finding_counts"), dict) else {}
    r23_boundary = r23_c52_governance_recheck.get("boundary_conclusion", {}) if isinstance(r23_c52_governance_recheck.get("boundary_conclusion"), dict) else {}
    r23_final = r23_c52_governance_recheck.get("final_decision", {}) if isinstance(r23_c52_governance_recheck.get("final_decision"), dict) else {}
    r23_not_performed = r23_c52_governance_recheck.get("scope", {}).get("not_performed", []) if isinstance(r23_c52_governance_recheck.get("scope"), dict) else []
    r23_registry = next(
        (record for record in records if isinstance(record, dict) and record.get("source_id") == "S63"),
        {},
    )
    r23_claim = next(
        (claim for claim in claims.get("claims", []) if isinstance(claim, dict) and claim.get("claim_id") == "CL36"),
        {},
    )
    r23_contract = next(
        (
            item
            for item in contract.get("artifacts", [])
            if isinstance(item, dict) and item.get("artifact") == "analysis/r23_c52_governance_registration_independent_recheck_20260815.*"
        ),
        {},
    )
    required_r23_artifacts = {
        "analysis/r23_c52_governance_registration_independent_recheck_20260815.md",
        "analysis/r23_c52_governance_registration_independent_recheck_20260815.json",
    }
    r23_gate_registration_valid = (
        required_r23_artifacts <= set(gate_manifest.get("required_artifacts", []))
        and r23_contract.get("verifier_check") == "R09 R23 governance-registration follow-up and substantive-boundary control"
        and r23_contract.get("blocking_if_missing") is True
        and any("R23 may close only R22-M-004" in str(item) for item in gate_manifest.get("pass_conditions", []))
    )
    check(
        "R23 governance-registration historical audit, limited closure and VETO boundary",
        r23_c52_governance_recheck.get("schema_version") == "d5pt_r23_c52_governance_registration_independent_recheck.v1"
        and r23_c52_governance_recheck.get("artifact_id") == "D5PT-R23-C52-GOVERNANCE-REGISTRATION-INDEPENDENT-RECHECK-v1"
        and r23_c52_governance_recheck.get("reviewer", {}).get("role") == "research-report-reviewer"
        and r23_c52_governance_recheck.get("reviewer", {}).get("mode") == "independent_read_only_governance_recheck"
        and r23_r22_historical_valid
        and r23_r09_historical_valid
        and len(r23_checks) == len(expected_r23_check_results)
        and r23_check_results == expected_r23_check_results
        and r23_m004.get("historical_finding_id") == "R22-M-004"
        and r23_m004.get("historical_status") == "PRESERVED_IN_R22"
        and r23_m004.get("follow_up_status") == "CLOSED_BY_R23_GOVERNANCE_REGISTRATION_RECHECK"
        and "Closes only the governance-registration follow-up identified by R22-M-004" in str(r23_m004.get("closure_scope"))
        and "does not amend, erase, or close R22-M-001 through R22-M-003" in str(r23_m004.get("closure_scope"))
        and r23_findings.get("S") == []
        and r23_findings.get("A") == []
        and r23_findings.get("B") == []
        and r23_counts == {"S": 0, "A": 0, "B": 0, "M": 3}
        and set(r23_m_by_id) == {"R23-M-001", "R23-M-002", "R23-M-003"}
        and all(
            r23_m_by_id[f"R23-M-00{number}"].get("status") == f"CONTINUING_FROM_R22-M-00{number}"
            for number in (1, 2, 3)
        )
        and r23_boundary.get("r22_m004_governance_follow_up_closed") is True
        and r23_boundary.get("r22_substantive_limitations_closed") is False
        and r23_boundary.get("c48_status_unchanged") is True
        and r23_boundary.get("c49_conditional_route_unchanged") is True
        and r23_boundary.get("c51_not_admitted_unchanged") is True
        and r23_boundary.get("historical_replay_accepted") is False
        and r23_boundary.get("positive_five_percent_floor_accepted") is False
        and r23_boundary.get("data_rights_granted") is False
        and r23_boundary.get("strategy_admitted") is False
        and r23_boundary.get("product_or_parameter_selected") is False
        and r23_boundary.get("external_action_authorized") is False
        and r23_final.get("audit_recommendation") == "PASS_GOVERNANCE_REGISTRATION_BOUNDARY_ONLY"
        and r23_final.get("actionability_status") == "VETO"
        and any("external action" in str(item) for item in r23_not_performed)
        and r23_registry.get("source_id") == "S63"
        and r23_registry.get("path") == "analysis/r23_c52_governance_registration_independent_recheck_20260815.json"
        and r23_registry.get("quality_tier") == "independent_governance_registration_follow_up_recheck"
        and isinstance(r23_registry.get("sha256"), str)
        and bool(r23_registry.get("sha256"))
        and sha256(R23_C52_GOVERNANCE_RECHECK) == r23_registry.get("sha256")
        and r23_claim.get("source_ids") == ["S53", "S54", "S58", "S61", "S62", "S63"]
        and r23_gate_registration_valid,
        f"R22 historical={r23_r22_historical_valid}; R09 historical={r23_r09_historical_valid}; findings={r23_counts}; actionability={r23_final.get('actionability_status')}; gate_registration={r23_gate_registration_valid}",
    )
    c53_registry = next(
        (record for record in records if isinstance(record, dict) and record.get("source_id") == "S64"),
        {},
    )
    c53_claim = next(
        (claim for claim in claims.get("claims", []) if isinstance(claim, dict) and claim.get("claim_id") == "CL37"),
        {},
    )
    c53_contract = next(
        (
            item
            for item in contract.get("artifacts", [])
            if isinstance(item, dict) and item.get("artifact") == "analysis/c53_equity_led_domestic_target_strategy_protocol_20260815.*"
        ),
        {},
    )
    required_c53_artifacts = {
        "analysis/c53_equity_led_domestic_target_strategy_protocol_20260815.md",
        "analysis/c53_equity_led_domestic_target_strategy_protocol_20260815.json",
        "data/c53_quarterly_paper_observation_ledger_template_20260815.json",
        "data/c53_quarterly_paper_observation_ledger_template_20260815.csv",
    }
    c53_ledger_contract = next(
        (
            item
            for item in contract.get("artifacts", [])
            if isinstance(item, dict) and item.get("artifact") == "data/c53_quarterly_paper_observation_ledger_template_20260815.{json,csv}"
        ),
        {},
    )
    check(
        "C53 source, claim, gate and artifact-contract registration",
        c53_registry.get("source_id") == "S64"
        and c53_registry.get("path") == "analysis/c53_equity_led_domestic_target_strategy_protocol_20260815.json"
        and c53_registry.get("quality_tier") == "draft_paper_protocol_with_no_strategy_admission"
        and c53_registry.get("sha256") == sha256(C53)
        and c53_claim.get("source_ids") == ["S38", "S40", "S41", "S53", "S64"]
        and required_c53_artifacts <= set(gate_manifest.get("required_artifacts", []))
        and c53_contract.get("verifier_check") == "R09 C53 non-admission, source-registration and fail-closed control"
        and c53_contract.get("blocking_if_missing") is True
        and c53_ledger_contract.get("verifier_check") == "R09 C53 bound-ledger reconstruction and no-action control"
        and c53_ledger_contract.get("blocking_if_missing") is True,
        f"registry={c53_registry.get('sha256')}; claim={c53_claim.get('source_ids')}; gate={sorted(required_c53_artifacts & set(gate_manifest.get('required_artifacts', [])))}; contract={c53_contract.get('verifier_check')}; ledger_contract={c53_ledger_contract.get('verifier_check')}",
    )

    c40_gates = c40.get("gate_results", [])
    c41_gates = c41.get("gate_assessment", [])
    c42_gates = c42.get("gate_assessment", [])
    c41_controls = c41.get("research_controls", {}) if isinstance(c41.get("research_controls"), dict) else {}
    c42_classification = c42.get("classification", {}) if isinstance(c42.get("classification"), dict) else {}
    issuer_boundary_failures: list[str] = []
    if not (
        c40.get("status") == "NON_ADMITTED_RESEARCH_SUBJECT"
        and c40.get("current_action") == "NO_ACTION"
        and c40.get("research_only") is True
        and c40.get("external_orders") is False
        and c40.get("portfolio_q") == 0
        and len(c40_gates) == 10
        and any(str(item.get("status")) != "PASS" for item in c40_gates if isinstance(item, dict))
    ):
        issuer_boundary_failures.append("C40")
    if not (
        c41.get("status") == "NON_ADMITTED_RESEARCH_SUBJECT"
        and c41_controls.get("research_only") is True
        and c41_controls.get("external_orders") is False
        and c41_controls.get("portfolio_q") == 0
        and c41_controls.get("action_status") == "NO_ACTION"
        and len(c41_gates) == 10
        and any(str(item.get("status")) != "PASS" for item in c41_gates if isinstance(item, dict))
    ):
        issuer_boundary_failures.append("C41")
    if not (
        c42_classification.get("status") == "NON_ADMITTED_RESEARCH_SUBJECT"
        and c42_classification.get("current_disposition") == "NO_ACTION"
        and c42_classification.get("research_only") is True
        and c42_classification.get("external_orders") is False
        and c42_classification.get("portfolio_q") == 0
        and c42.get("gate_summary", {}).get("admission_allowed") is False
        and len(c42_gates) == 10
        and any(str(item.get("status")) != "PASS" for item in c42_gates if isinstance(item, dict))
    ):
        issuer_boundary_failures.append("C42")
    check("C40/C41/C42 G0-G9 non-admission and action boundary", not issuer_boundary_failures, ", ".join(issuer_boundary_failures) or "all matched")

    c40_point_in_time = c40.get("liquidity_execution_and_point_in_time", {}) if isinstance(c40.get("liquidity_execution_and_point_in_time"), dict) else {}
    c40_query_locator = str(c40_point_in_time.get("sse_query_timestamp_locator_only") or "")
    check(
        "C40 H1 query-response retention versus availability boundary",
        "case-archived" in c40_query_locator
        and "hash-verified" in c40_query_locator
        and "timestamp semantics" in c40_query_locator
        and "same-session availability" in c40_query_locator
        and "raw response are not retained" not in c40_query_locator,
        c40_query_locator,
    )
    zero_capture_manifest = CASE_DIR / "sources" / "probe-sse-600519-announcement-query-20260815" / "manifest.json"
    zero_capture_valid = False
    if zero_capture_manifest.is_file():
        zero_capture = load_json(zero_capture_manifest)
        zero_capture_valid = (
            zero_capture.get("status") == "intentionally_abandoned_zero_capture"
            and zero_capture.get("evidence_status") == "not_an_evidence_source"
            and zero_capture.get("files") == []
        )
    check("C40 zero-capture probe hygiene", zero_capture_valid, str(zero_capture_manifest.relative_to(CASE_DIR)))

    archive_failures: list[str] = []
    records_by_id = {str(item.get("source_id")): item for item in records if isinstance(item, dict)}
    for source_id in ("S46", "S47", "S48"):
        record = records_by_id.get(source_id, {})
        manifest_text = str(record.get("case_source_manifest") or "")
        expected_hash = str(record.get("case_source_manifest_sha256") or "")
        manifest_path = resolve(manifest_text)
        if not manifest_text or not expected_hash or not manifest_path.is_file() or sha256(manifest_path) != expected_hash:
            archive_failures.append(f"{source_id}: manifest binding")
            continue
        manifest = load_json(manifest_path)
        files = manifest.get("files", [])
        if not isinstance(files, list) or not files:
            archive_failures.append(f"{source_id}: no files")
            continue
        for file_record in files:
            if not isinstance(file_record, dict):
                archive_failures.append(f"{source_id}: invalid file record")
                break
            path = resolve(str(file_record.get("path") or ""))
            expected_file_hash = str(file_record.get("sha256") or "")
            if not path.is_file() or not expected_file_hash or sha256(path) != expected_file_hash:
                archive_failures.append(f"{source_id}: file integrity")
                break
    check("C40/C41/C42 source-archive manifest and file integrity", not archive_failures, "; ".join(archive_failures) or "all matched")

    c33 = load_json(C33)
    c34 = load_json(C34)
    c35 = load_json(C35)
    c36 = load_json(C36)
    c33_codes = [str(item.get("code")) for item in c33.get("actual_instruments", []) if isinstance(item, dict)]
    check("C33 exact five-code set", c33_codes == ["510300", "510880", "511010", "518880", "511990"], str(c33_codes))
    check(
        "C33 C34 strict-screen and action boundary",
        c33.get("status") == "research_only_not_paper_operable_not_admitted"
        and c33.get("current_action") == "NO_ACTION"
        and c33.get("external_orders") is False
        and c33.get("admission", {}).get("strict_five_percent_proxy_hurdle") == "FAIL"
        and c33.get("admission", {}).get("result") == "NO_ADMITTED_USABLE_STRATEGY",
        "C33 research-only/NO_ACTION/strict-screen state",
    )
    hurdle = c34.get("hurdle_assessment", {}) if isinstance(c34.get("hurdle_assessment"), dict) else {}
    full = hurdle.get("base_full_sample", {}) if isinstance(hurdle.get("base_full_sample"), dict) else {}
    holdout = hurdle.get("base_holdout", {}) if isinstance(hurdle.get("base_holdout"), dict) else {}
    check(
        "C34 reported strict-screen failure",
        full.get("rolling_five_year_below_5pct_count") == 43
        and full.get("rolling_five_year_endpoint_count") == 98
        and holdout.get("annualized_market_price_proxy_change_after_illustrative_cost") == 0.046852659717272704,
        "full rolling failures and chronological robustness slice",
    )
    check(
        "C35/C36 actionability boundary",
        c35.get("status") == "research_only_forward_ledger_incomplete"
        and c35.get("external_orders") is False
        and c36.get("source_integrity_status") == "PASS"
        and c36.get("actionability_status") == "VETO",
        "C35 research-only and C36 dated-source PASS/actionability VETO",
    )
    c33_hash_failures: list[str] = []
    for evidence in c33.get("evidence_refs", []):
        if not isinstance(evidence, dict):
            c33_hash_failures.append("invalid evidence ref")
            continue
        path = CASE_DIR / str(evidence.get("artifact") or "")
        expected_hash = str(evidence.get("sha256") or "")
        if not path.is_file() or not expected_hash or sha256(path) != expected_hash:
            c33_hash_failures.append(str(evidence.get("artifact") or "unknown"))
    check("C33 evidence hashes", not c33_hash_failures, ", ".join(c33_hash_failures) or "all matched")
    ledger_template = load_json(C33_LEDGER_TEMPLATE)
    check("C33 forward ledger remains incomplete", ledger_template.get("status") == "template_only_no_observations", str(ledger_template.get("status")))
    exhaustion_items = load_json(CASE_DIR / "source_exhaustion_log.json").get("items", [])
    exhaustion_scopes = {str(item.get("scope")) for item in exhaustion_items if isinstance(item, dict)}
    check("C34 source-exhaustion entry", "C34 five-ETF dual-horizon inverse-volatility candidate" in exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    request_ids = {str(item.get("id")) for item in request_pack.get("requirements", []) if isinstance(item, dict)}
    unresolved_ids = {str(item.get("id")) for item in unresolved.get("requirements", []) if isinstance(item, dict)}
    check("C34 missing-data request", "c34_five_etf_total_return_event_and_execution_evidence" in request_ids, ", ".join(sorted(request_ids)))
    check("C34 unresolved gates", {"c34_total_return_and_execution_evidence", "c34_forward_paper_observation_record"} <= unresolved_ids, ", ".join(sorted(unresolved_ids)))
    check("C37/C39 source-exhaustion entries", {"C37 domestic ETF investor-total-return source route", "C39 audited cash-flow realization cohort hypothesis"} <= exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    check("C37/C39 missing-data requests", {"c37_new_etf_historical_total_return_event_and_execution_contract", "c39_preregistered_equity_cohort_data_execution_and_forward_record"} <= request_ids, ", ".join(sorted(request_ids)))
    check("C37/C39 unresolved gates", {"c37_etf_total_return_event_execution_and_rights", "c39_preregistered_cohort_data_execution_and_forward_record"} <= unresolved_ids, ", ".join(sorted(unresolved_ids)))
    check("C46/C47 source-exhaustion entry", "C46/C47 five-family actual-contract calendar-curve route" in exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    check("C48 source-exhaustion entry", "C48 current-environment formal historical research capability" in exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    c48_exhaustion = next((item for item in exhaustion_items if isinstance(item, dict) and item.get("scope") == "C48 current-environment formal historical research capability"), {})
    check("C49 source-exhaustion evidence", "analysis/c49_official_authorized_data_route_recheck_20260815.json" in c48_exhaustion.get("evidence", []), str(c48_exhaustion.get("evidence")))
    check("C46/C48 missing-data requests", {"new_calendar_relative_value_actual_contract_execution_and_rights_contract", "current_environment_formal_strategy_data_rights_and_acceptance"} <= request_ids, ", ".join(sorted(request_ids)))
    check("C48 unresolved gate", "current_environment_formal_data_rights_total_return_execution_acceptance" in unresolved_ids, ", ".join(sorted(unresolved_ids)))
    check("C50 source-exhaustion entry", "C50 SSE general pledged reverse-repo yield-floor screen" in exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    check("C50 unresolved gate", "c50_general_repo_yield_floor_and_execution_evidence" in unresolved_ids, ", ".join(sorted(unresolved_ids)))
    check("C51 source-exhaustion entry", "C51 SSE ETF-collar option non-duplication and data-contract screen" in exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    check("C51 unresolved gate", "c51_sse_etf_option_collar_data_and_execution_evidence" in unresolved_ids, ", ".join(sorted(unresolved_ids)))
    c52_exhaustion_scope = "C52 SSE public ETF-option historical-source route screen"
    c52_exhaustion = next(
        (item for item in exhaustion_items if isinstance(item, dict) and item.get("scope") == c52_exhaustion_scope),
        {},
    )
    check("C52 source-exhaustion entry", c52_exhaustion_scope in exhaustion_scopes, ", ".join(sorted(exhaustion_scopes)))
    check(
        "C52 source-exhaustion and R22 VETO evidence",
        "analysis/c52_sse_etf_option_history_route_screen_20260815.json" in c52_exhaustion.get("evidence", [])
        and "analysis/r22_c52_independent_source_audit_20260815.json" in c52_exhaustion.get("evidence", [])
        and "sources/c52-sse-etf-option-history-route-20260815/manifest.json" in c52_exhaustion.get("evidence", [])
        and c52_exhaustion.get("status") == "public_source_coverage_insufficient_for_c51_historical_replay"
        and "VETO" in str(c52_exhaustion.get("consequence"))
        and "NO_ACTION" in str(c52_exhaustion.get("consequence")),
        str(c52_exhaustion.get("evidence")),
    )
    required_c52_r22_artifacts = {
        "analysis/c52_sse_etf_option_history_route_screen_20260815.md",
        "analysis/c52_sse_etf_option_history_route_screen_20260815.json",
        "analysis/r22_c52_independent_source_audit_20260815.md",
        "analysis/r22_c52_independent_source_audit_20260815.json",
    }
    contract_artifacts = {
        str(item.get("artifact"))
        for item in contract.get("artifacts", [])
        if isinstance(item, dict)
    }
    check(
        "C52/R22 gate-manifest and artifact-contract registration",
        required_c52_r22_artifacts <= set(gate_manifest.get("required_artifacts", []))
        and "analysis/c52_sse_etf_option_history_route_screen_20260815.*" in contract_artifacts
        and "analysis/r22_c52_independent_source_audit_20260815.*" in contract_artifacts,
        f"required={sorted(required_c52_r22_artifacts & set(gate_manifest.get('required_artifacts', [])))}; contract={sorted(contract_artifacts & {'analysis/c52_sse_etf_option_history_route_screen_20260815.*', 'analysis/r22_c52_independent_source_audit_20260815.*'})}",
    )
    required_artifact_failures = [
        path_text
        for path_text in gate_manifest.get("required_artifacts", [])
        if not (CASE_DIR / str(path_text)).is_file()
    ]
    check("gate-manifest required artifacts exist", not required_artifact_failures, ", ".join(required_artifact_failures) or "all present")

    prohibited_pattern = re.compile(r"本金|初始资金|初始金额|initial capital|initial_capital|\\bprincipal\\b|starting amount", re.IGNORECASE)
    reader_paths = [
        CASE_DIR / "research_brief.md",
        CASE_DIR / "analysis" / "c16_actual_contract_settlement_diagnostic_20260815.md",
        CASE_DIR / "analysis" / "c17_diversified_actual_contract_settlement_diagnostic_20260815.md",
        CASE_DIR / "analysis" / "c18_direct_sse_company_bond_ladder_feasibility_20260815.md",
        CASE_DIR / "analysis" / "c19_bond_historical_data_source_feasibility_20260815.md",
        CASE_DIR / "analysis" / "c20_domestic_public_reit_strategy_feasibility_20260815.md",
        CASE_DIR / "analysis" / "c21_public_reit_historical_data_route_research_20260815.md",
        CASE_DIR / "analysis" / "c22_company_bond_historical_data_route_research_20260815.md",
        CASE_DIR / "analysis" / "c23_open_ended_public_fund_data_feasibility_20260815.md",
        CASE_DIR / "analysis" / "c24_direct_ashare_equity_data_feasibility_20260815.md",
        CASE_DIR / "analysis" / "r13_r10_v1_scope_mismatch_correction_20260815.md",
        CASE_DIR / "analysis" / "r14_open_universe_feasibility_expansion_audit_20260815.md",
        CASE_DIR / "analysis" / "r07_current_open_universe_disposition_20260815.md",
        CASE_DIR / "analysis" / "c30_etf_candidate_rule_and_diagnostic_20260815.md",
        CASE_DIR / "analysis" / "c31_etf_product_diligence_refresh_20260815.md",
        CASE_DIR / "analysis" / "c32_personal_operation_and_risk_design_20260815.md",
        CASE_DIR / "analysis" / "c33_integrated_candidate_strategy_20260815.md",
        CASE_DIR / "analysis" / "c34_dual_horizon_inverse_vol_etf_candidate_20260815.md",
        CASE_DIR / "analysis" / "c35_c34_operational_action_card_20260815.md",
        CASE_DIR / "analysis" / "c36_c31_source_crosscheck_20260815.md",
        CASE_DIR / "analysis" / "c37_domestic_etf_total_return_source_route_20260815.md",
        CASE_DIR / "analysis" / "c38_direct_equity_institutional_research_route_20260815.md",
        CASE_DIR / "analysis" / "c39_independent_strategy_hypothesis_protocol_20260815.md",
        CASE_DIR / "analysis" / "c40_600519_equity_diligence_20260815.md",
        CASE_DIR / "analysis" / "c41_600900_equity_diligence_20260815.md",
        CASE_DIR / "analysis" / "c42_601088_equity_diligence_20260815.md",
        CASE_DIR / "analysis" / "c43_actual_contract_calendar_curve_protocol_20260815.md",
        CASE_DIR / "analysis" / "c44_actual_contract_calendar_curve_diagnostic_20260815.md",
        CASE_DIR / "analysis" / "c45_five_family_actual_contract_source_readiness_20260815.md",
        CASE_DIR / "analysis" / "c46_actual_contract_calendar_curve_source_control_protocol_20260815.md",
        CASE_DIR / "analysis" / "c47_source_controlled_calendar_curve_diagnostic_20260815.md",
        CASE_DIR / "analysis" / "c48_current_environment_data_capability_audit_20260815.md",
        CASE_DIR / "analysis" / "c49_official_authorized_data_route_recheck_20260815.md",
        CASE_DIR / "analysis" / "c50_sse_general_repo_yield_floor_screen_20260815.md",
        CASE_DIR / "analysis" / "c51_sse_etf_option_collar_scope_screen_20260815.md",
        CASE_DIR / "analysis" / "c52_sse_etf_option_history_route_screen_20260815.md",
        CASE_DIR / "analysis" / "c53_equity_led_domestic_target_strategy_protocol_20260815.md",
        CASE_DIR / "data" / "c53_quarterly_paper_observation_ledger_template_20260815.json",
        CASE_DIR / "data" / "c53_quarterly_paper_observation_ledger_template_20260815.csv",
        CASE_DIR / "analysis" / "r16_parallel_route_repair_plan_20260815.md",
        CASE_DIR / "analysis" / "r17_r16_repair_independent_recheck_20260815.md",
        CASE_DIR / "analysis" / "r18_c49_independent_source_audit_20260815.md",
        CASE_DIR / "analysis" / "r19_c50_independent_source_audit_20260815.md",
        CASE_DIR / "analysis" / "r20_c51_initial_independent_source_audit_20260815.md",
        CASE_DIR / "analysis" / "r20_c51_repair_plan_20260815.md",
        CASE_DIR / "analysis" / "r21_c51_repair_independent_recheck_20260815.md",
        CASE_DIR / "analysis" / "r22_c52_independent_source_audit_20260815.md",
        CASE_DIR / "analysis" / "r23_c52_governance_registration_independent_recheck_20260815.md",
        CASE_DIR / "data" / "source_registry.md",
        CASE_DIR / "data" / "claim_audit.md",
        CASE_DIR / "source_exhaustion_log.md",
        CASE_DIR / "missing_data_request_pack.md",
        CASE_DIR / "gate_manifest.md",
        CASE_DIR / "artifact_contract.md",
    ]
    hits = [str(path.relative_to(CASE_DIR)) for path in reader_paths if prohibited_pattern.search(path.read_text(encoding="utf-8"))]
    check("reader-facing amount-language exclusion", not hits, ", ".join(hits) or "no prohibited terms")

    report = {
        "schema_version": "r09_research_control_record_audit.v1",
        "artifact_id": "D5PT-R09-CONTROL-RECORD-AUDIT-v1",
        "as_of": AS_OF,
        "result": "PASS" if not failures else "FAIL",
        "result_interpretation": "control_record_consistency_only_not_route_admission",
        "scope": "source registry, claim audit, C16/C17/C18/C20/C23/C24/C34/C38/C39/C46/C50/C51/C53 ledger state, R07/R14 controls, C33-C53 integration/non-admission controls, R16/R17 repair closure, R18/R19 source audits, R20/R21 C51 repair controls, R22 C52 frozen-source audit, R23 governance-registration follow-up, source-archive integrity and reader-facing amount-language exclusion",
        "source_record_count": len(source_ids),
        "claim_count": len(claim_ids),
        "checks": checks,
        "failures": failures,
        "boundary": "A PASS is a control-record consistency result only, not route or strategy admission. This audit does not admit a strategy, select a product, calculate an investor result or authorize an external action.",
    }
    OUTPUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# R09 研究控制记录审计",
        "",
        f"- 控制记录结果：`{report['result']}`。",
        "- 范围：来源登记、主张审计、C16/C17/C18/C20/C23/C24/C34/C38/C39/C46/C50/C51 研究台账、R07/R14 来源控制、C33--C52 整合/未准入控制、R16/R17 修复关闭、R18/R19 来源审计、R20/R21 C51 修复控制、R22 C52 冻结来源审计、R23 治理登记后续复核、逐股来源归档完整性、研究阻断治理与读者材料中的金额表述排除。",
        "- PASS 只表示控制记录一致，不是路线或策略准入；不选择产品、不计算投资者结果，也不产生外部动作。",
        "",
        "| 检查 | 结果 | 说明 |",
        "|---|---|---|",
    ]
    for item in checks:
        lines.append(f"| {item['name']} | {'PASS' if item['passed'] else 'FAIL'} | {item['detail']} |")
    if failures:
        lines.extend(["", "## 失败项", "", *[f"- {failure}" for failure in failures]])
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"R09 RESEARCH CONTROL RECORD AUDIT: {report['result']}")
    for failure in failures:
        print(f"- {failure}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
