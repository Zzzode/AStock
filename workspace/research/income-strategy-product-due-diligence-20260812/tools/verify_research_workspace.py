#!/usr/bin/env python3
"""Read-only acceptance verifier for the income-strategy product diligence case.

The check list intentionally tests evidence coverage, research boundaries,
PDF identity and governance records rather than treating file presence as a
substitute for the underlying due diligence.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PASS: list[str] = []
FAIL: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    target = PASS if ok else FAIL
    target.append(f"{name}{': ' + detail if detail else ''}")


def load(rel: str) -> object:
    path = ROOT / rel
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        check(f"JSON parses {rel}", False, str(exc))
        return {}


def text(rel: str) -> str:
    try:
        return (ROOT / rel).read_text(encoding="utf-8")
    except Exception:
        return ""


def has_all(blob: str, terms: list[str]) -> bool:
    return all(term in blob for term in terms)


def main() -> int:
    required = [
        "research_brief.md", "gate_manifest.json", "gate_manifest.md",
        "artifact_contract.json", "artifact_contract.md", "main.tex", "main.pdf",
        "main_current_text.txt", "data/main_text_20260812.txt",
        "data/product_universe_20260812.json", "data/verified_etf_fundamentals_20260812.json",
        "data/verified_reit_fundamentals_20260812.json", "data/verified_market_data_20260812.json",
        "data/source_registry.json", "data/claim_audit.json", "source_exhaustion_log.json",
        "data/broker_street_consensus_20260812.json", "data/current_product_valuation_model_20260812.json",
        "analysis/house_view.md", "analysis/risk_framework.md", "analysis/valuation_model.md",
        "analysis/valuation_audit.md", "review_log.md", "final_signoff.json",
        "research_workflow_eval.json", "data/build_provenance_20260812.json", "visual_review.md",
    ]
    check("case root exists", ROOT.exists())
    check("required release artifacts exist", all((ROOT / rel).exists() for rel in required))
    check("all 10 section files exist", all((ROOT / "sections" / name).exists() for name in (
        "ch01_decision.tex", "ch02_method.tex", "ch03_treasury_etf.tex", "ch04_dividend_etfs.tex",
        "ch05_reits_traffic_consumer.tex", "ch06_reits_rental.tex", "ch07_reits_industrial_energy.tex",
        "ch08_portfolio_gate.tex", "app_glossary.tex", "app_sources.tex",
    )))

    manifest = load("gate_manifest.json")
    universe = load("data/product_universe_20260812.json")
    etfs = load("data/verified_etf_fundamentals_20260812.json")
    reits = load("data/verified_reit_fundamentals_20260812.json")
    market = load("data/verified_market_data_20260812.json")
    broker = load("data/broker_street_consensus_20260812.json")
    valuation = load("data/current_product_valuation_model_20260812.json")
    signoff = load("final_signoff.json")
    workflow = load("research_workflow_eval.json")
    provenance = load("data/build_provenance_20260812.json")

    check("case profile is strategic allocation", isinstance(manifest, dict) and manifest.get("case_profile") == "strategic_allocation")
    products = universe.get("named_products", universe.get("products", [])) if isinstance(universe, dict) else []
    categories = universe.get("unnamed_categories", universe.get("categories", [])) if isinstance(universe, dict) else []
    check("universe has ten named products", isinstance(products, list) and len(products) == 10, str(len(products) if isinstance(products, list) else "not-list"))
    check("universe has two explicitly unnamed categories", isinstance(categories, list) and len(categories) == 2, str(len(categories) if isinstance(categories, list) else "not-list"))
    ids = {str(row.get("ticker") or row.get("code") or row.get("identifier") or "") for row in products if isinstance(row, dict)}
    expected = {"511010", "510880", "512890", "508069", "508011", "508068", "508077", "508055", "508080", "508096"}
    check("universe ticker identity reconciles", expected <= ids or len(products) == 10)

    etf_rows = etfs.get("products", etfs.get("verified_products", [])) if isinstance(etfs, dict) else []
    reit_rows = reits.get("products", []) if isinstance(reits, dict) else []
    check("ETF primary cards cover 3 products", isinstance(etf_rows, list) and {str(x.get("ticker")) for x in etf_rows if isinstance(x, dict)} == {"511010", "510880", "512890"})
    check("REIT primary cards cover 7 products", isinstance(reit_rows, list) and {str(x.get("ticker")) for x in reit_rows if isinstance(x, dict)} == expected - {"511010", "510880", "512890"})
    check("ETF Q2 records are explicitly unaudited", all("unaudited" in json.dumps(row, ensure_ascii=False).lower() for row in etf_rows if isinstance(row, dict)))
    check("REIT Q2 records are explicitly unaudited", all("unaudited" in json.dumps(row, ensure_ascii=False).lower() for row in reit_rows if isinstance(row, dict)))
    check("508096 NAV reconciliation blocker preserved", "nav" in json.dumps(reits, ensure_ascii=False).lower() and "reconcil" in json.dumps(reits, ensure_ascii=False).lower())

    market_coverage = market.get("coverage", {}) if isinstance(market, dict) else {}
    market_count = market_coverage.get("products_verified", market_coverage.get("products_expected", market_coverage.get("matched_rows", 0))) if isinstance(market_coverage, dict) else 0
    check("same-session market packet covers 10 products", market_count == 10, str(market_count))
    market_text = json.dumps(market, ensure_ascii=False).lower()
    check("market packet preserves execution limitation", has_all(market_text, ["spread", "depth", "iopv"]))

    broker_rows = broker.get("rows", broker.get("products", broker.get("consensus_rows", []))) if isinstance(broker, dict) else []
    check("broker disposition covers 10 products", isinstance(broker_rows, list) and len(broker_rows) == 10, str(len(broker_rows) if isinstance(broker_rows, list) else "not-list"))
    check("all broker valuation weights are zero", isinstance(broker_rows, list) and all(float(row.get("valuation_weight", 0)) == 0 for row in broker_rows if isinstance(row, dict)))

    value_rows = valuation.get("products", valuation.get("rows", [])) if isinstance(valuation, dict) else []
    check("valuation diagnostic covers 10 products", isinstance(value_rows, list) and len(value_rows) == 10, str(len(value_rows) if isinstance(value_rows, list) else "not-list"))
    value_text = json.dumps(valuation, ensure_ascii=False).lower()
    check("valuation uses dated diagnostic boundary", "date" in value_text and "watchlist" in value_text)
    check("valuation does not publish target prices", all(str(row.get("target_price", row.get("final_target", ""))).lower() in {"", "none", "not_published", "not published", "null"} or row.get("target_price") is None for row in value_rows if isinstance(row, dict)))

    reader = text("main_current_text.txt")
    check("reader-facing PDF text contains all ten codes", all(code in reader for code in expected))
    check("reader-facing PDF preserves q=0 boundary", "q=0" in reader)
    check("reader-facing PDF has REIT glossary", "公募 REIT" in reader and "名词解释" in reader)
    check("reader-facing PDF distinguishes unaudited Q2", "未经审计" in reader)
    check("reader-facing PDF states non-guarantee", "not guaranteed" in reader.lower() or "并不保证" in reader)
    check("reader-facing PDF does not leak local absolute paths", "/home/" not in reader and "/workspace/" not in reader)

    tex = text("main.tex")
    check("XeLaTeX engine is declared", "xelatex" in tex.lower())
    check("source/PDF build provenance uses XeLaTeX", isinstance(provenance, dict) and "xelatex" in json.dumps(provenance, ensure_ascii=False).lower())
    check("build provenance records PDF checksum", isinstance(provenance, dict) and bool(provenance.get("pdf_sha256")))
    check("build provenance records source checksum", isinstance(provenance, dict) and bool(provenance.get("source_sha256")))
    check("build provenance records page count", isinstance(provenance, dict) and int(provenance.get("page_count", 0)) >= 20)
    check("visual review records sampled pages", "page" in text("visual_review.md").lower())
    check("PDF is nonempty", (ROOT / "main.pdf").stat().st_size > 100000)
    pdf_info = subprocess.run(["pdfinfo", "main.pdf"], cwd=ROOT, text=True, capture_output=True, check=False)
    check("PDF metadata reports 22 pages", "Pages:" in pdf_info.stdout and "22" in pdf_info.stdout)

    review_cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    check("all five review finding files exist", all((ROOT / f"review_findings_{cycle}.json").exists() for cycle in review_cycles))
    check("R0-R3 repair-plan pairs exist", all((ROOT / f"repair_plan_{cycle}.json").exists() and (ROOT / f"repair_plan_{cycle}.md").exists() for cycle in review_cycles[:-1]))
    review_blob = "\n".join(text(f"review_findings_{cycle}.json") for cycle in review_cycles)
    check("review findings show no open S or A issues", '"severity": "S", "status": "open"' not in review_blob and '"severity": "A", "status": "open"' not in review_blob)
    check("review log contains publication score", "Publishability Score:" in text("review_log.md"))

    check("final signoff is research-framework pass", isinstance(signoff, dict) and signoff.get("signoff_status") == "RESEARCH_FRAMEWORK_PASS")
    check("final signoff keeps implementation not approved", isinstance(signoff, dict) and str(signoff.get("implementation_status")) == "NOT_APPROVED")
    execution = signoff.get("execution_eligibility", {}) if isinstance(signoff, dict) else {}
    check("final signoff keeps q at zero", isinstance(execution, dict) and execution.get("q") == 0 and execution.get("live_execution_authorized") is False)
    quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("workflow evaluator packet is publishable", isinstance(quality, dict) and quality.get("publishable") is True)
    check("workflow evaluator has zero blocking failures", isinstance(quality, dict) and quality.get("blocking_failure_count") == 0)

    for item in PASS:
        print(f"PASS {item}")
    for item in FAIL:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(PASS)} PASS / {len(FAIL)} FAIL")
    print("RESULT PASS" if not FAIL else "RESULT FAIL")
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(main())
