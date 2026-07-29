#!/usr/bin/env python3
"""Case-local publication verifier for the Desay SV full single-stock note.

The checks are intentionally tied to this report's disclosed price, financial
base, source boundaries, model arithmetic and final reader-facing artifacts.
They do not manufacture customer, ASP, order-conversion or broker-target data.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path
from typing import Any


CASE = Path(__file__).resolve().parents[1]
PASSES: list[str] = []
FAILURES: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    (PASSES if condition else FAILURES).append(f"{name}: {detail}" if detail else name)


def text(rel: str) -> str:
    path = CASE / rel
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def payload(rel: str) -> Any:
    try:
        return json.loads((CASE / rel).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def rows(data: Any, *keys: str) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        return []
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def pages() -> int:
    pdf = CASE / "main.pdf"
    if not pdf.exists():
        return 0
    result = subprocess.run(["pdfinfo", str(pdf)], text=True, capture_output=True, check=False)
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def review_closed(rel: str) -> bool:
    data = payload(rel)
    return isinstance(data, dict) and data.get("cycle_status") == "PASS" and data.get("open_s_count", 0) == 0 and data.get("open_a_count", 0) == 0


def main() -> int:
    gate = payload("gate_manifest.json")
    contract = payload("artifact_contract.json")
    registry = payload("data/source_registry.json")
    claims = payload("data/claim_audit.json")
    exhaustion = payload("source_exhaustion_log.json")
    broker = payload("data/broker_street_consensus_20260723.json")
    universe = payload("data/full_chain_universe_20260723.json")
    relationships = payload("data/supply_chain_relationships.json")
    customers = payload("data/customer_chain_audit.json")
    valuation = payload("data/current_valuation_model_20260723.json")
    model_rows = rows(valuation, "rows", "valuations")
    row = model_rows[0] if len(model_rows) == 1 else {}

    check("01 research brief", (CASE / "research_brief.md").exists())
    check("02 gate manifest parses", isinstance(gate, dict) and gate.get("report_type") == "single_stock_full_note")
    check("03 artifact contract parses", isinstance(contract, dict) and len(contract.get("artifacts", [])) >= 10)
    check("04 source registry depth", (CASE / "data/source_registry.md").exists() and len(rows(registry, "sources")) >= 8)
    check("05 claim audit depth", (CASE / "data/claim_audit.md").exists() and len(rows(claims, "claims")) >= 12)
    check("06 source exhaustion pair", (CASE / "source_exhaustion_log.md").exists() and bool(exhaustion))
    financials = text("data/verified_financials.md")
    check("07 official financial bridge", all(term in financials for term in ("FY2025", "32.5572", "2.4536", "2026Q1", "unaudited", "2.8838")))
    market = text("data/verified_market_data.md")
    check("08 market anchor", all(term in market for term in ("83.48", "596.8093m", "49.8216bn", "21.36x")))
    broker_rows = rows(broker, "rows")
    check("09 broker consensus pair", (CASE / "data/broker_street_consensus_20260723.md").exists() and len(broker_rows) >= 16)
    pdf_dir = CASE / "sources/broker-reports/2026-07-23"
    check("10 original broker PDFs", len(list(pdf_dir.glob("*.pdf"))) >= 4)
    check("11 official annual report archive", (CASE / "sources/ir-20260723/desay_sv_2025_annual_report_cninfo.pdf").exists())
    check("12 broker target boundary", "0 个可用锚点" in text("data/consensus_analysis.md") and all(float(item.get("valuation_weight", 0) or 0) == 0 for item in broker_rows))
    universe_rows = rows(universe, "universe", "nodes", "rows")
    core = [item for item in universe_rows if item.get("classification") == "core_valuation"]
    check("13 full-chain classification", len(universe_rows) >= 40 and len(core) == 1 and core[0].get("listed_ticker") == "002920.SZ")
    check("14 relationship governance", len(rows(relationships, "relationships")) >= 15)
    check("15 customer governance", len(rows(customers, "audits", "audit_rows")) >= 16)
    economics = text("analysis/value_chain_economics.md").lower()
    check("16 value-chain economics", all(term in economics for term in ("asp", "margin", "capacity", "utilization", "order", "valuation credit")))
    bridge = text("analysis/chain_earnings_bridge.md")
    check("17 order-to-income boundary", all(term in bridge for term in ("CNY35bn", "订单年化", "不能")))
    growth = text("analysis/growth_earnings_model.md")
    check("18 growth model artifact", (CASE / "analysis/segment_forecast_bridge.md").exists() and (CASE / "analysis/implied_growth_sensitivity.md").exists() and (CASE / "data/growth_driver_model.json").exists())
    check("19 growth model boundaries", all(term in growth for term in ("Base Business", "Growth Segment", "CNY4.69", "optionality credit", "Current-Price-Implied")))
    check("20 valuation structured row", len(model_rows) == 1 and row.get("ticker") == "002920.SZ")
    required = {"ticker", "company", "current_price", "price_date", "shares_100mn", "market_cap_100mn_cny", "revenue_2026e_100mn", "np_2026e_100mn", "eps_2026e", "method", "bear", "base", "bull", "market_implied_anchor", "fundamental_weight", "market_weight", "broker_weight", "final_target", "upside", "action", "evidence_quality"}
    check("21 valuation fields", required.issubset(row))
    check("22 price and shares", abs(float(row.get("current_price", 0)) - 83.48) < 0.001 and abs(float(row.get("shares_100mn", 0)) - 5.96809294) < 0.000001)
    check("23 market cap arithmetic", abs(float(row.get("market_cap_100mn_cny", 0)) - float(row.get("current_price", 0)) * float(row.get("shares_100mn", 0))) < 0.02)
    check("24 target upside arithmetic", abs(float(row.get("upside", 0)) - (float(row.get("final_target", 0)) / float(row.get("current_price", 1)) - 1)) < 0.0005)
    check("25 scenario and weights", float(row.get("bear", 0)) < float(row.get("base", 0)) < float(row.get("bull", 0)) and abs(sum(float(row.get(key, 0)) for key in ("fundamental_weight", "market_weight", "broker_weight")) - 1.0) < 1e-9)
    valuation_text = text("analysis/valuation_model.md")
    sections = ("Final Valuation Table", "Three-Tier Targets", "Relative / PEG / PSG Comparison", "Seasonality Calibration", "Next-Quarter Threshold", "Method and Assumption Bridge", "Market-Expectation Valuation Bridge", "Broker/Street Comparison", "Market-Implied Sentiment Anchor", "Growth Earnings Dependency", "Full-Chain Classification Dependency")
    check("26 valuation sections", all(section in valuation_text for section in sections))
    check("27 valuation reproducibility", "Model Reproducibility: PASS" in text("analysis/valuation_audit.md"))
    segment = text("analysis/segment_valuation_model.md").lower()
    check("28 segment valuation depth", all(term in segment for term in ("segment", "sotp", "revenue", "net profit", "multiple", "sensitivity", "validation trigger")))
    secondary = text("analysis/secondary_market_analysis.md").lower()
    market_terms = ("price", "volume", "turnover", "drawdown", "relative performance", "valuation crowding", "support", "resistance", "seat", "institutional", "northbound", "financing", "trading style", "hot-money", "fund attitude", "trend swing")
    check("29 secondary-market boundary", all(term in secondary for term in market_terms) and "not disclosed" in secondary)
    check("30 house and risk", "market-supported watch" in text("analysis/house_view.md") and "Risk Framework" in text("analysis/risk_framework.md") and "失效" in text("analysis/risk_framework.md"))
    reader = "\n".join(text(rel) for rel in ("main.tex", "main_current_text.txt", "analysis/house_view.md", "analysis/valuation_model.md"))
    check("31 no placeholders", not any(token in reader for token in ("TODO", "TBD", "待补", "PLACEHOLDER")))
    sections_dir = CASE / "sections"
    check("32 LaTeX report depth", (CASE / "main.tex").exists() and len(list(sections_dir.glob("*.tex"))) >= 10 and len(text("main.tex")) >= 1200)
    check("33 PDF present", (CASE / "main.pdf").exists() and (CASE / "main.pdf").stat().st_size >= 100_000 if (CASE / "main.pdf").exists() else False)
    page_total = pages()
    check("34 PDF institutional length", 40 <= page_total <= 60, f"pages={page_total}")
    extracted = text("main_current_text.txt")
    check("35 extracted report", len(extracted) >= 35_000 and all(term in extracted for term in ("83.48", "596.8093", "86.4", "35.0")))
    cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    check("36 review lifecycle", all((CASE / f"review_findings_{cycle}.json").exists() for cycle in cycles) and all((CASE / f"repair_plan_{cycle}.md").exists() and (CASE / f"repair_plan_{cycle}.json").exists() for cycle in cycles[:-1]))
    signoff = payload("final_signoff.json")
    check("37 final signoff", isinstance(signoff, dict) and signoff.get("signoff_status") == "PASS" and signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0)
    workflow = payload("research_workflow_eval.json")
    quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("38 workflow evaluation", isinstance(quality, dict) and quality.get("publishable") is True and quality.get("blocking_failure_count") == 0 and float(quality.get("score", 0)) >= 90)
    check("39 R0 review closed", review_closed("review_findings_R0_evidence.json"))

    for item in PASSES:
        print(f"PASS {item}")
    for item in FAILURES:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(PASSES)} PASS / {len(FAILURES)} FAIL")
    return 0 if not FAILURES and len(PASSES) == 39 else 1


if __name__ == "__main__":
    raise SystemExit(main())
