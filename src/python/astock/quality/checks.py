"""Deterministic quality checks for system evolution workflows."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

DEGRADED_QUALITY_TIERS = {
    "cached",
    "degraded",
    "delayed",
    "partial",
    "snapshot",
    "snapshot_degraded",
    "unavailable",
}

DEFAULT_REPORT_CHECKS: dict[str, tuple[str, ...]] = {
    "evidence": ("evidence", "source", "provenance", "data"),
    "risk": ("risk", "downside", "drawdown"),
    "contrarian": ("contrarian", "bear case", "counterargument"),
    "monitoring_trigger": ("trigger", "monitor", "watch"),
    "invalidation": ("invalidation", "invalidate", "fails if"),
    "data_quality": ("data quality", "quality_tier", "degraded"),
    "source_exhaustion": ("source exhaustion", "source_exhaustion", "exhaustion log"),
    "full_chain_coverage": ("full-chain", "full_chain_universe", "coverage gap"),
    "valuation_reproducibility": (
        "model reproducibility",
        "valuation audit",
        "valuation_reproducibility",
    ),
    "review_lifecycle": ("review findings", "repair plan", "review lifecycle"),
    "final_signoff": ("final sign-off", "final_signoff", "publishability score"),
    "evidence_depth": (
        "customer",
        "order",
        "asp",
        "utilization",
        "evidence gap",
    ),
    "model_depth": (
        "base business",
        "growth segment",
        "gross profit",
        "net profit",
        "eps",
    ),
    "ic_readiness": (
        "portfolio",
        "position",
        "risk budget",
        "expected return",
        "investment committee",
    ),
}

CASE_ROOT_ARTIFACTS = (
    "research_brief.md",
    "gate_manifest.json",
    "artifact_contract.json",
    "review_log.md",
    "final_signoff.json",
)

CASE_MD_JSON_PAIRS = (
    "gate_manifest",
    "artifact_contract",
    "final_signoff",
    "source_exhaustion_log",
    "data/source_registry",
    "data/claim_audit",
)

INDUSTRY_CHAIN_ARTIFACTS = (
    "analysis/template_brief.md",
    "analysis/full_chain_taxonomy.md",
    "analysis/chain_business_research.md",
    "analysis/core_vs_satellite_universe.md",
    "analysis/coverage_gap_matrix.md",
    "analysis/supply_chain_model.md",
    "analysis/company_fundamental_cards.md",
    "analysis/value_chain_economics.md",
    "analysis/chain_earnings_bridge.md",
    "analysis/competitive_landscape.md",
    "analysis/variant_perception.md",
    "data/supply_chain_relationships.json",
    "data/customer_chain_audit.json",
)

ARTIFACT_CONTRACT_DEPTH_FIELDS = (
    "required_fields",
    "minimum_depth",
    "blocking_conditions",
    "reviewer_cycle",
    "verifier_check",
)

GATE_MANIFEST_DEPTH_GATES = (
    "evidence_depth",
    "broker_consensus_depth",
    "model_depth",
    "valuation_depth",
    "ic_readiness",
)

STRATEGIC_ALLOCATION_DEPTH_GATES = (
    "evidence_depth",
    "model_depth",
    "allocation_model_depth",
    "risk_tax_depth",
    "product_structure_depth",
    "scope_control_depth",
)

LEGACY_PASS_SIGNOFF_STATUSES = {
    "pass",
    "passed",
    "approved",
    "signed",
    "publishable",
}

STRATEGIC_RESEARCH_FRAMEWORK_SIGNOFF_STATUSES = {
    "research_framework_pass",
    "research framework pass",
}

IMPLEMENTATION_BLOCKED_STATUSES = {
    "blocked",
    "not_approved",
    "not approved",
}

INACTIVE_EXECUTION_STATUSES = {
    "blocked",
    "not_approved",
    "not approved",
    "not_authorized",
    "not authorized",
    "not_run",
    "not run",
    "pending",
}

STRATEGIC_MATERIAL_DISCLOSURE_KEYS = (
    "return_target_not_guarantee",
    "return_evidence_not_sufficient_for_implementation",
    "risk_budget_not_approved",
    "implementation_not_authorized",
)

MATERIAL_RESIDUAL_RISK_TERMS = (
    "customer",
    "order",
    "asp",
    "utilization",
    "capacity",
    "broker target",
    "broker target-price",
    "street target",
    "street/broker",
    "consensus",
    "insufficient evidence",
    "not collected",
    "not found",
    "abstract only",
)

BROKER_CONSENSUS_REQUIRED_FIELDS = (
    "ticker",
    "broker",
    "report_date",
    "rating",
    "target_price",
    "revenue_E",
    "net_profit_E",
    "EPS_E",
    "method",
    "implied_upside",
    "source_quality",
    "source_path",
)

BROKER_WEAK_SOURCE_QUALITIES = {
    "abstract_only",
    "aggregator",
    "incomplete",
    "media_repost",
    "not_disclosed",
    "not_found",
    "partial",
    "paywall",
    "search_snippet",
    "third_party_aggregate",
    "third_party_consensus_aggregate",
    "third_party_preview",
    "unavailable",
}

BROKER_INTERNAL_SOURCE_QUALITIES = {
    "astock_house",
    "astock_house_model",
    "house_model",
    "house_model_auditable",
    "internal_model",
}

BROKER_INTERNAL_NAME_TERMS = (
    "astock",
    "house view",
    "house model",
    "internal",
)

BROKER_EXTERNAL_POSITIVE_SOURCE_QUALITIES = {
    "original_pdf",
    "broker_official_page",
    "auditable_consensus_snapshot",
    "auditable_broker_repost",
    "broker_repost_full_fields",
}

BROKER_UNAVAILABLE_VALUES = {
    "",
    "-",
    "abstract only",
    "n/a",
    "na",
    "none",
    "not available",
    "not collected",
    "not disclosed",
    "not found",
    "null",
    "paywall",
    "unavailable",
    "unknown",
}

BROKER_CONSENSUS_USABLE_FIELDS = (
    "broker",
    "report_date",
    "rating",
    "target_price",
    "revenue_E",
    "net_profit_E",
    "EPS_E",
    "method",
    "implied_upside",
)

VALUATION_REQUIRED_SECTIONS = (
    "Final Valuation Table",
    "Three-Tier Targets",
    "Relative / PEG / PSG Comparison",
    "Seasonality Calibration",
    "Next-Quarter Threshold",
    "Method and Assumption Bridge",
    "Market-Expectation Valuation Bridge",
    "Broker/Street Comparison",
    "Market-Implied Sentiment Anchor",
    "Growth Earnings Dependency",
    "Full-Chain Classification Dependency",
)

VALUATION_REQUIRED_ROW_FIELDS = (
    "ticker",
    "company",
    "current_price",
    "price_date",
    "shares_100mn",
    "market_cap_100mn_cny",
    "revenue_2026e_100mn",
    "np_2026e_100mn",
    "eps_2026e",
    "method",
    "bear",
    "base",
    "bull",
    "market_implied_anchor",
    "fundamental_weight",
    "market_weight",
    "broker_weight",
    "final_target",
    "upside",
    "action",
    "evidence_quality",
)

SINGLE_STOCK_INSTITUTIONAL_DEPTH_TERMS = {
    "segment valuation depth": (
        "analysis/segment_valuation_model.md",
        (
            "segment",
            "sotp",
            "revenue",
            "net profit",
            "multiple",
            "sensitivity",
            "validation trigger",
        ),
        "S",
    ),
    "secondary-market analysis depth": (
        "analysis/secondary_market_analysis.md",
        (
            "price",
            "volume",
            "turnover",
            "drawdown",
            "relative performance",
            "valuation crowding",
            "support",
            "resistance",
            "seat",
            "institutional",
            "northbound",
            "financing",
            "trading style",
            "hot-money",
            "fund attitude",
            "trend swing",
        ),
        "S",
    ),
}

INDUSTRY_DEPTH_TERM_SETS: dict[str, tuple[str, tuple[str, ...], str]] = {
    "chain business research depth": (
        "analysis/chain_business_research.md",
        (
            "upstream business",
            "downstream business",
            "business relationship",
            "core technology",
            "core revenue business",
            "2026e expectation",
        ),
        "A",
    ),
    "value-chain economics depth": (
        "analysis/value_chain_economics.md",
        (
            "asp",
            "margin",
            "capacity",
            "utilization",
            "order",
            "valuation credit",
        ),
        "A",
    ),
    "growth earnings model depth": (
        "analysis/growth_earnings_model.md",
        (
            "base business",
            "growth segment",
            "unit",
            "asp",
            "gross",
            "net profit",
            "eps",
            "bear",
            "bull",
            "current-price-implied",
        ),
        "A",
    ),
    "company card operating depth": (
        "analysis/company_fundamental_cards.md",
        (
            "cash flow",
            "inventory",
            "capex",
            "debt",
            "order",
            "certification",
        ),
        "A",
    ),
    "valuation anchor depth": (
        "analysis/valuation_model.md",
        (
            "current",
            "share",
            "market cap",
            "broker",
            "street",
            "market-implied",
            "weight",
            "target",
            "upside",
        ),
        "S",
    ),
}

CLOSED_REVIEW_STATUSES = {
    "closed",
    "verified",
    "resolved",
    "resolved_at_framework_scope",
    "resolved_at_research_framework_scope",
    "resolved at framework scope",
    "resolved at research framework scope",
    "pass",
    "passed",
    "superseded",
}

DEFAULT_FORBIDDEN_SKILL_TERMS = (
    "place order",
    "submit order",
    "execute trade",
    "route order",
    "broker login",
    "brokerage password",
)


@dataclass(frozen=True)
class SkillEvalCase:
    """One deterministic skill-boundary evaluation case."""

    name: str
    response: str
    prompt: str = ""
    required_terms: tuple[str, ...] = ()
    forbidden_terms: tuple[str, ...] = DEFAULT_FORBIDDEN_SKILL_TERMS
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SkillEvalCase":
        return cls(
            name=str(data.get("name", "unnamed_case")),
            prompt=str(data.get("prompt", "")),
            response=str(data.get("response", "")),
            required_terms=_tuple_from_value(data.get("required_terms")),
            forbidden_terms=(
                _tuple_from_value(data.get("forbidden_terms"))
                or DEFAULT_FORBIDDEN_SKILL_TERMS
            ),
            metadata=_json_ready_mapping(
                cast(Mapping[str, Any], data.get("metadata", {}))
                if isinstance(data.get("metadata"), Mapping)
                else {}
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "prompt": self.prompt,
            "response": self.response,
            "required_terms": list(self.required_terms),
            "forbidden_terms": list(self.forbidden_terms),
            "metadata": dict(self.metadata),
        }


def evaluate_source_health(
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Evaluate source health from provenance-like records."""

    grouped: dict[str, list[Mapping[str, Any]]] = {}
    for record in records:
        source = _text(record.get("source"), "unknown")
        grouped.setdefault(source, []).append(record)

    summaries = [
        _source_summary(source, items) for source, items in sorted(grouped.items())
    ]
    failing = sum(1 for item in summaries if item["status"] == "failing")
    degraded = sum(1 for item in summaries if item["status"] == "degraded")
    overall_status = "good"
    if failing:
        overall_status = "failing"
    elif degraded:
        overall_status = "degraded"

    return {
        "schema_version": "quality.source_health.v1",
        "record_count": len(records),
        "source_count": len(summaries),
        "overall_status": overall_status,
        "sources": summaries,
    }


