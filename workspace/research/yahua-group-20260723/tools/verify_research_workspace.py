#!/usr/bin/env python3
"""Publication verifier for the Yahua full single-stock coverage case."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


CASE = Path(__file__).resolve().parents[1]
PASS_STATUSES = {"closed", "verified", "resolved", "pass", "passed", "approved"}
passes: list[str] = []
failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    message = f"{name}: {detail}" if detail else name
    (passes if condition else failures).append(message)


def read(rel: str) -> str:
    path = CASE / rel
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def load(rel: str) -> Any:
    try:
        return json.loads(read(rel))
    except json.JSONDecodeError:
        return {}


def pages() -> int:
    pdf = CASE / "main.pdf"
    if not pdf.exists():
        return 0
    output = subprocess.run(
        ["pdfinfo", str(pdf)], text=True, capture_output=True, check=False
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)$", output, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        for key in ("rows", "findings", "issues"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
    return payload if isinstance(payload, list) else []


def findings_closed(rel: str) -> bool:
    result = rows(load(rel))
    return bool(result) and all(
        str(item.get("status", item.get("lifecycle_status", "open"))).lower()
        in PASS_STATUSES
        or str(item.get("waiver_status", "")).lower() == "waived"
        for item in result
    )


def contains_all(text: str, tokens: tuple[str, ...]) -> bool:
    lower = text.lower()
    return all(token.lower() in lower for token in tokens)


def main() -> int:
    gate = load("gate_manifest.json")
    contract = load("artifact_contract.json")
    registry = load("data/source_registry.json")
    claims = load("data/claim_audit.json")
    exhaustion = load("source_exhaustion_log.json")
    brokers = load("data/broker_street_consensus_20260723.json")
    growth = load("data/growth_driver_model.json")
    model = load("data/current_valuation_model_20260723.json")
    signoff = load("final_signoff.json")
    workflow = load("research_workflow_eval.json")
    extracted = read("main_current_text.txt")
    valuation = read("analysis/valuation_model.md")

    required_sections = {
        "ch01_dashboard.tex", "ch02_variant.tex", "ch03_lithium.tex",
        "ch04_minblast.tex", "ch05_financials.tex", "ch06_competition.tex",
        "ch07_market.tex", "ch08_valuation.tex", "ch09_risks.tex",
        "ch10_cycle.tex", "ch11_model_detail.tex", "ch12_peer.tex",
        "ch13_reassessment.tex", "app_model_disclosure.tex", "app_source_audit.tex",
        "app_historical.tex", "app_model_inputs.tex", "app_relationships.tex",
        "app_governance.tex", "app_reconciliation.tex",
    }
    valuation_sections = (
        "Final Valuation Table", "Three-Tier Targets", "Relative / PEG / PSG Comparison",
        "Seasonality Calibration", "Next-Quarter Threshold", "Method and Assumption Bridge",
        "Market-Expectation Valuation Bridge", "Broker/Street Comparison",
        "Market-Implied Sentiment Anchor", "Growth Earnings Dependency",
        "Full-Chain Classification Dependency",
    )

    check("01 full-note research brief", "single_stock_full_note" in read("research_brief.md"))
    check("02 brief price and action", contains_all(read("research_brief.md"), ("17.75", "17.0", "减持")))
    check("03 full-note report type", isinstance(gate, dict) and gate.get("report_type") == "single_stock_full_note")
    check("04 five institutional depth gates", isinstance(gate, dict) and set(gate.get("depth_gates", [])) == {"evidence_depth", "broker_consensus_depth", "model_depth", "valuation_depth", "ic_readiness"})
    check("05 artifact contract parses", isinstance(contract, dict) and isinstance(contract.get("artifacts"), list))
    check("06 contract depth fields", isinstance(contract, dict) and all(isinstance(item, dict) and all(item.get(key) for key in ("required_fields", "minimum_depth", "blocking_conditions", "reviewer_cycle", "verifier_check")) for item in contract.get("artifacts", [])))
    check("07 source archive", (CASE / "sources").exists())
    check("08 primary company documents", all((CASE / rel).exists() for rel in ("sources/official-financial-20260723/002497_2025_annual_report.pdf", "sources/official-financial-20260723/002497_2026_q1_report.pdf", "sources/official-financial-20260723/002497_2026_h1_earnings_preview.pdf")))
    check("09 historical financial packet", contains_all(read("data/verified_financials.md"), ("118.953", "85.432", "-5.698", "-4.306")))
    check("10 H1 preview range", contains_all(read("data/claim_audit.md"), ("C-03", "CNY1.10–1.30bn")))
    check("11 2026-07-23 market packet", contains_all(read("data/verified_market_data.md"), ("17.75", "1,152,562,520", "20.458", "2026-07-23")))
    check("12 market price path and benchmark", contains_all(read("data/verified_market_data.md"), ("-27.99", "-22.68", "-2.77")))
    check("13 three original broker PDFs", len(list((CASE / "sources/broker-reports/2026-07-23").glob("*.pdf"))) >= 3)
    broker_rows = rows(brokers)
    check("14 broker packet has three rows", len(broker_rows) == 3)
    check("15 broker fields and zero weights", bool(broker_rows) and all(all(key in item for key in ("target_price", "revenue_E", "net_profit_E", "EPS_E", "implied_upside", "valuation_weight")) and float(item.get("valuation_weight", 1)) == 0.0 for item in broker_rows))
    check("16 source registry depth", isinstance(registry, list) and len(registry) >= 12 and any(item.get("source_id") == "FIN-26H1P" for item in registry if isinstance(item, dict)))
    check("17 claim boundary", isinstance(claims, list) and any(str(item.get("evidence_status", "")).startswith("not_supported") for item in claims if isinstance(item, dict)))
    check("18 source exhaustion records broker gap", contains_all(read("source_exhaustion_log.md"), ("broker", "target")))
    check("19 announcement causality boundary", "cannot establish" in read("data/announcement_event_audit_20260723.md").lower())
    check("20 full-chain universe", len(rows(load("data/full_chain_universe_20260723.json"))) >= 21)
    check("21 relationship and customer audits", len(rows(load("data/supply_chain_relationships.json"))) >= 9 and len(rows(load("data/customer_chain_audit.json"))) >= 10)
    check("22 value-chain history and zero credit", contains_all(read("analysis/value_chain_economics.md"), ("2025", "valuation_credit", "零信用")))
    check("23 H1 plus H2 model bridge", contains_all(read("analysis/segment_forecast_bridge.md"), ("11.0", "12.0", "13.0", "4.0", "8.1", "11.7")))
    check("24 growth model machine inputs", isinstance(growth, dict) and "2026" in json.dumps(growth) and "2027" in json.dumps(growth))
    model_rows = rows(model)
    check("25 current valuation structured row", len(model_rows) == 1 and model_rows[0].get("current_price") == 17.75 and model_rows[0].get("final_target") == 17.07)
    check("26 valuation scenarios", contains_all(valuation, ("15.0", "20.1", "24.7", "10.3", "17.3", "26.1")))
    check("27 valuation full-note headings", contains_all(valuation, valuation_sections))
    check("28 valuation arithmetic audit", "Model Reproducibility: PASS" in read("analysis/valuation_audit.md"))
    check("29 segment valuation depth", contains_all(read("analysis/segment_valuation_model.md"), ("segment", "sotp", "revenue", "net profit", "multiple", "sensitivity", "validation trigger")))
    check("30 secondary-market depth", contains_all(read("analysis/secondary_market_analysis.md"), ("price", "volume", "turnover", "drawdown", "relative performance", "valuation crowding", "support", "resistance", "seat", "institutional", "northbound", "financing", "trading style", "hot-money", "fund attitude", "trend swing")))
    actual_sections = {path.name for path in (CASE / "sections").glob("*.tex")}
    check("31 full chapter set present", required_sections <= actual_sections)
    check("32 main tex uses full-note chapters", contains_all(read("main.tex"), ("ch10_cycle", "ch11_model_detail", "ch12_peer", "ch13_reassessment", "app_governance", "app_reconciliation")))
    check("33 reader text carries current conclusion", contains_all(extracted, ("17.75", "17.0", "减持", "1.74", "正式 H1")))
    check("34 reader text excludes event-report identity", "业绩预告事件研究" not in extracted and "PASS_EVENT_RESEARCH_ONLY" not in extracted)
    check("35 PDF present", (CASE / "main.pdf").exists() and (CASE / "main.pdf").stat().st_size > 500000)
    check("36 PDF institutional length", 40 <= pages() <= 60, f"pages={pages()}")
    render_dir = CASE / "rendered/full-note-20260723-r1"
    check("37 fresh rendered pages", render_dir.exists() and len(list(render_dir.glob("*.png"))) == pages())
    check("38 visual and exhibit review", contains_all(read("visual_review.md"), ("PASS", "40 页", "full-note-20260723-r3")) and contains_all(read("governance/exhibit_format_review_R1.md"), ("PASS", "exhibit")))
    cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    all_closed = all(findings_closed(f"review_findings_{cycle}.json") for cycle in cycles)
    workflow_quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("39 R0-R4, sign-off and workflow", all_closed and isinstance(signoff, dict) and signoff.get("signoff_status") == "PASS" and signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0 and workflow_quality.get("publishable") is True)

    for item in passes:
        print(f"PASS {item}")
    for item in failures:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(passes)} PASS / {len(failures)} FAIL")
    return 0 if len(passes) == 39 and not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
