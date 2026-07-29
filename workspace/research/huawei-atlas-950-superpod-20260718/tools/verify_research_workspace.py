#!/usr/bin/env python3
"""Read-only 39-check verifier for the Atlas 950 research workspace."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


CASE = Path(__file__).resolve().parents[1]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""


def load(path: Path) -> Any:
    return json.loads(read(path))


class Verifier:
    def __init__(self) -> None:
        self.passes: list[str] = []
        self.failures: list[str] = []

    def check(self, name: str, condition: bool, detail: str = "") -> None:
        line = f"{name}: {detail}" if detail else name
        (self.passes if condition else self.failures).append(line)

    def exists(self, name: str, *paths: str) -> None:
        missing = [path for path in paths if not (CASE / path).exists()]
        self.check(name, not missing, f"missing={missing}")

    def run(self) -> int:
        self.check("01 case directory", CASE.is_dir(), str(CASE))
        self.exists("02 report source and PDF", "main.tex", "main.pdf")
        self.exists("03 extracted text and visual review", "main_current_text.txt", "visual_review.md")
        self.exists("04 scope and template briefs", "research_brief.md", "analysis/template_brief.md")
        self.exists("05 gate manifest pair", "gate_manifest.md", "gate_manifest.json")
        self.exists("06 artifact contract pair", "artifact_contract.md", "artifact_contract.json")
        self.exists("07 source registry pair", "data/source_registry.md", "data/source_registry.json")
        self.exists("08 claim audit pair", "data/claim_audit.md", "data/claim_audit.json")
        self.exists("09 source exhaustion pair", "source_exhaustion_log.md", "source_exhaustion_log.json")
        self.exists("10 raw financial and market packets", "data/raw_financials.md", "data/raw_market_data.md")
        self.exists("11 verified financial and market packets", "data/verified_financials.md", "data/verified_market_data.md")
        self.exists("12 broker catalog and analysis", "data/report_catalog.md", "data/consensus_analysis.md")

        pdfs = list((CASE / "sources/broker-reports/2026-07-18").glob("*.pdf"))
        texts = list((CASE / "sources/broker-reports/2026-07-18").glob("*.txt"))
        self.check("13 original broker archive depth", len(pdfs) >= 38 and len(texts) >= 38, f"pdf={len(pdfs)} txt={len(texts)}")
        self.exists("14 broker consensus pair", "data/broker_street_consensus_20260718.md", "data/broker_street_consensus_20260718.json")
        consensus = load(CASE / "data/broker_street_consensus_20260718.json") if (CASE / "data/broker_street_consensus_20260718.json").exists() else {}
        crows = consensus.get("rows", []) if isinstance(consensus, dict) else []
        qualities = {row.get("source_quality") for row in crows if isinstance(row, dict)}
        self.check("15 broker schema and source-quality vocabulary", len(crows) >= 36 and qualities <= {"original_pdf", "not_found"}, f"rows={len(crows)} qualities={sorted(str(x) for x in qualities)}")

        self.exists("16 full-chain universe pair", "data/full_chain_universe_20260718.md", "data/full_chain_universe_20260718.json")
        universe = load(CASE / "data/full_chain_universe_20260718.json") if (CASE / "data/full_chain_universe_20260718.json").exists() else {}
        urows = universe.get("rows", []) if isinstance(universe, dict) else []
        blocks = {row.get("chain_block") for row in urows if isinstance(row, dict)}
        required_universe = {"node_type", "chain_block", "subsegment", "evidence_status", "source_count", "classification", "valuation_status", "next_verification_path"}
        self.check("17 full-chain coverage and schema", len(urows) >= 50 and len(blocks) == 8 and all(required_universe <= set(row) for row in urows), f"rows={len(urows)} blocks={len(blocks)}")
        self.exists("18 full-chain analysis set", "analysis/full_chain_taxonomy.md", "analysis/core_vs_satellite_universe.md", "analysis/coverage_gap_matrix.md")
        self.exists("19 supply-chain model and relationship pair", "analysis/supply_chain_model.md", "data/supply_chain_relationships.md", "data/supply_chain_relationships.json")
        relationships = load(CASE / "data/supply_chain_relationships.json") if (CASE / "data/supply_chain_relationships.json").exists() else {}
        rrows = relationships.get("rows", []) if isinstance(relationships, dict) else []
        relationship_fields = {"ticker", "company", "chain_layer", "product_or_process", "downstream_customer_or_platform", "source_tier", "order_visibility", "valuation_eligibility", "evidence_gap"}
        self.check("20 relationship depth", len(rrows) >= 14 and all(relationship_fields <= set(row) for row in rrows), f"rows={len(rrows)}")
        self.exists("21 customer-chain audit pair", "data/customer_chain_audit.md", "data/customer_chain_audit.json")
        audits = load(CASE / "data/customer_chain_audit.json") if (CASE / "data/customer_chain_audit.json").exists() else {}
        arows = audits.get("rows", []) if isinstance(audits, dict) else []
        audit_text = json.dumps(arows, ensure_ascii=False).lower()
        self.check("22 customer audit includes negative/unconfirmed evidence", len(arows) >= 8 and any(term in audit_text for term in ("not confirmed", "denied", "unconfirmed", "未确认", "否认")), f"rows={len(arows)}")
        self.exists("23 industry and competition", "analysis/industry_landscape.md", "analysis/competitive_landscape.md")
        industry = read(CASE / "analysis/industry_landscape.md")
        self.check("24 physical/roadmap/memory boundary", all(term in industry for term in ("1,024", "8,192", "256 TB", "global unified address space", "not the same as")))
        self.exists("25 house view and variant perception", "analysis/house_view.md", "analysis/variant_perception.md")
        self.exists("26 growth earnings artifact set", "analysis/growth_earnings_model.md", "analysis/segment_forecast_bridge.md", "analysis/implied_growth_sensitivity.md", "data/growth_driver_model.json")
        growth = load(CASE / "data/growth_driver_model.json") if (CASE / "data/growth_driver_model.json").exists() else {}
        drivers = growth.get("drivers", []) if isinstance(growth, dict) else []
        self.check("27 growth model depth", len(drivers) >= 12 and all(row.get("valuation_credit") and row.get("next_quarter_validation_threshold") for row in drivers), f"rows={len(drivers)}")
        self.exists("28 valuation artifact set", "analysis/valuation_model.md", "analysis/valuation_audit.md", "data/current_valuation_model_20260718.md", "data/current_valuation_model_20260718.json")
        valuation = load(CASE / "data/current_valuation_model_20260718.json") if (CASE / "data/current_valuation_model_20260718.json").exists() else {}
        vrows = valuation.get("rows", []) if isinstance(valuation, dict) else []
        arithmetic_ok = all(abs((row["final_target"] / row["current_price"] - 1) - row["upside"]) <= 0.005 for row in vrows)
        self.check("29 valuation rows and arithmetic", len(vrows) >= 12 and arithmetic_ok, f"rows={len(vrows)}")
        self.check("30 Atlas earnings credit is zero", bool(vrows) and all(row.get("atlas_950_revenue_credit_2026e_100mn") == 0 for row in vrows))
        self.check("31 valuation reproducibility pass", "Model Reproducibility: PASS" in read(CASE / "analysis/valuation_audit.md"))
        self.exists("32 risk and contrarian artifacts", "analysis/risk_framework.md", "analysis/risk_matrix.md", "analysis/contrarian_case.md")
        self.exists("33 exhibit and narrative plans", "analysis/exhibit_plan.md", "analysis/narrative_blueprint.md", "analysis/narrative_evidence_map.md")

        sections = list((CASE / "sections").glob("*.tex"))
        self.check("34 report section depth", len(sections) >= 13, f"sections={len(sections)}")
        report_text = read(CASE / "main_current_text.txt")
        required_report_terms = ("1,024", "8,192", "256TB", "申菱环境", "科大讯飞", "Atlas 专属收入", "估值", "风险")
        self.check("35 reader report contains required decisions", len(report_text) >= 30000 and all(term in report_text for term in required_report_terms), f"chars={len(report_text)}")
        bad_markers = re.findall(r"<[^>]+>|TODO|TBD|FIXME|是否\.\.\.|是否…", report_text, flags=re.I)
        self.check("36 reader report has no unfinished markers", not bad_markers, f"markers={bad_markers[:8]}")

        page_count = 0
        if (CASE / "main.pdf").exists():
            proc = subprocess.run(["pdfinfo", str(CASE / "main.pdf")], text=True, capture_output=True, check=False)
            match = re.search(r"^Pages:\s+(\d+)", proc.stdout, flags=re.M)
            page_count = int(match.group(1)) if match else 0
        self.check("37 PDF page count and validity", page_count >= 25 and (CASE / "main.pdf").stat().st_size >= 500_000 if (CASE / "main.pdf").exists() else False, f"pages={page_count}")

        cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
        findings_ok = all((CASE / f"review_findings_{cycle}.json").exists() for cycle in cycles)
        open_blockers = 0
        if findings_ok:
            for cycle in cycles:
                payload = load(CASE / f"review_findings_{cycle}.json")
                for finding in payload.get("findings", []):
                    if finding.get("severity") in {"S", "A"} and finding.get("status") not in {"closed", "verified", "resolved", "pass", "passed"} and not finding.get("waived", False):
                        open_blockers += 1
        self.check("38 review lifecycle and zero blockers", findings_ok and open_blockers == 0, f"open_blockers={open_blockers}")

        self.exists("39 final signoff and workflow evaluation", "review_log.md", "final_signoff.md", "final_signoff.json", "research_workflow_eval.md", "research_workflow_eval.json")

        for item in self.passes:
            print(f"PASS {item}")
        for item in self.failures:
            print(f"FAIL {item}")
        print(f"SUMMARY {len(self.passes)} PASS / {len(self.failures)} FAIL")
        return 0 if not self.failures else 1


if __name__ == "__main__":
    raise SystemExit(Verifier().run())