def check_prompt_drift(
    file_pairs: Sequence[Mapping[str, Any]],
    *,
    root_path: str | Path | None = None,
) -> dict[str, Any]:
    """Compare prompt file pairs and report hash drift or missing files."""

    root = Path(root_path) if root_path is not None else None
    results: list[dict[str, Any]] = []
    for pair in file_pairs:
        name = _text(pair.get("name"), "prompt_pair")
        left = _resolve_path(pair.get("left"), root)
        right = _resolve_path(pair.get("right"), root)
        left_exists = left.exists()
        right_exists = right.exists()
        left_hash = _sha256_file(left) if left_exists else None
        right_hash = _sha256_file(right) if right_exists else None
        identical = bool(left_exists and right_exists and left_hash == right_hash)
        results.append(
            {
                "name": name,
                "left": str(left),
                "right": str(right),
                "left_exists": left_exists,
                "right_exists": right_exists,
                "left_sha256": left_hash,
                "right_sha256": right_hash,
                "identical": identical,
                "status": "ok" if identical else "drift",
            }
        )

    drift_count = sum(1 for item in results if item["status"] != "ok")
    return {
        "schema_version": "quality.prompt_drift.v1",
        "pair_count": len(results),
        "drift_count": drift_count,
        "status": "ok" if drift_count == 0 else "drift",
        "pairs": results,
    }


