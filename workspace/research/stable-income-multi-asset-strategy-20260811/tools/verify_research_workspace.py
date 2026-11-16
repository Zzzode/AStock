#!/usr/bin/env python3
"""Integrity checks for the strategic-allocation research case.

The verifier checks the declared active artifact graph rather than accepting a
legacy chapter list. Publication checks intentionally remain red until an
identity-matched XeLaTeX build with recorded provenance and independent review
are available.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
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


def path(rel: str) -> Path:
    return CASE_DIR / rel


def exists(rel: str) -> None:
    target = path(rel)
    check(f"exists {rel}", target.exists(), "" if target.exists() else "missing")


def load_json(rel: str) -> Any:
    target = path(rel)
    if not target.exists():
        check(f"json parses {rel}", False, "missing")
        return {}
    try:
        payload = json.loads(target.read_text(encoding="utf-8"))
    except Exception as exc:  # deliberate: surface malformed audit artifacts
        check(f"json parses {rel}", False, str(exc))
        return {}
    check(f"json parses {rel}", True)
    return payload


def as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def is_positive_number(value: Any) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and math.isfinite(float(value))
        and float(value) > 0
    )


def is_explicit_declaration(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value) and any(is_explicit_declaration(item) for item in value.values())
    if isinstance(value, list):
        return bool(value) and all(is_explicit_declaration(item) for item in value)
    return False


def text_near_anchor(
    text: str,
    anchors: tuple[str, ...],
    term_groups: tuple[tuple[str, ...], ...],
    window: int = 500,
) -> bool:
    folded = text.casefold()
    for anchor in anchors:
        folded_anchor = anchor.casefold()
        start = 0
        while (position := folded.find(folded_anchor, start)) >= 0:
            context = folded[max(0, position - window) : position + len(folded_anchor) + window]
            if all(any(term.casefold() in context for term in group) for group in term_groups):
                return True
            start = position + len(folded_anchor)
    return False


def source_sha256(rel: str) -> str:
    return hashlib.sha256(path(rel).read_bytes()).hexdigest()


def source_graph_sha256(rels: list[str]) -> str:
    digest = hashlib.sha256()
    for rel in rels:
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path(rel).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def parse_active_inputs(main_source: str) -> list[str]:
    inputs = []
    for raw in re.findall(r"\\input\{([^}]+)\}", main_source):
        if not raw.startswith("sections/"):
            continue
        inputs.append(raw if raw.endswith(".tex") else f"{raw}.tex")
    return inputs


def main() -> int:
    check("case directory", CASE_DIR.is_dir(), str(CASE_DIR))
    if not CASE_DIR.is_dir():
        return finish()

    for rel in (
        "research_brief.md",
        "gate_manifest.md",
        "artifact_contract.md",
        "data/source_registry.md",
        "data/claim_audit.md",
        "source_exhaustion_log.md",
        "analysis/template_brief.md",
        "analysis/allocation_model.md",
        "analysis/scenario_model.md",
        "analysis/cashflow_and_tax.md",
        "analysis/risk_framework.md",
        "analysis/implementation_checklist.md",
        "analysis/valuation_model.md",
        "analysis/valuation_audit.md",
        "analysis/delta_audit.md",
        "main.tex",
        "final_signoff.md",
        "visual_review.md",
        "research_workflow_eval.md",
        "data/raw_market_data_20260811.md",
        "data/verified_market_data_20260811.md",
        "data/execution_eligibility_policy_20260812.json",
    ):
        exists(rel)

    manifest = as_mapping(load_json("gate_manifest.json"))
    contract = as_mapping(load_json("artifact_contract.json"))
    source_registry = as_list(load_json("data/source_registry.json"))
    claim_audit = as_list(load_json("data/claim_audit.json"))
    return_model = as_mapping(load_json("data/portfolio_return_model_20260811.json"))
    execution_policy = as_mapping(load_json("data/execution_eligibility_policy_20260812.json"))
    stock_pool = as_mapping(load_json("data/high_dividend_stock_pool_20260811.json"))
    source_archive_status = as_mapping(load_json("data/source_archive_status.json"))
    final_signoff = as_mapping(load_json("final_signoff.json"))
    workflow_eval = as_mapping(load_json("research_workflow_eval.json"))

    expected_profile = "strategic_allocation"
    scope_id = str(manifest.get("scope_id") or "")
    check("strategic-allocation profile", manifest.get("case_profile") == expected_profile)
    check("scope ID declared", bool(scope_id), scope_id)
    check("manifest/contract scope ID parity", bool(scope_id) and contract.get("scope_id") == scope_id)

    for rel in ("gate_manifest.md", "artifact_contract.md"):
        text = path(rel).read_text(encoding="utf-8") if path(rel).exists() else ""
        check(f"scope ID mirrored in {rel}", bool(scope_id) and scope_id in text)

    main_source = path("main.tex").read_text(encoding="utf-8") if path("main.tex").exists() else ""
    parsed_sections = parse_active_inputs(main_source)
    declared_sections = [str(item) for item in as_list(manifest.get("active_section_paths"))]
    check("main.tex declares active section inputs", bool(parsed_sections), ", ".join(parsed_sections))
    check("main.tex active inputs unique", len(parsed_sections) == len(set(parsed_sections)))
    check(
        "manifest section graph equals main.tex inputs",
        parsed_sections == declared_sections,
        f"main={parsed_sections}; manifest={declared_sections}",
    )
    for rel in declared_sections:
        exists(rel)
    legacy_sections = {
        "sections/ch02_objectives.tex",
        "sections/ch03_architecture.tex",
        "sections/ch04_product_mechanics.tex",
        "sections/ch05_cashflow.tex",
        "sections/ch06_allocation.tex",
        "sections/ch08_implementation.tex",
        "sections/app_source_audit.tex",
    }
    check("no legacy-only chapter appears in active graph", not (set(parsed_sections) & legacy_sections))

    source_ids = {str(row.get("source_id")) for row in source_registry if isinstance(row, Mapping)}
    active_archive = as_mapping(source_archive_status.get("active_scope"))
    active_source_ids = {str(item) for item in as_list(active_archive.get("source_ids"))}
    active_registry_ids = {
        str(row.get("source_id"))
        for row in source_registry
        if isinstance(row, Mapping) and row.get("active_scope") is True
    }
    active_claims = [
        claim
        for claim in claim_audit
        if isinstance(claim, Mapping) and claim.get("active_scope") is not False
    ]
    unresolved_ids = []
    for claim in active_claims:
        for source_id in as_list(claim.get("source_ids")):
            if str(source_id) not in active_source_ids:
                unresolved_ids.append(f"{claim.get('claim_id')}:{source_id}")
    check(
        "active claim-audit source IDs resolve to active archive scope",
        not unresolved_ids and active_source_ids == active_registry_ids,
        ", ".join(unresolved_ids)
        + f"; archive={sorted(active_source_ids)}; registry={sorted(active_registry_ids)}",
    )
    retired_claims = [
        claim
        for claim in claim_audit
        if isinstance(claim, Mapping) and claim.get("active_scope") is False
    ]
    retired_ids = {
        str(item)
        for item in as_list(as_mapping(source_archive_status.get("legacy_context")).get("retired_source_ids"))
    }
    retired_claim_ids = {
        str(source_id)
        for claim in retired_claims
        for source_id in as_list(claim.get("source_ids"))
    }
    check(
        "retired source claims are excluded from active scope",
        bool(retired_claims)
        and retired_claim_ids.issubset(retired_ids)
        and retired_ids.isdisjoint(active_source_ids),
        f"retired_claim_ids={sorted(retired_claim_ids)}; retired_ids={sorted(retired_ids)}",
    )

    controls = as_mapping(manifest.get("strategy_controls"))
    check("initial direct-stock weight is zero", controls.get("initial_direct_stock_weight") == 0.0)
    check("direct-stock aggregate cap is 15%", controls.get("direct_stock_aggregate_cap") == 0.15)
    check("direct-stock single-issuer cap is 5%", controls.get("direct_stock_single_issuer_cap") == 0.05)
    check("REIT initial weight is zero", controls.get("reit_initial_weight") == 0.0)
    check("issuer target-price policy is none", controls.get("issuer_target_price_policy") == "none")

    policy_thresholds = as_mapping(execution_policy.get("thresholds"))
    failure_waterfall = as_mapping(execution_policy.get("failure_waterfall"))
    record_requirements = as_mapping(execution_policy.get("record_requirements"))
    freshness_policy = as_mapping(execution_policy.get("freshness_policy"))
    sleeve_controls = as_mapping(execution_policy.get("sleeve_controls"))
    check("execution-eligibility policy status is not_run", execution_policy.get("status") == "not_run")

    fallback_result = str(failure_waterfall.get("failed_or_missing_check_result") or "").casefold()
    fallback_destination = str(failure_waterfall.get("destination") or "").casefold()
    staging_cash_rule = re.sub(
        r"[\s,]", "", str(failure_waterfall.get("staging_cash_rule") or "").casefold()
    )
    check(
        "execution policy has deterministic protected-liquidity fallback and CNY10000 staging cap",
        "q_0" in fallback_result
        and ("no_trade" in fallback_result or "no trade" in fallback_result)
        and "protected" in fallback_destination
        and "liquidity" in fallback_destination
        and policy_thresholds.get("staging_cash_hard_cap_cny") == 10000
        and "10000" in staging_cash_rule
        and (
            "never" in staging_cash_rule
            or "atorbelow" in staging_cash_rule
            or "notexceed" in staging_cash_rule
            or "不超过" in staging_cash_rule
        ),
        f"destination={failure_waterfall.get('destination')}; cap={policy_thresholds.get('staging_cash_hard_cap_cny')}",
    )

    market_threshold_fields = (
        "premium_discount_abs_max_pct",
        "quoted_spread_max_pct_of_mid",
        "proposed_tranche_max_pct_of_same_session_traded_value_or_executable_depth",
    )
    check(
        "execution policy has explicit ETF premium/discount, spread and liquidity thresholds",
        all(is_positive_number(policy_thresholds.get(field)) for field in market_threshold_fields),
        ", ".join(
            f"{field}={policy_thresholds.get(field)!r}" for field in market_threshold_fields
        ),
    )

    named_etf_controls = ("511010", "510880", "512890", "518880")
    missing_etf_control_checks: list[str] = []
    for ticker in named_etf_controls:
        required_checks = {
            str(item) for item in as_list(as_mapping(sleeve_controls.get(ticker)).get("required_checks"))
        }
        missing = {"premium_discount", "spread", "liquidity"} - required_checks
        if missing:
            missing_etf_control_checks.append(f"{ticker}:{','.join(sorted(missing))}")
    check(
        "named ETF controls require premium/discount, spread and liquidity checks",
        not missing_etf_control_checks,
        "; ".join(missing_etf_control_checks),
    )

    common_record_fields = {
        str(item) for item in as_list(record_requirements.get("common_fields"))
    }
    required_current_session_fields = {
        "validation_date",
        "market_session",
        "source_name",
        "source_locator",
        "capture_timestamp",
        "market_price_timestamp",
        "iopv_or_reference_timestamp",
    }
    market_field_freshness = str(freshness_policy.get("market_fields") or "").casefold()
    check(
        "execution policy requires current-session sourced and timestamped ETF records",
        required_current_session_fields.issubset(common_record_fields)
        and "same" in market_field_freshness
        and "session" in market_field_freshness,
        "missing="
        + ", ".join(sorted(required_current_session_fields - common_record_fields))
        + f"; market_fields={freshness_policy.get('market_fields')!r}",
    )

    combined_holdings_fields = {
        str(item) for item in as_list(record_requirements.get("combined_holdings_fields"))
    }
    secondary_etf_checks = {
        str(item)
        for item in as_list(as_mapping(sleeve_controls.get("512890")).get("required_checks"))
    }
    check(
        "execution policy enforces 25% portfolio and 35% equity-sleeve combined-holdings caps",
        policy_thresholds.get("combined_sector_max_pct_of_total_portfolio") == 25.0
        and policy_thresholds.get("top_ten_issuer_group_max_pct_of_equity_sleeve") == 35.0
        and {
            "fund_holdings_as_of",
            "holdings_source_locator",
            "combined_sector_weight_of_total_portfolio_pct",
            "top_ten_issuer_group_weight_of_equity_sleeve_pct",
        }.issubset(combined_holdings_fields)
        and "dated_combined_holdings_look_through" in secondary_etf_checks,
        "sector_cap="
        f"{policy_thresholds.get('combined_sector_max_pct_of_total_portfolio')}; issuer_cap="
        f"{policy_thresholds.get('top_ten_issuer_group_max_pct_of_equity_sleeve')}",
    )

    base_core = [row for row in as_list(return_model.get("active_base_core")) if isinstance(row, Mapping)]
    total_weight = sum(float(row.get("weight") or 0.0) for row in base_core)
    check("return-model base weights sum to 100%", abs(total_weight - 1.0) < 1e-9, f"{total_weight:.6f}")
    direct_rows = [row for row in base_core if row.get("asset") == "直接高股息股票"]
    check(
        "return-model direct-stock weight is zero",
        len(direct_rows) == 1 and direct_rows[0].get("weight") == 0.0,
        f"rows={len(direct_rows)}",
    )
    check(
        "return model is planning range rather than point forecast",
        str(return_model.get("model_type", "")).startswith("strategic allocation planning range"),
    )
    check(
        "return model declares formula-only total-return sensitivity",
        is_explicit_declaration(return_model.get("formula_only_total_return_sensitivity")),
    )
    check(
        "return model declares actual-cash ledger contract",
        is_explicit_declaration(return_model.get("actual_cash_ledger_contract")),
    )
    activation_controls = as_mapping(return_model.get("activation_controls"))
    direct_activation = as_mapping(activation_controls.get("direct_high_dividend_stocks"))
    direct_review = as_list(direct_activation.get("required_independent_review"))
    check(
        "return-model direct-stock activation controls reconcile",
        direct_activation.get("initial_weight") == controls.get("initial_direct_stock_weight")
        and "红利权益ETF" in str(direct_activation.get("only_replaces") or "")
        and direct_activation.get("aggregate_cap") == controls.get("direct_stock_aggregate_cap")
        and direct_activation.get("single_issuer_cap") == controls.get("direct_stock_single_issuer_cap")
        and len(direct_review) >= 7,
    )
    reit_activation = as_mapping(activation_controls.get("public_reits"))
    reit_checks = as_list(reit_activation.get("required_checks"))
    check(
        "return-model REIT activation controls reconcile",
        reit_activation.get("initial_weight") == controls.get("reit_initial_weight")
        and reit_activation.get("activation_requires_independent_projects")
        == controls.get("reit_required_independent_projects")
        and reit_activation.get("per_project_cap") == controls.get("reit_single_project_cap")
        and reit_activation.get("aggregate_cap") == controls.get("reit_aggregate_cap_after_activation")
        and "高质量人民币利率债" in str(reit_activation.get("funding_source_on_activation") or "")
        and len(reit_checks) >= 7,
    )
    cash_policy = as_mapping(return_model.get("cash_distribution_policy"))
    actual_measure = str(cash_policy.get("actual_measure") or "")
    check(
        "return-model D0 cash policy",
        "D0" in actual_measure
        and "past-12-month" in actual_measure
        and "after-tax" in actual_measure
        and "after-fee" in actual_measure
        and cash_policy.get("forward_fixed_distribution_cny") is None
        and "reinvest" in str(cash_policy.get("default_use") or "").lower(),
    )
    check("stock-pool direct-stock weight is zero", stock_pool.get("active_direct_stock_weight") == 0.0)
    check(
        "historical stock-pool packet is retired from active scope",
        stock_pool.get("active_scope") is False
        and stock_pool.get("scope_status") == "retired_from_active_scope"
        and "retired_from_active_scope" in str(stock_pool.get("use_in_conclusion") or ""),
    )

    scenario_text = (
        path("analysis/scenario_model.md").read_text(encoding="utf-8")
        if path("analysis/scenario_model.md").exists()
        else ""
    )
    observed_drawdown_is_defined = text_near_anchor(
        scenario_text,
        ("observed drawdown", "观测回撤", "实际回撤"),
        (
            ("defined as", "definition", "means", "is measured", "is calculated", "定义为", "定义", "指", "计算为"),
            ("peak", "high-water", "high water", "maximum", "峰值", "最高", "高水位"),
            ("current", "latest", "verified", "net asset", "portfolio value", "当前", "最新", "净值", "组合价值"),
        ),
    )
    check(
        "scenario model defines observed drawdown from a peak to current verified value",
        observed_drawdown_is_defined,
    )
    scenario_stress_is_not_a_live_action = text_near_anchor(
        scenario_text,
        ("scenario stress", "stress scenario", "情景压力", "压力情景"),
        (
            ("does not trigger", "do not trigger", "never trigger", "not trigger", "不触发", "不会触发", "不得触发"),
            (
                "live drawdown action",
                "observed drawdown action",
                "actual drawdown action",
                "live-drawdown action",
                "实际回撤行动",
                "观测回撤行动",
                "实时回撤行动",
            ),
        ),
    )
    check(
        "scenario stress does not trigger a live drawdown action",
        scenario_stress_is_not_a_live_action,
    )

    tex_paths = [path("main.tex"), *(path("sections").glob("*.tex"))]
    unescaped_percent = []
    for tex_path in tex_paths:
        for number, line in enumerate(tex_path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"(?<!\\)%", line) and not line.lstrip().startswith("%"):
                unescaped_percent.append(f"{tex_path.name}:{number}")
    check("TeX percent signs escaped", not unescaped_percent, ", ".join(unescaped_percent[:5]))

    old_reader_model = (
        "高股息个股（8只） & 30\\%" in main_source
        or "组合预期年化总收益4.7" in main_source
        or "CNY7,060" in main_source
    )
    check("main reader source excludes legacy direct-stock model", not old_reader_model)

    archive_status = str(source_archive_status.get("status") or "").lower()
    check(
        "primary-source archive complete for active scope",
        archive_status == "complete_for_active_scope"
        and active_archive.get("archive_status") == "complete_for_active_scope"
        and active_archive.get("success_count") == active_archive.get("source_id_count")
        and active_archive.get("partial_count") == 0
        and active_archive.get("failed_count") == 0,
        archive_status or "missing status",
    )
    declared_success_ids = {str(item) for item in as_list(active_archive.get("success_source_ids"))}
    archive_records: dict[str, Mapping[str, Any]] = {}
    archive_manifest_errors: list[str] = []
    for batch in as_list(active_archive.get("archive_batches")):
        if not isinstance(batch, Mapping):
            archive_manifest_errors.append("invalid batch record")
            continue
        manifest_rel = str(batch.get("manifest") or "")
        manifest = as_mapping(load_json(manifest_rel)) if manifest_rel else {}
        if not manifest_rel or not manifest:
            archive_manifest_errors.append(f"missing manifest:{manifest_rel or 'none'}")
            continue
        for record in as_list(manifest.get("records")):
            if not isinstance(record, Mapping):
                archive_manifest_errors.append(f"invalid record:{manifest_rel}")
                continue
            source_id = str(record.get("source_id") or "")
            if source_id:
                archive_records[source_id] = record

    missing_success_records = sorted(
        source_id
        for source_id in declared_success_ids
        if source_id not in archive_records
        or str(archive_records[source_id].get("archive_status") or "").lower() != "success"
    )
    check(
        "source archive manifests cover declared successful IDs",
        not archive_manifest_errors and not missing_success_records,
        "; ".join([*archive_manifest_errors, *missing_success_records]),
    )

    archive_hash_errors: list[str] = []
    for source_id in sorted(declared_success_ids):
        record = archive_records.get(source_id, {})
        local_rel = str(record.get("local_path") or "")
        expected_sha = str(record.get("sha256") or "")
        local_file = path(local_rel) if local_rel else None
        if not local_rel or not expected_sha or local_file is None or not local_file.is_file():
            archive_hash_errors.append(f"{source_id}:missing")
            continue
        actual_sha = hashlib.sha256(local_file.read_bytes()).hexdigest()
        if actual_sha != expected_sha:
            archive_hash_errors.append(f"{source_id}:sha")
    check(
        "source archive successful bytes match manifest hashes",
        not archive_hash_errors,
        ", ".join(archive_hash_errors),
    )

    exists("main.pdf")
    exists("main_current_text.txt")
    current_source_sha = source_sha256("main.tex") if path("main.tex").exists() else ""
    current_source_graph_sha = source_graph_sha256(["main.tex", *declared_sections]) if declared_sections else ""
    check("final sign-off scope matches current scope", final_signoff.get("scope_id") == scope_id)
    check(
        "final sign-off reviewed source hash matches",
        final_signoff.get("reviewed_source_sha256") == current_source_sha,
        str(final_signoff.get("reviewed_source_sha256") or "missing"),
    )
    check(
        "final sign-off reviewed source graph hash matches",
        final_signoff.get("reviewed_source_graph_sha256") == current_source_graph_sha,
        str(final_signoff.get("reviewed_source_graph_sha256") or "missing"),
    )
    check(
        "final sign-off PDF identity is current",
        final_signoff.get("pdf_identity_status") == "current",
        str(final_signoff.get("pdf_identity_status") or "missing"),
    )

    visual_text = path("visual_review.md").read_text(encoding="utf-8") if path("visual_review.md").exists() else ""
    check("visual review references current scope", scope_id in visual_text)
    check(
        "visual review is current and passed",
        "Status: PASS" in visual_text
        and current_source_sha in visual_text
        and current_source_graph_sha in visual_text,
    )
    check(
        "XeLaTeX render provenance present",
        all(
            field in visual_text
            for field in (
                "Build engine: XeLaTeX",
                "Build platform:",
                "TeX distribution:",
                "CJK font:",
                "Build command:",
            )
        ),
    )

    review_scope_ok = True
    open_s_count = 0
    for cycle in ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic"):
        rel = f"review_findings_{cycle}.json"
        payload = as_mapping(load_json(rel))
        check(f"review findings scope recorded {cycle}", payload.get("scope_id") == scope_id)
        review_scope_ok = review_scope_ok and payload.get("scope_id") == scope_id
        findings = [row for row in as_list(payload.get("findings")) if isinstance(row, Mapping)]
        for finding in findings:
            if str(finding.get("severity", "")).upper().startswith("S") and str(finding.get("status", "open")).lower() not in {"closed", "verified", "resolved", "pass", "passed", "superseded"}:
                open_s_count += 1
    check("all review finding files refer to current scope", review_scope_ok)
    check("no open current-scope S-level findings", open_s_count == 0, str(open_s_count))

    quality = as_mapping(workflow_eval.get("quality"))
    check("workflow scope matches current scope", workflow_eval.get("scope_id") == scope_id)
    check("workflow marked publishable", quality.get("publishable") is True)

    return finish()


def finish() -> int:
    for name, passed, detail in RESULTS:
        print(f"{'PASS' if passed else 'FAIL'} {name}{': ' + detail if detail else ''}")
    failures = sum(1 for _, passed, _ in RESULTS if not passed)
    passes = len(RESULTS) - failures
    print(f"SUMMARY {passes} PASS / {failures} FAIL")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
