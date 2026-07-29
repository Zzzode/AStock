#!/usr/bin/env python3
"""Case-local publication verifier for the 2026 year-end double-upside screen."""

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
    valuation = payload("data/current_valuation_model_20260722.json")
    zero_weight = payload("data/zero_weight_valuation_model_20260722.json")
    rows = valuation.get("rows", []) if isinstance(valuation, dict) else []
    zero_rows = zero_weight.get("rows", []) if isinstance(zero_weight, dict) else []
    by_ticker = {
        str(row.get("ticker")): row
        for row in rows
        if isinstance(row, dict) and row.get("ticker")
    }
    yahua = by_ticker.get("002497", {})
    zero_by_ticker = {
        str(row.get("ticker")): row
        for row in zero_rows
        if isinstance(row, dict) and row.get("ticker")
    }
    enjie = zero_by_ticker.get("002812", {})

    check("01 research brief", (CASE / "research_brief.md").exists())
    check("02 gate manifest parses", isinstance(gate, dict) and bool(gate))
    check("03 artifact contract parses", isinstance(contract, dict) and bool(contract))
    check("04 source registry pair", (CASE / "data/source_registry.md").exists() and isinstance(registry, dict) and len(registry.get("sources", [])) >= 24)
    check("05 claim audit pair", (CASE / "data/claim_audit.md").exists() and isinstance(claims, dict) and len(claims.get("claims", [])) >= 12)
    check("06 source exhaustion pair", (CASE / "source_exhaustion_log.md").exists() and isinstance(exhaustion, dict) and len(exhaustion.get("probes", [])) >= 8)
    verified_financials = text("data/verified_financials.md")
    check("07 verified financials", all(item in verified_financials for item in ("600150", "301308", "002812", "002240", "300390", "002497", "2026Q1 OCF")))
    verified_market = text("data/verified_market_data.md")
    check("08 verified market data", "16/16 matched" in verified_market and "Ten-session drawdown" in verified_market)
    check("09 broker consensus pair", (CASE / "data/broker_street_consensus_20260722.md").exists() and isinstance(broker, dict) and len(broker.get("rows", [])) == 2)
    check("10 official PDFs archived", len(list((CASE / "sources/official-20260722").glob("*.pdf"))) == 21)
    check("11 original broker PDFs archived", len(list((CASE / "sources/broker-reports/2026-07-22").glob("*/*.pdf"))) == 14)
    check("12 operating-driver artifacts", all((CASE / rel).exists() for rel in ("analysis/company_fundamental_cards.md", "analysis/value_chain_economics.md", "analysis/chain_earnings_bridge.md", "data/supply_chain_relationships.json", "data/customer_chain_audit.json")))
    check("13 valuation structured rows", len(rows) == 1 and set(by_ticker) == {"002497"} and len(zero_rows) == 5 and set(zero_by_ticker) == {"600150", "301308", "002812", "002240", "300390"})
    required = {"ticker", "company", "current_price", "price_date", "shares_100mn", "market_cap_100mn_cny", "revenue_2026e_100mn", "np_2026e_100mn", "eps_2026e", "method", "bear", "base", "bull", "market_implied_anchor", "fundamental_weight", "market_weight", "broker_weight", "final_target", "upside", "action", "evidence_quality"}
    check("14 valuation required fields", all(required.issubset(row.keys()) for row in rows if isinstance(row, dict)))
    check("15 current prices frozen", yahua.get("current_price") == 16.79 and enjie.get("current_price") == 47.84 and yahua.get("price_date") == "2026-07-22" and enjie.get("price_date") == "2026-07-22")
    arithmetic_ok = all(abs(float(row["final_target"]) / float(row["current_price"]) - 1 - float(row["upside"])) < 0.0005 for row in rows if isinstance(row, dict))
    check("16 target and upside reproduce", arithmetic_ok)
    check("17 share reconciliation", abs(float(yahua.get("shares_100mn", 0)) - 11.5256) < 1e-4 and abs(float(enjie.get("shares_100mn", 0)) - 9.8132) < 1e-4)
    check("18 scenario values reproduce", abs(float(yahua.get("bear", 0)) - 9.12) < 1e-9 and abs(float(yahua.get("bull", 0)) - 42.08) < 1e-9 and abs(float(enjie.get("bull", 0)) - 103.20) < 1e-9 and float(enjie.get("external_target_weight", -1)) == 0.0)
    check("19 anchor weights sum", all(abs(sum(float(row.get(key, 0)) for key in ("fundamental_weight", "market_weight", "broker_weight")) - 1.0) < 1e-9 for row in rows if isinstance(row, dict)))
    valuation_text = text("analysis/valuation_model.md")
    sections = ("Final Valuation Table", "Three-Tier Targets", "Relative / PEG / PSG Comparison", "Seasonality Calibration", "Next-Quarter Threshold", "Method and Assumption Bridge", "Market-Expectation Valuation Bridge", "Broker/Street Comparison", "Market-Implied Sentiment Anchor", "Growth Earnings Dependency", "Full-Chain Classification Dependency")
    check("20 valuation sections complete", all(section in valuation_text for section in sections))
    check("21 valuation reproducibility", "Model Reproducibility: PASS" in text("analysis/valuation_audit.md"))
    segment = text("analysis/segment_valuation_model.md").lower()
    check("22 segment model depth", all(term in segment for term in ("segment", "sotp", "revenue", "net profit", "multiple", "sensitivity", "validation trigger")))
    secondary = text("analysis/secondary_market_analysis.md").lower()
    check("23 secondary market depth", all(term in secondary for term in ("price", "volume", "turnover", "drawdown", "relative performance", "valuation crowding", "support", "resistance", "institutional", "northbound", "financing", "hot-money", "fund attitude", "trend swing")))
    risk = text("analysis/risk_framework.md")
    check("24 risk framework", "Probability-Impact Matrix" in risk and "Invalidation Rules" in risk and "Year-End Timing Risk" in risk)
    house = text("analysis/house_view.md")
    check("25 house view anchors", all(item in house for item in ("only conditional core", "002497", "002812", "600150", "20%", "zero-weight")))
    reader_text = "\n".join(text(rel) for rel in ("main.tex", "main_current_text.txt", "analysis/house_view.md", "analysis/valuation_model.md"))
    banned = ("TODO", "TBD", "待补", "PLACEHOLDER", "guaranteed double", "必然翻倍")
    check("26 no generic placeholders", not any(item in reader_text for item in banned))
    check("27 main tex present", (CASE / "main.tex").exists() and len(text("main.tex")) >= 1000)
    section_files = list((CASE / "sections").glob("*.tex")) if (CASE / "sections").exists() else []
    check("28 section depth", len(section_files) >= 13)
    tex_corpus = text("main.tex") + "\n" + "\n".join(path.read_text(encoding="utf-8", errors="replace") for path in section_files)
    check("29 report conclusion anchors", all(item in tex_corpus for item in ("没有高置信度", "唯一条件核心", "103元", "42元")))
    check("30 PDF present", (CASE / "main.pdf").exists() and (CASE / "main.pdf").stat().st_size >= 300_000 if (CASE / "main.pdf").exists() else False)
    pages = page_count()
    check("31 PDF page count", 25 <= pages <= 35, f"pages={pages}")
    current_text = text("main_current_text.txt")
    check("32 extracted text present", len(current_text) >= 25_000)
    check("33 extracted report anchors", all(item in current_text for item in ("16.79", "47.84", "25.32", "103", "零权")))
    check("34 rendered page coverage", len(list((CASE / "rendered").glob("page-*.png"))) == pages and pages > 0)
    review_cycles = ("R0_evidence", "R1_model", "R2_draft", "R3_render_compliance", "R4_final_ic")
    check("35 review lifecycle", all((CASE / f"review_findings_{cycle}.json").exists() for cycle in review_cycles))
    check("36 repair plans", all((CASE / f"repair_plan_{cycle}.json").exists() and (CASE / f"repair_plan_{cycle}.md").exists() for cycle in review_cycles[:-1]))
    signoff = payload("final_signoff.json")
    check("37 final signoff", isinstance(signoff, dict) and signoff.get("signoff_status") == "PASS" and signoff.get("open_s_count") == 0 and signoff.get("open_a_count") == 0)
    workflow = payload("research_workflow_eval.json")
    quality = workflow.get("quality", {}) if isinstance(workflow, dict) else {}
    check("38 workflow eval", isinstance(quality, dict) and quality.get("publishable") is True and quality.get("blocking_failure_count") == 0 and int(quality.get("score", 0)) >= 90)
    check("39 review log score", "Publishability Score: 93" in text("review_log.md"))

    for item in passes:
        print(f"PASS {item}")
    for item in failures:
        print(f"FAIL {item}")
    print(f"SUMMARY {len(passes)} PASS / {len(failures)} FAIL")
    return 0 if not failures and len(passes) == 39 else 1


if __name__ == "__main__":
    raise SystemExit(main())
