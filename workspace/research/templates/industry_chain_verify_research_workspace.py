#!/usr/bin/env python3
"""Reusable industry-chain research workspace content verifier.

Copy this script into `workspace/research/<case>/tools/` or run it directly:

    python3 workspace/research/templates/industry_chain_verify_research_workspace.py workspace/research/<case>

This template checks content gates that generic case verifiers often miss:
full-chain universe, core/satellite classification, coverage gaps, value-chain
economics, competitive landscape, source exhaustion, valuation reproducibility,
variant perception, and publishability score.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


NODE_TYPES = {"listed", "overseas", "private", "demand_anchor", "low_purity", "unavailable"}
REQUIRED_UNIVERSE_FIELDS = {
    "node_type",
    "chain_block",
    "subsegment",
    "evidence_status",
    "source_count",
    "classification",
    "valuation_status",
    "next_verification_path",
}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def extract_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("rows", "nodes", "universe", "full_chain_universe", "items"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        for value in payload.values():
            if isinstance(value, list) and all(isinstance(row, dict) for row in value):
                return value
    return []


def text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


class Verifier:
    def __init__(self, case_dir: Path) -> None:
        self.case_dir = case_dir
        self.failures: list[str] = []
        self.passes: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        message = f"{name}: {detail}" if detail else name
        if condition:
            self.passes.append(message)
        else:
            self.failures.append(message)

    def exists(self, rel: str) -> Path:
        path = self.case_dir / rel
        self.check(f"exists {rel}", path.exists())
        return path

    def run(self) -> int:
        if not self.case_dir.exists():
            print(f"FAIL case directory missing: {self.case_dir}")
            return 2

        self.exists("research_brief.md")
        self.exists("analysis/template_brief.md")
        self.exists("analysis/full_chain_taxonomy.md")
        self.exists("analysis/core_vs_satellite_universe.md")
        self.exists("analysis/coverage_gap_matrix.md")
        self.exists("analysis/competitive_landscape.md")
        self.exists("analysis/value_chain_economics.md")
        self.exists("analysis/supply_chain_model.md")
        self.exists("analysis/company_fundamental_cards.md")
        self.exists("analysis/core_candidate_company_cards.md")
        self.exists("analysis/valuation_coverage_reconciliation.md")
        self.exists("analysis/chain_earnings_bridge.md")
        self.exists("analysis/variant_perception.md")
        self.exists("analysis/valuation_audit.md")
        self.exists("analysis/field_evidence_completion_audit.md")
        self.exists("analysis/residual_proxy_field_audit.md")
        self.exists("data/supply_chain_relationships.json")
        self.exists("data/customer_chain_audit.json")
        self.exists("data/field_evidence_completion_20260701.json")
        self.exists("data/proxy_field_official_filing_collection_20260701.json")
        self.exists("data/residual_proxy_field_audit_20260701.json")
        self.exists("data/growth_driver_model.json")
        self.exists("data/valuation_triage_20260630.json")
        self.exists("data/core_candidate_valuation_disposition_20260630.json")
        self.exists("data/source_registry.json")
        self.exists("data/claim_audit.json")
        self.exists("source_exhaustion_log.md")
        self.exists("source_exhaustion_log.json")
        self.exists("review_log.md")

        universe_files = sorted((self.case_dir / "data").glob("full_chain_universe_*.json"))
        self.check("full-chain universe json present", bool(universe_files))
        rows: list[dict[str, Any]] = []
        if universe_files:
            try:
                rows = extract_rows(load_json(universe_files[-1]))
            except Exception as exc:  # pragma: no cover - defensive verifier output
                self.failures.append(f"full-chain universe json parses: {exc}")
            self.check("full-chain universe rows present", bool(rows))

        if rows:
            missing_fields = [
                idx
                for idx, row in enumerate(rows, start=1)
                if REQUIRED_UNIVERSE_FIELDS - set(row.keys())
            ]
            invalid_node_types = [
                idx for idx, row in enumerate(rows, start=1) if str(row.get("node_type", "")) not in NODE_TYPES
            ]
            blocks = {str(row.get("chain_block", "")).strip() for row in rows if row.get("chain_block")}
            classifications = {str(row.get("classification", "")).strip() for row in rows}
            node_types = {str(row.get("node_type", "")).strip() for row in rows}
            brief = (text(self.case_dir / "research_brief.md") + "\n" + text(self.case_dir / "analysis/template_brief.md")).lower()
            min_blocks = 8 if "aidc" in brief or "ai data-center" in brief else 4
            self.check("universe required fields", not missing_fields, f"rows missing fields: {missing_fields[:10]}")
            self.check("universe node_type enum", not invalid_node_types, f"invalid rows: {invalid_node_types[:10]}")
            self.check("universe chain block count", len(blocks) >= min_blocks, f"{len(blocks)} blocks, required {min_blocks}")
            self.check("core valuation classification present", "core_valuation" in classifications)
            self.check("satellite or watch classification present", bool({"satellite_watch", "watchlist", "satellite"} & classifications))
            self.check("demand anchor nodes present", "demand_anchor" in node_types)

        coverage = text(self.case_dir / "analysis/coverage_gap_matrix.md").lower()
        self.check("coverage gap has next verification path", "next verification" in coverage or "next_verification_path" in coverage)
        self.check("coverage gap has valuation blocker", "valuation" in coverage and "block" in coverage)

        economics = text(self.case_dir / "analysis/value_chain_economics.md").lower()
        for keyword in ("asp", "margin", "capacity", "certification", "valuation"):
            self.check(f"value-chain economics has {keyword}", keyword in economics)

        competitive = text(self.case_dir / "analysis/competitive_landscape.md").lower()
        for keyword in ("global", "china", "localization", "substitution"):
            self.check(f"competitive landscape has {keyword}", keyword in competitive)

        consensus = text(self.case_dir / "data/consensus_analysis.md").lower()
        self.check("consensus labels source quality", "source_quality" in consensus or "source quality" in consensus)

        valuation_audit = text(self.case_dir / "analysis/valuation_audit.md")
        self.check("valuation model reproducibility pass", "Model Reproducibility: PASS" in valuation_audit)

        triage_rows = extract_rows(load_json(self.case_dir / "data/valuation_triage_20260630.json"))
        core_rows = extract_rows(load_json(self.case_dir / "data/core_candidate_valuation_disposition_20260630.json"))
        self.check("valuation triage covers mapped stock pool", len(triage_rows) >= 173, f"rows={len(triage_rows)}")
        self.check("core candidate disposition covers core pool", len(core_rows) >= 58, f"rows={len(core_rows)}")
        self.check(
            "valuation triage has disposition fields",
            all(row.get("valuation_disposition") and row.get("target_price_status") for row in triage_rows),
        )
        self.check(
            "core candidate cards reference all core rows",
            all(str(row.get("company")) in text(self.case_dir / "analysis/core_candidate_company_cards.md") for row in core_rows),
        )

        chain_matrix_payload = load_json(self.case_dir / "data/chain_business_matrix_20260630.json")
        chain_block_rows = chain_matrix_payload.get("block_rows", []) if isinstance(chain_matrix_payload, dict) else []
        chain_company_rows = chain_matrix_payload.get("company_rows", []) if isinstance(chain_matrix_payload, dict) else []
        chain_company_fields = {
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
        }
        missing_chain_business_fields = [
            str(row.get("company") or "<missing company>")
            for row in chain_company_rows
            if isinstance(row, dict)
            and (
                chain_company_fields - set(row.keys())
                or any(not row.get(field) for field in chain_company_fields)
            )
        ]
        self.check("chain business matrix has all AIDC blocks", len(chain_block_rows) == 8, f"block_rows={len(chain_block_rows)}")
        self.check("chain business matrix covers core candidates", len(chain_company_rows) >= 58, f"company_rows={len(chain_company_rows)}")
        self.check("chain business matrix company fields complete", not missing_chain_business_fields, "; ".join(missing_chain_business_fields[:10]))

        supply_chain_chapter = text(self.case_dir / "sections/ch04_supply_chain.tex")
        required_chapter_terms = (
            "算力与存储",
            "服务器、整柜与网络设备",
            "光通信",
            "PCB、CCL",
            "供配电与液冷",
            "AIDC/IDC 运营",
            "附录证据索引",
            "价值量--收入确认--利润率--现金流--估值信用",
        )
        missing_chapter_terms = [term for term in required_chapter_terms if term not in supply_chain_chapter]
        first_exhibit = supply_chain_chapter.find(r"\begin{exhibitbox}")
        chapter_prose = supply_chain_chapter[:first_exhibit] if first_exhibit >= 0 else supply_chain_chapter
        prose_chars = len(re.sub(r"\\[A-Za-z]+\*?(?:\{[^{}]*\})?", "", chapter_prose).strip())
        matrix_in_chapter = (
            "58 个核心候选公司级产业链业务矩阵" in supply_chain_chapter
            or "company_chain_business_tex_table" in supply_chain_chapter
        )
        self.check("supply-chain chapter has prose before exhibits", prose_chars >= 2200, f"prose_chars={prose_chars}")
        self.check("supply-chain chapter covers causal chain", not missing_chapter_terms, "; ".join(missing_chapter_terms))
        self.check("supply-chain company matrix kept out of main chapter", not matrix_in_chapter)

        relationships_payload = load_json(self.case_dir / "data/supply_chain_relationships.json")
        relationships = relationships_payload.get("relationships", []) if isinstance(relationships_payload, dict) else []
        relationship_fields = {
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
            "valuation_eligibility",
            "downgrade_trigger",
        }
        missing_relationship_fields = [
            str(row.get("company") or "<missing company>")
            for row in relationships
            if isinstance(row, dict) and relationship_fields - set(row.keys())
        ]
        self.check("supply-chain relationships cover core candidates", len(relationships) >= 58, f"rows={len(relationships)}")
        self.check("supply-chain relationship fields complete", not missing_relationship_fields, "; ".join(missing_relationship_fields[:10]))

        audit_payload = load_json(self.case_dir / "data/customer_chain_audit.json")
        audits = audit_payload.get("audits", []) if isinstance(audit_payload, dict) else []
        audit_fields = {
            "ticker",
            "company",
            "customer_or_platform",
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
        }
        missing_audit_fields = [
            str(row.get("company") or "<missing company>")
            for row in audits
            if isinstance(row, dict) and audit_fields - set(row.keys())
        ]
        target_claim_types = {
            "target_model_customer_chain",
            "extended_target_model_customer_chain",
            "extended_house_fair_value_customer_chain",
            "extended_ps_sotp_customer_chain",
        }
        target_audits = [row for row in audits if isinstance(row, dict) and row.get("claim_type") in target_claim_types]
        expected_target_rows = int((audit_payload.get("metadata") or {}).get("target_model_rows") or 18) if isinstance(audit_payload, dict) else 18
        blocked_targets = [str(row.get("company") or "<missing company>") for row in target_audits if row.get("blocks_valuation") is True]
        self.check("customer-chain audit covers core candidates", len(audits) >= 58, f"rows={len(audits)}")
        self.check("customer-chain audit fields complete", not missing_audit_fields, "; ".join(missing_audit_fields[:10]))
        self.check("customer-chain target rows not valuation-blocked", len(target_audits) >= expected_target_rows and not blocked_targets, f"target_rows={len(target_audits)} expected={expected_target_rows} blocked={blocked_targets[:10]}")

        field_payload = load_json(self.case_dir / "data/field_evidence_completion_20260701.json")
        field_rows = field_payload.get("rows", []) if isinstance(field_payload, dict) else []
        field_metadata = field_payload.get("metadata", {}) if isinstance(field_payload, dict) else {}
        required_evidence_fields = {
            "revenue_exposure",
            "customer_or_platform",
            "order_or_backlog",
            "capacity_or_certification",
            "asp_or_price_proxy",
            "utilization_or_yield",
            "margin_impact",
        }
        missing_field_schema = [
            str(row.get("ticker") or row.get("company") or "<missing>")
            for row in field_rows
            if not isinstance(row.get("fields"), dict)
            or required_evidence_fields - set(row.get("fields", {}).keys())
        ]
        unresolved_target_fields = []
        for row in field_rows:
            if not isinstance(row, dict) or row.get("target_model") is not True:
                continue
            cells = row.get("fields", {})
            for field in required_evidence_fields:
                status = str(cells.get(field, {}).get("status") or "")
                if status in {"", "source_exhausted", "watchlist_blocked"}:
                    unresolved_target_fields.append(f"{row.get('ticker')}:{field}:{status}")
        total_cells = int(field_metadata.get("total_field_cells") or 0)
        self.check("field evidence completion covers candidates", len(field_rows) >= 59 and total_cells >= len(field_rows) * len(required_evidence_fields), f"rows={len(field_rows)} cells={total_cells}")
        self.check("field evidence completion schema complete", not missing_field_schema, "; ".join(missing_field_schema[:10]))
        self.check("field evidence target models have no unresolved fields", not unresolved_target_fields, "; ".join(unresolved_target_fields[:10]))

        proxy_tickers = {
            str(row.get("ticker"))
            for row in field_rows
            if isinstance(row, dict)
            and any(isinstance(cell, dict) and cell.get("status") == "proxy" for cell in row.get("fields", {}).values())
        }
        proxy_payload = load_json(self.case_dir / "data/proxy_field_official_filing_collection_20260701.json")
        proxy_rows = proxy_payload.get("rows", []) if isinstance(proxy_payload, dict) else []
        covered_proxy_tickers = {
            str(row.get("ticker"))
            for row in proxy_rows
            if isinstance(row, dict) and int(row.get("filings_archived") or 0) > 0
        }
        proxy_missing = sorted(ticker for ticker in proxy_tickers if ticker and ticker not in covered_proxy_tickers)
        proxy_hit_cells = 0
        for row in proxy_rows:
            if not isinstance(row, dict):
                continue
            proxy_hit_cells += sum(1 for value in row.get("proxy_field_direct_hits", {}).values() if int(value or 0) > 0)
        self.check("proxy-field official collection covers proxy candidates", proxy_tickers <= covered_proxy_tickers, f"proxy_candidates={len(proxy_tickers)} covered={len(covered_proxy_tickers)} missing={proxy_missing[:10]}")
        self.check("proxy-field official collection has extracted field hits", proxy_hit_cells >= len(proxy_tickers), f"hit_cells={proxy_hit_cells} proxy_candidates={len(proxy_tickers)}")

        proxy_cells = []
        for row in field_rows:
            if not isinstance(row, dict):
                continue
            for field, cell in (row.get("fields") or {}).items():
                if isinstance(cell, dict) and cell.get("status") == "proxy":
                    proxy_cells.append((str(row.get("ticker")), str(field)))
        residual_payload = load_json(self.case_dir / "data/residual_proxy_field_audit_20260701.json")
        residual_rows = residual_payload.get("rows", []) if isinstance(residual_payload, dict) else []
        residual_covered = {
            (str(row.get("ticker")), str(row.get("field")))
            for row in residual_rows
            if isinstance(row, dict)
        }
        residual_missing = [f"{ticker}:{field}" for ticker, field in proxy_cells if (ticker, field) not in residual_covered]
        residual_shallow = [
            f"{row.get('ticker')}:{row.get('field')}"
            for row in residual_rows
            if isinstance(row, dict)
            and (
                not row.get("remaining_gap")
                or not row.get("valuation_consequence")
                or not row.get("next_verification_path")
            )
        ]
        self.check("residual proxy-field audit covers proxy cells", len(residual_rows) == len(proxy_cells) and not residual_missing, f"proxy_cells={len(proxy_cells)} audit_rows={len(residual_rows)} missing={residual_missing[:10]}")
        self.check("residual proxy-field audit has valuation consequence", not residual_shallow, "; ".join(residual_shallow[:10]))

        growth_payload = load_json(self.case_dir / "data/growth_driver_model.json")
        drivers = growth_payload.get("drivers", []) if isinstance(growth_payload, dict) else []
        growth_fields = {
            "ticker",
            "company",
            "growth_segment_revenue",
            "unit_volume_or_proxy",
            "ASP_or_price",
            "value_amount_or_proxy",
            "supply_demand_state",
            "capacity_or_utilization",
            "certification_or_customer_qualification",
            "recognized_revenue_ratio",
            "incremental_opex",
            "growth_net_profit_100mn",
            "growth_EPS",
            "current_price_implied_growth",
            "next_quarter_validation_threshold",
        }
        missing_growth_fields = [
            str(row.get("company") or "<missing company>")
            for row in drivers
            if isinstance(row, dict) and growth_fields - set(row.keys())
        ]
        generic_growth = [
            str(row.get("company") or "<missing company>")
            for row in drivers
            if isinstance(row, dict)
            and any(
                token in str(row.get(field) or "").lower()
                for field in ("growth_segment_revenue", "unit_volume_or_proxy", "ASP_or_price")
                for token in ("growth segment not separately disclosed", "not uniformly disclosed", "use current price implied pe only")
            )
        ]
        self.check("growth-driver model covers valuation universe", len(drivers) >= 18, f"rows={len(drivers)}")
        self.check("growth-driver fields complete", not missing_growth_fields, "; ".join(missing_growth_fields[:10]))
        self.check("growth-driver has no generic placeholders", not generic_growth, "; ".join(generic_growth[:10]))

        variant = text(self.case_dir / "analysis/variant_perception.md").lower()
        for keyword in ("consensus", "opposing", "falsification", "trigger"):
            self.check(f"variant perception has {keyword}", keyword in variant)

        review_log = text(self.case_dir / "review_log.md")
        score_match = re.search(r"publishability\s+score\D+(\d{1,3})", review_log, re.IGNORECASE)
        score = int(score_match.group(1)) if score_match else None
        self.check("review log publishability score present", score is not None)
        if score is not None:
            self.check("publishability score pass threshold", score >= 90, str(score))

        for item in self.passes:
            print(f"PASS {item}")
        for item in self.failures:
            print(f"FAIL {item}")
        print(f"SUMMARY {len(self.passes)} PASS / {len(self.failures)} FAIL")
        return 1 if self.failures else 0


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: industry_chain_verify_research_workspace.py <case-dir>", file=sys.stderr)
        return 2
    return Verifier(Path(argv[1])).run()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
