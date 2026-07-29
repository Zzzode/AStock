#!/usr/bin/env python3
"""Case-local publication verifier for the China Shipbuilding report."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


CASE = Path(__file__).resolve().parents[1]
passes: list[str] = []
failures: list[str] = []


def check(name: str, condition: bool, detail: str = "") -> None:
    message = f"{name}: {detail}" if detail else name
    (passes if condition else failures).append(message)


def text(rel: str) -> str:
    path = CASE / rel
    return path.read_text(encoding="utf-8", errors="replace") if path.exists() else ""


def payload(rel: str) -> object:
    path = CASE / rel
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def page_count() -> int:
    pdf = CASE / "main.pdf"
    if not pdf.exists():
        return 0
    completed = subprocess.run(
        ["pdfinfo", str(pdf)], text=True, capture_output=True, check=False
    )
    match = re.search(r"^Pages:\s+(\d+)$", completed.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else 0


def main() -> int:
    gate = payload("gate_manifest.json")
    contract = payload("artifact_contract.json")
    registry = payload("data/source_registry.json")
    claims = payload("data/claim_audit.json")
    exhaustion = payload("source_exhaustion_log.json")
    broker = payload("data/broker_street_consensus_20260722.json")
    growth = payload("data/growth_earnings_model_20260722.json")
    valuation = payload("data/current_valuation_model_20260722.json")
    rows = valuation.get("rows", []) if isinstance(valuation, dict) else []
    row = rows[0] if rows and isinstance(rows[0], dict) else {}

    check("01 research brief", (CASE / "research_brief.md").exists())
    check("02 gate manifest parses", isinstance(gate, dict) and bool(gate))
    check("03 artifact contract parses", isinstance(contract, dict) and bool(contract))
    check("04 source registry depth", (CASE / "data/source_registry.md").exists() and isinstance(registry, dict) and len(registry.get("sources", [])) >= 40)
    check("05 claim audit depth", (CASE / "data/claim_audit.md").exists() and isinstance(claims, dict) and len(claims.get("claims", [])) >= 35)
    check("06 source exhaustion pair", (CASE / "source_exhaustion_log.md").exists() and isinstance(exhaustion, dict) and bool(exhaustion))
    financials = text("data/verified_financials.md")
    check("07 official financial bridge", all(term in financials for term in ("2024A", "Restated", "2026Q1", "Monetary funds", "Cash capex")))
    market = text("data/verified_market_data.md")
    check("08 market anchor", all(term in market for term in ("33.02", "7,525,621,288", "2,484.96")))
    check("09 broker consensus pair", (CASE / "data/broker_street_consensus_20260722.md").exists() and isinstance(broker, dict) and len(broker.get("rows", [])) >= 13)
    check("10 official company PDFs", len(list((CASE / "sources/official-company-20260722").glob("*.pdf"))) >= 15)
    check("11 original broker PDFs", len(list((CASE / "sources/broker-reports/2026-07-22").glob("*.pdf"))) >= 13)
    check("12 industry archive", (CASE / "sources/official-industry-20260722/SOURCE_INDEX.md").exists() and len(list((CASE / "sources/official-industry-20260722").glob("*.pdf"))) >= 5)
    full_chain = payload("data/full_chain_universe_20260722.json")
    nodes = full_chain.get("nodes", []) if isinstance(full_chain, dict) else []
    core = [node for node in nodes if isinstance(node, dict) and node.get("classification") == "core_valuation"]
    check("13 full-chain classification", len(nodes) >= 25 and len(core) == 1 and core[0].get("listed_ticker") == "600150.SH")
    relationships = payload("data/supply_chain_relationships.json")
    customer = payload("data/customer_chain_audit.json")
    check("14 relationship governance", isinstance(relationships, dict) and len(relationships.get("relationships", [])) >= 12 and len(relationships.get("row_governance", [])) >= 12)
    check("15 customer governance", isinstance(customer, dict) and len(customer.get("audit_rows", [])) >= 10 and len(customer.get("row_governance", [])) >= 10)
    chain_text = text("analysis/chain_earnings_bridge.md") + text("analysis/coverage_gap_matrix.md")
    check("16 order boundary", "4,674.51" in chain_text and "R1" in chain_text and "中远" in chain_text)
    check("17 growth model pair", isinstance(growth, dict) and bool(growth) and (CASE / "analysis/growth_earnings_model.md").exists())
    growth_text = text("analysis/growth_earnings_model.md") + text("analysis/growth_model_audit.md")
    growth_boundaries = all(
        term in growth_text
        for term in ("H1", "75.256", "backlog", "Model Reproducibility: PASS")
    ) and ("COSCO" in growth_text or "中远" in growth_text)
    check("18 growth model boundaries", growth_boundaries)
    check("19 valuation structured row", len(rows) == 1 and row.get("ticker") == "600150.SH")
    required = {"ticker", "company", "current_price", "price_date", "shares_100mn", "market_cap_100mn_cny", "revenue_2026e_100mn", "np_2026e_100mn", "eps_2026e", "method", "bear", "base", "bull", "market_implied_anchor", "fundamental_weight", "market_weight", "broker_weight", "final_target", "upside", "action", "evidence_quality"}
    check("20 valuation fields", required.issubset(row.keys()))
    price = float(row.get("current_price", 0) or 0)
    target = float(row.get("final_target", 0) or 0)
    upside = float(row.get("upside", 0) or 0)
    check("21 price and shares", abs(price - 33.02) < 1e-9 and abs(float(row.get("shares_100mn", 0) or 0) - 75.25621288) < 1e-7)
    check("22 market cap", abs(float(row.get("market_cap_100mn_cny", 0) or 0) - price * float(row.get("shares_100mn", 0) or 0)) < 0.02)
    check("23 target upside", target > 0 and abs(target / price - 1 - upside) < 0.0005)
    check("24 scenario ordering", 0 < float(row.get("bear", 0) or 0) < float(row.get("base", 0) or 0) < float(row.get("bull", 0) or 0))
    check("25 anchor weights", abs(sum(float(row.get(key, 0) or 0) for key in ("fundamental_weight", "market_weight", "broker_weight")) - 1.0) < 1e-9 and float(row.get("broker_weight", 0) or 0) == 0.0)
    valuation_text = text("analysis/valuation_model.md")
    sections = ("Final Valuation Table", "Three-Tier Targets", "Relative / PEG / PSG Comparison", "Seasonality Calibration", "Next-Quarter Threshold", "Method and Assumption Bridge", "Market-Expectation Valuation Bridge", "Broker/Street Comparison", "Market-Implied Sentiment Anchor", "Growth Earnings Dependency", "Full-Chain Classification Dependency")
    check("26 valuation sections", all(section in valuation_text for section in sections))
    check("27 valuation reproducibility", "Model Reproducibility: PASS" in text("analysis/valuation_audit.md"))
    segment = text("analysis/segment_valuation_model.md").lower()
    check("28 segment model", all(term in segment for term in ("segment", "sotp", "revenue", "net profit", "multiple", "sensitivity", "validation trigger")))
    secondary = text("analysis/secondary_market_analysis.md").lower()
    market_structure = payload("data/market_structure_20260722.json")
    capital = payload("data/capital_positioning_20260722.json")
    market_ok = (
        isinstance(market_structure, dict)
        and market_structure.get("historical_daily_kline", {}).get("adjustment_parameter") == "fqt=1"
        and market_structure.get("historical_daily_kline", {}).get("coverage", {}).get("trading_days", 0) >= 250
        and market_structure.get("cutoff_market_snapshot", {}).get("turnover_pct") == 1.44
        and market_structure.get("share_float_interpretation", {}).get("strict_free_float_shares") is None
    )
    capital_ok = (
        isinstance(capital, dict)
        and "75.6724" in text("data/capital_positioning_20260722.md")
        and "2.4093" in text("data/capital_positioning_20260722.md")
        and "1.7335" in text("data/capital_positioning_20260722.md")
        and "9201" in text("data/capital_positioning_20260722.md")
    )
    prose_ok = all(term in secondary for term in ("relative performance", "support", "resistance", "institutional", "northbound", "financing", "hot-money", "fund attitude", "trend swing"))
    check("29 secondary market evidence", market_ok and capital_ok and prose_ok, "labelled K-line, turnover/float boundary, margin, Connect, fund and Dragon-Tiger evidence")
    check("30 house and risk", "中性偏多" in text("analysis/house_view.md") and "风险矩阵" in text("analysis/risk_framework.md") and "失效条件" in text("analysis/risk_framework.md"))
    reader_text = "\n".join(text(rel) for rel in ("main.tex", "main_current_text.txt", "analysis/house_view.md", "analysis/valuation_model.md"))
    check("31 no placeholders", not any(item in reader_text for item in ("TODO", "TBD", "待补", "PLACEHOLDER")))
    section_files = list((CASE / "sections").glob("*.tex")) if (CASE / "sections").exists() else []
    check("32 tex depth", (CASE / "main.tex").exists() and len(text("main.tex")) >= 1000 and len(section_files) >= 10)
    check("33 PDF present", (CASE / "main.pdf").exists() and (CASE / "main.pdf").stat().st_size >= 100_000 if (CASE / "main.pdf").exists() else False)
    pages = page_count()
    check("34 PDF page count", 40 <= pages <= 60, f"pages={pages}")
    current_text = text("main_current_text.txt")
    check("35 extracted report", len(current_text) >= 40_000 and all(term in current_text for term in ("33.02", "75.256", "4,674.51")))
    cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    check("36 review lifecycle", all((CASE / f"review_findings_{cycle}.json").exists() for cycle in cycles))
    signoff = payload("final_signoff.json")
    check("37 final signoff", isinstance(signoff, dict) and signoff.get("signoff_status") == "PASS" and signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0)
    workflow = payload("research_workflow_eval.json")
    quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("38 workflow eval", isinstance(quality, dict) and quality.get("publishable") is True and quality.get("blocking_failure_count") == 0 and int(quality.get("score", 0)) >= 90)
    r0 = payload("review_findings_R0_evidence.json")
    check("39 R0 closed", isinstance(r0, dict) and r0.get("cycle_status") == "PASS" and r0.get("open_s_count") == 0 and r0.get("open_a_count") == 0)

    for item in passes:
        print(f"PASS {item}")
    for item in failures:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(passes)} PASS / {len(failures)} FAIL")
    return 0 if not failures and len(passes) == 39 else 1


if __name__ == "__main__":
    raise SystemExit(main())
