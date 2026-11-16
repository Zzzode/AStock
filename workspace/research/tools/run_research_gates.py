#!/usr/bin/env python3
"""Run publication gates for an AStock research case.

This runner is intentionally stricter than a layout verifier. It checks the
workflow artifacts that prove a research report went through evidence intake,
review/repair cycles, model reproducibility, final sign-off, and case-local
verification before publication.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, cast


EXPECTED_REVIEW_CYCLES = (
    "R0_evidence",
    "R1_model",
    "R2_draft",
    "R3_render_compliance",
    "R4_final_ic",
)

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

REQUIRED_ROOT_ARTIFACTS = (
    "research_brief.md",
    "gate_manifest.md",
    "gate_manifest.json",
    "artifact_contract.md",
    "artifact_contract.json",
    "review_log.md",
    "final_signoff.md",
    "final_signoff.json",
    "research_workflow_eval.md",
    "research_workflow_eval.json",
)

REQUIRED_MD_JSON_PAIRS = (
    "gate_manifest",
    "artifact_contract",
    "final_signoff",
    "research_workflow_eval",
    "source_exhaustion_log",
    "data/source_registry",
    "data/claim_audit",
)

INDUSTRY_CHAIN_MD_JSON_PAIRS = (
    "data/valuation_triage_20260630",
    "data/core_candidate_valuation_disposition_20260630",
    "data/residual_proxy_field_audit_20260701",
)

FINAL_SIGNOFF_KEYS = (
    "case_id",
    "report_type",
    "data_cutoff",
    "pdf_path",
    "page_count",
    "publishability_score",
    "verifier_results",
    "open_s_count",
    "open_a_count",
    "residual_risks",
    "signoff_status",
)

INDUSTRY_CHAIN_ARTIFACTS = (
    "analysis/template_brief.md",
    "analysis/full_chain_taxonomy.md",
    "analysis/chain_business_research.md",
    "analysis/core_vs_satellite_universe.md",
    "analysis/coverage_gap_matrix.md",
    "analysis/supply_chain_model.md",
    "analysis/company_fundamental_cards.md",
    "analysis/core_candidate_company_cards.md",
    "analysis/valuation_coverage_reconciliation.md",
    "analysis/value_chain_economics.md",
    "analysis/chain_earnings_bridge.md",
    "analysis/competitive_landscape.md",
    "analysis/variant_perception.md",
    "analysis/field_evidence_completion_audit.md",
    "analysis/residual_proxy_field_audit.md",
    "data/chain_business_matrix_20260630.json",
    "data/supply_chain_relationships.json",
    "data/customer_chain_audit.json",
    "data/field_evidence_completion_20260701.json",
    "data/proxy_field_official_filing_collection_20260701.json",
    "data/residual_proxy_field_audit_20260701.json",
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

# A research-framework publication is deliberately narrower than an
# implementation approval.  Keep these states separate so a strategic
# allocation case cannot make a q=0 / evidence-pending design look like a
# live investment authorization.  Non-strategic reports retain the legacy
# PASS-only contract below.
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

INDUSTRY_CHAIN_DEPTH_GATES = (
    "valuation_coverage_reconciliation",
    "supply_chain_chapter_prose_led",
    "chain_business_matrix_depth",
    "residual_proxy_field_depth",
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
    ),
}

INDUSTRY_DEPTH_TERM_SETS: dict[str, tuple[str, tuple[str, ...]]] = {
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
    ),
}


class GateRunner:
    def __init__(self, case_dir: Path) -> None:
        self.case_dir = case_dir.resolve()
        self.repo_root = Path(__file__).resolve().parents[3]
        self.passes: list[str] = []
        self.failures: list[str] = []
        self.warnings: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        message = f"{name}: {detail}" if detail else name
        if condition:
            self.passes.append(message)
        else:
            self.failures.append(message)

    def warn(self, name: str, detail: str = "") -> None:
        self.warnings.append(f"{name}: {detail}" if detail else name)

    def exists(self, rel: str) -> Path:
        path = self.case_dir / rel
        self.check(f"exists {rel}", path.exists())
        return path

    def run(self) -> int:
        self.check("case directory exists", self.case_dir.exists(), str(self.case_dir))
        if not self.case_dir.exists():
            return self.finish()

        for rel in REQUIRED_ROOT_ARTIFACTS:
            self.exists(rel)
        for stem in REQUIRED_MD_JSON_PAIRS:
            self.check(
                f"md/json pair present {stem}",
                (self.case_dir / f"{stem}.md").exists()
                and (self.case_dir / f"{stem}.json").exists(),
            )

        gate_manifest = self.load_json("gate_manifest.json")
        artifact_contract = self.load_json("artifact_contract.json")
        final_signoff = self.load_json("final_signoff.json")
        workflow_eval = self.load_json("research_workflow_eval.json")
        strategic_allocation_case = case_is_strategic_allocation(gate_manifest)
        # A manifest-declared strategic allocation is a mutually exclusive case
        # type.  Its prose can legitimately say that it is *not* an industry
        # chain study; do not turn that negated wording into an industry gate.
        industry_case = (
            not strategic_allocation_case
            and case_requires_industry_chain(gate_manifest, self.case_text())
        )

        if industry_case:
            for stem in INDUSTRY_CHAIN_MD_JSON_PAIRS:
                self.check(
                    f"md/json pair present {stem}",
                    (self.case_dir / f"{stem}.md").exists()
                    and (self.case_dir / f"{stem}.json").exists(),
                )

        required_artifacts = set()
        required_artifacts.update(artifact_paths_from_payload(gate_manifest))
        required_artifacts.update(artifact_paths_from_payload(artifact_contract))
        for rel in sorted(required_artifacts):
            self.check(
                f"manifest artifact exists {rel}",
                resolve_artifact(self.case_dir, rel).exists(),
            )

        self.check_gate_manifest_depth(
            gate_manifest,
            INDUSTRY_CHAIN_DEPTH_GATES if industry_case else (),
            base_required_gates=(
                STRATEGIC_ALLOCATION_DEPTH_GATES
                if strategic_allocation_case
                else GATE_MANIFEST_DEPTH_GATES
            ),
        )
        self.check_artifact_contract_depth(artifact_contract)
        self.check_review_lifecycle(gate_manifest)
        self.check_source_governance()
        if strategic_allocation_case:
            self.check_strategic_allocation_depth(gate_manifest)
        else:
            self.check_valuation_reproducibility()
            self.check_valuation_model_depth()

        if industry_case:
            self.check_valuation_coverage_reconciliation()
            self.check_supply_chain_chapter_prose_led()
        elif not strategic_allocation_case:
            self.check_single_stock_depth()
        if strategic_allocation_case:
            self.check(
                "issuer broker/target-price gate correctly skipped",
                strategic_allocation_can_skip_issuer_broker_gate(gate_manifest),
                "strategic cases may skip issuer targets only when direct equities are either permanently excluded or no named T3 issuer has entered the decision universe",
            )
            if not strategic_allocation_can_skip_issuer_broker_gate(gate_manifest):
                self.check_valuation_reproducibility()
                self.check_valuation_model_depth()
                self.check_broker_street_consensus(
                    final_signoff,
                    allow_zero_weight_exhaustion=False,
                )
                self.check_strategic_named_direct_equity_reconciliation(
                    gate_manifest
                )
        else:
            self.check_broker_street_consensus(
                final_signoff,
                allow_zero_weight_exhaustion=not industry_case,
            )
        self.check_final_signoff(
            final_signoff,
            gate_manifest=gate_manifest,
            strategic_allocation_case=strategic_allocation_case,
        )
        self.check_workflow_eval(
            workflow_eval,
            strategic_allocation_case=strategic_allocation_case,
        )
        self.check_case_verifier()
        self.check_reader_facing_no_generic_placeholders()

        if industry_case:
            self.check_industry_chain_artifacts()
            self.check_industry_chain_depth()
            self.check_chain_business_matrix_depth()
            self.check_supply_chain_relationship_depth()
            self.check_customer_chain_audit_depth()
            self.check_field_evidence_completion_depth()
            self.check_proxy_field_official_collection_depth()
            self.check_residual_proxy_field_audit_depth()
            self.check_growth_driver_depth()
            self.check_industry_chain_verifier()
        else:
            self.warn("industry-chain verifier skipped", "case not marked as full-chain")

        return self.finish()

    def load_json(self, rel: str) -> Any:
        path = self.case_dir / rel
        if not path.exists():
            self.check(f"json parses {rel}", False, "missing")
            return {}
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive CLI output
            self.check(f"json parses {rel}", False, str(exc))
            return {}
        self.check(f"json parses {rel}", True)
        return payload

    def load_first_json(self, pattern: str) -> Any:
        matches = sorted(self.case_dir.glob(pattern), reverse=True)
        if not matches:
            return {}
        rel = str(matches[0].relative_to(self.case_dir))
        return self.load_json(rel)

    def case_text(self) -> str:
        return "\n".join(
            read_text(self.case_dir / rel)
            for rel in (
                "research_brief.md",
                "analysis/template_brief.md",
                "review_log.md",
            )
        )

    def check_review_lifecycle(self, gate_manifest: Any) -> None:
        expected_cycles = expected_review_cycles(gate_manifest)
        review_log = read_text(self.case_dir / "review_log.md")
        score = extract_publishability_score(review_log)
        self.check("publishability score present", score is not None)
        if score is not None:
            self.check("publishability score >= 90", score >= 90, str(score))

        open_s_count = 0
        open_unwaived_a_count = 0
        for cycle in expected_cycles:
            findings_path = self.case_dir / f"review_findings_{cycle}.json"
            self.check(f"review findings present {cycle}", findings_path.exists())
            if not findings_path.exists():
                continue
            payload = self.load_json(findings_path.name)
            for finding in extract_review_findings(payload):
                severity = review_severity(finding)
                status = review_status(finding)
                waived = review_waived(finding)
                if severity == "S" and status not in CLOSED_REVIEW_STATUSES:
                    open_s_count += 1
                if (
                    severity == "A"
                    and status not in CLOSED_REVIEW_STATUSES
                    and not waived
                ):
                    open_unwaived_a_count += 1

            if cycle != "R4_final_ic":
                self.check(
                    f"repair plan pair present {cycle}",
                    (self.case_dir / f"repair_plan_{cycle}.md").exists()
                    and (self.case_dir / f"repair_plan_{cycle}.json").exists(),
                )

        self.check("zero open S-Level findings", open_s_count == 0, str(open_s_count))
        self.check(
            "zero open unwaived A-Level findings",
            open_unwaived_a_count == 0,
            str(open_unwaived_a_count),
        )

    def check_gate_manifest_depth(
        self,
        gate_manifest: Any,
        extra_required_gates: Sequence[str] = (),
        base_required_gates: Sequence[str] = GATE_MANIFEST_DEPTH_GATES,
    ) -> None:
        if not isinstance(gate_manifest, Mapping):
            self.check("gate manifest depth gates complete", False, "not an object")
            return
        depth_gates = gate_manifest.get("depth_gates")
        if not isinstance(depth_gates, Sequence) or isinstance(
            depth_gates, (str, bytes, bytearray)
        ):
            self.check("gate manifest depth gates complete", False, "missing depth_gates")
            return
        normalized_gates = {normalize(gate) for gate in depth_gates}
        required_gates = (*base_required_gates, *extra_required_gates)
        missing = [gate for gate in required_gates if gate not in normalized_gates]
        self.check(
            "gate manifest depth gates complete",
            not missing,
            ", ".join(missing) if missing else "all depth gates present",
        )

    def check_artifact_contract_depth(self, artifact_contract: Any) -> None:
        if not isinstance(artifact_contract, Mapping):
            self.check("artifact contract declares field-level depth gates", False, "not an object")
            return
        artifacts = artifact_contract.get("artifacts")
        if not isinstance(artifacts, Sequence) or isinstance(
            artifacts, (str, bytes, bytearray)
        ):
            self.check("artifact contract declares field-level depth gates", False, "missing artifacts")
            return
        if not artifacts:
            self.check("artifact contract declares field-level depth gates", False, "empty artifacts")
            return

        missing_by_artifact: list[str] = []
        for item in artifacts:
            if not isinstance(item, Mapping):
                missing_by_artifact.append("<non-object>: all depth fields")
                continue
            path = str(item.get("path") or item.get("artifact") or "<missing path>")
            missing = [
                field
                for field in ARTIFACT_CONTRACT_DEPTH_FIELDS
                if not has_items(item.get(field))
            ]
            if missing:
                missing_by_artifact.append(f"{path}: {', '.join(missing)}")
        detail = "; ".join(missing_by_artifact[:8])
        if len(missing_by_artifact) > 8:
            detail += "; ..."
        self.check(
            "artifact contract declares field-level depth gates",
            not missing_by_artifact,
            detail,
        )

    def check_source_governance(self) -> None:
        for rel in (
            "data/source_registry.json",
            "data/claim_audit.json",
            "source_exhaustion_log.json",
        ):
            self.load_json(rel)
        self.check("sources directory present", (self.case_dir / "sources").exists())

    def check_strategic_allocation_depth(self, gate_manifest: Any) -> None:
        if not isinstance(gate_manifest, Mapping):
            self.check("strategic allocation manifest controls", False, "not an object")
            return

        controls = gate_manifest.get("strategy_controls")
        if not isinstance(controls, Mapping):
            self.check("strategic allocation manifest controls", False, "missing strategy_controls")
            return

        scope_id = str(gate_manifest.get("scope_id") or "").strip()
        open_item_admission = strategic_allocation_uses_open_item_admission(
            gate_manifest
        )
        self.check("strategic allocation scope ID declared", bool(scope_id), scope_id)
        direct_weight = first_float(controls.get("initial_direct_stock_weight"))
        self.check(
            "strategic allocation initial direct-stock weight zero",
            direct_weight == 0.0,
            str(direct_weight),
        )
        direct_aggregate_cap = first_float(controls.get("direct_stock_aggregate_cap"))
        direct_single_cap = first_float(controls.get("direct_stock_single_issuer_cap"))
        if open_item_admission:
            research_policy = normalize(controls.get("research_universe_policy"))
            issuer_policy = normalize(controls.get("issuer_target_price_policy"))
            raw_tickers = controls.get("named_t3_direct_equity_tickers")
            named_tickers = (
                [str(ticker).strip() for ticker in raw_tickers if str(ticker).strip()]
                if isinstance(raw_tickers, Sequence)
                and not isinstance(raw_tickers, (str, bytes, bytearray))
                else []
            )
            named_count = int_value(controls.get("named_t3_direct_equity_count"))
            self.check(
                "strategic allocation open research universe is explicitly gated",
                direct_aggregate_cap is None
                and direct_single_cap is None
                and "open" in research_policy
                and "direct" in research_policy
                and issuer_policy == "required_for_each_named_t3_direct_equity"
                and named_count is not None
                and named_count == len(named_tickers)
                and len(named_tickers) == len(set(named_tickers)),
                f"aggregate={direct_aggregate_cap}; single={direct_single_cap}; issuer_policy={issuer_policy or 'missing'}; named_t3={named_count}; tickers={len(named_tickers)}",
            )
        else:
            self.check(
                "strategic allocation direct-stock caps are legal",
                direct_aggregate_cap is not None
                and direct_single_cap is not None
                and 0.0 <= direct_single_cap <= direct_aggregate_cap <= 1.0,
                f"aggregate={direct_aggregate_cap}; single={direct_single_cap}",
            )
            self.check(
                "strategic allocation issuer target-price policy absent",
                normalize(controls.get("issuer_target_price_policy")) in {"none", "not applicable"},
                str(controls.get("issuer_target_price_policy")),
            )
        self.check(
            "strategic allocation REIT initial weight zero",
            first_float(controls.get("reit_initial_weight")) == 0.0,
            str(controls.get("reit_initial_weight")),
        )
        reit_project_count = int_value(controls.get("reit_required_independent_projects"))
        reit_single_cap = first_float(controls.get("reit_single_project_cap"))
        reit_aggregate_cap = first_float(controls.get("reit_aggregate_cap_after_activation"))
        if open_item_admission:
            self.check(
                "strategic allocation open-universe REIT controls are non-forcing",
                reit_project_count is not None
                and reit_project_count >= 1
                and reit_aggregate_cap is None,
                f"projects={reit_project_count}; per_project={reit_single_cap}; aggregate={reit_aggregate_cap}",
            )
        else:
            self.check(
                "strategic allocation REIT activation caps are legal and feasible",
                reit_project_count is not None
                and reit_project_count >= 1
                and reit_single_cap is not None
                and reit_aggregate_cap is not None
                and 0.0 < reit_single_cap <= reit_aggregate_cap <= 1.0
                and reit_project_count * reit_single_cap >= reit_aggregate_cap,
                f"projects={reit_project_count}; per_project={reit_single_cap}; aggregate={reit_aggregate_cap}",
            )

        declared_model_paths = [
            str(item)
            for item in (gate_manifest.get("required_artifacts") or [])
            if isinstance(item, str)
            and re.fullmatch(r"data/portfolio_return_model_\d{8}\.json", item)
        ]
        self.check(
            "strategic allocation declares exactly one return model",
            len(declared_model_paths) == 1,
            ", ".join(declared_model_paths) or "missing",
        )
        if len(declared_model_paths) != 1:
            return
        return_model = self.load_json(declared_model_paths[0])
        base_core = (
            return_model.get("active_base_core")
            if isinstance(return_model, Mapping)
            else None
        )
        valid_rows = [row for row in base_core if isinstance(row, Mapping)] if isinstance(base_core, Sequence) else []
        total_weight = sum(first_float(row.get("weight")) or 0.0 for row in valid_rows)
        self.check(
            "strategic allocation return-model weights sum to 100%",
            abs(total_weight - 1.0) < 1e-9,
            f"{total_weight:.6f}",
        )
        direct_rows = [
            row
            for row in valid_rows
            if normalize(row.get("asset"))
            in {"直接高股息股票", "direct high-dividend stocks", "direct_high_dividend_stocks", "direct equities", "direct_equities"}
        ]
        if open_item_admission:
            self.check(
                "strategic allocation current fallback has no direct-equity allocation",
                not direct_rows,
                f"rows={len(direct_rows)}",
            )
        else:
            self.check(
                "strategic allocation return-model direct-stock weight zero",
                len(direct_rows) == 1 and first_float(direct_rows[0].get("weight")) == 0.0,
                f"rows={len(direct_rows)}",
            )
        self.check(
            "strategic allocation has no point return forecast",
            isinstance(return_model, Mapping)
            and normalize(return_model.get("model_type")).startswith("strategic allocation planning range"),
            str(return_model.get("model_type") if isinstance(return_model, Mapping) else "missing"),
        )

        activation_controls = (
            return_model.get("activation_controls")
            if isinstance(return_model, Mapping)
            else None
        )
        direct_activation = (
            activation_controls.get("direct_equities")
            if open_item_admission and isinstance(activation_controls, Mapping)
            else activation_controls.get("direct_high_dividend_stocks")
            if isinstance(activation_controls, Mapping)
            else None
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
            self.check(
                "strategic allocation direct-equity dossier gates reconcile",
                isinstance(direct_activation, Mapping)
                and first_float(direct_activation.get("initial_weight")) == direct_weight
                and first_float(direct_activation.get("aggregate_cap")) is None
                and first_float(direct_activation.get("single_issuer_cap")) is None
                and "open" in normalize(direct_activation.get("current_model_treatment"))
                and direct_review_count >= 8,
                f"review_items={direct_review_count}",
            )
        else:
            self.check(
                "strategic allocation return-model direct-stock activation controls reconcile",
                isinstance(direct_activation, Mapping)
                and first_float(direct_activation.get("initial_weight")) == direct_weight
                and (
                    (direct_aggregate_cap == 0.0 and direct_single_cap == 0.0
                     and "excluded" in normalize(direct_activation.get("current_model_treatment")))
                    or bool(str(direct_activation.get("only_replaces") or "").strip())
                )
                and first_float(direct_activation.get("aggregate_cap"))
                == direct_aggregate_cap
                and first_float(direct_activation.get("single_issuer_cap"))
                == direct_single_cap
                and direct_review_count >= 7,
                f"review_items={direct_review_count}",
            )

        reit_activation = (
            activation_controls.get("public_reits")
            if isinstance(activation_controls, Mapping)
            else None
        )
        reit_checks = (
            reit_activation.get("required_checks")
            if isinstance(reit_activation, Mapping)
            else None
        )
        reit_check_count = (
            len(reit_checks)
            if isinstance(reit_checks, Sequence)
            and not isinstance(reit_checks, (str, bytes, bytearray))
            else 0
        )
        if open_item_admission:
            self.check(
                "strategic allocation open-universe REIT dossier controls reconcile",
                isinstance(reit_activation, Mapping)
                and first_float(reit_activation.get("initial_weight"))
                == first_float(controls.get("reit_initial_weight"))
                and int_value(reit_activation.get("activation_requires_independent_projects")) == reit_project_count
                and reit_activation.get("aggregate_cap") is None
                and "protected liquidity" in normalize(reit_activation.get("inactive_behavior"))
                and reit_check_count >= 7,
                f"check_items={reit_check_count}",
            )
        else:
            self.check(
                "strategic allocation return-model REIT activation controls reconcile",
                isinstance(reit_activation, Mapping)
                and first_float(reit_activation.get("initial_weight"))
                == first_float(controls.get("reit_initial_weight"))
                and int_value(reit_activation.get("activation_requires_independent_projects")) == reit_project_count
                and first_float(reit_activation.get("per_project_cap"))
                == reit_single_cap
                and first_float(
                    reit_activation.get("aggregate_cap"),
                    reit_activation.get("target_weight_after_activation"),
                )
                == reit_aggregate_cap
                and (
                    bool(str(reit_activation.get("funding_source_on_activation") or "").strip())
                    or (
                        "protected liquidity" in normalize(reit_activation.get("inactive_behavior"))
                        and "protected liquidity" in normalize(controls.get("fallback_policy"))
                    )
                )
                and reit_check_count >= 7,
                f"check_items={reit_check_count}",
            )

        cash_policy = (
            return_model.get("cash_distribution_policy")
            if isinstance(return_model, Mapping)
            else None
        )
        actual_measure = str(cash_policy.get("actual_measure") or "") if isinstance(cash_policy, Mapping) else ""
        legacy_d0_policy = (
            isinstance(cash_policy, Mapping)
            and "D0" in actual_measure
            and "past-12-month" in actual_measure
            and "after-tax" in actual_measure
            and "after-fee" in actual_measure
            and cash_policy.get("forward_fixed_distribution_cny") is None
            and "reinvest" in normalize(cash_policy.get("default_use"))
        )
        cash_ledger = (
            return_model.get("cash_ledger_and_accounting")
            if isinstance(return_model, Mapping)
            else None
        )
        total_return_measurement = (
            return_model.get("total_return_measurement")
            if isinstance(return_model, Mapping)
            else None
        )
        total_return_cash_policy = (
            isinstance(cash_ledger, Mapping)
            and isinstance(total_return_measurement, Mapping)
            and bool(cash_ledger.get("eligible_receipt_types"))
            and bool(cash_ledger.get("not_receipt_types"))
            and bool(str(cash_ledger.get("capital_repayment_like_component") or "").strip())
            and bool(str(total_return_measurement.get("formula") or "").strip())
            and bool(str(total_return_measurement.get("reinvestment_rule") or "").strip())
            and "once" in normalize(total_return_measurement.get("cash_receipt_accounting_rule"))
            and isinstance(cash_policy, Mapping)
            and cash_policy.get("automatic_reinvestment") is False
            and cash_policy.get("mandatory_retention") is False
        )
        total_return_schema = isinstance(cash_ledger, Mapping) or isinstance(
            total_return_measurement, Mapping
        )
        self.check(
            "strategic allocation return-model cash accounting policy",
            total_return_cash_policy if total_return_schema else legacy_d0_policy,
            (
                "single-objective cash-ledger controls"
                if total_return_schema
                else actual_measure or "legacy cash-accounting policy missing"
            ),
        )
        if total_return_schema:
            return_evidence = (
                return_model.get("return_evidence")
                if isinstance(return_model, Mapping)
                else None
            )
            self.check(
                "strategic allocation return evidence explicitly blocks implementation",
                isinstance(return_evidence, Mapping)
                and implementation_gate_is_not_approved(
                    normalize(return_evidence.get("implementation_status"))
                )
                and bool(str(return_evidence.get("formal_test_requirement") or "").strip())
                and bool(str(return_evidence.get("benchmark_requirement") or "").strip()),
                "return_evidence implementation boundary",
            )

            risk_budget = (
                return_model.get("risk_budget")
                if isinstance(return_model, Mapping)
                else None
            )
            self.check(
                "strategic allocation risk budget explicitly blocks implementation",
                isinstance(risk_budget, Mapping)
                and implementation_gate_is_not_approved(
                    normalize(risk_budget.get("implementation_status"))
                )
                and bool(str(risk_budget.get("approval_requirement") or "").strip())
                and bool(str(risk_budget.get("loss_limit") or "").strip()),
                "risk_budget implementation boundary",
            )

    def check_valuation_reproducibility(self) -> None:
        valuation_audit = read_text(self.case_dir / "analysis/valuation_audit.md")
        self.check(
            "valuation model reproducibility pass",
            "model reproducibility: pass" in normalize(valuation_audit),
        )

    def check_valuation_model_depth(self) -> None:
        valuation_path = self.case_dir / "analysis/valuation_model.md"
        if not valuation_path.exists():
            self.check(
                "valuation model required sections complete",
                False,
                "missing analysis/valuation_model.md",
            )
            return

        valuation_text = normalize(read_text(valuation_path))
        missing_sections = [
            section
            for section in VALUATION_REQUIRED_SECTIONS
            if normalize(section) not in valuation_text
        ]
        self.check(
            "valuation model required sections complete",
            not missing_sections,
            ", ".join(missing_sections)
            if missing_sections
            else "all valuation sections present",
        )

        rows = valuation_rows(self.load_first_json("data/current_valuation_model_*.json"))
        self.check("valuation model structured rows present", bool(rows), f"rows={len(rows)}")
        if not rows:
            return

        missing_by_row: list[str] = []
        arithmetic_errors: list[str] = []
        for row in rows:
            ticker = str(row.get("ticker") or "<missing ticker>")
            missing = [
                field
                for field in VALUATION_REQUIRED_ROW_FIELDS
                if not has_items(row.get(field))
            ]
            if missing:
                missing_by_row.append(f"{ticker}: {', '.join(missing)}")

            current = float_value(row.get("current_price"))
            target = float_value(row.get("final_target"))
            upside = float_value(row.get("upside"))
            if current and target is not None and upside is not None:
                expected = target / current - 1
                if abs(expected - upside) > 0.005:
                    arithmetic_errors.append(
                        f"{ticker}: upside {upside:.4f} != target/current-1 {expected:.4f}"
                    )

        detail = "; ".join(missing_by_row[:6])
        if len(missing_by_row) > 6:
            detail += "; ..."
        self.check("valuation model row fields complete", not missing_by_row, detail)
        self.check(
            "valuation model target/upside recalculates",
            not arithmetic_errors,
            "; ".join(arithmetic_errors[:6]),
        )

    def check_strategic_named_direct_equity_reconciliation(
        self,
        gate_manifest: Any,
    ) -> None:
        """Require every declared T3 direct issuer in valuation and Street packets."""

        controls = (
            gate_manifest.get("strategy_controls")
            if isinstance(gate_manifest, Mapping)
            else None
        )
        raw_tickers = (
            controls.get("named_t3_direct_equity_tickers")
            if isinstance(controls, Mapping)
            else None
        )
        named_tickers = (
            [str(ticker).strip() for ticker in raw_tickers if str(ticker).strip()]
            if isinstance(raw_tickers, Sequence)
            and not isinstance(raw_tickers, (str, bytes, bytearray))
            else []
        )
        named_set = set(named_tickers)
        valuation_tickers = {
            str(row.get("ticker")).strip()
            for row in valuation_rows(
                self.load_first_json("data/current_valuation_model_*.json")
            )
            if has_items(row.get("ticker"))
        }
        broker_tickers = {
            str(row.get("ticker")).strip()
            for row in broker_consensus_rows(
                self.load_first_json("data/broker_street_consensus_*.json")
            )
            if has_items(row.get("ticker"))
        }
        missing_valuation = sorted(named_set - valuation_tickers)
        missing_broker = sorted(named_set - broker_tickers)
        self.check(
            "strategic named T3 direct-equity registry reconciles to valuation universe",
            not missing_valuation and len(named_tickers) == len(named_set),
            ", ".join(missing_valuation) or f"matched={len(named_tickers)}",
        )
        self.check(
            "strategic named T3 direct-equity registry reconciles to broker/Street universe",
            not missing_broker and len(named_tickers) == len(named_set),
            ", ".join(missing_broker) or f"matched={len(named_tickers)}",
        )

    def check_single_stock_depth(self) -> None:
        missing_artifacts: list[str] = []
        shallow_artifacts: list[str] = []
        for rel, terms in SINGLE_STOCK_INSTITUTIONAL_DEPTH_TERMS.values():
            path = self.case_dir / rel
            text = normalize(read_text(path))
            if not path.exists():
                missing_artifacts.append(rel)
                continue
            missing_terms = [term for term in terms if normalize(term) not in text]
            if missing_terms:
                shallow_artifacts.append(f"{rel}: {', '.join(missing_terms)}")
        detail_parts = []
        if missing_artifacts:
            detail_parts.append("missing " + ", ".join(missing_artifacts))
        if shallow_artifacts:
            detail_parts.append("; ".join(shallow_artifacts[:4]))
        self.check(
            "single-stock valuation model institutional depth",
            not missing_artifacts and not shallow_artifacts,
            "; ".join(detail_parts)
            if detail_parts
            else "segment valuation and secondary-market artifacts present",
        )

    def check_valuation_coverage_reconciliation(self) -> None:
        triage_payload = self.load_json("data/valuation_triage_20260630.json")
        core_payload = self.load_json("data/core_candidate_valuation_disposition_20260630.json")
        triage_rows = valuation_rows(triage_payload)
        core_rows = valuation_rows(core_payload)
        current_rows = valuation_rows(self.load_first_json("data/current_valuation_model_*.json"))

        self.check("valuation triage rows cover full mapped pool", len(triage_rows) >= 173, f"rows={len(triage_rows)}")
        self.check("core candidate disposition rows cover core pool", len(core_rows) >= 58, f"rows={len(core_rows)}")
        self.check(
            "original target-price combo remains explicit subset",
            len(current_rows) <= len(core_rows) and len(current_rows) >= 18,
            f"current={len(current_rows)} core={len(core_rows)}",
        )
        if not triage_rows or not core_rows:
            return

        triage_companies = [str(row.get("company") or "") for row in triage_rows]
        duplicate_companies = sorted(
            {company for company in triage_companies if company and triage_companies.count(company) > 1}
        )
        self.check("valuation triage companies deduplicated", not duplicate_companies, ", ".join(duplicate_companies[:10]))

        required_triage_fields = (
            "company",
            "primary_classification",
            "target_price_status",
            "valuation_disposition",
            "evidence_gap",
            "next_verification_path",
        )
        missing_triage = [
            str(row.get("company") or "<missing company>")
            for row in triage_rows
            if any(not has_items(row.get(field)) for field in required_triage_fields)
        ]
        self.check("valuation triage row fields complete", not missing_triage, "; ".join(missing_triage[:10]))

        required_core_fields = (
            "company",
            "chain_blocks",
            "subsegments",
            "candidate_method",
            "target_price_status",
            "valuation_disposition",
            "upgrade_trigger",
        )
        missing_core = [
            str(row.get("company") or "<missing company>")
            for row in core_rows
            if any(not has_items(row.get(field)) for field in required_core_fields)
        ]
        self.check("core candidate disposition fields complete", not missing_core, "; ".join(missing_core[:10]))

        core_from_triage = {
            str(row.get("company"))
            for row in triage_rows
            if row.get("primary_classification") == "core_valuation"
        }
        core_from_disposition = {str(row.get("company")) for row in core_rows}
        missing_core_disposition = sorted(core_from_triage - core_from_disposition)
        self.check(
            "all core triage companies have disposition rows",
            not missing_core_disposition,
            ", ".join(missing_core_disposition[:10]),
        )

        original_target_companies_from_triage = {
            str(row.get("company"))
            for row in triage_rows
            if row.get("existing_target_price_model") is True
            or row.get("target_price_status") == "target_price_published"
        }
        target_companies_from_model = {str(row.get("company")) for row in current_rows}
        self.check(
            "original target-price model reconciles to triage",
            target_companies_from_model == original_target_companies_from_triage,
            f"model_only={sorted(target_companies_from_model - original_target_companies_from_triage)[:6]} triage_only={sorted(original_target_companies_from_triage - target_companies_from_model)[:6]}",
        )

        extended_payload = self.load_first_json("data/core_candidate_extended_valuation_model_*.json")
        extended_rows = valuation_rows(extended_payload)
        target_statuses = {"target_model_ready", "house_target_model_ready", "ps_sotp_target_model_ready"}
        extended_target_rows = [
            row for row in extended_rows if str(row.get("publication_status") or "") in target_statuses
        ]
        explicit_broker_rows = [
            row for row in extended_rows if row.get("publication_status") == "target_model_ready"
        ]
        house_rows = [
            row for row in extended_rows if row.get("publication_status") == "house_target_model_ready"
        ]
        ps_sotp_rows = [
            row for row in extended_rows if row.get("publication_status") == "ps_sotp_target_model_ready"
        ]
        watchlist_rows = [
            row for row in extended_rows if row.get("publication_status") == "watchlist_only_insufficient_model"
        ]
        legacy_no_street_rows = [
            row for row in extended_rows if row.get("publication_status") == "financial_model_ready_no_street_anchor"
        ]
        missing_extended_model_fields = [
            str(row.get("company") or "<missing company>")
            for row in extended_target_rows
            if any(not has_items(row.get(field)) for field in ("current_price", "final_target", "upside", "method", "company_specific_disposition"))
        ]
        non_zero_house_broker_weight = [
            str(row.get("company") or "<missing company>")
            for row in house_rows
            if float_value(row.get("broker_weight")) not in (0.0, None)
        ]
        published_companies_from_triage = {
            str(row.get("company"))
            for row in triage_rows
            if row.get("published_target_price_model") is True
            or row.get("existing_target_price_model") is True
        }
        extended_target_companies = {str(row.get("company")) for row in extended_target_rows}
        combined_model_companies = target_companies_from_model | extended_target_companies
        self.check(
            "extended core-candidate valuation model depth",
            len(extended_rows) == 41
            and len(extended_target_rows) == 38
            and len(explicit_broker_rows) == 13
            and len(house_rows) == 24
            and len(ps_sotp_rows) == 1
            and len(watchlist_rows) == 3
            and not legacy_no_street_rows
            and not missing_extended_model_fields
            and not non_zero_house_broker_weight,
            (
                f"rows={len(extended_rows)} target={len(extended_target_rows)} explicit={len(explicit_broker_rows)} "
                f"house={len(house_rows)} ps_sotp={len(ps_sotp_rows)} watchlist={len(watchlist_rows)} "
                f"legacy_no_street={len(legacy_no_street_rows)} missing={missing_extended_model_fields[:6]} "
                f"non_zero_house_broker_weight={non_zero_house_broker_weight[:6]}"
            ),
        )
        self.check(
            "combined target-price/fair-value universe reconciles to triage",
            len(combined_model_companies) == 56 and combined_model_companies == published_companies_from_triage,
            f"combined={len(combined_model_companies)} triage={len(published_companies_from_triage)} model_only={sorted(combined_model_companies - published_companies_from_triage)[:6]} triage_only={sorted(published_companies_from_triage - combined_model_companies)[:6]}",
        )

        cards_text = read_text(self.case_dir / "analysis/core_candidate_company_cards.md")
        missing_cards = [
            company
            for company in sorted(core_from_disposition)
            if company and company not in cards_text
        ]
        self.check("core candidate company cards present", not missing_cards, ", ".join(missing_cards[:10]))

    def check_broker_street_consensus(
        self,
        final_signoff: Any,
        *,
        allow_zero_weight_exhaustion: bool = False,
    ) -> None:
        consensus_files = sorted(
            (self.case_dir / "data").glob("broker_street_consensus_*.json"),
            reverse=True,
        )
        self.check(
            "broker/street consensus json present",
            bool(consensus_files),
            "data/broker_street_consensus_<YYYYMMDD>.json",
        )
        if not consensus_files:
            return

        md_path = consensus_files[0].with_suffix(".md")
        self.check(
            "broker/street consensus md pair present",
            md_path.exists(),
            str(md_path.relative_to(self.case_dir)),
        )

        rows = broker_consensus_rows(
            self.load_json(str(consensus_files[0].relative_to(self.case_dir)))
        )
        self.check("broker/street consensus rows present", bool(rows), f"rows={len(rows)}")

        valuation_payload_rows = valuation_rows(
            self.load_first_json("data/current_valuation_model_*.json")
        )
        covered_tickers = {
            str(row.get("ticker"))
            for row in valuation_payload_rows
            if has_items(row.get("ticker"))
        }
        zero_weight_valuation_tickers = {
            str(row.get("ticker"))
            for row in valuation_payload_rows
            if has_items(row.get("ticker"))
            and first_float(row.get("broker_weight")) == 0.0
        }
        row_tickers = {
            str(row.get("ticker"))
            for row in rows
            if has_items(row.get("ticker"))
        }
        missing_coverage = sorted(covered_tickers - row_tickers)
        self.check(
            "broker/street consensus covers valuation universe",
            not missing_coverage,
            ", ".join(missing_coverage)
            if missing_coverage
            else f"covered={len(row_tickers)}",
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
                if not has_items(row.get(field))
            ]
            if missing:
                missing_by_row.append(f"{ticker}: {', '.join(missing)}")

            unusable = [
                field
                for field in BROKER_CONSENSUS_USABLE_FIELDS
                if not broker_value_usable(row.get(field))
            ]
            if unusable:
                unusable_rows.append(row)
                unusable_by_row.append(f"{ticker}: {', '.join(unusable)}")

            source_quality = normalize(row.get("source_quality"))
            if source_quality in BROKER_WEAK_SOURCE_QUALITIES or unusable:
                weak_rows.append(row)
                weight = first_float(
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
                and (first_float(
                    row.get("street_weight"),
                    row.get("broker_weight"),
                    row.get("valuation_weight"),
                    row.get("weight"),
                ) or 0.0) > 0.0
            ):
                positive_anchor_tickers.add(ticker)
                if broker_row_external(row):
                    external_positive_anchor_tickers.add(ticker)

        detail = "; ".join(missing_by_row[:8])
        if len(missing_by_row) > 8:
            detail += "; ..."
        self.check("broker/street consensus row fields complete", not missing_by_row, detail)
        unusable_detail = "; ".join(unusable_by_row[:8])
        if len(unusable_by_row) > 8:
            unusable_detail += "; ..."
        self.check(
            "broker/street weak sources are zero-weight or unavailable",
            not weak_not_downweighted,
            "; ".join(weak_not_downweighted[:8]),
        )

        source_exhaustion = normalize(read_text(self.case_dir / "source_exhaustion_log.md"))
        broker_gap_documented = (
            ("broker" in source_exhaustion or "券商" in source_exhaustion)
            and ("target" in source_exhaustion or "目标价" in source_exhaustion)
        )
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
            or (first_float(
                row.get("street_weight"),
                row.get("broker_weight"),
                row.get("valuation_weight"),
                row.get("weight"),
            ) or 0.0) > 0.0
        ]
        self.check(
            "broker/street consensus values usable for valuation anchor",
            not unusable_positive_rows,
            unusable_detail,
        )

        missing_positive_anchor = sorted(
            covered_tickers - positive_anchor_tickers - auditable_zero_weight_tickers
        )
        self.check(
            "broker/street positive-weight auditable anchor covers valuation universe",
            not missing_positive_anchor,
            ", ".join(missing_positive_anchor[:8]),
        )
        missing_external_anchor = sorted(
            covered_tickers - external_positive_anchor_tickers - auditable_zero_weight_tickers
        )
        self.check(
            "broker/street external positive anchor covers valuation universe",
            not missing_external_anchor,
            ", ".join(missing_external_anchor[:8]),
        )

        self.check(
            "broker/street gaps recorded in source exhaustion",
            not (weak_rows or unusable_rows)
            or broker_gap_documented,
            "source_exhaustion_log.md must record broker target-price gaps",
        )

        signoff_status = normalize(
            final_signoff.get("signoff_status") if isinstance(final_signoff, Mapping) else ""
        )
        self.check(
            "broker/street consensus complete before PASS sign-off",
            signoff_status not in {"pass", "passed", "approved", "signed", "publishable"}
            or not (weak_rows or unusable_rows)
            or (
                broker_gap_documented
                and not weak_not_downweighted
                and covered_tickers <= auditable_zero_weight_tickers
            ),
            "PASS cannot coexist with incomplete broker/Street target-price coverage",
        )

    def check_final_signoff(
        self,
        final_signoff: Any,
        *,
        gate_manifest: Any = None,
        strategic_allocation_case: bool = False,
    ) -> None:
        if not isinstance(final_signoff, Mapping):
            self.check("final sign-off is object", False)
            return

        for key in FINAL_SIGNOFF_KEYS:
            self.check(
                f"final sign-off has {key}",
                key in final_signoff and final_signoff.get(key) not in (None, ""),
            )

        status = normalize(final_signoff.get("signoff_status") or final_signoff.get("status"))
        strategic_framework_signoff = (
            strategic_allocation_case
            and status in STRATEGIC_RESEARCH_FRAMEWORK_SIGNOFF_STATUSES
        )
        if strategic_framework_signoff:
            framework_status = normalize(final_signoff.get("framework_status"))
            implementation_status = normalize(final_signoff.get("implementation_status"))
            live_execution_authorized = final_signoff.get("live_execution_authorized")
            implementation_gates = final_signoff.get("implementation_gates")
            execution_eligibility = final_signoff.get("execution_eligibility")
            self.check(
                "strategic allocation research-framework sign-off status pass",
                status in STRATEGIC_RESEARCH_FRAMEWORK_SIGNOFF_STATUSES
                and framework_status in LEGACY_PASS_SIGNOFF_STATUSES,
                f"signoff={status or 'missing'}; framework={framework_status or 'missing'}",
            )
            self.check(
                "strategic allocation implementation explicitly not approved",
                implementation_status in IMPLEMENTATION_BLOCKED_STATUSES,
                implementation_status or "missing",
            )
            self.check(
                "strategic allocation live execution explicitly unauthorized",
                live_execution_authorized is False,
                str(live_execution_authorized),
            )

            gates_ok, gates_detail = strategic_implementation_gates_are_blocking(
                implementation_gates
            )
            self.check(
                "strategic allocation return-evidence and risk-budget gates block implementation",
                gates_ok,
                gates_detail,
            )

            execution_ok, execution_detail = strategic_execution_is_inactive(
                execution_eligibility
            )
            self.check(
                "strategic allocation execution eligibility remains inactive",
                execution_ok,
                execution_detail,
            )

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
            disclosure_ok, disclosure_detail = strategic_material_claims_disclosed(
                final_signoff,
                cash_objective_required=cash_objective_required,
            )
            self.check(
                "strategic allocation material claims are explicitly disclosed",
                disclosure_ok,
                disclosure_detail,
            )
        else:
            self.check(
                "final sign-off status pass",
                status in LEGACY_PASS_SIGNOFF_STATUSES,
                status or "missing",
            )

        score = int_value(final_signoff.get("publishability_score"))
        self.check("final sign-off score >= 90", score is not None and score >= 90, str(score))
        self.check("final sign-off open S count zero", int_value(final_signoff.get("open_s_count")) == 0)
        self.check("final sign-off open A count zero", int_value(final_signoff.get("open_a_count")) == 0)
        if strategic_framework_signoff:
            residual_ok, residual_detail = strategic_residual_risks_disclosed(
                final_signoff
            )
            self.check(
                "strategic allocation residual implementation blockers are disclosed",
                residual_ok,
                residual_detail,
            )
        else:
            self.check(
                "final sign-off residual risks do not conflict with PASS",
                not final_signoff_has_material_residual_risk_conflict(final_signoff),
                "material residual risk cannot be hidden in a PASS sign-off",
            )

    def check_workflow_eval(
        self,
        workflow_eval: Any,
        *,
        strategic_allocation_case: bool = False,
    ) -> None:
        if not isinstance(workflow_eval, Mapping):
            self.check("workflow eval is object", False)
            return
        quality = workflow_eval.get("quality")
        self.check("workflow eval has quality packet", isinstance(quality, Mapping))
        if not isinstance(quality, Mapping):
            return
        self.check("workflow eval publishable", quality.get("publishable") is True)
        self.check(
            "workflow eval zero blocking failures",
            int_value(quality.get("blocking_failure_count")) == 0,
        )
        score = int_value(quality.get("score"))
        self.check("workflow eval score >= 90", score is not None and score >= 90, str(score))
        strategic_framework_workflow = strategic_allocation_case and (
            "implementation_status" in quality
            or normalize(quality.get("status"))
            in {
                "pass_research_framework_implementation_not_approved",
                "research_framework_pass_implementation_not_approved",
            }
        )
        if strategic_framework_workflow:
            self.check(
                "strategic allocation workflow status distinguishes research from implementation",
                normalize(quality.get("status"))
                in {
                    "pass_research_framework_implementation_not_approved",
                    "research_framework_pass_implementation_not_approved",
                },
                str(quality.get("status") or "missing"),
            )
            self.check(
                "strategic allocation workflow implementation explicitly not approved",
                normalize(quality.get("implementation_status"))
                in IMPLEMENTATION_BLOCKED_STATUSES,
                str(quality.get("implementation_status") or "missing"),
            )

    def check_case_verifier(self) -> None:
        verifier = self.case_dir / "tools" / "verify_research_workspace.py"
        self.check("generic case verifier present", verifier.exists())
        if verifier.exists():
            completed = subprocess.run(
                [sys.executable, "tools/verify_research_workspace.py"],
                cwd=self.case_dir,
                text=True,
                capture_output=True,
                check=False,
            )
            detail = tail(completed.stdout + completed.stderr)
            self.check("generic case verifier pass", completed.returncode == 0, detail)

    def check_reader_facing_no_generic_placeholders(self) -> None:
        body = read_text(self.case_dir / "main_current_text.txt")
        banned = (
            "核心候选" + "，暂列观察",
            "补齐" + "官方收入拆分",
            "产能利用率、" + "ASP 或毛利证据后，才可升级",
            "多数公司" + "未披露 AI 订单",
            "只有当产品、客户/平台认证、订单或项目交付、ASP/价格代理、产能利用率和毛利率形成闭环，才可以进入目标价模型",
        )
        hits = [item for item in banned if item in body]
        self.check(
            "reader-facing report has no generic valuation placeholders",
            not hits,
            ", ".join(hits),
        )

    def check_industry_chain_artifacts(self) -> None:
        for rel in INDUSTRY_CHAIN_ARTIFACTS:
            self.exists(rel)
        universe_files = sorted((self.case_dir / "data").glob("full_chain_universe_*.json"))
        self.check("full-chain universe json present", bool(universe_files))

    def check_industry_chain_depth(self) -> None:
        for name, (rel, terms) in INDUSTRY_DEPTH_TERM_SETS.items():
            text = normalize(read_text(self.case_dir / rel))
            missing = [term for term in terms if normalize(term) not in text]
            self.check(
                name,
                not missing,
                f"{rel} missing: {', '.join(missing)}"
                if missing
                else f"{rel} contains required depth terms",
            )

    def check_chain_business_matrix_depth(self) -> None:
        payload = self.load_json("data/chain_business_matrix_20260630.json")
        block_rows = payload.get("block_rows") if isinstance(payload, Mapping) else None
        company_rows = payload.get("company_rows") if isinstance(payload, Mapping) else None
        if (
            not isinstance(block_rows, Sequence)
            or isinstance(block_rows, (str, bytes, bytearray))
            or not isinstance(company_rows, Sequence)
            or isinstance(company_rows, (str, bytes, bytearray))
        ):
            self.check("chain-business matrix rows structured", False, "block_rows/company_rows missing")
            return
        required_fields = (
            "ticker",
            "company",
            "chain_layer",
            "upstream_business",
            "downstream_business",
            "business_relationship",
            "core_technology",
            "core_revenue_business",
            "2026e_expectation",
            "valuation_credit",
        )
        missing_by_row = [
            str(row.get("company") or "<missing company>")
            for row in company_rows
            if isinstance(row, Mapping)
            and any(not has_items(row.get(field)) for field in required_fields)
        ]
        non_objects = [row for row in company_rows if not isinstance(row, Mapping)]
        self.check("chain-business matrix has all AIDC blocks", len(block_rows) == 8, f"block_rows={len(block_rows)}")
        self.check(
            "chain-business matrix covers core candidates",
            len(company_rows) >= 58,
            f"company_rows={len(company_rows)}",
        )
        self.check(
            "chain-business matrix company fields complete",
            not missing_by_row and not non_objects,
            "; ".join(missing_by_row[:10]),
        )

    def check_supply_chain_chapter_prose_led(self) -> None:
        chapter = read_text(self.case_dir / "sections/ch04_supply_chain.tex")
        normalized = normalize(chapter)
        required_terms = (
            "算力与存储",
            "服务器、整柜与网络设备",
            "光通信",
            "PCB、CCL",
            "供配电与液冷",
            "AIDC/IDC 运营",
            "附录证据索引",
            "价值量--收入确认--利润率--现金流--估值信用",
        )
        missing_terms = [term for term in required_terms if normalize(term) not in normalized]
        first_exhibit = chapter.find(r"\begin{exhibitbox}")
        prose_before_first_exhibit = chapter[:first_exhibit] if first_exhibit >= 0 else chapter
        prose_chars = len(re.sub(r"\\[A-Za-z]+\*?(?:\{[^{}]*\})?", "", prose_before_first_exhibit).strip())
        matrix_title = "58 个核心候选公司级产业链业务矩阵"
        self.check(
            "supply-chain chapter has prose before exhibits",
            prose_chars >= 2200,
            f"prose_chars_before_first_exhibit={prose_chars}",
        )
        self.check(
            "supply-chain chapter covers causal chain",
            not missing_terms,
            f"missing={', '.join(missing_terms)}",
        )
        self.check(
            "supply-chain company matrix kept out of main chapter",
            matrix_title not in chapter and "company_chain_business_tex_table" not in chapter,
            "58-row company matrix belongs in appendix, not chapter 4",
        )

    def check_supply_chain_relationship_depth(self) -> None:
        payload = self.load_json("data/supply_chain_relationships.json")
        relationships = payload.get("relationships") if isinstance(payload, Mapping) else None
        if not isinstance(relationships, Sequence) or isinstance(relationships, (str, bytes, bytearray)):
            self.check("supply-chain relationship rows structured", False, "relationships missing")
            return
        required_fields = (
            "ticker",
            "company",
            "chain_layer",
            "node_type",
            "downstream_customer_or_platform",
            "relationship_type",
            "source_tier",
            "evidence_score",
            "revenue_exposure",
            "capacity_or_certification",
            "order_visibility",
            "ASP_or_price_proxy",
            "utilization_or_yield",
            "margin_or_earnings_impact",
            "source",
            "evidence_gap",
            "valuation_eligibility",
            "downgrade_trigger",
            "used_in_valuation",
        )
        missing_by_row = [
            str(row.get("company") or "<missing company>")
            for row in relationships
            if isinstance(row, Mapping)
            and any(not has_items(row.get(field)) for field in required_fields)
        ]
        non_objects = [row for row in relationships if not isinstance(row, Mapping)]
        self.check(
            "supply-chain relationship rows cover core candidates",
            len(relationships) >= 58,
            f"relationships={len(relationships)}",
        )
        self.check(
            "supply-chain relationship row fields complete",
            not missing_by_row and not non_objects,
            "; ".join(missing_by_row[:10]),
        )

    def check_customer_chain_audit_depth(self) -> None:
        payload = self.load_json("data/customer_chain_audit.json")
        audits = payload.get("audits") if isinstance(payload, Mapping) else None
        if not isinstance(audits, Sequence) or isinstance(audits, (str, bytes, bytearray)):
            self.check("customer-chain audit rows structured", False, "audits missing")
            return
        required_fields = (
            "ticker",
            "company",
            "customer_or_platform",
            "claim_type",
            "product_or_process",
            "certification_status",
            "order_or_backlog",
            "ASP_or_price_proxy",
            "capacity",
            "utilization_or_yield",
            "revenue_exposure",
            "margin_impact",
            "source_tier",
            "evidence_score",
            "source",
            "evidence_gap",
            "blocks_valuation",
            "downgrade_trigger",
            "adopted_wording",
        )
        missing_by_row = [
            str(row.get("company") or "<missing company>")
            for row in audits
            if isinstance(row, Mapping)
            and any(not has_items(row.get(field)) for field in required_fields)
        ]
        target_claim_types = {
            "target_model_customer_chain",
            "extended_target_model_customer_chain",
            "extended_house_fair_value_customer_chain",
            "extended_ps_sotp_customer_chain",
        }
        target_rows = [
            row
            for row in audits
            if isinstance(row, Mapping)
            and normalize(row.get("claim_type")) in target_claim_types
        ]
        metadata = payload.get("metadata") if isinstance(payload, Mapping) else {}
        expected_target_rows = 18
        if isinstance(metadata, Mapping):
            raw_expected = metadata.get("target_model_rows")
            if isinstance(raw_expected, int):
                expected_target_rows = raw_expected
        blocked_targets = [
            str(row.get("company") or "<missing company>")
            for row in target_rows
            if row.get("blocks_valuation") is True
        ]
        weak_target_sources = [
            str(row.get("company") or "<missing company>")
            for row in target_rows
            if normalize(row.get("source_tier")) in {"triage_only", "full_chain_taxonomy", ""}
        ]
        bad_wording = [
            str(row.get("company") or "<missing company>")
            for row in audits
            if isinstance(row, Mapping)
            and any(
                token in str(row.get("adopted_wording") or "")
                for token in (
                    "核心候选" + "，暂列观察",
                    "补齐" + "官方收入拆分",
                    "才可" + "升级为目标价模型",
                )
            )
        ]
        self.check(
            "customer-chain audit rows cover core candidates",
            len(audits) >= 58,
            f"audits={len(audits)}",
        )
        self.check(
            "customer-chain audit row fields complete",
            not missing_by_row,
            "; ".join(missing_by_row[:10]),
        )
        self.check(
            "customer-chain audit target rows align with valuation model",
            len(target_rows) >= expected_target_rows and not blocked_targets and not weak_target_sources,
            f"target_rows={len(target_rows)} expected={expected_target_rows} blocked={blocked_targets[:8]} weak_sources={weak_target_sources[:8]}",
        )
        self.check(
            "customer-chain audit has no generic upgrade placeholder wording",
            not bad_wording,
            "; ".join(bad_wording[:10]),
        )

    def check_field_evidence_completion_depth(self) -> None:
        payload = self.load_json("data/field_evidence_completion_20260701.json")
        rows = payload.get("rows") if isinstance(payload, Mapping) else None
        metadata = payload.get("metadata") if isinstance(payload, Mapping) else {}
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
            self.check("field-evidence completion rows structured", False, "rows missing")
            return
        fields = (
            "revenue_exposure",
            "customer_or_platform",
            "order_or_backlog",
            "capacity_or_certification",
            "asp_or_price_proxy",
            "utilization_or_yield",
            "margin_impact",
        )
        missing_schema = []
        unresolved_target_fields = []
        for row in rows:
            if not isinstance(row, Mapping):
                missing_schema.append("<non-object>")
                continue
            cells = row.get("fields")
            if not isinstance(cells, Mapping) or any(field not in cells for field in fields):
                missing_schema.append(str(row.get("ticker") or row.get("company") or "<missing>"))
                continue
            if row.get("target_model") is True:
                for field in fields:
                    cell = cells.get(field)
                    status = normalize(cell.get("status") if isinstance(cell, Mapping) else None)
                    if status in {"", "source_exhausted", "watchlist_blocked"}:
                        unresolved_target_fields.append(f"{row.get('ticker')}:{field}:{status}")
        total_cells = int(metadata.get("total_field_cells") or 0) if isinstance(metadata, Mapping) else 0
        self.check(
            "field-evidence completion covers modeled core candidates",
            len(rows) >= 59 and total_cells >= len(rows) * len(fields),
            f"rows={len(rows)} cells={total_cells}",
        )
        self.check(
            "field-evidence completion row schema complete",
            not missing_schema,
            "; ".join(missing_schema[:10]),
        )
        self.check(
            "field-evidence target models have no unresolved fields",
            not unresolved_target_fields,
            "; ".join(unresolved_target_fields[:10]),
        )

    def check_proxy_field_official_collection_depth(self) -> None:
        field_payload = self.load_json("data/field_evidence_completion_20260701.json")
        field_rows = field_payload.get("rows") if isinstance(field_payload, Mapping) else None
        if not isinstance(field_rows, Sequence) or isinstance(field_rows, (str, bytes, bytearray)):
            self.check(
                "proxy-field source field-evidence rows structured",
                False,
                "rows missing",
            )
            return
        proxy_tickers = set()
        for row in field_rows:
            if not isinstance(row, Mapping):
                continue
            fields = row.get("fields")
            if not isinstance(fields, Mapping):
                continue
            if any(
                isinstance(cell, Mapping) and normalize(cell.get("status")) == "proxy"
                for cell in fields.values()
            ):
                proxy_tickers.add(str(row.get("ticker")))
        payload = self.load_json("data/proxy_field_official_filing_collection_20260701.json")
        rows = payload.get("rows") if isinstance(payload, Mapping) else None
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
            self.check("proxy-field official collection rows structured", False, "rows missing")
            return
        covered = {
            str(row.get("ticker"))
            for row in rows
            if isinstance(row, Mapping) and int(row.get("filings_archived") or 0) > 0
        }
        missing = sorted(ticker for ticker in proxy_tickers if ticker and ticker not in covered)
        hit_cells = 0
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            direct_hits = row.get("proxy_field_direct_hits")
            if not isinstance(direct_hits, Mapping):
                continue
            hit_cells += sum(
                1
                for value in direct_hits.values()
                if int(value or 0) > 0
            )
        self.check(
            "proxy-field official collection covers proxy candidates",
            proxy_tickers <= covered,
            f"proxy_candidates={len(proxy_tickers)} covered={len(covered)} missing={missing[:10]}",
        )
        self.check(
            "proxy-field official collection has extracted field hits",
            hit_cells >= len(proxy_tickers),
            f"hit_cells={hit_cells} proxy_candidates={len(proxy_tickers)}",
        )

    def check_residual_proxy_field_audit_depth(self) -> None:
        field_payload = self.load_json("data/field_evidence_completion_20260701.json")
        field_rows = field_payload.get("rows") if isinstance(field_payload, Mapping) else None
        if not isinstance(field_rows, Sequence) or isinstance(field_rows, (str, bytes, bytearray)):
            self.check(
                "residual proxy-field source field-evidence rows structured",
                False,
                "rows missing",
            )
            return
        proxy_cells: list[tuple[str, str]] = []
        for row in field_rows:
            if not isinstance(row, Mapping):
                continue
            ticker = str(row.get("ticker") or "")
            fields = row.get("fields")
            if not isinstance(fields, Mapping):
                continue
            for field, cell in fields.items():
                if isinstance(cell, Mapping) and normalize(cell.get("status")) == "proxy":
                    proxy_cells.append((ticker, str(field)))

        payload = self.load_json("data/residual_proxy_field_audit_20260701.json")
        rows = payload.get("rows") if isinstance(payload, Mapping) else None
        if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes, bytearray)):
            self.check("residual proxy-field audit rows structured", False, "rows missing")
            return

        covered = {
            (str(row.get("ticker") or ""), str(row.get("field") or ""))
            for row in rows
            if isinstance(row, Mapping)
        }
        missing = [
            f"{ticker}:{field}"
            for ticker, field in proxy_cells
            if (ticker, field) not in covered
        ]
        shallow = []
        for row in rows:
            if not isinstance(row, Mapping):
                continue
            consequence = normalize(row.get("valuation_consequence"))
            has_policy = any(
                token in consequence
                for token in ("上修", "目标价", "估值", "valuation", "uplift", "target")
            )
            if (
                not has_items(row.get("remaining_gap"))
                or not has_items(row.get("valuation_consequence"))
                or not has_items(row.get("next_verification_path"))
                or not has_policy
            ):
                shallow.append(f"{row.get('ticker')}:{row.get('field')}")
        self.check(
            "residual proxy-field audit covers every proxy cell",
            len(rows) == len(proxy_cells) and not missing,
            f"proxy_cells={len(proxy_cells)} audit_rows={len(rows)} missing={missing[:10]}",
        )
        self.check(
            "residual proxy-field audit states valuation consequence",
            not shallow,
            "; ".join(shallow[:10]),
        )

    def check_growth_driver_depth(self) -> None:
        payload = self.load_json("data/growth_driver_model.json")
        drivers = payload.get("drivers") if isinstance(payload, Mapping) else None
        if not isinstance(drivers, Sequence) or isinstance(drivers, (str, bytes, bytearray)):
            self.check("growth-driver rows structured", False, "drivers missing")
            return
        required_fields = (
            "ticker",
            "company",
            "base_business_revenue",
            "growth_segment_revenue",
            "unit_volume_or_proxy",
            "ASP_or_price",
            "value_amount_or_proxy",
            "supply_demand_state",
            "capacity_or_utilization",
            "certification_or_customer_qualification",
            "recognized_revenue_ratio",
            "growth_gross_margin",
            "growth_gross_profit_100mn",
            "incremental_opex",
            "growth_net_profit_100mn",
            "growth_EPS",
            "source",
            "evidence_gap",
            "valuation_credit",
            "current_price_implied_growth",
            "next_quarter_validation_threshold",
        )
        missing_by_row = [
            str(row.get("company") or "<missing company>")
            for row in drivers
            if isinstance(row, Mapping)
            and any(not has_items(row.get(field)) for field in required_fields)
        ]
        generic_placeholders = [
            str(row.get("company") or "<missing company>")
            for row in drivers
            if isinstance(row, Mapping)
            and any(
                token in normalize(row.get(field))
                for field in ("growth_segment_revenue", "unit_volume_or_proxy", "ASP_or_price")
                for token in (
                    "growth segment not separately disclosed",
                    "not uniformly disclosed",
                    "use current price implied pe only",
                )
            )
        ]
        self.check("growth-driver rows cover valuation universe", len(drivers) >= 18, f"drivers={len(drivers)}")
        self.check("growth-driver row fields complete", not missing_by_row, "; ".join(missing_by_row[:10]))
        self.check(
            "growth-driver rows avoid generic placeholder model language",
            not generic_placeholders,
            "; ".join(generic_placeholders[:10]),
        )

    def check_industry_chain_verifier(self) -> None:
        verifier = (
            self.repo_root
            / "workspace"
            / "research"
            / "templates"
            / "industry_chain_verify_research_workspace.py"
        )
        self.check("industry-chain verifier present", verifier.exists())
        if verifier.exists():
            completed = subprocess.run(
                [sys.executable, str(verifier), str(self.case_dir)],
                cwd=self.repo_root,
                text=True,
                capture_output=True,
                check=False,
            )
            detail = tail(completed.stdout + completed.stderr)
            self.check("industry-chain verifier pass", completed.returncode == 0, detail)

    def finish(self) -> int:
        for item in self.passes:
            print(f"PASS {item}")
        for item in self.warnings:
            print(f"WARN {item}")
        for item in self.failures:
            print(f"FAIL {item}")
        print(f"SUMMARY {len(self.passes)} PASS / {len(self.failures)} FAIL")
        print("RESULT PASS" if not self.failures else "RESULT FAIL")
        return 0 if not self.failures else 1


def expected_review_cycles(gate_manifest: Any) -> tuple[str, ...]:
    if isinstance(gate_manifest, Mapping):
        cycles = gate_manifest.get("review_cycles")
        if isinstance(cycles, Sequence) and not isinstance(cycles, (str, bytes, bytearray)):
            parsed = tuple(str(cycle) for cycle in cycles if str(cycle).strip())
            if parsed:
                return parsed
    return EXPECTED_REVIEW_CYCLES


def artifact_paths_from_payload(payload: Any) -> set[str]:
    paths: set[str] = set()
    if isinstance(payload, str):
        if looks_like_artifact_path(payload):
            paths.add(payload.strip())
        return paths
    if isinstance(payload, Mapping):
        for key, item in payload.items():
            key_text = normalize(key)
            if key_text in {
                "path",
                "file",
                "relpath",
                "relative_path",
                "artifact",
                "artifact_path",
                "output",
            } and isinstance(item, str):
                if looks_like_artifact_path(item):
                    paths.add(item.strip())
                continue
            paths.update(artifact_paths_from_payload(item))
        return paths
    if isinstance(payload, Sequence) and not isinstance(payload, (bytes, bytearray)):
        for item in payload:
            paths.update(artifact_paths_from_payload(item))
    return paths


def looks_like_artifact_path(value: str) -> bool:
    text = value.strip()
    if not text or text.startswith(("http://", "https://")):
        return False
    if any(token in text for token in ("\n", "\t", "{", "}")):
        return False
    suffix = Path(text).suffix.lower()
    return suffix in {".csv", ".json", ".md", ".pdf", ".png", ".tex", ".txt", ".xlsx"}


def resolve_artifact(case_dir: Path, rel: str) -> Path:
    path = Path(rel)
    if path.is_absolute():
        return path
    return case_dir / path


def case_requires_industry_chain(gate_manifest: Any, text_blob: str) -> bool:
    gate_text = ""
    if isinstance(gate_manifest, Mapping):
        if case_is_strategic_allocation(gate_manifest):
            return False
        report_type = normalize(gate_manifest.get("report_type"))
        # A single-stock report may embed a full value-chain module without
        # becoming a multi-company industry-chain valuation case.  The latter
        # requires universe-wide triage and proxy-field artifacts that are not
        # applicable to a one-ticker valuation parent.
        if report_type.startswith("single_stock"):
            return False
        gate_text = json.dumps(gate_manifest, ensure_ascii=False)
    haystack = normalize(f"{gate_text}\n{text_blob}")
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


def case_is_strategic_allocation(gate_manifest: Any) -> bool:
    if not isinstance(gate_manifest, Mapping):
        return False
    return normalize(gate_manifest.get("case_profile")) == "strategic_allocation"


def strategic_allocation_uses_open_item_admission(gate_manifest: Any) -> bool:
    """Identify the explicit open-research / item-level-admission profile."""

    if not isinstance(gate_manifest, Mapping):
        return False
    controls = gate_manifest.get("strategy_controls")
    return (
        isinstance(controls, Mapping)
        and normalize(controls.get("research_universe_mode"))
        == "open_with_item_level_admission"
    )


def strategic_allocation_can_skip_issuer_broker_gate(gate_manifest: Any) -> bool:
    """Skip issuer consensus only when there is no issuer under review.

    Legacy strategic cases can skip because direct stock exposure is expressly
    excluded.  An open-universe case can skip only while T3 contains no named
    direct equity; the manifest must instead require a valuation package for
    every future named T3 issuer.
    """

    if not isinstance(gate_manifest, Mapping):
        return False
    controls = gate_manifest.get("strategy_controls")
    if not isinstance(controls, Mapping):
        return False
    if strategic_allocation_uses_open_item_admission(gate_manifest):
        raw_tickers = controls.get("named_t3_direct_equity_tickers")
        named_tickers = (
            [str(ticker).strip() for ticker in raw_tickers if str(ticker).strip()]
            if isinstance(raw_tickers, Sequence)
            and not isinstance(raw_tickers, (str, bytes, bytearray))
            else []
        )
        return (
            first_float(controls.get("initial_direct_stock_weight")) == 0.0
            and normalize(controls.get("issuer_target_price_policy"))
            == "required_for_each_named_t3_direct_equity"
            and int_value(controls.get("named_t3_direct_equity_count")) == 0
            and not named_tickers
        )
    return strategic_allocation_has_zero_direct_stock(gate_manifest)


def strategic_allocation_has_zero_direct_stock(gate_manifest: Any) -> bool:
    if not isinstance(gate_manifest, Mapping):
        return False
    controls = gate_manifest.get("strategy_controls")
    if not isinstance(controls, Mapping):
        return False
    return (
        first_float(controls.get("initial_direct_stock_weight")) == 0.0
        and normalize(controls.get("issuer_target_price_policy")) in {"none", "not applicable"}
    )


def strategic_implementation_gates_are_blocking(payload: Any) -> tuple[bool, str]:
    """Require the distinct evidence and risk gates that keep a research pass non-live."""

    if not isinstance(payload, Mapping):
        return False, "implementation_gates missing or not an object"

    required = ("return_evidence", "risk_budget", "suitability", "execution")
    values = {key: normalize(payload.get(key)) for key in required}
    missing = [key for key, value in values.items() if not value]
    incorrect = [key for key, value in values.items() if not implementation_is_blocked(value)]
    detail = "; ".join(f"{key}={value or 'missing'}" for key, value in values.items())
    return not missing and not incorrect, detail


def strategic_execution_is_inactive(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, Mapping):
        return False, "execution_eligibility missing or not an object"

    status = normalize(payload.get("status"))
    q = first_float(payload.get("q"))
    active = payload.get("live_execution_authorized")
    return (
        implementation_is_blocked(status) and q == 0.0 and active is False,
        f"status={status or 'missing'}; q={q}; live_execution_authorized={active}",
    )


def strategic_material_claims_disclosed(
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
        key for key in STRATEGIC_MATERIAL_DISCLOSURE_KEYS if disclosure.get(key) is not True
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
    normalized_text = normalize(disclosure_text)
    reader_boundary_present = (
        ("not guarantee" in normalized_text or "not guaranteed" in normalized_text)
        and ("not approved" in normalized_text or "not authorized" in normalized_text)
    )
    detail = ", ".join(missing) if missing else "all structured boundaries disclosed"
    if not reader_boundary_present:
        detail = f"{detail}; reader-facing decision/residual rationale lacks explicit not-guarantee/not-approved wording"
    return not missing and reader_boundary_present, detail


def strategic_residual_risks_disclosed(payload: Any) -> tuple[bool, str]:
    if not isinstance(payload, Mapping):
        return False, "final sign-off missing or not an object"
    residual_risks = payload.get("residual_risks")
    if not isinstance(residual_risks, Sequence) or isinstance(
        residual_risks, (str, bytes, bytearray)
    ) or not residual_risks:
        return False, "residual_risks must list implementation blockers"
    text = normalize(" ".join(str(item) for item in residual_risks))
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
    return not missing, ", ".join(missing) if missing else "return evidence, risk budget and authorization blockers disclosed"


def implementation_is_blocked(status: str) -> bool:
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


def implementation_gate_is_not_approved(status: str) -> bool:
    """Accept an explicitly inactive implementation gate, including a named pending reason."""

    return implementation_is_blocked(status)


def extract_review_findings(payload: Any) -> list[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [cast(Mapping[str, Any], item) for item in payload if isinstance(item, Mapping)]
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
            if isinstance(value, list) and all(isinstance(item, Mapping) for item in value):
                return [cast(Mapping[str, Any], item) for item in value]
    return []


def review_severity(finding: Mapping[str, Any]) -> str:
    severity = normalize(
        finding.get("severity") or finding.get("level") or finding.get("priority")
    ).upper()
    if severity.startswith("S"):
        return "S"
    if severity.startswith("A"):
        return "A"
    return "B"


def review_status(finding: Mapping[str, Any]) -> str:
    return normalize(
        finding.get("status")
        or finding.get("lifecycle_status")
        or finding.get("state")
        or "open"
    )


def review_waived(finding: Mapping[str, Any]) -> bool:
    waiver_status = normalize(finding.get("waiver_status"))
    return (
        review_status(finding) == "waived"
        or waiver_status == "waived"
        or truthy(finding.get("waived"))
    )


def final_signoff_has_material_residual_risk_conflict(payload: Any) -> bool:
    if not isinstance(payload, Mapping):
        return False

    status = normalize(payload.get("signoff_status") or payload.get("status"))
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

    normalized_risk = normalize(residual_text)
    if not normalized_risk:
        return False

    downgrade_status = normalize(payload.get("downgrade_status"))
    if "downgrade" in downgrade_status and "none" not in downgrade_status:
        return False

    return any(term in normalized_risk for term in MATERIAL_RESIDUAL_RISK_TERMS)


def valuation_rows(payload: Any) -> list[Mapping[str, Any]]:
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
            cast(Mapping[str, Any], row)
            for row in payload
            if isinstance(row, Mapping)
        ]
    return []


def broker_consensus_rows(payload: Any) -> list[Mapping[str, Any]]:
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
            cast(Mapping[str, Any], row)
            for row in payload
            if isinstance(row, Mapping)
        ]
    return []


def float_value(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def first_float(*values: Any) -> float | None:
    for value in values:
        parsed = float_value(value)
        if parsed is not None:
            return parsed
    return None


def extract_publishability_score(review_log: str) -> int | None:
    patterns = (
        r"publishability\s+score\D+(\d{1,3})",
        r"publishability_score\D+(\d{1,3})",
        r"(?:publication|research[- ]framework)\s+score\D+(\d{1,3})",
    )
    for pattern in patterns:
        match = re.search(pattern, review_log, re.IGNORECASE)
        if match:
            return int(match.group(1))
    return None


def int_value(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return normalize(value) in {"1", "true", "yes", "y", "waived"}


def has_items(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return bool(value)
    return bool(str(value).strip())


def broker_value_usable(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return normalize(value) not in BROKER_UNAVAILABLE_VALUES
    if isinstance(value, Mapping):
        return any(broker_value_usable(item) for item in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return any(broker_value_usable(item) for item in value)
    return bool(str(value).strip())


def broker_row_external(row: Mapping[str, Any]) -> bool:
    broker = normalize(row.get("broker"))
    source_quality = normalize(row.get("source_quality"))
    source_path = normalize(row.get("source_path"))
    if source_quality not in BROKER_EXTERNAL_POSITIVE_SOURCE_QUALITIES:
        return False
    if source_quality in BROKER_INTERNAL_SOURCE_QUALITIES:
        return False
    if any(term in broker for term in BROKER_INTERNAL_NAME_TERMS):
        return False
    if source_path.startswith("analysis/") or source_path.startswith("data/current_valuation"):
        return False
    return bool(broker)


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def normalize(value: Any) -> str:
    return str(value or "").strip().lower()


def tail(text: str, lines: int = 20) -> str:
    cleaned = [line for line in text.splitlines() if line.strip()]
    return "\n".join(cleaned[-lines:])


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: run_research_gates.py <case-dir>", file=sys.stderr)
        return 2
    return GateRunner(Path(argv[1])).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