def evaluate_report_quality(
    report_text: str,
    *,
    checks: Mapping[str, Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Evaluate whether a report includes required research-quality elements."""

    check_terms = checks or DEFAULT_REPORT_CHECKS
    normalized = _normalize(report_text)
    results: list[dict[str, Any]] = []
    passed_count = 0
    for name, terms in check_terms.items():
        hits = [term for term in terms if _normalize(term) in normalized]
        passed = bool(hits)
        if passed:
            passed_count += 1
        results.append(
            {
                "name": name,
                "passed": passed,
                "hits": hits,
                "expected_terms": list(terms),
            }
        )

    total = len(results)
    score = round(passed_count / total * 100, 2) if total else 100.0
    return {
        "schema_version": "quality.report_quality.v1",
        "score": score,
        "passed_count": passed_count,
        "check_count": total,
        "status": _score_status(score),
        "checks": results,
    }


def evaluate_research_case_quality(case_dir: str | Path) -> dict[str, Any]:
    """Evaluate artifact-level quality gates for a research case directory."""

    root = Path(case_dir)
    checks: list[dict[str, Any]] = []

    def add(name: str, passed: bool, detail: str = "", severity: str = "A") -> None:
        checks.append(
            {
                "name": name,
                "passed": passed,
                "severity": severity,
                "detail": detail,
            }
        )

    add("case directory exists", root.exists(), str(root), "S")
    if not root.exists():
        return _research_case_result(root, checks, requires_industry_chain=False)

    for rel in CASE_ROOT_ARTIFACTS:
        add(f"exists {rel}", (root / rel).exists(), rel, "S")

    for stem in CASE_MD_JSON_PAIRS:
        add(
            f"md/json pair present: {stem}",
            (root / f"{stem}.md").exists() and (root / f"{stem}.json").exists(),
            stem,
            "A",
        )

    gate_manifest, gate_error = _load_json_document(root / "gate_manifest.json")
    artifact_contract, contract_error = _load_json_document(
        root / "artifact_contract.json"
    )
    final_signoff, signoff_error = _load_json_document(root / "final_signoff.json")
    add("gate manifest json parses", gate_error is None, gate_error or "", "S")
    add(
        "artifact contract json parses",
        contract_error is None,
        contract_error or "",
        "S",
    )
    add("final sign-off json parses", signoff_error is None, signoff_error or "", "S")

    required_artifacts = set()
    required_artifacts.update(_artifact_paths_from_payload(gate_manifest))
    required_artifacts.update(_artifact_paths_from_payload(artifact_contract))
    for rel in sorted(required_artifacts):
        add(f"required artifact exists: {rel}", (root / rel).exists(), rel, "S")

    for gate_name, passed, detail, severity in _gate_manifest_depth_checks(
        gate_manifest
    ):
        add(gate_name, passed, detail, severity)

    for check_name, passed, detail, severity in _artifact_contract_depth_checks(
        artifact_contract
    ):
        add(check_name, passed, detail, severity)

    strategic_allocation_case = _case_is_strategic_allocation(gate_manifest)
    strategic_framework_case = _strategic_allocation_uses_framework_signoff(
        gate_manifest
    )
    strategic_can_skip_issuer_broker_gate = (
        _strategic_allocation_can_skip_issuer_broker_gate(gate_manifest)
        if strategic_allocation_case
        else False
    )
    strategic_requires_issuer_valuation = (
        strategic_allocation_case and not strategic_can_skip_issuer_broker_gate
    )

    requires_industry_chain = (
        not strategic_allocation_case
        and _case_requires_industry_chain(
            gate_manifest,
            "\n".join(
                (
                    _read_text(root / "research_brief.md"),
                    _read_text(root / "analysis" / "template_brief.md"),
                )
            ),
        )
    )
    if requires_industry_chain:
        for rel in INDUSTRY_CHAIN_ARTIFACTS:
            add(
                f"industry-chain artifact exists: {rel}",
                (root / rel).exists(),
                rel,
                "S",
            )
        universe_files = sorted((root / "data").glob("full_chain_universe_*.json"))
        add(
            "industry-chain full-chain universe json present",
            bool(universe_files),
            "data/full_chain_universe_<YYYYMMDD>.json",
            "S",
        )
        for check_name, passed, detail, severity in _industry_depth_checks(root):
            add(check_name, passed, detail, severity)

    review_findings = sorted(root.glob("review_findings_*.json"))
    add("review findings present", bool(review_findings), "review_findings_*.json", "S")
    open_s_count = 0
    open_unwaived_a_count = 0
    parse_failures = 0
    for findings_path in review_findings:
        payload, error = _load_json_document(findings_path)
        add(
            f"review findings parse: {findings_path.name}",
            error is None,
            error or "",
            "S",
        )
        if error:
            parse_failures += 1
            continue
        for finding in _extract_review_findings(payload):
            severity = _review_severity(finding)
            status = _review_status(finding)
            waived = _review_waived(finding)
            if severity == "S" and status not in CLOSED_REVIEW_STATUSES:
                open_s_count += 1
            if severity == "A" and status not in CLOSED_REVIEW_STATUSES and not waived:
                open_unwaived_a_count += 1

        cycle = findings_path.stem.removeprefix("review_findings_")
        if cycle != "R4_final_ic":
            add(
                f"repair plan pair present: {cycle}",
                (root / f"repair_plan_{cycle}.md").exists()
                and (root / f"repair_plan_{cycle}.json").exists(),
                cycle,
                "A",
            )

    add("no open S-Level findings", open_s_count == 0, str(open_s_count), "S")
    add(
        "no open unwaived A-Level findings",
        open_unwaived_a_count == 0,
        str(open_unwaived_a_count),
        "A",
    )

    review_log = _read_text(root / "review_log.md")
    publishability_score = _extract_publishability_score(review_log)
    add(
        "publishability score present",
        publishability_score is not None,
        "review_log.md",
        "S",
    )
    if publishability_score is not None:
        add(
            "publishability score >= 90",
            publishability_score >= 90,
            str(publishability_score),
            "S",
        )

    if strategic_framework_case:
        for check_name, passed, detail, severity in _strategic_allocation_depth_checks(
            root,
            gate_manifest,
        ):
            add(check_name, passed, detail, severity)
    if not strategic_allocation_case or strategic_requires_issuer_valuation:
        valuation_audit = _read_text(root / "analysis" / "valuation_audit.md")
        add(
            "valuation model reproducibility pass",
            "model reproducibility: pass" in _normalize(valuation_audit),
            "analysis/valuation_audit.md",
            "S",
        )
        for check_name, passed, detail, severity in _valuation_model_depth_checks(root):
            add(check_name, passed, detail, severity)
    if not requires_industry_chain and not strategic_allocation_case:
        for check_name, passed, detail, severity in _single_stock_depth_checks(root):
            add(check_name, passed, detail, severity)
    if not strategic_allocation_case:
        for check_name, passed, detail, severity in _broker_street_consensus_checks(
            root,
            final_signoff,
            allow_zero_weight_exhaustion=not requires_industry_chain,
        ):
            add(check_name, passed, detail, severity)
    elif strategic_requires_issuer_valuation:
        for check_name, passed, detail, severity in _broker_street_consensus_checks(
            root,
            final_signoff,
            allow_zero_weight_exhaustion=False,
        ):
            add(check_name, passed, detail, severity)
        for (
            check_name,
            passed,
            detail,
            severity,
        ) in _strategic_named_direct_equity_reconciliation_checks(
            root,
            gate_manifest,
        ):
            add(check_name, passed, detail, severity)

    signoff_status = ""
    if isinstance(final_signoff, Mapping):
        signoff_status = _normalize(
            final_signoff.get("signoff_status") or final_signoff.get("status")
        )
    if strategic_framework_case:
        strategy_controls = (
            gate_manifest.get("strategy_controls")
            if isinstance(gate_manifest, Mapping)
            else None
        )
        cash_objective_required = (
            strategy_controls.get("cash_objective_required")
            if isinstance(strategy_controls, Mapping)
            and isinstance(strategy_controls.get("cash_objective_required"), bool)
            else None
        )
        for check_name, passed, detail, severity in _strategic_signoff_checks(
            final_signoff,
            cash_objective_required=cash_objective_required,
        ):
            add(check_name, passed, detail, severity)
    if strategic_framework_case:
        residual_ok, residual_detail = _strategic_residual_risks_disclosed(
            final_signoff
        )
        add(
            "strategic allocation residual implementation blockers are disclosed",
            residual_ok,
            residual_detail,
            "S",
        )
    else:
        add(
            "final sign-off status pass",
            signoff_status in LEGACY_PASS_SIGNOFF_STATUSES,
            signoff_status or "missing",
            "S",
        )
        add(
            "final sign-off residual risks do not conflict with PASS",
            not _final_signoff_has_material_residual_risk_conflict(final_signoff),
            "material residual risk cannot be hidden in a PASS sign-off",
            "S",
        )

    workflow_eval, workflow_error = _load_json_document(
        root / "research_workflow_eval.json"
    )
    if strategic_framework_case:
        quality = (
            workflow_eval.get("quality") if isinstance(workflow_eval, Mapping) else None
        )
        add(
            "strategic allocation workflow implementation explicitly not approved",
            isinstance(quality, Mapping)
            and _normalize(quality.get("implementation_status"))
            in IMPLEMENTATION_BLOCKED_STATUSES,
            str(
                quality.get("implementation_status")
                if isinstance(quality, Mapping)
                else workflow_error or "missing"
            ),
            "S",
        )

    result = _research_case_result(
        root,
        checks,
        requires_industry_chain,
        strategic_allocation_case=strategic_framework_case,
    )
    result["review_summary"] = {
        "finding_file_count": len(review_findings),
        "parse_failure_count": parse_failures,
        "open_s_count": open_s_count,
        "open_unwaived_a_count": open_unwaived_a_count,
        "publishability_score": publishability_score,
    }
    return result


def evaluate_skill_response_cases(
    cases: Sequence[Mapping[str, Any] | SkillEvalCase],
) -> dict[str, Any]:
    """Run deterministic skill-boundary checks over response cases."""

    parsed_cases = [
        case if isinstance(case, SkillEvalCase) else SkillEvalCase.from_dict(case)
        for case in cases
    ]
    results = [_evaluate_skill_case(case) for case in parsed_cases]
    passed_count = sum(1 for result in results if result["passed"])
    total = len(results)
    score = round(passed_count / total * 100, 2) if total else 100.0
    return {
        "schema_version": "quality.skill_eval.v1",
        "score": score,
        "passed_count": passed_count,
        "case_count": total,
        "status": _score_status(score),
        "cases": results,
    }


def _research_case_result(
    root: Path,
    checks: Sequence[Mapping[str, Any]],
    requires_industry_chain: bool,
    strategic_allocation_case: bool = False,
) -> dict[str, Any]:
    passed_count = sum(1 for check in checks if bool(check.get("passed")))
    total = len(checks)
    score = round(passed_count / total * 100, 2) if total else 100.0
    blocking_failures = [
        check
        for check in checks
        if not bool(check.get("passed")) and str(check.get("severity")) in {"S", "A"}
    ]
    publishable = not blocking_failures and score >= 90
    status = (
        "research_framework_pass_implementation_not_approved"
        if publishable and strategic_allocation_case
        else (
            "excellent"
            if publishable
            else ("blocked" if blocking_failures else _score_status(score))
        )
    )
    result = {
        "schema_version": "quality.research_case.v1",
        "case_dir": str(root),
        "score": score,
        "passed_count": passed_count,
        "check_count": total,
        "blocking_failure_count": len(blocking_failures),
        "requires_industry_chain": requires_industry_chain,
        "publishable": publishable,
        "status": status,
        "checks": list(checks),
        "blocking_failures": blocking_failures,
    }
    if strategic_allocation_case:
        result["implementation_status"] = "NOT_APPROVED"
    return result


def _load_json_document(path: Path) -> tuple[Any, str | None]:
    if not path.exists():
        return {}, f"missing: {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - defensive diagnostics
        return {}, f"{path}: {exc}"


def _artifact_paths_from_payload(payload: Any) -> set[str]:
    paths: set[str] = set()
    paths.update(_artifact_paths_from_value(payload))
    return paths


def _gate_manifest_depth_checks(
    payload: Any,
) -> list[tuple[str, bool, str, str]]:
    if not isinstance(payload, Mapping):
        return [("gate manifest has depth gates", False, "not an object", "A")]

    depth_gates = payload.get("depth_gates")
    if not isinstance(depth_gates, Sequence) or isinstance(
        depth_gates, (str, bytes, bytearray)
    ):
        return [("gate manifest has depth gates", False, "missing depth_gates", "A")]

    normalized_gates = {_normalize(gate) for gate in depth_gates}
    required_gates = (
        STRATEGIC_ALLOCATION_DEPTH_GATES
        if _case_is_strategic_allocation(payload)
        else GATE_MANIFEST_DEPTH_GATES
    )
    missing = [gate for gate in required_gates if gate not in normalized_gates]
    return [
        (
            "gate manifest depth gates complete",
            not missing,
            ", ".join(missing) if missing else "all depth gates present",
            "A",
        )
    ]


def _artifact_contract_depth_checks(
    payload: Any,
) -> list[tuple[str, bool, str, str]]:
    if not isinstance(payload, Mapping):
        return [("artifact contract is field-level", False, "not an object", "A")]

    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, Sequence) or isinstance(
        artifacts, (str, bytes, bytearray)
    ):
        return [("artifact contract is field-level", False, "missing artifacts", "A")]
    if not artifacts:
        return [("artifact contract is field-level", False, "empty artifacts", "A")]

    missing_by_artifact: list[str] = []
    for item in artifacts:
        if not isinstance(item, Mapping):
            missing_by_artifact.append("<non-object>: all depth fields")
            continue
        path = _text(item.get("path") or item.get("artifact"), "<missing path>")
        missing_fields = [
            field
            for field in ARTIFACT_CONTRACT_DEPTH_FIELDS
            if not _has_items(item.get(field))
        ]
        if missing_fields:
            missing_by_artifact.append(f"{path}: {', '.join(missing_fields)}")

    return [
        (
            "artifact contract declares required fields and depth gates",
            not missing_by_artifact,
            "; ".join(missing_by_artifact[:8])
            + ("; ..." if len(missing_by_artifact) > 8 else ""),
            "A",
        )
    ]


def _industry_depth_checks(root: Path) -> list[tuple[str, bool, str, str]]:
    checks: list[tuple[str, bool, str, str]] = []
    for name, (rel, terms, severity) in INDUSTRY_DEPTH_TERM_SETS.items():
        text = _normalize(_read_text(root / rel))
        missing = [term for term in terms if _normalize(term) not in text]
        checks.append(
            (
                name,
                not missing,
                (
                    f"{rel} missing: {', '.join(missing)}"
                    if missing
                    else f"{rel} contains required depth terms"
                ),
                severity,
            )
        )
    return checks


def _valuation_model_depth_checks(root: Path) -> list[tuple[str, bool, str, str]]:
    checks: list[tuple[str, bool, str, str]] = []
    valuation_path = root / "analysis" / "valuation_model.md"
    valuation_text = _normalize(_read_text(valuation_path))
    missing_sections = [
        section
        for section in VALUATION_REQUIRED_SECTIONS
        if _normalize(section) not in valuation_text
    ]
    checks.append(
        (
            "valuation model required sections complete",
            not missing_sections,
            (
                ", ".join(missing_sections)
                if missing_sections
                else "all valuation sections present"
            ),
            "S",
        )
    )

    rows = _valuation_rows(
        _load_first_json(root, "data/current_valuation_model_*.json")
    )
    checks.append(
        (
            "valuation model structured rows present",
            bool(rows),
            f"rows={len(rows)}",
            "S",
        )
    )
    if not rows:
        return checks

    missing_by_row: list[str] = []
    arithmetic_errors: list[str] = []
    for row in rows:
        ticker = str(row.get("ticker") or "<missing ticker>")
        missing = [
            field
            for field in VALUATION_REQUIRED_ROW_FIELDS
            if not _has_items(row.get(field))
        ]
        if missing:
            missing_by_row.append(f"{ticker}: {', '.join(missing)}")

        current = _float_or_none(row.get("current_price"))
        target = _float_or_none(row.get("final_target"))
        upside = _float_or_none(row.get("upside"))
        if current and target is not None and upside is not None:
            expected = target / current - 1
            if abs(expected - upside) > 0.005:
                arithmetic_errors.append(
                    f"{ticker}: upside {upside:.4f} != target/current-1 {expected:.4f}"
                )

    detail = "; ".join(missing_by_row[:6])
    if len(missing_by_row) > 6:
        detail += "; ..."
    checks.append(
        ("valuation model row fields complete", not missing_by_row, detail, "S")
    )
    checks.append(
        (
            "valuation model target/upside recalculates",
            not arithmetic_errors,
            "; ".join(arithmetic_errors[:6]),
            "S",
        )
    )
    return checks


def _single_stock_depth_checks(root: Path) -> list[tuple[str, bool, str, str]]:
    checks: list[tuple[str, bool, str, str]] = []
    missing_artifacts: list[str] = []
    shallow_artifacts: list[str] = []
    for _name, (
        rel,
        terms,
        _severity,
    ) in SINGLE_STOCK_INSTITUTIONAL_DEPTH_TERMS.items():
        path = root / rel
        text = _normalize(_read_text(path))
        if not path.exists():
            missing_artifacts.append(rel)
            continue
        missing_terms = [term for term in terms if _normalize(term) not in text]
        if missing_terms:
            shallow_artifacts.append(f"{rel}: {', '.join(missing_terms)}")

    detail_parts = []
    if missing_artifacts:
        detail_parts.append("missing " + ", ".join(missing_artifacts))
    if shallow_artifacts:
        detail_parts.append("; ".join(shallow_artifacts[:4]))
    checks.append(
        (
            "single-stock valuation model institutional depth",
            not missing_artifacts and not shallow_artifacts,
            (
                "; ".join(detail_parts)
                if detail_parts
                else "segment valuation and secondary-market artifacts present"
            ),
            "S",
        )
    )
    return checks


def _broker_street_consensus_checks(
    root: Path,
    final_signoff: Any,
    *,
    allow_zero_weight_exhaustion: bool = False,
) -> list[tuple[str, bool, str, str]]:
    checks: list[tuple[str, bool, str, str]] = []
    consensus_files = sorted((root / "data").glob("broker_street_consensus_*.json"))
    checks.append(
        (
            "broker/street consensus json present",
            bool(consensus_files),
            "data/broker_street_consensus_<YYYYMMDD>.json",
            "S",
        )
    )
    if not consensus_files:
        return checks

    md_path = consensus_files[0].with_suffix(".md")
    checks.append(
        (
            "broker/street consensus md pair present",
            md_path.exists(),
            str(md_path.relative_to(root)),
            "S",
        )
    )
    payload, error = _load_json_document(consensus_files[0])
    checks.append(
        (
            "broker/street consensus json parses",
            error is None,
            error or "",
            "S",
        )
    )
    rows = _broker_consensus_rows(payload)
    checks.append(
        ("broker/street consensus rows present", bool(rows), f"rows={len(rows)}", "S")
    )

    valuation_rows = _valuation_rows(
        _load_first_json(root, "data/current_valuation_model_*.json")
    )
    covered_tickers = {
        str(row.get("ticker"))
        for row in valuation_rows
        if _has_items(row.get("ticker"))
    }
    zero_weight_valuation_tickers = {
        str(row.get("ticker"))
        for row in valuation_rows
        if _has_items(row.get("ticker"))
        and _first_float(row.get("broker_weight")) == 0.0
    }
    row_tickers = {
        str(row.get("ticker")) for row in rows if _has_items(row.get("ticker"))
    }
    missing_coverage = sorted(covered_tickers - row_tickers)
    checks.append(
        (
            "broker/street consensus covers valuation universe",
            not missing_coverage,
            (
                ", ".join(missing_coverage)
                if missing_coverage
                else f"covered={len(row_tickers)}"
            ),
            "S",
        )
    )

    missing_by_row: list[str] = []
    unusable_by_row: list[str] = []
    weak_not_downweighted: list[str] = []
    weak_rows: list[Mapping[str, Any]] = []
    unusable_rows: list[Mapping[str, Any]] = []
    positive_anchor_tickers: set[str] = set()
    external_positive_anchor_tickers: set[str] = set()
    for row in rows:
        ticker = str(row.get("ticker") or "<missing ticker>")
        missing = [
            field
            for field in BROKER_CONSENSUS_REQUIRED_FIELDS
            if not _has_items(row.get(field))
        ]
        if missing:
            missing_by_row.append(f"{ticker}: {', '.join(missing)}")

        unusable = [
            field
            for field in BROKER_CONSENSUS_USABLE_FIELDS
            if not _broker_value_usable(row.get(field))
        ]
        if unusable:
            unusable_rows.append(row)
            unusable_by_row.append(f"{ticker}: {', '.join(unusable)}")

        source_quality = _normalize(row.get("source_quality"))
        if source_quality in BROKER_WEAK_SOURCE_QUALITIES or unusable:
            weak_rows.append(row)
            weight = _first_float(
                row.get("street_weight"),
                row.get("broker_weight"),
                row.get("valuation_weight"),
                row.get("weight"),
            )
            if weight not in (0.0, None):
                weak_not_downweighted.append(
                    f"{ticker}: {source_quality or 'unusable_fields'} weight={weight}"
                )
        if (
            not missing
            and not unusable
            and source_quality not in BROKER_WEAK_SOURCE_QUALITIES
            and (
                _first_float(
                    row.get("street_weight"),
                    row.get("broker_weight"),
                    row.get("valuation_weight"),
                    row.get("weight"),
                )
                or 0.0
            )
            > 0.0
        ):
            positive_anchor_tickers.add(ticker)
            if _broker_row_external(row):
                external_positive_anchor_tickers.add(ticker)

    detail = "; ".join(missing_by_row[:8])
    if len(missing_by_row) > 8:
        detail += "; ..."
    checks.append(
        ("broker/street consensus row fields complete", not missing_by_row, detail, "S")
    )
    unusable_detail = "; ".join(unusable_by_row[:8])
    if len(unusable_by_row) > 8:
        unusable_detail += "; ..."
    checks.append(
        (
            "broker/street weak sources are zero-weight or unavailable",
            not weak_not_downweighted,
            "; ".join(weak_not_downweighted[:8]),
            "S",
        )
    )

    source_exhaustion = _normalize(_read_text(root / "source_exhaustion_log.md"))
    broker_gap_documented = (
        "broker" in source_exhaustion or "券商" in source_exhaustion
    ) and ("target" in source_exhaustion or "目标价" in source_exhaustion)
    auditable_zero_weight_tickers = (
        zero_weight_valuation_tickers
        if allow_zero_weight_exhaustion
        and broker_gap_documented
        and not weak_not_downweighted
        else set()
    )
    unusable_positive_rows = [
        row
        for row in unusable_rows
        if str(row.get("ticker") or "") not in auditable_zero_weight_tickers
        or (
            _first_float(
                row.get("street_weight"),
                row.get("broker_weight"),
                row.get("valuation_weight"),
                row.get("weight"),
            )
            or 0.0
        )
        > 0.0
    ]
    checks.append(
        (
            "broker/street consensus values usable for valuation anchor",
            not unusable_positive_rows,
            unusable_detail,
            "S",
        )
    )

    missing_positive_anchor = sorted(
        covered_tickers - positive_anchor_tickers - auditable_zero_weight_tickers
    )
    checks.append(
        (
            "broker/street positive-weight auditable anchor covers valuation universe",
            not missing_positive_anchor,
            ", ".join(missing_positive_anchor[:8]),
            "S",
        )
    )
    missing_external_anchor = sorted(
        covered_tickers
        - external_positive_anchor_tickers
        - auditable_zero_weight_tickers
    )
    checks.append(
        (
            "broker/street external positive anchor covers valuation universe",
            not missing_external_anchor,
            ", ".join(missing_external_anchor[:8]),
            "S",
        )
    )

    checks.append(
        (
            "broker/street gaps recorded in source exhaustion",
            not (weak_rows or unusable_rows) or broker_gap_documented,
            "source_exhaustion_log.md must record broker target-price gaps",
            "A",
        )
    )

    signoff_status = ""
    if isinstance(final_signoff, Mapping):
        signoff_status = _normalize(
            final_signoff.get("signoff_status") or final_signoff.get("status")
        )
    checks.append(
        (
            "broker/street consensus complete before PASS sign-off",
            signoff_status
            not in {"pass", "passed", "approved", "signed", "publishable"}
            or not (weak_rows or unusable_rows)
            or (
                broker_gap_documented
                and not weak_not_downweighted
                and covered_tickers <= auditable_zero_weight_tickers
            ),
            "PASS cannot coexist with incomplete broker/Street target-price coverage",
            "S",
        )
    )
    return checks


def _load_first_json(root: Path, pattern: str) -> Any:
    matches = sorted(root.glob(pattern), reverse=True)
    if not matches:
        return {}
    payload, error = _load_json_document(matches[0])
    return {} if error else payload


def _valuation_rows(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, Mapping):
        for key in ("rows", "valuations", "items"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [
                    cast(Mapping[str, Any], row)
                    for row in rows
                    if isinstance(row, Mapping)
                ]
    if isinstance(payload, list):
        return [
            cast(Mapping[str, Any], row) for row in payload if isinstance(row, Mapping)
        ]
    return []


def _broker_consensus_rows(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, Mapping):
        for key in ("rows", "consensus", "items", "broker_street_consensus"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [
                    cast(Mapping[str, Any], row)
                    for row in rows
                    if isinstance(row, Mapping)
                ]
    if isinstance(payload, list):
        return [
            cast(Mapping[str, Any], row) for row in payload if isinstance(row, Mapping)
        ]
    return []


def _first_float(*values: Any) -> float | None:
    for value in values:
        parsed = _float_or_none(value)
        if parsed is not None:
            return parsed
    return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _final_signoff_has_material_residual_risk_conflict(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False

    status = _normalize(payload.get("signoff_status") or payload.get("status"))
    if status not in {"pass", "passed", "approved", "signed", "publishable"}:
        return False

    residual_risks = payload.get("residual_risks")
    if isinstance(residual_risks, str):
        residual_text = residual_risks
    elif isinstance(residual_risks, Sequence) and not isinstance(
        residual_risks, (bytes, bytearray)
    ):
        residual_text = " ".join(str(item) for item in residual_risks)
    else:
        residual_text = ""

    normalized_risk = _normalize(residual_text)
    if not normalized_risk:
        return False

    downgrade_status = _normalize(payload.get("downgrade_status"))
    if "downgrade" in downgrade_status and "none" not in downgrade_status:
        return False

    return any(term in normalized_risk for term in MATERIAL_RESIDUAL_RISK_TERMS)


def _artifact_paths_from_value(value: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(value, str):
        if _looks_like_artifact_path(value):
            paths.add(value.strip())
        return paths
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = _normalize(key)
            if key_text in {
                "path",
                "file",
                "relpath",
                "relative_path",
                "artifact",
                "artifact_path",
                "output",
            } and isinstance(item, str):
                if _looks_like_artifact_path(item):
                    paths.add(item.strip())
                continue
            paths.update(_artifact_paths_from_value(item))
        return paths
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            paths.update(_artifact_paths_from_value(item))
    return paths


def _looks_like_artifact_path(value: str) -> bool:
    text = value.strip()
    if not text or text.startswith(("http://", "https://")):
        return False
    if any(token in text for token in ("\n", "\t", "{", "}")):
        return False
    suffix = Path(text).suffix.lower()
    artifact_suffixes = {
        ".csv",
        ".json",
        ".md",
        ".pdf",
        ".png",
        ".tex",
        ".txt",
        ".xlsx",
    }
    return suffix in artifact_suffixes


def _case_requires_industry_chain(gate_manifest: Any, text_blob: str) -> bool:
    gate_text = ""
    if isinstance(gate_manifest, Mapping):
        report_type = _normalize(gate_manifest.get("report_type"))
        if report_type.startswith(("single_stock", "single-stock")):
            return False
        gate_text = json.dumps(gate_manifest, ensure_ascii=False)
    haystack = _normalize(f"{gate_text}\n{text_blob}")
    return any(
        token in haystack
        for token in (
            "industry-chain",
            "industry_chain",
            "full-chain",
            "full_chain",
            "supply-chain",
            "supply_chain",
            "产业链",
            "全产业链",
        )
    )


def _case_is_strategic_allocation(gate_manifest: Any) -> bool:
    return (
        isinstance(gate_manifest, Mapping)
        and _normalize(gate_manifest.get("case_profile")) == "strategic_allocation"
    )


def _strategic_allocation_uses_open_item_admission(gate_manifest: Any) -> bool:
    """Return whether a strategy explicitly separates open research from allocation.

    An open research universe is not a relaxation of the implementation
    boundary.  It is a distinct strategic-allocation profile in which no
    direct equity is named or allocated yet, but future candidates must clear
    item-level and portfolio-level gates before entering T3/T4.
    """

    if not isinstance(gate_manifest, Mapping):
        return False
    controls = gate_manifest.get("strategy_controls")
    return (
        isinstance(controls, Mapping)
        and _normalize(controls.get("research_universe_mode"))
        == "open_with_item_level_admission"
    )


def _strategic_allocation_can_skip_issuer_broker_gate(gate_manifest: Any) -> bool:
    """Return whether no direct issuer has entered an issuer-level gate.

    Closed-universe strategic notes can skip issuer evidence only when they
    expressly exclude direct-stock exposure.  An open-universe note can skip
    only while it has no named T3 direct-equity issuer and commits each future
    issuer to the exact valuation-policy contract.  A named T3 issuer must
    instead clear the normal issuer valuation and broker/Street packet gates.
    """

    if not isinstance(gate_manifest, Mapping):
        return False
    controls = gate_manifest.get("strategy_controls")
    if not isinstance(controls, Mapping):
        return False
    if _strategic_allocation_uses_open_item_admission(gate_manifest):
        tickers = controls.get("named_t3_direct_equity_tickers")
        named_tickers = (
            [str(ticker).strip() for ticker in tickers if str(ticker).strip()]
            if isinstance(tickers, Sequence)
            and not isinstance(tickers, (str, bytes, bytearray))
            else []
        )
        return (
            _first_float(controls.get("initial_direct_stock_weight")) == 0.0
            and _normalize(controls.get("issuer_target_price_policy"))
            == "required_for_each_named_t3_direct_equity"
            and _int_or_none(controls.get("named_t3_direct_equity_count")) == 0
            and not named_tickers
        )
    return _strategic_allocation_has_zero_direct_stock(gate_manifest)


def _strategic_allocation_has_zero_direct_stock(gate_manifest: Any) -> bool:
    if not isinstance(gate_manifest, Mapping):
        return False
    controls = gate_manifest.get("strategy_controls")
    if not isinstance(controls, Mapping):
        return False
    return _first_float(
        controls.get("initial_direct_stock_weight")
    ) == 0.0 and _normalize(controls.get("issuer_target_price_policy")) in {
        "none",
        "not applicable",
    }


def _strategic_named_direct_equity_reconciliation_checks(
    root: Path,
    gate_manifest: Any,
) -> list[tuple[str, bool, str, str]]:
    """Reconcile every named open-universe T3 issuer to its evidence packets."""

    if not isinstance(gate_manifest, Mapping):
        return []
    controls = gate_manifest.get("strategy_controls")
    if not isinstance(controls, Mapping):
        return []
    raw_tickers = controls.get("named_t3_direct_equity_tickers")
    named_tickers = (
        [str(ticker).strip() for ticker in raw_tickers if str(ticker).strip()]
        if isinstance(raw_tickers, Sequence)
        and not isinstance(raw_tickers, (str, bytes, bytearray))
        else []
    )
    valuation_rows = _valuation_rows(
        _load_first_json(root, "data/current_valuation_model_*.json")
    )
    valuation_tickers = {
        str(row.get("ticker")).strip()
        for row in valuation_rows
        if _has_items(row.get("ticker"))
    }
    broker_rows = _broker_consensus_rows(
        _load_first_json(root, "data/broker_street_consensus_*.json")
    )
    broker_tickers = {
        str(row.get("ticker")).strip()
        for row in broker_rows
        if _has_items(row.get("ticker"))
    }
    named_set = set(named_tickers)
    missing_valuation = sorted(named_set - valuation_tickers)
    missing_broker = sorted(named_set - broker_tickers)
    return [
        (
            "strategic named T3 direct-equity registry reconciles to valuation universe",
            not missing_valuation and len(named_tickers) == len(named_set),
            ", ".join(missing_valuation) or f"matched={len(named_tickers)}",
            "S",
        ),
        (
            "strategic named T3 direct-equity registry reconciles to broker/Street universe",
            not missing_broker and len(named_tickers) == len(named_set),
            ", ".join(missing_broker) or f"matched={len(named_tickers)}",
            "S",
        ),
    ]


def _strategic_allocation_uses_framework_signoff(gate_manifest: Any) -> bool:
    """Return whether a strategic case adopts the framework-only sign-off schema.

    The project contains two compatible strategic-allocation families:
    legacy closed-universe research notes, whose documented `PASS` sign-off
    predates the framework-only schema, and framework cases that explicitly
    separate research publication from implementation authorization.  The
    latter must receive the extra non-authorization checks; the former must
    retain its legacy validation path.
    """

    if not isinstance(gate_manifest, Mapping):
        return False
    if _strategic_allocation_uses_open_item_admission(gate_manifest):
        return True
    return _normalize(gate_manifest.get("publication_status")) in {
        "research_framework_pass_implementation_not_approved",
        "pass_research_framework_implementation_not_approved",
    }


def _strategic_allocation_depth_checks(
    root: Path,
    gate_manifest: Any,
) -> list[tuple[str, bool, str, str]]:
    """Check the evidence boundary for a strategic allocation research memo.

    This covers a strategic allocation while no direct issuer has crossed the
    item-level admission boundary.  If an open-universe case names a T3 direct
    equity, ``evaluate_research_case_quality`` additionally runs the issuer
    valuation and broker-consensus gates.  The strategy checks here substitute
    explicit return-evidence, risk-budget and non-authorization checks only
    while that issuer-level review is not yet required.
    """

    checks: list[tuple[str, bool, str, str]] = []
    controls = (
        gate_manifest.get("strategy_controls")
        if isinstance(gate_manifest, Mapping)
        else None
    )
    checks.append(
        (
            "strategic allocation manifest controls",
            isinstance(controls, Mapping),
            (
                "strategy_controls"
                if isinstance(controls, Mapping)
                else "missing strategy_controls"
            ),
            "S",
        )
    )
    if not isinstance(controls, Mapping):
        return checks

    open_item_admission = _strategic_allocation_uses_open_item_admission(gate_manifest)
    direct_weight = _first_float(controls.get("initial_direct_stock_weight"))
    direct_aggregate_cap = _first_float(controls.get("direct_stock_aggregate_cap"))
    direct_single_cap = _first_float(controls.get("direct_stock_single_issuer_cap"))
    if open_item_admission:
        research_policy = str(controls.get("research_universe_policy") or "")
        issuer_policy = _normalize(controls.get("issuer_target_price_policy"))
        named_t3_tickers = controls.get("named_t3_direct_equity_tickers")
        named_t3_count = _int_or_none(controls.get("named_t3_direct_equity_count"))
        named_t3_list = (
            [str(ticker).strip() for ticker in named_t3_tickers if str(ticker).strip()]
            if isinstance(named_t3_tickers, Sequence)
            and not isinstance(named_t3_tickers, (str, bytes, bytearray))
            else []
        )
        checks.append(
            (
                "strategic allocation open research universe has item-level direct-equity admission",
                direct_weight == 0.0
                and direct_aggregate_cap is None
                and direct_single_cap is None
                and "open" in _normalize(research_policy)
                and "direct" in _normalize(research_policy)
                and issuer_policy == "required_for_each_named_t3_direct_equity"
                and named_t3_count is not None
                and named_t3_count == len(named_t3_list)
                and len(named_t3_list) == len(set(named_t3_list)),
                f"initial={direct_weight}; aggregate_cap={direct_aggregate_cap}; single_cap={direct_single_cap}; issuer_policy={issuer_policy or 'missing'}; named_t3={named_t3_count}; tickers={len(named_t3_list)}",
                "S",
            )
        )
    else:
        checks.append(
            (
                "strategic allocation direct-stock scope is zero and capped",
                direct_weight == 0.0
                and direct_aggregate_cap is not None
                and direct_single_cap is not None
                and 0.0 <= direct_single_cap <= direct_aggregate_cap <= 1.0
                and _normalize(controls.get("issuer_target_price_policy"))
                in {"none", "not applicable"},
                f"initial={direct_weight}; aggregate_cap={direct_aggregate_cap}; single_cap={direct_single_cap}",
                "S",
            )
        )

    required = (
        gate_manifest.get("required_artifacts")
        if isinstance(gate_manifest, Mapping)
        else None
    )
    model_paths = [
        str(path)
        for path in required or []
        if isinstance(path, str)
        and re.fullmatch(r"data/portfolio_return_model_\d{8}\.json", path)
    ]
    checks.append(
        (
            "strategic allocation declares exactly one return model",
            len(model_paths) == 1,
            ", ".join(model_paths) or "missing",
            "S",
        )
    )
    if len(model_paths) != 1:
        return checks

    return_model, error = _load_json_document(root / model_paths[0])
    checks.append(
        ("strategic allocation return model parses", error is None, error or "", "S")
    )
    if not isinstance(return_model, Mapping):
        return checks

    weights = return_model.get("active_base_core")
    rows = (
        [row for row in weights if isinstance(row, Mapping)]
        if isinstance(weights, Sequence)
        and not isinstance(weights, (str, bytes, bytearray))
        else []
    )
    total_weight = sum(_first_float(row.get("weight")) or 0.0 for row in rows)
    checks.append(
        (
            "strategic allocation return-model weights sum to 100%",
            abs(total_weight - 1.0) < 1e-9,
            f"{total_weight:.6f}",
            "S",
        )
    )
    checks.append(
        (
            "strategic allocation has no point return forecast",
            _normalize(return_model.get("model_type")).startswith(
                "strategic allocation planning range"
            ),
            str(return_model.get("model_type") or "missing"),
            "S",
        )
    )

    total_return = return_model.get("total_return_measurement")
    cash_ledger = return_model.get("cash_ledger_and_accounting")
    cash_policy = return_model.get("cash_distribution_policy")
    cash_objective_required = controls.get("cash_objective_required")
    legacy_cash_measurement = return_model.get("cash_measurement")
    serialized_model = json.dumps(return_model, ensure_ascii=False).lower()
    legacy_cash_policy = (
        isinstance(legacy_cash_measurement, Mapping)
        and bool(
            str(legacy_cash_measurement.get("net_cash_yield_formula") or "").strip()
        )
        and bool(legacy_cash_measurement.get("eligible_receipts"))
        and bool(str(legacy_cash_measurement.get("failure_rule") or "").strip())
        and isinstance(total_return, Mapping)
        and bool(str(total_return.get("formula") or "").strip())
        and bool(str(total_return.get("reinvestment_rule") or "").strip())
        and bool(str(total_return.get("failure_rule") or "").strip())
    )
    single_objective_cash_policy = (
        isinstance(cash_ledger, Mapping)
        and bool(cash_ledger.get("eligible_receipt_types"))
        and bool(cash_ledger.get("not_receipt_types"))
        and bool(str(cash_ledger.get("capital_repayment_like_component") or "").strip())
        and isinstance(cash_policy, Mapping)
        and cash_policy.get("automatic_reinvestment") is False
        and cash_policy.get("mandatory_retention") is False
        and isinstance(total_return, Mapping)
        and bool(str(total_return.get("formula") or "").strip())
        and bool(str(total_return.get("reinvestment_rule") or "").strip())
        and "once" in _normalize(total_return.get("cash_receipt_accounting_rule"))
        and all(
            token not in serialized_model
            for token in (
                "cash_target_pct",
                "net_cash_yield_formula",
                "covered_net_cash_formula",
                "cash_target_failure",
                "rolling_twelve_month_actual_net_cash_target_pct",
                "b2_income",
            )
        )
    )
    checks.append(
        (
            "strategic allocation cash and total-return measurement are explicit",
            (
                single_objective_cash_policy
                if cash_objective_required is False or isinstance(cash_ledger, Mapping)
                else legacy_cash_policy
            ),
            (
                "single-objective cash-ledger controls"
                if cash_objective_required is False or isinstance(cash_ledger, Mapping)
                else "legacy cash and total-return controls"
            ),
            "S",
        )
    )
    return_evidence = return_model.get("return_evidence")
    checks.append(
        (
            "strategic allocation return evidence explicitly blocks implementation",
            isinstance(return_evidence, Mapping)
            and _implementation_is_blocked(
                _normalize(return_evidence.get("implementation_status"))
            )
            and bool(str(return_evidence.get("formal_test_requirement") or "").strip())
            and bool(str(return_evidence.get("benchmark_requirement") or "").strip()),
            "return_evidence implementation boundary",
            "S",
        )
    )
    risk_budget = return_model.get("risk_budget")
    checks.append(
        (
            "strategic allocation risk budget explicitly blocks implementation",
            isinstance(risk_budget, Mapping)
            and _implementation_is_blocked(
                _normalize(risk_budget.get("implementation_status"))
            )
            and bool(str(risk_budget.get("approval_requirement") or "").strip())
            and bool(str(risk_budget.get("loss_limit") or "").strip()),
            "risk_budget implementation boundary",
            "S",
        )
    )

    activation = return_model.get("activation_controls")
    direct_activation = (
        activation.get("direct_equities")
        if open_item_admission and isinstance(activation, Mapping)
        else (
            activation.get("direct_high_dividend_stocks")
            if isinstance(activation, Mapping)
            else None
        )
    )
    direct_review = (
        direct_activation.get("required_independent_review")
        if isinstance(direct_activation, Mapping)
        else None
    )
    direct_review_count = (
        len(direct_review)
        if isinstance(direct_review, Sequence)
        and not isinstance(direct_review, (str, bytes, bytearray))
        else 0
    )
    if open_item_admission:
        checks.append(
            (
                "strategic allocation direct-equity dossier is complete before T3",
                isinstance(direct_activation, Mapping)
                and _first_float(direct_activation.get("initial_weight")) == 0.0
                and _first_float(direct_activation.get("aggregate_cap")) is None
                and _first_float(direct_activation.get("single_issuer_cap")) is None
                and "open"
                in _normalize(direct_activation.get("current_model_treatment"))
                and direct_review_count >= 8,
                f"review_items={direct_review_count}",
                "S",
            )
        )
    reit_activation = (
        activation.get("public_reits") if isinstance(activation, Mapping) else None
    )
    if open_item_admission:
        checks.append(
            (
                "strategic allocation open-universe REIT controls are non-forcing",
                isinstance(reit_activation, Mapping)
                and _first_float(reit_activation.get("initial_weight"))
                == _first_float(controls.get("reit_initial_weight"))
                and reit_activation.get("aggregate_cap") is None
                and bool(reit_activation.get("required_checks"))
                and "protected liquidity"
                in _normalize(reit_activation.get("inactive_behavior")),
                "REIT eligibility and fallback",
                "S",
            )
        )
    else:
        checks.append(
            (
                "strategic allocation REIT activation controls are non-forcing",
                isinstance(reit_activation, Mapping)
                and _first_float(reit_activation.get("initial_weight"))
                == _first_float(controls.get("reit_initial_weight"))
                and bool(reit_activation.get("required_checks"))
                and "protected liquidity"
                in _normalize(reit_activation.get("inactive_behavior")),
                "REIT eligibility and fallback",
                "S",
            )
        )
    return checks


def _strategic_signoff_checks(
    final_signoff: Any,
    *,
    cash_objective_required: bool | None = None,
) -> list[tuple[str, bool, str, str]]:
    if not isinstance(final_signoff, Mapping):
        return [
            (
                "strategic allocation final sign-off is object",
                False,
                "not an object",
                "S",
            )
        ]

    status = _normalize(
        final_signoff.get("signoff_status") or final_signoff.get("status")
    )
    framework_status = _normalize(final_signoff.get("framework_status"))
    implementation_status = _normalize(final_signoff.get("implementation_status"))
    checks: list[tuple[str, bool, str, str]] = [
        (
            "strategic allocation research-framework sign-off status pass",
            status in STRATEGIC_RESEARCH_FRAMEWORK_SIGNOFF_STATUSES
            and framework_status in LEGACY_PASS_SIGNOFF_STATUSES,
            f"signoff={status or 'missing'}; framework={framework_status or 'missing'}",
            "S",
        ),
        (
            "strategic allocation implementation explicitly not approved",
            implementation_status in IMPLEMENTATION_BLOCKED_STATUSES,
            implementation_status or "missing",
            "S",
        ),
        (
            "strategic allocation live execution explicitly unauthorized",
            final_signoff.get("live_execution_authorized") is False,
            str(final_signoff.get("live_execution_authorized")),
            "S",
        ),
    ]

    gates_ok, gates_detail = _strategic_implementation_gates_are_blocking(
        final_signoff.get("implementation_gates")
    )
    checks.append(
        (
            "strategic allocation return-evidence and risk-budget gates block implementation",
            gates_ok,
            gates_detail,
            "S",
        )
    )
    execution_ok, execution_detail = _strategic_execution_is_inactive(
        final_signoff.get("execution_eligibility")
    )
    checks.append(
        (
            "strategic allocation execution eligibility remains inactive",
            execution_ok,
            execution_detail,
            "S",
        )
    )
    disclosure_ok, disclosure_detail = _strategic_material_claims_disclosed(
        final_signoff,
        cash_objective_required=cash_objective_required,
    )
    checks.append(
        (
            "strategic allocation material claims are explicitly disclosed",
            disclosure_ok,
            disclosure_detail,
            "S",
        )
    )
    return checks


def _strategic_implementation_gates_are_blocking(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, Mapping):
        return False, "implementation_gates missing or not an object"
    required = ("return_evidence", "risk_budget", "suitability", "execution")
    values = {key: _normalize(payload.get(key)) for key in required}
    missing = [key for key, value in values.items() if not value]
    incorrect = [
        key for key, value in values.items() if not _implementation_is_blocked(value)
    ]
    detail = "; ".join(f"{key}={value or 'missing'}" for key, value in values.items())
    return not missing and not incorrect, detail


def _strategic_execution_is_inactive(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, Mapping):
        return False, "execution_eligibility missing or not an object"
    status = _normalize(payload.get("status"))
    q = _first_float(payload.get("q"))
    active = payload.get("live_execution_authorized")
    return (
        _implementation_is_blocked(status) and q == 0.0 and active is False,
        f"status={status or 'missing'}; q={q}; live_execution_authorized={active}",
    )


def _strategic_material_claims_disclosed(
    payload: Any,
    *,
    cash_objective_required: bool | None = None,
) -> tuple[bool, str]:
    if not isinstance(payload, Mapping):
        return False, "final sign-off missing or not an object"
    disclosure = payload.get("material_claim_disclosure")
    if not isinstance(disclosure, Mapping):
        return False, "material_claim_disclosure missing or not an object"
    missing = [
        key
        for key in STRATEGIC_MATERIAL_DISCLOSURE_KEYS
        if disclosure.get(key) is not True
    ]
    if cash_objective_required is False:
        if disclosure.get("cash_objective_not_required") is not True:
            missing.append("cash_objective_not_required")
        if "cash_target_not_guarantee" in disclosure:
            missing.append("legacy_cash_target_not_guarantee_must_be_absent")
    elif disclosure.get("cash_target_not_guarantee") is not True:
        missing.append("cash_target_not_guarantee")
    disclosure_text = " ".join(
        str(value)
        for value in (
            payload.get("decision"),
            payload.get("residual_risks"),
            payload.get("implementation_rationale"),
        )
    )
    normalized_text = _normalize(disclosure_text)
    reader_boundary_present = (
        "not guarantee" in normalized_text or "not guaranteed" in normalized_text
    ) and ("not approved" in normalized_text or "not authorized" in normalized_text)
    detail = ", ".join(missing) if missing else "all structured boundaries disclosed"
    if not reader_boundary_present:
        detail = f"{detail}; reader-facing decision/residual rationale lacks explicit not-guarantee/not-approved wording"
    return not missing and reader_boundary_present, detail


def _strategic_residual_risks_disclosed(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, Mapping):
        return False, "final sign-off missing or not an object"
    residual_risks = payload.get("residual_risks")
    if (
        not isinstance(residual_risks, Sequence)
        or isinstance(residual_risks, (str, bytes, bytearray))
        or not residual_risks
    ):
        return False, "residual_risks must list implementation blockers"
    text = _normalize(" ".join(str(item) for item in residual_risks))
    required_concepts = (
        ("return", "evidence"),
        ("risk", "budget"),
        ("not approved", "not authorized"),
    )
    missing = [
        "/".join(concept)
        for concept in required_concepts
        if not any(term in text for term in concept)
    ]
    return (
        not missing,
        (
            ", ".join(missing)
            if missing
            else "return evidence, risk budget and authorization blockers disclosed"
        ),
    )


def _implementation_is_blocked(status: str) -> bool:
    return status in INACTIVE_EXECUTION_STATUSES or status.startswith(
        (
            "blocked",
            "not_approved",
            "not approved",
            "not_authorized",
            "not authorized",
            "not_run",
            "not run",
            "pending",
        )
    )


def _extract_review_findings(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [
            cast(Mapping[str, Any], item)
            for item in payload
            if isinstance(item, Mapping)
        ]
    if isinstance(payload, Mapping):
        for key in ("findings", "issues", "items", "review_findings"):
            value = payload.get(key)
            if isinstance(value, list):
                return [
                    cast(Mapping[str, Any], item)
                    for item in value
                    if isinstance(item, Mapping)
                ]
        for value in payload.values():
            if isinstance(value, list) and all(
                isinstance(item, Mapping) for item in value
            ):
                return [cast(Mapping[str, Any], item) for item in value]
    return []


def _review_severity(finding: Mapping[str, Any]) -> str:
    severity = _normalize(
        finding.get("severity") or finding.get("level") or finding.get("priority")
    ).upper()
    if severity.startswith("S"):
        return "S"
    if severity.startswith("A"):
        return "A"
    return "B"


def _review_status(finding: Mapping[str, Any]) -> str:
    return _normalize(
        finding.get("status")
        or finding.get("lifecycle_status")
        or finding.get("state")
        or "open"
    )


def _review_waived(finding: Mapping[str, Any]) -> bool:
    waiver_status = _normalize(finding.get("waiver_status"))
    return (
        _review_status(finding) == "waived"
        or waiver_status == "waived"
        or _truthy(finding.get("waived"))
    )


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return _normalize(value) in {"1", "true", "yes", "y", "waived"}


def _extract_publishability_score(review_log: str) -> int | None:
    matches = list(
        re.finditer(
            r"publishability(?:\s+score|_score)\D+(\d{1,3})",
            review_log,
            re.IGNORECASE,
        )
    )
    if matches:
        return int(matches[-1].group(1))
    fallback = re.search(
        r"(?:publication|research[- ]framework)\s+score\D+(\d{1,3})",
        review_log,
        re.IGNORECASE,
    )
    return int(fallback.group(1)) if fallback else None


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _source_summary(
    source: str,
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    total = len(records)
    error_count = sum(1 for record in records if _has_items(record.get("errors")))
    warning_count = sum(1 for record in records if _has_items(record.get("warnings")))
    ok_count = sum(1 for record in records if record.get("ok", True) is not False)
    quality_counts: dict[str, int] = {}
    latency_values: list[float] = []

    degraded_count = 0
    unavailable_count = 0
    for record in records:
        quality = _quality_tier(record)
        quality_counts[quality] = quality_counts.get(quality, 0) + 1
        if quality in DEGRADED_QUALITY_TIERS:
            degraded_count += 1
        if quality == "unavailable":
            unavailable_count += 1
        latency = _float_or_none(record.get("latency_ms"))
        if latency is not None:
            latency_values.append(latency)

    avg_latency = (
        round(sum(latency_values) / len(latency_values), 2) if latency_values else None
    )
    error_rate = error_count / total if total else 0.0
    warning_rate = warning_count / total if total else 0.0
    degraded_rate = degraded_count / total if total else 0.0
    latency_penalty = min((avg_latency or 0.0) / 1000 * 5, 15)
    score = (
        100 - error_rate * 60 - degraded_rate * 25 - warning_rate * 10 - latency_penalty
    )
    score = round(max(min(score, 100.0), 0.0), 2)

    status = "good"
    if score < 50 or error_rate >= 0.5:
        status = "failing"
    elif score < 80 or degraded_count:
        status = "degraded"

    return {
        "source": source,
        "record_count": total,
        "ok_count": ok_count,
        "warning_count": warning_count,
        "error_count": error_count,
        "degraded_count": degraded_count,
        "unavailable_count": unavailable_count,
        "avg_latency_ms": avg_latency,
        "quality_counts": quality_counts,
        "health_score": score,
        "status": status,
    }


def _evaluate_skill_case(case: SkillEvalCase) -> dict[str, Any]:
    normalized = _normalize(case.response)
    required_hits = [
        term for term in case.required_terms if _normalize(term) in normalized
    ]
    missing_required = [
        term for term in case.required_terms if _normalize(term) not in normalized
    ]
    forbidden_hits = [
        term
        for term in case.forbidden_terms
        if _has_unnegated_forbidden_term(normalized, _normalize(term))
    ]
    passed = not missing_required and not forbidden_hits
    score = 100 - len(missing_required) * 20 - len(forbidden_hits) * 50
    return {
        "name": case.name,
        "passed": passed,
        "score": max(score, 0),
        "required_hits": required_hits,
        "missing_required": missing_required,
        "forbidden_hits": forbidden_hits,
        "metadata": dict(case.metadata),
    }


def _has_unnegated_forbidden_term(response: str, term: str) -> bool:
    """Return whether a forbidden action is asserted rather than explicitly denied."""
    if not term:
        return False

    for match in re.finditer(re.escape(term), response):
        sentence_start = max(
            response.rfind(".", 0, match.start()),
            response.rfind("!", 0, match.start()),
            response.rfind("?", 0, match.start()),
            response.rfind(";", 0, match.start()),
            response.rfind("。", 0, match.start()),
            response.rfind("！", 0, match.start()),
            response.rfind("？", 0, match.start()),
            response.rfind("；", 0, match.start()),
            response.rfind("\n", 0, match.start()),
        )
        prefix = response[sentence_start + 1 : match.start()].strip()
        clause = re.split(r"(?:\bbut\b|\bhowever\b|但是|但|而是|；|;|，|,)", prefix)[
            -1
        ].strip()
        explicit_english_denial = re.search(
            r"(?:\b(?:do|does|did|will|shall|can)\s+not\b|\b(?:cannot|can't|won't|never|not)\b)(?:\s+\w+){0,3}\s*$",
            clause,
        )
        explicit_chinese_denial = re.search(
            r"(?:不会|不能|不可|不得|禁止|严禁|不予)(?:[\s\w\u4e00-\u9fff、:：-]){0,40}$",
            clause,
        )
        if explicit_english_denial is None and explicit_chinese_denial is None:
            return True
    return False


def _resolve_path(value: Any, root: Path | None) -> Path:
    path = Path(str(value or ""))
    if root is not None and not path.is_absolute():
        return root / path
    return path


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _quality_tier(record: Mapping[str, Any]) -> str:
    for key in ("quality_tier", "level", "quality", "data_quality"):
        value = record.get(key)
        if isinstance(value, Mapping):
            nested = _quality_tier(cast(Mapping[str, Any], value))
            if nested != "unknown":
                return nested
        elif value:
            return _normalize(value)
    return "unknown"


def _tuple_from_value(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),)


def _json_ready_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    return {str(key): _json_ready(item) for key, item in value.items()}


def _json_ready(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return _json_ready_mapping(cast(Mapping[str, Any], value))
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_json_ready(item) for item in value]
    return str(value)


def _has_items(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return bool(value)
    return bool(str(value).strip())


def _broker_value_usable(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return _normalize(value) not in BROKER_UNAVAILABLE_VALUES
    if isinstance(value, Mapping):
        return any(_broker_value_usable(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return any(_broker_value_usable(item) for item in value)
    return bool(str(value).strip())


def _broker_row_external(row: Mapping[str, Any]) -> bool:
    broker = _normalize(row.get("broker"))
    source_quality = _normalize(row.get("source_quality"))
    source_path = _normalize(row.get("source_path"))
    if source_quality not in BROKER_EXTERNAL_POSITIVE_SOURCE_QUALITIES:
        return False
    if source_quality in BROKER_INTERNAL_SOURCE_QUALITIES:
        return False
    if any(term in broker for term in BROKER_INTERNAL_NAME_TERMS):
        return False
    if source_path.startswith("analysis/") or source_path.startswith(
        "data/current_valuation"
    ):
        return False
    return bool(broker)


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def _text(value: Any, default: str) -> str:
    text = str(value or "").strip()
    return text or default


def _score_status(score: float) -> str:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "pass"
    if score >= 50:
        return "weak"
    return "fail"
