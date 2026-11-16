#!/usr/bin/env python3
"""Verify the open-universe total-return allocation research case.

The verifier validates the case's declared artifact graph, primary-source
archive, cash-accounting boundary, T1-to-T4 admission controls and final
render identity. It intentionally treats implementation as a research
boundary: every market-traded candidate remains q=0 until a later, dated T2
decision universe, item dossier and portfolio packet clear independently.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


CASE_DIR = (
    Path(sys.argv[1]).resolve()
    if len(sys.argv) > 1
    else Path(__file__).resolve().parents[1]
)
RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    RESULTS.append((name, condition, detail))


def relpath(rel: str) -> Path:
    return CASE_DIR / rel


def exists(rel: str) -> None:
    check(f"exists {rel}", relpath(rel).is_file(), "" if relpath(rel).is_file() else "missing")


def load_json(rel: str) -> Any:
    target = relpath(rel)
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:
        check(f"json parses {rel}", False, str(exc))
        return {}
    check(f"json parses {rel}", True)
    return payload


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def rows(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def sha256_file(rel: str) -> str:
    return hashlib.sha256(relpath(rel).read_bytes()).hexdigest()


def source_graph_sha256(rels: list[str]) -> str:
    digest = hashlib.sha256()
    for rel in rels:
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(relpath(rel).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def inventory_records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [item for item in rows(payload.get("files")) if isinstance(item, Mapping)]


def inventory_matches_files(records: list[Mapping[str, Any]]) -> bool:
    for record in records:
        rel = str(record.get("relative_path") or record.get("file") or "")
        if not rel or not relpath(rel).is_file():
            return False
        if record.get("size_bytes") != relpath(rel).stat().st_size:
            return False
        expected_sha = str(record.get("sha256") or "")
        if expected_sha and sha256_file(rel) != expected_sha:
            return False
    return True


def main() -> int:
    check("case directory", CASE_DIR.is_dir(), str(CASE_DIR))
    if not CASE_DIR.is_dir():
        return finish()

    required = (
        "research_brief.md",
        "gate_manifest.json",
        "artifact_contract.json",
        "data/source_registry.json",
        "data/claim_audit.json",
        "data/portfolio_return_model_20260812.json",
        "data/return_evidence_20260812.json",
        "analysis/return_evidence.md",
        "data/risk_budget_20260812.json",
        "analysis/execution_protocol.md",
        "data/reit_candidate_pool_20260812.json",
        "data/execution_eligibility_policy_20260812.json",
        "sources/official-20260812/manifest.json",
        "main.tex",
        "main.pdf",
        "data/main_text_20260812.txt",
        "visual_review.md",
        "completion_audit_manifest.json",
        "completion_audit_manifest.md",
        "data_room_index.md",
        "data/report_quality_eval.json",
        "data/report_quality_eval.md",
        "data/core_artifact_checksums_20260814.json",
        "data/core_artifact_checksums_20260814.md",
        "data/root_artifact_inventory_20260814.json",
        "data/root_artifact_inventory_20260814.md",
        "data/top_level_data_artifact_inventory_20260814.json",
        "data/top_level_data_artifact_inventory_20260814.md",
        "final_signoff.json",
        "research_workflow_eval.json",
        "analysis/variant_perception.md",
        "analysis/exhibit_plan.md",
    )
    for rel in required:
        exists(rel)

    manifest = mapping(load_json("gate_manifest.json"))
    contract = mapping(load_json("artifact_contract.json"))
    source_registry = rows(load_json("data/source_registry.json"))
    claims = rows(load_json("data/claim_audit.json"))
    model = mapping(load_json("data/portfolio_return_model_20260812.json"))
    return_evidence = mapping(load_json("data/return_evidence_20260812.json"))
    risk_budget = mapping(load_json("data/risk_budget_20260812.json"))
    candidates = mapping(load_json("data/reit_candidate_pool_20260812.json"))
    eligibility = mapping(load_json("data/execution_eligibility_policy_20260812.json"))
    source_manifest = mapping(load_json("sources/official-20260812/manifest.json"))
    signoff = mapping(load_json("final_signoff.json"))
    workflow = mapping(load_json("research_workflow_eval.json"))
    completion_audit = mapping(load_json("completion_audit_manifest.json"))
    report_quality = mapping(load_json("data/report_quality_eval.json"))
    core_checksums = mapping(load_json("data/core_artifact_checksums_20260814.json"))
    root_inventory = mapping(load_json("data/root_artifact_inventory_20260814.json"))
    data_inventory = mapping(load_json("data/top_level_data_artifact_inventory_20260814.json"))

    scope_id = str(manifest.get("scope_id") or "")
    active_sections = [str(item) for item in rows(manifest.get("active_section_paths"))]
    main_source = relpath("main.tex").read_text(encoding="utf-8", errors="ignore") if relpath("main.tex").exists() else ""
    parsed_sections = [
        raw if raw.endswith(".tex") else f"{raw}.tex"
        for raw in re.findall(r"\\input\{(sections/[^}]+)\}", main_source)
    ]

    check("strategic allocation profile", manifest.get("case_profile") == "strategic_allocation")
    check("scope ID declared", bool(scope_id), scope_id)
    check("manifest and contract scope IDs match", bool(scope_id) and contract.get("scope_id") == scope_id)
    check("main section graph matches manifest", parsed_sections == active_sections, f"main={parsed_sections}")
    check("active section inputs unique", len(parsed_sections) == len(set(parsed_sections)))
    for rel in active_sections:
        exists(rel)

    source_ids = {str(row.get("source_id")) for row in source_registry if isinstance(row, Mapping)}
    claim_source_ids = {
        str(source_id)
        for claim in claims
        if isinstance(claim, Mapping) and claim.get("active_scope") is not False
        for source_id in rows(claim.get("source_ids"))
    }
    check("active claims resolve to registered sources", bool(claim_source_ids) and claim_source_ids <= source_ids)
    check("source registry is primary-source tier", all(
        isinstance(row, Mapping) and str(row.get("quality_tier") or "").startswith("tier_1")
        for row in source_registry
    ), f"sources={len(source_registry)}")

    manifest_records = {str(item.get("source_id")): item for item in rows(source_manifest.get("files")) if isinstance(item, Mapping)}
    check("source archive covers registered IDs", source_ids == set(manifest_records), f"registry={len(source_ids)} archive={len(manifest_records)}")
    archive_errors = []
    for row in source_registry:
        if not isinstance(row, Mapping):
            archive_errors.append("non-object registry row")
            continue
        source_id = str(row.get("source_id") or "")
        local_path = str(row.get("local_path") or "")
        record = mapping(manifest_records.get(source_id))
        if not local_path or not relpath(local_path).is_file() or record.get("file") != Path(local_path).name:
            archive_errors.append(f"{source_id}:path")
            continue
        if sha256_file(local_path) != record.get("sha256"):
            archive_errors.append(f"{source_id}:sha256")
    check("source archive bytes match manifest hashes", not archive_errors, ", ".join(archive_errors[:6]))

    allocations = [row for row in rows(model.get("post_approval_reference_vector")) if isinstance(row, Mapping)]
    total_weight = sum(float(row.get("weight") or 0) for row in allocations)
    current_core = [row for row in rows(model.get("active_base_core")) if isinstance(row, Mapping)]
    current_core_weight = sum(float(row.get("weight") or 0) for row in current_core)
    current_state = mapping(model.get("current_state"))
    check("open universe has no pre-approved allocation vector", not allocations and total_weight == 0, f"rows={len(allocations)}")
    check("scale-neutral model declares no funding or account-holding assumption", model.get("portfolio_size_assumption") and current_state.get("approved_model_allocation") == "none" and current_state.get("account_holding_inference") == "none")
    check("notional fallback reference weights reconcile to 100%", abs(current_core_weight - 1.0) < 1e-9 and all(row.get("notional_only") is True for row in current_core), f"{current_core_weight:.6f}")
    serialized_model = json.dumps(model, ensure_ascii=False).lower()
    check("model has no fixed-scale arithmetic", all(token not in serialized_model for token in ("annual_cny200k", "amount_cny", "200000", "cny200,000")))

    controls = mapping(manifest.get("strategy_controls"))
    activation = mapping(model.get("activation_controls"))
    direct_activation = mapping(activation.get("direct_equities"))
    reit_activation = mapping(activation.get("public_reits"))
    universe = mapping(model.get("open_research_universe"))
    direct_review = rows(direct_activation.get("required_independent_review"))
    check("open-universe policy is declared", controls.get("research_universe_mode") == "open_with_item_level_admission" and "open" in str(controls.get("research_universe_policy") or "").lower())
    check("T1-to-T4 admission chain is declared", all(str(universe.get(key) or "").strip() for key in ("T0_research_boundary", "T1_open_research_universe", "T2_decision_universe", "T3_approved_investable_universe", "T4_approved_portfolio")))
    check("direct equities remain q=0 without being permanently excluded", controls.get("initial_direct_stock_weight") == 0.0 and controls.get("direct_stock_aggregate_cap") is None and controls.get("direct_stock_single_issuer_cap") is None and controls.get("named_t3_direct_equity_count") == 0 and len(direct_review) >= 8)
    check("no leverage or derivatives are permitted", all(model.get("risk_controls", {}).get(key) is True for key in ("no_leverage", "no_futures_or_options", "no_margin_financing")))
    check("REITs start at zero eligibility", controls.get("reit_initial_weight") == 0.0 and reit_activation.get("initial_weight") == 0.0)
    required_projects = int(controls.get("reit_required_independent_projects") or 0)
    check("REIT admission remains non-forcing", required_projects >= 5 and controls.get("reit_aggregate_cap_after_activation") is None and reit_activation.get("aggregate_cap") is None)
    check("REIT model controls reconcile", reit_activation.get("minimum_independent_projects") == required_projects and len(rows(reit_activation.get("required_checks"))) >= 7 and "protected liquidity" in str(reit_activation.get("inactive_behavior") or "").lower())

    candidate_rows = [row for row in rows(candidates.get("candidates")) if isinstance(row, Mapping)]
    sectors = {str(row.get("sector")) for row in candidate_rows}
    managers = {str(row.get("manager")) for row in candidate_rows}
    check("REIT pool has at least five independent candidates", len(candidate_rows) >= required_projects and len(sectors) >= 5 and len(managers) >= 5, f"candidates={len(candidate_rows)} sectors={len(sectors)} managers={len(managers)}")
    check("all REIT candidates remain watch-only", all(row.get("eligibility") == "watch_only_pending_current_validation" for row in candidate_rows))

    cash_ledger = mapping(model.get("cash_ledger_and_accounting"))
    total_return_measurement = mapping(model.get("total_return_measurement"))
    excluded = " ".join(str(item).lower() for item in rows(cash_ledger.get("not_receipt_types")))
    check("cash ledger excludes sales, gains, NAV and external cash", all(token in excluded for token in ("asset sale", "unrealized", "nav", "external")))
    check("cash objective is explicitly not required", controls.get("cash_objective_required") is False)
    check("cash ledger has no standalone target mechanics", all(token not in serialized_model for token in ("cash_target_pct", "net_cash_yield_formula", "covered_net_cash_formula", "cash_target_failure", "rolling_twelve_month_actual_net_cash_target_pct", "b2_income")))
    capital_like = str(cash_ledger.get("capital_repayment_like_component") or "").lower()
    check("capital-repayment-like receipt needs separate treatment", "flag" in capital_like and "not labelled investment return" in capital_like)
    cash_policy = mapping(model.get("cash_distribution_policy"))
    check("cash use is separate from receipt eligibility", cash_policy.get("default_use") is None and str(cash_policy.get("cash_use_instruction") or "").startswith("none") and cash_policy.get("automatic_reinvestment") is False and cash_policy.get("mandatory_retention") is False and {"retain", "withdraw", "no_action"} <= {str(item) for item in rows(cash_policy.get("cash_use_options_without_market_allocation"))} and "dated" in str(cash_policy.get("new_market_allocation_requirement") or "").lower())
    check("total-return policy uses TWRR and MWRR", total_return_measurement.get("strategy_measure") == "TWRR" and total_return_measurement.get("investor_measure") == "MWRR_XIRR" and "flow" in str(total_return_measurement.get("subperiod_formula") or "").lower())
    check("total-return policy forbids double count", "once" in str(total_return_measurement.get("cash_receipt_accounting_rule") or "").lower() and "second return" in str(total_return_measurement.get("cash_receipt_accounting_rule") or "").lower())
    check("return evidence remains an explicit implementation blocker", str(mapping(return_evidence.get("gate")).get("status") or "").lower() == "fail" and str(mapping(return_evidence.get("gate")).get("formal_backtest_status") or "").lower() == "not_run_blocked")
    check("risk budget remains not approved at q=0", risk_budget.get("status") == "not_approved" and mapping(risk_budget.get("current_state")).get("portfolio_q") == 0 and mapping(risk_budget.get("planning_common_stress")).get("known_sleeves_subtotal_pct") == -25.0)
    check("retired vector does not use an unapproved diversifier", mapping(mapping(risk_budget.get("planning_common_stress")).get("defensive_diversifier")).get("status") == "undefined_q_0")

    sleeve_controls = mapping(eligibility.get("sleeve_controls"))
    check("execution policy remains not run", eligibility.get("status") == "not_run" and eligibility.get("execution_authorization") == "none")
    check("all named market candidate classes remain q=0", all(mapping(sleeve_controls.get(key)).get("q") == 0 for key in ("511010", "510880", "direct_equities", "public_reits", "sovereign_or_cash_candidates")))
    failure = mapping(eligibility.get("failure_waterfall"))
    check("failed eligibility does not infer an account holding", "no_model_allocation" in str(failure.get("destination") or "") and "remains" in str(failure.get("reit_force_fill_rule") or "").lower())

    current_source_sha = sha256_file("main.tex") if relpath("main.tex").is_file() else ""
    current_graph_sha = source_graph_sha256(["main.tex", *active_sections]) if active_sections and relpath("main.tex").is_file() else ""
    pdf_sha = sha256_file("main.pdf") if relpath("main.pdf").is_file() else ""
    text_sha = sha256_file("data/main_text_20260812.txt") if relpath("data/main_text_20260812.txt").is_file() else ""
    page_count = 0
    if relpath("main.pdf").is_file():
        info = subprocess.run(["pdfinfo", "main.pdf"], cwd=CASE_DIR, text=True, capture_output=True, check=False)
        match = re.search(r"^Pages:\s*(\d+)", info.stdout, re.MULTILINE)
        page_count = int(match.group(1)) if match else 0
    check("PDF has a readable multi-page render", page_count >= 10, str(page_count))
    check("sign-off source identity matches", signoff.get("reviewed_source_sha256") == current_source_sha and signoff.get("reviewed_source_graph_sha256") == current_graph_sha)
    check("sign-off PDF and text identities match", signoff.get("pdf_sha256") == pdf_sha and signoff.get("text_sha256") == text_sha and signoff.get("page_count") == page_count)
    visual = relpath("visual_review.md").read_text(encoding="utf-8", errors="ignore") if relpath("visual_review.md").is_file() else ""
    check("visual review is hash-bound and passed", "Status: PASS" in visual and current_source_sha in visual and current_graph_sha in visual)
    quality = mapping(workflow.get("quality"))
    blocking_failure_count = quality.get("blocking_failure_count")
    check(
        "workflow evaluation is current and publishable",
        workflow.get("scope_id") == scope_id
        and quality.get("publishable") is True
        and isinstance(blocking_failure_count, int)
        and blocking_failure_count == 0,
    )
    check("workflow is scoped framework-only status", quality.get("status") == "RESEARCH_FRAMEWORK_PASS_IMPLEMENTATION_NOT_APPROVED" and quality.get("implementation_status") == "NOT_APPROVED")

    check("completion audit preserves implementation boundary", completion_audit.get("scope_id") == scope_id and completion_audit.get("decision") == "do_not_mark_complete" and completion_audit.get("publication_status") == "research_framework_pass_implementation_not_approved")
    check("report quality records current PDF facts", report_quality.get("scope_id") == scope_id and report_quality.get("pages") == page_count and report_quality.get("pdf_sha256") == pdf_sha and report_quality.get("source_sha256") == current_source_sha)
    core_records = inventory_records(core_checksums)
    root_records = inventory_records(root_inventory)
    data_records = inventory_records(data_inventory)
    check("core artifact checksum manifest is current", core_checksums.get("scope_id") == scope_id and core_checksums.get("file_count") == len(core_records) and bool(core_records) and inventory_matches_files(core_records))
    check("root artifact inventory is current", root_inventory.get("scope_id") == scope_id and root_inventory.get("root_files") == len(root_records) and bool(root_records) and inventory_matches_files(root_records))
    check("top-level data inventory is current", data_inventory.get("scope_id") == scope_id and data_inventory.get("top_level_data_files") == len(data_records) and bool(data_records) and inventory_matches_files(data_records))
    data_room = relpath("data_room_index.md").read_text(encoding="utf-8", errors="ignore") if relpath("data_room_index.md").is_file() else ""
    check("data room index records current release boundary", scope_id in data_room and "cash-receipt objective" in data_room and "q=0" in data_room)

    implementation_gates = mapping(signoff.get("implementation_gates"))
    check("scoped framework sign-off is explicit", signoff.get("signoff_status") == "RESEARCH_FRAMEWORK_PASS" and signoff.get("framework_status") == "PASS" and signoff.get("implementation_status") == "NOT_APPROVED" and signoff.get("live_execution_authorized") is False)
    check("four implementation gates remain blocked", all(str(implementation_gates.get(key) or "").upper() in {"BLOCKED_PENDING_FORMAL_TEST", "NOT_APPROVED", "PENDING", "NOT_AUTHORIZED"} for key in ("return_evidence", "risk_budget", "suitability", "execution")))

    reader_text = relpath("data/main_text_20260812.txt").read_text(encoding="utf-8", errors="ignore") if relpath("data/main_text_20260812.txt").is_file() else ""
    check("reader draft rejects annual guarantee language", "年度最低收益" in reader_text and "不构成证券买卖建议" in reader_text)
    check("reader draft identifies current non-action and implementation block", all(token in reader_text for token in ("510880", "508069", "q = 0", "实施未获批准", "回报证据")))
    check("reader draft has no retired funding, compulsory-cash or cash-target language", all(token not in reader_text for token in ("本金", "CNY200,000", "200000", "复投规则", "3%现金", "3\\%现金", "现金目标", "现金覆盖", "现金命中率", "B0/B1/B2")))

    return finish()


def finish() -> int:
    for name, passed, detail in RESULTS:
        print(f"{'PASS' if passed else 'FAIL'} {name}{': ' + detail if detail else ''}")
    failures = sum(1 for _, passed, _ in RESULTS if not passed)
    print(f"SUMMARY {len(RESULTS) - failures} PASS / {failures} FAIL")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
